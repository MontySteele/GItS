# Sprint log — larger-n D13 confirmation + the Kokomi stability instrument (2026-07-29)

Two measurement tasks and one doc. **World throughout: `RT7 / D13 / P3 / C4`.**
No version bump, no yaml sheet value, no ratified band and no `DECISIONS.md`
entry was touched. **Every number below is REPORTED. Nothing here is
ratified, and the stability band is NOT declared** — that is a reserved [USER]
ruling under R51 and D5.

**Suite:** `python -m pytest -q` from the repo root — **1466 passed, 1 skipped,
0 failed**, on the merged tree.

Two notes on the count, because the number is not comparable to this morning's
1412 without them:

- Mid-sprint the suite read **1455 passed, 1 failed** —
  `test_encoding_gate.py::test_no_new_undeclared_encodings` on
  `tools/art_lint.py`. That was the **concurrent tooling pass mid-edit**, not
  this sprint: nothing here touches `tools/`. It was green by the time the tree
  settled, and 1466 is the joint total of both passes' new tests (16 of them
  are this sprint's instrument tests).
- **Disclosure: commit `4ee6881` swept in the concurrent pass's files.** The
  brief called for `git add` of owned paths only, and that is what was staged —
  but the other agent staged its own work into the shared index between the
  `add` and the `commit`, and a plain `git commit` takes the whole index. The
  resulting commit therefore contains both passes (24 files). Nothing was lost
  and the combined state is green and self-consistent; the attribution is
  simply wrong, and un-picking it by resetting a shared branch under a live
  concurrent writer was judged the more dangerous of the two options. The
  files owned here are: `tier0/engine/combat.py`,
  `tier0/harness/metrics.py`, `tier05/run_metrics.py`,
  `tier05/exp_roster_anchors.py`, `tier05/exp_kokomi_stability.py`,
  `tier05/tests/test_stability_trajectory.py`, and the two docs.

---

## Task 1 — the D13 roster table at n=3000

### Why n=3000

The sim-hygiene log's D12→D13 table ran at n=600 and separated nowhere: it
reported fanfare 1.8→2.8 and spotlight 2.3→3.3, both **+1.0**, both inside
overlapping Wilson intervals. A Wilson half-width at p≈0.025, n=600 is roughly
±0.8pp, which is most of a +1.0 move. At **n=3000** it is ±0.6pp on the same
p — enough to resolve a real +1.0 and, as it turns out, enough to kill this one.

The full 12-arm table at n=3000 costs about **4.5 minutes** wall-clock on this
machine at `--jobs 0` (16 workers), so the brief's permission to restrict the
expensive arms was **not needed**: every arm ran at n=3000 in both worlds.

### Exact command lines

```
# D13 (this tree, HEAD = 3e3c243 + this sprint's instrument changes)
python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729

# D12 (git worktree at 4343ecd, the commit before the D13 bump)
cd <worktree>; python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729
```

- **Fresh seed: `20260729`.** Today's published table used seed 11; reusing it
  would have made the larger-n run a superset of the smaller one rather than an
  independent confirmation.
- **D13 stamp:** `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT7/D13/P3/C4`
- **D12 stamp:** `cell=roster-anchors[jobs=0,runs=3000,seed=20260729] seed=20260729 runs=3000 RT7/D12/P3/C4`

Three procedural notes on the D12 half, because they are the kind of thing that
silently produces a wrong comparison:

1. `game_ref/` is gitignored, so a fresh worktree cannot build `real_ironclad`
   or `real_silent` at all — it fails with `KeyError: 'real_ironclad'` inside a
   worker, which surfaces as `BrokenProcessPool` and looks like an OOM. The
   directory was **copied** into the worktree (read-only use, originals
   untouched) and the two anchors then ran.
2. `jobs` was verified **result-invariant** before any of this was trusted:
   `real_silent` at n=200 seed 20260729 gives byte-identical win/act-1/acts at
   `--jobs 0`, `8` and `1`. `run_many` chunks by run index and seeds each run
   `seed + i`, so parallelism cannot move a number — checked rather than assumed.
3. The ad-hoc two-arm script needed an `if __name__ == "__main__":` guard. On
   Windows `spawn`, a module-level driver re-executes in every child and
   recursively spawns pools until the pool breaks. Same `BrokenProcessPool`,
   entirely different cause.

