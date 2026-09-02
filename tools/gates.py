#!/usr/bin/env python3
"""Run the gates and print ONE LINE EACH. The raw output goes to a log file.

THE TOKEN THIS SAVES, which is the whole reason it exists. A pre-push check is
four commands and about four hundred lines of output -- `run_lints` prints a
35-row table, `pytest -q` prints a progress bar and a summary, each codegen
check prints its own paragraph, `dotnet` prints a build log. An agent reads all
of it into context to learn four booleans. Twelve agents in one sitting each
read it two or three times.

So: every gate runs exactly as it always did, its stdout and stderr are written
to a log file whose path is printed, and what comes back on the terminal is one
line per gate with the counts, plus the NAMES of failing tests and nothing else
about them. When a gate is red the log path is where the traceback is, and
reading it is a deliberate second step rather than the default.

    python tools/gates.py                    # --fast: lints + the fast lane
    python tools/gates.py --full             # the whole suite, bands included
    python tools/gates.py --full --dotnet --codegen     # everything
    python tools/gates.py --oneline          # a single verdict line
    python tools/gates.py --only pytest      # one gate by name

WHAT --fast IS AND IS NOT. `--fast` is the inner loop: `-m "not battery"`,
which drops the 82 calibration-band items. `operations/test.md` is explicit
that the fast lane is NEVER the gate before a push -- "a band that was not run
is not a band" -- so `--fast` says so in its own output rather than letting a
green line stand in for one it did not earn.

Exit 0 only if every gate that ran passed.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: pytest's own summary line, whichever combination of outcomes it carries.
PYTEST_COUNT = re.compile(r"(\d+) (passed|failed|skipped|xfailed|xpassed|"
                          r"error|errors|deselected|warnings?)")
PYTEST_FAIL = re.compile(r"^(?:FAILED|ERROR) ([^\s]+)", re.MULTILINE)
LINT_OK = re.compile(r"^OK: (\d+) lint\(s\) passed", re.MULTILINE)
LINT_FAILED = re.compile(r"^FAILED: (.*)$", re.MULTILINE)
#: `dotnet test`'s summary, both the .NET 6 and .NET 8 spellings.
DOTNET = re.compile(r"(?:Passed!|Failed!).*?"
                    r"Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+)",
                    re.DOTALL)
DOTNET_BUILD = re.compile(r"(\d+) Warning\(s\)\s+(\d+) Error\(s\)")


@dataclass
class Gate:
    name: str
    argv: list[str]
    #: Only run when the matching switch is given.
    optional: str = ""
    cwd: Path = REPO


@dataclass
class Result:
    gate: Gate
    code: int
    seconds: float
    summary: str
    failures: list[str] = field(default_factory=list)
    skipped: bool = False

    @property
    def ok(self) -> bool:
        return self.skipped or self.code == 0


def _python() -> str:
    """The repo venv's interpreter if there is one, else this one.

    Same rule the PowerShell gates follow: a check run under a different
    interpreter from the one the suite runs under is a check about a different
    tree.
    """
    for rel in (".venv/Scripts/python.exe", ".venv/bin/python"):
        candidate = REPO / rel
        if candidate.exists():
            return str(candidate)
    return sys.executable


def gates(args) -> list[Gate]:
    py = _python()
    lane = ["-m", "not battery"] if args.fast else []
    jobs = [] if args.serial else ["-n", "auto", "--dist", "loadscope"]
    suite = ["tier0/tests"] if args.fast else ["tier0/tests", "tier05/tests"]
    out = [
        Gate("lints", [py, "tools/run_lints.py", "--lane", "ci"]),
        Gate("pytest", [py, "-m", "pytest", *suite, "-q",
                        "-p", "no:cacheprovider", *lane, *jobs]),
        Gate("codegen-roster", [py, "tools/gen_roster_cards.py", "--check"],
             optional="codegen"),
        Gate("codegen-prototype",
             [py, "tools/gen_prototype_cards.py", "--check"],
             optional="codegen"),
        Gate("dotnet-build", ["dotnet", "build", "klee-mod/KleeCode",
                              "-v", "minimal", "--nologo"], optional="dotnet"),
        Gate("dotnet-test", ["dotnet", "test", "klee-mod/KleeTests",
                             "--nologo", "-v", "q"], optional="dotnet"),
    ]
    picked = []
    for gate in out:
        if gate.optional and not getattr(args, gate.optional):
            continue
        if args.only and gate.name not in args.only:
            continue
        picked.append(gate)
    return picked


def summarise(gate: Gate, text: str, code: int) -> tuple[str, list[str]]:
    """`(one-line summary, failing names)` for one gate's raw output."""
    if gate.name == "lints":
        ok = LINT_OK.search(text)
        if ok:
            return f"{ok.group(1)} passed", []
        bad = LINT_FAILED.search(text)
        names = [n.strip() for n in bad.group(1).split(",")] if bad else []
        return f"{len(names)} FAILED", names
    if gate.name == "pytest":
        counts = dict((kind, int(n)) for n, kind in PYTEST_COUNT.findall(text))
        parts = [f"{counts[k]} {k}" for k in
                 ("passed", "failed", "error", "errors", "skipped", "xfailed",
                  "deselected") if counts.get(k)]
        return ", ".join(parts) or "no items", PYTEST_FAIL.findall(text)
    if gate.name.startswith("codegen"):
        return ("in sync" if code == 0 else "STALE -- regenerate"), []
    if gate.name == "dotnet-test":
        m = DOTNET.search(text)
        if m:
            failed, passed, skipped = m.groups()
            names = re.findall(r"^\s*(?:Failed|X)\s+([\w.]+)", text,
                               re.MULTILINE)
            return (f"{passed} passed, {failed} failed, {skipped} skipped",
                    names)
        return ("ok" if code == 0 else "FAILED"), []
    if gate.name == "dotnet-build":
        m = DOTNET_BUILD.search(text)
        if m:
            return f"{m.group(2)} error(s), {m.group(1)} warning(s)", []
        return ("built" if code == 0 else "BUILD FAILED"), []
    return ("ok" if code == 0 else f"exit {code}"), []


