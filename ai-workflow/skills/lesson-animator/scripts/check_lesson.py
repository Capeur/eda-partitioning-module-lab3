#!/usr/bin/env python3
"""Check built lesson pages and save a contact sheet per page.

  python3 check_lesson.py build/en/index.html build/fr/index.html --sheets build/check

Errors (exit code 1): storyboard anchors that do not resolve, claims that the lab rules contradict,
windows that end before they start, page errors.
Warnings (exit 1 only with --strict):
  - a move cut short: two keys of one track closer than the move takes (pose 1.1 s, camera 1.3 s, ...)
  - text on screen for less than --min-text seconds
  - text over text, or text over a node (sampled every 0.5 s and after every key)
  - a frame slower than 8 ms of script on a CPU slowed 6x
Needs: pip install playwright pillow; python3 -m playwright install chromium
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


def overlap(a, b) -> float:
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return max(0.0, w) * max(0.0, h)


async def check_page(pw, page_path: Path, sheets: Path | None, min_text: float, perf: bool) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    b = await pw.chromium.launch()
    pg = await b.new_page(viewport={"width": 1280, "height": 1000})
    page_errors = []
    pg.on("pageerror", lambda e: page_errors.append(str(e)))
    await pg.goto(page_path.resolve().as_uri())
    await pg.wait_for_function("window.__lesson !== undefined", timeout=10000)
    await pg.wait_for_timeout(300)
    L = await pg.evaluate("""() => { const x = window.__lesson; return { errors: x.errors, claims: x.claims, tracks: x.tracks,
        move: x.moveSeconds, overlays: x.overlays, duration: x.duration, lang: x.lang, sentences: x.sentences, question: x.question }; }""")
    errs += [f"{e}" for e in L["errors"]]
    errs += [f"page error: {e}" for e in page_errors]
    ok_claims = sum(1 for c in L["claims"] if c["ok"])
    print(f"  claims: {ok_claims}/{len(L['claims'])} match the lab rules")

    # 1. moves cut short
    for name, keys in L["tracks"].items():
        need = L["move"].get(name, 1.0)
        for (t0, r0), (t1, r1) in zip(keys, keys[1:]):
            if 0 < t1 - t0 < need * 0.9:
                warns.append(f"{name}: '{r1}' at {t1:.2f}s starts {t1 - t0:.2f}s after '{r0}' (the move takes {need}s): "
                             f"add a pause after that sentence, or move one key")
    # 2. short text
    for o in L["overlays"]:
        if o["b"] < 1e8 and o["b"] - o["a"] < min_text:
            warns.append(f"text '{o['label']}' is on screen {o['b'] - o['a']:.2f}s (from {o['a']:.2f}s); keep it at least {min_text}s")
    # 3. overlaps
    times = set()
    for o in L["overlays"]:
        end = min(o["b"], L["duration"])
        for t in (o["a"] + 0.6, (o["a"] + end) / 2, end - 0.4):
            if o["a"] < t < end:
                times.add(round(t, 2))
    for keys in L["tracks"].values():
        for t, _ in keys:
            times.add(round(t + 1.4, 2))
    t = 0.0
    while t < L["duration"]:
        times.add(round(t, 2)); t += 0.5
    seen = set()
    for t in sorted(times):
        if t > L["duration"]:
            continue
        bx = await pg.evaluate(f"(() => {{ window.__lesson.render({t}); return window.__lesson.boxes(); }})()")
        boxes = bx["boxes"]
        texts = [x for x in boxes if x["kind"] == "overlay"]
        nodes = [x for x in boxes if x["kind"] == "node"]
        for i, a in enumerate(texts):
            if a["x"] < -2 or a["y"] < -2 or a["x"] + a["w"] > bx["stage"]["w"] + 2 or a["y"] + a["h"] > bx["stage"]["h"] + 2:
                k = ("out", a["label"])
                if k not in seen:
                    seen.add(k); warns.append(f"{t:6.2f}s text '{a['label']}' runs off the stage")
            for c in texts[i + 1:]:
                ov = overlap(a, c)
                if ov > 0.04 * min(a["w"] * a["h"], c["w"] * c["h"]):
                    k = ("tt", a["label"], c["label"])
                    if k not in seen:
                        seen.add(k); warns.append(f"{t:6.2f}s text over text: '{a['label']}' and '{c['label']}'")
            for n in nodes:
                if overlap(a, n) > 0.15 * n["w"] * n["h"]:
                    k = ("tn", a["label"], n["label"])
                    if k not in seen:
                        seen.add(k); warns.append(f"{t:6.2f}s text '{a['label']}' covers node {n['label']}")
    # 4. speed on a slow machine
    if perf:
        cdp = await pg.context.new_cdp_session(pg)
        await cdp.send("Emulation.setCPUThrottlingRate", {"rate": 6})
        r = await pg.evaluate("""() => { const L = window.__lesson, T = [];
            for (let t = 0; t < L.duration; t += 0.25) { const a = performance.now(); L.render(t); T.push(performance.now() - a); }
            T.sort((x, y) => x - y); return { med: T[T.length >> 1], p95: T[Math.floor(T.length * 0.95)], max: T[T.length - 1] }; }""")
        await cdp.send("Emulation.setCPUThrottlingRate", {"rate": 1})
        print(f"  speed (CPU slowed 6x): script per frame median {r['med']:.2f} ms, 95% under {r['p95']:.2f} ms, worst {r['max']:.2f} ms")
        if r["p95"] > 8:
            warns.append(f"slow frames on a slow CPU: 95% of frames under {r['p95']:.1f} ms (aim for 8 ms)")
    # 5. contact sheet
    if sheets:
        from PIL import Image, ImageDraw
        sheets.mkdir(parents=True, exist_ok=True)
        pick = sorted({round(o["a"] + 0.9, 2) for o in L["overlays"] if o["a"] + 0.9 < min(o["b"], L["duration"])})
        if len(pick) > 32:
            step = len(pick) / 32
            pick = [pick[int(i * step)] for i in range(32)]
        stage = await pg.query_selector(".stage")
        await pg.evaluate("window.__lesson.setRecording(true)")  # no colour fades: each shot shows the settled picture
        ims = []
        for t in pick:
            await pg.evaluate(f"window.__lesson.render({t})")
            await pg.wait_for_timeout(60)
            f = sheets / f"_{L['lang']}_{t:07.2f}.png"
            await stage.screenshot(path=str(f))
            im = Image.open(f).convert("RGB"); im = im.resize((im.width // 2, im.height // 2))
            ImageDraw.Draw(im).text((8, im.height - 18), f"{t:.1f}s", fill=(220, 0, 0))
            ims.append(im); f.unlink()
        if ims:
            w, h = ims[0].size; cols = 4; rows = (len(ims) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * w, rows * h), "white")
            for i, im in enumerate(ims):
                sheet.paste(im, ((i % cols) * w, (i // cols) * h))
            out = sheets / f"sheet-{L['lang']}.png"
            sheet.save(out)
            print(f"  contact sheet: {out} ({len(ims)} frames, one just after each text appears)")
    await b.close()
    print(f"  {L['lang']}: {L['duration']:.1f} s, {len(L['sentences'])} sentences, {len(L['overlays'])} texts, question at "
          f"{L['question']:.1f}s" if L["question"] is not None else "")
    return errs, warns


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="+", type=Path)
    ap.add_argument("--sheets", type=Path, help="folder for the contact sheets")
    ap.add_argument("--min-text", type=float, default=2.0)
    ap.add_argument("--no-perf", action="store_true")
    ap.add_argument("--strict", action="store_true", help="warnings also fail")
    a = ap.parse_args()
    from playwright.async_api import async_playwright
    total_e = total_w = 0
    async with async_playwright() as pw:
        for p in a.pages:
            print(f"== {p}")
            e, w = await check_page(pw, p, a.sheets, a.min_text, not a.no_perf)
            for x in e:
                print(f"  ERROR   {x}")
            for x in w:
                print(f"  warning {x}")
            if not e and not w:
                print("  no problems")
            total_e += len(e); total_w += len(w)
    print(f"\n{total_e} error(s), {total_w} warning(s)")
    return 1 if total_e or (a.strict and total_w) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
