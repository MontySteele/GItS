# KLEEMOD-KOKOMI — blind seat, lane 1, run 2, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 5, run 2, first of three chained seats (act 1 only).
- **Lane:** 1.
- **Character:** KLEEMOD-KOKOMI.
- **Run seed:** never printed on any screen I saw.
- **Act:** 1. The map screen names the boss at the top of the act: **The Kin**.
- **Actions accepted / refused:** **208 accepted**, **2 refused**. The two refusals were the same command (`choose "Slack Water"` on the enchant screen), both refused with "your pick is already made". Two further `skip` commands on that screen returned `ok: true` but then printed `error No cancel/close button is currently enabled` and changed nothing — I count those among the 208 as accepted-but-inert, and they are the only commands in the run that did not do what the screen said they would.
- **Termination reason:** **Stop condition (2) — the run ended.** `end turn` on round 8 of the boss returned `TOOL-BLOCKED: game_over` / "the run is over; there is nothing left to play. The run ended on floor 17." I was killed by The Kin at `HP 2/80` with 12 incoming and a block ceiling of 10.
- **Where the run stands:** dead on floor 17, the act-1 boss. The lane is left exactly where it stopped, on the game-over state; I sent no further commands after the blocked `end turn`.
- **The boss in full:** the map named **The Kin**, which turned out to be three enemies — Kin Priest (190 HP) plus two Kin Followers (58 and 59).
- **Final gold:** 115. **Final potions:** none (both were spent in the floor-6 elite). **Final relics (5):** Tamakushi Casket, Golden Pearl, Akabeko, Juzu Bracelet, Frozen Egg.
- **Final deck (19):** Strike ×3, Defend ×4, Kurage's Oath+, Slack Water, Sea-Salt Prayer, Feint+ (Sharp 2), Feint ×2, Vanguard ×2, Undertow+, Undertow, Battle Plan, Read the Field.

### HP trajectory — every reading the screens printed, in order

`64/80` (fight 1 r1) → `61` (r2) → `61` (r3) → `61` (r4) → `61` (fight 2 r1) → `61` (r2) → `54` (r3) → `50` (r4) → `50` (fight 3 r1) → `50` (r2) → `45` (r3) → `45` (elite r1) → `45` (r2) → `29` (r3) → `29` (r4) → `29` (r5) → `29` (r6) → `29` (r7) → **rest** → `53` → **Tablet of Truth heal** → `73` → `73` (Byrdonis r1) → `56` (r2) → `52` (r3) → `52` (Mawler r1) → `46` (r2) → `46` (r3) → `40` (rest site) → **rest** → `64` → `64` (boss r1) → `53` (r2) → `34` (r3) → `27` (r4) → `26` (r5) → `20` (r6) → `16` (r7) → `2` (r8) → dead.

Max HP never moved from 80. Total healing received all act: 24 + 20 + 24 = 68.

### Starting position

First battle screen printed `HP 64/80`. The run therefore opened below full — 64 of 80 — and no screen ever explained why.

Relics as printed:

- **Tamakushi Casket** — "Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy."
- **Golden Pearl** — "Upon pickup, gain 150 Gold."

Starting deck, reconstructed from the faces printed in hand across rounds 1 and 2 of fight 1 (draw pile 5 + hand 5 = 10 cards, and rounds 1–2 together showed all ten):

- Strike ×4 — cost 1, attack, "Deal 6 damage."
- Defend ×4 — cost 1, skill, "Gain 5 Block."
- Kurage's Oath ×1 — cost 1, skill, "Play on the Bake-Kurage. Plan: Deal 7 damage to ALL enemies."
- Slack Water ×1 [Hydro] — cost 1, attack, "Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies."

---

## Neow (floor 0)

Three options printed:

- **Stone Humidifier** — "Whenever you Rest at a Rest Site, raise your Max HP by 5."
- **Golden Pearl** — "Upon pickup, gain 150 Gold."
- **Silver Crucible** — "The first 3 card rewards you see are Upgraded. The first Treasure Chest you open is empty."

**Predicted / reasoned:** Silver Crucible is the biggest raw power spike but pays for it with a whole relic (the act-1 chest), and the map showed **three Treasure rooms** on one floor, so the cost was real but capped at one. Stone Humidifier only pays out if I spend rest sites resting rather than upgrading. Golden Pearl is the only downside-free option and I control the spend.

**Took:** Golden Pearl. Screen confirmed "Took: Golden Pearl — Upon pickup, gain 150 Gold."

This is a real choice with a clean trade: guaranteed flexible resource now (150 gold) vs. conditional deck power (3 upgrades) bought with a relic.

## The map (act 1)

The map screen printed the whole act, 16 floors, every room per floor:

```
- 1 floor ahead: Monster, Monster
- 2 floors ahead: Monster, Unknown, Monster
...
- 9 floors ahead: Treasure, Treasure, Treasure
- 15 floors ahead: RestSite, RestSite, RestSite, RestSite
- 16 floors ahead: Boss
At the top of this act: **The Kin**
```

Choices offered were `Monster (path 1)` (leads on to: Monster) and `Monster (path 2)` (leads on to: Unknown, Monster). Took path 2 for the extra branch.

Note on what the map does and does not print: it lists the rooms on each floor but **not the edges between them**, so beyond the one-floor lookahead ("leads on to") I could not actually plan a route. Every later map screen only re-offered the immediate nodes.

---

## Fight 1 — Fuzzy Wurm Crawler (floor 1)

Opening screen: `Fuzzy Wurm Crawler — HP 57/57`, `Intent: Aggressive (Attack) — the number on its icon is 4`. My `HP 64/80`, `Energy 3/3`.

The Bake-Kurage was on the field from turn 1 by the Casket: "The Bake-Kurage is on the field for the whole fight. Enemies cannot touch it. Play a card on it to write its **Plan** line instead of playing the card now." / "Nothing is planned. The morning is empty."

### Round 1 — predicted 12 damage, got exactly 12

Hand: Kurage's Oath, Defend, Strike, Slack Water, Defend.

**Prediction:** enemy hits for only 4, so block is worthless; spend all 3 energy on damage. Slack Water = 4 damage + 1 Weak, and the Weak is a debuff so the Casket adds "2 Hydro damage to that enemy" = 6. Strike = 6. Total 12 this turn. Kurage's Oath onto the Bake-Kurage banks 7 for next turn. Weak should cut the 4-damage intent.

**Happened:** enemy `57/57` → `45/57`. Exactly 12. Intent re-printed as `the number on its icon is 3` — 4 × 0.75 = 3, matching `Weak 1 (debuff) — Attacks deal 25% less damage for 1 turn.` Enemy also gained `Hydro Aura 2 (aura)` from Slack Water's *Applies Hydro* rider. Bake-Kurage showed `Planned, and carried out at the start of your next turn in this order (1): 1. Kurage's Oath`.

### Round 2 — Plan paid exactly 7

Screen printed the Plan resolving: `Bake-Kurage: Kurage's Oath, 7`. Enemy `45` → `38`. My HP `64` → `61`, i.e. I took exactly the 3 the weakened intent advertised.

