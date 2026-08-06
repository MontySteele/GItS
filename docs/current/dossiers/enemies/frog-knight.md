# Frog Knight — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `FrogKnight`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `FrogKnightNormal` — a solo encounter that spawns exactly **one** Frog Knight in the default slot. No allies, no summons, no reinforcements.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Frog Knight runs a **fully deterministic** four-move machine with one conditional branch. No RNG is consulted anywhere in its AI, so the entire fight is readable from turn one.

The four moves:

1. **Tongue Lash** — shows an *attack* intent **and** a *debuff* intent. One hit, then applies **Frail 2** to every player.
2. **Strike Down Evil** — shows a single *attack* intent. One heavy hit.
3. **For the Queen** — shows a *buff* intent. Gains **+5 Strength** (permanent, no cap).
4. **Beetle Charge** — shows a single *attack* intent. One very heavy hit, fires **at most once per fight**.

Wiring: the machine opens on **Tongue Lash**, then Tongue Lash → Strike Down Evil → For the Queen → *(branch)*. Beetle Charge, when taken, returns to Tongue Lash.

The branch is a half-health check evaluated **only in the slot immediately after For the Queen**:

- If the Frog Knight has **already used Beetle Charge**, or its current HP is **≥ half** its max, it goes back to Tongue Lash.
- If it has **not** used Beetle Charge and current HP is **< half** max, it takes Beetle Charge.

Two consequences worth internalizing:

- **The half-health check is only polled every third turn.** Dropping the Frog Knight below 50% on, say, its Strike Down Evil turn does nothing until the next For the Queen resolves. You can drop it below half and still eat two ordinary turns before the charge arrives.
- **The charge flag latches permanently.** Once Beetle Charge has been used, the branch condition can never select it again — the rest of the fight is a clean three-beat loop, no matter how low the enemy's HP goes.

The baseline loop, therefore:

| Turn | Move | Effect |
| --- | --- | --- |
| 1 | Tongue Lash | attack + Frail 2 |
| 2 | Strike Down Evil | heavy attack |
| 3 | For the Queen | +5 Strength |
| 4 | Tongue Lash **or** Beetle Charge | (branch fires here, once) |
| 5 | Strike Down Evil (or Tongue Lash if 4 was the charge) | … |

Because Frail 2 is refreshed every third turn and ticks down at the end of each enemy turn, Frail uptime is roughly **two turns on, one turn off** — the player gets exactly one clean blocking turn per cycle, and it is the buff turn.

## Numbers

| Value | Base | Ascension-tier value |
| --- | --- | --- |
| Starting HP (fixed, no roll) | **191** | **199** (Tough Enemies) |
| Plating (starting armor counter) | **15** | **19** (Tough Enemies) |
| Tongue Lash damage | 13 | 14 (Deadly Enemies) |
| Tongue Lash Frail | 2 | 2 (not scaled) |
| Strike Down Evil damage | 21 | 23 (Deadly Enemies) |
| Beetle Charge damage | 35 | 40 (Deadly Enemies) |
| For the Queen Strength | +5 | +5 (not scaled) |

HP is a **fixed** value — min and max initial HP are the same number — so there is no per-run HP roll to hope for.

Effective damage with the Strength ramp folded in (base / Deadly-Enemies tier), before Frail, Weak, block, or player modifiers:

| Cycle | Strength during cycle | Tongue Lash | Strike Down Evil | Beetle Charge (if it fires this cycle) |
| --- | --- | --- | --- | --- |
| 1 (turns 1–3) | 0 | 13 / 14 | 21 / 23 | — |
| 2 (turns 4–6) | +5 | 18 / 19 | 26 / 28 | 40 / 45 |
| 3 (turns 7–9) | +10 | 23 / 24 | 31 / 33 | 45 / 50 |
| 4 (turns 10–12) | +15 | 28 / 29 | 36 / 38 | 50 / 55 |
| 5 (turns 13–15) | +20 | 33 / 34 | 41 / 43 | 55 / 60 |

Damage per full cycle climbs by **+10** every three turns and never stops. There is no enrage timer as such; the Strength ramp *is* the timer.

Frail reduces block gained to 75% for its duration (2-turn counter, ticks at end of the enemy turn). It affects only the player's block, not the Frog Knight's own armor — see below.

## Gimmicks

- **Plating is the fight.** The Frog Knight enters combat carrying a counter-style armor buff at 15 (19 at the Tough-Enemies tier). It grants Block equal to its current amount **before the player's first turn** and again **at the end of every enemy turn**, and the counter decrements by 1 at the start of each enemy turn from round 2 onward. So the wall reads roughly 15, 15, 14, 13, 12, … 1, then vanishes around turn 16.
  - Cumulative Block the player must chew through if the fight goes the distance: **≈135 base / ≈209 at the Tough-Enemies tier** — on top of 191/199 HP. The real health pool is closer to **325–410**.
  - The armor block is granted as *unpowered* value, which matters mechanically: it is not affected by the player's Weak/Frail-style block modifiers and is not touched by the multiplayer block scaler (Plating carries its own multiplayer rule instead — see below).
