# Gremlin Merc — behavior dossier

- **Class:** `GremlinMerc`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounter:** `GremlinMercNormal` — at combat start the board holds **only** the Merc (slot `merc`). Fat Gremlin (`fat`) and Sneaky Gremlin (`sneaky`) do not exist until the Merc dies.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Merc runs a **fixed three-move cycle with no randomness and no conditionals**. There is no roll, no HP threshold, no first-turn special case, and no "can't use twice in a row" rule — the three move states point at each other in a ring and it walks that ring forever:

**Gimme → Double Smash → Hehe → Gimme → …**

| Turn | Move | Intent icons shown | Effect |
| --- | --- | --- | --- |
| 1, 4, 7, … | **Gimme** | Multi-attack (2 hits) | 7 damage × 2, then steals gold. First time only, it speaks a banter line before attacking (a short cosmetic beat, no mechanical effect). |
| 2, 5, 8, … | **Double Smash** | Multi-attack (2 hits) + Debuff | 6 damage × 2, steals gold, then applies **Weak 2** to its targets. |
| 3, 6, 9, … | **Hehe** | Single attack + Buff | 8 damage, steals gold, then gives **itself +2 Strength**. |

Because the cycle is rigid and the buff lands on the last beat of it, damage climbs in a perfectly predictable staircase. Every full 3-turn lap adds +2 Strength, which is +2 to Hehe, **+4 to Gimme** and **+4 to Double Smash** (2 hits each). The player can compute the whole fight from turn one.

Projected output at base numbers (single player, Strength applied per hit):

| Lap | Gimme | Double Smash | Hehe | Lap total |
| --- | --- | --- | --- | --- |
| 1 (turns 1–3) | 14 | 12 | 8 | 34 |
| 2 (turns 4–6) | 18 | 16 | 10 | 44 |
| 3 (turns 7–9) | 22 | 20 | 12 | 54 |
| 4 (turns 10–12) | 26 | 24 | 14 | 64 |

Note that Weak 2 lands on the *second* turn of every lap, so the Weak is live for Hehe and for the following lap's Gimme unless cleansed — the fight's own debuff partially offsets its own Strength staircase from the player's side of the exchange.

## Numbers

| Value | Base | Tough-Enemies tier |
| --- | --- | --- |
| Starting HP roll | 47–49 | 51–53 |
| Gimme | 7 damage × 2 hits | 8 × 2 |
| Double Smash | 6 damage × 2 hits, then Weak 2 | 7 × 2, then Weak 2 |
| Hehe | 8 damage, then +2 Strength to self | 9, then +2 Strength |
| Block gained | **none** | none |
| Strength gained per lap | +2 | +2 (not ascension-scaled) |
| Gold stolen, per player, per move | up to 20 | unchanged |

It has **no block, no heal, no summon-on-timer, no enrage threshold, and no artifact**. Its entire defensive profile is its HP bar; its entire offensive escalation is the +2 Strength every third turn.

Its two successors, for the death-phase math:

| Successor | HP (base / Tough) | Behavior |
| --- | --- | --- |
| Sneaky Gremlin | 10–14 / 11–15 | One stunned spawn turn, then **9 damage** (10 at Deadly Enemies) every turn, forever. |
| Fat Gremlin | 13–17 / 14–18 | One stunned spawn turn, then **escapes permanently**. Deals no damage ever. Carries the stolen gold. |

## Gimmicks

