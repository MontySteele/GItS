# G4 — Session isolation policy (PREPARED, awaiting [USER] process ruling)

**Status: DRAFTED, NOT ADOPTED.** This is about [USER]'s machine and workflow,
so the sprint only drafts it.

---

## This is not hypothetical, and it stopped being hypothetical during the sprint

The premise was: *multiple Opus workstreams share one working directory;
collisions happen pre-commit, where CI cannot see them — G3 catches wreckage,
not causes.*

**It happened while this sprint was running.** Between the Track B commit
(01:37) and the Track C commit (02:04), another workstream wrote
`tier0/tests/test_card_scope.py` and edited
`klee-mod/KleeCode/Powers/KokomiConscript.cs` into this same working directory
— a Kokomi conscript soft-lock fix from a 2026-07-26 playtest. A routine
`git add -A` swept both into the Track C commit.

Nothing was lost: the commit was split and both files were returned to the
working tree untouched. But note what did and did not catch it —

- **The suite did not catch it.** The other session's work was correct and
  green; that is precisely why it was invisible.
- **CI would not have caught it.** By the time anything reaches a runner, the
  files are already in somebody else's commit. This is the "wreckage, not
  causes" point, demonstrated.
- **A human reading the commit output caught it** — one unexpected filename in
  a `--stat`.

Two sessions were also mutating shared derived state: this sprint rebuilt
`klee.pck`, ran the codegen, and reverted a sheet mid-measurement (the D3
paired test). Any of those would have corrupted a concurrent session's
measurement without either side seeing an error.

---

## Proposal

### (a) One git worktree per active workstream, branch per workstream

Sessions never share a working directory. This is the only part that addresses
the *cause*; (b) and (c) are containment.

**Sequencing note, and it is load-bearing:** (a) is only viable **after Track A
lands**, and Track A has landed. Before it, a worktree without art was a red
suite, so worktrees were unusable in practice and sharing the art-bearing
directory was the path of least resistance. That is no longer true — see (c).

### (b) Merges to `main` go through PRs, with the G3 jobs as required checks

The merge race gets a referee instead of a convention. This is the one place
G3 and G4 genuinely compose: G3 alone catches a bad merge after the fact; G3 as
a required check on a PR catches it before `main` moves.

Depends on G3 being adopted.

### (c) Junction/symlink rule: never link gitignored asset dirs into a worktree

From the 2026-07-25 incident, in which a `git worktree remove` followed a
junction into the real directory and **destroyed `game_ref/`** — twice, across
the project's history, and four of its files are not regenerable.

The rule is now cheap to follow because **Track A made an art-less worktree a
working environment rather than a broken one**: the suite is green on a bare
tree (871 passed / 21 skipped, verified), so a worktree simply lacking art is
fine. The 21 skips are the artifact-gated set, behaving as designed.

Corollary worth stating: the things a worktree cannot do without art are
exactly the things that must happen on the main checkout anyway — `build_pck`,
`deploy`, the art passes. That is a clean split, not a limitation.

---

## What [USER] is being asked to rule

1. Adopt (a) as a working practice — one worktree per session, branch per
   session.
2. Adopt (b), which requires adopting G3 first.
3. Adopt (c) as a hard rule (it already has two incidents behind it).

If only one of these is taken, **(c) is the one with the worst downside**: it
has already cost non-regenerable files twice, and it costs nothing to follow.

If (a) is not adopted, the practical mitigation for a shared directory is
narrower and should be recorded as the fallback: **stage explicitly, never
`git add -A`** — which is what this sprint switched to for every commit after
the collision, and which is why Tracks D, E, F and G each staged a named file
list.
