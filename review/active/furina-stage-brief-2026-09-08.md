Status: OPEN (three picks, §11)

# Furina — character brief, the Stage: draft 1

Written 2026-09-08, from the afternoon's design discussion with [USER]. It
replaces the Tide sketch (three passes, PR #443) and the concepts packet's
working theory. Every rule below was settled in that discussion unless §10
marks it as a default I took. Numbers are opening values for the sim unless
a file is cited. The audience for this draft is [USER] and, relayed by
[USER], GPT for a sanity audit; nothing is built until the audit is read.

## 0. The test this brief has to pass

A Furina run has to feel unlike a Defect run while using Defect's chassis,
and unlike a Necrobinder run while using its pet. The test is the fight-one
script in §7: on turn one of the first hallway fight there is a wager a new
player can see and will argue about, and on the last turn there is a cash
decision the same player will regret getting wrong. If a reader cannot find
either turn, the brief has failed.

## 1. The promise, in three sentences

Furina's party is a cast of three performers who stand on stage in front of
her, and each performer's HP bar is the applause it is running on: its
Fanfare. Enemies hit her Block, then the lead performer, then her, so every
Defend is a stage card and the show grows when she defends well. She spends
that applause for damage, and the show ends when the fight does, so every
fight is a build and then a cash-out, and choosing the moment is the game.

## 2. The lore audit, and what each fact became

| Genshin | here |
|---|---|
| Salon Solitaire summons three members: Usher, Chevalmarin, Crabaletta | the three Salon members, Furina's own kit, and nothing else enters the stage in this draft |
| the members drain the party's HP to deal damage | Spend: Furina's cards pay the lead performer's Fanfare for a bigger number |
| Fanfare rises as the party's HP changes, and is spent by the Burst | Fanfare is the performer's bar itself, raised by Refill and regen, lowered by hits and Spend; no counter beside it |
| the party needs a healer to sustain the drain | Refill cards restore a performer's bar, which is legal at Common because the bar is not the player's (§10, default 6) |
| Let the People Rejoice | a Rare card, not a Burst bar (§5.3) |
| Furina is not a god, the show is what sustains her | the cast stands between her and the enemy, and dies when the defence fails |

Retired by this brief, each without a job under the shape above: Encore,
the Spotlight in both modes, the Fanfare counter and its riders, the
reframe's `proto_fr_` arm and `FURINA_REFRAME` switch, the Salon member
Powers, the Burst bar, and the Salon panel as built for them. The identity
record's lines on Spotlight, Encore and the Fanfare cap
(`docs/current/characters/furina-identity-record.md`) are revised by this
sentence, as that file says a brief may: **Furina's stage is three
performers with their own bars, and Fanfare is that bar.**

## 3. The rules of the kit

1. **The stage has three seats**, front, middle, back. A performer in a
   seat is a pet on Furina's side (the engine's own kind: Osty, Byrdpip,
   the Bake-Kurage) with a visible bar. Pets live one combat, so the stage
   is empty at the start of every fight except for rule 2.
2. **Combat opens with Usher in the front seat at 3 Fanfare**, granted by
   her starting relic. Defect's free Lightning orb, as a body.
3. **A summon card fills the back-most empty seat** with that performer at
   1 Fanfare. On a full stage it rotates the cast: the front performer
   leaves without a bow, the other two step forward, and the newcomer takes
   the back seat with the leaver's Fanfare. Pools are never lost to
   rotation.
4. **The lead performer regains 1 Fanfare at the start of Furina's turn.**
   Only the lead. Bars have no cap.
5. **Refill lands on the back-most performer.** "Raise 5 Fanfare on the
   back performer." With one performer on stage, that is the lead.
6. **Damage order, per attack: Furina's Block, then the lead performer's
   Fanfare, then Furina.** The lead absorbs what one attack puts through
   her Block, up to its bar; the rest reaches Furina. It never runs on to
   the middle seat. A big single hit rips through the lead and lands on
   her; a flurry can kill the lead and leave her untouched; each is
   answered differently and the intent shows which is coming.
7. **A performer at 0 Fanfare leaves the stage.** By a hit: it just leaves.
   By Spend: it takes a bow (rule 9).
8. **Spend N** is a rider on her cards: "Deal 7. Spend 3: deal 13 instead."
   It pays N from the lead performer's bar. If the lead has less than N,
   the rider still fires in full, the lead pays what it has and leaves
   with a bow. With no performer on stage the rider cannot fire and the
   card plays at its base number.
9. **The curtain call.** A performer emptied by Spend performs its
   departure effect once. Usher: Furina gains 4 Block. Chevalmarin: Hydro
   on every enemy. Crabaletta: deal 8 to a random enemy. Death by a hit
   earns no bow.
10. **Each performer performs at the end of Furina's turn**, a flat act
    that does not read its bar: Usher gives Furina 3 Block, Chevalmarin
    deals 2 to every enemy and applies Hydro, Crabaletta deals 5 to a
    random enemy. Scaling on Fanfare lives in payoff cards (§5.2), never
    in the performer.
