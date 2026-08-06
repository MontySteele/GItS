# Enemy Dossier — The Adversary Mk 3

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `TheAdversaryMkThree` (`MonsterModel`, sealed)
- **Kind:** boss
- **Act:** Act 3 tier of the Adversary ladder (Mk 1 / Mk 2 / Mk 3 are a 100 / 200 / 300 HP escalation of one identical script). No encounter registration for any Adversary appears anywhere in the decompiled tree, so the act slot is **inferred from the ladder position, not confirmed** — treat the act field as provisional.
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table description of mechanics and constants.

---

## 1. What this fight is

A single armored machine that does one thing: hit you on a fixed three-beat loop and get
permanently stronger every third turn. There are no adds, no summons, no phase change, no
hidden intent, no block, no debuffs aimed at the player, and no randomness in move
selection. The only defensive trick it owns is a small stack of Artifact applied on entry,
which taxes your debuff plan rather than your damage plan.

It is the third and hardest member of a scripted family. All three Adversaries share an
identical state machine, an identical move shape, and identical follow-up wiring; only the
constants differ:

| | Mk 1 | Mk 2 | **Mk 3** |
|---|---|---|---|
| HP (min = max) | 100 | 200 | **300** |
| Opening single attack | 12 (Smash) | 13 (Bash) | **15 (Crash)** |
| Beam single attack | 15 | 16 (also carries a status-count constant, unused by the move) | **18 (Flame Beam)** |
| Barrage per hit × hits | 8 × 2 | 9 × 2 | **10 × 2** |
| Strength gained per Barrage | +2 | +3 | **+4** |
| Artifact on entry | 0 (i.e. none) | 1 | **2** |

Mk 3 is not a different fight from Mk 1; it is the same fight with every dial turned up,
most sharply the Strength dial.

## 2. Intent pattern / AI

Fully deterministic. Three move states, each hard-wired to the next, in a closed ring:

1. **Crash** — single attack.
2. **Flame Beam** — single attack.
3. **Barrage** — multi-attack, then self-buff.
4. → back to Crash.

The initial state is Crash, and the state machine will not transition away from a move
state before the first move has actually been performed, so the very first combat turn is
guaranteed to be Crash. There is no RNG in the transition (no weighted rolls, no
"can't repeat" guard needed), so the entire fight is legible from turn one and stays
legible: the player can plan an arbitrary number of turns ahead with certainty.

Intents shown:

| Move | Telegraph |
|---|---|
| Crash | single-attack intent, 15 |
| Flame Beam | single-attack intent, 18 |
| Barrage | multi-attack intent, 10 × 2, **plus a separate buff intent icon** |

The buff icon on Barrage is the fight's only warning system — it is shown alongside the
attack, so the Strength gain is never a surprise.

## 3. Damage and block numbers

| Stat | Value |
|---|---|
| HP | 300 flat (min == max, so no HP roll and no per-instance variance) |
| Crash | 15 damage, one hit |
| Flame Beam | 18 damage, one hit |
| Barrage | 10 damage × 2 hits (20 raw), then **+4 Strength to itself** |
| Block | **none** — it has no block move at all |
| Debuffs applied to player | none |
| Powers on entry | Artifact 2 |

Strength is additive to damage per hit, so it inflates the two-hit Barrage twice as fast as
it inflates the single attacks. Unmitigated cycle math (Strength S at the start of each
cycle, before that cycle's Barrage resolves):

| Cycle | Crash | Flame Beam | Barrage total | Cycle damage | Running total | Str after |
|---|---|---|---|---|---|---|
| 1 (S=0) | 15 | 18 | 20 | 53 | 53 | 4 |
| 2 (S=4) | 19 | 22 | 28 | 69 | 122 | 8 |
| 3 (S=8) | 23 | 26 | 36 | 85 | 207 | 12 |
| 4 (S=12) | 27 | 30 | 44 | 101 | 308 | 16 |
| 5 (S=16) | 31 | 34 | 52 | 117 | 425 | 20 |

Each completed cycle adds +16 to the next cycle's raw output (+4 on each single attack,
+8 on Barrage). The incoming-damage curve is linear per cycle, but the *block* curve the
player must sustain is superlinear in practice because Barrage's per-hit structure eats
Block in two bites and each bite grows.

## 4. Gimmicks

There are exactly two, and both are quiet:

