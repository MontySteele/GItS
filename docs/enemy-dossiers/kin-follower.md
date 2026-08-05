# Kin Follower

- **Class:** `KinFollower`
- **Kind:** boss (boss-encounter member, not a solo boss)
- **Act:** 1 (act index 0)
- **Encounter:** `TheKinBoss` — boss room, custom BGM `act1_boss_the_kin`, three slots (`slot1`, `slot2`, `leaderSlot`)
- **Fight class:** **swarm**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

The Kin Follower never spawns alone and never spawns outside its own boss encounter. `TheKinBoss`
always generates exactly three creatures: two Kin Followers (`slot1`, `slot2`) and one **Kin Priest**
(`leaderSlot`). The encounter's monster pool contains only these two classes, so the composition is
fixed — no variants, no rolls, no summons mid-fight. Camera is pulled back slightly for the
three-body lineup.

Cosmetically, each Follower picks one of three hair skins at random on spawn; this is purely visual
and has no gameplay read. Its hurt sound is borrowed from the Priest, and its damage-material is the
"fur" family.

## Minion status (the single most important structural fact)

On room entry, before turn 1, each Follower applies **Minion** to itself. Minion marks the creature
as a **secondary enemy**: a secondary enemy cannot sustain the combat by itself and dies
automatically once no primary enemy remains. In this encounter the Priest is the only primary enemy,
so:

- **Killing the Priest ends the fight instantly**, whatever HP the Followers have left.
- **Killing both Followers does not end the fight** and does not damage the Priest.
- A Follower's death does not trigger any fatal/kill-the-encounter bookkeeping, and the Minion power
  is not stripped when its applier dies.

The Priest watches the Followers die: each Follower death pushes the boss music's progress parameter
one step, and when the *last* living Follower dies the Priest plays a scripted taunt line. That is
flavour only — no stat change fires on it.

## Intent pattern

A fixed, fully deterministic three-beat rotation with no randomness, no HP threshold, and no
conditional branching. Each state hard-points at the next; the machine is barred from transitioning
before its first move resolves, so turn 1 is always the initial state.

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Quick Slash** | single attack | attack |
| 2 | **Boomerang** | attack, 2 hits | multi-attack (×2) |
| 3 | **Power Dance** | gains Strength (permanent, no cap) | buff |

Then back to Quick Slash, forever.

**The two Followers are deliberately desynchronised.** The `slot1` Follower is built with the
"starts with dance" flag set and therefore opens on Power Dance; the `slot2` Follower opens on Quick
Slash. Their rotations run one beat apart for the whole fight, which means the player almost never
faces two identical intents and almost never gets a turn where both adds are idle.

| Turn | slot1 Follower | slot2 Follower |
|---|---|---|
| 1 | Power Dance | Quick Slash |
| 2 | Quick Slash | Boomerang |
| 3 | Boomerang | Power Dance |
| 4 | Power Dance | Quick Slash |

Layered on top, the Priest runs its own fixed four-beat cycle (Orb of Frailty → Orb of Weakness →
Beam ×3 → Ritual +Strength), so the encounter's combined intent pattern has a period of 12 turns and
is fully knowable from turn 1 by a player who has seen it once.

## Damage / block numbers

Per Follower. Values are pre-Strength; Strength is added **per hit**.

| Stat | Base | Ascension variant |
|---|---|---|
| HP roll | **58–59** | **62–63** (A8 `ToughEnemies`) |
| Quick Slash damage | 5 | 5 (unchanged at A9) |
| Boomerang damage per hit | 2 | 2 (unchanged at A9) |
| Boomerang hit count | 2 | 2 |
| Power Dance — Strength gained | 2 | **3** (A9 `DeadlyEnemies`) |
| Block gained | **none — the Follower never blocks** | — |

The two Followers are given *distinct* max-HP rolls out of the 58–59 (A8: 62–63) window where
possible, so in practice one add is always one point squishier than the other. There is no Artifact,
no thorns, no retaliation, and no self-heal anywhere on the model.

### The Strength ramp

Power Dance grants a flat amount every third turn and never stops. Unlike the Priest's Ritual it does
not escalate its own grant, but it fires on a 3-turn clock rather than the Priest's 4-turn clock, so
over a long fight a Follower's Strength outpaces the boss's.

Cumulative per Follower (base / A9), and the resulting outgoing damage:

| Dances resolved | Strength (base) | Quick Slash | Boomerang total | Strength (A9) | Quick Slash (A9) | Boomerang total (A9) |
|---|---|---|---|---|---|---|
| 0 | 0 | 5 | 4 | 0 | 5 | 4 |
| 1 | 2 | 7 | 8 | 3 | 8 | 10 |
| 2 | 4 | 9 | 12 | 6 | 11 | 16 |
| 3 | 6 | 11 | 16 | 9 | 14 | 22 |
| 4 | 8 | 13 | 20 | 12 | 17 | 28 |
| 5 | 10 | 15 | 24 | 15 | 20 | 34 |

