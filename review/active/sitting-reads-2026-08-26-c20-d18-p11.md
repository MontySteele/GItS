# Standing roster re-baseline, 2026-08-26 — the `C20`/`D18`/`P11` world

> **Lifecycle: ACTIVE.** This is the ONE standing re-baseline the project owed
> at `RT12/D18/P11/C20`. It is descriptive only. It runs, records and reports.
> It recommends nothing, tunes nothing, and reads nothing into the numbers.
> Every call these numbers feed stays [USER]'s.

> **IT PUBLISHES BOTH AS THE STANDING RE-BASELINE AND AS THE PHASE-4 MILESTONE
> TABLE.** The predecessor published DIAGNOSTIC-SCOPED and explicitly not as
> the milestone table, because three scorer caveats made eight of `W3`'s rows
> FLOORS. R211 item 7 set the condition in terms — *the Phase-4 milestone read
> follows when the caveats clear* — and the caveats were to clear at this
> re-baseline, not at the `P11` commits. **All three were checked against the
> code at `main` = `190e598` before the numbers were read, and all three grade
> CLEARED** (§0, with file:line). The milestone read is the same twelve arms at
> the cell where the caveats clear, so one run serves both and only one was
> taken. **The label is Claude's call under R212 and the reasoning is in §0.4.**

> **This table supersedes
> `review/active/sitting-reads-2026-08-25-c19-d17-p10.md` as the standing
> read.** That file is not rewritten and not struck: it is a published record of
> the `C19`/`D17`/`P10` world and stands as published (R101b), its
> DIAGNOSTIC-SCOPED header included. Its `C19/D17/P10` columns are quoted below
> as this table's `before` and are archive from the commits named there. **The
> milestone label taken here does not reach backwards**: the predecessor's eight
> rows were floors when it published and remain floors as published.

> **IT IS TWELVE ARMS, AND ALL TWELVE RAN IN ONE PASS.** The read was taken in
> the primary checkout, the only tree that can see the gitignored `game_ref/`,
> so both `real_*` floors sit in the main tables rather than in an addendum.
> The run reached arm 12 without raising; exit code 0. BACKLOG `EB-128` is
> unchanged by that.

> **THE Δ COLUMN SPANS THREE STAMP FIELDS AT ONCE, AND ATTRIBUTION TO ANY ONE
> OF THEM IS NOT AVAILABLE.** `before` is `RT12/D17/P10/C19`; `after` is
> `RT12/D18/P11/C20`. Between them sit **one `DRAFTER_VERSION` bump**
> (`D17` → `D18`), **one `POLICY_VERSION` bump** (`P10` → `P11`, with
> `PILOT_WEIGHTS_VERSION` 5 → 6 beside it) and **one `CONSTANTS_VERSION` bump**
> (`C19` → `C20`). `RUNTEMPLATE_VERSION` is unmoved at 12. **No row's Δ below is
> attributable to `D18`, to `P11` or to `C20` alone**, and no attribution is
> attempted here. Per-window attribution is commit-hash scratch comparison
> (R207), taken at build time, and is not citable the way this table is.

## Terms used here

Unchanged from the 2026-08-13, 2026-08-24, 2026-08-24 `C13`/`D16` and
2026-08-25 `C19`/`D17`/`P10` packets, and repeated so this file is readable on
its own.

- **The stamp.** A version label like `RT12/D18/P11/C20`. It says which version
  of the game world produced a number. Numbers from different stamps are not
  comparable unless they are labeled, which is what this file does.
- **Plan (also "arm").** One way to build a character's deck.
- **Anchor.** A reference character measured against. `real_ironclad` and
  `real_silent` are the two real Slay the Spire characters; `ref_ironclad` is
  a reference build of the Ironclad, built from committed sheets alone.
- **95% interval.** The range a measured percentage could really be, given the
  sample size. Two intervals that do not overlap mean the difference is real
  at this sample size; two that overlap mean we cannot tell them apart. All
  intervals here are Wilson intervals, from `tier05.stats.wilson95`.
