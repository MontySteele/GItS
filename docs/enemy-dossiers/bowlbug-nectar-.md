# Bowlbug (Nectar) — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `BowlbugNectar`
- **Kind:** normal
- **Act:** Act 2 (the Hive; act index 1)
- **Appears in:** `BowlbugsNormal` (Rock in the "first" slot + two *distinct* workers drawn from Egg / Silk / Nectar, so Nectar shows up in 2 of the 3 possible worker pairs), `BowlbugsWeak` (Rock + one worker, coin-flip Egg or Nectar). Both encounters carry the `Workers` encounter tag and use a dedicated scene.
- **Source read:** decompiled `BowlbugNectar`, `MonsterModel`, `MonsterMoveStateMachine` / `MoveState`, `AttackCommand` (targeting + intent preview), `StrengthPower`, `AttackIntent`, `Creature.ScaleHpForMultiplayer` / `MultiplayerScalingModel`, `Hive`, and the sibling bowlbugs for contrast. Behavioral notes only; no code reproduced.

## Stat block

| Quantity | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| Starting HP (rolled inclusive in range) | 35–38 | 36–39 | — |
| Thrash damage (pre-Strength) | 3 | — | 3 (unchanged) |
| Buff: Strength gained | 15 | — | 16 |
| **Post-buff Thrash damage** | **18** | — | **19** |

HP is rolled once at combat start from the inclusive min–max range. The two ascension knobs are independent and ride different levels: the HP bump on "Tough Enemies", the Strength bump on "Deadly Enemies". Note the unusual shape — the *attack* number is a flat literal that ascension never touches; ascension raises the **buff** instead, so the ascension delta only exists after turn 2. There is no act-based scaling; the monster only exists in Act 2 and every number is a literal.

## Intent pattern

Three states, fully deterministic — no RNG, no conditionals, no branch. The chain is:

1. **Turn 1 — Thrash** (attack intent, 3). The state machine holds the opening state until a move has actually been performed, so the first telegraphed intent is always the small thrash.
2. **Turn 2 — Buff** (generic buff intent, no number shown). Plays the buff animation and applies **Strength 15 (16)** to *itself*. Nothing else: no block, no damage, no ally effect.
3. **Turn 3 onward — Thrash again, forever.** The third state's follow-up is itself, so it is an unbroken loop of the same 3-damage attack, now riding +15/+16 Strength for **18/19 per turn** with no further escalation and no cooldown.

The Strength is a plain additive counter that applies to powered move damage, and monster move damage is powered by default, so the modifier lands cleanly on the thrash. The intent preview is computed through the same damage-modification path the player sees, meaning **the turn-3 intent honestly reads 18 (19)** — the cliff is telegraphed one full turn in advance by the buff icon and then again by the number itself. There is no hidden information here; the fight is a pre-announced deadline.

Total damage delivered across a fight, per seat: 3 on turn 1, 0 on turn 2, then 18/19 every turn after. Killing it during the buff turn costs the player 3 damage total.

## Gimmicks

- **The damage cliff is the entire creature.** A 6× multiplier on its own attack, applied once, permanently, on a fixed schedule. It has the lowest printed attack in the bowlbug family before the buff (3, vs Egg's 7 and Silk's 2×4) and the highest after it (18, vs Rock's 15 headbutt).
- **Self-only buff.** The Strength targets and is sourced from the Nectar itself, so it does *not* pump the Rock or the other worker. Despite the "Nectar" name (a hive-worker feeding motif) and the goop skin, there is no allied-support behavior anywhere in the model — no ally heal, no ally buff, no summon.
- **One-shot, not stacking.** The buff state is visited exactly once and is never returned to. Strength does not tick upward over a long fight, so a scaled-down or Strength-stripped Nectar stays down: any effect that removes or negates the Strength permanently defuses it, because it has no way to re-apply.
- **No block, no debuff, no death payload.** It never defends and never applies anything to the player. HP is the only thing between the player and the buff resolving.
- **Family contrast:** Silk alternates a 2×4 (2×5) thrash with a Weak-applying spit; Egg attacks and re-blocks itself every turn; Rock enters with a self-applied Imbalanced power and stun-branches out of its own headbutt. Nectar is the only one whose threat level changes over time.

## Multiplayer / seat count

No seat-count logic is written into the monster; the Strength gain and the base thrash are per-seat constants. Two engine-level adjustments matter:

- **HP scales, damage does not.** With more than one player, max HP is multiplied by player count and by the act's multiplayer factor (Act 2 = 1.2). A 2-player run faces ≈2.4× the printed HP (roughly 84–94 depending on roll and ascension), 3-player ≈3.6× (≈126–140), while the thrash stays 3 → 18/19. **This is the important co-op interaction:** the kill-before-turn-3 window is gated by HP that grows ~2.4–3.6×, while the reward for meeting it is unchanged. The race gets materially harder per seat as the table grows.
- **The thrash hits every seat.** A monster attack built with no explicit target defaults to targeting all living opponents, and the full per-hit amount is dealt to each of them. So post-buff the Nectar deals 18/19 to *each* living hero every turn — table-wide damage output scales linearly with seat count on top of the HP scaling. (Flagging this because the `bowlbug-egg-` dossier describes untargeted monster attacks as hitting a single seat; the decompiled attack builder says otherwise, and the same correction applies to Egg's bite.)

## Proposed fight class: **spike**

What this fight demands per turn is a countdown, not a grind: the player gets exactly two cheap turns (3 damage total) to either kill 35–38 HP or land a Strength-negating answer, and if they miss the window the incoming rate jumps 6× permanently to 18–19 per seat per turn. Every turn before the cliff asks "can you burst this specific target," and every turn after asks "can you build an 18-block wall or race a body you already failed to race" — both are spike-shaped questions, not attrition ones, since the creature's HP pool is small and nothing about the fight rewards a long trade. The buff is fully telegraphed a turn ahead and never repeats, so there is no ongoing puzzle to solve and no escalation curve; there is a single threshold moment that a build either clears or doesn't. Track B note: the *encounter* it sits in (Rock plus one or two workers, with Rock's own 15-damage headbutt) reads **mixed** at the encounter level — spike is the Nectar's own contribution to the demand curve, and it is the one that sets the encounter's kill-priority order.
