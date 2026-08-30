"""EB-118 sec.5.4: the generic choose-one / modal effect surface.

ONE shipped card carries a `choose_one` -- `deep_breath`, the Phase-2C
prototype (R192 picked the card, R194 ruled the pair, R205 re-bodied mode 2)
-- and the prototype section below is the pin that keeps it one. The pattern
is not copied until the pilot and the price can distinguish the modes, which
is the packet's own sequencing and not a style preference. THE PILOT NOW CAN:
the chooser is live since 2026-08-24. The PRICE still cannot, and that is the
accepted under-credit rather than an oversight.

The pilot's half of that pair lives in `test_eb118_mode_chooser` (switch on,
which is now the shipped world) and `test_eb118_switch_off` (switch forced
off); the price's half is the MAX arbitration pin below, which is SYNTHETIC
because the shipped card's mode 2 prices at a static zero and cannot exercise
it (R194's accepted under-credit).

This file is about the SURFACE, not about which mode wins: its fixtures reach
a body by index and take the `fixed_index` fixture where that matters.

The sheet syntax under test:

    {op: choose_one, modes: [
        {label: "Gain 2 Encore",        effects: [{op: gain_encore, amount: 2}]},
        {label: "Spend 2 Encore: draw", effects: [{op: spend_encore, amount: 2},
                                                  {op: draw, amount: 2}]}]}
"""

import copy

import pytest

from tier0.content import loader, upgrades
from tier0.engine import effects
from tier0.engine.state import Card
from tier0.pilot import policy
from tier05 import draft
from tools import effect_walk, role_tempo


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


@pytest.fixture
def fixed_index(monkeypatch):
    """The chooser held OFF, so mode A is the mode that resolves.

    Added at the 2C activation flip (2026-08-24) on the pattern the house used
    at 2A: a test that describes the OFF world has to name it once the shipped
    default is ON. Every test taking this fixture is about the GRAMMAR of a
    mode body -- an op inside a mode is the op it is outside one -- and reaches
    its body by index for convenience, so forcing the fixed index keeps the
    board and the claim verbatim instead of re-tuning bodies until a live
    chooser happens to agree. WHICH mode a live chooser takes is
    `test_eb118_mode_chooser`'s subject, not this file's.
    """
    monkeypatch.setattr(policy, "MODE_CHOOSER_ENABLED", False)


# --- resolution ------------------------------------------------------------

def test_the_chosen_mode_resolves_and_the_others_do_not(state):
    c = card(effects=[modal(
        [{"op": "damage", "amount": 6, "target": "enemy"}],
        [{"op": "block", "amount": 6}])])
    effects.resolve_card(state, c)
    assert state.enemies[0].hp == 44
    assert state.player.block == 0


def test_a_mode_body_is_an_ordinary_effect_list(state, fixed_index):
    """Multi-effect bodies resolve in order, and nest like anything else."""
    c = card(effects=[modal(
        [{"op": "block", "amount": 3},
         {"op": "conditional", "if": "has_spark",
          "then": [{"op": "block", "amount": 99}],
          "else": [{"op": "block", "amount": 4}]}],
        [{"op": "damage", "amount": 6, "target": "enemy"}])])
    effects.resolve_card(state, c)
    assert state.player.block == 7


def test_a_mode_body_spends_through_the_overdraw_primitive(state, fixed_index):
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


def test_a_mode_body_spend_overdraws_into_hp(state, fixed_index):
    """The half the substitution could never have modelled. A spend past the
    buffer drains TRUE HP; a negative `gain_encore` would have clamped at
    zero and charged nothing.

    EB-182 MOVED THE SPEND ONE LINE DOWN and the claim is unchanged. A spend
    at the HEAD of a mode body is that mode's PRICE, and the mode is not
    offered below it; a spend after something else is a CONSEQUENCE of the
    mode -- here paid partly out of what the same body just generated -- and
    still rides the overdraw primitive exactly as EB-119 left it. Both sides
    of that boundary are pinned in `test_eb182_mode_playability`.
    """
    state.player.encore = 1
    c = card(effects=[modal([{"op": "gain_encore", "amount": 1},
                             {"op": "spend_encore", "amount": 4}],
                            [{"op": "gain_encore", "amount": 2}])])
    effects.resolve_card(state, c)
    assert state.player.encore == 0
    assert state.player.hp == 78
    assert [e["amount"] for e in state.log
            if e["event"] == "encore_overdraw"] == [2]


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


def test_the_role_tempo_classifier_sees_mode_bodies_and_does_not_gate_them():
    """The tags this classifier derives are LANDED on the sheet, so a blind
    spot here does not stay an instrument problem -- it becomes authored
    metadata. Blind to modes it read `deep_breath` as one unknown op and
    moved its fight band.

    Mode bodies are NOT gated. A conditional branch may never fire, which is
    what `gated` means; one mode always resolves and the player picks which,
    the same distinction the drafter's MAX-not-share-blend rests on.
    """
    row = {"effects": [modal([{"op": "block", "amount": 5}],
                             [{"op": "draw", "amount": 2}])]}
    walked = list(role_tempo._walk(row["effects"]))
    assert [fx["op"] for fx, _, _ in walked] == ["block", "draw"]
    assert not any(gated for _, gated, _ in walked)


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


