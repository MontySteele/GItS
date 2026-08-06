# Enemy Dossier — The Forgotten

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `TheForgotten`
- **Kind:** normal
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounters:** `TheLostAndForgottenNormal` — always a fixed pair, one `TheLost` + one `TheForgotten`. It never appears alone and never appears with anything else.
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A stone-bodied Act 3 ghost with a fixed 106 HP and exactly two moves that strictly alternate. It has
no randomness of any kind — not in HP (min and max initial HP are the same value), not in move
selection. What it has instead is a **theft engine**: every other turn it strips **Dexterity** from
the whole player side and moves that Dexterity onto itself, where it does double duty — it raises the
enemy's own Block *and* its own attack damage.

Its partner `TheLost` runs the identical machine one stat over, stealing **Strength**. Between them
the encounter drains the player's offense and defense in parallel while both bodies grow. That pairing
is the design; the two units should be read as one fight.

Both units carry a "Possess" bookkeeping buff (applied on entering the room, amount 1) whose only job
is to remember how much it stole from whom and **hand it all back when that unit dies**.

## 2. Intent pattern / AI

Two move states wired as a hard two-cycle. Each state's follow-up is the other state, so there is no
branch, no dice, and no anti-repeat logic to reason about. It **always opens on Miasma**.

| Turn | State | Intent shown | Effect |
|---|---|---|---|
| 1, 3, 5, … | `MIASMA` | debuff **+** defend **+** buff (three icons) | −2 Dexterity to **all** players, then gain 8 Block, then +2 Dexterity to itself |
| 2, 4, 6, … | `DREAD` | single attack | One hit for 13 + its own current Dexterity |

The three-icon Miasma intent is honest: it really does all three things, in that order. The ordering
matters — the Block is gained **before** the self-Dexterity tick, so the Block from a given Miasma
reflects only the Dexterity banked on *previous* Miasmas.

The intent damage number for Dread is computed live from current Dexterity, so the growing attack is
always visible one turn ahead.

## 3. Gimmicks

**Dexterity theft, transferred not destroyed.** Miasma applies −2 Dexterity to every player creature
and +2 Dexterity to itself. This is the whole fight compressed into one line, because Dexterity is
load-bearing on *both* sides of the board:

- On the player, negative Dexterity is a flat subtraction from every Block gain. Two Miasmas in and
  each Block card is worth 4 less; three in, 6 less. A defensive deck degrades faster than a
  damage deck does, and the degradation is permanent for the combat.
- On The Forgotten, Dexterity adds to the Block it gains from its own move — so **Miasma's Block
  compounds with itself**, 8 → 10 → 12 → 14 as the fight runs.
- Unusually, its **attack also scales off Dexterity, not Strength**. Dread's damage is base + its own
  Dexterity, so every Miasma is simultaneously a debuff, a defend, and a +2 damage buff to the move
  that follows it. There is no separate Strength engine to disable, and Strength-removal effects miss.

**Death refunds the theft.** The Possess buff tracks the cumulative negative Dexterity it inflicted on
each player and, on the owner's death (unless removal was prevented), restores exactly that amount to
each of them. This creates the encounter's real decision: the debt is only cancelled by *killing that
specific body*. Dispel/cleanse on the player side removes the debuff but does not stop the enemy
keeping its own stolen stacks, and it does not stop the next Miasma re-applying.

**Target-priority puzzle with The Lost.** The Lost steals Strength (2 per cast, same alternating
shape) and attacks twice for 4; its damage grows with the Strength it took. The Forgotten steals
Dexterity and attacks once for 13; its damage and its Block grow with the Dexterity it took. Killing
one refunds only that one's stat. So the party must decide early which half of its game plan it can
least afford to lose — and the answer is build-dependent, which is why the fight reads differently to
different characters:

- Block-based/defensive decks bleed to The Forgotten (their Block shrinks while its Block grows,
  extending the fight, which grants more Miasmas — a genuine feedback loop).
- Damage/attack decks bleed to The Lost.
- The Forgotten is the harder body to kill of the two (more HP, and it is the one gaining Block), so
  "kill the one hurting you" and "kill the one that dies fastest" point in different directions.

**Anti-synergy note for Track B:** the loop is self-reinforcing only through the Block half. Every
turn the party fails to close, Miasma fires again and adds +2 to Dread, +2 to Miasma's Block, and −2
to the party's Block. There is no cap and no reset.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP | 106 (fixed, no roll) | 111 | — |
| Dread (single attack) | 13 + own Dexterity | — | 15 + own Dexterity |
| Miasma Dexterity steal | 2 from each player | — | 2 (**unchanged**) |
| Miasma self-Dexterity gain | +2 | — | +2 (unchanged) |
| Miasma Block | 8 + own Dexterity | — | — |
| Possess buff amount | 1 (bookkeeping only) | — | — |

