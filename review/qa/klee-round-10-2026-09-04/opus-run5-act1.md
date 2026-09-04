# Klee round 10, run 5, act 1 — blind seat record

## Identity

- **Model / seat:** Claude Opus (Fable 5.1), blind TESTER seat, KLEEMOD-KLEE, lane 1.
- **Run seed:** not printed on any screen the bridge showed me; I cannot state it.
- **Character:** Klee (inferred only from the mod name I was given and from the
  Hexerei keyword text, which says "Klee is one too"; no screen named the
  character to me).
- **Act:** 1. Map header said **"At the top of this act: Vantom"** from the first
  map screen onward, so the boss was named in advance.
- **Actions accepted:** 204 accepted `act` calls (cap 250). One refusal, at the
  third rest site: `error Rest site room is not open` on `rest` immediately after
  arriving; the identical command a moment later was accepted.
- **Termination reason:** the stop condition, not a budget. The act-1 boss died,
  its reward screen was handled, and the lane is sitting on the act-2 map
  (`Ancient (path 1)` offered, boss floor 16 behind me). I did not enter act 2.
- **HP trajectory:** 62/62 → 60 → 56 → 43 → 40 → (event −8 max, Mango +14 max)
  54/68 → 45 → rest 70/73 → 39 → elite 25/73 → rest 51/78 → rest 79/83 →
  **39/83** after the boss.
- **Gold at the end:** 275. Note: after the Tea Master event no shop was
  reachable, so ~160 gold I had deliberately saved for one was stranded.
- **Potions held:** none. All three (Block, Skill, Poison) were spent — Block and
  Skill on the elite, Poison on the elite.
- **Deck at the end** (16 cards, as tracked from printed hands; the bridge never
  showed me a deck screen outside the two removal/selection overlays):
  3× Strike, 3× Defend, Ka-pow!, Jumpy Dumpty, Mine Toss, Sizzle,
  Fish-Flavored Bait, Dodoco Cover, Big Badda Boom, Fwoosh!, Dig In+ (upgraded),
  Sugar Rush+ (upgraded), Spore Mind (curse). Whether the 3 Wounds Vantom gave
  me persist past combat, no screen told me.
- **Relics at the end:** Pounding Surprise (start), Stone Humidifier (Neow),
  Mango, Amethyst Aubergine, Toxic Egg, Tea of Discourtesy, Vambrace.

