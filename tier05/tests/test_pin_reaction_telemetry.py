"""Pins for the two definitions inside D1's per-act surface that a mutation
round (track K, 2026-08-05) found unprotected: WHICH nodes are fights, and
WHAT `reactions_per_fight` is per.

`test_reaction_telemetry` pins the act arithmetic and the report-not-grade
fence. These two pins sit under it: both mutations leave the table
well-formed, both leave every other assertion in that file green, and both
change what a published number means.

The fixtures are the sibling module's, reused rather than retyped -- the same
import idiom `test_understudy_p15` uses for `test_understudy_soak`'s bridge.
"""

from __future__ import annotations

from tier0 import constants as C
from tier05 import reaction_telemetry

from .test_reaction_telemetry import _FS, _Run


def test_a_boss_node_is_a_fight_and_its_damage_is_in_the_cohort():
    """`_fight_contexts`' docstring fixes the rule and names its precedent:
    "only N/E/B nodes run a fight", the same rule
    `elite_blitz._fight_contexts` runs on. The list is zipped against
    `fight_stats`, so dropping a kind does two things at once -- it loses that
    fight's damage AND it shifts every later fight into the wrong act. Act 3
    is where the bosses are, so the kind that would be quietly dropped is the
    one carrying the act whose share the instrument was built to read.
    """
    kinds = (["N"] + ["?"] * (C.MAP_FLOORS - 1)
             + ["B"] + ["?"] * (C.MAP_FLOORS - 1))
    run = _Run(kinds, [_FS(all_ops=100, amp=10, reactions=1),
                       _FS(all_ops=200, splash=50, reactions=2)])

    per_act = reaction_telemetry.aggregate([run])
    assert per_act[-1]["fights"] == 2
    assert 1 in per_act, "the boss node's act is missing from the table"
    assert per_act[1]["fights"] == 1
    assert per_act[1]["damage_all_ops"] == 200
    assert per_act[1]["splash"] == 50
    assert per_act[-1]["damage_all_ops"] == 300


def test_reactions_per_fight_is_per_fight_and_not_per_reacting_fight():
    """The key says what its denominator is. `fights` and `fights_with_any`
    are both in the bucket and they are different populations -- a cohort
    where half the fights never reacted reads 2.0 per fight and 4.0 per
    reacting fight, and only one of those is the column's name. The narrower
    denominator inflates every act where reactions are rare, which is exactly
    the regime the instrument was built to report on.
    """
    kinds = ["N", "N"] + ["?"] * (C.MAP_FLOORS - 2)
    run = _Run(kinds, [_FS(all_ops=100, amp=10, reactions=4),
                       _FS(all_ops=100, reactions=0)])

    total = reaction_telemetry.aggregate([run])[-1]
    assert total["fights"] == 2
    assert total["fights_with_any"] == 1
    assert total["reactions"] == 4
    assert total["reactions_per_fight"] == 2.0