- **Cell.** The exact configuration a measurement was taken in — script,
  sample size, seed, route, loadout and world stamp. Two numbers are only
  comparable if their cells match in everything but the one thing under study.
- **Floor.** A number produced by an instrument that cannot see part of what
  the card prints. It bounds the card's contribution from below and says
  nothing about the ceiling. A floor that reads as no movement is not a
  finding of no movement. **The three caveats that made eight rows floors in
  the predecessor are cleared here (§0); the word survives in this file only
  where it names what the predecessor published.**

---

## Why this packet exists

Two obligations, discharged by one run.

**The standing re-baseline.** The live cell moved three fields off the standing
baseline's cell:

- **`DRAFTER_VERSION` 17 → 18.** `EB-28`: the Salon deploy stops pricing at
  zero. ONE new [USER]-overridable dial, `STATIC_SALON_MEMBER_VALUE = 1.5`, and
  nine Furina salon rows re-price on both faces.
- **`POLICY_VERSION` 10 → 11, with `PILOT_WEIGHTS_VERSION` 5 → 6 beside it.**
  The scorer-literacy window (R207): `EB-143`'s Spark hold-versus-spend term,
  `EB-144`'s five score-time predicates and both Salon verbs, `EB-145`'s
  payout-aware selection scoring, `EB-129` riding.
- **`CONSTANTS_VERSION` 19 → 20.** `EB-139`'s Swirl aura-aware bind (R211) and
  the ruled Sweet Dreams body (R189/R205), joined into one window.

Stamp law says every published number is world-stamped and worlds are not
comparable (R68), so every `C19`/`D17`/`P10` roster number became archive at
those commits.

**The Phase-4 milestone read.** R211 item 7 made it conditional on the standing
read's three caveats clearing, and the repairs landed as the one `P11` window
with the clearance deferred to the re-baseline. §0 does the clearance check
against code; the label follows from it.

### Experiments-law check, done first

Same check the prior packets made, same answer. This is a descriptive re-read
of an already-published comparison, re-produced from an unchanged script under
a moved stamp. `EXPERIMENTS.md` limits pre-registration and blind grading to a
measurement a playtest will grade (D5); no playtest grades this. Nothing in
this file is a registration, a grade or a band. The rule that makes the re-run
necessary at all is R68; the rule that makes it the ONE public read for the
span rather than one per bump is R207.

### What is deliberately not here

**The core-attainment columns.** `core attain`, `core 95%` and `tto` are not
printed, for the same tooling reason as on 2026-08-13, 2026-08-24, 2026-08-24
`C13`/`D16` and 2026-08-25: `tier05/exp_roster_anchors` has never printed them.
Restoring them is a separate build.

**Commentary.** Movements are stated as old value, new value and both
intervals. No claim is made about why any arm moved, and none about whether any
movement is good or bad.

**Per-window attribution.** See the Δ-span note in the header. R207 put that in
scratch reads, which are not published.

**A verdict on any card.** §0 grades whether the INSTRUMENT can see three named
things. It does not grade a card, and clearing a caveat is not a finding about
the card the caveat was about.

---

## 0. The caveat check — done from code, before the numbers were read

The predecessor named three scorer caveats and published DIAGNOSTIC-SCOPED
because of them. Each is checked below against the code at `main` = `190e598`,
with file:line. **All three grade CLEARED.**

### 0.1 Spark hold-versus-spend — **CLEARED**

The predecessor's claim: *"`spend_spark` appears **nowhere** in
`tier0/pilot/`, so spending 2 Sparks costs the pilot exactly nothing at score
time while the payoff it buys is scored in full."*

That is now false in code, and the repair is in the score seam rather than
beside it:

- `SPARK_HOLD_VALUE_WEIGHT = 1.0` — `tier0/pilot/policy.py:1076`. Its own
  comment names 0.0 as the degenerate setting at which the pilot is
  byte-identical to `P10`; it ships at 1.0, so the term is LIVE and not staged
  behind a default-off switch.
