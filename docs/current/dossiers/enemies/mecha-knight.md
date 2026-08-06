# Mecha Knight

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `MechaKnight` (`MonsterModel`, sealed)
- **Kind:** elite
- **Act:** Act 3 (Glory; act index 2)
- **Encounter:** `MechaKnightElite` — `RoomType.Elite`, a **solo** encounter. `AllPossibleMonsters` and `GenerateMonsters` both return exactly one body, with no slot label and no adds. Camera pulled to 0.9× scale and shifted 50px down.
- **Fight class:** `mixed`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What Mecha Knight is

Mecha Knight is a single, very large armored body — the biggest solo HP bar among Act 3 elites at 300 (320 at Tough Enemies) — that runs a **fully deterministic, no-randomness move loop**. There is no branch node, no weighted roll, no repeat limiter, and no HP-threshold phase change anywhere in its move machine. Every state hands off to exactly one successor. If you know what it did last turn, you know with certainty what it will do for the rest of the fight.

What it trades that predictability for is a set of three simultaneous pressures that don't overlap in time:

1. a **telegraphed, unbounded-rising single spike** every third turn,
2. a **hand-clog status dump** (4 Burns per seat) on a different third of turns,
3. a **combat-start Artifact stack** that eats the player's first three debuffs — the standard answer to a telegraphed spike (Weak) is taxed before it works.

The two non-damage turns in each cycle are not free turns; they are the turns where the fight decides how bad the next spike will be.

## 2. Intent pattern / AI

The state machine is a **linear chain with a loop-back**, seeded on Charge. Because the machine suppresses transitions until the monster has actually performed its first move, **turn 1 is always Charge**, deterministically.

```
Turn 1:  CHARGE
           ↓
         FLAMETHROWER  ←──────────┐
           ↓                      │
         WINDUP                   │
           ↓                      │
         HEAVY CLEAVE  ───────────┘
```

**Charge is a one-time opener.** Heavy Cleave loops back to Flamethrower, not to Charge, so the Charge state is entered exactly once per combat and never again. From turn 2 onward the fight is a strict **3-turn cycle**: Flamethrower → Windup → Heavy Cleave.

| Turn | Move | Intent shown | Effect |
| --- | --- | --- | --- |
| 1 (once only) | **Charge** | single attack | 25 damage (30 at Deadly Enemies) |
| 2, 5, 8, … | **Flamethrower** | status-card intent, count 4 | Adds **4 Burn** to the hand of **every** player |
| 3, 6, 9, … | **Windup** | *two* intents: defend **and** buff | Gains **15 Block**, then **+5 Strength** (permanent) |
| 4, 7, 10, … | **Heavy Cleave** | single attack | 35 base (40 at Deadly) **+ accumulated Strength** |

Three things a demand model should take from the shape:

- **Two of every three turns deal zero direct damage.** The player's HP bar moves on Cleave turns (and on Charge, turn 1) and otherwise only via Burn chip. Incoming damage is extremely lumpy.
- **The spike is telegraphed two turns out, not one.** Windup is the tell: the moment you see the defend+buff intent pair you know the *next* intent is the cleave, and you already know its exact number. There is also a redundant visual tell — see §4.3.
- **The intent number is honest and per-seat.** The attack intent recomputes damage through the local player's own damage-modification hooks, so the printed number already includes the monster's Strength and that seat's own Vulnerable/mitigation state. Players are never surprised by the cleave's size; they are only surprised by how fast it grows.

## 3. Numbers

| Stat | Base | Tough Enemies (asc 8) | Deadly Enemies (asc 9) |
| --- | --- | --- | --- |
| Initial HP | 300 (min == max, no roll) | 320 | — |
| Charge damage (turn 1 only) | 25 | — | 30 |
| Heavy Cleave base damage | 35 | — | 40 |
| Windup Block | 15 | — | unchanged |
| Windup Strength gain | +5 | — | unchanged |
| Flamethrower Burn count | 4 per seat | — | unchanged |
| Combat-start Artifact | 3 | — | unchanged |

### 3.1 The cleave curve

Strength is gained on every Windup and never spent, decayed, or capped by anything in the kit. Windup always immediately precedes Heavy Cleave, so the *k*-th cleave lands with exactly `5k` Strength:

| Cleave # | Turn | Base ascension | Deadly Enemies |
| --- | --- | --- | --- |
| 1st | 4 | 40 | 45 |
| 2nd | 7 | 45 | 50 |
| 3rd | 10 | 50 | 55 |
| 4th | 13 | 55 | 60 |
| 5th | 16 | 60 | 65 |
| *k*-th | 3k+1 | **35 + 5k** | **40 + 5k** |

Averaged over the 3-turn cycle, direct incoming is `(35 + 5k)/3` ≈ **13.3 + 1.7·k per turn**, plus up to 8 more per cycle if the Burns are held (§4.2). That is a slow slope in per-turn terms but a brutal one in per-*event* terms: the player must cover a single number that starts at 40 and grows by 5 every three turns, on a schedule they can read from turn 3.

Against a 300 HP bar, a party clearing ~40 damage/turn kills it around turn 8 — i.e. after eating Charge plus two cleaves (40 + 45 + 25 = 110 incoming, before Burns). A party at ~20 damage/turn is still fighting on turn 15 and is by then covering 60-point hits, which is where this elite actually kills people.

### 3.2 The block is small and does not gate the fight

15 Block once every three turns against a 300 HP pool is a rounding error solo — roughly 5% of the bar, and only on one turn in three. **Solo, Mecha Knight is not a wall.** This changes materially in co-op (§6), where the same 15 becomes 36–72.

## 4. Gimmicks

### 4.1 Combat-start Artifact — the anti-debuff tax

Before the first turn, Mecha Knight applies **3 Artifact** to itself. Artifact is a counter-type buff that fully nullifies the next incoming *visible debuff* and decrements by one per absorption. It only intercepts powers whose net type is Debuff and only ones flagged visible, so hidden/bookkeeping powers pass through.

This is the single most important thing to model about the fight, because it is aimed squarely at the fight's own weakness. A telegraphed rising spike is normally answered with Weak; a 300 HP bar is normally answered with Vulnerable. Mecha Knight makes the player spend **three debuff applications on nothing first**, and in co-op the count rises with headcount (§6). A deck whose mitigation plan is "stack Weak before the big hit" does not come online until roughly the second cleave.

Note the interaction with the cycle: three Artifact charges is almost exactly one cleave cycle's worth of setup. The design reads as "your debuff plan is delayed by one spike," not "your debuff plan is dead."

### 4.2 Flamethrower — 4 Burns per seat, every third turn

Flamethrower deals **no damage**. It adds 4 copies of **Burn** to the hand of every player creature in the combat (the move receives the full player-creature list as its targets and adds the cards to each).

Burn is an unplayable status card, cost -1, no upgrade, that deals **2 damage to its holder at end of turn if still in hand**. Four copies is therefore **8 chip damage per cycle** — but that damage carries the standard Move value-props and is **not** flagged unblockable, so residual block absorbs it. Players who over-block on a Flamethrower/Windup turn eat none of it.

The real cost is not the 8 damage; it is the **hand slot occupancy**. Four unplayable cards land in hand on the exact turn before the Windup→Cleave setup window, which is the turn the player most wants a full hand to bank block or push damage. In practice Flamethrower converts one of every three player turns into a partial turn, and any card that discards/exhausts/scries at scale is disproportionately valuable here.

Also worth carrying: the Burns are added **to hand**, not to discard/draw, so they do not permanently pollute the deck for the rest of combat unless the player's own draw rules recycle them. The clog is per-cycle and self-clearing at end of turn, not cumulative.

### 4.3 The wound-up state is a visual tell with no mechanical body

The monster tracks an internal "wound up" flag, set by Windup and cleared by Heavy Cleave. It drives **only the animator**: while wound up, the idle and hurt animations swap to their wound-up variants. There is no damage, block, resistance, or targeting consequence attached to it anywhere.

For a demand model this is worth one line: the fight gives the player a **persistent, always-visible** state readout for "the cleave is loaded," on top of the intent icon. There is no hidden information in this encounter at all.

### 4.4 No adds, no summons, no death rider, no minions

Solo body, solo encounter, single-element monster list. Nothing spawns, nothing revives, nothing splits. Whatever the party's AoE is worth, it is worth nothing here.

## 5. Scaling by act / ascension