### THE PRE-PLAYTEST REFERENCE TABLE — D13, n=3000, seed 20260729

`win 95%` and `act-1 95%` are Wilson intervals from `tier05.stats.wilson95`,
now printed by `exp_roster_anchors` itself so a point estimate cannot be quoted
without its width. `z` is a two-proportion test on the D12→D13 difference;
|z| ≥ 1.96 is nominal significance, and with **24 comparisons in the table** the
Bonferroni bar is |z| ≥ 3.1.

| character | plan | D12 win | **D13 win** | **D13 win 95%** | Δ | z | D12 act-1 | **D13 act-1** | **D13 act-1 95%** | Δ | z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| klee | demolition | 7.8% | **7.2%** | [6.3, 8.2] | −0.6 | −0.88 | 83.0% | **83.2%** | [81.8, 84.5] | +0.2 | 0.21 |
| klee | spark | 5.8% | **5.5%** | [4.7, 6.4] | −0.3 | −0.50 | 80.7% | **80.5%** | [79.0, 81.9] | −0.2 | −0.20 |
| klee | reaction | 9.6% | **9.4%** | [8.4, 10.5] | −0.2 | −0.26 | 86.9% | **86.5%** | [85.2, 87.7] | −0.4 | −0.46 |
| furina | **salon** | 11.4% | **10.6%** | [9.5, 11.8] | −0.8 | −0.99 | 59.0% | **60.6%** | [58.8, 62.3] | +1.6 | 1.26 |
| furina | **spotlight** | 2.2% | **2.8%** | [2.3, 3.5] | +0.6 | 1.49 | 59.1% | **61.7%** | [59.9, 63.4] | +2.6 | 2.06 |
| furina | **fanfare** | 2.2% | **2.1%** | [1.6, 2.7] | −0.1 | −0.27 | 55.4% | **58.1%** | [56.3, 59.9] | +2.7 | 2.11 |
| kokomi | priest | 2.9% | **2.3%** | [1.8, 2.9] | −0.6 | −1.46 | 45.1% | **43.3%** | [41.5, 45.1] | −1.8 | −1.40 |
| kokomi | commander | 3.0% | **2.9%** | [2.4, 3.6] | −0.1 | −0.23 | 53.4% | **52.2%** | [50.4, 54.0] | −1.2 | −0.93 |
| kokomi | assist | 0.7% | **0.5%** | [0.3, 0.8] | −0.2 | −1.00 | 37.1% | **35.5%** | [33.8, 37.2] | −1.6 | −1.29 |
| ref_ironclad | generic | 11.0% | **10.8%** | [9.7, 12.0] | −0.2 | −0.25 | 71.5% | **71.4%** | [69.8, 73.0] | −0.1 | −0.09 |
| real_ironclad | generic | 8.0% | **8.1%** | [7.2, 9.1] | +0.1 | 0.14 | 70.4% | **70.2%** | [68.5, 71.8] | −0.2 | −0.14 |
| real_silent | generic | 2.2% | **2.1%** | [1.6, 2.7] | −0.1 | −0.19 | 64.0% | **61.1%** | [59.3, 62.8] | −2.9 | −2.32 |

Full D13 row detail (acts / deck / fights) is in the script output; the columns
above are the ones the playtest will be read against.

### The four questions the brief asked, answered

**1. Are fanfare's and spotlight's +1.0 winrate moves real at this n? NO.**

- **Fanfare's +1.0 does not exist.** At n=3000 the D12→D13 move is **−0.1**
  (2.2% → 2.1%, z = −0.27). The n=600 reading of 1.8 → 2.8 was noise on both
  ends, and it read as the largest relative gain in the table.
- **Spotlight's +1.0 is +0.6 and does not separate** (2.2% → 2.8%, z = 1.49).
  It is the largest surviving Furina move and it is still consistent with zero.
- **Nothing in the winrate column separates at n=3000.** Every |z| < 1.5, on
  five times the sample that already failed to separate. This is now a
  measurement, not a sample-size complaint: the op repricing did **not** move
  run winrate for any arm on the roster.
- The **act-1 column**, the tighter instrument, is the only place anything
  moves: spotlight **+2.6** (z = 2.06), fanfare **+2.7** (z = 2.11), and
  real_silent **−2.9** (z = −2.32) reach nominal significance. **None survives
  the 24-comparison Bonferroni bar of |z| ≥ 3.1**, so the honest statement is
  *directional, in the direction the repricing story predicts, at nominal
  significance only*. It is worth noticing that the two Furina arms that move
  are exactly the two built out of verbs v12 could not see, and that the third
  nominal mover is the anchor built entirely from official cards — the
  repricing touched those too.

