# Rocket

- **Class:** `Rocket` (`MonsterModel`)
- **Kind:** boss — the *right arm* of the Kaiser Crab boss encounter
- **Act:** Act 2 (act index 1). One of that act's boss options.
- **Encounter:** `KaiserCrabBoss` — always spawns exactly two monsters, `Crusher` in the `crusher` slot and `Rocket` in the `rocket` slot, on a custom animated background with its own BGM track (`act2_boss_kaiser_crab`) and the camera pulled back to 0.75× with players fully centered.
- **Fight class:** `spike`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What Rocket is

Rocket is half a boss. It is the Kaiser Crab's right claw; `Crusher` is the left claw, dossiered separately. Both arms are always present, there is no variant roster and no add-summoning, and the two share a background node, a music progress parameter, and the `CrabRage` death rider.

Rocket is the **artillery** arm. Its cycle is one throwaway poke, one mid hit, a visible charge, the encounter's single biggest hit, and then a full turn of doing nothing. Crusher is the grinding arm with debuffs and self-block; Rocket has no block, no debuff, and no healing — it exists to deliver one enormous number on a fixed, unmissable clock.

Rocket is also the arm that *installs the encounter gimmick*: it is Rocket, not Crusher, that applies **Surrounded** to every player at combat start.

## 2. Intent pattern / AI

Rocket's move state machine is a **fixed five-move loop with no branching and no RNG**. Each state's follow-up is the next state and the fifth returns to the first. The machine is seeded so that the first move is always Targeting Reticle; from there the order never varies and cannot be perturbed by anything the player does. There are no HP-threshold phases and no move re-rolls.

| Turn (mod 5) | Move | Intent shown | Effect |
| --- | --- | --- | --- |
| 1 | **Targeting Reticle** | single attack | 3 damage (4 at Deadly Enemies) |
| 2 | **Precision Beam** | single attack | 18 damage (20 at Deadly) |
| 3 | **Charge Up** | buff | gains **+2 Strength** (+3 at Deadly); starts a looping charge SFX |
| 4 | **Laser** | single attack | 31 damage (35 at Deadly), plus accumulated Strength |
| 5 | **Recharge** | **sleep** | nothing at all |

The shape is a metronome: *tap, hit, telegraph, haymaker, rest.* The buff intent on turn 3 and the sleep intent on turn 5 are both fully legible one turn ahead, so the player always knows exactly which turn the Laser lands on and always gets a free turn immediately after it. The fight gives back the tempo it takes — but only on its own schedule.

Two consequences worth carrying into a demand model:

- **Turn 3 is the block-banking turn.** Charge Up deals no damage, so the block spent on turn 3 is pure prep for turn 4. A player who spends turn 3 on offense is choosing to eat the Laser raw.
- **Turn 5 is the only genuinely free turn in the encounter** — and it is not actually free, because Crusher is still attacking on the same turn (Guarded Strike, 12/14 plus 18 block). The "rest" is a rest from Rocket only.

## 3. Numbers

| Stat | Base | Tough Enemies (asc) | Deadly Enemies (asc) |
| --- | --- | --- | --- |
| Initial HP | 199 (min == max, no roll) | 209 | — |
| Targeting Reticle damage | 3 | — | 4 |
| Precision Beam damage | 18 | — | 20 |
| Charge Up Strength gain | +2 | — | +3 |
| Laser damage | 31 | — | 35 |
| Recharge | no effect | — | — |
| Block gained, ever | **0** | — | — |

Rocket never blocks and never debuffs. Every point of its output is raw attack damage.

**Cycle totals (base ascension, Strength included, no back-attack multiplier):**

| Cycle | Reticle | Beam | Laser | Cycle total |
| --- | --- | --- | --- | --- |
| 1 | 3 | 18 | 33 (31 + 2) | 54 |
| 2 | 5 | 20 | 35 | 60 |
| 3 | 7 | 22 | 37 | 66 |
| 4 | 9 | 24 | 39 | 72 |

