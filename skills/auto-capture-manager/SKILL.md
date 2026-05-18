---
name: auto-capture-manager
description: Instructions for using polyphonic_wiki automation without flattening voice layers. Use this when the user wants automatic saving, inbox processing, review queue handling, or recurring management.
license: MIT
---

# auto-capture-manager

This skill manages automatic capture and conservative folding for `polyphonic_wiki`.

The core rule:

> Save automatically. Classify conservatively. Review anything ambiguous or sensitive.

Do not convert all inputs into accepted knowledge. Do not flatten P1, P1.5, P2, and P3 into one summary.

---

## 1. Operating model

Use the local tool:

```bash
python tools/polyphonic_auto.py <command> --wiki <wiki-root>
```

The tool can:

- initialize automation folders;
- capture text into `inbox/`;
- process pending inbox items;
- append high-confidence entries to topic pages;
- send ambiguous or sensitive items to `events/queue/`;
- list and approve queued review items;
- watch the inbox while the user works.

---

## 2. When processing a new input

Prefer explicit voice markers in user text:

```markdown
[P1] my stance or hypothesis
[P1.5] AI-mediated objection, frame, analogy, or question
[P2] field or relational voice
[P3] public anchor
```

If explicit markers are absent, infer from `source_type`:

| source_type | default voice |
|---|---|
| self_memo / decision_note | P1 |
| ai_dialogue | P1.5 |
| field_note / meeting_note / interview / reaction | P2 |
| public_anchor / public_source / article / paper | P3 |

If both markers and source_type are missing, do not confidently append. Send to review.

---

## 3. P1.5 safety

Every P1.5 entry must include:

```text
not_use_as:factual_evidence
```

Acceptable uses:

```text
hypothesis, counterargument, framing, analogy, question, synthesis, error_signal
```

Never treat AI-mediated output as public evidence.

---

## 4. P2 privacy

P2 entries require:

```text
speaker_role
privacy
consent
quote_policy
```

If any of `speaker_role`, `privacy`, or `consent` is absent, route the item to `events/queue/`.

Prefer paraphrase over raw quote unless explicit consent and context permit quoting.

---

## 5. P3 refresh

P3 entries require:

```text
refresh_after
anchor_strength
url_or_ref
```

Use `refresh_after` because public anchors can become stale.

---

## 6. Daily workflow

1. Capture notes into `inbox/`.
2. Run `process` or keep `watch` open during a writing session.
3. Check `events/queue/`.
4. Approve or rewrite queued items.
5. Run `polyphonic_lint.py`.
6. Add missing tensions or missing voices if needed.

---

## 7. Output discipline

When reporting what happened, summarize as:

```text
applied: <count>
queued: <count>
updated topics: <list>
review reasons: <short list>
```

Do not claim that an item is true just because it was saved.
