# Soul Fysh

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `SoulFysh` (`MonsterModel`)
- **Kind:** boss (sole monster of the `SoulFyshBoss` encounter)
- **Act:** Act 1 — Underdocks (act index 0, the non-default Act 1 branch; second in the act's boss discovery order, behind Waterfall Giant and ahead of Lagavulin Matriarch)
- **Fight class:** `gimmick`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. Shape of the fight

One monster, alone, on a custom background with its own boss track. No adds, no
summons, no second body, no phase transitions triggered by HP. What it has instead is a
**fixed five-turn ring** that never varies and never rolls dice, built out of three
distinct pressure types layered on the same clock:

1. a status-card generator that converts the player's *deck* into HP loss,
2. two ordinary attacks and one attack-plus-Vulnerable finisher,
3. one turn of near-invulnerability (Intangible) every lap.

The whole fight is a scheduling puzzle: the boss tells you exactly what is coming for
the next five turns, and the player's job is to line their damage window up against the
one turn the boss is *not* untouchable while paying down a deck that keeps getting worse.

## 2. Intent pattern / move cycle

The move state machine is a pure ring. Every move's follow-up is hard-wired to the next
move; no RNG, no conditionals, no HP thresholds, no branch on player state. Once the
first move resolves, the order is fully deterministic for the rest of the fight.

```
BECKON → DE GAS → GAZE → FADE → SCREAM → BECKON → ...
```

| # | Move | Intent icon(s) shown | Effect |
| --- | --- | --- | --- |
| 1 | Beckon | status (2) | Adds 2 Beckon status cards per player — one shuffled into a random position in the draw pile, one straight into the discard pile |
| 2 | De Gas | attack | Single heavy hit |
| 3 | Gaze | attack + status (1) | Hit, then 1 Beckon per player into the discard pile |
| 4 | Fade | buff | Goes intangible: applies Intangible 2 to itself, turns invisible (alternate hurt/death animations), deals no damage |
| 5 | Scream | attack + debuff | Drops invisibility, hits, then applies Vulnerable 3 to every player |

Two presentation notes that read as mechanics but are not: the invisible state only
swaps the animation set (there is no dodge, no miss chance, no targeting change — the
damage cap comes entirely from Intangible), and the fight drives two music parameters
(a fight-progress value that steps on Fade/Scream/death, and a flag that turns on
whenever the local player is holding a Beckon).

## 3. The Beckon status card

This is the fight's actual engine, and it lives in the player's deck rather than on the
enemy.

- Card type Status, cost 1, no target, cannot be upgraded, no play effect.
- **If it is still in hand at end of turn it deals 6 HP loss to its owner — unblockable,
  unaffected by powers, and flagged as move damage.** Block does nothing against it.
- Because it costs 1 and does nothing when played, the only ways to answer it are:
  pay 1 energy to dump it out of hand, discard/exhaust it with card effects, or eat 6.

Cards are dealt per-player and owned by that player, so they clog the individual deck
rather than a shared one.

Per full lap the boss manufactures **3 Beckons per player** (2 on Beckon, 1 on Gaze),
one of which is seeded into the draw pile at a random position and two of which enter
the discard pile — i.e. they arrive on a delay governed by the player's own shuffle
rate. A fast, thin deck sees them sooner and more often; a big deck delays them but
accumulates more of them. Left entirely unanswered, three Beckons drawn and held cost
18 unblockable HP per lap, on top of the attacks, and the count keeps growing because
nothing removes them.

## 4. Numbers

Base (Ascension 0, single player):

| Stat | Value |
| --- | --- |
| Initial HP | 211 (min == max — no roll) |
| De Gas damage | 16 |
| Gaze damage | 7 |
| Scream damage | 13 |
| Beckon status cards | 2 per player (1 draw pile at a random position, 1 discard pile) |
| Gaze status cards | 1 per player (discard pile) |
| Beckon card HP loss | 6, unblockable, at end of turn while in hand |
| Scream debuff | Vulnerable 3 |
| Fade buff | Intangible 2 (self) |

The boss has **no block, no self-heal, no Strength gain, and no scaling of its own**.
Its printed damage on lap 10 is identical to lap 1. All growth in the fight comes from
the accumulating Beckon pile and from Vulnerable amplification.

### Damage math per lap

Raw attack total per lap is 16 + 7 + 13 = **36**, spread across three of five turns
(two turns — Beckon and Fade — are zero-damage).

Vulnerable interacts with the ring in a specific, load-bearing way. Vulnerable is a
1.5× multiplier on incoming powered attacks and ticks down at the end of each enemy
turn. Scream applies 3 at the end of the lap, which ticks to 2 immediately, so it
covers the next Beckon turn (no attack — one stack wasted) and is still live for the
following **De Gas**. In practice the boss's biggest single hit lands amplified on
every lap after the first:

| Turn in lap | Move | Raw | With carried Vulnerable | Notes |
| --- | --- | --- | --- | --- |
| 1 | Beckon | 0 | 0 | +2 Beckon/player; Vulnerable burns a stack here |
| 2 | De Gas | 16 | **24** | the amplified hit |
| 3 | Gaze | 7 | 7 | Vulnerable has expired; +1 Beckon/player |
| 4 | Fade | 0 | 0 | Intangible 2 on itself |
| 5 | Scream | 13 | 13 | + Vulnerable 3 for next lap |

Steady-state incoming per lap: **44 attack damage plus up to 18 unblockable Beckon
damage**, against a 211 HP boss — i.e. the player needs roughly 42 damage per lap
(~11/turn across the four non-Intangible turns) to close it in 5 laps.

### The Intangible window

Intangible caps *all* damage taken at 1 and decrements at the end of each enemy turn.
Fade applies 2 during the enemy's turn 4, which ticks to 1 at that turn's end — so the
counter covers the whole of the player's turn 5 and expires as Scream resolves. Net
effect: **exactly one of the player's five turns is worth at most 1 damage**, every lap,
forever. A player who front-loads a big burst without tracking the ring loses 20% of
their offense to it; a player who tracks it loses nothing, because the window is fully
telegraphed by the buff intent one turn ahead.

This is also why block-heavy setups feel odd here: Fade turn and Beckon turn are
zero-attack turns, so half the lap's defensive spend is dead weight unless it converts
into card draw or discard.

## 5. Ascension scaling

Every ascension change is a flat alternate value, not a modifier:

| Ascension gate | What changes | 0 → gated |
| --- | --- | --- |
| Tough Enemies | Initial HP | 211 → 221 |
| Deadly Enemies | De Gas damage | 16 → 17 |
| Deadly Enemies | Scream damage | 13 → 15 |
| Deadly Enemies | Gaze damage | 7 → 8 |

Not scaled at any ascension: the number of Beckon cards per move (2 and 1), the Beckon
card's 6 HP loss, Vulnerable 3, and Intangible 2. Raw attack total per lap moves
36 → 40 (+11%), and the entire gimmick layer — the deck pollution, the untouchable turn,
the Vulnerable-on-De-Gas rhythm — is **identical at every ascension**. Ascension makes
this fight faster, not different.

## 6. Multiplayer / seat count

Four things happen in co-op, and only one of them is in the boss's own definition:

- **HP.** Boss HP is multiplied by seat count and by the act's multiplayer factor. Act
  index 0 uses **1.1**, so 211 → ~464 at 2 seats, ~696 at 3, ~928 at 4 (Tough Enemies
  scales the same way from 221).
- **Attacks hit every seat at full value.** Monster attacks default to targeting all
  opponents, and the list is refreshed between hits. De Gas, Gaze, and Scream each land
  on every player for the printed number; party damage is not divided.
- **Status cards are per-seat.** Beckon and Gaze walk the target list and create a fresh
  Beckon owned by each player (routing through pet owners where relevant), so every seat
  gets its own 3 cards per lap into its own piles. Party-wide unblockable pressure scales
  linearly with seats: 18/lap at 1 seat, 72/lap at 4.
- **Vulnerable 3 goes on everyone.** The Scream debuff is applied to the full target
  list, so the amplified De Gas next lap is amplified for every seat simultaneously.

The general multiplayer block multiplier is irrelevant here — the boss never gains block.
Net co-op read: HP roughly 2.2×/3.3×/4.4× while the per-seat demand is unchanged, so co-op
lengthens the fight in laps, which is exactly the axis that makes the Beckon pile
dangerous. Four seats means four decks, each accumulating 3 dead cards per lap, over more
laps than a solo run.

## 7. Proposed fight class: `gimmick`

Per turn, this fight demands *sequencing*, not raw output or sustained mitigation. The
boss's own numbers are modest and flat — 36 raw per 5 turns, no Strength, no block, no
heal — so it will never out-race a competent deck on damage alone; what it asks is that
the player read a fully deterministic five-beat ring and answer each beat with a
different resource: energy and card-filtering on the Beckon/Gaze turns, block on the two
attack turns, and *withheld* damage on the Fade turn where 1 is the cap. Getting any of
those out of order is the entire failure mode: burst into Intangible and you lose a fifth
of your damage; ignore the status cards and you take 18+ unblockable per lap that no
amount of block answers. It is not `attrition` (the boss does not grow and its damage per
turn is low), not `spike` (the top hit is a 24-point amplified De Gas that block trivially
covers when anticipated), and not `swarm` (single body). Track B should model it as a
low-but-nonzero baseline demand with two hard, *scheduled* spikes in demand type — a
deck-hygiene requirement that ratchets every lap and a once-per-lap turn where the
correct offensive demand is near zero.
