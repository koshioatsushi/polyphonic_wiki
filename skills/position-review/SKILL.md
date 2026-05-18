---
name: position-review
description: Review a claim from multiple voice positions and preserve disagreements as tensions.
license: MIT
---

# position-review

Use this skill when a topic or decision is becoming too smooth.

## Goal

Generate a structured review from four positions.

## Output format

```markdown
# Position review: <claim>

## Target claim
<Claim under review>

## P1 review — self-critical
- What assumption am I making?
- What would embarrass this claim later?

## P1.5 review — AI-mediated objection
- What counter-frame did AI generate?
- Is it a thinking aid or a factual claim?

## P2 review — field objection
- What would a stakeholder, customer, reader, or collaborator object to?
- Is there actual P2 material or only imagined P2?

## P3 review — public anchor objection
- What public source could support or challenge this?
- Is the anchor fresh?

## Decision
- Keep / revise / contest / retire

## New tensions
- <Tension entries to create or update>
```

## Important distinction

An imagined P2 objection is not P2. It is P1.5 or P1 until a real field voice exists.
