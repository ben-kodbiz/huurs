"""Clip Mining Pipeline for Islamic Lectures.

This package provides tools for:
- Detecting viral clip candidates from lecture transcripts
- Extracting video clips using ffmpeg
- Managing clip metadata in the database
- RAG integration for clip-aware search
- Hugging Face authentication for private models
"""

from clip_pipeline.detect_clips import ClipDetector
from clip_pipeline.extract_clips import ClipExtractor
from clip_pipeline.clips_db import ClipsDB
from clip_pipeline.clip_retriever import ClipRetriever, RAGEngineWithClips
from clip_pipeline.run_pipeline import ClipMiningPipeline, check_hf_auth

__all__ = [
    "ClipDetector",
    "ClipExtractor",
    "ClipsDB",
    "ClipRetriever",
    "RAGEngineWithClips",
    "ClipMiningPipeline",
    "check_hf_auth"
]
