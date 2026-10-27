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
    title: "Une partition valide à la main",
    level: "Initiation",
    prompt: "Petit graphe. Cliquez sur les nœuds pour mettre chacun sur un côté vous-même (sans bouton de départ). Valide veut dire : plus aucun nœud gris et aucun côté de plus de 3 nœuds.",
    hint: "Un clic met un nœud gris sur le côté 0 ; le clic suivant le passe sur le côté 1. Deux d'un côté et trois de l'autre, c'est valide.",
    setup: setup("tiny"),
    check: () => on("tiny") && M.handOnly(state) && M.legal(state),
  },
  {
    id: "hand-cut-3",
    title: "La meilleure partition à la main : coupe 3",
    level: "Initiation",
    prompt: "Petit graphe. Construisez à la main la partition valide qui a la plus petite coupe. Les arêtes rouges en pointillés sont celles que vous coupez.",
    hint: "Gardez les deux arêtes de poids 5 à l'intérieur d'un côté : A–B ensemble, D–E ensemble. Où C coupe-t-il le moins ?",
    setup: setup("tiny"),
    check: () => on("tiny") && M.handOnly(state) && M.legal(state) && cutNow() === 3,
  },
  {
    id: "grow-d-cut-3",
    title: "Croissance depuis D à la main",
    level: "Initiation",
    prompt: "Petit graphe. Cliquez sur « Croissance à la main », cliquez sur D, puis sur le nœud que la croissance ajoute ensuite : le bout de l'arête la plus lourde qui sort du côté qui grandit.",
    hint: "Le côté qui grandit s'arrête à 2 nœuds (la moitié de 5, arrondie vers le bas). L'arête la plus lourde de D est D–E (5).",
    setup: setup("tiny"),
    check: () => on("tiny") && M.handGrowOk(state, "D"),
  },
  {
    id: "grow-a-cut-5",
    title: "Corriger la croissance depuis A en un seul déplacement",
    level: "Pratique",
    prompt: "Petit graphe. Lancez « Croissance depuis A » (coupe 5). Puis déplacez exactement UN nœud pour que la partition reste valide et que la coupe tombe à 3.",
    hint: "La croissance depuis A s'arrête à A, B. Le nœud C tient à B par un poids de 4 : quel côté doit-il rejoindre ?",
    setup: setup("tiny"),
    check: () => {
      const moved = M.movedSinceStart(state);
      return on("tiny") && !state.revealed && state.base?.method.kind === "grow" && state.base.method.start === "A" &&
        moved?.length === 1 && M.legal(state) && cutNow() === 3;
    },
  },
  {
    id: "random-lucky",
    title: "Trouver une graine chanceuse",
    level: "Pratique",
    prompt: "Petit graphe. Saisissez des graines et lancez l'aléatoire jusqu'à obtenir une coupe de 3, aussi bonne que la meilleure partition. Laissez cette partition aléatoire à l'écran.",
    hint: "La plupart des graines sont malchanceuses. Essayez 0, 1, 2 … et lisez la coupe à chaque fois ; le journal liste chaque graine lancée.",
    setup: setup("tiny"),
    check: () => on("tiny") && M.isMethod(state, "random") && cutNow() === 3,
  },
  {
    id: "keep-best",
    title: "Garder la meilleure de quatre graines",
    level: "Pratique",
    prompt: "Petit graphe. Lancez l'aléatoire avec au moins quatre graines différentes. Puis remettez à l'écran la meilleure trouvée (relancez sa graine).",
    hint: "Le journal à droite liste la coupe de chaque graine essayée. La plus petite gagne ; les égalités sont acceptées.",
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
    title: "Le meilleur nœud de départ pour la croissance",
    level: "Pratique",
    prompt: "Graphe pont. Lancez la croissance depuis CHAQUE nœud, comparez les coupes dans le journal, puis laissez à l'écran une partition de croissance de plus petite coupe.",
    hint: "La croissance s'arrête à 3 nœuds. Partir du triangle de gauche garde le triangle ensemble ; partir de C ou D attire le pont.",
    setup: setup("bridge"),
    check: () => {
      const runs = M.triedKinds(state, "grow");
      const all = state.nodes.every((x) => runs.some((t) => t.start === x));
      return on("bridge") && all && M.isMethod(state, "grow") && cutNow() === Math.min(...runs.map((t) => t.cut));
    },
  },
  {
    id: "hand-grow-tie",
    title: "Croissance à la main à travers une égalité",
    level: "Approfondissement",
    prompt: "Graphe pont. Faites grandir à la main depuis C, dans l'ordre de la règle. Après le pont, quatre arêtes de poids 3 sont à égalité : la règle prend le plus petit nom.",
    hint: "C d'abord, puis D (le pont, poids 4). Ensuite C–A, C–B, D–E et D–F pèsent toutes 3 : prenez la plus petite lettre.",
    setup: setup("bridge"),
    check: () => on("bridge") && M.handGrowOk(state, "C"),
  },
  {
    id: "star-cap",
    title: "Étoile : la meilleure partition valide",
    level: "Approfondissement",
    prompt: "Graphe en étoile. Construisez à la main la partition valide de plus petite coupe. Six nœuds, donc chaque côté en contient 3. Une coupe de 5 est-elle possible si elle doit être valide ?",
    hint: "Tout autour de A du même côté donne une coupe de 5, mais c'est 5 nœuds contre 1 : pas valide. Gardez A–B (9) ensemble.",
    setup: setup("star"),
    check: () => on("star") && M.handOnly(state) && M.legal(state) && cutNow() === 15,
  },
  {
    id: "manual-beats-greedy",
    title: "Battre le glouton sur le graphe à égalité",
    level: "Approfondissement",
    prompt: "Graphe à égalité. Lancez d'abord le glouton : il s'ancre sur A–B, l'une des deux arêtes de poids 5. Puis construisez à la main une partition valide de coupe 4.",
    hint: "Le glouton garde A–B et coupe D–E. Gardez LES DEUX arêtes de poids 5 à l'intérieur, et ne coupez que des arêtes légères.",
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
    "aria-label": "Graphe",
    onChange: (e) => {
      reset(e.target.value);
      lastMsg = `Graphe changé : ${M.GRAPHS[state.graphKey].label}. La partition et le journal ont été effacés.`;
      ctx.rerender();
    },
  });
  for (const [k, g] of Object.entries(M.GRAPHS)) {
    const o = el("option", { value: k, text: g.label });
    if (k === state.graphKey) o.selected = true;
    sel.append(o);
  }
  return [
    el("label", { className: "ib-control" }, ["Graphe ", sel]),
    btn("Effacer la partition", "btn-ghost", () => {
      state = M.clearSplit(state);
      lastMsg = "Partition effacée : tous les nœuds sont de nouveau gris.";
      ctx.rerender();
    }),
  ];
}

