# OPERATIONS

How to build, test, simulate, generate, and ship. Commands run from the repo
root. Depth for any subsystem lives in `docs/current/atlas/` — this file is the
index of what to type, not how it works.

## Environment

- Python 3.12. No requirements file in-tree; the suite's actual imports are
  `pytest pyyaml pillow numpy`. CI installs exactly those.
- Most sim entry points need `PYTHONPATH=.`. Codegen and tools run as
  `.venv/bin/python tools/<x>.py` (Windows: `.venv/Scripts/python`).
- `tools/` is an implicit namespace package: both `python3 tools/x.py` and
  `from tools import x` work.

## Test — the gate wall

`tier0/tests` + `tier05/tests` is not a unit suite; it is the repo's gate wall
(engine pins, sheet/content lints, C#-parity, art checks, encoding/convention
lints, frozen-battery calibration bands, understudy contracts).

```sh
python3 -m pytest tier0/tests tier05/tests -q          # what CI runs
GITS_REFERENCE_MODE=committed-only python3 -m pytest tier0/tests -q   # fresh-clone mode
```

`GITS_REFERENCE_MODE=committed-only` hides the gitignored `game_ref/` pool
atomically, reproducing the bare-clone world CI actually starts from. CI does
NOT set it (a runner has no `game_ref/`), and that is the point: the `pytest`
job asserts the *committed* world is sound. Tests are cwd-sensitive — run from
the repo root.

## Simulate

Tier-0 combat balance (Monte Carlo, 7-axis scorecard, anchor
`ref_ironclad/starter = 3.0`):

```sh
PYTHONPATH=. python3 -m tier0.harness.runner --character klee --deck reaction_package --pilot reaction --fights 1000
PYTHONPATH=. python3 -m tier0.harness.runner --score --character klee --deck demolition_package
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
without a stamp is not citable (R68). `jobs` is a wall-clock lever only — run
*i* is a pure function of `seed + i`. Depth: `docs/current/atlas/tier0-harness-tests.md`,
`tier05-sim-core.md`, `tier05-economy.md`, `tier05-metrics.md`.

## Codegen — roster cards

One character-aware generator emits the C# card classes from the canonical
YAML sheets. Klee is the compatibility baseline; Furina and Kokomi are the
other profiles.

```sh
.venv/bin/python tools/gen_roster_cards.py           # generate all profiles
.venv/bin/python tools/gen_roster_cards.py --check    # verify committed output, no write
```

The generator rejects unknown card-level fields as well as unknown effects
(load-bearing: `encore_cost` changes playability without being an effect).
Partial upgrades are forbidden — a card gets its complete ruled upgrade or lists
under `upgrades.no_upgrade_path`. Depth: `docs/current/atlas/klee-mod-cards.md`.

## Art pipeline

Tier F art never ships and never enters the repo; only the ledgers
(`art/SOURCES.tsv`, `art/plan.tsv`) and the tools are tracked.

```sh
python3 tools/art_fetch.py && python3 tools/art_process.py [--apply-picks art/picks.tsv]
python3 tools/art_coverage.py            # CI runs it WITHOUT --strict (empty bill on a runner)
python3 tools/art_hunt.py Furina ; python3 tools/art_contact_sheet.py --list
.venv/Scripts/python tools/cut_combat_layers.py klee [--check]
.venv/Scripts/python tools/gen_furina_stills.py    # and gen_kokomi_stills.py
.venv/Scripts/python tools/gen_char_icon_outlines.py [--check]   # all three outline halos
```

`art/plan.tsv` is UTF-8 + CRLF — read with `encoding="utf-8", newline=""` and
`rstrip("\r\n")`, or the last column silently stops matching. Depth:
`docs/current/art/` and `docs/current/atlas/tools.md`.

## Build & deploy (Windows, art-bearing main checkout only)

```
tools\build_pck.ps1            # one character-aware resource pack + klee.pck.contract.txt
klee-mod\build\deploy.ps1      # stages the pack; rejects a missing/stale/mismatched contract
klee-mod\build\validate.ps1    # the S-gate deploy validation
```

After any roster-resource change, run `build_pck.ps1` **before** `deploy.ps1` —
an old Klee-only PCK cannot pass validation. Machine paths come from
`klee-mod/local.props` / `Directory.Build.props`. Depth:
`docs/current/atlas/klee-mod-build-pck.md`, `klee-mod-runtime.md`.

## Lints

CI's `lints` job invokes these directly (the softlock gates):

```sh
python3 tools/lint_handwritten_parity.py   tools/lint_constant_parity.py   tools/lint_op_parity.py
python3 tools/gen_roster_cards.py --check
python3 tools/lint_pool_membership.py       tools/lint_ancient_coverage.py
python3 tools/suggest_role_tempo_tags.py --check    tools/lint_role_tempo_coverage.py --gate
python3 tools/lint_roster_registry.py       tools/lint_vendor_pin.py       tools/art_coverage.py
```

Local-only (not in CI): `lint_text_encoding.py`, `lint_generated_structure.py`,
`art_lint.py`, `card_distinctness_report.py --gate`, `dump_claimed_sources.py`.
`tools/README.md` is the authoritative map of which tool is gated by what.

Encoding rule is repo-wide and structural: **every text read/write declares
`encoding=`** (an omitted encoding is cp1252 on Windows, UTF-8 on CI). The
content path carries zero encoding debt.

## Worktrees — one working directory per workstream

Sessions never share a working directory; collisions happen *before* commit,
where CI cannot look.

```sh
git worktree add ../GItS-<workstream> -b <sprint-or-topic>-<short-slug>
git worktree remove ../GItS-<name>     # when the workstream lands
git worktree prune
```

- **Sibling directories only**, one branch per worktree, lowercase-hyphen branch
  names (no slashes).
- **Stage explicitly; never `git add -A`.** Read the `--stat` before you push —
  one unexpected filename is the whole signal.
- **NEVER link a gitignored asset directory** (`game_ref/`, `ImageGen/images/`,
  `art/raw/`, `art/candidates/`) into a worktree. `git worktree remove` follows a
  junction/symlink and deletes what it finds — this has destroyed non-regenerable
  `game_ref/` files. A worktree simply lacks art, and that is fine; `build_pck`,
  `deploy`, and art passes happen on the main checkout.

Rationale and incident history: `docs/current/rationale/`.

## CI (`.github/workflows/repo.yml`)

Three jobs, all on `ubuntu-latest`: **(a) `pytest`** — the fresh-clone gate;
**(b) `lints`** — the softlock lints above, invoked directly; **(c)
`patch-sentinel`** — advisory, `continue-on-error`, never blocks a merge (a
runner has no game, so it prints `skipped` by design). Set the `repo` check as
required on `main` in branch protection ([USER]'s to click).
