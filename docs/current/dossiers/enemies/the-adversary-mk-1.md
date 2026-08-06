# The Adversary Mk 1

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `TheAdversaryMkOne`
- **Kind:** boss
- **Act:** unassigned — no encounter model in the build references this monster
- **Encounter:** none (see "Where it appears")
- **Fight class:** **attrition**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

Nothing in the decompiled tree instantiates The Adversary Mk 1 except the global model-type registry
that enumerates every monster class. There is no `*Boss.cs` / `*Elite.cs` / `*Normal.cs` encounter
model for it, no event that spawns it, and no mock encounter that references it. It is registered and
playable but unrouted — reachable only through debug spawning or a future encounter that has not
shipped in this build. Any act assignment for it is therefore a projection, not a fact.

It is the first rung of a three-model ladder that is clearly one design object: **Mk 1 / Mk 2 / Mk 3**
are byte-for-byte the same machine with three tunings. The family reads like the mech-boss analogue of
the Battle Friend V1/V2/V3 dummy ladder — same skeleton, escalating settings — except that unlike the
dummies, the Adversaries actually fight back.

| | HP | Move 1 | Move 2 | Move 3 (barrage) | Strength gain | Artifact on spawn |
|---|---|---|---|---|---|---|
| **Mk 1** | **100** | Smash **12** | Beam **15** | **8 × 2** | **+2** | declared 0 — never applies |
| Mk 2 | 200 | Bash 13 | Flame Beam 16 | 9 × 2 | +3 | 1 |
| Mk 3 | 300 | Crash 15 | Flame Beam 18 | 10 × 2 | +4 | 2 |

## Intent pattern

A fixed three-beat loop with no branching, no RNG, and no reactive states. The move state machine has
exactly three move states wired nose-to-tail in a ring; each state's only successor is the next one,
and the third points back to the first. The machine consults no RNG, no HP threshold, no player state,
and no turn counter. There is no stun state, no phase change, no opening special, and no enrage.

| Turn | Move | Intent shown | Effect |
|---|---|---|---|
| 1 | Smash | single attack, 12 | 12 damage |
| 2 | Beam | single attack, 15 | 15 damage |
| 3 | Barrage | multi-attack 8 ×2, **plus a buff icon** | 8 damage twice, then **+2 Strength to itself, permanently** |
| 4 | Smash | single attack, 14 | repeats the loop at higher Strength |

The player sees the barrage turn coming two turns in advance and can read the buff icon on it, so the
fight is fully telegraphed. The rotation always starts on Smash; the machine's opening state is the
Smash state and the first move can never be skipped.

The only state-dependence in the whole model is the standard "cannot transition away before the first
move is performed" guard shared by all monsters, which just prevents the intent from being re-rolled
before the opening move resolves.

## Damage / block numbers

| Stat | Value |
|---|---|
| HP (min = max, no roll) | **100** |
| Smash | 12 |
| Beam | 15 |
| Barrage | 8 per hit × 2 hits = 16 |
| Block gained | **none, ever** — it has no defensive move |
| Debuffs applied to the player | none |
| Powers on itself | Strength, +2 per barrage (unbounded) |

**It never blocks and never debuffs.** Every point of pressure it exerts is raw single-type attack
damage. The player's entire defensive requirement is HP-and-block arithmetic; no artifact-strip, no
vulnerable/weak management, no discard hate, no summon clearing.

### The escalation curve

Strength is additive to every hit, so the barrage benefits twice per application. Writing the loop
number as *n* (n = 1 is turns 1–3), the monster carries 2(n−1) Strength through cycle *n*:

| Cycle | Smash | Beam | Barrage | Cycle damage | Cumulative |
|---|---|---|---|---|---|
| 1 | 12 | 15 | 8×2 = 16 | 43 | 43 |
| 2 | 14 | 17 | 10×2 = 20 | 51 | 94 |
| 3 | 16 | 19 | 12×2 = 24 | 59 | 153 |
| 4 | 18 | 21 | 14×2 = 28 | 67 | 220 |
| 5 | 20 | 23 | 16×2 = 32 | 75 | 295 |

Cycle damage grows by a flat +8 per loop (+2 on each single, +4 on the doubled barrage). The growth is
linear, not exponential, and it is slow relative to the 100 HP pool: against a solo player, the fight
should end inside two cycles, meaning the Strength ramp usually lands **once**. The ramp is
insurance against stalling, not the fight's main threat — it only becomes the story if the player's
kill takes four or more cycles, at which point it runs away with the fight.

Nothing removes the Strength. There is no decay and no self-inflicted downside, so any player-side
Strength reduction is straightforwardly correct against it — and, unusually for a boss, actually
lands (see below).

