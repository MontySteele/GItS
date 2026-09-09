Status: OPEN (six A picks, §8; paper only, no row moves until ruled)

# Klee pool consolidation: what to cut, what the space is for, and whether Spark is a problem yet

Written 2026-09-09 from [USER]'s notes and GPT's review of the same day, read
against the brief (`review/active/klee-brief-2026-09-01.md`, draft 4 + §18),
the 53 rows on `docs/prototype-surface.yaml` (`proto_ko_*`), the engine
(`tier0/engine/klee_overhaul.py`), the comparison pass
(`review/records/klee-pool-comparison-pass-2026-09-06.md`) and a census of
every seat record from round 10 to round 26 plus both of [USER]'s runs. The
census is a scratch read, not a count: packets name the cards a seat argued
about, not every reward passed. Prototype stage: nothing here is a number.

## 1. The question

The pool is 51 draftable rows and 2 basics. The brief's own shape (§7.4) is
about 60 of her own cards, and it says to stop at the number that is live.
So the question is not how to fill 60. It is which of the 51 earn a slot,
and what decision a new row would add that no current row asks.

## 2. GPT's review, fact-checked

Four implementation claims, all checked against the engine and the records.

1. **Grounded reads the board, not the quiet turn.** True. Round 18 changed
   "if none of your Bombs went off last turn" to "if you have a Bomb on the
   field" (`EB-516`) because Mines going off on the enemy's beat made the
   quiet turn nearly impossible: 7 of the 10 explosions in a Cook deck were
   Mines answering an attack. The fix made Grounded a decision again (round
   19) and also removed it from the cook-or-cash tension the brief's §4 built
   it for: a Bomb is on the field nearly every turn once Jumpy Dumpty is
   Innate. GPT's "detonate and replace keeps it running" is right. §5.
2. **Sparks 'n' Splash copies the largest Bomb without consuming it.** True,
   and ruled that way (R250 pick 1). The brief's §5.2 Rare is different: "at
   the end of her turn, set off a random enemy's Bombs", which is the
   rule-breaker (rule 7, nothing fires by itself). The built card is the
   brief's own failure mode in §9, "watch it rise", printed on a Rare. The
   one seat that held it called it "a dead card in its own deck" (round 15).
   That is the new fact a re-ask needs. §5.
