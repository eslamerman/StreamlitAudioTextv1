import os
import boto3
import yt_dlp

class YouTubeDownloader:
    """Handles downloading audio from YouTube."""
    def __init__(self, output_path, cookie_path=None):
        self.output_path = output_path
        self.cookie_path = cookie_path or "cookies.txt" 

    def download_audio(self, url):
        """Download YouTube video audio as MP3."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
          #  'proxy': 'http://3.212.148.199:80',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            }
        }


        # Add cookies to options if provided
        if self.cookie_path:
            ydl_opts['cookiefile'] = self.cookie_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                audio_filename = ydl.prepare_filename(info)
                audio_filename = os.path.splitext(audio_filename)[0] + '.mp3'
                return info.get('title', 'Unknown Title'), audio_filename
            except Exception as e:
                raise Exception(f"Error downloading audio: {str(e)}")

class S3Uploader:
    """Handles uploading files to S3."""
    def __init__(self, bucket_name, s3_client):
        self.bucket_name = bucket_name
        self.s3_client = s3_client

    def upload(self, file_path, s3_key):
        """Upload a file to S3."""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            return f"s3://{self.bucket_name}/{s3_key}"
        except Exception as e:
            raise Exception(f"Error uploading to S3: {str(e)}")
