# Playbook: how Lab 03 (initial bipartition) was upgraded, and how to do the next lab

Course: yongfu-li/eda-learning (VLSI, SJTU). Student: Capeur. Dates: 2026-10-20 → 2026-10-27.
Result: https://capeur.github.io/eda-partitioning-module-lab3/ (EN) and /fr/ (FR).

## 0. Setup that worked
- **One light clone per lab** (`eda-learning-lab3`), sparse: the slide pipeline, `common/`, the module, the tool,
  shared assets, the lab page. No branch, no stash. GitHub ran at 25 KB/s from China, so the clone was made in the
  cloud chat and handed over as a 22 MB zip.
- **Mullvad VPN** (WireGuard) routes everything. Slow server → switch to Tokyo, Hong Kong or Singapore.
- **Claude Code in VS Code**, one stage per conversation, `/add-dir ~/Documents/3A/SJTU/VLSI_Mort/test2` first.
- Long media runs (French and English voice and video) were run **by the student in a terminal**: Claude's
  background jobs gave no progress and one hung for 10 minutes on the network (0 % CPU).

## 1. Audit (Sonnet), what it found
- The teacher's goldens disagreed: EXAMPLES said seed 7 gives AE|BCD cut 12; the code gives AB|CDE cut 5.
- The shared `randomBipartition` sorted with a random comparator, so its result depended on node order:
  not reproducible in Python.
- Greedy had an unwritten tie-break, a forced node and **no size limit** (a 5|1 split on a star).
- A transcript slide described grow wrongly (it stops at 2 of 5 nodes).
- `common/` had no Python random/greedy/grow; the 10 browser challenges all passed by clicking a method button.

## 2. Content (Sonnet): decisions
- Random = **mulberry32 (the course's own PRNG) + 2 warm-up draws + Fisher–Yates**, shared by Python and JS.
  Without the warm-up, seeds 0–3 gave the same split (the second draw is near 0 for small seeds: verified).
- Greedy = an exact rule with a size cap; it now gives ABC|DE cut 3 on the tiny graph. The old greedy is kept as a
  contrast example.
- Checker `examples/initial_bipartition_check.py`: 23 PASS, `--show`, `--impl`, `--vs-node`.
- Three new graphs, each flipping one result: **star** (a size cap makes cut 15 the best legal one, the uncapped 5|1
  cut 5 is illegal), **tie** (anchor A–B gives 9, D–E gives 4), **bridge** (greedy 12, grow from A 4).
- 8-item quiz, EXAMPLES with tables pasted from the checker.

## 3. Script and figures (Opus)
- First version: 20 sections, 1,401 words, 8:31. Student feedback: **too long and repetitive**.
- Polish pass: 28 sections, 30 slides, 1,182 words, **7:26 EN / 7:55 FR**, in **5 parts** of 1:19–1:42, each with
  a hook and a "Pause and guess" answered by the next part; each idea said once (plus the recap); Pitfalls and
  Recap merged; 9 **step figures** so the picture changes every 5–10 s.
  → In the next lab, write it this way from the start (lab-upgrade Stage 3 now says so).
- Walkthrough frames redrawn by patching a **scratch copy** of the viewer (the real `walkthrough.js` is outside the
  allowed folders; put it on the teacher list).
- Figure scripts in `test2/tools/lab03-figures/` (`run_all.sh`, `facts.py`, `--lang fr`): they had first been left
  in Claude's temporary scratchpad. Never do that.

## 4. Browser lab (Opus)
- Model (`initial-bipartition-lab-model.js`, pure) + UI. 10 challenges that check what the learner built.
- Nothing passes on load, from a preset, from the reveal, or after editing a method's result.
- Colour rule after review: the side holding A is blue (as in the slides).
- Tests: 37 model-vs-checker checks; 70 Playwright cases (13 positive, 52 negative, 5 colour).

## 5. Site (Sonnet)
- Copied from the Lab 02 site; French transcript, figures, frames, lab strings; French voice built by the student.
- Then **5 video parts** (cut with the slide timings, cached, each part verified to start on the right slide),
  **speed buttons** 1–2× (remembered), gentle zoom on figure slides, French subtitle fix (a lone "?").
- Tests: 169 site checks, 70 lab cases per language. `docs/` 79 MB; `.cache/` in `.gitignore`.
- Push through the VPN at about 50 KB/s: 10–15 minutes.

## 6. Findings for the teacher (in WHAT_CHANGED.md)
1. `partitioning-core.js`: the `randomBipartition` docstring is wrong about seed 7, and the function depends on node order.
2. `enrich_transcripts.py` writes that wrong claim into transcripts (never rerun it on the module).
3. The tool page's DOCTYPE was missing `<`.
4. The shared partitioning benchmark (`partition-benchmark-app.js`) and multistart code still use the old random/greedy.
5. The walkthrough viewer (`walkthrough.js`) still holds the old frame text; the new text is in `assets/STEPS.md`.

## 7. Animated lessons (prototype → `lesson-animator` skill)
- Student: the video "isn't dynamic enough". A prototype for Part 1 drew the lesson **live in the browser**, in time
  with the narration: chip → graph morph, zooms, word-timed text, counters, balance bars, an auto-pause question,
  click-to-try. Second round: the voice felt forced and animations skipped → **pauses between sentences** (about 22 s
  per part) and **continuous moves** (a new move starts from where the last one is). Student: "way better".
- 1.6 MB per part (voice only), 60 fps on a CPU slowed 6×, French by swapping voice and texts; an MP4 can be recorded.
- Next: listen to the newer voices (`en-US-AndrewMultilingualNeural`, `fr-FR-VivienneMultilingualNeural`, ...) and
  build the real lessons with `voice_build.py` (exact word timings). Lessons sit **next to** the video parts.

## 8. Token measurement (optional, for the student)
`/usage` (plan limits) before and after each stage, plus `stage_tokens.py` for exact tokens per conversation.

## Checklist for the next lab
1. Find the lab on the website (crumb "Lab NN", URL `labs/<tool>/`), then module and tool names.
2. Make a light clone `eda-learning-labNN`; install the two skills; `/add-dir` the `test2` folder.
3. Stages 1–6 with `prompts.md`; review Stage 1 notes and the Stage 3 PDF carefully.
4. Write the script in parts from the start; keep figure scripts in `../tools/labNN-figures/`.
5. Site from the Lab 03 template; you run the media commands; check both languages' test lines.
6. Watch a part per language at 1.5×, push, Pages, WHAT_CHANGED.md to the teacher.
7. Optional: `lesson-animator` for each part.
