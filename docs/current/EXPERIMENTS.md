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
- **EB-17p force-first-copy paired winrate** — **RUN AND GRADED 2026-08-10.**
  Countersigned complete (`N` = 2400 pairs, Strike filler, 4h ceiling, §6.1b
  co-primary), §8 predictions committed ahead of the run (`eb67706`), graded
  blind in §13: **3 PREDICTED / 1 SPLIT / 1 MISS** (`borrowed_brilliance`, wrong
  sign). §11.1's disclosed 12-pair read was **ruled immaterial (R173)** and the
  registered range ran unchanged. **The measurement is closed; what stays open is
  a design act** — §8.1's redesign trigger fired for `borrowed_brilliance` and
  `elemental_ecstasy`, now QUEUE `M17`, and it must be read with §13.8's
  instrument caveat →
  `review/active/eb17p-registration-draft-2026-08-08.md` §13;
  `review/active/eb17p-results-2026-08-10.txt`.
- **Shop companion channel re-run (`S4-G10` / `C9`)** — **DRAFT, awaiting
  [USER] countersign at QUEUE `M14`, unrun.** The packet is in HEAD as of the
  `shop-floor-2026-08-10` merge. The channel's world moved ([USER] restored slot 2's
  Uncommon floor, `CONSTANTS_VERSION` 9) and the instrument's two defects were
  repaired, both on 2026-08-10; the packet asks to re-measure in the new world.
  Predictions are explicit [USER] slots and are still blank →
  `review/active/shop-rerun-registration-2026-08-10.md`.
- **The regret margins (`M13` / `EB-72`)** — **DRAFT, awaiting [USER]
  countersign at QUEUE `M13`, unrun.** `ROUTE_REGRET_MARGIN` and its drafter
  twin (`draft.DRAFT_REGRET_MARGIN`, the `+1.0`) have no recorded derivation;
  R164 ruled that the measurement is pre-registered and that **`+1.0` is not
  ratified**. `EB-72` leg (1) landed the distribution printer
  (`tools/regret_distribution.py`) that made a registration possible at all —
  the margin-free gap distribution for both numbers, on a read-only pass over
  finished runs, with no stamp movement. The packet's §7 predictions are
  explicit [USER] slots and are still blank, and its §6 lays out four
  derivation options at equal weight — including the upper-percentile
  derivation, whose circularity is stated there rather than assumed away →
  `review/active/regret-margin-registration-2026-08-12.md`.
- **Kokomi stability band (D5)** — no band is declared yet (the declaration
  is QUEUE `S4-G6`; until it lands, the band rides DARK, `band = None`); its
  grading playtest is `docs/current/playtest/kokomi-playtest-protocol.md`
  (unrun; Answers block still blank).

New registrations add a pointer here and land their packet under
`review/active/`; when a registration is graded and closed, both leave HEAD.
