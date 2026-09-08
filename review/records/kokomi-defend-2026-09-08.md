Status: RECORD (was OPEN, no pick; the defaults it names were applied; moved 2026-09-08 under R267)

# Kokomi, the Defend: the last unwritable card is worth more while the jellyfish holds a Plan

Written 2026-09-08, evening, from rounds 28 to 31. With the basic Strike
carrying a Plan line (`EB-703`), the two seats of round 31 name the same
card from two sides. Round 28 lane 2: Defend is "the only card in the deck
that cannot be pointed at the jellyfish, so the only card that never poses
the kit's question." Round 31 lane 2: the one dead turn of a 39-turn run
was a hand of two Defends, two Wounds and two cards it could not use. Round
31 lane 1 died on the elite to a five-card hand with no Block at all
against 21 incoming: "the kit's defence is concentrated in three cards, and
two of them only pay when the Casket is firing." Defend is unwritable, and
Block is thin.

## 1. What not to do

Not a Plan line. Block a turn late is the half every seat has rejected
(Read the Field's Plan, round 28 lane 1, "always one turn late"), and a Dusk
line on the basic would make Breakwater a strictly worse card the day
after it was rebuilt. The Plan-less-hand note kept one card that cannot be
written so the question stays a question; that stands.

Not a rule. "The jellyfish Blocks for you" is the decoration round 27 lane 2
warned of, and a rule change is [USER]'s to play.

Not more Block cards in the starter. Lane 1's hand had no Defend because
the draw did not offer one; a stronger Defend does not change how often a
Defend is drawn, and the dead-run rate under the sim is the number that
says whether the starter needs a fifth Block card. That number is asked
for below and not guessed.

## 2. The card

Kokomi's basic Defend becomes her own, the way her Strike did:

- **Defend** (Kokomi), cost 1, Skill, basic: "Gain 5 Block, plus 2 if the
  Bake-Kurage is holding a Plan." Upgrade: 8, plus 2.

"Holding" is the jellyfish's queue at the moment Defend is played: a Plan
written earlier this turn counts, a Dusk entry counts until it resolves,
and a queue emptied by the morning's carry-out does not. So the card asks
its question by ordering, on the turn: write first and Block for 7, or
Block first for 5 and keep the energy uncommitted. That is the same shape
the seats already play (Opening Gambit before Scout Ahead; Kurage's Oath
before Breakwater), and it puts the kit's engine under its floor: a turn
that writes a Plan is a turn whose Defend is a Defend+, and a hand of
Defends with nothing to write is, still, a hand of Defends. Two points is
the size of Breakwater's per-Plan clause and of the basic Strike's premium.

## 3. What it does to the numbers, and what is asked of the sim

A turn with one write and one Defend gains 2 Block; the starter writes on
most turns from fight 1 (round 31: 17 writes in two lanes' 66 turns, and a
Plan line in every opening hand). The sim reports the dead-run rate and
the act-1 winrate before and after, and the fraction of Defends played with
a Plan held; if the rate does not move, the floor question moves to the
pool (a Common face-up Block card with a Plan-shaped rider), not to a rule.

## 4. What is asked

Nothing. Default (E, applied): pool pass seven is the one card above, built
in both engines with the sim's starter ids and the mod's `StartingDeck`
swapped to it (`StarterDefend` returning it, as `StarterStrike` does), never
offered, priced as 5 plus the neutral single-unit estimate of the rider;
then a natural round 32 whose debrief counts Defends played with a Plan
held against those played without, and asks whether the order was chosen.
