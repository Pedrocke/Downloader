const { getData } = require('spotify-url-info');
const { execSync } = require('child_process');
const path = require('path');

async function downloadSpotifyTrack(url) {
    console.log(`Processing: ${url}`);
    const trackInfo = await getData(url);
    
    const artist = trackInfo.artists[0].name;
    const title = trackInfo.name;
    const safeFileName = `${artist} - ${title}.mp3`.replace(/[/\\?%*:|"<>]/g, '-');
    const outputDir = path.resolve('downloads');
    const outputPath = path.join(outputDir, safeFileName);

    console.log(`Searching YouTube for: ${artist} - ${title}`);
    // This command tells yt-dlp to search YouTube for this song and download the audio as an MP3
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
