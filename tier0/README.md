# Tier 0 Balance Simulator

Monte Carlo combat sim for validating Teyvat Spire card designs before any
C# is written. Spec: `docs/tier0-simulator-spec.md`. Decisions made during
implementation: `DECISIONS.md`.

## Setup

```sh
python3 -m venv .venv && .venv/bin/pip install pyyaml pytest
```

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

# Tests (70; includes frozen-battery regression bands)
.venv/bin/python -m pytest tier0/tests -q
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
