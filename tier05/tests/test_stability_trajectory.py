"""The WITHIN-fight half of Kokomi's stability instrument.

`stability_profile` (E1, Serenitea Sweep I) reads `hp_start` and `hp_end` --
one number per fight. That is enough to separate a character who loses 20% a
fight from one who alternates 5% and 35%, and it is NOT enough to see inside a
fight: 100% -> 80% reads identically whether it was four even chips or a dive
to 25% and a recovery. The dive is the thing R51's healer fantasy forbids, and
until `trajectory_profile` it was invisible at every tier.

The band stays DARK here for the same reason it is dark there (R51, D5): the
acceptance band is a reserved [USER] ruling, declared from design intent before
the confirmatory playtest and never revised against the playtest that grades
it. These tests pin the absence of a verdict first, because that is the part a
later pass is most likely to "helpfully" fill in.
"""

from __future__ import annotations

import pytest

from tier0.engine import combat
from tier0.harness import metrics
from tier05 import run_metrics


class _Fight:
    def __init__(self, hp_start, hp_by_round):
        self.hp_start = hp_start
        self.hp_by_round = list(hp_by_round)
        self.hp_end = self.hp_by_round[-1] if self.hp_by_round else hp_start


class _Run:
    def __init__(self, fights):
        self.fight_stats = fights


# --- the gate ------------------------------------------------------------

def test_the_band_is_none_and_nothing_judges():
    p = run_metrics.trajectory_profile([_Run([_Fight(100, [90, 80])])], 100)
    assert p["band"] is None, (
        "a band appeared in the trajectory instrument. Bands are user-ratified "
        "(house rule) and this one is a D5 design-intent declaration -- see "
        "R51, D5, missed-requirements sec.1.3.")
    forbidden = {"ok", "pass", "passed", "fail", "failed", "verdict",
                 "acceptable", "within_band"}
    assert not (forbidden & set(p)), forbidden & set(p)


# --- jaggedness is not attrition ----------------------------------------

def test_the_dive_and_the_even_chips_are_told_apart():
    """The reason the module exists, as a test.

    Both fights start at 100 and end at 80. `stability_profile` cannot see any
    difference; this must.
    """
    even = run_metrics.trajectory_profile(
        [_Run([_Fight(100, [95, 90, 85, 80])])], 100)
    dive = run_metrics.trajectory_profile(
        [_Run([_Fight(100, [25, 40, 60, 80])])], 100)

    assert dive["within_fight_sd_pct"] > even["within_fight_sd_pct"] * 3
    assert dive["max_drawdown_pct"] == pytest.approx(0.75)
    assert even["max_drawdown_pct"] == pytest.approx(0.20)
    assert dive["worst_round_drop_pct"] == pytest.approx(0.75)
    assert even["worst_round_drop_pct"] == pytest.approx(0.05)


def test_drawdown_is_peak_to_trough_and_survives_a_recovery():
    """A run that heals back to full between fights has still taken the dive.

    Attrition-only metrics forgive the recovery; a drawdown must not, because
    the moment that nearly ended the run happened.
    """
    run = _Run([_Fight(100, [30]), _Fight(100, [90])])
    p = run_metrics.trajectory_profile([run], 100)
    assert p["max_drawdown_pct"] == pytest.approx(0.70)


def test_attrition_alone_does_not_read_as_jagged():
    """Ten fights each losing an even 10% is a steep DECLINE and a flat curve.

    Pooling every round in the run would give this a large SD and call the
    character unstable, which is why the SD is per-fight and then averaged.
    """
    fights = [_Fight(100 - 10 * i, [100 - 10 * (i + 1)]) for i in range(9)]
    p = run_metrics.trajectory_profile([_Run(fights)], 100)
    # Single-round fights contribute no within-fight SD at all.
    assert p["within_fight_sd_pct"] == 0.0
    # ...but the run-scale drawdown correctly sees the whole slide.
    assert p["max_drawdown_pct"] == pytest.approx(0.90)


# --- time spent low -----------------------------------------------------

def test_rounds_below_a_fraction_are_counted_over_rounds_not_runs():
    runs = [_Run([_Fight(100, [60, 40, 20, 45])])]
    p = run_metrics.trajectory_profile(runs, 100)
    assert p["rounds"] == 4
    assert p["round_share_below_50"] == pytest.approx(3 / 4)
    assert p["round_share_below_30"] == pytest.approx(1 / 4)


def test_the_low_fractions_are_a_declared_dial():
    p = run_metrics.trajectory_profile(
        [_Run([_Fight(100, [80, 60])])], 100, low_fractions=(0.90,))
    assert p["round_share_below_90"] == pytest.approx(1.0)
    assert "round_share_below_50" not in p


