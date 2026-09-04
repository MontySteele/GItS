# WATCH REGISTER (dormant)

> Blessed mechanisms with a named quantity and a named trigger: monitored,
> not open decisions, and nothing is tuned on the strength of being watched.
> Each returns to [USER] only when its trigger fires. Moved out of
> `STATE.md` 2026-09-01 under the prose diet (machinery review, change 5);
> nothing was changed in the move.

---

- `W1` X4 (block-side Guest Cast), `W2` X6 (salon power level), `W3` X12 (co-op
  reaction potency — instrument unblocked since `O-1` closed; a new reading
  runs under EXPERIMENTS law), `W4` X5 (fanfare floor).
- **`W5` `lynette_box_trick`** (X7, R161) — deliberately left at its current
  rarity; as a companion card it is close to "what if I high-roll a colorless
  option". **Trigger:** playtest shows it overperforming.
- **`W6` `gyorin_formation` — pre-emptive Block RATE.** Explicitly not a
  single-turn spike: the card is 6 Block now (+1 per 2 Charge) and 6 more at the
  start of the next turn — 12 across two turns, not 12 on one. The worry is 6
  pre-emptive Block *every turn* for as long as it keeps coming around, on a
  character whose Charge bank fills on every rotation and is never spent (R80).
  **Trigger:** her stability number moves materially in the post-fill baseline.
- **`W7` `what_the_tokoyo_took` — upper-tail discard count and realized
  damage.** The reprice (cost 2 → 1, 3-per → 4-per) was ruled as a real power
  increase. A chained turn reaching 6+ discards is 30 damage for 1 energy (33
  upgraded). **The obligation is on the INSTRUMENT:** the post-fill baseline
  must report **p90/p99 per-turn discard count and this card's realized damage
  distribution**, never a worked example. The tail is the whole question.
- **`W8` `send_the_runner` — burst-particle cadence.** Charge is a wash
  (`CHARGE_PER_EXHAUST = 1` replaces the dropped grant exactly), but the card
  now also pays `KOKOMI_BURST_PER_EXHAUST = 2` particles it never paid before —
  at Common, at cost 0, repeatable. **Trigger:** Burst frequency across a run
  reads above the ratified meter-20 cadence (R139) in the post-fill baseline.
- **`W9` `X9` — Kokomi's Charge bank, uncapped and never spent.** R188 ruled
  workshop axis **G**, the null option: **no Charge read budget** — a deferral
  of a nerf, not an endorsement, with the §3.3 double read ruled intended
  deckbuilder stacking. Reads per turn are instrumented and the instrument is
  deliberately inert (`resources.note_charge_read` →
  `CombatState.charge_reads_this_turn`, one `charge_reads_turn` sample per
  completed player turn; nothing reads the tally back, so it is not a budget and
  cannot become one by accident). Declared blind spot: the sample rides
  `turn_close`, which a turn ending in the last kill or the player's death never
  reaches, so the truncation is toward the BUSY end — measured 2026-08-30 at 46
  turns of 106,907, carrying zero reads between them. **THE TRIGGER HAS FIRED.**
  `X9READ-S1` was countersigned (R233), run and graded 2026-08-30 at
  `RT12/D18/P11/C21`: the repeatable readers are **58.91%** of completed-turn
  reads against `W9` Limb A's `> 50%` (51.68% with `EB-242`'s pilot-estimate
  reads removed), while the ruled double read lands on **0.22%** of attack plays
  and Limb B does not fire. The severity indicator is QUIET — `p50` 0 reads per
  turn, and the pulse floor the slate was drafted against does not exist at this
  cell (`KURAGE_ALWAYS_ON` is read only under the quarantined `KURAGE_MEMORY`).
  Re-read 2026-09-04 after `EB-242` (`x9read-reread-2026-09-04.md`): Limb A
  51.76%, still QUIET. **Ruled R255 (M69 pick 1): R188 stands, no read budget;
  the trigger is discharged** and the instrument stays inert. Nothing was
  nerfed, capped, deduped or budgeted (packet §9; `EB-78` closed on it).

(Migrated from the retired watch-items docket, frozen at tag
`pre-simplification-2026-08-06`; `W5` added 2026-08-10, `W6`–`W8` at `EB-69`
2026-08-23, `W9` 2026-08-24.)
