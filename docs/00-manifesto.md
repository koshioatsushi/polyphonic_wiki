# 00 — Manifesto

`polyphonic_wiki` starts from a simple claim:

> LLM-era memory should preserve voices before it compresses them into conclusions.

A normal knowledge base often moves toward a clean third-person summary. That can be useful when the question is settled. It can be harmful when the value lies in how different positions were formed.

A founder's doubt, a field user's discomfort, an AI-mediated counter-frame, and a public report should not be merged into one flat paragraph. They come from different positions. They have different failure modes. They should change decisions in different ways.

## What is new here

`polyphonic_wiki` does not try to replace evidence checking, source quality, or primary / secondary / tertiary source classification. It adds another first-class metadata layer:

```text
voice provenance: whose position did this memory come from?
```

This is especially important for LLM workflows because fluent summaries can hide whether a statement came from the user's own hypothesis, an AI dialogue, a field reaction, or a public anchor.

## Design goals

1. **Make position visible** — Every reusable entry carries a voice layer.
2. **Separate voice from certainty** — `P1`, `P1.5`, `P2`, and `P3` are not truth levels.
3. **Preserve productive disagreement** — Tensions are first-class objects, not noise.
4. **Protect person-bound context** — The most valuable information is often the least recoverable from public search.
5. **Prevent AI flattening** — LLM answers should name whose voice says what, not hide provenance behind smooth prose.
6. **Keep public anchors refreshable** — Public information is not discarded; it is stored as concise, checkable, refreshable context.

## The anti-goal

The anti-goal is a beautiful summary that erases the path that produced it.

A bad answer says:

> The market appears to care about governance and auditability.

A better answer says:

> P1 currently frames the issue as operational ownership. P1.5 raised auditability as an alternative market-forming frame. P2 reactions currently support ownership more strongly than accuracy, but the field sample is thin. P3 anchors show that audit and accountability requirements are still shifting. The missing voice is a compliance buyer who has actually rejected or approved such tooling.

The second answer is less elegant, but it is more useful for future decisions.
