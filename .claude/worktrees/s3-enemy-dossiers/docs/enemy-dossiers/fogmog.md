# Fogmog

- **Class:** `Fogmog`
- **Kind:** normal
- **Act:** 1 (Overgrowth, act index 0)
- **Encounter:** `FogmogNormal` — two slots (`fogmog`, `illusion`), only Fogmog is generated at combat start; the `illusion` slot is reserved for the creature Fogmog summons
- **Fight class:** **gimmick**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

Fogmog is an ordinary Act 1 monster encounter, one of the twenty-two rooms in Overgrowth's encounter
pool. It is not in the fixed first-run tutorial ordering, so a player meets it only once the act is
generating rooms freely. The encounter has a dedicated background scene and always spawns exactly
one Fogmog; the second slot stays empty until turn 1 resolves. Its take-damage sound family is
"plant".

## Intent pattern

The move machine is a fixed opener followed by a small two-branch loop. There is no HP threshold, no
phase change, and the only randomness is a single 40/60 weighted branch.

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 (always) | **Illusion** | Summons an **Eye With Teeth** into the `illusion` slot | summon |
| 2 (always) | **Swipe** | Single attack, then **+1 Strength on itself** | attack + buff |
| 3 | branch | 60% → Headbutt, 40% → a second Swipe | — |

The branch's two exits then hard-point back into the loop:

- **60% path (2-turn loop):** Swipe → Headbutt → Swipe → branch …
- **40% path (3-turn loop):** Swipe → Swipe → Headbutt → Swipe → branch …

Structural consequences worth modelling:

- **Turn 1 is never an attack.** The opener is a pure summon; the player gets one free turn of setup
  and one free turn of damage against a 74/78 HP body before anything hits.
- **Headbutt never repeats back-to-back**, and there are never more than two Swipes in a row. The
  branch carries a cannot-repeat guard, but because the branch is only ever entered from a Swipe the
  guard is effectively inert — the practical distribution is a flat 40/60 each time the branch is
  reached.
- **Fogmog summons exactly once, ever.** Nothing in the machine routes back to the Illusion state, so
  there is only one Eye With Teeth for the whole fight (see Gimmicks — it does not stay dead).
- The branch's two hidden move states are suppressed from the bestiary so the entry lists Illusion,
  Swipe and Headbutt once each rather than duplicating them.

## Damage / HP numbers

Base values and the ascension variants:

| Stat | Base | Ascension |
|---|---|---|
| Fogmog HP (min = max, no roll) | **74** | **78** (A8 `ToughEnemies`) |
| Swipe damage | 8 | 9 (A9 `DeadlyEnemies`) |
| Swipe self-buff | +1 Strength, permanent | unchanged |
| Headbutt damage | 14 | 16 (A9 `DeadlyEnemies`) |
| Eye With Teeth HP | 6 | unchanged |
| Eye With Teeth output | 3 Dazed to each player's discard | unchanged |

Fogmog gains no block at any point and applies no debuffs to players. Its entire damage profile is
the two attacks plus its own accumulating Strength, which is simply a count of how many Swipes it has
thrown. Strength applies to both moves.

Base-difficulty solo projection, taking the 60% (two-turn) loop throughout:

| Turn | Fogmog | Damage to each player | Fogmog Strength after |
|---|---|---|---|
| 1 | Illusion | 0 | 0 |
| 2 | Swipe | 8 | 1 |
| 3 | Headbutt | 15 | 1 |
| 4 | Swipe | 9 | 2 |
| 5 | Headbutt | 16 | 2 |
| 6 | Swipe | 10 | 3 |
| 7 | Headbutt | 17 | 3 |
| 8 | Swipe | 11 | 4 |

Add 3 Dazed per turn from turn 2 onward on top of this. The ramp is linear and shallow — roughly
+0.58 Strength per turn in expectation (1.4 Strength per 2.4-turn loop) — so unlike a boss this fight
has no real clock; a stalled fight gets worse slowly rather than catastrophically. On A9 the same
table reads 9/17/10/18/11/19… : the shape is identical, shifted up.

## Gimmicks

### The Eye With Teeth (the whole fight)

A 6 HP minion summoned on turn 1 into the reserved slot. Three properties stack into the fight's
identity:

