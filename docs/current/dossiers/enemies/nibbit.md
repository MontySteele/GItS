# Nibbit — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Nibbit`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounters:** `NibbitsNormal` — **two** Nibbits in named `front` / `back` slots, the front one flagged at spawn. `NibbitsWeak` — **one** Nibbit, flagged "alone", tagged as a Nibbit-family weak room.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Three moves and no randomness anywhere. Every Nibbit runs the same fixed three-beat loop; the only thing that differs between bodies is **which beat it starts on**.

1. **Butt** — single-attack intent. One big hit, nothing else.
2. **Slice** — single-attack intent **plus** a defend intent on the same turn. One medium hit, then the Nibbit gains Block for itself.
3. **Hiss** — buff intent. Applies Strength to **itself only** (permanent, no decay, does not touch its sibling).

Wiring is a pure cycle: **Butt → Slice → Hiss → Butt → …**, forever. There is no branch after the first turn, no HP threshold, no enrage, no summon, no player debuff, and no roll of any kind — a Nibbit's entire remaining fight is knowable from its current intent.

The one branch in the machine is the entry point, evaluated once to choose the opening beat:

| Body | Opens on | Turn 1 | Turn 2 | Turn 3 | Turn 4 | … |
| --- | --- | --- | --- | --- | --- | --- |
| **Front** (paired room) | Slice | Slice | Hiss | Butt | Slice | cycles |
| **Back** (paired room) | Hiss | Hiss | Butt | Slice | Hiss | cycles |
| **Alone** (weak room) | Butt | Butt | Slice | Hiss | Butt | cycles |

So in the paired encounter the two bodies are **phase-offset by one beat and never sync up**: exactly one of them is buffing on any given turn, and exactly one is landing the big Butt on any turn after the first. The player therefore faces a repeating three-turn rhythm of light / medium / heavy incoming, with the heavy beat growing every cycle as Strength accumulates.

**Slice is deliberately hidden from the bestiary.** The bestiary entry advertises only Butt and Hiss — a player consulting it sees a big attack and a buff and will not be told that the third beat also gives the enemy Block, so the fight reads as shorter than it is.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll (per body) | 42–46 | 44–48 (*Tough Enemies* tier) |
| Butt damage | 12 | 13 (*Deadly Enemies* tier) |
| Slice damage | 6 | 7 (*Deadly Enemies* tier) |
| Slice Block (self) | 5 | 6 (*Tough Enemies* tier) |
| Hiss Strength (self) | +2 | +3 (*Deadly Enemies* tier) |

HP is rolled per body and the game prefers **distinct** max-HP values across the enemy side, so the two Nibbits in the paired room will normally show two different totals from the band. Combined paired pool: **84–92 base**, **88–96** at the *Tough Enemies* tier — a large pool for an Act 1 normal room, and the Slice Block adds an effective **+5 (+6) per body per three turns** on top of it.

Strength is applied to the caster and is permanent for the combat, so it compounds: it raises **both** Butt and Slice for that body on every later cycle.

Paired room, single player, both bodies alive (base numbers):

| Turn | Front | Back | Incoming total |
| --- | --- | --- | --- |
| 1 | Slice 6 (+5 Blk) | Hiss (Str 2) | **6** |
| 2 | Hiss (Str 2) | Butt 14 | **14** |
| 3 | Butt 14 | Slice 8 (+5 Blk) | **22** |
| 4 | Slice 8 (+5 Blk) | Hiss (Str 4) | **8** |
| 5 | Hiss (Str 4) | Butt 16 | **16** |
| 6 | Butt 16 | Slice 10 (+5 Blk) | **26** |
| 7 | Slice 10 (+5 Blk) | Hiss (Str 6) | **10** |
| 9 | Butt 18 | Slice 12 (+5 Blk) | **30** |

At the *Deadly Enemies* tier the same turns read **7 / 16 / 26 / 10 / 19 / 32 / 13**, with the heavy beat climbing +6 per cycle instead of +4.

Weak (solo) room, single player: **12, 6 (+5 Blk), —, 14, 8 (+5 Blk), —, 16, 10 (+5 Blk), —, 18 …** — a big opener, then one damage-free turn out of every three, and roughly +2 damage per body-cycle thereafter.

The structural facts that matter for modelling: the heavy turn is **every third turn**, it is **always visible one turn in advance** (the Hiss that feeds it is on screen the turn before), and the ramp is **linear and unbounded** — nothing caps Strength.

## Gimmicks

