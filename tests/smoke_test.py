#!/usr/bin/env python3
"""Smoke test for the synthetic polyphonic_wiki fixture."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        fixture = Path(tmp)
        (fixture / "topics").mkdir(parents=True)
        shutil.copy(ROOT / "examples" / "topic-ai-agent-governance.md", fixture / "topics" / "ai-agent-governance.md")
        run([sys.executable, "tools/polyphonic_lint.py", "--wiki", str(fixture), "--today", "2026-05-18"])
    run([sys.executable, "tools/polyphonic_auto.py", "--help"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
