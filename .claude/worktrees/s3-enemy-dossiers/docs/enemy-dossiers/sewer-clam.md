# Sewer Clam — behavior dossier

- **Class:** `SewerClam`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounter:** `SewerClamNormal` — a solo encounter that spawns exactly **one** Sewer Clam in an unnamed default slot. No adds, no allies, no summons anywhere in the kit.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Sewer Clam runs a **two-state move machine with zero randomness and zero branching**. Both states point at each other as hard-wired follow-ups, so the fight is a strict alternation that the player can read from turn one and predict forever.

The two moves:

1. **Pressurize** — shows a *buff* intent. Grants itself **+4 Strength**, permanently, with no upper bound. No block, no debuff, no damage.
2. **Jet** — shows a *single-attack* intent. One blunt hit on a player.

The machine's **initial state is Jet**, not Pressurize. So the clam opens by hitting you, and the buff turn is always the *even* turn:

| Turn | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | … |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Move | Jet | Pressurize | Jet | Pressurize | Jet | Pressurize | Jet | Pressurize | Jet | alternating forever |

There is no HP-threshold branch, no enrage, no "first turn only" special case in the move machine, and no state the clam can get stuck in. Every second turn is a free turn for the player in damage terms — and every one of those free turns makes the next attack 4 points worse.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP (fixed, no roll) | 56 | **58** at the Tough-Enemies tier |
| Opening Plating counter | 8 | **9** at the Tough-Enemies tier |
| Jet damage (before Strength) | 10 | **11** at the Deadly-Enemies tier |
| Pressurize Strength gain | +4 | +4 (no ascension scaling) |

HP is a fixed value — min and max initial HP are the same number — so unlike most Act 1 bodies there is no HP roll and no variance between runs. Damage feedback reads as **stone**, consistent with the shell.

Because Pressurize is unbounded and lands every other turn, Jet's damage escalates linearly and never stops:

| Turn | 1 | 3 | 5 | 7 | 9 | 11 | 13 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Strength | 0 | +4 | +8 | +12 | +16 | +20 | +24 |
| Jet (base) | 10 | 14 | 18 | 22 | 26 | 30 | 34 |
| Jet (Deadly-Enemies tier) | 11 | 15 | 19 | 23 | 27 | 31 | 35 |

The attack intent displays the *modified* number, so the player always sees the escalated hit a turn in advance.

## Gimmicks

- **Plating is the whole defensive kit.** The clam applies a counter-style Plating buff to itself as it enters the room — it is not a move and cannot be prevented by killing tempo. Plating does three things: it grants Block equal to its remaining count at the **start of the first round**, it grants Block equal to its remaining count at the **end of every enemy turn**, and it **ticks down by 1 per round** from round 2 onward. When it reaches 0 the clam is naked for the rest of the fight.
- **The block schedule is therefore a decaying wall, front-loaded.** Solo, base tier: 8 Block before the player's first turn, then 8 / 7 / 6 / 5 / 4 / 3 / 2 / 1 laid down at the end of each of the clam's first eight turns. That is roughly **44 points of block** on top of 56 HP — an effective pool near **100** if none of it is wasted — but all of it is spent by around turn 9, exactly when Jet is hitting for 26+.
- **The two clocks run opposite directions and cross.** Defense decays 1/turn while offense grows 4/two-turns. Early turns are trivially survivable and hard to hurt; late turns are soft to hurt and lethal to sit through. The fight's entire tension is whether the player closes before the crossover.
- **Block is per-turn, so chip damage is structurally punished.** Because the clam re-lays its Block every enemy turn, any player turn that deals less than the current Plating count accomplishes literally nothing. A deck that deals 6 a turn does not kill this enemy slowly — it does not kill it at all until Plating decays under 6. Concentrated damage beats spread damage by a wide margin here.
- **The buff turn is not a rest turn.** Pressurize deals no damage, which invites the player to spend their block cards elsewhere — but the clam still lays Plating block at the end of that same turn, so the "free" turn is also the turn the wall gets re-erected. Skipping offense on Pressurize turns is the main way players lose this fight slowly.
- No debuffs applied to the player at any point. No block-removal, no artifact, no thorns, no retaliation on being hit.

