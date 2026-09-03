---
name: gates
description: Run the repo's gates and read a ten-line summary instead of four hundred lines of pytest, lint-table and dotnet output. Use before a push, after a build, or any time you were about to run run_lints and pytest by hand.
---

# Gates — one line per gate, the raw output in a log

Never paste `run_lints` + `pytest` + the codegen checks one at a time and read
their output. One command runs them, prints one line each with the counts and
the failing test NAMES, and writes everything else to a log file whose path it
prints.

```sh
python tools/gates.py                 # --fast: lints + tier0, `-m not battery`
python tools/gates.py --full          # tier0 + tier05, bands included
python tools/gates.py --full --codegen --dotnet    # everything
python tools/gates.py --only pytest   # one gate
python tools/gates.py --oneline       # a single verdict line
```

**`--fast` is the inner loop and is NEVER the pre-push gate.** It drops the 82
calibration-band items, and `operations/test.md` is explicit: a band that was
not run is not a band. Run `--full` before you push; the tool says so in its own
output so a green `--fast` line cannot stand in for one.

## Reading the result

- `[ok  ] pytest  4940 passed, 47 skipped, 12 xfailed  (59.0s)` — done, move on.
- A red gate lists the failing test names under it and nothing else. **Open the
  log only for the one you are fixing**: `sed -n '/<test name>/,+40p' <log>`.
- `dotnet-test` — the mod's C# suite, `klee-mod/KleeTests` with
  `-p:PrototypeCards=true` — runs in BOTH lanes and is **not** behind
  `--dotnet`. It is the one gate no GitHub runner can hold (it references four
  assemblies out of the Steam install), so its line always says `local-only`.
  `dotnet` gates are skipped with a note when `dotnet` is not on PATH or the
  machine has no `local.props`; a skip is reported as a skip, never as a pass.

Logs land in `.gates/` (gitignored). They are per-run, so an old one is the
record of an old tree — quote the path with the result if you report it.
