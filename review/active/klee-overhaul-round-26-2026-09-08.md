Status: OPEN (one A pick, §5; the defaults in §6 are applied)

# Klee round 26: the sinks work when the bank can pay, and the bank cannot pay on turn one

Written 2026-09-08, late, from two blind Opus seats on `0.2.3159+proto`
(main `9b598cf0` after #468), the first build carrying pool pass two
(`review/records/klee-pool-pass-two-2026-09-08.md`, `EB-732`, six Spark
sinks priced on Regent's ladder under R270). Records:
`review/qa/klee-round-26-2026-09-08/opus-lane1-natural.md` (lane 1, natural,
no grant) and `opus-lane2-spark-sinks.md` (lane 2, granted the six sinks
plus Dig In and Fwoosh!). Prototype stage, Guardrail 7. Each seat's brief was
the standard brief with one question appended, (f) below.

## 1. The two hypotheses, and the outcome

**Lane 1:** "a natural seat offered the pass's rows takes at least one,
reaches a turn on which two Spark-priced cards in hand compete for one
bank, and names which it bought and why." Outcome: 120 of 120 acts, floor
14, six fights, 39 of 62 HP, fights 4 and 5 taken at zero damage. It was
offered Blast Shield twice, Return to Sender, Bottomless Bag and Bang Bang!;
took Bottomless Bag and declined the rest on price. **No turn had two
Spark-priced cards competing for a bank that could not pay both.**

**Lane 2:** "the seat reaches the act-1 elite with no Block turn failing on
detonator draw, and where a Block turn fails the record names whether the
Spark, the card or the Energy was missing." Outcome: 120 of 120, floor 8,
six fights including the elite Byrdonis, killed; 31 of 62. No Block turn
failed on detonator draw. Six Block turns fell short; the missing thing was
the Spark on three, the card on two, the Energy on one.

## 2. The reads

**1. The bank is a wall on turn one and a surplus after fight three.** Lane
2's three Spark-missing turns were all opening turns (fight 1 turn 3 with the
bank still at 1, fight 3 turn 1, fight 4 turn 1): the bank is 1 by rule 4
until a Bomb goes off, and the pass's cheapest sink is 2. Once Grounded was
drafted the constraint moved to Energy, "which is the healthier failure",
and 8 Sparks burned at two fight ends because the killing card was free. In
its words: "a wall for the first three fights and a surplus for the last
three, and it crossed over the moment I drafted Grounded. There is no
middle."

**2. A 1-Spark setter is free; 2 is the only real price.** Lane 1: Pocket
Match and Fwoosh! spend 1 and Pounding Surprise refunds 1 the instant the
Bomb goes off, so "a 1-Spark card is free and a 2-Spark card is the only
real price in the currency." Its bank sat at 1 to 4 and expired unspent in
every fight; the one turn a price bound was Bottomless Bag at 2 on a bank of
1, and that was because no Bomb had gone off yet.

**3. Regent's ladder was taken without Regent's opening.** The pass priced
its rows 2 / 3 / 5 from the decompile note. Regent's starter opens every
fight at 3 Stars (Divine Right) and its Basic sink costs 2; Klee opens at 1
(rule 4, R242) and her income is per explosion. So the same prices land two
turns later on Klee than on Regent, on exactly the turns the pass was
written for. That is the design fact this round adds.

**4. The sinks made turns when the bank could pay.** Return to Sender
absorbed 18 of the elite's hits into a Bomb 32 that killed it next turn,
"the single best thing the Spark economy did all round"; Blast Shield
returned to hand twice in one turn for 12 Block; Once More! bought a second
Perfect Timing; Bottomless Bag was lane 1's only real second use of the
bank. Lane 2 also named the trap on Once More!'s face: 3 Sparks to return a
Set off card that may itself cost the fourth. That is a decision the card
prints, and it read it before it paid.

**5. Sparkling Burst was never played, and Blazing Delight was never seen.**
Lane 2 rejected Sparkling Burst three times: "the bank it drains is the same
bank the Energy is supposed to buy things with." Neither lane was offered
Blazing Delight, so the top of the ladder is unread.

**6. One placer in the starter.** Lane 1, structural: Jumpy Dumpty is the
only Bomb source in the starter, so turn one was the same play in all six
fights and every Set off card is a below-Strike attack on any turn after the
first detonation; Powder Charge (floor 12) was the fix, and the seat called
declining Bang Bang! on price "my worst pick of the run". This is the
starter's shape (R242, R261) read from the placer side where round 23 read
it from the detonator side; it is recorded, not raised, and option 1 below
reaches it sideways.

**7. What the seats liked, again.** Grow or fire, decided by the enemy's
intent line (Nibbit's telegraphed Block; Ritual's clock answered the same
question two ways in one fight); Cryo before Pyro; which setter eats the
detonation once the deck holds a free one and a paid one. Lane 1's fight 2
turn 2 computed a kill to the point off five printed numbers and a Mine's
rider. Both seats said the screens' arithmetic is what makes the kit read.

## 3. Where the screen and the outcome disagreed

- **`Bomb 21` beside `sizes: 12`** on the power block (lane 1, fights 4 and
  5): the Melt-folded header beside the raw size, `EB-721` seen again.
- **"What reacted this turn" empty on turns a reaction fired** (both lanes,
  three turns: two Melts and an Overloaded that drove Perfect Timing's
  replay). `EB-710`'s family; the evidence is added to the row.
- **The enchantment chooser prints no enchantment tag** (lane 1, Self-Help
  Book): ten identical Strike and Defend rows where the combat hand prints
  `(Spiral)`; the seat could not aim the pick. New row.
- **Reaction preview on a card that Sets off first** (lane 1, Pocket Match):
  "this card's 7 lands 12" against an aura its own first sentence consumes;
  it landed 7. New row.
- **"Say `confirm` after `choose`" printed above "Confirm is not available"**
  on the Rare chooser and the potion chooser (lane 2): `EB-704`'s family;
  evidence added.
- Not defects: Shrink did not reduce an explosion (rule 5 and R248, a Bomb
  carries the target's modifiers only, and the Bomb tip says "only Vulnerable
  and the HP cap move it"); two Grounded stacks paid 8 Block and 1 Spark (the
  Spark is flat by rule, `KLEE_OVERHAUL_GROUNDED_SPARK`, and the line said
  so); Large Capsule's "no face" caveat was the bridge describing its own
  feed, and the relics and cards arrived.

## 4. What the round did not test

Blazing Delight (never offered). An act-1 boss. A natural lane that took a
2-Spark sink before fight 4. Whether Sparkling Burst reads differently on a
deck whose Energy binds, which lane 2's elite suggests and one rejection per
turn does not settle.

## 5. Pick

Rule 4 (brief §3, R242) opens every combat at 1 Spark. Both lanes say the
pass's prices are right for the bank Regent has and wrong for the bank Klee
has, and the brief cannot settle which bank she should have.

1. **The opening bank (A).** **Default: 1.** (1) Open every combat at 3
   Sparks, Regent's Divine Right: rule 4 changes, the pass's prices stay, a
   2-Spark sink is playable on turn one and a 3-Spark one after the first
   explosion, and Powder Charge becomes a turn-one second placer; a rule
   change [USER] plays, with lane 1's surplus as the known risk (three
   Sparks that expire unspent in a fight with no sink). (2) Reprice the pass
   to the bank she has: Blast Shield 1, Bottomless Bag 1, Return to Sender
   1 Energy and 1 Spark, Once More! 2, Sparkling Burst 2, Blazing Delight 4;
   rule 4 untouched, no play owed, and 1-Spark sinks that do not refund
   still bind only on turn one. (3) As it is: read a third lane that is told
   the sinks are affordable, and let the surplus stand.

## 6. Rows and defaults

Minted: `EB-733` the reaction preview on a Set-off-first card; `EB-734` the
enchantment chooser's missing tags. Evidence appended in place to `EB-710`
(the empty reaction log) and `EB-704` (the confirm note on choosers);
`EB-721` cited. Defaults applied (E): nothing built, nothing measured, no
number moved; the two new rows are display and bridge work. Round 27's
hypothesis is written from the ruling on §5 (QUEUE `klee-opening-bank
5.1`); nothing is scheduled before it.
