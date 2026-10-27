#!/usr/bin/env python3
"""Golden self-check for module01-03 initial bipartition (Track A).

    python3 examples/initial_bipartition_check.py                    # check the reference
    python3 examples/initial_bipartition_check.py --show             # also print every result
    python3 examples/initial_bipartition_check.py --impl my_init.py  # check YOUR functions
    python3 examples/initial_bipartition_check.py --vs-node          # compare the PRNG with the JS lab

Your file may define any of (nodes = list of names, edges = [(u, v, w), ...] with u < v):
    random_bipartition(nodes, seed)       -> {node: "0" | "1"}
    greedy_bipartition(nodes, edges)      -> {node: "0" | "1"}
    grow_bipartition(nodes, edges, start) -> {node: "0" | "1"}
    is_legal(nodes, assignment)           -> bool
Two splits are the same if they group the nodes the same way (labels 0/1 may be swapped).
Functions you have not written yet are reported as SKIP. You may copy `mulberry32` from here.

Every start must be LEGAL: each node on exactly one side, both sides non-empty, and neither
side larger than ceil(n / 2) nodes (all node sizes are 1 in this lab).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # do not leave __pycache__ in common/
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "common"))

from graphutil import adjacency, cutsize, load_graph, parts_string  # noqa: E402

M32 = 0xFFFFFFFF


# ---------------- the random start: mulberry32 + Fisher-Yates ----------------
def mulberry32(seed: int):
    """Tiny 32-bit PRNG, identical to `mulberry32` in platform/assets/partitioning-core.js.

    Python's `random` and JavaScript's `Math.random` never agree, so both the checker and the
    browser lab use this one function. It returns floats in [0, 1).
    """
    t = seed & M32

    def nxt() -> float:
        nonlocal t
        t = (t + 0x6D2B79F5) & M32
        r = ((t ^ (t >> 15)) * (1 | t)) & M32
        r ^= (r + (((r ^ (r >> 7)) * (61 | r)) & M32)) & M32
        return ((r ^ (r >> 14)) & M32) / 4294967296

    return nxt


def random_bipartition(nodes, seed):
    """Seeded shuffle, then deal the first floor(n/2) nodes to side 0.

    1. order = nodes sorted by name (so the input order never matters)
    2. rng = mulberry32(seed); throw away its first two numbers (small seeds start out alike:
       without this, seeds 0 to 3 all give the same split)
    3. for i = n-1 down to 1: j = floor(rng() * (i + 1)); swap order[i], order[j]
    4. side 0 = first floor(n/2) nodes of `order`, side 1 = the rest
    Why: a fair shuffle gives every split the same chance; the same seed gives the same split.
    """
    order = sorted(nodes)
    rng = mulberry32(seed)
    rng(), rng()
    for i in range(len(order) - 1, 0, -1):
        j = int(rng() * (i + 1))
        order[i], order[j] = order[j], order[i]
    left = set(order[: len(order) // 2])
    return {n: "0" if n in left else "1" for n in sorted(nodes)}


# ---------------- the greedy start ----------------
def greedy_bipartition(nodes, edges, _anchor=None):
    """Anchor on the heaviest edge, seed side 1 with the loosest node, then place by least added cut.

    cap = ceil(n / 2): no side may ever hold more than cap nodes.
    1. Anchor: the heaviest edge; ties go to the smaller (u, v). Both ends go to side 0.
    2. Side-1 seed: the unplaced node with the smallest total weight to the placed nodes
       (ties: smaller name). It goes to side 1.
    3. Repeat until all are placed: take the unplaced node with the largest total weight to the
       placed nodes (ties: smaller name). Putting it on side 0 would cut its edges to side 1;
       putting it on side 1 would cut its edges to side 0. Choose the side with the smaller added
       cut among the sides that still have room; a tie goes to side 0.
    Why: the heaviest edges are kept inside a side, and the cap keeps the split balanced.
    """
    nodes = sorted(nodes)
    n = len(nodes)
    cap = math.ceil(n / 2)
    adj = adjacency(edges)
    side: dict = {}
    if _anchor:  # only used to show what the other tie-break would have done
        u0, v0 = _anchor
    elif edges:
        u0, v0, _ = min(edges, key=lambda e: (-e[2], e[0], e[1]))
    else:
        u0, v0 = nodes[0], nodes[1]
    side[u0] = side[v0] = "0"
    todo = [x for x in nodes if x not in side]
    if not todo:  # n == 2
        side[v0] = "1"
        return {x: side[x] for x in nodes}

    def tie(x):
        return sum(w for y, w in adj.get(x, {}).items() if y in side)

    seed1 = min(todo, key=lambda x: (tie(x), x))
    side[seed1] = "1"
    todo.remove(seed1)
    while todo:
        x = max(todo, key=lambda y: (tie(y), [-ord(c) for c in y]))
        todo.remove(x)
        to0 = sum(w for y, w in adj.get(x, {}).items() if side.get(y) == "0")
        to1 = sum(w for y, w in adj.get(x, {}).items() if side.get(y) == "1")
        n0 = sum(1 for s in side.values() if s == "0")
        n1 = len(side) - n0
        add0, add1 = to1, to0  # cut added if x joins side 0 / side 1
        if n0 >= cap:
            pick = "1"
        elif n1 >= cap:
            pick = "0"
        else:
            pick = "0" if add0 <= add1 else "1"
        side[x] = pick
    return {x: side[x] for x in nodes}


def greedy_legacy(nodes, edges):
    """The shared lab's old greedy, written out, to show what goes wrong. Not a reference.

    Heaviest edge (ties by u, v) on side 0; the first unplaced node by name is forced onto
    side 1; every other node in name order goes where more of its weight already is, a tie to
    side 0. There is no size cap.
    """
    nodes = sorted(nodes)
    adj = adjacency(edges)
    u0, v0, _ = min(edges, key=lambda e: (-e[2], e[0], e[1]))
    side = {u0: "0", v0: "0"}
    rest = [x for x in nodes if x not in side]
    if rest:
        side[rest.pop(0)] = "1"
    for x in rest:
        a0 = sum(w for y, w in adj.get(x, {}).items() if side.get(y) == "0")
        a1 = sum(w for y, w in adj.get(x, {}).items() if side.get(y) == "1")
        side[x] = "0" if a0 >= a1 else "1"
    return {x: side[x] for x in nodes}


# ---------------- the grow start ----------------
def grow_bipartition(nodes, edges, start):
    """Flood outward from `start` until side 0 holds floor(n / 2) nodes.

    1. grown = {start}
    2. while |grown| < floor(n / 2): add the node outside `grown` reached by the heaviest single
       edge leaving `grown` (ties: smaller node name). If no edge leaves, add the smallest
       unplaced name.
    3. side 0 = grown, side 1 = the rest
    Why: the heaviest wires pull their ends together, so the grown side stays tightly connected.
    """
    nodes = sorted(nodes)
    adj = adjacency(edges)
    target = len(nodes) // 2
    grown = [start]
    while len(grown) < target:
        best = None
        for u in grown:
            for v, w in adj.get(u, {}).items():
                if v in grown:
                    continue
                if best is None or w > best[0] or (w == best[0] and v < best[1]):
                    best = (w, v)
        if best is None:
            best = (0, next(x for x in nodes if x not in grown))
        grown.append(best[1])
    return {x: "0" if x in grown else "1" for x in nodes}


# ---------------- legality and the report ----------------
def is_legal(nodes, assignment):
    """Every node has side "0" or "1", both sides are used, and neither side exceeds ceil(n/2)."""
    if set(assignment) != set(nodes) or any(s not in ("0", "1") for s in assignment.values()):
        return False
    n0 = sum(1 for s in assignment.values() if s == "0")
    n1 = len(nodes) - n0
    cap = math.ceil(len(nodes) / 2)
    return 0 < n0 <= cap and 0 < n1 <= cap


def best_start(nodes, edges, seeds):
    """Try every start: random over `seeds`, greedy, and grow from each node.

    Returns (cut, label, parts) of the legal start with the smallest cut. Ties keep the first
    candidate in this order: greedy, then grow A, grow B, ... (random seeds first when given)
    """
    cands = [(f"random {s}", random_bipartition(nodes, s)) for s in seeds]
    cands.append(("greedy", greedy_bipartition(nodes, edges)))
    cands += [(f"grow {x}", grow_bipartition(nodes, edges, x)) for x in sorted(nodes)]
    scored = [(cutsize(a, edges), label, parts_string(a)) for label, a in cands if is_legal(nodes, a)]
    return min(scored, key=lambda t: t[0])  # min keeps the first of equal cuts


def report(g, a):
    return parts_string(a), cutsize(a, g["edges"])


# ---------------- goldens (also printed in EXAMPLES.md) ----------------
GOLDEN = {
    # random(seed) on the tiny graph, seeds 0..15: (split, cut)
    "tiny_random": [
        ("ABE|CD", 11.0), ("AB|CDE", 5.0), ("AE|BCD", 12.0), ("ACE|BD", 16.0),
        ("ABD|CE", 12.0), ("ABC|DE", 3.0), ("ABD|CE", 12.0), ("AD|BCE", 13.0),
        ("AD|BCE", 13.0), ("ACD|BE", 15.0), ("AC|BDE", 12.0), ("AB|CDE", 5.0),
        ("ACD|BE", 15.0), ("ADE|BC", 9.0), ("ABC|DE", 3.0), ("ABC|DE", 3.0),
    ],
    "tiny_greedy": ("ABC|DE", 3.0),
    "star_greedy": ("ABD|CEF", 15.0),
    "tie_greedy": ("ABE|CDF", 9.0),
    "tie_greedy_other_anchor": ("ABF|CDE", 4.0),  # anchor D-E instead of A-B
    "bridge_greedy": ("AEF|BCD", 12.0),
    # grow(start) for every start node: (split, cut)
    "tiny_grow": {
        "A": ("AB|CDE", 5.0), "B": ("AB|CDE", 5.0), "C": ("ADE|BC", 9.0),
        "D": ("ABC|DE", 3.0), "E": ("ABC|DE", 3.0),
    },
    "bridge_grow": {
        "A": ("ABC|DEF", 4.0), "B": ("ABC|DEF", 4.0), "C": ("ACD|BEF", 12.0),
        "D": ("ACD|BEF", 12.0), "E": ("ABF|CDE", 12.0), "F": ("ABE|CDF", 12.0),
    },
    # best_start(..., ()): greedy and every grow start, no random seed: (cut, winner, split)
    "tiny_best": (3.0, "greedy", "ABC|DE"),
    "tie_best": (4.0, "grow C", "ABF|CDE"),
    "bridge_best": (4.0, "grow A", "ABC|DEF"),
    # the OLD greedy of the shared lab (no size cap, forced node)
    "star_legacy": ("ABDEF|C", [1, 5]),
    "tiny_legacy": ("AB|CDE", 5.0),
    "tiny_legacy_renamed": ("AB|CDE", 3.0),  # same graph, A<->E and B<->D renamed
}


def vs_node() -> int:
    core = HERE.parents[3] / "platform" / "assets" / "partitioning-core.js"
    if not core.exists():
        print("SKIP  --vs-node: platform/assets/partitioning-core.js not found")
        return 0
    js = (
        f'import {{ mulberry32 }} from "{core.as_uri()}";'
        "const out = {raw: {}, split: []};"
        "for (const s of [0, 1, 7, 12, 123456789]) { const r = mulberry32(s); out.raw[s] = [r(), r(), r(), r()]; }"
        "for (let seed = 0; seed < 16; seed++) {"
        "  const r = mulberry32(seed); r(); r();"
        "  const o = ['A', 'B', 'C', 'D', 'E'];"
        "  for (let i = o.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [o[i], o[j]] = [o[j], o[i]]; }"
        "  out.split.push(o.slice(0, 2).sort().join(''));"
        "}"
        "console.log(JSON.stringify(out));"
    )
    try:
        res = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"SKIP  --vs-node: node failed ({exc})")
        return 0
    want = json.loads(res.stdout)
    bad = 0
    for s, vals in want["raw"].items():
        r = mulberry32(int(s))
        ok = [r() for _ in vals] == vals
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'}  mulberry32({s}) matches node: first four values")
    nodes = ["A", "B", "C", "D", "E"]
    got = ["".join(sorted(n for n, s in random_bipartition(nodes, seed).items() if s == "0")) for seed in range(16)]
    ok = got == want["split"]
    bad += not ok
    print(f"{'PASS' if ok else 'FAIL'}  shuffle + deal: side 0 for seeds 0-15 matches node" + ("" if ok else f"\n        py: {got}\n        js: {want['split']}"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--impl", help="your .py file with the bipartition functions")
    ap.add_argument("--show", action="store_true", help="print every result")
    ap.add_argument("--dump", action="store_true", help="print the golden tables as Python (for authors)")
    ap.add_argument("--vs-node", action="store_true", help="compare mulberry32 with the browser lab's JS")
    args = ap.parse_args()

    if args.vs_node:
        return vs_node()

    fns = {
        "random": random_bipartition,
        "greedy": greedy_bipartition,
        "grow": grow_bipartition,
        "legal": is_legal,
    }
    name = "reference"
    if args.impl:
        spec = importlib.util.spec_from_file_location("learner_init", args.impl)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fns = {
            "random": getattr(mod, "random_bipartition", None),
            "greedy": getattr(mod, "greedy_bipartition", None),
            "grow": getattr(mod, "grow_bipartition", None),
            "legal": getattr(mod, "is_legal", None),
        }
        name = args.impl
    print(f"checking {name}")

    tiny = load_graph(HERE / "tiny_graph.json")
    star = load_graph(HERE / "star_graph.json")
    tie = load_graph(HERE / "tie_graph.json")
    bridge = load_graph(HERE / "bridge_graph.json")

    if args.dump:
        return dump({"tiny": tiny, "star": star, "tie": tie, "bridge": bridge})

    results = []

    def check(label, key, run, ok_fn, expect):
        fn = fns[key]
        if fn is None:
            results.append(None)
            print(f"SKIP  {label}   (function not defined yet)")
            return
        got = run(fn)
        ok = ok_fn(got)
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + ("" if ok else f"\n        got:      {got}\n        expected: {expect}"))
        if args.show:
            print(f"        {got}")

    def sp(g, a):
        return parts_string(a), cutsize(a, g["edges"])

    def rev(g):
        return list(reversed(g["nodes"])), list(reversed(g["edges"]))

    # --- random: seeds table ---
    want = GOLDEN["tiny_random"]
    check(f"tiny graph, random: seeds 0-{len(want) - 1} give the golden splits and cuts", "random",
          lambda f: [sp(tiny, f(tiny["nodes"], s)) for s in range(len(want))],
          lambda g: g == want, want)
    check("tiny graph, random: node order does not matter (input reversed)", "random",
          lambda f: [sp(tiny, f(rev(tiny)[0], s)) for s in range(len(want))],
          lambda g: g == want, want)
    check("tiny graph, random: every seed gives a legal 2|3 split", "legal",
          lambda f: [f(tiny["nodes"], random_bipartition(tiny["nodes"], s)) for s in range(len(want))],
          lambda g: all(g), "all True")

    # --- greedy ---
    for label, g in [("tiny", tiny), ("star", star), ("tie", tie), ("bridge", bridge)]:
        want = GOLDEN[f"{label}_greedy"]
        check(f"{label} graph, greedy: {want[0]} cut {want[1]:g}", "greedy",
              lambda f, g=g: sp(g, f(g["nodes"], g["edges"])), lambda x, want=want: x == want, want)
    check("tiny graph, greedy: input reversed gives the same split", "greedy",
          lambda f: sp(tiny, f(*rev(tiny))),
          lambda x: x == GOLDEN["tiny_greedy"], GOLDEN["tiny_greedy"])
    check("tie graph, greedy: input reversed gives the same split", "greedy",
          lambda f: sp(tie, f(*rev(tie))), lambda x: x == GOLDEN["tie_greedy"], GOLDEN["tie_greedy"])
    check("star graph, greedy: both sides stay within ceil(n/2) nodes (3|3)", "greedy",
          lambda f: is_legal(star["nodes"], f(star["nodes"], star["edges"])), lambda x: x is True, True)

    # --- grow ---
    for label, g in [("tiny", tiny), ("bridge", bridge)]:
        want = GOLDEN[f"{label}_grow"]
        check(f"{label} graph, grow: from each node gives the golden split and cut", "grow",
              lambda f, g=g: {x: sp(g, f(g["nodes"], g["edges"], x)) for x in sorted(g["nodes"])},
              lambda x, want=want: x == want, want)
    check("tiny graph, grow: input reversed gives the same splits", "grow",
          lambda f: {x: sp(tiny, f(*rev(tiny), x)) for x in sorted(tiny["nodes"])},
          lambda x: x == GOLDEN["tiny_grow"], GOLDEN["tiny_grow"])

    # --- legality ---
    one_side = {x: "0" for x in tiny["nodes"]}
    check("tiny graph, legality: everything on one side (cut 0) is NOT legal", "legal",
          lambda f: f(tiny["nodes"], one_side), lambda x: x is False, False)
    check("tiny graph, legality: a 1|4 split is NOT legal, a 2|3 split is", "legal",
          lambda f: (f(tiny["nodes"], {"A": "0", "B": "1", "C": "1", "D": "1", "E": "1"}),
                     f(tiny["nodes"], {"A": "0", "B": "0", "C": "1", "D": "1", "E": "1"})),
          lambda x: x == (False, True), (False, True))

    if not args.impl:
        # --- reference only: these use helpers that are not part of the learner API ---
        def ref(label, ok):
            results.append(ok)
            print(f"{'PASS' if ok else 'FAIL'}  {label}")

        for label, g in [("tiny", tiny), ("tie", tie), ("bridge", bridge)]:
            key = f"{label}_best"
            ref(f"{label} graph, best of greedy + all grows (no random): {GOLDEN[key]}",
                best_start(g["nodes"], g["edges"], ()) == GOLDEN[key])
        other = sp(tie, greedy_bipartition(tie["nodes"], tie["edges"], ("D", "E")))
        ref(f"tie graph, greedy anchored on D-E instead of A-B: {GOLDEN['tie_greedy_other_anchor']}",
            other == GOLDEN["tie_greedy_other_anchor"])
        leg = greedy_legacy(star["nodes"], star["edges"])
        sizes = sorted(sum(1 for v in leg.values() if v == k) for k in "01")
        ref(f"star graph, OLD greedy (no cap): {GOLDEN['star_legacy']}, cut {cutsize(leg, star['edges']):g}, "
            f"legal={is_legal(star['nodes'], leg)}", (parts_string(leg), sizes) == GOLDEN["star_legacy"]
            and not is_legal(star["nodes"], leg))
        ref(f"tiny graph, OLD greedy (forced node): {GOLDEN['tiny_legacy']}",
            sp(tiny, greedy_legacy(tiny["nodes"], tiny["edges"])) == GOLDEN["tiny_legacy"])
        swap = {"A": "E", "B": "D", "C": "C", "D": "B", "E": "A"}
        pe = [tuple(sorted((swap[u], swap[v]))) + (w,) for u, v, w in tiny["edges"]]
        pn = sorted(swap[x] for x in tiny["nodes"])
        ref(f"tiny graph renamed A<->E, B<->D, OLD greedy: {GOLDEN['tiny_legacy_renamed']} (the letters changed the answer)",
            sp({"edges": pe}, greedy_legacy(pn, pe)) == GOLDEN["tiny_legacy_renamed"])
        ref(f"tiny graph renamed, new greedy: still cut {GOLDEN['tiny_greedy'][1]:g}",
            sp({"edges": pe}, greedy_bipartition(pn, pe))[1] == GOLDEN["tiny_greedy"][1])

    if args.show:
        print("\nrandom, tiny graph:", [f"{i}:{p} {c:g}" for i, (p, c) in enumerate(GOLDEN["tiny_random"])])

    fails = sum(r is False for r in results)
    skips = sum(r is None for r in results)
    if fails:
        print(f"{fails} check(s) differ")
    else:
        print("all goldens match" + (f" ({skips} skipped)" if skips else ""))
    return 1 if fails else 0


def dump(graphs) -> int:
    """For authors: print fresh values for the GOLDEN table above."""
    def sp(g, a):
        return parts_string(a), cutsize(a, g["edges"])

    t = graphs["tiny"]
    print("tiny_random =", [sp(t, random_bipartition(t["nodes"], s)) for s in range(16)])
    for k, g in graphs.items():
        print(f"{k}_greedy =", sp(g, greedy_bipartition(g["nodes"], g["edges"])))
    for k in ("tiny", "bridge"):
        g = graphs[k]
        print(f"{k}_grow =", {x: sp(g, grow_bipartition(g["nodes"], g["edges"], x)) for x in sorted(g["nodes"])})
    for k in ("tiny", "tie", "bridge"):
        g = graphs[k]
        print(f"{k}_best =", best_start(g["nodes"], g["edges"], ()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
