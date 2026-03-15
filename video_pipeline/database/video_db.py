import sqlite3
from configs.settings import DATABASE_PATH


class VideoDB:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.create_tables()

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
            summary TEXT
        )
        """)

        self.conn.commit()

    def insert_video(self, video_id, title, channel, url):

        cur = self.conn.cursor()

        cur.execute("""
        INSERT OR IGNORE INTO videos(video_id,title,channel,url)
        VALUES(?,?,?,?)
        """,(video_id,title,channel,url))

        self.conn.commit()

    def insert_transcript(self, video_id, timestamp, text, summary):

        cur = self.conn.cursor()

        cur.execute("""
        INSERT INTO transcripts(video_id,timestamp,text,summary)
        VALUES(?,?,?,?)
        """,(video_id,timestamp,text,summary))

        self.conn.commit()