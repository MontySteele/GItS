## CI (`.github/workflows/repo.yml`)

Three jobs, all on `ubuntu-latest`: **(a) `pytest`** — the fresh-clone gate;
**(b) `lints`** — exactly `python tools/run_lints.py --lane ci` (the same list
the pre-push hook runs; `operations/lints.md`) plus the deploy gate's static
rules; **(c)
`patch-sentinel`** — advisory, `continue-on-error`, never blocks a merge (a
runner has no game, so it prints `skipped` by design). Since 2026-09-28
`pytest` is a four-shard matrix whose rows read `pytest (1/4)` to
`pytest (4/4)` (see "Speed pass two" below). `main` has no branch protection
and no required checks today, which is what made that rename safe; if
required checks are ever added, require `lints` and the four `pytest (n/4)`
rows. `lints` and `patch-sentinel` are still named as they were.

### The deploy gate's static rules run here too (2026-09-02)

The `lints` job gained one step, `deploy gate static rules`: `pwsh
./klee-mod/build/validate_static.ps1`, which runs `validate.ps1`'s S4 (pool
registration), S5 (loc template syntax) and S8 (build scripts pure ASCII) in
about 4 s. They read committed text and nothing else, and they call the SAME
functions the deploy gate calls (`klee-mod/build/static_rules.ps1`) — one
implementation, two callers, so a finding here is the string that would refuse
the deploy.

A STEP, not a job, because the three job names above are load-bearing. Why it
exists: PR #291 put the base game's `[blue]` numeral colour on every power
face, this workflow was green, it merged, and the next deploy was refused by
S5 — a regex over C# that a runner executes in seconds. Rules that need the
staged package, the game install, the built pck or the pytest suite stay at
deploy time; `static_rules.ps1`'s header has the table and the reason for each.

### The one gate that is NOT here: the mod's C# suite (2026-09-02)

`klee-mod/KleeTests` runs locally and only locally, and that is a fact about
the assemblies rather than a preference: the project references `sts2.dll`,
`0Harmony.dll`, `GodotSharp.dll` and the Workshop `BaseLib.dll` — four binaries
that live in a Steam install, are gitignored, and are not ours to publish — so
no `ubuntu-latest` runner can hold the check at all (the same reason
`patch-sentinel` prints `skipped` here, and the reason the NOT-doing list at the
head of `repo.yml` refuses a Windows runner). Until 2026-09-02 that meant it was
in **no** gate: optional behind `gates.py --dotnet`, absent from this workflow,
absent from the push hook — and two pins sat red on `main` for days with every
badge green (a roster sweep in `CompanionOverhaulTests`, and the Kokomi Plan
clause-count pin that R236's twelfth clause moved). It is now a first-class gate
in `tools/gates.py`, in **both** lanes and no longer optional, running `dotnet
test klee-mod/KleeTests` twice: the default build, which since 2026-09-28 is
the current kits (`klee-mod/Directory.Build.props`), and `-p:ShippedKits=true
-p:PrototypeCards=true`, the old shipped kits with the arms compiled but off,
and the git `pre-push` hook runs it through that same wrapper — one
implementation, two callers. Its line in the gates output says `local-only: no
game dlls on a runner` every time, green or red, so a green CI run is never read
as evidence about it; a machine with no `dotnet` or no `local.props` gets a
**skip with its reason**, never a silent pass and never a blocked push.

### Speed pass, 2026-08-29

Three changes, no jobs added or renamed:

1. **`pytest` runs in parallel** — `-n auto --dist loadscope`, the same arm
   `tools/hooks/push_gate.py` runs, minus the gate's `-m "not battery"`
   deselection. CI keeps the bands.
2. **A docs-only fast path.** `tools/ci_changed_paths.py` (with `--self-test`)
   answers `docs_only=true` only when EVERY changed path is a `.md` file under
   `docs/current/`, `review/`, or the repo root. Anything else — a card sheet,
   a `review/qa` JSON, a `.py`, a `.cs`, the workflow itself — is `false`, and
   so is an empty or unreadable diff (it **fails safe** to the full run). On
   `true`, the `pytest` job runs only the modules that read committed
   markdown (named in the workflow) and prints a
   loud notice saying what it skipped; `patch-sentinel` skips its two steps.
   The **`lints` job always runs in full**.
3. **pip cache** — `cache: 'pip'` keyed on `.github/requirements-ci.txt`,
   which all three jobs install from.

No `paths-ignore` at the trigger level, ever: a trigger-level filter makes a
job report *nothing* rather than report success, and a required check that
never reports blocks the pull request forever. That is precisely why the
docs-only decision lives inside a job that always runs. A `concurrency:` block
(cancel superseded runs on one branch) is optional and unclaimed.

### Speed pass two, 2026-09-28

The `pytest` job took 8.5–9 minutes, all of it the suite. Two changes; no test
deleted, skipped or loosened, and no battery size, seed or band moved:

1. **Waste out of the suite.** PyYAML's pure-Python parser was 45% of all test
   time (387 of 863 s summed over workers), nearly all of it the same sheets
   parsed over and over. `tier0/content/yaml_memo.py` (and its twin
   `understudy/yaml_memo.py`, a copy because the blind seat may not import
   `tier0`) parses each distinct text once with the same parser and returns
   a deep copy every call; `tier0/tests/test_yaml_memo.py` proves the data is
   identical on every committed sheet. Also fixed: a test re-parsing the
   prototype surface once per generated file, a test sleeping out a 10 s
   relaunch gap an earlier test left behind, and stub HTTP servers that
   waited 0.5 s on their own shutdown.
2. **Four shards.** `tools/ci_shards.py` splits the suite by file (a module is
   never split, for the loadscope reason), balanced by the per-file seconds in
   `.github/test-durations.json`, heaviest first; each shard still runs
   `-n auto --dist loadscope`. It fails safe: the file list comes from the
   disk, so a file with no timing still lands in a shard, and the `lints` job
   runs `ci_shards.py --of 4 --verify`, which fails unless the four shards
   together collect exactly the full suite. Refresh the timings with
   `python tools/ci_shards.py --update-durations <junit.xml>` when the shards
   drift apart; stale timings cost minutes, never coverage. On a docs-only
   change shard 1 runs the markdown-reading list and shards 2–4 report green
   with a notice.

A `concurrency:` block is still [USER]'s call and still not added.

The blind spot, stated plainly: a docs-only pull request does not run the rest
of pytest. It does not need to — no markdown under those three trees is read
by anything else — and the push gate ran the whole fast lane locally before
the push regardless. If a test starts reading one of those trees, add its
module to the docs-only list in `repo.yml`.
