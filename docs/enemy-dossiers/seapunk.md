# Seapunk — behavior dossier

- **Class:** `Seapunk`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounters:** `SeapunkWeak` (solo Seapunk; flagged as a *weak* encounter, i.e. the early-act pool) and `SeapunkNormal` (Calcified Cultist + Seapunk, in that spawn order)
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Seapunk runs a **three-state, fully deterministic loop with no randomness**. There is no roll, no HP threshold, no enrage, no first-turn special case: the move machine starts on Sea Kick and each state hard-wires its own successor.

1. **Sea Kick** — single attack. Intent: attack (one number).
2. **Spinning Kick** — multi-attack, 4 hits of a small number. Intent: attack ×4 (the multi-hit intent format).
3. **Bubble Burp** — gains block on itself, then applies Strength to itself. Intent: **buff + defend shown together**, so the player can see both halves of the move coming.

Then straight back to Sea Kick. The cycle is **attack → multi-attack → buff/block**, repeating for the whole fight.

| Enemy turn | Move | Effect |
| --- | --- | --- |
| 1 | Sea Kick | single hit |
| 2 | Spinning Kick | 4 small hits |
| 3 | Bubble Burp | block + Strength to self |
| 4 | Sea Kick | single hit, now Strength-boosted |
| 5 | Spinning Kick | 4 hits, each Strength-boosted |
| 6 | Bubble Burp | more block, more Strength |
| … | … | pattern repeats indefinitely |

Because the successor of each state is fixed, the intent shown is always the next step of that cycle, and a player who has seen the fight once knows every future turn of it.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 44–46 | 47–49 (Tough Enemies) |
| Sea Kick damage | 11 | 13 (Deadly Enemies) |
| Spinning Kick damage | 2 per hit | 2 (unscaled) |
| Spinning Kick hit count | 4 | 4 (unscaled) |
| Bubble Burp block | 7 | 8 (Tough Enemies) |
| Bubble Burp Strength | +1 | +2 (Deadly Enemies) |

HP is rolled inside the band, preferring a value not already used by another enemy on its side where the band allows (this matters in `SeapunkNormal`, where a 38–41/39–42 Calcified Cultist sits next to it).

Strength applies **per hit**, so the two attacks scale at very different rates off the same buff. The resulting damage-per-turn curve, assuming the Seapunk is never interfered with:

| Enemy turn | Move | Base damage | Ascension (Deadly + Tough) |
| --- | --- | --- | --- |
| 1 | Sea Kick | 11 | 13 |
| 2 | Spinning Kick | 2×4 = **8** | 2×4 = **8** |
| 3 | Bubble Burp | 0 (block 7, Str→1) | 0 (block 8, Str→2) |
| 4 | Sea Kick | 12 | 15 |
| 5 | Spinning Kick | 3×4 = **12** | 4×4 = **16** |
| 6 | Bubble Burp | 0 (block 7, Str→2) | 0 (block 8, Str→4) |
| 7 | Sea Kick | 13 | 17 |
| 8 | Spinning Kick | 4×4 = **16** | 6×4 = **24** |
| 9 | Bubble Burp | 0 (Str→3) | 0 (Str→6) |
| 10 | Sea Kick | 14 | 19 |
| 11 | Spinning Kick | 5×4 = **20** | 8×4 = **32** |

Cumulative unmitigated damage across the first nine enemy turns: **72 base / 93 at the ascension tiers.** Every third turn is a free turn for the player in exchange for a permanently steeper curve.

## Gimmicks

