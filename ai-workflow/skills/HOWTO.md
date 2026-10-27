# Upgrading the next lab with Claude Code: setup and run

This zip holds two skills:
- `lab-upgrade/` (version 3): the six stages, from audit to the bilingual site with video parts.
- `lesson-animator/`: animated, interactive lessons that play next to the video parts (optional Stage 7).

`lab-upgrade/PLAYBOOK.md` tells the whole Lab 03 story; read it once.

## 1. Install (once)
```bash
unzip ~/Downloads/eda-skills.zip -d /tmp/eda-skills
mkdir -p ~/.claude/skills
rm -rf ~/.claude/skills/lab-upgrade ~/.claude/skills/lesson-animator
cp -r /tmp/eda-skills/lab-upgrade /tmp/eda-skills/lesson-animator ~/.claude/skills/
mkdir -p ~/Documents/3A/SJTU/VLSI_Mort/test2/tools
cp ~/.claude/skills/lab-upgrade/scripts/stage_tokens.py ~/Documents/3A/SJTU/VLSI_Mort/test2/tools/
pip install playwright pillow edge-tts markdown && python3 -m playwright install chromium
```
In VS Code's Claude panel, type `/lab-` and `/lesson-`: both skills should be suggested.

## 2. A clean clone for the new lab (no branch, no stash)
```bash
cd ~/Documents/3A/SJTU/VLSI_Mort/test2
git clone --depth 1 --filter=blob:none --sparse https://github.com/yongfu-li/eda-learning.git eda-learning-labNN
cd eda-learning-labNN
git sparse-checkout set .cursor/skills/module-slides courses/<course>/common courses/<course>/scripts \
    courses/<course>/<module> platform/assets platform/tools/<tool> platform/courses/<course>/labs/<tool>
git status --short   # nothing
```
If GitHub crawls (25 KB/s), ask Claude in the chat to make this clone and send it as a zip.
Find `<module>` and `<tool>` from the lab's page on the website (its URL ends in `labs/<tool>/`; the page says "Lab NN").

## 3. Run the stages
Open `eda-learning-labNN` in VS Code. For each stage: new Claude conversation, `/add-dir ~/Documents/3A/SJTU/VLSI_Mort/test2`,
pick the model, paste the stage prompt from `~/.claude/skills/lab-upgrade/prompts.md`, review, fix in the same
conversation, note `/usage`.

| Stage | Model | You check before moving on |
|---|---|---|
| 1 Audit | Sonnet | UPGRADE_NOTES.md (bring it to the chat for a second opinion) |
| 2 Content | Sonnet | the checker prints all PASS |
| 3 Script + figures | Opus | `slides.pdf` page by page; lint 0 problems; parts in the notes |
| 4 Browser lab | Opus | play the challenges yourself; tests all ok |
| 5 Site + French | Sonnet | `python3 -m http.server 8000 --directory docs`, EN and FR |
| 6 Final | Sonnet | `git status --short` only the two lab folders; videos 7–8 min |

Long media runs (`narrate_clips.sh`, `make_fr_media.py`): Claude gives you the commands; run them in a terminal and
watch the audio files appear (`reference/workflow.md`). Keep the VPN on, the laptop awake.

## 4. Publish
Create the empty GitHub repo, then in the site repo: `git remote add origin ...`, `git add -A`, `git commit`,
`git push -u origin main`; Settings → Pages → main, `/docs`. Watch one part per language at 1.5×.

## 5. Hand-off to the teacher
The site link and `WHAT_CHANGED.md` (with its findings for the teacher).
Optional, for yourself: tokens per conversation with
`python3 ~/Documents/3A/SJTU/VLSI_Mort/test2/tools/stage_tokens.py --match labNN`.

## Rules the skills enforce (remind Claude if it drifts)
- Only the module folder and the tool folder change in the teacher clone; never `common/` or `platform/assets`.
- No branch, commit or push in the teacher clone; you push only your site repo.
- Every number comes from running code.
- Never run the course's transcript generators on the module.