Enemy intent: `Empower (Buff)` — no attack incoming. Hand was Strike ×3, Defend ×2, so block was dead weight; played 3 Strikes for 18. Enemy `38` → `20`.

### Round 3 — the first turn that was actually a decision

Screen: `Fuzzy Wurm Crawler — HP 20/57`, `Strength 7 (buff) — Increases attack damage by 7`, `Intent: Aggressive (Attack) — the number on its icon is 11`. The Empower had turned a 4-damage enemy into an 11-damage one in one turn.

Hand: Defend, Strike, Kurage's Oath, Defend, Slack Water. 3 energy, 20 enemy HP, so **the kill was out of reach this turn** (max available was Strike 6 + Slack Water 6 = 12).

I worked the draw out exactly: deck is 10, discard was 0, draw pile 5, and hand held Strike ×1 / Defend ×2 / Oath / Slack Water — so the draw pile was *provably* Strike ×3 + Defend ×2, and next turn's hand would be exactly those five. Three Strikes = 18.

So the question was only "how much HP do I pay to reach a kill I get either way next turn":

- Strike + Slack Water + Oath → enemy at 8, take 8 (11 weakened to 8), kill next turn.
- Strike + Slack Water + Defend → enemy at 8, take 3, kill next turn.
- **Slack Water + Defend + Defend → enemy at 14, take 0, kill next turn (18 ≥ 14).**

Since 18 covered 14 comfortably, the all-block line dominated: same kill turn, zero HP.

**Predicted:** enemy 20 → 14 (4 + 2 Casket), intent 11 → 8, Block 10 absorbs all of it, take 0.

**Happened:** enemy `20` → `14`. HP stayed `61/80`. Exactly as predicted, 0 damage taken.

### Round 4 — kill

Hand was the predicted Strike ×3, Defend ×2. Three Strikes for 18 vs 14 HP. Enemy died.

**Fight 1 result:** won on round 4 at `HP 61/80`. Total damage taken across the whole fight: **3**.

### Reward

`16 Gold` and a card choice, all four cost 1 and all four skills:

- **Tide Wall** — "Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning."
- **Stolen Chapter** — "Draw 2 cards. Plan: Draw 4 cards."
- **Sea-Salt Prayer** — "Gain 4 Block. Apply 1 Weak."
- **Thoma — Blazing Barrier** — "Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block."

**Reasoning:** no attack was on offer at all. My deck already held 4 Defends, so a fifth pure block card was the weakest add. Draw was not my constraint — I was energy-capped every single turn of fight 1 (3 energy, 5 cards), so Stolen Chapter's 2 cards would have sat unplayable. Sea-Salt Prayer was the only card advancing two axes at once: 4 Block, plus a Weak that both cuts an incoming hit 25% and trips the Casket for 2 Hydro damage — roughly "7 block-equivalent + 2 damage for 1 energy."

**Took:** Sea-Salt Prayer. Deck now 11 cards.

---

## Fight 2 — three Slimes (floor 2)

Opening: `Leaf Slime (S) — HP 12/12` (Intent: `Strategic (StatusCard) ... intends to give you 1 Status card`), `Twig Slime (M) — HP 26/26` (same Status intent), `Twig Slime (S) — HP 10/10` (`Attack for 4`). My `HP 61/80`.

### Round 1 — killing a status-giver before it acts

**Prediction:** two of the three intend to hand me Status cards. If an enemy dies before its turn, its intent never resolves — so killing a status-giver is worth more than raw damage. Leaf Slime (S) is 12 HP and two Strikes are exactly 12: no overkill. The only attack is 4, and Sea-Salt Prayer's 4 Block covers it exactly while its Weak trips the Casket.

Played Sea-Salt Prayer on Twig Slime (S), then Strike ×2 on Leaf Slime (S).

