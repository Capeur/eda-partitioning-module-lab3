#!/usr/bin/env python3
"""Capture assets/lab-starter.png for transcript slide 16 after a few real learner actions.

    python3 -m http.server 8080 --directory <clone>/platform     # in another shell
    python3 capture_lab.py --module <clone>/courses/learn_partitioning/module01-03-initial-bipartition

French (the translated lab of the built site, served from docs/):
    python3 -m http.server 8090 --directory <site repo>/docs
    python3 capture_lab.py --lang fr --url http://127.0.0.1:8090/fr/tools/initial-bipartition/index.html \\
        --out <site repo>/i18n/fr/module01-03-initial-bipartition/assets/lab-starter.png

The teacher's capture_lab_snapshot.py only loads the page; this one runs random seed 3, greedy,
grow from A and grow from D on the tiny graph (so the log compares four cuts), then takes a
1280x1080 shot that starts at the challenge box, so the graph and the metrics are both in view.
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--module", type=Path, help="module dir (English: writes <module>/assets/lab-starter.png)")
ap.add_argument("--url", default="http://127.0.0.1:8080/tools/initial-bipartition/index.html")
ap.add_argument("--lang", choices=["en", "fr"], default="en")
ap.add_argument("--out", type=Path, help="output PNG (default: <module>/assets/lab-starter.png)")
args = ap.parse_args()
out = args.out or (args.module / "assets" / "lab-starter.png")
if not args.out and not args.module:
    ap.error("give --module or --out")
BUTTONS = {"en": ("Run random", "Run greedy"), "fr": ("Lancer l'aléatoire", "Lancer le glouton")}[args.lang]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 1080})
    pg.goto(args.url, wait_until="networkidle")
    pg.add_style_tag(content="html{scroll-behavior:auto!important}")
    pg.wait_for_selector("#lab-root canvas")
    btn = lambda t: pg.locator(f'#lab-root button:text-is("{t}")').first.click()  # noqa: E731
    pg.fill("#ib-seed", "3")
    btn(BUTTONS[0])
    btn(BUTTONS[1])
    pg.locator('#lab-root button.ib-grow:text-is("A")').click()
    pg.locator('#lab-root button.ib-grow:text-is("D")').click()
    top = pg.evaluate(  # the site header is sticky: keep the challenge box below it
        "document.querySelector('#lab-root .challenge').getBoundingClientRect().top + scrollY"
        " - document.querySelector('.site-header').offsetHeight - 16")
    pg.evaluate(f"scrollTo(0, {top})")
    pg.wait_for_timeout(400)
    out.parent.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=str(out))
    b.close()
print(f"Wrote {out}")
