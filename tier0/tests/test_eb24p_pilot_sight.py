"""EB-24p — the pilot reads `reaction_triggered_this_turn` (POLICY 5).

`policy._active_effects` skips the WHOLE conditional for a predicate not on
its allowlist — both branches, including an unconditional else. With
`reaction_triggered_this_turn` unlisted, `audience_participation`'s honest
else-glue (2 Encore + 1 draw) scored ~0 and the card measured drawn 974 /
played 0 (EB-20 census;
`git show 12f4a21:review/active/eb24-dead-riders-worksheet.md`).
These pin the read on the real sheet card, both branch states.
"""

from tier0.content import loader
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


def _ops(state, card):
    return [fx["op"] for fx in policy._active_effects(state, card.effects)]


def test_the_pilot_sees_the_else_glue_on_a_quiet_turn():
    st = make_state(enemies=[make_enemy(hp=50)])
    card = loader.get_card("audience_participation")
    st.reactions_this_turn = 0
    # The defect state was []: the whole conditional skipped, every value
    # term seeing a card with no effects.
    assert _ops(st, card) == ["gain_encore", "draw"]
    amounts = [fx["amount"]
               for fx in policy._active_effects(st, card.effects)]
    assert amounts == [2, 1]


def test_the_pilot_sees_the_reaction_payoff_when_the_window_is_open():
    st = make_state(enemies=[make_enemy(hp=50)])
    card = loader.get_card("audience_participation")
    st.reactions_this_turn = 2
    amounts = [fx["amount"]
               for fx in policy._active_effects(st, card.effects)]
    assert _ops(st, card) == ["gain_encore", "draw"]
    assert amounts == [4, 2]


def test_mid_resolution_predicates_stay_excluded():
    # reaction_triggered_by_this is NOT knowable at score time; the fix must
    # not have widened past the turn-level counter.
    st = make_state(enemies=[make_enemy(hp=50)])
    st.reactions_this_turn = 5
    gated = [{"op": "conditional", "if": "reaction_triggered_by_this",
              "then": [{"op": "damage", "amount": 99}],
              "else": [{"op": "block", "amount": 99}]}]
    assert list(policy._active_effects(st, gated)) == []