The Strength ramp is +2 per cycle across 3 hits, so **+6 damage per cycle**, and roughly 61% of every cycle arrives on a single turn. At Deadly Enemies the ramp is +3 across 3 hits (**+9/cycle**) on top of a higher baseline, so long fights diverge rather than shift by a constant.

**Laser with the back-attack multiplier (§4.1):** cycle-1 Laser 33 → ~50; Deadly cycle-1 Laser 38 → ~57. This is the largest single number in the encounter by a wide margin and the reason parties usually choose to keep facing Rocket and eat Crusher's back-attacks instead.

Sibling reference (Crusher, left arm): 209 HP (219 Tough); cycle 12 → 4 → 6×2 + Weak 2/Frail 2 → +2 Strength → 12 + 18 block. Crusher deals ~40/cycle over 5 hits; Rocket deals ~54/cycle over 3.

## 4. Gimmicks

### 4.1 Surrounded — the facing rule (installed by Rocket)

At combat start Rocket applies **Surrounded** to every one of its opponents (every player), and each arm applies a marker power naming its side: Crusher carries the left marker, Rocket the right.

Surrounded means: **the arm you are not facing hits you for ×1.5.** Players start facing *right*, i.e. **facing Rocket**, which means Crusher begins the fight at their back. Playing a *targeted* card or using a *targeted* potion on the arm behind you flips your facing toward that arm — and puts the other arm behind you.

Points that matter for modelling:

- Facing is **per-seat**. Each player carries their own Surrounded instance and their own facing; in co-op the party can genuinely have different arms behind different players.
- Only *targeted* plays flip you. Untargeted cards, block cards, and power cards leave facing untouched, so a pure defensive turn locks in whatever multiplier you already had.
- The ×1.5 lives on the *player's* power and is applied multiplicatively at damage time, so it compounds with the player's own Weak/Vulnerable modifiers rather than being baked into the printed intent. The intent number the player sees is the pre-multiplier value.
- Because Rocket starts in front, a party that simply focuses Rocket never takes an amplified Laser at all — the tax lands on Crusher's five smaller hits instead. Turning to burn down Crusher is what turns the Laser into a ~50-point hit. This is the encounter's central tension and it is *entirely* Rocket-shaped: the arm you want to leave alone is the arm you must keep looking at.
- When one arm dies, if every remaining hittable enemy is on the same side, facing is auto-corrected toward the survivor. The back-attack tax therefore **ends** at the start of phase two.

### 4.2 Crab Rage — the kill-order trap

Both arms carry **Crab Rage**. When one arm dies, the survivor immediately gains **+6 Strength and 99 Block**, and the power is consumed.

For Rocket specifically: killing Crusher first hands Rocket +6 Strength on a cycle whose top move is already 31–35 base, taking a cycle-1-equivalent Laser to **39** (45 at Deadly) before any further Charge Ups, behind a 99-block wall that absorbs roughly two player turns of output — arriving precisely when the party has just spent its burst. Rocket only has 3 hits per cycle, so the +6 is worth +18 damage per cycle to it, versus +30 per cycle to Crusher; but Rocket concentrates it into the spike, which is far more likely to actually kill somebody.

The intended answer is to bring both bars low and finish them within a turn or two of each other. The 99 block is flagged as an unpowered value and therefore does **not** receive multiplayer block scaling (§6), so the rage wall is proportionally much smaller in a 4-player game than it is solo.

### 4.3 Presentation-side notes (no mechanical effect)

