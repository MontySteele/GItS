"""EB-118 2C with the mode chooser ON: which body a `choose_one` resolves.

Every test here flips `policy.MODE_CHOOSER_ENABLED` for its own duration.
Nothing in the shipped suite runs with it on -- that is the staging contract,
and `test_eb118_switch_off` holds the other half of it.

The flag is 2C's OWN, not the 2A pair's `PILOT_POLICIES_ENABLED`: R191 ruled
the chooser takes its own activation window, and the 2A pair flips first in
the ruled sequence, so a shared flag would activate this policy inside 2A's
window. The two are independent here on purpose.

Boards are built to vary ONE thing. Where a term is not what a test is about
it is neutralised on both sides, so a pass here is a statement about the term
named in the test and not about the sum.
"""

import pytest

from tier0.content import loader
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
SPEND_2_DRAW_2 = [{"op": "spend_encore", "amount": 2},
                  {"op": "draw", "amount": 2}]


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


# --- (2) the overdraw penalty ----------------------------------------------

def test_a_spend_the_bank_covers_is_not_penalised(chooser_on):
    """`spend_encore_or_hp` drains Encore first, so a covered spend costs the
    buffer and no HP -- and the buffer is what `_sustain_value` prices on the
    other side of the ledger. The mode is worth its draw."""
    state = make_state([make_enemy(hp=60)])
    state.player.encore = 8
    modes = modal(SPEND_2_DRAW_2, DRAW_2)["modes"]
    assert policy.mode_score(state, modes[0]) \
        == pytest.approx(policy.mode_score(state, modes[1]))


def test_an_overdrawing_spend_pays_hp_and_loses_the_comparison(chooser_on):
    """The same pair on an EMPTY bank. Two points of TRUE HP at
    MODE_OVERDRAW_HP_VALUE is the whole difference, and it is enough to lose
    to the mode that draws the same two cards for nothing."""
    state = make_state([make_enemy(hp=60)])
    state.player.encore = 0
    modes = modal(SPEND_2_DRAW_2, DRAW_2)["modes"]
    assert policy.mode_score(state, modes[0]) == pytest.approx(
        policy.mode_score(state, modes[1]) - 2 * policy.MODE_OVERDRAW_HP_VALUE)
    assert policy.choose_mode(state, modes) == 1


def test_the_shortfall_is_the_penalty_not_the_spend(chooser_on):
    """A partial bank pays the difference, not the whole spend: one point of
    Encore covered, one point of HP charged."""
    state = make_state([make_enemy(hp=60)])
    state.player.encore = 1
    mode = modal(SPEND_2_DRAW_2)["modes"][0]
    bare = modal(DRAW_2)["modes"][0]
    assert policy.mode_score(state, mode) == pytest.approx(
        policy.mode_score(state, bare) - policy.MODE_OVERDRAW_HP_VALUE)


def test_a_gain_earlier_in_the_same_body_refills_the_bank(chooser_on):
    """The bank is walked in body ORDER because that is what the engine does
    when a gain and a spend sit in one mode -- the gain has already landed by
    the time the spend reads the meter."""
    state = make_state([make_enemy(hp=60)])
    state.player.encore = 0
    refilled = [{"op": "gain_encore", "amount": 2},
                {"op": "spend_encore", "amount": 2}]
    assert policy._mode_overdraw_hp(state, {"effects": refilled}) == 0.0
    assert policy._mode_overdraw_hp(
        state, {"effects": list(reversed(refilled))}) == 2.0


def test_the_overdraw_penalty_survives_resolution(chooser_on):
    """Not only a score: the mode the chooser declined is the one that would
    have cost HP, and taking the other one costs none."""
    state = make_state([make_enemy(hp=60)])
    state.player.encore = 0
    effects.resolve_card(state, card(effects=[modal(SPEND_2_DRAW_2, DRAW_2)]))
    assert state.player.hp == 80
    assert not [e for e in state.log if e["event"] == "encore_overdraw"]


# --- (3) the tie-break, and the placeholder as its degenerate case ---------

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


# --- (4) the frame is not scored -------------------------------------------

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


# --- (5) the shipped prototype ---------------------------------------------

def _deep_breath_modes():
    return loader._card_index()["deep_breath"].effects[0]["modes"]


@pytest.mark.parametrize("bank", [0, 1, 2, 5, 20])
def test_deep_breath_takes_mode_1_on_every_bank(chooser_on, bank):
    """THE HONEST READING, PINNED SO IT CANNOT BE MISTAKEN FOR A NULL RESULT.

    Under the hand-picked weights the ruled pair is DOMINATED: mode 1 scores
    `energy 1` + `gain_encore 2` = 1.0 + 1.6 = 2.6 with no state-dependent
    term in it, and mode 2 tops out at `draw 2` = 2.0 with a full bank and
    falls from there as the overdraw penalty bites. The gap is at least 0.6
    whatever the board looks like, so the chooser takes mode 1 always.

    That is a real reading of the pilot's currency, not a broken chooser --
    and it means throwing 2C's switch is expected to move NO Furina number
    until the weights are swept in 2C's own window (the W4 pattern, R191) or
    the pair is redesigned. This test is here so that a null measurement is
    read as "the pair is dominated" rather than "modal cards are neutral".
    """
    state = make_state([make_enemy(hp=60)])
    state.player.encore = bank
    modes = _deep_breath_modes()
    assert policy.choose_mode(state, modes) == 0
    assert policy.mode_score(state, modes[0]) \
        >= policy.mode_score(state, modes[1]) + 0.6


def test_deep_breath_mode_1_resolves_as_the_pre_conversion_card(chooser_on):
    """Which is why the conversion is quiet in both engines: the mode the
    pilot takes IS the body the card shipped with, so the sheet edit changes
    what the player MAY do without changing what the sim DOES."""
    state = make_state([make_enemy(hp=60)])
    state.player.energy = 3
    state.player.encore = 4
    effects.resolve_card(state, loader._card_index()["deep_breath"])
    assert (state.player.energy, state.player.encore) == (4, 6)
    assert state.player.hp == 80
