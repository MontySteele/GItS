# Punch Construct — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `PunchConstruct`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounters:**
  - `PunchConstructNormal` — a single Punch Construct, alone. (This is the entry listed in Underdocks' encounter table.)
  - `ConstructMenagerieNormal` — one Punch Construct plus **two** Cubex Constructs.
  - `PunchOffEventEncounter` — **two** Punch Constructs, spawned by the `PunchOff` event (Underdocks event pool, gated to total floor ≥ 6). Both bodies enter pre-damaged and one of them opens on a different beat; see *Gimmicks*.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

A three-state move machine with **zero randomness**. Every transition is a hard-wired follow-up, so the whole fight is readable from turn one.

The three moves, in cycle order:

1. **Ready** — shows a *defend* intent. Plays a cast/buff animation and gains **10 Block**. No damage.
2. **Fast Punch** — shows a *multi-attack* intent (damage × 2) **and** a *debuff* intent. Two quick hits, then applies **1 Frail** to the target(s).
3. **Strong Punch** — shows a *single-attack* intent. One large hit. No rider.

Wiring: Ready → Fast Punch → Strong Punch → Ready → … forever. It is a closed loop with no exits, no branches, no HP thresholds, and no RNG — unlike most normals, the machine never rolls; it just walks the ring.

The **opening state is a per-instance flag.** By default the construct starts on **Ready** (it spends turn 1 blocking). The `PunchOff` event flips one of its two constructs to start on **Fast Punch**, which offsets that body's whole cycle by one turn and de-syncs the pair. Standard first-move handling applies: whatever the opening state is, it is performed on turn 1 before any transition can occur.

Base single-player, no ascension, default opening:

| Turn | Move | Intent shown | Effect |
| --- | --- | --- | --- |
| 1 | Ready | defend | +10 Block |
| 2 | Fast Punch | attack ×2 + debuff | **5 × 2 = 10** damage, then **1 Frail** |
| 3 | Strong Punch | attack | **14** damage |
| 4 | Ready | defend | +10 Block |
| 5 | Fast Punch | attack ×2 + debuff | 10 damage, 1 Frail |
| 6 | Strong Punch | attack | 14 |

Cumulative incoming damage: 0 / 10 / 24 / 24 / 34 / **48** by turn 6, 72 by turn 9. **The damage rate is flat — 24 per three-turn cycle, forever.** There is no Strength gain, no ramp, no enrage. The only thing that changes across the fight is how much Block the construct has soaked up.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP | **55** (fixed — min and max are the same value) | **60** at the *Tough Enemies* tier |
| Strong Punch damage | 14 | **16** at the *Deadly Enemies* tier |
| Fast Punch damage | 5, **twice** | **6**, twice, at the *Deadly Enemies* tier |
| Fast Punch Frail | 1 stack | not ascension-scaled |
| Ready Block | 10 | not ascension-scaled |
| Opening Artifact | 1 | not ascension-scaled (but see multiplayer) |
| Starting HP reduction | 0 normally; **2–9** in the `PunchOff` event | not ascension-scaled |

HP is a **fixed 55 (60)** — there is no roll and no per-body variance, so two Punch Constructs in the same room have identical HP and the kill turn is fully plannable. It is a low number for a normal: two solid attack turns can end the fight before the second Strong Punch ever resolves.

At the *Deadly Enemies* tier the cycle becomes 0 / 12 / 16, i.e. **28 per cycle** instead of 24, with the same shape.

Damage taken uses the armored/metallic hit profile (cosmetic only).

## Gimmicks

- **1 Artifact on entry.** The first *visible debuff* aimed at it is eaten and the Artifact is consumed. This blanks the obvious counterplay — the fight's damage is concentrated in one telegraphed hit, so the natural answer is Weak — and guarantees the first Weak whiffs. Cheap throwaway debuffs strip it; players who lead with their real one are down a card.
- **Frail is timed, not incidental.** Frail lands on the Fast Punch turn, which is *immediately before* Strong Punch. Debuffs applied to players skip their first duration tick, so the stack survives the player's next turn and expires at the end of the following enemy turn — meaning the 25% Block reduction is live exactly on the turn the player wants to block the 14 (16). This is the whole design: the small multi-hit turn is a setup for the big single-hit turn, and the enemy is deliberately punishing block-based defense on the one turn block matters most. Frail multiplies *block gain* by 0.75; it does not touch HP or damage.
- **Ready is a real tempo tax, every cycle.** Unlike enemies that block once on entry, the Punch Construct re-blocks **10 every third turn** for the entire fight. Against a 55-HP body that is ~18% of its effective health restored per cycle, and it lands on a turn where the player takes no damage and is therefore most likely to be attacking. Damage aimed at the Ready turn is partly wasted; damage aimed at the two punch turns lands clean.
- **The player's optimal rhythm is the inverse of the enemy's.** Attack on the punch turns (no block up), defend into the Frail→Strong Punch pair, and try not to spend a big attack into a fresh 10 Block. The fight is short enough that one mistimed cycle is a meaningful fraction of the total damage taken.
- **Two-hit split on Fast Punch.** Flat per-hit damage reduction gets double value on the Fast Punch turn and single value on Strong Punch; thorns/retaliate effects likewise trigger twice. The pair of moves reads very differently to per-hit versus per-turn defenses.
- **`PunchOff` variant.** In the event, both constructs enter with **2–9 HP already shaved off** (independently rolled per body, floored at 1 HP), and one of them starts on Fast Punch instead of Ready. Practical effect: the two bodies are one turn out of phase, so the party sees a punch turn from one of them almost every turn rather than a clean shared "everyone blocks" beat — and both are a little easier to kill than a fresh one. The event's idle punching animation before combat is cosmetic and deals no damage. Taking the fight is opt-in and pays a relic **and** a potion **per player**.
- **Deterministic to the end.** No summons, no revive, no HP-threshold branch, no RNG in the machine.

## Scaling by act / ascension

- **Act:** none. Punch Construct is Act 1 content and reads no act index; the only act-derived factor touching it is the multiplayer scaler below (act index 0 → factor **1.1**).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP 55 → **60**.
  - *Deadly Enemies* tier: Strong Punch 14 → **16**, Fast Punch 5 → **6** per hit (so 10 → 12 on that turn).
  - The Frail, the Block, and the Artifact are **not** ascension-scaled — the shape of the fight is identical at every ascension, only its three constants move.

## Multiplayer / seat-count adjustments

- **HP scales by (player count × 1.1)** at act index 0, applied at creature creation. 55 → **121** at 2 players, **~181** at 3. At the *Tough Enemies* tier: 132 / 198. In `PunchOff` the flat 2–9 reduction is applied *after* scaling, so it is a proportionally smaller dent the more seats are present.
- **The Ready block scales the same way** — monster-move block is multiplied by (player count × act factor). 10 → **22** at 2 players, **33** at 3. Because the block recurs every cycle, this is the single most seat-sensitive number in the kit: the party's per-cycle overkill requirement grows with seat count *and* repeats.
- **Artifact scales with seats:** granted as `1 + (players − 1)`, so **2** Artifact at 2 players and **3** at 3. In 3-player co-op the party must burn three throwaway debuffs before any real Weak sticks — an expensive tax on the only clean answer to Strong Punch.
- **Damage does not scale per seat, but it is applied to every seat.** Both attacks target all opposing player creatures rather than picking one: Fast Punch hits **every** player twice for its listed damage, Strong Punch hits **every** player once. Each individual seat sees exactly the single-player table; the party's total incoming damage is that table times seat count.
- **Frail does not scale** — power scaling only applies to powers landing on enemies — so every player gets exactly **1 Frail** on each Fast Punch turn. The timing pressure is identical at every seat count.
- Net effect: HP up ~2.2× / 3.3× and recurring Block up 2.2× / 3.3×, while the damage rate per seat stays flat. More seats means a noticeably longer fight against a flat damage curve — annoying rather than dangerous, the opposite of the Cubex's behavior in the same room.

## Fight-class reasoning — `mixed`

Each beat of the three-turn ring asks the player for a genuinely different thing, and no one axis dominates. The Ready turn is an offense-timing problem (10 recurring Block on a 55-HP body — hit it on the wrong turn and a chunk of your damage evaporates); the Fast Punch turn is chip damage plus a *scheduled* Frail; the Strong Punch turn is a mitigation check deliberately made harder by the Frail applied the turn before. `spike` overstates it — 14 (16) on a fixed three-turn clock with no ramp is a bump, not a burst, and the fight is usually dead in two cycles. `attrition` is wrong on a flat 24-per-cycle curve against a body that dies quickly, and `gimmick` over-weights the Artifact, which delays counterplay by one card rather than posing a puzzle.
