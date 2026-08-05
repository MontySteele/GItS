"""D1: reactions' share of damage, per act, over a finished cohort.

Reads finished RunResults; changes nothing and gates nothing. R14: this is a
diagnostic, and no acceptance target lives here.

WHY THIS EXISTS. The audit's sentence about reactions -- physics that never
moved the design in -- was written without the share behind it, because no
surface computed one. `tier0.harness.metrics.reaction_share` is that surface
per battery; this is the same figure per ACT of a real run, which is where the
question actually lives: a reaction share is a function of how many auras a
deck can put up against how many bodies the act fields, and act 1 and act 3
field very different bodies.

METRIC DEFINITIONS, fixed here so no later run can redefine them mid-sweep and
identical to `metrics.reaction_share`'s:

- amp        the Vaporize/Melt multiplier's DELTA over the unamplified hit. The
             base hit is a base op's damage; only the uplift is the reaction's.
- splash     Overload's explosion, overkill-clamped at the emit site.
- dot        Electro-Charged's DoT ticking on an ENEMY, likewise clamped. This
             one is NOT inside `total_damage_dealt` -- `dot_tick` is not a
             `damage` event -- so the denominator is widened for it. That is
             the whole of the difference between this share and the older
             `summarize()["reaction_damage_share"]`, which is left untouched
             because it feeds the ratified A6 axis.
- share      POOLED: sum(reaction) / sum(all) over the act's fights. Not a mean
             of per-fight shares -- a 6-damage fight must not weigh as much as
             a 300-damage one.

WHAT THIS DOES NOT MEASURE, said plainly. Everything a reaction does that is
not damage: Superconduct's Vulnerable, Frozen's halved action, Crystallize's
block, Courtroom Drama's stand. A reaction with a 0% damage share can still be
the reason a fight was won. This is a share of DAMAGE and answers only that.
"""

from __future__ import annotations

from tier0 import constants as C

FIGHT_KINDS = ("N", "E", "B")


def _fight_contexts(result) -> list[tuple[int, str]]:
    """(act_index, node_kind) per FIGHT, aligned with `fight_stats`. Same rule
    as elite_blitz._fight_contexts: only N/E/B nodes run a fight, and act
    boundaries sit at multiples of MAP_FLOORS."""
    return [(floor // C.MAP_FLOORS, kind)
            for floor, kind in enumerate(result.node_kinds)
            if kind in FIGHT_KINDS]


def aggregate(results: list) -> dict:
    """RunResults -> per-act reaction share. Key -1 carries the cohort total."""
    if not results:
        return {}
    per_act: dict[int, dict] = {}

    def _bucket(act: int) -> dict:
        return per_act.setdefault(act, {
            "fights": 0, "fights_with_any": 0, "damage_all_ops": 0,
            "damage_from_reactions": 0, "amp": 0, "splash": 0, "dot": 0,
            "reactions": 0})

    for r in results:
        for (act, _kind), fs in zip(_fight_contexts(r), list(r.fight_stats)):
            for b in (_bucket(act), _bucket(-1)):
                b["fights"] += 1
                b["fights_with_any"] += bool(fs.damage_from_reactions)
                b["damage_all_ops"] += fs.damage_all_ops
                b["damage_from_reactions"] += fs.damage_from_reactions
                b["amp"] += fs.reaction_damage_amp
                b["splash"] += fs.reaction_damage_splash
                b["dot"] += fs.reaction_damage_dot
                b["reactions"] += fs.reactions

    for b in per_act.values():
        b["damage_from_base_ops"] = (b["damage_all_ops"]
                                     - b["damage_from_reactions"])
        b["share"] = b["damage_from_reactions"] / max(1, b["damage_all_ops"])
        b["reactions_per_fight"] = b["reactions"] / max(1, b["fights"])
    return per_act


def format_block(per_act: dict) -> str:
    """Report-only rendering. '' when the cohort never landed a point of
    reaction damage, so a non-reacting character prints nothing rather than a
    row of zeroes everyone learns to skip."""
    if not per_act or not any(b["damage_from_reactions"]
                              for b in per_act.values()):
        return ""
    lines = ["  D1 reactions share of damage (report-only, R14)",
             f"    {'act':>4} {'fights':>7} {'share':>8} {'react dmg':>10} "
             f"{'all dmg':>9} {'amp':>7} {'splash':>7} {'dot':>6} "
             f"{'react/fight':>12}"]
    for act in sorted(per_act):
        b = per_act[act]
        label = "all" if act == -1 else str(act + 1)
        lines.append(
            f"    {label:>4} {b['fights']:>7} {b['share']:>8.4f} "
            f"{b['damage_from_reactions']:>10} {b['damage_all_ops']:>9} "
            f"{b['amp']:>7} {b['splash']:>7} {b['dot']:>6} "
            f"{b['reactions_per_fight']:>12.2f}")
    return "\n".join(lines)
