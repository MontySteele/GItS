# Blind seat record — KLEEMOD-KLEE, lane 1, act 2

## Identity

- **Model / seat:** Claude Opus 5 (`claude-opus-5[1m]`), blind TESTER seat, lane 1.
- **Run:** Klee round 10, run 5, act 2 — the second of chained seats. Seed not printed
  by any screen I saw; I never went looking for it.
- **Character:** Klee (bomb / Spark / Pyro kit).
- **Act:** 2. Map header printed `At the top of this act: **Knowledge Demon**`.
  I never reached the boss.
- **Neow pick:** none, inherited. I did not make this run's Neow pick; I picked up
  the lane on the act-2 map with the previous seat's deck, relics and potions.
- **Actions accepted:** 199 `act` calls issued, of which **198 accepted and 1 refused**
  (`choose "Clone"` → `error Rest site room is not open`, fired one call too early;
  it succeeded on the immediate retry). Cap was 250.
- **Termination reason:** **not a budget stop — the run ended.** I died on the
  act-2 elite (Entomancer) on floor 31. The next `observe` printed, verbatim:

  ```
  TOOL-BLOCKED: game_over

  the run is over; there is nothing left to play

  The run ended on floor 31.
  ```

  Per the brief I stopped there. The lane is **not** on the act-3 map.
- **HP trajectory:** 83/83 (first battle screen of act 2 — note the coordinator briefed
  me that act 1 ended at 39/83, so something between the act break and my first fight
  restored it; I never saw the screen that did) → 58 after fight 1 → 52 → 31 after
  fight 3 → rest to 60/88 → 41 → 39 → 20 → 15 → **9/88** after the first elite →
  rest to 40/93 → 10 → 5 after fight 5 → **dead on the second elite** at 5 HP with
  8 total mitigation against a printed 18.
- **Gold at the end:** ~121 (589 at the shop, 415 spent there, plus later rewards).
- **Potions held at the end:** Stable Serum (Retain your Hand for 2 turns). Spent
  during the run: Fire Potion (killed the Slumbering Beetle), Attack Potion (took
  Rapid Fire off it).
- **Relics at the end:** Pounding Surprise, Stone Humidifier, Mango, Amethyst
  Aubergine, Toxic Egg, Tea of Discourtesy, Vambrace, Pael's Growth, Gorget,
  White Star, Stone Cracker.
- **Deck at the end** (as printed across screens): Strike ×3, Defend ×3, Jumpy Dumpty,
  Ka-pow! (Sharp 2), Mine Toss, Mine Toss+, Sizzle ×2, Fish-Flavored Bait,
  Dodoco Cover, Big Badda Boom (Clone) ×2 — one of the pair printed as
  **Big Badda Boom+** — Fwoosh!, Dig In+, Sugar Rush+, Quick Fuse+ ×2,
  Powder Charge+, Safety Lesson, Careful Now+, The Big One+, Alice's Recipe.
  Spore Mind (curse) was removed at the shop.

### Non-combat picks, one sentence each

- **Pael (Ancient), `Pael's Growth` — "Enchant a card with Clone."** Picked over
  `Pael's Horn` ("Add 2 Relax to your Deck" — I had no idea what Relax was) and
  `Pael's Eye` (a conditional extra turn for ending a turn with no cards played,
  which my hand never wants to do); I put Clone on **Big Badda Boom** as the
  biggest single-card ceiling in a deck I had just seen for the first time.
  **The event never told me what Clone does.** I only learned it at the next battle
  screen: *"Clone — This card can be duplicated at Rest Sites."* I had guessed a
  combat effect; it is a rest-site option.
- **Self-Help Book, "Read the Back" → Sharp 2 on Ka-pow!.** Same gap: the event
  printed "Enchant with Sharp 2" and no definition. Ka-pow! is cost 0 and Retains,
  so it is the card I play most; the next combat confirmed Sharp 2 = +2 damage
  (Ka-pow! went 4 → 6). The selection list **omitted Big Badda Boom**, which is how
  I learned a card holds only one enchantment — never stated anywhere.
