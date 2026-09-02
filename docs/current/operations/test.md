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

One local dependency. **Added to CI's install line 2026-08-29** ([USER]
overturned the refusal recorded at the end of this section):

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
  Correction D a push that ran NOTHING is refused outright — since 2026-09-02
  by the git `pre-push` hook (`tools/hooks/pre_push_gate.py`, installed once
  per clone with `python tools/hooks/install.py`), which runs the fast lane and
  the `ci` lint lane in ~60 s — **a floor under this rule, not a substitute for
  it.** The hook cannot afford the bands; you can. It left `PreToolUse` because
  such a hook necessarily judged the tree as it stood BEFORE the command: an
  `edit && commit && push` one-liner was gated on the pre-edit tree, and often
  refused over the state of a file that same command was fixing.
- **bare `pytest` stays bare.** No `addopts`. Anyone who types the CI line
  gets the CI run.

**SUPERSEDED 2026-08-29 — [USER] made the trade.** This section used to end
"CI is deliberately untouched", on the grounds that a 2–4 vCPU runner only
buys the `-n 4` shape and that xdist would sit on the critical path of the
fresh-clone job. [USER] asked for the speed-up after watching a
markdown-only pull request take about five minutes, and CI's `pytest` job now
runs `-n auto --dist loadscope` over the full suite. Measured on the 16-CPU
dev box 2026-08-29 at `917e07f`: 4451 passed / 46 skipped / 12 xfailed either
way, **281.4 s serial → 59.2 s parallel**. No test needed isolating and no
`serial` marker was added, exactly as the 2026-08-24 measurement predicted.

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
