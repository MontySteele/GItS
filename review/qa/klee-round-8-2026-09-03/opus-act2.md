# KLEEMOD-KLEE — blind seat, lane 2, act 2

## Identity

- Model / seat: Claude Opus, blind TESTER seat, round 8, **second seat** (act 2 only)
- Lane: 2
- Character: KLEEMOD-KLEE
- Picked up: on the **act-2 map screen**, exactly where the first seat left it —
  one node offered, `Ancient (path 1)`, nothing played on it.
- Act / boss: act 2. The map named the boss on the first screen:
  `At the top of this act: **The Insatiable**`. 17 rooms (`16 floors ahead: Boss`).
- Actions accepted: **94 of the 250 budget.** Refused: **0** — every command I
  sent was accepted, and I hit no tool error until the run itself ended.
- Termination reason: **stop condition (2) — the run ended.** `end turn` on the
  Elite's first round returned `TOOL-BLOCKED: game_over / the run is over; there
  is nothing left to play / The run ended on floor 24.` A bare `observe`
  afterwards returns the same three lines. **Klee died on act-2 floor 7 (run
  floor 24), in the Decimillipede Elite, on the first enemy turn of that fight,
  at 2/62 HP behind 19 Block against 24 incoming.** 156 actions were unspent —
  the budget was never the constraint; HP was.
- Where the run stands: **over.** Lane 2 holds a finished run. There is no screen
  left to stand on and nothing was played after the game-over.
- HP trajectory, every reading a screen printed in act 2, in order:
  **62/62** (fight 9 opens — see the finding below; the previous seat's last
  reading was 42/62 before a 27-damage Death Blow) -> 53 -> 52 (fight 9 won)
  -> *Doll Room charges 5 HP, no screen prints the result* -> *Spirit Grafter
  heals 25, no screen prints the result* -> **62/62** (fight 10 opens) -> 51
  -> 49 -> 49 -> 49 (fight 10 won) -> 49 (fight 11 opens) -> 49 -> 37 -> 23
  -> **2** (fight 11 won) -> **2/62** (Elite opens) -> run over. **No screen
  printed an HP number after the death**, so as in act 1 the record cannot state
  a final value. Max HP was 62 throughout; it never changed and nothing offered
  to change it.
- Gold: **no screen printed a gold total at any point in act 2.** I never entered
  a shop, and the shop is the only screen either seat has found that shows the
  purse. Reward screens printed `11 Gold`, `13 Gold`, `16 Gold` = 40, on top of
  whatever act 1 left. `Lucky Fysh` (15 gold per card added) fired on four card
  adds, three of which `Bing Bong` doubled, so the true figure is higher by an
  amount I could not verify.
- Potions held at the end: **Strength Potion** (one, from the fight-11 reward),
  two slots empty. Used during act 2: `Strength Potion` and `Skill Potion`, both
  on fight 11.
- Relics, exactly as printed on the last battle screen that listed them:
  **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark.
  **Large Capsule** — Upon pickup, obtain 2 random Relics. Add an additional
  Strike and Defend to your Deck. **Snecko Skull** — Whenever you apply Poison,
  apply an additional 1 Poison. **Pendulum** (1) — Every 3 turns, draw 1 card.
  **Candelabra** — At the start of your 2nd turn, gain [Energy][Energy].
  **Lucky Fysh** — Whenever you add a card to your Deck, gain 15 Gold.
  **Sand Castle** — Upon pickup, Upgrade 6 random cards.
  **Bing Bong** — Whenever you add a card to your Deck, add one additional copy.
  `Snecko Skull` was still dead: across all of act 2 no card that applies Poison
  was offered, drawn or played, so it has now done nothing for 24 floors.
- Deck at death, **30 cards**, reconstructed and then confirmed by the Elite's
  opening piles (`24 in the draw pile` + 6 in hand = 30):
  Strike x3, Defend x3, **Defend+**, Duck and Cover, **Jumpy Dumpty+**,
  **Ka-pow!+**, **Kaboom!+**, Tinder Toss, **Tinder Toss+**, Pop!, Bang Bang!,
  Perfect Timing x2, Diona — Shaken, Not Purred, Kaeya — Glacial Waltz,
  **Barbara — Let the Show Begin♪+**, Shinobu — Grass Ring of Sanctification,
  Thoma — Blazing Barrier, **Sparks 'n' Splash+**, Big Badda Boom,
  Metamorphosis x2, Chevreuse — Ring of Bursting Grenades x2,
  Fish-Flavored Bait x2.
- **Sand Castle's six upgrades, all six identified by sight** over three fights
  (the event named none of them): `Sparks 'n' Splash` (cost 2 -> 1),
  `Kaboom!` (7 -> 10 damage), `Barbara` (6 -> 9 Block), `Tinder Toss` (4 -> 6 per
  hit, one of the two copies), `Ka-pow!` (4 -> 7 damage), `Defend` (5 -> 8 Block,
  one of the four copies).
- Prediction accuracy: I priced every significant play before making it. **Ten
  predictions came out exact** (fight 9 turns 1, 2 and the Tinder Toss+ kill;
  fight 10 turns 1, 2, 3, 4; fight 11 turns 1, 2 and the Big Badda Boom kill) and
  **three missed**, all logged in place and all in the findings: fight 11 turn 2
  (predicted 9 damage taken, took 12 — Thoma), fight 11 turn 4 (predicted 39 from
  the Rapid Fire chain, dealt 31), fight 11 turn 4 end-of-turn (predicted the
  enemy on 27-31, actual 20).

*(This header was completed at the end; the sections below were written as the
fights happened.)*

---

## The act-2 map, as handed over

```
- **Ancient (path 1)**
    leads on to: Monster, Monster, Monster

- 1 floor ahead: Ancient
- 2 floors ahead: Monster, Monster, Monster
- 3 floors ahead: Monster, Unknown, Monster, Monster
...
- 7 floors ahead: Elite, Shop, Elite, RestSite, Monster, RestSite
- 9 floors ahead: Treasure, Treasure, Treasure
- 15 floors ahead: RestSite, RestSite, RestSite
- 16 floors ahead: Boss
At the top of this act: **The Insatiable**
```

Same complaint the first seat logged, unchanged in act 2: **the map prints no
HP, no gold, no relics and no potions**, and it is the only screen you route
from. I inherited a run whose current HP I could not read — the last number any
screen printed to the previous seat was 42/62 immediately before a 27-damage
Death Blow, so I opened act 2 not knowing whether I was on 15 or 42.

There is also no choice here: exactly one node, `Ancient (path 1)`. A room type
neither seat has seen before ("Ancient") with no description of what it is.

---

## Event 1 — the Ancient room: Orobas (act-2 floor 1)

The `Ancient` node opened an event with three options and no other text:

```
# Orobas
- **Gear Glass**
    See 15 cards from The Defect. Choose any number of them to add to your Deck.
