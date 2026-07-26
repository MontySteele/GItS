"""Frail: a real DECAYING debuff that reduces the AFFECTED creature's
BLOCK GAINED by 25% (StS Frail). Not mapped to Weak (that is -damage
dealt). Run-model rework §4/§8.

HARD RULE 7 lock: each assertion below FAILS against the pre-rework code
(no `frail` power wired) -- the bug it catches is "frail is inert / block
is not reduced".
"""

from tier0.engine import effects, powers
from tier0.tests.conftest import make_state
from tier0.engine.state import Card


def _block_card(amount):
    return Card(id="t", name="t", cost=1, type="skill",
                effects=[{"op": "block", "amount": amount}])


def test_frail_reduces_card_block_gained():
    st = make_state()
    p = st.player
    p.powers["frail"] = 1
    effects.resolve_card(st, _block_card(8))
    # StS Frail floors block*0.75: floor(8 * 0.75) == 6, not 8.
    assert p.block == 6


def test_no_frail_full_block():
    st = make_state()
    effects.resolve_card(st, _block_card(8))
    assert st.player.block == 8


def test_frail_decays_like_weak(state):
    p = state.player
    p.powers["frail"] = 2
    powers.on_turn_end(state, p)
    assert p.powers["frail"] == 1
    powers.on_turn_end(state, p)
    assert p.powers.get("frail", 0) == 0


def test_frail_helper_reduces_amount(state):
    p = state.player
    p.powers["frail"] = 1
    assert powers.modify_block_gained(p, 8) == 6
    assert powers.modify_block_gained(p, 10) == 7   # floor(7.5)
    p.powers["frail"] = 0
    assert powers.modify_block_gained(p, 8) == 8
