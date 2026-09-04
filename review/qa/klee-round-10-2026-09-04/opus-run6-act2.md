# Blind seat record — KLEEMOD-KLEE, lane 2, act 2 (run 6, chained seat)

## Identity

- **Model / seat:** Opus (Claude Fable 5.1), blind TESTER seat, lane 2.
- **Run seed:** not printed by the bridge on any screen I saw; I have no seed to report.
- **Character:** Klee (Pyro / Bomb kit). **Act:** 2. **Boss named at the top of the act
  map:** *The Insatiable*.
- **Neow pick:** none, inherited. I picked up the lane on the act-2 map with the
  previous seat's deck, relics and potions and made no Neow choice.
- **Actions accepted:** 172 `act` calls (cap was 250).
- **Termination reason:** not a budget. **The run ended — I died.** On my last turn
  `end turn` returned `TOOL-BLOCKED: game_over` / "the run is over; there is nothing
  left to play. The run ended on floor 33." I was killed by the act-2 boss's
  **Sandpit** timer ("When The Insatiable takes its turn, you will be eaten and die"),
  not by damage — I was at 30/72 HP with 19 Block when it fired.
  **The lane is therefore NOT on the act-3 map.**
- **HP trajectory:** 62/62 (start of my first fight, already healed by the previous
  seat) → 45 → 35 → 32 → **2** (after the Entomancer elite) → 23 (rest) → 44 (rest)
  → 69/72 (Spirit Grafter heal; max HP had gone 62 → 72 at the Stone of All Time)
  → 53 → 30 → dead on floor 33.
- **Gold at the end:** 18.
- **Potions held at the end:** 1 — Dexterity Potion (unused; I never found a turn
  where +2 Dexterity beat the block already in hand). Spent during the act: Poison
  Potion (killed the Burrowed Tunneler through 32 Block), Colorless Potion (took
  Prowess), Radiant Tincture (boss turn 3). Heart of Iron was traded away at an event.
- **Relics at the end:** Pounding Surprise (Bomb goes off → 1 Spark), Silver Crucible,
  Empty Cage, Twisted Funnel (4 Poison to ALL at combat start), Candelabra (+2 Energy
  at the start of your 2nd turn).
- **Deck at the end** (as last printed to me, ~27 cards): Strike ×1, Defend ×4,
  Ka-pow!, Jumpy Dumpty+, Mine Toss+, Dodoco Cover+, Ammo Scavenging, Quick Fuse+,
  Fwoosh!, Sizzle ×2, Big Badda Boom+ ×2 (one upgraded at the Smith), Sparks 'n'
  Splash, Alice's Recipe, Dig In ×3, Diona — Signature Mix, Sorry Jean..., Careful Now,
  Grounded, Safety Lesson+, Metamorphosis, plus the 6 **Frantic Escape** statuses the
  boss inserted.

Route taken: Ancient shrine (Empty Cage, removed 2 Strikes) → Monster (Bowlbugs) →
Shop → Monster (Tunneler) → Shop → Stone of All Time → Monster (The Obscura) →
Elite (Entomancer) → Treasure (Candelabra) → RestSite (rest) → Shop → RestSite (rest)
→ Spirit Grafter → Potion Courier → RestSite (Smith) → Boss.

---

## Fight 1 — Bowlbug (Rock) 47/47, Bowlbug (Nectar) 36/36

**Turn 1.** Played Diona — Signature Mix → Jumpy Dumpty+ on Rock → Dig In → Defend.
The screen decided this: Rock printed `Imbalanced 1 — If Bowlbug (Rock)'s attacks are
fully blocked, it becomes Stunned`, and its intent said 15. Diona's 2 Weak took the
pair from 15+3 to 11+2 = 13, and Dig In (8) + Defend (5) = exactly 13 Block.
**Rejected:** blocking without Diona (13 Block against 18 raw leaks 5 and misses the
Stun); leading with Ka-pow! (not in hand). This was the fight's best turn — the
Imbalanced clause turns "how much block" into "exactly how much block", which is a
decision with a right answer you can compute off the printed numbers.