**Happened:** Leaf Slime died; **no Status card came from it**. Twig Slime (S) went `10/10` → `8/10` (the Casket's 2) and took `Weak 1`, its intent re-printing as `the number on its icon is 3`. Block 4 held the 3-damage hit to zero: HP stayed `61/80`.

**Unannounced grant:** Sea-Salt Prayer's own text is "Gain 4 Block. Apply 1 Weak" — it carries no `[Hydro]` tag and says nothing about elements. But the target came out wearing `Hydro Aura 2 (aura)`. The Casket's retaliation ("deals 2 Hydro damage") is what applied it, and no screen says that the relic's ping also lays an aura. That is a real, useful effect the card face cannot tell you about.

### Round 2 — the Status card, and Weak on the big hitter

Pile arithmetic showed the Status card arriving without any screen naming it: `1 in the draw pile, 6 discarded` + 5 in hand = 12 cards against an 11-card deck. Twig Slime (M) had delivered one.

Board: `Twig Slime (M) — HP 26/26, Attack 11`, `Twig Slime (S) — HP 8/10, Attack 4`. 15 incoming, 3 energy.

I compared four lines explicitly and took: Slack Water on Twig Slime (M) (4 damage + 2 Casket = 6, and a Weak that drops 11 → 8), Kurage's Oath onto the Bake-Kurage, one Defend.

**Prediction:** M `26` → `20`; incoming 8 + 4 = 12 against 5 Block, so take 7; next turn the Plan takes 7 off *both*.

**Happened:** exactly. HP `61` → `54`. Round 3 opened with `Bake-Kurage: Kurage's Oath, 7`, `Twig Slime (M) — HP 13/26`, `Twig Slime (S) — HP 1/10`.

**Contradiction found.** The `Plan` glossary line, printed on every screen, says: "the Plan lands first thing next turn **on the front enemy**." Kurage's Oath's own text says "Deal 7 damage to **ALL enemies**." The card text is what happened — both slimes took exactly 7 (20→13 and 8→1). The glossary line is wrong for any Plan whose card says ALL, and it is the line the game repeats most often.

### Round 3 — the Status card revealed

The Status card was `Slimed — cost 1, status. Draw 1 card. Exhaust.` It costs energy to cycle itself, so in an energy-capped deck it is a tax, not a blank.

M at 13, S at 1, 15 incoming. Killing M needed all three energy (Slack Water 6 + Strike 6 + Strike 6 = 18 vs 13) and capped incoming at 4 instead of 11. **Predicted take 4; took exactly 4** (`54` → `50`). Round 4 killed S with one Strike.

**Fight 2 result:** won at `HP 50/80`, 11 damage taken.

### Reward

`11 Gold`, `Block Potion` (Gain 12 Block), and a card from: **Song of Pearls** (power, "Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block"), **Feint** [Hydro] ("Deal 6 damage. Plan: Deal 10 damage."), **Salt Line** ("Gain 8 Block. Exhaust."), **Thoma — Blazing Barrier**.

Took **Feint** — the first attack offered in two card screens, and the only card that beat a Strike: same 6 from hand, or 10 for the same 1 energy through the Plan lane. Deck 12.

The `Slimed` did not persist: next combat opened with `7 in the draw pile` + 5 in hand = 12, my deck size exactly. Status cards leave at end of combat, which no screen states.

---

## Fight 3 — Shrinker Beetle (floor 3, entered from an "Unknown" node)

The `Unknown (path 1)` node resolved **straight into a battle** with no event text at all — the screen went from map to `# Battle — round 1`. An Unknown can simply be a fight, and nothing warns you.

Opening: `Shrinker Beetle — HP 40/40`, `Intent: Strategic (DebuffStrong) — This enemy intends to apply a Debuff to you.` My `HP 50/80`.

### Round 1 — no incoming damage, so block is dead

**Prediction:** nothing is attacking, so all three energy go to damage, and Feint is worth more banked (Plan 10) than played (6). Feint → Bake-Kurage, Strike (6), Sea-Salt Prayer (0 useful Block, but 2 Casket damage). Expect 8 now, 10 at the top of next turn: 40 − 18 = 22.

**Happened:** `Shrinker Beetle — HP 22/40`. Exactly 18.

### The sharpest mechanical finding of the run

Round 2 opened with a new debuff on me:

> `Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks deal 30% less damage.`

Every card face **rewrote its own number** to the shrunk value: `Strike — Deal 4 damage` (from 6), `Slack Water — Deal 2 damage` (from 4), `Feint — Deal 4 damage. Plan: Deal 10 damage.`

Note what Feint's face did *not* change: the printed Plan stayed at **10** while its from-hand number fell 6 → 4. And the arithmetic confirms the Plan actually paid 10: the Shrink landed at the end of round 1, and round 2 opened with `Bake-Kurage: Feint, 10` and the beetle at 22 — that is 6 + 2 dealt pre-debuff, plus the full 10, with no 30% cut anywhere.

**So the Bake-Kurage's Plan damage ignores an attack-damage debuff that halves everything played from hand.** Under Shrink, Feint from hand is 4 and Feint as a Plan is 10 — a 2.5x swing on the same card for the same 1 energy. That inverted my whole play pattern for the fight, and it is the single most interesting thing the character did.

### Rounds 2–3

Round 2: Oath → Plan, Slack Water on the beetle (2 + 2 Casket = 4, Weak 7 → 5), Strike (4). Also learned that under Shrink, **Slack Water strictly dominates Strike**: both deal 4 (2 shrunk + 2 un-shrinkable Casket vs 4 shrunk), but Slack Water adds a Weak. The Casket's 2 is flat and is not reduced by Shrink, so the worse the debuff, the larger the relic's share.

**Predicted** beetle 22 → 14, take 5. **Happened:** exactly; HP `50` → `45`. Round 3 opened `Shrinker Beetle — HP 7/40` (14 − 7 Plan).

Its intent had escalated `7` → `13`, so the kill was urgent. Two Strikes (4 + 4 = 8 ≥ 7) finished it.

**Fight 3 result:** won at `HP 45/80`, 5 damage taken.

### Reward

`16 Gold`, `Liquid Bronze` (a potion), and a card from: **Rally** ("Apply 1 Weak. The next Companion card you play this turn costs 1 less."), **Feint**, **Stolen Chapter**, **Sayu — Muji-Muji Daruma** ("For 2 turns, at the end of your turn deal 6 damage to a random enemy if you are above 70% HP, otherwise gain 6 Block. Exhaust.").

Took a **second Feint**. Rally was near-blank — I have never been offered a card tagged Companion, so "the next Companion card you play this turn costs 1 less" is text I cannot use. Sayu's 70%-HP switch reads backwards for a deck that is losing HP: at 45/80 (56%) it would only ever have given Block, i.e. it turns off exactly when you would want the damage.

Deck 13.

---

## Event — Self-Help Book (floor 4, an "Unknown")

```
- **Read the Back**        Choose an Attack to Enchant with Sharp 2.
- **Read a Random Passage** Choose a Skill to Enchant with Nimble 2.
- **Locked** (not available) You don't have any Powers that can be Enchanted.
```

**Neither "Sharp" nor "Nimble" is defined on this screen**, and neither appears in the "Words on this screen" glossary that every other screen carries. I had to commit to one of them blind. I picked the Attack branch because damage was my measured weakness.

The card-picking screen also printed no definition. Only *after* provisionally picking a card did the preview reveal it:

> `*Sharp* — Increases damage on this card by 2.`

And the preview showed the thing that mattered:

> `**Feint (2)** [Hydro] (Sharp 2) — cost 1, attack` / `Deal 8 damage. Plan: Deal 10 damage.`

**Sharp 2 raises the from-hand number 6 → 8 and leaves the Plan number at 10.** So an enchant is worth nothing on the mode of the card I actually wanted to use. That is only discoverable by picking the card and reading the preview.

### A screen that contradicts itself, and a pick I could not take back

Having learned Sharp does not touch Plans, I wanted to move the enchant to Slack Water (always played from hand; 6 damage + the Casket's 2 = 8 *plus* a Weak, strictly better than an 8-damage Strike). The screen told me I could:

> `You may say `skip` to undo this pick and choose again; it does not leave the screen.`

`skip` returned:

> `error No cancel/close button is currently enabled - selection may be mandatory`

and `choose "Slack Water"` was refused with:

> `your pick is already made and this screen is showing it back to you; naming another card here would change what gets taken without changing what you are being shown. Say `confirm` to take it, or `skip` to put it back and choose again.`

Both forms the refusal offers point at each other: `choose` says use `skip`, `skip` says there is nothing to cancel. **The pick was unrevokable despite two separate lines of on-screen text promising it was revokable.** I confirmed because it was the only form that resolved. This cost me the better enchant target and is the sharpest usability defect I hit.

## Shop (floor 5)

`You have 292 gold.`

**Unannounced grant:** my tally of every gold line printed to that point was 150 (Neow) + 16 + 11 + 16 = 193. The shop said 292 — exactly 99 more. The run began with **99 starting gold that no screen ever printed**; the shop is the first place the number appears at all.

Shelves:

```
Feint            1  attack  51   Deal 6 damage. Plan: Deal 10 damage.
Undertow         1  attack  52   Deal 7 damage. If the enemy has a debuff, deal 10 instead.
Battle Plan      1  skill   74   Play on the Bake-Kurage. Plan: Gain 1 Energy and draw 2 cards.
Vanguard         0  skill   26   Play on the Bake-Kurage. Plan: Apply 1 Vulnerable and 1 Weak. Exhaust.
Treatise         1  power   72   Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card.
Kujou Sara       1  attack  71   Deal 5 damage. Next turn, your Attacks deal 5 additional damage.
Gorou            1  skill   76   Plan: play a copy of the last other Companion card you played this turn.
Tuning Fork      relic     229   Every time you play 10 Skills, gain 7 Block.
War Paint        relic     155   Upon pickup, Upgrade 2 random Skills.
Ghost Seed       relic     222   Strikes and Defends gain Ethereal.
Fysh Oil         potion     74   Gain 1 Strength and 1 Dexterity.
Flex Potion      potion     49   Gain 5 Strength. At the end of your turn, lose 5 Strength.
Energy Potion    potion     51   Gain [Energy][Energy].
Card Removal                75
```

**Bought:** Vanguard (26), Undertow (52), Feint (51), Battle Plan (74), Card Removal (75) = 278, leaving 14.

**Reasoning, from what play had shown me:**

- **Vanguard at 26 was the standout price.** It is the only **0-cost** card offered, its Plan applies *two* debuffs (Vulnerable + Weak) which the Casket converts into 2 × 2 = 4 free Hydro damage, and the Plan glossary states "Enemy **Vulnerable raises it**" — so it is the one card that scales the Plan lane I had already proved was my best damage rate.
- **Undertow** is the only *immediate* 10-damage 1-cost in the shop, and its condition ("if the enemy has a debuff") is one the Casket/Slack Water/Sea-Salt Prayer/Vanguard make near-permanent. In the shop listing it prints without an element tag; in my deck list it prints as `**Undertow** [Hydro]`. **The shop screen hides the element tag that the deck screen shows.**
- I was **energy-capped on literally every turn of the run so far** (3 energy, 5 cards, never once short of cards), which is why I bought **Battle Plan** (its Plan refunds the energy and draws 2) over **Treatise** (draw only) and over **Stolen Chapter** earlier.
- **Skipped Gorou (76)** as unusable: "play a copy of the last other **Companion** card you played this turn" — I have never been offered a card tagged Companion and cannot tell from any screen which cards are Companions. The same dead text sat on **Rally** in an earlier reward.
- **Skipped all three relics.** Ghost Seed ("Strikes and Defends gain Ethereal") reads as a pure downside for a deck that still runs 3 Strikes and 4 Defends, and at 222 it would have eaten the whole budget.

Removed a **Strike**. Deck 16:
Strike ×3, Defend ×4, Kurage's Oath, Slack Water, Sea-Salt Prayer, Feint ×3 (one with Sharp 2), Undertow, Vanguard, Battle Plan.

---

## Elite — Phrog Parasite → 4 Wrigglers (floor 6). The best fight of the run.

Entered at `HP 45/80`. `Phrog Parasite — HP 61/61`, `Intent: Strategic (StatusCard) — the number on its icon is 3`, and the line that made the whole fight:

> `Infested 4 (buff) — Upon dying, summons... something.`

That is the literal text. It tells you a death trigger exists, gives it a number (4), and then declines to say what it summons. As a warning it worked — I planned around a post-kill surprise — but it is the only power in the run whose effect is deliberately withheld.

### Round 1 — 16 predicted, 16 dealt

No damage incoming, so Defends were dead cards. Feint → Plan (10), Slack Water (4 + 2 Casket = 6), one Defend for the spare energy. **Predicted 61 − 16 = 45. Got `HP 45/61`.**

Pile count then read 6 + 8 + 5 = **19** against my 16-card deck: the 3 Status cards had arrived, unannounced by any line of text.

### Round 2 — Thorns against a 4×4 attacker

Intent read `the number on its icon is 4x4 — This enemy intends to Attack for 4 damage 4 times`. Liquid Bronze is `Gain 3 Thorns` / `When hit by an attack, deal 3 damage back` — against four separate hits that is 12 damage for a potion, so I spent it here rather than on a single-hit enemy.

Played: Liquid Bronze, Feint → Plan, Kurage's Oath → Plan, Strike (6).

**Predicted:** 45 − 6 = 39, then 4 hits × 3 Thorns = 12 → 27, then next turn's two Plans (10 + 7 = 17) → **10**. I take the full 16.

**Happened:** round 3 opened `Phrog Parasite — HP 10/61` and `HP 29/80`. Every number exact.

Two mechanical facts confirmed here: **Thorns does not reduce incoming damage** (I took all 16), and Thorns fires per *hit*, not per attack action.

### Round 3 — Undertow's condition, and stacking Plans in order

`Undertow — Deal 7 damage. If the enemy has a debuff, deal 10 instead.` The Parasite was wearing `Hydro Aura 1`. **Undertow dealt 7, not 10** (10 → 3), confirming that an aura is not a debuff for this condition — which the aura footnote does say outright ("it is neither [buff nor debuff]"), so the two texts agree. Good.

I set two Plans **in a deliberate order**, because the Bake-Kurage "carried these out ... in this order": Vanguard first (`Plan: Apply 1 Vulnerable and 1 Weak`), Feint second (`Plan: Deal 10 damage`), so that Vanguard's Vulnerable would already be on the target when Feint landed — the Plan glossary promises "Enemy Vulnerable raises it". Then Strike killed the Parasite.

**This is the most interesting decision the character offered all run.** Ordering two Plans so an amplifier resolves before a payload is a real, legible, non-obvious play, and it worked.

### The summon

```
- **Wriggler (1)** — HP 17/17   Intent: Stunned (Stun) — This enemy can't act on its next turn.
- **Wriggler (2)** — HP 19/19   Stunned
- **Wriggler (3)** — HP 21/21   Stunned
- **Wriggler (4)** — HP 18/18   Stunned
```

**75 HP of new enemies against my 29.** The saving grace, printed clearly, is that all four enter Stunned, which buys exactly one turn.

Round 4 opened with only **three** Wrigglers. The stacked Plans had killed the 17 HP one outright: Vanguard applied 2 debuffs (Vulnerable + Weak), each tripping the Casket for 2 = 4 damage, leaving 13, and the Vulnerable-amplified Feint covered the rest. The ordering paid for itself immediately.

### The Status card, and a rule the block bar quietly enforces

> `Infection — cost 0, status. Unplayable. At the end of your turn, if this is in your Hand, take 3 damage.`

This is a genuinely threatening status: unplayable, so you cannot cycle it out, and it bills you every turn it sits in hand.

Round 4 I played Sea-Salt Prayer (Weak + 2 Casket) and Strike into the 18 HP Wriggler and one Defend, for 9 Block. I **predicted HP 29 − 3 (Infection) = 26**. Round 5 printed `HP 29/80` — **the prediction was wrong and the screen was right**: 9 Block absorbed the Infection's 3 *and* the 6-damage attack, exactly 9. So Infection's damage is ordinary damage that Block eats, and it resolves at end of *your* turn while your Block is still standing. Nothing says this; I only learned it by mispredicting.

Also confirmed: `Wriggler (2)` went `21 → 18` on a turn its attack was **fully blocked**. Thorns fires on a blocked hit.

### Rounds 5–7 — the race

Round 5: three Wrigglers (19 / 18 / 10), two of them Empowered to `Strength 2`, 16 incoming, and **no block card in hand**. Spent the Block Potion (12), killed the 10 HP Wriggler with Undertow (7) + Feint (6), and banked the Sharp Feint as a Plan for 10 rather than playing it for 8 — a straight +2 with no lethal on the line.

**Result: `HP 29/80` unchanged**, and the front Wriggler fell 19 → 16 (Thorns) → 6 (Plan).

Round 6 was the cleanest turn of the run. Board: `Wriggler (1) — HP 6/19` Empowering (no attack), `Wriggler (2) — HP 18/21` intending `Attack for 8`. My three attacks were Feint 6 + Strike 6 + Strike 6 = **exactly 18**. Killing W2 before its turn meant the only remaining enemy was not attacking, so the turn cost **0 HP** — strictly better than killing the cheap 6 HP target and eating 8.

Round 7: the last Wriggler sat at 6 HP with `Strength 4`, intending 10. One Strike is exactly 6. Dead.

**Elite result:** won at `HP 29/80`. Took 16 damage across the entire two-stage fight, all of it on the single 4×4 turn.

### Reward

`40 Gold`, the relic **Akabeko**, and a card from: **Undertow**, **Shell Guard** ("Gain 5 Block. Until your next turn, whenever the Tamakushi Casket strikes, gain 3 Block."), **Salt Line**, **Venti — Wind's Grand Ode** (cost 2, "Deal 8 damage to ALL enemies. For 2 turns, at the end of your turn Swirl ALL enemies. Exhaust.").

Took a second **Undertow**: 10 damage for 1 energy is the best from-hand rate in my deck and its condition is one my own relic keeps satisfied. Venti was tempting after a 4-enemy swarm, but at cost 2 with Exhaust it is 4 damage per energy per enemy, and I was energy-capped every turn of the run. Deck 17.

Gold 54.

---

## Event — Aroma of Chaos (floor 7)

`Let Go` (Transform a card) vs `Maintain Control` (Upgrade a card). Took the Upgrade: a Transform is a random replacement and I could not afford a coin flip on a deck I had just tuned.

Upgraded **Kurage's Oath**, my only card that scales with enemy count, having just been nearly killed by a four-enemy swarm. Preview:

> `**Kurage's Oath+** (upgraded) — Play on the Bake-Kurage. Plan: Deal 10 damage to ALL enemies.` (7 → 10)

**This is the clean contrast with the Sharp enchant.** An *upgrade* raises the Plan number (7 → 10). The *Sharp 2* enchant did not (Plan stayed 10 while the hand number moved 6 → 8). Two different power-ups, opposite behaviour toward the same number, and neither card face says so.

### What the deck screen could not tell me

The card list on this screen carried a block titled "Not on this list, and why", holding **seven `Infection` rows**, each reading:

> `**Infection** — on the screen's list nowhere, and nothing on the feed says why`

with the footnote:

> `This page has no deck on this screen's data feed: the list above is your deck as it stood in the last fight (floor 7), minus the cards the screen is offering. Anything you have picked up since is in neither list.`

So this is the bridge being honest about a limitation rather than a game defect: the list it can show is the *last fight's* deck, which still contained the seven Infections generated during that fight. It does mean **I could not verify from any screen whether Infection persists into the permanent deck** — I resolved that later by pile arithmetic (see below).

## Rest site (floor 8) — Rest

`Rest — Heal for 30% of your Max HP (24).` At `HP 29/80` this was not a choice. `HP 29/80` → `HP 53/80`, exactly +24.

## Treasure (floor 9) — Juzu Bracelet

`Juzu Bracelet — Regular enemy combats are no longer encountered in ? rooms.` Free, and it retroactively fixes the thing that had surprised me on floor 3, where an `Unknown` resolved directly into the Shrinker Beetle with no event text.

The chest was **not** empty — the cost I declined at Neow (Silver Crucible's "The first Treasure Chest you open is empty") would have eaten this relic.

## Rest site (floor 10) — Smith

At 53/80 with more rest sites known to be ahead (the map showed a floor of four), I took the upgrade. Put it on the already-enchanted Feint:

> `**Feint+** (upgraded) [Hydro] (Sharp 2) — Deal 11 damage. Plan: Deal 13 damage.`

The upgrade added +3 to **both** modes (6→9 base and 10→13 Plan) and Sharp's +2 still rode on the hand number, giving 11. **Enchant and upgrade stack**, on different halves of the card.

## Event — Tablet of Truth (floor 11)

`Decipher` (Lose 3 Max HP, upgrade a random card) vs `Smash` (Heal 20 HP). Took **Smash**: at 53/80 heading into two elite-heavy floors, 20 HP beat a random upgrade with a permanent Max-HP cost, especially since 7 of my 16 unupgraded cards were Strikes and Defends — a 44% chance of spending 3 Max HP on a dud. `HP 53` → `HP 73/80`.

## Rest site (floor 12) — Smith

At 73/80 a Rest would have healed only 7 of its 24, so the upgrade was worth strictly more.

> `**Undertow+** (upgraded) [Hydro] — Deal 10 damage. If the enemy has a debuff, deal 13 instead.`

13 damage for 1 energy, on a condition my own relic keeps live.

**Deck at this point (17):** Strike ×3, Defend ×4, Kurage's Oath+, Slack Water, Sea-Salt Prayer, Feint+ (Sharp 2), Feint ×2, Vanguard, Undertow+, Undertow, Battle Plan.
**Relics (4):** Tamakushi Casket, Golden Pearl, Akabeko, Juzu Bracelet.
**Potions:** none (both spent in the elite). **Gold:** 54.

---

## Elite 2 — Byrdonis (floor 13). The turn the character finally showed what it is.

Entered at `HP 73/80`. Opening screen carried a new relic line and a new buff:

> `**Akabeko** — At the start of each combat, gain 8 Vigor.`
> `Vigor 8 (buff) — Your next Attack deals 8 additional damage.`

`Byrdonis — HP 81/81`, `Intent: Attack for 17`, `Territorial 1 (buff) — At the end of Byrdonis's turn, it gains 1 Strength.` An escalating 81 HP wall: at 17, 18, 19, 20 a turn, a four-turn fight costs 74 and I had 73.

### Confirmed here: Infection does not persist

Piles read `12 in the draw pile` + 5 in hand = **17**, exactly my deck. The seven Infections from the elite were gone. **Status cards do not survive combat**, which no screen ever states — I could only establish it by counting.

### A display defect, proven by arithmetic

With `Vigor 8` up, my hand printed:

```
- **Strike (1)**  Deal 14 damage.        (6 + 8, correct)
- **Strike (2)**  Deal 14 damage.
- **Undertow+**   Deal 10 damage. If the enemy has a debuff, deal 13 instead.
```

Undertow+ showed **10**. I played it first and Byrdonis went `81 → 63` — it dealt **18**. So Vigor *did* apply, and the face understated it by 8, while the plain Strikes in the same hand had their faces correctly rewritten to 14.

Reproduced next fight (Mawler): with Vigor 8 up, `Feint — Deal 14`, `Slack Water — Deal 12`, `Strike — Deal 14` all included the +8, and `Undertow+ — Deal 10` again did not. **Vigor is reflected on every attack face except Undertow+.** It costs real decisions: I nearly spent the Vigor on a Strike reading 14 when Undertow+ was actually the 18.

### The best turn of the run

Round 2, after Battle Plan's Plan resolved (`Energy 4/3`, and 7 cards in hand — it does exactly what it says), I had 4 energy and this line:

1. **Vanguard** (cost **0**) → Plan — `Apply 1 Vulnerable and 1 Weak`
2. **Kurage's Oath+** → Plan — `Deal 10 damage to ALL enemies`
3. **Feint+** → Plan — `Deal 13 damage`
4. Slack Water from hand — 4 + 2 Casket = 6, and its Weak cut the incoming 12 to 9
5. Defend — 5 Block

Played in that order **specifically so Vanguard's Vulnerable would resolve first** and amplify the two payloads behind it.

**Predicted:** 57 − 6 = 51 now; then next turn 4 (two Casket pings) + 15 (Oath+ ×1.5) + 19 (Feint+ ×1.5) = 38, leaving 13.

**Happened:** round 3 opened `Byrdonis — HP 11/81` and `HP 52/80`. Two better than predicted, and the reason is worth recording: **Vulnerable amplified the Casket's pings too** — 2 became 3 each, so the resolution was 6 + 15 + 19 = 40, not 38. The relic's damage is an Attack for Vulnerable's purposes.

That is **46 damage from one Plan resolution for 3 energy paid a turn earlier**, and it is by a wide margin the most satisfying thing the character does.

Round 3: Byrdonis sat at 11 still wearing `Vulnerable 1`. Undertow saw two debuffs (10) amplified to 15. Dead before it could swing.

**Elite 2 result:** won at `HP 52/80` — **21 damage taken from an 81 HP elite that hits for 17 and grows.** Compare the first elite, fought without Vulnerable access: 16 damage but a 75 HP second stage.

Also noted: with Vulnerable on the enemy, Feint's face rewrote itself to `Plan: Deal 15 damage` (10 × 1.5). **The Plan number previews the Vulnerable multiplier correctly** — which makes Undertow+'s failure to preview Vigor look like an isolated bug rather than a general rule.

### Reward

`42 Gold`, relic **Frozen Egg**, and a card from **Read the Field** ("Gain 5 Block. Plan: Gain 10 Block."), **Tide Wall**, **Moon's Reflection**, **Shinobu — Thundergrust** [Electro].

Took **Read the Field**. My only real gap was Block — four 5-Block Defends against bosses hitting 17+ — and 10 Block for 1 energy in the Plan lane I already use every turn beat Tide Wall's conditional count. Deck 18.

---

## Fight — Mawler (floor 14)

`Mawler — HP 72/72`, `Attack for 4 damage 2 times`. Entered `HP 52/80`.

Round 1 Vigor routing was a genuine decision: Vigor lands on the *next* attack only, so the question was which card should carry +8. Putting it on **Slack Water** (4 + 8 = 12, +2 Casket = 14) also applied the Weak that upgraded **Undertow+** from 10 to 13 — 27 damage from two cards, more than leading with Undertow+ (18) would have produced. Third energy banked Feint as a Plan (10 > 6 from hand).

**Predicted** 72 − 14 − 13 = 45, then Plan 10 → 35, and 6 taken (8 weakened to 6). **Round 2 printed `Mawler — HP 35/72` and `HP 46/80`.** Exact.

Round 2: it intended only a debuff, so Block was dead; Sea-Salt Prayer (2 + Weak) + Undertow (10, debuff live) = 12, and Read the Field → Plan for 10 Block on the turn it would actually attack. `35 → 23`.

Round 3: it had applied `Vulnerable 3 (debuff) — Receive 50% more damage from Attacks for 3 turns` **to me**, and intended 21. With only Feint+ (11) available from hand I could not reach 23, so I blocked to 15 total and pre-loaded Vanguard → Kurage's Oath+ as Plans. Took exactly 6 (`46 → 40`), which confirms **the printed intent number already includes my own Vulnerable** — 21 was the real figure, not 21 × 1.5.

The banked Plans killed Mawler at the start of the following turn (4 Casket + 15 amplified Oath+ ≥ 12) and the fight ended without me acting again.

**Reward:** `19 Gold` and a card from **Vanguard**, **Treatise+** (Innate), **Coral Bulwark**, **Gorou**. Took a second **Vanguard**: at cost 0 it never competes for energy, and Vulnerable is the multiplier the whole deck is built on — its Weak is defense in the same card. Deck 19.

## Rest site (floor 15) — Rest

`HP 40/80` → `HP 64/80`. Standing on the boss node.

**Going into the boss:** HP 64/80, 115 gold, no potions, relics Tamakushi Casket / Golden Pearl / Akabeko / Juzu Bracelet / Frozen Egg.

---

## Boss — The Kin (floor 17). Where the run ended, and why.

Entered at `HP 64/80`, deck 19, five relics, no potions.

```
- **Kin Follower (1)** — HP 58/58   Intent: Empower (Buff)
    Minion 1 (buff) — Minions abandon combat without their leader.
- **Kin Follower (2)** — HP 59/59   Intent: Attack for 5
    Minion 1 (buff) — Minions abandon combat without their leader.
- **Kin Priest** — HP 190/190       Intent: Attack for 8, and also: apply a Debuff to you
```

`Minion 1 (buff) — Minions abandon combat without their leader` is a genuinely excellent piece of printed text: it tells you, without a tutorial, that the 117 HP of Followers is optional and only the Priest's 190 matters. I read it and committed to a Priest-only race.

### The structural problem, and the test I ran to confirm it

The Plan glossary, printed on every screen of the run, says a Plan "lands first thing next turn **on the front enemy**". The Priest is listed **third**. If that line is literal, then the entire Plan lane — the character's defining mechanic, and provably its best damage rate — cannot touch the boss while two 58/59 HP minions stand in front of it.

I spent one energy on round 2 to test it rather than guess: banked a Feint as a Plan and watched where the 10 landed.

**Result:** round 3 printed `Kin Follower (1) — HP 48/58` (exactly −10) while the Priest showed `144/190`, down exactly the 22 my three hand-played attacks had done (6 + 6 + 10). **Single-target Plans hit the front minion, not the boss.** Confirmed by arithmetic, not inference.

That is the fight, in one line. Against Byrdonis my Plan stack did **46 damage in a single resolution**. Against The Kin, the same cards deliver 10–13 into a minion I have no reason to kill. What remained was Kurage's Oath+ (10 to ALL, so 10 of it reaches the Priest) and Slack Water's Weak-to-ALL — plus hand-played attacks worth roughly 22–28 a turn into a 190 HP target.

### The Priest attacks the deck, not just the character

Its debuff intent alternated between two debuffs aimed precisely at my two win conditions:

- `Frail 1 (debuff) — Gain 25% less Block from cards for 1 turn.` My Defends visibly rewrote to `Gain 3 Block`. It landed on rounds 2 and 6.
- `Weak 1 (debuff) — Attacks deal 25% less damage for 1 turn.` Feint+ rewrote to `Deal 8`. It landed on round 3.

Worth recording that under my own Weak the Plan lane is again the correct mode, exactly as the glossary promises — "Enemy Vulnerable raises it; **your Weak does not**" — and Feint+ kept printing `Plan: Deal 13` while its hand number fell to 8. The mechanic is coherent; it simply had no legal target here.

### Round by round

- **R1.** Vigor routed onto Slack Water (12) so its Weak upgraded Undertow to 10: 24 total. **Predicted 190 → 166; got `166/190`.** Took 11 (5 + weakened 6), `64 → 53`.
- **R2.** Battle Plan's Plan delivered `Energy 4/3` and 7 cards. Ran the Plan-targeting test plus 22 to the Priest. Took 19, `53 → 34`.
- **R3.** 17 incoming at 34 HP. Blocked 10 and banked Vanguard → Kurage's Oath+. Took exactly 7, `34 → 27`. The resolution paid: Vulnerable made Follower 1 take 6 + 15 = 21, and **Oath+ hit all three for 10** (Priest 144 → 134).
- **R4.** Only 7 incoming (both Priest and Follower 1 Empowering). Used the Vulnerable window to kill Follower 1 with two Undertows (10 and 10, each ×1.5 = 30 vs 27 HP), and Sea-Salt Prayer's Weak held the damage to **1**. `27 → 26`.
- **R5.** Blocked and banked Battle Plan. Took 6, `26 → 20`.
- **R6.** Weakened the Priest, hit for 17, banked Oath+. Took 4, `20 → 16`.
- **R7.** 24 incoming (9 + 5×3). Block ceiling was 10 (two Defends). **Predicted 16 − 14 = 2; got `HP 2/80`.**
- **R8.** The Priest Empowered instead of attacking, so only the Follower's 6×2 = 12 was incoming — survivable in principle. But the arithmetic was closed: my whole hand held exactly 10 Block (Read the Field 5 + Defend 5) and exactly 16 damage (Undertow+ 10 + Strike 6) against a 21 HP Follower. **I could neither block 12 nor kill 21.** 12 − 10 = 2, and I had 2. `end turn` returned `TOOL-BLOCKED: game_over`.

**Final board:** Kin Priest `97/190` (I removed 93 of it), Kin Follower `11/59`, one Follower killed. Died on floor 17.

**Was it winnable from where I stood?** I do not think so, and the numbers say why rather than my judgement: from round 3 onward the Priest alone needed ~5 more turns at my achievable ~25/turn against it, while incoming climbed from 13 to 24 a turn with both Followers Empowering repeatedly. I had 64 HP entering and 68 HP of total healing across the whole act. Where I would play differently is earlier — see findings.

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

**Plan ordering was the best decision the game offered.** On Byrdonis I played Vanguard → Kurage's Oath+ → Feint+ onto the Bake-Kurage *in that order*, because the screen says plans are "carried out ... in this order" and that Vulnerable "raises" Plan damage. The payoff was 46 damage in one resolution. Nothing told me to do this; it was inferable from two separate printed lines, and it worked. That is a real, deep choice.

**Whether to bank a card or play it.** Every Plan card is a live decision each turn: Feint+ is 11 now or 13 next turn; under Shrink it was 4 now or 10 next turn; under Vulnerable the Plan face rose to 15. The trade is tempo against rate, and the answer genuinely changed with the board.

**Where to route Vigor.** Akabeko's 8 goes to the *next* Attack only. On Mawler, putting it on Slack Water (12) rather than Undertow+ (18) was correct because Slack Water's Weak turned Undertow+ from 10 into 13 — 27 across two cards instead of 24. A small, real optimisation.

**Kill-before-it-acts.** Repeatedly the sharpest lever: killing Leaf Slime with exactly 12 cancelled a Status card; killing Wriggler (2) with exactly 18 cost me 0 HP where killing the cheap 6 HP target would have cost 8; killing the Parasite's first stage before its second Status intent saved three more cards.

**Fight-1 round 3** was a well-shaped early puzzle: I could prove the draw pile was Strike ×3 + Defend ×2, prove 18 ≥ 14, and therefore prove that the all-block line reached the same kill turn for zero HP.

### (b) What felt automatic, and what never seemed worth playing

**Defend was automatic and mostly dead.** Turn after turn the correct play was "the enemy is Empowering or applying a debuff, so Block does nothing" — on those turns Defends were simply unplayable value. When Block did matter, 5 was too small against 17–24 hits.

**Strike was automatic.** 6 damage, no text, no decision. By the end it was the worst card in the deck and I removed one at the first opportunity.

**Never worth playing:** cards keyed to **Companion**. `Rally` ("The next Companion card you play this turn costs 1 less") and `Gorou — Crystal Collapse` ("play a copy of the last other Companion card you played this turn") were offered three times between them, and **no screen in the entire run ever identified a card as a Companion.** Named cards like `Thoma — Blazing Barrier`, `Sayu`, `Kujou Sara`, `Shinobu` are presumably it, but nothing says so. I could not evaluate those cards, so I never took them.

**Stolen Chapter / Treatise (draw)** never looked worth it: I was energy-capped on effectively every turn of the run, and never card-capped.

### (c) What I could not understand, or that contradicted its own printed text

1. **The Plan glossary contradicts the Plan cards.** "the Plan lands first thing next turn **on the front enemy**" is printed on nearly every screen, yet Kurage's Oath's own text says "Deal 7 damage to **ALL enemies**" and it verifiably hit all of them (both slimes took exactly 7). The glossary is simply wrong for ALL-Plans — and it is the most repeated line in the game.
2. **`skip` on the enchant screen.** Two separate lines promised the pick was revokable; `skip` returned `error No cancel/close button is currently enabled`, and `choose` refused me back to `skip`. The two forms point at each other and neither works.
3. **"Sharp" and "Nimble" are never defined** at the point of choosing between them. The Self-Help Book asks you to pick one blind; `Sharp` is only explained after you provisionally select a card.
4. **`Infested 4 (buff) — Upon dying, summons... something.`** Deliberately withheld. It worked as a warning, but I could not price the decision to kill.
5. I could not tell **which enemy is "the front"** from any screen. I inferred it is the first listed, and the Feint test confirmed it, but nothing marks it.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted:** `Infection — cost 0, status. Unplayable. At the end of your turn, if this is in your Hand, take 3 damage.` Unplayable, so it cannot be cycled, and it bills you for holding it. Seven accumulated inside one fight. `Defend` is the honourable mention — the card I most often played only because nothing better was legal.

**Happiest to draw:** `Vanguard — cost 0. Play on the Bake-Kurage. Plan: Apply 1 Vulnerable and 1 Weak.` It costs nothing, so it never competes for the resource I was always short of; it sets up every other card in the deck; and its two debuffs each trip the Casket. It turned an 81 HP escalating elite into a 3-turn kill. `Feint+` is the runner-up on raw numbers, but Vanguard is the card that made the deck a deck.

### (e) Did the first turn of the first fight already present a decision?

**Yes, though a shallow one.** Round 1 of fight 1 offered 3 energy, a 4-damage intent, and a hand of Kurage's Oath / Strike / Slack Water / Defend ×2. The real decision was recognising that a 4-damage intent makes both Defends worthless, and that Kurage's Oath must be *banked* rather than played — the Bake-Kurage and the Plan line are both introduced and both matter on turn one. What makes it shallow is that the answer is forced: with only one non-Defend line available there is no cost to weigh. The **third** turn of that fight was the first genuine decision (see (a)).

### (f) Anything a screen granted or changed without saying so

1. **99 starting gold.** No screen printed it. My tally of every gold line said 193; the shop said `You have 292 gold`. The difference is exactly 99, and the shop is the first place gold appears at all.
2. **The run began at 64/80**, not full. Nothing explained the missing 16.
3. **Status cards arrive silently.** No line ever said "you gained a card". I detected all of them by pile arithmetic (e.g. `6 + 8 + 5 = 19` against a 16-card deck).
4. **Status cards leave silently too.** Nothing says they are temporary. I established it by counting: after the elite that gave me seven Infections, the next combat opened at `12 draw + 5 hand = 17`, exactly my deck.
5. **The Casket's ping applies an aura.** Sea-Salt Prayer carries no `[Hydro]` tag and says nothing about elements, but its target came out wearing `Hydro Aura 2` — the relic's 2 Hydro damage lays an aura, which no text mentions.
6. **Infection's damage is absorbed by Block.** Its text ("take 3 damage") reads like unpreventable loss; I predicted −3 and the screen printed unchanged HP, because 9 Block ate the 3 plus a 6-damage attack.
7. **Vulnerable amplifies the relic's pings.** The Casket's 2 became 3 each under Vulnerable — which is why Byrdonis ended on 11 instead of my predicted 13.
8. **Thorns fires through full Block.** Wriggler (2) went 21 → 18 on a turn its attack was completely blocked.

---

## Findings, ranked by sharpness

**1. The boss's formation disables the character's core mechanic, and the glossary is where you would learn that — except it says the opposite.**
Single-target Plans land on the front enemy; The Kin puts 117 HP of Followers in front of a 190 HP Priest whose own text (`Minions abandon combat without their leader`) tells you not to kill them. Proof: I banked a Feint as a Plan on boss round 2; round 3 printed `Kin Follower (1) — HP 48/58` (−10) while the Priest moved only by the 22 my hand attacks did (`166 → 144`). Against a single target the same lane produced **46 damage in one resolution** (Byrdonis, `57 → 11` across one turn boundary). The player is asked to build around Plans all act and is then handed a boss that reads them out of the fight, with no printed way to retarget. **This is the finding I would act on first.**

**2. The `Plan` glossary line is factually wrong, and it is the most-printed line in the game.**
"the Plan lands first thing next turn **on the front enemy**" appears on essentially every screen, including screens showing cards that say "ALL enemies". Kurage's Oath hit both slimes for exactly 7 (20→13 and 8→1) and later hit all three Kin for 10. A player who trusts the glossary will mis-evaluate every AoE Plan in the kit; a player who trusts the card will be right.

**3. An enchant pick is advertised as revokable twice and is not.**
Screen: "You may say `skip` to undo this pick and choose again; it does not leave the screen." `skip` → `error No cancel/close button is currently enabled - selection may be mandatory`. `choose "Slack Water"` → refused, with the refusal telling me to use `skip`. The two documented escape hatches point at each other and neither functions. It cost me the correct enchant target: Sharp 2 on Slack Water is 6 + 2 Casket = 8 damage **plus a Weak**, strictly better than the 8-damage Feint I was locked into.

**4. `Sharp` and `Nimble` are undefined at the moment you must choose between them.**
The Self-Help Book offers "Enchant with Sharp 2" vs "Enchant with Nimble 2" with no definition on that screen and none in its glossary block. `*Sharp* — Increases damage on this card by 2` only appears after provisionally selecting a card — one screen *past* the irreversible branch.

**5. Sharp does not raise a Plan number; an upgrade does. Nothing says so.**
`Feint (Sharp 2) — Deal 8 damage. Plan: Deal 10 damage.` (hand +2, Plan unchanged) versus `Kurage's Oath+ — Plan: Deal 10 damage` (7 → 10). Two power-ups behaving oppositely on the same number, discoverable only by reading a preview carefully. It is a real trap: I nearly put the enchant on the card whose Plan mode I use most, where it would have been worth almost nothing.

**6. Vigor is previewed on every attack face except Undertow+, which still receives it.**
With `Vigor 8` up: `Strike — Deal 14` (6+8, correct), `Feint — Deal 14`, `Slack Water — Deal 12`, but `Undertow+ — Deal 10`. Played first, Undertow+ took Byrdonis `81 → 63` — it dealt **18**. Reproduced the next fight, with the same three cards correct and Undertow+ again understated. This actively misroutes the decision: the faces say the Strike is your biggest hit when Undertow+ is.

**7. Companion-keyed cards are unevaluable because nothing marks a Companion.**
`Rally` and `Gorou — Crystal Collapse` both key off "Companion card"; no card, glossary line, or deck screen in 17 floors ever tagged one. Three separate card rewards were effectively one option shorter than they looked.

**8. Vulnerable amplifies relic damage — a real, undocumented bonus.**
Byrdonis finished on `11/190` where I predicted 13; the gap is exactly the Casket's two pings going 2 → 3 under Vulnerable. Good behaviour, but it means the relic's contribution scales with the debuff engine in a way no text hints at.

**9. Status-card lifetime is invisible.** Nothing says Slimed/Infection are temporary. Establishing it took pile arithmetic across two combats. The deck screen actively cannot help: it renders seven `Infection` rows under "Not on this list, and why", with the honest footnote that it is showing the *last fight's* deck.

**10. Two silent grants at the start of a run:** 99 gold that appears for the first time inside the shop total, and an opening `HP 64/80` that no screen explains.

**11. Where I could not tell.** I could not determine whether the act-1 boss is beatable by this character with better play from floor 1 — my sample is one run, and I never saw a full-strength deck reach it. What I *can* say with numbers is that the loss was not a play error inside the boss fight (every prediction inside it landed exactly, and round 8 was arithmetically closed at 10 Block / 16 damage versus 12 incoming / 21 HP); it was decided by the 190 HP target being unreachable by the lane the deck is built on. I also cannot tell whether "front enemy" would have shifted to the Priest had I killed both Followers — I never got there, and no screen states the rule.

---

## Non-blindness declaration

- **Commands outside the two allowed forms: none.** Every game action was `GITS_LANE=1 python -m understudy.blindplay observe` or `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, run from the repo root. I ran no other `understudy` subcommand, no `git`, and never touched lane 2. I never launched, closed, restarted or tore down the game.
- **Tools used:** the Bash tool (only for the two blindplay commands above, plus `sed`/`grep`/`tail`/`cat >>` to trim output and append to this record), the Write tool (to create this record and one scratch file under the session scratchpad), and the Edit tool (to fill in this record's Identity block). Nothing else.
- **Repo files read: none.** I read no source, YAML, docs, rulings, backlog, or any earlier record. Everything above comes from what the screens printed.
- **Files written:** this record, `review/qa/kokomi-round-5-2026-09-03/opus-run2-act1.md`, and one scratch file under `C:\Users\Monty\AppData\Local\Temp\claude\...\scratchpad\` used only to assemble this record's final sections. I minted no identifiers and edited no other file in the repo.
- **Lane state:** the lane was left standing exactly where it stopped — on the game-over state after the round-8 `end turn` returned `TOOL-BLOCKED: game_over`. I sent no command after that.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
