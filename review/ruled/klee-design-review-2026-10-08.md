Status: RULED 2026-10-08 (all five picks at the defaults; building)

# Klee design review: the starter, the rules, the pool, 2026-10-08

Asked for by [USER] after suite 4 and the turn-one paper: "I think this
calls for a design review ... draft a paper going over the full card pool
and archetypes for a deeper analysis - I want to see if we really need to
mess with the starters, or if the starters are in fact the problem, and
what the most thematic solutions might be to the overall snarl we're in."

Pool read from `origin/klee-next` aeb2c069 (`KleeOverhaulRoster.Slice`, 78
cards; the row texts from `docs/prototype-surface.yaml` on that branch).
Base pools from `game_ref/<character>.json`. Fight numbers from the fight
telemetry (`tools/telemetry_report.py`, `load_fights`), bot feed, one seat,
normal fights unless a boss row is named; windows as the suite records give
them (base five 2026-10-05 before 16:50; Klee suites 2 and 3 2026-10-07
01:39 to 03:13 and 13:29 to 14:21; the Common test arm 03:13 to 04:20;
suite 4 from 20:46). Seat quotes are from the gitignored seat records in
the session scratchpad (`suite3/`, `suite4/`, `seat-laneN/record-actK.md`).

---

## Summary: is the starter the problem?

**No. The starter is where the slow turn one is visible; the rules and the
pool are where it comes from.** Three findings carry that:

1. **The starter can deal a base character's turn one and chooses not to.**
   Jumpy Dumpty (Bomb 8) plus Ka-pow! (Set off, 4) on turn one is 12 damage
   for 1 Energy: the same as two Strikes for 2. Seats never do it. In 85
   act-2 and act-3 normal fights across suites 2 to 4, Jumpy Dumpty was
   played on turn one 85 times and Ka-pow! on turn one 0 times. They hold
   because rule 1 (Bombs grow 4 a turn) pays them 4 free damage for every
   turn they wait, and because Ka-pow!'s Retain makes waiting cost no card.
   The card is a cash button; the rule says never press it yet.

2. **In act 1 the starter explains the whole turn-one gap, and the gap is
   repaid on turn two.** Klee's act-1 turns read 14 / 28 / 20 / 19 against
   the base five's 20 / 20 / 18 / 11 (tempo paper, sec.1): she is 6 behind
   on turn one, the price of 1 Energy spent on a Bomb instead of a Strike,
   and 8 ahead on turn two. Act-1 damage and HP lost are within a few
   points of the base five in every suite (ratios 1.01 to 1.07; 0.65 to
   1.04). The starter's slowness is a one-turn loan that act 1 pays back.

3. **In act 3 the gap is 50 points and the starter can account for 12 of
   it at most.** Base decks open an act-3 fight with 57 to 62 damage; Klee
   opens with 5 to 9. Her decks play as many cards on turn one as theirs
   (3.7 to 4.1 against 3.1 to 4.3) and spend them on placers (2.2 a turn in
   act 3), Powers and Block, because that is what her Common layer offers:
   7 of her 25 Commons are Attacks (the base five: 9 to 13 of 20), 8 are
   single-Bomb placers that deal nothing the turn they are played, and her
   only scaling is **time**: a Bomb grows with the turn count, not with the
   deck. Base decks scale with the deck (Inflame and Shivs are the two
   commonest act-3 turn-one plays in the base runs). Deck-scaling pays on
   turn one of every fight; time-scaling pays on turn four. That, not the
   starter, is why her act-3 fights run 4.7 turns to their 3.3 and why she
   loses 1.57 times their HP there while gaining more Block a turn.

**What to do, in the stage gate's order.** No starter change. (i) Rule 1:
Bombs grow 2 a turn, not 4; Alice's Recipe still doubles it. Rule 4: she
starts each combat with 3 Sparks, not 1 (Regent opens with 3 Stars). Every
drafted placer prints 2 bigger, so a Bomb cashed the turn it lands is worth
what it is worth today and a Bomb held three turns is worth less. This is
the turn-one paper's default and [USER]'s proposal with one addition. (ii)
Two Commons in, two out: **Fire! Fire!** (her normal attack: place a Bomb
and set the enemy off in one card, so a deck that never cooks still has
Bomb-typed damage and a Spark every turn) and **Blasting Spree** (a Bomb on
ALL enemies for a Dazed: Spray's fuel and the status bridge [USER] asked
for); Playdate and Pop! out. (iii) Cook stays in the pool as a
drafted plan (Alice's Recipe, Chain Fuse, Witch's Homework, Stoke the Fuse,
Half a Mountain, Simmer, Taste Test) and stops being the only plan the
starter can teach. Under growth 2 the starter's lesson becomes "plant, then
pop when it pays", which is the fast-and-fragile character [USER]
described, with the same ten cards.

What the data cannot settle is in sec.1.4. The picks are at the end.