- **The Lost Wisp: took 58 gold** over "Add Decay to your Deck. Obtain the Lost Wisp",
  because a shop was two floors away and I could not see what the Lost Wisp did.
- **Shop (589 gold):** Safety Lesson 73, Powder Charge+ 78, Quick Fuse+ 50,
  Stable Serum 77, Card Removal 75 (removed Spore Mind), Gorget 166, Sizzle 25.
- **Card rewards:** Quick Fuse+, Mine Toss+, Careful Now+, The Big One,
  Alice's Recipe; skipped the last one to keep the deck thin.
- **Rest sites:** Rest (31→60, +5 max), Clone (duplicated Big Badda Boom),
  Rest (9→40, +5 max).
- **Treasure:** White Star.

---

## Fight 1 — Tunneler, HP 87

**Round 1.** Hand: Big Badda Boom (2), Fwoosh! (1 Spark), Sugar Rush+ (2 Sparks,
printed `CANNOT BE PLAYED: you have 1 Spark, and this costs 2`), Sizzle (1),
Strike (1). No bombs on the enemy, so every "Set off" clause was dead text.
Played **Big Badda Boom → Strike** for 18 (87 → 69, exactly as printed).
*Rejected:* Sizzle instead of Strike — identical 6 damage with a dead rider, so
I discarded the one whose rider might matter later. *Rejected:* Fwoosh! for 6 more
— it spends the Spark I was banking toward Sugar Rush+, and its Set off was also dead.
**This is a turn with no real decision in it:** with no bomb on the board, every
card in the hand was a vanilla number and the only question was arithmetic.

**Round 2.** Enemy intent: Empower + Defend, no attack. Played **Dodoco Cover**
(Bomb 4, Block), then **Strike ×2** (12).
*Rejected:* the two Defends — the intent printed no attack, so block would rot.
*Rejected:* holding the Strikes because it intended to Defend — I read Defend as
happening *on its turn*, i.e. after mine, so my attacks would land first. They did.
**Screen honesty, noted:** before I played anything, both Defends and Dodoco Cover
printed **"Gain 10 Block"** — Vambrace's doubling folded into the preview. The moment
Dodoco Cover consumed Vambrace, the two Defends re-printed as **"Gain 5 Block"**.
The preview was correct both times.

**Round 3.** Enemy at 57 with **Block 32** and `Burrowed 1 — Block is not removed at
the start of Tunneler's turn. Stunned if all Block is removed.` Bomb 8 sitting on it.
I read the Bomb keyword — *"Not an Attack: only their Vulnerable and a cap move it"* —
as meaning bomb damage ignores Block. Played **Jumpy Dumpty** (Bomb 8, total 2 bombs
= 16) then **Ka-pow!** to set off.
**The screen and the outcome disagreed with my reading, not with itself:** its HP
did not move at all (57 → 57) and its Block went 32 → 12, so the 16 bomb damage and
Ka-pow!'s 4 were all eaten by Block. The keyword line is about *damage modifiers*,
not about Block, and I mis-read it; it is the most natural mis-read available and it
cost me a turn. Sparks went 1 → 3, matching Pounding Surprise at 1 per bomb.
Then **Mine Toss** (Mine 4), **Dig In+** (11 Block), **Spore Mind** (the curse prints
`cost 1, curse / Exhaust` and is playable, so I paid 1 energy to bin it).
*Rejected:* setting off the fresh Mine with a second payoff — a Mine goes off for free
when the enemy attacks, so spending a card on it is pure waste.

