# Enemy Dossier — Louse Progenitor

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `LouseProgenitor`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `LouseProgenitorNormal` (solo — one Progenitor, no escorts)
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Louse Progenitor is the grown-up version of the Act 1 louse joke: a single fat body with a large
HP pool that fights alone and gets **permanently stronger every third turn**. It has one attack, one
attack-with-a-debuff-rider, and one turn spent curling into a ball to gain Block and **+5 Strength**
that never expires and never ticks down.

It does not summon, does not split, has no on-death effect, no low-HP phase change, and never varies
its order. What it has instead is a ramp with no ceiling and a reactive Block trigger inherited from
the classic louse curl-up, so the fight is a race whose difficulty curve is entirely a function of how
many turns you let it live.

## 2. Intent pattern / AI

Three states in a fixed ring, **fully deterministic** — the state machine consults no RNG for this
enemy. The whole fight is readable from turn 1 and never deviates.

| State | Intent shown | Effect |
|---|---|---|
| `CURL_AND_GROW_MOVE` | Defend + Buff | Curls up: gains Block and **+5 Strength** (permanent). Sets its curled flag. |
| `POUNCE_MOVE` | Single attack | Uncurls (if curled) and hits for the Pounce number, modified by accumulated Strength. |
| `WEB_CANNON_MOVE` | Single attack + Debuff | Uncurls (if curled) and hits for the Web number, then applies **Frail 2**. |

Flow: **Curl & Grow → Pounce → Web Cannon → Curl & Grow → …** forever.

- The **first turn is always Curl & Grow** — the state machine cannot transition away from the initial
  state before performing a move, so the fight opens with a free buff turn and no incoming damage.
- Curled/uncurled is an **animation and death-pose state only**; it has no defensive value on its own.
  Being curled costs the enemy nothing on the turn it uncurls to attack.
- Because the order never changes, the party can plan the ramp exactly: incoming damage steps up by 5
  on every attack turn after each curl.

## 3. Gimmicks

**Curl Up (reactive Block, one-shot, applied on room entry).** Before the first turn the Progenitor
gives itself a Curl Up counter equal to its Curl Block value. It watches for the first *card-sourced,
power-modified attack* that damages it; when the card that dealt that damage finishes resolving, the
Progenitor curls, **gains Block equal to the counter**, and the power removes itself. Consequences for
play:

- It fires **once per combat**, not once per turn.
- The Block arrives *after* the triggering card completes, so multi-hit cards spend all their hits
  before the Block appears — a multi-hit opener strips the curl for the price of one card, whereas a
  single big hit strips it for the price of your best card.
- Damage that does not come from a card (thorns-style retaliation, power ticks, non-card sources)
  does not arm or trigger it.

**Permanent Strength ramp.** +5 Strength per curl turn, on a Counter-type stack that has no duration
and nothing in this fight to remove it. This is the whole difficulty curve: the base attack numbers
are unremarkable, and by the third or fourth cycle they are not.

**Frail rider.** Web Cannon lands Frail 2, which multiplies the recipient's Block gain by **0.75** for
the following turns. It is timed badly on purpose: Web is the last move of the cycle, so the Frail is
live exactly when the party wants to block the escalating Pounce two turns later. Frail ticks down at
the end of enemy turns, and the Web recurs every three turns, so under a stalled fight the party is
Frail-taxed a majority of the time.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 134–136 | 138–141 | — |
| Pounce | 14 | — | 16 |
| Web Cannon | 9 + **Frail 2** | — | 10 + **Frail 2** |
| Curl & Grow Block | 14 | 18 | — |
| Curl & Grow Strength | +5 (permanent) | — | — |
| Curl Up starting counter | 14 | 18 | — |

Damage actually taken, with the Strength stack folded in (base values, single player, no Block):

