#!/usr/bin/env python3
"""PostToolUse/Edit|Write: a hand edit under `game_ref/` owes the vault a backup.

Correction D. operations/game-ref-backup.md: *"Run the backup after ANY
restore, extraction, or
hand edit of `game_ref/`"*. `game_ref/` is gitignored, decompile-derived, and
half of it is thirteen hand-authored pass layers no tool can regenerate; it has
been destroyed FOUR times. `git` cannot notice a hand edit there -- the tree is
ignored, so `git status` is clean by construction and nothing downstream ever
asks. This hook is the only place in the pipeline that sees the edit happen.

WHY IT REMINDS INSTEAD OF MIRRORING, and this is the honest part. The tool
operations/game-ref-backup.md names is `python -m tools.backup_game_ref`, a full mirror of the
tree into `C:\\Users\\Monty\\OneDrive\\GItS-vault\\game_ref`. It does not
prompt -- it is safe to type unattended, and its ten-file guard is the reason
it exists -- but PostToolUse fires on EVERY Edit and Write, and a per-edit
full-tree mirror into a OneDrive-synced directory is seconds of copying and a
sync storm for a pass layer that is still being edited. Mirroring a
half-finished edit is also not obviously desirable. So the default is a
reminder on stderr, which under the hooks contract is the channel that
actually reaches Claude, and the mirror stays a deliberate act at the end of
the session.

    GITS_HOOK_RUN_BACKUP=1     # opt in: run the real mirror on every such edit

EXIT CODE. `2` on a PostToolUse hook does not undo anything -- the write has
already happened -- it is simply the documented way to put stderr in front of
Claude. The message says so in its first clause, so a reminder can never be
misread as a failed edit.

    python tools/hooks/game_ref_backup_reminder.py               # hook mode
    python tools/hooks/game_ref_backup_reminder.py --self-test   # prove it fires
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _hooklib import (ALLOW, BLOCK, REPO, edit_payload, edited_path,  # noqa: E402
                      note, read_payload, run_self_test)

WATCHED = "game_ref"
BACKUP = "python -m tools.backup_game_ref"
MIN_FILES = 10          # backup_game_ref's own refusal threshold


def under_game_ref(raw: str) -> bool:
    """True when `raw` names something inside a `game_ref/` tree.

    Compared on normalised parts rather than on the string, so a Windows path,
    a Git-Bash path and a path relative to the repo root all answer the same
    question the same way. `game_ref_backup/` and `game_reference/` are NOT
    matches -- the part has to be the directory name exactly.
    """
    if not raw:
        return False
    parts = Path(raw.replace("\\", "/")).parts
    return WATCHED in parts


def _local_file_count() -> int:
    tree = REPO / WATCHED
    if not tree.is_dir():
        return 0
    count = 0
    for _ in tree.rglob("*"):
        count += 1
        if count > MIN_FILES:
            break
    return count


def decide(payload: dict, execute: bool = True) -> int:
    path = edited_path(payload)
    if not under_game_ref(path):
        return ALLOW

    if execute and os.environ.get("GITS_HOOK_RUN_BACKUP") == "1":
        if _local_file_count() < MIN_FILES:
            note(f"REMINDER (the edit SUCCEEDED): {path} is under game_ref/, "
                 f"but this checkout holds fewer than {MIN_FILES} files there, "
                 f"so `{BACKUP}` would hit its own guard and refuse. If local "
                 f"game_ref/ is empty, THE VAULT IS THE SOURCE -- copy the "
                 f"other way.")
            return BLOCK
        proc = subprocess.run([sys.executable, "-m", "tools.backup_game_ref"],
                              cwd=REPO, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            note(f"REMINDER (the edit SUCCEEDED): the game_ref/ backup was "
                 f"attempted and FAILED, exit {proc.returncode}. "
                 f"{proc.stdout.strip()[-400:]}")
            return BLOCK
        note(f"game_ref/ mirrored to the OneDrive vault after editing {path}.")
        return ALLOW

    note(f"REMINDER (the edit SUCCEEDED -- this is not an error): {path} is "
         f"under game_ref/, which is gitignored, decompile-derived, partly "
         f"NOT tool-regenerable, and has been destroyed four times. Nothing "
         f"in git will notice this edit. Run `{BACKUP}` from the primary "
         f"checkout when the edit is finished.")
    return BLOCK


CASES = [
    (edit_payload("game_ref/klee_char_facts.yaml"), 2, "relative path"),
    (edit_payload(r"C:\Users\Monty\Documents\GitHub\GItS\game_ref\pass7\x.yaml"), 2,
     "windows absolute path"),
    (edit_payload("/c/Users/Monty/Documents/GitHub/GItS/game_ref/a.txt"), 2,
     "git-bash path"),
    (edit_payload("game_ref/deep/nested/file.json", tool="Write"), 2, "Write"),
    (edit_payload("docs/current/OPERATIONS.md"), 0, "a docs edit"),
    (edit_payload("tools/hooks/_hooklib.py"), 0, "a tools edit"),
    (edit_payload("game_ref_backup/x.yaml"), 0, "the backup dir is not game_ref"),
    (edit_payload("art/game_reference/x.png"), 0, "a similar name is not a match"),
    (edit_payload(""), 0, "no path"),
    ("not json at all", 0, "unparseable payload"),
]


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test(CASES, lambda p: decide(p, execute=False))
    return decide(read_payload())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
