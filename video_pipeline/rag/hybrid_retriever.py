"""Hybrid Retriever for Per-Video Databases

Supports:
- Single video search
- Multi-video search (across all databases)
- Video-specific filtering
"""

import sqlite3
import json
import math
import re
import os
from database.per_video_db import get_all_video_dbs, PerVideoDB
from modules.tools.embedding_generator import generate_embedding


class HybridRetriever:
    """Hybrid retrieval across per-video databases."""

    def __init__(self, video_id=None):
        """
        Initialize retriever.
        
        Args:
            video_id: Optional. If provided, search only this video.
                     If None, search all videos.
        """
        self.video_id = video_id
        self.connections = {}  # Cache DB connections

    def search(self, query, limit=10, k_factor=60):
        """
        Hybrid search using Reciprocal Rank Fusion (RRF).

        Args:
            query: Search query
            limit: Results to return
            k_factor: RRF constant (lower = more weight to rank)

        Returns:
            List of results ranked by combined score
        """
        # Get keyword results (FTS5)
        keyword_results = self._fts5_search(query, limit=limit*2)

        # Get semantic results (vectors)
        semantic_results = self._vector_search(query, limit=limit*2)

        # Combine with RRF
        fused = self._reciprocal_rank_fusion(
            keyword_results, 
            semantic_results, 
            k=k_factor
        )

        return fused[:limit]

    def _get_db_paths(self):
        """Get database paths to search."""
        if self.video_id:
            # Search specific video
            db_path = PerVideoDB(self.video_id).db_path
            return [db_path] if os.path.exists(db_path) else []
        else:
            # Search all videos
            return get_all_video_dbs()

    def _get_connection(self, db_path):
        """Get or create database connection."""
        if db_path not in self.connections:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            self.connections[db_path] = conn
        return self.connections[db_path]

    def _fts5_search(self, query, limit=20):
        """FTS5 keyword search across databases."""
        all_results = []
        
        for db_path in self._get_db_paths():
            conn = self._get_connection(db_path)
            cur = conn.cursor()
            
            sanitized = self._sanitize_query(query)
            
            # Get video metadata
            cur.execute("SELECT video_id, title FROM videos LIMIT 1")
            video_row = cur.fetchone()
            if not video_row:
                continue
            
            video_id = video_row["video_id"]
            video_title = video_row["title"]
            
            cur.execute("""
            SELECT
                t.id,
                t.video_id,
                t.timestamp,
                t.text,
                'keyword' as source
            FROM transcript_fts
            JOIN transcripts t ON transcript_fts.rowid = t.id
            WHERE transcript_fts MATCH ?
            LIMIT ?
            """, (sanitized, limit))

            for rank, row in enumerate(cur.fetchall(), 1):
                all_results.append({
                    "id": f"{db_path}:{row['id']}",
                    "video_id": row["video_id"],
                    "video_title": video_title,
                    "timestamp": row["timestamp"],
                    "text": row["text"],
                    "source": "keyword",
                    "rank": rank,
                    "db_path": db_path
                })

        return all_results

    def _vector_search(self, query, limit=20):
        """Semantic search using embeddings."""
        all_results = []
        query_embedding = generate_embedding(query)

        for db_path in self._get_db_paths():
            conn = self._get_connection(db_path)
            cur = conn.cursor()
            
            # Get video metadata
            cur.execute("SELECT video_id, title FROM videos LIMIT 1")
            video_row = cur.fetchone()
            if not video_row:
                continue
            
            video_id = video_row["video_id"]
            video_title = video_row["title"]
            
            cur.execute("""
            SELECT id, video_id, timestamp, text, embedding
            FROM enriched_transcripts
            WHERE embedding IS NOT NULL
            """)

            results = []
            for row in cur.fetchall():
                if row["embedding"]:
                    chunk_embedding = json.loads(row["embedding"])
                    similarity = self._cosine_similarity(query_embedding, chunk_embedding)

                    results.append({
                        "id": f"{db_path}:{row['id']}",
                        "video_id": row["video_id"],
                        "video_title": video_title,
                        "timestamp": row["timestamp"],
                        "text": row["text"],
                        "source": "semantic",
                        "similarity": similarity,
                        "db_path": db_path
                    })

            # Sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)

            # Add rank
            for rank, result in enumerate(results[:limit], 1):
                result["rank"] = rank

            all_results.extend(results[:limit])

        return all_results

    def _reciprocal_rank_fusion(self, keyword_results, semantic_results, k=60):
        """Combine results using Reciprocal Rank Fusion."""
        scores = {}

        # Score keyword results
        for result in keyword_results:
            result_id = result["id"]
            if result_id not in scores:
                scores[result_id] = {**result, "rrf_score": 0}
            scores[result_id]["rrf_score"] += 1.0 / (k + result["rank"])

        # Score semantic results
        for result in semantic_results:
            result_id = result["id"]
            if result_id not in scores:
                scores[result_id] = {**result, "rrf_score": 0}
            scores[result_id]["rrf_score"] += 1.0 / (k + result["rank"])

        # Sort by RRF score
        fused = sorted(scores.values(), key=lambda x: x["rrf_score"], reverse=True)

        # Add final rank
        for rank, result in enumerate(fused, 1):
            result["final_rank"] = rank

        return fused

    def _sanitize_query(self, query):
        """Sanitize query for FTS5."""
        query = query.replace('-', ' ')
        special_chars = ['"', '*', '+', '~', '(', ')', '<', '>', '@']
        for char in special_chars:
            query = query.replace(char, '')
        query = re.sub(r'[^\w\s]', '', query)
        words = query.split()
        return ' OR '.join(words) if len(words) > 1 else ' '.join(words)

    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity."""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0

    def close(self):
        """Close all database connections."""
        for conn in self.connections.values():
            conn.close()
        self.connections.clear()

    def get_all_videos(self):
        """Get list of all videos with stats."""
        videos = []
        
        for db_path in get_all_video_dbs():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute("SELECT video_id, title, channel FROM videos LIMIT 1")
            video_row = cur.fetchone()
            
            if video_row:
                cur.execute("SELECT COUNT(*) FROM transcripts")
                transcript_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM enriched_transcripts")
                enriched_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM enriched_transcripts WHERE embedding IS NOT NULL")
                embedded_count = cur.fetchone()[0]
                
                videos.append({
                    "video_id": video_row["video_id"],
                    "title": video_row["title"],
                    "channel": video_row["channel"],
                    "db_path": db_path,
                    "transcripts": transcript_count,
                    "enriched": enriched_count,
                    "with_embeddings": embedded_count
                })
            
            conn.close()
        
        return videos


# Test
if __name__ == "__main__":
    retriever = HybridRetriever()
    
    # Show available videos
    print("Available videos:")
    for video in retriever.get_all_videos():
        print(f"  - {video['title'][:50]}...")
        print(f"    Transcripts: {video['transcripts']}, Enriched: {video['enriched']}, Embeddings: {video['with_embeddings']}")
    
    # Test search
    test_queries = [
        "What is Surah Al Mulk?",
        "patience",
        "hellfire protection"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)

        results = retriever.search(query, limit=3)

        for i, r in enumerate(results, 1):
            print(f"\n{i}. [RRF: {r['rrf_score']:.4f}] {r['video_title'][:40]}... @ {r['timestamp']}")
            print(f"   Text: {r['text'][:100]}...")

    retriever.close()
