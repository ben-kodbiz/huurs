"""Test the video pipeline with a local video file."""

from run_video_pipeline import run
import os

# Check for videos in data/videos directory
videos_dir = "data/videos"

if os.path.exists(videos_dir):
    video_files = [f for f in os.listdir(videos_dir) if f.endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    if video_files:
        video_path = os.path.join(videos_dir, video_files[0])
        print(f"Testing video pipeline with: {video_path}")
        print("=" * 60)
        run(video_path)
    else:
        print(f"No video files found in {videos_dir}/")
        print("Please add a video file to test the pipeline.")
else:
    print(f"Videos directory not found: {videos_dir}/")
    print("Please create the directory and add a video file.")
