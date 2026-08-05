# Atlas — tier05-sim-core

Scope: `tier05/model.py`, `acts.py`, `runner.py`, `draft.py`, `route.py`,
`maps.py`, `cells.py` — the run-level simulator and the drafter.

## 1. Purpose

The run layer above the tier0 combat kernel: `model.run_one` walks a generated
act map, resolves fights/rests/shops/events/treasure, and hands reward screens
to a draft policy, so **decks EMERGE from drafting instead of being authored**
(`tier05/__init__.py:3-5`). `draft.py` is the drafter — an offer-time scorer
with no combat state — and `cells.py` is the identity object that makes any two
run numbers comparable (R68). The scope boundary is one sentence: *simulate what
WE design (cards, pools, reward slots, draft flow); measure what MegaCrit
designed with Tier 1/2 on the real game* (`__init__.py:4-5`). It is explicitly
**not** the combat engine (`tier0/engine/` stays emit-only and its battery is
frozen — `acts.py:26-29`), **not** an authored spine any more (the fixed
11-node template died at RUNTEMPLATE 6 — `model.py:236-241`), and it must not be
re-implemented inside `understudy/`, which drives the real game and "is not a
simulator and it must never become one" (`understudy/README.md:10`).

## 2. Entry points

From the repo root with `PYTHONPATH=.`:

```sh
# the CLI: terminal run report + stamp, optional CSV
PYTHONPATH=. python3 -m tier05.runner --character klee --archetype demolition \
    --runs 500 --seed 42
PYTHONPATH=. python3 -m tier05.runner --character furina --archetype salon \
    --realistic --runs 600 --seed 11 --jobs 0        # the ratified loadout
PYTHONPATH=. python3 -m tier05.runner --character klee --ab --runs 500
PYTHONPATH=. python3 -m tier05.runner --route-ab --character furina --runs 600
PYTHONPATH=. python3 -m tier05.runner --acts 1 --csv out.csv   # 1-act instrument

python3 -m pytest tier05/tests -q
python3 -m pytest tier0/tests tier05/tests -q          # what CI runs
PYTHONPATH=. python3 tools/lint_op_parity.py           # 56 ops, 56 priced
```

Flags: `--character --archetype --runs --seed --csv --policy --ab --route
--route-ab --realistic --jobs/-j --acts` (`runner.py:81-118`).

In-process, and the preferred path for experiment scripts:

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

- **One `random.Random` per run**; every fight seed, reward roll and map roll
  flows through it — determinism at run granularity, same contract as tier0
  (`model.py:19-21`, `acts.py:21-24`, `maps.py:22-23`).
- **Side measurements get DEDICATED streams so they cannot renumber the run**:
  banner `seed + 2e9` (`model.py:284-295`), starting deck `seed + 3e9`
  (`model.py:298-300`), draft_regret `seed + i + 1e9` (`model.py:779-781`).
- **`len(node_kinds) == MAP_FLOORS * n_acts`, and the index IS the floor
  index** — every path visits exactly one room per floor, act boundaries sit at
  multiples of `C.MAP_FLOORS` (`model.py:345-350`, `model.py:188-192`).
- **`jobs` is a wall-clock lever only**: run *i* is a pure function of
  `seed + i`, so an N-job result list is element-for-element identical to the
  serial one (`model.py:810-823`; pinned by `tests/test_parallel_runs.py:31`).
  Workers receive the policy **by name**, because a callable cannot cross a
  process boundary (`model.py:786-791`).
- **Run-layer effects live here, never in combat**: Burning Blood's post-fight
  heal, gold income, relic/potion grants and every reward roll
  (`model.py:613-633`); combat only states facts.
- **Reward screens: the fight's own, then any the fight EARNED.** An extra
  screen (`state.extra_card_screens`) is card-only — no companion slot, no pity
  credit, never the boss's forced-Rare tier (`model.py:684-685`,
  `model.py:718-723`).
- **A non-final boss forces Rare on BOTH the card offers and the companion
  slot** (v5; forcing only the companion was the Ironclad-0.6% bug) and the
  boundary then heals to full (`model.py:662-670`, `model.py:733-744`).
- **Pool YAML has a closed key schema.** `_validate_pool` raises on any unknown
  tier/encounter/enemy/intent key, because pools are read through `.get()` and a
  typo (`is_bos: true`) is otherwise a silent no-op (`acts.py:53-103`).