---

## 1. Starter, rules, pool: what each one does to turn one

### 1.1 What the starter does

Ten cards: Strike x4, Defend x4 (the base game's), Jumpy Dumpty (1 Energy,
Innate: place a Bomb 8; when it goes off, a Mine 3 on ALL enemies) and
Ka-pow! (0 Energy, Retain: Set off the enemy, 4 Pyro). Relic: Pounding
Surprise, 1 Spark per Bomb that goes off (`Relics/PoundingSurprise.cs`).
Rule 4 adds 1 Spark at the start of every combat.

Measured, all suites, every act: **Jumpy Dumpty is the first card of every
fight.** 104 of 104 act-1 fights and 85 of 85 act-2 and act-3 fights in
suites 2 to 4; the seats call it "automatic" and "always the right play".
Ka-pow! on turn one: 8 of 104 in act 1 (all in suites 2 and 3, none in
suite 4), 0 of 85 later. The first Set off of a fight comes on turn 2 as a
median in every act and suite; in suite 4's act 2 the median is turn 3.
Half of the act-2 and act-3 fights (50 of 85) have seen a Set off by the
end of turn two; the other half have not.

So the starter puts a Bomb on the table on turn one, every fight, and the
detonator waits. Two things on the starter itself make waiting cheap:
Innate on the placer (the Bomb starts growing a turn earlier; restored
2026-10-03 after the sanity round lost the act-1 boss twice without it,
`docs/notes/prototype-surface-provenance.md`), and Retain on the detonator
(the row has `retain: true` on the base face; the brief's sec.8 and the
slice packet had Retain on the upgrade only). Neither is wrong on its own.
Innate is what makes the plan legible on turn one; Retain is what keeps a
detonator in hand in a pool where detonators are scarce (sec.1.3). They
become a slow-play machine only because of the rule below.

### 1.2 What the rules do

**Rule 1, growth 4.** A Bomb 8 cashed on turn one is 8; on turn three, 16.
Holding costs nothing (Retain), so holding is right unless the enemy is
about to die or about to hit hard. The seats learned exactly that rule and
wrote it down: "hold Ka-pow! when the Bomb is still growing" (suite 4,
Defect seed, act 1, rules learned). It is correct play, and it is the
opposite of fast.

The tier-0.5 sim shows the other side (turn-one paper, sec.1): a pilot that
cashes immediately deals 45 on act-3 turn one with today's rules, near the
sim's base Ironclad at 49. The same decks can be fast. The rule pays them
not to be. Growth 2 in the sim costs that fast pilot 1.5 points of win rate
(5.1% to 3.6%) because every Bomb it cashes is smaller; +2 on every placer
pays it back (4.8%). The sim cannot cook, so it cannot show what growth 2
does to a cooking seat; that is what the round is for.

**Rule 4, 1 opening Spark.** Eight of her 25 Commons cost a Spark (Tinder
Toss, Quick Fuse, Booby Trap, Dig In, Blast Shield, Bottomless Bag, Boom
Badge at 2, Explosive Spark). With 1 Spark, one of them is live on turn one
and Boom Badge is not. Every seat record since the scaling rounds names the
dead Spark card: "Boom Badge and Blazing Delight sat dead in hand at 1
Spark on four early turns" (scaling round 1); "only 1 Spark so Boom Badge
(2 Sparks) was dead in hand" (suite 4, Silent seed, act 1); "1 Energy
unspent because I had no set-off (Boom-Boom Strike needed 2 Sparks, I had
1)" (suite 4, Defect seed, act 2). The first explosion is the only Spark
income, so the Spark cards wait for the first cash, and the first cash
waits for the Bomb to be big. The two rules lock each other.

Regent opens every combat with 3 Stars and Venerate makes 2 more; the
brief (sec.19) already used Regent's 3 as the yardstick when Dodoco Tales
was set. Three opening Sparks is the base game's own number.

### 1.3 What the pool does

**Turn one in act 3, by what was played.** The base five's commonest
turn-one cards in act-3 normal fights: Inflame 18, Shiv 16, Strike 15,
Defend 10, then Open the Casket, Frostgnaw, Bash, Finisher, Blade Dance,
Shrug It Off, Claw. Klee's (suite 4): Jumpy Dumpty 18, Klee's Secret Base
6, Oz 4, Pop! 4, Damage Report 3, then Run Away!, Bottomless Bag,
Windtrace, Look Out!, Mine Toss, Spark Knight, Bombs Away!. One list is
damage with a Power on top; the other is placers and Powers with Block on
top. She is not short of Energy or cards on turn one (3.7 cards played to
their 4.3). She is short of cards that do something on turn one.

