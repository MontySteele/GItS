Status: OPEN (no pick; the default in §4 is applied)

# Kokomi, the Plan-less hand: the basic Strike gets a Plan line, so every hand poses the kit's question

Written 2026-09-08, afternoon, from rounds 26 to 30. The one finding those
five rounds repeat without a row is this: a hand with no Plan card in it
has no decision in it. Round 30 lane 1 counted three of its eleven opening
turns, including the first turn of the run; round 27 lane 2 opened fight 1
on "three Strikes and two Defends, the unmodified basic deck", and the
jellyfish panel printed "No Plan card in hand: the jellyfish waits." Round
28 lane 2 named Defend "the only card in the deck that cannot be pointed at
the jellyfish, so the only card that never poses the kit's question."

## 1. Where the Plan-less hand comes from

The starter is four Strike, four Defend, Kurage's Oath and Slack Water
(`KokomiOverhaulRoster.StartingDeck`, `C.KOKOMI_OVERHAUL_STARTER_IDS`). Two
Plan cards in ten. A five-card opening hand from ten cards holds no Plan
card on roughly a fifth of draws, and the first two turns of a fight see
the whole deck once, so one of every fight's first two hands is Plan-less
often enough that every seat since round 25 has named the turn. The pool
fixes it slowly, one draft at a time; the starter is where the turn lives.

## 2. The rule that would fix it, and why not

Give the jellyfish something to do on a hand of basics: "if nothing is
planned at the start of your turn, the Bake-Kurage does X." That is a new
rule in the loop, which [USER] plays, and it papers over the hand rather
than giving it a decision: the jellyfish acting on its own is exactly the
"decoration" round 27 lane 2 called it before its first Plan. Not taken.

## 3. The card that fixes it

Kokomi's basic Strike becomes her own card, the way Klee's starter Strike is
Klee's (`KleeOverhaulRoster.StarterStrike`):

- **Strike** (Kokomi), cost 1, Attack, basic: "Deal 6 damage. Plan: Deal 8
  damage." Upgrade: 9 and 11.

Every hand now holds the kit's question. The written half is Ambush's shape
at a basic's premium: two more damage for a turn's delay, small enough that
"a Plan lands in whatever Block the enemy is standing in" and the enemy's
intent decide it, the same two printed things that decided every
write-or-play turn in the records. Face-up stays the default against a
body about to die or to Block; written is the tempo trade on a safe turn,
and it feeds Feint, Treatise, Scout Ahead and Opening Gambit the way any
damage Plan does. Four Strikes written on one safe turn is 32 next morning
for four energy against 24 now, which is the cap question round 26 closed:
the competition is damage needed now, and nothing here changes that.

Defend stays the base game's. Block a turn late is the dead half every
seat rejected (Read the Field's Plan, round 28 lane 1), a Dusk basic Block
would obsolete Breakwater, and one card in the hand that cannot be written
keeps the question a question.

## 4. What is asked

Nothing. Default (E, applied): pool pass six is the one card above, built
in both engines with the sim's `KOKOMI_OVERHAUL_STARTER_IDS` and the mod's
`StartingDeck` swapped to it, the draft price set as a written 8 against a
face-up 6, and a natural round 31 after it whose debrief counts the opening
hands with no decision in them. If the sim's winrate moves past the
prototype's own band on the change, the number moves, not the shape.
