#!/usr/bin/env python3
"""Monitor enrichment progress."""
import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.per_video_db import get_all_video_dbs

print("="*70)
print("ENRICHMENT & EMBEDDING PROGRESS MONITOR")
print("="*70)

total_chunks = 0
total_enriched = 0
total_embedded = 0

for db_path in get_all_video_dbs():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute('SELECT video_id, title FROM videos LIMIT 1')
    video = cur.fetchone()
    if not video:
        continue
    
    cur.execute('SELECT COUNT(*) FROM transcripts')
    total = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM enriched_transcripts')
    enriched = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM enriched_transcripts WHERE embedding IS NOT NULL')
    embedded = cur.fetchone()[0]
    
    total_chunks += total
    total_enriched += enriched
    total_embedded += embedded
    
    print(f"\n{video[0][:60]}...")
    print(f"  📄 Transcripts: {total}")
    print(f"  ✨ Enriched: {enriched}/{total} ({enriched/total*100:.1f}%)")
    print(f"  🔢 Embeddings: {embedded}/{enriched} ({embedded/enriched*100 if enriched else 0:.1f}%)")
    
    conn.close()

print(f"\n{'='*70}")
print(f"TOTAL: {total_enriched}/{total_chunks} enriched, {total_embedded}/{total_enriched} with embeddings")
print(f"{'='*70}")
