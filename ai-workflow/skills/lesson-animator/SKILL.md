---
name: lesson-animator
description: Turn one part of an eda-learning lab's narration into an animated, interactive lesson page (graph that moves with the voice, word-timed text, zooms, live cut counter, auto-pause "pause and guess", click-to-try, EN and FR from one storyboard), with natural pauses and optional MP4 export. Use when asked for a dynamic or animated video/lesson for a lab, or to add one next to the site's video parts.
---

# Lesson animator

Builds what the Lab 03 prototype showed: a web page that plays the narration and **draws the lesson live**
(not a video file). One storyboard drives English and French; each animation is anchored to a word in each
language, so it lands on that word whatever the language's pace. Everything on screen is a pure function of
the audio time, so seeking, the 1×–2× speed buttons and frame-by-frame MP4 recording all agree.

Worked example (Lab 03, Part 1, EN + FR, checks clean): `examples/lab03-part1/` (read its README first).

## Hard rules
1. **Numbers come from the lab's rules.** Every split, cut or seed the text states goes in `claims`; the engine
   recomputes them (cut, legality, the course's mulberry32 dealer) and the checker fails on any mismatch.
   Numbers that come from elsewhere (KL results, best-of tables) are taken from the lab's checker output.
2. **Never edit the teacher's pipeline.** The lesson page sits *next to* the course video. It reads the
   transcript and (optionally) the site's existing part audio; it writes only into the site repo
   (or a folder the user names).
3. **One storyboard per part, both languages in it.** Each anchor has an `en` and an `fr` word; each text has
   `en` and `fr`. A word that occurs twice in a slide is written `"three#1"` (second occurrence).
4. **Run the checker before showing anything** (`scripts/check_lesson.py`, 0 errors, 0 warnings), and look at
   the contact sheet of each language.
5. Long network steps (voice) print one line per sentence; if nothing new appears for a minute, stop, ask the
   user to switch VPN server, and rerun the same command (finished sentences are cached).

## Inputs (ask once, then write them in the part's folder `lessons/part-N/README.md`)
| Input | Example |
|---|---|
| Transcript(s) | `courses/<course>/<module>/transcript.md` (EN), `i18n/fr/<module>/transcript.md` (FR) |
| Part's slide range | transcript slides `1-6` (the site's `PARTS` use PDF pages; code slides make them differ) |
| Voice source | A) new voice: `voice_build.py` (preferred) · B) reuse the site's `docs/parts/part-N.mp4` + `.vtt`: `timing_from_vtt.py` |
| Voices (A) | listen to samples first; e.g. `en-US-AndrewMultilingualNeural`, `fr-FR-VivienneMultilingualNeural`, `--rate=-4%` |
| The lab's graph | the module's `examples/*.json` (nodes, edges, weights) |
| Output | site repo `docs/lessons/part-N/` and `docs/fr/lessons/part-N/` |

## Steps (one Claude Code conversation per part is plenty)
1. **Read** `reference/storyboard.md` (format) and `reference/design-rules.md` (what makes it feel right).
   List the part's spoken sentences in each language (the words anchors are searched in):
   `python3 scripts/lessonlib.py <transcript.md> 1-6 --repo <teacher clone>`. EN and FR should have the same
   sentences per slide; if not, anchors still work (they search the whole slide), but compare the two lists.
2. **Write `storyboard.json`**: poses (where nodes stand), splits, camera shots, the timeline (what changes
   on which word), show windows (cut colouring, counter, balance…), overlays (headlines, terms, tags,
   equations, compare table, question), the question, chapters, claims, pause rules. Start by copying the
   example and changing it; keep its scene rhythm (one idea per sentence).
3. **Voice + timings** for each language:
   - A (new, natural voice, exact word timings):
     `python3 scripts/voice_build.py --transcript T --slides 1-6 --lang en --voice V --rate=-4% --storyboard SB --repo <teacher clone> --workdir .cache/voice --out-audio build/lesson-en.m4a --out-timing build/timing-en.json`
   - B (reuse the existing narration, estimated word timings):
     `python3 scripts/timing_from_vtt.py --transcript T --slides 1-6 --vtt docs/parts/part-1.vtt --audio docs/parts/part-1.mp4 --lang en --storyboard SB --repo <clone> --out-audio ... --out-timing ...`
   Both add the pauses (`reference/voice-and-pacing.md`).
4. **Build**: `python3 scripts/build_lesson.py --storyboard SB --timing build/timing-en.json --audio build/lesson-en.m4a --lang en --out docs/lessons/part-1 --fonts site_src/fonts --storage-key labNN-lesson-speed` (same for `fr` into `docs/fr/lessons/part-1`). `--fonts` self-hosts the fonts (Google Fonts is blocked in mainland China).
5. **Check**: `python3 scripts/check_lesson.py docs/lessons/part-1/index.html docs/fr/lessons/part-1/index.html --sheets build/check`. Fix every error and warning in the storyboard (move a text, shorten it, add a pause after a sentence, move a key), rebuild, recheck. Then look at both contact sheets.
6. **Link it from the site** next to the video parts (`reference/site-integration.md`), rebuild the site, run its tests.
7. Optional: `python3 scripts/record_mp4.py docs/lessons/part-1/index.html --audio ... --out lesson-part1-en.mp4` (about 3 s of work per second of video at 1280 px).

## Files
- `engine/lesson-engine.js`, `engine/lesson.css`, `engine/lesson.html`: the player (no library, no network).
- `scripts/lessonlib.py`: transcript → spoken sentences (the teacher's cleaner when `--repo` is given), anchors, pauses, ffmpeg concat.
- `scripts/voice_build.py`, `scripts/timing_from_vtt.py`, `scripts/build_lesson.py`, `scripts/check_lesson.py`, `scripts/record_mp4.py`.
- `reference/storyboard.md`, `reference/design-rules.md`, `reference/voice-and-pacing.md`, `reference/site-integration.md`.
- `examples/lab03-part1/`: storyboard + README with the exact commands and results.

Needs: Python 3.10+, ffmpeg, `pip install playwright pillow edge-tts` (edge-tts 7.1+ for word timings), `python3 -m playwright install chromium`.
