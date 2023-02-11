import os

import yt_dlp


class YoutubeDownloader:
    def __init__(self, url, download_path="."):
        # Ensure directory exists
        if not os.path.isdir(download_path):
            os.makedirs(download_path)

        self.url = url
        self.download_path = download_path
        metadata = self.get_metadata()

        self.duration = metadata["duration"]
        self.title = metadata["title"]

        # Replace backward slash with space
        self.title = self.title.replace("\\", " ")
        self.title = self.title.replace("/", " ")

    def get_metadata(self):
        opts = {"skip_download": True, "quiet": True}

        metadata = {}

        with yt_dlp.YoutubeDL(opts) as ydl:
            yt_info = ydl.extract_info(self.url, download=False)
            metadata["title"] = yt_info.get("title", "NO TITLE")
            metadata["duration"] = yt_info["duration"]
        return metadata

    def download_video_to_mp3(self):
        title = self.title
        filename = f"{title}.mp3"
        filename = os.path.join(self.download_path, filename)

        opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
            "quiet": True,
            "outtmpl": filename,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            error_code = ydl.download(self.url)
        return error_code, filename

    def get_video_thumbnail(self):
        title = self.title
        filename = f"{title}"
        filename = os.path.join(self.download_path, filename)

        opts = {
            "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "writethumbnail": True,
            "postprocessors": [
                {
                    "format": "jpg",
                    "key": "FFmpegThumbnailsConvertor",
                    "when": "before_dl",
                }
            ],
            "skip_download": True,
            "outtmpl": filename,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            error_code = ydl.download(self.url)

        filename = f"{filename}.jpg" if not filename.endswith(".jpg") else filename
        return error_code, filename
