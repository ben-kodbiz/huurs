"""Use processed_chunks.json from video pipeline for clip mining.

This skips redundant topic classification and just adds:
- Timestamp format conversion
- Emotion scoring
- Clip candidate detection

Usage:
    python clip_pipeline/use_processed_chunks.py
"""

import json
from clip_pipeline.detect_clips import ClipDetector
from clip_pipeline.clips_db import ClipsDB
from clip_pipeline.extract_clips import ClipExtractor


def seconds_to_mmss(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def process_existing_chunks(input_path: str, output_db: str = "database/clips.db"):
    """Process already-classified chunks for clip mining."""
    
    print("="*60)
    print("CLIP MINING FROM PROCESSED CHUNKS")
    print("="*60)
    
    # Load processed chunks from video pipeline
    with open(input_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} processed chunks from {input_path}")
    
    # Initialize detector and database
    detector = ClipDetector()
    db = ClipsDB(db_path=output_db)
    
    # Process each chunk
    print("\nAdding emotion scores and detecting clip candidates...")
    clip_candidates = []
    
    for i, chunk in enumerate(chunks):
        # Convert timestamp
        timestamp_seconds = float(chunk.get("timestamp", 0))
        start_mmss = seconds_to_mmss(timestamp_seconds)
        end_mmss = seconds_to_mmss(timestamp_seconds + 8)  # Assume 8s per chunk
        
        # Get existing topic from video pipeline
        existing_topic = chunk.get("topic", "Other")
        existing_summary = chunk.get("summary", "")
        
        # Calculate emotion score (reusing existing topic)
        text = chunk.get("text", "")
        emotion_score = detector.calculate_emotion_score(text, existing_topic, existing_summary)
        
        # Determine if clip candidate
        clip_candidate = (
            existing_topic != "Other" and
            emotion_score >= 7
        )
        
        if clip_candidate:
            clip_candidates.append({
                "video_id": chunk.get("video_id", "unknown")[:50].replace(" ", "_"),
                "video_title": chunk.get("video_id", "unknown"),
                "timestamp_start": start_mmss,
                "timestamp_end": end_mmss,
                "start_seconds": timestamp_seconds,
                "end_seconds": timestamp_seconds + 8,
                "topic": existing_topic,
                "emotion_score": emotion_score,
                "text": text[:100] + "..."  # Preview
            })
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i+1}/{len(chunks)} chunks...")
    
    print(f"\n✓ Found {len(clip_candidates)} clip candidates (score ≥7)")
    
    # Merge adjacent clips
    print("\nMerging adjacent clips...")
    merged_clips = detector.merge_adjacent_clips(clip_candidates)
    print(f"✓ Merged into {len(merged_clips)} clips")
    
    # Store in database
    print("\nStoring in database...")
    inserted = db.insert_clips_batch(merged_clips)
    print(f"✓ Stored {inserted} clips in {output_db}")
    
    # Show results
    print("\n" + "="*60)
    print("CLIP CANDIDATES")
    print("="*60)
    
    for i, clip in enumerate(sorted(merged_clips, key=lambda x: -x['emotion_score'])[:10], 1):
        print(f"{i:2}. [{clip['topic']:12}] {clip['timestamp_start']}-{clip['timestamp_end']} | "
              f"Score: {clip['emotion_score']} | Duration: {clip['duration']}s")
    
    # Stats
    stats = db.get_stats()
    print("\n" + "="*60)
    print("DATABASE STATS")
    print("="*60)
    print(f"Total clips: {stats['total_clips']}")
    print(f"By topic: {stats['by_topic']}")
    print(f"Videos with clips: {stats['videos_with_clips']}")
    
    db.close()
    
    return merged_clips


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process existing chunks for clip mining")
    parser.add_argument(
        "--input",
        type=str,
        default="video_pipeline/processed_chunks.json",
        help="Path to processed_chunks.json from video pipeline"
    )
    parser.add_argument(
        "--output-db",
        type=str,
        default="database/clips.db",
        help="Path to clips database"
    )
    
    args = parser.parse_args()
    
    clips = process_existing_chunks(args.input, args.output_db)
    
    print("\n" + "="*60)
    print("NEXT STEP: Extract video clips (requires source video)")
    print("="*60)
    print(f"""
python -m clip_pipeline.run_pipeline \\
    --transcript {args.input} \\
    --video-id your_video_id \\
    --title "Your Video Title"
""")
