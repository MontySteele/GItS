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
- Change one variable per measurement window **where a causal answer will
  actually change the next decision** (R207). The drafter/constants version is
  part of the variable set — a scorer change **is** a version bump in the same
  edit (`DRAFTER_VERSION` in `tier0/constants.py`). Where nothing turns on
  attributing a movement to one edit, several variables may share a window; the
  stamp then labels the world, and a number taken in it is attributable to the
  window rather than to any one edit inside it. **The null-scratch call is
  Claude's, disclosed (R212):** where the scratch read is null — no interval
  separation on any arm — Claude shares the window without asking, and the row
  and the PR text carry the scratch hash and that null read.
- **A published standing baseline is spent where it buys something, not owed at
  every bump (R207).** A **standing table** is published at a meaningful product
  milestone, or when a pending decision needs one. Intermediate attribution
  comes from **commit-hash scratch comparisons** — build a throwaway world at
  one commit, read it, compare it against another commit, and publish neither.
  **Its honest limit is that a scratch comparison is not citable the way a
  stamped baseline is:** scratch worlds are never pushed, so a scratch read
  cannot be re-read later without rebuilding the world it was taken in. Nothing
  here relaxes stamping or citability — see *Versioning* below — and every
  already-registered read stands as registered.

### Versioning
- **Version stamps are mandatory exactly as before (R207 left this untouched):**
  any change to a published-world variable bumps its stamp, and a report without
  a stamp is not citable. What R207 relaxed is when a **standing baseline** is
  published, not when a stamp is bumped.
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
- **Prediction slates are DRAFTED by Claude (R212)** from written design intent
  and committed as their own commit, labelled DRAFTED, **before any seed run**;
  [USER] countersigns in batch, or vetoes within five days. Pre-registration
  holds on commit-before-run, not on authorship. The grade still goes in blind.
- **Countersign once — restamp-and-hold is abolished (R212).** The packet's own
  world-check refuses to run on a moved world. A moved world means re-drafting
  the affected slots and disclosing the diff in the row; it never means
  re-signing an already-countersigned slate.

### Decision linkage (R206)
- **Every registration names the DECISION each outcome would change** — slot by
  slot, in the packet, before the run. A prediction with no decision attached to
  its outcomes is not registered.
- **If every plausible outcome leaves the next action unchanged, the experiment
  is not run.** An interesting number is not a reason; the reason is the act the
  number selects between. This reaches registrations only — a sweep is
  engineering tuning and is governed below.

### What registration law does NOT reach: engineering tuning
- A **sweep** is not a registered experiment and is not blind-graded — there is
  no prediction to grade, and nothing above reaches it. Three rules underneath
  that law carry over verbatim, and a sweep that skips them is not citable.
  **(1) Stamp law (R68):** every printed row carries its cell's `RT/D/P/C`; a
  sweep taken across a bump is two sweeps, and an unstamped row cannot say
  which. **(2) The dead-knob gate (R67, with R33):** a swept knob nothing READ
  produces a flat table indistinguishable from "the knob does not matter", so
  the point is refused rather than printed — and the gate may not be satisfied
  by adding a read. **(3) Look-first:** rows print in GRID ORDER, never sorted
  by outcome, and the adoption rule is fixed before any row is read, because
  picking the grid maximum of a noisy sweep afterwards is the forking-paths
  defect with extra steps. `tier05/sweeps.py` covers the `constants.py` knobs
  and `tier05/pilot_weight_sweep.py` the pilot weights filed outside it; both
  write their expected outcome down in advance, since a null that was predicted
  is a result and a null that was not is an unfalsifiable instrument. **`W4`
  finding, `P11` (2026-08-26):** making the scorer payout-aware puts `_score`
  through `exhaust_future_value`, so `discover_scope` reclassified all four
  exhaust-gate weights `pair_own` → `shared` and that gate now has **no
  sweepable surface left** — whether to sweep a shared weight anyway is
  [USER]'s call, not an integration's.

## Graded

The published record. A graded registration stands as published and is never
re-read against a later world or a later ruling (R101b); its packet and its raw
results file stay in `review/active/`, unedited. The narrative each entry
carried while it was active is in the commit message that retired it.