**Round 4.** Enemy Block down to 5. Played **Strike** first, deliberately, to strip the
last Block and fire `Burrowed`'s stun clause. It worked: intent flipped to
`Stunned (Stun) — This enemy can't act on its next turn.` Then **Fish-Flavored Bait**
and **Jumpy Dumpty** to bank Bomb 12 across two bombs.
*Rejected:* Fwoosh! for an immediate 18-damage set-off — bombs grow 4 each per turn
and a stunned enemy cannot re-Block, so waiting one turn was worth ~8 free damage.
**This is the best decision the kit gave me all round** and it was legible: the stun
clause, the growth clause and the Block interaction were all printed on screen.

**Round 5.** Bombs at 20. Played **Dodoco Cover** (→ 24 across 3 bombs), **Sizzle**
(set off), **Ka-pow!**, **Strike**. I predicted 40; it dealt **43** (52 → 9).
The three points are Jumpy Dumpty's rider: its bomb going off placed a Mine 3, and
Ka-pow!'s *second* Set off in the same turn detonated that Mine immediately.
Sparks +4 rather than +3 confirms four detonations. **The chain is real and pleasant,
and nothing on screen advertises that a rider-placed Mine is live inside the same turn.**

**Round 6.** Enemy at 9 and Defending. **Sugar Rush+** (2 Sparks → 3 Energy, draw 1)
drew Big Badda Boom; played it for the kill.
*Rejected:* Strike for 6 into a 9-HP enemy that was about to gain Block — one short.

---

## Fight 2 — Exoskeleton ×3, HP 27 / 24 / 25, each with `Hard To Kill 9`

`Hard To Kill 9 — Reduce all damage taken and HP lost by Exoskeleton to 9.`
This is the cap the Bomb keyword mentions, and it inverts the kit: because Set off
detonates every bomb **one at a time**, three Bombs of 6 beat one Bomb of 18.

**Round 1.** Played **Fish-Flavored Bait → Strike → Sizzle**, all on Exoskeleton (2),
for exactly 20 (24 → 4).
*Rejected:* **Big Badda Boom.* Its printed 12 caps to 9, and its "damage equal to what
the Bombs dealt" rider caps too, so 2 energy bought strictly less than two 1-cost
attacks. **That is a genuine, printed-text decision and it is the best moment in
this fight.** Then **Sugar Rush+**, which drew Big Badda Boom — spent on the 4-HP
Exoskeleton to remove the 8-damage attacker, wasting 5 of its 9.

**Round 2.** Two left, one with Strength 2. Played **Defend → Defend → Mine Toss →
Ka-pow!** on the Strength one.
*Rejected:* skipping block for a third attack — 18 incoming against 55 HP said no.
Ka-pow! printed `(Sharp 2) … Deal 6 damage`, confirming the enchantment.

