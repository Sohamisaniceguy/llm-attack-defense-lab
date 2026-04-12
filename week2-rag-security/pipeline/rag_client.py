"""
RAG client — ties together ChromaDB retrieval + Groq LLM to answer questions.
Retrieves top-3 chunks, builds context, sends to LLM.
"""
import os
from dotenv import load_dotenv
from groq import Groq
from typing import Dict, Any
from pipeline.vector_store import get_client, get_collection, query as vector_query

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a security policy assistant. Answer questions using ONLY the context provided below.
If the context does not contain the answer, say "I don't have that information in my knowledge base."
Do not use any prior knowledge. Cite which document your answer comes from."""


def build_context(retrieval_results: Dict[str, Any]) -> str:
    docs = retrieval_results["documents"][0]
    metas = retrieval_results["metadatas"][0]
    context_parts = []
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        source = meta.get("source", "unknown")
        context_parts.append(f"[{i+1}] Source: {source}\n{doc}")
    return "\n\n".join(context_parts)


def ask(
    question: str,
    collection_name: str = "documents",
    n_results: int = 3,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Ask a question against the RAG pipeline.
    Returns: answer, retrieved_docs, context used.
    """
    client = get_client(persist=True)
    collection = get_collection(client, name=collection_name)

    retrieval = vector_query(collection, question, n_results=n_results)
    context = build_context(retrieval)

    if verbose:
        print(f"\n[RETRIEVAL] Top {n_results} chunks:\n{context}\n")

    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.0,
    )

    answer = response.choices[0].message.content
    return {
        "question": question,
        "answer": answer,
        "retrieved_docs": retrieval["documents"][0],
        "retrieved_sources": [m.get("source") for m in retrieval["metadatas"][0]],
        "context": context,
    }


if __name__ == "__main__":
    result = ask("What is the password rotation policy?", verbose=True)
    print(f"\nQ: {result['question']}")
    print(f"A: {result['answer']}")
