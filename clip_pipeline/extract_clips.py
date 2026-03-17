"""Extract video clips from lectures using ffmpeg.

This module handles:
- Clip extraction from source videos
- Timestamp merging for adjacent segments
- Clip metadata management
"""

import subprocess
from pathlib import Path
from typing import Optional


class ClipExtractor:
    """Extract video clips from source videos using ffmpeg."""

    def __init__(self, output_dir: str = "clips"):
        """
        Initialize clip extractor.

        Args:
            output_dir: Directory to store extracted clips.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_clip(
        self,
        video_path: str,
        start_time: str | float,
        end_time: str | float,
        output_name: str,
        add_subtitles: bool = False,
        subtitle_path: Optional[str] = None
    ) -> str:
        """
        Extract a clip from source video.

        Args:
            video_path: Path to source video.
            start_time: Start time (seconds or "MM:SS" format).
            end_time: End time (seconds or "MM:SS" format).
            output_name: Name for output file (without extension).
            add_subtitles: Whether to burn in subtitles.
            subtitle_path: Path to subtitle file (if add_subtitles=True).

        Returns:
            Path to extracted clip.

        Raises:
            subprocess.CalledProcessError: If ffmpeg fails.
        """
        # Convert to seconds if string format
        if isinstance(start_time, str):
            start_seconds = self._parse_timestamp(start_time)
        else:
            start_seconds = start_time

        if isinstance(end_time, str):
            end_seconds = self._parse_timestamp(end_time)
        else:
            end_seconds = end_time

        duration = end_seconds - start_seconds

        if duration <= 0:
            raise ValueError(f"Invalid duration: {duration}s")

        output_path = self.output_dir / f"{output_name}.mp4"

        # Build ffmpeg command
        if add_subtitles and subtitle_path:
            # Extract with burnt-in subtitles
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(start_seconds),
                "-t", str(duration),
                "-vf", f"subtitles={subtitle_path}",
                "-c:a", "copy",
                "-y",
                str(output_path)
            ]
        else:
            # Fast extraction without re-encoding
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(start_seconds),
                "-t", str(duration),
                "-c", "copy",
                "-y",
                str(output_path)
            ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✓ Extracted clip: {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to extract clip: {e.stderr}")
            raise

    def extract_clips_from_moments(
        self,
        video_path: str,
        moments: list[dict],
        clip_duration: float = 60,
        prefix: str = "clip"
    ) -> list[str]:
        """
        Extract clips for multiple moments.

        Args:
            video_path: Path to source video.
            moments: List of moment dicts with 'timestamp_start' and 'timestamp_end'.
            clip_duration: Default duration if not specified (seconds).
            prefix: Prefix for output filenames.

        Returns:
            List of paths to extracted clips.
        """
        clip_paths = []

        for i, moment in enumerate(moments):
            start = moment.get("timestamp_start", moment.get("start_seconds", 0))
            end = moment.get("timestamp_end", moment.get("end_seconds", start + clip_duration))

            # Sanitize topic for filename
            topic = moment.get("topic", f"moment_{i}")
            safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:20])

            output_name = f"{prefix}_{i:03d}_{safe_topic}"

            try:
                clip_path = self.extract_clip(
                    video_path, start, end, output_name
                )
                clip_paths.append(clip_path)
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to extract clip {i}: {e}")

        return clip_paths

    def create_vertical_clip(
        self,
        video_path: str,
        start_time: str | float,
        end_time: str | float,
        output_name: str
    ) -> str:
        """
        Create a vertical (9:16) clip for social media.

        Args:
            video_path: Path to source video.
            start_time: Start time.
            end_time: End time.
            output_name: Output filename.

        Returns:
            Path to vertical clip.
        """
        if isinstance(start_time, str):
            start_seconds = self._parse_timestamp(start_time)
        else:
            start_seconds = start_time

        if isinstance(end_time, str):
            end_seconds = self._parse_timestamp(end_time)
        else:
            end_seconds = end_time

        duration = end_seconds - start_seconds
        output_path = self.output_dir / f"{output_name}_vertical.mp4"

        # Crop to 9:16 aspect ratio (center crop)
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(start_seconds),
            "-t", str(duration),
            "-vf", "crop=ih*(9/16):ih",
            "-c:a", "copy",
            "-y",
            str(output_path)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✓ Extracted vertical clip: {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to extract vertical clip: {e.stderr}")
            raise

    def _parse_timestamp(self, timestamp: str | float) -> float:
        """
        Parse timestamp to seconds.

        Args:
            timestamp: Timestamp in seconds or "MM:SS" / "HH:MM:SS" format.

        Returns:
            Time in seconds.
        """
        if isinstance(timestamp, (int, float)):
            return float(timestamp)

        if not timestamp:
            return 0.0

        parts = timestamp.replace(".", ":").split(":")

        if len(parts) == 2:
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds

        try:
            return float(timestamp)
        except ValueError:
            return 0.0

    def get_video_duration(self, video_path: str) -> float:
        """
        Get video duration using ffprobe.

        Args:
            video_path: Path to video file.

        Returns:
            Duration in seconds.
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    def format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as MM:SS timestamp.

        Args:
            seconds: Time in seconds.

        Returns:
            Formatted timestamp string.
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def format_timestamp_hms(self, seconds: float) -> str:
        """
        Format seconds as HH:MM:SS timestamp.

        Args:
            seconds: Time in seconds.

        Returns:
            Formatted timestamp string.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# Test
if __name__ == "__main__":
    print("Testing ClipExtractor...")

    extractor = ClipExtractor(output_dir="test_clips")

    # Test timestamp parsing
    print(f"\nTimestamp parsing tests:")
    print(f"  '02:30' -> {extractor._parse_timestamp('02:30')}s")
    print(f"  '01:02:30' -> {extractor._parse_timestamp('01:02:30')}s")
    print(f"  150.5 -> {extractor._parse_timestamp(150.5)}s")

    # Test timestamp formatting
    print(f"\nTimestamp formatting tests:")
    print(f"  150s -> {extractor.format_timestamp(150)}")
    print(f"  3750s -> {extractor.format_timestamp_hms(3750)}")
