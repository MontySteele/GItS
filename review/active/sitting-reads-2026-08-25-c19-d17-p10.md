# Standing roster re-baseline, 2026-08-25 — the `C19`/`D17`/`P10` world

> **Lifecycle: ACTIVE.** This is the ONE standing read `EB-118`'s Window 3
> owes — the single public table for the whole `W3` window, not one table per
> slice and not one per intervening bump. It is descriptive only. It runs,
> records and reports. It recommends nothing, tunes nothing, and reads nothing
> into the numbers. Every call these numbers feed stays [USER]'s.

> **IT PUBLISHES DIAGNOSTIC-SCOPED AND IT IS NOT THE PHASE-4 MILESTONE TABLE**
> (R211 item 7, [USER] 2026-08-25; BACKLOG `EB-118` (e)). Three of `W3`'s eight
> shipped rows are measured by an instrument that cannot see the thing they
> print, so their contribution to every number below is a **FLOOR** and a null
> on them is **NOT EVIDENCE** of a null card. Named, with the code that makes
> each one true:
>
> - **The three Klee Spark sinks — `powder_charge`, `hold_the_line`,
>   `smoke_and_sparks` — are floors, because the pilot has no
>   hold-versus-spend term.** `spend_spark` appears **nowhere** in
>   `tier0/pilot/`, so spending 2 Sparks costs the pilot exactly nothing at
>   score time while the payoff it buys is scored in full. A pilot that cannot
>   value banking a Spark against spending one cannot price a sink, and three
>   new sinks are precisely what this slice ships.
> - **Both new Furina rows are scorer-blind floors.** `change_the_bill`'s two
>   Salon verbs (`salon_rotate`, `salon_perform`) appear nowhere in
>   `tier0/pilot/` — it scores as Block 3 and nothing else.
>   `take_it_from_the_top`'s bar, `spotlight_moved_this_turn`, is not in
>   `policy._active_effects`'s conditional whitelist (`:132-166`), so an
>   unrecognised predicate yields **neither branch** and the 10-damage arm is
>   invisible — it scores as Block 5 and nothing else. The sheet records the
>   arm firing on 16.7% of spotlight-arm plays.
> - **`Tide of Names` (`the_tide_remembers`) is a scorer-blind floor on its
>   payout.** Its damage is `5 + 2 per exhaust_selection_cost` to all enemies,
>   and the selection has not happened at score time, so the scorer prices the
>   base and not the slope. (The `P10` chooser repair makes the **pick**
>   formula-aware; it does not make the **score** formula-aware, and those are
>   two different seams.)
>
> `hold_the_line` carries a second, same-shaped blindness the sheet already
> records: `enemy_intends_attack` is likewise absent from `tier0/pilot/`, so
> its conditional Block 6 is credited at zero against a measured 72.6% fire
> rate on the demolition arm.
>
> **The Phase-4 milestone read follows when these caveats clear. `W3` is not
> owed it and this is not it.**

> **This table supersedes `review/active/sitting-reads-2026-08-24-c13-d16.md`
> as the standing read.** That file is not rewritten and not struck: it is a
> published record of the `C13`/`D16` world and stands as published (R101b),
> its §8 addendum included. Its `C13/D16` columns are quoted below as this
> table's `before` and are archive from the commits named here.

> **IT IS TWELVE ARMS, AND ALL TWELVE RAN IN ONE PASS.** The predecessor
> published ten and appended two in a dated addendum because `game_ref/` had
> been destroyed mid-window. That tree is present on this machine and the run
> reached arm 12 without raising, so the two `real_*` floors sit in the main
> tables here rather than in an addendum. BACKLOG `EB-128` is unchanged by
> that: it narrowed on the restore and did not close.

