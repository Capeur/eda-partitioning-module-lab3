#!/usr/bin/env python3
"""French walkthrough frames (assets/steps/NN-*.png) for the French deck of Lab 03.

    python3 -m http.server 8081 --bind 127.0.0.1 --directory wt-platform &     # the scratch viewer (patch_walkthrough.py)
    python3 capture_fr_frames.py --steps <site repo>/i18n/fr/walkthrough-steps.json \\
        --out <site repo>/i18n/fr/module01-03-initial-bipartition/assets/steps

The English viewer draws the graph; this script swaps its text for the French captions before each shot
(same 1100x900 viewport and #walk-frame element as the teacher's capture_algorithm_walkthrough.py, so the
frames have the same size as the English ones). Numbers and file names must match the English frames.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--steps", required=True, type=Path, help="walkthrough-steps.json (French captions)")
ap.add_argument("--out", required=True, type=Path)
ap.add_argument("--base", default="http://127.0.0.1:8081/tools/algorithm-walkthrough")
ap.add_argument("--algo", default="initial-bipartition")
args = ap.parse_args()
data = json.loads(args.steps.read_text(encoding="utf-8"))
args.out.mkdir(parents=True, exist_ok=True)
n = len(data["steps"])

SWAP = """([d, st, i, n]) => {
  const f = document.getElementById('walk-frame');
  f.querySelector('.walk-banner .algo').textContent = d.algo;
  f.querySelector('.walk-banner h1').textContent = st.title;
  const meta = f.querySelector('.step-meta');
  meta.textContent = meta.textContent.replace(/^Step \\d+ \\/ \\d+/, `${d.step_word} ${i} / ${n}`);
  f.querySelector('.walk-explain h2').textContent = d.explanation;
  f.querySelector('.walk-explain .caption').textContent = st.caption;
  const lis = f.querySelectorAll('.walk-explain li');
  if (lis.length !== st.bullets.length) throw new Error('bullet count differs from the English frame');
  st.bullets.forEach((b, k) => { lis[k].textContent = b; });
  if (st.metrics) f.querySelector('.walk-metrics').textContent = st.metrics.join('\\n');
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1100, "height": 900})
    for i, st in enumerate(data["steps"], 1):
        page.goto(f"{args.base}/?algo={args.algo}&step={i}", wait_until="networkidle")
        page.wait_for_selector("#walk-frame[data-ready='1']")
        page.wait_for_timeout(300)
        page.evaluate(SWAP, [data, st, i, n])
        page.locator("#walk-frame").screenshot(path=str(args.out / st["file"]))
        print("wrote", args.out / st["file"])
    b.close()
