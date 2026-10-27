# How this lab was built with AI

This folder documents how Lab 03 (initial bipartition, partitioning course) was upgraded with AI assistance, and
holds the two reusable skills that came out of it, so the same work can be repeated on another lab.

- Student: Capeur (VLSI course, SJTU). Teacher's course: [yongfu-li/eda-learning](https://github.com/yongfu-li/eda-learning).
- Result: https://capeur.github.io/eda-partitioning-module-lab3/ (English) and `/fr/` (French).
- AI used: **Claude** in two ways.
  - **Claude chat** (claude.ai, with a cloud workspace): planning, reviews, checking numbers by running the teacher's
    code, prototypes, writing the skills.
  - **Claude Code** (VS Code extension, on the student's laptop): ran the upgrade stage by stage with the
    `lab-upgrade` skill.
- Every change was reviewed and applied by the student; nothing was pushed to the teacher's repo.

## 1. Timeline

| Date | What happened |
|---|---|
| 2026-10-20 | Clustering Lab 02 (affinity metrics) upgraded in the chat: new content, golden checker, interactive lab, beginner script, bilingual site ([eda-clustering-module-lab2](https://capeur.github.io/eda-clustering-module-lab2/)). |
| 2026-10-27 morning | To make the work repeatable on other labs, the chat turned the Lab 02 work into a skill, `lab-upgrade`: six stages, one conversation each, notes carried in `UPGRADE_NOTES.md`. |
| 2026-10-27, 13:00 | Target corrected from partitioning Lab 02 to **Lab 03**. Skill retargeted. A clean, light clone of the teacher's repo was made in the cloud and handed over as a zip, because GitHub ran at 25 KB/s from China. |
| 13:40–16:35 | **Stages 1–6 in Claude Code**: audit, content and checker, beginner script and figures, browser lab, bilingual site, final check. The student reviewed each stage in the chat before the next one. |
| 16:45–17:05 | Site pushed. Student feedback: the video is too long and repeats itself. |
| 17:05–18:15 | **Polish pass**: repetition removed, script cut into 5 parts with hooks and "pause and guess" questions, more pictures, video parts, speed buttons. Pushed. |
| 18:25–19:05 | Student: the video should be more dynamic. The chat built an **animated lesson prototype** for Part 1, drawn live in the browser in time with the voice. Version 2 added natural pauses and smooth transitions after the student's feedback ("way better"). |
| 19:10–19:40 | Both skills written and tested: `lab-upgrade` v3, and a new `lesson-animator`. Playbook and this summary written. |

## 2. Who decided what

| Decision | By | Why |
|---|---|---|
| Audience = high-school level; videos under 10 minutes | Student | the site is for learners without background |
| Edit only the lab's module and tool folders; never commit to the teacher's repo; publish in a separate repo | Student | keep the teacher's repo clean and reviewable |
| One stage per conversation, a smaller model (Sonnet) for audit, content, site and hand-off, a stronger one (Opus) for the script and the browser lab | Chat proposal, student agreed | short conversations stay focused; the strongest model where writing and design matter |
| Random start = the course's `mulberry32` + Fisher–Yates, the same in Python and JavaScript | Proposed by Claude Code in Stage 1, checked in the chat, approved by the student | the teacher's shuffle depended on node order and could not be reproduced in Python |
| Greedy with an exact written rule and a size limit; the old greedy kept as a counter-example | Same | the old one had an unwritten tie-break and could give an illegal 5\|1 split |
| 5 parts, hooks, "pause and guess", each idea said once | Student request, implemented by Claude Code | the first video was too long and repetitive |
| Speed buttons 1× to 2×; video parts that play one after another | Student | |
| Animated lessons sit **next to** the video parts, not instead of them | Student | keep the teacher's video pipeline untouched |

## 3. Problems met and how they were solved

| Problem | Fix |
|---|---|
| The teacher's numbers disagreed across files (seed 7 described wrongly; a grow step described wrongly) | Every number now comes from a checker script; the shared-code bugs are listed for the teacher in `WHAT_CHANGED.md` |
| `git pull` blocked by uncommitted Lab 02 work | A separate light clone per lab |
| GitHub and the voice service slow or stuck from China | Mullvad server change; long voice and video runs done by the student in a terminal; stalls show as 0 % CPU with no new file |
| Figure scripts first left in Claude's temporary folder | Moved to `tools/lab03-figures/`; the skill now forbids temporary-only files |
| French subtitles showed a lone "?" | Fixed in the subtitle splitter |
| Encoded video parts would have been pushed twice | `.cache/` added to `.gitignore` |
| The voice sounded forced, animations skipped scenes (prototype v1) | Pauses between sentences, chosen per moment; motion that starts from where the previous move had got to |

## 4. Results

- Content: golden checker (23 checks), 3 new example graphs, 8-question quiz, rewritten examples, checklist and README.
- Script: 1,182 words in English, 1,292 in French, 30 slides, 5 parts of 1:19 to 1:42 each; videos of 7:26 (EN) and 7:55 (FR).
- Browser lab: 10 challenges that check what the learner builds; 37 model-vs-checker checks and 70 browser test cases, in both languages.
- Site: English and French, video parts with subtitles, speed buttons, walkthrough, slides, downloads; 169 automated checks, no external requests.
- Findings for the teacher: see `WHAT_CHANGED.md` at the repo root (5 items in the shared code and pages).

## 5. Reusing this on another lab

`skills/` holds both skills (install them into `~/.claude/skills/`, see `skills/HOWTO.md`):
- **`lab-upgrade`** (version 3): the stage-by-stage method, copy-paste prompts, the environment guide, and
  `PLAYBOOK.md`, the full Lab 03 story with a checklist for the next lab.
- **`lesson-animator`**: animated lessons drawn live in the browser in time with the narration, in both languages
  from one storyboard, with an automatic checker and an optional MP4 export. Example: Lab 03 Part 1.

## 6. Limits and what is not done yet

- Animated lessons: only Part 1 exists, as a prototype; Parts 2–5 are still to be storyboarded.
- The skill's voice script was tested only with a stand-in voice (the voice service was blocked in the cloud
  workspace); its first real run should be checked.
- Video playback and "next part plays by itself" must be checked in a real browser (Firefox or Chrome); the
  automated test browser cannot play H.264.
