"""O-1 pinned: a per-fight rate is per COMBAT, not per merged record.

Track O slice 12 (`docs/archive/instrument-redteam-2026-08-05.md`, TOP-5 #1) found
that `runner.run_battery` merges the two stages of the `gauntlet` encounter
into ONE `FightStats`, while `aura_profile` / `payoff_profile` / `summarize`
divide their per-fight rates by `len(all_stats)` -- records, not combats. The
numerator covered 3500 combats and the denominator counted 3000 records, so
every published Track H per-fight rate on the battery surface was overstated
by 16.7% on the `all` row and by 2x on the gauntlet row. Ruled at the
2026-08-06 sitting as unambiguous-correct-behavior: **per-combat denominators
are correct.**

The first test below reproduces the defect's exact shape -- O's own two-stage
fixture, one reacting stage and one starved one -- and asserts the corrected
denominator. The rest hold the fence around it: the pooled counts must not
move, the single-stage encounters must not move, and the record-level figures
that describe the encounter ATTEMPT (winrate, turns, HP) must stay per record.

Fixture shape lifted from `review/redteam/fixtures/track_o/s12-pooling-fixture.py`.
"""

from __future__ import annotations

import copy

from tier0.harness import metrics
from tier0.harness.runner import run_battery


def _combat(**kw) -> metrics.FightStats:
    """One COMBAT's worth of counters; everything not named is inert."""
    base = dict(
        won=True, turns=5, hp_start=80, hp_end=80, total_damage_dealt=0,
        damage_by_turn={}, energy_by_turn={}, total_block_gained=0,
        damage_blocked=0, energy_spent=0, cards_drawn_extra=0,
        energy_generated_extra=0, healing=0, encore_absorbed=0,
        debuff_stacks_applied=0, debuffed_intents=0, aura_intents=0,
        total_intents=0, reactions=0, reaction_damage=0, auras_wasted=0)
    base.update(kw)
    return metrics.FightStats(**base)


def _gauntlet_stages() -> list[metrics.FightStats]:
    """Stage 1 reacts; stage 2 bricks. The shape that made a starved combat
    disappear: merged, `reactions` is 1 and the record reads as not starved."""
    stage1 = _combat(
        reactions=1, auras_wasted=1, aura_ops={"apply_aura": 2},
        aura_applications_by_source={"hit": 4},
        aura_applications_by_element={"pyro": 4},
        reactions_by_name={"melt": 1},
        conditional_evaluated={"reaction_triggered_by_this": 2},
        conditional_fired={"reaction_triggered_by_this": 1})
    stage2 = _combat(reactions=0, auras_wasted=0)
    return [stage1, stage2]


# --- the defect, and the denominator that replaces it ---------------------

def test_a_two_stage_record_denominates_per_combat_not_per_record():
    """O-1. One gauntlet record = two combats: four applications over two
    combats is 2.0/fight, and the old record denominator read it as 4.0."""
    merged = [metrics.merge_stages(_gauntlet_stages())]
    assert len(merged) == 1
    aura = metrics.aura_profile(merged)
    assert aura["fights"] == 1                 # records
    assert aura["combats"] == 2                # combats
    assert aura["applications"] == 4           # pooled count: unmoved
    assert aura["applications_per_fight"] == 2.0
    assert aura["aura_ops_total"] == 2
    assert aura["aura_ops_per_fight"] == 1.0
    # The old, record-denominated figures, named so the pin says what it is
    # pinning against: 4/1 and 2/1.
    assert aura["applications_per_fight"] != aura["applications"] / len(merged)
    assert aura["aura_ops_per_fight"] != aura["aura_ops_total"] / len(merged)


def test_a_starved_combat_merged_with_a_reacting_one_is_still_starved():
    """O-1's erased row: `aura_starved_fights` counted records with zero
    reactions, and a starved stage merged with a reacting stage reads
    `reactions > 0`. Half of this gauntlet was starved."""
    merged = [metrics.merge_stages(_gauntlet_stages())]
    s = metrics.summarize(merged)
    assert s["fights"] == 1 and s["combats"] == 2
    assert s["aura_starved_fights"] == 0.5
    assert s["reactions_per_fight"] == 0.5     # one reaction, two combats
    assert s["auras_wasted_per_fight"] == 0.5