**2. Does fanfare clear the 2.0 floor, or sit on it? It sits exactly on it.**

Fanfare **2.10% [1.64, 2.68]** against the roster floor real_silent **2.10%
[1.64, 2.68]** — the same point estimate to two decimals and the same interval
at n=3000. The interval brackets 2.0 from both sides. **Fanfare is the floor**,
and the fanfare-compensation sprint's REPORT-AND-STOP finding survives at five
times the sample size. Spotlight at 2.8% [2.3, 3.5] is above the floor and
still a quarter of salon.

**3. Does salon's near-zero move hold? In magnitude yes, in sign no.**

n=600 read **+0.2**; n=3000 reads **−0.8** (11.4% → 10.6%, z = −0.99). Both are
statistically indistinguishable from zero, which is the claim that holds: the
repricing did not move the salon arm. The *published sign* did flip, which is a
useful demonstration of what a n=600 delta is worth in this cohort.

**4. The design question the repricing was aimed at.** The sim-hygiene log read
the +1.0s as "directional evidence against everything feeding Salon by
construction". **At n=3000 that evidence is gone from the winrate column.** What
remains is the weaker act-1 observation in question 1. Salon leads the Furina
arms 10.6 vs 2.8 vs 2.1 and the repricing changed none of it. The drafter's
blindness was real, 54 cards did become visible, and it bought **no measurable
winrate anywhere** — which is itself the more interesting finding, and one only
the larger n could produce.

### Instrument change

`tier05/exp_roster_anchors.py` now prints a Wilson 95% interval beside every
rate column, from `tier05.stats.wilson95`. The reason is the paragraph the
sim-hygiene log had to write in prose and this table did not: at n=600 a +1.0pp
move sits inside overlapping intervals, and a table that prints the point
estimate alone invites exactly the quotation that log had to spend a paragraph
forbidding. The width is part of the row now.

---

## Task 2 — the Kokomi stability instrument

### First finding: `missed-requirements.md` §1.3 is STALE

The brief (quoting §1.3) says "no variance/flatness metric exists in
`tier05/run_metrics.py` or `tier0/harness/metrics.py`". That was true when the
audit was written and is not true now: **`run_metrics.stability_profile` exists**
— built by Serenitea Sweep I's E1, dark by design, `band: None`, pinned by
`tier0/tests/test_stability_band.py`, and amended by **D5** (2026-07-27), which
rules where the band may come from and when it may be graded.

What was actually missing was **the reading**. Nothing ever ran it: there is no
experiment script and no report on record that prints a stability number for any
cohort. From the outside, a dark instrument nobody points at a cohort is
indistinguishable from no instrument at all — which is presumably how §1.3 came
to be written after E1 landed.

**[USER] item owed:** §1.3 should be amended to "built, never read; now read"
rather than "never built". Not edited here — the ledger is the user's.

### What was built

1. **`FightStats.hp_by_round`** (`tier0/harness/metrics.py`) — player HP at the
   end of every round, in order. Sampled by a new **log-only** `round_hp` emit
   in `combat._run_rounds`, where `state.player.hp` is authoritative. Deriving
   it in `metrics.py` from `player_hit` + `heal` was rejected: HP also moves
   through `effects.py`'s block-ignoring self-damage, the Encore shortfall in
   `resources.py` and the Fairy revive, none of which emit either event, so a
   derived trajectory would be quietly wrong on exactly the cards a stability
   reading is about. The `break` in the round loop became `if not state.over`
   (control-flow-identical — the loop condition re-tests it) so the final,
   possibly lethal, round is sampled too. Every telemetry `trace()` in the repo
   filters by event name, so the extra event is inert; the suite confirms it.
2. **`run_metrics.trajectory_profile`** — the within-fight half
   `stability_profile` structurally could not see. Three questions, because
   "flat" turned out to be three claims: **jaggedness**
   (`within_fight_sd_pct`, the mean per-fight SD of end-of-round HP — per-fight
   then averaged, because pooling would mostly measure the act's downward drift,
   which is attrition), **spike depth** (`max_drawdown_pct`,
   `p90_drawdown_pct`, `survived_drawdown_pct`, `worst_round_drop_pct`) and
   **time spent low** (`round_share_below_50`, `round_share_below_30`).
   Everything is a fraction of max HP so rows compare without rescaling.
   `band` is `None` and the absence of any verdict key is pinned by test.
