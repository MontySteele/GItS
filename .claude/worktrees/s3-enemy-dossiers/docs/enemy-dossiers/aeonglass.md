# Aeonglass

- **Class:** `Aeonglass`
- **Kind:** boss
- **Act:** 3 (Glory, act index 2)
- **Encounter:** `AeonglassBoss` — solo spawn, boss room, custom BGM `act3_boss_queen`
- **Fight class:** **mixed**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

Aeonglass is one of the three Act 3 bosses (alongside the Queen and the Test Subject) and sits third
in the act's boss discovery order. The encounter always generates exactly one monster: Aeonglass
itself. There are no adds, no summons, and no second phase creature — everything happens on one
statline. Its take-damage sound set is the "stone" family, and the act's boss music track parameter
(`queen_progress`) is pushed to its combat value when Aeonglass enters the room and to its
resolution value when it dies, so the fight shares the Queen's musical progression rig.

## Opening (on room entry, before turn 1)

Three things happen before anyone acts:

1. **Withering Presence** is applied to *each* opposing creature — one instanced counter power per
   player, starting at 6.
2. **Artifact 3** on Aeonglass itself.
3. The boss track parameter is set.

Both of these matter more than the raw numbers suggest and are covered under Gimmicks below.

## Intent pattern

A fixed, fully deterministic three-beat rotation. There is no randomness, no HP-threshold phase
change, and no conditional branching anywhere in the move machine — each state hard-points at the
next one, and the cycle starts on Ebb.

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Ebb** | AoE attack, then gains block | attack + defend |
| 2 | **Eye Lasers** | AoE attack, 2 hits | multi-attack (×2) |
| 3 | **Increasing Intensity** | upgrades every existing Wither, adds Wither(s) to each player's discard, gains Strength | status + buff |

Then back to Ebb, forever. Turn 1 is always Ebb; the state machine is barred from transitioning
before the first move resolves.

Two structural notes for modelling:

- **Every attack is AoE.** Both attacking moves are built as monster attacks targeting all
  opponents, so in co-op every seat eats the full listed number — there is no target selection and
  no split. The Ebb intent renders as a single-target icon, but that is cosmetic.
- **The rotation is knowable from turn 1.** A player who has seen the fight once can plan a full
  three-turn window in advance, which is what makes the escalation (below) the real difficulty
  rather than the surprise.

## Damage / block numbers

Base values, and the A9 (`DeadlyEnemies`) variants where they differ:

| Stat | Base | A9+ |
|---|---|---|
| HP (min = max, no roll) | **512** | **535** (A8 `ToughEnemies`) |
| Ebb damage | 26 | 32 |
| Ebb block gained | 33 | 33 (unchanged) |
| Eye Lasers damage per hit | 11 | 12 |
| Eye Lasers hit count | 2 | 2 |
| Increasing Intensity — Strength gained, first cast | 3 | 4 |
| Increasing Intensity — Wither cards added per player | 1 | 2 |
| Artifact on entry | 3 | 3 (scales by seat count, not ascension) |
| Withering Presence counter | 6 | 6 |

Block is gained *after* the Ebb attack resolves, so the 33 block is standing when the player's turn
begins — Ebb turns are both the biggest incoming hit and the turn the boss is hardest to damage.
Block is not ascension-scaled, so its relative value shrinks as the rest of the fight gets harder.

### The Strength escalation

Increasing Intensity does not grant a flat buff. The amount granted **rises by one every time the
move is used**: 3, then 4, then 5, then 6 (A9: 4, 5, 6, 7). Since it fires once per three-turn
cycle, cumulative Strength after *k* cycles is 3k + k(k−1)/2 — and Strength applies per hit, so it
is worth double on the Eye Lasers beat.

Base-difficulty damage curve, assuming no player interference:

| Turn | Move | Damage to each player |
|---|---|---|
| 1 | Ebb | 26 |
| 2 | Eye Lasers | 11 ×2 = 22 |
| 3 | Increasing Intensity | 0 (Str → 3) |
| 4 | Ebb | 29 |
| 5 | Eye Lasers | 14 ×2 = 28 |
| 6 | Increasing Intensity | 0 (Str → 7) |
| 7 | Ebb | 33 |
| 8 | Eye Lasers | 18 ×2 = 36 |
| 9 | Increasing Intensity | 0 (Str → 12) |
| 10 | Ebb | 38 |
| 11 | Eye Lasers | 23 ×2 = 46 |
| 12 | Increasing Intensity | 0 (Str → 18) |
| 13 | Ebb | 44 |
| 14 | Eye Lasers | 29 ×2 = 58 |

Per-cycle incoming (excluding Wither) runs 48 → 57 → 69 → 84 → 102 …, i.e. roughly quadratic. Add
the Wither damage below and the real soft cap on fight length lands somewhere around turns 15–18 for
a typical Act 3 deck. This is a boss with a **hard clock** even though nothing in it says "timer".

