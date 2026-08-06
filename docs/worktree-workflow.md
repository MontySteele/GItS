# Worktree workflow — one working directory per workstream

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

**Status: ADOPTED 2026-07-27** (Serenitea Sweep II, B2). Ruling recorded
against G4; the argument and the incident evidence are in
`docs/pending/serenitea-g4-session-isolation.md`.

This is the operating doc. It says what to do. The *why* is one paragraph:

> Two Opus sessions sharing one working directory collide **before commit**,
> which is the one place CI cannot look. It happened during Sweep I: between
> two commits, a second workstream wrote `test_card_scope.py` and edited
> `KokomiConscript.cs` into the shared tree, and a routine `git add -A` swept
> both into somebody else's commit. The suite did not catch it — the other
> session's work was correct and green, which is exactly why it was invisible.
> CI could not have caught it. A human reading one unexpected filename in a
> `--stat` caught it.

---

## The five rules

### 1. One worktree per workstream

Sessions never share a working directory.

```
git worktree add ../GItS-<workstream> -b <branch>
```

The main checkout at `GItS/` stays on `main` and is the **art-bearing tree**:
it is where `build_pck`, `deploy` and the art passes happen. Worktrees are for
code, sims, sheets and docs.

### 2. Branch naming: `<sprint-or-topic>-<short-slug>`

Lowercase, hyphens, no slashes. Slashes work in git but make the sibling
directory names ambiguous when a worktree is named after its branch.

```
serenitea-sweep-ii          kokomi-pool-rework
neap-tide-v2.1              axis-validity-session
```

One branch per worktree, one worktree per branch. If you need the same branch
in two places, you wanted two branches.

### 3. Merges to `main` go through a PR, with `repo` as a required check

`.github/workflows/repo.yml` (adopted as B1) runs three jobs: the bare-clone
pytest suite, the softlock lints, and the ledger duplicate check. Set all three
as required checks on `main` in GitHub branch protection.

This is the one place the two policies genuinely compose: CI alone catches a
bad merge *after* `main` moves; CI as a required check catches it before.

> **Not yet done.** Branch protection is a GitHub setting, not a file in this
> repo. It is [USER]'s to click, and until it is clicked rule 3 is a
> convention rather than a gate.

### 4. Stage explicitly. Never `git add -A`

```
git add tier0/harness/runner.py tier0/tests/test_stale_band_annotations.py   # yes
git add -A                                                                   # no
git commit -a                                                                # no
```

`git add -A` is what turned the Sweep-I collision from "two sessions edited the
same tree" into "one session committed the other's work". Rule 1 makes that
collision rare; rule 4 makes it survivable when rule 1 is skipped — and rule 1
gets skipped, because the art-bearing tree is genuinely more convenient for
some work.

Read the `--stat` before you push. One unexpected filename is the whole signal.

### 5. NEVER link a gitignored asset directory into a worktree

No junctions, no symlinks, no `mklink /J`, for any of:

```
game_ref/          ImageGen/images/     art/raw/     art/candidates/
```

**This rule has cost non-regenerable files twice.** A `git worktree remove`
follows a junction into the real directory and deletes what it finds there. It
destroyed `game_ref/` on 2026-07-25, and `game_ref/` contains four files that
cannot be regenerated.

A worktree simply **lacks art, and that is fine.** Sweep-I Track A made the
suite green on a bare tree — that was the whole point of it, and it is what
made this policy adoptable. The artifact-gated tests skip by design.

If a task genuinely needs art, do it in the main checkout. That is not a
limitation; the things a worktree cannot do without art (`build_pck`, `deploy`,
art passes) are the things that have to happen on the main checkout anyway.

---

## The transition, and why it is the risky moment

Creating worktrees is safe. Creating them **while sessions hold uncommitted
work in the shared tree** is not: the work belongs to whatever branch the
shared tree happens to be on, and moving it afterwards is guesswork about who
wrote what.

Do it once, quietly, in this order:

1. **Close every session.** Not "pause" — closed. A session that wakes up mid
   transition writes into a tree that has moved under it.
2. **Commit or stash all in-flight work to its owning branch.** If you cannot
   tell which branch owns a change, that is the collision this policy exists
   to prevent, and it is cheaper to resolve now than after the split.
3. **Verify the tree is clean:** `git status --porcelain` prints nothing.
4. **Only then** create the worktrees.

```
git worktree list                      # what exists now
git worktree add ../GItS-<name> -b <branch>
git worktree remove ../GItS-<name>     # when the workstream lands
git worktree prune                     # after deleting a directory by hand
```

Before any `git worktree remove`, confirm rule 5 is intact for that tree:

```
# Windows: junctions show as <JUNCTION> in a bare listing
cmd //c dir /AL ..\GItS-<name>
```

Nothing there means nothing to follow, and the remove is safe.