**Why: the Common layer.** 25 Commons; 7 Attacks and 18 Skills, no Powers.
The base five's Common layers are 9 to 13 Attacks of 20. Of her 7 Common
Attacks, three are Set off cards whose value on an empty board is 3 to 6
(Tinder Toss, Sizzle, Pocket Match), and the four that hit without a Bomb
are Fish Blasting (8 to ALL, a Confiscated), Forbidden Fun (10, a Dazed),
Simmer (4 plus half the largest Bomb, a Dazed) and Explosive Spark (12 for a
Spark). Her 8 Common placers (Pop!, Mine Toss, Lizard-Tail Gunpowder,
Booby Trap, Coven Errand, Bombs Away!, Windtrace, Playdate) each place one
Bomb of 3 to 8 and deal nothing now. The Silent's equivalent, Blade Dance,
is three Shivs for 1 Energy: 12 damage this turn, on cards that Accuracy
and Phantom Blades scale with the deck.

**Set off is scarce, and the rule makes that bite.** 13 of 78 cards set off
(5 Common: Tinder Toss, Quick Fuse, Sizzle, Countdown, Pocket Match; 6
Uncommon: Big Badda Boom, Boom-Boom Strike, Perfect Timing, Flash Point,
Team Effort, Survival Rulebook; 2 Rare: The Big One, Windblume Fireworks).
The count is of cards whose effects perform a `set_off`. Four more rows
print the words and do not detonate (Boom Badge, Treasure Map, Sparkborne
Magic, Prune), so a text search reads 17 and the tempo paper's 18 counted
the same way on the older pool. A hand holding Boom Badge and no detonator
is the seats' "dead" hand, which is why this paper counts 13.
Two of the Commons cost a Spark and one (Pocket Match) sets off only the
largest Bomb. The runs in suites 2 to 4 played between 3 and 8 distinct Set
off cards each over a whole run (the Necrobinder seed in suite 4: Ka-pow!,
Countdown, Sizzle; it died on floor 9). A 25-card deck with Ka-pow! and two
drafted Set off cards draws an opening hand with none of them half the
time (50%); with four, 38%. The seats say the same in words: "the whole
offense depended on ONE card, Ka-pow!, and I drew it on only 2 of 8 turns -
bombs sat on the Priest unused" (suite 3, Silent seed, act-1 boss, lost);
"T5 had 4 Bombs on the Owl and no Set off in hand except Pocket Match. The
two Boom Badges and Stoke the Fuse are dead without one" (suite 4, Silent
seed, act 3). Rule 7 ("nothing fires by itself") is what makes the
shortage matter: a Defect's orbs fire their passive every turn whether or
not Dualcast is drawn; a Necrobinder's Osty attacks on its own. Klee's
deferred damage waits for a card. That is a chosen rule and a good one,
but it means the pool has to hand her detonators as freely as Shivs, and
it hands her 13 in 78.

**Where the damage comes from.** Bombs and Mines are 45% of her damage in
act 1 and 58% to 71% in act 3 (suite 4 and the test arm). Strike is 24% to
28% of her act-1 damage (the base five: 32%) and 2% to 3% in act 3 (base:
6%). Her act-3 damage is almost entirely deferred damage waiting for a
card.

### 1.4 What the data cannot settle

- **Whether [USER] cooks.** The seats are Sonnet; [USER] wins A0 to A5
  solo and found the loop "fun and interesting, with a challenge around
  bomb management" (STATE.md). If he cashes earlier than the seats, the
  turn-one numbers above overstate the problem for him. His next run should
  note turn-one plays.
- **Hands are not logged.** "No Set off in hand" is seat testimony plus the
  draw arithmetic above, not a count. Logging the hand at turn start would
  settle it (an instrument item, not a design one).
- **Act 3 rests on 18 fights (suite 4) and 9 (suite 3),** one run a seed.
  The act-3 ratios (0.79, 1.57) are a direction, not a measurement.
- **The sim never cooks,** so it prices the fast player only. Growth 2's
  effect on a cooking deck's boss turns is unmeasured.
- **Boss fights.** Act-1 and act-2 bosses are at or better than the base
  five (suite 4: act-1 boss HP lost 39% to their 47%, act-2 46% to 50%);
  the act-3 boss is the wall (61% on two fights, both lost, to their 35% on
  five, all won). Suites 2 and 3 also lost two act-1 bosses out of ten; the
  base five lost none of eighteen. Both losses were the Silent seed with a
  single detonator in the deck.

---

## 2. The 78 cards by archetype

Counts are from the sheet's own effects (`set_off`, `plant_bomb`,
`spend_spark`, `block`, `damage`), not from the printed text, except where
noted. A card can serve two lines; each is counted where it does its main
work. Pool 25 / 32 / 21; 21 Attacks, 40 Skills, 17 Powers; costs 0: 24, 1:
42, 2: 10, 3: 2.

### 2.1 Cook (the starter's plan today; 16 cards)

