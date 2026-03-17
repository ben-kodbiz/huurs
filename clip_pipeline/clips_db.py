"""Clips Database Manager.

Manages the clips table for storing clip metadata.
"""

import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = "database/clips.db"


class ClipsDB:
    """Database manager for clip metadata."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """
        Initialize clips database.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create clips table if not exists."""
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS clips(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            video_title TEXT,
            start_time TEXT,
            end_time TEXT,
            start_seconds REAL,
            end_seconds REAL,
            duration REAL,
            topic TEXT,
            all_topics TEXT,
            emotion_score INTEGER,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create index on topic for faster searches
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_clips_topic ON clips(topic)
        """)

        # Create index on video_id
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_clips_video ON clips(video_id)
        """)

        # Create index on emotion_score for top clips queries
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_clips_score ON clips(emotion_score DESC)
        """)

        self.conn.commit()
        print(f"✓ Clips database initialized: {self.db_path}")

    def insert_clip(
        self,
        video_id: str,
        video_title: str,
        start_time: str,
        end_time: str,
        start_seconds: float,
        end_seconds: float,
        duration: float,
        topic: str,
        emotion_score: int,
        file_path: str = None,
        all_topics: list = None
    ) -> int:
        """
        Insert a clip record.

        Args:
            video_id: Source video ID.
            video_title: Source video title.
            start_time: Start timestamp (MM:SS).
            end_time: End timestamp (MM:SS).
            start_seconds: Start time in seconds.
            end_seconds: End time in seconds.
            duration: Clip duration in seconds.
            topic: Primary topic classification.
            emotion_score: Emotional impact score (1-10).
            file_path: Path to extracted clip file.
            all_topics: List of all topics in merged clip.

        Returns:
            Inserted clip ID.
        """
        cur = self.conn.cursor()

        all_topics_str = ",".join(all_topics) if all_topics else topic

        cur.execute("""
        INSERT INTO clips(
            video_id, video_title, start_time, end_time,
            start_seconds, end_seconds, duration,
            topic, all_topics, emotion_score, file_path
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """, (
            video_id, video_title, start_time, end_time,
            start_seconds, end_seconds, duration,
            topic, all_topics_str, emotion_score, file_path
        ))

        self.conn.commit()
        return cur.lastrowid

    def insert_clips_batch(self, clips: list[dict]) -> int:
        """
        Insert multiple clips in a batch.

        Args:
            clips: List of clip dicts with required fields.

        Returns:
            Number of clips inserted.
        """
        cur = self.conn.cursor()

        inserted = 0
        for clip in clips:
            try:
                self.insert_clip(
                    video_id=clip.get("video_id", ""),
                    video_title=clip.get("video_title", ""),
                    start_time=clip.get("timestamp_start", ""),
                    end_time=clip.get("timestamp_end", ""),
                    start_seconds=clip.get("start_seconds", 0),
                    end_seconds=clip.get("end_seconds", 0),
                    duration=clip.get("duration", 0),
                    topic=clip.get("topic", "Other"),
                    emotion_score=clip.get("emotion_score", 5),
                    file_path=clip.get("file_path"),
                    all_topics=clip.get("all_topics")
                )
                inserted += 1
            except Exception as e:
                print(f"⚠️ Failed to insert clip: {e}")

        return inserted

    def get_clip(self, clip_id: int) -> sqlite3.Row:
        """Get clip by ID."""
        cur = self.conn.cursor()

        cur.execute("SELECT * FROM clips WHERE id = ?", (clip_id,))
        return cur.fetchone()

    def get_clips_by_topic(self, topic: str, limit: int = 20) -> list[sqlite3.Row]:
        """Get clips by topic."""
        cur = self.conn.cursor()

        cur.execute("""
        SELECT * FROM clips
        WHERE topic = ?
        ORDER BY emotion_score DESC
        LIMIT ?
        """, (topic, limit))

        return cur.fetchall()

    def get_clips_by_video(self, video_id: str, limit: int = 50) -> list[sqlite3.Row]:
        """Get all clips for a video."""
        cur = self.conn.cursor()

        cur.execute("""
        SELECT * FROM clips
        WHERE video_id = ?
        ORDER BY start_time
        LIMIT ?
        """, (video_id, limit))

        return cur.fetchall()

    def get_top_clips(self, limit: int = 20) -> list[sqlite3.Row]:
        """Get top clips by emotion score."""
        cur = self.conn.cursor()

        cur.execute("""
        SELECT * FROM clips
        ORDER BY emotion_score DESC, start_time
        LIMIT ?
        """, (limit,))

        return cur.fetchall()

    def search_clips(self, query: str, limit: int = 20) -> list[sqlite3.Row]:
        """Search clips by topic or video title."""
        cur = self.conn.cursor()

        cur.execute("""
        SELECT * FROM clips
        WHERE topic LIKE ? OR video_title LIKE ? OR all_topics LIKE ?
        ORDER BY emotion_score DESC
        LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))

        return cur.fetchall()

    def get_candidate_clips(
        self,
        min_score: int = 7,
        limit: int = 100
    ) -> list[sqlite3.Row]:
        """Get clip candidates above minimum emotion score."""
        cur = self.conn.cursor()

        cur.execute("""
        SELECT * FROM clips
        WHERE emotion_score >= ?
        ORDER BY emotion_score DESC
        LIMIT ?
        """, (min_score, limit))

        return cur.fetchall()

    def update_clip_file(self, clip_id: int, file_path: str) -> None:
        """Update clip file path after extraction."""
        cur = self.conn.cursor()

        cur.execute("""
        UPDATE clips SET file_path = ?
        WHERE id = ?
        """, (file_path, clip_id))

        self.conn.commit()

    def delete_clip(self, clip_id: int) -> None:
        """Delete a clip record."""
        cur = self.conn.cursor()

        cur.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
        self.conn.commit()

    def get_stats(self) -> dict:
        """Get clip database statistics."""
        cur = self.conn.cursor()

        stats = {}

        # Total clips
        cur.execute("SELECT COUNT(*) as count FROM clips")
        stats["total_clips"] = cur.fetchone()["count"]

        # Clips by topic
        cur.execute("""
        SELECT topic, COUNT(*) as count
        FROM clips
        GROUP BY topic
        ORDER BY count DESC
        """)
        stats["by_topic"] = {row["topic"]: row["count"] for row in cur.fetchall()}

        # Average emotion score
        cur.execute("SELECT AVG(emotion_score) as avg FROM clips")
        stats["avg_emotion_score"] = cur.fetchone()["avg"] or 0

        # Videos with clips
        cur.execute("SELECT COUNT(DISTINCT video_id) as count FROM clips")
        stats["videos_with_clips"] = cur.fetchone()["count"]

        return stats

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Test
if __name__ == "__main__":
    print("Testing ClipsDB...")

    with ClipsDB(":memory:") as db:
        # Test insert
        clip_id = db.insert_clip(
            video_id="test_video",
            video_title="Test Lecture",
            start_time="02:30",
            end_time="03:15",
            start_seconds=150,
            end_seconds=195,
            duration=45,
            topic="Charity",
            emotion_score=8
        )
        print(f"✓ Inserted clip ID: {clip_id}")

        # Test retrieval
        clip = db.get_clip(clip_id)
        print(f"✓ Retrieved clip: {clip['topic']} (score: {clip['emotion_score']})")

        # Test stats
        stats = db.get_stats()
        print(f"✓ Stats: {stats}")
