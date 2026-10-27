#!/usr/bin/env python3
"""Build the bilingual (English / French) Lab 03 GitHub Pages site into docs/.

    docs/            English page + English lab
    docs/fr/         French page + French lab (language switch on every page)

Sources
    English: your eda-learning clone (with the Lab 03 upgrade applied)
        courses/learn_partitioning/module01-03-initial-bipartition/   slides, video, quiz, examples, STEPS.md
        platform/tools/initial-bipartition/                           interactive browser lab (tests/ is not copied)
    French: this repo
        i18n/fr/module01-03-initial-bipartition/   French transcript, images, and (after
                                                   make_fr_media.py) slides, narration, video
        i18n/fr/EXAMPLES.md, quiz.json             Track A guide and quiz
        i18n/fr/walkthrough-steps.json             French walkthrough captions (same frames as STEPS.md)
        i18n/fr/lab_strings.py                     French text for the browser lab
        i18n/strings.py                            page text in both languages

Usage (from this repo's root):
    python3 make_fr_media.py --repo ../eda-learning-lab3     # French slides + video (once, needs internet)
    python3 build_site.py --repo ../eda-learning-lab3

The video is also cut into five parts (PARTS below) with ffmpeg: parts/part-N.mp4 + parts/part-N.vtt per language,
with a gentle zoom and pan on the figure slides. The full video.mp4 stays untouched, as a download. Cut parts are
cached in .cache/parts/ (keyed on the video, the timings and the zoom settings), so a rebuild only re-encodes what changed.

Needs: python3, ffmpeg, pdftoppm (poppler-utils), and `pip install markdown pyyaml pillow`.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "site_src"
FR_ROOT = HERE / "i18n/fr"
FR_MODULE = FR_ROOT / "module01-03-initial-bipartition"
MODULE_REL = Path("courses/learn_partitioning/module01-03-initial-bipartition")
TOOL_REL = Path("platform/tools/initial-bipartition")
ASSET_REL = Path("platform/assets")
CACHE = HERE / ".cache/parts"

# The five parts of the video, as (first slide, last slide), 1-based. They are the deck's PDF pages, i.e. the
# slides of outline.yaml (a code slide belongs to the part of the section it follows). Titles: i18n/strings.py.
PARTS = [(1, 6), (7, 11), (12, 19), (20, 25), (26, 30)]
FPS = 30
ZOOM_TYPES = {"two_column", "image"}   # figure slides; title, bullets and code slides stay still
ZOOM_MAX = 1.06                        # the picture grows by 6 % over the slide, no more
ZOOM_MIN_SECONDS = 4.0                 # shorter slides do not move
PART_SETTINGS = f"v1 fps={FPS} zoom={ZOOM_MAX} min={ZOOM_MIN_SECONDS} crf=27 veryfast {sorted(ZOOM_TYPES)}"

sys.path.insert(0, str(HERE / "i18n"))
from strings import LANGS  # noqa: E402


FONTS = [  # self-hosted (fonts.googleapis.com is blocked or very slow in some regions)
    ("Source Sans 3", 400, "source-sans-3-latin-400-normal.woff2"),
    ("Source Sans 3", 600, "source-sans-3-latin-600-normal.woff2"),
    ("Source Sans 3", 700, "source-sans-3-latin-700-normal.woff2"),
    ("Fraunces", 500, "fraunces-latin-500-normal.woff2"),
    ("Fraunces", 700, "fraunces-latin-700-normal.woff2"),
    ("IBM Plex Mono", 400, "ibm-plex-mono-latin-400-normal.woff2"),
    ("IBM Plex Mono", 500, "ibm-plex-mono-latin-500-normal.woff2"),
]
GOOGLE_FONTS = re.compile(r'@import url\("https://fonts\.googleapis\.com[^)]*\);\s*')


def fontface_css(prefix: str) -> str:
    """@font-face rules pointing at docs/fonts/ (prefix = path from the CSS file)."""
    return "".join(
        f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{w};font-display:swap;'
        f'src:url("{prefix}{f}") format("woff2");}}\n'
        for fam, w, f in FONTS
    )


def webp(src: Path, dest: Path, width: int, quality: int = 82) -> None:
    """Resized WebP copy for fast page loads (the full PNG stays available)."""
    from PIL import Image

    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "WEBP", quality=quality, method=6)


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- slides

def slide_titles(media: Path) -> list[str]:
    import yaml

    data = yaml.safe_load((media / "outline.yaml").read_text(encoding="utf-8"))
    return [str(s.get("title", f"Slide {i + 1}")) for i, s in enumerate(data.get("slides", []))]


def render_slides(pdf: Path, out: Path) -> int:
    if not pdf.is_file():
        die(f"missing {pdf}")
    if not shutil.which("pdftoppm"):
        die("pdftoppm not found: sudo apt install poppler-utils")
    dest = out / "slides"
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-png", "-r", "110", str(pdf), str(dest / "s")], check=True)
    pngs = sorted(dest.glob("s-*.png"), key=lambda p: int(re.findall(r"\d+", p.stem)[-1]))
    for i, p in enumerate(pngs, 1):
        full = dest / f"{i:02d}.png"
        p.rename(full)
        webp(full, dest / "thumb" / f"{i:02d}.webp", 480)
    webp(dest / "01.png", dest / "poster.webp", 1000)
    return len(pngs)


# ---------------------------------------------------------------- subtitles

def _fmt_ts(t: float, sep: str) -> str:
    ms_total = int(round(max(0.0, t) * 1000))
    h, rem = divmod(ms_total, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def _chunks(sentence: str, limit: int = 84) -> list[str]:
    """Split one sentence into caption-sized pieces (about two short lines)."""
    out, cur = [], ""
    for w in sentence.split():
        if cur and w in {"?", "!", ":", ";", "»"}:  # French puts a space before these: keep them on the word before
            cur = f"{cur} {w}"
        elif cur and len(cur) + 1 + len(w) > limit:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        out.append(cur)
    return out


def build_cues(repo: Path, media: Path) -> list[tuple[float, float, str]]:
    """Timed captions: each spoken section's audio length is shared over its caption
    chunks in proportion to their length (same per-slide timings as the video)."""
    scripts = repo / ".cursor/skills/module-slides/scripts"
    sys.path.insert(0, str(scripts))
    import synthesize_audio as sa  # noqa: E402
    from transcript_parse import load_transcript_sections  # noqa: E402
    from transcript_to_speech import clean_narration_prose  # noqa: E402

    # French code-slide titles ("— à essayer") must map back to their section too.
    fr = load_module(HERE / "make_fr_media.py", "make_fr_media")
    if not getattr(sa, "_fr_patched", False):
        sa._norm_title = fr.french_norm_title(sa._norm_title)
        sa._fr_patched = True

    timings = json.loads((media / "audio/slide_timings.json").read_text(encoding="utf-8"))
    sections = [s for s in load_transcript_sections(media / "transcript.md") if clean_narration_prose(s.body)]
    counts = sa._outline_slide_counts(media, len(sections))
    durations = [float(t["duration"]) for t in timings]

    cues, t, k = [], 0.0, 0
    for section, n in zip(sections, counts):
        span = sum(durations[k : k + n])
        k += n
        speech = clean_narration_prose(section.body)
        sentences = [x for x in re.split(r"(?<=[.!?])\s+", speech) if x.strip()]
        pieces = [c for s in sentences for c in _chunks(s)]
        total = sum(len(p) for p in pieces) or 1
        start = t
        for p in pieces:
            d = span * len(p) / total
            cues.append((start, start + d, p))
            start += d
        t += span
    return cues


def write_subtitles(cues, out: Path) -> None:
    vtt, srt = ["WEBVTT", ""], []
    for i, (a, b, text) in enumerate(cues, 1):
        vtt += [f"{_fmt_ts(a, '.')} --> {_fmt_ts(b, '.')}", text, ""]
        srt += [str(i), f"{_fmt_ts(a, ',')} --> {_fmt_ts(b, ',')}", text, ""]
    (out / "subs.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (out / "subs.srt").write_text("\n".join(srt), encoding="utf-8")


# ---------------------------------------------------------------- parts (the video cut in five)

def mmss(seconds: float) -> str:
    s = int(round(seconds))
    return f"{s // 60}:{s % 60:02d}"


def slide_kinds(media: Path) -> list[str]:
    import yaml

    data = yaml.safe_load((media / "outline.yaml").read_text(encoding="utf-8"))
    return [str(s.get("type", "")) for s in data.get("slides", [])]


def zoom_chain(kind: str, seconds: float, index: int) -> str:
    """ffmpeg filters for a slow zoom (1 -> ZOOM_MAX, eased) that drifts toward the figure.
    Two-column slides have the figure on the right, the walkthrough frames sit left of centre. The picture is
    first scaled to 4K so zoompan's whole-pixel steps do not show as jitter."""
    n = max(1, round(seconds * FPS))
    p = f"min(on/{n},1)"
    ease = f"({p}*{p}*(3-2*{p}))"
    fx0, fx1 = (0.5, 0.62) if kind == "two_column" else (0.5, 0.38)
    return (f"scale=3840:2160:flags=lanczos,"
            f"zoompan=z='1+{ZOOM_MAX - 1:.3f}*{ease}':"
            f"x='(iw-iw/zoom)*({fx0}+({fx1 - fx0:.3f})*{ease})':y='(ih-ih/zoom)*0.5':"
            f"d=1:s=1920x1080:fps={FPS}")


