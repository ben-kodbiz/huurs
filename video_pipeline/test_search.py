"""Test the search functionality."""

from modules.search.video_search import VideoSearch


def test_search():
    """Test search functionality."""
    search = VideoSearch()
    
    print("=" * 60)
    print("Testing Video Search")
    print("=" * 60)
    print()
    
    # List all videos
    print("[1] Getting all videos...")
    videos = search.get_all_videos()
    print(f"    Found {len(videos)} videos:")
    for v in videos:
        print(f"      - {v['video_id']}: {v['title']}")
    print()
    
    # Test keyword search
    print("[2] Testing keyword search for 'Allah'...")
    results = search.search("Allah", limit=5)
    print(f"    Found {len(results)} results")
    for i, r in enumerate(results[:3], 1):
        print(f"      [{i}] {r['video_id']} @ {r['timestamp']}")
    print()
    
    # Test video transcripts
    if videos:
        video_id = videos[0]['video_id']
        print(f"[3] Getting transcripts for '{video_id}'...")
        results = search.get_video_transcripts(video_id, limit=5)
        print(f"    Found {len(results)} transcript chunks")
        for i, r in enumerate(results[:3], 1):
            print(f"      [{i}] @ {r['timestamp']}: {r['text'][:50]}...")
    print()
    
    search.close()
    print("=" * 60)
    print("Search test completed!")


if __name__ == "__main__":
    test_search()
