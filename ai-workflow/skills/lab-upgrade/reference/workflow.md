# Workflow and environment (what worked for Lab 03)

## Folders (student's machine, Ubuntu)
```
~/Documents/3A/SJTU/VLSI_Mort/test2/
  eda-learning/                    old full clone (holds the clustering Lab 02 changes; keep it: Lab 03's
                                   patch_walkthrough.py copies the walkthrough viewer from it)
  eda-learning-labNN/              one light clone per lab, on main, nothing committed
  eda-clustering-module-lab2/      site repo, Lab 02
  eda-partitioning-module-lab3/    site repo, Lab 03 = template for the next labs
  tools/                           stage_tokens.py, labNN-figures/, labNN-notes/ (outside every repo)
```

## A clean teacher clone for each lab
Do not branch or stash in an old clone: make a new light clone next to it.
```bash
cd ~/Documents/3A/SJTU/VLSI_Mort/test2
git clone --depth 1 --filter=blob:none --sparse https://github.com/yongfu-li/eda-learning.git eda-learning-labNN
cd eda-learning-labNN
git sparse-checkout set .cursor/skills/module-slides courses/<course>/common courses/<course>/scripts \
    courses/<course>/<module> platform/assets platform/tools/<tool> platform/courses/<course>/labs/<tool>
```
Whole `platform/` or whole `courses/<course>` pulls every module's video: avoid. From China, GitHub can run at
25 KB/s: if it does, ask Claude in the chat to make this sparse clone in its cloud workspace and hand it over as a
zip (about 22 MB for Lab 03, git history included, `git status` clean).

## Network from mainland China
- A VPN is needed for GitHub and for edge-tts (speech.platform.bing.com). The student uses **Mullvad (WireGuard)**:
  it routes everything, SSH included (`ip -brief link` shows `wg0-mullvad`), so no proxy settings are needed.
- Slow? Switch Mullvad server (Tokyo, Osaka, Hong Kong, Singapore) and measure:
  `curl -o /dev/null -w "%{speed_download}\n" https://speed.cloudflare.com/__down?bytes=10000000`.
  A git push is a single connection and can stay slow (50 KB/s) even when a speed test says 10 Mb/s.
- A run that shows **0 % CPU and no new file for minutes** is stuck on the network:
  `ps aux | grep -E "make_fr_media|edge-tts|ffmpeg|soffice" | grep -v grep` then kill it by pid, fix the VPN, rerun.
- Watch media runs with: `watch -n 30 'ls -lt --time-style=+%H:%M:%S <module>/audio/*.mp3 | head -4'`.
- Google Fonts is blocked or slow: the sites self-host fonts (`site_src/fonts`).

## Claude Code in VS Code
- Open the **clone** as the VS Code folder. In each new conversation, first type
  `/add-dir ~/Documents/3A/SJTU/VLSI_Mort/test2` so Claude can read the template site and write the new site repo.
- One stage per conversation (a new conversation = `/clear`). Same conversation to fix that stage's results.
- Permission modes: "accept edits automatically, ask before commands" is a good default. The automatic mode's online
  checker fails when the network drops (10 failures end the session): switch to asking mode while the VPN is unstable.
- Claude's commands stop after 10 minutes in the foreground, and background jobs started with `nohup … &` do not
  report back. So for anything long, **Claude gives the commands and the user runs them** in a terminal (rule 7).
- If the user must leave mid-run: press Esc, ask Claude to append "what is finished, what still has to run" to the
  notes, close the laptop. Resume in the same conversation ("I'm back. Check what finished and continue.").

## Models (Lab 03 experience)
| Stage | Model | Notes |
|---|---|---|
| 1 audit | Sonnet | found more problems than expected (seed bugs, order-dependent shuffle) |
| 2 content | Sonnet | numbers are checked by the checker, so mistakes show as FAIL |
| 3 script + figures | Opus | writing for a high-school reader is the hardest part |
| 4 browser lab | Opus | challenge design + 70-case tests |
| 5 site + French | Sonnet | Opus only if it struggles |
| 6 final | Sonnet | |

## Measuring tokens (optional)
`/usage` shows the plan's limits (subscription). For exact tokens per conversation:
`python3 ~/Documents/3A/SJTU/VLSI_Mort/test2/tools/stage_tokens.py --match labNN --csv labNN-tokens.csv`
(reads `~/.claude/projects/*/*.jsonl`; `cache_read` is the conversation being re-read and is the biggest number).

## Python environment
The pipeline needs python-pptx, pyyaml, edge-tts, markdown, playwright, pillow, LibreOffice, ffmpeg, poppler-utils.
If the system python lacks `markdown`: `python3 -m venv --system-site-packages ~/eda-venv && ~/eda-venv/bin/pip install markdown edge-tts playwright pillow`.
Set `PYTHONDONTWRITEBYTECODE=1` so no `__pycache__` lands in the clone.
