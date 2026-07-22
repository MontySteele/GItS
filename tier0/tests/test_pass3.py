"""Pass-3 ruling verification (docs/pass2-rulings-round3.md)."""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.harness import metrics
from tier0.harness.runner import run_battery, score_character

# Band/median checks run at canonical scorecard parameters — at low
# fight counts the A2 band is noise-marginal (3.59 vs 3.36 canonical).
FIGHTS = 300
SEED = 42


@pytest.fixture(scope="module")
def klee_report():
    return score_character("klee", FIGHTS, SEED)


def test_boom_rework_is_amp_nuke():
    boom = loader.get_card("boom_goes_the_dynamite")    # sheet v0.3
    assert boom.effects[0]["amount"] == 18               # survival sprint B
    assert boom.effects[1]["then"][0]["op"] == "repeat_this"


def test_reaction_solo_floors():
    # Ruling: co-op-primary archetype, accepted solo floors.
    tb = metrics.summarize(run_battery("klee", "reaction_weighted",
                                       "tank_boss", "reaction", 300, 42))
    ga = metrics.summarize(run_battery("klee", "reaction_weighted",
                                       "gauntlet", "reaction", 300, 42))
    assert tb["winrate"] >= 0.35, tb
    assert ga["winrate"] >= 0.75, ga


def test_median_identity_evaluation(klee_report):
    # Heuristic + A1>A2 are judged on starter + archetype median.
    assert klee_report["median_flags"] == [], klee_report["median_flags"]
    m = klee_report["median_scores"]
    assert m["A1_frontload"] > m["A2_scaling"]


def test_per_deck_a2_bands(klee_report):
    bands = loader.deck_bands("klee")["A2_scaling"]
    for deck, cap in bands.items():
        score = klee_report["per_deck"][deck]["scores"]["A2_scaling"]
        assert score <= cap, (deck, score, cap)
        assert not any("BAND EXCEEDED" in f
                       for f in klee_report["per_deck"][deck]["heuristic_flags"])


def test_packages_have_no_hard_constraint_flags(klee_report):
    for deck, result in klee_report["per_deck"].items():
        if deck == "starter":
            continue
        assert not any("CONSTRAINT VIOLATED" in f
                       for f in result["heuristic_flags"]), (deck, result)


def test_splash_proc_cap_armed_and_functional():
    # ARMED (was dormant round 3) by the errata/M5 triage ruling 1: the
    # sanctioned demolition ceiling knob, codified in sheet v0.4.
    from tier0.engine import effects
    from tier0.engine.state import Bomb
    from tier0.tests.conftest import make_enemy, make_state
    assert C.DETONATION_SPLASH_PROC_CAP == 3

    st = make_state(enemies=[make_enemy(hp=200, name="a"),
                             make_enemy(hp=200, name="b")])
    st.player.powers["detonation_splash"] = 3
    st.splash_procs_this_turn = 0
    st.enemies[0].bombs = [Bomb(damage=5) for _ in range(5)]
    effects.detonate_bombs(st, st.enemies[0])
    splashes = [e for e in st.log
                if e["event"] == "damage"
                and e.get("source") == "detonation_splash"]
    # 5 detonations, cap 3 -> 3 procs x 2 enemies = 6 splash events
    assert len(splashes) == 6
