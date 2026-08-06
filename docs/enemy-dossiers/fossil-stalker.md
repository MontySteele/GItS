# Enemy Dossier — Fossil Stalker

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `FossilStalker`
- **Kind:** normal
- **Act:** Act 1 (`Underdocks`, act index 0 — the alternate Act 1 pool alongside `Overgrowth`)
- **Encounters:** `FossilStalkerNormal` — a solo encounter, one Fossil Stalker and nothing else
- **Fight class:** `gimmick`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A single stone-bodied predator with roughly 52 HP and three unremarkable attacks, wrapped around one
loud rule: **it grows permanently every time it draws blood.** On entering the room it applies a
counter-style buff to itself worth **3**, and after any of its own attacks connect for *unblocked*
damage it converts that into **+3 Strength per connecting hit**. Nothing else in its kit gains Block,
heals, summons, or reacts to low HP — the whole fight is the escalation clock and one Frail rider.

It is a Phobia-skinned body (cosmetic variant support) and takes stone-type hit reactions; neither
affects play.

## 2. Intent pattern / AI

Three move states behind a single equal-weight random branch. Every move routes back into the same
branch, so there is no phase, no sequence, and no memory beyond an anti-repeat rule.

| State | Intent shown | Effect |
|---|---|---|
| `LATCH_MOVE` | single attack, 12 | Straight 12 damage. The **opening move is always Latch** — it is the machine's initial state. |
| `TACKLE_MOVE` | attack **+ debuff** | 9 damage, then **1 Frail** to the player side. |
| `LASH_MOVE` | multi-attack, 3 × 2 | Two hits of 3 (6 raw), one animation, two separate damage events. |

Flow: turn 1 is always Latch. From then on the branch rolls uniformly — **1/3 Latch, 1/3 Tackle, 1/3
Lash** — with one constraint from the branch weights: a move that has already been chosen on the two
most recent moves is weighted to zero, so **no move can appear three turns in a row**. There is no
cooldown beyond that and no once-per-combat move.

