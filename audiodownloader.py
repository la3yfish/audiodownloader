import argparse
import os
import logging
import json
from datetime import datetime
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        if not os.path.exists(config_file):
            logging.warning(f"Config file {config_file} not found, using defaults")
            return get_default_config()

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info(f"Loaded configuration from {config_file}")
        return config

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config file {config_file}: {str(e)}")
        logging.info("Using default configuration")
        return get_default_config()
    except Exception as e:
        logging.error(f"Error loading config file {config_file}: {str(e)}")
        logging.info("Using default configuration")
        return get_default_config()

def get_default_config():
    """Return default configuration"""
    return {
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
            "skip_existing": True,
            "progress_update_interval": 1.0,
            "quiet_download": False
        },
        "logging": {
            "level": "INFO",
            "console_level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S"
        }
    }

def setup_logging(config):
    """Setup logging based on configuration"""
    log_file = config['paths']['log_file']
    log_level = getattr(logging, config['logging']['level'].upper(), logging.INFO)
    console_level = getattr(logging, config['logging']['console_level'].upper(), logging.INFO)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(min(log_level, console_level))  # Set to highest level between file and console

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(config['logging']['format'], config['logging']['date_format'])
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler for progress messages
    console = logging.StreamHandler()
    console.setLevel(console_level)
    console_formatter = logging.Formatter('%(message)s')
    console.setFormatter(console_formatter)
    logger.addHandler(console)

def ensure_output_directory(path):
    """Create output directory if it doesn't exist"""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"Created output directory: {path}")
        return True
    except Exception as e:
        logging.error(f"Failed to create output directory {path}: {str(e)}")
        return False

def create_ydl_opts(config):
    """Create yt-dlp options from configuration"""
    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(config['paths']['output_dir'], '%(title)s.%(ext)s'),
        'quiet': config['behavior']['quiet_download'],
        'forcetitle': True,
        'noplaylist': True,
        'prefer_ffmpeg': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': config['audio']['codec'],
            'preferredquality': config['audio']['quality'],
        }],
        'postprocessor_args': [
            '-ar', config['audio']['sample_rate']
        ],
        'progress_hooks': [],  # Will be set in download function
    }

class DownloadProgress:
    """Handle download progress updates"""
    def __init__(self, url, config):
        self.url = url
        self.last_progress = 0
        self.update_interval = config['behavior']['progress_update_interval']

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                progress = float(d.get('_percent_str', '0%').replace('%', ''))
                if progress - self.last_progress >= self.update_interval:
                    print(f"Progress: {progress:.1f}%")
                    self.last_progress = progress
            except (ValueError, KeyError):
                pass
        elif d['status'] == 'finished':
            logging.info(f"Download completed for: {self.url}")
        elif d['status'] == 'error':
            logging.error(f"Download error for: {self.url}")

def check_file_exists(url, info_dict, config):
    """Check if file already exists for given URL"""
    if not config['behavior']['skip_existing']:
        return False, None

    if info_dict:
        title = info_dict.get('title', '')
        if title:
            output_dir = config['paths']['output_dir']
            ext = config['audio']['codec']

            # Check in main directory and subdirectories
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(f'.{ext}') and title.lower() in file.lower():
                        return True, os.path.join(root, file)

    # Fallback: check by URL identifier
    url_parts = url.rstrip('/').split('/')
    potential_title = url_parts[-1] if url_parts else 'unknown'

    output_dir = config['paths']['output_dir']
    ext = config['audio']['codec']

    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(f'.{ext}') and potential_title.lower() in file.lower():
                return True, os.path.join(root, file)

    return False, None

def download_audio(url, config):
    """Download audio from given URL with enhanced error handling"""
    try:
        # Create yt-dlp options
        ydl_opts = create_ydl_opts(config)

        # First, try to get info without downloading to check for duplicates
        ydl_opts_info = ydl_opts.copy()
        ydl_opts_info['quiet'] = True

        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)

                if info_dict:
                    # Check if file already exists
                    exists, existing_file = check_file_exists(url, info_dict, config)
                    if exists:
                        logging.info(f"File already exists, skipping: {existing_file}")
                        return f"SKIPPED (exists: {os.path.basename(existing_file)})"

            except Exception:
                # If we can't get info, continue with download anyway
                pass

        # Create progress handler for this download
        progress_handler = DownloadProgress(url, config)
        ydl_opts_copy = ydl_opts.copy()
        ydl_opts_copy['progress_hooks'] = [progress_handler.progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts_copy) as ydl:
            logging.info(f'Starting download: {url}')
            info_dict = ydl.extract_info(url, download=True)

            if info_dict:
                title = info_dict.get('title', 'Unknown Title')
                duration = info_dict.get('duration', 0)
                filesize = info_dict.get('filesize', 0) or info_dict.get('filesize_approx', 0)

                logging.info(f"Successfully downloaded: '{title}'")
                if duration:
                    logging.info(f"Duration: {duration:.2f} seconds")
                if filesize:
                    logging.info(f"File size: {filesize / (1024*1024):.2f} MB")
                return title
            else:
                logging.error(f"No info extracted for: {url}")
                return 'NO INFO EXTRACTED'

    except DownloadError as e:
        error_msg = str(e)
        if 'HTTP Error 404' in error_msg:
            logging.error(f"Content not found (404): {url}")
        elif 'HTTP Error 403' in error_msg:
            logging.error(f"Access forbidden (403): {url}")
        elif 'Unsupported URL' in error_msg:
            logging.error(f"Unsupported URL format: {url}")
        else:
            logging.error(f"Download error for {url}: {error_msg}")
        return 'DOWNLOAD ERROR'

    except ExtractorError as e:
        logging.error(f"Extractor error for {url}: {str(e)}")
        return 'EXTRACTOR ERROR'

    except Exception as e:
        logging.error(f"Unexpected error downloading {url}: {str(e)}")
        return 'UNEXPECTED ERROR'

