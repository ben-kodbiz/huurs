import yt_dlp
import os
from configs.settings import VIDEO_DIR, SUBTITLE_DIR


class YTDownloader:

    def __init__(self):

        os.makedirs(VIDEO_DIR, exist_ok=True)
        os.makedirs(SUBTITLE_DIR, exist_ok=True)

    def fetch_metadata(self, url):

        opts = {"quiet": True}

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "video_id": info["id"],
            "title": info["title"],
            "channel": info["channel"],
            "url": url
        }


    def download_subtitles(self, url):

        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "outtmpl": f"{SUBTITLE_DIR}/%(id)s.%(ext)s"
        }

        with yt_dlp.YoutubeDL(opts) as ydl:

            info = ydl.extract_info(url, download=True)

            video_id = info["id"]

        sub_vtt = f"{SUBTITLE_DIR}/{video_id}.en.vtt"

        if not os.path.exists(sub_vtt):

            raise Exception("Subtitles unavailable. Pipeline halted.")

        return sub_vtt