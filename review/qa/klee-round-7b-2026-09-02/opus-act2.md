# Blind seat record — KLEEMOD-KLEE, lane 2, act 1 finish + act 2 opening

## Identity

- **Model / seat:** Claude Opus 5 (1M context), blind TESTER seat, round 7b, second seat.
- **Lane:** 2 (`GITS_LANE=2 python -m understudy.blindplay`).
- **Character:** KLEEMOD-KLEE. **Act-1 boss:** Ceremonial Beast. **Act-2 boss named by the map:** **The Insatiable**.
- **Picked up at:** act 1, 7 floors cleared, 9 floors to the boss, **HP 23/62**, on the map screen the previous seat left (`Unknown (path 1)` / `RestSite (path 2)`).
- **Stopped at:** act 2, 3 floors cleared, **HP 36/62**, on the **card-reward screen after act-2 fight 2** (the four cards are listed in §4; I did not have the budget left to pick one). The lane is left standing on that screen.
- **Actions accepted:** **150 accepted `act` calls, 0 refused.** No `TOOL-BLOCKED`, no refusal streak, no repeated-screen stop.
- **Termination reason:** act-call budget (150) exhausted. Wall clock was not close to the limit. The act-1 boss **was** beaten; the act-2 boss was not reached (16 floors ahead of the act-2 start).

**Fights this session:** 6 — numbered on from the previous record as **Fight 7 … Fight 12**, and the act-1 boss is Fight 10.

**HP trajectory** (every reading the screens printed, in order):

23 → **41** (rest) → 46 (Planisphere on the ? room) → **55** (event "Consume", heal 9) → *elite:* 55 → 38 → 37 → 37 → won at 37 → *fight 8:* 37 → 30 → 27 → won at 27 → *fight 9:* 27 → 22 → won at 22 → 27 (Planisphere on the shop) → **45** (rest) → *boss:* 45 → 45 → 35 → won at 35 → **62/62** (full heal on entering act 2) → *fight 11:* 62 → 62 → 62 → 47 → won at 47 → 52 (Planisphere) → *fight 12:* 52 → 49 → 36 → won at **36/62**.

**Gold.** The shop screen printed the first running total this run has ever shown: **325 gold** on arrival. Spent 206 (Candelabra) + 75 (Card Removal) = 281, leaving 44. Then +100 (boss) +19 +20 = **183 gold** at the stop.

**Potions at the end:** `Dexterity Potion — Gain 2 Dexterity.`, `Skill Potion — Choose 1 of 3 random Skill cards to add into your Hand. It's free to play this turn.`, `Flex Potion` (claimed on the last reward screen; its text never printed). Spent: `Poison Potion — Apply 6 Poison.` (fight 11, round 3).

**Relics at the end, exactly as printed:**

- **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark. Card rewards after a fight offer a fourth Companion choice.
- **Hefty Tablet** — Upon pickup, choose 1 of 3 Rare cards to add to your Deck, and add 1 Injury to your Deck.
- **Planisphere** — Whenever you enter a ? room, heal 5 HP.
- **Vexing Puzzlebox** — At the start of each combat, add a random card into your Hand. It's free to play this turn.
- **Twisted Funnel** — At the start of each combat, apply 4 Poison to ALL enemies.
- **Candelabra** — At the start of your 2nd turn, gain [Energy][Energy].
- **Very Hot Cocoa** — Start each combat with an additional 4[Energy].

**Deck at the end — 23 cards.** This one is *not* reconstructed: the Sapphire Seed upgrade screen and the shop's Card Removal screen both printed the whole deck, and the piles (18 draw + 5 real cards in hand at the start of fight 12) check out.

- **Strike** ×4 — cost 1, attack. "Deal 6 damage."
- **Defend** ×4 — cost 1, skill. "Gain 5 Block."
- **Jumpy Dumpty+** (upgraded) — cost 1, skill. "Place a Bomb 11. When it goes off, place a Mine 4 on ALL enemies."
- **Ka-pow!** [Pyro] — cost 0, attack. "Retain. Set off. Deal 4 damage."
- **Sparks 'n' Splash (proto)** — cost 2, power. "At the end of your turn, deal Pyro damage to a random enemy equal to the Bombs on it."
- **Pop!** — cost 0, skill. "Place a Bomb 5."
- **Fish-Flavored Bait** [Pyro] — cost 1, attack. "Deal 4 damage. Place a Bomb 4."
- **Grounded** — cost 1, power. "At the start of your turn, if none of your Bombs went off last turn, gain 6 Block."
- **Thoma — Blazing Barrier (proto)** — cost 1, skill. "Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block."
- **Charlotte — Framing: Freezing Point Composition** [Cryo] — cost 1, attack. "Deal 4 damage. Draw 1 card."
- **Ammo Scavenging** ×2 — cost 1, skill. "Place a Bomb 4. Draw 1 card for each of your Bombs that went off this turn."
- **The Big One** [Pyro] — cost 3, attack. "Set off for quadruple damage." *(elite reward)*
- **Dig In** — cost 1 Spark, skill. "Gain 8 Block." *(fight 9 reward)*
- **Kamisato Ayaka — Soumetsu** — cost 2, skill. "For 2 turns, at the end of your turn deal 8 Cryo damage to ALL enemies. Then deal 16 Cryo damage to ALL enemies. Exhaust." *(boss reward, Companion)*
- **Barbara — Let the Show Begin♪ (proto)** [Hydro] — cost 1, skill. "Gain 6 Block. Apply Hydro." *(fight 11 reward, Companion)*
- **Spoils Map** — cost 0, quest. "Unplayable. Marks a site of 600 extra Gold in the next Act."

