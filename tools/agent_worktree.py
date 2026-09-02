#!/usr/bin/env python3
"""Open a sibling worktree for one workstream, and print what to read in it.

THE RITUAL. Every agent handed a workstream types the same four things: a
fetch, `git worktree add ../GItS-<name> -b <branch> origin/main`, a copy of
`klee-mod/local.props` (a worktree has none, and half the build refuses without
it), and then a guess at which of CLAUDE.md's on-demand documents its task
needs. The first three are mechanical. The fourth is CLAUDE.md's own read
order, which is written down and is nonetheless re-derived by hand every time.

    python tools/agent_worktree.py kokomi-fold --task build
    python tools/agent_worktree.py r241-slate --task packet --base origin/main
    python tools/agent_worktree.py audit-2026-09-02 --task audit --dry-run
    python tools/agent_worktree.py klee-r6 --task seat --oneline

SIBLING DIRECTORIES ONLY, and nothing is ever linked into one. That is
`operations/worktrees.md`'s rule and it is not stylistic: a junction to a
gitignored asset tree is FOLLOWED and deleted by a worktree teardown, and doing
it once cost this repo `game_ref/` twice. This tool creates the directory and
copies ONE file into it, by value.

IT REFUSES WHILE A SEAT IS LIVE IN THIS CHECKOUT. `understudy/logs/embark-*.json`
is the manifest of an open run and `--teardown` is what closes it; a sidecar
whose reversibility ledger still carries APPLIED rows, on a lane whose bridge
port answers, is a game that is UP. Adding a worktree in that state is how a
session ends up with two checkouts both thinking they own lane 1's profile --
and `deploy_proto.ps1` already refuses for the same reason, by image name,
because one install means one deployed build for every lane.
"""
from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: CLAUDE.md's on-demand read order, per task shape. ALWAYS is its "always"
#: pair; the rest is the file the task names and nothing else, which is the
#: whole point of the read order -- a fresh session must not bulk-load the repo.
ALWAYS = ("CLAUDE.md", "docs/current/STATE.md")
READ_LISTS: dict[str, tuple[str, ...]] = {
    "build": (
        "docs/current/BACKLOG.md -- the one engineering register (the row you "
        "are building)",
        "docs/current/operations/test.md -- the suite, the fast lane, the "
        "parallel lanes",
        "docs/current/operations/lints.md -- run_lints and how to add one",
        "docs/current/operations/prototype.md -- if the work is behind the "
        "PROTOTYPE_CARDS switch",
        "docs/current/operations/codegen.md -- if a YAML sheet moves",
        "the ONE yaml sheet the task touches; never all of them",
    ),
    "packet": (
        "docs/current/LAW.md -- the governing constraints",
        "docs/current/QUEUE.md -- [USER]'s open A/B/C picks, and nothing else",
        "docs/current/kit-checklist.md -- the yes/no checks a kit sheet meets",
        "docs/current/RULINGS.md -- to close a re-ask by its ruling id",
        "docs/current/operations/stage-gate.md -- Paper / Prototype / Balance",
        "the packet in review/active/ this work belongs to",
    ),
    "seat": (
        "docs/current/operations/understudy-seats.md -- scenarios, staged "
        "rounds, seats, blind play, lanes",
        "docs/current/operations/seat-brief.md -- the blindness rules to hand "
        "an Opus seat",
        "docs/current/EXPERIMENTS.md -- measurement law, if this is a Balance "
        "reading",
        "docs/current/operations/prototype.md -- the arm door for a +proto run",
    ),
    "audit": (
        "docs/current/BACKLOG.md and docs/current/QUEUE.md -- the two "
        "registers a finding triages into",
        "docs/current/LAW.md -- before calling anything a defect",
        "docs/current/RULINGS.md -- a question already ruled is closed by its "
        "id, not re-asked",
        "docs/current/operations/mechanisms.md -- what is enforced, and by what",
        "docs/current/operations/register-ids.md -- before minting a row",
    ),
}

#: Lane label -> bridge port, mirrored from `understudy/instances.py`. Read
#: rather than imported: importing `instances` pulls `soak` in behind it and
#: this tool must run in a checkout with no game and no local.props.
LANE_PORTS = {"lane0": 15526, "lane1": 15527, "lane2": 15528}


def _git(args: list[str], cwd: Path = REPO) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          cwd=str(cwd))


def main_checkout(root: Path = REPO) -> Path:
    """The ART-BEARING primary checkout, even when this runs from a worktree.

    `--git-common-dir` is the shared `.git` every worktree points at; its
    parent is the main working tree. This matters for exactly one file --
    `klee-mod/local.props`, which names THIS machine's Steam install, is
    gitignored, and exists only in the primary checkout — and for the lane
    scan, since the game is deployed from there.
    """
    res = _git(["rev-parse", "--path-format=absolute", "--git-common-dir"],
               cwd=root)
    if res.returncode or not res.stdout.strip():
        return root
    common = Path(res.stdout.strip())
    return common.parent if common.name == ".git" else root


