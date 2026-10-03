#!/usr/bin/env python3
"""The shipped card-image set: the one list deploy stages into images/cards.

THE DEFECT. Both deploy scripts copied every png in the five
`ImageGen/images/cards/<dir>` folders into the flat `images/cards` next to the
dll. ImageGen keeps the paintings of cut cards and of the deleted old kits on
purpose (`tools/art_coverage.py` lists them as STALE, "NOT coverage for
anything"), so the 2026-10-02 deploy shipped 743 images where 433 can ever be
drawn: about 310 files and 71 MB of art for cards that no longer exist.

WHAT THE GAME CAN DRAW. `RosterArt.CardPortrait("<id>")`
(klee-mod/KleeCode/KleeArt.cs) is the only code that reads `images/cards`,
and every call passes a literal key -- generated rows, hand-written cards,
tokens, Ancients, mode faces and C#-only cards alike. A row with
`art_of: <neighbour>` is generated asking for the neighbour's key. So the
literal keys in the mod source ARE the runtime set (`art_coverage.mod_art_keys`).
A key with no png falls back to RosterArt's blank portrait, logged once.

THE SURFACE CROSS-CHECK. `docs/prototype-surface.yaml` says the same thing
another way: every row id that wears no neighbour, plus every `art_of`
target. A surface key the C# does not ask for means the generated C# is stale
(or a hand-written class forgot its portrait); that is a finding, never a
silent drop.

The pck carries no card portraits (`tools/build_pck.ps1`'s header): card art
reaches the game only through this staging step.

Usage (deploy.ps1 / deploy_proto.ps1 call --stage; validate.ps1 calls --list):
  python tools/shipped_card_art.py                  # dry run: what ships, what is dropped
  python tools/shipped_card_art.py --stage DIR      # copy the shipped set into DIR
  python tools/shipped_card_art.py --check-stage DIR  # DIR holds exactly the shipped set
  python tools/shipped_card_art.py --list           # one shipped stem per line
  --images-root PATH  overrides ImageGen/images/cards (default: this checkout's)
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import art_coverage  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SURFACE = ROOT / "docs" / "prototype-surface.yaml"
IMAGES = art_coverage.IMAGES


def runtime_keys(src: Path = art_coverage.MOD_SRC) -> set[str]:
    """Every portrait key the compiled mod can ask for."""
    return set(art_coverage.mod_art_keys(src))


def surface_keys(surface: Path = SURFACE) -> set[str]:
    """Live surface row ids that wear their own art, plus every art_of target."""
    rows = yaml.safe_load(surface.read_text(encoding="utf-8")) or []
    keys = set()
    for row in rows:
        if not isinstance(row, dict) or "id" not in row:
            continue
        keys.add(row.get("art_of") or row["id"])
    return keys


def shipped_keys(src: Path = art_coverage.MOD_SRC,
                 surface: Path = SURFACE) -> set[str]:
    """THE shipped set's keys: the runtime set, widened by the surface set.

    The two agree today (the test holds them together); the union is what
    ships so that a drift between them costs spare megabytes, never a blank
    card.
    """
    return runtime_keys(src) | surface_keys(surface)


def source_images(images_root: Path = IMAGES) -> dict[str, Path]:
    """stem -> png across EVERY card dir under images_root, read off disk.

    Not a closed list of directories: a character left off such a list is
    how Kokomi's art missed the stage for a day (2026-07-25). Ids are unique
    across characters (`tools/lint_unique_names.py`) and the stage is flat;
    on a duplicate stem the first dir in name order wins.
    """
    out: dict[str, Path] = {}
    if not images_root.is_dir():
        return out
    for d in sorted(x for x in images_root.iterdir() if x.is_dir()):
        for p in sorted(d.glob("*.png")):
            out.setdefault(p.stem, p)
    return out


def plan(images_root: Path = IMAGES, keys: set[str] | None = None):
    """(ship, dropped, missing): ship and dropped are {stem: path}, missing is
    the sorted keys with no png (each renders RosterArt's blank)."""
    keys = shipped_keys() if keys is None else keys
    images = source_images(images_root)
    ship = {s: p for s, p in images.items() if s in keys}
    dropped = {s: p for s, p in images.items() if s not in keys}
    missing = sorted(k for k in keys if k not in images)
    return ship, dropped, missing


def missing_findings(missing) -> list[str]:
    """A shipped key with no png must be on art_coverage.KNOWN_MISSING, and
    every KNOWN_MISSING entry must still be a missing shipped key."""
    known = art_coverage.KNOWN_MISSING
    out = [f"{k}: requested by the mod, no png, not on "
           f"art_coverage.KNOWN_MISSING (renders blank)"
           for k in missing if k not in known]
    out += [f"{k}: on art_coverage.KNOWN_MISSING but no longer a missing "
            f"shipped key -- delete the entry" for k in sorted(known)
            if k not in missing]
    return out


def check_stage(stage: Path, images_root: Path = IMAGES,
                keys: set[str] | None = None) -> list[str]:
    """A staged images/cards must hold every shipped png and nothing else."""
    ship, _dropped, _missing = plan(images_root, keys)
    staged = {p.stem for p in stage.glob("*.png")} if stage.is_dir() else set()
    out = [f"{s}.png ships in the set and is not staged (renders blank)"
           for s in sorted(set(ship) - staged)]
    out += [f"{s}.png is staged and no card can draw it" for s in
            sorted(staged - set(ship))]
    return out


def stage_to(dest: Path, images_root: Path = IMAGES) -> tuple[int, int]:
    """Copy the shipped set into dest. Returns (files, bytes)."""
    ship, _d, _m = plan(images_root)
    dest.mkdir(parents=True, exist_ok=True)
    total = 0
    for stem, path in sorted(ship.items()):
        shutil.copy2(path, dest / f"{stem}.png")
        total += path.stat().st_size
    return len(ship), total


def _mb(n: int) -> str:
    return f"{n / 1e6:.1f} MB"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--images-root", type=Path, default=IMAGES)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--stage", type=Path)
    g.add_argument("--check-stage", type=Path)
    g.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    root = args.images_root

    if not root.is_dir():
        print(f"no card art at {root}")
        return 1 if args.stage or args.check_stage else 0

    if args.list:
        ship, _d, _m = plan(root)
        print("\n".join(sorted(ship)))
        return 0
    if args.check_stage:
        findings = check_stage(args.check_stage, root)
        for f in findings:
            print(f"  {f}")
        print(f"shipped card art vs stage: {len(findings)} finding(s)")
        return 1 if findings else 0
    if args.stage:
        n, size = stage_to(args.stage, root)
        _s, dropped, missing = plan(root)
        print(f"Staged {n} card images ({_mb(size)}); left {len(dropped)} "
              f"unreachable ImageGen png(s) behind; {len(missing)} shipped "
              f"key(s) have no png")
        return 0

    ship, dropped, missing = plan(root)
    drift = sorted(surface_keys() - runtime_keys())
    size = lambda d: sum(p.stat().st_size for p in d.values())  # noqa: E731
    print(f"SHIPPED  {len(ship)} png ({_mb(size(ship))})")
    print(f"DROPPED  {len(dropped)} png ({_mb(size(dropped))}) -- in ImageGen, "
          f"drawn by no card:")
    for stem, path in sorted(dropped.items()):
        print(f"  {path.parent.name}/{stem}.png")
    print(f"MISSING  {len(missing)} shipped key(s) with no png (blank portrait):")
    for k in missing:
        tag = "known" if k in art_coverage.KNOWN_MISSING else "NEW"
        print(f"  [{tag}] {k}")
    if drift:
        print("SURFACE KEYS THE C# DOES NOT ASK FOR (regenerate the C#):")
        for k in drift:
            print(f"  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
