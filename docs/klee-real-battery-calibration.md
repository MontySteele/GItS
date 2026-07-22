# Real-build synthetic-battery calibration

**Date:** 2026-07-22
**Status:** Klee and real-Ironclad surfaces complete. No bands have been
changed yet.

## Question

After the survival rebalance invalidated Klee's old authored-deck tank-boss
ceilings, run boss-reaching **real Klee** and **real Ironclad** builds back
through the frozen synthetic battery, then decide how to rescale the legacy
acceptance surface.

The calibration intentionally reports two surfaces:

- `deck`: the boss-reaching drafted/upgraded deck, without relics or potions;
- `loaded`: the same deck with its run's combat relics and representative
  potion belt.

The deck-only surface is the direct successor to authored-deck bands. The
loaded surface answers actual power, but is expected to saturate easier probes.

## Current-world Klee result

Measurement world: Git `ee7ec04`, tracked-worktree digest `26cb73a000a6`,
1,500 real Act-1 runs per plan, seed 11. Forty evenly sampled boss-reaching
loadouts per plan were run for 50 fights per battery encounter.

| Plan | Real-run clear | Boss reached | Tank boss, deck | Tank boss, loaded |
|---|---:|---:|---:|---:|
| Generic | 32.5% | 784/1500 | 95.4% | 99.6% |
| Demolition | 34.9% | 816/1500 | 97.7% | 100.0% |
| Spark | 30.0% | 757/1500 | 94.0% | 99.9% |
| Reaction | 27.9% | 675/1500 | 93.1% | 99.9% |

Per-loadout deck-only tank-boss distributions (`p10 / median / p90`):

- Generic: 87% / 99% / 100%
- Demolition: 94% / 99% / 100%
- Spark: 84% / 96% / 100%
- Reaction: 80% / 96% / 100%

Every other battery encounter is effectively saturated. Deck-only Spark's
gauntlet is 99.7%; the remaining deck-only cells are 99.9–100%. All loaded
non-tank cells are 100%.

## Finding

Widening the old 45–65% Spark tank-boss band to encompass these results would
not recalibrate a useful guard. It would preserve a probe that cannot
distinguish any boss-ready Klee plan. The full-loadout surface confirms the
same thing more strongly, but the deck-only surface proves relic/potion
saturation is not the cause.

The likely choices after the Ironclad line is restored are:

1. if real Ironclad also saturates, retire absolute synthetic-battery
   winrate bands for boss-reaching builds and keep the battery as a starter /
   authored identity probe only; or
2. re-grade the synthetic encounters against real Ironclad until they regain
   useful resolution, then band Klee relative to that line.

No band or encounter change should land before that comparison.

## 57-card Ironclad upgrade baseline

The upgrade blocker is resolved. The extractor now produces applicable deltas
for all 57 cards (35 extractor rows plus the 22-card supplement), and the
builder/loader fail closed if pool and upgrade IDs ever drift.

Measurement world: Git `80af97c`, tracked-worktree digest `3f6a88aa8fb2`,
1,500 real Act-1 runs, seed 11. Forty evenly sampled boss-reaching loadouts
were run for 50 fights per battery encounter.

| Surface | Upgrades disabled | Full 57/57 upgrades | Delta |
|---|---:|---:|---:|
| Real-run clear | 29.4% | 33.1% | +3.7 pp |
| Boss reached | 591/1500 | 656/1500 | +65 |
| Tank boss, deck | 94.1% | 97.5% | +3.4 pp |

The no-upgrade column is a diagnostic counterfactual from the exact same
world and seeds, with only the external Ironclad upgrade index disabled in
memory. It is not a supported runtime configuration. All loaded battery cells
were 100%; deck-only non-tank cells were 99.5--100%, so the synthetic battery
remains effectively saturated for boss-reaching real builds.

This also confirms that missing upgrades were not harmless data cleanup: they
suppressed the real-run clear rate by 3.7 percentage points and changed rest,
shop, Armaments, and Aggression decisions. The historical 40% Ironclad target
was measured in an unupgraded world and should not be carried into the balance
pass as a current invariant.

Reproduce the upgraded measurement with:

```text
python -m tools.build_ironclad_sheet --verify
python -m tools.real_battery_calibration \
  --runs 1500 --sample 40 --fights 50 --seed 11 --configs ironclad
```

## Pass-5 67-card Ironclad result

Pass 5 adds the ten cards whose runtime primitives were already implemented
and pinned in Tier 0. It does not add free-play, generation-pool, reentrant
draw, or mutable-card-state foundations. The builder now treats pass 4 and
pass 5 as ordered, required, mutually disjoint local layers and derives clean
upgrades for all 67 cards.

Measurement world: Git `ba48777`, tracked-worktree digest `274e468f977e`,
1,500 runs, seed 11, with the same 40-loadout / 50-fight battery cell. The
57-card counterfactual filters only the ten pass-5 IDs in memory; everything
else, including upgrades, seeds, Klee balance work, relics and potions, is
identical.

| Surface | 57-card counterfactual | Full 67/67 pool | Delta |
|---|---:|---:|---:|
| Real-run clear | 33.1% | 40.3% | +7.2 pp |
| Boss reached | 656/1500 | 746/1500 | +90 |
| Tank boss, deck | 97.5% | 99.4% | +1.9 pp |

The exact reproduction of the prior 57-card result in the same-world control
rules out worktree drift as the cause of the gain. The expanded reward pool is
the treatment. Molten Fist is the strongest visible draft-pressure signal:
the assigned drafter selected it on 707 of 766 offers (92.3%). Conditional
winrates by card are selection-biased and are not treated as causal.

The real-run line has therefore returned near the old nominal 40% target for a
new and valid reason: a broader, fully upgraded local reference pool. The
synthetic battery has become even less discriminating (99.4% deck-only tank
boss; every other deck cell 99.9--100%), so no legacy battery band should be
restored from this coincidence.

## Pass-6 76-card Ironclad result

Pass 6 adds the nine bounded cards that read turn/combat history or mutate one
circulating card instance: Drum of Battle, Evil Eye, Forgotten Ritual,
Perfected Strike, Rampage, Second Wind, Spite, Stomp, and Tear Asunder. The
implementation does not open the remaining autoplay or generation paths. It
does pin the exact Strike-tag set, preserves Rampage growth through Armaments,
and counts Evil Eye / Second Wind's individual BlockGained hooks.

Measurement world: Git `ba48777`, tracked-worktree digest `4ed8553c10e0`,
1,500 runs, seed 11, with the same 40-loadout / 50-fight battery cell. The
67-card counterfactual filters only the nine pass-6 reward IDs in memory; code,
upgrades, seeds, relics, potions, and the local 76-card artifact are identical.

| Surface | 67-card counterfactual | Full 76/76 pool | Delta |
|---|---:|---:|---:|
| Real-run clear | 40.3% | 38.1% | -2.2 pp |
| Boss reached | 746/1500 | 742/1500 | -4 |
| Tank boss, deck | 99.4% | 97.2% | -2.2 pp |
| Tank boss, loaded | 99.9% | 100.0% | +0.1 pp |

The exact reproduction of the 67-card result rules out shared-engine drift.
This is the reward-pool treatment under the current assigned drafter: several
new cards are situational and dilute prior offers. Reward pick rates ranged
from 0% for Drum of Battle / Forgotten Ritual to roughly 28--34% for Evil Eye,
Perfected Strike, Rampage, Second Wind, and Spite; Stomp was 4.8% and Tear
Asunder 1.8%. Those rates and conditional winrates are selection-biased, so
they diagnose policy pressure rather than prove individual-card causality.

Coverage is now 76 of 87 discovered classes. Eleven remain: Demonic Shield and
Tank are multiplayer-only; Hellraiser and Stampede remain explicitly unsafe
because their reentrant/autoplay behavior runs below the current degeneracy
guard; and the seven ordinary hard cards are Cascade, Havoc, Howl From Beyond,
Infernal Blade, Primal Force, Stoke, and Thrash. Those seven require autoplay,
generation/transform, or random cross-card mutation semantics and should be a
separate foundation decision rather than another low-risk supplement pass.
