#!/usr/bin/env python3
"""Draw the explanation figures for the partitioning Lab 03 slides, in English and French.

    chip-to-graph.png     cells and wires on a chip -> the same thing as a weighted graph
    cut-and-balance.png   ABC|DE (cut 3, legal) versus everything on one side (cut 0, not legal)
    worked-unlucky.png    random seed 3, ACE|BD: the cut 16 added up edge by edge
    grow-a.png            grow from A, step by step: AB|CDE, cut 5
    star-cap.png          star graph: old greedy 5|1 (cut 5, not legal) versus capped greedy 3|3 (cut 15)
    tie-graph.png         tie graph: anchor A-B gives cut 9, anchor D-E gives cut 4
    bridge-graph.png      bridge graph: greedy anchors the bridge (cut 12), grow from A keeps both triangles (cut 4)

Every split comes from facts.json (written by facts.py from the module checker), and every number on
a figure is computed here from those splits and the example graphs. Graphs are drawn with the
course's own drawGraph (platform/assets/clustering-ui.js), so the figures look like the lab.

Needs Playwright + Chromium and the platform served locally (run_all.sh does both):
    python3 -m http.server 8081 --directory wt-platform
    python3 make_figures.py --module <module dir> [--base http://127.0.0.1:8081]          # English, into <module>/assets
    python3 make_figures.py --module <module dir> --lang fr --out <folder>               # French, into <folder>
The French text lives in TEXT below; every number still comes from facts.json.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "facts.json").read_text())

# design coordinates; drawGraph scales them into the canvas
TINY_LAYOUT = {"A": [90, 80], "B": [220, 60], "C": [160, 160], "D": [280, 200], "E": [120, 240]}
STAR_LAYOUT = {"A": [200, 150], "B": [330, 150], "C": [200, 40], "D": [90, 90], "E": [90, 210], "F": [200, 260]}
TIE_LAYOUT = {"A": [80, 60], "B": [260, 60], "E": [80, 170], "F": [260, 170], "D": [80, 280], "C": [260, 280]}
BRIDGE_LAYOUT = {"A": [40, 60], "B": [40, 240], "C": [150, 150], "D": [290, 150], "E": [400, 60], "F": [400, 240]}


TEXT = {
    "en": {
        "chip_top": "On the chip: cells joined by wires",
        "chip_bottom": "As a graph: weight = number of wires",
        "cell": "cell",
        "legal_cut": "{p}: cut {sum}. Sizes 3 and 2: legal.",
        "one_side": "All five on one side: cut 0. Sizes 5 and 0: not legal.",
        "unlucky_title": "Random seed 3: {p}",
        "unlucky_1": "1. Cut (red): {edges}",
        "unlucky_2": "2. Cut: {sum}",
        "unlucky_3": "3. Sizes 3 and 2: legal, but the worst start",
        "grow_title": "Grow from A",
        "grow_1": "1. Start the side with A",
        "grow_2": "2. Heaviest edge out of A: A–B 5, add B",
        "grow_3": "3. 2 of 5 nodes: the side is full, stop",
        "grow_4": "4. Cut: {sum}",
        "star_old": "Old greedy, no size limit: {p}. Sizes {a} and {b}, cut {cut}. Not legal.",
        "star_new": "Greedy with the limit: {p}. Sizes 3 and 3, cut {cut}. Legal.",
        "tie_ab": "Anchor A–B (the rule): {p}, cut {cut}",
        "tie_de": "Anchor D–E: {p}, cut {cut}",
        "bridge_greedy": "Greedy anchors the bridge C–D: {p}, cut {cut}",
        "bridge_grow": "Grow from A: {p}, cut {cut}",
    },
    "fr": {
        "chip_top": "Sur la puce : des cellules reliées par des fils",
        "chip_bottom": "En graphe : poids = nombre de fils",
        "cell": "cellule",
        "legal_cut": "{p} : coupe {sum}. Tailles 3 et 2 : valide.",
        "one_side": "Les cinq du même côté : coupe 0. Tailles 5 et 0 : non valide.",
        "unlucky_title": "Aléatoire, graine 3 : {p}",
        "unlucky_1": "1. Coupées (rouge) : {edges}",
        "unlucky_2": "2. Coupe : {sum}",
        "unlucky_3": "3. Tailles 3 et 2 : valide, mais le pire départ",
        "grow_title": "Croissance depuis A",
        "grow_1": "1. Le côté démarre avec A",
        "grow_2": "2. Arête la plus lourde depuis A : A–B 5, on ajoute B",
        "grow_3": "3. 2 nœuds sur 5 : le côté est plein, stop",
        "grow_4": "4. Coupe : {sum}",
        "star_old": "Ancien glouton, sans limite : {p}. Tailles {a} et {b}, coupe {cut}. Non valide.",
        "star_new": "Glouton avec la limite : {p}. Tailles 3 et 3, coupe {cut}. Valide.",
        "tie_ab": "Ancre A–B (la règle) : {p}, coupe {cut}",
        "tie_de": "Ancre D–E : {p}, coupe {cut}",
        "bridge_greedy": "Le glouton s'ancre sur le pont C–D : {p}, coupe {cut}",
        "bridge_grow": "Croissance depuis A : {p}, coupe {cut}",
    },
}


def load(mod: Path, name: str) -> dict:
    g = json.loads((mod / "examples" / name).read_text())
    return {"nodes": g["nodes"], "edges": g["edges"]}


def a_side(a: dict) -> dict:
    """Swap labels so A's side is "0" (blue), as in the walkthrough frames."""
    return a if a["A"] == "0" else {n: "1" if s == "0" else "0" for n, s in a.items()}


