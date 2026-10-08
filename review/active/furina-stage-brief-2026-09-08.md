Status: FROZEN 2026-10-05. The v1 Stage's brief; the build is at tag `furina-stage-frozen-2026-10-04`. Furina's current rules are the Salon's Tab, `review/active/furina-research-proposal-2026-10-05.md`. Kept in place because `tier0/tests/test_furina_seat_round_b_2026_09_25.py` reads it.

# Furina — character brief, the Stage: draft 2

Written 2026-09-08 from the afternoon's design discussion with [USER];
draft 2 the same evening after GPT's read of draft 1 (commit `19ace88`),
whose corrections are all taken and listed in §14. [USER] ruled the three
picks the same evening (R269, §11): build it, the healing law gets the pet
clause, the older alternatives close. This is the kit's brief through the
Prototype build. Numbers are opening values for the sim unless a file is
cited.

## 0. The test this brief has to pass

A Furina run has to feel unlike a Defect run while using Defect's chassis,
and unlike a Necrobinder run while using its pet. Draft 1 claimed fight one
proved it; GPT showed it does not (§14), and draft 2 makes the smaller
claim: fight one shows a wager on turn one and nothing more, and whether
preserving a reserve pays is a question for a longer fight and a seat round
(§9, §13). If a seat round finds neither a wager nor a reason to keep a
second performer alive, the brief has failed.

## 1. The promise, in three sentences

Furina's party is a cast of three performers who stand on stage in front of
her, and each performer's bar is the applause it is running on: its
Fanfare. Enemies hit her Block, then the lead performer, then her, so every
Defend is a stage card and the show grows when she defends well. She spends
that applause for damage, either by growing a performer and cashing it, or
by fielding cheap ones and spending them small, and which of those a deck
does is the draft.

## 2. The lore audit, and what each fact became

