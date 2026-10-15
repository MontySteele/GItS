"""SHRINE-R2 SEAT FIXES (lane 4, 2026-10-14; main-session decisions,
`docs/notes/prototype-surface-provenance.md`).

  1. A Wildfire Tenko's live clause reads per enemy, "18 to each enemy",
     never "18 to ALL" (a seat read that as one volley split).
  2. An Edit (the chooser and Reborn as Guuji Yae) never reaches a card
     with a Published Annotation; with no other target it does nothing,
     as a dead Edit does.

The sim half. The C# half is
`klee-mod/KleeTests/Prototype/YaeShrineR2SeatFixTests.cs`.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        Y.SCALING = "level"
        loader.reset_arm_caches()


def _state():
    enemies = [Enemy(hp=100, max_hp=100, name="e0",
                     intents=[{"kind": "block", "amount": 0}])]
    p = Y.build_player()
    p.draw_pile = []
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _card(name):
    return loader.get_card("proto_ym_" + name)


def _play(st, card):
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _published(card, annotation=Y.RED_INK):
    Y.annotate(None, card, annotation, "published")
    card.ym_published = True
    return card


# ---- 1. the Wildfire clause ------------------------------------------------

def test_wildfire_reads_per_enemy_and_plain_tenko_is_unchanged():
    assert Y.tenko_words(Y.WILDFIRE, 18) == ": 18 to each enemy"
    assert "ALL" not in Y.tenko_words(Y.WILDFIRE, 18)
    assert Y.tenko_words(Y.THUNDER, 12) == " (12 damage)"


# ---- 2. an Edit never reaches a Published card -----------------------------

def test_the_edit_chooser_skips_a_published_card_for_a_plain_one():
    st = _state()
    pub = _published(loader.get_card("strike"))
    plain = loader.get_card("strike")
    st.player.hand += [pub, plain]
    _play(st, _card("footnote"))
    assert pub.ym_annotation == Y.RED_INK
    assert plain.ym_annotation == Y.FOOTNOTE


def test_an_edit_with_only_a_published_card_in_hand_does_nothing():
    st = _state()
    pub = _published(loader.get_card("strike"))
    st.player.hand.append(pub)
    _play(st, _card("footnote"))
    assert pub.ym_annotation == Y.RED_INK
    assert Y.ledger(st.player).edits == 0


def test_a_pilot_choice_of_a_published_card_edits_nothing():
    st = _state()
    pub = _published(loader.get_card("strike"))
    st.player.hand.append(pub)
    Y.ledger(st.player).edit_choice = lambda state, editor, ann: pub
    _play(st, _card("footnote"))
    assert pub.ym_annotation == Y.RED_INK
    assert Y.ledger(st.player).edits == 0


def test_reborn_skips_a_published_card():
    st = _state()
    Y.ledger(st.player).reborn_choice = Y.FOOTNOTE
    pub = _published(loader.get_card("strike"))
    plain = loader.get_card("defend")
    st.player.hand += [pub, plain]
    _play(st, _card("reborn_as_guuji_yae"))
    assert pub.ym_annotation == Y.RED_INK
    assert plain.ym_annotation == Y.FOOTNOTE
    assert Y.ledger(st.player).edits == 1
