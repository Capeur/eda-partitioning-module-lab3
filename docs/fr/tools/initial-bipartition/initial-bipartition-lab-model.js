/**
 * initial-bipartition-lab-model.js — pure state + rules for the Lab 03 initial-bipartition lab
 * (no DOM, so it can be unit-tested in Node).
 *
 * Mirrors Track A: courses/learn_partitioning/module01-03-initial-bipartition/examples/
 * initial_bipartition_check.py (random, greedy, grow, is_legal). Same rules, same tie-breaks:
 *   random = mulberry32(seed), throw away two numbers, Fisher–Yates over the sorted names,
 *            side 0 = first floor(n/2) names
 *   greedy = anchor on the heaviest edge (ties: smaller u, v), side-1 seed = loosest node,
 *            then place by least added cut, no side above ceil(n/2), ties to side 0
 *   grow   = from a start node, add the end of the heaviest edge leaving the grown set
 *            (ties: smaller name) until floor(n/2) nodes
 * A split is legal when every node is on side "0" or "1" and both sides hold 1..ceil(n/2) nodes.
 */
import { mulberry32 } from "../../assets/partitioning-core.js";

const G = (nodes, edges) => ({ nodes, edges: edges.map(([u, v, w]) => ({ u, v, w })) });

/** Same graphs as the module's examples/*.json (the model test checks they match). */
export const GRAPHS = {
  tiny: {
    label: "Petit graphe (A–E)",
    data: G(["A", "B", "C", "D", "E"], [["A", "B", 5], ["A", "C", 1], ["B", "C", 4], ["C", "D", 2], ["D", "E", 5], ["C", "E", 1]]),
    layout: { A: { x: 90, y: 80 }, B: { x: 220, y: 60 }, C: { x: 160, y: 160 }, D: { x: 280, y: 200 }, E: { x: 120, y: 240 } },
  },
  star: {
    label: "Graphe en étoile (limite de taille)",
    data: G(["A", "B", "C", "D", "E", "F"], [["A", "B", 9], ["A", "C", 5], ["A", "D", 5], ["A", "E", 5], ["A", "F", 5]]),
    layout: { A: { x: 200, y: 150 }, B: { x: 330, y: 150 }, C: { x: 200, y: 40 }, D: { x: 90, y: 90 }, E: { x: 90, y: 210 }, F: { x: 200, y: 260 } },
  },
  tie: {
    label: "Graphe à égalité (deux arêtes les plus lourdes)",
    data: G(["A", "B", "C", "D", "E", "F"], [["A", "B", 5], ["A", "E", 3], ["B", "F", 3], ["C", "D", 1], ["D", "E", 5], ["E", "F", 1]]),
    layout: { A: { x: 80, y: 60 }, B: { x: 260, y: 60 }, E: { x: 80, y: 170 }, F: { x: 260, y: 170 }, D: { x: 80, y: 280 }, C: { x: 260, y: 280 } },
  },
  bridge: {
    label: "Graphe pont (fil lourd au milieu)",
    data: G(["A", "B", "C", "D", "E", "F"], [["A", "B", 3], ["A", "C", 3], ["B", "C", 3], ["C", "D", 4], ["D", "E", 3], ["D", "F", 3], ["E", "F", 3]]),
    layout: { A: { x: 40, y: 60 }, B: { x: 40, y: 240 }, C: { x: 150, y: 150 }, D: { x: 290, y: 150 }, E: { x: 400, y: 60 }, F: { x: 400, y: 240 } },
  },
};

/* ---------------- graph helpers ---------------- */

const byName = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
const norm = (e) => (e.u < e.v ? e : { u: e.v, v: e.u, w: e.w });

function adjacency(edges) {
  const adj = {};
  for (const { u, v, w } of edges) {
    (adj[u] ||= {})[v] = (adj[u][v] || 0) + w;
    (adj[v] ||= {})[u] = (adj[v][u] || 0) + w;
  }
  return adj;
}

/** Weight of edges whose two ends are on different sides (unplaced nodes cut nothing). */
export function cutOf(asn, edges) {
  let t = 0;
  for (const { u, v, w } of edges) if (asn[u] != null && asn[v] != null && asn[u] !== asn[v]) t += w;
  return t;
}

export function cutEdges(asn, edges) {
  return edges.filter(({ u, v }) => asn[u] != null && asn[v] != null && asn[u] !== asn[v]).map(norm);
}

