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

def _deep_breath_modes(face="deep_breath"):
    return loader.get_card(face).effects[0]["modes"]


# The crossover, as arithmetic. Mode 1 is `energy 1` + `gain_encore 2` =
# 1.0 + 1.6 = 2.6 and carries NO state-dependent term, so it is flat at every
# bank. Mode 2 is `draw 3` = 3.0 minus the shortfall the bank cannot cover, at
# MODE_OVERDRAW_HP_VALUE = 1.0 a point.
DEEP_BREATH_SCORES = {0: (2.6, 0.0), 1: (2.6, 1.0), 2: (2.6, 2.0),
                      3: (2.6, 3.0), 4: (2.6, 3.0), 5: (2.6, 3.0),
                      8: (2.6, 3.0), 20: (2.6, 3.0)}


@pytest.mark.parametrize("face", ["deep_breath", "deep_breath+"])
@pytest.mark.parametrize("bank", sorted(DEEP_BREATH_SCORES))
def test_deep_breath_crosses_over_at_a_bank_of_three(chooser_on, face, bank):
    """THE CROSSOVER, PINNED ON BOTH FACES AND ACROSS THE BANK.

    THIS PIN IS AN INVERSION AND SAYS SO. It replaces one that asserted the
    chooser took mode 1 on EVERY bank, and whose prose read a null at
    activation as "this pair is dominated". That was an honest reading of the
    pair as R194 ratified it -- `spend 2 / draw 2` topped out at 2.0 against a
    flat 2.6 -- and it is FALSIFIED as a description of the shipped card,
    because R205 re-bodied mode 2 to `spend 3 / draw 3` for exactly this
    reason. A dominated pair is not a fact about modal cards; it was a fact
    about two numbers, and the numbers moved.

    What the re-body bought is a board for each mode: 3.0 when the bank can
    pay the spend, 2.0 at a one-point shortfall, so mode 2 wins at a bank of
    3 or more and loses below it. The rate is unchanged at one card per
    Encore -- this is a bigger transaction, not a better exchange.

    BOTH FACES, and the reason they agree is structural rather than lucky:
    the upgrade delta is `{cost: -1}`, `mode_score` reads the mode BODY on a
    neutral frame (`_mode_probe`), and a frame the choice does not select
    cannot move the argmax. A 0-cost Deep Breath that still Exhausts chooses
    exactly as the 1-cost one does.
    """
    state = make_state([make_enemy(hp=60)])
    state.player.encore = bank
    modes = _deep_breath_modes(face)
    expect_1, expect_2 = DEEP_BREATH_SCORES[bank]
    assert policy.mode_score(state, modes[0]) == pytest.approx(expect_1)
    assert policy.mode_score(state, modes[1]) == pytest.approx(expect_2)
    assert policy.choose_mode(state, modes) == (1 if bank >= 3 else 0)


def test_the_crossover_is_at_the_spend_and_not_at_a_tuned_number(chooser_on):
    """WHY 3 is the crossover: it is the mode's own printed spend, not a
    constant anyone picked. One point short and the shortfall costs exactly
    one point of TRUE HP, which is what drops mode 2 under mode 1."""
    modes = _deep_breath_modes()
    spend = next(fx["amount"] for fx in modes[1]["effects"]
                 if fx["op"] == "spend_encore")
    below = make_state([make_enemy(hp=60)])
    below.player.encore = spend - 1
    at = make_state([make_enemy(hp=60)])
    at.player.encore = spend
    assert policy.mode_score(at, modes[1]) - policy.mode_score(
        below, modes[1]) == pytest.approx(policy.MODE_OVERDRAW_HP_VALUE)
    assert policy.choose_mode(below, modes) == 0
    assert policy.choose_mode(at, modes) == 1


def test_deep_breath_resolves_the_mode_the_crossover_names(chooser_on):
    """End to end through the seam, on both sides of the crossover. Below it
    the card is the buffer body it always was; at or above it the pilot cashes
    the bank and the spend is covered, so no HP is paid."""
    thin = make_state([make_enemy(hp=60)])
    thin.player.energy, thin.player.encore = 3, 2
    effects.resolve_card(thin, loader.get_card("deep_breath"))
    assert (thin.player.energy, thin.player.encore) == (4, 4)
    assert thin.player.hp == 80

    deep = make_state([make_enemy(hp=60)])
    deep.player.energy, deep.player.encore = 3, 4
    effects.resolve_card(deep, loader.get_card("deep_breath"))
    assert (deep.player.energy, deep.player.encore) == (3, 1)
    assert deep.player.hp == 80
    assert [e["index"] for e in deep.log
            if e["event"] == "mode_chosen"] == [1]
