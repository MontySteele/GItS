Status: OPEN (no pick; the defaults in §6 are applied, two of them after the doctrine read in §5)

# Klee round eighteen: Cook and Spray on the same relic, and the Spark ledger read turn by turn

Written 2026-09-05, under the Prototype loop. Two blind Opus seats on
`0.2.2696+proto` (round-17 head `2394745c`: the pool passes, fixers I and
J). Records: `review/qa/klee-round-18-2026-09-05/opus-cook-act1.md` (lane 1,
the Cook set granted) and `opus-spray-act1.md` (lane 2, the Spray set
granted). Prototype stage, Guardrail-7. The round-17 starter pick (PR #398)
is unruled, so the starter is unchanged on both lanes.

## 1. The hypothesis

"On two seeds, an assembled Cook deck (Grounded, Stoke the Fuse, Chain Fuse,
Careful Arrangement, Big Badda Boom, Pop!) and an assembled Spray deck (Mine
Toss twice, Fwoosh!, Tinder Toss, Pocket Match, Pop!) reach the same floor
with different reward wants; if the Spray deck runs on Sparks alone and the
Cook deck's Sparks come from Mines, the relic's incentive is the finding and
not the pools." Each seat logged Sparks held at the end of every turn.

**Cook** (lane 1, seed `SX9ZHGZ3WXN5`, Ascension 0): 120 of 120, floor 12,
five of five fights won and two turns of a sixth, 29 of 62 HP. **Spray**
(lane 2, seed `PYX0CB1JAWPK`, Ascension 1): 120 of 120, floor 12, six of
six, 26 of 62. Same floor, no deaths, different decks.

## 2. What the round found

**The ledgers.** Cook ended its turns on 1 to 3 Sparks, 1 on most of them,
and "anything go off?" was yes on 10 of 19 logged turns, seven of those on
a Mine firing on the enemy's beat or Ka-pow! collecting; Grounded fired
once in five fights, "on a turn I had already conceded". Spray ended its
turns on 0 to 7, ran dry (0) on four opening turns with Spark-priced cards
in hand, and sat on 4 to 7 with an all-Energy hand at the end of fights 4
and 5, "a full battery visibly evaporating at the end of combat". **The
hypothesis is confirmed in both halves:** the relic pays Spray through
explosion count and pays Cook through Mines, and the Cook payoff that the
brief wrote for the quiet turn (Grounded) paid once. Both seats named the
relic's shape unprompted: Spray "found the core loop on turn one of fight
one" (a Spark-priced Set off into a bombed body costs nothing net); Cook
called Grounded "a trap in its own deck", the second seat in two rounds to.

**Both plans are real, and both seats say the kit's best decisions are the
same three.** Assembly order (Cook fight 2 turn 1: Pop!, Stoke, Careful
Arrangement, Big Badda Boom for 38; fight 5 turn 3: Barbara, Chain Fuse,
Ka-pow! into a Vaporize for 45 through 7 Block). Bank or spend (Spray fight
5 turn 1: place three Bombs, deal nothing, take 8, cash 52 next turn, "the
best decision in the round"; fight 6 turn 1 the mirror, spend now because
the Ship is about to hand you Dazed). Leave the enemy alive for its own
Mine (Spray fights 2 and 6, Cook fight 6 turn 1). The draft was sharpest on
Spray, because the deck "arrives with a visible economic flaw, all attacks
priced in Sparks and one Spark of income", and the seat bought Sizzle for
25 gold as the only energy-priced detonator and "won three fights" on it.

**Reward wants differed, which is what the hypothesis asked.** Cook wanted
Set off cards after fight 1 wasted a Bomb 12 for lack of one ("every reward
pick and both shop purchases were about that one hole"); Spray wanted
energy-priced attacks and then Spark sinks (Sizzle, Raiden, Amber; Stoke the
Fuse over Razor "answering my Sparks have nowhere to go"). Two decks on one
pool asking for different cards is the depth reading the loop names.

**What the pool pass displaced, second reading.** Random Set-off cards break
the Spark loop: Tinder Toss "the one I never wanted", its random picks hit
the bomb-less body and stranded Pocket Match unplayable; Rapid Fire "spends
a mine early that would have fired free on the enemy's beat" and was round
17's least-wanted card. Sorry, Jean... bought and never played. Careful
Arrangement and Chain Fuse "worse Strikes" against a small single enemy.
Pocket Match's Retain read "as a liability" when unpayable; Ka-pow!'s Retain
"was not close" as the happiest draw.

**What read true.** Careful Arrangement preserves Mine status when it
merges (the body line said so; the card does not). Mines fire before the
hit and not on a Debuff turn, learned on the screen. The Vaporize preview
"talked me out of a play" (Barbara has no hit for the multiplier). Weak and
Frail restate the numbers; Bombs ignore Weak as "Not an Attack".

**Defects, four rows.** Overloaded did not fire on a killing hit and nothing
says a kill skips its reaction (`EB-515`). Stoke the Fuse billed 2 Sparks
and the counter still read 2 (`EB-512`). Frail rewrote Defend and not
Diona's Block (`EB-513`). The stacked-Bomb headline hides the hit count
(`EB-514`). One refusal, the seat's own energy miscount, named its forms.

## 3. What the round did not test

The act-1 boss on either lane. Long Fuse, Fish Blasting, Bombs Away!,
Fireworks Show, Kindling, Flash Point, Vermillion Pact, Split Charge, All of
My Treasures!: none drafted or granted this round. Nothing here is a
strength reading.

## 4. The smallest interventions, ranked

1. **Grounded, adjusted, not cut.** Two seats in two rounds read its
   condition as "pays you for skipping the loop", and the ledger shows why:
   under this relic something goes off on most turns even in a Cook deck,
   because Mines fire on the enemy's beat. The smallest change keeps the
   card conditional (brief §6, C4) and keys it to cooking rather than to
   not cashing: *At the start of your turn, if you have a Bomb on the field,
   gain 6 Block and 1 Spark.* Read at §5.
2. **Random Set off aims a bombed body first.** Tinder Toss and Rapid Fire
   share one fault, and one rule fixes both without a new card: *a random
   Set off picks among enemies carrying a Bomb; if none, any enemy.* Read at
   §5.
3. **The relic stands.** Its incentive is now measured on two decks and it
   pays both; the imbalance the brief feared (Spray paid more directly) is
   real and is Grounded's job to offset, which item 1 lets it do.
4. **Sorry, Jean... and Pocket Match's Retain**: readings, held.

## 5. The doctrine read

Two arms to the doctrine role (`review/records/card-audit-2026-09-04.md`
§5.6): Grounded's condition and the random-Set-off rule, with the census
pasted and the two seats' lines quoted. Verdicts and the record are in
§5.6; a REQUIRES_MODIFICATION is withdrawn here, never argued.

## 6. Defaults applied (D and E), disclosed

- **`EB-512` to `EB-515` minted.**
- **D, after the read:** Grounded's condition becomes "if you have a Bomb
  on the field"; a random Set off prefers a bombed enemy. Built only on
  FOLLOWS.
- **The relic stands; the starter waits on the round-17 pick.**
- **The two records are the round's evidence.**
