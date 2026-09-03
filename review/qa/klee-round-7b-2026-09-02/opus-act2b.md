# Blind seat record — KLEEMOD-KLEE, lane 2, act 2 continued

## Identity

- **Model / seat:** Claude Opus 5 (1M context), blind TESTER seat, round 7b, **third seat**.
- **Lane:** 2 (`GITS_LANE=2 python -m understudy.blindplay`).
- **Character:** KLEEMOD-KLEE. **Act-2 boss named by the map:** **The Insatiable**.
- **Picked up at:** act 2, the **card-reward screen after act-2 fight 2** (fight 12) that the second seat left standing, **HP 36/62**, 4 cards offered and unpicked.
- **Stopped at:** the **act-3 map screen**, one node into act 3, **HP 43/62**, having beaten The Insatiable and handled its reward screen. The act-3 boss the map names is **Aeonglass**. The lane is left standing on that map screen.
- **Actions accepted / refused:** **141 accepted, 1 refused.** The single refusal was `play "Tinder Toss" on "Hunter Killer"` → `error Card 'Tinder Toss' cannot be played on 'Hunter Killer'`; the card reads "a random enemy", so it takes no target, and the untargeted replay was accepted.
- **Termination reason:** **the act-2 boss resolved and its reward screen handled** — the brief's second stop condition, reached at 141 of 250 acts. Not budget, not death.

**Fights this session:** four — **Fight 13 … Fight 16**, numbered on from the previous record, which ended at Fight 12. **Fight 16 is the act-2 boss, The Insatiable, and it was killed on round 5.** No fight this session was lost and no fight took me below 25/62.

**HP trajectory** (every reading the screens printed, in order):

36 (pickup) → *Colossal Flower, 2 rungs, −11* → **30** (fight 13 r1) → 27 (r2) → 27 (r3, fully blocked) → 25 (r4) → won at 25 → **25** at the shop (Planisphere paid nothing — see the Planisphere finding) → **43** (rest) → *Future of Potions event* → *Treasure* → **48** (Planisphere, Unknown node) → **62/62** (Spirit Grafter, "Heal 25", capped) → *fight 14:* 62 → 62 (r2) → 45 (r3) → won at 45 → **50** (Planisphere, Unknown node) → *fight 15:* 50 → 40 (r2) → 40 (r3, fully blocked) → 40 (r4, fully blocked) → won at 40 → **45** (Planisphere, Unknown node) → **62/62** (rest before the boss) → *boss:* 62 → 62 (r2) → 54 (r3) → 43 (r4) → 43 (r5) → **won at 43/62**

