# 07 — Automation without flattening voices

`polyphonic_wiki` can be automated, but the automation should not be blind.

The safe model is:

```text
automatic capture  →  conservative classification  →  high-confidence append
                                      └────────────→  review queue for ambiguous or sensitive items
```

The system should save more than it trusts. It can capture inputs automatically, but it should not silently turn every input into accepted knowledge.

---

## What gets automated

### 1. Capture

Any memo, AI dialogue, field note, or public source pointer can be saved into `inbox/`.

The automation adds frontmatter such as:

```yaml
date: 2026-05-18
title: AI agent governance memo
topic: ai-agent-governance
source_type: self_memo
status: pending
```

### 2. Conservative classification

The automation classifies entries into:

- `P1` for self-generated thoughts and decision reasons
- `P1.5` for AI-mediated hypotheses, objections, frames, analogies, and questions
- `P2` for field or relational voices
- `P3` for public anchors

Classification is based on explicit markers, source type, and simple cues.

Best practice: use explicit markers when writing quickly.

```markdown
[P1] I think the bottleneck is operational ownership.
[P1.5] The AI objected that auditability may create the market first.
[P2] Enterprise user reacted strongly to incident handoff.
[P3] Public policy material points to accountability requirements.
```

### 3. Safe fold into topic pages

High-confidence items are appended to `topics/<topic>.md` under the correct voice section.

Processed inbox items stay in `inbox/` with `status: processed` by default. If an individual entry needs review, a JSON review item is written to `events/queue/` and points back to the original inbox file through `source_file`. If `archive_processed_inputs` is enabled, processed inputs are moved to `archive/inputs/`.

### 4. Review queue

The automation sends an item to `events/queue/` when:

- the voice classification is low-confidence;
- no topic is specified;
- sensitive cues are detected;
- a `P2` item lacks `speaker_role`, `privacy`, or `consent` metadata.

The queue items are JSON files so they can be listed and approved mechanically.

---

## Commands

Initialize directories and config:

```bash
python tools/polyphonic_auto.py init --wiki .
```

Capture a self memo and process it immediately:

```bash
python tools/polyphonic_auto.py capture \
  --wiki . \
  --topic ai-agent-governance \
  --topic-type product_hypothesis \
  --source-type self_memo \
  --title "first hypothesis" \
  --text "The adoption blocker may be operational ownership, not model accuracy." \
  --process
```

Capture an AI-mediated item:

```bash
python tools/polyphonic_auto.py capture \
  --wiki . \
  --topic ai-agent-governance \
  --source-type ai_dialogue \
  --model example-model \
  --session 2026-05-18-agent-governance \
  --title "AI counter-frame" \
  --text "Auditability may become easier to buy before organizations redesign operational ownership." \
  --process
```

Capture a field reaction. Because this is `P2`, include role and privacy metadata:

```bash
python tools/polyphonic_auto.py capture \
  --wiki . \
  --topic ai-agent-governance \
  --source-type field_note \
  --speaker-role synthetic_enterprise_user \
  --privacy pseudonymized \
  --consent synthetic \
  --title "synthetic field reaction" \
  --text "The strongest reaction was uncertainty about who stops an agent when it behaves unexpectedly." \
  --process
```

Capture a public anchor. Keep it concise and refreshable:

```bash
python tools/polyphonic_auto.py capture \
  --wiki . \
  --topic ai-agent-governance \
  --source-type public_anchor \
  --anchor-strength synthetic \
  --url-or-ref synthetic-public-anchor \
  --refresh-after 2026-06-18 \
  --title "synthetic public anchor" \
  --text "A synthetic public governance source treats auditability and accountability as active requirements." \
  --process
```

Process all pending inbox files:

```bash
python tools/polyphonic_auto.py process --wiki . --lint
```

Watch the inbox while you work:

```bash
python tools/polyphonic_auto.py watch --wiki . --lint
```

List queued review items:

```bash
python tools/polyphonic_auto.py review --wiki .
```

Approve one queued item:

```bash
python tools/polyphonic_auto.py approve --wiki . --item <event-file>.json --topic ai-agent-governance --voice P2
```

Run structure checks and save `reports/last-lint-report.md`:

```bash
python tools/polyphonic_auto.py report --wiki .
```

You can also run the linter directly:

```bash
python tools/polyphonic_lint.py --wiki . --today 2026-05-18
```

---

## What happens when automation runs

Given this input:

```markdown
---
date: 2026-05-18
title: AI counter-frame
topic: ai-agent-governance
source_type: ai_dialogue
model: example-model
session: 2026-05-18-agent-governance
status: pending
---

Auditability may become easier to buy before organizations redesign operational ownership.
```

`polyphonic_auto.py process` appends this to `topics/ai-agent-governance.md`:

```markdown
- 2026-05-18: Auditability may become easier to buy before organizations redesign operational ownership. [voice_layer:P1.5 | evidence_state:interpreted | source_position:ai_dialogue | use_as:hypothesis | not_use_as:factual_evidence | model:example-model | session:2026-05-18-agent-governance | source_ref:inbox/... | retention_policy:distill | auto_saved:true]
```

Notice the safety tag:

```text
not_use_as:factual_evidence
```

Automation preserves the AI-mediated contribution, but it does not promote it into factual evidence.

---

## Safety defaults

The default config is intentionally conservative.

```json
{
  "auto_apply_min_confidence": 0.76,
  "review_unknown": true,
  "review_sensitive": true,
  "review_p2_missing_metadata": true,
  "default_refresh_days": 30,
  "archive_processed_inputs": true
}
```

You can make the system more aggressive by lowering `auto_apply_min_confidence` or disabling some review gates, but the recommended default is:

```text
save automatically, trust gradually
```

---

## Recommended operating modes

### Mode A — safe auto-save

Use `capture --process` for quick notes. High-confidence entries are appended; risky entries go to review.

### Mode B — inbox watcher

Run `watch` while writing into `inbox/`. This is useful when another app, editor, or shortcut writes files into the inbox.

### Mode C — review-first

Use `capture` without `--process`, then run `process` and review the queue at the end of the day.

### Mode D — LLM-assisted distillation

For long AI dialogues or long meetings, ask an LLM client to run the relevant `SKILL.md` first, then save the distilled output into `inbox/`. This keeps the automation from trying to classify raw transcripts blindly.