| Role | Cards |
|---|---|
| Grow or fetch (7) | Chain Fuse (C, +6 each on the enemy), Exquisite Compound (U, merge +5), Witch's Homework (U, largest +8), Stoke the Fuse (U, all Sparks into the largest at 5 each), Treasure Map (U, a Set off back, +3), Half a Mountain (R, double the largest), Alice's Recipe (R, growth doubles) |
| Multiply the cash (3) | Boom Badge (C, 2 Sparks: next Set off doubles), Big Badda Boom (U, 12 then what the Bombs dealt again), The Big One (R, x4) |
| Damage while cooking (2) | Simmer (C), Taste Test (U) |
| Defence or status (4) | Return to Sender (U), Favonius Escort (R), Jean, Lion's Fang (R), Albedo, Dust of Purification (R) |

- **Turn one:** Jumpy Dumpty, a Defend or two, maybe Chain Fuse. Nothing
  cashes. Act-3 turn one is 5 to 9 damage.
- **Damage source:** one pile, cashed once, multiplied. The best turns in
  every record are this: "Boom Badge + Big Badda Boom = 12 + 110 + 110 =
  232" (suite 3, Defect seed, act 3); "The Big One on a 43 bomb (172)"
  (suite 4, Ironclad seed, act 3). Big Badda Boom is the one card whose
  damage per play grows with the run (suite 1: 20.9, 34.8, 36.9).
- **Defence:** Block cards drafted to buy the waiting turns. This is the
  line that put her Block above the base five's (tempo paper, sec.1). The
  tempo paper cut its four "pay for waiting" cards; Jean still pays for
  waiting.
- **Where it is broken or thin.** It is not thin; it is the whole kit's
  centre of gravity, and it is slow by construction. Its cash button is
  the scarce card (sec.1.3). Its damage-while-cooking Commons are new
  (Simmer played in 4 fights, Taste Test in none, suite 4). Under growth 2
  the line needs Chain Fuse, Witch's Homework or Alice's Recipe to be a
  plan, which is what "opt-in" means (sec.3).

### 2.2 Spray (many Bombs, cashed fast, paid in Sparks; 30 cards)

| Role | Cards |
|---|---|
| Placers, Common (8) | Pop! (0, Bomb 5), Mine Toss (1, Mine 7), Booby Trap (0, 1 Spark, Mine 5), Lizard-Tail Gunpowder (1, Bomb 4, draw per Bomb gone off), Coven Errand (1, Bomb 8 or 12), Bombs Away! (1, Bomb 4 and Block), Windtrace (1, 6 Block and Mine 3), Playdate (0, Bomb 3 and a Companion discount) |
| Placers, Uncommon and Rare (7) | Jumpy Dumpty Mk.III (U, 3 hits of 3, Bomb 2 each: the one multi-placer), Klee's Secret Base (U Power, a Bomb 4 a turn), Party Poppers (U Power, a Bomb 3 per Spark card), Little Hexenzirkel (U Power, per Companion card), Dodoco (R Power, a Mine 3 a turn), All of My Treasures! (R), Windblume Fireworks (R) |
| Detonators (10) | Tinder Toss (C, 1 Spark, ALL), Quick Fuse (C, 1 Spark, +3 then Set off), Pocket Match (C, 0, Retain, largest only), Countdown (C, 1, draw 2), Sizzle (C, 1); Boom-Boom Strike (U, 2 Sparks, 8 and a Bomb 4), Survival Rulebook (U, 7 Block and Set off), Team Effort (U), Perfect Timing (U), Flash Point (U) |
| Sparks into damage (3) | Explosive Spark (C, 1 Spark, 12), Fireworks Finale (R, all Sparks, 5 to ALL each), Spark Knight (R Power, 3 to ALL per Spark gained) |
| Sparks into other things (7) | Dig In (C, 8 Block), Blast Shield (C, 4 Block, returns to hand), Bottomless Bag (C, draw 2), Sparkling Burst (U, Energy), Cover Your Ears! (U, Strength down), Blazing Delight (R Power), Tinkering (U, 2 Sparks for a Confiscated) |
| Engines and defence (4) | Chained Reactions (R), Sparks 'n' Splash (R), Run Away! (C), Look Out! (U) |

- **Turn one:** Jumpy Dumpty, Pop! or Booby Trap, a Strike. The one Spark
  buys one card. A deck of Spark cards is dead until the first cash, and
  the first cash is a Bomb 8 on turn two at the earliest.
- **Damage source:** Spark-priced detonators and Explosive Spark, once the
  Sparks flow; Spark Knight and Fireworks Finale as the Rare payoff.
  Explosive Spark was the most-played of the tempo paper's five (28
  fights; 6 of its 36 plays on turn one).
- **Defence:** Run Away! (0, 3 Block plus more if a Bomb went off), Dig In
  and Blast Shield from the bank, Look Out! from Mines. The seats call
  Blast Shield "the best block in the kit" and one played it 22 times in 3
  fights (suite 4 record). This is Spray's version of the Block problem:
  the bank buys Block instead of damage because the damage card is Rare
  or 12 for a Spark.
