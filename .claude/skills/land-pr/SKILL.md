---
name: land-pr
description: Land a plumbing PR - check the CI runs, merge with --merge, purge the branch's worktree, fast-forward the main checkout, and handle the untracked-file trap that blocks the pull. Use only for a PR that is plumbing by CLAUDE.md's definition.
---

# land-pr — check, merge, purge, fast-forward

```sh
python tools/land_pr.py <n> --dry-run     # the decision, touching nothing
python tools/land_pr.py <n>               # do it
python tools/land_pr.py <n> --no-purge    # keep the worktree
```

Three lines back: what merged, what happened to the worktree, and where `main`
now is.

## Only for plumbing

A PR is [USER]'s only when it carries an open A/B/C pick, amends `LAW.md` or
`EXPERIMENTS.md` text, or moves a shipped-sheet number or balance constant
(R259). Everything else is plumbing, round packets with no pick and built rows
included, and Claude lands it on green CI. That judgement is yours, not the
tool's; a [USER] PR is left open and said so.

## What it refuses, and why each refusal is real

- **A check that is not green** (`pending` included) — named, with its
  conclusion.
- **A PR that is not `MERGEABLE`** — rebase or resolve first.
- **An untracked file in the main checkout that DIFFERS from the incoming
  version.** This is the trap: a sitting writes a file in the main checkout, the
  worktree commits it, and `git pull` then refuses to overwrite it. Byte-
  identical copies are deleted before the pull (nothing is lost — the same bytes
  arrive with it). A differing copy STOPS the land and is named, because that is
  an unsaved change and no tool chooses which copy survives.

The worktree is retired with `python -m tools.purge_worktree`, never
`git worktree remove` — that deletes gitignored content out of a clean tree, and
it took both `game_ref/` backups doing it (`EB-128`).
