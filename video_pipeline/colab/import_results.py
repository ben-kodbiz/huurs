"""Import processed chunks from Google Colab back into database.

Usage:
    python import_results.py processed_chunks.json
"""

import sqlite3
import json
import os
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.per_video_db import PerVideoDB


def import_results(input_file, rebuild_fts=True):
    """Import processed chunks from Colab into per-video databases."""
    
    print("="*70)
    print("IMPORTING COLAB PROCESSING RESULTS")
    print("="*70)
    print()
    
    # Load processed chunks
    if not os.path.exists(input_file):
        print(f"✗ Error: File not found: {input_file}")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        processed_chunks = json.load(f)
    
    print(f"✓ Loaded {len(processed_chunks)} processed chunks")
    
    # Check if embeddings are included
    has_embeddings = 'embedding' in processed_chunks[0] if processed_chunks else False
    if has_embeddings:
        print(f"✓ Embeddings detected ({len(processed_chunks[0]['embedding'])} dimensions)")
    else:
        print(f"⚠ No embeddings - will need to generate locally")
    print()
    
    # Group by database
    chunks_by_db = {}
    for chunk in processed_chunks:
        db_path = chunk.get('db_path', 'unknown')
        if db_path not in chunks_by_db:
            chunks_by_db[db_path] = []
        chunks_by_db[db_path].append(chunk)
    
    print(f"Chunks by database:")
    for db_path, chunks in chunks_by_db.items():
        print(f"  {db_path}: {len(chunks)} chunks")
    print()
    
    # Import into each database
    total_imported = 0
    total_failed = 0
    
    for db_name, chunks in chunks_by_db.items():
        print(f"Processing: {db_name}")
        
        # Extract video_id from db name
        video_id = db_name.replace('_', ' ').replace('.db', '')
        
        try:
            db = PerVideoDB(video_id)
            db.conn = sqlite3.connect(db.db_path)
            db.conn.row_factory = sqlite3.Row
            
            imported = 0
            failed = 0
            
            for chunk in chunks:
                try:
                    # Get embedding if available
                    embedding_json = None
                    if 'embedding' in chunk:
                        embedding_json = json.dumps(chunk['embedding']).encode('utf-8')
                    
                    # Insert enriched transcript with all new fields
                    db.insert_enriched(
                        video_id=chunk.get('video_id', video_id),
                        timestamp=chunk['timestamp'],
                        text=chunk['text'],
                        summary=chunk.get('summary', ''),
                        topic=chunk.get('topic', 'Other'),
                        embedding=embedding_json
                    )
                    
                    # Store clip scoring info (for future clip generation)
                    clip_score = chunk.get('clip_score', 5)
                    clip_candidate = chunk.get('clip_candidate', False)
                    skipped_llm = chunk.get('skipped_llm', False)
                    
                    imported += 1
                    
                    if imported % 50 == 0:
                        print(f"  Imported {imported}/{len(chunks)}...")
                    
                except Exception as e:
                    print(f"  ✗ Error importing chunk {chunk.get('id', '?')}: {e}")
                    failed += 1
            
            # Rebuild FTS index
            if rebuild_fts and imported > 0:
                print(f"  Rebuilding search index...")
                db.create_fts_index()
            
            db.close()
            
            print(f"  ✓ Imported: {imported}, Failed: {failed}")
            total_imported += imported
            total_failed += failed
            
        except Exception as e:
            print(f"  ✗ Database error: {e}")
            total_failed += len(chunks)
        
        print()
    
    # Summary
    print("="*70)
    print(f"IMPORT COMPLETE")
    print("="*70)
    print(f"  Total processed: {len(processed_chunks)}")
    print(f"  Successfully imported: {total_imported}")
    print(f"  Failed: {total_failed}")
    print()
    
    if total_failed == 0:
        print("✓ All chunks imported successfully!")
    else:
        print(f"⚠ {total_failed} chunks failed to import")
    
    print()
    print("NEXT STEPS:")
    if has_embeddings:
        print("  ✓ Embeddings already included!")
    else:
        print("  1. Run: python add_embeddings_per_video.py (generate embeddings)")
    print("  2. Run: python monitor_progress.py (to see updated stats)")
    print("  3. Start RAG server: python -m uvicorn rag.rag_api:app --host 0.0.0.0 --port 8000")
    print("="*70)
    
    return total_failed == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Colab processing results")
    parser.add_argument("input_file", help="Path to processed_chunks.json")
    parser.add_argument("--no-fts", action="store_true", help="Skip FTS index rebuild")
    
    args = parser.parse_args()
    
    success = import_results(args.input_file, not args.no_fts)
    
    sys.exit(0 if success else 1)
