---
name: dialogue-distill
description: Distill an AI dialogue into reusable P1.5 entries while keeping AI-mediated output separate from factual evidence.
license: MIT
---

# dialogue-distill

Use this skill for AI conversation logs.

## Goal

Extract only the parts of an AI dialogue that are worth preserving as `P1.5` memory.

## Keep

- an objection that changed or sharpened the user's view,
- a taxonomy or frame the user may reuse,
- a question that exposed a blind spot,
- a synthesis that made voice tensions visible,
- an analogy that unlocks later explanation,
- an error pattern that reveals ambiguity.

## Drop

- generic advice,
- factual claims that should be checked elsewhere,
- long summaries of public information,
- polite filler,
- obvious restatements of the user's prompt.

## Required fields

Every output line must include:

```text
voice_layer:P1.5
source_position:ai_dialogue
use_as:hypothesis|counterargument|framing|analogy|question|synthesis|error_signal
not_use_as:factual_evidence
model:<model>
session:<session id or date>
```

## Output format

```markdown
# Dialogue distillation: <title>

## Context
- date:
- model:
- prompt_intent:
- source:

## P1.5 entries
- YYYY-MM-DD: <distilled entry>. [voice_layer:P1.5 | evidence_state:interpreted | source_position:ai_dialogue | use_as:counterargument | not_use_as:factual_evidence | model:<model> | session:<id>]

## Follow-up checks
- <What would need P2 or P3 support?>

## Tensions created
- <What existing P1/P2/P3 entry does this challenge?>
```