/* ---------------- workspace panel ---------------- */

function sourceLine() {
  if (state.revealed) return "meilleure partition révélée (révision) : ne compte pas";
  if (state.method) return `${M.methodLabel(state.method)} (inchangée)`;
  if (state.handGrow) return state.handGrow.done ? "votre croissance à la main (terminée)" : "votre croissance à la main (en cours)";
  if (state.base) return `vos modifications de « ${M.methodLabel(state.base.method)} » (${M.movedSinceStart(state).length} nœud(s) déplacé(s))`;
  return "vos clics";
}

function legalLine() {
  const { s0, s1, unplaced } = M.sizesOf(state.asn);
  const cap = M.capOf(state.nodes.length);
  if (unplaced) return `valide : non (${unplaced} nœud(s) gris non placé(s))`;
  if (!s0 || !s1) return "valide : non (un côté est vide)";
  if (s0 > cap || s1 > cap) return `valide : non (un côté contient plus de ${cap})`;
  return "valide : oui";
}

function renderWorkspace(ctx) {
  drawWorkspace(ctx.canvas);
  ctx.canvas.onclick = (ev) => {
    const hit = hitNode(ctx.canvas, ev.clientX, ev.clientY, M.GRAPHS[state.graphKey].layout);
    if (hit) apply(ctx, M.clickNode(state, hit));
  };

  const box = el("div", { className: "ib-panel" });
  box.append(el("p", { className: "ib-muted", text: "Cliquez sur un nœud pour le passer de l'autre côté (gris → côté 0 → côté 1 → côté 0 …)." }));

  // 1. The three starts
  const seed = el("input", {
    id: "ib-seed",
    type: "number",
    min: "0",
    step: "1",
    className: "ib-input",
    "aria-label": "Graine aléatoire",
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
    row("Aléatoire", [seed, btn("Lancer l'aléatoire", "btn-secondary", () => apply(ctx, M.runRandom(state, seedText)))]),
    row("Glouton", [btn("Lancer le glouton", "btn-secondary", () => apply(ctx, M.runGreedy(state)))]),
    row("Croissance depuis", state.nodes.map((x) => btn(x, "btn-secondary ib-grow", () => apply(ctx, M.runGrow(state, x))))),
    row("À la main", [
      btn("Croissance à la main", "btn-secondary", () => {
        state = M.startHandGrow(state);
        lastMsg = `Croissance à la main : tous les nœuds sont sur le côté 1. Cliquez sur votre nœud de départ, puis sur chaque nœud que la croissance ajouterait, jusqu'à ce que le côté 0 en contienne ${Math.floor(state.nodes.length / 2)}.`;
        ctx.rerender();
      }),
    ]),
    row("Révision", [
      btn("Révéler la meilleure partition (révision)", "btn-ghost", () => {
        state = M.revealBest(state);
        lastMsg = "Meilleure partition valide révélée (révision) : elle ne compte pour aucun défi. Effacez la partition ou lancez un départ pour continuer.";
        ctx.rerender();
      }),
    ])
  );
  if (lastMsg) box.append(el("p", { className: "ib-msg", text: lastMsg }));

  // 2. The two numbers and where the split came from
  const { s0, s1 } = M.sizesOf(state.asn);
  const cutList = M.cutEdges(state.asn, state.edges).map((e) => `${e.u}–${e.v} ${e.w}`);
  const lines = [
    `graphe : ${M.GRAPHS[state.graphKey].label}`,
    `partition : ${M.parts(state) || "—"}`,
    `taille de coupe : ${M.cut(state)}${cutList.length ? `  (${cutList.join(", ")})` : ""}`,
    `équilibre : ${s0} | ${s1} nœuds (limite ${M.capOf(state.nodes.length)} par côté)`,
    `couleurs : bleu = côté ${blueSide()} (contient ${[...state.nodes].sort().find((n) => state.asn[n] != null) || "A"})`,
    legalLine(),
    `obtenue par : ${sourceLine()}`,
  ];
  if (state.steps.length) lines.push("", "comment le départ a été construit :", ...state.steps.map((t) => `  ${t}`));
  lines.push("", "départs lancés sur ce graphe :");
  if (state.tried.length) {
    for (const t of state.tried) lines.push(`  ${M.methodLabel(t).padEnd(22)} ${t.parts.padEnd(8)} coupe ${t.cut}${t.legal ? "" : "  (non valide)"}`);
  } else lines.push("  (aucun pour l'instant)");
  box.append(metricsBlock(lines));

  ctx.metrics.innerHTML = "";
  ctx.metrics.append(box);
}

createChallengeLab(root, {
  starterButtonLabel: "Réinitialiser",
  workspaceBeforeActions: false,
  idlePromptHtml:
    "Choisissez un défi et cliquez sur <strong>Commencer</strong>. Construisez la partition vous-même, puis <strong>Vérifier</strong>. La révélation sert à réviser : ce qu'elle montre ne compte jamais.",
  starterHtml: `
    <p><strong>Votre espace de travail :</strong> cliquez sur les nœuds pour les passer d'un côté à l'autre et observez
    la taille de coupe et l'équilibre. Lancez l'aléatoire, le glouton et la croissance, et comparez leurs coupes dans le journal.
    Les défis vérifient la partition que <em>vous</em> avez construite : un départ que vous modifiez ne compte plus comme ce départ,
    et la révélation de révision ne compte jamais.</p>
  `,
  challenges,
  loadStarter() {
    reset(state.graphKey);
  },
  extraActions,
  renderWorkspace,
});