**Turn 2.** Rock **Stunned**, Nectar on Empower. Zero incoming. I played nothing and
retained Ka-pow!, letting Bomb 11 → 15. **Rejected:** popping the bomb with Ka-pow!
for 19 (block gained on a turn with no attack is wasted, and the Spark it would have
banked is the only thing carried forward — so the +4 of one turn's growth was free).
A turn with no decision except "don't", which is still a decision.

**Turn 3.** Nectar had come off Empower with **Strength 15** — its 3 became 18. Played
Dodoco Cover+ on Rock (Bomb 6 onto the pile) → Ka-pow! on Rock → Mine Toss+ → Defend.
Ordering Dodoco *before* Ka-pow! was the whole turn: Set off reads "Every Bomb on the
target goes off", so the 6 joined the 19 and the pile hit for 19+6+4 = 29 (47 → 18,
exactly as printed) and paid 2 Sparks instead of 1. **Rejected:** Ammo Scavenging over
Defend — it would have drawn 2, but I had counted the draw pile down to exactly
{Strike, Big Badda Boom+, Sparks 'n' Splash, Alice's Recipe} and had no energy left to
play what it found.

**Turn 4.** Rock Stunned *again* — my 16 Block had eaten its 15 exactly. Played Big
Badda Boom+ on Nectar → Strike on Nectar → Dig In. **Rejected:** killing Rock (7 HP)
first; Nectar at 25 with permanent Strength 15 was the clock, Rock was Stunned and idle.

**Turn 5.** Ka-pow! killed Nectar (3 HP), then Mine Toss+ → Quick Fuse+ on Rock: Mine 7
grown by 6 = 13 into a 7-HP Rock. **Rejected:** Strike on Rock (6 into 7 HP leaves 1).
Quick Fuse+ costs a Spark and no Energy, which is what made a two-kill turn fit.

*Reward:* took Sizzle over Careful Now / Fish-Flavored Bait / Kaeya, because the fight
had shown me the deck's real bottleneck — bombs everywhere, almost nothing to set them
off, and the Spark cards deadlocked (see (c)).

## Fight 2 — Tunneler 87/87

**Turn 1.** Mine Toss+ → Dodoco Cover+ → Dig In. 15 Block against a printed 13,
fully blocked. **Rejected:** nothing, really — the hand was Mine Toss+, Dodoco Cover+
and *three* Dig Ins against 1 Spark. This turn presented no choice; it presented a
resource jam.

**Turn 2.** It was on Empower+Defend, so nothing incoming. Jumpy Dumpty+ (Bomb 11 onto
the standing Bomb 10 = 21) → Big Badda Boom+ → Fwoosh!. BBB+ printed 58 damage
(21 + 16 + 21) and the screen showed 80 → 22, i.e. exactly what the card said. Fwoosh!
then set off the Mine 4 that Jumpy Dumpty had spawned: 22 → 12. **Rejected:** banking
another turn for a bigger pile — it was already Defending next turn and I wanted the
damage in before Block landed.

**Turn 3.** Here the fight turned: Tunneler came back with **Block 32** and
`Burrowed 1 — Block is not removed at the start of Tunneler's turn. Stunned if all
Block is removed`, on 12 HP. My hand had no attack at all. I used the **Poison Potion**
(6 Poison), then Diona + Defend + Defend for 10 Block. Poison ignored the 32 Block and
did the whole job. **Rejected:** chipping the Block toward the Stun — 10 damage a turn
against 32 persistent Block is not a plan.

**Turns 4–5.** Defend, Defend, Sizzle (chip); then one Defend while Poison finished it
at 1 HP. **Rejected on turn 5:** Big Badda Boom+ + Sizzle + Ka-pow! = exactly 26 into
exactly 26 Block — it would have Stunned it and dealt 0 to HP, which is a fun piece of
arithmetic and a bad play.

*Reward:* took the second Big Badda Boom.

## Fight 3 — The Obscura 123/123 (+ Parafright 21/21, summoned)

**Turn 1.** It printed Summon, so nothing was coming. Alice's Recipe → Jumpy Dumpty+.
**Rejected:** any attack. A free first turn is where Alice's Recipe (bombs grow twice)
pays, and it did: Bomb 11 → 19 rather than 15.

**Turn 2.** Parafright printed `Illusion 1 — When this dies, it revives next turn at
full HP` and `Minion 1 — Minions abandon combat without their leader`, which read
together as "do not spend a card on this thing". Diona → Mine Toss+ → Defend → Dig In,
13 Block against a weakened 12. **Rejected:** killing the 21-HP Parafright (Illusion
makes it free for them, expensive for me).

**Turn 3.** Sparks 'n' Splash → Defend → Dig In. **Rejected:** Quick Fuse+ for an
immediate 54. I kept the pile because Sparks 'n' Splash reads "deal Pyro damage equal
to its largest Bomb" and, as I found out, **does not consume the bomb** — 27 damage
that turn with the 27 still standing. That is the single best interaction I found in
the kit.

**Turn 4.** Obscura at 81 behind Block 6 with a Bomb 35 on it. Dodoco Cover+ first
(pile 35 → 41), then Big Badda Boom+ — 41 + 16 + 41, dead through the Block, and the
Minion clause ended the fight without my ever touching the Parafright.
**Rejected:** BBB+ alone, which I had computed at 86 against 81 HP + 6 Block = 87, one
short. Being able to do that arithmetic off the printed badge is the best thing about
this kit's screens.

## Fight 4 (Elite) — Entomancer 145/145

**Turn 1.** It printed 3×7 and `Personal Hive 1 — Whenever this enemy is hit by an
Attack, add 1 Dazed into your Draw Pile`. Bombs print "Not an Attack", so the whole
kit is supposed to walk past this — but my hand had **no block card at all**: Big
Badda Boom, Ka-pow!, Sizzle, Mine Toss+, Sparks 'n' Splash. Played Mine Toss+ and
Sparks 'n' Splash and ate 21 on the chin, 32 → 11. **Rejected:** dumping BBB+Sizzle+
Ka-pow! for 22 damage and 3 Dazed. There was no defensive alternative to reject; the
hand had none.

**Turn 2.** 18 incoming at 11 HP. Jumpy Dumpty+ (Bomb 11) → Careful Now (Block = largest
Bomb, 10) → **Sorry, Jean...** (remove that same bomb, Block 11) → Diona. 21 Block
against a weakened 13, zero taken. **Rejected:** keeping the bomb and taking 3 (HP 8).
I worked the next turn out first: 13 incoming − Diona's 4 = 9, which is more than 8 and
less than 11. Eating my own bomb for Block was the correct, and very strange-feeling,
play — Sorry, Jean... and Careful Now want the same bomb Big Badda Boom+ wants.

**Turn 3.** It Empowered; free turn. Ammo Scavenging only. **Rejected:** BBB+ for 24
(4 + 16 + 4 off a Bomb 4) — the payoff card is worth a fraction of itself on a small
pile, so holding is nearly always right, which is itself a finding about how narrow
the "when do I detonate" decision is.

**Turn 4.** It came off Empower at **Personal Hive 2, Strength 1, 4×7 = 28**. Dodoco
Cover+ → Defend → Defend → Dig In → Dig In: 37 Block against 28, zero taken. Note this
was possible only because Dig In costs a **Spark, not Energy** — three energy bought
17 Block and two Sparks bought 16 more. **Rejected:** nothing; every card in hand was
block and I played all of it.

**Turn 5.** 19 incoming, 11 HP, hand = Ka-pow! + 2 Defends + Alice's Recipe + Sizzle +
an unplayable Quick Fuse+ (0 Sparks). 10 Block, took 9 → **2 HP**. **Rejected:**
Sizzle setting off the Bomb 22 for 28 damage and 2 Sparks. I kept the pile
specifically because Sorry, Jean... and Careful Now turn a big bomb into Block, and at
2 HP a bomb is a block card. That call is what kept me alive.

**Turn 6.** It Empowered again — the free turn I needed. Jumpy Dumpty+ only (pile 30 →
41 across 3 bombs). **Rejected:** Ka-pow! for 34 and 2 Sparks; the pile was worth more
as the kill.

**Turn 7.** Drew both Big Badda Booms. Dodoco Cover+ (pile 53 → 59) then Big Badda
Boom+: 59 + 16 + 59 into 91 HP. Dead. **Rejected:** BBB+ alone (would also have killed;
the Dodoco top-up was insurance I could afford). Won the elite at **2 HP**.

## Fight 5 (Boss) — The Insatiable 321/321

**Turn 1.** Empower + `Strategic (StatusCard) — intends to give you 6 Status cards`.
Nothing incoming. Dodoco Cover+ → Mine Toss+ (2 bombs, 13). **Rejected:** Metamorphosis
(2 energy, 3 free Attacks into the *draw* pile) — bomb growth compounds and card
quality does not.

**Turn 2** (Candelabra gave 5 energy). The 6 status cards were **Frantic Escape** —
`Get farther away. Increase Sandpit by 1. Increase the cost of this card by 1` — and
the boss now printed `Sandpit 4 — In 4 turns, you will be eaten and die`. So the boss
is a **hard timer**, and the only lever on the timer is playing the junk it gives you,
at a cost that rises each time. Played Frantic Escape ×2 (Sandpit → 6) and Sparks 'n'
Splash. Took 16. **Rejected:** Quick Fuse+ for an immediate 33 — banking beats cashing
while Sparks 'n' Splash is chipping for free off the same pile.

**Turn 3.** Used Radiant Tincture (+1 energy now, +1 for three turns) → Alice's Recipe
→ Grounded → Defend. **Rejected:** Alice's + Grounded with no Defend (would have taken
28 at 53 HP). Grounded — `at the start of your turn, if none of your Bombs went off
last turn, gain 6 Block and 1 Spark` — is written for exactly the bank-the-pile plan I
was running, and it is the best 37 gold I spent all act.

