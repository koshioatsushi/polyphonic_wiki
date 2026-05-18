#!/usr/bin/env python3
"""Minimal absent-voice linter for polyphonic_wiki.

This tool intentionally uses only the Python standard library.
It checks Markdown topic pages for structural voice-provenance risks:

- missing required or recommended voice layers by topic_type;
- P1.5 lines without not_use_as:factual_evidence;
- P2 lines without speaker_role/privacy/consent;
- P3 lines without refresh_after or with expired refresh_after;
- pages with multiple voices but no Tensions section;
- pages with synthesis but no Missing voices section.

It does not judge truth. It only flags voice-structure problems.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

VOICE_RE = re.compile(r"voice_layer\s*:\s*(P1\.5|P1|P2|P3)\b")
FIELD_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*([^\]|\s]+)")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")

EXPECTATIONS: Dict[str, Dict[str, List[str]]] = {
    "default": {"required": ["P1"], "recommended": ["P1.5", "P2", "P3"]},
    "product_hypothesis": {"required": ["P1", "P2"], "recommended": ["P1.5", "P3"]},
    "research_claim": {"required": ["P1", "P3"], "recommended": ["P1.5", "P2"]},
    "decision_trace": {"required": ["P1"], "recommended": ["P1.5", "P2", "P3"]},
    "field_pattern": {"required": ["P2"], "recommended": ["P1", "P3"]},
    "public_issue": {"required": ["P3"], "recommended": ["P1", "P2"]},
    "creative_work": {"required": ["P1"], "recommended": ["P1.5", "P2"]},
}


@dataclass
class PageReport:
    path: Path
    topic_type: str
    voices: Set[str] = field(default_factory=set)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def parse_frontmatter(text: str) -> Dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data: Dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def parse_fields(line: str) -> Dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in FIELD_RE.finditer(line)}


def topic_files(root: Path) -> Iterable[Path]:
    topics = root / "topics"
    if topics.exists():
        yield from sorted(p for p in topics.rglob("*.md") if p.is_file())
    else:
        yield from sorted(p for p in root.rglob("*.md") if p.is_file())


def has_section(text: str, name: str) -> bool:
    return re.search(rf"^#+\s+{re.escape(name)}\b", text, re.MULTILINE | re.IGNORECASE) is not None


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def lint_page(path: Path, root: Path, today: dt.date) -> PageReport:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    topic_type = fm.get("topic_type", "default") or "default"
    expectations = EXPECTATIONS.get(topic_type, EXPECTATIONS["default"])
    report = PageReport(path=path, topic_type=topic_type)

    for match in VOICE_RE.finditer(text):
        voice = match.group(1)
        report.voices.add(voice)
        start = text.rfind("\n", 0, match.start()) + 1
        end = text.find("\n", match.end())
        if end == -1:
            end = len(text)
        line = text[start:end]
        fields = parse_fields(line)
        ln = line_number(text, match.start())

        if voice == "P1.5":
            if fields.get("not_use_as") != "factual_evidence":
                report.errors.append(f"L{ln}: P1.5 line missing not_use_as:factual_evidence")
            if "use_as" not in fields:
                report.warnings.append(f"L{ln}: P1.5 line missing use_as")
            if "model" not in fields:
                report.warnings.append(f"L{ln}: P1.5 line missing model")

        if voice == "P2":
            for required in ("speaker_role", "privacy", "consent"):
                if required not in fields:
                    report.errors.append(f"L{ln}: P2 line missing {required}")
            if "quote_policy" not in fields:
                report.warnings.append(f"L{ln}: P2 line missing quote_policy")

        if voice == "P3":
            refresh_after = fields.get("refresh_after")
            if not refresh_after:
                report.errors.append(f"L{ln}: P3 line missing refresh_after")
            else:
                try:
                    refresh_date = dt.date.fromisoformat(refresh_after)
                    if refresh_date < today:
                        report.warnings.append(
                            f"L{ln}: P3 refresh_after {refresh_after} is older than {today.isoformat()}"
                        )
                except ValueError:
                    report.errors.append(f"L{ln}: invalid refresh_after date {refresh_after!r}")
            if "anchor_strength" not in fields:
                report.warnings.append(f"L{ln}: P3 line missing anchor_strength")

    for required_voice in expectations["required"]:
        if required_voice not in report.voices:
            report.errors.append(f"Missing required voice {required_voice} for topic_type:{topic_type}")

    for recommended_voice in expectations["recommended"]:
        if recommended_voice not in report.voices:
            report.warnings.append(f"Missing recommended voice {recommended_voice} for topic_type:{topic_type}")

    if len(report.voices) >= 2 and not has_section(text, "Tensions"):
        report.warnings.append("Multiple voice layers present but no Tensions section found")

    if has_section(text, "Provisional synthesis") and not has_section(text, "Missing voices"):
        report.warnings.append("Provisional synthesis exists but Missing voices section is absent")

    if not report.voices:
        report.warnings.append("No voice_layer tags found")

    return report


def format_report(reports: List[PageReport], root: Path) -> str:
    total_errors = sum(len(r.errors) for r in reports)
    total_warnings = sum(len(r.warnings) for r in reports)
    lines: List[str] = []
    lines.append("# polyphonic_wiki lint report")
    lines.append("")
    lines.append(f"Pages checked: {len(reports)}")
    lines.append(f"Errors: {total_errors}")
    lines.append(f"Warnings: {total_warnings}")
    lines.append("")

    for report in reports:
        rel = report.path.relative_to(root)
        voices = ", ".join(sorted(report.voices)) if report.voices else "none"
        status = "OK" if not report.errors and not report.warnings else "CHECK"
        lines.append(f"## {rel} — {status}")
        lines.append(f"- topic_type: {report.topic_type}")
        lines.append(f"- voices: {voices}")
        if report.errors:
            lines.append("- errors:")
            for item in report.errors:
                lines.append(f"  - {item}")
        if report.warnings:
            lines.append("- warnings:")
            for item in report.warnings:
                lines.append(f"  - {item}")
        if not report.errors and not report.warnings:
            lines.append("- no structural issues found")
        lines.append("")

    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint polyphonic_wiki voice structure")
    parser.add_argument("--wiki", default=".", help="Path to wiki root")
    parser.add_argument("--today", default=dt.date.today().isoformat(), help="Date for refresh checks, YYYY-MM-DD")
    args = parser.parse_args(argv)

    root = Path(args.wiki).resolve()
    try:
        today = dt.date.fromisoformat(args.today)
    except ValueError:
        print(f"Invalid --today date: {args.today!r}", file=sys.stderr)
        return 2

    reports = [lint_page(path, root, today) for path in topic_files(root)]
    print(format_report(reports, root))
    return 1 if any(r.errors for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