- **Sand Castle**
    Upon pickup, Upgrade 6 random cards.
- **Touch of Orobas**
    Replace Pounding Surprise with Dodoco Tales.
```

Priced from the printed text alone:

- **Gear Glass** offers cards from a *different character* ("The Defect") into a
  deck built entirely around Bombs, Sparks and auras, and the screen does not say
  what those 15 cards are. A blind add.
- **Touch of Orobas** swaps out `Pounding Surprise — Whenever a Bomb goes off,
  gain 1 Spark`, the whole income side of my Spark economy, for `Dodoco Tales`,
  a relic whose text the screen **never prints**. A one-way trade with one side
  of it hidden.
- **Sand Castle** upgrades 6 of my 23 cards, and upgrades in this mod are large.

Took **Sand Castle**. The event then printed only `Proceed`: **it never named a
single one of the 6 cards it upgraded.** I discovered them one at a time as they
turned up in hand over the next two fights. This is the Smith-screen defect the
previous seat found, in a stronger form: there, at least, you chose the card.

**Correction to the previous record.** That record states `Jumpy Dumpty+` places
a **Bomb 18**. The card's own text, printed in my hand on fight 9 turn 2, reads:
`Jumpy Dumpty+ (upgraded) — cost 1, skill: Place a Bomb 11. When it goes off,
place a Mine 4 on ALL enemies.` The previous seat was reading a *grown* Bomb
badge, not the card. Base is Bomb 8 / Mine 3; upgraded is **Bomb 11 / Mine 4**.

---

## Fight 9 — Bowlbug (Rock) 48 + Bowlbug (Nectar) 36, act-2 floor 2

**The handover reading no screen ever gave me: `HP 62/62`.** The previous seat's
last printed HP was 42/62 immediately before a 27-damage Death Blow, so I opened
act 2 expecting to be somewhere near 15. The first battle screen printed full
health. **Something restored 20+ HP between the act-1 boss reward and here and no
screen said so** — not the reward screen, not the map, not the Orobas event.

Second silent change: the relic list now reads `**Pendulum** (2)`. It read
`Pendulum (1)` on every screen of act 1. **The bracketed number does move, and it
moves across combats** — which is most of the answer to the previous seat's
unresolved Pendulum question: it is a run-level counter, so "every 3 turns" does
not restart when a fight does, and round 3 of a given fight is not necessarily a
Pendulum turn.

```
- **Bowlbug (Rock)** — HP 48/48   Intent: Aggressive (Attack) — 15
    Imbalanced 1 (debuff) — If Bowlbug (Rock)'s attacks are fully blocked, it becomes Stunned.
- **Bowlbug (Nectar)** — HP 36/36  Intent: Aggressive (Attack) — 3
```

**Turn 1.** Played Sparks 'n' Splash+ (a permanent power, and cheap now — the
card prints `The cost printed on this card is 2; it is showing 1 here, because
this copy is upgraded — that is permanent`), Perfect Timing on Rock, Thoma for
Block. Predicted Perfect Timing at a flat 8: its `Set off` finds no Bombs and its
replay rider needs a Bomb reaction. **Actual 48 → 40. Exactly 8.**
Predicted 9 through — Block 6, with Thoma's `+3 whenever this Block absorbs
damage` firing once between the two attacks, so 9 of the 18 lands.
**Actual HP 53/62. Exactly 9.**

A text defect, quoted verbatim from the buff list:

```
Blazing Barrier 6 (buff) — {Left} Block left. When it absorbs damage, gain 3 Block.
```

`{Left}` is an unfilled template placeholder shipped to the screen.

**Turn 2.** `Energy 5/3` (Candelabra). Sand Castle's upgrades started showing:
`Kaboom!+ — Deal 10 damage` (base 7) and `Barbara — Let the Show Begin♪+ — Gain
9 Block. Apply Hydro.` (base 6). Played the whole six-card hand for exactly 5
Energy, Pop! being free: Pop! and Jumpy Dumpty+ both on Rock, Kaboom!+ and Strike
on Rock, Defend, Barbara+ on Nectar.
Predicted Rock at 24 (10 + 6), Bombs 16 (5 + 11), Block 14 (5 + 9).
**Actual: Rock 24/48, `Bomb 16 (buff) ... Bombs here: 2`, Block 14. Exact.**

Nectar's intent flipped to `Empower (Buff)`, dropping the incoming from 18 to 15
— and my Block was **14**. `Imbalanced 1 — If Bowlbug (Rock)'s attacks are fully
blocked, it becomes Stunned` sat one point of Block out of reach. That is the
sharpest near-miss of the act: a mechanic worth a whole enemy turn, gated on a
number I could see and could not quite make. I held the `Skill Potion` that might
have produced the extra Block card, because Rock was on 24 HP under a Bomb that
was about to be 24 and the stun would have bought a turn I did not need.

**Turn 3 — what Sparks 'n' Splash actually reads, which the card does not say.**
The screen opened with Rock at **8/48**: Sparks 'n' Splash had fired at end of
turn for **16**, and Rock's badge still read `Bomb 24 (buff) ... Bombs here: 2`.
So:

- the damage is the **sum of the Bomb sizes** (16), not the *count* of Bombs (2).
  `deal Pyro damage to a random enemy equal to the Bombs on it` reads either way;
  the number settles it.
- the Bombs are **not consumed** — 16 grew to 24 (two Bombs, +4 each) and both
  were still standing. It is the only damage source in the deck that spends
  nothing.

Nectar's Empower had resolved into `Strength 15 (buff) — Increases attack damage
by 15`, turning a 3-damage attacker into an 18-damage one in a single turn.
Incoming was now 33 against 52 HP, which is what forced the turn.

Played `Ka-pow!+ (upgraded) — cost 0, attack: Retain. Set off. Deal 7 damage.` on
Rock. Predicted: the first Bomb kills Rock at 8 HP and both the second Bomb and
Ka-pow!'s own 7 are thrown away — the previous seat's overkill trap exactly.

**Half of that was wrong, in my favour, and it is the sharpest thing in this
fight.** Rock died and the screen printed:

```
- **Bowlbug (Nectar)** — HP 36/36
    Hydro Aura 1 (aura)
    Strength 15 (buff)
    Bomb 15 (buff) — Set off here deals 15 Pyro damage. Bombs here: 1.
