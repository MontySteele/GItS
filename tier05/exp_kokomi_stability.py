"""Kokomi's stability band, READ OUT loud for the first time (2026-07-29).

R51 moved her healer fantasy *entirely* to the stability band -- "the healer
fantasy moves entirely to the stability band (HP-trajectory flatness) in the
act-level realistic sims" -- and the kickoff s3 pre-registered flatness, not
winrate margin, as her acceptance signature. Two things then happened, in this
order, and the second is why this script exists:

1. `run_metrics.stability_profile` was built (Serenitea Sweep I, E1) and lands
   DARK by design. `docs/archive/missed-requirements.md` s1.3 still says the instrument
   "was never built"; it is STALE as of E1, and the entry should be amended.
2. Nothing ever RAN it. There is no experiment script and no report on record
   that prints a stability number, so what did not exist was not the metric but
   the READING -- and a dark instrument nobody points at a cohort is
   indistinguishable, from the outside, from no instrument at all.

`trajectory_profile` (this sprint) adds the within-fight half that
`stability_profile` structurally could not see: it reads `hp_start`/`hp_end`,
one number per fight, so a fight entered at 100% and left at 80% reads the same
whether it was four even chips or a dive to 25% and a recovery. The dive is what
the fantasy forbids.

**NO BAND IS DECLARED BY THIS SCRIPT AND NONE MAY BE READ OUT OF IT.** Both
profiles report `band: None`. Declaring the band is a reserved [USER] ruling
under R51 and D5 (from design intent, recorded as such, before the confirmatory
playtest, and never revised against the playtest that grades it). What this
gives the ruling is the one thing it was missing: what "stable" looks like
relative to the rest of the roster, in the CURRENT world, on one invocation.

The contrast arms are the point. A flatness number alone is uninterpretable --
Kokomi's 0.11 means nothing until Klee's and the Ironclad's sit beside it,
measured in the same world, in the same run.

Usage: python -m tier05.exp_kokomi_stability [--runs N] [--seed N] [--jobs N]
"""

from __future__ import annotations

import sys

from tier0.content import loader
from tier05 import cells, run_metrics

BASE = cells.CANONICAL.but(name="kokomi-stability")

#: Kokomi's three plans, then the contrasts. Klee is the roster's declared HP
#: VOLATILITY pole (kickoff: "Furina = HP volatility, Kokomi = HP stability"),
#: so her reaction arm is the far end of the axis rather than a neutral
#: reference; `ref_ironclad` is the neutral one, and `furina/salon` is included
#: because it is the roster's strongest arm and the question "is flatness a
#: winning trait here" needs the leader in the table.
ARMS: tuple[tuple[str, str], ...] = (
    ("kokomi", "priest"),
    ("kokomi", "commander"),
    ("kokomi", "assist"),
    ("klee", "reaction"),
    ("furina", "salon"),
    ("ref_ironclad", "generic"),
)


def main(argv: list[str] | None = None) -> int:
    base, _ = cells.parse_overrides(
        list(sys.argv[1:] if argv is None else argv), BASE)
    cells.print_header(base, "KOKOMI STABILITY BAND -- REPORTED, NOT BANDED",
                       f"{len(ARMS)} arms; Kokomi's three plans + 3 contrasts")
    print("  Every value is a FRACTION OF MAX HP, so rows are comparable "
          "without rescaling.")
    print("  BAND NOT DECLARED. Every column is REPORTED. Declaring an "
          "acceptance band is a")
    print("  reserved [USER] ruling (R51, D5) -- this script measures and "
          "does not judge.")

    print(f"\n  {'character':>13} {'plan':>11} {'hp':>4} | "
          f"{'lossSD':>7} {'lossCV':>7} {'lossMean':>8} {'worstFt':>7} | "
          f"{'inFtSD':>7} {'wrstRnd':>7} {'<50%':>6} {'<30%':>6} | "
          f"{'drawdn':>7} {'p90dd':>7} {'livedDD':>7} | {'prev/ft':>7}")

    for character, archetype in ARMS:
        cell = base.but(character=character, archetype=archetype)
        results = cell.run()
        max_hp = loader._character_index()[character]["hp"]
        s = run_metrics.stability_profile(results, max_hp)
        t = run_metrics.trajectory_profile(results, max_hp)
        print(f"  {character:>13} {archetype:>11} {max_hp:>4} | "
              f"{s['hp_loss_sd_pct']:>7.3f} {s['hp_loss_cv']:>7.3f} "
              f"{s['hp_loss_mean_pct']:>8.3f} "
              f"{s['worst_fight_loss_pct']:>7.3f} | "
              f"{t['within_fight_sd_pct']:>7.3f} "
              f"{t['worst_round_drop_pct']:>7.3f} "
              f"{t['round_share_below_50']:>6.3f} "
              f"{t['round_share_below_30']:>6.3f} | "
              f"{t['max_drawdown_pct']:>7.3f} "
              f"{t['p90_drawdown_pct']:>7.3f} "
              f"{t['survived_drawdown_pct']:>7.3f} | "
              f"{s['prevented_per_fight']:>7.2f}")

    print("\n  HOW TO READ THIS")
    print("  lossSD/lossCV/lossMean/worstFt -- stability_profile: per-FIGHT "
          "HP loss, pooled.")
    print("    lossSD is the headline flatness number; lossCV divides it by "
          "the mean, which")
    print("    separates 'flat because nothing hits her' from 'flat because "
          "she absorbs evenly'.")
    print("  inFtSD/wrstRnd -- trajectory_profile: WITHIN fights, round by "
          "round. inFtSD is the")
    print("    mean per-fight SD of end-of-round HP (jaggedness, not "
          "attrition); wrstRnd is the")
    print("    biggest single-round fall, which is the burst a ward is "
          "supposed to eat.")
    print("  <50%/<30% -- share of all rounds fought that ENDED under that "
          "fraction of max HP.")
    print("  drawdn/p90dd -- run-scale peak-to-trough. SATURATED: ~90% of "
          "runs end in death and")
    print("    a death has fallen almost all the way, so this reads ~1.0 for "
          "flat and jagged")
    print("    alike. livedDD is the same over only the fights she walked out "
          "of -- uncensored,")
    print("    but survivorship-biased the other way. Neither is the "
          "discriminating column today.")
    print("  THE LETHAL ROUND IS EXCLUDED from every column: dying is what "
          "the winrate table")
    print("    measures, and a round ending at 0 HP is trivially under every "
          "threshold.")
    print("  prev/ft -- R51's ruled ward-prevention feed, in raw HP. "
          "Reported, never axis-credited.")
    print("  A LOWER number is flatter for every column here. Flatter is not "
          "the same as better:")
    print("  a dead run stops generating rounds, so read these beside the "
          "winrate table.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
