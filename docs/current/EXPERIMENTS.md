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
  window rather than to any one edit inside it.
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
- Pre-registration drafts are a [USER]-gated class; the grade goes in blind.

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
  is a result and a null that was not is an unfalsifiable instrument.

## Active registrations (pointers — packets live in `review/active/`)
- **EB-118 card-connectivity instrument** — static pre-registration at
  `review/active/eb118-richness-phase0-2026-08-23.md` §2, [USER]-approved
  2026-08-23. Deterministic, sheets-only, moves no `RT/D/P/C` version; eight
  pools (five canon via the `game_ref/` extraction surfaces, three mod) under
  one frozen classifier; honest mod-only stop when canon is absent. **Built
  (`tools/card_connectivity_report.py`) and calibration-run 2026-08-23 —
  descriptive only, NOT the baseline; no threshold is registered; the archived
  run was taken under classifier `v1`, before the same-day `v2` completion
  grounded the last three canon detectors, so it is not a `v2` read** —
  directional predictions only
  (§2.4); an absolute gate may be proposed only after the frozen classifier
  has read all five canon pools. **THE PAIRED BASELINE IS TAKEN, 2026-08-24 —
  `review/active/eb118-connectivity-baseline-2026-08-24.txt`**, at `a2e389f`
  and as the first commit of the Phase-1 branch, so every Phase-1 sheet edit
  is later than it in branch history, which is what §2.3(3)'s "immediately
  before the first sheet edit" means operationally. **All eight pools read**
  — the honest-stop path was not taken — and **UNCLASSIFIED is zero in every
  one of them**, so no share below rests on a silently-zeroed unknown.
  **The classifier is FROZEN from that commit** (§2.3(4)): if the vocabulary
  is later found wrong, BOTH sides are re-run under a new `VOCAB_VERSION`,
  never the post result alone. No threshold was derived and none may be — the
  five-canon precondition of §2.5 is now met, but meeting it authorizes a
  PROPOSAL to [USER], not a gate. Registered blind spots at §2.6 (the
  `decide%` gaps, the lowest-HP target heuristic, the `_worst_card` exhaust
  proxy).
