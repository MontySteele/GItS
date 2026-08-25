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


def _print_invariants(flags: list | None) -> None:
    """EB-50's two declared invariants, printed as advice.

    `None` means the reading was out of scope (baseline, or a package deck),
    and silence is the honest output there -- an empty list is the verdict
    "checked, both hold" and says so. The marker is `·`, not `⚠`: D3 leaves
    the axes descriptive, so a breach is a finding to read, not a failure.
    """
    if flags is None:
        return
    for flag in flags:
        print(f"  · INVARIANT {flag}")
    if not flags:
        print("  ✓ both declared scorecard invariants hold")


def _print_identity(flags: list | None) -> None:
    """The declared per-character identity comparison, printed as advice.

    R204 (2026-08-24) demoted this from gate semantics -- `CONSTRAINT
    VIOLATED` on starter and on the median, `warn (package deck)` elsewhere --
    to a report, and retired the deck-band system it was gated beside. It
    prints under the same `· INVARIANT` banner as EB-50's two, because that is
    the reporting the ruling migrated it into and conspicuousness is the whole
    reason it survives. Same `None` convention: silence where no identity is
    declared, and the verdict line where one is declared and holds.
    """
    if flags is None:
        return
    for flag in flags:
        print(f"  · INVARIANT {flag}")
    if not flags:
        print("  ✓ the declared identity comparison holds")


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
    _print_invariants(result.get("invariant_flags"))
    _print_identity(result.get("identity_flags"))


def print_median(character: str, rep: dict) -> None:
    print(f"\n=== {character}: archetype-median identity (round-3 canon) ===")
    for ax in AXES:
        score = rep["median_scores"][ax]
        print(f"  {_AXIS_LABELS[ax]:<14} {score:>4.1f}  {_bar(score)}")
    for flag in rep["median_flags"]:
        print(f"  ⚠ {flag}")
    if not rep["median_flags"]:
        # R204: the identity half left this list for the report below, so the
        # verdict names only what this list still checks.
        print("  ✓ median statline passes the balance heuristic")
    for flag in rep.get("band_flags", []):
        marker = "⚠" if flag.startswith("WINRATE BAND") else "·"
        print(f"  {marker} {flag}")
    if rep.get("band_flags") == []:
        print("  ✓ all ratified winrate bands hold")
    _print_invariants(rep.get("median_invariant_flags"))
    _print_identity(rep.get("median_identity_flags"))


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


def _pct(v) -> str:
    """A rate, or '-' when the split it came from was empty. None is not 0%
    (metrics.card_flow_profile keeps the two apart on purpose)."""
    return "-" if v is None else f"{v:.0%}"


def print_card_flow(encounter: str, flow: dict, top: int = 25) -> None:
    """EB-17's aggregate, printed. Same fence as print_reaction_share and
    print_aura_payoff: this surface makes the counts readable and reads
    nothing into them -- no threshold, no dead-card verdict, no redesign
    trigger. The sprint plan's rule is that the trigger is a design act, and
    a design act does not happen in a print function.

    Sorted by dead-in-hand count, most-dead first, because that is the order
    the question is asked in; `top` bounds the rows so a 90-card pool does not
    scroll the summary away.
    """
    if not flow:
        return
    print(f"  card flow   [{encounter}] {flow['draws']} draws, "
          f"{flow['plays']} plays, "
          f"{flow['played_when_drawn']} played-when-drawn, "
          f"{flow['dead_in_hand']} dead-in-hand "
          f"({flow['combats']} combats)")
    rows = sorted(flow["by_card"].items(),
                  key=lambda kv: (-kv[1]["dead_in_hand"], kv[0]))
    for cid, r in rows[:top]:
        # `plays` is printed beside `draws` and not folded into it: a kit
        # Burst is granted to hand and never drawn, so it reads 0 draws and a
        # positive play count, and a row that showed only draws made that look
        # like a card nobody ever saw.
        print(f"    {cid:<28} draws {r['draws']:>5}  "
              f"plays {r['plays']:>5}  "
              f"pwd {r['played_when_drawn']:>5} "
              f"({_pct(r['played_when_drawn_rate'])})  "
              f"dead {r['dead_in_hand']:>5} "
              f"({_pct(r['dead_in_hand_rate'])})  "
              f"first-copy {r['force_first_copy']}/"
              f"{r['first_copy_drawn_combats']} "
              f"({_pct(r['force_first_copy_rate'])})  "
              f"win {_pct(r['winrate_first_copy_played'])} played vs "
              f"{_pct(r['winrate_first_copy_dead'])} dead")
    if len(rows) > top:
        print(f"    ... {len(rows) - top} more card ids")


