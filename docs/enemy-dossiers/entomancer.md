# Entomancer

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Entomancer` (`MonsterModel`)
- **Kind:** elite
- **Act:** Act 2 (the Hive; act index 1). One of that act's elite pool alongside `DecimillipedeElite` and `InfestedPrismsElite`.
- **Encounter:** `EntomancerElite` — a **solo** elite. The encounter's possible-monster list has exactly one entry and generation always emits one Entomancer with no slot override. No adds, no minions, no summon move.
- **Fight class:** `mixed`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What Entomancer is

A single bug-caller with a fixed three-move loop and no defensive options at all: it has no Block move, no heal, no summon, and no debuff application. Everything it does is either damage or self-buff.

Its identity lives in one power, **Personal Hive**, applied to itself on entering the room. The Hive punishes the player for *how* they deal damage rather than for how much: every instance of attack damage the Entomancer takes shuffles Dazed into the attacker's draw pile. The move cycle then ramps Strength on a fixed cadence, and because the signature attack is a seven-hit barrage, each point of Strength is worth seven damage.

So the fight is a stopwatch with a tax attached. The Entomancer gets meaningfully more dangerous every third turn, and the natural way to end it fast — many small attacks — feeds the Hive hardest.

## 2. Intent pattern / AI

The move state machine is a **fixed three-move loop with no branching and no RNG**. Each state's follow-up points at the next, and the third points back to the first. The machine is seeded on **Bees**, and the shared state-machine driver suppresses the first transition, so **turn 1 is always Bees**. The order never varies and cannot be perturbed by player action, killing an ally (there is none), or HP thresholds.

| Turn (mod 3) | Move | Intent shown | Effect |
| --- | --- | --- | --- |
| 1 | **Bees** | multi-attack (7×3) | 3 damage × 7 hits, ranged, one attack animation for the whole barrage |
| 2 | **Spear** | single attack | 18 damage |
| 3 | **Pheromone Spit** | buff | see §4.1 — grows the Hive, then Strength |

Read as a demand curve, the cadence is: **wall turn → spike turn → free turn**, repeating. The wall turn (Bees) is where player Block is maximally efficient, because 7 small hits chew through a block pile with no overkill waste. The spike turn (Spear) is where Block is least efficient and a single mitigation card either covers it or doesn't. The buff turn deals zero damage and is the party's designated push window — and it is also the turn the fight's difficulty permanently increases.

Intents are telegraphed one turn ahead as normal, so the pattern is fully readable from turn 2 onward. There is nothing to dodge; there are only turns to choose between blocking and racing.

## 3. Numbers

| Stat | Base | Tough Enemies (asc) | Deadly Enemies (asc) |
| --- | --- | --- | --- |
| Initial HP | 145 (min == max, no roll) | 155 | — |
| Spear damage | 18 | — | 20 |
| Bees damage per hit | 3 | — | 3 (unchanged) |
| Bees hit count | 7 | — | **8** |
| Bees total (Str 0) | 21 | — | 24 |
| Personal Hive starting stacks | 1 | — | — |
| Personal Hive cap (via Spit) | 3 | — | — |
| Strength per Spit | +1 below Hive cap, **+2 at cap** | — | unchanged |

Strength is additive **per hit**, so the Bees turn double-dips on every buff. Bees deals `(3 + Strength) × 7` (`× 8` at Deadly Enemies); Spear deals `18 + Strength`.

Projected solo, no-ascension timeline:

| Turn | Move | Strength before | Damage | Hive after |
| --- | --- | --- | --- | --- |
| 1 | Bees | 0 | 21 | 1 |
| 2 | Spear | 0 | 18 | 1 |
| 3 | Spit | 0 → 1 | 0 | 2 |
| 4 | Bees | 1 | 28 | 2 |
| 5 | Spear | 1 | 19 | 2 |
| 6 | Spit | 1 → 2 | 0 | 3 |
| 7 | Bees | 2 | 35 | 3 |
| 8 | Spear | 2 | 20 | 3 |
| 9 | Spit | 2 → 4 | 0 | 3 (capped) |
| 10 | Bees | 4 | 49 | 3 |
| 11 | Spear | 4 | 22 | 3 |
| 12 | Spit | 4 → 6 | 0 | 3 |
| 13 | Bees | 6 | **63** | 3 |

Damage per full 3-turn cycle: 39, then 47, then 55, then **71**, then 87. The slope *steepens* at turn 9, because once the Hive is capped the Spit stops splitting its payout and hands over the full +2 Strength. The fight is priced to end inside four cycles; a party that stalls past cycle 4 is fighting a materially different monster.

At Deadly Enemies the same table reads 24 / 32 / 40 / 56 / 72 on the Bees turns and 20 / 21 / 22 / 24 on the Spears — the eighth bee makes every Strength point worth +8 instead of +7, so ascension changes the ramp slope, not just the baseline.

## 4. Gimmicks

### 4.1 Pheromone Spit — the two-stage buff

Spit checks the Entomancer's own Personal Hive stack count and branches:

- **Hive below 3:** +1 Personal Hive **and** +1 Strength.
- **Hive at 3 or above:** +2 Strength (Hive is not raised further).

Since the Hive starts at 1, the sequence over successive Spit turns is: Hive 2 / Str +1 → Hive 3 / Str +1 → Str +2 thereafter, forever. There is no cap on Strength.

The branch matters for modelling: the *first two* Spits split their value between "you take more damage" and "your deck gets worse", and every Spit after that is pure damage ramp. Any effect that removes the Entomancer's Hive stacks would, perversely, put the buff turn back into the weaker branch — but nothing in the kit reduces its own stacks, and this is the only place the Hive count is read for anything other than the Dazed payload.

### 4.2 Personal Hive — Dazed on being attacked

Applied to itself at 1 stack on entering the room, before the first turn.

**Trigger:** the Entomancer receives damage where the damage is flagged as *attack damage* — the flag that marks damage originating from Attack cards and from creatures attacking. It fires **after** the damage resolves, per damage instance.

**Payload:** the player who dealt the damage gets **N Dazed** created and shuffled into their **draw pile at random positions**, where N is the current Hive stack count (1, then 2, then 3). The addition is previewed to the dealer, with a short pause.

Dazed is a cost -1 Status card with **Ethereal** and **Unplayable**. It cannot be played, and it exhausts itself at end of turn if drawn — so the cost is drawn cards and tempo, not permanent deck rot within the combat.

Consequences worth carrying into any model of this fight:

- **It is per damage instance, not per card.** A multi-hit attack card triggers the Hive once per hit. At Hive 3, a 4-hit attack card injects **12** Dazed into that player's draw pile. Multi-hit decks — exactly the archetype that best exploits an enemy with no Block — pay the steepest tax here, and pay it worst late, when both the Hive and their own scaling are maxed.
- **Only attack damage counts.** Damage flagged unpowered — relics, potions, and powers, which is where Poison-style and Thorns-style chip lives — does **not** trigger the Hive, and neither does unblockable HP-loss damage. A poison or power-based damage plan walks through this elite paying nothing at all. That is the single largest build-dependent swing in the fight.
- **The Dazed goes to the dealer, not to everyone.** Attribution is per-player, and pet damage is redirected to the pet's owner (the Osty pet is explicitly re-attributed to its owner's creature) so a pet cannot launder the tax.
- **Draw pile, random position.** The Dazed do not clog the current hand; they surface over the following turns, which means the punishment lands one or two turns after the burst that earned it — usually right on top of the next Bees turn.

### 4.3 No defense whatsoever

The Entomancer never gains Block, never heals, and applies no Weak/Frail/Vulnerable. Whatever damage the party can deliver, it lands. The only thing standing between the player and the health bar is the Dazed tax on the *method* of delivery.

## 5. Scaling by act / ascension

- **By act:** none. Entomancer appears only in Act 2's encounter pool and has no per-act variant. The act index matters only through the multiplayer HP scaling constant (§6).
- **By ascension:** two gates, both binary.
  - *Tough Enemies*: HP 145 → 155.
  - *Deadly Enemies*: Spear 18 → 20, Bees hit count 7 → 8 (per-hit damage stays 3). Personal Hive stacks, the Hive cap, and the Spit's Strength payout are unchanged.
  - *Swarming Elites* is a run-structure ascension — it raises the number of elite rooms on the map by 60% — and does not touch this monster's stats, but it does raise how often the party meets it.

## 6. Multiplayer / seat count

- The encounter spawns exactly **one** monster at any seat count. Headcount is absorbed by HP, not by adds.
- **HP** is multiplied by `player count × act constant`; Act 2's constant is **1.2**. So Entomancer is 145 solo, **348** at 2 players, **522** at 3, **696** at 4 (Tough Enemies raises the base to 155 first: 372 / 558 / 744).
- **Block scaling does not apply** — the monster has no Block move to scale.
- **Damage is NOT divided among seats.** Both attacks target *all opponents*. Every player independently eats the full Bees barrage (7×3, or 8×3 at Deadly) and the full Spear, each modified by their own defensive powers. Party-wide incoming damage per cycle therefore scales linearly with seat count while the HP pool scales at `players × 1.2` — a slightly worse trade for the party than the raw HP number suggests.
- **The Hive tax is per-seat and additive across seats.** Each player who attacks gets their own Dazed, so a 4-player party at Hive 3 generates up to 12 Dazed per round from four single-hit attacks alone — the total deck pollution scales with the party while the Hive counter does not. This is the one place co-op is meaningfully harder than the HP math implies.
- Correspondingly, in co-op the Hive rewards **designating a hitter**: concentrating damage into one seat's big single hits, with the other seats blocking or using unpowered damage sources, keeps the total Dazed count down. Nothing enforces this — it is a coordination skill check that does not exist solo.

## 7. Proposed fight class: `mixed`

Per turn, the fight demands three different things on a rotating three-beat cadence, and no single bucket covers them. The Bees turn is a **wall** turn where broad, cheap Block is maximally efficient against seven small hits; the Spear turn is a **spike** turn where a single 18–22 point hit either gets covered or gets eaten; the Spit turn deals nothing and is a pure push window whose price is a permanent ramp. That alone is a spike/attrition hybrid on a fixed clock.

The Personal Hive then adds a demand that never appears in an incoming-damage curve at all: the player must choose *how* to deal damage, not just how much. Multi-hit attack packages are taxed per hit and get buried in Dazed; unpowered damage — poison, thorns, relics, powers — pays nothing. That is a genuine gimmick axis, and it is build-dependent enough that two parties with identical damage-per-turn can experience completely different fights.

`mixed` is the honest label. A Track B demand curve for this elite should carry a **steepening** attrition baseline (39 → 47 → 55 → 71 damage per cycle, slope increasing at cycle 4 when the Hive caps), a periodic single-target spike overlay every third turn, and a separate deck-quality cost term keyed to the player's hit count rather than to turns elapsed.
