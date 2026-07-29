import argparse
from tier05 import draft, model, run_metrics, stats
from tier0.content import loader


def measure(character, runs=1500, seed=11, grant_relics=False,
            grant_potions=False):
    archetype = "generic"
    pilot = "generic"
    policy = draft.POLICIES["assigned"]
    results = model.run_many(character, archetype, pilot, policy, runs, seed,
                             grant_relics=grant_relics,
                             grant_potions=grant_potions,
                             n_acts=1)   # §10: Act-1 instrument, pinned
    max_hp = loader._character_index()[character]["hp"]
    surv = run_metrics.survival_profile(results, max_hp)
    n = len(results)
    k = sum(r.won for r in results)
    # ONE Wilson (tier05.stats, sim-hygiene sprint 2026-07-29). The local
    # copy this replaces returned (p, lo, hi); the point estimate is a
    # division every caller already has, so the shared one returns the
    # interval only and the third tuple slot stops being a second shape.
    p = k / n if n else 0.0
    lo, hi = stats.wilson95(k, n)
    tag = (" +relics" if grant_relics else "") + (" +potions" if grant_potions
                                                  else "")
    print(f"=== {character}{tag} ({n} runs, seed {seed}) ===")
    print(f"  winrate            {p:.4f} ({k}/{n})  Wilson95 [{lo:.4f}, {hi:.4f}]  = {p:.1%} [{lo:.1%}, {hi:.1%}]")
    print(f"  act_median_hp_pct  {surv['act_median_hp_pct']:.4f}  = {surv['act_median_hp_pct']:.1%}")
    print(f"  act_share_below_30 {surv['act_share_below_30pct']:.4f}  = {surv['act_share_below_30pct']:.1%}")
    print(f"  near_death_rate    {surv['near_death_rate']:.4f}  = {surv['near_death_rate']:.1%}")
    print(f"  max_hp             {max_hp}")
    print(f"  median HP% by fight: " + " ".join(f"{x:.0%}" for x in surv['median_hp_pct_by_fight']))
    print()
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Realistic Act 1 gauntlet.")
    ap.add_argument("--grant-relics", action="store_true",
                    help="accrue relics through the StS Act-1 cadence (W2)")
    ap.add_argument("--grant-potions", action="store_true",
                    help="accrue + use potions through the Act-1 cadence "
                         "(drops, shop stock, mid-combat use-policy)")
    ap.add_argument("--both", action="store_true",
                    help="measure OFF then ON, to show the winrate shift "
                         "(varies whichever grant flag(s) are set)")
    ap.add_argument("--runs", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    # --both sweeps OFF then ON for the enabled grant flag(s), so a run with
    # --both --grant-potions contrasts no-potions vs potions, etc. Plain --both
    # (no flag) defaults to sweeping potions on, the new lever this pass adds.
    on = (args.grant_relics, args.grant_potions)
    if args.both and not (args.grant_relics or args.grant_potions):
        on = (False, True)
    modes = [(False, False), on] if args.both else [(args.grant_relics,
                                                     args.grant_potions)]
    for gr, gp in modes:
        for ch in ("ref_ironclad", "real_ironclad", "klee"):
            measure(ch, runs=args.runs, seed=args.seed, grant_relics=gr,
                    grant_potions=gp)