/** "ABC|DE": each side's names sorted, sides sorted (labels 0/1 do not matter). */
export function partsOf(asn) {
  const g = {};
  for (const [n, s] of Object.entries(asn)) if (s != null) (g[s] ||= []).push(n);
  return Object.values(g).map((a) => a.sort(byName).join("")).sort(byName).join("|");
}

export const capOf = (n) => Math.ceil(n / 2);

export function sizesOf(asn) {
  const v = Object.values(asn);
  return { s0: v.filter((x) => x === "0").length, s1: v.filter((x) => x === "1").length, unplaced: v.filter((x) => x == null).length };
}

export function isLegal(nodes, asn) {
  if (!nodes.every((n) => asn[n] === "0" || asn[n] === "1")) return false;
  const { s0, s1 } = sizesOf(asn);
  const cap = capOf(nodes.length);
  return s0 > 0 && s0 <= cap && s1 > 0 && s1 <= cap;
}

/* ---------------- the three starts (same rules as the checker) ---------------- */

export function randomBipartition(nodes, seed) {
  const order = [...nodes].sort(byName);
  const rng = mulberry32(seed);
  rng();
  rng(); // warm-up: small seeds start out alike
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  const left = new Set(order.slice(0, Math.floor(order.length / 2)));
  return { asn: Object.fromEntries([...nodes].sort(byName).map((n) => [n, left.has(n) ? "0" : "1"])), order };
}

/** Returns { asn, steps } where steps explain each placement (shown after a run). */
export function greedyBipartition(nodes, edges, anchor = null) {
  const names = [...nodes].sort(byName);
  const n = names.length;
  const cap = capOf(n);
  const adj = adjacency(edges);
  const side = {};
  const steps = [];
  let u0, v0;
  if (anchor) [u0, v0] = anchor;
  else if (edges.length) {
    const best = edges.map(norm).reduce((a, e) => (e.w > a.w || (e.w === a.w && (e.u < a.u || (e.u === a.u && e.v < a.v))) ? e : a));
    u0 = best.u;
    v0 = best.v;
  } else [u0, v0] = names;
  side[u0] = side[v0] = "0";
  steps.push(`ancre ${u0}–${v0} (arête la plus lourde) → côté 0`);
  const todo = names.filter((x) => !(x in side));
  if (!todo.length) {
    side[v0] = "1";
    return { asn: Object.fromEntries(names.map((x) => [x, side[x]])), steps };
  }
  const tie = (x) => Object.entries(adj[x] || {}).reduce((t, [y, w]) => t + (y in side ? w : 0), 0);
  const seed1 = todo.reduce((a, x) => (tie(x) < tie(a) || (tie(x) === tie(a) && x < a) ? x : a));
  steps.push(`${seed1} → côté 1 (lien le plus faible avec l'ancre : ${tie(seed1)})`);
  side[seed1] = "1";
  todo.splice(todo.indexOf(seed1), 1);
  while (todo.length) {
    const x = todo.reduce((a, y) => (tie(y) > tie(a) || (tie(y) === tie(a) && y < a) ? y : a));
    todo.splice(todo.indexOf(x), 1);
    let to0 = 0;
    let to1 = 0;
    for (const [y, w] of Object.entries(adj[x] || {})) {
      if (side[y] === "0") to0 += w;
      else if (side[y] === "1") to1 += w;
    }
    const n0 = Object.values(side).filter((s) => s === "0").length;
    const n1 = Object.keys(side).length - n0;
    const add0 = to1;
    const add1 = to0;
    let pick;
    let why;
    if (n0 >= cap) [pick, why] = ["1", "le côté 0 est plein"];
    else if (n1 >= cap) [pick, why] = ["0", "le côté 1 est plein"];
    else
      [pick, why] = add0 <= add1
        ? ["0", `coupe +${add0} ; le côté 1 ajouterait ${add1}`]
        : ["1", `coupe +${add1} ; le côté 0 ajouterait ${add0}`];
    side[x] = pick;
    steps.push(`${x} → côté ${pick} (${why})`);
  }
  return { asn: Object.fromEntries(names.map((x) => [x, side[x]])), steps };
}

