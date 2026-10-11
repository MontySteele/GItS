"""KOKOMI GROWTH POWERS (2026-10-10): Rising Tide in, The General's Banner
out, Grand Design bent, Brine Sting deals damage.

Brief `review/active/kokomi-growth-powers-2026-10-10.md`, ruled ("Agreed on
both"). The sim half; the C# twin is
`KleeTests/Prototype/KokomiGrowthPowersTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).
"""

from __future__ import annotations

import collections
import inspect

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    _faces, carry_out, kokomi_state, overhaul)


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _casket(**kw):
    st = kokomi_state(**kw)
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    return st


# --- the pool -----------------------------------------------------------------

def test_rising_tide_replaces_the_generals_banner(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == len(set(ids)) == 78
    assert ids[-1:] == C.KOKOMI_GROWTH_POWERS_IDS == ("proto_kk_rising_tide",)
    assert "proto_kk_the_generals_banner" not in ids
    assert "proto_kk_the_generals_banner" not in {
        c.id for c in loader.prototype_cards()}
    rarity = collections.Counter(_row(cid).rarity for cid in ids)
    assert rarity == {"common": 21, "uncommon": 36, "rare": 21}


# --- Rising Tide ---------------------------------------------------------------

def test_rising_tide_row(overhaul):
    row = _row("proto_kk_rising_tide")
    assert (row.cost, row.type, row.rarity) == (1, "power", "uncommon")
    assert _faces()[row.id] == (
        "At the start of your turn, the [gold]Casket[/gold] gains 1.")
    assert row.effects == [{"op": "apply_power",
                            "power": kokomi_plan.RISING_TIDE, "amount": 1,
                            "target": "self"}]
    assert not row.innate
    up = _up("proto_kk_rising_tide")
    assert up.cost == 1 and up.innate


def test_rising_tide_adds_one_per_copy_each_turn(overhaul):
    st = kokomi_state()
    kokomi_plan.rising_tide(st)
    assert st.kk_casket == 0                     # not worn: nothing
    st.player.powers[kokomi_plan.RISING_TIDE] = 1
    kokomi_plan.rising_tide(st)
    assert st.kk_casket == 1                     # no relic asked
    st.player.powers[kokomi_plan.RISING_TIDE] = 2    # two copies
    kokomi_plan.rising_tide(st)
    assert st.kk_casket == 3


def test_rising_tide_is_paid_at_the_long_game_site(overhaul):
    src = inspect.getsource(combat._player_turn)
    draw = src.index("refpowers.player_turn_start_late(state)")
    long_game = src.index("kokomi_plan.long_game(")
    rising = src.index("kokomi_plan.rising_tide(state)")
    morning = src.index("kokomi_plan.resolve_all(state)")
    assert draw < long_game < rising < morning


# --- Grand Design --------------------------------------------------------------

def test_grand_design_row_is_bent(overhaul):
    row = _row("proto_kk_grand_design")
    assert (row.cost, row.type, row.rarity) == (2, "power", "rare")
    assert _faces()[row.id] == (
        "[gold]Open the Casket[/gold] no longer empties the "
        "[gold]Casket[/gold].")
    up = _up("proto_kk_grand_design")
    assert up.cost == 1 and not up.innate


def _open(st):
    token = kokomi_plan.open_the_casket_card()
    st.player.hand.append(token)
    st.player.energy = 3
    combat.play_card(st, token)


def test_open_empties_the_casket_without_grand_design(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    st.kk_casket = 3
    _open(st)
    assert st.player.powers.get("strength") == 3
    assert st.kk_casket == 0


def test_grand_design_keeps_the_count_and_gives_the_whole_count(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    st.player.powers[kokomi_plan.GRAND_DESIGN] = 1
    st.kk_casket = 3
    _open(st)
    assert st.player.powers.get("strength") == 3
    assert st.kk_casket == 3                     # kept
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert st.kk_casket == 4
    _open(st)
    assert st.player.powers.get("strength") == 3 + 4
    assert st.kk_casket == 4


def test_grand_design_no_longer_feeds_the_casket_per_energy(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    st.player.powers[kokomi_plan.GRAND_DESIGN] = 1
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert st.kk_casket == C.KOKOMI_OVERHAUL_CASKET_PER_PLAN == 1


# --- Brine Sting ---------------------------------------------------------------

def test_brine_sting_plans_3_damage_then_weak(overhaul):
    row = _row("proto_kk_brine_sting")
    assert (row.cost, row.type, row.rarity) == (0, "skill", "common")
    assert _faces()[row.id] == (
        "[gold]Plan[/gold]: Deal 3 [gold]Hydro[/gold] damage. Apply 1 "
        "[gold]Weak[/gold].")
    assert row.plan == [
        {"op": "damage", "amount": 3, "target": "front_enemy"},
        {"op": "apply_power", "power": "weak", "amount": 1,
         "target": "front_enemy"}]
    assert _up("proto_kk_brine_sting").plan[1]["amount"] == 2
    assert _up("proto_kk_brine_sting").plan[0]["amount"] == 3


def test_brine_sting_carried_out_hits_and_weakens(overhaul):
    enemy = make_enemy(hp=50)
    st = kokomi_state(enemies=[enemy])
    carry_out(st, _row("proto_kk_brine_sting").plan)
    assert enemy.hp == 50 - 3
    assert enemy.powers.get("weak") == 1


# --- the two raises that were already in place ----------------------------------

def test_kurage_canopy_and_ceremonial_garment_print_2_and_3(overhaul):
    for cid in ("proto_kk_kurage_canopy", "proto_kk_ceremonial_garment"):
        assert _row(cid).effects[0]["amount"] == 2
        assert _up(cid).effects[0]["amount"] == 3