**Injury was removed** at the shop (Card Removal, 75 gold). `Spoils Map` did appear on the removal screen and I kept it, because it at least promises something in act 2 where Injury promises nothing.

---

## Fight 7 (Elite): Byrdonis — HP 81/81

Printed on it from turn 1: `Territorial 1 (buff) — At the end of Byrdonis's turn, it gains 1 Strength.` So every turn I spend costs me more HP than the last — a clock, stated plainly, and it changed how I played.

**Turn 1.** Vexing Puzzlebox had put `Sizzle` in my hand at cost 0 ("The cost printed on this card is 1; it is showing 0 here"). Sizzle reads "Set off. Deal 6 damage." I played it **first, before any bomb existed**, so its Set off hit an empty board and I banked 6 free damage. Then `Jumpy Dumpty+` (Bomb 11) → `Fish-Flavored Bait` (4 damage, Bomb 4) → `Grounded`. **Rejected:** playing Sizzle *after* the bombs — that would have converted a 15 stack into 15 damage and switched Grounded off before it ever ticked. Also rejected `Charlotte` in Grounded's slot: 6 Block a turn for the rest of a long fight beats 4 damage once. Real decision, and the ordering trick is only visible because the screen prints Set off's wording where you can read it against an empty board.

Outcome: 81 → 71 (6 + 4, exact). `Bomb 15 (buff) ... Bombs here: 2`. Took the full 17.

**Turn 2.** Bomb 23. `Sparks 'n' Splash (proto)` (2) + `Defend` (1). **Rejected:** `Ka-pow!` for 23 + 4 = 27 immediately. The power reads the stack without spending it, so holding converts the same 23 into 23 *per turn*. Also rejected `Strike` over `Defend`. Tick landed **exactly 23** (71 → 48). The badge and the outcome agreed to the point.

**A screen-vs-outcome note.** The intent read `4x3` with `Strength 1` showing, and I took exactly 12 through 11 Block, i.e. **1**. So the printed per-hit number already includes Strength; the screen is honest and I had over-estimated the damage. Worth saying because I got this *wrong in my head* and the screen was right.

**Turn 3.** Byrdonis 48, Bomb 31, 19 incoming. `Ammo Scavenging` (Bomb 4 → 35) → `Thoma` → `Defend`. **Rejected:** `Ka-pow!` for 35 — identical damage this turn, but it empties a stack that would tick 35 again next turn and it turns Grounded off. Result: **0 damage taken** (Thoma + Defend + Grounded ate all 19), tick 35, Byrdonis to 13.

**Turn 4.** Bomb 47 vs 13 HP. `Ka-pow!` — free, immediate, lethal, and it denies the 20 that was pointed at me. **Rejected:** ending the turn and letting the tick do it — same kill, but I'd have eaten 20 first. The elite cost me **18 HP total** and never got a third attack in.

---

## Fight 8: Vine Shambler — HP 61/61

**Turn 1.** Puzzlebox gave `Big Badda Boom` at 0 ("printed 2"): "Set off. Deal 12 damage. Then deal damage equal to what the Bombs dealt." Same trick as Sizzle — played first, into an empty board, for a clean 12. Then `Sparks 'n' Splash (proto)` (2) + `Defend` (1). **Rejected:** `Grounded` in the power slot — I had *no bomb-placer in hand at all* this turn, so the engine card was the one worth installing on the cheap turn. **This hand is a finding on its own: six cards, not one of them placed a bomb.** 61 → 45 (12 + 4 poison, exact).

**Turn 2.** `Pop!` (0) + `Fish-Flavored Bait` (1) → stack 9; `Defend` + `Strike`. **Rejected:** two Strikes instead of Defend + Strike — 6 more damage for 5 more HP, and at 30/62 with a boss ahead the HP was worth more. Real, if small.

**Turn 3 — the turn a new keyword bit.** The screen opened with `Tangled 1 (debuff) — Attacks cost an additional [Energy] this turn.` My hand re-printed itself accordingly: **`Ka-pow!` now read "cost 1"** (it is a 0-cost card) and **`The Big One` read "cost 4" with "CANNOT BE PLAYED: you do not have enough energy."** That is exactly right and exactly legible — the debuff is shown *on the affected cards*, not just in a status line. Very good.

Shambler at 23, Bomb 17, 16 incoming. Played `Jumpy Dumpty+` (stack → 28), `Thoma`, `Defend`. **Rejected:** the Ka-pow! line (17 + 4 = 21, leaves it alive at 2 and burns the stack). The tick did 28 into 23 and killed it before its 16 landed. **Rejected:** also, holding the block cards — I played them as insurance in case the tick chose badly, which cost nothing since a card left in hand is discarded anyway.

---

## Fight 9: Twig Slime (M) 27/27, Leaf Slime (M) 35/35, Twig Slime (S) 7/7, Leaf Slime (S) 12/12

Four enemies. `Twisted Funnel` opened with `Poison 4` on all of them, which turns out to matter a lot: poison is *per enemy*, so a wide fight is where that relic pays.