/** Returns { asn, order, steps }: order = nodes in the order grow takes them. */
export function growBipartition(nodes, edges, start) {
  const names = [...nodes].sort(byName);
  const adj = adjacency(edges);
  const target = Math.floor(names.length / 2);
  const grown = [start];
  const steps = [`départ ${start}`];
  while (grown.length < target) {
    let best = null;
    for (const u of grown)
      for (const [v, w] of Object.entries(adj[u] || {})) {
        if (grown.includes(v)) continue;
        if (!best || w > best.w || (w === best.w && v < best.v)) best = { w, u, v };
      }
    if (!best) {
      best = { w: 0, u: null, v: names.find((x) => !grown.includes(x)) };
      steps.push(`aucune arête ne sort : on prend ${best.v}`);
    } else steps.push(`+ ${best.v} (arête ${best.u}–${best.v}, poids ${best.w})`);
    grown.push(best.v);
  }
  return { asn: Object.fromEntries(names.map((x) => [x, grown.includes(x) ? "0" : "1"])), order: grown, steps };
}

/** The legal split with the smallest cut (study reveal). Ties: first found, node 1 on side 0. */
export function bestLegal(nodes, edges) {
  const names = [...nodes].sort(byName);
  let best = null;
  for (let mask = 0; mask < 1 << names.length; mask++) {
    const asn = Object.fromEntries(names.map((x, i) => [x, mask & (1 << i) ? "1" : "0"]));
    if (!isLegal(names, asn)) continue;
    const c = cutOf(asn, edges);
    if (!best || c < best.cut) best = { asn, cut: c };
  }
  return best;
}

/* ---------------- state ---------------- */

/**
 * State fields:
 *  asn       node → "0" | "1" | null (null = not placed yet)
 *  method    the start that produced the split on screen, or null once the learner edits it
 *  base      { method, asn } of the last start run since Clear (the split edits started from)
 *  tried     every start run on this graph: { key, kind, seed?, start?, parts, cut, legal }
 *  handGrow  { order, done } while / after growing by hand; null once edited
 *  revealed  the best split was revealed (study): nothing counts until Clear or a new start
 */
export function createState(graphKey = "tiny") {
  const g = GRAPHS[graphKey];
  return {
    graphKey,
    nodes: [...g.data.nodes],
    edges: g.data.edges.map((e) => ({ ...e })),
    asn: Object.fromEntries(g.data.nodes.map((n) => [n, null])),
    method: null,
    base: null,
    tried: [],
    handGrow: null,
    revealed: false,
    steps: [],
  };
}

export const cloneState = (s) => JSON.parse(JSON.stringify(s));

export const cut = (s) => cutOf(s.asn, s.edges);
export const legal = (s) => isLegal(s.nodes, s.asn);
export const parts = (s) => partsOf(s.asn);

export function methodLabel(m) {
  if (!m) return null;
  if (m.kind === "random") return `aléatoire graine ${m.seed}`;
  if (m.kind === "grow") return `croissance depuis ${m.start}`;
  return "glouton";
}

const methodKey = (m) => (m.kind === "random" ? `random:${m.seed}` : m.kind === "grow" ? `grow:${m.start}` : "greedy");

function applyStart(s, method, res) {
  const n = cloneState(s);
  n.asn = { ...res.asn };
  n.method = method;
  n.base = { method, asn: { ...res.asn } };
  n.revealed = false;
  n.handGrow = null;
  n.steps = res.steps || [];
  const entry = { key: methodKey(method), ...method, parts: partsOf(res.asn), cut: cutOf(res.asn, s.edges), legal: isLegal(s.nodes, res.asn) };
  n.tried = n.tried.filter((t) => t.key !== entry.key).concat(entry);
  return n;
}

export function runRandom(s, seed) {
  const k = Number(seed);
  if (!Number.isInteger(k) || k < 0) return { state: s, msg: "Saisissez un entier supérieur ou égal à 0 comme graine." };
  const res = randomBipartition(s.nodes, k);
  const n = applyStart(s, { kind: "random", seed: k }, { ...res, steps: [`ordre mélangé : ${res.order.join(" ")}`, `côté 0 = les ${Math.floor(s.nodes.length / 2)} premiers noms`] });
  return { state: n, msg: `Aléatoire, graine ${k} : ${parts(n)}, coupe ${cut(n)}.` };
}

export function runGreedy(s) {
  const n = applyStart(s, { kind: "greedy" }, greedyBipartition(s.nodes, s.edges));
  return { state: n, msg: `Glouton : ${parts(n)}, coupe ${cut(n)}.` };
}

