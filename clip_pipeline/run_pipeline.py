"""Clip Mining Pipeline Runner.

Orchestrates the full clip mining workflow:
1. Load transcripts
2. Detect clip candidates
3. Merge adjacent segments
4. Extract video clips
5. Store metadata in database

Supports Hugging Face authentication for private models.
"""

import json
import os
from pathlib import Path
from typing import Optional

from clip_pipeline.detect_clips import ClipDetector
from clip_pipeline.extract_clips import ClipExtractor
from clip_pipeline.clips_db import ClipsDB


def check_hf_auth():
    """Check and setup Hugging Face authentication."""
    hf_token = os.environ.get("HF_TOKEN")
    
    if hf_token:
        print(f"✓ HF_TOKEN found (authenticated)")
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            user = api.whoami(token=hf_token)
            print(f"  Logged in as: {user['name']}")
        except Exception as e:
            print(f"  ⚠️ Token validation failed: {e}")
        return hf_token
    else:
        print("⚠️ No HF_TOKEN - using public models only")
        print("  Set HF_TOKEN env var for private/gated models")
        print("  Get token: https://huggingface.co/settings/tokens")
        return None


class ClipMiningPipeline:
    """Full clip mining pipeline orchestrator."""

    def __init__(
        self,
        video_dir: str = "data/videos",
        output_dir: str = "clips",
        db_path: str = "database/clips.db"
    ):
        """
        Initialize clip mining pipeline.

        Args:
            video_dir: Directory containing source videos.
            output_dir: Directory for extracted clips.
            db_path: Path to clips database.
        """
        self.video_dir = Path(video_dir)
        self.output_dir = Path(output_dir)
        self.db_path = Path(db_path)

        self.detector = ClipDetector()
        self.extractor = ClipExtractor(output_dir=str(self.output_dir))
        self.db = ClipsDB(db_path=str(db_path))

    def run(
        self,
        transcript_path: str,
        video_id: str,
        video_title: str = "",
        extract_clips: bool = True,
        min_emotion_score: int = 7
    ) -> dict:
        """
        Run full clip mining pipeline.

        Args:
            transcript_path: Path to transcript JSON file.
            video_id: Video ID for lookup.
            video_title: Video title for display.
            extract_clips: Whether to extract video clips.
            min_emotion_score: Minimum emotion score for candidates.

        Returns:
            Pipeline results dict.
        """
        print("=" * 60)
        print("CLIP MINING PIPELINE")
        print("=" * 60)
        print(f"Video: {video_id}")
        print(f"Title: {video_title}")
        print(f"Transcript: {transcript_path}")
        print("=" * 60)

        # Step 1: Load transcripts
        print("\n[1/4] Loading transcripts...")
        chunks = self.detector.load_transcripts(transcript_path)
        print(f"✓ Loaded {len(chunks)} transcript chunks")

        # Step 2: Detect clip candidates
        print("\n[2/4] Detecting clip candidates...")
        processed = self.detector.process_batch(chunks)

        # Filter candidates
        candidates = [
            c for c in processed
            if c.get("clip_candidate") and c.get("emotion_score", 0) >= min_emotion_score
        ]
        print(f"✓ Found {len(candidates)} clip candidates (score ≥ {min_emotion_score})")

        # Step 3: Merge adjacent clips
        print("\n[3/4] Merging adjacent clips...")
        merged_clips = self.detector.merge_adjacent_clips(candidates)
        print(f"✓ Merged into {len(merged_clips)} clips")

        # Add video metadata
        for clip in merged_clips:
            clip["video_title"] = video_title

        # Step 4: Extract clips and store in database
        print("\n[4/4] Processing clips...")
        if extract_clips:
            self._extract_and_store(merged_clips, video_id)
        else:
            # Just store metadata
            self.db.insert_clips_batch(merged_clips)
            print(f"✓ Stored {len(merged_clips)} clip records in database")

        # Summary
        stats = self.db.get_stats()
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Total clips in database: {stats['total_clips']}")
        print(f"Videos with clips: {stats['videos_with_clips']}")
        print(f"Average emotion score: {stats['avg_emotion_score']:.1f}")
        print("=" * 60)

        return {
            "video_id": video_id,
            "chunks_processed": len(chunks),
            "candidates_found": len(candidates),
            "clips_created": len(merged_clips),
            "clips": merged_clips
        }

    def _extract_and_store(self, clips: list[dict], video_id: str) -> None:
        """Extract video clips and store in database."""
        # Find video file
        video_file = self._find_video_file(video_id)

        if not video_file:
            print(f"⚠️ Video file not found for {video_id} - storing metadata only")
            self.db.insert_clips_batch(clips)
            return

        print(f"✓ Found video: {video_file}")

        # Extract each clip
        for i, clip in enumerate(clips):
            topic = clip.get("topic", "clip")
            safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:20])
            output_name = f"{video_id}_clip{i:03d}_{safe_topic}"

            try:
                # Extract clip
                clip_path = self.extractor.extract_clip(
                    video_path=str(video_file),
                    start_time=clip["timestamp_start"],
                    end_time=clip["timestamp_end"],
                    output_name=output_name
                )

                # Store in database with file path
                clip["file_path"] = clip_path
                print(f"  ✓ Clip {i+1}/{len(clips)}: {clip_path}")

            except Exception as e:
                print(f"  ✗ Failed to extract clip {i}: {e}")
                clip["file_path"] = None

        # Store all clips in database
        self.db.insert_clips_batch(clips)

    def _find_video_file(self, video_id: str) -> Optional[Path]:
        """Find video file for given video ID."""
        # Try common video extensions
        for ext in ["mp4", "mkv", "avi", "mov", "webm"]:
            video_file = self.video_dir / f"{video_id}.{ext}"
            if video_file.exists():
                return video_file

            # Try with video_id as prefix
            for f in self.video_dir.glob(f"{video_id}*.{ext}"):
                return f

        return None

    def run_from_candidates(
        self,
        candidates_path: str,
        video_id: str,
        video_title: str = "",
        extract_clips: bool = True
    ) -> dict:
        """
        Run pipeline from pre-computed candidates.

        Args:
            candidates_path: Path to JSON file with clip candidates.
            video_id: Video ID.
            video_title: Video title.
            extract_clips: Whether to extract video clips.

        Returns:
            Pipeline results dict.
        """
        print("=" * 60)
        print("CLIP MINING PIPELINE (from candidates)")
        print("=" * 60)

        # Load candidates
        with open(candidates_path, "r", encoding="utf-8") as f:
            candidates = json.load(f)

        print(f"Loaded {len(candidates)} candidates from {candidates_path}")

        # Merge adjacent clips
        merged_clips = self.detector.merge_adjacent_clips(candidates)
        print(f"Merged into {len(merged_clips)} clips")

        # Add video metadata
        for clip in merged_clips:
            clip["video_title"] = video_title

        # Extract and store
        if extract_clips:
            self._extract_and_store(merged_clips, video_id)
        else:
            self.db.insert_clips_batch(merged_clips)

        return {
            "video_id": video_id,
            "clips_created": len(merged_clips),
            "clips": merged_clips
        }

    def close(self):
        """Close database connection."""
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# CLI entry point
def main():
    """Run clip mining pipeline from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Clip Mining Pipeline")
    parser.add_argument(
        "--transcript",
        type=str,
        required=True,
        help="Path to transcript JSON file"
    )
    parser.add_argument(
        "--video-id",
        type=str,
        required=True,
        help="Video ID"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="Video title"
    )
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="Skip video clip extraction (metadata only)"
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=7,
        help="Minimum emotion score for candidates"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="clips",
        help="Output directory for clips"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="database/clips.db",
        help="Path to clips database"
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="Hugging Face token (or set HF_TOKEN env var)"
    )

    args = parser.parse_args()

    # Setup HF authentication
    print("="*60)
    print("HUGGING FACE AUTHENTICATION")
    print("="*60)
    
    # Use provided token or check environment
    if args.hf_token:
        os.environ["HF_TOKEN"] = args.hf_token
    
    hf_token = check_hf_auth()
    
    if hf_token:
        print("\n✓ Authenticated - can access private/gated models")
    else:
        print("\n⚠️ Not authenticated - public models only")
    
    print("="*60)
    print()

    with ClipMiningPipeline(
        output_dir=args.output_dir,
        db_path=args.db_path
    ) as pipeline:
        results = pipeline.run(
            transcript_path=args.transcript,
            video_id=args.video_id,
            video_title=args.title,
            extract_clips=not args.no_extract,
            min_emotion_score=args.min_score
        )

        print(f"\n✓ Pipeline completed successfully!")
        print(f"  Clips created: {results['clips_created']}")


if __name__ == "__main__":
    main()