def test_the_max_leg_arbitrates_between_two_nonzero_priced_modes():
    """R194's owed SYNTHETIC pin, and the reason it is owed.

    The shipped modal card cannot exercise this leg. Deep Breath's mode 2 is
    `spend_encore` + `draw`, `draw` is a static ZERO and the spend is
    negative, so `MAX(modes)` returns mode 1 by construction and never
    performs a comparison. Without this fixture the arbitration would first
    run in front of a Phase-3 card carrying real stakes.

    Two NONZERO-priced modes, asserted in BOTH orders, so the result is the
    max and not a first-mode read: a max that silently returned `modes[0]`
    would pass one order and fail the other.
    """
    lo = [{"op": "block", "amount": 4}]
    hi = [{"op": "damage", "amount": 9, "target": "enemy"}]
    lo_price = draft._static_power(card(cost=1, effects=lo))
    hi_price = draft._static_power(card(cost=1, effects=hi))
    assert lo_price > 0 and hi_price > lo_price      # both modes are priced

    for order in ((lo, hi), (hi, lo)):
        priced = draft._static_power(card(cost=1, effects=[modal(*order)]))
        assert priced == hi_price
    # ... and a third mode priced between them does not disturb the max.
    mid = [{"op": "block", "amount": 6}]
    assert draft._static_power(
        card(cost=1, effects=[modal(lo, hi, mid)])) == hi_price


# --- the prototype ---------------------------------------------------------

def test_deep_breath_is_the_only_modal_card():
    """EB-118 2C converts ONE card (R192). The prototype discipline is the
    packet's own (sec.5.4): do not copy the pattern to four cards until the
    pilot and the price can distinguish the modes. This pin is what makes
    "one card" a fact rather than an intention."""
    modal_cards = sorted(c.id for c in loader._card_index().values()
                         if any(fx.get("op") == "choose_one"
                                for fx in effects._walk_effects(c.effects)))
    assert modal_cards == ["deep_breath"]


def test_deep_breaths_modes_are_the_ruled_pair():
    """R194 Option A, mode 2 RE-BODIED at R205 ([USER] 2026-08-24).

    Mode 1 is the body the card already shipped -- that is the whole reason
    the pair was chosen -- and it is UNCHANGED by the re-body. Mode 2 still
    reaches the OVERDRAW primitive rather than paraphrasing it as a negative
    gain (EB-119); what moved is only its two amounts, 2/2 -> 3/3, so that the
    chooser has a board it takes each mode on (the crossover pin lives in
    `test_eb118_mode_chooser`).
    """
    dbreath = loader._card_index()["deep_breath"]
    fx, = dbreath.effects
    assert fx["op"] == "choose_one"
    assert [m["effects"] for m in fx["modes"]] == [
        [{"op": "energy", "amount": 1}, {"op": "gain_encore", "amount": 2}],
        [{"op": "spend_encore", "amount": 3}, {"op": "draw", "amount": 3}]]
    assert [m["label"] for m in fx["modes"]] == [
        "Gain 1 Energy and 2 Encore", "Spend 3 Encore: draw 3"]


def test_the_frame_is_mode_independent():
    """Contract point 5: the choice selects a body, never a frame. Exhaust,
    cost, type and rarity are the CARD's and survive the conversion; the
    upgrade is the ruled cost line (R194 point 6) and touches no mode."""
    dbreath = loader._card_index()["deep_breath"]
    assert (dbreath.cost, dbreath.type, dbreath.rarity, dbreath.exhaust) \
        == (1, "skill", "uncommon", True)
    up = upgrades.apply_upgrade(copy.deepcopy(dbreath))
    assert (up.id, up.cost, up.exhaust) == ("deep_breath+", 0, True)
    assert up.effects == dbreath.effects


def test_the_conversion_moves_no_drafter_number():
    """The accepted under-credit, as arithmetic (R194).

    `draw` and `energy` are both static ZERO, so mode 2 prices at minus its
    own spend and the max returns mode 1 -- which IS the pre-conversion body.
    Deep Breath is therefore priced to the digit as it was before it became
    modal, and the acceptance note at the `choose_one` price row says so in
    prose. If a dial moves and this test fails, that row is what to re-read.
    """
    dbreath = loader._card_index()["deep_breath"]
    old_body = card(cost=1, effects=[{"op": "energy", "amount": 1},
                                     {"op": "gain_encore", "amount": 2}])
    assert draft._static_power(dbreath) == draft._static_power(old_body)
