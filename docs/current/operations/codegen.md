## Codegen — roster cards

One character-aware generator emits the C# card classes from the canonical
YAML sheets. Klee is the compatibility baseline; Furina and Kokomi are the
other profiles.

```sh
.venv/bin/python tools/gen_roster_cards.py           # generate all profiles
.venv/bin/python tools/gen_roster_cards.py --check    # verify committed output, no write
```

The generator rejects unknown card-level fields as well as unknown effects
(load-bearing: `encore_cost` changes playability without being an effect).
Partial upgrades are forbidden — a card gets its complete ruled upgrade or lists
under `upgrades.no_upgrade_path`. Depth: `docs/current/atlas/klee-mod-cards.md`.

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
