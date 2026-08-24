"""EB-118 sec.5.4: the generic choose-one / modal effect surface.

STAGED. No shipped card carries a `choose_one`, and the last test in this
file is the pin that says so -- the surface exists, is validated and is
priced, but the battery cannot move because nothing reaches it. The first
card to use it is the Phase-2 prototype, priced with the pilot's real
mode-valuation policy (a POLICY_VERSION move), not here.

The sheet syntax under test:

    {op: choose_one, modes: [
        {label: "Gain 2 Encore",        effects: [{op: gain_encore, amount: 2}]},
        {label: "Spend 2 Encore: draw", effects: [{op: spend_encore, amount: 2},
                                                  {op: draw, amount: 2}]}]}
"""

import pytest

from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import Card
from tier0.pilot import policy
from tier05 import draft
from tools import effect_walk


def card(**kw):
    base = dict(id="t", name="t", cost=1, type="attack")
    base.update(kw)
    return Card(**base)


def modal(*bodies, labels=None):
    """A `choose_one` effect over N mode bodies, labelled A/B/C by default."""
    names = labels or [f"mode {chr(ord('A') + i)}" for i in range(len(bodies))]
    return {"op": "choose_one",
            "modes": [{"label": n, "effects": list(b)}
                      for n, b in zip(names, bodies)]}


# --- resolution ------------------------------------------------------------

def test_the_chosen_mode_resolves_and_the_others_do_not(state):
    c = card(effects=[modal(
        [{"op": "damage", "amount": 6, "target": "enemy"}],
        [{"op": "block", "amount": 6}])])
    effects.resolve_card(state, c)
    assert state.enemies[0].hp == 44
    assert state.player.block == 0


def test_a_mode_body_is_an_ordinary_effect_list(state):
    """Multi-effect bodies resolve in order, and nest like anything else."""
    c = card(effects=[modal(
        [{"op": "block", "amount": 3},
         {"op": "conditional", "if": "has_spark",
          "then": [{"op": "block", "amount": 99}],
          "else": [{"op": "block", "amount": 4}]}],
        [{"op": "damage", "amount": 6, "target": "enemy"}])])
    effects.resolve_card(state, c)
    assert state.player.block == 7


def test_a_mode_body_spends_through_the_overdraw_primitive(state):
    """EB-119, the sim leg of the modal-spend repair.

    The docstring above prints `spend_encore` in mode B and means it: a mode
    body reaches the OVERDRAW primitive, the same one a printed spend rides.
    Nothing about the op changes inside a mode -- which is exactly why the
    generator had to learn to emit it rather than have a fixture paraphrase
    it as a negative gain.
    """
    state.player.encore = 5
    c = card(effects=[modal([{"op": "spend_encore", "amount": 2}],
                            [{"op": "gain_encore", "amount": 2}])])
    effects.resolve_card(state, c)
    assert state.player.encore == 3
    assert state.player.hp == 80
    assert [e["amount"] for e in state.log
            if e["event"] == "encore_spent"] == [2]


def test_a_mode_body_spend_overdraws_into_hp(state):
    """The half the substitution could never have modelled. A spend past the
    buffer drains TRUE HP; a negative `gain_encore` would have clamped at
    zero and charged nothing."""
    state.player.encore = 1
    c = card(effects=[modal([{"op": "spend_encore", "amount": 4}],
                            [{"op": "gain_encore", "amount": 2}])])
    effects.resolve_card(state, c)
    assert state.player.encore == 0
    assert state.player.hp == 77
    assert [e["amount"] for e in state.log
            if e["event"] == "encore_overdraw"] == [3]


# --- the chooser seam ------------------------------------------------------

def test_mode_selection_rides_the_chooser_seam_not_the_rng(state):
    """The placeholder is a fixed index, and it is the ONE door.

    `_chosen_mode` sits beside `_worst_card` / `_best_card` as an INSTRUMENT
    SURFACE, so a future policy replaces one function rather than N call
    sites. Monkeypatching it must move the mode that resolves.
    """
    c = card(effects=[modal(
        [{"op": "block", "amount": 5}],
        [{"op": "damage", "amount": 6, "target": "enemy"}])])
    original = effects._chosen_mode
    try:
        effects._chosen_mode = lambda st, modes, cd: 1
        effects.resolve_card(state, c)
    finally:
        effects._chosen_mode = original
    assert state.enemies[0].hp == 44
    assert state.player.block == 0


