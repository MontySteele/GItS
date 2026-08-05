# Atlas — tier05-sim-core

Scope: `tier05/model.py`, `acts.py`, `runner.py`, `draft.py`, `route.py`,
`maps.py`, `cells.py` — the run-level simulator and the drafter.

## 1. Purpose

The run layer above the tier0 combat kernel: `model.run_one` walks a generated
act map, resolves fights/rests/shops/events/treasure and hands reward screens to
a draft policy, so **decks EMERGE from drafting instead of being authored**
(`tier05/__init__.py:3-5`). `draft.py` is the drafter — an offer-time scorer with
no combat state; `cells.py` is the identity object that makes two run numbers
comparable (R68). Scope boundary, verbatim: *simulate what WE design (cards,
pools, reward slots, draft flow); measure what MegaCrit designed with Tier 1/2
on the real game* (`__init__.py:4-5`). It is explicitly **not** the combat engine
(`tier0/engine/` is emit-only, its battery frozen and no longer read here —
`acts.py:26-29`, `model.py:86-89`), **not** an authored spine any more (the
11-node template died at RUNTEMPLATE 6 — `model.py:236-241`), and must not be
re-implemented inside `understudy/`, which drives the real game and "is not a
simulator and it must never become one" (`understudy/README.md:10`).

## 2. Entry points

From the repo root with `PYTHONPATH=.`:

```sh
PYTHONPATH=. python3 -m tier05.runner --character klee --archetype demolition \
    --runs 500 --seed 42
PYTHONPATH=. python3 -m tier05.runner --character furina --archetype salon \
    --realistic --runs 600 --seed 11 --jobs 0        # the ratified loadout
PYTHONPATH=. python3 -m tier05.runner --character klee --ab --runs 500
PYTHONPATH=. python3 -m tier05.runner --route-ab --character furina --runs 600
PYTHONPATH=. python3 -m tier05.runner --acts 1 --csv out.csv   # 1-act instrument
python3 -m pytest tier0/tests tier05/tests -q          # what CI runs
PYTHONPATH=. python3 tools/lint_op_parity.py           # 56 ops, 56 priced
```

Full flag list: `runner.py:81-118`. Experiment scripts go through a `Cell`,
which carries the stamp a report needs to be citable:

```python
from tier05 import cells
cell = cells.CANONICAL.but(runs=200)     # cells.py:237, cells.py:176-193
results = cell.run(); print(cell.stamp())
```

Lower level: `model.run_one(...) -> RunResult` (`model.py:244`),
`model.run_many(..., jobs=N)` (`model.py:801`), `draft.POLICIES`
(`draft.py:1499`), `route.POLICIES` (`route.py:145`), `runner.resolve_plan`
(`runner.py:62`). Tests script node sequences through the `scripted_map`
fixture (`tier05/tests/conftest.py:17-38`), which patches `model.build_act_map`.

## 3. Key invariants

- **One `random.Random` per run** — fight seeds, reward rolls, map rolls
  (`model.py:19-21`, `acts.py:21-24`, `maps.py:22-23`). Side measurements take
  DEDICATED streams so they cannot renumber a run: banner `seed+2e9`
  (`model.py:284-295`), starting deck `seed+3e9` (`:298-300`), draft_regret
  `seed+i+1e9` (`:779-781`). The boss draw consumes an rng call even from a
  1-entry pool, so growing a pool renumbers nothing (`acts.py:211-212`).
- **`len(node_kinds) == MAP_FLOORS * n_acts`, and the index IS the floor
  index** — one room per floor, act boundaries at multiples of `C.MAP_FLOORS`
  (`model.py:345-350`, `:188-192`).
- **`jobs` is a wall-clock lever only**: run *i* is a pure function of
  `seed + i`, so an N-job list is element-for-element identical to the serial
  one (`model.py:810-823`; pinned by `tests/test_parallel_runs.py:31`). Workers
  take the policy **by name** — a callable cannot be pickled (`:786-791`).
