# Enemy Dossier — Decimillipede (Back Segment)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `DecimillipedeSegmentBack`
- **Kind:** elite
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounter:** `DecimillipedeElite` (elite room), three fixed slots — Front, Middle, Back segments, always all three
- **Fight class:** `mixed`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Back Segment is one third of a single creature. All three segments (Front / Middle / Back) are the
same logic class with different visual scenes attached — the Back subclass exists **only** to route the
attack-shake animation to its own segment driver node. Every number, every move, and every rule below
is shared identically with the Front and Middle segments; there is no back-specific stat, no
back-specific move, and no positional behavior. It is not listed in the compendium separately (the
bestiary shows the Decimillipede as one composite entry).

Two things define the fight:

1. **The trio is phase-locked.** Each segment runs the same fixed three-move cycle, but the encounter
   deals each segment a different starting offset, so on every turn of the fight the party eats one of
   each move — one multi-hit, one self-buff attack, one Weak attack — until the pattern is broken by a
   death.
2. **Segments do not stay dead.** Killing one only makes it dormant; it reattaches and comes back with
   HP. The fight ends only when all three are dead at the same time.

## 2. Intent pattern / AI

Three attack moves in a strict rotation, plus a two-state death/revive detour.

| State | Intent shown | Effect |
|---|---|---|
| `WRITHE_MOVE` | multi-attack, 5 × 2 | Two hits of 5 |
| `BULK_MOVE` | single attack 6 **+ buff** | 6 damage, then **+2 Strength to itself** (permanent, no cap) |
| `CONSTRICT_MOVE` | single attack 8 **+ debuff** | 8 damage, then **1 Weak** to the target(s) |
| `DEAD_MOVE` | no intent | Does nothing; it is dead this turn |
| `REATTACH_MOVE` | heal | Revives itself and heals |

Rotation (the follow-up chain is fixed and unconditional):

**Writhe → Constrict → Bulk → Writhe → …**

- The encounter rolls one starting index for the Front segment; Middle starts one step later, Back
  starts **two steps later**. So the Back Segment's opening move is whichever of the three the other
  two are not opening with — over the trio, all three moves fire on turn 1 and on every turn after.
- There is no HP-threshold behavior, no enrage, no reaction to a sibling dying, and no randomness in
  the baseline loop. Intents are fully readable a full cycle ahead.
- **After a revive the rotation re-randomizes.** The revive path is Dead → Reattach → *random branch*,
  and that branch picks one of the three moves with a cannot-repeat rule (it will not immediately pick
  the same move twice in a row out of the branch). From there the fixed chain resumes. This is the only
  RNG in the fight, and it means a revived segment can fall in phase with a sibling — two Bulks or two
  Constricts landing on the same turn.
- The Reattach state is flagged **must-perform-once-before-transitioning**: the revive turn cannot be
  skipped or short-circuited by any move-forcing effect.

All three attacks are declared as monster attacks against **all opponents** — in single player that is
the one player, in co-op it is every seat (see §5).

## 3. The gimmick — Reattach

Every segment enters the room carrying a **Reattach** buff worth **25 HP** (this buff is flagged to
scale with seat count).

What happens when a segment's HP reaches zero:

- If **any other segment is still alive**, the death is *not* fatal to the encounter: the segment is
  immediately forced into the Dead state, is made **non-interactable** (cannot be targeted), and is
  **not removed from combat**. Its corpse stays on the field with the shriveled art, showing no intent.
- It is also protected while dormant: a hit-permission hook refuses damage and power application to it
  while it is reviving. Damage and debuffs aimed at a dead segment are wasted.
- Its next turn is the Reattach turn — a heal intent, and it heals **25** (not to full). It becomes
  targetable again and rejoins the cycle at a random move.
- It also does not vanish to removal-from-combat effects, and it is explicitly exempt from the
  "disappear from Doom" behavior — a Doom-style instant-kill does not delete the body.

So the practical rule for the player is: **you must land the third kill inside the revive window.**
Killing a segment buys you exactly one turn of relief (its Dead turn) at the cost of leaving a 25-HP
target that comes back with whatever Strength it had banked (Strength is not reset by the revive —
nothing clears it). Focus-firing one segment down repeatedly is a net loss; the fight wants near-
simultaneous execution of all three. When the last living segment dies while all others are already
dead, the encounter resolves and all three bodies fade out together.

Corollary worth flagging for balance work: because a revived segment sits at 25 HP while its siblings
sit at 40–52, **the cheapest correct line is usually to bring all three low and then finish, not to
kill sequentially** — an unavoidable execute-window puzzle rather than a damage race.

