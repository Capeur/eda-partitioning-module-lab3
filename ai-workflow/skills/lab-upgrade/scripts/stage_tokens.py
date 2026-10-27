#!/usr/bin/env python3
"""Token use per Claude Code conversation, read from Claude Code's local logs.

Claude Code (terminal and VS Code) stores each conversation as a .jsonl file in
~/.claude/projects/<folder-name>/. Each reply records its token usage. This script
sums them per conversation and per model, so you can report what each stage cost.

Usage:
    python3 stage_tokens.py                      # conversations for the eda-learning-lab3 folder
    python3 stage_tokens.py --match lab3         # any project folder whose name contains "lab3"
    python3 stage_tokens.py --all                # every project
    python3 stage_tokens.py --csv tokens.csv     # also save a table for your report

Columns:
    input        new input tokens
    cache_write  tokens written to the prompt cache
    cache_read   tokens read back from the cache (cheap; most of a long conversation)
    output       tokens Claude wrote
"""
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"
FIELDS = ["input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"]
LABELS = ["input", "cache_write", "cache_read", "output"]


def read_session(path: Path):
    """Return (start, end, first user prompt, {model: [4 counts]}) for one conversation file."""
    seen = set()
    per_model = defaultdict(lambda: [0, 0, 0, 0])
    start = end = None
    first_prompt = ""
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = rec.get("timestamp")
        if ts:
            t = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
            start = t if start is None or t < start else start
            end = t if end is None or t > end else end
        msg = rec.get("message") or {}
        if rec.get("type") == "user" and not first_prompt:
            content = msg.get("content")
            if isinstance(content, str):
                first_prompt = content
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        first_prompt = part.get("text", "")
                        break
        usage = msg.get("usage")
        if rec.get("type") != "assistant" or not usage:
            continue
        # A reply is logged once per content block with the same id and usage: count it once.
        key = msg.get("id") or rec.get("requestId") or rec.get("uuid")
        if key in seen:
            continue
        seen.add(key)
        counts = per_model[msg.get("model", "unknown")]
        for i, f in enumerate(FIELDS):
            counts[i] += int(usage.get(f) or 0)
    return start, end, " ".join(first_prompt.split())[:70], dict(per_model)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--match", default="eda-learning-lab3", help="part of the project folder name")
    ap.add_argument("--all", action="store_true", help="every project")
    ap.add_argument("--csv", help="also write the table to this CSV file")
    args = ap.parse_args()

    if not ROOT.is_dir():
        raise SystemExit(f"No Claude Code logs found in {ROOT}")
    dirs = [d for d in ROOT.iterdir() if d.is_dir() and (args.all or args.match in d.name)]
    if not dirs:
        names = "\n  ".join(sorted(d.name for d in ROOT.iterdir() if d.is_dir()))
        raise SystemExit(f"No project folder contains '{args.match}'. Folders:\n  {names}")

    rows = []
    for d in dirs:
        for f in d.glob("*.jsonl"):
            start, end, prompt, per_model = read_session(f)
            for model, c in per_model.items():
                rows.append([start, end, d.name, f.stem[:8], model, *c, prompt])
    rows.sort(key=lambda r: r[0] or datetime.min.astimezone())

    head = f"{'start':16} {'min':>4} {'session':8} {'model':24} " + " ".join(f"{l:>11}" for l in LABELS)
    print(head)
    print("-" * len(head))
    totals = defaultdict(lambda: [0, 0, 0, 0])
    for start, end, _proj, sid, model, *rest in rows:
        counts, prompt = rest[:4], rest[4]
        mins = int((end - start).total_seconds() // 60) if start and end else 0
        when = start.strftime("%m-%d %H:%M") if start else "?"
        print(f"{when:16} {mins:>4} {sid:8} {model[:24]:24} " + " ".join(f"{n:>11,}" for n in counts))
        if prompt:
            print(f"{'':31}first prompt: {prompt}")
        for i, n in enumerate(counts):
            totals[model][i] += n
    print("-" * len(head))
    for model, c in totals.items():
        print(f"{'TOTAL':16} {'':>4} {'':8} {model[:24]:24} " + " ".join(f"{n:>11,}" for n in c))

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["start", "end", "project", "session", "model", *LABELS, "first_prompt"])
            for start, end, *rest in rows:
                w.writerow([start.isoformat() if start else "", end.isoformat() if end else "", *rest])
        print(f"\nSaved {args.csv}")


if __name__ == "__main__":
    main()
