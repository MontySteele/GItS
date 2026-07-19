"""M2: axis computation, gauntlet stage-merge, frozen-battery regression."""

import pytest

from tier0.harness import axes, metrics
from tier0.harness.runner import run_battery, score_config

FIGHTS = 150   # small but stable enough for the wide bounds below
SEED = 11


@pytest.fixture(scope="module")
def baseline():
    return score_config("ref_ironclad", "starter", "generic", FIGHTS, SEED)


@pytest.fixture(scope="module")
def package():
    return score_config("ref_ironclad", "archetype_package", "generic",
                        FIGHTS, SEED)


def test_baseline_scores_are_exactly_three(baseline):
    for ax, v in baseline["scores"].items():
        assert v == pytest.approx(3.0), ax


def test_baseline_has_no_heuristic_flags(baseline):
    assert baseline["heuristic_flags"] == []


def test_package_deck_scales_better_than_starter(package, baseline):
    # Strength ramp is the package's whole identity: A2 must move up.
    # Note the exponent itself is negative for BOTH decks (late-fight
    # energy shifts to blocking as the boss ramps) — only the relative
    # comparison is meaningful.
    assert package["scores"]["A2_scaling"] > 3.0
    assert package["curve_exponent"] > baseline["curve_exponent"]


def test_package_deck_beats_starter_on_tank_boss(package):
    wr = metrics.summarize(package["stats"]["tank_boss"])["winrate"]
    assert wr > 0.5


def test_gauntlet_merges_stages():
    stats = run_battery("ref_ironclad", "starter", "gauntlet", "generic",
                        20, SEED)
    swarm = run_battery("ref_ironclad", "starter", "swarm", "generic",
                        20, SEED)
    # Gauntlet fights must be longer than swarm alone (second stage exists)
    assert (sum(s.turns for s in stats) / 20
            > sum(s.turns for s in swarm) / 20)
    # HP carryover: gauntlet is strictly harder than punisher alone.
    punisher = run_battery("ref_ironclad", "starter", "punisher", "generic",
                           200, SEED)
    gauntlet = run_battery("ref_ironclad", "starter", "gauntlet", "generic",
                           200, SEED)
    assert (metrics.summarize(gauntlet)["winrate"]
            < metrics.summarize(punisher)["winrate"])


# --- frozen battery regression (recalibrating requires editing these) ---

@pytest.mark.parametrize("enc,lo,hi", [
    ("punisher", 0.40, 0.70),      # target 50-60%
    ("swarm", 0.95, 1.01),
    ("attrition", 0.95, 1.01),
    ("tank_boss", -0.01, 0.10),    # starter loses to the boss by design
])
def test_frozen_battery_starter_winrates(enc, lo, hi):
    stats = run_battery("ref_ironclad", "starter", enc, "generic", 300, SEED)
    wr = metrics.summarize(stats)["winrate"]
    assert lo < wr < hi, f"{enc}: {wr} outside frozen calibration band"


def test_frozen_battery_fight_lengths():
    swarm = metrics.summarize(run_battery(
        "ref_ironclad", "starter", "swarm", "generic", 300, SEED))
    assert 5 <= swarm["avg_turns"] <= 7.5
    attr = metrics.summarize(run_battery(
        "ref_ironclad", "starter", "attrition", "generic", 300, SEED))
    assert attr["avg_turns"] >= 12
    boss = metrics.summarize(run_battery(
        "ref_ironclad", "starter", "tank_boss", "generic", 300, SEED))
    assert boss["avg_turns"] >= 10     # A2 needs turn-10 data


def test_a7_self_referential_sanity(baseline):
    # Review ruling #3: REF_IRONCLAD starter reaches 70% of its own peak
    # window within the first few turns (no engine to assemble).
    assert baseline["raw"]["A7_setup_tax"] < 6


def test_heuristic_flag_logic():
    flat = {ax: 3.0 for ax in axes.AXES}
    assert any("FLAT" in f for f in axes.heuristic_flags(flat))
    assert any("NO_WEAKNESS" in f for f in axes.heuristic_flags(flat))
    healthy = dict(flat, A1_frontload=4.5, A6_utility=4.2, A2_scaling=1.5)
    assert axes.heuristic_flags(healthy) == []
