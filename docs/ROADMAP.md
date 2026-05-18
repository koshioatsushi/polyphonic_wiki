# Roadmap

## v0.1 — Local Markdown protocol

- Four voice layers: P1, P1.5, P2, P3
- Inline voice metadata
- Markdown templates for topics, dialogues, field notes, public anchors, decisions, tensions, and weekly reviews
- Local capture CLI: `tools/polyphonic_auto.py`
- Local structural linter: `tools/polyphonic_lint.py`
- Review queue for ambiguous or sensitive entries
- Synthetic examples only

## v0.2 — LLM client workflows

- Stronger `SKILL.md` workflows for voice capture, dialogue distillation, field-note extraction, and polyphonic answering
- Prompt-intent tracking for P1.5 entries
- Better distinction between actual P2 and imagined P2
- Review-first workflows for sensitive teams

## v0.3 — Export adapters

- JSONL export with voice metadata
- Graph-ready export for systems that use nodes, relations, and provenance
- Agent-memory export profiles
- LlamaIndex / LangGraph-style metadata adapters
- Obsidian / Logseq-compatible vault layouts

## v0.4 — Privacy hardening

- P2 redaction helper
- Confidentiality linting
- Safer public-export profile
- Consent-state review reports

## v0.5 — Evaluation

- Decision traceability metric
- P1.5 usefulness review
- P2 recovery metric
- Missing-voice detection quality
- Voice-flattening benchmark
