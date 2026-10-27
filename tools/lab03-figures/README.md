# Lab 03 figures (partitioning, initial bipartition)

Scripts that drew the Stage 3 pictures of
`eda-learning-lab3/courses/learn_partitioning/module01-03-initial-bipartition/assets/`.
They live outside the teacher clone on purpose. Stage 5 added a French option (`--lang fr`) and a copy of this folder
sits in the site repo (`eda-partitioning-module-lab3/tools/lab03-figures/`); this folder stays the source of truth.

## Run everything

```bash
bash run_all.sh                      # teacher clone defaults to ../../eda-learning-lab3
bash run_all.sh /path/to/clone       # or pass it
```

Needs: Python 3 with Playwright + Chromium (`pip install playwright && playwright install chromium`),
`curl`, the teacher clone, and `../../eda-learning/platform` (the full platform, which has the
walkthrough viewer the lab clone lacks). Ports 8080 and 8081 must be free.

It writes only into the module's `assets/`: the 5 walkthrough frames in `steps/` + `STEPS.md` (CRLF),
the 7 figures, `lab-starter.png`, and `real-shell.png` + `real-shell.txt`. Then rebuild the deck with the
teacher's pipeline (see `UPGRADE_NOTES.md` in the module).

## The files

| File | What it does |
|---|---|
| `facts.py <module>` | Runs the module checker and saves every split, cut, cut edge and side size to `facts.json`. All numbers on the pictures come from here. |
| `patch_walkthrough.py [--source …/platform]` | Copies the full platform to `wt-platform/` (first run only), writes the 5 frame texts into its `walkthrough.js`, and adds a CSS override that restores the teacher's frame shape (940×468). The teacher's viewer is never edited. |
| `make_figures.py --module <module> [--only name.png]` | Draws the 7 figures with the platform's own `drawGraph`. Needs `wt-platform/` served on port 8081. |
| `run_all.sh` | All of the above, plus the teacher's `capture_algorithm_walkthrough.py` and `capture_real_shell.py` with the options that were used, and `capture_lab.py`. |
| `capture_fr_frames.py --steps <walkthrough-steps.json> --out <folder>` | French walkthrough frames: loads the (English) scratch viewer, swaps the text for the French captions, shoots `#walk-frame` (same 940x468 size). |
| `capture_lab.py` | `assets/lab-starter.png` (slide 16): opens the Stage 4 lab, runs random seed 3, greedy, grow A and grow D, and shoots 1280×1080 from the challenge box down. Replaced `capture_lab_snapshot.py`, which only loads the page. |

Generated here (safe to delete): `facts.json`, `steps.json`, `wt-platform/`.

## Change one picture

- Frame text (title, caption, bullets, metrics): edit the `steps` list in `patch_walkthrough.py`, then `run_all.sh`.
- One figure: start the 8081 server on `wt-platform/`, then
  `python3 make_figures.py --module <module> --only star-cap.png`.
- Lab screenshot: `python3 capture_lab.py --module <clone>/courses/learn_partitioning/module01-03-initial-bipartition` (serve `<clone>/platform` on 8080 first), then rebuild the deck.

Colours: A's side is always blue, the other side green, cut edges red, the highlighted kept edge amber.

## French (Stage 5)

Output goes to the site repo, never to the teacher clone. Serve the scratch viewer on 8081 and the built site's `docs/` on 8090 first.

```bash
SITE=../eda-partitioning-module-lab3; M=../eda-learning-lab3/courses/learn_partitioning/module01-03-initial-bipartition
python3 make_figures.py --module $M --lang fr --out $SITE/i18n/fr/module01-03-initial-bipartition/assets     # 7 figures, TEXT["fr"]
python3 capture_fr_frames.py --steps $SITE/i18n/fr/walkthrough-steps.json --out $SITE/i18n/fr/module01-03-initial-bipartition/assets/steps
python3 capture_lab.py --lang fr --url http://127.0.0.1:8090/fr/tools/initial-bipartition/index.html \
    --out $SITE/i18n/fr/module01-03-initial-bipartition/assets/lab-starter.png
```

`make_figures.py` without `--lang` still writes the English figures, byte for byte the same as before (checked with `cmp`).
Numbers on the French frames must equal the English ones (the digits of every caption, bullet and metric line of `walkthrough-steps.json` were compared with `steps.json`, the English frames' source).
