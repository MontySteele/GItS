"""THE KOKOMI DEFENCE PASS (2026-10-22), the sim side.

[USER], after his Kokomi run: "I think it's fine for the Casket to pay on
0-cost cards as an intended loop, but I think 2 block per plan is making them
too strong. Let's try 1a, 3a, and reducing the Casket to 1 again", and on
Watatsumi's Grace, "Otherwise agreed"
(review/active/kokomi-next-2026-10-19.md, "Defence pass, 2026-10-22").

1. The Tamakushi Casket pays 1 Block a counted play (Stings and Wards still
   count); the Watatsumi Casket 2 (C# only, `WatatsumiCasket.WatatsumiBlock`).
2. Watatsumi's Grace: "... for each Plan waiting. Stings and Wards don't
   count."
3. Kurage Canopy: "At the start of your turn, if 2 or more of your Plans were
   carried out, add a Ward to your Hand. Stings and Wards don't count."
4. Tide Wall's Plan: "Gain 4 [6] Block, plus the biggest attack an enemy
   intends when this is carried out."

The C# twins are pinned in
`klee-mod/KleeTests/Prototype/KokomiDefencePassTests.cs`.
NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import inspect

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan
from tier0.engine.state import Card
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, kokomi_state, write)


def _plan(i):
    return Card(id=f"proto_kk_probe{i}", name=f"Probe {i}", cost=0,
                type="skill", effects=[],
                plan=[{"op": "energy", "amount": 1}])


def _morning(st):
    """The turn start's Kokomi steps, in `combat._player_turn`'s order."""
    kokomi_plan.resolve_all(st)
    kokomi_plan.battle_formation(st)
    kokomi_plan.kurage_canopy(st)


def _wards(st, upgraded=False):
    want = kokomi_plan.WARD_ID + (upgrades.SUFFIX if upgraded else "")
    return sum(1 for c in st.player.hand if c.id == want)


# --- 1. the Casket -------------------------------------------------------------

def test_the_casket_pays_1_for_a_planned_sting():
    st = kokomi_state()
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    st.player.block = 0
    write(st, card(kokomi_plan.STING_ID))
    assert C.KOKOMI_OVERHAUL_CASKET_BLOCK == 1
    assert st.player.block == 1
    paid = [e for e in st.log if e["event"] == "casket_block"]
    assert [e["amount"] for e in paid] == [1]


# --- 2. Watatsumi's Grace --------------------------------------------------------

def test_grace_ignores_waiting_stings_and_wards():
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATATSUMIS_GRACE] = 3
    write(st, card(kokomi_plan.STING_ID))
    write(st, card(kokomi_plan.WARD_ID))
    st.player.block = 0
    kokomi_plan.turn_end(st)
    assert len(st.kk_plan_queue) == 2
    assert st.player.block == 0
    write(st, card("proto_kk_coral_crash"))
    write(st, card("proto_kk_tide_wall"))
    st.player.block = 0
    kokomi_plan.turn_end(st)
    assert st.player.block == 2 * 3


def test_grace_reads_the_count_tideturn_reads():
    assert "chain_plans_held(state)" in inspect.getsource(kokomi_plan.turn_end)


# --- 3. Kurage Canopy -------------------------------------------------------------

def test_canopy_adds_one_ward_after_two_plans_once():
    st = kokomi_state()
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 1
    for i in range(4):
        kokomi_plan.schedule(st, _plan(i))
    st.player.hand = []
    _morning(st)
    assert st.kk_chain_plans_this_turn == 4
    assert _wards(st) == 1
    assert len([e for e in st.log if e["event"] == "plan_kurage_canopy"]) == 1


def test_canopy_one_plan_pays_nothing():
    st = kokomi_state()
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 1
    kokomi_plan.schedule(st, _plan(0))
    st.player.hand = []
    _morning(st)
    assert _wards(st) == 0


def test_canopy_stings_and_wards_dont_count():
    st = kokomi_state()
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 1
    kokomi_plan.schedule(st, card(kokomi_plan.STING_ID))
    kokomi_plan.schedule(st, card(kokomi_plan.WARD_ID))
    kokomi_plan.schedule(st, _plan(0))
    st.player.hand = []
    _morning(st)
    assert st.kk_plans_carried_out_this_turn == 3
    assert st.kk_chain_plans_this_turn == 1
    assert _wards(st) == 0


def test_canopy_left_the_plan_bus():
    st = kokomi_state()
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 1
    for i in range(3):
        kokomi_plan.schedule(st, _plan(i))
    st.player.hand = []
    kokomi_plan.resolve_all(st)          # e.g. Change of Plans, mid-turn
    assert _wards(st) == 0


def test_canopy_copies_add_one_each_and_upgraded_copies_upgraded_wards():
    st = kokomi_state()
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 2
    st.player.powers[kokomi_plan.KURAGE_CANOPY_PLUS] = 1
    for i in range(2):
        kokomi_plan.schedule(st, _plan(i))
    st.player.hand = []
    _morning(st)
    assert _wards(st) == 2
    assert _wards(st, upgraded=True) == 1


def test_the_turn_start_reads_canopy_right_after_battle_formation():
    src = inspect.getsource(combat._player_turn)
    resolve = src.index("kokomi_plan.resolve_all(state)")
    formation = src.index("kokomi_plan.battle_formation(state)")
    canopy = src.index("kokomi_plan.kurage_canopy(state)")
    dawn = src.index("kokomi_plan.dawn_tide(state)")
    assert resolve < formation < canopy < dawn


# --- 4. Tide Wall -------------------------------------------------------------------

def test_tide_wall_plan_block_is_the_face_up_number():
    wall = loader.get_card("proto_kk_tide_wall")
    assert wall.effects == [{"op": "block", "amount": 4}]
    assert wall.plan == [{"op": "block_max_intent", "amount": 4}]
    up = upgrades.apply_upgrade(wall)
    assert up.effects[0]["amount"] == 6
    assert up.plan[0]["amount"] == 6