def test_the_pilot_forecast_agrees_with_the_mode_that_resolves(state):
    """policy._active_effects must not keep a second copy of the rule."""
    fx = modal([{"op": "block", "amount": 5}],
               [{"op": "draw", "amount": 2}])
    original = effects._chosen_mode
    try:
        effects._chosen_mode = lambda st, modes, cd: 1
        seen = list(policy._active_effects(state, [fx]))
    finally:
        effects._chosen_mode = original
    assert seen == [{"op": "draw", "amount": 2}]


# --- the emit stream -------------------------------------------------------

def test_the_taken_mode_is_recorded_in_the_emit_stream(state):
    """Three fields, so parity and telemetry can read a per-mode take-rate.

    The C# side records the same event name and the same fields; the shape is
    pinned there by klee-mod/KleeTests (ModalChoicePinTests).
    """
    c = card(effects=[modal(
        [{"op": "block", "amount": 5}],
        [{"op": "draw", "amount": 2}],
        labels=["Gain 5 Block", "Draw 2"])])
    effects.resolve_card(state, c)
    chosen = [e for e in state.log if e["event"] == "mode_chosen"]
    assert chosen == [{"turn": state.turn, "event": "mode_chosen",
                       "card": "t", "index": 0, "label": "Gain 5 Block"}]


# --- red: the shape is checked AT LOAD -------------------------------------

def test_one_mode_is_rejected_it_is_not_a_choice():
    with pytest.raises(ValueError, match="at least 2 modes"):
        loader._validate_effect_vocabulary(
            "probe", [modal([{"op": "draw", "amount": 1}])])


def test_zero_modes_is_rejected():
    with pytest.raises(ValueError, match="at least 2 modes"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "choose_one", "modes": []}])


def test_a_missing_modes_list_is_rejected():
    with pytest.raises(ValueError, match="needs a `modes:` list"):
        loader._validate_effect_vocabulary("probe", [{"op": "choose_one"}])


def test_an_unknown_key_inside_a_mode_is_rejected():
    """The `effect:`/`effects:` typo class -- it would resolve as an empty
    mode rather than raising, so the load-time key set is the only catch."""
    with pytest.raises(ValueError, match="unknown mode keys"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "choose_one", "modes": [
                {"label": "a", "effect": [{"op": "draw", "amount": 1}]},
                {"label": "b", "effects": [{"op": "draw", "amount": 1}]}]}])


def test_an_unknown_key_on_the_modal_itself_is_rejected():
    with pytest.raises(ValueError, match="unknown modal fields"):
        loader._validate_effect_vocabulary(
            "probe", [dict(modal([{"op": "draw", "amount": 1}],
                                 [{"op": "draw", "amount": 2}]),
                           **{"if": "has_spark"})])


def test_a_mode_needs_a_label_the_label_is_the_card_text():
    with pytest.raises(ValueError, match="non-empty `label:`"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "choose_one", "modes": [
                {"label": "", "effects": [{"op": "draw", "amount": 1}]},
                {"label": "b", "effects": [{"op": "draw", "amount": 1}]}]}])


def test_a_mode_needs_a_non_empty_effects_list():
    with pytest.raises(ValueError, match="non-empty `effects:`"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "choose_one", "modes": [
                {"label": "a", "effects": []},
                {"label": "b", "effects": [{"op": "draw", "amount": 1}]}]}])


def test_validation_recurses_into_mode_bodies():
    with pytest.raises(ValueError, match="unknown op"):
        loader._validate_effect_vocabulary(
            "probe", [modal([{"op": "draw", "amount": 1}],
                            [{"op": "no_such_op"}])])


