## game_ref backup — the OneDrive vault

`game_ref/` is gitignored, decompile-derived, and half of it is thirteen
hand-authored pass layers that no tool can regenerate. It has been destroyed
four times. RULED [USER] 2026-08-24: *"Agreed on the backup in OneDrive"* — the
durable copy lives at

```
C:\Users\Monty\OneDrive\GItS-vault\game_ref
```

hard-coded in `tools/backup_game_ref.py` (a configurable backup root is one
that can be pointed somewhere temporary and quietly stop being a backup).

```sh
python -m tools.backup_game_ref             # mirror local -> vault
python -m tools.backup_game_ref --dry-run   # what it would do
python tools/lint_game_ref_backup.py        # staleness tripwire, never writes
```

**Run the backup after ANY restore, extraction, or hand edit of `game_ref/`** —
after `tools.extract_base_game_pool` + `tools.build_official_sheet`, after
restoring pass layers from anywhere, after editing a `*_char_facts.yaml` by
hand. Two mechanisms carry this now: `tools/hooks/game_ref_backup_reminder.py`
fires on any Edit/Write under `game_ref/` (git cannot — the tree is ignored,
so `git status` is clean by construction), and the staleness tripwire is in
`run_lints.py`'s **local** lane, so a normal `python tools/run_lints.py` says
when the vault has fallen behind.

**The guard is the tool's reason to exist.** `backup_game_ref` REFUSES (exit 2,
loud, vault untouched) when local `game_ref/` is missing or holds fewer than ten
files — every destruction so far left the directory *present and empty* with
`git status` clean, and a mirror run "to be safe" in that state would take the
last copy with it. **If local `game_ref/` is empty, the vault is the source —
copy the other way.**

The lint's three verdicts — absent/empty, under ten files, ten or more — and
why each is a NOTE or a failure are in `lint_game_ref_backup.py`'s own
docstring, where they cannot drift from the code that implements them.

**Backups never live in worktrees.** The vault is outside every checkout
because a worktree teardown deletes gitignored content; the `worktree` skill
and the deny hook carry the rest of that rule.

**A missing layer fails at the door, not mid-cell.** Asking for a `real_*` arm
without `game_ref/` raises `loader.MissingReferenceLayer` out of
`tier05.runner.resolve_plan` before any run starts, and the message names this
tool as the restore point. **Never stub, fabricate or approximate the layer to
make an anchor load** — a stubbed `real_ironclad` produces numbers that look
like floors and are not.
