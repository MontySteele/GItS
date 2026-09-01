# ancient-upgrades.yaml - comment provenance

Long comment blocks that used to sit in `docs/ancient-upgrades.yaml`. They
moved here on 2026-09-01 so an agent reading the sheet loads rows,
not prose. Blocks are verbatim and in sheet order.

A heading names the row the block was attached to. `before <id>`
means a column-0 section note that sat above that row. `header` is
the file header. Blocks of three lines or fewer stayed in the sheet.

## header

```
# Lifecycle: LIVING — expected to change; read it to work on the project.  (lint-ok)
# ANCIENT upgrade deltas (R127, EB-30m) — companion file to
# tier0/content/cards/ancients.yaml.
#
# WHY THIS IS A SEPARATE SHEET. These three cards have no row in any
# docs/<char>-cards.yaml, because their C# classes are hand-written and
# codegen must never try to emit them. Folding the deltas into a character
# upgrade sheet would put them back in front of the generator:
# `tools/gen_klee_cards.UPGRADE_SHEETS` reads exactly the three character
# files and this one is deliberately absent from it, the same arrangement
# `ref-ironclad-upgrades.yaml` already has. Registration is therefore in
# `tier0/content/upgrades.py` UPGRADE_SHEETS ONLY.
#
# THESE DELTAS ARE THE PLAYED NUMBERS, not a smithing option. The Dusty Tome
# grants the Ancient already upgraded (C# DustyTome.AfterObtained), so the
# `+` form is what a run actually holds and what
# tools/lint_handwritten_parity.py's ANCIENT_WITNESS pins. The base rows exist
# for the smith-less acquisition paths the C# headers name.
#
# Grammar authority: docs/upgrade-conventions.md. No new applier keys were
# needed — `damage`, `bomb_damage` and `power_amount` all already exist.
```
