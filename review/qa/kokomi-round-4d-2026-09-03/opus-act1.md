# KLEEMOD-KOKOMI — blind seat, lane 1, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 4d, first seat of three (act 1 only).
- **Lane:** 1.
- **Character:** KLEEMOD-KOKOMI.
- **Run seed:** never printed on any screen I saw.
- **Act:** 1. Map depth 16 floors. Boss named by the map: **Ceremonial Beast**.
- **Actions accepted / refused:** **195 accepted, 0 refused.** No `act` call was ever rejected and
  no bare `observe` ever produced a traceback or a `PacketLeak`.
- **Termination reason:** **stop condition (1)** — the act-1 boss was resolved, its reward screen was
  handled, and the lane now stands on the act-2 map screen. 55 of the 250-action budget unspent.
- **Where the run stands:** act-2 map, first node choice (`Ancient (path 1)`), HP **58/87**. The
  act-2 boss is printed as **The Insatiable**.
- **HP trajectory (every reading the screens printed, in order):**
  64/80, 64/80, 62/80 (fight 1) — 62/80, 62/80, 58/80, 57/80 (fight 2) — 64/87, 60/87, 60/87
  (fight 3) — 60/87, 53/87, 43/87 (fight 4) — 43/87, 43/87, 43/87, 43/87, 35/87 (elite 1) —
  35/87 then 61/87 (rest 1) — 61/87, 50/87, 44/87, 28/87 (elite 2) — 28/87 then 54/87 (rest 2) —
  54/87, 54/87, 54/87 (fight 5) — 54/87, 54/87, 54/87, 54/87 (elite 3) — 54/87 then 80/87 (rest 3) —
  80/87, 80/87, 69/87, 69/87, 69/87, 58/87 (boss). **Final: 58/87.**
- **Gold:** 15, 27, 38, 51, 92, 128, 147, 189, **304** after the boss (the boss paid `100 Gold` plus
  a separate `15 Gold` row, which is `Amethyst Aubergine`).
- **Potions held at the stop:** `Vulnerable Potion` — "Apply 3 Vulnerable". (Spent during the act:
  `Attack Potion` on elite 1, `Strength Potion` on the boss, `Colorless Potion` traded at the
  Future of Potions event. A `Power Potion` off elite 3 was selected and silently not granted.)
- **Relics, exactly as printed:**
  - **Tamakushi Casket** — "Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy. Card rewards after a fight offer a fourth Companion choice."
  - **Kaleidoscope** — "Upon pickup, obtain 2 card rewards from other characters."
  - **Oddly Smooth Stone** — "Start each combat with 1 Dexterity."
  - **Snecko Skull** — "Whenever you apply Poison, apply an additional 1 Poison."
  - **Meal Ticket** — "Whenever you enter a shop room, heal 15 HP." (never triggered; no reachable Shop)
  - **Anchor** — "Start each combat with 10 Block."
  - **Amethyst Aubergine** — "Enemies drop 15 additional Gold."

### Deck as reconstructed from faces printed in hand (22 cards at the stop)

The starter was **10 cards**, fixed by pile counts in fight 2 (hand 5 + hand 5 + draw 3 = 13 with no
reshuffle, against a 13-card deck that already held Uproar and Pounce):

- `Strike` x4 — cost 1, attack, "Deal 6 damage."
- `Defend` x4 — cost 1, skill, "Gain 5 Block."
- `Kurage's Oath (proto)` — cost 1, skill, "Play on the Bake-Kurage. Plan: Deal 7 damage to ALL enemies."
- `Slack Water (proto)` [Hydro] — cost 1, attack, "Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies."

Added during act 1:

- `Uproar` — cost 2, attack, "Deal 6 damage twice. Play a random Attack from your Draw Pile." (Neow)
- `Pounce` — cost 2, attack, "Deal 14 damage. The next Skill you play costs 0 [Energy]." (Neow)
- `Amber — Explosive Puppet` — cost 1, skill, "The next time an enemy attacks you, take 3 less damage and deal 8 Pyro damage to ALL enemies." (fight 1)
- `Razor — Lightning Fang` — cost 1, skill, "For 2 turns, your Attacks apply Electro and deal 3 additional damage. Exhaust." (fight 2)
- `War Council` — cost 1, skill, "Play on the Bake-Kurage. Plan: Deal 5 damage and apply 1 Weak to ALL enemies." (fight 3)
- `Razor — Claw and Thunder` [Electro] — cost 1, attack, "Deal 8 damage. If this is the third Attack you played this turn, gain 1 Energy." (fight 4)
- `Sango Isshin (proto)` [Hydro] — cost 2, attack, "Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead." (elite 1)
- `Kamisato Ayaka — Soumetsu` x2 — cost 2, skill, "For 2 turns, at the end of your turn deal 8 Cryo damage to ALL enemies. Then deal 16 Cryo damage to ALL enemies. Exhaust." (elite 2, and the boss)
- `Vanguard` — cost 0, skill, "Play on the Bake-Kurage. Plan: Apply 1 Vulnerable and 1 Weak. Exhaust." (fight 5)
- `Battle Plan` — cost 1, skill, "Play on the Bake-Kurage. Plan: Gain 1 Energy and draw 2 cards." (elite 3)
- `Undertow (proto)+` (upgraded) [Hydro] — cost 1, attack, "Deal 10 damage. If the enemy has a debuff, deal 13 instead." (Future of Potions event)

Three **Status cards** were forced into my piles by the Phrog Parasite. I never drew one and no
screen ever printed a face for them, so they are not in the list above; the only evidence they
existed is a pile count of 22 against a 19-card deck.

---

## Neow (opening event)

Screen printed three options:

- **Lead Paperweight** — "Choose 1 of 2 Colorless cards to add to your Deck."
- **Kaleidoscope** — "Obtain 2 card rewards from other characters."
- **Neow's Sacrifice** — "Procure 1 Ambergris and add 1 Guilty to your Deck."

**Predicted:** two whole card rewards is more raw power than one colorless pick, and I did not
know what `Ambergris` or `Guilty` were — the screen never defined either word, so the third option
was unpriceable. Chose **Kaleidoscope**.

**Happened:** two card-reward screens, both drawn from other characters' pools.

Reward 1 offered:
- `Glitterstream` — cost 2, skill, "Gain 11 Block. Next turn, gain 5 Block."
- `Uproar` — cost 2, attack, "Deal 6 damage twice. Play a random Attack from your Draw Pile."
- `Shared Billing [Hydro]` — cost 1, skill, "Apply Hydro to a random enemy. Spotlighted Companion
  numbers are 25% stronger this turn. Gain 1 Energy."

Took **Uproar**: 12 printed damage for 2 energy plus a free extra attack beat 16 block over two
turns, and `Shared Billing` referenced "Spotlighted Companion", a term no screen had defined and
which my character showed no sign of having.

Reward 2 offered:
- `Tinder Toss [Pyro]` — cost 1 **Spark**, attack, "Set off and deal 4 damage to a random enemy twice."
- `Pounce` — cost 2, attack, "Deal 14 damage. The next Skill you play costs 0 [Energy]."
- `Compile Driver` — cost 1, attack, "Deal 7 damage. Draw 1 card for each unique Orb you have."

Took **Pounce**. `Compile Driver` scales on Orbs and nothing had printed an Orb; `Tinder Toss` costs
a Spark and the glossary said "Start each combat with 1" with no cap — free damage, but random
target and only once per combat unless something grants more Sparks, and the card that grants more
(`Pounding Surprise`) is named in its own glossary line without being in my deck.