- **payoff-reach re-registration** — the `RARITY_ODDS` fence. **RUN AND GRADED
  2026-08-24.** Q18 countersigned (R121); predictions committed 2026-08-13
  (R186) as the registration's `## 6`, before any sprint number was read; §6.5
  amended pre-run 2026-08-23 (`M28` ratified, R196) and that amendment
  implemented as `EB-120`; §6.6's `P12` freeze taken 2026-08-24; the registered
  cell run and graded blind the same day. **All six steps of `R121`'s
  countersigned order have now run, in order and complete.** Steps (5) and (6)
  were deliberately left out of the grading window and taken in the next one,
  2026-08-24: `EB-43`'s staged D15 landed with its re-baseline (`D` 14 → 15),
  and the `RA-G1`/`RA-G2`/`tto` quarantine lifted on the graded read.
  **THE OUTCOME, in one line: nine arms, nine `P5` MISSES on both axes — every
  arm ABOVE its band window, never below — Q-A SPLIT and Q-B SPLIT, no tripwire
  fired, and the redesign trigger fired roster-wide and minted `QUEUE` `M37` —
  **which [USER] then RULED the same day (R199), so the row has left HEAD and
  the design call is settled, not pending.**
  **The three commits, in the order the registration prescribes them.**
  **(1) the freeze**, `6e9fd92` — §6.6's `P12` taken at the live
  `RT12/D14/P7/C11`, re-stamping §6's world string and `T1`'s registered stamp
  string (in the tripwire table and in `tier05/exp_payoff_reach`) from the
  superseded `RT10/D14/P7/C9`. **No version integer moved in either
  direction**: the world moved first, by `RT` 10→11→12 and `C` 9→10→11, each an
  authorized bump fingerprinted against this fence when it landed, and the
  registration caught up to it. Left stale, `T1` fired on every arm of every run
  for the single reason that its string named a superseded world — a stale
  citation, not a finding. Re-stamped, it is silent on the frozen world and
  fires on a divergence in any of the four fields, both directions pinned by a
  test written against the constant rather than against the live tree.
  **(2) the run**, `19ed641` — the registered cell value for value: n = 600 per
  arm, seed 11, `hunter`, `assigned`, realistic, all registered acts, the nine
  arms of §6.5 and no others, nothing overridden. **56 seconds against a 4-hour
  stop-and-report ceiling.** Raw results at
  `review/active/payoff-reach-results-2026-08-24.txt`, on the `EB-17p`
  precedent — the instrument's own stdout with a provenance header, not a
  rewrite.
  **(3) the grade**, `56470ea` — blind-first, in §6.5's prescribed order:
  every prediction slot graded before any narrative (registration §7), then the
  design-facing readout (§8), then the mint.
  **TRIPWIRES `T1`–`T4`: NONE FIRED.** `T2`'s deck sizes land 19.3–25.0 inside
  the registered 12–30; `T4` finds no zero-payoff arm (smallest supply 5); and
  **`T3`'s amended classifier-integrity condition HOLDS with zero
  disagreements** — across every finished deck in every arm, no reward-pool base
  id classified differently on the deck side than in the static pool, with
  `draft.is_on_plan_payoff` the only route either leg took. That is what makes
  the nine misses a fact about content rather than about the instrument.
  **THE GRADE, slot by slot.** `P5` — the OFFICIAL post-settle static read, the
  one §6.5 reserved for after `EB-69` — is **0 PREDICTED / 0 SPLIT / 9 MISS**,
  both axes in every arm: supplies 5–14 (1.7×–4.7× the canonical ceiling of 3)
  against windows of 0–2 and 1–3, offers 0.0385–0.1270 (1.8×–5.9× canonical
  TOP) against intervals topping out at 0.0214. **The nine provisional misses
  `R196` adopted as information are SUPERSEDED by this read, not confirmed by
  it** — the three Kokomi arms were genuinely re-read after the fill, moved on
  both axes, and did not change verdict. **Q-A (A-ii): SPLIT** — direction
  holds (realized reach beats the blind-draft floor in all nine arms) and the
  ≥ 3× clause holds everywhere (3.8×–46.6×), while the ≥ 1.0-in-HIGH clause
  fails in one of three, `kokomi/commander` at 0.81 payoffs per finished deck
  with 48.3% of decks holding none. **Q-B (B-ii): SPLIT** — direction holds
  (six of nine arms print ZERO common payoffs; the counterfactual exceeds the
  actual in all nine) and the median-doubles clause holds under **both**
  available readings, 2.17× by median ratio and 2.46× by median offer, so the
  reading never had to be chosen; the band-crossing clause is **unsatisfiable**
  at these figures, because all nine actual offers already sit above the highest
  band boundary and §6.1's amendment forbids inventing one above `TOP`. **The
  `EB-118` Phase-0 §2.4 Kokomi supply clause: SPOILED, NOT GRADED** per
  R197/§6.8 — the supply did rise 3 → 5 by the one batch the amended fence
  admits, and a prediction voided before the read is not a prediction that
  missed. It stays struck where published and is not rewritten (`R101b`).
  **THE CONTROLS, reported and never part of a verdict.** `C1` is
  **half-executed**: §6.5 names its arms `(real_ironclad, starter)` /
  `(real_silent, starter)`, `starter` is a tier-0 DECK PACKAGE name that tier
  0.5 has no archetype for, and the pair's only constructible form is
  `real_ironclad/generic` / `real_silent/generic` — a naming reconciliation
  recorded rather than performed silently. `real_ironclad` reads realized reach
  2.11 at the same cell; `real_silent` is **BLOCKED** by a pre-existing engine
  defect (`BACKLOG EB-123`), reported as blocked and NOT at a reduced `n`,
  because dropping the one run that crashed is exactly the silent shrink the
  sample plan forbids. `C2` ran `blind` over the same nine arms — the only
  reading under which an empirical floor exists for each of the nine arms Q-A is
  predicted over — and puts that floor at 0.39–1.40 per deck against arithmetic
  floors of 0.037–0.278, i.e. **the registered comparator is 2.4×–19.3× lower
  than the floor a blind draft actually produces.** Recorded; it does not
  re-grade Q-A, which stays graded against the arithmetic floor (`D5`).
  §6.5's "7,800 with controls" implies four control arms and names two; the
  registered PARAMETER (600 per arm) was honoured exactly and the arithmetic
  discrepancy is recorded in the results artifact rather than resolved by
  picking two arms out of nine.
  **`C1` RUNS IN THE PRIMARY CHECKOUT ONLY, per §6.7** — `game_ref/` is
  gitignored and a worktree must never be given one — so the whole range was
  taken with the frozen reader loaded by path against the primary tree's
  content, the only configuration in which every registered arm and both
  controls read at once. The reader's only deletion across the two trees is the
  `T1` literal, so `static_leg`, `sim_leg` and `membership_audit` are
  byte-identical between them.
  **TWO DEFECTS FOUND BY THE RUN, BOTH FILED, NEITHER FIXED.** `EB-123`:
  NightmarePower resolves its remembered card through `loader.get_card`, and a
  Status card is synthesized under an id no loader index holds — one run of 600
  in `real_silent` dies on it. `EB-124`: `T3`'s `external-source` exclusion
  line counts ENCHANTED reward-pool cards and labels them as having come from
  outside the pool — all 122 such ids carry an `@`, genuinely external on-plan
  payoffs numbered zero in every arm, and `T3`'s answer is unchanged under
  either normalization (verified, not assumed). Neither was fixed inside the
  sprint: a behaviour fix moves the world and `P12` forbade that until the
  graded read, and editing a frozen reader after seeing its output is how an
  instrument gets tuned to its own reading.
  **`P12` IS DISCHARGED.** The freeze ran from the freeze act to the graded
  read, which is exactly the span §6.6 gave it, and no `RT`/`D`/`P`/`C` bump
  landed inside it. **`R190`'s remaining Assist payoff-supply fence is
  discharged by the same read.**
  **STEPS (5) AND (6) ARE EXECUTED, 2026-08-24, in the window after this one
  and in R121's order.** Step (5): `EB-43`'s staged D15 landed — the spotlight
  limb of `core_complete`/`_core_progress` now requires a machinery payoff, and
  `D` moved 14 → 15 with its twelve-arm re-baseline in the same window and
  nothing else beside it (`review/active/sitting-reads-2026-08-24.md`). **Every
  number this registration published is a `D14` reading and is archive by stamp
  law from that bump** — which changes nothing about the grade: a graded record
  stands as published (`R101b`) and is never re-run against a later world. Step
  (6): the `RA-G1`/`RA-G2`/`tto` quarantine lifted, which `R121` put "on the
  graded read, and nowhere earlier". **The design call the grade raised was
  `QUEUE` `M37`, and it is ANSWERED — R199, [USER] 2026-08-24:** the canonical
  bands stay a directional richness benchmark rather than a hard 1–3
  requirement, the sheets do over-use `role: payoff`, and `EB-118` Phase 3 is
  authorized to convert genuine setup / access / repair / bridge cards to glue
  or enabler under four named guardrails. The row has left HEAD, and so has the
  `EB-118` row that carried the Phase-3 fence — the pass ran to completion and
  closed on 2026-08-25 — so the durable text of both is **R199** and **R211** in
  their own commit messages. Nothing in this registration is
  reopened by it; a graded record is not re-read against a later ruling →
  `review/active/payoff-reach-reregistration.md` §7–§8;
  `review/active/payoff-reach-results-2026-08-24.txt`.
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
  to **`RT12/D17/P10/C19`**, with a new descriptive `Q4` on the bare-form play
  rate.
  **PARTLY FILLED 2026-08-13 (R189), and deliberately NOT countersigned:**
  `N` = 2,400 pairs/card, a 4-hour stop-and-report ceiling, §8.1's redesign
  trigger carried forward unchanged, and the `Q4` materiality threshold at 5%
  — the last recorded as [USER]'s chosen threshold, **not** evidence-derived.
  **§8's per-arm prediction table and the direction half of `Q4` stay blank**,
  so the packet is not cleared to launch; the countersign is withheld until the
  post-window restamp, because predictions are filled against the settled world
  — and the `RT`/`C` window that was open at R189 has since CLOSED (2026-08-24),
  so the restamp and the fill are now takeable. R189 also chose the **route** —
  measure-first, so this sweep runs before the `elemental_ecstasy` redesign
  (Option `C2`), which lands after the graded read as its own `C` bump.
  **Sequencing: its payoff-reach gate is DISCHARGED, and `S3`'s two-way fork is
  RESOLVED to the re-stamp arm.** It was to run *after* the payoff-reach
  sprint's graded read, per the approved settle-first plan, and *before* the
  staged `EB-43`/D15 landing — or, failing that, re-stamped past it (`S3`). The
  graded read landed 2026-08-24 and **D15 landed the same day**, so the "land
  before D15" arm is spent and the fork falls to the other one.
  **THE RE-STAMP IS TAKEN, 2026-08-25: `RT10/D14/P7/C9` →
  `RT12/D17/P10/C19`** — step (2) of the packet's own `§9` order, executed
  under R189's sequence at [USER]'s 2026-08-25 direction, and NOT a
  countersign-time act after all. The target the pointer last named
  (`RT12/D15/P7/C11`) was overtaken before it could be applied: `EB-118`'s
  richness pass ran to completion and `EB-136` landed inside the same span, so
  all four fields moved rather than a fourth. **Nothing countersign-gated was
  written:** `§8`'s per-arm table and the direction half of `Q4` are still
  blank and still [USER]'s, the countersign line is still blank, and the `Q4`
  estimand — the bare-form `played_when_drawn_rate` — was deliberately NOT
  measured, because reading an estimand before its prediction exists is the
  retro-fit `§8` prevents. `S3` is **spent** (the `D15` boundary is behind the
  packet, not ahead of it) and `S1` now pins all four fields; `§10`'s owed
  re-verification is done at the new stamp; and the run is staged mechanically
  at the packet's new `§9.2`. Nothing else in `S3` moves: the sweep still runs
  before the `C2` redesign. The countersign is still withheld and is still
  [USER]'s, and what precedes it is `§8`'s fill →
  `review/active/m17-sweep-reregistration-p7-2026-08-13.md`; companion redesign
  options packet `review/active/m17-elemental-ecstasy-redesign-2026-08-13.md`.
