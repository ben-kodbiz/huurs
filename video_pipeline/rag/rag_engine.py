"""RAG Engine - Combine retrieval and LLM reasoning."""

from rag.retriever import Retriever
from rag.prompt_builder import PromptBuilder
from rag.llm_client import LLMClient


class RAGEngine:
    """Main RAG engine for answering questions."""
    
    def __init__(self):
        self.retriever = Retriever()
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
        chunks = self.retriever.search_transcripts(question, limit)
        
        if not chunks:
            return {
                "answer": "No lecture content matched your question. Please try rephrasing.",
                "sources": []
            }
        
        # Step 2: Build context
        context = self.prompt_builder.build_context(chunks)
        
        # Step 3: Build prompt
        prompt = self.prompt_builder.build_prompt(question, context)
        
        # Step 4: Get LLM answer
        answer = self.llm.ask(prompt)
        
        # Step 5: Prepare sources
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
            "context_used": context
        }
    
    def close(self):
        """Close resources."""
        self.retriever.close()
