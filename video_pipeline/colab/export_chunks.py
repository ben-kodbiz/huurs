"""Export transcript chunks for Google Colab GPU processing.

Usage:
    python export_chunks.py                    # Export all pending chunks
    python export_chunks.py --video "Surah"   # Export from specific video
"""

import sqlite3
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.per_video_db import get_all_video_dbs


def export_pending_chunks(output_file="chunks.json", video_filter=None):
    """Export chunks that need enrichment to JSON file."""
    
    all_chunks = []
    video_stats = {}
    
    print("="*70)
    print("EXPORTING PENDING CHUNKS FOR COLAB PROCESSING")
    print("="*70)
    print()
    
    for db_path in get_all_video_dbs():
        # Filter by video name if specified
        if video_filter and video_filter.lower() not in db_path.lower():
            continue
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get video info
        cur.execute("SELECT video_id, title FROM videos LIMIT 1")
        video = cur.fetchone()
        
        if not video:
            conn.close()
            continue
        
        video_id = video["video_id"]
        video_name = os.path.basename(db_path).replace('.db', '')
        
        # Get pending chunks (no summary yet)
        cur.execute("""
        SELECT id, video_id, timestamp, text
        FROM transcripts t
        WHERE NOT EXISTS (
            SELECT 1 FROM enriched_transcripts e 
            WHERE e.video_id = t.video_id AND e.timestamp = t.timestamp
        )
        """)
        
        chunks = []
        for row in cur.fetchall():
            chunks.append({
                "db_path": video_name,
                "id": row["id"],
                "video_id": row["video_id"],
                "timestamp": row["timestamp"],
                "text": row["text"]
            })
        
        # Get already processed count
        cur.execute("""
        SELECT COUNT(*) FROM enriched_transcripts
        """)
        processed = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM transcripts")
        total = cur.fetchone()[0]
        
        conn.close()
        
        video_stats[video_name] = {
            "total": total,
            "processed": processed,
            "pending": len(chunks)
        }
        
        all_chunks.extend(chunks)
        
        print(f"✓ {video_name[:50]}...")
        print(f"    Total: {total}, Processed: {processed}, Pending: {len(chunks)}")
    
    print()
    print(f"TOTAL CHUNKS TO PROCESS: {len(all_chunks)}")
    print()
    
    if not all_chunks:
        print("✓ No pending chunks to process!")
        return None
    
    # Save to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(output_file) / 1024  # KB
    
    print(f"✓ Exported to: {output_file}")
    print(f"  File size: {file_size:.1f} KB")
    print()
    print("="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Open Google Colab: https://colab.research.google.com/")
    print("2. Upload the notebook: colab_notebook/colab_pipeline.ipynb")
    print("3. Upload this file: chunks.json")
    print("4. Run all cells (GPU will process the chunks)")
    print("5. Download: processed_chunks.json")
    print("6. Run: python import_results.py processed_chunks.json")
    print("="*70)
    
    return output_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export chunks for Colab processing")
    parser.add_argument("--output", default="chunks.json", help="Output JSON file")
    parser.add_argument("--video", help="Filter by video name (partial match)")
    
    args = parser.parse_args()
    
    export_pending_chunks(args.output, args.video)