11. **Furina's own bar is touched by nothing in the kit.** No Restore, no
    Spend from it, no reader on it. Her sustain is the cast.

What is not in this draft, by decision: Spend as an Energy-free cost (held
for a second batch), Fontaine Companions that summon a character with its
own act (held until the loop is proven), and co-op, where a partner's bar
would sit in the same damage order. Companion cards stay the shared action
pool; their touchpoint is Chevalmarin's Hydro, which the Fontaine bench's
Pyro and Cryo react off.

## 4. The contested thing: Spend

Spend, read flat, is Bloodletting with extra steps: HP for damage, and the
intent is visible, so the arithmetic is exact. Three facts about the pool
make it a decision instead.

- **The pool dies at the curtain.** Every point unspent when the last enemy
  falls is wasted. Mid-fight, Spend costs Furina's HP by proxy, because the
  lead's bar is her buffer against the posted intent. On the last turn it
  costs nothing. So every fight has a build phase and a cash phase, and the
  cash phase needs a Spend card in hand, which is a thing to hold for.
- **The lead's bar has two other claims on it.** It absorbs this turn's
  attack, and the payoff cards read it. Spend is the decision to stop
  building and take the lump.
- **Spend for lethal is clean, Spend to empty is a bow, Spend speculatively
  is the wager.** The same rider reads as three plays depending on the
  turn. The turn-one line in §7 is the wager in its purest form.

The one number the sim reports on Spend: in what fraction of turns the
rider fires outside the last turn and outside lethal. Near zero means the
rider is a tax and the rate rises; near one means the pool never builds
and the rate falls. Opening rate: 2 damage per Fanfare.

## 5. Her plans, three, separated by card slots

### 5.1 The Salon (the starter's plan)

Summon, defend, spend the lead, cash at the curtain. Wants Block in hand
on the big-intent turns and a Spend card on the last one. Its cards: the
three named summons, Curtain Rise and its Uncommon siblings, Standing
Ovation and the Refills.

### 5.2 The Ovation (the payoff plan)

Cards that read a performer's bar. "Deal damage equal to the lead's
Fanfare." "Gain Block equal to the back performer's Fanfare." "Raise 3
Fanfare on every performer." Wants a fat back seat and rotation cards, and
is where a Common Skill that rotates without summoning, "Take a Bow," earns
its place, so the reserve is not waiting on summon draws.

### 5.3 The Guest Cast (the reaction plan)

Chevalmarin's Hydro every turn, and the Fontaine bench's Pyro and Cryo
Companions reacting off it. Wants Companions and Chevalmarin in front,
where she regenerates and cannot be rotated out by accident.

The Rare all three aim at: **Let the People Rejoice**, 2 Energy, Exhaust.
Spend all Fanfare on stage. Deal that much damage to every enemy. Every
performer takes a bow, then returns at 1. Worth nothing on an empty stage.

## 6. The intended weakness

She is weak to a big single hit on a turn her Block is short: it kills the
lead and lands on her, and she has no Restore. She is weak in a fight she
enters with a thin deck of summons, because an empty stage makes every
Spend card a Strike. She is weak on the turn after a rotation, when a
1-Fanfare newcomer sits at the back doing nothing until Refill finds it.
She survives anyway because Defend protects the cast and the cast protects
her, so a plain Block deck keeps the show alive, and because the last turn
always pays.

## 7. Fight one: Nibbit, turn by turn

Nibbit at 44 HP (`tier05/content/act1_pool.yaml`: Butt 12, Hesitant Slice
6 with 5 Block, Hiss +2 Strength). Furina 78, 3 Energy, five cards a turn.
The starter: three Soloist's Solicitation (6), three Stage Presence (Block
6), Regal Bearing (Block 3, Weak 1), all the base game's basics and
untouched; plus Salon Début (summon a random performer not on stage),
Curtain Rise (Deal 7. Spend 3: deal 13 instead), Standing Ovation (Raise 5
Fanfare on the back performer). Usher is in front at 3 from the relic.
Nibbit's script here: Butt, Hiss, Slice, Butt.

**Turn 1.** Hand: Solicitation, Solicitation, Presence, Curtain Rise,
Standing Ovation. Intent Butt 12.

| line | play | Block | damage | enemy after | stage after enemy | Furina |
|---|---|---|---|---|---|---|
| A, build | Presence, Standing Ovation (Usher 3 to 8), Solicitation; Usher performs Block 3 | 9 | 6 | 38 | Usher 8, takes 3, at 5 | 78 |
| B, wager | Presence, Curtain Rise with Spend 3 (Usher 3 to 0, bows: Block 4), Solicitation | 10 | 19 | 25 | empty | 76 |
| C, plain | Presence, Curtain Rise unspent, Solicitation; Usher performs Block 3 | 9 | 13 | 31 | Usher 3, takes 3, dies, no bow | 78 |

