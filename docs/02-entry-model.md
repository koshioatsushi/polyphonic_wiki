# 02 — Entry model

The unit of `polyphonic_wiki` is a **voice entry**.

A voice entry is a short reusable item with position metadata. It can live in a topic page, a dialogue file, a field note, a decision file, or a tension file.

## Minimal line format

```markdown
- YYYY-MM-DD: <entry text>. [voice_layer:P1 | evidence_state:captured | source_position:self | sensitivity:private]
```

## Metadata fields

| Field | Required | Meaning |
|---|---:|---|
| `voice_layer` | yes | `P1`, `P1.5`, `P2`, or `P3` |
| `evidence_state` | yes | lifecycle state of the entry |
| `source_position` | yes | more specific origin label |
| `sensitivity` | recommended | privacy level |
| `retention_policy` | recommended | how long and how directly to keep it |
| `source_quality` | optional | quality or inspectability of public/institutional sources |
| `entry_id` | recommended | stable reference for later decisions |

## Evidence states

| State | Meaning |
|---|---|
| `captured` | stored as originally observed, remembered, or paraphrased |
| `interpreted` | processed into a frame or hypothesis |
| `supported` | supported by another voice or later observation |
| `externally_anchored` | anchored to a public source |
| `contested` | actively challenged by another voice |
| `contradicted` | strong counter-evidence exists |
| `stale` | time-sensitive and likely out of date |
| `retired` | no longer used, but kept for traceability |

## Source positions

| Source position | Typical voice layer |
|---|---|
| `self` | P1 |
| `ai_dialogue` | P1.5 |
| `field_reaction` | P2 |
| `public_anchor` | P3 |
| `mixed` | any page-level synthesis that must be decomposed before reuse |

## Entry IDs

Recommended format:

```text
VYYYYMMDD-<topic>-<serial>
```

Example:

```text
V20260518-agent-governance-001
```

## Voice layer is not source quality

`voice_layer` describes position. It should not replace evidence checking, source quality, or source classification. A public anchor can be weak. A first-person memory can later be supported. A field reaction can be vivid but unrepresentative. Keep those distinctions visible.

## Line-level metadata beats section-level metadata

Topic pages may have sections for P1, P1.5, P2, and P3. Still, important entries should carry inline tags. LLMs and grep-like tools are more reliable when metadata travels with the line.
