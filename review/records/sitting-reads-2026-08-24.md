Status: RECORD

# Standing roster re-baseline, 2026-08-24 — the twelve-arm table across `D14 → D15`

> **Lifecycle: ACTIVE.** This is the re-baseline the `DRAFTER` 14 → 15 bump
> owes, and `EB-43`'s row required that it land **with** the bump rather than
> after it. It is descriptive only. It runs, records and reports. It recommends
> nothing, tunes nothing, and reads nothing into the numbers. Every call these
> numbers feed stays [USER]'s.

> **This table supersedes `review/records/sitting-reads-2026-08-13.md` as the
> standing twelve-arm read.** That file is not rewritten and not struck: it is a
> published record of two earlier windows and stands as published (R101b). It is
> simply archive now — every column in it is a `D14` reading.

## Terms used here

Unchanged from the 2026-08-13 packet, and repeated so this file is readable on
its own.

- **The stamp.** A version label like `RT12/D15/P7/C11`. It says which version
  of the game world produced a number. Numbers from different stamps are not
  comparable unless they are labeled, which is what this file does.
- **Plan (also "arm").** One way to build a character's deck.
- **Anchor.** A reference character measured against. `real_ironclad` and
  `real_silent` are the two real Slay the Spire characters; `ref_ironclad` is a
  reference build of the Ironclad.
- **95% interval.** The range a measured percentage could really be, given the
  sample size. Two intervals that do not overlap mean the difference is real at
  this sample size; two that overlap mean we cannot tell them apart. All
  intervals here are Wilson intervals, from `tier05.stats.wilson95`.
- **Cell.** The exact configuration a measurement was taken in — script, sample
  size, seed, route, loadout and world stamp. Two numbers are only comparable if
  their cells match in everything but the one thing under study.

---

## Why this packet exists

`DRAFTER_VERSION` moved 14 → **15** on 2026-08-24: `EB-43`, the staged
spotlight-limb payoff-presence change, landing as step (5) of `R121`'s
countersigned six-step order. `core_complete` and `_core_progress` now ask a
spotlight deck for a machinery **payoff** as well as machinery, so
`_core_progress` — which feeds `score_offer`'s +3.0 core-advance bonus —
answers differently and the drafter picks differently. Stamp law says every
published number is world-stamped and worlds are not comparable (R68), so every
`D14` roster number became archive at that commit. This is the re-take.

### Experiments-law check, done first

Same check the 2026-08-13 packet made, same answer. This is a descriptive
re-read of an already-published comparison, re-produced from an unchanged script
under a moved stamp. `EXPERIMENTS.md` limits pre-registration and blind grading
to a measurement a playtest will grade (D5); no playtest grades this. Nothing in
this file is a registration, a grade or a band. The rule that makes the re-run
necessary at all is R68.

### What is deliberately not here

**The core-attainment columns.** `core attain`, `core 95%` and `tto` are not
printed, for the same mechanical reason as on 2026-08-13:
`tier05/exp_roster_anchors` has never printed them — they came from the
roster-anchor document's own throwaway per-arm harness — and nothing below
reconstructs them. **This is now a tooling fact and no longer a quarantine
fact:** the `Q18`/`Q19` quarantine over those columns lifted on the graded read
the same day (`R121` step (6)). Restoring the columns to this script is a
separate build, not part of this re-baseline.

**Commentary.** Movements are stated as old value, new value and both intervals.
No claim is made about why any arm moved.

---

## The cell

Both columns were re-run. The `D14` column is **not** quoted from the
2026-08-13 packet — see "why the before column was re-run" below.

| | |
|---|---|
| branch | `d15-landing` (worktree `../GItS-d15`) |
| **before** HEAD | `812a1cd` — `main` at the merge of PR #57, taken in the primary checkout |
| **after** HEAD | `499186b` — the D15 landing commit, taken in the worktree |
| command (both) | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| before cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D14/P7/C11` |
| after cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D15/P7/C11` |
| route / policy / loadout | `hunter` / `assigned` / realistic, relics + potions, all registered acts |
| intervals | 95% Wilson (`tier05.stats.wilson95`), computed in-row by the script |
| errors | none — both runs completed all twelve arms, zero tracebacks |

Notes on that table:

- Both stamps were read live via `tier05/cells.py`, never hand-written.
- The two runs differ in **`DRAFTER_VERSION` and nothing else**: same script,
  same seed, same n, same route, same loadout, same twelve arms, same machine.
  `--jobs` is wall-clock only; run *i* is a pure function of `seed + i`.
