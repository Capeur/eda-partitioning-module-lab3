#!/usr/bin/env python3
"""Playwright test of the built site (docs/), English and French pages.

    python3 -m http.server 8090 --directory docs        # from this repo's root, in another shell
    python3 tools/test_site.py [--base http://127.0.0.1:8090] [--teacher ../eda-learning-lab3]

Per language: no console error, no 404, no request outside the site (0 external requests, fonts included);
every image loads; 22 slides and 5 walkthrough frames; the walkthrough captions are the ones in STEPS.md
(English) or i18n/fr/walkthrough-steps.json (French); the video and its subtitle track answer 200 when present;
the quiz scores 8/8 when answered right and 0/8 when answered wrong; the language switch keeps #hash
(page and lab); the lab opens in the same language with no leftover English in the French one.
The lab's own challenges are tested by tools/test_lab_site.py.

The test Chromium cannot decode H.264, so the video is checked by its HTTP status, not by playing it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--base", default="http://127.0.0.1:8090")
ap.add_argument("--teacher", default=HERE.parent / "eda-learning-lab3", type=Path)
args = ap.parse_args()
BASE = args.base.rstrip("/")
MODULE = args.teacher / "courses/learn_partitioning/module01-03-initial-bipartition"

sys.path.insert(0, str(HERE))
import build_site  # noqa: E402  (steps_from_md: the same parser the build uses)

EN_STEPS = build_site.steps_from_md(MODULE / "assets/STEPS.md")
FR_STEPS = json.loads((HERE / "i18n/fr/walkthrough-steps.json").read_text(encoding="utf-8"))["steps"]
QUIZ = {"en": json.loads((MODULE / "quiz.json").read_text(encoding="utf-8")),
        "fr": json.loads((HERE / "i18n/fr/quiz.json").read_text(encoding="utf-8"))}
TXT = {  # words the page shows per language
    "en": {"prefix": "", "steps": EN_STEPS, "pass": "passed", "fail": "try again", "other": "Français",
           "lab_btn": "Open the lab", "leftover": []},
    "fr": {"prefix": "fr/", "steps": FR_STEPS, "pass": "réussi", "fail": "réessayez", "other": "English",
           "lab_btn": "Ouvrir le lab",
           "leftover": ["Click a node", "Run random", "Run greedy", "Pick one", "Challenges", "legal:", "cutsize:",
                        "balance:", "Reset workspace", "Clear split", "Show hint", "Next challenge", "Reveal best"]},
}

rows: list[tuple[str, str, bool]] = []


def check(lang: str, what: str, ok: bool, detail: str = "") -> None:
    rows.append((lang, what + (f" ({detail})" if detail and not ok else ""), bool(ok)))


def correct_index(item: dict) -> int:
    return (0 if item["answer"] else 1) if item["type"] == "true_false" else item["answer"]


with sync_playwright() as p:
    b = p.chromium.launch()
    for lang, t in TXT.items():
        pg = b.new_page(viewport={"width": 1280, "height": 2000})
        problems: list[str] = []
        pg.on("console", lambda m: m.type == "error" and problems.append(f"console: {m.text}"))
        pg.on("pageerror", lambda e: problems.append(f"page error: {e}"))
        # the video preload is cancelled when the test navigates away (this Chromium cannot decode H.264): not an error
        pg.on("requestfailed", lambda r: r.url.endswith(".mp4") and r.failure == "net::ERR_ABORTED"
              or problems.append(f"request failed: {r.url} {r.failure}"))
        pg.on("response", lambda r: r.status >= 400 and problems.append(f"HTTP {r.status}: {r.url}"))
        pg.on("request", lambda r: not r.url.startswith((BASE, "data:", "blob:")) and problems.append(f"external: {r.url}"))
        url = f"{BASE}/{t['prefix']}index.html"
        pg.goto(url, wait_until="networkidle")
        pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => { i.loading = 'eager'; })")
        pg.wait_for_load_state("networkidle")
        pg.wait_for_timeout(500)

        # --- page structure
        check(lang, "html lang attribute", pg.get_attribute("html", "lang") == lang)
        check(lang, "22 slide thumbnails", pg.locator(".slides figure").count() == 22, str(pg.locator(".slides figure").count()))
        broken = pg.evaluate("[...document.images].filter(i => !i.naturalWidth).map(i => i.src)")
        check(lang, "every image loads", not broken, str(broken))
        fonts = pg.evaluate("document.fonts.check('16px \"Source Sans 3\"') && document.fonts.check('700 16px Fraunces')")
        check(lang, "self-hosted fonts load", fonts)
        check(lang, "20 transcript sections", pg.locator("#transcript h3").count() == 20, str(pg.locator("#transcript h3").count()))

        # --- walkthrough: STEPS.md captions (EN) / French captions (FR)
        figs = pg.locator(".walk-step")
        check(lang, "5 walkthrough frames", figs.count() == 5, str(figs.count()))
        for i, st in enumerate(t["steps"]):
            if i >= figs.count():
                break
            cap = figs.nth(i).locator("figcaption span").inner_text().strip()
            title = figs.nth(i).locator("figcaption b").inner_text()
            src = figs.nth(i).locator("img").get_attribute("src")
            bullets = figs.nth(i).locator("li").all_inner_texts()
            ok = (cap == st["caption"] and st["title"] in title and Path(src).stem == Path(st["file"]).stem
                  and bullets == st["bullets"])
            check(lang, f"walkthrough step {i + 1} = {'STEPS.md' if lang == 'en' else 'walkthrough-steps.json'}", ok, cap[:40])
        # same pictures as the slides' source: the PNG next to the thumbnail is the course frame (EN) or the French one
        for i, st in enumerate(t["steps"]):
            png = pg.request.get(f"{BASE}/{t['prefix']}img/steps/{st['file']}")
            check(lang, f"frame {st['file']} downloads", png.status == 200 and len(png.body()) > 10_000)

        # --- video + subtitles
        video = pg.locator("video source")
        if video.count():
            r = pg.request.get(f"{BASE}/{t['prefix']}" + video.first.get_attribute("src"))
            check(lang, "video.mp4 answers 200", r.status == 200 and len(r.body()) > 100_000)
            tracks = pg.locator("video track")
            if tracks.count():
                tr = pg.request.get(f"{BASE}/{t['prefix']}" + tracks.first.get_attribute("src"))
                check(lang, "subtitle track answers 200", tr.status == 200 and "-->" in tr.text())
            print(f"  note [{lang}]: video present, subtitle tracks: {tracks.count()}")
        else:
            print(f"  note [{lang}]: no video on the page (placeholder)")
        for f in ("slides.pdf", "slides.pptx", "transcript.md", "quiz.json"):
            check(lang, f"download {f}", pg.request.get(f"{BASE}/{t['prefix']}{f}").status == 200)
        # the five example files are shared by both languages: follow the links the page itself shows
        links = pg.eval_on_selector_all(".files a", "as => as.map(a => a.href)")
        names = sorted(Path(l).name for l in links)
        want = ["bridge_graph.json", "initial_bipartition_check.py", "star_graph.json", "tie_graph.json", "tiny_graph.json"]
        check(lang, "5 example files listed", names == want, str(names))
        for l in links:
            check(lang, f"download {Path(l).name} (page link)", pg.request.get(l).status == 200, l)

        # --- quiz: right answers give 8/8, wrong ones 0/8
        quiz = QUIZ[lang]
        n = len(quiz["items"])
        for label, pick in (("right", lambda it: correct_index(it)), ("wrong", lambda it: 1 - correct_index(it) if it["type"] == "true_false" else (correct_index(it) + 1) % len(it["choices"]))):
            pg.locator("#quiz-root button:has-text('Reset'), #quiz-root button:has-text('Recommencer')").first.click()
            for i, item in enumerate(quiz["items"]):
                pg.locator(f"#quiz-root input[name=q{i}]").nth(pick(item)).check()
            pg.locator("#quiz-root button.primary").click()
            score = pg.inner_text("#quiz-root .score")
            want = f"{n} / {n}" if label == "right" else f"0 / {n}"
            word = t["pass"] if label == "right" else t["fail"]
            check(lang, f"quiz {label} answers -> {want}", score.startswith(want) and word in score, score)
        check(lang, "quiz text is in the page language", quiz["items"][0]["prompt"][:30] in pg.inner_text("#quiz-root"))

        # --- language switch keeps the hash (page)
        pg.goto(f"{url}#quiz", wait_until="networkidle")
        pg.locator("a.lang-switch").click()
        pg.wait_for_load_state("networkidle")
        want_url = f"{BASE}/{'' if lang == 'fr' else 'fr/'}index.html#quiz"
        check(lang, "switch keeps #hash on the page", pg.url == want_url, pg.url)
        check(lang, "switch lands on the other language", pg.get_attribute("html", "lang") == ("en" if lang == "fr" else "fr"))

        # --- lab: opens in the same language; its switch goes to the other lab
        pg.goto(url, wait_until="networkidle")
        pg.locator(f"a.btn.primary:has-text('{t['lab_btn']}')").click()
        pg.wait_for_selector("#lab-root canvas")
        check(lang, "lab opens in the same language", pg.get_attribute("html", "lang") == lang)
        text = pg.inner_text("body")
        left = [w for w in t["leftover"] if w in text]
        check(lang, "no English left in the French lab" if lang == "fr" else "lab shows its English text",
              (not left) if lang == "fr" else "Challenges" in text, str(left))
        n_opts = pg.locator("#lab-chal-sel option").count()
        check(lang, "10 challenges listed", n_opts == 10, str(n_opts))
        lab_url = pg.url
        pg.goto(lab_url + "#top", wait_until="networkidle")
        pg.locator(".site-nav a[hreflang]").click()
        pg.wait_for_selector("#lab-root canvas")
        check(lang, "lab switch goes to the other lab", pg.get_attribute("html", "lang") == ("en" if lang == "fr" else "fr"))
        pg.locator(".site-nav a", has_text=re.compile("Lab 0?3|Accueil du Lab 03|Lab 03 home")).first.click()
        pg.wait_for_load_state("networkidle")
        check(lang, "lab header links back to the page", pg.locator("#walkthrough").count() == 1)

        check(lang, "0 console errors, 404s or external requests", not problems, "; ".join(problems[:4]))
        pg.close()
    b.close()

# --- static checks on the built files
docs = HERE / "docs"
for name in ("tools/initial-bipartition", "fr/tools/initial-bipartition"):
    d = docs / name
    check("static", f"{name} has no tests/ folder", d.is_dir() and not (d / "tests").exists() and not list(d.glob("test_*")))
    check("static", f"{name} has the model file", (d / "initial-bipartition-lab-model.js").is_file())
ext = []
for f in list(docs.rglob("*.css")) + list(docs.rglob("*.js")) + list(docs.rglob("*.html")):
    s = f.read_text(encoding="utf-8", errors="ignore")
    ext += [f"{f.relative_to(docs)}: {m}" for m in re.findall(r"@import\s+url\(\s*[\"']?https?://[^)]+|<(?:script|link|img)[^>]+(?:src|href)=[\"']https?://[^\"']+|fonts\.(?:googleapis|gstatic)\.com", s)
            if "rel=\"alternate\"" not in m]
check("static", "no external stylesheet, script, image or font reference in docs/", not ext, "; ".join(ext[:3]))

w = max(len(r[1]) for r in rows)
bad = [r for r in rows if not r[2]]
for lang, what, ok in rows:
    print(f"{lang:6} {what.ljust(w)}  {'ok' if ok else 'FAIL'}")
print(f"\n{len(rows)} checks, {len(bad)} failed")
sys.exit(1 if bad else 0)
