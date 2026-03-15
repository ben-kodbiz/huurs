"""RAG Engine - Combine retrieval and LLM reasoning."""

from rag.hybrid_retriever import HybridRetriever
from rag.prompt_builder import PromptBuilder
from rag.llm_client import LLMClient


class RAGEngine:
    """Main RAG engine for answering questions."""

    def __init__(self):
        self.retriever = HybridRetriever()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()

    def answer_question(self, question, limit=10):
        """
        Answer a question using RAG.

        Args:
            question: User's question
            limit: Number of transcript chunks to retrieve

        Returns:
            Dict with answer and sources
        """
        # Step 1: Retrieve relevant transcripts
        chunks = self.retriever.search(question, limit)
        
        if not chunks:
            return {
                "answer": "No lecture content matched your question. Please try rephrasing.",
                "sources": [],
                "llm_used": False
            }
        
        # Step 2: Check if LLM is available
        llm_available = self.llm.is_available()

        if llm_available:
            # Step 3: Build context and get LLM answer
            context = self.prompt_builder.build_context(chunks)
            prompt = self.prompt_builder.build_prompt(question, context)
            answer = self.llm.ask(prompt)
            llm_used = True
        else:
            # Fallback: Return retrieved chunks without LLM
            answer = self._build_fallback_answer(chunks)
            llm_used = False

        # Step 4: Prepare sources
        sources = [
            {
                "video_id": chunk["video_id"],
                "timestamp": chunk["timestamp"]
            }
            for chunk in chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
            "llm_used": llm_used
        }
    
    def _build_fallback_answer(self, chunks):
        """Build answer from retrieved chunks when LLM is unavailable."""
        answer = "[LLM unavailable - Showing retrieved transcript excerpts]\n\n"
        
        for i, chunk in enumerate(chunks, 1):
            answer += f"[{i}] {chunk['video_id']} @ {chunk['timestamp']}\n"
            answer += f"    \"{chunk['text'][:300]}\"\n\n"
        
        answer += f"\nFound {len(chunks)} relevant transcript segments above."
        return answer
    
    def close(self):
        """Close resources."""
        self.retriever.close()
