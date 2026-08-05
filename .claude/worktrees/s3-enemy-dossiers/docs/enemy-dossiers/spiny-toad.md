# Enemy Dossier — Spiny Toad

- **Class:** `SpinyToad`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `SpinyToadNormal` only. That encounter is a **single fixed monster** with no rolled
  slots and no allies — the toad is always alone, and it appears in no other encounter.
- **Fight class:** `gimmick`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A lone, fairly beefy Act 2 body that runs a **fixed three-beat loop**: it arms itself with retaliation
damage, spends that armament as a large single hit, then throws a smaller filler attack, and repeats.
Nothing about it is random — there is no branching, no conditional state, no RNG roll anywhere in its
move machine, and its intents are fully predictable from turn one for the entire fight.

Its whole design pressure lives in a one-turn **Thorns window** that opens on a schedule the player
can read in advance. The fight is not asking "can you survive the incoming numbers"; it is asking
"can you shape your damage output differently on one turn out of every three."

Cosmetically it has two full body states (spiked and "naked"), with separate idle/hurt/death
animations for each — the spiky look is an honest tell for whether the retaliation is currently live.

## 2. Intent pattern / AI

Three move states wired in a closed ring. No conditions, no randomness:

| Order | State | Intent shown | Effect |
|---|---|---|---|
| 1 | `PROTRUDING_SPIKES_MOVE` | Buff (no number) | Deals no damage. Goes spiky and gains **Thorns 5** on itself. |
| 2 | `SPIKE_EXPLOSION_MOVE` | Single attack (23) | Goes un-spiky, hits one target for **23**, then **removes 5 Thorns** from itself. |
| 3 | `TONGUE_LASH_MOVE` | Single attack (17) | Hits one target for **17**. |

Flow: the opening move is always **Protruding Spikes**. Spikes → Explosion → Lash → Spikes → … with
each state's follow-up hard-wired to the next. The loop never exits, never re-orders, and has no
low-HP, ally-death, or player-state behavior change.

Both attacks are ordinary single-target attacks; neither is AoE and neither multi-hits.

## 3. Gimmick — the Thorns window

`ThornsPower` here is a self-buff worth **5**, and it retaliates for its amount against the *dealer*
on **every incoming powered attack instance** — per instance, not per turn, and not per point of
damage. Attacks flagged unpowered (and the retaliation itself) do not re-trigger it, and non-attack
damage sources do not trigger it at all.

The schedule matters more than the number:

- Thorns goes **up at the end of the Spikes turn**, so it is live for exactly the **player turn that
  immediately follows Spikes**.
- Thorns comes **down during the Explosion move, after the 23 damage resolves**, so by the player's
  next turn it is gone.
- Net: **one player turn in every three is a retaliation turn**, and it is always the turn *before*
  the fight's biggest hit lands.

Consequences for how a turn must be played:

- On the retaliation turn, damage **shape** is taxed, not damage **quantity**. One 30-damage swing
  costs 5 HP; six 5-damage hits cost 30 HP and probably kill more of the player than the toad's own
  attacks do all fight. Shiv/multi-strike/scattershot decks eat their worst turn here on a clock.
- That same turn is also the turn the player needs to be banking Block for a 23-hit, so the cost is
  paid twice: attacking hurts, and not attacking gives the toad free time on a ~118 HP body.
- Skipping the retaliation turn entirely (all Block, no attack) is a legitimate and often correct
  line, which is unusual for a solo normal — the fight rewards *choosing not to attack*.
- Damage that is not a powered attack — poison/burn-style effects, orb/summon chip if it is flagged
  unpowered, non-attack sources — bypasses the window completely, so this enemy is a soft check on
  whether a build has any non-attack damage at all.

The Explosion's Thorns removal is a flat −5 tied to the move, i.e. the toad disarms itself as part of
spending the spikes; it never stacks Thorns across cycles and never exceeds 5.

## 4. Numbers

| Stat | Base | With Tough Enemies (A8) | With Deadly Enemies (A9) |
|---|---|---|---|
| HP (rolled range) | 116–119 | 121–124 | — |
| Thorns applied by Spikes | 5 | — | — |
| Spike Explosion damage | 23 | — | 25 |
| Tongue Lash damage | 17 | — | 19 |

Damage cadence per three-turn cycle, solo:

| Turn in cycle | Incoming | Cumulative |
|---|---|---|
| Spikes | 0 | 0 |
| Explosion | 23 | 23 |
| Lash | 17 | 40 |

**40 damage per 3 turns (~13.3/turn average) at base; 44 per cycle (~14.7/turn) on Deadly Enemies.**
The spread is the point — a 0 / 23 / 17 pattern on a fixed loop means Block is either wasted or
insufficient unless the player is reading the cycle, and the free turn is bought back by the
retaliation tax rather than by incoming damage.

Time-to-kill benchmark: at ~118 HP solo, a deck doing 25/turn kills in five turns and takes roughly
one and a half cycles (~63 damage before mitigation) plus two retaliation turns of Thorns.

## 5. Scaling

**By act:** none. Act 2 exclusive; no act-conditional stats or behavior.

**By ascension:** two flat levers off the shared ascension helper, and they are cleanly separated.
Tough Enemies moves only the HP roll (116–119 → 121–124, about +4%). Deadly Enemies moves only the two
attack numbers (23 → 25, 17 → 19, about +10% per cycle). **Neither level touches the Thorns amount,
the cycle order, or the cycle length**, so ascension makes this fight longer and harder-hitting
without making the gimmick itself any sharper — the retaliation tax is a constant 5 at every
ascension.

**By seat count (multiplayer):**

| Players | HP (× players × 1.2) | Thorns | Explosion | Lash |
|---|---|---|---|---|
| 1 | 116–119 | 5 | 23, one target | 17, one target |
| 2 | ~278–286 | 5 | 23, one target | 17, one target |
| 3 | ~418–428 | 5 | 23, one target | 17, one target |
| 4 | ~557–571 | 5 | 23, one target | 17, one target |

Only HP scales, and it scales super-linearly (player count × the Act 2 non-boss factor of 1.2). The
Thorns value, both attack values, and the three-turn cadence are all untouched, and both attacks stay
**single-target** — so per-seat incoming pressure is divided by the table size while the health bar
multiplies. In co-op this collapses into a long, low-threat slog where the *only* live mechanic is the
retaliation window, and that window gets strictly worse: four seats attacking into a live Thorns 5
pay four times as many instances against a body that now takes four-plus times as long to kill, i.e.
the number of retaliation turns the party must sit through roughly triples from solo. Expect co-op
tables to converge on "everyone holds their multi-hit turn" every third turn, which is the same
decision solo makes but repeated far more often.

## 6. Proposed fight class — `gimmick`

The per-turn demand is not about surviving quantity — 40 damage per three turns from a solo Act 2
normal is unremarkable, and there is no swarm, no scaling clock, and no attrition wall (no Block, no
Plating, no heal, no regeneration). What the fight demands is that the player **change the shape of a
turn on a fixed schedule**: on one turn in three, small-hit damage is actively self-harming and the
correct play may be to hold or to switch to non-attack damage, while the other two turns are plain
Block-and-swing. That single mechanic, plus perfectly deterministic intents that make it fully
telegraphed, is the entire fight — remove Thorns and this is a stat block with no decisions in it. For
Track B it should be modeled as a **flat-baseline demand curve with a periodic constraint spike on
damage-delivery shape**, and it is the roster's cleanest probe for whether a deck can either front-load
its damage into a few large instances or bring any non-attack source at all.