def cut_part(video: Path, start: float, durations: list[float], kinds: list[str], out: Path) -> None:
    """One part: [start, start + sum(durations)) of the full video, re-encoded; figure slides get the zoom."""
    chains, t = [], 0.0
    for i, (d, kind) in enumerate(zip(durations, kinds)):
        chain = f"[0:v]trim=start={t:.3f}:end={t + d:.3f},setpts=PTS-STARTPTS"
        if kind in ZOOM_TYPES and d >= ZOOM_MIN_SECONDS:
            chain += "," + zoom_chain(kind, d, i)
        chains.append(chain + f"[v{i}]")
        t += d
    graph = ";".join(chains) + ";" + "".join(f"[v{i}]" for i in range(len(chains))) + f"concat=n={len(chains)}:v=1:a=0[v]"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{sum(durations):.3f}", "-i", str(video),
           "-filter_complex", graph, "-map", "[v]", "-map", "0:a:0",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "27", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)


def part_cues(cues, t0: float, t1: float) -> list[tuple[float, float, str]]:
    """The cues of one part, with times counted from the start of that part."""
    return [(max(a, t0) - t0, min(b, t1) - t0, text) for a, b, text in cues if b > t0 + 1e-6 and a < t1 - 1e-6]


def frame_signature(png: Path):
    from PIL import Image

    return Image.open(png).convert("L").resize((320, 180), Image.LANCZOS)


