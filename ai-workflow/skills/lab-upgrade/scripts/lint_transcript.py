#!/usr/bin/env python3
"""Lint a module transcript.md BEFORE building slides, using the teacher's own builder.

    python3 lint_transcript.py <module_dir> [--scripts <.cursor/skills/module-slides/scripts>]

Reports, per slide: the slide type the builder will make, bullets that will be CUT
(sentence > 90 chars, so the builder keeps only one half), words the TTS will misread
(a slash becomes "or"), and deck totals (slides, words, minutes at 150 wpm).
Exit code 1 if there is any CUT or slash problem.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def find_scripts(start: Path) -> Path | None:
    for d in [start, *start.parents]:
        s = d / ".cursor/skills/module-slides/scripts"
        if (s / "transcript_to_outline.py").is_file():
            return s
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("module_dir", type=Path)
    ap.add_argument("--scripts", type=Path, help="teacher scripts dir (auto-found from module_dir)")
    args = ap.parse_args()
    mod = args.module_dir.resolve()
    if mod.name == "transcript.md":
        mod = mod.parent
    scripts = args.scripts.resolve() if args.scripts else find_scripts(mod)
    if not scripts:
        sys.exit("Can't find .cursor/skills/module-slides/scripts; pass --scripts")
    sys.path.insert(0, str(scripts))
    import prose_to_bullets as pb  # noqa: E402
    from transcript_to_outline import transcript_to_outline  # noqa: E402

    outline = transcript_to_outline(mod)
    slides = outline["slides"]
    problems = 0
    words = 0
    seen_notes: set[str] = set()
    print(f"Deck: {outline['title']!r} — {len(slides)} slides\n")
    for n, s in enumerate(slides, 1):
        kind = s["type"]
        notes = s.get("notes") or ""
        issues: list[str] = []
        if notes and notes not in seen_notes:  # code slides repeat their section's notes
            seen_notes.add(notes)
            words += len(re.findall(r"\w+", notes))
            # the TTS cleaner turns any word/word (paths in backticks too) into "word or word"
            for m in re.finditer(r"\S*\w\s*/\s*\w\S*", notes):
                issues.append(f"SLASH  read as 'or': {m.group(0)!r}")
        sentences = pb._split_sentences(notes)
        if kind == "title":
            first = sentences[0] if sentences else ""
            if len(pb._normalize(first)) > pb.MAX_SUBTITLE_CHARS:
                issues.append(f"CUT    subtitle {len(first)} > {pb.MAX_SUBTITLE_CHARS}: {first!r}")
        elif kind in ("bullets", "two_column"):
            for sent in sentences[: pb.MAX_BULLETS]:
                if len(pb._normalize(sent)) > pb.MAX_BULLET_CHARS:
                    kept = pb.summarize_bullet(sent)
                    issues.append(f"CUT    {len(sent)} chars -> shows only {kept!r}")
            if len(sentences) > pb.MAX_BULLETS:
                issues.append(f"info   {len(sentences)} sentences: only the first "
                              f"{pb.MAX_BULLETS} are on screen (rest spoken)")
        elif kind == "image" and s.get("image", "").split("/")[-1] and \
                not re.search(r"assets/(lab|steps/)|real-shell", s.get("image", "")):
            issues.append("info   image slide without bullets (needs >= 2 sentences for two-column)")
        problems += sum(1 for i in issues if not i.startswith("info"))
        mark = "!!" if any(not i.startswith("info") for i in issues) else "ok"
        print(f"{mark} {n:2d} [{kind:10s}] {s.get('title', '')}")
        for i in issues:
            print(f"        {i}")
    print(f"\nWords spoken: {words} (~{words / 150:.1f} min at 150 wpm)")
    print(f"Problems: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
