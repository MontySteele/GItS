"""Seat 2026-10-19, Yae lane 2: Sakura Seal+ on a Souped Strike took it from
Deal 9 to Deal 6, because the Edit cleared the card's one enchantment slot. A
card wearing a named enchantment is never Edited, in the sim as in the mod
(`klee-mod/KleeTests/Prototype/YaeEditKeepsEnchantmentTests.cs`).

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

from __future__ import annotations

from tier0.content import enchantments, loader
from tier0.engine import yae_shrine as Y
from tier0.tests.test_yae_red_ink_sakura import _card, _play, _state, yae  # noqa: F401


def _sharp_strike():
    return loader.get_card(enchantments.decorate("strike", "sharp", 3))


def test_an_enchanted_card_is_out_of_every_edits_reach():
    st = _state()
    sharp, plain = _sharp_strike(), loader.get_card("strike")
    st.player.hand += [sharp, plain]
    assert Y.wears_other_enchantment(sharp)
    assert not Y.wears_other_enchantment(plain)
    assert Y._edit_reaches(st, None, Y.RED_INK) == [plain]


def test_an_edit_attempt_keeps_the_enchantment():
    sharp = _sharp_strike()
    before = sharp.enchant_damage
    assert before == 3
    Y.annotate(None, sharp, Y.RED_INK)
    Y.publish_to(sharp, [Y.RED_INK])
    assert not Y.is_annotated(sharp)
    assert sharp.enchant_damage == before


def test_reborn_skips_the_enchanted_card():
    st = _state()
    Y.ledger(st.player).reborn_choice = Y.RED_INK
    sharp, plain = _sharp_strike(), loader.get_card("strike")
    st.player.hand += [sharp, plain]
    _play(st, _card("reborn_as_guuji_yae"))
    assert Y.temp(plain) == Y.RED_INK
    assert not Y.is_annotated(sharp)
    assert sharp.enchant_damage == 3


def test_the_publish_offer_skips_the_enchanted_card():
    cards = {0: _sharp_strike(), 1: loader.get_card("strike")}
    drafts = {0: Y.RED_INK, 1: Y.RED_INK}
    assert Y.publish_choices(drafts, {}, cards) == [1]
