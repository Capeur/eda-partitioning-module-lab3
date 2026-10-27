#!/usr/bin/env python3
"""Browser test of the BUILT site's lab, in English and French (adapted from the course's
platform/tools/initial-bipartition/tests/test_lab_playwright.py: same learner actions and cases, with
the button texts, the PASS word and the metrics labels of each language).

    python3 -m http.server 8090 --directory docs          # from this repo's root, in another shell
    python3 tools/test_lab_site.py [--base http://127.0.0.1:8090] [--lang en|fr|both] [--headed]

Every challenge must pass when solved and fail on wrong work, page load, a start button, the reveal and an
edit after a start; the side holding A must be drawn blue; no console error, failed request or request
outside the site. Needs: pip install playwright && python3 -m playwright install chromium
"""
from __future__ import annotations

import argparse
import sys

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--base", default="http://127.0.0.1:8090")
ap.add_argument("--lang", choices=["en", "fr", "both"], default="both")
ap.add_argument("--headed", action="store_true")
args = ap.parse_args()

# what the page says in each language (the lab's button texts, the PASS word, two metrics lines)
LANGS = {
    "en": {"random": "Run random", "greedy": "Run greedy", "hand": "Grow by hand", "reveal": "Reveal best split (study)",
           "clear": "Clear split", "reset": "Reset workspace", "pass": "PASS", "empty": "split: —",
           "blue": lambda s, extra="": f"blue = side {s}{extra}", "has": lambda n: f" (has {n})"},
    "fr": {"random": "Lancer l'aléatoire", "greedy": "Lancer le glouton", "hand": "Croissance à la main",
           "reveal": "Révéler la meilleure partition (révision)", "clear": "Effacer la partition",
           "reset": "Réinitialiser", "pass": "RÉUSSI", "empty": "partition : —",
           "blue": lambda s, extra="": f"bleu = côté {s}{extra}", "has": lambda n: f" (contient {n})"},
}
L = LANGS["en"]

# ---------------- learner actions ----------------


def btn(pg, text):
    pg.locator(f'#lab-root button:text-is("{text}")').first.click()


def click_node(pg, n, times=1):
    # screen position from the same layout fit the lab uses
    x, y = pg.evaluate(
        """async (n) => {
          const { fitGraphLayout } = await import("../../assets/canvas-hires.js");
          const M = await import("./initial-bipartition-lab-model.js");
          const c = document.querySelector("#lab-root canvas");
          const key = document.querySelector("#ib-graph").value;
          const { layout } = fitGraphLayout(M.GRAPHS[key].layout, c.clientWidth, c.clientHeight);
          const r = c.getBoundingClientRect();
          return [r.left + layout[n].x, r.top + layout[n].y];
        }""",
        n,
    )
    for _ in range(times):
        pg.mouse.click(x, y)


def node_colour(pg, n):
    """'blue', 'green', 'grey' or the raw rgb, sampled inside node n (left of its letter)."""
    rgb = pg.evaluate(
        """async (n) => {
          const { fitGraphLayout } = await import("../../assets/canvas-hires.js");
          const M = await import("./initial-bipartition-lab-model.js");
          const c = document.querySelector("#lab-root canvas");
          const key = document.querySelector("#ib-graph").value;
          const { layout, nodeR } = fitGraphLayout(M.GRAPHS[key].layout, c.clientWidth, c.clientHeight);
          const k = c.width / c.clientWidth;
          const d = c.getContext("2d").getImageData(Math.round((layout[n].x - nodeR * 0.65) * k), Math.round(layout[n].y * k), 1, 1).data;
          return [d[0], d[1], d[2]];
        }""",
        n,
    )
    names = {"blue": (0x1D, 0x4E, 0xD8), "green": (0x0F, 0x6B, 0x5C), "grey": (0x94, 0xA3, 0xB8)}
    for name, ref in names.items():
        if all(abs(a - b) <= 6 for a, b in zip(rgb, ref)):
            return name
    return tuple(rgb)


def build(side0, side1):
    """From an all-grey split: one click puts a node on side 0, two clicks on side 1."""
    def act(pg):
        for n in side0:
            click_node(pg, n, 1)
        for n in side1:
            click_node(pg, n, 2)
    return act


def flips(*nodes):
    def act(pg):
        for n in nodes:
            click_node(pg, n)
    return act


def grow(start):
    return lambda pg: pg.locator(f'#lab-root button.ib-grow:text-is("{start}")').click()


def grow_all(nodes, last):
    def act(pg):
        for n in nodes:
            grow(n)(pg)
        grow(last)(pg)
    return act


def rand(*seeds):
    def act(pg):
        for s in seeds:
            pg.fill("#ib-seed", str(s))
            btn(pg, L["random"])
    return act


def hand_grow(*order):
    def act(pg):
        btn(pg, L["hand"])
        for n in order:
            click_node(pg, n)
    return act


