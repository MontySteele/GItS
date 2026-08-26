---
name: sitting
description: Take a registered experiment's run - verify the pinned world stamp, run the packet's exact command, write the provenance header, grade blind slot by slot, update the registers, gate and commit. Use for any pre-registered cell in review/active/.
---

# Sitting — running a registered experiment

A sitting is not "run the sim and look". It is a countersigned packet executed
literally. Commands run from the repo root.

1. **Refuse to start unless the packet is ready** — its prediction slate filled
   and its countersign line signed, each as its own commit, both BEFORE this
   run. Predictions are filled against the settled world, never the result.

2. **World check. The run does not start until this prints the pinned stamp.**

   ```sh
   PYTHONPATH=. python -c "from tier05 import cells; v=cells.CANONICAL.versions; print('RT{RT}/D{D}/P{P}/C{C}'.format(**v))"
   ```

   Compare with the stamp in the packet header / §2 / §4 (e.g.
   `RT12/D17/P10/C19`). **Mismatch is tripwire S1: STOP, do not run.**
   Re-stamp the packet against the live world and re-register — a tripwire
   naming a superseded world is a citation defect, not a finding.

3. **Prove the tree is green first**, so a red suite cannot be blamed on the run:
   `python -m pytest tier0/tests tier05/tests -q -n auto --dist loadscope`

4. **Run the packet's exact command, capturing stdout beside the packet.** `n`,
   seed, arms and route come from the packet; override nothing, and **never
   `--smoke`** for a real run (a smoke banner is non-quotable).

   ```sh
   PYTHONPATH=. python -m tier05.<instrument> <registered args> | tee review/active/<cell>-results-<YYYY-MM-DD>.txt
   ```

5. **Provenance header**, above the UNEDITED stdout, never a rewrite of it:
   registration path + §§; countersign; run date; world (and "verified by step
   2"); commit + branch; instrument path; `n` / seed; arms; wall clock and exit
   code; every deviation from the packet's literal text declared (e.g. `python`
   for `python3`); stderr at the foot; and the line
   **THE GRADE IS NOT IN THIS FILE**.

6. **Grade blind, slot by slot, in the packet's prescribed order.** Vocabulary:
   **PREDICTED / MISS / SPLIT**. A SPLIT names which clause failed and never
   rounds to the agreeing half. No slot's grade depends on another's; every
   slot is graded before any narrative. Write the grade **beside** the
   prediction section, never over it (R101b), and quote percentages rather than
   the instrument's own hardcoded "IN BAND" word.

7. **Registers, after the grade and only after it.** `EXPERIMENTS.md` pointer →
   `RUN AND GRADED <date>` plus the tally and whether the packet stays in HEAD;
   `QUEUE.md` row rewritten in place (measurement half done, design call left
   standing); `BACKLOG.md` only if a gated row unblocks. **`STATE.md` is not
   touched by a grade commit** — a grade moves no stamp.

8. **Gate, then commit.** `python -m pytest tier0/tests tier05/tests -q -n auto
   --dist loadscope` and `python tools/run_lints.py --lane ci`. The grade is its
   own commit, carrying the verbatim run command, the world-check output, the
   tally, and any deviation.
