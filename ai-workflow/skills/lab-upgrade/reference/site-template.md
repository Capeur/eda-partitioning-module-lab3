# Site repo from the Lab 03 template

Template: the user's repo `eda-partitioning-module-lab3` (live at https://capeur.github.io/eda-partitioning-module-lab3/).
It has: English and French pages, the narrated video **cut into parts** with subtitles per part, speed buttons
(1–2×, remembered), gentle zoom on figure slides in the parts, the walkthrough section, slides, PDF/PPTX downloads,
the lab, Track A files, quiz, transcript, self-hosted fonts, WebP images, 0 external requests, and two test scripts.
Do **not** rewrite the builder: copy the repo and change the lab-specific places.

```bash
cd ~/Documents/3A/SJTU/VLSI_Mort/test2
rsync -a --exclude .git --exclude docs --exclude .cache --exclude 'i18n/fr/module*' --exclude 'tools/lab03-figures' eda-partitioning-module-lab3/ eda-<course-short>-module-labNN/
cd eda-<course-short>-module-labNN && git init -b main && mkdir docs
grep -rn -E "initial-bipartition|initial_bipartition|module01-03|learn_partitioning|lab03|Lab 03|bipartition initiale" \
  --include='*.py' --include='*.tmpl' --include='*.md' --include='*.js' --include='*.css' --include='.gitignore' .
```

## Places to change (the grep finds them all)
| File | What |
|---|---|
| `build_site.py` constants | `FR_MODULE`, `MODULE_REL`, `TOOL_REL`, **`PARTS`** (PDF page ranges of the parts, from the Stage 3 notes) |
| `build_site.py` `copy_lab` | destination `tools/<tool>`, the model file name, the CSS the lab page links |
| `build_site.py` `other_lab` | the two `tools/<tool>/index.html` links (EN ↔ FR) |
| `build_site.py` docstring, `README.md` | names, paths, URLs |
| `make_fr_media.py` | `FR_DIR`, `MODULE_REL`, `FOOTER` (French course footer, e.g. "learn_partitioning — 03 bipartition initiale") |
| `site_src/player.js` | `KEY` (`labNN-speed`) |
| `site_src/index.html.tmpl` | tool hrefs |
| `i18n/strings.py` | every EN and FR string, including `part_titles` (one per part) and `parts_note` |
| `i18n/fr/lab_strings.py` | rewrite for the new lab's JS and HTML (below) |
| `i18n/fr/EXAMPLES.md`, `quiz.json`, `walkthrough-steps.json`, `<module>/transcript.md` + figures | translations |
| `.gitignore` | the French media folder names (`i18n/fr/<module>/audio/`, `frames/`, `video.mp4`, `build.log`) and `.cache/` |
| `tools/test_site.py` | module paths, the speed key, the example file list, the lab tool path and model file |
| `tools/test_lab_site.py` | rewrite for the new lab's challenges (from the clone's `tests/test_lab_playwright.py`) with an EN/FR `LANGS` table |
| `tools/labNN-figures/` | the new lab's figure scripts (copy of `../tools/labNN-figures`) |

## How the parts work (build_site.py)
- `PARTS = [(first_page, last_page), ...]` in **PDF pages** (code slides make pages differ from transcript slides).
- Each part is cut from `video.mp4` with the slide timings (`audio/slide_timings.json`; French ones for French),
  re-encoded (`-preset veryfast -crf 27`), with its own `part-N.vtt`. Results are cached in `.cache/parts/`
  (keep `.cache/` in `.gitignore`, or every push uploads the videos twice).
- The build checks a frame of every slide of every part against the deck: it stops if a part starts on the wrong slide.
- Zoom only in figure slides (`two_column`, `image`) of 4 s or more, 1.00 → 1.06; the full video has none.
- A lone "?" subtitle (French puts a space before ?) is avoided by `_chunks`; keep that fix.

## French lab text (`lab_strings.py`)
Exact `(english, french)` replacements per file (lab `index.html`, the tool's JS, its model's messages, and any
shared JS that prints UI text). The build stops if a snippet is not found. Collect strings with
`grep -n -o -E '"[^"]*[A-Za-z]{3,}[^"]*"|`[^`]*`' platform/tools/<tool>/*.js`. Never translate ids or classes.
Terminology: *partition, bipartition, coupe* (cut), *taille de coupe* (cutsize), *équilibre* (balance),
*côté* (side), *graine* (seed), *aléatoire / gloutonne / par croissance* (random / greedy / grow). Code, commands and
program output stay English.

## French media
`make_fr_media.py --repo <clone>` copies the French transcript into `i18n/fr/<module>/`, runs the teacher's builder
there, localises footer and code-slide titles, patches `_norm_title`, voices with `VOICE` (default fr-FR-DeniseNeural)
and builds the video. The user runs it in a terminal (it takes 10–30 minutes and needs the VPN). The French transcript
keeps the English slide count and image paths. The title slide's subtitle must fit one line (shorten it if not).

## Build, test, publish
```bash
python3 build_site.py --repo ../eda-learning-labNN          # about 5 min the first time, 40 s with the parts cache
python3 -m http.server 8090 --directory docs &              # stop it by pid afterwards
python3 tools/test_site.py && python3 tools/test_lab_site.py   # read BOTH language lines of each
```
The test Chromium cannot play H.264: real playback (and "next part starts by itself") must be checked by the user in
Firefox or Chrome, once per language, at 1.5×.
Publish: empty GitHub repo, `git remote add origin git@github.com:<user>/<repo>.git`, commit, push (about 40–80 MB the
first time; slow through a VPN), then Settings → Pages → main, `/docs`.