def test_validation_recurses_into_a_conditional_inside_a_mode():
    with pytest.raises(ValueError, match="unknown predicate"):
        loader._validate_effect_vocabulary(
            "probe", [modal([{"op": "draw", "amount": 1}],
                            [{"op": "conditional", "if": "no_such_predicate",
                              "then": [{"op": "draw", "amount": 1}]}])])


# --- red: a negative gain is not a spend (EB-119) --------------------------

def test_a_non_positive_gain_encore_is_rejected():
    """`gain_encore: -2` reads as a spend and is not one. It is INERT in the
    mod (FurinaResources.GainEncore returns on `amount <= 0`) while the sim
    would move the meter, so a row carrying it diverges between the engines
    by construction. Refused at load, on every sheet, at every depth."""
    with pytest.raises(ValueError, match="gain_encore amount must be"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "gain_encore", "amount": -2}])


def test_a_non_positive_gain_encore_inside_a_mode_is_rejected():
    """The depth that matters: the mode body is where the substitution was
    reached for, because until EB-119 it was the only encore shape a mode
    could hold."""
    with pytest.raises(ValueError, match="gain_encore amount must be"):
        loader._validate_effect_vocabulary(
            "probe", [modal([{"op": "gain_encore", "amount": 0}],
                            [{"op": "draw", "amount": 1}])])


def test_a_positive_gain_encore_still_loads():
    loader._validate_effect_vocabulary(
        "probe", [modal([{"op": "gain_encore", "amount": 2}],
                        [{"op": "spend_encore", "amount": 2},
                         {"op": "draw", "amount": 2}])])


# --- the connectivity walk -------------------------------------------------

def test_effect_walk_descends_mode_bodies():
    """The packet's connectivity tool walks effects via tools/effect_walk;
    a mode body is reachable printed text, so it is not a blind spot."""
    row = {"effects": [modal(
        [{"op": "place_bomb", "amount": 1}],
        [{"op": "conditional", "if": "has_spark",
          "then": [{"op": "gain_spark", "amount": 1}]}])]}
    ops = [fx.get("op") for fx in effect_walk.iter_effects(row)]
    assert ops == ["choose_one", "place_bomb", "conditional", "gain_spark"]
    assert [fx.get("op") for fx in effect_walk.iter_effects_top(row)] \
        == ["choose_one"]
    assert [fx.get("op") for fx in effect_walk.branch_effects(row)] \
        == ["place_bomb", "conditional", "gain_spark"]


def test_the_engine_printed_power_walk_sees_mode_bodies():
    c = card(effects=[modal([{"op": "damage", "amount": 6, "target": "enemy"}],
                            [{"op": "block", "amount": 4}])])
    assert effects._printed_power(c) == 10


def test_the_drafter_classification_walk_sees_mode_bodies():
    c = card(effects=[modal([{"op": "damage", "amount": 6, "target": "enemy"}],
                            [{"op": "draw", "amount": 2}])])
    assert draft._has_tempo(c)


# --- pricing ---------------------------------------------------------------

def test_a_modal_prices_as_the_max_of_its_modes():
    """PROPOSED aggregate. The player picks with the board in front of them,
    so there is no reachability share to blend -- and max is the conservative
    end of the defensible range (it declines to credit the optionality)."""
    big = [{"op": "damage", "amount": 9, "target": "enemy"}]
    small = [{"op": "block", "amount": 4}]
    both = draft._static_power(card(cost=1, effects=[modal(small, big)]))
    assert both == draft._static_power(card(cost=1, effects=big))
    assert both > draft._static_power(card(cost=1, effects=small))


def test_the_modal_op_carries_a_price_rationale():
    assert draft.STATIC_OP_PRICING["choose_one"]
    assert "choose_one" in draft._PRICED_INLINE


# --- the staging pin -------------------------------------------------------

def test_no_shipped_card_is_modal_yet():
    """EB-118 Phase 1 builds the SURFACE only. While this holds, no committed
    number can have moved: the op is unreachable from every sheet."""
    modal_cards = [c.id for c in loader._card_index().values()
                   if any(fx.get("op") == "choose_one"
                          for fx in effects._walk_effects(c.effects))]
    assert modal_cards == []
