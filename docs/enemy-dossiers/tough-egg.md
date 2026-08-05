# Tough Egg — behavior dossier

- **Class:** `ToughEgg`
- **Kind:** normal
- **Act:** Act 2 (the Hive; act index 1)
- **Appears in:** `OvicopterNormal` only. It is never placed by the encounter's generator — the encounter spawns the Ovicopter alone into the `ovicopter` slot and reserves five egg slots (`egg1`–`egg5`) that the Ovicopter fills at runtime with its Lay Eggs move.
- **Source read:** decompiled `ToughEgg`, `Ovicopter`, `OvicopterNormal`, `MonsterModel`, `MonsterMoveStateMachine` / `MoveState`, `HatchPower`, `MinionPower`, `Creature` HP setup + `ScaleHpForMultiplayer`, `MultiplayerScalingModel`, `Rng`, the Hive act table. Behavioral notes only; no code reproduced.

## Stat block

| Quantity | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| Egg-phase HP (rolled, inclusive) | 14–18 | 15–19 | — |
| Hatchling HP (rolled on hatch) | 19–21 | 20–22 | — |
| Nibble damage | 4 | — | 5 |

Two independent ascension knobs, same pattern as the rest of the Hive roster: the HP bumps ride on the "Tough Enemies" level, the damage bump on "Deadly Enemies". No act scaling — it exists in exactly one Act 2 encounter and every number is a literal.

Two roll quirks worth carrying into any model of this fight:

- The **egg** HP roll goes through the engine's standard monster-HP path, which is inclusive of the max and additionally tries to hand every creature on the side a *distinct* max-HP value. So three eggs laid together will normally have three different HP totals inside the band, and only fall back to a plain roll once the band is exhausted (which it will be at 5 eggs on a 5-wide band).
- The **hatchling** HP roll is done by hand on hatch with an exclusive upper bound, so the realised band is one point narrower than the model's own Min/Max properties advertise (19–21 rather than 19–22; 20–22 rather than 20–23 under Tough Enemies). Treat 21/22 as the real ceiling.

The egg carries no block, no thorns, no on-death payload.

## Intent pattern

The move machine has two states and no branch, no RNG, no conditional:

1. **HATCH (summon intent).** Its opening state. Follow-up is Nibble.
2. **NIBBLE (single attack intent, 4/5).** Follows itself forever.

So the sequence is fixed and total: hatch once, then nibble every turn until it dies. There is no re-egg, no second hatch, no alternate move.

**Timing.** Eggs are laid during the enemy turn. The state machine suppresses its first transition, so an egg spends the intervening player turn showing the summon (hatch) intent and performs the hatch on the *next* enemy turn — one full player turn of warning. A `Hatch` counter power on the egg displays the countdown: it goes on at 2 stacks when the egg is laid mid-enemy-turn (1 stack if an egg is somehow placed outside the enemy turn) and ticks down at the end of each enemy side turn, so it reads 1 while the player is deciding. The counter is display/telegraph; the state machine is what actually fires the hatch.

The hatch turn deals **no damage**. The egg's damage output is zero on the turn it spawns, zero on the turn it hatches, and 4 (5) per turn from the turn after that, forever.

Targeting on Nibble is the engine default for an untargeted monster attack (one player seat), not scripted.

## Gimmicks

- **Hatching is a full heal and a full cleanse.** This is the whole design. When the egg hatches it strips every power on itself except the minion marker — poison, vulnerable, weak, any stacking debuff the player invested in — and then *sets max and current HP to a freshly rolled 19–21 (20–22)*. Any chip damage dealt to the egg phase is erased; the hatchling comes out at full on a larger pool than the egg had. The fight therefore asks a binary question about every egg: **kill it inside the one player turn it sits there, or get nothing for the damage you spent on it.** A 14–18 HP body that must die *this turn* is the real stat line.
- **It is a renewable resource, not a fixed add count.** The Ovicopter lays three eggs whenever three or fewer of its teammates are alive, into the highest free egg slots (cap of 5 live adds). Its own cycle is Lay → Smash → Tenderizer → (Lay again if ≤3 teammates alive, else self-buff Strength) → Smash → … So clearing eggs efficiently *re-arms the summon branch*, and killing nothing lets the board sit at five nibblers while the Ovicopter starts stacking Strength instead. Both extremes are punishing; that tension is the fight.
- **Two identities in one creature.** Egg and hatchling are the same `Creature` with different names, skins, hurt/death animations and death SFX. The egg picks one of two visual variants at spawn. For bestiary/save-restore purposes the model can be constructed pre-hatched, in which case it skips straight to the hatchling state and the Nibble loop.
- **Minion-flagged.** Eggs carry the minion power, which marks them as *secondary* enemies: their deaths do not trigger the fight's fatal/win check and the power survives its applier's death. Nothing in the model despawns eggs when the Ovicopter dies — the flag exists so the eggs don't count as the fight.
- **The damage is trivial per body and the threat is the count.** One hatchling is 4 (5) a turn. Five hatchlings are 20 (25) a turn on top of the Ovicopter's 16 (17) Smash and its 7 (8) + Vulnerable 2 Tenderizer. The failure mode is a board that quietly compounds while the player answers the big body.

## Multiplayer / seat count

No per-seat logic in the moves: Nibble stays 4 (5) regardless of player count, and the number of eggs laid per Lay is a flat three.

HP is the only seat-aware quantity, and it is scaled in **both** phases:

- Egg-phase HP is scaled by the engine's standard monster-HP multiplier when the creature is added.
- The hatchling HP roll is explicitly scaled by the same formula at hatch time, using the live player count and act index — so hatching does not launder the multiplier away.

Act 2's multiplayer factor is 1.2, so a 2-player table faces ≈2.4× printed HP (egg ≈34–43, hatchling ≈46–53) and 3-player ≈3.6× (egg ≈50–65, hatchling ≈68–79), while the Nibble stays 4/5 and the lay count stays 3. Net co-op effect: the "kill it before it hatches" window closes hard — the one-turn kill threshold on an egg roughly doubles or triples while the reward for hitting it does not, and the fight leans further toward letting eggs hatch and grinding a wide board.

## Proposed fight class: **swarm**

Per turn the Tough Egg asks a width question, not a size one: bodies arrive three at a time up to a cap of five, each individually flimsy and individually near-irrelevant (4–5 damage), and the aggregate is what kills. The hatch timer sharpens that demand rather than changing its shape — it puts a one-turn deadline on the AoE, because damage that does not finish an egg in its single vulnerable turn is refunded to the enemy at full HP, so the fight is specifically testing whether the player has *enough* wide damage at once rather than whether they have any. The gimmick label is tempting and the hatch-heal is genuinely a puzzle, but it resolves into the same instruction every swarm gives — clear the adds now or drown in the count — and the summoner re-arms the Lay branch as soon as the board thins, so there is no one-time trick to solve. Note for Track B that the egg's contribution is what makes `OvicopterNormal` read **mixed** at the encounter level: a swarm engine bolted to a single 124–132 HP spike/attrition body that self-buffs Strength whenever the swarm is full.