| Turn | Move | Strength after | Hit |
|---|---|---|---|
| 1 | Curl & Grow | 5 | 0 (gains 14 Block) |
| 2 | Pounce | 5 | 19 |
| 3 | Web Cannon | 5 | 14 + Frail 2 |
| 4 | Curl & Grow | 10 | 0 (gains 14 Block) |
| 5 | Pounce | 10 | 24 |
| 6 | Web Cannon | 10 | 19 + Frail 2 |
| 7 | Curl & Grow | 15 | 0 (gains 14 Block) |
| 8 | Pounce | 15 | 29 |
| 9 | Web Cannon | 15 | 24 + Frail 2 |

Closed form for cycle *n* (n = 1, 2, 3 …): Pounce = 14 + 5n, Web = 9 + 5n, so **33 damage in the first
cycle, +10 more each cycle after** (43, 53, 63 …). Averaged over the three-turn loop that is 11
damage/turn in cycle 1 and 21 by cycle 3. On Deadly Enemies add 3 per cycle (26 + 10n).

The pool is large for an Act 2 normal (mid-130s) and the enemy adds 14–18 Block on a third of its
turns plus one 14–18 reactive Block, so the effective pool to chew through is roughly **HP + 14 per
completed cycle + 14 once**. Overkill damage on curl turns is wasted; damage timed onto Pounce/Web
turns is not.

## 5. Scaling

**By act:** none. Act 2 only, no act-conditional stats.

**By ascension:** two independent levers, and they touch different halves of the fight.

- *Tough Enemies* raises the HP band (134–136 → 138–141) **and** the Curl Block / Curl Up counter
  (14 → 18). This lengthens the fight, which is the worst possible thing to do against a permanent
  ramp — the extra Block is worth far more than its face value because every extra turn is another
  +5 Strength.
- *Deadly Enemies* raises Pounce 14 → 16 and Web 9 → 10, i.e. +3 per cycle on top of the ramp.
- The Strength gain (5) and the Frail amount (2) have **no** ascension variants.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 2 non-boss factor
  being **1.2**.

| Players | Effective HP band (base roll) |
|---|---|
| 1 | 134–136 (no scaling at 1 player) |
| 2 | ~322–326 |
| 3 | ~482–490 |
| 4 | ~643–653 |

- *Block scales twice over, by two different routes, each firing once.* The Curl & Grow Block is
  monster-move Block and goes through the enemy-Block multiplier (× players × 1.2), so at two seats
  the curl turn is worth roughly 34 instead of 14. The reactive Curl Up counter is instead scaled at
  application time (the power is flagged to scale in multiplayer), then paid out as unpowered Block so
  it is not multiplied a second time — same magnitude, different plumbing.
- *Strength does not scale* — still +5 per curl regardless of seat count.
- *Both attacks target every opponent.* Monster attacks here are built against all opponents rather
  than one seat, so **each player takes the full listed number**; the party's total intake is the
  table number × seats.
- *Frail 2 is applied to every player creature*, so the Block tax lands table-wide.

Net co-op shape: HP and enemy Block grow super-linearly while the per-seat threat stays identical,
which means more turns alive, which means more +5 stacks. This is the one enemy in the Act 2 normal
pool whose multiplayer scaling actively works against the players' clock rather than merely padding
it.

## 6. Proposed fight class — `attrition`

Every turn this fight asks the same unglamorous thing — soak a telegraphed hit whose size grows by 5
each cycle while your Block is quietly worth 25% less — and it asks it for as many turns as you fail
to close. There is no burst turn to survive and no threshold that pays out, which rules out `spike`;
one solitary body rules out `swarm`; and while Curl Up is a real puzzle, it is a single one-shot
decision about how to package the opening attack rather than a mechanic the fight is built around, so
it does not carry `gimmick` or make the fight `mixed`. For Track B this is a **damage race against a
self-compounding clock**: the demand curve starts low (11/turn averaged in cycle 1) and rises linearly
without bound, the enemy converts a third of its turns into Block instead of damage, and the correct
counterplay is front-loading burst rather than out-sustaining it — a deck that cannot kill inside
three or four cycles does not lose slowly, it loses to a number it could have computed on turn 1.
