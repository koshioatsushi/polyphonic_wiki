# Contributing

Thank you for improving `polyphonic_wiki`.

## What contributions fit

Good contributions include:

- clearer voice-layer definitions;
- safer privacy defaults;
- better Markdown templates;
- LLM client skill files;
- local CLI improvements;
- synthetic examples;
- adapters that export voice metadata to other tools.

## What not to contribute

Please do not contribute real private notes, real customer reactions, raw transcripts, private AI conversation logs, or identifiable P2 field material.

## Development check

Run the local linter against the synthetic fixture:

```bash
mkdir -p /tmp/polyphonic_wiki_fixture/topics
cp examples/topic-ai-agent-governance.md /tmp/polyphonic_wiki_fixture/topics/ai-agent-governance.md
python tools/polyphonic_lint.py --wiki /tmp/polyphonic_wiki_fixture --today 2026-05-18
python tools/polyphonic_auto.py --help
```
