"""Vector embedding generator for semantic search."""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def get_model():
    """Load embedding model (singleton)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def generate_embedding(text):
    """
    Generate vector embedding for text.
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats (384 dimensions)
    """
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def generate_batch_embeddings(texts, batch_size=32):
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts: List of texts
        batch_size: Batch size for processing
        
    Returns:
        List of embeddings
    """
    model = get_model()
    embeddings = model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
    return embeddings.tolist()
