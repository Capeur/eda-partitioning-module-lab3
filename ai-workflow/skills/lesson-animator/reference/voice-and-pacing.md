# Voice and pacing

## Why the course video sounds "forced"
- The teacher's pipeline uses `en-US-JennyNeural` and `fr-FR-DeniseNeural`, older assistant-style voices.
- Each slide's narration is read in one go, with no pauses between sentences.
- The script reads like a textbook (long sentences, no questions to the listener).

## Fix 1: a newer voice (no code change)
Generate the same lines with a few voices and let the user choose by ear:
```bash
T="So, here's the question. Could a split made at random be just as good? Take a second to think about it."
for V in en-US-JennyNeural en-US-AndrewMultilingualNeural en-US-AvaMultilingualNeural en-US-EmmaMultilingualNeural en-US-BrianMultilingualNeural; do
  edge-tts --voice $V --text "$T" --write-media "/tmp/$V.mp3"; done
F="Alors, voici la question. Un découpage fait au hasard peut-il être aussi bon ? Prenez une seconde pour y réfléchir."
for V in fr-FR-DeniseNeural fr-FR-VivienneMultilingualNeural fr-FR-RemyMultilingualNeural; do
  edge-tts --voice $V --text "$F" --write-media "/tmp/$V.mp3"; done
edge-tts --list-voices | grep -i multilingual      # what exists today
```
`voice_build.py --voice ... --rate=-4%` uses the chosen voice; a rate of −3 to −6 % sounds calmer.
(The course video can use it too: `VOICE=... narrate_clips.sh` and `VOICE=... make_fr_media.py`.)

## Fix 2: pauses between sentences (lessonlib.pause_plan)
`voice_build.py` records one clip per sentence and joins them with silence:

| After | Default | Storyboard key |
|---|---|---|
| a sentence, same slide | 0.55 s | `pausing.between` |
| the last sentence of a slide (picture changes) | + 0.9 s | `pausing.scene` |
| a question | 1.3 s | `pausing.question` |
| the last sentence | 2.0 s | `pausing.tail` |
| a specific sentence | any | `pauses: [{ "after": "@anchor" or "slide:N:end", "sec": 1.5 }]` |

Use explicit pauses after: a number that should sink in ("from three to sixteen", "2 + 1 = 3"), a list being
revealed (labels popping one by one), a swap or regrouping animation, a definition.
Lab 03 Part 1: 102 s of speech became about 124 s with about 22 s of pauses, and it felt much more human.

## Fix 3: write for the ear (transcript edits, done in the module's transcript.md)
- Short sentences; contractions ("it's", "you'll", "c'est"); one idea each.
- Talk to the learner: "Look at C.", "Here's the thing:", "So…", short questions.
- Say numbers in words; no slashes, no symbols (the teacher's linter flags them).
- After editing, rerun the module's lint and rebuild the course deck and video as usual.

## Word timings
- `voice_build.py` asks edge-tts for **WordBoundary** events (edge-tts 7.1+: `boundary="WordBoundary"`), so each
  word has its exact time. Older edge-tts sends them by default; with none, times are estimated and the script says so.
- `timing_from_vtt.py` estimates word times inside each subtitle line by character position: a highlight can be
  0.1–0.3 s off. Good for a prototype; use `voice_build.py` for the real thing.

## Network (mainland China)
- edge-tts needs `speech.platform.bing.com`: a VPN must be on. Mullvad (WireGuard) routes everything; if it is
  slow, switch server (Tokyo, Hong Kong, Singapore) and test speed:
  `curl -o /dev/null -w "%{speed_download}\n" https://speed.cloudflare.com/__down?bytes=10000000`.
- `voice_build.py` prints one line per sentence, times out a stuck request (`--timeout 40`), retries 3 times,
  and caches finished sentences in `--workdir`: after a failure, fix the VPN and run the same command again.
- A process with 0 % CPU and no new file for minutes is waiting on the network: stop it (Ctrl+C) and rerun.