- It is applied inside `_score` (`tier0/pilot/policy.py:1212`) at
  **`tier0/pilot/policy.py:1252-1253`** —
  `if spark_cost(card): total -= SPARK_HOLD_VALUE_WEIGHT * _spark_hold_cost(state, card)`.
  This is the same `total` the damage, block, tempo and sustain terms
  accumulate into, so the charge lands on the number the pilot argmaxes.
- `_spark_hold_cost` — `tier0/pilot/policy.py:1138`. Three legs, largest wins:
  the stock floor `spent * C.PILOT_SPARK_VALUE`; the threshold leg
  `_spark_free_attack_loss` (`:1125`); the reader leg `_spark_reader_loss`
  (`:1111`), which re-reads every other card in hand at the two bank levels
  through `_spark_bank_probe` (`:1088`).
- The quantity charged is the engine's own cost line, `combat.spark_cost`
  (`tier0/engine/combat.py:181-194`), which sums TOP-LEVEL `spend_spark` ops
  through `effects.spend_spark_amount` (`tier0/engine/effects.py:892-906`) —
  so the pilot cannot charge itself for a quantity the playability gate would
  not have demanded.

**Is `spend_spark` valued at score time for the three sinks?** Yes, for all
three, because each prints the op at top level where `spark_cost` reads it:
`powder_charge` `docs/klee-cards.yaml:249`, `hold_the_line`
`docs/klee-cards.yaml:304`, `smoke_and_sparks` `docs/klee-cards.yaml:321` —
`{op: spend_spark, amount: 2}` on each. `spark_cost` returns 2 for each and 0
for every other card in the repo, so the term fires on exactly the three rows
the caveat named.

### 0.2 Predicate blindness — **CLEARED**

The predecessor's claim, in two parts: `spotlight_moved_this_turn` was outside
the conditional whitelist so `take_it_from_the_top` scored as Block 5 and
nothing else; `enemy_intends_attack` was likewise absent so `hold_the_line`'s
conditional Block 6 was credited at zero; and both Salon verbs appeared nowhere
in `tier0/pilot/` so `change_the_bill` scored as Block 3 and nothing else.

**The two predicates are in the scorable set.** `_ENGINE_LIVE_PREDICATES`
(`tier0/pilot/policy.py:156-160`) holds `enemy_intends_attack` (`:157`),
`has_salon_members` (`:158`) and `spotlight_moved_this_turn` (`:159`), and it
is unioned into `SCORABLE_PREDICATES` at `tier0/pilot/policy.py:163-175`.
`_active_effects` evaluates them by delegating VERBATIM to the engine's own
`effects._predicate` at `tier0/pilot/policy.py:271-281`, so the pilot's
forecast of which branch fires cannot disagree with the branch that fires.
`BLIND_PREDICATES` (`:183-189`) now holds only the two mid-resolution names
that have no honest score-time answer, `reaction_triggered_by_this` and
`killed_target` — neither of which is a caveat the predecessor raised. The
split is enforced rather than described: `tier0/tests/test_eb144_predicate_literacy.py`
fails the build if any printed predicate is in neither collection.

The two rows the caveat named print exactly those predicates —
`take_it_from_the_top` at `docs/furina-cards.yaml:624`
(`{op: conditional, if: spotlight_moved_this_turn, ...}`) and `hold_the_line`
at `docs/klee-cards.yaml:306` (`if: enemy_intends_attack`).

