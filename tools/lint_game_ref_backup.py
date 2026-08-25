#!/usr/bin/env python3
"""Tripwire: is the OneDrive vault a current mirror of local `game_ref/`?

Check-only. This tool NEVER writes -- not to the vault, not to `game_ref/`.
The mirroring is `tools/backup_game_ref.py`'s job; this is the thing that
notices you have not run it. Exit 0 (clean) or 1 (stale), nothing else.

Vault: `C:\\Users\\Monty\\OneDrive\\GItS-vault\\game_ref`, ruled by [USER]
2026-08-24 ("Agreed on the backup in OneDrive").

Three verdicts, keyed on what the LOCAL `game_ref/` is:

  * **absent, or present and empty** -- NOTE, exit 0. This is validate.ps1's
    S7 convention and it is deliberate: a fresh clone, a CI runner and every
    worktree have no `game_ref/` at all (it is gitignored, decompile-derived),
    and a lint that failed there would be a lint everybody learns to ignore.
    Nothing local means nothing to be stale about.
  * **present but under the backup tool's ten-file floor** -- NOTE, exit 0,
    loudly. Incompleteness is real and it is S7's finding, not this one:
    `validate.ps1` fails on a partial `game_ref/` and names the missing files.
    Failing here too would give one defect two owners, and the fix line this
    lint prints could not be applied anyway -- `backup_game_ref` REFUSES a
    short source by design, so telling you to run it would be telling you to
    run something that exits 2. The vault holding an older, complete
    generation while local is partial is the correct state, not a defect.
  * **present with ten or more files** -- the real check. The vault must
    exist, must contain every source file, and no source file may be larger
    or smaller than its vault copy, or newer than it by more than the
    filesystem skew tolerance. Otherwise: exit 1 with the one-line fix.

Vault-only files are NOTES, never failures. They are usually a prior
generation's outputs, and deleting them is `backup_game_ref`'s job -- a
check-only tool that made a file's continued existence a build failure would
be pushing someone to `rm` inside the vault by hand, which is the class of
action this whole discipline exists to prevent.

    python tools/lint_game_ref_backup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.backup_game_ref import (              # noqa: E402
    MIN_SOURCE_FILES, SKEW_SECONDS, SOURCE, VAULT, relative_files)

FIX = "run python -m tools.backup_game_ref"


def check() -> tuple[list[str], list[str]]:
    """Return (failures, notes). Empty failures means exit 0."""
    failures: list[str] = []
    notes: list[str] = []

    src_files = relative_files(SOURCE)
    if not src_files:
        why = ("absent" if not SOURCE.is_dir() else "present but empty")
        notes.append(f"local game_ref is {why} ({SOURCE}) -- fresh-clone "
                     f"convention (validate.ps1 S7): nothing to back up")
        return failures, notes

    if len(src_files) < MIN_SOURCE_FILES:
        notes.append(
            f"local game_ref holds {len(src_files)} file(s), under the "
            f"{MIN_SOURCE_FILES}-file floor -- backup_game_ref will refuse "
            f"it, and validate.ps1 S7 owns the incompleteness finding. The "
            f"vault is deliberately NOT refreshed from a partial tree.")
        return failures, notes

    if not VAULT.is_dir():
        failures.append(f"vault directory does not exist: {VAULT}")
        return failures, notes
    vault_files = relative_files(VAULT)

    for rel, src in src_files.items():
        dst = vault_files.get(rel)
        if dst is None:
            failures.append(f"missing from vault: {rel}")
            continue
        s, d = src.stat(), dst.stat()
        if s.st_size != d.st_size:
            failures.append(f"size differs: {rel} "
                            f"(local {s.st_size}, vault {d.st_size})")
        elif s.st_mtime > d.st_mtime + SKEW_SECONDS:
            failures.append(f"local is newer: {rel} "
                            f"(by {s.st_mtime - d.st_mtime:.0f}s)")

    for rel in sorted(set(vault_files) - set(src_files)):
        notes.append(f"vault-only file (not a failure): {rel}")

    return failures, notes


def main() -> int:
    print(f"lint_game_ref_backup: source={SOURCE}")
    print(f"                      vault ={VAULT}")
    failures, notes = check()
    for n in notes:
        print(f"  NOTE  {n}")
    for f in failures:
        print(f"  FAIL  {f}")
    if failures:
        print(f"\n{len(failures)} vault staleness finding(s). Fix: {FIX}")
        return 1
    print("\nvault is a current mirror of local game_ref (or there is nothing "
          "local to mirror)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