3. **Blast Shield has no Retain.** True (`mark_return_to_hand`: "it discards
   at end of turn like any card"). The pass-two record's line that it is
   "never the card that was missing from the hand" overstates: it is
   repeatable within a turn, not present across turns. The record is a
   Prototype record and the sentence is corrected here, not there.
4. **Return to Sender converts all absorbed damage, not the card's 8.** True
   and deliberate in both engines (`block_absorbed`: "the charge is the whole
   absorbed amount and not the mark"). The face says "damage this Block
   absorbs"; a reader takes "this Block" as the 8. A Bomb 32 off one hit
   killed an elite in round 26. Text and limit disagree. §5.

Where I disagree with GPT: the "mischief and cleanup" direction (a package
around Confiscated) would be a fourth private language in a pool that the
checklist's seventh check already asks to keep open. Fish Blasting is fine as
a plain AoE with a deck cost, which is the third check's shape, and it needs
no package. Where I agree without reservation: test the opening bank at 3
against 1 on the same decks, and do not reprice the sinks at the same time.

## 3. Is Spark a real problem right now?

No. It is an artifact of reading Spark as a resource that should ration
detonators. It cannot, by design: a Spark-priced *Set off* refunds itself
from the explosion it causes (Pounding Surprise), and the brief's Spray loop
is built on exactly that refund (§5.2, "which mint the Sparks for the next
one"). Every "never scarce" read from round 23 to round 26 was a read of
detonators. The one binding case, round 23's deadlock, was a deck of
Spark-priced detonators with no Energy-priced one, and Countdown plus the
Innate Jumpy Dumpty closed it.

Where Spark should bind is on the purchases that do not refund: setup,
Block, cards, Energy. Until pass two there were two of those (Dig In, Powder
Charge) and both cost 1, which the refund covers. Pass two put six on the
sheet at 2 to 5 and round 26 read them once: they bind on opening turns and
work after. That is one read, and it is the first read of the economy that
has anything to buy. One asymmetry is worth naming because it is a feature:
Spray makes many small explosions and floods Sparks; Cook makes one big one
and starves. So Spray's surplus buys Block and cards, and Cook's payoff is
the number. The sinks were written for both; they will be Spray's.

So the order [USER] proposed is the right one: consolidate, add what is
missing, read it, and only then return to the opening bank. Pick 6 holds
PR #470's pick where it is.

## 4. The cuts: nine rows that add nothing a neighbour does not, and one redesign

Each line is the card, its nearest neighbour, and the evidence.

1. **Fwoosh!** (1 Spark, Set off 6). Pocket Match is the same card at 5 with
   Retain, and Retain is what the seats drafted it for ("the answer to the
   aura-timer-versus-shuffle problem", round 20). One point of damage is not
   a decision.
2. **Long Fuse** (1 Energy, Retain, Set off 6, escalation removed). A third
   Retained detonator beside Ka-pow! and Pocket Match; "the Retain is a lie
   told by the card frame" (round 17). Countdown is the Energy-priced exit.
3. **Quick Fuse** (1 Spark, grow 3, Set off). Pocket Match plus three damage
   on a Skill. Its bridge line in the brief's §5.4 passes to Pocket Match.
4. **Rapid Fire** (2 Energy, four random Set offs). "The card never worth
   playing" (round 11), "never once earned 2 energy" (round 17). Its idea,
   one Attack setting off several enemies, is Tinder Toss's (§5).
5. **Fireworks Show** (2 Sparks, Set off ALL). "A strictly worse Tinder
   Toss" (round 22); the comparison pass named the intervention as a merge
   or a cut. Merged into Tinder Toss (§5).
6. **Kindling** (grow on a foreign aura). Offered three times, passed three,
   never played; both seats read it as switching itself off in a Pyro deck.
7. **Catalytic Converter** (Power: a Spark per reacting explosion). The most
   condemned row in the pool ("dead on arrival", round 19; "wrong direction
   entirely", round 26): it pays the currency that never binds, in the loop
   least able to trigger it.
8. **Explosives Workshop** (Power: Bombs grow 1 more). Alice's Recipe owns the
   growth axis; "the same dead stat the cap had just shown me" (round 10),
   passed almost every time it was offered.
9. **Sugar Rush** (Rare, 2 Sparks, exhaust: 2 Energy, draw 1). Sparks into
   Energy is Sparkling Burst's job since R270; this is the draft-4 "Energy
   only at Rare" line that R270 lifted. Frequently `CANNOT BE PLAYED`.
10. **Powder Charge** (1 Spark, Bomb 6) is not cut but redesigned (§6): it
    is Pop! (free, Bomb 5) with a price. The seats loved its shape, a
    0-Energy placer bought with the bank, so the shape stays and the card
    changes.

Kept on purpose, against the "more of the same" reading: Sizzle, Perfect
Timing and Flash Point (damage, replay, economy; Perfect Timing is the most
praised card in the pool), Dig In beside Blast Shield (once against a bank
dump), Countdown (the plain Energy detonator; the sixth check allows plain),
Pocket Fireworks (pressure that leaves Bombs alone), Fish Blasting (§2).

After the cuts: 42 draftable rows and 2 basics. Cook 12, Spray 9, React 4,
defence 8, cards and Energy 6, Hexerei 3.

## 5. Four rows adjusted

1. **Grounded.** Default: "At the start of your turn, if you played no *Set
   off* card last turn, gain 4 Block and 1 Spark." This is the brief's
   quiet-turn rule with the round-18 trap removed: a Mine going off under an
   attacker is the enemy's doing, not a *Set off*, so the Cook deck's Mines
   no longer switch Grounded off. Cashing switches it off, which is the point.
2. **Return to Sender.** Default: the Bomb is capped at the card's own Block
   (8, 11 upgraded); the face keeps "this Block". The engine already carries
   the mark, so this is the narrow reading it was built to support.
3. **Tinder Toss** takes the brief's shape and Fireworks Show's slot:
   Common Attack, 0 Energy, 2 Sparks, "Set off ALL enemies. Deal 3 damage to
   ALL enemies." It ends the random-target complaint (round 11 to `EB-595`)
   and makes the Spray chain from §5.2 one card. Price is a D default.
4. **Sparks 'n' Splash** returns to the brief's rule-breaker: Rare Power,
   "At the end of your turn, *Set off* a random enemy." Something now fires
   by itself, the chain no longer needs a card in hand, and the Bomb is
   consumed, so it is not a second Alice's Recipe.

## 6. What the space is for: batch one, five rows

The decisions the pool does not ask yet, read off the checklist and the
seats' own words. Each row below adds one, and none reads Spark.

1. **Booby Trap** (Powder Charge redesigned; Common Skill, 0 Energy, 1
   Spark): "Place a Mine 5." The only single-target Mine. The decision is
   targeting by intent: the trap goes under the one about to swing.
2. **Tripwire** (Common Skill, 1 Energy): "One of your Bombs becomes a Mine."
   The cook-or-cash decision with a third answer: give up choosing when, and
   let the attacker choose. Cook's bomb becomes Cook's defence.
3. **Explosive Frags** (Uncommon Power, 1 Energy): "Whenever a Mine goes off,
   apply 2 Vulnerable to that enemy." The brief's §2 promised this card
   ("kept, re-keyed to Mines") and it was never authored. The Mine deck's
   signpost. The shipped Rare of the same name is hidden by the flag, as
   Sparks 'n' Splash's twin is.
4. **Where Did I Put It?** (Common Skill, 1 Energy): "Draw cards until you
   draw a *Set off* card." Every natural seat since round 21 named the
   detonator as the piece the draft has to find. This makes finding it a
   deck-building decision instead of a shuffle.
5. **Big Bounce** (Uncommon Attack, 1 Energy): "*Set off*. Explosion damage
   past the enemy's HP hits a random other enemy." Rule 3 (Jump) as a verb,
   Cook's answer to its named weakness (hallways), and the round-20 overkill
   reading ("the 10 had nowhere to go") answered by a card.

Three Mine rows because Mines are the kit's most praised idea (Mine Toss,
"the kit's best card by both seats' account") and the verb has one Common.
That takes the pool to 46 and 2 basics. Breadth past 50 goes where the
brief's §7.4 put it: the stand-in layer, where different decks want
different friends, which is GPT's companion point and a later sitting. No
Rare is added; the three rule-breakers stand.

## 7. Defaults applied (D and E), disclosed

- The price on Tinder Toss (2 Sparks) and every number on the five new faces
  is a starting point (D).
- The mischief package is declined (E); one line reopens it.
- Blast Shield's pass-two sentence is corrected here and nowhere else (E).
- Nothing is built. On the ruling, one Opus pass writes the cuts, the four
  adjustments and the five rows in both engines under one `EB` row, the
  doctrine door reads the adjusted and new faces, and round 27 reads the
  consolidated pool on one natural lane and one Mine lane.

## 8. Picks

1. **The cuts (§4).** (1) *All nine, and the Powder Charge redesign* [default]. (2) All but Fwoosh!, Quick
   Fuse and Explosives Workshop, held for one more natural read. (3) Your
   own list.
2. **Grounded's condition (§5.1).** (1) *"if you played no Set off card
   last turn"* [default]. (2) A threshold: "if your largest Bomb is 10 or
   more". (3) As built, a Bomb on the field.
3. **Return to Sender (§5.2).** (1) *Capped at the card's own Block, face
   unchanged* [default]. (2) The whole absorbed amount, face says "your
   Block", price 3 Sparks.
4. **Sparks 'n' Splash (§5.4; re-asks R250 pick 1 on the §2 fact).** (1)
   *The brief's rule-breaker: end of turn, Set off a random enemy*
   [default]. (2) As built.
5. **Batch one (§6).** (1) *All five* [default]. (2) The three Mine rows
   only. (3) Nothing until the cut pool is read.
6. **The opening bank, PR #470.** (1) *Hold at "as it is"; after batch one
   is read, one round compares 1 against 3 on the same decks and seeds with
   the sinks unpriced* [default]. (2) Rule 3 Sparks now. (3) Reprice the
   sinks now.
