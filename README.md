# Audio Downloader v0.31

A command-line tool for downloading audio from various platforms (YouTube, SoundCloud, etc.) with advanced configuration options.

## Features

- **Multiple platforms support**: YouTube, SoundCloud, and many others supported by yt-dlp
- **Audio format conversion**: Convert to MP3 with custom quality and sample rate
- **Duplicate detection**: Skip files that already exist
- **Progress tracking**: Real-time download progress displayed in console
- **Configurable logging**: File logging with customizable levels
- **JSON configuration**: Easy configuration through JSON file
- **Error handling**: Robust error handling with detailed error messages
- **Single URL download**: Download a single track directly via command-line argument

## Requirements

- Python 3.7+
- yt-dlp
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

# Download a single track
python audiodownloader.py -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Use custom config file
python audiodownloader.py -c my_config.json

# Override output path
python audiodownloader.py -o d:/my_music

# Skip existing files (overrides config setting)
python audiodownloader.py -s
```

### Command Line Options

- `-c, --config CONFIG`: Configuration file (default: config.json)
- `-l, --links LINKS`: Text file containing links to download (overrides config)
- `-o, --output OUTPUT`: Destination folder for downloads (overrides config)
- `-u, --url URL`: Download single URL directly (ignores links.txt)
- `-s, --skip-existing`: Skip files that already exist (overrides config setting)

### Links File Format

Create a `links.txt` file with one URL per line. Comments starting with `#` are ignored:

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
  "audio": {
    "codec": "mp3",
    "quality": "320",
    "sample_rate": "48000"
  },
  "paths": {
    "links_file": "links.txt",
    "output_dir": "./audiodownloads",
    "log_file": "audiodownloader.log"
  },
  "behavior": {
    "skip_existing": true,
    "quiet_download": true
  },
  "logging": {
    "level": "INFO",
    "console_level": "ERROR",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
  }
}
```

### Configuration Options

- **audio.codec**: Output audio codec (mp3, wav, etc.)
- **audio.quality**: Audio quality/bitrate
- **audio.sample_rate**: Audio sample rate in Hz
- **paths.links_file**: Path to the links file
- **paths.output_dir**: Directory for downloaded files
- **paths.log_file**: Path to the log file
- **behavior.skip_existing**: Skip downloads if file already exists
- **behavior.quiet_download**: If true, suppress most console output during download
- **logging.level**: Logging level for file (DEBUG, INFO, WARNING, ERROR)
- **logging.console_level**: Logging level for console (DEBUG, INFO, WARNING, ERROR)

## Output

The downloader creates:
- Audio files in the specified output directory
- A log file (`audiodownloader.log`) with detailed information
- Updates `links.txt` with download status comments (when not using single URL mode)

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

