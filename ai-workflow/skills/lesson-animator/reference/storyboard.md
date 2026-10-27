# Storyboard format (one JSON file per part, both languages)

The stage is a 960 × 540 drawing (16:9). Positions of nodes and camera shots use those units; overlay positions
use % of the stage (`x`, `y` = top-left corner). Copy `examples/lab03-part1/storyboard.json` and edit it.

## Times: anchors and references
Every `at`, `from`, `to` is a **time reference**:

| Reference | Meaning |
|---|---|
| `"@name"` | the word of anchor `name` (defined in `anchors`), in the page's language |
| `"@name+0.4"`, `"@name-0.3"` | shifted by seconds |
| `"slide:4"` / `"slide:4:end"` | start of the first / end of the last sentence of transcript slide 4 |
| `"start"`, `"end"` (`"start+0.2"`) | start / end of the part's audio |
| a number | seconds (avoid: breaks when the voice changes) |

```json
"anchors": {
  "sixteen":   { "slide": 1, "en": "sixteen", "fr": "seize" },
  "threeCuts": { "slide": 1, "en": "three#1", "fr": "trois#1" },
  "two":       { "slide": 4, "en": "two plus", "fr": "deux plus" },
  "edge":      { "slide": 3, "en": "edge", "fr": "arête", "edge": "end" }
}
```
- A word matches when it **starts with** the anchor (case and accents ignored; `l'équilibre` matches `équilibre`).
- `"three#1"` = the second "three" of that slide (counting from 0). Several words = consecutive words (`"two plus"`).
- `"edge": "end"` anchors the end of the word instead of its start; `"shift": 0.3` adds seconds.
- Anchors are searched only inside their slide. A missing word is an **error** in the checker, with the slide's
  words listed, so fix the anchor rather than guessing.
- Pick words that are **said when the thing should happen**: the noun or number that the picture shows.

## Graph, poses, splits, cameras
```json
"graph":  { "nodes": ["A","B","C","D","E"], "edges": [["A","B",5], ["A","C",1]], "groups": 2, "cap": 3 },
"poses":  { "base": { "A": [280,230], "B": [553,195] }, "split": { } },
"splits": { "good": "ABC|DE" },
"cameras": { "wires": [416, 262, 540] },
"divider": { "x": 570 }, "chip": { "x": 175, "y": 120, "w": 610, "h": 395 },
"thumbPose": "base", "freePose": "base", "goodCut": 3, "badCut": 9,
"widgets": { "counter": { "x": 81, "y": 68 }, "balance": { "x": 77, "y": 26 } }
```
- `splits` gives optional names (literal split strings work everywhere too). A camera is `[centre x, centre y, width]`;
  its height is width × 9/16. JSON has no comments: keep notes in the part's README.
- `cap` defaults to ceil(nodes / groups). A split is **legal** when every node is placed and each group has 1..cap nodes.
- A split string lists groups separated by `|` (`"ABC|DE"`, `"ABCDE"` = one group, `"none"` = nothing placed).
  Multi-letter names: separate with commas (`"n1,n2|n3"`).
- Colours never depend on group numbers: the group holding the alphabetically first node is blue, then green,
  amber, rose (same rule as the lab and its figures).
- Keep every pose 30 px inside the stage (the builder refuses otherwise). Leave the top 25 % free for headlines
  and the right 20 % for the counter or balance when they show. For a two-side split, put group 0 left of the divider.
- Camera shots are clamped to the stage; width 520–600 is a gentle zoom.

## Timeline: what changes, on which word
```json
"initial": { "pose": "base", "split": "none", "camera": "full", "shape": "node", "wires": false, "dim": 1 },
"timeline": [
  { "at": "@first",   "pose": "split", "split": "ABC|DE" },
  { "at": "slide:2",  "shape": "cell", "wires": true },
  { "at": "@many",    "camera": "wires" },
  { "at": "@several", "dim": 0.12 }
]
```
| Key | Values | Move time |
|---|---|---|
| `pose` | a pose name: nodes glide to it | 1.1 s |
| `split` | split string or name: colours change, the counter counts to the new cut | 1.2 s (count) |
| `camera` | shot name or `"full"` | 1.3 s |
| `shape` | `"cell"` (chip rectangles) or `"node"` (dots) | 0.9 s |
| `wires` | `true`: each edge drawn as w copper wires; `false`: one line | 1.0 s |
| `dim` | graph opacity (0.12 when a card covers it) | 0.6 s |