- **Artifact 2 on entry.** Applied to itself the moment it is added to the room. It nulls
  the next two visible debuffs it would receive (and only debuffs — a power whose amount
  resolves as a buff, or an invisible/internal power, passes straight through and does not
  burn a charge). Each nulled debuff decrements the counter by one. Practical effect: a
  Weak/Vulnerable-based mitigation plan must pay a two-application entry fee before it does
  anything, and a build that carries exactly one debuff card is close to shut out for the
  opening cycle. **In multiplayer this stack grows — see §6.**
- **Uncapped Strength ramp.** +4 per Barrage, forever, with no decay, no cap, and no
  removal condition in the model. This is the fight's clock. Nothing else about the
  encounter changes over time.

Notably absent: no block, no artifact refresh, no enrage threshold, no HP-gated phase, no
death rattle, no minion spawn, no self-heal, no player debuff. The take-damage sound is the
armored type, which is cosmetic.

## 5. Scaling by act / ascension

- **By act:** none in the model. The Adversary's constants are literals; there is no act
  index anywhere in its logic. The only act-sensitivity is indirect, through the
  multiplayer scaling curve (§6).
- **By ascension:** effectively **none**. HP is written through the ascension helper against
  the "tough enemies" ascension level, but the ascended value and the fallback value are
  **both 300** — the hook is wired up and does nothing. Mk 2 has the same no-op (200/200);
  Mk 1 does not use the helper at all. No damage constant, hit count, Strength gain, or
  Artifact count is ascension-gated. Any ascension pressure on this fight has to come from
  the player's side of the ledger, not the boss's.

That makes Mk 3 unusually flat for a boss: the difficulty ladder is expressed by *which
Adversary you face*, not by act or ascension modifiers on a single one.

## 6. Multiplayer / seat-count adjustments

The Adversary itself contains no multiplayer code, but three engine-level rules land on it
hard:

- **HP multiplies by seat count and then by an act coefficient.** For a party of *n* > 1,
  max HP becomes 300 × *n* × the multiplayer coefficient for the current act: **1.1 in
  Act 1, 1.2 in Act 2, and 1.3 in Act 3 for boss-room encounters** (1.2 in Act 3 for
  non-boss rooms). As a boss in the Act 3 slot, a 2-player Mk 3 is 780 HP and a 3-player
  Mk 3 is 1170 HP.
- **Every attack it makes hits every living player for full damage.** Its moves are built as
  "target all opponents" with no random-target flag and no damage split, so with two
  seats alive the party absorbs 2× the table in §3, with three seats 3×. Barrage
  re-resolves its target list per hit, so a seat that dies mid-Barrage stops taking the
  remaining hits, and its Strength bonus applies to each player's copy of each hit.
- **Artifact scales with the party.** The Artifact power scales in multiplayer by
  *amount + (player count − 1)*, so the entry stack is 2 solo, **3 in duo, 4 in trio**. A
  co-op party pays a strictly larger debuff entry fee than a solo player, which
  disproportionately punishes a designated debuff seat.

The block-scaling rule that normally multiplies enemy Block by seat count never applies
here, because the Adversary never gains Block.

## 7. What the fight demands, turn by turn

- Turns 1 and 2 of each cycle: a single clean block number to eat one telegraphed hit.
- Turn 3 of each cycle: block that survives being split across two hits, plus the knowledge
  that the wall just got 4 higher permanently.
- Across the whole fight: 300 (solo) effective damage output before the Strength curve
  outpaces your defensive ceiling. Killing it inside four cycles (12 turns) means ~25
  damage per turn sustained; every cycle past that costs +16 incoming.

There is no burst to survive, no add to clear, no puzzle to solve, and no turn where the
correct play is unclear. What varies is only *how long* you can keep paying.

## 8. Proposed fight class: `attrition`

Every turn asks the same question — can you cover a known, telegraphed number and still
push damage — and the fight's whole design is making that number creep past your answer.
The Strength ramp is a soft timer rather than a threat spike: no single turn ever demands
several times the previous turn's mitigation, but the floor rises by +16 per cycle without
bound, so the loss condition is running out of sustain, not being caught off guard.
Artifact 2 (3–4 in co-op) reinforces the same axis by taxing the exact tool that would
flatten the curve, and the total absence of block, adds, randomness, or phase changes rules
out `swarm`, `gimmick`, and `mixed`. Track B should read this as a long, flat, rising demand
curve with a hard damage-per-turn threshold, not as a burst-mitigation checkpoint.