**Turn 1.** Puzzlebox gave `Powder Charge — cost 1 Spark, skill. Place a Bomb 6.` I had Spark 1, so it was free in the sense that mattered. Played it and `Jumpy Dumpty+` and `Fish-Flavored Bait` all onto **Leaf Slime (M)** (35, the biggest), then `Strike` into **Twig Slime (S)** (7 → 1) so that poison would finish it *at the start of its turn, before it attacked*. **Rejected:** Strike into Leaf Slime (S) instead — 12 HP is out of one-Strike-plus-poison range, whereas Twig Slime (S) was exactly in range, so the same card bought a kill instead of a dent. **Rejected:** `Defend` — the only attacker on the board was the 4-damage slime I was about to delete. This was the best-shaped turn of the session: the poison numbers, the HP numbers and the intents were all on screen and they picked the target for me.

It worked: Twig Slime (S) died to poison and never attacked.

**Turn 2 — the turn the kit's AoE finally showed up.** Leaf Slime (M) at 27 with `Bomb 33`, and 22 damage incoming across three bodies at 27 HP. `Ka-pow!` on Leaf Slime (M): the 33 killed it outright, and Jumpy Dumpty's rider fired — Mines on the survivors. Then `Ammo Scavenging`, which prints "Draw 1 card for each of your Bombs that went off this turn": **three bombs had gone off, and it drew exactly 3.** I played the second copy and it drew 3 again. That is the only card in the deck that turns a cash-out into a hand, and it is the reason detonating was correct here rather than ruinous. **Rejected:** holding the stack — with three enemies alive the tick is a 1-in-3 lottery and I was at 27 HP.

`Spark` went from (spent to 0) to **3** on the set off — Pounding Surprise pays **one per bomb**, not one per detonation, exactly as in the previous seat's fight 2.

Then `Pop!` and the second `Ammo Scavenging` onto **Twig Slime (M)**, `Thoma` with the last energy. **Rejected:** `Grounded` — bombs had gone off this turn, so its condition ("if none of your Bombs went off last turn") would pay nothing next turn. The card told me that plainly and I obeyed it.

**Where the screen and the outcome disagreed — the mine count, again, and worse.** One rider that says "place a **Mine 4** on ALL enemies" produced, on the same screen:

- `Twig Slime (M) — Bomb 8 ... Bombs here: 2, including 1 Mine` (Mine 4 + my Ammo bomb 4)
- `Leaf Slime (S) — Bomb 8 ... Bombs here: 2, including **2 Mines**`

**Two different mine counts on two enemies, from one "on ALL enemies" rider.** I could not derive either number from the card, and I could not derive the asymmetry from anything at all.

**Turn 3.** Leaf Slime (S) died on its own mines. Twig Slime (M) at 16 with Bomb 25. Hand was `Defend`, `Strike` ×3, `Sparks 'n' Splash`. Played three Strikes for 18. **Rejected:** `Sparks 'n' Splash` + one Strike, which is also lethal via the 25 tick — but installing a Power on the last turn of a fight is pure waste. Two lethal lines and a reason to prefer one is still a thin decision; I'll call it half a turn of decision.

**The damage arithmetic I could not close.** End of turn 2 I had Thoma's 6 Block up, and the board pointed 11 (Twig M, after a Mine 4 pre-hit) + 3 (Leaf S) = 14 at me. I took **5**. That is consistent with *both* "Leaf Slime (S)'s hit landed even though its own Mines killed it" and "it didn't land, and Thoma's +3 top-up covered the rest". **The previous seat's finding about "before the hit lands" is therefore neither confirmed nor refuted here** — but see Fight 11 below, where Thoma's block visibly did nothing at all, which makes the first reading the more likely one.

---

## Fight 10 (Act-1 Boss): Ceremonial Beast — HP 252/252

**Turn 1 — a free turn, and the kit knows what to do with it.** Intent `Empower (Buff)`. Puzzlebox gave `Rapid Fire` at 0 ("printed 2"): "Deal 3 damage to a random enemy 4 times. Set off each enemy hit." Third time this session that the free card was a detonator, and third time the right answer was **play it before placing anything**: into an empty board it is a clean 12. Then `Jumpy Dumpty+` (Bomb 11), `Pop!` (Bomb 5), `Strike`, `Thoma`. **Rejected:** placing first and then Rapid Fire — that line deals 28 this turn instead of 18 but hands back a 16 stack that would otherwise tick 24, 40, 60 on the following turns.

**Turn 2 — Candelabra paid and the boss showed its rule.** `Energy 5/3`. The board now printed `Plow 150 (debuff) — The first time Ceremonial Beast's HP reaches 150 or below, it becomes Stunned and loses all its Strength.` That is a boss mechanic stated as a number I can aim at, and it reorganised the whole fight: it turned "grind 252" into "race to 150". Played `Sparks 'n' Splash (proto)` (2) + `Ammo Scavenging` (1) + `Defend` + `Strike`. **Rejected:** `Ka-pow!` for 28 — same reason as every other turn; the tick reads the stack for free.

**Turn 3 — the reaction the card previewed.** Boss 193, Bomb 40, 20 incoming, `Plow` 43 damage away. `Charlotte` carried a `*Reaction preview: Melt*` line because my own bombs had left a Pyro aura, and it hit for **7** — 4 × 1.75, exactly as previewed (193 → 186). Then `Ammo Scavenging` (stack 44) and `Dig In` (8 Block for **1 Spark**, no energy) and `Defend`. **Rejected:** `Ka-pow!` again. The tick took the boss to 142, **Plow fired, the boss was Stunned, and it never took its turn** — my 13 Block was wasted and I was glad of it.

