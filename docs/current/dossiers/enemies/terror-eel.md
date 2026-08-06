# Terror Eel

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `TerrorEel`
- **Kind:** elite
- **Act:** 1 (Underdocks, act index 0)
- **Encounter:** `TerrorEelElite` — solo spawn, elite room, camera scaled to 0.9
- **Fight class:** **gimmick**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

The Terror Eel is an Act 1 (Underdocks) elite. Its encounter always generates exactly one monster —
no adds, no summons, no minions, and no second creature at any point. It takes damage with the
"slime" hit-sound family. It is the only user of its signature power, Shriek, in the whole model
set, so everything below is self-contained to this one fight.

## Opening (on room entry, before turn 1)

One thing happens on entry: the eel applies **Shriek** to *itself*. Shriek is displayed as a debuff
(a counter, with a Stun hover tip attached), and its number is the eel's own HP threshold — see
Gimmicks. Nothing else is set up; there is no opening buff, block, or status.

## Intent pattern

The visible loop is a two-beat alternation with no randomness and no branching:

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Crash** | single-target-style attack (see AoE note) | attack |
| 2 | **Thrash** | 3-hit attack, then gains Vigor 6 | multi-attack (×3) + buff |

Crash points at Thrash, Thrash points back at Crash, forever. Turn 1 is always Crash — the state
machine is barred from transitioning before the first move resolves. A player who has seen the
fight once knows every turn of it in advance.

Two further states exist that are **not** part of the loop and are reachable only through the Shriek
trigger:

| State | What it does | Notes |
|---|---|---|
| **Stun** | nothing at all — a lost enemy turn | hidden from the bestiary listing |
| **Terror** | applies **Vulnerable 99** to every player | shows a debuff intent; then hands back to Crash |

The registered Stun state chains into Terror, and Terror chains back into Crash, so the fight's real
shape is: `Crash ⇄ Thrash …` → *(threshold trips)* → `Stunned` → `Terror` → `Crash ⇄ Thrash …`
under a permanent 1.5× damage multiplier.

**Every attack is AoE.** Both attacking moves are built as monster attacks against all opponents, so
in co-op each living seat eats the full listed number on every hit — there is no target roll and no
split. The Crash intent renders with a single-target icon, but that is cosmetic.

## Damage / block numbers

Base values, with the two ascension variants where they differ:

| Stat | Base | Ascension variant |
|---|---|---|
| HP (min = max, no roll) | **140** | **150** (`ToughEnemies`) |
| Crash damage | 16 | 18 (`DeadlyEnemies`) |
| Thrash damage per hit | 3 | 4 (`DeadlyEnemies`) |
| Thrash hit count | 3 | 3 (unchanged) |
| Vigor gained after Thrash | 6 | 6 (unchanged) |
| Shriek threshold | 70 | 75 (`ToughEnemies`) |
| Terror — Vulnerable applied | 99 | 99 (unchanged) |

**The eel never gains block, ever.** There is no defensive move in its kit. All 140 HP is raw
damage the player must push through, and no turn is wasted on mitigation — the trade is that no turn
is wasted on the player's side either.

### Vigor and the real Crash number

Thrash grants the eel Vigor 6 *after* its hits land, so Thrash never boosts itself. Vigor is a
one-shot additive damage bonus consumed by the eel's next attack — which is always the following
Crash. Steady-state, therefore:

| Turn | Move | Damage to each player (base) | (`DeadlyEnemies`) |
|---|---|---|---|
| 1 | Crash | 16 | 18 |
| 2 | Thrash | 3 ×3 = 9 | 4 ×3 = 12 |
| 3 | Crash (+Vigor 6) | **22** | **24** |
| 4 | Thrash | 9 | 12 |
| 5 | Crash (+Vigor 6) | 22 | 24 |

So only the very first Crash is the "printed" 16; every later Crash is 22. Pre-threshold incoming
runs ~31 per two-turn cycle (~15.5/turn), or ~36 per cycle (~18/turn) on `DeadlyEnemies`. That is a
flat, unescalating curve — nothing in the eel ramps on its own.

### After Terror

Vulnerable 99 multiplies damage taken by 1.5× and ticks down one per enemy turn end, so 99 stacks is
"permanent for the rest of this combat" in every realistic fight length. Post-Terror the same loop
reads:

| Move | Base | (`DeadlyEnemies`) |
|---|---|---|
| Crash (no Vigor) | 24 | 27 |
| Crash (+Vigor 6) | 33 | 36 |
| Thrash | ≈4 ×3 ≈ 13 | 6 ×3 = 18 |

Roughly 46 per two-turn cycle (~23/turn) base, ~54 per cycle (~27/turn) on `DeadlyEnemies` — a clean
1.5× step, not a ramp. Per-hit fractions resolve through the engine's normal damage rounding.

