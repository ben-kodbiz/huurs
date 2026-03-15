import subprocess
import os
from configs.settings import FTS_INDEX_DIR


class YTFTSIndexer:

    def __init__(self):

        os.makedirs(FTS_INDEX_DIR, exist_ok=True)

    def index_subtitles(self, subtitle_file, video_id):

        cmd = [
            "yt-fts",
            "index",
            subtitle_file,
            "--index-dir",
            FTS_INDEX_DIR,
            "--video-id",
            video_id
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:

            raise Exception("yt-fts indexing failed")

        return True