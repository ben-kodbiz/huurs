import subprocess
import os
import sqlite3
from configs.settings import FTS_INDEX_DIR


class YTFTSIndexer:

    def __init__(self):
        os.makedirs(FTS_INDEX_DIR, exist_ok=True)

    def index_subtitles(self, subtitle_file, video_id):
        """
        Index subtitles for search.
        
        For offline videos: Creates a simple SQLite database with transcript.
        For YouTube Videos: Uses yt-fts CLI tool.
        """
        
        # Check if this is a local/offline video
        is_local = os.path.exists(subtitle_file)
        
        if is_local:
            return self._index_offline(subtitle_file, video_id)
        else:
            return self._index_youtube(subtitle_file, video_id)
    
    def _index_offline(self, subtitle_file, video_id):
        """Create SQLite index for offline video subtitles."""
        
        db_path = os.path.join(FTS_INDEX_DIR, f"{video_id}.db")
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Create transcripts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transcripts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                text TEXT
            )
        """)
        
        # Parse subtitle file and insert transcripts
        transcripts = self._parse_subtitle(subtitle_file)
        
        for t in transcripts:
            cur.execute(
                "INSERT INTO transcripts (timestamp, text) VALUES (?, ?)",
                (t["timestamp"], t["text"])
            )
        
        conn.commit()
        conn.close()
        
        print(f"[INFO] Created offline index: {db_path}")
        return True
    
    def _parse_subtitle(self, subtitle_file):
        """Parse SRT/VTT subtitle file into transcripts."""
        
        transcripts = []
        
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple SRT parser
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Line 1: sequence number
                # Line 2: timestamp
                # Line 3+: text
                timestamp = lines[1].split(' --> ')[0].strip()
                text = ' '.join(lines[2:])
                
                # Clean text (remove SRT tags)
                text = text.replace('<i>', '').replace('</i>', '')
                text = text.replace('<b>', '').replace('</b>', '')
                text = text.replace('{', '').replace('}', '')
                
                transcripts.append({
                    "timestamp": timestamp,
                    "text": text
                })
        
        return transcripts
    
    def _index_youtube(self, subtitle_file, video_id):
        """Use yt-fts CLI for YouTube videos."""
        
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
            print(f"[WARN] yt-fts output: {result.stderr}")
            # Fallback to offline indexing
            print("[INFO] Falling back to offline indexing...")
            return self._index_offline(subtitle_file, video_id)

        return True