- Both arms are drawn on the shared Kaiser Crab background rather than as free-standing sprites; hurt, attack and death animations are dispatched to the background node by arm side.
- Rocket's Charge Up starts a looping buff SFX that is explicitly stopped by the Laser move, and stopped again if the monster is removed from the room mid-charge.
- Music progress is driven by a custom parameter: Rocket (right arm) dying sets it to 1, Crusher to 2, and either arm dying while combat is already ending sets it to 5 and plays the whole body's death animation. Facing drives a second music parameter, but only for the local player.
- Rocket does not fade after death and is **immune to removal by Doom** effects; its death animation is held for 2.5 seconds. The corpse stays on screen for the whole second phase.

## 5. Scaling by act / ascension

- **By act:** none. Kaiser Crab is an Act 2 boss only and has no per-act variant. Act index matters only through the multiplayer scaling constant (§6).
- **By ascension:** two binary gates, no continuous curve.
  - *Tough Enemies*: HP 199 → 209 (Crusher 209 → 219).
  - *Deadly Enemies*: Targeting Reticle 3 → 4, Precision Beam 18 → 20, Laser 31 → 35, Charge Up +2 → +3 Strength.
  - The Charge Up bump is the important one: it changes the ramp slope (+9/cycle instead of +6), so the Laser's growth curve steepens rather than merely starting higher.
  - *Double Boss* is a run-structure ascension and does not alter this monster's stats.

## 6. Multiplayer / seat count

- The encounter spawns exactly **two** monsters at every seat count. Headcount is absorbed into stats, not into extra bodies.
- **HP** is multiplied by `player count × act constant`. Act index 1 gives a constant of **1.2**, so Rocket is 199 solo, ~478 at 2 players, ~716 at 3, ~955 at 4 (Tough Enemies raises the base to 209 first: ~502 / ~752 / ~1003).
- **Block scaling is irrelevant to Rocket** — it never gains block from a move. The only block it can ever have is Crab Rage's 99, which is tagged unpowered and is explicitly exempt from the multiplayer multiplier. So the rage wall is 99 whether there is one player or four.
- **Damage is NOT divided among seats.** Rocket's attacks target *all opponents*; every player takes the full printed number, each further modified by their own facing and their own defensive powers. A 33-damage Laser is 33 to each of four players (≈132 party-wide), and up to ~50 for any player who happens to be facing away.
- **Surrounded is applied per opponent**, so each seat tracks its own facing. Coordinating who targets which arm is a real co-op skill check that does not exist solo, and it is possible for the party to be in the worst configuration — some players facing Crusher, some facing Rocket — where both arms are landing ×1.5 on somebody every single turn.
- Because Rocket's damage does not split but its HP multiplies by roughly 1.2× per seat, the Laser stays a lethal-threshold problem at every party size while the fight gets *longer* — meaning more Charge Ups, and a strictly larger Laser by the time the bar empties.

## 7. Proposed fight class: `spike`

Rocket's entire demand profile is one number on a known turn. Two of its five turns deal negligible or zero damage (3-damage Reticle, no-damage Recharge) and a third is a pure telegraph, so the fight asks nothing of the player for stretches and then asks for a full 33–50+ point answer on turn 4 of every cycle — and the answer is required, because the Strength ramp makes the Laser grow +2 (or +3) every cycle while the player's block economy does not.

That is the defining per-turn demand: not sustained mitigation but **peak mitigation on a predictable clock**, plus enough burst to end the fight before the peak outgrows what a single defensive turn can cover. The Charge Up/Recharge pair even hands the player the tempo to set that up, which is precisely what marks this as a spike pattern rather than attrition — the pressure is entirely in the amplitude, not the average.

Two caveats for Track B. First, Rocket is scored here as a *component*, not as a standalone encounter: the parent `KaiserCrabBoss` fight is classed `mixed`, because Crusher supplies an attrition baseline and the Surrounded/Crab-Rage gimmicks add decision costs that never appear in incoming-damage numbers. Second, the ×1.5 back-attack multiplier means Rocket's spike has two magnitudes depending on a player choice made on a *different* turn — a demand curve for this arm should carry both the faced (33/35/37…) and unfaced (~50 and climbing) Laser tracks rather than a single line.
