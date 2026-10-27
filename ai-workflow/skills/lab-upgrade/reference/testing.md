# Testing the browser lab and the site

Install once: `pip install playwright && python3 -m playwright install chromium`.
Serve the teacher's platform: `python3 -m http.server 8080 --directory platform`
(lab URL `http://127.0.0.1:8080/tools/<tool>/index.html`).

## Patterns that avoid flaky tests
- Use a **tall viewport** (`1400×3000`) and inject `html{scroll-behavior:auto!important}`.
  Otherwise clicks land mid smooth-scroll on the wrong element.
- Click buttons with `page.locator('button:text-is("Check my score")')`, not `text=…`:
  challenge prompts contain button names, so `text=` clicks the prompt.
- Click canvas nodes by coordinates computed from the model's layout, after
  `fitHiDpiCanvas` (read `canvas.getBoundingClientRect()` and scale by the layout box).
- Test the pure model in Node first (`node --input-type=module -e "import …"`); it's faster
  and catches most bugs without a browser.
- Collect `page.on("console")` errors and `page.on("requestfailed")`; fail on any.

## What to prove for each challenge
1. **Positive:** perform the learner's actions → the challenge shows PASS.
2. **Negative:** a wrong value, or the right state reached through a "(study)" reveal → no PASS.
Print a table `challenge | positive | negative` and require all `ok`.

## Skeleton (Python)

```python
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8080/tools/<tool>/index.html"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1400, "height": 3000})
    errors = []
    pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
    pg.goto(URL)
    pg.add_style_tag(content="html{scroll-behavior:auto!important}")
    def run_challenge(cid, actions):
        pg.select_option("#lab-chal-sel", cid)
        pg.click("#lab-chal-start")
        actions(pg)                      # the learner's clicks and typing
        pg.click("#lab-chal-check")
        return pg.inner_text("#lab-status")   # "PASS" or "Not yet …" (translated in FR)
    # assert run_challenge("edge-top3", solve_edge_top3) == "PASS"
    # assert run_challenge("edge-top3", wrong_edge_top3) != "PASS"
    assert not errors, errors
    b.close()
```

Note: the test Chromium can't play H.264 video. A video that doesn't play there is a
limitation of the test browser; check that the `<video>` source returns 200 instead.

## Lab 03 standard (copy it)
- **Model vs checker** (Node, no browser): every random seed 0–15, greedy and every grow on every example graph give
  the checker's goldens; the test must fail when the PRNG warm-up is removed (prove it once).
- **Negative cases per challenge**: page load; a wrong split; the matching start button; an edit after a start
  (flip a node twice so the split looks the same); the study reveal. Plus the "reset workspace" preset.
- **Colour cases**: sample the pixel inside each node; the group holding the first node name must be blue.
- Lab 03 counts: 13 positive + 52 negative + 5 colour = 70 cases, run in EN and FR on the built site.
