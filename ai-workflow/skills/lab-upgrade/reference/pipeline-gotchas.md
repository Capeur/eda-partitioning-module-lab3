# Teacher pipeline — commands and gotchas

Scripts live in `.cursor/skills/module-slides/scripts/` (read its `SKILL.md` only if something
here is unclear). Run from the repo root, inside the venv that has `requirements.txt`
(python-pptx, pyyaml, edge-tts) plus LibreOffice, ffmpeg and poppler-utils.

```bash
S=.cursor/skills/module-slides/scripts
M=courses/<course>/<module>
python3 $S/transcript_to_outline.py $M         # transcript.md -> outline.yaml + slides.md
python3 $S/build_pptx.py $M                    # -> slides.pptx
python3 $S/verify_clip.py $M
python3 $S/verify_transcript_consistency.py $M
bash    $S/pptx_to_pdf.sh $M/slides.pptx       # -> slides.pdf (LibreOffice)
pdftoppm -r 50 -png $M/slides.pdf /tmp/pg      # then LOOK at every page
# final, once text is frozen (needs internet: speech.platform.bing.com)
bash    $S/narrate_clips.sh $M                 # all of the above + audio + video.mp4
```

## Slide text (prose_to_bullets.py)
- The **first 6 sentences** of a slide's prose become bullets; the rest is spoken only.
- Each bullet is max **90 characters**. A longer sentence is cut at the first of
  `": "`, `"; "`, `" — "`, `" - "`, `", and "`, `", "` — and only **one half is kept**. So a
  long sentence silently loses half its meaning on screen. Keep sentences ≤ 90 characters.
- The title slide subtitle allows 120 characters.

## Images (transcript_to_outline.py)
- Paths starting `assets/lab…`, containing `real-shell`, or under `assets/steps/` become
  **full-slide images** (prose is spoken only).
- Any other image becomes a **two-column** slide (bullets left, image right): use tall images.
- Keep the alt text meaningful; it is also the image caption.

## Spoken text (transcript_to_speech.clean_narration_prose)
- Dashes `—` `–` become `", "`.
- **Any slash between words or numbers becomes "or"**: `2/3` is read "2 or 3", `A/B` "A or B".
  Write "two thirds", "A and B", "cut over total". `ABC|DE` is fine on a slide but write
  "A B C on one side, D E on the other" in prose if it should be spoken well.
- Markdown, code fences and image embeds are removed from speech.

## Code slides and timing
- A ```` ```bash ```` block in a section creates an extra slide titled `<title> — try these`.
  `synthesize_audio._norm_title` maps it back to its section by stripping the English
  suffixes "— try these", "— more", "— listing", "(n/m)". If titles are translated (French
  "— à essayer", "— suite"), patch `_norm_title` at runtime (see `make_fr_media.py`
  `french_norm_title`) or audio timings drift by one slide per code slide.
  Check: number of entries in `audio/slide_timings.json` = number of PDF pages.

## Other files
- `assets/STEPS.md` uses **CRLF** line endings. Normalise to LF, edit, write CRLF back; use
  `[^\n]+` not `.+?` in regexes over it.
- Keep `<!-- algorithm-walkthrough -->` … `<!-- /algorithm-walkthrough -->` and the
  `assets/steps/NN-*.png` names: the website walkthrough page reads them.
- Never delete or hand-edit `audio/`, `frames/`, `video.mp4`; regenerate them.
  If you break one while testing, `git checkout -- <path>`.

## Learned on Lab 03 (2026-10)
- **Course generators overwrite transcripts.** `courses/learn_partitioning/scripts/enrich_transcripts.py` writes
  slide-1 sentences (with a wrong seed-7 claim). Never run it, or similar scripts, on an upgraded module.
- **The walkthrough viewer is outside the allowed folders.** `platform/tools/algorithm-walkthrough/walkthrough.js`
  holds each lab's frame text. To redraw `assets/steps/*.png`, copy the platform to a scratch folder, patch that copy,
  and run the teacher's `capture_algorithm_walkthrough.py` against it; the current viewer CSS makes frames 940×636,
  so add `.walk-body{min-height:0}` and a 320 px canvas to get the teacher's 940×468. Put "copy the new frame text
  from STEPS.md into walkthrough.js" on the teacher list.
- **`capture_lab_snapshot.py` only loads the page** (an empty graph, cut at 1080 px). Write a capture script that
  runs a few starts first and shoots from the challenge box down.
- **Code slides add PDF pages**: transcript slides ≠ PDF pages. The site's `PARTS` use PDF pages.
- **French subtitles**: a space before `?` made a 67 ms cue with a lone "?"; keep the template's `_chunks` fix.
- **The title slide subtitle** must fit one line in both languages; shorten the first sentence if it wraps.
- **A tool page started with `!DOCTYPE html>`** (missing `<`): the text showed on the page (quirks mode). Fix it in
  the tool folder and tell the teacher (the same bug may be in other labs).
- **`__pycache__`** appears under `.cursor/skills/module-slides/scripts/` after running the lint: set
  `PYTHONDONTWRITEBYTECODE=1`; never commit them (the clone is never committed anyway).
- `pkill -f <pattern>` can kill the shell that runs it: stop jobs by pid.
