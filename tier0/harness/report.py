"""Terminal summary output + the 7-axis scorecard table."""

from __future__ import annotations

from tier0.harness.axes import AXES

_AXIS_LABELS = {
    "A1_frontload": "A1 Frontload",
    "A2_scaling": "A2 Scaling",
    "A3_block": "A3 Block econ",
    "A4_sustain": "A4 Sustain",
    "A5_velocity": "A5 Velocity",
    "A6_utility": "A6 Utility",
    "A7_setup_tax": "A7 Setup tax",
}


def _bar(score: float, width: int = 20) -> str:
    filled = round(score / 10.0 * width)
    return "█" * filled + "·" * (width - filled)


def print_scorecard(character: str, deck: str, result: dict) -> None:
    print(f"\n=== Scorecard: {character}/{deck} "
          f"(REF_IRONCLAD starter = 3.0) ===")
    for ax in AXES:
        score, raw = result["scores"][ax], result["raw"][ax]
        print(f"  {_AXIS_LABELS[ax]:<14} {score:>4.1f}  {_bar(score)}  "
              f"(raw {raw:.2f})")
    print(f"  curve exponent (tank_boss DPT~turn^k): "
          f"{result['curve_exponent']:.2f}")
    print(f"  pressure delta (punisher - attrition winrate): "
          f"{result['pressure_delta']:+.2f}")
    regret = sum(sum(s.regrets for s in ss) for ss in result["stats"].values())
    plays = sum(sum(s.cards_played for s in ss)
                for ss in result["stats"].values())
    print(f"  pilot regret rate: {regret / max(1, plays):.1%}")
    for flag in result["heuristic_flags"]:
        print(f"  ⚠ {flag}")
    if not result["heuristic_flags"]:
        print("  ✓ statline shape passes the balance heuristic")


def print_median(character: str, rep: dict) -> None:
    print(f"\n=== {character}: archetype-median identity (round-3 canon) ===")
    for ax in AXES:
        score = rep["median_scores"][ax]
        print(f"  {_AXIS_LABELS[ax]:<14} {score:>4.1f}  {_bar(score)}")
    for flag in rep["median_flags"]:
        print(f"  ⚠ {flag}")
    if not rep["median_flags"]:
        print("  ✓ median statline passes heuristic + identity constraints")
    for flag in rep.get("band_flags", []):
        marker = "⚠" if flag.startswith("WINRATE BAND") else "·"
        print(f"  {marker} {flag}")
    if rep.get("band_flags") == []:
        print("  ✓ all ratified winrate bands hold")


def print_reaction_share(encounter: str, r: dict) -> None:
    """D1's aggregate, printed. Numbers only -- no verdict, no band, no
    comparison against the spec §4.4 archetype range: this surface exists to
    make the share readable, and reading it is a design act that happens
    somewhere else."""
    if not r:
        return
    print(f"  reactions share [{encounter}] "
          f"{r['share']:.4f} pooled  ({r['damage_from_reactions']} of "
          f"{r['damage_all_ops']}; base {r['damage_from_base_ops']})  "
          f"amp {r['amp']} splash {r['splash']} dot {r['dot']}  "
          f"per-fight mean {r['share_by_fight_mean']:.4f}  "
          f"fights with any {r['fights_with_any_reaction_damage']}/{r['fights']}")


def print_aura_payoff(encounter: str, aura: dict, payoff: dict) -> None:
    """H1+H2's aggregates, printed. Same fence as print_reaction_share: this
    surface makes the counts readable and reads nothing into them."""
    if not aura:
        return
    ops = ", ".join(f"{k} {v}" for k, v in sorted(aura["aura_ops"].items())) \
        or "none"
    src = ", ".join(f"{k} {v}" for k, v
                    in sorted(aura["applications_by_source"].items())) or "none"
    el = ", ".join(f"{k} {v}" for k, v
                   in sorted(aura["applications_by_element"].items())) or "none"
    rx = ", ".join(f"{k} {v}" for k, v
                   in sorted(aura["reactions_by_name"].items())) or "none"
    print(f"  aura ops    [{encounter}] {aura['aura_ops_total']} "
          f"({aura['aura_ops_per_fight']:.2f}/fight): {ops}")
    print(f"  aura apps   [{encounter}] {aura['applications']} "
          f"({aura['applications_per_fight']:.2f}/fight, "
          f"{aura['applications_per_turn']:.2f}/turn; wasted "
          f"{aura['auras_wasted']}) by source: {src} | by element: {el}")
    print(f"  reactions   [{encounter}] {aura['reactions']}: {rx}")
    if payoff:
        for label, key in (("reaction payoff", "reaction_payoff"),
                           ("aura payoff", "aura_payoff")):
            sl = payoff[key]
            rows = ", ".join(
                f"{p} {v['fired']}/{v['evaluated']}"
                for p, v in sl["predicates"].items()) or "-"
            absent = (f"  absent: {', '.join(sl['absent'])}"
                      if sl["absent"] else "")
            print(f"  {label:<11} [{encounter}] fired {sl['fired']} of "
                  f"{sl['evaluated']} evaluations: {rows}{absent}")


def print_summary(character: str, deck: str, encounter: str, s: dict) -> None:
    flags = f"  FLAGS: {','.join(s['flags'])} ({s['flagged_fights']} fights)" \
        if s.get("flags") else ""
    react = ""
    if s["reactions_per_fight"] > 0:
        react = (f"  react/fight {s['reactions_per_fight']:>4.1f}"
                 f" (dmg {s['reaction_damage_share']:.0%},"
                 f" starved {s['aura_starved_fights']:.0%})")
    print(f"{character}/{deck} vs {encounter:<12} "
          f"win {s['winrate']:>6.1%}  "
          f"turns {s['avg_turns']:>4.1f}  "
          f"hpΔ {s['avg_hp_delta']:>+6.1f}  "
          f"dpt {s['avg_dpt']:>5.1f}{react}{flags}")
