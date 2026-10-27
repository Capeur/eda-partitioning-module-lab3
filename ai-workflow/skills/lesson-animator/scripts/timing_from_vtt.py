#!/usr/bin/env python3
"""Reuse an already narrated part (the site's parts/part-N.mp4 + part-N.vtt) for an animated lesson.

No new voice is made: the existing narration is cut at each sentence and joined again with designed pauses
(lessonlib.pause_plan). Word times inside a sentence are ESTIMATED from the subtitle text (by character
position), so a highlight can be a fraction of a second early or late; voice_build.py gives exact ones.

  python3 timing_from_vtt.py --transcript docs/transcript.md --slides 1-6 \
      --vtt docs/parts/part-1.vtt --audio docs/parts/part-1.mp4 --lang en \
      --storyboard storyboard.json --out-audio lesson-en.m4a --out-timing timing-en.json [--repo ../eda-learning-lab3]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lessonlib import concat_with_pauses, duration, load_json, norm, parse_range, pause_plan, slide_sentences  # noqa: E402


def read_vtt(path: Path) -> list[tuple[float, float, str]]:
    cues = []
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.strip().split("\n")
        m = next((re.match(r"(\d+):(\d+):([\d.]+)\s*-->\s*(\d+):(\d+):([\d.]+)", ln) for ln in lines if "-->" in ln), None)
        if not m:
            continue
        s = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
        e = int(m[4]) * 3600 + int(m[5]) * 60 + float(m[6])
        text = " ".join(ln for ln in lines[lines.index(next(l for l in lines if "-->" in l)) + 1:])
        cues.append((s, e, text))
    return cues


def vtt_words(cues) -> list[dict]:
    """Every subtitle word with an estimated start time (by character position inside its cue)."""
    out = []
    for s, e, text in cues:
        off, total = 0, max(1, len(text))
        for w in text.split():
            out.append({"w": w, "t": s + (e - s) * off / total, "n": norm(w), "cue_end": e})
            off += len(w) + 1
    return [w for w in out if w["n"]]


def align(sents: list[dict], words: list[dict]) -> list[tuple[int, int]]:
    """For each sentence, the [first, last] subtitle word indexes. Sequential, tolerant of small differences."""
    spans, j = [], 0
    for si, s in enumerate(sents):
        toks = [norm(w) for w in s["text"].split() if norm(w)]
        # find the sentence's first token at or after j (look a few words ahead)
        start = None
        for k in range(j, min(len(words), j + 25)):
            if words[k]["n"] == toks[0] or words[k]["n"].startswith(toks[0][:4]):
                start = k
                break
        if start is None:
            raise SystemExit(f"sentence {si + 1} (slide {s['slide']}) not found in the subtitles near word {j}: {s['text'][:70]!r}")
        end = min(len(words) - 1, start + len(toks) - 1)
        # tolerate one extra or missing word: snap the end to the last token if it is close
        for k in range(max(start, end - 3), min(len(words), end + 4)):
            if words[k]["n"] == toks[-1]:
                end = k
                break
        spans.append((start, end))
        j = end + 1
    matched = sum(1 for s, (a, b) in zip(sents, spans) if b - a + 1 == len([w for w in s["text"].split() if norm(w)]))
    print(f"aligned {len(sents)} sentences ({matched} with the exact word count)")
    return spans


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transcript", required=True, type=Path)
    ap.add_argument("--slides", required=True, help="transcript slide range of this part, e.g. 1-6")
    ap.add_argument("--vtt", required=True, type=Path)
    ap.add_argument("--audio", required=True, type=Path, help="part audio or video (its audio track is used)")
    ap.add_argument("--lang", required=True)
    ap.add_argument("--storyboard", type=Path, help="for pause rules (pausing, pauses)")
    ap.add_argument("--repo", type=Path, help="teacher clone, to use its exact speech cleaner")
    ap.add_argument("--out-audio", required=True, type=Path)
    ap.add_argument("--out-timing", required=True, type=Path)
    a = ap.parse_args()

    first, last = parse_range(a.slides)
    sents = slide_sentences(a.transcript, first, last, a.repo)
    words = vtt_words(read_vtt(a.vtt))
    spans = align(sents, words)
    sb = load_json(a.storyboard) if a.storyboard else None
    gaps = pause_plan(sents, sb, a.lang)
    total = duration(a.audio)

    starts = [max(0.0, words[s]["t"] - 0.05) for s, _ in spans]
    ends = starts[1:] + [total]
    clips, timing, t = [], [], 0.0
    for i, (s, (w0, w1)) in enumerate(zip(sents, spans)):
        a0, b0 = starts[i], ends[i]
        clips.append((a.audio, a0, b0))
        ws = [{"w": words[k]["w"], "t": round(t + (words[k]["t"] - a0), 3)} for k in range(w0, w1 + 1)]
        speech_end = min(b0, words[w1]["cue_end"])
        timing.append({"slide": s["slide"], "text": s["text"], "start": round(t + (words[w0]["t"] - a0), 3),
                       "end": round(t + (speech_end - a0), 3), "pause_after": gaps[i], "words": ws})
        t += (b0 - a0) + gaps[i]
    a.out_audio.parent.mkdir(parents=True, exist_ok=True)
    concat_with_pauses(clips, gaps, a.out_audio)
    real = duration(a.out_audio)
    out = {"lang": a.lang, "slides": [first, last], "source": "vtt", "words": "estimated",
           "duration": round(real, 3), "sentences": timing}
    a.out_timing.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.lang}: {len(sents)} sentences, {total:.1f} s -> {real:.1f} s with pauses ({sum(gaps):.1f} s of pauses)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
