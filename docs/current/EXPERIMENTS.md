# EXPERIMENTS

Standing measurement law, plus pointers to the active registrations. The
registration packets themselves live under `review/active/` — one home, not two.

## Measurement law

### Stamp law
- **Every published number is world-stamped, and worlds are not comparable.**
  `RUNTEMPLATE`, `DRAFTER_VERSION`, and `POLICY` bumps archive their
  predecessors; check the stamp before quoting anything (R68).
- Run experiments through a `Cell` (`tier05/cells.py`) — it carries the stamp a
  report needs to be citable. **A report without a stamp is not citable.**
- **Frozen calibration surfaces must not be retuned.** The encounter battery,
  the pilots' `block: 1.2`, and `understudy/policy_v0.py` are frozen; editing one
  retroactively moves every archived number measured against it.

### Instrument visibility — one variable per window (D4)
- A prediction must **name the instrument that can SEE the changed object**, and
  confirm it can. The sim is one-seat; a C#-only change never gets a sim
  prediction; `support` is never linted because no instrument sees it.
- Change one variable per measurement window. The drafter/constants version is
  part of the variable set — a scorer change **is** a version bump in the same
  edit (`DRAFTER_VERSION` in `tier0/constants.py`).

### Versioning
- The run-cell stamp is `RT/D/P/C`, read live via `tier05/cells.py`:
  `RUNTEMPLATE_VERSION`, `DRAFTER_VERSION`, `CONSTANTS_VERSION` in
  `tier0/constants.py`, and `POLICY_VERSION` in `tier05/draft.py`. The
  scorecard's `A6_INSTRUMENT_VERSION` lives separately in `tier0/harness/axes.py`
  and is not part of the run-cell stamp. v1 and v2 A6 numbers are discontinuous
  and must never be compared unlabeled.

### Pre-registration + blind grading
- A measurement that a playtest will grade is **pre-registered from design
  intent**, with its contamination stated, and **never revised against the
  playtest that grades it** (D5 — the Kokomi stability band, which lands DARK,
  `band = None`).
- Pre-registration drafts are a [USER]-gated class; the grade goes in blind.

## Active registrations (pointers — packets live in `review/active/`)
- **payoff-reach re-registration** — the `RARITY_ODDS` fence. Q18 is
  countersigned; the open step is authoring the kickoff predictions (`Q-C` in
  `docs/current/QUEUE.md`) *before* any number is read →
  `review/active/payoff-reach-reregistration.md`.
- **EB-17p force-first-copy paired winrate** — **COUNTERSIGNED 2026-08-10**,
  not launched. The engineering prerequisites (§10) have landed and the
  `force_cards` seam is pinned; no seed in the registered range has been run.
  Two things still gate the sweep: the §7 cost ceiling, and §8's predictions
  as their own commit →
  `review/active/eb17p-registration-draft-2026-08-08.md`.
- **Kokomi stability band (D5)** — no band is declared yet (the declaration
  is QUEUE `S4-G6`; until it lands, the band rides DARK, `band = None`); its
  grading playtest is `docs/current/playtest/kokomi-playtest-protocol.md`
  (unrun; Answers block still blank).

New registrations add a pointer here and land their packet under
`review/active/`; when a registration is graded and closed, both leave HEAD.
