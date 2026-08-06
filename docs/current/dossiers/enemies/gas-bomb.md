# Gas Bomb — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `GasBomb`
- **Kind:** normal (non-elite, non-boss) — but never a starting body
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounters:** `LivingFogNormal` only. The encounter *generates* a single Living Fog in the `livingFog` slot; the Gas Bomb is listed among the encounter's possible monsters purely so its assets preload. Every Gas Bomb you ever fight is **summoned mid-combat** by the Living Fog's Bloat move into one of five reserved slots (`bomb1`…`bomb5`).
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Gas Bomb has the simplest state machine in the roster: **one state, one move, no transitions, no RNG.**

- **Explode** — a *Death Blow* intent (its own distinct intent icon, not the ordinary attack icon). Deals its damage to **every** player creature, then **kills itself**. The self-kill is unconditional and immediate; the bomb never survives its own move.

Because there is only one move state and the state machine is forbidden from transitioning away before the first move is performed, the bomb telegraphs Explode from the instant it appears and can never telegraph anything else. There is no idle turn, no wind-up variant, no HP-threshold branch.

**Timing is the whole enemy.** The bomb is created during the Living Fog's Bloat move — i.e. on the enemy turn — so it does not act on the turn it spawns. It sits with Explode telegraphed through exactly **one player turn**, then detonates at the start of the next enemy phase. The player therefore always has precisely one turn, and only one turn, to remove 7 HP.

Combined with the Living Fog's own fixed cycle (Advanced Gas → Bloat → Super Gas Blast → Bloat → Super Gas Blast → …), a bomb arrives on the Fog's **turn 2 and every second turn thereafter**, and detonates on the odd turns alongside Super Gas Blast. Steady state, if the bombs are never killed:

| Enemy turn | Living Fog | Bomb | Party takes |
| --- | --- | --- | --- |
| 1 | Advanced Gas (8) + Smoggy debuff | — | 8 + card affliction |
| 2 | Bloat (5) + summon bomb | (spawns, telegraphs) | 5 |
| 3 | Super Gas Blast (8) | **Explode (8)** | **16** |
| 4 | Bloat (5) + summon bomb | (spawns) | 5 |
| 5 | Super Gas Blast (8) | **Explode (8)** | **16** |

So the bomb converts a flat ~8/turn fight into a **5 / 16 / 5 / 16 sawtooth**, and the player's answer is to spend 7 damage on the off-turn to flatten it back down.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP | **7** (fixed) | **8** (*Tough Enemies* tier) |
| Explode damage | **8** | **9** (*Deadly Enemies* tier) |
| Block | none — no block move, no defensive power | — |

Min and max initial HP are the **same value**, so unlike most multi-body enemies the Gas Bomb gets no per-body HP roll and no "distinct HP per creature" spread: every live bomb sits on the identical number. That is a deliberate legibility choice — the kill threshold is a constant the player can memorise, and a single card either clears a bomb or does not.

The bomb has **no attack other than Explode, no block, no debuff application, and no powers** except the Minion tag below. It contributes nothing to the enemy side while alive; its entire value to the Fog is the threat of the pending detonation.

Damage exchange rate for the player: **7 HP removed (8 on Tough) buys 8 damage prevented (9 on Deadly)** — and the bomb dies to its own move anyway, so killing it is never "wasted" damage against the fight's real HP pool… which is exactly the trap, see below.

## Gimmicks

- **Death Blow / suicide attack.** Explode is flagged with a dedicated *Death Blow* intent so the player can distinguish "this thing will hit you once and leave" from a recurring attacker. It also means the bomb has a **death animation branch**: it only plays the ordinary death animation if it has *not* exploded, so a bomb the player killed and a bomb that detonated read differently on screen.
- **Minion / secondary enemy.** The bomb carries a Minion power on spawn, which marks it a *secondary* enemy. Consequences:
  - **Killing the Living Fog kills every live bomb instantly.** When the last primary enemy dies and only secondary enemies remain, they are all killed automatically. Any telegraphed Explode is cancelled. Racing the Fog is therefore a legitimate way to ignore the entire gimmick.
  - The bomb's death is **not fatal to the encounter** — it never counts as the fight-ending kill.