- **The buff is the clock.** Bubble Burp is the only thing that changes over the fight, and it changes both defense and offense at once. Each cycle adds +1 Strength (+2 at Deadly Enemies) *and* 7–8 block. Every three turns the fight gets both harder to kill and harder to survive.
- **Strength multiplies through a 4-hit attack.** Spinning Kick starts as the *weakest* move on the board (8 total) and becomes the *strongest* by turn 5 base / turn 5 ascended, because each point of Strength is worth 4 damage on it. It crosses Sea Kick permanently after the first Bubble Burp at ascension, and after the second one at base. Deadly Enemies effectively doubles the slope: +8 damage per cycle on Spinning Kick instead of +4.
- **Four small hits punish thin block and Thorns-shaped defenses in opposite directions.** Each hit is resolved against block separately, so a single 8-block card eats the whole early Spinning Kick, while any per-hit retaliation triggers four times. Once Strength is stacked, the same move stops being chip damage and starts one-shotting a partial block wall.
- **The Seapunk blocks itself.** Unlike most Act 1 normals, it has real mitigation on a third of its turns. Burst that lands on the Bubble Burp turn is partly wasted; burst that lands on an attack turn is not. This creates an actual timing decision for a big single hit, and rewards damage that ignores or strips block.
- **No debuffs at all.** It never applies Weak, Vulnerable, Frail, or anything else to the player. All of its pressure is raw damage on a rising curve.
- **In `SeapunkNormal`, both enemies are buff-engines on different clocks.** The Calcified Cultist's opening move grants itself Ritual (+2 Strength every turn thereafter) and it then attacks every turn for 9 (11 at Deadly Enemies). The Cultist's Strength curve is *steeper* (every turn) but rides a single-hit attack; the Seapunk's is slower but multiplied by four. The standard read is to kill the Cultist first and the Seapunk's own scaling is what punishes you for taking too long doing it.

## Scaling by act / ascension

- **Act:** none. Seapunk is Act 1-only content, and none of its numbers read the act index. The act index enters only through the multiplayer scaler below (Act 1 factor = 1.1).
- **Ascension:**
  - *Tough Enemies* tier: HP band 44–46 → **47–49**; Bubble Burp block 7 → **8**.
  - *Deadly Enemies* tier: Sea Kick 11 → **13**; Bubble Burp Strength +1 → **+2**. The Strength change is the important one — it is a *slope* change, not a flat bump, and it compounds through the 4-hit move for the rest of the fight.
  - Spinning Kick's base damage (2) and hit count (4) are **not** ascension-scaled at all; the entire ascension increase to that move arrives via Strength.
  - The move cycle itself is identical at every ascension.

## Multiplayer / seat-count adjustments

- **HP scales per seat.** On combat entry, monster max HP is multiplied by (player count × act factor), the Act 1 factor being **1.1**. A 2-player Seapunk sits at roughly **97–108 HP** and a 3-player one at roughly **145–162**. Its damage numbers do **not** scale.
- **Block scales per seat too, and this is the sharper edge.** Enemy block gained from a monster move is multiplied by the same (player count × act factor), so Bubble Burp's 7–8 becomes roughly **15–18 at two seats** and **23–26 at three**. A move that is a minor speed bump solo becomes a genuine wall in co-op, once every three turns, on top of a body that already has double or triple HP.
- **Attacks hit every player.** Neither move picks a single target: with more than one valid target the attack resolves against all of them, so the full Sea Kick number and *all four* Spinning Kick hits land on each seat. Party-wide damage taken therefore scales linearly with seat count while the Seapunk's own damage-per-hit stays flat — the total incoming per enemy turn at three seats is 3× the solo table above.
- **Strength is on the Seapunk, not per-seat**, so the buff curve is unchanged; what changes is that each point of Strength is now worth 4 damage × player count across the party.
- Net effect: co-op stretches the fight (more HP, more block) while multiplying the damage the party eats per turn. The scaling curve is the same shape, just entered later and paid for by more people.

## Fight-class reasoning — `attrition`

Seapunk asks the same question every single turn and asks it a little harder each time: can you keep absorbing a damage number that grows by a fixed step every third turn, for as long as it takes to chew through 44–49 HP that is also gaining block. There is no burst turn to plan around — the largest single hit in the first six turns is 15 — and no puzzle to solve, since the cycle is deterministic and telegraphs everything; the demand is sustained mitigation and steady throughput, and the failure mode is being *slow*, not being caught out. It is not `spike` because no turn spikes: the multi-hit move opens as the fight's *smallest* number and only overtakes the single attack after two buff cycles. It is not `gimmick` (self-Strength on a fixed loop is a scaling dial, not a mechanic to be solved) and not `swarm` (one body, or two independent ones in the Cultist pairing); `mixed` would obscure that both of its attacks and its buff all point at the same single demand — survive the ramp, and out-race it.
