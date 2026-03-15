"""
Video Pipeline - Offline Mode

Pipeline flow:
    video → subtitle → chunk transcript → store chunks → build search index
"""

from modules.downloader.yt_downloader import YTDownloader
from modules.transcript.subtitle_parser import SubtitleParser
from modules.transcript.transcript_chunker import TranscriptChunker
from modules.search.ytfs_indexer import YTFTSIndexer
from database.video_db import VideoDB
from configs.settings import VIDEO_DIR
import os


def run(source=None):
    """
    Run the video pipeline.

    Args:
        source: Path to local video file or YouTube URL
    """

    if source is None:
        # Look for videos in the videos directory
        if os.path.exists(VIDEO_DIR):
            video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(('.mp4', '.mkv', '.avi', '.mov'))]
            if video_files:
                source = os.path.join(VIDEO_DIR, video_files[0])
                print(f"[INFO] Found local video: {source}")
            else:
                source = input("Enter video file path or YouTube URL: ")
        else:
            source = input("Enter video file path or YouTube URL: ")

    # Initialize components
    downloader = YTDownloader()
    parser = SubtitleParser()
    chunker = TranscriptChunker()
    fts = YTFTSIndexer()
    db = VideoDB()

    # Step 1: Fetch metadata
    print("[INFO] fetching metadata")
    video = downloader.fetch_metadata(source)

    db.insert_video(
        video["video_id"],
        video["title"],
        video["channel"],
        video["url"]
    )

    print(f"[INFO] Video: {video['title']}")
    print(f"[INFO] Channel: {video['channel']}")

    # Step 2: Download/locate subtitles
    print("[INFO] downloading subtitles")
    subtitle_file = downloader.download_subtitles(source)

    if subtitle_file is None:
        print("[!] No subtitles available. Pipeline halted.")
        print("[HINT] Please provide a video with subtitles or add subtitle file manually.")
        return

    print(f"[INFO] Subtitle file: {subtitle_file}")

    # Step 3: Index subtitles
    print("[INFO] indexing subtitles")
    fts.index_subtitles(subtitle_file, video["video_id"])

    # Step 4: Parse subtitles
    print("[INFO] parsing subtitles")
    transcript = parser.parse(subtitle_file)

    # Step 5: Chunk transcript
    chunks = chunker.chunk(transcript)
    print(f"[INFO] processing {len(chunks)} transcript chunks")

    # Step 6: Store chunks
    for i, chunk in enumerate(chunks):
        text = " ".join([x["text"] for x in chunk])
        timestamp = chunk[0]["timestamp"]

        print(f"  Storing chunk {i+1}/{len(chunks)}...")

        db.insert_transcript(
            video["video_id"],
            timestamp,
            text
        )

    # Step 7: Rebuild search index
    print("[INFO] building search index")
    db.rebuild_fts_index()

    print("[✓] pipeline completed")


if __name__ == "__main__":
    run()