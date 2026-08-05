# Tier 0 Balance Simulator

Monte Carlo combat sim for validating Teyvat Spire card designs before any
C# is written. Origin spec: `docs/archive/tier0-simulator-spec.md` (archived
2026-07-26 — the sim has outgrown it by sanctioned scope growth; the living
law is `DECISIONS.md` and `harness/axes.py`). Decisions made during
implementation: `DECISIONS.md`.

## Setup

```sh
python3 -m venv .venv && .venv/bin/pip install pyyaml pytest pillow
```

(Pillow is needed by the art/still tests — `tests/test_char_stills.py`,
`tests/test_art_coverage.py` — and the `tools/` art pipeline.)

## Usage

Run from the repo root with `PYTHONPATH=.`:

```sh
# Full battery summary for a config
PYTHONPATH=. .venv/bin/python -m tier0.harness.runner \
    --character klee --deck reaction_package --pilot reaction --fights 1000

# 7-axis scorecard (runs the REF_IRONCLAD baseline alongside)
PYTHONPATH=. .venv/bin/python -m tier0.harness.runner --score \
    --character klee --deck demolition_package --pilot demolition

# Per-fight CSV for spreadsheet work
PYTHONPATH=. .venv/bin/python -m tier0.harness.runner --csv out.csv ...

# Tests (~590 collected; includes frozen-battery regression bands)
.venv/bin/python -m pytest tier0/tests -q
```

### Telemetry on the per-fight record

`harness.metrics.FightStats` is the per-fight record and is **sim-local**: it
is read by `tier0/`, `tier05/` and `tools/` and by nothing on the C# side. The
Py↔C# parity-tested fight schema is the *other* one — `understudy/soak.py`'s,
documented in `understudy/README.md` — and it is not this. Fields added here
do not cross that boundary.

Two instruments hang off it (Last Call track D, 2026-08-05):

- **D1, reactions' share of damage.** `reaction_damage_amp` (Vaporize/Melt
  uplift), `reaction_damage_splash` (Overload), `reaction_damage_dot`
  (Electro-Charged, which lives *outside* `total_damage_dealt`), plus the
  derived `damage_from_reactions` / `damage_all_ops` / `damage_from_base_ops`
  / `reaction_share`. Aggregate hook: `metrics.reaction_share(stats)` for a
  battery, `tier05.reaction_telemetry.aggregate(results)` for a cohort by act
  (printed on the default tier 0.5 report, silent when nothing reacted).
  The older `summarize()["reaction_damage_share"]` is **unchanged** — it feeds
  the ratified A6 axis, and the difference between the two is exactly the DoT.
- **D2, the per-turn record.** `turn_trajectory`, one row per player turn:
  `[turn, hp_at_open, block_at_open, block_at_end, incoming_hits,
  incoming_damage]`. `incoming_damage` is pre-block/ward/Encore — demand, not
  what survived mitigation. `block_at_end` is `-1` when the fight ended inside
  that turn (unsampled, never zero). Aggregate hook:
  `metrics.turn_profile(stats)`. tier0 models one seat, so there is no seat
  axis. CSV: `--turns-csv out.csv`.

Both report and neither grades; see `tests/test_track_d_telemetry.py`.

```sh
# D1 at battery level, printed
PYTHONPATH=. .venv/bin/python -m tier0.harness.runner \
    --character klee --deck reaction_weighted --pilot reaction \
    --fights 200 --reaction-share
```

Characters/decks live in `content/characters/*.yaml` (a deck is
`starter` or a package name), cards in `content/cards/*.yaml` (the schema
doubles as the mod's card sheet), pilots in `content/pilots/*.yaml`.

To iterate a card design: edit its YAML row, re-run `--score`. ~3s for a
full battery + baseline at 500 fights/encounter (~3k fights/sec).

## Frozen calibration

The encounter battery and the pilots' block weight (1.2) were calibrated
in M2 and are **frozen** — all scores are relative to REF_IRONCLAD starter
= 3.0 on this battery. Retuning either invalidates every comparison;
regression tests in `tests/test_axes.py` will fail loudly if you try.
