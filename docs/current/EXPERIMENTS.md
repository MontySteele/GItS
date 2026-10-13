# EXPERIMENTS

Standing measurement law. A registration packet lives under `review/active/`
while its picks are open and moves to `review/records/` once it has been run.
One home at a time, not two.

**The sim-law half of this file does not gate kit balance**: a kit at Balance
is measured on the real game (first section below, ruled 2026-10-05).

## Measurement law

### Kit balance is measured on the real game (2026-10-05)
- For a kit at Balance, the instrument is the real game: the kit's seat runs on
  the base-five baseline seeds and the per-fight telemetry
  (`review/active/klee-balance-measurement-2026-10-05.md`, ruled). Its numbers
  are compared with the base five's on the same seeds and acts.
- **Rows are chosen by run instance, never by clock window, and each act is
  compared only on the seeds where both sides have fights in that act**
  (2026-10-08, Klee suite 5 record pick 3). The base side is every counted base
  run on those seeds (today the 10-05 runs and the 2026-10-08 control). Pooled
  numbers may be shown beside the matched ones, never instead: a kit that dies
  early on a strong base seed otherwise reads as weaker in the later acts.
- Pre-registration for kit balance is **one line in the change's own paper,
  written before the suite runs and graded by it**. Slates, countersigns and
  blind grading below do not apply to kit balance, and the twelve-arm sim
  re-baseline is not its gate.
- The sections below govern the sim whenever it is used.

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
- **An engine legality fix is absorbed at the next planned bump, not
  re-baselined on its own ([USER], 2026-08-30, on `EB-182`).** `EB-182`
  made a priced `choose_one` mode unofferable when the bank cannot pay it;
  shipped `deep_breath`'s second mode used to overdraw Encore into HP and
  now is simply not offered below 3 Encore, which moves tier 0.5 numbers for
  any arm holding the card. None of the four stamps names an engine rule, so
  no stamp moved; published numbers stand (R101b); the next planned
  `RT/D/P/C` bump carries the re-baseline that absorbs it, and until then a
  read of an arm holding `deep_breath` says which side of the fix it is on.

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

### The blind-QA funnel (retired)

The staged-turn funnel's rules (R221 to R223: the seat control, the local-seat battery, stopping early) moved out with the dormant Codex and local seats; the text is at `git show b0eaa3108:docs/current/EXPERIMENTS.md`.

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

## Measurement authority (moved out of LAW, 2026-09-01)

Three blocks of `LAW.md` were measurement law rather than design or
engineering law, so they live here. They are moved verbatim, with their old
line ranges named. LAW keeps a one-line pointer at each site.

### What a measured number may be used for (was LAW lines 272 to 296)

- **The simulator's authority is relative deltas and structural findings, not
  absolute human-play winrates;** a ratification resting on an absolute winrate
  rests on the wrong number. (principles §7)
- **Seven-axis numbers are reportable, not load-bearing:** **all seven** axes are
  permanently CLOSED as reportable-only (never a gate, target, or justification
  to move a value). There is **no "Fanfare axis"** — R118's term names no axis;
  Fanfare is a Furina mechanic that falls under **scaling**, and the per-axis
  disposition therefore collapses to one disposition for all seven. (principles
  §7; D3; R90 Q7; R118; R138)
- **Ratified 1000-fight winrate bands change only by ruling, with archives;**
  small-n heuristic locks may be retuned to measured-noise reality only with a
  dated comment and disclosure. Authored Tier-0 25-card batteries are
  ceiling-saturated and keep only their matchup floors; Tier 0.5 owns the
  upper-power comparison. (R62; R47)
- **No number measured on a prototype row is quotable** — not in a packet, not
  in a register, not in a commit message. The quarantined prototype surface
  exists to be played, not to be measured against the shipped world: its rows
  reach no pool, no digest, no balance report and no stamp, so a figure taken
  off one has no comparable. The single exception is the decision-closeness
  falsifier (R213 F), which reads the TURN rather than the row. (R213 B; R215)

### A material card-sheet edit is a world change (was LAW lines 249 to 269)

- **A material card-sheet edit is a world change and lands under a
  `CONSTANTS_VERSION` bump.** *"A card-sheet edit that materially changes the
  drafted or combat world — card additions or removals, cost changes,
  effect-number changes, rarity moves — is a world change. It lands under a
  `CONSTANTS_VERSION` bump like any other balance constant, and numbers are not
  comparable across it."* The sheets sit outside the `RT/D/P/C` stamp, so
  without this rule two worlds differing in whether a card exists at all are
  indistinguishable to a reader of the stamp. **Rename amendment:** a
  *cosmetic* rename is exempt from the bump **only when neither the card id nor
  the display name is read mechanically** — and the burden is on the renamer to
  establish that, because at least one relic reads both. `card_name_damage_bonus`
  matches a **substring** against the card id **OR** the display name
  (`tier0/engine/relics.py:385-398`); its one carrier is `strike_dummy`,
  substring `"strike"`, `+3` to attacks only, FROZEN. A rename that adds or
  removes such a substring on either field moves damage and is not cosmetic.
  (R179; M15 draft text ratified as written, amended on the rename clause)
  **Role/archetype amendment (RATIFIED 2026-08-24, R202):** a change to a card's
  `role` or `archetypes` is a material card-sheet edit because both fields are
  mechanically read by drafting. It requires a `CONSTANTS_VERSION` bump, and
  drafted-world numbers are not comparable across it.


### The distinctness gate (was LAW lines 238 to 240)

- **Distinctness gate (red test):** uniq ≥ 70, maxclu ≤ 5, neardup ≤ 0.40/card;
  `top%`/`vocab` carry no permanent gate; a partial-pool anchor can only loosen a
  threshold, never certify it. (R81)

## The retired-era ledger

The Graded table (the EB-17p, KLEESPARK-*, KURAGECAD-*, X9READ and KOKOMI-SLICE1 registrations) and the EB-118 and M13 active registrations are at `git show b0eaa3108:docs/current/EXPERIMENTS.md`; their packets and results stay in `review/records/`.
