/* lesson-engine.js — animated, narrated lesson player for graph labs (eda-learning).
 *
 * LessonEngine.mount({ sb, timing, lang, audioId?, rootId?, ui?, storageKey? })
 *   sb      storyboard (see reference/storyboard.md): graph, poses, timeline, show windows, overlays, question...
 *   timing  { lang, duration, sentences: [{ slide, text, start, end, words: [{ w, t }] }] }
 *           made by scripts/voice_build.py (edge-tts word timings) or scripts/timing_from_vtt.py
 *   lang    "en" | "fr": picks the anchor word and the text of every overlay
 *
 * Everything on screen is a pure function of the audio time t, so seeking, speed changes and frame-by-frame
 * recording all show the same picture. A new key in a track starts from wherever the previous move had got to
 * (no jumps). window.__lesson exposes the internals the checker uses.
 */
(function () {
  "use strict";

  const I18N = {
    en: {
      play: "Play", pause: "Pause", position: "Position in the lesson", speed: "Playback speed", captions: "CC",
      chapters: "Chapters", yourSplit: "Your split", back: "Back to the lesson",
      paused: "Paused. You are building your own split.", turn: "Pause and guess",
      deal: "Deal a random split with seed", dealBtn: "Deal",
      clickHint: "Or click the nodes on the stage to move them from one side to the other.",
      noSplit: "No split yet. Deal a seed or click a node.", noSplitNoDeal: "No split yet. Click a node to start.",
      backMsg: "Back in the lesson. Click a node to try again.",
      cut: "cut", sides: "sides", legal: "legal", notLegal: "not legal: at most {cap} per side",
      toPlace: "still to place: {list}", cutsize: "cutsize", perSide: "cells per side", max: "max {cap}",
      think: "Take a moment to think, then pick one.", seed: "Seed {s}: ", yours: "Your split: ",
      cell: "Cell {n}: click to move it to the other side", lesson: "Animated lesson", graph: "Graph",
      verdictYes: "legal", verdictNo: "not legal",
    },
    fr: {
      play: "Lecture", pause: "Pause", position: "Position dans la leçon", speed: "Vitesse de lecture", captions: "ST",
      chapters: "Chapitres", yourSplit: "Votre partition", back: "Revenir à la leçon",
      paused: "En pause. Vous construisez votre propre partition.", turn: "Faites une pause et devinez",
      deal: "Distribuer une partition au hasard avec la graine", dealBtn: "Distribuer",
      clickHint: "Ou cliquez sur les nœuds de la scène pour les changer de côté.",
      noSplit: "Pas encore de partition. Distribuez une graine ou cliquez sur un nœud.",
      noSplitNoDeal: "Pas encore de partition. Cliquez sur un nœud pour commencer.",
      backMsg: "De retour dans la leçon. Cliquez sur un nœud pour réessayer.",
      cut: "coupe", sides: "côtés", legal: "valide", notLegal: "non valide : {cap} au plus par côté",
      toPlace: "reste à placer : {list}", cutsize: "taille de coupe", perSide: "cellules par côté", max: "max {cap}",
      think: "Prenez un moment pour réfléchir, puis choisissez.", seed: "Graine {s} : ", yours: "Votre partition : ",
      cell: "Cellule {n} : cliquez pour la changer de côté", lesson: "Leçon animée", graph: "Graphe",
      verdictYes: "valide", verdictNo: "non valide",
    },
  };

  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const ease = (p) => { p = clamp(p); return p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; };
  const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const norm = (w) => w.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");
  /** Keys a spoken word can be matched by: the whole word, and the part after an apostrophe (l'arête → arete). */
  const wordKeys = (w) => { const k = [norm(w)]; const m = w.split(/['’]/); if (m.length > 1) k.push(norm(m[m.length - 1])); return k; };
  const fill = (s, o) => s.replace(/\{(\w+)\}/g, (m, k) => (o[k] !== undefined ? o[k] : m));

  const FULL = [0, 0, 960, 540];
  const DUR_POSE = 1.1, DUR_CAM = 1.3, DUR_SHAPE = 0.9, DUR_WIRES = 1.0, DUR_DIM = 0.6, DUR_COUNT = 1.2;

  function mount(cfg) {
    const sb = cfg.sb, TM = cfg.timing, lang = cfg.lang || "en";
    const T = Object.assign({}, I18N[lang] || I18N.en, cfg.ui || {});
    const L = (v) => (v == null ? "" : typeof v === "string" ? v : v[lang] != null ? v[lang] : v.en != null ? v.en : "");
    const errors = [];
    const err = (m) => { errors.push(m); console.error("[lesson] " + m); };
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const D = reduce ? 0.001 : 1;

    /* ---------------- timing ---------------- */
    const SENT = TM.sentences.map((s) => {
      const words = s.words.map((w) => ({ w: w.w, t: w.t, keys: wordKeys(w.w) }));
      words.forEach((w, i) => { w.e = i + 1 < words.length ? words[i + 1].t : s.end; });
      return Object.assign({}, s, { words });
    });
    const DUR = TM.duration;
    const slideSents = (n) => SENT.filter((s) => s.slide === n);

    function findWords(obj, label) {
      const needle = obj[lang] != null ? obj[lang] : null;
      if (needle == null) { err(`anchor ${label}: no "${lang}" word given`); return null; }
      const [phrase, nthTxt] = String(needle).split("#");
      const nth = nthTxt != null ? parseInt(nthTxt, 10) : obj.nth || 0;
      const toks = phrase.split(/\s+/).map(norm).filter(Boolean);
      const pool = obj.slide != null ? slideSents(obj.slide) : SENT;
      if (!pool.length) { err(`anchor ${label}: slide ${obj.slide} has no narration in this part`); return null; }
      const ws = pool.flatMap((s) => s.words);
      let hit = 0;
      for (let i = 0; i + toks.length <= ws.length; i++) {
        if (toks.every((tk, j) => ws[i + j].keys.some((k) => k.startsWith(tk)))) {
          if (hit++ === nth) return { first: ws[i], last: ws[i + toks.length - 1] };
        }
      }
      err(`anchor ${label}: "${needle}" not found in slide ${obj.slide} (${lang}). Words: ${ws.map((w) => w.w).join(" ")}`);
      return null;
    }
    const anchorCache = new Map();
    function resolve(ref, label = "") {
      if (ref == null) return 0;
      if (typeof ref === "number") return ref;
      const key = typeof ref === "string" ? ref : JSON.stringify(ref);
      if (anchorCache.has(key)) return anchorCache.get(key);
      let t = 0;
      if (typeof ref === "string") {
        const m = ref.trim().match(/^(@[\w-]+|slide:\d+(?::end)?|end|start)\s*(?:([+-])\s*([\d.]+))?$/);
        if (!m) { err(`bad time reference "${ref}" ${label}`); return 0; }
        const shift = m[2] ? (m[2] === "-" ? -1 : 1) * parseFloat(m[3]) : 0;
        const base = m[1];
        if (base[0] === "@") {
          const a = sb.anchors && sb.anchors[base.slice(1)];
          if (!a) { err(`unknown anchor ${base} ${label}`); t = 0; } else t = resolveObj(a, base);
        } else if (base === "end") t = DUR;
        else if (base === "start") t = 0;
        else {
          const [, n, e] = base.split(":");
          const ss = slideSents(+n);
          if (!ss.length) err(`slide ${n} has no narration in this part ${label}`);
          else t = e ? ss[ss.length - 1].end : ss[0].start;
        }
        t += shift;
      } else t = resolveObj(ref, label);
      anchorCache.set(key, t);
      return t;
    }
    function resolveObj(o, label) {
      const hit = findWords(o, label);
      if (!hit) { const ss = o.slide != null ? slideSents(o.slide) : []; return (ss[0] ? ss[0].start : 0) + (o.shift || 0); }
      return (o.edge === "end" ? hit.last.e : hit.first.t) + (o.shift || 0);
    }

    /* ---------------- graph ---------------- */
    const NODES = sb.graph.nodes.slice();
    const EDGES = sb.graph.edges.map((e) => (Array.isArray(e) ? e : [e.u, e.v, e.w]));
    const K = sb.graph.groups || 2;
    const CAP = sb.graph.cap != null ? sb.graph.cap : Math.ceil(NODES.length / K);
    const names = (g) => (g.includes(",") ? g.split(",").map((x) => x.trim()) : g.trim().split(""));
    function parseSplit(v) {
      if (v == null || v === "none" || v === "") return null;
      const s = sb.splits && sb.splits[v] != null ? sb.splits[v] : v;
      const asn = Object.fromEntries(NODES.map((n) => [n, null]));
      s.split("|").forEach((g, gi) => names(g).filter(Boolean).forEach((n) => {
        if (!(n in asn)) err(`split "${s}": unknown node ${n}`); else asn[n] = gi;
      }));
      return asn;
    }
    /** Colour rank of each group: the group holding the first node name is 0 (blue), and so on. */
    function colourOf(asn) {
      const firsts = new Map();
      for (const n of [...NODES].sort()) if (asn[n] != null && !firsts.has(asn[n])) firsts.set(asn[n], firsts.size);
      return firsts;
    }
    function cutOf(asn) {
      if (!asn) return null;
      let c = 0;
      for (const [u, v, w] of EDGES) if (asn[u] != null && asn[v] != null && asn[u] !== asn[v]) c += w;
      return c;
    }
    function sizes(asn) {
      const out = Array(K).fill(0); if (!asn) return out;
      const col = colourOf(asn);
      for (const n of NODES) if (asn[n] != null) { const c = col.get(asn[n]); if (c < K) out[c]++; }
      return out;
    }
    function legal(asn) {
      if (!asn || NODES.some((n) => asn[n] == null)) return false;
      const s = sizes(asn);
      return s.every((x) => x > 0 && x <= CAP);
    }
    function partsStr(asn) {
      const col = colourOf(asn), groups = [];
      for (const n of [...NODES].sort()) if (asn[n] != null) { const c = col.get(asn[n]); (groups[c] = groups[c] || []).push(n); }
      return groups.map((g) => g.join("")).join(" | ");
    }
    /* The course's random dealer (Lab 03): mulberry32, two warm-up draws, Fisher–Yates over sorted names. */
    function mulberry32(seed) {
      let t = seed >>> 0;
      return function next() {
        t += 0x6d2b79f5;
        let r = Math.imul(t ^ (t >>> 15), 1 | t);
        r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
        return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
      };
    }
    function randomSplit(seed) {
      const order = [...NODES].sort();
      const rng = mulberry32(seed); rng(); rng();
      for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
      const left = new Set(order.slice(0, Math.floor(order.length / 2)));
      return Object.fromEntries(NODES.map((n) => [n, left.has(n) ? 0 : 1]));
    }

    /* claims: every number the narration or the text states, checked against the rules above */
    const claims = [];
    for (const c of sb.claims || []) {
      const asn = c.deal != null ? randomSplit(c.deal) : parseSplit(c.split);
      const got = { split: asn ? partsStr(asn) : null, cut: cutOf(asn), legal: legal(asn) };
      const want = parseSplit(c.split);
      const okSplit = c.split == null || (c.deal == null) || (want && partsStr(want) === got.split);
      const okCut = c.cut == null || c.cut === got.cut;
      const okLegal = c.legal == null || c.legal === got.legal;
      const ok = okSplit && okCut && okLegal;
      claims.push({ claim: c, got, ok });
      if (!ok) err(`claim failed: ${JSON.stringify(c)} -> ${JSON.stringify(got)}`);
    }

    /* ---------------- tracks ---------------- */
    const POSES = sb.poses;
    for (const [pn, p] of Object.entries(POSES)) for (const n of NODES) if (!p[n]) err(`pose ${pn} has no position for ${n}`);
    const cam = (v) => {
      if (v == null || v === "full") return FULL;
      const c = sb.cameras && sb.cameras[v] != null ? sb.cameras[v] : v;
      if (!Array.isArray(c) || c.length !== 3) { err(`bad camera ${JSON.stringify(v)}`); return FULL; }
      const [cx, cy, w0] = c, w = Math.min(w0, 960), h = (w * 9) / 16;
      return [clamp(cx - w / 2, 0, 960 - w), clamp(cy - h / 2, 0, 540 - h), w, h]; // a shot never shows past the scene
    };
    const init = Object.assign({ pose: Object.keys(POSES)[0], split: null, camera: "full", shape: "node", wires: false, dim: 1 }, sb.initial || {});
    const conv = {
      pose: (v) => { if (!POSES[v]) { err(`unknown pose ${v}`); return POSES[init.pose]; } return POSES[v]; },
      split: (v) => v, camera: cam, shape: (v) => (v === "cell" ? 0 : 1), wires: (v) => (v ? 1 : 0), dim: (v) => +v,
    };
    const tracks = {};
    for (const k of Object.keys(conv)) tracks[k] = [[0, conv[k](init[k]), "initial"]];
    (sb.timeline || []).forEach((item, i) => {
      const t = resolve(item.at, `(timeline #${i})`);
      for (const k of Object.keys(conv)) if (k in item) tracks[k].push([t, conv[k](item[k]), item.at]);
    });
    for (const k of Object.keys(tracks)) tracks[k].sort((a, b) => a[0] - b[0]);

    const memo = new Map();
    function sampler(name, dur, mix) {
      if (memo.has(name)) return memo.get(name);
      const list = tracks[name], startVal = [];
      const valAt = (t) => {
        let i = -1;
        for (let k = 0; k < list.length; k++) { if (list[k][0] <= t) i = k; else break; }
        if (i <= 0) return list[0][1];
        if (startVal[i] === undefined) startVal[i] = valAt(list[i][0] - 1e-6);
        return mix(startVal[i], list[i][1], ease((t - list[i][0]) / (dur * D)));
      };
      memo.set(name, valAt);
      return valAt;
    }
    const mixArr = (a, b, p) => a.map((v, i) => lerp(v, b[i], p));
    const mixPose = (a, b, p) => { const o = {}; for (const n of NODES) o[n] = mixArr(a[n], b[n], p); return o; };
    const posAt = sampler("pose", DUR_POSE, mixPose);
    const camAt = sampler("camera", DUR_CAM, mixArr);
    const shapeAt = sampler("shape", DUR_SHAPE, lerp);
    const wiresAt = sampler("wires", DUR_WIRES, lerp);
    const dimAt = sampler("dim", DUR_DIM, lerp);
    function splitSeg(t) {
      const list = tracks.split; let i = 0;
      for (let k = 0; k < list.length; k++) if (list[k][0] <= t) i = k;
      return { cur: list[i][1], prev: i > 0 ? list[i - 1][1] : list[i][1], t0: list[i][0] };
    }
    function shownCut(t) {
      const s = splitSeg(t), c1 = cutOf(parseSplit(s.cur)), c0 = cutOf(parseSplit(s.prev));
      if (c1 == null) return null;
      if (c0 == null) return c1;
      return Math.round(lerp(c0, c1, ease((t - s.t0) / (DUR_COUNT * D))));
    }

    /* ---------------- show windows ---------------- */
    const WIN = {};
    (sb.show || []).forEach((w, i) => {
      const a = resolve(w.from, `(show ${w.show} #${i})`), b = w.to == null ? 1e9 : resolve(w.to, `(show ${w.show} #${i})`);
      if (b <= a) err(`show ${w.show} #${i}: ends (${b.toFixed(2)}s) before it starts (${a.toFixed(2)}s)`);
      (WIN[w.show] = WIN[w.show] || []).push({ a, b, edges: (w.edges || []).map((e) => e.replace(/\s/g, "")), stagger: w.stagger || 0 });
    });
    const win = (name, t) => (WIN[name] || []).find((w) => t >= w.a && t < w.b);
    const edgeIn = (w, u, v) => w && (w.edges.length === 0 || w.edges.includes(`${u}-${v}`) || w.edges.includes(`${v}-${u}`));
    /** Edge styles (heavy, pulse, flash): several windows can be open at once, each for its own edges. */
    const edgeOn = (name, t, u, v) => (WIN[name] || []).some((w) => t >= w.a && t < w.b && edgeIn(w, u, v));

    /* ---------------- DOM ---------------- */
    const root = document.getElementById(cfg.rootId || "lesson-root");
    const qa = sb.question;
    root.innerHTML = `
<div class="wrap">
  <header>
    <div class="eyebrow">${esc(L(sb.eyebrow))}</div>
    <h1>${esc(L(sb.title))}</h1>
    ${sb.lede ? `<p class="lede">${L(sb.lede)}</p>` : ""}
  </header>
  <section class="player" aria-label="${esc(T.lesson)}">
    <div class="stage">
      <svg class="scene" viewBox="0 0 960 540" role="img" aria-label="${esc(T.graph)}"></svg>
      <div class="layer"></div>
      <div class="banner"><b>${esc(T.yourSplit)}</b><button class="btn" type="button" data-act="back">${esc(T.back)}</button></div>
    </div>
    <div class="captions" aria-live="off"></div>
    <div class="transport">
      <button class="play" type="button" aria-label="${esc(T.play)}">▶</button>
      <div class="scrub"><input type="range" min="0" max="${DUR}" step="0.01" value="0" aria-label="${esc(T.position)}"><div class="time">0:00 / ${fmt(DUR)}</div></div>
      <div class="opts"><div class="seg" role="group" aria-label="${esc(T.speed)}"></div><button class="tbtn" type="button" aria-pressed="true">${esc(T.captions)}</button></div>
    </div>
  </section>
  <div class="cols">
    <section aria-label="${esc(T.chapters)}"><h2>${esc(T.chapters)}</h2><ul class="chapters"></ul></section>
    <section class="bench" aria-label="${esc(T.turn)}">
      <h2>${esc(T.turn)}</h2>
      ${qa ? `<p>${md(L(qa.text))}</p><div class="row bench-opts"></div><p class="feedback"></p>` : ""}
      ${sb.bench && sb.bench.deal ? `<div class="row"><label for="lesson-seed">${esc(T.deal)}</label><input class="seedbox" id="lesson-seed" type="number" min="0" max="999" value="${sb.bench.seed != null ? sb.bench.seed : 3}"><button class="btn primary" type="button" data-act="deal">${esc(T.dealBtn)}</button></div>` : ""}
      <p>${esc(T.clickHint)}</p>
      <div class="readout">${esc(sb.bench && sb.bench.deal ? T.noSplit : T.noSplitNoDeal)}</div>
    </section>
  </div>
  ${sb.note ? `<p class="note">${L(sb.note)}</p>` : ""}
</div>`;
    const $ = (sel) => root.querySelector(sel);
    const stage = $(".stage"), svg = $("svg.scene"), layer = $(".layer");
    const NS = "http://www.w3.org/2000/svg";
    const mk = (tag, attrs = {}, parent = svg) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; };

    const divX = (sb.divider && sb.divider.x) || 570;
    const halves = mk("g");
    mk("rect", { class: "tint0", x: 0, y: 0, width: divX, height: 540 }, halves);
    mk("rect", { class: "tint1", x: divX, y: 0, width: 960 - divX, height: 540 }, halves);
    const divider = mk("line", { class: "divider", x1: divX, y1: 110, x2: divX, y2: 525 });
    const chipBox = sb.chip || { x: 175, y: 120, w: 610, h: 395 };
    const chip = mk("g");
    mk("rect", { class: "chipbody", x: chipBox.x, y: chipBox.y, width: chipBox.w, height: chipBox.h, rx: 18 }, chip);
    const pins = Math.max(4, Math.floor((chipBox.w - 40) / 48));
    for (let i = 0; i < pins; i++) {
      mk("rect", { class: "pin", x: chipBox.x + 30 + i * 48, y: chipBox.y - 14, width: 14, height: 14, rx: 2 }, chip);
      mk("rect", { class: "pin", x: chipBox.x + 30 + i * 48, y: chipBox.y + chipBox.h, width: 14, height: 14, rx: 2 }, chip);
    }
    const graph = mk("g");
    const edgeEls = EDGES.map(([u, v, w]) => {
      const g = mk("g", { class: "edge" }, graph);
      const wires = Array.from({ length: Math.min(w, 9) }, () => mk("line", { class: "wire" }, g));
      const main = mk("line", { class: "main" }, g);
      const wl = mk("g", { class: "wl" }, g);
      mk("rect", { x: -14, y: -12, width: 28, height: 24, rx: 6 }, wl);
      mk("text", { x: 0, y: 1 }, wl).textContent = String(w);
      return { u, v, w, g, wires, main, wl };
    });
    const nodeEls = NODES.map((n) => {
      const g = mk("g", { class: "node nu", tabindex: 0, role: "button", "aria-label": fill(T.cell, { n }) }, graph);
      const r = mk("rect", {}, g);
      const t = mk("text", { x: 0, y: 1 }, g); t.textContent = n;
      g.addEventListener("click", () => clickNode(n));
      g.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); clickNode(n); } });
      return { n, g, r, t };
    });

    /* text markup: {piece@ref} appears at its own time, **x** accent, !!x!! red, ##x## number */
    function md(s) {
      let h = esc(s);
      h = h.replace(/\{([^{}@]+)@([^{}]+)\}/g, (m, piece, ref) => {
        ref = ref.trim();
        if (!/^(slide:|start|end|@)/.test(ref)) ref = "@" + ref; // {piece@name} means the anchor @name
        return `<span data-a="${resolve(ref, `(text "${piece}")`).toFixed(3)}">${piece}</span>`;
      });
      h = h.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/!!(.+?)!!/g, '<span class="red">$1</span>').replace(/##(.+?)##/g, '<span class="num">$1</span>');
      return h;
    }
    function thumb(item) {
      const asn = parseSplit(item.split), P = POSES[item.pose || sb.thumbPose || Object.keys(POSES)[0]], col = colourOf(asn);
      const xs = NODES.map((n) => P[n][0]), ys = NODES.map((n) => P[n][1]);
      const x0 = Math.min(...xs) - 60, y0 = Math.min(...ys) - 50, w = Math.max(...xs) - x0 + 60, h = Math.max(...ys) - y0 + 50;
      let s = `<svg viewBox="${x0} ${y0} ${w} ${h}" aria-hidden="true">`;
      for (const [u, v] of EDGES) {
        const c = asn[u] !== asn[v];
        s += `<line x1="${P[u][0]}" y1="${P[u][1]}" x2="${P[v][0]}" y2="${P[v][1]}" stroke="${c ? "var(--cut)" : "var(--edge)"}" stroke-width="${c ? 7 : 5}" ${c ? 'stroke-dasharray="14 9"' : ""}/>`;
      }
      for (const n of NODES) s += `<circle cx="${P[n][0]}" cy="${P[n][1]}" r="30" fill="var(--g${col.get(asn[n]) || 0})"/><text x="${P[n][0]}" y="${P[n][1] + 1}" fill="#fff" font-size="30" font-weight="700" text-anchor="middle" dominant-baseline="central" font-family="Source Sans 3, sans-serif">${esc(n)}</text>`;
      s += "</svg>";
      const best = item.best ? `<span class="ok" data-a="${resolve(item.best, "(thumb best)").toFixed(3)}">${esc(L(item.bestLabel) || "best")}</span>` : "";
      return `<div class="thumb${item.best ? " best" : ""}">${s}<span class="c">${esc(partsStr(asn))} · ${esc(T.cut)} ${cutOf(asn)}</span>${best}</div>`;
    }
    const BUILD = {
      headline: (o) => `<div class="hl"${o.size ? ` style="font-size:${+o.size}cqw"` : ""}>${md(L(o.text))}</div>${o.sub ? `<div class="sub">${md(L(o.sub))}</div>` : ""}`,
      term: (o) => `<div class="term"><span class="t">${md(L(o.text))}</span><span class="d">${md(L(o.sub))}</span></div>`,
      chip: (o) => `<span class="chip">${md(L(o.text))}</span>`,
      tag: (o) => `<div class="tag">${md(L(o.text))}</div>`,
      tags: (o) => `<div class="tags">${o.items.map((it) => `<div class="tag"${it.at ? ` data-a="${resolve(it.at, "(tags)").toFixed(3)}"` : ""}>${md(L(it.text))}</div>`).join("")}</div>`,
      label: (o) => `<span class="label c${o.color || 0}">${md(L(o.text))}</span>`,
      vocab: (o) => `<div class="vocab">${o.items.map((it) => `<div${it.at ? ` data-a="${resolve(it.at, "(vocab)").toFixed(3)}"` : ""}><b>${esc(L(it.k))}</b>${md(L(it.text))}</div>`).join("")}</div>`,
      eq: (o) => `<div class="eq">${md(L(o.text))}</div>`,
      stamp: (o) => `<div class="stamp">${md(L(o.text))}</div>`,
      bigq: (o) => `<div class="bigq"><div class="q">?</div><div class="hl">${md(L(o.text))}</div></div>`,
      compare: (o) => `<div class="cmp">${o.rows.map((r) => `<div class="row ${r.tone || ""}"><span>${md(L(r.label))}</span><span class="k">${md(L(r.value))}</span><span>${md(L(r.note))}</span></div>`).join("")}</div>`,
      thumbs: (o) => `<div class="thumbs">${o.items.map(thumb).join("")}</div>`,
      question: () => `<div class="qcard"><span class="e">${esc(T.turn)}</span><span class="q">${md(L(qa && qa.text))}</span><span class="h qh">${esc(L(qa && qa.hint) || T.think)}</span><span class="qbtns">${(qa ? qa.options : []).map((op, i) => `<button class="btn" type="button" data-q="${i}">${esc(L(op.label))}</button>`).join("")}</span><span class="h qans"></span></div>`,
      html: (o) => L(o.html),
    };
    const OV = (sb.overlays || []).map((o, i) => {
      const lab = `(overlay #${i} ${o.type})`;
      const a = resolve(o.from, lab), b = o.to == null ? 1e9 : resolve(o.to, lab);
      if (b <= a) err(`overlay #${i} (${o.type}) ends (${b.toFixed(2)}s) before it starts (${a.toFixed(2)}s)`);
      const d = document.createElement("div");
      d.className = "ov ov-" + o.type; d.style.left = (o.x || 0) + "%"; d.style.top = (o.y || 0) + "%";
      if (o.width) d.style.width = o.width + "cqw";
      if (!BUILD[o.type]) err(`overlay #${i}: unknown type ${o.type}`);
      d.innerHTML = BUILD[o.type] ? BUILD[o.type](o) : "";
      layer.appendChild(d);
      const label = (d.textContent || "").trim().replace(/\s+/g, " ").slice(0, 48);
      return { a, b, d, label, type: o.type, parts: [...d.querySelectorAll("[data-a]")].map((e) => ({ e, t: +e.dataset.a })) };
    });
    const widget = (cls, pos, html) => {
      const d = document.createElement("div"); d.className = "ov " + cls; d.style.left = pos.x + "%"; d.style.top = pos.y + "%";
      d.innerHTML = html; layer.appendChild(d); return d;
    };
    const W = sb.widgets || {};
    const counter = widget("ov-counter", W.counter || { x: 81, y: 68 }, `<div class="counter"><span class="l">${esc(T.cutsize)}</span><span class="v">0</span></div>`);
    const cv = counter.querySelector(".v"), cbox = counter.querySelector(".counter");
    const balance = widget("ov-balance", W.balance || { x: 77, y: 26 }, `<div class="balance"><span class="l">${esc(T.perSide)}</span><div class="bars">${Array.from({ length: K }, (_, i) => `<div class="bar c${i}"></div>`).join("")}<div class="cap"><span>${esc(fill(T.max, { cap: CAP }))}</span></div></div><span class="verdict"></span></div>`);
    const bars = balance.querySelectorAll(".bar"), capLine = balance.querySelector(".cap"), verdict = balance.querySelector(".verdict");
    capLine.style.bottom = (CAP / NODES.length) * 100 + "%";

    /* ---------------- render ---------------- */
    let free = null, lastP = null, lastCam = FULL;
    const setOp = (el, v) => { el.style.opacity = v; };
    const fadeIn = reduce ? 0.01 : 0.35, fadeOut = reduce ? 0.01 : 0.25;
    function ovStyle(el, t, a, b) {
      const on = t >= a && t < b, o = on ? Math.min(clamp((t - a) / fadeIn), clamp((b - t) / fadeOut)) : 0;
      el.style.opacity = o;
      el.style.transform = on && !reduce ? `translateY(${((1 - ease((t - a) / 0.5)) * 0.8).toFixed(3)}cqw)` : "none";
      return on;
    }
    function render(t) {
      const F = free;
      const asn = F ? F.asn : parseSplit(splitSeg(t).cur);
      const P = F ? POSES[sb.freePose || Object.keys(POSES)[0]] : posAt(t);
      const shape = F ? 1 : shapeAt(t), spread = F ? 0 : wiresAt(t);
      const C = F ? FULL : camAt(t);
      lastP = P; lastCam = C;
      svg.setAttribute("viewBox", C.map((v) => v.toFixed(1)).join(" "));
      const chipOn = !F && !!win("chip", t), cellMode = chipOn && shape < 0.5;
      setOp(chip, chipOn ? 1 : 0);
      const div = !F && !!win("divider", t);
      setOp(divider, div ? 0.55 : 0); setOp(halves, div ? 1 : 0);
      setOp(graph, F ? 1 : dimAt(t));
      const showCut = F || !!win("cut", t), weights = F || !!win("weights", t);
      const col = asn ? colourOf(asn) : null;

      for (const e of edgeEls) {
        const [x1, y1] = P[e.u], [x2, y2] = P[e.v];
        const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len;
        e.wires.forEach((ln, i) => {
          const o = (i - (e.wires.length - 1) / 2) * 9 * spread;
          ln.setAttribute("x1", x1 + nx * o); ln.setAttribute("y1", y1 + ny * o);
          ln.setAttribute("x2", x2 + nx * o); ln.setAttribute("y2", y2 + ny * o);
          ln.style.opacity = clamp(spread * 1.6);
        });
        e.main.setAttribute("x1", x1); e.main.setAttribute("y1", y1); e.main.setAttribute("x2", x2); e.main.setAttribute("y2", y2);
        e.main.style.opacity = clamp(1 - spread * 1.4);
        const isCut = showCut && asn && asn[e.u] != null && asn[e.v] != null && asn[e.u] !== asn[e.v];
        const isHeavy = !F && edgeOn("heavy", t, e.u, e.v);
        e.main.setAttribute("stroke-width", isHeavy ? 9 : 2.5 + Math.min(e.w, 8) * 0.9);
        e.g.classList.toggle("cut", !!isCut);
        e.g.classList.toggle("heavy", isHeavy);
        e.g.classList.toggle("pulse", !F && edgeOn("pulse", t, e.u, e.v));
        e.g.classList.toggle("flash", !F && edgeOn("flash", t, e.u, e.v));
        const mx = (x1 + x2) / 2 + nx * 18, my = (y1 + y2) / 2 + ny * 18;
        e.wl.setAttribute("transform", `translate(${mx.toFixed(1)} ${my.toFixed(1)})`);
        setOp(e.wl, weights ? 1 : 0);
      }
      const labW = WIN.labels;
      nodeEls.forEach((N, i) => {
        const [x, y] = P[N.n];
        N.g.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
        const R = 25, w = lerp(68, 2 * R, shape), h = lerp(46, 2 * R, shape), rx = lerp(7, R, shape);
        N.r.setAttribute("x", -w / 2); N.r.setAttribute("y", -h / 2); N.r.setAttribute("width", w); N.r.setAttribute("height", h); N.r.setAttribute("rx", rx);
        const side = !asn || asn[N.n] == null ? "nu" : "g" + Math.min(col.get(asn[N.n]), 3);
        N.g.setAttribute("class", "node " + (cellMode ? "ncell" : side));
        let lab = true;
        if (!F && labW) { const w0 = labW.find((w) => t >= w.a && t < w.b); lab = !!w0 && t >= w0.a + w0.stagger * i; }
        N.t.style.opacity = lab ? 1 : 0;
      });

      for (const o of OV) {
        const on = !F && ovStyle(o.d, t, o.a, o.b);
        if (F) { o.d.style.opacity = 0; }
        for (const p of o.parts) {
          const po = on && t >= p.t ? clamp((t - p.t) / (reduce ? 0.01 : 0.3)) : 0;
          p.e.style.opacity = po;
          p.e.style.transform = po > 0 && po < 1 && !reduce ? `translateY(${((1 - po) * 0.6).toFixed(3)}cqw)` : "none";
        }
      }
      const cw = win("counter", t);
      const showCounter = F ? !!asn && NODES.some((n) => asn[n] != null) : !!cw;
      if (F) counter.style.opacity = showCounter ? 1 : 0; else if (cw) ovStyle(counter, t, cw.a, cw.b); else counter.style.opacity = 0;
      if (showCounter) {
        const c = F ? cutOf(asn) : shownCut(t);
        cv.textContent = c == null ? "–" : c;
        cbox.classList.toggle("bad", c != null && sb.badCut != null && c >= sb.badCut);
        cbox.classList.toggle("good", c != null && sb.goodCut != null && c === sb.goodCut && legal(asn));
      }
      const bw = win("balance", t);
      const showBal = F ? !!asn : !!bw;
      if (F) balance.style.opacity = showBal ? 1 : 0; else if (bw) ovStyle(balance, t, bw.a, bw.b); else balance.style.opacity = 0;
      if (showBal) {
        const s = sizes(asn);
        bars.forEach((b, i) => { b.style.height = (s[i] / NODES.length) * 100 + "%"; b.textContent = s[i] || ""; });
        const capOn = F || !!win("cap", t);
        capLine.style.opacity = capOn ? 1 : 0;
        const ok = legal(asn);
        verdict.textContent = capOn ? (ok ? T.verdictYes : T.verdictNo) : "";
        verdict.className = "verdict " + (ok ? "yes" : "no");
      }
      renderCaptions(t);
      renderTransport(t);
    }

    /* ---------------- captions ---------------- */
    const capEl = $(".captions");
    let capIdx = -2;
    function renderCaptions(t) {
      if (free) { if (capIdx !== -3) { capEl.textContent = T.paused; capIdx = -3; } return; }
      let i = -1;
      for (let k = 0; k < SENT.length; k++) if (SENT[k].start <= t) i = k;
      if (i < 0) i = 0;
      if (i !== capIdx) {
        capEl.innerHTML = "";
        SENT[i].words.forEach((w) => { const s = document.createElement("span"); s.textContent = w.w + " "; capEl.appendChild(s); });
        capIdx = i;
      }
      [...capEl.children].forEach((s, k) => s.classList.toggle("said", t >= SENT[i].words[k].t));
    }

    /* ---------------- transport ---------------- */
    const au = document.getElementById(cfg.audioId || "lesson-audio");
    const playBtn = $(".play"), scrub = $(".scrub input"), timeEl = $(".time");
    const CHAP = (sb.chapters || []).map((c, i) => ({ t0: resolve(c.at, `(chapter #${i})`), title: L(c.title) }));
    const chapBtns = CHAP.map((c) => {
      const li = document.createElement("li"), b = document.createElement("button");
      b.type = "button"; b.innerHTML = `<span class="ts">${fmt(c.t0)}</span><span>${esc(c.title)}</span>`;
      b.addEventListener("click", () => { seek(c.t0 + 0.01); play(); });
      li.appendChild(b); $(".chapters").appendChild(li); return { t0: c.t0, b };
    });
    function renderTransport(t) {
      if (document.activeElement !== scrub) scrub.value = t;
      timeEl.textContent = `${fmt(t)} / ${fmt(DUR)}`;
      let cur = 0; chapBtns.forEach((c, i) => { if (t >= c.t0) cur = i; });
      chapBtns.forEach((c, i) => c.b.setAttribute("aria-current", String(i === cur && !free)));
    }
    const QT = qa ? resolve(qa.at || "end", "(question)") : null;
    let asked = false, raf = 0;
    function loop() {
      if (QT != null && !asked && !au.paused && au.currentTime >= QT) { asked = true; au.pause(); au.currentTime = QT; stage.classList.add("asking"); }
      render(au.currentTime);
      if (!au.paused) raf = requestAnimationFrame(loop);
    }
    function resetAsk(t) { if (QT != null && t < QT - 0.05) { asked = false; stage.classList.remove("asking"); const a = layer.querySelector(".qans"); if (a) a.textContent = ""; } }
    function play() {
      if (free) leaveFree();
      if (au.ended || au.currentTime >= DUR - 0.05) { au.currentTime = 0; resetAsk(0); }
      const p = au.play(); if (p && p.catch) p.catch(() => {});
    }
    function seek(t) { if (free) leaveFree(); au.currentTime = clamp(t, 0, DUR); resetAsk(au.currentTime); render(au.currentTime); }
    playBtn.addEventListener("click", () => (au.paused ? play() : au.pause()));
    au.addEventListener("play", () => { playBtn.textContent = "❚❚"; playBtn.setAttribute("aria-label", T.pause); cancelAnimationFrame(raf); loop(); });
    au.addEventListener("pause", () => { playBtn.textContent = "▶"; playBtn.setAttribute("aria-label", T.play); render(au.currentTime); });
    au.addEventListener("seeked", () => render(au.currentTime));
    au.addEventListener("ended", () => { const b = $(".bench"); b.classList.remove("pulse"); void b.offsetWidth; b.classList.add("pulse"); });
    scrub.addEventListener("input", () => { if (free) leaveFree(); au.currentTime = +scrub.value; resetAsk(+scrub.value); render(+scrub.value); });
    document.addEventListener("keydown", (e) => {
      const a = document.activeElement;
      if (e.code === "Space" && !/INPUT|BUTTON|TEXTAREA|SELECT/.test(a.tagName) && !(a.closest && a.closest(".node"))) { e.preventDefault(); au.paused ? play() : au.pause(); }
    });
    const SPEEDS = [1, 1.25, 1.5, 1.75, 2], KEY = cfg.storageKey || "lesson-speed";
    let rate = 1;
    try { const r = parseFloat(localStorage.getItem(KEY)); if (SPEEDS.includes(r)) rate = r; } catch (e) { /* storage blocked */ }
    const speedBtns = SPEEDS.map((r) => {
      const b = document.createElement("button"); b.type = "button"; b.textContent = r + "×";
      b.addEventListener("click", () => setRate(r)); $(".seg").appendChild(b); return { r, b };
    });
    function setRate(r) {
      rate = r; au.playbackRate = r; au.preservesPitch = true;
      speedBtns.forEach((x) => x.b.setAttribute("aria-pressed", String(x.r === r)));
      try { localStorage.setItem(KEY, String(r)); } catch (e) { /* storage blocked */ }
    }
    setRate(rate);
    au.addEventListener("loadedmetadata", () => setRate(rate));
    const ccBtn = $(".tbtn"), playerEl = $(".player");
    ccBtn.addEventListener("click", () => { const on = ccBtn.getAttribute("aria-pressed") !== "true"; ccBtn.setAttribute("aria-pressed", String(on)); playerEl.classList.toggle("nocc", !on); });

    /* ---------------- your turn ---------------- */
    const readout = $(".readout");
    function describe(asn, prefix) {
      const placed = NODES.filter((n) => asn[n] != null), all = placed.length === NODES.length;
      const s = sizes(asn);
      return `${esc(prefix)}${esc(partsStr(asn))} &nbsp; ${esc(T.cut)} ${cutOf(asn)} &nbsp; ${esc(T.sides)} ${s.join(" | ")} &nbsp; ` +
        (all ? (legal(asn) ? `<span class="ok">${esc(T.legal)}</span>` : `<span class="no">${esc(fill(T.notLegal, { cap: CAP }))}</span>`)
          : esc(fill(T.toPlace, { list: NODES.filter((n) => asn[n] == null).join(", ") })));
    }
    function enterFree(asn) { au.pause(); free = { asn: Object.assign({}, asn) }; stage.classList.add("free"); render(au.currentTime); }
    function leaveFree() { free = null; stage.classList.remove("free"); readout.textContent = T.backMsg; }
    function clickNode(n) {
      if (!free) enterFree(parseSplit(splitSeg(au.currentTime).cur) || Object.fromEntries(NODES.map((k) => [k, null])));
      const a = free.asn;
      a[n] = a[n] == null ? 0 : (a[n] + 1) % K;
      readout.innerHTML = describe(a, T.yours);
      render(au.currentTime);
    }
    root.querySelector('[data-act="back"]').addEventListener("click", () => { leaveFree(); render(au.currentTime); });
    const dealBtn = root.querySelector('[data-act="deal"]');
    if (dealBtn) dealBtn.addEventListener("click", () => {
      const inp = root.querySelector("#lesson-seed");
      const s = Math.max(0, Math.min(999, parseInt(inp.value, 10) || 0)); inp.value = s;
      const asn = randomSplit(s); enterFree(asn); readout.innerHTML = describe(asn, fill(T.seed, { s }));
    });
    if (qa) {
      const fb = $(".feedback"), opts = $(".bench-opts");
      qa.options.forEach((op) => {
        const b = document.createElement("button"); b.type = "button"; b.className = "btn"; b.textContent = L(op.label);
        b.addEventListener("click", () => { fb.innerHTML = md(L(op.reply)); }); opts.appendChild(b);
      });
      layer.querySelectorAll(".qbtns button").forEach((b) => b.addEventListener("click", () => {
        const op = qa.options[+b.dataset.q];
        layer.querySelector(".qans").innerHTML = md(L(op.reply));
        stage.classList.remove("asking");
        const p = au.play(); if (p && p.catch) p.catch(() => {});
      }));
    }

    /* ---------------- diagnostics for scripts/check_lesson.py ---------------- */
    function stageRect(el) {
      const s = stage.getBoundingClientRect(), r = el.getBoundingClientRect();
      return { x: r.left - s.left, y: r.top - s.top, w: r.width, h: r.height };
    }
    window.__lesson = {
      render, duration: DUR, errors, claims, lang,
      tracks: Object.fromEntries(Object.entries(tracks).map(([k, v]) => [k, v.map((x) => [x[0], typeof x[2] === "string" ? x[2] : JSON.stringify(x[2])])])),
      moveSeconds: { pose: DUR_POSE, camera: DUR_CAM, shape: DUR_SHAPE, wires: DUR_WIRES, dim: DUR_DIM, split: DUR_COUNT },
      overlays: OV.map((o) => ({ a: o.a, b: o.b, label: o.label, type: o.type })),
      sentences: SENT.map((s) => ({ slide: s.slide, start: s.start, end: s.end, text: s.text })),
      question: QT,
      boxes() {
        const s = stage.getBoundingClientRect(), out = [];
        const sx = s.width / lastCam[2], sy = s.height / lastCam[3];
        nodeEls.forEach((N) => {
          if (+(graph.style.opacity || 1) < 0.6) return; // a dimmed graph sits behind the text on purpose
          const [x, y] = lastP[N.n], cx = (x - lastCam[0]) * sx, cy = (y - lastCam[1]) * sy, r = 26 * sx;
          if (cx + r < 0 || cy + r < 0 || cx - r > s.width || cy - r > s.height) return;
          out.push({ kind: "node", label: N.n, x: cx - r, y: cy - r, w: 2 * r, h: 2 * r });
        });
        [...OV.map((o) => ({ d: o.d, label: o.label })), { d: counter, label: "counter" }, { d: balance, label: "balance" }].forEach((o) => {
          // fully shown text only, not mid-fade
          if (+o.d.style.opacity > 0.9) { const r = stageRect(o.d.firstElementChild || o.d); out.push({ kind: "overlay", label: o.label, x: r.x, y: r.y, w: r.w, h: r.h }); }
        });
        return { stage: { w: s.width, h: s.height }, boxes: out };
      },
      setRecording(on) { root.classList.toggle("norec", !!on); },
    };
    if (errors.length) console.error(`[lesson] ${errors.length} problem(s); see window.__lesson.errors`);
    render(0);
  }

  window.LessonEngine = { mount };
})();
