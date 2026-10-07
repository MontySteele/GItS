# Klee's defence in acts 2 and 3: a short paper, 2026-10-07

Asked for by suite 3, pick 2 ([USER]: "Agreed on both defaults - let's look
into block next"). The question: why does Klee lose more HP than the base
five in acts 2 and 3 (suite 3: 1.17 and 1.59 of their HP lost), and what is
the smallest change that fixes it. Pool read from `klee-next` 4628ed9c
(`KleeOverhaulRoster.Slice`, 78 cards, against `docs/prototype-surface.yaml`);
base pools from `game_ref/<character>.json`; numbers from
`tools/telemetry_report.py`, normal fights, base window 2026-10-05 before
16:50.

## 1. She is not short of Block

**Count.** Klee's pool has 17 Block cards: 7 Common, 7 Uncommon, 3 Rare. The
base five have 11 to 15 each, 4 to 6 of them Common.

**Block gained a turn, normal fights (median):**

| Act | Base five | Klee, suite 3 | Klee, test arm |
|---|---|---|---|
| 1 | 2.2 | 3.3 | 2.7 |
| 2 | 2.9 | 5.5 | 7.3 |
| 3 | 7.5 | 7.7 | 11.3 |

She blocks as much as the base five or more in every act.

## 2. Where the HP goes instead

**Act 2: fights last a turn longer.** Klee's act-2 normal fights last 4 turns
(median), the base five's 3. Per turn she loses less than they do (3.7% of
max HP against 4.2%); over the extra turn she loses more (14.7% against
12.6%). Act-2 damage a turn is 0.86 of theirs. So act 2's HP gap is a
damage gap that shows up as HP.

**Act 3: spike turns.** On 9 fights she loses 5.0% a turn against their 4.2%.
All four suite-3 deaths after act 1 were one big hit with no Block in hand
(the suite 3 record quotes each). That fits a deck whose Block is in it but
not in the hand on the turn it is needed.

## 3. What the seats actually play

Plays over suite 3 and the test arm (10 runs):

| Card | Rarity | Plays | What it asks |
|---|---|---|---|
| Defend | starter | 354 | -- |
| Bombs Away! | Common | 82 | 1 Energy: a Bomb 4, Block 4 + 2 per enemy with a Bomb |
| Dig In | Common | 56 | 0 Energy, 1 Spark: Block 8 |
| Noelle, Survival Rulebook, Look Out!, Behind Jean's Desk | mixed | 14 to 24 each | -- |
| Run Away!, Windtrace, Blast Shield, Return to Sender, Sit Tight | mixed | 2 to 12 each | -- |
| It Wasn't Me!, Sorry, Jean..., Klee Can Explain!, Grounded | 2 Common, 2 Unc. | 0 | -- |

The Block card the seats take is the one that also places a Bomb. Of the
seven Commons, two are never played: **It Wasn't Me!** (0 Energy, Block 6, a
Dazed into the discard) and **Sorry, Jean...** (remove one of your Bombs,
Block equal to its size), which spends her plan to defend.

Sparks are rarely the limit: two seats ended turns on 5 to 10 unspent. Only
the Defect seed's final-boss death came from a Spark-priced Block card sitting
dead, after Fireworks Finale spent the bank on a kill.

## 4. The change

The stage gate's order is a card adjusted before anything new. The evidence
points at one dead Common, rewritten so its Block rides on her plan the way
Bombs Away! does:

**It Wasn't Me!** (Common Skill), from "0 Energy. Gain 6 Block. Add a Dazed
into your Discard Pile." to:

> 1 Energy. Gain 7 [10] Block. Your largest Bomb grows by 3.

- **Why this shape.** Block a seat takes because it also feeds the Bomb, so
  more of her Block reaches the hand. The growth also adds a little damage,
  the act-2 lever.
- **Against the base.** Shrug It Off is 1 Energy, 8 Block and a card. This
  is 7 Block and 3 Bomb, which is worth nothing without a Bomb out.
- **What it gives up.** One Dazed source of the status package. Forbidden
  Fun, Up in Smoke! and Fish Blasting still feed it.
- **Wording.** Uses Witch's Homework's existing `grow_largest` op and
  wording; no new rule.

**Sorry, Jean...** stays as it is in this pass. It is a dead card, but no
evidence says what to make it, and two changes at once would blur the round.

## 5. What this does not fix

The act-2 extra turn is a damage question: how much she deals in the first
two turns of a fight, before her Bombs have grown. That is a separate paper
if this change does not move act 2.

## Picks

1. **The read.** Klee is not short of Block: she gains as much a turn as
   the base five or more. Act 2's HP gap is fights a turn longer; act 3's is
   spike turns with no Block in hand. **Default: agree.**
2. **The change.** **Default (a):** It Wasn't Me! becomes "1 Energy. Gain 7
   [10] Block. Your largest Bomb grows by 3.", built on `klee-next`.
   - (b) Same text, at 8 [11] Block.
   - (c) Leave defence alone and write the damage paper (section 5) instead.
3. **The round.** **Default:** suite 4 on the same five seeds, graded the
   same way, reading act-2/3 HP lost and how often It Wasn't Me! is played.
