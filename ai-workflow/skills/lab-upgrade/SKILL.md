---
name: lab-upgrade
description: Upgrade one lab of the yongfu-li/eda-learning course (any course, e.g. learn_partitioning or learn_clustering) - complete the thin teacher content, golden self-check script, a beginner narrated deck written in short parts with hooks, a graded interactive browser lab, and a bilingual EN/FR GitHub Pages site with video parts and speed control. Use when asked to upgrade, complete or improve a lab/module of eda-learning, or to run one stage of that work.
---

# Lab upgrade (eda-learning), version 3

Reproduces two finished, reviewed upgrades:
- clustering Lab 02 "affinity metrics": https://capeur.github.io/eda-clustering-module-lab2/
- partitioning Lab 03 "initial bipartition": https://capeur.github.io/eda-partitioning-module-lab3/ (**the template**:
  5 video parts, speed buttons, walkthrough section, 169 site checks, 70 lab cases per language)

**One stage per conversation.** Finish a stage, append to `UPGRADE_NOTES.md`, then the user starts a new conversation.
The full story of Lab 03, with every problem met and its fix, is in `PLAYBOOK.md` next to this file; read
`reference/workflow.md` before the first command of a session.

## 0. Inputs (ask once if missing, then write them to `UPGRADE_NOTES.md`)

| Input | Example (Lab 03) | How to find it |
|---|---|---|
| Course | `learn_partitioning` | `courses/` |
| Module dir | `module01-03-initial-bipartition` | lab page crumb, see below |
| Tool dir | `platform/tools/initial-bipartition` | `<script src>` in the lab page |
| Lab number | `Lab 03` | `grep -o 'Lab [0-9]*' platform/courses/<course>/labs/<tool>/index.html` |
| Teacher clone | `../eda-learning-lab3` | a separate light clone for this lab (workflow.md) |
| Site repo | `../eda-partitioning-module-lab3` | the user's own repo, created in Stage 5 from the template |

The lab number comes from the website crumb, never from the module number (module01-01 = Lab 02, module01-03 = Lab 03,
because Lab 01 is the intro).

## 1. Hard rules (never break)

1. Edit **only** `courses/<course>/<module>/` and `platform/tools/<tool>/` in the teacher clone.
   Never edit `common/`, `platform/assets/*`, other modules, or `.cursor/skills/module-slides/`.
   Importing from them (read-only) is fine. If a fix needs a shared file, work around it in the tool folder and
   put the shared-file problem on the **teacher list** (Stage 6).
2. Never `git commit`, `git push`, `git checkout -b` or open a PR in the teacher clone. It stays on `main`, with
   uncommitted changes; the user reviews `git diff`. The published result is the separate site repo.
3. The site repo is committed and pushed **by the user**, when they ask.
4. Keep the teacher's pipeline: slides, audio and video come from `.cursor/skills/module-slides/scripts/*` and
   `transcript.md`. Never hand-edit `slides.pptx`, `outline.yaml` or `audio/`.
5. **Every number comes from running code** (the module checker, `common/solvers.py`, the lab model), never from
   mental arithmetic. When two files state the same golden, check both against the code.
6. **Never run course generators** on the module (Lab 03: `courses/learn_partitioning/scripts/enrich_transcripts.py`
   rewrites transcripts with wrong claims).
7. **Long network or media runs** (`narrate_clips.sh`, `make_fr_media.py`, more than ~5 minutes): give the user the
   exact commands to run in their own terminal, wait, then check the outputs (workflow.md explains why).
8. Files that must survive the session (figure scripts, notes) go in `../tools/labNN-*/`, never only in the scratchpad.

## 2. Stages

### Stage 1: Audit (small model, about 10 minutes)
- Run `python3 ${CLAUDE_SKILL_DIR}/scripts/audit_lab.py <clone> <course> <module> <tool-name>` (bare tool name) and
  `python3 ${CLAUDE_SKILL_DIR}/scripts/lint_transcript.py <module>/transcript.md`.
- Read the module's `transcript.md`, `EXAMPLES.md`, `quiz.json` and the tool's `.js`.
- **Cross-check every golden** that appears in several places (EXAMPLES pseudocode, transcript titles, `.js`
  challenges, shared docstrings) by running the platform's own functions (node can import `platform/assets/*.js`).
  Lab 03 found: seed 7 wrong everywhere; a "random" that depends on node order; a greedy with an unwritten
  tie-break, a forced node and no size limit; a transcript slide that described grow wrongly.
