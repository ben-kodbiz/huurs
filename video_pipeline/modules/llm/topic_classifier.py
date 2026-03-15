"""LLM topic classifier for transcript chunks."""

import httpx
from configs.settings import LMSTUDIO_BASE_URL, MODEL_NAME, TIMEOUT


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
    "Justice/Oppression",
    "Sin/Repentance",
    "Other"
]

CLASSIFIER_PROMPT = """You are an Islamic knowledge classifier.
Classify the given lecture transcript chunk into the most relevant topic.

Available topics:
{topics}

Return ONLY valid JSON:
{{
  "primary_topic": "Topic Name",
  "secondary_topics": ["Topic2", "Topic3"],
  "confidence": 0.95
}}

Rules:
- Choose 1 primary topic (most relevant)
- Choose 0-2 secondary topics (optional)
- Confidence: 0.0 to 1.0
- Return ONLY JSON, no explanation

Transcript chunk:
---
{text}
---

JSON:"""


class TopicClassifier:
    """LLM-based topic classifier for transcript chunks."""
    
    def __init__(self):
        self.endpoint = f"{LMSTUDIO_BASE_URL}/chat/completions"
        self.topics_list = "\n".join(f"- {t}" for t in ISLAMIC_TOPICS)
    
    def classify(self, text):
        """
        Classify a transcript chunk into topics.
        
        Args:
            text: Transcript chunk text
            
        Returns:
            Dict with primary_topic, secondary_topics, confidence
        """
        prompt = CLASSIFIER_PROMPT.format(
            topics=self.topics_list,
            text=text[:2000]  # Limit text length
        )
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an Islamic knowledge classifier. Output only JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 256
        }
        
        try:
            client = httpx.Client(timeout=TIMEOUT)
            r = client.post(self.endpoint, json=payload)
            r.raise_for_status()
            
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            
            # Parse JSON response
            import json
            content = content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            
            # Validate topic
            primary = result.get("primary_topic", "Other")
            if primary not in ISLAMIC_TOPICS:
                primary = "Other"
            
            return {
                "primary_topic": primary,
                "secondary_topics": result.get("secondary_topics", []),
                "confidence": result.get("confidence", 0.8)
            }
            
        except Exception as e:
            print(f"[WARN] Classification error: {e}")
            # Fallback to keyword-based classification
            return self._keyword_classify(text)
    
    def _keyword_classify(self, text):
        """Fallback keyword-based classification."""
        text_lower = text.lower()
        
        keyword_topics = {
            "prayer": "Salah (Prayer)",
            "salah": "Salah (Prayer)",
            "charity": "Zakat (Charity)",
            "zakat": "Zakat (Charity)",
            "fasting": "Sawm (Fasting)",
            "ramadan": "Sawm (Fasting)",
            "hajj": "Hajj (Pilgrimage)",
            "patience": "Sabr (Patience)",
            "sabr": "Sabr (Patience)",
            "gratitude": "Shukr (Gratitude)",
            "shukr": "Shukr (Gratitude)",
            "dua": "Dua (Supplication)",
            "supplication": "Dua (Supplication)",
            "oppression": "Justice/Oppression",
            "justice": "Justice/Oppression",
            "sin": "Sin/Repentance",
            "repentance": "Sin/Repentance",
            "forgive": "Forgiveness",
        }
        
        for keyword, topic in keyword_topics.items():
            if keyword in text_lower:
                return {
                    "primary_topic": topic,
                    "secondary_topics": [],
                    "confidence": 0.6
                }
        
        return {
            "primary_topic": "Other",
            "secondary_topics": [],
            "confidence": 0.5
        }
