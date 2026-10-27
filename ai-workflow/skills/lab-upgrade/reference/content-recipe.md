# Content recipe — what "upgraded" means

The teacher leaves each lab deliberately thin. Typical signs (the audit script flags them):
generic starter prompts ("Change one knob and report what moved"), a "Stretch" with no task,
quiz items that test nothing ("This module's primary algorithm is… / Gate-level SDF
annotation"), one example graph, browser challenges that only check one final state, and a
five-frame walkthrough with one sentence of narration per frame.

The upgrade has five parts. For each, the clustering Lab 02 (affinity metrics) version is given
as the model to copy.

## §1 Concepts first (decide before writing anything)

Pick 2–4 ideas the lab must make a learner *able to do*, each one shown by a tiny example where
the idea **changes an answer**. Lab 02 had three:

| Idea | Example that proves it matters |
|---|---|
| Edge weight is the simplest score | tiny graph: A–B and D–E tie at 5; the tie-break picks A–B |
| Shared neighbours change the ranking | priority graph: edge score picks X–Y (5); shared picks the triangle P–Q (8) |
| Wide nets must count less (pin-count) | netlist: raw count A–B 2 > E–F 1; pin-count A–B 0.5 < E–F 1 |

For **cutsize and balance** (partitioning Lab 02), possible ideas to check against the course:
cutsize alone prefers putting everything on one side (cut 0, useless); balance needs node
sizes, not node counts; weighted cut versus counted cut; the hyperedge cut (a net is cut once,
however many pins are on the other side); a balance tolerance turns "the best cut" into "the
best legal cut". Verify each against `common/` and the course docs before using it.

For **initial bipartition** (partitioning Lab 03, current target), ideas to check:
KL and FM (Labs 04–05) only *improve* a split, so they need a legal starting one; **random**
(shuffle and deal half, like dealing cards) is fast but luck-dependent, and different seeds give
very different cuts (tiny graph: ABC|DE cut 3 versus AE|BCD cut 12); **greedy** keeps the heaviest
edges inside one side (AB|CDE cut 5); **grow** floods outward from a seed node until one side is
half full (grow from D gives ABC|DE cut 3, grow from A gives cut 5), so the seed node matters;
**try several starts and keep the best legal one**. Do not teach KL or FM themselves (Labs 04–05).
Teacher example: `tiny_graph.json` — A–B 5, A–C 1, B–C 4, C–D 2, D–E 5, C–E 1, all sizes 1.

## §2 Golden self-check script — `examples/<topic>_check.py`

- Imports the course `common/` helpers when they exist; adds a reference function for each new
  idea (docstring with the formula and a one-line "why").
- Holds the golden tables as data and prints `PASS`/`FAIL` per table.
- `--show` prints every result; `--impl my_file.py` imports the learner's functions and checks
  them, reporting `SKIP` for functions not written yet.
- Feeds inputs in a **shuffled or reversed order** in at least one check, to catch
  tie-break or ordering bugs.
- Documents the sort/tie-break rule in the docstring (Lab 02: score descending, then u, then v).
- Standard library only; runs with `python3` from the module folder.
- **Seeded randomness:** Python's `random` and JavaScript's `Math.random` never agree. If a
  golden depends on a seed, write one tiny PRNG (e.g. mulberry32 or an LCG plus Fisher–Yates
  shuffle) identically in the checker and in `<tool>-lab-model.js`, and add a golden table that
  lists the split for each seed so both sides can be compared. Keep the teacher's seed numbers
  only if your PRNG reproduces their splits; otherwise say so in the notes and pick new seeds.
- **Exact rules:** write down every rule the teacher left vague (Lab 03 greedy: which edge first,
  how ties break, what to do when a side is full) in the docstring and in EXAMPLES.md.

## §3 EXAMPLES.md, quiz, checklist, README

- EXAMPLES.md sections: Goal · API (with tie-break) · Definitions · Pseudocode (one block per
  idea) · Golden tables (pasted from `--show`, with a "Why" column) · Try-these (python3
  commands) · Starter prompts that ask *why* (e.g. "Explain in one sentence why A–C climbs").
- quiz.json: 6–8 items in the same JSON shape as the teacher's. Each item tests one idea with
  numbers from the examples; `explain` gives the computation. Keep `passing_score`.
- CHECKLIST.md: one box per idea per track, plus the checker command.
- README.md: outcomes, steps, file tree (including new figures and examples).
- `assets/_demo.sh`: runs the checker (keep the teacher's `ROOT` pattern).

## §4 Beginner script in parts (the deck and video)

Audience: a high-school student who has never seen a chip. **1,100–1,300 spoken words (7–8 minutes) in 4–6 parts
of 1–2 minutes**, 26–30 slides. The site cuts the video into those parts (speed buttons, next part plays by itself),
and each part can become an animated lesson. Lab 03's parts, reusable for most labs:

| Part | Content | Opens with (hook) | Ends with ("Pause and guess") |
|---|---|---|---|
| 1 What and why | chip to graph, the two numbers, why this step exists | a surprising contrast ("same graph: cut 3 or cut 16") | a question Part 2 answers |
| 2 The method(s) | the teacher's walkthrough frames (`<!-- algorithm-walkthrough -->`, 5 slides) | the answer to Part 1's question | "was that luck?" |
| 3 Why it is not enough | a worked example computed step by step, the fix | the answer | a deeper question |
| 4 Traps | one slide per extra example graph (ties, limits, misleading heaviest edge) | the answer | a comparison question |
| 5 Your turn | browser lab, Python track, one "Remember" slide (pitfalls + recap merged), next lab | the answer | a teaser for the next lab (checked with the course solver) |

**Repetition rules** (the student's main complaint about the first script): each idea is said where it is taught and
once in the recap, no more. Before writing, list the ideas and the one slide each lives on; after writing, scan the
transcript for repeated phrases (Lab 03: "try several starts, keep the best" in 3 places only, "cut and balance" in 1,
"cuts from 3 to 16" in 2). Merge Pitfalls and Recap into one slide.

**The picture changes every 5–10 s**: split long slides in two and give the second a **step figure** (the full
figure with its later parts hidden, same size, so nothing jumps). The walkthrough block stays exactly 5 frame slides
(the teacher's capture script is fixed at 5).

Writing rules: short sentences (each becomes a bullet, max 90 characters); one idea per sentence; numbers in words
("five", "zero point five"); no slashes; everyday analogies (dealing cards, teams, a drop of ink spreading); capitalise
terms on cards ("Initial bipartition"). After editing, sync `assets/STEPS.md` (CRLF file).

French follows every English change: same slides, same parts, hooks and questions, French figures and frames, then
`make_fr_media.py`. Check both decks have the same page count and both videos decode to the end.

Figures: draw them with the platform's own code so they match the lab look (serve the platform, a scratch page
that imports `assets/clustering-ui.js` `drawGraph`, screenshot with Playwright). Tall (about 900 × 1000), because
non-lab images become two-column slides. Keep the scripts in `../tools/labNN-figures/` with `facts.py` (every number
the figures cite, from the checker), `run_all.sh` and a `--lang fr` option.

## §5 Interactive browser lab

Architecture (Lab 02 `platform/tools/affinity-metrics/`):
- `<tool>-lab-model.js`: graphs, layouts, scoring functions, state, and the challenge checks
  as pure functions. No DOM, so it can be tested in Node.
- `<tool>.js`: canvas picking (click nodes), inputs, buttons, metrics panel; uses only the
  shared helpers (`createChallengeLab`, `drawGraph`, `el`, `metricsBlock`, `fitHiDpiCanvas`,
  `hitNode`) without editing them.
- `index.html`: lead text, local `<style>` only.

Learner actions that challenges can check (Lab 02): pick a pair and **type** its score
(accepts "1/4 + 1/4"); build a ranking one pair at a time (prefix must be right); edit an edge
weight ±1 to make a pair win, with a budget ("total change 1"); switch the example graph.
Study helpers are allowed but marked "(study)": show breakdown, reveal ranking — and a
challenge never passes from a reveal.

Challenge ladder: 3 Intro (read the first idea), 4 Practice (compute, type, rank), 3 Stretch
(change the input so the answer flips — e.g. "make D–E win with one unit of change",
"make X–Y score exactly 9"). For partitioning: build a partition by clicking nodes to the
other side, reach a target cut under a balance limit, find a cut-0 partition and see that it
fails balance, change one node size so the best legal cut moves.
For initial bipartition: grow a side yourself by clicking nodes in BFS order from a chosen
seed (the order is checked), predict the cut of a random seed before revealing it, find a seed
whose random split is worse than greedy, pick the grow seed node that gives the smallest cut.

Draw multi-pin nets as stars with a small hub node and a halo label, so labels don't overlap.
