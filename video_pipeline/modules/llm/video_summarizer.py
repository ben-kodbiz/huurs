import httpx
from configs.settings import LMSTUDIO_BASE_URL, MODEL_NAME, TIMEOUT


class VideoSummarizer:

    def summarize(self, text):

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role":"system",
                    "content":"Summarize Islamic lecture text into key lessons."
                },
                {
                    "role":"user",
                    "content":text
                }
            ],
            "temperature":0.3
        }

        client = httpx.Client(timeout=TIMEOUT)
        r = client.post(
            f"{LMSTUDIO_BASE_URL}/chat/completions",
            json=payload
        )

        data = r.json()

        return data["choices"][0]["message"]["content"]