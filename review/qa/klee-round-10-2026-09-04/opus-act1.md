# Klee round 10, run 1 — blind seat, act 1

## Identity

- **Model / seat:** Claude Opus (Fable-family), blind TESTER seat, lane 1, `KLEEMOD-KLEE`.
- **Run seed:** not printed on any screen I was shown; I have no seed to report.
- **Character:** Klee (Pyro / Bomb / Spark kit).
- **Act:** 1. The map named the act boss as **Vantom** from the first map screen.
- **Actions accepted:** 206 `act` calls. Refusals: 3 (two were my own shell-quoting
  of apostrophes, one was targeting a corpse). Two `rest` calls returned
  `error Rest site room is not open` on first try and worked on retry — I counted
  those as one accepted action each.
- **Termination reason:** the stop condition was met, not a budget. Vantom died,
  its reward screen was handled, and the lane now sits on the act-2 map (next node
  `Ancient`). Under the 250-action cap with ~44 to spare.
- **HP trajectory:** 62 → 55 (fight 1) → 62 (event heal) → 62 (fight 2) → 62
  (fight 3) → 41 (fight 4) → 19 (fight 5) → 34 (rest) → 34 (fight 6) → 13
  (fight 7 mid) → 6 (fight 7 end) → 24 (rest) → **10/62** at the end of the boss.
  Lowest point 6/62. Never above 62; max HP never moved.