- **Where it is broken or thin.**
  - **Fuel is single and slow.** Every Common placer places one Bomb of 3
    to 8 that pays nothing this turn. The Silent's Shiv line has 13 makers
    and its Common ones pay now. Her only multi-placer is an Uncommon
    Attack (Mk.III); her only "a Bomb every turn" is an Uncommon Power
    (Secret Base). Pop! is named "NEVER AGAIN" or "never wanted" in six
    records across suites 2 to 4 and the test arm.
  - **The Spark gate on turn one** (sec.1.2): Boom Badge and Boom-Boom
    Strike need 2 and she has 1.
  - **No Common that places and sets off in one card.** Every Spray turn
    is two cards from two piles. The suite 4 picks already named this
    lever.
  - Mines on a boss "fire pre-attack and waste growth" (three records).
    Under growth 2 they waste half as much, and a Mine that pre-empts an
    attack is the fastest defence she has.

### 2.3 React (7 cards)

Sizzle (C), Perfect Timing (U), Flash Point (U), Wait For It... (U),
Sparkborne Magic (R), Aftershock (R), Prune, Hexhunter Chime (U, Klee's
own companion: Swirl, and the next Bomb set off deals the Swirled element).

- **Turn one:** a companion applier (Mika, Diona, Kaeya, Oz) and the Bomb.
  The payoff is next turn's Melt or Vaporize on the oldest Bomb.
- **Damage source:** the first Bomb's multiplier (Melt 1.75). "Ka-pow!
  (Bomb 15 Melt = 26, +4)" (suite 4, Defect seed, act 1). Real and liked
  when a Cryo companion is in the deck.
- **Defence:** none of its own.
- **Where it is broken or thin.** It is companion-fed by [USER]'s ruling
  (later-acts round, pick 1 (a)), and that stands. Two things to check,
  not to redesign: Perfect Timing's replay "never fired in any fight where
  I read it" (suite 4, Defect seed, acts 1 and 2; the seat's reactions came
  from Mika's hit, not the Bomb, but a Melt on Ka-pow!'s Bomb should have
  counted); and Wait For It... "never fired - I carried it dead the whole
  run" (suite 3, Silent seed). Both may be display or timing. One line
  each in the round.

### 2.4 Companion (8 cards)

Coven Errand (C), Playdate (C), Little Hexenzirkel (U Power), Team Effort
(U), Tag Along (U), Come Back and Play! (U), Alice's Introduction Magic
(R), Adventure Club (R).

- A side line that reads the companion slot. Coven Errand is drafted on its
  own merits (a Bomb 8 for 1 Energy, Common; 8 turn-one plays in suites 2
  and 3, act 2). Playdate is "never wanted" (later-acts round) and was not
  played once in suite 4's 73 normal fights. The line is thin
  but it is meant to be: the brief's sec.7 calls it a bridge, not a loop.

### 2.5 Status (15 cards: 10 loaders, 5 payoffs)

Loaders: Fish Blasting, Forbidden Fun, Up in Smoke!, Simmer (C); Lisa's
Treats, Behind Jean's Desk, Taste Test, Tinkering, Dodoco Tag (U); Red
Knight (R). Payoffs: Finders Keepers, Klee Can Explain!, Kitchen Alchemy
(U); Damage Report, Albedo (R).

- The payoffs are still almost never played (suite 4: Damage Report 3,
  Kitchen Alchemy and Klee Can Explain! 0). The loaders that reached decks
  were Dodoco Tag (23 fights; "clogged the hand") and Forbidden Fun. [USER]
  wants this line to bridge Cook and Spray; it has Cook's half (Simmer,
  Taste Test: read the Bombs, do not pop them) and lacks Spray's half
  ("planting lots of bombs in exchange for statuses"). Sec.4 adds it.

### 2.6 Mines (10 cards, across lines)

Jumpy Dumpty's payload, Mine Toss, Booby Trap, Windtrace (C); Mine, All
Mine!, Hair Trigger, Exquisite Compound's rider, Explosive Frags, Look Out!
(U); Dodoco (R).

