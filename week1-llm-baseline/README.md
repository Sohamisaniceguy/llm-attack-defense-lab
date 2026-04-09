# Week 1 — LLM Attack & Defense Lab

**Goal:** Build 5 prompt injection attack scenarios and 3 defense mechanisms against a Groq-backed LLM. Evaluate attack vs. defense effectiveness in a structured matrix.

## Structure

```
week1-llm-baseline/
├── attacks/          # 5 prompt injection attack scripts
├── defenses/         # 3 defense implementations
├── eval_matrix.md    # Attack vs defense scoring
└── THREAT-MODEL.md   # Threat model documentation
```

## Attacks

1. Direct injection
2. Indirect injection via retrieved context
3. Jailbreak via role-play
4. Multi-turn manipulation
5. Instruction override

## Defenses

1. Input sanitization + keyword blocklist
2. System prompt hardening with instruction anchoring
3. Output validation layer

## Model

`llama-3.3-70b-versatile` via Groq API