---

## Map (act 1)

```
- 1 floor ahead: Monster, Monster, Monster
- 2 floors ahead: Monster, Unknown, Monster, Unknown
- 3 floors ahead: Unknown, Monster, Unknown, Shop, Unknown
- 4 floors ahead: Monster, Monster, Monster, Unknown
- 5 floors ahead: Unknown, Monster, Monster, Shop
- 6 floors ahead: Unknown, RestSite, Monster
- 7 floors ahead: Elite, Unknown, Unknown, Elite, RestSite
- 8 floors ahead: RestSite, Elite, Shop, Monster
- 9 floors ahead: Treasure, Treasure
- 10 floors ahead: Elite, Elite, RestSite
- 11 floors ahead: Unknown, RestSite, Monster
- 12 floors ahead: Monster, Elite, RestSite
- 13 floors ahead: Elite, Monster, Monster
- 14 floors ahead: Unknown, Unknown, Elite
- 15 floors ahead: RestSite, RestSite
- 16 floors ahead: Boss
At the top of this act: Ceremonial Beast
```

Took `Monster (path 1)` — the only first node whose printed continuation offered both a Monster and
an Unknown ("leads on to: Monster, Unknown").

---

## Fight 1 — Shrinker Beetle (38 HP)

Opening screen, round 1: HP **64/80**, Energy 3/3, draw pile 7, `Bake Kurage 1 (buff)`.

The Bake-Kurage block printed: "The Bake-Kurage is on the field for the whole fight. Enemies cannot
touch it. Play a card on it to write its **Plan** line instead of playing the card now. / Nothing is
planned. The morning is empty."

Enemy intent round 1: "Strategic (DebuffStrong) — This enemy intends to apply a Debuff to you."

Hand: `Defend`, `Strike`, `Pounce`, `Uproar`, `Strike`.

**Predicted:** the intent was a debuff, so Block was worth nothing this turn. `Uproar` at 12 printed
damage plus a random attack out of a 7-card draw pile that I believed was mostly Strikes should beat
`Pounce`'s 14 even counting Pounce's free skill. Estimated Uproar ≈ 18, then Strike 6 → enemy to 14.

**Happened:** Uproar took the Beetle 38 → **20**, exactly 18. It also left `Hydro Aura 2 (aura)` and
`Weak 1 (debuff)` on the Beetle, and the draw pile went 7 → 6 with 2 cards in discard. So the random
attack it pulled was a Hydro attack from my starting deck that applies Weak. 12 + 6 = 18: either
that card deals 6, or it deals 4 and the Tamakushi Casket's "2 Hydro damage whenever you apply a
debuff" made up the difference. **The screen never printed that card's face, so I could not tell
which** — this is the only card in my own starting deck whose text I have never seen.

Then Strike: 20 → **14**, exactly 6.

Round 2. New debuff on me: `Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks deal
30% less damage.` **Every Strike in hand now printed "Deal 4 damage" instead of "Deal 6 damage"** —
the card face is rewritten to the post-debuff number, which is genuinely useful and is the clearest
thing any screen did all fight.

Hand: `Defend` ×3, `Kurage's Oath (proto)`, `Strike`(4). Enemy 14 HP, intent "Attack for 7".

`Kurage's Oath (proto)` — cost 1, skill: "Play on the Bake-Kurage. Plan: Deal 7 damage to ALL enemies."

