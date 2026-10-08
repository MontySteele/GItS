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

## 2. Why: each engine is missing its damage

[USER]'s frame (2026-10-07): Klee holds three archetypes in tension. **Cook**
grows a few Bombs large and cashes them at a very big number, "but you
probably die along the way ... The problem here is we don't have many effects
which deal damage without setting off the bombs." **Spray** places and sets
off many Bombs fast for the Sparks, "but then you need to solve damage
again ... we don't have many ways to directly convert the sparks back into
damage, as opposed to a support engine." **Companion, Reaction and Status**
cards sit between them. "So Cook is too slow, which skews us towards
defensive decks. And Spray doesn't have the damage to compete."

The pool agrees, card for card:

- **18 of her 78 cards say Set off.** Damage that leaves the Bombs cooking
  is 8 cards, 2 of them Common: Forbidden Fun (10, a Dazed) and Fish Blasting
  (8 to ALL, a Confiscated). The rest are Mine, All Mine! and Jumpy Dumpty
  Mk.III (Uncommon, both also place Bombs), Prune (a companion), and three
  Rares (Red Knight, Sparks 'n' Splash, Spark Knight). A Cook deck has no
  Common way to deal damage while it waits, so it waits behind Block.
- **14 cards spend Sparks; one turns them straight into damage, and it is
  Rare** (Fireworks Finale, 5 to ALL per Spark). Of the rest, four buy Block
  (Dig In, Blast Shield, Sit Tight, Cover Your Ears!), five are engine
  (Bottomless Bag, Sparkling Burst, Blazing Delight, Boom Badge, Stoke the
  Fuse), and four are more Bombs or more Set off (Booby Trap, Tinder Toss,
  Quick Fuse, Boom-Boom Strike). Spray's Sparks loop back into Spray.
- **Four cards pay for waiting**, which is Cook's rule turned into defence:
  Grounded, Sit Tight, Experiment in Progress, Jean, Lion's Fang.
- **Two Block Commons are never played:** It Wasn't Me! and Sorry, Jean...
  (0 plays in 10 runs).

## 3. The change

Smallest first, per the stage gate. Starter basics and the starter relic are
untouched. Two cards for each engine's missing damage, paid for by four
defence cards.

**Out (4):** Grounded (Uncommon Power), Sit Tight (Uncommon), It Wasn't Me!
(Common), Sorry, Jean... (Common). Block cards go from 17 to 13, the base
five's range.

**In (4):**

| Card | Engine | Rarity | Text |
|---|---|---|---|
| **Dodoco Tag** | Cook | Common Attack, 1 | Deal 9 [12] Pyro damage. Your largest Bomb grows by 2. |
| **Simmer** | Cook | Uncommon Attack, 1 | Deal 5 Pyro damage, plus half your largest Bomb's size. The Bomb does not go off. |
| **Explosive Spark** | Spray | Common Attack, 0 | Costs 1 Spark. Deal 7 [10] Pyro damage. |
| **Kaboom!** | Spray | Uncommon Attack, 1 | Costs 2 Sparks. Deal 18 [24] Pyro damage. |

- **Dodoco Tag** is Cook's plain Common Attack: a base-rate hit that keeps
  the Bomb growing instead of spending it. It is what a Cook deck plays on
  the "quiet" turns instead of a Defend.
- **Simmer** is the Uncommon payoff for having cooked: at a Bomb 20 it hits
  for 15 and the Bomb is still there. It is the Sparks 'n' Splash idea at
  Uncommon, on a card, once.
- **Explosive Spark** is the Spray Common: one Spark, one hit, 0 Energy, the
  name of Klee's charged attack in the source game. With Tinder Toss (1
  Spark: Set off ALL) minting Sparks from a board of Bombs, the Sparks now
  come back as damage.
- **Kaboom!** is the Uncommon Spark payoff at 9 a Spark, between Explosive
  Spark (7) and Fireworks Finale (5 to each enemy).
- **Archetype three** loses one Dazed source (It Wasn't Me!); Forbidden Fun,
  Up in Smoke! and Fish Blasting still feed the status cards.
- Pool stays 78, 25 / 32 / 21 (two Commons out, two in; two Uncommons out,
  two in). One Power leaves (Grounded), none comes in.
- **Build note.** Dodoco Tag, Explosive Spark and Kaboom! use ops the build
  has (`damage`, `grow_largest`, `spend_spark`). Simmer needs one new op,
  damage read off the largest Bomb's size, which Sparks 'n' Splash's power
  already computes.

**Not changed this pass:** Experiment in Progress and Jean, Lion's Fang also
pay for waiting; rule 1's growth of 4 a turn stays.

## 4. What a round should show

Turn-one and turn-two damage up in acts 2 and 3; fights at the base five's
3 turns; Block a turn at or below theirs; HP lost a fight at or below theirs
because the fights are shorter. Per engine: how often the four new cards are
played, and whether Spark-heavy decks spend Sparks on Explosive Spark and
Kaboom! rather than on Block.

## Picks

1. **The read.** Klee is slow (act-3 turn-one damage 9 to the base five's
   62) and her Block pays for it, because Cook has no Common damage that
   leaves the Bombs cooking and Spray has no Spark-to-damage card below
   Rare. The identity is fast and fragile, in [USER]'s words above, recorded
   in her brief. **Default: agree.**
2. **The change.**
   - **Default (a):** the four out, the four in (section 3), built on
     `klee-next`.
   - (b) (a), plus rule 1's growth from 4 to 2 a turn and every placing card
     +2, so a Bomb cashed now is worth nearly as much as one cashed later.
     This changes a core rule and every Cook card's maths; it is the bigger
     lever if (a) is not enough.
   - (c) (a), plus Experiment in Progress and Jean, Lion's Fang out for one
     more card per engine (a second paper for their texts).
3. **The round.** **Default:** suite 4 on the same five seeds, graded on the
   section 4 measures.
