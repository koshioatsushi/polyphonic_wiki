# 01 — Voice layers

Voice layers describe where an entry came from. They do not describe whether it is true.

## P1 — first-person

`P1` stores the user's own stance, hypothesis, decision, doubt, interpretation, or memory.

Use `P1` for:

- a hypothesis you currently hold,
- a reason you made a decision,
- a doubt or discomfort,
- a shift in your own view,
- a note about what would change your mind.

Do not use `P1` as external evidence. A P1 line can be valuable precisely because it records your situated position.

## P1.5 — AI-mediated

`P1.5` stores output that emerged through a dialogue between the user and an AI system.

This layer is not “the AI's objective opinion.” It is an interaction product shaped by the user's prompt, the conversation history, model behavior, tool access, system constraints, and training distribution.

Use `P1.5` for:

- an AI-generated objection that changed the user's thinking,
- a frame, taxonomy, analogy, or question that is worth reusing,
- a synthesis that exposed a tension between voices,
- an AI error that revealed a useful misconception or ambiguity.

Required tag:

```text
not_use_as:factual_evidence
```

A P1.5 line can help think. It should not become evidence without a P2 or P3 check.

## P2 — second-person / field

`P2` stores voices from people in relation to the user: customers, collaborators, readers, colleagues, stakeholders, interviewees, local observers, and people in the field.

Use `P2` for:

- direct reactions,
- paraphrased field observations,
- stakeholder objections,
- customer language,
- small signals from the surrounding environment.

Required metadata should avoid unnecessary personal exposure:

```text
speaker_role:<role>
privacy:public|pseudonymized|internal|confidential
consent:explicit|implied|unknown
quote_policy:quote|paraphrase|summarize_only
```

P2 should not be averaged too quickly. One vivid reaction is not a trend, but it may be the earliest visible form of a real constraint.

## P3 — public anchor

`P3` stores public anchors: official sources, academic work, reports, public data, regulations, public statements, or reputable coverage.

P3 is not the center of this wiki. It is the refreshable anchor against which P1, P1.5, and P2 can be checked.

Required metadata:

```text
anchor_strength:official|academic|reputable_media|industry|weak
refresh_after:YYYY-MM-DD
```

Do not paste large public documents into the wiki. Store a concise claim summary and a pointer.
