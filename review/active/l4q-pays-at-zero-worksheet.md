# L4q worksheet — `pays_at_zero` tag semantics (prepared 2026-08-07)

**The decision:** what does "pays at zero" mean for a damage card that reads
a meter? Two candidate readings, one QUEUE row (`L4q`), your call.

## The two readings

- **Literal (shipped):** `role_tempo.scan_row` calls a line frontload only
  when it carries a literal positive `amount:`. A card written as
  `amount_formula: {base: 5, per: 1, count: exhaust_pile}` reads as
  `scaling` only — the base is invisible to the scanner.
- **Printed floor (proposed):** `effect_walk.printed_floor` — `amount: 5`
  and `amount_formula: {base: 5, ...}` are the same promise to the player
  (five, before the meter says anything), so both are frontload. A formula
  with no base, or an explicit `amount: 0` + bonus, still pays nothing at
  zero and stays scaling-only.

## What the worksheet establishes (measured, not argued)

1. **The pin's factual premise is stale.** The guarding test
   (`test_role_tempo_coverage.py:259`) says "`pearl_barrage` deals only `N
   per exhausted card`, so at an empty pile it deals nothing." The shipped
   sheet says otherwise: `5 + 1 per exhausted card`, and its own comment
   records the v0.3 base raise (3 → 5) as "the floor must be playable
   before the pile exists." The card was deliberately given a floor after
   the pin's sentence was written. Same for `undertow` (4 +) and
   `depths_judgment` (10 +).
2. **The "19 cards of tagging inverted" warning does not materialize.** The
   full `classify_pool` pipeline (scan + meter-payoff derivation +
   inheritance) was run under both readings across all three sheets. The
   complete diff is **three cards**, each **gaining** `frontload`, nothing
   losing anything, no inheritance ripple:

   | card | solve (shipped) | solve (printed-floor) |
   |---|---|---|
   | kokomi `pearl_barrage` | scaling | **frontload**, scaling |
   | kokomi `undertow` | scaling, velocity | **frontload**, scaling, velocity |
   | kokomi `depths_judgment` | scaling | **frontload**, scaling |

   The 19-card figure described a different (or since-closed) pool state;
   on today's sheets it is empirically absent.

## Recommendation

Adopt `printed_floor`. The three re-tags match what the cards print and
what their own sheet comments say they were tuned to do. Execution on a
yes: swap the one expression in `role_tempo.scan_row`, re-tag the three
`solve:` lists on the kokomi sheet, and rewrite the pin's docstring to the
corrected premise (its `scaling_only` list shrinks to `the_final_verdict`).

If instead you ratify the pin as written, the sheets should change, not
the scanner: the three bases become explicit `amount: 0` + bonus (the
`suffering_for_art` idiom) or the pin's docstring must stop describing
`pearl_barrage` as floorless — the current state asserts both halves of a
contradiction.

*Provenance: L4q (QUEUE); diff measured 2026-08-07 by dual-pipeline run of
`classify_pool` under both readings (this worksheet's §2); sheet lines
`docs/kokomi-cards.yaml:388,484,561`.*
