## CI (`.github/workflows/repo.yml`)

Three jobs, all on `ubuntu-latest`: **(a) `pytest`** — the fresh-clone gate;
**(b) `lints`** — the softlock lints above, invoked directly; **(c)
`patch-sentinel`** — advisory, `continue-on-error`, never blocks a merge (a
runner has no game, so it prints `skipped` by design). Set the `repo` check as
required on `main` in branch protection ([USER]'s to click). **Those three job
names are load-bearing** — they may be required checks, and a renamed job
reports nothing and blocks every pull request. Rename nothing here.

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
   `true`, the `pytest` job runs only the nine modules that read committed
   markdown (named in the workflow, audited over a full run) and prints a
   loud notice saying what it skipped; `patch-sentinel` skips its two steps.
   The **`lints` job always runs in full** — the register, stamp and
   namespace gates are lints, and they are the other half of what a markdown
   edit can break.
3. **pip cache** — `cache: 'pip'` keyed on `.github/requirements-ci.txt`,
   which all three jobs install from.

No `paths-ignore` at the trigger level, ever: a trigger-level filter makes a
job report *nothing* rather than report success, and a required check that
never reports blocks the pull request forever. That is precisely why the
docs-only decision lives inside a job that always runs. A `concurrency:` block
(cancel superseded runs on one branch) is optional and unclaimed.

The blind spot, stated plainly: a docs-only pull request does not run the rest
of pytest. It does not need to — no markdown under those three trees is read
by anything else — and the push gate ran the whole fast lane locally before
the push regardless. If a test starts reading one of those trees, add its
module to the docs-only list in `repo.yml`.
