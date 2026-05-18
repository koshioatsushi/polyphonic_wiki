---
name: voice-capture
description: Classify a memo, meeting note, dialogue, or source pointer into P1/P1.5/P2/P3 voice entries for polyphonic_wiki.
license: MIT
---

# voice-capture

Use this skill when an input has not yet been separated by voice layer.

## Goal

Turn one input into a small set of reusable voice entries without flattening the voices into a single summary.

## Inputs

- A Markdown file in `inbox/`, or
- pasted notes, or
- a short public source pointer, or
- a mixed synthesis draft.

## Output targets

- `topics/<topic>.md` for topic-level entries
- `voices/p1-self/` for longer first-person source notes
- `voices/p15-ai/` for AI dialogue distillations
- `voices/p2-field/` for field notes
- `voices/p3-public/` for public anchor notes
- `tensions/` when voices disagree

## Classification rules

- User's own stance, doubt, hypothesis, decision reason → `P1`
- AI-mediated frame, objection, taxonomy, analogy, or question → `P1.5`
- Stakeholder, customer, collaborator, reader, local observation → `P2`
- Public paper, regulation, statistic, report, announcement → `P3`
- A mixed paragraph that already blends voices → split it, or mark `source_position:mixed` and send to review

## Required output format

```markdown
## Extracted voice entries

### P1
- YYYY-MM-DD: <entry>. [voice_layer:P1 | evidence_state:captured | source_position:self | sensitivity:private | retention_policy:keep]

### P1.5
- YYYY-MM-DD: <entry>. [voice_layer:P1.5 | evidence_state:interpreted | source_position:ai_dialogue | use_as:<type> | not_use_as:factual_evidence | model:<model> | session:<id>]

### P2
- YYYY-MM-DD: <entry>. [voice_layer:P2 | evidence_state:captured | source_position:field_reaction | speaker_role:<role> | privacy:pseudonymized | consent:implied | quote_policy:paraphrase]

### P3
- YYYY-MM-DD: <entry>. [voice_layer:P3 | evidence_state:externally_anchored | source_position:public_anchor | anchor_strength:<strength> | refresh_after:YYYY-MM-DD]
```

## Do not

- Do not convert AI dialogue into public evidence.
- Do not generalize one P2 reaction into a market claim.
- Do not paste long public texts.
- Do not remove tension to make the output smoother.
