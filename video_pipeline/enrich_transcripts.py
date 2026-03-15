"""Enrich transcripts with LLM summaries and topics."""

import sqlite3
from configs.settings import DATABASE_PATH, LMSTUDIO_BASE_URL, MODEL_NAME, TIMEOUT
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


def create_enriched_table():
    """Create table for enriched transcripts."""
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    
    # Drop existing table if exists
    cur.execute("DROP TABLE IF EXISTS enriched_transcripts")
    
    # Create enriched table
    cur.execute("""
    CREATE TABLE enriched_transcripts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        timestamp TEXT,
        text TEXT,
        summary TEXT,
        topic TEXT
    )
    """)
    
    conn.commit()
    return conn


def get_chunks(conn, limit=20):
    """Get transcript chunks to enrich."""
    cur = conn.cursor()
    cur.execute("""
    SELECT id, video_id, timestamp, text
    FROM transcripts
    LIMIT ?
    """, (limit,))
    
    return cur.fetchall()


def enrich_chunk(llm, text):
    """Enrich a single chunk with summary and topic."""
    # Generate summary
    summary_prompt = SUMMARY_PROMPT.format(text=text[:500])
    summary = llm.ask(summary_prompt)
    
    # Generate topic
    topic_prompt = TOPIC_PROMPT.format(text=text[:500])
    topic = llm.ask(topic_prompt).strip()
    
    # Validate topic
    valid_topics = [
        "Tawheed (Oneness of Allah)", "Salah (Prayer)", "Zakat (Charity)",
        "Sawm (Fasting)", "Hajj (Pilgrimage)", "Akhlaq (Character/Manners)",
        "Sabr (Patience)", "Shukr (Gratitude)", "Love/Mercy", "Forgiveness",
        "Knowledge/Wisdom", "Death/Afterlife", "Dua (Supplication)",
        "Justice/Oppression", "Sin/Repentance", "Quran/Sunnah", "Other"
    ]
    
    if topic not in valid_topics:
        topic = "Other"
    
    return summary, topic


def main():
    """Main enrichment process."""
    print("=" * 60)
    print("Transcript Enrichment Pipeline")
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
    print("[2] Connecting to database...")
    conn = create_enriched_table()
    print("    Created enriched_transcripts table")
    print()
    
    # Get chunks to process
    print("[3] Loading transcript chunks...")
    chunks = get_chunks(conn, limit=20)
    print(f"    Selected {len(chunks)} chunks for enrichment")
    print()
    
    # Process each chunk
    print("[4] Enriching chunks with LLM...")
    print()
    
    cur = conn.cursor()
    
    for i, (id, video_id, timestamp, text) in enumerate(chunks, 1):
        print(f"    Processing chunk {i}/{len(chunks)}...")
        
        try:
            summary, topic = enrich_chunk(llm, text)
            
            cur.execute("""
            INSERT INTO enriched_transcripts (video_id, timestamp, text, summary, topic)
            VALUES (?, ?, ?, ?, ?)
            """, (video_id, timestamp, text, summary, topic))
            
            print(f"      Topic: {topic}")
            print(f"      Summary: {summary[:80]}...")
            
        except Exception as e:
            print(f"      ERROR: {e}")
            cur.execute("""
            INSERT INTO enriched_transcripts (video_id, timestamp, text, summary, topic)
            VALUES (?, ?, ?, ?, ?)
            """, (video_id, timestamp, text, "Processing failed", "Other"))
        
        conn.commit()
        print()
    
    # Summary
    print("[5] Enrichment complete!")
    print()
    
    # Show statistics
    cur.execute("SELECT topic, COUNT(*) FROM enriched_transcripts GROUP BY topic")
    topics = cur.fetchall()
    
    print("Topic distribution:")
    for topic, count in sorted(topics, key=lambda x: -x[1]):
        print(f"  {topic}: {count}")
    
    print()
    print("=" * 60)
    
    conn.close()


if __name__ == "__main__":
    main()
