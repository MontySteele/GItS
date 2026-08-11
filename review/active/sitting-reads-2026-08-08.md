# Sitting re-reads, 2026-08-08 — three published comparisons, re-taken under `RT9/D14/P6/C8`

> **Lifecycle: ACTIVE.** This is the evidence packet for the next [USER]
> sitting. It is descriptive only. It runs, records and reports. It recommends
> nothing and tunes nothing. Every call these numbers feed stays [USER]'s.

## Terms used here

- **The stamp.** A version label like `RT9/D14/P6/C8`. It says which version of
  the game world produced a number. Numbers from different stamps are not
  comparable. `RT9/D14/P6/C8` is the world that ships today.
- **Plan (also "arm").** One way to build a character's deck. Furina has salon,
  spotlight and fanfare. Kokomi has priest, commander, assist and generic.
- **Anchor.** A reference character we measure against. `real_ironclad` and
  `real_silent` are the two real Slay the Spire characters. `ref_ironclad` is a
  reference build of the Ironclad.
- **Floor.** An anchor's winrate used as a "must clear this" line.
- **95% interval.** The range a measured percentage could really be, given the
  sample size. Two intervals that do not overlap mean the difference is real at
  this sample size. Two that overlap mean we cannot tell them apart. All
  intervals here are Wilson intervals.
- **k/n.** How many runs were won, out of how many were played.
- **Structure HELD.** The shape of a result survived the world change: the same
  things are above and below each other, even though the raw percentages moved.
- **Act-1 clear.** The share of runs that finished act 1.
- **Cell.** The exact configuration a measurement was taken in — script, sample
  size, seed, and world stamp. Two numbers are only comparable if their cells
  match.

---

## Why this packet exists

Three QUEUE rows — `S4-G7`, `S4-G13` and `M9` — quote percentages that were
measured two or more stamp boundaries ago (`RT7→RT9`, `P3→P6`, `C6→C8`). Those
boundaries were declared to make the numbers not comparable to today's world.
Each row's own note says the numbers must be re-read before the sitting.

This is that re-read. Same table shape. Same sample size. Same seed. Same
recipe. Run against the world that ships today.

### Experiments-law check, done first

The standing rule says to check `EXPERIMENTS.md` before measuring. All three
reads here are descriptive re-reads of comparisons that were already published.
So none of them needs a new registration.

`EXPERIMENTS.md` limits pre-registration and blind grading to "a measurement
that a playtest will grade" (D5). None of these is graded by a playtest. Each is
a Monte-Carlo table, re-produced from an unchanged script, under a moved stamp.

The rule that *does* apply is the reason these are being re-run at all: "every
published number is world-stamped, and worlds are not comparable" (R68).

Nothing in this file is a registration, a grade, or a band.

### Two things deliberately not touched

**Quarantined columns.** The `core attain`, `core 95%` and `tto` columns of the
standing roster-anchor table are quarantined under `Q18` / `Q19`, R121, pending
the payoff-reach re-registration. `tier05/exp_roster_anchors` does not print
them. No quarantined quantity is read, quoted or reconstructed anywhere below.

**The `M9` meter bracket.** The bracket runs meter 10, 15, 20 and 25. Only
meter 20 is re-read here. Every other arm would require editing `burst_max` in
the ratified `tier0/content/characters/kokomi.yaml`. This packet changes no code
and no YAML, so only the **shipped** meter-20 arm is re-read.

---

## Where the fresh numbers came from

