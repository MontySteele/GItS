# Bowlbug (Egg) — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `BowlbugEgg`
- **Kind:** normal
- **Act:** Act 2 (the Hive; act index 1)
- **Appears in:** `BowlbugsNormal` (Rock + two distinct workers drawn from Egg / Silk / Nectar), `BowlbugsWeak` (Rock + one worker, Egg or Nectar). Both encounters carry the `Workers` encounter tag and use a dedicated scene.
- **Source read:** decompiled `BowlbugEgg`, `MonsterModel`, `MonsterMoveStateMachine` / `MoveState`, `Creature` HP setup, `MultiplayerScalingModel`, the two Bowlbug encounter models. Behavioral notes only; no code reproduced.

## Stat block

| Quantity | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| Starting HP (rolled inclusive in range) | 21–22 | 23–24 | — |
| Bite damage | 7 | — | 8 |
| Protect block | 7 | — | 8 |

HP is rolled once at combat start from the inclusive min–max range. The two ascension knobs are independent: the HP bump rides on the "Tough Enemies" ascension level, the damage/block bump on "Deadly Enemies" (the two adjacent late-ascension tiers). There is no act-based scaling on this monster — it only exists in Act 2, and its numbers are literals.

## Intent pattern

The move machine has exactly one state, and that state's follow-up is itself. There is no branch, no counter, no conditional, no opening-turn special case. Every turn, from turn one until it dies, the Egg does the same thing.

The single move is a compound: it telegraphs an **attack intent plus a defend intent** on the same turn (the intent bar shows both an attack value and a shield). On resolution it, in order:

1. Bites one target for the Bite value (single-target attack, blunt hit fx, standard monster attack animation).
2. Immediately gains the Protect block value on itself, credited as move-sourced block.

Because the block is applied at the tail of its own turn, it is standing when the player acts and is stripped at the start of the Egg's next turn — i.e. the player faces a fresh 7 (8) block wall on **every** player turn, indefinitely.

Target selection is the engine default for an untargeted monster attack (single random/assigned player seat), not a scripted target.

## Gimmicks

- **No hatch.** Despite the name and the cocoon/egg skin (it renders as a bowlbug wearing a cocoon with an idling egg sub-skeleton), nothing in the model spawns, transforms, or summons. It never becomes another monster and nothing else in the tree references the class outside the two encounter tables. The "egg" is flavor and a visual state, not a timer.
- **Self-block as a damage filter.** The recurring block is the whole design. Effective HP against a chip build is far above the 21–24 printed number; against a build that lands one hit above the block threshold it is exactly the printed number. Two 4-damage hits per turn do nothing to it; one 9-damage hit kills it in three turns.
- **No powers, no debuffs, no buffs.** Contrast the siblings it shares a slot with: Silk alternates a 2×4 (2×5) thrash with a debuff spit, Nectar has a buff move in its cycle, and Rock enters combat with a self-applied Imbalanced power and a stun-branching cycle. The Egg is the flat one.
- **Death is clean** — no on-death payload, no retaliation.

## Multiplayer / seat count

No seat-count logic is written into this monster: damage and block are per-seat constants regardless of player count. The only adjustment is the engine-wide HP scale applied when the creature is built — with more than one player, max HP is multiplied by the player count and by the act's multiplayer factor, which for Act 2 is 1.2. So a 2-player run faces roughly 2.4× the printed HP (≈50–58 depending on roll and ascension), 3-player ≈3.6×, while the Bite stays 7/8 and the Protect block stays 7/8 — the block wall does **not** grow with the table. Net effect in co-op: the Egg's block becomes proportionally much less relevant and it reads as a plain HP sponge.

## Proposed fight class: **attrition**

Per turn, the Egg asks the same small, unvarying question: absorb or trade against 7–8 incoming, and clear a 7–8 block wall before any damage sticks. Nothing about it spikes, escalates, or forces a reactive turn — there is no burst turn to plan around and no window to exploit, so the pressure it applies is a slow, flat drain on the player's HP and tempo across however many turns the wider encounter runs. Its one real demand is *concentration*: it taxes wide/chip damage patterns every single turn while a build that can commit one above-threshold hit deletes it in ~3 turns, which is an attrition-shaped efficiency test rather than a gimmick puzzle. Note for Track B that the encounters it appears in (Rock plus one or two workers) read as **mixed/swarm** at the encounter level — the attrition label is the Egg's own contribution to that curve, not the fight's total shape.
