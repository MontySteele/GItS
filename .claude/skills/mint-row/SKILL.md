---
name: mint-row
description: Mint a BACKLOG or QUEUE row - the derived id, the pipe syntax, the character gate and both register lints - or read one row out of a register without loading the whole file. Use before writing any register row by hand.
---

# mint-row — one row, minted or read

## Read one row
```sh
python tools/row.py EB-311            # the four fields, unpacked
python tools/row.py EB-311 --oneline  # id, register:line, section, status
python tools/row.py M69               # QUEUE too; the register is found
```

Never grep `BACKLOG.md` for one row.

## Mint one row

```sh
python tools/mint_row.py BACKLOG tools --scope "..." --next-action "..." \
  --gate "none." --acceptance "..." --provenance "R240"      # dry run
python tools/mint_row.py BACKLOG tools ... --write     # insert + run the lints
python tools/mint_row.py QUEUE 5 --decision "**CHOOSE** (1) x or (2) y" \
  --status "OPEN -- gated on the round" --write
```

The section is a unique prefix (`tools`, `5`). The id is **derived**, so
**nothing in `lint_register_ids.py` is edited when you mint**. Quote the printed
id in your commit message.

## The rules the tool cannot keep for you

- **BACKLOG rows are four things** — scope / next action / gate / acceptance,
  all required, ≤600 chars. QUEUE rows carry a human-only ask verb, a numbered
  pick list (or `eyes-on`) and a gated status, ≤500 chars.
- **Mint nothing you were not asked for.** Findings triage three ways:
  confirmed defect → BACKLOG, an A/B/C call → QUEUE, false positive → nowhere.
- **Closing a row is the other half**: delete it AND add its number to `RETIRED`
  in the lint, same commit, with its line in `operations/register-ids.md`.
