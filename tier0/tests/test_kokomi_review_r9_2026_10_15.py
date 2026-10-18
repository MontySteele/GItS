"""The Kokomi review, round 9 (2026-10-15): items 1 to 10.

`review/active/kokomi-review-r9-2026-10-15.md`, Claude's (Kokomi is at
Prototype). Tidecleanse draws (1), both Orders cost 0 (2, 3), and the display
and seat-page fixes (4 to 10). The C# twin is
`klee-mod/KleeTests/Prototype/KokomiReviewR9Tests.cs`; items 4, 5 and 9 are
mod-side and pinned there.
"""
from __future__ import annotations

from pathlib import Path

from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan, statuses
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, kokomi_state)
from tier0.tests.test_kokomi_status_batch import (_filler, _play_now,
                                                  _quiet_state)
from understudy import blindplay_render

REPO = Path(__file__).resolve().parents[2]
VARKA_NO_AURA = '"' + chr(92) + 'n(no aura: no Swirl)"'


def _src(rel):
    return (REPO / rel).read_text(encoding="utf-8")


# ---- item 1: Tidecleanse ---------------------------------------------------

def test_tidecleanse_draws_one_card_for_each_status_it_exhausts():
    st = _quiet_state()
    st.player.hand = [statuses.make_status("dazed"),
                      statuses.make_status("wound"),
                      statuses.make_status("slimed")] + _filler(2)
    st.player.draw_pile = _filler(6)
    _play_now(st, loader.get_card("proto_kk_tidecleanse"))
    # 3 statuses + 2 filler, 2 exhausted, 2 drawn: hand is 3 + 2.
    assert len(st.player.hand) == 5
    assert len(st.player.draw_pile) == 4


def test_tidecleanse_with_no_status_draws_nothing():
    st = _quiet_state()
    st.player.hand = _filler(3)
    st.player.draw_pile = _filler(6)
    _play_now(st, loader.get_card("proto_kk_tidecleanse"))
    assert len(st.player.hand) == 3 and len(st.player.draw_pile) == 6


def test_tidecleanse_text_says_draw_for_each():
    row = loader.get_card("proto_kk_tidecleanse")
    assert "Draw 1 card for each." in _src("docs/prototype-surface.yaml")
    assert row.cost == 0 and row.rarity == "common"


# ---- items 2 and 3: the Orders ---------------------------------------------

def test_orders_from_the_shrine_pick_costs_zero_this_turn():
    st = kokomi_state()
    assert kokomi_plan.choose_common_companion(st) == 1
    added = st.player.hand[-1]
    assert added.ethereal and added.free_this_turn


def test_sangonomiyas_orders_costs_two_and_the_card_costs_zero():
    row = loader.get_card("proto_kk_sangonomiyas_orders")
    assert row.cost == 2
    assert upgrades.apply_upgrade(row).cost == 2      # the upgrade is Innate
    st = kokomi_state()
    st.player.powers[kokomi_plan.SANGONOMIYAS_ORDERS] = 1
    before = len(st.player.hand)
    kokomi_plan.turn_start_generators(st)
    made = st.player.hand[before:]
    assert len(made) == 1 and made[0].ethereal and made[0].free_this_turn


def test_watatsumi_muster_cards_keep_their_costs():
    st = kokomi_state()
    before = len(st.player.hand)
    kokomi_plan.add_companions(st, 2)
    assert not any(c.free_this_turn for c in st.player.hand[before:])


# ---- item 4: Shell of Sanctuary (cut by the Kokomi card paper v2) ---------

def test_draft_the_orders_is_five_eight_block_and_a_discount():
    """Shell of Sanctuary's slot since the Kokomi card paper v2 (2026-10-18):
    5 [8] Block, no Retain, and the plan discount."""
    row = loader.get_card("proto_kk_draft_the_orders")
    assert not row.retain and row.cost == 1 and row.plan == []
    assert row.effects[0] == {"op": "block", "amount": 5}
    up = upgrades.apply_upgrade(row)
    assert up.effects[0] == {"op": "block", "amount": 8}
    st = kokomi_state()
    st.player.block = 0
    from tier0.engine import effects
    effects.resolve_card(st, loader.get_card("proto_kk_draft_the_orders"))
    assert st.player.block == 5
    assert st.player.powers[kokomi_plan.DRAFT_THE_ORDERS] == 1


