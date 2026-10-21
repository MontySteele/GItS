"""The Kokomi level pass (2026-10-12), the sim side.

`review/ruled/kokomi-level-pass-2026-10-12.md`, ruled "On the Kokomi level
paper - agreed on all defaults": section 1's trims and section 2's floors.
Provenance note "Kokomi level pass, 2026-10-12". The C# twin is
`klee-mod/KleeTests/Prototype/KokomiLevelPassTests.cs`. NOTHING MEASURED HERE
IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import collections

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import kokomi_plan
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, write)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


# --- section 1: the trims ----------------------------------------------------

def test_the_trims_print_the_papers_numbers():
    crash, rebuke = card("proto_kk_coral_crash"), card("proto_kk_tidal_rebuke")
    assert (crash.cost, _up("proto_kk_coral_crash").cost) == (1, 0)
    assert (rebuke.cost, _up("proto_kk_tidal_rebuke").cost) == (2, 1)
    assert rebuke.retain
    flotsam = card("proto_kk_flotsam_surge")
    assert (flotsam.effects[0]["amount"],
            _up("proto_kk_flotsam_surge").effects[0]["amount"]) == (10, 13)
    tide = card("proto_kk_steady_tide")
    assert (tide.effects[0]["amount"],
            _up("proto_kk_steady_tide").effects[0]["amount"]) == (9, 12)
    assert tide.ethereal and tide.plan == [{"op": "draw", "amount": 3}]
    # The Kokomi upgrade pass (2026-10-19): Plan draw 3 [4].
    assert _up("proto_kk_steady_tide").plan == [{"op": "draw", "amount": 4}]
    ruin = card("proto_kk_riptide_ruin")
    assert ruin.effects == [{"op": "damage", "amount": 11,
                             "target": "all_enemies", "times": 2}]
    assert _up("proto_kk_riptide_ruin").effects[0]["amount"] == 14


def test_change_of_plans_is_uncommon_and_the_split_is_20_38_20():
    assert card("proto_kk_change_of_plans").rarity == "uncommon"
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 79  # Kokomi v3 (2026-10-18): Unbroken Tide
    rarity = collections.Counter(loader.get_card(c).rarity for c in ids)
    assert rarity == {"common": 20, "uncommon": 39, "rare": 20}


# --- section 2: the floors ---------------------------------------------------

def test_flank_reads_the_intents_when_carried_out():
    """Written over a board of Defends, carried out over attackers: it hits
    the attackers, as Tide Wall reads its intent."""
    st = kokomi_state(n_enemies=2)
    for e in st.enemies:
        e.intents = [{"kind": "defend", "amount": 5}]
    write(st, card("proto_kk_flank"))
    st.enemies[1].intents = [{"kind": "attack", "amount": 6}]
    hp = [e.hp for e in st.enemies]
    carry_out(st)
    assert st.enemies[0].hp == hp[0]
    assert st.enemies[1].hp < hp[1]
    assert _up("proto_kk_flank").plan[0]["amount"] == 14


def test_war_banner_blocks_now_and_plans_permanent_strength():
    banner = card("proto_mi_gorou_war_banner")
    assert banner.effects == [{"op": "block", "amount": 7}]
    assert banner.plan == [{"op": "gain_strength", "amount": 1}]
    up = _up("proto_mi_gorou_war_banner")
    # Kokomi balance audit, ruled 2026-10-21: the upgrade adds Block only.
    assert (up.effects[0]["amount"], up.plan[0]["amount"]) == (10, 1)


def test_orders_from_the_shrine_offers_three_and_keeps_one():
    st = kokomi_state()
    orders = card("proto_kk_orders_from_the_shrine")
    assert (orders.cost, _up("proto_kk_orders_from_the_shrine").cost) == (1, 0)
    before = len(st.player.hand)
    assert kokomi_plan.choose_common_companion(st) == 1
    offered = [e for e in st.log if e["event"] == "kk_companions_offered"]
    assert offered and len(offered[0]["cards"]) == min(
        3, len(kokomi_plan.generated_companions(st, "common")))
    assert len(st.player.hand) == before + 1
    added = st.player.hand[-1]
    assert added.ethereal and added.rarity == "common"


def test_crystal_collapse_reads_a_companion_from_an_earlier_turn():
    st = kokomi_state()
    juuga = card("proto_mi_gorou_juuga")
    kokomi_plan.note_companion_played(st, juuga)
    kokomi_plan.roll_turn(st)
    collapse = card("proto_mi_gorou_crystal_collapse")
    kokomi_plan.note_companion_played(st, collapse)
    assert kokomi_plan.last_other_companion(st, collapse) is juuga
