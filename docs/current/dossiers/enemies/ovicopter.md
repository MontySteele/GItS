# Enemy Dossier — Ovicopter

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Ovicopter`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `OvicopterNormal` (one Ovicopter, alone at spawn, plus five reserved egg slots)
- **Fight class:** `swarm`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A fat, hovering egg-layer that opens the fight alone and then fills the room. The encounter reserves
**six slots** — `egg1`–`egg5` plus the `ovicopter` slot — but generates only the Ovicopter itself, so
the entire rest of the board is something the enemy builds during the fight out of **Tough Eggs**.

The Ovicopter's own offence is modest and completely fixed: one big hit, one small hit with
Vulnerable, and a third turn spent either laying or buffing. All of the fight's actual pressure comes
from how many eggs are on the board and what you chose to do about them.

## 2. Intent pattern / AI

**Fully deterministic** — no RNG is consulted anywhere in the move machine. A three-beat cycle with a
single conditional slot at the top:

| Beat | State | Intent shown | Effect |
|---|---|---|---|
| 1 | `LAY_EGGS_MOVE` *or* `NUTRITIONAL_PASTE_MOVE` | Summon *or* Buff | Lay up to 3 Tough Eggs, **or** give itself +3 Strength |
| 2 | `SMASH_MOVE` | attack, 16 | 16 damage to its target |
| 3 | `TENDERIZER_MOVE` | attack 7 + debuff | 7 damage to its target, then **Vulnerable 2** on it |

Flow: it **opens on Lay Eggs**, then Smash, then Tenderizer, then hits the branch and returns to beat
1 — forever. The branch is the only decision the enemy ever makes:

- **`CanLay`** — true when the Ovicopter has **3 or fewer living teammates** (i.e. 3 or fewer eggs /
  hatchlings still on the board).
- If `CanLay` → **Lay Eggs**. If not → **Nutritional Paste** (+3 Strength to itself, permanent and
  stacking).

So the branch is a *valve that inverts the obvious play*: clear the field aggressively and the
Ovicopter keeps refilling it every third turn; leave four or five bodies alive and it stops laying but
starts compounding its own damage by +3 every third turn instead. There is no way to make it do
nothing.

**Bestiary note:** `TENDERIZER_MOVE` is deliberately hidden from the bestiary listing. The Vulnerable
beat is meant to be learned in the room, not read beforehand.

**Laying details.** Each lay attempts **three** eggs, one at a time, into whichever egg slot is
currently unoccupied — taking the *last* free slot each time, so the field fills backwards from
`egg5`. With five slots total, a lay from an empty board produces 3 eggs; a lay with 3 already alive
produces only 2 (slot-capped). Every laid egg gets **Minion** status, which marks it a secondary
enemy and, importantly, means **killing the Ovicopter does not kill the eggs** — they are not fatal-
linked to their parent and the fight continues until every body is down.

## 3. The eggs (Tough Egg / Hatchling)

The summon is a two-stage body, and it is the reason the fight has a clock at all.

| Stage | HP band | Behavior |
|---|---|---|
| Tough Egg | 14–18 | Inert. Shows a Summon intent and a hatch countdown; deals no damage. |
| Hatchling | 19–22 (**re-rolled and re-scaled** on hatch) | Attacks for **4** every single turn, forever. |

- A freshly laid egg carries a hatch counter of **2** (laid during the enemy phase; an egg placed
  outside the enemy phase gets 1 instead), ticking down at the end of each enemy phase. In practice
  the egg **hatches on its next action**, i.e. the enemy turn after the one it was laid on.
- On hatching it clears every power it carries **except** Minion — so any Poison, Vulnerable, Weak or
  other debuff you invested into the egg shell is **wiped**, and its HP is replaced with a fresh
  Hatchling roll rather than being carried over. **Chip damage into an unhatched egg is refunded to
  the enemy.** Eggs must be killed *outright* before they hatch or the investment is lost.
- Hatchlings never do anything but nibble. There is no second escalation stage.

Practical consequence: an egg is a 14–18 HP object with a one-turn fuse, and a hatchling is a 19–22 HP
object generating 4 damage per turn in perpetuity. A full board of five hatchlings is **20 incoming
damage per turn** on top of the parent.

## 4. Interaction between the pieces

The Tenderizer's Vulnerable has a specific and easily-misread window. Vulnerable ticks down at the end
of the **enemy** phase, so the 2 stacks applied on beat 3 cover exactly **beat 1 of the next cycle** —
the Lay/Paste turn, on which the Ovicopter itself does not attack. The Vulnerable therefore does
almost nothing for the Smash (which arrives on beat 2, after it has expired) and instead exists to
**amplify the hatchling swarm by 1.5×** on the summon turn. With a full board that converts a 20-
damage nibble turn into 30. The debuff is a swarm multiplier wearing an attack's clothing.

The two halves of the branch also trade against each other over time:

- Play the "kill everything" line and you take Smash + Tenderizer + a 1.5×-boosted nibble turn from
  whatever hatched, every three turns, forever, and the Ovicopter never gains Strength.
- Play the "starve the valve" line (hold 4–5 bodies alive) and you take a much larger flat nibble
  load *plus* an Ovicopter whose Smash climbs 16 → 19 → 22 → 25 and whose Tenderizer climbs
  7 → 10 → 13 → 16 across successive cycles.

Neither line is free; the fight is asking which of the two costs your deck is better shaped to pay.

## 5. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| Ovicopter HP roll | 124–130 | 126–132 | — |
| Smash | 16 | — | 17 |
| Tenderizer | 7 (+ Vulnerable 2) | — | 8 (+ Vulnerable 2) |
| Nutritional Paste | +3 Strength (self) | — | +4 Strength |
| Eggs per lay | 3 (slot-capped at 5 on board) | — | — |
| Tough Egg HP | 14–18 | 15–19 | — |
| Hatchling HP | 19–22 | 20–23 | — |
| Hatchling Nibble | 4 | — | 5 |

- Strength stacks are permanent and additive onto both Smash and Tenderizer; nothing removes them.
- The Ovicopter never gains Block, so the enemy-Block multiplayer scaler never touches this fight.
- Steady-state parent output alone is **~7.7 damage/turn** averaged over the 3-turn cycle at base,
  before Strength. The swarm is where the real damage lives.

## 6. Scaling

**By act:** none. Act 2 only, no act-conditional stats.

**By ascension:** three flat levers, all small. Tough Enemies moves the Ovicopter's HP band up 2 at
both ends and every egg/hatchling band up 1. Deadly Enemies raises Smash 16→17, Tenderizer 7→8,
Nibble 4→5, and — the one that actually matters — **Paste 3→4 Strength**, which makes the
starve-the-valve line escalate a third faster.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 2 non-boss factor
  being **1.2**. This applies to the Ovicopter and to every egg on spawn, and again to the Hatchling
  roll at hatch time.

| Players | Ovicopter HP band | Egg HP band | Hatchling HP band |
|---|---|---|---|
| 1 | 124–130 | 14–18 | 19–22 |
| 2 | ~298–312 | ~34–43 | ~46–53 |
| 3 | ~446–468 | ~50–65 | ~68–79 |
| 4 | ~595–624 | ~67–86 | ~91–106 |

- **No move in this kit scales with seat count.** Smash, Tenderizer, Paste, the eggs-per-lay count of
  3 and the five-slot cap are all flat. The board never gets wider in co-op; it only gets tougher.
- Because eggs are the thing you must kill *inside a one-turn fuse*, and their HP triples at three
  seats while the fuse stays one turn, **co-op tips the fight hard toward the starve-the-valve line by
  force** — a two-seat egg at ~34–43 HP is frequently not killable before it hatches, so the board
  fills, `CanLay` goes false, and the Ovicopter simply farms Strength instead.
- Both attacks are single-target, so per-seat damage pressure from the parent falls off with table
  size while the total hatchling nibble load stays constant and gets split.

## 7. Proposed fight class — `swarm`

Per turn this fight asks for **multi-target throughput on a one-turn deadline**: three fresh 14–18 HP
bodies land every third turn, each with a single turn before it converts into a permanent 4-damage-
per-turn attacker whose shell wiped your chip damage and debuffs. That per-turn demand — "can you kill
N small things right now, not eventually" — is the defining ask, and the parent's flat 16/7 is a
sideshow you block through while doing it. It is not `spike` (nothing ever threatens a lethal turn),
not `attrition` (the HP pool is large but the fight is decided by board count, not by grinding), and
not `gimmick` in the puzzle sense, though the `CanLay` valve is a genuine gimmick rider: the anti-
swarm answer is *also* the thing that switches the Ovicopter onto an unbounded Strength ramp, so
Track B should model this as a swarm whose **suppression is priced** rather than one you can simply
out-clear. The runner-up label is `mixed`, on the strength of that valve; `swarm` wins because at
every single decision point the player is being asked how much simultaneous damage they can point at
how many bodies.