3. **`tier05/exp_kokomi_stability.py`** — the report, six arms.
4. **16 tests** in `tier05/tests/test_stability_trajectory.py`.
5. **A sixth hand-rolled percentile, fixed.** `stability_profile`'s `p90` was
   nearest-rank (`ordered[int(0.90 * n)]`) inside a module whose own convention
   is linear — the sim-hygiene sprint unified five copies and missed this one.
   Now `stats.percentile`. No published number quoted it.

### Two judgement calls worth arguing with

**The lethal round is excluded from every column.** Measured with it in,
`max_drawdown_pct` came out at **1.03–1.08 for all six arms** — because ~90% of
tier-0.5 runs end in death, and a death is a fall to zero from wherever you
were, so the column was reporting the death rate in a costume. Time-spent-low
leaked the same way: a round ending at 0 HP is trivially under every threshold.
Dying is what the winrate table measures; this instrument is about the shape of
a living character's curve. Excluded rounds are counted in `lethal_rounds`.

**Run-scale drawdown still saturates and is the weakest column.** Even with the
lethal round out, the round *before* death is usually a sliver, so `drawdn`
reads 0.94–0.99 for flat and jagged alike. It is reported because it is the
standard definition and a higher-winrate world will make it bite.
`survived_drawdown_pct` (`livedDD`) is the uncensored companion — the same
statistic over only the fights she walked out of, so it is the deepest trough
she actually **recovered from** — and it carries a survivorship bias in the
opposite direction. Both are printed; neither is presented as the answer. The
discriminating columns today are `inFtSD`, `wrstRnd` and the below-threshold
shares.

### Command line

```
python -m tier05.exp_kokomi_stability --runs 600 --jobs 0 --seed 20260729
```

**Stamp:** `cell=kokomi-stability[jobs=0,runs=600,seed=20260729] seed=20260729 runs=600 RT7/D13/P3/C4`

### THE STABILITY TABLE — D13, n=600, seed 20260729

| character | plan | max hp | lossSD | lossCV | lossMean | worstFt | inFtSD | wrstRnd | <50% | <30% | drawdn | p90dd | livedDD | prev/ft |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kokomi | priest | 70 | 0.234 | 1.119 | 0.209 | 0.713 | 0.082 | 0.119 | 0.417 | 0.203 | 0.960 | 1.086 | 0.712 | 1.05 |
| kokomi | commander | 70 | 0.231 | 1.140 | 0.203 | 0.716 | 0.079 | 0.115 | 0.407 | 0.193 | 0.972 | 1.086 | 0.729 | 0.72 |
| kokomi | assist | 70 | 0.246 | 1.105 | 0.223 | 0.724 | 0.085 | 0.119 | 0.424 | 0.216 | 0.957 | 1.071 | 0.629 | 0.54 |
| klee | reaction | 62 | 0.204 | 1.094 | 0.187 | 0.674 | 0.079 | 0.127 | 0.419 | 0.183 | 0.993 | 1.177 | 0.916 | 0.00 |
| furina | salon | 60 | 0.223 | 1.251 | 0.178 | 0.701 | 0.071 | 0.107 | 0.314 | 0.133 | 0.972 | 1.117 | 0.763 | 0.00 |
| ref_ironclad | generic | 80 | 0.248 | 1.035 | 0.239 | 0.867 | 0.095 | 0.135 | 0.332 | 0.145 | 0.976 | 1.087 | 0.770 | 0.00 |

### How to read this

Every value is a **fraction of max HP**. **Lower is flatter in every column.**
Values above 1.0 are not bugs: `max_hp` is the *starting* max, and `gain_max_hp`
raises the real ceiling mid-run.

- **`lossSD` / `lossCV` / `lossMean` / `worstFt`** — `stability_profile`, the
  E1 instrument: per-**fight** HP loss, pooled. `lossSD` is the headline
  flatness number; `lossCV` divides it by the mean, which separates "flat
  because nothing hits her" from "flat because she absorbs evenly". `worstFt` is
  the kickoff's literal "max HP-loss": each run's worst single fight, averaged.
