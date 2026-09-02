#!/usr/bin/env python3
"""Land a PLUMBING pull request: check CI, merge, purge the worktree, fast-forward.

THE RITUAL, AND THE TRAP IN IT. Landing a plumbing PR is five steps, four
mechanical and one that has bitten twice in a week:

  1. read the merge state and every check run (a REST call, `gh api`);
  2. `gh pr merge <n> --merge` -- merge commits, matching this repo's history;
  3. retire the branch's sibling worktree with `tools/purge_worktree`, never
     `git worktree remove` (`EB-128`: it deletes gitignored content out of a
     clean tree and took both `game_ref/` backups doing it);
  4. fast-forward the main checkout;
  5. **the trap** -- a file the branch COMMITTED can still be sitting UNTRACKED
     in the main checkout, because a sitting wrote it there first and committed
     it from the worktree. `git pull` then refuses with "untracked working tree
     files would be overwritten", and the whole land stops on a file that is
     already correct.

Step 5 is the reason this exists rather than a three-line skill. A blocking
untracked file whose bytes are IDENTICAL to the incoming version is deleted
(nothing is lost -- the identical bytes arrive with the pull, and the file is
in git from that moment). One whose bytes DIFFER stops the land and is named,
with both hashes, because that is an unsaved change and no tool gets to guess.

    python tools/land_pr.py 297
    python tools/land_pr.py 297 --dry-run          # decide, do nothing
    python tools/land_pr.py 297 --no-purge         # keep the worktree
    python tools/land_pr.py 297 --oneline

REFUSES on a red or pending check, on a PR that is not mergeable, and -- always
-- if the merge would be anything but `--merge`. This lands PLUMBING only:
CLAUDE.md's Norms define it (no card-sheet number, no balance constant, no LAW
or EXPERIMENTS text, no design prose), and that judgement is the caller's.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

GH_CANDIDATES = (
    r"C:\Program Files\GitHub CLI\gh.exe",
    r"C:\Program Files (x86)\GitHub CLI\gh.exe",
)

#: Check-run conclusions that are not a reason to stop. `neutral` and `skipped`
#: are how a path-filtered job reports "not my change".
OK_CONCLUSIONS = {"success", "neutral", "skipped"}


def gh_path(explicit: str = "") -> str:
    import shutil
    if explicit:
        return explicit
    found = shutil.which("gh")
    if found:
        return found
    for candidate in GH_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise SystemExit(r"gh not found; it lives at 'C:\Program Files\GitHub "
                     r"CLI\gh.exe' on this machine. Pass --gh <path>.")


def _run(argv: list[str], cwd: Path = REPO) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, cwd=str(cwd))


def _git(args: list[str], cwd: Path = REPO) -> subprocess.CompletedProcess:
    return _run(["git", *args], cwd)


def main_checkout(root: Path = REPO) -> Path:
    """The primary working tree, even when this runs from a worktree."""
    res = _git(["rev-parse", "--path-format=absolute", "--git-common-dir"],
               cwd=root)
    if res.returncode or not res.stdout.strip():
        return root
    common = Path(res.stdout.strip())
    return common.parent if common.name == ".git" else root


def pr_state(gh: str, number: int) -> dict:
    """`{state, mergeable, head branch, checks: [(name, conclusion)]}`."""
    res = _run([gh, "pr", "view", str(number), "--json",
                "number,title,state,mergeable,mergeStateStatus,"
                "headRefName,baseRefName,statusCheckRollup"])
    if res.returncode:
        raise SystemExit(f"gh pr view {number} failed:\n{res.stderr.strip()}")
    blob = json.loads(res.stdout)
    checks = []
    for row in blob.get("statusCheckRollup") or []:
        name = row.get("name") or row.get("context") or "?"
        outcome = (row.get("conclusion") or row.get("state")
                   or row.get("status") or "").lower()
        checks.append((name, outcome))
    blob["checks"] = checks
    return blob


def blocking_untracked(branch: str, root: Path) -> tuple[list[str], list[str]]:
    """`(identical, differing)` untracked files the incoming merge would touch.

    Compared BY CONTENT, `git hash-object` against the blob the remote branch
    carries at the same path -- so "identical" is the same test git itself
    would apply, and "differing" is a real unsaved difference rather than a
    timestamp or a line-ending guess.
    """
    listed = _git(["ls-files", "--others", "--exclude-standard"], cwd=root)
    untracked = [p for p in listed.stdout.split("\n") if p.strip()]
    if not untracked:
        return [], []
    incoming = _git(["ls-tree", "-r", "--name-only", f"origin/{branch}"],
                    cwd=root)
    arriving = {p for p in incoming.stdout.split("\n") if p.strip()}
    same, different = [], []
    for rel in untracked:
        if rel not in arriving:
            continue
        theirs = _git(["rev-parse", f"origin/{branch}:{rel}"], cwd=root)
        local = _git(["hash-object", rel], cwd=root)
        if theirs.returncode or local.returncode:
            different.append(rel)
        elif theirs.stdout.strip() == local.stdout.strip():
            same.append(rel)
        else:
            different.append(rel)
    return same, different


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("number", type=int)
    ap.add_argument("--gh", default="")
    ap.add_argument("--dry-run", action="store_true",
                    help="report the decision and touch nothing")
    ap.add_argument("--no-purge", action="store_true",
                    help="leave the branch's worktree in place")
    ap.add_argument("--oneline", action="store_true")
    args = ap.parse_args(argv)

    gh = gh_path(args.gh)
    pr = pr_state(gh, args.number)
    branch = pr["headRefName"]
    root = main_checkout()
    bad = [f"{n}={c or 'pending'}" for n, c in pr["checks"]
           if c not in OK_CONCLUSIONS]
    mergeable = pr.get("mergeable") == "MERGEABLE" and pr.get("state") == "OPEN"

    lines: list[str] = []
    verdict = "GREEN"
    if pr.get("state") != "OPEN":
        verdict = f"REFUSED -- PR is {pr.get('state')}"
    elif bad:
        verdict = f"REFUSED -- {len(bad)} check(s) not green: {', '.join(bad)}"
    elif not mergeable:
        verdict = (f"REFUSED -- not mergeable "
                   f"({pr.get('mergeStateStatus')}); rebase or resolve first")

    _git(["fetch", "origin", branch], cwd=root)
    same, different = blocking_untracked(branch, root)
    if different and verdict == "GREEN":
        verdict = (f"REFUSED -- {len(different)} untracked file(s) in the main "
                   f"checkout DIFFER from the incoming version: "
                   f"{', '.join(different)}. Save or delete them by hand; a "
                   f"tool does not get to choose which copy survives.")

    if args.dry_run or verdict != "GREEN":
        head = (f"land_pr #{args.number} ({branch}): {verdict}")
        if args.oneline:
            print(head)
        else:
            print(head)
            print(f"  checks:    {len(pr['checks'])} run, "
                  f"{len(pr['checks']) - len(bad)} green")
            print(f"  untracked: {len(same)} identical, "
                  f"{len(different)} differing")
        return 0 if (args.dry_run and verdict == "GREEN") else (
            0 if verdict == "GREEN" else 1)

    for rel in same:
        (root / rel).unlink(missing_ok=True)
    merged = _run([gh, "pr", "merge", str(args.number), "--merge"])
    if merged.returncode:
        print(f"land_pr #{args.number}: MERGE FAILED\n"
              f"{(merged.stdout + merged.stderr).strip()}")
        return 1

    purged = ""
    worktree = root.parent / f"GItS-{branch}"
    if not args.no_purge and worktree.exists():
        res = _run([sys.executable, "-m", "tools.purge_worktree",
                    str(worktree)], cwd=root)
        purged = ("purged" if res.returncode == 0
                  else f"REFUSED (exit {res.returncode}) -- "
                       f"{(res.stdout or '').strip().splitlines()[-1:] or ''}")
    elif not args.no_purge:
        purged = "none found"
    else:
        purged = "kept (--no-purge)"

    _git(["checkout", "main"], cwd=root)
    pull = _git(["pull", "--ff-only", "origin", "main"], cwd=root)
    at = _git(["rev-parse", "--short", "HEAD"], cwd=root).stdout.strip()

    if args.oneline:
        print(f"land_pr: #{args.number} merged; worktree {purged}; "
              f"main at {at}"
              f"{'' if pull.returncode == 0 else ' (FF FAILED)'}")
        return 0 if pull.returncode == 0 else 1
    print(f"merged:   #{args.number} {pr.get('title', '')} ({branch})")
    print(f"worktree: {worktree.name} {purged}"
          + (f"; removed {len(same)} identical untracked file(s)"
             if same else ""))
    print(f"main:     {at}"
          + ("" if pull.returncode == 0
             else f" -- FAST-FORWARD FAILED: {pull.stderr.strip()}"))
    return 0 if pull.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
