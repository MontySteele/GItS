# Assassin Raider

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `AssassinRubyRaider`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounter:** `RubyRaidersNormal` only
- **Fight class:** **spike**

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of observed mechanics and constants, per the IP rule used for the DLL card extraction.

## Where it shows up

The Assassin Raider is never a solo encounter. It exists only inside the Ruby Raiders normal fight,
which builds its lineup by drawing **three** raiders from a pool of five distinct raider types, each
of which may appear **at most once**. The five are Axe, Assassin, Brute, Crossbow, and Tracker. With
draw-without-replacement over five equally weighted types, the Assassin is present in roughly 60% of
Ruby Raiders encounters, and never as a duplicate pair.

The Ruby Raiders room is also pinned into a fixed slot on a player's very first run ever (it is the
sixth normal encounter of the scripted first-run ordering), so a large share of new players meet this
monster at a known point in Act 1 with a nearly-starter deck.

## Intent pattern

This is the simplest AI in the raider family: a **single move state that loops back into itself**.

| Turn | Intent | Effect |
| --- | --- | --- |
| 1 | Attack (single-target) | Killshot |
| 2 | Attack (single-target) | Killshot |
| n | Attack (single-target) | Killshot |

There is no cycle, no cooldown, no alternating defend turn, no ramp, no conditional branch on its own
HP or on the player's state, and no randomized move roll. The state machine's only reachable state is
the Killshot state, whose follow-up is itself. Consequently the telegraphed intent is fully
predictable from turn one and never changes for the life of the monster — the player can plan the
whole fight against it on the first intent read.

## Damage / block numbers

| Stat | Base | Ascension-modified |
| --- | --- | --- |
| Starting HP (rolled in range) | 18–23 | 19–24 (Tough Enemies tier) |
| Killshot damage | 10 | 11 (Deadly Enemies tier) |

- **Block:** none. It never gains Block, ever.
- **Powers/debuffs applied:** none. No Strength gain, no Weak/Vulnerable/Frail application, no
  status-card insertion, no summons, no on-death effect.
- **Defensive traits:** none beyond raw HP. (It uses the armored take-damage sound, which is
  cosmetic flavor for the raider faction and carries no damage reduction.)
- Attack is a single hit, single target, resolved through the standard attack pipeline — it is
  subject to the usual player Block, Vulnerable, and monster Strength/Weak modifiers.

## Gimmicks

None, and that is the design point. The Assassin is the raider band's **flat damage tap**: the
highest per-turn single-target output of the group, paid for with the lowest effective durability
profile relative to that output. Compare within the same encounter:

| Raider | HP band (base) | Per-turn threat | Shape |
| --- | --- | --- | --- |
| Assassin | 18–23 | 10 every turn | flat, unconditional |
| Axe | 20–22 | 5 + 5 Block, 5 + 5 Block, then 12 | 3-beat cycle, self-shielding |
| Brute | 30–33 | 7, alternating with a +3 Strength self-buff | ramping, tanky |
| Crossbow / Tracker | (see their own dossiers) | — | — |

So the Assassin's role is to make the *first two turns* of the Ruby Raiders fight lethal while the
Brute is still ramping and the Axe is still shielding. It is a threat that must be answered
immediately or it is simply free chip damage on the player for the entire encounter. Its own low HP
band (18–23) is inside single-card or two-card kill range for most Act 1 decks, which is the intended
counterplay: the fight asks the player to spend early burst on the Assassin rather than on the
tankier Brute.

## Scaling by act / ascension

- **Act:** no act scaling. It appears in Act 1 only; there is no Act 2/3 variant, no elite version,
  and no boss-fight cameo.
- **Ascension:** two independent bumps, each gated on a distinct ascension threshold rather than on a
  numeric level:
  - *Tough Enemies* threshold — HP roll band shifts from 18–23 up to 19–24 (+1 to both ends).
  - *Deadly Enemies* threshold — Killshot goes from 10 to 11 (+10% damage).
  Both are one-time step changes, not per-level scaling. There is no third tier.
- The HP bump is negligible (it does not move the number of cards needed to kill it for most decks),
  while the damage bump compounds: at 11/turn a three-turn Ruby Raiders fight leaks 33 unmitigated
  damage from this monster alone.

## Multiplayer / seat count

Nothing in the Assassin's own model reads player count, seat count, or co-op state: HP, damage, and
the move loop are identical at any seat count. Its attack resolves against whichever seat the shared
monster-targeting layer has it aimed at, so in co-op the 10–11 damage lands on one hero per turn
rather than being split or duplicated. The encounter generator likewise fixes the lineup at three
raiders regardless of party size. Net effect: in co-op the Assassin's relative threat *drops* (same
output spread across a larger total party HP pool and more removal available on turn one), which
makes it a solo-seat problem far more than a party problem.

## Proposed fight class: `spike`

Per-turn, this monster demands one thing and demands it immediately: **absorb or prevent ~10 damage,
or delete it before it swings again.** There is no ramp to outpace, no attrition curve to survive, no
puzzle to solve — the entire decision surface is a turn-one race between the player's burst and the
Assassin's flat clock, and its HP band is deliberately set just inside single-turn kill range so that
race is winnable but tight. The correct play is a front-loaded damage spike, and every turn the
player fails to produce that spike costs a fixed, non-negotiable 10–11 HP. Note that the *containing*
encounter (Ruby Raiders as a whole) is closer to `mixed`, since the Brute ramps and the Axe shields;
this label describes the demand the Assassin itself contributes, which is pure front-loaded pressure.
