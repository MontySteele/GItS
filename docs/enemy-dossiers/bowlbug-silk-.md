# Bowlbug (Silk)

- **Class:** `BowlbugSilk`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1)
- **Encounters:** `BowlbugsNormal` (as one of two randomly drawn "worker" bugs), `SlumberingBeetleNormal` (fixed middle slot)
- **Fight class:** **attrition**

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of observed mechanics and constants, per the IP rule used for the DLL card extraction.

## Where it shows up

The Silk bowlbug is never a solo encounter — it is always a support body in a three-monster Act 2
lineup, and both of its encounters are tagged as "Workers" fights.

- **Bowlbugs (normal).** The lineup is always Bowlbug (Rock) in the front slot plus **two** workers
  drawn without replacement from {Egg, Silk, Nectar}. Since two of three distinct worker types are
  always taken, the Silk is present in **two thirds** of these encounters, and never as a duplicate.
- **Slumbering Beetle (normal).** A fixed, non-random lineup: Bowlbug (Rock) first, **Bowlbug (Silk)
  second**, Slumbering Beetle third. Here the Silk is guaranteed.

In both cases it shares the screen with Bowlbug (Rock), which is the heavy hitter of the family
(45–48 HP, a 15-damage Headbutt alternating with a self-stun recovery turn). Reading the Silk's
threat in isolation understates it: its whole job is to make the Rock's Headbutt land harder.

## Intent pattern

A strict **two-state alternation** with no randomness, no conditional branches, and no HP-threshold
behavior. The machine has exactly two move states that point at each other, and it **starts on the
debuff state**, so the fight opens with a Weak turn.

| Turn | Intent shown | Move | Effect |
| --- | --- | --- | --- |
| 1 | Debuff | Toxic Spit | Applies 1 Weak to **all** player creatures |
| 2 | Attack (multi-hit, shown as damage x2) | Thrash | 2 hits of 4 damage, each hit re-targeting all opponents |
| 3 | Debuff | Toxic Spit | 1 Weak to all players |
| 4 | Attack x2 | Thrash | 2 x 4 |
| n odd | Debuff | Toxic Spit | — |
| n even | Attack x2 | Thrash | — |

The pattern is fully predictable from turn one and never deviates. Because the debuff comes first,
the Silk's Weak is already on the party when Bowlbug (Rock) takes its first Headbutt turn — the
alternation is phase-locked to make the player's *own* damage worse on the turn they most want to
burst down the Rock.

## Damage / block numbers

| Stat | Base | Ascension-modified |
| --- | --- | --- |
| Starting HP (rolled in range) | 40–43 | 41–44 (Tough Enemies tier) |
| Thrash damage per hit | 4 | 5 (Deadly Enemies tier) |
| Thrash hit count | 2 (fixed) | 2 |
| Thrash total per turn | 8 | 10 |
| Toxic Spit | 1 stack of Weak, all players | unchanged |

- **Block:** none. The Silk never gains Block and has no damage-reduction trait; its 40–43 HP is its
  whole defensive budget. (Its sibling Egg is the one that shields.)
