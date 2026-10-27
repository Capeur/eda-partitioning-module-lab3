/**
 * Initial bipartition — learner-driven lab (Lab 03).
 *
 * The learner moves nodes between the two sides by clicking them, runs the three starts
 * (random with a seed, greedy, grow from a node), grows a side by hand in the rule's order,
 * and compares cuts on four graphs. Challenges read that learner state: a split edited after a
 * start no longer counts as that start, and the study reveal never counts.
 */
import { fitGraphLayout, fitHiDpiCanvas } from "../../assets/canvas-hires.js";
import { hitNode } from "../../assets/interactive-graph-lab.js";
import { PALETTE, createChallengeLab, el, metricsBlock } from "../../assets/clustering-ui.js";
import * as M from "./initial-bipartition-lab-model.js";

const root = document.getElementById("lab-root");

let state = M.createState("tiny");
let seedText = "0"; // text in the seed box (kept across rerenders)
let lastMsg = "";

function reset(graphKey = state.graphKey) {
  state = M.createState(graphKey);
  lastMsg = "";
}

/* ---------------- drawing ---------------- */

const [BLUE, GREEN] = PALETTE;
const UNPLACED = "#94a3b8";

/** Side number drawn blue: the side holding A (first placed name), as in the slides and partsString. */
function blueSide() {
  const first = [...state.nodes].sort().find((n) => state.asn[n] != null);
  return first ? state.asn[first] : "0";
}