## Scaling by act / ascension

- **Act:** none. Sewer Clam is Underdocks (Act 1) content only, and none of its numbers read the act index. The act index enters only through the multiplayer scaler below (Act 1 factor = **1.1**).
- **Ascension:** two independent tier-keyed bumps, and they hit different halves of the fight.
  - *Tough Enemies* tier: HP 56 → **58**, and opening Plating 8 → **9**. The Plating bump is the larger of the two in practice: one more stack adds one more block-laying turn *and* raises every earlier turn's block by 1, worth roughly +17 effective HP on its own (9+9+8+…+1 ≈ 54 block vs ≈ 44), against +2 from the HP line.
  - *Deadly Enemies* tier: Jet 10 → **11**. This shifts the whole escalation table up by 1 without changing its slope.
  - The **Strength gain is not ascension-scaled** — the ramp is +4 per buff turn at every ascension level. Ascension makes the clam tankier and its opening hit harder; it does not make it ramp faster.

## Multiplayer / seat-count adjustments

- **HP scales by seats × act factor.** On combat entry, enemy max HP is multiplied by (player count × 1.1) for an Act 1 non-boss room. A 2-player clam sits near **123 HP** (2 × 1.1 × 56), a 3-player clam near **185**; at the Tough-Enemies tier, roughly 128 / 191.
- **Plating scales on the amount, and only once.** Plating declares itself multiplayer-scaling and multiplies its applied amount by `((seats − 1) × 2 + 1)` — ×1 solo, **×3 at two players**, **×5 at three**. So the opening counter is 8 / 24 / 40. Its per-turn decrement is also raised to equal the player count, so the *duration* stretches rather than the count simply running out faster: 24 counting down by 2 lasts 12 rounds, 40 counting down by 3 lasts ~13. The block it lays is flagged as unpowered, so the general enemy-block multiplier does **not** apply on top — the scaling is applied once, at the power's amount, not twice.
- **The co-op block wall is the real difficulty spike.** Total block laid over the fight goes from ~44 solo to roughly **160 at two seats** and **~290 at three** — far outpacing the HP multiplier. Combined with the per-turn reset rule, a co-op party that cannot concentrate 24+ damage into a single turn makes zero net progress for the first several rounds.
- **Damage does not scale with seat count, and Strength does not either.** Jet's listed damage and the +4 per Pressurize are seat-count independent; the attack is applied against the opposing side, so per-seat incoming pressure stays flat while the health-plus-block pool grows several-fold.
- **Net effect:** co-op makes the fight much longer without making any individual turn much scarier — which is precisely the wrong direction against an enemy whose damage grows with turn count. A 3-seat clam that survives to turn 15 is jetting for 34+ every other turn at a party that only ever prepared for 10.

## Fight-class reasoning — `attrition`

What this fight asks for, every single turn, is **throughput above a moving floor**: the clam re-lays Block equal to its Plating count at the end of each of its turns, so the player's damage is measured against a threshold rather than accumulated freely, and any turn under that threshold contributes nothing at all. That is the defining attrition ask — sustained, right-sized, concentrated damage over many turns against an effective pool near 100 solo and 300+ in three-seat co-op — and it is doubled by the fact that the clam's only offensive act is a single predictable hit that never needs a defensive spike answered on short notice. The escalating Strength is a *clock on the attrition check*, not a spike phase: it is telegraphed a full turn ahead, it grows in small fixed steps, and it only becomes lethal if the player has already failed the throughput test for many rounds. `gimmick` would over-read the Plating decay (it is a stat curve, not a puzzle with a solution), and `spike` misreads a 4-point-per-two-turns ramp as burst when nothing in the kit ever demands a big block turn out of nowhere.