# --- the lethal round -----------------------------------------------------

def test_the_lethal_round_is_excluded_from_every_column():
    """The judgement call, pinned with its evidence.

    ~90% of tier-0.5 runs end in death, and a death is a fall to zero from
    wherever you were. Measured with the lethal round in, `max_drawdown_pct`
    read 1.03-1.08 for all six arms of the first reading -- the death rate in a
    costume -- and every round ending at 0 HP is trivially under every
    time-spent-low threshold too. Dying is the winrate table's job.
    """
    died = _Run([_Fight(100, [60, 0])])
    p = run_metrics.trajectory_profile([died], 100)
    assert p["lethal_rounds"] == 1
    assert p["rounds"] == 1
    assert p["max_drawdown_pct"] == pytest.approx(0.40)
    assert p["round_share_below_30"] == 0.0
    assert p["worst_round_drop_pct"] == pytest.approx(0.40)


def test_a_cohort_that_only_ever_died_reports_no_flatness_not_perfect_flatness():
    p = run_metrics.trajectory_profile([_Run([_Fight(100, [0])])], 100)
    assert p["rounds"] == 0
    assert p["lethal_rounds"] == 1
    assert "within_fight_sd_pct" not in p


# --- comparability ------------------------------------------------------

def test_everything_is_a_fraction_of_max_hp():
    """So Kokomi (70), Klee (62) and REF_IRONCLAD (80) read against each other
    without rescaling -- the survival_profile rule."""
    small = run_metrics.trajectory_profile([_Run([_Fight(50, [25])])], 50)
    large = run_metrics.trajectory_profile([_Run([_Fight(100, [50])])], 100)
    assert (small["max_drawdown_pct"]
            == pytest.approx(large["max_drawdown_pct"]))
    assert (small["worst_round_drop_pct"]
            == pytest.approx(large["worst_round_drop_pct"]))


# --- degenerate inputs --------------------------------------------------

def test_no_data_does_not_read_as_perfectly_flat():
    assert run_metrics.trajectory_profile([], 80) == {}
    assert run_metrics.trajectory_profile([_Run([])], 80)["rounds"] == 0
    assert "within_fight_sd_pct" not in run_metrics.trajectory_profile(
        [_Run([])], 80)


def test_a_zero_max_hp_does_not_divide():
    assert run_metrics.trajectory_profile([_Run([_Fight(1, [0])])], 0) == {}


def test_a_fight_with_no_recorded_trajectory_is_skipped_not_zeroed():
    """Pre-instrument FightStats carry an empty list. Counting them as flat
    would let a stale cohort dilute a real reading toward stability."""
    p = run_metrics.trajectory_profile(
        [_Run([_Fight(100, []), _Fight(100, [50])])], 100)
    assert p["rounds"] == 1
    assert p["max_drawdown_pct"] == pytest.approx(0.50)


# --- the engine feed ----------------------------------------------------

def test_the_engine_samples_one_hp_per_round_and_metrics_extracts_them():
    """`round_hp` is sampled where `state.player.hp` is authoritative.

    Derivation from `player_hit` + `heal` was rejected: HP also moves through
    block-ignoring self-damage, the Encore shortfall and the Fairy revive,
    none of which emit either event.
    """
    assert 'emit("round_hp"' in _combat_source()

    class _State:
        turn = 3
        log = [{"turn": 1, "event": "round_hp", "hp": 70},
               {"turn": 2, "event": "round_hp", "hp": 55},
               {"turn": 3, "event": "fight_end", "won": True, "turns": 3}]

        class player:
            hp = 55
    stats = metrics.extract(_State(), hp_start=80)
    assert stats.hp_by_round == [70, 55]
    assert stats.hp_end == 55


def test_merged_stages_concatenate_their_trajectories():
    """A gauntlet's HP curve runs continuously across the stage break."""
    def _stage(rounds, hp_start, hp_end):
        return metrics.FightStats(
            won=True, turns=len(rounds), hp_start=hp_start, hp_end=hp_end,
            total_damage_dealt=0, damage_by_turn={}, energy_by_turn={},
            total_block_gained=0, damage_blocked=0, energy_spent=0,
            cards_drawn_extra=0, energy_generated_extra=0, healing=0,
            encore_absorbed=0, debuff_stacks_applied=0, debuffed_intents=0,
            aura_intents=0, total_intents=0, reactions=0, reaction_damage=0,
            auras_wasted=0, hp_by_round=list(rounds))

    merged = metrics.merge_stages([_stage([70, 60], 80, 60),
                                   _stage([50, 40], 60, 40)])
    assert merged.hp_by_round == [70, 60, 50, 40]


def _combat_source() -> str:
    import inspect
    return inspect.getsource(combat._run_rounds)
