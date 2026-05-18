# 03 — Ingest workflow

The ingest workflow is designed to protect voices from being merged too early.

## Step 1 — identify input type

Common input types:

- personal memo,
- AI dialogue,
- meeting note,
- field note,
- public source pointer,
- decision note,
- synthesis draft.

## Step 2 — split by voice layer

Do not summarize the whole input first. Split it into voice candidates first.

Questions:

- Is this my own stance or interpretation? → `P1`
- Did this emerge from an AI dialogue? → `P1.5`
- Did this come from another person in relation to me or the project? → `P2`
- Is this a public anchor? → `P3`
- Is it already a synthesis of multiple voices? → decompose it or mark `source_position:mixed`

## Step 3 — discard low-value public filler

The wiki is not a warehouse for public content. For P3, keep a small anchor entry with a pointer and a refresh date.

## Step 4 — preserve exactness where it matters

For P2, decide whether to quote, paraphrase, or summarize. Default to paraphrase unless the exact words are essential and safe to keep.

## Step 5 — fold into topic, decision, or tension

Use:

- `topics/` for continuing domains,
- `decisions/` for decisions and decision traces,
- `tensions/` for unresolved disagreement,
- `voices/` for longer voice-specific source files.

## Step 6 — record missing voices

When a topic only contains P1 and P1.5, name the missing P2/P3 explicitly. When a topic only contains P3, name the missing P1/P2 relevance explicitly.