- **`inFtSD` / `wrstRnd`** — `trajectory_profile`, **within** fights, round by
  round. `inFtSD` is jaggedness, not attrition. `wrstRnd` is the biggest
  single-round fall — the burst a ward is supposed to eat.
- **`<50%` / `<30%`** — share of all rounds fought that **ended** under that
  fraction of max HP.
- **`drawdn` / `p90dd` / `livedDD`** — run-scale peak-to-trough. Saturated; see
  above. `livedDD` is the uncensored, survivorship-biased companion.
- **`prev/ft`** — R51's ruled ward-prevention feed, in raw HP per fight.
  Reported, never axis-credited. It is nonzero **only** for Kokomi, which is the
  one column where her kit is unambiguously doing something no one else's does.
- **Flatter is not better.** A dead run stops generating rounds, so read this
  table beside Task 1's winrate table, where all three Kokomi arms sit at
  0.5–2.9%.

### What the roster says "stable" looks like — and the finding

**Kokomi is not the flattest character on the roster on any column.**

- The flattest arm in the table is **Furina/salon**: lowest `inFtSD` (0.071 vs
  Kokomi's 0.079–0.085), lowest `wrstRnd` (0.107 vs 0.115–0.119), lowest
  `<50%` (0.314) and lowest `<30%` (0.133 vs Kokomi's 0.193–0.216).
- **Klee/reaction — the roster's *declared HP-volatility pole*** ("Furina = HP
  volatility, Kokomi = HP stability", kickoff §1) — beats every Kokomi arm on
  `lossSD` (0.204) and on `<30%` (0.183), and ties the best of them on `inFtSD`.
- Kokomi's three arms cluster tightly together (`lossSD` 0.231–0.246, `inFtSD`
  0.079–0.085), so this is a **character** reading, not one bad plan.
- The two columns where Kokomi does lead are **`livedDD`** (0.63–0.73 vs Klee's
  0.916 — of the fights she survives, she recovers from shallower troughs) and
  **`prev/ft`**, the ward feed, which is hers alone.
- `ref_ironclad` is the jaggedest row on most columns, which is a sanity check
  on direction: a 80-HP bruiser taking whole intents to the face should be.

Read plainly: **on the instrument R51 made the entire home of her healer
fantasy, Kokomi currently reads mid-pack to worst, and the character the
kickoff named as her opposite reads flatter than she does.** That is a design
finding, not a grade — no band exists to fail. It is also the most direct
argument yet for the Task-3 pool fill: the flatness verbs her identity claims
(pre-emptive Block, Charge-bought defence, per-turn Block) are printed on two
commons and one uncommon in the whole pool.

### BAND NOT DECLARED — awaiting [USER]

**No band is declared by this sprint and none may be read out of this table.**
Both profiles return `band: None`, both docstrings say why, and both test files
pin the absence of a verdict key. Under **R51** the band is the entire home of
her healer fantasy; under **D5** it must be declared from **design intent**,
recorded as such, **before** the post-rework confirmatory playtest that grades
it, and **may not be revised against that playtest**. This table is input to
that declaration — what "stable" looks like relative to the roster in the
current world — and is not a candidate band. Picking a threshold off it would be
drawing the target around the shot.

---

## Task 3 — pool-fill proposals

`docs/brief-kokomi-pool-fill.md`. **Doc only**: 15 proposals, no yaml sheet
edited, so nothing unratified is in the measured pool.

---

## Still owed

1. **[USER] ruling: the stability band.** Design-intent declaration under D5,
   before the confirmatory playtest. This log is input, not a candidate.
2. **[USER] amendment: `missed-requirements.md` §1.3** — "built (E1), never
   read; read 2026-07-29", not "never built".
3. **[USER] red pen: Task 3's 15 proposals**, including the one that needs a new
   engine power.
4. **`DECISIONS.md`** — not written. The Task-1 table is a MEASUREMENT-class
   record and the ledger is the user's; the reference table itself is above and
   stamped so a ruling can cite it.
5. **The D13 repricing bought no measurable winrate.** All 33 v13 prices are
   still PROPOSED and the larger-n table is now the evidence a red-pen pass
   should be read against — including the possibility that the correct
   conclusion is "the offer scorer was blind, fixing it was right, and it does
   not matter to the run".
6. **`tools/art_lint.py` encoding-gate failure** is the concurrent agent's; not
   touched here.
