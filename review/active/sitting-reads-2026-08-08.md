# Sitting re-reads, 2026-08-08 — three published comparisons, re-taken under `RT9/D14/P6/C8`

> **Lifecycle: ACTIVE** — the evidence packet for the next [USER] sitting.
> Descriptive only. It runs, records and reports; it recommends nothing and
> tunes nothing. Every call these numbers feed stays [USER]'s.

## Why this exists

Three QUEUE rows — `S4-G7`, `S4-G13`, `M9` — quote percentages taken two or
more declared-uncomparable stamp boundaries back (`RT7→RT9`, `P3→P6`,
`C6→C8`), and each row's own note says the numbers must be re-read before the
sitting. This is that re-read: the **same table shape, the same n, the same
seed, the same recipe**, run against the world that ships today.

**EXPERIMENTS-law check (done first, per the standing rule).** All three are
**descriptive re-reads of already-published comparisons**, so none needs a new
registration. `EXPERIMENTS.md` fences pre-registration and blind grading to
*"a measurement that a playtest will grade"* (D5) — none of these is graded by
a playtest; each is a Monte-Carlo table re-produced from an unchanged script
under a moved stamp. The stamp law that *does* apply is the reason they are
being re-run at all: *"every published number is world-stamped, and worlds are
not comparable"* (R68). Nothing here is a registration, a grade, or a band.

**Two things deliberately NOT touched.**

- The `core attain` / `core 95%` / `tto` columns of the standing roster-anchor
  table are **QUARANTINED** (`Q18`/`Q19`, R121) pending the payoff-reach
  re-registration. `tier05/exp_roster_anchors` does not print them, and no
  quarantined quantity is read, quoted or reconstructed anywhere below.
- The `M9` meter bracket (meter 10 / 15 / 20 / 25) is **not** re-read: every
  non-20 arm would require editing `burst_max` in the ratified
  `tier0/content/characters/kokomi.yaml`. This packet changes no code and no
  YAML, so only the **shipped** meter-20 arm is re-read.

## Provenance of the fresh numbers

| | |
|---|---|
| branch / HEAD | `sitting-prep-2026-08-08` @ `170ac7b` |
| cell stamp | **`RT9/D14/P6/C8`** (read live via `tier05/cells.py`; `A6_INSTRUMENT_VERSION` is not read by anything here) |
| §1 + §2 command | `PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729` |
| §1 + §2 cell | `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT9/D14/P6/C8` — route `hunter`, policy `assigned`, realistic loadout (relics + potions), all registered acts |
| §3 command | `PYTHONPATH=. python -m tier05.runner --character kokomi --archetype <plan> --runs 500 --realistic --jobs 0` (one invocation per plan) |
| §3 cell | `cell=cli seed=20260719 runs=500 RT9/D14/P6/C8` (`--seed` omitted ⇒ `C.DEFAULT_SEED = 20260719`, unchanged since the tag) |
| intervals | **95% Wilson** (`tier05.stats.wilson95`) — the same one the prior tables used; `exp_roster_anchors` computes it in-row, `print_run_report` prints it for the run winrate |
| `real_*` anchors | **present and live.** `game_ref/` is on this checkout (`game_ref/char_real_ironclad.yaml`, `char_real_silent.yaml`); both anchor rows produced numbers, so no `ref_*` substitution was needed |
| `--jobs` | wall-clock only — run *i* is a pure function of `seed + i`, so `--jobs 0` and `--jobs 1` give identical results (`runner.py:111-114`) |

