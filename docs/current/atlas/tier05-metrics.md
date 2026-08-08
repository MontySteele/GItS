# Atlas — tier05-metrics

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `tier05/run_metrics.py`, `stats.py`, `sweeps.py`, `ab.py`, the seven
`*_telemetry.py` modules, and the `exp_*` experiment-file convention.

## 1. Purpose

The measurement layer over the tier-0.5 run simulator. `run_metrics` turns a
list of `RunResult` into the fragility surfaces win rate cannot express
("62 HP, reluctant defense" — `run_metrics.py:1-5`); `ab.py` owns the three
spec alarms (divergence / relevance / achievability) and the same-seed A/B
harnesses; `sweeps.py` is the ONLY legal way to sweep a constant; the
`*_telemetry` modules reduce a fight's event log into per-fight traces while
the log still exists. Everything here **reads and reports; nothing gates** —
acceptance bands are [USER] rulings, so `band` is `None` by design
(`run_metrics.py:342-344`, `:515-516`). It is explicitly NOT a scorer (pricing
and offer logic are `draft.py`, atlas `tier05-sim-core`), NOT the combat engine,
and NOT an instrument for the real game — `understudy/` drives the actual mod
and "is not a simulator and it must never become one"
(`understudy/README.md:10`).

## 2. Entry points

From the repo root with `PYTHONPATH=.`:

```sh
PYTHONPATH=. python3 -m tier05.runner --character furina --archetype salon \
    --realistic --runs 600 --seed 11 --jobs 0     # prints the run report
PYTHONPATH=. python3 -m tier05.runner --character klee --ab --runs 1000
PYTHONPATH=. python3 -m tier05.runner --route-ab --character furina --runs 600
PYTHONPATH=. python3 -m tier05.exp_roster_anchors --runs 600 --jobs 0
PYTHONPATH=. python3 -m tier05.exp_pilot_gap all --runs 600 --jobs 0
python3 -m pytest tier0/tests tier05/tests -q          # what CI runs
```

Library surface: `run_metrics.summarize_runs` (`:25`), `survival_profile`
(`:160`), `stability_profile` (`:236`), `trajectory_profile` (`:366`),
`route_profile` (`:83`), `act_funnel` (`:134`), `banner_variance` (`:523`),
`conditional_assembly` (`:553`), `floor_kind_labels` (`:587`),
`print_run_report` (`:610`); `ab.divergence / relevance / achievability /
run_ab / run_route_ab` (`ab.py:34`, `:73`, `:112`, `:138`, `:218`);
`stats.percentile / wilson95` (`stats.py:41`, `:60`); `sweeps.sweep /
sweep_pairs / armed` (`sweeps.py:75`, `:104`, `:61`). Every telemetry module is
the same pair — `trace(state.log)` per fight, `aggregate(traces)`
(`fanfare_telemetry.py:135`, `:180`).

**`exp_*` convention** — one experiment per file, `python -m tier05.exp_<name>
[block] [--runs N] [--seed N] [--jobs N]`, `main(argv) -> int` under
`if __name__ == "__main__"`, a module docstring that REGISTERS its metric
definitions and names the sprint doc it belongs to, and a `Usage:` line
(`exp_curtain_call.py:1-20`, `exp_pilot_gap.py:1-46`). Cells come from
`cells.CANONICAL.but(...)` and every table prints `Cell.stamp()`
(`exp_pilot_gap.py:145`, `exp_roster_anchors.py:1-33`).

## 3. Key invariants

- **The axis is FLOORS, never `results[0]`'s length.** Every per-position
  surface sizes itself `C.MAP_FLOORS * n_acts`, because a dead run is short and
  one unlucky first run would size the whole report (`run_metrics.py:32-35`,
  `:190`, `:596`). Under §11 routing there is no shared layout, so floor labels
  are a distribution, not a template (`run_metrics.py:587-593`).
- **Fight positions are `N`/`E`/`B` only.** `R`/`T`/`$` carry the previous HP
  value forward; reading them as a survival sample is the defect
  `survival_profile` was rewritten to remove. A run that died earlier
  contributes 0; a run that reached the floor but did not fight is EXCLUDED,
  not zeroed (`run_metrics.py:191-217`).
- **Stability reads `FightStats`, not `hp_by_node`** — node HP carries across
  rests and shops, so differencing it measures the rest economy
  (`run_metrics.py:283-287`). Trajectory reads `FightStats.hp_by_round`, and
  **the lethal round is excluded from every column** (`run_metrics.py:422-430`,
  `:467-469`).
- **`band` is `None` and no verdict key exists** in `stability_profile` and
  `trajectory_profile`; pinned by test (`run_metrics.py:342-344`, `:515-516`;
  `tier0/tests/test_stability_band.py:54-60`;
  `tier05/tests/test_stability_trajectory.py:40-47`).
- **`stamp` is a keyword-only REQUIRED argument** of `print_run_report`: an
  omitted stamp must be a `TypeError`, not a thinner report (R68 —
  `run_metrics.py:610-621`; wired at `runner.py:168-183`).