def test_payoff_evaluations_per_fight_are_per_combat():
    """`evaluated_per_fight` is on the same denominator as every other
    per-fight rate; two evaluations across two combats is 1.0."""
    merged = [metrics.merge_stages(_gauntlet_stages())]
    pay = metrics.payoff_profile(merged)
    assert pay["combats"] == 2
    row = pay["by_predicate"]["reaction_triggered_by_this"]
    assert row["evaluated"] == 2               # pooled count: unmoved
    assert row["fired"] == 1
    assert row["evaluated_per_fight"] == 1.0


def test_fights_with_any_aura_counts_combats():
    """A per-fight COUNT of fights is on the same unit as a per-fight rate:
    one of this gauntlet's two combats put an aura up, not one of one."""
    merged = [metrics.merge_stages(_gauntlet_stages())]
    assert metrics.aura_profile(merged)["fights_with_any_aura"] == 1
    assert metrics.reaction_share(merged)["combats"] == 2


def test_the_pooled_counts_and_ratios_of_sums_are_unchanged():
    """Track O: "pooled counts and every ratio-of-sums are unaffected -- the
    defect is exactly in the per-record denominators." The merged record and
    the two loose combats must agree everywhere except those denominators."""
    stages = _gauntlet_stages()
    loose = [copy.deepcopy(s) for s in stages]
    merged = [metrics.merge_stages([copy.deepcopy(s) for s in stages])]
    a_loose, a_merged = metrics.aura_profile(loose), metrics.aura_profile(merged)
    for key in ("applications", "aura_ops", "aura_ops_total", "reactions",
                "reactions_by_name", "applications_by_source",
                "applications_by_element", "auras_wasted",
                "applications_per_turn", "applications_per_fight",
                "aura_ops_per_fight", "fights_with_any_aura", "combats"):
        assert a_loose[key] == a_merged[key], key
    for key in ("reactions_per_fight", "aura_starved_fights",
                "auras_wasted_per_fight", "combats"):
        assert metrics.summarize(loose)[key] == metrics.summarize(merged)[key]


# --- the fence -----------------------------------------------------------

def test_a_single_combat_record_is_one_combat_and_carries_no_stages():
    """The other five encounters must not move: an unmerged record has no
    stage list and denominates as itself."""
    one = _combat(reactions=2, aura_applications_by_source={"hit": 3})
    assert one.stages == [] and one.combats == 1
    assert metrics.per_combat([one, one]) == [one, one]
    aura = metrics.aura_profile([one, one])
    assert aura["fights"] == aura["combats"] == 2
    assert aura["applications_per_fight"] == 3.0


def test_merge_stages_returns_the_lone_stage_unchanged_for_one_stage():
    """`run_battery` breaks out of the stage loop when the player dies, so a
    gauntlet that ended in stage 1 is ONE combat and must not be counted as
    two. merge_stages' one-stage path returns that stage as it stands."""
    only = _combat(reactions=1)
    assert metrics.merge_stages([only]) is only
    assert metrics.merge_stages([only]).combats == 1


def test_the_record_level_figures_stay_per_attempt():
    """HP carries across the stage break, so a gauntlet is ONE encounter
    attempt: winrate, turns and the HP delta are per record on purpose and
    are not moved onto the combat denominator (`summarize` docstring)."""
    stages = _gauntlet_stages()
    stages[1].turns = 3
    stages[1].hp_end = 50
    s = metrics.summarize([metrics.merge_stages(stages)])
    assert s["fights"] == 1 and s["combats"] == 2
    assert s["winrate"] == 1.0                 # one attempt, won
    assert s["avg_turns"] == 8                 # 5 + 3, the whole attempt
    assert s["avg_hp_delta"] == -30            # 80 -> 50 across the break


def test_the_stage_records_survive_the_merge_unmutated():
    """The per-combat denominator is only recoverable if the stage records
    still read as the individual combats they were, so merge_stages copies
    stage 1 instead of accumulating into it."""
    stages = _gauntlet_stages()
    before = copy.deepcopy(stages[0].__dict__)
    merged = metrics.merge_stages(stages)
    assert stages[0].__dict__ == before
    assert merged.stages == stages
    assert merged is not stages[0]


# --- the pooled row, where the overstatement was measured -----------------