**Post-EB-57 / EB-58 label (applies to every number in this file).** All three
reads were taken **after** the two instrument fixes at `170ac7b` (EB-57, the
reaction amp counter re-settled as realized uplift; EB-58, aura-uptime
intervals bounded at the target's death). That commit declares
non-comparability for the `reaction_damage_amp` / `reaction_damage` /
`damage_from_base_ops` / `reaction_share` / `reaction_damage_share` family and
for `aura_telemetry` uptime, and states that fights are otherwise
bit-identical (120-fight battery: wins, reactions, total damage, aura
applications all identical pre/post). **No quantity in this file belongs to
either moved family** — these are winrates, act-1 clear rates, acts, deck size
and fights. The label is carried anyway, as instructed, so no reader has to
reconstruct which side of the fix a number sits on. No stamp moved at that
commit (instrument fix, not a world change).

---

## 1. `S4-G7` — Furina, three plans or one

**Prior read.** `docs/current/roster/roster-anchor-v14-v6-2026-08-06.md`
(the quotable standing table, R118 / queue row 10.2), n=3000, seed 20260729,
stamp **`RT7/D14/P3/C6`**, same twelve-arm recipe.

**Structural claim being tested (the row's own words):** *salon vs spotlight
and fanfare — non-overlapping intervals; fanfare still overlapping the
`real_silent` floor.* (In the prior table spotlight and fanfare were the same
point estimate with the same interval, so "non-overlapping" names salon's
separation from both, not a separation between those two.)

| arm | prior win `RT7/D14/P3/C6` | prior 95% | fresh win `RT9/D14/P6/C8` | fresh 95% | fresh k/n |
|---|---|---|---|---|---|
| `furina / salon` | **11.20%** | [10.1, 12.4] | **4.70%** | [4.00, 5.52] | 141/3000 |
| `furina / spotlight` | **2.23%** | [1.8, 2.8] | **1.50%** | [1.12, 2.00] | 45/3000 |
| `furina / fanfare` | **2.23%** | [1.8, 2.8] | **1.30%** | [0.95, 1.77] | 39/3000 |
| `real_silent / generic` (floor) | 1.70% | [1.3, 2.2] | **1.37%** | [1.01, 1.85] | 41/3000 |
| `real_ironclad / generic` (floor) | 8.53% | [7.6, 9.6] | **6.13%** | [5.33, 7.05] | 184/3000 |
| `ref_ironclad / generic` | 13.83% | [12.6, 15.1] | **9.40%** | [8.41, 10.50] | 282/3000 |

Act-1 clear, same cell, for completeness: salon 54.33% [52.55, 56.11],
spotlight 55.50% [53.72, 57.27], fanfare 47.67% [45.88, 49.46],
`real_silent` 58.93% [57.16, 60.68], `real_ironclad` 69.93% [68.27, 71.55]
(prior: 60.60 / 59.57 / 58.17 / 60.90 / 69.87).

**Interval arithmetic on the fresh read.**

- salon [4.00, 5.52] vs spotlight [1.12, 2.00] — **do not overlap**.
- salon [4.00, 5.52] vs fanfare [0.95, 1.77] — **do not overlap**.
- spotlight [1.12, 2.00] vs fanfare [0.95, 1.77] — overlap (as in the prior
  read, where the two were identical).
- fanfare [0.95, 1.77] vs `real_silent` [1.01, 1.85] — **overlap**.

### Structure: **HELD.**

Salon separates from both other plans at this n; fanfare still sits on the
`real_silent` floor with overlapping intervals. Magnitudes fell across the
boundary (salon 11.20% → 4.70%), and the whole table fell with it — the two
reference anchors dropped too (`ref_ironclad` 13.83 → 9.40, `real_ironclad`
8.53 → 6.13).

**One ordering fact that MOVED, recorded because it is a fact about the same
columns, not a recommendation.** In the prior table `furina/salon` (11.20%)
sat **above** `real_ironclad` (8.53%) with no interval overlap; in the fresh
read `furina/salon` (4.70% [4.00, 5.52]) sits **below** `real_ironclad`
(6.13% [5.33, 7.05]), again with no interval overlap. `ref_ironclad` (9.40%)
remains alone at the top, as it was after the 2026-08-06 republication.
Spotlight [1.12, 2.00] also overlaps the `real_silent` floor on this read; it
overlapped it on the prior read as well ([1.8, 2.8] vs [1.3, 2.2]).

---

## 2. `S4-G13` — Kokomi below the Ironclad-anchored floor

**Prior read.** The same standing table, same recipe, n=3000, seed 20260729,
stamp **`RT7/D14/P3/C6`**.

**Structural claim being tested (the row's own words):** *priest / commander /
assist all below `real_ironclad`; assist below even the `real_silent` floor;
non-overlapping.*

| arm | prior win `RT7/D14/P3/C6` | prior 95% | fresh win `RT9/D14/P6/C8` | fresh 95% | fresh k/n |
|---|---|---|---|---|---|
| `kokomi / priest` | **2.47%** | [2.0, 3.1] | **1.10%** | [0.78, 1.54] | 33/3000 |
| `kokomi / commander` | **3.00%** | [2.4, 3.7] | **2.20%** | [1.73, 2.79] | 66/3000 |
| `kokomi / assist` | **0.63%** | [0.4, 1.0] | **0.57%** | [0.35, 0.91] | 17/3000 |
| `real_ironclad / generic` (floor) | **8.53%** | [7.6, 9.6] | **6.13%** | [5.33, 7.05] | 184/3000 |
| `real_silent / generic` (floor) | 1.70% | [1.3, 2.2] | **1.37%** | [1.01, 1.85] | 41/3000 |

Act-1 clear, same cell: priest 42.20% [40.44, 43.98], commander 51.83%
[50.04, 53.62], assist 35.37% [33.68, 37.10] (prior: 42.83 / 51.33 / 35.30).

**Interval arithmetic on the fresh read.**

- priest [0.78, 1.54], commander [1.73, 2.79], assist [0.35, 0.91] — each
  interval's upper bound lies **below** `real_ironclad`'s lower bound (5.33).
  All three **do not overlap** the Ironclad floor.
- assist [0.35, 0.91] vs `real_silent` [1.01, 1.85] — **do not overlap**;
  assist is below the Silent floor.

### Structure: **HELD.**

All three plans remain below the `real_ironclad` floor with no interval
overlap, and assist remains below even the `real_silent` floor with no
interval overlap. The magnitudes moved down with the rest of the table; the
gap to the Ironclad floor did not close.

Recorded as fact, not as a claim the row makes: priest [0.78, 1.54] now
overlaps the `real_silent` floor [1.01, 1.85] — it overlapped it on the prior
read too ([2.0, 3.1] vs [1.3, 2.2]). Act-1 clear rates are essentially
unmoved across the boundary (within a point on all three plans) even though
the run winrates fell.

---

## 3. `M9` — Kokomi meter-20, the 500-run confirm

**Prior read.** `docs/archive/kokomi-v0.4-report.md` §2.3 (the "500-run
confirm at meter 20"), retrievable at tag `pre-simplification-2026-08-06`.
The report's §0 fixes the measurement convention: *`--realistic` runs at 500
runs, default seed*, invoked as
`python -m tier05.runner --character kokomi --archetype <plan> --runs 500 --realistic`.
Its world predates the stamp: `RT7/D14/P3/C6` and earlier.

**What the meter-20 quantity is.** "Meter 20" is `burst_max: 20` in
`tier0/content/characters/kokomi.yaml` — the v0.4 O4 salvage moved it 10 → 20,
and it is the shipped value today. The quantity the 500-run confirm reports is
the **act-1 clear rate and run winrate of Kokomi's four plans under that
meter**. §6 ask 2 is the ratification: *"Meter 20 ratification on the 500-run
confirm."*

**The comparator is dead, and is not replaced.** §2.3's right-hand column is
*"vs W1 baseline"* — the **v0.3 world** (a different `burst_max`, a
pre-rework starter, and a pre-`RT9`/`C8` engine). The row's own note says that
comparator was self-declared superseded at the tag; reproducing it would mean
editing ratified content YAML, which this packet does not do. §6 ask 2's
alternative comparator — *"or name meter 15"* — is the same problem: meter 15
is not a shipped world either. **So the meter-20 quantity is re-read alone.**
No comparator is invented.

| plan | prior act-1 `RT7`-and-earlier | prior run | fresh act-1 `RT9/D14/P6/C8` | fresh run | fresh 95% (Wilson) | fresh k/n |
|---|---|---|---|---|---|---|
| `priest` | 30% | 0.6% | **41%** | **1.4%** | [0.7, 2.9] | 7/500 |
| `commander` | 45% | 1.4% | **50%** | **2.2%** | [1.2, 3.9] | 11/500 |
| `generic` | 26% | 0.4% | **42%** | **1.0%** | [0.4, 2.3] | 5/500 |
| `assist` | 24% | 0.2% | **34%** | **0.4%** | [0.1, 1.4] | 2/500 |

(Act-1 clear is the `act funnel` line's *"act1 reached 100% cleared N%"*, the
same integer-percent quantity the v0.4 table printed. The prior table carried
no intervals; the fresh ones are the Wilson intervals
`print_run_report` now prints for the run winrate.)

**The structural claim being tested** is the one §2.2/§2.3 rest the meter-20
choice on: *at meter 20 the priest and commander act-1 clear rates sit in the
pre-registered 35–50% acceptance band, and no plan's run winrate is more than
a couple of points.* On the original 500-run confirm priest read 30% — below
the band's lower edge — with commander at 45% inside it.

### Structure: **HELD, and priest moved INTO the band.**

Fresh: commander 50% sits at the band's upper edge, priest 41% sits inside the
band (it was below it on the original confirm), and every plan's run winrate
remains at or under 2.2%. The band membership the meter-20 choice was made on
is intact under the current stamp; the one movement is priest rising from
below the band into it. The `generic` plan rose most (26% → 42% act-1) and
assist rose from 24% → 34%, just under the band's lower edge.

**Caveat carried forward:** ratifying meter 20 against *this* read is a
one-sided comparison. The trade §6 ask 2 asks [USER] to confirm — *"the arm
costs ~3–4 act-1 points and priest run winrate vs v0.3"* — cannot be re-read
without rebuilding the v0.3 world, which is a content change, not a
measurement. Whether that matters is [USER]'s call.

---

## Reproduction

```sh
# §1 + §2 — the twelve-arm standing-table recipe, 2m23s wall clock
PYTHONPATH=. python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729

# §3 — one invocation per plan
for p in priest commander generic assist; do
  PYTHONPATH=. python -m tier05.runner --character kokomi --archetype $p \
      --runs 500 --realistic --jobs 0
done
```

Full n was used for every read; nothing was reduced. The §1/§2 two-decimal
figures and the `k/n` counts come from a throwaway harness that derives the
identical cells (`cells.CANONICAL.but(name="roster-anchors").but(jobs=0,
runs=3000, seed=20260729).but(character=…, archetype=…).arm()`) and prints
more digits — its rows agree with the committed script's one-decimal output
row for row. No file in the repository was modified to take any of these
readings.
