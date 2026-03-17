"""Clip-Aware Retriever for RAG System.

Extends HybridRetriever to include clip candidates in search results.
Allows users to discover and reference viral clip moments.
"""

import sqlite3
import sys
from pathlib import Path

# Add video_pipeline to path for imports
video_pipeline_path = Path(__file__).parent.parent / "video_pipeline"
if str(video_pipeline_path) not in sys.path:
    sys.path.insert(0, str(video_pipeline_path))

from rag.hybrid_retriever import HybridRetriever
from clip_pipeline.clips_db import ClipsDB


class ClipRetriever:
    """Retrieve clips and transcripts for RAG queries."""

    def __init__(self, clips_db_path: str = "database/clips.db"):
        """
        Initialize clip retriever.

        Args:
            clips_db_path: Path to clips database.
        """
        self.clips_db = ClipsDB(db_path=clips_db_path)
        self.hybrid_retriever = HybridRetriever()

    def search_with_clips(
        self,
        query: str,
        limit: int = 10,
        include_clips: bool = True,
        clip_limit: int = 5,
        min_emotion_score: int = 7
    ) -> dict:
        """
        Search with clip integration.

        Args:
            query: Search query.
            limit: Number of transcript chunks to return.
            include_clips: Whether to include clip results.
            clip_limit: Maximum number of clips to return.
            min_emotion_score: Minimum emotion score for clips.

        Returns:
            Dict with transcript chunks and clip results.
        """
        results = {
            "query": query,
            "chunks": [],
            "clips": [],
            "clip_references": []
        }

        # Step 1: Search for relevant clips by topic
        if include_clips:
            # Search clips by topic matching query keywords
            clips = self.clips_db.search_clips(query, limit=clip_limit)
            
            # Filter by emotion score
            clips = [
                c for c in clips
                if c["emotion_score"] >= min_emotion_score
            ]

            for clip in clips:
                results["clips"].append({
                    "id": clip["id"],
                    "video_id": clip["video_id"],
                    "video_title": clip["video_title"],
                    "timestamp_start": clip["timestamp_start"],
                    "timestamp_end": clip["timestamp_end"],
                    "duration": clip["duration"],
                    "topic": clip["topic"],
                    "emotion_score": clip["emotion_score"],
                    "file_path": clip["file_path"]
                })

        # Step 2: Search transcripts using hybrid retriever
        chunks = self.hybrid_retriever.search(query, limit=limit)

        for chunk in chunks:
            results["chunks"].append({
                "video_id": chunk["video_id"],
                "video_title": chunk["video_title"],
                "timestamp": chunk["timestamp"],
                "text": chunk["text"],
                "source": chunk.get("source", "hybrid"),
                "rrf_score": chunk.get("rrf_score", 0)
            })

            # Step 3: Check if this chunk overlaps with any clip
            if include_clips:
                overlapping_clips = self._find_overlapping_clips(
                    chunk["video_id"],
                    chunk["timestamp"],
                    results["clips"]
                )
                if overlapping_clips:
                    results["clip_references"].append({
                        "chunk_timestamp": chunk["timestamp"],
                        "clips": overlapping_clips
                    })

        return results

    def _find_overlapping_clips(
        self,
        video_id: str,
        timestamp: str,
        clips: list
    ) -> list:
        """Find clips that overlap with a timestamp."""
        if not timestamp or not clips:
            return []

        # Parse timestamp to seconds
        chunk_seconds = self._parse_timestamp(timestamp)

        overlapping = []
        for clip in clips:
            if clip["video_id"] != video_id:
                continue

            clip_start = clip["timestamp_start"]
            clip_end = clip["timestamp_end"]

            start_seconds = self._parse_timestamp(clip_start)
            end_seconds = self._parse_timestamp(clip_end)

            if start_seconds <= chunk_seconds <= end_seconds:
                overlapping.append({
                    "id": clip["id"],
                    "timestamp_start": clip_start,
                    "timestamp_end": clip_end,
                    "topic": clip["topic"],
                    "emotion_score": clip["emotion_score"]
                })

        return overlapping

    def get_clips_for_video(self, video_id: str, limit: int = 50) -> list:
        """Get all clips for a specific video."""
        clips = self.clips_db.get_clips_by_video(video_id, limit=limit)
        return [
            {
                "id": clip["id"],
                "video_id": clip["video_id"],
                "video_title": clip["video_title"],
                "timestamp_start": clip["timestamp_start"],
                "timestamp_end": clip["timestamp_end"],
                "duration": clip["duration"],
                "topic": clip["topic"],
                "emotion_score": clip["emotion_score"],
                "file_path": clip["file_path"]
            }
            for clip in clips
        ]

    def get_top_clips(self, limit: int = 20) -> list:
        """Get top clips by emotion score."""
        clips = self.clips_db.get_top_clips(limit=limit)
        return [
            {
                "id": clip["id"],
                "video_id": clip["video_id"],
                "video_title": clip["video_title"],
                "timestamp_start": clip["timestamp_start"],
                "timestamp_end": clip["timestamp_end"],
                "duration": clip["duration"],
                "topic": clip["topic"],
                "emotion_score": clip["emotion_score"],
                "file_path": clip["file_path"]
            }
            for clip in clips
        ]

    def get_clips_by_topic(self, topic: str, limit: int = 20) -> list:
        """Get clips by topic."""
        clips = self.clips_db.get_clips_by_topic(topic, limit=limit)
        return [
            {
                "id": clip["id"],
                "video_id": clip["video_id"],
                "video_title": clip["video_title"],
                "timestamp_start": clip["timestamp_start"],
                "timestamp_end": clip["timestamp_end"],
                "duration": clip["duration"],
                "topic": clip["topic"],
                "emotion_score": clip["emotion_score"],
                "file_path": clip["file_path"]
            }
            for clip in clips
        ]

    def _parse_timestamp(self, timestamp: str) -> float:
        """Parse timestamp to seconds."""
        if not timestamp:
            return 0.0
        parts = timestamp.replace(".", ":").split(":")
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return 0.0

    def close(self):
        """Close database connections."""
        self.clips_db.close()
        self.hybrid_retriever.close()


