# Ceremonial Beast

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `CeremonialBeast`
- **Kind:** boss
- **Act:** 1 (Overgrowth, act index 0)
- **Encounter:** `CeremonialBeastBoss` — solo spawn, boss room, custom BGM `act1_boss_ceremonial_beast`, custom background, camera pulled to 0.9× and nudged down
- **Fight class:** **mixed**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

One of the three Act 1 bosses, second in the act's boss discovery order (between Vantom and The
Kin). The encounter always generates exactly one monster and nothing else: no adds, no summons, no
second creature. Its take-damage sound family is "fur". It is flagged not to disappear from Doom
effects and not to fade after death, which matters only cosmetically. The encounter preloads the
`Ringing` affliction overlay art, which is the tell that the card-lock gimmick below is the fight's
identity.

## Structure: two phases separated by a damage threshold

This is a **phase boss with an HP-threshold break**, and almost everything about how the fight plays
follows from that. There is no randomness anywhere in the move machine — every state hard-points at
its successor — so the whole fight is deterministic once you know the break.

### Phase 1 — the charge

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 (always) | **Stamp** | Applies the **Plow** counter to *itself* at 150 | buff |
| 2, 3, 4, … | **Plow** | Charging single-target attack for 18, then gains **2 Strength** | attack + buff |

Plow loops into itself forever. There is no other move, no block, and no defensive beat: phase 1 is
one attack that gets 2 points bigger every turn while the beast stands still and takes whatever you
give it.

### The break

The Plow counter is not a debuff on you — it is a self-applied **HP threshold marker** on the beast,
displayed as a counter of 150. Whenever the beast takes **unblocked** damage and its current HP
lands **at or below that number**, it immediately:

1. loses **all Strength**, both permanent and temporary, wiping the entire phase-1 ramp;
2. becomes **stunned**, forfeiting its next turn entirely;
3. drops the Plow counter (the break can only happen once).

Since it starts at 252 HP, the break costs **102 unblocked damage** at base difficulty — about 40%
of its bar. The threshold check is on damage *received*, not on attacks specifically, so chip
sources count.

### Phase 2 — the ritual

The stun turn is a free turn (hidden from the bestiary move list, though the bestiary does show a
stun entry). The beast then locks into a fixed three-beat rotation, entered on Beast Cry:

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Beast Cry** | Applies **Ringing** to *every* player | debuff |
| 2 | **Stomp** | Single-target attack, 15 | attack |
| 3 | **Crush** | Single-target attack 17, then gains **3 Strength** | attack + buff |

Then back to Beast Cry, forever. Note the Strength engine restarts from zero after the break, so the
fight's damage curve resets and re-climbs at a slower per-turn rate (+3 per three turns instead of
+2 per turn) — but now every third player turn is spent under the card lock.

## Damage / block numbers

| Stat | Base | Ascension variant |
|---|---|---|
| HP (min = max, no roll) | **252** | **262** at A8 `ToughEnemies` |
| Plow threshold (Plow counter) | 150 | 160 at A9 `DeadlyEnemies` |
| Plow damage | 18 | 20 at A9 |
| Plow Strength gain | 2 | 2 (unchanged) |
| Stomp damage | 15 | 17 at A9 |
| Crush damage | 17 | 19 at A9 |
| Crush Strength gain | 3 | 4 at A9 |
| Beast Cry | Ringing 1 to all players | unchanged |

**The beast never blocks.** There is no defensive move in either phase, so every point of output the
player generates lands, and the fight is a pure race in both directions.

### Phase 1 damage curve (base, uninterrupted)

| Beast turn | Move | Damage | Cumulative taken |
|---|---|---|---|
| 1 | Stamp | 0 | 0 |
| 2 | Plow | 18 | 18 |
| 3 | Plow | 20 | 38 |
| 4 | Plow | 22 | 60 |
| 5 | Plow | 24 | 84 |
| 6 | Plow | 26 | 110 |
| 7 | Plow | 28 | 138 |

A typical Act 1 player enters with roughly 70–80 HP, so an unmitigated phase 1 kills around beast
turn 5. You have to deal 102 in the ~4 player turns before that, *while* blocking — which is exactly
the tension the fight is built on. Every turn you spend blocking instead of hitting pushes the break
one turn later and makes the next Plow 2 bigger.

### Phase 2 damage curve (base, from the break)

| Beat | Move | Damage | Strength after |
|---|---|---|---|
| — | (stunned) | 0 | 0 |
| 1 | Beast Cry | 0 | 0 |
| 2 | Stomp | 15 | 0 |
| 3 | Crush | 17 | 3 |
| 4 | Beast Cry | 0 | 3 |
| 5 | Stomp | 18 | 3 |
| 6 | Crush | 20 | 6 |
| 7 | Beast Cry | 0 | 6 |
| 8 | Stomp | 21 | 6 |
| 9 | Crush | 23 | 9 |

Per-cycle incoming runs 32 → 38 → 44 → 50 …, +6 per cycle. With 150 HP left to remove and one of
every three player turns crippled, the practical phase-2 length for a healthy Act 1 deck is three to
five cycles.

## Gimmicks

### Plow (the threshold, and the free turn it buys)

