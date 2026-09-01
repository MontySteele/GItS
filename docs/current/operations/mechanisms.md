## Mechanisms — what is enforced, and by what

**Correction D (2026-08-26).** Claude treats `CLAUDE.md` and this file as
CONTEXT, not as enforced configuration — the official guidance is explicit:
*to block an action regardless of what Claude decides, use a PreToolUse hook*.
A rule that lives only in prose is advice a long session can lose. Every rule
in the table below used to be a paragraph in this file and is now a hook, a
skill or a lint, and **the prose it replaced is DELETED rather than kept
beside it**: two statements of one rule is one too many, and the copy that is
not executable is the one that rots.

`.claude/settings.json` wires the hooks. Each is a small portable Python
script that reads the hook payload on stdin and exits 0 (allow) or 2 (block,
with a one-line reason shown to Claude), so it behaves the same from Git Bash
and from PowerShell.

| event | matcher | script | what it refuses / does |
|---|---|---|---|
| PreToolUse | `Bash\|PowerShell` | `tools/hooks/deny_dangerous_git.py` | `git add -A` / `.` / `--all`; `git worktree remove`; `git push` at `main` or forced; `--no-verify` on `commit` or `push` |
| PreToolUse | `Bash\|PowerShell` | `tools/hooks/push_gate.py` | a real `git push` runs the fast lane + `run_lints --lane ci` first (~21 s measured) **in the tree the push targets** — resolved from `git -C`, then the last in-line `cd`, then the payload's `cwd`, and NAMED in the note — and is BLOCKED on red, on timeout, or when that tree holds no `tools/run_lints.py` / `tier0/tests` |
| PostToolUse | `Edit\|Write\|NotebookEdit` | `tools/hooks/game_ref_backup_reminder.py` | an edit under `game_ref/` prints the vault-backup reminder; `GITS_HOOK_RUN_BACKUP=1` runs the mirror instead |

Skills (`.claude/skills/<name>/SKILL.md`) carry the procedures this file used
to narrate: **`sitting`** — a registered experiment's run, world-check to
commit; **`deploy`** — `build_pck` → `deploy` → `validate`; **`worktree`** —
add, the no-link rule, purge.

Lints, all registered in `run_lints`'s `ci` lane: `register-shape`,
`stamp-rows`, `sheet-stamp`, `experiments-active`, `hook-self-tests`. The
register/stamp lints ship **green** by carrying a curated `DEBT` set of the
rows that failed when the gate was born, so it binds from that commit forward
while the old rows stay a work list. Each lint prints its own DEBT count — the
number is not repeated here because it only shrinks: a `DEBT` entry that has
since become clean FAILS, and an emptied set makes the lint ordinary.

**What a mechanism cannot reach.** A hook sees a tool call, not an intention:
nothing here can tell that a *sitting* skipped its blind grade, that a `QUEUE`
row was answered by Claude rather than by [USER], or that a design call was
settled without being asked. Those stay norms in `CLAUDE.md`, and the lints
above gate only their SHAPE — that a row has an ask and a gate, never that the
ask was honoured.
