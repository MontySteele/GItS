# Enemy Dossier — Exoskeleton

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Exoskeleton`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `ExoskeletonsNormal` (four Exoskeletons, slots `first`/`second`/`third`/`fourth`), `ExoskeletonsWeak` (three, slots `first`/`second`/`third`)
- **Fight class:** `mixed`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A roach. Small HP, small numbers, and two rules that make the fight not small: it enters combat
wearing a **hard damage cap of 9 per damage instance on itself**, and it spends roughly every second
or third turn giving *itself* permanent **+2 Strength**. The encounter is a monoculture — three or
four identical bodies, no support unit, no summoner, no leader.

It has no Block move, no debuff move, no heal, no on-death effect, no summon, and no low-HP behavior
change. The entire fight is: many bodies you are not allowed to one-shot, all of them getting
stronger on a clock.

## 2. Intent pattern / AI

Three moves and two branch nodes. The branch that matters is an entry conditional keyed to the
**slot the body occupies**, which is what staggers the group.

| Move | Intent shown | Effect |
|---|---|---|
| Skitter | multi-attack, 1 × 3 | Three separate 1-damage hits (single attack animation, played once). |
| Mandibles | single attack, 8 | One heavy bite. |
| Enrage | buff | Applies **+2 Strength to itself**, permanently. Deals no damage. |

**Opening move is decided by slot** (deterministic, no RNG):

| Slot | Turn-1 move |
|---|---|
| `first` | Skitter |
| `second` | Mandibles |
| `third` | Enrage |
| `fourth` | random Skitter / Mandibles, 50/50 |

**Follow-up rules** are fixed per move:

- Skitter → random branch
- Mandibles → **always Enrage**
- Enrage → random branch

The random branch offers Skitter or Mandibles at equal weight, each flagged *cannot repeat*, which in
this state machine means "not the move I logged last turn." Because the branch is only ever reached
directly after a Skitter or an Enrage, the practical consequences are:

- After a **Skitter**, the branch cannot pick Skitter again, so **Mandibles is forced**.
- After an **Enrage**, the last logged move was Enrage, so both attacks are live — a true 50/50.

That collapses the whole AI into two loops:

- **3-beat loop:** Skitter → Mandibles → Enrage → (50%) …
- **2-beat loop:** Mandibles → Enrage → (50%) …

with a coin flip after every Enrage deciding which loop runs next. Consequences worth having on hand:

- **Skitter never repeats, and Mandibles never repeats** — attacks always alternate types.
- **Every Enrage is preceded by a Mandibles**, and every Mandibles is followed by an Enrage. The buff
  turn is always telegraphed one turn early by the heavy-bite intent.
- Each body Enrages every 2–3 turns, expected cadence **+2 Strength per 2.5 turns ≈ +0.8 Str/turn**,
  unbounded, for the whole fight.
- A body only skips damage on its Enrage turn, so a body contributes an attack on ~60–67% of turns.

In `ExoskeletonsWeak` all three openers are deterministic (Skitter / Mandibles / Enrage), so turn 1 of
that fight is exactly 3 + 8 = **11 damage while the third body buffs**. In `ExoskeletonsNormal` the
fourth body adds 3 or 8 on top, i.e. **14 or 19** on turn 1.

## 3. Gimmicks

**Hard To Kill 9 — the defining rule.** Applied to itself on room entry, at amount 9, and never
decremented or removed by anything. It functions as a **per-damage-instance cap**: any single
instance of damage aimed at this creature is clamped to at most 9 before it lands, and the power
flashes when it bites. It is not a shield, not a counter that burns down, and not a percentage — it
is a ceiling that is in force from turn 1 to death.

What that costs the player:

- A 24–28 HP body needs **at least 3 damage instances** to die no matter what you hit it with. A
  four-body room therefore needs **≥12 landed instances** minimum.
- Single-big-hit builds are throttled hardest: a 40-damage strike is a 9-damage strike here, and the
  overkill is simply deleted.
- Wide, small, repeated damage is *rewarded* — an AoE that hits all four for 7 loses nothing to the
  cap while a single 30 loses 21. The cap pushes the answer toward the same tooling the bodycount
  already wanted.
- It caps instances, not turns: multi-hit cards are unaffected per hit, so hit-count is the currency
  this fight trades in, not damage-per-card.

**Self-Enrage stacking, and the Skitter crossover.** Strength adds per hit, so the 1 × 3 move scales
three times as fast as the 8-damage move. The "chip" attack becomes the killing attack almost
immediately:

| Strength | Skitter total | Mandibles |
|---|---|---|
| 0 | 3 | 8 |
| 2 | 9 | 10 |
| 4 | 15 | 12 |
| 6 | 21 | 14 |
| 8 | 27 | 16 |

Skitter overtakes Mandibles at the **first** Enrage and runs away from it thereafter. Any read of the
threat that treats the multi-attack as the harmless intent is wrong after turn ~3.

Two secondary notes: the multi-hit shape means Block absorbs Skitter efficiently at low Strength but
not at high, and any per-hit retaliation the player has (thorns-likes) gets triple value against it —
which also means the damage cap applies to that retaliation per hit, and 1-per-hit retaliation is
nowhere near the 9 ceiling, so it is uncapped in practice.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 24–28 | 25–29 | — |
| Skitter | 1 × 3 hits = 3 | — | 1 × **4** hits = 4 |
| Mandibles | 8 | — | **9** |
| Enrage | +2 Strength (self) | — | — |
| Damage cap on self | 9 per instance | — | — |

- HP is rolled inclusively from the band; the encounter's unique-HP pass hands each body a distinct
  roll where the band is wide enough (5 values, 4 bodies — all four are distinct in the normal
  encounter).
- It never gains Block, so the enemy-Block multiplayer scaler never touches it.
- Whole-room output, `ExoskeletonsNormal`, expected damage per turn with all four alive: **~15 at
  Strength 0**, rising to **~30 around the 6th turn** (all four at roughly +4 Str), and continuing to
  climb by ~+3.5 per turn thereafter for as long as the room is alive.
- Worst-case burst: four bodies happening to land on Mandibles together at +6 Str is **56** in one
  turn; four Skitters at +6 Str is **84**. Neither is likely, both are reachable.

## 5. Scaling

**By act:** none. Act 2 only, no act-conditional stats.

**By ascension:** two flat levers, and they hit different halves of the fight.

- *Tough Enemies* moves the HP band up by 1 at both ends (24–28 → 25–29). Small in isolation, but
  under a 9 cap it is the difference between a 3-instance kill and a 4-instance kill on the high
  rolls — the ascension effectively buys a whole extra required hit on some bodies.
- *Deadly Enemies* adds a **fourth Skitter hit** and takes Mandibles from 8 to 9. The extra Skitter
  hit is the real one: it makes the multi-attack scale +4 per Strength point instead of +3, so at
  +6 Str the move is 28 instead of 21, and the whole late-fight damage curve steepens by a third.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 2 non-boss factor
  being **1.2**.

| Players | Effective HP band (base roll) | Minimum damage instances per body (cap 9) |
|---|---|---|
| 1 | 24–28 | 3 |
| 2 | ~57–67 | 7–8 |
| 3 | ~86–100 | 10–12 |
| 4 | ~115–134 | 13–15 |

- **The damage cap does not scale with seats.** This is the single most important co-op fact in the
  dossier: HP goes up 2.4×/3.6×/4.8× while the ceiling stays at 9, so the required number of landed
  hits per body multiplies with the table. A four-body room at two seats needs roughly **30 capped
  instances** to clear.
- Attacks are delivered against **all opposing seats** — each player takes the Skitter or Mandibles
  independently and blocks it independently. Per-seat incoming pressure is therefore *unchanged* by
  seat count while total enemy HP multiplies, which means the fight lasts far longer and the Strength
  ramp gets far more turns to compound. The co-op version is not an easier version of the fight; it
  is the same per-turn pressure applied over two to three times as many turns, against a ramp with no
  ceiling.
- Enrage is self-targeted and has no seat term. The cap amount has no seat term. Neither move's
  damage has a seat term.

## 6. Proposed fight class — `mixed`

Three different demands stack here and none of them dominates: the bodycount asks for wide AoE (a
`swarm` demand), the 9-per-instance cap asks you to deliver damage as *many hits* rather than big
ones and invalidates burst tooling outright (a `gimmick` demand), and the unbounded +2 Strength every
2–3 turns per body turns any slow clear into a race you lose (a `spike`/`attrition` demand). The
per-turn ask visibly changes shape mid-fight: turns 1–3 want throughput and almost no Block (~15
incoming, spread thin), while turns 5+ want serious Block *and* still want throughput, because
bodies you failed to remove are now hitting for 15–21 each. For Track B, model this as a
**front-loaded swarm curve with a steep, uncapped late slope and a hard per-instance damage ceiling**
— the counterplay is early wide damage plus focus-fire to remove Enrage sources, not out-blocking,
and any deck whose damage arrives in few large packets should be scored as failing this fight
regardless of its raw damage total.
