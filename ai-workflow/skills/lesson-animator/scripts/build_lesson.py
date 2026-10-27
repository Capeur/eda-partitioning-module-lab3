#!/usr/bin/env python3
"""Build one animated lesson page from a storyboard, a timing file and its audio.

  python3 build_lesson.py --storyboard storyboard.json --timing timing-en.json --audio lesson-en.m4a \
      --lang en --out docs/lessons/part-1/            # writes index.html + lesson-en.m4a next to it
  ... --fonts site_src/fonts                          # self-host the three fonts (needed in mainland China)
  ... --inline-audio --artifact                       # one self-contained file to preview as a claude.ai artifact

The page is static: engine + CSS + data in one HTML file, the audio beside it (or inlined).
"""
from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent / "engine"
GOOGLE = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
          '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700'
          '&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:wght@400;600;700&display=swap">')
FONT_FILES = {  # @fontsource woff2 names used by the course sites (site_src/fonts)
    ("Fraunces", 500): "fraunces-latin-500-normal.woff2", ("Fraunces", 700): "fraunces-latin-700-normal.woff2",
    ("IBM Plex Mono", 400): "ibm-plex-mono-latin-400-normal.woff2", ("IBM Plex Mono", 500): "ibm-plex-mono-latin-500-normal.woff2",
    ("Source Sans 3", 400): "source-sans-3-latin-400-normal.woff2", ("Source Sans 3", 600): "source-sans-3-latin-600-normal.woff2",
    ("Source Sans 3", 700): "source-sans-3-latin-700-normal.woff2",
}
REQUIRED = ["graph", "poses", "timeline", "overlays"]


def check_storyboard(sb: dict) -> list[str]:
    probs = [f"storyboard has no '{k}'" for k in REQUIRED if k not in sb]
    g = sb.get("graph", {})
    nodes = set(g.get("nodes", []))
    for e in g.get("edges", []):
        u, v = (e[0], e[1]) if isinstance(e, list) else (e.get("u"), e.get("v"))
        if u not in nodes or v not in nodes:
            probs.append(f"edge {e} uses a node that is not in graph.nodes")
    for name, pose in sb.get("poses", {}).items():
        for n in nodes:
            p = pose.get(n)
            if not p:
                probs.append(f"pose {name}: no position for {n}")
            elif not (30 <= p[0] <= 930 and 30 <= p[1] <= 510):
                probs.append(f"pose {name}: {n} at {p} is outside the 960x540 stage (keep 30 px clear)")
    for i, o in enumerate(sb.get("overlays", [])):
        for k in ("from", "type"):
            if k not in o:
                probs.append(f"overlay #{i} has no '{k}'")
    return probs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--storyboard", required=True, type=Path)
    ap.add_argument("--timing", required=True, type=Path)
    ap.add_argument("--audio", required=True, type=Path)
    ap.add_argument("--lang", required=True)
    ap.add_argument("--out", required=True, type=Path, help="output folder (index.html is written there)")
    ap.add_argument("--fonts", type=Path, help="folder with the woff2 files to self-host (else Google Fonts)")
    ap.add_argument("--inline-audio", action="store_true", help="embed the audio as base64 (single file)")
    ap.add_argument("--artifact", action="store_true", help="omit doctype/html/head/body (claude.ai artifact preview)")
    ap.add_argument("--storage-key", default=None, help="localStorage key for the speed (default lesson-speed)")
    ap.add_argument("--ui", type=Path, help="JSON of UI string overrides for this language")
    a = ap.parse_args()

    sb = json.loads(a.storyboard.read_text(encoding="utf-8"))
    timing = json.loads(a.timing.read_text(encoding="utf-8"))
    probs = check_storyboard(sb)
    if probs:
        print("storyboard problems:\n  " + "\n  ".join(probs), file=sys.stderr)
        return 1
    if timing.get("lang") and timing["lang"] != a.lang:
        print(f"timing file is for {timing['lang']}, not {a.lang}", file=sys.stderr)
        return 1

    a.out.mkdir(parents=True, exist_ok=True)
    if a.inline_audio:
        audio_src = "data:audio/mp4;base64," + base64.b64encode(a.audio.read_bytes()).decode()
    else:
        dest = a.out / f"lesson-{a.lang}{a.audio.suffix}"
        if a.audio.resolve() != dest.resolve():
            shutil.copyfile(a.audio, dest)
        audio_src = dest.name

    head = GOOGLE
    if a.fonts:
        fdir = a.out / "fonts"
        fdir.mkdir(exist_ok=True)
        faces = []
        for (fam, wt), fn in FONT_FILES.items():
            src = a.fonts / fn
            if not src.is_file():
                print(f"missing font file {src}", file=sys.stderr)
                return 1
            shutil.copyfile(src, fdir / fn)
            faces.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:normal;font-display:swap;src:url(fonts/{fn}) format('woff2')}}")
        head = "<style>" + "".join(faces) + "</style>"

    data = {"sb": sb, "timing": timing, "lang": a.lang}
    if a.storage_key:
        data["storageKey"] = a.storage_key
    if a.ui:
        data["ui"] = json.loads(a.ui.read_text(encoding="utf-8"))
    title = sb.get("pageTitle", sb.get("title", "Lesson"))
    title = title.get(a.lang, title.get("en", "Lesson")) if isinstance(title, dict) else title
    html = (ENGINE / "lesson.html").read_text(encoding="utf-8")
    html = (html.replace("__LANG__", a.lang).replace("__TITLE__", title).replace("__HEAD_EXTRA__", head)
            .replace("__CSS__", (ENGINE / "lesson.css").read_text(encoding="utf-8"))
            .replace("__ENGINE__", (ENGINE / "lesson-engine.js").read_text(encoding="utf-8"))
            .replace("__AUDIO_SRC__", audio_src)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    if a.artifact:
        import re
        html = re.sub(r"<!doctype html>\s*<html[^>]*>\s*<head>\s*<meta charset=\"utf-8\">\s*<meta name=\"viewport\"[^>]*>\s*", "", html, flags=re.I)
        html = html.replace("</head>\n<body>\n", "").replace("</body>\n</html>\n", "")
    out = a.out / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out} ({out.stat().st_size / 1e6:.2f} MB), {timing['duration']:.1f} s, {len(timing['sentences'])} sentences, words {timing.get('words', '?')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