**Turn 4 — the payoff the deck was built for.** Boss 140, `Bomb 60 (buff) — Set off here deals 60 Pyro damage. Bombs here: 4.` I played **`The Big One`** (3 energy, "Set off for quadruple damage") and the fight ended on the spot. **Rejected:** the tick line (60 + a Strike + a Bait ≈ 70, not lethal, and another 20-plus turn taken to the face). This is the one turn all session where detonating was strictly right, and it was right by a factor of four.

**Badge vs outcome:** badge said 60, the card says quadruple, the boss had 140, and it died — so ≥140 landed off a badge that reads 60. The badge does not price the card that reads it.

**The boss cost me 10 HP across four turns** (45 → 35) and I never saw its second attack. Two of its four turns were a buff and a stun.

---

## Fight 11: Bowlbug (Rock) 48/48, Bowlbug (Nectar) 38/38

Act 2 opened at **62/62** — the act transition healed me to full — and at `Energy 7/3` (Very Hot Cocoa + base).

**Turn 1 — a debuff worth reading.** `Bowlbug (Rock)` printed `Imbalanced 1 (debuff) — If Bowlbug (Rock)'s attacks are fully blocked, it becomes Stunned.` My hand was four Defends, a Strike and a free `Catalytic Converter`. Incoming 15 + 3 = 18, so I played **four Defends for 20 Block** and it stuck: 0 damage, and `Intent: Stunned (Stun) — This enemy can't act on its next turn.` **Rejected:** blocking only the Rock's 15 exactly (three Defends) — the shared block pool means Nectar's 3 could have spilled and broken "fully blocked", and I could not tell from the screen whether the game resolves them separately. Paying one extra Defend to remove that uncertainty was the decision. `Strike` went into Nectar rather than Rock: fewer enemies makes my random-target tick deterministic sooner, which is the lesson act 1 taught.

**Turn 2 — no incoming, so a pure placement turn.** `Ammo Scavenging` ×2 onto the Rock, `Strike` into Nectar, `Thoma`. **Rejected:** splitting the bombs. With `The Big One` in the deck I want one big pile, and the Rock is both the bigger body and the 15-damage threat. No real block decision existed (nothing was attacking), so this turn was placement-by-rote.

**Turn 3 — the sharpest turn of act 2.** Nectar came out of its buff at **`Strength 15`**, intending 18, while the Rock pointed another 15: **33 incoming, and I had no block card in hand.** Nectar was at 19. I worked out that poison resolves at the start of *its* turn, so I did not need 19 damage, I needed enough that poison finished the job — and the `Poison Potion` (Apply 6) stacked onto its existing Poison 2 makes that 8. So: potion on Nectar, then `Charlotte` → `Strike` → `Fish-Flavored Bait` all into Nectar, `Pop!` onto the Rock. Nectar ended on 2 with Poison 8 and **died at the start of its turn without attacking.** 18 damage prevented for one potion. **Rejected:** putting Bait on the Rock where its Bomb 4 would have lived — it had to hit Nectar or the kill did not reach, and a wasted bomb is cheaper than an 18-damage hit.

**Something the screen did not tell me until after the fact:** Charlotte applies Cryo, Bait applies Pyro, and playing them in that order made **Bait itself the Melt trigger** — it hit for 7 instead of 4 (19 − 17 = 2 on the board, where my arithmetic said 5). Charlotte's card had the `*Reaction preview: Melt*` line the previous turn when the aura already existed; **Bait had no preview, because the aura I was about to create was not there when the screen printed.** The preview system only sees the board as it stands, so a reaction you set up *within one turn* is invisible until it happens. That is a real gap and it worked in my favour by accident.

**Turn 4.** Rock at 39, `Bomb 41`. `Ka-pow!` — free, lethal, immediate. **Rejected:** nothing meaningful.

**A clear screen-vs-outcome disagreement.** Across rounds 3 and 4 my status bar read `Blazing Barrier 6 (buff) — 6 Block left. When it absorbs damage, gain 3 Block.` while `Block` read 0. On round 3 the Rock hit me for 15 and I went 62 → 47 — **the full 15, with a buff on screen claiming 6 Block left.** Either the buff is a display that does not correspond to a live block pool, or Thoma's block silently expires and the buff line does not. I recorded the same mismatch, less cleanly, at the boss (18 incoming, Defend 5 plus "Blazing Barrier 6", 10 taken).

---

## Fight 12: Exoskeleton 24/24, Exoskeleton 28/28, Exoskeleton 26/26

**This is the fight act 2 added, and it is a good one.** All three printed `Hard To Kill 9 (buff) — Reduce all damage taken and HP lost by Exoskeleton to 9.` A damage cap is a direct, deliberate counter to a deck whose entire output is one enormous number, and the answer is on the cards if you read them: **`Set off` says "Every Bomb on the target goes off first, *one at a time*, each a Pyro hit for its size."** One at a time means N bombs is N separate capped hits. Against this enemy **bomb *count* is the stat and stack *size* is worthless** — the exact inversion of everything act 1 taught me.

