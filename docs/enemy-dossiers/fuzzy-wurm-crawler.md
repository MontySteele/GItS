# Enemy Dossier — Fuzzy Wurm Crawler

- **Class:** `FuzzyWurmCrawler`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act pool it appears in
- **Encounters:** `FuzzyWurmCrawlerWeak` (solo, weak/opening encounter), `OvergrowthCrawlers` (one Shrinker Beetle + one Fuzzy Wurm Crawler)
- **Fight class:** `spike`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Fuzzy Wurm Crawler is Act 1's *ramp* body: a mid-HP worm with exactly two moves — a small
single-target spit and a self-buff that grants a very large, permanent Strength gain. Its opening hit
is trivially small (4), but every third turn it inhales and adds **+7 Strength**, and because Strength
is a plain additive counter on powered attacks, the same little spit becomes 11, then 18, then 25, and
so on with no ceiling.

It has no Block move, no summon, no debuff application, no on-death effect, no low-HP behavior change,
and no reaction to its partner dying. The whole fight is a fixed three-beat clock plus a compounding
damage number.

The "puffed" state it enters on Inhale is **cosmetic only** — it swaps the idle/hurt/death animation
set and is cleared when it next spits. It grants no damage reduction, no thorns, and no mechanical
difference of any kind; the Strength is the real payload, and the Strength does not go away when the
puff does.

## 2. Intent pattern / AI

Three states chained head-to-tail, **fully deterministic** — the state machine never consults RNG for
this enemy, so the entire fight is readable from turn 1.

| State | Intent shown | Effect |
|---|---|---|
| Acid Goop (opening variant) | single attack | One attack of 4 (base) against its target. Functionally identical to the ordinary goop; it exists only as a distinct node in the loop. |
| Inhale | buff | Grants **itself +7 Strength**, permanently. Plays an inhale animation and enters the puffed look. |
| Acid Goop | single attack | One attack of 4 (base) + accumulated Strength. Clears the puffed look. |

Flow: **Goop → Inhale → Goop → Goop → Inhale → Goop → Goop → Inhale → …** — a three-turn cycle of
*attack, buff, attack* that repeats forever with no branch and no interrupt.

The opening-goop node is hidden from the bestiary listing (the bestiary shows only the ordinary goop
and the inhale), which is a UI detail, not a behavior one: to the player the pattern simply reads as
"it buffs every third turn."

The self-buff is applied to itself with no player-choice interaction, so nothing about the buff turn
is contestable except by killing it, stripping the Strength, or applying Weak to blunt the output.

### Damage-by-turn ladder (base, single player, no ascension)

| Turn | Move | Strength after | Damage dealt |
|---|---|---|---|
| 1 | Goop | 0 | 4 |
| 2 | Inhale | 7 | — |
| 3 | Goop | 7 | 11 |
| 4 | Goop | 7 | 11 |
| 5 | Inhale | 14 | — |
| 6 | Goop | 14 | 18 |
| 7 | Goop | 14 | 18 |
| 8 | Inhale | 21 | — |
| 9 | Goop | 21 | 25 |
| 10 | Goop | 21 | 25 |

Cumulative damage taken if fully unblocked: 4 / 15 / 26 / 44 / 62 / 87 / 112 by end of turn 10. The
first three turns cost the party 4 damage total; turns 6–10 cost 86. That asymmetry is the whole
enemy.

Steady-state throughput over a cycle after *n* inhales is `2 × (base + 7n) / 3` per turn, i.e. it
grows by ~4.7 damage/turn every cycle and never plateaus.

## 3. Gimmicks

**Compounding Strength with no decay.** +7 is a large single grant for an Act 1 normal — for scale, it
is roughly the size of a whole early-game attack buff — and it stacks as a counter, so nothing removes
it on its own. Any run that stalls this fight (heavy block turtling, a slow scaling deck, a bad draw
sequence) converts a harmless worm into a lethal one on a strict schedule. Conversely, an artifact- or
debuff-strip effect that removes Strength resets the clock, and **Weak** on the worm is unusually
valuable here because it multiplies down a number that keeps growing.

