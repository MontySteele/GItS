#!/usr/bin/env python3
"""Mirror the primary checkout's `game_ref/` into the OneDrive vault.

**THE GUARD IS THE POINT.** This tool REFUSES to run (exit 2) when the source
`game_ref/` is missing or holds fewer than ten files. Read that as the whole
reason the tool exists rather than as a nicety: `game_ref/` has been destroyed
four times, and each time the directory was left *present and empty* with
`git status` clean. A plain mirror pointed at a destroyed-empty source would
faithfully propagate the destruction -- delete every file in the vault -- and
the one surviving copy of thirteen hand-authored, explicitly NOT
tool-regenerable pass layers would be gone the moment someone ran the backup
"to be safe". The refusal is what makes an unattended run safe to type.

The vault is `C:\\Users\\Monty\\OneDrive\\GItS-vault\\game_ref`, ruled by
[USER] 2026-08-24: "Agreed on the backup in OneDrive". OneDrive is chosen
precisely because it is NOT a directory git or a worktree teardown can reach:
the 2026-08-24 loss took both prior backup copies because they lived inside
worktrees, and `git worktree remove` deletes gitignored content out of a clean
worktree. **Backups never live in worktrees** -- see OPERATIONS.md.

Source resolution: the repo root is taken from this script's own location, so
the tool works from whatever checkout it is invoked in. That is a convenience,
not a licence -- the **primary checkout** (`C:\\Users\\Monty\\Documents\\GitHub\\GItS`)
is the canonical source. `game_ref/` is gitignored and decompile-derived, so a
worktree has none at all; running this there hits the guard and exits 2, which
is the correct answer rather than a bug.

What it does once the guard passes: copies files that are new or changed
(mtime/size), deletes vault files whose source is gone, leaves the rest alone,
and prints a table of the three counts.

    python -m tools.backup_game_ref              # mirror
    python -m tools.backup_game_ref --dry-run    # say what it would do
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "game_ref"

# RULED by [USER] 2026-08-24 -- "Agreed on the backup in OneDrive". Hard-coded
# on purpose: a configurable backup root is a backup root that can be pointed
# at a temp directory and quietly stop being a backup.
VAULT = Path(r"C:\Users\Monty\OneDrive\GItS-vault\game_ref")

# The guard threshold. A complete game_ref is 25 files today; validate.ps1's S7
# reference list alone names 8. Ten is comfortably below any real tree and
# comfortably above the destroyed-empty state (0) this exists to refuse.
MIN_SOURCE_FILES = 10

# Filesystem skew tolerance, seconds. FAT/exFAT store mtimes at 2 s
# granularity, and a OneDrive round trip can land a hair either side of the
# NTFS value, so "source is newer" means newer by more than this.
SKEW_SECONDS = 2.0


def relative_files(root: Path) -> dict[str, Path]:
    """{posix relative path: absolute path} for every file under `root`."""
    if not root.is_dir():
        return {}
    return {p.relative_to(root).as_posix(): p
            for p in sorted(root.rglob("*")) if p.is_file()}


def guard(source: Path) -> str | None:
    """The refusal reason, or None when mirroring is safe.

    Split out from `main` so the suite (and a reader) can see the two refusal
    cases without running a mirror.
    """
    if not source.is_dir():
        return f"source game_ref does not exist: {source}"
    count = len(relative_files(source))
    if count < MIN_SOURCE_FILES:
        return (f"source game_ref holds {count} file(s), fewer than the "
                f"{MIN_SOURCE_FILES}-file floor: {source}")
    return None


def needs_copy(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True
    s, d = src.stat(), dst.stat()
    return s.st_size != d.st_size or s.st_mtime > d.st_mtime + SKEW_SECONDS


def mirror(source: Path, vault: Path, dry_run: bool = False
           ) -> tuple[list[str], list[str], list[str]]:
    """Return (copied, deleted, unchanged) as sorted relative-path lists."""
    src_files = relative_files(source)
    vault_files = relative_files(vault)

    copied, unchanged = [], []
    for rel, src in src_files.items():
        dst = vault / rel
        if needs_copy(src, dst):
            copied.append(rel)
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)          # copy2 keeps mtime, which is
        else:                                   # what the lint compares
            unchanged.append(rel)

    deleted = sorted(set(vault_files) - set(src_files))
    if not dry_run:
        for rel in deleted:
            vault_files[rel].unlink()
        # Prune directories the deletions emptied; never the vault root.
        for d in sorted((p for p in vault.rglob("*") if p.is_dir()),
                        key=lambda p: -len(p.parts)):
            if not any(d.iterdir()):
                d.rmdir()

    return sorted(copied), deleted, sorted(unchanged)


def report(copied: list[str], deleted: list[str], unchanged: list[str],
           dry_run: bool) -> None:
    print()
    if dry_run:
        print("  DRY RUN -- nothing was written; counts are what WOULD happen")
    print("  " + "count".rjust(6) + "  action")
    print(f"  {len(copied):6d}  copied to vault")
    print(f"  {len(deleted):6d}  deleted from vault")
    print(f"  {len(unchanged):6d}  unchanged")
    for label, rows in (("copy", copied), ("delete", deleted)):
        for rel in rows:
            print(f"    {label:<6} {rel}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change; write nothing")
    args = ap.parse_args(argv)

    print(f"backup_game_ref: source={SOURCE}")
    print(f"                 vault ={VAULT}")

    refusal = guard(SOURCE)
    if refusal is not None:
        print()
        print("  REFUSING TO MIRROR -- " + refusal)
        print("  Mirroring a destroyed-empty (or partial) game_ref would")
        print("  DELETE the only surviving copy of the hand-authored pass")
        print("  layers, which are not tool-regenerable. The vault was NOT")
        print("  touched.")
        print("  If game_ref is genuinely gone, RESTORE it from the vault")
        print("  first (copy the other way), then re-run this.")
        print("  If you are in a worktree, that is expected: game_ref is")
        print("  gitignored and lives only in the primary checkout.")
        return 2

    if not VAULT.exists():
        print(f"  vault does not exist yet; creating {VAULT}")
        if not args.dry_run:
            VAULT.mkdir(parents=True, exist_ok=True)

    copied, deleted, unchanged = mirror(SOURCE, VAULT, args.dry_run)
    report(copied, deleted, unchanged, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
