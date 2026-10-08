## Codegen — the kits' cards

One character-aware generator (`tools/gen_klee_cards.py`: the profiles, the
body and upgrade emitters) builds the C# card classes, and
`tools/gen_prototype_cards.py` drives it over `docs/prototype-surface.yaml`,
the current kits' one sheet, into `klee-mod/KleeCode/Cards/Prototype/Generated/`
with its `manifest.json`. The shipped roster generator, its sheets and its
output are deleted (legacy cleanup stages 5 and 6, 2026-10-01).

```sh
.venv/Scripts/python.exe tools/gen_prototype_cards.py           # generate
.venv/Scripts/python.exe tools/gen_prototype_cards.py --check   # verify committed output, no write
```

The generator rejects unknown card-level fields as well as unknown effects.
Partial upgrades are forbidden — a row gets its complete upgrade (`upgrade:` on
the row, or the Prototype-stage default), or says why not with `no_upgrade:`
(`operations/prototype.md`). Depth: `docs/current/atlas/klee-mod-cards.md`.

**One shipped leftover stays in the generated cards**, because removing it
changes the emitted C# of current rows: companion and Furina damage and Block
still route through `SpotlightSystem`'s print fold, the identity since stage
5 (a `BACKLOG.md` line). The other, each file's header naming a deleted
`docs/<character>-upgrades.yaml`, now names the row's `upgrade:` (text pass
2026-10-08; a comment, no emitted behaviour).

- **Cost lines are DERIVED from the printed spend, at TWO levels** (`EB-182`).
  A top-level `spend_spark` / `spend_charge` is the CARD's price and makes it
  unplayable below the bank (`combat.spark_cost` / `charge_cost` →
  `card_playable`; C# an `IsPlayable` override). A spend at the HEAD of a
  `choose_one` MODE is that MODE's price: the mode is not offered when the
  bank is short (`effects.mode_price` → `offered_modes` → `_chosen_mode`, the
  one seam the pilot, the falsifier and a replay all pass through; C#
  `ModalChoice.ModePrice` omits it from the choose-a-card screen, which the
  0.111.0 decompile gives no per-option disabled state to grey). The card
  stays playable while ANY mode is affordable; one with none is refused with a
  reason naming the price and the bank (`combat.modal_refusal`). A spend
  further down a mode body is a consequence, not a price, and is refused where
  it resolves as it always was.

The Teyvat frame's three codegen sections (dressed events, dressed Ancients,
creature scenes and motion) were folded into `operations/teyvat-frame.md` on
2026-10-08; that page names the commit with the full text.
