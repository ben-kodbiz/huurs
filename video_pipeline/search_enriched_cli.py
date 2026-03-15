"""CLI for searching enriched transcripts."""

from modules.search.enriched_search import EnrichedSearch


def main():
    search = EnrichedSearch()
    
    print("=" * 60)
    print("Enriched Transcript Search")
    print("=" * 60)
    print()
    
    while True:
        print("Commands:")
        print("  topics          - List all topics")
        print("  topic <name>    - Search by topic")
        print("  summary <query> - Search in summaries")
        print("  time <ts>       - Get chunk by timestamp")
        print("  quit            - Exit")
        print()
        
        cmd = input("> ").strip()
        
        if cmd == "quit" or cmd == "exit":
            break
        
        parts = cmd.split(" ", 1)
        action = parts[0]
        
        if action == "topics":
            topics = search.get_all_topics()
            print(f"Topics ({len(topics)}):")
            for t in topics:
                print(f"  {t['topic']}: {t['count']}")
        
        elif action == "topic" and len(parts) > 1:
            topic = parts[1]
            results = search.search_by_topic(topic)
            print_results(results, f"Topic: {topic}")
        
        elif action == "summary" and len(parts) > 1:
            query = parts[1]
            results = search.search_summary(query)
            print_results(results, f"Summary search: {query}")
        
        elif action == "time" and len(parts) > 1:
            ts = parts[1]
            result = search.get_chunk(ts)
            if result:
                print(f"Timestamp: {result['timestamp']}")
                print(f"Topic: {result['topic']}")
                print(f"Summary: {result['summary']}")
                print(f"Text: {result['text'][:200]}...")
            else:
                print("Chunk not found")
        
        else:
            print("Unknown command")
        
        print()
        print("-" * 60)
        print()
    
    search.close()
    print("Goodbye!")


def print_results(results, title):
    """Print search results."""
    if not results:
        print("No results found.")
        return
    
    print(f"{title} - Found {len(results)} result(s):")
    print()
    
    for i, r in enumerate(results, 1):
        print(f"[{i}] {r['video_id']} @ {r['timestamp']}")
        print(f"    Topic: {r['topic']}")
        print(f"    Summary: {r['summary'][:150]}...")
        print()


if __name__ == "__main__":
    main()