- **Pool YAML is cached by FILENAME, not act index**, so a monkeypatched
  `RUN_ACTS` can never serve a stale entry (`acts.py:106-111`); text is read
  with an explicit `encoding=` (`acts.py:111`), the repo-wide structural rule
  (`tier0/tests/test_encoding_gate.py:1-22`).
- **The boss draw always consumes an rng call**, even from a 1-entry pool, so
  growing a pool never silently renumbers the other streams (`acts.py:211-212`).
- **Routing is a whole-map plan, not a greedy next-room choice**: exact backward
  induction over the layered DAG, ties broken on room index so a seed replays
  identically (`route.py:56-87`).
- **`STATIC_OP_PRICING` must cover the engine's whole `OPS` registry**, priced
  zeros included and each with a written rationale; `tools/lint_op_parity.py`
  fails the build otherwise (`draft.py:986-1003`).
- **`draft.py` defines no version constant.** The live stamp is
  `DRAFTER_VERSION` in `tier0/constants.py`; do not read a version off this file
  (`draft.py:9-11`). A scorer change IS a version bump in the same edit
  (`tier0/DECISIONS.md:2658` / R84).

## 4. Rulings that shaped it

- **R2.1 / R2.2** — the hybrid's power term was adopted into `score_offer` and
  `hybrid_policy` became an alias; reaction gets a steeper lean line (cap 13 ×
  0.4), while applier/amp raises measured worse
  (`docs/archive/tier05-m8-report.md:100-118`; `draft.py:657-668`,
  `draft.py:1494`).
- **R61** — the sim MODELS the shop as an economy channel (distinguished from
  the static-effect exemptions), which is why `run_one` has a `$` branch and
  `RunResult` logs offers separately from purchases
  (`tier0/DECISIONS.md:1813-1824`; `model.py:392-453`, `model.py:169-174`).
- **R64** — the Featured Banner went live and `roll_banner`'s `nations` must be
  passed explicitly from the sheets; the argument-free default had silently
  filtered every non-Mondstadt 5-star out of every run
  (`tier0/DECISIONS.md:1922-1949`; `model.py:284-295`).
- **R66** — Kokomi's archetype vocabulary is the sheet's; every adaptive number
  taken through the broken registry is archived, assigned-plan numbers stand
  because they route through `runner.py`'s plan registry
  (`tier0/DECISIONS.md:1989-2060`; `draft.py:1284-1314`).
- **R68** — the canonical cell: `Cell` is the single source of truth for cell
  identity, version fields are read live and never stored, plan→pilot resolves
  only through `runner.resolve_plan`, and **a report without a stamp is not
  citable** (`tier0/DECISIONS.md:2122-2163`; `cells.py:61-149`, `runner.py:62`).
- **R83** — the draft-scorer pass is the authorized policy work; the anchors'
  role labels do not track generic value, so plan bonuses are scaled on
  `archetype == "generic"` only (`tier0/DECISIONS.md:2623-2656`;
  `draft.py:689-736`, `draft.py:1154`).
- **R84** — DRAFTER 11 constants ratified, `STATIC_DEXTERITY_VALUE` added as the
  Strength mirror, `STATIC_POWER_ENGINE_VALUE` kept at 0.0 as a *documented dead
  dial* (`tier0/DECISIONS.md:2658-2698`; `draft.py:738-773`).
- **R87 (3)** — the DRAFTER 13 op repricing: 42 of 56 ops priced at zero biased
  every run-layer winrate; on the bump every DRAFTER-12 number became archive
  (`tier0/DECISIONS.md:2868-2879`; `draft.py:775-1003`).

## 5. Traps

- **Every published number is world-stamped, and worlds are not comparable.**
  RUNTEMPLATE 4→5→6→7 each broke seed comparability (v6 totally — the template
  is gone); DRAFTER and POLICY bumps archive their predecessors
  (`tier0/constants.py:580-628`, `:821-917`). Check the stamp before quoting.
- **`node_template()` and `ELITES_PER_ACT` are DEAD but must not be deleted** —
  they name the v5 spine archived tools were measured on
  (`model.py:236-241`, `acts.py:46-50`). `RUN_NODE_TEMPLATE` likewise
  (`tier0/constants.py:629-631`).
