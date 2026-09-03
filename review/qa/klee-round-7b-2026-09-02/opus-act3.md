# Blind seat record — KLEEMOD-KLEE, lane 2, act 3

## Identity

- **Model / seat:** Claude Opus 5 (1M context), blind TESTER seat, round 7b, **fourth seat**.
- **Lane:** 2 (`GITS_LANE=2 python -m understudy.blindplay`).
- **Character:** KLEEMOD-KLEE. **Act-3 boss named by the map:** **Aeonglass**.
- **Picked up at:** the **act-3 map screen** the third seat left standing, **HP 43/62**, 15 floors below the boss, one node offered (`Ancient (path 1)`).
- **Stopped at:** **dead.** The run ended inside **Fight 22**, the second act-3 elite (`Mecha Knight`, 300 HP), on floor 46 — **two floors below Aeonglass**, which I never saw. The final screen reads, verbatim: `TOOL-BLOCKED: game_over` / `the run is over; there is nothing left to play` / `The run ended on floor 46.` The lane is left exactly there.
- **Actions accepted / refused:** **156 accepted, 0 refused.**
- **Termination reason:** **death** — the brief's second stop condition, reached at 156 of 300 acts. Not budget, not a refusal streak, not a repeated screen.

**Fights this session:** six — **Fight 17 … Fight 22**, numbered on from the previous record, which ended at Fight 16 (the act-2 boss). Fights 20 and 22 were elites; I won 20 at 9 HP and lost 22.

