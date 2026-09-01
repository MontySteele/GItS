Status: RECORD

# Standing roster re-baseline, 2026-08-13 — the twelve-arm table across `RT10 → RT11`, and again across `RT11/C9 → RT12/C10`

> **Two windows, one document.** Part 1 (§1–§5) is the `RT10 → RT11` re-baseline, published as taken. Part 2 (§6–§10) is the second re-take, owed by the window-2 correctness batch's coordinated bump later the same day. Part 1 is not rewritten and its `RT11` column is Part 2's `RT11` column — the same numbers, from the same run, quoted once.

> **Lifecycle: ARCHIVE as of 2026-08-24.** This was the re-baseline the
> `RUNTEMPLATE` 10 → 11 bump owed. It is descriptive only. It runs, records and
> reports. It recommends nothing, tunes nothing, and reads nothing into the
> numbers. Every call these numbers feed stays [USER]'s.

> **ARCHIVE NOTE (whole document), 2026-08-24 — `D14 → D15`.** `EB-43` landed
> the spotlight-limb payoff-presence change and `DRAFTER_VERSION` moved 14 →
> 15, so **every column in this file is a `D14` reading and is archive by stamp
> law** (R68) — the nine non-Kokomi rows of Part 2 included, which the C11 note
> below had left standing. The standing twelve-arm table is now
> `review/records/sitting-reads-2026-08-24.md`, taken at `RT12/D15/P7/C11`.
> Nothing here is rewritten (R101b); the numbers stand exactly as published and
> are quotable only with their own stamps. **Recorded from the re-take, because
> it bears on how this file is read:** re-run at `C11`/`D14`, all nine
> non-Kokomi rows of Part 2 reproduced to the printed precision on every
> column, and all three Kokomi rows moved — which is what the note below said
> would happen.

> **ARCHIVE NOTE (Kokomi rows only), 2026-08-23 — `C10 → C11`.** The
> rotation law landed (`CONSTANTS_VERSION` 11): a Status or Curse is no
> longer conscriptable or chosen-exhaustable by Kokomi and pays no
> Charge/Burst. Every Kokomi number below is therefore pre-C11 archive —
> quoted only with its stamp, not comparable unlabeled with any C11 read.
> All non-Kokomi rows are untouched by C11 and remain the standing
> baseline. Nothing below is rewritten (R101b).

## Terms used here

- **The stamp.** A version label like `RT11/D14/P7/C9`. It says which version of
  the game world produced a number. Numbers from different stamps are not
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
  size, seed, route, loadout and world stamp. Two numbers are only comparable
  if their cells match in everything but the one thing under study.

---

## Why this packet exists

`RUNTEMPLATE_VERSION` moved 10 → 11 on 2026-08-13: the `EB-82` Grave of the
Forgotten conversion and the `EB-85` batch of five enchantment fixes, landed
together under one coordinated bump. Stamp law says every published number is
world-stamped and worlds are not comparable (R68), so every `RT10` roster
number became archive at that commit. This is the re-take.

### Experiments-law check, done first

This is a descriptive re-read of an already-published comparison, re-produced
from an unchanged script under a moved stamp. `EXPERIMENTS.md` limits
pre-registration and blind grading to a measurement a playtest will grade (D5);
no playtest grades this. Nothing in this file is a registration, a grade or a
band. The rule that applies is the one that makes the re-run necessary at all:
R68.

### What is deliberately not here

**Quarantined columns.** `core attain`, `core 95%` and `tto` stay quarantined
under `Q18`/`Q19` (R121) pending the payoff-reach re-registration.
`tier05/exp_roster_anchors` does not print them and nothing below reconstructs
them.

**Commentary.** Movements are stated as old value, new value and both
intervals. No claim is made about why any arm moved, and no arm's movement is
attributed to either half of the window.

---

## The cell