export function runGrow(s, start) {
  const n = applyStart(s, { kind: "grow", start }, growBipartition(s.nodes, s.edges, start));
  return { state: n, msg: `Croissance depuis ${start} : ${parts(n)}, coupe ${cut(n)}.` };
}

/** Learner moves one node to the other side (an unplaced node goes to side 0). */
export function flipNode(s, id) {
  if (!(id in s.asn)) return { state: s, msg: "" };
  const n = cloneState(s);
  n.asn[id] = s.asn[id] === "0" ? "1" : "0";
  const wasMethod = s.method;
  n.method = null; // an edited split no longer counts as the start that made it
  n.handGrow = null;
  n.steps = [];
  const msg = wasMethod ? `${id} → côté ${n.asn[id]}. Vous avez modifié la partition « ${methodLabel(wasMethod)} » : elle compte maintenant comme la vôtre.` : `${id} → côté ${n.asn[id]}.`;
  return { state: n, msg };
}

export function clearSplit(s) {
  const n = cloneState(s);
  n.asn = Object.fromEntries(s.nodes.map((x) => [x, null]));
  n.method = null;
  n.base = null;
  n.handGrow = null;
  n.revealed = false;
  n.steps = [];
  return n;
}

/** Study aid: show the best legal split. It never counts for a challenge. */
export function revealBest(s) {
  const n = cloneState(s);
  n.asn = { ...bestLegal(s.nodes, s.edges).asn };
  n.method = null;
  n.base = null;
  n.handGrow = null;
  n.revealed = true;
  n.steps = [];
  return n;
}

/** Grow by hand: everyone starts on side 1; each click moves one node to side 0. */
export function startHandGrow(s) {
  const n = clearSplit(s);
  n.asn = Object.fromEntries(s.nodes.map((x) => [x, "1"]));
  n.handGrow = { order: [], done: false };
  return n;
}

export function handGrowClick(s, id) {
  if (!s.handGrow || s.handGrow.done) return flipNode(s, id);
  if (s.asn[id] === "0") return { state: s, msg: `${id} est déjà dans le côté qui grandit.` };
  const n = cloneState(s);
  n.asn[id] = "0";
  n.handGrow.order.push(id);
  const target = Math.floor(s.nodes.length / 2);
  n.handGrow.done = n.handGrow.order.length >= target;
  const msg = n.handGrow.done
    ? `Côté qui grandit : ${n.handGrow.order.join(", ")} (${target} nœuds). Terminé : cliquez sur Vérifier.`
    : `Côté qui grandit : ${n.handGrow.order.join(", ")}. Cliquez sur le nœud que la croissance prendrait ensuite.`;
  return { state: n, msg };
}

export const clickNode = (s, id) => (s.handGrow && !s.handGrow.done ? handGrowClick(s, id) : flipNode(s, id));

/* ---------------- challenge predicates (read learner state only) ---------------- */

const sameAsn = (a, b) => Object.keys({ ...a, ...b }).every((k) => a[k] === b[k]);

/** Built by clicking only: no start run since Clear, nothing revealed, not a hand grow. */
export const handOnly = (s) => !s.base && !s.revealed && !s.handGrow && !s.method;

/** The split on screen is exactly the result of this start, not edited since. */
export function isMethod(s, kind, extra = {}) {
  const m = s.method;
  if (!m || s.revealed || m.kind !== kind) return false;
  return Object.entries(extra).every(([k, v]) => m[k] === v) && sameAsn(s.asn, s.base.asn);
}

/** Nodes whose side differs from the start the edits began from. */
export function movedSinceStart(s) {
  if (!s.base) return null;
  return s.nodes.filter((x) => s.asn[x] !== s.base.asn[x]);
}

/** The hand grow is finished, untouched since, and follows the grow rule from its first node. */
export function handGrowOk(s, start = null) {
  const h = s.handGrow;
  if (!h || !h.done || s.revealed || !h.order.length) return false;
  if (start && h.order[0] !== start) return false;
  const want = growBipartition(s.nodes, s.edges, h.order[0]);
  return want.order.join() === h.order.join() && sameAsn(s.asn, want.asn);
}

export const triedKinds = (s, kind) => s.tried.filter((t) => t.kind === kind);
