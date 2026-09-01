Status: RECORD

# Standing roster re-baseline, 2026-08-24 — the `C13`/`D16` world

> **Lifecycle: ACTIVE.** This is the re-baseline the `EB-118` Phase-2
> integration window owes — the one `CONSTANTS_VERSION` 12 deliberately
> deferred, plus the one `DRAFTER_VERSION` 15 → 16 asks for, taken ONCE for
> both because both fields moved in the same window. It is descriptive only.
> It runs, records and reports. It recommends nothing, tunes nothing, and
> reads nothing into the numbers. Every call these numbers feed stays
> [USER]'s.

> **This table supersedes `review/records/sitting-reads-2026-08-24.md` as the
> standing read.** That file is not rewritten and not struck: it is a
> published record of the `D14 → D15` window and stands as published (R101b).
> Both of its columns are `C11` readings and both are archive now.

> **IT IS TEN ARMS, NOT TWELVE, AND THE SHORTFALL IS AN INSTRUMENT LOSS.**
> `real_ironclad` and `real_silent` could not be run at all — not "moved", not
> "substituted": the gitignored `game_ref/` tree was destroyed on this machine
> for a fourth time and the loader cannot construct either character. §5 has
> the evidence and the consequences; the defect is BACKLOG `EB-128`.

## Terms used here

Unchanged from the 2026-08-13 and 2026-08-24 packets, and repeated so this
file is readable on its own.

- **The stamp.** A version label like `RT12/D16/P7/C13`. It says which version
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

---

## Why this packet exists

Two stamp fields moved on 2026-08-24 in one integration window:

- **`CONSTANTS_VERSION` 12 → 13.** Every material sheet and engine edit that
  reached `main` after C12 was stamped: Phase 2B's two `big_badda_boom` PRs,
  door (a)'s twelve `place_bomb` row conversions, door (b)'s Explosives
  Workshop conversion *and its new engine power* `bomb_damage_per_rotation`,
  door (c)'s `lasting_impression`, and Phase 2C's landed `deep_breath`
  content. C12's own note deferred this table in terms — "two of the three
  staged items move Klee combat numbers again the moment they are pulled" —
  and that deferral bought exactly this: one table after the landings instead
  of one before and one after.
- **`DRAFTER_VERSION` 15 → 16.** The two inert drafter terms going live.
  `STATIC_ETHEREAL_SHARE` now moves a real drafted price
  (`big_badda_boom` 8.0000 → 4.8000); `choose_one`'s MAX arbitration is
  reachable from a shipped card and moves none.

Stamp law says every published number is world-stamped and worlds are not
comparable (R68), so every `C11`/`D15` roster number became archive at those
commits. This is the re-take.

### Experiments-law check, done first

Same check the two prior packets made, same answer. This is a descriptive
re-read of an already-published comparison, re-produced from an unchanged
script under a moved stamp. `EXPERIMENTS.md` limits pre-registration and blind
grading to a measurement a playtest will grade (D5); no playtest grades this.
Nothing in this file is a registration, a grade or a band. The rule that makes
the re-run necessary at all is R68.

### What is deliberately not here

**The core-attainment columns.** `core attain`, `core 95%` and `tto` are not
printed, for the same tooling reason as on 2026-08-13 and 2026-08-24:
`tier05/exp_roster_anchors` has never printed them. Restoring them is a
separate build.

**Commentary.** Movements are stated as old value, new value and both
intervals. No claim is made about why any arm moved.

---

## The cell

The `before` column is **quoted, not re-run** — and this is the one place this
packet differs from its predecessor's method, deliberately and for a stated
reason. The 2026-08-24 `D15` column was taken at `RT12/D15/P7/C11` by the same
script, same seed, same n, same route, same loadout, four hours earlier on this
machine, and **nothing has moved inside `C` or `D` since it was taken except
the contents of this window**. Its predecessor had to re-run its before column
because two unlabelled things (`C10 → C11` and the `EB-69` fill) sat between
the two worlds; here there is exactly one window between them and it is the
window under study. Re-running it is also no longer possible in the shape it
was taken: `game_ref/` is gone (§5), so the two `real_*` rows of that column
cannot be reproduced by anyone on this machine today.