Line C is the one to teach against: unspent, Usher dies to the same 3
points a bow would have covered, and the stage is empty with nothing to
show for it. A and B are the wager. A keeps the show and Furina whole; B
takes 13 more damage now at the cost of 2 HP and an empty stage. Neither
is wrong, and the seat question for round one is which one a seat picked
and why.

**Turn 2, on line A.** Usher regenerates to 6. Hand: Presence, Presence,
Regal Bearing, Salon Début, Solicitation. Intent Hiss. A free turn: Salon
Début fields Crabaletta at the back with 1, Solicitation 6 (38 to 32),
Regal Bearing for the Weak on next turn's hit. Performances: Usher Block 3
(wasted), Crabaletta 5 (32 to 27). Nibbit gains 2 Strength.

**Turn 3.** Reshuffle. Hand: Presence, Solicitation, Curtain Rise, Standing
Ovation, Solicitation. Intent Slice, 6 plus 2 Strength, Weak makes it 6,
with 5 Block for Nibbit on its turn. Usher 7. Play Presence, Standing
Ovation (Crabaletta 1 to 6, the reserve), Curtain Rise with Spend 3 (Usher
7 to 4) for 13: 27 to 14. Performances: Usher Block 3, Crabaletta 5, 14 to
9. Block 9 against 6, nothing through. Rejected: Curtain Rise unspent and a
Solicitation, 13 for the same energy but no Refill, so the back seat stays
at 1 and the cash-out next turn is 5 smaller.

**Turn 4, the curtain.** Usher 5, Crabaletta 6. Nibbit at 9 with 5 Block.
Hand: Solicitation, Solicitation, Solicitation, Regal Bearing, Salon Début.
Three Solicitations for 18 kill it. Nothing to spend and 11 Fanfare
evaporates, which is the lesson of the last turn: the cash-out needs the
Spend card, and it was played on turn 3. Holding Curtain Rise on turn 3
would have cost 6 damage then and paid 13 now against a dead enemy's
Block, so playing it was right; the point is that the player feels the
waste. Furina leaves at 78.

The fight is easy, as fight one is for every starter. What it showed: one
wager on turn one, one Refill decision on turn three, and a waste on turn
four the player will try to fix by drafting.

## 8. Failure modes, named

- **The cast is chaff.** If bars stay small, performers die to every
  unblocked point and the stage is a card sink. Lever: the opening 3,
  regen, and Refill's size.
- **The cast is a second life bar.** If Refill is Defend-priced and the
  lead absorbs freely, sixty HP of cast is healing in spirit. Lever: Refill
  lands at the back, not on the lead, and the sim prices Refill against
  Block at the same Energy.
- **Spend is always right, or never.** §4's number.
- **Three Ostys.** If a seat reads the performers as one Osty three times,
  the acts and the bows are not distinct enough. Round-one debrief
  question.
- **The intent lies.** The enemy's arrow points at Furina while the damage
  lands on the lead. Block already has this property and players read it;
  the panel must show the lead's bar beside her Block, in the damage order.

## 9. What fight one does not test, and where it is tested

Rotation on a full stage (needs three summon cards in the deck), the
Ovation readers, the Guest Cast's reactions, and a boss with a flurry
intent. Each is a seat-round deck, granted, after the audit.

## 10. Defaults taken, disclosed (D and E)

1. Usher is the fixed opening performer (E). Fixed for legibility; random
   is the alternative if fight one reads as samey.
2. Salon Début summons a random performer not on stage (D); the three
   named summons are Commons in the pool.
3. Opening Fanfare 3, regen 1, Refill 5, Spend rate 2, the acts and the
   bows at the numbers in §3 (D, the sim's).
4. A Spend larger than the lead's bar fires in full and the lead bows (E),
   as [USER] said.
5. Rotation on a full stage retires the front without a bow (E): a bow is
   earned by Spend only.
6. Refill on a performer is legal at any rarity: the healing law
   (`docs/current/LAW.md`, "Content authoring", the Rare-and-Exhaust line)
   binds the player's own bar (E, applied as [USER]'s reading; §11 pick 2
   asks whether to write the sentence into LAW).
7. Furina's max HP stays 78 until the sim reads her under the new damage
   order (D).

## 11. What is asked

1. **The direction (A).** Default: this brief, as written, goes to GPT for
   a sanity audit and then to a `+proto` build. 2: another discussion pass
   first.
2. **The healing law's reach (C, `LAW.md`).** Default: add one sentence,
   "the Rare-and-Exhaust rule binds the player's bar; a pet's bar may be
   restored at any rarity." 2: leave LAW as it is and carry the reading in
   this brief only.
3. **The concepts packet (A).** Default: it closes, its working theory
   superseded by this brief, and PR #433 closes with it. 2: keep B, the
   Arkhe, open as a challenger.