- **Weak in this build** multiplies the *afflicted creature's* powered attack damage by 0.75 (a 25%
  cut) and is a duration counter that ticks down at the end of the enemy turn, so one application
  covers exactly the player's next turn. With the alternating cycle, the party is Weak on every
  other player turn, effectively 50% uptime for a standing ~12.5% damage tax across the fight
  (more if the player's burst turns land on the wrong parity).
- The Spit targets *every* player creature, not a chosen seat.
- Thrash resolves through the standard all-opponents attack path with the target list refreshed
  between the two hits; both hits are ordinary attacks subject to player Block, Vulnerable, and any
  monster Strength/Weak modifiers.
- No summons, no on-death effect, no status-card insertion, no self-buff, no artifact-style
  debuff resistance.

## Gimmicks

One, and it is a *force multiplier* rather than a threat of its own: **the Silk taxes the player's
damage on a fixed clock while a bigger bug does the killing.** Its own 8 (or 10) per-turn output is
low for Act 2 — the fight's actual lethality comes from the Rock's 15-damage Headbutt and, in the
beetle encounter, from the Slumbering Beetle. The Silk's contribution is that every second player
turn is a 25%-reduced-damage turn, which lengthens the fight, which in turn means more Headbutt
turns land. This creates a classic kill-order puzzle:

| Body (Bowlbugs normal) | HP band (base) | Per-turn threat | Role |
| --- | --- | --- | --- |
| Bowlbug (Rock) | 45–48 | 15 Headbutt, alternating with a self-stun turn | damage source |
| Bowlbug (Silk) | 40–43 | 8 (2 x 4) + Weak on all players every other turn | damage tax / fight lengthener |
| Bowlbug (Egg) | 21–22 | 7 damage + 7 Block on the same turn | durable chip |
| Bowlbug (Nectar) | 35–38 | 3, 3, then a buff turn | buffer |

Killing the Silk first is a real temptation (it removes the Weak tax and shortens everything after)
but it costs the player 40+ HP of removal aimed away from the Rock, during turns where the Weak is
still active. Killing the Rock first means eating more Weak turns but stops the big number sooner.
The Silk exists to make that choice non-obvious.

Also worth noting for anyone porting the feel: the spit is *aimed* — the visual leans the bug toward
the leftmost player creature — but the mechanical application is party-wide, so the aiming is pure
telegraph flavor and should not be read as single-target.

## Scaling by act / ascension

- **Act:** no act scaling. Act 2 only; there is no Act 1 or Act 3 appearance, no elite variant, and
  no boss cameo. (The "Silk" name is a skin/variant of the shared bowlbug rig — the Rock, Egg, and
  Nectar bugs are separate models with their own numbers, not ascension tiers of this one.)
- **Ascension:** two independent step bumps, each gated on a named ascension threshold rather than
  on a numeric level:
  - *Tough Enemies* — HP band shifts 40–43 up to 41–44 (+1 both ends).
  - *Deadly Enemies* — Thrash goes 4 to 5 per hit, i.e. **8 to 10 total per attack turn (+25%)**,
    since the hit count is fixed at 2.
  Both are one-time step changes; there is no third tier and no per-level ramp. The Weak
  application is **not** ascension-scaled — it stays at 1 stack.
- The damage bump is the meaningful one: at 10 per attack turn the Silk stops being pure chip and
  starts contributing real pressure alongside the Rock's ascended 16 Headbutt.

## Multiplayer / seat count

The Silk's own model reads no player count, but **both of its moves are party-wide**, which makes it
scale badly (for the player) with seat count:

- **Toxic Spit** applies Weak to *every* player creature, so the debuff cost is paid by the whole
  party each odd turn regardless of party size — a 2-seat party takes 2 Weak stacks' worth of value
  from one enemy turn, a 3-seat party takes 3.
- **Thrash** targets all opponents rather than a single seat, and re-picks targets between its two
  hits, so each seat is exposed to the full 2 x 4 (or 2 x 5) rather than the party sharing 8 damage.
  Total party damage per Thrash turn therefore rises roughly linearly with seat count.
- Against that, the shared multiplayer layer scales monster HP by `players x 1.2` in Act 2, so a
  2-player Silk sits around 96–103 HP and a 3-player Silk around 144–155 HP. Enemy Block is scaled
  by the same factor, but the Silk gains no Block, so that half of the multiplayer scaling does
  nothing for it.
- Net: at higher seat counts the Silk gets *relatively* more dangerous than a single-target chipper
  would (its output multiplies with the party while its durability multiplies at the same rate), and
  the "kill the Silk first" line gets more expensive in exact proportion. Co-op parties should
  expect the Weak tax to be the dominant cost, not the 8 damage.

## Proposed fight class: `attrition`

Per turn, this monster asks the player to absorb a small, unavoidable, perfectly predictable bill —
8 to 10 damage on even turns and a 25% damage cut on odd ones — and it never asks for anything
sharper than that. There is no burst to prevent, no ramp racing away, no puzzle mechanic to disarm;
the demand is simply *sustain your clear rate while your clear rate is being throttled*, and its
40–43 HP is deliberately outside single-turn-kill range for most Act 2 decks so that the throttle
stays on for several turns. The Weak alternation is a fight-lengthener aimed at the player's damage
economy rather than a gimmick with its own counterplay, which is why this reads attrition rather than
gimmick. Note the *containing* encounters are closer to `mixed` (the Rock spikes, the Egg shields) —
this label describes the demand the Silk itself contributes.