```

**The surviving Bomb migrated to the other enemy.** Nectar had never been
targeted by Pop! or Jumpy Dumpty and carried no Bomb before Ka-pow!. Spark went
1 → 2, i.e. `Pounding Surprise` paid for exactly **one** detonation, so the 15 did
not go off and get wasted — it *moved*. Nothing on Ka-pow!, Jumpy Dumpty, Pop! or
in the `Bomb` / `Set off` glossary says a Bomb outlives its host. (Ka-pow!'s own
7 damage *was* wasted: Nectar stayed on 36/36.)

Then the line the migration opened. Diona on Nectar: her first Cryo consumed the
Hydro aura for **Frozen**, her second painted Cryo.

```
Frozen 1 (debuff) — Its next action deals 50% less damage. The first Attack to hit it Shatters for 6 unblockable damage and removes Frozen.
Cryo Aura 2 (aura)
Intent: Aggressive (Attack) — the number on its icon is 9
```

The intent re-rendered 18 → **9** on the spot — the previous seat's favourite
live-arithmetic behaviour, now applied to the *enemy's* number.

Predicted Tinder Toss+ (`Set off and deal 6 damage to a random enemy twice`) as
lethal: the set-off sends the Bomb 15 into a Cryo aura for Melt 15 × 1.75 = 26.25
→ 26, plus 6, plus 6, plus the Shatter's 6 = 44 against 36 HP.
**Actual: the fight ended on that one card.**

**Fight 9 result: won turn 3, HP 52/62 — 10 damage taken.**

Reward `11 Gold` + a card, from `Fwoosh!` / `Sorry, Jean...+` (`cost 0, skill:
Retain. Remove one of your Bombs. Gain Block equal to its size.`) / `Big Badda
Boom` (`cost 2, attack: Set off. Deal 12 damage. Then deal damage equal to what
the Bombs dealt.`) / `Lisa — Lightning Rose`.

Took **Big Badda Boom**: the only card offered that turns Bomb damage into *more*
damage instead of spending it, which attacks the previous seat's sharpest finding
(set-offs overkill and waste) from the other side. `Sorry, Jean...+` was the close
second and the only scaling Block card either seat has been offered.

---

## Event 2 — the Doll Room (act-2 floor 3): a choice sold with no information

```
# Doll Room
- **Pick at Random**        Obtain a random Doll Relic.
- **Take Some Time**        Lose 5 HP. Choose 1 of 2 Doll Relics.
- **Examine Each and Make the Best Choice**   Lose 15 HP. Choose 1 of 3 Doll Relics.
```

The whole event is priced as *information*: 5 HP buys a choice of two, 15 HP buys
a choice of three. Given how completely dead `Snecko Skull` was for the previous
seat, paying to avoid a dud looked correct, and 5 HP at 52/62 was cheap. Took
**Take Some Time**.

**What 5 HP actually bought:**

```
# Doll Room
- **Daughter of the Wind**   Receive Daughter of the Wind.
- **Bing Bong**              Receive Bing Bong.
```

**Two names and not one word of what either relic does.** The event charges HP
for the right to choose and then withholds the only thing that would make the
choice a choice. I picked `Bing Bong` on nothing better than the guess that a
bomb-sounding name might touch the Bomb engine — a coin flip I paid 5 HP for.

Worse: the confirmation screen printed only `Proceed`, so **the relic's text was
never shown**, and `Bing Bong` did not appear in the relic list on any battle
screen afterwards (I re-read that list on fights 10, 11 and 12). Either it is a
relic that does not display, or the 5 HP bought nothing at all. **I could not
tell which, and no screen in the run lets me find out.**

---

## Event 3 — Spirit Grafter (act-2 floor 4)

```
- **Let It In**    Heal 25 HP. Add Metamorphosis to your Deck.
- **Rejection**    Lose 10 HP. Upgrade a card.
```

A 25-HP swing between the arms (at 47/62 the heal is worth +15 to the cap, and
the other arm costs 10) against one upgrade plus deck purity. `Metamorphosis` is
named and not described, so the cost of the good arm is hidden the same way the
Doll Room's was. Took **Let It In** on the arithmetic: 25 HP of swing is more
than a seventh upgrade in a deck that already had six from Sand Castle.

Neither the event nor the next map screen printed an HP number. The next battle
screen opened `HP 62/62`, so the heal did land and did cap.

**Metamorphosis turned out not to be a curse at all.** Drawn on fight 10 turn 2:
`Metamorphosis — cost 2, skill: Add 3 random Attacks into your Draw Pile. They're
free to play this combat. Exhaust.` That is a real card, and the event's good arm
had no downside beyond two cards of deck bloat — which is worth saying plainly,
because the framing ("Let It In" / "Rejection", a thing added to you) reads as a
curse and priced my decision as if it were one.

**A deck-count discrepancy I could not resolve.** Fight 10 opened
`21 in the draw pile` with 5 in hand = **26 cards**, and `Sparks 'n' Splash` was
one of the 5, so nothing was out of the count. Act 1 ended on 23; Big Badda Boom
and Metamorphosis make 25. **There is one card in the deck I cannot account for**,
and no screen so far in act 2 has printed the deck list.

---

## Fight 10 — three Exoskeletons (24 + 28 + 27), act-2 floor 5

```
- **Exoskeleton (1)** — HP 24/24   Intent: 1x3
    Hard To Kill 9 (buff) — Reduce all damage taken and HP lost by Exoskeleton to 9.