| Genshin | here |
|---|---|
| Salon Solitaire summons three members: Usher, Chevalmarin, Crabaletta | the three Salon members, Furina's own kit, and nothing else enters the stage in this batch |
| the members drain the party's HP to deal damage | Spend: Furina's cards pay the back performer's Fanfare for a bigger number |
| Fanfare rises as the party's HP changes, and is spent by the Burst | an adaptation, not a translation: Fanfare is the performer's bar itself, so applause is something attacks deplete, Refill and regen raise, and Spend cashes |
| the party needs a healer to sustain the drain | Refill cards restore a performer's bar, legal at Common because the bar is not the player's (`LAW.md`, the healing rule's pet clause, R269) |
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
   her starting relic. Defect's free Lightning orb, as a body. The first
   hand sees 3. (Since the rules pass, 2026-10-01, nothing regains it but The
   Curtain Never Falls; rule 4 is cut.)
3. **A summon card fills the back-most empty seat** with that performer at
   1 Fanfare. **A summon on a full stage works like a Defect orb**
   (2026-09-25; [USER]: "treat this like a Defect orb summon? the stage
   members rotate, … bows, and their remaining fanfare transfers to the
   newest member", and the seat that leaves is the lead): the lead
   performer takes a Bow and leaves, the other two step forward, and the
   newcomer takes the back seat and adds its Fanfare: its own arrival
   Fanfare (1, or a Guest Star's N) plus the lead's remaining Fanfare
   (2026-09-25, so a guest cast onto a front at 1 does not arrive unable to
   pay). The Summon tip: "On a full stage, the front one Bows and leaves
   its Fanfare to the newcomer." (2026-09-25 night; it read "and the
   newcomer adds its Fanfare", which a seat only understood from the log.)
   The Bow is a real one (its effect and every Bow reader fire, Thunderous
   Applause included), in the order bow, readers, arrival; A Five-Century
   Act does not also return it. This replaced the rotation that retired the
   front WITHOUT a bow, which a first-time co-op player met as a summon that
   did nothing. **The trio can be cloned** (2026-09-25: the trio can be
   cloned; [USER]: "Let's allow for copies and then check the balance."): a
   named summon always summons, even when that performer is already on
   stage, and a random summon picks uniformly from all three, on stage or
   not. Named and random summons meet a full stage the same way. **Guest
   Star: Wriothesley joins at the front** (2026-09-25, the guest seat round:
   "he joins at the back, where hits never reach him, so his act lands
   nothing"): the others shift back one, and on a full stage the recast's
   leaver is the back performer instead, which Bows and leaves while he
   arrives at the front holding his 8 plus its remaining Fanfare. A second
   copy still Bows him and returns him to his own seat. **Wriothesley is
   "Always your front performer"** (the rules pass, 2026-10-01; [USER]: "Yes
   on Wriothesley - it's much cleaner"): that one sentence on his face
   replaces his exceptions. Every summon and seat move works as normal around
   him, and he is never moved from the front: his own summon on a full stage
   Bows the front performer, as any summon does, and he takes the front; a
   summon while he stands there Bows the performer behind him. Pools are
   never lost. A newcomer performs with
   the others at the end of that turn, never on arrival (round one,
   `EB-738`: both engines had read this sentence as an act on play).
4. ~~**The lead performer regains 1 Fanfare at the start of Furina's
   turn**~~. **Cut by the rules pass (2026-10-01);** [USER]: "Agreed, remove
   the freebie. The Ancient relic can give it back, as planned." The front
   regains nothing; The Curtain Never Falls ("Your front performer regains 2
   Fanfare at the start of each turn", from her second turn) gives the only
   regain. The fade (rule 12) is no longer cancelled on the front. Bars have
   no cap.
5. **Refill lands on the back-most performer.** "Raise 5 Fanfare on the
   back performer." With one performer on stage, that is the lead. The
   front performer is the shield and the back performer is the bank
   (R276): Raise fills the bank, and Spend and the Fanfare readers draw
   from it (rule 8). A face may name another seat (the lead, every
   performer); a bare Raise means the back performer. **Only what you play
   summons on an empty stage** (the rules pass, 2026-10-01; [USER]: "This
   makes sense - agreed on your split"): a card or potion you play that gives
   Fanfare, on an empty stage, summons a random performer holding it, not the
   usual 1, and nothing else is raised (Rising Applause, Cheered On, Warm
   Reception, Hold Your Places, Singer of Many Waters, Bottled Applause). A
   gain from a Power, a relic or a reaction trigger does nothing on an empty
   stage (Season Tickets, Thunderous Applause, Tide of Applause, the
   Ancient's turn-start Raise, the co-op powers), and a gain naming "each
   performer" has nobody to land on (Grand Deluge, Curtain Water). The
   Fanfare tip: "If no one is on stage, a card that gives Fanfare summons a
   random performer holding it." (Round four had every Raise summon.)
   Arkhe Alignment's Pneuma is a turn-start choice, not a played card, so it
   keeps "regains" and summons nobody.
6. **Damage order, per attack: Furina's Block, then the lead performer's
   Fanfare, then Furina.** The lead absorbs what one attack puts through
   her Block, up to its bar; the rest reaches Furina. It never runs on to
   the middle or back seat. A big single hit rips through the lead and lands on
   her; a flurry can kill the lead and leave her untouched; each is
   answered differently and the intent shows which is coming. A performer
   emptied by a hit Bows before the rest of that hit reaches you
   (2026-09-25 night, the granted-guest seat round: Usher's Bow Block had
   landed after the overflow, so it never protected anything).
7. **A performer at 0 Fanfare takes a Bow and leaves,** whatever emptied it: a Spend, a hit, or a summon on a full stage (2026-09-25; [USER]: "Stage members bow out when they are destroyed or replaced, not just when you deliberately spend them down to 0"). A hit's Bow comes inside the hit that caused it, on the enemy's turn: the performer leaves, Bows, and only then does the rest of that hit reach Furina (her Block first, so Usher's Bow Block catches it; rule 6), and whatever that Block leaves meets the next hit. (2026-09-25 evening, [USER], overruling the start-of-turn wait the draft-3 seat round had prompted: "I think it would be better to have the performer bow immediately (during the opponent's turn) instead of at the start of your turn.")
8. **Spend N** is a choice on her cards, made when the card is played:
   "Deal 7" or "Spend 3: deal 13 instead" (round two, `EB-746`: both engines
   had fired the rider whenever a lead stood, and four seats asked for the
   verb). **It pays from the back performer first, then forward** (the
   rules pass, 2026-10-01; [USER]: "Agreed, spending start back-forwards";
   R276 had the back pay alone and in full). If the whole stage holds less
   than N, or no performer is on stage, the Spend mode cannot be chosen and
   the card plays its base mode. Every performer the Spend empties leaves
   with a bow, back to front. The bank still empties first. Palais Ledger,
   which was this rule, now reads "Your Spends cost 1 less Fanfare"; Center
   of Attention's first Spend each turn is free and no longer chosen on a
   short bar.
9. **The Bow is the performer's act, once more** (2026-09-25; [USER] ruled the Stage review's pick 1: one effect per performer, since Chevalmarin's Bow was "strictly worse than the end-of-turn effect"). A performer that Bows acts one last time as it leaves. Ousia and Pneuma double it like any act; Full House does not repeat it.
10. **Each performer performs at the end of Furina's turn**, from any
    seat, a flat act that does not read its bar: Usher gives Furina 3 Block, Chevalmarin deals 2 to every enemy, Crabaletta deals 5 damage to a random enemy. No act applies Hydro (2026-09-25; [USER]: "we may need to do the same here, removing the Hydro application from the end-of-turn effects on Chevalmarin and Crabaletta", as Klee's Pyro became a payoff). Hydro comes from cards: Tidal Flourish and Quick Cue apply it in their Spend modes, Bubble Aria and Grand Deluge apply it too, and Chevalmarin's card applies it on play. On the four Attacks the Hydro rides the hit, so a reaction multiplies that hit (Bubble Aria: its first hit), as Klee's Pyro does (2026-09-26 seat round: the Hydro rides the hit). Scaling on Fanfare lives in payoff cards
    (§5.2), never in the performer.
11. **Furina's own bar is touched by nothing in the kit.** No Restore, no
    Spend from it, no reader on it. Her sustain is the cast.
12. **The applause fades.** At the start of Furina's turn (from her second), before anything else she does, every performer, the front one included, loses a quarter of its Fanfare, rounded down: 0 to 3 lose 0, 4 to 7 lose 1, 8 to 11 lose 2, 12 loses 3, 20 loses 5. A quarter never empties a performer, so the fade never causes a Bow. Why: the bank had no cost to hold, so spending it had no cost either; the fade makes a fat bank a choice (spend it or cash it out). [USER] ruled out a flat halving in draft 3 ("hard to build up fanfare"); the quarter is his ("What about a percentage fade, say 25%? Anything below 4 rounds to losing 0."). The divisor is the knob. (The fade pass, 2026-09-29, §18. Draft 3's rule was half of the Fanfare above 5, behind the front only; in the sim it faded 0 to 2 Fanfare a fight.) (2026-10-03, [USER]'s run notes: "Fanfare decay should be at the start of the next turn, not the end." Was the end of her turn, after the acts; it now comes after the enemies attack, so their hits meet the unfaded bars. Same amount. The forecast no longer shows a fade.)

What is not in this batch, by decision: Spend as an Energy-free cost,
Fontaine Companions that summon a character with its own act (held until
the loop is proven), and co-op, where a partner's bar would sit in the same
damage order. Companion cards stay the shared action pool; since draft 3 no
act applies Hydro, so the Hydro the Fontaine bench's Pyro and Cryo react off
comes from Furina's cards (Tidal Flourish and Quick Cue in their Spend modes,
and Chevalmarin's card), and a guest brings its own element (2026-09-25).

## 4. The contested thing: Spend, and the two decks it makes

Spend, read flat, is Bloodletting with extra steps: HP for damage, and the
intent is visible, so the arithmetic is exact. What makes it a decision is
that the pool has other claims on it and a short life.

- **The pool dies at the curtain.** Every point unspent when the last enemy
  falls is gone, as unused Block is gone. That is not a mistake in itself;
  it is the reason the pool is worth spending.
- **The two seats have two jobs (R276).** The lead is the shield: it
  absorbs this turn's attack and regenerates. The back performer is the
  bank: Raise fills it, and Spend and the readers draw from it. With one
  performer on stage it is both, so a lone Usher's bar is shield and bank
  at once. Scene Change moves a fat bank forward as a shield, or a hurt
  lead back to be refilled.
- **Spend pays the full price, the bank first.** A Spend needs its whole
  price on the stage; the back performer pays first, then the one in front
  of it (the rules pass, 2026-10-01; R276 asked the back alone). A stage
  short of it cannot choose the Spend mode. Every performer the Spend
  empties takes a bow. So there are two decks,
  and neither is the approved one:
  - **Preserve.** Keep the lead alive behind Block, Refill the bank, cash
    big with Spend, the readers and the Rare.
  - **Expend.** Raise a performer to exactly a Spend's price and empty it
    for the rider and the bow, then replace it. Pays in cards and Energy,
    not in Fanfare.

Since 2026-09-25 a hit earns the bow too, so Expend's edge is choosing when the bow lands: on Furina's turn, with the rider paid.

"Two damage per Fanfare" is a nominal rate. The sim's job is to report
which deck wins and by how much, not to set one rate (§13). Until R276 the
rider fired in full off a bar of any size, and six of nine seats called
spending a 1-Fanfare body for the full rider a loophole; the full-price
rule closes it.

**Three ways out (2026-09-25).** A performer knocked out by a hit or a Spend gets only its Bow. One recast off a full stage Bows too, and the newcomer arrives holding its Fanfare. One cashed out by an Expend card (Bravura, Final Bow, Let the People Rejoice) is paid for all its Fanfare at a scaling rate, then Bows. The recast pays off once the guest batch gives the newcomer a different body.

## 5. Her plans, three, separated by card slots

### 5.1 The Salon (the starter's plan)

Summon, defend, spend the lead. Wants Block in hand on the big-intent turns
and a Spend card when the enemy can die. Its cards: the three named
summons, Curtain Rise and its siblings, Rising Applause and the Refills,
and Understudy for the Expend line. (2026-09-28: Understudy and the
Gentilhomme Usher card left the pool in the balance pass, §15; Usher the
performer stays.)

### 5.2 The Ovation (the payoff plan)

Cards that read a performer's bar. "Deal damage equal to the back
performer's Fanfare." (Ousia Surge, the bank reader.) "Gain Block equal to
the lead performer's Fanfare." (Pneuma Refrain, the shield reader.) Wants a
fat reserve and a way to move it forward, and is where a Common Skill that
rotates without summoning, Scene Change, earns its place, so the reserve is
not waiting on summon draws. Rotation grants no bow, and the card's name
says nothing about one.

### 5.3 The Guest Cast (the reaction plan)

Chevalmarin's Hydro every turn, from any seat, and the Fontaine bench's
Pyro and Cryo Companions reacting off it. Wants Chevalmarin on stage and
Companions in hand; the back seat is her safest, since only the lead is
exposed and a summon on a full stage removes the front.

The Rare all three aim at: **Let the People Rejoice**, 2 Energy, Exhaust.
Spend all Fanfare on stage. Deal twice that much damage to every enemy
(2026-09-25: it paid 1 per Fanfare, and a seat found performers never held
enough to make 2 Energy worth it; Spend's nominal rate, §4, is 2). Every
performer takes a bow, then returns at 1. Worth nothing on an empty stage.

## 6. The intended weakness

She is weak to a big single hit on a turn her Block is short: it kills the
lead and lands on her, and she has no Restore. She is weak in a fight she
enters with a thin deck of summons, because an empty stage makes every
Spend card a Strike. Her reserve is thin until Refill finds it: a newcomer
on an empty seat arrives at 1, acts at the end of the turn with the others
(rule 3, `EB-738`), and absorbs nothing until it is the lead. Since the
rules pass (2026-10-01) only a card or potion she plays refills an empty
stage, and nothing regains the front but The Curtain Never Falls. She survives anyway because Defend protects the cast and
the cast protects her, so a plain Block deck keeps the show alive.

## 7. Fight one: Nibbit, turn by turn

Nibbit at 44 HP (`tier05/content/act1_pool.yaml`: Butt 12, Hesitant Slice
6 with 5 Block, Hiss +2 Strength). Furina 78, 3 Energy, five cards a turn.
The starter: three Soloist's Solicitation (6), three Stage Presence (Block
6), Regal Bearing (Block 3, Weak 1), all the base game's basics and
untouched; plus Take the Stage (summon a random performer),
Curtain Rise (Deal 7. Spend 3: deal 13 instead), Rising Applause (Raise 5
Fanfare on the back performer). Usher is in front at 3 from the relic.
Nibbit's script here: Butt, Hiss, Slice, Butt.

**The starter changed on 2026-09-28, and the walk-through below predates it.**
[USER]: "Typically we'd include 4 strikes, 4 defends and 2 actually useful
cards that teach the character's core mechanics - this seems like an
unnecessary power spike." "I agree with keeping Curtain Raise and Rising
Applause." "We should really just replace Soloist's Solicitation and Stage
Presence with the basic strike and defend." "The characters' kits should all
use basic Strike and Defend." The Stage now opens with the base game's Strike
x4 (6 damage) and Defend x4 (Block 5), Curtain Rise and Rising Applause: ten
cards (`FurinaStageRoster.StartingDeck`, sim `furina_stage.STARTER_IDS`). Take
the Stage and Regal Bearing left the starter and are offered as Commons (sec.12).

**Turn 1.** Hand: Solicitation, Solicitation, Presence, Curtain Rise,
Rising Applause. Intent Butt 12.

| line | play | Block | damage | enemy after | stage after enemy | Furina |
|---|---|---|---|---|---|---|
| A, build | Presence, Rising Applause (Usher 3 to 8), Solicitation; Usher performs Block 3 | 9 | 6 | 38 | Usher 8, takes 3, at 5 | 78 |
| B, wager | Presence, Curtain Rise with Spend 3 (Usher 3 to 0, bows: Block 4), Solicitation | 10 | 19 | 25 | empty | 76 |
| C, plain | Presence, Curtain Rise unspent, Solicitation; Usher performs Block 3 | 9 | 13 | 31 | Usher 3, takes 3, dies, no bow | 78 |

Lines B and C now end differently. Line C ends in Usher's Bow after the hit (rule 7, 2026-09-25), and since the same day his Bow gives the front performer 4 Fanfare rather than Furina 4 Block (rule 9); on the stage he leaves empty in lines B and C, that is a random performer arriving with 4. Line B's "bows: Block 4" and its Block of 10 are the old Bow. The numbers above predate both changes.

All three are legitimate. A keeps the show and Furina whole for the least
damage. B takes 13 more damage than A for 2 HP and an empty stage. C sits
between them: it loses Usher like B, keeps the 2 HP, and deals 6 less,
which matters only if the 6 changes what Nibbit does next, and here it
does not. The turn-one wager is A against B; C is the line a player takes
who has not yet seen that Usher dies either way. The seat question for
round one is which line a seat picked and why.

**Turn 2, on line A.** Usher regenerates to 6. Hand: Presence, Presence,
Regal Bearing, Take the Stage, Solicitation. Intent Hiss. A free turn: Take
the Stage fields Crabaletta at the back with 1, Solicitation 6 (38 to 32),
Regal Bearing for the Weak on next turn's hit. Performances: Usher Block 3
(wasted), Crabaletta 5 (32 to 27). Nibbit gains 2 Strength.

**Turn 3.** Reshuffle. Hand: Presence, Solicitation, Curtain Rise, Rising
Applause, Solicitation. Intent Slice, 6 plus 2 Strength, Weak makes it 6,
with 5 Block for Nibbit on its turn. Usher 7. Two lines:

- **Refill:** Presence, Rising Applause (Crabaletta 1 to 6), Curtain Rise
  with Spend 3 (Usher 7 to 4) for 13. With Crabaletta's 5, Nibbit is at 9.
  Block 9 against 6, nothing through.
- **Damage:** Presence, Curtain Rise with Spend 3, Solicitation: 19, and
  with Crabaletta's 5, Nibbit is at 3. Same Block, nothing through.

The damage line is better in this fight, and the Refill line's reserve is
never used: draft 1 claimed otherwise and was wrong. (Under R276 the damage
line is gone: Spend draws from the back performer, Crabaletta at 1 cannot
pay 3, and only the Refill line can spend -- Crabaletta 1 to 6, then 6 to 3
for the 13, Nibbit at 9. `tier0/tests/test_furina_stage.py` plays that
line.) What the Refill line
buys is a 6-Fanfare Crabaletta for a fight that lasts longer than this
one, and this one does not. That is the honest reading: in a four-turn
hallway fight the reserve does not pay, and whether it pays in a
seven-turn fight or against a flurry is what §9 tests.

**Turn 4, the curtain.** On the damage line Nibbit is at 3 with 5 Block;
any two Solicitations kill it. Usher 5, Crabaletta 1. Whatever is left on
the bars is gone, as leftover Block would be, and nothing about it was a
mistake. Furina leaves at 78.

What fight one shows: one wager on turn one. What it does not show: a
reason to build a reserve, or a regrettable cash-out. Both are claims for a
longer fight, and the brief no longer makes them here.

## 8. Failure modes, named

- **The cast is chaff.** If bars stay small, performers die to every
  unblocked point and the stage is a card sink. Lever: the opening 3,
  regen, and Refill's size.
- **The cast is a second life bar.** If Refill is Defend-priced and the
  lead absorbs freely, sixty HP of cast is healing in spirit. Lever: Refill
  lands at the back, not on the lead, and the sim prices every Refill point
  as damage prevention where the pet stands in front of the player, as the
  LAW clause says.
- **A solo Usher is best.** With one performer, regen and Refill both reach
  the exposed bar; a second performer sends Refill away from it. If a
  carefully kept lone Usher beats every cast, the second seat has no
  reason to exist. Lever: what the acts and readers pay for a full stage.
- **Expend beats Preserve outright.** §4's guard: the bow's size.
- **Three interchangeable shields.** If a seat does not care which
  performer it keeps, the acts and bows are not different enough, and
  merely enlarging the differences will not fix it. Round-one debrief
  question.
- **The intent lies.** The enemy's arrow points at Furina while the damage
  lands on the lead. Block already has this property and players read it;
  the strip must show the lead's bar beside her Block, in the damage order.

## 9. What fight one does not test, and where it is tested

Whether a reserve pays: a seven-turn fight and a flurry intent (the act-1
elite and a two-body hallway). Rotation on a full stage: a deck granted all
three summons. The Ovation readers, Scene Change and the Rare: a granted
Preserve deck. Understudy and the bows: a granted Expend deck. The Guest
Cast's reactions: a Chevalmarin deck with two Fontaine Companions. Round
one runs the natural starter and the two granted decks, Preserve and
Expend, on the same seed.

## 10. Defaults taken, disclosed (D and E)

1. Usher is the fixed opening performer (E). Fixed for legibility; random
   is the alternative if fight one reads as samey.
2. Take the Stage summons a random performer, picked uniformly from all
   three (D); the three named summons are Commons, and a named summon
   always summons, even when that performer is already on stage (2026-09-25:
   the trio can be cloned; [USER]: "Let's allow for copies and then check
   the balance.").
3. Opening Fanfare 3, regen 1 from turn two, Refill 5, the nominal rate 2,
   the acts and the bows at the numbers in §3 (D, the sim's).
4. A Spend needs its full price from the back performer, and a bow comes
   from an exact emptying (R276 pick 1; it replaced the E default that a
   short bar still fired the rider in full). A hit also earns the bow since 2026-09-25 (rule 7).
5. ~~Rotation on a full stage retires the front without a bow (E): a bow
   is earned by Spend only.~~ Reversed 2026-09-25 by [USER] ("treat this
   like a Defect orb summon? the stage members rotate, … bows, and their
   remaining fanfare transfers to the newest member"; the lead leaves): a
   random summon on a full stage bows the lead, which returns to the back
   seat with its Fanfare. See rule 3.
6. Furina's max HP stays 78 until the sim reads her under the new damage
   order (D).
7. Names in §12 are provisional and cosmetic (R179).

## 11. What was asked, and ruled: R269 (2026-09-08)

[USER], after relaying GPT's read: "Overall I agree with GPT - we move to
coding / playtesting, we take the LAW amendment, and we close alternatives.
This seems to be the most promising idea thus far."

1. **The direction (A):** build it. Draft 2 goes to a `+proto` build
   (`EB-724` engine, `EB-725` C#, `EB-723` pool) and a seat round on §13's
   questions.
2. **The healing law's reach (C):** the sentence is in `LAW.md`: the
   Rare-and-Exhaust rule binds the player's own bar; a pet's bar may be
   restored at any rarity, priced as damage prevention wherever the pet
   stands between the player and the enemy.
3. **The alternatives (A):** closed. The concepts packet is in
   `review/ruled/`, the Tide sketch has left HEAD, PR #433 is closed, and
   B the Arkhe is not held as a challenger.

## 12. Batch one, the faces

**2026-09-25, the text pass.** [USER], after the overnight tooltip pass: "for
the Furina work, I also wanted a text cleanup pass. It's not just that some
text was missing - it's that the existing text is often very verbose and
unintuitive." The faces below are the pass's words
(`review/records/furina-text-pass-2026-09-25.md`). No rule and no number
moved. `Raise` and `Rotate` are retired as keywords (faces say "gains N
Fanfare" and say what moves), "lead performer" is "front performer"
everywhere, "act" is the one verb for what performers do, and a Spend card's
face drops "Choose one:".

Seventeen cards, enough to play Preserve and Expend against each other.
Every `Spend` pays its full price, from the back performer first, then
forward (the rules pass, 2026-10-01; R276 had the back pay alone); Fanfare a
card gives lands on the back performer unless the face names another.
Names are provisional.

**The starter's kit cards (two, beside the base Strike x4 and Defend x4)**

2026-09-28, [USER]'s ruling (sec.7): the base game's Strike and Defend, four
each, replace Soloist's Solicitation and Stage Presence; Take the Stage and
Regal Bearing leave the starter for the Commons below.

| card | cost | type | text |
|---|---|---|---|
| Curtain Rise | 1 | Attack | Deal 7 damage. Spend 3: deal 17 instead. [10 / 21] (2026-09-29 fade pass, §18: the Spend mode was 13, 16 upgraded.) |
| Rising Applause | 1 | Skill | Your back performer gains 5 Fanfare. (Was Standing Ovation; renamed under R179 in round one, `EB-739`, since a shipped Power carries that name.) |

**Commons (eight, and two more since 2026-09-28; Gentilhomme Usher and Understudy left the pool in the balance pass, §15)**

| card | cost | type | text |
|---|---|---|---|
| ~~Gentilhomme Usher~~ | 1 | Skill | Summon Usher. (2026-09-25: the trio can be cloned; the "already on stage" clause is gone.) (2026-09-28: out of the pool, §15.) |
| Surintendante Chevalmarin | 1 | Skill | Apply Hydro to ALL enemies. Summon Chevalmarin. (2026-09-25, draft 3: Hydro comes from cards. The same evening: the trio can be cloned.) |
| Mademoiselle Crabaletta | 1 | Skill | Summon Crabaletta. (2026-09-25: the trio can be cloned.) |
| ~~Understudy~~ | 0 | Skill | Summon a random performer. Exhaust. (2026-09-25: the face follows the full-stage ruling, rule 3.) (2026-09-28: out of the pool, §15.) |
| Warm Reception | 1 | Skill | Your back performer gains 3 Fanfare. Draw 1 card. |
| Tidal Flourish | 1 | Attack | Deal 5 damage to ALL enemies. Spend 2: deal 9 and apply Hydro to ALL instead. (2026-09-25, draft 3.) (2026-09-29 fade pass, §18: Spend 3 for 13 [16]; §16 had made it Spend 3 for 10 [13].) |
| Interposition | 1 | Skill | Gain 5 Block. Spend 2: gain 10 instead. |
| ~~Scene Change~~ | 0 | Skill | Move your front performer to the back. (2026-09-29: out of the pool, §17.) |
| Take the Stage | 1 | Skill | Summon a random performer with 3 Fanfare. Draw 1 card. [cost 0] (2026-09-28: out of the starter and a Common with a stronger face. Tentative: [USER], "'Become Common with a stronger effect' is fine as a tentative proposal, and then we can do an audit of the pool as part of the balance pass to see if we still want it." Was "Summon a random performer." at basic; was Salon Début, renamed under R179, `EB-739`.) |
| Regal Bearing | 1 | Skill | Gain 5 Block. Apply 1 Weak. [6 Block, 2 Weak] (2026-09-28: out of the starter and a Common; [USER]: "5 block, 1 weak" upgraded to "6 block, 2 weak". The shipped basic prints Block 3, Weak 1 and does not move.) |

**Uncommons (five)**

| card | cost | type | text |
|---|---|---|---|
| Grand Entrance | 2 | Attack | Deal 12 damage. Spend 5: deal 24 instead. [16 / 28] (2026-09-26 balance review: was 10 / 20.) (2026-09-29 fade pass, §18: Spend 7 for 40 [45]; §16 had made it Spend 7 for 32 [36].) |
| Ousia Surge | 1 | Attack | Deal 3 damage, plus 1 for each Fanfare on your back performer. [base 6] (2026-09-29 audit pass, §17: was damage equal to the Fanfare, plus 4 upgraded.) (R276: was the front's.) (2026-09-26 balance review: the upgrade was cost 0.) |
| Pneuma Refrain | 1 | Skill | Gain 3 Block, plus 1 for each Fanfare on your front performer. [base 6] (2026-09-29 audit pass, §17: was Block equal to the Fanfare, plus 4 upgraded.) (R276: was the back's.) (2026-09-26 balance review: the upgrade was cost 0.) |
| Bis! | 1 | Skill | Your front performer acts twice. [cost 0] (2026-09-26 balance review: was "acts now". A lead that leaves after the first act does not act again.) |
| Final Bow | 1 | Skill | Your back performer Bows and leaves. Gain Block equal to twice its Fanfare. Exhaust. [no Exhaust] (2026-09-29 audit pass, §17: was equal to its Fanfare.) (R276: was the front.) |

**Rare (one)**

| card | cost | type | text |
|---|---|---|---|
| Let the People Rejoice | 2 | Attack | Deal damage to ALL enemies equal to twice your performers' Fanfare. They all Bow, then return with 1. Exhaust. (2026-09-25: was once their Fanfare.) |

The relic: **Salon Solitaire**, Furina's starting relic. Start each combat
with Usher in front with 3 Fanfare.

Tips the faces need: Spend, Fanfare (the bar), Bow, Summon, the front
performer, the back performer, and the three performers. (Before the text
pass: Spend, Fanfare, Raise, Bow, the lead, the back performer, Rotate.)

### Batch two (R276)

Fifteen cards on the rules R276 set: the front performer is the shield,
the back performer the bank, and a Spend pays its full price. Numbers are starting
values; names are provisional. Upgrades in brackets.

**Commons (six)**

| card | cost | type | text |
|---|---|---|---|
| Improvised Number | 1 | Attack | Deal 8 damage. If no one is on stage, Summon a random performer. [Deal 11] (2026-09-29 audit pass, §17: was 6, 9 upgraded.) |
| Between Acts | 1 | Skill | Gain 5 Block. If no one is on stage, draw 2 cards. [8 Block] |
| Ensemble Piece | 1 | Attack | Deal 5 damage for each performer on stage. [7 each] (2026-09-29 audit pass, §17: was 4, 5 upgraded.) |
| Hold Your Places | 1 | Skill | Gain 5 Block. Your front performer gains 2 Fanfare. [7 Block, gains 3] |
| Quick Cue | 0 | Attack | Deal 3 damage. Spend 3: deal 11 and apply Hydro instead. [4 / 13] (2026-09-25, draft 3: Spend 2 for 8.) (§16 made it Spend 3 for 11 [4 / 12]; the 2026-09-29 fade pass, §18, 14 [4 / 16]; the rules pass, 2026-10-01, §19: 11 [4 / 13], since at 0 cost it beat Curtain Rise's Spend.) |
| Step Forward | 0 | Skill | Move your back performer to the front. Gain 3 Block. [5 Block] |

**Uncommons (seven)**

| card | cost | type | text |
|---|---|---|---|
| ~~Gala Dinner~~ | 1 | Skill | Each performer gains 2 Fanfare. [gains 3] (2026-09-28 balance pass: was 3, 4 upgraded.) (2026-09-29: out of the pool, §17.) |
| Double Casting | 1 | Skill | Summon 2 random performers. [cost 0] (2026-09-25: the face follows the full-stage ruling, rule 3.) |
| Tutti! | 1 | Skill | All your performers act now. [Retain] (2026-10-03, [USER]'s run notes: was 2, 1 upgraded.) (Round four: was 2, 1 upgraded; round four's 1 and 0 undone in the 2026-09-26 balance review.) |
| Bravura | 1 | Attack | Spend your back performer's Fanfare. Deal 5 damage, plus 4 per point. (The rules pass, 2026-10-01: face trimmed.) [plus 5 per point] (2026-09-29 fade pass, §18: was plus 3, 4 upgraded.) (2026-09-29 Bravura fix, §16: was 3 per point, no base, 4 upgraded.) |
| Full House | 3 | Power | If all three seats are filled at the end of your turn, your performers act twice. [cost 2] (2026-09-26 balance review: was 2, 1 upgraded.) |
| Thunderous Applause | 1 | Power | Whenever a performer Bows, draw 1 card and your back performer gains 1 Fanfare. [gains 2] (2026-09-28 balance pass: was 2, 3 upgraded; the draw is unchanged.) |
| ~~A Rapt Audience~~ | 1 | Power | Whenever an enemy hits your front performer, your back performer gains 2 Fanfare. Needs 2 performers. [gains 3] (2026-09-26 balance review: was half the Fanfare lost, all of it upgraded. Copies add; a hit its Block fully absorbs does not count.) (2026-09-29: out of the pool, §17.) |

**Rares (two)**

| card | cost | type | text |
|---|---|---|---|
| Arkhe Alignment | 2 | Power | At the start of your turn, choose Ousia or Pneuma. (The Ousia and Pneuma tips carry the two modes: acts deal double damage; or acts give double Block and your front performer gains 2 Fanfare.) [cost 1] |
| A Five-Century Act | 3 | Power | The first time each turn a performer Bows and leaves, it returns at the back with 1 Fanfare if a seat is free. [returns with 3] (2026-09-30 power cost sweep: was 2, cost 1 upgraded.) (2026-09-27, once a turn however many copies; [USER]: "For the furina Fix items - I like your default.") (2026-09-26 seat round: two seats expected a performer that Bowed to make room on a full stage to return; the rule stays, since there is no free seat, and the face now says so.) |

How the edges resolve: Improvised Number and Between Acts check the stage
when played. Step Forward moves the back performer to the front and shifts
the others back one; with one performer it only gives Block. Bravura empties
the back performer exactly, so it always bows; on an empty stage it deals its base 5.
Double Casting with one open seat summons one. Full House: each performer's
act resolves twice, and each further copy adds one more act. Thunderous
Applause gives its Fanfare after the bowing performer has left, so on an
empty stage it lands on nobody (the rules pass, 2026-10-01; round four had it
summon), and the draw still happens. Let the People Rejoice's performers return to empty seats
only, so one that finds none does not return. Since the trio can be cloned (2026-09-25) the no-duplicate rule applies to guests only: a guest that a summon already brought back does not return a second time. A Rapt Audience does nothing while one
performer is both front and back. Arkhe Alignment's "double" multiplies the
act's printed number (Usher 6 Block, Chevalmarin 4 to every enemy, Crabaletta
10). One question a turn however many copies are in play: copies add (two
copies x3), and Pneuma's front-performer gain is 2 per copy. A Five-Century Act's returnee takes the back-most empty seat and does not
act that turn; after Let the People Rejoice a performer returns once.

Tips added: Ousia and Pneuma, on Arkhe Alignment and its power only (round
four: they had ridden Ousia Surge and Pneuma Refrain by name).

## 13. What the sim reports, and what round one asks

The sim, per run and per fight, under `FURINA_STAGE`:

- Spend fires: how many, split by the paying bar at the moment of Spend
  (1 to 2, 3 to 5, 6 and up) and by whether the target died.
- Performers lost by a hit, by a Spend, and by a full-stage summon (all three bow).
- Turns with one, two and three performers on stage, and the winrate of
  decks by their summon count.
- Fanfare absorbed on the lead against Fanfare Furina would have taken:
  the Refill-as-prevention price.
- A granted Preserve deck against a granted Expend deck on the same seeds.

Round one, three seats on one seed, natural starter plus the two granted
decks, and the debrief asks:

1. On turn one of fight one, which line, and why.
2. Did you ever spend a performer at 1 on purpose, and did that feel like
   a play or a loophole.
3. Did you want a second performer on stage, and what for.
4. Which performer did you protect, and could you say why in one sentence.
5. Did the three read as three, or as one Osty three times.

## 14. What GPT's read of draft 1 changed

All of it taken; none of it a redesign.

- Fight one's line C was called a trap; it is a trade (2 HP for 6 damage).
  §7 says so.
- Turn three's Refill line never used its reserve, and the damage line
  wins the fight; §7 shows both and says which is better here.
- Turn four showed harmless surplus, not a cash-out mistake; the claim is
  withdrawn, and holding a card needs Retain, which the starter lacks.
- A 1-Fanfare performer is the cheapest Spend, which makes an Expend deck
  as valid as a Preserve deck; §4 names both, §12 gives both cards, and
  "2 per Fanfare" is a nominal rate, not a measure.
- Chevalmarin's act works from any seat and the front is where rotation
  removes her; §5.3 corrected.
- A newcomer performs at once and, on a full stage, inherits a bar; §3 and
  §6 corrected.
- "Take a Bow" would teach a bow rotation does not grant; the card is
  Scene Change.
- Regen begins on the second turn, so the first hand sees 3; §3 rule 2.
- The lore table calls Fanfare-as-the-bar an adaptation.
- Two watch items added to §8: the lone Usher, and the three shields.

## 15. Balance pass one (2026-09-28)

[USER]'s Stage run on 2026-09-28 was "extremely easy" until an act-3 elite.
The review found Fanfare generation too high, and the spend side fine: "I
actually think the spend is totally fine; it's the generation that's the
issue. Let's leave these alone for now." Bravura and every spender are
unchanged. Ruled, and built on `furina-stage-balance-1`:

1. **Dual Nature**: the upgrade is +1 draw (draw 2) instead of cost -1; it
   stays 1 cost. "I think a is good".
2. **Guest Star: Lynette, Sigewinne, Wriothesley**: the guest arrives with 5
   Fanfare, not 8; the upgrade stays +2 (7). "a) is good for now. This is
   much more effective block than a Necrobinder deck gives, but the per-card
   amount is fine; it's more the frequency that's higher."
3. **Gala Dinner** gives each performer 2 (3 upgraded); **Season Tickets**
   gives 1 a turn (2 upgraded); **Thunderous Applause** gives 1 Fanfare a Bow
   (2 upgraded), its draw of 1 a Bow unchanged. "agreed".
4. **No change to Bravura or any spender** (the quote above).
5. **Plot Twist** is an Attack: "Reverse the order of your performers. Deal 7
   damage." (10 upgraded), at one enemy, no Block; cost 1, Common. "a)".
6. **Understudy and the Gentilhomme Usher card leave the pool**, 80 cards to
   78. Usher the performer stays. "agreed on a)".

Row provenance: `docs/notes/prototype-surface-provenance.md`, "Furina, the
Stage — balance pass one".

## 16. The Spend pass (2026-09-28)

After balance pass one, two Sonnet seats both cleared both A0 bosses
comfortably. [USER]: "If Furina is still generating too much Fanfare and not
enough damage, we could solve her problem by upping both the spend and output
of her cards." So the five fixed-Spend cards cost more Fanfare and pay more.
Each keeps its upgrade shape.

| card | plain | Spend mode | upgraded |
|---|---|---|---|
| Quick Cue (0) | 3 damage | Spend 3: deal 11 and apply Hydro | 4 / 12 |
| Spirited Aria (1) | 8 damage | Spend 3: deal 11 and draw 2 cards | 11 / 14, draw 2 both |
| Tidal Flourish (1) | 5 to ALL | Spend 3: deal 10 and apply Hydro to ALL | 8 / 13 |
| Interposition (1) | 5 Block | Spend 3: gain 13 | 8 / 16 |
| Grand Entrance (2) | 12 damage | Spend 7: deal 32 | 16 / 36 |

Spirited Aria's face now reads "Deal 8 damage. Spend 3: deal 11 and draw 2
cards instead." Quick Cue's upgrade is +1 on both numbers (it was +1 and +2).
Not changed: Curtain Rise (the starter is [USER]'s pick), Bravura, Bring the
House Down, Let the People Rejoice, and the performers' acts.

**Spend legibility.** Both seats: "Spend 2 wasn't offered on some turns and
offered on others; I only learned by trying." The game offers a Spend mode
only when the back performer can pay the whole price, and otherwise plays the
plain mode without opening the chooser. The blind-seat page now prints the
refused mode under its hand card, marked "unavailable" with the reason (for
example "your back performer has 2 Fanfare"). The game's chooser is
unchanged: it has no greyed-out state to show.

Row provenance: `docs/notes/prototype-surface-provenance.md`, "Furina, the
Stage — the Spend pass".

**Bravura (2026-09-29).** The Spend pass left Bravura alone. The Sonnet seats
of 2026-09-28 (run FSR3RUN2Q7XB, acts 1 to 3) named it their "never again"
card: "Bravura -- deals 3 damage per Fanfare of a back performer that is
almost always 1". Under the same direction ("upping both the spend and output
of her cards") it gains a base: "Spend all of your back performer's Fanfare.
Deal 5 damage, plus 3 per point." Upgraded, plus 4 per point; the base stays 5.
At 1 Fanfare it deals 8 (was 3); at 4 it deals 17 (was 12).

## 17. The audit pass (2026-09-29)

[USER] asked for "a dedupe / audit / balance pass on Furina, aimed at
polishing the existing core systems", with three standing notes from his
2026-09-28 run: "too many cards give very high amounts of Fanfare", "stage
rotation spam", and "damage is missing from the Commons". The evidence is a
factual packet read off the sheet and the twelve seat records (seven on the
current build, four older, one empty): §4 counts which cards the seats named,
§5 prices every Attack and Block card per Energy. Designed by the main
session; built on `furina-audit-pass`.

**Cut (three; the pool is 75, was 78).**

| card | why | evidence |
|---|---|---|
| Gala Dinner (Uncommon) | a generation card, and generation is the excess | named by none of the 12 records (packet §4b) |
| A Rapt Audience (Uncommon) | a generation Power | named by none of the 12 records (packet §4b) |
| Scene Change (Common) | a third rotation Common beside Plot Twist and Step Forward, with Revolving Stage above them | "stage rotation spam" ([USER]); 4 mentions, none a pick, passed over at a draft ("Wriothesley over Scene Change", fs-run3 act 1) |

**Numbers (base, then upgraded).**

| card | now | was | evidence |
|---|---|---|---|
| Ensemble Piece (Common) | 5 per performer [7] | 4 [5] | NEVER AGAIN: "it was a 0-cost 9 damage that did nothing a Strike wouldn't" (fs-run3 act 3) |
| Improvised Number (Common) | 8 [11] | 6 [9] | "damage is missing from the Commons" ([USER]); 6 per Energy, lowest single-target Common (packet §5) |
| Ousia Surge (Uncommon) | 3 plus 1 per back Fanfare [base 6] | 0 plus 1 [base 4] | 1, 3 or 5 damage at 1, 3 or 5 Fanfare (packet §5); "Ousia/Pneuma type cards never came up" (fs-run2 act 1) |
| Pneuma Refrain (Uncommon) | 3 Block plus 1 per front Fanfare [base 6] | 0 plus 1 [base 4] | 1, 3 or 5 Block at 1, 3 or 5 Fanfare (packet §5); "only OK" (fs-run act 1) |
| Final Bow (Uncommon) | Block equal to twice the Fanfare; the upgrade still removes Exhaust | once the Fanfare | 5 Fanfare gave 5 Block, worse than a Defend; passed over on all four draft screens that offered it, one on the old build (packet §4d) |
| Bring the House Down (Rare, 2) | 3 to ALL per point [4] | 2 [3] | 1, 3 or 5 per Energy at 1, 3 or 5 Fanfare (packet §5); 3 mentions, never in a deck |
| Grand Deluge (Rare, 2) | 12 to ALL [16] | 10 [14] | 5 per Energy at Rare (packet §5), against [USER]'s "5 to 7 damage per 1 energy is roughly the going rate on AoE commons" (Kokomi Casket pass) |

The faces: Ousia Surge "Deal 3 damage, plus 1 for each Fanfare on your back
performer."; Pneuma Refrain "Gain 3 Block, plus 1 for each Fanfare on your
front performer."; Final Bow "Your back performer Bows and leaves. Gain Block
equal to twice its Fanfare." Each keeps its in-combat number.

**Two fixes.** In a boss fight only minions can be Frozen and every other
creature takes Vulnerable instead (LAW §Combat); a seat saw "Frozen" on Vantom
and was hit for 26 (fs-run3 act 1). The Frozen preview and the seat page's
Frozen row now say "In a boss fight, only minions can be Frozen; the others
become Vulnerable instead." The doubled end-of-turn preview (the same record:
Neuvillette "8 Hydro to ALL, twice", the second act "could not pay") was not
the forecast skipping a payment: both engines' forecasts pay each Full House
repeat on the copy before counting it, now pinned on a board where
Neuvillette at 5 pays once. Its cause is still open (`BACKLOG.md`).

Row provenance: `docs/notes/prototype-surface-provenance.md`, "Furina, the
Stage — the audit pass".

## 18. The fade pass (2026-09-29)

After his first run on the new starter, [USER]: "I swear that I have never
seen it tick down any of the summons in-game before." Then his direction:
"make Fanfare deplete faster, but make that depletion more impactful. Keep her
Block cards generally weak but her Spend cards strong." On the shape: "What
about a percentage fade, say 25%? Anything below 4 rounds to losing 0." And
on the whole pass: "Yes, please proceed!" Designed by the main session; built
on `furina-fade-pass`.

**The evidence.** The main session's sim read (200 fights per deck, the
`tank_boss` instrument): draft 3's rule 12 (half of the Fanfare above 5,
behind the front only) fades 0 to 2 Fanfare a fight in every deck, against 16
to 49 gained, and exactly 0 in the natural starter, bank and solo decks. The
fade was real on paper and invisible in play.

**The rule (rule 12, rewritten above).** At the end of Furina's turn, after
the acts, every performer, the front one included, loses a quarter of its
Fanfare, rounded down: 0 to 3 lose 0, 4 to 7 lose 1, 8 to 11 lose 2, 12 loses
3, 20 loses 5. A quarter never empties a performer, so the fade never causes a
Bow. The face, wherever the game or the seat page states the rule: "At the end
of your turn, each performer loses a quarter of its Fanfare, rounded down."
Grand Theater Program still turns the fade off.

**Cut (three; the pool is 72, was 75).** Held Applause (skip one fade),
Echoing Hall (half the fade's loss to the front) and Eternal Applause (fade
only above 10). Each bent the old line, and the new rule has no line to bend;
their engine code left with them.

**Spend buffs (base, then upgraded).** Only the Spend mode or the Spend payoff
moves; the plain mode stays, and every Block card is unchanged.

| card | now | was |
|---|---|---|
| Curtain Rise (starter) | Spend 3: deal 17 [21] | 13 [16] |
| Tidal Flourish (Common) | Spend 3: deal 13 to ALL [16] | 10 [13] |
| Quick Cue (Common) | Spend 3: deal 14 [16] | 11 [12] |
| Spirited Aria (Common) | Spend 3: deal 14 and draw 2 [17] | 11 [14] |
| Grand Entrance (Uncommon) | Spend 7: deal 40 [45] | 32 [36] |
| Bravura (Uncommon) | 5 damage, plus 4 per point [plus 5] | plus 3 [plus 4] |
| Bring the House Down (Rare) | 4 to ALL per point [5] | 3 [4] |

Not changed: Interposition, Final Bow, Let the People Rejoice, and every Block
card. Curtain Rise is a starter card; [USER] approved the pass that moves it.

Row provenance: `docs/notes/prototype-surface-provenance.md`, "Furina, the
Stage — the fade pass".

**After his run on the fade pass (2026-09-29).** [USER]: "Overall I think
she's in a better spot... keeping Fanfare fed enough to use them was an actual
challenge! One issue on Wriothesley is that keeping him in the front was
actually hard. Can we pin him to the front of the Stage while he's present?
And I think Siegwinne needs to be rethought - she's strictly fanfare-negative
while she's summoned." Two changes (guest paper, frame rule 2 and the guest
table): Wriothesley holds the front while he is on the stage (no seat move
takes it from him; a full-stage summon Bows the performer behind him
instead); Sigewinne is the medic, free: "Your front performer regains half
the Fanfare hits took from it since her last act, at least 2."

## 19. The rules pass (2026-10-01)

Paper `review/ruled/furina-rules-pass-2026-10-01.md`, all picks ruled
([USER], on the check-in: "she finally has a good design to stand around, but
let's do a similar audit (rules, card pool, lore) to look for what we can
improve upon"). Built in both engines.

**Rules (§3 above).** Rule 8: a Spend pays the back performer first, then
forward, refused only when the whole stage holds less. Rule 5: only a card or
potion you play summons on an empty stage. Rule 4 is cut; The Curtain Never
Falls keeps its regain of 2. Wriothesley is "Always your front performer".
Palais Ledger now reads "Your Spends cost 1 less Fanfare"; Center of
Attention reads "The first Spend you choose each turn takes no Fanfare."

**The old-kit cards.** Her twelve surviving old-kit rows are prototype rows
now. Singer of Many Waters: "Your front performer gains 6 [9] Fanfare.
Exhaust." Three Attacks replace the Companion feeders: Opening Number (Common,
1: deal 9 [12]; if it is the first card you played this turn, your back
performer gains 2 Fanfare), Leading Lady (Uncommon, 1: deal 6 [9], plus 1 for
each Fanfare on your front performer) and Endless Waltz (Rare, 2: deal 14
[18] to ALL; each performer with 5 or more Fanfare acts). Commanding Gaze,
Undercurrent, Stage Combat, Courtroom Drama, Crashing Waves, Duet, Quick
Change and The Witness Stand are ported as they are. The pool stays 78.

**Text.** Quick Cue's Spend deals 11 [13]. The Bow tip covers Grand Finale
("as it leaves the stage or, if a card says so, stays"); Bring the House Down
adds "If it empties, it Bows."; Grand Deluge, Bravura, Guest of Honor, Pneuma
Refrain and Stage Whisper are trimmed. The damage order moved from the
Fanfare tip to the front performer's ("Takes hits after your Block; what its
Fanfare cannot hold reaches you."), so the Fanfare tip carries the empty-stage
line within the tip ceiling.

Row provenance and the builder's readings:
`docs/notes/prototype-surface-provenance.md`, "Furina rules pass,
2026-10-01".

## 20. Run-note changes (2026-10-03)

[USER]'s run notes, built as ruled:

- **Rule 12 moves to the start of her turn.** "Fanfare decay should be at the
  start of the next turn, not the end." The fade is the first thing her turn
  does, from her second turn on, so the enemies' hits meet the bars before
  they fade. The amount is unchanged. The tip and the Stage badge now say "at
  the start of your turn".
- **Tutti!** costs 1 (was 2). Its upgrade gives Retain (was cost -1).
- **Gala Premiere** costs 1 (was 2), 0 upgraded, and still Exhausts.
