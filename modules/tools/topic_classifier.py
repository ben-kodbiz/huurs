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

PROMPT_TEMPLATE = """You are an Islamic knowledge classifier.
Classify the given text into one or more topics from this list:

{topics}

Return ONLY valid JSON with this structure:
{{
  "topics": ["Topic1", "Topic2"]
}}

Rules:
- Choose 1-3 most relevant topics
- Return ONLY JSON, no explanation
- If content doesn't match any topic well, use "Other"

Text to classify:
---
{text}
---

JSON:"""

def classify(text):
    """
    Classify Islamic wisdom text into relevant topics.
    
    Args:
        text: The extracted text from poster (Arabic + translation)
    
    Returns:
        List of topic strings
    """
    prompt = PROMPT_TEMPLATE.format(topics="\n".join("- " + t for t in ISLAMIC_TOPICS), text=text)
    
    try:
        response = llm.ask(prompt)
        
        # Clean the response
        response = response.replace("```json", "").replace("```", "").strip()
        
        import json
        data = json.loads(response)
        topics = data.get("topics", ["Other"])
        
        # Validate topics
        valid_topics = [t for t in topics if t in ISLAMIC_TOPICS]
        return valid_topics if valid_topics else ["Other"]
        
    except Exception as e:
        print(f"Classification error: {e}")
        # Fallback: keyword-based classification
        return keyword_classify(text)

def keyword_classify(text):
    """Fallback keyword-based classification."""
    text_lower = text.lower()
    topics = []
    
    if any(w in text_lower for w in ["prayer", "salah", "pray"]):
        topics.append("Salah (Prayer)")
    if any(w in text_lower for w in ["patience", "sabr", "patient"]):
        topics.append("Sabr (Patience)")
    if any(w in text_lower for w in ["gratitude", "shukr", "thank"]):
        topics.append("Shukr (Gratitude)")
    if any(w in text_lower for w in ["dua", "supplication", "pray", "lord"]):
        topics.append("Dua (Supplication)")
    if any(w in text_lower for w in ["knowledge", "wisdom", "learn"]):
        topics.append("Knowledge/Wisdom")
    if any(w in text_lower for w in ["mercy", "love", "compassion"]):
        topics.append("Love/Mercy")
    if any(w in text_lower for w in ["forgive", "forgiveness"]):
        topics.append("Forgiveness")
    
    return topics if topics else ["Other"]
