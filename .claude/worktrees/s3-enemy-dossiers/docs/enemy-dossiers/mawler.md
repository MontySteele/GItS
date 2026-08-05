# Enemy Dossier — Mawler

- **Class:** `Mawler`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act pool it appears in
- **Encounters:** `MawlerNormal` (a single Mawler, alone). On a player's very first run ever, the act
  pins `MawlerNormal` to the **5th normal encounter slot**, so it is a scripted early-game teaching
  fight.
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A solo beast with three moves: a two-hit claw, a single big bite, and exactly one roar that lays
Vulnerable on the whole party. It has no Block move, no buff, no summon, no minion, no on-death
effect, no low-HP phase change, and no starting power. Its entire threat is "a predictable stream of
attacks that gets 50% bigger once, and stays bigger."

Structurally it is the simplest shape in the Act 1 pool: one body, one debuff, fixed HP.

## 2. Intent pattern / AI

Three move states hanging off a single uniform random branch. Every move routes back to the same
branch node, which offers all three moves at **equal weight (1 each)** with two repeat constraints:

| State | Intent shown | Effect |
|---|---|---|
| `CLAW_MOVE` | multi-attack, 4 × 2 | Two attack hits of 4 (8 total before Block) against **all opponents**. One attack animation plays for both hits. |
| `RIP_AND_TEAR_MOVE` | single attack, 14 | One attack hit of 14 against **all opponents**. |
| `ROAR_MOVE` | generic **debuff** icon (no number) | Applies **Vulnerable 3** to every player. Deals no damage. |

Repeat rules:

- **Claw** — *cannot repeat*: weight drops to 0 if it was the immediately previous move.
- **Rip and Tear** — *cannot repeat*: same rule.
- **Roar** — *use only once*: weight drops to 0 permanently the moment it has been used. **There is
  exactly one Roar per combat, ever.**

The state machine's initial state is Claw, and the first roll is suppressed (a monster does not
transition away from its opening move before performing it), so:

- **Turn 1 is always Claw (4 × 2).** No RNG.
- **Turn 2** is a 50/50 between Rip and Tear and Roar (Claw is blocked by no-repeat).
- Every turn after that, the previous move is excluded and Roar is excluded once spent.

The consequence worth modeling: **once the Roar has been used, the fight becomes fully
deterministic** — the only two legal moves are Claw and Rip and Tear, each blocked from repeating, so
the beast strictly alternates **Claw → Rip → Claw → Rip …** for the rest of the fight. The whole
random surface of this enemy is a single question: *which turn does the Roar land on?*

Roll distribution for when the Roar arrives (uniform branch, weights as above):

| Roar lands on | Probability |
|---|---|
| Turn 2 | 50% |
| Turn 3 | 25% |
| Turn 4 | 12.5% |
| Turn 5 | 6.25% |
| Turn *n* (n ≥ 2) | 2^−(n−1) |

Expected Roar turn ≈ **3.0**, i.e. it almost always arrives while the player is still at or near full
HP and before most Act 1 decks have their engine online. Median fight length for a tier-0.5-ish Act 1
deck against 72 HP is roughly 5–7 turns, so the party spends most of the fight *after* the Roar.

## 3. Gimmicks

**The Roar is the whole fight.** Vulnerable 3 multiplies incoming powered attack damage by 1.5×, and
it ticks down one stack at the end of each enemy turn — so the Roar turn plus the following two enemy
turns are amplified. Because the beast alternates Claw/Rip after the Roar, those amplified turns are
guaranteed to include at least one Rip and Tear:

| Under Vulnerable | Damage |
|---|---|
| Claw (4 × 2) | 6 × 2 = **12** |
| Rip and Tear (14) | **21** |

Two second-order notes:

- The Roar **costs the beast a turn of damage**, so the Vulnerable window is roughly damage-neutral
  on the Roar turn itself and only profitable across the two turns that follow. Killing fast, or
  cleansing/out-blocking exactly two turns, defuses it entirely.
- Vulnerable multiplies **per hit**, so Claw takes 4→6 twice rather than 8→12 once. Any per-hit
  mitigation the player has (Thorns-likes, flat per-hit reduction, Block granularity) interacts
  differently with the two attacks — Claw is the hit-count move, Rip is the lump-sum move.

**The debuff intent under-sells itself.** The Roar is telegraphed with the *plain* debuff icon rather
than the "strong debuff" variant, and no magnitude is shown. A player reading intents cannot tell
that a 3-stack party-wide Vulnerable is coming — they only see "some debuff." For a scripted 5th
encounter, this is the fight that teaches the player to respect an unlabeled debuff intent.