def nearest_slide(frame: Path, slides_dir: Path, n_slides: int) -> int:
    """Number of the deck slide that looks most like this video frame (mean pixel difference at 320x180)."""
    from PIL import ImageChops, ImageStat

    sig = frame_signature(frame)
    diffs = [(ImageStat.Stat(ImageChops.difference(sig, frame_signature(slides_dir / f"{i:02d}.png"))).mean[0], i)
             for i in range(1, n_slides + 1)]
    return min(diffs)[1]


def verify_part_frames(part_files: list[Path], slides_dir: Path, durations: list[float], tmp: Path) -> list[str]:
    """Grab a frame 0.2 s after the start of every slide in every part (the zoom has barely begun there, so the
    frame still looks like the deck page) and check which deck slide it shows: parts start on the right slide
    and nothing drifts inside a part."""
    tmp.mkdir(parents=True, exist_ok=True)
    problems = []
    for k, ((first, last), mp4) in enumerate(zip(PARTS, part_files), 1):
        at = 0.0
        for slide in range(first, last + 1):
            png = tmp / f"p{k}-s{slide:02d}.png"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{at + 0.2:.3f}", "-i", str(mp4),
                            "-frames:v", "1", str(png)], check=True)
            got = nearest_slide(png, slides_dir, len(durations))
            if got != slide:
                problems.append(f"part {k}, {at + 0.2:.1f} s in: expected slide {slide}, the frame looks like slide {got}")
            at += durations[slide - 1]
    return problems


