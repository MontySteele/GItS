## Worktrees — one working directory per workstream

**The procedure is the `worktree` skill** — sibling-directory add, the
never-link-a-gitignored-asset-tree rule, `python -m tools.purge_worktree`
instead of `git worktree remove` (which the deny hook refuses), and prune.
Sessions never share a working directory; collisions happen *before* commit,
where CI cannot look. Rationale and incident history:
`docs/current/rationale/`.

### While seat lanes are live

A new worktree is allowed while a seat lane runs: `tools/agent_worktree.py`
prints one line naming the live lanes and goes on (`--allow-live-lane` is
accepted and does nothing). A sibling directory touches neither the install
nor the lane. What changes the instrument under a running round is a deploy,
because one install serves every lane, and a pull in the main checkout. So
while a lane is up, do not deploy (`tools/deploy_round.py`, `deploy.ps1` and
`deploy_proto.ps1` refuse while any game process runs) and do not pull in the
main checkout. Embark a seat from the main checkout only: a lane's embark
records live in that checkout's `understudy/logs/`, and an embark from a
worktree cannot see them.

### Two things a new worktree used to owe by hand

**`local.props` is machine state, not workstream state.** It is gitignored (it
names this machine's Steam install), so every new worktree began unable to
build until somebody copied it across. The build now falls back to a
machine-level copy:

```
%LOCALAPPDATA%\gits\local.props        # once per machine; every worktree reads it
```

Copy `klee-mod/local.props.example` there and edit it, and no worktree needs
one again. A worktree's own `klee-mod/local.props` still WINS where it exists,
so a per-tree override stays possible; `$(GitsLocalProps)` — a property or an
environment variable — moves the fallback somewhere else.
`klee-mod/Directory.Build.props` is where this is decided.

**The git hooks install once per clone, not per worktree.**
`python tools/hooks/install.py` writes `<git-common-dir>/hooks/pre-push`, and
every linked worktree shares that directory — so one run covers the worktrees
you have and every one you add later. `--check` reports without installing.

### Line endings

`.gitattributes` asks for LF in the working tree (`* text=auto eol=lf`). A
checkout made before that file existed still holds CRLF, and the first `git
add` of one of those files prints "CRLF will be replaced by LF". Refresh the
working tree once — it changes no blob, no commit and no file content:

```sh
git rm --cached -r -q . && git reset --hard
```

`git checkout-index -f -a` looks gentler and is not enough: measured
2026-09-02, it rewrote one file out of 2694 and left every entry whose cached
stat still matched the index untouched.