**Turn 4.** Empower; free turn. Used the Colorless Potion, took **Prowess** (+1 Str,
+1 Dex) and played it free. **Rejected:** Stratagem (a tutor on reshuffle, and I only
had ~3 reshuffles left in the clock) and Automation. With 4 energy, no bomb placer in
hand and no incoming, there was **nothing else to spend the turn on** — I ended it with
4 unspent energy, which is the second time the kit handed me a live turn I could not
use.

**Turn 5.** Careful Now (11) + Defend (6) on top of Grounded's 6 = 23 against 20, zero
taken; banked the pile at 38. **Rejected:** Big Badda Boom+ for 77 right then. With
Sandpit at 3 I judged 77-now worse than a bigger pile later, and I still think that was
right — the losing move was earlier.

**Turn 6.** Sandpit 2, 221 HP, no escape card in hand. Diona → Jumpy Dumpty+ → Ammo
Scavenging → Safety Lesson+ → Dig In: pile to 53 across 3 bombs, 15 Block against a
weakened 15, zero taken. **Rejected:** detonating for 38+17+38 = 93 — it does not kill,
and it switches Grounded off.

**Turn 7 (last).** `Sandpit 1 — When The Insatiable takes its turn, you will be eaten
and die`, boss at 182, pile at 77, and **no Big Badda Boom in hand**. The only line
that could save the run was to dig for a Frantic Escape: Ka-pow! set off all three
bombs (82 damage, 182 → 100, +3 Sparks, +9 Block off Safety Lesson+), which made Ammo
Scavenging draw 3. It drew Sorry Jean, Sizzle, Dig In ×2, Metamorphosis — **no Frantic
Escape**. Sizzle + Strike took it to 78. **Rejected:** holding the pile for Sparks 'n'
Splash (4 damage — the pile's largest single bomb was only 46 before the set-off and 4
after), and Metamorphosis, which puts its free Attacks into the *draw pile* and so
cannot be cashed on the turn you die. Ended turn; `TOOL-BLOCKED: game_over`, floor 33.