**HP trajectory** (every reading the screens printed, in order — note that the map screen prints no HP, so I never saw seat 3's 43/62 myself, and the first combat screen after the Darv shrine read 62/62; see finding 7):

62/62 (fight 17 entry) → 62 (r2) → won at **62/62** → **51/62** (The Round Tea Party, `Pick a Fight`, −11) → *fight 18:* 51 → 49 (r2) → won at **49/62** → *fight 19:* 46/62 (Shinobu's own −3 HP) → **35/56** (r2 — **Max HP 62 → 56**, three `Paper Cuts` instances) → won at **35/56** → *fight 20 (elite):* 35 → **13** (r2) → **9** (r3) → 9 (r4) → won at **9/56** → **30/56** (rest site: `Eternal Feather` paid 21 on entry) → **35/56** (`Planisphere`, Unknown node) → *fight 21:* 35 → 32 (Shinobu) → 28 (r3) → 27 (r4) → won at **27/56** → *fight 22 (elite):* 27 → **18** (r2) → 18 (r3) → 18 (r4) → **23/61** (`Fruit Juice`) → **dead**.

**Gold**, as the screens printed it: the first act-3 shop opened at **250** (seat 3 stopped on 194 and fight 17 paid 12; I never saw a screen accounting for the other 44). Spent 217 there (`Explosives Workshop+` 71 + `Shinobu` 72 + `Fysh Oil` 74) → 33. +14 (fight 18) +14 (fight 19) = **61** at the second shop, printed; spent 38 → 23. +37 (elite) +18 (fight 21) = **78** at death, unspent.

**Potions at death:** `Strength Potion — Gain 2 Strength.` **Spent:** `Dexterity Potion` (fight 17 r1), `Dexterity Potion` (fight 20 r1), `Fysh Oil` (fight 20 r2), `Fruit Juice` (fight 22 r4). **Lost:** `Fire Potion`, claimed off fight 19's reward screen and never in a slot (finding 9).

**Relics at death, exactly as printed — thirteen:**

- **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark. Card rewards after a fight offer a fourth Companion choice.
- **Hefty Tablet** — Upon pickup, choose 1 of 3 Rare cards to add to your Deck, and add 1 Injury to your Deck.
- **Planisphere** — Whenever you enter a ? room, heal 5 HP.
- **Vexing Puzzlebox** — At the start of each combat, add a random card into your Hand. It's free to play this turn.
- **Twisted Funnel** — At the start of each combat, apply 4 Poison to ALL enemies.
- **Candelabra** — At the start of your 2nd turn, gain [Energy][Energy].
- **Very Hot Cocoa** — Start each combat with an additional 4[Energy].
- **Frozen Egg** — Whenever you add a Power into your Deck, Upgrade it.
- **Velvet Choker** — Gain [Energy] at the start of each turn. You cannot play more than 6 cards per turn. *(Darv shrine)*
- **Bag of Marbles** — At the start of each combat, apply 1 Vulnerable to ALL enemies. *(The Round Tea Party, unnamed by the event)*
- **Eternal Feather** — For every 5 cards in your Deck, heal 3 HP whenever you enter a Rest Site. *(Treasure)*
- **Letter Opener** — Every time you play 3 Skills in a single turn, deal 5 damage to ALL enemies. *(elite reward)*
- **Forgotten Soul** — Whenever you Exhaust a card, deal 1 damage to a random enemy. *(Grave of the Forgotten, unnamed by the event)*

**Deck at death — 35 or 36 cards.** The 25 upgradeable entries are quoted from the Smith screen (with `The Big One` upgraded there); the rest are cards the Smith did not list (finding 13), so the count carries one card of uncertainty — the card the act-2 Symbiote event Transformed a `Strike` into was never printed by any screen this session, and `Sorry, Jean...` appeared in one opening hand without my ever drafting it, so it is either that Transform or a `Vexing Puzzlebox` card.

- **Strike** ×3 — cost 1, attack. "Deal 6 damage."
- **Defend** ×4 — cost 1, skill. "Gain 5 Block."
- **Ka-pow!** [Pyro] — cost 0, attack. "Retain. Set off. Deal 4 damage."
- **Sparks 'n' Splash (proto)** — cost 2, power. "At the end of your turn, deal Pyro damage to a random enemy equal to the Bombs on it."
- **Pop!** — cost 0, skill. "Place a Bomb 5."
- **Fish-Flavored Bait** [Pyro] — cost 1, attack. "Deal 4 damage. Place a Bomb 4."
- **Grounded** — cost 1, power. "At the start of your turn, if none of your Bombs went off last turn, gain 6 Block."
- **Thoma — Blazing Barrier (proto)** — cost 1, skill. "Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block."
- **Charlotte — Framing: Freezing Point Composition** [Cryo] — cost 1, attack. "Deal 4 damage. Draw 1 card."
- **Ammo Scavenging** ×2 — cost 1, skill. "Place a Bomb 4. Draw 1 card for each of your Bombs that went off this turn."
- **Dig In** — cost 1 Spark, skill. "Gain 8 Block."
- **Kamisato Ayaka — Soumetsu** — cost 2, skill. "For 2 turns, at the end of your turn deal 8 Cryo damage to ALL enemies. Then deal 16 Cryo damage to ALL enemies. Exhaust."
- **Barbara — Let the Show Begin♪ (proto)** [Hydro] — cost 1, skill. "Gain 6 Block. Apply Hydro."
- **Chain Fuse** — cost 1, skill. "Each Bomb on the enemy grows by 6."
- **Alice's Recipe** — cost 2, power. "Your Bombs grow twice each turn."
- **Metamorphosis** — cost 2, skill. "Add 3 random Attacks into your Draw Pile. They're free to play this combat. Exhaust."
- **Kirara — Surprise Dispatch** — cost 1, skill. "Gain 8 Block. Next turn, deal 10 damage to a random enemy."
- **Shrug It Off** — cost 1, skill. "Gain 8 Block. Draw 1 card."
- **The Big One+** (upgraded) [Pyro] — cost 2, attack. "Set off for quadruple damage." *(upgraded at the act-3 Smith)*
- **The Big One+** (upgraded) [Pyro] — cost 2, attack. "Set off for quadruple damage." *(seat 3's copy)*
- **Jumpy Dumpty+** (upgraded) — cost 1, skill. "Place a Bomb 11. When it goes off, place a Mine 4 on ALL enemies."
- **Fish-Flavored Bait+** (upgraded) [Pyro] — cost 1, attack. "Deal 7 damage. Place a Bomb 6."
- **Dig In+** (upgraded) — cost 1 Spark, skill. "Gain 11 Block."
- **Nicole — Revelation, Uncreated Light+** (upgraded) — cost 1, power. "At the start of your turn, gain 5 Block, and 2 Strength if you ended last turn with Block."
- **Powder Charge** — cost 1 Spark, skill. "Place a Bomb 6." *(fight-17 reward, this session)*
- **Shinobu — Sanctifying Ring (proto)** — cost 1, skill. "Lose 3 HP. For 3 turns, at the end of your turn deal 5 Electro damage to ALL enemies and gain 5 Block. Exhaust." *(shop, this session)*
- **Explosives Workshop+** (upgraded) ×2 — cost 1, power. "At the start of your turn, your Bombs grow by 2 more." *(both shops, this session)*
- **Run Away!+** (upgraded) — cost 0, skill. "Gain 6 Block. If a Bomb went off this turn, gain 4 additional Block." *(fight-18 reward, this session)*
- **Sorry, Jean...** — cost 0, skill. "Remove one of your Bombs. Gain Block equal to its size." *(provenance unknown, see above)*
- *Two `Burn` — cost 0, status — were also seen in the deck during fight 22; whether the Mecha Knight's four copies persist past the fight is not something any screen said, and the run ended before I could find out.*

*(This file was written incrementally, after every fight.)*

---

## Ancient node: Darv (act 3, floor 1)

Three relics, pick one, no price and no decline option printed:

- **Philosopher's Stone** — Gain [Energy] at the start of each turn. ALL enemies start combat with 1 Strength.
- **Velvet Choker** — Gain [Energy] at the start of each turn. You cannot play more than 6 cards per turn.
- **Dusty Tome** — Obtain Jumpy Dumpty Mk.Omega+.

**Took `Velvet Choker`.** Both previous seats measured this deck as *hand*-limited on turns 1–2 (Very Hot Cocoa's +4 and Candelabra's +2 land on turns where five cards, not energy, is the binding constraint) and *energy*-limited from turn 3 on, at a flat 3. A permanent +1 every turn buys exactly the turns that are short. Its cost — a 6-card cap — has never once bound in 16 fights of records: the most either previous seat played in a turn was five.

**Rejected `Philosopher's Stone`:** the same +1 energy, but "ALL enemies start combat with 1 Strength" is a real recurring cost against act-3 multi-hit intents, and seat 3 proved Strength is a live stat here.
**Rejected `Dusty Tome`:** **`Jumpy Dumpty Mk.Omega+` is a name and nothing else** — no cost, no text, no rules. That is the seventh one-way choice across four seats that asks you to buy an undefined word, and it is again on a shrine screen, which is again the kind of screen that carries no "Words on this screen" glossary block. The name at least tells me it is in a family I own, which is more than `Pollinous Core` or `Sown` gave; it still does not tell me whether it is a card, what it costs, or what it does.

---

## Fight 17: Scroll of Biting (1) 32/32, Scroll of Biting (2) 34/34, Scroll of Biting (3) 35/35

Entered at **62/62**, `Energy 8/4` — the first screen that shows Velvet Choker paying (4 base+1, +4 Very Hot Cocoa). All three enemies printed:

> **Paper Cuts 2 (buff)** — Whenever Scroll of Biting deals unblocked attack damage to you, you lose 2 Max HP.

That is the first enemy in this run whose damage is *permanent*, and it reframes the whole fight: blocking is no longer a HP trade, it is Max-HP preservation, and a multi-hit intent (`5x2`) costs twice as much Max HP as a single `14`. All three opened with `Poison 4` from Twisted Funnel.

**Turn 1.** Intents: (1) `5x2`, (2) `Empower`, (3) `14`. Vexing Puzzlebox handed me `Big Badda Boom` at cost 0 ("The cost printed on this card is 2; it is showing 0 here").

I killed **Scroll (3)** outright — the single 14, because 14 is the one number I could not block and a `5x2` is the one I could: `Fish-Flavored Bait` (4 damage, Bomb 4) → `Ammo Scavenging` (Bomb 4, and **drew nothing**, correctly, because no bomb had gone off yet) → `The Big One` on the `Bomb 8` stack. 35 − 4 = 31, and quadruple-of-8 = 32 killed it exactly.

Then, with the board empty of bombs, `Big Badda Boom` on Scroll (1) for a clean **12** — the empty-board detonator trick, now confirmed by a fourth seat and for the fourth different card (`Sizzle`, `Rapid Fire`, `Tinder Toss`, `Flame Dance`, and now `Big Badda Boom` a second time). Then `Kamisato Ayaka — Soumetsu`, then `Dexterity Potion`, then `Dig In`.

**Rejected:** playing `Big Badda Boom` *before* the bombs, which is the ordering seat 2 established — here it was wrong, because its "Then deal damage equal to what the Bombs dealt" clause would have doubled an 8 stack for +8 while `The Big One`'s quadruple wanted the same 8 for +32. Two detonators in one hand made the ordering rule conditional for the first time: fire the *weaker* detonator into the empty board and save the multiplier for the stack.
**Rejected:** holding the Dexterity Potion. `Dig In`'s 8 Block against a `5x2` leaves 2 unblocked — and 2 unblocked means **2 permanent Max HP**. Dexterity 2 took Block to exactly 10 and made the turn free. Against Paper Cuts a potion that would normally be hoarded is correctly spent to buy the last 2 points of a block total.

**Confirmed on the screen:** `Dexterity 2 (buff) — Increases Block gained from cards by 2`, and `Dig In` produced **Block 10**; on the following turn my `Defend` re-printed itself as **"Gain 7 Block"** rather than 5. The debuff/buff-on-the-card-face behaviour both previous seats praised for `Shrink`, `Tangled` and `Weak` also works upward, for Dexterity.

End of turn: Ayaka's 8 Cryo hit Scroll (1) through the `Pyro Aura 2` that Big Badda Boom had left → **20 → 6, exactly 14 = 8 × 1.75**, a fourth exact Melt confirmation. Scroll (2), which had no aura, took a plain 8. Scroll (1)'s `5x2` hit 10 Block for **zero**, and **no Max HP was lost**.

**Turn 2.** Scroll (1) at 2/32 with `Poison 3` — dead at the start of its turn without acting, so it was not worth a card. Scroll (2) at 22/34, `Strength 2`, `Cryo Aura 1` (Ayaka's), intent `7x2`.

I spent the turn on a **deliberate measurement** rather than the cheapest kill, because the board was a clean instrument: `Pop!` (Bomb 5) → `Ammo Scavenging` (Bomb 4) → badge, then `Ka-pow!`. The badge read, verbatim:

> **Bomb 9 (buff)** — Set off here deals 9 Pyro damage. Bombs here: 2. Each grows at the start of your turn. None goes off by itself.

`Ka-pow!` printed `*Reaction preview: Melt*` on its own face. Card-face arithmetic is 9 + 4 = **13**. **22 → 6: exactly 16.** See finding 2.

**Rejected:** ending the turn with no plays at all, which was in fact lethal (Soumetsu's last turn does 8 + 16 = 24 to ALL, and the two survivors were on 2 and 6). I spent four act calls to get a clean read on whether the badge prices a reaction. It does not.

End of turn Soumetsu's finale killed both. **Won at 62/62 on round 2 — no damage and no Max HP taken in a three-body fight.**

**Reward:** 12 gold, and a card. Took **`Powder Charge` — cost 1 Spark, skill. "Place a Bomb 6."** — a bomb placer that costs **no energy at all**, in a deck seat 3 measured as energy-starved from turn 3 on, and one whose Bomb 6 compounds at +8 a turn under `Alice's Recipe`. **Rejected `Sucrose — Catalyst Conversion (proto)`** (0, gain 1 Energy, draw 1, Exhaust) — strictly positive and genuinely well-designed, but +1 energy once is worth less than a bomb that grows all fight. **Rejected `Sizzle`** and **`Tinder Toss+`**, both detonators, for the reason three seats have now recorded.

---

## Event: The Round Tea Party (act 3, floor 2)

> - **Enjoy Your Tea** — Obtain Royal Poison. Heal to full HP.
> - **Pick a Fight** — Lose 11 HP. Obtain a random Relic.

**Took `Pick a Fight`, 62/62 → 51/62.** I was at **full HP**, so half of the first option was worth literally nothing and the other half was `Royal Poison`, an eighth undefined name. There is no third option and no way to decline.

**The finding is what happened next: the event never named the relic it gave me.** It printed `Continue`, then `Proceed`, then dropped me on the map. I learned what I had bought — **`Bag of Marbles` — At the start of each combat, apply 1 Vulnerable to ALL enemies** — only from the relic list on the *next combat screen*, two rooms later. An event that charges 11 HP for a named category and then declines to say what arrived is the same wart as `Pollinous Core`, running in the other direction: there, a name with no effect; here, an effect with no name.

It is also, by luck, the best relic this deck could have drawn — seat 3 proved `Vulnerable` multiplies the bomb badge by 1.5, so `Bag of Marbles` is a free ×1.5 on the opening stack of every fight.

---

## Shop (act 3, floor 3) — 250 gold

Bought **`Explosives Workshop+`** (71, "At the start of your turn, your Bombs grow by 2 more"), **`Shinobu — Sanctifying Ring (proto)`** (72), **`Fysh Oil`** (74). Left with 33.

**Rejected `Vambrace`** (202, "The first time you gain Block from a card each combat, double the amount gained") — real, but one card's worth of block per fight for four fifths of my purse. **Rejected `Royal Stamp`** (222, "choose an Attack or Skill in your Deck to Enchant with **Royally Approved**") — the ninth undefined word, and the most expensive one anyone has been offered. **Rejected `Card Removal`** (125) with a 31-card deck, which I still think was close. **Rejected `Careful Arrangement`, `Fwoosh!`, `Flame Dance`, `Bang Bang!`** for the reasons three seats have recorded.

**A legibility finding I only got by buying:** `Fysh Oil` is a **potion**, not a relic, and *nothing on the shop screen said so*. It printed as `**Fysh Oil** — 74 gold / Gain 1 Strength and 1 Dexterity` — a bare name, a price and an effect, in exactly the format `Vambrace`, `Stone Calendar` and `Royal Stamp` use one line above it. I bought it believing it was a permanent Strength relic, which after seat 3's finding is a bomb-size relic and would have been the best 74 gold on the shelf. The only thing that ever disclosed it was the *sold-out* line after purchase, which re-printed the slot as `**Potion** — 74 gold (not available)`. **The shop discloses an item's category only after you can no longer act on it.**

By contrast the sold-out *card* shelves are scrupulous, and worth quoting as the counter-example: *"(this shelf is empty) — Bought, or never stocked. The game clears a shelf's card the moment it is sold, and the name, the text and the cost all live on that card, so nothing on the feed can say which one it was."*

---

## Fight 18: Living Shield 55/55, Turret Operator 41/41 (Block 25)

Entered at **51/62**. Both opened with `Poison 4` (Twisted Funnel) **and `Vulnerable 1`** (Bag of Marbles, its first firing). Living Shield printed:

> **Rampart 25 (buff)** — At the start of the player's turn, Turret Operator gains 25 Block.

A two-body fight where one body is the other's armour: 25 Block a turn on the 41-HP attacker for as long as the 55-HP shield lives. Kill order is the whole fight and the screen states it in one line.

**Turn 1 — a prediction I wrote before acting, and the screen met it exactly.** Vexing Puzzlebox handed me `The Big One` at cost 0 ("The cost printed on this card is 3; it is showing 0 here"). I had `Powder Charge` (1 Spark, Bomb 6) and `Chain Fuse` (1, each Bomb +6) and one Spark.

I predicted, from seat 3's finding 8, that the badge would fold the Vulnerable in silently and read **18** rather than 12. Played `Powder Charge` then `Chain Fuse` on Living Shield, and the badge read, verbatim:

> **Bomb 18 (buff)** — Set off here deals 18 Pyro damage. Bombs here: 1. Each grows at the start of your turn. None goes off by itself.

(6 + 6) × 1.5 = 18, and the word `Vulnerable` appears nowhere in the badge — where the fight-15 badge said "**after Weak**" in the same slot. Then `The Big One` at 0: **Living Shield died from 55/55 in one card.** 18 × 4 = 72.

**Rejected:** using the free `The Big One` on the Turret Operator, which is the bigger threat (`3x5`) — but it was sitting behind 25 Block, and a quadrupled stack spent into a block wall is the worst card in the game. **Rejected:** holding `Chain Fuse`; with exactly one bomb on the board it is a flat +6, which seat 3 measured as its weak case, but here that +6 was worth **+24** through the quadruple, which is the first time `Chain Fuse`'s "Each" scaling has been worth taking on a single bomb.

Then `Kirara` (8 Block, 10 damage next turn), `Defend` (5), `Metamorphosis` (2) — six cards, exactly Velvet Choker's cap, the first time in 18 fights the cap has bound anything, and it bound nothing, because I had nothing left to play. 15 incoming, 13 Block, **took exactly 2**.

**Turn 2.** The Turret's Block 25 was gone at its own turn start (nothing on screen says when enemy Block clears; it just does). 41 → 27 = Poison 4 + Kirara's promised 10, exact. `Pocket Fireworks` (a free Attack from `Metamorphosis`, 0 cost) dealt exactly **9** and left `Pyro Aura 2`. Then `Shinobu`, `Strike`, `Dig In`, `Pop!`.

**The measurement I want to flag, and its caveat.** After `Pocket Fireworks` the Turret was on 18. `Strike` prints 6. `Shinobu` prints "deal 5 Electro damage to ALL enemies" at end of turn, into a live `Pyro Aura 2`. **The fight ended on that end-of-turn tick** — 18 HP gone to a printed 6 plus a printed 5. I did not `observe` between the Strike and the end of the turn, so I cannot split the 18 cleanly; what is certain is that **11 printed damage killed 18 HP**, and the only unaccounted-for element on the board was Electro meeting Pyro. See finding 3.

**Won on round 2, HP 49/62** (2 taken from the Turret, 3 paid to Shinobu's own cost).

**Reward:** 14 gold, `Fruit Juice`, and a card. Took **`Run Away!+`** — cost **0**, "Gain 6 Block. If a Bomb went off this turn, gain 4 additional Block." Block that never competes for energy is the exact shape of what seat 3 measured this deck as short of. **Rejected `Sorry, Jean...`** (0, "Remove one of your Bombs. Gain Block equal to its size") a third time across three seats — with `Alice's Recipe` and now `Explosives Workshop+` the stack gets large enough that this is a huge Block card late, but it pays 1× block for a bomb my finisher would have paid 4× damage for. **Rejected `Gorou — Inuzaka All-Round Defense (proto)`** (1, 8 damage + 4 Block), which is a fine card in a deck with fewer than 33.

---

## Fight 19: Scroll of Biting ×4 — 31/31, 36/36, 30/30, 32/32

Entered at **46/62**. Four bodies, 129 HP, every one of them carrying `Paper Cuts 2`, `Poison 4` and `Vulnerable 1`. Round-1 intents: `14`, `5x2`, `Empower`, `Empower` — 24 damage and **three** separate Paper Cuts instances pointed at me.

**Turn 1.** `Alice's Recipe` arrived free from the Puzzlebox (printed 2, showing 0). Played it, then `Shrug It Off` (8 Block, draw 1 — it found a `Defend`), then `Kamisato Ayaka — Soumetsu`, `Defend`, and `Pop!` + `Powder Charge` **both onto Scroll (2)**, the 36-HP body.

**Rejected:** `Sparks 'n' Splash (proto)`, which was in hand with the energy to spare. With **four** enemies its "a random enemy" clause is a 1-in-4 lottery, and on turn 1 the stack it would have read was 11. This is the clause all three previous seats named as the kit's worst line, and it is the first time in this record that it made me leave my own engine card in hand.
**Rejected:** spreading the two bombs. Concentration is what `Set off` pays, and putting both on the *biggest* body is a bet that the last enemy alive will be the bombed one — which is also the only way the random-target tick ever becomes deterministic.

**The reason Ayaka was the whole plan:** 8 + 8 + 16 = 32 to ALL over three turns, plus Poison 4/3/2, is 41 per body against bodies of 30–36. One 2-cost card kills a four-enemy board on a printed schedule, and it does it without ever consulting the random-target clause.

Took **11** through 13 Block (24 incoming, exact) — and **Max HP went 62 → 56.** Three unblocked instances, three × 2 Max HP, exactly as `Paper Cuts` prints. This is the first permanent cost this run has paid to an enemy.

**Two exact numbers off the end-of-turn tick.** Every enemy went down by **16**: Poison 4 + Ayaka's 8 **× 1.5 for Vulnerable = 12**. So `Vulnerable` scales a Companion's Cryo tick, not merely Attacks — the same widening seat 3 proved for bomb damage, now shown on a card that is a **Skill** and whose damage is dealt by a *buff* at end of turn. And the bomb badge read:

> **Bomb 27 (buff)** — Set off here deals 27 Pyro damage. Bombs here: 2.

11 placed, +16 grown = 2 bombs × **+8**, i.e. `Alice's Recipe`'s doubling of the base +4, exactly as seat 3 measured, and with the `Vulnerable` gone the badge is back to raw.

**Turn 2 — 42 damage pointed at 35 HP.** Scroll (1) `Empower`; (2) `14`; (3) `7x2` with `Strength 2`; (4) `7x2` with `Strength 2`. Five more Paper Cuts instances, i.e. 10 more Max HP, on a 56 ceiling.

`Charlotte` first, to dig (4 damage and a card) — it found `Barbara`, and **that draw is the finding of this fight**. Barbara arrived carrying a preview neither previous seat ever saw:

> *Reaction preview: Frozen* — This card supplies Hydro or Cryo while an enemy has the other aura. **Its next action deals half damage**; attacking it Shatters for 6 damage.

Every enemy was wearing `Cryo Aura 1` — put there by *my own* Ayaka tick the turn before. So Barbara, a 6-Block skill, was also a **damage-halving debuff**, and the card said so on its face, in context, with the number. Seat 3 saw this same card fire `Vaporize` for nothing and called the preview system "silent about the case where the reaction has no hit to attach to"; here is the case that redeems it — a reaction on a **damage-less card whose entire payload is defensive**, previewed correctly.

Played `The Big One` on Scroll (2) — the only legal target, since it was the only body holding bombs — then `Barbara` on Scroll (3) to halve one of the two `7x2` swings, then `Thoma`.

**Rejected:** `Defend` and `Chain Fuse` in Barbara's slot. Barbara is 6 Block *and* roughly 7 damage prevented, which is a Defend and a half on one card, and I could only reach it because Charlotte dug.
**Rejected:** trusting Soumetsu's finale and skipping the whole hedge. Ayaka's last turn is 8 + 16 = 24 and every enemy was on 15/20/14/16, so the fight was in fact already over — but if that read were wrong I was facing 42 into 35 HP, and the cost of being wrong was the run.

Soumetsu's finale killed all four. **Won on round 2 at 35/56.**

**Reward:** 14 gold, `Fire Potion`, and a card — **skipped**. `Big Badda Boom+` (2, Set off, 16 damage, then damage equal to what the Bombs dealt) is a **doubler**: on a stack S it pays 2S + 16, where `The Big One+` at the same cost pays 4S. `Rapid Fire` and `Fish-Flavored Bait` I already own better versions of, and `Gorou` is fine and generic. At 34 cards the marginal card is worth less than the dilution, and this is the first reward all session where skipping was clearly right.

---

## Shop (act 3, floor 6) and Treasure (floor 7)

61 gold. Bought a **second `Explosives Workshop+`** (38) — cheap, and a Power that compounds is the only thing worth a slot in a 34-card deck. **Rejected `Dolly's Mirror`** (227, "obtain an additional copy of a card in your Deck"), which would have been the best relic on the shelf for a deck with two `The Big One`s, at four times my purse.

Treasure: **`Eternal Feather` — For every 5 cards in your Deck, heal 3 HP whenever you enter a Rest Site.** Taken (free). Worth flagging as a *design* observation rather than a defect: it is the first thing this run has offered that pays you for a **big** deck, and my deck is 35 cards because six card rewards in a row were worth less than the dilution. A relic that inverts the deck-size incentive arriving right after the two rewards I skipped is the sharpest moment of tension the run's economy has produced.

**A potion vanished without comment.** After fight 19 I claimed `Fire Potion` off the reward screen — the screen accepted it (`ok Claiming reward: potion (Fire Potion)`) — and the next combat's Potions block listed only `Fysh Oil`, `Dexterity Potion`, `Fruit Juice`. Three slots, four potions, and **nothing anywhere said the claim had failed or that a slot was full.** The reward screen let me spend a claim on a potion that could not exist.

---

## Fight 20 (Elite): Soul Nexus — HP 234/234

Entered at **35/56** against a 234-HP elite whose opening intent was a flat **29**. This was the closest the run has come to ending: I was at **9 HP from the end of round 1 to the end of the fight**, and won on round 4.

**Turn 1 — a single enemy, which is the whole reason this was winnable.** The kit's worst clause (`a random enemy`) is simply absent against one body, so `Sparks 'n' Splash` becomes a deterministic engine. Played `Dexterity Potion`, then **both copies of `Grounded`** (one free from the Puzzlebox), `Sparks 'n' Splash (proto)`, `Fish-Flavored Bait+`, `Pop!`, `Defend` — six cards, the cap again, and again it bound nothing.

**Rejected:** any line that spends the stack. `Grounded` pays *only* for not detonating, and with two copies down that is 12 Block a turn for free, forever — which against a 29-per-turn elite is the difference between a fight I can grind and one I cannot.

`Fish-Flavored Bait+` dealt exactly **10** (printed 7, × 1.5 for Bag of Marbles' Vulnerable). Badge read `Bomb 16` = (6 + 5) × 1.5 = 16.5, **truncated to 16** — the first place I have seen the badge round, and it rounds *down*. Took **22** (29 − 7). **HP 35 → 13.**

**Turn 2 — the stacking display, and a Dexterity boundary.** The status bar read:

> **Grounded 12 (buff)** — At the start of your turn, if none of your Bombs went off last turn, gain **12** Block.

Two copies of a card printing "gain 6 Block" merged into **one buff line whose own text was rewritten to the summed number**. That is excellent — better than showing two lines of 6 — and it also settles something: `Dexterity 2` was up, and the buff says 12, not 16. **Dexterity does not apply to Block granted by a Power**, only to Block from playing a card, which is exactly what its text says ("Increases Block gained from **cards**"). Both halves of that are legible and both are correct.

Spent `Fysh Oil` (+1 Strength, +1 Dexterity), then `Fish-Flavored Bait` **before** `Chain Fuse` — deliberately, because Chain Fuse grows *each* Bomb by 6 and placing first meant three bombs got the +6 instead of two, turning a +12 card into a +18 card for the same energy. Then `Nicole — Revelation, Uncreated Light+` and `Defend`.

**Rejected:** `Chain Fuse` first, which is the natural reading order and costs 6 damage a turn forever. Seat 3 called `Chain Fuse` "a multiplier printed as though it were a flat buff"; the practical consequence is a **sequencing** rule the card never states — *place every bomb you are going to place before you play it.*

Took **4** (24 through 20 Block). **HP 13 → 9.**

**Turn 3 — a combo I built on the previous seats' rules, and it failed for a reason worth more than the combo.** Enemy at 154 with `Pyro Aura 1` and `Bomb 62`. My reasoning: `Sparks 'n' Splash` deals **Pyro** damage equal to the stack, so if I could leave a **Cryo** aura on the target, the end-of-turn tick would Melt and 62 would become 108. `Charlotte` is a Cryo attack and it was in hand carrying `*Reaction preview: Melt*`.

Played `Explosives Workshop+`, `Shrug It Off` (11 Block, draw), `Strike`, then `Charlotte` last. 154 → 133, exactly **21** = Strike 9 + Charlotte 12, where Charlotte's 12 is (4 + 3 Strength) × 1.75 truncated from 12.25. Every number exact.

**And then the aura was simply gone.** The next screen showed Soul Nexus with **no aura at all** — the Melt consumed the Pyro and Charlotte's "Applies Cryo" never fired. See finding 1: this is a rule the cards do state, in a clause nobody would read as load-bearing, and it silently killed the best line I found all session.

Took **0** (18 into 28 Block).

**Turn 4 — the turn the elite bit back.** The screen opened with `Vulnerable 2` and `Weak 2` **on me** — the first time this run an enemy has debuffed the player — and an intent of `9x4`. That is 36 base, **54 after my own Vulnerable**, into 9 HP. Simultaneously my `Weak 2` re-printed the badge as:

> **Bomb 63 (buff)** — Set off here deals 63 Pyro damage **after Weak**.

So the enemy's debuff shrank *my stack*, and the badge named which modifier it had applied — the good behaviour seat 3 logged for fight 15, on the turn it mattered most.

Enemy on 75. I played `Strike` (75 → 67), then `Jumpy Dumpty+`, and **stopped to read the badge before committing**, because the whole fight turned on whether one card was lethal:

> **Bomb 75 (buff)** — Set off here deals 75 Pyro damage after Weak. Bombs here: 4.

63 + 12, where 12 is Jumpy Dumpty+'s printed 11 plus 5 Strength, × 0.75 for Weak — the number I had predicted before playing it. 75 ≥ 67, so `Ka-pow!` — free, Retained since turn 4 of a four-round fight — **killed a 234-HP elite from 67**.

**Rejected:** the full-block line (Defend + Dig In+ + Thoma on top of Grounded's 12 = 48 Block against 54, plus Thoma's top-ups). It was *probably* survivable and it was not close to worth it: at 9 HP, "probably" is the whole run, and the badge had already told me the alternative was lethal.

**Won at 9/56 on round 4.** The elite landed 26 damage across four turns against a deck that spent every one of those turns refusing to detonate.

**Reward:** 37 gold, **`Letter Opener`** (relic), and a card — **skipped** (a third `The Big One`, a third `Explosives Workshop+`, `Fwoosh!`, `Jean — Gale Blade`). At 36 cards the finisher I already own two of is worth less than the draw consistency.

---

## Rest site (floor 9) and event: Grave of the Forgotten (floor 10)

Walked in on **9/56** and the screen already read **HP 30/56** — `Eternal Feather` paid **21** on entry (36 cards ÷ 5 = 7, × 3), before the rest-site choice was even offered. That is a third of my ceiling, free, for having the deck the rest of the run's economy told me to trim.

**Took `Smith` over `Rest`** (16 HP) on that arithmetic: the map showed a row of **three** rest sites immediately before the boss, and Eternal Feather turns each of those into 21 + 16 = 37, so healing here would have been the cheaper resource. **Upgraded `The Big One` → `The Big One+`, cost 3 → 2**, giving me two 2-cost quadruple finishers. The Smith screen prints the current face and the upgraded face side by side under "What you have picked", says "Confirm is available", and lets `skip` un-pick without leaving — the single best-designed screen in this bridge, and it is the one that needs it least.

**A small, checkable gap:** the Smith's list of upgradeable cards had 25 entries, and my deck is 36. Eight of the missing eleven are cards I know are already upgraded. The other three — `Powder Charge`, `Shinobu — Sanctifying Ring (proto)`, and the card the act-2 Symbiote event Transformed a `Strike` into — are not upgraded and are not on the list, and no line on the screen says why a card is absent.

**The event is the purest instance of the undefined-word wart anyone has logged**, because *both* options are made of nothing else:

> - **Confront with Truth** — Add **Decay** to your Deck. Enchant a card that Exhausts with **Soul's Power**.
> - **Accept the Forgotten Soul** — Obtain **Forgotten Soul**.

Four proper nouns, zero rules text, no decline, no glossary block. There is no reading of this screen that informs the choice; I picked the option with no stated downside and, as at The Round Tea Party, **the event never said what arrived.** I learned it two rooms later from the next combat's relic list: **`Forgotten Soul` — Whenever you Exhaust a card, deal 1 damage to a random enemy.** (The elite's relic was likewise only identified in combat: **`Letter Opener` — Every time you play 3 Skills in a single turn, deal 5 damage to ALL enemies.**)

---

## Fight 21: Globe Head — HP 148/148

Entered at **35/56**. The enemy printed one buff that is aimed squarely at this deck:

> **Galvanic 6 (buff)** — Powers are afflicted with **Galvanized**.

**`Galvanized` is not in the "Words on this screen" glossary.** That block, on this exact screen, defines `Bomb`, `Set off` and `Spark` and stops. So on round 1 — the turn you decide whether to install your engine — the enemy's entire mechanic is a word the screen refuses to define, on the one kind of screen every previous seat has praised for defining its words.

**And then, on round 2, it defined it perfectly.** `Grounded` came into my hand printing:

> **Grounded** — cost 1, power
> At the start of your turn, if none of your Bombs went off last turn, gain 6 Block. **Take 6 damage.**
> *Galvanized* — Take 6 damage when this card is played.

The debuff is written into the affected card's own body text *and* its keyword block — the same excellent behaviour seat 2 logged for `Tangled` and seat 3 for `Weak`. **The word is defined where it bites and undefined where it is announced.** That is a sharper, more fixable version of the complaint than "the glossary is missing", because the machinery to fix it demonstrably exists.

Its practical effect is a genuinely good fight: my deck runs five Powers (`Sparks 'n' Splash`, `Grounded`, `Alice's Recipe`, `Explosives Workshop+` ×2, `Nicole+`) and at 35 HP I could afford **none** of them. I played the whole fight without installing a single Power, on bombs, poison, one Companion and two relics — and won.

**Turn 1.** `Fish-Flavored Bait+`, `Strike`, `Shinobu`, `Dig In+`, `Defend`. 148 → 123, exactly **25** = Bait+ 10 (7 × 1.5 Vulnerable) + Strike 9 (6 × 1.5) + **Letter Opener 5, un-multiplied** + **Forgotten Soul 1** (Shinobu exhausting). See finding 4 — the two relics' damage is the only damage on the board that `Vulnerable` did *not* touch.

**Turn 2 — the Overload measurement.** 123 → 106 = **17** = Poison 4 + **13** from `Shinobu`'s printed *5 Electro* into the `Pyro Aura` my own Bait+ had left. I could not price that from any card face at the time. **Two rounds later the game handed me the formula unprompted**, on `Ka-pow!`:

> *Reaction preview: Overloaded* — This card supplies Pyro or Electro while an enemy has the other aura. It deals **6 splash damage to all enemies and applies 1 Weak** to the reacted enemy.

So Overload is not a multiplier at all: it is the hit, **plus a flat 6, plus Weak**. 5 × 1.5 (Vulnerable) = 7, + 6 = **13**. Exact. And it retro-explains nothing about Melt — the two reactions have completely different shapes, which is good design and is stated nowhere except on a card that happens to be in your hand.

Also on turn 2 the enemy applied `Frail 2 — Gain 25% less Block from cards for 2 turns`, and every block card in hand re-printed: `Shrug It Off` "Gain 6 Block" (8 × 0.75), `Defend` "Gain 3 Block" (5 × 0.75 = 3.75, truncated). Correct and legible, again.

**Turns 2–3** were `Shrug It Off` + `Defend` + `Metamorphosis`, then `Chain Fuse` + `Kirara` + `Run Away!+` — each a **three-Skill turn**, which is `Letter Opener`'s trigger, so a relic I acquired by accident quietly added 5 damage a turn to a fight where I had chosen to play no Powers. Both turns' totals were exact to the point (6 = 5 + 1; 22 = Kirara 10 + Letter Opener 5 + Shinobu 5 + Poison 2).

**Turn 4 — 60 damage from one 0-cost card, and the screen predicted all of it.** Board: Globe Head **70/148**, `Bomb 42` across 2 bombs, `Electro Aura 1` left by my own Shinobu, and `Sizzle` free in hand from `Metamorphosis`:

> **Sizzle** [Pyro] — cost 0, attack. Set off. Deal 6 damage. **If a Bomb triggered an Elemental Reaction this turn, deal 6 additional damage.**

I predicted 42 + 6 (Overload splash) + 6 (printed) + 6 (its own conditional, because the *bomb* would be what triggered the reaction) = **60**. **70 → 10. Exactly 60**, and `Weak 1` appeared on the enemy — Overload's rider — dropping its printed intent from 15 to 11 on the same screen.

That is the best single card interaction in the run: three cards' worth of text (`Set off`, a reaction preview on a *different* card, and a conditional keyed to bombs rather than to the card playing it) resolving to a number I could compute in advance. **Rejected:** `Ka-pow!` first, which is the same 60 rearranged; and rejected installing `Explosives Workshop+` or `Nicole+`, each of which was in hand and each of which prints "Take 6 damage" under Galvanized — 12 HP at 27/56 to speed up a fight I was about to win.

`Pocket Fireworks` (9) and `Ka-pow!` (4) finished it. **Won at 27/56 on round 4.**

**Reward:** 18 gold, `Strength Potion`, card **skipped** (`Catalytic Converter+`, `Flame Dance`, `Rapid Fire+`, `Mika — Starfrost Swirl`). The Strength Potion is the pick-up worth naming: after seat 3's finding, a potion that reads as an Attack buff is in this deck a **stack-size** potion, and it goes to the boss.

---

## Fight 22 (Elite): Mecha Knight — HP 300/300 — **the run ends here**

Entered at **27/56**, forced: the map offered exactly one node. `Mecha Knight` opened at 300 HP with a printed **25**, and one buff:

> **Artifact 1 (buff)** — Negates 1 debuff.

**And it had neither `Poison 4` nor `Vulnerable 1` on it, while `Artifact` still read 1.** Both of my start-of-combat relics fired in every other act-3 fight; here **one Artifact charge absorbed two separate debuffs from two separate relics and did not decrement.** Seat 3 logged the display half of this against the Chompers; this is the same wart with the arithmetic pinned down — one charge, two negations, counter unmoved, and no line anywhere saying a negation happened.

**Turn 1.** `Charlotte` first to dig (it found a `Defend`), then `Pocket Fireworks` into the Cryo Charlotte had left: **9 × 1.75 = 15**, and 300 → 281 is exactly 4 + 15. Then `Dig In+` (11) and `Defend` (5) — 16 Block against 25. **Took 9. HP 27 → 18.**

**Rejected:** `Powder Charge` over `Dig In+`. Both cost the one Spark I had, and at 27 HP against a printed 25 an 11-Block card beats a Bomb 6. **Rejected `Metamorphosis`**, which was in hand with the energy free: it adds 3 random **Attacks** to the draw pile, and the thing I needed to draw was Block. That is the first time this run that a card's *own quality* was irrelevant and its effect on the draw pile decided it.

**Turn 2 — the enemy printed 8, so I built.** `Fish-Flavored Bait+`, `Fish-Flavored Bait`, `Ammo Scavenging` (stack to 3 bombs), `Kirara` and `Run Away!+` for 14 Block. Three of those are Skills, so `Letter Opener` fired. **Took 0.**

**Turn 3 — the intent line lied by omission, and it is the sharpest screen-vs-outcome disagreement in this record.** The round-2 intent had read, verbatim:

> Intent: Aggressive (Attack) — the number on its icon is 8 — This enemy intends to Attack for 8 damage.

My round-3 hand opened with **four `Burn` cards in it**:

> **Burn** — cost 0, status. Unplayable. At the end of your turn, if this is in your Hand, take 2 damage.

Eight damage a turn, at 18/56, from an intent that announced 8 damage and nothing else. This game *has* a status-card intent — seat 3 recorded `Strategic (StatusCard)` on the Chompers — so the vocabulary to warn me existed and was not used.

I could not remove them, so I tested them: I played `Jumpy Dumpty+` (stack to 4 bombs), `Shrug It Off`, and both `Defend`s for **18 Block** on a turn the enemy intended to `Defend` and deal me nothing, purely to see whether Burn is blockable. **HP stayed 18/56 through four Burns.** So Burn's "take 2 damage" **is** absorbed by Block — which the card does not say. Playing four Skills also fired `Letter Opener` for a clean 5 (255 → 250, exact).

**Turn 4 — 40 into 23, with 12 Block available.** The enemy came off its `Defend` with `Block 15`, `Strength 5` and a printed **40**. My hand held `Thoma` (6), `Barbara` (6), `Pop!`, two `Strike`s and the retained `Ka-pow!` — **twelve points of Block for four energy, and no fourth block card in the deck's reach.**

I spent `Fruit Juice` (which prints "Gain 5 Max HP" and in fact did **both** — 18/56 → **23/61**, healing 5 as well as raising the ceiling, a rare case of a card under-promising), played `Thoma` and `Barbara` for 12, `Pop!` as a third Skill for Letter Opener, and both `Strike`s.

**Rejected:** `Ka-pow!` on the `Bomb 53`. Set off would have dealt 57 into 15 Block for 42, leaving the Knight on ~200 — and it would have spent the only win condition I had left. **Rejected:** `Barbara` as a *Frozen* play, which is what would have saved me: Frozen halves the enemy's next action, and 40 halved is 20 against 12 Block and 23 HP. It needs a Cryo or Hydro aura already on the target, my `Charlotte` was in the discard pile, and the Knight's aura had expired. **The one defensive tool in the deck that answers a 40-damage intent requires a two-card combination the deck cannot assemble on demand.**

40 − 12 = 28 into 23 HP. **The run ended on floor 46**, two floors below Aeonglass, with the boss never seen.

**What killed the run, stated plainly from the screens:** the Knight's intents across four rounds were **25, 8, Defend, 40**. The 8 was not an 8 — it was 8 plus four Burns worth 8 more a turn — and the `Defend` turn is what let the 40 arrive with `Strength 5` behind it. A deck whose block floor is a 5-point `Defend`, and whose two good block cards cost a currency (`Spark`) generated only by detonating, cannot answer a 40 on demand; and I had already spent the run's HP buffer on the *previous* elite, which the map gave me no way to avoid: **both act-3 elites were on single-node floors.**

---

## Findings, ranked by sharpness

### 1. A single-hit elemental card **consumes** the aura and applies **nothing**; a multi-hit one re-applies its own element

The clause, printed on every elemental card in the game, verbatim:

> *Applies Cryo* — If the target has no aura, this applies Cryo for 2 turns. **A different aura is consumed to trigger a Reaction instead.**

Fight 20, turn 3. Soul Nexus carried `Pyro Aura 1`. I played `Charlotte` (Cryo, one hit) deliberately last in the turn, because `Sparks 'n' Splash` deals **Pyro** damage equal to the stack at end of turn, and a Cryo aura would have made that 62-point tick a Melt worth 108. Charlotte hit for exactly 12 — (4 + 3 Strength) × 1.75 — **and the next screen showed Soul Nexus with no aura at all.** The tick landed as a plain 62.

Compare fight 17: `Ka-pow!` (Pyro, a **Set off**, i.e. several hits) into a `Cryo Aura` → the first hit Melted, and the enemy ended the exchange wearing `Pyro Aura 2`. Same in fight 21 with `Sizzle` into `Electro Aura`, and again in fight 22 with `Pocket Fireworks`.

So the rule is: **a reaction eats the aura and cancels your element; only a card with a *second* hit gets to leave its own aura behind.** The word carrying that is "instead", and nothing else on any screen says it. It is the difference between a combo that doubles the engine and a combo that disarms it — I built the line, played it, and watched it evaporate.

### 2. Four Elemental Reactions, four completely different shapes, and none of them is in the glossary

- **Melt** — "The triggering hit deals **1.75x** damage and consumes the aura."
- **Vaporize** — "The triggering hit deals **1.5x** damage and consumes the aura."
- **Frozen** — "**Its next action deals half damage**; attacking it Shatters for 6 damage." (boss variant: "Bosses cannot be Frozen … applies **2 Vulnerable** instead")
- **Overloaded** — "It deals **6 splash damage to all enemies and applies 1 Weak** to the reacted enemy."

Two multipliers, a defensive debuff, and a flat splash-plus-Weak. **None of the four appears in the "Words on this screen" block**, on any screen, ever — that block carries `Bomb`, `Set off`, `Spark`, `Mine`, `Block`, and stops. A reaction is stated only as a `*Reaction preview:*` line on a card that happens to be in your hand *and* happens to supply the right element *and* only while the aura is already on the board.

The consequence is measurable. Fight 21, round 1: `Shinobu`'s tick printed *5 Electro* and dealt **13** into a Pyro aura. I could not price it — no card in hand carried an Overload preview — so I logged 13 and moved on. **Two rounds later the formula arrived unprompted on `Ka-pow!`**, and 5 × 1.5 (Vulnerable) + 6 (Overload splash) = **13**, exact. The rule existed the whole time; whether I was allowed to see it depended on my draw.

### 3. `Galvanized` is announced by the enemy and defined nowhere — then written perfectly into the card it hurts

Fight 21, round 1, the enemy's only mechanic:

> **Galvanic 6 (buff)** — Powers are afflicted with **Galvanized**.

The "Words on this screen" block on that same screen defines `Bomb`, `Set off` and `Spark`. Not `Galvanized`. So on the one turn where the decision is "do I install my engine", the price of installing it is a word the screen will not define.

Round 2, `Grounded` came into hand:

> **Grounded** — cost 1, power
> At the start of your turn, if none of your Bombs went off last turn, gain 6 Block. **Take 6 damage.**
> *Galvanized* — Take 6 damage when this card is played.

Body text rewritten, keyword defined, both correct. **The machinery that fixes the round-1 screen is the machinery that got round 2 right**: the glossary needs to read the enemy's buff text as well as the cards in hand. This is the most fixable finding in the record.

(The mechanic itself makes a good fight. My deck runs five Powers and at 35/56 I could afford none of them, so I won that fight without installing a single one — the first time in 22 fights that "don't play your deck" was the right answer.)

### 4. `Vulnerable` moves card damage that is not an Attack, and does not move relic damage

Printed: `Vulnerable 1 (debuff) — Receive 50% more damage from **Attacks** for 1 turn.`

What it multiplied, each exact:

- `Kamisato Ayaka — Soumetsu`'s end-of-turn Cryo tick — a **Skill**, whose damage is dealt by a buff two steps later: 8 → **12** on all four bodies (fight 19).
- Every bomb badge: `(6+6) × 1.5 = 18`; `(6+5) × 1.5 = 16.5 → 16` (fights 18, 20).
- `Fish-Flavored Bait+`: 7 → **10**.

What it did **not** multiply:

- `Letter Opener`'s 5 (fight 21, round 1: 148 → 123 is exactly 10 + 9 + **5** + 1).
- `Forgotten Soul`'s 1.

"Attacks" is therefore wrong in both directions on the same screen: it understates (Skills and bombs *are* boosted) and overstates (relic damage is not). Seat 3 proved the first half for bombs; the Ayaka case widens it to Companion Skills, and the Letter Opener case is the first *negative* result any seat has recorded.

### 5. An intent that printed "Attack for 8 damage" also put four unplayable cards in my hand

Fight 22, round 2, verbatim:

> Intent: Aggressive (Attack) — the number on its icon is 8 — This enemy intends to Attack for 8 damage.

Round 3 opened with **four `Burn`s** in hand — "Unplayable. At the end of your turn, if this is in your Hand, take 2 damage" — i.e. 8 HP a turn, doubling the announced cost of that intent, at 18/56, in the fight that ended the run. The bridge has a status-card intent type (`Strategic (StatusCard)`, seat 3's fight 13), so the vocabulary existed and was not used.

**The consolation finding, which I got by testing it:** I held 18 Block on a turn the enemy intended to Defend, kept all four Burns, and **took 0**. Burn is blockable. The card does not say so, and it is the opposite of the usual convention, so a player who reads the card correctly will overpay to be rid of them.

### 6. `Artifact 1` ate two debuffs from two relics and never decremented

`Mecha Knight` opened with `Artifact 1 (buff) — Negates 1 debuff`, **no `Poison`, no `Vulnerable`**, and `Artifact` still reading **1** for the whole fight. `Twisted Funnel` (4 Poison to ALL) and `Bag of Marbles` (1 Vulnerable to ALL) both fired correctly in fights 17, 18, 19, 20 and 21. One charge, two negations, counter unmoved, and no screen saying a negation occurred — so from the player's chair two relics simply did not work, silently. This sharpens seat 3's finding 7, which had one debuff and a display complaint; the arithmetic here says either the rule or the counter is wrong, not just the display.

### 7. Two more events name a thing and never say what arrived — and one is made of nothing but undefined words

> **The Round Tea Party** — `Enjoy Your Tea` — Obtain **Royal Poison**. Heal to full HP. / `Pick a Fight` — Lose 11 HP. Obtain a random Relic.

> **Grave of the Forgotten** — `Confront with Truth` — Add **Decay** to your Deck. Enchant a card that Exhausts with **Soul's Power**. / `Accept the Forgotten Soul` — Obtain **Forgotten Soul**.

The Grave is the purest instance any seat has logged: **four proper nouns, zero rules text, two options, no decline.** There is no reading of that screen that informs the choice.

Both events then **declined to name what they gave me.** I learned that the Tea Party's random relic was `Bag of Marbles`, and that `Forgotten Soul` is "Whenever you Exhaust a card, deal 1 damage to a random enemy", from the **relic list of a later combat screen**. With seat 2's `Sown` and `Golden Compass` and seat 3's `Pollinous Core`, `Metamorphosis`, `Corrupted` and `Transform`, plus this act's `Jumpy Dumpty Mk.Omega+` (shrine), `Royally Approved` (shop) and `Royal Poison`, that is **eleven one-way choices across four seats** in the same shape. Every one is on an event, shrine or shop screen; none of those screens carries a glossary block.

Related and unexplained: HP went from the **43/62** seat 3 recorded to **62/62** across the Darv shrine, with no screen printing a heal. I did not `observe` between the map and the first combat, so I cannot say which screen did it — only that 19 HP appeared and nothing announced it.

### 8. The shop tells you an item's category only after you can no longer act on it

`Fysh Oil` printed as `**Fysh Oil** — 74 gold / Gain 1 Strength and 1 Dexterity` — a bare name, a price and an effect, in the identical format used by `Vambrace`, `Stone Calendar` and `Royal Stamp` one line above. I bought it as a permanent Strength relic, which after seat 3's finding is a **bomb-size** relic and would have been the best 74 gold in the act. It is a potion. The only disclosure is the **sold-out** line, which re-printed the slot as `**Potion** — 74 gold (not available)`.

The sold-out **card** shelves, by contrast, explain themselves at length: *"Bought, or never stocked. The game clears a shelf's card the moment it is sold, and the name, the text and the cost all live on that card, so nothing on the feed can say which one it was."* The screen is scrupulous about what it cannot tell you and careless about what it can.

### 9. A claimed potion vanished with no message

I claimed `Fire Potion` off fight 19's reward screen and the tool answered `ok Claiming reward: potion (Fire Potion)`. The next combat listed three potions and `Fire Potion` was not among them. Three slots, four potions, and **no line on either screen** saying the claim had failed or that a slot was full.

### 10. Rounding is always down, and `Fruit Juice` under-promises

`Bomb 16` where (6 + 5) × 1.5 = 16.5 (fight 20); `Defend` printing "Gain 3 Block" where 5 × 0.75 = 3.75 (fight 21); Melt landing 12 where (4+3) × 1.75 = 12.25. Rounding is consistently **down**, which matters when a lethal is computed off a badge — I committed to one this session that was lethal by 8.

`Fruit Juice` prints "Gain 5 Max HP" and moved me **18/56 → 23/61**: it healed 5 as well. The one card all session that does more than it says.

### 11. Two things this bridge does very well, stated as findings because they are checkable

**Buff stacking is displayed by rewriting the number into the text.** Two `Grounded`s produced one line — `Grounded 12 (buff) — At the start of your turn, if none of your Bombs went off last turn, gain **12** Block` — rather than two lines of 6. And that same line settles a rule: `Dexterity 2` was up and the buff still said 12, not 16, because Dexterity's own text is "Increases Block gained from **cards**" and Grounded's Block comes from a Power. Both halves correct, both legible without a manual.

**Every modifier applied to me was re-printed on the affected card face.** `Shrink` (seat 1), `Tangled` (seat 2), `Weak` (seat 3), and this session `Dexterity` (`Defend` → "Gain 7 Block"), `Strength` (`Strike` → "Deal 9 damage", `Ka-pow!` → 7), `Frail` (`Shrug It Off` → "Gain 6 Block", `Defend` → 3) and `Galvanized` ("Take 6 damage"). Four seats, seven modifiers, no exceptions.

### 12. `Chain Fuse` has a sequencing rule it does not print

> **Chain Fuse** — cost 1, skill. **Each** Bomb on the enemy grows by 6.

Fight 20 turn 2 I placed `Fish-Flavored Bait` *before* Chain Fuse on purpose, turning a two-bomb +12 into a three-bomb +18 for the same energy. The rule — *place every bomb you intend to place before you play it* — follows from "Each" and is stated nowhere. Seat 3 called the card "a multiplier printed as though it were a flat buff"; the practical form of that complaint is an ordering rule left to the player to derive.

### 13. The Smith's upgrade list omits cards without saying why

The upgrade screen listed **25** cards against a deck of 35–36. Eight of the missing are already upgraded, which is obviously right. The remainder — `Powder Charge`, `Shinobu — Sanctifying Ring (proto)`, and the card the act-2 Symbiote event Transformed a `Strike` into — are not upgraded and are not listed, and no line explains the absence. On a screen that is otherwise the most scrupulous in the bridge (side-by-side faces, `skip` to un-pick, an explicit "Confirm is available"), a silent omission is conspicuous.

*(Unranked, and it deserves saying as loudly as seat 3 said it: the **arithmetic is honest**. Across six fights I checked roughly thirty outcomes against the screens — 60, 75, 63, 62, 53, 52, 42, 25, 22, 21, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 6, 5 — and every one was exact, or exact after a truncation I could see on the screen. `Set off`, quadruple, per-bomb growth, `Alice's Recipe`, `Explosives Workshop+`, `Chain Fuse`, `Poison`, `Letter Opener`, `Forgotten Soul`, `Eternal Feather` (21 = 3 × 7), `Candelabra`, `Velvet Choker`, `Pounding Surprise`, Melt, Vaporize, Overload, and every `Vulnerable` / `Weak` / `Strength` / `Dexterity` / `Frail` interaction landed on the number. **Everything above is wording, labelling and disclosure, not maths.**)*

---

## What the previous records got wrong or right

- **"Strength, Weak and Vulnerable modify Bomb damage."** *(seat 3, finding 1)* — **Right, confirmed four more times, and widened.** `Bomb 18` = (6+6) × 1.5; `Bomb 16` = (6+5) × 1.5 truncated; `Bomb 63` and `Bomb 75`, both badged "*after Weak*"; and `Jumpy Dumpty+`'s printed 11 entered a stack as **12** = (11 + 5 Strength) × 0.75, a number I predicted before playing the card and then read off the badge. I also extended the rule past bombs — `Vulnerable` multiplied `Kamisato Ayaka`'s Cryo tick 8 → 12 on four bodies at once — and found its edge: it does **not** touch relic damage (finding 4).

- **"A Melt preview multiplies the Bomb hit, not the card's number."** *(seat 3, finding 2)* — **Neither confirmed nor refuted, and I would rather say so than pad it.** My fight-17 instrument (`Bomb 9`, a printed 4, result exactly **16**) is arithmetically symmetric: 5 × 1.75 + 4 + 4, and 9 + (4 × 1.75), and 4 × 1.75 + 5 + 4 all give 16. What I did prove is finding 1 — *which hits carry your element afterwards* — which is the half of the rule that decides whether a Melt line can be built at all. And I confirmed a third time that **the badge never prices the reaction**: `Bomb 9` on a Cryo-aura'd target produced 16 against a card-face 13, with the word "Melt" printed on the card and nowhere on the badge.

- **"A lethal Mine does not pre-empt the hit."** *(seat 3, finding 3)* — **Not re-tested.** No fight this session put a Mine on an enemy that was inside its own Mine's damage; the only Mine I placed all act was on the 250-HP Knight in the turn before I died. Seat 3's instance had exact numbers and a single attacker and I have no reason to doubt it.

- **"The badge folds `Vulnerable` in silently while it names `Weak`."** *(seat 3, finding 8)* — **Right, and I confirmed it as a prediction rather than a post-hoc read.** Before playing anything in fight 18 I committed to the claim that `Powder Charge` + `Chain Fuse` under Bag of Marbles would badge at **18**, not 12. It badged at 18, with the word "Vulnerable" nowhere on it — and two fights later the same badge said "**after Weak**" in the same slot. Same furniture, one modifier named, the other not.

- **"`Very Hot Cocoa` adds energy to the one turn that is already hand-limited."** *(seat 3, finding 11)* — **Right, and `Velvet Choker` is the proof by contradiction.** I took the +1-energy-per-turn relic whose cost is a 6-cards-per-turn cap on exactly seat 3's reasoning, and across six fights **the cap bound zero times**: I reached six cards on three separate turns and each time had nothing left to play. Meanwhile the +1 was live on every turn from three onward. A relic whose drawback is unreachable is the cleanest confirmation of their measurement I could have run.

- **"The kit's two best block cards are priced in a currency only the opposite strategy generates."** *(seat 3, finding 10)* — **Right, and it is what killed the run.** At the Mecha Knight I held `Dig In` printing `CANNOT BE PLAYED: you have no Spark, and this costs 1` on two separate turns, because I had spent the fight refusing to detonate — which is exactly what `Grounded` and `Sparks 'n' Splash` pay you to do. The deck's answer to a 40-damage intent was in my hand, unplayable, for the reason seat 3 named a session earlier.

- **"Never detonate for tempo you do not need."** *(seat 3's amendment of seats 1 and 2)* — **Right, and act 3 charges for tempo harder still.** I detonated four times and each was forced by a clock the fight printed: a one-turn Vulnerable window (fight 18), a lethal check against a rising Strength (fight 20), an Electro aura about to expire (fight 21), a `Soumetsu` counter running out (fight 19). The turn I *refused* — fight 22, round 4, holding `Ka-pow!` on a `Bomb 53` — is the turn I died on, and I still think refusing was right: 42 into a 250-HP body was not a plan, it was a gesture.

- **"Fire the free detonator into the empty board before placing anything."** *(seat 2's best discovery, generalised by seat 3 to five cards)* — **Right, and now conditional.** Fight 17 turn 1 gave me **two** detonators at once: `Big Badda Boom` free from the Puzzlebox, and `The Big One` in hand. Big Badda Boom's "then deal damage equal to what the Bombs dealt" *doubles* a stack; The Big One's quadruples it. So the rule becomes: **fire the weaker detonator into the empty board and save the multiplier for the stack.** I banked a clean 12 and then killed a 35-HP body with a quadrupled 8.

- **"`Flame Dance` is worded to switch itself off against the kit's own Pyro — but is correct on turn one."** *(seats 1 and 2 declined it; seat 3 played it)* — **Right, and the pattern generalises past that card.** `Sizzle`'s conditional ("If a **Bomb** triggered an Elemental Reaction this turn, deal 6 additional damage") is keyed to the bomb, not to Sizzle, so it collects on a reaction that its *own* Set off caused a moment earlier. That chain — Set off → first bomb Overloads → Sizzle's conditional sees it → +6 — is how one 0-cost card did 60 damage in fight 21, and it is the single most satisfying thing I found.

- **"Seat 3's `Sling of Courage` rejection was the most expensive mistake of that session."** — **Endorsed, and I nearly repeated it.** `Fysh Oil` (1 Strength, 1 Dexterity) is a bomb-size item in this deck and I bought it partly on that corrected reasoning. It turned out to be a potion, which is a disclosure failure rather than a judgement error (finding 8). The `Strength Potion` from fight 21 went unspent, because the run ended two floors later.

---

## What act 3 asked of the deck that acts 1 and 2 did not

**It attacked the deck's identity, not its numbers.** Act 2's best fight (`Hard To Kill 9`) inverted one stat — stack size stopped mattering and bomb count started. Act 3 went after the pieces:

- **`Galvanic` taxes Powers.** This deck is five Powers deep — `Sparks 'n' Splash`, `Grounded`, `Alice's Recipe`, `Explosives Workshop+` ×2, `Nicole+` — and Globe Head charged 6 HP to install each one. At 35/56 the correct line was to run the whole fight with **no engine at all** and win on bombs, poison, one Companion and two relics. Nothing in acts 1 or 2 ever made "do not play your deck" the right answer.

- **`Paper Cuts` makes damage permanent.** Blocking stopped being an HP trade and became a Max-HP trade, and a `5x2` became strictly worse than a single `14` — the first time in the run that the *shape* of an intent mattered more than its total. It cost me 6 Max HP in one turn, permanently, and every later fight was fought on the smaller ceiling.

- **Enemies debuff the player.** Acts 1 and 2 debuffed my *cards* (`Shrink`, `Tangled`, `Weak` on a card face). Act 3's `Vulnerable 2` + `Weak 2` (Soul Nexus) and `Frail 2` (Globe Head) hit the two axes the deck cannot rebuild: `Weak` shrinks the stack you spent five turns growing, and `Frail` shrinks the block you were going to survive on. `Weak` reading the **badge** is the sharp part — an enemy debuff retroactively devalues a resource you have already banked, and the badge tells you so to the point.

- **`Rampart`, `Artifact` and enemy `Block` all say the same thing: your one big number is the wrong shape.** Living Shield hands 25 Block a turn to somebody else; Mecha Knight blocks 15 the turn before it swings 40; Artifact eats both of the relics that open every fight for me. Act 3 is full of ways to make a stack arrive at the wrong moment against the wrong body.

- **Above all, act 3 asks for block on a schedule, and this deck cannot make one.** The Mecha Knight's four intents were **25, 8, Defend, 40**. Nothing in 36 cards answers a 40 except a two-card `Frozen` combination that needs an aura already on the target. The only *scheduled* block is `Grounded` (12 a turn with two copies in play) and `Nicole+` (5 a turn) — and both are Powers, which is what `Galvanic` taxes, and `Grounded` switches itself off the moment you detonate, which is what killing anything requires.

**And the map asked one thing that has nothing to do with the deck:** of the twelve act-3 floors I walked, **eight offered exactly one node** — including **both elites**. Seat 1 counted the same shape in act 1 and seat 3 in act 2. I could not route around a 300-HP elite at 27/56 because there was nothing to route to, and the run ended there.

**What act 3 did *not* ask, and it belongs on the record because seat 3 predicted it would:** the `random enemy` clause still never bit. Fight 19 was the only four-body fight of the act, and `Kamisato Ayaka — Soumetsu` — 8 + 8 + 16 to **ALL** enemies on a printed schedule — cleared it in two rounds without the clause ever being consulted. Four seats have now named "a random enemy" as the kit's worst line, and no seat has yet been punished by it, because the answer has been sitting in the deck since the act-1 boss reward.

---

## Non-blindness declaration

- **Commands outside the two allowed ones:** none. Every game interaction was `GITS_LANE=2 python -m understudy.blindplay observe` or `GITS_LANE=2 python -m understudy.blindplay act "<command>"`. I never ran `harness`, `session`, `audit`, `notes`, `scenario`, `staged_turn`, `soak`, git, python, or any file listing.
- **Tools used:** the **Bash** tool for every game call; the **Read** tool three times, for the three previous seats' records, before touching the lane; the **Write** tool for this file and for two scratchpad fragments of this file's own text; and the **Edit** tool once, on this file's Identity block.
- **Other shell usage, all of it output-trimming or call-chaining on the two allowed commands:** `cd` to the repo at the head of each call; `for c in ...; do ... done` loops and newlines to issue several `act` calls plus a closing `observe` in one tool call (each looped `act` counted as one accepted action); `| tail -N`, `| head -N`, `grep -E`/`grep -A` and `| sed -n '...p'` to print only the state, hand and enemy sections of an `observe`; `cat >> …` and `wc -l`/`tail` against **this record file only**.
- **Repo files read:** `review/qa/klee-round-7b-2026-09-02/opus-act1.md`, `opus-act2.md` and `opus-act2b.md`, once each, first, as the brief required. **No other repo file was read** — no source, no YAML, no design doc, no ruling, no backlog.
- **The lane:** left exactly where the run ended, on `TOOL-BLOCKED: game_over`. Nothing was launched, closed, restarted or torn down, and lane 1 was never touched.

---

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