- **By act:** none intrinsic. `MechaKnight` appears only in Glory (Act 3) and reads no act index directly. Act enters only through the multiplayer scaling constant (§6).
- **By ascension:** two binary gates, both narrow, and both hitting only the *baseline*:
  - *Tough Enemies* (asc 8): HP 300 → 320. About +7%.
  - *Deadly Enemies* (asc 9): Charge 25 → 30, Heavy Cleave base 35 → 40. About +14–20% on the two attacks.
  - **Nothing else is ascension-gated.** The Windup +5 Strength, the 15 Block, the 4 Burns, and the 3 Artifact are all identical at every ascension. As with `FlailKnight`, the *slope* of the threat curve is ascension-invariant and only the intercept moves — Deadly Enemies is worth a flat +5 on every cleave forever, which is exactly one extra Windup's worth, i.e. the fight starts three turns "further along" and is otherwise unchanged.
  - *Swarming Elites* (asc 1) changes how many elites the map contains, not this monster.

## 6. Multiplayer / seat count

Headcount is absorbed entirely by the monster's own numbers; the encounter never adds bodies.

- **HP** scales by `player count × act constant`. Act 3 **non-boss** uses **1.2**. So: 300 solo, **720** at 2 players, **1,080** at 3, **1,440** at 4 (base 320 first at Tough Enemies → 768 / 1,152 / 1,536).
- **Windup Block scales the same way** — monster-move block is multiplied by `player count × 1.2`. The 15 becomes **36** at 2 players, **54** at 3, **72** at 4. This is the biggest qualitative change in the fight: solo the block is negligible, at 4 players it is a real recurring wall the party must chew through every third turn on top of a 1,440 bar.
- **Artifact scales additively with headcount**: 3 solo, then `+1 per extra player` — **4 / 5 / 6** at 2 / 3 / 4 players. The anti-debuff tax gets worse exactly when the party has more debuff appliers, so the delay before Weak/Vulnerable comes online stays roughly constant in *turns* rather than shrinking.
- **Strength is NOT scaled for multiplayer.** The +5 per Windup is flat at every seat count. The cleave curve is identical solo and in a 4-player party.
- **Damage is NOT divided among seats.** Both attacks are built as monster attacks targeting *all opponents* with the target list refreshed between hits, so **every player takes the full printed number**. Charge is 25 to each seat; the *k*-th cleave is `35 + 5k` to each seat. A 4-player party absorbs 4× the printed cleave.
- **Flamethrower is also per-seat and undivided:** **4 Burns to every player**, so a 4-player party takes 16 Burns and up to 32 chip damage per cycle spread across four hands.
- No co-op-only moves, no aggro or threat mechanic, no per-seat state, no target selection of any kind. The monster does not "choose" anyone.

Net co-op read: seat count roughly quadruples the party's total incoming and quadruples the monster's effective bar, but *also* adds a 72-block recurring wall and a 6-charge debuff shield that the party's extra damage has to fight through. This fight scales harder than a linear headcount model would predict, and the pressure lands on the two turns per cycle that are nominally "safe."

## 7. Proposed fight class: `mixed`

The per-turn demand oscillates on a strict 3-beat and asks a genuinely different question on each beat: on the Flamethrower turn the question is *can you still act with four dead cards in hand*; on the Windup turn it is *do you spend this turn racing the block and the ramp or banking mitigation*; on the Cleave turn it is *can you cover a single hit of 40, 45, 50, 55…*. No single axis dominates for more than one turn at a time, which is what makes a one-axis label dishonest here.

`spike` is the runner-up and captures the damage profile alone — two of every three turns deal no direct damage, and the whole HP loss is concentrated in one telegraphed, unbounded-rising hit. But a pure-spike curve would miss the two mechanics that decide whether the spike is survivable: the 3–6 Artifact charges that delay the standard anti-spike answer (Weak/Vulnerable) by roughly one full cycle, and the 4-Burn-per-seat hand clog that removes capacity on the setup turn. Both are resource-denial gimmicks, not damage, and both are load-bearing.

`attrition` is wrong despite the 300/720/1,440 HP pool: the fight is long, but nothing about it demands *sustained* per-turn mitigation — the safe turns are genuinely safe, and a party that only defends on cleave turns loses nothing but 8 Burn chip. `swarm` is trivially wrong (solo body, no adds, AoE is worthless).

A Track B demand curve for `MechaKnightElite` should be modeled as a **3-period sawtooth with a rising peak (35 + 5k) and a near-zero floor**, with a separate hand-capacity penalty on the pre-peak turn and a fixed 3-to-6-application debuff deductible at the front of the fight. Averaging it into a smooth line loses the fight.