Derived escalation, single player, nothing interfering:

| Enemy turn | Move | Enemy Dex after | Block gained | Dread damage |
|---|---|---|---|---|
| 1 | Miasma | 2 | 8 | — |
| 2 | Dread | 2 | — | 15 |
| 3 | Miasma | 4 | 10 | — |
| 4 | Dread | 4 | — | 17 |
| 5 | Miasma | 6 | 12 | — |
| 6 | Dread | 6 | — | 19 |
| 7 | Miasma | 8 | 14 | — |
| 8 | Dread | 8 | — | 21 |

Player Dexterity over the same window: −2, −2, −4, −4, −6, −6, −8, −8. Note the effective damage
swing is worse than the Dread column alone suggests: on turn 5 the player is taking 19 while every
Block card is 6 weaker than printed.

- HP is fixed, so encounter-to-encounter variance is zero — a good property for calibration work.
- The Dexterity steal has **no** ascension variant. Deadly Enemies raises the flat attack base only;
  it does not accelerate the engine.
- Companion for reference (`TheLost`): 93 HP / 99 with Tough Enemies; steals 2 Strength from all
  players and gives itself 2; attacks 4 × 2 hits, 5 × 2 with Deadly Enemies; also refunds on death.

## 5. Scaling

**By act:** none internal. Act 3 only, no act-conditional stats. Its relevance to act is entirely
contextual: by Act 3 most decks have a scaling engine (Strength/Dexterity/Block multipliers) worth
attacking, which is what makes a flat −2/−2 theft pair actually bite.

**By ascension:** two flat levers and neither touches the gimmick. *Tough Enemies* raises HP 106 → 111,
which is worse than the 5 points suggest — a longer fight is measured in *extra Miasmas*, and each
extra Miasma is +2 enemy Block, +2 Dread, −2 player Dexterity. *Deadly Enemies* raises Dread 13 → 15;
the steal amount stays at 2 on both units.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, the Act 3 non-boss factor being
  **1.2**.

| Players | Effective HP (base 106) |
|---|---|
| 1 | 106 (no scaling at 1 player) |
| 2 | ~254 |
| 3 | ~382 |
| 4 | ~509 |

- *Block is also seat-scaled*, by the same player-count × 1.2 multiplier applied to monster move Block,
  on top of the additive Dexterity bonus. So the 8/10/12/14 ladder becomes roughly a 19/24/29/34 ladder
  at two seats and a 38/48/58/67 ladder at four — the fight's defensive half grows *faster* than the
  HP bar does.
- *The Dexterity theft is per-seat on the debit side and flat on the credit side.* Miasma applies −2
  to **every** player creature, but only ever gives itself +2 regardless of table size. At four seats
  the encounter strips 8 Dexterity-points of value per cast while the enemy banks 2. The debuff is the
  part that scales with seats; the enemy's own ramp is not.
- *Dread stays a single attack*, so incoming damage per seat drops with table size while the Block
  wall and the debuff pressure both rise. Co-op therefore shifts this fight decisively from "survive
  the damage" toward "out-race a growing Block wall while your defenses rot" — the least spiky, most
  grind-shaped version of the encounter.
- Death refunds are per-player and complete, so in co-op a kill un-rots the whole table at once. That
  makes focus-firing one body strictly better than spreading damage across two, and the seat-scaled
  Block makes spreading damage worse still.

## 6. Proposed fight class — `attrition`

Per turn, this fight never asks the player to survive a burst — the incoming number tops out around
19–21 in a solo Act 3 context and is telegraphed a full turn ahead — it asks them to **keep producing
throughput while their own defensive numbers decay and the enemy's grow**. Every turn not spent
closing costs compounding value in three directions at once (enemy Block +2, enemy damage +2, player
Block −2), with no cap, no reset, and no threshold to hit; that is the definition of a grind curve
rather than a spike or denial curve. It is not `swarm` (two bodies, both slow and neither summoning),
and it is not `gimmick` in the Fossil-Stalker sense because there is no binary the player can re-solve
each turn to switch the engine off — the theft fires unconditionally whether or not they block. The
only reason to hesitate over `mixed` is the genuine kill-order puzzle the Lost/Forgotten pairing
creates; for Track B that should be modeled as a one-time targeting decision layered on top of an
otherwise straight sustained-damage-over-N-turns demand curve, where N grows with seat count.