| | |
|---|---|
| branch / HEAD | `sitting-prep-2026-08-08` @ `170ac7b` |
| cell stamp | **`RT9/D14/P6/C8`** |
| §1 + §2 command | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| §1 + §2 cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT9/D14/P6/C8` |
| §3 command | `PYTHONPATH=. python -m tier05.runner --character kokomi --archetype <plan> --runs 500 --realistic --jobs 0` |
| §3 cell | `cell=cli seed=20260719 runs=500 RT9/D14/P6/C8` |
| intervals | 95% Wilson (`tier05.stats.wilson95`) |

Notes on that table:

- The stamp was read live via `tier05/cells.py`. `A6_INSTRUMENT_VERSION` is not
  read by anything here.
- The §1 and §2 runs used route `hunter`, policy `assigned`, a realistic loadout
  with relics and potions, and all registered acts.
- The §3 runs were one invocation per plan. `--seed` was omitted, so the seed is
  `C.DEFAULT_SEED = 20260719`, unchanged since the tag.
- The Wilson interval is the same one the prior tables used.
  `exp_roster_anchors` computes it in-row. `print_run_report` prints it for the
  run winrate.
- The `real_*` anchors are present and live. `game_ref/` is on this checkout
  (`game_ref/char_real_ironclad.yaml`, `char_real_silent.yaml`). Both anchor
  rows produced numbers, so no `ref_*` substitution was needed.
- `--jobs` affects wall-clock time only. Run *i* is a pure function of
  `seed + i`, so `--jobs 0` and `--jobs 1` give identical results
  (`runner.py:111-114`).

### The post-EB-57 / EB-58 label

This label applies to every number in this file.

All three reads were taken **after** two instrument fixes, at commit `170ac7b`:

- `EB-57` — the reaction amplification counter was re-settled as realized
  uplift.
- `EB-58` — aura-uptime intervals are now cut off at the target's death.

That commit declares non-comparability for one family of quantities:
`reaction_damage_amp`, `reaction_damage`, `damage_from_base_ops`,
`reaction_share` and `reaction_damage_share`. It also declares it for
`aura_telemetry` uptime. It states that fights are otherwise bit-identical. A
120-fight battery gave identical wins, reactions, total damage and aura
applications before and after the fix.

**No quantity in this file belongs to either moved family.** The quantities here
are winrates, act-1 clear rates, acts, deck size and fights.

The label is carried anyway, as instructed, so that no reader has to work out
which side of the fix a number sits on.

No stamp moved at that commit. It was an instrument fix, not a world change.

---

## 1. `S4-G7` — Furina: three plans or one

**The prior read.** `docs/current/roster/roster-anchor-v14-v6-2026-08-06.md`,
the quotable standing table (R118, queue row 10.2). n=3000, seed 20260729, stamp
**`RT7/D14/P3/C6`**, same twelve-arm recipe.

**What claim is being tested.** In the row's own words: salon versus spotlight
and fanfare, with non-overlapping intervals; and fanfare still overlapping the
`real_silent` floor.

One clarification on that wording. In the prior table, spotlight and fanfare had
the same point estimate and the same interval. So "non-overlapping" describes
salon's separation from both of them. It does not describe any separation
between spotlight and fanfare.

| arm | prior win `RT7/D14/P3/C6` | prior 95% | fresh win `RT9/D14/P6/C8` | fresh 95% | fresh k/n |
|---|---|---|---|---|---|
| `furina / salon` | **11.20%** | [10.1, 12.4] | **4.70%** | [4.00, 5.52] | 141/3000 |
| `furina / spotlight` | **2.23%** | [1.8, 2.8] | **1.50%** | [1.12, 2.00] | 45/3000 |
| `furina / fanfare` | **2.23%** | [1.8, 2.8] | **1.30%** | [0.95, 1.77] | 39/3000 |
| `real_silent / generic` (floor) | 1.70% | [1.3, 2.2] | **1.37%** | [1.01, 1.85] | 41/3000 |
| `real_ironclad / generic` (floor) | 8.53% | [7.6, 9.6] | **6.13%** | [5.33, 7.05] | 184/3000 |
| `ref_ironclad / generic` | 13.83% | [12.6, 15.1] | **9.40%** | [8.41, 10.50] | 282/3000 |

Act-1 clear rates from the same cell, for completeness: salon 54.33%
[52.55, 56.11], spotlight 55.50% [53.72, 57.27], fanfare 47.67% [45.88, 49.46],
`real_silent` 58.93% [57.16, 60.68], `real_ironclad` 69.93% [68.27, 71.55]. The
prior values were 60.60 / 59.57 / 58.17 / 60.90 / 69.87.

**Which intervals overlap on the fresh read.**

- salon [4.00, 5.52] against spotlight [1.12, 2.00] — **no overlap**.
- salon [4.00, 5.52] against fanfare [0.95, 1.77] — **no overlap**.
- spotlight [1.12, 2.00] against fanfare [0.95, 1.77] — they overlap. They also
  overlapped on the prior read, where the two were identical.
- fanfare [0.95, 1.77] against `real_silent` [1.01, 1.85] — they **overlap**.

### Structure: HELD

Salon separates from both other plans at this sample size. Fanfare still sits on
the `real_silent` floor, with overlapping intervals.

The magnitudes fell across the boundary. Salon went from 11.20% to 4.70%. The
whole table fell with it: `ref_ironclad` dropped from 13.83 to 9.40, and
`real_ironclad` from 8.53 to 6.13.

### One ordering fact MOVED

This is recorded because it is a fact about the same columns. It is not a
recommendation.

On the prior table, `furina/salon` at 11.20% sat **above** `real_ironclad` at
8.53%, with no interval overlap. On the fresh read, `furina/salon` at 4.70%
[4.00, 5.52] sits **below** `real_ironclad` at 6.13% [5.33, 7.05], again with no
interval overlap.

`ref_ironclad` at 9.40% remains alone at the top, as it was after the 2026-08-06
republication.

Spotlight [1.12, 2.00] also overlaps the `real_silent` floor on this read. It
overlapped it on the prior read too: [1.8, 2.8] against [1.3, 2.2].

---

## 2. `S4-G13` — Kokomi below the Ironclad-anchored floor

**The prior read.** The same standing table, same recipe, n=3000, seed 20260729,
stamp **`RT7/D14/P3/C6`**.

**What claim is being tested.** In the row's own words: priest, commander and
assist all below `real_ironclad`; assist below even the `real_silent` floor;
non-overlapping.

| arm | prior win `RT7/D14/P3/C6` | prior 95% | fresh win `RT9/D14/P6/C8` | fresh 95% | fresh k/n |
|---|---|---|---|---|---|
| `kokomi / priest` | **2.47%** | [2.0, 3.1] | **1.10%** | [0.78, 1.54] | 33/3000 |
| `kokomi / commander` | **3.00%** | [2.4, 3.7] | **2.20%** | [1.73, 2.79] | 66/3000 |
| `kokomi / assist` | **0.63%** | [0.4, 1.0] | **0.57%** | [0.35, 0.91] | 17/3000 |
| `real_ironclad / generic` (floor) | **8.53%** | [7.6, 9.6] | **6.13%** | [5.33, 7.05] | 184/3000 |
| `real_silent / generic` (floor) | 1.70% | [1.3, 2.2] | **1.37%** | [1.01, 1.85] | 41/3000 |

Act-1 clear rates from the same cell: priest 42.20% [40.44, 43.98], commander
51.83% [50.04, 53.62], assist 35.37% [33.68, 37.10]. The prior values were
42.83 / 51.33 / 35.30.

**Which intervals overlap on the fresh read.**

- priest [0.78, 1.54], commander [1.73, 2.79] and assist [0.35, 0.91] — each
  upper bound lies **below** `real_ironclad`'s lower bound of 5.33. All three
  fail to overlap the Ironclad floor.
- assist [0.35, 0.91] against `real_silent` [1.01, 1.85] — **no overlap**.
  Assist is below the Silent floor.

### Structure: HELD

All three plans remain below the `real_ironclad` floor, with no interval
overlap. Assist remains below even the `real_silent` floor, with no interval
overlap.

The magnitudes moved down with the rest of the table. The gap to the Ironclad
floor did not close.

Two further facts, recorded as facts and not as claims the row makes. First,
priest [0.78, 1.54] now overlaps the `real_silent` floor [1.01, 1.85]. It
overlapped it on the prior read too: [2.0, 3.1] against [1.3, 2.2]. Second, the
act-1 clear rates are essentially unmoved across the boundary, within a point on
all three plans, even though the run winrates fell.

---

## 3. `M9` — Kokomi meter 20, the 500-run confirm

**The prior read.** `docs/archive/kokomi-v0.4-report.md` §2.3, the "500-run
confirm at meter 20". It is retrievable at tag `pre-simplification-2026-08-06`.

That report's §0 fixes the measurement convention: `--realistic` runs, 500 runs,
default seed, invoked as
`python -m tier05.runner --character kokomi --archetype <plan> --runs 500 --realistic`.
Its world predates the stamp: `RT7/D14/P3/C6` and earlier.

**What "meter 20" means.** It is `burst_max: 20` in
`tier0/content/characters/kokomi.yaml`. The v0.4 O4 salvage moved it from 10 to
20, and 20 is the shipped value today. The quantity the 500-run confirm reports
is the act-1 clear rate and the run winrate of Kokomi's four plans under that
meter. §6 ask 2 is the ratification: "Meter 20 ratification on the 500-run
confirm."

### The old comparison column is dead, and was not replaced

§2.3's right-hand column was "vs W1 baseline". That baseline is the v0.3 world:
a different `burst_max`, a pre-rework starter, and an engine from before `RT9`
and `C8`.

The QUEUE row's own note says that comparator was self-declared superseded at
the tag. Reproducing it would mean editing ratified content YAML, which this
packet does not do.

§6 ask 2 offers an alternative comparator — "or name meter 15" — but that has
the same problem. Meter 15 is not a shipped world either.

**So the meter-20 quantity is re-read on its own. No comparator is invented.**

| plan | prior act-1 `RT7`-and-earlier | prior run | fresh act-1 `RT9/D14/P6/C8` | fresh run | fresh 95% (Wilson) | fresh k/n |
|---|---|---|---|---|---|---|
| `priest` | 30% | 0.6% | **41%** | **1.4%** | [0.7, 2.9] | 7/500 |
| `commander` | 45% | 1.4% | **50%** | **2.2%** | [1.2, 3.9] | 11/500 |
| `generic` | 26% | 0.4% | **42%** | **1.0%** | [0.4, 2.3] | 5/500 |
| `assist` | 24% | 0.2% | **34%** | **0.4%** | [0.1, 1.4] | 2/500 |

Two notes on that table. Act-1 clear is the `act funnel` line's "act1 reached
100% cleared N%" — the same integer-percent quantity the v0.4 table printed. The
prior table carried no intervals; the fresh ones are the Wilson intervals that
`print_run_report` now prints for the run winrate.

**What claim is being tested.** It is the one §2.2 and §2.3 rest the meter-20
choice on: at meter 20, the priest and commander act-1 clear rates sit in the
pre-registered 35–50% acceptance band, and no plan's run winrate is more than a
couple of points. On the original 500-run confirm, priest read 30%, below the
band's lower edge, with commander at 45% inside it.

### Structure: HELD, and priest moved INTO the band

On the fresh read, commander at 50% sits at the band's upper edge. Priest at 41%
sits inside the band, where it was below the band on the original confirm. Every
plan's run winrate stays at or under 2.2%.

The band membership that the meter-20 choice was made on is intact under the
current stamp. The one movement is priest rising from below the band into it.

The `generic` plan rose most, from 26% to 42% act-1 clear. Assist rose from 24%
to 34%, which is just under the band's lower edge.

### Caveat carried forward

Ratifying meter 20 against *this* read is a one-sided comparison.

§6 ask 2 asks [USER] to confirm a specific trade: "the arm costs ~3–4 act-1
points and priest run winrate vs v0.3". That trade cannot be re-read without
rebuilding the v0.3 world. Rebuilding it is a content change, not a measurement.

Whether that matters is [USER]'s call.

---

## How to reproduce these numbers

```sh
# §1 + §2 — the twelve-arm standing-table recipe, 2m23s wall clock
PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729

# §3 — one invocation per plan
for p in priest commander generic assist; do
  PYTHONPATH=. python -m tier05.runner --character kokomi --archetype $p \
      --runs 500 --realistic --jobs 0
done
```

Full sample size was used for every read. Nothing was reduced.

The two-decimal figures and the `k/n` counts in §1 and §2 come from a throwaway
harness. That harness derives the identical cells
(`cells.CANONICAL.but(name="roster-anchors").but(jobs=0, runs=3000,
seed=20260729).but(character=…, archetype=…).arm()`) and prints more digits. Its
rows agree with the committed script's one-decimal output, row for row.

No file in the repository was modified to take any of these readings.
