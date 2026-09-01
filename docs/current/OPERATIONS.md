# OPERATIONS

An index, and the handful of commands every session needs. Everything else
lives in one file under `docs/current/operations/`, named for the task. Open
the one your task reaches; never all of them. Depth for any subsystem is in
`docs/current/atlas/`. Commands run from the repo root.

## Open the file your task names

| Your task | File |
|---|---|
| install Python, the deps, the venv | `operations/environment.md` |
| find out what is enforced, and by what | `operations/mechanisms.md` |
| run the suite, the fast lane, the parallel lanes | `operations/test.md` |
| run the tier-0 or tier-0.5 sim, read a stamp | `operations/simulate.md` |
| regenerate the C# cards from a YAML sheet | `operations/codegen.md` |
| move a kit Paper to Prototype to Balance | `operations/stage-gate.md` |
| add, try or delete a quarantined prototype row | `operations/prototype.md` |
| fetch, process or lint art | `operations/art.md` |
| build the pck and deploy into the game | `operations/build-deploy.md` |
| run a scenario, a staged round, a seat or blind play | `operations/understudy-seats.md` |
| brief an agent, or work out what it should read | `operations/briefing.md` |
| run the lints, or add one | `operations/lints.md` |
| add or retire a worktree | `operations/worktrees.md` |
| read or change what CI runs | `operations/ci.md` |
| back up or restore `game_ref/` | `operations/game-ref-backup.md` |
| repair the pin after Steam moves the game | `operations/steam-moves.md` |

## The commands every session needs

Run the suite. `tier0/tests` plus `tier05/tests` is the gate wall, not a unit
suite. Tests are cwd-sensitive, so run them from the repo root.

```sh
python3 -m pytest tier0/tests tier05/tests -q          # what CI runs
GITS_REFERENCE_MODE=committed-only python3 -m pytest tier0/tests -q   # fresh-clone mode
```

Run the sim. Tier-0 is combat balance against the `ref_ironclad/starter = 3.0`
anchor; tier-0.5 is the run-level sim, where decks come out of drafting.

```sh
PYTHONPATH=. python3 -m tier0.harness.runner --score --character klee --deck demolition_weighted
PYTHONPATH=. python3 -m tier05.runner --character klee --archetype demolition --runs 500 --seed 42
```

Regenerate the cards. The generator writes the C# from the YAML sheets, and
`--check` verifies the committed output without writing.

```sh
.venv/bin/python tools/gen_roster_cards.py           # generate all profiles
.venv/bin/python tools/gen_roster_cards.py --check    # verify, no write
```

Run the lints. `run_lints.py` is the one entry point; its `ci` lane is what the
`lints` job in `.github/workflows/repo.yml` invokes.

```sh
python tools/run_lints.py --lane ci      # the softlock gates CI runs
python tools/run_lints.py --list         # every lint, by lane
```

Build and deploy. The sequence is the `deploy` skill: pre-deploy checks,
`build_pck.ps1`, then `deploy.ps1`, which runs `validate.ps1` itself before it
copies anything. Windows, and only on the art-bearing main checkout.
`operations/build-deploy.md` has the rest.

Deploy a prototype arm. Prototype rows are quarantined out of every pool and
ship only on a `+proto` dev build. `operations/prototype.md` has the flag and
the deletion rule; `understudy/embark.py --arm` is what grants a row into a
starting deck once a run is open.