| | |
|---|---|
| branch | `overnight-burn-2026-08-12` |
| **pre-window** HEAD | `f9b9fa2` + both crash fixes (see the label below), taken in the sibling checkout `GItS-prewindow` |
| **post-window** HEAD | `768dae6` — the stamp-bump commit, taken in the primary checkout |
| command (both) | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| pre-window cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT10/D14/P7/C9` |
| post-window cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT11/D14/P7/C9` |
| route / policy / loadout | `hunter` / `assigned` / realistic, relics + potions, all registered acts |
| intervals | 95% Wilson (`tier05.stats.wilson95`), computed in-row by the script |
| errors | none — both runs completed all twelve arms, zero tracebacks |

Notes on that table:

- Both stamps were read live via `tier05/cells.py`. `A6_INSTRUMENT_VERSION` is
  not read by anything here.
- The two runs differ in **the window and nothing else**: same script, same
  seed, same n, same route, same loadout, same twelve arms, same machine, and
  the same two engine fixes on both sides. `--jobs` is wall-clock only; run *i*
  is a pure function of `seed + i`.
- `game_ref/` was present for both runs, so both `real_*` anchors are live and
  no `ref_*` substitution was needed. The pre-window run was taken in a sibling
  checkout holding a **copy** of `game_ref/` — a copy, never a junction or
  symlink, because `OPERATIONS.md:154` forbids linking one into a worktree
  (`git worktree remove` follows a link and has destroyed non-regenerable
  files). The copy was deleted before the worktree was removed.

### The label every number here carries: two crash fixes, on BOTH sides

This table could not be taken at all until two defects were fixed, and both are
disclosed here rather than left for a reader to discover from a commit log.

The last twelve-arm read at this n was 2026-08-08, under `RT9` — before
enchantments entered the run layer. Re-taking it now, **both `real_*` anchors
died mid-run and printed no row**, at two independent places where the upgrade
path is not enchantment-aware:

1. `refpowers._upgraded` reaches a card's upgraded form by appending
   `upgrades.SUFFIX` and letting the card index miss. On an enchanted upgraded
   id the second suffix lands *inside* the decoration (`x@nimble-2++`) and
   `enchantments.split` reaches `int("2+")` first. Aggression recalls from the
   discard pile, so any Ironclad run holding an enchanted upgraded attack
   aborted. Fixed at `21d6b75`.
2. `upgrades.apply_upgrade` looked the *decorated* id up in the upgrade index
   and raised "no applicable upgrade", while `has_upgrade` — taught by R82's
   reopen — looked past the mark and answered True for the same card.
   `_best_upgrade_target` scores candidates by calling `apply_upgrade`, so one
   enchanted upgradable card in hand killed the run. Fixed at `2eff2bd`.

**Both fixes are present on both sides of the comparison**, so neither is a
confound: the only thing that differs between the two tables is the window.
Neither fix renumbers a published result, because no `RT10` number existed for
either anchor to renumber — they were crashing. Three sibling call sites with
the same shape were left unfixed and are filed as `EB-109`.

---

## 1. The twelve arms — run winrate

| arm | `RT10` win | `RT10` 95% | `RT11` win | `RT11` 95% |
|---|---|---|---|---|
| `klee / demolition` | 7.8% | [6.9, 8.8] | **7.4%** | [6.5, 8.4] |
| `klee / spark` | 4.2% | [3.5, 5.0] | **3.9%** | [3.3, 4.7] |
| `klee / reaction` | 6.7% | [5.8, 7.6] | **6.4%** | [5.5, 7.3] |
| `furina / salon` | 4.9% | [4.2, 5.7] | **5.0%** | [4.3, 5.8] |
| `furina / spotlight` | 1.2% | [0.9, 1.7] | **1.0%** | [0.7, 1.4] |
| `furina / fanfare` | 1.3% | [0.9, 1.7] | **1.2%** | [0.9, 1.7] |
| `kokomi / priest` | 0.9% | [0.6, 1.3] | **1.0%** | [0.7, 1.4] |
| `kokomi / commander` | 1.7% | [1.3, 2.2] | **1.6%** | [1.2, 2.1] |
| `kokomi / assist` | 0.3% | [0.2, 0.6] | **0.4%** | [0.2, 0.7] |
| `ref_ironclad / generic` | 8.8% | [7.8, 9.9] | **9.4%** | [8.4, 10.5] |
| `real_ironclad / generic` (floor) | 6.2% | [5.4, 7.2] | **6.5%** | [5.7, 7.5] |
| `real_silent / generic` (floor) | 1.3% | [1.0, 1.8] | **1.4%** | [1.0, 1.9] |

