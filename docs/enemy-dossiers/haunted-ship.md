# Enemy Dossier — Haunted Ship

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `HauntedShip`
- **Kind:** normal
- **Act:** Act 1 (`Underdocks`, act index 0) — the only act pool it appears in
- **Encounters:** `HauntedShipNormal` (one Haunted Ship, alone — no partner, no summons)
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A single large body, fixed HP, that opens the fight with a **one-time scream** — no damage, but Weak
on every player plus a fat dump of Dazed into every player's discard — and then settles into a rigid
two-beat physical alternation for the rest of the combat. Everything scary about it happens on turn
one, and everything after turn one is arithmetic.

It never blocks, never buffs itself, never summons, has no on-death effect, no low-HP phase change,
and no starting power applied on room entry. It also does not re-cast its opener: once the state
machine leaves the scream, nothing routes back to it.

Its HP has **no roll at all** — minimum and maximum are the same number — so the fight length is
identical every time you see it at a given ascension and seat count.

## 2. Intent pattern / AI

Three states, **fully deterministic** — no RNG is consulted anywhere in this enemy's transitions.

| State | Intent shown | Effect |
|---|---|---|
| `HAUNT_MOVE` | debuff + status (5) | Applies **Weak 3** to every player and adds **5 Dazed** to every player's discard pile. Deals no damage. |
| `SWIPE_MOVE` | single attack, 13 | One attack of 13 against its current target. |
| `STOMP_MOVE` | multi-attack, 4 × 3 | Three attack hits of 4 (12 total before Block) against its current target, on a single played animation. |

Flow: **Haunt → Swipe → Stomp → Swipe → Stomp → …** forever. The haunt is the machine's initial
state and is unreachable afterwards, so it is strictly a turn-1 event. From turn 2 onward the enemy
alternates 13 / 12 with no branch, no escalation, and no interrupt — the entire fight is readable
from the first intent icon.

Because both attack moves are single-target, in co-op the physical half of the fight lands on one
seat at a time while the turn-1 haunt lands on the whole table at once.

## 3. Gimmicks

**The scream is the whole design.** It is a pure tempo tax delivered before you have taken a point of
damage:

- **Weak 3** on every player. Weak here is a multiplicative **0.75×** on the player's own powered
  attack damage, and it ticks down once at the end of each enemy turn — so it covers your first
  three offensive turns, exactly the window in which you would otherwise be racing this enemy's
  smallish HP pool. Practical effect: the ship is functionally ~33% tankier for the opening of the
  fight, which converts directly into extra turns of Swipe/Stomp chip.
- **5 Dazed** into each player's *discard* pile. Dazed is cost −1 (uncastable cost), **Unplayable**
  and **Ethereal**. Landing in discard rather than hand means it does not brick the current turn; it
  arrives on the next shuffle and degrades draw quality from then on. Ethereal makes each drawn copy
  self-delete at end of turn, so the pollution is self-clearing — but with 5 copies from a single
  cast and no second cast to refill, this is a one-shot slug of bad draws timed to hit right when
  the Weak wears off.

**Multi-hit stomp.** 4 × 3 rather than 12 × 1 matters only against per-hit effects: flat per-hit
damage reduction and Thorns-style retaliation are strongly favoured against it, while raw Block sees
the same 12. It also means the stomp is the turn where per-hit triggers on the player side pay out
three times.

**No Block move at all**, so the enemy-Block multiplayer scaler never touches this fight — a rare
case where added seats do nothing but inflate HP.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP (fixed, no roll) | 63 | 67 | — |
| Haunt — Weak applied | 3 (all players) | — | — |
| Haunt — Dazed to discard | 5 (each player) | — | — |
| Swipe | 13 | — | 14 |
| Stomp | 4 × 3 hits = 12 | — | 5 × 3 hits = 15 |

- Steady-state output from turn 2 is **12.5 damage/turn averaged** (13 / 12 alternating), rising to
  **14.5/turn** on Deadly Enemies (14 / 15).
- Turn 1 deals **0** damage. Total damage taken over an N-turn kill is therefore roughly
  12.5 × (N − 1) at base, and the Weak is what pushes N up.
- Weak on the player ticks at the end of each enemy turn, so it covers player turns 2, 3 and 4
  (the three turns after the scream).

## 5. Scaling

**By act:** none. Act 1 (`Underdocks`) only, no act-conditional stats.

**By ascension:** two independent flat levers.

- *Tough Enemies* raises the fixed HP from 63 to **67** (+6.3%). Because min == max, this is a hard
  number, not a band shift.
- *Deadly Enemies* raises both attacks: Swipe 13 → **14**, and each Stomp hit 4 → **5**, i.e. the
  stomp turn goes 12 → **15**. That is the larger of the two moves' bumps and makes the alternation
  slightly *stomp-heavy* instead of swipe-heavy.
- Neither the Weak amount (3) nor the Dazed count (5) has an ascension variant.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 1 non-boss factor
  being **1.1**.

| Players | Effective HP (base) | Effective HP (Tough Enemies) |
|---|---|---|
| 1 | 63 (no scaling at 1 player) | 67 |
| 2 | ~139 | ~147 |
| 3 | ~208 | ~221 |
| 4 | ~277 | ~295 |

- *Swipe and Stomp do not scale* with seats and hit a single target, so per-seat incoming damage
  falls off sharply as players are added — at four seats the party is soaking 12.5/turn spread across
  four health bars while chewing ~277 HP.
- *The haunt scales for free*: Weak 3 and 5 Dazed are delivered to **every** player, so the total
  debuff and garbage created is 3 Weak × seats and 5 Dazed × seats from the one cast. In a four-seat
  party that is 20 status cards and a table-wide 0.75× damage multiplier for three turns against a
  pool that just quadrupled.
- Net co-op shape: the fight stops being a damage race and becomes a long, low-threat slog whose only
  real cost is the opening tempo hit — the one part of it that *does* grow with the table.

## 6. Proposed fight class — `attrition`

What this fight asks per turn is small and unchanging: block or eat 12–13 (14–15 on Deadly Enemies)
from a perfectly telegraphed alternation, with no turn where the number jumps and no threshold that
pays out — which rules out `spike`. One body rules out `swarm`, and the scream is not a puzzle to
solve or a state to manage (it fires once, cannot be prevented, and never returns), so it is not
`gimmick`; nor is there a second live demand type running alongside the attacks to make it `mixed`.
The enemy's actual design lever is **turn inflation** — Weak 3 slows your clock by 25% for the exact
window you would use to burst it down, and the 5 Dazed degrade your draws just as the Weak expires,
so every turn you fail to close costs you another 12.5 chip. For Track B this should be modeled as a
**short flat-pressure grind with a front-loaded output tax**: the demand curve is "sustain ~12.5/turn
while your damage output is multiplied by 0.75 for three turns and your deck gains five dead cards,"
and the counterplay that matters is having enough non-attack throughput (or Weak removal) that the
opener does not add turns.
