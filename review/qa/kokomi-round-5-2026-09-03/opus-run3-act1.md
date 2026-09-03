# KLEEMOD-KOKOMI — blind seat, lane 1, run 3, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 5, run 3, first of three chained seats.
- **Lane:** 1.
- **Character:** KLEEMOD-KOKOMI.
- **Run seed:** *(no screen printed a seed — see final Identity block)*
- **Act:** 1. The map screen names the top of the act: **Vantom**.
- **Actions accepted / refused:** 223 accepted, 1 refused.
- **Termination reason:** stop condition (1) — act-1 boss resolved and its reward screen handled.
- **Where the run stands:** the act-2 map screen, boss named **The Insatiable**.

*Full details — HP trajectory, gold, potions, relics and the reconstructed deck — are in the **Identity (completed)** section at the end of this document. The running log below is written as it happens.*

---

## Running log

### Neow (floor 0)

Screen printed three options:

- **Winged Boots** — "You may ignore paths when choosing the next rooms to travel to 3 times."
- **Stone Humidifier** — "Whenever you Rest at a Rest Site, raise your Max HP by 5."
- **Silken Tress** — "Lose all Gold. Enchant all cards in your first card reward with Glam."

**Prediction / reasoning.** Blind, "Glam" is an unknown enchant keyword and the cost is *all* gold, which is the run's only shop currency; the payoff is at most one enchanted card, because you take one card from a reward. Winged Boots is routing freedom with no stat behind it. Stone Humidifier is a permanent max-HP escalator, and max HP is the resource that decides whether you survive an act-1 boss.

**Took:** Stone Humidifier. The tool echoed `Took: Stone Humidifier — Whenever you Rest at a Rest Site, raise your Max HP by 5.`

Note: the screen never printed my HP, max HP, gold or starting relics at this point — Neow is a bare option list.

### Map (act 1)

```
- 1 floor ahead: Monster, Monster
- 2 floors ahead: Monster, Monster, Monster
- 3 floors ahead: Monster, Unknown, Monster, Monster
- 4 floors ahead: Unknown, Monster, Monster, Shop, Unknown
- 5 floors ahead: Monster, Unknown, Monster, Unknown
- 6 floors ahead: Elite, Monster, Unknown, Monster
- 7 floors ahead: RestSite, Monster, RestSite, Elite
- 8 floors ahead: Monster, RestSite, Monster, Monster
- 9 floors ahead: Treasure, Treasure, Treasure, Treasure, Treasure
- 10 floors ahead: Shop, Monster, RestSite, Monster
- 11 floors ahead: Unknown, Elite, Unknown, Elite, Unknown
- 12 floors ahead: RestSite, RestSite, Shop, RestSite, Monster, Unknown
- 13 floors ahead: Unknown, Monster, Monster, Elite, Elite, Monster
- 14 floors ahead: Monster, Elite, Unknown, Monster, Elite
- 15 floors ahead: RestSite, RestSite, RestSite, RestSite
- 16 floors ahead: Boss
```

At the top of this act: **Vantom**. Sixteen floors before the boss — a long act.

Two openings: "Monster (path 1)" leading on to one Monster, "Monster (path 2)" leading on to two. Took path 2 to keep both branches live. **The map page prints no HP and no node-by-node route**, only per-floor room counts, so routing has to be done from the floor list plus my own HP reading carried out of the last fight.

### Fight 1 — Shrinker Beetle (40 HP), floor 1

Opening screen: **HP 64/80**, Energy 3/3, draw pile 5 (so a 10-card deck). Relics printed:

- **Tamakushi Casket** — "Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy."
- **Stone Humidifier** — "Whenever you Rest at a Rest Site, raise your Max HP by 5."

The Bake-Kurage panel: "The Bake-Kurage is on the field for the whole fight. Enemies cannot touch it. Play a card on it to write its **Plan** line instead of playing the card now. / Nothing is planned. The morning is empty."

Starting hand: Kurage's Oath, Defend, Slack Water, Strike, Strike.

- **Kurage's Oath** — cost 1, skill. "Play on the Bake-Kurage. Plan: Deal 7 damage to ALL enemies."
- **Slack Water** [Hydro] — cost 1, attack. "Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies."
- **Strike** — cost 1, attack. "Deal 6 damage."
- **Defend** — cost 1, skill. "Gain 5 Block."

**Turn 1.** Intent: `Strategic (DebuffStrong) — This enemy intends to apply a Debuff to you.` No damage number, so Block is dead this turn and every point of energy should buy damage.

Priced the three cards I could afford:
- Strike = 6.
- Slack Water = 4 + 2 (the Casket fires on the Weak) = **6**, and it throws in a Weak and a Hydro aura free.
- Kurage's Oath = 7, but next turn.

So Slack Water ties Strike on damage and strictly beats it on riders. Played **Oath → Bake-Kurage**, **Slack Water**, **Strike**.

*Predicted 12 this turn. Got 12:* 40 → **28**. Enemy left with `Hydro Aura 2` and `Weak 1`.

**Turn 2.** Two things landed at once.

1. The Plan resolved and the screen logged it: `Bake-Kurage: Kurage's Oath, 7`. 28 → **21**, exactly 7.
2. The enemy's turn-1 debuff was `Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks deal 30% less damage.` My Strike's printed face changed from "Deal 6 damage" to **"Deal 4 damage"** (6 × 0.7 = 4.2 → 4).

**This is the sharpest mechanical finding of the fight: the Plan dealt its full 7 while Shrink -1 was already active.** Shrink was applied on the enemy's turn 1, so it was live when the Bake-Kurage carried out the Oath at the start of my turn 2, and the log still printed `7`, not 4. The Bake-Kurage's Plan damage is not "your Attack" for the purposes of a percentage attack-reduction debuff.

Hand was Defend ×3, Strike ×2 — no Plan card available. Intent `Attack for 7`. Played Strike, Strike, Defend. *Predicted 8 damage and 7−5 = 2 taken. Got both:* 21 → **13**, HP 64 → **62**.

**Turn 3.** Enemy at 13 HP, intent escalated to `Attack for 13`. I checked whether I could kill: absolute maximum with 3 energy was Strike 4 + Strike 4 + Slack Water (2 + 2 Casket) = **12** — one short of lethal. The screen shows Slack Water's face had also shrunk, "Deal 2 damage".

Since the kill was out of reach, the right line was to reduce the incoming hit rather than chase it. Played **Slack Water** (Weak), **Strike**, **Defend**.

*Predicted: 8 damage dealt; incoming 13 × 0.75 = 9.75 → 9; minus 5 Block = 4 taken.* Got exactly that: 13 → **5**, HP 62 → **58**.

**Turn 4.** Enemy at 5, intent back down to `Attack for 7` (its pattern over the fight was DebuffStrong → 7 → 13 → 7). Strike + Strike = 8 ≥ 5. Dead.

**Fight 1 result: won on turn 4, HP 58/80, no potion spent.**

**Reward screen:** `10 Gold`, `Gambler's Brew`, `Add a card to your deck.` Took all three.

Card offer:

- **Salt Line** — cost 1, skill. "Gain 8 Block. Exhaust."
- **Ambush** — cost 1, skill. "Play on the Bake-Kurage. Plan: Deal 12 damage."
- **Rally** — cost 1, skill. "Apply 1 Weak. The next Companion card you play this turn costs 1 less."
- **Shinobu — Grass Ring of Sanctification** — cost 0, skill. "Gain 4 Block. If you lost HP this turn, gain 4 additional Block."

**Took Ambush.** Reasoning at the time: 12 damage for 1 energy is double a Strike, my whole problem in fight 1 was that the fight ran four turns and the enemy's intent escalated while I chipped, and I had just watched Plan damage ignore a 30% attack-reduction debuff. Rally's second clause names **Companion**, a keyword no card in my deck carries and which no glossary on the screen defined — dead text to me. Shinobu is the card I would most want to revisit; a 0-cost Block card is real, and it is probably the "Companion" Rally is talking about, but nothing on the screen said so.

### Map, after fight 1

Both openings printed "Monster (path 1) → Monster" and "Monster (path 2) → Monster" — **identical text, nothing to choose between them.** Took path 1.

### Fight 2 — Fuzzy Wurm Crawler (55 HP), floor 2

