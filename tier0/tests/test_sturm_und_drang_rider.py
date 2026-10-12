"""STURM UND DRANG'S RIDER, A SEPARATE HIT (the Varka round 3 fix,
2026-10-10; review/records/varka-round-3-2026-10-10.md, item 1).

The rider used to replace the Attack's element with the Swirled one, so for
Varka every Swirl armed a rider that cancelled his next Swirl. Now the Attack
keeps its own element and the rider's 6 lands after it as a separate hit of
the Swirled element. The card text is unchanged. Lightning Fang's INSTEAD
override (a different card) is untouched.
"""
from __future__ import annotations

from tier0.engine import effects
from tier0.tests.test_varka_oath import (_enemy, _play, _state, _vk,  # noqa: F401
                                         varka)


def test_crosswind_after_a_swirl_with_the_rider_armed_still_swirls(varka):
    st = _state(enemies=[_enemy(name="a", aura="pyro")], fang=False)
    st.player.powers["mc_swirl_charge"] = 6
    st.player.mc_swirl_element = "hydro"
    block = st.player.block
    _play(st, _vk("crosswind"))
    # "If it Swirls, gain 5 Block": the Anemo hit Swirled the Pyro aura.
    assert st.player.block == block + 5
    # The old charge was spent; the Swirl it made banks no new one (no
    # Sturm und Drang standing), and the rider's Hydro hit landed after.
    assert "mc_swirl_charge" not in st.player.powers
    e = st.enemies[0]
    assert e.aura == "hydro"
    # Exactly 6 more than the same Crosswind with no charge banked.
    bare = _state(enemies=[_enemy(name="a", aura="pyro")], fang=False)
    _play(bare, _vk("crosswind"))
    assert e.hp == bare.enemies[0].hp - 6


def test_crosswind_with_sturm_und_drang_standing_rebanks_for_the_next(varka):
    st = _state(enemies=[_enemy(name="a", aura="cryo")], fang=False)
    st.player.powers["mc_sturm_und_drang"] = 6
    st.player.powers["mc_swirl_charge"] = 6
    st.player.mc_swirl_element = "electro"
    _play(st, _vk("crosswind"))
    # This Crosswind Swirled the Cryo: a fresh charge, of Cryo, waits for
    # the next Attack; the spent one landed as Electro.
    assert st.player.powers["mc_swirl_charge"] == 6
    assert st.player.mc_swirl_element == "cryo"
    assert st.enemies[0].aura == "electro"


def test_lightning_fang_still_overrides_instead(varka):
    st = _state(fang=False)
    st.player.powers["mc_lightning_fang"] = 2
    st.player.powers["mc_swirl_charge"] = 6
    st.player.mc_swirl_element = "hydro"
    from tier0.content import loader
    card = loader.get_card(_vk("crosswind"))
    assert effects.companion_overhaul_card_start(st, card) == "electro"


# --- the turn-start Swirl (the 2026-10-11 Companion pass) ------------------
#
# "At the start of your turn, Swirl a random enemy." A Swirl source of its own,
# so a deck that rarely Swirls still banks the rider.


def test_sturm_und_drang_swirls_a_random_enemy_at_turn_start(varka):
    st = _state(enemies=[_enemy(name="a", aura="pyro")], fang=False)
    st.player.powers["mc_sturm_und_drang"] = 6
    swirls = st.mi_swirls_this_turn
    effects.companion_overhaul_turn_start(st)
    # The Pyro was Swirled, and that Swirl banked the rider in Pyro.
    assert st.mi_swirls_this_turn == swirls + 1
    assert st.player.powers["mc_swirl_charge"] == 6
    assert st.player.mc_swirl_element == "pyro"


def test_sturm_und_drang_turn_start_swirl_is_once_per_turn(varka):
    """The stack is the rider's damage; copies bank more, not Swirl twice."""
    st = _state(enemies=[_enemy(name="a", aura="hydro"),
                         _enemy(name="b", aura="hydro")], fang=False)
    st.player.powers["mc_sturm_und_drang"] = 12
    swirls = st.mi_swirls_this_turn
    effects.companion_overhaul_turn_start(st)
    assert st.mi_swirls_this_turn == swirls + 1
    assert st.player.powers["mc_swirl_charge"] == 12


def test_no_sturm_und_drang_no_turn_start_swirl(varka):
    st = _state(enemies=[_enemy(name="a", aura="pyro")], fang=False)
    effects.companion_overhaul_turn_start(st)
    assert st.enemies[0].aura == "pyro"
    assert "mc_swirl_charge" not in st.player.powers
