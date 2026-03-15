import sqlite3
from configs.settings import DATABASE_PATH


class VideoSearch:
    """Search engine for video transcripts using FTS5."""
    
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def search(self, query, limit=20):
        """
        Keyword search using FTS5.
        
        Args:
            query: Search query string
            limit: Maximum results to return
            
        Returns:
            List of matching transcript segments
        """
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT
            transcripts.video_id,
            transcripts.timestamp,
            transcripts.text
        FROM transcript_fts
        JOIN transcripts
        ON transcript_fts.rowid = transcripts.id
        WHERE transcript_fts MATCH ?
        LIMIT ?
        """, (query, limit))
        
        results = []
        for row in cur.fetchall():
            results.append({
                "video_id": row["video_id"],
                "timestamp": row["timestamp"],
                "text": row["text"]
            })
        
        return results
    
    def get_video_transcripts(self, video_id, limit=100):
        """Get all transcripts for a specific video."""
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT
            video_id,
            timestamp,
            text
        FROM transcripts
        WHERE video_id = ?
        LIMIT ?
        """, (video_id, limit))
        
        results = []
        for row in cur.fetchall():
            results.append({
                "video_id": row["video_id"],
                "timestamp": row["timestamp"],
                "text": row["text"]
            })
        
        return results
    
    def get_all_videos(self):
        """Get list of all videos in database."""
        cur = self.conn.cursor()
        
        cur.execute("SELECT video_id, title, channel FROM videos")
        
        return [dict(row) for row in cur.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
