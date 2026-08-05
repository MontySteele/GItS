# Enemy Dossier — Decimillipede (Front Segment)

- **Class:** `DecimillipedeSegmentFront`
- **Kind:** elite
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `DecimillipedeElite` (three segments: Front, Middle, Back, in slots `segment1/2/3`)
- **Fight class:** `mixed`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Front Segment is one third of a single elite creature that the engine models as three separate
bodies sharing one abstract behavior class. **The Front subclass contains no logic of its own** — it
exists only to bind the shared segment behavior to the correct visual scene and to shake the right
rig node when the body attacks. Front, Middle and Back are mechanically identical; they differ only
in which sprite drivers shake (Middle shakes two, Front and Back one each) and in which phase of the
move cycle they start on.

Everything worth knowing therefore lives in the shared segment behavior, and this dossier describes
that. The interesting part is not any one move — the moves are a plain three-beat attack rotation —
but the **Reattach** rule that makes the three bodies a single kill.

## 2. Intent pattern / AI

Each segment runs a **fully deterministic three-move loop** with no RNG once the fight starts:

> Writhe → Constrict → Bulk → Writhe → …

| State | Intent shown | Effect |
|---|---|---|
| `WRITHE_MOVE` | multi-attack, 5 × 2 | Two attack hits of 5 (blunt hit fx, triple-attack sfx). |
| `CONSTRICT_MOVE` | attack + debuff, 8 | One hit of 8, then **1 Weak** on its target. |
| `BULK_MOVE` | attack + buff, 6 | One hit of 6, then **+2 Strength on itself** (permanent). |
| `DEAD_MOVE` | *(no intent)* | Does nothing. Only entered by dying — see §3. |
| `REATTACH_MOVE` | heal | Heals itself **25** and returns to the fight. Must resolve once before the machine can move on. |

The encounter, not the monster, sets the **starting phase**: it rolls one index for the Front Segment
and gives Middle and Back that index +1 and +2. The three bodies are therefore permanently offset by
one beat, which means **every single turn the party eats exactly one Writhe, one Constrict and one
Bulk** — one of each, forever, until a body goes down. There is no turn where the trio doubles up on
a move and no turn where a move is missing.

After a Reattach the segment does *not* resume where it left off: it drops into a random branch that
picks Writhe / Constrict / Bulk with equal weight and a no-immediate-repeat rule, then continues the
fixed loop from there. **Reviving is the only thing that can desynchronize the three bodies**, and it
is the only RNG in the fight after setup.

## 3. Gimmicks

**Reattach (the whole fight).** Every segment enters the room carrying a Reattach power worth 25.
Its effects, in order of how much they change play:

- **A segment cannot be killed while any other segment lives.** Dropping one to 0 does not remove it
  from combat and does not trigger Fatal-keyword effects; the body is forced into the `DEAD_MOVE`
  state instead.
- **While down it is untargetable and unhittable.** The power refuses hits and power applications on
  its owner while reviving, so you cannot chip it, pre-stack poison on it, or debuff it. It also
  deals no damage — a downed segment is two turns of relief.
- **Two-beat downtime, then it comes back at 25 HP.** The turn after it falls it shows no intent and
  does nothing; the following turn it shows a **heal** intent and reattaches, healing 25 and becoming
  targetable again. It returns at 25 out of its full bar, not at full.
- **Death strips its powers.** Only Reattach survives the owner's death, so a segment that has been
  bulking all fight **loses its accumulated Strength** when you drop it. Killing a fat segment is a
  real reset of that body's damage curve, not just tempo.
- **The fight ends only when a segment dies while both others are already down.** That is the actual
  win condition: the last standing body must be finished inside the ~2-turn window the other two are
  in the dead state. When that happens all three fade out together.
- Doom-style removal does not make it disappear, and it does not fade after death; the sprite swaps
  to a shriveled variant while down and back to the live variant on reattach — a clean visual tell of
  who is about to return.

**Staggered, unique HP.** On entering the room each segment rounds its rolled max HP up to an even
number and then walks upward in steps of 2 until it does not collide with any teammate's max HP,
wrapping back to the bottom of the band if it overshoots the top. The three bars are therefore always
**distinct even numbers inside the band**, which is what lets you tell them apart and plan a kill
order at all.

