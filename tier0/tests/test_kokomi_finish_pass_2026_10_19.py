"""THE KOKOMI FINISH PASS (2026-10-19), the sim side.

The ruling is review/active/kokomi-cards-2026-10-18.md sec.7, "The changes",
ruled all (a) ([USER], 2026-10-19: "I like this all around"):

1. Battle Formation (Rare Power, 2): "At the start of your turn, if 2 or more
   of your Plans were carried out, gain [E] [and draw 1 card]. Stings and
   Wards don't count." Read once, after the morning's Plans. Every copy adds
   1 Energy; each upgraded copy also 1 card.
2. Grand Design (Rare Skill, 1): "Plan up to 3 [4] cards from your Hand. They
   cost 0. Draw 1 card for each. Exhaust."

The C# twins are pinned in
`klee-mod/KleeTests/Prototype/KokomiFinishPassTests.cs`.
NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import inspect

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan
from tier0.engine.state import Card
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, kokomi_state)


def _draw_plan(i):
    return Card(id=f"proto_kk_probe{i}", name=f"Probe {i}", cost=0,
                type="skill", effects=[],
                plan=[{"op": "draw", "amount": 1}])


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _filler(n):
    return [card("proto_kk_coral_bulwark") for _ in range(n)]


def _morning(st):
    """The turn start's Kokomi steps, in `combat._player_turn`'s order."""
    kokomi_plan.resolve_all(st)
    kokomi_plan.battle_formation(st)


# --- 1. Battle Formation ------------------------------------------------------

def test_battle_formation_row_and_upgrade():
    row = loader.get_card("proto_kk_battle_formation")
    assert (row.cost, row.type, row.rarity) == (2, "power", "rare")
    assert row.effects == [{"op": "apply_power", "power": "kk_battle_formation",
                            "amount": 1, "target": "self"}]
    up = _up("proto_kk_battle_formation")
    assert up.cost == 2 and not up.innate
    assert up.effects[0]["power"] == kokomi_plan.BATTLE_FORMATION_PLUS


def test_two_plans_at_dawn_pay_one_energy_and_no_card():
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    for i in range(2):
        kokomi_plan.schedule(st, _draw_plan(i))
    st.player.draw_pile = _filler(10)
    st.player.energy = 0
    _morning(st)
    paid = [e for e in st.log if e["event"] == "plan_battle_formation"]
    assert len(paid) == 1
    assert (paid[0]["energy"], paid[0]["cards"]) == (1, 0)
    assert st.player.energy == 1


def test_one_plan_at_dawn_pays_nothing():
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    kokomi_plan.schedule(st, _draw_plan(0))
    st.player.draw_pile = _filler(4)
    st.player.energy = 0
    _morning(st)
    assert not [e for e in st.log if e["event"] == "plan_battle_formation"]
    assert st.player.energy == 0


def test_stings_and_wards_dont_count():
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    kokomi_plan.schedule(st, card(kokomi_plan.STING_ID))
    kokomi_plan.schedule(st, card(kokomi_plan.WARD_ID))
    kokomi_plan.schedule(st, _draw_plan(0))
    st.player.draw_pile = _filler(4)
    st.player.energy = 0
    _morning(st)
    assert st.kk_plans_carried_out_this_turn == 3
    assert st.kk_chain_plans_this_turn == 1
    assert st.player.energy == 0


def test_copies_stack_energy_and_upgraded_copies_add_a_card_each():
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    st.player.powers[kokomi_plan.BATTLE_FORMATION_PLUS] = 2
    for i in range(2):
        kokomi_plan.schedule(st, _draw_plan(i))
    st.player.draw_pile = _filler(10)
    st.player.hand = []
    st.player.energy = 0
    _morning(st)
    paid = [e for e in st.log if e["event"] == "plan_battle_formation"]
    assert (paid[0]["energy"], paid[0]["cards"]) == (3, 2)
    assert st.player.energy == 3
    # 2 cards from the Plans' own draws, 2 from Battle Formation.
    assert len(st.player.hand) == 4
    assert C.KOKOMI_BATTLE_FORMATION_DRAW == 1


def test_a_carry_out_later_in_the_turn_does_not_pay():
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    for i in range(3):
        kokomi_plan.schedule(st, _draw_plan(i))
    st.player.draw_pile = _filler(10)
    st.player.energy = 0
    kokomi_plan.resolve_all(st)          # e.g. Change of Plans, mid-turn
    assert not [e for e in st.log if e["event"] == "plan_battle_formation"]
    assert st.player.energy == 0


def test_the_turn_start_reads_it_right_after_the_plans():
    src = inspect.getsource(combat._player_turn)
    resolve = src.index("kokomi_plan.resolve_all(state)")
    formation = src.index("kokomi_plan.battle_formation(state)")
    dawn = src.index("kokomi_plan.dawn_tide(state)")
    assert resolve < formation < dawn


# --- 2. Grand Design ----------------------------------------------------------

def test_grand_design_row_and_upgrade():
    row = loader.get_card("proto_kk_grand_design")
    assert (row.cost, row.type, row.rarity) == (1, "skill", "rare")
    assert row.exhaust
    assert row.effects == [{"op": "kokomi", "kind": "grand_design",
                            "amount": 3}]
    up = _up("proto_kk_grand_design")
    assert up.effects[0]["amount"] == 4
    assert not up.retain and up.exhaust and up.cost == 1


def test_grand_design_draws_one_for_each_card_planned():
    st = kokomi_state()
    gd = card("proto_kk_grand_design")
    oath = card("proto_kk_kurages_oath")
    st.player.hand = [gd, oath, card("strike")]
    st.player.draw_pile = _filler(10)
    combat.play_card(st, gd)
    assert len(st.kk_plan_queue) == 2
    # Both picks left the hand; two cards came back.
    assert len(st.player.hand) == 2
    assert len(st.player.draw_pile) == 8
    assert gd in st.player.exhaust_pile


def test_upgraded_grand_design_plans_four():
    st = kokomi_state()
    gd = upgrades.apply_upgrade(card("proto_kk_grand_design"))
    st.player.hand = [gd] + [card("strike") for _ in range(5)]
    st.player.draw_pile = _filler(10)
    combat.play_card(st, gd)
    assert len(st.kk_plan_queue) == 4
    # One Strike stayed; four drawn.
    assert len(st.player.hand) == 5