**Every arm's two intervals overlap.** No arm separated from its own `RT10`
value at n = 3000. The largest point movements are `ref_ironclad` +0.6 pp and
`klee/demolition` −0.4 pp, and both sit well inside their intervals.

That is a statement about this sample size and nothing else. It is **not** a
claim that the window changed nothing: the numbers are not the same numbers,
and per R68 the `RT10` column is archive regardless of how far it moved.

## 2. Act-1 clear rate, same cell

| arm | `RT10` act-1 | `RT11` act-1 | `RT11` 95% |
|---|---|---|---|
| `klee / demolition` | 84.3% | **84.3%** | [82.9, 85.5] |
| `klee / spark` | 80.9% | **80.9%** | [79.5, 82.3] |
| `klee / reaction` | 85.9% | **85.9%** | [84.6, 87.1] |
| `furina / salon` | 55.2% | **55.2%** | [53.4, 56.9] |
| `furina / spotlight` | 57.4% | **57.4%** | [55.6, 59.2] |
| `furina / fanfare` | 50.3% | **50.3%** | [48.5, 52.1] |
| `kokomi / priest` | 43.7% | **43.7%** | [41.9, 45.4] |
| `kokomi / commander` | 52.4% | **52.4%** | [50.6, 54.2] |
| `kokomi / assist` | 34.7% | **34.7%** | [33.0, 36.4] |
| `ref_ironclad / generic` | 71.1% | **71.1%** | [69.4, 72.7] |
| `real_ironclad / generic` | 70.9% | **70.9%** | [69.3, 72.5] |
| `real_silent / generic` | 59.3% | **59.3%** | [57.5, 61.0] |

Act-1 clear is unchanged to the printed precision on all twelve arms. Recorded
as measured. No inference is drawn from it here.

## 3. Shape columns, same cell

`acts` (mean acts cleared), `deck` (mean final deck size) and `fights` (mean
fights survived). Only the arms whose printed values moved are listed; the
other seven printed identically.

| arm | `acts` `RT10` → `RT11` | `deck` | `fights` |
|---|---|---|---|
| `klee / spark` | 1.06 → **1.05** | 24.4 → 24.4 | 14.7 → 14.7 |
| `furina / spotlight` | 0.71 → **0.70** | 21.6 → 21.6 | 11.0 → **10.9** |
| `furina / fanfare` | 0.63 → 0.63 | 19.9 → **19.8** | 10.2 → 10.2 |
| `kokomi / commander` | 0.70 → **0.69** | 22.3 → 22.3 | 10.7 → 10.7 |
| `ref_ironclad / generic` | 1.16 → **1.17** | 22.4 → 22.4 | 15.3 → **15.4** |
| `real_ironclad / generic` | 1.05 → **1.06** | 22.1 → 22.1 | 14.3 → **14.4** |

## 4. What is NOT comparable to this table

- **The 2026-08-08 twelve-arm read** (`review/records/sitting-reads-2026-08-08.md`),
  taken at `RT9/D14/P6/C8`. Three of the four stamp fields have moved since.
  It is archive and must not be diffed against either column above.
- **Any `RT10` roster number published elsewhere.** The `RT10` column here is
  reproduced so this file's own comparison is self-contained; it is not a
  licence to re-quote `RT10` going forward.
- **Both `real_*` anchors under `RT10` from any earlier source.** No such
  number was ever produced at this n — the arms crashed. The `RT10` anchor
  column above exists only because the two fixes were back-applied to the
  pre-window checkout for exactly this purpose.

## 5. Raw output

Both runs' full stdout, warnings included, is reproducible from the cell in the
table above. Nothing in this file is quoted from any run other than the two
named there.

---

# Part 2 — the `RT11/C9 → RT12/C10` re-take

