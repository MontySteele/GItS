# KLEEMOD-KOKOMI — blind seat, lane 1, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 5, first of three chained seats.
- **Lane:** 1
- **Character:** KLEEMOD-KOKOMI
- **Run seed:** never printed on any screen.
- **Act:** 1. Map header printed: `At the top of this act: **Waterfall Giant**`.
- **Actions accepted:** **191**. **Refused: 1** (one, at the card-removal confirm screen — see Shop 1).
- **Termination reason:** **stop condition (2), the run ends.** `TOOL-BLOCKED: game_over` / `the run is over; there is nothing left to play` / `The run ended on floor 17.`
- **Where the run stands:** the act-1 boss **Waterfall Giant was killed** on round 6 of the boss fight, and then its `Steam Eruption` corpse killed me on round 7 for **27 damage against 26 HP**, one point short. The lane stands on the game-over state at floor 17. There is no act-2 map to hand on.
- **HP trajectory — every reading any screen printed, in order:**
  `64/80` · `62` · `56` · `52` · `44` · `44` · `44` · `44` · `36` · `30` · `30` · `30` · `26` · `26` · `26` · `21` · `21` · `21` · `21` (rest site) → `45` · `45` · `34` · `31` · `31` · `31` · `31` (rest site) → `55` · `55` · `46` · `43` · `38` · `32` · `32` (rest site) → `56` · `56` · `56` · `52` · `46` · `46` · `26` · `26` · **dead**.
  Max HP was `80` on every reading and never moved.
- **Gold:** never printed at Neow or on any map/reward screen as a running total — only inside shops. Reward screens printed `13`, `18`, `14`, `16`, `45`, `45`, `35` = 61+112 banked; shop 1 opened at **160 gold** and shop 2 at **208**, so a starting stake of roughly 99 gold was never shown anywhere. Final: **37 gold**.
- **Potions:** at death, **none**. Held over the run: `Energy Potion` (fight-1 reward, spent on Elite 1 turn 1), `Powdered Demise — Enemy loses 9 HP at the end of each of its turns` (fight-3 reward, spent on the Haunted Ship turn 1), `Attack Potion — Choose 1 of 3 random Attack cards to add into your Hand. It's free to play this turn.` (Elite 2 reward, spent on boss turn 5), `Potion-Shaped Rock — Deal 15 damage` (granted each combat by Petrified Toad, spent on boss turn 3).
- **Relics, exactly as printed:**
  - `Tamakushi Casket — Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy.` (starting)
  - `Fishing Rod — Every 3 normal combats, Upgrade a random card in your Deck.` (Neow)
  - `Paper Krane — Enemies with Weak deal 40% less damage to you rather than 25%.` (Elite 1)
  - `Sparkling Rouge — At the start of your 3rd turn, gain 1 Strength and 1 Dexterity.` (Treasure)
  - `Strike Dummy — Cards containing "Strike" deal 3 additional damage.` (Elite 2)
  - `Petrified Toad — At the start of each combat, procure a Potion-Shaped Rock.` (Elite 3)
  - `Centennial Puzzle — The first time you lose HP each combat, draw 3 cards.` (Treasure)
- **Deck at death — 17 cards**, reconstructed from faces printed in hand and cross-checked against the boss fight's own count (`Piles: 12 in the draw pile, 0 discarded` + 5 in hand = 17):
  Strike ×1, Strike+ ×1, Defend ×4, Kurage's Oath, Slack Water+, Exposed Flank ×2, Feint+, Undertow ×2, Vanguard, Ambush ×2, Sango Isshin.
  Starting deck was **10**: Strike ×4, Defend ×4, Kurage's Oath, Slack Water — established from fight 1, where turn 1 held Defend ×3 + Kurage's Oath + Strike with 5 in the draw pile, and turn 2 drew Strike ×3 + Defend + Slack Water with the pile then empty.

---

## Floor 0 — Neow

Screen printed three options and nothing else — no HP, no deck, no gold:

- **Fishing Rod** — Every 3 normal combats, Upgrade a random card in your Deck.
- **Booming Conch** — At the start of Elite combats, draw 2 additional cards and gain [Energy].
- **Precarious Shears** — Remove 2 cards from your Deck. Lose 16 HP.

**Prediction / reasoning.** Blind, with no HP reading on the screen, `Lose 16 HP` was an unpriced cost — I could not see the denominator it came out of. Fishing Rod pays across all three acts and costs nothing. Took **Fishing Rod**.

Note: the Neow screen never printed my HP, my deck, my gold or my relics. The first HP reading in the whole run arrived on the first battle screen.

## The map (act 1)

16 floors to the boss. Two openings, `Monster (path 1)` (leads on to one Monster) and `Monster (path 2)` (leads on to two Monsters). Took path 2 for the wider fan.

Printed floor list, nearest first:

```
1: Monster, Monster
2: Monster, Monster, Monster
3: Unknown, Monster, Monster
4: Monster, Shop, Monster, Monster
5: Monster, Monster, Shop, Unknown
6: Monster, Unknown, Unknown, Monster
7: Monster, Elite, Elite, Monster
8: RestSite, Unknown, RestSite, Monster
9: Treasure, Treasure, Treasure, Treasure
10: Elite, Elite, Unknown, Shop, RestSite, Monster
11: RestSite, Unknown, RestSite, Unknown
12: Elite, Monster, RestSite, Elite, Elite, RestSite
13: Unknown, Elite, Unknown, Monster
14: Unknown, Unknown, Monster
15: RestSite, RestSite
16: Boss
```

## Fight 1 — Toadpole ×2

Opening screen (round 1): **HP 64/80**, Block 0, Energy 3/3, draw pile 5.

Relics as printed:

- **Tamakushi Casket** — Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy.
- **Fishing Rod** — Every 3 normal combats, Upgrade a random card in your Deck.

The companion, printed as its own section every battle screen:

> The Bake-Kurage is on the field for the whole fight. Enemies cannot touch it. Play a card on it to write its **Plan** line instead of playing the card now.
> Nothing is planned. The morning is empty.

Enemies: `Toadpole (1)` HP 24/24, intent *Empower (Buff)*; `Toadpole (2)` HP 23/23, intent *Aggressive — the number on its icon is 7*.

Hand: Defend ×3 (1e, 5 Block), **Kurage's Oath** (1e skill, "Play on the Bake-Kurage. Plan: Deal 7 damage to ALL enemies."), Strike (1e, 6 damage).

**Turn 1, predicted:** Oath on the Kurage (1e) to bank 7-to-all for next turn; Strike Toadpole (2) 23→17; Defend for 5, so the printed 7-damage intent lands for 2. Predicted HP 62.
**Turn 1, happened:** exactly that. Toadpole (2) 17/23, HP 62/80 on the round-2 screen. The Kurage section changed to `Planned, and carried out at the start of your next turn in this order (1): 1. Kurage's Oath`, and a second status line appeared, `Plan 1 (buff) — Carries out 1 Plan at the start of your next turn, in order.`

**Turn 2 opening screen** resolved the Plan and printed the receipt:

> The Bake-Kurage carried these out at the start of this turn, front first:
> - Bake-Kurage: Kurage's Oath, 7

Toadpole (1) 24→17, Toadpole (2) 17→10. **Both** enemies took 7, matching the card's own "Deal 7 damage to ALL enemies" and NOT the Plan glossary line, which says on every single screen: *"the Plan lands first thing next turn on the front enemy."* First contradiction of the run.

