#!/usr/bin/env python3
"""Install this repo's git hooks. Today that is one: `pre-push`.

    python tools/hooks/install.py            # install (idempotent)
    python tools/hooks/install.py --check    # report, change nothing
    python tools/hooks/install.py --self-test

WHY AN INSTALLER AT ALL. Git hooks live in `.git/`, which is not tracked, so a
hook cannot simply be committed. It has to be written into place once per
clone -- and the thing written is deliberately a three-line SHIM that calls
`tools/hooks/pre_push_gate.py` out of the working tree, so the gate's rules
stay versioned with the repo and a hook installed months ago runs today's
checks.

ONE INSTALL COVERS EVERY WORKTREE. `git rev-parse --git-common-dir` is the
shared directory behind every linked worktree, and hooks live there rather
than in a worktree's own `.git` file. This project runs one worktree per
workstream, so an installer that only covered the checkout it was run from
would be an installer that covered almost nothing.

IT NEVER CLOBBERS A HOOK IT DID NOT WRITE. The shim carries a marker line; an
existing `pre-push` without that marker is reported and left alone. Somebody
else's hook is not ours to overwrite, and silently replacing it would be a
worse failure than not installing.

`core.hooksPath` IS HONOURED. If the repo or the machine has redirected hooks,
that directory is where the shim goes -- writing to `.git/hooks` while git
reads somewhere else would install a gate that never fires, which is the
failure mode this whole family exists to prevent.
"""
from __future__ import annotations

import stat
import subprocess
import sys
from pathlib import Path

MARKER = "installed by tools/hooks/install.py"

HOOK_NAME = "pre-push"

# `sh`, not python, because that is what git executes on every platform this
# repo is used on (Git for Windows ships its own sh and runs hooks through
# it). The shim resolves the gate out of the TREE BEING PUSHED --
# `--show-toplevel` under the hook's own environment is the worktree git is
# pushing from -- so a sibling worktree is gated by its own copy of the rules.
#
# THREE LAYERS, AND THE THIRD IS THE POINT. The hook is installed ONCE into the
# shared `.git`, so it fires for every worktree immediately -- including every
# worktree cut from a commit that predates `tools/hooks/pre_push_gate.py`. The
# first version of this shim printed "nothing gated" and exited 0 on those,
# which is a gate that installs itself everywhere and then waves through most
# of what it sees. Caught the same day it was written, on a real push from a
# worktree cut from main.
#
#   1. the pushing worktree's own copy         -- the rules it is pushing
#   2. the MAIN worktree's copy, which lives beside the shared .git that this
#      hook itself was installed into and is therefore as up to date as the
#      hook is
#   3. NEITHER: run the two checks inline, right here, over the pushing tree.
#      The same fast lane and the same `run_lints --lane ci`. An old tree is
#      still a tree full of tests, and "I could not find my own script" is not
#      a reason to let an untested push through.
#
# A tree that holds no `tools/run_lints.py` or no `tier0/tests` is BLOCKED by
# name, in every layer: a push from a tree the gate cannot test is exactly
# what must not slip through.
SHIM = f"""#!/bin/sh
# {MARKER} -- do not edit; edit tools/hooks/pre_push_gate.py instead.
#
# Runs the fast lane + `run_lints --lane ci` over the tree being pushed and
# refuses the push if either is red. Bypass (do not) with `git push --no-verify`.
top=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -n "$top" ] || exit 0

PY=python
command -v python >/dev/null 2>&1 || PY=python3

# (1) the tree being pushed.
gate="$top/tools/hooks/pre_push_gate.py"
if [ ! -f "$gate" ]; then
  # (2) the main worktree, which is the directory holding the shared .git this
  #     hook was installed into.
  common=$(git rev-parse --git-common-dir 2>/dev/null)
  case "$common" in
    /*|[A-Za-z]:*) ;;
    "") common="$top/.git" ;;
    *) common="$top/$common" ;;
  esac
  gate=$(dirname "$common")/tools/hooks/pre_push_gate.py
fi

cd "$top" || exit 1

# git EXPORTS these to its hooks, and the checks below shell out to git in
# temporary repositories of their own -- with GIT_DIR still pointing at the
# real one, those tests operate on THIS repo instead. Measured 2026-09-02, and
# it is not merely noisy: `tier0/tests/test_rulings_index.py` builds a fake
# history by committing, so the first run of this hook without the scrub wrote
# six fixture commits onto the pushing worktree's branch, re-inited the shared
# repo bare, and did the same to three sibling worktrees whose agents pushed in
# the same minutes. 26 tests failed and the damage was real. Scrub first.
# (pre_push_gate.py scrubs the same list in the child environment it builds;
# this is the shell half, for the inline arm below.)
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_QUARANTINE_PATH
unset GIT_REFLOG_ACTION GIT_INTERNAL_GETTEXT_TEST_FALLBACKS

if [ -f "$gate" ]; then
  exec "$PY" "$gate" "$@"
fi

# (3) No gate script anywhere: run the same two checks here rather than allow.
if [ ! -f tools/run_lints.py ] || [ ! -d tier0/tests ]; then
  echo "PUSH BLOCKED by the pre-push hook: $top holds no tools/run_lints.py and/or no tier0/tests, so this gate cannot test the tree being pushed. A push from a tree the gate cannot see is the case it exists for." >&2
  exit 1
fi
echo "pre-push: this worktree predates tools/hooks/pre_push_gate.py; running the same fast lane + run_lints --lane ci inline over $top." >&2
XARGS=""
if "$PY" -c "import xdist" >/dev/null 2>&1; then
  XARGS="-n auto --dist loadscope"
fi
PYTHONPATH="$top" "$PY" -m pytest tier0/tests tier05/tests -q -m "not battery" $XARGS || {{
  echo "PUSH BLOCKED by the pre-push hook: the fast lane is RED in $top. Nothing is pushed until it is green." >&2
  exit 1
}}
PYTHONPATH="$top" "$PY" tools/run_lints.py --lane ci || {{
  echo "PUSH BLOCKED by the pre-push hook: run_lints --lane ci is RED in $top." >&2
  exit 1
}}
echo "pre-push: GREEN -- fast lane + run_lints --lane ci over $top (inline fallback). NOT run: the battery items. Before a merge, run the full suite." >&2
exit 0
"""


