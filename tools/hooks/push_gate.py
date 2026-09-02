#!/usr/bin/env python3
"""PreToolUse/Bash|PowerShell: keep the real `pre-push` hook installed, and
refuse the one flag that would go round it.

WHAT THIS USED TO BE, AND WHY IT STOPPED (2026-09-02).

Until today this file WAS the gate: a `PreToolUse` hook that matched any shell
command containing `git push`, ran the fast lane and `run_lints --lane ci`, and
returned exit 2 on red. It caught real breakage. It also gated the wrong tree,
by construction and not by a bug: a `PreToolUse` hook fires BEFORE the command
runs, so the tree it tested was the tree as it stood BEFORE the command. The
ordinary shape of a turn here is

    <edit files> && git commit -am "..." && git push

and the gate read that as a push, tested the PRE-EDIT tree, and refused the
whole command over the state of a file the same command line was about to fix.
The only way through was to split the command by hand -- a tax paid to a gate
that was measuring the wrong thing.

Git already has the hook for this. `pre-push` runs at the moment git holds the
refs, with the working directory at the top of the worktree being pushed, so
the tree it checks IS the tree being pushed and a `commit && push` one-liner is
gated once and correctly. The checks did not change -- the same fast lane, the
same `run_lints --lane ci`, the same messages -- they moved to
`tools/hooks/pre_push_gate.py`. All of the command-line archaeology this file
used to do (`git -C`, an in-line `cd`, PowerShell's `Set-Location`, deciding
WHICH sibling worktree a push targets) is answered by git itself now, and is
gone with it.

SO WHAT IS LEFT HERE, and it is two things:

  1. INSTALL THE HOOK IF IT IS MISSING. A git hook lives in `.git/`, which is
     not tracked: a fresh clone has none. Rather than trust that somebody ran
     `python tools/hooks/install.py`, the first push of a session installs it.
     One install covers every sibling worktree, because linked worktrees share
     the common git dir the hook lives in.
  2. REFUSE `--no-verify`. That flag tells git to skip pre-push hooks. It is
     the one command line that can push past the gate without anything being
     wrong, and a gate with a documented bypass is a suggestion.

Everything else is ALLOWED here and gated by git a moment later, including
`--dry-run` (which pushes nothing) and the pushes `deny_dangerous_git.py`
owns.

    python tools/hooks/push_gate.py               # hook mode (stdin)
    python tools/hooks/push_gate.py --self-test   # routing only
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _hooklib import (ALLOW, bash_command, bash_payload, deny,  # noqa: E402
                      git_subcommand, note, payload_cwd, push_target,
                      read_payload, simple_commands)
import install as hook_installer                                   # noqa: E402

# Flags that make git skip the pre-push hook. On `git push` there is exactly
# ONE. Not `-n`: that is `--dry-run` here (it is `--no-verify`'s short form on
# `git commit`, which is where the confusion comes from), and refusing a dry
# run -- which pushes nothing and runs no hook because there is nothing to
# hook -- would be a gate blocking the safest command it can see.
SKIP_FLAGS = {"--no-verify"}


def push_flags(command: str) -> list[list[str]]:
    """The argument list of every real `git push` on this command line."""
    out: list[list[str]] = []
    for tokens in simple_commands(command):
        sub, args = git_subcommand(tokens)
        if sub == "push":
            out.append(args)
    return out


def decide(payload: dict, execute: bool = True) -> int:
    command = bash_command(payload)
    pushes = push_flags(command)
    if not pushes:
        return ALLOW

    for args in pushes:
        skipping = sorted(set(args) & SKIP_FLAGS)
        if skipping:
            return deny(
                f"PUSH BLOCKED by tools/hooks/push_gate.py: this command line "
                f"carries {', '.join(skipping)}, which tells git to skip the "
                f"pre-push hook -- the fast lane and run_lints --lane ci would "
                f"not run. Push without it. If the gate is wrong, fix the gate "
                f"(tools/hooks/pre_push_gate.py); a bypass that leaves no "
                f"trace is not a fix.")

    if not execute:
        return ALLOW

    target = push_target(command, payload_cwd(payload))
    state, hook = hook_installer.status(target)
    if state == "missing":
        if hook_installer.install(target, quiet=True) == 0:
            note(f"push_gate: installed the pre-push hook at {hook}. The fast "
                 f"lane + run_lints --lane ci run there, on the tree being "
                 f"pushed, from this push onward.")
        else:
            note(f"push_gate: could NOT install the pre-push hook at {hook}; "
                 f"this push is NOT gated. Run python tools/hooks/install.py "
                 f"and read what it says.")
    elif state == "foreign":
        note(f"push_gate: {hook} exists and was not written by "
             f"tools/hooks/install.py, so this push may not be gated. Look at "
             f"it before trusting a green push.")
    elif state == "no-repo":
        note(f"push_gate: {target} is not a git checkout, so there is no hook "
             f"to install and nothing to gate.")
    return ALLOW


# --- routing: which command lines does this shim have anything to say about?
CASES = [
    (bash_payload("git push origin topic"), 0, "a plain push is allowed here"),
    (bash_payload("git push"), 0, "a bare push is allowed here"),
    (bash_payload("echo x && git push origin topic"), 0,
     "a push behind a separator is allowed"),
    (bash_payload("cd ../GItS-gov && git push"), 0,
     "a push after a cd is allowed"),
    (bash_payload("git push --dry-run origin topic"), 0, "--dry-run is free"),
    (bash_payload("git status"), 0, "not a push"),
    (bash_payload("echo 'git push --no-verify'"), 0,
     "a quoted mention is not a push"),
    (bash_payload(""), 0, "empty command"),
    ("not json at all", 0, "unparseable payload"),
    # THE ONE REFUSAL. Both spellings, both shells: `--no-verify` is what
    # turns the pre-push hook off, and a gate with a bypass is a suggestion.
    (bash_payload("git push --no-verify origin topic"), 2,
     "--no-verify is refused"),
    (bash_payload("git push -n origin topic"), 0,
     "-n is --dry-run on push, not --no-verify: allowed"),
    (bash_payload("git push --no-verify origin topic", tool="PowerShell"), 2,
     "and from PowerShell, which is the other shell this session has"),
    (bash_payload("cd ../GItS-gov && git push --no-verify"), 2,
     "behind a cd as well"),
]


def self_test() -> int:
    failures: list[str] = []
    for raw, expected, label in CASES:
        got = decide(read_payload(raw), execute=False)
        if got != expected:
            failures.append(f"self-test FAIL [{label}]: expected exit "
                            f"{expected}, got {got} -- payload {raw}")

    # The gate this shim exists to keep alive must still be there, and must
    # still be the thing that runs the checks. A shim pointing at nothing is
    # the exact shape of a gate that stopped gating.
    gate = Path(__file__).resolve().parent / "pre_push_gate.py"
    if not gate.exists():
        failures.append("self-test FAIL [gate]: tools/hooks/pre_push_gate.py "
                        "is missing, so nothing runs the fast lane at all")
    elif "run_lints" not in gate.read_text(encoding="utf-8"):
        failures.append("self-test FAIL [gate]: pre_push_gate.py no longer "
                        "mentions run_lints; the lint half of the gate is gone")

    for line in failures:
        print(line)
    print(f"self-test: {len(CASES) + 1} case(s), {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    return decide(read_payload())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
