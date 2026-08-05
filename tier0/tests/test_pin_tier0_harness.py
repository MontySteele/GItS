"""Pin tests for the tier-0 harness instrument (axes / metrics / runner).

Three definitions that the instrument publishes as numbers and that nothing
else in the suite reads back: WHERE the A7 setup-tax clock stops, WHAT counts
as an enemy action in the control-uptime denominator, and WHICH WAY round the
reported matchup-texture delta is subtracted. Each is a definition, not an
arithmetic detail: change it and every scorecard printed afterwards means
something different while still looking well-formed.
"""

from __future__ import annotations

from tier0.harness import axes, metrics
from tier0.harness.runner import score_config
from tier0.tests.conftest import make_state

FIGHTS = 40
SEED = 11


def _stats(**kw) -> metrics.FightStats:
    """A zeroed FightStats; callers set only the fields their axis reads."""
    base = dict(won=True, turns=1, hp_start=80, hp_end=80,
                total_damage_dealt=0, damage_by_turn={}, energy_by_turn={},
                total_block_gained=0, damage_blocked=0, energy_spent=0,
                cards_drawn_extra=0, energy_generated_extra=0, healing=0,
                encore_absorbed=0, debuff_stacks_applied=0,
                debuffed_intents=0, aura_intents=0, total_intents=0,
                reactions=0, reaction_damage=0, auras_wasted=0)
    base.update(kw)
    return metrics.FightStats(**base)


# --- A7: the setup-tax clock stops at 70% of the config's OWN peak --------

def test_setup_tax_clock_stops_at_seventy_percent_of_own_peak_window():
    """A7 counts the first turn whose trailing 3-turn DPT window reaches
    70% of the fight's own best window -- not half of it, and not any other
    fraction. A fight whose windows run 0, 0, 6, 6, 6, 10 peaks at 10: 70%
    of that is 7, which only the final window clears, so the plan is
    "online" on turn 6. Every looser fraction would call it online at
    turn 3, when only 60% of the peak is on the board.
    """
    s = _stats(turns=6, total_damage_dealt=48, damage_by_turn={3: 18, 6: 30})

    assert axes._turns_to_own_peak(s) == 6
    # And the same number is what the axis publishes for that pool.
    raw = axes.raw_axes({"synthetic": [s]}, battery=False)
    assert raw["A7_setup_tax"] == 6.0


# --- §2.2a: scripted sleeps are enemy ACTIONS -----------------------------

def test_scripted_enemy_sleeps_count_as_enemy_actions_in_control_uptime():
    """A turn an enemy spends asleep is a turn of enemy output the player
    got for free, so it belongs in the control-uptime denominator alongside
    the intents actually taken. Dropping it would shrink the denominator and
    inflate the reported share of enemy actions companions negated.
    """
    state = make_state()
    for _ in range(3):
        state.emit("intent", enemy="dummy", kind="attack",
                   debuffed=False, aura=False)
    state.emit("enemy_sleep", enemy="dummy")
    state.emit("frozen_action", enemy="dummy", kind="attack",
               by_companion=True)

    s = metrics.extract(state, hp_start=80)

    assert s.total_intents == 3
    assert s.enemy_actions == 4          # 3 intents + 1 sleep
    assert s.control_negated == 0.5
    # summarize divides by that same denominator, so the sleep moves the
    # published uptime too: 0.5/4, never 0.5/3.
    assert metrics.summarize([s])["control_uptime"] == 0.125


# --- runner: the sign of the reported matchup-texture delta ---------------

def test_pressure_delta_is_punisher_winrate_minus_attrition_winrate():
    """pressure_delta is subtracted punisher-first: a POSITIVE value means
    the config does better against the burst matchup than the grind, and a
    negative value means the reverse. The reference starter beats attrition
    far more often than punisher, so its delta is negative -- printed the
    other way round, every scorecard would read its texture backwards.
    """
    result = score_config("ref_ironclad", "starter", "generic", FIGHTS, SEED)
    punisher = metrics.summarize(result["stats"]["punisher"])["winrate"]
    attrition = metrics.summarize(result["stats"]["attrition"])["winrate"]

    assert result["pressure_delta"] == punisher - attrition
    assert punisher < attrition
    assert result["pressure_delta"] < 0