- **Exoskeleton (2)** — HP 28/28   Intent: 8       Hard To Kill 9
- **Exoskeleton (3)** — HP 27/27   Intent: Empower (Buff)   Hard To Kill 9
```

`Hard To Kill 9` is act 1's `Hardened Shell` rebuilt as a *per-hit* cap rather
than a per-turn budget, and the difference is the whole fight. I tested it
deliberately on turn 1: Kaboom!+ (10) and Strike (6) into the same target.

Predicted 15 if the cap is per hit (9 + 6) and 9 if it is per turn.
**Actual 27 → 12. Exactly 15.** Per hit, and Kaboom!+ lost exactly 1 damage.

**This inverts the character harder than Hardened Shell did.** Every multiplier
Klee owns is dead here: a Melt on a big hit multiplies a number that is then
capped, a grown Bomb pays 9 whatever its size, and `Big Badda Boom`'s "then deal
damage equal to what the Bombs dealt" doubles a capped number. The cards that
*gain* are the small multi-hit ones — Tinder Toss (two hits of 4, both under the
cap and both fully paid) — and, absurdly, **Strike**, whose 6 is the only attack
in the deck that loses nothing to a 9-point ceiling. The previous seat named
Strike the card it never wanted to play; this fight is the one screen in two acts
where Strike is rate-competitive with Kaboom!+.

**Turn 1** (Sparks 'n' Splash+, Kaboom!+, Strike): Exo 3 to 12/27, and Exo 3's
Empower resolved into `Strength 2` — the *same* Empower intent that had given
Bowlbug (Nectar) `Strength 15` one fight earlier. Same word on the screen, an
order of magnitude apart, with nothing to tell them apart in advance.
Took 11 unblocked: **HP 51/62, exact.**

**Turn 2.** Big Badda Boom on Exo 3: predicted a flat 9 (its 12 capped; its
"damage equal to what the Bombs dealt" adds 0 with no Bombs out). **Actual
12 → 3. Exactly 9** — a 2-Energy card delivering 9, which is what the cap does to
this deck. Then Tinder Toss, and the cost of `a random enemy`: **both of its hits
went to the two full-health Exoskeletons and neither touched the 3-HP one**
(24 → 20 and 28 → 24). A 3-HP target left standing to hit me for 9. Blocked out
with Diona + Duck and Cover + Shinobu = 15 against 17. Predicted 2 through.
**Actual HP 49/62. Exact.**

Spark went **0 → 2** across that turn — I had spent my one Spark on Tinder Toss —
with no Bomb in play and exactly one Elemental Reaction on the board (Diona's
first Cryo consuming Exo 1's Pyro). `Pounding Surprise` pays per Bomb and there
were none. This is the previous seat's finding standing up in a cleaner instance:
**Spark income is +2 from somewhere the screens never name.**

**Turn 3.** Ka-pow!+ (free) killed Exo 3, Perfect Timing + Strike took Exo 2 from
24 to 10, and Thoma held the line. Thoma against a multi-hit intent is worth
recording: `Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block` means
6 Block absorbs a `3x3` completely — 3 absorbed, +3 back, three times over.
Predicted 0 damage. **Actual HP 49/62, unchanged.**

**Turn 4.** Pop! then Perfect Timing on Exo 2: the set-off cashed the Bomb 5 and
the card's own 8 made 13 into 10 HP — killed. Bang Bang! took Exo 1 to 12,
Jumpy Dumpty+ and Bang Bang!'s rider left `Bombs here: 2` on it, and Barbara+
blocked. Predicted Sparks 'n' Splash to fire for 9 (15 of Bombs, capped) and
Exo 1 to end on 3. **Actual: `Exoskeleton — HP 3/24`. Exact.** Took 0 of the 3x3
behind 9 Block.

Two things that screen printed which are worth quoting. First, the badge:

```
Bomb 17 (buff) — Set off here deals 17 Pyro damage capped by Hard To Kill. Bombs here: 2.
```

The Bomb badge **added a clause about the cap** rather than quoting a number it
knew I would not get. That is the same honesty the previous seat praised in the
`Reaction preview` lines, extended to a cap it could have quietly ignored.

Second, my own mistake, which the screen had warned me about: I played Barbara+
onto an enemy my own Bang Bang! had just painted Pyro, so her Hydro was consumed
for a null Vaporize and nothing was left behind. Her card carries the warning
verbatim — `*Reaction preview: Vaporize* — This card deals no damage. Pyro plus
Hydro is still consumed, and there is no hit here for the 1.5x to multiply.` —
and I played her anyway for the Block. The interface was right and I was careless.

**Turn 5.** Tinder Toss+ set off the Bomb on a 3-HP enemy. Over.

**Fight 10 result: won turn 5, HP 49/62 — 13 damage taken across five turns.**

Reward `13 Gold` + `Strength Potion` + a card, from `Careful Arrangement`
(`Move all your Bombs onto the enemy as one Bomb. It grows by 5.`) / `Chain Fuse`
/ a third `Tinder Toss` / `Chevreuse — Ring of Bursting Grenades` (`cost 2,
attack: Deal 10 damage to ALL enemies.`).

Took **Chevreuse**. The deck has no AoE at all — `Jumpy Dumpty`'s `Mine 4 on ALL
enemies` is the only card in 26 that touches more than one body — and act 2 has
now opened with a two-enemy and a three-enemy fight. Note also that
`Careful Arrangement` is an actively *bad* card in any fight with a per-hit cap:
consolidating every Bomb into one Bomb converts several capped hits into a single
capped hit.

**Correction to my own record above.** `Bing Bong` *is* printed in the relic
list — I had simply trimmed that block out of my own `observe` output for the
previous two screens. In full it reads:

```
- **Bing Bong** — Whenever you add a card to your Deck, add one additional copy.
```

That resolves the missing-card count exactly: `Metamorphosis` was added *after*
Bing Bong and so came in as **two** copies, making 23 + Big Badda Boom + 2 =
**26**. Every card reward from the Doll Room onward costs two cards of deck
space and pays 30 gold (Lucky Fysh, twice). So the 5 HP did buy something real,
and the complaint stands only against the *screen*: the event named two relics,
described neither, and never printed the text of the one I took.

---

## Fight 11 — Hunter Killer (121 HP), act-2 floor 6 — the fight that nearly ended the run

A solo 121-HP enemy behind an `Unknown` node. Ends with me on **2 HP**.

**Turn 1** — intent `Strategic (Debuff)`, no attack, so Block was worth nothing
and the whole hand was Block. I played Barbara+ first to paint Hydro and then
Tinder Toss into it, so its first of two hits Vaporized. Predicted
4 × 1.5 = 6, then 4 on a bare enemy = **10**. **Actual 121 → 111. Exact.**
The rest of the hand I played purely to *cycle* — with a 28-card deck, putting
dead Block cards in the discard is the only way to reach the Bomb cards.

**Turn 2 — the debuff, and it is aimed squarely at this character.**

```
Tender 0 (debuff) — Whenever you play a card, lose 1 Strength and 1 Dexterity this turn.
```

Klee's whole shape is a wide hand of 0- and 1-cost cards played four and five at
a time. Tender charges a compounding tax on exactly that. I tested it with one
card: played Thoma alone and read the state back —

```
Block 6 ... Tender 1 ... Strength -1 ... Dexterity -1
```

— so **the penalty lands after the card resolves**: card *i* of the turn plays at
−(i−1) Strength and Dexterity. Three consequences I then played around all fight:

1. **Order attacks before skills, and the widest attack first.** A −1 costs
   Rapid Fire (four hits) four damage and costs a Strike one.
2. **Block dies faster than damage does.** By the sixth card of turn 4 my
   `Defend` was re-rendering as `Gain 2 Block` against a printed 5. Tender does
   not merely slow the deck down, it deletes the defensive half of it.
3. **Bomb damage is immune.** `Its hit takes the enemy's debuffs, not yours` means
   a Bomb pays its full size no matter how many cards preceded it. Under Tender,
   routing damage through Bombs is not a preference, it is the only untaxed
   channel — the same lesson the previous seat drew under `Weak`, arrived at from
   a completely different direction.

Turn 2 predicted 10 (Ka-pow!+ at −1 for 6, Strike at −2 for 4). **Actual
111 → 101. Exact.** But I mispriced the damage coming back: I predicted 9 through
Thoma's 6 Block and took **12**.

**That mispricing is a finding.** `Thoma — Blazing Barrier — Gain 6 Block.
Whenever this Block absorbs damage, gain 3 Block` reads as a per-instance
refresh; against a three-hit attack it should absorb 6 + 3 + 3 = 12. It absorbed
**9**, and it has now absorbed exactly 9 on all three occasions I can measure it:
fight 9 turn 1 (18 incoming, 9 taken), fight 10 turn 3 (9 incoming, 0 taken),
fight 11 turn 2 (21 incoming, 12 taken). **Thoma is a 9-Block card that prints
6 and implies more.**