| Registration | Graded | Cell | Grade | Record |
|---|---|---|---|---|
| `EB-17p` force-first-copy paired winrate | 2026-08-10 | `RT9/D14/P6/C8` | 3 PREDICTED / 1 SPLIT / 1 MISS (`borrowed_brilliance`, wrong sign). §8.1's redesign trigger fired for `borrowed_brilliance` and `elemental_ecstasy`; R180 split them | packet `review/active/eb17p-registration-draft-2026-08-08.md` §13, §13.8; raw `review/active/eb17p-results-2026-08-10.txt` |
| payoff-reach re-registration (the `RARITY_ODDS` fence) | 2026-08-24 | `RT12/D14/P7/C11` | `P5`: 0 PREDICTED / 0 SPLIT / **9 MISS**, every arm ABOVE its window on both axes. Q-A SPLIT, Q-B SPLIT. Tripwires `T1`–`T4` all silent. The design call it raised was `M37`, ruled the same day (R199) | packet `review/active/payoff-reach-reregistration.md` §7–§8; raw `review/active/payoff-reach-results-2026-08-24.txt` |
| force-first-copy re-registered under `P7` (`M17`) | 2026-08-26 | `RT12/D17/P10/C19` | 4 PREDICTED / 1 SPLIT / 0 MISS; `Q4` PREDICTED on both halves (bare-form play rate 5.99%). §8.1's redesign trigger silent for **every** card — for `elemental_ecstasy` by 0.17 pp, on a delta whose sign is not established at that `N`. `C2` landed at Block 5, `a49bf20` | packet `review/active/m17-sweep-reregistration-p7-2026-08-13.md` §12; raw `review/active/m17-sweep-results-2026-08-26.txt` |
| shop companion channel re-run (`S4-G10`) | 2026-08-26 | `RT12/D17/P10/C19` | 2 PREDICTED / 1 SPLIT / 2 MISS over 6,000 runs. The redesign trigger FIRED on condition 4 alone, mean winrate Δ −0.07 pp; conditions 1–3 did not. The design call it raised is open at QUEUE `M14` | packet `review/active/shop-rerun-registration-2026-08-10.md` §8; raw `review/active/shop-rerun-results-2026-08-26.txt` |

## Active registrations (pointers — packets live in `review/active/`)

- **`EB-118` card-connectivity instrument** — static pre-registration at
  `review/active/eb118-richness-phase0-2026-08-23.md` §2, [USER]-approved
  2026-08-23. **Instrument:** `tools/card_connectivity_report.py` —
  deterministic, sheets-only, moves no `RT/D/P/C` version. **Cell:** eight
  pools (five canon through the `game_ref/` extraction surfaces, three mod)
  under one frozen classifier. **Status:** the paired baseline is TAKEN —
  `review/active/eb118-connectivity-baseline-2026-08-24.txt`, at `a2e389f` and
  as the first commit of the Phase-1 branch. All eight pools read and
  UNCLASSIFIED is zero in every one; the classifier is FROZEN from that commit,
  so if the vocabulary is later found wrong BOTH sides re-run under a new
  `VOCAB_VERSION`, never the post result alone. Directional predictions only
  (§2.4): no threshold is registered and none may be derived — meeting §2.5's
  five-canon precondition authorizes a PROPOSAL to [USER], not a gate.
  Registered blind spots at §2.6.
- **The regret margins (`M13`)** — **DRAFT, unrun**, §7's predictions blank.
  **Instrument:** `tools/regret_distribution.py`, a read-only pass over
  finished runs that moves no stamp. **Cell:** the margin-free gap distribution
  for `ROUTE_REGRET_MARGIN` and its drafter twin, whose `+1.0` R164 left
  unratified. **Status:** R181 settled the scope slots — control `C2`
  authorised with its build owed before the run, `C3` declined so `Q5` and §6's
  Option B are unavailable, and Option D (no margin) retained as the standing
  answer. Under R212(2) the §7 slate is Claude's to draft from written design
  intent and commit DRAFTED before the run, then countersigned in batch; the
  work is BACKLOG `M13` →
  `review/active/regret-margin-registration-2026-08-12.md`.
- **Charge reads per turn (`EB-78`)** — **DRAFT, unrun**, §5's prediction slots
  blank; §5.1 is where *repeatable reads dominant* becomes a number.
  **Instrument:** `resources.note_charge_read` — emit-only, count-only, tagged
  per source. **Cell:** resolved Charge reads per completed player turn.
  **Status:** descriptive, so it grades no design and cannot on its own fire a
  nerf; it moves no version and opens no window. Its payoff-reach sequencing
  gate is discharged. Under R212(2) the §5 slate is drafted and committed
  DRAFTED by Claude, then countersigned in batch →
  `review/active/charge-reads-per-turn-registration-2026-08-13.md`.
- **Kokomi stability band (D5)** — no band is declared, so it rides DARK
  (`band = None`). The declaration is QUEUE `S4-G6`; its grading playtest is
  `docs/current/playtest/kokomi-playtest-protocol.md` (unrun, Answers block
  blank).

New registrations add a pointer here and land their packet under
`review/active/`. When one is graded, it moves to the **Graded** table above —
the packet and its raw results stay where they are, unedited (R101b), and the
long active-entry narrative goes to the commit message that moved it.
