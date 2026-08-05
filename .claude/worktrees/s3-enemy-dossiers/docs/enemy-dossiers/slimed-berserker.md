# Enemy Dossier — Slimed Berserker

- **Class:** `SlimedBerserker`
- **Kind:** normal
- **Act:** Act 3 (`Glory`, act index 2) — the only act pool it appears in
- **Encounters:** `SlimedBerserkerNormal` (solo; the encounter spawns exactly one body, no partners)
- **Fight class:** `mixed`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A single fat 261 HP body in Act 3 that runs a **strictly deterministic four-turn loop**: pollute,
flurry, buff-and-debuff, then a very large single hit. It has no Block move, no summon, no on-death
effect, no low-HP phase change, and no RNG anywhere in its move selection — the entire fight is
readable from turn 1 and stays on the same clock until it dies.

The one thing that *does* change over the fight is its Strength: every fourth turn it gives itself a
permanent +3, so both of its attacks get worse the longer the fight runs. That ramp, sitting on top
of a large HP pool, is the whole design: it is a soft timer that punishes decks which cannot close.

Note a presentation quirk: the big single attack is **deliberately hidden from the bestiary entry**.
The other three moves are listed; the finisher is not. A player who scouts this enemy will know about
the slime, the flurry and the hug, and will meet the 30-damage smother cold the first time.

## 2. Intent pattern / AI

Four move states chained head-to-tail in a closed ring, entered at Vomit Ichor. No branch, no
cooldown, no interrupt, no reroll — the state machine never consults RNG for this enemy.

| Turn in cycle | State | Intent shown | Effect |
|---|---|---|---|
| 1 | `VOMIT_ICHOR_MOVE` | status, 10 cards | Adds **10 Slimed** to the discard pile of **every player**. Deals no damage. |
| 2 | `FURIOUS_PUMMELING_MOVE` | multi-attack, 4 × 4 | Four hits of 4 (16 before Block and before Strength). |
| 3 | `LEECHING_HUG_MOVE` | debuff + buff | **Weak 3** to every player, **+3 Strength** to itself (permanent, uncapped). |
| 4 | `SMOTHER_MOVE` | single attack, 30 | One hit of 30 (before Block, before Strength). Hidden from the bestiary. |

Flow: Vomit → Pummeling → Hug → Smother → Vomit → … forever.

The rhythm this produces is worth stating plainly, because it is what the fight actually *feels* like:

- **Turn 1 of each cycle is a free turn defensively** — zero incoming damage — but it is the turn the
  enemy taxes your deck. It is the natural turn to dump Block-less setup and to push damage.
- **Turn 2 is the small-hit turn**: four separate 4s. Thin Block is eaten cheaply; per-hit mitigation
  (anything that reduces damage per instance) is disproportionately good here, and per-hit *punish*
  effects (thorns-likes) get four triggers.
- **Turn 3 is again zero damage**, but it is the turn that makes every future turn worse and blunts
  your own offense for the next three turns.
- **Turn 4 is the spike**: one large hit that grows by +3 per cycle. Any per-hit mitigation is nearly
  worthless; you want a real Block wall or to have already won.

## 3. Gimmicks

**Slimed flood (10 per player, per cycle).** Slimed here is a 1-cost Status card that Exhausts and
**draws 1 when played**. It is not unplayable and it is not Ethereal — so unlike Dazed, it is a real
1-energy cantrip tax rather than a dead card. The pollution therefore hits **energy**, not draw
quality: a hand with three Slimed in it costs three energy and three card-plays to clear, and it
clears itself permanently (Exhaust) once paid. Ten copies land in the *discard*, so they arrive on the
next shuffle rather than the current hand, and each cycle refills the pool faster than most decks can
burn it. Deck-size-agnostic decks with spare energy shrug at this; tight 3-energy curves drown.

**Strength ramp (+3 every fourth turn, permanent).** Applied on the Hug turn, no cap, no removal
condition. Because the flurry is a **four-hit** move, each +3 is worth **+12 on the Pummeling turn**
and only +3 on the Smother turn — the multi-hit move is where the ramp actually bites.

**Weak 3, reapplied every four turns.** Weak in STS2 is a multiplicative **×0.75 on the affected
creature's own powered attacks**, ticking down at the end of the enemy's turn. Applied on turn 3 of
each cycle with 3 stacks and refreshed every 4 turns, it covers 3 of every 4 of your turns — roughly
**75% uptime of a 25% damage cut on your attacks** for the whole fight. Combined with the enemy's own
Strength ramp, the damage race tilts against you a little more every cycle, which is exactly the
pressure the design wants.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP | 261 (fixed — min and max are equal, no roll) | 281 | — |
| Vomit Ichor | 10 Slimed to each player's discard | — | — |
| Furious Pummeling | 4 × 4 hits = 16 | — | 5 × 4 hits = **20** |
| Leeching Hug | Weak 3 to all players; +3 Strength to self | — | — |
| Smother | 30 | — | **33** |

