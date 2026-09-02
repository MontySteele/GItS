## Worktrees — one working directory per workstream

**The procedure is the `worktree` skill** — sibling-directory add, the
never-link-a-gitignored-asset-tree rule, `python -m tools.purge_worktree`
instead of `git worktree remove` (which the deny hook refuses), and prune.
Sessions never share a working directory; collisions happen *before* commit,
where CI cannot look. Rationale and incident history:
`docs/current/rationale/`.

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
