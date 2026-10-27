#!/usr/bin/env python3
"""Every split the Stage 3 figures and transcript cite, computed by the module checker.

    python3 facts.py <module_dir>  ->  prints a summary, writes facts.json next to this script
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # importing the checker must not leave __pycache__ in the teacher clone
mod = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(mod / "examples"))
import initial_bipartition_check as ck  # noqa: E402
from graphutil import cutsize, load_graph, parts_string  # noqa: E402


def load(name):
    g = load_graph(mod / "examples" / name)
    return g


def item(g, a, label):
    cut_edges = [f"{u}|{v}" if u < v else f"{v}|{u}" for u, v, w in g["edges"] if a[u] != a[v]]
    sizes = [sum(1 for s in a.values() if s == x) for x in ("0", "1")]
    return {"label": label, "assignment": a, "parts": parts_string(a), "cut": cutsize(a, g["edges"]),
            "cut_edges": cut_edges, "sizes": sizes, "legal": ck.is_legal(g["nodes"], a)}


tiny, star, tie, bridge = (load(f) for f in ("tiny_graph.json", "star_graph.json", "tie_graph.json", "bridge_graph.json"))
T = lambda g: (g["nodes"], g["edges"])  # noqa: E731

facts = {
    "random5": item(tiny, ck.random_bipartition(tiny["nodes"], 5), "random seed 5"),
    "random3": item(tiny, ck.random_bipartition(tiny["nodes"], 3), "random seed 3"),
    "greedy": item(tiny, ck.greedy_bipartition(*T(tiny)), "greedy"),
    "growD": item(tiny, ck.grow_bipartition(*T(tiny), "D"), "grow D"),
    "growA": item(tiny, ck.grow_bipartition(*T(tiny), "A"), "grow A"),
    "growC": item(tiny, ck.grow_bipartition(*T(tiny), "C"), "grow C"),
    "random_all": [item(tiny, ck.random_bipartition(tiny["nodes"], s), f"seed {s}") for s in range(16)],
    "best_tiny": ck.best_start(*T(tiny), []),
    "best_tiny_seeds0_3": ck.best_start(*T(tiny), range(4)),
    "star_greedy": item(star, ck.greedy_bipartition(*T(star)), "greedy (cap)"),
    "star_legacy": item(star, ck.greedy_legacy(*T(star)), "old greedy"),
    "tie_greedy": item(tie, ck.greedy_bipartition(*T(tie)), "greedy anchor A-B"),
    "tie_growC": item(tie, ck.grow_bipartition(*T(tie), "C"), "grow C"),
    "best_tie": ck.best_start(*T(tie), []),
    "bridge_greedy": item(bridge, ck.greedy_bipartition(*T(bridge)), "greedy"),
    "bridge_growA": item(bridge, ck.grow_bipartition(*T(bridge), "A"), "grow A"),
    "best_bridge": ck.best_start(*T(bridge), []),
    "total_tiny": sum(w for _, _, w in tiny["edges"]),
}
# the tie graph's other anchor (D-E), through the checker's own hook
try:
    facts["tie_anchorDE"] = item(tie, ck.greedy_bipartition(*T(tie), _anchor=("D", "E")), "greedy anchor D-E")
except Exception as e:  # noqa: BLE001
    facts["tie_anchorDE"] = {"error": repr(e)}

for k, v in facts.items():
    if isinstance(v, dict):
        print(f"{k:14s} {v.get('parts')} cut {v.get('cut')} cut_edges {v.get('cut_edges')} sizes {v.get('sizes')} legal {v.get('legal')}")
    elif k == "random_all":
        print("random 0-15  ", [(x["parts"], x["cut"]) for x in v])
    else:
        print(f"{k:14s} {v}")
(Path(__file__).parent / "facts.json").write_text(json.dumps(facts, indent=1))
