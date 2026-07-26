# Klee survival sprint — frontload as defense

**Status:** implementation checkpoint reached, 2026-07-22; the candidate is
measured but awaits the legacy tank-boss-band ruling. See
`docs/klee-survival-sprint-report.md`.
**Source finding:** `klee-design-review.md` and the follow-up red pen.
**Goal:** bring Klee's realistic Act-1 clear rate into the real-Ironclad
neighborhood without giving her Ironclad-shaped Block or sustain.

## 0. Measurement discipline

Another thread is landing simulator bug fixes during this sprint. Old numbers
are therefore context, not locks. Every measurement window records:

- the exact Git commit and dirty-worktree state;
- `CONSTANTS_VERSION`, `DRAFTER_VERSION`, `RUNTEMPLATE_VERSION`, and
  `A6_INSTRUMENT_VERSION`;
- runs, seed, draft policy, pilot, relic/potion flags;
- a fresh same-world control immediately before the treatment.

If a control does not reproduce an archived number, continue from the fresh
control unless a test failure or obvious discontinuity identifies a new bug.
Attribution is always treatment minus the adjacent same-world control.

Standing realistic-run cell:

```text
character=klee
policy=assigned
pilot=<generic|demolition|spark|reaction>
grant_relics=true
grant_potions=true
seed=11
runs=1500 for decisions (300 is an iteration smoke)
```

Primary outputs: run winrate, net HP loss on normals, act median HP%, near-death
rate, death-node distribution. Identity regressions: Tier-0 A1/A2/A6,
archetype tank-boss bands, and the existing degeneracy suite.

## 1. Window A — armed Bombs suppress attacks

### Design

The first attack action an enemy makes while it has at least one pending Bomb
deals damage as though the enemy were Weak. The enemy then adapts for the rest
of that combat. This is a property of the armed Bomb state, not a Weak stack:

- every hit of one multi-hit action is suppressed;
- the protection is spent after that action, even if more Bombs remain;
- detonating before an attack forfeits the immediate protection but does not
  spend it, so a later armed Bomb can still catch that enemy once;
- additional Bombs do not strengthen or refresh it;
- actual Weak and armed-Bomb suppression do not multiply together;
- non-attack damage is unaffected.

The play decision is the point: leave the first mine armed to soften one
attack, or detonate it early for tempo. The once-per-enemy limit prevents a
Bomb engine from maintaining boss-scale Weak without investing in Weak.

### Acceptance

- focused combat tests cover pending, early detonation, natural detonation,
  multiple Bombs, and non-stacking with Weak;
- the frozen reference anchor remains exact;
- normal-fight HP bleed improves materially;
- Klee remains fragile: the treatment is not expected to reach 40% alone.

## 2. Window B — frontloaded live-card repair

Only cards whose immediate bodies are below their job receive changes. Scaling
powers, Burst, Gleeful Barrage, The Big One, and long-fight engines are out of
scope so the pass raises A1 without raising A2.

| Card | Base change |
|---|---|
| Kaboom! | damage 6 -> 7 |
| Jumpy Dumpty | hit damage 7x2 -> 8x2; Bomb unchanged |
| Big Badda Boom | damage 12 -> 16 |
| Blast Radius | damage 6 all -> 9 all |
| Pocket Fireworks | damage 4x2 -> 5x2 |
| Rapid Fire | damage 3x4 -> 4x4 |
| Snap! | damage 5 -> 6 |
| Sizzle | damage 7 -> 8; aura rider 5 -> 6 |
| Boom Goes the Dynamite | damage 16 -> 18 |
| Flame Dance | damage 7 all -> 9 all; aura rider unchanged |

Upgrade deltas are adjusted to preserve sensible upgraded endpoints rather
than blindly preserving every old delta. Each changed row receives a sheet
pin or behavior test.

### Acceptance

- realistic generic center target: 35-45%; archetype texture may vary around
  it rather than every plan being forced to exactly 40%;
- A1 rises and remains above A2; A2 is unchanged within noise;
- demolition does not breach its tank-boss ceiling and spark stays within its
  ratified band;
- normal-fight bleed closes substantially without Klee acquiring sustain.

If Window A plus the full table overshoots, trim the card table; do not weaken
the Bomb design merely to preserve a larger collection of number buffs.

## 3. Window C — Overload stagger

Candidate shared-system change: Overload additionally applies 1 Weak to the
reacting enemy. This is a separate window because it changes every present and
future Pyro/Electro character.

Ship only if Reaction remains materially below the solo floor after A+B. Run
Klee, Furina, reaction-specific tests, control-uptime checks, and amplifier
guards. A cross-character regression vetoes the change; the fallback is a
Klee-personal reaction payoff rather than special-casing the resolver.

## 4. Window D — companion interfaces and dead-card telemetry

Do not use raw pick rate as the redesign trigger. The current static drafter
values only printed damage and Block, so draw, debuffs, generation, Bombs, and
many engines are invisible.

First add or run paired evidence for:

- offered / picked / played-when-drawn;
- conditional activation and dead-in-hand rate;
- damage, Block, energy, and cards generated by source card;
- force-first-copy paired winrate.

Then consider, one at a time:

- `friendly_visit`: Block plus a reliable Companion draw/discount;
- `study_buddy`: a modest Block body on the replay setup;
- `borrowed_brilliance`: make the temporary copy usable at base;
- `elemental_ecstasy`: aura-gated mitigation at a playable cost.

Shared companion rows are not the baseline Klee fix: flat buffs there affect
every character and risk violating enabler-not-carry.

## 5. Sprint exit

The sprint is done when:

1. full suite is green;
2. a current-world report records control and every shipped window;
3. Klee's realistic Act-1 winrate is centered near parity while her HP profile
   remains visibly more volatile than Ironclad's;
4. normal-fight bleed, not merely boss survival, has improved;
5. no old tank-boss, reaction, support-carry, or scaling guard is silently
   invalidated.
