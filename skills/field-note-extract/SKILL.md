---
name: field-note-extract
description: Extract P2 field voices from meetings, interviews, comments, reactions, or local observations with privacy metadata.
license: MIT
---

# field-note-extract

Use this skill when the input contains another person's reaction or a field observation.

## Goal

Capture `P2` without overexposing people and without turning a single reaction into a general claim.

## Extraction rules

- Preserve the role and situation.
- Prefer paraphrase over direct quote unless exact wording matters.
- Keep sample limits visible.
- Add consent and privacy metadata.
- Separate observation from interpretation.

## Required fields

```text
voice_layer:P2
source_position:field_reaction
speaker_role:<role>
privacy:public|pseudonymized|internal|confidential
consent:explicit|implied|unknown
quote_policy:quote|paraphrase|summarize_only
```

## Output format

```markdown
# Field note extraction: <title>

## P2 entries
- YYYY-MM-DD: <role-level paraphrase>. [voice_layer:P2 | evidence_state:captured | source_position:field_reaction | speaker_role:<role> | privacy:pseudonymized | consent:implied | quote_policy:paraphrase | sensitivity:private]

## What this does not prove
- <Limits of generalization>

## Candidate tensions
- <Which P1/P1.5/P3 entries does this support or challenge?>
```

## Redaction checklist

Remove direct identifiers, contact information, contract values, employment details, health/legal/family details, and raw transcript fragments unless they are essential and safe.
