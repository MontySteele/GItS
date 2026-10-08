---
name: sitting
description: Take a registered SIM experiment's run - verify the pinned world stamp, run the packet's exact command, write the provenance header, grade blind slot by slot, gate and commit. Use only for a pre-registered sim cell; it does not apply to kit balance, which is measured on the real game.
---

# Sitting — running a registered sim experiment

**Scope: sim-law registrations only, not kit balance.** A kit at Balance is
measured on the real game: seat suites on the base-five seeds and the fight
telemetry, each change graded by its one-line prediction
(`docs/current/EXPERIMENTS.md`, "Kit balance is measured on the real game",
ruled 2026-10-05; `operations/stage-gate.md`). Slates and blind grading below
do not gate kit balance. Use this skill only when a sim cell has been
pre-registered. Commands run from the repo root.

1. **Refuse to start unless the packet is ready** — its prediction slate
   committed in its own commit BEFORE any seed runs (the pre-registration is
   the commit-before-run). Predictions are filled against the settled world,
   never the result.

2. **World check. The run does not start until this prints the pinned stamp.**

   ```sh
   PYTHONPATH=. python -c "from tier05 import cells; v=cells.CANONICAL.versions; print('RT{RT}/D{D}/P{P}/C{C}'.format(**v))"
   ```

   Compare with the stamp in the packet. **On a mismatch, stop.** Re-draft only
   the slots the move affects, disclose the stamp diff in the packet, then run
   against the live world.

3. **Prove the tree is green first**, so a red suite cannot be blamed on the run:
   `python tools/gates.py --full`.

4. **Run the packet's exact command, capturing stdout beside the packet.** `n`,
   seed and route come from the packet; override nothing, and **never
   `--smoke`** for a real run (a smoke banner is non-quotable).

   ```sh
   PYTHONPATH=. python -m tier05.<instrument> <registered args> | tee review/active/<cell>-results-<YYYY-MM-DD>.txt
   ```

5. **Provenance header**, above the UNEDITED stdout, never a rewrite of it:
   registration path and sections; run date; world (and "verified by step 2");
   commit and branch; instrument path; `n` / seed; wall clock and exit code;
   every deviation from the packet's literal text declared (e.g. `python` for
   `python3`); stderr at the foot; and the line **THE GRADE IS NOT IN THIS
   FILE**.

6. **Grade blind, slot by slot, in the packet's order.** Vocabulary:
   **PREDICTED / MISS / SPLIT**. A SPLIT names which clause failed and never
   rounds to the agreeing half. Every slot is graded before any narrative.
   Write the grade **beside** the prediction, never over it, and quote
   percentages rather than the instrument's own "IN BAND" word.

7. **Record, after the grade.** The packet moves to `review/records/` once run.
   A design call the grade feeds goes to [USER] as a numbered pick
   (`QUEUE.md`); a `BACKLOG.md` line only if a gated item unblocks.
   **`STATE.md` is not touched by a grade commit** — a grade moves no stamp.

8. **Gate, then commit.** `python tools/gates.py --full`. The grade is its own
   commit, carrying the verbatim run command, the world-check output, the
   tally, and any deviation.
