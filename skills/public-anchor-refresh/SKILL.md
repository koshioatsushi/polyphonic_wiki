---
name: public-anchor-refresh
description: Create or refresh P3 public anchors without turning the wiki into a public document warehouse.
license: MIT
---

# public-anchor-refresh

Use this skill for public information that anchors or challenges person-bound entries.

## Goal

Create small, refreshable `P3` anchors.

## Rules

- Store a concise claim summary, not a long copied text.
- Prefer official, academic, or otherwise inspectable sources.
- Add `refresh_after` for anything time-sensitive.
- Link P3 anchors to the P1/P1.5/P2 entries they check or challenge.

## Output format

```markdown
# Public anchor: <title>

## P3 entries
- YYYY-MM-DD: <concise public anchor summary>. [voice_layer:P3 | evidence_state:externally_anchored | source_position:public_anchor | anchor_strength:official | url_or_ref:<pointer> | refresh_after:YYYY-MM-DD | retention_policy:refresh]

## Supports
- <entry id or topic>

## Challenges
- <entry id or topic>

## Refresh note
- Re-check after: YYYY-MM-DD
```
