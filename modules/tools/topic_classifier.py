from modules.llm.llm_engine import LMStudioLLM

llm = LMStudioLLM()

ISLAMIC_TOPICS = [
    "Tawheed (Oneness of Allah)",
    "Salah (Prayer)",
    "Zakat (Charity)",
    "Sawm (Fasting)",
    "Hajj (Pilgrimage)",
    "Akhlaq (Character/Manners)",
    "Sabr (Patience)",
    "Shukr (Gratitude)",
    "Love/Mercy",
    "Forgiveness",
    "Knowledge/Wisdom",
    "Death/Afterlife",
    "Dua (Supplication)",
    "Jihad (Struggle)",
    "Halal/Haram",
    "Family/Parents",
    "Neighbors/Community",
    "Wealth/Rizq",
    "Health/Healing",
    "Other"
]

SYSTEM_PROMPT = f"""You are an Islamic knowledge classifier.
Classify the given text into one or more topics from this list:

{chr(10).join("- " + t for t in ISLAMIC_TOPICS)}

Return ONLY valid JSON with this structure:
{{
  "topics": ["Topic1", "Topic2"]
}}

Rules:
- Choose 1-3 most relevant topics
- Return ONLY JSON, no explanation
- If content doesn't match any topic well, use "Other"
"""

def classify(text):
    """
    Classify Islamic wisdom text into relevant topics.
    
    Args:
        text: The extracted text from poster (Arabic + translation)
    
    Returns:
        List of topic strings
    """
    prompt = f"""Classify this Islamic wisdom content:

---
{text}
---

Return JSON with topics list."""

    response = llm.ask(SYSTEM_PROMPT + "\n\n" + prompt)
    
    try:
        import json
        # Clean the response
        response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(response)
        return data.get("topics", ["Other"])
    except Exception as e:
        print(f"Classification error: {e}")
        return ["Other"]
