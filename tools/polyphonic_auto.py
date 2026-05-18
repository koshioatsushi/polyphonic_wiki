#!/usr/bin/env python3
"""Automatic capture and safe fold manager for polyphonic_wiki.

This tool uses only the Python standard library.

Policy:
- save inputs automatically;
- append high-confidence entries to topic pages;
- send ambiguous or sensitive items to events/queue/;
- never treat AI-mediated P1.5 entries as factual evidence;
- keep an append-only log in logs/auto-log.md.

Typical use:

    python tools/polyphonic_auto.py init --wiki .
    python tools/polyphonic_auto.py capture --wiki . --topic ai-agent-governance --source-type self_memo --title "First thought" --text "..." --process
    python tools/polyphonic_auto.py process --wiki .
    python tools/polyphonic_auto.py watch --wiki .
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
URL_RE = re.compile(r"https?://[^\s\])>]+")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\-\s()]{7,}\d)(?!\d)")
VOICE_TAG_RE = re.compile(r"\[\s*(P1\.5|P1|P2|P3)\s*\]|^\s*(P1\.5|P1|P2|P3)\s*[:：]", re.IGNORECASE)
STATUS_RE = re.compile(r"(^status\s*:\s*)(\S+)", re.MULTILINE)

VOICE_SECTIONS = {
    "P1": "P1 — first-person",
    "P1.5": "P1.5 — AI-mediated",
    "P2": "P2 — field / relational voices",
    "P3": "P3 — public anchors",
}

SOURCE_TYPE_TO_VOICE = {
    "self_memo": "P1",
    "personal_memo": "P1",
    "manual_memo": "P1",
    "decision_note": "P1",
    "ai_dialogue": "P1.5",
    "dialogue": "P1.5",
    "field_note": "P2",
    "meeting_note": "P2",
    "interview": "P2",
    "reaction": "P2",
    "public_anchor": "P3",
    "public_source": "P3",
    "article": "P3",
    "paper": "P3",
}

P1_CUES = ["自分:", "自分：", "私:", "私：", "仮説:", "仮説：", "違和感:", "違和感：", "decision:", "hypothesis:"]
P15_CUES = ["ai:", "assistant:", "chatgpt:", "claude:", "gemini:", "llm:", "gpt:", "ai：", "claude：", "chatgpt："]
P2_CUES = ["顧客:", "顧客：", "ユーザー:", "ユーザー：", "読者:", "読者：", "現場:", "現場：", "同僚:", "同僚：", "customer:", "user:", "stakeholder:"]
P3_CUES = ["出典:", "出典：", "論文", "統計", "報道", "制度", "法律", "規制", "standard", "report", "paper", "regulation"]
SENSITIVE_CUES = [
    "住所", "電話", "メール", "実名", "個人情報", "患者", "診断", "病歴", "給与", "評価", "契約", "NDA", "秘密", "未公開",
    "confidential", "salary", "medical", "patient", "address", "phone"
]

DEFAULT_CONFIG = {
    "auto_apply_min_confidence": 0.76,
    "review_unknown": True,
    "review_sensitive": True,
    "review_p2_missing_metadata": True,
    "default_topic_type": "default",
    "default_refresh_days": 30,
    "watch_interval_seconds": 8,
    "archive_processed_inputs": True,
    "run_lint_after_process": True,
    "lint_report_path": "reports/last-lint-report.md",
    "sensitive_cues": SENSITIVE_CUES,
}


@dataclass
class ClassifiedEntry:
    text: str
    voice: str
    confidence: float
    reason: str
    sensitive: bool
    url: str = ""


def slugify(value: str, fallback: str = "item") -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\-_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or fallback


def today_str() -> str:
    return dt.date.today().isoformat()


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def relpath(path: Path, root: Path) -> str:
    if is_relative_to(path, root):
        return str(path.resolve().relative_to(root.resolve()))
    return str(path)


def load_config(root: Path) -> Dict[str, object]:
    path = root / "config" / "polyphonic_auto.json"
    cfg = dict(DEFAULT_CONFIG)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
    return cfg


def save_default_config(root: Path) -> None:
    config_dir = root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    path = config_dir / "polyphonic_auto.json"
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_layout(root: Path) -> None:
    for rel in ["inbox", "topics", "events/queue", "events/processed", "events/rejected", "logs", "sources", "archive/inputs", "config", "reports"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    save_default_config(root)
    log = root / "logs" / "auto-log.md"
    if not log.exists():
        log.write_text("# polyphonic_wiki auto log\n\n", encoding="utf-8")


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    data: Dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line or raw_line.strip().startswith("#"):
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, text[match.end():]


def write_frontmatter_status(path: Path, status: str) -> None:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return
    fm = match.group(1)
    if STATUS_RE.search(fm):
        new_fm = STATUS_RE.sub(rf"\g<1>{status}", fm, count=1)
    else:
        new_fm = fm.rstrip() + f"\nstatus: {status}"
    path.write_text("---\n" + new_fm + "\n---\n" + text[match.end():], encoding="utf-8")


def strip_prefix(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^[-*]\s+", "", text)
    text = re.sub(r"^\[\s*(P1\.5|P1|P2|P3)\s*\]\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(P1\.5|P1|P2|P3)\s*[:：]\s*", "", text, flags=re.IGNORECASE)
    for cue in P1_CUES + P15_CUES + P2_CUES:
        if text.lower().startswith(cue.lower()):
            return text[len(cue):].strip()
    return text


def body_to_candidate_lines(body: str) -> List[str]:
    lines: List[str] = []
    paragraph: List[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            if paragraph:
                lines.append(" ".join(paragraph).strip())
                paragraph = []
            continue
        if line.startswith("#") or line.startswith("<!--"):
            continue
        if re.match(r"^[-*]\s+", line) or VOICE_TAG_RE.search(line):
            if paragraph:
                lines.append(" ".join(paragraph).strip())
                paragraph = []
            lines.append(line)
        else:
            paragraph.append(line)
    if paragraph:
        lines.append(" ".join(paragraph).strip())
    return [ln for ln in lines if ln]


def detect_sensitive(line: str, cfg: Dict[str, object]) -> bool:
    cues = [str(x) for x in cfg.get("sensitive_cues", SENSITIVE_CUES)]
    lowered = line.lower()
    if any(cue.lower() in lowered for cue in cues):
        return True
    if EMAIL_RE.search(line) or PHONE_RE.search(line):
        return True
    return False


def classify_line(line: str, fm: Dict[str, str], cfg: Dict[str, object]) -> ClassifiedEntry:
    raw_line = line.strip()
    lowered = raw_line.lower()
    sensitive = detect_sensitive(raw_line, cfg)
    url_match = URL_RE.search(raw_line)
    url = url_match.group(0) if url_match else fm.get("url", "") or fm.get("url_or_ref", "")

    explicit = VOICE_TAG_RE.search(raw_line)
    if explicit:
        voice = (explicit.group(1) or explicit.group(2)).upper()
        if voice == "P1.5":
            voice = "P1.5"
        return ClassifiedEntry(strip_prefix(raw_line), voice, 0.96, "explicit voice marker", sensitive, url)

    explicit_fm_voice = fm.get("voice_layer", "").strip().upper()
    if explicit_fm_voice in {"P1", "P2", "P3"} or explicit_fm_voice == "P1.5":
        return ClassifiedEntry(strip_prefix(raw_line), explicit_fm_voice, 0.90, "voice_layer frontmatter", sensitive, url)

    source_type = (fm.get("source_type") or fm.get("source_kind") or "").strip().lower()
    if source_type in SOURCE_TYPE_TO_VOICE:
        return ClassifiedEntry(strip_prefix(raw_line), SOURCE_TYPE_TO_VOICE[source_type], 0.88, f"source_type:{source_type}", sensitive, url)

    if any(lowered.startswith(c.lower()) for c in P15_CUES):
        return ClassifiedEntry(strip_prefix(raw_line), "P1.5", 0.84, "AI dialogue cue", sensitive, url)
    if any(lowered.startswith(c.lower()) for c in P2_CUES):
        return ClassifiedEntry(strip_prefix(raw_line), "P2", 0.82, "field/reaction cue", sensitive, url)
    if url or any(c.lower() in lowered for c in P3_CUES):
        return ClassifiedEntry(strip_prefix(raw_line), "P3", 0.80, "public/source cue", sensitive, url)
    if any(lowered.startswith(c.lower()) for c in P1_CUES):
        return ClassifiedEntry(strip_prefix(raw_line), "P1", 0.82, "first-person cue", sensitive, url)

    default_voice = fm.get("default_voice", "").strip().upper()
    if default_voice in {"P1", "P2", "P3"} or default_voice == "P1.5":
        return ClassifiedEntry(strip_prefix(raw_line), default_voice, 0.78, "default_voice frontmatter", sensitive, url)

    return ClassifiedEntry(strip_prefix(raw_line), "P1", 0.45, "unknown; defaulted to P1 for review", sensitive, url)


def topic_path(root: Path, slug: str) -> Path:
    return root / "topics" / f"{slugify(slug, 'untitled')}.md"


def ensure_topic_page(root: Path, topic: str, title: str = "", topic_type: str = "default") -> Path:
    path = topic_path(root, topic)
    if path.exists():
        return path
    display_title = title or topic.replace("-", " ").replace("_", " ").title()
    now = today_str()
    content = f"""---