def _git(*args: str, cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout.strip()


def hooks_dir(repo: Path) -> Path | None:
    """Where git will look for hooks for `repo`, or None if it is not a repo.

    `core.hooksPath` first (a redirect makes `.git/hooks` a decoy), then the
    COMMON git dir, which is the one every linked worktree shares.
    """
    code, configured = _git("config", "--get", "core.hooksPath", cwd=repo)
    if code == 0 and configured:
        path = Path(configured)
        return path if path.is_absolute() else (repo / path)

    code, common = _git("rev-parse", "--git-common-dir", cwd=repo)
    if code != 0 or not common:
        return None
    path = Path(common)
    if not path.is_absolute():
        path = repo / path
    return path / "hooks"


def status(repo: Path) -> tuple[str, Path | None]:
    """`(state, path)` where state is one of installed / missing / foreign /
    no-repo."""
    directory = hooks_dir(repo)
    if directory is None:
        return "no-repo", None
    hook = directory / HOOK_NAME
    if not hook.exists():
        return "missing", hook
    try:
        text = hook.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "foreign", hook
    return ("installed" if MARKER in text else "foreign"), hook


def install(repo: Path, quiet: bool = False) -> int:
    """Write the shim. Returns 0 on success (including already-installed)."""
    state, hook = status(repo)
    if state == "no-repo":
        print(f"install: {repo} is not a git checkout; nothing installed.",
              file=sys.stderr)
        return 1
    if state == "foreign":
        print(f"install: {hook} exists and was not written by this installer. "
              f"Leaving it alone -- move it aside and re-run, or call "
              f"tools/hooks/pre_push_gate.py from it yourself.",
              file=sys.stderr)
        return 1

    hook.parent.mkdir(parents=True, exist_ok=True)
    existing = ""
    if hook.exists():
        existing = hook.read_text(encoding="utf-8", errors="replace")
    if existing != SHIM:
        # newline="\n": git runs this through sh, and sh chokes on the CR of a
        # CRLF shebang line with "bad interpreter". On a repo whose .gitattributes
        # asks for LF everywhere this is belt and braces; it is also the one
        # place a stray CRLF would be silent until a push failed strangely.
        hook.write_text(SHIM, encoding="utf-8", newline="\n")
        mode = hook.stat().st_mode
        hook.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        if not quiet:
            print(f"install: wrote {hook}")
    elif not quiet:
        print(f"install: {hook} is already current")
    return 0


def self_test() -> int:
    import tempfile
    failures: list[str] = []
    cases = 0

    # A real, throwaway repository -- the installer's whole job is filesystem
    # placement, and a mock of the filesystem would prove placement into the
    # mock.
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "r"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True,
                       capture_output=True)

        cases += 1
        if status(repo)[0] != "missing":
            failures.append("self-test FAIL [fresh]: a fresh repo reported "
                            "something other than 'missing'")

        cases += 1
        if install(repo, quiet=True) != 0:
            failures.append("self-test FAIL [install]: install returned "
                            "non-zero on a fresh repo")

        cases += 1
        state, hook = status(repo)
        if state != "installed":
            failures.append(f"self-test FAIL [installed]: state is {state!r}")

        cases += 1
        if hook and MARKER not in hook.read_text(encoding="utf-8"):
            failures.append("self-test FAIL [marker]: the written hook does "
                            "not carry the marker it is recognised by")

        cases += 1
        if hook and b"\r" in hook.read_bytes():
            failures.append("self-test FAIL [crlf]: the shim was written with "
                            "CR bytes; sh reports 'bad interpreter'")

        cases += 1
        if install(repo, quiet=True) != 0:
            failures.append("self-test FAIL [idempotent]: a second install "
                            "failed")

        cases += 1
        hook.write_text("#!/bin/sh\necho mine\n", encoding="utf-8",
                        newline="\n")
        if status(repo)[0] != "foreign":
            failures.append("self-test FAIL [foreign]: a hand-written hook "
                            "was not recognised as foreign")

        cases += 1
        if install(repo, quiet=True) == 0:
            failures.append("self-test FAIL [no-clobber]: the installer "
                            "overwrote a hook it did not write")
        if "echo mine" not in hook.read_text(encoding="utf-8"):
            failures.append("self-test FAIL [no-clobber]: the foreign hook's "
                            "content is gone")

        # core.hooksPath is honoured: a redirect must move the install, not be
        # ignored while git reads elsewhere.
        cases += 1
        elsewhere = Path(tmp) / "hooks-elsewhere"
        subprocess.run(["git", "-C", str(repo), "config", "core.hooksPath",
                        str(elsewhere)], check=True, capture_output=True)
        if hooks_dir(repo) != elsewhere:
            failures.append("self-test FAIL [hooksPath]: core.hooksPath was "
                            "ignored, so the shim would go where git is not "
                            "looking")

        cases += 1
        if install(repo, quiet=True) != 0 or not (elsewhere / HOOK_NAME).exists():
            failures.append("self-test FAIL [hooksPath]: nothing was written "
                            "to the redirected hooks directory")

    cases += 1
    with tempfile.TemporaryDirectory() as tmp:
        if status(Path(tmp))[0] != "no-repo":
            failures.append("self-test FAIL [no-repo]: a directory that is no "
                            "checkout was not reported as such")

    # THE REGRESSION THAT CAUGHT US ON DAY ONE. The hook is installed into the
    # SHARED .git, so it fires for every worktree at once -- including the ones
    # cut from commits that predate pre_push_gate.py. The first shim printed
    # "nothing gated" and exited 0 on exactly those, which is a gate that
    # installs itself everywhere and then waves through most of what it sees.
    cases += 1
    if "nothing gated" in SHIM:
        failures.append("self-test FAIL [fallback]: the shim still has a path "
                        "that reports 'nothing gated' and allows the push")
    cases += 1
    if "run_lints.py --lane ci" not in SHIM:
        failures.append("self-test FAIL [fallback]: the shim has no inline "
                        "lint fallback, so a worktree without the gate script "
                        "is ungated")
    cases += 1
    if "PUSH BLOCKED" not in SHIM:
        failures.append("self-test FAIL [fallback]: the shim can no longer "
                        "refuse anything by itself")
    cases += 1
    if "--git-common-dir" not in SHIM:
        failures.append("self-test FAIL [fallback]: the shim no longer looks "
                        "for the main worktree's copy of the gate")
    # THE SCRUB. git exports GIT_DIR to its hooks; the checks make their own
    # temporary repositories, and with GIT_DIR still set they write to THIS
    # one -- six fixture commits onto a live branch and a bare re-init, on the
    # first run without it (2026-09-02). This is the highest-consequence line
    # in the shim.
    cases += 1
    if "unset GIT_DIR" not in SHIM:
        failures.append("self-test FAIL [env]: the shim does not scrub GIT_DIR, "
                        "so every test that makes its own repository will "
                        "write into this one")

    for line in failures:
        print(line)
    print(f"self-test: {cases} case(s), {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    repo = Path(__file__).resolve().parents[2]
    if "--self-test" in argv:
        return self_test()
    if "--check" in argv:
        state, hook = status(repo)
        print(f"{HOOK_NAME}: {state} ({hook})")
        return 0 if state == "installed" else 1
    return install(repo)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
