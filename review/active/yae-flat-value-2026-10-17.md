# Yae: flat value now, on the cards she drafts early (2026-10-17)

Yae is a Prototype kit, so these are Claude's cards and carry no pick.
[USER]: "I suspect the solution here is in a review of the non-scaling kinds
of cards that you draft in act 1 or early act 2. Things that provide some
flat value right now rather than being set up. Let's do that paper."

## 1. What the numbers say

**Sources:**
- Yae: rounds 7 and 8.
- Base five: two runs each on the same five seeds, 2026-10-08 and 10-10, 187
  fights. Those runs record enemy HP every turn; the usual baseline does not.
- Script:
  `C:\Users\Monty\AppData\Local\Temp\claude\C--Users-Monty-Documents-GitHub-GItS\3bee9add-2181-4b79-8aec-fcedf624f7ec\scratchpad\yae-ramp\ramp.py`.

**Findings:**
- **Turn 1 is the gap.** Act-1 normal fights, median damage a turn, base
  against Yae: turn 1 20 vs 15, turn 2 17 vs 14, turn 3 17 vs 19. By act 3
  she is ahead from turn 2.
- **Her fights run about half a turn longer.** 3.7 turns vs 3.1 in act 1, 3.9
  vs 3.5 in act 2. 55% of her normal fights reach turn 4; base, 41%.
- **Block a turn is at par**, and HP lost per normal fight is near it (6.6 vs
  5.9 in act 1, lower than base after). She is not bleeding out in normal
  fights; she is slow to start.
- **A third of her damage (32%) is Sakura strikes.** A Sakura pays about 3 a
  turn for 3 turns. One planted on turn 2 or 3 of a 3.7-turn fight gets one or
  two strikes before the fight ends.
- **In act 1 her deck is mostly Strikes.** 201 Strike plays in 67 normal
  fights. She takes her planters and Block Commons (Twin Sakura 47%, Evergreen
  Charm 41%) more often than most of her attack Commons (Kitsune Pounce 12%,
  Publisher's Deadline 7%).

**The base rate.** The base five's 37 one-cost Common attacks have a median
first hit of 8 (`game_ref/*.json`):
- plain hits are 9 to 10 (Pommel Strike 9, Headbutt 9, Photon Cut 10);
- Sucker Punch is 8 plus 1 Weak;
- a 2-cost Common hits 15 to 18 (Predator 15, Cinder 18).

## 2. The rule for this pass

The cards she drafts in act 1 should pay at the base rate on the turn they
are played. A rider that pays later goes on top of that rate, not inside it.
- Her attack Commons come up to the base numbers.
- Her two planting attack Commons get one new line: the Sakura they plant
  strikes once as it lands. That is damage now. The card also shows what a
  Sakura does the first time she plays one.
- Nothing scaling changes: no Levels, Tenko, Edit payoffs or Rares. Block
  stays where it is, at par.

## 3. The changes (11 attacks, numbers and one line)

| Card | Today | New | Upgrade | Why |
|---|---|---|---|---|
| **Sly Strike** (C 1) | Deal 7. Apply 1 Weak. | Deal 8. Apply 1 Weak. | 10, 2 Weak | Sucker Punch's numbers |
| **Margin Note** (C 1) | Deal 5. Edit: Red Ink. | Deal 7. Edit: Red Ink. | 10 | 4.6 a play in act 1. Red Ink is worth about 3 later |
| **Thunder Petal** (C 1) | Deal 5. Plant a Sakura. | Deal 5. Plant a Sakura. **It strikes this enemy.** | 8 | 8 now (5 + a Level 1 strike of 3) and the Sakura after |
| **Foxfire Sweep** (C 1) | Deal 4 to ALL. Plant a Foxfire Sakura. | Deal 4 to ALL. Plant a Foxfire Sakura. **It strikes now.** | 6 | 6 to ALL now, against Thunderclap's 4 |
| **Sesshou Fang** (C 1) | Deal 6; 6 more if a Sakura is Level 3+. | Deal 8; 6 more if a Sakura is Level 3+. | 10, 8 | Level 3 is rare in act 1. The base hit must stand alone |
| **Thunder Rite** (C 2) | Deal 8. Tenko. | Deal 13. Tenko. | 17 | 8 for 2 with an empty shrine. Base 2-cost Commons hit 15 to 18 |
| **Publisher's Deadline** (C 2) | Deal 12. Costs 1 less if you Edited this turn. | Deal 14. Same condition. | 18 | 2-cost rate. At 1 after an Edit, it is the Edit deck's payoff |
| **Galley Proof** (U 2) | Deal 11. Edit: Reprint. | Deal 14. Edit: Reprint. | 18 | Taken 4 of 8 as the Reprint enabler, but 11 for 2 is far under rate |
| **Kitsune Pounce** (C 1) | unchanged, 8 | | | At rate; its Sakura strike is a bonus |
| **Cliffhanger** (C 1) | unchanged, 8 | | | At rate with Retain on top |
| **Kitsune Barrage** (C 1) | unchanged, 4 x2 | | | Twin Strike's shape; 3 hits with a full shrine |

**Readings for the builder:**
- **"It strikes this enemy" / "It strikes now."** The Sakura the card just
  planted acts once, at its planted Level, on this card's target. A Foxfire
  Sakura hits ALL.
- **Turns.** The strike uses none of its turns, and it is not a Tenko: no
  refresh, and "whenever you Tenko" does not fire. It is Falling Blossom's
  aimed strike, without the wither.
- **Full shrine.** If the plant refreshed a Sakura instead, that Sakura
  strikes.
- **Damage numbers** are the cards' own damage field; upgrades stay as listed.

## 4. Looked at and left alone

- **The planting Skills** (Twin Sakura, Yakan Evocation, Dawn Prayer, Fox
  Fire Draft): setup by design. The fix is that her attacks now pay on their
  own, so a planter turn costs less.
- **The Block Commons:** Block is at par, and she is fragile only in long boss
  fights, where everyone's Block falls short.
- **Her starter:** Yakan Evocation was a never-again pick twice. Basics change
  only on [USER]'s pick ("Starter basics are never changed"), so it is not in
  this paper.
- **The Uncommon and Rare payoffs** (Thunderbolt Tithe, Petal Storm, Tenko
  Kenshin, Daisesshou): already at or above rate per Energy (14 to 20) once
  set up.

## 5. How to check it

Run five seats on the same seeds after the build. The bar:
- act-1 turn-1 damage within 15% of base (15 today, 20 base);
- normal-fight length nearer 3.1 turns;
- no rise in act-2 or act-3 damage beyond base.
