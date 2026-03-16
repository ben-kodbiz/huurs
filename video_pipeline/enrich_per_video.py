"""Enrich transcripts with LLM summaries and topics.

Supports per-video databases with progress tracking and ETA.
"""

import sqlite3
import os
import time
from datetime import datetime, timedelta
from database.per_video_db import PerVideoDB, get_all_video_dbs
from rag.llm_client import LLMClient


# LLM prompts
SUMMARY_PROMPT = """Summarize this lecture transcript chunk in 1-2 sentences.
Focus on the main Islamic teaching or lesson.

Transcript:
{text}

Summary:"""

TOPIC_PROMPT = """Classify this transcript chunk into ONE primary Islamic topic.

Available topics:
- Tawheed (Oneness of Allah)
- Salah (Prayer)
- Zakat (Charity)
- Sawm (Fasting)
- Hajj (Pilgrimage)
- Akhlaq (Character/Manners)
- Sabr (Patience)
- Shukr (Gratitude)
- Love/Mercy
- Forgiveness
- Knowledge/Wisdom
- Death/Afterlife
- Dua (Supplication)
- Justice/Oppression
- Sin/Repentance
- Quran/Sunnah
- Other

Transcript:
{text}

Primary topic (only the topic name):"""


valid_topics = [
    "Tawheed (Oneness of Allah)", "Salah (Prayer)", "Zakat (Charity)",
    "Sawm (Fasting)", "Hajj (Pilgrimage)", "Akhlaq (Character/Manners)",
    "Sabr (Patience)", "Shukr (Gratitude)", "Love/Mercy", "Forgiveness",
    "Knowledge/Wisdom", "Death/Afterlife", "Dua (Supplication)",
    "Justice/Oppression", "Sin/Repentance", "Quran/Sunnah", "Other"
]


def enrich_chunk(llm, text):
    """Enrich a single chunk with summary and topic."""
    summary_prompt = SUMMARY_PROMPT.format(text=text[:500])
    summary = llm.ask(summary_prompt)

    topic_prompt = TOPIC_PROMPT.format(text=text[:500])
    topic = llm.ask(topic_prompt).strip()

    if topic not in valid_topics:
        topic = "Other"

    return summary, topic


def get_pending_chunks(db):
    """Get all transcript chunks that need enrichment."""
    cur = db.conn.cursor()
    cur.execute("""
    SELECT t.id, t.video_id, t.timestamp, t.text
    FROM transcripts t
    LEFT JOIN enriched_transcripts e 
        ON t.video_id = e.video_id AND t.timestamp = e.timestamp
    WHERE e.id IS NULL
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


def process_video_db(db_path, llm):
    """Process a single video database."""
    video_id = os.path.basename(db_path).replace('.db', '').replace('_', ' ')
    
    print(f"\n{'='*70}")
    print(f"Video: {video_id}")
    print(f"Database: {db_path}")
    print('='*70)
    
    db = PerVideoDB(video_id)
    db.conn = sqlite3.connect(db_path)
    db.conn.row_factory = sqlite3.Row
    
    chunks = get_pending_chunks(db)
    
    if not chunks:
        print("✓ No pending chunks to enrich")
        db.close()
        return 0, 0
    
    total = len(chunks)
    print(f"Pending chunks: {total}")
    print()
    
    # Timing tracking
    start_time = time.time()
    chunk_times = []
    enriched_count = 0
    
    for i, (id, video_id, timestamp, text) in enumerate(chunks, 1):
        chunk_start = time.time()
        
        try:
            summary, topic = enrich_chunk(llm, text)
            db.insert_enriched(video_id, timestamp, text, summary, topic)
            enriched_count += 1
            
        except Exception as e:
            print(f"  ERROR at chunk {i}: {e}")
            continue
        
        # Track timing
        chunk_time = time.time() - chunk_start
        chunk_times.append(chunk_time)
        avg_time = sum(chunk_times) / len(chunk_times)
        
        # Progress reporting (every 10 chunks or last one)
        if i % 10 == 0 or i == total:
            elapsed = time.time() - start_time
            remaining = (total - i) * avg_time
            eta = datetime.now() + timedelta(seconds=remaining)
            
            # Get recent topic for display
            print(f"  [{i}/{total}] {i/total*100:.1f}% | "
                  f"Elapsed: {elapsed/60:.1f}m | "
                  f"ETA: {format_eta(remaining)} ({eta.strftime('%H:%M')}) | "
                  f"Avg: {avg_time:.1f}s/chunk | "
                  f"Topic: {topic}")
    
    total_time = time.time() - start_time
    print(f"\n✓ Enriched {enriched_count} chunks in {total_time/60:.1f} minutes")
    
    db.close()
    return enriched_count, total_time


def main():
    """Main enrichment process."""
    print("="*70)
    print("TRANSCRIPT ENRICHMENT PIPELINE (Per-Video)")
    print("="*70)
    print()
    
    # Initialize LLM
    llm = LLMClient()
    
    print("[1] Checking LLM availability...")
    if not llm.is_available():
        print("    ✗ ERROR: LLM not available. Please start LM Studio.")
        return
    print("    ✓ LLM available")
    print()
    
    # Get all video databases
    print("[2] Finding video databases...")
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
        cur.execute("SELECT COUNT(*) FROM transcripts")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM enriched_transcripts")
        enriched = cur.fetchone()[0]
        total_pending += (total - enriched)
        db.close()
    
    if total_pending == 0:
        print("✓ All chunks already enriched!")
        return
    
    print(f"[3] Total pending chunks: {total_pending}")
    print(f"    Estimated time: {format_eta(total_pending * 10)}")
    print()
    print("Starting enrichment... (Press Ctrl+C to stop anytime)")
    print("="*70)
    
    # Process each database
    total_enriched = 0
    total_time = 0
    
    start_all = time.time()
    for db_path in db_paths:
        enriched, time_taken = process_video_db(db_path, llm)
        total_enriched += enriched
        total_time += time_taken
    
    all_time = time.time() - start_all
    
    print()
    print("="*70)
    print(f"[4] ENRICHMENT COMPLETE!")
    print(f"    Total enriched: {total_enriched} chunks")
    print(f"    Total time: {all_time/60:.1f} minutes")
    print("="*70)


if __name__ == "__main__":
    main()