Opened HP 58/80, draw pile 6 (deck now 11 with Ambush). Potions: `1 of 3 slots are full` — `Gambler's Brew — Discard any number of cards, then draw that many.` (Note the reward screen printed only the bare name "Gambler's Brew"; the potion's actual text appeared for the first time on the combat screen.)

**Turn 1.** 55 HP, intent `Attack for 4`. Big pool, small hit — so racing beats blocking: every extra enemy turn costs ~4 HP, and 1 energy of Defend saves 4 while 1 energy of attack removes 6.

Played **Ambush → Bake-Kurage**, **Strike**, **Slack Water**. *Predicted 12 now (6 + 4 + 2 Casket), 12 next turn, and the Weak turning the 4 into 3.*

Got all of it: 55 → **43**, HP 58 → **55** (took 3, not 4).

**Turn 2.** Log: `Bake-Kurage: Ambush, 12`. 43 → **31**. Ambush paid its printed 12 for 1 energy.

Intent `Empower (Buff)` — no damage number again, so Block dead again. Played **Kurage's Oath → Bake-Kurage**, **Strike**, **Strike**. *Predicted 12 now, 31 → 19; then 7 at the start of turn 3, → 12.*

**Turn 3.** Confirmed: enemy at **12/55**. The buff had resolved into `Strength 7 (buff) — Increases attack damage by 7`, and the intent read `Attack for 11` (4 base + 7 Strength).

12 HP against my hand of Strike 6, Slack Water 4, Defend ×3. Strike 6 + Slack Water (4 + 2 Casket) = **exactly 12**. Played Slack Water then Strike; the fight ended on the second card. The Strength-7 hit never landed.

**Fight 2 result: won on turn 3, HP 55/80, took 3 damage total, no potion spent.**

**Reward:** `12 Gold`, `Skill Potion`, card. Took all.

Card offer:

- **Chain of Command** — cost 1, skill. "Play on the Bake-Kurage. Plan: Deal 6 damage for each Companion card you played last turn."
- **Sango Isshin** [Hydro] — cost 2, attack. "Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead."
- **Stolen Chapter** — cost 1, skill. "Draw 2 cards. Plan: Draw 4 cards."
- **Kujou Sara — Crowfeather Cover** — cost 0, skill. "Your next Attack this turn deals 4 additional damage and applies Electro."

**Took Sango Isshin.** At Max HP 80 the conditional clause reads **20 damage to ALL enemies for 2 energy**, and its condition is the rhythm I was already playing — plan on turn N, the Kurage carries it out at the start of turn N+1, so Sango Isshin is live on every turn after a planned one. It also scales with Stone Humidifier, since resting raises Max HP and the card reads a quarter of Max HP.

Chain of Command is the second card in two rewards to be priced in **Companion** cards, of which I own none — for me it reads "Deal 0 damage."

### Fight 3 — Nibbit (46 HP), floor 3

**A glossary line changed mid-run.** On this screen the Plan entry read:

> **Plan** — On the Bake-Kurage, paid now; lands next turn on the front enemy, **or ALL if it says so**. Enemy Vulnerable counts; your Weak does not.

In fights 1 and 2 the same entry read "the Plan lands first thing next turn on the front enemy" with no "or ALL" clause — i.e. it flatly contradicted Kurage's Oath's own "Deal 7 damage to ALL enemies". The Elemental Reaction entry also grew a new paragraph on this screen, warning that the Tamakushi Casket can re-apply the aura inside the same beat so a reaction "looks as though it did not happen".

**Turn 1.** Nibbit 46 HP, intent `Attack for 12`. Played **Ambush → Bake-Kurage**, **Slack Water**, **Strike** — Slack Water and Strike deal the same 6 (4 + 2 Casket), but Slack Water adds the Weak that turns 12 into 9.

*Predicted 12 dealt, 9 taken.* Got both: 46 → **34**, HP 55 → **46**.

**Turn 2.** `Bake-Kurage: Ambush, 12` → 34 → **22**. Intent now `Attack for 6` **and also** `Defensive (Defend)` — a two-line intent, the first I'd seen.

That Block changes the pricing: damage dealt *now* lands before the Block goes up, damage next turn has to chew through it. So I took the max-damage line rather than the safe one, and planned Oath as well, because a Plan resolving on turn 3 is also what arms Sango Isshin. Played **Kurage's Oath → Bake-Kurage**, **Strike**, **Strike**. 22 → **10**, took the full 6 (no Weak this time), HP 46 → **40**.

**Turn 3.** `Bake-Kurage: Kurage's Oath, 7`, and the enemy showed **8/46**, not 3.

**Plan damage is absorbed by enemy Block.** 10 − 7 = 3 was my naive prediction; the actual 8 means the Nibbit's Block ate 5 of the 7 and only 2 reached HP. So the Bake-Kurage ignores *my* attack-reduction debuffs (fight 1) but does not ignore *enemy* Block. Both halves are consistent — it is a damage source of its own, not an Attack of mine — but no screen says so.

Intent `Empower (Buff)`, 8 HP left, two Strikes = 12. Dead on turn 3.

**Fight 3 result: won on turn 3, HP 40/80.** This fight cost 15 HP, more than fights 1 and 2 combined (6 + 3).

**Reward:** `19 Gold`, card.

- **Salt Line** — cost 1. "Gain 8 Block. Exhaust."
- **Feint** [Hydro] — cost 1, attack. "Deal 6 damage. Plan: Deal 10 damage."
- **Read the Field** — cost 1, skill. "Gain 5 Block. Plan: Gain 10 Block."
- **Sayu — Yoohoo Art: Fuuin Dash** — cost 1, attack. "Deal 8 damage to a random enemy and Swirl it." (*Swirl* — "The enemy's aura is consumed and copied onto ALL enemies. No aura, no effect.")

**Took Read the Field.** Two jobs for one card: 10 Block for 1 energy is double a Defend, *and* because Block from a Plan arrives at the start of my turn it still covers the enemy's next attack, so it is strictly better timing than holding a Defend — and planning it also arms Sango Isshin. Nibbit had just cost me 15 HP through 5-Block Defends, so Block was the gap.

### Shop (floor 4)

Routed here deliberately: at 40/80 HP a Shop is the only node that costs no HP, and it converts gold I was otherwise banking.

**The shop screen printed `You have 140 gold`.** The three reward screens had printed 10 + 12 + 19 = **41**. So roughly 99 gold of starting money existed that **no screen ever printed** — not Neow, not any combat screen, not any reward. This is a straight answer to "anything a screen granted without saying so".

Shelves:

- Sango Isshin, 157 · Feint, 50 · Tide Wall, 74 · Shell Guard, 75 · **Treatise, 37** · **Shinobu — Sanctifying Ring, 78** · Diona — Signature Mix, 74
- Orichalcum 241 · Akabeko 246 · Sling of Courage 215 (all unaffordable)
- Cure All 71 · Cunning Potion 77 · Heart of Iron 75 · Card Removal 75

**Bought Shinobu — Sanctifying Ring (78)** — "Lose 3 HP. For 3 turns, at the end of your turn deal 5 Electro damage to ALL enemies and gain 5 Block. Exhaust." That is 15 damage *and* 15 Block for one energy and 3 HP, and the Block arrives at the end of my turn so it covers the enemy's swing. The best boss card on the shelf.

**Bought Treatise (37)** — "Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card." I plan nearly every turn, so this is a card a turn for 37 gold, the cheapest thing on the shelf by a distance.

Left with 25 gold, nothing else affordable. Deck now 16 cards.

A nice touch worth recording: once bought, a shelf prints `(this shelf is empty) — card, 37 gold (not available)` and says plainly that the name and text lived on the card so the feed cannot say what it was.

### Fight 4 — Leaf Slime 13 + Leaf Slime 11 + Slithering Strangler 55 (floor 5)

The first multi-enemy fight, and the one that answered the Plan-targeting question outright.

**Turn 1.** Intents: both slimes `Attack for 3`, Strangler `Strategic (Debuff)`.

With three bodies on the field Kurage's Oath's Plan is worth 7 × 3 = **21 damage for 1 energy**, its best rate of the run. Played **Oath → Bake-Kurage**, then two Strikes into the 11 HP slime — 12 damage, exactly enough to kill it, where 12 into the 13 HP slime would have left it at 1.

*Predicted: slime 2 dies; next turn Oath hits everything left.*

**Turn 2 confirmed the ruling.** `Bake-Kurage: Kurage's Oath, 7`, and both survivors had taken exactly 7: the 13 HP slime read **6/13**, the Strangler **48/55**.

**So the card's own "Deal 7 damage to ALL enemies" governs, and the glossary's "lands next turn on the front enemy" is wrong** — or rather, was wrong for two fights and then quietly rewrote itself to "or ALL if it says so". Anyone reading only the keyword box would have mispriced this card by 14 damage.

I also picked up `Constrict 3 (debuff) — While the Slithering Strangler is alive, at the end of your turn, take 3 damage.` A per-turn clock that only stops when one specific enemy dies — it makes the Strangler the target, not the slimes.

HP 40 → **37** (one surviving slime hit for 3; the dead one's 3 never came).

**The Sango turn.** A Plan had been carried out that turn, so Sango Isshin's conditional was live. Max HP 80, a quarter is 20:

Played **Sango Isshin** → Strangler **48 → 28**, and the 6 HP slime died. Exactly 20 to ALL, exactly as computed. 26 damage removed for 2 energy.

Then **Shinobu — Sanctifying Ring** with the last energy, and the end-of-turn chain went off in full:

- Shinobu's 5 Electro hit the Strangler's **Hydro** aura → **Electro-Charged**, which the screen renders as `Poison 3 (debuff) — At the start of its turn, loses 3 HP, then reduce Poison by 1` (i.e. applied at 4, shown at 3 after one tick).
- The Poison is a debuff, so the **Tamakushi Casket fired for 2 Hydro damage** — and re-applied the Hydro aura in the same beat, so the screen still showed `Hydro Aura 1` and nothing ever looked consumed.
- Then Poison ticked 4 at the start of its turn.

Arithmetic: 28 − 5 (Electro) − 2 (Casket) − 4 (Poison) = **17**, which is exactly what the screen showed. **This is precisely the case the expanded Elemental Reaction glossary warns about**, and without that paragraph I would have concluded the reaction had not fired.

HP 37 → **24**: 3 (Shinobu's own cost) + 3 (Constrict) + 7 (the Strangler's 12 minus Shinobu's 5 Block).

**Turn 3.** Strangler 17 HP, `Poison 3`, intent `Strategic (Debuff)` — no damage, so the turn was nearly free. Played **Strike** (17 → 11), **Read the Field → Bake-Kurage** (10 Block banked for a turn that might not come), **Defend**.

*Predicted the kill without a fourth turn:* end of turn Shinobu 5 → 6, reaction + Casket 2 → 4, then Poison ≥ 4 at the start of its turn = dead. It died before acting. Correct.

**Fight 4 result: won on turn 3.** Cost: 16 HP, the most expensive fight so far (running total 6, 3, 15, 16 — rising steeply).

**Reward:** `20 Gold`, `Vulnerable Potion`, card.

- **Deep Current** [Hydro] — cost 1. "Deal 6 damage to ALL enemies."
- **Feint** [Hydro] — cost 1. "Deal 6 damage. Plan: Deal 10 damage."
- **Coral Bulwark** — cost 1. "Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak."
- **Charlotte — Framing: Freezing Point Composition** [Cryo] — cost 1. "Deal 4 damage. Draw 1 card."

**Took Coral Bulwark.** I priced it against the fight I had just had: planned, it is 8 Block *plus* a Weak that turns a 12-damage swing into 9, so it prevents 11 where a Defend prevents 5, and the Weak also fires the Casket for 2. Replayed over fight 4 it saves about 6 HP. Feint was the runner-up (a strictly-better Strike and a third Plan card to keep Sango live); Charlotte was the interesting one — a Cryo source next to my all-Hydro deck, and per the glossary Hydro + Cryo on a **boss** "applies 2 Vulnerable instead", and Vulnerable is the one thing the Plan box says *does* raise Plan damage. I passed on it because a two-card combo at 24 HP is worse than a card that never blanks.

### Wellspring (floor 6)

- **Bottle** — "Procure 1 random Potion."
- **Bathe** — "Remove 1 card from your Deck. Add 1 Guilty to your Deck."

Took **Bottle**. Bathe is card-count-neutral and "Guilty" is a name with no text anywhere on the screen — blind, trading a known Strike for an unnamed penalty card is a bad deal, and my deck had no card bad enough to be worth it.

**The potion it produced could not be taken.** The screen printed `Regen Potion` and then:

> *Your potion slots are full: 3 of 3. A potion claimed now has nowhere to go, and the game says nothing when one is dropped -- so this page will not claim it until a slot is free.*

I tried to claim it anyway (my one refusal of the run). The refusal read: "your potion slots are full: 3 of 3 ... **Use one first**, or leave this on the screen". But this screen's grammar is only `choose` / `proceed` — **there is no `use potion` form on a reward screen**, so "use one first" is advice that cannot be followed. At 24/80 HP a Regen Potion was the single most valuable thing I had been offered all act, and it was structurally unreachable. Lost it.

### ELITE — Phrog Parasite (64 HP) + 4 Wrigglers (floor 7)

Entered at **HP 24/80**, forced: the map offered exactly one node. Potions full: Gambler's Brew, Skill Potion, `Vulnerable Potion — Apply 3 Vulnerable`.

The elite printed `Infested 4 (buff) — Upon dying, summons... something.` This is the brief's "clock that pays out after a kill", so the first thing I did every round was re-read the number. **It stayed at 4 all fight — it does not grow.** So the danger was not *when* I killed it but *what state I was in* when it died.

**Turn 1.** Intent `Strategic (StatusCard)` — 3 Status cards, no damage. A free turn, so Block played now would be wasted but Block *planned* arrives at the start of my next turn and covers the next attack. Played **Treatise**, **Coral Bulwark → Bake-Kurage**, **Strike**.

**Turn 2.** Everything paid as predicted: `Block 8`, the enemy carried `Weak 1`, and 64 − 6 (Strike) − 2 (Casket, fired by the planned Weak) = **56**. Treatise drew me a 6th card. Intent `Attack for 3 damage 4 times`.

A Plan had been carried out, so Sango was live: **Sango Isshin** → 56 → **36** (20 to ALL again), then **Shinobu — Sanctifying Ring**.

End of turn chain: Electro 5 → 31, Electro-Charged → Poison, Casket 2 → 29, Poison 4 at its turn start → **25**. Total 31 damage in one turn for 3 energy. The 4×3 attack (weakened, 8) was fully eaten by 8 + 5 = 13 Block: **HP 24 → 21, and the only 3 of that was Shinobu's own cost.**

**Turn 3 — the kill-timing decision, and the sharpest judgement call of the run.** Enemy 25 HP, `Poison 3`, intent `StatusCard` again — another free turn.

I could kill it this turn: 3 Strikes (18) → 7, then Shinobu's end-of-turn 5 + Casket 2 = dead. But that kill lands at the *end of my turn*, so the summons would arrive and the enemy phase would begin immediately, with me holding only Shinobu's 5 Block at 21 HP.

Instead I left it alive on purpose: **Strike, Strike** (25 → 13) and **Kurage's Oath → Bake-Kurage**. The plan was that it dies at the *start* of my next turn, so I would meet whatever it summoned with a full hand and 3 energy. Its printed intent was harmless, so the delay cost nothing.

**It died even earlier than that, and the reason is a real finding: Poison stacks additively.** It sat at `Poison 3`; Shinobu's Electro triggered a fresh Electro-Charged worth 4, and 3 + 4 = 7 killed it outright at the start of its own turn from 6 HP — before it acted, so the 3 Status cards were never delivered either.

**Turn 4.** `Infested 4` summoned **exactly 4 Wrigglers** — the buff's number is the count. And they arrived at 13/20, 14/21, 12/19, 11/18: **every one already down exactly 7**, because they spawned during the enemy phase and my Kurage's Oath Plan then swept the whole new field at the start of my turn. All four printed `Intent: Stunned (Stun) — This enemy can't act on its next turn.`

So the cautious line paid twice over: the summons walked into a pre-paid AoE and could not act.

I then placed 2 Strikes to let the end-of-turn tick finish the rest — Strike on the 13 (→7, killed by Electro 5 + Casket 2) and Strike on the 14 (→8, left at 1 for Poison), planning **Coral Bulwark** so the Weak's Casket ping would clean up the survivor. *I predicted one Wriggler would survive at 1 HP.* All four died. I could not tell from the screens whether the Casket fired once per enemy or the Poison ticks ran higher than I modelled.

**ELITE CLEARED at HP 21/80, taking 0 damage from the summons.**

**Reward:** `42 Gold`, **Oddly Smooth Stone** (relic), card.

- **Nereid's Ascension** — cost 2. "Play on the Bake-Kurage. Plan: for 2 turns, the Bake-Kurage carries out every Plan twice. Exhaust."
- **Moon's Reflection** — cost 1. "Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none. Exhaust."
- **Song of Pearls** — cost 1, power. "Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block."
- **Gorou — Inuzaka All-Round Defense** — cost 1, attack. "Deal 8 damage. Gain Block equal to half the damage dealt."

**Took Gorou.** 8 damage *and* 4 Block for 1 energy is a strict upgrade on the four 6-damage Strikes that are the dead weight of my deck, it never blanks, and at 21/80 HP it answers the actual problem. Nereid's Ascension is the most exciting card I was offered all act — doubling Ambush to 24 a turn — but it wants a 3-energy setup turn that deals no damage, which is the turn that kills me at this HP.

### Fight 5 — Cubex Construct (65 HP), floor 8

Entered HP 21/80. New relic in play: **Oddly Smooth Stone — "Start each combat with 1 Dexterity"**, and `Dexterity 1 (buff) — Increases Block gained from cards by 1`. Every Block face went up by 1 on the card itself: Defend printed "Gain 6 Block", Coral Bulwark "Gain 7 Block".

The enemy carried `Artifact 1 (buff) — Negates 1 debuff` and its intent was `Empower (Buff)` — another free first turn. Played **Treatise**, **Coral Bulwark → Bake-Kurage**, **Strike**, deliberately spending the planned Weak as a throwaway to strip the Artifact so that the real debuff (the Electro-Charged Poison) would stick later.

**Turn 2 gave a clean negative result.** Block came in at **9** — so Dexterity *does* apply to Block delivered by a Plan (8 + 1), which no text says. The Weak was absent and `Artifact` was gone, consumed. And the damage was 65 − 6 = **59 exactly**: **a negated debuff does not fire the Tamakushi Casket.** No 2 Hydro damage. The relic keys off the debuff actually landing, not off the attempt.

Intent `Attack for 11` *and* `Empower` on the same turn, with `Strength 4` — this enemy ramps every round, so it is a race.

A Plan had resolved, so Sango was live: **Sango Isshin** (59 → 39) + **Shinobu — Sanctifying Ring**. End of turn: Electro 5 → 34, Electro-Charged, Casket 2 → 32, Poison 4 at its turn start → **28**. 31 damage again. The 9-damage attack was fully blocked (9 + 5). HP 21 → **18**, all of it Shinobu's own cost.

**Turn 3 — the sequencing turn.** Gorou's card face now carried a line the main glossary never lists:

> *Reaction preview: Crystallize* — This card supplies Geo to an existing aura. The aura is consumed and you gain 4 Block.

So Gorou is **Geo**, and playing it would eat the Hydro aura my Electro chain depends on. That makes order load-bearing: Gorou first (banking the Crystallize Block), then Slack Water to *re-apply* Hydro, so Shinobu's end-of-turn Electro still had an aura to react with.

Played **Gorou** → 28 → **20**, and Block **9** = 4 (half the 8 damage dealt) + 4 (Crystallize) + 1 (Dexterity). The Hydro aura vanished from the enemy exactly as the preview said.

Then **Slack Water** (re-applying Hydro, +Weak +Casket) and **Strike**, leaving it at 8. *Prediction: end of turn Electro 5 → 3, Electro-Charged + Casket 2 → 1, then Poison kills it at the start of its turn before it can attack — the same before-it-acts kill the Phrog showed me.*

That is what happened. **Fight 5 won, 0 damage taken that turn, HP 18/85.**

**Reward:** `11 Gold`, `Snecko Oil`, card. **Snecko Oil could not be claimed — potion slots full again.** That is the second potion lost to a full inventory. The practical lesson, learned too late twice: a potion should be *spent during the fight* to open a slot before the reward screen appears, because the reward screen has no `use potion` form.

Card offer: Deep Current, Moon's Reflection, Rally, **Shinobu — Thundergrust** [Electro] — cost 1, "Deal 8 damage. If you are below half HP, deal 5 additional damage."

**Took Thundergrust.** At 18/85 that reads **13 damage for 1 energy**, the best rate offered all act, and its floor (8) still beats a Strike's 6. More importantly it is a repeatable **Electro** source in an all-Hydro deck, which lets me trigger the Electro-Charged → Poison → Casket chain on purpose instead of only when Shinobu's Ring is up.

### Treasure (floor 9) and Rest (floor 10)

Chest: **Red Mask — "At the start of each combat, apply 1 Weak to ALL enemies."** Taken. It should also fire the Casket for 2 per enemy on turn 0, since the Casket triggers on applying a debuff.

Routing: both nodes were Treasure, but one led on to a RestSite and the other to a Monster. At 18 HP that chose itself.

**Rest site.** Printed `HP 18/80` and offered `Rest — Heal for 30% of your Max HP (24). Raise your Max HP by 5.` or `Smith — Upgrade a card in your Deck.` Rested.

**Result: HP 18/80 → 47/85 — a gain of 29, where the screen promised 24.** The Stone Humidifier's +5 Max HP also added +5 to *current* HP, which neither the relic ("raise your Max HP by 5") nor the rest option says. A pleasant surprise, but an unannounced one.

Two knock-on effects worth noting: Sango Isshin reads "a quarter of your Max HP", so it is now **21**, not 20 — the Humidifier and Sango scale together. And 47 is above half of 85, so Thundergrust drops back to 8 damage.

### ELITE 2 — Byrdonis (83 HP), floor 11

Entered HP 47/85. **Red Mask worked as hoped and the screen showed the whole chain on turn 0:** Byrdonis opened at **81/83** carrying `Weak 1` and `Hydro Aura 1` — the free Weak fired the Casket for 2 Hydro damage, and the Casket's Hydro hit left the aura behind. A relic that opens every fight with a debuff, 2 damage and an aura for the reaction engine.

Its buff: `Territorial 1 — At the end of Byrdonis's turn, it gains 1 Strength.` A permanent ramp, so every extra turn is paid for twice.

**Turn 1.** Played **Treatise**, **Ambush → Bake-Kurage**, **Strike**. 81 → **63** on turn 2 (Strike 6 + Ambush 12 = 18, exact).

**But I took the full 12, not 9.** `Weak 1` was displayed on Byrdonis at combat start, yet the 12-damage attack landed for 12 — HP 47 → **35**. Compare the Shrinker Beetle in fight 1, where a Weak applied *during my turn* turned a printed 13 into 9. **Red Mask's Weak appears to expire before the enemy's first attack ever happens**, so its damage-reduction half is wasted; only the Casket ping and the aura survive. I could not test this a second time.

**Turn 2 — the Vulnerable turn.** I spent `Vulnerable Potion — Apply 3 Vulnerable` here rather than saving it for the boss, for three reasons: an 83 HP enemy that ramps is exactly what a damage multiplier is for, Vulnerable's 3 turns overlap Shinobu's Ring 3 turns, and using a potion mid-fight is the only way to have a free slot when the reward screen appears.

It immediately showed something the text does not: 63 → **60**. The Casket's ping came in at **3, not 2** — `Vulnerable 3 — Receive 50% more damage from Attacks` scales relic damage too (2 × 1.5 = 3).

Then **Slack Water**, **Strike**, **Shinobu — Sanctifying Ring**. Predicted total: Slack Water 6 + Casket 3 + Strike 9 + Electro 7 + Casket 3 + Poison 4 = **32**. Actual: 60 → **28**. Exact.

HP 35 → **28** = 3 (Shinobu) + 4 (the 3×4 attack, weakened to 9, less 5 Block).

**Turn 3 — and two display facts worth recording.**

`Kurage's Oath` printed **"Plan: Deal 10 damage to ALL enemies"**, up from its usual 7 — the card face folds Vulnerable into the Plan's number (7 × 1.5 = 10.5 → 10), which is the Plan box's "Enemy Vulnerable raises it" made visible. But `Shinobu — Thundergrust` still printed a flat **"Deal 8 damage"** while I was below half HP *and* the target was Vulnerable, so its real value was 19. **Plan cards show their modified number; attack cards do not.** A player pricing the turn off the printed faces would under-read Thundergrust by 11.

Thundergrust also gained a *Reaction preview: Electro-Charged* line, the same style of per-card hint Gorou got for Crystallize.

Byrdonis at 28 HP intending **19 damage** into my 28 HP — a turn I had to end. Thundergrust (8 + 5 below-half = 13, ×1.5 Vulnerable = 19) + Strike (9) = 28, exactly lethal, and it died on the second card.

**ELITE 2 CLEARED, HP 28/85, 3 turns.**

**Reward:** `44 Gold`, `Stable Serum`, **Blood Vial** (relic), card — **and this time the potion was claimable**, because the Vulnerable Potion had opened a slot mid-fight.

**The card screen finally defined the keyword five rewards had been priced in:**

> **Companion** — A card titled with a character's name, a dash, then its own. Card rewards after a fight offer a fourth, Companion, choice.

That explains the shape of every reward: three ordinary cards plus one "Name — Title" card. Rally and Chain of Command, offered in fights 1 and 2, were priced in Companions before anything on screen said what a Companion was.

Offer: Sea-Salt Prayer · War Council · The General's Banner · **Thoma — Blazing Barrier** (cost 1, "Gain 6 Block. Whenever this Block absorbs damage, gain 3 Block").

**Took Thoma.** With Dexterity it opens at 7 and grows 3 per absorbing hit, which is the direct counter to the 4×3 / 3×4 multi-hit attacks this act keeps using, and I am 28/85 heading for a boss.

### Fight 6 — three Inklets (11 / 16 / 14 HP), floor 12

Entered 28/85; **Blood Vial — "At the start of each combat, heal 2 HP"** took me to 30 before the first card.

Red Mask opened again, but with a discrepancy I could not explain: each Inklet showed **1** damage taken (11→10, 16→15, 14→13), where Byrdonis had taken the full **2** from the same relic. Same relic, same trigger, half the damage on a three-enemy board. Nothing on the screen accounts for it.

Low-threat fight (7 total damage, all Weakened). Turn 1: **Gorou** into the 14 (Crystallize consumed its Hydro aura, Block 9) and two Strikes to kill the 11 — chosen because Gorou's Block covered the whole incoming turn. **0 damage taken.** Turn 2: Strike killed the 5 HP one — deliberately the one intending `2 damage 3 times`, removing 6 of the 9 incoming — plus **Kurage's Oath → Plan** and **Treatise**. Took 3. Turn 3: Oath's Plan had taken the last one 15 → 8, and Thundergrust (13, below half) finished it.

**Won in 3 turns for 3 HP.** Reward `20 Gold` + card: took **Battle Plan** ("Plan: Gain 1 Energy and draw 2 cards") over a second Coral Bulwark — it repays its own energy, adds two cards, and is itself a Plan card, so it arms Sango on the turn it resolves.

### Routing decision, floor 13

Two nodes: `Elite → Monster` or `Monster → Elite`. Both orders force the same two fights before the guaranteed all-RestSite floor, so the only question was which fight to take at my healthiest. I took the **Elite first at 27 HP** rather than meeting it at ~22 after a monster. (Blood Vial made it 29 on arrival.)

### ELITE 3 — Bygone Effigy (127 HP), floor 13

The most interesting fight of the run, and the one where the screens rewarded reading closely.

Two lines mattered:

> Intent: `Sleeping (Sleep) — This enemy is doing nothing this turn.`
> `Slow 0 (debuff) — Whenever you play a card, this enemy receives 10% more damage from Attacks this turn.`

Slow inverts normal pricing: cheap cards are not filler, they are a multiplier, and the **order** of a turn decides its damage. Combined with a free first turn against a 127 HP body, the correct play was to build the biggest possible single turn.

**Turn 1 (free).** Used **Stable Serum — "Retain your Hand for 2 turns"** specifically to carry **Sango Isshin** into the following turn instead of discarding it (it would otherwise have gone to the bottom of a 21-card deck), and to open a potion slot. Then **Battle Plan → Bake-Kurage**, **Shinobu — Sanctifying Ring**, **Strike**.

The Strike did **7, not 6** — 6 × 1.2, because two cards had been played before it. Slow confirmed, and confirmed to count only cards played *earlier in the turn*.

**Turn 2 — the payoff.** Battle Plan delivered: **Energy 4/3** and a **9-card hand**, and because a Plan had been carried out, Sango was live. Intent was `Empower` again — a second free turn.

Sequenced deliberately, biggest hit last: **Ambush → Plan** (card 1), **Thundergrust** (card 2, ×1.2), **Sango Isshin** (card 3, ×1.3). Playing Sango last rather than second is worth about 1 damage on Sango and costs about 1 on Thundergrust — I checked both orderings and took the better one.

Result: **107 → 35, 72 damage in one round.** The chain: Thundergrust 15 + Casket 2, Sango 27, Shinobu's Electro 5 + Casket 2, Ambush's Plan 12, and Poison. **Poison reached 14** — each Electro-Charged stacks a fresh 4 onto the existing count, and with two reactions per round it compounds fast.

**Turn 3 — the kill, priced off Poison rather than damage.** The Effigy sat at 35 HP with `Poison 14`, `Strength 10`, intending **23 damage** into my 26 HP. The naive read is "I need 35 damage and I do not have it."

The real requirement was ~10. Shinobu's last Electro tick would restack Poison to ~18 and add 5 + 2, so anything that brought it under ~28 would die to Poison **at the start of its turn, before it attacks** — the same ordering the Phrog and the Cubex had already taught me.

Played **Thoma — Blazing Barrier** (7 Block as insurance, and a Slow stack) then two Strikes at ×1.2 and ×1.3 = 14 damage. It died before swinging.

**ELITE 3 CLEARED, HP 26/85, 0 damage taken in the entire fight.** A 127 HP elite that never landed a hit.

**Reward:** `44 Gold`, **Strike Dummy** (relic), card. Took **Kirara — Surprise Dispatch** (cost 1, "Gain 8 Block. Next turn, deal 10 damage to a random enemy") over a second Battle Plan: 9 Block *and* 10 damage for one energy is the best rate on offer, and energy — not cards — is my binding constraint.

### Fight 7 — Leaf Slime (M) 34 + Flyconid 47, floor 14

New relic live: **Strike Dummy — "Cards containing 'Strike' deal 3 additional damage."** My four Strikes immediately printed **9** instead of 6, which is the single biggest lift the deck's dead weight received all act. (It also implies it would boost any card with "Strike" in its *name* — Heizou's "Heartstopper Strike" was later offered and would have read 9.)

Red Mask again, and this time each of the two enemies took the full **2** (34→32, 47→45), where the three Inklets had each taken only 1. I have no explanation from the screens.

**Turn 1.** Battle Plan → Plan, Strike (9) and Gorou (8) both into the **Flyconid** — chosen because it was the one dealing damage while the Slime only handed out Status cards, and Gorou's 9 Block covered the whole incoming turn. Flyconid 45 → **28**, 0 damage taken.

**Turn 2.** The Flyconid's debuff landed: `Frail 2 — Gain 25% less Block from cards for 2 turns`, and every Block face on my screen dropped at once (Thoma 7→5, Defend 6→4, Kirara 8→6, Read the Field 6→4). Energy 4/3 from Battle Plan.

Played **Shinobu — Sanctifying Ring**, **Thundergrust** (13) and **Strike** (9) into the Flyconid, plus **Kirara — Surprise Dispatch**. Note the enemies had no auras at this point (Gorou's Crystallize had eaten one), so my Electro cards applied Electro rather than reacting — no Poison this round. Flyconid → 1, and Kirara's 10 plus Shinobu's 5 took the Slime 32 → 17. Again **0 combat damage** (the 3 HP lost was Shinobu's own cost).

**Turn 3 — the turn that needed reading.** I was carrying `Vulnerable 2 — Receive 50% more damage from Attacks for 2 turns` (the Flyconid's second debuff), and the Flyconid intended **16**, which against Vulnerable is **24** into my 25 HP. That is the kill.

But it sat at **1 HP**. One Strike removed a 24-damage threat for one energy — the cheapest defensive play of the run, and only visible because the screen prints both the intent number and my own debuffs.

Then **Sango Isshin** into the Slime, which its own card face now previewed: *Reaction preview: Electro-Charged*, because Sango is Hydro and the Slime wore Electro. Sango 8 + Casket 2, then the end-of-turn Shinobu tick and a second reaction finished it.

**Won in 3 turns, 0 combat damage taken across the whole fight.**

**Reward:** `10 Gold`, `Explosive Ampoule` (claimable — the Stable Serum I spent in the Effigy fight had left a slot open), card.

**I skipped the card.** Offer was Deep Current (6 to ALL), Stolen Chapter, Sea-Salt Prayer, Shikanoin Heizou — Heartstopper Strike. With Strike Dummy live my ordinary Strike deals **9**, so Deep Current's 6 and Heizou's 9-without-a-Swirl are both at or below what I already hold; Sea-Salt Prayer is a weaker Coral Bulwark; Battle Plan already supplies draw. At 23 cards a marginal card mostly lowers the odds of drawing Sango, Battle Plan or Kirara in the boss fight, so taking nothing was worth more than taking any of these.

### Rest before the boss (floor 15)

`Rest — Heal for 30% of your Max HP (25). Raise your Max HP by 5.` versus `Smith — Upgrade a card`. At 25 HP before a boss, no single upgrade competes with ~30 HP.

**HP 25/85 → 55/90.** Worth noting the arithmetic differs from the first rest: the heal was **25**, which is 30% of the *old* 85 max, and the +5 Max HP was added on top — so the heal is calculated before the Humidifier's bump, not after. Sango Isshin now reads a quarter of 90 = **22**.

### BOSS — Vantom (173 HP), floor 16

Entered **57/90** (Blood Vial's +2 on top of 55).

> `Slippery 7 (buff) — The next 7 times Vantom loses HP, it only loses 1 HP instead.`

This is the boss's whole puzzle, and it inverts normal pricing: for the first seven *instances* of HP loss, the size of the hit is irrelevant. Playing Sango (22) into Slippery would have converted my best card into 1 damage. The correct play is to spend seven of the **cheapest** instances available, then unload. Red Mask's opening Casket ping had already spent one (173 → 172, exactly 1 damage, confirming the reading before I committed anything).

**Turn 1 — deliberate waste.** Strike, Strike, **Thundergrust**. Thundergrust was chosen precisely *because* it was weak at that moment: I was above half HP so it read 8 rather than 13, and as an Electro hit on a Hydro aura it triggers Electro-Charged, whose Poison is a debuff, which fires the Casket — **two instances from one card**.

Result: Slippery **7 → 2**, and 172 → 167, i.e. exactly 5 damage from 5 instances (Strike, Strike, Thundergrust, Casket, Poison tick). The mechanic behaves exactly as printed.

Also a **second data point on Red Mask**: the boss's printed 5-damage attack landed for the full 5 despite `Weak 1` being on it at combat start. Combined with Byrdonis's 12, I am fairly confident Red Mask's Weak expires before the enemy's first action.

**Turn 2 — clearing the rest, and a discovery.** Shinobu's Ring alone supplies the two remaining instances at end of turn (its Electro, then the Casket off the reaction's Poison), so I spent the other two energy setting up and **tested whether the Bake-Kurage can hold more than one Plan.** It can:

> Planned, and carried out at the start of your next turn in this order **(2)**:
> 1. **Battle Plan**
> 2. **Coral Bulwark**

**Nothing in the Plan glossary says Plans stack** — only the buff's phrase "in order" hints at it. This is a significant hidden rule: it means a turn's energy can be banked wholesale into the next turn.

**Turn 3 — the payoff.** Both Plans resolved: Energy **4/3** plus two cards from Battle Plan, and Block 9 plus a Weak from Coral Bulwark, and Slippery was gone. Strike, Strike, Kirara, Oath → Plan.

**Vantom 156 → 104: 52 damage in one round**, and I took **0** (18 Block vs a weakened 14). The breakdown: Strikes 18, Shinobu 7, Poison 10, Kirara's delayed 10, Oath's Plan 7.

**Turn 4 — sequencing again.** It buffed (free turn), so all three energy went to damage: **Gorou first** (its Crystallize eats the Hydro aura, +9 Block), **then Slack Water** to re-apply Hydro, then Strike. Playing Gorou second would have left the boss bare and Shinobu's final Electro would have applied an aura instead of reacting — stalling the Poison engine that was doing most of my damage. 104 → **58**, Poison up to 12.

(Slack Water also printed **7 damage**, up from 4 — **Strike Dummy is boosting a card whose printed name contains no "Strike"**. I cannot tell from any screen why.)

**Turn 5.** Vantom handed me its 3 Status cards as two unplayable `Wound` cards. Strike, **Coral Bulwark → Plan** (banking 8 Block + Weak and arming Sango) and a Defend. 58 → 35 with Poison at 11.

**Turn 6 — the kill, again priced off Poison and not damage.** Below half HP, Thundergrust read **13**. Played Thundergrust (+ its Electro-Charged restacking Poison to ~15 and a Casket ping), **Kirara** for 9 more Block, and **Oath → Plan**. I deliberately did **not** spend Explosive Ampoule: 18 Block against a weakened 8 meant no risk, and Poison plus the queued Oath would finish it — so the potion carries forward to the next seat.

**VANTOM KILLED.** Reward `100 Gold` and a boss card.

Offer: The Clouds Like Waves Rippling · **Sango Isshin** · The Moon, A Ship O'er the Seas · Raiden Shogun — Musou no Hitotachi ("Deal 20 damage. Deals 5 additional damage for each Companion card you played this combat").

**Took the second Sango Isshin.** Raiden has the higher ceiling (I own five Companion cards, so ~30–35 single-target), but Sango is 22 to ALL for 2 energy on a condition my deck meets almost every turn, and it is the one card that **scales with Max HP**, which Stone Humidifier raises at every rest. Doubling its frequency was worth more than a 3-cost finisher.

**Act 1 complete. The lane stands on the act-2 map. Act 2's boss is named `The Insatiable`.**

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

Four stand out.

1. **The Effigy's kill-timing, and the Phrog's before it.** With the Phrog Parasite I could have killed it on turn 3 with three Strikes. I chose not to, because the kill would have landed at the *end* of my turn and `Infested 4 — Upon dying, summons... something` would have put unknown enemies on the board with the enemy phase starting immediately. Leaving it alive to die at the start of my next turn traded one round of clutter for a full turn of energy against the summons. It paid twice: the four Wrigglers arrived pre-damaged by my queued Oath (each exactly −7) and every one printed `Stunned`.

2. **Slippery vs. my best card.** The boss's `Slippery 7` made "play your biggest card" actively wrong. Choosing to spend Strikes and a *deliberately weakened* Thundergrust as throwaways — and to hold Sango entirely — was the sharpest read the run asked for.

3. **Sequencing within a turn.** Twice the order of three cards changed the outcome: Gorou-before-Slack-Water (so Crystallize's aura consumption was repaired before Shinobu's Electro needed it), and cheap-cards-before-Sango under the Effigy's `Slow`. Same three cards, different totals.

4. **Skipping a card reward.** After Strike Dummy made my Strikes deal 9, every card offered at floor 14 was at or below what I already had, so taking nothing beat taking something. That is a real choice the game let me make and that mattered.

Routing was a genuine choice twice: the Shop at 40/80 (the only node that costs no HP), and Elite-before-Monster at floor 13 — both orders forced the same two fights, so the only question was which to meet at my healthiest.

### (b) What felt automatic, and what never seemed worth playing

**Automatic:** the opening of nearly every fight. If the enemy's intent printed no damage number, the turn wrote itself — never Block, always plan a card and spend the rest on damage. That happened in seven of eleven combats, because this act is full of `DebuffStrong`, `Empower`, `StatusCard` and `Sleeping` first turns. Also automatic: whenever a Plan had resolved and Sango was in hand, Sango was played. It was never a question.

**Never worth playing:** **Defend**. Across the entire act I played it perhaps four times, always as the last energy of a turn with nothing better. At 5 Block (6 with Dexterity) it was outclassed by Coral Bulwark, Read the Field, Thoma, Kirara and Gorou — Gorou in particular gives 8 damage *and* 9 Block for the same energy. The four Defends were the deck's dead weight all act, and Strike only escaped the same fate because Strike Dummy arrived at floor 12 and made them 9.

**Rally** and **Chain of Command** were unplayable-on-sight in fights 1 and 2 — both priced in "Companion", a keyword the game did not define until the eleventh card screen.

### (c) What I could not understand, or that contradicted its own printed text

- **The Plan glossary flatly contradicted the cards for two fights.** It read "the Plan lands first thing next turn **on the front enemy**" while Kurage's Oath read "Deal 7 damage to **ALL** enemies". The card was right (fight 4: all three enemies took exactly 7). From fight 3 onward the glossary silently rewrote itself to "…on the front enemy, **or ALL if it says so**". I never saw an explanation for the change.
- **Red Mask's Weak does nothing defensively.** Twice (Byrdonis 12, Vantom 5) the enemy's first attack landed at full value with `Weak 1` visibly on it. A Weak I applied *during* my own turn always worked (13→9, 12→9). I could not test a third time.
- **The Casket ping varied and I cannot say why.** 2 damage each to Byrdonis and to both floor-14 enemies, but only **1** to each of three Inklets.
- **Strike Dummy boosted Slack Water** (4 → 7), whose printed name contains no "Strike".
- **Attack cards do not show their real number; Plan cards do.** Under Vulnerable, Kurage's Oath's face changed 7 → 10, but Thundergrust kept printing "8" when it was actually worth 19 (below-half +5, then ×1.5). Pricing a turn off the printed faces would have under-read it by 11.
- **Whether Block absorbs Constrict** — the end-of-turn ordering produced the same HP under either interpretation, so I could not separate them.
- Minor: **Slippery's initial value.** It printed 7 after Red Mask had already consumed one instance, so I never saw whether it began at 7 or 8.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: Defend.** 5–6 Block for a full energy, in a deck where Gorou buys 8 damage *and* 9 Block for the same price. It was filler from the first fight to the last.

**Happiest to draw: Sango Isshin** — 20/21/22 to ALL for 2 energy, on a condition my deck meets naturally. It removed 26 HP in the Strangler fight, 20 from the Phrog, and 27 in the Effigy turn. **Shinobu — Sanctifying Ring** is the close second and arguably did more total work, because its Electro is what kept the Electro-Charged → Poison → Casket loop running; that loop, not my attacks, is what killed the Phrog, the Cubex and Vantom.

### (e) Did the first turn of the first fight already present a decision?

**Yes, a real one, and it turned on arithmetic the screen gave me.** The Shrinker Beetle's intent was `DebuffStrong` — no damage number — which immediately deleted Defend from consideration and made it a pure damage question with 3 energy and four candidates.

The non-obvious part: Slack Water prints "Deal 4 damage" against Strike's "Deal 6", so it reads as the weaker card. But Slack Water applies a Weak, and the Tamakushi Casket adds 2 Hydro damage on any debuff — so it is **also 6**, plus a Weak and a Hydro aura for free. Once that ties, it strictly dominates the second Strike, and Kurage's Oath (7 for 1 energy, delayed) beats both on rate. The turn had a correct answer that was not the obvious one, and it required combining a card, a relic and an intent. That is a real decision on turn one.

### (f) Anything a screen granted or changed without saying so

- **~99 starting gold.** The shop printed `You have 140 gold`; the three reward screens before it had printed 10 + 12 + 19 = **41**. No screen — not Neow, not any combat or reward page — ever showed the starting balance. After the shop, no screen printed a running total again either.
- **The first rest healed 29, not the 24 it promised.** `Heal for 30% of your Max HP (24). Raise your Max HP by 5.` took me 18/80 → **47/85**. The Humidifier's +5 Max HP silently carried +5 *current* HP with it. (The second rest confirmed the shape: 25/85 → 55/90, where the heal was 25 = 30% of the **old** max, applied after the bump.)
- **The Bake-Kurage accepts multiple Plans**, which no card or glossary states.
- **Electro-Charged is rendered as `Poison`**, a word the glossary never uses, and **it stacks additively** — this is what killed the Phrog (3 + 4 = 7 against 6 HP) and drove Poison to 14 on the Effigy and 15 on Vantom. Nothing says it stacks.
- **Vulnerable scales relic damage**: the Casket ping went from 2 to 3 under Vulnerable.
- **Dexterity applies to Block delivered by a Plan** (Coral Bulwark's planned 8 arrived as 9).
- Conversely, a **negated debuff grants nothing**: when Artifact ate my Weak, the Casket did not fire at all (65 − 6 = 59 exactly).

---

## Findings, ranked by sharpness

**1. The Plan keyword box contradicted the cards it explains, then changed mid-run.** For fights 1–2 it read "lands first thing next turn **on the front enemy**", full stop, while Kurage's Oath read "Deal 7 damage to **ALL** enemies". Fight 4 settled it in the cards' favour — the Strangler went 55→48 and the surviving slime 13→6, both exactly 7, on the same Plan. From fight 3 the box read "…**or ALL if it says so**". A player who trusted the glossary would have valued Oath at 7 in a three-enemy fight where it was worth 21.

**2. Bake-Kurage Plan damage ignores my attack-reduction debuffs but not enemy Block.** Under `Shrink -1` ("your Attacks deal 30% less damage"), which visibly cut Strike's face from 6 to 4, the Oath Plan still logged `Kurage's Oath, 7` and took 28→21 — full value. But against the Nibbit's Block, the same 7 removed only 2 HP (10→8), with 5 eaten by Block. Both are consistent with the Kurage being a damage source of its own rather than "my Attack" — but no text anywhere says so, and the two halves point in opposite directions.

**3. The Bake-Kurage queues multiple Plans, which nothing documents.** Boss turn 2 printed `carried out at the start of your next turn in this order (2): 1. Battle Plan 2. Coral Bulwark`, and both resolved (Energy 4/3, Block 9, Weak applied). The only hint anywhere is the word "in order" in the buff line. This changes the whole economy of a turn — energy can be banked wholesale into the next one.

**4. Electro-Charged is printed as `Poison` and stacks additively; it was my main damage source and no screen says either.** The glossary says Electro-Charged makes the enemy "lose 4 HP at the start of its turn, 1 less each turn"; the enemy panel calls it `Poison N`. Two reactions in one round compound: the Phrog died at `Poison 7` (3 + 4) from 6 HP before it acted; the Effigy reached **14**; Vantom reached **15**. Three of my four hardest kills — Phrog, Cubex, Vantom — were finished by Poison at the start of the enemy's turn, not by an attack.

**5. Poison kills before the enemy acts, which repeatedly turned an unwinnable turn into a free one.** Ordering is: my end-of-turn triggers → enemy turn begins → Poison ticks → enemy acts. The Cubex (11 damage intent) and the Effigy (**23** damage intent into my 26 HP) both died in that gap. Against the Effigy this meant the turn needed only ~10 damage from cards, not 35 — the difference between "I cannot survive this" and a clean kill.

**6. Attack cards hide their modified damage; Plan cards show theirs.** Elite-2 turn 3: `Kurage's Oath` printed "Deal **10** damage to ALL" (7 × 1.5 Vulnerable), while `Shinobu — Thundergrust` printed a flat "Deal **8** damage" when it was worth **19** (8 + 5 below-half, then ×1.5). Pricing lethal off the printed faces would have missed a 28-damage kill.

**7. Red Mask's Weak expires before the enemy's first attack, so half the relic does nothing.** Byrdonis showed `Weak 1` at combat start and hit for its full printed 12; Vantom likewise hit for its full 5. A Weak applied during my own turn always worked (Shrinker Beetle 13→9, Byrdonis 12→9). Two data points, both negative; I could not force a third test. What the relic *does* reliably deliver is a free Casket ping and a Hydro aura on turn 0 — which is how it opened the boss (173→172) and gave my Electro cards something to react with.

**8. `Slow` makes card order, not card choice, the decision.** "Whenever you play a card, this enemy receives 10% more damage from Attacks this turn" was confirmed the first time I saw it — a Strike printed 6 dealt **7** as the third card played. Playing the same three cards in a different order changes a turn's damage by several points, and playing the biggest card last is correct. Combined with a Sleeping first turn and Battle Plan's +1 energy, this produced the run's biggest round: **107 → 35, 72 damage**.

**9. A potion reward is unclaimable when slots are full, and the screen's own advice cannot be followed.** The refusal read "your potion slots are full: 3 of 3 … **Use one first**, or leave this on the screen", but a reward screen's grammar is only `choose` / `proceed` — there is no `use potion` form there. I lost a **Regen Potion** at 24/80 HP (the most useful item offered all act) and later a **Snecko Oil**. The workaround is entirely non-obvious: spend a potion *during the fight* so a slot is open when the reward appears. I only learned it by accident, when spending Vulnerable Potion on Byrdonis happened to free the slot that let me claim Stable Serum.

**10. Starting gold is never printed.** 140 appeared at the shop against 41 shown in rewards. A player budgeting from reward screens alone would have mis-planned every shop.

**11. Smaller, unresolved.** The Casket ping dealt **1** to each of three Inklets but **2** to Byrdonis and to both floor-14 enemies — I could not tell why. **Strike Dummy** boosted Slack Water (4→7) despite no "Strike" in its printed name. And the first rest granted **29 HP** where it promised 24, because the Humidifier's Max HP bump silently carried current HP with it.

**Where I could not tell:** whether Block absorbs Constrict (both orderings produce the same HP); whether Slippery began at 7 or 8; whether the Casket fires once per enemy or once per application on a multi-enemy board; and why all four Wrigglers died on the turn I predicted one would survive at 1 HP.

---

## Identity (completed)

- **Model / seat:** Claude Opus, blind TESTER seat, round 5, run 3, first of three chained seats.
- **Lane:** 1. **Character:** KLEEMOD-KOKOMI.
- **Run seed:** **never printed.** No screen in the run displayed a seed.
- **Act:** 1. Boss as named by the map: **Vantom** (defeated). Act 2's boss is named **The Insatiable**.
- **Actions accepted:** **223**. **Refused: 1** (attempting to claim the Regen Potion with full potion slots).
- **Termination reason:** **stop condition (1)** — the act-1 boss was resolved and its reward screen handled; the lane stands on the act-2 map screen. Budget was not exhausted (223 of 250).
- **Where the run stands:** act-2 map screen, one node available (`Ancient (path 1)`), 16 floors to `The Insatiable`. Nothing is mid-screen; no reward or choice is pending.

**HP trajectory — every reading the screens printed, in order:**

64/80 → 64 → 62 → 58 (fight 1) → 58 → 55 → 55 (fight 2) → 55 → 46 → 40 (fight 3) → 40 → 37 → 24 (fight 4) → 24 → 24 → 21 → 21 (elite 1) → 21 → 21 → 18 (fight 5) → **18/80 at the rest site → 47/85** → 47 → 35 → 28 (elite 2) → 30/85 → 30 → 27 (fight 6) → 28/85 → 26 → 26 (elite 3) → 28/85 → 28 → 25 (fight 7) → **25/85 at the rest site → 55/90** → 57/90 → 52 → 42 → 42 → 42 → **39/90** (boss round 6, the last HP the screens printed).

Max HP rose 80 → 85 → 90 across two rests (Stone Humidifier). The lowest point of the run was **18/80**, immediately before the first rest.

**Gold:** the only running total any screen ever printed was at the shop — `You have 140 gold`, then `25` after buying. Claimed since: 20 + 42 + 11 + 44 + 20 + 44 + 10 + 100 = 291, giving **316** by my own count. No screen has confirmed it.

**Potions (3 of 3):** `Gambler's Brew — Discard any number of cards, then draw that many.` · `Skill Potion — Choose 1 of 3 random Skill cards to add into your Hand. It's free to play this turn.` · `Explosive Ampoule — Deal 10 damage to ALL enemies.`
Spent during the act: Vulnerable Potion (Byrdonis), Stable Serum (Bygone Effigy). Lost unclaimed to full slots: Regen Potion, Snecko Oil.

**Relics, exactly as printed:**

- **Tamakushi Casket** — Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy.
- **Stone Humidifier** — Whenever you Rest at a Rest Site, raise your Max HP by 5.
- **Oddly Smooth Stone** — Start each combat with 1 Dexterity.
- **Red Mask** — At the start of each combat, apply 1 Weak to ALL enemies.
- **Blood Vial** — At the start of each combat, heal 2 HP.
- **Strike Dummy** — Cards containing "Strike" deal 3 additional damage.

**Deck as reconstructed from faces printed in hand — 22 cards:**

| # | Card | Printed face (final, with relics live) |
|---|---|---|
| 4 | Strike | cost 1, attack — Deal 9 damage *(6 base + Strike Dummy)* |
| 4 | Defend | cost 1, skill — Gain 6 Block *(5 base + Dexterity)* |
| 2 | **Sango Isshin** [Hydro] | cost 2, attack — Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead *(= 22 at Max HP 90)* |
| 1 | Slack Water [Hydro] | cost 1, attack — Deal 7 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies |
| 1 | Kurage's Oath | cost 1, skill — Play on the Bake-Kurage. Plan: Deal 7 damage to ALL enemies |
| 1 | Ambush | cost 1, skill — Play on the Bake-Kurage. Plan: Deal 12 damage |
| 1 | Battle Plan | cost 1, skill — Play on the Bake-Kurage. Plan: Gain 1 Energy and draw 2 cards |
| 1 | Read the Field | cost 1, skill — Gain 6 Block. Plan: Gain 10 Block |
| 1 | Coral Bulwark | cost 1, skill — Gain 7 Block. Plan: Gain 8 Block and apply 1 Weak |
| 1 | Treatise | cost 1, power — Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card |
| 1 | Gorou — Inuzaka All-Round Defense | cost 1, attack — Deal 8 damage. Gain Block equal to half the damage dealt *(Geo: Crystallize)* |
| 1 | Shinobu — Sanctifying Ring | cost 1, skill — Lose 3 HP. For 3 turns, at the end of your turn deal 5 Electro damage to ALL enemies and gain 5 Block. Exhaust |
| 1 | Shinobu — Thundergrust [Electro] | cost 1, attack — Deal 8 damage. If you are below half HP, deal 5 additional damage |
| 1 | Thoma — Blazing Barrier | cost 1, skill — Gain 7 Block. Whenever this Block absorbs damage, gain 3 Block |
| 1 | Kirara — Surprise Dispatch | cost 1, skill — Gain 9 Block. Next turn, deal 10 damage to a random enemy |

Vantom added two unplayable `Wound` status cards during the boss fight; I saw no screen after combat that would show whether they persist, so I cannot say whether the deck is 22 or 24.

**Record of combats:** 11 fought, 11 won — 7 monster rooms, 3 elites, 1 boss. Zero deaths, no potion spent outside the two noted. The three elites cost 3, 19 and **0** HP respectively; the 127 HP Bygone Effigy never landed a hit.

---

## Non-blindness declaration

- **Commands run:** only the two permitted forms, `GITS_LANE=1 python -m understudy.blindplay observe` and `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, from the repo root. No other `understudy` subcommand was invoked — no `harness`, `session`, `audit`, `notes`, `scenario`, `staged_turn`, `soak`, `embark`. No `git`. The lane was never launched, closed, restarted or torn down, and lane 2 was never touched.
- **Shell usage beyond those two commands:** one `mkdir -p` to create this record's directory; `cat >>` appends to write this file; and `sed -n` filters applied to `observe` output to trim it. Nothing else.
- **Tools used:** Bash (for the two commands above, the record appends and the one `mkdir`) and Write (to create this record file and one scratch fragment of its own text under the session scratchpad). No other tool.
- **Repo files read: none.** No source, YAML, docs, rulings, backlog, or earlier records were opened at any point. Everything in this document comes from what the two commands printed to me.
- **Identifiers minted: none.** No file was edited other than this record.
- **Refusals: 1**, quoted in full in the Wellspring section.
- **The lane is left standing** exactly where play stopped: lane 1, act-2 map screen, one node available (`Ancient (path 1)`), no pending reward, choice or prompt.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
