"""Shared helpers for the lesson-animator scripts: transcript → spoken sentences, anchors, pauses, ffmpeg.

Speech text follows the teacher's pipeline (.cursor/skills/module-slides/scripts/transcript_to_speech.py,
clean_narration_prose): when a teacher clone is given with --repo, its own function is imported so the
voice says exactly what the course video says. The fallback below copies its rules.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

SLIDE_HEADING = re.compile(r"^##\s+Slide\s+(\d+)\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)


def _fallback_clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"```[\w-]*\n.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("§", "Section ")
    text = re.sub(r"\s*[—–]\s*", ", ", text)
    text = re.sub(r"(?<=\w)\s*/\s*(?=\w)", " or ", text)
    return text.strip()


def cleaner(repo: Path | None):
    """Return the teacher's clean_narration_prose if the clone has it, else the copy above."""
    if repo:
        scripts = Path(repo) / ".cursor/skills/module-slides/scripts"
        if (scripts / "transcript_to_speech.py").is_file():
            sys.path.insert(0, str(scripts))
            try:
                from transcript_to_speech import clean_narration_prose  # type: ignore
                return clean_narration_prose
            except Exception as exc:  # pragma: no cover
                print(f"warning: could not import the teacher's speech cleaner ({exc}); using the copy", file=sys.stderr)
    return _fallback_clean


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    # split after . ! ? (and French « ? » spacing) followed by a space and a capital, digit or quote
    parts = re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-ÖØ-Ý0-9«\"“])", text)
    return [p.strip() for p in parts if p.strip()]


def slide_sentences(transcript: Path, first: int, last: int, repo: Path | None = None) -> list[dict]:
    """Spoken sentences of slides first..last (transcript '## Slide N' numbers), in order."""
    clean = cleaner(repo)
    src = Path(transcript).read_text(encoding="utf-8")
    heads = list(SLIDE_HEADING.finditer(src))
    out = []
    for i, m in enumerate(heads):
        n = int(m.group(1))
        if not first <= n <= last:
            continue
        body = src[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(src)]
        paras = []
        for block in body.split("\n\n"):
            block = block.strip()
            if not block or block.startswith("#"):
                continue
            paras.append(block)
        spoken = clean("\n\n".join(paras))
        for s in split_sentences(spoken):
            out.append({"slide": n, "text": s})
    if not out:
        raise SystemExit(f"no narration found for slides {first}-{last} in {transcript}")
    return out


def norm(w: str) -> str:
    w = unicodedata.normalize("NFD", w)
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w.lower())


def word_keys(w: str) -> list[str]:
    keys = [norm(w)]
    bits = re.split(r"['’]", w)
    if len(bits) > 1:
        keys.append(norm(bits[-1]))
    return keys


def find_anchor_sentence(sents: list[dict], anchor: dict, lang: str) -> int | None:
    """Index of the sentence holding the anchor's word (same matching as the engine)."""
    needle = anchor.get(lang)
    if needle is None:
        return None
    phrase, _, nth_txt = str(needle).partition("#")
    nth = int(nth_txt) if nth_txt else anchor.get("nth", 0)
    toks = [norm(t) for t in phrase.split() if norm(t)]
    hit = 0
    for i, s in enumerate(sents):
        if anchor.get("slide") is not None and s["slide"] != anchor["slide"]:
            continue
        words = s["text"].split()
        for k in range(len(words) - len(toks) + 1):
            if all(any(key.startswith(tk) for key in word_keys(words[k + j])) for j, tk in enumerate(toks)):
                if hit == nth:
                    return i
                hit += 1
    return None


def pause_plan(sents: list[dict], sb: dict | None, lang: str) -> list[float]:
    """Silence after each sentence. Rules (a person reading aloud to a learner):
    - 0.55 s between two sentences of the same slide;
    - +0.45 s when the next sentence starts a new slide (the picture changes);
    - 1.3 s after a question;
    - storyboard "pauses": [{"after": "@anchor" | "slide:N:end", "sec": 1.5}] override (anchor = the sentence holding it);
    - 2.0 s after the last sentence (room for the auto-paused question)."""
    p = sb.get("pausing", {}) if sb else {}
    base, scene, question, tail = p.get("between", 0.55), p.get("scene", 0.45), p.get("question", 1.3), p.get("tail", 2.0)
    gaps = []
    for i, s in enumerate(sents):
        g = base
        if i + 1 < len(sents) and sents[i + 1]["slide"] != s["slide"]:
            g += scene
        if s["text"].rstrip().endswith("?"):
            g = max(g, question)
        gaps.append(g)
    if gaps:
        gaps[-1] = tail
    for rule in (sb or {}).get("pauses", []):
        ref = rule["after"]
        idx = None
        if ref.startswith("@"):
            a = (sb.get("anchors") or {}).get(ref[1:])
            idx = find_anchor_sentence(sents, a, lang) if a else None
        elif ref.startswith("slide:"):
            n = int(ref.split(":")[1])
            ids = [i for i, s in enumerate(sents) if s["slide"] == n]
            idx = ids[-1] if ids else None
        if idx is None:
            print(f"warning: pause rule {rule} matches no sentence ({lang})", file=sys.stderr)
            continue
        gaps[idx] = float(rule["sec"])
    return gaps


def duration(path: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).decode())


def concat_with_pauses(clips: list[tuple[Path, float, float]], gaps: list[float], out: Path, rate: int = 24000) -> None:
    """clips = [(file, start, end)]; joins each clip slice then its gap of silence; writes AAC (m4a)."""
    args, filt, parts = ["ffmpeg", "-v", "error", "-y"], [], []
    srcs = {}
    for f, _, _ in clips:
        if str(f) not in srcs:
            srcs[str(f)] = len(srcs)
            args += ["-i", str(f)]
    for k, ((f, a, b), g) in enumerate(zip(clips, gaps)):
        seg = b - a
        filt.append(f"[{srcs[str(f)]}:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,aresample={rate},aformat=channel_layouts=mono,"
                    f"afade=t=in:d=0.01,afade=t=out:st={max(0.0, seg - 0.03):.3f}:d=0.03[s{k}]")
        filt.append(f"aevalsrc=0:d={g:.3f}:s={rate}:c=mono[g{k}]")
        parts += [f"[s{k}]", f"[g{k}]"]
    filt.append("".join(parts) + f"concat=n={len(parts)}:v=0:a=1[out]")
    subprocess.run(args + ["-filter_complex", ";".join(filt), "-map", "[out]", "-c:a", "aac", "-b:a", "96k", str(out)], check=True)


def load_json(p) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def parse_range(s: str) -> tuple[int, int]:
    a, _, b = s.partition("-")
    return int(a), int(b or a)


def _main() -> int:
    """python3 lessonlib.py <transcript.md> <first-last> [--repo <teacher clone>]: list the part's spoken sentences."""
    import argparse
    ap = argparse.ArgumentParser(description="List the spoken sentences of a part (what anchors are searched in).")
    ap.add_argument("transcript", type=Path)
    ap.add_argument("slides")
    ap.add_argument("--repo", type=Path)
    a = ap.parse_args()
    first, last = parse_range(a.slides)
    for i, s in enumerate(slide_sentences(a.transcript, first, last, a.repo), 1):
        print(f"{i:>3}  slide {s['slide']:>2}  {s['text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
