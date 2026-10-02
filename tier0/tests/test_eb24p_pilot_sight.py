"""EB-24p — the pilot reads `reaction_triggered_this_turn` (POLICY 5).

`policy._active_effects` skips the WHOLE conditional for a predicate not on
its allowlist — both branches, including an unconditional else. With
`reaction_triggered_this_turn` unlisted, `audience_participation`'s honest
else-glue (2 Encore + 1 draw) scored ~0 and the card measured drawn 974 /
played 0 (EB-20 census;
`git show 12f4a21:review/active/eb24-dead-riders-worksheet.md`).
These pinned the read on the real sheet card; since legacy cleanup stage 6
deleted that sheet, they pin it on the card's shape, with Block in place of
the retired Encore, both branch states.
"""

from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


def _ops(state, card):
    return [fx["op"] for fx in policy._active_effects(state, card.effects)]


def _crowd_answers():
    """The retired `audience_participation`'s shape."""
    return Card(id="audience_participation", name="The Crowd Answers",
                cost=1, type="skill", effects=[
                    {"op": "conditional", "if": "reaction_triggered_this_turn",
                     "then": [{"op": "block", "amount": 4},
                              {"op": "draw", "amount": 2}],
                     "else": [{"op": "block", "amount": 2},
                              {"op": "draw", "amount": 1}]}])


def test_the_pilot_sees_the_else_glue_on_a_quiet_turn():
    st = make_state(enemies=[make_enemy(hp=50)])
    card = _crowd_answers()
    st.reactions_this_turn = 0
    # The defect state was []: the whole conditional skipped, every value
    # term seeing a card with no effects.
    assert _ops(st, card) == ["block", "draw"]
    amounts = [fx["amount"]
               for fx in policy._active_effects(st, card.effects)]
    assert amounts == [2, 1]


def test_the_pilot_sees_the_reaction_payoff_when_the_window_is_open():
    st = make_state(enemies=[make_enemy(hp=50)])
    card = _crowd_answers()
    st.reactions_this_turn = 2
    amounts = [fx["amount"]
               for fx in policy._active_effects(st, card.effects)]
    assert _ops(st, card) == ["block", "draw"]
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
