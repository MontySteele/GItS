## Simulate

Tier-0 combat balance (Monte Carlo, 7-axis scorecard, anchor
`ref_ironclad/starter = 3.0`):

```sh
PYTHONPATH=. python3 -m tier0.harness.runner --character klee --deck reaction_weighted --pilot reaction --fights 1000
PYTHONPATH=. python3 -m tier0.harness.runner --score --character klee --deck demolition_weighted
PYTHONPATH=. python3 -m tier0.harness.runner --report-character --character furina --fights 1000
```

Tier-0.5 run-level sim + drafter (decks emerge from drafting):

```sh
PYTHONPATH=. python3 -m tier05.runner --character klee --archetype demolition --runs 500 --seed 42
PYTHONPATH=. python3 -m tier05.runner --character furina --archetype salon --realistic --runs 600 --seed 11 --jobs 0
PYTHONPATH=. python3 -m tier05.runner --character klee --ab --runs 500
```

**Every published number is world-stamped, and worlds are not comparable.**
Run experiments through a `Cell` so the report carries its stamp; a report
without a stamp is not citable (R68). **Running a REGISTERED cell is the
`sitting` skill**, not a command line assembled here: world-check → the
packet's exact command → provenance header → blind grade → registers → gate.
`jobs` is a wall-clock lever only — run
*i* is a pure function of `seed + i`. Depth: `docs/current/atlas/tier0-harness-tests.md`,
`tier05-sim-core.md`, `tier05-economy.md`, `tier05-metrics.md`.

Pilot-policy weight sweep (`W4`, `EB-118`) — the pilot weights that live in
`tier0/pilot/policy.py` rather than in `constants.py`, which is why
`tier05.sweeps` cannot reach them:

```sh
PYTHONPATH=. python3 -m tier05.pilot_weight_sweep                       # plan only, runs NOTHING
PYTHONPATH=. python3 -m tier05.pilot_weight_sweep --execute --stage coverage --jobs 0
PYTHONPATH=. python3 -m tier05.pilot_weight_sweep --execute --stage screen  --jobs 0
PYTHONPATH=. python3 -m tier05.pilot_weight_sweep --execute --stage search  --jobs 0 --axes <the LIVE axes coverage named>
PYTHONPATH=. python3 -m tier05.pilot_weight_sweep --execute --stage confirm --jobs 0 --point-json P.json
```

Run the stages in that order: coverage says which weights are read at all, the
screen moves one axis at a time, the search combines only the axes coverage
kept live, and confirm re-runs one candidate on a **held-out seed**. `--execute`
is mandatory — the bare command prints the design and exits. **`--jobs` is a
wall-clock lever at the (point, cell) level only**: every cell is pinned to
`jobs=1` internally, because a `run_many` worker re-imports `policy.py` and
would run the shipped weights while the parent believed it was sweeping.
**ONE gate per sweep** (`--gate`): `PILOT_POLICIES_ENABLED` and
`MODE_CHOOSER_ENABLED` are separate activation windows (R191), and forcing both
would put two of them through one measurement. That is R207's rule, not a
stricter one — the separation is owed exactly where attributing the movement to
one gate is what the next decision turns on. Where nothing turns on that
attribution the two may share a window, and under R212 that call is Claude's
whenever the scratch read is null (disclose the scratch hash and the null read);
the stamp then labels the world and the number belongs to the window, not to
either gate. A weight no measurement cell READ is refused rather than printed
(R67/R33) — that refusal is the instrument working, and the answer to it is to
leave the weight alone. Only a DOMINATING point that reproduces at confirm may
be adopted, and adopting one is its own `PILOT_WEIGHTS_VERSION` bump; TRADE,
INSEPARABLE, a SHARED weight, an adopted zero and any stack-cap move are
[USER]'s. The design, the grid, the five cells and the decision rule are the
module's own docstring — it documents itself,
`understudy/soak.py`'s pattern, so the design cannot drift from the code.
