Status: OPEN (no pick; the defaults in §5 are applied)

# Klee round nineteen: Grounded pays a cook and asks a question, and the Spark bank still outruns its sinks

Written 2026-09-05, under the Prototype loop. Two blind Opus seats on
`0.2.2729+proto` (round-18 head `a280c4f3`, fixers K and L in: Grounded
keyed to a Bomb on the field, random Set offs preferring a bombed body,
the Spark spend and the killing-blow reaction fixed). Records:
`review/qa/klee-round-19-2026-09-05/opus-arm-act1.md` (lane 1, assembled)
and `opus-natural-act1.md` (lane 2, natural). Prototype stage, Guardrail-7.

## 1. The hypothesis

"With Grounded keyed to a Bomb on the field and random Set offs preferring
a bombed body, a Cook deck's quiet turns pay on most turns and Tinder Toss
stops stranding the Spark loop; the seat wants Grounded rather than
cutting it first."

**Assembled deck** (lane 1, seed `BTJFUT7XQSQX`, Ascension 0): Grounded,
Tinder Toss, Rapid Fire, Chain Fuse, Pop!, Careful Arrangement added. 112
of 120, four fights and the Terror Eel elite won, 33 of 62. **Natural run**
(lane 2, seed `8BA9UUG794AR`, Ascension 1): 119 of 120, floor 11, five of
five including both elites, 40 of 68, zero HP lost in three fights.

## 2. What the round found

**Grounded, adjusted, is a decision now.** Logged every turn: paid three
times, failed twice, and both failures were on the turn after the seat had
detonated everything, which is the card's price rather than its trap. The
seat's best turn of the round was the one the brief wrote the card for:
"Run Away! and Grounded pull in opposite directions, one needs a Bomb to
go off this turn, the other needs one standing next turn, resolved by
detonating a Mine then placing a fresh Bomb after." Two rounds ago two
seats said "cut it first"; this seat played it three times and named it in
the round's best decision. **The first half of the hypothesis holds.** What
it lacks is a line: the two failures "printed no near-miss line, I caught
it only by diffing my own Block" (`EB-533`).

**The random Set off, half tested.** Rapid Fire went into a bombed body
twice, both lethal. Tinder Toss was played twice, both into a body with no
Bomb, but both on a one-enemy board where no Bomb stood anywhere, so the
rule had nothing to prefer. Not exercised on a hallway; carried, not
concluded.

**The Spark bank outruns its sinks, a fourth reading.** The assembled seat
ended fights on 5, 6 and 5 Sparks "with nothing able to spend them", and
both its card picks were sinks (Fwoosh!, Fireworks Show); Catalytic
Converter "proposes to make more, which is why it was dead on arrival". The
natural seat's answer was Dig In and Dig In+, after which "Bang Bang!+ at
2 Sparks against Dig In+ at 1 off an income of 1 at start plus 1 a
detonation is the kit's most interesting tension". The reading is access:
the sinks exist (Dig In, Fwoosh!, Pocket Match, Stoke the Fuse, Fireworks
Show) and a seat that does not draft one is stranded. The loop's smallest
intervention is a rarity or an offer weight, not a card; §4.

**Careful Arrangement, cut candidate.** Drawn three times, played never:
"merging N Bombs into one destroys N minus one growth ticks a turn,
collapses the multi-hit Set off, and appears to convert Mines into plain
Bombs". Round 18's Cook seat read the opposite on the Mine question ("the
body line said so"), so the two seats disagree on what the card does
(`EB-534`), and the face says only "as one Bomb". The displaced-row reading
the loop asks for: the card's price (growth ticks) is real and its payoff
(+5 and a single big hit for Big Badda Boom) reads as smaller than the
price to one seat and worth it to another.

**Turn one, a ninth round.** Assembled lane: Ka-pow!, Tinder Toss and Chain
Fuse in the opening hand, three cards that reference Bombs and no placer,
"Chain Fuse was strictly inert". Natural lane: two Strikes and three
Defends, "the kit arrived on turn 2 when Jumpy Dumpty and Ka-pow! came up
together, and either alone is filler". The round-17 pick (PR #398).

**What read true.** "Nothing contradicted its printed text": every predicted
number landed (27 off the previewed Vaporize, 31 to the Shriek line, 25
into 24 HP). The Bomb status line ("Bombs here: 7 / 7 / 9, including 2
Mines") "is the best writing in the kit; I built three plans directly off
it". Ordering: Ka-pow! before Razor to spend the Pyro aura on Overloaded,
the third Attack last for Razor's refund. Detonate-now-versus-grow
changed by enemy (Hardened Shell made growth worthless; the seat named
Jumpy Dumpty on turn one "a 9-HP trap" there).

**Legibility, five rows.** Grounded's silent failure (`EB-533`). The
merge's effect on a Mine (`EB-534`). The Hexerei line on a Klee run says
"cards of hers pay" and not what (`EB-535`). Round 18's new headline clause
"in 1 hit for as many Sparks" was "never comprehensible", and the Bomb tip
("goes off only when Set off") sits above the Mine tip that says otherwise
(`EB-536`). Freminet's face references Shatter with no glossary entry when
Frozen is unreachable (`EB-537`). The Doors of Light and Dark event never
named the two cards it upgraded (`EB-448`, cited). Thorns off a Bomb was an
ambiguity the seat routed around at 15 HP ("every card hit is one" against
"Not an Attack"); `EB-521` built the Thorns line this morning and the
deployed build carries it, so the next seat reads the answer.

**Companions.** Assembled: Barbara taken, "the only Hydro, she alone made
the entire reaction ruleset reachable"; Gorou twice and Sucrose declined.
Natural: Razor taken, Yae Miko, Noelle, Bennett, Freminet declined; "the
fourth-choice rule held every time".

## 3. What the round did not test

The act-1 boss on either lane. Tinder Toss on a hallway. Long Fuse, Pocket
Match, Bombs Away!, Fireworks Show played, Kindling, Flash Point,
Vermillion Pact, Split Charge, All of My Treasures!. Nothing here is a
strength reading.

## 4. The smallest interventions, ranked

1. **Grounded's line** (`EB-533`): a tip, before any number.
2. **Spark sinks by access, not by card:** Dig In and Fwoosh! are Common
   already; the reading is that a seat which never sees one strands the
   bank. The smallest intervention is the Neow bundles and the act-1 offer
   weights carrying a sink the way the round-17 pick's option 3 carries a
   placer. Recorded; it rides on that pick's ruling.
3. **Careful Arrangement:** pin what it does to a Mine and say it
   (`EB-534`); the cut question waits on a seat that reads the face right.
4. **Tinder Toss on a hallway:** round 20's assembled lane.

## 5. Defaults applied (D and E), disclosed

- **`EB-533` to `EB-537` minted; `EB-448`, `EB-521` cited.**
- **Grounded and the random Set off stand as adjusted**; the first read is
  in §2.
- **Careful Arrangement stays** until `EB-534` says what it does.
- **The two records are the round's evidence.**
