from transcriptor.youtube.youtube_functions import YouTubeTranscriptDownloader
import time
import logging
import os
logger = logging.getLogger('youtube transcript')

def execute_transcript_youtube(args):
    url=args.url
    logger.info(f"Started at {time.strftime('%H:%M:%S')}")
    start_time = time.time()
    path_processed = os.path.normpath(args.path_processed)

    # Example usage:
    # Initialize the downloader with a language parameter
    downloader = YouTubeTranscriptDownloader(
        output_dir=path_processed,
        ffmpeg_path=os.path.normpath(args.ffmpeg_path),
        language="pt"  # For a list use this link https://github.com/yt-dlp/yt-dlp/issues/2205
    )
    # Pass a single video URL or playlist URL
    downloader.download_transcripts(url)
