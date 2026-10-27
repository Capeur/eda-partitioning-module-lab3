#!/usr/bin/env python3
"""Record a built lesson page to an MP4 (for YouTube, a download, or the teacher's video folder).

  python3 record_mp4.py build/en/index.html --audio build/lesson-en.m4a --out lesson-part1-en.mp4 [--fps 30] [--width 1920]

The page is stepped frame by frame (window.__lesson.render(t)), so the video matches the page exactly,
whatever the speed of the machine; the question card is shown but the video does not stop at it.
Captions are not burned in: pass --vtt to add them as a subtitle track (players can switch them on).
A 2-minute part at 30 fps is about 3,700 screenshots: count a few minutes.
"""
from __future__ import annotations

import argparse
import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path


async def frames(page: Path, out_dir: Path, fps: int, width: int, start: float, end: float | None) -> float:
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        scale = width / 960
        pg = await b.new_page(viewport={"width": 1000, "height": 800}, device_scale_factor=scale)
        await pg.goto(page.resolve().as_uri())
        await pg.wait_for_function("window.__lesson !== undefined")
        dur = await pg.evaluate("window.__lesson.duration")
        await pg.evaluate("window.__lesson.setRecording(true)")
        # stage at exactly 960 css px wide so one css px = one stage unit
        await pg.add_style_tag(content=".wrap{max-width:none;width:960px;margin:0} body{padding:0} .stage{width:960px}")
        stage = await pg.query_selector(".stage")
        t, i, stop = start, 0, min(dur, end) if end else dur
        while t <= stop:
            await pg.evaluate(f"window.__lesson.render({t:.4f})")
            await stage.screenshot(path=str(out_dir / f"{i:06d}.png"))
            i += 1
            t = start + i / fps
            if i % (fps * 10) == 0:
                print(f"  {t:6.1f}s / {stop:.1f}s", flush=True)
        await b.close()
    return stop - start


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", type=Path)
    ap.add_argument("--audio", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--vtt", type=Path, help="subtitle track to add (not burned in)")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, help="stop early (for a quick test)")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is needed")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        length = asyncio.run(frames(a.page, tmp, a.fps, a.width, a.start, a.end))
        cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(a.fps), "-i", str(tmp / "%06d.png"),
               "-ss", f"{a.start:.3f}", "-t", f"{length:.3f}", "-i", str(a.audio)]
        if a.vtt:
            cmd += ["-i", str(a.vtt)]
        cmd += ["-map", "0:v", "-map", "1:a"] + (["-map", "2:s", "-c:s", "mov_text"] if a.vtt else [])
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(a.out)]
        subprocess.run(cmd, check=True)
    print(f"{a.out} ({a.out.stat().st_size / 1e6:.1f} MB, {length:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
