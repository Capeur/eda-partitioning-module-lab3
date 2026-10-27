#!/usr/bin/env python3
"""Audit one eda-learning lab: what exists, what is thin, what to upgrade.

    python3 audit_lab.py <repo> <course> <module> <tool>
    python3 audit_lab.py ~/eda-learning learn_partitioning module01-03-initial-bipartition initial-bipartition

Prints a Markdown report to paste into UPGRADE_NOTES.md. Read-only.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

GENERIC = [  # phrases the teacher's generator leaves in thin labs
    "Change one knob", "Scale the instance slightly", "One algorithm per lab",
    "Gate-level SDF", "UVM phase", "Liberty CCSP", "Course-scale", "Drop-in replacement",
    "Note tying the run", "primary algorithm is", "Implement track is the fidelity path",
    "Quality without balance is often", "run the algorithm once", "Common traps",
]
SKIP_DIRS = {"audio", "frames", "__pycache__"}


def words(text: str) -> int:
    return len(re.findall(r"\w+", text))


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    repo, course, module, tool = Path(sys.argv[1]).expanduser().resolve(), *sys.argv[2:]
    mod = repo / "courses" / course / module
    tdir = repo / "platform/tools" / tool
    common = repo / "courses" / course / "common"
    for p in (mod, tdir):
        if not p.is_dir():
            sys.exit(f"missing: {p}")
    out: list[str] = [f"# Audit — {course} / {module}", ""]

    # Lab number from the website crumb
    crumb = "?"
    page = repo / "platform/courses" / course / "labs" / tool / "index.html"
    if page.is_file():
        m = re.search(r"data-lab-crumb>([^<]+)<", page.read_text(encoding="utf-8"))
        crumb = m.group(1) if m else "?"
    out += [f"- Lab number (website crumb): **{crumb}**  (`{page.relative_to(repo)}`)",
            f"- Module: `{mod.relative_to(repo)}`", f"- Tool: `{tdir.relative_to(repo)}`", ""]

    # Files
    out += ["## Module files", ""]
    for f in sorted(mod.rglob("*")):
        rel = f.relative_to(mod)
        if f.is_file() and not (set(rel.parts) & SKIP_DIRS):
            out.append(f"- `{rel}` ({f.stat().st_size // 1024} KB)")
    examples = sorted((mod / "examples").glob("*")) if (mod / "examples").is_dir() else []
    has_checker = any(f.name.endswith("_check.py") for f in examples)
    out += ["", f"- Example inputs: {len([f for f in examples if f.suffix == '.json'])}; "
            f"golden checker script: {'yes' if has_checker else '**no**'}", ""]

    # Transcript
    tr = (mod / "transcript.md").read_text(encoding="utf-8") if (mod / "transcript.md").is_file() else ""
    sections = re.findall(r"^## (.+)$", tr, re.M)
    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", tr)
    out += ["## Transcript", "",
            f"- {len(sections)} sections, {words(tr)} words (~{words(tr) / 150:.1f} min); "
            f"target for the beginner rewrite: 18–22 sections, 1,200–1,400 words",
            f"- Images: {', '.join(f'`{i}`' for i in images) or 'none'}",
            "- Sections: " + " · ".join(s.split("—", 1)[-1].strip() for s in sections),
            "- Run `lint_transcript.py` for cut bullets and TTS problems.", ""]

    # EXAMPLES / quiz / checklist
    ex = (mod / "EXAMPLES.md").read_text(encoding="utf-8") if (mod / "EXAMPLES.md").is_file() else ""
    tables = len(re.findall(r"^\|[- |]+\|$", ex, re.M))
    out += ["## EXAMPLES.md", "", f"- {words(ex)} words, {tables} tables, "
            f"pseudocode blocks: {ex.count('```text')}, "
            f"GOLDEN lines: {len(re.findall('GOLDEN', ex))}", ""]
    quiz = {}
    if (mod / "quiz.json").is_file():
        quiz = json.loads((mod / "quiz.json").read_text(encoding="utf-8"))
    items = quiz.get("items", [])
    out += ["## quiz.json", "", f"- {len(items)} items (target 6–8, each testing one idea with numbers)"]
    for it in items:
        out.append(f"  - {it.get('id')}: {it.get('prompt', '')[:90]}")
    out.append("")

    # Generic placeholders
    hits = []
    for f in [mod / "EXAMPLES.md", mod / "quiz.json", mod / "transcript.md", mod / "CHECKLIST.md",
              mod / "README.md", *tdir.glob("*.js")]:
        if f.is_file():
            text = f.read_text(encoding="utf-8")
            for g in GENERIC:
                if g.lower() in text.lower():
                    hits.append(f"`{f.name}`: “{g}”")
    out += ["## Placeholder text found (teacher left these thin on purpose)", ""]
    out += [f"- {h}" for h in hits] or ["- none"]
    out.append("")

    # Browser lab
    out += ["## Browser lab", ""]
    for js in sorted(tdir.glob("*.js")):
        src = js.read_text(encoding="utf-8")
        levels = re.findall(r'level:\s*"(\w+)"', src)
        imports = re.findall(r'from\s+"([^"]+)"', src)
        out.append(f"- `{js.name}`: {src.count(chr(10))} lines, {len(levels)} challenges "
                   f"({', '.join(f'{l} {levels.count(l)}' for l in dict.fromkeys(levels))}); "
                   f"imports {', '.join(f'`{i}`' for i in imports)}")
        uses_reveal = "revealAssignment" in src or "Reveal" in src
        out.append(f"  - reveal/golden button present: {'yes — make sure no challenge passes from it' if uses_reveal else 'no'}")
        for cid, title in re.findall(r'id:\s*"([\w-]+)",\s*\n\s*title:\s*"([^"]+)"', src):
            out.append(f"  - `{cid}` — {title}")
    css = re.findall(r'href="\.\./\.\./assets/([^"]+\.css)"', (tdir / "index.html").read_text(encoding="utf-8")) \
        if (tdir / "index.html").is_file() else []
    out += [f"- Shared CSS linked by the page: {', '.join(css)}", ""]

    # Course helpers
    out += ["## Course `common/` helpers you can import (do not edit them)", ""]
    for py in sorted(common.glob("*.py")):
        if py.name.startswith("test_"):
            continue
        defs = re.findall(r"^def (\w+)", py.read_text(encoding="utf-8"), re.M)
        out.append(f"- `{py.name}`: {', '.join(d for d in defs if not d.startswith('_'))}")
    out.append("")

    # Git state
    try:
        r = subprocess.run(["git", "-C", str(repo), "status", "--short"], capture_output=True,
                           text=True, timeout=30)
        st = r.stdout.strip() if r.returncode == 0 else "(not a git repository)"
        out += ["## git status (teacher clone)", "", "```", st or "(clean)", "```", ""]
    except Exception:
        pass

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
