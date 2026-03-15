"""Prompt Builder Module - Build context for LLM."""


class PromptBuilder:
    """Build structured prompts for the LLM."""
    
    SYSTEM_PROMPT = """You are an Islamic knowledge assistant.
Answer the user's question using only the lecture excerpts provided below.

Rules:
- Use only the information from the lecture excerpts
- If the answer is not in the excerpts, say: "The lectures did not discuss this topic."
- Cite timestamps when referencing specific content
- Be clear and concise

"""
    
    def build_context(self, chunks):
        """
        Build a formatted context string from transcript chunks.
        
        Args:
            chunks: List of transcript chunks with video_id, timestamp, text
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_lines = []
        
        for chunk in chunks:
            context_lines.append(f"Video: {chunk['video_id']}")
            context_lines.append(f"Timestamp: {chunk['timestamp']}")
            context_lines.append(f"Transcript: {chunk['text']}")
            context_lines.append("")  # Empty line between chunks
        
        return "\n".join(context_lines)
    
    def build_prompt(self, question, context):
        """
        Build the full prompt for the LLM.
        
        Args:
            question: User's question
            context: Formatted context from transcript chunks
            
        Returns:
            Complete prompt string
        """
        prompt = self.SYSTEM_PROMPT
        prompt += f"\nQuestion:\n{question}\n\n"
        prompt += f"Lecture excerpts:\n{context}\n"
        prompt += "\nAnswer:"
        
        return prompt