**Neow pick: Stone Humidifier** ("Whenever you Rest at a Rest Site, raise your
Max HP by 5"). I took it over Lava Rock because Lava Rock's two relics land at
the act-1 boss, i.e. at the exact moment my round ends, and over Precarious
Shears because −16 HP on floor 1 with an unknown kit is a bet I could not price.

---

## Fight 1 — Shrinker Beetle, HP 38/38

**Turn 1.** Hand was 3× Strike / 2× Defend — every card a basic. Enemy intent was
`Strategic (DebuffStrong)`, so Block would have prevented nothing. Played all
three Strikes for 18. **Alternative rejected: none.** There was no decision here;
with no kit card in hand and a non-damaging intent, "play the three attacks" is
the only line. This is the answer to (e) below.

**Turn 2.** The debuff landed: `Shrink -1 — While Shrinker Beetle is alive, your
Attacks deal 30% less damage`, and Strike's printed face changed from "Deal 6
damage" to "Deal 4 damage". The screen updating the printed number was the single
clearest piece of teaching I got all run. Drew Ka-pow! and Jumpy Dumpty. The Bomb
keyword read *"Not an Attack: only their Vulnerable and a cap move it"*, which I
took to mean Shrink does not touch Bomb damage — so the correct play against a
Shrink enemy is to route damage through Bombs. Played Jumpy Dumpty (Bomb 8),
Ka-pow! (Set off → 8, plus its own 2), Strike, Defend. **Rejected: double Defend
to blank the 7-damage hit** — rejected because Shrink is priced per turn the
beetle is alive, so racing costs less than stalling. Outcome matched: 20 → 10,
exactly 8 + 2, and Ka-pow's own hit was the shrunk 2, not 4.

**Turn 3.** Mine 3 (placed by Jumpy Dumpty's bomb going off) detonated on the
beetle's attack for 3, before the hit, exactly as the Mine keyword said. One
Strike finished it. **Rejected: rebuilding a bomb** — pointless at 3 HP.

Result: 60/62. Card reward taken: **Mine Toss** over Pop! — Pop! places a Bomb 5
for 0 but is inert without a Set off card, and I had exactly one (Ka-pow!).

---

## Fight 2 — Fuzzy Wurm Crawler, HP 57/57

**Turn 1.** Intent 4 damage. Played Jumpy Dumpty (Bomb 8), Mine Toss (Mine 4),
Strike. **Rejected: playing the retained Ka-pow! to cash the Bomb 8** — rejected
because the Bomb keyword prints "grows 4 a turn" and the enemy only threatened 4,
so a growth turn was nearly free. This was the first turn of the run that felt
like a real decision: bank or cash.

**Turn 2.** Enemy intent `Empower (Buff)` — zero incoming. Played three Strikes,
held Ka-pow!. **Rejected: detonating the Bomb 12** — same reason, a buff turn is
a free growth turn. Cost: the enemy came out of it with **Strength 7**, which is
the counter-pressure on banking.

**Turn 3.** 29 HP left, Bomb 16 on it. Played Jumpy Dumpty (a second Bomb 8),
then Ka-pow! → both bombs went off for 24 total plus Ka-pow's 4. **Rejected: one
more growth turn** — rejected because Strength 7 had turned its hit from 4 into
11. Strike finished it. Here I learned the badge arithmetic: the enemy's badge
reads `Bomb 16 ... Bombs here: 1` and then, after the second placement and
detonation, `Bomb 6 ... Bombs here: 2, including 2 Mines`. **The number on the
badge is the sum of all bombs, not the size of one.** Nothing on screen says so;
I worked it out from the damage.

Result: 56/62. Reward: **Sizzle** over Careful Now / Dodoco Cover / Fischl. I
took a second Set off because one detonator in a 12-card deck means bombs sit
inert on the turns I do not draw it.

---

## Fight 3 — Nibbit, HP 44/44

**Turn 1.** Intent 12 damage. Played Mine Toss, Strike, Defend, held Ka-pow!.
**Rejected: playing Ka-pow! to set off the fresh Mine 4** — rejected because a
Mine detonates itself for free when its enemy attacks, so spending a Set off card
on one throws the card away. That distinction (Mine self-triggers, Bomb does not)
is well taught by the two keyword blocks.

**Turn 2.** Intent was `Aggressive (Attack) 6` **and also** `Defensive (Defend)`.
Because its Block arrives on its own turn, damage now lands bare and damage
banked for next turn does not. Played Jumpy Dumpty, Ka-pow! (8 + 4), Strike,
Strike. **Rejected: banking the Bomb 8 for a turn of growth** — rejected on the
Defend half of the intent. 34 → 10, then Mine 3 on its attack → 7.

**Turn 3.** 7 HP behind Block 5. Played Jumpy Dumpty then Sizzle: bomb 8 + 6 = 14
into 12 effective. Dead. **Rejected: Sizzle alone** (6 into 5 Block = 1).

Result: 43/62. Reward: **Fish-Flavored Bait** (4 damage *and* a Bomb 4 for one
energy) over Safety Lesson, whose 2 Block per bomb is worse than one Defend at
the bomb counts I was actually seeing.

---

## Fight 4 — Mawler, HP 72/72

**Turn 1.** Intent 4×2. Fish-Flavored Bait, Strike, Defend; held Ka-pow!.
**Rejected: Ka-pow! on the Bomb 4** — 4 now against 8 next turn on a 72-HP body.

**Turn 2.** Intent `Strategic (Debuff)` — a free turn. Jumpy Dumpty, Mine Toss,
Strike, still holding Ka-pow!. **Rejected: a third Strike over Mine Toss** —
6 now vs a Mine that reads 8 after one growth tick; I chose the mine.

**Turn 3.** Badge read `Bomb 32 (buff) ... Bombs here: 3, including 1 Mine` and I
was Vulnerable 3 against a 21-damage intent at 40 HP. Played Ka-pow! → **exactly
36** (32 bombs + 4), then Strike, Strike, Sizzle (which set off the Mine 3 that
Jumpy Dumpty's detonation had just laid). Killed it from 56 in one turn.
**Rejected: Ka-pow! + Sizzle + two Defends**, which would have left it on 11 and
me eating 21 — rejected once I had counted 57 available damage against 56 HP.
This was the best turn of the run and the first time the kit's shape was legible
to me as a *plan* rather than a set of cards: place, wait, cash.

Result: 40/62. Reward: **Dodoco Cover** over Witches' Circle (no Hexerei card in
my deck at all, so it reads as blank), Run Away!, and Barbara.

---

## Fight 5 — Cubex Construct, HP 65/65

**Turn 1.** `Empower (Buff)` intent. Dodoco Cover (Bomb 4 + Block), Strike, and a
Defend played purely to cycle it out of a 14-card deck. **Rejected: holding the
third energy** — with a buff intent the Block was dead anyway, so the only value
left in the card was getting it into the discard.

**Turn 2.** Jumpy Dumpty, Strike, Strike; held Ka-pow!. **Rejected: Defend
against its 9** — its Strength was climbing 2 per turn, so I bought tempo.

**Turn 3.** Bomb 24 on board, 47 HP. Fish-Flavored Bait (adds Bomb 4 *before* the
set off), Ka-pow! (28 bombs + 4), Sizzle (the Mine 3 + 6), Strike. 47 → dead.
**Rejected: another growth turn** — Strength 4 and rising.

Result: 45/68 (after the Unrest Site event, below). Reward: **Big Badda Boom** —
"Set off. Deal 12 damage. Then deal damage equal to what the Bombs dealt." Its
text made its use obvious the moment I read it: it pays the stack twice.

**Unrest Site (between fights 4 and 5):** offered "Rest Anyways: heal to full,
receive Poor Sleep" and "Kill the Trees: lose 8 Max HP, obtain a random Relic."
Took Kill the Trees. **The screen never printed which relic I got.** I only found
out it was Mango (+14 Max HP) by reading my relic list at the top of the next
combat. That is a legibility gap in the bridge or the event, not in the kit.

---

## Fight 6 — Axe Raider 20/20, Crossbow Raider 18/18, Tracker Raider 23/23

First multi-enemy fight, and the one that exposed the kit's shape most sharply:
**Set off is single-target** ("Every Bomb on **the target**"), while Mine Toss and
Jumpy Dumpty's rider place on **ALL** enemies. So against a group, the AoE half of
the kit and the detonator half do not meet — except through Mines, which
self-trigger per enemy.

**Turn 1.** Fish-Flavored Bait onto the Tracker (largest, and debuffing so it
would not Block), Strike into the Crossbow, Defend. **Rejected: spreading damage**
— with a single-target detonator I wanted one fat stack, on the body that would
still be alive to receive it.

**Turn 2.** Frail 2 landed and Defend's printed face dropped from 5 to 3 — again,
the screen updates the number, which I appreciated. Big Badda Boom into the
Tracker: 8 (bomb) + 12 + 8 = 28 into 19 HP, dead. Then Strike + Ka-pow! into the
Crossbow. **Rejected: blocking** — Frail made a card of Block worth 3 against a
14-damage attacker I wanted dead.

**Turn 3.** Sizzle killed the Crossbow (5 HP). Jumpy Dumpty + Ka-pow! into the Axe
Raider: **12 damage into 20 HP behind Block 5 left it on 13.** So **Block does
absorb Bomb damage**, even though the Bomb keyword says "Not an Attack: only their
Vulnerable and a cap move it." That sentence enumerates what *scales* the bomb and
is silent on what *absorbs* it; I read it as implying block-immunity and I was
wrong. See (c). Then Mine Toss. **Rejected: Dodoco Cover** — the Mine's 4 on its
attack beat 3 Block plus a bomb I would not live to grow.

**Turn 4.** Strike finished the Axe Raider.

Result: 39/73. Reward: **Fwoosh!** (cost **1 Spark**, Set off, 6 damage) over
Flame Dance, Chain Fuse and Lynette. Until this card I had accumulated Sparks all
run — 5 by the end of one fight — with **nothing in my deck that spends them**.
Pounding Surprise had been generating a resource I could not use.

---

## Fight 7 — ELITE: Byrdonis, HP 82/82

`Territorial 1 — At the end of Byrdonis's turn, it gains 1 Strength.` I came in at
39/73, which was my own mismanagement, and this fight was the closest I came to
dying.

**Turn 1.** Strike, Strike, Defend, plus **Block Potion**: 5 + 12 = 17 Block
against a 17-damage intent, taking exactly 0. **Rejected: saving the potion for a
bigger hit later** — rejected because Block prevents its own value whenever it is
spent, and pairing it with a Defend to exactly cover a 17 meant none of it spilled.

**Turn 2.** Jumpy Dumpty then Big Badda Boom: 8 + 12 + 8 = **28 exactly**. 70 →
42. **Rejected: holding the Bomb 8 to grow** — rejected because Big Badda Boom is
not Retain, so it would have shuffled away, and it is the card that pays the stack
twice. Then **Skill Potion**, which offered Run Away! / Mine Toss / Quick Fuse; I
took **Run Away!** for 7 Block ("+4 if a Bomb went off this turn" — it had) over
Quick Fuse's net +3 damage. Free-to-play covered the energy, which the potion's
text said and which held.

**Turn 3.** 34 HP against a 19-damage intent, elite on 39. Emptied the hand:
Fish-Flavored Bait, Dodoco Cover, Ka-pow! (8 bombs + 4), **Fwoosh!** (its Spark
price, not energy — so it fit alongside a full three-energy turn, which is the
whole point of the card), Defend, plus **Poison Potion**. 39 → 17, then poison.
**Rejected: banking a turn** — at 34 HP with Strength climbing there was no fourth
exchange available to me.

**Turn 4.** Jumpy Dumpty + Fwoosh! = 8 + 6 into 11 HP. Dead.

Result: 25/73. Rewards: Toxic Egg, and **Dig In+** (cost 1 Spark, gain 11 Block)
over **The Big One** ("Set off for quadruple damage", cost 3). I picked defence
because I had nearly died; The Big One is plainly the stronger card for the
engine and I want to say plainly that I passed on it out of fear, not judgement.

---

## Fight 8 — BOSS: Vantom, HP 173/173

`Slippery 8 (buff) — The next 8 times Vantom loses HP, it only loses 1 HP
instead.` This is a direct, deliberate answer to the bomb kit, and it produced the
most interesting decision of the run — and the most uncomfortable.

Because **Set off resolves every bomb "one at a time, each a Pyro hit for its
size"**, each bomb in a stack is its own HP-loss event. Detonating a 16-point,
two-bomb stack under Slippery would have paid me **2 damage** and burned 2
charges. And because **every attack in my deck except Strike and Fish-Flavored
Bait carries a mandatory Set off**, I could not chip at the charges without
throwing away the stack. For two turns most of my hand was, in effect, unplayable.

**Turn 1.** Fish-Flavored Bait, Strike, Dodoco Cover. 173 → 171 (two hits, 1 each,
exactly as printed), Slippery 8 → 6. Dodoco printed **"Gain 10 Block"** — Vambrace
had already folded its doubling into the printed number, which is the right way to
show it. **Rejected: any Set off** — see above.

**Turn 2.** The real decision: **spend the 16-point stack cheaply to buy charges,
or hold it and be unable to act.** I spent it. Ka-pow! set off two bombs and hit
itself: 3 charges for 3 damage, Slippery 6 → 3, and Pounding Surprise handed me
+2 Sparks for the two detonations — the relic and the Slippery mechanic
interacting is a nice accident. Then Fwoosh! on a now-bare enemy (a 6-damage card
used as a 1-damage charge-burner), Big Badda Boom likewise (12 → 1), Spore Mind
exhausted, Dig In+ for Block. Slippery 3 → 1. **Rejected: holding Big Badda Boom**
— it would have sat useless while Slippery lived, and it reshuffles.
Note: Dig In+ gave **11**, not 22 — Vambrace's "first time each combat" had
already been spent on turn 1's Dodoco Cover. Correct, and I had mis-planned it.

**Turn 3.** Intent 26 + 3 Status cards. Strike burned the last charge. Two
Defends. **Rejected: Mine Toss for 4 chip** — a block card was worth more than 4
against a 26.

**Turn 4.** `Empower` — free turn. Jumpy Dumpty, Strike, and a Defend cycled.
**Rejected: Sizzle and Fwoosh!, both in hand and both affordable** — I could not
play either, because their Set off is mandatory and would have cashed a Bomb 8 for
8. On a free turn I had two attacks in hand I was forbidden to use. That is the
sharpest thing I learned about this kit.

**Turn 5.** Strike, Strike, Mine Toss, Dig In+ (11 Block against a 9): 16 damage
taken 0.

**Turn 6.** Fish-Flavored Bait + Dodoco Cover, holding Ka-pow!. Third energy
**stranded** — the hand was Ka-pow (0, retain), two Wounds, and nothing else.

**Turn 7.** Badge read `Bomb 36 ... Bombs here: 3`, and Big Badda Boom came up.
**84 damage in one card** (36 + 12 + 36). 139 → 55. **Rejected: holding for one
more growth tick** — impossible, Big Badda Boom is not Retain. Then Defend +
Dig In+ for 16 Block against a 28.

**Turn 8.** Another `Empower` free turn. Jumpy Dumpty + Dodoco Cover +
Fish-Flavored Bait, rebuilding to 16 and holding Ka-pow!. **Rejected: cashing 16
immediately** — a free turn is worth 12 of growth across three bombs.

**Turn 9.** Bomb 28. Ka-pow! → 32, then three Strikes. 48 → dead.

Result: **39/83.** Rewards: 115 gold and **Sugar Rush+** (2 Sparks: gain 3 Energy,
draw 1, exhaust) over Chained Reactions, Alice's Introduction Magic+ and Venti+ —
I picked it because I had ended the boss fight holding **7 Sparks** and had twice
stranded energy, and this card is the only thing I have seen that trades the
surplus back into a turn. No relic was offered by the boss.

---

## The kit, after 8 fights

**(a) Which decisions felt like real choices, and what they traded off.**

One decision carried this whole run, and it is a good one: **bank or cash.** Bombs
grow 4 a turn each and go off only when a Set off card fires, so every turn asks
whether to add to the pile or empty it. The trade-off is legible in both
directions and the game keeps pricing it honestly:

- The *reason to bank* is arithmetic I could do from the screen: three bombs on
  the board is +12 a turn, better than any card in my deck.
- The *reasons to cash* were all printed on the enemy: a `Defensive` half-intent
  (banked damage will meet Block), a Strength-gaining buff (Byrdonis, Cubex,
  Fuzzy Wurm all made waiting more expensive each turn), and Big Badda Boom
  turning up in hand without Retain, which is a hard deadline.

Enemy intent lines therefore drove almost every real choice. `Empower` and
`Strategic` turns read as *free growth turns* and I learned to look for them; a
`Defensive` line read as *cash now*. That is a genuine and readable dialogue
between the kit and the enemy roster.

Two more that were real: **whether to spend a Set off card on a Mine** (never —
Mines self-trigger, so the card is wasted), and, at the boss, **whether to dump
a stack cheaply to strip Slippery**. That last one is the best puzzle the run
produced, even though it made two of my turns feel like a penalty box.

**(b) What felt automatic, and what never seemed worth playing.**

Automatic: the basic Strikes and Defends, throughout. By fight 4 they existed to
fill the third energy pip and to cycle. Also automatic once seen: Dodoco Cover
and Fish-Flavored Bait — a bomb stapled to a Defend or a Strike is a strict
upgrade, so there is no decision in playing them, only in what they replaced.

Never worth playing: **Mine Toss against a single enemy.** A Mine on a lone
attacker just detonates for its printed number on the next hit and never grows,
so it is a 4-damage card for one energy — worse than Strike. It is excellent
against three enemies and dead weight against one, and nothing on the card says so.

Structurally not-worth-playing, and this is the finding I most want on the record:
**Sizzle and Fwoosh! became unplayable whenever I was banking.** Their Set off is
mandatory, not optional. On boss turn 4 I had a free turn, three energy, a full
hand, and two attacks I was not allowed to touch. A kit whose plan is "stack for
three turns" and whose cheap attacks all read "Set off" is fighting itself. An
optional Set off, or one cheap non-set-off Pyro attack, would fix it.

Also: **Sparks were an inert resource for six fights.** Pounding Surprise fed me
1 Spark per detonation from floor 1, and I ended fights holding 4 or 5, with no
card in my deck that had a Spark price. The Spark keyword even says "no cap ...
Gone after combat", so it was visibly accumulating and visibly being thrown away.
Once Fwoosh! and Dig In+ arrived it became the best thing about the kit — a whole
second energy bar that pays for a set-off and a block card on the same turn as
three full-energy plays. The floor for that should probably be in the starting
deck rather than left to card rewards.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **The Bomb badge number is a sum, and nothing says so.** `Bomb 32 ... Bombs
   here: 3, including 1 Mine` means three bombs totalling 32, not three bombs of
   32. I inferred it from damage after the fact. The line "Set off here deals 32
   Pyro damage" is what saved me, but the badge title reads as a per-bomb size.

2. **"Not an Attack: only their Vulnerable and a cap move it."** I read this as
   Bomb damage ignoring Block. It does not: 12 points of Set off into Axe Raider
   at 20 HP behind Block 5 left it on 13. The sentence lists what *scales* a bomb
   and is silent on what *absorbs* one, and that silence reads as a claim.

3. **Set off is single-target, but the placers are ALL-enemies.** Jumpy Dumpty
   places one Bomb and, on detonation, a Mine on ALL; Mine Toss places on ALL.
   Every Set off card says "the target". Against three Raiders the kit therefore
   has two disconnected halves, and only Mines bridge them. Nothing signposts this.

4. **Ka-pow!'s printed damage silently included the Shrink reduction** (it read
   "Deal 2 damage" under Shrink, "Deal 4" without). That is correct behaviour and
   I liked it — I flag it only because it means the printed number is a *current*
   number, which took me a fight to trust.

5. **The whole Elemental Reaction block was dead text for me.** Every card I owned
   was Pyro and every bomb detonation applies Pyro, so I never once triggered a
   reaction. Sizzle's rider ("If a Bomb triggered an Elemental Reaction this turn,
   deal 6 additional damage") never fired in eight fights, because my own bombs
   refresh the Pyro aura they would need to react against. Roughly a screen and a
   half of keyword text — Melt, Vaporize, Overloaded, Superconduct,
   Electro-Charged, Frozen, plus a long paragraph about a reaction that "looks as
   though it did not happen" — was printed on every combat screen and was never
   once load-bearing. That paragraph in particular I could not parse and never
   needed to.

6. **Non-kit, bridge-side:** the boss screen printed `## Your hand` **twice** in a
   row before the hand list. And "Kill the Trees — obtain a random Relic" never
   printed which relic I obtained.

7. **Non-kit, rest sites:** Rest printed "Heal for 30% of your Max HP (20)" and
   healed 25; the next printed 21 and healed 26. Both are explained by Stone
   Humidifier's +5 Max HP also granting 5 current HP, which no screen says. The
   printed number is the one I planned against and it was wrong by 5 both times.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Mine Toss** in a single-enemy fight — and, more painfully,
**Sizzle**, which I repeatedly held because playing it would have destroyed my
own plan. Sizzle is the card I most often had in hand and least often played.

Happiest to draw: **Big Badda Boom**, without contest. "Then deal damage equal to
what the Bombs dealt" turns the banking decision into a payoff you can feel — 28,
then 84, both landing on the exact number I had counted. It is the card that makes
the whole stack-and-wait plan feel like a plan rather than a stall. Second place:
**Fwoosh!**, for making Sparks real and for letting a full three-energy turn also
contain a detonation.

**(e) Did the first turn of the first fight already present a decision?**

**No.** The opening hand was 3× Strike and 2× Defend — five basic cards, no kit
card — against an enemy whose intent was `Strategic (DebuffStrong)`, so Block was
worth nothing. There was exactly one line: play the three Strikes. I rejected no
alternative because there was none. The kit did not speak to me until turn 2 of
fight 1, when Ka-pow! and Jumpy Dumpty arrived together; and I only understood
what it *wanted* on turn 3 of fight 4, when a 32-point badge cashed for exactly 36
in one card. That is a slow open, and if the intent is for the first turn to teach
the kit, one Bomb card in the opening five would do it.

---

## Non-blindness declaration

Commands run outside the two allowed ones:

- `mkdir -p <scratchpad>` and `echo "<n>" > <scratchpad>/actcount.txt` (about
  twenty times), to keep the running count of accepted `act` calls the
  coordinator required. Never read back into any decision except the budget.
- `cat <scratchpad>/actcount.txt` once, immediately after creating it, to confirm
  the file existed.
- `sed -n '<ranges>'` and `head -N` / `tail -N` filters applied to the output of
  `observe` and `act`, to re-read one block of a screen (the enemy block, the
  hand, the command list) without reprinting the whole page. These only trimmed
  output I had already been shown; no output was redirected away from my view.
- `for i in 1 2 3; do ... done` once, to issue three identical `act` calls.

Tools used: **Bash** (for the two allowed commands and the scratch operations
above) and **Write** (once, for this record).

I did not run `harness state`, `scenario`, `staged_turn`, `soak`, or any other
understudy command. No `TOOL-BLOCKED` and no `REFUSED: ...leak...` line appeared
at any point. The one refusal I received was
`error Rest site room is not open`, recorded above.

**Repo files read: none.**