- **Damage spent on bombs does not shorten the fight.** The Fog is an 80–82 HP primary; every point sunk into a 7 HP bomb is a point not sunk into that pool, and the Fog will simply summon another one two turns later. The bomb is a **recurring toll**, not an objective. The player's real decision each cycle is: pay 7 damage to avoid 8, or eat the 8 and put the 7 into the Fog to end the loop sooner. The exchange rate is deliberately set just barely in the player's favour so that neither line is obviously wrong.
- **Five-slot cap.** The encounter reserves five bomb slots, and the summon quietly does nothing if no slot is free — the Bloat move still deals its damage. In practice the cap is unreachable: the Fog summons exactly one bomb per Bloat, and each bomb removes itself on the following enemy turn, so at most one bomb is alive at a time and the slots exist for edge cases (e.g. a bomb whose detonation was prevented, or effects that delay enemy turns).
- **Interaction with the Fog's debuff.** The Fog's Advanced Gas applies Smoggy, which afflicts the player's *skills* with Smog when a skill is played. That pushes the player toward attacks — which is also what clearing bombs requires — so the two halves of the encounter point the same direction rather than fighting each other.
- No summons of its own, no revive, no scaling counter, no enrage. The list above is the whole kit.

## Scaling by act / ascension

- **Act:** none. Gas Bomb is Act 1 content, reachable only through the Living Fog encounter, and its numbers do not read the act index. The only act-derived factor that touches it is the multiplayer HP scaler below (act index 0 → ×1.1).
- **Ascension:** two independent, tier-keyed bumps, one on each side of the exchange.
  - *Tough Enemies* tier: HP 7 → **8**.
  - *Deadly Enemies* tier: Explode damage 8 → **9**.
  - Both matter more than +1 usually does, because the whole enemy is a threshold: the HP bump can push the bomb out of one-card-clear range for a given deck, and the damage bump raises the price of failing to clear it. At the top tier the trade is **8 HP for 9 damage** — still favourable, but the fight's per-turn tax has gone up on both axes.
  - Summon rate, summon count (always one per Bloat), and the one-turn fuse are **not** ascension-scaled.

## Multiplayer / seat-count adjustments

- **HP scales by seats, including on mid-combat spawns.** HP scaling is applied at creature-creation time, so bombs summoned during the fight are scaled exactly like starting bodies: base HP × player count × act factor (**1.1** in Act 1). A 2-player bomb sits around **15** HP and a 3-player bomb around **23** (about **18 / 26** at the Tough-Enemies tier). Note this is *worse than proportional* — the ×1.1 means the party pays a 10% premium per bomb relative to solo.
- **Explode damage does not scale, but it is applied per seat.** Monster attacks hit **all** player creatures rather than picking one, so every player takes the full 8 (9 at the Deadly tier). Per-seat incoming damage is identical to solo; total party damage prevented by a kill is 8 × seats.
- **The block scaler is inert here** — the multiplayer system inflates enemy block from monster moves, and the Gas Bomb has no block move.
- **Net effect: co-op sharpens the ultimatum into a coordination problem.** Solo, 7 HP is a single card off the top of almost any hand. At three seats, ~23 HP inside one turn is a real commitment that usually needs contributions from more than one player, and a party that *partially* chips the bomb has wasted everything it spent — the detonation is all-or-nothing. Meanwhile the payoff scales the other way (24 damage prevented across three seats), so the bomb becomes both more expensive and more important, and the party has to agree in advance whose turn pays the toll.

## Fight-class reasoning — `gimmick`

What the Gas Bomb demands per turn is not damage output or survivability but a **binary threshold decision on a one-turn fuse**: remove exactly 7 HP this turn, or take 8 to every seat. Nothing about the body is a threat in itself — it has one move, no block, no debuffs, and it dies whether or not you touch it — so `spike` overstates an 8-damage hit and `attrition` misreads a creature that contributes zero on every turn but one. The mechanic that sets the demand curve is the **toll structure**: damage spent on the bomb does not shorten the fight, the Fog reissues the bill every other turn, and killing the primary cancels every outstanding bomb at once, which means the player is really being asked each cycle whether to pay the toll or race past it. `swarm` is the near-miss — five slots and a low-HP body look swarm-shaped — but bombs are issued one at a time and remove themselves, so the fight never presents a body count to sweep; it presents the same yes/no question on a timer, which is the signature of `gimmick`.
