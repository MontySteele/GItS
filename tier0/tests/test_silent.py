"""M3: REF_SILENT validity check (spec §7). If Silent doesn't look like
Silent, the axes are miscomputed — these tests lock the shape."""

import pytest

from tier0.engine import effects
from tier0.engine.state import Card
from tier0.harness.runner import score_config
from tier0.tests.conftest import make_state

FIGHTS = 150
SEED = 11


@pytest.fixture(scope="module")
def silent():
    return score_config("ref_silent", "shiv_package", "generic", FIGHTS, SEED)


@pytest.fixture(scope="module")
def ironclad_pkg():
    return score_config("ref_ironclad", "archetype_package", "generic",
                        FIGHTS, SEED)


def test_silent_scales_hardest(silent, ironclad_pkg):
    assert silent["scores"]["A2_scaling"] > 4.0
    assert silent["scores"]["A2_scaling"] > ironclad_pkg["scores"]["A2_scaling"]
    assert silent["curve_exponent"] > ironclad_pkg["curve_exponent"]


def test_silent_velocity_above_baseline(silent, ironclad_pkg):
    assert silent["scores"]["A5_velocity"] > 3.2
    assert silent["scores"]["A5_velocity"] > ironclad_pkg["scores"]["A5_velocity"]


def test_silent_weakness_is_utility(silent):
    # Single-target shivs, no AoE: A6 must be the statline hole.
    assert silent["scores"]["A6_utility"] <= 2.5
    assert min(silent["scores"], key=silent["scores"].get) == "A6_utility"


def test_silent_frontload_not_above_baseline(silent):
    assert silent["scores"]["A1_frontload"] <= 3.0


def test_tag_damage_power_scopes_to_tag():
    st = make_state()
    st.player.powers["tag_damage_shiv"] = 4
    shiv = Card(id="shiv", name="s", cost=0, type="attack", tags=["shiv"],
                effects=[{"op": "damage", "amount": 4, "target": "enemy"}])
    effects.resolve_card(st, shiv)
    assert st.enemies[0].hp == 42          # 50 - (4+4)
    strike = Card(id="strike", name="s", cost=1, type="attack",
                  effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    effects.resolve_card(st, strike)
    assert st.enemies[0].hp == 36          # untagged: no bonus