1. **It taxes draw every turn.** Its only move — repeated forever, it has a single self-looping state
   — puts **3 Dazed into every player's discard pile**. Dazed is a 0-cost Unplayable **Ethereal**
   status, so each copy self-destructs if it is sitting in hand at end of turn. The cost is therefore
   throughput, not permanent deck pollution: the player pays draw slots and tempo every turn, and the
   pile never permanently grows.
2. **It does not stay dead.** It carries an Illusion buff: when killed, it is *not* removed from
   combat. It plays a stun animation, spends its next turn on a revive move (shown as a heal intent)
   that restores it to full 6 HP, and cannot be hit or receive powers while reviving. It also keeps
   its buffs through death, and it is immune to the "doom"-style removal that clears other adds. So
   killing it buys **exactly one Dazed-free turn** for 6 damage, repeatable indefinitely — a tempo
   trade, never a solution.
3. **It is a minion, not a second boss.** It is flagged as a secondary enemy: its death does not
   trigger the fatal/victory check, and combat ends the moment Fogmog itself dies (the Eye's own
   death animation is gated on no primary enemy being alive). Damage spent on the Eye is damage not
   spent on the actual win condition.

The intended tension is exactly that: every turn the player chooses between 6 damage for one clean
draw step, or eating 3 Dazed and pushing the 74 HP race. AoE and multi-hit decks resolve this
trivially — they clear the Eye as splash while pressuring Fogmog — while single-target decks pay the
tax in full. This is the single largest deck-shape swing in the fight.

### Strength on the throttle move

The Strength buff rides on the *low* attack, not the high one, so the fight tightens fastest along
the branch path that hurts least in the moment. It is permanent and uncapped, but at ~0.58/turn it
only matters if the player is stalling, which is precisely what the Dazed stream encourages. The two
gimmicks are aimed at each other.

## Scaling

**By act:** none. Fogmog exists only in Act 1's pool; nothing on the model reads the act index except
through the shared multiplayer HP formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | Fogmog HP 74 → 78 |
| A9 `DeadlyEnemies` | Swipe 8 → 9; Headbutt 14 → 16 |

Neither ascension level touches the Eye With Teeth — its 6 HP and its 3-Dazed output are constant at
every difficulty. The gimmick load is therefore flat while the damage load rises, so the fight's
character shifts slightly toward a race at high ascension.

**By seat count (multiplayer):**

- **Fogmog's HP** uses the standard scale: base × players × **1.1** (the Act 1 multiplier; Act 2 and
  Act 3 non-boss rooms use 1.2).

| Players | HP (base 74) | HP (A8, 78) |
|---|---|---|
| 1 | 74 | 78 |
| 2 | ≈162 | ≈171 |
| 3 | ≈244 | ≈257 |
| 4 | ≈325 | ≈343 |

- **The Eye With Teeth does not scale at all.** It is created mid-combat by the summon move, and the
  multiplayer HP scale is applied only to creatures placed at encounter setup. It stays at 6 HP in a
  four-player game — the cheapest possible answer to the fight's main pressure, and the reason the
  gimmick gets *softer* per seat.
- **Both attacks are AoE.** Monster attacks default to targeting all opponents, so every seat takes
  the full Swipe/Headbutt number; there is no split and no target selection. Party-wide damage taken
  scales linearly with seats on top of the HP scale.
- **Dazed is per-seat and undivided:** every player receives their own 3 Dazed each turn, so the
  throughput tax is constant per player regardless of party size.
- Fogmog gains no block, so the multiplayer enemy-block multiplier never applies here.

## Proposed fight class: **gimmick**

What this fight demands per turn is a *target-priority decision*, not a defensive or offensive check:
the incoming damage is a modest, shallowly escalating 8–17 that most Act 1 decks can absorb or block
without special preparation, and 74 HP is not a race anyone loses on numbers. The real question each
turn is whether to spend 6 damage resetting a minion that always comes back for one turn of clean
draw, or to accept 3 Ethereal Dazed and keep pressure on the actual win condition — and the answer
swings hard on deck shape, since AoE or multi-hit decks solve it for free while single-target decks
pay every turn. It is not attrition, because the damage curve is too flat and the body too small to
be an HP war; it is not spike, because 17 is the ceiling of anything it throws; it is not swarm,
because there is only ever one add and its 6 HP makes it a decision rather than a threat. For Track
B, model it as a low, gently rising damage baseline plus a recurring per-turn *draw-throughput
penalty* that a player can buy out at a fixed small damage price — the demand curve should reward
splash damage and punish decks with no way to hit a second target.
