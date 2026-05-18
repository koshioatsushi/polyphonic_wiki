---
name: polyphonic-answer
description: Answer questions against polyphonic_wiki without flattening P1/P1.5/P2/P3 voices into a single third-person summary.
license: MIT
---

# polyphonic-answer

Use this skill for querying the wiki.

## Required answer structure

```markdown
## P1 — current stance
<What the user's own entries say>

## P1.5 — AI-mediated contributions
<Frames, objections, questions, analogies. Do not use as factual evidence.>

## P2 — field / relational voices
<What surrounding people or field voices say, with role/context limits.>

## P3 — public anchors
<What public anchors say and whether they are fresh or stale.>

## Tensions
<Disagreements among voices.>

## Missing voices
<Which voice layer is absent or weak.>

## Provisional answer
<A useful answer that preserves uncertainty and voice provenance.>

## What would change this answer
<Concrete next observations or anchors.>
```

## Hard rules

- Never cite P1.5 as factual evidence.
- Never turn one P2 entry into “customers think X” unless the sample supports it.
- Do not hide stale P3 anchors.
- If a topic lacks P2, say so before giving field-sensitive advice.
- If a topic lacks P3, say so before making public-world claims.
