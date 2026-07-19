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
    for flag in result["heuristic_flags"]:
        print(f"  ⚠ {flag}")
    if not result["heuristic_flags"]:
        print("  ✓ statline shape passes the balance heuristic")


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
