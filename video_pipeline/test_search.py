"""Test the search functionality."""

from modules.search.video_search import VideoSearch


def test_search():
    """Test search functionality."""
    search = VideoSearch()
    
    print("=" * 60)
    print("Testing Video Search")
    print("=" * 60)
    print()
    
    # List all topics
    print("[1] Getting all topics...")
    topics = search.get_all_topics()
    print(f"    Found {len(topics)} topics:")
    for t in topics[:10]:  # Show first 10
        print(f"      - {t}")
    if len(topics) > 10:
        print(f"      ... and {len(topics) - 10} more")
    print()
    
    # Test keyword search
    print("[2] Testing keyword search for 'Allah'...")
    results = search.search("Allah", limit=5)
    print(f"    Found {len(results)} results")
    for i, r in enumerate(results[:3], 1):
        print(f"      [{i}] {r['video_id']} @ {r['timestamp']}")
        print(f"          Topic: {r['primary_topic']}")
    print()
    
    # Test topic search
    if topics:
        topic = topics[0]
        print(f"[3] Testing topic search for '{topic}'...")
        results = search.search_by_topic(topic, limit=5)
        print(f"    Found {len(results)} results")
        for i, r in enumerate(results[:3], 1):
            print(f"      [{i}] {r['video_id']} @ {r['timestamp']}")
    print()
    
    # Test hybrid search
    print("[4] Testing hybrid search...")
    results = search.hybrid_search("guidance", limit=5)
    print(f"    Found {len(results)} results")
    for i, r in enumerate(results[:3], 1):
        print(f"      [{i}] {r['video_id']} @ {r['timestamp']}")
        print(f"          Topic: {r['primary_topic']}")
    print()
    
    search.close()
    print("=" * 60)
    print("Search test completed!")


if __name__ == "__main__":
    test_search()