- A Mine is the one thing in the kit that fires without a card (rule 6: it
  goes off when its enemy attacks her, before the hit). It is both her
  fastest damage and her only Block that scales ("only the Mine plus Look
  Out! line scales", suite 3, Ironclad seed). It is under-used because a
  Mine on a boss fires at a small size. Growth 2 and +2 on placers help it
  twice: the Mine is bigger when placed and loses less by firing early.

### 2.7 Block, counted

14 cards grant Block (5 Common: Dig In, Run Away!, Bombs Away!, Blast
Shield, Windtrace). The base five hold 10 to 13 (4 to 6 Common). The count
is inside the range since the tempo paper; the Block she gains a turn is
not (suite 4: 3.7 / 6.7 / 9.8 by act to their 2.2 / 2.9 / 7.5), because
she buys Block with the turns a slow fight gives her and with the Sparks
the bank gives her. Less Block is a result of shorter fights, not a cut.

---

## 3. Should Cook stay the starter's taught plan?

The brief's sec.1 says the starter teaches "plant, wait, boom" and
everything else is a branch. [USER]'s direction (tempo paper, sec.1) is
that she should "kill the enemies faster than other characters in exchange
for chip damage in long fights". Those two sentences cannot both be true
of the same starter under growth 4.

Three ways to resolve it:

- **Change the starter so it teaches Spray.** Replace Jumpy Dumpty with a
  plant-and-pop card, or make Ka-pow! place a Bomb. This loses the
  Dodoco-themed placer, the Mine payload (the one fast defence the starter
  has) and the badge-reads-11-at-dawn moment the brief's sec.8 is built on.
  It is a starter change, so it is [USER]'s, and nothing in the data asks
  for it: the starter's two cards already add up to a Strike's worth of
  damage on turn one.
- **Keep the starter and the rule, add fast cards to the pool.** Fire!
  Fire! and Blasting Spree (sec.4) alone. Act-1 turn one would still be Jumpy
  Dumpty and a hold, because growth 4 still pays 4 to wait. The drafted
  deck gets faster; the taught plan does not.
- **Keep the starter, change the rule, add the fast cards.** Under growth
  2, Jumpy Dumpty's Bomb 8 cashed by Ka-pow! on turn one is 12 plus a Mine
  3 on every enemy and a Spark now; held to turn two it is 14. The decision
  is still "is it enough yet" (lethal, a Block threshold, a stun line, a
  soft turn coming), which is the decision the seats enjoy ("the whole
  turn was 'which turn do I spend the stack'", suite 3), but "always wait"
  stops being the answer. The starter's ten cards and its lore are
  untouched; its lesson changes from cook to **plant, then pop when it
  pays.** Cook becomes the plan you draft into: Alice's Recipe (growth
  back to 4), Chain Fuse, Witch's Homework, Stoke the Fuse, Half a
  Mountain for the number; Simmer and Taste Test for damage while you
  wait; Jean, Return to Sender, Favonius Escort for the waiting turns. That
  is 10 cards and a Rare that breaks the rule, which is what the brief says
  a loop needs.

The third is the recommendation. It is the only one that changes what the
starter teaches without changing the starter.

---

## 4. The solutions, in the stage gate's order

The order (`operations/stage-gate.md`): a display or tip corrected, an
existing card adjusted, access improved, two redundant cards merged or one
cut, a new capability, a core rule changed. The lore each change stands on
is from the brief's sec.2 table.

### 4.1 Display (no pick needed; backlog lines)

- The shop lists Explosive Spark at "cost 0" without its Spark price
  (suite 4 record; already a backlog line).
- Perfect Timing's replay and Wait For It...'s trigger: check that a Bomb
  reacting inside the Set off that the card itself performs counts as
  "this turn" (sec.2.3). If it does not, that is a defect, not a design
  question.
- Boom Badge's Retain reads as if the doubling carries over (scaling round
  1, item 2). Tip: "this turn only".

### 4.2 Existing cards adjusted