- **ONE percentile (linear interpolation, type 7) and ONE Wilson interval**, in
  `tier05.stats`; `run_metrics` re-exports them under the old private names, and
  `wilson95` returns `(lo, hi)` only (`stats.py:1-34`, `:41-57`, `:60-83`;
  `run_metrics.py:17-22`; `kurage_telemetry.py:41-44`).
- **A/B arms run over identical seeds and differ in exactly one thing** —
  policy for `run_ab`, route for `run_route_ab` (`ab.py:15-17`, `:148-151`,
  `:224-230`). `divergence` is stored for the adaptive arm ONLY, because under
  `assigned` the shape restates the input (`ab.py:166-171`).
- **`relevance` conditions on `plan_live`**: core progress caps at 1.0, so
  post-completion screens are structurally unable to advance the plan and
  counting them penalises the fastest archetype worst (`ab.py:73-98`).
- **Every constant sweep goes through the gated harness.** `sweep()` resets
  `effects.reset_knob_reads()`, arms the knob, and raises `DeadKnobError` on
  the FIRST cell recording zero reads; `sweep_pairs` requires EVERY knob live in
  EVERY cell (`sweeps.py:75-101`, `:104-133`). Counting is real attribute
  access via a PEP 562 `__getattr__` on `tier0/constants.py:979-989`, so
  `from tier0.constants import X` would bind at import and slip the hook —
  do not introduce one (`tier0/constants.py:969-972`).
- **Telemetry traces are reduced AT THE FIGHT**, act-tagged `(act_index, Trace)`
  per fight, because `state.log` does not survive onto `RunResult`
  (`model.py:558-597`, `:194-233`). Metric definitions are REGISTERED in the
  module docstring and fixed for the pass so no later cell can redefine them
  mid-sweep (`fanfare_telemetry.py:1-21`, `encore_telemetry.py:10-56`,
  `burst_telemetry.py:18-32`, `kurage_telemetry.py:16-28`).

## 4. Rulings that shaped it

- **R14** — dose cells are diagnostics, never acceptance targets; every
  telemetry module restates it in its own docstring
  (`klee-mod/DECISIONS.md:603-605`; `kurage_telemetry.py:3`,
  `burst_telemetry.py:3`, `aura_telemetry.py:18`, `overlap_telemetry.py:3`).
- **R33** — dead-knob claims need an EXERCISE COUNTER, and the counter may not
  be satisfied by artificial reads (`tier0/DECISIONS.md:620-635`; quoted
  verbatim in `sweeps.py:96-100`).
- **R51** — Kokomi's healer fantasy moves ENTIRELY to the stability band
  (HP-trajectory flatness), and `FightStats.prevented` is a reported feed into
  it, never axis-credited (`tier0/DECISIONS.md:1285-1295`;
  `run_metrics.py:238-244`, `:333-339`).
- **R66** — the starvation check keys on THIS COHORT's archetype family, not on
  Klee's module-level list, which made every non-Klee run fire a spurious alarm
  (`tier0/DECISIONS.md:1989`; `ab.py:50-59`).
- **R67** — nine dead knobs deleted and KNOB_READS graduated from opt-in to
  GATE; **no sweep may be run outside the gated harness**
  (`tier0/DECISIONS.md:2065-2120`; `sweeps.py:1-40`).
- **R68** — a report without a stamp is not citable; the CLI's own config is a
  `Cell`, so runner and experiment stamps are produced identically
  (`tier0/DECISIONS.md:2122-2163`; `run_metrics.py:613-621`).
- **R85** — Curtain Call; `aura_telemetry` is its Track D rider and its ±10%
  bound lives in the sprint log, not in the code
  (`tier0/DECISIONS.md:2699`; `aura_telemetry.py:1-19`).
- **R87 (3)** — the DRAFTER 13 repricing: on the stamp bump every
  drafter-layer number taken under DRAFTER 12 became archive and must be
  re-measured before it is quoted (`tier0/DECISIONS.md:2834`, `:2870-2879`).
- **D3** — the axis-validity deferral: seven-axis numbers are reportable but
  NOT load-bearing, and no new band may be ratified until that session rules
  (`tier0/DECISIONS.md:2402-2444`).
- **D4** — a registered prediction must name an instrument that can SEE the
  change; any quantitative claim used as rationale carries a measurement or the
  `UNMEASURED` marker (`tier0/DECISIONS.md:2446-2500`;
  `conditional_telemetry.py:1`).
- **D5** — the stability band's provenance and schedule: the reviewed playtest
  is EXPLORATORY, the band is declared from DESIGN INTENT before the
  confirmatory playtest, and may not be revised against the playtest that
  grades it (`tier0/DECISIONS.md:2504-2562`; `run_metrics.py:258-269`).

## 5. Traps