def spaced(parts: str) -> str:
    """'ABC|DE' -> 'A B C | D E' (easier to read on a figure)."""
    return " | ".join(" ".join(side) for side in parts.split("|"))


def weight(g: dict, pair: str) -> float:
    u, v = pair.split("|")
    return next(e["w"] for e in g["edges"] if {e["u"], e["v"]} == {u, v})


def cut_sum(g: dict, item: dict) -> str:
    """'C–D 2 + C–E 1 = 3', checked against the checker's cut."""
    ws = [(p.replace("|", "–"), weight(g, p)) for p in item["cut_edges"]]
    assert sum(w for _, w in ws) == item["cut"], item
    return " + ".join(f"{name} {w:g}" for name, w in ws) + f" = {item['cut']:g}"


def build(mod: Path, lang: str = "en") -> dict:
    T = TEXT[lang]
    tiny, star, tie, bridge = (load(mod, f) for f in
                               ("tiny_graph.json", "star_graph.json", "tie_graph.json", "bridge_graph.json"))
    one_side = {n: "0" for n in tiny["nodes"]}
    r3, ga = F["random3"], F["growA"]
    sl, sg = F["star_legacy"], F["star_greedy"]
    tg, td = F["tie_greedy"], F["tie_anchorDE"]
    bg, ba = F["bridge_greedy"], F["bridge_growA"]
    assert not sl["legal"] and sg["legal"] and r3["legal"]

    def panel(g, layout, item_or_asn, caption, hi=()):
        asn = item_or_asn["assignment"] if "assignment" in item_or_asn else item_or_asn
        return {"graph": g, "layout": layout, "assignment": a_side(asn), "caption": caption, "hi": list(hi)}

    return {
        "chip-to-graph.png": {"chip": True, "graph": tiny, "layout": TINY_LAYOUT, "t": T},
        "cut-and-balance.png": {"panels": [
            panel(tiny, TINY_LAYOUT, F["greedy"],
                  T["legal_cut"].format(p=spaced(F["greedy"]["parts"]), sum=cut_sum(tiny, F["greedy"]))),
            panel(tiny, TINY_LAYOUT, one_side, T["one_side"]),
        ]},
        "worked-unlucky.png": {
            "title": T["unlucky_title"].format(p=spaced(r3["parts"])),
            "panels": [panel(tiny, TINY_LAYOUT, r3, "", hi=[])],
            "box": [T["unlucky_1"].format(edges=", ".join(p.replace("|", "–") for p in r3["cut_edges"])),
                    T["unlucky_2"].format(sum=" + ".join(f"{weight(tiny, p):g}" for p in r3["cut_edges"]) + f" = {r3['cut']:g}"),
                    T["unlucky_3"]],
        },
        "grow-a.png": {
            "title": T["grow_title"],
            "panels": [panel(tiny, TINY_LAYOUT, ga, "", hi=["A|B"])],
            "box": [T["grow_1"], T["grow_2"], T["grow_3"], T["grow_4"].format(sum=cut_sum(tiny, ga))],
        },
        "star-cap.png": {"panels": [
            panel(star, STAR_LAYOUT, sl, T["star_old"].format(p=spaced(sl["parts"]), a=max(sl["sizes"]),
                                                              b=min(sl["sizes"]), cut=f"{sl['cut']:g}")),
            panel(star, STAR_LAYOUT, sg, T["star_new"].format(p=spaced(sg["parts"]), cut=f"{sg['cut']:g}")),
        ]},
        "tie-graph.png": {"panels": [
            panel(tie, TIE_LAYOUT, tg, T["tie_ab"].format(p=spaced(tg["parts"]), cut=f"{tg['cut']:g}"), hi=["A|B"]),
            panel(tie, TIE_LAYOUT, td, T["tie_de"].format(p=spaced(td["parts"]), cut=f"{td['cut']:g}"), hi=["D|E"]),
        ]},
        "bridge-graph.png": {"panels": [
            panel(bridge, BRIDGE_LAYOUT, bg, T["bridge_greedy"].format(p=spaced(bg["parts"]), cut=f"{bg['cut']:g}"), hi=["C|D"]),
            panel(bridge, BRIDGE_LAYOUT, ba, T["bridge_grow"].format(p=spaced(ba["parts"]), cut=f"{ba['cut']:g}")),
        ]},
    }