A new key starts from wherever the previous move had got to, so motion never jumps. But two keys of one track
closer than its move time make a rushed move; the checker warns. Fix: add a pause after the sentence
(`pauses`) or anchor the second key to a later word.

## Show windows (things on for a while)
```json
"show": [
  { "show": "cut", "from": "@cut", "to": "@need" },
  { "show": "heavy", "from": "@heaviest", "to": "slide:4", "edges": ["A-B", "D-E"] },
  { "show": "labels", "from": "@five", "to": "end", "stagger": 0.3 }
]
```
`weights` (edge numbers), `labels` (node letters; if any `labels` window exists, letters show only inside one;
`stagger` pops them one by one), `chip` (chip outline), `divider` (dashed line + tinted halves), `cut` (cut edges
red and dashed), `heavy` / `pulse` / `flash` (edge highlights; `edges` lists them, several windows can overlap),
`counter` (live cutsize), `balance` (bars per group), `cap` (the max line on the bars).

## Overlays (text on the stage)
Each: `{ "from", "to", "x", "y", "type", ... }`. Text fields are `{ "en": "...", "fr": "..." }`.

| type | fields | use |
|---|---|---|
| `headline` | `text`, `sub`, `size` (cqw, default 4.3) | the idea of the moment, top-left |
| `term` | `text` (the term, capitalised), `sub` (plain definition) | first time a word appears |
| `chip` | `text` | short labels that pile up (method names) |
| `tag` | `text` | one fact next to the picture |
| `tags` | `items: [{ text, at? }]` | 2–3 facts appearing one by one |
| `label` | `text`, `color` 0–3 | coloured caption over a group ("Team 1") |
| `vocab` | `items: [{ k, text, at }]` | a growing glossary |
| `eq` | `text` | an equation built term by term |
| `stamp` | `text` | a verdict ("useless") |
| `bigq` | `text` | a big "?" with a sentence; dim the graph |
| `compare` | `rows: [{ tone: "bad"/"good", label, value, note }]` | two outcomes side by side; dim the graph |
| `thumbs` | `items: [{ split, best?, bestLabel? }]` | small graphs with their cuts (computed) |
| `question` | (uses `question`) | the pause-and-guess card |
| `html` | `html` | escape hatch; avoid |

Inline markup inside any text:
- `{piece@name}` makes `piece` appear when anchor `name` is said (also `{piece@slide:3}`).
- `**accent**` gives blue bold, `!!red!!` gives red, and `##5##` marks a number.

## Question, bench, chapters, claims, pauses
```json
"question": { "at": "slide:6:end+0.5", "text": {...}, "hint": {...},
              "options": [ { "label": {...}, "reply": {...} } ] },
"bench": { "deal": true, "seed": 3 },
"chapters": [ { "at": "start", "title": {...} } ],
"claims": [ { "split": "ACE|BD", "cut": 16, "legal": true }, { "deal": 3, "split": "ACE|BD" } ],
"pausing": { "between": 0.55, "scene": 0.9, "question": 1.3, "tail": 2.0 },
"pauses": [ { "after": "@sixteen", "sec": 1.3 }, { "after": "slide:2:end", "sec": 1.5 } ]
```
- The player **stops at `question.at`** and waits for an answer on the stage, then plays the rest.
- `bench.deal` adds the "deal a random split with seed" box. It uses the course's mulberry32 dealer, only for
  two-group partition labs.
- `claims` are checked against the rules. Put every number the narration or the texts say here.
- `pauses` override the silence after the sentence holding an anchor (see `voice-and-pacing.md`).

Page text: `pageTitle`, `eyebrow`, `title`, `lede`, `note` (all `{en, fr}`).
