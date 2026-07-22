# Klee survival sprint — implementation checkpoint

**Date:** 2026-07-22
**Status:** candidate implementation measured; not merge-ready until the
legacy tank-boss-band collision is ruled.
**Plan:** `docs/klee-survival-sprint-plan.md`

## Which simulator answers which question

The headline results below are from the current **Tier 0.5 real-run model**:
the real Act-1 encounter roster, drafting, rest upgrades/removals, relics, and
potions. This is the acceptance layer for "why does Klee die in Act 1?"

The old **Tier 0 battery** appears only in the regression section. It is not
being used as the survival target. Its frozen 25-card decks and synthetic
tank boss are retained as a guard for established archetype matchup texture.

Measurement world: Git `c355804`, constants/drafter/run-template/A6 versions
`2/2/3/2`, tracked behavioral-worktree SHA-256
`43496c51f9525700afa9d333ca65f707d3619ab77bdd94174bcd342fd412dd19`,
assigned policy, relics and potions enabled. Every treatment was run next to a
fresh control in a separate process. The worktree also contains the concurrent
simulator-fix thread, so archived figures are context rather than attribution
evidence.

## Candidate implementation

### A. Armed-Bomb defense

The first attack action each enemy makes while carrying a pending Bomb deals
damage at the Weak rate. One multi-hit action is reduced coherently; the enemy
then adapts for the rest of combat. Actual Weak does not multiply with the
effect. Early detonation gives up the immediate protection but leaves the
once-per-enemy opportunity available for a later Bomb.

The first version suppressed every attack while Bombed. It reached the desired
real-run neighborhood but functioned as permanent Weak against bosses, so it
was rejected before this checkpoint.

### B. Live-card frontload pass

Ten immediate damage bodies were raised, without touching Burst, long-fight
powers, or scaling multipliers: Kaboom, Jumpy Dumpty, Big Badda Boom, Blast
Radius, Pocket Fireworks, Rapid Fire, Snap, Sizzle, Boom Goes the Dynamite,
and Flame Dance. Endpoints are pinned in tests.

### C. Overload stagger

Overload applies 1 ordinary Weak to the reacted target. It is a shared
reaction rule, not a Klee-only exception, and naturally does not multiply
with armed-Bomb suppression.

### D. Companion interfaces

- Friendly Visit: 5 Block before its discount and draw.
- Study Buddy: 6 Block before arming the replay.
- Borrowed Brilliance: the temporary copy costs 0 at base; the upgrade draws
  1 instead of being the first point at which the copy becomes usable.
- Sweet Dreams: 8 Block when played into a non-Pyro aura, in addition to aura
  refresh and per-aura draw.

These are pool-quality changes, not credited as the main survival fix.

## Tier 0.5 real-run result

All cells are 1,500 runs at seed 11. Percentages in the four plan columns are
full-act clear rates.

| Cell | Generic | Demolition | Spark | Reaction |
|---|---:|---:|---:|---:|
| Fresh control, all windows off | 8.0% | 10.4% | 6.9% | 4.3% |
| A only: once-per-enemy Bomb defense | 14.9% | 19.1% | 13.3% | 10.3% |
| B only: damage bodies | 16.6% | 18.9% | 16.4% | 11.5% |
| A + B | 31.4% | 34.5% | 29.3% | 24.1% |
| A + B + companion interfaces | 32.1% | 34.5% | 29.2% | 25.4% |
| A + B + companions + Overload | **32.5%** | **34.9%** | **30.0%** | **27.9%** |

Final generic Wilson 95% interval: **30.2–34.9%**. The pre-registered generic
target was 35–45%, so the patch is just below the target rather than a clean
pass.

The mechanism is correct even though the magnitude is a little short:
generic normal-fight loss falls from **9.09 HP / 14.7% max HP** to
**6.80 HP / 11.0%**, and act median HP rises from **30.4% to 41.5%**. This is
less chip carried into later gates, not sustain hiding the damage.

Marginal reads:

- A and B are complementary rather than redundant: neither reaches 17%
  generic alone, but together reach 31.4%.
- The companion pass is deliberately small: +0.7 points generic and +1.3
  Reaction, with normal bleed effectively flat.
- Overload is selective: +2.5 points Reaction, versus +0.4 generic,
  +0.4 Demolition, and +0.8 Spark.

## Companion telemetry checkpoint

The current 120-run × four-plan dead-card scan shows that the visible bodies
resurrect Friendly Visit and Study Buddy: neither remains in the bottom-15
pick list. Borrowed Brilliance and Sweet Dreams are still picked 0% because
the assigned drafter's printed-power proxy does not value copying, aura
refresh, or conditional Block. That is an instrumentation limitation, not
evidence that the new text never has value. Played-when-drawn and forced-copy
experiments remain the required next evidence before further buffs.

## Shared-system guard

At 1,500 current-world Furina runs, Overload stagger is a null within
resolution: Salon remains 0.1%, Spotlight 0.0%, and Fanfare 0.0%. The near-zero
absolute Furina result is a separate calibration problem; the on/off pair says
Overload did not cause it. The focused Klee/Furina/reaction/anchor suite is
green: 143 tests passed.

## Legacy Tier 0 regression collision

These are 1,000-fight, seed-42 frozen-battery checks. Again, they are not the
Act-1 survival target.

| Cell | Demo tank boss | Spark tank boss | Reaction tank boss | Reaction gauntlet |
|---|---:|---:|---:|---:|
| Fresh control | 95.7% | 58.7% | 52.1% | 92.6% |
| Full candidate | **99.3%** | **89.0%** | 88.2% | 99.7% |
| Ratified band | 85–97% | 45–65% | ≥35% | ≥75% |

The two ceilings fail. Isolation shows why:

- Bomb defense alone: Demo 97.2%, Spark 67.9% — close, but already just over
  both ceilings.
- Reverting Blast Radius and Pocket Fireworks while keeping the starter buffs
  still leaves Spark at 82.7%.
- Reverting Kaboom and Jumpy Dumpty as well brings Spark to 67.9%, but collapses
  Tier 0.5 generic clear rate from 32.5% to roughly 17% (17.1% before the final
  companion/Overload increments).

This is not a one-card overshoot. The old absolute bands and a meaningful
roster-wide base-envelope repair are pulling in opposite directions.

The legacy-lock test file records three expected failures at this checkpoint:
the two ceilings above and the frozen v0.1 A1 median (current 4.75 versus the
old 4.19 ±0.3). Its other nine checks pass. No lock was silently edited or
weakened.

Full-suite result after the Ironclad upgrade-pipeline patch: **454 passed, 3
failed**. All three failures are
the declared legacy locks above; there are no unrelated test regressions.

## Recommendation and next sprint gate

**Recommend re-ratifying the old absolute tank-boss bands after this base-kit
rebalance, while preserving their qualitative ordering in a real-run matchup
grid.** Demolition should remain the boss specialist and Spark should remain
the act-fight specialist; the synthetic battery's exact 65% Spark ceiling
should not force Klee back to a 17% real Act-1 clear rate.

If the old bands must remain exact, this candidate should not ship as written.
The next design would need a larger run-only source of survivability—most
likely reward-card defense or first-cycle effects—rather than base damage,
and parity will require another sprint rather than a small trim.

After the band ruling:

1. run a 3,000-seed confirmation on the accepted package;
2. inspect death-node movement before adding the last 2.5–7.5 points;
3. add played-when-drawn / forced-copy telemetry for the two sim-blind
   companion interfaces;
4. run the full suite and mirror final card/rule text into the mod layer.
