"""Detect viral clip candidates from lecture transcripts.

This module analyzes transcript chunks and identifies segments
suitable for social media clips based on:
- Topic classification
- Emotional impact scoring
- Keyword detection
"""

import json
import re
from pathlib import Path
from typing import Optional


# Valid topics for classification
VALID_TOPICS = [
    "Charity",
    "Oppression",
    "Dua",
    "Mercy",
    "Death",
    "Tawakkul",
    "Sabr",
    "Afterlife",
    "Faith",
    "Prayer",
    "Quran",
    "Hadith",
    "Other"
]

# Keywords that indicate important Islamic content
IMPORTANT_KEYWORDS = [
    "allah", "prophet", "quran", "hadith", "islam", "muslim",
    "faith", "belief", "prayer", "salah", "zakat", "sadaqah",
    "charity", "oppression", "dua", "supplication", "mercy",
    "rahmah", "forgiveness", "paradise", "jannah", "hellfire",
    "jahannam", "death", "grave", "afterlife", "akhirah",
    "sabr", "patience", "tawakkul", "trust", "Allah"
]

# Emotional impact keywords
EMOTIONAL_KEYWORDS = [
    "love", "mercy", "fear", "hope", "beautiful", "amazing",
    "powerful", "heart", "soul", "weep", "cry", "remember",
    "death", "grave", "paradise", "hellfire", "forgiveness"
]

# Religious content keywords
RELIGIOUS_KEYWORDS = [
    "allah", "prophet", "quran", "faith", "belief", "worship",
    "prayer", "fasting", "charity", "pilgrimage", "islam"
]

# Teaching indicator keywords
TEACHING_KEYWORDS = [
    "remember", "learn", "understand", "know", "lesson",
    "teach", "wisdom", "guidance", "advice"
]

# Important topic boosters
IMPORTANT_TOPICS = [
    "Charity", "Oppression", "Dua", "Mercy", "Patience",
    "Afterlife", "Death", "Faith"
]


