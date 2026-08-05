# Two-Tailed Rat — behavior dossier

- **Class:** `TwoTailedRat`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0 — the alternate/unlockable Act 1, same index as `Overgrowth`)
- **Encounters:** `TwoTailedRatsNormal` only — **three** rats at start, in an encounter that declares **five** body slots. The two empty slots exist so the rats can fill them mid-fight. There is no weak variant and no mixed encounter; the rat only ever appears with its own kind.
- **Proposed fight class:** `swarm`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Each rat runs a **weighted random branch** with four moves, re-rolled every turn. There is no fixed cycle: after any move the rat returns to the same random hub.

The four moves:

1. **Scratch** — *single-attack* intent. One hit.
2. **Disease Bite** — *single-attack* intent. One smaller hit.
3. **Screech** — *debuff* intent. No damage; applies **1 Frail** to every player.
4. **Call for Backup** — *summon* intent. No damage; adds a **new full-HP Two-Tailed Rat** to the board.

Branch weights depend entirely on one question: **is a summon currently legal for this rat?**

| Situation | Scratch | Disease Bite | Screech | Call for Backup |
| --- | --- | --- | --- | --- |
| Summon **not** available | 1/3 | 1/3 | 1/3 | — |
| Summon **available** | 1/12 | 1/12 | 1/12 | **3/4** |

Those raw weights are then filtered by two repeat rules:

- **Scratch, Disease Bite and Screech cannot repeat back-to-back** on the same rat.
- **Screech additionally carries a 3-move cooldown** — it is unavailable if the rat used it within its last three moves. Over a long fight a single rat's ceiling is therefore one Screech per four turns, and its move mix drifts to roughly 37.5% / 37.5% / 25% (attack / attack / Screech).
- **Call for Backup is once-per-rat** for its own state machine, on top of the shared group cap below.

**Turn 1 is fully deterministic in composition.** The encounter picks one random start index and hands the three rats consecutive indices in a 3-cycle, so the opening turn is always exactly one Scratch, one Disease Bite and one Screech — only *which rat does which* varies by seed. From turn 2 onward every rat rolls independently.

**Summon eligibility** (`CanSummon`) requires all four of:

1. The rat has taken **at least 2 non-summon moves** — an internal counter starts at 2 and ticks down only when Scratch, Disease Bite or Screech resolves. So the earliest a starting rat can telegraph a summon is its **third** turn.
2. The shared **call-for-backup count is below 3**.
3. There is an **empty slot** in the encounter.
4. **No living ally is already telegraphing Call for Backup** — the rats will not double-summon in the same turn.

Consequently the fight has a very characteristic shape: two quiet chip turns, then — if the player has not closed it out — a ~75%-per-eligible-rat scramble to add bodies on turn 3 and 4.

| Turn | What the board does (base numbers, 3 rats) |
| --- | --- |
| 1 | 8 + 6 damage and 1 Frail, guaranteed composition |
| 2 | 3 independent rolls over {Scratch, Bite, Screech}; expected ~9–10 damage plus Frail |
| 3 | First rat becomes summon-eligible; each eligible rat takes the summon branch 75% of the time |
| 4+ | Board is typically 4–5 rats; summons are exhausted by the slot/count caps and the fight settles into pure chip |

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll (per rat) | 17–21 | 18–22 (*Tough Enemies* tier) |
| Scratch damage | 8 | 9 (*Deadly Enemies* tier) |
| Disease Bite damage | 6 | 7 (*Deadly Enemies* tier) |
| Screech Frail applied | 1 | 1 — not ascension-scaled |
| Call for Backup summons | 1 rat | 1 rat — not ascension-scaled |
| Shared summon cap per combat | 3 | 3 — not ascension-scaled |
| Turns before a rat may summon | 2 | 2 — not ascension-scaled |

HP is rolled per body and the game prefers a **distinct** max-HP value per creature on the enemy side while the band allows, so a fresh 3-pack usually sits on three different totals inside 17–21. Summoned rats roll into the same band, so each addition is another ~19 HP the party has to chew through.

The rats have **no block move and no self-buff of any kind** — this is a pure offense statline.

Total pool: **~51–63** for the opening three (54–66 at the Tough-Enemies tier). With the summon cap fully spent it reaches roughly **~95–105** across the fight — i.e. a maximally-permitted rat fight is nearly *double* the HP of a rat fight that is closed out fast. The player's own clock, not the encounter, decides which fight they are in.

Frail reduces block gained to 75% while it lasts, and ticks down at the end of the enemy turn. Screech applies only **1 stack**, so a single Screech is a one-turn tax; sustained Frail requires the pack to keep rolling it, which a 4–5 rat board does frequently even under the per-rat cooldown.

Per-turn output, base numbers, assuming the long-run mix (37.5% Scratch / 37.5% Bite / 25% Screech):

| Living rats | Expected damage/turn | Frail expected/turn |
| --- | --- | --- |
| 3 | ~15.8 | 0.75 |
| 4 | ~21 | 1.0 |
| 5 | ~26.3 | 1.25 |

