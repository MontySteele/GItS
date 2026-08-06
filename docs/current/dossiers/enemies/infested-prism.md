# Infested Prism — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `InfestedPrism`
- **Kind:** elite
- **Act:** Act 2 (`Hive`, act index 1)
- **Encounter:** `InfestedPrismsElite` — a solo elite. One Prism, one slot, no minions, no reinforcements, no second wave despite the plural encounter name. The encounter pre-loads the **Tainted** affliction overlay art, which is the tell that the card-tax is the point of the fight.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

There is no randomness in this AI at all. Four moves are wired into a closed ring, each naming the next as its follow-up, and the machine starts on Jab:

> **Jab → Radiate → Whirlwind → Pulsate → Jab → …**

No weights, no repeat limits, no HP-threshold branch, no cooldowns, no conditional nodes, no bestiary-hidden moves (all four appear in the codex). The standard "the first move never transitions away" rule means turn 1 is always the Jab. Once the player has seen one lap they know every turn of the fight — including, critically, exactly which turn is safe to play Skills on and which turn is not.

| Turn (mod 4) | Move | Telegraph shown | Effect |
| --- | --- | --- | --- |
| 1, 5, 9, … | **Jab** | single-attack intent | one hit |
| 2, 6, 10, … | **Radiate** | single-attack intent **+ defend** icon | one hit, then it gains Block |
| 3, 7, 11, … | **Whirlwind** | multi-attack intent, **×3** | **three separate hits** |
| 4, 8, 12, … | **Pulsate** | single-attack intent **+ buff + defend** icons | one hit, a large Block gain, then **+2 to its own Vital Spark counter** |

### Why the cycle order matters

The ring is built so that the enemy's own escalation and the player's punish-window collide. The Vital Spark counter — which sets how much the player pays for every Skill they play — rises on **Pulsate**, the turn immediately before the ring loops back to Jab. Two turns after that raise comes **Whirlwind**, the only multi-hit move, and the Tainted tax is applied **per hit taken**, not per turn. So the fight's damage peak is always "the newly-raised tax, tripled," and it lands on a fixed, publicly announced schedule.

The two Block turns (Radiate, Pulsate) are also the two turns that carry riders, so the player cannot cleanly separate "the turn I race the body" from "the turn I answer the gimmick."

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| HP | **161**, fixed (min = max, no roll) | **171** at the *Tough Enemies* tier |
| Jab damage | 15 | 17 at the *Deadly Enemies* tier |
| Radiate damage | 11 | 13 at the *Deadly Enemies* tier |
| Radiate Block | 11 | 13 at the *Deadly Enemies* tier |
| Whirlwind damage | 5 **×3 hits** (15 total) | 6 ×3 (18 total) at the *Deadly Enemies* tier |
| Pulsate damage | 8 | 10 at the *Deadly Enemies* tier |
| Pulsate Block | 20 | **22 at the *Tough Enemies* tier** |
| Vital Spark, applied at combat start and again per Pulsate | 2 | 3 at the *Deadly Enemies* tier |
| Whirlwind hit count | 3 | — (fixed, not ascension-keyed) |

**Note the ascension-key asymmetry.** Radiate's Block is keyed to the *damage* ascension tier while Pulsate's Block is keyed to the *toughness* tier. Everything else follows the obvious key. A run sitting at the Tough tier but below Deadly gets a tougher Pulsate wall and an unchanged Radiate; a run at Deadly gets the opposite. This is almost certainly deliberate (the Radiate Block is a small attack-shaped rider, the Pulsate Block is the real wall) but it means the two defensive numbers move on different ascension steps.

### Raw damage per lap (single player, base tier, before any Tainted tax)

| Turn | Move | Incoming | Block gained | Vital Spark after |
| --- | --- | --- | --- | --- |
| 1 | Jab | 15 | — | 2 |
| 2 | Radiate | 11 | 11 | 2 |
| 3 | Whirlwind | 5/5/5 = **15** | — | 2 |
| 4 | Pulsate | 8 | 20 | **4** |
| 5 | Jab | 15 | — | 4 |
| 6 | Radiate | 11 | 11 | 4 |
| 7 | Whirlwind | 5/5/5 = **15** | — | 4 |
| 8 | Pulsate | 8 | 20 | **6** |

**49 raw damage per four-turn lap — about 12 a turn.** That is soft for an Act 2 elite, and it is supposed to be: the printed numbers are not where this fight's damage comes from. It also gains **31 Block per lap**, so its effective health is roughly 161 + 31 per lap survived; a deck killing it in two laps must push ~28 a turn through an intermittent wall, and a deck taking four laps is facing ~285 effective HP.

## Gimmicks

- **Vital Spark → Tainted → self-inflicted damage amplification.** This is the whole encounter.
  - The Prism applies **Vital Spark to itself the moment it is added to the room**, at 2 (3 at the Deadly tier). It is a counter-style buff on the enemy, not on the player.
  - At combat start, Vital Spark afflicts **every Skill card in every player's combat deck** with **Tainted**, at the counter's current value. Any Skill card that *enters* combat later (generated, added, transformed in) is afflicted too — but only if it does not already carry some other affliction; a card already afflicted is spared.
  - **Playing a Tainted card gives its own player that many stacks of Tainted Power.** Tainted Power is a debuff counter on the player creature that adds its amount to **every instance of incoming damage from a monster move**. It is removed at the end of the enemy's turn, so it is live for exactly one enemy turn: the one right after the play.
  - **It is additive per damage instance, so multi-hit attacks multiply it.** This is the load-bearing interaction. Two Skills played at Vital Spark 4 is +8 per hit; into Jab that is 15 → 23, into Whirlwind it is 5/5/5 = 15 → 13/13/13 = **39**.
  - Raising the counter **retroactively re-prices every already-Tainted card in play** — the affliction amounts are rewritten to the new value, they do not stay at the value they were stamped with. Killing or otherwise stripping Vital Spark **clears every Tainted affliction at once**, so any effect that removes an enemy buff is a full answer to the fight.