// Own drawing (same look as drawGraph): unplaced nodes are grey and their edges are never "cut".
function drawWorkspace(canvas) {
  const { ctx, w, h } = fitHiDpiCanvas(canvas);
  const { layout, nodeR, fontPx, edgeW } = fitGraphLayout(M.GRAPHS[state.graphKey].layout, w, h);
  const asn = state.asn;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#f7faf9";
  ctx.fillRect(0, 0, w, h);
  for (const { u, v, w: wt } of state.edges) {
    const a = layout[u];
    const b = layout[v];
    const isCut = asn[u] != null && asn[v] != null && asn[u] !== asn[v];
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.strokeStyle = isCut ? "#9f1239" : "#94a3b8";
    ctx.lineWidth = isCut ? edgeW * 1.6 : edgeW;
    if (isCut) ctx.setLineDash([9, 5]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.font = `${Math.max(11, fontPx - 1)}px ui-monospace, Menlo, Consolas, monospace`;
    ctx.fillStyle = isCut ? "#9f1239" : "#334155";
    ctx.fillText(String(wt), (a.x + b.x) / 2 + 4, (a.y + b.y) / 2 - 4);
  }
  const order = state.handGrow ? state.handGrow.order : [];
  const blue = blueSide();
  for (const n of state.nodes) {
    const p = layout[n];
    ctx.beginPath();
    ctx.arc(p.x, p.y, nodeR, 0, Math.PI * 2);
    ctx.fillStyle = asn[n] == null ? UNPLACED : asn[n] === blue ? BLUE : GREEN;
    ctx.fill();
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = "#fff";
    ctx.font = `bold ${fontPx}px system-ui, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(n, p.x, p.y);
    const k = order.indexOf(n);
    if (k >= 0) {
      // grow order badge: 1, 2, 3 …
      ctx.beginPath();
      ctx.arc(p.x + nodeR * 0.85, p.y - nodeR * 0.85, nodeR * 0.45, 0, Math.PI * 2);
      ctx.fillStyle = "#b45309";
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.font = `bold ${Math.max(10, fontPx - 4)}px system-ui, sans-serif`;
      ctx.fillText(String(k + 1), p.x + nodeR * 0.85, p.y - nodeR * 0.85);
    }
  }
  ctx.textAlign = "start";
  ctx.textBaseline = "alphabetic";
}

/* ---------------- challenges (all read learner state) ---------------- */

const on = (key) => state.graphKey === key;
const setup = (graphKey) => () => reset(graphKey);
const cutNow = () => M.cut(state);

const challenges = [
  {
    id: "two-sides",
    title: "A legal split by hand",
    level: "Intro",
    prompt: "Tiny graph. Click nodes to put every node on a side yourself (no start button). Legal means no grey node left and no side with more than 3 nodes.",
    hint: "One click puts a grey node on side 0; the next click moves it to side 1. Two on one side and three on the other is legal.",
    setup: setup("tiny"),
    check: () => on("tiny") && M.handOnly(state) && M.legal(state),
  },
  {
    id: "hand-cut-3",
    title: "Best split by hand: cut 3",
    level: "Intro",
    prompt: "Tiny graph. Build by hand the legal split with the smallest cut. The red dashed edges are the ones you cut.",
    hint: "Keep both weight-5 edges inside a side: A–B together, D–E together. Where does C cut less?",
    setup: setup("tiny"),
    check: () => on("tiny") && M.handOnly(state) && M.legal(state) && cutNow() === 3,
  },
  {
    id: "grow-d-cut-3",
    title: "Grow from D by hand",
    level: "Intro",
    prompt: "Tiny graph. Press “Grow by hand”, click D, then click the node that grow adds next: the end of the heaviest edge leaving the grown side.",
    hint: "The grown side stops at 2 nodes (half of 5, rounded down). D's heaviest edge is D–E (5).",
    setup: setup("tiny"),
    check: () => on("tiny") && M.handGrowOk(state, "D"),
  },
  {
    id: "grow-a-cut-5",
    title: "Fix grow from A with one move",
    level: "Practice",
    prompt: "Tiny graph. Run “Grow from A” (cut 5). Then move exactly ONE node so the split stays legal and the cut drops to 3.",
    hint: "Grow from A stops at A, B. Node C hangs on B with weight 4: which side should it join?",
    setup: setup("tiny"),
    check: () => {
      const moved = M.movedSinceStart(state);
      return on("tiny") && !state.revealed && state.base?.method.kind === "grow" && state.base.method.start === "A" &&
        moved?.length === 1 && M.legal(state) && cutNow() === 3;
    },
  },
  {
    id: "random-lucky",
    title: "Find a lucky seed",
    level: "Practice",
    prompt: "Tiny graph. Type seeds and run random until the split has cut 3, as good as the best split. Leave that random split on screen.",
    hint: "Most seeds are unlucky. Try 0, 1, 2 … and read the cut each time; the log lists every seed you ran.",
    setup: setup("tiny"),
    check: () => on("tiny") && M.isMethod(state, "random") && cutNow() === 3,
  },
  {
    id: "keep-best",
    title: "Keep the best of four seeds",
    level: "Practice",
    prompt: "Tiny graph. Run random with at least four different seeds. Then put the best one you found back on screen (run its seed again).",
    hint: "The log on the right lists the cut of every seed you tried. The smallest one wins; ties are fine.",
    setup: setup("tiny"),
    check: () => {
      const runs = M.triedKinds(state, "random");
      const best = Math.min(...runs.map((t) => t.cut));
      return on("tiny") && runs.length >= 4 && M.isMethod(state, "random") &&
        runs.some((t) => t.seed === state.method.seed) && cutNow() === best;
    },
  },
  {
    id: "grow-best-start",
    title: "Best start node for grow",
    level: "Practice",
    prompt: "Bridge graph. Run grow from EVERY node, compare the cuts in the log, then leave a grow split with the smallest cut on screen.",
    hint: "Grow stops at 3 nodes. Starting on the left triangle keeps the triangle together; starting at C or D pulls the bridge in.",
    setup: setup("bridge"),
    check: () => {
      const runs = M.triedKinds(state, "grow");
      const all = state.nodes.every((x) => runs.some((t) => t.start === x));
      return on("bridge") && all && M.isMethod(state, "grow") && cutNow() === Math.min(...runs.map((t) => t.cut));
    },
  },
  {
    id: "hand-grow-tie",
    title: "Grow by hand through a tie",
    level: "Stretch",
    prompt: "Bridge graph. Grow by hand from C, in the rule's order. After the bridge, four edges of weight 3 tie: the rule takes the smaller name.",
    hint: "C first, then D (the bridge, weight 4). Then C–A, C–B, D–E and D–F all weigh 3: pick the smallest letter.",
    setup: setup("bridge"),
    check: () => on("bridge") && M.handGrowOk(state, "C"),
  },
  {
    id: "star-cap",
    title: "Star: the best legal split",
    level: "Stretch",
    prompt: "Star graph. Build by hand the legal split with the smallest cut. Six nodes, so each side holds 3. Is cut 5 possible if it must be legal?",
    hint: "Everything around A on one side gives cut 5, but that is 5 nodes against 1: not legal. Keep A–B (9) together.",
    setup: setup("star"),
    check: () => on("star") && M.handOnly(state) && M.legal(state) && cutNow() === 15,
  },
  {
    id: "manual-beats-greedy",
    title: "Beat greedy on the tie graph",
    level: "Stretch",
    prompt: "Tie graph. Run greedy first: it anchors on A–B, one of two edges of weight 5. Then build by hand a legal split with cut 4.",
    hint: "Greedy keeps A–B and cuts D–E. Keep BOTH weight-5 edges inside, and cut only light edges.",
    setup: setup("tie"),
    check: () => on("tie") && M.triedKinds(state, "greedy").length > 0 && !state.method && !state.revealed &&
      !state.handGrow && M.legal(state) && cutNow() === 4,
  },
];

/* ---------------- controls ---------------- */

function btn(text, cls, onClick, disabled = false) {
  return el("button", { className: `btn ${cls}`, type: "button", text, onClick, disabled });
}

function apply(ctx, res) {
  state = res.state;
  lastMsg = res.msg;
  ctx.rerender();
}

function extraActions(ctx) {
  const sel = el("select", {
    id: "ib-graph",
    "aria-label": "Graph",
    onChange: (e) => {
      reset(e.target.value);
      lastMsg = `Graph changed to ${M.GRAPHS[state.graphKey].label}: the split and the log were cleared.`;
      ctx.rerender();
    },
  });
  for (const [k, g] of Object.entries(M.GRAPHS)) {
    const o = el("option", { value: k, text: g.label });
    if (k === state.graphKey) o.selected = true;
    sel.append(o);
  }
  return [
    el("label", { className: "ib-control" }, ["Graph ", sel]),
    btn("Clear split", "btn-ghost", () => {
      state = M.clearSplit(state);
      lastMsg = "Split cleared: every node is grey again.";
      ctx.rerender();
    }),
  ];
}

/* ---------------- workspace panel ---------------- */

function sourceLine() {
  if (state.revealed) return "revealed best split (study) — does not count";
  if (state.method) return `${M.methodLabel(state.method)} (unchanged)`;
  if (state.handGrow) return state.handGrow.done ? "your hand grow (finished)" : "your hand grow (in progress)";
  if (state.base) return `your edits of ${M.methodLabel(state.base.method)} (${M.movedSinceStart(state).length} node(s) moved)`;
  return "your clicks";
}

function legalLine() {
  const { s0, s1, unplaced } = M.sizesOf(state.asn);
  const cap = M.capOf(state.nodes.length);
  if (unplaced) return `legal: no (${unplaced} grey node(s) not placed)`;
  if (!s0 || !s1) return "legal: no (one side is empty)";
  if (s0 > cap || s1 > cap) return `legal: no (a side holds more than ${cap})`;
  return "legal: yes";
}

function renderWorkspace(ctx) {
  drawWorkspace(ctx.canvas);
  ctx.canvas.onclick = (ev) => {
    const hit = hitNode(ctx.canvas, ev.clientX, ev.clientY, M.GRAPHS[state.graphKey].layout);
    if (hit) apply(ctx, M.clickNode(state, hit));
  };

  const box = el("div", { className: "ib-panel" });
  box.append(el("p", { className: "ib-muted", text: "Click a node to move it to the other side (grey → side 0 → side 1 → side 0 …)." }));

  // 1. The three starts
  const seed = el("input", {
    id: "ib-seed",
    type: "number",
    min: "0",
    step: "1",
    className: "ib-input",
    "aria-label": "Random seed",
    value: seedText,
    onInput: (e) => {
      seedText = e.target.value;
    },
    onKeydown: (e) => {
      if (e.key === "Enter") apply(ctx, M.runRandom(state, seedText));
    },
  });
  const row = (label, items) => el("div", { className: "tool-actions ib-row" }, [el("span", { className: "ib-label", text: label }), ...items]);
  box.append(
    row("Random", [seed, btn("Run random", "btn-secondary", () => apply(ctx, M.runRandom(state, seedText)))]),
    row("Greedy", [btn("Run greedy", "btn-secondary", () => apply(ctx, M.runGreedy(state)))]),
    row("Grow from", state.nodes.map((x) => btn(x, "btn-secondary ib-grow", () => apply(ctx, M.runGrow(state, x))))),
    row("By hand", [
      btn("Grow by hand", "btn-secondary", () => {
        state = M.startHandGrow(state);
        lastMsg = `Grow by hand: all nodes are on side 1. Click your start node, then each node grow would add, until side 0 holds ${Math.floor(state.nodes.length / 2)}.`;
        ctx.rerender();
      }),
    ]),
    row("Study", [
      btn("Reveal best split (study)", "btn-ghost", () => {
        state = M.revealBest(state);
        lastMsg = "Best legal split revealed (study): it does not count for any challenge. Clear the split or run a start to go on.";
        ctx.rerender();
      }),
    ])
  );
  if (lastMsg) box.append(el("p", { className: "ib-msg", text: lastMsg }));

  // 2. The two numbers and where the split came from
  const { s0, s1 } = M.sizesOf(state.asn);
  const cutList = M.cutEdges(state.asn, state.edges).map((e) => `${e.u}–${e.v} ${e.w}`);
  const lines = [
    `graph: ${M.GRAPHS[state.graphKey].label}`,
    `split: ${M.parts(state) || "—"}`,
    `cutsize: ${M.cut(state)}${cutList.length ? `  (${cutList.join(", ")})` : ""}`,
    `balance: ${s0} | ${s1} nodes (limit ${M.capOf(state.nodes.length)} per side)`,
    `colours: blue = side ${blueSide()} (has ${[...state.nodes].sort().find((n) => state.asn[n] != null) || "A"})`,
    legalLine(),
    `made by: ${sourceLine()}`,
  ];
  if (state.steps.length) lines.push("", "how the start was built:", ...state.steps.map((t) => `  ${t}`));
  lines.push("", "starts you ran on this graph:");
  if (state.tried.length) {
    for (const t of state.tried) lines.push(`  ${M.methodLabel(t).padEnd(15)} ${t.parts.padEnd(8)} cut ${t.cut}${t.legal ? "" : "  (not legal)"}`);
  } else lines.push("  (none yet)");
  box.append(metricsBlock(lines));

  ctx.metrics.innerHTML = "";
  ctx.metrics.append(box);
}

createChallengeLab(root, {
  starterButtonLabel: "Reset workspace",
  workspaceBeforeActions: false,
  idlePromptHtml:
    "Pick a challenge and click <strong>Start</strong>. Build the split yourself, then <strong>Check</strong>. The reveal is for study: what it shows never counts.",
  starterHtml: `
    <p><strong>Your workspace:</strong> click nodes to move them between the two sides and watch the
    cutsize and the balance. Run random, greedy and grow, and compare their cuts in the log.
    Challenges check the split <em>you</em> built: a start you edit no longer counts as that start,
    and the study reveal never counts.</p>
  `,
  challenges,
  loadStarter() {
    reset(state.graphKey);
  },
  extraActions,
  renderWorkspace,
});
