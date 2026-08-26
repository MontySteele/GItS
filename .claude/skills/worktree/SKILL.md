---
name: worktree
description: Create, work in, and retire a git worktree for one workstream - sibling directories only, never link a gitignored asset tree, and purge_worktree instead of git worktree remove. Use before adding or removing any worktree.
---

# Worktrees — one working directory per workstream

Sessions never share a working directory; collisions happen *before* commit,
where CI cannot look.

1. **Add it as a SIBLING of the repo, one branch per worktree**, lowercase-
   hyphen branch names, no slashes:

   ```sh
   git worktree add ../GItS-<workstream> -b <sprint-or-topic>-<short-slug>
   ```

2. **NEVER link a gitignored asset directory into it** — `game_ref/`,
   `ImageGen/images/`, `art/raw/`, `art/candidates/`. A junction or symlink is
   followed and deleted by a worktree teardown; this has destroyed
   non-regenerable `game_ref/` files. A worktree simply lacks art, and that is
   fine: `build_pck`, `deploy` and art passes happen on the main checkout.

3. **Never park the only copy of anything in a worktree.** Backups live in the
   OneDrive vault, outside every checkout, for exactly this reason.

4. **Stage explicitly.** `git add -A` / `git add .` are refused by
   `tools/hooks/deny_dangerous_git.py`. Read the `--stat` before you push —
   one unexpected filename is the whole signal.

5. **Retire it with `purge_worktree`, never with `git worktree remove`.**
   `git worktree remove` deletes GITIGNORED content out of a CLEAN worktree —
   `git status` reads clean because ignored files are ignored — and on
   2026-08-24 a routine purge took both surviving `game_ref/` backups that way
   (`EB-128`). The hook refuses the raw command; this is the door:

   ```sh
   python -m tools.purge_worktree ../GItS-<name> --dry-run   # see the list
   python -m tools.purge_worktree ../GItS-<name>             # check, then remove
   git worktree prune
   ```

   It runs `git -C <worktree> status --ignored --porcelain` and REFUSES
   (exit 2, naming what it found) when the worktree holds gitignored data it
   was not told to expect. Build outputs, caches and `local.props` are on its
   allowlist; `game_ref/` and the art trees deliberately are not.
   `--acknowledge` is the flag you type **after reading that list**, never one
   you set in advance.

6. **A phase's content does not merge to `main` until the prior phase's
   required read is complete (R206).** Build it, test it, push the branch —
   merging is the act that is sequenced, not the work. A branch waiting on a
   read is INERT, not blocked, and merging one IS the pull. Pushes to `main`
   and forced pushes are refused by the hook; the PR merge is [USER]'s.
