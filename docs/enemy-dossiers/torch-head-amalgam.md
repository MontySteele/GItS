# Torch Head Amalgam

- **Class:** `TorchHeadAmalgam`
- **Kind:** boss (boss-tier creature; mechanically a *secondary* enemy)
- **Act:** 3 (Glory, act index 2)
- **Encounter:** `QueenBoss` — always paired with `Queen`, boss room, custom BGM `act3_boss_queen`
- **Fight class:** **mixed**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

The Amalgam never spawns alone and never spawns anywhere else. The `QueenBoss` encounter always
generates exactly two creatures into two named slots: the Amalgam in the `amalgam` slot and the Queen
in the `queen` slot, in that order. Slot order matters for modelling — the Amalgam is generated
first and therefore takes its turn ahead of the Queen every round, so any buff the Queen hands it
lands on the *following* round, not the current one. The Queen's own asset list pulls in the
Amalgam's assets, and the Queen caches a reference to the Amalgam on room entry, so the two models
are hard-wired together.

The camera for this encounter is pulled back (0.9× scale, offset down) to fit both bodies.

## The one thing to know first: it is a minion

On room entry the Amalgam applies **Minion** to itself. That single power changes its role
completely:

- It is a **secondary enemy**. A secondary enemy cannot hold the combat open on its own — if the
  Queen dies first, the Amalgam is removed regardless of its remaining HP.
- Killing the Amalgam **does not end the fight** and does not trigger the Queen's fatal path. The
  Minion power is explicitly configured so that its owner's death is not fatal to the encounter and
  so the power is not stripped on owner death.
- Its death is a **phase trigger** for the Queen (see Gimmicks). This is the whole strategic content
  of the creature: its HP bar is a lever, not a win condition.

## Intent pattern

Fully deterministic, no RNG, no HP thresholds, no conditional branching anywhere in its move machine
— every state hard-points at exactly one successor. There is a three-move opening that never
repeats, and then a permanent three-beat loop.

| Beat | Move | Effect | Intent shown |
|---|---|---|---|
| 1 (opening only) | **Tackle** | single AoE attack, heavy | attack |
| 2 (opening only) | **Tackle (2)** | same attack again | attack |
| 3 | **Soul Beam** | AoE attack, 3 hits, one animation | multi-attack (×3) |
| 4 | **Weak Tackle** | single AoE attack, reduced | attack |
| 5 | **Weak Tackle (2)** | same reduced attack | attack |
| → | back to **Soul Beam** | — | — |

So the lifetime sequence is: heavy, heavy, beam, light, light, beam, light, light, beam, … The two
opening heavy tackles are the only time those numbers are ever seen; from turn 4 onward the loop is
permanently **light / light / beam**. The state machine is barred from transitioning before the
first move resolves, so turn 1 is always the first Tackle.

Two structural notes for modelling:

- **Every attack is AoE.** All three moves are built as monster attacks against all opponents, so in
  co-op each seat eats the full listed number with no split and no target selection. The Tackle
  intents render as single-target icons; that is cosmetic.
- **The rotation is knowable from turn 1** and the creature has no reactive behavior of any kind. It
  never blocks, never buffs itself, never debuffs, and never responds to being hit. All of its
  variance comes from *outside* — from the Queen.

## Damage / block numbers

Base values, and the A9 (`DeadlyEnemies`) variants where they differ:

| Stat | Base | A9+ |
|---|---|---|
| HP (min = max, no roll) | **199** | **211** (A8 `ToughEnemies`) |
| Tackle damage (opening beats 1–2) | 18 | 19 |
| Weak Tackle damage (loop) | 14 | 15 |
| Soul Beam damage per hit | 8 | 8 (**unchanged**) |
| Soul Beam hit count | 3 | 3 |
| Block gained, ever | **0** | 0 |

The Amalgam has no block, no thorns, no artifact, no self-heal, and no damage mitigation. It is a
pure output body with an armour-family take-damage sound. At 199 HP against an Act 3 deck it is
killable in one or two good turns — which is the point, because killing it is a *decision*, not a
formality.

Soul Beam is the only number ascension leaves alone, which quietly makes the beam a *smaller* share
of the fight at A9 in raw terms — but see the Strength ramp below, which reverses that completely.