- **Per-combat is not per-run.** `fanfare_telemetry.aggregate` returns
  `*_per_combat` rates; a mislabel to `_per_run` once inverted a gate verdict by
  ~9x. Rescale only via `per_run(agg, runs)` with the caller's own run count —
  RUNTEMPLATE 6+ makes the fights-per-run count variable
  (`fanfare_telemetry.py:207-213`, `:241-248`; `model.py:197-201`).
- **Sweep rows from a dead knob are instrument error, NOT a null result**, and
  a flat table looks identical either way — that is why it is a gate and not a
  reviewer (`sweeps.py:16-28`; `tier05/tests/test_sweep_gate.py:6-13`). Never
  add a read to make a sweep go green (`sweeps.py:96-100`).
- **Pre-instrument log events are skipped, not zeroed.** `gain_fanfare` rows
  without `requested` are "unmeasured" (zero waste would read as a healthy
  world); a missing `hp_by_round` is skipped, because a missing trajectory is
  not a flat one (`fanfare_telemetry.py:163-167`, `run_metrics.py:471-474`).
  Relatedly, `read_at_floor` is NET of `reads_empty` and the two must stay
  distinct: before any grant the floor is 0, so a dead meter and a meter on a
  built baseline are the same event to the flag and opposite diagnoses
  (`fanfare_telemetry.py:51-54`, `:99-107`).
- **Encore "drained" is not `encore_spent`** — `absorb_into_encore` emits
  `encore_absorb`, and reading the ratio against spends alone reports every
  point the buffer ATE as wasted. Upkeeps cut short by fight end are excluded
  from all-ticked, not counted as dry (`encore_telemetry.py:40-56`).
- **`achievability` filters `is not None`, not truthiness** — a falsy test would
  silently drop a run that came online at fight 0 (`ab.py:122-126`).
- **Small cells are withheld, not printed as zero.** `overlap_telemetry` marks
  anything under `MIN_CELL = 20` rather than rendering a number that would be
  read as one, and its `win both` column is explicitly NOT gradeable at
  Kokomi's ~3% win rate (`overlap_telemetry.py:51-68`, `:103-104`, `:235-236`).
  Its zeroes also read per PLAN: `honor_guard` is `archetypes: [commander]`, so
  its columns are structurally empty elsewhere (`overlap_telemetry.py:80-82`).
  Strict attribute access on the trace fields is deliberate — a `getattr`
  default would render a vanished field as "nobody played these cards"
  (`overlap_telemetry.py:161-163`).
- **Run-scale drawdown SATURATES** in this ~90%-death cohort and is the weakest
  column; the discriminating ones are `within_fight_sd_pct`,
  `worst_round_drop_pct` and the below-threshold shares. Values above 1.0 are
  not bugs (`gain_max_hp` moves the real ceiling) (`run_metrics.py:398-420`).
  `avg_final_deck_won` / `_lost` is likewise observation only — no rule reads
  it, and the printer emits both halves or neither (`run_metrics.py:59-72`).
- **The report forces stdout to UTF-8** because the death-heatmap block glyph
  killed the table mid-print on cp1252 (`runner.py:132-140`); the repo-wide
  encoding rule is structural (`tier0/tests/test_encoding_gate.py:1-22`).
- **A failed `exp_furina_strength` arm holds its ROW** and prints `ARM FAILED`;
  it used to vanish from `rows` and leave the comparison looking authoritative
  (`exp_furina_strength.py:622-676`;
  `tier0/tests/test_exp_strength_missing_arm.py`).
- **Every published number is world-stamped and worlds are not comparable** —
  RUNTEMPLATE / DRAFTER / POLICY bumps archive their predecessors, which is why
  `exp_roster_anchors` re-runs anchors in ONE invocation rather than quoting
  older tables (`exp_roster_anchors.py:1-20`), and why every rate column now
  carries a Wilson interval so a point estimate cannot be quoted bare
  (`exp_roster_anchors.py:26-33`;
  `docs/current/calibration/sprint-sim-hygiene-log-2026-07-29.md:159`).

## 6. Reading order

1. `tier05/stats.py` — the whole file; the one percentile, the one interval,
   and why five copies disagreed.
2. `tier05/run_metrics.py` — module docstring, then `summarize_runs`,
   `survival_profile`, `stability_profile`, `trajectory_profile` docstrings
   (the instrument reasoning lives there, not in a doc).
3. `tier05/sweeps.py` + `tier0/constants.py:955-1013` — the gate and the read
   hook that makes it uncheatable.
4. `tier05/ab.py` — the three alarms and the same-seed discipline.
5. `tier05/fanfare_telemetry.py`, then `overlap_telemetry.py` — the trace /
   aggregate shape and the two hardest reporting rules (per-combat units;
   withheld small cells); `model.py:194-233` and `:558-597` for how traces
   attach.
6. `tier05/exp_roster_anchors.py` + `exp_pilot_gap.py` — the `exp_*`
   convention, cells and stamps; then `tier0/DECISIONS.md` for the R-number
   behind anything you plan to change.
