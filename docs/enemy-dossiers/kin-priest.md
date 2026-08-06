# Kin Priest

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `KinPriest`
- **Kind:** boss
- **Act:** 1 (Overgrowth, act index 0)
- **Encounter:** `TheKinBoss` — three-creature spawn (2× `KinFollower` + 1× `KinPriest`), boss room, custom BGM `act1_boss_the_kin`, custom background, camera pulled to 0.85× and nudged down 50px
- **Fight class:** **swarm**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

Third and last of the three Act 1 bosses in the act's boss discovery order (after Vantom and the
Ceremonial Beast). The Kin Priest never appears alone: the encounter always generates exactly three
creatures into the slots `slot1`, `slot2`, `leaderSlot` — two Kin Followers flanking the Priest,
who occupies the leader slot. There are no summons, no reinforcements, and no respawns; the three
bodies you see on turn 1 are the whole fight. Take-damage sound family is "fur" for both the Priest
and the Followers.

Cosmetic-only: each Follower rolls one of three hair skins at spawn, and the run music carries a
custom parameter track that is bumped when a Follower dies and set to its terminal value when the
Priest dies. Neither has any mechanical effect.

## Structure: a leader with a kill switch and two independent engines

There are **no phases, no HP thresholds, and no randomness anywhere in this fight**. All three
creatures run fixed, hard-pointed move cycles that loop forever. Once you know the three cycles you
know every intent for the rest of the fight.

The one structural rule that dominates everything else:

> **The Priest is the only primary enemy. Both Followers carry the Minion power, which marks them
> as secondary enemies — and a secondary enemy dies automatically the instant no living primary
> enemy remains.** Killing the Priest therefore ends the fight immediately, wherever the Followers'
> health bars happen to be.

The reverse is not true and is worth stating explicitly, because it is the shape a lot of bosses
have and this one does not: **killing both Followers does nothing mechanically to the Priest.** It
does not enrage, buff, heal, re-summon, or change cycle. It plays a one-off spoken line and the
music ticks. Clearing the adds is pure, uncompensated gain.

### The Priest's cycle (4 beats, loops forever, starts on beat 1)

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Orb of Frailty** | Attack 8, then applies **Frail 1 to every player** | attack + debuff |
| 2 | **Orb of Weakness** | Attack 8, then applies **Weak 1 to every player** | attack + debuff |
| 3 | **Soul Beam** | Attack **3 damage × 3 hits** | multi-attack |
| 4 | **Ritual** | Applies **2 Strength to itself**, permanent, uncapped | buff |

Beat 4 loops back to beat 1. The Priest **never blocks and never heals**; it has no defensive move
at all, so every point of player output lands.

The Ritual line of spoken flavor fires only on the first Ritual; subsequent Rituals are silent but
mechanically identical.

### The Followers' cycle (3 beats, loops forever, offset between the two)

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| A | **Quick Slash** | Attack 5 | attack |
| B | **Boomerang** | Attack **2 damage × 2 hits** | multi-attack |
| C | **Power Dance** | Applies **2 Strength to itself**, permanent, uncapped | buff |

The two Followers are deliberately **phase-offset**. The `slot1` Follower is spawned with a flag
that starts it on Power Dance; the `slot2` Follower starts on Quick Slash. So on turn 1 you see
buff / attack / attack across the three enemies, and the two Followers are never on the same beat.
Followers also never block.

## Damage / block numbers

| Stat | Base | Ascension variant |
|---|---|---|
| Priest HP (min = max, no roll) | **190** | **199** at A8 `ToughEnemies` |
| Follower HP (rolled 58–59, distinct per body) | **58 / 59** | **62 / 63** at A8 |
| Orb of Frailty damage | 8 | **9** at A9 `DeadlyEnemies` |
| Orb of Weakness damage | 8 | **9** at A9 |
| Soul Beam damage | 3 × 3 hits | 3 × 3 (**unchanged**) |
| Ritual Strength gain | 2 | **3** at A9 |
| Quick Slash damage | 5 | 5 (**unchanged**) |
| Boomerang damage | 2 × 2 hits | 2 × 2 (**unchanged**) |
| Power Dance Strength gain | 2 | **3** at A9 |
| Block, anywhere in the fight | **none** | none |

Because HP is rolled per-creature from a 2-wide band and the roll excludes values already taken by
teammates, the two Followers reliably end up on **different** HP values (58 and 59; 62 and 63 at
A8). Total enemy HP pool at one seat is therefore **307** base / **324** at A8 — but see the kill
switch: the *winning* damage requirement is only the Priest's **190**.

