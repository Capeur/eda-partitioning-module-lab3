# Example: Lab 03 (initial bipartition), Part 1 "What and why", EN + FR

Transcript slides 1–6, 23 sentences in each language (same sentences per slide). Graph = the lab's tiny graph
(A–B 5, A–C 1, B–C 4, C–D 2, D–E 5, C–E 1). The storyboard is a port of the prototype the student reviewed
("way better", "dynamic enough"), with its fixes: one zoom instead of two, French headlines resized, texts that
stay at least 2 s, a real stop at the question, and the term "Initial bipartition" capitalised.

## Scenes (anchor words EN / FR)
| Slide | Scene | Main changes |
|---|---|---|
| 1 | Hook | split on *first / première*; ACE \| BD and the counter 3 → 16 on *sixteen / seize*; thumbnails of three starts, "best" on *best / meilleur* |
| 2 | Chip | cells as copper rectangles with wire bundles; letters pop on *five / cinq*; zoom on *many / beaucoup* |
| 3 | Graph | rectangles → dots on *dot / point*; wires merge on *edge / arête*; weights on *weight / poids*; A–B, D–E amber on *heaviest / lourdes* |
| 4 | Cut | split + divider on *two / deux*; zoom on the cut edges on *cut / coupées*; "2 + 1 = 3" built term by term |
| 5 | Balance | all on one side, cut 0, "useless"; bars; the max-3 line on *more / dépasse*; back to ABC \| DE on *five / cinq* |
| 6 | Why a start | ACE \| BD cut 16; swap B ↔ E on *moving / déplaçant* (counter 16 → 3); "?"; teams; bad vs good start; question |

## Commands used (from the site repo, teacher clone at ../eda-learning-lab3)
```bash
SK=~/.claude/skills/lesson-animator; EX=$SK/examples/lab03-part1
for L in en fr; do P=$([ $L = fr ] && echo docs/fr || echo docs)
  python3 $SK/scripts/timing_from_vtt.py --transcript $P/transcript.md --slides 1-6 \
      --vtt $P/parts/part-1.vtt --audio $P/parts/part-1.mp4 --lang $L --storyboard $EX/storyboard.json \
      --repo ../eda-learning-lab3 --out-audio build/lessons/part-1/lesson-$L.m4a --out-timing build/lessons/part-1/timing-$L.json
  python3 $SK/scripts/build_lesson.py --storyboard $EX/storyboard.json --timing build/lessons/part-1/timing-$L.json \
      --audio build/lessons/part-1/lesson-$L.m4a --lang $L --out $([ $L = fr ] && echo docs/fr || echo docs)/lessons/part-1 \
      --fonts site_src/fonts --storage-key lab03-lesson-speed
done
python3 $SK/scripts/check_lesson.py docs/lessons/part-1/index.html docs/fr/lessons/part-1/index.html --sheets build/check
```
To use a new, more natural voice instead, replace `timing_from_vtt.py` by `voice_build.py` with `--voice` and `--rate`
(see `reference/voice-and-pacing.md`); the storyboard does not change.

## Results (2026-10-27, from the published site's Part 1)
- Alignment: 23/23 sentences with the exact word count, EN and FR.
- Length with pauses: EN 102.1 → 123.7 s, FR 103.5 → 125.1 s (21.6 s of pauses).
- Checker: claims 8/8, 0 errors, 0 warnings in both languages; script per frame 0.8 ms median, 2.5 ms for 95 %
  of frames on a CPU slowed 6×.
- `record_mp4.py`: 6 s test clip at 1280 × 720 in 19 s.
- `voice_build.py` was tested with a stand-in for edge-tts (no network in the build sandbox): 23 clips, word
  timings, pauses, cache reuse on the second run. **Not yet run against the real edge-tts**: the first real run
  should be watched (word boundaries present? `"words": "exact"` in the timing file).