**Turn 1.** Puzzlebox gave `Explosives Workshop` at 0 ("printed 1"): "At the start of your turn, your Bombs grow by 1 more." Played it, plus `Jumpy Dumpty+` and `Ammo Scavenging` onto one Exoskeleton, plus `Dig In` (8 Block for 1 Spark). 11 incoming, 3 taken. **Rejected:** spending a fifth card on `Defend` to zero it — I was hoarding act calls by then and 3 HP was the cheaper currency. That is a budget decision, not a game decision, and I am flagging it as such. Growth confirmed at **+5 per bomb** next turn (11 + 4 = 15 → 25).

**Turn 2 — measuring the cap.** `Fish-Flavored Bait` for a third bomb, then **`The Big One`**. The badge read `Bomb 25 (buff) — Set off here deals 25 Pyro damage`; the card says quadruple, which is 100; the enemy had 20 HP after Bait and **died**, which means somewhere between 20 and 27 actually landed (three bombs × a 9 cap). **The badge, the card and the enemy's own rule disagree with each other on the same screen, and none of the three numbers is what happens.** The correct read — 3 hits × 9 — is derivable, but only from the *Set off* glossary's "one at a time", and nothing points you there. **Rejected:** holding for the tick, which is capped at 9 a turn and would have taken four turns to do what one card did.

The rider fired again and produced the **same asymmetry as fight 9**: one survivor showed `Bombs here: 1, including 1 Mine`, the other `Bombs here: 2, including 2 Mines`. Twice in two fights, from a card that says "on ALL enemies".

**Turn 3.** Both survivors buffed (no incoming). `Charlotte` (Melt, 7) + `Strike` (6) killed the 11-HP one — **two small hits, both under the cap, which is the whole lesson of the fight**. `Pop!` onto the last one, `Thoma`. **Rejected:** any bomb-stacking line into the survivor; with a 9 cap, a Bomb 30 and a Bomb 9 are the same card.

**Turn 4.** Last Exoskeleton at 11 with `Bomb 10`. `Strike` (6 → 5 HP) then `Sparks 'n' Splash (proto)`, and the end-of-turn tick — capped at 9, which was six more than it needed — finished it. **Rejected:** `Kamisato Ayaka — Soumetsu`, which would also have killed it; I kept the Exhaust card for a fight that needs it.

Took 16 across the fight (52 → 36).

---

## Map, shop, rest, events

**Twelve map screens, node counts in order: 2, 2, 2, 2, 1, 1, 2, 1, 1, 1 (act 2 start), 2, 1.** Half of the act-1 screens after the elite offered a single node, i.e. no decision at all; the two act-2 screens I saw offered 1 and 2.

- **Map 1 (2 nodes).** `Unknown (path 1)` (leads on to Treasure) vs `RestSite (path 2)` (leads on to Treasure, Treasure). Took the rest at 23/62. Both branches converged on Treasure, so the only thing at stake was 18 HP versus Planisphere's 5 + an event roll.
- **Rest 1.** `Rest — Heal for 30% of your Max HP (18).` vs `Smith — Upgrade a card in your Deck.` Took Rest → 41/62.
- **Map 2 (2 nodes).** Two Treasures; took the one whose downstream list was longer (`Unknown, RestSite` vs `Unknown`).
- **Treasure.** `Vexing Puzzlebox — At the start of each combat, add a random card into your Hand. It's free to play this turn.` Taken. It shaped four of my six fights.
- **Map 3 (2 nodes).** `Unknown` (leads on to RestSite, Elite) vs `RestSite` (leads on to Monster). Took the Unknown because it kept both a rest and an elite reachable.
- **Event: Sapphire Seed.** `Consume — Heal 9 HP. Upgrade a card in your Deck.` vs `Plant and Nourish — Enchant a card with Sown.` **I took Consume, and the reason is a finding: "Sown" is never defined anywhere on the screen.** There is a "Words on this screen" glossary block on every other screen in this bridge, and this event had none. One option was two concrete numbers; the other was a word I had no way to price.
  The upgrade screen is good, though: it prints the current face and the upgraded face side by side, and `skip` un-picks without leaving. I used that to compare two candidates. `Sparks 'n' Splash (proto)+` reads **cost 1** (with the odd line "The cost printed on this card is 2; it is showing 1 here"); `Jumpy Dumpty+` reads **Bomb 11, Mine 4**. I took **Jumpy Dumpty+**: the engine reads the stack *every turn without spending it*, so +3 on a bomb is +3 on every future tick, whereas the cheaper Power saves one energy once per fight. The Mine 4 also improves the only AoE the deck has.
- **Map 4 (2 nodes).** `RestSite` vs `Elite`, both to Monster. Took the Elite at 55/62.
- **Maps 5, 6 (1 node each).** No decision.
- **Map 7 (2 nodes).** `Monster` vs `Unknown`, both to RestSite. Took the Unknown at 22/62 for the guaranteed Planisphere 5.
- **Shop** (this was the ? room; Planisphere healed 5 on entry, 22 → 27). **325 gold.** Bought **Candelabra (206)** and **Card Removal (75)**, removed **Injury**. **Rejected:** `Pear — 215 gold. Upon pickup, raise your Max HP by 10.` — at 22/62 with a guaranteed rest site between me and the boss, +2 energy on turn 2 of *every* fight beat +10 ceiling once; and `Careful Arrangement — 36 gold. Move all your Bombs onto the enemy as one Bomb. It grows by 5.` at the end with 44 gold spare — collapsing four bombs into one destroys 12 growth a turn to gain 5 once, which reads like a trap next to the +4-per-bomb rule. Also on the shelves and declined: `Bread`, `Fortifier`, `Liquid Bronze`, `Speed Potion`, `Tinder Toss`, `Fwoosh!`, `Powder Charge`, `Catalytic Converter`.
  **Small legibility wart:** after I bought it, the Candelabra's slot re-printed as `**Relic** — 206 gold (not available)`. The name is gone from a thing I own and am standing in front of.
