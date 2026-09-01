Status: RECORD

# Making GitHub's checks fast — 2026-08-29

**The ask.** "Github takes about 5 minutes to run those checks even if the PR
is just altering markdown files. Is there a way to speed that up?" — and then:
"Yeah, let's do 1+2+3." This is what 1, 2 and 3 turned out to be.

Nothing here renames a job. `pytest`, `lints` and `patch-sentinel` keep their
exact names, because those names may be listed as required checks in branch
protection and a renamed job reports nothing at all — which would block every
pull request instead of speeding one up.

---

## 1. The test job now runs in parallel

The suite was running one test at a time. It now runs across every core the
runner has, using the identical command the local push gate has been running
for weeks (`-n auto --dist loadscope`). The `--dist loadscope` half matters:
it keeps a whole test file on one worker, so the expensive simulation fixtures
are computed once instead of once per worker.

Measured here, on this branch, on the 16-core dev box, at `917e07f`:

| arm | result | wall clock |
|---|---|---|
| serial (what CI ran until today) | 4451 passed, 46 skipped, 12 xfailed | **281.4 s** (4 m 41 s) |
| parallel `-n auto --dist loadscope` | 4451 passed, 46 skipped, 12 xfailed | **59.2 s** |

Identical counts, both green. **No test turned out to be unsafe in parallel**,
so nothing had to be isolated, quarantined or marked — which is what the
2026-08-24 measurement predicted and this run confirms. A GitHub runner has
2–4 cores rather than 16, so expect a smaller multiple there than 4.8×; the
real number is the one [USER] will see on the pull request.

`pytest-xdist` (the plugin that does this) is now installed in CI. The comment
in `tools/hooks/push_gate.py` saying it was "deliberately not in CI's install
line" was true until today and has been corrected to say what is true now.

## 2. A markdown-only pull request runs a markdown-sized check

A new tool, `tools/ci_changed_paths.py`, looks at the list of files a change
touches and answers one question: is every single one of them a `.md` file
living under `docs/current/`, `review/`, or the repo root?

- **Yes** → the `pytest` job skips the full suite and runs only the tests that
  actually read markdown (listed below), printing a loud one-line notice
  saying so. `patch-sentinel` skips its two steps. Both jobs still finish and
  still report success, so required checks are satisfied.
- **No** → everything runs exactly as before.

Anything that is not markdown in one of those three places makes it "no": a
card sheet (`docs/*.yaml`), a `review/qa` JSON or TXT, any `.py` or `.cs`, the
workflow file itself, `tools/`, `tier0/`, `klee-mod/`, `understudy/`,
`vendor/`, and markdown that lives elsewhere (`docs/kokomi-kickoff-v1.md`,
`understudy/README.md`) — all of those are read by the suite, so all of them
get the full run.

**It fails safe.** An empty list of changed files is "no", not "yes". The
empty case is what a broken measurement looks like — a shallow checkout, a
force-push, a first push whose "before" commit is all zeros — and the one
answer that must never come out of a broken measurement is "run less". The
tool ships with a `--self-test` covering 31 cases, including that one.

We deliberately did **not** use GitHub's own `paths-ignore` filter, which is
the obvious way to do this. A job filtered out that way does not report
"passed"; it reports nothing, and a required check that never reports blocks
the pull request forever. That is why the decision is made inside a job that
always runs.

### The tests that still run on a docs-only pull request

These nine were not guessed at. The full suite was run once with an audit hook
recording every markdown file any test actually opened, and these are the
modules that opened one the tool classifies as a doc — plus
`test_r_numbers_lint`, which enumerates the same page set without opening it.
Together, 322 tests in 17 s.

