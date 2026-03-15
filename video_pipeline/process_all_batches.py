"""Process all remaining chunks in batches."""

import sqlite3
import sys
import time
from configs.settings import DATABASE_PATH
from enrich_transcripts import (
    create_enriched_table, get_chunks, enrich_chunk, LLMClient
)


def get_enriched_count(conn):
    """Get count of already enriched chunks."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM enriched_transcripts")
    return cur.fetchone()[0]


def get_total_chunks(conn):
    """Get total chunks in transcripts table."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM transcripts")
    return cur.fetchone()[0]


def process_batch(conn, llm, batch_size=20, offset=0):
    """Process a single batch of chunks."""
    chunks = get_chunks(conn, limit=batch_size, offset=offset)
    
    if not chunks:
        return 0
    
    cur = conn.cursor()
    processed = 0
    
    for id, video_id, timestamp, text in chunks:
        try:
            summary, topic = enrich_chunk(llm, text)
            
            cur.execute("""
            INSERT INTO enriched_transcripts (video_id, timestamp, text, summary, topic)
            VALUES (?, ?, ?, ?, ?)
            """, (video_id, timestamp, text, summary, topic))
            
            processed += 1
            
        except Exception as e:
            print(f"      ERROR: {e}")
            cur.execute("""
            INSERT INTO enriched_transcripts (video_id, timestamp, text, summary, topic)
            VALUES (?, ?, ?, ?, ?)
            """, (video_id, timestamp, text, "Processing failed", "Other"))
            processed += 1
        
        conn.commit()
    
    return processed


def main():
    """Process all chunks in batches."""
    print("=" * 60)
    print("Batch Enrichment Processor")
    print("=" * 60)
    print()
    
    # Initialize LLM
    llm = LLMClient()
    
    print("[1] Checking LLM availability...")
    if not llm.is_available():
        print("    ERROR: LLM not available. Please start LM Studio.")
        return
    print("    LLM available: ✓")
    print()
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Get counts
    total = get_total_chunks(conn)
    enriched = get_enriched_count(conn)
    remaining = total - enriched
    
    print(f"[2] Database status:")
    print(f"    Total chunks: {total}")
    print(f"    Already enriched: {enriched}")
    print(f"    Remaining: {remaining}")
    print()
    
    if remaining == 0:
        print("    All chunks already enriched! ✓")
        conn.close()
        return
    
    # Process in batches
    batch_size = 20
    total_batches = (remaining + batch_size - 1) // batch_size
    
    print(f"[3] Processing {remaining} chunks in batches of {batch_size}...")
    print(f"    Estimated batches: {total_batches}")
    print(f"    Estimated time: ~{total_batches * 5} minutes")
    print()
    
    offset = enriched
    batch_num = 0
    total_processed = 0
    
    while offset < total:
        batch_num += 1
        print(f"{'=' * 60}")
        print(f"Batch {batch_num}/{total_batches} (offset={offset})")
        print(f"{'=' * 60}")
        print()
        
        processed = process_batch(conn, llm, batch_size=batch_size, offset=offset)
        total_processed += processed
        
        print(f"    ✓ Batch {batch_num} complete: {processed} chunks")
        print()
        
        offset += batch_size
        
        # Show progress
        enriched_now = get_enriched_count(conn)
        progress = (enriched_now / total) * 100
        print(f"    Progress: {enriched_now}/{total} ({progress:.1f}%)")
        print()
        
        # Small delay between batches
        if offset < total:
            time.sleep(1)
    
    # Final statistics
    print("=" * 60)
    print("[4] Complete!")
    print()
    
    cur = conn.cursor()
    cur.execute("SELECT topic, COUNT(*) FROM enriched_transcripts GROUP BY topic ORDER BY COUNT(*) DESC")
    topics = cur.fetchall()
    
    print("Final topic distribution:")
    for topic, count in topics:
        pct = (count / total_processed) * 100
        bar = "█" * int(pct / 5)
        print(f"  {topic:30} {count:3} ({pct:5.1f}%) {bar}")
    
    print()
    print("=" * 60)
    
    conn.close()


if __name__ == "__main__":
    main()
