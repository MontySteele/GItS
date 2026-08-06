# Owl Magistrate — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `OwlMagistrate`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `OwlMagistrateNormal` — a single-monster encounter, one Owl Magistrate in the default slot. No allies, no summons, no second body.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Owl runs a **four-state move machine with zero randomness**. Every state has a hard-wired follow-up and the fourth wraps back to the first, so the whole fight is one fixed loop the player can read from turn one and never has to guess again.

The loop, starting state first:

1. **Magistrate Scrutiny** — *single-attack* intent. One medium hit, gaze VFX.
2. **Peck Assault** — *multi-attack* intent, damage × 6. Six small hits played under a single peck animation.
3. **Judicial Flight** — *buff* intent only, **no damage**. The Owl takes off, goes airborne (a distinct flying animation set, flight loop SFX, its hurt/death sounds change), and gains **Soar**.
4. **Verdict** — *single-attack* + *debuff* intent. It lands out of the dive: one heavy hit, then applies **Vulnerable 4** to every player, then Soar is removed. A short beat follows before control returns.

Then straight back to Scrutiny. Sequence, forever:

| Turn | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | … |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Move | Scrutiny | Peck Assault | Judicial Flight | **Verdict** | Scrutiny | Peck Assault | Judicial Flight | **Verdict** | loop |

There is no HP-threshold branch, no enrage, no opening special, and no state the machine can get stuck in or skip. The intent icon on the flight turn is a pure buff icon, so the "free" turn is always visible one turn ahead of it — and so is the Verdict, because the flight turn *is* the tell.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Max HP | **231** (fixed — min and max are the same, no roll) | **247** at the *Tough Enemies* tier |
| Magistrate Scrutiny damage | 16 | 17 at the *Deadly Enemies* tier |
| Peck Assault damage | 4, **six times** (24 total) | 4 × 6 — **not** ascension-scaled |
| Judicial Flight | 0 damage; gain Soar 1 | unchanged |
| Verdict damage | 33 | 36 at the *Deadly Enemies* tier |
| Verdict Vulnerable applied | 4 | 4 — not ascension-scaled |
| Block gained, ever | **none** | none |

**Soar:** while the Owl holds it, powered attack damage dealt *to the Owl* is multiplied by **50%**. It is a single-stack buff, applied at the end of the flight turn and removed at the end of the Verdict move. In practice it covers exactly **one player turn** — the turn between Judicial Flight and Verdict. Non-attack damage and unpowered damage (poison ticks, direct HP loss, and anything not flagged as a powered attack) ignore Soar entirely.

**Vulnerable:** multiplies damage received by **1.5×**, and ticks down at the end of each *enemy* turn. That timing matters. Vulnerable 4 is applied during the Owl's Verdict turn, so the Verdict hit that delivered it is unamplified, and the first tick fires at the end of that same enemy turn:

| Enemy turn | Move | Vulnerable stacks in effect | Damage taken by each player |
| --- | --- | --- | --- |
| n (Verdict) | Verdict | 0 during the hit → 4 applied → ticks to 3 | 33 |
| n+1 | Scrutiny | 3 → 2 | **24** (16 × 1.5) |
| n+2 | Peck Assault | 2 → 1 | **36** (4 × 1.5 = 6, six times) |
| n+3 | Judicial Flight | 1 → 0 | 0 — a stack is spent on a no-damage turn |
| n+4 | Verdict | 0 | 33 |

So the debuff amplifies exactly two moves per cycle — the Scrutiny and the Peck Assault that follow it — and always wastes its fourth stack on the flight turn. It never touches a Verdict.

**Per-cycle damage, per player** (before player block and modifiers):

| Cycle | Scrutiny | Peck | Flight | Verdict | Cycle total |
| --- | --- | --- | --- | --- | --- |
| First (no Vulnerable yet) | 16 | 24 | 0 | 33 | **73** |
| Steady state (Vulnerable up) | 24 | 36 | 0 | 33 | **93** |
| Steady state, *Deadly Enemies* tier | 25 | 36 | 0 | 36 | **~97** |

The Owl's damage does not ramp, gain Strength, or otherwise grow. Cycle two onward is the ceiling; the fight's arithmetic is fully known by turn five.

## Gimmicks

