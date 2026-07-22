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

## Current-world Ironclad result

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