Damage-per-cycle with the Strength ramp folded in (base ascension, no player mitigation):

| Cycle | Pummeling turn | Smother turn | Cycle total | Cumulative |
|---|---|---|---|---|
| 1 (turns 1–4) | 4×4 = 16 (Str 0) | 30 (Str 0) | 46 | 46 |
| 2 (turns 5–8) | 4×7 = 28 (Str 3) | 36 (Str 6 by then) | 64 | 110 |
| 3 (turns 9–12) | 4×10 = 40 (Str 6) | 39 | 79 | 189 |
| 4 (turns 13–16) | 4×13 = 52 (Str 9) | 42 | 94 | 283 |

(Strength is granted on turn 3 of each cycle, so the Pummeling turn of cycle *n* runs at Strength
3(n−1) and the Smother turn of cycle *n* at Strength 3n.) Steady state adds **+15 damage per cycle**,
i.e. roughly **+3.75 damage/turn per cycle elapsed** — a genuinely divergent curve, not a plateau.

At Deadly Enemies the same table starts at 4×5 = 20 and 33, and the Pummeling ramp is unchanged in
slope (Strength adds per hit, so still +12/cycle) but starts from a higher base: 20 → 32 → 44 → 56.

## 5. Scaling

**By act:** none. Act 3 only, no act-conditional stats.

**By ascension:** two flat levers, and they hit different halves of the fight. Tough Enemies adds 20
HP (261 → 281), which because of the Strength ramp is worth more than 20 damage of extra effort — it
buys the enemy roughly a third of an extra cycle at exactly the point where cycles are most expensive.
Deadly Enemies raises the per-hit flurry damage from 4 to 5 (16 → **20** per Pummeling turn) and
Smother from 30 to **33**. The Slimed count (10), the Weak amount (3) and the Strength gain (3) have
no ascension variants.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 3 **non-boss** factor
  being **1.2** (only Act 3 bosses get 1.3).

| Players | Effective HP (base) | Effective HP (Tough Enemies) |
|---|---|---|
| 1 | 261 (no scaling at 1 player) | 281 |
| 2 | ~626 | ~674 |
| 3 | ~940 | ~1012 |
| 4 | ~1253 | ~1349 |

- *Both attacks target every opponent.* Monster attacks built this way target all opposing creatures,
  so Pummeling and Smother land in **full on each seat** — the damage is not split across the party.
  Per-seat pressure is therefore identical at 1 and 4 players.
- *Vomit Ichor* delivers its 10 Slimed to **each player** independently, so total garbage created is
  10 × seats per cycle. It is not divided.
- *Leeching Hug* applies Weak 3 to **every player** and a single +3 Strength to itself — the Strength
  does not scale with seats, but because the Strength applies to attacks that hit every seat, its
  *effective* output does.
- There is no Block move, so the enemy-Block multiplayer scaler never touches it.

Net co-op shape: this is the bad direction for a scaling enemy. HP grows by ×N×1.2 while the per-seat
damage and per-seat status load stay constant, so the fight takes proportionally *longer* — and every
extra turn is another slice of a Strength ramp that is applied to attacks hitting every seat at once.
A four-seat table is fighting roughly 4.8× the HP with the same per-player defensive budget, and will
reach cycle 4–5 (52–65 per flurry turn, 42–45 per smother) where a solo run reaches cycle 2–3.

## 6. Proposed fight class — `mixed`

The per-turn demand here rotates through four genuinely different asks on a fixed clock, and no single
one dominates: turn 1 asks for nothing defensively but taxes your energy budget for the next several
turns, turn 2 asks for per-hit mitigation against a 4-hit flurry, turn 3 asks you to accept a
permanent enemy buff and a 25% cut to your own offense, and turn 4 asks for a single large Block wall
against a hit that starts at 30 and never stops growing. That last beat is a real `spike` and the
261-HP-plus-Strength-ramp body is real `attrition`, but neither label alone would tell Track B to
model a player who needs *both* a thin-hit answer and a fat-hit answer within the same two turns —
which is the actual difficulty of this fight. It is not `swarm` (one body, no summons) and not
`gimmick` (the Slimed flood is a resource tax, not a puzzle with a solution state), so `mixed` is the
honest label; if the curve ever needs a single-mode fallback, `attrition` is the better second choice,
because the fight is ultimately lost on the clock rather than on any one turn.
