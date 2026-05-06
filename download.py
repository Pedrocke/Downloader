import sys, os, re, json, requests
from pathlib import Path

def extract_track_id(url: str) -> str:
    match = re.search(r'track/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Spotify track URL")

def download_track(track_url: str):
    track_id = extract_track_id(track_url)
    print(f"Track ID: {track_id}")

    # Use the unofficial spotifydown.com API
    api_url = f"https://api.spotifydown.com/track/{track_id}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://spotifydown.com/"
    }

    # 1. Get metadata and download link
    resp = requests.get(api_url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        raise RuntimeError(f"API error: {data.get('message', 'Unknown error')}")

    title = data["metadata"]["title"]
    artist = data["metadata"]["artists"]
    download_url = data["link"]

    print(f"Downloading: {artist} - {title}")
    print(f"URL: {download_url}")

    # 2. Download the MP3
    audio = requests.get(download_url, headers=headers)
    audio.raise_for_status()

    # 3. Save to downloads/
    os.makedirs("downloads", exist_ok=True)
    safe_name = f"{artist} - {title}".replace('/', '_').replace('\\', '_')
    filepath = Path(f"downloads/{safe_name}.mp3")
    with open(filepath, "wb") as f:
        f.write(audio.content)

    print(f"Saved to {filepath}")
    return str(filepath)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download.py <spotify_track_url>")
        sys.exit(1)
    download_track(sys.argv[1])