## Gimmicks

### Wither (the status)

Wither is a 0-slot unplayable Status card. It is not merely dead weight: it deals damage to its
owner **at the end of every turn it is still in hand**, starting at 3. It has no real upgrade level
— it uses a cosmetic "fake upgrade" that adds +3 damage per step and shows as Wither+1, Wither+2 and
so on.

The important interaction: every Increasing Intensity fake-upgrades **every Wither the player owns
anywhere in the combat**, and the boss also stamps the current upgrade count onto any Wither
generated later, from any source. So there is one global Wither strength for the fight:

| Increasing Intensity casts | Wither end-of-turn damage, each copy in hand |
|---|---|
| 0 | 3 |
| 1 | 6 |
| 2 | 9 |
| 3 | 12 |
| 4 | 15 |

Copies are added to the **discard pile**, not hand, so they arrive on a delay and then recycle
forever. Late in the fight a hand holding two Wither+4s is quietly taking 30 unblockable-by-default
damage per turn on top of the boss's attack, and drawing them costs draw slots as well.

### Withering Presence (the card-throughput tax)

Each player carries their own counter, starting at 6. Every card *that player* plays decrements it;
at zero, a Wither is added directly to **hand** and the counter resets to 6. Combined with the
global upgrade above, this means:

- The more cards you play, the more Wither you generate, and the Wither you generate is as strong as
  the boss's current tier.
- Playing many cheap cards — the standard Act 3 engine plan — is actively taxed. Low-card-count,
  high-value turns are rewarded.
- The counter is per-seat, so a fast-cycling co-op seat feeds itself Wither while a slow seat does
  not. It does not scale with party size; each player simply runs their own clock.

### Artifact 3

The entry Artifact eats the first three visible debuffs applied to Aeonglass, decrementing per
absorbed debuff. That blanks the opening of most debuff-lean plans (Weak/Vulnerable stacking,
Strength reduction) and, notably, means Strength-down answers to the escalation must first spend
three applications to get through — by which point the ramp is already two or three cycles deep.

## Scaling

**By act:** none — Aeonglass exists only in Act 3, and nothing on the model reads the act index
except through the shared multiplayer HP formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | HP 512 → 535 |
| A9 `DeadlyEnemies` | Ebb 26 → 32; Eye Lasers 11 → 12 per hit; Strength ramp starts at 4 instead of 3; Increasing Intensity adds **2** Wither per player instead of 1 |

The A9 Wither change is the harshest of the four: it doubles the rate at which the status pile fills
while the per-copy damage curve is unchanged, so the end-of-turn chip roughly doubles at every point
on the curve, and it doubles the draw-dilution rate too. Block is untouched at both levels.

**By seat count (multiplayer):**

- **HP** goes through the standard scale: base × players × 1.3 (the Act 3 *boss-room* multiplier —
  bosses get 1.3 where ordinary Act 3 rooms get 1.2).

| Players | HP (base) | HP (A8+) |
|---|---|---|
| 1 | 512 | 535 |
| 2 | ≈1331 | ≈1391 |
| 3 | ≈1997 | ≈2087 |
| 4 | ≈2662 | ≈2782 |

- **Damage does not scale, but it is AoE** — every seat takes the full Ebb / Eye Lasers number, so
  party-wide damage taken scales linearly with seats on top of the HP scale.
- **Increasing Intensity hits every player**: each seat gets its own Wither copies, and the global
  upgrade level applies to all of them.
- **Withering Presence** is applied once per opposing creature as a separate instanced counter, so
  every seat runs its own 6-card clock independently.
- **Artifact scales**: 3 + (players − 1), so a 4-player party faces 6 absorbed debuffs. This is the
  one number that gets *disproportionately* worse in co-op, because a party has more debuff sources
  than a solo player but each still gets eaten one-for-one.

## Proposed fight class: **mixed**

The rotation asks for a genuinely different thing on each of its three beats, and no single demand
dominates: the Ebb turn is a defensive check against the fight's largest single hit while the boss
is simultaneously walled behind 33 block, the Eye Lasers turn is a multi-hit check where per-hit
mitigation and block-per-instance behave completely differently, and the Increasing Intensity turn
is a free window that converts entirely into an offensive DPS check because standing still there
makes every later turn permanently worse. Layered under that rotation is a real gimmick axis — a
global, monotonically upgrading self-damaging status whose generation rate is driven by the player's
own card-play throughput, plus Artifact soft-locking the obvious debuff answer for the first several
attempts. It is not attrition, because the incoming curve is quadratic rather than flat and the
fight has a hard practical turn cap; it is not spike, because no single turn is designed to be
lethal in isolation. For Track B, model it as an escalating three-phase demand vector — block,
multi-hit mitigation, output — with an additive self-damage term that grows with both turn count and
cards played per turn.
