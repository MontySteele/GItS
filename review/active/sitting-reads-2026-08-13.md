# Standing roster re-baseline, 2026-08-13 — the twelve-arm table across `RT10 → RT11`

> **Lifecycle: ACTIVE.** This is the re-baseline the `RUNTEMPLATE` 10 → 11 bump
> owes. It is descriptive only. It runs, records and reports. It recommends
> nothing, tunes nothing, and reads nothing into the numbers. Every call these
> numbers feed stays [USER]'s.

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

- **The 2026-08-08 twelve-arm read** (`review/active/sitting-reads-2026-08-08.md`),
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