Also on that screen, unannounced: **both** Toadpoles now carried `Hydro Aura 1 (aura)`. Kurage's Oath prints no `[Hydro]` tag and no `Applies Hydro` clause — the aura arrived from the companion carrying it out, and nothing on the card said it would.

Toadpole (1) had gained `Thorns 2 (buff) — When hit by an attack, deal 2 damage back` (that was its Empower), and its intent turned to `3x3` = 9. Toadpole (2) now intended Empower.

New card seen: **Slack Water** `[Hydro]` — 1e attack, "Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies." with the *Applies Hydro* clause.

**Turn 2, the real decision.** Two lines were within one point of each other on paper:
- (a) 2 Strikes kill Toadpole (2) at 10 HP with **no** Thorns cost, + Defend 5 vs the 9-damage intent → take 4 → HP 58, leaving a 17 HP Thorns enemy to kill through 6 Thorns next turn. Total to end of fight: 10 HP.
- (b) 3 Strikes = 18 kills Toadpole (1) at 17 HP through Thorns 2 ×3 = 6 → HP 56, leaving a 10 HP enemy to kill through 4 Thorns next turn. Total to end of fight: 10 HP.

Identical on paper; I took (b) because its turn 3 needs only two attacks rather than three, so it fails softer. **Predicted HP 56.**
**Happened:** Toadpole (1) dead, HP 56/80 exactly. Thorns fired on the killing blow too (3 hits × 2 = 6, not 4).

**Turn 3:** drew Strike ×4 + Defend. Toadpole at 10/23 with Thorns 2, intent 3x3. Two Strikes = 12 killed it; predicted 4 Thorns → HP 52.

**Reward screen:** `13 Gold`, `Energy Potion`, `Add a card to your deck.` — the reward screen prints no HP, so 52 is my arithmetic, not a reading.

Card options offered:

- **Coral Bulwark** — 1e skill, Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak.
- **Exposed Flank** — 1e skill, Apply 1 Vulnerable. Plan: Apply 2 Vulnerable to ALL enemies.
- **Stolen Chapter** — 1e skill, Draw 2 cards. Plan: Draw 4 cards.
- **Sucrose — Astable Anemohypostasis** — 0e skill, Swirl ALL enemies. Exhaust. (*Swirl* — The enemy's aura is consumed and copied onto ALL enemies. No aura, no effect.)

Took **Exposed Flank**: it is the only card on offer that turns the Casket's "whenever you apply a debuff … 2 Hydro damage" into free damage, the Plan glossary explicitly says *"Enemy Vulnerable raises it"* so it scales the Kurage, and the deck's whole damage output at this point is a 6-damage Strike.

**Deck after fight 1 (10 → 11):** Strike ×4, Defend ×4, Kurage's Oath, Slack Water, Exposed Flank.

## Fight 2 — Corpse Slug ×2

Opening: **HP 52/80** (exactly the number my turn-3 arithmetic predicted, so the reward screens' silence about HP was recoverable). Fishing Rod now prints a counter: `**Fishing Rod** (1)`. Potions section appeared for the first time: `1 of 3 slots are full. — **Energy Potion** — Gain [Energy][Energy].`

Enemies: `Corpse Slug (1)` 26/26, intent Attack 8; `Corpse Slug (2)` 27/27, intent Debuff. Both carried
`Ravenous 4 (buff) — When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and gaining 4 Strength.`

**Turn 1 — the best decision of the run so far.** Hand: Exposed Flank, Strike ×3, Kurage's Oath. I stacked *two* Plans on the Kurage in a deliberate order — Exposed Flank first, then Kurage's Oath — betting that the Kurage resolves them in the order written and that the Vulnerable therefore lands before the damage. Third energy into a Strike on Slug (1). Predicted: take 8, HP 44; at the top of turn 2 both slugs eat 2 Vulnerable, take the Casket's 2, and then take 7×1.5.

**Happened.** The round-2 screen printed:

> - Bake-Kurage: Exposed Flank, 2
> - Bake-Kurage: Kurage's Oath, 10

HP 44/80 ✓ (8 taken). Slug (1) **7/26**, Slug (2) **14/27**. Slug (2) had taken no direct card, so its 13 HP loss is entirely the two Plans — but the receipt above adds to **12**. One point is unprinted. The turn-2 result resolves which line is short: Slack Water (base 4) on a Vulnerable target dealt exactly 6, i.e. 4×1.5, and the target went 14 → 5, a 9-point drop = 6 damage + **3** from the Casket. So the Casket's "2 Hydro damage" is itself amplified by Vulnerable to 3, and the Kurage's receipt line prints the **base** number of the card, not the number actually dealt. `Exposed Flank, 2` dealt 3; `Kurage's Oath, 10` dealt 10 (7×1.5, rounded up from 10.5).

Slug (2)'s debuff landed as `Frail 2 — Gain 25% less Block from cards for 2 turns`, and the honest thing here is that my Defends immediately **re-printed their own face** as `Gain 3 Block` rather than 5. The card text tracks the debuff. Good.

**Turn 2.** Killed Slug (1) with a Strike (9 into 7), which triggered Ravenous — the survivor ate it and the screen printed `Intent: Stunned (Stun)`, `Strength 4 (buff)`, so the eat costs the enemy a whole turn. Slack Water into Slug (2) took it to 5 as computed. Defend gave 3, not 5 (Frail).

**Turn 3.** Slug at 5/27 with intent `7x2` (3 base + Strength 4). One Strike killed it. **No HP lost on turns 2 or 3** — HP 44 throughout.

Reward: `18 Gold`, `Add a card to your deck.` Offered:

- **Feint** [Hydro] — 1e attack, Deal 6 damage. Plan: Deal 10 damage.
- **Vanguard** — 0e skill, Play on the Bake-Kurage. Plan: Apply 1 Vulnerable and 1 Weak. Exhaust.
- **Tide Wall** — 1e skill, Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning.
- **Thoma — Blazing Barrier** — 1e skill, Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block.

Took **Feint**. Its Plan is 10 damage for 1 energy — a 67% jump over its own face and the highest single number my deck could reach; against a Vulnerable target it reads 15.

**Deck after fight 2 (12):** Strike ×4, Defend ×4, Kurage's Oath, Slack Water, Exposed Flank, Feint.

## Fight 3 — Sludge Spinner

Opening: **HP 44/80**, Fishing Rod `(2)`. One enemy, `Sludge Spinner` 37/37, with a two-line intent:

> Intent: Aggressive (Attack) — the number on its icon is 8
>   and also: Strategic (Debuff) — This enemy intends to apply a Debuff to you.

**Turn 1.** Hand had no Exposed Flank and no Feint. Kurage's Oath on the Kurage (7 banked beats a 6-damage Strike for the same energy) + Strike ×2. Predicted: enemy 37−12 = 25, then −7 at the top of turn 2 = 18; me 44−8 = 36.
**Happened:** enemy **18/37**, me **HP 36/80**. Exact.

The debuff landed as `Weak 1 — Attacks deal 25% less damage for 1 turn`, and again every attack card in hand re-printed its own reduced face: `Strike — Deal 4 damage` (6×0.75 = 4.5, floored to 4), `Slack Water — Deal 3 damage`, `Feint — Deal 4 damage`. Weak costs a Strike **2 of 6** because of the floor, not 1.5.

Also: the Spinner was wearing `Hydro Aura 1` with no Hydro card ever played on it. The only Hydro source that had touched it was the Kurage carrying out Kurage's Oath — a card whose face carries neither the `[Hydro]` tag nor the *Applies Hydro* clause. Second time the Kurage applied an element the card never mentioned.

**Turn 2 — the second real decision.** Enemy 18 HP, intent **11**. Under Weak my whole hand added to 13 damage; with the Energy Potion (+2 energy) I computed a kill on the spot for 0 further HP. The alternative was to bank Exposed Flank *and* Feint on the Kurage and block: 2 Vulnerable + Casket 3 + Feint 10×1.5 = 15, total **18**, exactly lethal at the top of turn 3, with a Defend for 5 against the 11 in between.

I took the banked line: 6 HP to keep the potion, and the kill needs no draw at all. Predicted HP 30, enemy dead before it acts again.
**Happened:** the next screen was the reward screen — the two Plans killed it at the top of turn 3 as computed.

Reward: `14 Gold`, `Powdered Demise` (potion), `Add a card to your deck.` Offered:

- **Treatise** — 1e power, Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card.
- **Read the Field** — 1e skill, Gain 5 Block. Plan: Gain 10 Block.
- **Undertow** [Hydro] — 1e attack, Deal 7 damage. If the enemy has a debuff, deal 10 instead.
- **Shikanoin Heizou — Heartstopper Strike** — 1e attack, Deal 6 damage. Deals 4 additional damage for each Swirl this turn.

Took **Undertow**. My damage was the bottleneck — four 6-damage Strikes against 26–37 HP enemies — and Undertow beats a Strike unconditionally (7 > 6) and reads 10 next to the Casket, which is already the reason to apply debuffs. Heizou's card is dead in this deck: I own no Swirl, so it is a strictly worse Strike. Undertow is also the **first card of the run with no Plan line at all**.

**Deck after fight 3 (13):** Strike ×4, Defend ×4, Kurage's Oath, Slack Water, Exposed Flank, Feint, Undertow.

## Fight 4 — Haunted Ship (63 HP)

Opening: **HP 30/80** — again exactly the number I had computed off screens that never printed it. Fishing Rod's counter, which had read `(1)` then `(2)`, was **gone from the relic line** with no message anywhere saying it had fired. Two potions now: `Energy Potion`, `Powdered Demise — Enemy loses 9 HP at the end of each of its turns.`

Enemy: `Haunted Ship` 63/63 with a compound intent:

> Intent: Strategic (Debuff) — This enemy intends to apply a Debuff to you.
>   and also: Strategic (StatusCard) — the number on its icon is 5 — This enemy intends to give you 5 Status cards.

**Turn 1.** The intent carries no damage number at all, so Block was worth nothing this turn; every energy went forward. Popped **Powdered Demise** immediately — it is per-turn, so its value is strictly maximised by using it on turn 1 against a 63 HP body — then Exposed Flank onto the Kurage and two Strikes for 12. Predicted enemy 63 → 51, → 42 after the Demise tick, → 39 after the Plan.

**Happened:** enemy **37/63**, i.e. 26 lost against 21 I could account for. The receipt printed only `Bake-Kurage: Exposed Flank, 2`. The missing 5 reconciles as **two Casket triggers the screen never mentions**: `Powdered Demise` applies `Demise 9 (debuff)`, and the Casket says *whenever you apply a debuff to an enemy* — so the potion itself fired it for 2 — and the Exposed Flank plan fired it again for 2×1.5 = 3 against the Vulnerable it had just applied. 2 + 9 + 3 + 12 = 26 ✓. Nothing on any screen says a potion counts as "you apply a debuff."

The debuff landed as `Weak 3` and the deck took 5 Status cards (piles went 3 + 10 + 5 = 18 against a 13-card deck).

**A card-face reading I got wrong and then corrected.** On the round-2 screen Kurage's Oath read `Plan: Deal 10 damage to ALL enemies` where it had always read 7, and on round 3 Feint read `Plan: Deal 15 damage` where it had read 10. My first reading was "the Fishing Rod upgraded these." It did not. Both are ×1.5 of the printed base, and the enemy was carrying `Vulnerable`: **the Plan line on a card face is previewed against the current enemy's Vulnerable**, exactly as the glossary promises (*"Enemy Vulnerable raises it; your Weak does not"*), while the card's immediate damage line is previewed against my **Weak** and not against Vulnerable. On round 3, plain `Strike — Deal 4` (6×0.75), `Strike+ — Deal 6` (9×0.75), `Feint — Deal 4` immediate but `Plan: Deal 15`. Two different multipliers on two lines of the same card, and the screen never says which line is adjusted for what.

The genuine Fishing Rod product was `**Strike+** (upgraded) — Deal 9 damage`, which shows up mid-fight with no announcement at any point.

**Turn 2 decision.** Enemy 37, intent **13**, me at 30. Demise removes 9 per enemy turn on its own, so the fight was already won on a clock; the question was purely how much of the 13 I ate. I banked Kurage's Oath on the Kurage, played Slack Water at the ship to put `Weak` on **it** (13 → 9) and Defended. Predicted take 4, HP 26.
**Happened:** HP **26/80**. Enemy 37 → 30 (Slack Water 4 + Casket 3) → 21 (Demise) → 11 (Oath plan for 10).

That 10 is worth pinning: the enemy had `Vulnerable 2` when I banked the Oath and the face read 10, but by the time the Plan resolved the stack had ticked to `Vulnerable 1` and the receipt still printed 10 and dealt 10. So `Vulnerable 2 … for 2 turns` covered **my turn 2 and the enemy's turn**, not two of my turns.

**Turn 3.** Enemy 11 with `Vulnerable 1`. Strike+ (9 face → 9 base ×0.75 Weak = 6 printed, ×1.5 Vulnerable when it lands) plus a Strike killed it. HP stayed **26**.

Reward `16 Gold` + card. Offered **Vanguard** (0e, Plan: 1 Vulnerable and 1 Weak, Exhaust), **Chain of Command** (1e, Plan: Deal 6 damage for each Companion card you played last turn), **The Moon, A Ship O'er the Seas** (2e, Mend 3 / Plan: Mend 6, Exhaust), **Heizou — Heartstopper Strike** again.

Took **Vanguard**: zero energy, two debuffs in one Plan, which with the Casket is two free damage triggers and turns both Undertows into 10s.

`Chain of Command` is the one card I could not price at all. It counts "**Companion card**s you played last turn" and **no glossary line on that screen, or any screen in the run, defines a Companion card.** I own the Bake-Kurage but I have never been dealt a card the screen called a Companion.

## The shop (floor 5)

`You have 160 gold.` I had banked 13 + 18 + 14 + 16 = **61** gold from four fights. The other **99 was never printed by any screen** — no starting-gold line at Neow, no running total anywhere before this. That is the single largest thing the run granted me without saying so.

Shelves: Deep Current 49 (6 damage to ALL), Undertow 49, Tide Wall 75, Stolen Chapter 25, Song of Pearls 75 (power: 3 Block per Plan, once per turn), Gorou — Crystal Collapse 74, Varka — Sturm und Drang 146, Razor Tooth 279, Horn Cleat 193, Chemical X 215, three potions at 72–75, Card Removal 75.

Bought a second **Undertow** (49) and a **Card Removal** (75), removing a plain Strike; 36 gold left, which buys nothing on the shelf except Stolen Chapter, and I would rather keep the deck at 15 than add a 1-energy Draw 2.

**Refusal #1 of the run, and it was a good one.** After naming the card, `choose 1` came back:

> your pick is already made and this screen is showing it back to you; naming another card here would change what gets taken without changing what you are being shown. Say `confirm` to take it, or `skip` to put it back and choose again.

The removal screen is the one screen with a two-step confirm, and it is the only screen in the run whose grammar is not printed in its own `What you can say` block until you trip it.

**Deck census printed by the removal screen (15, 14 after the removal):** Strike ×3, Strike+ ×1, Defend ×4, Kurage's Oath, Slack Water, Exposed Flank, Feint, Undertow ×2, Vanguard.

A trap worth recording: while my pick was pending, that screen listed **sixteen** card rows — `Strike (1)`, `Strike+`, `Strike (2)`, `Strike (3)`, four Defends, Oath, Slack Water, Exposed Flank, Feint, `Undertow (1)`, Vanguard, `Undertow (2)`, and then a bare unnumbered **`Strike`** at the end. I first read that as a fifth Strike-family card, i.e. as the Fishing Rod having *added* an upgraded Strike rather than upgrading one in place. It is not: the trailing unnumbered row is the **pending pick echoed back**, exactly as the refusal text says (*"this screen is showing it back to you"*). The give-away is that it carries no `(N)` while every genuine duplicate does. Pile arithmetic settles it — fight 4 ran on a 13-card deck and the boss fight on a 17-card deck, both of which require the upgrade to have been in place. **A screen that appends the selection to the same list it is selecting from, in the same format, is a real misread hazard.**

Status cards did not persist: the census has none of the 5 the Haunted Ship gave me.

## Event (floor 6) — Doors of Light and Dark

> - **Light Door** — Upgrade 2 random cards.
> - **Dark Door** — Remove 1 card from your Deck.

Took **Light Door**. Two upgrades beat one removal on a 15-card deck where every card has a meaningful upgrade, and the next room was a forced Elite at 26/80 HP.

**The screen never says what it upgraded.** After `choose "Light Door"` the whole page becomes `- **Proceed**`. I learned the answer two screens later, mid-fight, from card faces: `Slack Water+` (7 damage, `Plan: Apply 2 Weak to ALL enemies`) and `Feint+` (9 damage, `Plan: Deal 19 damage`). Both times I had to reverse-engineer an upgrade from a number on a card in my hand.

## Elite (floor 7) — Phantasmal Gardener ×4

Opening: **HP 26/80**, and this is the fight the run turned on. Four bodies, 29 + 30 + 28 + 31 = **118 HP**, intents `1x3`, `5`, `7`, `Empower` = 15 incoming, and every one of them carrying

> `Skittish 6 (buff) — The first time Phantasmal Gardener is hit each turn, it gains 6 Block.`

At 26 HP against 118 HP that reads unwinnable: 24 points of block per turn across four bodies, on a deck whose best card was a 10.

**Turn 1 — the whole fight.** Spent the Energy Potion for 5 energy and wrote **three** Plans onto the Kurage in a chosen order — Exposed Flank, then Kurage's Oath, then Slack Water+ — and spent the last two on both Defends for 10 Block against the printed 15.

My prediction was pessimistic. I expected the Casket ping from Exposed Flank to trip Skittish first, so each gardener would eat 3, then gain 6 Block, then take the Oath's 10 minus 6 = 4, then have the Slack Water ping fully blocked: **10 each, 40 total.**

**What happened was 16 each, 64 total.** Round-2 screen:

> - Bake-Kurage: Exposed Flank, 2
> - Bake-Kurage: Kurage's Oath, 10
> - Bake-Kurage: Slack Water+, 2

Gardeners 29→**13**, 30→**14**, 28→**12**, 31→**15**. 3 (Casket, Vulnerable-amplified) + 10 (Oath, 7×1.5) + 3 (Casket again) = 16, with **not one point absorbed and no Block on any of them**.

**This is the sharpest thing I found in the run: the Bake-Kurage's Plans do not trip Skittish.** Nothing on the Kurage's text, the Plan glossary, or Skittish's own line says the companion's hits are not "the first time it is hit each turn". Against a four-body Skittish elite that single unprinted fact is worth 24 damage a turn, and it is the difference between the line I played and the line I expected.

HP 26 → **21** (15 − 10 Block), exactly as predicted. `Weak 2` on all four also did visible work: Gardener (3)'s intent re-rendered as `the number on its icon is 0x3 — This enemy intends to Attack for 0 damage 3 times`. A 1-damage attack under Weak rounds to literally nothing.

**Turn 2.** Hand: Feint+ (9), Strike+ (9), Strike (6), Undertow ×2 (10 vs a debuffed target). Every gardener was Vulnerable, so those read 13 / 13 / 9 / **15**. Targets 13, 14, 12, 15. I predicted three kills if — and only if — the first hit of the turn lands in full *before* Skittish's Block goes up.

Undertow → Gardener (4) at 15: **dead**, so the hit resolves before the Block. Undertow → Gardener (2) at 14: dead. Feint+ (9×1.5 = 13.5, floored to 13) → Gardener (1) at exactly 13: dead. **Three kills in three cards**, and the survivor's intent was `0x3`, so I took **zero** damage that turn.

**Turn 3.** Last gardener 12 HP, `Vulnerable 1`, intent Empower. Here the Skittish tax finally bit properly: Strike for 9 left it at 3 and the Block went up, and my remaining damage in hand (an Exposed Flank Casket ping for 3) would have been eaten whole. So I played the fight's lesson back at it — banked **Vanguard** (0 energy) on the Kurage and ended the turn. Its Plan applies 1 Vulnerable and 1 Weak, i.e. **two** Casket triggers, which ignore Skittish. The next screen was the reward screen.

**Elite cleared at HP 21/80, having taken 5 damage in the entire fight**, from a position I had written off.

Reward: `45 Gold`, `Paper Krane`, card. **The relic's text is not printed on the reward screen** — `Took: Paper Krane.` and nothing else; I would not learn what it does until the next battle's relic list.

Card offered: a second **Exposed Flank**, **Cleansing Wave** (5 Block, remove one of your debuffs; Plan: 10 Block), **Battle Plan** (Plan: Gain 1 Energy and draw 2 cards), Heizou again. Took the second **Exposed Flank** — it is the card that made this fight work, it is 2 Vulnerable to ALL for 1 energy, and every Casket ping it fires bypasses whatever the enemy's on-hit defence is.

## Rest site (floor 8)

`HP 21/80`. Two options, `Rest — Heal for 30% of your Max HP (24)` and `Smith — Upgrade a card in your Deck`. Rested: **21 → 45/80**. The screen prints the actual number (24) rather than only the percentage, which is the one place in the run where a percentage effect showed its arithmetic up front.

## Treasure (floor 9)

`Sparkling Rouge — At the start of your 3rd turn, gain 1 Strength and 1 Dexterity.` Taken.

## Elite 2 (floor 10) — Terror Eel (140 HP)

Opening **HP 45/80**, and the relic list finally explained the elite reward I had taken blind two rooms earlier:

> - **Paper Krane** — Enemies with Weak deal 40% less damage to you rather than 25%.
> - **Sparkling Rouge** — At the start of your 3rd turn, gain 1 Strength and 1 Dexterity.

One body, **140 HP**, `Intent: Aggressive — the number on its icon is 16`, and

> `Shriek 70 (debuff) — The first time Terror Eel's HP reaches 70 or below, it becomes Stunned.`

That last line is the fight's whole shape, printed in advance: there is a free turn buried at exactly half its health, and it is worth timing a burst to cross 70 in one turn rather than two.

**Turn 1.** Exposed Flank and Feint+ both banked on the Kurage (in that order, so the Vulnerable lands first), one Defend. Predicted: take 16 − 5 = 11 → HP 34; at the top of turn 2, Casket 3 + Feint+ 13×1.5 = 19, so 140 → 118.
**Happened:** receipt `Exposed Flank, 2` / `Feint+, 19`; eel **118/140**; **HP 34/80**. Exact on both.

**Turn 2.** Banked Vanguard (0 energy) and the second Exposed Flank, then Slack Water+ into the eel (7×1.5 = 10, plus Weak, plus Casket 3) and a Strike (9). Predicted 22 damage now and about 9 more from three Casket pings at the top of turn 3.
**Happened:** eel 118 → 96 on my cards, then → **87** at the top of turn 3 from `Vanguard, 1` + `Exposed Flank, 2`, i.e. three pings of 3. HP 34 → **31**: the eel's `3x3` under Weak and the Paper Krane came through as 3 total.

Paper Krane's 40% is visible in the intent line, not just in the HP: on turn 3 the eel showed `Vigor 6 (buff) — Terror Eel's next Attack deals 6 additional damage` and an intent of **13**, which is (16 + 6) × 0.6 = 13.2. The intent number is printed already reduced by my Weak, which made the block decision arithmetic instead of guesswork.

Sparkling Rouge fired exactly on schedule: `Strength 1`, `Dexterity 1` at the top of turn 3, and every card face moved with it — `Strike — Deal 7`, `Strike+ — Deal 10`, `Defend — Gain 6 Block`.

**Turn 3 — the timed burst.** Eel 87, needed 17 to trip Shriek. Undertow (10 base for a debuffed target + 1 Strength = 11, ×1.5 = 16), Strike+ (10×1.5 = 15), Strike (7×1.5 = 10) = **41**. Predicted eel at 46 and Stunned.
**Happened:** `Terror Eel — HP 46/140`, `Intent: Stunned (Stun)`. Exact. I took **zero** damage that turn and the next.

**Turn 4.** Eel's intent was `Strategic (Debuff)` — no damage — so nothing went into Block. Feint+ (15) + Undertow (16) + Strike (10) = 41 → eel **5/140**.

**Turn 5 — the one screen that nearly ended the run.** Eel at 5 HP printed `Intent: Aggressive — the number on its icon is 33`. I was at **31 HP**. A 5 HP enemy was one turn from killing me outright, and the only reason I could see it was that the intent prints the number. Undertow (16) killed it first.

**Elite 2 cleared at HP 31/80 — 14 damage taken against a 140 HP elite.**

Reward: `45 Gold`, `Attack Potion`, `Strike Dummy`, card. Offered **Ambush** (1e, Play on the Bake-Kurage. Plan: Deal 12 damage), Salt Line (8 Block, Exhaust), a plain Feint, Noelle — Breastplate. Took **Ambush**: 12 as a Plan is 18 against a Vulnerable target, and by now I had proof that Plan damage skips on-hit defences.

## Rest site (floor 11)

Rested again: **31 → 55/80**.

## Elite 3 (floor 12) — Skulking Colony (75 HP)

Opening **HP 55/80**. New relic text finally legible: `**Strike Dummy** — Cards containing "Strike" deal 3 additional damage.` Potion: `Attack Potion — Choose 1 of 3 random Attack cards to add into your Hand. It's free to play this turn.`

> `Skulking Colony — HP 75/75` … `Hardened Shell 20 (buff) — Skulking Colony cannot lose more than 20 HP each turn.`

A hard damage cap changes the whole optimisation: overkill is burned, so the right play is to reach exactly 20 with the cheapest cards and put every other energy into Block and debuffs. I priced the fight at 4 capped turns minimum (75/20) before playing a card.

**The one mechanical mistake I made all run.** I banked `Ambush` and then `Exposed Flank`, in that order, and the receipt read

> - Bake-Kurage: Ambush, 12
> - Bake-Kurage: Exposed Flank, 2

Ambush resolved **before** the Vulnerable it should have been riding: 12 instead of 18. In the Terror Eel fight I had ordered Exposed Flank first on purpose and got the 19. The order of Plans on the Kurage is a real, load-bearing decision and I got it wrong by writing the cards in the wrong sequence, which is the kind of error the screen gives you no warning about — the Plan list is printed in order but nothing flags that a debuff Plan should precede a damage Plan.

**`Hardened Shell` is a live budget, not a static number, and that is excellent.** After the 15 landed it re-printed as `Hardened Shell 5` — the remaining HP the enemy can still lose this turn. Next turn it read `11`, then `10`, then `20` again on a fresh turn. Every turn I could read straight off the screen exactly how much more damage was worth spending, and I sized each turn to it: turn 2 spent one card into the last 5 and put the other two energy into a Weak and a Defend; turn 3 spent one Strike+ into the last 11 and banked Kurage's Oath; turn 4 spent one Strike into the last 10 and double-Defended.

Numbers, in order: 75 → 60 (Ambush 12 + Casket 3, shell 20→5) → 55 (Slack Water+ capped to 5) → 46 (three Casket pings from Vanguard + Exposed Flank, shell 20→11) → 35 (Strike+ 19 capped to 11) → 25 (Kurage's Oath 10, shell 20→10) → 15 (Strike 15 capped to 10) → dead to Strike+ for 19 against 15.

HP: 55 → 46 → 43 → 38 → 32. **23 damage taken.** Weak was doing most of that work: a printed `14` intent arrived as 8 through the Paper Krane, then as 3 once a Defend was under it.

Sparkling Rouge fired on turn 3 again and the card faces moved with the relics in a way I could check: with Strength 1 and Strike Dummy, `Strike — Deal 10` (6 + 1 + 3) and `Strike+ — Deal 13` (9 + 1 + 3).

Reward `35 Gold`, `Petrified Toad`, card. Offered Deep Current, a second **Ambush**, a third Exposed Flank, and `Kujou Sara — Crowfeather Cover` (0e, next Attack +4 and applies Electro). Took **Ambush** — 12 as a Plan, 18 under Vulnerable, for one energy.

## Shop 2 (floor 13)

`You have 208 gold.` Bought **Sango Isshin** (71) —

> cost 2, attack — Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead.

— which in this deck reads *20 damage to ALL enemies for 2 energy, 30 under Vulnerable*, because the Kurage carries out a Plan on nearly every turn I play. And a **Card Removal** (100), taking out a plain Strike. 37 gold left.

`Chain of Command` was on this shelf too, at 76 gold, still counting "Companion cards" that no screen in the run has ever defined.

## Treasure (floor 14)

`Centennial Puzzle — The first time you lose HP each combat, draw 3 cards.` Taken.

## Rest site (floor 15) and the boss (floors 16–17) — Waterfall Giant, 240 HP

Rested 32 → **56/80**, then the only node was `Boss (path 1)`.

Opening screen: **HP 56/80**, seven relics, two potions (`Attack Potion`, and `Potion-Shaped Rock — Deal 15 damage`, which Petrified Toad hands over at the start of every combat). Draw pile 12 + hand 5 = a 17-card deck.

> `Waterfall Giant — HP 240/240` · `Intent: Empower (Buff)`

**Turn 1.** A buff intent means zero incoming, so Block was worth nothing and every energy went into the Kurage: Exposed Flank first, then Ambush, then Ambush. Predicted Casket 3 + 12×1.5 + 12×1.5 = 39.
**Happened:** receipt `Exposed Flank, 2` / `Ambush, 18` / `Ambush, 18`; boss **201/240**. Exact.

Turn 2's screen printed the thing that eventually killed me:

> `Steam Eruption 15 (buff) — When killed, deals 15 damage at the end of your next turn.`

and it grew by **3 every round**: 15 → 18 → 21 → 24 → 27. It is a lethality clock that runs against you for the whole fight and is paid at the *end of the turn after* the kill, when whatever Block you spent on the killing turn has already expired.

**Turn 2.** Slack Water+ into the boss (10×1.5 = 15, plus Weak, plus Casket 3), Undertow (15), Vanguard banked, one Defend. Boss 201 → 168; the printed 15 intent arrived as 9 through the Paper Krane's Weak and 4 through the Defend. HP 56 → **52**. Centennial Puzzle fired on that first HP loss and drew three extra cards, which is why turn 3 had an eight-card hand.

**Turn 3.** Boss 162 after Vanguard's two Casket pings. Spent the Potion-Shaped Rock and Sango Isshin — its condition, *if the Bake-Kurage carried out a Plan this turn*, was satisfied by Vanguard's plan — and banked Exposed Flank. **Predicted 52 damage (Rock 15×1.5 = 22, Sango 20×1.5 = 30). Got 38.** Boss 162 → **124**.

That gap is the one piece of arithmetic I could not close from screens, and the reason is structural: **only the Kurage's Plans print a receipt.** Direct card damage and potion damage are never itemised anywhere. `Bake-Kurage: Ambush, 18` tells me what a Plan did; nothing tells me what Sango Isshin or a potion did, so when a two-term total misses by 14 I cannot say which term was wrong — whether the Rock ignores Vulnerable, whether Sango's "quarter of your Max HP" is taken before or after my Weak, or both.

**Turn 4.** Boss 121, `Intent: Heal` and Empower. Nothing incoming, so all three energy into damage: Strike+ 19, Slack Water+ 16 plus Casket 3, Undertow 16 = 54. Boss 121 → 67 → **77**, i.e. it healed exactly **10**.

**Turn 5 — the losing decision, and I can name it precisely.** Boss 77, intent **20**, Steam Eruption at 24. Hand: Ambush ×2, Strike+, Defend ×2, plus the Attack Potion. I chose maximum speed: potion (took Undertow off it, 16), both Ambushes banked, Strike+ (19). Boss 77 → **42**. No Block, so HP 46 → **26**.

I priced this at the time and got it wrong in one specific way. I reasoned "kill on turn 6, then use turn 7 to Block the Eruption." What I did not price is that **the Eruption lands at the end of the turn after the kill, so the Block has to be in the hand you draw after the boss is already dead.** The correct line was to give up one Ambush for a Defend on turn 5, finish at HP 32 instead of 26, and still kill on turn 6. Six HP, one card, the whole run.

**Turn 6.** `Ambush, 18` + `Ambush, 18` at the top of the turn took the boss 42 → **6**. I played both Defends *first* (12 Block, in case the Eruption resolved at the end of this turn) and only then Feint+ for the kill — deliberately in that order, because I could not tell from the printed text whether killing would end the combat outright and strand the Block.

It did not end the combat. The boss re-rendered as:

> `Waterfall Giant — HP 999999999/999999999` · `Intent: Stunned (Stun)` · `Steam Eruption 27`

**Turn 7.** HP **26**, Block 0 (turn-6 Block had expired), and:

> `Intent: Death Blow (DeathBlow) — the number on its icon is 27 — This creature is trying to take you down with it. It will attack you for 27 damage before being destroyed.`

Hand: Undertow ×2, Strike, Sango Isshin, Exposed Flank. **No Block card, no Weak card, no potion, one card left in the draw pile and nothing in the deck that draws.** Every out was checked against printed text and every one was closed:

- Block: none in hand; the only Block in my 17-card deck is four Defends, all elsewhere.
- Weak: Paper Krane would have made 27 into 16 and I would have lived at 10. My only Weak sources are Slack Water+ (in the discard) and Vanguard (`Exhaust`, gone since turn 2).
- Kill it: I spent an Undertow to test whether the sentinel HP was a display artifact. It is not — `999999999` → **`999999991`**, a real 8 damage into a real billion-HP pool. Undertow read 8 rather than 11 because the corpse carries no debuff any more, so its "deal 10 instead" clause was off.
- Outlast it: `end turn` is the only other verb.

Ended the turn into the Death Blow: `TOOL-BLOCKED: game_over`, `The run ended on floor 17.`

**The boss itself was beaten — 240 HP to 0 in six rounds for 30 HP of damage taken. The corpse won.**

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

Four, and they were the four best moments of the run.

1. **Which Plans to write on the Kurage, and in what order.** Elite 1 turn 1 is the case: with the Energy Potion I could write three Plans, and I chose Exposed Flank → Kurage's Oath → Slack Water+ specifically so the Vulnerable would land before the damage. The receipt paid it off — `Exposed Flank, 2` / `Kurage's Oath, 10` — the Oath's 7 became 10 because it resolved second. The trade is a whole turn of tempo: a banked Plan does nothing on the turn you pay for it, so every Plan is "give up this turn's damage or Block to buy a bigger next turn", and against `Skulking Colony` with its `Intent: Aggressive — the number on its icon is 14` that is a real bet.
   I also got it **wrong** once, which is what makes it a real choice: against the Colony I wrote `Ambush` before `Exposed Flank` and the receipt read `Ambush, 12` where it should have read 18.

2. **Which enemy to kill, priced against its own printed defence.** Fight 1: `Toadpole (1)` had `Thorns 2 — When hit by an attack, deal 2 damage back` and 17 HP, `Toadpole (2)` had 10 and no Thorns. Both lines cost 10 HP to the end of the fight on paper; I took the Thorns one because its turn 3 then needed two attacks rather than three. Elite 1 turn 2 is the sharper version: 13/14/12/15 HP against Undertow 15, Strike+ 13, Feint+ 13, with `Skittish 6` meaning a *second* card into the same body is worth six less. Three cards, three bodies, three kills, and the survivor's intent was `0x3`.

3. **Spend the potion or eat the damage.** Fight 3 turn 2: the Energy Potion bought a guaranteed kill for 0 further HP; banking Exposed Flank and Feint+ behind a Defend bought the same kill one turn later for 6 HP and kept the potion. I took the 6 HP, and that potion was what made Elite 1 survivable four rooms later. The trade only exists because the screen prints the intent number (`the number on its icon is 11`), so the cost of waiting is a known integer rather than a guess.

4. **How much damage is worth spending, against a cap.** `Hardened Shell 20 — cannot lose more than 20 HP each turn` re-prints every turn as the *remaining* budget (`20` → `5` → `11` → `10`), so each turn was an explicit "buy exactly this much damage, put the rest into Block or Weak" decision. That is the cleanest decision surface in the run, and it exists purely because the number is live.

### (b) What felt automatic, and what never seemed worth playing

**Automatic:** `Defend` when the printed intent exceeded my Block, and nothing when it did not. Because intents print an exact number with my Weak already folded in, Block decisions were arithmetic rather than judgement — on Elite 3 turn 2 the screen said 14, Paper Krane made it 8, one Defend made it 3, and there was nothing to think about. Likewise, on any turn whose intent was `Empower`, `Heal`, or `Strategic (Debuff)` with no damage number, a Defend was strictly wrong and anything else strictly right; those turns played themselves.

Also automatic: **playing Exposed Flank onto the Kurage rather than at an enemy.** `Apply 1 Vulnerable` versus `Plan: Apply 2 Vulnerable to ALL enemies` for the same 1 energy is not a decision, it is a dominated option with a one-turn delay attached. I played it as a Plan every single time.

**Never worth playing:** the character-guest cards.
- `Shikanoin Heizou — Heartstopper Strike — Deal 6 damage. Deals 4 additional damage for each Swirl this turn.` Offered **three separate times** (fight 2, fight 3, Elite 1). I own no Swirl, so its text resolves to a strictly worse Strike at the same cost.
- `Varka — Sturm und Drang` (146 gold, "Whenever a Swirl happens…") — same dead condition, at the highest price on the shelf.
- `Chain of Command` (reward, and 76 gold) — see (c).

`Kurage's Oath`, my starting Plan card, quietly stopped being worth an energy: 7 base against a 240 HP boss, against `Ambush`'s 12 for the same cost and the same delay.

### (c) What I could not understand, or that contradicted its own printed text

1. **The Plan glossary contradicts the Plan cards, on every screen, all run.**
   > **Plan** — On the Bake-Kurage, paid now; the Plan lands first thing next turn on the **front enemy**.

   The first Plan I ever resolved hit **both** Toadpoles for 7 (24→17 and 17→10), matching its own card text `Deal 7 damage to ALL enemies`. Elite 1 confirmed it at scale: one Oath Plan hit all four Gardeners for 10 apiece. The card text is right; the always-on glossary is wrong.

2. **"Companion card" is never defined.** `Chain of Command` prices itself entirely on *"each Companion card you played last turn"* and `The General's Banner` (73 gold) on *"when you play a Companion card"*. No glossary entry for Companion appears on any card-reward, shop or battle screen in 17 floors. I own a companion — the Bake-Kurage has its own section on every battle screen — but was never dealt a card the game called a Companion card, so I could not tell whether Chain of Command reads 0, 6 or 18. I declined it twice as unpriceable rather than as bad.

3. **Two lines of one card use two different previews, and the screen never says so.** Under Weak 3, against a Vulnerable enemy, `Feint+` printed `Deal 4 damage. Plan: Deal 15 damage.` The 4 is 6 × 0.75 (my Weak, not the enemy's Vulnerable); the 15 is 10 × 1.5 (the enemy's Vulnerable, not my Weak). It is consistent with the glossary's `Enemy Vulnerable raises it; your Weak does not` — but that sentence is written about Plans, and nothing says the immediate line is adjusted by the opposite rule. I first misread this as the Fishing Rod having upgraded two cards, and only unwound it by watching the number move as the Vulnerable stack ticked down.

4. **Whether the Bake-Kurage's Hydro belongs to the card or to the Kurage.** `Kurage's Oath` and `Exposed Flank` carry no `[Hydro]` tag and no `Applies Hydro` clause, yet every time either resolved as a Plan the target came out wearing `Hydro Aura`. The companion evidently carries an element the cards it executes do not print.

5. **`Undertow`'s face does not preview its own conditional consistently.** Under Weak on the Haunted Ship it printed `Deal 7 damage`, which is 10 × 0.75 — the conditional 10 *was* previewed. Against the boss's corpse it printed `Deal 7 damage`, which is the unconditional base. The same number means two different things on two screens.

6. **A corpse reports `HP 999999999/999999999`** and takes real damage (8 into it read back as 999999991). The footnote *"A power's number is what the game's data feed reports for it"* is at least honest that this is a raw feed value, but nothing says the thing is unkillable; the only way to learn it was to spend a card testing.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted:** plain `Defend`. Not because Block was bad — it is why I survived Elite 1 — but because it is the only card in the deck with **no Plan line**, so it cannot be fed to the Kurage, and it sat in hand every turn next to a card that could be. In this deck's own idiom, Defend is inert. (`Undertow` also has no Plan line, but it is 10 damage for 1 energy.)

**Happiest to draw:** `Ambush`. `Play on the Bake-Kurage. Plan: Deal 12 damage.` One energy, 18 against a Vulnerable target, and — the part that made me buy the second one on sight — Plan damage went straight through `Skittish 6` and would go through anything else that reacts to being hit. Two of them ended the boss: `Ambush, 18` / `Ambush, 18` took the Waterfall Giant from 42 to 6 before I played a card.

Runner-up, for pure relief: `Undertow`, the only card that reliably read 15–16 for one energy, and the card that killed the Terror Eel on the turn it printed a 33.

### (e) Did the first turn of the first fight already present a decision

**Yes, and a genuine one.** Round 1 of fight 1: 3 energy, a hand of Defend ×3 + `Kurage's Oath` + `Strike`, against `Toadpole (1)` intending `Empower` and `Toadpole (2)` intending 7. The choice is whether to spend an energy on a card that does **nothing this turn** — `Play on the Bake-Kurage. Plan: Deal 7 damage to ALL enemies` — while a printed 7-damage intent is pointed at you and you hold exactly enough Block to erase it.

I banked the Oath, Struck once and Defended once, taking 2 instead of 0 and buying 14 damage across two bodies for the next turn. Three of the four available lines were defensible, and the fight's whole shape — Thorns appearing on turn 2, the Plan landing on both bodies — followed from it. That is a real first turn, not a tutorial turn.

Worth adding that the *actual* first decision of the run, at Neow, was not. `Precarious Shears — Remove 2 cards from your Deck. Lose 16 HP.` is priced in a currency the screen refuses to show: Neow prints no HP, no max HP, no deck, no gold. 16 out of what? I declined it for that reason alone.

### (f) Anything a screen granted or changed without saying so

Seven, in rough order of how much they mattered:

1. **~99 starting gold.** Never printed. The first gold figure in the run is `You have 160 gold` on the floor-5 shop screen, against 61 banked from four reward screens.
2. **Plans ignore `Skittish`.** Sixty-four damage landed across four Gardeners with not one point of Block interposed. No text anywhere says the companion's hits are exempt from on-hit triggers, and it decided the fight.
3. **A potion counts as "you apply a debuff" for the Tamakushi Casket.** `Powdered Demise` applying `Demise 9 (debuff)` fired the relic for 2, which is the only way the Haunted Ship's 63 → 37 reconciles. Nothing on either the relic or the potion suggests it.
4. **The Fishing Rod's upgrade is announced nowhere.** The relic's counter simply stops printing `(2)` and later prints `(1)` again; the product turned up mid-fight as `Strike+ (upgraded)` in a hand.
5. **The Light Door's upgrades are announced nowhere.** `Upgrade 2 random cards`, then the entire screen becomes `- **Proceed**`. I identified `Slack Water+` and `Feint+` from card faces one and two fights later.
6. **A relic's text is not printed when you take it.** `Took: Paper Krane.` and nothing else; likewise Strike Dummy, Petrified Toad and Centennial Puzzle. You learn what your new relic does at the top of the next combat.
7. **A 2-stack Vulnerable fires the Casket twice, at two different amounts.** The Haunted Ship's Exposed Flank plan step dealt 5 where the receipt printed `2`, consistent with one ping at 2 and one at 3 as the stack landed. The receipt prints the card's base number, never the number dealt.

Two smaller ones: **`Vulnerable 2` covers my turn and the enemy's turn, not two of my turns** (an Oath banked while the boss showed `Vulnerable 2` resolved for 10, not 15, once the stack had ticked to 1), and **the Kurage applies Hydro on behalf of cards that never mention Hydro**.

---

## Findings, ranked by sharpness

**1. The Bake-Kurage's Plans bypass on-hit defensive triggers, and nothing says so. This is the single largest unprinted fact in the run.**
Elite 1, four `Phantasmal Gardener`s each carrying `Skittish 6 (buff) — The first time Phantasmal Gardener is hit each turn, it gains 6 Block`. Three Plans resolved at the top of round 2, receipt `Exposed Flank, 2` / `Kurage's Oath, 10` / `Slack Water+, 2`. Every gardener went down by exactly **16** (29→13, 30→14, 28→12, 31→15) = 3 + 10 + 3, with **zero** absorbed and no Block on any body afterwards. My pre-play model, which assumed the first Casket ping would trip Skittish, predicted 10 each. The 6-per-body-per-turn tax that made the elite look unwinnable at 26 HP simply does not apply to the companion. My own cards *did* pay it one turn later: a Strike for 9 into a 12 HP gardener left it at 3 and put 6 Block up, and the fight had to be closed by banking `Vanguard` on the Kurage instead.

**2. `Steam Eruption` is a lethality clock that cannot be blocked with the Block you used to kill the boss, and that is what ended the run.**
`When killed, deals 27 damage at the end of your next turn.` It grew +3 per round for the whole fight (15/18/21/24/27), so a longer fight is a bigger posthumous hit. I killed the boss on round 6 at 26 HP with 12 Block up; Block is `Until next turn`, so it expired before the bill came due. Round 7's drawn hand — Undertow ×2, Strike, Sango Isshin, Exposed Flank — held no Block and no Weak, and the corpse (`HP 999999999`, `Intent: Death Blow … 27`) killed me by **one point**. The requirement the fight actually imposes is *be above the Eruption number at the moment of the kill, or hold a Block card through the kill*, and neither the buff text nor the Block glossary lets you read that off the screen. I derived it one turn too late.

**3. Only Plans print a damage receipt; direct card damage and potion damage are never itemised, so a wrong model is undiagnosable.**
The Kurage prints `Bake-Kurage: Ambush, 18`. Nothing prints for a card I play or a potion I drink. On boss turn 3 I predicted 52 from `Potion-Shaped Rock` (15) and `Sango Isshin` (a quarter of 80 Max HP = 20) against a Vulnerable target; the boss went 162 → **124**, i.e. 38. Fourteen points unaccounted across exactly two unlabelled terms, and no screen can split them. Compare the Plan side, where every prediction I made across seven fights came out exact because the receipt let me check each term.

**4. The always-printed Plan glossary states the wrong targeting, on every battle screen in the run.**
> `**Plan** — On the Bake-Kurage, paid now; the Plan lands first thing next turn on the front enemy.`

Fight 1: one Oath Plan took `Toadpole (1)` 24→17 **and** `Toadpole (2)` 17→10. Elite 1: one Oath Plan took all four Gardeners for 10 each. The card text (`Deal 7 damage to ALL enemies`) is correct; the glossary is not, and it is the one line reprinted on literally every combat screen.

**5. The order in which Plans are written onto the Kurage is load-bearing, and no screen flags it.**
Terror Eel, Exposed Flank written before Feint+: receipt `Exposed Flank, 2` / `Feint+, 19` — 13 × 1.5, the Vulnerable landed first. Skulking Colony, Ambush written before Exposed Flank: receipt `Ambush, 12` / `Exposed Flank, 2` — the same 12-damage Plan, six points worse, purely because I wrote the two cards in the other order. The Kurage's section does print the queue in order, which is exactly enough to verify the order after the fact and not enough to warn you before.

**6. Intent numbers arrive pre-adjusted for my debuffs, which is why every Block decision in the run was arithmetic rather than a guess.**
Terror Eel with `Vigor 6` (16 + 6 = 22) under my Weak with Paper Krane printed `the number on its icon is 13` = 22 × 0.6 = 13.2. A weakened Gardener's 1-damage triple printed `the number on its icon is 0x3` and dealt literally nothing. Every HP prediction made off these numbers came out exact: 64→62, →56, →52, →44, →36, →30, →26, →21, →34, →31. That is a genuinely good screen.

**7. `Hardened Shell` printing as a live remaining budget turns a damage cap into a readable decision each turn.**
`Hardened Shell 20 — cannot lose more than 20 HP each turn` re-rendered as `5`, then `11`, then `10`, then `20` as each turn's budget was consumed. I sized four consecutive turns straight off that number — one card into the last 5, one Strike+ into the last 11, one Strike into the last 10 — and put every other energy into Weak and Block, taking 23 damage across a 75 HP elite. Contrast `Skittish 6`, which never changes its printed number however much Block it has actually granted.

**8. The card-removal screen appends your pending pick to the same list, in the same format, and it reads as an extra copy.**
Sixteen rows where the deck held fifteen, the extra being a bare `Strike` after `Undertow (2)`, distinguishable only by the absence of a `(N)` index. I misread the deck size off it and corrected only by cross-checking two later fights' pile counts. That same screen is also the only one whose two-step `confirm` grammar is not printed until you trip its refusal — which, to be fair, is the best-written refusal in the run: it explains *why* naming a second card is refused, not merely that it is.

**9. Three of six card rewards, and two shop shelves, offered cards this character cannot use — and two more priced on undefined vocabulary.**
`Shikanoin Heizou — Heartstopper Strike` (Deal 6, +4 per Swirl) appeared at fight 2, fight 3 and Elite 1 while I owned no Swirl card, having declined the only one ever offered (`Sucrose — Astable Anemohypostasis`) at the very first reward, before any screen had explained what Swirl was for. `Varka — Sturm und Drang` sat at 146 gold on the same dead condition. `Chain of Command` and `The General's Banner` both price themselves on **Companion cards**, a term no screen in 17 floors defines.

**10. The run's economy and its upgrades are invisible at the moment they happen — with one counter-example that shows the fix.**
Starting gold (~99) is never printed; the Fishing Rod's upgrade, the Light Door's two upgrades, and every relic's text on pickup are all silent, discovered one or two rooms later from a card face or a relic list. Against that, the rest site prints `Heal for 30% of your Max HP (24)` — the percentage *and* the number it resolves to. That is exactly the treatment `Precarious Shears — Remove 2 cards from your Deck. Lose 16 HP.` needed and did not get, on a screen that shows no HP at all.

**Where I could not tell.** Whether Sango Isshin's "quarter of your Max HP" is reduced by my Weak, or raised by enemy Vulnerable, or neither — boss turn 3 is 14 short of my model with no receipt to split it. Whether the Casket's 2 Hydro damage counts as an "attack" for every purpose or only for Vulnerable scaling. Whether combat would have ended immediately on the boss's death had I not been holding Block (I played the Defends first precisely because I could not tell; the answer turned out to be that combat continues). And whether `Skittish` grants its Block before or after the triggering hit — the Undertow that killed a 15 HP Gardener at exactly 15 says "after", but a killing blow may not be a fair test.

---

## Non-blindness declaration

- **Commands run outside the two allowed ones: none.** Every game action in this run was `GITS_LANE=1 python -m understudy.blindplay observe` or `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, run from the repo root. No `harness`, `session`, `audit`, `notes`, `scenario`, `staged_turn`, `soak` or `embark`. No git. The game was never launched, closed, restarted or torn down by me, and lane 2 was never touched.
- **Tools used:** the Bash tool (to run the two blindplay commands, to pipe `observe` through `sed`/`grep`/`head` for trimming, and to append to this record with `cat >>`); the Write tool (to create this record); the Read and Edit tools (on this record only — to fill in the Identity block and to correct the deck-census paragraph once pile arithmetic disproved my first reading).
- **Repo files read: none.** No source, no YAML, no docs, no rulings, no backlog, no earlier records, no other seat's record. The only file I opened was this one, which I wrote.
- **Files written: one** — `review/qa/kokomi-round-5-2026-09-03/opus-act1.md`. No scratch file was created. No identifiers were minted.
- **Lane left standing:** yes, exactly where it stopped. The last action was `end turn` on round 7 of the boss fight, which returned `TOOL-BLOCKED: game_over` / `The run ended on floor 17.` No further `act` was issued and nothing was reset or cleaned up.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
