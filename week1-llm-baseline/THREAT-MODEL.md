# Threat Model — Week 1: LLM Attack & Defense Lab

## Assets at Risk

- LLM inference endpoint (Groq API)
- System prompt / application instructions
- User data passed to the model

## Attack Surface

- User input field (direct injection)
- Retrieved context from external sources (indirect injection)
- Conversational history (multi-turn attacks)

## Threat Actors

- Malicious end users attempting to bypass application controls
- Automated adversarial inputs from upstream systems

## Attack Vectors

| Vector | Description | Severity |
|--------|-------------|----------|
| Direct prompt injection | User overrides system prompt via crafted input | High |
| Indirect injection | Malicious content in retrieved context manipulates LLM | High |
| Jailbreak via role-play | Role assignment bypasses safety instructions | Medium |
| Multi-turn manipulation | Gradual conversation steering over multiple turns | Medium |
| Instruction override | Explicit commands to ignore prior instructions | High |

## Mitigations Implemented

- [x] Input sanitization + keyword blocklist
- [x] System prompt hardening with instruction anchoring
- [x] Output validation layer

## Residual Risk

**After all three defenses layered (tested April 2026 against llama-3.3-70b via Groq):**

- Base64 encoded payloads slipped through input sanitization when the decoded text appeared benign. Obfuscation via novel encodings or natural-sounding override phrases remains a gap in D1.
- System prompt hardening is model-dependent and probabilistic. A different model or rephrased attack may succeed where this one failed.
- Output validation only catches attacks that leave a detectable signal in the response. Subtle information leakage (partial system prompt, indirect confirmation) may not match any pattern.
- Multi-turn manipulation relies entirely on D2. No pre- or post-generation layer catches gradual conversation steering — each individual turn looks benign.
- Semantic attacks (no injection keywords, pure social engineering phrasing) can bypass D1 entirely and may bypass D2 depending on model.

**Unmitigated vectors:**
- Novel encoding schemes not in the blocklist
- Adversarial prompts crafted specifically against this system prompt
- Attacks arriving via RAG-retrieved context at scale (covered in Week 2)