def _port_answers(port: int, timeout: float = 0.35) -> bool:
    """True if something is listening. A CONNECT, never a request."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout):
            return True
    except OSError:
        return False


def live_lanes(root: Path = REPO) -> list[str]:
    """Every lane this checkout has embarked and not torn down, with evidence.

    Two conditions, both required. The SIDECAR says this checkout opened a run
    (`understudy/logs/embark-<stamp>.json`) and its reversibility ledger still
    carries `APPLIED` rows, which is what `--teardown` turns into `REVERTED`.
    The PORT says a game is actually up on that lane. Either alone is a false
    positive: a sidecar outlives a crashed game, and lane 0's port answers for
    the owner's own Steam launch, which is none of this tool's business.
    """
    out: list[str] = []
    logs = root / "understudy" / "logs"
    for sidecar in sorted(logs.glob("embark-*.json")):
        try:
            blob = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ledger = Path(blob.get("ledger") or "")
        try:
            entries = json.loads(ledger.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not any(e.get("state") == "APPLIED" for e in entries):
            continue
        label = str(blob.get("instance") or "lane0")
        port = int(blob.get("port") or LANE_PORTS.get(label, 15526))
        if _port_answers(port):
            out.append(f"{label} (port {port}, sidecar {sidecar.name}, "
                       f"ledger still APPLIED)")
    return out


def read_list(task: str) -> list[str]:
    return [*ALWAYS, *READ_LISTS[task]]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="the workstream: `../GItS-<name>`, and the "
                                 "branch name unless --branch says otherwise")
    ap.add_argument("--base", default="origin/main",
                    help="the ref to branch from (default origin/main, "
                         "fetched first)")
    ap.add_argument("--branch", default="",
                    help="branch name (default: the workstream name)")
    ap.add_argument("--task", choices=sorted(READ_LISTS), default="build",
                    help="which of CLAUDE.md's read orders to print")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--allow-live-lane", action="store_true",
                    help="proceed even with a seat up in this checkout")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and the read list, create nothing")
    ap.add_argument("--oneline", action="store_true")
    args = ap.parse_args(argv)

    branch = args.branch or args.name
    target = (REPO.parent / f"GItS-{args.name}").resolve()

    primary = main_checkout()
    lanes = live_lanes()
    if primary != REPO:
        lanes += live_lanes(primary)
    if lanes and not args.allow_live_lane:
        print("REFUSED: a seat is live in this checkout -- " + "; ".join(lanes))
        print("  Tear it down first (python -m understudy.embark --teardown "
              "[--lane N]); one install means one deployed build for every "
              "lane, and a second checkout cannot own the same profile.")
        print("  --allow-live-lane if you have read that and it is fine.")
        return 2

    if target.exists():
        print(f"REFUSED: {target} already exists. Retire it with "
              f"`python -m tools.purge_worktree {target}` "
              f"(never `git worktree remove`) or pick another name.")
        return 2

    if args.dry_run:
        if not args.oneline:
            print(f"would fetch:   {'no' if args.no_fetch else 'origin'}")
            print(f"would create:  {target}")
            print(f"on branch:     {branch} from {args.base}")
            props = primary / "klee-mod" / "local.props"
            print(f"would copy:    {props} "
                  f"({'present' if props.exists() else 'absent, skipped'})")
    else:
        if not args.no_fetch:
            fetched = _git(["fetch", "origin"])
            if fetched.returncode:
                print(f"REFUSED: git fetch origin failed:\n"
                      f"{fetched.stderr.strip()}")
                return 1
        made = _git(["worktree", "add", "-b", branch, str(target), args.base])
        if made.returncode:
            print(f"REFUSED: git worktree add failed:\n{made.stderr.strip()}")
            return 1
        props = primary / "klee-mod" / "local.props"
        if props.exists():
            shutil.copyfile(props, target / "klee-mod" / "local.props")

    reads = read_list(args.task)
    if args.oneline:
        print(f"agent_worktree: {target.name} on {branch} from {args.base}"
              f"{' (dry run)' if args.dry_run else ''}; "
              f"read {len(reads)} file(s) for --task {args.task}")
        return 0

    print(f"\nworktree: {target}")
    print(f"branch:   {branch} (from {args.base})")
    print(f"\nRead order for --task {args.task} (CLAUDE.md; nothing else, and "
          f"never git history or review/):")
    for i, item in enumerate(reads, 1):
        print(f"  {i}. {item}")
    print("\nWork ONLY in that directory. Stage by name -- `git add -A` is "
          "denied by tools/hooks/deny_dangerous_git.py. Retire it with "
          "`python -m tools.purge_worktree`, never `git worktree remove`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