## 4. Numbers

Per-segment, single player:

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 40–46 | 46–52 | — |
| Writhe | 5 × 2 (= 10) | — | 6 × 2 (= 12) |
| Bulk | 6 + 2 Strength (self) | — | 7 + 2 Strength (self) |
| Constrict | 8 + 1 Weak | — | 9 + 1 Weak |
| Reattach heal | 25 | — | — |

- **No Block.** No segment ever gains Block, so the enemy-Block multiplayer scaler never applies here.
- **HP assignment is deliberately unique per segment.** On entering the room each segment rounds its
  rolled HP up to an even number and then walks upward in steps of 2 until no teammate shares that
  value, wrapping back to the bottom of the band if it passes the top. Practical consequence: the three
  segments always have *distinct, even* max HP inside the band, so the player can tell them apart by
  HP bar — and the spread between them is small (a few points), which is what makes the simultaneous-
  kill plan viable at all.
- **Strength is per-segment and cumulative.** Each segment Bulks once every three turns for +2, and
  that Strength is never removed — not by its own death and revive. Writhe is the multiplier: a
  segment's two-hit move gains **+2 per point of Strength**, so a segment that has Bulked twice writhes
  for 9 × 2 instead of 5 × 2.
- **Trio damage per turn, single player, ascension 0** (one of each move, since the segments are
  phase-offset): 10 (Writhe) + 6 (Bulk) + 8 (Constrict) = **24 raw**, before Strength and before Weak.
  Weak arrives every turn from whichever segment is on Constrict, so the party is effectively under
  permanent Weak upkeep pressure. By turn 4 each segment has +2 Strength, pushing the round to
  roughly 32; by turn 7, roughly 40.

## 5. Scaling

**By act:** none. It is Act 2 only and has no act-conditional stats. (Act index does enter the
multiplayer formula — see below.)

**By ascension:** two levers, both flat. Tough Enemies moves the whole HP band up 6 (40–46 → 46–52).
Deadly Enemies adds +1 to each attack — critically, Writhe is two hits, so Deadly Enemies is worth
**+2 per Writhe**, and it is worth more still once Strength is stacked. Nothing changes the Reattach
heal, the +2 Strength per Bulk, or the 1 Weak.

**By seat count (multiplayer):**

- HP uses the shared formula — base × player count × act factor, with the **Act 2 non-boss factor 1.2**:

| Players | Per-segment HP band | Trio total (approx) |
|---|---|---|
| 1 | 40–46 | 120–138 |
| 2 | ~96–110 | ~288–331 |
| 3 | ~144–166 | ~432–497 |
| 4 | ~192–221 | ~576–662 |

- **The Reattach heal scales too** (the buff is explicitly marked as multiplayer-scaling): 25 × players
  × 1.2 — roughly 60 at 2 players, 90 at 3, 120 at 4. It scales with the same multiplier as HP, so the
  revive returns the segment to a *constant fraction* (~55%) of its max HP at every seat count. The
  execute window does not get more forgiving in co-op.
- **Attack damage does not scale, but it is table-wide.** Every segment attack targets all opponents,
  so each seat individually takes the full 24-raw round; aggregate incoming damage rises linearly with
  seat count while HP rises super-linearly. Weak likewise lands on every seat every turn.
- The unique-HP walk runs against the multiplayer-scaled band, so the three segments stay distinct at
  any seat count.

## 6. Proposed fight class — `mixed`

Per turn, the fight makes two unrelated demands simultaneously. The first is ordinary grind: three
bodies, no Block, a fixed and fully readable 24-and-climbing round of damage plus permanent Weak
upkeep, with self-stacking Strength as a soft clock — that half reads as pure `attrition`. The second
is a hard rule the damage numbers say nothing about: kills do not stick unless all three land inside
one revive window, so the player must hold three separate HP pools low and then execute them together,
and any single-target focus plan is actively punished by a scaled 25-HP heal — that half reads as pure
`gimmick`. Neither half dominates the other; a deck that can only grind loses to the reattach rule and
a deck that can only burst one target loses to the Strength ramp. For Track B this should be modeled as
an **attrition baseline with a multi-target execute gate layered on top** — its demand curve is a
sustained AoE-damage floor for the first N turns and then a spike requirement of roughly three times
the per-segment remaining HP in one turn, not as a swarm (only three bodies, each individually
significant) and not as a spike (the ramp is slow and telegraphed, with no single burst turn to survive).