topic: {slugify(topic, 'untitled')}
title: {display_title}
topic_type: {topic_type or 'default'}
status: active
created: {now}
updated: {now}
---

# {display_title}

## Why this topic exists

<Add a short reason for tracking this topic.>

## P1 — first-person

## P1.5 — AI-mediated

## P2 — field / relational voices

## P3 — public anchors

## Tensions

## Missing voices

## Provisional synthesis

## Next checks

"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def append_to_section(path: Path, section_name: str, entry_line: str) -> None:
    text = path.read_text(encoding="utf-8")
    section_re = re.compile(rf"(^##\s+{re.escape(section_name)}\s*$)", re.MULTILINE)
    match = section_re.search(text)
    if not match:
        text = text.rstrip() + f"\n\n## {section_name}\n\n{entry_line}\n"
        path.write_text(text, encoding="utf-8")
        return
    start = match.end()
    next_match = re.search(r"^##\s+", text[start:], re.MULTILINE)
    insert_pos = start + next_match.start() if next_match else len(text)
    before = text[:insert_pos].rstrip()
    after = text[insert_pos:]
    new_text = before + "\n\n" + entry_line + "\n" + after
    path.write_text(new_text, encoding="utf-8")


def field_value(fm: Dict[str, str], key: str, default: str = "") -> str:
    value = fm.get(key, "").strip()
    return value or default


