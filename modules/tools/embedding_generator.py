from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_model():
    """Load embedding model (singleton pattern)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def generate_embedding(text):
    """
    Generate vector embedding for Islamic wisdom text.
    
    Args:
        text: The text content to embed
    
    Returns:
        List of floats (vector embedding)
    """
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()