**Round 3.** Both enemies on Empower, no attack. Played **Jumpy Dumpty → Dodoco Cover
→ Fwoosh!** on the wounded one: two bombs of 8 and 4, each under the cap, set off for
12, plus 6 — 18 total, exactly killing a 15-HP body. Then **Strike** on the survivor.
*Rejected:* blocking on a turn with no printed attack.
**Something I could not reconcile:** after that kill the survivor printed
`Bomb 6 … Bombs here: 2, including 2 Mines`. I can account for one Mine 3 (Jumpy
Dumpty's rider, "place a Mine 3 on ALL enemies"). I cannot account for the second.
No screen I read explains it.

**Round 4.** Survivor at 17 with `Bomb 14 … Bombs here: 2` (7 + 7, both under the cap).
**Big Badda Boom** for 14 + 9 + 9. Kill.

---

## Fight 3 — Bowlbug (Rock) 48 / Bowlbug (Silk) 41 / Slumbering Beetle 86

The Beetle printed `Block 15`, `Plating 15` and
`Slumber 3 — Awakens upon taking turns or losing HP 3 times`.
I planned the whole fight around not waking it, then watched Slumber tick 3 → 2 → 1
on its own while it slept: **"taking turns" includes sleeping turns**, so the clause
that reads like a threat you control is actually a timer you do not. That is the one
piece of text in the round I would call misleading rather than merely unexplained.

**Round 1.** Rock printed `Imbalanced 1 — If Bowlbug (Rock)'s attacks are fully
blocked, it becomes Stunned` and an attack of 15. Defend showed 10 (Vambrace) and
Gorget's Plating 4 would add 4 at end of turn — **14, one short of the 15 needed to
fire the stun**, with no third block source in hand. Played **Defend →
Fish-Flavored Bait → Sizzle** on Rock (14 damage, 1 taken).
*Rejected:* the full-damage line (FFB + Sizzle + Strike, 20 damage) — 6 extra damage
for 10 extra HP in a three-enemy fight was a bad trade.
**The one-short arithmetic is the decision of the fight and it is entirely legible.**

**Round 2.** Both Bowlbugs would attack. Played **Mine Toss+ → Mine Toss** (Mines 7
and 4 on ALL) then **Jumpy Dumpty** and **Powder Charge+** on Rock.
*Rejected:* any block — I had none in hand, so the choice was between banking mines
that auto-fire before their hits and doing nothing. Took 20 (51 → 31); the mines
returned 11 to each Bowlbug for free on their turn.
Note the Beetle received mines too and took nothing, because placement is not damage
and a sleeping enemy never attacks to trigger them.

**Round 3.** Rock at 23 with `Bomb 25` on it. Played **Safety Lesson** (power:
2 Block per bomb going off), then **Quick Fuse+** — "Each Bomb on the enemy grows by 6.
Set off." — two bombs → +12 → 37 damage into a 23-HP body. Dead. Then two Defends.
Result: Rock killed and **zero damage taken**.
*Rejected:* a second Quick Fuse+ on the Beetle — it would have burned the mines I
wanted auto-firing later, and Silk had no bombs at all so Quick Fuse there is a blank.

**Round 4.** Beetle awake, 16 incoming, Silk 4×2. Played **Dig In+ (11) → Dodoco Cover
→ Ka-pow! → Fwoosh! → Sugar Rush+**, then Strike. Held the Beetle's four Mines (41)
unspent so they would fire on its own attack.
They did: it took 41, its Block 13 evaporated, and Safety Lesson turned four
detonations into 8 Block *before* the hit landed. **I took 0 from a printed 24.**
This is the single best turn the kit produced and every part of it was readable off
the screen: Mine timing, Safety Lesson, and Plating stacking.

**Round 5.** Beetle 45, Silk 11, me 31. Played **Quick Fuse+** (14) → **Big Badda Boom**
(12) → **Fire Potion** (20) to kill the Beetle outright, then **Sizzle** on Silk.
*Rejected:* saving the Fire Potion for the boss and finishing the Beetle next turn.
The line without the potion left me at ~13 HP needing 24 damage across two bodies on
one draw; I bought 18 HP for a potion I never reached the boss to use anyway.

**Round 6.** **Fish-Flavored Bait → Sizzle** for the kill.

---

## Fight 4 (elite) — Infested Prism, HP 161, `Vital Spark 2 — ALL Skills are Tainted 2`

**The keyword that decides this fight is never defined until you have already paid
for it.** Every skill in my hand printed "Gain 2 Tainted" and nothing on the screen —
not the card, not the enemy block, not the glossary at the foot of the page — said
what Tainted does. I spent a card to find out: after playing Mine Toss+ my status read
`Tainted 2 (debuff) — Take 2 additional damage from Attacks this turn`, and the enemy's
intent number ticked 15 → 17 in the same beat. **The live intent update is excellent;
the missing definition beforehand is the defect.**

**Round 1.** After the test, played **Jumpy Dumpty → Mine Toss → Quick Fuse+**:
three bombs grown +6 each to 37, set off for 37, plus the rider Mine for 3. 161 → 121,
20 taken.
*Rejected:* Jumpy Dumpty + Sizzle (21 damage, 15 taken). Quick Fuse's growth clause
turned 4 extra HP into 16 extra damage.

**Round 2.** It intended 11 + Defend. Played **Dodoco Cover → Powder Charge+ →
Big Badda Boom**: bombs 13, set off 13 + 12 + 13 = 38, and 10 Block against a
Tainted-inflated 15. 121 → 83, **2 taken**.
*Rejected:* Strike — no energy left and it was the worst card in the hand.

**Round 3.** It now sat behind **Block 11** and intended **5×3**. Tainted revealed its
teeth here: my Defend printed "Gain 5 Block. Gain 2 Tainted", and Tainted applies
**per hit**, so the intent went 5×3 → **7×3**. Defend was worth +5 block and +6 damage —
**a block card that is strictly negative to play.** I did not play it.
*Rejected:* Defend, for that reason. Played **Safety Lesson** (a power, and the card
correctly printed no Tainted line — powers are exempt), **Sugar Rush+**, then
**Sizzle → Big Badda Boom** for 7 through Block. Took 19 → 20 HP.
This is the turn where the fight stopped being winnable on tempo.

**Round 4.** It intended only 8. Played **Fish-Flavored Bait → Fwoosh! → Strike**
(20 damage) and **retained Ka-pow! and Careful Now+**.
*Rejected:* spending Ka-pow! for 6 now — it is cost 0 and Retains, so keeping it is a
guaranteed free Set off next turn, which is exactly what a bomb deck wants banked.

**Round 5.** Me 15, it 56 behind **Block 20** with `Vital Spark 4` — every skill now
costs 4 Tainted. Kill was arithmetically impossible (76 needed). The whole turn was one
optimisation: **how many skills can I play before Tainted outruns the Block they buy?**
- 0 skills → 15 damage, 0 block → dead.
- 1 (Dig In+) → 19 damage, 11 block → 7 HP left.
- 2 (+ Defend) → 23 damage, 16 block → 8 HP.
- 4 (+ Powder Charge+ → Careful Now+, whose block equals my largest Bomb) →
  31 damage, 25 block → **9 HP**, and a Bomb 9 left planted.
Played all four. Landed on 9 HP exactly as computed.
**This is the sharpest puzzle the round produced** — a debuff that makes defence
self-defeating, solved by noticing that block scales faster than Tainted as long as
each skill is worth more than 4.

**Round 6.** Its Block cleared, 56 HP, Bomb 13 planted. **Jumpy Dumpty** (→ 21 across
two bombs) → **Big Badda Boom** (21 + 12 + 21 = 54) → **Ka-pow!** on the rider Mine
for the last 2. Elite dead at 9 HP.
*Rejected:* leading with Big Badda Boom — it deals 50 without the extra bomb, and 50
is 6 short. The bomb-first ordering is the whole kill.

---

## Fight 5 — Spiny Toad, HP 117, `Thorns 5`

**Round 1.** It only Empowered. Played **Mine Toss+ → Powder Charge+ → Strike →
Defend**, banking Mine 7 + Bomb 9 rather than cashing them.
*Rejected:* Mine Toss+ / Powder Charge+ / Big Badda Boom+ for 48 immediately —
with no damage incoming, one turn of growth turned 16 bomb-points into 24.

**Round 2.** It printed `Thorns 5 — When hit by an attack, deal 5 damage back`.
This is the second cap-like clause that rewards the kit: **bombs are not attacks, so
they do not wake Thorns; only the payoff card does.** Played **Jumpy Dumpty** then
**Big Badda Boom** — 32 bomb-points set off, then 12, then 32 again: 76 damage,
117 → 35.
*Rejected:* Safety Lesson + Big Badda Boom (60 damage, 4 block) — 16 more damage was
worth more than 4 block at that HP.
**Screen versus outcome, the clearest disagreement of the round:** I budgeted 5 HP for
Thorns and lost 10. Big Badda Boom's two damage clauses ("Deal 12" and "deal damage
equal to what the Bombs dealt") each count as a separate attack instance and each
took 5 back. Nothing printed says the second clause is a second attack — the card
reads as one hit with a rider. 40 HP → 10 HP instead of the 15 I had planned for.

**Round 3.** Me 10, it 26, Thorns **no longer listed** on its status. Played
**Defend → Defend** first, then **Fwoosh!** as a probe, and watched my HP: it did not
move, so Thorns really had expired and the status line was telling the truth by
absence. Then **Attack Potion** → took **Rapid Fire** (3×4 = 12) over Pocket Fireworks
(9) and Perfect Timing (8), and played it free.
*Rejected:* Careful Now+ — "Gain Block equal to your largest Bomb" with no bomb on
the board is a blank card, and the screen said so plainly enough by printing the
clause rather than a number.

**Round 4.** It Empowered; **Sizzle → Sizzle → Ka-pow!** for the kill.
Skipped the card reward (Ammo Scavenging+, Quick Fuse+, Witches' Circle+, Shinobu) to
keep a 26-card deck from getting worse at finding The Big One+.

---

## Fight 6 (elite) — Entomancer, HP 145 — the run ends here

The map gave me exactly one node out of the last rest site — **Elite** — at 5 HP.
There was no route around it.

`Personal Hive 1 — Whenever this enemy is hit by an Attack, add 1 Dazed into your
Draw Pile.` A third clause that a bomb deck answers cleanly: bombs are not attacks,
and Quick Fuse+ is a *skill* that sets them off, so the kit has a genuine
Dazed-free damage line. I never got to use it twice.

**Round 1.** Intent 3×7 = 21. **Dig In+** printed **"Gain 22 Block"** — Vambrace
doubling an 11 — which with Gorget's Plating 4 covered 21 exactly. Played
**Dig In+ → Mine Toss+ → Jumpy Dumpty**, banking Mine 7 + Bomb 8.
*Rejected:* Fish-Flavored Bait — it is an attack, and one Dazed shuffled into a
26-card deck at 5 HP is a real cost.
Took **0** from a printed 21.

**Round 2.** Intent **18**, single hit. My hand: Sizzle, Defend, Strike, Ka-pow!,
Quick Fuse+. Total mitigation available: **Defend 5 + Plating 3 = 8.** Nothing else
in hand, no Careful Now+, no second Dig In+, no healing relic (I re-read the relic
list to be sure — Stone Cracker turned out to be
"Upgrade 2 random cards in your Draw Pile for the rest of combat", not a save).
18 − 8 = 10 against 5 HP. **There was no surviving line and the screen said so
plainly** — I could read my own death off the intent number and the block arithmetic
before I played a card.
Played the maximum-damage turn anyway — **Defend → Quick Fuse+ (18) → Sizzle →
Strike → Ka-pow!**, 36 damage, 138 → ~102 — and ended the turn.
*Rejected:* nothing, honestly. There was no alternative to reject; that is the point.
The next `observe` printed `TOOL-BLOCKED: game_over`.

**Where the loss actually happened:** not here. It happened in fight 5 round 2, where
Big Badda Boom cost me 10 HP of Thorns instead of the 5 the card reads as, and in
fight 4 round 3, where `Vital Spark` made my only block card negative to play. I
arrived at the last elite at 5 HP with a deck that could deal 76 damage in a turn and
could not gain 15 block in one.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The kit's real decision, and it is a good one, is **bank or cash**: bombs grow 4 a turn
and only pay when a Set off card converts them, so every turn asks whether to spend the
payoff now or let the pile compound. It is a genuine trade because the enemy's intent
prices it — banking against a stunned Tunneler was free, banking against the Spiny
Toad's 23 cost me 20 HP. Three enemy clauses sharpened it further, and all three are
excellent design:

- **`Hard To Kill 9`** inverts bomb sizing. Because Set off detonates bombs *one at a
  time*, three small bombs beat one big one, and Big Badda Boom — the deck's best card —
  becomes its worst. Choosing three 1-cost attacks over the 2-cost bomb payoff was the
  most satisfying read of the round.
- **`Thorns 5`** and **`Personal Hive`** both punish *Attacks* and ignore *Bombs*,
  which makes "which of my damage sources is technically an attack" a live question and
  rewards Quick Fuse+ (a skill that sets off) over Ka-pow!/Sizzle/BBB.
- **`Vital Spark` / Tainted** makes defence cost damage, so the turn becomes an
  optimisation rather than a reflex: I worked out that 4 skills beat 1 skill beat 0
  skills, and landed on the exact HP I predicted.

Below that, the **Spark economy** is a good second currency: Pounding Surprise pays a
Spark per detonation, so a big set-off turn refunds the Sparks that Fwoosh!, Dig In+,
Powder Charge+ and Quick Fuse+ want. Twice I chose to bank a Spark toward Sugar Rush+
instead of spending it on 6 damage, and twice that was right.

**(b) What felt automatic, and what never seemed worth playing.**

**Strike and Defend are pure filler** and never presented a decision — the only
question they ever posed was arithmetic. **Fish-Flavored Bait** (4 damage, Bomb 4) was
consistently the weakest bomb placer once Powder Charge+ and Mine Toss+ existed, and
against `Personal Hive` it was actively bad. **Fwoosh!** is a strictly worse Ka-pow!
in most spots: same 6 damage, but it costs a Spark and does not Retain.

The automatic turns were all the same shape: **a hand with no bomb on the board and no
placer in it**, where every "Set off" clause is dead text and the cards collapse into
vanilla numbers. That was fight 1 round 1, and it is exactly the answer to (e) below.

**(c) What I could not understand, or that seemed to contradict its own printed text.**

1. **Enchantments are sold before they are defined.** "Enchant a card with Clone" and
   "Enchant with Sharp 2" are both *choices you make* with no printed meaning attached.
   I learned Clone means "duplicable at Rest Sites" one room later, from a battle
   screen. That is a pick made blind inside a game that otherwise prints everything.
2. **`Tainted` is the same defect with teeth.** Every skill in the Infested Prism fight
   printed "Gain 2 Tainted" with no glossary entry anywhere on the screen. I had to
   spend a card to discover it means "+2 damage per attack instance this turn". In a
   fight where that number decides whether your block card is worth playing, learning
   it by experiment is a real cost.
3. **Big Badda Boom is two attacks, printed as one.** "Set off. Deal 12 damage. Then
   deal damage equal to what the Bombs dealt." Against Thorns 5 that cost me 10, not 5.
   Nothing on the card suggests the rider is a separate attack instance.
4. **The Bomb keyword's "Not an Attack" line reads as Block-piercing and is not.**
   *"Not an Attack: only their Vulnerable and a cap move it"* is about damage
   *modifiers*, but the natural reading is "bypasses Block", and I burned a 16-point
   detonation into 32 Block finding out. One clause saying bomb damage is still
   absorbed by Block would fix it.
5. **`Slumber 3 — Awakens upon taking turns or losing HP 3 times`** reads as a
   threat under my control. It is not: sleeping *is* taking a turn, so the counter
   ran down on its own while I carefully avoided touching it.
6. **Unexplained:** after fight 2 round 3, the survivor showed
   `Bombs here: 2, including 2 Mines` when Jumpy Dumpty's rider accounts for only one.
7. **Cosmetic:** at fight 5 the two Cloned copies printed as **Big Badda Boom** and
   **Big Badda Boom+** — I never saw the screen that upgraded one of them, though
   Stone Cracker ("Upgrade 2 random cards in your Draw Pile for the rest of combat")
   is the likely and reasonable cause.

Against all that, the things the screen got **right** deserve saying, because they are
the reason most of these fights were decidable: Vambrace's doubling shows in the card
preview and drops out the instant it is consumed; Weak re-prints Strike as 4; Tainted
re-prints the enemy's intent live (5×3 → 7×3); Powers correctly print no Tainted line
where Skills do; `CANNOT BE PLAYED: you have 1 Spark, and this costs 2` and
`CANNOT BE PLAYED: no enemy is holding a Bomb` are model refusals; and Thorns
disappearing from the status block was trustworthy enough to bet 5 HP on.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Defend.** Filler at best, and in the Infested Prism fight it was
*strictly negative* — 5 block for 6 extra incoming. A block card you must decline to
play is a memorable failure state, and I mean that as praise for Vital Spark and
criticism of Defend.

Happiest to draw: **Quick Fuse+.** "Each Bomb on the enemy grows by 6. Set off." for
one Spark and no energy. It grows and cashes in one card, costs the resource my relic
refunds, and is a *skill*, which dodges Thorns and Personal Hive entirely. It killed
Bowlbug (Rock) from 23 through a 37-point detonation and it was my whole last turn
alive. Honourable mention to **Ka-pow!** — cost 0, Retains, and the round-5 discovery
that its Set off fires rider-placed Mines *within the same turn* is the kit's most
pleasant hidden interaction.

**(e) Did the first turn of the first fight already present a decision?**

**No.** Fight 1 round 1 opened with Big Badda Boom, Fwoosh!, Sugar Rush+ (unplayable,
1 Spark of 2), Sizzle and Strike against a bare Tunneler. With no bomb on the board,
Big Badda Boom's "Set off" and "damage equal to what the Bombs dealt" were both dead,
Sizzle's Set off was dead, and Fwoosh!'s Set off was dead — three of five cards were
printing text that did nothing. The turn reduced to "which 3 energy of vanilla damage
is largest", and the answer was forced. The kit's first *actual* decision arrived in
round 3, and its first *good* one in round 4.

To be fair to the deck: this is a hand-shape problem, not a kit problem. A round-1 hand
holding Jumpy Dumpty or Mine Toss+ is immediately interesting. But the opening hand I
was dealt had four payoff cards and one placer, and a deck whose payoffs outnumber its
setup will keep dealing that turn.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside the two allowed ones, all through the Bash tool:

- `mkdir -p <scratchpad>` and `echo "<n>" > <scratchpad>/actcount.txt` — the running
  accepted-action counter the coordinator asked for. Written before/after `act` calls
  throughout.
- `cat > <scratchpad>/obs.sh <<'EOF' … EOF` — wrote a two-line helper that runs
  `GITS_LANE=1 python -m understudy.blindplay observe` and pipes it through `sed` to
  strip the repeated glossary block, so I could re-read a screen without re-reading
  the elemental-reaction table forty times. It adds nothing and hides nothing that
  changed between turns; every line it removed was static keyword text I had already
  read in full.
- `sh <scratchpad>/obs.sh` and `GITS_LANE=1 python -m understudy.blindplay observe`
  piped through `sed`/`head`/`tail` — same purpose: trimming the printed screen to the
  sections that had moved. Output was never redirected away from my own view; where I
  wrote `>/dev/null` it was on an `act` call whose result I read on the very next
  `observe`.
- `for c in …; do … done` shell loops — these only batch several `act` calls into one
  Bash invocation. Each loop iteration is one ordinary `act`, counted in the total.

Tools used: **Bash** (above), and **Write** once, for this record, at the path the
coordinator gave. No `harness state`, no `scenario`, no `staged_turn`, no `soak`, no
other understudy subcommand. I did not read any YAML sheet, C# source, doc, packet,
review file, or any other seat's record, and I did not open any other file in
`review/qa/klee-round-10-2026-09-04/`.