def plus_days(days: int) -> str:
    return (dt.date.today() + dt.timedelta(days=days)).isoformat()


def entry_to_markdown(entry: ClassifiedEntry, fm: Dict[str, str], source_rel: str, cfg: Dict[str, object]) -> str:
    date = field_value(fm, "date", today_str())
    text = re.sub(r"\s+", " ", entry.text.replace("\n", " ")).strip()
    if len(text) > 600:
        text = text[:597].rstrip() + "..."
    if not text.endswith((".", "。", "?", "？", "!", "！")):
        text = text + "。"
    source_ref = source_rel.replace(" ", "%20")

    if entry.voice == "P1":
        sensitivity = field_value(fm, "sensitivity", "private")
        tags = ["voice_layer:P1", "evidence_state:captured", "source_position:self", f"source_ref:{source_ref}", f"sensitivity:{sensitivity}", "retention_policy:keep", "auto_saved:true"]
    elif entry.voice == "P1.5":
        model = field_value(fm, "model", "unknown_model")
        session = field_value(fm, "session", Path(source_ref).stem)
        use_as = field_value(fm, "use_as", "hypothesis")
        tags = ["voice_layer:P1.5", "evidence_state:interpreted", "source_position:ai_dialogue", f"use_as:{use_as}", "not_use_as:factual_evidence", f"model:{model}", f"session:{session}", f"source_ref:{source_ref}", "retention_policy:distill", "auto_saved:true"]
    elif entry.voice == "P2":
        speaker_role = field_value(fm, "speaker_role", "unknown_role")
        privacy = field_value(fm, "privacy", "pseudonymized")
        consent = field_value(fm, "consent", "unknown")
        quote_policy = field_value(fm, "quote_policy", "paraphrase")
        sensitivity = field_value(fm, "sensitivity", "private")
        tags = ["voice_layer:P2", "evidence_state:captured", "source_position:field_reaction", f"speaker_role:{speaker_role}", f"privacy:{privacy}", f"consent:{consent}", f"quote_policy:{quote_policy}", f"source_ref:{source_ref}", f"sensitivity:{sensitivity}", "auto_saved:true"]
    else:
        anchor_strength = field_value(fm, "anchor_strength", "weak")
        url_or_ref = entry.url or field_value(fm, "url_or_ref", source_ref)
        refresh_after = field_value(fm, "refresh_after", plus_days(int(cfg.get("default_refresh_days", 30))))
        tags = ["voice_layer:P3", "evidence_state:externally_anchored", "source_position:public_anchor", f"anchor_strength:{anchor_strength}", f"url_or_ref:{url_or_ref}", f"refresh_after:{refresh_after}", "retention_policy:refresh", "auto_saved:true"]
    return f"- {date}: {text} [" + " | ".join(tags) + "]"


