#!/usr/bin/env python3
"""PreToolUse/Bash|PowerShell: refuse the four git invocations OPERATIONS.md forbids in prose.

Correction D. Each rule below was, until this file existed, a sentence in a
document -- and a sentence is context, not configuration. These four were
chosen because each one has already cost this repo something:

  1. **`git add -A` / `git add .` / `git add --all`.** operations/worktrees.md
     section: *"Stage explicitly; never `git add -A`. Read the `--stat` before
     you push -- one unexpected filename is the whole signal."* A blanket add
     in a tree that carries gitignored art, decompile output and local props
     is how an unreviewed file reaches a branch.
  2. **`git worktree remove`.** It deletes GITIGNORED CONTENT out of a CLEAN
     worktree. On 2026-08-24 a routine purge took both surviving `game_ref/`
     backups this way and turned one deletion into a fourth total loss of a
     tree that cannot be committed and cannot be regenerated (`EB-128`).
     `python -m tools.purge_worktree` asks the question git does not.
  3. **`git push` at `main`, or any forced push.** `main` is push-protected by
     ratified workflow -- a branch goes up, and the PR merge is [USER]'s -- and
     a force-push is the one git operation that destroys published history.
     `--force-with-lease` is refused with the rest: a lease makes a force
     safer, never non-destructive, and the rule here is about WHO merges to
     `main`, not about racing.
  4. **`--no-verify`.** On `commit` or on `push` it is the switch that turns
     off the hook layer this correction is building. A gate with a documented
     bypass is a suggestion.

TWO REVIEW DEFECTS, FIXED 2026-08-26. **The matcher was `Bash` alone**, and
this session also has a PowerShell tool that carries its command line at the
same `tool_input.command` -- so every rule below had a second shell as its
bypass. It is now `Bash|PowerShell`, and `Set-Location` / `sl` / `pushd` read
as `cd`. **And the bare-push branch check ran in the wrong tree**: it asked
the hook script's own checkout what branch was out, while the push itself is
routinely made from a sibling worktree (`cd ../GItS-gov && git push`). It now
asks the tree the push actually targets, resolved by `_hooklib.push_target`.

Everything else is allowed and must stay allowed: `git add docs/current`,
`git push origin my-branch`, `git worktree add`, `git worktree prune`,
`git commit -m`. The self-test carries those as cases precisely so a later
tightening cannot quietly start blocking the normal workflow.

    python tools/hooks/deny_dangerous_git.py               # hook mode (stdin)
    python tools/hooks/deny_dangerous_git.py --self-test   # prove it bites
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _hooklib import (ALLOW, REPO, bash_command, bash_payload, deny,  # noqa: E402
                      git_subcommand, payload_cwd, push_target, read_payload,
                      run_self_test, simple_commands)

ADD_EVERYTHING = {"-A", "--all", "--no-ignore-removal", ".", "./", ":/", ":"}
FORCE_FLAGS = {"-f", "--force", "--force-with-lease", "--force-if-includes"}
NO_VERIFY = {"-n", "--no-verify"}
PROTECTED = {"main", "master"}


def _refspec_targets_protected(args: list[str]) -> str:
    """The protected branch a push refspec would write to, or `""`.

    A refspec's DESTINATION is the half after the colon (`HEAD:main`), the
    whole token when there is no colon (`main`), and neither when the token is
    an option or a remote. Reading only the last token would miss
    `git push -u origin main --tags`; reading any token would fire on a remote
    that happened to be named `main`.
    """
    skip_next = False
    for index, token in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if token.startswith("-"):
            if token in ("-o", "--push-option", "--repo", "--receive-pack",
                         "--exec"):
                skip_next = True
            continue
        if index == 0:
            continue                     # the remote (`origin`, a URL, a path)
        spec = token.lstrip("+")
        destination = spec.split(":", 1)[1] if ":" in spec else spec
        if destination.rsplit("/", 1)[-1] in PROTECTED:
            return destination
    return ""


def _current_branch(repo: Path | None = None) -> str:
    """The checked-out branch, for a BARE `git push` with no refspec.

    `repo` is the tree the push actually targets, which is not this script's
    own checkout whenever the push is made from a sibling worktree -- asking
    the wrong tree returns the wrong branch and the rule silently stops
    applying. Failures are silent and read as "not main": a hook that cannot
    answer the question must not answer it with a refusal.
    """
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(repo or REPO), capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def verdict(tokens: list[str], repo: Path | None = None) -> str:
    """The refusal one simple command earns, or `""` if it is fine.

    `repo` is the tree a bare `git push` would push FROM; everything else here
    is answered from the command line alone.
    """
    sub, args = git_subcommand(tokens)
    if not sub:
        return ""

    if sub == "add":
        hit = sorted({a for a in args if a in ADD_EVERYTHING})
        if hit:
            return (f"DENIED by tools/hooks/deny_dangerous_git.py: "
                    f"`git add {' '.join(hit)}` stages everything. "
                    f"operations/worktrees.md: stage explicitly and read the --stat "
                    f"before you push -- one unexpected filename is the whole "
                    f"signal. Name the paths.")

    if sub == "worktree" and args and args[0] == "remove":
        target = next((a for a in args[1:] if not a.startswith("-")), "<path>")
        return (f"DENIED by tools/hooks/deny_dangerous_git.py: "
                f"`git worktree remove` deletes GITIGNORED content out of a "
                f"CLEAN worktree -- this is how both surviving game_ref/ "
                f"backups were lost on 2026-08-24 (EB-128). Use: "
                f"python -m tools.purge_worktree {target}")

    if sub == "push":
        forced = sorted({a for a in args if a in FORCE_FLAGS})
        if forced:
            return (f"DENIED by tools/hooks/deny_dangerous_git.py: "
                    f"`git push {' '.join(forced)}` rewrites published "
                    f"history. If a branch really must be replaced, that is "
                    f"[USER]'s call, not this session's.")
        if "--no-verify" in args:
            return ("DENIED by tools/hooks/deny_dangerous_git.py: "
                    "`git push --no-verify` disables the pre-push hook layer. "
                    "Fix what is red instead of muting it.")
        branch = _refspec_targets_protected(args)
        if not branch and not any(not a.startswith("-") for a in args[1:]):
            live = _current_branch(repo)
            branch = live if live in PROTECTED else ""
        if branch:
            return (f"DENIED by tools/hooks/deny_dangerous_git.py: this push "
                    f"targets `{branch}`. Branches go up; the PR merge to "
                    f"main is [USER]'s. Push the workstream branch instead.")

    if sub == "commit" and any(a in NO_VERIFY for a in args):
        return ("DENIED by tools/hooks/deny_dangerous_git.py: "
                "`git commit --no-verify` skips the hooks. A gate with a "
                "bypass is a suggestion -- fix the failure, or say why in "
                "the commit message and ask [USER].")

    return ""


def decide(payload: dict) -> int:
    command = bash_command(payload)
    repo = push_target(command, payload_cwd(payload))
    for tokens in simple_commands(command):
        reason = verdict(tokens, repo)
        if reason:
            return deny(reason)
    return ALLOW


CASES = [
    # --- refusals, one per rule ------------------------------------------
    (bash_payload("git add -A"), 2, "add -A"),
    (bash_payload("git add ."), 2, "add ."),
    (bash_payload("git add --all"), 2, "add --all"),
    (bash_payload("echo hi && git add -A"), 2, "add -A behind a separator"),
    (bash_payload("git -C ../GItS-foo add -A"), 2, "add -A with -C"),
    (bash_payload("git worktree remove ../GItS-foo"), 2, "worktree remove"),
    (bash_payload("git worktree remove --force ../GItS-foo"), 2, "forced remove"),
    (bash_payload("git push origin main"), 2, "push to main"),
    (bash_payload("git push origin HEAD:main"), 2, "push HEAD:main"),
    (bash_payload("git push -u origin main --tags"), 2, "push -u origin main"),
    (bash_payload("git push origin +refs/heads/main"), 2, "forced refspec to main"),
    (bash_payload("git push --force origin topic"), 2, "force push"),
    (bash_payload("git push -f origin topic"), 2, "-f push"),
    (bash_payload("git push --force-with-lease origin topic"), 2, "leased force"),
    (bash_payload("git push --no-verify origin topic"), 2, "push --no-verify"),
    (bash_payload("git commit --no-verify -m 'x'"), 2, "commit --no-verify"),
    (bash_payload("git commit -n -m 'x'"), 2, "commit -n"),
    # --- the second shell is not a bypass (review defect 2) ---------------
    (bash_payload("git add -A", tool="PowerShell"), 2, "PowerShell add -A"),
    (bash_payload("git push --force origin topic", tool="PowerShell"), 2,
     "PowerShell force push"),
    (bash_payload("Set-Location ../GItS-gov; git push origin main",
                  tool="PowerShell"), 2, "PowerShell Set-Location then main"),
    (bash_payload("git worktree remove ../GItS-foo", tool="PowerShell"), 2,
     "PowerShell worktree remove"),
    (bash_payload("Set-Location ../GItS-gov; git push origin topic",
                  tool="PowerShell"), 0, "PowerShell branch push is allowed"),
    # --- and the workflow that must NOT be blocked ------------------------
    (bash_payload("git add docs/current/OPERATIONS.md tools/hooks"), 0, "explicit add"),
    (bash_payload("git add -p tier0/constants.py"), 0, "add -p"),
    (bash_payload("git push origin gov-d-mechanisms"), 0, "push a branch"),
    (bash_payload("git push origin HEAD:gov-d-mechanisms"), 0, "push HEAD:branch"),
    (bash_payload("git worktree add ../GItS-foo -b foo"), 0, "worktree add"),
    (bash_payload("git worktree prune"), 0, "worktree prune"),
    (bash_payload("git worktree list"), 0, "worktree list"),
    (bash_payload("git commit -m 'main: a message mentioning git add -A'"), 0,
     "the rule named inside a quoted message"),
    (bash_payload("git status --short"), 0, "status"),
    (bash_payload("python -m tools.purge_worktree ../GItS-foo"), 0, "the legal purge"),
    (bash_payload(""), 0, "empty command"),
    ("not json at all", 0, "unparseable payload"),
]


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test(CASES, decide)
    return decide(read_payload())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
