# 06 — Privacy and consent

`polyphonic_wiki` stores person-bound context. That makes privacy design central, not optional.

## Default posture

- Prefer role labels over real names.
- Prefer paraphrase over exact quotation.
- Prefer local/private storage over public publication.
- Keep sensitive details out of topic pages.
- Separate raw source files from distilled voice entries when needed.

## P2 safety fields

Every P2 entry should include:

```text
speaker_role:<role>
privacy:public|pseudonymized|internal|confidential
consent:explicit|implied|unknown
quote_policy:quote|paraphrase|summarize_only
```

## Redaction checklist

Before storing a P2 entry, remove or generalize:

- full names unless public and necessary,
- contact information,
- exact company details if confidential,
- contract amounts,
- employment or compensation details,
- health, legal, or family details unless essential and safe,
- raw transcripts when a distilled paraphrase is enough.

## When not to store

Do not store a field voice when:

- the person would reasonably expect the context to disappear,
- the entry would expose them without clear value,
- the same insight can be preserved as a safer role-level paraphrase,
- the consent status is unknown and the content is sensitive.