- **Rest 2.** Rest → 45/62 before the boss. **Rejected:** Smith — a Sparks 'n' Splash cost reduction is worth less than 18 HP going into a 252-HP boss.
- **Act 2, Ancient node: Tezcatara.** Three relics, pick one, no price printed. `Very Hot Cocoa — Start each combat with an additional 4[Energy].` **Taken.** **Rejected:** `Toasty Mittens — At the start of your turn, Exhaust 1 card from your Hand and gain 1 Strength.` — Strength boosts Attacks, and this deck's damage is bombs, which are not Attacks; and forced Exhaust would eventually eat `Sparks 'n' Splash` or `The Big One`. **Rejected:** `Golden Compass — Replace the Act 2 Map with a single special path.` — a second option whose effect the screen does not actually describe. Two of the three shrine options this act asked me to buy an undefined word.
- **Map 11 (2 nodes).** Two Monsters; took the one leading on to an Unknown.
- **Map 12 (1 node).** Unknown — which turned out to be a **fight** (fight 12), not an event. Planisphere still paid its 5, so the relic's "? room" covers combat ?s and shops both.

---

## Companions and offers

Pounding Surprise's fourth-choice clause held on **every** card reward this session, and the shop stocked two more. Quoted exactly as printed:

1. **Diona — Signature Mix** — cost 1, skill. "Apply 2 Weak to ALL enemies. For 2 turns, at the start of your turn gain 4 Block. Exhaust." *(elite reward, and again in the shop at 75 gold. Not taken.)* Makes sense beside the kit — Weak is live with the bomb line per the Mine glossary — but I was short of placers, then short of gold.
2. **Thoma — Crimson Ooyoroi (proto)** — cost 1, skill. "For 2 turns, whenever you play an Attack, deal 5 Pyro damage to a random enemy and gain 3 Block. Exhaust." *(fight 8. Not taken.)* Coherent, but it pays per **Attack**, and this deck's Attacks are four Strikes and a Bait that I am usually correct not to play. A payoff keyed to the half of the deck the kit itself makes redundant.
3. **Amber — Explosive Puppet** — cost 1, skill. "The next time an enemy attacks you, take 3 less damage and deal 8 Pyro damage to ALL enemies." *(fight 9. Not taken.)* Fits well and I nearly took it; it is the third companion (with Dahlia in act 1) that restates the Mine idea in different words. Three cards for "when it attacks you, something goes off first" is a lot of concept overlap.
4. **Fischl — Oz, at Your Side (proto)** — cost 1, power, 74 gold. "At the end of your turn, Oz deals 5 Electro damage to a random enemy." *(shop. Not taken.)* Sensible: a second end-of-turn tick, and Electro is a third element to react off. It also inherits the kit's own worst clause — *a random enemy*.
5. **Kamisato Ayaka — Soumetsu** — cost 2, skill. "For 2 turns, at the end of your turn deal 8 Cryo damage to ALL enemies. Then deal 16 Cryo damage to ALL enemies. Exhaust." *(boss reward. **Taken**.)* The best-reasoned pick of the session: 32 damage that hits **ALL enemies** rather than a random one, on the same end-of-turn clock as my engine, in an element that Melts off my own Pyro auras. It patches the exact hole act 1 exposed. I never got to draw it.
6. **Barbara — Let the Show Begin♪ (proto)** [Hydro] — cost 1, skill. "Gain 6 Block. Apply Hydro." *(fight 11 reward. **Taken**.)* A Defend that is strictly better than my Defends and leaves an aura for my Pyro to react into. Makes sense next to the kit and needs no explanation, which is a compliment.
7. **Chevreuse — Interdiction Fire** [Pyro] — cost 1, attack. "Deal 7 damage." *(fight 12 reward — the screen I stopped on. Not taken; budget.)* The only Companion all session with no mechanic on it at all: a named Strike+1. Next to Ayaka and Diona it reads like a placeholder.

**Cards printing "(proto)" that I saw** (reported without seeking): `Sparks 'n' Splash (proto)`, `Thoma — Blazing Barrier (proto)`, `Thoma — Crimson Ooyoroi (proto)`, `Fischl — Oz, at Your Side (proto)`, `Barbara — Let the Show Begin♪ (proto)`. **Four of the five are Companions**, which matches the previous seat's ratio.

**Non-companion cards offered and declined, worth naming because of what they have in common:** `Bang Bang!` (2 Sparks, Set off), `Quick Fuse` (1 Spark, grow then Set off), `Fwoosh!` (1 Spark, Set off), `Tinder Toss` (1 Spark, Set off), `Flame Dance` (Set off each enemy whose aura is not Pyro), `Chained Reactions`, `Chain Fuse`, `Careful Arrangement`, `Sugar Rush`, `Sorry, Jean... — cost 0, skill. Remove one of your Bombs. Gain Block equal to its size.` The act-2 fight-11 reward screen offered **three Set off cards and one Companion, i.e. no non-detonator card at all.**

