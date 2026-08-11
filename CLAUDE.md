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
  - open decisions owned by [USER] → `docs/current/QUEUE.md`
  - open engineering work → `docs/current/BACKLOG.md`
  - measurement law + active registrations → `docs/current/EXPERIMENTS.md`
  - build / test / sim / codegen / art / worktrees → `docs/current/OPERATIONS.md`
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

- **Hygiene fixes** (typos, dead references, obvious defects) are normal
  commits — no per-item authorization needed.
- **Design, behavior, taste, or money** calls go to [USER] via `QUEUE.md`.
  Don't settle them yourself.
- **Experiments** keep pre-registration and blind grading — see
  `EXPERIMENTS.md`. No looking at results before the grade is in.
- **Audit findings triage three ways:** confirmed defect → `BACKLOG.md`;
  design / taste / behavior call → `QUEUE.md`; false positive or
  non-actionable → nowhere permanent. Raw audit output is PR text or a temp
  artifact, never committed prose.
- **Closed items leave HEAD in the same commit that closes them (R178).**
  Exit is part of close, never a later sweep — "close now, clean later"
  is how cleanup sweeps become necessary. No strikethroughs, no supersession
  banners — edit in place. [USER]'s verbatim words belong in the commit
  message, not a doc. Every file under `review/active/` carries a
  `lifecycle / owner / exit_when` block; when its owning row closes, the
  packet leaves HEAD in that same commit (`tools/lint_docs_lifecycle.py`
  enforces both). The one exception is existing LAW, not a carve-out: a published
  measurement record stands as published, struck rather than rewritten
  (R101b).
- **One worktree per workstream, sibling directories only.** Never link a
  gitignored asset directory into a worktree (`OPERATIONS.md` has the rule and
  the reason).

Non-Claude agents: `AGENTS.md` routes them here. These norms are canonical in
this file only — don't restate them elsewhere.
