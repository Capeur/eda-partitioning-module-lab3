#!/usr/bin/env python3
"""Build the French slides, narration and video for Lab 03 with the course's own tools.

French sources live in i18n/fr/module01-03-initial-bipartition/:
    transcript.md      French narration (source of truth for slides + speech)
    assets/            French images (walkthrough frames, figures, lab screenshot)

Usage (from this repo's root):
    python3 make_fr_media.py --repo ../eda-learning              # slides + audio + video
    python3 make_fr_media.py --repo ../eda-learning --no-audio   # slides only (offline)

Audio uses edge-tts (needs internet) with the French voice fr-FR-DeniseNeural.
Outputs (slides.pptx/.pdf, audio/, video.mp4) stay in that folder; build_site.py picks them up.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FR_DIR = HERE / "i18n/fr/module01-03-initial-bipartition"
MODULE_REL = Path("courses/learn_partitioning/module01-03-initial-bipartition")
VOICE = os.environ.get("VOICE", "fr-FR-DeniseNeural")
FOOTER = "learn_partitioning — 03 bipartition initiale"


def run(cmd: list[str], **kw) -> None:
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def localize_outline(path: Path) -> None:
    """French footer and code-slide titles (the course scripts write English ones)."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["footer"] = FOOTER
    for s in data.get("slides", []):
        t = str(s.get("title", ""))
        t = re.sub(r" — try these( \(\d+/\d+\))?$", lambda m: " — à essayer" + (m.group(1) or ""), t)
        t = re.sub(r" — more$", " — suite", t)
        s["title"] = t
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def french_norm_title(original):
    """Wrap the course's title normalizer so French code-slide titles map back to
    their transcript section (otherwise narration timing drifts by one per code slide)."""
    def norm(title: str) -> str:
        t = re.sub(r"\s*[—–-]\s*à essayer.*$", "", title.strip())
        t = re.sub(r"\s*[—–-]\s*suite.*$", "", t)
        return original(t)
    return norm


def synthesize_french(scripts: Path) -> None:
    sys.path.insert(0, str(scripts))
    import asyncio

    import synthesize_audio as sa

    sa._norm_title = french_norm_title(sa._norm_title)
    asyncio.run(sa.synthesize_clip_audio(FR_DIR, voice=VOICE))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, type=Path, help="path to your eda-learning clone")
    ap.add_argument("--no-audio", action="store_true", help="skip narration and video (offline)")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    scripts = repo / ".cursor/skills/module-slides/scripts"
    if not (scripts / "build_pptx.py").is_file():
        print(f"ERROR: {repo} is not an eda-learning clone", file=sys.stderr)
        return 1

    # The terminal screenshot shows program output (English) — reuse the course one.
    src_assets = repo / MODULE_REL / "assets"
    for name in ["real-shell.png"]:
        if not (FR_DIR / "assets" / name).is_file():
            shutil.copy2(src_assets / name, FR_DIR / "assets" / name)
    # The lab screenshot must show the French lab (tools/lab03-figures/capture_lab.py --lang fr, taken from the
    # built docs/fr). Until it exists, the English one stands in so the deck still builds.
    if not (FR_DIR / "assets/lab-starter.png").is_file():
        print("WARNING: no French lab-starter.png yet, using the English screenshot (see README: French images)",
              file=sys.stderr)
        shutil.copy2(src_assets / "lab-starter.png", FR_DIR / "assets/lab-starter.png")

    py = sys.executable
    run([py, scripts / "transcript_to_outline.py", FR_DIR])
    localize_outline(FR_DIR / "outline.yaml")
    run([py, scripts / "build_pptx.py", FR_DIR])
    run([py, scripts / "verify_clip.py", FR_DIR])
    run([py, scripts / "verify_transcript_consistency.py", FR_DIR])
    run(["bash", scripts / "pptx_to_pdf.sh", FR_DIR / "slides.pptx"])
    if args.no_audio:
        print("Slides done (no audio). Run again without --no-audio to build the French video.")
        return 0
    synthesize_french(scripts)
    run(["bash", scripts / "build_video.sh", "--target-dir", FR_DIR])
    print(f"French video: {FR_DIR / 'video.mp4'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