### Strength is the whole damage curve

Every attack in this fight is small; the numbers on the card are almost irrelevant by turn 6. What
matters is that **all three creatures run their own uncapped Strength engine**, and Strength is
applied per hit:

- Priest **Soul Beam** is 3 hits, so each Ritual is worth **+6 Beam damage**, not +2.
- Follower **Boomerang** is 2 hits, so each Power Dance is worth **+4 Boomerang damage**.
- Nothing in the fight removes, caps, or decays any of it.

Priest damage per 4-beat cycle, with `N` = number of Rituals already resolved:
`(8+2N) + (8+2N) + 3×(3+2N)` = **25 + 10N** base, i.e. 25 → 35 → 45 → 55 per cycle.
At A9 the same expression is `(9+3N) + (9+3N) + 3×(3+3N)` = **27 + 15N**, i.e. 27 → 42 → 57 → 72.

### Turn-by-turn incoming (base, one seat, nothing killed, no mitigation)

| Turn | Priest | `slot1` Follower | `slot2` Follower | Turn total | Cumulative |
|---|---|---|---|---|---|
| 1 | Frailty 8 (+Frail) | Dance (0) | Quick Slash 5 | 13 | 13 |
| 2 | Weakness 8 (+Weak) | Quick Slash 7 | Boomerang 4 | 19 | 32 |
| 3 | Beam 9 | Boomerang 8 | Dance (0) | 17 | 49 |
| 4 | Ritual (0) | Dance (0) | Quick Slash 7 | 7 | 56 |
| 5 | Frailty 10 | Quick Slash 9 | Boomerang 8 | 27 | 83 |
| 6 | Weakness 10 | Boomerang 12 | Dance (0) | 22 | 105 |
| 7 | Beam 15 | Dance (0) | Quick Slash 9 | 24 | 129 |
| 8 | Ritual (0) | Quick Slash 11 | Boomerang 12 | 23 | 152 |
| 9 | Frailty 12 | Boomerang 16 | Dance (0) | 28 | 180 |
| 10 | Weakness 12 | Dance (0) | Quick Slash 11 | 23 | 203 |

Two properties fall out of the table and both matter for modelling:

1. **The Followers are the majority of the damage from turn 5 onward.** By turn 9 they are dealing
   16 of the 28 incoming. A player who ignores them to race the Priest is racing a 190-HP bar while
   the ignored half of the board compounds at +4 and +2 per its own cycle.
2. **The incoming is flat-ish and spread, never spiked.** The largest single hit on the board at
   turn 9 is 16, and it arrives as 2 × 8. There is no turn the fight is trying to kill you with;
   it kills you by arithmetic. A typical Act 1 player at 70–80 HP dies around turn 4–5 unmitigated,
   which is a *normal* Act 1 boss clock, not a fast one.

## Gimmicks

### The kill switch (Minion / secondary-enemy status)

The Followers carry the Minion power, whose only job here is the secondary-enemy flag. When the
last living primary enemy dies, every remaining secondary enemy is killed as part of that death
resolution. In practice:

- **Focusing the Priest is a legal 190-HP win condition** that skips 117 HP of Follower bar.
- **Follower deaths never end the fight**, no matter how many die — they are not the primary enemy,
  so the combat continues with the Priest alone.
- Powers the Followers applied to themselves are irrelevant on death; they buff only themselves.

This creates the fight's one real decision, and it is not a per-turn decision — it is a single
strategic commitment made around turn 2–3: **decapitate, or clear the flanks first.** Decapitation
is faster but leaves you eating full Follower output the entire time; clearing takes ~117 extra HP
of removal (and Follower Strength makes that cost rise if you delay) but flattens the back half of
the damage curve to just `25 + 10N`.

### Frail / Weak cadence

Both orbs apply their debuff to **every player creature**, not to a chosen target, at 1 stack each.
Both are counter-type (they tick down per turn) and both are −25% multipliers: Frail cuts Block
gained, Weak cuts damage dealt. Player-side debuffs skip their first duration tick, so one stack is
live for exactly the player's next turn.

That produces a fixed four-turn texture on the player side, in lockstep with the Priest's cycle:

| Player turn following Priest beat | Tax |
|---|---|
| after beat 1 (Frailty) | **−25% Block** — the turn you most want to defend, you defend worse |
| after beat 2 (Weakness) | **−25% damage** — the turn you most want to push, you push worse |
| after beat 3 (Beam) | clean |
| after beat 4 (Ritual) | clean |

The design intent is legible: you get two clean turns to do real work, and the two clean turns are
the ones where the Priest is doing its *least* damage (Beam turn, and the zero-damage Ritual turn).
Banking a big turn into the post-Ritual slot is the fight's main sequencing lever.

### Multi-hit attacks

Two of the five attack moves are multi-hit (Beam 3×, Boomerang 2×). Combined with the uncapped
Strength engines this means per-hit damage reduction is worth triple/double here, and it means the
fight scales *superlinearly* against flat mitigation as Strength climbs while the raw numbers stay
tiny.

## Scaling

**By act:** none. The Kin exists only in Act 1, and the only act index read anywhere is the shared
multiplayer scaling constant.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | Priest HP 190 → 199; Follower HP 58–59 → 62–63 |
| A9 `DeadlyEnemies` | Orb of Frailty 8 → 9; Orb of Weakness 8 → 9; Ritual Strength 2 → 3; Power Dance Strength 2 → 3 |

Note what A9 does **not** touch: Soul Beam's base 3, Quick Slash's 5, and Boomerang's 2 are all
unchanged. The entire A9 tax is loaded onto the two Strength engines (both +50% per application),
which means ascension changes the *slope* of this fight, not its opening. At A9 the Priest's cycle
damage climbs at +15 per cycle instead of +10 and each Follower at +6 instead of +4 — so a slow
clear is punished far harder at high ascension than a slow start is.

**By seat count (multiplayer):**

- **HP** uses the standard formula: base × players × 1.1 (the Act 1 multiplier; Act 1 has no
  separate boss rate).

| Players | Priest HP | Follower HP (each) | Total pool |
|---|---|---|---|
| 1 | 190 | 58 / 59 | 307 |
| 2 | 418 | ≈128 / ≈130 | ≈676 |
| 3 | 627 | ≈191 / ≈195 | ≈1013 |
| 4 | 836 | ≈255 / ≈260 | ≈1351 |

(A8 values scale from 199 and 62/63 by the same factor.)

- **Every attack in this fight hits every seat for full.** All five attack moves are declared
  against the whole opposing side, and there is no random single-seat selection anywhere. So the
  turn-by-turn incoming table above is **per player and seat-count invariant** — four players each
  take the full 28 on turn 9, for 112 party-wide, against a bar that grew 4.4×.
- **Frail and Weak land on every player**, one stack each, unscaled by seat count.
- **Strength does not scale in multiplayer** — the Ritual and Power Dance amounts are flat, so the
  ramp slope per seat is identical at every party size.
- **Enemy Block scaling is irrelevant here** — nothing in this encounter ever blocks.

The net multiplayer shape is unusually harsh for a co-op scaling model: the party's *effective* HP
pool grows linearly with seats while the enemy's grows at 1.1× per seat on top, and the incoming
damage per seat does not thin out at all. Whatever the party's damage multiplier is, it has to beat
4.4× on the HP side at four seats while each individual seat still needs the same per-turn block it
needed solo. The kill-switch shortcut becomes correspondingly more attractive at high seat counts:
at four players, decapitation skips ≈515 HP of Follower bar.

## Proposed fight class: **swarm**

Three separate bodies act every turn, all of them attacking from turn 1, and each running its own
independent uncapped Strength engine — so the per-turn demand is **broad, repeated mitigation
against many small hits plus enough throughput to trim 117 HP of side bar before it compounds**,
which is the swarm curve rather than the boss curve. Nothing here asks the player to survive a
turn: the biggest hit on the board through turn 10 is 16 damage delivered as two ticks, so it is
not **spike**; and the Priest never blocks over a modest 190-HP bar with the fight capped at roughly
eight to ten turns, so it is not **attrition** either. The one genuinely puzzle-shaped element — the
Minion kill switch that ends the fight the moment the Priest dies — is a strategic escape hatch
rather than a per-turn requirement, so it modifies the swarm curve rather than replacing it, and
it is the reason this is not labelled **gimmick** or **mixed**. For Track B, model it as a swarm
whose add-clear value has a hard opt-out: demand = per-turn AoE mitigation against 3 sources with
a +10/cycle (base) or +15/cycle (A9) ramp, and a branch point where sufficient single-target burst
on the leader collapses the remaining enemy HP requirement to zero.