| | |
|---|---|
| branch | `phase2-cd-close` (worktree `../GItS-close`) |
| **before** | `review/records/sitting-reads-2026-08-24.md` §§1–3, `D15` columns, HEAD `499186b` |
| **after** HEAD | `phase2-cd-close` at the `D16` stamp commit |
| command (both) | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| before cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D15/P7/C11` |
| after cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D16/P7/C13` |
| route / policy / loadout | `hunter` / `assigned` / realistic, relics + potions, all registered acts |
| intervals | 95% Wilson (`tier05.stats.wilson95`), computed in-row by the script |
| errors | **ten arms completed; arm 11 (`real_ironclad`) raised `KeyError: 'real_ironclad'` and the run stopped there.** See §5. |

Notes on that table:

- Both stamps were read live via `tier05/cells.py`, never hand-written. The
  header of this run reads `RT12/D16/P7/C13`, which is the whole point of
  taking it after the stamp commits rather than before them.
- The two runs differ in **`CONSTANTS_VERSION`, `DRAFTER_VERSION` and the
  content those two label** — same script, same seed, same n, same route, same
  loadout, same machine. `--jobs` is wall-clock only; run *i* is a pure
  function of `seed + i`.
- The `before` run had `game_ref/` present; this one did not. **§5.2 shows
  that this is not a term in any of the ten rows**, and shows it with data
  rather than by argument.

---

## 1. The ten arms — run winrate

| arm | `C11/D15` win | `C11/D15` 95% | `C13/D16` win | `C13/D16` 95% | Δ |
|---|---|---|---|---|---|
| `klee / demolition` | 6.4% | [5.6, 7.4] | **5.8%** | [5.0, 6.7] | −0.6 pp |
| `klee / spark` | 3.9% | [3.3, 4.7] | **4.2%** | [3.5, 4.9] | +0.3 pp |
| `klee / reaction` | 5.6% | [4.8, 6.4] | **6.4%** | [5.5, 7.3] | +0.8 pp |
| `furina / salon` | 3.9% | [3.3, 4.7] | **3.7%** | [3.1, 4.4] | −0.2 pp |
| `furina / spotlight` | 1.4% | [1.1, 1.9] | **1.3%** | [1.0, 1.8] | −0.1 pp |
| `furina / fanfare` | 1.1% | [0.8, 1.6] | **0.8%** | [0.6, 1.2] | −0.3 pp |
| `kokomi / priest` | 0.7% | [0.5, 1.1] | **0.7%** | [0.5, 1.1] | — |
| `kokomi / commander` | 1.9% | [1.4, 2.4] | **1.9%** | [1.4, 2.4] | — |
| `kokomi / assist` | 0.2% | [0.1, 0.4] | **0.2%** | [0.1, 0.4] | — |
| `ref_ironclad / generic` | 7.5% | [6.6, 8.5] | **7.5%** | [6.6, 8.5] | — |
| `real_ironclad / generic` (floor) | 5.5% | [4.7, 6.3] | *not run* | — | — |
| `real_silent / generic` (floor) | 1.3% | [0.9, 1.7] | *not run* | — | — |

**Six arms moved and four printed identically on every column.** The four that
did not move are the three Kokomi arms and `ref_ironclad` — which is the
window's own control, stated in advance at the C13 stamp and reported here
rather than asserted: nothing in (a)–(f) touches Kokomi's sheet or her engine
path, and `ref_ironclad` is built from committed sheets that this window did
not edit.

**No arm separated from its own prior value at n = 3000.** Every moved row's
two intervals overlap, including the largest mover (`klee / reaction`, whose
[4.8, 6.4] and [5.5, 7.3] share [5.5, 6.4]).

Per R68 the `C11/D15` column is archive from these commits regardless of how
far any row moved, including the four that did not move at all.

## 2. Act-1 clear rate, same cell