---

## The kit, after 12 fights

### (a) Which decisions felt like real choices, and what they traded off

**"Spend the stack or grow it" is still the good one**, and act 2 did not blunt it: fights 7 (three separate turns), 8, 10 and 11 were all decided on it. What made it stay interesting is that the *answer* kept moving. Against Byrdonis the clock (`Territorial`, +1 Strength a turn) pushed toward spending; against the boss the `Plow 150` threshold pushed toward one enormous cash-out at the right moment; against the Exoskeletons' damage cap the whole axis inverted and stack size stopped mattering at all.

**Three more with real teeth this session:**

- **Ordering the free detonator against an empty board.** Vexing Puzzlebox handed me `Sizzle`, `Big Badda Boom` and `Rapid Fire` on three different turn ones, and each time the right play was to fire it *before* placing a single bomb, so its Set off hit nothing and I banked the flat damage. That is a genuine, non-obvious, entirely card-legible trick and it is the best thing I found this session.
- **Reading poison against the turn order.** Fight 9's `Strike` into a 7-HP slime, and fight 11's `Poison Potion`, both worked because poison resolves at the *start of the enemy's turn* — so the question is never "can I kill it" but "can I get it under the poison line". The screens print every number that decision needs.
- **`Imbalanced`** (fight 11): "if its attacks are fully blocked, it becomes Stunned" turned four Defends — the most boring cards in the deck — into the best turn available. A debuff that makes vanilla Defends matter is doing real work.

### (b) What felt automatic, and what never seemed worth playing

**Placement turns with nothing incoming played themselves.** Fight 11 turn 2 and fight 12 turn 1 were "put the bombs on the biggest thing, block if anything is pointed at you" and nothing else was ever in question. When the board is quiet the kit has exactly one line.

**`Strike` remained the card I did not want** — with one act-2 exception that is itself interesting: against the 9-damage cap, Strike's 6 is *near-optimal* per card, and my 40-damage tick is not. The Exoskeletons briefly made the worst card in my deck one of the best, which is a good thing for a fight to do.

**The Set off pool is still fighting the rest of the kit, and act 2 made it starker.** I was offered `Sizzle`, `Big Badda Boom`, `Rapid Fire`, `Bang Bang!`, `Quick Fuse`, `Fwoosh!`, `Tinder Toss`, `Flame Dance`, `Chain Fuse`, `Careful Arrangement` — and I declined every single draftable one, because `Sparks 'n' Splash` converts the stack to damage *every turn without consuming it*, so any card that consumes it is selling a subscription for a one-off. The exception, and it is a real one, is **`The Big One`**: quadruple is the multiplier at which cashing out finally beats waiting, and it won the boss single-handed. The design already contains its own fix; it is just that one card in ten is the fix and the other nine are the trap.

**`Pounding Surprise`'s Spark clause came alive this session** and I want to correct the previous seat on it: the pool *is* full of Spark-priced cards (`Powder Charge`, `Dig In`, `Bang Bang!`, `Fwoosh!`, `Tinder Toss`, `Quick Fuse`, `Sugar Rush`). Once I drafted **one** (`Dig In`, 8 Block for 1 Spark), the relic stopped being a counter and became an extra card most turns. The problem is not that Sparks do nothing; it is that **Sparks do nothing until your first Spark card, and the relic's own text does not tell you that you need to go and draft one.**

### (c) What I could not understand, or that contradicted its own printed text

- **The Mine count is wrong twice more, and now it is asymmetric.** Fight 9: one rider, `Bombs here: 2, including 1 Mine` on one enemy and `including 2 Mines` on another. Fight 12: exactly the same split. "Place a Mine 4 on ALL enemies" produced different numbers on different enemies, in two separate fights. I still cannot derive any of it from the card.
- **The Bomb badge does not price the card that reads it, or the enemy that resists it.** `Bomb 60 → Set off here deals 60 Pyro damage`, then `The Big One` killed 140. `Bomb 25 → deals 25`, then against `Hard To Kill 9` the same set off delivered ~27 across three capped hits. The badge is a single number that is right only for the plain detonators.
- **`Blazing Barrier N (buff) — N Block left` absorbed nothing.** Fight 11 round 3: the buff read "6 Block left", the Rock hit for 15, I lost exactly 15. At the boss the same buff was up and the arithmetic missed by 5 the other way. Either it is a stale display or block is being accounted somewhere the screen does not show, but a status line that says "6 Block left" while 15 damage passes through is the clearest screen-vs-outcome contradiction I found.
- **The Elemental Reaction preview only sees the board as it is, not as I am about to make it.** `Charlotte` printed `*Reaction preview: Melt*` when the aura already existed, and delivered 7 for 4 exactly as promised — excellent. But in fight 11 I played Charlotte (Cryo) and then Bait (Pyro) in the same turn, and **Bait** was the card that Melted, with no preview on it, and my damage arithmetic came out 3 short of what happened. The best legibility feature in the kit is blind to combos built inside a single turn.
- **`Sown` (Sapphire Seed) and `Golden Compass`'s "special path" are both undefined on the screen that asks you to pick them.** Every combat screen carries a "Words on this screen" glossary; the event and shrine screens do not, and those are exactly the screens where a one-way choice is being made.
- **The Bomb glossary still drops the number.** Card-embedded text: "Grows **by 4** at the start of your turn." Glossary directly below, on the same screen: "Grows at the start of your turn." And with `Explosives Workshop` down it is +5 per bomb, which neither line can express. The number is the mechanic and the glossary is the copy that omits it.
- **`Vexing Puzzlebox` says "It's free to play this turn" and it is not always true.** `Powder Charge` and `Dig In`-style Spark cards arrived printed at their real Spark cost (`cost 1 Spark`), with none of the "the cost printed on this card is X; it is showing Y here" line the energy cards get. Free apparently means free of *energy*.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted:** `Spoils Map`. `Injury` was worse and I paid 75 gold to delete it, but Spoils Map is the one that is still there — a permanent unplayable card in my combat deck, acquired from an event option that printed no cost while the option beside it printed "Lose 8 HP" honestly. It showed up in four of the six hands I looked at closely.

