# Crusher

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Crusher` (`MonsterModel`)
- **Kind:** boss — the *left arm* of the Kaiser Crab boss encounter
- **Act:** Act 2 (the Hive; act index 1). One of that act's three boss options.
- **Encounter:** `KaiserCrabBoss` — always spawns two monsters, `Crusher` in the `crusher` slot and `Rocket` in the `rocket` slot, on a custom animated background with its own BGM track and a camera pulled back to 0.75× scale.
- **Fight class:** `mixed`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What Crusher is

Crusher is not a standalone monster. It is one of two halves of a single creature: the Kaiser Crab's left claw. The right claw is `Rocket`, dossiered separately, and the two share a background node, a music progress parameter, and — critically — a shared death rider that makes the survivor far more dangerous than either arm was alone.

Both arms are always present. There is no variant roster, no randomized spawn, and no add-summoning. The entire fight is two fixed HP pools with two fixed, non-random move cycles running in parallel, wrapped in a positional gimmick that decides which of them is hurting you more.

Crusher is the **melee/attrition** arm: mid-size repeating attacks, a Strength ramp, self-block, and the only debuff application in the encounter. Rocket is the artillery arm with the big single-turn spike.

## 2. Intent pattern / AI

Crusher's move state machine is a **fixed five-move loop with no branching and no RNG**. Every state's follow-up is the next state, and the fifth loops back to the first. The machine is seeded on the first move, so turn 1 is always Thrash; from there the order never varies, never repeats early, and cannot be perturbed by player action.

| Turn (mod 5) | Move | Intent shown | Effect |
| --- | --- | --- | --- |
| 1 | **Thrash** | single attack | 12 damage (14 at Deadly Enemies) |
| 2 | **Enlarging Strike** | single attack | 4 damage |
| 3 | **Bug Sting** | multi-attack + debuff | 6 damage ×2 (7 ×2 at Deadly), then **Weak 2** and **Frail 2** |
| 4 | **Adapt** | buff | gains **+2 Strength** (+3 at Deadly) |
| 5 | **Guarded Strike** | single attack + defend | 12 damage (14 at Deadly), then gains **18 Block** |

Read as a demand curve, the cycle is a two-beat rest sandwiched between three real beats: the player gets a soft turn (Enlarging Strike, 4 damage) and a no-damage turn (Adapt), and pays for both — Adapt's Strength is permanent and compounds every subsequent cycle, and Bug Sting's Weak/Frail arrives right before the Adapt/Guarded-Strike block window, which is exactly when the player wants to be pushing damage.

Because the intent is fully deterministic and telegraphed one turn ahead, this boss is *readable* but not *dodgeable*: there is no move you can prevent, only turns you can choose to block or race through.

## 3. Numbers

| Stat | Base | Tough Enemies (asc) | Deadly Enemies (asc) |
| --- | --- | --- | --- |
| Initial HP | 209 (min == max, no roll) | 219 | — |
| Thrash damage | 12 | — | 14 |
| Enlarging Strike damage | 4 | — | 4 (unchanged) |
| Bug Sting damage | 6 × 2 hits | — | 7 × 2 hits |
| Bug Sting debuffs | Weak 2 + Frail 2 | — | unchanged |
| Adapt Strength gain | +2 | — | +3 |
| Guarded Strike damage | 12 | — | 14 |
| Guarded Strike block | 18 | — | unchanged |

Sibling reference (Rocket, right arm): 199 HP (209 Tough); cycle is 3 → 18 → +2 Strength → **31** → sleep. Its Laser is the encounter's spike; Crusher never lands a single hit that large on its own.

Per full 5-turn Crusher cycle, ignoring Strength: 12 + 4 + 12 + 12 = 40 damage across 4 attacking hits (Bug Sting is 2 hits, so 5 hits total). Strength adds to *every hit*, so each Adapt is worth +2 damage × 5 hits = **+10 damage per cycle**, and the multi-hit Bug Sting double-dips. By cycle 4 Crusher's Thrash is hitting for 18 (base) and the fight has quietly become a race.

Note that **Enlarging Strike's printed 4 does not scale with ascension** — it is the designated soft turn, and its only real job is to grow with Strength. The move name is aspirational: it has no self-scaling of its own.

## 4. Gimmicks

### 4.1 Surrounded — the facing rule (encounter-level, applied by Rocket)

On combat start, Rocket applies **Surrounded** to every player, and each arm applies a marker power identifying which side it stands on (Crusher = left marker, Rocket = right marker).

Surrounded means: **the arm you are not facing hits you for ×1.5.** The player creature has a facing (right by default at combat start, so **Crusher — the left arm — starts behind you**). Whenever that player plays a *targeted* card or uses a *targeted* potion at the arm behind them, the player flips to face that arm — and the other arm is now at their back.

Consequences worth carrying into any model of this fight:

- Facing is **per-seat**, not global. Each player carries their own Surrounded instance and their own facing.
- Only *targeted* plays flip you. Untargeted cards, block, and power cards leave your facing alone — so a defensive or ramp turn locks in whatever back-attack multiplier you already had.
- Flipping is free but not costless: you cannot damage both arms and face both. Alternating targets each turn means you spend the entire fight taking one arm's damage at ×1.5.
- Crusher's numbers, seen from the wrong side, are: Thrash 18, Bug Sting 9×2, Guarded Strike 18 (base ascension). Rocket's Laser seen from the wrong side is 46/52 — which is why most parties end up choosing to eat Crusher's back-attacks rather than Rocket's.
- The multiplier is applied by the *player's* power, so it stacks multiplicatively with the player's own vulnerability/weak modifiers rather than being baked into the monster's intent.
- When one arm dies, if all remaining hittable enemies are on the same side, facing is auto-corrected toward the survivor. The back-attack tax therefore **ends** with the second phase — the surviving arm can no longer hit your back.

### 4.2 Crab Rage — the kill-order trap

Both arms carry **Crab Rage**. When one arm dies, the surviving arm immediately gains **+6 Strength and 99 Block**, and Crab Rage is consumed.

This is the load-bearing decision of the fight. Killing Crusher first hands Rocket +6 Strength on a cycle whose top-end move is 31 → **37** before its own Charge Ups are counted, behind a 99-block wall that eats roughly two full player turns of output. Killing Rocket first hands Crusher +6 Strength — less explosive per hit, but Crusher hits 5 times per cycle, so the same +6 is worth +30 damage per cycle to it.

The intended answer is to bring both arms low and finish them close together, so the survivor's rage window is short. A party that over-focuses one arm gets punished twice: once by the rage payout, once by the 99 block arriving while their damage burst is already spent.

The 99 block is flat and does **not** receive the multiplayer block scaling that Guarded Strike's 18 does (see §6) — it is tagged as an unpowered value. In a 4-player game, the rage wall is proportionally much smaller than the routine Guarded Strike wall.

### 4.3 Presentation-side notes (no mechanical effect)

- Both arms are drawn on the shared background rather than as free-standing creature sprites; hurt, attack, and death animations are dispatched to the background node by arm side.
- The boss music tracks progress through a custom parameter: right arm dead sets it to 1, left arm (Crusher) dead sets it to 2, and either arm dying while the combat is already ending sets it to 5 and plays the whole body's death animation. Facing also drives a music parameter, but only for the local player.
- Crusher does not fade after death and is not removed by Doom effects; its death animation is held for 2.5 seconds. That means the corpse stays on screen for the entire second phase.

## 5. Scaling by act / ascension

- **By act:** none. Kaiser Crab is an Act 2 boss only and has no per-act variant. Act index matters only through the multiplayer HP/block scaling constant (§6).
- **By ascension:** two gates, both binary rather than continuous.
  - *Tough Enemies*: HP 209 → 219 (Rocket 199 → 209).
  - *Deadly Enemies*: Thrash 12 → 14, Bug Sting 6 → 7 per hit, Guarded Strike 12 → 14, Adapt +2 → +3 Strength. Enlarging Strike, Bug Sting's Weak/Frail, and Guarded Strike's 18 block are unchanged.
  - The Adapt bump is the sharpest of these: +3/cycle instead of +2 changes the ramp slope, not just the baseline, so long fights diverge rather than shifting by a constant.
  - *Double Boss* is a run-structure ascension and does not touch this monster's stats.

## 6. Multiplayer / seat count

- The encounter spawns exactly **two** monsters at any seat count. Headcount is absorbed by stats, not by adds.
- **HP** is multiplied by `player count × act constant`. For an Act 3-indexed boss the constant is 1.3; Kaiser Crab sits at act index 1, where the constant is **1.2**. So Crusher is 209 solo, ~502 at 2 players, ~753 at 3, ~1004 at 4 (Tough Enemies raises the base to 219 before scaling).
- **Block from moves** is scaled by the same `player count × act constant` factor. Guarded Strike's 18 becomes ~43 at 2 players, ~65 at 3, ~86 at 4. Crab Rage's 99 is exempt (unpowered value prop) and stays 99 at every seat count.
- **Damage is NOT divided among seats.** Crusher's attacks target *all opponents*, and the target list is refreshed between hits. Every player takes the full printed number, each modified by their own facing and their own defensive powers. Bug Sting therefore applies Weak 2 + Frail 2 to the whole party simultaneously, and each player independently takes 6×2 — or 9×2 if Crusher is at their back.
- **Facing is per-seat**, so in co-op the party can genuinely be surrounded in the intended sense: one player facing Crusher while another faces Rocket means both arms are landing ×1.5 on someone every turn. Coordinating target choice is a real multiplayer skill check that does not exist solo.
- Weak/Frail hitting all seats at once, combined with the shared HP pool, makes Bug Sting turn disproportionately punishing in co-op: it taxes the whole party's output on the exact turn the party most needs to be pushing through the Guarded Strike block.

## 7. Proposed fight class: `mixed`

Crusher's own kit is textbook **attrition** — a deterministic five-turn loop with no burst, a permanent Strength ramp, self-block on a fifth of its turns, and a Weak+Frail tax that suppresses player output precisely when the block wall goes up. It asks for sustained, repeatable mitigation rather than a single big defensive turn, and it wins by outlasting a party that cannot keep pace with the ramp.

But its per-turn demand cannot be separated from the two gimmicks it lives inside. Surrounded means every turn also carries a *targeting* decision — attack the arm behind you and flip the ×1.5 tax onto the other arm, or hold facing and eat it — and Crab Rage means the whole fight is gated on a *kill-order* decision that must be resolved before either health bar empties. Meanwhile the sibling arm's 31/35 Laser injects a genuine **spike** beat the player must bank block for on a fixed cadence.

Per turn, the player is answering three different questions at once: can I absorb this cycle's chip, who am I facing, and are the two bars close enough to finish together. No single-label bucket captures that. `mixed` is the honest classification; a Track B demand curve for this fight should carry an attrition baseline with a periodic spike overlay and a non-damage decision cost that does not show up in incoming-damage numbers at all.