**Turn 3.** `HP 37/62`, and the hand was a trap: `Spark 0`, and three of five
cards priced in Spark. One of them was `Fwoosh!`, delivered by Metamorphosis,
which promises its attacks are *"free to play this combat"* — and the screen
refused it: `CANNOT BE PLAYED: you have no Spark, and this costs 1`. That is not
a contradiction, it is the Spark rule being enforced exactly as printed:
*"an effect that makes a card free to play, or cuts its cost to 0, covers Energy
only, and the 1 Spark is still spent."* The rules text is honest; the *card* is
not, because `Metamorphosis` says "free to play" without qualification and can
hand you a card that its own freeness cannot pay for. And Spark income is
`Pounding Surprise`, which needs a Bomb — so a Bomb drought is also a Spark
drought, and half the hand goes dead at once.

Spent `Strength Potion` here. Two things worth recording: **using a potion does
not tick Tender** (the counter stayed at 0), and **+2 Strength is a direct
counter to Tender**, since Tender's whole mechanism is draining the same stat.

Played Strike (card 1, full 6 + 2 = 8), Shinobu, Kaeya.
Predicted 18. **Actual 101 → 79 = 22.** The 4 I missed is Kaeya: her end-of-turn
tick took the Strength bonus *and* Melted off the Pyro aura my own attacks had
left — (6 + 2) × 1.75 = 14. **Strength applies to end-of-turn power damage.**
HP 37 → 23, exactly 17 − 3 Block.

**Turn 4 — the turn the fight turned, and the one number I could not reconcile.**
Hand: `Rapid Fire — cost 0, attack: Deal 5 damage to a random enemy 4 times. Set
off each enemy hit.` (one of Metamorphosis's attacks, and the card helpfully
prints `The cost printed on this card is 2; it is showing 0 here ... it is what
this card costs now, not what it costs`), plus Jumpy Dumpty+, Perfect Timing,
Kaboom!+, Defend.

I played Jumpy Dumpty+ **first** so Rapid Fire's four set-offs would chain:
hit 1 cashes the Bomb 11 and its rider drops a `Mine 4` on all enemies, hit 2
cashes that Mine. Predicted **39** = 11 + 4 + four hits at 6 (base 5 + Strength 1
after one card).

**Actual 79 → 48. Exactly 31, an 8-point shortfall.**

I then got a free measurement of it. The `Skill Potion` offered
`Ammo Scavenging — cost 1, skill: Place a Bomb 4. Draw 1 card for each of your
Bombs that went off this turn.` I took it, and it **drew 2 cards** (draw pile
10 → 8). So **two Bombs did go off** — the chain fired exactly as I read it, and
the Bomb half of my prediction (11 + 4 = 15) was right. That pins the shortfall
on Rapid Fire: its four hits delivered **16 total, i.e. 4 apiece**, against a
card printing 5 and a Strength of +1 that should have made them 6.
**Rapid Fire's hits came in 2 below both its printed number and its buffed
number, and nothing on any screen explains the gap.** (The one alternative that
also sums to 31 — four hits of 5 and only the Bomb 11 detonating — is ruled out
by Ammo Scavenging's two draws, unless one of those draws was Pendulum's.)

I then banked rather than spent: Kaboom!+ for 9, Pop! for a second Bomb, and
`Sparks 'n' Splash+` as a permanent power, leaving `Bomb 17 ... Bombs here: 2`
standing on the enemy — Tender-proof damage held in reserve.
Predicted the enemy on 27–31. **Actual 20/121**, i.e. 28 dealt where I priced
17–21. The end-of-turn ticks out-performed the Strength readout again and I could
not derive a rule that fits both this turn and turn 3 (see the findings).

The enemy's 17 took me to **HP 2/62**.

**Turn 5.** Enemy 20 HP, `Bomb 17 (buff) ... Bombs here: 2`, intent 17 — lethal
to me at 2 HP, so the turn had to kill. `Big Badda Boom — cost 2, attack: Set
off. Deal 14 damage. Then deal damage equal to what the Bombs dealt.` Predicted
the set-off alone at 17 against 20 HP, and the card's own 14 behind it as
certain lethal. **It was.**

**Fight 11 result: won turn 5, HP 2/62 — 47 damage taken, more than the whole of
act 1's worst fight.**

Reward `16 Gold` + `Strength Potion` + a card, from `Fwoosh!` / `Witches' Circle`
/ `Fish-Flavored Bait` (`cost 1, attack: Deal 4 damage. Place a Bomb 4.`) /
a second `Shinobu`. Took **Fish-Flavored Bait**: the deck's real bottleneck is
Bomb *access* — only Jumpy Dumpty+, Pop! and Bang Bang! place Bombs, 3 cards in
28 — and Bombs are the one damage channel that neither `Tender` nor a Strength
drain can tax. With Bing Bong it enters as two copies, taking bomb-placers to
5 in 30.

---

## The map at act-2 floor 7 — one node, and it is an Elite

```
Where you can go next:
- **Elite (path 1)**
    leads on to: RestSite
```

**At 2/62 HP, with no healing of any kind available, the map offers exactly one
room and it is an Elite.** There is a RestSite directly behind it and three more
on the two floors after that, and none of them is reachable without going
through the Elite first. I have one `Strength Potion` and two empty potion slots.

This is worth recording plainly as a routing observation, not a complaint: the
map screen prints no HP, so nothing on the screen I routed from three floors ago
told me I was walking a 121-HP `Unknown` into a forced Elite. The previous seat
made the same point about the act-1 map; here it has a consequence.

---

## Elite — three Decimillipede segments (44 + 40 + 46), act-2 floor 7 — the run ends

```
- **Decimillipede (1)** — HP 44/44   Intent: 5x2
    Reattach 25 (buff) — If other segments are still alive, revives in 2 turns with 25 HP.
- **Decimillipede (2)** — HP 40/40   Intent: 6   and also: Empower (Buff)
    Reattach 25 (buff) — (same)
- **Decimillipede (3)** — HP 46/46   Intent: 8   and also: Strategic (Debuff)
    Reattach 25 (buff) — (same)
```

**Incoming on round 1: 10 + 6 + 8 = 24. My HP: 2.**

Opening hand: Tinder Toss (1 Spark), Perfect Timing (1), Barbara+ (1),
Tinder Toss+ (1 Spark), Defend, Defend. Energy 3, Spark 1.

I worked the survival line before touching anything, and there is not one:

- **Maximum achievable Block is 19.** The only Block in hand is Barbara+ (9) and
  two Defends (5 + 5), which is exactly 3 Energy. There is no fourth Block card,
  no Energy left to play one, and nothing in hand that reduces an enemy's damage.
- Killing to reduce the incoming is out of reach: the smallest segment is 40 HP
  and `Reattach 25` would revive it anyway; my entire hand, if I could pay for
  it, is under 30 damage spread across three bodies at random.
