"""Add vector embeddings to enriched transcripts."""

import sqlite3
import json
from configs.settings import DATABASE_PATH
from modules.tools.embedding_generator import generate_embedding


def add_vector_column(conn):
    """Add vector column to enriched_transcripts."""
    cur = conn.cursor()
    
    # Check if column exists
    cur.execute("PRAGMA table_info(enriched_transcripts)")
    columns = [row[1] for row in cur.fetchall()]
    
    if "embedding" not in columns:
        cur.execute("ALTER TABLE enriched_transcripts ADD COLUMN embedding BLOB")
        conn.commit()
        print("Added embedding column")
    else:
        print("Embedding column already exists")


def get_unembedded_chunks(conn):
    """Get chunks without embeddings."""
    cur = conn.cursor()
    cur.execute("""
    SELECT id, text, summary 
    FROM enriched_transcripts 
    WHERE embedding IS NULL
    """)
    return cur.fetchall()


def add_embeddings(conn, chunks):
    """Add embeddings to chunks."""
    cur = conn.cursor()
    
    for i, (id, text, summary) in enumerate(chunks, 1):
        # Combine text and summary for better embedding
        content = f"{summary} {text[:300]}"
        
        print(f"  Generating embedding {i}/{len(chunks)}...")
        embedding = generate_embedding(content)
        
        # Store as JSON blob
        embedding_json = json.dumps(embedding).encode('utf-8')
        
        cur.execute("""
        UPDATE enriched_transcripts 
        SET embedding = ? 
        WHERE id = ?
        """, (embedding_json, id))
        
        conn.commit()


def main():
    """Main embedding process."""
    print("=" * 60)
    print("Vector Embedding Generator")
    print("=" * 60)
    print()
    
    conn = sqlite3.connect(DATABASE_PATH)
    
    print("[1] Adding vector column...")
    add_vector_column(conn)
    print()
    
    print("[2] Finding chunks without embeddings...")
    chunks = get_unembedded_chunks(conn)
    print(f"    Found {len(chunks)} chunks to process")
    print()
    
    if chunks:
        print("[3] Generating embeddings...")
        add_embeddings(conn, chunks)
        print()
    
    # Verify
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM enriched_transcripts WHERE embedding IS NOT NULL")
    count = cur.fetchone()[0]
    print(f"[4] Complete! {count} chunks have embeddings")
    print()
    
    conn.close()
    print("=" * 60)


if __name__ == "__main__":
    main()