def _mixed_battery() -> list[metrics.FightStats]:
    """A battery whose records are NOT all one combat each -- three
    single-stage records and two two-stage ones. This is the shape of the
    `all` row that carried O-1's +16.7%: single-stage encounters pooled with
    the gauntlet, one denominator over both units.

    Every combat here contributes 3 aura applications and 1 reaction, so the
    correct per-combat rates are exactly 3.0 and 1.0 whatever the mix is --
    the arithmetic is fixed by construction and the only free variable is the
    denominator under test. 7 combats live behind 5 records.
    """
    def one():
        return _combat(reactions=1, reactions_by_name={"melt": 1},
                       aura_ops={"apply_aura": 1},
                       aura_applications_by_source={"hit": 3},
                       aura_applications_by_element={"pyro": 3},
                       conditional_evaluated={"reaction_triggered_by_this": 2},
                       conditional_fired={"reaction_triggered_by_this": 1})
    return [one(), one(), one(),
            metrics.merge_stages([one(), one()]),
            metrics.merge_stages([one(), one()])]


def test_a_mixed_battery_rate_is_the_known_per_combat_rate():
    """O-1's headline: 5 records, 7 combats, 21 applications and 7 reactions.
    The per-fight rates are the KNOWN 3.0 and 1.0 -- one combat's worth --
    and the record denominator read them as 4.2 and 1.4, overstating by
    exactly 7/5 = +40% on this mix."""
    battery = _mixed_battery()
    aura = metrics.aura_profile(battery)
    assert aura["fights"] == 5 and aura["combats"] == 7
    assert aura["applications"] == 21 and aura["aura_ops_total"] == 7
    assert aura["applications_per_fight"] == 3.0
    assert aura["aura_ops_per_fight"] == 1.0
    s = metrics.summarize(battery)
    assert s["fights"] == 5 and s["combats"] == 7
    assert s["reactions_per_fight"] == 1.0
    # The defect, stated as the number it produced: dividing the same pooled
    # counts by RECORDS overstates by combats/records on any mixed row.
    assert aura["applications"] / s["fights"] == 4.2
    assert aura["applications"] / s["fights"] == 3.0 * 7 / 5


def test_a_mixed_battery_rate_does_not_move_when_the_mix_does():
    """The point of the per-combat denominator: a rate that is 3.0/combat is
    3.0 whether the battery is all single-stage, all two-stage, or mixed.
    Under the record denominator the same world read 3.0, 6.0 and 4.2 --
    which is why a gauntlet row could not be compared with a punisher row."""
    def one():
        return _combat(reactions=1, aura_applications_by_source={"hit": 3})
    all_single = [one(), one(), one(), one()]
    all_double = [metrics.merge_stages([one(), one()]) for _ in range(2)]
    rate = 3.0
    for battery in (all_single, all_double, _mixed_battery()):
        assert metrics.aura_profile(battery)["applications_per_fight"] == rate
        assert metrics.summarize(battery)["reactions_per_fight"] == 1.0


def test_the_payoff_rate_on_the_mixed_battery_is_per_combat_too():
    """Same battery, the H2 surface: 14 evaluations over 7 combats is 2.0."""
    pay = metrics.payoff_profile(_mixed_battery())
    assert pay["fights"] == 5 and pay["combats"] == 7
    row = pay["by_predicate"]["reaction_triggered_by_this"]
    assert row["evaluated"] == 14 and row["fired"] == 7
    assert row["evaluated_per_fight"] == 2.0
    assert row["rate"] == 0.5                  # ratio-of-sums: unmoved


# --- on a real battery ---------------------------------------------------

def test_the_gauntlet_battery_reports_more_combats_than_records():
    """End to end through `run_battery`: `gauntlet` has two stages and every
    other encounter has one, which is the whole of O-1. The combat count sits
    between `fights` (every run died in stage 1) and 2x it."""
    fights = 25
    gauntlet = run_battery("klee", "reaction_weighted", "gauntlet",
                           "reaction", fights, 5)
    punisher = run_battery("klee", "reaction_weighted", "punisher",
                           "reaction", fights, 5)
    g, p = metrics.aura_profile(gauntlet), metrics.aura_profile(punisher)
    assert g["fights"] == p["fights"] == fights
    assert p["combats"] == fights
    assert fights < g["combats"] <= 2 * fights
    # and the rate is the pooled count over THAT denominator, exactly.
    assert (g["applications_per_fight"]
            == g["applications"] / g["combats"])
