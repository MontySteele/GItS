# Varka solo check, 2026-10-07

The solo half of [USER]'s co-op standard (`docs/current/operations/stage-gate.md`,
"Solo first, co-op checked"): "the characters should not be outright weak in
single player and dependent on reactions in a way that makes co-op
exponentially easier." The co-op round (`coop-reaction-round-2026-10-07.md`)
found Varka supplies most of a pair's reaction debuffs, so this reads him
alone. Varka is at Prototype, so nothing here binds; it is a reading.

**What ran.** Solo Varka on the five base-five baseline seeds, A0, one Sonnet
seat (medium) per act with the previous act's record as handoff, on lanes
Klee's suite 2 freed (`klee-next` 0.2.4516+next; Varka's kit is the same on
`main`). Graded against the base characters' baseline runs on the same seeds
(`telemetry_report.py`, base window 2026-10-05 before 16:50).

## Result: 1 win of 5, and three runs went as far as the base character

| Seed (base character) | Varka ended | Base character ended | Klee suite 2 ended |
|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | floor 48, Test Subject (third form, 190/300 left) | floor 48 | floor 25 |
| CYHZM9S0VPW6 (Silent) | floor 17, The Kin (Priest about 43/190 left) | floor 48 | floor 17 |
| DJCAV76ZKAUN (Defect) | **won**, floor 48, 15/87 HP | floor 48 | floor 33 |
| YEWA0B7AVE45 (Necrobinder) | floor 46, Mecha Knight elite | floor 46 | floor 33 |
| R41TX5Q0ZQYN (Regent) | floor 33, Kaiser Crab (act-2 boss) | floor 48 | floor 33 |

The base five went 0 of 5 on these seeds with the same seat model.

## Telemetry: normal fights against the base five, same seeds

| Act | Varka damage a turn | Ratio | Varka HP lost, % of max | Ratio | Varka Block a turn |
|---|---|---|---|---|---|
| 1 | 19.5 | 1.05 | 5.4 | **0.61** | 3.5 |
| 2 | 37.4 | 1.13 | 5.4 | **0.43** | 7.2 |
| 3 | 43.4 | 0.90 | 8.8 | **0.69** | 9.7 |

- Damage is level with the base five; HP lost is 30 to 57% below them,
  outside the bar on the strong side in every act. Base Block a turn on these
  seeds was 2.2, 2.7 and 5.8 (suite 1 record); Varka's is roughly double.
- Thundering Verdict is his scaling card (53 a play in act 2, 72 in act 3);
  Four Winds' Ascension grows from 18 to 28 a play.

## Reactions alone

102 fights, 394 turns (`--reactions`): 1.00 reactions a turn (Swirl 0.54,
Superconduct 0.13, Overload 0.12, Melt 0.11), amplifier bonus 0.8 damage a
turn, reaction debuffs 0.5 stacks a turn (Vulnerable 0.24, Poison 0.13, Weak
0.11). In co-op with Klee he set off 1.30 a turn and applied 0.87 debuff
stacks a turn: a partner adds about a third to his reactions and three
quarters to his debuffs. Klee's suite-2 seats, alone, set off 0.05 a turn.

## What it says

1. **Varka is not weak alone.** He is level on damage and well ahead on
   survival, and he makes his own reactions (his Anemo sets off any aura he
   or a companion leaves). He meets the solo half of the standard.
2. **Klee is the reaction-dependent one.** Alone she almost never reacts
   (0.05 a turn), so a partner's elements are nearly all new value for her;
   that is why co-op lifts her far more than it lifts Varka.
3. **Varka may be too sturdy** when he reaches Balance: HP lost at about half
   the base five's. One run a seed is a small sample; a Balance suite would
   settle it.

No picks: Varka is at Prototype, and the measurement law binds at Balance.
This is a note for his Balance plan.
