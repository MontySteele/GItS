# Scroll of Biting

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `ScrollOfBiting`
- **Kind:** normal
- **Act:** 3 (Glory, act index 2)
- **Encounters:** `ScrollsOfBitingWeak` (3 copies, weak/early-act pool), `ScrollsOfBitingNormal` (4 copies) — both tagged `Scrolls`, both monster-room
- **Fight class:** **swarm**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

Scroll of Biting never appears alone. It is spawned only by the two Scrolls encounters in Act 3, one
of which is flagged as a *weak* encounter (Act 3 runs two weak encounters before the pool opens up),
so the same monster shows up first as a three-body fight and later as a four-body fight. There is no
mixed-species encounter containing it in the tree — every fight it is in is entirely Scrolls of
Biting.

Each spawned scroll rolls one of two visual skins at random, and each gets a **unique** max-HP value
within its band (the encounter deliberately avoids handing two scrolls the same HP), so an AoE plan
almost never gets a clean simultaneous clear.

## Intent pattern

Three moves and one random branch, wired as a short loop:

| Move | Effect | Intent shown |
|---|---|---|
| **Chomp** | single big attack | attack |
| **Chew** | attack, 2 hits | multi-attack (×2) |
| **More Teeth** | self-buff: +2 Strength | buff |

The wiring, in plain language:

- **Chomp always leads into More Teeth.** No exceptions, no roll.
- **More Teeth always leads into Chew.** No exceptions, no roll.
- **Chew leads into a coin flip** between Chomp and Chew, at equal weight.
  - Chomp is barred from repeating back-to-back (it can never immediately follow itself — it never
    can anyway, since Chomp's follow-up is hard-wired).
  - Chew is capped at **two consecutive uses**; after a second Chew in a row, the branch is forced to
    Chomp.

So the fight is a 3-beat cycle — **Chomp → More Teeth → Chew** — with a 50% chance of one extra Chew
inserted before the cycle restarts, and a hard stop at two Chews. The realized period is 3 or 4
turns, average 3.5. **Every full cycle grants +2 Strength**, permanently, per scroll.

### Staggering (the important structural detail)

Each scroll is assigned a starter index and enters the loop at a *different* beat:

- **Weak encounter (3 scrolls):** the three starters are a rotation of {Chomp, Chew, More Teeth} —
  the trio is always exactly out of phase. Turn 1 is therefore *always* one Chomp, one Chew, one
  buff, regardless of seed. Only the assignment of which body does what is random.
- **Normal encounter (4 scrolls):** the first three are the same rotation; the **fourth always starts
  on More Teeth**. Turn 1 is one Chomp, one Chew, and two buffs.

Because the cycles branch independently after the first Chew, the phases drift apart over the fight
and the incoming-damage-per-turn curve becomes lumpy rather than flat — some turns are two Chomps,
some are all buffs.

## Damage / HP numbers

| Stat | Base | Ascension variant |
|---|---|---|
| HP (per scroll, rolled in band, unique per body) | **30–37** | **33–39** at A8 `ToughEnemies` |
| Chomp damage | **14** | **16** at A9 `DeadlyEnemies` |
| Chew damage per hit | **5** | **6** at A9 |
| Chew hit count | 2 | 2 (unchanged) |
| More Teeth — Strength gained | 2 | 2 (unchanged) |
| Paper Cuts on entry | 2 | 2 (unchanged) |

No move in the kit grants block, and no move debuffs the player. There is no defensive beat at all —
the scrolls do not protect themselves, so every point of player output lands.

### Per-scroll damage with Strength

Strength applies **per hit**, so Chew scales twice as fast as Chomp:

| Cycles completed | Strength | Chomp | Chew total | A9 Chomp | A9 Chew total |
|---|---|---|---|---|---|
| 0 | 0 | 14 | 10 | 16 | 12 |
| 1 | 2 | 16 | 14 | 18 | 16 |
| 2 | 4 | 18 | 18 | 20 | 20 |
| 3 | 6 | 20 | 22 | 22 | 24 |
| 4 | 8 | 22 | 26 | 24 | 28 |

Chew overtakes Chomp at +4 Strength (two completed cycles, roughly turn 7–8) and keeps pulling ahead.
A body left alive past turn ~10 is doing double its printed output.

### Encounter-level incoming damage (solo, base difficulty)

Turn 1 is fixed by the stagger: **24** in the weak fight (14 + 10 + a buff) and **24** in the normal
fight (14 + 10 + two buffs). From turn 2 the phases diverge; a rough expectation per scroll per turn
is (Chomp + Chew) ÷ 3.5 beats ≈ 6.9 at zero Strength, so an untouched trio averages ~21/turn early
and an untouched quartet ~28/turn, both climbing by roughly +4 per scroll per completed cycle.

Total HP to chew through: **90–111** (weak, ~99–117 at A8) and **120–148** (normal, ~132–156 at A8).

## Gimmicks

### Paper Cuts (the whole identity of the fight)

Every scroll applies **Paper Cuts 2 to itself** the moment it enters the room — before turn 1, on
every body, in every encounter. It is a counter-type buff on the monster, and it reads:

> whenever this monster's attack deals **unblocked** damage to a player, that player loses **2 max
> HP**.

The details that matter for modelling:

- **It triggers per damage instance, not per turn and not per point.** One unblocked point of a Chomp
  costs the same 2 max HP as a fully unblocked 22-damage Chomp. Chew, being two hits, triggers
  **twice** — a fully unblocked Chew is 4 max HP.
- **It is fully preventable by block.** The trigger requires unblocked damage above zero, so a hit
  that is completely absorbed costs nothing. Partial block does *not* reduce the cost.
- **It is permanent.** Max HP loss persists for the rest of the run; this is the only lasting cost of
  an otherwise ordinary normal fight, and it is why the fight punishes slow, chip-tanking play far
  out of proportion to its damage numbers.
- The amount does not grow on its own — nothing in the kit stacks it past 2 — so the per-instance
  price is flat all fight. What grows is the *number of instances you fail to block*, because
  Strength growth makes each hit harder to fully absorb.

Worst-case turn-1 exposure with nothing blocked: **6 max HP** in the weak fight (one Chomp = 2, one
Chew = 4) and the same 6 in the normal fight. A four-scroll fight that runs long, with two scrolls
both on Chew beats, can hit 8 max HP in a single turn.

The design consequence: the player's block is being asked to be *exact per incoming instance*, not
merely large. A turn with 20 block against 14 + 10 loses only the Chew instances if block is spent in
the right order; a turn with 20 block spread badly loses everything. This is the one place the fight
rewards precision over totals.

### Independent Strength, not shared

Each scroll ramps its own Strength on its own cycle. There is no shared buff and no leader body, so
there is no priority target from a buff standpoint — but killing any body removes its entire future
ramp, which makes focused elimination strictly better than spread chip damage.

## Scaling

**By act:** none. Scroll of Biting exists only in Act 3 and reads no act index except through the
shared multiplayer HP formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | HP band 30–37 → 33–39 per body |
| A9 `DeadlyEnemies` | Chomp 14 → 16; Chew 5 → 6 per hit (10 → 12 per use) |

Paper Cuts, the Strength grant, the hit count and the move wiring are all untouched by ascension. The
A9 change is quietly nastier than the numbers look because raising Chew's per-hit damage raises the
bar for *fully* absorbing each of its two instances, which is what the max-HP tax keys off.

**By seat count (multiplayer):**

- **Both attacks are AoE.** They are built as monster attacks against all opponents, so in co-op
  every seat takes the full listed Chomp and the full 2-hit Chew from *every* scroll. Nothing is
  split. The Chomp intent renders as a single-target icon; that is cosmetic.
- **Paper Cuts therefore fires per seat.** Each player who takes unblocked damage from a given attack
  loses 2 max HP from it, so a 4-scroll fight can bleed max HP from the whole party simultaneously.
  This is the sharpest co-op scaling in the fight and it is not visible in any displayed number.
- **Body count does not scale with seats** — the encounters spawn a fixed 3 or 4 scrolls regardless
  of party size.
- **HP scales** by the standard formula: base × players × 1.2 (Act 3 non-boss multiplier).

| Players | HP per scroll (base band) | Weak-encounter total | Normal-encounter total |
|---|---|---|---|
| 1 | 30–37 | 90–111 | 120–148 |
| 2 | 72–89 | ~216–266 | ~288–355 |
| 3 | 108–133 | ~324–400 | ~432–533 |
| 4 | 144–178 | ~432–533 | ~576–710 |

Net effect: co-op multiplies the bodies' durability *and* multiplies the party-wide max-HP bleed,
while the number of targets a party must clear stays flat. Of the two, the max-HP bleed is the one
that carries out of the room.

## Proposed fight class: **swarm**

What this fight demands, every single turn, is **body removal against a clock** — three or four
identical low-HP attackers, deliberately staggered so at least one is always mid-swing, each
independently accruing +2 Strength per cycle, none of them ever defending. The dominant per-turn
question is "how many of these can I delete this turn", because a scroll killed is a whole future
ramp and a whole future stream of max-HP triggers deleted with it, and the unique-HP roll means AoE
rarely clears the row cleanly enough to skip the follow-up. Paper Cuts does not make this a gimmick
fight; it is a multiplier *on* the swarm demand, converting every hit the party fails to fully absorb
into permanent run damage and thereby turning "kill them a turn earlier" from a comfort into the
scoring function. For Track B, model it as a swarm with an unusually steep unblocked-instance
penalty: demand per turn is roughly (bodies alive × per-body output, ramping) for the block/kill
axis, plus a discrete 2-max-HP term per unblocked damage *instance* per seat — which means hit count,
not damage total, is the load-bearing input on the penalty side.