# ---- item 7: one wording for "no aura" --------------------------------------

def test_varka_says_no_aura_no_swirl_like_sucrose():
    varka = _src("klee-mod/KleeCode/Powers/Prototype/VarkaOath.cs")
    assert VARKA_NO_AURA in varka
    sucrose = _src("klee-mod/KleeCode/Cards/SwirlAuraFace.cs")
    assert "(No aura to Swirl)" not in varka
    assert '" (no aura: no Swirl)"' in sucrose


# ---- item 6: a summon's reactions on the seat page ---------------------------

def test_a_summon_row_names_the_reaction_its_volley_set_off():
    said = {"unfinished": False, "card": "Sanctifying Ring",
            "line": "Sanctifying Ring, 6", "number": 6, "kind": "damage",
            "asked": None, "moved": [], "board_read": False, "riders": [],
            "reactions": ["Electro-Charged", "Electro-Charged"]}
    rows = blindplay_render._carry_out_rows([said], [], None,
                                            name_reactions=True)
    assert "It set off Electro-Charged." in rows[0]
    assert "set off" not in blindplay_render._carry_out_rows(
        [said], [], None)[0]
    assert "set off" not in blindplay_render._carry_out_rows(
        [dict(said, reactions=[])], [], None, name_reactions=True)[0]


# ---- item 8: the card-limit page --------------------------------------------

SMOGGY = {"name": "Smoggy", "stacks": 1,
          "text": "You cannot play more than 1 Skill each turn."}


def test_a_card_limit_says_writing_a_plan_counts():
    note = blindplay_render.PLAYED_CAP_PLAN_NOTE
    assert blindplay_render._played_cap_lines(SMOGGY, None, plans=True) == [
        note]
    assert blindplay_render._played_cap_lines(SMOGGY, None) == []
    counted = blindplay_render._played_cap_lines(
        SMOGGY, [{"card": "Vanguard"}], plans=True)
    assert counted[0].startswith("    - Counted this turn:")
    assert counted[-1] == note
    assert "Writing a Plan counts as playing that card" in note
    # Pick 1 (a), 2026-10-15; [USER]: "let's get rid of Companions as Plans
    # unless we make a card that specifically has a Plan line." Item 9's
    # Companion sentence went with the rule, on the page and on the hover.
    assert "Companion" not in note
    tip = _src("klee-mod/KleeCode/Cards/Prototype/ArmKeywordTips.cs")
    assert "again when it lands" not in tip


# ---- item 10: the Energy line ------------------------------------------------

LANTERN = {"name": "Lantern",
           "text": "At the start of each combat, gain 1 Energy."}
ANTLER = {"name": "Seal of Gold",
          "text": "At the start of your turn, spend 5 Gold to gain 1 Energy."}


def test_a_combat_opening_relic_is_named_on_round_one_only():
    you = {"energy": 4, "max_energy": 3, "relics": [LANTERN]}
    assert blindplay_render._energy_line(you, 1) == (
        "Energy 4 (3 a turn, +1 Lantern)")
    assert blindplay_render._energy_line(you, 3) == (
        "Energy 4 (3 a turn, +1 from other effects)")
    assert blindplay_render._energy_line(you) == (
        "Energy 4 (3 a turn, +1 Lantern)")


# ---- item 9: the last carry-out box ------------------------------------------

def test_a_combat_opening_clears_the_last_carry_out_receipts():
    plan = _src("klee-mod/KleeCode/Powers/Prototype/KokomiPlan.cs")
    app = _src("klee-mod/KleeCode/Powers/ElementalApplication.cs")
    assert "public static void ResetFight()" in plan
    assert "KokomiPlan.ResetFight();" in app
