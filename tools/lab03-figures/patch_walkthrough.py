#!/usr/bin/env python3
"""Replace the initial-bipartition block in a SCRATCH copy of walkthrough.js with the Stage 3 frames.

    python3 patch_walkthrough.py [--source ../../eda-learning/platform]

Copies <source> to ./wt-platform the first time (the teacher's viewer is never edited), then:
- writes the 5 frames below into wt-platform/tools/algorithm-walkthrough/walkthrough.js;
- adds a CSS override to wt-platform/tools/algorithm-walkthrough/index.html that restores the
  teacher's frame shape (940x468). The current viewer CSS gives 940x636, which fills only half a slide.

Splits come from facts.json (made by facts.py from the module checker). Labels are swapped so the
side holding A is always "0", which keeps the colours the same from frame to frame.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--source", type=Path, default=HERE.parents[1] / "eda-learning/platform",
                help="a full platform/ folder that has tools/algorithm-walkthrough (default: ../../eda-learning/platform)")
args = ap.parse_args()
WT_ROOT = HERE / "wt-platform"
if not WT_ROOT.is_dir():
    shutil.copytree(args.source, WT_ROOT, symlinks=True)  # course-media/* are dangling links
    print("copied", args.source, "->", WT_ROOT)
facts = json.loads((HERE / "facts.json").read_text())
wt = WT_ROOT / "tools/algorithm-walkthrough/walkthrough.js"
wt_html = WT_ROOT / "tools/algorithm-walkthrough/index.html"


def a_side(key):
    a = facts[key]["assignment"]
    return a if a["A"] == "0" else {n: "1" if s == "0" else "0" for n, s in a.items()}


f = facts
assert f["random5"]["cut"] == 3 and f["random3"]["cut"] == 16 and f["greedy"]["cut"] == 3
assert f["growD"]["cut"] == 3 and f["growA"]["cut"] == 5 and f["growC"]["cut"] == 9
cuts = [x["cut"] for x in f["random_all"]]
assert (min(cuts), max(cuts)) == (3, 16)

steps = [
    {
        "id": "empty",
        "title": "Need a legal starting split",
        "caption": "Kernighan–Lin and FM only improve a split, so they need a first one. "
                   "Every node goes on one of two sides, and no side may hold more than 3 of the 5 nodes.",
        "bullets": ["Every node on exactly one side", "Here: sides of 2 and 3 nodes",
                    "Report cutsize and balance"],
        "metrics": ["5 nodes, 6 edges, total weight 18", "legal sizes: 2 | 3"],
        "assignment": None,
        "highlightPairs": [],
    },
    {
        "id": "random-lucky",
        "title": "Random seed 5: lucky ABC|DE cut 3",
        "caption": "Random shuffles the nodes like cards and deals two of them to one side. "
                   "Seed 5 deals D and E: only C–D and C–E are cut, cutsize 3. Seed 3 deals A, C, E: cutsize 16.",
        "bullets": ["Same seed, same split every time", "Seed 5 → ABC|DE, cut 3",
                    "Seed 3 → ACE|BD, cut 16"],
        "metrics": ["method: random seed=5", f"parts: {f['random5']['parts']}",
                    "cutsize: 3 = C–D 2 + C–E 1"],
        "assignment": a_side("random5"),
        "highlightPairs": ["A|B", "D|E"],
    },
    {
        "id": "greedy",
        "title": "Greedy: ABC|DE cut 3",
        "caption": "Greedy keeps the heaviest edge A–B inside one side (it ties with D–E; the smaller name wins). "
                   "D, the node least tied to A and B, starts the other side. "
                   "C joins A and B; E joins D, since that cuts 1 instead of 5.",
        "bullets": ["Anchor: A–B, weight 5", "Other side starts with D",
                    "Each node goes where it adds less cut"],
        "metrics": ["method: greedy", f"parts: {f['greedy']['parts']}", "cutsize: 3"],
        "assignment": a_side("greedy"),
        "highlightPairs": ["A|B"],
    },
    {
        "id": "grow-d",
        "title": "Grow from D: ABC|DE cut 3",
        "caption": "Grow starts a side with D and adds the node behind the heaviest edge leaving it: E, weight 5. "
                   "The side now holds 2 of the 5 nodes, so it stops. A, B and C are the other side: cut 3.",
        "bullets": ["Start node: D", "Heaviest edge out: D–E (5)",
                    "Grow from A → AB|CDE, cut 5"],
        "metrics": ["method: grow from D", f"parts: {f['growD']['parts']}", "cutsize: 3"],
        "assignment": a_side("growD"),
        "highlightPairs": ["D|E"],
    },
    {
        "id": "takeaway",
        "title": "Try several starts, keep the best",
        "caption": "Every start here is legal, but the cuts go from 3 to 16 on the same graph. "
                   "Build several starts, drop any illegal one, and keep the smallest cut.",
        "bullets": ["Random: 3 to 16, depends on the seed", "Grow: 3, 5 or 9, depends on the start",
                    "Greedy: 3 here, but not always"],
        "metrics": [f"best: {f['best_tiny'][2]}, cut 3",
                    "greedy 3 · grow A 5 · grow C 9 · grow D 3"],
        "assignment": a_side("greedy"),
        "highlightPairs": [],
    },
]

block = (
    '  "initial-bipartition": {\n'
    '    title: "Initial bipartition",\n'
    '    module: "module01-03-initial-bipartition",\n'
    f'    steps: {json.dumps(steps, ensure_ascii=False, indent=2)},\n'
    '  },\n\n'
)
src = wt.read_text(encoding="utf-8")
new, n = re.subn(r'  "initial-bipartition": \{.*?(?=  "kl-partition": \{)', lambda _: block, src, count=1, flags=re.S)
assert n == 1
wt.write_text(new, encoding="utf-8")
(HERE / "steps.json").write_text(json.dumps(steps, ensure_ascii=False, indent=1))
print("patched", wt)

html = wt_html.read_text(encoding="utf-8")
if "scratch only" not in html:
    css = ("  <style>/* scratch only: teacher's original frame shape for slides */ "
           ".walk-body{min-height:0} .walk-canvas-wrap canvas{height:320px;max-height:320px}</style>\n</head>")
    wt_html.write_text(html.replace("</head>", css, 1), encoding="utf-8")
    print("patched", wt_html)