def needs_review(entry: ClassifiedEntry, fm: Dict[str, str], cfg: Dict[str, object]) -> Tuple[bool, str]:
    threshold = float(cfg.get("auto_apply_min_confidence", 0.76))
    if entry.confidence < threshold and bool(cfg.get("review_unknown", True)):
        return True, f"low confidence ({entry.confidence:.2f}): {entry.reason}"
    if entry.sensitive and bool(cfg.get("review_sensitive", True)):
        return True, "sensitive cue detected"
    if entry.voice == "P2" and bool(cfg.get("review_p2_missing_metadata", True)):
        missing = [key for key in ("speaker_role", "privacy", "consent") if not fm.get(key)]
        if missing:
            return True, "P2 missing metadata: " + ", ".join(missing)
    if not fm.get("topic"):
        return True, "missing topic frontmatter"
    return False, ""


def queue_review(root: Path, source: Path, fm: Dict[str, str], entry: ClassifiedEntry, reason: str) -> Path:
    queue_dir = root / "events" / "queue"
    queue_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1((str(source) + entry.text + reason).encode("utf-8")).hexdigest()[:10]
    path = queue_dir / f"{now_stamp()}-{digest}.json"
    payload = {
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "reason": reason,
        "source_file": relpath(source, root),
        "proposed_topic": fm.get("topic", ""),
        "proposed_voice": entry.voice,
        "confidence": entry.confidence,
        "classification_reason": entry.reason,
        "sensitive": entry.sensitive,
        "frontmatter": fm,
        "text": entry.text,
        "url": entry.url,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def log_run(root: Path, message: str) -> None:
    log = root / "logs" / "auto-log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"- {dt.datetime.now().isoformat(timespec='seconds')}: {message}\n")


def process_file(root: Path, path: Path, cfg: Dict[str, object]) -> Tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm.get("status") == "processed":
        return 0, 0
    lines = body_to_candidate_lines(body)
    applied = 0
    queued = 0
    topic = fm.get("topic", "").strip()
    source_rel = relpath(path, root)

    for line in lines:
        entry = classify_line(line, fm, cfg)
        review, reason = needs_review(entry, fm, cfg)
        if review:
            queue_review(root, path, fm, entry, reason)
            queued += 1
            continue
        tpath = ensure_topic_page(root, topic, title=fm.get("topic_title", fm.get("title", topic)), topic_type=fm.get("topic_type", str(cfg.get("default_topic_type", "default"))))
        md_line = entry_to_markdown(entry, fm, source_rel, cfg)
        append_to_section(tpath, VOICE_SECTIONS[entry.voice], md_line)
        applied += 1

    new_status = "review_queued" if queued else "processed"
    write_frontmatter_status(path, new_status)
    log_run(root, f"processed {source_rel}: applied={applied}, queued={queued}, status={new_status}")

    if queued == 0 and bool(cfg.get("archive_processed_inputs", False)) and path.exists():
        date = fm.get("date") or today_str()
        archive_dir = root / "archive" / "inputs" / date
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest = archive_dir / path.name
        if dest.exists():
            dest = archive_dir / f"{path.stem}-{now_stamp()}{path.suffix}"
        shutil.move(str(path), str(dest))

    return applied, queued


def pending_inbox_files(root: Path) -> List[Path]:
    inbox = root / "inbox"
    if not inbox.exists():
        return []
    files: List[Path] = []
    for p in sorted(inbox.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".md", ".txt"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm, _ = parse_frontmatter(text)
        if fm.get("status") not in {"processed", "review_queued", "archived", "done", "skip", "skipped"}:
            files.append(p)
    return files



def run_lint_report(root: Path) -> Tuple[int, Path]:
    report_path = root / "reports" / "last-lint-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lint_script = root / "tools" / "polyphonic_lint.py"
    if not lint_script.exists():
        report_path.write_text("# polyphonic_wiki lint report\n\npolyphonic_lint.py not found.\n", encoding="utf-8")
        return 0, report_path
    result = subprocess.run(
        [sys.executable, str(lint_script), "--wiki", str(root), "--today", today_str()],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    report_path.write_text(result.stdout, encoding="utf-8")
    return result.returncode, report_path

def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.wiki).resolve()
    ensure_layout(root)
    print(f"initialized polyphonic_wiki automation at {root}")
    return 0


def cmd_capture(args: argparse.Namespace) -> int:
    root = Path(args.wiki).resolve()
    ensure_layout(root)
    if args.text:
        body = args.text
    elif args.file:
        body = Path(args.file).read_text(encoding="utf-8")
    else:
        body = sys.stdin.read()
    if not body.strip():
        print("No input text provided", file=sys.stderr)
        return 2
    date = args.date or today_str()
    title = args.title or "untitled"
    slug = slugify(args.slug or title or args.source_type, "capture")
    path = root / "inbox" / f"{date}-{now_stamp()}-{slug}.md"
    fm_lines = [
        "---",
        f"date: {date}",
        f"title: {title}",
        f"topic: {args.topic or ''}",
        f"topic_type: {args.topic_type or ''}",
        f"source_type: {args.source_type}",
        "status: pending",
    ]
    optional = {
        "model": args.model,
        "session": args.session,
        "use_as": args.use_as,
        "speaker_role": args.speaker_role,
        "privacy": args.privacy,
        "consent": args.consent,
        "quote_policy": args.quote_policy,
        "url_or_ref": args.url_or_ref,
        "anchor_strength": args.anchor_strength,
        "refresh_after": args.refresh_after,
        "sensitivity": args.sensitivity,
    }
    for key, value in optional.items():
        if value:
            fm_lines.append(f"{key}: {value}")
    fm_lines.append("---")
    path.write_text("\n".join(fm_lines) + "\n\n" + body.strip() + "\n", encoding="utf-8")
    print(path.relative_to(root))
    if args.process:
        cfg = load_config(root)
        applied, queued = process_file(root, path, cfg)
        print(f"processed: applied={applied}, queued={queued}")
        if getattr(args, "lint", False) or bool(cfg.get("run_lint_after_process", False)):
            _, report = run_lint_report(root)
            print(f"lint_report={report.relative_to(root)}")
    return 0


def run_lint(root: Path, cfg: Dict[str, object]) -> Tuple[int, Path]:
    report_path = root / str(cfg.get("lint_report_path", "reports/last-lint-report.md"))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    script = root / "tools" / "polyphonic_lint.py"
    if not script.exists():
        report_path.write_text("# polyphonic_wiki lint report\n\npolyphonic_lint.py not found.\n", encoding="utf-8")
        return 0, report_path
    import subprocess
    result = subprocess.run([sys.executable, str(script), "--wiki", str(root), "--today", today_str()], text=True, capture_output=True)
    report_path.write_text(result.stdout + (("\n" + result.stderr) if result.stderr else ""), encoding="utf-8")
    return result.returncode, report_path


def cmd_process(args: argparse.Namespace) -> int:
    root = Path(args.wiki).resolve()
    ensure_layout(root)
    cfg = load_config(root)
    files = [Path(args.file).resolve()] if args.file else list(pending_inbox_files(root))
    total_applied = 0
    total_queued = 0
    for path in files:
        if not path.exists():
            print(f"missing file: {path}", file=sys.stderr)
            continue
        applied, queued = process_file(root, path, cfg)
        total_applied += applied
        total_queued += queued
    print(f"processed_files={len(files)} applied={total_applied} queued={total_queued}")
    if getattr(args, "lint", False) or bool(cfg.get("run_lint_after_process", False)):
        _, report = run_lint_report(root)
        print(f"lint_report={report.relative_to(root)}")
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    root = Path(args.wiki).resolve()
    ensure_layout(root)
    cfg = load_config(root)
    interval = int(args.interval or cfg.get("watch_interval_seconds", 8))
    print(f"watching {root / 'inbox'} every {interval}s. Press Ctrl-C to stop.")
    seen: set[str] = set()
    try:
        while True:
            changed = False
            for path in pending_inbox_files(root):
                key = str(path) + str(path.stat().st_mtime_ns)
                if key in seen:
                    continue
                applied, queued = process_file(root, path, cfg)
                print(f"{path.relative_to(root)}: applied={applied}, queued={queued}")
                seen.add(key)
                changed = True
            if changed and (getattr(args, "lint", False) or bool(cfg.get("run_lint_after_process", False))):
                _, report = run_lint_report(root)
                print(f"lint_report={report.relative_to(root)}")
            if getattr(args, "once", False):
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("stopped")
        return 0


def cmd_review(args: argparse.Namespace) -> int:
    root = Path(args.wiki).resolve()
    queue = root / "events" / "queue"
    items = sorted(queue.glob("*.json")) if queue.exists() else []
    if not items:
        print("event queue is empty")
        return 0
    for idx, path in enumerate(items, 1):
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"[{idx}] {path.name}")
        print(f"  reason: {data.get('reason')}")
        print(f"  proposed: topic={data.get('proposed_topic') or '-'} voice={data.get('proposed_voice')} confidence={data.get('confidence')}")
        print(f"  text: {data.get('text')}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    root = Path(args.wiki).resolve()
    ensure_layout(root)
    cfg = load_config(root)
    item_path = Path(args.item)
    if not item_path.is_absolute():
        item_path = root / "events" / "queue" / item_path
    if not item_path.exists():
        print(f"missing event item: {item_path}", file=sys.stderr)
        return 2
    data = json.loads(item_path.read_text(encoding="utf-8"))
    fm = dict(data.get("frontmatter", {}))
    topic = args.topic or data.get("proposed_topic") or fm.get("topic")
    voice = args.voice or data.get("proposed_voice")
    if not topic:
        print("approval needs --topic", file=sys.stderr)
        return 2
    if voice not in VOICE_SECTIONS:
        print("approval needs --voice P1|P1.5|P2|P3", file=sys.stderr)
        return 2
    fm["topic"] = topic
    entry = ClassifiedEntry(text=args.text or data.get("text", ""), voice=voice, confidence=1.0, reason="human approved", sensitive=bool(data.get("sensitive")), url=data.get("url", ""))
    tpath = ensure_topic_page(root, topic, title=fm.get("topic_title", topic), topic_type=fm.get("topic_type", str(cfg.get("default_topic_type", "default"))))
    md_line = entry_to_markdown(entry, fm, data.get("source_file", relpath(item_path, root)), cfg)
    append_to_section(tpath, VOICE_SECTIONS[voice], md_line)
    processed_dir = root / "events" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(item_path), str(processed_dir / item_path.name))
    log_run(root, f"approved {item_path.name}: topic={topic}, voice={voice}")
    print(f"approved -> topics/{slugify(topic)}.md ({voice})")
    return 0



def cmd_report(args: argparse.Namespace) -> int:
    root = Path(args.wiki).resolve()
    ensure_layout(root)
    code, report = run_lint_report(root)
    print(report.read_text(encoding="utf-8"))
    print(f"saved_report={report.relative_to(root)}")
    return code

def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.wiki).resolve()
    pending = list(pending_inbox_files(root))
    queued = list((root / "events" / "queue").glob("*.json")) if (root / "events" / "queue").exists() else []
    topics = list((root / "topics").glob("*.md")) if (root / "topics").exists() else []
    print(f"pending_inbox={len(pending)}")
    print(f"events_queue={len(queued)}")
    print(f"topics={len(topics)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automatic capture and safe fold manager for polyphonic_wiki")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create automation directories and config")
    p.add_argument("--wiki", default=".")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("capture", help="save text/file/stdin to inbox")
    p.add_argument("--wiki", default=".")
    p.add_argument("--text", default="")
    p.add_argument("--file", default="")
    p.add_argument("--process", action="store_true", help="process immediately after capture")
    p.add_argument("--lint", action="store_true", help="run structural lint after processing")
    p.add_argument("--date", default="")
    p.add_argument("--title", default="")
    p.add_argument("--slug", default="")
    p.add_argument("--topic", default="")
    p.add_argument("--topic-type", default="")
    p.add_argument("--source-type", "--source-kind", dest="source_type", default="mixed", choices=["mixed", "self_memo", "personal_memo", "manual_memo", "ai_dialogue", "dialogue", "field_note", "meeting_note", "interview", "reaction", "public_anchor", "public_source", "article", "paper", "decision_note"])
    p.add_argument("--model", default="")
    p.add_argument("--session", default="")
    p.add_argument("--use-as", default="")
    p.add_argument("--speaker-role", default="")
    p.add_argument("--privacy", default="")
    p.add_argument("--consent", default="")
    p.add_argument("--quote-policy", default="")
    p.add_argument("--url-or-ref", default="")
    p.add_argument("--anchor-strength", default="")
    p.add_argument("--refresh-after", default="")
    p.add_argument("--sensitivity", default="")
    p.set_defaults(func=cmd_capture)

    p = sub.add_parser("process", help="process pending inbox files")
    p.add_argument("--wiki", default=".")
    p.add_argument("--file", default="")
    p.add_argument("--lint", action="store_true", help="run structural lint after processing")
    p.set_defaults(func=cmd_process)

    p = sub.add_parser("watch", help="poll inbox and process new pending files")
    p.add_argument("--wiki", default=".")
    p.add_argument("--interval", type=int, default=0)
    p.add_argument("--lint", action="store_true", help="run structural lint after each changed pass")
    p.add_argument("--once", action="store_true", help="run one polling pass and exit")
    p.set_defaults(func=cmd_watch)

    p = sub.add_parser("review", help="list event queue")
    p.add_argument("--wiki", default=".")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("approve", help="approve an event queue item")
    p.add_argument("--wiki", default=".")
    p.add_argument("--item", required=True, help="event item file name or path")
    p.add_argument("--topic", default="")
    p.add_argument("--voice", default="")
    p.add_argument("--text", default="")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("report", help="run structural lint and save reports/last-lint-report.md")
    p.add_argument("--wiki", default=".")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("status", help="show pending/event/topic counts")
    p.add_argument("--wiki", default=".")
    p.set_defaults(func=cmd_status)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
