"""Per-Video Database Manager

Each video gets its own database file for clean segregation.
Database location: data/db/{sanitized_video_name}.db
"""

import sqlite3
import os
import re
from configs.settings import DATA_DIR


def sanitize_filename(name):
    """Convert video name to safe filename."""
    # Remove special characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Limit length
    return name[:100]


def get_video_db_path(video_id):
    """Get database path for a specific video."""
    db_dir = os.path.join(DATA_DIR, 'db')
    os.makedirs(db_dir, exist_ok=True)
    
    # Use video_id as filename (sanitized)
    filename = sanitize_filename(video_id)
    return os.path.join(db_dir, f"{filename}.db")


def get_all_video_dbs():
    """Get list of all video databases."""
    db_dir = os.path.join(DATA_DIR, 'db')
    if not os.path.exists(db_dir):
        return []
    
    return [
        os.path.join(db_dir, f) 
        for f in os.listdir(db_dir) 
        if f.endswith('.db')
    ]


class PerVideoDB:
    """Database manager for a single video."""

    def __init__(self, video_id):
        """
        Initialize database for a specific video.
        
        Args:
            video_id: Unique video identifier (used as DB filename)
        """
        self.video_id = video_id
        self.db_path = get_video_db_path(video_id)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create all required tables for this video."""
        cur = self.conn.cursor()

        # Videos table (metadata)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS videos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE,
            title TEXT,
            channel TEXT,
            url TEXT
        )
        """)

        # Transcripts table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transcripts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            timestamp TEXT,
            text TEXT
        )
        """)

        # Enriched transcripts table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS enriched_transcripts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            timestamp TEXT,
            text TEXT,
            summary TEXT,
            topic TEXT,
            embedding BLOB
        )
        """)

        # FTS5 virtual table for full-text search
        cur.execute("DROP TABLE IF EXISTS transcript_fts")
        cur.execute("""
        CREATE VIRTUAL TABLE transcript_fts USING fts5(
            text,
            content='transcripts',
            content_rowid='id'
        )
        """)

        self.conn.commit()

    def create_fts_index(self):
        """Create/rebuild FTS index from transcripts."""
        cur = self.conn.cursor()
        
        # Rebuild FTS index
        cur.execute("""
        INSERT INTO transcript_fts(rowid, text)
        SELECT id, text
        FROM transcripts
        """)
        
        self.conn.commit()

    def insert_video(self, video_id, title, channel, url):
        """Insert video metadata."""
        cur = self.conn.cursor()
        cur.execute("""
        INSERT OR IGNORE INTO videos(video_id, title, channel, url)
        VALUES (?, ?, ?, ?)
        """, (video_id, title, channel, url))
        self.conn.commit()

    def insert_transcript(self, video_id, timestamp, text):
        """Insert transcript chunk."""
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO transcripts(video_id, timestamp, text)
        VALUES (?, ?, ?)
        """, (video_id, timestamp, text))
        
        # Insert into FTS index
        try:
            cur.execute("""
            INSERT INTO transcript_fts(rowid, text)
            VALUES (?, ?)
            """, (cur.lastrowid, text))
        except sqlite3.OperationalError:
            pass  # FTS might need rebuild
        
        self.conn.commit()

    def insert_enriched(self, video_id, timestamp, text, summary, topic, embedding=None):
        """Insert enriched transcript."""
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO enriched_transcripts(video_id, timestamp, text, summary, topic, embedding)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (video_id, timestamp, text, summary, topic, 
              embedding if embedding else None))
        self.conn.commit()

    def update_embedding(self, id, embedding):
        """Update embedding for enriched transcript."""
        cur = self.conn.cursor()
        cur.execute("""
        UPDATE enriched_transcripts 
        SET embedding = ? 
        WHERE id = ?
        """, (embedding, id))
        self.conn.commit()

    def get_transcripts_count(self):
        """Get total transcripts count."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transcripts")
        return cur.fetchone()[0]

    def get_enriched_count(self):
        """Get enriched transcripts count."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM enriched_transcripts")
        return cur.fetchone()[0]

    def get_enriched_with_embeddings_count(self):
        """Get count of enriched transcripts with embeddings."""
        cur = self.conn.cursor()
        cur.execute("""
        SELECT COUNT(*) FROM enriched_transcripts 
        WHERE embedding IS NOT NULL
        """)
        return cur.fetchone()[0]

    def get_video_metadata(self):
        """Get video metadata."""
        cur = self.conn.cursor()
        cur.execute("""
        SELECT video_id, title, channel, url 
        FROM videos 
        LIMIT 1
        """)
        row = cur.fetchone()
        return dict(row) if row else None

    def search_transcripts(self, query, limit=10):
        """Search transcripts using FTS5."""
        cur = self.conn.cursor()
        
        # Sanitize query
        query = query.replace('-', ' ')
        special_chars = ['"', '*', '+', '~', '(', ')', '<', '>', '@']
        for char in special_chars:
            query = query.replace(char, '')
        words = query.split()
        query = ' OR '.join(words) if len(words) > 1 else ' '.join(words)
        
        cur.execute("""
        SELECT t.video_id, t.timestamp, t.text
        FROM transcript_fts fts
        JOIN transcripts t ON fts.rowid = t.id
        WHERE fts MATCH ?
        LIMIT ?
        """, (query, limit))
        
        return [dict(row) for row in cur.fetchall()]

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'conn'):
            self.conn.close()
