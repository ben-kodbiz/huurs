"""RAG Retriever Module - Search transcript chunks."""

import sqlite3
import re
from configs.settings import DATABASE_PATH


class Retriever:
    """Retrieve relevant transcript chunks from SQLite."""
    
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def search_transcripts(self, query, limit=10):
        """
        Search for transcript chunks matching the query.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of transcript chunks with video_id, timestamp, text
        """
        # Sanitize query for FTS5 - remove special characters
        query = self._sanitize_query(query)
        
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
    
    def _sanitize_query(self, query):
        """Sanitize query string for FTS5."""
        # Remove FTS5 special characters
        special_chars = ['"', '*', '-', '+', '~', '(', ')', '<', '>', '@']
        for char in special_chars:
            query = query.replace(char, '')
        
        # Keep only alphanumeric and spaces
        query = re.sub(r'[^\w\s]', '', query)
        
        # Normalize whitespace
        query = ' '.join(query.split())
        
        return query
    
    def close(self):
        """Close database connection."""
        self.conn.close()