FIG_JS = r"""
async (spec) => {
  const { drawGraph } = await import('/assets/clustering-ui.js');
  const toLayout = (l) => Object.fromEntries(Object.entries(l).map(([k, [x, y]]) => [k, { x, y }]));
  document.body.innerHTML = '';
  document.body.style.background = '#fff';
  const wrap = document.createElement('div');
  wrap.id = 'fig';
  wrap.style.cssText = 'display:flex;flex-direction:column;gap:14px;padding:18px;background:#fff;width:640px;font:600 24px system-ui,sans-serif;color:#1c2421';
  document.body.append(wrap);
  const text = (txt, css = '') => { const h = document.createElement('div'); h.textContent = txt; h.style.cssText = css; wrap.append(h); };
  const canvas = (h) => {
    const c = document.createElement('canvas');
    c.style.cssText = `width:600px;height:${h}px;display:block;border:1px solid #ccc;border-radius:6px`;
    wrap.append(c); return c;
  };

  if (spec.chip) {
    const layout = toLayout(spec.layout);
    text(spec.t.chip_top);
    const c = canvas(330);
    const dpr = 2, W = 600, H = 330;
    c.width = W * dpr; c.height = H * dpr;
    const ctx = c.getContext('2d'); ctx.scale(dpr, dpr);
    ctx.fillStyle = '#f7faf9'; ctx.fillRect(0, 0, W, H);
    const xs = Object.values(layout).map(p => p.x), ys = Object.values(layout).map(p => p.y);
    const sx = (x) => 70 + (x - Math.min(...xs)) / (Math.max(...xs) - Math.min(...xs)) * (W - 140);
    const sy = (y) => 50 + (y - Math.min(...ys)) / (Math.max(...ys) - Math.min(...ys)) * (H - 100);
    for (const { u, v, w } of spec.graph.edges) {
      const ax = sx(layout[u].x), ay = sy(layout[u].y), bx = sx(layout[v].x), by = sy(layout[v].y);
      const len = Math.hypot(bx - ax, by - ay), nx = -(by - ay) / len, ny = (bx - ax) / len;
      for (let i = 0; i < w; i++) {
        const off = (i - (w - 1) / 2) * 5;
        ctx.beginPath(); ctx.moveTo(ax + nx * off, ay + ny * off); ctx.lineTo(bx + nx * off, by + ny * off);
        ctx.strokeStyle = '#b45309'; ctx.lineWidth = 1.6; ctx.stroke();
      }
    }
    for (const [n, p] of Object.entries(layout)) {
      const x = sx(p.x), y = sy(p.y);
      ctx.fillStyle = '#0f6b5c'; ctx.fillRect(x - 30, y - 22, 60, 44);
      ctx.strokeStyle = '#0b3f36'; ctx.lineWidth = 2; ctx.strokeRect(x - 30, y - 22, 60, 44);
      ctx.fillStyle = '#fff'; ctx.font = 'bold 18px system-ui'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(n, x, y - 4);
      ctx.font = '11px system-ui'; ctx.fillText(spec.t.cell, x, y + 12);
    }
    text(spec.t.chip_bottom);
    const same = Object.fromEntries(spec.graph.nodes.map((n) => [n, '0']));
    drawGraph(canvas(330), spec.graph, { layout, assignment: same });
    return;
  }

  if (spec.title) text(spec.title);
  const single = spec.panels.length === 1;
  for (const p of spec.panels) {
    if (p.caption) text(p.caption, 'font-weight:600;font-size:22px;line-height:1.35');
    drawGraph(canvas(single ? 380 : 330), p.graph,
              { layout: toLayout(p.layout), assignment: p.assignment, highlightPairs: p.hi });
  }
  if (spec.box) {
    const box = document.createElement('div');
    box.style.cssText = 'font:500 22px ui-monospace,Menlo,monospace;line-height:1.6;background:#f3efe6;border-radius:8px;padding:12px 16px';
    box.innerHTML = spec.box.map((l, i) => i === spec.box.length - 1 ? `<b>${l}</b>` : l).join('<br>');
    wrap.append(box);
  }
}
"""


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--module", required=True, type=Path)
    ap.add_argument("--base", default="http://127.0.0.1:8081")
    ap.add_argument("--only", nargs="*", help="figure file names to redraw")
    ap.add_argument("--lang", choices=sorted(TEXT), default="en")
    ap.add_argument("--out", type=Path, help="output folder (default: <module>/assets)")
    args = ap.parse_args()
    figs = build(args.module.resolve(), args.lang)
    out = (args.out or args.module / "assets").resolve()
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        page = await b.new_page(viewport={"width": 1200, "height": 1800}, device_scale_factor=2)
        for name, spec in figs.items():
            if args.only and name not in args.only:
                continue
            await page.goto(f"{args.base}/tools/initial-bipartition/index.html", wait_until="networkidle")
            await page.evaluate(FIG_JS, spec)
            await page.wait_for_timeout(300)
            await page.locator("#fig").screenshot(path=str(out / name))
            print("wrote", out / name)
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
