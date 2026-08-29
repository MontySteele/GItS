#!/usr/bin/env python3
"""PreToolUse/Bash|PowerShell: a `git push` runs the fast lane and the CI lints first, or it does not run.

Correction D. OPERATIONS.md's ratified discipline ([USER] 2026-08-24) reads
*"before any push -- the FULL suite and the full lint battery"*. That sentence
has been true and unenforced: nothing has ever stopped a push that was never
tested, and a push is the last moment the repo can refuse.

**WHICH TREE IT GATES (fixed 2026-08-26, review defect 1).** The first version
ran both gate commands in the directory the hook script lives in -- the
checkout whose `.claude/settings.json` fired. Every push in this project is
made from a SIBLING WORKTREE while the session's directory stays the main
checkout (`cd ../GItS-gov && git push -u origin gov-2026-08-26`, or
`git -C ../GItS-gov push`), so the gate tested a different branch, usually one
behind, and printed GREEN for a tree it had never looked at. That is worse
than no gate: it is a gate that lies. `_hooklib.push_target` now resolves the
directory the push itself targets -- `-C` first, then the last in-line `cd`
before the push, then the payload's own `cwd` field -- both commands run
there, and **the note names the directory that was gated** so the claim can be
checked rather than trusted. A target holding no `tools/run_lints.py` or no
`tier0/tests` is BLOCKED by name: a push from a tree this gate cannot test is
exactly what must not slip through.

**WHICH SHELLS IT COVERS (fixed 2026-08-26, review defect 2).** The matcher is
`Bash|PowerShell`. It was `Bash` alone, and this session also has a PowerShell
tool carrying its command line at the same `tool_input.command` -- so every
rule here had a second shell as its bypass. `Set-Location` / `sl` / `pushd`
are read as `cd`; `;` was already a separator, and PS 5.1 has no `&&` / `||`
to worry about.

WHAT IT ACTUALLY RUNS, AND WHY NOT THE FULL SUITE. The ratified rule names the
full suite; a PreToolUse hook has a wall-clock budget measured in tens of
seconds, because a gate that adds three minutes to every push is a gate
someone turns off. Measured 2026-08-26: fast lane `-n auto --dist loadscope`
18.5 s over 3546 items, `run_lints --lane ci` 2.3 s over 21 tools. So the gate
is the fast lane plus the CI lint lane, and it says so out loud rather than
letting the reader assume it was the full thing. The 82 deselected `battery`
items are the calibration bands -- **a band that was not run is not a band**.

  * `--dist loadscope` keeps a module on one worker, so a module-scoped
    battery fixture is computed once rather than once per worker.
  * Without `pytest-xdist` the same lane runs serially at ~55 s -- still
    inside budget, and the note says which arm ran. CI installs xdist too as
    of 2026-08-29 ([USER]) and its `pytest` job runs the SAME arm,
    `-n auto --dist loadscope`, over the full suite: this gate and the
    workflow now differ only in the `-m "not battery"` deselection below.
  * A timeout BLOCKS. A gate that waves the call through because it ran out of
    time reads green, which is the one thing it must never do wrongly.
  * Free: `--dry-run`, and anything `deny_dangerous_git.py` is about to refuse
    anyway -- no point spending 21 s on a call that dies at the other hook.

    python tools/hooks/push_gate.py               # hook mode (stdin)
    python tools/hooks/push_gate.py --self-test   # routing + resolution only
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _hooklib import (ALLOW, BLOCK, bash_command, bash_payload,  # noqa: E402
                      git_subcommand, note, payload_cwd, push_target,
                      read_payload, simple_commands)
from deny_dangerous_git import verdict as deny_verdict                 # noqa: E402

BUDGET_SECONDS = 300          # a hard stop, not the expected cost (~21 s)
FAST_LANE = ["-m", "pytest", "tier0/tests", "tier05/tests", "-q",
             "-m", "not battery"]
PARALLEL = ["-n", "auto", "--dist", "loadscope"]
LINTS = ["tools/run_lints.py", "--lane", "ci"]

# What a directory must hold before this gate can honestly claim to have
# tested it. Both, not either: `run_lints.py` alone would let a docs-only
# checkout look gateable.
REQUIRED = (Path("tools") / "run_lints.py", Path("tier0") / "tests")


def is_push(command: str, repo: Path | None = None) -> bool:
    """True when this command line pushes for real."""
    for tokens in simple_commands(command):
        sub, args = git_subcommand(tokens)
        if sub != "push":
            continue
        if "--dry-run" in args:
            continue
        if deny_verdict(tokens, repo):
            continue          # deny_dangerous_git.py owns this one
        return True
    return False


def ungateable(directory: Path) -> str:
    """Why `directory` cannot be gated, or `""` when it can."""
    if not directory.is_dir():
        return "the directory does not exist"
    missing = [str(part) for part in REQUIRED
               if not (directory / part).exists()]
    return ("it holds no " + " and no ".join(missing)) if missing else ""


def _have_xdist() -> bool:
    try:
        import xdist  # noqa: F401
    except ImportError:
        return False
    return True


def _child_env(cwd: Path) -> dict[str, str]:
    env = dict(os.environ)
    # EB-93: the child's stdout is a pipe here, and a tool that echoes a card
    # title carrying U+266A dies on a cp1252 host and takes the exit code.
    env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
    # The TARGET tree, not the hook's own: an inherited PYTHONPATH pointing at
    # the session's checkout would import that tree's modules while pytest
    # collected the worktree's tests.
    env["PYTHONPATH"] = str(cwd)
    return env


def _run(args: list[str], budget: float, cwd: Path) -> tuple[int, str, float]:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, *args], cwd=str(cwd), capture_output=True,
            text=True, encoding="utf-8", errors="backslashreplace",
            timeout=budget, env=_child_env(cwd))
    except subprocess.TimeoutExpired:
        return 124, f"TIMED OUT after {budget:.0f}s", time.perf_counter() - start
    except OSError as exc:
        return 127, f"{type(exc).__name__}: {exc}", time.perf_counter() - start
    return proc.returncode, proc.stdout + proc.stderr, time.perf_counter() - start


def _tail(text: str, lines: int = 15) -> str:
    kept = [line for line in text.splitlines() if line.strip()][-lines:]
    return "\n".join(kept)


def decide(payload: dict, execute: bool = True) -> int:
    command = bash_command(payload)
    target = push_target(command, payload_cwd(payload))
    if not is_push(command, target):
        return ALLOW
    if not execute:               # self-test: routing only, nothing is run
        return BLOCK

    problem = ungateable(target)
    if problem:
        note(f"PUSH BLOCKED by tools/hooks/push_gate.py: the push targets "
             f"{target} and {problem}, so this gate cannot test the tree "
             f"being pushed. A push from a tree the gate cannot see is the "
             f"case it exists for.")
        return BLOCK

    parallel = _have_xdist()
    lane = FAST_LANE + (PARALLEL if parallel else [])
    arm = "-n auto --dist loadscope" if parallel else "SERIAL (no pytest-xdist)"

    started = time.perf_counter()
    code, output, seconds = _run(lane, BUDGET_SECONDS, target)
    if code != 0:
        note(f"PUSH BLOCKED by tools/hooks/push_gate.py: the fast lane is RED "
             f"in {target} ({arm}, {seconds:.1f}s, exit {code}). Nothing is "
             f"pushed until it is green.\n{_tail(output)}")
        return BLOCK

    remaining = max(30.0, BUDGET_SECONDS - (time.perf_counter() - started))
    code, output, lint_seconds = _run(LINTS, remaining, target)
    if code != 0:
        note(f"PUSH BLOCKED by tools/hooks/push_gate.py: run_lints --lane ci "
             f"is RED in {target} ({lint_seconds:.1f}s, exit {code})."
             f"\n{_tail(output)}")
        return BLOCK

    note(f"push_gate: GREEN in {time.perf_counter() - started:.1f}s -- gated "
         f"{target} with the fast lane ({arm}) + run_lints --lane ci. NOT "
         f"run: the 82 `battery` items (the calibration bands) and the local "
         f"lint lane. Before a merge, run the full suite.")
    return ALLOW


# --- routing: does this command line get gated at all? ---------------------
CASES = [
    (bash_payload("git push origin gov-d-mechanisms"), 2, "a real push gates"),
    (bash_payload("git push"), 2, "a bare push gates"),
    (bash_payload("echo x && git push origin topic"), 2, "push behind a separator"),
    (bash_payload("cd ../GItS-gov && git push"), 2, "push after a cd gates"),
    # Defect 2: the second shell is not a bypass.
    (bash_payload("git push origin topic", tool="PowerShell"), 2,
     "a PowerShell push gates"),
    (bash_payload("Set-Location ../GItS-gov; git push origin topic",
                  tool="PowerShell"), 2, "a PowerShell cd + push gates"),
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

# --- resolution: WHICH tree would be gated ---------------------------------
# Asserted through the pure helper, so the self-test stays routing-only and
# runs no tests. The home is a POSIX drive path on purpose: it is the spelling
# Git Bash hands over, and the one the first version could not read.
HOME = "/r/GItS"
TARGET_CASES = [
    ("cd ../GItS-gov && git push", "R:/GItS-gov", "cd then push"),
    ("cd /c/Users/x/GItS-gov; git push origin b", "C:/Users/x/GItS-gov",
     "absolute POSIX drive path, `;` separator"),
    ("git -C ../GItS-gov push", "R:/GItS-gov", "git -C on the push itself"),
    ("cd ../a && cd ../b && git push", "R:/b", "the LAST cd wins"),
    ("git push && cd ../x", "R:/GItS", "a cd AFTER the push does not count"),
    ("git -C ../a -C b push", "R:/a/b", "repeated -C composes, as git does"),
    ("cd - && git push", "R:/GItS", "`cd -` is unknown; payload cwd stands"),
    ("cd && git push", "R:/GItS", "bare `cd` is unknown; payload cwd stands"),
    ('cd "../GItS gov" && git push', "R:/GItS gov", "a quoted path with a space"),
    ("Set-Location ../GItS-gov; git push", "R:/GItS-gov", "PowerShell Set-Location"),
    ("sl ../GItS-gov; git push", "R:/GItS-gov", "the `sl` alias"),
    ("pushd ../GItS-gov && git push", "R:/GItS-gov", "pushd"),
    ("git push origin b", "R:/GItS", "no cd at all: the payload cwd"),
]


# A bare `git push` is routed by the branch of the tree it would push FROM:
# on a topic branch it gates, on `main` the deny hook owns it and this gate
# steps aside. That answer must not depend on WHICH checkout the self-test
# happens to run in -- it did, and the case below read as a gate failure on
# every checkout sitting on `main` (the primary after a merge, CI's post-
# merge run). The branch is pinned per pass instead.
AT_MAIN_CASES = [
    (bash_payload("git push"), 0, "a bare push AT MAIN is the deny hook's"),
    (bash_payload("cd ../GItS-gov && git push"), 0,
     "a bare push after a cd, target on main, is the deny hook's"),
    (bash_payload("git push origin topic"), 2, "an explicit topic push gates even from main"),
]


def _routing_pass(cases, branch: str, failures: list[str]) -> None:
    import deny_dangerous_git as deny
    original = deny._current_branch
    deny._current_branch = lambda repo=None: branch
    try:
        for raw, expected, label in cases:
            got = decide(read_payload(raw), execute=False)
            if got != expected:
                failures.append(f"self-test FAIL [{label} @ {branch}]: expected "
                                f"exit {expected}, got {got} -- payload {raw}")
    finally:
        deny._current_branch = original


def self_test() -> int:
    failures: list[str] = []
    _routing_pass(CASES, "topic", failures)
    _routing_pass(AT_MAIN_CASES, "main", failures)

    for command, want, label in TARGET_CASES:
        got = push_target(command, HOME).as_posix()
        if got.lower() != want.lower():
            failures.append(f"self-test FAIL [{label}]: {command!r} resolved "
                            f"to {got!r}, expected {want!r}")

    # And the refusal that keeps an unresolvable target from slipping through.
    if not ungateable(Path(HOME) / "definitely-not-a-checkout"):
        failures.append("self-test FAIL [ungateable]: a directory holding no "
                        "run_lints.py and no tier0/tests was accepted as "
                        "gateable")
    if ungateable(Path(__file__).resolve().parents[2]):
        failures.append("self-test FAIL [ungateable]: this very checkout was "
                        "rejected as ungateable")

    for line in failures:
        print(line)
    print(f"self-test: {len(CASES) + len(AT_MAIN_CASES) + len(TARGET_CASES) + 2} case(s), "
          f"{len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    return decide(read_payload())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
