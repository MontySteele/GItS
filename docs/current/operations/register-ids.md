# Register ids (frozen 2026-09-23)

No new ids are minted. The process trim of 2026-09-23 (the last ruling, R276,
`review/ruled/process-review-2026-09-23.md`) retired the EB/M id machinery:

- `BACKLOG.md` is a plain to-do list. An existing item keeps its `EB-` id so
  old citations still resolve; a new item is a plain line with no id, and a
  built item is deleted in the commit that builds it.
- `QUEUE.md` holds [USER]'s open picks, named by the document and pick number
  ("Klee review, pick 2").
- The id lint (`tools/lint_register_ids.py`), its hand-kept `RETIRED` list,
  the minting tool (`tools/mint_row.py`) and the row reader (`tools/row.py`)
  are gone.

The mint notes and retirement notes that used to fill this page (a per-id
ledger of every EB number, 1,744 lines) are in git:

```
git show 2b73880a:docs/current/operations/register-ids.md
```

A closed EB row's text is in the commit that closed it (`git log -S'EB-<n>'`),
or in the BACKLOG copy at `2b73880a` or at tag `backlog-archive-2026-09-08`.
