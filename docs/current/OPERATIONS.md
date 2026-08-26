# OPERATIONS

How to build, test, simulate, generate, and ship. Commands run from the repo
root. Depth for any subsystem lives in `docs/current/atlas/` — this file is the
index of what to type, not how it works.

## Environment

- Python 3.12. No requirements file in-tree; the suite's actual imports are
  `pytest pyyaml pillow numpy`. CI installs exactly those. `pytest-xdist` is
  optional, local, and not in that list — see the parallel-suite section below
  for what it buys and why CI does not install it.
- Most sim entry points need `PYTHONPATH=.`. Codegen and tools run as
  `.venv/bin/python tools/<x>.py` (Windows: `.venv/Scripts/python`).
- `tools/` is an implicit namespace package: both `python3 tools/x.py` and
  `from tools import x` work.

## Mechanisms — what is enforced, and by what

**Correction D (2026-08-26).** Claude treats `CLAUDE.md` and this file as
CONTEXT, not as enforced configuration — the official guidance is explicit:
*to block an action regardless of what Claude decides, use a PreToolUse hook*.
A rule that lives only in prose is advice a long session can lose. Every rule
in the table below used to be a paragraph in this file and is now a hook, a
skill or a lint, and **the prose it replaced is DELETED rather than kept
beside it**: two statements of one rule is one too many, and the copy that is
not executable is the one that rots.

`.claude/settings.json` wires the hooks. Each is a small portable Python
script that reads the hook payload on stdin and exits 0 (allow) or 2 (block,
with a one-line reason shown to Claude), so it behaves the same from Git Bash
and from PowerShell.

| event | matcher | script | what it refuses / does |
|---|---|---|---|
| PreToolUse | `Bash` | `tools/hooks/deny_dangerous_git.py` | `git add -A` / `.` / `--all`; `git worktree remove`; `git push` at `main` or forced; `--no-verify` on `commit` or `push` |
| PreToolUse | `Bash` | `tools/hooks/push_gate.py` | a real `git push` runs the fast lane + `run_lints --lane ci` first (~21 s measured) and is BLOCKED on red or on timeout |
| PostToolUse | `Edit\|Write\|NotebookEdit` | `tools/hooks/game_ref_backup_reminder.py` | an edit under `game_ref/` prints the vault-backup reminder; `GITS_HOOK_RUN_BACKUP=1` runs the mirror instead |

Skills (`.claude/skills/<name>/SKILL.md`) carry the procedures this file used
to narrate: **`sitting`** — a registered experiment's run, world-check to
commit; **`deploy`** — `build_pck` → `deploy` → `validate`; **`worktree`** —
add, the no-link rule, purge.

Lints, all registered in `run_lints`'s `ci` lane: `register-shape`,
`stamp-rows`, `sheet-stamp`, `experiments-active`, `hook-self-tests`. The four
register/stamp lints ship **green** by carrying a curated `DEBT` set of the
rows that fail today — 42 register rows, 3 stamp rows, 4 registrations — so
the gate binds from this commit forward while the existing rows stay a work
list. A `DEBT` entry that has since become clean FAILS, so the sets can only
shrink; empty one and the lint becomes ordinary.

**What a mechanism cannot reach.** A hook sees a tool call, not an intention:
nothing here can tell that a *sitting* skipped its blind grade, that a `QUEUE`
row was answered by Claude rather than by [USER], or that a design call was
settled without being asked. Those stay norms in `CLAUDE.md`, and the lints
above gate only their SHAPE — that a row has an ask and a gate, never that the
ask was honoured.

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

### RATIFIED [USER] 2026-08-24 — parallel suite, fast lane, concurrent lints

Measured 2026-08-24 on the 16-CPU Windows box, branch `test-speed`, from
`origin/main` `4bbc9bc`. **Nothing below changes a default**: `pytest.ini`
registers marker names and sets no `addopts`, so a bare `python -m pytest`
and CI's line behave exactly as before. What was proposed, and is now
ratified, is the *workflow* — the discipline at the end of this section.

One optional local dependency, deliberately NOT added to CI's install line:

```sh
python -m pip install pytest-xdist      # 3.8.0, pulls execnet 2.1.2
```

```sh
python -m pytest tier0/tests tier05/tests -q -n auto --dist loadscope
python -m pytest tier0/tests tier05/tests -q -m "not battery" -n auto --dist loadscope
python tools/run_lints.py               # concurrent lint battery, ci + local lanes
python tools/run_lints.py --lane ci     # exactly CI's `lints` job
python tools/run_lints.py --list        # the registry, and any lint missing from it
```

| arm | wall clock | items run |
|---|---|---|
| full suite, serial (today's gate) | 152–159 s | 3195 |
| full suite, `-n auto` (16) `--dist loadscope` | 35 s | 3195 |
| full suite, `-n 8 --dist loadscope` | 36 s | 3195 |
| fast lane, `-m "not battery" -n auto` | 13 s | 3113 (97.4%) |
| fast lane, `-m "not battery"` serial | 55 s | 3113 |
| lints, serial (17 tools) | 5.3 s | — |
| lints, concurrent (17 tools) | 1.0 s | — |

Pass/skip/xfail counts are identical across every arm (3138 / 45 / 12; the
fast lane drops 82 items and nothing else). Two back-to-back `-n auto` runs
agreed to 0.4 s and no test flaked, so no test needed a `serial` marker and
none was added — `battery` is the only marker registered.

`--dist loadscope` is load-bearing, not a preference: it keeps a module on one
worker, so a module-scoped battery fixture (`test_pass3.klee_report`,
`test_silent.silent`, `test_axes.package`) is computed once instead of once
per worker. The knee of the curve is at 8 workers; 16 buys about 1 s more,
because past that point the run is bounded by the longest single module scope
plus per-worker collection.

`battery` marks the 52 test functions (82 collected items) whose time is spent
in a Monte-Carlo battery (`run_battery` / `score_config` / `score_character`)
or a run-level sim (`model.run_many`, repeated route walks) **and** that cost
at least 0.45 s serially. Everything else stays in the fast lane by
construction: sheet lints, codegen checks, encoding and register gates, the
event-pool resolution sweep, the C#-parity pins.

The discipline, **RATIFIED** ([USER] 2026-08-24; the verbatim is in the
ratifying commit, per CLAUDE.md — no R-number was minted, the same
date-attributed shape the C11 ruling took):

- **inner loop** — the targeted tests for what you are editing, plus the fast
  lane. Seconds, not minutes.
- **before any push** — the FULL suite (`-n auto --dist loadscope`) and the
  full lint battery. The fast lane is never the gate: the deselected 82 items
  are the calibration bands, and a band that was not run is not a band. Since
  Correction D a push that ran NOTHING is refused outright by
  `tools/hooks/push_gate.py`, which runs the fast lane and the `ci` lint lane
  in ~21 s — **a floor under this rule, not a substitute for it.** The hook
  cannot afford the bands; you can.
- **bare `pytest` stays bare.** No `addopts`. Anyone who types the CI line
  gets the CI run.

CI is deliberately untouched. A hosted `ubuntu-latest` runner has 2–4 vCPU, so
the gain there is the `-n 4` shape (52 s measured here) rather than the `-n 16`
shape — real, but roughly a third of the local saving, and it would put a
plugin install on the critical path of the one job that asserts the fresh-clone
world is sound. That trade is [USER]'s to make, not this branch's.

Two facts this measurement turned up, neither fixed here:

- `tools/lint_role_tempo_coverage.py --gate` is **green** — 17 findings against
  the 17 then pinned when this was measured on `4bbc9bc`, and 18 against 18
  since the `EB-118` Window-1 label pass disclosed an inherited
  `furina/spotlight frontload|mid` gap. Only the bare invocation, which no gate
  uses, exits 1.
- `tools/card_distinctness_report.py --gate` exits **2** — "NO OFFICIAL ANCHOR
  IN THIS RUN" — on the art-bearing main checkout as well as in a worktree,
  because its official pools want `tools/extract_base_game_pool.py` to have
  been run first. It is a standing red in the local-only lane, so
  `run_lints.py --lane ci` is the arm that goes green today.

## game_ref backup — the OneDrive vault

`game_ref/` is gitignored, decompile-derived, and half of it is thirteen
hand-authored pass layers that no tool can regenerate. It has been destroyed
four times. RULED [USER] 2026-08-24: *"Agreed on the backup in OneDrive"* — the
durable copy lives at

```
C:\Users\Monty\OneDrive\GItS-vault\game_ref
```

hard-coded in `tools/backup_game_ref.py` (a configurable backup root is one
that can be pointed somewhere temporary and quietly stop being a backup).

```sh
python -m tools.backup_game_ref             # mirror local -> vault
python -m tools.backup_game_ref --dry-run   # what it would do
python tools/lint_game_ref_backup.py        # staleness tripwire, never writes
```

**Run the backup after ANY restore, extraction, or hand edit of `game_ref/`** —
after `tools.extract_base_game_pool` + `tools.build_official_sheet`, after
restoring pass layers from anywhere, after editing a `*_char_facts.yaml` by
hand. Two mechanisms carry this now: `tools/hooks/game_ref_backup_reminder.py`
fires on any Edit/Write under `game_ref/` (git cannot — the tree is ignored,
so `git status` is clean by construction), and the staleness tripwire is in
`run_lints.py`'s **local** lane, so a normal `python tools/run_lints.py` says
when the vault has fallen behind.

**The guard is the tool's reason to exist.** `backup_game_ref` REFUSES (exit 2,
loud, vault untouched) when local `game_ref/` is missing or holds fewer than ten
files — every destruction so far left the directory *present and empty* with
`git status` clean, and a mirror run "to be safe" in that state would take the
last copy with it. **If local `game_ref/` is empty, the vault is the source —
copy the other way.**