- **The tax is aimed squarely at Block.** Defensive cards are Skills. The player's normal response to a telegraphed multi-hit — play Block — is precisely the action that inflates the multi-hit. The fight's per-turn question is not "how much Block do I need," it is "is this a turn where Blocking costs me more than not Blocking."
- **The escalation curve.** Vital Spark 2 → 4 → 6 → 8 on turns 4/8/12. A one-lap fight barely notices the gimmick; a four-lap fight is charging 8 per Skill, 24 per Skill into Whirlwind. Nothing decays it, nothing caps it, and it never spends.
- **The Attack/Power escape hatch.** Tainted can only be applied to Skills. A deck that defends with Powers, mitigates with Attacks, or simply races does not pay the tax at all. This is a fight whose difficulty varies enormously by deck composition rather than by player skill.
- No summons, no death rattle, no self-heal, no enrage threshold, no HP-gated behaviour change. Everything is on the metronome; only the price changes.

## Scaling by act / ascension

- **Act:** none. Infested Prism is Act 2 content only and none of its numbers read the act index. The act index is consumed only by the multiplayer scalers below (Act 2 → factor **1.2**).
- **Ascension:** flat tier-keyed swaps, no behavioural change.
  - *Tough Enemies* tier: HP 161 → **171**, Pulsate Block 20 → 22.
  - *Deadly Enemies* tier: Jab 15 → 17, Radiate 11 → 13 damage **and** 11 → 13 Block, Whirlwind 5 → 6 per hit (15 → **18** total), Pulsate 8 → 10, **Vital Spark 2 → 3**.
  - **Vital Spark is the ascension step that actually matters.** Going from 2 to 3 per Skill is a 50% increase on the tax at every point in the curve, and it compounds through the Pulsate raises (3 → 6 → 9 → 12 rather than 2 → 4 → 6 → 8). A four-lap fight at the Deadly tier is charging 12 per Skill, i.e. **36 per Skill into Whirlwind**. The raw-damage bumps add ~9 to a lap; the Vital Spark bump changes what the player is allowed to do.
  - The move ring, the hit count, and the +2-per-Pulsate raise step are identical at every ascension.

## Multiplayer / seat-count adjustments

- **HP multiplies hard.** Enemy max HP is scaled by (player count × act factor), Act 2 = **1.2**. That puts the Prism at roughly **386** HP at 2 players, **580** at 3, **773** at 4 (≈410 / 616 / 821 at the Tough tier). Applied at creature creation, before any move resolves.
- **Block multiplies by the same factor**, because both Block gains are move-typed and therefore in scope for the multiplayer block scaler. Pulsate's 20 becomes **48** at 2 players, 72 at 3, **96** at 4; Radiate's 11 becomes 26 / 40 / 53. Per lap the Prism gains ~74 Block at 2 players and ~149 at 4 — on top of the inflated body. This is one of the steeper co-op effective-HP curves in its cohort.
- **Damage does not scale, but every attack lands on every seat.** All four moves target all opponents, so Jab, Radiate, Whirlwind and Pulsate each hit *everyone* for the listed number. Party-wide incoming grows linearly with seats on top of the HP and Block inflation.
- **The Tainted tax is per-seat on the supply side and self-inflicted on the demand side.** Vital Spark walks every allied creature that is a player and afflicts *that player's* Skill cards, so **every seat's Skills are Tainted**. But playing a Tainted card applies Tainted Power to **the card's own owner only** — one player's greedy Skill turn does not tax their teammates. The result is that each seat independently negotiates the same puzzle, and the party's total tax scales with how many seats are Skill-heavy.
- **The single Vital Spark counter serves all seats**, and it rises on the same four-turn metronome regardless of seat count. This is where co-op bites: the body has 2.4–4.8× the HP and 2.4–4.8× the Block, so a 4-player fight runs many more laps, so the counter reaches 8, 10, 12+ while every seat is still being asked to Block a tripled multi-hit. The gimmick was priced for a two-lap solo fight and gets substantially harsher per extra seat.
- Any single removal of Vital Spark still clears the affliction from **all** players' cards at once, so one teammate carrying an enemy-buff-stripping effect solves the fight for the whole party — an unusually sharp all-or-nothing co-op swing.

## Fight-class reasoning — `gimmick`

What this fight demands per turn is not throughput and not mitigation — it is a card-type decision: *may I play Skills this turn, and if so how many, given which move is telegraphed?* The printed damage is soft for an Act 2 elite (~12 a turn raw), the ring is fully deterministic, and the body only becomes threatening because Tainted Power converts the player's own defensive plays into damage amplification, applied per hit and therefore tripled on the announced Whirlwind turn. It is not `attrition` — the raw curve is too flat and the fight is decided by deck composition and one binary per-turn choice rather than by sustaining a line — and not `spike`, since the peak turn is scheduled and its size is set by the player's own actions rather than the enemy's. `mixed` overstates it: there is exactly one question, asked every turn, at a price that steps up every fourth turn. Track B should model this as a low, flat baseline demand with a build-dependent multiplier that spikes on a known 4-turn phase and can collapse to near-zero for a deck that answers enemy buffs or simply does not play Skills.
