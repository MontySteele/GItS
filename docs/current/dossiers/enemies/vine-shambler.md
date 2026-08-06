# Vine Shambler — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `VineShambler`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounter:** `VineShamblerNormal` — a **solo fight**. The encounter generates exactly one Vine Shambler and nothing else; the class appears in no other encounter and no other act's encounter list. It is in the normal (not weak) pool, and it is not one of the fixed first-run rooms.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

A **fixed three-move loop with zero randomness**. The move machine is built from three move states chained head-to-tail:

- **Swipe** → follow-up is **Grasping Vines**
- **Grasping Vines** → follow-up is **Chomp**
- **Chomp** → follow-up is **Swipe**

Swipe is also the machine's initial state, and the machine will not transition away before the first move has been performed. There is no RNG call anywhere in this enemy's transition logic, no HP threshold, no enrage, no repeat guard, no alternate opener, and no state that can be skipped. The sequence from turn 1 is therefore:

**Swipe → Vines → Chomp → Swipe → Vines → Chomp → …** for the entire combat.

Intent display per move:

| Turn in cycle | Move | Intent shown |
| --- | --- | --- |
| 1 | Swipe | multi-attack (damage × 2 hits) |
| 2 | Grasping Vines | single-attack **plus a card-debuff icon** |
| 3 | Chomp | single-attack (the big number) |

The card-debuff icon on the Vines turn is the only non-attack marker the enemy ever shows, and it is the fight's tell. Resolution order on that turn is fixed: **damage first, then the debuff is applied.**

Animation-wise it is a lurching plant-thing with distinct cast/chomp/swipe/vines states; the swipe plays its animation once and lands two hits inside it, so the visual undersells the hit count relative to the intent number.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP | 61 (fixed — min = max, no roll) | **64** (Tough Enemies, A8+) |
| Swipe | 6 × 2 hits = 12 | **7 × 2 = 14** (Deadly Enemies, A9+) |
| Grasping Vines | 8, + Tangled 1 | **9**, + Tangled 1 |
| Chomp | 16 | **18** (Deadly Enemies) |
| Block | — | it never gains block, ever |

Damage per full three-turn cycle, before player-side modifiers: **36** base, **41** at the Deadly-Enemies tier — an average of 12.0 / 13.7 per turn, with the per-turn spread running 8 → 12 → 16 (9 → 14 → 18 ascended).

Cumulative incoming if wholly unmitigated: 12 / 20 / 36 / 48 / 56 / 72 by end of turns 1–6 (base); 14 / 23 / 41 / 55 / 64 / 82 ascended. Against a 61–64 HP body, a deck clearing ~12 damage/turn kills it on turn 5–6 and eats 56–72 in the process, which is why this fight is a real HP tax in Act 1 rather than a formality.

## Gimmicks

- **Tangled / Entangled — the one mechanic.** Grasping Vines applies a 1-stack Tangled debuff to the player. On application it afflicts **every Attack card the player owns in that combat** (draw, hand, discard, exhaust — the whole combat card pool) with *Entangled*, and it keeps afflicting **any new Attack card that enters combat** while it is up. An Entangled card costs **+1 energy** (the surcharge equals the Tangled stack amount). Non-Attack cards — skills, powers, block — are untouched.
- **It is a one-turn tax, not a stack.** Tangled removes itself at the end of the player side's turn, and removal clears the Entangled affliction from every card it marked. Because the loop re-applies it only every third turn and it self-expires first, it never accumulates past 1 in a solo fight — the surcharge is always exactly +1 energy.
- **The tax is deliberately aimed at the worst turn.** Vines lands at the end of the monster's turn; the player's *next* turn is both the turn where Attacks cost +1 **and** the turn where the intent reads Chomp (16/18). So on one turn in three, the player's offense is throttled precisely while the largest hit is telegraphed. That coupling is the whole design: the fight asks you to pivot to skills/block on the Vines→Chomp beat and to spend attacks freely on the other two.
- **No defense, no ramp, no summons.** No block move, no Strength gain, no scaling power, no minion spawn, no death rattle, no revive, no HP-threshold branch. Every point of its output is raw damage, and its only defensive tool is the energy it steals from your attack cards.
- **Grasping Vines' hit VFX is spawned on each creature at the base of the model** — the vines visually erupt under every target. Cosmetic, but it is the honest tell that the move is party-wide (see below).

## Scaling by act / ascension

- **Act:** none. Act 1 exclusively; nothing in the enemy reads the act index. The only act-derived factor that touches it is the multiplayer HP scaler (Act 1 factor = **1.1**).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* (A8+): HP 61 → **64**. Fixed value both ways — this enemy has no HP roll at all, so its kill deadline is exactly predictable at every ascension.
  - *Deadly Enemies* (A9+): all three moves bump together — Swipe 6→7 per hit (so 12→14 per turn, the largest absolute jump of the three), Vines 8→9, Chomp 16→18. Cycle damage 36 → 41, a ~14% increase.
  - **The Tangled application does not scale with ascension.** It is 1 stack (= +1 energy) at every level. The gimmick's severity is flat across the ladder; ascension only raises the damage floor and the kill deadline.

## Multiplayer / seat-count adjustments

- **HP scales hard.** Max HP is multiplied by (player count × act factor), Act 1 factor **1.1**, then truncated: 2 players ≈ **134** HP, 3 players ≈ **201**, 4 players ≈ **268** (at the Tough-Enemies tier: ≈140 / 211 / 281). The loop therefore runs roughly 2–3× as many cycles in co-op.
- **Damage does not split — it is charged per seat.** All three moves are built to target *all* opposing player creatures, with the valid-target list recomputed on every hit (so the Swipe's second hit re-resolves against whoever is still alive). Every player takes the full listed number every turn. Party-wide load per cycle is 36 × seat count at base, 41 × seat count ascended.
- **Tangled is applied to every target, not one.** Each seat gets its own 1-stack Tangled and its own Entangled surcharge on its own Attack cards, and each copy expires on its owner's turn end. The gimmick is seat-count independent in severity but universal in reach — there is no "one player eats it" mitigation, and no seat can play around it for the others.
- **Block scaling is irrelevant here** — the enemy gains no block, so the multiplayer block multiplier never fires on it.
- Net effect: co-op turns a ~5-turn solo race into a long grind against the same unchanging 3-beat loop, with the energy tax landing on the whole party on every third turn. The per-turn *demand* is unchanged; the number of turns you must meet it roughly triples.

## Fight-class reasoning — `mixed`

Per turn this fight demands two different things on a fixed rotation, and that is exactly what disqualifies the single-axis labels. Two turns in three it is pure throughput against a flat, no-block, no-ramp 61-HP body taking a steady 12–16 a turn — textbook `attrition`, and the honest skeleton of the encounter. But the third beat is a genuine mode switch: Tangled makes every Attack in your deck cost +1 on the same turn the 16/18 Chomp is telegraphed, so the correct play flips from "spend everything on damage" to "block with skills and ride it out," and a player who does not read the card-debuff icon gets caught holding unaffordable attacks in front of the biggest hit in the loop. `spike` overstates a 16-damage hit that is fully predictable from turn 1 and only 33% above the cycle average; `gimmick` overstates a one-stack, one-turn, non-scaling surcharge that never accumulates and cannot end the fight on its own. `mixed` is the label that carries both halves of the demand curve — sustained damage on two beats, defensive pivot with a throttled hand on the third.