The honest post-mortem: I bet the fight on banking one enormous pile for a Big Badda
Boom+ and the clock ran out with both copies in the discard. Nothing on the screen told
me the pile plan was slower than the timer — I had to work that out, and I worked it
out one turn too late.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The kit's live decision, and it is a good one, is **when to cash the pile**. Bombs grow
4 a turn (8 under Alice's Recipe), Big Badda Boom+ pays `pile + 16 + pile`, and Sparks
'n' Splash bills the largest bomb every turn *without consuming it* — so every turn you
choose between compounding and collecting, and the answer changes with the enemy's
remaining HP. Fight 3 turn 4 (Dodoco first so the pile cleared 87 rather than 86) and
elite turn 7 were both real, computable, satisfying decisions.

The second real choice is **the pile as a block bank**. Careful Now (block = largest
bomb, ≤10) and Sorry, Jean... (remove a bomb, block = its size) compete with Big Badda
Boom for the same object. At 11 HP against the Entomancer I ate my own Bomb 11 for 11
Block and lived; two turns later I refused to detonate a Bomb 22 for the same reason.
That tension — the resource is both my damage and my armour — is the best thing in the kit.

Third, **ordering within a turn** matters constantly and legibly: place before setting
off, Careful Now before Sorry Jean, Diona before counting block. Screens give you the
numbers to get it exactly right, and "exactly" pays (Imbalanced stunned the Bowlbug
twice off 13 and 16 block).

And **Sparks are a second, genuinely separate currency**. Dig In and Fwoosh! cost no
Energy at all, so a 3-energy turn can be a 5-card turn. Elite turn 4 (37 block off 3
energy and 2 sparks) only exists because of that.

**(b) What felt automatic, and what never seemed worth playing.**

Blocking turns are automatic: when the intent number is bigger than my HP the hand
plays itself, and about a third of my turns were that. Strike (7 damage) and Defend
were never decisions. **Metamorphosis** I never once cast usefully — its free Attacks
go to the *draw pile*, so it does nothing on the turn you need it and I drew it on the
turn I died. **Ammo Scavenging's** Bomb 4 is beneath the other placers and its draw
clause only fires on a turn you already detonated, i.e. a turn you have already spent.
**Alice's Recipe** and **Sparks 'n' Splash** are 2-cost powers that are excellent on a
free turn and unaffordable on any turn you have to block, which made them feel like
cards the fight had to gift me a window for.

Free turns were the odd one out: three separate times (fight 1 turn 2, boss turn 4,
elite turn 3) the enemy Empowered, I had energy and nothing whatsoever to spend it on,
and the correct play was to pass. The kit has no cheap way to convert a spare turn
into pile.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **The Spark deadlock.** Sparks come from bombs going off (Pounding Surprise); Quick
   Fuse+ and Fwoosh! *set off* bombs but cost Sparks. With 1 starting Spark I repeatedly
   held a hand of Dig In ×3 and Quick Fuse+ and could play one card. Fight 2 turn 1 was
   literally Mine Toss+, Dodoco Cover+ and three unplayable Dig Ins. Nothing on the
   screens warns that the currency's only source is behind a card that costs it.
2. **"Set off" vs. a Mine's own trigger.** The keyword says "Every Bomb on the target
   goes off". When the Tunneler attacked, only the Mine went off — the Dodoco Bomb 6
   was still standing (and had grown to 10) on the next screen. Both readings are
   defensible from the two glossary entries, but they disagree in tone and I had to
   learn the answer by losing a turn to it.
3. **The badge number is a sum; "largest Bomb" is not.** `Bomb 42 … Bombs here: 2` sets
   off for 42, but Sparks 'n' Splash paid 27 and the Mine popped for 15. Correct, and
   the badge does say "Bombs here: 2" — but the one number in bold is the one the other
   card doesn't use.
4. **Undefined words on cards offered for sale or reward,** with no keyword entry
   anywhere on the screen that printed them: **Hexerei** (Witches' Circle: "Whenever
   you play a Hexerei card"), **Swirl** (Sucrose — Wind Spirit Creation; also Prune's
   Hexhunter Chime), **Vigorous** (Stone of All Time: "Enchant an Attack with Vigorous
   8"), **Plating** (Heart of Iron: "Gain 7 Plating"), and **Oz** (Fischl — Nightrider:
   "If Oz is out"). I had to price five purchases blind on those words.
5. **Flame Dance** reads `Set off each enemy whose aura is not Pyro` — and every bomb
   this kit sets off *applies* Pyro. I skipped it twice because I could not tell whether
   it is anti-synergistic by design or by accident.
6. **Silver Crucible** ("The first 3 card rewards you see are Upgraded") never once
   produced an upgraded reward in my four card rewards. It may well have been spent in
   act 1 by the previous seat — I cannot tell, and the relic line does not say.
7. **Heart of Iron** was offered in the relic slot of a combat reward and the tool
   reported `Claiming reward: potion (Heart of Iron)`. It behaved as a potion.
8. **Sandpit.** The boss's timer is printed clearly and Frantic Escape's fix is printed
   clearly, but nothing tells you the exchange rate — how many turns of extension the
   six copies actually buy, or that the extension card gets more expensive per copy
   rather than per play. I bought two turns for 2 energy and then never drew another
   copy across five turns, which decided the run.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Metamorphosis** — 2 energy to improve a draw pile I did not live to
reach. (Strike is worse in the abstract, but it is at least honest.)

Happiest to draw: **Big Badda Boom+**. `Set off. Deal 16. Then deal damage equal to
what the Bombs dealt` turned a 59-pile into a 134-damage turn and killed the Entomancer
from 2 HP. Its problem is that it is the whole plan — the run ended with both copies in
the discard on the turn I needed one. **Grounded** is the honourable mention: 6 Block
and 1 Spark a turn for banking, which is the exact plan the rest of the kit wants.

**(e) Did the first turn of the first fight already present a decision?**

Yes, and a good one. Bowlbug (Rock) printed Imbalanced ("if its attacks are fully
blocked, it becomes Stunned") on a 15 intent next to a 3, and my hand had Diona (2 Weak
+ 4 Block/turn), Jumpy Dumpty+ (Bomb 11), two Dig Ins and a Defend against 3 energy and
1 Spark. Weak first turned 18 into 13 and made 13 Block reachable — turning "block as
much as I can" into "block *exactly* enough to stun the big one", while still spending
a card on the bomb the whole kit is built around. That is a real opening turn.

---

## Non-blindness declaration

Commands outside the two allowed ones, in full:

- `mkdir -p "<scratchpad>"` and `echo "<n>" > "<scratchpad>/actcount.txt"` — one
  scratch file in the session scratchpad holding my running count of accepted `act`
  calls, written repeatedly through the round and read back once at the start.
- `sed -n '<ranges>p'` piping some `observe` output, to re-read one block of a long
  screen. I never used it in a way that could hide the enemy list: every combat screen
  was read either in full or with the ranges chosen to include the whole
  `## The other side` section, and I re-read the head of each screen for HP/Energy/Spark.

Tools used: **Bash** (for every `observe`/`act` and the scratch commands above) and
**Write** (once, for this record).

I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no other
understudy subcommand.

**Repo files read: none.**
