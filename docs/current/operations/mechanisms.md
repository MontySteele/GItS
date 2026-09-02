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
| PreToolUse | `Bash\|PowerShell` | `tools/hooks/push_gate.py` | installs the `pre-push` hook below when it is missing, and REFUSES `git push --no-verify` — the one flag that turns that hook off. It runs no tests itself any more |
| git `pre-push` | every push, every worktree | `tools/hooks/pre_push_gate.py` | the fast lane (`-n auto --dist loadscope -m "not battery"`, 57.1 s measured 2026-09-02) + `run_lints --lane ci`, over **the tree being pushed** — git runs the hook with the working directory at that worktree's top, so nothing has to parse a command line to find it. BLOCKED on red, on timeout, or when the tree holds no `tools/run_lints.py` / `tier0/tests`. A pure ref DELETION carries no code and is allowed |
| PostToolUse | `Edit\|Write\|NotebookEdit` | `tools/hooks/game_ref_backup_reminder.py` | an edit under `game_ref/` prints the vault-backup reminder; `GITS_HOOK_RUN_BACKUP=1` runs the mirror instead |

**The push gate is a git hook now (2026-09-02).** It was a `PreToolUse` hook,
which fires BEFORE the command runs — so `edit && commit && push` on one line
was judged on the PRE-EDIT tree, and was refused over the state of a file the
same command was about to fix. `pre-push` runs when git holds the refs, in the
worktree being pushed, so the tree checked is the tree pushed. Install it with

```sh
python tools/hooks/install.py          # --check to report, never installs twice
```

which writes `<git-common-dir>/hooks/pre-push` — **the shared one, so a single
run covers every existing and future worktree of this clone.** A fresh clone
owes exactly that one command (the `PreToolUse` shim also runs it on the first
push of a session, so a session that forgets still ends up gated). A worktree
cut from a commit older than `tools/hooks/pre_push_gate.py` is NOT waved
through: the shim falls back to the main worktree's copy, and failing that runs
the same two checks inline.

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
