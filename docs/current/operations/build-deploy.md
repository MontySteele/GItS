## Build & deploy (Windows, art-bearing main checkout only)

**The sequence is the `deploy` skill** — pre-deploy checks, `build_pck.ps1`,
`deploy.ps1` (which runs `validate.ps1` itself before copying), and the opt-in
C# suite. From a worktree the one legal command is
`klee-mod\build\deploy_bridge.ps1 -BuildOnly` (`EB-142`).

### The gate's S7 arm — when the suite runs here, and when CI's run stands

`validate.ps1`'s S7 is the pytest suite. Until 2026-09-02 it ran the WHOLE
repo suite, serially, on every deploy: **399.3 s measured**, in a gate whose
other twelve rules together are about 6 s. CI had already run that same suite,
in parallel, on that same commit. The deploy was re-deriving a fact GitHub was
already holding, and charging eight minutes a build for it.

S7 now picks one of three arms, and the pick is DERIVED rather than passed:

| arm | when | cost |
|---|---|---|
| **TRUSTED** — the suite does not run here | the working tree is clean, `HEAD` is an ancestor of `origin/main`, and GitHub's `pytest` and `lints` check runs for **that exact sha** are green | 0 s, plus one line naming the run it trusted and its URL |
| **FAST** | anything else | 57 s — `tier0/tests` + `tier05/tests`, `-n auto --dist loadscope`, battery deselected: the same arm the push gate runs |
| **FULL** | `-FullGate`, or `pytest-xdist` missing from the venv | 399 s — the old whole-repo serial suite |

`klee-mod/build/ci_trust.ps1` owns the three conditions, and each is checked
separately because none is implied by the others: an uncommitted change is in
no commit CI has seen; a green topic branch is not the tree that ships; and
the branch's latest run is not this commit's run. **Every failure to establish
one is "not proven", and runs the tests** — no `gh`, offline, unauthenticated,
a pending run, a stale local `origin/main` ref, all of them. A gate that waved
a deploy through because it could not reach GitHub would be the R70 failure
class wearing a network error's coat.

`patch-sentinel` is ignored by name: `repo.yml` marks it `continue-on-error`
on purpose, so treating its red as a blocker would import a decision that
workflow has already made.

Dry-run the decision without deploying anything:

```powershell
powershell -NoProfile -Command ". klee-mod\build\ci_trust.ps1; Get-CiSuiteTrust -RepoRoot (Get-Location).Path | Format-List"
```

Force the old behaviour with `-FullGate` on either deploy script. **S1–S6 and
S8–S12 are never skipped by any of this**, and neither is anything else in the
gate.

### The static rules also run in CI

S4 (pool registration), S5 (loc template syntax) and S8 (build scripts pure
ASCII) read committed text and nothing else. They live in
`klee-mod/build/static_rules.ps1`; `validate.ps1` calls them and reports them
under their own numbers, and `.github/workflows/repo.yml`'s `lints` job runs
`klee-mod/build/validate_static.ps1` — the same functions, under `pwsh` on
ubuntu, in about 4 s. One implementation, two callers.

That happened because on 2026-09-02 a merged, CI-green pull request put the
base game's `[blue]` numeral colour on every power face and the round-six
deploy was refused by S5, which is a regex over committed C#. The wrapper was
what made it unreachable; it was never what made it correct.

Everything that needs the staged package (S1, S2, S3, S9, S12), the game
install (S3, S16) or the built pck (S6c's contract half) stays at deploy time.
`static_rules.ps1`'s header carries the table and the reason for each.

### The version stamp: what `+dirty` means

`+dirty` (and `+proto.dirty`) means **uncommitted changes to TRACKED files**,
and nothing else. It used to mean whatever `git status --porcelain` printed,
which includes untracked files — so on a machine that always has seat logs
under `understudy/logs/` and capture packets under `review/qa/`, every build
ever made from a clean `main` was stamped dirty and the mark distinguished
nothing. Untracked files are now a one-line count instead, printed as a note.
`Get-AutoVersion` in `klee-mod/build/version.ps1` is the rule;
`tier0/tests/test_manifest_version_gate.py` pins all four shapes against a
scratch repository whose state is known rather than observed.