- **Every drafted Bomb or Mine placer prints 2 bigger**, base and upgrade
  (the turn-one paper's default): Pop! 7, Booby Trap 7, Mine Toss 9,
  Lizard-Tail 6, Coven Errand 10 / 14, Bombs Away! 6, Windtrace 5, Mk.III's
  per-hit Bomb 4, Secret Base 6 / 8, Party Poppers 5, Little Hexenzirkel 5,
  Dodoco 5, Boom-Boom Strike's Bomb 6, Windblume's 8, and so on. Jumps and
  copies (Aftershock, All of My Treasures!) do not. **Jumpy Dumpty does
  not**, unless [USER] picks it (pick 4). This is the half of the rule
  change that keeps a Bomb cashed now worth what it is today.
- **Only if rule 4 stays at 1 Spark:** Boom-Boom Strike 2 Sparks to 1, so
  Spray's signature card is live on turn one. With 3 opening Sparks it is
  live already and should stay at 2.

### 4.3 Access

Boom Badge is Common since suite 3 and reached decks (10 fights, 2 of 5
runs). Nothing further here; the two new Commons below are the access
change for detonators and fuel.

### 4.4 Cut (two Commons, to keep 78 at 25 / 32 / 21)

- **Playdate** (0, Bomb 3 and a Companion discount). "Never wanted"
  (later-acts round); not played once in suite 4's 73 normal fights. The
  companion line keeps seven cards.
- **Pop!** (0, Bomb 5). Named "NEVER AGAIN" or "never wanted" in six
  records across suites 2 to 4 and the test arm ("a 0-cost 5-size Bomb that
  rarely got set off"); 19 plays in suite 4, mostly turn-one filler.
  Blasting Spree takes its job (cheap Spray fuel at Common) and does it for
  three enemies. Klee Can Explain! transforms statuses into Pop!, so the
  card stays in the build off-pool, the way the token statuses already do
  (`KleeOffPoolCards.cs`); only its reward-screen slot goes.
- **Not Bombs Away!**, which a first draft of this paper cut on direction
  (a Block card). It is the seats' most-played drafted card (24 plays in
  suite 4, 82 across suites 2 and 3 and the test arm); one seat drafted it
  on purpose ("wanted block that also plants"), one wrote "NEVER AGAIN";
  and [USER] kept Blast Shield and Kitchen Alchemy over a census for the
  same reason ("I personally found ... quite useful in my runs"). A card
  people play is not the second cut. The Block count stays 14, inside the
  base five's range; less Block a turn is to come from shorter fights, not
  from this list.
- Alternative second cut: Simmer (4 plays, one seat's "weakest card"). It
  is new and unread, so this paper keeps it one more round.

### 4.5 New capability: two Commons

**Fire! Fire!** (Common Attack, 1 Energy, Pyro). Her normal attack in the
source game, *Kaboom!*: she throws bombs that explode on impact. The name
"Kaboom!" is not reused: it was the renamed starter Strike until R242, it
sits one letter from "Ka-pow!" in a hand list, and a drafted "Kaboom!" was
renamed "Sparks Fly" two days ago for that reason. "Fire! Fire!" is her own
line when she throws. Alternatives for the naming audit: "Dodoco Toss"
(though Dodoco, Dodoco Tag and the Dodoco Tales relic already share the
name) and the plain "Bomb Throw".

> Place a Bomb 7 on the enemy. Set off the enemy.

Upgrade: Bomb 10. On an empty board it is 7 Pyro damage and 1 Spark for 1
Energy, against Strike's 6 and Regent's Solar Strike (Common, 1: 9 damage
and 1 Star). Its damage is an explosion, so Boom Badge doubles it, Big
Badda Boom reads it, Chained Reactions and Spark Knight fire on it, and it
cashes whatever is already cooking on the enemy. After Jumpy Dumpty on
turn one it is 8 plus 7, a Mine 3 on every enemy and 2 Sparks for 2 Energy:
a base character's turn one, from her own rules. It does not take the +2
of sec.4.2 (it is priced as an Attack). It is the card that makes a deck
that never cooks still generate Sparks every turn, which is [USER]'s "make
non-bomb decks more consistent" in one Common. In co-op nothing changes: it
sets off only when she plays it.

**Blasting Spree** (Common Skill, 1 Energy). Her hobby in the story is
blasting fish out of Starfell Lake and getting confiscated for it; Fish
Blasting already carries the Confiscated. This is the Spray half of the
status bridge [USER] asked for ("planting lots of bombs in exchange for
statuses"). Name is a candidate for the naming audit; "Bombs for
Everyone!" is the other.

> Place a Bomb 4 on ALL enemies. Add a Dazed into your Discard Pile.

Upgrade: Bomb 6. Priced against Thunderclap (Ironclad Common, 1: 4 to ALL
and Vulnerable) and Dagger Spray (Silent Common, 1: 4 to ALL twice): the
same 4 to ALL, delayed, growing, and worth a Spark per enemy when cashed,
with the package's light tax (a Dazed) for the volume. The numbers above
are final; it does not take the +2 again. It gives Spray three Bombs for
one card at Common (today only Mk.III, an Uncommon, does that), gives
Tinder Toss three targets, and adds a fourth Common loader for Finders
Keepers and Damage Report to read.

Both are three ops the build has (`plant_bomb`, `set_off`, `add_card`;
`plant_bomb` with `target: all_enemies` is already Windblume Fireworks'
second half).

### 4.6 Core rules (the turn-one paper's default, restated)

- **Rule 1:** every Bomb grows by **2** at the start of her turn (today 4).
  Alice's Recipe: "Your Bombs grow twice each turn" still doubles it, to 4.
  The brief's sec.3 is edited in place.
- **Rule 4:** she starts every combat with **3** Sparks (today 1). Pounding
  Surprise's text does not move. Dodoco Tales adds 4, so 7 with it.

Lore for both: Pounding Surprise in the source game is a passive that
hands her Explosive Sparks from her ordinary attacks, so she is never
without one; and her bombs in the story go off when she wants them to,
which is usually at once. The slow-cooked Bomb is Alice's recipe, not
Klee's: the Rare says so.

**Risks, named.** Blast Shield at 3 opening Sparks is 12 Block for 0 Energy
on turn one when drawn; [USER] kept the card, so the round reads Blast
Shield plays a fight before anything is done. Boom Badge plus Ka-pow! on
turn one doubles a Bomb 8 for 20; that is a fast turn, which is the point.
Cook's boss numbers shrink (The Big One on a pile that grew 2 a turn); the
round reads boss fights apart. Mines on bosses improve for free.

### 4.7 Considered for the starter and not recommended

Each is [USER]'s to pick; this paper's default is none of them.

- **Jumpy Dumpty loses Innate.** Tried 2026-10-02, lost the act-1 boss
  twice, restored 2026-10-03. Not again.
- **Ka-pow! loses Retain (base face).** Retain is what keeps a detonator in
  hand in a pool with 13; without it the Silent seed's "drew it on 2 of 8
  turns" gets worse. Growth 2 removes the reason to hold; Retain can stay.
- **Ka-pow! gains a Spark or a Bomb.** Redundant with 3 opening Sparks and
  with Fire! Fire!, and it puts a good card in the starter, which [USER]
  declined on 2026-09-05 ("I still would rather avoid putting too many
  actually good cards in the starting deck").
- **Jumpy Dumpty 8 to 10** (the turn-one paper's option (c)). Harmless and
  consistent with the +2 on every other placer; it makes the starter's
  turn-one cash 14 instead of 12. Offered as pick 4 (b) because it is the
  one starter edit the rule change argues for, not because the data needs
  it.

---

## 5. What the round should read

Suite 5 on the five base seeds, Sonnet seats per act as suites 2 to 4,
built on `klee-next`, graded against the base five's runs:

1. **Turn one, acts 2 and 3, normal fights:** damage dealt (today 11 and
   5; the base five 30 and 62); fights with a Set off card played on turn
   one (today 25 of 85, 29%); fights with a Set off by the end of turn two
   (today 50 of 85); the first Set off's median turn (today 2 to 3). The
   bar: turn one at or above half the base five's, and a Set off on turn
   one in at least half the fights.
2. **Fight length and HP:** act-3 normal fights at or under 4 turns mean
   (today 4.7; base 3.3 to 3.6); HP lost ratio in act 3 toward 1.0 (today
   1.57); Block gained a turn at or below the base five's (today 9.8 to
   7.5 in act 3).
3. **Boss fights, separately:** the act-3 boss reached on at least three
   seeds and HP lost there read against the base five's 35%; whether Cook
   decks still produce a 100-plus turn under growth 2 (any record naming
   one).
4. **Uptake:** Fire! Fire! and Blasting Spree fights played and runs holding
   them; Explosive Spark, Boom Badge, Boom-Boom Strike plays on turn one
   (the 3-Spark effect); Blast Shield plays a fight (the risk); Mines on
   bosses named as waste or not.
5. **Cook as opt-in:** how many runs draft Alice's Recipe, Chain Fuse or
   Witch's Homework, and whether those runs' boss turns differ from the
   others'.
6. **Then [USER] plays**, because a rule changed (CLAUDE.md norm), and
   notes his own turn-one plays in acts 2 and 3: the one number the seats
   cannot give.

---

## Picks

**Ruled 2026-10-08.** [USER]: "Nope, this all looks good. I'm now in
agreement with all picks." All five at the defaults.

1. **The read.** The starter is not the root. Rule 1 and rule 4 make
   waiting free and the Spark cards dead; the Common layer offers placers
   and Block on turn one where the base five's offers damage; her only
   scaling is time. **Default: agree.**

2. **The rules** (the turn-one paper's pick 1, restated).
   - **Default (a):** growth 4 to 2 (Alice's Recipe to 4), 3 opening
     Sparks, every drafted placer +2, Jumpy Dumpty unchanged.
   - (b) [USER]'s proposal as stated: growth 2 and 3 Sparks, no +2.
   - (c) Growth 3 and 2 opening Sparks (the sim's variant F, 4.6%): half
     the step, if (a) reads as too far on his own run.

3. **The pool.**
   - **Default (a):** Fire! Fire! and Blasting Spree in (sec.4.5); Playdate
     and Pop! out (Pop! kept off-pool for Klee Can Explain!); pool 78,
     25 / 32 / 21.
   - (b) Fire! Fire! in, Playdate out; no Blasting Spree yet (one new card
     a round).
   - (d) Bombs Away! out instead of Pop!, if [USER] reads Block cards as
     the thing to thin; the first draft's choice, withdrawn in sec.4.4.
   - (c) The rules alone this round; read the pool again after suite 5.

4. **The starter.**
   - **Default (a):** no change. Innate on Jumpy Dumpty and Retain on
     Ka-pow! both stay.
   - (b) Jumpy Dumpty's Bomb 8 to 10 (11 to 13 upgraded), so the starter
     takes the same +2 as every other placer. A starter change.
   - (c) Ka-pow!'s Retain moves to the upgrade only, as the brief's sec.8
     had it. Not recommended (sec.4.7).

5. **The round.** **Default:** suite 5 on the same five seeds, read on
   sec.5, boss fights apart; then [USER]'s run on the build that passes,
   with his turn-one plays noted. Alternative: his run first, on the
   `klee-next` build, before any seats.
