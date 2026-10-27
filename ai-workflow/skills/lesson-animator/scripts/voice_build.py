#!/usr/bin/env python3
"""Make the narration of one lesson part with edge-tts: one clip per sentence, exact word timings, designed pauses.

  python3 voice_build.py --transcript courses/.../transcript.md --slides 1-6 --lang en \
      --voice en-US-AndrewMultilingualNeural --rate=-4% --storyboard storyboard.json \
      --workdir .cache/voice --out-audio lesson-en.m4a --out-timing timing-en.json [--repo .]

Why per sentence: the pauses between sentences are then exact (lessonlib.pause_plan + storyboard "pauses"),
and each clip carries edge-tts word boundaries, so every word-anchored animation lands on the word.

Network behaviour (edge-tts needs speech.platform.bing.com; in mainland China use a VPN):
- every sentence prints a line, so a stall is visible at once;
- each request has a timeout and up to --tries attempts; a sentence that keeps failing stops the run with
  a clear message (switch VPN server, then run the same command again);
- finished sentences are cached in --workdir by text + voice + rate, so a rerun only makes what is missing.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import inspect
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lessonlib import concat_with_pauses, duration, load_json, parse_range, pause_plan, slide_sentences  # noqa: E402

TICKS = 10_000_000  # edge-tts offsets are in 100-nanosecond units


async def synth(text: str, voice: str, rate: str, out: Path, timeout: float) -> list[dict]:
    import edge_tts  # imported here so --help works without it

    params = inspect.signature(edge_tts.Communicate.__init__).parameters
    kw = {"rate": rate}
    if "boundary" in params:            # edge-tts >= 7.1 sends sentence boundaries unless asked for words
        kw["boundary"] = "WordBoundary"
    if "receive_timeout" in params:
        kw["receive_timeout"] = int(timeout)
    if "connect_timeout" in params:
        kw["connect_timeout"] = 15
    com = edge_tts.Communicate(text, voice, **kw)
    words, audio = [], bytearray()

    async def run():
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"w": chunk["text"], "t": chunk["offset"] / TICKS, "d": chunk["duration"] / TICKS})

    await asyncio.wait_for(run(), timeout=timeout + 15)
    if not audio:
        raise RuntimeError("no audio received")
    out.write_bytes(bytes(audio))
    return words


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transcript", required=True, type=Path)
    ap.add_argument("--slides", required=True, help="transcript slide range of this part, e.g. 1-6")
    ap.add_argument("--lang", required=True)
    ap.add_argument("--voice", required=True, help="e.g. en-US-AndrewMultilingualNeural, fr-FR-VivienneMultilingualNeural")
    ap.add_argument("--rate", default="+0%", help='speaking rate for edge-tts, e.g. "-4%%" (write --rate=-4%%)')
    ap.add_argument("--storyboard", type=Path, help="for pause rules (pausing, pauses)")
    ap.add_argument("--repo", type=Path, help="teacher clone, to use its exact speech cleaner")
    ap.add_argument("--workdir", type=Path, default=Path(".cache/voice"))
    ap.add_argument("--timeout", type=float, default=40)
    ap.add_argument("--tries", type=int, default=3)
    ap.add_argument("--out-audio", required=True, type=Path)
    ap.add_argument("--out-timing", required=True, type=Path)
    a = ap.parse_args()

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        raise SystemExit("edge-tts is not installed: pip install edge-tts (version 7.1 or newer gives word timings)")

    first, last = parse_range(a.slides)
    sents = slide_sentences(a.transcript, first, last, a.repo)
    sb = load_json(a.storyboard) if a.storyboard else None
    gaps = pause_plan(sents, sb, a.lang)
    a.workdir.mkdir(parents=True, exist_ok=True)

    clips, timing, t = [], [], 0.0
    for i, s in enumerate(sents):
        key = hashlib.sha1(f"{a.voice}|{a.rate}|{s['text']}".encode()).hexdigest()[:16]
        mp3, meta = a.workdir / f"{key}.mp3", a.workdir / f"{key}.json"
        label = f"[{i + 1:>2}/{len(sents)}] slide {s['slide']:>2}"
        if mp3.is_file() and meta.is_file():
            words = json.loads(meta.read_text(encoding="utf-8"))
            print(f"{label} cached   {s['text'][:60]}", flush=True)
        else:
            for attempt in range(1, a.tries + 1):
                t0 = time.time()
                try:
                    words = asyncio.run(synth(s["text"], a.voice, a.rate, mp3, a.timeout))
                    meta.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
                    print(f"{label} {time.time() - t0:5.1f}s   {s['text'][:60]}", flush=True)
                    break
                except Exception as exc:  # network stalls show up here instead of hanging
                    print(f"{label} attempt {attempt} failed after {time.time() - t0:.0f}s: {type(exc).__name__}: {exc}", flush=True)
                    mp3.unlink(missing_ok=True)
                    if attempt == a.tries:
                        raise SystemExit("edge-tts keeps failing: check the VPN (switch server), then run the same command "
                                         "again; finished sentences are cached and will not be remade.")
                    time.sleep(3 * attempt)
        if not words:
            print(f"{label} warning: no word timings (edge-tts older than 7.1?); estimating", flush=True)
        d = duration(mp3)
        clips.append((mp3, 0.0, d))
        if words:
            ws = [{"w": w["w"], "t": round(t + w["t"], 3)} for w in words]
            speech_end = t + words[-1]["t"] + words[-1].get("d", 0.3)
        else:  # fall back to character-position estimates
            ws, off = [], 0
            for w in s["text"].split():
                ws.append({"w": w, "t": round(t + d * off / max(1, len(s["text"])), 3)})
                off += len(w) + 1
            speech_end = t + d
        timing.append({"slide": s["slide"], "text": s["text"], "start": round(ws[0]["t"], 3), "end": round(min(speech_end, t + d), 3),
                       "pause_after": gaps[i], "words": ws})
        t += d + gaps[i]

    a.out_audio.parent.mkdir(parents=True, exist_ok=True)
    concat_with_pauses(clips, gaps, a.out_audio)
    real = duration(a.out_audio)
    out = {"lang": a.lang, "slides": [first, last], "source": "edge-tts", "voice": a.voice, "rate": a.rate,
           "words": "exact" if all(len(x["words"]) for x in timing) else "partly estimated",
           "duration": round(real, 3), "sentences": timing}
    a.out_timing.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.lang}: {len(sents)} sentences, {real:.1f} s ({sum(gaps):.1f} s of pauses) -> {a.out_audio}, {a.out_timing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