def main():
    """Main function to process links file"""
    parser = argparse.ArgumentParser(description='Audio downloader from various platforms (v0.31)')
    parser.add_argument('-c', '--config', default='config.json',
                       help='Configuration file (default: config.json)')
    parser.add_argument('-l', '--links',
                       help='Text file containing links to download (overrides config)')
    parser.add_argument('-o', '--output',
                       help='Destination folder for downloads (overrides config)')
    parser.add_argument('-s', '--skip-existing', action='store_true',
                       help='Skip files that already exist (overrides config setting)')
    parser.add_argument('-u', '--url',
                       help='Download single URL directly (ignores links.txt)')

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Override config with command line arguments
    if args.links:
        config['paths']['links_file'] = args.links
    if args.output:
        config['paths']['output_dir'] = args.output
    if args.skip_existing:
        config['behavior']['skip_existing'] = True

    # Setup logging after config is loaded
    setup_logging(config)

    # Show configuration
    logging.info("=== Audio Downloader v0.31 Started ===")
    logging.info(f"Config file: {args.config}")
    logging.info(f"Links file: {config['paths']['links_file']}")
    logging.info(f"Output directory: {config['paths']['output_dir']}")
    logging.info(f"Skip existing files: {config['behavior']['skip_existing']}")
    logging.info(f"Audio format: {config['audio']['codec']} {config['audio']['quality']}kbps {config['audio']['sample_rate']}Hz")

    # Ensure output directory exists
    if not ensure_output_directory(config['paths']['output_dir']):
        logging.error("Cannot proceed without valid output directory")
        return

    # Prepare URLs to process
    if args.url:
        # Single URL mode
        lines = [args.url]
        logging.info(f"Processing single URL: {args.url}")
    else:
        # Links file mode
        try:
            with open(config['paths']['links_file'], 'r', encoding='utf-8') as f:
                lines = f.readlines()
            logging.info(f"Found {len(lines)} lines in {config['paths']['links_file']}")

        except FileNotFoundError:
            logging.error(f"Links file not found: {config['paths']['links_file']}")
            return
        except Exception as e:
            logging.error(f"Error reading links file {config['paths']['links_file']}: {str(e)}")
            return

    processed_count = 0
    success_count = 0
    error_count = 0
    skipped_count = 0

    for i, url in enumerate(lines):
        # Skip commented lines and empty lines
        url = url.strip()
        if not url or url.startswith('#') or not (url.startswith('https://') or url.startswith('http://')):
            continue

        processed_count += 1
        logging.info(f"Processing {processed_count}: {url}")

        title = download_audio(url, config)

        if title.startswith('SKIPPED'):
            skipped_count += 1
            lines[i] = f'# {url} # {title}\n'
        elif title not in ['DOWNLOAD ERROR', 'EXTRACTOR ERROR', 'UNEXPECTED ERROR', 'NO INFO EXTRACTED']:
            success_count += 1
            lines[i] = f'# {url} # {title}\n'
        else:
            error_count += 1
            lines[i] = f'# {url} # ERROR: {title}\n'

        # Update links file after each download (only in links file mode)
        if not args.url:
            try:
                with open(config['paths']['links_file'], 'w', encoding='utf-8') as f:
                    f.write(''.join(lines))
            except Exception as e:
                logging.error(f"Failed to update links file: {str(e)}")

    # Final statistics
    logging.info("=== Download Summary ===")
    logging.info(f"Total processed: {processed_count}")
    logging.info(f"Successful: {success_count}")
    logging.info(f"Skipped (existing): {skipped_count}")
    logging.info(f"Errors: {error_count}")
    logging.info("=== Audio Downloader v0.31 Finished ===")

if __name__ == '__main__':
    main()