- **Gold at end:** 114 (spent 213 on Dolly's Mirror at the act-1 shop).
- **Potions held:** 1 — Colorless Potion. (Spent: Skill Potion in fight 7, Speed
  Potion and Dexterity Potion in the boss fight.)
- **Relics at end:** Pounding Surprise (starter — a Bomb going off gives 1 Spark),
  Arcane Scroll, Ripple Basin (4 Block on a turn with no Attacks), Dolly's Mirror,
  Tingsha (3 damage per card discarded during your turn — never once triggered; I
  had no discard effect all act).
- **Deck at end (21 cards):** Strike ×4 (one enchanted *Slither*), Defend ×4,
  Jumpy Dumpty+ ×2, Ka-pow!, Sparks 'n' Splash+, Fwoosh!, Perfect Timing,
  Coven Errand, Fish-Flavored Bait, Dig In, Amber — Fiery Rain,
  Noelle — I Got Your Back, Chained Reactions, Clumsy (curse).

**Neow pick: Arcane Scroll** ("Obtain a random Rare Card"). I took it over New Leaf
(transform 1) because on a kit I had never seen, a rare card is the fastest way to
learn what the kit's ceiling looks like; and over Silken Tress because it printed
the word "Glam" with no definition anywhere on the screen and also cost all my gold,
so I would have been paying everything for a keyword the game had not shown me.
**The screen never told me which rare I got.** I only learned it was Sparks 'n' Splash
two rooms later, on an unrelated enchant screen that happened to list my deck. Same
gap later at the "This or That?" event: I chose the random relic and the screen never
named it — I found out it was Tingsha at the start of the next fight.

---

## Fight 1 — Nibbit (42 HP)

**Turn 1** (62 HP, 3 energy). Played **Jumpy Dumpty** (Bomb 8) → **Strike** (6) →
**Defend** (5 Block). Held Ka-pow!.
*Rejected:* Ka-pow! immediately, which would have set off the Bomb 8 for 8 + 4 = 12
right then. I rejected it because Ka-pow! prints **Retain** and costs 0, so holding
it costs literally nothing while the badge printed *"grows 4 a turn"* — waiting one
turn turns 8 into 12 for free. That is a real decision and the card text is what
made it decidable. Also rejected double-Defend (10 Block, 0 damage): 12 incoming
against 62 HP did not justify the tempo.
Took 7 (12 attack − 5 Block). 55/62.

**Turn 2** (Nibbit 36, Bomb 15 badge reading `Bomb 12`, intent 6 + Defend). Played
**Ka-pow!** (0) → Bomb 12 went off for 12, then 4 = 16 → three **Strike**s.
*Rejected:* waiting another turn for Bomb 16. Rejected because the enemy printed a
*Defensive (Defend)* intent alongside its attack — blocking next turn would have
eaten my Strikes, so spending the bomb before the shield went up was strictly better.
Also the Jumpy Dumpty rider put a Mine 3 on the enemy, and the printed Mine rule
(*"goes off when its enemy attacks you, before the hit lands"*) meant its own attack
would finish it. It did: the fight ended on the enemy's turn.

**Reward:** 15 gold + **Fwoosh!** over Mine Toss / Sorry, Jean... / a Freminet
companion. Fwoosh! prints *cost 1 Spark* and the screen went out of its way to say
the Spark is a price and not an Energy cost — that is an energy-free Set off, and
with Pounding Surprise giving a Spark per Bomb going off, it reads as a loop the
moment you have two bombs stacked. That reasoning turned out to be exactly right.

---

## Fight 2 — Leaf Slime (S) 15, Twig Slime (M) 27, Twig Slime (S) 7

Entered at 62/62 (a Sapphire Seed event had healed 9 and upgraded Jumpy Dumpty to
**Jumpy Dumpty+**, Bomb 11 / Mine 4).

**Turn 1.** **Jumpy Dumpty+** on Twig Slime (M) → **Ka-pow!** on the same target
(Bomb 11 went off: 11 + 4 = 15, Mine 4 landed on all three, Spark 1→2) →
**Fwoosh!** on Twig Slime (S), which set off the freshly-laid Mine 4 there for
4 + 6 = 10 and killed it outright → two **Strike**s into Leaf Slime (S) to leave
it at 3, so its own Mine 4 would finish it when it attacked.
*Rejected:* spreading the Jumpy bomb onto the small slimes. Rejected because the
card's rider is *"When it goes off, place a Mine 3 on ALL enemies"* — the bomb is a
delivery system for board-wide mines, so it wants to be on the target you will
detonate, not the target you want dead. This was the first turn where the kit felt
like it had an actual shape.
Result after the enemy turn: two of three dead, no damage taken. The Mine wall did
exactly what its badge said, including the "before the hit lands" clause.

**Turn 2.** Twig Slime (M) at 12, Mine 8 on it, attacking for 11. Played
**Sparks 'n' Splash+**… (the rare, cost 2, *"At the end of your turn, deal Pyro
damage to a random enemy equal to its largest Bomb"*) then **Strike**.
*Rejected:* just Striking and letting the Mine finish it — which would also have
worked. I paid 2 energy for the power specifically because I had not seen it work
and wanted to read it, and I say so plainly: that was a tester's choice, not the
best play. It killed the slime at end of turn for 8.

**Reward:** **Perfect Timing** over Bang Bang! / Ammo Scavenging / Razor. I picked
it for 1 energy, 8 damage, and Set off attached — the cheapest reliable detonator —
over Bang Bang! (2 Sparks) because my Spark income depended on bombs I did not yet
reliably have.

---

## Fight 3 — Shrinker Beetle (38 HP)

**I misread this fight's board and the bridge is why.** The opening screen printed
the enemy block *twice*, and I recorded "two Shrinker Beetles" in my head. There was
one. The duplication recurred in fights 5, 6, 7 and the boss, always and only when
exactly one enemy was alive, so I am confident it is a printing artifact of the
bridge and not the game. It cost me nothing here, but on a screen where an
identically-named enemy really is duplicated, this makes the board unreadable.

**Turn 1.** **Jumpy Dumpty+** (Bomb 11) → **Sparks 'n' Splash+**.
*Rejected:* Strike + Defend. Rejected because the enemy's printed intent was a
Debuff, not an attack, so Block was worth nothing and a power played on a free turn
is a power that pays for the rest of the fight.
Splash dealt 11 at end of turn. Then the debuff landed: **Shrink −1 — "While
Shrinker Beetle is alive, your Attacks deal 30% less damage."**

The best thing the kit did all act happened here without any fanfare: **every card
in my hand redrew itself at the reduced number.** Ka-pow! printed `Deal 2 damage`,
Perfect Timing printed `Deal 5`, Strike printed `4`. Meanwhile `Bomb 15` did not
move, because the Bomb keyword prints *"Not an Attack: only their Vulnerable and a
cap move it."* I could read straight off the screen that the debuff had gutted my
attacks and not touched my bombs, and I changed plan on that basis. That is the one
place the kit's text and the kit's behaviour were in complete agreement.

**Turn 2.** **Strike** (4, shrunk) → **Defend** ×2, holding Ka-pow!.
*Rejected:* Perfect Timing to set off Bomb 15 for 15 + 5. Rejected precisely because
of the split above — my attacks were worth 30% less this turn and the bomb was not,
so the bomb wanted to keep growing while my attacks were bad. Splash dealt 15 for
free at end of turn.

**Turn 3.** Enemy at 8, Bomb 19. **Ka-pow!** (0) for 19 + 2. Over.
*Rejected:* nothing. This was not a decision, it was a formality — the correct play
was the 0-cost card I had been holding for two turns.

**Reward:** 16 gold, Skill Potion, and **Coven Errand** over Rapid Fire / Sorry,
Jean... / Lisa. I wanted a second bomb placer more than I wanted damage.

---

## Fight 4 — Vine Shambler (61 HP)

**Turn 1.** Drew no bomb placer at all. **Fwoosh!** (Spark, set off nothing — just
6 damage) → **Perfect Timing** (8, set off nothing) → **Strike** → **Defend**.
*Rejected:* full aggression (a second Strike instead of Defend) for 26 instead of 20.
Rejected because with no bomb on the board there was no payoff to racing; the extra
6 damage was not worth 5 HP.
**This is the kit's dead hand.** Fwoosh!, Perfect Timing and Ka-pow! all print
"Set off" and all three are worth roughly a vanilla Strike when there is nothing to
set off. On a hand with no placer, Klee is a below-rate basic deck and the turn has
no decision in it.

**Turn 2.** **Sparks 'n' Splash+** (now cost 1 after a Smith) → two Strikes →
Defend. Then the enemy applied **Tangled**, printed on my status bar as `Tangled 1 —
Attacks cost an additional [Energy] this turn`, while the same effect on each card
printed as `*Entangled* — Costs an additional [Energy]`. **Two names for one thing on
one screen.** Minor, but I had to stop and check whether they were two separate
debuffs.

**Turn 3.** With both placers in hand: **Jumpy Dumpty+** (Bomb 11) → **Coven Errand**
(Bomb 5) → **Defend**, holding Ka-pow!.
*Rejected:* Jumpy + Ka-pow! immediately, for 11 + 4 now plus board mines. Rejected
because two stacked bombs both grow 4 a turn, so banking turned 16 into 24 for one
turn of patience, and Ka-pow!'s Retain made the wait free. I paid 11 HP for it. The
aggregate badge made this legible: it printed `Bomb 24 (buff) — Set off here deals 24
Pyro damage. Bombs here: 2.` One number for the whole pile plus the count is exactly
the right thing to print.

**Turn 4.** **Ka-pow!** for 24 + 4 into an 18-HP enemy. Over.

**Reward:** **Fish-Flavored Bait** (4 damage + Bomb 4 for 1 energy) over Flame Dance /
Powder Charge / Dahlia. Third placer, and one that is not a dead card on an empty
board.

---

## Fight 5 — Brute Raider 30, Assassin Raider 22, Tracker Raider 25

The fight that nearly ended the run: 41 → 19 HP.

**Turn 1.** **Coven Errand** on Assassin (Bomb 5) → **Fwoosh!** on Assassin (set off
5, +6 = 11, and Pounding Surprise handed the Spark straight back) →
**Sparks 'n' Splash+** → **Defend**.
*Rejected:* banking the Bomb 5 instead of popping it. Rejected because Fwoosh! costs
no Energy and the Spark returns when the bomb goes off, so the pop was free in both
currencies — that is the loop I bought Fwoosh! for, and it worked exactly as the two
cards read together.
Took 12. 29/62.

**Turn 2.** Frail 2 landed; Defend printed `Gain 3 Block` instead of 5, again
correctly redrawn on the card. 18 incoming, 29 HP. **Jumpy Dumpty+ on the Assassin
(11 HP) rather than the Brute** → **Defend** ×2.
*Rejected:* the Brute (30 HP, the durable target where a growing bomb is not wasted),
and rejected Fish-Flavored Bait for tempo damage. I put the Bomb 11 on the 11-HP
Assassin specifically because Sparks 'n' Splash+ deals *"damage equal to its largest
Bomb"* at end of turn, and 11 was exact lethal on that target if the power picked it.
It did. The Assassin died at end of my turn and never took its 10-damage swing —
I took 2 instead of 12.

**And then the board did something no screen had told me about.** The Assassin died
carrying a Bomb 11. Next turn, the *Brute Raider* was wearing `Bomb 15`. The bomb
moved off the corpse onto a survivor and grew on schedule. Nothing in the Bomb
keyword, the Mine keyword, or any card says what happens to a Bomb when its host
dies. It worked in my favour and I took the 15-damage detonation happily, but I could
not have predicted it, and if it had gone the other way (bomb lost) I would have
mis-planned an entire turn on it. **This is the single largest hole in the printed
rules that I hit all act.**

**Turn 3.** **Perfect Timing** on the Brute → Bomb 15 went off for 15, +8 = 23; the
Jumpy rider then dropped a Mine 4 on the Brute itself, **Ka-pow!** set that off too,
and the Brute (30 HP, Strength 3) died to 15 + 8 + 4 + 4. Spark went 1 → 3, which is
how I reconstructed that two separate bombs had gone off. Then two Strikes into the
Tracker.
*Refusal logged:* my third `play "Strike (1)" on "Brute Raider"` was refused because
the Brute was already dead. The refusal was correct and the card stayed in hand.

**Turn 4.** Tracker at 5 (its own Mine had taken 4 off it before it swung).
One Strike. Over. No decision.

**Reward:** **Dig In** (1 Spark, 8 Block) over Powder Charge / Tinder Toss /
Charlotte. At 19/62 with four Sparks banked, energy-free Block was the only thing I
wanted. It later did the most load-bearing work in the boss fight.

---

## Fight 6 — Twig Slime (M) 27, Leaf Slime (M) 32, Leaf Slime (S) 14, Twig Slime (S) 9

**Turn 1.** **Jumpy Dumpty+** on the biggest slime → **Strike** the 9-HP one down to
3 → **Defend**.
*Rejected:* playing only skills to collect Ripple Basin's 4 Block. Rejected because
7 incoming against 35 HP did not need it, and leaving the small slime at 3 set up a
Mine kill.

**Turn 2.** 23 incoming, 35 HP. **Perfect Timing** on the bombed slime → Bomb 15
went off (15 + 8 = 23), Mine 4 landed on all four → **Dig In** (8, paid with the
Spark the detonation had just generated) → **Defend** ×2. 18 Block.
*Rejected:* holding the bomb another turn for 19. Rejected because the mines were
worth more than the 4 extra damage: three of the four slimes were attacking, so
three Mine 4s would fire before their hits landed. They did. The 3-HP slime died to
its own mine before swinging, and I took **1 damage off a 23-damage turn**. This was
the best turn of the run and the reason was legible in advance from two badges.

**Turn 3.** **Fwoosh!** set off a Mine 8 for 8 + 6 = 14, exactly killing a 14-HP
slime; **Strike** killed a 5-HP one; **Ka-pow!**, **Strike**, **Fish-Flavored Bait**
took the last one to 9 with a fresh Bomb 4 on it.
*Rejected:* using Ka-pow! on the bombed target instead of the bare one. Rejected
because Fwoosh! was free (Spark) and Ka-pow! was free (0 energy) — with two free
detonators I could aim one at each pile, which is a genuinely nice piece of design.

**Turn 4.** Ka-pow! for 8 + 4 into a 9-HP enemy. Over.

**Reward:** **Amber — Fiery Rain** (1 energy, 4 damage to ALL enemies 3 times) over
Fwoosh! / Sugar Rush / Quick Fuse. Best damage-per-energy on the screen and my only
real AoE.

**Shop (227 gold):** bought **Dolly's Mirror** (213) and copied **Jumpy Dumpty+**.
*Rejected:* Regal Pillow (184, +15 per rest — one rest remained, so 15 HP),
Careful Arrangement, and Card Removal at 75. Doubling the card that both places the
biggest bomb and seeds the board-wide mines was worth more than any of them, and it
is the purchase the boss fight was won on.

---

## Fight 7 — Snapping Jaxfruit 31, Flyconid 47

**Turn 1.** No Defend in hand at all. **Fish-Flavored Bait** on Flyconid (4 + Bomb 4)
→ two **Strike**s, holding Ka-pow!.
*Rejected:* Ka-pow! to pop the Bomb 4 for 8 total. Rejected because popping a Bomb 4
is the worst possible use of a detonator; banking it turned it into 8 next turn at no
cost. Took 11 with no Block available. 23/62.

**Turn 2.** 23 HP, 16 incoming, Frail (Defends at 3). **Jumpy Dumpty+** on Flyconid
(pile → 19) → **Ka-pow!** for 19 + 4 = 23, Mine 4 on both → **Defend** ×2.
*Rejected:* the all-skills line (Jumpy + 2 Defends, keeping Ka-pow! retained), which
would have left me at 17 instead of 13 with a Bomb 23 banked. I chose the detonation
because it took Flyconid from 31 to 4, and removing an 11-damage attacker permanently
is worth more than 4 HP of Block once. That was the right call and it still left me
at 13, then 6.

**Turn 3.** 13 HP. Used **Skill Potion** — offered Pop! / Careful Arrangement /
Powder Charge, i.e. **three bomb-placement skills and no defensive option at all**,
which at 13 HP was a genuinely bleak roll. Took **Pop!** (0 energy, Bomb 5).
Then **Coven Errand** (Bomb 5) → **Pop!** (Bomb 5, pile now 10) → **Fwoosh!**
(set off 10, +6 = 16) → **Perfect Timing** (8) → **Strike** killed Flyconid.
Jaxfruit went 27 → 3.
*Rejected:* killing Flyconid with Fwoosh! and pointing the Strike elsewhere. Rejected
because stacking two Bomb 5s *before* the free Spark detonator is worth 10 extra
damage, and the free card should always be the one aimed at the pile.

**Turn 4.** One Strike into a 3-HP enemy. Over, at 6/62.

**Reward:** **Noelle — I Got Your Back** (6 Block, +4 per Mine going off this turn)
over Quick Fuse / Pop! / Coven Errand. At 6 HP I needed Block, and it is the only
card I was offered all act that pays Klee's own mines back as defence.

---

## Fight 8 (boss) — Vantom, 173 HP, **Slippery 8**

`Slippery 8 (buff) — The next 8 times Vantom loses HP, it only loses 1 HP instead.`

This is a direct counter to the Bomb keyword and I could read that off the two texts
together: *Set off* prints *"Every Bomb on the target goes off first, **one at a
time**, each a Pyro hit for its size"* — so a three-bomb pile detonated under
Slippery is three separate HP-loss events for **3 total damage**. The whole boss is
"do not touch your own detonators until the shield is gone," and the kit's read of
that was clean. Best single interaction of the round.

**Turn 1** (24 HP, 7 incoming). **Jumpy Dumpty+** (Bomb 11, banked) → **Strike**
(burns 1 charge for 1 damage) → **Dig In** (8 Block).
*Rejected:* Fwoosh! + Ka-pow!, which would have burned three charges but blown the
Bomb 11 for 1 damage. Rejected on the arithmetic above. Also rejected skipping the
Strike to collect Ripple Basin's 4 Block — 8 Block already covered the 7 incoming, so
the fourth block was worthless and the charge burn was free.
Took 0.

**Turn 2** (12 incoming). **Amber — Fiery Rain** — three hits, therefore **three
Slippery charges for 3 damage**, the single most efficient charge-burner I owned →
**Coven Errand** (bank) → **Defend**.
*Rejected:* Strike instead of Coven Errand. Rejected because a second bomb in the
pile compounds — two bombs grow 8 a turn, one grows 4.
Slippery 7 → 4. Took 7. 17/62.

**Turn 3.** Vantom announced **26 damage** into my 17 HP. **Speed Potion** (+5 Dex)
→ **Dexterity Potion** (+2 Dex) → **Defend** (12) → **Noelle** (13) →
**Jumpy Dumpty+** (third bomb), all skills so **Ripple Basin** added 4. 29 Block
against 26. **Took 0.**
*Rejected:* spending anything on damage. There was nothing to decide about whether to
survive; the decision was whether the Dexterity Potion's permanent +2 was worth
burning early, and I judged yes because Dig In and Noelle both scale off it and both
recur.

**Turn 4** (Vantom buffing, no attack). **Sparks 'n' Splash+** → **Strike** →
**Defend**. Slippery 4 → 2 (the Strike and the power's end-of-turn tick each burned
one).
*Rejected:* detonating the Bomb 51 pile. Rejected because three bombs under
Slippery 4 = 3 damage. Discovered here that **Sparks 'n' Splash+ burns a Slippery
charge every turn for free without consuming the bomb** — the power ticks off the
largest bomb's value but leaves the bomb standing. Under a shield that counts events,
that is a free charge-stripper; without one it is a free ~15/turn. Strongest card in
the deck and the least obviously so from its text.

**Turn 5.** Slippery 2, Bomb 63 across 3 bombs. **Strike (Slither, 0)** → **Strike**
(shield now 0) → **Strike** (full 6) → **Ka-pow!** → **63 in one beat**, +4, plus two
Mine 4s that fired on Vantom's own attack. Vantom 167 → 80. **Defend** covered the
swing.
*Rejected:* banking one more turn for Bomb 75. Rejected because Vantom's damage was
escalating faster than the pile (26 → 28) and I was at 15 HP; one more turn of
banking was a turn I could not pay for. Ordering the three cheap Strikes *before* the
detonator, to strip the last shield charges with 1-damage hits, was the whole turn
and it is the most satisfying thing this kit let me do.

**Turn 6.** 15 HP, 28 incoming. **Jumpy Dumpty+ ×2** (both copies — the Dolly's
Mirror purchase paying out) → **Defend**, all skills → Ripple Basin. 11 Block.
Took 5.

**Turn 7.** 10 HP, 28 incoming. **Dig In** (10) → **Noelle** (8) → **Defend** (7) →
Ripple Basin (4) = **29 Block vs 28.** Took 0. Splash chipped 15 off for free.
*Rejected:* Amber for 12 damage, which would have forfeited Ripple Basin's 4 and put
me on 7 HP. At 10 HP against a boss that had just announced 28, no amount of damage
was worth 3 HP of margin.

**Turn 8.** Vantom buffing again — a free turn at 54 HP with a Bomb 38 pile.
**Strike** (6) → **Fish-Flavored Bait** (4 damage, and its Bomb 4 joined the pile
*before* detonation) → **Perfect Timing** set off 42 and added 8. **Vantom dead**,
me at 10/62.
*Rejected:* Perfect Timing first. Playing Bait before the detonator was worth 4 extra
damage for free, and that ordering question — which placer goes in before you pull the
trigger — is a real, repeatable decision the kit asks every big turn.

**Boss reward:** 100 gold + **Chained Reactions** ("Whenever one of your Bombs goes
off, place a Bomb 3 on a random enemy") over Sparks 'n' Splash / Sugar Rush /
Neuvillette. Lane left on the act-2 map, next node `Ancient`.

---

## The kit, after 8 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Four, and they recurred:

1. **Bank or pop.** Every bomb prints its size and *"grows 4 a turn"*, and my main
detonator (Ka-pow!) is 0-cost with Retain — so waiting is free in energy and costs
only HP. Almost every turn asked "is +4 per bomb worth one more enemy swing?" and the
answer genuinely changed with my HP, with Frail, with the enemy's printed intent, and
with whether a Defend had shown up. That is the kit's spine and it is a good one.
2. **Which target carries the pile.** Jumpy Dumpty+'s rider (*Mine 4 on ALL enemies
when it goes off*) means the bomb is a delivery system for board-wide mines, so it
wants the target you intend to *detonate*, not the target you want dead. But
Sparks 'n' Splash+ hits "a random enemy equal to its largest Bomb", which wants the
bomb on a target whose HP equals the bomb. In fight 5 those two pulled opposite ways
and I had to pick. That is a real tension between two of my own cards.
3. **Ordering inside the detonation turn.** Placers before detonators; cheap 1-damage
hits before the big pop when a shield counts events; the free (Spark, 0-cost) cards
aimed at the pile so the Energy cards can go elsewhere. Fight 7 turn 3 and boss
turn 5 were both won on ordering alone, with the same cards in the same hand.
4. **Spark versus Energy.** Fwoosh!, Dig In and Powder Charge cost Sparks, and
Pounding Surprise refills Sparks from detonations. So "do I detonate" is also "do I
want to be able to afford 8 Block next turn." The screens are unusually careful about
this — every Spark card reprints *"its N Spark is a price, not an Energy cost"* — and
the resource genuinely opened lines that Energy could not.

**(b) What felt automatic, and what never seemed worth playing.**

- **Ka-pow! on the pile is never a decision** — it is 0 cost, it retains, and once the
pile is big enough the card plays itself. Four of my eight fights literally ended on a
Ka-pow! I had been holding for two turns. Correct, satisfying the first time, a
formality by the fourth.
- **The kill turn.** Every fight ended the same shape: bank, bank, detonate, mop up.
The last turn of six of eight fights had no rejected alternative at all.
- **Tingsha never fired once.** No card in my deck discards, so a relic I carried for
three fights was pure decoration. Not a kit bug, but worth noting that a Klee deck may
have no way to turn it on.
- **Defend and Strike.** Unremarkable, but the basics being 20% of a 21-card deck is
what made the dead hands (below) happen.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **A Bomb survives its host's death and moves to another enemy, and nothing says
so.** Fight 5: I put Bomb 11 on the Assassin, the Assassin died at end of my turn, and
next turn the Brute was wearing `Bomb 15`. The Bomb keyword, the Mine keyword and
Jumpy Dumpty's text between them describe growth, detonation and Vulnerable — and are
silent on death. This is the one rule I played the whole act without knowing.
2. **"Hexerei" is defined in a way that does not let you use it.** Coven Errand's
condition is *"If you played a Hexerei card this turn, place it on ALL enemies
instead"*, and the keyword reads *"A Companion card from the witches' circle. It does
nothing by itself; Klee is one too, and her own cards pay when you play one."* I was
offered several Companion cards (Amber, Noelle, Freminet, Lisa, Charlotte, Fischl,
Navia, Dahlia) and could not tell from any screen which of them are "from the witches'
circle" and therefore turn Coven Errand on. I never once knew whether my Coven Errand
was going to hit one enemy or all of them. The Companion keyword is defined
separately and purely typographically ("a character's name, a dash, then its own"),
which makes the two terms look like synonyms while Coven Errand clearly treats them
as different. **Klee is one too** also implies playing a *Klee* card satisfies it,
which would mean nearly anything satisfies it — but Coven Errand never once printed
an "all enemies" preview, so evidently not.
3. **Sparks 'n' Splash's "its largest Bomb"** — whose? The random enemy's, or mine?
On a solo enemy it did not matter; on a four-slime board I placed a bomb specifically
to game it and still could not tell from the text whether an unbombed target would be
picked and deal 0. It behaved as "the chosen enemy's own largest bomb", but the
sentence does not say that.
4. **Tangled vs Entangled** — one debuff, two spellings, on the same screen (status
bar says `Tangled`, the card keyword says `*Entangled*`).
5. **Bridge-level, not kit:** the enemy block **prints twice whenever exactly one
enemy is alive**, which cost me a misread of fight 3's board. And two `rest` calls
returned `error Rest site room is not open` on a rest screen that was plainly open,
then worked on immediate retry.
6. Two "obtain a random X" effects (Neow's Arcane Scroll, the This-or-That relic)
**never named what I got**. I learned both by accident, rooms later.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** **Fwoosh!** in an opening hand. On turn 1 with no bomb on the
board it is a Strike that costs my only Spark, and the whole Set off clause — the
reason it exists — is blank. Ka-pow! and Perfect Timing have the same failure mode
but at least cost 0 and 1 Energy; Fwoosh! spends the resource I need for Dig In. The
runner-up is **Clumsy**, but it is Ethereal and self-exhausts, so it barely counts.
- **Happiest to draw:** **Jumpy Dumpty+**, and it is not close. It is the only card
that both grows the pile *and* seeds the board with mines, and the mines are the
kit's defence, its finisher on low-HP enemies, and (via Noelle) its Block. In fight 6
one Jumpy Dumpty+ detonation turned a 23-damage enemy turn into 1 damage taken.
Honourable mention to **Sparks 'n' Splash+**, which quietly did more total damage
than any attack in the deck and whose text badly undersells it.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one.** Turn 1 of fight 1 I held a 0-cost Retain detonator
(Ka-pow!) and a card that placed a Bomb 8 that the screen told me would grow to 12.
The decision — pop for 12 now or hold for 16 next turn and eat 7 more damage — was
fully legible from the three printed lines (*Retain*, *grows 4 a turn*, *goes off
only when Set off*) and had a real cost either way. I have played opening turns in
this genre that were "play Strike, play Defend"; this was not one.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside the two allowed `observe` / `act` forms, all via the Bash tool:

- `mkdir -p <scratchpad>/…` — once, to create my scratch directory.
- `echo "…" >> <scratchpad>/actions.txt` — appended after every accepted action, as
  the coordinator instructed, to keep the running count. `start` was the first line.
- `cat <scratchpad>/actions.txt | tail -5` — once, to check my own action count.
- `ls review/qa/klee-round-10-2026-09-04` — once, to check the record directory
  existed. It printed nothing; I did not open any file in it.
- `mkdir -p review/qa/klee-round-10-2026-09-04` — once, after the `ls` printed
  nothing, to guarantee the record path existed before writing.
- `sed -n '…p'` and `head -N` / `tail -N` piped onto `observe` and `act` output, many
  times, to re-read one block of a screen I had already been shown. These filtered
  the tool's own output and read nothing else.
- `for c in …; do … done` shell loops, several times, to issue a planned sequence of
  `act` calls in one Bash call. Each loop iteration is one ordinary `act`.

Tools used: **Bash** (as above) and **Write** (once, for this file). No Read, no Grep,
no Glob, no Agent, no other understudy subcommand — no `harness state`, `scenario`,
`staged_turn`, or `soak`.

Three refused commands, none consecutive, all logged above: two were my own shell
mis-quoting of apostrophes in card and relic names (`Sparks 'n' Splash`,
`Dolly's Mirror`) which the tool refused with the working forms listed back, and one
was `play "Strike (1)" on "Brute Raider"` after the Brute was already dead. No
`TOOL-BLOCKED` and no `REFUSED: …leak…` line appeared at any point.
