import yt_dlp
import os
from configs.settings import VIDEO_DIR, SUBTITLE_DIR


class YTDownloader:

    def __init__(self):
        os.makedirs(VIDEO_DIR, exist_ok=True)
        os.makedirs(SUBTITLE_DIR, exist_ok=True)

    def fetch_metadata(self, url_or_path):
        """Fetch video metadata from URL or local file."""
        
        # Check if it's a local file
        if os.path.exists(url_or_path):
            video_path = os.path.abspath(url_or_path)
            video_id = os.path.splitext(os.path.basename(video_path))[0]
            
            # For local files, use filename as title
            return {
                "video_id": video_id,
                "title": video_id,
                "channel": "Local Video",
                "url": video_path,
                "is_local": True
            }
        else:
            # YouTube URL
            opts = {
                "quiet": True,
                "no_warnings": True
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url_or_path, download=False)

            return {
                "video_id": info["id"],
                "title": info["title"],
                "channel": info["channel"],
                "url": url_or_path,
                "is_local": False
            }

    def download_subtitles(self, url_or_path):
        """Download subtitles for URL or local file."""
        
        # For local files, check if subtitle already exists
        if os.path.exists(url_or_path):
            video_path = os.path.abspath(url_or_path)
            video_id = os.path.splitext(os.path.basename(video_path))[0]
            
            # Check for existing subtitle in multiple locations
            video_dir = os.path.dirname(video_path)
            possible_subs = [
                f"{video_dir}/{video_id}.en.vtt",
                f"{video_dir}/{video_id}.en.srt",
                f"{video_dir}/{video_id}.vtt",
                f"{video_dir}/{video_id}.srt",
                f"{SUBTITLE_DIR}/{video_id}.en.vtt",
                f"{SUBTITLE_DIR}/{video_id}.en.srt",
            ]
            
            for sub_file in possible_subs:
                if os.path.exists(sub_file):
                    print(f"[INFO] Found subtitle: {sub_file}")
                    return sub_file
            
            # If no subtitle found, return None (pipeline will handle)
            print(f"[INFO] No subtitle found for {video_id}")
            return None
        
        # For YouTube URLs
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
                info = ydl.extract_info(url_or_path, download=True)
        except Exception as e:
            print(f"[INFO] Human subtitles not found, trying auto subtitles...")
            opts["writesubtitles"] = False
            opts["writeautomaticsub"] = True
            
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url_or_path, download=True)
            except Exception as e2:
                print(f"[!] Subtitle download failed: {e2}")
                return None

        video_id = info["id"]

        sub_vtt = f"{SUBTITLE_DIR}/{video_id}.en.vtt"
        sub_srt = f"{SUBTITLE_DIR}/{video_id}.en.srt"

        if os.path.exists(sub_vtt):
            return sub_vtt
        elif os.path.exists(sub_srt):
            return sub_srt
        else:
            return None