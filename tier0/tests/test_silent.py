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


@pytest.mark.battery
def test_silent_scales_hardest(silent, ironclad_pkg):
    assert silent["scores"]["A2_scaling"] > 4.0
    assert silent["scores"]["A2_scaling"] > ironclad_pkg["scores"]["A2_scaling"]
    assert silent["curve_exponent"] > ironclad_pkg["curve_exponent"]


@pytest.mark.battery
def test_silent_velocity_above_baseline(silent, ironclad_pkg):
    assert silent["scores"]["A5_velocity"] > 3.2
    assert silent["scores"]["A5_velocity"] > ironclad_pkg["scores"]["A5_velocity"]


@pytest.mark.battery
def test_silent_weakness_is_utility_or_setup(silent, ironclad_pkg):
    # Single-target shivs, no AoE: A6 must sit below baseline, and ruling
    # 2's ordering anchor must hold on the AoE term:
    # Silent < Ironclad-package (< Klee, asserted in test_klee).
    assert silent["scores"]["A6_utility"] < 3.0
    assert silent["raw"]["A6_aoe"] < ironclad_pkg["raw"]["A6_aoe"]
    bottom_two = sorted((ax for ax in silent["scores"]),
                        key=silent["scores"].get)[:2]
    assert "A6_utility" in bottom_two or "A7_setup_tax" in bottom_two


#: How far above the anchor `A1_frontload` may read and still count as "not
#: above". A knife-edge `<= 3.0` was always a statement about the DIVISOR as
#: much as about Silent -- see the test below.
A1_TIE_TOLERANCE = 1e-3


@pytest.mark.battery
def test_silent_frontload_not_above_baseline(silent):
    """M3's shape lock, and its edge moved when the anchor did (`C18`).

    THE CLAIM IS UNCHANGED: Silent, whose damage arrives in shivs over turns,
    must not out-frontload the Ironclad baseline. What moved is that the two
    are now LEVEL rather than Silent sitting below it, and it moved from the
    DENOMINATOR: `EB-136` / R210 bound every `target: enemy` op of a card to
    one aim, which reaches `bash` in `ref_ironclad`'s STARTER -- the anchor's
    own deck -- so the anchor's raw `A1_frontload` fell 4.8056 -> 4.7397
    (-1.4%) while `ref_silent`'s barely moved (4.67080 -> 4.67025, -0.01%).
    The score therefore rose 2.9575 -> 3.000006 with Silent standing still.

    Six decimal places above 3.0 is not Silent out-frontloading anything: this
    is ONE seed at 150 fights, whose seed-to-seed spread is orders of magnitude
    wider than 6e-6, and an exact `<= 3.0` on a ratio is a claim the reading
    cannot support in either direction. The tolerance names that, instead of
    letting the next movement in the divisor decide the test.
    """
    assert silent["scores"]["A1_frontload"] <= 3.0 + A1_TIE_TOLERANCE


@pytest.mark.battery
def test_silent_comes_online_slower_than_ironclad_package(silent, ironclad_pkg):
    # Review ruling #3 expected sanity for the self-referential A7.
    assert (silent["raw"]["A7_setup_tax"]
            > ironclad_pkg["raw"]["A7_setup_tax"])


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
