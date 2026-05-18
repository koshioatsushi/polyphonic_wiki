# 08 — Positioning among LLM memory tools

`polyphonic_wiki` is not a replacement for RAG, GraphRAG, agent memory systems, NotebookLM-like research tools, or PKM apps.

It asks a prior question:

> Whose voice is this memory, and what must not be flattened?

## Complementary role

| Tool family | Primary question | What `polyphonic_wiki` adds |
|---|---|---|
| RAG | What should be retrieved? | Whose voice is the retrieved memory? |
| GraphRAG | How are entities and relations connected? | Which voice produced, supports, or contests each relation? |
| Agent memory | What should the agent remember and reuse? | What must not be collapsed into a generic memory? |
| Research assistants | What do these sources say? | Which parts are mine, AI-mediated, field reactions, or public anchors? |
| PKM tools | How do I organize notes? | How can an LLM read them without flattening voice differences? |

The intended role is a local-first voice-provenance layer before memories are retrieved, summarized, graphed, exported, or acted upon.

## What this does not claim

`polyphonic_wiki` does not claim that public information is unimportant, that public facts can be regenerated reliably by an LLM, or that source verification can be skipped.

Instead, it uses `P3` as a public anchor:

- store concise summaries and pointers rather than long public texts;
- add `refresh_after` for time-sensitive information;
- use public anchors to support, contest, or contextualize P1 / P1.5 / P2 entries;
- re-check public anchors before relying on them for decisions.

## Relationship to source classification

Primary / secondary / tertiary source classification describes how a source relates to an event, object, or analysis. Voice provenance describes whose position the memory came from.

These axes should be used together:

```text
source classification: closeness or relation to the event / claim
voice provenance:      first-person, AI-mediated, field, or public position
evidence state:        captured, interpreted, supported, anchored, contested, stale, retired
```

## Safe novelty claim

Many existing tools focus on memory storage, retrieval, linking, context management, or agent reuse. `polyphonic_wiki` focuses on what should not be flattened before those systems operate: the voice position of each memory.

The project's practical contribution is not a claim of being the first memory system. It is a Markdown-native governance layer for preserving P1 / P1.5 / P2 / P3 voice provenance in local-first knowledge work.
