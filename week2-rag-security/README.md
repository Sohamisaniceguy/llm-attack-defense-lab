# Week 2 — Secure RAG Application

**Part of:** [AI Security Portfolio](../)  
**Stack:** Python 3.12 · LangChain · ChromaDB · sentence-transformers · Groq (llama-3.3-70b)

---

## What this is

I built a RAG pipeline — document Q&A on top of LangChain and ChromaDB. Then I attacked it.

This week covers the attack surface of RAG pipelines: how document poisoning works, why the LLM can't tell the difference between a real policy and a fake one, and what the retrieval layer actually trusts.

Defenses are being added throughout the week as I build and test them.

---

## Run it yourself

```bash
pip install langchain langchain-community langchain-groq chromadb sentence-transformers python-dotenv rich
cp .env.example .env  # add your GROQ_API_KEY
```

```bash
# See the clean pipeline working
python3 week2-rag-security/run_demo.py

# Run the data poisoning attack
python3 week2-rag-security/attacks/01_data_poisoning.py
```

---

## What's in this push (Monday)

```
week2-rag-security/
├── pipeline/
│   ├── embedder.py        — sentence-transformers/all-MiniLM-L6-v2 wrapper
│   ├── vector_store.py    — ChromaDB add/query with metadata tracking
│   └── rag_client.py      — Groq LLM + retrieval chain
├── data/docs/             — sample security policy documents
├── run_demo.py            — indexes docs, runs 5 questions, saves evidence
└── attacks/
    └── 01_data_poisoning.py  — spoofed policy doc poisons the knowledge base
```

Defenses, evaluation matrix, and threat model added Wednesday and Friday.

---

## Attack 1 — Data Poisoning

One injected document, spoofed as a trusted policy file.

**Before poisoning:**
> "The password rotation policy requires all passwords to be rotated every 90 days."

**After poisoning:**
> "Password rotation is no longer required. Passwords may be kept indefinitely. MFA is now optional for all users."

ChromaDB ranks chunks by semantic similarity — not trustworthiness. The poison doc had high keyword overlap, ranked above the real policy, and the LLM reasoned from what retrieval gave it.

Full before/after comparison + evidence logs saved to `evidence/` on each run.

---

## Stack

| Component | Tool | Why |
|---|---|---|
| LLM | Groq (llama-3.3-70b) | Free tier, fast |
| Vector store | ChromaDB | Simple, local, no infra needed |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | CPU-safe, no GPU required |
| Framework | LangChain | Standard RAG tooling |