- `game_ref/` was present for both runs, so both `real_*` anchors are live and
  no `ref_*` substitution was needed. The worktree run used a **copy** of
  `game_ref/` — a copy, never a junction or symlink, because `OPERATIONS.md`
  forbids linking one into a worktree (`git worktree remove` follows a link and
  has destroyed non-regenerable files). The copy was deleted after the run.

### Why the `before` column was re-run rather than quoted

The 2026-08-13 packet's `RT12` column was taken at `RT12/D14/P7/**C10**`. Two
things have moved since inside `C`: `CONSTANTS` 10 → 11 (the Kokomi rotation
law) and `EB-69` (Kokomi's pool 62 → 76 cards, content with no version integer).
That packet's own archive note already voided its three Kokomi rows for exactly
this reason. Quoting a nine-row `C10` column beside three blanks would have made
the `D14 → D15` comparison rest on two different worlds, so the whole twelve-arm
table was re-taken at `C11` first and the bump measured against that.

**What the re-take shows about that scope claim, stated as measured.** All nine
non-Kokomi rows at `RT12/D14/P7/C11` reproduce the 2026-08-13 packet's `RT12`
column **to the printed precision, on every column** — winrate, act-1 and all
three shape values. All three Kokomi rows moved. That is what the C11 archive
note said would happen, and it is recorded here as a fact about two runs, not
attributed to either half of the `C10 → C11` window.

| Kokomi arm | `C10` win (2026-08-13) | `C11` win (here, `D14`) | `C10` act-1 | `C11` act-1 |
|---|---|---|---|---|
| `kokomi / priest` | 1.1% | **0.7%** | 42.3% | **39.9%** |
| `kokomi / commander` | 1.5% | **1.9%** | 51.3% | **49.7%** |
| `kokomi / assist` | 0.5% | **0.2%** | 33.8% | **32.2%** |

---

## 1. The twelve arms — run winrate

| arm | `D14` win | `D14` 95% | `D15` win | `D15` 95% |
|---|---|---|---|---|
| `klee / demolition` | 6.4% | [5.6, 7.4] | **6.4%** | [5.6, 7.4] |
| `klee / spark` | 3.9% | [3.3, 4.7] | **3.9%** | [3.3, 4.7] |
| `klee / reaction` | 5.6% | [4.8, 6.4] | **5.6%** | [4.8, 6.4] |
| `furina / salon` | 3.9% | [3.3, 4.7] | **3.9%** | [3.3, 4.7] |
| `furina / spotlight` | 1.0% | [0.7, 1.4] | **1.4%** | [1.1, 1.9] |
| `furina / fanfare` | 1.1% | [0.8, 1.6] | **1.1%** | [0.8, 1.6] |
| `kokomi / priest` | 0.7% | [0.5, 1.1] | **0.7%** | [0.5, 1.1] |
| `kokomi / commander` | 1.9% | [1.4, 2.4] | **1.9%** | [1.4, 2.4] |
| `kokomi / assist` | 0.2% | [0.1, 0.4] | **0.2%** | [0.1, 0.4] |
| `ref_ironclad / generic` | 7.5% | [6.6, 8.5] | **7.5%** | [6.6, 8.5] |
| `real_ironclad / generic` (floor) | 5.5% | [4.7, 6.3] | **5.5%** | [4.7, 6.3] |
| `real_silent / generic` (floor) | 1.3% | [0.9, 1.7] | **1.3%** | [0.9, 1.7] |

**Eleven of the twelve arms printed identically on every column.** One arm
moved: `furina / spotlight`, +0.4 pp, 1.0% → 1.4%. Its two intervals overlap on
[1.1, 1.4], so it has **not** separated from its own `D14` value at n = 3000.

Per R68 the `D14` column is archive from this commit regardless of how far any
row moved, including the eleven that did not move at all.

## 2. Act-1 clear rate, same cell

Eleven arms printed identically here too and are listed for completeness; only
`furina / spotlight` moved.

| arm | `D14` act-1 | `D15` act-1 | `D15` 95% |
|---|---|---|---|
| `klee / demolition` | 83.9% | **83.9%** | [82.6, 85.2] |
| `klee / spark` | 80.6% | **80.6%** | [79.2, 82.0] |
| `klee / reaction` | 85.2% | **85.2%** | [83.8, 86.4] |
| `furina / salon` | 53.6% | **53.6%** | [51.8, 55.4] |
| `furina / spotlight` | 55.4% | **59.4%** | [57.7, 61.2] |
| `furina / fanfare` | 48.6% | **48.6%** | [46.8, 50.4] |
| `kokomi / priest` | 39.9% | **39.9%** | [38.2, 41.7] |
| `kokomi / commander` | 49.7% | **49.7%** | [47.9, 51.5] |
| `kokomi / assist` | 32.2% | **32.2%** | [30.6, 33.9] |
| `ref_ironclad / generic` | 65.5% | **65.5%** | [63.8, 67.2] |
| `real_ironclad / generic` | 67.2% | **67.2%** | [65.5, 68.8] |
| `real_silent / generic` | 54.4% | **54.4%** | [52.6, 56.2] |

**`furina / spotlight` act-1 moved 55.4% [53.6, 57.2] → 59.4% [57.7, 61.2], and
these two intervals do NOT overlap** (57.2 against 57.7). At this n that is a
real separation, and it is the one separation in the table. Recorded as
measured; no inference is drawn from it here.

## 3. Shape columns, same cell

`acts` (mean acts cleared), `deck` (mean final deck size) and `fights` (mean
fights survived), all twelve arms at `D15`. **Only `furina / spotlight` moved**;
its `D14` values are given beside it and the other eleven printed their `D14`
values unchanged.

| arm | `acts` | `deck` | `fights` |
|---|---|---|---|
| `klee / demolition` | 1.18 | 25.3 | 15.7 |
| `klee / spark` | 1.03 | 24.2 | 14.5 |
| `klee / reaction` | 1.17 | 21.7 | 15.5 |
| `furina / salon` | 0.78 | 21.5 | 11.4 |
| `furina / spotlight` | 0.67 → **0.73** | 21.3 → **21.8** | 10.7 → **11.2** |
| `furina / fanfare` | 0.60 | 19.6 | 9.9 |
| `kokomi / priest` | 0.47 | 20.7 | 8.7 |
| `kokomi / commander` | 0.64 | 21.8 | 10.2 |
| `kokomi / assist` | 0.35 | 19.4 | 7.5 |
| `ref_ironclad / generic` | 1.04 | 21.6 | 14.1 |
| `real_ironclad / generic` | 0.97 | 21.6 | 13.5 |
| `real_silent / generic` | 0.65 | 20.8 | 10.7 |

## 4. The blast radius, recorded because it is checkable and it checked

`tier0/constants.py`'s D15 note claims the change reaches spotlight arms and
nothing else. The table above is that claim's test at n = 3000, and it holds
exactly: one arm of twelve moved, and it is the spotlight arm. Eleven arms
printing bit-identical across a drafter bump is what a correctly scoped limb
change looks like, and it is the reason this packet does not need to disentangle
D15 from anything else — nothing else was in the window.

That is a statement about this cell. It is **not** a claim that the change is
good, that `furina / spotlight` is now well-placed, or that +0.4 pp is a
meaningful gain — the winrate intervals overlap and the act-1 intervals do not,
which is a description of two columns and nothing more.

## 5. What is NOT comparable to this table

- **Every column of `review/records/sitting-reads-2026-08-13.md`.** Its `RT10`
  and `RT11` columns were already archive; its `RT12` column is a `D14`/`C10`
  reading and is archive from this bump. The `D14` column above is reproduced so
  this file's comparison is self-contained; that is not a licence to re-quote
  `D14` going forward.
- **`review/records/sitting-reads-2026-08-08.md`**, taken at `RT9/D14/P6/C8` —
  all four stamp fields have now moved.
- **The roster-anchor standing table**
  (`docs/current/roster/roster-anchor-v14-v6-2026-08-06.md`), taken at
  `RT7/D14/P3/C6`. Its `RA-G1`/`RA-G2`/`tto` quarantine lifted on 2026-08-24,
  which restores those columns as **readable**; it does not make a `C6`/`D14`
  reading comparable with anything here. The two facts are independent and both
  apply.
- **Every number published by the payoff-reach registration**
  (`review/records/payoff-reach-reregistration.md`), a `D14` read. Archive by
  stamp law from this bump; the grade itself stands as published (R101b) and is
  never re-run against a later world.
- **§4.7 shop-channel figures of any vintage**, unchanged from the 2026-08-13
  packet's note.

## 6. Raw output

Both runs' full stdout, warnings included, is reproducible from the cells in the
table above. Nothing in this file is quoted from any run other than the two
named there.
