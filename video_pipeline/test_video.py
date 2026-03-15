"""Test the video pipeline with a local video file."""

from run_video_pipeline import run
from configs.settings import VIDEO_DIR
import os

# Check for videos in VIDEO_DIR directory
if os.path.exists(VIDEO_DIR):
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    if video_files:
        video_path = os.path.join(VIDEO_DIR, video_files[0])
        print(f"Testing video pipeline with: {video_path}")
        print("=" * 60)
        run(video_path)
    else:
        print(f"No video files found in {VIDEO_DIR}/")
        print("Please add a video file to test the pipeline.")
else:
    print(f"Videos directory not found: {VIDEO_DIR}/")
    print("Please create the directory and add a video file.")
