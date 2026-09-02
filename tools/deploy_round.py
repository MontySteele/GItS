#!/usr/bin/env python3
"""Decide and drive one dev deploy: pck if it is stale, deploy_proto, verify.

THE RITUAL, AND THE MISTAKE IN IT. A round's deploy is `build_pck.ps1` then
`deploy_proto.ps1` with the arm switches, then three things read back off disk.
Two of those steps have a decision in them that gets taken wrong:

  * **Whether the pck needs rebuilding.** `klee-mod/assets/klee.pck` is built
    from `ImageGen/images/**` and `klee-mod/pck-src/**`; if either moved since
    the pck's mtime, deploying without rebuilding ships a package whose art is
    a build behind. Both source trees are gitignored or scene-source, so `git
    status` says nothing about it. This tool compares mtimes and says so.
  * **Where it runs.** `build_pck` and `deploy_proto` are main-checkout-only:
    a worktree has no `local.props` and no art. Agents deployed from a worktree
    twice this week; `tools/hooks/deny_deploy_outside_main.py` is the hard stop
    and this is the one that explains itself.

    python tools/deploy_round.py --dry-run                    # the decision
    python tools/deploy_round.py --arms klee,companion,kokomi --dry-run
    python tools/deploy_round.py --arms klee --pck            # force the pck
    python tools/deploy_round.py --oneline

THE ARMS are `deploy_proto.ps1`'s own switches, named here in lower case:
`klee` -> `-KleeOverhaul`, `companion` -> `-CompanionOverhaul`, `kokomi` ->
`-KokomiOverhaul`, `furina` -> `-FurinaReframe`. They are independent and the
supported dev build carries all of them; a dev build always carries the
prototype surface, because that is what `deploy_proto.ps1` IS.

IT REFUSES WHILE THE GAME IS UP, by image name and for the same reason the
script does: one install means ONE deployed build for every lane, so a second
lane's game holds the same lock on `klee.dll` as the first. Tear the lane down
(`python -m understudy.embark --teardown --lane N`) rather than deploying
around it.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: lower-case arm -> the switch `deploy_proto.ps1` declares for it.
ARMS = {
    "klee": "-KleeOverhaul",
    "companion": "-CompanionOverhaul",
    "kokomi": "-KokomiOverhaul",
    "furina": "-FurinaReframe",
}

PCK = "klee-mod/assets/klee.pck"
#: What the pck is BUILT FROM. `ImageGen/images` is gitignored Tier F art and
#: `klee-mod/pck-src` is the git-tracked scene-source overlay; the build reads
#: both, so either moving makes the pck stale.
PCK_SOURCES = ("ImageGen/images", "klee-mod/pck-src")


def _git(args: list[str], cwd: Path = REPO) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          cwd=str(cwd))


def is_main_checkout(root: Path = REPO) -> bool:
    """True when `root` is the primary working tree, not a linked worktree."""
    res = _git(["rev-parse", "--path-format=absolute", "--git-common-dir"],
               cwd=root)
    if res.returncode or not res.stdout.strip():
        return False
    common = Path(res.stdout.strip())
    return common.name == ".git" and common.parent.resolve() == root.resolve()


def game_running() -> list[str]:
    """Every `SlayTheSpire2` pid, by IMAGE NAME. Empty list when none."""
    try:
        res = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq SlayTheSpire2.exe", "/NH",
             "/FO", "CSV"], capture_output=True, text=True)
    except OSError:
        return []
    pids = []
    for line in (res.stdout or "").split("\n"):
        parts = [p.strip('" ') for p in line.split('","')]
        if len(parts) > 1 and parts[0].lower().startswith("slaythespire2"):
            pids.append(parts[1])
    return pids


def newest(rel: str, root: Path = REPO) -> float:
    """The newest mtime under a path, or 0.0 if it is not there."""
    base = root / rel
    if not base.exists():
        return 0.0
    if base.is_file():
        return base.stat().st_mtime
    best = 0.0
    for p in base.rglob("*"):
        if p.is_file():
            best = max(best, p.stat().st_mtime)
    return best


def pck_decision(root: Path = REPO) -> tuple[bool, str]:
    """`(rebuild?, why)` -- the mtime comparison, stated in words."""
    pck = newest(PCK, root)
    if not pck:
        return True, f"{PCK} does not exist"
    movers = [rel for rel in PCK_SOURCES if newest(rel, root) > pck]
    if movers:
        return True, f"{', '.join(movers)} changed since the pck was built"
    absent = [rel for rel in PCK_SOURCES if not (root / rel).exists()]
    if absent:
        return False, (f"pck is present and {', '.join(absent)} is not in this "
                       f"checkout -- nothing to compare it against")
    return False, "pck is newer than both source trees"


def verification(root: Path = REPO) -> list[str]:
    """The three lines a deploy is read back on, off disk.

    Deliberately NOT the deploy script's own stdout: a deploy that printed
    success and staged nothing is the failure this reads past.
    """
    game_dir = None
    props = root / "klee-mod" / "local.props"
    if props.exists():
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(props)
            found = tree.find(".//GameDir")
            if found is not None and found.text:
                game_dir = Path(found.text.strip())
        except ET.ParseError:
            game_dir = None
    if game_dir is None:
        return ["installed version: UNKNOWN -- no readable klee-mod/local.props",
                "bridge:            UNKNOWN", "staged images:     UNKNOWN"]

    manifest = game_dir / "mods" / "klee" / "manifest.json"
    try:
        version = json.loads(manifest.read_text(encoding="utf-8")).get(
            "version", "?")
    except (OSError, ValueError):
        version = "NOT INSTALLED"
    bridge = (game_dir / "mods" / "STS2_MCP").is_dir()
    images = game_dir / "mods" / "klee" / "images" / "cards"
    count = len(list(images.glob("*.png"))) if images.is_dir() else 0
    return [f"installed version: {version}  ({manifest})",
            f"bridge:            {'present' if bridge else 'ABSENT'} "
            f"({game_dir / 'mods' / 'STS2_MCP'})",
            f"staged images:     {count} card png(s)"]


def plan(args) -> list[list[str]]:
    """The PowerShell commands this round would run, in order."""
    out: list[list[str]] = []
    rebuild, _ = pck_decision()
    if args.pck or rebuild:
        out.append(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-File", "tools\\build_pck.ps1"])
    switches = [ARMS[a] for a in args.arms]
    out.append(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", "klee-mod\\build\\deploy_proto.ps1", *switches])
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default="",
                    help="comma-separated: " + ", ".join(sorted(ARMS)))
    ap.add_argument("--pck", action="store_true",
                    help="rebuild the pck whatever the mtimes say")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the decision and the commands, run nothing")
    ap.add_argument("--oneline", action="store_true")
    args = ap.parse_args(argv)

    names = [a.strip().lower() for a in args.arms.split(",") if a.strip()]
    unknown = [a for a in names if a not in ARMS]
    if unknown:
        print(f"REFUSED: unknown arm(s) {', '.join(unknown)}. "
              f"Known: {', '.join(sorted(ARMS))}")
        return 2
    args.arms = names

    if not is_main_checkout():
        print("REFUSED: this is not the main checkout. `build_pck.ps1` and "
              "`deploy_proto.ps1` run from the art-bearing primary tree only "
              "-- a worktree has no klee-mod/local.props and no "
              "ImageGen/images, so a deploy from one ships a package with no "
              "art. The bridge build (`deploy_bridge.ps1 -BuildOnly`) is the "
              "one legal build in a worktree.")
        return 2

    running = game_running()
    if running and not args.dry_run:
        print(f"REFUSED: Slay the Spire 2 is running (PID "
              f"{', '.join(running)}). Close EVERY game process: one install "
              f"means one deployed build for all lanes, so a second lane's "
              f"game holds the same lock on klee.dll. Tear the lane down "
              f"(python -m understudy.embark --teardown --lane N).")
        return 2

    rebuild, why = pck_decision()
    steps = plan(args)

    if args.dry_run:
        if args.oneline:
            print(f"deploy_round: pck "
                  f"{'REBUILD' if (args.pck or rebuild) else 'skip'} ({why}); "
                  f"arms {', '.join(args.arms) or 'none'}; "
                  f"{len(steps)} command(s); "
                  f"game {'UP -- ' + ', '.join(running) if running else 'closed'}")
            return 0
        print(f"pck:  {'REBUILD' if (args.pck or rebuild) else 'skip'} -- {why}"
              + ("  (--pck forced)" if args.pck and not rebuild else ""))
        print(f"arms: {', '.join(args.arms) or 'none (prototype surface only)'}")
        print(f"game: {'UP -- ' + ', '.join(running) if running else 'closed'}")
        print("\nwould run:")
        for cmd in steps:
            print("  " + " ".join(cmd))
        print("\nwould then verify:")
        for line in verification():
            print("  " + line)
        return 0

    for cmd in steps:
        res = subprocess.run(cmd, cwd=str(REPO))
        if res.returncode:
            print(f"deploy_round: FAILED at `{' '.join(cmd)}` "
                  f"(exit {res.returncode})")
            return res.returncode
    lines = verification()
    if args.oneline:
        print("deploy_round: " + "; ".join(l.split(":", 1)[1].strip()
                                           for l in lines))
        return 0
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