**Shared attack animation.** Whichever segment is acting, all segments visibly writhe and a rock vfx
plays over the arena. Cosmetic, but it makes the trio read as one creature and makes per-body intent
tracking harder than it looks.

**No Block, ever.** No segment has a defend move, so the enemy-Block multiplayer scaler never touches
this fight.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP band per segment (min–max) | 40–46 | 46–52 | — |
| Writhe | 5 × 2 hits = 10 | — | 6 × 2 hits = 12 |
| Constrict | 8 + 1 Weak | — | 9 + 1 Weak |
| Bulk | 6 + 2 Strength (self) | — | 7 + 2 Strength (self) |
| Reattach heal | 25 | — | — |
| Strength per Bulk | 2 | — | — |

Because the three bodies are phase-offset, the trio's **per-turn output is the sum of one of each
move**, and one segment gains +2 Strength every turn. Strength adds per hit, so it is worth double on
the Writhe body.

| Turn | Trio damage (base) | Notes |
|---|---|---|
| 1 | 24 | 10 + 6 + 8, one Weak lands |
| 2 | 28 | first +2 Str online |
| 3 | 30 | |
| 4 | 32 | |
| 5 | 36 | |
| 6 | 38 | |
| 7 | 40 | |

That is roughly **+8 damage per three turns (~+2.7/turn), compounding indefinitely**, on top of a
Weak that is reapplied every turn and so is effectively permanent (Weak is a ×0.75 multiplier on the
afflicted attacker's attacks). Deadly Enemies moves the turn-1 figure from 24 to **28** and shifts the
whole curve up by 4.

Total starting HP pool is only about **126–138** (three distinct even values in 40–46), or ~144–150
under Tough Enemies — small for an elite, which is the point: the pool is cheap, the *ordering* is
not, and every failed close-out refunds 25 HP.

## 5. Scaling

**By act:** none beyond Act 2 membership. No act-conditional stats.

**By ascension:** two flat levers, as above. Tough Enemies lifts the HP band by 6 at both ends
(40–46 → 46–52), adding ~18 HP across the trio. Deadly Enemies raises each move by 1 per hit
(Writhe 5→6 per hit, Constrict 8→9, Bulk 6→7). Neither the Strength gain (2) nor the Reattach heal
(25) has an ascension variant.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 2 non-boss factor
  being **1.2**.

| Players | Effective HP band per segment |
|---|---|
| 1 | 40–46 (no scaling at 1 player) |
| 2 | ~96–110 |
| 3 | ~144–166 |
| 4 | ~192–221 |

- *Reattach* is explicitly flagged to scale in multiplayer and uses the same default formula, so the
  heal is 25 × seats × 1.2 — **60 at two seats, 90 at three, 120 at four**. The revive is therefore a
  constant fraction of the segment's bar at every table size; co-op does not make the gimmick softer.
- *Damage* does not scale: Writhe, Constrict and Bulk hit one seat for the same numbers regardless of
  table size. Per-seat incoming pressure falls off sharply as seats are added, and the Weak lands on
  one seat rather than the table.
- The uniqueness-of-HP pass runs against the multiplayer-scaled band, so the segments stay
  distinguishable at every seat count.

Net co-op shape: the damage race relaxes and the fight becomes almost purely a **coordination
puzzle** — three fat bars that must be brought down inside the same short window by parties whose
damage is not centrally controlled.

## 6. Proposed fight class — `mixed`

Per turn this fight makes two different demands at once, and neither is decorative. The first is
ordinary escalating pressure: 24 damage on turn one growing ~+2.7 per turn forever, with a Weak
riding permanently on whoever is being constricted — that half is textbook `attrition` and sets a
hard clock. The second is a kill-condition puzzle that invalidates the standard elite answer:
focus-fire is *punished*, because a segment dropped alone is untargetable for two turns and then
returns with 25 HP (60/90/120 in co-op), so the fight only ends if you level all three bars and then
close two of them plus the last inside a two-turn window. For Track B this should be modeled as an
attrition curve with a **burst gate at the end** — the demand is "sustain ~24–40 incoming while
building a spread-damage board, then produce one oversized multi-target turn" — which is why it is
neither pure `attrition` (a grind deck loses to the refunds) nor pure `gimmick` (a puzzle solution
alone loses to the Strength curve), and not `swarm` despite the three bodies, since they are one
creature with one shared clock.
