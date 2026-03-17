"""Convert existing chunks.json to clip pipeline format.

Usage:
    python convert_chunks.py

Reads: video_pipeline/chunks.json
Writes: video_pipeline/chunks_for_clips.json
"""

import json
from pathlib import Path


def seconds_to_mmss(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def convert_chunks(input_path: str, output_path: str):
    """Convert chunks to clip pipeline format."""
    
    with open(input_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks from {input_path}")
    
    converted = []
    for i, chunk in enumerate(chunks):
        # Parse timestamp (in seconds)
        timestamp_seconds = float(chunk.get("timestamp", 0))
        
        # Estimate end time (assume ~8 seconds per chunk)
        end_seconds = timestamp_seconds + 8
        
        # Convert to MM:SS format
        start_mmss = seconds_to_mmss(timestamp_seconds)
        end_mmss = seconds_to_mmss(end_seconds)
        
        # Get video_id (sanitize if needed)
        video_id = chunk.get("video_id", f"video_{i}")
        video_id = video_id.replace(" ", "_").replace(":", "_")[:50]
        
        converted_chunk = {
            "video_id": video_id,
            "video_title": chunk.get("video_id", ""),  # Keep original title
            "timestamp_start": start_mmss,
            "timestamp_end": end_mmss,
            "start_seconds": timestamp_seconds,
            "end_seconds": end_seconds,
            "text": chunk.get("text", "")
        }
        
        converted.append(converted_chunk)
    
    # Save converted chunks
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Converted {len(converted)} chunks")
    print(f"✓ Saved to: {output_path}")
    
    # Show sample
    print("\nSample converted chunk:")
    print(json.dumps(converted[0], indent=2))
    
    return converted


if __name__ == "__main__":
    input_file = "video_pipeline/chunks.json"
    output_file = "video_pipeline/chunks_for_clips.json"
    
    convert_chunks(input_file, output_file)
    
    print("\n" + "="*60)
    print("NEXT STEP: Run clip mining pipeline")
    print("="*60)
    print(f"""
python -m clip_pipeline.run_pipeline \\
    --transcript {output_file} \\
    --video-id nouman_al_mulk \\
    --title "Studying Surah Al-Mulk" \\
    --min-score 7
""")
