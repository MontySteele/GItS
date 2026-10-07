# Klee should end fights sooner: a short paper, 2026-10-07

Asked for by suite 3, pick 2 ([USER]: "Agreed on both defaults - let's look
into block next"). A first draft proposed more Block that feeds the Bomb.
[USER] turned the direction on reading it (2026-10-07): "Klee's supposed to
read as fragile, which is to say I think her goal should be to kill the
enemies faster than other characters in exchange for chip damage in long
fights. So the fact that she actually has more block, rather than less, in
her card pool reads as a problem to me. I think the real issue is that bombs
need to cook, which forces her to be a slow-play character, rather than a
fast one. I expect Klee to average less block per turn that base characters
but in exchange end fights sooner rather than later."

This paper is rewritten to that direction. Pool read from `klee-next`
4628ed9c (`KleeOverhaulRoster.Slice`, 78 cards); base pools from
`game_ref/<character>.json`; numbers from the fight telemetry, normal fights,
base five on 2026-10-05 before 16:50, Klee from suites 2 and 3 and the test
arm (all 2026-10-07).

## 1. She is slow, and her Block pays for it

**Enemy HP gone by the end of each turn, and damage dealt on each turn
(normal fights, means):**

| Act | Who | Gone by end of turn 1 / 2 / 3 | Damage on turn 1 / 2 / 3 / 4 |
|---|---|---|---|
| 1 | Base five | 35% / 66% / 92% | 20 / 20 / 18 / 11 |
| 1 | Klee | 25% / 71% / 91% | 14 / 28 / 20 / 19 |
| 2 | Base five | 31% / 56% / 85% | 30 / 24 / 40 / 31 |
| 2 | Klee | 26% / 50% / 73% | 24 / 25 / 26 / 36 |
| 3 | Base five | 41% / 66% / 85% | 62 / 42 / 42 / 41 |
| 3 | Klee | 7% / 32% / 64% | 9 / 32 / 61 / 118 |

(Klee is suites 2 and 3 together; the test arm reads the same, act 3 turn
one 6.) Damage taken a turn is the same for both (act 2: 11, 11, 18 against
11, 11, 19), so **every extra turn costs her what it costs anyone**, and her
act-2 and act-3 fights last 4 turns to their 3.

The gap opens with the act. In act 1 she is level by turn two. By act 3 the
base five's decks open with half a fight's damage on turn one, and hers opens
with a Bomb.

**Her Block makes up for it.** She has 17 Block cards to the base five's 11
to 15, and gains more Block a turn than they do (act 2: 5.5 against 2.9).
That is the slow character's trade, the reverse of the one asked for.

## 2. Why: the rules and the pool both pay for waiting

- **Rule 1** grows every Bomb by 4 at the start of her turn. A Bomb set off
  the turn it lands is the smallest it will ever be, so every Set off card
  says "wait".
- **Four cards pay her for not setting off:** Grounded ("if you played no Set
  off card last turn, gain 4 Block and 1 Spark"), Sit Tight (Block if none of
  your Bombs went off), Experiment in Progress (Bomb grows if you played no
  Set off card), and Jean, Lion's Fang (Block and a card if none went off).
- **Turn one has nothing to set off.** Her damage cards are mostly Set off
  cards, and on turn one the only Bomb is the one she just placed.
- **Two Block Commons are never played:** It Wasn't Me! and Sorry, Jean...
  (0 plays in 10 runs).

## 3. The change

Smallest first, per the stage gate. Starter basics and the starter relic are
untouched; rule 1 is offered as an alternative, not the default.

**Out (4 cards, all defence that pays for waiting or is never played):**
Grounded (Uncommon Power), Sit Tight (Uncommon), It Wasn't Me! (Common),
Sorry, Jean... (Common). Block cards go from 17 to 13, the base five's range.

**In (4 cards, all damage on the turn they are played):**

| Card | Rarity | Text |
|---|---|---|
| **Fuse's Lit!** | Common Attack, 1 | Place a Bomb 6 [9], then Set off the enemy. Deal 4 Pyro damage. |
| **Pop-Pop-Pop!** | Common Skill, 1 | Place a Bomb 4 [6] on ALL enemies. |
| **Dodoco Barrage** | Uncommon Attack, 2 | 3 times: place a Bomb 5 [7] on a random enemy. Then Set off ALL enemies. |
| **Head Start** | Uncommon Skill, 0 | Innate. Exhaust. Place a Bomb 6 [9] on each enemy. Gain 1 Spark. |

- **Fuse's Lit!** is a full Set off turn on one card, 10 damage and a Spark
  on turn one (Ka-pow! needs a Bomb already out). It sits beside Pocket Match
  and Countdown, and is the Common the seats can open with.
- **Pop-Pop-Pop!** is the hallway turn: with Tinder Toss (1 Spark: Set off
  ALL, 3 to ALL) it clears three small enemies on turn one or two.
- **Dodoco Barrage** is 15 damage plus every Bomb already out, and 3 Sparks,
  in one card. Its Spark yield pays for the follow-up Attacks the Spray plan
  needs.
- **Head Start** puts her first explosion on turn one. It is a drafted card,
  not the starter (the combat-start Bomb relic was vetoed 2026-10-05; a
  drafted card earns its gain).
- Pool stays 78; rarity 25 / 32 / 21 unchanged (two Commons out, two in; two
  Uncommons out, two in). One Power leaves (Grounded), none comes in.
- All four use ops the build already has (`plant_bomb`, `set_off`, `damage`,
  `gain_spark`); Innate and Exhaust are base keywords.

**Not changed this pass:** Experiment in Progress and Jean, Lion's Fang also
pay for waiting; they are kept to see what four cards do first.

## 4. What a round should show

Turn-one and turn-two damage up in acts 2 and 3; fights at the base five's
3 turns; Block a turn at or below theirs; HP lost a fight at or below theirs
because the fights are shorter.

## Picks

1. **The read.** Klee is slow (act-3 turn-one damage 9 to the base five's
   62) and her Block pays for it. The identity is fast and fragile, in
   [USER]'s words above, recorded in her brief. **Default: agree.**
2. **The change.**
   - **Default (a):** the four out, the four in (section 3), built on
     `klee-next`.
   - (b) (a), plus rule 1's growth from 4 to 2 a turn and every placing card
     +2, so a Bomb cashed now is worth nearly as much as one cashed later.
     This changes a core rule and every Cook card's maths; it is the bigger
     lever if (a) is not enough.
   - (c) Cards only, but cut Experiment in Progress and Jean, Lion's Fang
     too, with two more fast cards (a second paper for their texts).
3. **The round.** **Default:** suite 4 on the same five seeds, graded on the
   section 4 measures.