## Gimmicks

**The Artifact that isn't there.** On being added to the room, Mk 1 asks the engine to give itself
Artifact — with a declared amount of **zero**. The power-application path bails out immediately on a
zero amount, *before* the multiplayer scaling step ever runs. The consequence is that Mk 1 spawns with
**no Artifact in any configuration, solo or co-op**, and its two siblings (declared 1 and 2) do get
theirs and do scale them upward with seat count. Whether that is a deliberate "the Mk 1 is the one you
are allowed to debuff" tuning or a leftover placeholder in an unrouted monster, the observable
behavior is the same: **every debuff the player throws at Mk 1 sticks on the first try.** Weak,
Vulnerable, Strength-down, and any strip effect all connect. This is the single largest gap between
Mk 1 and the rest of the ladder and should not be assumed to carry forward to Mk 2/Mk 3.

Beyond that it has no gimmick at all: no adds, no minions, no revive, no environmental hook, no
countdown, no positional trick, and no death rattle. Its only cosmetic tell is that it registers as an
armored-hit target for damage SFX, i.e. it reads as a machine.

## Scaling

**By act:** none. HP is a fixed 100 (min equals max, so there is not even the usual per-fight HP roll),
and no damage number is act-conditional.

**By ascension:** **none on Mk 1.** This is worth flagging as a difference within its own family:
Mk 2 and Mk 3 both route their HP through the ascension helper against the "tough enemies" level —
but with the ascension value set equal to the fallback value (200 and 200; 300 and 300), so those
branches are no-ops too. Mk 1 does not even have the branch. The entire ladder is currently
**ascension-flat**, with two of three models carrying a wired-but-inert hook that a future tuning pass
would only have to fill in. For calibration purposes: assume no ascension term today, but expect the
Mk 2/Mk 3 HP numbers to be the ones that move first if MegaCrit turns the dial.

**By seat count (multiplayer):**

1. *HP* goes through the standard multiplayer scale: base × player count × an act multiplier
   (1.1× in act 1, 1.2× in act 2, 1.2× in act 3 outside boss rooms and **1.3× in an act 3 boss room**).
   Because Mk 1 has no encounter model, the boss-room branch cannot currently be reached by it; if it
   is eventually slotted as an act 3 boss it picks up the 1.3×.

| Players | HP as an act 1 fight (1.1×) | HP as an act 3 boss (1.3×) |
|---|---|---|
| 1 | 100 | 100 |
| 2 | 220 | 260 |
| 3 | 330 | 390 |
| 4 | 440 | 520 |

2. *Damage does not scale.* Smash/Beam/Barrage stay at 12/15/8×2 at every seat count. But both
   single attacks and the barrage are aimed at **all opposing creatures**, with the target list
   refreshed between the barrage's two hits — so **each seat takes the full printed number**, not a
   share of it. Party-wide incoming damage per cycle is 43 × seats at cycle 1.
3. *Strength does not scale with seat count* (it is not a multiplayer-scaling power), so the escalation
   term stays at +2 per cycle regardless of party size.
4. *Artifact would scale* — the Artifact power adds one stack per extra player — but Mk 1's zero
   amount short-circuits before that math, so its Artifact stays zero at four players too.

Net effect on co-op: HP rises super-linearly with seats while per-seat incoming damage stays flat and
the escalation term stays flat. A four-player party facing 440 HP needs to sustain roughly the same
personal block wall as a solo player but for **more cycles**, which is exactly the regime where the
+2/cycle ramp starts to matter. Mk 1 is a soft fight solo and a genuinely grindy one at four seats,
and the difficulty difference is carried entirely by the extra turns, not by bigger hits.

## Proposed fight class: **attrition**

Every turn asks the same question in a slightly larger font: *can you cover 12–20 incoming damage
again?* There is no burst turn to bank block for, no add wave to clear, and no rule to solve — the
barrage turn is only marginally above the Beam turn, so nothing in the rotation justifies holding a
defensive card in reserve. What the fight demands per turn is a steady, repeatable block floor plus
enough offense to finish before the linear Strength ramp outpaces that floor; the loss condition is
running out of sustain across many similar turns, not eating one spike. The one non-standard feature —
the Artifact that never applies, leaving it fully debuffable — pushes it further toward attrition
rather than gimmick, because it *removes* a special rule rather than adding one, and it rewards the
same Weak/Strength-down mitigation that a pure damage-race check already wants. For Track B, model it
as a flat-plus-linear incoming curve (43 per three-turn cycle, +8 per cycle thereafter, per seat) with
zero utility demand and a soft turn cap set by where the player's block economy crosses the ramp.
