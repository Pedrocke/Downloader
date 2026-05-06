# Spotify Downloader (Official API + YouTube)

Downloads Spotify tracks as tagged MP3 files using the **official Spotify API** (metadata) and **YouTube** as the audio source.

> **Legal:** This tool uses Spotify’s public API to fetch track names and artists. Audio is downloaded from YouTube. Please respect copyright laws; this is for personal/educational use only.

## Setup (one time)

### 1. Get free Spotify API credentials
- Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- Log in and click **“Create app”**
- Give it a name (e.g., `my-downloader`), description, and set a dummy redirect URI like `http://localhost:8080`
- Note down the **Client ID** and **Client Secret**

### 2. Add them as GitHub Secrets
- In your GitHub repository, go to **Settings → Secrets and variables → Actions**
- Click **New repository secret** and add:
  - Name: `SPOTIFY_CLIENT_ID`, Secret: *your client ID*
  - Name: `SPOTIFY_CLIENT_SECRET`, Secret: *your client secret*

### 3. Push this repo to GitHub
All files are already included. Just clone and push.

## How to download a track

1. Go to the **Actions** tab of your repository.
2. Select the **“Download Spotify Track (YouTube method)”** workflow.
3. Click **Run workflow**.
4. Paste a Spotify track URL like `https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT`
5. Click **Run workflow**.

The workflow will fetch the track info, download audio from YouTube, tag it with album art, and commit the MP3 to the `downloads/` folder.
