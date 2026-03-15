import sqlite3
from configs.settings import DATABASE_PATH


class VideoDB:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.create_tables()
        self.create_fts_index()

    def create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS videos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE,
            title TEXT,
            channel TEXT,
            url TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS transcripts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            timestamp TEXT,
            text TEXT,
            summary TEXT,
            primary_topic TEXT,
            secondary_topics TEXT,
            confidence REAL
        )
        """)

        self.conn.commit()

    def create_fts_index(self):
        """Create FTS5 virtual table for full-text search."""
        cur = self.conn.cursor()
        
        # Drop existing FTS table if exists
        cur.execute("DROP TABLE IF EXISTS transcript_fts")
        
        # Create FTS5 virtual table
        cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS transcript_fts USING fts5(
            text,
            summary,
            primary_topic,
            content='transcripts',
            content_rowid='id'
        )
        """)
        
        self.conn.commit()

    def rebuild_fts_index(self):
        """Rebuild FTS index from transcripts table."""
        cur = self.conn.cursor()
        
        # Rebuild FTS index
        cur.execute("""
        INSERT INTO transcript_fts(rowid, text, summary, primary_topic)
        SELECT id, text, summary, primary_topic
        FROM transcripts
        """)
        
        self.conn.commit()

    def insert_video(self, video_id, title, channel, url):
        cur = self.conn.cursor()

        cur.execute("""
        INSERT OR IGNORE INTO videos(video_id,title,channel,url)
        VALUES(?,?,?,?)
        """,(video_id,title,channel,url))

        self.conn.commit()

    def insert_transcript(self, video_id, timestamp, text, summary, 
                          primary_topic=None, secondary_topics=None, confidence=None):
        cur = self.conn.cursor()

        cur.execute("""
        INSERT INTO transcripts(video_id,timestamp,text,summary,
                                primary_topic,secondary_topics,confidence)
        VALUES(?,?,?,?,?,?,?)
        """,(video_id,timestamp,text,summary,primary_topic,secondary_topics,confidence))

        # Also insert into FTS index
        try:
            cur.execute("""
            INSERT INTO transcript_fts(rowid, text, summary, primary_topic)
            VALUES(?, ?, ?, ?)
            """, (cur.lastrowid, text, summary, primary_topic))
        except sqlite3.OperationalError:
            # FTS index might not be ready yet
            pass

        self.conn.commit()