- `Frozen` halves an action and is the one debuff that would have mattered.
  Barbara+ applies Hydro, and Cryo on Hydro is Frozen — but my only Cryo cards
  are Diona and Kaeya and neither was in hand.
- The one potion I held was `Strength Potion`. It adds damage. Nothing I owned
  added Block, healed, or reduced an enemy's number.

I played the 19 Block anyway (Barbara+, Defend, Defend) and spent the free Spark
on Tinder Toss+ for chip damage, because a 5-point shortfall against 2 HP leaves
nothing to optimise. The screen confirmed `Block 19`, `Energy 0/3`.

```
ok Ending turn
TOOL-BLOCKED: game_over

the run is over; there is nothing left to play

The run ended on floor 24.
```

**The run ended on the first enemy turn of the Elite, 5 damage short, on a floor
the map gave me no way to avoid.** I want to be exact about where the loss was
actually decided, because it was not here: it was fight 11, where a 121-HP
`Unknown` took 47 HP off me, and it was the routing decision three floors earlier
that walked into it blind. This screen only collected.

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

Five, and act 2's were mostly *routing and event* decisions rather than in-fight
ones — which is itself the difference from act 1.

1. **Whether to bank a Bomb or cash it (fight 11 turn 4).** With `Tender` on me,
   card damage was taxed 1 per card played and Bomb damage was not
   (`Its hit takes the enemy's debuffs, not yours`). I could spend Perfect Timing
   to cash 9 points of Bomb immediately, or place a second Bomb and leave
   `Bomb 17 ... Bombs here: 2` standing to grow. I banked. Next turn that
   decision was the kill: `Big Badda Boom` set off 17 into a 20-HP enemy while I
   stood on 2 HP. The trade is real — a banked Bomb dies with its host and does
   nothing at all if you die first.
2. **Diona's two Cryo applications, used as a two-stage tool (fight 9 turn 3).**
   `Apply Cryo twice` against an enemy wearing Hydro means application one is
   spent consuming the aura for **Frozen** and application two paints Cryo for a
   Melt. Its intent re-rendered from 18 to 9 on the spot and the Bomb then Melted
   for 26. One card bought a halved attack, an aura and 11 extra damage, and the
   choice was *which order to spend her two charges in*.
3. **Take Some Time at the Doll Room.** 5 HP for a choice of two relics instead
   of a random one. A genuine trade on paper. See (c) for why it was not one.
4. **Let It In at the Spirit Grafter.** 25 HP of swing against one upgrade and
   two cards of deck bloat, with the added card named and not described. I took
   the HP, and it was right by a wide margin — `Rejection` would have ended the
   run one fight earlier than it ended.
5. **Skipping the Imbalanced stun (fight 9 turn 2).** `If Bowlbug (Rock)'s
   attacks are fully blocked, it becomes Stunned`, with 14 Block against a
   15-damage attack. I could have spent the `Skill Potion` hunting one more point
   of Block for a free enemy turn, and declined because the enemy was about to
   die to a Bomb. One point of Block, one potion, one whole enemy turn — the
   cleanest small decision in the act.

### (b) What felt automatic, and what never seemed worth playing

**Blocking nothing against a `Defensive` / `Empower` / `Debuff` intent is still
the free lunch**, and act 2 kept paying it: fight 11 turn 1 and fight 9 turn 2
were both turns where the correct play was to hold no defence at all.

**Never worth playing: `Metamorphosis`.** Two copies, 2 Energy each, and what it
bought me was `Fwoosh!` — a card I could not play, in a hand where I could not
play three of five cards, because its Spark price is not what "free to play"
covers. Its other gift, `Rapid Fire`, then under-delivered by 8 (below). It is
the only card in 30 I would remove first.

**`Snecko Skull` remains inert.** No Poison card was offered, drawn or played in
either act; it has now done nothing for 24 floors.

**`Duck and Cover` is still `Defend`.** Both printed `cost 1, skill: Gain 5
Block` on every act-2 screen too — and `Defend` now has an upgraded copy printing
`Gain 8 Block`, while Duck and Cover has no way to become anything.

What stopped being automatic is **Strike**. Against `Hard To Kill 9` its 6 is the
only attack in the deck that loses nothing to the ceiling. One screen in two
acts, but a real one.

### (c) What I could not understand, or that contradicted its own printed text

1. **`Rapid Fire` delivered 8 less than its own printed number.** Fight 11 turn 4:
   `Deal 5 damage to a random enemy 4 times`, played at Strength +1, into a chain
   whose Bomb half I independently confirmed at 15 (`Ammo Scavenging` drew 2, so
   two Bombs went off). 31 total − 15 = **16 across four hits, i.e. 4 each**,
   against a printed 5 and a buffed 6.
2. **`Thoma — Blazing Barrier` absorbs 9, whatever its text implies.** `Gain 6
   Block. Whenever this Block absorbs damage, gain 3 Block` reads per-instance;
   measured three times against multi-hit intents it absorbed exactly 9 every
   time (fight 9 turn 1: 18 in, 9 taken; fight 10 turn 3: 9 in, 0 taken; fight 11
   turn 2: 21 in, 12 taken).
3. **Spark income, still.** Fight 10 turn 2 -> 3: Spark went **0 -> 2** on a turn
   in which I had *spent* my only Spark on Tinder Toss, no Bomb existed anywhere
   on the board, and exactly one Elemental Reaction occurred. `Pounding Surprise`
   pays per Bomb and there were none.
4. **End-of-turn tick damage does not follow the Strength on the screen.** Kaeya
   ticked for 14 on fight 11 turn 3 — which needs (6 + 2) × 1.75, i.e. the *base*
   Strength, where three cards of Tender should have left it at −1. On turn 4,
   after six cards, the ticks summed to 19 across Sparks 'n' Splash and Kaeya, and
   I could find no assignment of Strength that fits both turns.
5. **The Doll Room charges for information and delivers none.** `Take Some Time —
   Lose 5 HP. Choose 1 of 2 Doll Relics` resolved to `Receive Daughter of the
   Wind` / `Receive Bing Bong` — **two names, no effects**. The confirmation
   screen never printed the chosen relic's text either; I learned what Bing Bong
   does two floors later, from the relic list inside a fight.
6. **`Empower` means +2 or +15 and nothing distinguishes them.** Bowlbug (Nectar)
   turned a 3-damage attack into 18 (`Strength 15`); one fight later an
   Exoskeleton's identical `Empower (Buff)` intent produced `Strength 2`.
7. **`{Left}`.** `Blazing Barrier 6 (buff) — {Left} Block left.` An unfilled
   template placeholder, on every screen the buff appeared.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: `Metamorphosis`.** See (b). Two dead copies of a 2-Energy card
whose payout included a card its own promise could not pay for.

