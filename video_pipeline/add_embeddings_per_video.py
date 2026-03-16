"""Add vector embeddings to enriched transcripts.

Supports per-video databases with progress tracking and ETA.
"""

import sqlite3
import json
import os
import time
from datetime import datetime, timedelta
from database.per_video_db import PerVideoDB, get_all_video_dbs
from modules.tools.embedding_generator import generate_embedding


def get_pending_embeddings(db):
    """Get enriched chunks that need embeddings."""
    cur = db.conn.cursor()
    cur.execute("""
    SELECT id, text, summary
    FROM enriched_transcripts
    WHERE embedding IS NULL
    """)
    return cur.fetchall()


def format_eta(seconds):
    """Format seconds into human readable ETA."""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds/60)} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def process_video_db(db_path):
    """Process a single video database."""
    video_id = os.path.basename(db_path).replace('.db', '').replace('_', ' ')
    
    print(f"\n{'='*70}")
    print(f"Video: {video_id}")
    print(f"Database: {db_path}")
    print('='*70)
    
    db = PerVideoDB(video_id)
    db.conn = sqlite3.connect(db_path)
    db.conn.row_factory = sqlite3.Row
    
    chunks = get_pending_embeddings(db)
    
    if not chunks:
        print("✓ No pending embeddings to generate")
        db.close()
        return 0, 0
    
    total = len(chunks)
    print(f"Pending embeddings: {total}")
    print()
    
    # Timing tracking
    start_time = time.time()
    chunk_times = []
    embedded_count = 0
    
    for i, (id, text, summary) in enumerate(chunks, 1):
        chunk_start = time.time()
        
        try:
            # Combine text and summary for better embedding
            content = f"{text} {summary}" if summary else text
            embedding = generate_embedding(content)
            
            # Convert to JSON for storage
            embedding_json = json.dumps(embedding).encode('utf-8')
            
            db.update_embedding(id, embedding_json)
            embedded_count += 1
            
        except Exception as e:
            print(f"  ERROR at {i}: {e}")
            continue
        
        # Track timing
        chunk_time = time.time() - chunk_start
        chunk_times.append(chunk_time)
        avg_time = sum(chunk_times) / len(chunk_times)
        
        # Progress reporting (every 20 chunks or last one)
        if i % 20 == 0 or i == total:
            elapsed = time.time() - start_time
            remaining = (total - i) * avg_time
            eta = datetime.now() + timedelta(seconds=remaining)
            
            print(f"  [{i}/{total}] {i/total*100:.1f}% | "
                  f"Elapsed: {elapsed/60:.1f}m | "
                  f"ETA: {format_eta(remaining)} ({eta.strftime('%H:%M')}) | "
                  f"Avg: {avg_time:.2f}s/chunk")
    
    total_time = time.time() - start_time
    print(f"\n✓ Generated {embedded_count} embeddings in {total_time/60:.1f} minutes")
    
    db.close()
    return embedded_count, total_time


def main():
    """Main embedding process."""
    print("="*70)
    print("VECTOR EMBEDDING GENERATOR (Per-Video)")
    print("="*70)
    print()
    
    # Get all video databases
    print("[1] Finding video databases...")
    db_paths = get_all_video_dbs()
    
    if not db_paths:
        print("    ✗ No video databases found in data/db/")
        return
    
    print(f"    Found {len(db_paths)} video database(s)")
    for db_path in db_paths:
        print(f"      - {os.path.basename(db_path)}")
    print()
    
    # Calculate total work
    total_pending = 0
    for db_path in db_paths:
        db = PerVideoDB('test')
        db.conn = sqlite3.connect(db_path)
        cur = db.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM enriched_transcripts WHERE embedding IS NULL")
        pending = cur.fetchone()[0]
        total_pending += pending
        db.close()
    
    if total_pending == 0:
        print("✓ All embeddings already generated!")
        return
    
    print(f"[2] Total pending embeddings: {total_pending}")
    # Embedding is faster (~2s per chunk vs 10s for enrichment)
    print(f"    Estimated time: {format_eta(total_pending * 2)}")
    print()
    print("Starting embedding generation... (Press Ctrl+C to stop anytime)")
    print("="*70)
    
    # Process each database
    total_embedded = 0
    total_time = 0
    
    start_all = time.time()
    for db_path in db_paths:
        embedded, time_taken = process_video_db(db_path)
        total_embedded += embedded
        total_time += time_taken
    
    all_time = time.time() - start_all
    
    print()
    print("="*70)
    print(f"[3] EMBEDDING COMPLETE!")
    print(f"    Total embedded: {total_embedded} chunks")
    print(f"    Total time: {all_time/60:.1f} minutes")
    print("="*70)


if __name__ == "__main__":
    main()
