# 05 — Absent voices

A voice-first wiki should not only preserve what exists. It should also show what is missing.

Absent voices matter because LLMs are good at producing fluent answers from incomplete memory. Fluency can hide a one-sided evidence base.

## Topic-type expectations

Different topic types need different voice coverage. The goal is not a fixed 25/25/25/25 balance. The goal is to detect whether the voices needed for this kind of topic are absent or weak.

| Topic type | Required voices | Recommended voices |
|---|---|---|
| `product_hypothesis` | P1, P2 | P1.5, P3 |
| `research_claim` | P1, P3 | P1.5, P2 |
| `decision_trace` | P1 | P1.5, P2, P3 |
| `field_pattern` | P2 | P1, P3 |
| `public_issue` | P3 | P1, P2 |
| `creative_work` | P1 | P1.5, P2 |
| `default` | P1 | P1.5, P2, P3 |

## Warning signs

- A topic has only P1 and P1.5 → possible self/AI echo loop.
- A topic has only P3 → it may be a research note, not situated memory.
- A topic has P2 but no role or privacy metadata → unsafe field capture.
- A topic has P1.5 with no `not_use_as:factual_evidence` → AI output may be misused.
- A synthesis exists without a `Missing voices` section → likely over-compression.

## Linting

Use:

```bash
python tools/polyphonic_lint.py --wiki . --today 2026-05-18
```

The linter is intentionally simple. It is not a judge of truth. It is a guardrail against voice erasure.