### The Strength ramp (this is the real damage curve)

The Amalgam gains no Strength on its own. The Queen's **Burn Bright For Me** grants +1 Strength to
every teammate (i.e. the Amalgam) and 20 block to herself, and — critically — the Queen's move
machine **loops that move against itself for as long as the Amalgam is alive**. Her cycle is:
turn 1 a card-binding debuff, turn 2 a permanent triple-debuff, then Burn Bright For Me on turn 3
and *every turn thereafter* while the Amalgam lives. She deals no damage at all during that loop.

Consequences:

- The Amalgam accrues **+1 Strength per turn, forever, starting from its turn 4** (the Queen acts
  after it, so her turn-3 cast lands for the Amalgam's turn 4).
- **Strength applies per hit.** Soul Beam therefore grows three times as fast as the tackles. The
  beam starts as the smallest hit in the rotation and becomes the largest by a wide margin.
- The Queen's own +1-per-turn feed is uncapped. There is no soft cap other than the Amalgam's HP.

Base-difficulty raw damage curve, no player interference, before the Vulnerable multiplier:

| Turn | Move | Str | Raw damage to each player |
|---|---|---|---|
| 1 | Tackle | 0 | 18 |
| 2 | Tackle | 0 | 18 |
| 3 | Soul Beam | 0 | 8 ×3 = 24 |
| 4 | Weak Tackle | 1 | 15 |
| 5 | Weak Tackle | 2 | 16 |
| 6 | Soul Beam | 3 | 11 ×3 = 33 |
| 7 | Weak Tackle | 4 | 18 |
| 8 | Weak Tackle | 5 | 19 |
| 9 | Soul Beam | 6 | 14 ×3 = 42 |
| 10 | Weak Tackle | 7 | 21 |
| 11 | Weak Tackle | 8 | 22 |
| 12 | Soul Beam | 9 | 17 ×3 = 51 |
| 15 | Soul Beam | 12 | 20 ×3 = 60 |

Per-three-turn-cycle raw incoming runs 60 → 64 → 79 → 94 → 109 …, i.e. **linear, +15 per cycle**,
with the beam beat carrying an increasing share (40% of the cycle at turn 6, 54% at turn 15). Every
one of these numbers is then multiplied by the Vulnerable the Queen applies on turn 2 and never
removes — so the effective curve a player experiences is roughly 1.5× the table above from turn 3
onward, while their own block is simultaneously suppressed by permanent Frail.

## Gimmicks

### It is the Queen's phase gate

The Amalgam's death flips a flag on the Queen that permanently reroutes her move machine. While the
Amalgam is alive, the Queen loops Burn Bright For Me (buff the Amalgam, gain 20 block, deal nothing).
Once the Amalgam dies she abandons that loop and switches to her damage cycle: a 5-hit multi-attack,
a single heavy hit, then a self-Strength enrage, repeating. If the Amalgam dies on a turn when the
Queen has already telegraphed Burn Bright For Me, that telegraphed intent is **immediately
overwritten** with the enrage — the intent the player is looking at changes out from under them.

This produces the fight's central decision, and it is a genuine trade rather than a puzzle with one
answer:

- **Kill it early:** you stop the Strength ramp at a low value and stop the Queen adding 20 block per
  turn — but you turn on the Queen's damage phase immediately and she has ~400 HP left to chew
  through while attacking.
- **Leave it alive:** the Queen deals literally zero damage, but the Amalgam's output climbs +1 (or
  +3 on beam turns) every single round and you are fighting through 20 block per turn on the body
  that actually matters.

There is no third option where both are quiet. Damage racing the Queen while ignoring the Amalgam is
the highest-risk line and the one the escalation curve is tuned to punish.

### Multi-hit shape

Soul Beam is one animation resolving three separate hits, aimed by repositioning a laser bone toward
the first target. For modelling purposes the shape matters more than the total: three instances
interact with per-hit mitigation, block-per-instance, thorns, and on-hit triggers completely
differently from one 24-point hit, and as Strength climbs the beam becomes the fight's single largest
turn while remaining maximally punishing to flat per-hit reduction.

