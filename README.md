# Lab 03 — Initial bipartition · Partitioning for EDA

A standalone, **bilingual (English / French)** GitHub Pages site for **Lab 03 (initial bipartition)** of the
[Partitioning for EDA course](https://github.com/yongfu-li/eda-learning) — a review build of the
upgraded lab, not yet merged into the course repository.

- English: `https://capeur.github.io/eda-partitioning-module-lab3/`
- Français : `https://capeur.github.io/eda-partitioning-module-lab3/fr/`

Each language has the narrated video with subtitles, every slide as an image, the five-frame walkthrough with its
captions, PDF/PowerPoint downloads, the **interactive browser lab** (10 challenges that check the split you built),
the Track A material, a quiz and the full transcript. A switch in every header (page and lab) jumps to the other
language at the same place.

Built from the Lab 02 template (`eda-clustering-module-lab2`) with a fresh history.

## Layout

| Path | What |
|------|------|
| `build_site.py` | builds `docs/` (English) and `docs/fr/` (French) |
| `make_fr_media.py` | builds the French slides, narration and video with the course's own tools |
| `site_src/` | page template, CSS, quiz script, self-hosted fonts (shared by both languages) |
| `i18n/strings.py` | all page text, English and French |
| `i18n/fr/module01-03-initial-bipartition/` | French narration (`transcript.md`), French images, French deck |
| `i18n/fr/EXAMPLES.md`, `i18n/fr/quiz.json` | French Track A guide and quiz |
| `i18n/fr/walkthrough-steps.json` | French captions of the five walkthrough frames (the English ones are the course's `assets/STEPS.md`) |
| `i18n/fr/lab_strings.py` | French text for the browser lab (exact replacements; the build fails if the lab changed) |
| `tools/lab03-figures/` | the scripts that draw the figures, the walkthrough frames and the lab screenshot, English and French |
| `tools/test_site.py`, `tools/test_lab_site.py` | Playwright tests of the built site and of the lab's 10 challenges, in both languages |
| `docs/` | the built site served by GitHub Pages (main branch, `/docs`) |

English content comes from your `eda-learning` clone (Lab 03 upgrade applied); nothing in it is modified. The lab is
copied file by file (`platform/tools/initial-bipartition/`, **without** its `tests/` folder) plus the shared
`platform/assets/` files it imports.

## Rebuild

```bash
# English narration + video, in the course clone (needs internet)
cd ~/path/to/eda-learning-lab3
bash .cursor/skills/module-slides/scripts/narrate_clips.sh \
  courses/learn_partitioning/module01-03-initial-bipartition

# French slides + narration + video, here (needs internet, LibreOffice, ffmpeg)
cd ~/path/to/eda-partitioning-module-lab3
pip install markdown pyyaml edge-tts pillow
python3 make_fr_media.py --repo ../eda-learning-lab3

# both sites
python3 build_site.py --repo ../eda-learning-lab3
git add -A && git commit -m "Rebuild site" && git push
```

If an English `video.mp4` is older than the deck, `build_site.py` warns; if its audio timings do not match the number of
slides, it embeds the video without subtitles and warns that it is stale.

Preview: `python3 -m http.server 8090 --directory docs` → `http://127.0.0.1:8090/` and `/fr/`.

## Tests

```bash
python3 -m http.server 8090 --directory docs &
python3 tools/test_site.py          # page, walkthrough captions, quiz, switch, 0 external requests, fonts
python3 tools/test_lab_site.py      # the 10 challenges: positive and negative cases, EN and FR
```

## French images

The French frames, figures and lab screenshot are made by `tools/lab03-figures/` (see its README), which is a snapshot
of `~/Documents/3A/SJTU/VLSI_Mort/test2/tools/lab03-figures/`:

```bash
# serve the scratch walkthrough viewer (8081) and the built docs (8090), then
python3 tools/lab03-figures/make_figures.py --module ../eda-learning-lab3/courses/learn_partitioning/module01-03-initial-bipartition \
    --lang fr --out i18n/fr/module01-03-initial-bipartition/assets
python3 tools/lab03-figures/capture_fr_frames.py --steps i18n/fr/walkthrough-steps.json \
    --out i18n/fr/module01-03-initial-bipartition/assets/steps
python3 tools/lab03-figures/capture_lab.py --lang fr --url http://127.0.0.1:8090/fr/tools/initial-bipartition/index.html \
    --out i18n/fr/module01-03-initial-bipartition/assets/lab-starter.png
```

Rebuild the French deck (`make_fr_media.py`) and the site afterwards.

**Terminology (French):** *netlist*, *net* and *quiz* stay in English, as in French EDA courses; *partition*,
*bipartition*, *coupe* (cut), *taille de coupe* (cutsize), *équilibre* (balance), *côté* (side), *valide* (legal),
*glouton* (greedy), *croissance* (grow), *graine* (seed). Code, commands and program output stay in English.

## Credits

Course content, browser lab framework and media pipeline: the
[EDA Algorithms Platform](https://github.com/yongfu-li/eda-learning) (CC BY 4.0).
Lab 03 upgrade and French translation built for the course assignment.
