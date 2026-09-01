## Worktrees — one working directory per workstream

**The procedure is the `worktree` skill** — sibling-directory add, the
never-link-a-gitignored-asset-tree rule, `python -m tools.purge_worktree`
instead of `git worktree remove` (which the deny hook refuses), and prune.
Sessions never share a working directory; collisions happen *before* commit,
where CI cannot look. Rationale and incident history:
`docs/current/rationale/`.