- **The phase offset is the whole encounter design.** Two identical bodies on the same cycle, started one beat apart, produce a deterministic light/medium/heavy sawtooth. Nothing here is random, so a player who reads intents once can plan the entire fight — and a player who does not will be surprised by the stacked turn where one body Butts while the other Slices.
- **Self-Strength, not shared.** Hiss buffs only the caster. Killing a body therefore deletes its accumulated ramp permanently, which makes focus-firing strictly correct and gives the fight a real targeting decision: the **back** Nibbit banks Strength first (it Hisses on turn 1) and so out-scales the front one for the whole fight, while the **front** Nibbit is the one carrying Block. Kill order genuinely matters.
- **Block on the same turn as an attack.** Slice is an attack *and* a defend in one beat, so the Nibbit that is "only" doing chip damage is also blunting your damage that same turn. Over a long fight this is where the extra effective HP lives, and it is the part the bestiary hides.
- **No player debuffs at all.** No Weak, no Vulnerable, no Frail, no status cards, no HP-loss effects — every point of pressure is plain attack damage. Defensive answers are unusually clean here; there is nothing to cleanse and nothing that punishes holding cards.
- **The ramp is the clock.** With no cap on Strength and a linear +2 (+3) per body every three turns, a stalled fight eventually becomes unsurvivable. The room is designed to punish pure-block turtling and reward a decisive kill on one body inside the first two or three cycles.
- **Fixed opener per slot.** Nothing is rolled — front always opens Slice, back always opens Hiss, the solo body always opens Butt. Turn 1 of the paired room is a fixed 6 (7) damage, which is the softest opening turn of any Act 1 two-body room and sets up the false impression of an easy fight.

## Scaling by act / ascension

- **Act:** none. Nibbit is Act 1 content only and reads no act index of its own; the only act-derived factor touching it is the multiplayer scaler below (Act 1 non-boss factor = 1.1).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 42–46 → **44–48** per body, and Slice Block 5 → **6**. Both changes lengthen the fight rather than raise the damage — the worst possible axis to lengthen against a linear self-Strength ramp.
  - *Deadly Enemies* tier: Butt 12 → 13, Slice 6 → 7, **Hiss +2 → +3**. The Hiss bump is the significant one: it is a 50% increase to the ramp rate, so by cycle three the Deadly-tier fight is dealing meaningfully more than the base fight, not a flat +1.
  - Move wiring, body count, slot flags, and the phase offset are identical at every ascension.
- **First-run pinning:** a brand-new save is fed `NibbitsWeak` as **normal-encounter index 0** — the first fight of the game — and `NibbitsNormal` at index 6. So the solo Nibbit is the tutorial body for "the enemy buffs itself and then hits harder," and the pair is the callback several rooms later.

## Multiplayer / seat-count adjustments

- **HP scales by seats.** On entering combat with more than one player, each body's max HP is multiplied by (player count × act factor); Act 1 non-boss uses **1.1**. A 2-player Nibbit sits at roughly 92–101 HP and a 3-player Nibbit at roughly 139–152 — paired-room pools of about **185–202** and **277–304**.
- **Block scales by seats too.** Monster-move Block is multiplied by the same (player count × 1.1) factor, so Slice grants about **11 Block at two seats** and **16–17 at three** instead of 5. On the *Tough Enemies* tier that is ~13 / ~20. This is the single largest multiplayer swing in the kit and it lands every third turn, per body.
- **Damage does not scale, but it is applied per seat.** Nibbit attacks resolve against every opposing player creature rather than picking one, so each Butt hits **every** player for its full value and each Slice likewise. Per-seat incoming damage is identical to the solo table above at any party size; the party's *total* damage taken multiplies by seat count.
- **Strength is per-body and unscaled**, so the ramp rate stays +2 (+3) per Hiss regardless of seats — but because HP and Block both grow with seats while the party's per-seat clock does not, larger parties spend more turns in the fight and therefore eat **more ramp cycles**. The multiplayer version is materially longer and its late turns are materially heavier.

## Fight-class reasoning — `attrition`

What this fight demands per turn is **sustained, repeatable throughput on both sides of the board rather than one big answer**: two ~45 HP bodies that block themselves every third turn and gain permanent Strength every third turn, against a fully deterministic light/medium/heavy incoming pattern with no debuffs and no surprises. The player's per-turn ask is a steady mix of damage and mitigation held over many turns, plus a kill-order decision — commit to one body and delete its ramp, because racing both at once loses to the Block and the compounding Strength. `spike` is wrong because the heaviest turn is telegraphed a full turn in advance and is only ~22–26 in single-player; `swarm` is wrong because two bodies with no summons is a pair, not a crowd, and the offset exists to smooth incoming damage rather than multiply it; `gimmick` over-reads the phase offset, which changes *when* things happen but never *what the player must do*. The failure mode of this room is running out of resources before the Strength ramp outruns your block — the textbook attrition loss.