Boomerang is where the ramp bites: Strength applies to both hits, so each Dance is worth +2 damage on
the Quick Slash turn but **+4** on the Boomerang turn (A9: +3 / +6). A Follower left alive for four
of its own cycles is hitting harder than the Priest's opening orbs. This is also why per-hit
mitigation (Weak, thorns-style flat reduction, block that survives multiple instances) reads very
differently on the two attack beats.

### Combined encounter pressure (base, nothing killed, single player)

| Turn | slot1 | slot2 | Priest | Total to the player |
|---|---|---|---|---|
| 1 | dance | 5 | 8 + Frail | 13 |
| 2 | 5 | 4 | 8 + Weak | 17 |
| 3 | 4 | dance | 9 (3×3) | 13 |
| 4 | dance (Str 4) | 7 | ritual (Str 2) | 7 |
| 5 | 7 | 8 | 10 | 25 |
| 6 | 8 | dance | 10 | 18 |
| 7 | dance (Str 6) | 11 | 15 (5×3) | 26 |
| 8 | 11 | 12 | ritual (Str 4) | 23 |

The curve is shallow early and linear-ish thereafter — the fight is not built to one-shot anyone, it
is built to keep a steady bleed running while the player decides what to point damage at.

## Gimmicks

- **Boomerang range fix-up.** Before the Boomerang animation plays, the Follower moves its attack
  distance control toward the *leftmost* player creature. Purely presentational (it makes the thrown
  weapon reach the closest seat), but worth knowing when reading co-op replays: the visual "leans
  toward" one player while the damage does not.
- **Boomerang plays its animation once for both hits.** Both hits land off a single wind-up, so the
  two instances arrive with essentially no gap — relevant for anything that reacts between hits.
- **No block, no defensive move.** Every turn a Follower is either attacking or buffing; there is no
  turn on which killing it is cheaper than on any other turn. Damage into a Follower is never wasted
  on block.
- **Minion / secondary-enemy behaviour** (see above) — the fight's real gimmick, since it makes
  killing the adds strictly optional and turns the whole encounter into a target-priority puzzle.

## Scaling

**By act:** none. The Follower exists only in the Act 1 boss room, and the model reads no act index
except through the shared multiplayer HP formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | HP roll 58–59 → 62–63 |
| A9 `DeadlyEnemies` | Power Dance Strength 2 → 3. **Base attack numbers do not change.** |

This is unusual and worth flagging for Track B: A9 does not raise the Follower's printed damage at
all, it raises only the ramp rate. The A9 Follower is identical to the base Follower on turn 1 and
50% worse per Dance thereafter — the ascension makes *fight length* the punished quantity, not the
opening burst. (The Priest, by contrast, gets both flat damage and ramp increases at A9.)

**By seat count (multiplayer):**

- **HP** uses the standard scale: base × players × **1.1** (the Act 1 multiplier — Act 1 does not
  get the boss-room bump that Act 3 does).

| Players | HP (base roll 58–59) | HP (A8+, roll 62–63) |
|---|---|---|
| 1 | 58–59 | 62–63 |
| 2 | ≈128–130 | ≈136–139 |
| 3 | ≈191–195 | ≈205–208 |
| 4 | ≈255–260 | ≈273–277 |

- **Both attacks are AoE across seats.** Monster attacks default to targeting all opponents, and with
  more than one player alive the damage is applied to every valid target rather than a randomly
  chosen one. So each seat takes the *full* Quick Slash / Boomerang number — party-wide damage taken
  scales linearly with seat count on top of the HP scale, and the same is true of the Priest's orbs
  and beam. The single-target intent icon on Quick Slash is cosmetic.
- **Strength does not scale with seats**, but because the attacks are AoE, each point of Strength is
  worth `players` damage to the party, so the ramp is effectively multiplied by party size.
- **Enemy block would scale with seats** under the same multiplayer model, but the Follower gains no
  block, so this never applies to it.
- Two Followers × AoE × a 3-turn ramp is the reason this encounter gets meaningfully harder in co-op
  than its solo numbers suggest: the party HP pool grows by `players`, the enemy HP pool grows by
  `players × 1.1`, and the incoming damage grows by `players` as well — but the *ramp* is unchanged,
  so the practical fight is longer and therefore further up the Strength curve.

## Proposed fight class: **swarm**

Every turn this fight asks the player *where to point damage*, not how much to survive: three
separate bodies with separate intents, two of them cheap (≈59 HP) permanent-Strength engines on a
3-turn clock and one of them a 190 HP primary whose death ends the combat outright. No single
incoming number is threatening — the largest early hit is 8 — but the encounter multiplies its
sources, desynchronises them by one beat so the intent bar is never quiet, and makes every ignored
Follower permanently worse in a way that compounds specifically on its double-hit turn. The classic
answer is split or area output early and a race on the Priest once the adds are handled, which is
exactly a swarm demand curve: throughput distributed across targets, with a target-priority decision
each turn rather than a defensive check. It is not attrition (the ramp is real and the fight has a
practical clock), and not spike (nothing here is designed to be lethal in one turn); the one
gimmick-flavoured element — killing the leader instantly clearing the minions — is a *release valve*
on the swarm, not a separate mechanic to solve.
