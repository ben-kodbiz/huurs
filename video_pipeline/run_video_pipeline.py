from modules.downloader.yt_downloader import YTDownloader
from modules.transcript.subtitle_parser import SubtitleParser
from modules.transcript.transcript_chunker import TranscriptChunker
from modules.search.ytfs_indexer import YTFTSIndexer
from modules.llm.video_summarizer import VideoSummarizer
from database.video_db import VideoDB
import os


def run(source=None):
    """
    Run the video pipeline.
    
    Args:
        source: YouTube URL or path to local video file
    """

    if source is None:
        # Look for videos in the videos directory
        videos_dir = "data/videos"
        if os.path.exists(videos_dir):
            video_files = [f for f in os.listdir(videos_dir) if f.endswith(('.mp4', '.mkv', '.avi', '.mov'))]
            if video_files:
                source = os.path.join(videos_dir, video_files[0])
                print(f"[INFO] Found local video: {source}")
            else:
                source = input("Enter YouTube URL or video file path: ")
        else:
            source = input("Enter YouTube URL or video file path: ")

    downloader = YTDownloader()
    parser = SubtitleParser()
    chunker = TranscriptChunker()
    fts = YTFTSIndexer()
    summarizer = VideoSummarizer()
    db = VideoDB()

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

    print("[INFO] downloading subtitles")

    subtitle_file = downloader.download_subtitles(source)

    if subtitle_file is None:
        print("[!] No subtitles available. Pipeline halted.")
        print("[HINT] Please provide a video with subtitles or add subtitle file manually.")
        return

    print(f"[INFO] Subtitle file: {subtitle_file}")
    print("[INFO] indexing subtitles with yt-fts")

    fts.index_subtitles(subtitle_file, video["video_id"])

    print("[INFO] parsing subtitles")

    transcript = parser.parse(subtitle_file)

    chunks = chunker.chunk(transcript)

    print(f"[INFO] summarizing {len(chunks)} transcript chunks")

    for i, chunk in enumerate(chunks):
        text = " ".join([x["text"] for x in chunk])
        timestamp = chunk[0]["timestamp"]

        print(f"  Processing chunk {i+1}/{len(chunks)}...")

        summary = summarizer.summarize(text)

        db.insert_transcript(
            video["video_id"],
            timestamp,
            text,
            summary
        )

    print("[✓] pipeline completed")


if __name__ == "__main__":
    run()