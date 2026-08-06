# Enemy Dossier — Chomper

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Chomper`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `ChompersNormal` (two Chompers, phase-offset), `TunnelerNormal` (one Chomper + one Tunneler)
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Chomper is the Hive's status-pollution body: a mid-size chewer with a two-hit bite on one turn and
a screech that dumps dead cards into every player's deck on the next. It carries **Artifact 2** from
the moment it enters the room, so the first two debuffs anyone lands on it are consumed for nothing.

It has no Block move, no buff move, no summon, no on-death effect, no low-HP behavior change, and no
reaction to the death of its partner. Everything it does is on a fixed two-beat clock.

## 2. Intent pattern / AI

Two states, chained head-to-tail, **fully deterministic** — the state machine consults no RNG for this
enemy, so the whole fight is readable from turn 1.

| State | Intent shown | Effect |
|---|---|---|
| `CLAMP_MOVE` | multi-attack, 8 × 2 | Two attack hits of 8 against its target (16 total before Block). |
| `SCREECH_MOVE` | status, 3 cards | Adds 3 **Dazed** to the discard pile of **every player**, with a barked line and a cast animation. |

Flow: Clamp → Screech → Clamp → Screech → … forever. No branch, no interrupt, no escalation.

The only variation is the **starting phase**, which the encounter sets rather than the monster:

- `ChompersNormal` spawns two Chompers and flips one of them to open on Screech. The pair is therefore
  permanently **out of phase**: every single turn of that fight the party eats one Clamp (16) *and*
  one Screech (3 Dazed per seat), and it stays that way until one body dies.
- `TunnelerNormal` spawns its single Chomper on the Screech opening, so turn 1 of that fight is
  status-first and the Tunneler carries the opening damage.

Killing one body in `ChompersNormal` therefore does two things at once: it halves incoming damage
*and* halves the status inflow — the fight's difficulty is very sensitive to focus-fire order, and
there is no reason ever to split damage between the two.

## 3. Gimmicks

**Artifact 2 (on room entry).** Applied to itself before the first turn. It eats the first two
*visible debuff* applications aimed at it, decrementing once per absorbed debuff. Practical effect:
opening Vulnerable/Weak plays are wasted unless you deliberately spend two cheap debuffs to strip the
charges first, and debuff-centric decks lose their first two turns of leverage. Invisible/internal
debuff bookkeeping is not affected — only things the player can see and would care about.

**Dazed flood.** Dazed is a status card, cost-less, **Unplayable** and **Ethereal**. Three copies go
to the *discard* pile per screech, per player, which means they do not clog the current hand — they
arrive on the next shuffle and thereafter dilute draws. Because they are Ethereal, each drawn copy
removes itself at end of turn, so the pollution is self-cleaning *per copy* but the source keeps
refilling every other turn. The tax is on draw quality and on any deck that cares about deck size,
retain, or "cards in hand" counts; it is not a discard-pile-synergy punish (it feeds those).

Note the asymmetry the two moves have in co-op: **Clamp hits one seat, Screech hits all seats.** The
status half of this enemy scales with the table; the damage half does not.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 60–64 | 63–67 | — |
| Clamp | 8 × 2 hits = 16 | — | 9 × 2 hits = 18 |
| Screech | 3 Dazed to each player's discard | — | — |
| Starting Artifact | 2 | — | — |

- HP is rolled inclusively from the band, with the encounter's unique-HP pass nudging bodies apart
  where it can.
- It never gains Block, so the enemy-Block multiplayer scaler never touches it.
- Steady-state single-Chomper output is **8 damage/turn averaged** (16 every other turn) plus 1.5
  Dazed/turn/seat. In `ChompersNormal` the offset pair makes it a flat **16 damage + 3 Dazed every
  turn** while both are alive.

## 5. Scaling

**By act:** none. Act 2 only, no act-conditional stats.

**By ascension:** two flat levers. Tough Enemies moves the HP band up by 3 at both ends (60–64 →
63–67). Deadly Enemies takes each Clamp hit from 8 to 9, i.e. 16 → **18 per clamp turn**, and in the
paired encounter that is 18 incoming every turn. Neither the screech count (3) nor the Artifact count
(2) has an ascension variant.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 2 non-boss factor
  being **1.2**.

| Players | Effective HP band (base roll) |
|---|---|
| 1 | 60–64 (no scaling at 1 player) |
| 2 | ~144–154 |
| 3 | ~216–230 |
| 4 | ~288–307 |

- *Artifact* explicitly scales with the table: the applied amount is 2 + (players − 1), so **3 at two
  seats, 4 at three, 5 at four**. Debuff-stripping gets meaningfully more expensive in co-op, and a
  co-op party has more debuff sources trying to spend into it.
- *Clamp* does not scale — still 8 × 2 against a single target, so per-seat damage pressure falls off
  hard as seats are added.
- *Screech* effectively scales by seat count without any code doing so: the 3 Dazed are delivered to
  every player, so the total garbage created per screech is 3 × seats.

Net co-op shape: the fight converts from a damage race into a long, low-pressure grind where the deck
pollution and the fattened Artifact are the only things still growing.

## 6. Proposed fight class — `attrition`

Per turn this fight asks for something modest and unglamorous — absorb 16 (18 on Deadly Enemies) with
no burst turn to survive and no threshold that pays out — while quietly making your deck worse every
other turn and denying your first two (or, in co-op, up to five) debuff plays outright. Nothing here
spikes: the damage is flat and fully telegraphed, there is no ramping buff, no summon, and no puzzle
state to solve, which rules out `spike` and `gimmick`; two bodies is not a `swarm`, and the two bodies
run the *same* clock offset by one, so there is no second demand type to make it `mixed`. The real
cost is time-shaped — every turn you fail to close adds 3 Dazed per seat and pushes the Artifact tax
further from being worth paying — so for Track B this should be modeled as a **decaying-resource
grind against a large HP pool**, where the demand curve is "sustain 16/turn while your draw quality
degrades linearly," and the correct counterplay is focus-firing one body rather than out-blocking the
pair.
