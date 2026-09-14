Status: OPEN (four A picks, §9; paper only, no row moves until ruled)

# Klee pool consolidation: two cuts, three repairs, a shelf, and the slices the space is for

Written 2026-09-09 from [USER]'s notes, GPT's two reviews of the same day
and [USER]'s reply to the first draft of this packet, read against the
brief (`review/active/klee-brief-2026-09-01.md`, draft 4 + §18), the 53
`proto_ko_*` rows on `docs/prototype-surface.yaml`, the engines
(`tier0/engine/klee_overhaul.py`, `KleeOverhaulPowers.cs`), the comparison
pass (`review/records/klee-pool-comparison-pass-2026-09-06.md`) and a scratch
census of every seat record from round 10 to round 26 plus both of [USER]'s
runs. Packets name the cards a seat argued about, not every reward passed, so
the census is a read and not a count. Prototype stage: nothing here is a
number.

## 1. The question, and the order

The pool is 51 draftable rows and 2 basics. [USER]'s order for this phase:
cut only what is plainly redundant, repair the salvageable bodies, tag the
debatable rows as lower value and revisit them only if the pool needs the
space, and spend the design effort on new slices, playtested gradually and
deduplicated as they land. The first draft of this packet cut nine rows on a
standard of "one card owns each effect"; that standard was wrong, and GPT's
second review named four places where the evidence described an older card.
This draft is written to the order above.

## 2. GPT's reviews, fact-checked

Every engine claim in both reviews is true, and four corrections to my first
draft are recorded here so they are not re-found.

1. **Grounded reads the board** since round 18 (`EB-516`), because Mines
   going off on the enemy's beat made "no Bomb went off last turn" nearly
   impossible: 7 of 10 explosions in a Cook deck were Mines. That fix also
   took Grounded out of the cook-or-cash tension the brief's §4 built it for.
2. **Sparks 'n' Splash copies the largest Bomb without consuming it**, and
   that was [USER]'s own design (2026-09-02: automatic detonation "completely
   bricks the growth build"), refined to the largest single charge under R250
   after round 8's seats found the sum made banking always right. The first
   draft's "return to the brief" ignored that history. It stays as built.
3. **Blast Shield has no Retain**: repeatable within a turn, not present
   across turns. The pass-two record's sentence overstated it.
4. **Return to Sender converts the whole absorbed amount** by design in both
   engines; the face's "this Block" reads as the card's 8. Round 26's
   evidence was three Bombs of 12, 10 and 10 after a three-hit attack, not
   one Bomb 32 from one hit. The mismatch stands either way.
