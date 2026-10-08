"""EB-118 2C with the mode chooser ON: which body a `choose_one` resolves.

THIS IS NOW THE SHIPPED WORLD. `MODE_CHOOSER_ENABLED` is True since the
Phase-2C activation window closed (2026-08-24, `POLICY_VERSION` 9,
`PILOT_WEIGHTS_VERSION` 4), so the fixture below asserts the default rather
than departing from it -- and it is KEPT rather than deleted, because a switch
that has moved once may move again and a test that names its world stays
readable when it does. `test_eb118_switch_off` holds the other half: the
legacy fixed-index path, still live behind the flag.

The flag is 2C's OWN, not the 2A pair's `PILOT_POLICIES_ENABLED`: R191 ruled
the chooser takes its own activation window, and the 2A pair flipped first in
the ruled sequence, so a shared flag would have activated this policy inside
2A's window. The two are independent here on purpose.

Boards are built to vary ONE thing. Where a term is not what a test is about
it is neutralised on both sides, so a pass here is a statement about the term
named in the test and not about the sum.
"""

import pytest

from tier0.engine import effects
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


@pytest.fixture
def chooser_on(monkeypatch):
    monkeypatch.setattr(policy, "MODE_CHOOSER_ENABLED", True)


def card(**kw) -> Card:
    base = dict(id="t", name="t", cost=1, type="skill")
    base.update(kw)
    return Card(**base)


def modal(*bodies, labels=None) -> dict:
    names = labels or [f"mode {chr(ord('A') + i)}" for i in range(len(bodies))]
    return {"op": "choose_one",
            "modes": [{"label": n, "effects": list(b)}
                      for n, b in zip(names, bodies)]}


BLOCK_5 = [{"op": "block", "amount": 5}]
HIT_9 = [{"op": "damage", "amount": 9, "target": "enemy"}]
DRAW_2 = [{"op": "draw", "amount": 2}]


# --- (1) argmax over the existing valuations -------------------------------

def test_the_chooser_takes_the_better_mode_not_the_first(chooser_on):
    """The inversion the placeholder could not make. Mode A is first and
    worse; a fixed index would take it."""
    state = make_state([make_enemy(hp=60)])
    assert policy.choose_mode(state, modal(BLOCK_5, HIT_9)["modes"]) == 1


def test_the_same_pair_flips_when_the_board_flips(chooser_on):
    """Not a static ranking of two bodies: Block is worth the damage it
    actually prevents, so an enemy winding up for a big swing makes the
    defensive mode the right one and a sleeping enemy makes it worthless.
    Same modes, same order, opposite answers."""
    heavy = make_enemy(hp=60, intents=[{"kind": "attack", "amount": 30}])
    quiet = make_enemy(hp=60, intents=[{"kind": "block", "amount": 5}])
    modes = modal([{"op": "block", "amount": 12}], HIT_9)["modes"]
    assert policy.choose_mode(make_state([heavy]), modes) == 0
    assert policy.choose_mode(make_state([quiet]), modes) == 1


def test_the_engine_resolves_the_mode_the_chooser_names(chooser_on):
    """End to end, through the seam rather than through the policy: the mode
    that resolves is the one the chooser picked."""
    state = make_state([make_enemy(hp=60)])
    effects.resolve_card(state, card(effects=[modal(BLOCK_5, HIT_9)]))
    assert state.enemies[0].hp == 51
    assert state.player.block == 0
    assert [e["index"] for e in state.log
            if e["event"] == "mode_chosen"] == [1]


def test_the_pilot_forecast_agrees_with_the_mode_that_resolves(chooser_on):
    """`_active_effects` has no host card to offer the chooser and the engine
    does, so this is the pin that says the score never needed one."""
    state = make_state([make_enemy(hp=60)])
    fx = modal(BLOCK_5, HIT_9)
    assert list(policy._active_effects(state, [fx])) == HIT_9


# --- (2) the tie-break, and the placeholder as its degenerate case ---------

def test_ties_go_to_the_lowest_index(chooser_on):
    """Two bodies worth exactly the same. The earlier one wins, always, so a
    replay of the same board takes the same mode."""
    state = make_state([make_enemy(hp=60)])
    modes = modal(DRAW_2, list(DRAW_2))["modes"]
    assert policy.choose_mode(state, modes) == 0


def test_a_later_mode_must_BEAT_the_incumbent_not_match_it(chooser_on):
    """The rule stated as code reads `score > best + eps`. Float noise must
    not decide a mode: two bodies whose scores differ below the epsilon are a
    tie and resolve to the earlier one."""
    state = make_state([make_enemy(hp=60)])
    modes = [{"label": "a", "effects": DRAW_2},
             {"label": "b", "effects": DRAW_2}]
    scores = iter([1.0, 1.0 + policy.MODE_TIE_EPSILON / 2])
    original = policy.mode_score
    try:
        policy.mode_score = lambda st, mode: next(scores)
        assert policy.choose_mode(state, modes) == 0
    finally:
        policy.mode_score = original


def test_the_placeholder_index_is_the_degenerate_case(chooser_on):
    """R191's contract point 2, as an assertion. Modes the chooser can say
    NOTHING about all score zero, the tie-break takes the lowest index, and
    the lowest index is the fixed 0 the seam was staged with. The pre-flip
    behaviour is reproduced BY the rule, not preserved beside it."""
    state = make_state([make_enemy(hp=60)])
    unscored = [{"op": "apply_aura", "element": "hydro", "target": "enemy"}]
    modes = modal(unscored, list(unscored), list(unscored))["modes"]
    assert [policy.mode_score(state, m) for m in modes] == [0.0, 0.0, 0.0]
    assert policy.choose_mode(state, modes) == 0


def test_the_choice_is_deterministic_across_repeats(chooser_on):
    """No rng anywhere in the chooser: the same board answers the same way
    every time, which is what a seeded replay depends on."""
    modes = modal(BLOCK_5, HIT_9, DRAW_2)["modes"]
    picks = {policy.choose_mode(make_state([make_enemy(hp=60)]), modes)
             for _ in range(20)}
    assert picks == {1}


# --- (3) the frame is not scored -------------------------------------------

def test_the_host_card_cannot_change_the_pick(chooser_on):
    """Contract point 5, as arithmetic. The card argument is accepted and
    ignored: cost, type and Exhaust are shared by every mode, so pricing them
    could only add a constant -- and a constant that reached one call site
    (the engine's, which has the card) and not the other (the pilot's
    forecast, which does not) is how the two would come to disagree."""
    state = make_state([make_enemy(hp=60)])
    modes = modal(BLOCK_5, HIT_9)["modes"]
    plain = policy.choose_mode(state, modes)
    for host in (card(cost=0, exhaust=True), card(cost=3, type="attack"),
                 None):
        assert policy.choose_mode(state, modes, host) == plain
