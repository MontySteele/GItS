# Enemy Dossier — Thieving Hopper

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `ThievingHopper`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `ThievingHopperWeak` only — a **weak-pool** encounter (one of Act 2's two weak
  slots), tagged `Thieves`, containing a **single fixed monster** with no rolled slots and no allies.
  The hopper is always alone and appears in no other encounter.
- **Fight class:** `gimmick`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

An early-Act-2 thief on a **hard five-turn clock**. It opens by stealing a card out of the player's
deck, spends the middle of the fight hitting moderately while wearing a damage-halving hover buff,
and then **leaves the fight forever on its fifth move**, taking the card with it. Nothing about the
sequence is random: the move machine is a straight chain with a terminal self-loop, so every intent
in the fight is knowable from turn one.

The loss condition is unusual for a normal fight: the player is not really in danger of dying (52
incoming damage across the entire encounter at base), they are in danger of **permanently losing a
deck card**. The card is pulled out of the run deck the moment it is stolen and is only given back if
the hopper is killed before it escapes.

It also has a visible countdown buff whose only job is to show how many turns remain before the
escape, and it pulses on the final turn — the fight is deliberately legible as a timer.

## 2. Intent pattern / AI

Five move states in a single chain; the last one loops on itself. No branching, no RNG in move
selection, no HP-threshold behavior.

| Turn | State | Intent shown | Effect |
|---|---|---|---|
| 1 | `THIEVERY_MOVE` | Attack (17) + card-debuff icon | Steals one card from **each living player** (see §3), then attacks for **17**. |
| 2 | `FLUTTER_MOVE` | Buff (no number) | Deals no damage. Takes off, becomes airborne, gains **Flutter 5** on itself. |
| 3 | `HAT_TRICK_MOVE` | Attack (21) | Hits for **21**. |
| 4 | `NAB_MOVE` | Attack (14) | Hits for **14**. |
| 5+ | `ESCAPE_MOVE` | Escape | Flees combat permanently. Follows up to itself, so once reached it can never leave this state. |

Flow is fixed: Thievery → Flutter → Hat Trick → Nab → Escape. **The player gets four monster turns of
fight and then the enemy is gone**, along with all of its powers and the stolen card.

All three attacks are ordinary attacks aimed at **all opponents** (the standard monster targeting), at
full listed value per seat. None of them multi-hit and none apply a status.

The only thing that can perturb the chain is a Flutter break (§4), which inserts one **stunned turn**
— the hopper does nothing that turn, then resumes at the follow-up of its last logged move. That
delays the escape by exactly one turn.

## 3. Gimmick A — the theft, and what makes it permanent

On its first move the hopper looks at **each living player's draw pile plus discard pile**, restricted
to cards that actually belong to that player's run deck (temporary/generated combat cards are
ineligible), and takes one.

**Selection priority** — it walks four filters in order and stops at the first that has any match,
then picks randomly within that bucket:

1. **Uncommon**, not Imbued
2. **Common / Rare / Event**, not Imbued
3. **Basic / Quest**, not Imbued
4. **Ancient**, or anything **Imbued**

So it preferentially eats mid-value cards, and it treats **Imbued enchantments as protection**: an
Imbued card is only stolen when the player has literally nothing else eligible. Ancient cards are
likewise last-resort. Rares are in bucket 2, not bucket 1 — an all-uncommon-free deck exposes rares.

**Consequences of the steal:**

- The card is removed from the combat piles **and from the run deck immediately**.
- The hopper gains an instanced Swipe buff carrying that card; hovering it shows the stolen card, so
  the player can see exactly what is at stake.
- **If the hopper dies:** the card is returned to the deck and also surfaced as a special end-of-combat
  reward callout, and the run's map history marks the loot as recovered.
- **If the hopper escapes:** all of its powers are stripped on the way out, the Swipe death-trigger
  never fires, and **the card is gone for the rest of the run**.

In co-op the theft is per seat: every living player loses one card on turn 1, chosen independently by
the same priority list, and every one of those cards is recovered or lost together on the single kill.

## 4. Gimmick B — Flutter, the hit-count shield

On turn 2 the hopper goes airborne and applies **Flutter 5** to itself. Flutter does two things:

- **Halves incoming damage** (a flat ×0.5 multiplicative reduction) from **powered attacks** only.
  Unpowered attacks and non-attack damage are unaffected — but they also do not break it.
- **Loses one stack per damage instance** that gets at least 1 point of unblocked damage through, from
  a powered attack. **Per instance, not per point** — five 1-damage pokes strip it exactly as fast as
  five 30-damage swings.

When the last stack comes off, the hopper is **stunned**: it plays a stun animation, wastes its entire
next turn, and drops out of hover. That is worth more than the damage reduction it removes, because
it pushes the escape one turn later — a Flutter break simultaneously **doubles the player's damage and
buys an extra attacking turn**, which is often the difference between recovering the card and not.