# Extended RAG Engine with clip support
class RAGEngineWithClips:
    """RAG Engine with clip integration."""

    def __init__(self, clips_db_path: str = "database/clips.db"):
        """
        Initialize RAG engine with clips.

        Args:
            clips_db_path: Path to clips database.
        """
        from rag.rag_engine import RAGEngine
        self.base_engine = RAGEngine()
        self.clip_retriever = ClipRetriever(clips_db_path)

    def answer_with_clips(
        self,
        question: str,
        limit: int = 10,
        clip_limit: int = 5,
        return_chunks_only: bool = False
    ) -> dict:
        """
        Answer question with clip integration.

        Args:
            question: User's question.
            limit: Number of transcript chunks.
            clip_limit: Maximum number of clips to include.
            return_chunks_only: Return chunks instead of answer.

        Returns:
            Dict with answer, sources, and clip references.
        """
        # Get search results with clips
        results = self.clip_retriever.search_with_clips(
            question,
            limit=limit,
            include_clips=True,
            clip_limit=clip_limit
        )

        if return_chunks_only:
            return {
                "chunks": results["chunks"],
                "clips": results["clips"]
            }

        # Get base answer from RAG engine
        base_result = self.base_engine.answer_question(
            question,
            limit=limit,
            return_chunks_only=False
        )

        # Add clip information
        base_result["clips"] = results["clips"]
        base_result["clip_references"] = results["clip_references"]

        # Add clip notice to answer if clips available
        if results["clips"]:
            clip_notice = f"\n\n🎬 Found {len(results['clips'])} relevant clip(s) for this topic!"
            base_result["answer"] += clip_notice

        return base_result

    def close(self):
        """Close resources."""
        self.base_engine.close()
        self.clip_retriever.close()


# Test
if __name__ == "__main__":
    print("Testing Clip Retriever...")

    retriever = ClipRetriever()

    # Test search with clips
    test_query = "charity"
    print(f"\nQuery: {test_query}")
    print("=" * 60)

    results = retriever.search_with_clips(test_query, limit=5, clip_limit=3)

    print(f"\nClips found: {len(results['clips'])}")
    for i, clip in enumerate(results["clips"], 1):
        print(
            f"  {i}. 🎬 {clip['video_title'][:40]}... | "
            f"{clip['timestamp_start']}-{clip['timestamp_end']} | "
            f"Topic: {clip['topic']} | Score: {clip['emotion_score']}"
        )

    print(f"\nTranscript chunks: {len(results['chunks'])}")
    for i, chunk in enumerate(results["chunks"][:3], 1):
        print(
            f"  {i}. {chunk['video_title'][:40]}... @ {chunk['timestamp']}"
        )
        print(f"     Text: {chunk['text'][:100]}...")

    retriever.close()
