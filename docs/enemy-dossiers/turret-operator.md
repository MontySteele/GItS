# Turret Operator — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `TurretOperator`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `TurretOperatorWeak` — a *weak* (early-act) encounter that always spawns exactly **two** bodies: a **Living Shield** and one **Turret Operator**. The Turret Operator appears in no other encounter. It is never fought alone.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

A three-state move machine with **zero randomness**, **no conditional branches**, and **no HP thresholds**. Every transition is a hard-wired follow-up, so the whole fight is readable from turn one.

The two distinct moves:

1. **Unload** — shows a *multi-attack* intent (damage × 5). Five hits, one attack animation played once (the five impacts land under a single swing), blunt hit FX.
2. **Reload** — shows a *buff* intent. Plays a hand-crank animation and grants the Turret Operator **+1 Strength**, permanently, to itself.

Wiring: **Unload → Unload → Reload → Unload → Unload → Reload → …** forever. The machine starts on the first Unload, so turn 1 is an attack. There is no opening buff turn, no defend move, and no debuff move anywhere in the kit — the Turret Operator never gains Block on its own initiative (see Gimmicks for where its Block actually comes from).

Note the machine holds two *separate* Unload states rather than one state that repeats. Functionally identical to the player, but it means the "two shots then crank" rhythm is structural and cannot be broken, skipped, or re-rolled by anything the player does.

Observed sequence (base numbers, no ascension):

| Turn | Move | Strength | Damage shown |
| --- | --- | --- | --- |
| 1 | Unload | 0 | 3 × 5 = **15** |
| 2 | Unload | 0 | 3 × 5 = **15** |
| 3 | Reload | 0 → +1 | — |
| 4 | Unload | +1 | 4 × 5 = **20** |
| 5 | Unload | +1 | 4 × 5 = **20** |
| 6 | Reload | +1 → +2 | — |
| 7 | Unload | +2 | 5 × 5 = **25** |
| 8 | Unload | +2 | 5 × 5 = **25** |
| 9 | Reload | +2 → +3 | — |
| 10–11 | Unload | +3 | 6 × 5 = **30** each |

Every three turns the fight loses one attack turn and gains **+5 per remaining attack turn** thereafter. Averaged over the cycle the Turret Operator deals 10 / 13.3 / 16.7 / 20 damage per turn across cycles 1–4.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP | **41** (fixed — min and max are identical, no roll) | **51** (Tough-Enemies tier) |
| Fire damage, per hit | 3 | 4 (Deadly-Enemies tier) |
| Hits per Unload | **5** (hard-coded; never scales) | 5 |
| Unload total, turn 1 | 15 | 20 |
| Reload Strength gain | +1 | +1 (no ascension scaling) |
| Block gained by its own moves | **0** — it has none | 0 |

**The hit count is the load-bearing number.** Because Unload is five separate hits, every point of Strength is worth **+5 damage per Unload**, not +1. A single Reload is a 33% damage increase; three Reloads double it. Conversely, per-hit damage is low enough (3, or 4 at the Deadly tier) that any effect reducing damage *per hit* is unusually strong against this enemy, while a flat Block pool absorbs the whole volley at face value.

Its HP is the lowest-variance stat in the encounter: **41 flat**, no band, no roll. That is a deliberately soft body — roughly 60% of its Living Shield partner's — and the fight is built around the player not being able to reach it (below).

## Gimmicks

- **The Rampart interaction is the whole fight.** The Living Shield enters combat carrying a large counter-style buff (Rampart, **25**). At the start of **each player turn** that buff grants Block equal to its counter to **every Turret Operator on the enemy side**. So the Turret Operator is handed **25 Block per turn, for free, indefinitely**, and never spends a turn of its own doing it. The counter does not decay. The Living Shield holds the buff, so the block feed only stops when the **Living Shield** dies.
- **A hard damage threshold, not a damage race.** 25 Block/turn against a 41 HP body means any turn dealing 25 or less into the Turret Operator accomplishes literally nothing. Chip damage and multi-small-hit decks are shut out; you need a ≥66-damage turn to kill it through the shield, or you kill the Living Shield first.
- **Killing the Living Shield is not free either.** The Living Shield's own machine branches on ally count: while the Turret Operator is alive it repeats a light 6-damage Shield Slam; the moment it is the **last enemy standing** it switches permanently to a heavy Smash (16, or 18 at the Deadly tier) that also grants **itself +3 Strength every turn**, escalating without limit. So the encounter poses a real order-of-kill question: shoot the shield first and you turn a 6-damage chip enemy into a runaway Strength engine while the turret keeps firing; shoot the turret first and you must punch through 25 Block a turn to do it.
- **No Block, no heal, no summon, no artifact, no debuff.** The Turret Operator applies nothing to the player — no Weak, no Frail, no status cards. It is pure, escalating, undodgeable numeric pressure with a borrowed defensive layer.
- **Strength is self-applied and permanent.** It cannot be stripped by killing the partner, and it is a genuine buff (not a counter), so Strength-removal effects are the only counterplay to the ramp.
- Damage feedback reads as fur rather than armor — cosmetically it is a creature operating a machine, not a construct, which matters only for damage-type flavor cues.