### Torch lights and Doom

The Amalgam has a dedicated response to dying by **Doom** specifically, which extinguishes its three
green torch flames. This is purely cosmetic cleanup (the normal death path handles the visuals
otherwise) but it confirms Doom-style instant-kill effects are a supported way to remove it — worth
noting because Doom bypasses the HP race entirely and hands the player precise control over *when*
the Queen's phase flips.

### Inherited context the Amalgam's numbers live inside

Not the Amalgam's own mechanics, but every number above is experienced through them:

- **Chains of Binding (Queen turn 1)**: 3 stacks. Drawn cards get Bound; only one Bound card may be
  played per turn, and the affliction clears at end of turn.
- **You're Mine (Queen turn 2)**: 99 stacks each of **Frail**, **Weak**, and **Vulnerable** on every
  player. These are effectively permanent. Vulnerable inflates every Amalgam hit, Frail suppresses
  the block used to answer them, and Weak slows the player's clock on both bodies at once.

## Scaling

**By act:** none. The Amalgam exists only in the Act 3 boss encounter; nothing on the model reads
the act index except through the shared multiplayer HP formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | HP 199 → 211 |
| A9 `DeadlyEnemies` | Tackle 18 → 19; Weak Tackle 14 → 15; Soul Beam **unchanged** at 8 per hit; the Queen's Strength grant is **unchanged** at +1 |

Ascension is unusually gentle on this creature: +1 per tackle, nothing on the beam, and no change to
the ramp rate. The A9 pressure in this fight arrives through the Queen's numbers instead (her heavy
hit and her 5-hit flurry both scale), so the Amalgam's relative share of incoming damage *falls*
slightly at high ascension while its role as the phase gate is untouched.

**By seat count (multiplayer):**

HP goes through the standard scale: base × players × 1.3 (the Act 3 *boss-room* multiplier — boss
rooms get 1.3 where ordinary Act 3 rooms get 1.2).

| Players | HP (base) | HP (A8+) |
|---|---|---|
| 1 | 199 | 211 |
| 2 | ≈517 | ≈549 |
| 3 | ≈776 | ≈823 |
| 4 | ≈1035 | ≈1097 |

- **Damage does not scale, but all three moves are AoE**, so party-wide damage taken scales linearly
  with seats on top of the HP scale. A 4-player party at turn 12 is absorbing ~204 raw points from
  the beam alone across the team, before Vulnerable.
- **The Amalgam gains no block**, so the enemy-block multiplayer multiplier never touches it — but it
  does touch the Queen's 20-per-turn Burn Bright block, which is the block the party has to punch
  through if it wants the Amalgam left alive. That asymmetry makes "leave it alive" markedly worse in
  co-op than solo.
- **The Strength ramp is per-turn, not per-player**, so it does not accelerate with seats — but since
  every seat eats the full ramped number, the party-wide cost of a slow kill grows linearly.
- **Nothing about the Minion / secondary-enemy relationship changes with seat count**; the phase gate
  is a single global flag.

## Proposed fight class: **mixed**

Turn to turn, the Amalgam demands three different things and none of them dominates: the opening two
tackles are a flat block check before any player engine is online, the beam beat is a multi-hit check
where per-instance mitigation and block behave nothing like they do against the tackles, and the
whole rotation sits on top of a linear Strength ramp that turns an ignorable 24-point beam into a
60-point one — an attrition curve with a real clock. Layered over that is an outright gimmick axis
that has nothing to do with damage at all: this creature's HP bar is a switch that reroutes the
Queen's entire move machine, so every turn the player is also answering "do I want the other boss
turned on yet?", and the answer changes as the ramp climbs. It is not pure attrition, because the
optimal line is a timed kill rather than a survival grind; it is not spike, because no single turn is
built to be lethal in isolation and the two biggest hits are telegraphed a full cycle out; it is not
gimmick alone, because the escalation is a real damage race that punishes indecision on its own
terms. For Track B, model it as an attrition base (linear +15 per three-turn cycle, beam-weighted,
all multiplied by permanent Vulnerable) with a discrete branch decision whose payoff inverts over
time — early kill trades ramp for the Queen's damage phase, late kill trades the reverse.