The lint's three verdicts — absent/empty, under ten files, ten or more — and
why each is a NOTE or a failure are in `lint_game_ref_backup.py`'s own
docstring, where they cannot drift from the code that implements them.

**Backups never live in worktrees.** The vault is outside every checkout
because a worktree teardown deletes gitignored content; the `worktree` skill
and the deny hook carry the rest of that rule.

**A missing layer fails at the door, not mid-cell.** Asking for a `real_*` arm
without `game_ref/` raises `loader.MissingReferenceLayer` out of
`tier05.runner.resolve_plan` before any run starts, and the message names this
tool as the restore point. **Never stub, fabricate or approximate the layer to
make an anchor load** — a stubbed `real_ironclad` produces numbers that look
like floors and are not.

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

**The sequence is the `deploy` skill** — pre-deploy checks, `build_pck.ps1`,
`deploy.ps1` (which runs `validate.ps1` itself before copying), and the opt-in
C# suite. From a worktree the one legal command is
`klee-mod\build\deploy_bridge.ps1 -BuildOnly` (`EB-142`).

### Understudy — targeted scenarios (attended only)

```
python -m understudy.scenario check                            # parse only, no game
python -m understudy.scenario run understudy/scenarios/spark-gate-refusal.yaml \
    --why "EB-142: does the Spark gate show as unplayable"
```

Needs the bridge DEPLOYED (`klee-mod\build\deploy_bridge.ps1`, no `-BuildOnly`),
`steam_appid.txt` in the game root, Steam running. Setup and teardown are the
soak's, via `soak.run_scripted`; the scenario itself starts at the first fight.

`--why` is required and is logged on every row, and every row also carries
`bridge.GRANT_GUARDRAIL`: a scenario grants a card and writes a board through
`/api/v1/gits/debug_state`, so **nothing measured on one is comparable to any
soak, any run, or any other scenario**. Guardrail-7 and the no-fun rule are
unchanged — it asserts numbers (HP, Block, power stacks, resource amounts,
prompts, `can_play`, `unplayable_reason`, printed text) and a failed assert is a
defect, never a design finding. It is deliberately unreachable from `soak.py`;
`tier0/tests/test_understudy_scenario.py` pins that. Depth:
`understudy/README.md` and `docs/current/atlas/understudy.md`.

