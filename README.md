# polyphonic_wiki

> A local-first Markdown protocol and CLI for preserving **voice provenance** in LLM-era memory.

Most AI memory tools ask:

> What should the model remember?

`polyphonic_wiki` asks:

> Whose voice is this memory — mine, AI-mediated, field reaction, or public anchor?

It is not another RAG system, vector database, hosted memory service, or autonomous agent framework. It is a **voice-provenance layer before retrieval**: a way to keep first-person, AI-mediated, field, and public voices from being flattened into one smooth summary before they are retrieved, graphed, summarized, exported, or acted upon.

---

## Why this exists

LLMs are good at turning messy notes into fluent third-person summaries. That is useful when the question is already settled. It is risky when the value lies in the difference between positions.

A founder's doubt, an AI-generated counter-frame, a field user's reaction, and a public report should not be merged into one authoritative-looking paragraph. They come from different positions, have different failure modes, and should change decisions in different ways.

`polyphonic_wiki` preserves those positions in Markdown so that humans and LLMs can later ask:

- What did I think at the time?
- What emerged through AI dialogue?
- What did people around the work actually react to?
- What public anchors supported, challenged, or contextualized those voices?
- Which voice is still missing?

---

## The four voice layers

| Layer | Name | What it stores | How an LLM should use it |
|---|---|---|---|
| `P1` | first-person | My own thoughts, doubts, hypotheses, decisions, reasons | Treat as stance or self-context, not as external evidence |
| `P1.5` | AI-mediated | Hypotheses, objections, frames, analogies, and questions generated through dialogue with AI | Treat as dialogue output; useful for thinking, unsafe as factual evidence |
| `P2` | field / relational voices | Reactions from customers, collaborators, readers, stakeholders, interviewees, or people around the work | Preserve role and situation; do not average too quickly |
| `P3` | public anchors | Papers, reports, regulations, statistics, public statements, public claims | Use as refreshable external anchors; do not let them erase situated context |

The voice layer is **not** a truth score. `P1`, `P1.5`, `P2`, and `P3` describe where a memory came from. They do not decide whether it is true.

This matters because evidence state and voice position are different questions:

```text
voice_layer:    Whose position did this memory come from?
evidence_state: How is this memory currently supported, contested, stale, or retired?
```

A `P1` hypothesis can later become supported. A `P3` anchor can become stale. A vivid `P2` reaction may be important but unrepresentative. A `P1.5` objection can be useful while still requiring external checking.

---

## Quickstart

Clone the repository, then run the local tools. The tools use only local files and do not call an LLM or web service by default.

```bash
git clone https://github.com/<your-name>/polyphonic_wiki.git
cd polyphonic_wiki

python tools/polyphonic_auto.py init --wiki .

python tools/polyphonic_auto.py capture \
  --wiki . \
  --topic ai-agent-governance \
  --topic-type product_hypothesis \
  --source-type self_memo \
  --title "first hypothesis" \
  --text "The adoption blocker may be operational ownership, not model accuracy." \
  --process

python tools/polyphonic_auto.py capture \
  --wiki . \
  --topic ai-agent-governance \
  --source-type ai_dialogue \
  --model example-model \
  --session 2026-05-18-agent-governance \
  --title "AI counter-frame" \
  --text "Auditability may become easier to buy before organizations redesign operational ownership." \
  --process

python tools/polyphonic_auto.py capture \
  --wiki . \
  --topic ai-agent-governance \
  --source-type field_note \
  --speaker-role synthetic_enterprise_user \
  --privacy pseudonymized \
  --consent synthetic \
  --title "synthetic field reaction" \
  --text "A synthetic enterprise user reacted most strongly to uncertainty about who stops an agent when it behaves unexpectedly." \
  --process

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

python tools/polyphonic_lint.py --wiki .
```

The first capture creates or updates a topic page and appends a `P1` entry:

```markdown
## P1 — first-person

- 2026-05-18: The adoption blocker may be operational ownership, not model accuracy. [voice_layer:P1 | evidence_state:captured | source_position:self | sensitivity:private | retention_policy:keep]
```

The AI-mediated capture becomes `P1.5`, with an explicit safety tag:

```markdown
## P1.5 — AI-mediated

- 2026-05-18: Auditability may become easier to buy before organizations redesign operational ownership. [voice_layer:P1.5 | evidence_state:interpreted | source_position:ai_dialogue | use_as:counterargument | not_use_as:factual_evidence | model:example-model | session:2026-05-18-agent-governance]
```

The field capture becomes `P2`, with privacy metadata:

```markdown
## P2 — field / relational voices

- 2026-05-18: A synthetic enterprise user reacted most strongly to uncertainty about who stops an agent when it behaves unexpectedly. [voice_layer:P2 | evidence_state:captured | source_position:field_reaction | speaker_role:synthetic_enterprise_user | privacy:pseudonymized | consent:synthetic | quote_policy:paraphrase]
```

The public-anchor capture becomes `P3`, with refresh metadata:

```markdown
## P3 — public anchors

- 2026-05-18: A synthetic public governance source treats auditability and accountability as active requirements. [voice_layer:P3 | evidence_state:externally_anchored | source_position:public_anchor | anchor_strength:synthetic | url_or_ref:synthetic-public-anchor | refresh_after:2026-06-18 | retention_policy:refresh]
```

For topic types such as `product_hypothesis`, the linter expects field material (`P2`). If you only capture P1 and P1.5, the linter will correctly report a missing field voice.

The key point is not the CLI itself. The key point is that the memory now carries voice metadata before any LLM retrieves or summarizes it.

---

## What automation does

`polyphonic_wiki` includes a local automation manager:

```text
automatic capture  →  conservative classification  →  high-confidence append
                                      └────────────→  review queue for ambiguous or sensitive items
```

Use it to:

```bash
python tools/polyphonic_auto.py init --wiki .
python tools/polyphonic_auto.py capture --wiki . --topic <topic> --source-type <type> --text "..." --process
python tools/polyphonic_auto.py process --wiki . --lint
python tools/polyphonic_auto.py review --wiki .
python tools/polyphonic_auto.py approve --wiki . --item <event-file>.json --topic <topic> --voice P2
python tools/polyphonic_auto.py status --wiki .
```

The automation can:

- create timestamped inbox files;
- classify entries into `P1`, `P1.5`, `P2`, or `P3`;
- create topic pages when needed;
- append high-confidence entries to the right voice section;
- force `P1.5` entries to carry `not_use_as:factual_evidence`;
- route low-confidence or sensitive entries to `events/queue/`;
- write an append-only log to `logs/auto-log.md`;
- save structural lint output to `reports/last-lint-report.md`;
- leave source records traceable through `source_ref`.

The default policy is intentionally conservative:

```text
save automatically, trust gradually
```

See [`docs/07-automation.md`](docs/07-automation.md) for details.

---

## Structural linting

Run:

```bash
python tools/polyphonic_lint.py --wiki . --today 2026-05-18
```

The linter does not decide truth. It flags structural risks:

- a topic type is missing a required voice layer;
- `P1.5` lacks `not_use_as:factual_evidence`;
- `P2` lacks `speaker_role`, `privacy`, or `consent`;
- `P3` lacks `refresh_after` or has become stale;
- a multi-voice page lacks a `Tensions` section;
- a page has a synthesis but no `Missing voices` section.

This is why the linter is named around **absent voices**, not balance. Different topic types need different voice coverage. A product hypothesis usually needs field reaction. A research claim usually needs public anchoring. A creative work may legitimately be P1-heavy.

---

## How this differs from existing LLM memory tools

`polyphonic_wiki` is designed to work before or alongside retrieval, graph, agent-memory, research-assistant, or PKM tools.