> **THE Δ COLUMN SPANS MORE THAN `W3`, AND THAT IS THE POINT OF TAKING IT
> HERE.** `before` is `RT12/D16/P7/C13`; `after` is `RT12/D17/P10/C19`. Between
> them sit **five `CONSTANTS_VERSION` bumps** (`C15` Window 1's labels, `C16`
> Window 2, `C17` Window 2b, `C18` `EB-136`'s same-target binding, `C19` `W3`),
> **one `DRAFTER_VERSION` bump** (`D17`) and **three `POLICY_VERSION` bumps**
> (`P8`, `P9`, `P10`). None of `C15`-`C18` was owed a standing baseline and none
> was given one; STATE records in terms that `W3`'s single public read absorbs
> their movement. **No row's Δ below is attributable to `W3` alone**, and no
> attribution is attempted. Per-character attribution inside `W3` is
> commit-hash scratch comparison (R207), taken at build time, and is not
> citable the way this table is.

## Terms used here

Unchanged from the 2026-08-13, 2026-08-24 and 2026-08-24 `C13`/`D16` packets,
and repeated so this file is readable on its own.

- **The stamp.** A version label like `RT12/D17/P10/C19`. It says which version
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
  finding of no movement.

---

## Why this packet exists

`EB-118`'s Phase-3 Window 3 landed on `main` at `a247f25` and moved three of
the four stamp fields at once:

- **`CONSTANTS_VERSION` 18 → 19.** `W3`'s card-body pass: eight sheet rows
  across all three characters, five new and three rewrites keeping their card
  ids. Klee's three `spend_spark` sinks, Furina's `change_the_bill` and
  `take_it_from_the_top`, and Kokomi's `pearl_barrage` / `shell_of_sanctuary`
  ("Salvage the Line") / `the_tide_remembers` ("Tide of Names").
- **`DRAFTER_VERSION` 16 → 17.** Two new pricing terms, and the first bump in
  the series where the drafter learns a **cost** rather than a value:
  `STATIC_SPARK_SPEND_COST = 2.5` and `spotlight_moved_this_turn` joining
  `STATIC_STATE_CONDITIONS` at `STATIC_SPOTLIGHT_MOVED_SHARE = 0.167`. Both
  are [USER]-overridable and each lives in exactly one constant.
- **`POLICY_VERSION` 9 → 10, with `PILOT_WEIGHTS_VERSION` 5 beside it.** The
  exhaust chooser's default payout hook becomes `formula_aware_payout`, with
  the new weight `EXHAUST_FORMULA_PAYOUT_WEIGHT = 1.0`.

Stamp law says every published number is world-stamped and worlds are not
comparable (R68), so every `C13`/`D16`/`P7` roster number became archive at
those commits. This is the re-take, and by R207 it is the ONE public read for
the window rather than one per slice.

### Experiments-law check, done first

Same check the prior packets made, same answer. This is a descriptive re-read
of an already-published comparison, re-produced from an unchanged script under
a moved stamp. `EXPERIMENTS.md` limits pre-registration and blind grading to a
measurement a playtest will grade (D5); no playtest grades this. Nothing in
this file is a registration, a grade or a band. The rule that makes the re-run
necessary at all is R68.

### What is deliberately not here

**The core-attainment columns.** `core attain`, `core 95%` and `tto` are not
printed, for the same tooling reason as on 2026-08-13, 2026-08-24 and
2026-08-24 `C13`/`D16`: `tier05/exp_roster_anchors` has never printed them.
Restoring them is a separate build.

**Commentary.** Movements are stated as old value, new value and both
intervals. No claim is made about why any arm moved, and none about whether any
movement is good or bad.

**Per-slice attribution.** See the Δ-span note in the header. R207 put that in
scratch reads, which are not published.

---

## The cell

The `before` column is **quoted, not re-run**, and the reason is stronger here
than it was for the predecessor. That column was taken by the same script, same
seed, same n, same route and same loadout on this machine, and it is the
standing baseline this table replaces. Re-running it is also not available:
reproducing it would mean checking the primary checkout — the only tree that
can see the gitignored `game_ref/`, and therefore the only tree that can run
the two `real_*` arms — back onto an archive ref, which is exactly what the
primary is kept clean of.

| | |
|---|---|
| checkout | primary (`game_ref/` is primary-local and gitignored; a worktree cannot see it) |
| **before** | `review/active/sitting-reads-2026-08-24-c13-d16.md` §§1–3 (`C13/D16` columns, ten arms) and §8.3 (the two `real_*` floors, same cell, `main` = `4fee4a6`) |
| **after** HEAD | `main` = **`a247f25`** (`a247f2542e877396f17ed0088bc68245191d1416`, PR #91, the `W3` merge) |
| command (both) | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| before cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D16/P7/C13` |
| after cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D17/P10/C19` |
| route / policy / loadout | `hunter` / `assigned` / realistic, relics + potions, all registered acts |
| intervals | 95% Wilson (`tier05.stats.wilson95`), computed in-row by the script |
| errors | **none; all twelve arms completed.** |

Notes on that table:

- Both stamps were read live via `tier05/cells.py`, never hand-written. The
  header of this run reads `RT12/D17/P10/C19`, which is the whole point of
  taking it after the stamp commits rather than before them.
- The two runs differ in **`CONSTANTS_VERSION`, `DRAFTER_VERSION`,
  `POLICY_VERSION` and the content those three label** — same script, same
  seed, same n, same route, same loadout, same machine. `--jobs` is wall-clock
  only; run *i* is a pure function of `seed + i`.
- The script has no arm selection — `ARMS` is a module constant — so the full
  twelve ran, and `game_ref/` was present for both columns.
- No tracked file in the primary checkout was edited to take this reading, and
  nothing from `game_ref/` is copied, linked or quoted here.

---

## 1. The twelve arms — run winrate

| arm | `C13/D16/P7` win | `C13/D16/P7` 95% | `C19/D17/P10` win | `C19/D17/P10` 95% | Δ |
|---|---|---|---|---|---|
| `klee / demolition` | 5.8% | [5.0, 6.7] | **5.1%** | [4.3, 5.9] | −0.7 pp |
| `klee / spark` | 4.2% | [3.5, 4.9] | **3.7%** | [3.1, 4.5] | −0.5 pp |
| `klee / reaction` | 6.4% | [5.5, 7.3] | **6.0%** | [5.2, 6.9] | −0.4 pp |
| `furina / salon` | 3.7% | [3.1, 4.4] | **2.5%** | [2.0, 3.1] | −1.2 pp |
| `furina / spotlight` | 1.3% | [1.0, 1.8] | **0.8%** | [0.6, 1.2] | −0.5 pp |
| `furina / fanfare` | 0.8% | [0.6, 1.2] | **0.9%** | [0.6, 1.3] | +0.1 pp |
| `kokomi / priest` | 0.7% | [0.5, 1.1] | **0.9%** | [0.6, 1.3] | +0.2 pp |
| `kokomi / commander` | 1.9% | [1.4, 2.4] | **2.3%** | [1.8, 2.9] | +0.4 pp |
| `kokomi / assist` | 0.2% | [0.1, 0.4] | **0.5%** | [0.3, 0.8] | +0.3 pp |
| `ref_ironclad / generic` | 7.5% | [6.6, 8.5] | **7.4%** | [6.5, 8.4] | −0.1 pp |
| `real_ironclad / generic` (floor) | 5.5% | [4.7, 6.3] | **5.2%** | [4.5, 6.1] | −0.3 pp |
| `real_silent / generic` (floor) | 1.3% | [0.9, 1.7] | **1.2%** | [0.8, 1.6] | −0.1 pp |

**No winrate row separated from its own prior value at n = 3000.** Every pair
of intervals overlaps, with one row at the boundary and it is recorded rather
than rounded away:

- **`furina / salon` is the boundary case.** Its prior interval printed
  [3.1, 4.4] and its new one prints [2.0, 3.1]: they **meet at the printed 3.1
  and share no more than that endpoint**. At full precision the answer depends
  on the exact success count behind the published `before` rate, which that
  record prints to one decimal and does not carry — the candidate `before`
  lower bounds span 3.05–3.11 and the `after` upper bounds span 3.09–3.16.
  **No separation is claimed, and none is available from the published
  record.**

## 2. Act-1 clear rate, same cell

| arm | `C13/D16/P7` act-1 | `C13/D16/P7` 95% | `C19/D17/P10` act-1 | `C19/D17/P10` 95% | Δ |
|---|---|---|---|---|---|
| `klee / demolition` | 83.1% | [81.7, 84.4] | **82.4%** | [81.0, 83.7] | −0.7 pp |
| `klee / spark` | 79.9% | [78.4, 81.3] | **79.6%** | [78.1, 81.0] | −0.3 pp |
| `klee / reaction` | 86.0% | [84.7, 87.2] | **85.0%** | [83.7, 86.3] | −1.0 pp |
| `furina / salon` | 52.8% | [51.0, 54.6] | **50.5%** | [48.7, 52.3] | −2.3 pp |
| `furina / spotlight` | 59.1% | [57.3, 60.8] | **59.0%** | [57.2, 60.7] | −0.1 pp |
| `furina / fanfare` | 45.6% | [43.8, 47.4] | **45.2%** | [43.4, 47.0] | −0.4 pp |
| `kokomi / priest` | 39.9% | [38.2, 41.7] | **45.0%** | [43.3, 46.8] | **+5.1 pp** |
| `kokomi / commander` | 49.7% | [47.9, 51.5] | **51.5%** | [49.7, 53.3] | +1.8 pp |
| `kokomi / assist` | 32.2% | [30.6, 33.9] | **35.2%** | [33.5, 36.9] | +3.0 pp |
| `ref_ironclad / generic` | 65.5% | [63.8, 67.2] | **64.3%** | [62.6, 66.0] | −1.2 pp |
| `real_ironclad / generic` | 67.2% | [65.5, 68.8] | **65.5%** | [63.7, 67.1] | −1.7 pp |
| `real_silent / generic` | 54.4% | [52.6, 56.2] | **54.1%** | [52.3, 55.8] | −0.3 pp |

**`kokomi / priest` act-1 is the ONE separation anywhere in this table.** Its
prior interval [38.2, 41.7] and its new interval [43.3, 46.8] do not overlap,
and the gap between them is 1.6 pp — wide enough that it survives any success
count consistent with the published `before` rate. This is stated as an
arithmetic fact about two intervals. **No cause is assigned to it here**, and
the Δ-span note in the header applies to it exactly as it applies to every
other row.

`kokomi / assist` is the near miss and is recorded so it is not read as a
second separation: [30.6, 33.9] and [33.5, 36.9] **do** overlap, on the band
[33.5, 33.9].

## 3. Shape columns, same cell

`acts` (mean acts cleared), `deck` (mean final deck size), `fights` (mean
fights survived). Prior value → new value on every row, because every row
moved.

| arm | `acts` | `deck` | `fights` |
|---|---|---|---|
| `klee / demolition` | 1.14 → **1.11** | 24.9 → **24.6** | 15.3 → **15.0** |
| `klee / spark` | 1.04 → **1.02** | 24.1 → **23.9** | 14.4 → **14.2** |
| `klee / reaction` | 1.19 → **1.17** | 21.8 → **21.6** | 15.6 → **15.5** |
| `furina / salon` | 0.76 → **0.66** | 21.3 → **20.6** | 11.2 → **10.3** |
| `furina / spotlight` | 0.72 → **0.71** | 21.8 → **21.7** | 11.2 → **11.1** |
| `furina / fanfare` | 0.55 → **0.55** | 19.1 → **19.1** | 9.4 → **9.5** |
| `kokomi / priest` | 0.47 → **0.54** | 20.7 → **21.2** | 8.7 → **9.2** |
| `kokomi / commander` | 0.64 → **0.68** | 21.8 → **22.1** | 10.2 → **10.6** |
| `kokomi / assist` | 0.35 → **0.39** | 19.4 → **19.7** | 7.5 → **7.9** |
| `ref_ironclad / generic` | 1.04 → **1.02** | 21.6 → **21.4** | 14.1 → **13.9** |
| `real_ironclad / generic` | 0.97 → **0.94** | 21.6 → **21.3** | 13.5 → **13.2** |
| `real_silent / generic` | 0.65 → **0.64** | 20.8 → **20.7** | 10.7 → **10.6** |

## 4. The blast radius — and why this table has NO control set

The predecessor could report a control: four of its twelve arms printed their
prior values on all five columns, and it used them as evidence. **This table
has no such set, and that was declared in advance rather than discovered
here.**

**All twelve arms moved on at least one column, and eleven moved on at least
four.** The `C18` stamp says why in terms: `EB-136`'s same-target binding
archives *"every combat AND tier-0.5 number for every character, INCLUDING THE
ANCHOR'S"*, because the anchor's own starter `bash` now lands its Vulnerable
on the body its damage killed instead of walking to a living bystander.
**`ref_ironclad` is therefore NOT a control across this span**, and neither
`real_*` floor is either. Anyone reading a downward Δ on a roster arm should
read the same three anchor rows before concluding anything about the roster:
they moved in the same direction.

The direction pattern, stated as arithmetic and nothing more:

- **The three Kokomi arms moved UP on all five columns each** — winrate, act-1,
  acts, deck and fights, without exception.
- **Eight arms moved DOWN or held on all five** — Klee's three, `furina/salon`,
  `furina/spotlight`, and all three anchors.
- **`furina / fanfare` is the one mixed row**: winrate +0.1 pp, act-1 −0.4 pp,
  `acts` and `deck` unmoved to the printed precision, `fights` +0.1.

No claim is made about which of the five constants bumps, the drafter bump or
the three policy bumps moved which arm. That question is what the scratch reads
answered at build time and what this table deliberately does not.

## 5. What is NOT comparable to this table

- **Every column of `review/active/sitting-reads-2026-08-24-c13-d16.md`**,
  §8's addendum included. Its `C13/D16` columns are quoted above as this
  table's `before` and are archive from these commits. Quoting them is what
  makes this file's comparison self-contained; it is not a licence to re-quote
  them going forward.
- **Every column of `review/active/sitting-reads-2026-08-24.md`** (`C11`,
  `D14`/`D15`), **`review/active/sitting-reads-2026-08-13.md`** (`C10`, `D14`)
  and **`review/active/sitting-reads-2026-08-08.md`** (`RT9/D14/P6/C8`).
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

## 6. Raw output

The run's full stdout is reproduced in §§1–3 row for row. Its stderr is the
relic-skip `UserWarning` block every run of this script emits — `juzu_bracelet`,
`bronze_scales`, `oddly_smooth_stone` — and nothing else; no traceback, no
skipped arm. Nothing in this file is quoted from any run other than the one
named in the cell table.