**No defense, no scaling.** The Mawler never gains Block, never buffs itself, and never changes
behavior with HP. Its damage output is flat for the whole combat except for the one Vulnerable
window. Nothing rewards or punishes fight length except the raw HP total.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP | **72** (fixed — min and max are the same, no roll) | **76** | — |
| Claw | 4 × 2 hits = 8 | — | 5 × 2 hits = **10** |
| Rip and Tear | 14 | — | **16** |
| Roar | Vulnerable 3 to every player | — | — |

- Because min HP == max HP, the encounter's unique-HP pass has nothing to vary; the body is always
  exactly 72 (76 with Tough Enemies).
- It gains no Block, so the enemy-Block multiplayer scaler never touches it.
- Steady-state output after the Roar is the strict alternation, averaging **11 damage/turn** base
  (8 and 14 alternating), or **13/turn** on Deadly Enemies (10 and 16).
- Under Vulnerable the same alternation averages **16.5/turn** base, **19.5/turn** on Deadly Enemies.

Rough unmitigated total for a 6-turn kill with the Roar on turn 3 (base, single seat): 8 + 14 + 0
(roar) + 12 + 21 + 8 ≈ **63**. That is a large fraction of an Act 1 HP bar, which is why this fight
is a block check rather than a race.

## 5. Scaling

**By act:** none. Act 1 only, no act-conditional stats.

**By ascension:** two flat levers, and they are the only two conditionals on the monster.

- *Tough Enemies* (ascension 8): HP 72 → **76**. Roughly a half-turn of extra fight for an Act 1
  deck. It does not widen the Vulnerable window (that has expired by then) — it just adds another
  Claw/Rip beat of flat damage at the back end.
- *Deadly Enemies* (ascension 9): Claw 4 → 5 per hit (8 → **10** per turn) and Rip and Tear 14 → **16**.
  Under Vulnerable those become 15 and 24. The Roar's Vulnerable amount (3) has **no** ascension
  variant.

**By seat count (multiplayer):** this enemy scales badly for the party, and the reason is targeting.

- *HP* uses the shared formula — base × player count × act factor, with the **Act 1 factor 1.1**:

| Players | HP (base 72) | HP (Tough Enemies 76) |
|---|---|---|
| 1 | 72 | 76 |
| 2 | ~158 | ~167 |
| 3 | ~238 | ~251 |
| 4 | ~317 | ~334 |

- *Both attacks target **all opponents**, not one seat.* Claw and Rip are built as attacks against
  every opponent of the attacker, so a 4-seat party takes 8 damage **each** from a Claw (32 across the
  table) and 14 **each** from a Rip. Damage is not divided among seats and there is no per-seat
  reduction anywhere in this monster.
- *Roar* likewise applies Vulnerable 3 to every player — the amount does **not** scale up with seat
  count (unlike enemies that fatten a starting Artifact per seat), but it also does not thin out.

Net co-op shape: HP goes up ~1.1× per seat while the damage load goes up ~1.0× per seat *per player*.
The fight therefore gets **strictly longer** while each individual player's per-turn block requirement
stays exactly the same as in singleplayer — more turns of the same tax, and the Vulnerable window
lands on everyone at once. There is no focus-fire decision (one body) and no way to spread the
damage; the only co-op lever is party-wide mitigation or a faster kill.

## 6. Proposed fight class — `attrition`

What this fight asks per turn is small, constant, and unavoidable: absorb 8, then 14, then 8, then
14, forever, with no body to remove, no add to intercept, and no threshold that ends the pressure
early. That flat repeated demand — and an HP pool that in co-op grows faster than the party's ability
to shorten the fight — is the attrition signature. It is not `spike`: the single largest hit is 21
(24 on Deadly Enemies), it is fully telegraphed by a numbered attack intent, and it arrives inside a
three-turn Vulnerable window that the alternating pattern makes completely predictable rather than as
a burst you must pre-block for. It is not `gimmick` (one debuff, no puzzle, no state to solve) and not
`swarm` (one body); the Roar is a one-shot 1.5× multiplier on the *same* demand curve rather than a
second demand type, which keeps it out of `mixed`. For Track B, model it as **flat sustained
damage-per-turn against a fixed HP pool, with a one-time ~1.5× amplitude bump on turns 2–5**, where
the counterplay is repeatable block (or a kill inside ~5 turns) and not burst mitigation.
