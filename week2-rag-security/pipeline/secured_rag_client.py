"""
Secured RAG client — drop-in replacement for rag_client.py with all 3 defenses layered in.

Defense layers:
  D1 (ingestion time) — validate docs before add_documents() — enforced in vector_store wrapper below
  D2 (retrieval time) — sanitize retrieved chunks before LLM context assembly
  D3 (output time)   — validate LLM answer before returning to caller
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.vector_store import get_client, get_collection, query as vector_query
from pipeline.rag_client import build_context, GROQ_MODEL, SYSTEM_PROMPT
from importlib import import_module
_d2 = import_module("defenses.02_retrieval_sanitizer")
sanitize_retrieval_results = _d2.sanitize_retrieval_results
_d3 = import_module("defenses.03_output_validator")
validate_output = _d3.validate_output

load_dotenv()


def secured_ask(
    question: str,
    collection_name: str = "documents",
    n_results: int = 3,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Ask a question through the hardened RAG pipeline.
    D2 and D3 are applied automatically. D1 is enforced at ingestion time.
    """
    client = get_client(persist=True)
    collection = get_collection(client, name=collection_name)

    # Retrieve
    raw_retrieval = vector_query(collection, question, n_results=n_results)

    # D2: sanitize retrieved chunks before LLM sees them
    sanitized_retrieval, audit_log = sanitize_retrieval_results(raw_retrieval)

    if verbose and any(entry["removals"] for entry in audit_log):
        print(f"[D2] Retrieval sanitizer removed content from {sum(1 for e in audit_log if e['removals'])} chunk(s)")
        for entry in audit_log:
            if entry["removals"]:
                print(f"     chunk {entry['chunk_index']} ({entry['source']}): {entry['removals']}")

    context = build_context(sanitized_retrieval)

    if verbose:
        print(f"\n[D2] Sanitized context sent to LLM:\n{context}\n")

    # LLM call
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.0,
    )
    raw_answer = response.choices[0].message.content

    # D3: validate output before returning
    is_safe, final_answer, flags = validate_output(
        question, raw_answer, sanitized_retrieval["documents"][0]
    )

    if verbose and flags:
        print(f"[D3] Output validator BLOCKED response. Flags: {flags}")

    return {
        "question": question,
        "answer": final_answer,
        "is_safe": is_safe,
        "d2_audit": audit_log,
        "d3_flags": flags,
        "retrieved_sources": [m.get("source") for m in sanitized_retrieval["metadatas"][0]],
    }


if __name__ == "__main__":
    questions = [
        "What is the password rotation policy?",
        "Is MFA required for admin accounts?",
        "Can I use ChatGPT for internal data?",
    ]
    for q in questions:
        result = secured_ask(q, verbose=True)
        print(f"Q: {result['question']}")
        print(f"A: {result['answer']}")
        print(f"Safe: {result['is_safe']}\n")
