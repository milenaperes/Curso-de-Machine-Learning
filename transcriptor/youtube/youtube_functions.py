import logging
from tqdm import tqdm
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from docx import Document
import re
import os


class YouTubeTranscriptDownloader:
    def __init__(self, output_dir='transcripts', ffmpeg_path=None, language='pt-BR', log_file='transcripts.log'):
        # Directory to save transcript files
        self.output_dir = output_dir
        self.ffmpeg_path = ffmpeg_path
        self.language = language  # Preferred language for the transcript or subtitle
        self.fallback_language = None  # Will be set dynamically

        # Configure logging
        logging.basicConfig(
            filename=log_file,
            filemode='w',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # yt-dlp options
        self.ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'writesubtitles': True,
            'subtitleslangs': [self.language],  # Preferred language
            'subtitlesformat': 'ttml',
            'outtmpl': f"{self.output_dir}/%(title)s.%(ext)s",
            'ffmpeg_location': self.ffmpeg_path,
        }

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', '_', filename)

    def save_to_docx(self, content, title):
        sanitized_title = self.sanitize_filename(title)
        transcript_path = os.path.join(self.output_dir, f"{sanitized_title}.docx")
        doc = Document()
        doc.add_heading(title, 0)
        for line in content:
            doc.add_paragraph(line)
        doc.save(transcript_path)
        self.logger.info(f"Transcript saved: {transcript_path}")

    def detect_original_language(self, video_url):
        with YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)
            self.fallback_language = video_info.get('original_language', 'en')
            self.logger.info(f"Detected original language: {self.fallback_language}")
            self.ydl_opts['subtitleslangs'].append(self.fallback_language)

    def fetch_video_transcripts_or_captions(self, video_url):
        self.detect_original_language(video_url)
        with YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)
            video_title = video_info.get('title', 'Unknown Title')
            video_id = video_info.get('id')

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[self.language])
            content = [entry['text'] for entry in transcript]
            self.save_to_docx(content, video_title)
        except NoTranscriptFound:
            self.logger.warning(f"No transcript found for {video_title} in {self.language}. Trying fallback language...")
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[self.fallback_language])
                content = [entry['text'] for entry in transcript]
                self.save_to_docx(content, video_title)
            except NoTranscriptFound:
                self.logger.warning(f"No transcript found for {video_title} in fallback language {self.fallback_language}.")
                self.fetch_subtitles(video_url, video_title)
        except TranscriptsDisabled:
            self.logger.warning(f"Transcripts are disabled for {video_title}. Trying captions...")
            self.fetch_subtitles(video_url, video_title)

    def fetch_subtitles(self, video_url, video_title):
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                subtitle_path = os.path.join(self.output_dir, f"{self.sanitize_filename(video_title)}.ttml")

                if os.path.exists(subtitle_path):
                    self.logger.info(f"Captions saved: {subtitle_path}")
                    with open(subtitle_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.save_to_docx([content], video_title)
                    os.remove(subtitle_path)
                else:
                    self.logger.warning(f"No captions available for {video_title}.")
        except Exception as e:
            self.logger.error(f"Failed to fetch captions for {video_title}: {e}")

    def is_playlist(self, url):
        return "playlist" in url or "&list=" in url

    def fetch_playlist_videos(self, playlist_url):
        with YoutubeDL(self.ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            entries = playlist_info.get('entries', [])
            return [f"https://www.youtube.com/watch?v={entry.get('id')}" for entry in entries if entry.get('id')]

    def download_transcripts(self, url):
        if self.is_playlist(url):
            video_urls = self.fetch_playlist_videos(url)
            self.logger.info(f"Found {len(video_urls)} videos in playlist.")
            for video_url in tqdm(video_urls, desc="Downloading transcripts", unit="video"):
                self.fetch_video_transcripts_or_captions(video_url)
        else:
            self.fetch_video_transcripts_or_captions(url)
