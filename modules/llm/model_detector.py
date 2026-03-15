import httpx
from configs.settings import LMSTUDIO_BASE_URL

def detect_model():

    r = httpx.get(f"{LMSTUDIO_BASE_URL}/models")

    models = r.json()["data"]

    return models[0]["id"]