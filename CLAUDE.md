# CLAUDE.md — Teyvat Spire

Task-routed context. This file and `docs/current/STATE.md` are the only
always-read docs. Everything else loads on demand, chosen by the task in front
of you. The point of this file is to keep a fresh session from bulk-loading the
repo.

## Read order

- **Always:** this file, then `docs/current/STATE.md` — the shipped snapshot
  (roster, systems, versions, active workstreams), which links into QUEUE and
  BACKLOG.
- **On demand, by task:**
  - governing constraints → `docs/current/LAW.md`
  - the yes/no checks a kit sheet is read against → `docs/current/kit-checklist.md`
  - [USER]'s open A/B/C picks, and nothing else → `docs/current/QUEUE.md`
  - the one engineering register → `docs/current/BACKLOG.md`
  - measurement law + active registrations → `docs/current/EXPERIMENTS.md`
  - build / test / sim / codegen / art / worktrees →
    `docs/current/OPERATIONS.md`, a 71-line index into
    `docs/current/operations/`; open the one file the task names
  - a ruling cited by number → `docs/current/RULINGS.md` (generated index:
    id, date, one line, and the commit or ledger to retrieve its words from)
  - stamp history (what a past RT/D/P/C level covered) → `docs/current/STAMPS.md`
  - the **one** YAML sheet the task touches (`docs/*-cards.yaml`,
    `*-upgrades.yaml`, `*-companions.yaml`, …). Never bulk-load all YAML.
- **Reference — open only when the task reaches it, never preload:**
  `docs/current/atlas/` (per-subsystem architecture maps),
  `docs/current/dossiers/` (enemy / boss / remap), `docs/current/research/`,
  `docs/current/calibration/`, `docs/current/characters/`, `docs/current/art/`,
  `docs/current/rationale/`, `docs/current/roster/`.
- **Never preload** git history or `review/`.

## History retrieval (works on a shallow clone)

Closed work and retired prose are not in HEAD — they live in git, tagged. To
read an old path:

```
git fetch --depth=1 origin tag pre-simplification-2026-08-06
git show pre-simplification-2026-08-06:<old-path>
```

Some citations name a commit instead of the tag — that means the file's HEAD
content differed from the tag copy, so the commit is the retrieval point:

```
git fetch --depth=1 origin <commit>
git show <commit>:<path>
```

## Norms

- **A kit moves Paper → Prototype → Balance.** *Paper* is a brief and sheet
  drafts, ruled on taste. *Prototype* is a `+proto` build with the rules
  implemented, graded on fun by [USER]'s play and by seat rounds. *Balance* is
  the shipped sheet. **Measurement law (`EXPERIMENTS.md` pre-registration,
  blind grading, stamps) binds only at Balance:** a Prototype arm gets no
  slate, no countersign, no register row and no re-baseline. Stage procedure,
  files and commands: `docs/current/operations/stage-gate.md`.
- **[USER] plays when a RULE changes, never when a card does:** after a brief
  is ruled, at the first build of a kit's rules, when a loop is added or a rule
  in the brief's rule list is rewritten, and at a release candidate. Between
  those the seats (Opus, GPT, Qwen) drive every playtest round, and no work
  waits on [USER] playing.
- **Hygiene fixes** (typos, dead references, obvious defects) are normal
  commits — no per-item authorization needed.
