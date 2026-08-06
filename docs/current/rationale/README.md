# `docs/pending/` — prepared, awaiting [USER]

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Everything in this directory was **Track G of the Serenitea Sweep**: work
prepared in full and deliberately **not landed**, because it needed a
countersign or a ruling.

**All four were ruled on 2026-07-27 and landed in Serenitea Sweep II.** What
remains here is the *argument* behind two of them, kept because the reasons a
thing was built (and the reasons five neighbouring things were not) outlive the
decision to build it.

| File | What it is | Status |
|---|---|---|
| `serenitea-g3-ci-proposal.md` | G3: the CI argument, three jobs, and the recorded NOT-doing list | **ADOPTED** (B1). Workflow now at `.github/workflows/repo.yml`. Retained as the standing argument — read it before adding a job. |
| `serenitea-g4-session-isolation.md` | G4: worktree-per-session policy | **ADOPTED** (B2). Operating doc at `docs/worktree-workflow.md`. Retained as the evidence and reasoning behind the policy. |

Landed and removed from this directory:

- `serenitea-g3-ci.yml` → `.github/workflows/repo.yml` (B1, all three jobs).
- `serenitea-g1-sheet-comments.patch` → applied (B3), and **deleted rather than
  archived**, because it no longer describes what landed. Five of its six files
  applied unchanged; the `kokomi-cards.yaml` hunks were regenerated against
  post-merge `main` after the Neap Tide merge rewrote that sheet. Applying the
  prepared version would have certified a stale number as intentional — see the
  B3 note in the sprint log. Git history holds the original.

## What G1/G2 actually was, kept because the shape matters

The audit called its 35 findings "real drift the gate's scope hid". On
inspection it was **34 comments legitimately citing numbers that are not the
row's** — sibling cards, superseded values, measurement brackets, worked
arithmetic, engine constants, and two *sheet line numbers* — plus **exactly one
real drift** (`depths_judgment` said "8 + 2 per exhausted card" against
`base: 10`). So it was per-line markers and one number correction, not 35
corrections.

Per-line `(lint-ok: <reason>)` reasons rather than a blanket exemption, so a
reviewer can tell "cites a sibling card" from "cites a number this row no
longer has". A sheet-wide suppression would switch off the drift class the lint
exists for. Furina's sheet was already clean because it already carried those
markers; the other five had never been through the pass.

**That reasoning is why B3 could not just `git apply`.** The Neap Tide merge
landed R77 (`surging_shoal` 7 → 6) and rewrote the rows around it, and one
prepared marker would have stamped `(lint-ok: sibling card's number)` onto a
line citing the sibling's *old* number. A marker asserts "this number is
correct and belongs to another row" — applying it to a stale number is worse
than no marker at all, because it certifies the staleness. Regenerating cost
ten minutes and turned up one real correction the prepared patch could not have
known about.

Verification today: `python -m pytest tier0/tests/test_sheet_lints.py -q` —
11 passed, all six sheets CLEAN.
