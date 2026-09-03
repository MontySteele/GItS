# Blind seat record — KLEEMOD-KLEE, lane 2, act 1

## Identity

- **Model / seat:** Claude Opus 5 (1M context), blind TESTER seat, round 7b.
- **Lane:** 2 (`GITS_LANE=2 python -m understudy.blindplay`).
- **Run seed:** never printed on any screen I saw. Not recorded.
- **Character:** KLEEMOD-KLEE (never named on screen; identified only by the kit's own words — Bomb / Set off / Spark / Mine).
- **Act:** 1. **Boss named by the map:** **Ceremonial Beast** (printed as "At the top of this act").
- **Actions accepted:** 130 accepted `act` calls, 0 refused.
- **Termination reason:** act-call budget (130) exhausted. Not a TOOL-BLOCKED, not a refusal streak, not a repeated screen. Boss NOT reached.
- **Where the run stands:** the act-1 map screen, 7 floors cleared, **9 floors ahead of me to the Boss**. The two nodes offered are `Unknown (path 1)` (leads on to Treasure) and `RestSite (path 2)` (leads on to Treasure, Treasure). Next floor row printed: `Unknown, Unknown, RestSite, Monster`.

**HP trajectory** (every reading the screens printed, in order):
62/62 → 60 (end fight 1) → 57 (fight 2 r2) → **54** (fight 3 r1 — 3 HP lost with nothing printed to explain it, see Fight 2) → 50 (fight 3 r2) → 48 (fight 4 r4) → 41 (elite r4) → 34 (elite r5) → 31 (fight 6 r4) → 27 (r5) → 25 (r6) → 23 (r7). **Ending HP: 23/62.**

**Gold:** no screen ever printed a running gold total. Gold *claimed* from rewards: 15 + 10 + 20 + 13 + 44 + 11 = **113** (plus whatever the run started with). The Spoils Map card in my deck prints "Marks a site of 600 extra Gold in the next Act."

**Potions at the end:** `Dexterity Potion — Gain 2 Dexterity.` (one slot filled). Spent during the run: `Duplicator — This turn, your next card is played an extra time.` (elite, round 3) and `Block Potion — Gain 12 Block.` (fight 6, round 3).

**Relics at the end, exactly as printed:**

- **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark. Card rewards after a fight offer a fourth Companion choice.
- **Hefty Tablet** — Upon pickup, choose 1 of 3 Rare cards to add to your Deck, and add 1 Injury to your Deck.
- **Planisphere** — Whenever you enter a ? room, heal 5 HP.

**Deck at the end — 19 cards.** No screen in this bridge shows a deck list, so this is reconstructed from card faces as they were printed in hand, and from the pile counts (fight 6 round 1 printed 13 in draw + 5 in hand = 18, and I added 1 card after that fight, which is the arithmetic check). Faces are quoted as printed *unshrunk*; note that Strike printed "Deal 4 damage" and Ka-pow! "Deal 2 damage" whenever a Shrinker Beetle was alive.

- **Strike** ×4 — cost 1, attack. "Deal 6 damage."
- **Defend** ×4 — cost 1, skill. "Gain 5 Block."
- **Jumpy Dumpty** — cost 1, skill. "Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies."
- **Ka-pow!** [Pyro] — cost 0, attack. "Retain. Set off. Deal 4 damage."
- **Sparks 'n' Splash (proto)** — cost 2, power. "At the end of your turn, deal Pyro damage to a random enemy equal to the Bombs on it." *(Neow rare)*
- **Pop!** — cost 0, skill. "Place a Bomb 5." *(fight 1 reward)*
- **Fish-Flavored Bait** [Pyro] — cost 1, attack. "Deal 4 damage. Place a Bomb 4." *(fight 2 reward)*
- **Grounded** — cost 1, power. "At the start of your turn, if none of your Bombs went off last turn, gain 6 Block." *(fight 3 reward)*
- **Thoma — Blazing Barrier (proto)** — cost 1, skill. "Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block." *(fight 4 reward, Companion)*
- **Charlotte — Framing: Freezing Point Composition** [Cryo] — cost 1, attack. "Deal 4 damage. Draw 1 card." *(elite reward, Companion)*
- **Ammo Scavenging** — cost 1, skill. "Place a Bomb 4. Draw 1 card for each of your Bombs that went off this turn." *(fight 6 reward)*
- **Injury** — cost 0, curse. "Unplayable." *(from Hefty Tablet)*
- **Spoils Map** — cost 0, quest. "Unplayable. Marks a site of 600 extra Gold in the next Act." *(from the event)*

**Neow pick: Hefty Tablet** ("Choose 1 of 3 Rare cards to add to your Deck. Add 1 Injury to your Deck.") — I had never seen this kit, and a screen showing three of its Rares was the largest amount of kit I could buy with one choice; the Injury was the price I paid for that look.

**The rare I took: Sparks 'n' Splash (proto)** — of the three, it was the only one that did not require me to already own a card that says "Set off"; Chained Reactions needs Bombs to *go off* and The Big One costs 3, and at that point I had no idea whether my starting deck contained a detonator at all. (It did — Ka-pow! — but I could not know that.)

---

## Fight 1: Shrinker Beetle — HP 40/40

**Turn 1.** Played `Jumpy Dumpty` → `Strike` → `Strike`, all on the Beetle. **Rejected:** `Defend`. The intent line read "Strategic (DebuffStrong) — This enemy intends to apply a Debuff to you", i.e. no attack number, so 5 Block would have prevented nothing. This was a real decision and the screen gave me exactly what I needed to make it.

**Turn 2.** Screen now read `Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks deal 30% less damage`, and — this is the good part — **the Strike in my hand had re-printed itself as "Deal 4 damage"** rather than 6. The debuff was legible on the card face, not just in a status line. Bomb had gone 8 → **12** ("Bomb 12 (buff) — Set off here deals 12 Pyro damage. Bombs here: 1"), matching "Grows by 4 at the start of your turn."

Played `Sparks 'n' Splash (proto)` (2) then `Defend` (1). **Rejected:** playing `Ka-pow!` to set off the Bomb 12 immediately. I held it because Ka-pow! prints `Retain`, so holding cost me nothing, and I wanted to find out whether the power consumed the bombs it read. Also rejected `Strike` over `Defend`: the Beetle intended 7, and blocking 5 of it was worth more than 4 shrunken damage since the kill was already arriving next turn either way.

**Outcome, and the thing I learned:** end of turn dealt exactly 12 and the Bomb **survived and grew to 16**. Sparks 'n' Splash reads the stack without spending it. That single fact set my whole line for the rest of the run.

**Turn 3.** `Ka-pow!` on the Beetle — Bomb 16 vs 16 HP, lethal, free. **Rejected:** nothing meaningful; this was an obvious lethal and presented no decision.

---

## Fight 2: Twig Slime (S) 9/9, Twig Slime (M) 26/26, Leaf Slime (S) 14/14

**Turn 1.** `Pop!` (0) and `Jumpy Dumpty` (1) both onto **Twig Slime (M)**, then `Strike` ×2 into **Twig Slime (S)**, killing it. **Rejected:** spreading the bombs across two slimes. "Bombs on one enemy go off together when Set off" told me concentration is how the stack pays, so I concentrated on the 26 HP body and used the Strikes to delete the 9 HP attacker outright rather than chip two enemies for no kill. Real decision, and the keyword text is what decided it.

**Turn 2.** Bomb read **21** with "Bombs here: 2" — two bombs, +8 in one turn, so growth is per bomb, which the card text (+4) does not quite say out loud. Played `Ka-pow!` (set off 21) then `Strike`, killing Twig Slime (M) before its 11 landed. **Rejected:** the two `Defend`s in hand — killing the 11-damage attacker outright is strictly better than blocking it, and the remaining slime's intent was a status card, not damage. Spark went 1 → 3, confirming Pounding Surprise pays per bomb, not per detonation.

**Turn 3 — the turn I played nothing.** Leaf Slime was at 14/14 and its badge read `Bomb 14 (buff) — ... Bombs here: 2, including 2 Mines ... A Mine also goes off when this enemy attacks you, before the hit lands.` Its intent was Attack 3. 14 mine damage vs 14 HP. I ended the turn without playing a card and the mines killed it. **Rejected:** Strike ×2 (12, not lethal) and any Defend. Trusting the printed mine rule *was* the decision, and it is the most interesting turn in the run — the kit let me win a turn by doing nothing, on purpose, because I'd read a keyword correctly.

**Two places the screen and the outcome disagreed here:**

1. **The mine count.** `Jumpy Dumpty` prints "When **it** goes off, place a **Mine 3** on ALL enemies" — one bomb, one mine. Two bombs went off (Pop!'s and Jumpy Dumpty's), and the surviving Leaf Slime showed "Bombs here: 2, **including 2 Mines**" totalling 14 (= 3+3 grown by +4 each). So the rider appears to have fired once per bomb that went off, not once for the Jumpy Dumpty bomb. I could not have predicted the mine count from the card.
2. **"before the hit lands."** The mines killed the Leaf Slime on its attack, and I was at HP 57 on the last screen of that fight — but the very next combat screen opened at **HP 54/62**. The only thing between them was the event, whose taken option ("Nab the Map — Receive the Spoils Map") printed no HP cost at all, while the option I *declined* printed "Lose 8 HP" explicitly. The most likely read is that the Leaf Slime's 3 damage landed even though the Mines killed it first, which is the opposite of what the Mine keyword promises. I cannot prove it from the screens; I am reporting the 3 HP and where it appeared.

---

## Fight 3: Fuzzy Wurm Crawler — HP 57/57

**Turn 1.** `Pop!` (0) → `Sparks 'n' Splash (proto)` (2) → `Strike` (1). **Rejected:** `Defend`. The Wurm intended 4; installing the power on the cheapest turn of a long fight against a 57 HP single target beat blocking 4. Real decision, and an easy one.

**Turn 2 — a turn with no decision in it.** Hand was `Fish-Flavored Bait`… no: hand was Defend, Strike, Defend, **Spoils Map** and **Injury**. Two of five cards printed "CANNOT BE PLAYED", the enemy's intent was "Empower (Buff)" so both Defends were dead, and that left exactly one legal useful play: `Strike`. I played it and ended. **No alternative was rejected, because none existed.** That is the finding.

It is also where I learned the event lied by omission: "Nab the Map — **Receive the Spoils Map**" reads like a relic. It is a card, it goes in your combat deck, and it prints `Unplayable`. Nothing on the event screen said I was adding a dead card to my draw pile.

**Turn 3 — the best decision of the run.** Wurm at 31 with `Bomb 13`, `Strength 7`, intending 11. I played `Fish-Flavored Bait` → `Jumpy Dumpty` → `Strike`, and **deliberately did not play the free `Ka-pow!` in my hand.** Setting off would have spent the 13 for 13. Stacking instead took the stack to 25, and Sparks 'n' Splash read all 25 at end of turn: 31 − 4 − 6 = 21, then 25 killed it before its 11 landed. Ka-pow!, a free card sitting in my hand, was the card it was correct to *not* play. That is a genuine, sharp trade-off — and it is also the kit quietly telling me its own detonators are bad.

---

## Fight 4: Mawler — HP 72/72

**Turn 1.** `Pop!` (0), `Defend`, `Defend` — 10 Block against a printed 4×2. **Rejected:** `Ka-pow!` to set off the Bomb 5 for 5. Five damage now versus a bomb that grows 4 a turn and gets read every turn by a power I hadn't drawn yet: easy hold.

**Turn 2.** `Sparks 'n' Splash (proto)` (2) + `Jumpy Dumpty` (1). **Rejected:** `Fish-Flavored Bait` in the same slot. Both lines put the Mawler on 55 this turn, but Bait leaves a 13 stack and Jumpy Dumpty leaves 17, and each extra bomb adds another +4 per turn forever. Choosing between two lines with identical damage *this* turn and different slopes is a real decision, and the badge ("Bombs here: 2") is what made the slope readable.

**Turn 3.** Took `Vulnerable 3` (50% more damage from attacks), Mawler at 6×2 = 18 incoming. Played `Grounded` (1) + `Defend` + `Defend`. **Rejected:** `Ka-pow!` for 25+4 — it would have dealt 29 immediately but zeroed the end-of-turn tick *and* switched Grounded off for the following turn ("if none of your Bombs went off last turn"). Also rejected Strike ×2 over the Defends: 12 damage vs 5 HP, and Sparks 'n' Splash was already doing 25 a turn for free, so my cards were better spent on staying alive.

**Turn 4.** Grounded paid out exactly as printed (Block 6 at turn start). Bomb 33 against 30 HP with a 21-damage attack pointed at me. **`Ka-pow!` — lethal, free, immediate.** This is the payoff turn the whole structure is built around: hold the detonator for four turns, then spend it the moment the stack passes the enemy's HP. **Rejected:** ending the turn and letting the tick do it — same result, but Ka-pow removed all randomness.

---

## Fight 5 (Elite): Bygone Effigy — HP 127/127

Printed on it from turn 1: `Slow 0 (debuff) — Whenever you play a card, this enemy receives 10% more damage from Attacks this turn.`

**Turn 1.** Intent "Sleeping (Sleep) — This enemy is doing nothing this turn." I dumped `Strike` ×3. **Rejected:** `Defend` — nothing was coming. **Screen vs outcome:** 3 Strikes moved it 127 → 108, i.e. **19**, where 3 unmodified Strikes are 18. Slow says +10% per card played; against a 6-damage Strike that is worth about half a point a swing and rounds mostly to nothing. The debuff is printed as though it matters and it did not.

**Turn 2.** Intent "Empower (Buff)" — another free turn. Played `Grounded` + `Sparks 'n' Splash (proto)` + `Ka-pow!` (for 4, since there were no bombs to set off). **Rejected:** the three block cards in hand, again because nothing was incoming. Two consecutive free turns at the top of an elite is generous, and it is what let a 34 HP-deficit run take this fight at all.

**Turn 3.** It buffed to `Strength 10` and pointed 23 at me. Hand had **no bomb-placer except Fish-Flavored Bait**, and my engine card was already down doing nothing (a Power that reads bombs, with no bombs on the board, ticks 0 — which it duly did). I used `Duplicator` on `Fish-Flavored Bait`, then `Defend` ×2. **Rejected:** saving Duplicator for a later, bigger card (Jumpy Dumpty's Bomb 8 would have been 16 instead of 8). I spent it early on purpose: a bomb placed now is worth +4/turn *compounding*, so two Bomb 4s on turn 3 beat two Bomb 8s on turn 5. The screen confirmed it — `Bomb 16 (buff) ... Bombs here: 2`.

**Turn 4.** `Pop!` + `Jumpy Dumpty` + `Defend` ×2. **Rejected:** `Strike`. Every bomb I add is +4 per turn forever *and* +its face to the tick; a Strike is 6 once. In this kit, once the power is down, attacking is the weak play. Tick read 29. Stack went to **45 across 4 bombs**.

**Turn 5.** 59 HP left, Bomb 45, 23 incoming. Played `Strike` → `Strike` → `Ka-pow!` last (so Slow's multiplier, such as it is, applied to the biggest hit). 6 + 6 + 45 + 4 killed it. **Rejected:** ending the turn and taking the 45 tick instead — that leaves it alive on 14 and eats 23 to the face. The elite never landed a single hit.

---

## Fight 6: Shrinker Beetle 39/39 + Fuzzy Wurm Crawler 56/56

**Turn 1.** `Jumpy Dumpty` + `Fish-Flavored Bait` onto the **Wurm**, then `Defend`. **Rejected:** bombing the Beetle. From fight 1 I knew Shrink reduces *Attacks* but not bomb damage (a Bomb 12 set off for exactly 12 under Shrink), so the Beetle's debuff didn't threaten my real damage — but the Wurm was the one that grows Strength and hits. Also rejected `Strike` over `Defend`: at 34 HP, blocking the whole incoming 4 was worth more than 6 shrunken damage.

**Turn 2.** `Charlotte` on the Wurm, then `Defend` ×2 (full block of the Beetle's 7). Charlotte's face had grown a new line: `*Reaction preview: Melt* — This card supplies Pyro or Cryo while an enemy has the other aura. The triggering hit deals 1.75x damage and consumes the aura.` — it appeared **because** the Wurm was carrying the Pyro aura my own bombs had left. That is the single best piece of legibility in the kit: the card told me what it was about to do, on the card, in context. It hit for 4 where its shrunken face said 2. **Rejected:** `Ka-pow!` on a 20 stack — the stack grows 8 a turn and I could still afford to block.

**Turn 3 — the turn the engine's weakness showed.** 24 incoming, 34 HP. I played `Ka-pow!` (set off 28 + 2), `Thoma`, `Sparks 'n' Splash (proto)`, `Block Potion`. **Rejected:** holding the detonator and letting the tick do 28 — and here is why: the power says "deal Pyro damage to **a random enemy**", all 28 of my bombs were on the Wurm, and there were two enemies. Holding meant a coin-flip between 28 damage and *nothing*. Detonating was worth less on paper and more in fact because it was deterministic. **The random-target clause is what turned my engine off in a two-enemy fight.** Thoma held up well: 18 Block plus its own top-ups ate 24 incoming for 3.

**Turn 4.** `Pop!` on the Wurm, `Grounded`, `Thoma`, `Defend`. **Rejected:** `Strike`, and rejected killing the Wurm — I couldn't: it was on 12, my Strike printed 4, and I had no detonator in hand. Tick landed on the Wurm (the flip went my way) for 5.

Also visible on this screen: **`Spark 5`**. I had five Sparks and not one card in my deck that costs Sparks. Pounding Surprise's first clause was, for my deck, a counter that goes up and never does anything.

**Turn 5.** `Ka-pow!` killed the Wurm off its Bomb 9, then `Strike` ×2 into the Beetle and `Defend`. **Rejected:** killing the Wurm with the two Strikes instead and keeping Grounded switched on — I chose the free detonator and spent the Strikes on the Beetle, knowingly paying 6 Block next turn for 8 damage. Grounded then correctly printed no Block the following turn; **the card told the exact truth about its own condition.**

**Turn 6.** `Charlotte` (2 damage + draw) to dig — it found `Fish-Flavored Bait`, and Charlotte's Cryo made Bait a Melt hit. Played `Bait` + `Defend`. **Rejected:** `Strike` over Bait — Bait plants, and with only one enemy left the "random enemy" clause was finally deterministic, so a bomb was worth strictly more than 4 damage.

**Turn 7.** Beetle on 18 with Bomb 8. Played `Jumpy Dumpty` (stack → 16) + `Strike` ×2, and let the end-of-turn tick finish it. **Rejected:** the `Ka-pow!` line — 8 + 2 + 4 + 4 = exactly 18, lethal with zero margin. Stacking gave 8 immediate + 16 on the tick = 24 against 18, and still killed before the Beetle's 13 landed. Choosing the line with margin over the line that is exactly lethal is a real decision and I was glad to have it.

---

## Companions and offers

Pounding Surprise prints "Card rewards after a fight offer a fourth Companion choice", and one appeared on every single card-reward screen. Quoted exactly as printed:

1. **Diona — Signature Mix** — cost 1, skill. "Apply 2 Weak to ALL enemies. For 2 turns, at the start of your turn gain 4 Block. Exhaust." — Makes sense beside the kit, and better than it looks: the Bomb glossary says "Weak shrinks it like any Bomb", so Weak is a live interaction with the bomb line rather than a generic debuff. *Not taken* (I needed bomb-placers more).
2. **Mika — Starfrost Swirl** [Cryo] — cost 1, attack. "Deal 5 damage to ALL enemies. Your next Attack costs 1 less." — Sensible, and the Cryo tag is the interesting half: it plants the *opposite* aura for the Pyro kit to react off. *Not taken.*
3. **Dahlia — Sacramental Shower (proto)** — cost 1, skill. "The next time an enemy attacks you, deal 9 Hydro damage to it first." — Reads as a Mine that isn't a Bomb: same "when it attacks you, first" timing, but it does not stack, does not grow, and is not read by Sparks 'n' Splash. Coherent, but it quietly duplicates the Mine concept in a way I'd have had to test to tell apart. *Not taken.*
4. **Thoma — Blazing Barrier (proto)** — cost 1, skill. "Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block." — **Taken** (fight 4). Fits the kit's actual problem: the kit has no healing I ever saw and 5-Block Defends, and a bomb build wants to survive turns rather than win them. It performed: 24 incoming became 3 taken on fight 6 turn 3.
5. **Charlotte — Framing: Freezing Point Composition** [Cryo] — cost 1, attack. "Deal 4 damage. Draw 1 card." — **Taken** (elite). Makes sense next to the kit for a reason the card doesn't state: my hands kept arriving with no bomb-placer, and a cantrip is the fix. Its Cryo also turned my own Pyro aura into Melt hits, which the card face then previewed for me.
6. **Sucrose — Astable Anemohypostasis (proto)** — cost 0, skill. "Swirl ALL enemies. Exhaust." with "*Swirl* — The enemy's aura is consumed and copied onto ALL enemies. No aura, no effect." — The one companion I could not place. My Pyro is already applied by nearly every attack I own, so copying Pyro onto everything looked close to a no-op, and "No aura, no effect" means it is dead in exactly the fights (single enemy) where I have spare energy. *Not taken.*

**Cards printing "(proto)" that I saw** (reported without seeking): `Sparks 'n' Splash (proto)`, `Thoma — Blazing Barrier (proto)`, `Dahlia — Sacramental Shower (proto)`, `Sucrose — Astable Anemohypostasis (proto)`. Three of the four are Companions.

---

## The kit, after 6 fights

### (a) Which decisions felt like real choices, and what they traded off

The kit's central decision is genuinely good and it is **"do I spend the stack, or let it grow?"** Bombs grow +4 each, per turn, forever; Set off converts the whole stack to damage once. So every turn asks: is the stack lethal yet? Fight 3 turn 3, fight 4 turn 3 and fight 6 turn 7 were all decided on that axis, and they felt different from each other because the enemy's HP and its intent number kept moving the answer. Holding a *free* card (`Ka-pow!` costs 0 and Retains) for four turns because playing it would be a mistake is a legitimately interesting thing for a deck to ask.

Two more that had real teeth: **which enemy to concentrate bombs on** (concentration is what makes Set off pay, but it is also what makes the random-target tick miss), and **paying block to keep Grounded switched on** — fight 6 turn 5, where I chose 8 damage over 6 Block by detonating, is a clean little trade the card states precisely.

### (b) What felt automatic, and what never seemed worth playing

**Strike was never worth playing** once Sparks 'n' Splash was down. 6 damage once, against a bomb-placer that adds +4/turn compounding *and* its face to every tick. From fight 3 onward, every turn where I chose a placer over a Strike was the same choice with the same answer, which is the automatic part: *place, block, wait.* Turns where I held a detonator, a full stack and two Defends played themselves.

**Defend was near-automatic in the other direction:** with intents printed as plain numbers, "block it or don't" is arithmetic, and the 5-Block face is small enough that the answer was usually "play both".

**Sparks 'n' Splash makes the kit's own Set-off cards bad.** I was offered `Sizzle`, `The Big One`, `Flame Dance`, `Bang Bang!`, `Rapid Fire`, `Perfect Timing`, `Chained Reactions` — seven cards built around detonating — while holding a Power that reads the whole stack every turn *without consuming it*, and a second Power (`Grounded`) that pays me 6 Block per turn **specifically for not detonating**. Half the pool I was shown actively fights the other half. That is the sharpest structural thing I found, and I'd flag that a player who takes the same Neow rare I did will correctly learn to skip most of the kit's attack cards.

### (c) What I could not understand, or that contradicted its own printed text

- **`Jumpy Dumpty`'s mine count.** "When it goes off, place a Mine 3 on ALL enemies" — but in fight 2 two bombs went off and the surviving enemy showed "Bombs here: 2, including 2 Mines" (14 total). One card, one rider, two mines. I could not derive that from the text.
- **"before the hit lands."** Fight 2's mines killed the Leaf Slime on its attack and I still appear to have paid its 3 damage (57 → 54 across an event that printed no HP cost). If the mine kill doesn't actually pre-empt the hit, the keyword is saying something untrue.
- **`Flame Dance`: "Set off each enemy whose aura is not Pyro."** Nearly every attack in this kit prints "Applies Pyro". So the card is worded to turn *off* against the aura my own deck is constantly applying. I skipped it twice because I couldn't work out when it would ever fire.
- **The Bomb glossary disagrees with the Bomb card text on the same screen.** Card-embedded text: "Grows **by 4** at the start of your turn." The "Words on this screen" glossary directly below: "Grows at the start of your turn." The number is missing from the glossary copy, on every screen, and the number is the entire mechanic. Worse, growth is actually +4 *per bomb* (Bomb 5 + Bomb 8 → 21, not 17), which neither wording says.
- **`Slow`** ("+10% damage from Attacks per card played") moved three Strikes from 18 to 19. It is printed like a mechanic and behaves like a rounding error.
- **`Pounding Surprise`'s Spark clause was inert for my whole run.** I finished at Spark 6 having never owned a card that costs Sparks. Sparks are only spendable on cards you might not draft, so a starting relic's headline effect can sit at zero for an entire act. The `Spark` glossary even advertises "Pounding Surprise grants more", which reads like a promise the deck can't cash.
- **The event.** "Nab the Map — Receive the Spoils Map" gave me a permanent unplayable card in my combat deck. The screen's other option printed its cost ("Lose 8 HP") honestly; this one printed nothing.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted:** `Strike`. It was the card I left in hand or played only as filler once the engine was running, and under Shrink it printed "Deal 4 damage" — four damage, for a full energy, in a deck whose Power was ticking 29. (`Injury` and `Spoils Map` are worse but they're not choices.)

**Happiest to draw:** `Sparks 'n' Splash (proto)` is the honest answer for power, but the card I was most *pleased* to see was **`Ka-pow!`** — free, Retain, and the only card whose value changed every single turn. It sat in my hand across four turns of the Mawler fight getting better, and then deleted 30 HP the instant it was lethal. A 0-cost card that I am repeatedly, correctly choosing *not* to play is a nice piece of design.

### (e) Did the first turn of the first fight already present a decision?

**Yes, and a fair one.** Hand was Strike, Strike, Defend, Jumpy Dumpty, Injury, 3 energy, against a Shrinker Beetle whose intent printed as "Strategic (DebuffStrong) — This enemy intends to apply a Debuff to you". No attack number meant Defend was visibly dead, so the turn was really "plant the bomb and swing twice, or hold". I had to read a keyword I'd never seen (Bomb: grows, never goes off by itself) and decide whether to invest a card in something that does nothing this turn. That is a decision, it was legible from the screen alone, and the Injury sitting there unplayable was the only sour note — turn one of the run, one of my five cards was already blank, which was my own Neow choice and fair enough.

---

## Non-blindness declaration

- **Commands outside the two allowed ones:** none. Every game interaction was `GITS_LANE=2 python -m understudy.blindplay observe` or `GITS_LANE=2 python -m understudy.blindplay act "<command>"`. I never ran `harness state`, `scenario`, `staged_turn`, `soak`, or any other understudy command.
- **Tools used:** the **Bash** tool (to run the two allowed commands, chaining them with `&&` to conserve tool calls), and the **Write** tool once, to create this file.
- **Other shell usage:** on two calls I piped an `observe` through `sed -n` to print only the hand/enemy sections and keep the transcript small (`... observe 2>&1 | sed -n '/## Your hand/,/## The other side/p'` and one variant). No other shell commands were run. I did not create a scratchpad notes file; all notes were kept in-context.
- **Repo files read: none.**