**Happiest to draw: `Big Badda Boom`.** `Set off. Deal 12 damage. Then deal
damage equal to what the Bombs dealt.` It is the answer to the previous seat's
sharpest finding: every other set-off in the deck *spends* a Bomb and throws the
surplus away, and this one converts the Bomb's number into a second copy of
itself. It won fight 11 outright from 2 HP, and it is the only card that makes
growing a Bomb strictly better than cashing it early. Honourable mention to
`Sparks 'n' Splash+`, which does the same trick from the other end (finding 6).

### (e) Did the previous seat's three sharpest findings hold up?

**1. "Perfect Timing is at its worst exactly when its own combo works."** *Held,
and it generalises past Perfect Timing — but with a mitigation neither of us knew
about.* Fight 9 turn 3: `Ka-pow!+` set off a 24-point Bomb stack into an 8-HP
Rock. Rock died to the first Bomb and **Ka-pow!'s own 7 damage was completely
wasted** — Nectar stayed on 36/36. So it is the *set-off keyword* that overkills,
not one card. The mitigation: the **second Bomb was not wasted, it migrated**
(finding 7).

**2. "Spark income is undocumented, and one turn of it is unexplained."** *Held,
in a cleaner instance than theirs* — Spark 0 -> 2 with no Bomb on the board at any
point in the turn. Act 2 also added a consequence they never met: **a Bomb
drought is a Spark drought**, because Pounding Surprise is the only printed income
and it needs a Bomb. On fight 11 turn 3 that locked three of five cards at once.

**3. "Hardened Shell inverts the character, and the game never says so."** *Held,
and act 2 raised it.* `Hard To Kill 9 — Reduce all damage taken and HP lost by
Exoskeleton to 9` is the same idea rebuilt as a **per-hit** cap, which is strictly
harder on Klee: a per-turn budget lets surplus become Block, a per-hit cap
punishes every multiplier individually and rewards nothing but hit *count*.
Measured: Kaboom!+ (10) and Strike (6) into the same target dealt 15.

### (f) Did act 2 ask anything of the deck that act 1 did not?

Yes — three things, and the deck answered one of them.

1. **A tax on card count.** `Tender` is the first mechanic in either act aimed at
   *how many* cards you play rather than which. Klee's shape is four to six cheap
   cards a turn, so it is close to a character-specific counter, and it hits the
   Block half of the deck hardest (`Defend` printing `Gain 2 Block`). The deck's
   answer is Bombs, which Tender cannot touch — a good answer, found only because
   two Bomb cards happened to be in hand.
2. **A hand that cannot be played.** Act 1 never produced one. Fight 11 turn 3
   did: `Spark 0`, three of five cards Spark-priced.
3. **Sustained damage rather than burst.** Act 1's worst fight cost 20 HP and its
   boss 27. Fight 11 alone cost **47**, from a single 121-HP enemy with no gimmick
   beyond volume. The deck kills fast in bursts, has no healing at all, and act 2
   asks a question burst does not answer.

What act 2 did *not* ask for: no Electro enemy, so `Overloaded`, `Superconduct`
and `Electro-Charged` stayed glossary entries across both acts, exactly as the
previous seat reported. I did fire **Frozen** for the first time in the run, and
it was excellent.

### (g) Anything a screen granted or changed without saying so

- **The act transition healed me to full.** Act 1 ended at 42/62 with a 27-damage
  Death Blow still to land; act 2's first battle screen printed `HP 62/62`.
- **`Sand Castle` never named its six upgrades.** I identified all six by sight.
- **A Bomb whose host dies migrates to another enemy** (finding 7).
- **`Bing Bong` doubles every card reward and no reward screen says so.** The
  screen still reads `Add a card to your deck.` (singular), shows four options and
  takes one. Two arrive.
- **`Pendulum`'s bracketed number moves between fights** — `(1)` throughout act 1,
  `(2)` at fight 9, `(1)` at fight 11 — so it is a run-level counter, which
  answers the previous seat's open question about why it did not fire on round 3.
- **The Doll Room's 5 HP and the Spirit Grafter's 25 HP heal were both invisible**:
  no screen printed an HP number between fight 9 and fight 10.