- **Shop companion channel re-run (`S4-G10`, registered at `RT12/D17/P10/C19`)**
  — **DRAFT, awaiting [USER] slate entry then countersign at QUEUE `M14`,
  unrun.** The packet is in HEAD as of the `shop-floor-2026-08-10` merge. The
  channel's world moved ([USER] restored slot 2's Uncommon floor,
  `CONSTANTS_VERSION` 9) and the instrument's two defects were repaired, both
  on 2026-08-10; the packet asks to re-measure in the new world. **Re-stamped
  FIVE times since, most recently 2026-08-25 (`RT12/D15/P7/C11` →
  `RT12/D17/P10/C19`), all under R182's sequence — the world moves, the packet
  catches up, then the slate is entered, then the countersign.** The fifth is
  the largest: thirteen bumps across three fields, and unlike the fourth it
  **reaches all three arms this cell runs** — `D16`/`D17` move the price table
  the shop's buy policy reads on every shelf entry, and `C19`'s new rows
  renumber the Klee and Furina shelves. `§2` items 12–15 enumerate it and
  `§2.1` names the table to author predictions against
  (`review/active/sitting-reads-2026-08-25-c19-d17-p10.md`, which supersedes
  the two 2026-08-24 tables; each stands as published, R101b). Predictions are
  explicit [USER] slots and are still blank; the run is staged mechanically at
  `§7.1`, where the instrument's standing hazards are named — it **prints the
  live `RT/D/P/C` as its first output line** (`EB-141(a)`, 2026-08-25) but
  **still does not route through a `Cell`** (`EB-141(b)`, gated on this
  registration's grade), so citability rests on `§7.1`'s provenance header
  binding that stdout to a registration, a commit and an `n`; and it has **no
  smoke path**, so any invocation reads the registered seed →
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
  and it is a [USER] slot. Its payoff-reach sequencing gate is DISCHARGED (the graded read
  landed 2026-08-24); it moves no version and opens no window, and what remains
  between it and a run is the countersign →
  `review/active/charge-reads-per-turn-registration-2026-08-13.md`.
- **Kokomi stability band (D5)** — no band is declared yet (the declaration
  is QUEUE `S4-G6`; until it lands, the band rides DARK, `band = None`); its
  grading playtest is `docs/current/playtest/kokomi-playtest-protocol.md`
  (unrun; Answers block still blank).

New registrations add a pointer here and land their packet under
`review/active/`; when a registration is graded and closed, both leave HEAD.
