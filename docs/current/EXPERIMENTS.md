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
- **payoff-reach re-registration** — the `RARITY_ODDS` fence. Q18 countersigned
  (R121); **predictions COMMITTED 2026-08-13 (R186)** as the registration's
  `## 6`, before any sprint number was read — step (2) of the countersigned
  execution order is executed and `Q-C` is closed. Committed: the ruled aims
  (R185), Q-A under its observational reading and Q-B under its arithmetic
  reading with direction and threshold, the two-leg instrument, the sample
  plan at the ratified cell (n=600/arm, seed 11, `hunter`, `assigned`,
  realistic), controls C1 and C2, a 4h ceiling and tripwires T1–T4. **UNRUN,
  and it does not run yet:** §6.6's approved P12 is **settle first** — the
  freeze begins only after the open `RT`/`C` window (`M14`'s batch: `EB-70`,
  the `EB-82` conversion, the `EB-85` batch, `EB-69`) lands and a dependency
  re-check passes; if the world moved, §6 is re-stamped before the freeze.
  Owed before the run and named in §6.4/§6.5: the generic reach reader
  (`tier05/exp_payoff_reach.py`) and the `blind` control policy — **both built
  2026-08-13**. Steps (3)–(6) run in order and none reorders →
  `review/active/payoff-reach-reregistration.md` §6.
- **EB-17p force-first-copy paired winrate** — **RUN AND GRADED 2026-08-10.**
  Countersigned complete (`N` = 2400 pairs, Strike filler, 4h ceiling, §6.1b
  co-primary), §8 predictions committed ahead of the run (`eb67706`), graded
  blind in §13: **3 PREDICTED / 1 SPLIT / 1 MISS** (`borrowed_brilliance`, wrong
  sign). §11.1's disclosed 12-pair read was **ruled immaterial (R173)** and the
  registered range ran unchanged. **The measurement is closed.** §8.1's redesign
  trigger fired for `borrowed_brilliance` and `elemental_ecstasy`, and **R180
  (2026-08-12) split the two**: `elemental_ecstasy` goes to redesign;
  `borrowed_brilliance` is **remeasured first**, by re-running the registered
  **five-card** sweep re-registered under `P7` — never a narrowed single-card
  experiment. **That re-registration is now DRAFTED and has its own pointer
  below**; it is a NEW packet beside this one. **R101b: this registration and
  its results file stay unedited** — there is no re-grade of §13 →
  `review/active/eb17p-registration-draft-2026-08-08.md` §13, §13.8;
  `review/active/eb17p-results-2026-08-10.txt`; QUEUE `M17`.
- **Force-first-copy paired winrate, re-registered under `P7` (`M17`)** —
  **DRAFT, awaiting [USER] countersign at QUEUE `M17`, unrun.** R180 ordered
  the **registered five-card** sweep re-run under `P7` — never a narrowed
  single-card experiment — because §13.8's `borrowed_brilliance` anomaly was
  pilot refusal that `P7` (R176) resolved, and because §13's Δ figures are `P6`
  reads. The draft is the parent's instrument and arm set unchanged, re-stamped
  to `RT10/D14/P7/C9`, with a new descriptive `Q4` on the bare-form play rate.
  **§8's predictions and §8.1's trigger are explicit [USER] slots and are
  blank**, so the packet is not cleared to launch. **Sequencing:** it runs
  *after* the payoff-reach sprint's graded read, per the approved settle-first
  plan, and before the staged `EB-43`/D15 landing (its own S3) →
  `review/active/m17-sweep-reregistration-p7-2026-08-13.md`; companion redesign
  options packet `review/active/m17-elemental-ecstasy-redesign-2026-08-13.md`.
- **Shop companion channel re-run (`S4-G10` / `C9`)** — **DRAFT, awaiting
  [USER] countersign at QUEUE `M14`, unrun.** The packet is in HEAD as of the
  `shop-floor-2026-08-10` merge. The channel's world moved ([USER] restored slot 2's
  Uncommon floor, `CONSTANTS_VERSION` 9) and the instrument's two defects were
  repaired, both on 2026-08-10; the packet asks to re-measure in the new world.
  Predictions are explicit [USER] slots and are still blank →
  `review/active/shop-rerun-registration-2026-08-10.md`.
- **The regret margins (`M13`)** — **DRAFT, §7 PARTLY FILLED 2026-08-12
  (R181), awaiting [USER] countersign at QUEUE `M13`, unrun.** `ROUTE_REGRET_MARGIN` and its drafter
  twin (`draft.DRAFT_REGRET_MARGIN`, the `+1.0`) have no recorded derivation;
  R164 ruled that the measurement is pre-registered and that **`+1.0` is not
  ratified**. The distribution printer `tools/regret_distribution.py` landed
  first and made a registration possible at all —
  the margin-free gap distribution for both numbers, on a read-only pass over
  finished runs, with no stamp movement. The packet's §7 predictions are
  explicit [USER] slots and are still blank, and its §6 lays out four
  derivation options at equal weight — including the upper-percentile
  derivation, whose circularity is stated there rather than assumed away.
  **R181 settled the scope slots:** control `C2` authorised (build owed before
  the run), control `C3` declined so `Q5` is dropped and Option B is
  unavailable, both sample rates reported separately, and **Option D — no
  margin — retained as the standing answer** unless the result shows a margin
  has utility. The predictions themselves are still blank →
  `review/active/regret-margin-registration-2026-08-12.md`.
- **Charge reads per turn (`EB-78`)** — **DRAFT, unrun, §5's prediction slots
  blank as [USER]'s.** R188 (2026-08-13) ruled **no** Charge read budget and
  returned `X9` to the watch register; a watch trigger needs the quantity it
  watches, and *how many reads a turn contains* was recorded nowhere until the
  instrument landed on 2026-08-13 (`resources.note_charge_read`, emit-only,
  tagged per source so the workshop's unsettled §6 scope boundary is not
  settled by construction). Descriptive: it grades no design and cannot on its
  own fire a nerf. §5.1 is where "repeatable reads dominant" becomes a number,
  and it is a [USER] slot. Sequenced after the payoff-reach graded read; it
  moves no version and opens no window →
  `review/active/charge-reads-per-turn-registration-2026-08-13.md`.
- **Kokomi stability band (D5)** — no band is declared yet (the declaration
  is QUEUE `S4-G6`; until it lands, the band rides DARK, `band = None`); its
  grading playtest is `docs/current/playtest/kokomi-playtest-protocol.md`
  (unrun; Answers block still blank).

New registrations add a pointer here and land their packet under
`review/active/`; when a registration is graded and closed, both leave HEAD.