**Both Salon verbs are scored.** `_salon_verb_yield`
(`tier0/pilot/policy.py:303-370`) returns `(damage, block, encore_spent)` by
running what the resolver runs — `salon_perform` asks `effects.salon_tick_amount`
on the leftmost member with `note=False`, and `salon_rotate` moves the queue
offset so an in-body rotate-then-perform reads the member that will actually
perform. It is wired into all three score-time terms, not into a side channel:
`_expected_damage` at **`tier0/pilot/policy.py:373`**, `_raw_block` at
**`:496`**, and `_sustain_value` at **`:715`** (which charges the Encore
upkeep at the same rate a point of Encore is credited). `change_the_bill`
prints `{op: salon_rotate}, {op: salon_perform}, {op: block, amount: 3}` at
`docs/furina-cards.yaml:473`, so all three of its ops now reach a term.

### 0.3 Formula-aware SCORE, not just pick — **CLEARED**

The predecessor's claim: *"The `P10` chooser repair makes the **pick**
formula-aware; it does not make the **score** formula-aware, and those are two
different seams."*

`_formula_amount` (`tier0/pilot/policy.py:1723`) is called from the SCORE
seam, in both places a printed `amount_formula` can appear:

- `_expected_damage` at **`tier0/pilot/policy.py:399-401`** —
  `amount = (_formula_amount(state, fx, card, selection) if "amount_formula" in fx else _est(...))`.
- `_raw_block` at **`tier0/pilot/policy.py:501-502`**, the same shape.

Both are score-time terms feeding `_score`, and neither is `exhaust_victim`
(`:1576`), which is the chooser seam `P10` repaired. When the printed formula
counts an exhaust selection — decided off the engine's own registration prefix
by `_reads_a_selection` (`:1659`), never a name list — `_formula_amount`
forecasts the selection this card's own chosen exhaust WOULD make
(`_forecast_exhaust_selection`, `:1673`), installs it into
`state.exhaust_selection`, evaluates through `effects._calc_amount`, and
restores unconditionally (`:1751-1756`). Every card printing no selection
formula takes the first branch at `:1737-1738` and is arithmetically unchanged.

`the_tide_remembers` prints
`{op: damage, amount_formula: {base: 5, per: 2, count: exhaust_selection_cost}, target: all_enemies}`
at `docs/kokomi-cards.yaml:639`, which is exactly the `5 + 2 per
exhaust_selection_cost` the caveat named, and `count` carries the
`exhaust_selection_` prefix `_reads_a_selection` matches on. The slope is
therefore priced at score time, not just the base.

### 0.4 The label, and why it is Claude's call under R212

**All three CLEARED, so this table publishes as the standing re-baseline AND
as the Phase-4 milestone table.** The reasoning, visible:

1. **R211 item 7 wrote the condition, not a preference.** It said the milestone
   read *follows when the caveats clear*. The caveats were named exactly, in
   code terms, by the predecessor. Whether each is repaired is a question about
   what `tier0/pilot/policy.py` and `tier0/engine/effects.py` contain, checkable
   by reading them — which §0.1–§0.3 do, with citations. It is a derived
   determination, not a pick between design directions.
2. **R212 places derived-not-picked determinations with Claude, disclosed.**
   Nothing on the "still [USER]'s" side of the ladder is touched: no eyes-on
   taste, no staged balance lever merged, no money, no one-way door, no LAW or
   measurement-law amendment, and no pick between genuinely different design
   directions. The label selects which registered obligation this table
   discharges; it does not move a number, tune a dial, or gate a merge.
3. **One run serves both by construction.** The milestone read is the same
   twelve arms, same script, same seed, same n, same route and loadout, at the
   cell where the caveats clear. That cell is `RT12/D18/P11/C20`, and this is
   the run taken in it. Taking a second identical run to carry the second label
   would produce the same numbers and a second citable table of the same world.
4. **The label is disclosed rather than assumed**, here and in `STATE.md` and
   the `P11` stamp row, so a veto has something concrete to land on.

### 0.5 Residual conservatisms the code discloses — recorded, not graded

The three caveats are the three the predecessor named, and each is cleared as
stated. The repairs disclose narrower conservatisms of their own, in their own
comments, and they are recorded here so "CLEARED" is not read as "exact". None
of them is one of the three, and none is graded by this packet:

- `_salon_verb_yield` does not price the Chevalmarin tick's hydro application
  or the `SALON_TICK_BURST` particle, does not count a stage the scored card
  would itself deploy into, and still counts later ticks of a perform that
  would kill the last enemy mid-loop (`tier0/pilot/policy.py:336-341`).
- `_spark_hold_cost`'s reader leg reads the HAND ONLY; a Spark reader in the
  draw pile is not counted, deliberately, because reading the pile would give
  the pilot information the player does not have
  (`tier0/pilot/policy.py:1050-1054`).
- Leg 1's existence — charging a stock floor for a Spark with no reader in hand
  and the threshold untouched — is flagged in code as a sheet-pass sweep item
  and a [USER] pick, one defensible answer rather than a ruled one
  (`tier0/pilot/policy.py:1056-1063`).

---

## The cell

The `before` column is **quoted, not re-run**, for the same reason the
predecessor gave for its own: that column was taken by the same script, same
seed, same n, same route and same loadout on this machine, and it is the
standing baseline this table replaces. Re-running it is also not available —
reproducing it would mean checking the primary checkout, the only tree that can
see the gitignored `game_ref/` and therefore the only tree that can run the two
`real_*` arms, back onto an archive ref, which is exactly what the primary is
kept clean of.

| | |
|---|---|
| checkout | primary (`game_ref/` is primary-local and gitignored; a worktree cannot see it) |
| **before** | `review/active/sitting-reads-2026-08-25-c19-d17-p10.md` §§1–3 (`C19/D17/P10` columns, all twelve arms, `main` = `a247f25`) |
| **after** HEAD | `main` = **`190e598`** (`190e5980fcd003bb1f64a7b33a2ce9199b80f812`, PR #101 merge) |
| command (both) | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| before cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D17/P10/C19` |
| after cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D18/P11/C20` |
| route / policy / loadout | `hunter` / `assigned` / realistic, relics + potions, all registered acts |
| intervals | 95% Wilson (`tier05.stats.wilson95`), computed in-row by the script |
| wall clock | **152 s**, 2026-08-26 18:09:57 → 18:12:29 |
| exit code | **0** |
| errors | **none; all twelve arms completed.** |

Notes on that table:

- Both stamps were read live via `tier05/cells.py`, never hand-written. A
  world-check was run before the read and printed `RT12/D18/P11/C20`; the run
  header printed the same stamp.
- The two runs differ in **`DRAFTER_VERSION`, `POLICY_VERSION`,
  `CONSTANTS_VERSION` and the content those three label** — same script, same
  seed, same n, same route, same loadout, same machine. `--jobs` is wall-clock
  only; run *i* is a pure function of `seed + i`.
- The script has no arm selection — `ARMS` is a module constant
  (`tier05/exp_roster_anchors.py:51-64`) — so the full twelve ran, and
  `game_ref/` was present for both columns.
- No tracked file in the primary checkout was edited to take this reading, and
  nothing from `game_ref/` is copied, linked or quoted here.

---

## 1. The twelve arms — run winrate

| arm | `C19/D17/P10` win | `C19/D17/P10` 95% | `C20/D18/P11` win | `C20/D18/P11` 95% | Δ |
|---|---|---|---|---|---|
| `klee / demolition` | 5.1% | [4.3, 5.9] | **4.9%** | [4.2, 5.8] | −0.2 pp |
| `klee / spark` | 3.7% | [3.1, 4.5] | **3.9%** | [3.2, 4.6] | +0.2 pp |
| `klee / reaction` | 6.0% | [5.2, 6.9] | **6.1%** | [5.3, 7.0] | +0.1 pp |
| `furina / salon` | 2.5% | [2.0, 3.1] | **3.4%** | [2.8, 4.1] | +0.9 pp |
| `furina / spotlight` | 0.8% | [0.6, 1.2] | **1.0%** | [0.7, 1.5] | +0.2 pp |
| `furina / fanfare` | 0.9% | [0.6, 1.3] | **1.2%** | [0.8, 1.6] | +0.3 pp |
| `kokomi / priest` | 0.9% | [0.6, 1.3] | **0.9%** | [0.6, 1.3] | 0.0 pp |
| `kokomi / commander` | 2.3% | [1.8, 2.9] | **2.3%** | [1.9, 2.9] | 0.0 pp |
| `kokomi / assist` | 0.5% | [0.3, 0.8] | **0.5%** | [0.3, 0.8] | 0.0 pp |
| `ref_ironclad / generic` | 7.4% | [6.5, 8.4] | **7.4%** | [6.5, 8.4] | 0.0 pp |
| `real_ironclad / generic` | 5.2% | [4.5, 6.1] | **5.2%** | [4.4, 6.0] | 0.0 pp |
| `real_silent / generic` | 1.2% | [0.8, 1.6] | **1.1%** | [0.8, 1.6] | −0.1 pp |

**No winrate row separated from its own prior value at n = 3000.** Every pair
of intervals overlaps, and unlike the predecessor there is no boundary case:
the widest mover, `furina / salon`, prints [2.0, 3.1] before and [2.8, 4.1]
after, which share the whole band [2.8, 3.1].

## 2. Act-1 clear rate, same cell

| arm | `C19/D17/P10` act-1 | `C19/D17/P10` 95% | `C20/D18/P11` act-1 | `C20/D18/P11` 95% | Δ |
|---|---|---|---|---|---|
| `klee / demolition` | 82.4% | [81.0, 83.7] | **82.5%** | [81.1, 83.8] | +0.1 pp |
| `klee / spark` | 79.6% | [78.1, 81.0] | **79.7%** | [78.2, 81.1] | +0.1 pp |
| `klee / reaction` | 85.0% | [83.7, 86.3] | **85.0%** | [83.7, 86.3] | 0.0 pp |
| `furina / salon` | 50.5% | [48.7, 52.3] | **51.8%** | [50.0, 53.6] | +1.3 pp |
| `furina / spotlight` | 59.0% | [57.2, 60.7] | **60.5%** | [58.8, 62.3] | +1.5 pp |
| `furina / fanfare` | 45.2% | [43.4, 47.0] | **46.2%** | [44.4, 48.0] | +1.0 pp |
| `kokomi / priest` | 45.0% | [43.3, 46.8] | **45.1%** | [43.3, 46.9] | +0.1 pp |
| `kokomi / commander` | 51.5% | [49.7, 53.3] | **51.1%** | [49.3, 52.9] | −0.4 pp |
| `kokomi / assist` | 35.2% | [33.5, 36.9] | **35.4%** | [33.7, 37.1] | +0.2 pp |
| `ref_ironclad / generic` | 64.3% | [62.6, 66.0] | **64.3%** | [62.6, 66.0] | 0.0 pp |
| `real_ironclad / generic` | 65.5% | [63.7, 67.1] | **65.5%** | [63.8, 67.2] | 0.0 pp |
| `real_silent / generic` | 54.1% | [52.3, 55.8] | **54.0%** | [52.2, 55.8] | −0.1 pp |

**NO INTERVAL SEPARATION ON ANY ARM, on either rate column.** All
twenty-four before/after interval pairs in §1 and §2 overlap. The count of
interval separations in this table is **zero**. The three widest act-1 movers
are recorded so none is read as a separation: `furina / spotlight` overlaps on
[58.8, 60.7], `furina / salon` on [50.0, 52.3], `furina / fanfare` on
[44.4, 47.0].

The predecessor's one separation — `kokomi / priest` act-1, 39.9% → 45.0%
across `D16` → `D17` — is not re-tested here. This table's `before` for that
row is its post-move value 45.0%, and it held at 45.1%.

## 3. Shape columns, same cell

`acts` (mean acts cleared), `deck` (mean final deck size), `fights` (mean
fights survived). Prior value → new value on every row.

| arm | `acts` | `deck` | `fights` |
|---|---|---|---|
| `klee / demolition` | 1.11 → **1.11** | 24.6 → **24.9** | 15.0 → **15.0** |
| `klee / spark` | 1.02 → **1.02** | 23.9 → **24.1** | 14.2 → **14.2** |
| `klee / reaction` | 1.17 → **1.17** | 21.6 → **21.9** | 15.5 → **15.5** |
| `furina / salon` | 0.66 → **0.70** | 20.6 → **21.1** | 10.3 → **10.7** |
| `furina / spotlight` | 0.71 → **0.74** | 21.7 → **22.1** | 11.1 → **11.3** |
| `furina / fanfare` | 0.55 → **0.57** | 19.1 → **19.4** | 9.5 → **9.7** |
| `kokomi / priest` | 0.54 → **0.53** | 21.2 → **21.2** | 9.2 → **9.2** |
| `kokomi / commander` | 0.68 → **0.68** | 22.1 → **22.1** | 10.6 → **10.5** |
| `kokomi / assist` | 0.39 → **0.40** | 19.7 → **19.8** | 7.9 → **7.9** |
| `ref_ironclad / generic` | 1.02 → **1.02** | 21.4 → **21.8** | 13.9 → **13.9** |
| `real_ironclad / generic` | 0.94 → **0.94** | 21.3 → **21.6** | 13.2 → **13.2** |
| `real_silent / generic` | 0.64 → **0.65** | 20.7 → **20.8** | 10.6 → **10.6** |

`real_silent` is the one row where the shape columns and the rate columns move
in opposite directions: `acts` +0.01 and `deck` +0.1 against winrate −0.1 pp
and act-1 −0.1 pp. It is recorded, not interpreted.

**`deck` moved UP on ten of the twelve arms** and held on the other two
(`kokomi / priest` 21.2, `kokomi / commander` 22.1). **No arm's `deck` moved
down.** That is stated as arithmetic about twelve printed numbers and nothing
more.

## 4. The blast radius, the anchors, and why this table again has NO control set

**All twelve arms moved on at least one column.** There is no set of arms that
printed their prior values on all five, so this table has no control set — the
same position the predecessor was in, reached for a different reason and
recorded rather than discovered.

### 4.1 The two floors did NOT move outside interval

`real_ironclad` prints **5.2%** win and **65.5%** act-1 on both sides.
`real_silent` prints **1.2% → 1.1%** win and **54.1% → 54.0%** act-1. Every one
of those four pairs of intervals overlaps almost entirely, and no floor's new
point estimate falls outside its own prior interval. **By the test the brief
set — did a floor move outside interval — the answer is no, on both anchors and
on both rate columns.**

### 4.2 They are nevertheless not identical, and this table says so rather than rounding it away

A Wilson interval at fixed n is a function of the success count alone, so a
shifted interval is a moved count even when the rounded rate is unchanged.
Inverting the published intervals over n = 3000 through `tier05.stats.wilson95`
— enumerating every k whose interval reproduces the printed string — gives:

| row | `before` k | `after` k | verdict |
|---|---|---|---|
| `real_ironclad` win | {156, 157, 158} | {154, 155} | disjoint — count moved DOWN by 1–4 runs |
| `real_ironclad` act-1 | {1962, 1963, 1964} | {1965, 1966, 1967} | disjoint — count moved UP by 1–5 runs |
| `real_silent` win | {34, 35} | {34, 35} | not disjoint — no movement provable |
| `real_silent` act-1 | {1622} | {1620, 1621} | disjoint — count moved DOWN by 1–2 runs |
| `ref_ironclad` win | {221, 222, 223} | {221, 222, 223} | not disjoint — no movement provable |
| `ref_ironclad` act-1 | {1929, 1930} | {1929, 1930} | not disjoint — no movement provable |

And on the shape columns, which carry no interval, **all three anchors' `deck`
moved up**: `ref_ironclad` 21.4 → 21.8, `real_ironclad` 21.3 → 21.6,
`real_silent` 20.7 → 20.8.

**So the anchors are not a control across this span.** Anyone reading a Δ on a
roster arm should read the three anchor rows first: they moved too, in the same
direction on `deck` and by a handful of runs on the rate columns. This table
does not assign a cause to that, does not reconcile it against any stamp row's
wording, and does not claim it is or is not expected. It records what the two
published tables print. **The movement is inside interval on every rate column,
which is why §4.1 answers the brief's question "no" — and it is recorded here
at count resolution so that "no" is not mistaken for "identical".**

### 4.3 The direction pattern, as arithmetic and nothing more

- **All three Furina arms moved UP on all five columns each** — winrate, act-1,
  `acts`, `deck` and `fights`, without exception.
- **Klee's three moved UP on act-1 and `deck`, held on `acts` and `fights`, and
  split on winrate** — `demolition` −0.2 pp, `spark` +0.2 pp, `reaction`
  +0.1 pp.
- **Kokomi's three held on winrate to the printed precision** and split
  elsewhere: `priest` +0.1 pp act-1 with `acts` −0.01, `commander` −0.4 pp
  act-1 with `fights` −0.1, `assist` +0.2 pp act-1 with `acts` and `deck` up.
- **The three anchors held on every printed rate column but `real_silent`'s
  two**, and all three moved up on `deck`.

No claim is made about which of the drafter bump, the policy bump or the
constants bump moved which arm. That question is what commit-hash scratch reads
answer at build time (R207) and what this table deliberately does not.

## 5. What is NOT comparable to this table

- **Every column of `review/active/sitting-reads-2026-08-25-c19-d17-p10.md`.**
  Its `C19/D17/P10` columns are quoted above as this table's `before` and are
  archive from those commits. Quoting them is what makes this file's comparison
  self-contained; it is not a licence to re-quote them going forward. That file
  stands as published (R101b), DIAGNOSTIC-SCOPED header included.
- **Every column of `review/active/sitting-reads-2026-08-24-c13-d16.md`**, §8's
  addendum included, and of **`review/active/sitting-reads-2026-08-24.md`**
  (`C11`, `D14`/`D15`), **`review/active/sitting-reads-2026-08-13.md`** (`C10`,
  `D14`) and **`review/active/sitting-reads-2026-08-08.md`**
  (`RT9/D14/P6/C8`).
- **The roster-anchor standing table**
  (`docs/current/roster/roster-anchor-v14-v6-2026-08-06.md`), `RT7/D14/P3/C6`.
- **Every number published by the payoff-reach registration**, a `D14` read.
  The grade itself stands as published (R101b) and is never re-run against a
  later world.
- **The `W4` weight-sweep figures of any vintage.** The sweep runs in a gated
  sandbox world that no shipped cell has ever been in.
- **The `EB-118` connectivity reads**
  (`eb118-connectivity-baseline-2026-08-24.txt`, the Phase-1 and Phase-2
  post-reads, `eb118-w1-postread-2026-08-25.txt`). Those are a different
  instrument answering a different question, and their worlds are `C13` and
  earlier.
- **§4.7 shop-channel figures of any vintage**, unchanged from the 2026-08-13
  packet's note.
- **Any pre-`P11` number quoted as a milestone reading.** This is the first
  table carrying the Phase-4 milestone label, and the label does not travel
  backwards to a table taken under the caveats.

## 6. Raw output

The run's full stdout and stderr are captured verbatim beside this file at
`review/active/sitting-reads-2026-08-26-c20-d18-p11-raw.txt`, and §§1–3
reproduce its twelve rows column for column. Its stderr is the relic-skip
`UserWarning` block every run of this script emits — `juzu_bracelet`,
`bronze_scales`, `oddly_smooth_stone`, and those three only — and nothing else:
no traceback, no skipped arm, exit code 0. Nothing in this file is quoted from
any run other than the one named in the cell table.
