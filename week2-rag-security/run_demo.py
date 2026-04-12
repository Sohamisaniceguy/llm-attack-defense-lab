"""
run_demo.py — Index policy documents and run 5 demo questions against the RAG pipeline.

Usage:
    python3 run_demo.py              # Index docs + run questions
    python3 run_demo.py --reset      # Wipe vector store and re-index
"""
import argparse
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pipeline.vector_store import get_client, get_collection, add_documents
from pipeline.rag_client import ask

console = Console()

DOCS_DIR = Path("data/docs")
EVIDENCE_DIR = Path("evidence")

DEMO_QUESTIONS = [
    "What is the password rotation policy?",
    "Is SMS-based MFA allowed for admin accounts?",
    "What should I do if I detect a P1 security incident?",
    "Can I use ChatGPT for work tasks involving internal data?",
    "What are the requirements for SageMaker notebook security?",
]


def load_and_chunk_docs(docs_dir: Path) -> tuple[list[str], list[dict], list[str]]:
    """Load .txt files, split into paragraph chunks, return (texts, metadatas, ids)."""
    texts, metadatas, ids = [], [], []
    doc_id = 0
    for txt_file in sorted(docs_dir.glob("*.txt")):
        content = txt_file.read_text()
        # Split on double newline — each section becomes a chunk
        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({
                "source": txt_file.name,
                "trust": "high",
                "ingested_at": datetime.now(timezone.utc).isoformat(),
            })
            ids.append(f"doc_{doc_id}")
            doc_id += 1
    return texts, metadatas, ids


def index_documents(reset: bool = False) -> int:
    client = get_client(persist=True)
    collection = get_collection(client, name="documents", reset=reset)

    # Skip re-indexing if already populated
    if not reset and collection.count() > 0:
        console.print(f"[yellow]Vector store already has {collection.count()} chunks — skipping indexing. Use --reset to re-index.[/yellow]")
        return collection.count()

    texts, metadatas, ids = load_and_chunk_docs(DOCS_DIR)
    console.print(f"[cyan]Indexing {len(texts)} chunks from {DOCS_DIR}...[/cyan]")
    add_documents(collection, texts, metadatas, ids)
    console.print(f"[green]Indexed {len(texts)} chunks into ChromaDB.[/green]")
    return len(texts)


def run_questions() -> list[dict]:
    results = []
    table = Table(title="RAG Demo — Policy Q&A", show_lines=True)
    table.add_column("Question", style="bold", max_width=40)
    table.add_column("Answer", max_width=60)
    table.add_column("Sources", style="dim", max_width=30)

    for question in DEMO_QUESTIONS:
        result = ask(question, verbose=False)
        results.append(result)
        sources = ", ".join(set(result["retrieved_sources"]))
        table.add_row(question, result["answer"][:300], sources)

    console.print(table)
    return results


def save_evidence(results: list[dict]) -> None:
    EVIDENCE_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = EVIDENCE_DIR / f"demo_run_{timestamp}.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    console.print(f"\n[green]Evidence saved to {output_path}[/green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG demo — index docs and run questions")
    parser.add_argument("--reset", action="store_true", help="Wipe and re-index the vector store")
    args = parser.parse_args()

    console.print(Panel("[bold blue]Week 2 — Secure RAG Application Demo[/bold blue]"))

    n_chunks = index_documents(reset=args.reset)
    console.print(f"\n[bold]Running {len(DEMO_QUESTIONS)} questions against {n_chunks} indexed chunks...[/bold]\n")

    results = run_questions()
    save_evidence(results)