def run(gate: Gate, log: Path) -> Result:
    if gate.argv[0] == "dotnet" and not shutil.which("dotnet"):
        return Result(gate, 0, 0.0, "skipped -- no dotnet on PATH",
                      skipped=True)
    env = dict(os.environ)
    # EB-93: a child whose stdout is a pipe on a cp1252 host dies on a shipped
    # card title. `run_lints` sets this for its own children for the same
    # reason; a wrapper that captures output has to set it too.
    env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
    start = time.perf_counter()
    res = subprocess.run(gate.argv, capture_output=True, text=True,
                         cwd=str(gate.cwd), env=env, errors="replace")
    seconds = time.perf_counter() - start
    text = (res.stdout or "") + (res.stderr or "")
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"\n{'=' * 70}\n$ {' '.join(gate.argv)}\n"
                 f"exit {res.returncode} in {seconds:.1f}s\n{'=' * 70}\n")
        fh.write(text)
    summary, failures = summarise(gate, text, res.returncode)
    return Result(gate, res.returncode, seconds, summary, failures)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    lane = ap.add_mutually_exclusive_group()
    lane.add_argument("--fast", action="store_true",
                      help="the inner loop: tier0 only, `-m not battery`. "
                           "NOT the pre-push gate (operations/test.md)")
    lane.add_argument("--full", action="store_true",
                      help="tier0 + tier05, bands included -- the push gate")
    ap.add_argument("--dotnet", action="store_true",
                    help="also `dotnet build` and `dotnet test`")
    ap.add_argument("--codegen", action="store_true",
                    help="also both codegen --check gates")
    ap.add_argument("--serial", action="store_true",
                    help="no xdist on pytest (the comparison arm)")
    ap.add_argument("--only", default="",
                    help="comma-separated gate names to run")
    ap.add_argument("--log-dir", default=str(REPO / ".gates"),
                    help="where the raw output goes (default .gates/)")
    ap.add_argument("--oneline", action="store_true",
                    help="one verdict line and the log path, nothing else")
    args = ap.parse_args(argv)
    if not args.full:
        args.fast = True
    args.only = {n.strip() for n in args.only.split(",") if n.strip()}

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / f"gates-{time.strftime('%Y%m%d-%H%M%S')}.log"
    log.write_text(f"gates {'--fast' if args.fast else '--full'} "
                   f"at {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                   encoding="utf-8")

    picked = gates(args)
    if not picked:
        print("gates: nothing selected")
        return 1

    results = [run(gate, log) for gate in picked]
    red = [r for r in results if not r.ok]

    try:
        rel = log.relative_to(Path.cwd()).as_posix()
    except ValueError:
        rel = str(log)

    if args.oneline:
        shape = ", ".join(f"{r.gate.name} {r.summary}" for r in results)
        print(f"gates {'FAST' if args.fast else 'FULL'}: "
              f"{'GREEN' if not red else 'RED (' + ', '.join(r.gate.name for r in red) + ')'}"
              f" -- {shape}; log {rel}")
        return 1 if red else 0

    width = max(len(r.gate.name) for r in results)
    for r in results:
        mark = "ok  " if r.ok else "FAIL"
        print(f"  [{mark}] {r.gate.name:<{width}}  {r.summary}  "
              f"({r.seconds:.1f}s)")
        for name in r.failures[:20]:
            print(f"         - {name}")
        if len(r.failures) > 20:
            print(f"         ... and {len(r.failures) - 20} more")
    print(f"\nlog: {rel}")
    if args.fast:
        print("lane: --fast (tier0, `-m not battery`). The bands did NOT run; "
              "operations/test.md requires --full before a push.")
    if red:
        print(f"RED: {', '.join(r.gate.name for r in red)}")
        return 1
    print(f"GREEN: {len(results)} gate(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