`KleeTests` (`EB-105`) runs the shipped `klee.dll` against the real game
assemblies **headless** — no Godot, no launch. It is opt-in, not a deploy gate;
its boundary and its co-op coverage are in `klee-mod/KleeTests/README.md`.

Machine paths come from `klee-mod/local.props` / `Directory.Build.props`.
Depth: `docs/current/atlas/klee-mod-build-pck.md`, `klee-mod-runtime.md`.

## Lints

CI's `lints` job invokes these directly (the softlock gates):

```sh
python3 tools/lint_handwritten_parity.py   tools/lint_constant_parity.py   tools/lint_op_parity.py
python3 tools/gen_roster_cards.py --check
python3 tools/lint_pool_membership.py       tools/lint_ancient_coverage.py
python3 tools/suggest_role_tempo_tags.py --check    tools/lint_role_tempo_coverage.py --gate
python3 tools/lint_roster_registry.py       tools/lint_upgrade_suffix_appends.py
python3 tools/lint_vendor_pin.py            tools/art_coverage.py
```

Correction D added five more to `run_lints`'s `ci` lane that `repo.yml` does
not yet name (`lint_register_shape.py`, `lint_stamp_rows.py`,
`lint_sheet_stamp.py`, `lint_experiments_active.py`,
`tools/hooks/selftest_all.py`) — see Mechanisms. `lint_sheet_stamp.py
--update` is the one that re-pins `SHEET_DIGEST` after a sheet edit, and it
belongs in the same commit as the edit.

Local-only (not in CI): `lint_text_encoding.py`, `lint_generated_structure.py`,
`art_lint.py`, `card_distinctness_report.py --gate`,
`lint_game_ref_backup.py`, `dump_claimed_sources.py`.
`tools/README.md` is the authoritative map of which tool is gated by what.

`tools/run_lints.py` runs the whole battery concurrently and prints one row per
tool with its exit code — see the parallel-suite section. It carries the
registry those two lists describe, and fails the run if a `tools/lint_*.py`
appears that no registry row names, so the list above cannot go stale in
silence.

Suite-gated (runs under `pytest`, not in the CI `lints` job):
`lint_recall_exhaust.py` (`EB-118`, merged **inert** 2026-08-23; gate
`tier0/tests/test_eb118_recall_exhaust.py`).

```sh
python3 tools/lint_recall_exhaust.py       # exit 1 with findings on stdout
```

Three sweeps in one tool — card shape, engine closure, a structural C# pin —
all enforcing `EB-118` §6.4's six constraints on `recall_to_draw` with
`from: exhaust`. Each leg, and why leg (a) is deliberately vacuous until a
committed sheet row ships `from: exhaust`, is in the tool's own docstring.

Encoding rule is repo-wide and structural: **every text read/write declares
`encoding=`** (an omitted encoding is cp1252 on Windows, UTF-8 on CI). The
content path carries zero encoding debt.

**The rule extends to `sys.stdout`** (EB-93, 2026-08-13). A console's encoding
is chosen by the terminal, not by the file that prints, so a tool that echoes
shipped content — card titles carry `♪` — raises `UnicodeEncodeError` on a
default Windows console and takes the process exit code with it. Any entry
point that prints content declares the console too:
`understudy.report.console_safe()` at the top of `main` (UTF-8, falling back to
`backslashreplace`, never raising).

## Worktrees — one working directory per workstream

**The procedure is the `worktree` skill** — sibling-directory add, the
never-link-a-gitignored-asset-tree rule, `python -m tools.purge_worktree`
instead of `git worktree remove` (which the deny hook refuses), and prune.
Sessions never share a working directory; collisions happen *before* commit,
where CI cannot look. Rationale and incident history:
`docs/current/rationale/`.

## CI (`.github/workflows/repo.yml`)

Three jobs, all on `ubuntu-latest`: **(a) `pytest`** — the fresh-clone gate;
**(b) `lints`** — the softlock lints above, invoked directly; **(c)
`patch-sentinel`** — advisory, `continue-on-error`, never blocks a merge (a
runner has no game, so it prints `skipped` by design). Set the `repo` check as
required on `main` in branch protection ([USER]'s to click).
