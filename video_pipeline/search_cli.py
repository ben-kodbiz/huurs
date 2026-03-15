"""Search CLI for video transcripts."""

from modules.search.video_search import VideoSearch


def main():
    search = VideoSearch()
    
    print("=" * 60)
    print("Video Transcript Search")
    print("=" * 60)
    print()
    
    while True:
        print("Commands:")
        print("  search <query>  - Keyword search")
        print("  topic <name>    - Search by topic")
        print("  topics          - List all topics")
        print("  video <id>      - Show video transcripts")
        print("  quit            - Exit")
        print()
        
        cmd = input("> ").strip()
        
        if cmd == "quit" or cmd == "exit":
            break
        
        parts = cmd.split(" ", 1)
        action = parts[0]
        
        if action == "search" and len(parts) > 1:
            query = parts[1]
            results = search.search(query)
            print_results(results)
        
        elif action == "topic" and len(parts) > 1:
            topic = parts[1]
            results = search.search_by_topic(topic)
            print_results(results)
        
        elif action == "topics":
            topics = search.get_all_topics()
            print(f"Available topics ({len(topics)}):")
            for t in topics:
                print(f"  - {t}")
        
        elif action == "video" and len(parts) > 1:
            video_id = parts[1]
            results = search.get_video_transcripts(video_id)
            print_results(results)
        
        else:
            print("Unknown command. Use 'search', 'topic', 'topics', 'video', or 'quit'.")
        
        print()
        print("-" * 60)
        print()
    
    search.close()
    print("Goodbye!")


def print_results(results):
    """Format and print search results."""
    if not results:
        print("No results found.")
        return
    
    print(f"Found {len(results)} result(s):")
    print()
    
    for i, r in enumerate(results, 1):
        print(f"[{i}] Video: {r['video_id']}")
        print(f"    Timestamp: {r['timestamp']}")
        print(f"    Topic: {r['primary_topic']}")
        print(f"    Summary: {r['summary'][:200]}...")
        print()


if __name__ == "__main__":
    main()