def _num(v, fmt: str = ".2f") -> str:
    """A figure, or '-' when the split it came from was empty. The `_pct`
    rule one type over: None is not zero (metrics keeps the two apart on
    purpose, and a ratio over nothing is not a ratio of nothing)."""
    return "-" if v is None else format(v, fmt)


def print_encore_census(encounter: str, census: dict, top: int = 25) -> None:
    """EB-20's aggregate, printed. Same fence as print_card_flow and the rest:
    this surface makes the census readable and reads nothing into it -- no
    saturation verdict, no target grant/drain ratio, no opinion on whether 19
    granters against 1 spender is the shape the character wants. D8's value is
    [USER]'s to pick and a pick does not happen in a print function.

    Silent on a cohort with no Encore in it (an empty profile), so a Klee run
    with the flag on prints nothing rather than a row of zeroes wearing
    Furina's vocabulary.

    Card rows are sorted by Encore granted, most first, because that is the
    order the "19 of 78 grant" sentence is asked in; `top` bounds them.
    """
    if not census:
        return
    print(f"  encore      [{encounter}] "
          f"granted {census['granted']} "
          f"({census['granted_per_combat']:.2f}/combat)  "
          f"drained {census['drained']} "
          f"= {census['spent']} spent + {census['absorbed']} absorbed  "
          f"gain/drain {_num(census['gain_drain_ratio'])}  "
          f"overdrew {census['overdrawn']} HP  "
          f"({census['encore_combats']} of {census['combats']} combats)")
    print(f"  encore held [{encounter}] "
          f"residual {_num(census['residual_per_combat'], '.2f')}/combat "
          f"({census['residual']} over {census['residual_samples']} combats, "
          f"{_pct(census['residual_share_of_granted'])} of grants)  "
          f"peak mean {census['peak_mean']:.2f} max {census['peak_max']}  "
          f"empty at {census['zero_turns']}/{census['turns_sampled']} turn "
          f"snapshots ({_pct(census['zero_turn_rate'])})")
    grants = ", ".join(f"{k} {v}" for k, v
                       in sorted(census["granted_by_source"].items())) or "none"
    spends = ", ".join(f"{k} {v}" for k, v
                       in sorted(census["spent_by_source"].items())) or "none"
    absorbs = ", ".join(
        f"{k} {v}" for k, v
        in sorted(census["absorbed_by_source"].items())) or "none"
    print(f"  encore src  [{encounter}] grants: {grants} | "
          f"spends: {spends} | absorbs: {absorbs}")
    legs = ", ".join(
        f"{leg} {v['applied']} ({_pct(v['share'])}"
        + (f", {v['wasted']} wasted" if v["wasted"] else "") + ")"
        for leg, v in census["fanfare_by_leg"].items()) or "none"
    absent = (f"  absent: {', '.join(census['legs_absent'])}"
              if census["legs_absent"] else "")
    odd = (f"  UNREGISTERED LEGS: {', '.join(census['legs_unexpected'])}"
           if census["legs_unexpected"] else "")
    print(f"  fanfare leg [{encounter}] {census['fanfare_applied']} applied; "
          f"encore legs {census['fanfare_from_encore']} "
          f"({_pct(census['fanfare_from_encore_share'])}): {legs}"
          f"{absent}{odd}")
    rows = sorted(census["by_card"].items(),
                  key=lambda kv: (-kv[1]["granted"], kv[0]))
    for cid, r in rows[:top]:
        print(f"    {cid:<28} granted {r['granted']:>6} "
              f"({_pct(r['share_of_granted'])}, "
              f"{r['granted_per_combat']:.2f}/combat, "
              f"{r['combats_granting']} combats)  "
              f"spent {r['spent']:>6} ({_pct(r['share_of_spent'])}, "
              f"{r['combats_spending']} combats)")
    if len(rows) > top:
        print(f"    ... {len(rows) - top} more card ids")


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
