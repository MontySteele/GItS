"""Kokomi Balance suite 4 (2026-10-21), the defects: the sim side.

`review/records/kokomi-balance-suite-4-2026-10-21.md`, "Defects and
legibility". Defect fixes only, no number moves. The C# twins are pinned in
`klee-mod/KleeTests/Prototype/KokomiSuite4FixesTests.cs`; Crystal Collapse's
gate is in `test_kokomi_wording_pass_2026_10_14.py` section 4.
NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, kokomi_plan
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, kokomi_state, write)


def _casket(st):
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]


# --- Grand Design pays the Tamakushi Casket for each card it plans -----------

def test_grand_design_pays_the_casket_once_per_card_planned():
    """"Whenever you Plan a card ..., gain 2 Block." Grand Design plans up to
    3 cards: a Plan card (its free write) and a Basic (planned as itself)
    each pay once. Two seats of the suite saw no Casket Block off them."""
    st = kokomi_state()
    _casket(st)
    gd = card("proto_kk_grand_design")
    oath, strike = card("proto_kk_kurages_oath"), card("strike")
    st.player.hand = [gd, oath, strike]
    st.player.draw_pile = [card("proto_kk_coral_bulwark") for _ in range(4)]
    st.player.block = 0
    combat.play_card(st, gd)
    assert len(st.kk_plan_queue) == 2
    assert st.player.block == 2 * C.KOKOMI_OVERHAUL_CASKET_BLOCK


def test_a_planned_basic_counts_for_the_casket_only_when_planned():
    assert kokomi_plan.casket_counts_planned(card("strike"))
    assert kokomi_plan.casket_counts_planned(card("defend"))
    assert kokomi_plan.casket_counts_planned(card("proto_kk_kurages_oath"))
    # Played face up, a Strike is no Plan and no Companion.
    assert not kokomi_plan.casket_counts(card("strike"), planned=False)


def test_a_plan_card_dragged_on_the_jellyfish_still_pays_once():
    st = kokomi_state()
    _casket(st)
    st.player.block = 0
    write(st, card("proto_kk_kurages_oath"))
    assert st.player.block == C.KOKOMI_OVERHAUL_CASKET_BLOCK