greedy = lambda pg: btn(pg, L["greedy"])  # noqa: E731
reveal = lambda pg: btn(pg, L["reveal"])  # noqa: E731
clear = lambda pg: btn(pg, L["clear"])  # noqa: E731
nothing = lambda pg: None  # noqa: E731


def seq(*acts):
    def act(pg):
        for a in acts:
            a(pg)
    return act


# ---------------- cases: (challenge, label, actions, expected PASS?) ----------------
TINY, SIX = "ABCDE", "ABCDEF"
CASES = {
    "two-sides": [
        ("build AB|CDE by hand", build("AB", "CDE"), True),
        ("page load", nothing, False),
        ("1|4 split (illegal)", build("A", "BCDE"), False),
        ("one node left grey", build("AB", "CD"), False),
        ("Run greedy button", greedy, False),
        ("reveal (study)", reveal, False),
    ],
    "hand-cut-3": [
        ("build ABC|DE by hand", build("ABC", "DE"), True),
        ("page load", nothing, False),
        ("build AB|CDE (cut 5)", build("AB", "CDE"), False),
        ("Grow from D button (cut 3)", grow("D"), False),
        ("reveal (study)", reveal, False),
        ("reveal, then flip C twice", seq(reveal, flips("C", "C")), False),
    ],
    "grow-d-cut-3": [
        ("grow by hand D, E", hand_grow("D", "E"), True),
        ("page load", nothing, False),
        ("grow by hand D, C (wrong next node)", hand_grow("D", "C"), False),
        ("Grow from D button", grow("D"), False),
        ("grow by hand D, E, then flip C twice", seq(hand_grow("D", "E"), flips("C", "C")), False),
        ("grow by hand from E (E, D)", hand_grow("E", "D"), False),
    ],
    "grow-a-cut-5": [
        ("Grow from A, move C", seq(grow("A"), flips("C")), True),
        ("page load", nothing, False),
        ("Grow from A only (cut 5)", grow("A"), False),
        ("build ABC|DE by hand, no grow", build("ABC", "DE"), False),
        ("Grow from D (cut 3, nothing moved)", grow("D"), False),
        ("Grow from A, move C and E", seq(grow("A"), flips("C", "E")), False),
        ("Grow from A, move C, then reveal", seq(grow("A"), flips("C"), reveal), False),
    ],
    "random-lucky": [
        ("seed 5 (cut 3)", rand(5), True),
        ("seeds 3 then 14 (cut 3)", rand(3, 14), True),
        ("page load", nothing, False),
        ("seed 3 (cut 16)", rand(3), False),
        ("seed 5, then flip A twice", seq(rand(5), flips("A", "A")), False),
        ("build ABC|DE by hand", build("ABC", "DE"), False),
        ("reveal (study)", reveal, False),
    ],
    "keep-best": [
        ("seeds 0 1 2 3, back to 1 (cut 5)", rand(0, 1, 2, 3, 1), True),
        ("page load", nothing, False),
        ("seeds 0 1 2 3, leave 3 (cut 16)", rand(0, 1, 2, 3), False),
        ("only three seeds 0 1 2, back to 1", rand(0, 1, 2, 1), False),
        ("seeds 0 1 2 3 1, then flip A twice", seq(rand(0, 1, 2, 3, 1), flips("A", "A")), False),
        ("seeds 0 1 2 3, then Grow from D", seq(rand(0, 1, 2, 3), grow("D")), False),
    ],
    "grow-best-start": [
        ("grow from all six, back to A (cut 4)", grow_all(SIX, "A"), True),
        ("grow from all six, back to B (tie, cut 4)", grow_all(SIX, "B"), True),
        ("page load", nothing, False),
        ("grow from all six, leave F (cut 12)", grow_all(SIX, "F"), False),
        ("only Grow from A", grow("A"), False),
        ("all six, back to A, flip C twice", seq(grow_all(SIX, "A"), flips("C", "C")), False),
        ("reveal (study)", reveal, False),
    ],
    "hand-grow-tie": [
        ("grow by hand C, D, A", hand_grow("C", "D", "A"), True),
        ("page load", nothing, False),
        ("grow by hand C, D, E (wrong tie-break)", hand_grow("C", "D", "E"), False),
        ("grow by hand C, A, D (skips the bridge)", hand_grow("C", "A", "D"), False),
        ("Grow from C button", grow("C"), False),
        ("grow by hand A, B, C (other start)", hand_grow("A", "B", "C"), False),
    ],
    "star-cap": [
        ("build ABC|DEF by hand (cut 15)", build("ABC", "DEF"), True),
        ("page load", nothing, False),
        ("build ABDEF|C (cut 5, illegal)", build("ABDEF", "C"), False),
        ("build ACD|BEF (cut 19)", build("ACD", "BEF"), False),
        ("Run greedy button (cut 15)", greedy, False),
        ("reveal (study)", reveal, False),
    ],
    "manual-beats-greedy": [
        ("greedy, then move E and F", seq(greedy, flips("E", "F")), True),
        ("greedy, clear, build ABF|CDE", seq(greedy, clear, build("ABF", "CDE")), True),
        ("page load", nothing, False),
        ("build ABF|CDE without greedy", build("ABF", "CDE"), False),
        ("greedy only (cut 9)", greedy, False),
        ("greedy, then Grow from C (cut 4)", seq(greedy, grow("C")), False),
        ("greedy, then reveal", seq(greedy, reveal), False),
    ],
}

