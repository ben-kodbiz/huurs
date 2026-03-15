"""Search enriched transcripts with topics and summaries."""

import sqlite3
from configs.settings import DATABASE_PATH


class EnrichedSearch:
    """Search enriched transcripts by topic and summary."""
    
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def search_by_topic(self, topic, limit=20):
        """Search transcripts by topic."""
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT video_id, timestamp, text, summary, topic
        FROM enriched_transcripts
        WHERE topic = ?
        LIMIT ?
        """, (topic, limit))
        
        return [dict(row) for row in cur.fetchall()]
    
    def search_summary(self, query, limit=20):
        """Search transcripts by keyword in summary."""
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT video_id, timestamp, text, summary, topic
        FROM enriched_transcripts
        WHERE summary LIKE ?
        LIMIT ?
        """, (f'%{query}%', limit))
        
        return [dict(row) for row in cur.fetchall()]
    
    def get_all_topics(self):
        """Get list of all topics with counts."""
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT topic, COUNT(*) as count
        FROM enriched_transcripts
        GROUP BY topic
        ORDER BY count DESC
        """)
        
        return [dict(row) for row in cur.fetchall()]
    
    def get_chunk(self, timestamp):
        """Get a specific chunk by timestamp."""
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT video_id, timestamp, text, summary, topic
        FROM enriched_transcripts
        WHERE timestamp = ?
        """, (timestamp,))
        
        row = cur.fetchone()
        return dict(row) if row else None
    
    def close(self):
        """Close database connection."""
        self.conn.close()