**Front-loaded softness.** Its base spit is only 4 and it is alone in its weak encounter, so the fight
punishes exactly one thing: taking too long. There is no defensive layer, no block, no healing, and
nothing to solve — the "puzzle" is entirely a DPS-versus-clock question.

**Partner interaction (`OvergrowthCrawlers`).** Paired with a Shrinker Beetle, the worm is the *back*
half of the threat: the beetle applies the early pressure while the worm ramps behind it. Killing the
worm first is nearly always correct because its threat is the only one that grows; leaving it alive
while clearing the beetle inverts the fight's difficulty curve.

**Co-op targeting asymmetry.** Acid Goop is a single-target attack that lands on one seat at a time.
There is no cleave, no all-seat effect, and no "attacks each player" behavior anywhere in this enemy.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 55–57 | 58–59 | — |
| Acid Goop (both variants) | 4 | — | 6 |
| Inhale | +7 Strength to self | — | — |
| Block | none, ever | — | — |

- HP is rolled inclusively from the band; the band is unusually tight (3 values, or 2 on Tough
  Enemies), so the fight length is very consistent run to run.
- Because it never gains Block, the enemy-Block multiplayer scaler never touches it.
- The Strength grant (7) has **no** ascension variant and **no** seat-count variant — it is a fixed
  constant in every configuration of the fight.

## 5. Scaling

**By act:** none. Act 1 only, no act-conditional stats.

**By ascension:** two flat levers, both small relative to the ramp.

- *Tough Enemies* moves the HP band from 55–57 to **58–59** (+3 at the floor, +2 at the ceiling) —
  roughly one extra turn of chip for a weak Act 1 deck, which is meaningful only because an extra turn
  is what the ramp wants.
- *Deadly Enemies* takes Acid Goop from 4 to **6**. Note this shifts the whole ladder up by 2 at every
  rung (6 / 13 / 13 / 20 / 20 / 27 …) rather than scaling it, so its relative importance *shrinks* as
  the fight lengthens; the +7 per inhale continues to dominate.
- Neither the Strength amount nor the cycle length has an ascension variant.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 1 non-boss factor being
  **1.1**.

| Players | Effective HP band (from base roll) |
|---|---|
| 1 | 55–57 (no scaling at 1 player) |
| 2 | ~121–125 |
| 3 | ~182–188 |
| 4 | ~242–251 |

- *Acid Goop* does not scale with seats — still one hit on one seat — so per-seat incoming damage falls
  as the table grows.
- *Inhale* does not scale with seats. The +7 stays +7.

Net co-op shape: HP more than doubles per added seat while the damage clock stays the same length and
the same size. That makes the ramp **strictly more dangerous in co-op** — a four-seat party must chew
through ~4.4× the HP against a worm that reaches +21 Strength on exactly the same turn it would
solo — but it is also spread across four health pools, so the failure mode is a long fight ending in
someone eating a 25+ hit rather than a party wipe. In practice co-op turns this from a race into a
race with a much longer track.

## 6. Proposed fight class — `spike`

What this fight demands per turn is not sustain but **tempo**: for the first three turns it asks for
almost nothing (4 damage total), and from then on it asks for a hit that grows by 7 every cycle
against a body that has no defenses to interact with. There is no resource to grind down, no status
pollution, no per-turn attrition tax, and only one body in the weak encounter — that rules out
`attrition` and `swarm`; the puffed state is pure animation and the pattern is fixed and readable, so
there is no puzzle to make it `gimmick` or a second demand type to make it `mixed`. For Track B this
should be modeled as a **soft-opening, hard-tailed clock**: the demand curve is near zero for three
turns and then rises without bound, so the correct read is that the player must front-load damage or
land Weak/Strength-strip, and every turn of stalling is repaid with interest.
