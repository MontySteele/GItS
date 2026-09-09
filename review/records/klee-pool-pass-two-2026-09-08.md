Status: RECORD (no pick; the defaults in §6 are applied)

# Klee pool pass two: six things to buy with Sparks, priced on Regent's ladder

Written 2026-09-08, evening, from R270 (the round-25 pick, option 1:
"Spark is a currency, its income stays, and the pool gets interesting things
to buy with it; the comparison is Regent"). Read against the brief
(`review/active/klee-brief-2026-09-01.md` §3 rule 4, §4, §5.5, §9), the
round-25 packet (`review/ruled/klee-overhaul-round-25-2026-09-08.md`), the
Regent decompile note (`docs/current/research/regent-stars-economy.md`) and
the pool as it stands (`docs/prototype-surface.yaml`, 45 `proto_ko_` rows).
Prototype stage: no slate, no stamp, no number here is quotable. Every row
went through the doctrine door before it was built (§4). Register row
`EB-730`.

## 1. What the reads said, and what Regent does

**Spark never binds.** Round 23's natural lane ended fights on 2 to 5 Sparks
and spent two all run; round 25's natural lane ended on 3, 5, 5 and spent
none; the assembled Spark-defence lane ran its bank from 1 to 8 across seven
fights and never failed a price, peaking while it was taking damage. The
things that were short on the failing turns were a Block card in hand, a Set
off card in hand, and Energy. Ten of the 45 rows carry a Spark price; nine
of them are Attacks or Bomb setup, one is Block (Dig In), one is Energy at
Rare (Sugar Rush). So the bank buys more of what the deck already has and
none of what it lacks, which is why lane 1 declined every Spark-priced offer.

**Regent, from the assembly.** 23 of 91 cards carry a Star price and 11
generate; the cheapest sink is 1 Star, the median printed price is 3, the
big ones are 5 to 7; 13 of the 23 spenders cost 0 Energy, so a Star price
reads as an alternative cost even though the engine adds the two. The
sinks are spread across Block (Cloak of Stars 1, Particle Wall 2 and it
returns to hand, Reflect 3), Energy (Alignment 2), draw and choice (Guiding
Star, Quasar 2, Decisions Decisions 6) and one Power at 5. The starter
makes 7 Stars a fight and spends 4. The price is a badge and never a line
of rules text.

**What this pass takes from that.** The shelves Regent sells and Klee does
not: Block that is always in hand, Block that feeds her own verb, cards,
a detonator back, Energy below Rare, and one big purchase at the top of the
ladder. The prices: 2 for the Commons and the repeatable Uncommon (Regent's
Particle Wall and Quasar tier), 3 for the median Uncommons, 5 for the Rare.
Income is not touched (R270).

## 2. The six rows

Rarity, Energy, Spark price; the row each is priced against.

**Block**

1. **Blast Shield** — Uncommon Skill, 0 Energy, 2 Sparks. *Gain 6 Block.
   Return this card to your hand.* Upgrade: 8 Block. Particle Wall's shape.
   Once drawn it is never the card that was missing from the hand, which is
   round 25's first failure; it is playable again in the same turn for 2
   more Sparks, so a bank of 8 is 24 Block on the turn that needs it and a
   bank of 1 is nothing. Against Dig In (1 Spark: 8, once): 2 less Block
   for 1 more Spark on a one-use turn; the price is the whole bank when the
   hit is big.
2. **Return to Sender** — Uncommon Skill, 1 Energy, 2 Sparks. *Gain 8 Block.
   This turn, damage this Block absorbs is placed on the attacker as a
   Bomb.* Upgrade: 11 Block. Reflect's shape with her verb: blocking a 12
   puts a Bomb 8 on the attacker, which grows 4 at dawn. Against Dodoco
   Cover (1 Energy: Bomb 4 and 5 Block): more Block, no Bomb on a turn the
   enemy does not attack, and 2 Sparks on top. The choice of which hit to
   block into is the player's.

**Cards**

3. **Bottomless Bag** — Common Skill, 0 Energy, 2 Sparks. *Draw 2 cards.*
   Upgrade: 3. A plain sink at Regent's Quasar price, as Cloak of Stars is
   plain. Against Skim (Uncommon, 1 Energy: draw 3): 1 Energy saved, one
   card fewer. Two Sparks are also two Fwoosh! plays or one Blast Shield,
   which is the competition R270 asked for.
4. **Once More!** — Uncommon Skill, 0 Energy, 3 Sparks. *Return the last Set
   off card you played this combat to your hand.* Upgrade: 2 Sparks. The
   detonator-draw answer: the scarce thing round 25 named is a Set off card
   in hand, and Sparks are the surplus, so the surplus buys the detonator
   back. Dead until a Set off has been played; Ka-pow! is Retained and so is
   rarely the one it returns. Deterministic, no choice prompt: the bridge
   and the seats read it off the log.

**Energy**

5. **Sparkling Burst** — Uncommon Skill, 0 Energy, 3 Sparks. *Gain 1 Energy.
   If a Bomb went off this turn, gain 1 more.* Upgrade: 2 Sparks. Not
   Exhaust. Alignment's shape with an ordering rider: after the detonation
   it is 2 Energy for 3 Sparks, and the detonation is what minted them; on a
   two-charge turn the bank is 1 down unupgraded. Against Sugar Rush (Rare,
   2 Sparks, Exhaust: 2 Energy and a card): less, for more, every fight.
   This lifts draft 4's "Energy only at Rare" line (§5.5); R270 names
   Energy among the things Spark buys, and Regent sells it at Uncommon.
6. **Blazing Delight** — Rare Power, 2 Energy, 5 Sparks. *At the start of
   your turn, gain 1 Energy and draw 1 card.* The top of the ladder. Sparks
   do not carry between fights, so 5 is bought mid-fight off this fight's
   explosions or not at all, and the purchase turn pays nothing: with a
   lethal 15 coming, buying it instead of blocking is the wrong turn, and
   holding 5 Sparks through two turns of Set off offers is the decision.
   Neutron Aegis's slot (Rare Power, 5 Stars).

Pool after the pass: 51 rows, Rares 9, Spark-priced 16. The second currency
now reaches Block, cards and Energy below Rare, and its sinks compete with
each other for the bank.

## 3. What the pass does not do

No income change: R270. No starter change: R242. No change to the ten
existing spenders. No Power that pays on spending (§4, Blast Goggles). No
second plain Block at 1 Spark: Dig In is that card. Nothing here is a
number pick; every figure is a starting point the seats move.

## 4. The audit

Seven arms went to the doctrine role as one read
(`review/qa/klee-pass-two-2026-09-08-prompt.txt`, reply `-reply.md`),
charter C1 to C6 with Regent's rows as C6 reference points. Six FOLLOWS,
each with its clause and its breaching line; one REQUIRES_MODIFICATION:

| arm | verdict | clause | the line |
|---|---|---|---|
| Blast Shield | FOLLOWS | C2, C5, C6 | 2 less Block than Dig In for 1 more Spark on a one-use turn; a non-attacking enemy makes declining right |
| Return to Sender | FOLLOWS | C2, C3, C6 | 3 more Block and 4 less Bomb than Dodoco Cover on a quiet turn, for 2 Sparks more; the hit chosen is the player's |
| Bottomless Bag | FOLLOWS | C2, C5, C6 | one card fewer than Skim; at bank 3 it forces Dig In or Fwoosh!, not both |
| Once More! | FOLLOWS | C2, C4, C5, C6 | returns nothing before a Set off is played; buys retrieval, not an explosion |
| Sparkling Burst | FOLLOWS | C1, C2, C5, C6 | 1 less Energy and a card than Sugar Rush; a two-charge turn nets the bank −1 |
| Blast Goggles | REQUIRES_MODIFICATION | C5 | "spends no Sparks itself ... never competes for the bank at all" |
| Blazing Delight | FOLLOWS | C1, C2, C5 | nothing on the purchase turn; against a lethal 15 buying it is wrong |

The reviewer's closing read: "with bank 3 and no further income this turn,
Blast Shield's 2-Spark purchase and Bottomless Bag's 2-Spark purchase cannot
both be funded." Blast Goggles (Uncommon Power, 1 Energy: 2 Block per Spark
spent, Child of the Stars' shape) is WITHDRAWN, not rewritten: a payoff on
spending is not a sink, and the pass is sinks.

## 5. The build and round 26

FOLLOWS rows are built C# first (stage-gate), then the tier0 twin, then the
surface row and both pool tuples; a new seam where an engine lacks one
(return to hand after play; absorbed Block placed as a Bomb; the last Set
off card played; a start-of-turn Energy-and-draw Power). Round 26 then reads
the pass on two lanes:

**Lane 1, natural:** "a natural seat offered the pass's rows takes at least
one, reaches a turn on which two Spark-priced cards in hand compete for one
bank, and names which it bought and why." **Lane 2, assembled on the pass**
(Blast Shield, Return to Sender, Once More!, Sparkling Burst, Dig In, one
drafted detonator): "the seat reaches the act-1 elite with no Block turn
failing on detonator draw, and where a Block turn fails the record names
whether the Spark, the card or the Energy was missing." Both read against
round 25's figures.

## 6. Defaults applied (D and E), disclosed

- **E:** six rows, not a shelf per Regent sink; the brief's own §7.4 rule,
  stop at the number that is live.
- **E:** prices 2 / 3 / 5 from Regent's ladder, income untouched (R270).
- **E:** Blast Goggles withdrawn on the verdict rather than re-priced; a
  priced version can return through a later pass with its own read.
- **E:** the brief's §4 sentence on stinginess and §5.5's "Energy only at
  Rare" line are amended in place under R270 (draft 4 amendments, §18).
- **E, from the build:** Blazing Delight is the pool's ninth Rare, one past
  the brief's §7.4 count of eight; a combat-long Energy engine is not an
  Uncommon, so the count moves and the brief's table says so. Its upgrade
  lowers the Spark price to 4 (the other two Spark-priced Uncommons'
  rail), not the Energy. Bottomless Bag's face is spelled with Countdown's
  draw variable so the upgrade shows on the card (`EB-283`). Once More!
  remembers the last card whose Set off resolved, which for every row on
  the surface is the last Set off card played.
- No number moved on an existing row; nothing measured; no stamp moves.

No pick.
