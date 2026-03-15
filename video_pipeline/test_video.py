"""Test the video pipeline with a specific URL."""

from run_video_pipeline import run

# Test URL - try a well-known Islamic video that should be available
URL = "https://www.youtube.com/watch?v=RYQnR_6bE-4"

print(f"Testing video pipeline with: {URL}")
print("=" * 60)

run(URL)
