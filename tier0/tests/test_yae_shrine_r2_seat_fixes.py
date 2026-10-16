"""SHRINE-R2 SEAT FIXES (lane 4, 2026-10-14), AS REVIEW R3 LEFT THEM.

  1. The Wildfire clause's fix ("18 to each enemy", never "to ALL") lives on
     as the Foxfire Sakura's words in the plain Tenko clause; the typed
     Tenko itself is gone (review r3, ruled 2026-10-14).
  2. #1308's "an Edit never reaches a Published card" is REPLACED (review
     r3, pick 2 (a)): an Edit on a Published card fills its one temporary
     slot, which a later Edit replaces and a Publish moves onto the stack.

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
    Y.publish_to(card, [annotation])
    return card


# ---- 1. the per-enemy words --------------------------------------------------

def test_a_foxfire_sakura_reads_per_enemy_in_the_clause():
    assert Y.tenko_words({Y.FOXFIRE: 18}) == " (18 to each enemy)"
    assert "ALL" not in Y.tenko_words({Y.THUNDER: 12, Y.FOXFIRE: 18})
    assert Y.tenko_words({Y.THUNDER: 12}) == " (12 damage)"


# ---- 2. an Edit on a Published card fills its temporary slot -----------------

def test_an_edit_reaches_a_published_card_and_keeps_its_stack():
    st = _state()
    pub = _published(loader.get_card("strike"))
    st.player.hand.append(pub)
    _play(st, _card("footnote"))
    assert Y.stack(pub) == [Y.RED_INK] and Y.temp(pub) == Y.FOOTNOTE
    assert Y.ledger(st.player).edits == 1
    # Both layers act: Red Ink's +3 and Footnote's draw.
    st.player.draw_pile = [loader.get_card("defend")]
    hp = st.enemies[0].hp
    _play(st, pub)
    assert hp - st.enemies[0].hp == 6 + 3
    assert any(c.id == "defend" for c in st.player.hand)


def test_a_later_edit_replaces_the_temporary_slot_never_the_stack():
    st = _state()
    pub = _published(loader.get_card("strike"))
    st.player.hand.append(pub)
    _play(st, _card("footnote"))
    _play(st, _card("cliffhanger"))
    assert Y.stack(pub) == [Y.RED_INK] and Y.temp(pub) == Y.DEADLINE


def test_reborn_reaches_a_published_card():
    st = _state()
    Y.ledger(st.player).reborn_choice = Y.FOOTNOTE
    pub = _published(loader.get_card("strike"))
    plain = loader.get_card("defend")
    st.player.hand += [pub, plain]
    _play(st, _card("reborn_as_guuji_yae"))
    assert Y.temp(pub) == Y.FOOTNOTE and Y.stack(pub) == [Y.RED_INK]
    assert Y.temp(plain) == Y.FOOTNOTE
    assert Y.ledger(st.player).edits == 2