**Predicted:** Oath (1) planned + Strike (1) for 4 + one Defend (1) for 5 block → enemy to 10, I eat
7 − 5 = **2** damage, and next turn the plan opens for something in the 4–7 range (I expected Shrink
to cut the plan's 7 down to 4, the same way it cut Strike).

**Happened:** HP 64 → **62**, exactly the 2 predicted. Enemy 14 → **3**, which is 11, not the 8 I
had penciled as the low case: the Bake-Kurage line printed `Bake-Kurage: Kurage's Oath (proto), 7`
and the plan dealt its **full 7 — Shrink did not reduce it**, while the Strike I played from hand
in the same fight was reduced from 6 to 4. That is the sharpest mechanical fact of the fight and
nothing on any screen says it.

Round 3: enemy 3 HP, intent "Attack for 13" (up from 7 — it escalates, and nothing printed says so).
One Strike for 4 killed it.

**Fight 1 result:** won on round 3, HP 62/80, 2 damage taken total.

### Fight 1 rewards

`15 Gold`, `Attack Potion`, and a card reward with **four** options (the Casket's promised fourth
Companion choice, and the fourth entry is indeed the only one with a character name on it):

- `Vanguard` — cost 0, skill, "Play on the Bake-Kurage. Plan: Apply 1 Vulnerable and 1 Weak. Exhaust."
- `Exposed Flank` — cost 1, skill, "Apply 1 Vulnerable. Plan: Apply 2 Vulnerable to ALL enemies."
- `Song of Pearls (proto)` — cost 1, power, "Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block."
- `Amber — Explosive Puppet` — cost 1, skill, "The next time an enemy attacks you, take 3 less damage and deal 8 Pyro damage to ALL enemies."

**Took `Amber — Explosive Puppet`**: 8 damage to all enemies plus 3 mitigation for 1 energy is the
biggest number on the screen, and it is the only one of the four that does not need the Plan engine
to already be running.

---

## Fight 2 — Nibbit (45 HP)

Round 1 opened HP **62/80**, Energy 3/3, draw 8, deck now 13.

This screen finally printed the face of the card Uproar had pulled in fight 1:

> **Slack Water (proto)** [Hydro] — cost 1, attack. "Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak
> to ALL enemies." *Applies Hydro* — If the target has no aura, this applies Hydro for 2 turns.

So fight 1's arithmetic resolves: 4 printed damage + the Casket's 2 Hydro for the Weak = 6, and
12 + 6 = the 18 I measured. **My starting deck is Strike x4, Defend x4, `Kurage's Oath (proto)`,
`Slack Water (proto)`** — confirmed by pile counts in fight 2 (hand r1 5 + hand r2 5 + draw 3 = 13
with no reshuffle, and the 3 unseen cards had to be Strike x2 + Amber).

Nibbit intent round 1: "Attack for 12".

**Predicted:** Slack Water (1) -> 4 + 2 = 6 and Weak; Pounce (2) -> 14; Defend free off Pounce -> 5
Block. Enemy to 25, Weak cuts 12 -> 9, I take 4.

**Happened:** exactly that. Nibbit 45 -> **25** (20 damage), the intent line **rewrote itself live to
"Attack for 9"** the moment Weak landed, and HP 62 -> **58**. The intent number honouring my own
debuff before I end the turn is the single most useful thing the combat screen does.

Round 2: Nibbit 25 HP, intent "Attack for 6" (its base attack varies turn to turn — 12, then 6 —
and no screen says by what rule).

**Predicted:** max damage this turn was Uproar 12 + a random draw-pile attack + Strike 6 = 24, one
short of the 25 needed, so I took the cheaper line — Uproar (18) + Defend (5 Block) — reasoning
that both lines end the fight on round 3 and this one costs 1 HP instead of 6.

**Happened:** Uproar dealt exactly **18** (25 -> 7); HP 58 -> **57**, exactly the predicted 1. This was
the one genuinely interesting decision of the fight and the arithmetic paid it off.

Round 3: Nibbit 7 HP with **Block 5** and an Empower intent. Strike x2 = 12 damage against 5 Block +
7 HP is exactly lethal; it was, on the nose.

**Result:** won round 3, HP **57/80**, 5 damage taken. Rewards: `12 Gold` and a card.

### Fight 2 reward

- `Treatise` — cost 1, power, "Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card."
- `Vanguard` — cost 0, skill, Plan: 1 Vulnerable + 1 Weak, Exhaust.
- `Change of Plans` — cost 1, skill, "The Bake-Kurage carries out your first Plan now. Exhaust."
- `Razor — Lightning Fang` — cost 1, skill, "For 2 turns, your Attacks apply Electro and deal 3
  additional damage. Exhaust."

Took **`Razor — Lightning Fang`**. Three of the four options are payoffs for a Plan engine I did not
have (one Plan card, `Kurage's Oath`, and a Plan mode on `Slack Water`); Razor pays out on the deck
I actually had, which is attacks.

---

## Event — Byrdonis Nest

> - **Eat the Egg** — Gain 7 Max HP.
> - **Take the Egg** — Add Byrdonis Egg to your Deck.

**The screen never printed what `Byrdonis Egg` does** — not a cost, not a type, not a line of text.
Choosing it would have been choosing a card by its name alone. Took **Eat the Egg**.

**Predicted:** +7 max HP, current HP unchanged at 57.
**Happened:** the next battle screen read **HP 64/87**. Max HP +7 *and* current HP +7. The event said
only "Gain 7 Max HP"; the 7 HP of healing was granted silently, and no screen between the event and
the battle printed an HP line at all.

---

## Fight 3 — Fuzzy Wurm Crawler (56 HP)

Round 1: HP 64/87, deck 14, enemy intent "Attack for 4".

**Predicted:** an enemy hitting for 4 is not worth blocking; Uproar (12 + a random draw-pile attack,
expected about 8 across Strike/Strike/Slack Water/Pounce) + Strike 6 = about 26.

**Happened: 20.** 56 -> 36. And the round-2 Bake-Kurage block explained why:

> The Bake-Kurage carried these out at the start of this turn, front first:
>   - Bake-Kurage: Slack Water (proto), 1

**Uproar's "Play a random Attack from your Draw Pile" pulled `Slack Water` and wrote it onto the
Bake-Kurage as a Plan instead of playing it at the enemy.** It dealt 0 damage on the turn Uproar was
played; at the start of round 2 the Kurage carried out Slack Water's *Plan* line ("Apply 1 Weak to
ALL enemies") and the Casket's 2 Hydro was the whole of the damage. Round 1 total was 12 + 6 = 18,
plus that 2 = the 20 I measured.

**In fight 1 the identical card, pulled by the identical Uproar, was played directly at the enemy**
for 4 damage + Hydro Aura 2 + Weak, immediately, and the Bake-Kurage read "Nothing is planned. The
morning is empty." on the very next screen. Same card, same source, two different behaviours. I
could not tell from any printed text which one is intended or what selects between them; this is the
sharpest contradiction I found.

Round 2: enemy 36 HP, intent "Empower (Buff)" — no damage incoming.

**Predicted:** Pounce (2) 14, then Amber free off Pounce, then Strike (1) 6 -> 20 now, enemy to 16,
Amber banked. Chose Amber over planning `Kurage's Oath` for exactly one reason I could price: Amber's
8 leaves the enemy at 8 next round versus Oath's 7 leaving it at 9, *and* Amber carries 3 mitigation.

**Happened:** 36 -> **16**, exactly 20. Amber resolved into a buff on me printed as:

> **Baron Bunny 1 (buff)** — The next time an enemy attacks you, take 3 less damage and deal 8 Pyro
> damage to ALL enemies.

The card is called `Amber — Explosive Puppet`; the buff it makes is called **Baron Bunny**. Nothing
on either screen connects the two names. I only knew they were the same thing because the buff text
is the card text word for word.

Round 3: enemy 16 HP with **Strength 7** and an intent of "Attack for 8". Pounce 14 + Strike 6 = 20
killed it before it swung. Fight 3 result: won round 3, HP **60/87**, 4 damage taken. Rewards:
`11 Gold` + card.

### Fight 3 reward

- `War Council` — cost 1, skill, Plan: "Deal 5 damage and apply 1 Weak to ALL enemies."
- `Battle Plan` — cost 1, skill, Plan: "Gain 1 Energy and draw 2 cards."
- `Salt Line (proto)` — cost 1, skill, "Gain 8 Block. Exhaust."
- `Sayu — Yoohoo Art: Fuuin Dash (proto)` — cost 1, attack, "Deal 8 damage to a random enemy and Swirl it."

Took **`War Council`**: with the Casket it is 5 + 2 = 7 to every enemy plus a 25% cut to every
enemy's attack, for 1 energy, and unlike the other three it does not exhaust.

---

## Fight 4 — three Inklets (15 / 14 / 13 HP)

The first fight that was actually a puzzle. Every Inklet carried:

> **Slippery 1 (buff)** — The next time Inklet loses HP, it only loses 1 HP instead.

Intents round 1: 3, "2 damage 3 times", 3 -> 12 incoming. My hand was Strike x2 and Defend x3 — no
AoE, and Slippery makes an AoE opener worthless (8 damage into a Slippery enemy is 1 damage).

**Predicted:** focus Inklet (2), the 2x3 one, because it is 6 damage per 14 HP where the others are
3 per 13-15. Strike pops Slippery for 1, Strike does 6, Defend takes the sting off: enemy to 7, I
take 12 - 5 = 7.
**Happened:** exactly. Inklet (2) 14 -> **7**, Slippery gone, HP 60 -> **53**.

Round 2 the two untouched Inklets went from 3 damage to **10 damage each** — 23 incoming against my
53 HP. Hand: Defend, Razor — Lightning Fang, Strike, Slack Water, Amber.

I could count the draw pile exactly here (5 in draw, 5 in discard, 15-card deck, and I knew every
card in all three zones), so I knew round 3's hand would be exactly Strike, Kurage's Oath, Uproar,
Pounce, War Council. That let me price the turn properly instead of guessing.

**Predicted:** Slack Water on Inklet (1) — 1 damage (Slippery caps it) + Weak + 2 Casket = 3, and
its 10 becomes 7 — then Amber, then Defend. I expected: Inklet (1) 15 -> 12 -> 4 after Amber's 8;
Inklet (2) 7 -> dead to Amber; Inklet (3) keeps Slippery so Amber's 8 becomes 1, leaving 12. Total
16 left, and I take about 12.

**Happened:** HP 53 -> **43** (10, close to the 12 I priced) and **two Inklets died, not one**. The
board came back as a single Inklet at **12/13** carrying `Pyro Aura 1`.

The extra kill is the Casket's Hydro plus Amber's Pyro. `Slack Water` is a [Hydro] card, so it left
Hydro on Inklet (1); Amber's 8 **Pyro** then hit a Hydro aura, and the glossary says "A hit of a
different element consumes the aura and triggers an Elemental Reaction". Inklet (1) was at 12 and
died to a printed 8. **The reaction is worth at least +4 damage on an 8-damage hit and no screen
anywhere printed the reaction's name, its number, or that it had happened** — I inferred it purely
from a corpse. That is the second sharpest thing I found.

Round 3: one Inklet, 12 HP, intent 3. Pounce (14) ended it.

**Result:** won round 3, HP **43/87**, 17 damage taken — the most expensive fight so far by a factor
of three, and the Slippery/AoE interaction is why.

### Fight 4 reward (`13 Gold` + card)

- `Battle Plan`; `Cleansing Wave` (1, "Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block.");
  `Salt Line (proto)`; `Razor — Claw and Thunder` [Electro] (1, "Deal 8 damage. If this is the third
  Attack you played this turn, gain 1 Energy.")

Took **`Razor — Claw and Thunder`**: 8 for 1 beats my Strike's 6 for 1 outright, and after watching a
Pyro-on-Hydro reaction kill something, an Electro applier next to a Hydro deck looked like the same
trick again.

---

## Treasure — An open chest

> **Oddly Smooth Stone** — Start each combat with 1 Dexterity.

Taken. It shows up in combat as `Dexterity 1 (buff) — Increases Block gained from cards by 1`, and
Defend's face changes from "Gain 5 Block" to "Gain 6 Block". The card face carrying the buffed
number is consistently the best thing these screens do.

---

## Elite 1 — Bygone Effigy (127 HP)

Entered at **43/87**. The Effigy opened "Sleeping (Sleep) — This enemy is doing nothing this turn"
and carried:

> **Slow 0 (debuff)** — Whenever you play a card, this enemy receives 10% more damage from Attacks
> this turn.

That one line is the whole fight: cheap cards first, biggest attack last, and the counter resets
every turn. Round 1 I got the ordering wrong and paid for it.

**Round 1, predicted:** `Razor — Lightning Fang` (1) then `Pounce` (2) then `Amber` free off Pounce.
I expected Pounce at 14 + 3 = 17 with a 10% or 20% Slow bonus, so 18 or 20.
**Happened:** 127 -> **109**, exactly **18**. So the multiplier a card gets is the Slow value
*before* that card's own increment: the first card played gets x1.00, the second x1.10, and so on.
The board afterwards read `Slow 30` for three cards played. Nothing on the screen states this, and
getting it backwards costs real damage — had I played Amber first and Pounce third, Pounce would
have been 17 x 1.2 = 20 instead of 18.

**Round 2** the screen produced the single most useful line of the run, on `Slack Water`:

> *Reaction preview: Electro-Charged* — This card supplies Hydro or Electro while an enemy has the
> other aura. The reacted enemy gains a 4-damage decaying damage-over-time effect.

That is a preview attached to the card *only when the board state makes it live*. It is the one
place the game explains a reaction before I commit to it.

**Predicted:** Slack Water first (7 with Lightning Fang, reacts with the Electro aura), then two
Strikes at 9 each so their Fang-applied Electro leaves an aura for Amber's Pyro to react with later:
7 x1.0 + 2 (Casket for Weak) + 9 x1.1 + 9 x1.2 = 7 + 2 + 9 + 10 = **28**.
**Happened: exactly 28**, 109 -> 81, and the reaction landed as `Poison 4 (debuff) — At the start of
its turn, loses 4 HP, then reduce Poison by 1.` The reaction preview calls it "a 4-damage decaying
damage-over-time effect"; the board calls it Poison. Two names, no cross-reference.

**Round 3** the Effigy woke with `Strength 10` and an intent of 20, and I was at 43 HP.

I spent the **Attack Potion** here — "Choose 1 of 3 random Attack cards to add into your Hand. It's
free to play this turn" — and it offered `Feint`, `Undertow (proto)` ("Deal 7 damage. If the enemy
has a debuff, deal 10 instead") and `Deep Current`. Took Undertow, which arrived in hand printed as

> **Undertow (proto)** [Hydro] — cost 0, attack ... The cost printed on this card is 1; it is
> showing 0 here.

That parenthetical is exactly the kind of thing I needed everywhere else and got only here.

**Predicted:** Defend, Defend (Slow to 20), Undertow at 10 x1.2 = 12, Razor Claw at 8 x1.3 = 10 —
**22 damage**, 12 Block, and 20 - 3 (Amber) - 12 = 5 damage to me.
**Happened: 26 damage** (77 -> 51), **Poison 3 -> 11**, and the enemy ended holding `Hydro Aura 2`
when I had expected Electro. The only reconstruction that fits every number is:

1. Undertow (Hydro) 12 damage, consumes Electro -> Electro-Charged -> Poison 3 -> 7; that Poison is a
   debuff I applied, so the **Tamakushi Casket fires for 2 Hydro damage, and that Hydro hit applies
   `Hydro Aura 2`**. Subtotal 14.
2. Razor Claw (Electro) 10 damage, consumes the *Casket's own* Hydro aura -> a second Electro-Charged
   -> Poison 7 -> 11; Casket fires again for 2, re-applying Hydro. Subtotal 12.

14 + 12 = 26, Poison 11, Hydro Aura 2 — all three match. So the Casket does not merely add chip
damage: **it re-arms the aura that the next off-element card reacts with, which makes a two-card
Hydro/Electro pair self-sustaining.** Nothing prints this. I only found it by having a number that
did not add up.

And the Casket appears to fire **at most once per card played**, not once per debuff: Slack Water in
round 2 applied both Weak and (via the reaction) Poison, and the total is only consistent with a
single 2-damage proc. Same relic, same fight, and the rule has to be inferred from two arithmetic
residuals.

**Round 3 enemy turn:** HP 43 -> **35**, and the enemy went 51 -> 28, i.e. 23 damage from
`Poison 11` + Amber's 8 Pyro. 11 + 8 = 19, so the Pyro landed for **12, not 8** — Pyro onto a Hydro
aura, x1.5. That is the same +50% that killed an Inklet in fight 4 for exactly 12, so I now have two
independent confirmations of a multiplier no screen ever names.

The 8 damage I took is the one number of the run I could not make add up. Intent printed 20, Baron
Bunny promises "take 3 less damage", Block was 12: 20 - 3 - 12 = 5, and I took 8. Either the -3 did
not apply, or the hit was 23 rather than the 20 the intent printed. **Two rounds later the same
buff visibly did apply** (intent 19, no Block, 19 - 3 = 16 taken, exactly). So the discrepancy is
in the elite's round-3 attack, not in Baron Bunny, and I could not tell which of the two from the
screen.

**Round 4:** enemy 28 HP, `Poison 10`, intent 23. I did not need to kill it — Poison 10 at the start
of its turn beats 28 - 24. Played Slack Water (4 + 2 Casket = 6), Strike (6), Undertow (10 x1.2 = 12)
for exactly the predicted **24**, taking it to 4, and Weak dropped its intent from 23 to 17 live on
the screen. Ended the turn; **Poison killed it at the start of its turn before it swung**, and I took
zero. Best decision of the run and it was made entirely off two printed numbers.

**Result:** elite down at HP **35/87**. Rewards: `41 Gold`, `Colorless Potion`, **Snecko Skull**
("Whenever you apply Poison, apply an additional 1 Poison"), and a card:

- `Vanguard`; `Salt Line (proto)`; `Sayu — Naptime (proto)` (0, "Gain 4 Block. Next turn, draw 2
  cards if you play no Attacks this turn."); and
- **`Sango Isshin (proto)`** [Hydro] — cost 2, attack, "Deal 8 damage. If the Bake-Kurage carried out
  a Plan this turn, deal **a quarter of your Max HP** to ALL enemies instead."

Took Sango Isshin. A quarter of 87 is 21 to every enemy for 2 energy, and I already hold three cards
that can leave a Plan on the Kurage. It is the first card I have seen that makes the Plan engine
worth building rather than a tax.

---

## Rest site 1

`HP 35/87`, "Rest — Heal for 30% of your Max HP (26)" or "Smith — Upgrade a card in your Deck."
Rested to **61/87**. At 35 HP with two elites and a boss left, an upgrade I could not name in advance
was not competitive with 26 HP I could.

## Treasure 2 — `Meal Ticket` ("Whenever you enter a shop room, heal 15 HP"). Taken; never used,
because no path I could reach afterwards contained a Shop.

---

## Elite 2 — Byrdonis (83 HP)

Entered at **61/87**. Intent 17, and:

> **Territorial 1 (buff)** — At the end of Byrdonis's turn, it gains 1 Strength.

A ramping enemy, so every turn spent blocking is a turn its damage grows. Snecko Skull was now live.

**Round 1 predicted:** plan `Kurage's Oath` (7 to all next turn is the best rate on the board at 1
energy), Strike 6, Defend 6 Block, taking 17 - 6 = 11.
**Happened:** exactly — HP 61 -> **50**, and at the start of round 2 the enemy read 70/83, i.e. the
6 from Strike plus the 7 from the plan. But it also read **`Hydro Aura 1`**, which nothing in my turn
should have applied: `Kurage's Oath` carries no element tag and its plan line is only "Deal 7 damage
to ALL enemies". **The Bake-Kurage's plan damage is Hydro and no screen says so.**

**Round 2 predicted:** play Strike, Strike, then `Razor — Claw and Thunder` third so its own clause
("If this is the third Attack you played this turn, gain 1 Energy") refunds the energy for a Defend:
6 + 6 + 8 + 2 Casket = 22 damage, 6 Block, take 12 - 6 = 6.
**Happened: exactly 22** (70 -> 48), the refund fired (Energy read 1/3 after three 1-cost cards),
HP 50 -> **44**, and Poison landed at **5** rather than 4 — Snecko Skull's extra stack, visible only
as a number one higher than the reaction preview promises. Hydro Aura 2 was back on the enemy
afterwards, confirming the Casket-re-arms-the-aura reading from the last fight.

That turn is the best-designed thing I met all act: a card whose text pays you for a play *order*,
where the ordering was independently forced by a different card's third-attack clause.

**Round 3:** enemy 43, Strength 2, intent 19. Pounce (14) -> Amber free off Pounce -> Strike (6) for
20, banking Baron Bunny onto a board that still had a Hydro aura.
**Predicted:** 20 now, then Poison 4 and a Vaporized Amber for 12 = 36 total, enemy to 7, and I take
19 - 3 = 16.
**Happened: exactly 36 and exactly 16.** 43 -> 7, HP 44 -> **28**. This is where Baron Bunny's -3
demonstrably applied.

**Round 4:** enemy 7 with Poison 3 (Poison alone would not have finished it). Strike 6 + Slack Water
(4 + 2) = 12, dead.

**Result:** elite 2 down at HP **28/87**, four rounds, 33 damage taken. Rewards: `36 Gold`,
`Strength Potion`, **`Anchor`**, and a card:

- `Moon's Reflection` (1, "Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out
  its Plan line, or plays it if it has none. Exhaust."); `Change of Plans`; `War Council`; and
- **`Kamisato Ayaka — Soumetsu`** — cost 2, skill, "For 2 turns, at the end of your turn deal 8 Cryo
  damage to ALL enemies. Then deal 16 Cryo damage to ALL enemies. Exhaust."

Took Ayaka: 8 + 8 + 16 = 32 AoE for 2 energy is the largest printed number I have been offered, and
Cryo is a fourth element to react with.

## Rest site 2

At 28/87. Rested to **54/87**.

---

## Fight 5 — Vine Shambler (61 HP)

Entered at 54/87 and, for the first time, with `Anchor` — "Start each combat with 10 Block" — which
the battle screen showed as `Block 10` on round 1 before I had played anything.

**Round 1 predicted:** Slack Water (4 + 2 Casket, applies Hydro), Strike (6), then
`Razor — Claw and Thunder` **as the third attack** so its own clause refunds 1 energy, its Electro
consuming Slack Water's Hydro for an Electro-Charged (8 + 2 Casket = 10), then spend the refunded
energy on `Razor — Lightning Fang`. Total 22 damage + Poison 5, and 12 - 10 Block = 2 to me, or 0 if
Slack Water's Weak lands first (12 becomes 9).
**Happened:** exactly 22 from cards, Poison 5, and at the start of round 2 the enemy read 34/61 —
22 + 5 poison + ... 61 - 34 = 27 = 22 + 5. HP stayed **54**: zero damage, because Weak took the hit
to 9 and Anchor's 10 Block ate all of it.

**Round 2:** played `Kamisato Ayaka — Soumetsu` (2) and a Defend.

**Round 3 opened with three things I could not account for:**

1. The enemy had gone 34 -> **20**, i.e. 14, where the printed parts are 8 Cryo + 4 Poison = 12. The
   extra 2 is exactly one Casket proc, which means the Cryo produced a debuff off a reaction; the
   board shows `Hydro Aura 1` on the enemy, consistent with the Casket's Hydro hit again.
2. **I took 0 from a printed 8-damage intent while holding only 6 Block.** HP read 54 before and
   54 after. 8 - 6 = 2 and I lost none of it. No screen said why.
3. I was handed `Tangled 1 (debuff) — Attacks cost an additional [Energy] this turn`, and every
   attack in hand correctly re-priced itself: Strike printed "cost 2", Uproar printed "cost 3", each
   with an `*Entangled*` note. That re-pricing is excellent; the debuff arriving with no line saying
   which enemy action produced it is not.

Soumetsu's own buff line is the clearest text in the game: `Soumetsu 1 (buff) — At the end of your
turn, deal 8 Cryo damage to ALL enemies, then 16 when it ends. Lasts for 1 turn.` I ended round 3 on
20 enemy HP knowing 8 + 16 = 24 was coming, played one Defend for insurance and passed. It died at
the end of my own turn without swinging. **Whole fight: 0 damage taken.**

Reward: `19 Gold`, `Vulnerable Potion`, and a card (`Coral Bulwark`, `War Council`, `Vanguard`,
`Noelle — Breastplate`). Took **`Vanguard`** — 0 cost, and its plan line (1 Vulnerable + 1 Weak)
both amplifies and, crucially, *is a Plan carried out*, which is the switch `Sango Isshin` needs.

---

## Elite 3 — Phrog Parasite (62 HP) and what it leaves behind

> **Infested 4 (buff)** — Upon dying, summons... something.

That is the actual printed text. Round 1 intent: "Strategic (StatusCard) — the number on its icon is
3 — This enemy intends to give you 3 Status cards."

**Round 1 predicted:** Pounce (14) -> `War Council` free off Pounce's "next Skill costs 0" and
written onto the Kurage as a Plan -> Slack Water (4 + 2). 20 now, 7 at the start of round 2.
**Happened:** exactly. 62 -> 35 across the two, and the free-skill discount **does** apply to a card
played onto the Bake-Kurage, which the screen nowhere promises.

The 3 Status cards went into my piles silently: the only evidence they existed is that hand + draw +
discard came to 22 against a 19-card deck. **No screen named them, printed their faces, or said
where they went.** I never once saw one in hand, so I cannot say what they do.

**Round 2** was the run's best turn and the only one that felt built rather than found. War Council's
plan had resolved, which switches `Sango Isshin` from "Deal 8" to "deal a quarter of your Max HP to
ALL enemies". Max HP 87.
**Predicted:** Razor Claw (8, Electro into the standing Hydro aura -> Electro-Charged -> Poison 4 + 1
Snecko = 5, + 2 Casket = 10), then Sango for 21. 31 total, leaving 4, with Poison 5 to finish it at
the start of its turn before it could attack.
**Happened: exactly 31** (35 -> 4), Poison exactly 5, and it died to Poison having never landed a
blow. **Zero damage taken in the fight.**

Then `Infested` paid out: **four Wrigglers, 17/21/19/20 HP, all `Stunned`.**

**Round 3 predicted:** Ayaka (2) + `Kurage's Oath` written as a Plan (1). End of turn: 8 Cryo to all
-> 9/13/11/12. Start of round 4: the Oath plan's 7 to all -> 2/6/4/5.
**Happened:** 4 dead / **4, 2, 3** — one more Wriggler dead and every survivor 2 lower than I
predicted, all four (three) carrying `Frozen 1` and `Hydro Aura 1`. The chain that fits every number:
Ayaka's Cryo leaves a **Cryo aura**; the Kurage's plan damage is **Hydro** (see elite 2); Hydro into
Cryo is the **Frozen** reaction; Frozen is a debuff, so the **Casket fires for 2 more Hydro each**,
which re-applies the Hydro aura you can see on the board. 7 + 2 = 9 per enemy, and 17 - 8 - 9 = 0.

Frozen prints properly when it lands: `Frozen 1 (debuff) — This creature's next action deals 50% less
damage. The first Attack that hits it Shatters for unblockable damage and removes Frozen.` What is
never printed is that my own deck can produce it, or that a relic that reads like chip damage is the
thing gluing the chain together.

Round 4: passed, and Soumetsu's 8 + 16 = 24 at end of turn killed all three. **Elite 3: 0 damage
taken.**

Rewards: `42 Gold`, `Amethyst Aubergine`, a card, and a `Power Potion` I could not take — I chose it
and the reward screen simply re-listed it, with no line saying the belt was full. Took **`Battle
Plan`** (1, Plan: gain 1 Energy and draw 2) as a second cheap switch for Sango.

---

## Event — The Future of Potions?

> - **Insert Common Potion** — Lose Colorless Potion. Obtain an Upgraded Common Attack.
> - **Insert Common Potion** — Lose Strength Potion. Obtain an Upgraded Common Attack.
> - **Insert Common Potion** — Lose Vulnerable Potion. Obtain an Upgraded Common Skill.

**There is no way to decline.** All three options spend a potion, and no "leave" line is printed.
Worse for a text bridge: **all three options have the same title**, so `choose "Insert Common
Potion"` is ambiguous by construction; it resolved to index 0 (the Colorless Potion), which happened
to be the one I wanted to spend, but I had no way to *aim* at the second or third. That is a real
defect in the screen, not in the tool: the tool prints exactly what the option is called.

Reward: `Undertow (proto)+`, `Feint+`, `Deep Current+`. Took **`Undertow (proto)+`** — "Deal 10
damage. If the enemy has a debuff, deal 13 instead" for 1 energy is the best single-target rate I was
ever shown, and my own deck guarantees the debuff.

## Rest site 3

At 54/87 before the boss. Rested.

---

## Boss — Ceremonial Beast (252 HP)

Entered at **80/87** with seven relics, `Strength Potion` and `Vulnerable Potion`, and a 21-card deck.

Round 1 intent: Empower — a free turn. Used it entirely on setup:

- `Strength Potion` ("Gain 2 Strength") first, so everything after it counts.
- `Vanguard` (0) written onto the Kurage, then `Battle Plan` (1) written onto the Kurage as well.
  **Two plans stack**, and the screen said so cleanly: `Plan 2 (buff) — Carries out 2 Plans at the
  start of your next turn, in order`, with the Kurage block listing them 1. Vanguard 2. Battle Plan.
- Strike, which now printed "Deal 8 damage" — Strength folded into the face.

**Predicted:** 8 from Strike this turn, then at the start of round 2 Vulnerable + Weak land, I get
+1 energy and 2 cards, and Sango becomes live.
**Happened:** 252 -> 238 by the start of round 2 — 8 from Strike, and **6 from the plan**, where
Vanguard applies two debuffs and the Casket's proc is 2. 6 = two procs of 2 amplified by the
Vulnerable that the same plan had just applied (2 x 1.5 = 3, twice). Energy read **4/3**.

The boss also revealed its one rule: `Plow 150 (debuff) — The first time Ceremonial Beast's HP
reaches 150 or below, it becomes Stunned and loses all its Strength.` That is a clearly printed,
plannable threshold and it is the best-designed thing on the boss.

**Round 2 predicted:** Razor — Lightning Fang, then `Undertow+` at (13 + 2 Strength + 3 Fang) x 1.5
Vulnerable = 27, then Amber banked, then `Kurage's Oath` planned. 30 with a Casket proc.
**Happened: exactly 30** (238 -> 208), and `Poison 5` appeared, which means Lightning Fang's applied
Electro **did** react against the standing Hydro aura even though the card played was itself Hydro.
That contradicts what I had concluded two fights earlier, where three Fang-boosted Strikes into a
Hydro board produced no reaction at all. I cannot reconcile those two turns.

**Round 3 predicted:** the enemy turn should cost the boss Poison 5 + a Vaporized Amber (8 x 1.5 =
12) + the Oath plan's 7 = 24, and cost me 11 - 3 = 8.
**Happened:** the boss lost **36**, twelve more than I can account for, and I took the **full 11**
with Baron Bunny's -3 apparently not applying — the mirror image of the elite-2 turn where it did.
These are the two places in the run where the printed numbers and the observed numbers disagree in
opposite directions, and neither screen offers a reason.

Round 3 was the payoff turn. Hand was Strike (11), Strike (11), Slack Water (9), War Council, Sango.
The Kurage had carried out a Plan, so Sango was live at 21 — but 3 Strikes-worth of attacks with
`Lightning Fang` still up was worth more, and **the Plow threshold at 150 made the target number
explicit**: 172 - 150 = 22 to cross it.
**Predicted:** about 35 and a crossed threshold. **Happened: 39** (172 -> **133**), `Plow` fired —
intent flipped to `Stunned` and Strength vanished from its list — and **Poison went 4 -> 19**,
because all three attacks carried Fang's Electro into the Hydro aura and each Electro-Charged is
4 + 1 (Snecko Skull) = 5.

That 19-stack decided the fight. The next three enemy turns took 19, 22 and 21 off the boss for free.

Round 4: boss stunned, no damage to me, board at 114. Played `Uproar` (8 twice) whose random
draw-pile attack was a Strike (this time it was **played**, not planned), then `Razor — Claw and
Thunder` as the **third** attack for its energy refund, then Strike with the refund.
**Predicted** about 36 and one more reaction. **Happened: exactly 36** (114 -> 78) and Poison 18 ->
23.

Round 5 opened with `Ringing 1 (debuff) — You can only play 1 card this turn`, and **every card in
hand re-printed itself with a `Ringing.` clause appended to its text**. That is the single best piece
of UI in the run: a global restriction written onto each individual card face. One card only, so I
played `Slack Water` for the Weak, taking the boss's 15 down to the 11 I actually took.

Round 6: boss at 17 with Poison 21 — it would have died to Poison at the start of its turn anyway,
but Strike (8) + Sango (8 + 2 Strength = 10) = 18 killed it outright on my own turn.

**Boss result: won on round 6 at HP 58/87, 22 damage taken across the whole fight.** Rewards:
`100 Gold`, a second `15 Gold` line (Amethyst Aubergine's "Enemies drop 15 additional Gold" printed
as its own reward row), and a card from `The Clouds Like Waves Rippling`, `Nereid's Ascension
(proto)`, `Sango Isshin (proto)`, `Kamisato Ayaka — Soumetsu`. Took a **second Ayaka**: 32 AoE for
2 energy, unconditional, versus a second Sango that needs a Plan resolved on the same turn.

Proceeded to the **act-2 map**, whose boss is named **The Insatiable**. Stopped there.

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

Four, and they are all the same shape — a printed number against a printed number.

1. **Fight 2, round 2.** "Uproar 12 + a random attack + Strike 6 = 24 against 25 HP" is one damage
   short of lethal, so the choice was *lose 6 HP for nothing* or *take the safe line*. I played
   Uproar + Defend and took 1 damage instead of 6, and the fight still ended on the same round. The
   trade was legible entirely because the enemy's HP and my card faces were both exact.
2. **Fight 4, round 2, against Slippery.** `Slippery 1 — The next time Inklet loses HP, it only
   loses 1 HP instead` inverts normal AoE logic: my 8-damage Amber was worth 1 into an untouched
   Inklet and 8 into a popped one. The choice was which single Slippery to pop with a 1-damage
   Slack Water so that the banked AoE landed properly. That is a genuine puzzle and it is the only
   fight in the act where the right play was not "biggest number".
3. **Elite 1, round 4.** `Poison 10` versus 28 HP: I could try to kill and fail, or deal 24 and let
   Poison finish at the start of its turn — which also meant it never swung. Trading 4 damage for a
   whole 23-damage attack is the best decision I made, and both halves of it were printed.
4. **Boss, round 3.** `Plow 150` turned "how much damage this turn" into an exact target of 22, and
   `Lightning Fang` expiring that turn made it a now-or-never. Threshold + expiring buff is the one
   moment the boss made me plan two resources against a deadline.

### (b) What felt automatic, and what never seemed worth playing

**Automatic:** every turn where the hand was Strikes and Defends. With 4 Strikes and 4 Defends in a
10-card starter, roughly a third of my turns had no decision in them — count the incoming number,
buy exactly enough Block with Defends, point the rest at the enemy. Fight 3 round 3 (`Pounce` +
`Strike` = 20 into a 16 HP enemy) took no thought at all.

**Never worth playing:** `Defend` against an `Empower` or `Debuff` intent, which the screen tells
you in advance — so on those turns one to three cards in my hand are dead, and the game knows it and
tells me it knows it. Also **`Kurage's Oath` as a *card*** rather than as a plan: it has no
non-Plan mode, so it is either 1 energy for 7 damage next turn or a brick.

The single least-used thing was the **Bake-Kurage's general "play any card on it" affordance**. Every
screen advertises `play "<card>" on "Bake-Kurage"`, but only cards that print a `Plan:` line are worth
putting there, and I never once found a reason to bank a normal card for later. The affordance is
advertised far more prominently than it is useful.

### (c) What I could not understand, or that contradicted its own printed text

- **`Uproar`'s random attack was planned once and played twice.** In fight 1 it pulled `Slack Water`
  and hit the enemy immediately (4 damage, Hydro, Weak). In fight 3 it pulled `Slack Water` and the
  next screen said `Bake-Kurage: Slack Water (proto), 1` — it had been written onto the Kurage as a
  Plan instead, losing its damage and delaying its Weak a full turn. In the boss fight it pulled a
  Strike and played it. Uproar's text says "Play a random Attack", not "Plan".
- **Shrink did not reduce plan damage.** `Shrink -1 — While Shrinker Beetle is alive, your Attacks
  deal 30% less damage` visibly rewrote Strike from 6 to 4, and in the same turn `Kurage's Oath`'s
  plan dealt its printed 7 in full.
- **Lightning Fang's Electro reacts, except when it doesn't.** Elite 1 round 2: two Fang-boosted
  Strikes into a Hydro-aura'd enemy, one reaction total and the totals only reconcile if the Strikes
  did not react. Boss round 3: three Fang-boosted attacks, three reactions (`Poison 4 -> 19`).
- **Baron Bunny's "take 3 less damage" applied once and not twice.** Byrdonis: intent 19, no Block,
  16 taken. Boss round 3: intent 11, no Block, 11 taken.
- **The Casket's proc rate.** The elite-1 round-2 numbers only work if it fires once per card even
  when two debuffs land; the boss round-1 numbers only work if it fires twice for one plan's two
  debuffs; and on the boss round 5 a `Slack Water` that applied Weak produced no proc at all
  (47 - 8 - 22 = 17, exactly what the board showed, with no room for a 2).
- **A printed 8-damage intent that cost me 0** through 6 Block, in fight 5 round 3.
- **`Amethyst Aubergine`** — "Enemies drop 15 additional Gold" — printed as a *separate reward row*
  ("15 Gold") rather than folding into the fight's gold, which reads like two gold rewards.
- **`Infested 4 (buff) — Upon dying, summons... something.`** The ellipsis is literal. I had to kill
  it to learn it was four Wrigglers totalling 77 HP.
- **The event card I was asked to choose sight unseen.** Byrdonis Nest offered "Add Byrdonis Egg to
  your Deck" with no cost, type, or text anywhere on the screen.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: `Defend`.** Not because 5–6 Block is bad, but because the intent line tells me in
advance whether it does anything, and on roughly half the turns of this act it did nothing. Four
copies in a 10-card starter is four cards that the screen itself can tell me are blank.

**Happiest to draw: `Razor — Claw and Thunder`.** Eight damage for 1 energy is already above my
deck's rate, but the reason is its second clause — "If this is the third Attack you played this
turn, gain 1 Energy" — which turns a hand of Strikes into an ordering puzzle with a real payoff, and
it is simultaneously my Electro applier, so it is the card that starts the Poison chain. It is the
only card in the deck that rewards *how* I play the turn rather than *what* I play.

Honourable mention to **`Sango Isshin (proto)`**: "a quarter of your Max HP to ALL enemies" is the
only card that made the Plan machinery worth building around, and the turn where War Council's plan
resolved and Sango hit for 21 was the one turn that felt authored rather than arithmetic.

### (e) Did the first turn of the first fight already present a decision?

**Yes, a real one.** Hand: Defend, Strike, Pounce, Uproar, Strike; 3 energy; enemy intent
"Strategic (DebuffStrong)". The intent being a debuff immediately kills Defend, so the turn is
`Pounce` (14 flat plus a free Skill) against `Uproar` (12 plus an unknown attack out of a 7-card
draw pile) — a known quantity against a gamble on my own deck's composition. It was decidable and it
mattered: Uproar came in at 18, four more than Pounce.

What the turn did **not** present was any use of the Bake-Kurage, which the screen spends the most
space explaining. My opening hand contained no card with a `Plan:` line, so the mechanic the game
leads with was unusable on the turn it was introduced.

### (f) Anything a screen granted or changed without saying so

- **Byrdonis Nest's "Gain 7 Max HP" also healed 7.** 57/80 before, 64/87 in the next fight.
- **The Bake-Kurage's plan damage is Hydro.** `Kurage's Oath` has no element tag and its plan is
  "Deal 7 damage to ALL enemies", yet the enemy came out of it wearing `Hydro Aura 1` (elite 2,
  round 2), and against the Wrigglers the Oath plan produced a **Frozen** reaction off Ayaka's Cryo.
- **The Tamakushi Casket's 2 Hydro damage applies a Hydro aura**, which is what makes a Hydro card
  followed by an Electro card chain into a second reaction. The relic reads as chip damage.
- **Elemental reaction multipliers are never printed.** Pyro into Hydro is x1.5: Amber's printed 8
  killed an Inklet sitting on exactly 12, and later took the Effigy for 12 in a turn whose other
  components were exactly known.
- **Snecko Skull's extra Poison** shows only as a stack one higher than the reaction preview promises.
- **The Phrog Parasite put 3 Status cards into my piles** and no screen named them, printed them, or
  told me where they went; the only trace was hand + draw + discard = 22 against a 19-card deck.
- **A reward I selected was silently not granted.** I chose the `Power Potion` off elite 3's reward
  screen, the call returned ok, and the screen simply re-listed it. My belt was full and nothing said
  so.
- **`Kurage's Oath` played onto the Kurage still got Pounce's "next Skill costs 0" discount** — the
  discount applies to planning, which no screen states.

---

## Findings, ranked by sharpness

1. **`Uproar`'s "Play a random Attack from your Draw Pile" sometimes writes that attack onto the
   Bake-Kurage as a Plan instead of playing it.** Fight 3, round 2 screen, verbatim: "The Bake-Kurage
   carried these out at the start of this turn, front first: / Bake-Kurage: Slack Water (proto), 1".
   Round-1 damage was 20 (12 Uproar + 6 Strike + 2 from the plan's Casket proc at the start of round
   2) where the same Uproar in fight 1 produced 18 on the turn it was played (12 + 4 + 2) with the
   Kurage reading "Nothing is planned. The morning is empty." Cost: the pulled card's damage is lost
   and its debuff is delayed a full turn.

2. **Plan damage ignores a debuff that visibly reduces card damage.** Fight 1, round 3: `Shrink -1`
   rewrote every Strike in hand from "Deal 6" to "Deal 4", and in the same turn the Kurage line read
   `Bake-Kurage: Kurage's Oath (proto), 7` and the enemy went 14 -> 3, i.e. 4 from the reduced Strike
   plus the **full** 7 from the plan.

3. **The elemental reaction chain is entirely unprinted and it is the strongest thing in the deck.**
   Boss round 3: three attacks under `Lightning Fang` took `Poison 4 -> 19`, and the boss then lost
   19, 22 and 21 HP over three consecutive enemy turns without my spending a card. The visible parts
   are a per-card "Reaction preview" line and a `Poison n` counter; the invisible parts are that
   Electro-Charged adds 4 (+1 from Snecko Skull), that the Tamakushi Casket's 2 Hydro re-applies the
   Hydro aura the next Electro card needs, and that Pyro-into-Hydro is x1.5.

4. **`Lightning Fang`'s applied Electro reacts inconsistently.** Elite 1 round 2, three attacks into
   a Hydro board, exactly one reaction (`Poison 4`) and a total of 28 that only reconciles with the
   two Strikes not reacting. Boss round 3, three attacks into a Hydro board, three reactions
   (`Poison 4 -> 19`). Same buff, same aura, opposite behaviour.

5. **`Baron Bunny`'s damage reduction fires inconsistently.** Byrdonis round 3: intent 19, 0 Block,
   HP 44 -> 28, i.e. 16 = 19 - 3. Boss round 3: intent 11, 0 Block, HP 80 -> 69, i.e. the full 11.
   Same buff line printed on both screens.

6. **The Tamakushi Casket's proc rule cannot be pinned down from three fights of arithmetic.** Boss
   round 1 needs two procs for one plan's two debuffs (6 damage). Elite 1 round 2 needs one proc for
   a card that applied two debuffs (28 total). Boss round 5 needs zero procs for a card that applied
   Weak (47 - 8 - 22 = 17 exactly). The relic is load-bearing and its rule is not printed.

7. **The event `The Future of Potions?` prints three options with identical titles and no way to
   decline.** All three read "Insert Common Potion"; they differ only in the description line. On a
   text bridge only the first is reachable by name, and there is no "leave" option, so a player who
   wants to keep all three potions cannot.

8. **A boss/elite reward can be selected and silently not granted.** Elite 3: `choose "Power Potion"`
   returned ok, and the reward screen re-listed `Power Potion` unchanged. Nothing said the belt was
   full.

9. **Events grant more than they promise.** "Gain 7 Max HP" gave 7 max HP **and** 7 current HP
   (57/80 -> 64/87), and no screen between the event and the next battle printed an HP line at all.

10. **The 16-floor act-1 map with 3 elites and 4 rest sites is very forgiving of a slow deck.** I
    fought only 5 normal fights and 3 elites in 16 floors, rested three times for 78 HP total, and
    reached the boss at 80/87 with 7 relics. **I could not tell** whether that is the intended
    pacing or an artefact of the routes this map offered; my path was frequently forced (five map
    screens presented exactly one node).

11. **Things that are done well, for contrast, since they are the parts a rewrite should not break:**
    card faces re-print the post-modifier number (Strike shows "Deal 4 damage" under Shrink, "Deal 11
    damage" under Strength + Lightning Fang, "cost 2" under Tangled, and a `Ringing.` clause appended
    under Ringing); intent numbers update live the moment Weak lands (23 -> 17 in front of me);
    `Undertow` handed to me by a potion printed "The cost printed on this card is 1; it is showing 0
    here"; and `Plow 150` states its threshold as a number I can aim at.

**Where I could not tell:** whether the Bake-Kurage is a good mechanic. Across eight fights I wrote
nine Plans, and seven of them were `Kurage's Oath`/`War Council`/`Vanguard`/`Battle Plan` played onto
it because their text says to — not because I chose between planning them and playing them. The only
turn where the Kurage was a *decision* was the boss's round 1, where stacking two plans set up
Sango. One decision in eight fights is not enough evidence for me to say the mechanic is thin rather
than merely under-supplied by the cards I happened to be offered.

---

## Non-blindness declaration

- **Commands outside the two allowed ones: none.** Every game action was
  `GITS_LANE=1 python -m understudy.blindplay observe` or
  `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, run from the repo root.
- **Other shell usage:** `cat`/`sed`/`grep`/`head` only, in two roles — trimming `observe` output for
  readability, and appending my own record file from scratch fragments under
  `C:\Users\Monty\AppData\Local\Temp\claude\...\scratchpad\`. One `wc -l` on my own record file.
- **Tools used:** Bash (for the two blindplay commands and the record-file plumbing) and Write (for
  this record and for the four scratchpad fragments that were concatenated into it). No Read, no
  Grep, no Glob, no Agent, no skill, no git.
- **Repo files read: none.** No source, no YAML, no docs, no rulings, no backlog, no logs. Everything
  in this record comes from what `observe` and `act` printed.
- **The only repo file written is this record**,
  `review/qa/kokomi-round-4d-2026-09-03/opus-act1.md`.
- **Lane:** lane 1 only. Lane 2 was never touched. The game was never launched, closed, restarted or
  torn down. **The lane is left standing on the act-2 map screen**, at the first node choice
  (`Ancient (path 1)`), HP 58/87, with the act-2 boss named as **The Insatiable**.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
