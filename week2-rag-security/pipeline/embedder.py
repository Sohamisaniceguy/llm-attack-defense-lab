"""
Embedder — wraps sentence-transformers/all-MiniLM-L6-v2 (CPU-safe, local inference)
"""
from sentence_transformers import SentenceTransformer
from typing import List


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of strings. Returns list of float vectors."""
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]


if __name__ == "__main__":
    sample = ["This is a test sentence.", "Security is important."]
    vecs = embed_texts(sample)
    print(f"Embedded {len(vecs)} texts, dimension: {len(vecs[0])}")
