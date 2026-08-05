# Enemy Dossier — Skulking Colony

- **Class:** `SkulkingColony`
- **Kind:** elite
- **Act:** Act 1 (`Underdocks`, act index 0 — the alternate Act 1 pool alongside `Overgrowth`)
- **Encounters:** `SkulkingColonyElite` — solo, a single Skulking Colony and nothing else
- **Fight class:** `gimmick`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A single armored body with a **fixed 75 HP** (no roll — its min and max initial HP are the same value)
and a completely deterministic four-move loop. Its entire identity is one self-applied buff, granted on
entering the room, that **caps the damage it can lose in a single turn at 20**. It gains no Block, never
heals, never summons, and never varies its sequence. What it does do is get permanently stronger on a
fixed clock while the shell guarantees the fight cannot be ended quickly.

`SkulkingColony` is the **only** user of this shell power anywhere in the model tree — it is a bespoke
mechanic, not a shared elite trait.

Cosmetics only: it supports the Phobia alternate skin (the accessibility skin toggle), takes
stone-type hit reactions, and has its own kick/spin/slap/thrust attack SFX set.

## 2. Intent pattern / AI

Four move states wired into a **hard cycle** — each state's follow-up is fixed, there is no random
branch, no weighting, and no RNG consulted at all. The machine also holds its initial state for the
first move, so the opening turn is always the same.

| Turn (mod 4) | State | Intent shown | Effect |
|---|---|---|---|
| 1 | `ZOOM_MOVE` | single attack, 14 | Straight 14 damage (heavy-attack anim, kick SFX) |
| 2 | `ZOOM_MOVE_2` | single attack, 14 | Identical second Zoom — a distinct state, same move |
| 3 | `INERTIA_MOVE` | attack **+ buff** | 9 damage, then **+2 Strength to itself**, permanently |
| 4 | `PIERCING_STABS_MOVE` | multi-attack, 7 × 2 | Two hits of 7, one animation, two damage events |
| → | back to `ZOOM_MOVE` | | loop forever |

The player can therefore read the entire fight from turn one, and the intent icon shows live
Strength-adjusted damage, so the growth is visible before it lands.

The **shape of the loop matters more than the numbers**: the two Zooms front-load the cycle, Inertia is
the only growth turn, and Piercing Stabs is the move that converts accumulated Strength most
efficiently (Strength applies *per hit*, so every point bought by Inertia is worth double on the
following turn).

## 3. Gimmicks

**Hardened Shell — a hard 20-damage-per-turn cap.** Applied to itself at 20 when the room loads. It is
a Buff-type counter, so debuff-strip and Artifact-style effects do not touch it, and it is never
removed or reduced during combat.

How it actually works:

- It intercepts **HP loss**, not just attacks, and clamps each incoming amount to
  `20 − (damage already taken this turn)`. Once the running total hits 20, every further point this
  turn is voided.
- The running total counts **unblocked** damage only, and a fully-blocked hit is ignored entirely.
  (The Colony has no Block, so in practice "unblocked" means "all of it".)
- **Poison, burn, and any other HP-loss share the same 20 budget** as your attacks. Damage-over-time is
  not a way around the shell; it is a competitor for the same allowance.
- The counter **resets at the start of each side's turn**. Practically that means the player gets one
  fresh 20 per player turn, and thorns/retaliation damage during the enemy turn draws on a separate
  fresh 20 — a small but real bonus for reactive damage builds.
- The displayed amount ticks down as you spend it, and when the budget is exhausted the enemy's HP
  readout switches to an "infinite" display: an explicit, unmissable tell that further damage this turn
  is wasted.

**Consequences worth stating plainly:**

- **Overkill is destroyed, not carried.** A single 40-damage hit deals 20. A 60-damage hit deals 20.
  Every burst archetype is flattened to the same output as a hand that deals exactly 20.
- **The fight has a hard minimum length of 4 player turns.** 75 HP against a 20/turn ceiling cannot be
  closed in three turns even in theory (3 × 20 = 60). The player is therefore *guaranteed* to face at
  least Zoom, Zoom, Inertia and Piercing Stabs — the full cycle, 55 incoming damage at base — no matter
  how strong their deck is.
- **The optimal play is to deal exactly 20 and spend everything else on defense.** This is the inverse
  of normal elite math: efficiency here means *under*-committing offense. Cards that deal 25 are worth
  the same as cards that deal 20, and the energy difference between them is the whole game.
- Multi-hit and single-hit damage are equivalent against the shell (unlike most armor mechanics, which
  favor one or the other), so deck archetype barely matters for the offense side — only the total.
- **A weak deck is punished as hard as a strong deck is throttled.** If the party cannot reliably reach
  20 per turn, the fight stretches past four turns into a second Inertia and a rising Strength curve,
  and the shell's floor becomes a ceiling on catching up.

**Inertia's escalation.** +2 Strength per cycle, permanent, applied after the Inertia attack resolves —
so the buff is felt from Piercing Stabs onward. Because Strength applies per hit, one Inertia adds
+2 to each Zoom, +2 to the next Inertia, and **+4 to the Piercing Stabs total**.

**Incoming damage per cycle** (base, before player Block), where *k* is the zero-indexed cycle number:

| Cycle | Str at cycle start | Zoom | Zoom | Inertia | Stabs (×2) | Cycle total |
|---|---|---|---|---|---|---|
| 1st (k=0) | 0 | 14 | 14 | 9 | 9 × 2 = 18 | **55** |
| 2nd (k=1) | 2 | 16 | 16 | 11 | 11 × 2 = 22 | **65** |
| 3rd (k=2) | 4 | 18 | 18 | 13 | 13 × 2 = 26 | **75** |

General form at base: `55 + 10k` per cycle, i.e. a gentle +2.5 damage/turn per cycle. This is a slow
burn by elite standards — the escalation is not the threat, the *floor on fight length combined with*
the escalation is. A party that solves the 20-per-turn puzzle sees only the 55 row; a party that
cannot see the 65 and 75 rows arrive on schedule.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP (fixed, no roll) | 75 | 80 | — |
| Hardened Shell (damage cap per turn) | 20 | — | — |
| Zoom (single) | 14 | — | 16 |
| Inertia (single + self-buff) | 9, then +2 Strength | — | 11, then +4 Strength |
| Piercing Stabs (multi) | 7 × 2 hits = 14 | — | 8 × 2 hits = 16 |
| Strength gained per Inertia | 2 | — | 4 |
| Starting Strength | 0 | — | — |

- HP is a fixed value, not a band — every Skulking Colony in every run has identical HP for a given
  ascension and seat count. This makes the turn-count floor exactly computable by the player.
- It never gains Block, so the enemy-Block multiplayer scaler never applies to it.
- The shell amount (20) has **no** ascension variant.

## 5. Scaling

**By act:** none. Underdocks-only, no act-conditional stats. As an Act 1 elite it is met with an
unrefined deck, which is exactly when a 20/turn cap is most likely to be the *binding* constraint
rather than a mild inconvenience.

**By ascension:** two levers, and they pull in interestingly different directions.

- *Tough Enemies* raises HP 75 → 80. This looks like a 6.7% bump but is worse than that: at 20/turn the
  kill floor goes from "4 turns with 15 damage of slack" to "4 turns with **zero** slack" — the party
  must now hit the full 20 cap on all four turns to close in four, or eat a fifth turn (a second Zoom
  cycle opener at elevated Strength).
- *Deadly Enemies* raises every attack (14→16, 9→11, 7→8 per stab) **and doubles the growth rate**
  (+2 → +4 Strength per Inertia). Ascended cycle totals become `67 + 20k`: **67 / 87 / 107**. The
  offense-side ceiling is unchanged, so the whole ascension effect lands on the defense side of the
  player's turn — precisely the side that the shell already forces them to over-invest in.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, the Act 1 non-boss factor being
  **1.1**.
- *The shell scales too* — it is explicitly flagged as a multiplayer-scaling power and goes through the
  same `amount × player count × act factor` path when applied to a primary/secondary enemy.

| Players | Effective HP | Effective per-turn damage cap | Turns to kill at cap |
|---|---|---|---|
| 1 | 75 | 20 | 4 |
| 2 | ~165 | 44 | 4 |
| 3 | ~248 | 66 | 4 |
| 4 | ~330 | 88 | 4 |

- **The 4-turn floor is preserved exactly at every seat count** — HP and the cap scale by the same
  factor, so co-op does not shorten or lengthen the guaranteed exposure. That is almost certainly
  deliberate.
- **Attacks are not split across seats.** A monster attack with no designated single target resolves
  against every player creature, so **each seat independently eats the full 14 / 14 / 9 / 7×2**, and
  every seat feels the Strength growth. Total damage output across the table is therefore `seats ×` the
  cycle table above, while the party's offense is capped at `seats × 1.1 ×` the solo cap.
- Net co-op shape: the incoming damage scales at `1.0× per seat` and the outgoing allowance at
  `1.1× per seat`, so the fight gets marginally *easier* per seat on the damage race — but the shared
  cap creates a coordination problem instead. A party where one seat can deal 60 and the others 10 each
  wastes most of the strong seat's turn, since the budget is a single pool the table spends together.
  The mechanic actively punishes uneven power distribution in co-op.
- Intent numbers are computed against the local seat's own modifiers, so each player sees their own
  adjusted incoming figure.

## 6. Proposed fight class — `gimmick`

What this fight demands per turn is not "survive a spike" or "outlast a pool" but a **budget
allocation**: deal exactly 20 (never more, since the surplus evaporates) and convert every remaining
point of energy into defense against a fully-telegraphed, fully-deterministic incoming number. Strip
the shell out and what remains is a 75 HP body swinging for ~13.75/turn on a fixed loop — a soft
Act 1 elite that most decks would delete in two turns. The shell inverts the normal offense/defense
tradeoff so completely that the correct line is to *hold damage back*, which is a rule no other Act 1
encounter asks for.

It is not `spike` (no burst turn exists — the loop's biggest single number is 14+Str, and it is
announced four turns in advance), not `attrition` (the HP pool is small and the escalation is only
+2.5 dmg/turn per cycle; the length floor is imposed by a rule, not by a resource race), and not
`swarm` (one body, no summons). For Track B it should be modeled as a **clipped demand curve**: player
damage demand is a step function that saturates hard at 20/turn — marginal offense above the cap has
exactly zero value — while defensive demand is a known, deterministic 55/65/75-per-cycle schedule with
a guaranteed minimum exposure of four turns. The right instrument is "can the party hit the cap every
turn *and* block the known incoming," not average DPS.