Because the intent icon reads live damage (base plus the monster's current Strength), the escalation
is visible in the intent number before it lands — the player can always see exactly how much the
engine has grown.

## 3. Gimmicks

**The Suck buff (self-applied, amount 3).** This is the fight. After the Stalker resolves an attack
against the player side, it looks at the attack's results **per hit**, and counts each hit in which
*any* target took at least 1 point of **unblocked** damage. It then gains `3 × (that count)` Strength.
Consequences worth stating plainly:

- **Blocking to zero denies it completely.** Fully absorbed damage yields no Strength; there is no
  partial credit and no chip-through clause.
- **Lash is the dangerous move, not Latch.** Its two hits are counted separately, so a fully connecting
  Lash grants **+6 Strength** — double what the big single attack grants — despite being the smallest
  raw number on the board. Every point of Strength then applies *per hit*, so Lash also benefits twice
  from the Strength it built. A player who "ignores the little one" and blocks only the big hits is
  feeding the exact move that compounds fastest.
- Pet damage is deliberately excluded from crediting the pet's owner, so pet-tanking does not
  accidentally launder a hit into a non-trigger for the owner (and vice versa).
- The buff is a Buff-type counter, so debuff-removal effects do not touch it; the only lever is Block.

**Frail rider on Tackle.** 1 Frail to the player side, i.e. **Block gained is multiplied by 0.75** on
the affected turn. This is a targeted attack on the one resource that denies the Suck engine: Tackle
makes the *next* turn's block-to-zero harder, which makes a Suck trigger likelier, which makes every
later turn harder. It ticks down at the end of the enemy turn, with the usual same-turn-application
guard, so a Tackle landed on the enemy turn is felt on the player's following turn.

**Escalation math (worst case, nothing blocked).** Turn 1 Latch 12 → Str 3. Turn 2 Lash (3+3)×2 = 12
→ Str 9. Turn 3 Latch 12+9 = **21** → Str 12. Turn 4 Lash (3+12)×2 = **30**. A run of unblocked turns
takes a ~12/turn enemy past 30/turn inside four turns, against an Act 1 HP pool. Conversely a party
that blocks to zero every turn fights a static 9/12/6 enemy with ~52 HP and wins without drama. The
gap between those two lines is the entire design.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 51–53 | 54–56 | — |
| Latch (single) | 12 | — | 14 |
| Tackle (single + debuff) | 9, then 1 Frail to players | — | 11, then 1 Frail |
| Lash (multi) | 3 × 2 hits = 6 | — | 4 × 2 hits = 8 |
| Starting Suck amount | 3 | — | — |
| Strength gained per connecting hit | 3 | — | — |

- HP is rolled inclusively from the band.
- It never gains Block, so the enemy-Block multiplayer scaler never applies to it.
- Frail is always 1 stack, never ascension- or seat-scaled.
- The Suck amount (3) has **no** ascension variant — Deadly Enemies raises the base numbers but not
  the escalation rate.

## 5. Scaling

**By act:** none. Underdocks-only, no act-conditional stats. It is an Act 1 normal encounter, so a
party meets it with an unrefined deck and often without a reliable block-to-zero turn — which is
precisely why the engine is tuned to punish a partial block.

**By ascension:** two flat levers. *Tough Enemies* shifts the HP band up by 3 at both ends (51–53 →
54–56), lengthening the fight by roughly a third of a turn and therefore granting the engine more
chances to trigger. *Deadly Enemies* raises all three attacks (12→14, 9→11, 3→4 per Lash hit). The
Deadly bump is nastier than it looks: raising the base damage raises the *block threshold* required to
deny a trigger, so on high ascension the same defensive hand that used to zero a move now leaks 1–2
damage and pays 3 (or 6) Strength for the privilege.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, the Act 1 non-boss factor being
  **1.1**.

| Players | Effective HP band (base roll) |
|---|---|
| 1 | 51–53 (no scaling at 1 player) |
| 2 | ~112–117 |
| 3 | ~168–175 |
| 4 | ~224–233 |

- *Attacks are not per-seat-scaled in magnitude, but they are delivered to the whole player side* —
  a monster attack with no single designated target resolves against every valid player creature.
  So each seat eats the full 12 / 9 / 3×2, and Tackle's Frail lands on **every** player.
- **The Suck trigger is an OR across the table, not an AND.** A hit counts if *any* seat took unblocked
  damage. Denying the engine in a 4-player game requires all four seats to block that hit to zero,
  every hit — and a fully-connecting Lash is still only +6 total, not +6 per seat. Co-op therefore
  makes denial roughly (seats)× harder to coordinate while leaving the reward for denial unchanged.
- Net co-op shape: a much longer fight (2–4× HP) in which the escalation is far more likely to get
  started, and once started it is aimed at everyone at once. This is the seat count where the Stalker
  stops being a puzzle and turns into a genuine race.

## 6. Proposed fight class — `gimmick`

What this fight demands per turn is a single binary the player must re-solve every round: **take zero
unblocked damage, or accept a permanent +3 (or +6) to everything the enemy will ever do again** — and
the Frail rider exists specifically to tax the resource that answers the question. That conditional,
state-dependent rule is the whole encounter; strip the Suck buff out and what remains is a solo
~52 HP body swinging for 12 in Act 1, which is not a fight at all. It is not `spike` (no telegraphed
burst turn to survive — the big number only exists if the player built it), not `attrition` (the HP
pool is small and the fight is short when played correctly), and not `swarm` (one body). For Track B
it should be modeled as a **threshold/denial curve rather than a sustain curve**: demand is near-zero
for a party that can reach exact-block each turn and rises superlinearly with each turn of leak, so the
right instrument is "probability the player can zero the incoming number this turn," not "average
damage per turn."
