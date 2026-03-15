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
            transcripts.text,
            transcripts.summary,
            transcripts.primary_topic,
            transcripts.secondary_topics
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
                "text": row["text"],
                "summary": row["summary"],
                "primary_topic": row["primary_topic"],
                "secondary_topics": row["secondary_topics"]
            })
        
        return results
    
    def search_by_topic(self, topic, limit=20):
        """
        Search by topic classification.
        
        Args:
            topic: Topic name to filter by
            limit: Maximum results to return
            
        Returns:
            List of transcript segments with matching topic
        """
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT
            video_id,
            timestamp,
            text,
            summary,
            primary_topic,
            secondary_topics
        FROM transcripts
        WHERE primary_topic = ?
        LIMIT ?
        """, (topic, limit))
        
        results = []
        for row in cur.fetchall():
            results.append({
                "video_id": row["video_id"],
                "timestamp": row["timestamp"],
                "text": row["text"],
                "summary": row["summary"],
                "primary_topic": row["primary_topic"],
                "secondary_topics": row["secondary_topics"]
            })
        
        return results
    
    def hybrid_search(self, query, topic=None, limit=20):
        """
        Hybrid search: keyword + topic filter.
        
        Args:
            query: Search query string
            topic: Optional topic filter
            limit: Maximum results to return
            
        Returns:
            List of matching transcript segments
        """
        cur = self.conn.cursor()
        
        if topic:
            cur.execute("""
            SELECT
                transcripts.video_id,
                transcripts.timestamp,
                transcripts.text,
                transcripts.summary,
                transcripts.primary_topic,
                transcripts.secondary_topics
            FROM transcript_fts
            JOIN transcripts
            ON transcript_fts.rowid = transcripts.id
            WHERE transcript_fts MATCH ?
            AND transcripts.primary_topic = ?
            LIMIT ?
            """, (query, topic, limit))
        else:
            cur.execute("""
            SELECT
                transcripts.video_id,
                transcripts.timestamp,
                transcripts.text,
                transcripts.summary,
                transcripts.primary_topic,
                transcripts.secondary_topics
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
                "text": row["text"],
                "summary": row["summary"],
                "primary_topic": row["primary_topic"],
                "secondary_topics": row["secondary_topics"]
            })
        
        return results
    
    def get_all_topics(self):
        """Get list of all unique topics."""
        cur = self.conn.cursor()
        
        cur.execute("SELECT DISTINCT primary_topic FROM transcripts WHERE primary_topic IS NOT NULL")
        
        return [row["primary_topic"] for row in cur.fetchall()]
    
    def get_video_transcripts(self, video_id, limit=100):
        """Get all transcripts for a specific video."""
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT
            video_id,
            timestamp,
            text,
            summary,
            primary_topic
        FROM transcripts
        WHERE video_id = ?
        LIMIT ?
        """, (video_id, limit))
        
        results = []
        for row in cur.fetchall():
            results.append({
                "video_id": row["video_id"],
                "timestamp": row["timestamp"],
                "text": row["text"],
                "summary": row["summary"],
                "primary_topic": row["primary_topic"]
            })
        
        return results
    
    def close(self):
        """Close database connection."""
        self.conn.close()