- **A per-turn damage floor.** Because fresh Block lands at the end of every enemy turn, any player turn dealing less than the current Plating amount accomplishes *literally nothing*. Early on that floor is 15 (19); it decays about 1 per turn. Chip damage, single small attacks, and thorns-style trickle are structurally dead until the counter has worn down.
- **Frail on a 2-of-3 duty cycle.** Tongue Lash's Frail 2 is applied to **all** player creatures, and lands every third turn, so the player's block cards are at 75% efficiency for two of every three turns — including the turn Strike Down Evil (the second-biggest hit) resolves.
- **One telegraphed spike, exactly once.** Beetle Charge is the single biggest hit in the kit (35/40 base, 40–55 with accumulated Strength) and it is announced a full player turn in advance. It is a one-shot event: no repeat, no second phase.
- **Hits read as armored.** Damage feedback uses the armor sound profile; cosmetic, but consistent with the Plating read.
- No summons, no minions, no HP-threshold behavior beyond the single Beetle Charge branch, no healing, no artifact/thorns-style retaliation.

## Scaling by act / ascension

- **Act:** none. Frog Knight is Act 3 content only and reads no act index of its own. The only act-derived factor touching it is the multiplayer scaler below (Act 3, non-boss → ×1.2).
- **Ascension:** two independent tier-keyed bumps.
  - *Tough Enemies* tier: HP 191 → **199**; Plating 15 → **19**. The Plating bump is the larger real change — it adds four more turns of wall and raises the per-turn damage floor by 4, worth roughly +74 effective HP over the fight.
  - *Deadly Enemies* tier: Tongue Lash 13 → 14, Strike Down Evil 21 → 23, Beetle Charge 35 → 40.
  - Frail amount and the +5 Strength gain are **not** ascension-scaled at any tier.

## Multiplayer / seat-count adjustments

- **HP scales by seat count × act factor.** Enemy max HP is multiplied by (player count × 1.2) for a non-boss Act 3 room. Approximate bodies:

  | Seats | Base HP | Tough-Enemies HP |
  | --- | --- | --- |
  | 1 | 191 | 199 |
  | 2 | ~458 | ~478 |
  | 3 | ~688 | ~716 |
  | 4 | ~917 | ~955 |

- **Plating scales on its own, aggressive curve.** The armor counter is a multiplayer-scaling power whose applied amount is multiplied by **((seats − 1) × 2 + 1)** — ×1 solo, **×3 at two players, ×5 at three, ×7 at four**. Its per-turn decrement also changes: for enemies it steps down by **one per player** each turn instead of by 1.
  - At two players, base Plating: starts at **45**, decays 2/turn, lasts ~23 turns, and grants a cumulative **~575 Block**. At three players it starts at **75**, decays 3/turn, and grants roughly **~1,000 Block** over the fight.
  - The practical effect is that the party's *combined* per-turn damage floor scales with seat count roughly the way HP does, so the "chip damage is dead" rule does not soften in co-op — it hardens.
- **Attacks hit every seat.** Monster attacks target all opposing player creatures with the target list refreshed per hit, so Tongue Lash, Strike Down Evil, and Beetle Charge each land on **every** player for the listed damage. Per-seat incoming damage is therefore flat with seat count while the health-plus-armor pool multiplies.
- **Frail is applied to all player creatures**, not one — the 75%-block tax is party-wide.
- **Strength gain is seat-count independent.** +5 per buff turn at any seat count, so the ramp table above is unchanged in co-op even though the fight lasts far longer — meaning higher seat counts reliably reach the +15/+20 Strength tiers that a solo run usually ends before seeing.

## Fight-class reasoning — `attrition`

What this fight demands, turn after turn, is a *damage floor*: fresh Block equal to the Plating counter lands at the end of every enemy turn, so any turn that fails to clear ~15 (19 at the Tough tier, 45–75 in co-op) is a turn that literally did not happen. Combined with a fixed 191/199 HP body, that armor stream turns a nameplate-normal encounter into a 325–410 effective pool that must be ground down while Frail 2 keeps the player's block at 75% for two turns out of every three. The Strength ramp (+5 per cycle, uncapped) means the grind is *timed* rather than open-ended, but it never produces a burst the player must specifically survive — it just widens the arithmetic gap the longer you take. `spike` would over-weight Beetle Charge, which fires exactly once and is telegraphed a full turn ahead; `gimmick` would mistake Plating for a puzzle when it is simply a large, decaying second health bar; the demand curve here is flat, high, and sustained, which is `attrition`.