Plow reads as a debuff-typed counter on the boss, and it is the fight's whole first act. Three
consequences worth modelling separately:

- **It rewards burst over sustain.** The check is a fixed HP line, not a damage-per-turn line, so
  banking damage into one big turn breaks the phase at the same point as spreading it — but every
  extra turn spent charging costs 2 more incoming damage *permanently*, so front-loaded output is
  worth strictly more than back-loaded output.
- **The Strength wipe is a refund.** Whatever the beast accumulated in phase 1 evaporates. A player
  who breaks late is punished during phase 1 but not after it, which caps how badly a slow start can
  snowball.
- **The break is only checked on unblocked damage.** Damage fully absorbed by any mitigation on the
  boss's side does not advance the check — practically irrelevant here since the beast never blocks,
  but it does mean the trigger is the damage-received hook and fires on the exact instance that
  crosses the line, mid-turn, granting the stun before its next intent resolves.

### Ringing (the card lock)

Beast Cry applies a one-stack Ringing power to every player. On application it stamps the **Ringing
affliction onto every card that player owns in the combat that does not already carry some other
affliction** — draw pile, hand, discard, everything — and it keeps stamping cards that enter combat
later that turn. The affliction's rule:

> A Ringing card can be played **only if that player has not yet started any card play this turn**.

So the effect is: **the turn after Beast Cry, you get exactly one card play.** The first card can be
anything; the moment it starts resolving, every Ringing card in your hand goes unplayable. The power
removes itself at the end of that player's turn and clears the affliction off every card as it goes.

Two exploitable seams:

- Cards that already carry a **different affliction** are never stamped with Ringing and stay
  playable through the lock. A deck carrying pre-afflicted cards effectively gets extra plays during
  the choked turn.
- Effects that resolve without being a card play — powers, relics, potions, end-of-turn triggers —
  are untouched. Potion-heavy and passive-engine builds barely feel the lock; combo decks that need
  four plays to function lose the turn outright.

The rhythm this creates is the reason phase 2 is not just a smaller phase 1: your turns alternate
between "one card only" and two full turns, so the fight demands you sequence a **big single card**
into the choked turn and dump the rest into the open ones.

## Scaling

**By act:** none. The beast exists only in Act 1, and the only act-index read is via the shared
multiplayer scaling formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | HP 252 → 262 |
| A9 `DeadlyEnemies` | Plow threshold 150 → 160; Plow 18 → 20; Stomp 15 → 17; Crush 17 → 19; Crush Strength 3 → 4 |

Note the unusual shape of A9 here: raising the Plow threshold makes the break happen *earlier* in
damage terms (92 damage to break at A9 alone, versus 102 at base), which partially compensates for
the fact that every Plow now hits for 20 and climbs from there. The real A9 tax is on the back half
— Crush's Strength gain going 3 → 4 changes the phase-2 escalation from +6 per cycle to +8, on top
of the flat +2 on both attacks.

**By seat count (multiplayer):**

- **HP** uses the standard formula: base × players × 1.1 (the Act 1 multiplier; Act 1 has no
  separate boss rate).

| Players | HP (base) | HP (A8+) |
|---|---|---|
| 1 | 252 | 262 |
| 2 | ≈554 | ≈576 |
| 3 | ≈832 | ≈865 |
| 4 | ≈1109 | ≈1153 |

- **The Plow threshold scales identically** — it is flagged to scale in multiplayer and uses the
  same players × 1.1 factor, so the break always sits at the same ~59.5% of the boss's bar (330 at
  two seats, 495 at three, 660 at four). The fraction of the fight spent in each phase is
  seat-count invariant, which is a good property for modelling.
- **Attack damage does not scale, and both attacks are single-target.** Plow, Stomp and Crush each
  pick one seat. In co-op the incoming damage is therefore *diluted* per player — the same numbers
  spread across more health bars — which makes phase 1 much more survivable and shifts the whole
  fight toward a pure output race against a bar that grew by more than the party's damage did.
- **Beast Cry is party-wide.** It applies Ringing to every player creature, at one stack each,
  unscaled. This is the only part of the fight that gets *worse* per seat in relative terms: the
  card-lock turn costs the whole party its tempo simultaneously, so a four-seat party loses four
  turns of throughput every third beat while facing a 4.4× HP bar.

## Proposed fight class: **mixed**

The two phases demand genuinely different things and neither dominates the fight's length. Phase 1
is a hard **race check** — a fixed 102-damage line with an escalating penalty of +2 incoming per
turn of delay, which asks for front-loaded output and punishes any turn spent purely on defense, and
which resolves into a free stun turn once cleared. Phase 2 is a **gimmick check** — a fixed
three-beat rotation whose only real threat is the one-card-per-turn Ringing lock, asking the player
to hold a single high-value card for the choked turn and to dump on the two open ones, while a much
gentler +6-per-cycle ramp runs in the background. It is not spike (no single hit is designed to be
lethal, and there is no burst turn to survive), not attrition (the beast never blocks, has a modest
bar, and the fight is short by construction), and not swarm (it is a solo boss with no adds). For
Track B, model it as two sequential demand vectors: a front-loaded damage-throughput race with a
turn-count-linear penalty term, then a rotation whose per-turn card budget alternates 1 / ∞ / ∞.