- **The flight turn is a two-sided trade, not a free turn.** The Owl gives up an entire attack (0 damage) to halve the damage it takes on the player's next turn. For a player playing evenly, that is a wash. For a burst deck it is a trap: the one turn the player is safest to go all-in on offense is precisely the turn their attacks are worth half. Correct play is to hold the nuke a turn and dump it into the post-Verdict window instead.
- **Soar is attack-only mitigation.** Poison, HP-loss, orb/other non-attack sources, and unpowered damage all pass through at full value. Any deck that damages the Owl without an attack simply does not have a flight turn.
- **Vulnerable is a self-renewing tax with near-total uptime on the damage that matters.** A four-stack counter on a four-turn cycle means the party is effectively Vulnerable for every turn the Owl actually swings, from the first Verdict to the end of the fight. There is no window where the player is "clean" except the pre-first-Verdict opening.
- **The two attack shapes ask opposite defensive questions.** Peck Assault's 6 × 4 (6 × 6 under Vulnerable) is chip that shreds thin block and punishes per-hit-flat mitigation; Verdict's single 33 is a wall-or-eat decision. Alternating them means the player cannot settle on one block plan.
- **Landing and takeoff are cosmetic-but-legible.** The airborne state swaps its animation set, bounds, hurt SFX and death SFX; if the Owl dies while airborne it plays a distinct flying death. The visual state is a reliable read on whether Soar is up, independent of the power icon.
- No block, ever. The Owl has no defensive turn other than Soar — the 231-HP bar is raw and never gets padded.
- No adds, no thresholds, no death rattle, no enrage.

## Scaling by act / ascension

- **Act:** none intrinsic. Owl Magistrate is Act 3 content only and its numbers do not read the act index. The only act-derived factor that touches it is the multiplayer scaler below (act index 2, non-boss room → factor 1.2).
- **Ascension:** two independent, tier-keyed bumps, both small.
  - *Tough Enemies* tier: HP 231 → **247** (+16, about +7%).
  - *Deadly Enemies* tier: Scrutiny 16 → 17, Verdict 33 → 36. Peck Assault stays at 4 per hit at every ascension.
  - Vulnerable amount (4), Soar's 50%, and the peck repeat count (6) are **not** ascension-scaled. This is a notably flat ascension curve for an Act 3 normal: the steady-state cycle goes from 93 to ~97 damage against a 7% bigger bar.

## Multiplayer / seat-count adjustments

- **HP multiplies by (player count × 1.2).** Act index 2 in a non-boss room gives a 1.2 factor, applied on creature creation. Two players: **~554** HP (231 × 2 × 1.2); three players: **~831**. At the Tough-Enemies tier: ~593 and ~889.
- **Block scaling is irrelevant here** — the Owl never gains block, so the block half of the multiplayer scaler never fires on this fight.
- **Damage does not scale, but it lands per seat.** Monster attacks target *all* opposing player creatures rather than picking one. Scrutiny hits every player for its full listed damage, Peck Assault hits every player six times, and Verdict hits every player for the full heavy hit. Party-wide incoming damage per cycle is therefore 93 × seats in steady state, against an HP pool that only grew by seats × 1.2.
- **Vulnerable 4 is applied to every player creature**, not to one target. There is no "the tank ate the debuff" outcome; the whole party is Vulnerable together, on the same clock, for the same two amplified turns per cycle.
- **Soar is a single stack on the Owl regardless of seat count** — the 50% reduction applies to each player's attacks independently, so at three seats the flight turn is costing the party three players' worth of half-damage while the Owl skips one attack. The trade gets *better* for the Owl as seats increase, and the longer fight (HP × seats × 1.2) means more flight turns are reached.

## Fight-class reasoning — `mixed`

The Owl rotates through four genuinely different asks on a fixed four-turn clock, and no single one dominates the fight's demand profile: turn 1 is chip to absorb, turn 2 is a six-hit spread that punishes thin or per-hit block, turn 3 is a damage-free turn that is secretly an *offense* puzzle because Soar halves attack damage exactly then, and turn 4 is a telegraphed 33-point wall-or-eat spike that pays itself forward as party-wide Vulnerable. Labelling it `spike` would capture only the Verdict and ignore that the Vulnerable-amplified Peck Assault (36 across six hits) is actually the biggest turn in the cycle; labelling it `attrition` would be defensible on the 231-HP single bar and the ~100% Vulnerable uptime, but it undersells the two hard timing decisions the fight forces every four turns. `gimmick` overweights Soar, which is only a 12.5%-of-turns damage tax to a player who reads it. What the fight demands *per turn* is a different answer each turn, which is what `mixed` is for.
