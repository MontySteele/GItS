Status: OPEN (no pick; one adjustment to the audit door, two rows held)

# Klee pool comparison pass one: what the ten rows displaced, rounds 17 to 23

Written 2026-09-06 under the Prototype loop (`operations/stage-gate.md`,
*The loop inside Prototype*: "a comparison pass on what an expansion
displaced precedes any further addition to that pool"). Pool pass one
(`review/active/klee-pool-pass-2026-09-05.md` §2) added ten rows and owed
this: for each, would a drafter still take its nearest neighbour, did it
make another strategy unnecessary, and did it thin the odds of finding an
essential piece. The evidence is the seven round packets 17 to 23 and the
fifteen seat records under `review/qa/klee-round-17-2026-09-05/` through
`review/qa/klee-round-23-2026-09-06/`, and nothing else; every count below
is a grep of those files. Prototype stage: no number here is quotable, and
the pool stays 45 rows.

## 1. Row by row

**Pocket Match** (Common, 0 energy, 1 Spark, Retain, Set off 5). Granted
once (round 18 Spray). Offered eight times: taken five (r18 Cook reward,
"the exact fix for fight 1 turn 4"; r19 arm, a second copy "for
reliability"; r20 natural, "Retain is the answer to the aura-timer-versus-
shuffle problem"; r23 natural, "three separate turns holding a fat Bomb with
nothing to detonate it"; r23 arm, in a Neow bundle), passed three (r17 Neow
at 1 Spark, r20 shop, r22 Gorge). Played on every lane that held it. Its
nearest neighbour, Fwoosh! (1 Spark, Set off 6, no Retain), was still taken
(r19 arm, r20 natural) and still played as the tempo line, so the two split
on Retain against damage and both are drafted. One counter-reading stands:
a retained card "I cannot pay for is not saved for a better moment, it is a
dead card occupying a slot" (r18 Spray). **Earns its place; Fwoosh! not
displaced.**

**Bombs Away!** (Common Attack, 1 energy, 3 to ALL, Bomb 2 on ALL). Never
granted. Taken twice (r18 Spray reward, "more energy-priced bomb placement,
and specifically an AoE one"; r23 shop), passed once for Dig In (r22 b).
Played as "a rate" against a per-turn damage cap on the r21 elite, and held
on purpose on a foreign aura in r23 ("a hit of a different element consumes
the aura"). Rejected once against Amber, Fiery Rain because 3 does not kill
a 7-HP minion. Mine Toss, its Skill neighbour, was still taken over it
(r18 Spray). **Earns its place**, and it is the Attack placer the Smoggy
reading asked for.

**Fish Blasting** (Common Attack, 1 energy, 5 to ALL, a Confiscated).
Granted once (r17), three plays, "good immediately". Offered three times,
passed three, each time to a detonator or to Fish-Flavored Bait. Plain Cook
pressure loses every contest with a detonator, and that is the starter's
detonator shortage (R262, held), not the card. **Earns its place; no
reading against it.**

**Flash Point** (Uncommon Attack, 1 energy, Set off 7, tempo rider).
Offered once, taken over Pocket Fireworks+ "because cashing Bombs is the
kit" (r20 arm); "every turn it appeared it was the correct play". One seat.
Its one reading is about overkill: "Set off. Deal 10" and the 10 "had
nowhere to go" when the Set off killed, which the seat called "probably
correct behaviour" and a face that "gives no hint that the first half can
eat the second" (r20 arm, finding 4). Recorded, no row: `EB-595`'s shape
(each clause its own line in the log) is the surface that answers it.
**Earns its place.**

**Split Charge** (Uncommon Skill, 1 energy, split the largest Bomb).
Offered once (r23 arm, a Neow bundle), played on a single-enemy board and
named "the best-designed decision of the run" against a second Strike; a
brick with no Bomb to split on the elite's fifth turn. **Earns its place.**

**Long Fuse** (Common Attack, 1 energy, Retain, Set off 6, costs 1 more
each turn held). Granted once (r17, five plays), offered twice, passed
twice. Three readings on one line: "never a decision ... the Retain is a
lie told by the card frame" (r17 arm); passed "because Retain plus an
escalating cost is a card that punishes the exact hand-holding the rest of
the kit rewards" (r18 Spray); passed without comment (r22 b). The pool pass
wanted "a card that stays in hand" for hold-or-fire (§1); Pocket Match
delivered that at a Spark, and Long Fuse's escalation is what the seats
read as the reason not to keep it. Against its nearest neighbour, Sizzle
(1 energy, Set off 6, +6 on a reaction), Long Fuse trades the reaction line
for a Retain the seats do not believe. Interventions in the stage-gate
order: a display fix answers nothing, because the r17 objection is that the
trade never favours holding (+4 Bomb against +1 energy), not that the trade
is hidden. **The smallest intervention is the existing card adjusted: the
escalation comes off** and the face reads "Set off. Deal 6 damage. Retain."
That makes it Pocket Match's Energy-priced twin, and the Energy-priced exit
the r23 assembled deadlock lacked; Sizzle keeps the reaction line, Countdown
the draw, Ka-pow! stays the free one. The counter-reading is the audit's
own: Long Fuse FOLLOWED C2 because "retaining it once raises its cost from
1 to 2 energy: keeping the detonator carries a binding price"
(`review/records/card-audit-2026-09-04.md`, §5.3 reply 1), and Held Tide was
WITHDRAWN on C1 because "Retain waits out the dead turns". **The adjusted
row goes to the audit door before any tester sees it**, through
`understudy.seat review` on the Codex bridge, which needs the local
machine; it is not built here.

**Fireworks Show** (Uncommon Skill, 0 energy, 2 Sparks, Set off ALL).
Granted once (r23 arm). Offered five times: taken twice ("to buy a sink for
surplus Sparks", r19 arm; "the only card offered that converts stored Bombs
into damage", r22 b), passed three. Two reads that disagree. The r22 b
natural lane never played it in four fights: "a strictly worse Tinder Toss
whenever there is one enemy, which is most of Act 1", "no niche in Act 1
that another card does not cover more cheaply", and `CANNOT BE PLAYED` four
times. The r23 assembled lane set off four Mine 3 with it for 12 damage and
four Sparks on a hallway, and then held it as the only detonator in hand,
priced out, at the elite. One round each way is not a finding (the pool
pass §1 rule on Sparks 'n' Splash). **Held.** The next natural lane that
drafts it decides, and the intervention if the r22 read repeats is named
now so it is not re-found: a merge with Tinder Toss or a cut, not a price,
because both seats that took it took it as a two-Spark sink.

**Kindling** (Common Skill, 0 energy, grows Bombs on non-Pyro auras).
Offered three times, passed three, never played. Two seats read the clause
as switching itself off: "in a deck where every set-off applies Pyro
appears to switch itself off" (r20 arm shop) and "anti-synergistic with the
deck's core action" (r23 arm shop). That is Catalytic Converter's shape by
design (pool pass §1), and the +2 floor was not valued by either. **Held**;
the finding is the archetype's, §2.

**All of My Treasures!** (Rare). Offered twice: taken at Neow (r22 a, a run
that ended at that screen on `EB-594`), passed for Razor (r20 arm). Never
played. **No evidence.**

**Vermillion Pact** (Rare Power). Offered once at Neow, rejected as
"unpriceable ... I was asked to price a rare against a mechanic the screen
would not name" (r22 a). That is the reaction glossary (`EB-410`), not the
card. **No evidence on the card.**

## 2. What the pass displaced, and did not

- **No strategy became unnecessary.** Fwoosh!, Mine Toss, Sizzle and
  Tinder Toss were all still drafted beside their new neighbours, and the
  seats that chose between them said why.
- **The odds of the essential piece.** Two natural seats said the
  detonator is the piece the draft has to find: "four card rewards passed
  before one was offered that I judged worth the slot over an engine piece"
  (r21), "a starting deck with exactly one detonator in ten cards is why I
  spent three of my six card picks on detonators" (r23). That is the
  starter's shortage, ruled R262 to hold; the pass's three detonators
  (Pocket Match, Long Fuse, Flash Point) are what the draft finds, and
  every natural lane found one by its third fight.
- **The React archetype has no natural route yet.** In seven rounds no
  natural lane drafted an applier Companion before a React row, and both
  React rows the seats met (Kindling, Vermillion Pact) were passed as
  self-defeating or unreadable. The brief's React hypothesis is untested,
  not failed, and the assembled deck is the instrument for that (stage-gate:
  "whether the strategy is interesting at all"). **Round 24's hypothesis:**
  "A React deck that leads with an applier Companion (Rosaria or Kaeya
  granted with Kindling, Flash Point and Vermillion Pact) makes Kindling's
  clause and the Pact's re-react read as decisions, and changes which
  Companions Klee wants from the rewards." One assembled lane and one
  natural lane, as every round since 17.

## 3. Interventions, in the stage-gate order

1. **An existing card adjusted:** Long Fuse's escalation off (§1), to the
   audit door, then built in both engines and read by the next round that
   offers it.
2. **Access:** nothing proposed; the React question is a round-24 assembled
   hypothesis, not a row.
3. **Held:** Fireworks Show (one read each way) and Kindling (no route).
4. **Nothing added.** The pool stays 45; a second addition waits on this
   pass's holds resolving.

## 4. Defaults applied (D and E), disclosed

- The Flash Point overkill line is recorded as a reading and mints no row.
- Round 24's hypothesis is drafted here (E), for the seats when the machine
  is back.
- No register row minted, no number moved, nothing deployed.

No pick.
