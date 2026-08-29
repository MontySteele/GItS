#!/usr/bin/env python3
"""Tripwire: is the pinned-assembly vault present, complete and honest?

Check-only. This tool NEVER writes -- not to the vault, not to the game. The
mirroring is `tools/backup_game_assemblies.py`'s job (EB-172 / R218 C); this is
the thing that notices you have not run it, or that what is there has rotted.

Vault: `C:\\Users\\Monty\\OneDrive\\GItS-vault\\game_assemblies`, beside
`game_ref` in the location [USER] ruled 2026-08-24.

FOUR VERDICTS, and only one of them fails:

  * **no vault at all** -- NOTE, exit 0. A fresh clone, a CI runner and every
    worktree have no OneDrive vault and no Steam install; this is
    `lint_game_ref_backup`'s convention and it is deliberate. A lint that
    failed there is a lint everybody learns to ignore.
  * **vault present and INTERNALLY consistent** -- OK. All four assemblies
    present, each matching the size and sha256 `PIN.json` records for it.
  * **vault present but INCOMPLETE OR ROTTEN** -- exit 1. A missing assembly,
    a missing or unreadable `PIN.json`, or a file whose bytes no longer match
    its recorded hash. This is the real check, and it is deliberately about
    the vault's agreement with ITSELF: a backup that cannot say what it is, or
    that says something it is not, is worse than no backup, because it looks
    like one.
  * **vault present and the LIVE GAME has moved off it** -- NOTE, exit 0,
    loudly, naming both versions. THIS IS NOT A FAILURE. It is the exact
    situation the vault exists for, and the moment its value is highest;
    failing here would train the reader to silence the tripwire precisely when
    it is doing its job. Re-pinning is a decision (a ruling moves `STATE.md`'s
    pin block), and only after that decision does re-running the mirror make
    the vault current again.

    python tools/lint_game_assemblies_backup.py

Exit 0 (clean or noted) or 1 (incomplete/rotten), nothing else.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.backup_game_assemblies import (           # noqa: E402
    ASSEMBLIES, PIN_FILE, VAULT, local_props_paths, release_info, sha256)

FIX = "run python -m tools.backup_game_assemblies"


def main() -> int:
    findings: list[str] = []
    notes: list[str] = []

    if not VAULT.is_dir():
        print(f"NOTE: no pinned-assembly vault at {VAULT} -- nothing to "
              f"check. On the primary Windows checkout, {FIX}.")
        return 0

    pin_path = VAULT / PIN_FILE
    if not pin_path.is_file():
        print(f"FINDING: {VAULT} exists but has no {PIN_FILE}. Four dlls in a "
              f"folder cannot say which build they are, so the vault is "
              f"unusable as a pin. Fix: {FIX}")
        return 1
    try:
        pin = json.loads(pin_path.read_text(encoding="utf-8"))
        recorded = pin["files"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"FINDING: {pin_path} is unreadable or malformed ({exc}). "
              f"Fix: {FIX}")
        return 1

    for name in ASSEMBLIES:
        p = VAULT / name
        if name not in recorded:
            findings.append(f"{PIN_FILE} records no entry for {name}")
            continue
        if not p.is_file():
            findings.append(f"{name} is recorded in {PIN_FILE} but missing "
                            f"from the vault")
            continue
        size = p.stat().st_size
        if size != recorded[name]["size"]:
            findings.append(f"{name}: {size} bytes on disk, "
                            f"{recorded[name]['size']} recorded")
            continue
        if sha256(p) != recorded[name]["sha256"]:
            findings.append(f"{name}: bytes do not match the recorded sha256")

    # The live-game comparison. A NOTE by construction -- see the docstring.
    data_dir, _ = local_props_paths()
    live = release_info(data_dir).get("version") if data_dir else None
    pinned = pin.get("game_version")
    if live and pinned and live != pinned:
        notes.append(
            f"the live game is {live} and the vault holds {pinned}. This is "
            f"NOT a defect -- it is what the vault is for. Build against the "
            f"vault with -p:UsePinnedAssemblies=true while the port is "
            f"written; re-run the mirror only after the pin is deliberately "
            f"MOVED (STATE.md, 'Mod build environment').")
    elif live and pinned:
        notes.append(f"vault and live game agree: {pinned}")

    for n in notes:
        print(f"NOTE: {n}")
    for f in findings:
        print(f"FINDING: {f}")
    if findings:
        print(f"{len(findings)} finding(s). Fix: {FIX}")
        return 1
    print(f"game-assemblies-backup OK: all {len(ASSEMBLIES)} assemblies "
          f"present in {VAULT} and matching {PIN_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
