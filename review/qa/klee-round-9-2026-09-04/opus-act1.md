# Klee round 9 — blind TESTER seat, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, Klee round 9, run 1, act 1.
- **Lane:** 2. **Seed:** `Q2XRYTNKBDJ2`. **Character:** KLEEMOD-KLEE. **Ascension:** 1.
- **Act:** 1. **Boss the map named:** *The Kin* (fought and killed: Kin Priest 190 HP
  plus two Kin Followers 59/58 carrying `Minion 1 — Minions abandon combat without
  their leader`).
- **Actions accepted:** ~196 `act` calls (1 refusal, see below). Cap was 250.
- **Termination reason:** the stated stop condition, not a budget — the act-1 boss
  was killed, its reward screen was handled (100 Gold + Alice's Recipe), and the
  lane is now sitting on the act-2 map with `Ancient (path 1)` the only exit. Wall
  clock and action budget both had room left.
- **HP trajectory:** 62/62 start → 60 → 54 → 54 → 43 → 41 → 37 → 21 (fight 5) →
  41 (rest) → 61 (rest) → 33 (elite) → 32 (fight 7) → 52 (rest) → 39 → 23 → 23 →
  16 → 12. **Ended 12/69** (max HP went 62 → 69 on the Byrdonis Nest egg).
- **Gold at the end:** ~172.
- **Potions held:** Skill Potion (1 of 3 slots). Flex Potion and Speed Potion were
  both spent on the boss. Two more (Strength Potion, Cure All) were offered by
  Tiny Mailbox at the pre-boss rest and could not be claimed — the bridge printed
  *"Your potion slots are full: 3 of 3. A potion claimed now has nowhere to go, and
  the game says nothing when one is dropped — so this page will not claim it until
  a slot is free."* There was no printed way to drop a potion outside combat.
- **Relics at the end:** Pounding Surprise (starter), Silver Crucible (Neow),
  Bone Tea (now reads "the next 0 combats" — spent), Tiny Mailbox (elite reward).
- **Deck at the end (22):** Strike ×4, Defend ×4, Ka-pow!, Jumpy Dumpty,
  Fwoosh!+, Mine Toss, Ammo Scavenging+, Pop!+, Quick Fuse, Dig In,
  Perfect Timing, Big Badda Boom, Kaeya — Glacial Waltz,
  Kaeya — Cold-Blooded Strike, Alice's Recipe.

**Neow pick: Silver Crucible** ("The first 3 card rewards you see are Upgraded.
The first Treasure Chest you open is empty.") — I picked it because I had never
seen this kit and upgraded copies show me both halves of a card's text at once,
which is the cheapest way for a blind seat to learn what a card is *for*;
Kaleidoscope would have filled my deck with other characters' cards and muddied
exactly the read I was there to take, and Lava Rock pays out at the end of the act
rather than at the start when I needed the information.

---

## Fight 1 — Nibbit 44 HP (attack 12)

Opening hand: Defend ×2, Ka-pow! (0, Retain, Set off, 4), Jumpy Dumpty (1, Bomb 8,
rider "place a Mine 3 on ALL enemies"), Strike.

**Turn 1** — Jumpy Dumpty on Nibbit, then Defend, Defend (10 block vs the printed
12). *Rejected:* Ka-pow! immediately, cashing the fresh Bomb 8 for 8+4. Rejected
because the Bomb badge printed *"Each grows at the start of your turn"* and Ka-pow!
prints Retain, so holding the detonator costs nothing while the bomb gains 4 a turn.
This is the decision the kit is actually built around and it was legible on turn 1.
*Also rejected:* Strike + one Defend — 6 damage for 5 block taken looked like a wash
against a 44-HP body.

**Turn 2** — Bomb had grown 8 → 12 exactly as printed. Ka-pow! (12 bomb + 4 = 16),
then Strike ×3. Nibbit 44 → 10. *Rejected:* holding another turn for Bomb 16.
Rejected because the intent line had changed to `Aggressive (Attack) 6` **and also**
`Defensive (Defend)` — banking damage into a shield is worse than spending it now.
The two-line intent print made that decision readable, which I want to record as a
positive.

**Turn 3** — Nibbit at 7 behind Block 5. Jumpy Dumpty (Bomb 8) → Ka-pow! (8 through
block, then 4). Dead. *Rejected:* Ka-pow! + Strike for 10, which would have left it
alive at 2 behind a shield for one more Empower turn.

Ended 54/62. **Reward:** took Fwoosh!+ (1 Spark, Set off, 9) over Chain Fuse+,
Sorry Jean...+ and Barbara+ — a second detonator that costs no Energy, when my only
one was a 4-damage card.

Screen note: the card-reward screen printed *"Its 1 Spark is a price, not an Energy
cost: an effect that makes a card free to play, or cuts its cost to 0, covers Energy
only, and the 1 Spark is still spent."* That is a clear, useful line and I never had
to guess about it again.

---

## Fight 2 — Shrinker Beetle 39 HP

**Turn 1** — the intent was `Strategic (DebuffStrong)`, no attack number, so every
Defend in hand was dead weight. Jumpy Dumpty (Bomb 8) + Strike ×2. *Rejected:*
Defends — the printed intent said no damage was coming, so blocking was throwing a
card away.

**Turn 2** — I now had `Shrink -1 (debuff) — While Shrinker Beetle is alive, your
Attacks deal 30% less damage`, and the hand redrew itself in front of me: Strike
printed **4** instead of 6, Fwoosh!+ printed **6** instead of 9. The Bomb badge still
read 12. Fwoosh!+ (Spark) then Mine Toss, then Strike ×2.

**The single most useful thing I learned in the run happened here.** 27 → 9 is 18
damage: 12 from the bomb *unreduced* plus 6 from the shrunk Fwoosh. The Bomb
keyword's *"Its hit takes the enemy's debuffs, not yours"* is not decoration — it
means the bomb payload is immune to your own attack debuffs, and the recalculated
card text next to the un-recalculated bomb badge showed me that without a word of
explanation. That is very good screen design.

**Turn 2 end** — I played Strike ×2 leaving it at 1 HP and ended turn expecting the
two Mines (3 + 4 = 7, printed as `Bombs here: 2, including 2 Mines`) to finish it
before its hit landed. They did: the fight ended with my HP untouched at 54.
*Rejected:* holding a Defend — the mines were arithmetic, not a gamble.

**Reward:** Ammo Scavenging+ (Bomb 7, draw 1 per bomb that went off this turn) over
Dig In+, Razor+ and Sorry Jean...+ — I had two detonators and one payload card.

---

## Fight 3 — Twig Slime (S) 11, Leaf Slime (M) 32, Leaf Slime (S) 15

**Turn 1 — no decision, and that is the finding.** The hand was Strike, Strike,
Defend, Defend, Defend: five base cards, no kit card. Two Strikes exactly killed the
only attacker (11 HP), and the third energy went on a Defend that could not matter.
I rejected nothing because there was nothing to reject. This happened again on
fight 4's last turn and fight 7's opening, and it is the clearest cost of an
eight-card Strike/Defend tax sitting on top of a deck whose whole identity is in the
other cards.

**Turn 2 — the best turn of the act's first half.** Jumpy Dumpty and Ammo Scavenging+
both onto Leaf Slime (M), then Mine Toss (Mine 4 on ALL). I ended the turn with
nothing blocked and took 11 on purpose. *Rejected:* swapping Mine Toss for a Defend.
Rejected because the mines pay twice — the badge says a Mine *"also goes off when
this enemy attacks you, before the hit lands,"* so each mine is 4 damage on their
turn plus a Spark from Pounding Surprise, where a Defend was 5 block once. That
trade (block now vs. free damage on their turn) is a real, repeatable decision and
it is the one I enjoyed most.

**Turn 3** — the badge read `Bomb 23` on Leaf Slime (M), exactly the 8 + 7 placed
plus 4 growth each. Fwoosh!+ (23 + 9 = 32) killed it, Ka-pow! + Strike killed the
small one. Took 0 damage that round.

**One thing I could not account for.** After Fwoosh!+ set off Leaf Slime (M)'s two
bombs, Leaf Slime (S) showed `Bomb 6 — Bombs here: 2, including 2 Mines`. Jumpy
Dumpty prints one rider — *"When it goes off, place a Mine 3 on ALL enemies"* — and
only one Jumpy Dumpty bomb went off, so I expected one Mine 3 and saw two. Its own
earlier Mine 4 from Mine Toss had already fired on its attack the turn before. I do
not know whether the rider fires once per bomb in the pile or whether I mis-tracked
a mine; the screen gave me no way to tell, because the badge aggregates ("Bombs
here: 2") and never lists them individually.

**Reward:** Pop!+ (0 energy, Bomb 7) — free payload is worth more than a fourth
detonator.

---

## Fight 4 — Inklet (1) 11, Inklet (2) 16, both `Slippery 1 — The next time Inklet loses HP, it only loses 1 HP instead`

**Turn 1 — the sharpest decision in the act.** Mine Toss + Defend + Defend, no
attacks at all. *Rejected:* Strike ×2. Rejected because Slippery converts *any* hit,
6 damage or 60, into 1 HP lost, so spending a real card to strip it wastes it; the
mines strip both Slipperies for free on the enemies' own turn, before their hits
land, and I keep the block. It worked exactly as printed and I took 0 from the
printed 9 of incoming.

**Screen and outcome disagreed here**, mildly: I had Block 10 against printed intents
of 3 and 2×3 = 9, and still lost 2 HP. The next screen explained it — a third Inklet
(11/12) had appeared. The bridge never printed a spawn intent, so the 2 HP looked
like a rules violation until the new body showed up in the list.

**Turn 2** — Jumpy Dumpty onto the 15-HP Inklet, Ka-pow! detonating it immediately
(15 → 7, rider spread Mine 3 across all three), Fwoosh!+ to kill the 11-HP one via
its fresh Mine 3 (3 + 9 = 12), then two Defends. *Rejected:* banking the bomb a
turn. Rejected because the Inklets multiply, so board tempo beats +4 growth, and
Jumpy Dumpty's rider is the only AoE in my deck — it has to be spent to be useful.
Took 0 damage that round.

**Turn 3** — one Inklet at 7, two Strikes, done. No decision.

I ended this fight on **Spark 7** with nothing in the deck that spends Spark except
Fwoosh!+ and Quick Fuse. This was the first sighting of a pattern that never went
away.

**Reward:** Quick Fuse (1 Spark: each bomb grows by 3, then Set off).

---

## Fight 5 — Snapping Jaxfruit 31, Flyconid 48

**Turn 1** — Ammo Scavenging+ put Bomb 7 on the Flyconid (the 48-HP body worth
banking on), Fwoosh!+ went on the *other* enemy for a clean 9, then Strike ×2 on the
Jaxfruit. *Rejected:* pointing Fwoosh!+ at the Flyconid, which would have set off my
own fresh bomb for 7 instead of letting it grow. Choosing which enemy to detonate is
a decision the "Set off" wording makes obvious once you have read it twice, and I
liked it.

**Turn 2 — the turn that taught me the engine.** Ka-pow! first, on the Flyconid,
purely to convert its Bomb 11 into damage **and one Spark**, because Quick Fuse was
sitting in hand printing `CANNOT BE PLAYED: you have no Spark, and this costs 1`.
Then Pop!+ (Bomb 7), Jumpy Dumpty (Bomb 8), then Quick Fuse — which grew both to 10
and 11 and set them off for 21 — then Strike. Flyconid 48 → 12, Jaxfruit 31 → 10,
both wearing a fresh Mine 3.

*Rejected:* the tidy-looking order of placing both bombs first and letting Ka-pow!
set off all 26 at once. I worked it out on the screen and it comes to the same 36
total, but it leaves both enemies *without* a Mine, because Jumpy Dumpty's rider
places the mines *after* the detonation it rides on. Detonating in two beats — the
old bomb with Ka-pow!, the new pair with Quick Fuse — keeps the mines on the board.
That is a genuinely good bit of design: the sequencing, not the card choice, is where
the value is.

**The chicken-and-egg I want on the record:** Spark is generated almost entirely by
bombs going off, and two of my three detonators cost Spark. On a turn where I have no
Spark and no bomb, Fwoosh!+ and Quick Fuse are both bricks and only Ka-pow! can start
the engine. Ka-pow! Retains, which is presumably why, but it means one particular
card is load-bearing in a way nothing on screen tells you.

**Turn 3** — Strike put the Jaxfruit to 1, Mine Toss put a Mine 4 on it, Defend for
the rest. Its own mine killed it before its hit landed and I took 0. *Rejected:*
killing the 3-HP Flyconid first — the Jaxfruit was the one attacking, with `Strength
4` and climbing.

**Turn 4** — Quick Fuse alone finished the Flyconid.

Ended 21/69. **Reward:** Kaeya — Glacial Waltz (6 Cryo at end of turn, 3 turns,
Exhaust). Taken deliberately as an instrument: every combat screen prints seven
Elemental Reaction keywords (Melt, Vaporize, Overloaded, Superconduct,
Electro-Charged, Frozen) and after five fights I had triggered **zero** of them,
because every card Klee owns is Pyro and a Pyro hit on a Pyro aura only refreshes it.
I wanted to know whether that table is reachable at all.

---

## Fight 6 — Elite: Bygone Effigy 127 HP

`Slow 0 (debuff) — Whenever you play a card, this enemy receives 10% more damage
from Attacks this turn.` Starting hand arrived upgraded off Bone Tea.

**Turn 1 (it printed `Sleeping — doing nothing this turn`)** — Perfect Timing+ went
**first**, before any bomb existed, so its "Set off" found nothing and it was simply
11 free damage; then Pop!+ (Bomb 7) and Jumpy Dumpty+ (Bomb 11). *Rejected:*
detonating for ~38 on a free turn — with nothing incoming, a banked turn is pure
profit. *Rejected:* blocking, for the same reason.

**Turn 2 (it printed `Empower` — a second free turn)** — I dumped the hand in
ascending damage order to milk Slow: Defend, Defend (worthless as block, played only
to add Slow stacks), Strike, then Quick Fuse (grew both bombs +3 to 32 and set them
off), then Ka-pow! on the Mine 4 the rider had just placed. *Rejected:* banking a
third turn — Quick Fuse and the whole Slow stack both evaporate at end of turn and
only Ka-pow! Retains, so "waiting" means discarding the payoff.

**This is where the screen and the outcome disagreed, and it is my strongest
finding.** The badge ended the turn reading `Slow 50 ... (Receives 50% more damage)`.
Its HP went 116 → 68, i.e. **48**. The printed parts sum to 46 before any bonus
(Strike 6, two bombs grown to 32, Ka-pow!'s Mine 4 and its own 4). The only
arithmetic that lands exactly on 48 is: **Slow multiplies my card attacks and does
not touch bomb Set-off damage at all** — Strike 6×1.2 = 7, bombs 32 flat, Mine 4
flat, Ka-pow!'s own 4×1.4 = 5. The last turn of the fight confirms it independently:
Slow 40, base 6 + 10 + 4 = 20, actual **21** (Strike 6×1.1 = 6, bomb 10 flat,
Ka-pow! 4×1.3 = 5).

If that reading is right it contradicts the Bomb keyword printed on the same screen —
*"Its hit takes the enemy's debuffs, not yours"* — because Slow **is** the enemy's
debuff, and I had already watched the same rule work in my favour in fight 2, where
my own Shrink correctly failed to shrink the bomb. So one printed sentence told me
bombs take the enemy's debuffs, one printed badge told me the enemy was taking 50%
more, and the number that came out said the bomb took neither. I could not tell from
the screen whether I had found a defect or misread a rule, and I could not check.

**Turn 3** — it woke up at `Strength 10`, attacking for 23. Ammo Scavenging+ for
payload, Kaeya — Glacial Waltz, Defend. *Rejected:* Mine Toss — I wanted block
against a 23, and Kaeya's Cryo mattered more (below).

**Melt does work, and the reaction table is reachable.** Kaeya's end-of-turn 6 Cryo
landed on the Pyro aura my own bombs had left and dealt **10** — 6 × 1.75, exactly as
the Melt keyword prints. The important consequence, which the Elemental Reaction
blurb does spell out but which took me a fight to believe, is that *the reacting hit
leaves no aura behind*: the enemy came out bare, so I could not turn round and Melt
it again with Pyro. The reaction is a one-shot per application, and to get the
1.75× on my own bombs I need a Cryo aura *standing* when I detonate — i.e. a Cryo
source that is not the same beat as the Pyro.

**Turn 4** — Fwoosh!+ set off Bomb 11 (20 damage) and re-applied Pyro, then Kaeya's
tick Melted it for another 10, plus Defend+ and Defend for 13 block against the 23.
*Rejected:* holding for a bigger bank — at 43 HP against a 23-a-turn body the bank
is not free any more.

**Turn 5** — 22 HP left on it, 23 incoming on me, 33 HP in hand. Ammo Scavenging+
(Bomb 7), Strike, Quick Fuse (grew it to 10, set off), Ka-pow!, Defend. It ended my
turn on 1 HP and Kaeya's last Cryo tick killed it. *Rejected:* any line that left it
alive, obviously.

Ended 33/69. **Rewards:** 42 Gold, Flex Potion, **Tiny Mailbox**, and I took
**Big Badda Boom** (2, Set off, deal 12, then deal damage equal to what the Bombs
dealt) over Rapid Fire, a second Mine Toss and Dahlia. It is the only card in the
pool that pays for the whole banking plan, and it says so in one line.

---

## Fight 7 — Nibbit (1) 44, Nibbit (2) 46

**Turn 1** — Jumpy Dumpty onto Nibbit (2) (Nibbit (1) had printed a `Defensive
(Defend)` intent and I did not want a bomb detonating into a shield), Kaeya —
Glacial Waltz, Defend. *Rejected:* firing Big Badda Boom straight away for
8 + 12 + 8 = 28. Rejected because BBB doubles the bomb number, so it wants the
biggest bank I can assemble, and neither Nibbit had yet printed a threatening
number. **This is the trap in the plan and I walked into it later:** Big Badda Boom
does *not* Retain, so "saving" it means shuffling it back into a 20-card deck. The
card's whole design points at banking and its own discard rule punishes banking.

**Turn 2 — the kit at its best.** Kaeya's tick had left `Cryo Aura 1` standing on
Nibbit (2), and the hand printed a line I had not seen before:
*`Reaction preview: Melt` — Pyro meets Cryo: this hit deals 1.75x damage and
consumes the aura*, sitting inside Ka-pow!'s own card text. That is an excellent
piece of screen design — it told me the multiplier was live without my having to
cross-reference the keyword table. Pop!+ (Bomb 7, total 19), then Ka-pow!:
40 → 8, i.e. 32 damage. The arithmetic is 12×1.75 = 21 for the first bomb, 7 flat
for the second, 4 for Ka-pow! — so **"one at a time" in the Set off keyword is
load-bearing: only the first bomb in the pile gets the reaction.** That caps what
Melt is worth and it is worth knowing; a bank of one fat bomb is much better with
Melt than a bank of three thin ones.

*Rejected:* banking again. The Cryo aura printed `1 more turn`, so the multiplier
was expiring; taking it now was worth more than +8 of growth.

**Turn 3** — Nibbit at 43 with `Bomb 14 (2 Mines)` and `Cryo Aura 1`. Quick Fuse
grew both mines to 10 and set them off: first one Melted for 17, second flat 10,
= 27. Then Perfect Timing, whose rider reads *"If a Bomb triggered an Elemental
Reaction this turn, play this again"* — and it did, twice, for exactly the 16 left.
*Rejected:* holding the mines to grow — the Cryo aura expired this turn and Perfect
Timing's double-play needed a bomb-triggered reaction in the same turn. Three cards
had to line up in one turn and I could see all three conditions on the screen. Best
turn of the run.

Ended 32/69 having taken 1 damage across the whole fight. **Reward:** Kaeya —
Cold-Blooded Strike (8 damage, apply Cryo) — a repeatable Melt enabler, since
Glacial Waltz Exhausts.

---

## Fight 8 — Boss: Kin Priest 190, Kin Follower (1) 59, Kin Follower (2) 58

The Followers printed `Minion 1 — Minions abandon combat without their leader`,
which made the whole fight a single-target race on a 190-HP body. I never attacked a
Follower.

**Turn 1** — Perfect Timing (8, applies Pyro), then Kaeya — Cold-Blooded Strike,
whose Cryo Melted that fresh Pyro aura for 14, then Jumpy Dumpty (Bomb 8).
190 → 168. *Rejected:* playing Kaeya last to leave a Cryo aura standing for next
turn's detonation. I chose the 22 now over the ~+9 later and I still think that was
right on a body this size, but it is exactly the tension the reaction system
creates: the aura you want for the payoff is the one your setup card consumes.

**Turn 2 — no decision, and it hurt.** Hand: Kaeya — Glacial Waltz, Defend, Defend,
Strike, Strike, under `Frail` so each Defend printed 3. Strike ×2 into the Priest and
one Defend. *Rejected:* Glacial Waltz — 6 Cryo a turn to a **random** enemy among
three, two of whom leave when the leader dies, is 2 expected damage a turn on the
only target that counts. A random-target card is close to unplayable in a
leader-plus-minions fight and nothing warns you at pick time.

**Turn 3** — 23 HP, 17 incoming, `Weak` on me. Dig In (8 block for 1 Spark and no
Energy) + Defend + Defend = 18 block, took 0. **Held the bank** rather than firing
Quick Fuse for 19. *Rejected:* Quick Fuse. 19 damage off 156 changes nothing;
the only line that wins is one enormous detonation, so the bomb keeps growing while
I block. Dig In is the card that made turtling possible — Spark-priced block is
exactly the right sink for a resource I was otherwise wasting.

**Turn 4 — the payoff, and it is spectacular.** Big Badda Boom finally arrived with
the Priest carrying Bomb 20. Flex Potion (5 Strength), Pop!+ (→27), Ammo
Scavenging+ (→34), then Big Badda Boom: **156 → 66, ninety damage from one card
sequence.** Then Ka-pow! on the Mine 3 the rider had left. *Rejected:* holding BBB
one more turn for a bank of ~46 — impossible, because it discards.

**Turn 5** — 16 HP, 27 incoming. Speed Potion (5 Dexterity) turned Dig In into 13
and Defend into 10 for 23 block; Perfect Timing put 8 on the Priest before Jumpy
Dumpty re-seeded a Bomb 8. *Rejected:* Mine Toss — two of its three mines land on
minions that will walk away.

**Turn 6 — lethal.** 12 HP against 22 incoming and `Frail` capping my only Defend at
3; there was no surviving line, only a killing one. Bomb 12 + Pop!+ (Bomb 7) = 19,
Strike for 6, then Big Badda Boom: 19 + 12 + 19 = 50 into 40. **The Kin died and the
two Followers abandoned the fight.**

Ended **12/69**. Rewards: 100 Gold, and I took **Alice's Recipe** ("Your Bombs grow
twice each turn") over Sugar Rush, Chained Reactions and Mona.

---

## The kit, after 8 fights

### (a) Which decisions felt like real choices, and what they traded off

Four kinds, and they are all good ones.

1. **Bank or cash.** Every turn with a bomb on the board and a detonator in hand is
   a real question, because the bomb grows 4 a turn for free and Ka-pow! Retains, so
   waiting is genuinely free — *until* the enemy's intent line changes. The two
   things that ended a bank for me were an enemy printing `Defensive (Defend)` and
   an enemy printing a number I could not survive. Both are legible on screen a turn
   in advance. This is the kit's spine and it works.
2. **Which body to point the detonator at.** Because Set off is targeted, Fwoosh!+
   pointed at enemy B is 9 clean damage that leaves my bank on enemy A intact. I made
   this call in fights 3, 4 and 5 and it mattered each time.
3. **Sequencing within a turn.** Fight 5's Ka-pow!-then-Quick-Fuse ordering, and
   fight 6's Perfect-Timing-before-any-bomb-exists, both produced more than the
   obvious order for the same cards. Jumpy Dumpty's rider firing *after* the
   detonation it rides on is the hinge; so is Perfect Timing's Set-off finding
   nothing when you play it first. Turn ordering carrying that much weight is rare
   and it is the most enjoyable thing here.
4. **Mines as pre-emptive removal.** Fight 4's Slippery is the showcase — the mines
   strip a "next hit only loses 1 HP" buff for free on the enemy's own turn, so you
   never spend a real card on it. Mine Toss vs. Defend is a live trade (free damage
   plus a Spark on their turn, versus block now) that came up repeatedly.

### (b) What felt automatic, and what never seemed worth playing

**Automatic:** every turn where the hand was all Strikes and Defends. That was
fight 3 turn 1, fight 4 turn 3, fight 7 turn 1 and boss turn 2 — four of about
twenty-four turns with literally no alternative to reject. Eight base cards in a
sixteen-card deck is a lot of turns where Klee is not playing Klee.

**Never worth playing:** Kaeya — Glacial Waltz's random targeting made it a
non-card in any multi-enemy fight, which is most of them. Defend became close to
worthless whenever `Frail` was on me (3 block a card), and Block generally was the
wrong side of the trade against enemies whose intents were Debuff or Empower — the
kit rewards reading the intent line and simply not blocking.

**Almost never worth playing, for a different reason:** Quick Fuse and Fwoosh!+ on
any turn where no bomb had yet gone off, because both cost Spark and Spark comes
almost entirely from bombs going off. I opened fight 5 turn 2 with `CANNOT BE
PLAYED: you have no Spark` on Quick Fuse. And the mirror problem: I ended fights on
Spark 7, 5 and 7 with nothing to spend it on. Spark is simultaneously scarce at the
start of a fight and worthless at the end. Dig In (Spark-priced block, no Energy) was
the single best fix and I only had it because I bought it.

### (c) What I could not understand, or that seemed to contradict its own printed text

1. **Slow vs. the Bomb keyword.** The elite printed `Slow ... (Receives 50% more
   damage)` while the Bomb keyword printed *"Its hit takes the enemy's debuffs, not
   yours."* My arithmetic on two separate turns says the bomb payload got no share of
   Slow at all, only my ordinary card attacks did — 48 actual vs 46 base at Slow 50,
   and 21 actual vs 20 base at Slow 40. In fight 2 the same keyword *did* correctly
   protect the bomb from my own Shrink. Those two behaviours cannot both be what the
   sentence means. Either the sentence needs to say "ignores your debuffs" rather
   than "takes the enemy's," or Slow is not reaching the bomb when it should.
2. **Jumpy Dumpty's rider count.** After one Jumpy Dumpty bomb went off in fight 3,
   a bystander showed `Bombs here: 2, including 2 Mines` totalling 6, where the
   printed rider ("place a Mine 3 on ALL enemies") predicts one Mine 3. The badge
   aggregates and never itemises, so I could not audit it.
3. **`This turn, Grounded counts nothing as having gone off`** on Kaeya —
   Cold-Blooded Strike, and the resulting `Cold Blooded 1` buff. Grounded is a card I
   have never owned; there is no keyword tooltip for it on the card; and a buff row
   in my own status bar referred to it. Text about a card I do not have, with no
   explanation of what it does, is noise on the one screen I read every turn.
4. **A Spark I cannot source.** Boss turn 1 went Spark 1 → 3 with no bomb going off
   (Perfect Timing set off an empty enemy). Pounding Surprise pays on bombs only. I
   never worked out where those two came from.
5. **Inklet spawning.** I lost 2 HP through 10 block against 9 printed damage; the
   explanation (a third Inklet had appeared) was only visible on the next screen.
   Nothing in the intent lines forecast a spawn.
6. Minor: potions offered when all three slots are full simply cannot be taken and
   there is no printed way to drop one outside combat, so Tiny Mailbox's payout was
   silently wasted at the rest site.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted:** Kaeya — Glacial Waltz. Random target across three bodies in a
fight where only one of them counts, and it Exhausts, so the miss is permanent. (Of
Klee's own cards, Mine Toss in a leader-and-minions fight is the same complaint in
smaller form — "on ALL enemies" is a downside when two of them are going to walk
away.)

**Happiest to draw: Big Badda Boom.** Ninety damage on boss turn 4 and the exact 50
that killed The Kin two turns later. It is the card that makes the banking loop mean
something, and its text — "then deal damage equal to what the Bombs dealt" — is four
words that tell you the whole plan. My one complaint is that it does not Retain, so
the card that most wants you to bank is the one you cannot hold while you do it.

Honourable mention to **Ka-pow!**: 0 energy, Retain, and it is the only detonator
that works when you have no Spark. I drew it in nearly every fight and it was never
a dead card.

### (e) Did the first turn of the first fight already present a decision?

**Yes, and a good one.** The opener was Jumpy Dumpty (Bomb 8), Ka-pow! (0 cost,
Retain, Set off, 4), two Defends and a Strike against a body printing 12 damage. The
question — cash the fresh Bomb 8 now for 12 total, or place it and hold the free
retaining detonator while it grows 4 a turn — is the kit's central question, it is
answerable purely from text printed on that screen (the Bomb badge says it grows at
the start of your turn; Ka-pow! says Retain), and getting it right mattered. I have
no complaint about the opening turn at all.

---

## Non-blindness declaration

**Repo files read: none.**

Every game action was one of the two allowed commands, `python -m
understudy.blindplay observe` and `python -m understudy.blindplay act "<command>"`,
each run through the Bash tool with the `GITS_LANE=2` prefix. I ran no other
understudy subcommand — no `harness state`, no `scenario`, no `staged_turn`, no
`soak`.

Other tool use, in full:

- **Bash**, beyond the two allowed commands: one `mkdir -p` for the scratch
  directory under the session scratchpad, and one `mkdir -p` for the record
  directory `review/qa/klee-round-9-2026-09-04/`.
- **Bash**, shaping the allowed commands' own output only: `&&` chaining of several
  `act` calls in one invocation; redirecting `act` output to `/dev/null` when I only
  wanted the `observe` that followed; `| tail -2` and `| sed -n '...p'` and one
  `| grep -E '^- \*\*'` to re-read a portion of an `observe` I had already been
  shown. None of these read anything the bridge had not printed to me.
- **Write**, once, for this file.

I wrote no scratch notes file in the end; all tracking was done in-context.

One refused command, per the brief: `act 'rest'` at the pre-boss rest site returned
`error Rest site room is not open` on the first attempt, immediately after the `go`
that entered the room. The `observe` right after it showed the rest screen fully
open with Rest and Smith available, and the identical command succeeded on the
retry. It reads as a race between the room opening and the command landing rather
than a rules refusal. That was the only refusal in ~196 accepted actions, and there
were no stalls.
