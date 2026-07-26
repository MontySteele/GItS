# Furina Tier 0.5 realistic-run baseline

**Date:** 2026-07-22  
**Status:** diagnostic baseline; no balance change authorized or applied.  
**World:** assigned draft policy, `RUNTEMPLATE_VERSION 3`, relic granting and
potions enabled, 1,500 runs/cell, seed 11. The ordinary runner now exposes
these cells through `--character furina --archetype <plan> --realistic`.

## Headline

Furina's Tier 0 sheet implementation is not the missing piece: Salon,
Spotlight, Fanfare, Encore, the selector, and her assigned pilots all execute
in the full Act-1 loop. The realistic-run floor is nevertheless collapsed.
This is shared across all three plans rather than one failed archetype.

| Character / plan | Act clear | Wilson 95% | First-elite survival | Act median HP |
|---|---:|---:|---:|---:|
| Furina / Salon | 2 / 1,500 (0.13%) | 0.04-0.48% | 255 / 1,489 (17.1%) | 29% |
| Furina / Spotlight | 0 / 1,500 | 0-0.26% | 200 / 1,498 (13.4%) | 30% |
| Furina / Fanfare | 0 / 1,500 | 0-0.26% | 213 / 1,500 (14.2%) | 31% |
| Klee / Generic control | 489 / 1,500 (32.6%) | 30.3-35.0% | 1,296 / 1,500 (86.4%) | 41% |
| real Ironclad / Generic control | 681 / 1,500 (45.4%) | 42.9-47.9% | 1,218 / 1,500 (81.2%) | 53% |
| ref Ironclad / Generic control | 299 / 1,500 (19.9%) | 18.0-22.0% | 1,045 / 1,500 (69.7%) | 49% |

The first elite is the binding gate: 82-87% of all Furina runs die there.
The median Furina run enters that fight on 34-37 HP after the first rest and
leaves it at zero. The two later elite/boss gates are not yet meaningfully
measurable because almost no runs reach them.

## Mechanism read

A 600-run same-world decomposition separates the early tempo profiles:

| Plan | Normal-fight turns | Normal DPT | First-elite DPT | First-elite Block | Encore absorbed |
|---|---:|---:|---:|---:|---:|
| Salon | 6.4 | 8.0 | 10.6 | 38.1 | 4.0 |
| Spotlight | 6.6 | 7.7 | 8.2 | 47.9 | 4.0 |
| Fanfare | 7.2 | 7.1 | 8.3 | 46.6 | 9.1 |
| Klee / Generic | 2.7 | 18.7 | 21.0 | 28.7 | 0 |
| real Ironclad / Generic | 3.8 | 13.5 | 17.6 | 30.2 | 0 |

Furina actually blocks more total damage than either control in the first
elite, and Fanfare absorbs another nine HP through Encore. It still loses
because those defenses are spread across fights lasting roughly twice as
long while dealing less than half the controls' damage per turn. Her declared
frontload weakness is therefore not merely visible; in the early Act-1 roster
it compounds into many additional enemy actions.

Normal-fight chip is important but is not the whole failure. A 200-loadout
delete test replayed every elite once from full HP and once from the carried
pre-elite HP:

| Plan | Full-HP elite win | Carried-HP elite win |
|---|---:|---:|
| Salon | 49.2% | 19.5% |
| Spotlight | 32.3% | 13.5% |
| Fanfare | 33.0% | 15.5% |

Restoring full HP roughly doubles or triples the elite result, but Spotlight
and Fanfare still lose about two-thirds of isolated elites. This is a combined
tempo + accumulated-chip problem, not a pure sustain miss.

The matchup split is also coherent rather than random. At full HP, Salon wins
91.9% against Byrdonis but only 27.8% against Bygone Effigy and 24.2% against
the four-body Phantasmal Gardener. Spotlight records 73.5% / 17.0% / 12.0%;
Fanfare 81.5% / 9.0% / 17.0%. Furina can answer the ramp clock, but not the
127-HP burst check or the early four-body board.

## Structural finding: package depth hid the Act-1 floor

Tier 0's design passes measured deep authored packages. The first realistic
elite arrives after only three reward screens. `DRAFT_CORE_SIZE` is four:

- Salon begins with one on-plan enabler and reaches its core in 21% of runs.
- Fanfare has starter support and reaches its core in 45%.
- Spotlight has no draft-card head start; at most three reward cards can be
  acquired before the first elite, so its four-card core cannot be online at
  that gate. Its measured online rate is 0% because almost no runs survive
  long enough to take the fourth on-plan card.

This does not by itself prove that the core-size definition should change.
It proves that the battery's median/deep-package balance and the realistic
run's early floor are asking different questions.

## Post-ruling rerun: fixed Salon slots and replacement effects

The next authorized pass made four linked changes: Stage Presence moved to
5 Block (8 upgraded), self-Spotlight moved from 1.25x to 1.0x, the Salon was
capped at three active Members with dry ticks at half damage and no HP loss,
and overflowed deployments gained a final action. A replacement triples the
deploying card's damage/Block rider or doubles a numeric utility rider once;
each displaced Member separately deals a triple-damage final bow. The direct
numbers on Salon cards also received a modest printed-value lift.

Same realistic world and sample size as the baseline:

| Plan | Baseline Act clear | Post-pass Act clear | Baseline first elite | Post-pass first elite |
|---|---:|---:|---:|---:|
| Salon | 0.13% | **5.2%** (78/1,500; 95% CI 4.2-6.4%) | 17.1% | **40.9%** (613/1,499) |
| Spotlight | 0% | **0.13%** (2/1,500; 95% CI 0.0-0.5%) | 13.4% | **24.7%** (371/1,500) |
| Fanfare | 0% | **0.07%** (1/1,500; 95% CI 0.0-0.4%) | 14.2% | **24.2%** (363/1,500) |

This is a real Salon rescue, not a general Furina rescue. Salon now reaches
the second elite in 535/1,500 runs, but Spotlight and Fanfare still lose
roughly three quarters of runs at the first elite and almost every survivor
at the second elite or boss.

The deep-package battery exposes the other side of the curve. Salon now wins
99.4% against `tank_boss`, and A2 Scaling reads 8.9 against its ratified 7.6
ceiling. In a 300-fight source audit, replacement bows supplied only 16.3% of
Salon damage (39.2 damage/fight); ordinary Member ticks supplied 52.3%
(125.3 damage/fight). The ceiling overshoot is therefore the complete
persistent engine plus the card
pass, not an accidental multiplier leaking into later cards. Spotlight still
exceeds its existing A2 ceiling narrowly (4.5 vs 4.3); the archetype median
otherwise passes the shape checks.

The pass widens the floor/ceiling split. It gives an assembled Salon too much
late power while leaving the sparse early-run deck, especially its three
4-damage normal attacks, far below the control characters' tempo. That makes
additional global Salon scaling a poor next lever: the next slice should move
power toward first-cycle access or frontload and away from persistent tick
growth, while Spotlight still needs an access/identity redesign of its own.

## Baseline disposition (superseded by the post-ruling rerun above)

No content numbers or ratified bands move on this baseline alone. The next
measurement window should target early access/tempo rather than global
scaling: starter first-cycle output, guaranteed/seeded first rewards, and
small live-card frontload doses, each measured against the first-elite split
above. Artifact and weapon bonuses should remain a later flagged A/B layer;
using them to hide a 0% base-run floor would make their balance uninterpretable.
