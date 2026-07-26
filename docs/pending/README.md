# `docs/pending/` — prepared, awaiting [USER]

Everything in this directory is **Track G of the Serenitea Sweep**: work that
was prepared in full and deliberately **not landed**, because it needs a
countersign or a ruling.

Nothing here is applied to the tree. The suite, the lints and `validate.ps1`
are all green *without* any of it.

| File | What it is | What it needs |
|---|---|---|
| `serenitea-g1-sheet-comments.patch` | G1 + G2: the sheet-comment pass over five sheets, plus the `lint_sheet_comments` fan-out from one sheet to six | **Countersign.** Sheets are ratified artifacts. |
| `serenitea-g3-ci-proposal.md` | G3: the CI argument, three jobs, and the recorded NOT-doing list | **Ruling.** |
| `serenitea-g3-ci.yml` | G3: the drafted workflow. Not in `.github/workflows/`, because putting it there is what adopting it means | Move it if adopted. |
| `serenitea-g4-session-isolation.md` | G4: worktree-per-session policy | **Process ruling** — [USER]'s machine, [USER]'s workflow. |

## Applying G1/G2

```
git apply docs/pending/serenitea-g1-sheet-comments.patch
python -m pytest tier0/tests/test_sheet_lints.py -q      # 10 passed
```

It was applied, verified green (all six sheets CLEAN, 10 tests), and reverted.
The patch is that exact state.

**Read this before countersigning it:** the audit calls the 35 findings "real
drift the gate's scope hid". On inspection it is **34 comments legitimately
citing numbers that are not the row's** — sibling cards, superseded values,
measurement brackets, worked arithmetic, engine constants, and two *sheet line
numbers* — plus **exactly one real drift** (`depths_judgment` says "8 + 2 per
exhausted card" against `base: 10`). So the patch is 29 per-line
`(lint-ok: <reason>)` markers and one number correction, not 35 corrections.

Furina's sheet is the one that was already clean, because it already carries
those markers; the other five had never been through the pass. Per-line reasons
rather than a blanket exemption, so a reviewer can tell "cites a sibling card"
from "cites a number this row no longer has" — a sheet-wide suppression would
switch off the drift class the lint exists for.