def build_parts(media: Path, out: Path, lang: str, durations: list[float], cues, n_slides: int, titles: list[str]) -> list[dict]:
    """Cut docs/<lang>/parts/part-N.mp4 + .vtt from the full video; return what the page needs."""
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        die("ffmpeg and ffprobe are needed to cut the video into parts")
    if PARTS[0][0] != 1 or PARTS[-1][1] != n_slides or any(b[0] != a[1] + 1 for a, b in zip(PARTS, PARTS[1:])):
        die(f"PARTS {PARTS} do not cover slides 1-{n_slides} exactly once")
    video, kinds = media / "video.mp4", slide_kinds(media)
    if len(kinds) != n_slides:
        die(f"{len(kinds)} slides in outline.yaml, {n_slides} in the deck")
    bounds = [0.0]
    for d in durations:
        bounds.append(bounds[-1] + d)
    (out / "parts").mkdir(parents=True, exist_ok=True)
    stamp = f"{video.stat().st_size}:{video.stat().st_mtime_ns}:{PART_SETTINGS}"
    parts = []
    for k, (first, last) in enumerate(PARTS, 1):
        durs, ks = durations[first - 1:last], kinds[first - 1:last]
        t0, t1 = bounds[first - 1], bounds[last]
        key = hashlib.sha1(f"{stamp}:{first}-{last}:{durs}:{ks}".encode()).hexdigest()[:12]
        cached = CACHE / lang / f"part-{k}-{key}.mp4"
        if not cached.is_file():
            print(f"[{lang}] encoding part {k} (slides {first}-{last}, {t1 - t0:.0f} s) ...", flush=True)
            for old in (CACHE / lang).glob(f"part-{k}-*.mp4"):
                old.unlink()
            cut_part(video, t0, durs, ks, cached)
        shutil.copy2(cached, out / f"parts/part-{k}.mp4")
        vtt = ["WEBVTT", ""]
        for a, b, text in part_cues(cues, t0, t1):
            vtt += [f"{_fmt_ts(a, '.')} --> {_fmt_ts(b, '.')}", text, ""]
        (out / f"parts/part-{k}.vtt").write_text("\n".join(vtt), encoding="utf-8")
        webp(out / "slides" / f"{first:02d}.png", out / f"slides/poster-{k}.webp", 1000)
        parts.append({"n": k, "first": first, "last": last, "seconds": t1 - t0, "title": titles[k - 1]})
    problems = verify_part_frames([out / f"parts/part-{k}.mp4" for k in range(1, len(PARTS) + 1)],
                                  out / "slides", durations, CACHE / lang / "check")
    if problems:
        die(f"[{lang}] the parts do not start or end on the right slide:\n  " + "\n  ".join(problems))
    return parts