- **Run-layer effects live here, never in combat**: Burning Blood's post-fight
  heal, gold income, relic/potion grants, every reward roll (`model.py:613-633`).
- **Reward screens: the fight's own, then any it EARNED.** An extra screen
  (`state.extra_card_screens`) is card-only — no companion slot, no pity credit,
  no forced-Rare tier (`model.py:684-685`, `:718-723`). A non-final boss forces
  Rare on BOTH card offers and companion slot, then heals to full
  (`:662-670`, `:733-744`).
- **Pool YAML has a closed key schema**: `_validate_pool` raises on any unknown
  tier/encounter/enemy/intent key, since pools are read via `.get()` and a typo
  (`is_bos: true`) is otherwise a silent no-op (`acts.py:53-103`). Cached by
  FILENAME so a monkeypatched `RUN_ACTS` cannot serve a stale entry, and read
  with explicit `encoding=` (`acts.py:106-111`) — the repo-wide structural rule
  (`tier0/tests/test_encoding_gate.py:1-22`).
- **Routing is a whole-map plan, not a greedy next-room choice**: exact backward
  induction over the layered DAG, ties broken on room index so a seed replays
  identically (`route.py:56-87`).
- **`STATIC_OP_PRICING` must cover the engine's whole `OPS` registry**, priced
  zeros included, each with a written rationale; `tools/lint_op_parity.py` fails
  the build otherwise (`draft.py:986-1003`). **`draft.py` itself defines no
  version constant** — the live stamp is `DRAFTER_VERSION` in
  `tier0/constants.py` (`draft.py:9-11`), and a scorer change IS a version bump
  in the same edit (`tier0/DECISIONS.md:2658`).

## 4. Rulings that shaped it

- **R2.1 / R2.2** — the hybrid's power term became `score_offer`'s
  (`hybrid_policy` is now an alias); reaction got a steeper lean line, and
  raising applier/amp measured worse
  (`docs/archive/tier05-m8-report.md:100-118`; `draft.py:657-668`, `:1494`).
- **R61** — the sim MODELS the shop as an economy channel: hence the `$` branch,
  with offers logged separately from purchases (`tier0/DECISIONS.md:1813-1824`;
  `model.py:392-453`, `:169-174`).
- **R64** — the Banner went live and `roll_banner`'s `nations` must be passed
  explicitly from the sheets; the argument-free default had filtered every
  non-Mondstadt 5-star out of every run (`:1922-1949`; `model.py:284-295`).
- **R66** — archetype vocabulary is the sheet's; adaptive numbers taken through
  the broken registry are archived, assigned-plan ones stand because they route
  through `runner.py`'s registry (`:1989-2060`; `draft.py:1284-1314`).
- **R68** — `Cell` is the single source of truth for cell identity, versions are
  read live and never stored, plan→pilot resolves only via
  `runner.resolve_plan`, and **a report without a stamp is not citable**
  (`:2122-2163`; `cells.py:61-149`, `runner.py:62`).
- **R83 / R84** — the scorer pass is the authorized policy work; anchor role
  labels do not track generic value, so plan bonuses scale on
  `archetype == "generic"` only, and DRAFTER 11-12 land
  `STATIC_DEXTERITY_VALUE` plus `STATIC_POWER_ENGINE_VALUE` as a *documented
  dead dial* (`:2623-2698`; `draft.py:689-773`, `:1154`).
- **R87 (3)** — the DRAFTER 13 op repricing: 42 of 56 ops priced at zero biased
  every run-layer winrate; on the bump every DRAFTER-12 number became archive
  (`:2868-2879`; `draft.py:775-1003`).

## 5. Traps

