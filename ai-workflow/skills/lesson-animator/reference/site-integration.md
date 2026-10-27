# Putting lessons next to the video parts (site repo built from eda-partitioning-module-lab3)

Decision (2026-10-27): the animated lesson **sits next to** the video parts; the course video stays as it is.

## Where things go
```
<site repo>/
  lessons/part-N/storyboard.json        # source (committed)
  lessons/part-N/README.md              # inputs, voices, commands, check result
  .cache/voice/                         # voice_build cache (already ignored: .cache/ is in .gitignore)
  build/lessons/                        # timing + audio made by voice_build or timing_from_vtt (add build/ to .gitignore)
  docs/lessons/part-N/index.html        # built English page + lesson-en.m4a + fonts/
  docs/fr/lessons/part-N/index.html     # built French page + lesson-fr.m4a + fonts/
```
Keep the built pages out of `build_site.py`'s cleanup (it may empty `docs/`): either build the lessons from
`build_site.py` (preferred, below) or rebuild them after every site build.

## build_site.py changes (lab-specific places stay the same)
1. After `build_parts(...)`, for each part N that has `lessons/part-N/storyboard.json` and its timing + audio in
   `build/lessons/`, call `build_lesson.py` (import its `main` or run it with `subprocess`) with
   `--out <out>/lessons/part-N --fonts site_src/fonts --storage-key labNN-lesson-speed`.
2. In `player_html`, give each part item a second link when its lesson exists:
   `<a class="lesson-link" href="lessons/part-N/">{t["lesson_link"]}</a>` (outside the `<button>`, so the button
   still loads the video).
3. `i18n/strings.py`: add `lesson_link` ("Interactive lesson" / "Leçon interactive") and a sentence in
   `parts_note` saying each part also exists as an interactive lesson.
4. The lesson page needs a way back: add to the storyboard `"lede"` a link to `../../index.html#video`
   (lede accepts HTML), in both languages.

## Tests to add (tools/test_site.py)
- each part with a storyboard has `lessons/part-N/index.html` and its audio, in EN and FR;
- the lesson link is in the part list and opens the page; the page has no external request (fonts self-hosted);
- `window.__lesson.errors` is empty on every lesson page; and run `check_lesson.py` on all of them (0 errors, 0 warnings).

## Pushing
Lesson audio is small (about 1.2 MB per part per language with pauses), much less than a video part.
Commit `lessons/*/storyboard.json`, `docs/lessons`, `docs/fr/lessons`; not `.cache/` or `build/`.