def player_html(parts: list[dict], t: dict, lang: str) -> str:
    """One <video> that plays part 1; the list below it loads the others (see site_src/player.js)."""
    items = "".join(
        f'<li><button type="button" class="part" data-src="parts/part-{p["n"]}.mp4" data-vtt="parts/part-{p["n"]}.vtt" '
        f'data-poster="slides/poster-{p["n"]}.webp"{" aria-current=\"true\"" if p["n"] == 1 else ""}>'
        f'<span class="pn">{t["part_word"]} {p["n"]}</span><span class="pt">{esc(p["title"])}</span>'
        f'<span class="pl">{mmss(p["seconds"])}</span></button></li>' for p in parts)
    speeds = "".join(f'<button type="button" class="chip" data-speed="{s}" aria-pressed="{"true" if s == "1" else "false"}">{s}×</button>'
                     for s in ("1", "1.25", "1.5", "1.75", "2"))
    return (f'<div class="player" data-lang="{lang}" data-subs-label="{esc(t["subs_label"])}">'
            f'<video controls preload="metadata" poster="slides/poster-1.webp">'
            f'<source src="parts/part-1.mp4" type="video/mp4">'
            f'<track kind="subtitles" src="parts/part-1.vtt" srclang="{lang}" label="{esc(t["subs_label"])}" default>'
            f'{t["video_fallback"]}</video>'
            f'<div class="speed" role="group" aria-label="{esc(t["speed_label"])}"><span>{t["speed_label"]}</span>{speeds}</div>'
            f'<p class="parts-note">{t["parts_note"]}</p>'
            f'<ol class="parts">{items}</ol></div>')


# ---------------------------------------------------------------- browser lab

def copy_lab(repo: Path, out: Path, t: dict, other_lab: str) -> None:
    tool, assets = repo / TOOL_REL, repo / ASSET_REL
    dest_tool, dest_assets = out / "tools/initial-bipartition", out / "assets"
    dest_tool.mkdir(parents=True, exist_ok=True)
    dest_assets.mkdir(parents=True, exist_ok=True)
    for f in tool.iterdir():  # files only: tests/ (Playwright + model checks) stays in the course repo
        if f.is_file():
            shutil.copy2(f, dest_tool / f.name)
    assert not (dest_tool / "tests").exists()

    # Shared course assets the lab imports (follow the import graph).
    needed, todo = {"site.css", "tools-shared.css", "clustering-lab.css"}, []
    for f in tool.glob("*.js"):
        todo += re.findall(r'from\s+"\.\./\.\./assets/([^"]+)"', f.read_text(encoding="utf-8"))
    while todo:
        name = todo.pop()
        if name in needed:
            continue
        needed.add(name)
        todo += re.findall(r'from\s+"\./([^"]+)"', (assets / name).read_text(encoding="utf-8"))
    for name in sorted(needed):
        shutil.copy2(assets / name, dest_assets / name)
        if name.endswith(".css"):
            css = (dest_assets / name).read_text(encoding="utf-8")
            if GOOGLE_FONTS.search(css):
                fonts_prefix = "../fonts/" if out.name != "fr" else "../../fonts/"
                css = fontface_css(fonts_prefix) + GOOGLE_FONTS.sub("", css)
                (dest_assets / name).write_text(css, encoding="utf-8")

    # Standalone header with the language switch (platform nav/search are not deployed here).
    page = (dest_tool / "index.html").read_text(encoding="utf-8")
    page = re.sub(r'\s*<script src="\.\./\.\./assets/site\.js"></script>', "", page)
    page = re.sub(
        r'<header class="site-header">.*?</header>',
        '<header class="site-header">\n    <div class="site-header-inner">\n'
        f'      <p class="brand"><a href="../../index.html">{t["lab_brand"]}</a></p>\n'
        '      <nav class="site-nav" aria-label="Site">\n'
        f'        <a href="../../index.html">{t["lab_nav_home"]}</a>\n'
        f'        <a href="../../index.html#slides">{t["lab_nav_slides"]}</a>\n'
        f'        <a href="{other_lab}" hreflang="{t["switch_lang"]}" lang="{t["switch_lang"]}">{t["switch_text"]}</a>\n'
        '      </nav>\n    </div>\n  </header>',
        page,
        flags=re.S,
    )
    page = re.sub(r'<footer class="site-footer">.*?</footer>',
                  f'<footer class="site-footer">{t["lab_footer"]}</footer>', page, flags=re.S)
    (dest_tool / "index.html").write_text(page, encoding="utf-8")


