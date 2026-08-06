# Vantom

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Vantom`
- **Kind:** boss
- **Act:** 1 (Overgrowth, act index 0)
- **Encounter:** `VantomBoss` — solo spawn, boss room, custom BGM `act1_boss_vantom`, custom background, camera pulled to 0.9× and nudged down
- **Fight class:** **mixed**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

First entry in Act 1's boss discovery order (ahead of Ceremonial Beast and The Kin). The encounter
generates exactly one monster — no adds, no summons, no second creature, and nothing in the fight
spawns anything later (the `Inklet` monster that shares its ink theming is not summoned here). Its
take-damage sound family is "magic". It is flagged not to disappear from Doom effects.

There is one boss-specific system outside the move machine: an FMOD music parameter (`vantom_progress`)
that Vantom drives from 1 → 3 as its cycle advances and slams to 5 on death, paired with a
three-stage spine "charge" ladder (`charged_1` → `charged_2` → `charged_3`, reset to `charged_0` on
the heavy attack). **This ladder is pure telegraph — it carries no mechanical effect.** It is worth
naming because it makes the fight *read* as a charging boss to the player even though the actual
escalation is a plain Strength stack; a player who fears the charge-up animation will over-block the
wrong beats.

## Structure: a fixed four-beat loop, no RNG

Vantom has no phases, no thresholds, no reactive triggers, and no randomness. Four move states point
at each other in a ring, and the machine simply walks it. The fight opens on Ink Blot and the ring
never changes.

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Ink Blot** | Attack, 7, hits **all** players | attack |
| 2 | **Inky Lance** | Attack, 6 **×2 hits**, all players | multi-attack (2 hits) |
| 3 | **Dismember** | Attack, 26, all players, then shuffles **3 Wounds into each player's discard pile** | attack + status (3) |
| 4 | **Prepare** | Gains **2 Strength** (permanent, self) | buff |

Then back to Ink Blot forever. Because the loop is closed and deterministic, the player always knows
the next three turns; the fight's difficulty is entirely in the *shape* of the loop, not in guessing.

Two structural consequences worth modelling:

- **The big hit lands on a known clock.** Dismember arrives on turn 3, 7, 11, 15, … The player can
  bank block for exactly those turns and spend everything else on offense. Any fight model that
  assumes uniform incoming damage will badly misprice this boss.
- **The buff turn is a free turn.** Beat 4 deals zero damage. Every fourth player turn is a
  full-tempo turn with no defensive obligation — which is also the turn the Wounds from the previous
  beat are clogging the deck.

## Damage / block numbers

| Stat | Base | Ascension variant |
|---|---|---|
| HP (min = max, no roll) | **173** | **183** at A8 `ToughEnemies` |
| Slippery (self, on entering the room) | **8** | **9** at A8 `ToughEnemies` |
| Ink Blot damage | 7 | 8 at A9 `DeadlyEnemies` |
| Inky Lance damage | 6 × 2 hits | 7 × 2 at A9 |
| Dismember damage | 26 | 30 at A9 |
| Dismember Wounds | 3 to each player's discard | unchanged |
| Prepare Strength gain | 2 | 2 (unchanged) |

**Vantom never blocks.** There is no defensive move anywhere in the ring, so every point of player
output lands once the Slippery counter is gone, and the boss's own survivability is entirely
front-loaded into that counter.

### Damage curve (base, all attacks hit every seat)

Strength lands on beat 4 and applies per hit, so Inky Lance gains twice as much from it as the other
two moves — the two-hit attack is the move that scales, even though the one-shot is the scary one.

| Cycle | Str during cycle | Ink Blot | Inky Lance | Dismember | Cycle total |
|---|---|---|---|---|---|
| 1 | 0 | 7 | 6+6 = 12 | 26 | **45** |
| 2 | 2 | 9 | 8+8 = 16 | 28 | **53** |
| 3 | 4 | 11 | 10+10 = 20 | 30 | **61** |
| 4 | 6 | 13 | 12+12 = 24 | 32 | **69** |
| 5 | 8 | 15 | 14+14 = 28 | 34 | **77** |

Per-cycle incoming climbs **+8 per cycle** (+2 Ink Blot, +4 Inky Lance, +2 Dismember), i.e. +2 per
boss turn averaged over the loop — a gentle ramp by boss standards. At A9 the cycle-1 total is 52
(8 / 7+7 / 30) and the ramp rate is unchanged.

Against a typical Act 1 bar of ~70–80 HP, an unmitigated fight kills somewhere in cycle 2: cumulative
incoming reaches 45 by the end of cycle 1 and 98 by the end of cycle 2, with the single Dismember
hits (26, then 28) being the individual events most likely to be lethal from a bad HP position.
Against 173 HP with no block on the boss's side, a competent Act 1 deck is looking at a three- to
four-cycle fight, so the ramp rarely gets past Strength 6.

## Gimmicks

### Slippery (the opening armor, and the reason your big card is wrong on turn 1)

Vantom applies **Slippery 8** to itself the moment it is added to the room — before the first player
turn. Slippery is a counter with a brutally simple rule:

> Any damage instance that would cost the owner 1 or more HP costs it **exactly 1** instead, and the
> counter drops by 1.

So the first eight damage *instances* the player lands, regardless of size, deal 1 damage each.
Everything about how the fight opens follows from that:

- **Damage per hit is worth nothing; hit count is everything.** A 30-damage haymaker on turn 1 deals
  1. Eight 1-damage pings clear the counter as fast as eight 30-damage swings and cost far less.
  This inverts the normal card-valuation heuristic for exactly the opening of the fight.
- **It is a flat 8-damage tax at best, and a wasted-burst tax at worst.** A wide multi-hit deck pays
  almost nothing (it would have hit eight times anyway); a single-big-card deck can lose a full turn
  or two of output. The variance between builds here is much larger than the 8 HP suggests.
- **Chip and passive sources burn it too.** Any damage instance decrements it, so thorns-style
  reflections, per-turn tick effects and off-turn pings all eat stacks — often before the player
  intends them to.
- **It is one-time.** Nothing in the ring reapplies it. Once gone, Vantom is a naked 165-HP bar with
  no mitigation whatsoever.

### Wound clog

Dismember puts **3 Wounds into the discard pile** — unplayable status cards — for **every** player,
on the same beat as the fight's biggest hit. That is 3 dead cards per cycle per seat, arriving on a
4-turn clock. In a three-cycle fight that is 9 Wounds; the deck-dilution curve is steep enough that a
slow deck's fourth cycle is measurably worse than its first, which is the fight's only real attrition
pressure. Note the Wounds go to *discard*, not draw or hand, so the pain is deferred by roughly one
shuffle — a fight short enough to end inside two shuffles barely feels it, and a long one feels it
compounding.

### What it does *not* have

No block, no heal, no summons, no threshold trigger, no debuffs applied to the player (other than
Wounds), no reaction to being buffed/debuffed, and no artifact-style protection. Every player-side
strategy that normally gets shut down by a boss's defensive tech works here. Vantom's own `ScaleTo`
hook exists only so the generic Shrink debuff can visually shrink it — a player-side interaction, not
part of its kit.

## Scaling

**By act:** none. Vantom exists only in Act 1; the only act-index read is via the shared multiplayer
scaling formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | HP 173 → 183; Slippery 8 → 9 |
| A9 `DeadlyEnemies` | Ink Blot 7 → 8; Inky Lance 6 → 7 per hit (12 → 14 per turn); Dismember 26 → 30 |

A9's weight is concentrated in Dismember: +4 on the one hit the player is already planning their
whole block budget around, versus +1 / +2 on the chip beats. In practice A9 turns a survivable
"partially blocked Dismember" into a lethal one for a mid-HP Act 1 character, and that single number
is the difference the ascension actually sells. A8's Slippery bump is nearly free for multi-hit decks
and another wasted turn for burst decks — the same build-variance amplifier as base Slippery, one
notch louder.

**By seat count (multiplayer):**

- **HP** uses the standard formula: base × players × 1.1 (the Act 1 multiplier; Act 1 has no separate
  boss rate).

| Players | HP (base) | HP (A8+) |
|---|---|---|
| 1 | 173 | 183 |
| 2 | ≈381 | ≈403 |
| 3 | ≈571 | ≈604 |
| 4 | ≈761 | ≈805 |

- **Slippery scales by raw seat count — ×2 / ×3 / ×4, with no 1.1 factor**: 16 / 24 / 32 stacks
  (18 / 27 / 36 at A8). This is the one number that gets *relatively cheaper* per seat, since a
  four-seat party generates far more than 4× the damage instances of a solo player; the opening tax
  is diluted in practice even though the printed number quadruples.
- **Every attack targets all opponents.** Ink Blot, Inky Lance and Dismember are all party-wide at
  full value — nothing is split or diluted across seats. A four-seat party eats 4 × 26 = 104 total
  damage on every Dismember beat, at unchanged per-player severity.
- **Dismember's Wounds are per-player**: 3 into each seat's discard, so the deck-clog cost scales
  linearly with party size too.

The net co-op shape: the HP bar grows by 2.2× / 3.3× / 4.4× while incoming per-player damage stays
flat, which makes the fight *longer* at the same per-turn lethality. Longer means more Dismember
beats, which means more Wounds and more Strength stacks — so co-op shifts Vantom measurably toward
its attrition half.

## Proposed fight class: **mixed**

The four-beat ring asks for three different things on a rotating schedule, and no one of them
dominates. Beats 1–2 demand almost nothing defensively (7 and 12 chip) and are pure output windows;
beat 3 is a hard **spike check** — a single 26–32 hit plus 3 Wounds that the player must have banked
block for, and the only event in the fight likely to kill anyone; beat 4 is free. Layered under that
rhythm are two non-spike demands: the opening **Slippery 8 gimmick**, which for one or two turns
makes damage-per-hit worthless and hit-count everything (a genuine deck-shape check, not a damage
check), and the **Wound accrual**, a slow deck-degradation clock that only bites parties or decks
slow enough to reach cycle 3+. It is not pure spike (two of four beats are trivial and the ramp is
only +2/turn), not pure attrition (no block, modest bar, short by construction), not gimmick (the
Slippery is over by turn 2), and not swarm (solo, no adds). For Track B, model it as a period-4
demand vector — `[low, low, HIGH-block, none]` on incoming, with a one-time hit-count requirement of
8 at t=0 and a +3-dead-cards-per-4-turns dilution term.
