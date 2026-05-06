// get-and-download.js (fixed)
const spotifyFactory = require('spotify-url-info');
const { execSync } = require('child_process');
const path = require('path');

// The module must be invoked to obtain the Spotify instance
const spotify = spotifyFactory(); // <-- this line was missing!

async function downloadSpotifyTrack(url) {
    console.log(`Processing: ${url}`);
    
    // Now getData is a method on the instance
    const trackInfo = await spotify.getData(url);
    
    const artist = trackInfo.artists[0].name;
    const title = trackInfo.name;
    const safeFileName = `${artist} - ${title}.mp3`.replace(/[/\\?%*:|"<>]/g, '-');
    const outputDir = path.resolve('downloads');
    const outputPath = path.join(outputDir, safeFileName);

    console.log(`Searching YouTube for: ${artist} - ${title}`);
    // yt-dlp search command with audio extraction & best quality
    const cmd = `yt-dlp -x --audio-format mp3 --audio-quality 0 -o "${outputPath}" "ytsearch1:${artist} - ${title} Official Audio"`;

    try {
        execSync(cmd, { stdio: 'inherit' });
        console.log(`Successfully saved to: ${outputPath}`);
    } catch (error) {
        console.error(`Download failed for "${artist} - ${title}": ${error}`);
        process.exit(1);
    }
}

downloadSpotifyTrack(process.argv[2]);