## Gimmicks

### Shriek → Stun → Terror (the whole fight)

Shriek sits on the eel from turn zero with a number equal to exactly **half its max HP** (70 of 140;
75 of 150 on `ToughEnemies`). It watches for one condition: the eel takes **unblocked** damage while
its current HP is at or below that number. When that happens, three things follow:

1. The eel is **stunned immediately** — its currently telegraphed intent is replaced on the spot with
   a stunned move that does nothing. A queued 22-damage Crash can be erased this way.
2. The turn after the stun, it performs **Terror**: a scream that applies Vulnerable 99 to every
   player. Terror deals no damage.
3. Shriek is then **removed**. The whole sequence fires exactly once per fight, never again.

Net effect: the player buys two damage-free enemy turns and pays for them with a permanent 1.5×
damage-taken multiplier for the back half of the fight. Both halves of that trade are forced — the
eel cannot be worn down past half HP without triggering it.

The one out: the trigger only lands if the eel is alive when it resolves. **Killing the eel outright
from above half HP skips the entire phase**, so a burst deck that can deliver 70+ damage in one
window never sees Terror at all. This is the fight's central planning question and the reason its
difficulty is so deck-shape dependent.

A second, smaller lever: because the trigger requires *unblocked* damage, the player has some control
over *when* it fires. Chip damage that lands while an expensive Crash is telegraphed converts that
Crash into a free turn; chip damage that lands on a Thrash turn wastes the stun on a 9-damage move.

### Non-mechanics worth recording

- No block, no healing, no self-buff other than the single-use Vigor.
- No adds, no minion spawns, no death rattle.
- No HP-percentage behavior other than the Shriek threshold.
- The stunned turn is hidden from the bestiary move list, so the in-game listing shows only Crash,
  Thrash, and Terror.

## Scaling

**By act:** none. The Terror Eel appears only in Act 1's encounter list; nothing on the model reads
the act index except through the shared multiplayer formulas.

**By ascension:**

| Level | Effect |
|---|---|
| `ToughEnemies` (8th in the ascension enum) | HP 140 → 150; Shriek threshold 70 → 75 (stays exactly half) |
| `DeadlyEnemies` (9th) | Crash 16 → 18; Thrash 3 → 4 per hit |

Vigor 6 and the Vulnerable 99 are untouched at both levels. Note that the `ToughEnemies` bump moves
the threshold with the HP, so the phase transition always sits at the halfway mark and the "burst it
from above half" plan needs 75 rather than 70. `SwarmingElites` (1st in the enum) is a run-level
modifier that affects how often elites are met, not this fight's internals.

**By seat count (multiplayer):**

- **HP** takes the standard scale: base × players × 1.1 (the Act 1 multiplier).

| Players | HP (base) | HP (`ToughEnemies`) |
|---|---|---|
| 1 | 140 | 150 |
| 2 | 308 | 330 |
| 3 | 462 | 495 |
| 4 | 616 | 660 |

- **Shriek scales with it.** Shriek is explicitly flagged to scale in multiplayer and goes through
  the same players × 1.1 formula, so the threshold stays pinned at half the scaled pool (154 of 308
  at two players, and so on). The phase transition therefore lands at the same *fraction* of the
  fight regardless of party size — but the absolute burst needed to skip it grows linearly with
  seats, which is why the "kill it above half" out is far harder in co-op than solo.
- **Damage does not scale, but it is AoE** — every seat takes the full Crash / Thrash number, so
  party-wide damage taken scales linearly with seats on top of the HP scale.
- **Terror hits every player**, each getting their own Vulnerable 99. There is no partial or
  single-seat version.
- **Vigor** is not multiplayer-scaled; it stays at 6 regardless of party size.

## Proposed fight class: **gimmick**

Turn to turn the eel asks a very plain question — block roughly 9 or 22 on an alternating clock, with
no block on its side, no ramp, and no adds — and that flat baseline is not what makes it an elite.
The fight's entire demand is concentrated in one binary the player must answer before combat starts:
either deliver ~70 damage (scaled, in co-op) in a single window and skip the phase change outright,
or accept a permanent 1.5× damage-taken multiplier and pre-bank the mitigation for a back half that
runs ~23 incoming per turn instead of ~15. That single HP-threshold trigger also inverts the usual
tempo logic, because the player controls *when* it fires and can deliberately spend it to erase a
telegraphed 22-damage Crash. For Track B, model it as a flat two-beat attrition baseline with a
one-time step function at 50% HP: a two-turn damage holiday followed by a permanent ×1.5 on every
subsequent incoming number, with an escape hatch that rewards single-window burst above the
threshold.
