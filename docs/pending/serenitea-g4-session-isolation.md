# G4 — Session isolation policy (RULED: ADOPTED 2026-07-27)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Status: ADOPTED**, Serenitea Sweep II track B2. All three parts — (a)
worktree per workstream, (b) PR-to-`main` with the `repo` workflow as a
required check, (c) the junction rule — were ruled in.

The operating doc is **`docs/worktree-workflow.md`**; that is what to follow.
This document is retained as the evidence behind it: the live collision that
made the premise concrete, and the two `game_ref/` losses behind (c). Keep it
for the incidents, not for the instructions.

One part is not fully executable from this repo: (b) needs branch protection
set on GitHub, which is a setting rather than a file. Flagged in the operating
doc as convention-until-clicked.

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

## What [USER] ruled (2026-07-27)

**(a), (b) and (c) all adopted.** See `docs/worktree-workflow.md`.

The fallback below was adopted too, and promoted from fallback to standing
rule 4: **stage explicitly, never `git add -A`**. It was proposed here as the
mitigation for *not* adopting (a), but (a) does not make it redundant — the
art-bearing main checkout is genuinely more convenient for some work, so the
shared tree will keep being used, and rule 4 is what makes that survivable.
Sweep II staged a named file list for every commit.
