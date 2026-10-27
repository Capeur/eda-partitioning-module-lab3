# Prompts: one Claude Code conversation per stage

Replace the values in angle brackets once (course, module, tool, lab number NN, site repo name). In every new
conversation, type first: `/add-dir ~/Documents/3A/SJTU/VLSI_Mort/test2`. Start each conversation in the lab's
teacher clone (VS Code folder `eda-learning-labNN`). Between stages: `/usage` (note it), new conversation.

## Stage 1: Audit (Sonnet)
```
/lab-upgrade Stage 1 for course <course>, module <module>, tool platform/tools/<tool>, Lab <NN>,
teacher clone = this folder (eda-learning-lab<NN>, on main, no branch), site repo ../eda-<short>-module-lab<NN>.
Run the audit and lint scripts, read only the files the skill names, cross-check every golden against the
platform's own functions (run them with node), note what common/ lacks and every vague rule, and write
UPGRADE_NOTES.md with the gaps, 2-4 concepts, a plan, and open questions each with a recommended answer.
Don't edit anything else.
```
Bring the notes to the chat for review if you like, answer the open questions in the same conversation, then
"approved, append the decisions to UPGRADE_NOTES.md".

## Stage 2: Content and goldens (Sonnet)
```
/lab-upgrade Stage 2. Read UPGRADE_NOTES.md first. Write the checker (exact written rules, tie-breaks,
caps; one portable PRNG shared with JS if anything is random, with a --vs-node check), extra example graphs,
EXAMPLES.md, quiz, checklist, README and _demo.sh. Every number must come from the checker. Prove that a
wrong --impl fails.
```
Then run the checker yourself: all PASS.

## Stage 3: Script in parts and figures (Opus)
```
/lab-upgrade Stage 3. Read UPGRADE_NOTES.md first. Write transcript.md for a high-school student, already
in 4-6 parts of 1-2 minutes (hook at the start, "Pause and guess" at the end, answered by the next part),
following the repetition rules and 1,100-1,300 spoken words. Make the figures and step figures with scripts
kept in ../tools/lab<NN>-figures (run_all.sh, facts.py, README, a --lang fr option). Redraw the walkthrough
frames. Lint, build the PDF and look at every page. Write the part boundaries (slides and PDF pages) in the
notes. No audio yet.
```
Open `slides.pdf` yourself; ask for fixes in the same conversation.

## Stage 4: Browser lab (Opus)
```
/lab-upgrade Stage 4. Read UPGRADE_NOTES.md first. Rebuild platform/tools/<tool> as model + UI with 8-10
challenges that check what the learner builds (nothing passes on load, from a preset, from the reveal, or
after editing a method's result), colours as in the figures, a model-vs-checker test and a Playwright test
with positive, negative and colour cases. Recapture the lab screenshot and rebuild the deck.
```
Try the lab yourself: `python3 -m http.server 8080 --directory platform`, then `http://localhost:8080/tools/<tool>/`.

## Stage 5: Site in EN and FR (Sonnet)
```
/lab-upgrade Stage 5. Read UPGRADE_NOTES.md first. Create ../eda-<short>-module-lab<NN> from the template
../eda-partitioning-module-lab3 (reference/site-template.md: fresh git init, change every lab-specific place,
PARTS from the notes). Write the French transcript, EXAMPLES, quiz, lab strings, walkthrough captions, and
French figures and frames. When the French media must be built, give me the exact commands to run in my own
terminal and wait. Then build and run both tests; report both language lines. Don't push.
```

## Stage 6: Final (Sonnet)
```
/lab-upgrade Stage 6. Read UPGRADE_NOTES.md first. Give me the exact narrate_clips.sh command for the
English media and wait until I say it finished. Then check the outputs, rebuild the site, rerun both tests,
check git status in the clone, write WHAT_CHANGED.md with the findings for the teacher, copy UPGRADE_NOTES.md
to ../tools/lab<NN>-notes/ and delete it from the module. Don't commit or push.
```
Then you watch one part per language at 1.5× in Firefox or Chrome, commit and push the site repo, and turn on Pages.

## Stage 7 (optional): animated lessons
Use the `lesson-animator` skill, one conversation per part (its SKILL.md lists the steps).