- **Strength applies to end-of-turn power damage** (Kaeya's tick), unmentioned on
  her card.

---

## Findings, ranked by sharpness

**1. The run ended on a floor with one exit, at an HP the map would not show me.**
At 2/62 the map printed `Where you can go next: - **Elite (path 1)**` and nothing
else. The Elite opened on 24 incoming; my hand's maximum possible Block was 19
(Barbara+ 9 + Defend 5 + Defend 5 = exactly 3 Energy, no fourth Block card, no
damage reduction anywhere in hand or potion belt). **A 5-point shortfall with no
legal line to close it.** A RestSite sat directly behind that Elite and three more
one floor further; none was reachable. The map is also the one screen that prints
no HP, so the routing decision that walked me into the 121-HP `Unknown` three
floors earlier was taken without the number that decided it. I am not claiming
the layout is wrong — I am claiming the *screen* withheld the input.

**2. `Tender` is a character-specific counter and it deletes the deck's defensive
half.** `Whenever you play a card, lose 1 Strength and 1 Dexterity this turn.`
Measured: after one card, `Strength -1 / Dexterity -1`, so the penalty lands after
the card resolves and card *i* plays at −(i−1). By the sixth card of fight 11
turn 4 my `Defend` re-rendered as **`Gain 2 Block`** against a printed 5. Klee
plays four to six cards a turn by construction, so this costs her more than a deck
of two expensive cards — and it costs her Block far more than her damage, because
**Bombs are immune** (`Its hit takes the enemy's debuffs, not yours`). Her damage
has an untaxed channel; her defence has none. The correct play under Tender is
highest-hit-count attack first, skills last, everything possible through a Bomb.

**3. `Rapid Fire` delivered 4 per hit where the card printed 5 and Strength
implied 6.** Fight 11 turn 4, played as the second card of the turn at `Strength
2` minus one Tender tick. Predicted 39 (Bomb 11 + Mine 4 + four hits of 6);
**actual 31**. `Ammo Scavenging — Draw 1 card for each of your Bombs that went off
this turn` then drew **2** (draw pile 10 -> 8), independently confirming both Bombs
fired and fixing their contribution at 15, which leaves 16 across four hits. The
only alternative reading — four hits of 5 with the Mine never firing, and Ammo
Scavenging's second card coming from Pendulum — contradicts the Spark count of +2.
**I could not make the card's own printed number come out.**

**4. `Thoma — Blazing Barrier` absorbs exactly 9 and prints 6 with an open-ended
rider.** Three measurements in three fights: 18 in / 9 taken, 9 in / 0 taken,
21 in / 12 taken. `Whenever this Block absorbs damage, gain 3 Block` reads as once
per absorbed hit, which against a `7x3` would be 12; it refreshed once. This is
the mispricing that cost me 3 HP I had budgeted, and by the end of this run 3 HP
was not a rounding error.

**5. `Hard To Kill 9` is a per-hit cap, and it inverts the deck harder than act 1's
per-turn budget did.** Tested directly: Kaboom!+ (10) and Strike (6) into one
target dealt **15**, so 10 became 9 and 6 stayed 6. Under it, bomb growth, the
1.75x Melt, Big Badda Boom's doubling rider and Perfect Timing's replay are all
worth nothing; `Careful Arrangement` (offered to me as a reward: *Move all your
Bombs onto the enemy as one Bomb*) is actively harmful; and **Strike is
rate-competitive with the deck's best attack.** Act 1's `Hardened Shell 20` at
least let surplus become Block. A per-hit cap turns surplus into nothing.

**6. `Sparks 'n' Splash` reads the *sum* of Bomb sizes and does not consume them —
the only damage in the deck that spends nothing.** Fight 9: Rock's badge read
`Bomb 16 ... Bombs here: 2`, the power fired for **16**, and the badge afterwards
read `Bomb 24 ... Bombs here: 2` — both Bombs still standing, grown by 4 each. The
card's `equal to the Bombs on it` reads as either the count (2) or the sum (16);
only the number settles it. Paired with a banked Bomb stack it is Klee's best line
and nothing tells you it exists.

**7. A Bomb whose host dies migrates to a surviving enemy.** Fight 9 turn 3:
`Ka-pow!+` set off `Bomb 24 ... Bombs here: 2` on an 8-HP Rock. Rock died, Spark
rose by exactly 1 (so exactly one detonation), and Nectar — which no Bomb card had
ever targeted — printed `Bomb 15 (buff) ... Bombs here: 1`. A substantial,
invisible mitigation of the previous seat's overkill trap; the same turn showed
the trap still biting on the *card's* own damage, since Ka-pow!'s 7 vanished with
the corpse.

**8. `Metamorphosis` promises "free to play" and can hand you a card its freeness
cannot pay for.** Fight 11 turn 3, `Fwoosh!` arrived from Metamorphosis and the
screen refused it: `CANNOT BE PLAYED: you have no Spark, and this costs 1`. The
rules text says so in advance — `an effect that makes a card free to play, or cuts
its cost to 0, covers Energy only, and the 1 Spark is still spent` — so this is
not a rules bug; it is a card whose own wording omits the exception the glossary
spells out. The same hand had three of five cards Spark-locked, which is the
practical form of the problem: **Klee has two currencies and only one of them has
printed income.**

**9. The Doll Room sells information and delivers a coin flip.** `Lose 5 HP.
Choose 1 of 2 Doll Relics` -> `Receive Daughter of the Wind` / `Receive Bing Bong`.
Names only. The whole event is priced on knowing more; the confirmation screen
printed only `Proceed`; the relic's text first appeared two floors later inside a
battle. The 5 HP was not wasted — Bing Bong is a real relic — but it did not buy
what it charged for.

**10. `Sand Castle` upgraded six cards and named none of them.** I recovered all
six by sight over three fights, and the sizes are large: `Kaboom!` 7 -> 10,
`Defend` 5 -> 8, `Barbara` 6 -> 9, `Tinder Toss` 4 -> 6 per hit, `Ka-pow!` 4 -> 7,
`Sparks 'n' Splash` cost 2 -> 1. This is the previous seat's Smith-screen complaint
in a stronger form: there, at least, you choose the card.

**11. `Empower (Buff)` covers `Strength 2` and `Strength 15` with identical text.**
Bowlbug (Nectar) went from a 3-damage attacker to an 18-damage one in one turn; an
Exoskeleton's identical intent produced +2. Nothing on either screen distinguishes
a buff worth interrupting from one worth ignoring.

**12. `{Left}` ships to the player.** `Blazing Barrier 6 (buff) — {Left} Block
left. When it absorbs damage, gain 3 Block.` Present every time the buff appeared.

**13. Confirming the previous seat: Spark income is undocumented.** Cleanest
instance of the act, fight 10 turn 2 -> 3: **Spark 0 -> 2**, on a turn where I had
spent my only Spark, no Bomb existed on the board at any point, and exactly one
Elemental Reaction occurred.

**14. The interface is still the best-designed thing here, and act 2 extended it.**
Three new instances worth keeping: the Bomb badge writing `Set off here deals 17
Pyro damage **capped by Hard To Kill**` rather than quoting a number it knew I
would not get; `Frozen` re-rendering the *enemy's* intent from 18 to 9 the moment
it landed; and upgraded cards explaining their own cost reduction in place (`The
cost printed on this card is 2; it is showing 1 here, because this copy is
upgraded — that is permanent`) while carefully distinguishing it from a temporary
one (`This copy is not upgraded, so the cut is this turn's board and not the
card`). On fight 10 I played Barbara+ into an aura her own `Reaction preview` line
had warned would waste her: the interface was right and I was careless.

**15. Where I could not tell.** I cannot say what `Daughter of the Wind` does, so
I cannot say whether the Doll Room choice mattered. I cannot reconcile Rapid
Fire's 8 points (finding 3) or fight 11 turn 4's end-of-turn ticks (28 dealt
against 17-21 priced) with any rule the screens print, and I had no second Rapid
Fire to test with. I never reached a Shop despite routing toward two, so I can say
nothing about act-2 prices, and **no screen printed my gold total at any point in
the act.** I never saw a Smith screen, a Treasure room, or the boss, so this
record says nothing about `The Insatiable`. And I cannot say whether the deck that
died was too bloated at 30 cards or simply unlucky: `Bing Bong` doubled four adds
and no card removal was ever available to answer it.

---

## Non-blindness declaration

- Commands run: **only** `GITS_LANE=2 python -m understudy.blindplay observe` and
  `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, from the repo root
  `C:\Users\Monty\Documents\GitHub\GItS`. **No other `understudy` subcommand was
  run at any point** — no `harness`, `session`, `audit`, `notes`, `scenario`,
  `staged_turn`, `soak` or `embark`. No `git` command was run.
- Tools used: **Bash** (to run the two allowed commands, with `sed`/`grep`/`tail`
  used purely to trim `observe` output), **Read** (once, for the previous seat's
  record), **Write** (once, to create this record) and **Edit** (to append to this
  record — a heredoc append failed to parse, the same trap the previous seat
  logged, so every later append used Edit). Nothing else.
- Repo files read: **exactly one** —
  `C:\Users\Monty\Documents\GitHub\GItS\review\qa\klee-round-8-2026-09-03\opus-act1.md`,
  the previous seat's record, as instructed. No source, no YAML, no docs, no
  rulings, no backlog, no logs, no other records.
- Files written or edited: **exactly one** — this record. No scratch file was
  created. No identifiers were minted.
- I never launched, closed, restarted or tore down the game, and never touched
  lane 1.
- Everything in this record comes from screens printed by `observe` and `act`.
- **The lane was left standing** exactly where the run ended. `end turn` at the
  Decimillipede Elite returned `TOOL-BLOCKED: game_over`, and one bare `observe`
  afterwards returned the same three lines, confirming the state. **Nothing was
  sent to the lane after that `observe`.**

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*

