"""Test the RAG system."""

from rag.rag_engine import RAGEngine


def test_rag():
    """Test RAG engine with sample questions."""
    print("=" * 60)
    print("Testing Video RAG System")
    print("=" * 60)
    print()
    
    engine = RAGEngine()
    
    # Check LLM availability
    print("[1] Checking LLM availability...")
    llm_available = engine.llm.is_available()
    print(f"    LLM available: {llm_available}")
    print()
    
    # Test questions
    questions = [
        "What does Islam say about charity?",
        "How can sins be forgiven?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"[{i}] Question: {question}")
        print()
        
        result = engine.answer_question(question, limit=5)
        
        print(f"    Answer: {result['answer'][:200]}...")
        print()
        
        if result['sources']:
            print(f"    Sources ({len(result['sources'])}):")
            for src in result['sources'][:3]:
                print(f"      - {src['video_id']} @ {src['timestamp']}")
        print()
        print("-" * 60)
        print()
    
    engine.close()
    print("RAG test completed!")


if __name__ == "__main__":
    test_rag()
