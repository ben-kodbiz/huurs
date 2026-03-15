import httpx
import base64
import re
import json

from configs.settings import LMSTUDIO_BASE_URL, MODEL_NAME, TIMEOUT


class LMStudioLLM:

    def __init__(self):
        self.endpoint = f"{LMSTUDIO_BASE_URL}/chat/completions"

    def _clean_output(self, text):
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        text = text.replace("```json", "")
        text = text.replace("```", "")
        return text.strip()

    def ask(self, prompt):
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1024
        }

        r = httpx.post(self.endpoint, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        return self._clean_output(content)

    def extract_text_from_image(self, image_path):
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()

        ext = image_path.split(".")[-1].lower()
        mime_type = f"image/{ext}" if ext in ["jpg", "jpeg", "png", "webp"] else "image/jpeg"

        prompt = """Extract ALL text from this image. Return ONLY valid JSON:

{
  "text_extraction": {
    "header": "",
    "main_title": "",
    "arabic_text": "",
    "translation": "",
    "source": ""
  }
}

Preserve Arabic text exactly. Leave empty string if not found."""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Only output JSON."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}
                ]}
            ],
            "temperature": 0.2,
            "max_tokens": 2048
        }

        r = httpx.post(self.endpoint, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        
        cleaned = self._clean_output(content)
        
        try:
            return json.loads(cleaned)
        except Exception as e:
            return {"error": "Invalid JSON", "raw": cleaned, "exception": str(e)}