5. **Corrections to my first draft:** the Long Fuse quotation ("a lie told by
   the card frame") was about the escalating cost the comparison pass has
   since removed; Quick Fuse grows *every* Bomb on the target, so it is not
   Pocket Match plus three; Rapid Fire's repeated Set offs can cash charges
   Chained Reactions plants mid-card, which a single Set off ALL cannot; the
   mischief direction is built from shared mechanics (Exhaust, discard,
   retrieval) and is deferred, not refused.

## 3. Spark: hold, and read the right question

Refunds are intentional: a Spark-priced *Set off* pays for itself from the
explosion it causes, so Spark will never ration detonators, and every "never
scarce" read from round 23 to round 26 was a read of detonators. The open
question is the one GPT states: whether the non-refunding purchases (Block,
cards, Energy, setup) compete for the bank and are reachable in the decks
that want them. Pass two gave them real prices and round 26 read them once.
One hypothesis for the next rounds, not a conclusion: Spray floods Sparks and
Cook starves, so the sinks may reach one loop and not the other; [USER]'s
own Spark-supported Cook defence was fun and inconsistent, which is the
case to watch. PR #470's opening-bank pick stays where it is until the
consolidated pool has a read, then one round compares 1 against 3 on the
same decks with the prices unchanged.

## 4. Two cuts and one redesign

1. **Fwoosh!** (1 Spark, Set off 6). Pocket Match is the same card at 5 with
   Retain, and Retain is what the seats drafted it for. One point of damage
   is not a decision.
2. **Fireworks Show** (2 Sparks, Set off ALL) merges into Tinder Toss (§5.3).
   "A strictly worse Tinder Toss" (round 22); the comparison pass already
   named the merge.
3. **Powder Charge** (1 Spark, Bomb 6) is Pop! with a price. Its shape, a
   0-Energy placer bought from the bank, is what the seats praised, so the
   shape stays and the card becomes **Booby Trap** (§7, batch one).

## 5. Three repairs

1. **Grounded.** "At the start of your turn, if you played no *Set off* card
   last turn, gain 4 Block and 1 Spark." The brief's quiet-turn rule with the
   round-18 trap removed, and two interactions stated so the round reads
   them: a Mine answering an attack is not a *Set off* card, so Cook's Mines
   no longer switch Grounded off; Sparks 'n' Splash is not a *Set off* either,
   so a deck holding both is paid every turn for not cashing by hand. That
   pairing is either an enjoyable Rare engine or the brief's "watch it rise";
   round 27's Cook lane holds both and says which.
2. **Return to Sender.** The conversion is capped at the Block the card
   granted, as one allowance spent across every hit that turn (8, or 11
   upgraded, and whatever a Block modifier made of it), never an independent
   cap per hit. The engine's mark already carries the allowance; the face
   keeps "this Block" and is now true.
3. **Tinder Toss** takes the brief's shape and Fireworks Show's slot: Common
   Attack, 0 Energy, 1 Spark, "*Set off* ALL enemies. Deal 3 damage to ALL
   enemies." It ends the random-target complaint (round 11 through `EB-595`)
   and makes the Spray chain of §5.2 one card. The price is a D default at
   1 Spark because it replaces the pool's 1-Spark multi-target card and early
   access is what the round should read; Rapid Fire keeps the repeated-Set-off
   line.

## 6. The lower-value shelf

Six rows stay in the pool, tagged here as the first to go if a slice needs
the space, each with the read that would clear or condemn it. The shelf is
re-read at every pool pass and nothing on it is cut before then.

| Row | Why it is on the shelf | The read that settles it |
|---|---|---|
| Long Fuse | Repaired (escalation off) and unread since | One natural lane holding it beside Countdown: does the Energy-priced Retain get held for a turn |
| Rapid Fire | "Never worth playing" twice; targeting fixed since | A lane holding it with Chained Reactions: do the later hits cash new charges |
| Explosives Workshop | Passed almost every offer | A Cook lane offered it before Alice's Recipe: is +1 growth a pick or a stat |
| Sugar Rush | Often unplayable at 2 Sparks; one-shot Energy | Held beside Sparkling Burst in one deck: which gets paid, and when |
| Kindling | Never played; reads as self-defeating in a Pyro deck | The React assembled lane (round 24's hypothesis) with an applier in hand |
| Catalytic Converter | Condemned in three rounds, all without an applier | The same React lane: is a Spark per reaction ever the reason to react |

## 7. The slices: what the space is for

The main work of this phase. Each slice is a decision the pool does not ask
yet, drafted to three or four rows, built alone, read on one natural lane
and one assembled lane, and deduplicated against its neighbours as it lands.
Batch one is drafted; the rest are named so [USER] can order them.

**Batch one, Mines (three rows).** Mines are the kit's most praised idea
("the kit's best card by both seats' account", Mine Toss) and the verb has
one Common.

1. **Booby Trap** (Common Skill, 0 Energy, 1 Spark): "Place a Mine 5." The
   only single-target Mine; the decision is which enemy is about to swing.
2. **Tripwire** (Common Skill, 1 Energy): "One of your Bombs becomes a
   Mine." A third answer to cook-or-cash: keep the charge, and let the
   attacker choose the moment. Manual *Set off* still cashes it.
3. **Explosive Frags** (Uncommon Power, 1 Energy): "Whenever a Mine goes
   off, apply 2 Vulnerable to that enemy." The Mine deck's signpost, the card
   the brief's §2 promised. Round 28 reads whether the Vulnerable lands
   before the damage that matters or after it; the shipped Rare of the same
   name is hidden by the flag, as Sparks 'n' Splash's twin is.

**Slice two, finding and overflow (two rows, redrafted on GPT's notes).**
Every natural seat since round 21 named the detonator as the piece the draft
has to find, and round 20 read overkill as "the 10 had nowhere to go".

4. **Where Did I Put It?** (Common Skill, 1 Energy): "Look at the top 4
   cards of your draw pile. Put one *Set off* card from them into your hand
   and the rest on the bottom." Bounded, so detonator density stays a deck
   decision and a hand of Ka-pow! cannot draw the pile.
5. **Big Bounce** (Uncommon Attack, 1 Energy): "*Set off*. Explosion damage
   past the enemy's HP is dealt as Pyro to a random other enemy." Rules:
   the overflow is one plain Pyro hit, it does not *Set off*, it does not
   bounce again, and Strength and Vulnerable apply once at the source and
   never again at the destination. It salvages damage; Jump (rule 3)
   preserves charges; the two do not overlap.

**Slice three, React's own route.** The comparison pass found no natural
lane ever drafted an applier before a React row. Within the law (off-element
comes from companions), Klee's own cards can make the companion arrive:
rows that read any Companion play, not only Hexerei, so different decks want
different friends. Drafted after batch one is read.

**Slice four, Spark-supported Cook.** Cook cards priced in Sparks that pay
for holding, the defence [USER] enjoyed and found inconsistent. Drafted
after the sinks' second read says whether they reach Cook at all.

**Slice five, mischief and cleanup.** Exhaust, discard and retrieval as
shared mechanics, with Confiscated as one hook and not the language.
Deferred; the direction is open.

No ceiling is asserted. The brief's §7.4 shape (about 60 of her own cards,
stop at the number that is live) stands, the stand-in layer is breadth of a
different kind and does not substitute for reward-pool breadth, and the pool
grows one slice at a time as ideas earn slots.

## 8. Staging, disclosed (E)

One approval, two builds, so a change in the reads can be attributed. Stage
one: the two cuts, the redesign and the three repairs, under one `EB` row,
read by round 27 on a natural lane and a Cook lane holding Grounded, Return
to Sender and Sparks 'n' Splash. Stage two: batch one, read by round 28 on a
natural lane and a Mine lane. Each new or changed face goes through the
doctrine door first. Every number on a face is a starting point (D). The
lower-value shelf is the mechanism [USER] named and is applied as written.

## 9. Picks

1. **The cuts (§4).** (1) *Fwoosh! and Fireworks Show cut, Powder Charge
   redesigned* [default]. (2) Also Catalytic Converter, now. (3) Your list.
2. **Grounded (§5.1).** (1) *"if you played no Set off card last turn", with
   the Mine and Splash interactions stated and read* [default]. (2) A
   threshold: "if your largest Bomb is 10 or more". (3) As built.
3. **Return to Sender (§5.2).** (1) *Capped at the Block the card granted,
   one allowance across the turn, face unchanged* [default]. (2) The whole
   absorbed amount, face says "your Block", price 3 Sparks.
4. **Slice order (§7).** (1) *Mines, then finding and overflow, then React's
   route, then Spark-supported Cook, then mischief* [default]. (2) React's
   route second, since it is the loop with no natural route. (3) Your order.
