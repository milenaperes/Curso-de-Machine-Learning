from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
from docx import Document
import re
import os


class YouTubeTranscriptDownloader:
    def __init__(self, output_dir='transcripts', ffmpeg_path=None):
        # Directory to save transcript files
        self.output_dir = output_dir
        self.ffmpeg_path = ffmpeg_path
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    @staticmethod
    def sanitize_filename(filename):
        # Replace invalid filename characters with underscores
        return re.sub(r'[\\/*?:"<>|]', '_', filename)

    def fetch_video_transcripts(self, video_url):
        """Fetch and save the transcript for a single video."""
        ydl_opts = {
            'quiet': True,
            'ffmpeg_location': self.ffmpeg_path,  # Custom ffmpeg path
        }

        with YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)
            video_title = video_info.get('title', 'Unknown Title')
            video_id = video_info.get('id')

        sanitized_title = self.sanitize_filename(video_title)
        transcript_path = os.path.join(self.output_dir, f"{sanitized_title}.docx")

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            doc = Document()
            doc.add_heading(video_title, 0)

            for entry in transcript:
                doc.add_paragraph(entry['text'])

            doc.save(transcript_path)
            print(f"Transcript saved: {transcript_path}")
        except Exception as e:
            print(f"Failed to fetch transcript for {video_title}: {e}")

    def fetch_playlist_transcripts(self, playlist_url):
        """Fetch and save transcripts for all videos in a playlist."""
        ydl_opts = {
            'quiet': True,
            'ffmpeg_location': self.ffmpeg_path,
            'retries': 10,  # Increase the number of retries
            'sleep_interval_requests': 2,  # Add a delay between retries to avoid rate limits
            'sleep_interval': 2,  # Delay between API calls
        }

        with YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            entries = playlist_info.get('entries', [])
            print(f"Found {len(entries)} videos in playlist.")

            for video in entries:
                video_url = video.get('url')
                self.fetch_video_transcripts(video_url)

    def download_transcripts(self, url):
        """Determine if the URL is a playlist or video and fetch transcripts."""
        ydl_opts = {
            'quiet': True,
            'ffmpeg_location': self.ffmpeg_path,  # Custom ffmpeg path
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:  # Playlist detected
                self.fetch_playlist_transcripts(url)
            else:  # Single video detected
                self.fetch_video_transcripts(url)

# Example usage:
# Initialize the downloader
downloader = YouTubeTranscriptDownloader(output_dir='A:/Gravações/transcript',
                                         ffmpeg_path="E:/PycharmProjects/transcriptor/transcriptor/ffmpeg/bin/ffmpeg.exe"
                                         )

# Pass a single video URL or playlist URL
url = "https://www.youtube.com/watch?v=Pny70rNPJLk"
downloader.download_transcripts(url)