- **Every published number is world-stamped, and worlds are not comparable.**
  RUNTEMPLATE 4→5→6→7 each broke seed comparability (v6 totally); DRAFTER and
  POLICY bumps archive their predecessors (`tier0/constants.py:580-628`,
  `:821-917`). Check the stamp before quoting anything. Relatedly,
  `node_template()`, `ELITES_PER_ACT` and `RUN_NODE_TEMPLATE` are DEAD but must
  not be deleted — they name the v5 spine archived tools were measured on
  (`model.py:236-241`, `acts.py:46-50`, `tier0/constants.py:629-631`).
- **Adaptive policies must never see the assigned label.** `emergent_plan`
  (`draft.py:1481`) is read at *three* sites — rest smithing, shop buying,
  events (`model.py:396-400`, `:461-465`, `:497-500`). A fourth decision channel
  added without it silently re-labels adaptive runs (measured: 5/40 seeds
  diverged, 2/40 win flips — `draft.py:1475-1480`).
- **`route_regret` does not exist**, though the research doc mandates it and
  `route.py`'s header once claimed it shipped (`route.py:13-15`,
  `docs/missed-requirements.md:93-104`); hunter-vs-cautious is the only real
  route countermeasure. And do **NOT** calibrate `MAP_ROOM_ODDS` or the route
  policies against a winrate — the target is player behaviour (median ~2.5
  elites fought per act, range 1-4), and tuning a difficulty dial to a winrate
  already had to be retracted once here (`route.py:17-27`,
  `tier0/constants.py:656-660`, `tier05/tests/test_maps_and_routing.py:1-10`).
- **The map generator carves paths; it does not roll widths.** Rolling per-floor
  widths produced lane-locked maps where 9% of elite-hunting routes reached zero
  elites, and widening floors did not help — *connectivity* binds
  (`maps.py:91-111`). Elite-not-twice-in-a-row is enforced at walk time by the
  draw (`maps.py:12-14`, `acts.py:226-233`), and `resolve_unknown` MUTATES the
  weights dict it is handed (`maps.py:155-182`).
- **Priced-at-zero drafter constants are measurements, not oversights** — each
  is a *named* dial so the next pass starts from the measurement
  (`draft.py:797-813`, `:721-725`, `:754-773`). Two latent footguns beside them:
  `reaction`'s lean penalty STACKS with the global bloat line past
  `DRAFT_DECK_SOFT_CAP` (`draft.py:1219-1226`), and `_drafted_readers` excludes
  basics deliberately, because Furina's starter carries a Fanfare read that
  would otherwise close the reader limb forever (`draft.py:244-261`).
- **`cells` ↔ `runner` is a deliberate one-way module edge**: `cells` imports
  `runner` at *call* time, `runner` imports `cells` inside `main()`; module
  scope on either side reintroduces the cycle (`runner.py:25-30`,
  `cells.py:49-58`). The CLI also forces stdout to UTF-8, because the
  death-heatmap glyph killed the report mid-table on cp1252 (`runner.py:136-140`).
- **`understudy/policy_v0.py` is FROZEN and delegates into these files**
  (`draft.assigned_policy`, `draft.score_offer`, `model.rest_action`,
  `tier05.route` — `understudy/policy_v0.py:9-10,193,315`). It is one arm of a
  published measurement, so a scoring change here retroactively moves a quoted
  number.

## 6. Reading order

1. `tier05/__init__.py` + `tier0/constants.py:578-700` — scope sentence, plus
   the run-model / map constants and their version history.
2. `tier05/model.py` — `run_one`: the node loop everything else plugs into.
3. `tier05/maps.py`, then `tier05/route.py` — node kinds and pathing, plus the
   confounder warning governing both.
4. `tier05/acts.py` — encounter pools, the key allowlist, `ActDraw`.
5. `tier05/draft.py` — docstring, `core_complete`/`_core_progress`,
   `score_offer`, `assigned_policy`, then the constants blocks (the record).
6. `tier05/cells.py` + `tier05/runner.py` — cell identity, stamps, plan→pilot;
   then `tier0/DECISIONS.md` for the R-number behind anything you plan to change.