- **It is a thief, and the theft is the fight.** On entering the room it applies a **per-player** thievery counter worth 20 gold. **Every one of its three moves** — not just Gimme — triggers a steal, taking up to 20 gold from each player (capped at what that player actually holds) and banking the running total on the counter. A Merc that lives four turns has taken up to ~80 gold per seat.
- **Its death does not end the fight.** It enters combat carrying a "surprise" buff whose entire job is to (a) block combat from resolving and (b) fire on its death. When it dies, the buff spawns a **Sneaky Gremlin** and a **Fat Gremlin** on the empty board. The fight the player thought they had won becomes a second, different fight.
- **The stolen pot transfers to the Fat Gremlin.** Each player's banked amount moves onto the Fat Gremlin as a per-player "heist" counter tagged to its victim. Kill the Fat Gremlin before it flees and each player is refunded their exact stolen amount as an extra gold reward (logged in run history as loot returned); let it escape and that gold is gone.
- **The room's own gold reward is hostage too.** The encounter overrides the standard rules: Fat Gremlin killed → **100%** of combat gold; Fat Gremlin escaped but nothing was ever stolen → **50%**; Fat Gremlin escaped *with* stolen gold → **0%**.
- **Kill timing is a genuine two-sided decision.** Every extra Merc turn is +20 gold per seat onto the pot *and* moves the Merc closer to its next +2 Strength. Killing it early caps both the loss and the prize; stalling it grows a pot you must then be able to burst down inside the Fat Gremlin's two-turn window (13–17 HP solo, ~29–37 at two seats) while a Sneaky Gremlin hits for 9 a turn. Rushing the kill with all your burst spent is the classic failure mode.
- **No forced targeting or protection mechanics** — no taunt, no minion-shield, no positional rule. The complexity is all in the timing and the reward line.

## Scaling by act / ascension

- **Act:** none. Act 1 content only; no number on this monster reads the act index. The only act-derived factor that touches it is the multiplayer scaler (Act 1 = 1.1).
- **Ascension:**
  - *Tough Enemies* tier raises **both** its HP band (47–49 → 51–53) **and, unusually, all three of its damage numbers** (7→8, 6→7, 8→9). Most enemies in this family put damage on the *Deadly Enemies* tier; the Merc's damage is on the Tough tier instead, so its whole profile steps up at once, one tier earlier than a reader would expect.
  - *Deadly Enemies* tier: **no effect on the Merc**. It does bump the Sneaky Gremlin's tackle 9 → 10 in the death phase.
  - The +2 Strength per lap, the Weak 2, the 20-gold steal, and the 3-move cycle are all **ascension-flat**.
  - Net at Tough tier: a lap goes 34 → 40 base damage before Strength, and HP goes up ~8%, so the fight lengthens and hits harder simultaneously.

## Multiplayer / seat-count adjustments

- **HP scales steeply.** On entering combat with more than one player, enemy max HP is multiplied by (player count × act factor); Act 1's factor is **1.1**. A 2-player Merc sits around **103–108 HP**, a 3-player one around **155–162**. Neither its damage nor its Strength gain scales — it is the same escalating attacker, kept alive twice or three times as long, which means the party eats **more full laps** and therefore more Strength ticks than a solo player facing the same monster.
- **Block scaling is irrelevant here** — it gains none, so the multiplayer block multiplier never applies to it.
- **The theft is explicitly per-seat.** A separate thievery counter is applied to each player at combat start, and every move drains **all of them**. A 3-player party loses up to 60 gold per Merc turn across the table, and all three pots land on the single Fat Gremlin.
- **Weak 2 hits the whole targeted side**, so Double Smash debuffs the party, not one seat.
- **Payback is per-victim, loss is collective.** Killing the Fat Gremlin refunds each player individually; letting it flee zeroes everyone's stolen gold *and* cuts the encounter's gold reward for the whole party.
- Because the Merc's HP roughly doubles/triples at 2/3 seats but the Fat Gremlin's escape window stays fixed at two turns, the co-op version of this fight is meaningfully harder on the reward line than the solo version: more gold stolen, a fatter target to burst, same clock.

## Fight-class reasoning — `gimmick`

Turn to turn the Merc's combat ask is unremarkable and fully deterministic — a 34-damage lap that grows by 10 each cycle, one Weak 2, no block to chew through — and a player who only reads the HP bars will beat it and still lose the room. The demand that actually defines the fight is **when** you kill it: every extra turn you allow is +20 gold per seat onto a pot that becomes either a refund or a total loss, and the Merc's death is a fake-out that converts the fight into a fixed two-turn burst check against a fleeing loot-carrier while a live attacker chips you. That is a resource/timing puzzle with information outside the health bars, not a damage race. `spike` is wrong because nothing it does is burst-shaped (its biggest single turn early is 14 across two hits); `attrition` is wrong because the deterministic Strength staircase makes it a *short* fight by design rather than a grind; `swarm` misreads a one-body opener whose adds only arrive post-mortem; and `mixed` would dilute the fact that one distinctive mechanic — steal, die, chase — governs every decision in the encounter.
