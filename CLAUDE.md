# CLAUDE.md — Teyvat Spire

Task-routed context. This file and `docs/current/STATE.md` are the only
always-read docs. Everything else loads on demand, chosen by the task in front
of you, so a fresh session does not bulk-load the repo.

## Read order

- **Always:** this file, then `docs/current/STATE.md` (what ships and what is
  next).
- **On demand, by task:**
  - governing constraints → `docs/current/LAW.md`
  - the yes/no checks a kit sheet is read against → `docs/current/kit-checklist.md`
  - [USER]'s open picks → `docs/current/QUEUE.md`
  - the engineering to-do list → `docs/current/BACKLOG.md`
  - measurement law (Balance stage only) → `docs/current/EXPERIMENTS.md`
  - build / test / sim / codegen / art / seats / worktrees →
    `docs/current/OPERATIONS.md`, a 75-line index into
    `docs/current/operations/`; open the one file the task names
  - a kit's design → its brief in `review/active/` (named in `STATE.md`)
  - an old R number → `docs/current/RULINGS.md` (frozen index, R1 to R276)
  - stamp history → `docs/current/STAMPS.md`
  - the **one** YAML sheet the task touches. Never bulk-load all YAML.
- **Reference, open only when the task reaches it:** `docs/current/atlas/`,
  `dossiers/`, `research/`, `calibration/`, `characters/`, `art/`,
  `rationale/`, `roster/`.
- **Never preload** git history or `review/`.

## History retrieval (works on a shallow clone)

Closed work and retired prose live in git. A citation names a tag or a commit:

```
git fetch --depth=1 origin tag pre-simplification-2026-08-06   # or: origin <commit>
git show <tag-or-commit>:<path>
```

## Norms

- **A kit moves Paper → Prototype → Balance.** Paper is a brief and sheet
  drafts, ruled on taste. Prototype is a `+proto` build graded on fun by
  [USER]'s play and by seat rounds. Balance is the shipped sheet.
  **Measurement law (`EXPERIMENTS.md`: pre-registration, blind grading,
  stamps) binds only at Balance.** Procedure and each kit's finish line:
  `docs/current/operations/stage-gate.md`.
- **Starter basics are never changed.** A change to a character's starter is
  a pick for [USER].
- **[USER] plays when a rule changes, never when a card does,** and at a kit's
  finish line. **Seat rounds run only on a rule change or a new card batch:
  two seats, a one-page record (what played well, what did not, what to
  change), raw transcripts gitignored.**
- **Claude decides and ships everything except a design direction, eyes-on
  taste, money and one-way doors, which come to [USER] as a numbered pick list
  with a marked default** (in `QUEUE.md` until ruled). Hygiene fixes need no
  authorization. A question already decided is not re-asked unless a new fact
  reopens it, stated in one line.
- **Decisions are recorded in the commit message, in [USER]'s words, and in
  the document they change,** which is edited in place. No R numbers (R276
  was the last) and no new register ids. A pick is named by its document and
  number ("Klee review, pick 2").
- **`BACKLOG.md` is a to-do list:** one line per open item, deleted in the
  commit that builds it. Existing `EB-` ids stay on their lines; new items get
  no id. Closed items leave HEAD; git keeps them.
- **Anything [USER] reads is plain English, about two pages,** every claim
  checkable against a named file or number, ending in the numbered picks.
  **Never route Claude's writing through GPT to summarise it;** GPT reviews
  designs and playtests only.
- **Model routing.** Design work (briefs, card design, loops and archetypes,
  any taste judgement) is the main Claude session's (Fable or Opus 5.5) and
  is never delegated. Subagents do coding, builds and tests and author no card
  designs. Sonnet does simple exploratory work such as assembling a packet or a
  census from files named in advance. Haiku does single-value lookups.
- **One worktree per workstream, sibling directories only.** Never link a
  gitignored asset directory into a worktree
  (`docs/current/operations/worktrees.md`). Pushes to `main` and force pushes
  are refused; work lands through a PR.
- **Claude merges every PR that asks nothing of [USER]** once CI is green
  (`gh pr merge --merge`) and says so in the turn. A PR is [USER]'s only when
  it carries an open pick, amends `LAW.md` or `EXPERIMENTS.md` text, or moves
  a shipped-sheet number or balance constant.

Non-Claude agents: `AGENTS.md` routes them here. These norms are canonical in
this file only.
