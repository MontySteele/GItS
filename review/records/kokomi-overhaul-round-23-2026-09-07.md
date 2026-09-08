Status: RECORD (was OPEN, no pick; the defaults it names were applied; moved 2026-09-08 under R267)

# Kokomi round twenty-three: the order written is a decision, two of the eight are dead, and the cap was never reached

Written 2026-09-07, evening, under the Prototype loop. Four blind Opus seats
on `0.2.2991+proto` (main `778b8e8a`, the pool pass two of `EB-643`), two
lanes at a time. Records in `review/qa/kokomi-round-23-2026-09-07/`:
`opus-defence-act1.md` (lane 1, six Block and Dusk rows granted),
`opus-attack-act1.md` (lane 2, six single-target and order rows granted),
`opus-cap-act1.md` (lane 1, six immediate rows granted, `GITS_KOKOMI_PLAN_CAP=2`
on the embark), `opus-natural-act1.md` (lane 2, nothing granted). All four
stopped on the action budget with every fight won (five, five, six, five
fights; floors 6, 10, 9, 10). Prototype stage, Guardrail-7; a granted deck is
one no generator produced and nothing here is comparable to another run.

## 1. The hypothesis

"With rows that make the queue's order matter, rows that spend the queue, and
two Plans that land at dusk, a seat names a turn where the order it wrote the
Plans in was a decision, a turn where it cancelled, cashed or re-aimed a Plan
on purpose, and a hit it covered at dusk rather than dawn; the three
assembled decks want different rewards; the natural lane meets at least one
of the eight; and the lane under the cap names the cap as a choice, not a
wall."

Order: **named, twice, on the turn.** Cancel, cash, re-aim: **never, on any
lane.** Dusk: **named, twice, and it kills the face-up half.** Different
rewards: **yes.** The natural lane met **none** of the eight. The cap: **not
reached**, so not read.

## 2. What the round found

**The order written is the decision the pass was for.** Lane 2: "Wrote three
Plans, in this order: Scout Ahead, Kurage's Oath, Pincer. This was the fight's
real decision"; "In fight 1 turn 2 I wrote Scout Ahead first on purpose and
got 2 cards; written last it is a blank"; the elite turn: "Feint's Plan 10,
times 2 (Opening Gambit), times 1.5 (Vulnerable) = 30", worked out on the
screen and delivered. Lane 1 (cap): "Writing Exposed Flank before Kurage's
Oath turned a 7 into a 10, and the log said so in words." The auto-pilot
complaint has its first counter-example: a free turn on these decks is a
sequencing puzzle, and the seats say so unprompted.

**The queue was never spent.** Second Thoughts was drawn three times on the
defence lane and played zero: "a fix for a mistake I never made, because
Plans are written and resolved inside two turns and nothing surprised me hard
enough to want one back." Ebb Tide, three draws on the cap lane, "a strictly
dead card every time, because it is only live in the situation you spent the
previous turn trying to create." Converging Tide, lane 2: "Jaxfruit was
already the front, so the redirect was redundant"; never played. The resource
path's premise, that a board changes between writing and morning often enough
to want a take-back, did not hold in act 1 with two-turn queues. It may hold
under the cap, where a queue outlives a morning; that is the one place it is
still worth reading.

**Dusk works and its face-up half is dead.** Lane 1: "a Plan that resolves
before the enemy acts rather than after collapses the usual 'planning costs
you a turn of defence' problem"; the Dusk Weak was written "specifically to
feed its Weak to the Artifact"; and "Night Watch face-up is 3 Block; as a Dusk
Plan it is 5 Block plus a Weak plus 2 relic damage, resolving before the enemy
acts, for the same energy. Breakwater is 4 vs 7 the same way. I never once
played either face-up." The dawn line is bigger than the face because it
waits a turn; the dusk line waits one enemy action and is still bigger, so
the choice on the card is gone. The trial says the keyword is right and the
numbers are wrong.

**Second Wave written alone reads as nothing.** "It produced no Block, the
log said 'Second Wave: no enemy lost HP', the buff list showed nothing
pending, and the very next Plan I wrote the following turn came out
un-doubled"; with a Plan behind it in the same morning "it works perfectly
(proved twice)." The rule is as designed (the rider lives in one drain) and
the face does not say so; the seat calls it "the round's clearest defect."
The same record notes that a Block-then-Plan face "reads as two sentences,
not as an either/or", the Plan rule's oldest legibility gap on a new row.

**The three assembled decks wanted different rewards.** Lane 2 took a second
Opening Gambit over Diona and put Sown on it; lane 1 (defence) took Sara and
Kaeya for reactions and never drafted a Block card; the cap lane took Kaeya
and Nereid's Ascension. Each lane's happiest draw was its own engine piece
(Opening Gambit; Amber; Kaeya).

**The natural lane met none of the eight**, and its answers are the kit's
standing ones: the face-or-Plan split "every turn, on the turn" and element
ordering inside a turn "the most satisfying thing in the kit". Four lanes,
four seats, one dead card named by all: Defend.

**The cap lane never wrote three Plans in a morning**, so the cap did not
engage and the record does not mention it; the deck given to it (immediate
rows with selective Plans) was the wrong deck for reading a cap. Nothing in
the lane's log proves the env var reached the game either; that acceptance
is owed before the cap is read at all.

**Two rules the screen does not print.** On three lanes a Shrink on Kokomi
reprinted her hand ("Kurage's Oath, 2") and the same card carried out by the
jellyfish dealt 7: her Strength folds into a Plan as it is written, and a
damage debuff applied afterwards does not follow it. As designed
(`kokomi_plan.hers`), and unsaid. And the page's note "the number on its
buff is how many are written" was read against the Bake-Kurage's own buff,
which is a presence marker pinned at 1; the count is the separate Plan badge.

**Smaller.** The Sown enchantment's face prints `Gain [Energy]`, brackets
and all, on the page (the markup fold leaves an unpaired token). The page's
"The other side" block printed twice on one screen. Both lanes that met the
Casket found its hit by arithmetic, not by a line.

## 3. What the round did not test

The cap (§2). Act 2. Path 4 (the shaken queue). A natural deck's draft of the
eight, since the offer never showed one in four lanes of act 1.

## 4. The smallest interventions, ranked

1. Second Wave's face gains "if a Plan follows it this morning", and the
   ledger line says "no Plan followed" when it does not (`EB-645`).
2. The Dusk lines re-priced to the face: Breakwater 4 now, Dusk 5; Night
   Watch 3 now, Dusk 3 and 1 Weak. Timing is the whole value (`EB-646`).
3. The Plan tip or panel says a written number does not change with later
   debuffs on Kokomi (`EB-647`); the count note names the Plan badge
   (`EB-648`).
4. Ebb Tide leaves the pool; Second Thoughts is held for the cap round only
   (`EB-649`).
5. The cap read for real: a many-small-Plans deck (Ripple, Tide Chart,
   Vanguard, Read the Field, Stolen Chapter, Well Laid) on the cap lane,
   after a scenario proves the env var reaches the lane's game (`EB-650`).
6. The page's `[Energy]` fold and the doubled block (`EB-651`).

## 5. Defaults applied (D and E), disclosed

Items 1 to 6 above are D and E defaults and are applied without a pick: the
first four are prototype rows and faces under the pool-first path R265 set,
the fifth is process, the sixth is page hygiene. No shipped number moves. The
carry-out rule (the cap) stays undecided, as R265 said it would be, until a
round reads it; the re-ask trigger is the cap lane in §4 item 5.