## Scaling by act / ascension

- **Act:** none. Turret Operator is Act 3 content only and appears in exactly one Act 3 weak encounter. Its numbers do not read the act index; the only act-derived factor that touches it is the multiplayer scaler below (Act 3 non-boss factor **1.2**).
- **Ascension:** two independent, tier-keyed bumps, and both are small.
  - *Tough Enemies* tier: HP **41 → 51** (+24%).
  - *Deadly Enemies* tier: fire damage **3 → 4** per hit, i.e. Unload **15 → 20** and every Strength stack still worth +5. The ramp table becomes 20 / 20 / crank / 25 / 25 / crank / 30 / 30 …
  - The hit count (5), the Reload gain (+1), the two-shots-then-crank cycle, and the Living Shield's Rampart value are **not** ascension-scaled. Ascension makes this enemy hit harder and live slightly longer; it does not change how the fight is solved.

## Multiplayer / seat-count adjustments

- **HP scales hard.** On combat entry, enemy max HP is multiplied by (player count × act factor); Act 3 non-boss is **1.2**. A 2-player Turret Operator sits at **98 HP** (41 × 2 × 1.2) and a 3-player one at **147** — 122 / 183 at the Tough-Enemies tier. The Living Shield alongside it scales the same way (65 base → 156 / 234).
- **The Rampart block feed scales too, and this is the seat-count headline.** Rampart is flagged to scale in multiplayer, so the counter is inflated at application time by (player count × 1.2): **25 → 60 at two seats, 90 at three**. The Block it grants each turn is flagged unpowered and therefore is *not* multiplied a second time by the block scaler — one scaling, not two. Still, a three-seat party faces a 147 HP turret being handed **90 Block every single turn**, i.e. a 237-damage focus-fire threshold to kill it in one turn. In practice multiplayer converts "should we kill the turret first?" from a judgement call into "no."
- **Damage does not scale, but it is applied per seat.** Monster attacks resolve against all opposing player creatures with the target list refreshed per hit, so Unload hits **every player five times** for its listed per-hit damage. Party-wide incoming damage therefore scales linearly with seat count while the party's total HP pool does too — per-seat pressure stays flat.
- **Strength gain is seat-count independent.** Reload is +1 at any seat count, so the ramp table above is unchanged; it simply applies to more targets.
- Net effect: at higher seat counts the turret's *offense* is unchanged per player while its *defense* becomes near-absolute, which pushes every party toward the same solution — burn the Living Shield, accept the Smash escalation, and race the turret's Strength ramp with a fully exposed, un-shielded, low-HP target.

## Fight-class reasoning — `mixed`

Per turn this fight asks two unrelated questions at once, which is exactly what `mixed` is for. Defensively it is an attrition ask: a deterministic, fully telegraphed 15 → 20 → 25 → 30 escalation with no burst turn to fear and no random spike, demanding unbroken per-turn mitigation that must grow on the same three-turn clock the enemy grows on. Offensively it is a gimmick ask: the Rampart feed puts a hard 25-Block-per-turn floor (60/90 in co-op) in front of a deliberately soft 41 HP body, so raw throughput is useless and the fight resolves on a targeting decision — break the shield and face an escalating +3 Strength Smash, or out-burst the block gate. Labelling it pure `attrition` would ignore that the correct play is a one-time structural choice rather than a grind, and labelling it pure `gimmick` would ignore that the Strength ramp punishes taking too long to make that choice.
