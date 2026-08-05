# Enemy Dossier — Bowlbug (Rock)

- **Class:** `BowlbugRock`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `BowlbugsNormal` (3 bodies), `BowlbugsWeak` (2 bodies), `SlumberingBeetleNormal` (3 bodies). It is the **fixed** member of all three — the other slots are rolled.
- **Fight class:** `gimmick`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Rock bowlbug is the heavy of the Hive worker packs: one large, slow, single-target headbutt on
repeat, with a self-destructive flaw. It is a re-skin (the "rock" skin) of the shared bowlbug/workbug
skeleton, and it is always present in a bowlbug encounter — the variable slots are filled by the Egg,
Silk, and Nectar workers, which are smaller and cheaper.

Its defining property is a starting debuff on itself, **Imbalanced**: any attack it makes that the
target **fully blocks** knocks it off balance. Being off balance costs it its next turn.

## 2. Intent pattern / AI

The move machine has two moves and one branch, and no randomness at all:

| State | Intent shown | Effect |
|---|---|---|
| `HEADBUTT_MOVE` | single attack, 15 | Deal 15 damage to one target. If it is off balance at that moment, it immediately stuns itself. |
| `DIZZY_MOVE` | Stun | Does nothing. Clears the off-balance flag. |

Flow:

- Opening move is always **Headbutt**.
- After a headbutt, a conditional branch checks the off-balance flag: if set, the next state is
  Dizzy; otherwise it is Headbutt again.
- Dizzy always returns to Headbutt.

So the baseline loop is **Headbutt every single turn, forever**, and the only way the loop is ever
interrupted is by the player. There is no ramp, no buff move, no block move, no debuff applied to the
player, no summon, and no behavior change on low HP or on the death of pack-mates.

## 3. The gimmick — Imbalanced

Imbalanced is applied to itself when it enters the room (1 stack, single-stack debuff type; it is
flagged as a debuff, so it is visible in the enemy's power row from turn 1).

- **Trigger condition:** the bowlbug deals attack damage and the result is *fully blocked* — the
  target's Block was greater than or equal to the incoming damage, so zero HP was lost. Partial
  mitigation does nothing; taking 1 damage through Block does nothing.
- **Effect:** the flag is set mid-attack, and because the headbutt checks the flag right after
  landing, the stun applies **immediately** — a stun animation plays and the enemy's next turn is
  pre-empted. The intent for the following turn reads as Stun.
- **Recovery:** on the stunned turn it performs the dizzy move, which clears the flag and does
  nothing else. The turn after that it headbutts again. The flag then has to be re-earned by fully
  blocking another headbutt.

Net effect: **fully blocking the headbutt halves its damage output** over the following two turns
(one headbutt becomes zero-through-block plus one skipped turn). Failing to reach the threshold gives
the normal 15 to the face and no tempo. It is an all-or-nothing block check on a fixed, fully
telegraphed number.

Note that the Imbalanced power is generic — it exists on other owners too, where the fully-blocked
trigger simply stuns the owner outright. The Rock bowlbug is the special case that routes it through
its own off-balance flag so it can play the dizzy animation and manage the state machine.

## 4. Numbers

| Stat | Base | With Tough Enemies ascension | With Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 45–48 | 46–49 | — |
| Headbutt damage | 15 | — | 16 |

- No Block, ever — it never gains Block, so the multiplayer enemy-Block scaling system never touches
  it.
- HP is rolled per-body from the inclusive range; the encounter's unique-HP pass avoids duplicating
  another enemy's roll where it can, so the exact value varies within the band.
- Pack context for damage budgeting (same act, same encounters): Egg 21–22 HP / 7 bite, Nectar 35–38
  HP / 3 thrash, Silk 40–43 HP / 4 thrash. The Rock is the largest body and roughly **twice the
  single-hit damage of the rest of the pack combined**.

## 5. Scaling

**By act:** none. It appears only in Act 2 and has no act-conditional stats.

**By ascension:** two levers only, both flat and both from the shared ascension helper — Tough
Enemies adds +1 to both ends of the HP band, Deadly Enemies takes the headbutt from 15 to 16. Nothing
changes the block threshold's *shape*: fully blocking is still a hard yes/no, it just moves by one
point. The 16-damage version is the meaningful one for balance, because a 15-Block plan that used to
stun it silently stops working at that ascension.

**By seat count (multiplayer):** HP is multiplied by the shared formula — base × player count ×
act factor, with the Act 2 non-boss factor being **1.2**.

| Players | Effective HP band (base) |
|---|---|
| 1 | 45–48 (no scaling at 1 player) |
| 2 | ~108–115 |
| 3 | ~162–173 |
| 4 | ~216–230 |

Damage does **not** scale with seat count: it is still one 15-damage headbutt against one target per
turn, so per-player incoming pressure falls sharply in co-op while its effective HP rises
super-linearly. The gimmick also gets easier in co-op in one specific way — only the *targeted* seat
has to reach the Block threshold, and any seat that happens to be well-armored that turn can trigger
the stun for the whole table. Conversely the pack around it does scale in count/HP, so the Rock
becomes proportionally less of the threat as seats are added.

## 6. Proposed fight class — `gimmick`

Per turn this enemy asks the player for exactly one number — reach 15 (16 on Deadly Enemies) Block on
the targeted seat — and pays out a skipped enemy turn for hitting it and nothing at all for missing it
by one. That threshold, not the raw damage, is what the fight is testing: the headbutt on its own is
an unremarkable medium single hit with no ramp, no debuffs, and no defensive stat to grind through,
which rules out `spike` and `attrition`; it is one large body in a pack whose other members are minor,
which rules out `swarm`. For Track B this should be modeled as a **binary defensive threshold check
with a tempo payout**, and it is the cleanest probe in the act for "can this deck produce an exact
block number on demand" — decks with lumpy or damage-only Block curves get the full 15 every turn
while threshold-capable decks take roughly half.
