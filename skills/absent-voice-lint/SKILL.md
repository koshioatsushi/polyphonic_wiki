---
name: absent-voice-lint
description: Inspect topic pages for missing voice layers, unsafe P1.5 usage, missing P2 privacy metadata, stale P3 anchors, and over-compressed syntheses.
license: MIT
---

# absent-voice-lint

Use this skill manually or via `tools/polyphonic_lint.py`.

## Checks

- Required voice layers are present for the topic type.
- Recommended voice layers are reported when missing.
- P1.5 lines include `not_use_as:factual_evidence`.
- P2 lines include `speaker_role`, `privacy`, and `consent`.
- P3 lines include `refresh_after` and stale anchors are flagged.
- Pages with multiple voices include `Tensions`.
- Pages with synthesis include `Missing voices`.

## Human review

The linter does not decide truth. It flags structural risk:

- self/AI echo loops,
- field voices without privacy metadata,
- public anchors that have gone stale,
- smooth answers built from missing voices.