| module | what it reads |
|---|---|
| `tier0/tests/test_rulings_index.py` | every `.md` under `docs/current/` — checks each R-number cited anywhere resolves to a row in `RULINGS.md` |
| `tier0/tests/test_register_ids_lint.py` | `docs/current/QUEUE.md`, `BACKLOG.md` — row-id uniqueness |
| `tier0/tests/test_r_numbers_lint.py` | the `docs/current` page set the R-namespace lint scans |
| `tier0/tests/test_reaction_phase_parity.py` | `docs/current/BACKLOG.md` — a code comment citing a row that has since closed |
| `tier0/tests/test_staged_turn.py` | `docs/current/BACKLOG.md` |
| `tier0/tests/test_pulse_multiplier_claims.py` | `docs/current/playtest/kokomi-playtest-protocol.md` — the live-value claims |
| `tier0/tests/test_prototype_surface.py` | `review/active/*.md` |
| `tier0/tests/test_prototype_authorship.py` | `review/qa/*/packet.md` |
| `tier0/tests/test_understudy_seat.py` | `review/qa/kokomi-first-turn-example/packet.md` |

On top of that, **the whole `lints` job runs unconditionally** — it was never
touched by the fast path. That is where the register-shape, stamp-row,
EXPERIMENTS-registration, R-namespace, row-id and rulings-index gates live,
and those are most of what a markdown edit can actually break.

## 3. pip cache

The three jobs used to type their package list inline and download everything
from scratch on every run. They now install from `.github/requirements-ci.txt`
and `setup-python` caches pip against that file. One shared file means one
shared cache across all three jobs. The packages are unchanged apart from
`pytest-xdist`, and they stay loosely pinned, carrying forward the workflow's
own reasoning: a resolver surprise should look like a resolver surprise, not
like a repo failure.

---

## The blind spot, stated plainly

A docs-only pull request does not run the rest of pytest. That is the whole
point, and it is a real gap rather than a free lunch: if some future test
starts reading a file under `docs/current/` or `review/` and is not added to
the list in `repo.yml`, a markdown edit could break it and CI would stay
green until the next non-docs pull request.

Two things sit under it. First, the `lints` job still runs in full, and it
owns the register gates. Second, the local push gate
(`tools/hooks/push_gate.py`) has already run the entire fast lane and the CI
lint lane on the machine, before the push that opened the pull request — CI
is the second look here, not the first. The mitigation, when it is needed, is
one line: add the module to the docs-only list in the workflow, where a
comment already says to.

## Optional, not done

A `concurrency:` block would cancel a still-running check when a new commit
is pushed to the same branch, instead of letting both finish. It saves runner
minutes on branches that get several pushes in a row and costs nothing else.
It was left out because it was not asked for; say the word and it is three
lines.

## The one thing to check in repo settings

Open **Settings → Branches → branch protection for `main`** and look at
*Require status checks to pass before merging*:

1. **Which checks are listed as required?** If `pytest`, `lints` or
   `patch-sentinel` are named there, they are now confirmed to be
   load-bearing and must never be renamed — this change keeps all three names
   intact, but it is worth knowing which are actually required. In particular,
   `patch-sentinel` is *advisory by design* (it can never answer its real
   question on a runner) — if it is currently required, it probably should not
   be.
2. **Is auto-merge enabled?** If it is, a docs-only pull request should now
   go green and merge itself in well under a minute rather than five.

## Verification run before this was committed

- `.github/workflows/repo.yml` parses as YAML; the three job names are
  unchanged (`lints`, `patch-sentinel`, `pytest`), and both embedded shell
  blocks pass `bash -n`.
- `python tools/ci_changed_paths.py --self-test` → 31 cases, 0 failures.
- Full suite parallel: 4451 passed, 46 skipped, 12 xfailed in 59.20 s.
- Full suite serial: 4451 passed, 46 skipped, 12 xfailed in 281.44 s.
- The docs-only subset on its own: 322 passed in 17.05 s.
- `python -m tools.run_lints --lane ci` green.
- `python tools/hooks/push_gate.py --self-test` → 32 cases, 0 failures.
