# Enemy Dossier — Shrinker Beetle

- **Class:** `ShrinkerBeetle`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act pool it appears in
- **Encounters:** `ShrinkerBeetleWeak` (one beetle, weak-pool), `OvergrowthCrawlers` (one beetle + one Fuzzy Wurm Crawler)
- **Fight class:** `gimmick`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Shrinker Beetle is Act 1's **damage-tax body**: a small, low-HP insect whose entire design is one
opening move that permanently cuts every player's attack damage by 30% for the rest of the fight.
Its own damage output is unremarkable — a 7/13 alternation — and it never blocks, buffs itself,
summons, or changes behavior at low HP.

It is one of the earliest encounters in the game (in the scripted first-run room order it is fixed to
the **third weak encounter** of Act 1), so it functions as the tutorial for "an enemy can change your
math instead of your HP bar."

## 2. Intent pattern / AI

Three states in a fixed chain, **fully deterministic** — no RNG is consulted for this enemy, so the
whole fight is readable from turn 1.

| State | Intent shown | Effect |
|---|---|---|
| `SHRINKER_MOVE` | strong debuff | Applies **Shrink** to every player. Cast animation, radial blur. |
| `CHOMP_MOVE` | attack, 7 | 7 damage to every player creature. |
| `STOMP_MOVE` | attack, 13 | 13 damage to every player creature. |

Flow: **Shrink → Chomp → Stomp → Chomp → Stomp → …** forever. Shrink is the initial state, fires
exactly once on turn 1, and is never returned to. After that the beetle is a two-beat metronome.

**Bestiary legibility note:** the beetle deliberately hides `STOMP_MOVE` from its bestiary entry.
A player who scouts it in the bestiary sees only Shrink and the 7-damage Chomp, and will therefore
underestimate its real per-turn output by nearly half. The reveal is meant to happen at the table.

## 3. Gimmicks

**Shrink (the whole enemy).** Applied to *all* player creatures on turn 1, and applied at the special
"infinite" amount rather than a stack count. Consequences of that choice:

- It renders as a **single, countless debuff icon**, not a counter, and it does **not tick down** at
  end of turn. It is permanent for the duration of the fight.
- The one thing that removes it is the **death of the applier**. When the beetle dies, the Shrink it
  put on everyone is stripped immediately.
- Effect: a **multiplicative ×0.70 on the owner's powered attacks** — i.e. the player deals 30% less
  attack damage. Being multiplicative, it costs the most in absolute terms on your biggest single
  hit, and it can round small hits down hard (a 3-damage multi-hit ping becomes 2).
- It only touches *powered* attack damage. Unpowered/flat damage sources (burn-style self-damage,
  effects deliberately flagged to skip powers) are unaffected.
- Cosmetically the shrunk creature scales to 50% size, which is also the tell that it landed.

**The kill-order rule in `OvergrowthCrawlers`.** Because Shrink dies with its applier, the paired
encounter has a correct answer: **kill the beetle first**. The Fuzzy Wurm Crawler is the larger body
(55–57 HP, 58–59 on Tough Enemies) and it *ramps* — its cycle is Acid Goop 4 → Inhale (+7 Strength)
→ Goop 11 → … — so trying to burn the Crawler down first means doing it at 70% damage into a target
whose output is climbing. Clearing the 38–40 HP beetle costs one or two turns, refunds your full
damage for the rest of the fight, and removes the smaller half of the incoming damage. This is the
single most load-bearing decision the enemy creates anywhere.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 38–40 | 40–42 | — |
| Chomp | 7 | — | 8 |
| Stomp | 13 | — | 14 |
| Shrink | −30% player attack damage, permanent | — | — |

- HP is rolled inclusively from the band; in `OvergrowthCrawlers` the unique-HP pass nudges bodies
  apart where the bands allow.
- It never gains Block, so the enemy-Block multiplayer scaler never touches it.
- Steady-state output from turn 2 onward is **10 damage/turn averaged** (20 per two-turn cycle), or
  **11/turn** on Deadly Enemies. Turn 1 deals **zero** damage.
- The effective-HP view is the honest one: 38–40 HP taken at 70% throughput plays like a
  **~54–57 HP body** (~57–60 with Tough Enemies) that also gave you a free first turn.

## 5. Scaling

**By act:** none. Act 1 only, no act-conditional stats.

**By ascension:** two flat levers, both small. Tough Enemies moves the HP band up 2 at each end
(38–40 → 40–42). Deadly Enemies takes Chomp 7 → 8 and Stomp 13 → 14, i.e. 20 → **22 per two-turn
cycle**. The Shrink percentage (30) has **no ascension variant** — the gimmick is identical at every
ascension, which means the enemy gets relatively *less* interesting as ascension rises: only the
boring half of it scales.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 1 factor being
  **1.1**.

| Players | Effective HP band (base roll) |
|---|---|
| 1 | 38–40 (no scaling at 1 player) |
| 2 | ~84–88 |
| 3 | ~125–132 |
| 4 | ~167–176 |

- *Shrink* is applied to **every player creature**, with no per-seat amount adjustment and no code
  branch — the debuff simply covers the whole table because the move targets all opponents. The tax
  is therefore **100% efficient in co-op**: one enemy turn, one animation, the entire party's damage
  cut by 30%.
- *Chomp and Stomp* also target all opponents at their **full listed value per seat** — 7/13 is what
  each player takes, not a total split among them. Per-seat damage pressure is flat across seat
  counts.

Net co-op shape: the beetle is meaningfully *harder* with more seats, and for an unusual reason. Its
HP grows superlinearly (×1.1 per seat on top of the per-seat multiplier) while the party's aggregate
damage against it is simultaneously cut 30%, so the number of turns to clear it stretches — and every
extra turn is another 7/13 landing on **each** seat. A 4-player table is fighting a ~170 HP body at
70% throughput while taking 10/turn/seat. This is the encounter's only genuinely dangerous
configuration.

## 6. Proposed fight class — `gimmick`

Per turn this fight demands almost nothing defensively: 7 or 13 telegraphed damage on a fixed
alternation, no burst turn, no ramp, no threshold, and a free turn 1. What it actually demands is
that you **re-solve your damage math once and then act on the answer** — accept that every attack is
worth 70% for the rest of the combat, notice that the tax dies with the taxman, and in
`OvergrowthCrawlers` sequence your targets accordingly instead of focusing the fat, ramping Crawler.
That is a single rule-shaped puzzle rather than a sustained resource demand, which rules out
`attrition` (the HP pool is tiny and the chip damage never threatens); the flat 13 is far too small
for `spike`, one body is not a `swarm`, and there is no second demand type running alongside the
gimmick to make it `mixed`. For Track B, model this as a **flat, low, fully-predictable damage floor
with a one-time multiplicative throughput penalty applied from turn 1** — the demand curve should be
near-zero on defense and should instead register as a ~1.43× lengthening of the player's expected
kill-time, with a discrete payoff for correct target priority in the two-body version.