| arm | `C11/D15` act-1 | `C13/D16` act-1 | `C13/D16` 95% | Δ |
|---|---|---|---|---|
| `klee / demolition` | 83.9% | **83.1%** | [81.7, 84.4] | −0.8 pp |
| `klee / spark` | 80.6% | **79.9%** | [78.4, 81.3] | −0.7 pp |
| `klee / reaction` | 85.2% | **86.0%** | [84.7, 87.2] | +0.8 pp |
| `furina / salon` | 53.6% | **52.8%** | [51.0, 54.6] | −0.8 pp |
| `furina / spotlight` | 59.4% | **59.1%** | [57.3, 60.8] | −0.3 pp |
| `furina / fanfare` | 48.6% | **45.6%** | [43.8, 47.4] | −3.0 pp |
| `kokomi / priest` | 39.9% | **39.9%** | [38.2, 41.7] | — |
| `kokomi / commander` | 49.7% | **49.7%** | [47.9, 51.5] | — |
| `kokomi / assist` | 32.2% | **32.2%** | [30.6, 33.9] | — |
| `ref_ironclad / generic` | 65.5% | **65.5%** | [63.8, 67.2] | — |
| `real_ironclad / generic` | 67.2% | *not run* | — | — |
| `real_silent / generic` | 54.4% | *not run* | — | — |

`furina / fanfare` is the largest single movement anywhere in the table at
−3.0 pp. **It has not separated:** its prior interval was [46.8, 50.4] and its
new one is [43.8, 47.4], which share [46.8, 47.4]. That is a narrow overlap
and it is still an overlap; no separation is claimed and none is available at
this n.

## 3. Shape columns, same cell

`acts` (mean acts cleared), `deck` (mean final deck size), `fights` (mean
fights survived). Prior values are given beside any that moved.

| arm | `acts` | `deck` | `fights` |
|---|---|---|---|
| `klee / demolition` | 1.18 → **1.14** | 25.3 → **24.9** | 15.7 → **15.3** |
| `klee / spark` | 1.03 → **1.04** | 24.2 → **24.1** | 14.5 → **14.4** |
| `klee / reaction` | 1.17 → **1.19** | 21.7 → **21.8** | 15.5 → **15.6** |
| `furina / salon` | 0.78 → **0.76** | 21.5 → **21.3** | 11.4 → **11.2** |
| `furina / spotlight` | 0.73 → **0.72** | **21.8** | **11.2** |
| `furina / fanfare` | 0.60 → **0.55** | 19.6 → **19.1** | 9.9 → **9.4** |
| `kokomi / priest` | **0.47** | **20.7** | **8.7** |
| `kokomi / commander` | **0.64** | **21.8** | **10.2** |
| `kokomi / assist` | **0.35** | **19.4** | **7.5** |
| `ref_ironclad / generic` | **1.04** | **21.6** | **14.1** |

## 4. The blast radius, recorded because it is checkable and it checked

The C13 stamp claims Kokomi is untouched by this window and says so as a
prediction the table would test rather than as a fact the table would
illustrate. It holds exactly: all three Kokomi arms print their prior values
on all five columns, to the printed precision.

`ref_ironclad` holds too, on all five columns. That matters for two separate
reasons and they should not be conflated: it is the **anchor-identity check**
this re-baseline owed, and it is also half the evidence in §5.2.

