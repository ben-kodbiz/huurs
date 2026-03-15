from modules.downloader.yt_downloader import YTDownloader
from modules.transcript.subtitle_parser import SubtitleParser
from modules.transcript.transcript_chunker import TranscriptChunker
from modules.search.ytfs_indexer import YTFTSIndexer
from modules.llm.video_summarizer import VideoSummarizer
from database.video_db import VideoDB


def run(url=None):

    if url is None:
        url = input("Enter YouTube URL: ")

    downloader = YTDownloader()
    parser = SubtitleParser()
    chunker = TranscriptChunker()
    fts = YTFTSIndexer()
    summarizer = VideoSummarizer()
    db = VideoDB()

    print("[INFO] fetching metadata")

    video = downloader.fetch_metadata(url)

    db.insert_video(
        video["video_id"],
        video["title"],
        video["channel"],
        video["url"]
    )

    print("[INFO] downloading subtitles")

    subtitle_file = downloader.download_subtitles(url)

    print("[INFO] indexing subtitles with yt-fts")

    fts.index_subtitles(subtitle_file, video["video_id"])

    print("[INFO] parsing subtitles")

    transcript = parser.parse(subtitle_file)

    chunks = chunker.chunk(transcript)

    print("[INFO] summarizing transcript chunks")

    for chunk in chunks:

        text = " ".join([x["text"] for x in chunk])

        timestamp = chunk[0]["timestamp"]

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