## 6. Why part 2 exists, and the cell

Both stamp fields moved again on 2026-08-13, hours after part 1 was taken: the
window-2 correctness batch (`EB-104`, all twelve members) landed under one
coordinated bump — `RUNTEMPLATE` 11 → **12** for its five run-layer fixes and
`CONSTANTS` 9 → **10** for its seven tier0 engine fixes. Stamp law makes every
`RT11/D14/P7/C9` roster number archive at that commit (R68), so the table is
re-taken. Same script, same n, same seed, same cell in every other respect.

| | |
|---|---|
| branch | `overnight-burn-2026-08-12` |
| **before** column | the `RT11` column of part 1 — **not re-run**, see the note below |
| **after** HEAD | `18de3fe` — the window-2 stamp-bump commit, taken in the primary checkout |
| command | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| after cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D14/P7/C10` |
| route / policy / loadout | `hunter` / `assigned` / realistic, relics + potions, all registered acts |
| intervals | 95% Wilson (`tier05.stats.wilson95`), computed in-row by the script |
| errors | none — all twelve arms completed, zero tracebacks |

**Why the `RT11` column was not re-run.** Part 1's `RT11` read was taken at
`768dae6`. The window-2 merges began at `462013d`. `git diff --name-only
768dae6 462013d` returns five paths and **not one of them is Python**: two
register documents, part 1 of this file, and two `klee-mod` C# files that no
sim run reads. The pre-window sim is therefore byte-identical to the one part 1
measured, and re-running it would re-derive the same twelve rows from the same
seed. No spot-check was needed to establish that and none is claimed.

`game_ref/` was present, so both `real_*` anchors are live and no `ref_*`
substitution was needed. Both crash fixes disclosed in part 1 are present on
both sides of this comparison too, as they were on both sides of part 1's.

## 7. The twelve arms — run winrate

| arm | `RT11` win | `RT11` 95% | `RT12` win | `RT12` 95% |
|---|---|---|---|---|
| `klee / demolition` | 7.4% | [6.5, 8.4] | **6.4%** | [5.6, 7.4] |
| `klee / spark` | 3.9% | [3.3, 4.7] | **3.9%** | [3.3, 4.7] |
| `klee / reaction` | 6.4% | [5.5, 7.3] | **5.6%** | [4.8, 6.4] |
| `furina / salon` | 5.0% | [4.3, 5.8] | **3.9%** | [3.3, 4.7] |
| `furina / spotlight` | 1.0% | [0.7, 1.4] | **1.0%** | [0.7, 1.4] |
| `furina / fanfare` | 1.2% | [0.9, 1.7] | **1.1%** | [0.8, 1.6] |
| `kokomi / priest` | 1.0% | [0.7, 1.4] | **1.1%** | [0.8, 1.6] |
| `kokomi / commander` | 1.6% | [1.2, 2.1] | **1.5%** | [1.1, 2.0] |
| `kokomi / assist` | 0.4% | [0.2, 0.7] | **0.5%** | [0.3, 0.8] |
| `ref_ironclad / generic` | 9.4% | [8.4, 10.5] | **7.5%** | [6.6, 8.5] |
| `real_ironclad / generic` (floor) | 6.5% | [5.7, 7.5] | **5.5%** | [4.7, 6.3] |
| `real_silent / generic` (floor) | 1.4% | [1.0, 1.9] | **1.3%** | [0.9, 1.7] |

**Every arm's two intervals overlap**, as they did in part 1 — but two of them
only just: `ref_ironclad` overlaps on [8.4, 8.5] and `furina / salon` on
[4.3, 4.7]. Recorded as measured. The largest point movements are
`ref_ironclad` −1.9 pp, `furina / salon` −1.1 pp and `klee / demolition`
−1.0 pp. No arm separated from its own `RT11` value at n = 3000.

That is a statement about this sample size and nothing else, and no movement
here is attributed to any member of the batch. Per R68 the `RT11` column is
archive from this commit regardless of how far it moved.

## 8. Act-1 clear rate, same cell

| arm | `RT11` act-1 | `RT12` act-1 | `RT12` 95% |
|---|---|---|---|
| `klee / demolition` | 84.3% | **83.9%** | [82.6, 85.2] |
| `klee / spark` | 80.9% | **80.6%** | [79.2, 82.0] |
| `klee / reaction` | 85.9% | **85.2%** | [83.8, 86.4] |
| `furina / salon` | 55.2% | **53.6%** | [51.8, 55.4] |
| `furina / spotlight` | 57.4% | **55.4%** | [53.6, 57.2] |
| `furina / fanfare` | 50.3% | **48.6%** | [46.8, 50.4] |
| `kokomi / priest` | 43.7% | **42.3%** | [40.5, 44.0] |
| `kokomi / commander` | 52.4% | **51.3%** | [49.5, 53.1] |
| `kokomi / assist` | 34.7% | **33.8%** | [32.1, 35.5] |
| `ref_ironclad / generic` | 71.1% | **65.5%** | [63.8, 67.2] |
| `real_ironclad / generic` | 70.9% | **67.2%** | [65.5, 68.8] |
| `real_silent / generic` | 59.3% | **54.4%** | [52.6, 56.2] |

Unlike part 1, where act-1 clear was unchanged to the printed precision on all
twelve arms, every arm's act-1 clear is lower here, by 0.3 to 5.6 pp. Recorded
as measured; no inference is drawn from it in this file.

## 9. Shape columns, same cell

`acts` (mean acts cleared), `deck` (mean final deck size) and `fights` (mean
fights survived), all twelve arms at `RT12`.

| arm | `acts` | `deck` | `fights` |
|---|---|---|---|
| `klee / demolition` | 1.18 | 25.3 | 15.7 |
| `klee / spark` | 1.03 | 24.2 | 14.5 |
| `klee / reaction` | 1.17 | 21.7 | 15.5 |
| `furina / salon` | 0.78 | 21.5 | 11.4 |
| `furina / spotlight` | 0.67 | 21.3 | 10.7 |
| `furina / fanfare` | 0.60 | 19.6 | 9.9 |
| `kokomi / priest` | 0.52 | 21.0 | 9.1 |
| `kokomi / commander` | 0.66 | 22.0 | 10.4 |
| `kokomi / assist` | 0.39 | 19.7 | 7.9 |
| `ref_ironclad / generic` | 1.04 | 21.6 | 14.1 |
| `real_ironclad / generic` | 0.97 | 21.6 | 13.5 |
| `real_silent / generic` | 0.65 | 20.8 | 10.7 |

**No `RT11 → RT12` shape deltas are stated, and the omission is deliberate.**
§3 printed only the six arms whose shape values moved across `RT10 → RT11`, so
this document holds `RT11` shape values for six arms and not for the other six.
Stating a delta for half the table and a blank for the rest would read as
"unchanged" where the truth is "not on record here". The six that are on record
are `klee / spark` (1.05 / 24.4 / 14.7), `furina / spotlight`
(0.70 / 21.6 / 10.9), `furina / fanfare` (0.63 / 19.8 / 10.2),
`kokomi / commander` (0.69 / 22.3 / 10.7), `ref_ironclad`
(1.17 / 22.4 / 15.4) and `real_ironclad` (1.06 / 22.1 / 14.4); a reader who
wants the other six can re-derive them at `462013d`.

## 10. What is NOT comparable to this table

- Everything §4 already lists, unchanged.
- **The `RT10` column of §1**, which was already archive and is two stamp
  boundaries away from §7.
- **Any `RT11` roster number published elsewhere.** The `RT11` columns above
  are reproduced so this comparison is self-contained; that is not a licence to
  re-quote `RT11` going forward.
- **§4.7 shop-channel figures of any vintage.** `EB-102` changes which card
  `rng.choice` lands on in the shop, so the shop channel is renumbered by this
  window independently of anything in the table above.

## 11. Raw output

Both runs' full stdout, warnings included, is reproducible from the cells in
§6 and in the part-1 cell table. Nothing in this file is quoted from any run
other than those named there.