The six arms that moved are the six the window edits reach — three Klee arms
(door (a)'s twelve rows, door (b)'s new power, 2B's card) and three Furina
arms (door (c), 2C's `deep_breath`, and Phase 1's landed Fanfare work
carrying through). No claim is made here about which edit moved which arm, and
no claim is made that any of these movements is good, bad or meaningful: six
point estimates moved, none of them separated, and that is the whole finding.

## 5. What could not be measured, and what that costs

### 5.1 The two `real_*` anchor rows

The run reached arm 11 and stopped:

```
  File "tier0/content/loader.py", line 636, in starting_deck
    spec = _character_index()[character_id]
KeyError: 'real_ironclad'
```

`real_ironclad` and `real_silent` are built from the gitignored `game_ref/`
tree. That directory exists on this machine and is **empty**: it was destroyed
at approximately 17:15 on 2026-08-24, the fourth such loss on record
(2026-07-23, 2026-07-25, 2026-08-05, and now). The loader is fail-open on
total absence by design — a fresh clone simply has no reference characters —
so the two rows do not become wrong, they become **absent**, and the script
raises rather than substituting anything.

**It is not recoverable on this machine.** Of the thirteen hand-authored,
explicitly NOT tool-regenerable pass layers plus five `*_char_facts.yaml`, a
whole-user-profile search found exactly two survivors
(`~/Downloads/ironclad_pool_pass5.yaml`, `~/Downloads/ironclad_pool_pass6.yaml`).
`game_ref/` has never been committed (`.gitignore`, public repo, decompiled
reference material), so `git log --all -- 'game_ref/*'` is empty and history
cannot restore it. The two known scratchpad `game_ref_backup/` directories are
both empty. Filed as BACKLOG `EB-128`; restoring it needs data only [USER]
has, and the durable-backup question the incident keeps raising is in that
row.

**What the absence costs this table, precisely:** the two roster **floors** are
missing. `real_ironclad / generic` 5.5% and `real_silent / generic` 1.3% were
the numbers every roster arm is read against, and nothing in this packet
replaces them. `ref_ironclad` is not a substitute for either — it is a
reference *build* from committed sheets, not the real character — and no
comparison in this file uses it as one.

### 5.2 Why the absence is not a term in the ten rows that DID run

This needs evidence rather than assurance, because the `before` column was
taken with `game_ref/` present and this one was taken without it.

**The evidence is the four unchanged rows.** `ref_ironclad / generic` and all
three Kokomi arms print their prior values on all five columns — winrate,
act-1 and the three shape values — across a boundary at which `game_ref/`
went from present to absent. If the reference tree's presence perturbed
sequencing, pool construction or any RNG stream those arms consume, those
twelve numbers could not have reproduced. They did.

This is a statement about these ten arms in this cell. It is not a general
claim that `game_ref/` never matters: it demonstrably matters to
`real_ironclad` and `real_silent`, which is why they are absent, and the
loader's own index size differs with it (`test_content_boundaries`).

## 6. What is NOT comparable to this table

- **Both columns of `review/records/sitting-reads-2026-08-24.md`.** Its `D14`
  column was already archive; its `D15` column is quoted above as the
  `before` and is archive from this bump. Quoting it above is what makes this
  file's comparison self-contained; it is not a licence to re-quote `D15`
  going forward.
- **Every column of `review/records/sitting-reads-2026-08-13.md`** (`C10`,
  `D14`) and **`review/records/sitting-reads-2026-08-08.md`** (`RT9/D14/P6/C8`).
- **The roster-anchor standing table**
  (`docs/current/roster/roster-anchor-v14-v6-2026-08-06.md`), `RT7/D14/P3/C6`.
  Its `RA-G1`/`RA-G2`/`tto` quarantine lifted on 2026-08-24, which restores
  those columns as *readable*; it does not make a `C6`/`D14` reading
  comparable with anything here.
- **Every number published by the payoff-reach registration**, a `D14` read.
  The grade itself stands as published (R101b) and is never re-run against a
  later world.
- **The `W4` weight-sweep figures**, stamped `RT12/D15/P8/C12` — a `P8`
  sandbox world that no shipped cell has ever been in.
- **§4.7 shop-channel figures of any vintage**, unchanged from the 2026-08-13
  packet's note.

## 7. Raw output

The run's full stdout is reproduced in §§1–3 row for row; its stderr is the
relic-skip `UserWarning` block every run of this script emits, plus the §5.1
traceback. Nothing in this file is quoted from any run other than the one
named in the cell table.

---

## 8. Addendum — 2026-08-24: the two floor arms, run

> **This section ADDS the two rows §5.1 could not run. It rewrites nothing.**
> Every number in §§1–3 stands exactly as published (R101b) — including the
> two `*not run*` cells, which are a true record of what that run did. This
> addendum is a second, later run of the same script in the same cell, and it
> is labeled as such rather than merged into the tables above.

### 8.1 Why it is runnable now

`game_ref/` was restored on 2026-08-24, after §5 was written: [USER] supplied
an other-local worktree backup (fourteen files), and the derived half was
regenerated through `tools.extract_base_game_pool` + `tools.build_official_sheet`.
Both pools rebuild and both verify — **ironclad 76 cards, silent 87** — and
`real_ironclad` / `real_silent` load again.

Two further derived artifacts had to be re-derived after the anchors loaded,
each of which announced itself only as a `FileNotFoundError`:
`game_ref/role_tempo_canon.json` (`tools.canon_role_tempo`, five canon pools)
and the `defect` / `necrobinder` / `regent` extractor pools
(`tools.extract_base_game_pool`). The canon regeneration doubles as an
integrity check on the restore and it passed: the tool rewrites two COMMITTED
docs beside its local artifact and **both came back byte-identical**. The
primary checkout's suite is green with **zero skips** (3199 passed).

BACKLOG `EB-128` NARROWS on that restore rather than closing: three
`*_char_facts.yaml` (`defect`, `necrobinder`, `regent`) are still missing —
the only file class the restore could not produce, and nothing reads them
today — the durable-backup location is still [USER]'s call, and the guard
against the destroyer is still owed.

**One repair was needed before the run and it is disclosed here, not buried.**
The recovered `silent_pool_pass2.yaml` predates `EB-71`/R174 and still printed
`sly_keyword: true` on `si_haze`, a field the loader now refuses — so the tree
passed `--verify` and still could not be loaded. `--verify` is a CONSISTENCY
check (does the on-disk pool match a rebuild from its own inputs), not a
CURRENCY check (does the vocabulary those inputs print still exist). The repair
is the migration the retirement message itself prescribes,
`sly_keyword: true` → `sly: [{op: sly_autoplay}]`, and `test_real_silent`'s
pinned count of seven `sly_autoplay` cards is what says it is complete: six came
from the extractor, `si_haze` is the seventh. **Nothing was fabricated, stubbed
or approximated** — one row's field name was migrated, and no number, cost,
rarity or effect moved.

### 8.2 The cell

Identical to §"The cell" in every field, and taken on the primary checkout at
`main` = `4fee4a6` (PR #72, the `C13`/`D16` merge) — which is the same world the
`after` column was taken in.

| | |
|---|---|
| checkout | primary (`game_ref/` is primary-local and gitignored; a worktree cannot see it) |
| HEAD | `main` at `4fee4a6` |
| command | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT12/D16/P7/C13` |
| route / policy / loadout | `hunter` / `assigned` / realistic, relics + potions, all registered acts |
| arms | **all twelve completed**; no arm raised |

The script has no arm selection — `ARMS` is a module constant — so the full
twelve ran. That is a free integrity check and it is reported in §8.4.

### 8.3 The two floors

| arm | `C11/D15` win | `C13/D16` win | `C13/D16` 95% | Δ |
|---|---|---|---|---|
| `real_ironclad / generic` (floor) | 5.5% | **5.5%** | [4.7, 6.3] | — |
| `real_silent / generic` (floor) | 1.3% | **1.3%** | [0.9, 1.7] | — |

| arm | `C11/D15` act-1 | `C13/D16` act-1 | `C13/D16` 95% | Δ |
|---|---|---|---|---|
| `real_ironclad / generic` | 67.2% | **67.2%** | [65.5, 68.8] | — |
| `real_silent / generic` | 54.4% | **54.4%** | [52.6, 56.2] | — |

Shape columns, same cell: `real_ironclad` **0.97 / 21.6 / 13.5**,
`real_silent` **0.65 / 20.8 / 10.7** (acts / deck / fights).

**They did not separate — they did not move at all.** Both floors print their
prior `C11/D15` values on both rate columns to the printed precision, so they
join `ref_ironclad` and the three Kokomi arms as the window's control set
rather than as movers. That is what the C13 stamp predicts of them and it is
reported rather than asserted: `real_ironclad` and `real_silent` are built from
`game_ref/`, which no edit in this window touches.

**The roster therefore has its floors back.** `real_ironclad / generic` 5.5%
and `real_silent / generic` 1.3% are the numbers every roster arm is read
against, and §5.1's recorded cost — "the roster has no floors" — is paid off at
these two values.

### 8.4 The other ten arms reproduced, exactly

Because the script runs all twelve, this addendum re-took the ten rows §§1–3
already publish. **All ten reproduce to the printed precision on all five
columns** — winrate, act-1 and the three shape values — against the `C13/D16`
column above them.

Two things follow, and they are different claims:

- **The addendum is in the same cell as the table it completes.** Two floor
  rows appended to a table taken separately would otherwise be an assumption;
  here it is a measurement.
- **`game_ref/`'s PRESENCE is not a term in the ten rows either.** §5.2 showed
  the absence was not a term, using the four unchanged arms. This run closes
  the other direction: the same ten rows reproduce with the tree present. The
  two readings together bracket it — the reference tree matters to
  `real_ironclad` and `real_silent`, and to nothing else in this table.

Nothing in §§1–7 is edited on the strength of this. The published run is the
published run; this is a later run that agrees with it.
