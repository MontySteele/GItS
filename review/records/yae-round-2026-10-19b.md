# Yae seat round, 2026-10-19 (the Kitsune pass)

Build: main bb4d92d07, deployed 0.2.5966. Under test: Kitsune Sakura at
Defect's Frost access (`review/active/yae-block-edit-pass-2026-10-19.md`,
#1458), plus the sweep's Daisesshou and Eternity (#1454). Two Sonnet seats,
whole runs, A0, seeds rolled. Lane 1 was briefed toward Kitsune planters,
lane 2 toward an Edit deck with Daisesshou and Eternity. Raw records:
scratchpad `seats-1019b/seat-laneN/record.md` (local).

| Lane | Brief | End |
|---|---|---|
| 1 | Kitsune | **Won** (Ceremonial Beast, Kaiser Crab, Aeonglass) |
| 2 | Edits | floor 33, act 2 boss pair (Crusher and Rocket), short 3 Block on the last turn |

Normal fights, Yae against the base five since 2026-10-05
(`tools/telemetry_report.py`), with the previous round
(`review/records/kokomi-yae-round-2026-10-19.md`) in brackets:

| Act | Block a turn (base) | HP lost a fight (base) | Damage a turn, ratio |
|---|---|---|---|
| 1 | 3.0 (2.5) [1.7] | 11.1% (8.8%) [12.0%] | 0.80 [1.27] |
| 2 | 14.2 (6.0) [3.7] | 4.2% (14.9%) [16.0%] | 1.04 [1.11] |
| 3 | 24.4 (10.0) [--] | 3.1% (10.0%) [--] | 0.85 [--] |

Two seats, 29 normal fights: a direction, not a measurement.

## What played well

- **Kitsune Block works.** Lane 1 drafted Twin Sakura, Kitsune Lantern x2,
  Shrine Maiden's Guard x3 and Kitsune Veil: "from about the second turn of
  each fight the shrine Block was enough"; Kaiser Crab ran 25 to 34 Block a
  turn from three Kitsune. Boss fights became damage races.
- The Edit deck chained 4 to 6 Edits a turn from the act 1 boss on (36 to 42
  from Bestseller with Reprint). No seat found an endless loop; the nearest
  was Dawn Prayer with Eternity.

## What did not

- **Act 1 is still the hole.** Block is now at base, but damage fell to 0.80
  and HP lost per fight is still 1.27 of base: the Kitsune turns trade tempo
  for Block before the shrine is up. The Edit deck was "slow and fragile" in
  act 1, with hands that had nothing to Edit.
- **Late game may now overshoot:** act-2 and act-3 HP lost is under a third
  of base. With Sakura Grove and Tenko Kenshin refreshing them, lane 1's
  Kitsune reached Level 10 to 15 (10 to 15 Block each) at the final boss.
- **The shrine cliff:** Kitsune all planted on one turn expire together; lane
  1 met 39 incoming with no Block on Ovicopter's turn 4.
- **Bug, fixed in its own PR:** an Edit replaced a base-game enchantment
  (Tezcatara's Ember on a Strike: 9 damage became 6). `YaeMasterpiece.Apply`
  cleared any enchantment; now a card wearing one is not Editable.
- Eternity was discarded three times in lane 2 (2 Energy, nothing that turn);
  Daisesshou was never offered.

## What to change

1. **Act 1 tempo**, not Block: a design question for the next Yae paper
   (the Kitsune makers' damage riders, or her act-1 Commons' rates).
2. **Watch Sakura Grove** with Kitsune in long fights; a cap on Levels, or
   Grove leveling one Sakura rather than all, if the next round repeats it.
3. Seat-page items to BACKLOG: a full-shrine plant of another kind withering
   a Sakura surprised lane 1; "refreshes and gains a Level" left a Sakura at
   Level 1 when the shrine was not full (lane 1).
