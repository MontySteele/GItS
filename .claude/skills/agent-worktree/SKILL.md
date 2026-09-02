---
name: agent-worktree
description: Open a sibling worktree for one workstream and print the exact read list CLAUDE.md's read order gives that task type. Use at the start of any delegated workstream, before reading any repo file.
---

# agent-worktree — the sibling, local.props, and what to read

```sh
python tools/agent_worktree.py <name> --task build      # or packet | seat | audit
python tools/agent_worktree.py <name> --task packet --base origin/main
python tools/agent_worktree.py <name> --task audit --dry-run
```

Creates `../GItS-<name>` on a new branch from `origin/main` (fetched first),
copies `klee-mod/local.props` **from the main checkout** — a worktree has none
and half the build refuses without it — and prints the read list. Read those
files and nothing else: the read order stops a session bulk-loading the repo.

## The rules it enforces so you do not have to remember them

- **Sibling directories only**, and **never link a gitignored asset tree into
  one** (`game_ref/`, `ImageGen/images/`, `art/raw/`): a junction is followed
  and deleted by a teardown, which has destroyed `game_ref/` more than once.
- **It refuses while a seat is live in this checkout** — an
  `understudy/logs/embark-*.json` whose ledger still reads `APPLIED` on a lane
  whose port answers. Tear the lane down first
  (`python -m understudy.embark --teardown --lane N`); one install means one
  deployed build for every lane.

## In the worktree

Work only there; never run git in the main checkout and never switch its
branch. Stage by name — `git add -A` is denied by the hook layer. Deploys and
pck builds are refused from a worktree by
`tools/hooks/deny_deploy_outside_main.py`; the one legal build here is
`klee-mod\build\deploy_bridge.ps1 -BuildOnly`.

Retire it with `python -m tools.purge_worktree ../GItS-<name>`, never
`git worktree remove`.