At the *Deadly Enemies* tier those become roughly 18 / 24 / 30.

## Gimmicks

- **Call for Backup is the whole kit.** The rat has no powers, no thresholds, no death triggers — the only non-linear element is that its damage-per-turn is a function of a body count it can raise itself.
- **The summon budget is shared, not per-rat.** After any rat summons, *every* living rat's counter is set to the running maximum plus one, so the group as a whole gets **at most 3 summons per combat**, no matter how many rats exist. Newly-spawned rats inherit the shared count, so a late arrival cannot reset the budget.
- **But the summon *timer* is per-rat and does not inherit.** Each new rat starts its own 2-move countdown, so it cannot summon on its first two turns either. Combined with the shared cap and the slot limit, the escalation is strictly bounded and front-loaded.
- **Slot geometry caps the board at 5.** The starting three occupy the last three of five slots; summons fill the remaining two — the summon routine takes the *last* free slot, so the board fills inward. Because eligibility re-checks for a free slot each roll, killing a rat **re-opens its slot** and can hand the group back a summon it could not otherwise use (up to the shared cap of 3). Slow, staggered killing is therefore mildly self-defeating, though nowhere near as punishing as a true death-trigger enemy.
- **A summoned rat does not act on the turn it arrives.** It appears, telegraphs an intent, and moves from the following enemy turn — the player gets exactly one turn of warning and one turn to kill it before it contributes.
- **The rats will not stack summon intents.** A rat will not roll Call for Backup while an ally is already telegraphing it, so the board grows by at most one per turn — you never lose two slots in a single turn.
- **Screech is pure tax.** No damage, no self-benefit — 1 Frail on everyone, to make the block that would answer a 5-rat board buy 25% less.
- Cosmetic only: the rat randomises head and barnacle skins per body, so the three rats look individually distinct without any mechanical difference.

## Scaling by act / ascension

- **Act:** none. Two-Tailed Rat is `Underdocks` content only (act index 0). Its damage, HP band and summon caps do not read the act index; the only act-derived factor touching it is the multiplayer HP/block scaler below, which at act index 0 is **×1.1**.
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 17–21 → **18–22** per rat. Small per body, but it applies to summons too — up to 5 bodies of +1.
  - *Deadly Enemies* tier: Scratch 8 → **9**, Disease Bite 6 → **7**. That is +2 per attacking rat per turn, so a full 5-rat board goes from ~26 to ~30 expected damage a turn.
  - Frail amount, summon count, the shared 3-summon cap, the 2-turn summon delay, the branch weights and the pack size are **not** ascension-scaled.

## Multiplayer / seat-count adjustments

- **HP scales by seats.** On combat entry enemy max HP is multiplied by (player count × act factor), and for a non-boss act-index-0 room that factor is **1.1**. A 2-player rat sits at roughly 37–46 HP and a 3-player rat at roughly 56–69. A 3-player fight that goes the distance is a pool north of **300 HP** — and every point of it is HP the party must clear before the summon window closes.
- **Damage does not scale, but it lands on every seat.** Monster attacks target all opposing player creatures rather than picking one, and the target list refreshes between hits. Scratch hits **every** player for its full amount, Disease Bite likewise, and Screech applies its 1 Frail to every player creature. Per-seat incoming damage is identical to solo, so co-op multiplies the party's total damage taken by the seat count while multiplying the HP the party must remove by roughly the same factor.
- **The enemy-block scaler is inert here** — the rats have no block move.
- **The summon caps are seat-count independent.** Three summons, five slots, 2-turn delay, regardless of party size. This is the key asymmetry: enemy HP grows with seats but the escalation budget does not, so the *relative* danger of the summon mechanic falls as seats rise — while the raw HP wall the party must clear inside the same 2-turn window rises sharply. In practice co-op parties almost always see the full 5-rat board, because inflated HP makes it far harder to close the fight before turn 3.

## Fight-class reasoning — `swarm`

The demand this fight makes each turn is **board clearance under a deadline**: three (soon five) low-HP, un-armoured bodies whose individual hits are small and whose threat is entirely additive in the count of living rats. No single turn spikes — the worst incoming turn is roughly 26–30 across a full board, delivered as four or five separate small attacks — and there is no attrition mechanic in the sense of an enemy that outlasts you, since the rats have no block, no healing and a strictly bounded escalation budget. What the encounter actually asks is whether the player can convert damage into *kills* fast enough during the first two turns to shrink the board before the 75%-weighted summon branch unlocks, which makes wide/AoE damage and efficient kill-sequencing the deciding resources — the textbook swarm demand curve. `gimmick` is the near-miss, since Call for Backup is a genuine special rule, but the rule only turns the throughput dial (more bodies, same per-body behaviour) rather than inverting the correct line the way a true gimmick enemy does; the body count sets the demand, so `swarm` is the honest label.
