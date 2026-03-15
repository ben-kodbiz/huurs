import yt_dlp
import os
from configs.settings import VIDEO_DIR, SUBTITLE_DIR


class YTDownloader:

    def __init__(self):
        os.makedirs(VIDEO_DIR, exist_ok=True)
        os.makedirs(SUBTITLE_DIR, exist_ok=True)

    def fetch_metadata(self, url):
        """Fetch video metadata."""
        opts = {
            "quiet": True,
            "no_warnings": True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "video_id": info["id"],
            "title": info["title"],
            "channel": info["channel"],
            "url": url
        }

    def download_subtitles(self, url):
        """Download subtitles (priority: human > auto)."""
        
        # Try human subtitles first
        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": False,
            "subtitleslangs": ["en"],
            "outtmpl": f"{SUBTITLE_DIR}/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as e:
            # Fallback to auto subtitles
            print(f"[INFO] Human subtitles not found, trying auto subtitles...")
            opts["writesubtitles"] = False
            opts["writeautomaticsub"] = True
            
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
            except Exception as e2:
                print(f"[!] Subtitle download failed: {e2}")
                raise Exception("Subtitles unavailable. Pipeline halted.")

        video_id = info["id"]

        # Check for subtitle file (vtt format)
        sub_vtt = f"{SUBTITLE_DIR}/{video_id}.en.vtt"
        sub_srt = f"{SUBTITLE_DIR}/{video_id}.en.srt"

        if os.path.exists(sub_vtt):
            return sub_vtt
        elif os.path.exists(sub_srt):
            return sub_srt
        else:
            raise Exception("Subtitles unavailable. Pipeline halted.")