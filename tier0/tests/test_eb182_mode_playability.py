"""EB-182: per-option playability on the choose-a-card screen (sim leg).

THE RULE. A `choose_one` mode whose body OPENS with a resource spend prints a
price -- "Spend 3 Encore: draw 3" -- and that price is the mode's cost line.
A mode the bank cannot pay is NOT OFFERED; the card stays playable while any
mode is affordable; a card whose every mode is priced out is unplayable, and
the refusal names the price and the bank that fell short.

WHERE IT LIVES. `effects.mode_price` / `offered_modes` (the predicate),
`effects._chosen_mode` (the one seam every mode selection passes through, so
the pilot, the falsifier and a replay inherit it without knowing the rule),
and `combat.card_playable` / `combat.modal_refusal` (the card-level gate and
its printable reason).

CONSUMERS. Furina's shipped `deep_breath`, whose mode 2 prices *Spend 3
Encore: draw 3* and was takeable on an empty bank; and the Klee arm this
unblocks, *Bag of Tricks*, whose expensive mode prices Sparks (R224 item 17
took option (3): build this, then re-ask the seat).

NOT this file's subject: EB-184, the separate targeting defect. Untouched.
"""

import pytest

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import Card
from tier0.pilot import policy

from .conftest import make_state


def card(**kw):
    base = dict(id="t", name="t", cost=0, type="skill")
    base.update(kw)
    return Card(**base)


def modal(*bodies, labels=None):
    names = labels or [f"mode {chr(ord('A') + i)}" for i in range(len(bodies))]
    return {"op": "choose_one",
            "modes": [{"label": n, "effects": list(b)}
                      for n, b in zip(names, bodies)]}


def deep_breath():
    return loader._card_index()["deep_breath"]


# --- the shipped consumer: deep_breath -------------------------------------

def test_a_short_bank_is_not_offered_deep_breaths_priced_mode(state):
    """(a) Encore 2 against a price of 3: mode 2 is gone, mode 1 remains.

    The card is NOT dead -- mode 1 (*Gain 1 Energy and 2 Encore*) prices
    nothing -- so the whole point of per-option playability is that the option
    disappears and the card does not.
    """
    c = deep_breath()
    fx, = c.effects
    state.player.encore = 2
    state.player.energy = 1
    assert effects.offered_modes(state, fx["modes"]) == [0]
    assert combat.modal_refusal(state, c) is None
    assert combat.card_playable(state, c)


def test_the_priced_mode_returns_when_the_bank_covers_it(state):
    """(b) Encore 3: both modes are offered again. The gate is the BANK, not
    the card -- nothing about the row changed."""
    c = deep_breath()
    fx, = c.effects
    state.player.encore = 3
    state.player.energy = 1
    assert effects.offered_modes(state, fx["modes"]) == [0, 1]
    assert combat.card_playable(state, c)


def test_the_chooser_cannot_resolve_a_mode_it_was_not_offered(state):
    """The seam, not the predicate: a chooser that would have taken mode 2 is
    handed a list that does not contain it.

    Forced by making mode 2 the obvious pick (a full hand of draw against a
    body that gains 2 Encore) and then emptying the bank underneath it.
    """
    c = deep_breath()
    state.player.encore = 0
    state.player.draw_pile = [card(id=f"d{i}") for i in range(5)]
    effects.resolve_card(state, c)
    chosen = [e for e in state.log if e["event"] == "mode_chosen"]
    assert [e["index"] for e in chosen] == [0]
    assert state.player.hp == 80          # nothing overdrew into HP
    assert not [e for e in state.log if e["event"] == "encore_overdraw"]


# --- every mode priced out -------------------------------------------------

def test_a_card_whose_every_mode_is_priced_out_is_unplayable(state):
    """(c) An empty bank against two priced modes: the card is refused, and
    the reason NAMES the price and the bank.

    Two priced modes rather than one: the loader requires at least two modes
    (`MIN_MODES`), so "every mode is priced out" is the smallest shape a
    sheet could actually carry.
    """
    c = card(id="twin_price", effects=[modal(
        [{"op": "spend_encore", "amount": 3}, {"op": "draw", "amount": 3}],
        [{"op": "spend_spark", "amount": 2}, {"op": "block", "amount": 9}],
        labels=["Spend 3 Encore: draw 3", "Spend 2 Sparks: gain 9 Block"])])
    state.player.encore = 0
    state.player.sparks = 1
    assert effects.offered_modes(state, c.effects[0]["modes"]) == []
    assert not combat.card_playable(state, c)
    reason = combat.modal_refusal(state, c)
    assert reason == (
        "twin_price: no mode is affordable -- "
        "'Spend 3 Encore: draw 3' needs 3 Encore, bank holds 0; "
        "'Spend 2 Sparks: gain 9 Block' needs 2 Sparks, bank holds 1")