- Note what `common/` lacks (Lab 03: random, greedy and grow had no Python version) and every vague rule.
- Write `UPGRADE_NOTES.md`: inputs, gaps, golden cross-check table, hidden problems, 2–4 concepts to teach,
  plan for stages 2–5, **open questions with a recommended answer each**. Done when the user approves.

### Stage 2: Content and goldens (small model)
Read `reference/content-recipe.md` §1–§3.
- `examples/<topic>_check.py`: reference implementation with **exact written rules** (tie-breaks, caps), golden
  tables, `--show`, `--impl my.py`, and a reversed-input check. If a golden depends on randomness, use **one
  portable PRNG** in Python and JS (Lab 03: the course's `mulberry32` + 2 warm-up draws + Fisher–Yates; small seeds
  give a near-zero second draw without the warm-up) and a `--vs-node` check that both sides agree.
- Extra example graphs in `examples/*.json`, each showing one idea flipping a result.
- `EXAMPLES.md`, `quiz.json` (6–8 items), `CHECKLIST.md`, `README.md`, `assets/_demo.sh`.
- Done when the checker prints all PASS and a deliberately wrong `--impl` gives FAIL/SKIP.

### Stage 3: Beginner script in parts, and figures (strong model)
Read `reference/content-recipe.md` §4 and `reference/pipeline-gotchas.md`.
- Write `transcript.md` **already in 4–6 parts** of 1–2 minutes: each part opens with a hook and ends with a
  "Pause and guess" question answered at the start of the next part. Follow the **repetition rules** (each idea said
  once where it's taught, once in the recap). Target 1,100–1,300 spoken words (7–8 minutes).
- Figures in `assets/` (tall), plus **step figures** (the same figure with later parts hidden) so the picture changes
  every 5–10 s. Walkthrough frames (`assets/steps/`, 5 of them) are redrawn with the teacher's capture script
  against a scratch copy of the viewer.
- Figure scripts live in `../tools/labNN-figures/` with `run_all.sh` and a README (never only in the scratchpad).
- Lint until clean; build outline, pptx, verify scripts, PDF; look at every page. Audio and video at the end.
- Write the part boundaries (slide ranges and PDF pages) in the notes: Stage 5 needs them.

### Stage 4: Interactive browser lab (strong model)
Read `reference/content-recipe.md` §5 and `reference/testing.md`.
- Split into `<tool>-lab-model.js` (pure, no DOM; imports shared helpers read-only) and `<tool>.js` (UI).
- 8–10 challenges that check what the learner **built**; nothing passes on page load, from a preset button or from
  the study reveal; editing after a method button cancels that method.
- Colours follow the figures (the group holding the first node name is blue).
- Tests: model vs checker (Node), Playwright positive and negative cases (page load, wrong split, matching start
  button, edit after a start, reveal) and colour checks. Recapture the lab screenshot the deck uses.

### Stage 5: Site repo in EN and FR (medium model)
Read `reference/site-template.md`.
- Copy the **Lab 03 site repo** (fresh `git init -b main`, no old history, no `docs/`, no `.cache/`), change the
  lab-specific places listed there, set `PARTS`, translate into `i18n/fr/`, make French figures and frames.
- Give the user the media commands (rule 7). Then build, run `tools/test_site.py` and `tools/test_lab_site.py`, and
  read **both** language lines of each test.

### Stage 6: Final check and hand-off
- `git -C <clone> status`: changes only in the two allowed folders (ignore `__pycache__`).
- The English media (`narrate_clips.sh`) run by the user, then rebuild the site and rerun both tests.
- `WHAT_CHANGED.md` in the site repo: concepts, files, figures, challenges, tests, part lengths, and
  **Findings for the teacher** (shared-file bugs found, generators not to run, stale viewer text).
- Copy `UPGRADE_NOTES.md` to `../tools/labNN-notes/`, then delete it from the module.
- Remind the user: commit and push the site repo, Pages on main `/docs`.

### Stage 7 (optional): animated lessons
Use the separate `lesson-animator` skill: an interactive lesson per part, next to the video parts.

## 3. `UPGRADE_NOTES.md` after every stage
Append: what was done, files touched, commands that verify it, decisions taken, open questions. The next
conversation starts by reading it instead of re-exploring the repo.

## 4. Files
- `PLAYBOOK.md`: the whole Lab 03 run, step by step, with the problems met and how they were solved.
- `reference/workflow.md`: clone, network, VS Code, permissions, models, tokens, stuck runs.
- `reference/content-recipe.md`, `reference/pipeline-gotchas.md`, `reference/site-template.md`, `reference/testing.md`.
- `prompts.md`: copy-paste prompts per stage.
- `scripts/audit_lab.py`, `scripts/lint_transcript.py`, `scripts/stage_tokens.py`.
