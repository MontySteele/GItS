#!/usr/bin/env python3
"""EB-154: sweep a headless MegaDot log for the failures its exit code hides.

WHAT WAS WRONG. `tools/build_pck.ps1` checked the two halves of the pack build
differently and both checks were wrong in a different direction:

  * the IMPORT log was swept with `Select-String 'ERROR'`, which is
    case-INSENSITIVE and UNANCHORED in PowerShell. It matches a path
    containing `error`, a warning that quotes the word, and the string
    "0 errors" -- and it does NOT match the three failures Godot actually
    reports for a dropped asset, none of which carries an `ERROR:` prefix:
    `Unrecognized dependency:`, `Failed loading resource`, `Cannot open file`.
  * the EXPORT was checked by EXIT CODE ONLY. Godot's headless exporter
    reports a missing referenced texture and exits 0, so a referenced texture
    could vanish from the pack with the build green. The pck contract is
    derived from the work directory (`build_pck.ps1`, C4), so a resource that
    never imported is simply absent from the contract as well -- consistent,
    and consistently silent.

WHY PYTHON AND NOT MORE POWERSHELL. The repo's own rule is that PS 5.1
semantics cannot be executed from pytest (`test_repo_python_convention.py`),
so a sweep written in PowerShell can only ever be pinned as SOURCE TEXT -- and
what has to be right here is the MATCHING, not the shape of the call site. As
a module it is driven by fixture logs on every platform, including the CI
runner that has neither Godot nor the game. `build_pck.ps1` calls it through
`Invoke-RepoPython`, the same convention every other native call in that file
uses.

THE PATTERN SET IS ANCHORED AND CASE-SENSITIVE, and both halves matter. Godot
writes its diagnostics at the start of a line with a fixed prefix; a substring
match anywhere on any line is how the old sweep both over- and under-matched.

Usage:
    python tools/godot_log_sweep.py <logfile> --stage import|export

Exit 1 with the offending lines on stdout; exit 0 and one summary line if the
log is clean.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Each entry: (name, compiled pattern, what it means).
#
# The three UNPREFIXED ones are the point of the row -- they are what a
# dropped dependency looks like, and the old `'ERROR'` sweep saw none of them.
# The prefixed ones are anchored rather than dropped: `ERROR:` at the head of a
# line is a real Godot error, `ERROR` in the middle of one is usually a path.
PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("godot-error", re.compile(r"^\s*ERROR:"),
     "a Godot error"),
    ("godot-script-error", re.compile(r"^\s*SCRIPT ERROR:"),
     "a Godot script error"),
    ("godot-user-error", re.compile(r"^\s*USER ERROR:"),
     "a Godot user error"),
    ("godot-fatal", re.compile(r"^\s*(FATAL|USER FATAL):"),
     "a fatal Godot condition"),
    ("dropped-dependency", re.compile(r"Unrecognized dependency:"),
     "a resource references something that is not in the pack"),
    ("load-failure", re.compile(r"Failed (?:loading|to load) resource"),
     "a resource did not load"),
    ("open-failure", re.compile(r"Cannot open file"),
     "a file the build asked for is not there"),
    ("import-failure", re.compile(r"Error importing"),
     "an asset failed to import"),
    ("no-loader", re.compile(r"No loader found for resource"),
     "an imported resource has no loader"),
)

STAGES = ("import", "export")


def findings(text: str) -> list[str]:
    """Every offending line, prefixed with the rule that caught it."""
    out: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for name, pattern, meaning in PATTERNS:
            if pattern.search(line):
                out.append(f"  line {lineno} [{name}: {meaning}] {line.strip()}")
                break
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", type=Path)
    ap.add_argument("--stage", choices=STAGES, required=True)
    args = ap.parse_args(argv)

    if not args.log.exists():
        print(f"godot log sweep: no {args.stage} log at {args.log}. The build "
              f"produced no diagnostics to read, which is not the same as "
              f"producing none -- treat it as a failure.")
        return 1

    text = args.log.read_text(encoding="utf-8", errors="replace")
    problems = findings(text)
    if problems:
        print(f"MegaDot {args.stage} log: {len(problems)} failure line(s) "
              f"in {args.log}")
        for line in problems:
            print(line)
        return 1
    print(f"godot log sweep: {args.stage} clean "
          f"({len(text.splitlines())} line(s), {len(PATTERNS)} pattern(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