def translate_lab(out: Path) -> None:
    """Apply i18n/fr/lab_strings.py to the French copy; fail if the lab drifted."""
    table = load_module(FR_ROOT / "lab_strings.py", "lab_strings").STRINGS
    missing = []
    files: dict[str, str] = {}
    for rel, en, fr in table:
        path = out / rel
        text = files.get(rel) or path.read_text(encoding="utf-8")
        if en not in text:
            missing.append(f"{rel}: {en[:70]}")
            continue
        files[rel] = text.replace(en, fr)
    if missing:
        die("French lab strings not found (the lab changed in eda-learning?). Update "
            "i18n/fr/lab_strings.py:\n  " + "\n  ".join(missing))
    for rel, text in files.items():
        (out / rel).write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- walkthrough

def steps_from_md(path: Path) -> list[dict]:
    """The English walkthrough: assets/STEPS.md of the course module (CRLF-safe)."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    steps = []
    for block in re.split(r"^## Step \d+ — ", text, flags=re.M)[1:]:
        title, _, rest = block.partition("\n")
        img = re.search(r"!\[[^\]]*\]\(steps/([^)]+)\)", rest)
        cap = re.search(r"\*\*Caption \(transcript\):\*\* ([^\n]+)", rest)
        bullets = re.findall(r"^- (.+)$", rest.split("**Slide bullets:**")[1].split("**On-screen")[0], flags=re.M)
        metrics = re.search(r"\*\*On-screen metrics:\*\*\s*```\n(.*?)```", rest, flags=re.S)
        if not (img and cap and bullets and metrics):
            die(f"cannot parse a step of {path}")
        steps.append({"file": img.group(1), "title": title.strip(), "caption": cap.group(1).strip(),
                      "bullets": bullets, "metrics": metrics.group(1).strip().splitlines()})
    return steps


def walkthrough_html(steps: list[dict], images: Path, out: Path, t: dict) -> str:
    """Five frames with the captions that are drawn in them (same pictures as the video's walkthrough slides)."""
    parts = []
    for i, st in enumerate(steps, 1):
        src = images / "steps" / st["file"]
        if not src.is_file():
            die(f"missing walkthrough picture {src}")
        webp(src, out / "img/steps" / (Path(st["file"]).stem + ".webp"), 940)
        shutil.copy2(src, out / "img/steps" / st["file"])
        bullets = "".join(f"<li>{esc(b)}</li>" for b in st["bullets"])
        parts.append(
            f'<figure class="walk-step"><a href="img/steps/{st["file"]}">'
            f'<img src="img/steps/{Path(st["file"]).stem}.webp" loading="lazy" width="940" height="468" '
            f'alt="{esc(t["step_word"])} {i} / {len(steps)}: {esc(st["title"])}"></a>'
            f'<figcaption><b>{esc(t["step_word"])} {i} / {len(steps)} · {esc(st["title"])}</b>'
            f'<span>{esc(st["caption"])}</span><ul>{bullets}</ul></figcaption></figure>')
    return "\n".join(parts)


# ---------------------------------------------------------------- page

def render_markdown(path: Path) -> str:
    import markdown

    return markdown.markdown(path.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])


