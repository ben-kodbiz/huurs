"""Generate video clips from key moments."""

import subprocess
from pathlib import Path


class ClipGenerator:
    """Generate short video clips from source video."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_name: str,
    ) -> str:
        """
        Generate a clip from the source video.

        Args:
            video_path: Path to source video.
            start_time: Start time in seconds.
            end_time: End time in seconds.
            output_name: Name for output file.

        Returns:
            Path to generated clip.
        """
        duration = end_time - start_time
        output_path = self.output_dir / f"{output_name}.mp4"

        # Use ffmpeg to cut video
        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-ss",
            str(start_time),
            "-t",
            str(duration),
            "-c",
            "copy",
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        return str(output_path)

    def generate_clips_from_moments(
        self, video_path: str, moments: list[dict], clip_duration: float = 60
    ) -> list[str]:
        """
        Generate clips for each key moment.

        Args:
            video_path: Path to source video.
            moments: List of moment dicts with 'time' and 'description'.
            clip_duration: Duration of each clip in seconds.

        Returns:
            List of paths to generated clips.
        """
        clip_paths = []

        for i, moment in enumerate(moments):
            start_time = max(0, moment["time"] - 5)  # Start 5s before moment
            end_time = start_time + clip_duration

            # Sanitize description for filename
            description = moment.get("description", f"moment_{i}")
            safe_name = "".join(c if c.isalnum() else "_" for c in description[:30])

            try:
                clip_path = self.generate_clip(
                    video_path, start_time, end_time, f"clip_{i}_{safe_name}"
                )
                clip_paths.append(clip_path)
            except subprocess.CalledProcessError as e:
                print(f"Failed to generate clip {i}: {e}")

        return clip_paths