**Happiest to draw:** **`The Big One`.** `Ka-pow!` is the elegant one — free, Retain, and its value changes every turn — but The Big One is the card that made the whole "never detonate" discipline pay. Four turns of refusing to spend a stack, and then one card converted 60 into a dead 252-HP boss. It also failed instructively in fight 12, where a damage cap turned quadruple into three nines, and that failure taught me more about the kit than any success.

### (e) Did the previous seat's three findings hold up?

1. **"Jumpy Dumpty's mine count cannot be derived from its text."** **Held, and got worse** — twice more, and now with two different mine counts on two enemies from the same "on ALL enemies" rider.
2. **"'Before the hit lands' may be untrue — the mine kill did not stop the hit."** **Not resolved, but leaning toward held.** Fight 9's arithmetic (14 pointed, 5 taken, 6 Block up with a +3 top-up) fits both readings. What I *did* prove separately is that the Blazing Barrier buff line lies about the block it is holding, which makes the "the hit landed" reading the more likely one.
3. **"Sparks 'n' Splash makes the kit's own Set-off cards bad, and Pounding Surprise's Spark clause sits inert."** **First half held hard** — I declined ten detonators over six fights and was right about nine of them. **Second half needs correcting:** the Spark clause is not inert, it is *unbootstrapped*. One drafted Spark card (`Dig In`) turned six banked Sparks into 8 free Block a turn, and the pool is full of them.

### (f) Did act 2 ask anything of the deck that act 1 did not?

**Yes, twice, and both times it was a good question.**

**`Hard To Kill 9` inverts the kit's central stat.** Every act-1 fight rewarded one enormous number. The Exoskeletons cap every hit at 9, which makes a Bomb 30 and a Bomb 9 identical and makes *bomb count* — and, absurdly, `Strike` — the way through. The answer is printed, in the `Set off` glossary's "one at a time", but it is three inference steps from any card face and neither the badge nor `The Big One`'s "quadruple" gives you a hint. This is the single best fight I played in the session and also the one where the kit's own display was least helpful.

**Act 2 also asks for block in a way act 1 did not.** `Bowlbug (Nectar)` went from an 3-damage nuisance to `Strength 15` and an 18-damage swing in one buff, and both Bowlbugs and all three Exoskeletons attack every turn. Act 1 gave me repeated free turns — the elite slept and buffed for two rounds, the boss buffed on turn 1 and was stunned on turn 4 — and act 2 has given me none so far. A deck whose defensive floor is a 5-Block Defend feels that immediately, and it is why `Dig In` and `Barbara` were the two cards I most wanted.

**What act 2 has not yet asked:** nothing has punished the `random enemy` clause harder than act 1's fight 6 did, because both act-2 fights let me delete an enemy early. That clause is still the kit's worst line and I expect it to bite in a fight I did not reach.

---

## Non-blindness declaration

- **Commands outside the two allowed ones:** none. Every game interaction was `GITS_LANE=2 python -m understudy.blindplay observe` or `GITS_LANE=2 python -m understudy.blindplay act "<command>"`. I never ran `harness state`, `scenario`, `staged_turn`, `soak`, or any other understudy command.
- **Tools used:** the **Bash** tool for every game call; the **Read** tool once, for the previous seat's record; the **Write** tool once, for this file.
- **Other shell usage, all of it output-trimming or call-chaining on the two allowed commands:** `cd` to the repo at the head of each call; `&&` to chain several `act` calls plus a closing `observe` into one tool call; `| tail -1`, `| tail -3` and `| head -N` to keep only the confirmation line of an `act`; `>/dev/null` to discard an `act`'s output entirely on two calls; `| sed -n '/^# Battle/,/^## Your relics/p;/^## Your hand/,/^## Words/p'` (and one variant starting at `## The other side`) to print only the state, hand and enemy sections of an `observe`; and one `for i in 1 2 3 4; do ... done` loop that issued four separate `act 'play "Defend (1)"'` calls in fight 11. Each of those four counted as an accepted `act`.
- **Scratchpad:** I did **not** create the notes file offered in the brief. All notes were kept in context.
- **The record I read:** `C:\Users\Monty\Documents\GitHub\GItS\review\qa\klee-round-7b-2026-09-02\opus-act1.md`, once, first, before touching the lane.
- **Other repo files read: none.**