class ClipDetector:
    """Detect viral clip candidates from transcript chunks."""

    def __init__(self, emotion_threshold: int = 7):
        """
        Initialize clip detector.

        Args:
            emotion_threshold: Minimum emotion score for clip candidate (1-10).
        """
        self.emotion_threshold = emotion_threshold

    def has_important_content(self, text: str) -> bool:
        """Check if chunk contains important Islamic content.

        Args:
            text: Transcript chunk text.

        Returns:
            True if important keywords detected.
        """
        text_lower = text.lower()
        for keyword in IMPORTANT_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

    def calculate_emotion_score(
        self,
        text: str,
        topic: str = "",
        summary: str = ""
    ) -> int:
        """Calculate viral clip potential score (1-10).

        Args:
            text: Transcript chunk text.
            topic: Classified topic.
            summary: LLM-generated summary.

        Returns:
            Emotion score from 1-10.
        """
        score = 5  # Base score
        text_lower = text.lower()
        combined_text = f"{text_lower} {summary.lower()}"

        # Emotional impact keywords (+2)
        if any(word in combined_text for word in EMOTIONAL_KEYWORDS):
            score += 2

        # Strong religious message (+2)
        if any(word in combined_text for word in RELIGIOUS_KEYWORDS):
            score += 1

        # Clear teaching indicators (+1)
        if any(word in combined_text for word in TEACHING_KEYWORDS):
            score += 1

        # Important topics (+1)
        if any(topic == important_topic for important_topic in IMPORTANT_TOPICS):
            score += 1

        # Cap at 10
        return min(score, 10)

    def detect_keywords(self, text: str) -> list[str]:
        """Detect keywords in text.

        Args:
            text: Transcript chunk text.

        Returns:
            List of detected keywords.
        """
        text_lower = text.lower()
        detected = []

        # Charity keywords
        if any(kw in text_lower for kw in ["zakat", "sadaqah", "donate", "charity"]):
            detected.append("charity")

        # Oppression keywords
        if any(kw in text_lower for kw in ["tyrant", "injustice", "oppressed", "oppression"]):
            detected.append("oppression")

        # Dua keywords
        if any(kw in text_lower for kw in ["supplication", "ask allah", "dua", "pray"]):
            detected.append("dua")

        # Mercy keywords
        if any(kw in text_lower for kw in ["rahmah", "forgiveness", "mercy"]):
            detected.append("mercy")

        return detected

    def classify_topic(self, text: str) -> str:
        """Classify topic of transcript chunk.

        This is a simple keyword-based classifier.
        For production, use LLM-based classification.

        Args:
            text: Transcript chunk text.

        Returns:
            Topic string from VALID_TOPICS.
        """
        text_lower = text.lower()

        # Topic keyword mappings
        topic_keywords = {
            "Charity": ["charity", "zakat", "sadaqah", "give", "donate", "poor", "needy"],
            "Oppression": ["oppression", "tyrant", "injustice", "oppressed", "wrong"],
            "Dua": ["dua", "supplication", "ask allah", "pray", "invoke"],
            "Mercy": ["mercy", "rahmah", "forgiveness", "compassion", "kindness"],
            "Death": ["death", "grave", "dying", "funeral", "burial"],
            "Tawakkul": ["tawakkul", "trust allah", "reliance", "depend"],
            "Sabr": ["sabr", "patience", "patient", "persevere"],
            "Afterlife": ["afterlife", "akhirah", "hereafter", "day of judgment"],
            "Faith": ["faith", "iman", "believe", "belief"],
            "Prayer": ["prayer", "salah", "pray", "rakat"],
            "Quran": ["quran", "recite", "verse", "ayah"],
            "Hadith": ["hadith", "prophet said", "messenger", "narrated"]
        }

        # Count matches for each topic
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                topic_scores[topic] = score

        if not topic_scores:
            return "Other"

        # Return topic with highest score
        return max(topic_scores, key=topic_scores.get)

    def process_chunk(
        self,
        chunk: dict,
        use_llm: bool = False,
        llm_client: Optional[object] = None
    ) -> dict:
        """Process a single transcript chunk.

        Args:
            chunk: Transcript chunk dict with 'text', 'timestamp', etc.
            use_llm: Whether to use LLM for classification.
            llm_client: Optional LLM client for classification.

        Returns:
            Processed chunk with clip detection metadata.
        """
        text = chunk.get("text", "")

        # Pre-filter: Check if chunk has important content
        has_important = self.has_important_content(text)

        if not has_important and not use_llm:
            # Skip detailed processing for generic content
            return {
                **chunk,
                "topic": "Other",
                "emotion_score": 3,
                "clip_candidate": False,
                "skipped": True
            }

        # Detect keywords
        keywords = self.detect_keywords(text)

        # Classify topic (use LLM if available)
        if use_llm and llm_client:
            topic = self._llm_classify_topic(text, llm_client)
        else:
            topic = self.classify_topic(text)

        # Calculate emotion score
        emotion_score = self.calculate_emotion_score(text, topic)

        # Determine if clip candidate
        clip_candidate = (
            topic != "Other" and
            emotion_score >= self.emotion_threshold
        )

        return {
            **chunk,
            "topic": topic,
            "keywords": keywords,
            "emotion_score": emotion_score,
            "clip_candidate": clip_candidate,
            "skipped": False
        }

    def _llm_classify_topic(self, text: str, llm_client: object) -> str:
        """Use LLM to classify topic.

        Args:
            text: Transcript chunk text.
            llm_client: LLM client object with 'ask' method.

        Returns:
            Topic string from VALID_TOPICS.
        """
        # Recommended model: Qwen2.5-3B-Instruct (fits on Tesla T4)
        prompt = f"""Classify the topic of this Islamic lecture segment.

Topics: {', '.join(VALID_TOPICS[:8])}

Text: {text[:600]}

Return topic only."""

        try:
            response = llm_client.ask(prompt)
            topic = response.strip().title()

            # Validate topic
            if topic in VALID_TOPICS:
                return topic
            return "Other"
        except Exception:
            # Fallback to keyword-based classification
            return self.classify_topic(text)

    def process_batch(
        self,
        chunks: list[dict],
        use_llm: bool = False,
        llm_client: Optional[object] = None
    ) -> list[dict]:
        """Process a batch of transcript chunks.

        Args:
            chunks: List of transcript chunk dicts.
            use_llm: Whether to use LLM for classification.
            llm_client: Optional LLM client.

        Returns:
            List of processed chunks with clip detection metadata.
        """
        results = []
        skipped_count = 0

        for i, chunk in enumerate(chunks):
            result = self.process_chunk(chunk, use_llm, llm_client)
            results.append(result)

            if result.get("skipped"):
                skipped_count += 1
                print(f"  ⏭️ Chunk {i+1}/{len(chunks)} - Skipped (generic)")
            else:
                clip_flag = "🎬 " if result["clip_candidate"] else ""
                print(
                    f"  {clip_flag}Chunk {i+1}/{len(chunks)} - "
                    f"Topic: {result['topic']} (Score: {result['emotion_score']})"
                )

        print(
            f"\nProcessed {len(chunks)} chunks: "
            f"{skipped_count} skipped, "
            f"{sum(1 for r in results if r['clip_candidate'])} clip candidates"
        )

        return results

    def merge_adjacent_clips(
        self,
        candidates: list[dict],
        max_duration: int = 60,
        min_duration: int = 15
    ) -> list[dict]:
        """Merge adjacent clip candidates.

        Args:
            candidates: List of clip candidate dicts.
            max_duration: Maximum clip duration in seconds.
            min_duration: Minimum clip duration in seconds.

        Returns:
            List of merged clip dicts.
        """
        if not candidates:
            return []

        # Sort by start time
        sorted_candidates = sorted(
            candidates,
            key=lambda x: self._parse_timestamp(x.get("timestamp_start", "00:00"))
        )

        merged_clips = []
        current_clip = None

        for candidate in sorted_candidates:
            start = self._parse_timestamp(candidate.get("timestamp_start", "00:00"))
            end = self._parse_timestamp(candidate.get("timestamp_end", "00:00"))

            if current_clip is None:
                # Start new clip
                current_clip = {
                    "video_id": candidate.get("video_id"),
                    "timestamp_start": candidate.get("timestamp_start"),
                    "timestamp_end": candidate.get("timestamp_end"),
                    "start_seconds": start,
                    "end_seconds": end,
                    "topics": [candidate.get("topic")],
                    "emotion_scores": [candidate.get("emotion_score", 0)],
                    "chunks": [candidate]
                }
            else:
                # Check if adjacent (within 10 seconds)
                time_gap = start - current_clip["end_seconds"]

                if time_gap <= 10:
                    # Merge into current clip
                    current_clip["timestamp_end"] = candidate.get("timestamp_end")
                    current_clip["end_seconds"] = end
                    current_clip["topics"].append(candidate.get("topic"))
                    current_clip["emotion_scores"].append(candidate.get("emotion_score", 0))
                    current_clip["chunks"].append(candidate)
                else:
                    # Save current clip and start new one
                    if self._is_valid_clip(current_clip, min_duration, max_duration):
                        merged_clips.append(self._finalize_clip(current_clip))

                    current_clip = {
                        "video_id": candidate.get("video_id"),
                        "timestamp_start": candidate.get("timestamp_start"),
                        "timestamp_end": candidate.get("timestamp_end"),
                        "start_seconds": start,
                        "end_seconds": end,
                        "topics": [candidate.get("topic")],
                        "emotion_scores": [candidate.get("emotion_score", 0)],
                        "chunks": [candidate]
                    }

        # Don't forget the last clip
        if current_clip and self._is_valid_clip(current_clip, min_duration, max_duration):
            merged_clips.append(self._finalize_clip(current_clip))

        return merged_clips

    def _is_valid_clip(
        self,
        clip: dict,
        min_duration: int,
        max_duration: int
    ) -> bool:
        """Check if clip meets duration requirements."""
        duration = clip["end_seconds"] - clip["start_seconds"]
        return min_duration <= duration <= max_duration

    def _finalize_clip(self, clip: dict) -> dict:
        """Finalize merged clip with computed fields."""
        duration = clip["end_seconds"] - clip["start_seconds"]

        # Get most common topic
        topic_counts = {}
        for topic in clip["topics"]:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        primary_topic = max(topic_counts, key=topic_counts.get)

        # Get max emotion score
        max_emotion = max(clip["emotion_scores"])

        return {
            "video_id": clip["video_id"],
            "timestamp_start": clip["timestamp_start"],
            "timestamp_end": clip["timestamp_end"],
            "start_seconds": clip["start_seconds"],
            "end_seconds": clip["end_seconds"],
            "duration": duration,
            "topic": primary_topic,
            "all_topics": list(set(clip["topics"])),
            "emotion_score": max_emotion,
            "clip_candidate": True,
            "chunk_count": len(clip["chunks"])
        }

    def _parse_timestamp(self, timestamp: str) -> int:
        """Parse timestamp string to seconds.

        Args:
            timestamp: Timestamp in "MM:SS" or "HH:MM:SS" format.

        Returns:
            Time in seconds.
        """
        if not timestamp:
            return 0

        parts = timestamp.replace(".", ":").split(":")

        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds

        return 0

    def load_transcripts(self, filepath: str) -> list[dict]:
        """Load transcript chunks from JSON file.

        Args:
            filepath: Path to JSON file with transcripts.

        Returns:
            List of transcript chunk dicts.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Transcript file not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle both list and dict with 'chunks' key
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "chunks" in data:
            return data["chunks"]

        return []

    def save_candidates(self, candidates: list[dict], filepath: str) -> None:
        """Save clip candidates to JSON file.

        Args:
            candidates: List of clip candidate dicts.
            filepath: Output file path.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved {len(candidates)} clip candidates to {filepath}")


# Test
if __name__ == "__main__":
    print("Testing ClipDetector...")

    detector = ClipDetector()

    # Test keyword detection
    test_text = "The Prophet said charity extinguishes sins like water extinguishes fire."
    print(f"\nTest text: {test_text}")
    print(f"Has important content: {detector.has_important_content(test_text)}")
    print(f"Detected keywords: {detector.detect_keywords(test_text)}")
    print(f"Classified topic: {detector.classify_topic(test_text)}")
    print(f"Emotion score: {detector.calculate_emotion_score(test_text, 'Charity')}")