Net effect on the fight's shape: **multi-hit decks trivialize the hopper; single-big-swing decks pay
the ×0.5 for the whole back half of the clock.** This is the exact inverse of the Spiny Toad's Thorns
window, and the two sit in the same act pool.

## 5. Numbers

| Stat | Base | With Tough Enemies (A8) | With Deadly Enemies (A9) |
|---|---|---|---|
| HP (fixed, no roll — min = max) | 79 | 84 | — |
| Thievery damage | 17 | — | 19 |
| Hat Trick damage | 21 | — | 23 |
| Nab damage | 14 | — | 16 |
| Flutter applied | 5 | — | — |
| Escape countdown | 5 turns | — | — |

Incoming damage over the full clock, solo:

| Monster turn | Incoming | Cumulative |
|---|---|---|
| 1 Thievery | 17 | 17 |
| 2 Flutter | 0 | 17 |
| 3 Hat Trick | 21 | 38 |
| 4 Nab | 14 | 52 |
| 5 Escape | 0 | 52 |

**52 total at base, 58 on Deadly Enemies — and that is the maximum the fight can ever deal**, since it
leaves afterwards. Per-turn average is only ~13, i.e. the HP threat is low for Act 2.

**The real budget is offensive.** 79 HP must be removed inside four player turns, with turns 3 and 4
taxed at ×0.5 if Flutter is intact:

- Ignoring Flutter entirely: 79 HP over an effective 3 turns of output → the deck needs roughly
  **26 damage per turn**, every turn, from turn one.
- Breaking Flutter on turn 3 with five hit instances: full damage on all turns plus one extra turn
  from the stun → the requirement drops toward **16/turn**.
- Doing neither: the hopper simply leaves with the card and the player "wins" the room with nothing
  but 52 damage taken and a hole in their deck.

## 6. Scaling

**By act:** none. Act 2 exclusive, no act-conditional stats or behavior.

**By ascension:** two independent flat levers. Tough Enemies raises HP 79 → 84 (about +6%, which is
directly a ~6% higher DPS requirement inside the same four turns). Deadly Enemies raises the three
attack values 17/21/14 → 19/23/16 (52 → 58 total). **Neither level touches the Flutter amount, the
escape countdown, the steal priorities, or the move order** — ascension makes the card marginally
harder to recover, not the gimmick sharper.

**By seat count (multiplayer):**

| Players | HP (× players × 1.2) | Flutter stacks (× players × 1.2) | Attacks | Cards stolen |
|---|---|---|---|---|
| 1 | 79 (84 at A8) | 5 | full value | 1 |
| 2 | ~190 | 12 | full value **to each seat** | 2 |
| 3 | ~284 | 18 | full value **to each seat** | 3 |
| 4 | ~379 | 24 | full value **to each seat** | 4 |

Three things scale and one crucially does not:

- **HP** scales super-linearly (players × the Act 2 non-boss factor 1.2).
- **Flutter** is one of the powers flagged to scale in multiplayer, by the same factor — 5 → 12 → 18 →
  24 stacks. A four-seat table needs **24 separate connecting hit instances** to break the shield, so
  the break line that is routine solo is close to unreachable in co-op and the ×0.5 should be assumed
  live for the whole back half.
- **Card loss** scales one-per-seat: a four-player table loses four run-deck cards, recovered only by
  the same single kill.
- **The escape countdown does NOT scale.** It is a flat 5 turns at every table size.

That combination is the interesting co-op fact: the health bar quadruples, the shield roughly
quintuples in hit-count terms, the reward for killing it quadruples, and **the time allowed stays
identical**. Larger tables have more total damage per turn, but the burden is a coordinated same-turn
focus-fire race, not a survival problem — the per-seat incoming damage does not go down (attacks hit
all opponents at full value), it just stays a modest ~13/turn while the kill window gets much tighter
relative to the body.

## 7. Proposed fight class — `gimmick`

Per turn, this fight demands almost nothing defensively — 52 damage total, spread 17/0/21/14, from a
solo enemy with no debuffs, no status cards, and no scaling threat; a player who simply ignores it
takes chip damage and walks away. What it demands instead is a **binary offensive race against a fixed
five-turn timer for a non-HP stake**: hit a specific DPS bar (~26/turn solo) or land five separate hit
instances to break Flutter, inside four turns, or permanently lose a deck card the enemy chose out of
the player's best-value bucket. It is not `spike` (no turn's incoming number is threatening), not
`attrition` (the fight has a hard maximum duration and cannot grind), and not `swarm` (always exactly
one body). For Track B it should be modeled as a **near-zero defensive demand curve with a hard
offensive threshold and a hit-count sub-threshold**, and it is the roster's cleanest probe for whether
a deck can produce burst *and* whether it can produce many small instances — with the co-op note that
the hit-count answer is effectively removed at 3–4 seats while the timer is not.
