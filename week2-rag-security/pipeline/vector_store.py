"""
Vector store — ChromaDB wrapper with document metadata tracking.
Metadata is used by defenses later (provenance, trust score).
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from pipeline.embedder import embed_texts, embed_query


DB_PATH = "evidence/chroma_db"


def get_client(persist: bool = True) -> chromadb.Client:
    if persist:
        return chromadb.PersistentClient(path=DB_PATH)
    return chromadb.EphemeralClient()


def get_collection(
    client: chromadb.Client,
    name: str = "documents",
    reset: bool = False,
) -> chromadb.Collection:
    if reset:
        try:
            client.delete_collection(name)
        except Exception:
            pass
    return client.get_or_create_collection(name)


def add_documents(
    collection: chromadb.Collection,
    docs: List[str],
    metadatas: List[Dict[str, Any]],
    ids: List[str],
) -> None:
    """Embed and add documents to the collection."""
    embeddings = embed_texts(docs)
    collection.add(
        documents=docs,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )


def query(
    collection: chromadb.Collection,
    query_text: str,
    n_results: int = 3,
) -> Dict[str, Any]:
    """Retrieve top-n most similar documents."""
    query_vec = embed_query(query_text)
    results = collection.query(
        query_embeddings=[query_vec],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    return results


if __name__ == "__main__":
    client = get_client(persist=False)
    col = get_collection(client, reset=True)
    add_documents(
        col,
        docs=["Passwords must be rotated every 90 days.", "MFA is required for all admin accounts."],
        metadatas=[{"source": "policy.txt", "trust": "high"}, {"source": "policy.txt", "trust": "high"}],
        ids=["doc1", "doc2"],
    )
    results = query(col, "What is the password policy?")
    print(results["documents"][0])
