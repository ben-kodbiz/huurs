"""Search enriched transcripts with topics and summaries."""

import sqlite3
import json
import math
from configs.settings import DATABASE_PATH
from modules.tools.embedding_generator import generate_embedding


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
    
    def semantic_search(self, query, limit=10):
        """
        Semantic search using vector embeddings.
        
        Args:
            query: Search query
            limit: Results to return
            
        Returns:
            List of chunks ranked by similarity
        """
        cur = self.conn.cursor()
        
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Get all chunks with embeddings
        cur.execute("""
        SELECT id, video_id, timestamp, text, summary, topic, embedding
        FROM enriched_transcripts
        WHERE embedding IS NOT NULL
        """)
        
        results = []
        for row in cur.fetchall():
            embedding_json = row["embedding"]
            if embedding_json:
                chunk_embedding = json.loads(embedding_json)
                similarity = cosine_similarity(query_embedding, chunk_embedding)
                
                results.append({
                    "id": row["id"],
                    "video_id": row["video_id"],
                    "timestamp": row["timestamp"],
                    "text": row["text"],
                    "summary": row["summary"],
                    "topic": row["topic"],
                    "similarity": similarity
                })
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]
    
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
    
    def has_embeddings(self):
        """Check if embeddings are available."""
        cur = self.conn.cursor()
        cur.execute("""
        SELECT COUNT(*) FROM enriched_transcripts 
        WHERE embedding IS NOT NULL
        """)
        return cur.fetchone()[0] > 0
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)
