# Design rules: what made the Lab 03 prototype feel right

These come from building and reviewing the prototype with the student (who found the first version "forced"
and noticed animations skipping). Follow them unless the user asks otherwise.

## Rhythm
- **One idea per sentence, one visual change per idea.** Each sentence gets at most one big change (a pose, a
  camera move, a split) plus small accents (a word appearing, an edge flashing).
- **Let moves finish.** A pose takes 1.1 s, a camera move 1.3 s. If two big changes fall inside one short sentence,
  merge them (Lab 03: one zoom framing A, B and C instead of zoom A–B then A–C 1.5 s later).
- **Text stays at least 2 s** (checker default). Swap two short headlines for one headline whose second half
  appears on its word: `"Before you can improve a split… {you need a **first** one.@needs}"`.
- **The picture should change every 5–10 s.** A sentence with nothing moving for 8 s feels static: add an accent
  (flash the edges being talked about, pulse an edge, pop a tag).
- **Pauses carry meaning** (see `voice-and-pacing.md`): longer after a number that should sink in, at scene
  changes, and a real stop at the question.

## Layout on the 960 × 540 stage
- Headline top-left (x 4 %, y 3–6 %); facts (tags, equation) top-right or bottom-left; counter bottom-right
  (81 %, 68 %); balance bars right (77 %, 26 %). Nodes stay below the top quarter.
- French runs about 15–25 % longer: give French headlines room (`size` 3.6 instead of 4.3) or shorten them.
  Check the French contact sheet, not only the English one.
- A card that covers the graph (thumbnails, compare table, big "?") goes with `dim` 0.12–0.15 on the graph.
- Never put text where a node will **move to** during the same window (a swap, a regrouping): put it on the side.
- Zooms: frame the 2–3 nodes being talked about; zoom out on the next scene change. Not more than one zoom per slide.

## Colour and meaning (same as the course lab and figures)
- Blue = the group holding the first node name, green = the other, red dashed = cut edge, amber = highlighted kept
  edge, grey = not placed yet, copper = chip and wires.
- The counter turns red for bad cuts (`badCut`), green for the best legal one (`goodCut`).

## Words on screen
- Headlines say the idea in under 8 words; they do not repeat the narration word for word.
- Terms get a card the first time (capitalised: "Initial bipartition") with a plain definition.
- Numbers on screen must be in `claims` or come from the lab's checker. No number appears only on screen.
- "Pause and guess" is a real stop: the question card, two or three answers, a reply that gives the reason and
  points to the next part.

## Interactivity
- Clicking any node pauses the lesson and enters "your split": the learner moves nodes and sees the cut, the
  sizes and legality live. "Back to the lesson" resumes.
- The bench under the player repeats the question and (for partition labs) deals random splits by seed.
- Keyboard: Space plays and pauses; nodes are focusable (Enter moves them).

## Accessibility and speed
- `prefers-reduced-motion` makes every move instant (no glides or zooms).
- Script per frame stays under 3 ms on a CPU slowed 6× (5 nodes); the checker reports it. Keep graphs under ~30 nodes.
