import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import subprocess
from pathlib import Path

# --- Configuration ---
DOWNLOAD_DIR = "downloads"
# ---------------------

def fetch_spotify_track_info(sp, track_url: str):
    """Given a Spotify track URL, return artist, title, album art URL."""
    try:
        track = sp.track(track_url)
    except Exception as e:
        raise RuntimeError(f"Failed to get track info: {e}")

    artist = track['artists'][0]['name']
    title = track['name']
    album_art_url = None
    if track['album']['images']:
        # Get the largest album art image
        album_art_url = track['album']['images'][0]['url']
    return artist, title, album_art_url

def download_from_youtube(artist: str, title: str, output_dir: str) -> str:
    """
    Search YouTube for artist+title, download audio, and return the path
    of the downloaded file (the final MP3 after conversion).
    """
    search_query = f"{artist} - {title} audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'default_search': 'ytsearch1',  # search YouTube, take first result
        'ignoreerrors': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=True)
            if info is None:
                raise RuntimeError("yt-dlp returned no info")
            # The filename might be derived from the video title, we need to find it
            # We'll reconstruct the expected filename after conversion
            # The actual file after extraction will be .mp3
            if 'entries' in info:
                entry = info['entries'][0]
            else:
                entry = info
            original_title = entry['title']
            # Clean filename to match output template (yt-dlp does this automatically)
            safe_name = f"{original_title}.mp3"
            downloaded_path = os.path.join(output_dir, safe_name)
            return downloaded_path
        except Exception as e:
            raise RuntimeError(f"yt-dlp download failed: {e}")

def embed_metadata_and_art(mp3_path: str, artist: str, title: str, art_url: str):
    """Use ffmpeg to add ID3 tags and embed album art from URL."""
    if not art_url:
        print("No album art URL, skipping metadata embedding")
        return

    # Download the album art image temporarily
    import requests
    art_path = os.path.join(os.path.dirname(mp3_path), "cover.jpg")
    try:
        r = requests.get(art_url, timeout=10)
        r.raise_for_status()
        with open(art_path, 'wb') as f:
            f.write(r.content)
    except Exception as e:
        print(f"Failed to download album art: {e}")
        return

    # Apply metadata with ffmpeg
    try:
        cmd = [
            'ffmpeg', '-y', '-i', mp3_path,
            '-i', art_path,
            '-map', '0:a', '-map', '1:v',
            '-c', 'copy',
            '-id3v2_version', '3',
            '-metadata', f'title={title}',
            '-metadata', f'artist={artist}',
            '-metadata:s:v', 'title=Album cover',
            '-metadata:s:v', 'comment=Cover (front)',
            mp3_path + '.tmp.mp3'
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        # Replace original with tagged version
        os.replace(mp3_path + '.tmp.mp3', mp3_path)
        os.remove(art_path)
        print("Metadata and album art embedded successfully.")
    except Exception as e:
        print(f"Metadata embedding failed: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python download.py <spotify_track_url>")
        sys.exit(1)

    spotify_url = sys.argv[1]

    # Spotify authentication via environment variables
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret= os.environ.get("SPOTIPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Missing Spotify credentials. Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables."
        )

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    print(f"Fetching metadata for: {spotify_url}")
    artist, title, art_url = fetch_spotify_track_info(sp, spotify_url)
    print(f"Found: {artist} - {title}")

    # Ensure download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    print("Downloading audio from YouTube...")
    mp3_path = download_from_youtube(artist, title, DOWNLOAD_DIR)
    print(f"Downloaded to: {mp3_path}")

    if art_url:
        print("Adding metadata and album art...")
        embed_metadata_and_art(mp3_path, artist, title, art_url)

    # Final safe rename to "artist - title.mp3"
    final_name = f"{artist} - {title}".replace('/', '_').replace('\\', '_')
    final_path = os.path.join(DOWNLOAD_DIR, final_name + ".mp3")
    if os.path.abspath(mp3_path) != os.path.abspath(final_path):
        os.rename(mp3_path, final_path)
        print(f"Renamed to: {final_path}")

    print("Done! File is ready for commit.")

if __name__ == "__main__":
    main()