**Gold:** 183 at pickup, +135 (Colossal Flower), +18 (fight 13) = **336** entering the shop. Spent 275 (Alice's Recipe 71 + Beetle Juice 104 + Card Removal 100), leaving 61. Then +16 (fight 14) +17 (fight 15) +100 (boss) = **194** at the stop.

**Potions at the stop:** `Dexterity Potion`, `Dexterity Potion`, `Speed Potion`. **Spent:** `Skill Potion` (fight 13 r4), `Beetle Juice` (boss, r3). **Lost to an event:** `Flex Potion` (The Future of Potions).

**Relics, exactly as printed:**

- **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark. Card rewards after a fight offer a fourth Companion choice.
- **Hefty Tablet** — Upon pickup, choose 1 of 3 Rare cards to add to your Deck, and add 1 Injury to your Deck.
- **Planisphere** — Whenever you enter a ? room, heal 5 HP.
- **Vexing Puzzlebox** — At the start of each combat, add a random card into your Hand. It's free to play this turn.
- **Twisted Funnel** — At the start of each combat, apply 4 Poison to ALL enemies.
- **Candelabra** — At the start of your 2nd turn, gain [Energy][Energy].
- **Very Hot Cocoa** — Start each combat with an additional 4[Energy].
- **Frozen Egg** — Whenever you add a Power into your Deck, Upgrade it. *(Treasure)*

**Deck at the stop — 30 cards.** Base 23 from seat 2, **minus** `Spoils Map` (removed at the shop), **plus** `Chain Fuse`, `Dig In+`, `Alice's Recipe`, `Fish-Flavored Bait+`, `Metamorphosis`, `The Big One` (2nd copy), `Kirara — Surprise Dispatch`; `The Big One` upgraded to `The Big One+` at the Smith; one `Strike` Transformed into an unknown card by the Symbiote event. Full list as the Smith screen printed it, with this session's changes marked:

- **Strike** ×3 — cost 1, attack. "Deal 6 damage." *(a 4th was Transformed at the Symbiote event into a card the screen never printed)*
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
- **The Big One+** (upgraded) [Pyro] — cost 2, attack. "Set off for quadruple damage." *(upgraded at the Smith)*
- **The Big One** [Pyro] — cost 3, attack. "Set off for quadruple damage." *(2nd copy, fight-14 reward)*
- **Dig In** — cost 1 Spark, skill. "Gain 8 Block."
- **Kamisato Ayaka — Soumetsu** — cost 2, skill. "For 2 turns, at the end of your turn deal 8 Cryo damage to ALL enemies. Then deal 16 Cryo damage to ALL enemies. Exhaust."
- **Barbara — Let the Show Begin♪ (proto)** [Hydro] — cost 1, skill. "Gain 6 Block. Apply Hydro."
- **Chain Fuse** — cost 1, skill. "Each Bomb on the enemy grows by 6." *(fight-12 reward, taken this session)*
- **Dig In+** (upgraded) — cost 1 Spark, skill. "Gain 11 Block." *(fight-13 reward)*
- **Alice's Recipe** — cost 2, power. "Your Bombs grow twice each turn." *(shop, 71 gold)*
- **Fish-Flavored Bait+** (upgraded) [Pyro] — cost 1, attack. "Deal 7 damage. Place a Bomb 6." *(Future of Potions event)*
- **Metamorphosis** — cost 2, skill. "Add 3 random Attacks into your Draw Pile. They're free to play this combat. Exhaust." *(Spirit Grafter event — see the undefined-words finding)*
- **Kirara — Surprise Dispatch** — cost 1, skill. "Gain 8 Block. Next turn, deal 10 damage to a random enemy." *(fight-15 reward, Companion)*
- **Nicole — Revelation, Uncreated Light+** (upgraded) — cost 1, power. "At the start of your turn, gain 5 Block, and 2 Strength if you ended last turn with Block." *(boss reward)*
- *`Spoils Map` **removed** at the shop (Card Removal, 100 gold).*
- *Two `Frantic Escape` status cards were added by the boss during fight 16; whether they persist is not something any screen told me.*

---

## The pick-up card reward (after fight 12)

Four cards: `Sorry, Jean...` (0, "Remove one of your Bombs. Gain Block equal to its size."), `Chain Fuse` (1, "Each Bomb on the enemy grows by 6."), `Quick Fuse` (1 Spark, "Each Bomb on the enemy grows by 3. Set off."), `Chevreuse — Interdiction Fire` (1, "Deal 7 damage.").

**Took `Chain Fuse`.** My engine reads the stack every turn without spending it, so a card that *grows* the stack compounds into every future tick, while `Quick Fuse`'s "Set off" sells the subscription for one payment. **Rejected `Chevreuse`** — the second seat called it "a named Strike+1" and it is. **Rejected `Sorry, Jean...`**, which is the interesting one: 0 cost, and Block equal to a bomb's size is a lot of Block late — but it deletes the bomb, and my only two win conditions both read the stack.

**A finding I paid for later:** Chain Fuse says "**Each** Bomb on the enemy grows by 6", so it scales with bomb *count*, not stack size. When I drew it in fight 13 I had exactly one bomb on the board, which made it a 1-energy "+6" — strictly worse than the Strike sitting next to it. The card is a multiplier printed as though it were a flat buff, and the hand where you want it (many small bombs) is not the hand the kit usually builds (one concentrated pile).

---

## Event: Colossal Flower (act 2, floor 3)

A **push-your-luck ladder**, and the first screen does not say so:

- Screen 1: `Extract Nectar — Gain 35 Gold.` / `Reach Deeper — Enter deeper. Lose 5 HP.`
- Screen 2: `Extract Nectar — Gain 75 Gold.` / `Reach Deeper — Enter even deeper. Lose 6 HP.`
- Screen 3: `Extract Nectar — Gain 135 Gold.` / `Enter the Center — Lose 7 HP. Obtain Pollinous Core.`

**Took two rungs (−11 HP) and banked 135 gold.** **Rejected `Enter the Center`:** at ~30/62 with three elites and a boss on the map, 7 more HP for **`Pollinous Core`, whose effect is printed nowhere**, is a blind buy; 135 gold buys a *chosen* relic at a shop one floor away.

**The finding:** the first screen prints "Lose 5 HP" honestly but gives no hint that a ladder exists, that it has three rungs, or that it terminates in an item. A player who takes 35 gold never learns the option was 135. And the terminal rung names an item and never says what it does — the same wart the second seat logged on `Sown` and `Golden Compass`. That is now **four** one-way choices this run that ask you to buy an undefined word, and every one of them is on an event or shrine screen, which are exactly the screens with no "Words on this screen" glossary block.

---

## Fight 13: Chomper (1) 62/62, Chomper (2) 61/61

Entered at **HP 30/62**, `Energy 7/3` (Very Hot Cocoa). Both Chompers printed `Artifact 1 (buff) — Negates 1 debuff.`

**The two Chompers alternate roles.** Round 1: Chomper (1) `Aggressive (Attack) — 8x2`, Chomper (2) `Strategic (StatusCard) — 3`. Round 2: swapped. Round 3: swapped back. So the board is always one 16-damage attacker plus 3 Status cards a turn, and the *status flood is the real clock* — my pile count went 24 → 27 → 30 → 32 over three rounds. That is a good fight design against a deck that wants to durdle, and I read it correctly and hurried.

**Turn 1.** Played `Grounded` → `Ammo Scavenging` (Bomb 4 on Chomper (1)) → `Dig In` → `Defend` → `Strike` on Chomper (1). Block 13 vs 16 incoming, took exactly 3. **Rejected:** nothing else was castable — I had 7 energy and only 5 playable cards, so **the binding constraint was hand size, not energy.** `Very Hot Cocoa`'s +4 energy did nothing at all on the turn it exists to help, because the kit's cards cost 1 and you only hold five of them. **Rejected `Quick Fuse`** — it printed `CANNOT BE PLAYED: no enemy is holding a Bomb`, which is a correct and well-worded refusal.

**Turn 2.** Grounded paid 6 at turn start, Candelabra printed `Energy 5/3`, the bomb grew 4 → 8 (+4, one bomb). Played `Charlotte` on Chomper (1) **first, to dig** — it drew a `Defend`, which is exactly what the turn needed. Then `Thoma` + `Defend` + `Strike` ×2. **Block 17 against 16: took 0.** **Rejected `Chain Fuse`** for a Strike, per the note above — one bomb on the board makes it +6, conditional on a detonator I had not drawn, against 6 damage banked now.

**Turn 3 — the turn the fight turned.** Chomper (1) at 40 with `Bomb 12` and, from Charlotte, `Cryo Aura 1`. `Ka-pow!` printed `*Reaction preview: Melt*`. I played **`Jumpy Dumpty+` first** (Bomb 11, stack → 23) and *then* `Ka-pow!`, so the Set off cashed both bombs at once into a live Cryo aura. **Rejected:** Ka-pow! before Jumpy Dumpty+ (it would have cashed 12 instead of 23), and rejected holding the detonator entirely — with a status flood on a clock and 27 HP, growing the stack was no longer free.

Chomper (1) went **40 → 4, exactly 36**. See finding 1 — that number is the sharpest measurement in this record.

**Turn 3, second half — a deliberate test.** Chomper (1) was left on **4 HP holding a `Mine 4`**, intending `8x2`. It dies to its own Mine either way, so the only thing at stake was whether I ate the 16. I spent the freed 2 energy on `Sparks 'n' Splash (proto)` and ended the turn. See finding 2.

**Turn 4.** One enemy left (so the tick is finally deterministic — the clause act 1 hated). Chomper at 57 with `Bomb 8`, 25 HP on me, 0 Block, 3 energy, and `The Big One` in hand — which is discarded if unplayed, and the draw pile was down to 3 cards, so "hold it for next turn" was not available. Played `Pop!` (stack → 13) then **`The Big One`**: **57 → 5, exactly 52 = 13 × 4.** **Rejected:** `Kamisato Ayaka — Soumetsu` + `Defend` (27 damage this turn and a 3-turn clock, versus 52 now); rejected Big One *before* Pop! (32 instead of 52).

That left me at 0 energy, 0 Block, 25 HP, with 16 pointed at me. I used the **`Skill Potion`** looking for block. See finding 4 — **all three offered Skills were bomb cards and none gave Block** — but `Powder Charge` (cost **1 Spark**, Bomb 6) rescued the turn anyway: I had `Spark 5` and no energy, so a Spark-priced card was the only thing in the game I could still play. `Bomb 6` on a 5-HP Chomper meant the end-of-turn tick killed it **before it attacked**. Took 0 on the last turn.

**Won at 25/62.** `Chain Fuse` and `Careful Arrangement` were the other two Skill-Potion options and both would have done *literally nothing* — there were no bombs on the board when I picked.

**Reward:** 18 Gold, and a card. Took **`Dig In+` — cost 1 Spark, "Gain 11 Block."** **Rejected `Diona — Shaken, Not Purred`** (1 energy, 6 Block, Apply Cryo twice, +5 Block if a Bomb goes off) — genuinely close, because I had just measured Melt multiplying a *bomb* hit by 1.75 and Diona is the cheapest way to plant Cryo; but at 25/62 I am short of HP, not damage, and **Dig In+ is block that costs no energy at all**, which is the scarcest resource in a 3-energy deck where every card wants to be a bomb. **Rejected `Pocket Fireworks`** (a 9-damage Strike) and **`Flame Dance`**, which both previous seats flagged and which is still worded to switch itself off against the Pyro aura my own deck applies constantly.

---

## Fight 14: Hunter Killer — HP 121/121

Entered at **62/62**. Hunter Killer carried `Poison 4` from Twisted Funnel — which is what proves the relic *does* fire, and therefore that fight 13's Artifact ate it (the Twisted Funnel finding).

**Turn 1 — a free turn** (`Strategic (Debuff)`), `Energy 7/3`. Played `Tinder Toss` **into an empty board** (seat 2's trick, third confirmation, and the first time on a Spark-priced card): its "Set off" found no bombs, so the 4+4 was clean profit. Then `Alice's Recipe`, `Strike` ×2, `Kamisato Ayaka — Soumetsu`. **Rejected `Dig In+`** — 11 Block against an enemy with no attack intent, and the Spark keeps.

**The one refused command of the session:** `play "Tinder Toss" on "Hunter Killer"` → `error Card 'Tinder Toss' cannot be played on 'Hunter Killer'`. The card reads "deal 4 damage to a random enemy twice", so it takes no target. Replayed untargeted and accepted. The refusal is correct, if terse.

Damage checked exactly: 121 − 12 (Strikes) = 109, − 8 (Tinder Toss) − **14** (Ayaka's 8 Cryo melting the Pyro that Tinder Toss left, 8 × 1.75) − 4 (Poison) = **83**.

**Turn 2 — the turn that produced the Strength-on-bombs finding.** The board opened `Tender 0 (debuff) — Whenever you play a card, lose 1 Strength and 1 Dexterity this turn.` I front-loaded the attacks (biggest first, while Strength was highest) and arranged the aura so the *last* element applied was Pyro, for Ayaka to melt at end of turn: `Fish-Flavored Bait+` → `Strike` → `Charlotte` (Cryo, melting Bait+'s Pyro) → `Fish-Flavored Bait` (re-applying Pyro) → `Ammo Scavenging`. **Rejected:** playing Charlotte last, which would have left Cryo up and cost Ayaka its 1.75x.

Damage: 7 + 5 + 3 + 1 = **16**, i.e. Tender's −1 applying *after* each card resolves, and Melt rounding down ((4−2) × 1.75 = 3.5 → 3). And the bomb badge read **`Bomb -1`** — the sharpest finding of the session.

**Turn 3.** Ayaka's finale: 67 − 14 (8 Cryo melted) − 16 ("then 16 when it ends") − 3 (Poison) = **34**, exact. Badge `Bomb 38` = the printed 6+4+4 **plus +8 per bomb**, confirming Alice's Recipe at double growth and confirming that Tender's −5 did *not* persist. `Ka-pow!` (free) then killed it — lethal with or without the Melt — **played first, before Tender could dock my Strength**. **Rejected:** `Jumpy Dumpty+` for a bigger stack, which was pure overkill on a 34-HP body.

**Won at 45/62**, 17 HP for a 121-HP enemy that landed one attack.

**Reward:** 16 gold, a Dexterity Potion, and a card. Took **a second `The Big One`** over `Run Away!` (0-cost, 3 Block, 7 if a Bomb went off), `Bang Bang!` and `Razor — Lightning Fang`. With Alice's Recipe doubling growth, stack size runs away from the enemy's HP, and quadruple is the only multiplier that keeps up; a second copy doubles how often the payoff is in hand.

---

## Fight 15: Bowlbug (Rock) 46/46, Bowlbug (Egg) 22/22, Bowlbug (Silk) 41/41

An Unknown node that resolved into a fight. All three opened with `Poison 4` — a wide board is where Twisted Funnel pays, exactly as seat 2 found. Rock carried `Imbalanced 1 — If Bowlbug (Rock)'s attacks are fully blocked, it becomes Stunned.`

**Turn 1.** `Flame Dance` arrived free from the Puzzlebox — **the card both previous seats declined as incoherent, and here it was correct**: with no bombs anywhere, its "Set off each enemy whose aura is not Pyro" clause costs nothing, so it is simply 5 damage to ALL for 0. Then `Charlotte` on Egg — Cryo into the Pyro that Flame Dance had just applied, **17 → 10, exactly 7 = 4 × 1.75** (third Melt confirmation) — which also drew a `Strike`. Then `Strike` on Egg to put it on **exactly 4 against its own `Poison 4`**, `Fish-Flavored Bait` on Rock, `The Big One+` on Rock (41 → 21, exactly 4 × 4 = 16), and `Defend`.

**Rejected:** blocking Rock's 15 to fire `Imbalanced`. I checked the arithmetic and it was unreachable — one `Defend` plus both Dexterity Potions is 9, and the pool is shared with Egg's 7 anyway. Also **rejected holding the Bomb 4 to grow it**: with no engine card in play, an ungrown bomb pays only through a detonator, and 16 now beat 32 in two turns' time against an enemy attacking for 15 each turn.

Egg died to its own Poison at the start of its turn **without attacking**.

**Turn 2.** Silk applied `Weak 1 — Attacks deal 25% less damage for 1 turn`, and **`Ka-pow!` immediately re-printed as "Deal 3 damage"** — the debuff shown on the affected card face, the good behaviour seat 2 logged for `Tangled`. Rock on 17 pointing 15. Played `Jumpy Dumpty+` then `Chain Fuse` (this time with a real target for it — see the Chain Fuse finding), read the badge, and only then committed: **`Bomb 12 (buff) — Set off here deals 12 Pyro damage after Weak.`** 11 + 6 = 17, × 0.75 = 12, and **the badge names the modifier it has applied** (a genuine positive, below). 12 + Ka-pow!'s 3 = 15 into 17 left Rock on 2 against `Poison 3` — dead before its 15 landed. Then `Sparks 'n' Splash`, `Dig In` and `Defend` for 13 Block against Silk's 8. **0 damage taken.**

**Turn 3 — a deliberate test on a free turn** (Silk's intent was `Debuff`). `Barbara` was showing `*Reaction preview: Vaporize*` on a card whose whole text is "Gain 6 Block. Apply Hydro" — no damage number anywhere. I played it to find out what a 1.5x multiplier does to nothing. See the Barbara/Vaporize finding. **Rejected:** `Kamisato Ayaka` in the same slot, which is what the aura was actually worth.

**Turn 4.** `Pop!` + `Strike` + `Dig In+` (11 Block against 8). **0 damage taken again.** Badge confirmed `Bomb 6 ... after Weak` (4 + 4 growth = 8, × 0.75).

**Turn 5.** Silk on 3; `Strike` finished it. **Won at 40/62** — 10 HP for a three-body fight, with two of the four rounds at zero damage taken.

**Reward:** 17 gold, a Speed Potion, and a card. Took **`Kirara — Surprise Dispatch`** (1 energy, "Gain 8 Block. Next turn, deal 10 damage to a random enemy") over `Grounded+`, `Dig In` (a third Spark block card) and `Perfect Timing`. Kirara is unconditional 8 Block *and* 10 damage on one card, and against a single boss the kit's worst clause — "a random enemy" — is deterministic. **Rejected `Grounded+`** specifically because its condition ("if none of your Bombs went off last turn") fights the boss plan of cashing a stack with The Big One+ (the Grounded/Dig In finding).

---

## Map, shop, rest, events

**Route from the pickup:** Unknown (Colossal Flower) → Monster (fight 13) → **Shop** → RestSite → Unknown (Future of Potions) → Treasure → Unknown (Spirit Grafter) → Monster (fight 14) → RestSite (Smith) → Unknown (fight 15) → Unknown (Symbiote) → RestSite → **Boss**. Six of the twelve map screens offered exactly **one** node, i.e. no decision at all.

- **Shop, 336 gold.** Bought **`Alice's Recipe` (71)** — "Your Bombs grow twice each turn", the best gold-per-power on the shelf and the card that finally gives `Very Hot Cocoa`'s dead turn-1 surplus something to buy; **`Beetle Juice` (104)**; **`Card Removal` (100)** to delete `Spoils Map`, whose "next Act" is the act I was already standing in, making it permanently dead. **Rejected `Mango` (277, "raise your Max HP by 14")** — that promises ceiling, not healing, and it was four fifths of my purse. **Rejected `Sling of Courage` (227, 2 Strength in Elite combats)** on seat 2's reasoning that bombs are not Attacks — **and the Strength-on-bombs finding shows that rejection was wrong**: Strength does modify bombs, so a Strength relic is a bomb-size relic. That is the most expensive mistake I made this session and I made it on inherited reasoning.
- **Rest sites (3).** Took **Smith** at the middle one and **Rest** at the other two, deliberately: at 45/62 a rest wastes most of its 18, so I upgraded there and banked the healing for the rest site sitting immediately before the boss. Upgraded **`The Big One` → `The Big One+`, cost 3 → 2** — chosen over `Sparks 'n' Splash+` (2 → 1) because Very Hot Cocoa and Candelabra make turns 1–2 energy-rich and every later turn a flat 3; the finisher is cast late, the engine early, so the cost cut is worth far more on the finisher.
- **Treasure: `Frozen Egg`** — "Whenever you add a Power into your Deck, Upgrade it." Free, taken, and it never fired afterwards.
- **The three events** are covered in the undefined-words finding below.

---

## Fight 16 (Act-2 Boss): The Insatiable — HP 321/321

Entered at **62/62**, `Energy 7/3`. Vexing Puzzlebox handed me **`Sparks 'n' Splash (proto)` at cost 0** ("The cost printed on this card is 2; it is showing 0 here") on a turn whose intent was `Empower (Buff)` — my engine, free, on a free turn.

**This is the fight the kit is built for, and it is the first one all session where that was true:** a **single** enemy, so the "random enemy" clause that both previous seats named as the kit's worst line is simply absent, and a 321-HP pool for a compounding stack to outgrow.

**Turn 1.** `Sparks 'n' Splash` (0) → `Fish-Flavored Bait+` (7 damage, Bomb 6) → `Strike`. **Rejected `Dig In+`** — 11 Block against an enemy with no attack intent. **Rejected `The Big One`**, which became legal the moment Bait+ planted: 6 × 4 = 24 now, against a bomb the tick reads *every turn without spending it*. Used 2 of 7 energy — hand-limited again, not energy-limited.

**Turn 2 — the boss states its clock.** Its Empower printed `Sandpit 4 (buff) — In 4 turns, you will be eaten and die`, and put two `Frantic Escape — cost 1, status. Get farther away. Increase Sandpit by 1. Increase the cost of this card by 1.` into my deck. So the boss is a **race with a buyable extension at an escalating price**, and the currency is status cards that are otherwise dead in hand. I played both immediately, while they were cheapest: **Sandpit 4 → 6, exactly as printed.** Then `Pop!`, `Kirara`, `Kamisato Ayaka`. Full 5 energy.

**Turn 3.** 298 → 256 = **42**, exact: tick 15 + Ayaka's 8 Cryo melting the Pyro aura for **14** + Kirara's promised 10 + Poison 3. And `Sandpit 6 → 5`, so it counts down one per turn. Boss pointed a single **28**. Spent `Beetle Juice` (it shows on the enemy as `Shrink 3`), installed `Alice's Recipe`, `Fish-Flavored Bait`, `Dig In`. Took **11** — 28 × 0.7 = 19, less 8 Block, exact.

**Turn 4.** 256 → 193 = **63**, exact: Bait 4 + tick 27 + Ayaka's finale **30** (the 8 melting for 14, then the closing 16) + Poison 2. Badge `Bomb 51` = 27 + **8 per bomb** across 3 bombs, confirming Alice's Recipe. Boss on `Empower` again — a second free turn — so I spent all of it on stack and draw: `Ammo Scavenging` (4th bomb), `Charlotte` (dig), and then the card Charlotte found: **`Barbara`, showing `*Reaction preview: Frozen (Boss)* — Bosses cannot be Frozen. Hydro plus Cryo is consumed and applies 2 Vulnerable instead.`** **Rejected:** the three block cards in hand, all worthless against an Empower.

**Turn 5 — the payoff.** 189 → 106 = **83**: the 55 stack × 1.5 for Vulnerable = 82, plus Poison. Badge now read **`Bomb 130`** — 87 (55, plus 8 per bomb across 4) × 1.5. Boss on 106, `Ka-pow!` free in hand and Retained since turn 1. Played `Jumpy Dumpty+` purely for margin, then **`Ka-pow!` — set off 130 into 106. The Insatiable died on round 5, with `Sandpit 3` still on the board.**

**The boss cost me 19 HP** (62 → 43) and never got a third attack in. Two of its five turns were Empowers.

**Reward:** 100 gold and a card — and all four offers were **Powers, three of them pre-upgraded**, which is `Frozen Egg` firing visibly on the reward screen. Took **`Nicole — Revelation, Uncreated Light+`** (1 energy, "At the start of your turn, gain 5 Block, and 2 Strength if you ended last turn with Block"). **Rejected `Alice's Recipe+`** (a second copy, cost 1 — I could not tell from any screen whether two copies multiply or overwrite, and I was not willing to pay a card for an unreadable interaction), **`The Big One`** (a third copy) and **`Chained Reactions+`**. Nicole wins because it fixes both documented weaknesses at once: unconditional 5 Block a turn — strictly better than `Grounded`'s conditional 6, which fights every detonation plan — and 2 Strength a turn, which this session proved is **bomb size**.

---

## Findings, ranked by sharpness

### 1. Strength, Weak and Vulnerable all modify **Bomb** damage — and both previous seats bet against that

Fight 14 turn 2. `Tender 0 (debuff) — Whenever you play a card, lose 1 Strength and 1 Dexterity this turn` took me to `Strength -5`. I then placed three bombs of printed size 6, 4 and 4 — 14 in total. The badge read, verbatim:

> **Bomb -1 (buff)** — Set off here deals **-1** Pyro damage. Bombs here: 3.

That is exactly `(6−5) + (4−5) + (4−5) = −1`. A **negative damage number printed on the screen**, and it is Strength doing it.

The same fact showed up three more times, each exact:

- Fight 15: `Bomb 12 (buff) — Set off here deals 12 Pyro damage **after Weak**` — 11 + Chain Fuse 6 = 17, × 0.75 = 12.
- Fight 16 turn 5: the tick did **83** where the stack was 55 — 55 × 1.5 for `Vulnerable`, plus Poison.
- Fight 16 turn 5 badge: `Bomb 130` where the raw stack was 87 — × 1.5 for `Vulnerable`.

**Why this is the sharpest thing here:** it is not a display bug, it is a strategy-inverting fact that no card, keyword or glossary states. Seat 2 rejected `Toasty Mittens` ("Strength boosts Attacks, and this deck's damage is bombs, which are not Attacks") and I inherited that reasoning and used it to **reject `Sling of Courage` at the shop for 227 gold**. A Strength relic in this kit is a bomb-size relic, and a bomb deck should be *hunting* Strength and Vulnerable. The whole kit reads as though bombs sit outside the Attack modifier system, and they do not.

It also means the kit has a real trap: any effect that hands you negative Strength doesn't just weaken your attacks, it **shrinks the entire stack you have been building for five turns** — the badge is recomputed live, as the recovery proved (fight 14 turn 3 read `Bomb 38` = the printed 6+4+4 plus growth, with the −5 gone).

### 2. `*Reaction preview: Melt*` multiplies the **bomb** hit, not the damage the card prints

`Ka-pow!` printed, verbatim:

> **Ka-pow!** [Pyro] — cost 0, attack
> Retain. Set off. Deal 4 damage.
> *Reaction preview: Melt* — This card supplies Pyro or Cryo while an enemy has the other aura. The triggering hit deals 1.75x damage and consumes the aura.

Board: Chomper (1) at **HP 40/62**, `Bomb 12`, `Cryo Aura 1`. I played `Jumpy Dumpty+` first (badge → `Bomb 23 ... Bombs here: 2`), then Ka-pow!. **40 → 4. Exactly 36.**

Card-face arithmetic is 12 + 11 + 4 = **27**. The excess is 9, and `12 × 1.75 = 21`, so what lands is **21 + 11 + 4 = 36**: the 1.75x hit the **first bomb of the Set off**, not the "Deal 4 damage" the card prints.

"The triggering hit" reads, on a card whose only printed number is 4, as the 4. Price it that way and you compute 30 and miss a kill you had by six. The previous seats only ever measured Melt on cards whose own damage *was* the hit (`Charlotte` 4 → 7, twice; I confirmed that a third time in fight 15), so this is the first case that separates the two readings — and the wording does not.

### 3. A lethal `Mine` does **not** pre-empt the hit it fires before

The glossary, verbatim:

> *Mine* — A Bomb that also goes off when its enemy attacks you, **before the hit lands**. Weak shrinks it like any Bomb; the badge shows the number.

The clean instance, fight 13: Chomper (1) on **HP 4/62**, badge `Bomb 4 ... Bombs here: 1, including 1 Mine`, intent `Aggressive (Attack) — the number on its icon is 8x2`. I was on **HP 27, Block 6**, and left it alive deliberately, because the Mine kills it either way and the only thing at stake was whether I ate the 16.

**HP 27 → 25.** I took exactly **2** through **6** Block — 8 raw, i.e. **one hit of a printed `8x2`**.

So the Mine fired, and killed (4 into exactly 4 HP), and the kill removed the *second* hit — but the *first* hit landed. "Before the hit lands" is true of the ordering and false of the consequence: the thing the phrase promises a player is that the enemy dies before hurting you, and it does not.

This **resolves** what seat 1 raised in act 1 fight 2 (57 → 54 with no printed cost) and seat 2 left explicitly open in fight 9. Both suspected the hit lands. It does. The arithmetic is unambiguous here because Mine size and enemy HP were both exactly 4, with a single attacker on the board.

### 4. A Reaction preview on a card with **no damage** silently destroys your own aura

Fight 15 turn 3. `Barbara — Let the Show Begin♪ (proto)` — whose entire text is "Gain 6 Block. Apply Hydro" — carried:

> *Reaction preview: Vaporize* — This card supplies Pyro or Hydro while an enemy has the other aura. **The triggering hit deals 1.5x damage** and consumes the aura.

Bowlbug (Silk) had `Pyro Aura 1`. I played Barbara. **Silk stayed on exactly 23/41 and its Pyro Aura was gone.**

The reaction *fired* — it consumed the aura — but Barbara has no damage for the 1.5x to multiply. So a card advertising a damage bonus delivered, in fact, only a **loss**: it ate the aura that my `Kamisato Ayaka` Cryo tick would have melted off for 14 instead of 8. The preview reads as an upside and is a downside, and nothing distinguishes it from the previews on `Ka-pow!` and `Charlotte`, which are genuinely worth having.

**The counter-example is on the same card and it is excellent.** At the boss, Barbara instead printed `*Reaction preview: Frozen (Boss)* — Bosses cannot be Frozen. Hydro plus Cryo is consumed and applies 2 Vulnerable instead.` That one names the substitution, names the boss exception, and is worth a card — and the 2 Vulnerable it applied is what turned an 87 stack into a 130 badge. So the preview system is not broken; it is **silent about the one case where the reaction has no hit to attach to.**

### 5. Two identically-titled options, a grammar that addresses options by title, and no way to tell which you took

The Future of Potions printed three options, **two of them character-for-character identical**:

> - **Insert Common Potion** — Lose Flex Potion. Obtain an Upgraded Common Attack.
> - **Insert Common Potion** — Lose Dexterity Potion. Obtain an Upgraded Common Skill.
> - **Insert Rare Potion** — Lose Beetle Juice. Obtain an Upgraded Rare Power.

The only grammar offered is `choose "<option>"`. I sent `choose "Insert Common Potion"`, it was **accepted with an empty refusal**, and no screen ever said which of the two it had taken. I could only infer it consumed the Flex Potion afterwards, from the fact that the reward pool was all Attacks. If the roll had gone the other way I would have lost a potion I meant to keep and been told nothing.

The same screen also has **no decline option at all** — `choose` is the only verb, so the event cannot be walked away from. The Symbiote event is the same: two options, no exit, and its card-selection sub-screen offered no `skip` either.

### 6. Four one-way choices this session name a thing and never say what it does

All on event and shrine screens — which are exactly the screens that carry **no "Words on this screen" glossary block**, while every combat screen does:

- `Enter the Center — Lose 7 HP. Obtain **Pollinous Core**.` (Colossal Flower)
- `Let It In — Heal 25 HP. Add **Metamorphosis** to your Deck.` (Spirit Grafter)
- `Approach — Enchant an Attack with **Corrupted**.` (Symbiote)
- `Kill with Fire — Choose a card to **Transform**.` (Symbiote)

I bought `Metamorphosis` blind for a heal. It turned out to be **"cost 2, skill. Add 3 random Attacks into your Draw Pile. They're free to play this combat. Exhaust."** — a perfectly good card, which I only ever read on the Smith screen two floors later. It could as easily have been a curse; nothing on the offering screen distinguished the cases. This continues the pattern seat 2 logged for `Sown` and `Golden Compass`, and it is now **six instances across three seats**, all of the same shape.

**Colossal Flower adds a second layer:** it is a push-your-luck ladder (35 → 75 → 135 gold, at 5 → 6 → 7 HP) and **the first screen gives no hint that a ladder exists**, that it has three rungs, or that it terminates. A player who banks the 35 never learns the option was 135.

**And the one place this is done right is worth quoting**, because it shows the bridge knows how: the Transform confirmation printed *"The card this becomes has NOT been chosen yet. This screen rolls it at random when you confirm, and the card it is showing on the right is an animation cycling through the possibilities several times a second — it is not the result, so it is not printed here. Confirming means accepting an unknown card."* That is scrupulous. The events are not.

### 7. `Twisted Funnel` printed no Poison, and `Artifact` was never consumed

> **Twisted Funnel** — At the start of each combat, apply 4 Poison to ALL enemies.

Fight 13, both Chompers printed `Artifact 1 (buff) — Negates 1 debuff.` and **no Poison badge**, for all four rounds — and `Artifact` **stayed at 1 the whole fight**. Fights 14, 15 and 16 all opened with `Poison 4` correctly on every enemy and no Artifact anywhere, which proves the relic fires and therefore that the Chompers' Artifact ate the Poison.

So the interaction is almost certainly correct and only the **display** is wrong: the counter that exists precisely to show a negation happened never moved, and no screen said a negation occurred. A player sees a relic silently not work.

### 8. The badge names one modifier and hides another

Fight 15: `Bomb 12 (buff) — Set off here deals 12 Pyro damage **after Weak**.` — excellent, it names the modifier it has applied.

Fight 16 turn 5: `Bomb 130 (buff) — Set off here deals 130 Pyro damage.` — the raw stack was 87, and the 130 is 87 × 1.5 for the `Vulnerable` on the target. **Same badge, same kind of adjustment, and this time it is silent about it.**

This is worth stating carefully because it **partly overturns seat 2**, who concluded "the badge does not price the card that reads it". It does: fight 13's `Bomb 13` badge produced exactly **52** off `The Big One` (13 × 4), and fight 15's `Bomb 12` produced exactly 12. The badge is reliable and it is the right base. What is unreliable is whether it *tells you* which modifiers are already baked in.

### 9. `Planisphere` keys on the **Unknown node**, not on the room it turns out to be

> **Planisphere** — Whenever you enter a ? room, heal 5 HP.

I entered a shop through a node the map printed as **`Shop (path 1)`** and got **nothing** — the rest site two screens later read `HP 25/62`, unchanged from the end of fight 13. Seat 2 entered a shop through a node printed as **`Unknown`** and was healed. And every `Unknown` node I took this session paid its 5, including the two that turned out to be **fights**.

So the rule is "the node is a `?`", not "the room is a shop or an event", and seat 2's phrasing — "the relic's '? room' covers combat ?s and shops both" — is right about the first half and misleading about the second. It matters for routing: I picked several Unknowns partly for the guaranteed 5 HP, and that reasoning would have been wrong applied to a signposted Shop.

### 10. The kit's two best block cards are priced in a currency only the *opposite* strategy generates

`Dig In` (8 Block) and `Dig In+` (11 Block) cost **Spark**, not energy — which fight 13 showed is the kit's best idea: at `Energy 0/3` with a card I could not cast, `Powder Charge — cost 1 Spark` was the only playable card in the game, because Spark is full exactly when energy is empty.

But Spark comes from **`Pounding Surprise` — Whenever a Bomb goes off, gain 1 Spark**, and you start each combat with 1. So the block cards are funded by **detonating**, while `Grounded` — "At the start of your turn, **if none of your Bombs went off last turn**, gain 6 Block" — pays only for **not** detonating, and `Sparks 'n' Splash` argues for never detonating at all. Three of the kit's defensive pieces pull in two directions, and a hand holding `Grounded` and `Dig In+` together cannot fully satisfy either.

I hit this directly and it is why I took `Nicole` over `Grounded+` at the boss: an unconditional 5 Block a turn is worth more than a conditional 6 in a deck whose finisher is a detonation.

### 11. `Very Hot Cocoa` adds energy to the one turn that is already hand-limited

Fight 13 turn 1 opened `Energy 7/3`. I played every card in my hand and **ended the turn with `Energy 3/3` unspent**. Fight 16 turn 1 opened `Energy 7/3` and I used **2**. The kit's cards cost 1 and a hand is five, so a relic granting +4 on turn 1 is pouring energy into the only turn where cards, not energy, are the constraint. `Candelabra`'s +2 on turn 2 has the same problem in milder form.

`Alice's Recipe` (cost 2) is the first card I owned that gave the turn-1 surplus anything to buy, which is a large part of why it was worth 71 gold.

### 12. One sentence does duty for a permanent upgrade and a one-turn discount

On a single fight-15 screen, the hand header read *"2 cards in your hand are shown at a cost LOWER than the cost printed on the card; each of them says so on its own line"*, and the two were:

- `The Big One+` (upgraded) — cost 2 — *"The cost printed on this card is 3; it is showing 2 here."* — a **permanent** Smith upgrade.
- `Flame Dance` — cost 0 — *"The cost printed on this card is 1; it is showing 0 here."* — a **one-turn** Vexing Puzzlebox discount that evaporates at end of turn.

Identical phrasing for a property of the card and a property of this turn. The `(upgraded)` tag is the only distinguisher, and it sits in the title rather than beside the cost line that is actually being explained.

### 13. `Chain Fuse` scales on bomb *count* and reads like a flat buff

> **Chain Fuse** — cost 1, skill. Each Bomb on the enemy grows by 6.

Drawn in fight 13 with `Bombs here: 1`, it is a 1-energy "+6 payable only through a detonator" — strictly worse than the `Strike` beside it. It was excellent in fight 15 (2 bombs, +12, and it bought the exact lethal). The word carrying the whole card is "**Each**", and the hand where it is good is not the hand this kit usually builds, because concentration into one pile is what `Set off` rewards.

*(Unranked, and worth saying plainly: almost every number this kit prints is honest. Across four fights I checked roughly twenty outcomes against the screens and the arithmetic came out **exact** every time — 36, 52, 16, 34, 38, 42, 63, 83, 130, 12, 20, 11. `Set off`, `The Big One`'s quadruple, per-bomb `+4` growth, `Alice's Recipe`'s doubling to `+8`, `Candelabra`, `Beetle Juice`, `Poison`, `Frantic Escape`'s +1 Sandpit and `Pounding Surprise`'s one-Spark-per-bomb were all precisely as printed. **The failures above are almost all in the wording and the labelling, not the maths.**)*

---

## What the previous records got wrong or right

- **"'Before the hit lands' may be untrue."** *(seat 1, act 1 fight 2; seat 2 left it open at fight 9)* — **RIGHT, and now proven.** Finding 3. Seat 2's refusal to call it on ambiguous arithmetic was the correct discipline; my instance had exact numbers.
- **"`Blazing Barrier N — N Block left` absorbed nothing."** *(seat 2's clearest contradiction)* — **Right that the display is wrong, wrong about the mechanism.** I watched `Block` go **6 → 12** the moment Thoma resolved, *while* a separate `Blazing Barrier 6 (buff) — 6 Block left` line appeared beside it. It is one pool printed twice, and it goes stale instead of decrementing — which is exactly why seat 2 saw "6 Block left" while 15 damage passed through. Their first branch ("either it is a stale display or…") contained the answer.
- **"The Bomb badge does not price the card that reads it."** *(seat 2)* — **Overturned, then refined.** `Bomb 13` → **52** off The Big One (13 × 4, exact); `Bomb 12` → 12. The badge is the right base and it is reliable. Seat 2's two examples were both confounded — one by a `Hard To Kill 9` cap, one by an unmeasurable overkill. What the badge *doesn't* reliably do is disclose which modifiers it has folded in (finding 8), and it never prices a **reaction** (finding 2).
- **"Jumpy Dumpty's mine count cannot be derived from its text."** *(both seats, who twice saw 1 Mine on one enemy and 2 on another from one "on ALL enemies" rider)* — **NOT reproduced.** In fight 13, two bombs went off simultaneously and each of the two enemies received exactly **1 Mine** (`Bombs here: 1, including 1 Mine` on both) — matching the card text and contradicting seat 1's "one mine per bomb that went off" theory. The asymmetry they saw is real but conditional on something none of the three of us has isolated.
- **"Bombs are not Attacks, so Strength does nothing for this deck."** *(seat 2's stated reason for rejecting `Toasty Mittens` and `Sling of Courage`)* — **WRONG, and it cost me money.** Finding 1. I inherited the reasoning and used it to decline `Sling of Courage` for 227 gold at the shop. Strength, Weak and Vulnerable all move bomb numbers.
- **"`Flame Dance` is worded to switch itself off against the kit's own Pyro."** *(seat 1, endorsed by seat 2; both declined it twice)* — **Right in general, wrong on turn one.** Played into an empty board with no auras anywhere, its "Set off each enemy whose aura is not Pyro" clause costs nothing and it is simply 5 damage to ALL for 0 energy. It opened fight 15 for me. This is the same shape as seat 2's best discovery — fire the detonator *before* placing anything — and it generalises further than they realised: it applies to `Sizzle`, `Big Badda Boom`, `Rapid Fire`, `Tinder Toss` **and** `Flame Dance`.
- **"Sparks 'n' Splash makes the kit's own Set-off cards bad."** *(seat 1, sharpened by seat 2)* — **Held, then bent by act 2.** I took `Chain Fuse` over `Quick Fuse` on exactly this reasoning. But detonating was correct **five separate times** this session, and each time for a reason act 1 never presented: a status-card clock (fight 13), a card that would be discarded if unplayed (fight 13 turn 4), an enemy about to attack for 15 (fight 15), and a stack that had simply outgrown the boss (fight 16). The rule is not "never detonate", it is "never detonate for tempo you do not need" — and act 2 charges for tempo constantly.
- **"The Spark clause is unbootstrapped, not inert."** *(seat 2's correction of seat 1)* — **Right, and stronger than they put it.** Spark turned out to be the currency that is full exactly when energy is empty, and at fight 13 turn 4 it was the only thing standing between me and a wasted turn. Finding 10 is the complication they did not reach: the currency is generated by the strategy the rest of the kit tells you not to play.
- **"Act 2 has not yet punished the `random enemy` clause harder than act 1 did; I expect it to bite in a fight I did not reach."** *(seat 2's closing prediction)* — **It did not bite, and the reason is worth recording.** Every act-2 fight I played let me delete a body early (poison lines in fights 13 and 15, a Ka-pow! kill in fight 15), and **the boss is a single enemy**, so the kit's worst clause was simply absent from the fight the kit exists for. The clause is still bad; act 2's shape happens to hide it.

---

## Non-blindness declaration

- **Commands outside the two allowed ones:** none. Every game interaction was `GITS_LANE=2 python -m understudy.blindplay observe` or `GITS_LANE=2 python -m understudy.blindplay act "<command>"`. I never ran `harness`, `session`, `audit`, `notes`, `scenario`, `staged_turn`, `soak`, git, or any other command against the repo or the game.
- **Tools used:** the **Bash** tool for every game call; the **Read** tool twice, for the two previous seats' records, before touching the lane; the **Write** tool for this file and for one scratchpad fragment of this file's own text; and two `python - <<PY` invocations that did nothing but string-replace inside **this record file**.
- **Other shell usage, all of it output-trimming or call-chaining on the two allowed commands:** `cd` to the repo at the head of each call; `for c in ...; do ... done` loops and `;`/newlines to issue several `act` calls plus a closing `observe` in one tool call (each looped `act` counted as one accepted action); `| tail -N` and `| sed -n '...p'` to print only the state, hand and enemy sections of an `observe`.
- **Repo files read:** `review/qa/klee-round-7b-2026-09-02/opus-act1.md` and `opus-act2.md`, once each, first, as the brief required. **No other repo file was read** — no source, no YAML, no design doc, no ruling, no backlog.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
