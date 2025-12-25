# Audio Downloader v0.3

A command-line tool for downloading audio from various platforms (YouTube, SoundCloud, etc.) with advanced configuration options.

## Features

- **Multiple platforms support**: YouTube, SoundCloud, and many others supported by yt-dlp
- **Audio format conversion**: Convert to MP3 with custom quality and sample rate
- **Duplicate detection**: Skip files that already exist
- **Progress tracking**: Real-time download progress with detailed statistics
- **Configurable logging**: File and console logging with customizable levels
- **JSON configuration**: Easy configuration through JSON file
- **Error handling**: Robust error handling with detailed error messages

## Requirements

- Python 3.7+
- FFmpeg (required for audio conversion)

### Installing FFmpeg

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Add FFmpeg to your system PATH
3. Or place ffmpeg.exe in the same directory as the script

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

## Installation

1. Clone or download this repository
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Download audio from links.txt using default config
python audiodownloader.py

# Use custom config file
python audiodownloader.py -c my_config.json

# Override paths
python audiodownloader.py -l my_links.txt -o d:/my_music
```

### Command Line Options

- `-c, --config CONFIG`: Configuration file (default: config.json)
- `-l, --links LINKS`: Text file containing links to download (overrides config)
- `-o, --output OUTPUT`: Destination folder for downloads (overrides config)
- `--skip-existing`: Skip files that already exist (default)
- `--no-skip-existing`: Download files even if they exist

### Links File Format

Create a `links.txt` file with one URL per line:

```
# Audio links
https://www.youtube.com/watch?v=VIDEO_ID
https://soundcloud.com/artist/track

# Comments are ignored
# https://example.com/old_link
```

## Configuration

The `config.json` file allows you to customize the downloader behavior:

```json
{
  "download": {
    "format": "bestaudio/best",
    "quiet": false,
    "force_title": true,
    "no_playlist": true,
    "prefer_ffmpeg": true
  },
  "audio": {
    "codec": "mp3",
    "quality": "320",
    "sample_rate": "48000"
  },
  "paths": {
    "links_file": "links.txt",
    "output_dir": "d:/mp3_yt-dlp",
    "log_file": "audiodownloader.log"
  },
  "behavior": {
    "skip_existing": true,
    "update_links_file": true,
    "progress_update_interval": 1.0
  },
  "logging": {
    "level": "INFO",
    "console_level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
  }
}
```

### Configuration Options

- **download.format**: Audio format to download (default: "bestaudio/best")
- **audio.codec**: Output audio codec (mp3, wav, etc.)
- **audio.quality**: Audio quality/bitrate
- **audio.sample_rate**: Audio sample rate in Hz
- **paths.output_dir**: Directory for downloaded files
- **behavior.skip_existing**: Skip downloads if file already exists
- **logging.level**: Logging level (DEBUG, INFO, WARNING, ERROR)

## Examples

### Download from YouTube

1. Add YouTube URLs to `links.txt`:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

2. Run the downloader:
```bash
python audiodownloader.py
```

### Download from SoundCloud

1. Add SoundCloud URLs to `links.txt`:
```
https://soundcloud.com/artist/track-name
```

2. Run with custom output directory:
```bash
python audiodownloader.py -o d:/music/soundcloud
```

### Use Custom Configuration

1. Create `my_config.json`:
```json
{
  "audio": {
    "codec": "wav",
    "quality": "lossless"
  },
  "paths": {
    "output_dir": "d:/high_quality_audio"
  }
}
```

2. Run with custom config:
```bash
python audiodownloader.py -c my_config.json
```

## Output

The downloader creates:
- Audio files in the specified output directory
- Log file (`audiodownloader.log`) with detailed information
- Updated `links.txt` with download status comments

## Troubleshooting

### Common Issues

**FFmpeg not found:**
- Ensure FFmpeg is installed and in your PATH
- Check that ffmpeg.exe is executable

**Download errors:**
- Check internet connection
- Verify URLs are valid and accessible
- Check log file for detailed error messages

**Permission errors:**
- Ensure write permissions for output directory
- Close any files that might be locked

### Log File

Check `audiodownloader.log` for detailed information about downloads, errors, and system status.

## License

This project is open source. Feel free to use and modify.

## Credits

Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp) - a fork of youtube-dl.