def test_one_affordable_mode_keeps_the_card_playable(state):
    """The same card, one meter topped up. A card dies only when EVERY mode
    does -- the half a card-level cost line could not express."""
    c = card(id="twin_price", effects=[modal(
        [{"op": "spend_encore", "amount": 3}, {"op": "draw", "amount": 3}],
        [{"op": "spend_spark", "amount": 2}, {"op": "block", "amount": 9}])])
    state.player.encore = 0
    state.player.sparks = 2
    assert effects.offered_modes(state, c.effects[0]["modes"]) == [1]
    assert combat.card_playable(state, c)
    assert combat.modal_refusal(state, c) is None


@pytest.mark.parametrize("op,field,meter", [
    ("spend_encore", "encore", "Encore"),
    ("spend_spark", "sparks", "Sparks"),
    ("spend_charge", "charge", "Charge"),
])
def test_all_three_meters_are_read_off_the_bank_they_price(op, field, meter):
    """One rule, three meters -- Encore (shipped), Sparks (Bag of Tricks) and
    Charge (the quarantined surface). The bank read is the meter named."""
    state = make_state()
    mode = {"label": f"Spend 2 {meter}: draw 2",
            "effects": [{"op": op, "amount": 2}, {"op": "draw", "amount": 2}]}
    assert effects.mode_price(state, mode) == (field, meter, 2)
    setattr(state.player, field, 1)
    assert not effects.mode_affordable(state, mode)
    assert effects.mode_refusal(state, mode) == (
        f"'Spend 2 {meter}: draw 2' needs 2 {meter}, bank holds 1")
    setattr(state.player, field, 2)
    assert effects.mode_affordable(state, mode)
    assert effects.mode_refusal(state, mode) is None


# --- the boundary: a price, not every spend --------------------------------

def test_a_spend_below_the_head_of_a_body_is_not_a_price(state):
    """The colon is the boundary. "Spend 3 Encore: draw 3" prices the mode;
    a spend further down the body is a consequence the mode pays out of what
    it just generated, and it keeps the overdraw the engine always gave it
    (`test_eb118_modal.test_a_mode_body_spend_overdraws_into_hp`)."""
    mode = {"label": "Gain 1 Encore, then spend 4",
            "effects": [{"op": "gain_encore", "amount": 1},
                        {"op": "spend_encore", "amount": 4}]}
    state.player.encore = 0
    assert effects.mode_price(state, mode) is None
    assert effects.mode_affordable(state, mode)
    assert effects.mode_refusal(state, mode) is None


# --- the regression: an unpriced world is untouched ------------------------

UNPRICED = [
    ("block_or_hit", modal([{"op": "block", "amount": 6}],
                           [{"op": "damage", "amount": 6,
                             "target": "enemy"}])),
    ("draw_or_gain", modal([{"op": "draw", "amount": 2}],
                           [{"op": "gain_encore", "amount": 2}])),
    ("three_modes", modal([{"op": "block", "amount": 3}],
                          [{"op": "block", "amount": 5}],
                          [{"op": "gain_spark", "amount": 1}])),
]


@pytest.mark.parametrize("chooser_on", [True, False])
def test_an_unpriced_fixture_offers_every_mode_at_every_bank(
        chooser_on, monkeypatch):
    """The regression, stated as the legal-move list itself.

    No mode of these fixtures opens with a spend, so `offered_modes` is the
    identity at every bank, the playable set is unchanged, and the chooser --
    on or off -- is handed the same list it was handed before EB-182. That is
    what makes the filter a no-op everywhere except on a priced mode.
    """
    monkeypatch.setattr(policy, "MODE_CHOOSER_ENABLED", chooser_on)
    for encore, sparks, charge in [(0, 0, 0), (3, 2, 6), (99, 99, 99)]:
        state = make_state()
        state.player.encore, state.player.sparks = encore, sparks
        state.player.charge = charge
        hand = [card(id=cid, effects=[fx]) for cid, fx in UNPRICED]
        state.player.hand = hand
        assert [c.id for c in hand if combat.card_playable(state, c)] \
            == [cid for cid, _ in UNPRICED]
        for c in hand:
            fx, = c.effects
            assert effects.offered_modes(state, fx["modes"]) \
                == list(range(len(fx["modes"])))
            assert combat.modal_refusal(state, c) is None
            # The chooser's own answer, taken through the seam that now
            # filters, is the answer it gave when nothing filtered.
            assert effects._chosen_mode(state, fx["modes"], c) == (
                policy.choose_mode(state, fx["modes"], c) if chooser_on else 0)