| Tool family | Primary question | What `polyphonic_wiki` adds |
|---|---|---|
| RAG | What should be retrieved? | Whose voice is the retrieved memory? |
| GraphRAG | How are entities and relations connected? | Which voice produced, supports, or contests each relation? |
| Agent memory | What should the agent remember and reuse? | What must not be collapsed into a generic memory? |
| Research assistants | What do these sources say? | Which parts are mine, AI-mediated, field reactions, or public anchors? |
| PKM tools | How do I organize my notes? | How can an LLM read them without flattening voice differences? |

This is not a claim that public information is unimportant or that LLMs can regenerate facts reliably. Public information still needs checking, attribution, and refresh. `polyphonic_wiki` simply treats `P3` as a **public anchor** rather than making public-source warehousing the center of the wiki.

---

## Not a replacement for primary / secondary / tertiary source classification

Traditional source classifications help describe how close a source is to an event, object, or analysis. They are still useful.

`polyphonic_wiki` adds a different axis:

```text
source classification: how the source relates to the event or claim
voice provenance:      whose position the memory came from
```

The two axes should complement each other. Voice provenance should sit alongside evidence state, source quality, and verification practices — not replace them.

---

## Repository layout

```text
polyphonic_wiki/
├── README.md
├── PRIVACY.md
├── docs/
├── schemas/
├── skills/
├── templates/
├── tools/
│   ├── polyphonic_auto.py
│   └── polyphonic_lint.py
├── examples/              # synthetic examples only
├── tests/
├── config/
├── inbox/                 # private runtime data; ignored except .gitkeep
├── topics/                # private runtime data; ignored except .gitkeep
├── voices/                # private runtime data; ignored except .gitkeep
├── events/                # private runtime data; ignored except .gitkeep
├── logs/                  # private runtime data; ignored except .gitkeep
├── reports/               # private runtime data; ignored except .gitkeep
└── archive/               # private runtime data; ignored except .gitkeep
```

The public repository should contain schemas, templates, tools, skills, docs, and synthetic examples. Your real wiki data should usually live in a private repository or local directory.

---

## Privacy model

`P2` entries are powerful because they preserve field and relational voices. They are also the highest privacy risk.

Default rules:

- use role labels instead of real names;
- prefer paraphrase over direct quotation;
- keep raw transcripts out of topic pages by default;
- mark `speaker_role`, `privacy`, `consent`, and `sensitivity`;
- keep your actual wiki private unless you have a reason to publish it;
- keep public examples synthetic.

See [`PRIVACY.md`](PRIVACY.md) and [`docs/06-privacy-and-consent.md`](docs/06-privacy-and-consent.md).

---

## LLM client skills

The `skills/` directory contains instruction files that can be loaded by LLM clients such as Claude Code, Codex CLI, Cursor, or other local workflows:

- `voice-capture` — split a mixed input into voice entries;
- `dialogue-distill` — turn an AI conversation into reusable `P1.5` entries;
- `field-note-extract` — extract safer `P2` entries with privacy metadata;
- `public-anchor-refresh` — create small, refreshable `P3` anchors;
- `polyphonic-answer` — answer without flattening voices;
- `position-review` — review a claim from multiple voice positions;
- `absent-voice-lint` — inspect pages for missing voices and unsafe metadata;
- `auto-capture-manager` — use automation without blind trust.

---

## Non-goals

`polyphonic_wiki` is not:

- a vector database;
- a hosted AI memory service;
- a web crawler;
- a replacement for RAG;
- a replacement for NotebookLM-like tools;
- an autonomous agent framework;
- a source of factual verification by itself.

It is a local-first structure for preserving voice provenance before memories are retrieved, summarized, graphed, exported, or acted upon.

---

## The central rule

Do not ask the wiki only:

> What is true?

Ask:

> Whose voice supports this, whose voice contests it, and which voice is missing?

