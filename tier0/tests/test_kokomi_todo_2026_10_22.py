"""Kokomi to-do pass (2026-10-22; [USER]: "Do you want to go ahead and take
those to-do items now?").

1. Flank's Plan hits each enemy that does NOT intend to attack, since Coral
   Crash (Common) already prints the attacker version.
2. Steady Tide's Plan puts up to 2 [3] cards from the Discard Pile into the
   Hand, since Tidal Screen (Common) already prints Block + a planned draw.
3. `lint_text_conventions.render` keeps a selector's else-branch on the
   measured face, and the upgraded face is held to the ceiling plus one add
   clause.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tier0.engine import kokomi_plan  # noqa: E402
from tier0.engine.state import Card  # noqa: E402
from tier0.tests.conftest import make_enemy  # noqa: E402
from tier0.tests.test_kokomi_plan import (  # noqa: E402,F401
    ATTACKER, BLOCKER, _row, kokomi_state, overhaul, plan_card)
from tools import lint_text_conventions as ltc  # noqa: E402


# ---- 1. Flank ---------------------------------------------------------------

def test_flank_plans_a_hit_on_each_enemy_not_intending_to_attack(overhaul):
    row = _row("proto_kk_flank")
    assert row.plan == [{"op": "damage", "amount": 11,
                         "target": "enemies_not_intending_attack"}]


def test_the_negated_aim_skips_attackers_read_at_carry_out(overhaul):
    swinger = make_enemy(hp=40, intents=ATTACKER)
    guard = make_enemy(hp=40, intents=BLOCKER)
    st = kokomi_state(enemies=[swinger, guard])
    card = plan_card([{"op": "damage", "amount": 11,
                       "target": "enemies_not_intending_attack"}])
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)
    assert swinger.hp == 40
    assert guard.hp == 40 - 11


def test_the_negated_aim_reads_the_board_when_it_lands(overhaul):
    swinger = make_enemy(hp=40, intents=ATTACKER)
    guard = make_enemy(hp=40, intents=BLOCKER)
    st = kokomi_state(enemies=[swinger, guard])
    card = plan_card([{"op": "damage", "amount": 11,
                       "target": "enemies_not_intending_attack"}])
    kokomi_plan.schedule(st, card)
    swinger.intents = BLOCKER
    guard.intents = ATTACKER
    kokomi_plan.resolve_all(st)
    assert swinger.hp == 40 - 11
    assert guard.hp == 40


# ---- 2. Steady Tide ----------------------------------------------------------

def test_steady_tide_plans_a_fetch_from_the_discard_pile(overhaul):
    from tier0.content import upgrades

    row = _row("proto_kk_steady_tide")
    assert row.effects == [{"op": "block", "amount": 9}]
    assert row.plan == [{"op": "discard_pile_to_hand", "amount": 2}]
    up = upgrades.apply_upgrade(_row("proto_kk_steady_tide"))
    assert up.effects[0]["amount"] == 12
    assert up.plan == [{"op": "discard_pile_to_hand", "amount": 3}]


def _card(cid):
    return Card(id=cid, name=cid, cost=1, type="skill", effects=[])


def test_the_fetch_takes_up_to_n_from_the_discard_pile(overhaul):
    st = kokomi_state()
    st.player.hand = []
    st.player.discard_pile = [_card("proto_kk_a"), _card("proto_kk_b"),
                              _card("proto_kk_c")]
    card = plan_card([{"op": "discard_pile_to_hand", "amount": 2}])
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)
    assert len(st.player.hand) == 2
    assert len(st.player.discard_pile) == 1


def test_the_fetch_on_an_empty_discard_pile_does_nothing(overhaul):
    st = kokomi_state()
    st.player.hand = []
    st.player.discard_pile = []
    assert kokomi_plan.discard_pile_to_hand(st, 2) == []
    assert st.player.hand == []


def test_the_fetch_takes_what_a_short_pile_has(overhaul):
    st = kokomi_state()
    st.player.hand = []
    st.player.discard_pile = [_card("proto_kk_a")]
    assert len(kokomi_plan.discard_pile_to_hand(st, 3)) == 1
    assert st.player.discard_pile == []


# ---- 3. The lint measures both faces ------------------------------------------

def test_a_replacement_selector_keeps_its_base_word_on_the_measured_face():
    raw = "Add {IfUpgraded:show:an upgraded|a} [gold]Ward[/gold] to your Hand."
    assert ltc.render(raw) == "Add a Ward to your Hand."
    assert ltc.render(raw, upgraded=True) == "Add an upgraded Ward to your Hand."


def test_an_add_clause_is_absent_from_the_measured_face():
    raw = "Deal 6 damage.{IfUpgraded:show: Draw 1 card.|}"
    assert ltc.render(raw) == "Deal 6 damage."
    assert ltc.render(raw, upgraded=True) == "Deal 6 damage. Draw 1 card."


def test_a_selector_holding_a_hole_is_resolved_with_braces_counted():
    raw = "Gain {IfUpgraded:show:{Block:diff()} more|{Block:diff()}} Block."
    assert ltc.render(raw) == "Gain 6 Block."
    assert ltc.render(raw, upgraded=True) == "Gain 6 more Block."


def test_an_upgraded_face_over_the_ceiling_plus_one_clause_is_flagged():
    base = "Gain 6 Block. " + "x" * 100 + "."
    assert len(ltc.render(base)) <= ltc.CEILING["card"]
    long_up = base + "{IfUpgraded:show: " + "y" * 40 + ".|}"
    found = ltc.findings_for([ltc.Row("card", "fx_up", long_up, "fixture")],
                             {}, gate=False)
    assert any("upgraded face" in f for f in found)
    # Within the base game's own measure: base face plus one add clause.
    short_up = base + "{IfUpgraded:show: Draw 1.|}"
    found = ltc.findings_for([ltc.Row("card", "fx_ok", short_up, "fixture")],
                             {}, gate=False)
    assert not any("upgraded face" in f for f in found)


def test_the_replacement_selector_counts_on_the_base_face():
    """Before this pass both branches were dropped, so a base word in a
    replacement selector was never measured."""
    base = "z" * 118 + " {IfUpgraded:show:an upgraded|abcde}."
    found = ltc.findings_for([ltc.Row("card", "fx_sel", base, "fixture")],
                             {}, gate=False)
    assert any("> 120" in f for f in found)
