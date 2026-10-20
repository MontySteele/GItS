"""THE KOKOMI UPGRADE PASS (2026-10-19), the sim side.

The ruling is review/active/kokomi-next-2026-10-19.md, "The weak-card and
upgrade pass" ([USER]: "This table looks good. Ship it"; "can we make sure
that if you upgrade a Plan card, both the Plan and non-Plan sides get
upgrades where possible?"). The C# twins are pinned in
`klee-mod/KleeTests/Prototype/KokomiUpgradePassTests.cs`.
NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import pytest

from tier0.content import loader, upgrades
from tier0.engine import kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, write)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _row(cid):
    return loader.get_card(cid)


# --- the numbers, plain and upgraded ------------------------------------------

@pytest.mark.parametrize("cid,now,plan,up_now,up_plan", [
    ("proto_kk_war_council",
     [{"op": "apply_power", "power": "weak", "amount": 2,
       "target": "all_enemies"}],
     [{"op": "energy", "amount": 2}, {"op": "draw", "amount": 0}],
     [{"op": "apply_power", "power": "weak", "amount": 3,
       "target": "all_enemies"}],
     [{"op": "energy", "amount": 2}, {"op": "draw", "amount": 1}]),
    ("proto_kk_sea_glass_harvest", [{"op": "block", "amount": 8}],
     [{"op": "transform_statuses_you_have"}],
     [{"op": "block", "amount": 11}],
     [{"op": "transform_statuses_you_have", "upgraded": True}]),
    ("proto_kk_steady_tide", [{"op": "block", "amount": 9}],
     [{"op": "draw", "amount": 3}],
     [{"op": "block", "amount": 12}], [{"op": "draw", "amount": 4}]),
])
def test_rows_and_upgrades(cid, now, plan, up_now, up_plan):
    row, up = _row(cid), _up(cid)
    assert (row.effects, row.plan) == (now, plan)
    assert (up.effects, up.plan) == (up_now, up_plan)


@pytest.mark.parametrize("cid,base,upgraded", [
    ("proto_kk_ambush", 12, 15),
    ("proto_kk_opening_gambit", 1, 2),
    ("proto_kk_tidal_screen", 2, 3),
    ("proto_kk_kelp_wall", 0, 4),
    ("proto_kk_kurages_wake", 3, 4),
    ("proto_kk_spearhead", 2, 3),
    ("proto_kk_turnabout", 0, 5),
    ("proto_mi_gorou_juuga", 3, 4),
])
def test_the_plan_line_upgrades(cid, base, upgraded):
    """(Joint Orders' and Coordinated Strike's co-op upgrades are pinned on
    the C# side: the sim's upgrade index carries no multiplayer row.)"""
    assert _row(cid).plan[0]["amount"] == base
    assert _up(cid).plan[0]["amount"] == upgraded


@pytest.mark.parametrize("cid", ["proto_kk_pincer", "proto_kk_second_wave",
                                 "proto_kk_read_the_field"])
def test_pincer_second_wave_and_read_the_field_plans_draw_1_upgraded(cid):
    assert _row(cid).plan[-1] == {"op": "draw", "amount": 0}
    assert _up(cid).plan[-1] == {"op": "draw", "amount": 1}


def test_turnabout_keeps_its_cost_and_juuga_both_sides_reach_4():
    assert _up("proto_kk_turnabout").cost == 2
    juuga = _up("proto_mi_gorou_juuga")
    assert juuga.effects[0]["amount"] == 4 and juuga.plan[0]["amount"] == 4


def test_ambush_now_line_upgrades_too():
    assert _up("proto_kk_ambush").effects[0]["amount"] == 3


# --- the behaviour ------------------------------------------------------------

def test_a_zero_draw_clause_draws_nothing_and_the_upgrade_draws_one():
    st = kokomi_state()
    st.player.draw_pile = [card("proto_kk_coral_bulwark") for _ in range(4)]
    st.player.hand = []
    write(st, card("proto_kk_war_council"))
    st.player.hand = []
    carry_out(st)
    assert st.player.hand == []
    st.player.hand = []
    write(st, _up("proto_kk_war_council"))
    st.player.hand = []
    carry_out(st)
    assert len(st.player.hand) == 1


@pytest.mark.parametrize("cid,ledger,bonus", [
    ("proto_kk_kelp_wall", "kk_damage_blocked_total", 4),
    ("proto_kk_turnabout", "kk_damage_taken_total", 5),
])
def test_the_counter_plans_add_their_upgrade_bonus(cid, ledger, bonus):
    for c, extra in ((_row(cid), 0), (_up(cid), bonus)):
        enemy = make_enemy(hp=300, intents=[{"kind": "block", "amount": 5}])
        st = kokomi_state()
        st.enemies = [enemy]
        kokomi_plan.schedule(st, c)
        setattr(st, ledger, getattr(st, ledger) + 7)
        kokomi_plan.resolve_all(st)
        assert 300 - enemy.hp == 7 + extra


def test_upgraded_sangonomiyas_orders_adds_an_upgraded_companion():
    up = _up("proto_kk_sangonomiyas_orders")
    assert up.effects[0]["power"] == kokomi_plan.SANGONOMIYAS_ORDERS_PLUS
    assert not up.innate
    st = kokomi_state()
    st.player.powers[kokomi_plan.SANGONOMIYAS_ORDERS_PLUS] = 1
    st.player.hand = []
    kokomi_plan.turn_start_generators(st)
    made = [c for c in st.player.hand if c.is_companion]
    assert len(made) == 1 and made[0].id.endswith("+")
    assert made[0].free_this_turn


def test_brine_sting_counts_for_the_shape_of_water():
    st = kokomi_state()
    kokomi_plan.note_sting_played(st, card("proto_kk_brine_sting"))
    assert st.kk_stings_played_this_turn == 1