- **The delegation ladder (R212, extended 2026-09-01) — Claude decides and
  ships, no ask:** art
  picks (apply shortlist rank 1, commit the contact sheet; `art_lint` still
  bites, [USER] vetoes on the sheet); prediction slates (DRAFTED from written
  intent, committed before any run, batch-countersigned — signed once, since a
  moved world means re-draft and disclose, never re-sign); band re-affirmation
  (defaults STANDS); window sharing when the scratch read is null (disclose
  hash + read); hygiene inside registered packets (R101b still binds inside a
  countersigned prediction block); derived-not-picked numbers (one-way error
  direction, archive scope, one constant) and provisional names proved
  cosmetic by lint (R179); and **every D / E / F pick**, meaning (D) a number
  the sim decides, (E) a process or hygiene call, (F) an item already ruled and
  re-asked. A D/E/F pick is taken at its stated default, disclosed in the slate
  as APPLIED, and never queued; [USER] vetoes.
  **Still [USER]'s, the A/B/C picks:** (A) a design direction a brief cannot
  settle, (B) eyes-on taste, (C) money, one-way doors, merging a staged balance
  lever, and LAW or measurement-law amendments.
- **An A/B/C pick returns as a NUMBERED PICK LIST with a marked default,**
  never a blank to fill.
- **A question already ruled is closed by its ruling id.** Cite the id instead
  of re-asking. A re-ask that does not state, in one line, the new fact that
  reopens it is a defect in the packet that raised it.
- **Anything [USER] reads is plain English, about two pages,** every claim
  checkable against a named file or number, no register dialect, ending in the
  numbered picks. **Never route Claude's writing through GPT to summarise it
  for [USER];** GPT reviews designs and playtests only, and a document that
  needs a summary is rewritten instead. `STATE.md` stays near 150 lines, a
  packet past 1,000 lines is split by decision, and a ruled packet leaves
  `review/active/` for `review/ruled/`, and a measurement record or
  registration for `review/records/`.
- **Model routing.** Design work (briefs, card design, loops and archetypes,
  any taste judgement) is the main Claude session's (Fable) and is never
  delegated. Opus subagents do coding, builds and tests and author no card
  designs. Sonnet does simple exploratory work such as assembling a packet or a
  census from files named in advance. Haiku does single-value lookups.
- **Two registers, and nothing else mints ids.** `BACKLOG.md` is the one
  engineering register and keeps the `EB` ids; `QUEUE.md` holds [USER]'s A/B/C
  picks only and is empty most of the time. **No new `M` ids after
  2026-09-01:** existing ones close in place, and a new pick is named by its
  packet section until it is ruled and then by its `R` number.
- **Claude merges every PR that asks nothing of [USER]** (R259, 2026-09-05).
  A PR is [USER]'s only when it carries an open A/B/C pick, amends `LAW.md`
  or `EXPERIMENTS.md` text, or moves a shipped-sheet number or balance
  constant (a staged lever is a C pick by itself). Everything else is
  plumbing: round packets with no pick, built rows, prototype rows under a
  disclosed D/E/F default, and the recording of a ruling already given. With
  CI green, Claude merges it (`gh pr merge --merge`, matching this repo's
  merge-commit history) and says so in the turn; [USER] reads packets when
  one carries a pick, and vetoes on the merged text. Main's push rule is
  unchanged.
- **Experiments** keep pre-registration and blind grading at the Balance stage
  — see `EXPERIMENTS.md`. No looking at results before the grade is in.
- **Audit findings triage three ways:** confirmed defect → `BACKLOG.md`; an
  A/B/C call → `QUEUE.md`; false positive or non-actionable → nowhere
  permanent. Raw audit output is PR text or a temp artifact, never committed
  prose.
- **Closed items leave HEAD.** No strikethroughs, no supersession banners —
  edit in place. [USER]'s verbatim words belong in the commit message, not a
  doc. The one exception is existing LAW, not a carve-out: a published
  measurement record stands as published, struck rather than rewritten
  (R101b).
- **One worktree per workstream, sibling directories only.** Never link a
  gitignored asset directory into a worktree
  (`docs/current/operations/worktrees.md` has the rule and the reason).
- **One batch per sitting** (R206, amended by R212): the sitting's decisions
  are assembled by Claude and recorded as ONE slate under ONE ruling — don't
  mint transient register rows for answers already in hand.

Non-Claude agents: `AGENTS.md` routes them here. These norms are canonical in
this file only — don't restate them elsewhere.
