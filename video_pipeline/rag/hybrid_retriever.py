"""Hybrid Retriever - Combine FTS5 keyword + vector search."""

import sqlite3
import json
import math
import re
from configs.settings import DATABASE_PATH
from modules.tools.embedding_generator import generate_embedding


class HybridRetriever:
    """Hybrid retrieval combining keyword and semantic search."""

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

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

    def _fts5_search(self, query, limit=20):
        """FTS5 keyword search."""
        sanitized = self._sanitize_query(query)

        cur = self.conn.cursor()
        cur.execute("""
        SELECT 
            transcripts.id,
            transcripts.video_id,
            transcripts.timestamp,
            transcripts.text,
            'keyword' as source
        FROM transcript_fts
        JOIN transcripts ON transcript_fts.rowid = transcripts.id
        WHERE transcript_fts MATCH ?
        LIMIT ?
        """, (sanitized, limit))

        results = []
        for rank, row in enumerate(cur.fetchall(), 1):
            results.append({
                "id": row["id"],
                "video_id": row["video_id"],
                "timestamp": row["timestamp"],
                "text": row["text"],
                "source": "keyword",
                "rank": rank
            })

        return results

    def _vector_search(self, query, limit=20):
        """Semantic search using embeddings."""
        query_embedding = generate_embedding(query)

        cur = self.conn.cursor()
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
                    "id": row["id"],
                    "video_id": row["video_id"],
                    "timestamp": row["timestamp"],
                    "text": row["text"],
                    "source": "semantic",
                    "similarity": similarity
                })

        # Sort by similarity (descending)
        results.sort(key=lambda x: x["similarity"], reverse=True)

        # Add rank
        for rank, result in enumerate(results[:limit], 1):
            result["rank"] = rank

        return results[:limit]

    def _reciprocal_rank_fusion(self, keyword_results, semantic_results, k=60):
        """
        Combine results using Reciprocal Rank Fusion.

        RRF Score = Σ 1 / (k + rank)

        Args:
            keyword_results: FTS5 results
            semantic_results: Vector results
            k: Constant (typically 60)

        Returns:
            Fused and ranked results
        """
        scores = {}

        # Score keyword results
        for result in keyword_results:
            chunk_id = result["id"]
            if chunk_id not in scores:
                scores[chunk_id] = {**result, "rrf_score": 0}
            scores[chunk_id]["rrf_score"] += 1.0 / (k + result["rank"])

        # Score semantic results
        for result in semantic_results:
            chunk_id = result["id"]
            if chunk_id not in scores:
                scores[chunk_id] = {**result, "rrf_score": 0}
            scores[chunk_id]["rrf_score"] += 1.0 / (k + result["rank"])

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
        """Close database connection."""
        self.conn.close()


# Test
if __name__ == "__main__":
    retriever = HybridRetriever()

    test_queries = [
        "What is patience?",
        "charity in Islam",
        "Surah ar-rahman",
        "forgiveness"
    ]

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)

        results = retriever.search(query, limit=3)

        for i, r in enumerate(results, 1):
            print(f"\n{i}. [RRF: {r['rrf_score']:.4f}] {r['video_id'][:40]}... @ {r['timestamp']}")
            print(f"   Text: {r['text'][:100]}...")

    retriever.close()