- **Adaptive policies must never see the assigned label.** `emergent_plan`
  (`draft.py:1481`) is read at *three* sites — rest smithing, shop buying and
  events (`model.py:396-400`, `:461-465`, `:497-500`). A fourth decision channel
  added without it silently re-labels adaptive runs (measured: 5/40 seeds
  diverged, 2/40 win flips — `draft.py:1475-1480`).
- **`route_regret` does not exist.** The research doc mandates it as a day-one
  countermeasure and `route.py`'s header used to claim it shipped; nothing
  defines it (`route.py:13-15`, `docs/missed-requirements.md:93-104`). The
  hunter-vs-cautious A/B is the only route countermeasure that is real.
- **Do NOT calibrate `MAP_ROOM_ODDS` or the route policies against a winrate.**
  The target is player behaviour — median ~2.5 elites fought per act, range 1-4
  — and tuning a difficulty dial to a winrate already had to be retracted once
  in this branch (`route.py:17-27`, `tier0/constants.py:656-660`,
  `tier05/tests/test_maps_and_routing.py:1-10`).
- **The map generator carves paths; it does not roll widths.** The first version
  rolled a width per floor and produced lane-locked maps where 9% of
  elite-hunting routes reached zero elites — widening floors did not help,
  because *connectivity* was binding (`maps.py:91-111`). Elite-not-twice-in-a-row
  is enforced at walk time by the draw, not by the generator
  (`maps.py:12-14`, `acts.py:226-233`).
- **`resolve_unknown` MUTATES the weights dict it is handed** — that is the
  real game's pity rule, reset per act (`maps.py:155-182`).
- **Priced-at-zero drafter constants are measurements, not oversights**
  (draw/energy/spark/burst, `raise_fanfare_cap`, `crash_fanfare`,
  `strip_block`, `GENERIC_REDUNDANCY_PENALTY`, `STATIC_POWER_ENGINE_VALUE`).
  Each is kept as a *named* constant so the next pass starts from a dial
  (`draft.py:797-813`, `:721-725`, `:754-773`).
- **`reaction`'s lean penalty STACKS with the global bloat line past
  `DRAFT_DECK_SOFT_CAP`** — unreachable today, so re-sweep before trusting
  either coefficient past 22 cards (`draft.py:1219-1226`).
- **`_drafted_readers` excludes basics on purpose**: Furina's starter carries a
  Fanfare read, so counting it would close the reader limb at run start forever
  and feed `_core_progress` a constant (`draft.py:244-261`).
- **`cells` ↔ `runner` is a deliberate one-way module edge.** `cells` imports
  `runner` at *call* time and `runner` imports `cells` inside `main()`; moving
  either to module scope reintroduces the cycle (`runner.py:25-30`,
  `cells.py:49-58`).
- **`understudy/policy_v0.py` is FROZEN and delegates into these files**
  (`draft.assigned_policy`, `draft.score_offer`, `model.rest_action`,
  `tier05.route`) — `understudy/policy_v0.py:9-10,193,315`. It is one arm of a
  published measurement, so a scoring change here retroactively moves a quoted
  number.
- **`--ab` is refused for Furina**: the adaptive classifier only recognizes
  Klee's shapes (`runner.py:126-131`).
- **The CLI reconfigures stdout to UTF-8** because the death-heatmap block glyph
  killed the report mid-table on a cp1252 console (`runner.py:136-140`).

## 6. Reading order

1. `tier05/__init__.py` + `tier0/constants.py:578-700` — the scope sentence and
   the run-model / map constants with their version history.
2. `tier05/model.py` — `run_one`: the node loop everything else plugs into.
3. `tier05/maps.py` then `tier05/route.py` — how node kinds and the path are
   produced, and the confounder warning that governs both.
4. `tier05/acts.py` — encounter pools, the key allowlist, `ActDraw`.
5. `tier05/draft.py` — read the module docstring, `core_complete`/
   `_core_progress`, `score_offer`, `assigned_policy`, then the constants blocks
   (they are the measurement record).
6. `tier05/cells.py` + `tier05/runner.py` — cell identity, stamps, plan→pilot.
7. `tier0/DECISIONS.md` — search the R-number before changing any behaviour.
