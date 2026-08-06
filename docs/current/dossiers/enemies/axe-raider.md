# Enemy Dossier — Axe Raider

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `AxeRubyRaider`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act whose encounter pool contains the Ruby Raiders fight
- **Encounter:** `RubyRaidersNormal` (a normal-monster room; also force-placed at normal-encounter index 5 of the act's discovery order)
- **Fight class:** `spike`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table description of the constants and mechanics.

---

## 1. Where it appears

Axe Raider is one of five interchangeable Ruby Raider bodies (Axe, Assassin, Brute, Crossbow,
Tracker). The Ruby Raiders encounter always fields **exactly three** raiders, drawn from the pool
of five *without replacement* — every raider is capped at one copy per fight. So Axe Raider is
present in the fight roughly 3-in-5 of the time, and never appears twice.

It is a plain melee body: no minion status, no summoning, no on-death effect, no aura on its
allies. Everything below concerns its own turn only. (Notably, the Brute's self-buff in the same
encounter is *self*-targeted, so it never inflates Axe Raider's numbers.)

## 2. Intent pattern / AI

The move machine is **fully deterministic — no RNG, no conditional branches, no HP-threshold
transitions.** It is a three-state ring, and it always starts on the first state:

| Turn in cycle | Move | Intent shown |
|---|---|---|
| 1 | Swing | Attack + Defend (two icons on one intent) |
| 2 | Swing (identical) | Attack + Defend |
| 3 | Big Swing | Attack only |
| then | back to turn 1 | — |

The first and second turns are two separate states running the *same* move; the duplication exists
purely to count out "two small turns before the big one." Both are hidden from the bestiary entry —
the bestiary lists only Big Swing — so a player reading the compendium sees the payoff move but not
the ramp.

Practical consequences:

- The pattern is **readable from turn one and never deviates.** A player who has seen the fight
  once knows the big hit lands on turns 3, 6, 9, … with no variance to hedge against.
- Because the machine is not allowed to leave a move state until that move has been performed at
  least once, there is no way to skip or double the Big Swing via stuns/skips that merely delay a
  turn — a lost enemy turn shifts the cycle rather than scrambling it.
- Its Block arrives **on the same turn as its attack**, gained after the attack resolves. There is
  no dedicated defend turn to punish.

## 3. Numbers

| Stat | Base | Ascension variant |
|---|---|---|
| Starting HP | 20–22 (rolled) | 21–23 with the *Tough Enemies* ascension |
| Swing damage | 5 | 6 with *Deadly Enemies* |
| Swing block (self) | 5 | 6 with *Deadly Enemies* |
| Big Swing damage | 12 | 13 with *Deadly Enemies* |

Derived, per full three-turn cycle (single player):

| | Base | Deadly Enemies |
|---|---|---|
| Damage dealt | 22 | 25 |
| Block gained | 10 | 12 |
| Effective HP if the block is never overkilled | ~30–32 | ~33–35 |

HP is rolled uniquely against the other enemies already placed on its side, so within its own
20–22 band it simply takes an unused value from that range.

## 4. Scaling

**By act:** none. The model has no act-varying stats and the encounter only exists in Act 1, so
there is nothing to model cross-act.

**By ascension:** two independent bumps, both flat and both small.
- *Tough Enemies* raises the HP band by exactly 1 at both ends (20–22 → 21–23).
- *Deadly Enemies* raises Swing damage 5→6, Swing block 5→6, and Big Swing 12→13.
There are no ascension-added moves, no cycle changes, and no extra bodies in the encounter.

**By seat count (multiplayer):** two separate multipliers apply, and both use the Act 1 factor of
**1.1**.

1. **HP** is multiplied by `players × 1.1` when there is more than one player.

   | Players | HP band |
   |---|---|
   | 1 | 20–22 (unscaled) |
   | 2 | ~44–48 |
   | 3 | ~66–73 |
   | 4 | ~88–97 |

2. **Block** gained by a monster move is multiplied by the same `players × 1.1`, because it
   qualifies as monster-move block and Axe Raider is a primary enemy (it is not a minion/illusion,
   so it is never excluded from the scaling). At 2 players its 5 Block becomes 11; at 4 players, 22
   — i.e. a 4-player table faces a body that reapplies more than a full turn's worth of a starter
   Defend on two turns out of every three.

3. **Damage is *not* divided among seats.** Its attack resolves against *every* opposing creature,
   so each hero eats the full 5 or 12. Total table-wide damage output therefore scales linearly
   with seat count on top of the HP/Block scaling, which makes the Big Swing turn the sharpest
   part of the fight in co-op rather than the most diluted.

## 5. Proposed fight class — `spike`

Reasoning from what the fight demands per turn: two cheap 5s followed by a telegraphed 12 is a
demand curve with a hard peak, and the peak is roughly 55% of Axe Raider's own maximum HP in a
single hit — the player must either hold defence for the third turn or kill the body before it
arrives. The self-Block layer is what makes that a real decision instead of a formality: it eats
small chip attacks, so "kill it before the swing" costs a genuine burst rather than two Strikes,
and in co-op the same block scales to 11–22 per application while the 12 keeps landing on every
seat at full value. It is not `attrition` (the fight is short, only 20-odd HP of body, and the
pressure is concentrated rather than steady), not `swarm` at the individual level (one body, no
summons — the *encounter* around it is a three-body swarm, which Track B should model at the
encounter layer, not here), and not `gimmick` (nothing unusual happens; the pattern is a plain
ramp). For the demand curve, treat it as a **3-turn sawtooth: two low-demand turns for setup,
then a burst-or-block check**, with a modest anti-chip tax attached to the low turns.
