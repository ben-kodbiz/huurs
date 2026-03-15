"""LLM Client Module - Communicate with LM Studio."""

import httpx
from configs.settings import LMSTUDIO_BASE_URL, MODEL_NAME, TIMEOUT


class LLMClient:
    """Client for LM Studio API."""
    
    def __init__(self):
        self.endpoint = f"{LMSTUDIO_BASE_URL}/chat/completions"
        self.model = MODEL_NAME
        self.timeout = TIMEOUT
    
    def ask(self, prompt, system_prompt=None):
        """
        Send a prompt to the LLM and get a response.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            
        Returns:
            LLM response text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1024
        }
        
        try:
            client = httpx.Client(timeout=self.timeout)
            r = client.post(self.endpoint, json=payload)
            r.raise_for_status()
            
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            
            return content.strip()
            
        except httpx.TimeoutException:
            return "Error: LLM request timed out. Please try again."
        except Exception as e:
            return f"Error: LLM request failed - {str(e)}"
    
    def is_available(self):
        """Check if LLM server is available."""
        try:
            client = httpx.Client(timeout=5)
            r = client.get(f"{LMSTUDIO_BASE_URL}/models")
            return r.status_code == 200
        except:
            return False