def transcript_html(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    parts = []
    for title, body in re.findall(r"^## Slide \d+ — (.+?)\n(.*?)(?=^## Slide |\Z)", text, flags=re.S | re.M):
        body = re.sub(r"```.*?```", "", body, flags=re.S)
        body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        paras = [p.strip() for p in body.split("\n\n") if p.strip()]
        parts.append(f"<h3>{esc(title)}</h3>" + "".join(f"<p>{esc(p)}</p>" for p in paras))
    return "\n".join(parts)


def build_language(repo: Path, out: Path, lang: str, base: str) -> dict:
    """Build one language into `out`. `base` is the path from `out` to the shared docs/ root."""
    t = LANGS[lang]
    en_module = repo / MODULE_REL
    media = en_module if lang == "en" else FR_MODULE  # slides, transcript, audio, video
    examples_md = en_module / "EXAMPLES.md" if lang == "en" else FR_ROOT / "EXAMPLES.md"
    quiz_path = en_module / "quiz.json" if lang == "en" else FR_ROOT / "quiz.json"
    images = (en_module if lang == "en" else FR_MODULE) / "assets"

    if lang == "fr" and not (FR_MODULE / "slides.pdf").is_file():
        die("no French slides yet: run  python3 make_fr_media.py --repo ../eda-learning  first")

    out.mkdir(parents=True, exist_ok=True)
    for name in ["slides.pdf", "slides.pptx", "transcript.md"]:
        shutil.copy2(media / name, out / name)
    shutil.copy2(quiz_path, out / "quiz.json")
    (out / "img").mkdir(exist_ok=True)
    for name in ["lab-starter.png", "real-shell.png"]:
        src = images / name if (images / name).is_file() else en_module / "assets" / name
        shutil.copy2(src, out / "img" / name)
    webp(out / "img" / "lab-starter.png", out / "img" / "lab-starter.webp", 1100)
    n_slides = render_slides(media / "slides.pdf", out)

    # Video + subtitles (built by narrate_clips.sh / make_fr_media.py), then cut into the five parts.
    video, timings = media / "video.mp4", media / "audio/slide_timings.json"
    has_video, has_subs, has_parts, runtime, cues, durs, parts = video.is_file(), False, False, "", [], [], []
    if has_video:
        newest = max((media / f).stat().st_mtime for f in ["transcript.md", "slides.pptx"])
        if video.stat().st_mtime < newest:
            print(f"WARNING [{lang}]: video.mp4 is older than the slides — rebuild the video", file=sys.stderr)
        shutil.copy2(video, out / "video.mp4")
        if timings.is_file():
            durs = [float(d["duration"]) for d in json.loads(timings.read_text(encoding="utf-8"))]
            runtime = mmss(sum(durs))
            if len(durs) != n_slides:  # old audio of a deck that has since been rewritten (Stage 6 rebuilds it)
                print(f"WARNING [{lang}]: {len(durs)} timings for {n_slides} slides: the video is STALE, "
                      "no subtitles or parts are written. Rebuild the audio and video.", file=sys.stderr)
            else:
                cues = build_cues(repo, media)
                write_subtitles(cues, out)
                has_subs = has_parts = True
    else:
        print(f"NOTE [{lang}]: no video yet — the page shows a placeholder.")
    if has_parts:
        parts = build_parts(media, out, lang, durs, cues, n_slides, t["part_titles"])

    # Browser lab (French copy is translated).
    other_lab = ("../../fr/tools/initial-bipartition/index.html" if lang == "en"
                 else "../../../tools/initial-bipartition/index.html")
    copy_lab(repo, out, t, other_lab)
    if lang == "fr":
        translate_lab(out)

    # Page.
    titles = slide_titles(media)
    steps_en = steps_from_md(en_module / "assets/STEPS.md")
    if lang == "en":
        steps = steps_en
    else:
        fr_steps = json.loads((FR_ROOT / "walkthrough-steps.json").read_text(encoding="utf-8"))["steps"]
        if [s["file"] for s in fr_steps] != [s["file"] for s in steps_en]:
            die("i18n/fr/walkthrough-steps.json and the module's STEPS.md list different frames")
        steps = fr_steps
    (out / "img/steps").mkdir(parents=True, exist_ok=True)
    quiz = json.loads(quiz_path.read_text(encoding="utf-8"))
    if has_parts:
        video_html = player_html(parts, t, lang)
        downloads = f'<a class="btn" href="video.mp4" download>{t["dl_video"]}</a><a class="btn" href="subs.srt" download>{t["dl_subs"]}</a>'
        meta = (f'<p class="meta"><strong>{runtime}</strong> · {len(parts)} {t["meta_parts"]} · {n_slides} {t["meta_slides"]} · '
                f'{t["meta_narration"]}{t["meta_and_subs"]}</p>')
    elif has_video:
        track = (f'<track kind="subtitles" src="subs.vtt" srclang="{lang}" label="{t["subs_label"]}" default>'
                 if has_subs else "")
        video_html = (f'<video controls preload="metadata" poster="slides/poster.webp">'
                      f'<source src="video.mp4" type="video/mp4">{track}{t["video_fallback"]}</video>')
        downloads = f'<a class="btn" href="video.mp4" download>{t["dl_video"]}</a>' + (
            f'<a class="btn" href="subs.srt" download>{t["dl_subs"]}</a>' if has_subs else "")
        meta = (f'<p class="meta"><strong>{runtime}</strong> · {n_slides} {t["meta_slides"]} · '
                f'{t["meta_narration"]}{t["meta_and_subs"] if has_subs else ""}</p>')
    else:
        video_html = f'<div class="missing">{t["video_missing"]}</div>'
        downloads, meta = "", f'<p class="meta">{n_slides} {t["meta_slides"]}</p>'

    def title_of(i: int) -> str:
        return titles[i - 1] if i <= len(titles) else ""

    slides = "\n".join(
        f'<figure><a href="slides/{i:02d}.png"><img src="slides/thumb/{i:02d}.webp" loading="lazy" width="480" height="270" '
        f'alt="{t["slide_alt"]} {i}: {esc(title_of(i))}"></a>'
        f"<figcaption><b>{i:02d}</b>{esc(title_of(i))}</figcaption></figure>"
        for i in range(1, n_slides + 1)
    )
    files = "\n".join(f'<a href="{base}{f}" download><code>{Path(f).name}</code><small>{esc(d)}</small></a>'
                      for f, d in t["files"])
    fill = {k: v for k, v in t.items() if isinstance(v, str)}
    fill.update({
        "base": base,
        "slides_intro": t["slides_intro"].format(n=n_slides),
        "quiz_intro": t["quiz_intro"].format(n=len(quiz["items"])),
        "WALKTHROUGH": walkthrough_html(steps, images, out, t),
        "VIDEO": video_html, "DOWNLOADS": downloads, "META": meta, "SLIDES": slides,
        "LAB_ITEMS": "\n".join(f"<li>{esc(x)}</li>" for x in t["lab_items"]),
        "QUIZ_JSON": json.dumps(quiz, ensure_ascii=False).replace("</", "<\\/"),
        "EXAMPLES_HTML": render_markdown(examples_md),
        "EXAMPLE_FILES": files,
        "TRANSCRIPT": transcript_html(media / "transcript.md"),
    })
    page = (SRC / "index.html.tmpl").read_text(encoding="utf-8")
    page = re.sub(r"\{\{(\w+)\}\}", lambda m: fill[m.group(1)] if m.group(1) in fill else die(f"no text for {{{{{m.group(1)}}}}}"), page)
    (out / "index.html").write_text(page, encoding="utf-8")
    return {"slides": n_slides, "video": has_video, "subs": has_subs, "parts": parts}


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, type=Path, help="path to your eda-learning clone")
    ap.add_argument("--out", default=HERE / "docs", type=Path, help="output folder (default: docs/)")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    if not (repo / MODULE_REL / "transcript.md").is_file() or not (repo / TOOL_REL / "index.html").is_file():
        die(f"{repo} does not look like eda-learning with the Lab 02 patch applied")

    out = args.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copytree(SRC / "fonts", out / "fonts")
    (out / "page.css").write_text(fontface_css("fonts/") + (SRC / "page.css").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copy2(SRC / "quiz.js", out / "quiz.js")
    shutil.copy2(SRC / "player.js", out / "player.js")
    (out / "examples").mkdir()
    for f, _ in LANGS["en"]["files"]:  # code files are shared by both languages
        shutil.copy2(repo / MODULE_REL / f, out / f)

    report = {"en": build_language(repo, out, "en", ""), "fr": build_language(repo, out / "fr", "fr", "../")}
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file()) / 1e6
    for lang, r in report.items():
        print(f"[{lang}] {r['slides']} slides, video: {'yes' if r['video'] else 'no'}, subtitles: {'yes' if r['subs'] else 'no'}, "
              f"parts: {', '.join(mmss(p['seconds']) for p in r['parts']) or 'none'}")
    print(f"Built {out} ({size:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
