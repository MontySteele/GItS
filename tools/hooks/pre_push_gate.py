#!/usr/bin/env python3
"""git `pre-push`: the fast lane and the CI lints run, or the push does not.

WHY THIS IS A GIT HOOK AND NOT A PreToolUse HOOK ANY MORE (2026-09-02).

The gate used to be `tools/hooks/push_gate.py`, a `PreToolUse` hook matching
any shell command containing `git push`. A `PreToolUse` hook fires BEFORE the
command runs, so it necessarily tested the tree as it stood BEFORE the command
-- and the ordinary shape of a turn here is

    <edit files> && git commit -am "..." && git push

which the gate read as "a push", tested the PRE-EDIT tree, and then either
passed on code that was about to change or, more often, REFUSED the whole
command over the state of a file the same command line was about to fix. The
only way through was to split the command, which is a workflow tax paid to a
gate that was measuring the wrong tree.

A real `pre-push` hook runs at the moment git has the refs in hand: the tree
it sees IS the tree being pushed, the commit has already been made, and a
`commit && push` one-liner is gated exactly once, correctly. Git runs hooks
with the working directory at the top level of the worktree doing the push, so
the "which tree is this?" question that the PreToolUse version had to answer
by parsing `-C` and in-line `cd` out of a command line is answered by git
itself.

WHAT IT RUNS, AND WHY NOT THE FULL SUITE. `operations/test.md`'s ratified
discipline ([USER] 2026-08-24) reads *"before any push -- the FULL suite and
the full lint battery"*. A hook has a wall-clock budget, because a gate that
adds seven minutes to every push is a gate someone turns off. Measured
2026-09-02 on this box: the fast lane `-n auto --dist loadscope` 57.1 s over
5827 items; the same suite serially, whole-repo, 399.3 s. So the gate is the
fast lane plus the CI lint lane, and it SAYS SO out loud rather than letting
the reader assume it was the full thing. The 82 deselected `battery` items are
the calibration bands -- **a band that was not run is not a band**.

  * `--dist loadscope` keeps a module on one worker, so a module-scoped
    battery fixture is computed once rather than once per worker.
  * Without `pytest-xdist` the same lane runs serially at ~3 minutes -- and
    the note says which arm ran.
  * A timeout BLOCKS. A gate that waves the push through because it ran out
    of time reads green, which is the one thing it must never do wrongly.
  * A branch DELETION (`git push origin :topic`, `--delete`) pushes no
    commits, so there is nothing to test and it is allowed with a note.
  * A tree holding no `tools/run_lints.py` or no `tier0/tests` is BLOCKED by
    name: a push from a tree this gate cannot test is exactly what must not
    slip through.

INSTALLATION. `python tools/hooks/install.py` writes the `.git/hooks/pre-push`
shim (into the COMMON git dir, so every sibling worktree is covered by the one
install). `tools/hooks/push_gate.py` is now a PreToolUse shim that does the
same install if it is missing, so a session that has never run the installer
still ends up gated. `git push --no-verify` skips this hook, and that is
exactly why push_gate.py refuses a command line carrying it.

    python tools/hooks/pre_push_gate.py            # hook mode (refs on stdin)
    python tools/hooks/pre_push_gate.py --self-test
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _hooklib import note                                          # noqa: E402

ALLOW = 0
BLOCK = 1                     # git blocks the push on any non-zero exit

BUDGET_SECONDS = 600          # a hard stop, not the expected cost (~60 s)
FAST_LANE = ["-m", "pytest", "tier0/tests", "tier05/tests", "-q",
             "-m", "not battery"]
PARALLEL = ["-n", "auto", "--dist", "loadscope"]
LINTS = ["tools/run_lints.py", "--lane", "ci"]

# What a directory must hold before this gate can honestly claim to have
# tested it. Both, not either: `run_lints.py` alone would let a docs-only
# checkout look gateable.
REQUIRED = (Path("tools") / "run_lints.py", Path("tier0") / "tests")

ZERO = "0" * 40


def pushes_commits(stdin_text: str) -> bool:
    """True when this push carries at least one non-deleting ref update.

    git hands the hook one line per ref:
        <local ref> <local sha> <remote ref> <remote sha>
    and a DELETION spells the local half as `(delete)` with an all-zero sha.
    Nothing is being added to the remote, so there is no tree to test.

    An EMPTY stdin means git had nothing to say -- everything already up to
    date, or a git old enough not to feed the hook. That is allowed: this
    gate exists to stop untested CODE, and no code is moving.
    """
    saw_update = False
    for line in stdin_text.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        local_sha = parts[1]
        if local_sha.strip("0") == "":
            continue                      # a deletion
        saw_update = True
    return saw_update


def ungateable(directory: Path) -> str:
    """Why `directory` cannot be gated, or `""` when it can."""
    if not directory.is_dir():
        return "the directory does not exist"
    missing = [str(part) for part in REQUIRED
               if not (directory / part).exists()]
    return ("it holds no " + " and no ".join(missing)) if missing else ""


def _have_xdist(cwd: Path) -> bool:
    proc = subprocess.run([sys.executable, "-c", "import xdist"], cwd=str(cwd),
                          capture_output=True)
    return proc.returncode == 0


def _child_env(cwd: Path) -> dict[str, str]:
    env = dict(os.environ)
    # EB-93: the child's stdout is a pipe here, and a tool that echoes a card
    # title carrying U+266A dies on a cp1252 host and takes the exit code.
    env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
    # The TREE BEING PUSHED, not whatever the session's PYTHONPATH points at:
    # an inherited PYTHONPATH aimed at another checkout would import that
    # tree's modules while pytest collected this one's tests.
    env["PYTHONPATH"] = str(cwd)
    # git sets these for the hook, and they leak into `python -m pytest` as a
    # repo the child would then treat as ITS repo. Nothing here shells out to
    # git, but tools/ does (lint_vendor_pin, the register lints), and a
    # GIT_DIR pointing at the common dir of a DIFFERENT worktree is exactly
    # the "gated the wrong tree" defect in a new coat.
    for leaked in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                   "GIT_PREFIX", "GIT_QUARANTINE_PATH"):
        env.pop(leaked, None)
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


def decide(stdin_text: str, target: Path, execute: bool = True) -> int:
    """The whole hook, as a function, so the self-test can route without
    running 60 s of tests."""
    if not pushes_commits(stdin_text):
        note("pre_push_gate: nothing but ref deletions (or nothing at all) in "
             "this push -- no tree to test, allowed.")
        return ALLOW

    problem = ungateable(target)
    if problem:
        note(f"PUSH BLOCKED by tools/hooks/pre_push_gate.py: the push targets "
             f"{target} and {problem}, so this gate cannot test the tree "
             f"being pushed. A push from a tree the gate cannot see is the "
             f"case it exists for.")
        return BLOCK

    if not execute:               # self-test: routing only, nothing is run
        return ALLOW

    parallel = _have_xdist(target)
    lane = FAST_LANE + (PARALLEL if parallel else [])
    arm = "-n auto --dist loadscope" if parallel else "SERIAL (no pytest-xdist)"

    started = time.perf_counter()
    code, output, seconds = _run(lane, BUDGET_SECONDS, target)
    if code != 0:
        note(f"PUSH BLOCKED by tools/hooks/pre_push_gate.py: the fast lane is "
             f"RED in {target} ({arm}, {seconds:.1f}s, exit {code}). Nothing "
             f"is pushed until it is green.\n{_tail(output)}")
        return BLOCK

    remaining = max(30.0, BUDGET_SECONDS - (time.perf_counter() - started))
    code, output, lint_seconds = _run(LINTS, remaining, target)
    if code != 0:
        note(f"PUSH BLOCKED by tools/hooks/pre_push_gate.py: run_lints --lane "
             f"ci is RED in {target} ({lint_seconds:.1f}s, exit {code})."
             f"\n{_tail(output)}")
        return BLOCK

    note(f"pre_push_gate: GREEN in {time.perf_counter() - started:.1f}s -- "
         f"gated {target} with the fast lane ({arm}) + run_lints --lane ci. "
         f"NOT run: the 82 `battery` items (the calibration bands) and the "
         f"local lint lane. Before a merge, run the full suite.")
    return ALLOW


# --- routing: which pushes get gated at all? -------------------------------
#
# The refs, as git spells them on stdin. A deletion's LOCAL sha is all zeros;
# that is the whole test, and it is here rather than in prose because the one
# thing a gate must never do is refuse the ordinary case.
UPDATE = "refs/heads/topic 1111111111111111111111111111111111111111 " \
         "refs/heads/topic 2222222222222222222222222222222222222222\n"
DELETE = f"(delete) {ZERO} refs/heads/topic " \
         "2222222222222222222222222222222222222222\n"

CASES = [
    (UPDATE, True, "a real ref update is gated"),
    (UPDATE + DELETE, True, "an update alongside a deletion is gated"),
    (DELETE, False, "a pure deletion pushes no code"),
    ("", False, "empty stdin: git had nothing to say"),
    ("garbage\n", False, "an unparseable line is not a ref update"),
]


def self_test() -> int:
    import tempfile
    failures: list[str] = []
    repo = Path(__file__).resolve().parents[2]

    for stdin_text, expect_gated, label in CASES:
        if pushes_commits(stdin_text) != expect_gated:
            failures.append(f"self-test FAIL [{label}]: pushes_commits said "
                            f"{not expect_gated}")

    # Routing through `decide`, with execute=False so no tests run: a gateable
    # tree ALLOWS at the routing stage, an ungateable one BLOCKS.
    if decide(UPDATE, repo, execute=False) != ALLOW:
        failures.append("self-test FAIL [gateable]: this very checkout was "
                        "rejected as ungateable")
    with tempfile.TemporaryDirectory() as tmp:
        if decide(UPDATE, Path(tmp), execute=False) != BLOCK:
            failures.append("self-test FAIL [ungateable]: a directory holding "
                            "no run_lints.py and no tier0/tests was accepted "
                            "as gateable")
        if decide(UPDATE, Path(tmp) / "nope", execute=False) != BLOCK:
            failures.append("self-test FAIL [missing]: a directory that does "
                            "not exist was accepted as gateable")

    # And the environment scrub, which is what keeps a hook fired from one
    # worktree from linting another one's git state.
    os.environ["GIT_DIR"] = "/somewhere/else/.git"
    try:
        if "GIT_DIR" in _child_env(repo):
            failures.append("self-test FAIL [env]: GIT_DIR survived into the "
                            "child environment")
    finally:
        os.environ.pop("GIT_DIR", None)

    for line in failures:
        print(line)
    print(f"self-test: {len(CASES) + 4} case(s), {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    try:
        stdin_text = sys.stdin.read()
    except (OSError, ValueError):
        stdin_text = ""
    return decide(stdin_text, Path(os.getcwd()).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
