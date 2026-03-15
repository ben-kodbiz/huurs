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
        print("  videos          - List all videos")
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
        
        elif action == "videos":
            videos = search.get_all_videos()
            print(f"Videos ({len(videos)}):")
            for v in videos:
                print(f"  - {v['video_id']}: {v['title']} ({v['channel']})")
        
        elif action == "video" and len(parts) > 1:
            video_id = parts[1]
            results = search.get_video_transcripts(video_id)
            print_results(results)
        
        else:
            print("Unknown command. Use 'search', 'videos', 'video', or 'quit'.")
        
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
        print(f"    Text: {r['text'][:200]}...")
        print()


if __name__ == "__main__":
    main()
