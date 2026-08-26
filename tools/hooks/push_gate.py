#!/usr/bin/env python3
"""PreToolUse/Bash: a `git push` runs the fast lane and the CI lints first, or it does not run.

Correction D. OPERATIONS.md's ratified discipline ([USER] 2026-08-24) reads
*"before any push -- the FULL suite and the full lint battery"*. That sentence
has been true and unenforced: nothing has ever stopped a push that was never
tested, and a push is the last moment the repo can refuse.

WHAT THIS GATE ACTUALLY RUNS, AND WHY NOT THE FULL SUITE. The ratified rule
names the full suite; a PreToolUse hook has a wall-clock budget measured in
tens of seconds, because a gate that adds three minutes to every push is a
gate someone turns off. Measured in this worktree on 2026-08-26:

    fast lane, -n auto --dist loadscope     18.5 s   3546 passed
    run_lints.py --lane ci (16 tools)        2.3 s   all green
                                            ------
                                            ~21 s

So the gate is the FAST LANE plus the CI lint lane, and it says so out loud on
every run rather than letting the reader assume it was the full thing. The 82
deselected `battery` items are the calibration bands -- **a band that was not
run is not a band** -- so this hook is a floor under the discipline, never a
replacement for it. The green line it prints names what it skipped.

  * `--dist loadscope` is load-bearing, not taste: it keeps a module on one
    worker so a module-scoped battery fixture is computed once.
  * Without `pytest-xdist` (optional, local, deliberately not in CI's install
    line) the same lane runs serially at ~55 s -- still inside budget, and the
    stderr line says which arm ran.
  * A timeout BLOCKS. A gate that waves the call through because it ran out of
    time is worse than no gate, because it reads green.
  * Pushes this hook must not delay: `--dry-run`, and anything the sibling
    `deny_dangerous_git.py` is about to refuse anyway (no point spending 21 s
    on a call that dies at the other hook).

    python tools/hooks/push_gate.py               # hook mode (stdin)
    python tools/hooks/push_gate.py --self-test   # routing only, runs no tests
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _hooklib import (ALLOW, BLOCK, REPO, bash_command, bash_payload,  # noqa: E402
                      git_subcommand, note, read_payload, run_self_test,
                      simple_commands)
from deny_dangerous_git import verdict as deny_verdict                 # noqa: E402

BUDGET_SECONDS = 300          # a hard stop, not the expected cost (~21 s)
FAST_LANE = ["-m", "pytest", "tier0/tests", "tier05/tests", "-q",
             "-m", "not battery"]
PARALLEL = ["-n", "auto", "--dist", "loadscope"]
LINTS = ["tools/run_lints.py", "--lane", "ci"]


def is_push(command: str) -> bool:
    """True when this command line pushes for real."""
    for tokens in simple_commands(command):
        sub, args = git_subcommand(tokens)
        if sub != "push":
            continue
        if "--dry-run" in args:
            continue
        if deny_verdict(tokens):
            continue          # deny_dangerous_git.py owns this one
        return True
    return False


def _have_xdist() -> bool:
    try:
        import xdist  # noqa: F401
    except ImportError:
        return False
    return True


def _run(args: list[str], budget: float) -> tuple[int, str, float]:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, *args], cwd=REPO, capture_output=True, text=True,
            encoding="utf-8", errors="backslashreplace", timeout=budget,
            # EB-93: the child's stdout is a pipe here, and a tool that echoes
            # a card title carrying U+266A dies on a cp1252 host and takes the
            # exit code with it.
            env=_child_env())
    except subprocess.TimeoutExpired:
        return 124, f"TIMED OUT after {budget:.0f}s", time.perf_counter() - start
    except OSError as exc:
        return 127, f"{type(exc).__name__}: {exc}", time.perf_counter() - start
    return proc.returncode, proc.stdout + proc.stderr, time.perf_counter() - start


def _child_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
    env.setdefault("PYTHONPATH", str(REPO))
    return env


def _tail(text: str, lines: int = 15) -> str:
    kept = [line for line in text.splitlines() if line.strip()][-lines:]
    return "\n".join(kept)


def decide(payload: dict, execute: bool = True) -> int:
    if not is_push(bash_command(payload)):
        return ALLOW
    if not execute:               # self-test: routing only
        return BLOCK

    parallel = _have_xdist()
    lane = FAST_LANE + (PARALLEL if parallel else [])
    arm = "-n auto --dist loadscope" if parallel else "SERIAL (no pytest-xdist)"

    started = time.perf_counter()
    code, output, seconds = _run(lane, BUDGET_SECONDS)
    if code != 0:
        note(f"PUSH BLOCKED by tools/hooks/push_gate.py: the fast lane is RED "
             f"({arm}, {seconds:.1f}s, exit {code}). Nothing is pushed until "
             f"it is green.\n{_tail(output)}")
        return BLOCK

    remaining = max(30.0, BUDGET_SECONDS - (time.perf_counter() - started))
    code, output, lint_seconds = _run(LINTS, remaining)
    if code != 0:
        note(f"PUSH BLOCKED by tools/hooks/push_gate.py: run_lints --lane ci "
             f"is RED ({lint_seconds:.1f}s, exit {code}).\n{_tail(output)}")
        return BLOCK

    note(f"push_gate: GREEN in {time.perf_counter() - started:.1f}s -- fast "
         f"lane ({arm}) + run_lints --lane ci. NOT run: the 82 `battery` "
         f"items (the calibration bands) and the local lint lane. Before a "
         f"merge, run the full suite.")
    return ALLOW


CASES = [
    (bash_payload("git push origin gov-d-mechanisms"), 2, "a real push gates"),
    (bash_payload("git push"), 2, "a bare push gates"),
    (bash_payload("echo x && git push origin topic"), 2, "push behind a separator"),
    (bash_payload("git push --dry-run origin topic"), 0, "--dry-run is free"),
    (bash_payload("git push origin main"), 0, "deny hook owns main"),
    (bash_payload("git push --force origin topic"), 0, "deny hook owns force"),
    (bash_payload("git status"), 0, "not a push"),
    (bash_payload("git fetch --depth=1 origin tag pre-simplification-2026-08-06"), 0,
     "fetch is not a push"),
    (bash_payload("echo 'git push origin main'"), 0, "a quoted mention is not a push"),
    (bash_payload(""), 0, "empty command"),
    ("not json at all", 0, "unparseable payload"),
]


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test(CASES, lambda p: decide(p, execute=False))
    return decide(read_payload())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