def run(lang: str) -> int:
    global L
    L = LANGS[lang]
    url = f"{args.base.rstrip('/')}/{'fr/' if lang == 'fr' else ''}tools/initial-bipartition/index.html"
    print(f"=== {lang}: {url}")
    with sync_playwright() as p:
        b = p.chromium.launch(headless=not args.headed)
        pg = b.new_page(viewport={"width": 1400, "height": 3000})
        errors = []
        site = args.base.rstrip("/")
        pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("requestfailed", lambda r: errors.append(f"request failed: {r.url}"))
        pg.on("request", lambda r: not r.url.startswith((site, "data:", "blob:")) and errors.append(f"external request: {r.url}"))
        pg.on("response", lambda r: r.status >= 400 and errors.append(f"HTTP {r.status}: {r.url}"))
        pg.goto(url)
        pg.add_style_tag(content="html{scroll-behavior:auto!important}")
        pg.wait_for_selector("#lab-root canvas")

        ids = pg.eval_on_selector_all("#lab-chal-sel option", "os => os.map(o => o.value)")
        assert sorted(ids) == sorted(CASES), f"challenge ids differ: page {ids}"

        # nothing is checkable before Start, and the first load shows an empty split
        assert pg.is_disabled("#lab-chal-check"), "Check must be disabled before Start"
        assert L["empty"] in pg.inner_text(".metrics-body"), "page load must show an empty split"

        rows, bad = [], 0

        # colour rule: the side holding A is blue whatever its side number (same as the slides)
        COLOURS = [
            ("Grow from D: A on side 1", grow("D"), {"A": "blue", "B": "blue", "C": "blue", "D": "green", "E": "green"}, L["blue"](1)),
            ("Grow from A: A on side 0", grow("A"), {"A": "blue", "B": "blue", "C": "green", "D": "green", "E": "green"}, L["blue"](0)),
            ("grow by hand D (A on side 1)", hand_grow("D"), {"A": "blue", "D": "green"}, L["blue"](1)),
            ("A grey, D clicked once", seq(clear, flips("D")), {"A": "grey", "D": "blue"}, L["blue"](0, L["has"]("D"))),
            ("ABC|DE by hand, then flip A", seq(clear, build("ABC", "DE"), flips("A")), {"A": "blue", "B": "green", "D": "blue"}, L["blue"](1)),
        ]
        btn(pg, L["reset"])
        for label, act, want, legend in COLOURS:
            act(pg)
            got = {n: node_colour(pg, n) for n in want}
            ok = got == want and legend in pg.inner_text(".metrics-body")
            bad += not ok
            rows.append(("(colour)", "colour", label, "ok" if ok else f"WRONG {got}"))

        for cid, cases in CASES.items():
            for label, act, want in cases:
                pg.select_option("#lab-chal-sel", cid)
                pg.click("#lab-chal-start")
                act(pg)
                pg.click("#lab-chal-check")
                got = pg.inner_text("#lab-status").strip() == L["pass"]
                ok = got == want
                bad += not ok
                rows.append((cid, "positive" if want else "negative", label, "ok" if ok else "WRONG"))

        # the starter reset (the only preset) stops checking instead of passing anything
        pg.select_option("#lab-chal-sel", "two-sides")
        pg.click("#lab-chal-start")
        btn(pg, L["reset"])
        preset_ok = pg.is_disabled("#lab-chal-check") and L["empty"] in pg.inner_text(".metrics-body")
        bad += not preset_ok
        rows.append(("(all)", "negative", "Reset workspace preset", "ok" if preset_ok else "WRONG"))
        b.close()


    w = max(len(r[0]) for r in rows)
    lw = max(len(r[2]) for r in rows)
    print(f"{'challenge'.ljust(w)}  {'case':8}  {'actions'.ljust(lw)}  result")
    for cid, kind, label, res in rows:
        print(f"{cid.ljust(w)}  {kind:8}  {label.ljust(lw)}  {res}")
    kinds = {k: sum(r[1] == k for r in rows) for k in ("positive", "negative", "colour")}
    print(f"\n{len(rows)} cases ({kinds['positive']} positive, {kinds['negative']} negative, {kinds['colour']} colour), "
          f"{bad} wrong, {len(errors)} page error(s)")
    for e in errors:
        print("  error:", e)
    return 1 if bad or errors else 0


langs = ["en", "fr"] if args.lang == "both" else [args.lang]
sys.exit(max(run(x) for x in langs))
