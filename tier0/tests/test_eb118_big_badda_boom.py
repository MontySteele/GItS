"""EB-118 Phase 2B: Big Badda Boom, the first DRAFTABLE Ethereal carrier.

`test_ethereal_base_field.py` proves the machinery on synthetic probes -- the
field, the shared predicate, the end-of-turn sweep, the remove-on-upgrade
delta. Everything there is true of a card nobody can be dealt. This file is
the other half: the ruled card, on the shipping sheet, through both engines.

Three legs, because a keyword that only half-crosses the wall is the exact
divergence the codegen whitelist exists to stop (a card that vanishes in the
sim and lingers in the game is a different card):

  1. tier0 runtime -- the shipped row burns unplayed, the upgraded row does
     not, in a real fight loop rather than a direct call to the flush.
  2. codegen -- the generator emits `CardKeyword.Ethereal` on the base and
     `RemoveKeyword(CardKeyword.Ethereal)` on the upgrade, and emits no
     number bump beside either.
  3. the SHIPPED artifact -- the committed generated file says the same. CI's
     `gen_roster_cards.py --check` proves the file matches the generator;
     this proves the generator was pointed at the right card.

The drafter leg is not here: it is a tier-0.5 price and lives in
`tier05/tests/test_ethereal_draft_valuation.py`, where the 0.6 share R193
ratified provisionally is exercised by this same card.
"""

from __future__ import annotations

from pathlib import Path

from tier0.content import loader
from tier0.engine import combat
from tier0.tests.conftest import make_enemy
from tools import gen_klee_cards as gen

CARD = "big_badda_boom"
GENERATED = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
             / "Cards" / "Generated" / "BigBaddaBoom.cs")


def _sheet_row() -> dict:
    row = next((c for c in gen._sheet_cards(gen.KLEE_PROFILE.sheet)
                if c["id"] == CARD), None)
    assert row is not None, f"{CARD} left docs/klee-cards.yaml"
    return row


def _unplayed_turn(card_id: str):
    """One fight, nothing playable, nothing to draw: the only thing that can
    move the card is the end-of-turn flush. Klee's own build_player, because
    the point is that the keyword works for the character who ships it."""
    p = loader.build_player("klee")
    p.draw_pile = []
    p.discard_pile = []
    p.hand = [loader.get_card(card_id)]
    p.energy = 0                      # the card costs 2; it cannot be played
    return combat.run_fight(
        p, [make_enemy(hp=1, intents=[{"kind": "block", "amount": 0}])],
        lambda s: None, seed=0)


# --- 1. tier0 runtime ------------------------------------------------------

def test_the_base_card_burns_in_hand():
    st = _unplayed_turn(CARD)
    assert any(c.id == CARD for c in st.player.exhaust_pile)
    assert not any(c.id == CARD for c in st.player.discard_pile)


def test_the_upgraded_card_does_not():
    """The red half, and the whole value of the upgrade: same card, same
    fight, upgraded -- it flushes to discard and comes back around."""
    st = _unplayed_turn(CARD + "+")
    assert not any(c.id.startswith(CARD) for c in st.player.exhaust_pile)
    assert any(c.id == CARD + "+" for c in st.player.discard_pile)


def test_the_damage_did_not_move_with_the_price():
    """The price was added FIRST and ALONE so the later read is one variable
    (packet §4.3). A number bump reintroduced beside the keyword would make
    R193's armed repricing trigger read a card it was not armed on."""
    base = loader.get_card(CARD)
    up = loader.get_card(CARD + "+")
    assert base.effects == up.effects == [
        {"op": "damage", "amount": 16, "target": "enemy"},
    ]
    assert base.cost == up.cost == 2


# --- 2. codegen ------------------------------------------------------------

def test_the_generator_emits_the_keyword_and_its_removal():
    cs = gen.emit(_sheet_row(), gen.KLEE_PROFILE)
    assert "CardKeyword.Ethereal" in cs
    assert "RemoveKeyword(CardKeyword.Ethereal);" in cs
    # The keyword renders through the game's auto-keyword pipeline (the A9
    # rail), so the description must NOT also say the word.
    assert "Ethereal." not in cs
    # And the upgrade is the keyword removal ALONE.
    assert "UpgradeValueBy" not in cs


def test_the_card_is_not_blocked():
    """`ethereal` is on the codegen field whitelist. Without that entry the
    first card ruled Ethereal from print blocks with "card field(s)
    ['ethereal'] not understood" -- which is the whitelist working, but it
    would mean this card ships in the sim and not in the mod."""
    assert gen.blocked_reason(_sheet_row(), gen.KLEE_PROFILE) is None


# --- 3. the shipped artifact ----------------------------------------------

def test_the_committed_generated_card_carries_it():
    cs = GENERATED.read_text(encoding="utf-8")
    assert "CardKeyword.Ethereal" in cs
    assert "RemoveKeyword(CardKeyword.Ethereal);" in cs
    assert "UpgradeValueBy" not in cs
