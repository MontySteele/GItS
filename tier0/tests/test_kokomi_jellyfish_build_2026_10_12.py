"""THE KOKOMI JELLYFISH BUILD (2026-10-12), the sim side.

Paper `review/ruled/kokomi-jellyfish-growth-2026-10-12.md`, ruled at all
defaults ([USER]: "Good with all defaults." and "I'm actually totally fine
with 0-cost plans"). Stings and Wards are the Silent's Shivs with a Plan line,
the generators are at the Silent's rates, Endless Shoal is the Uncommon "a
Sting per Plan carried out", and two growth cards join: All Streams Flow to
the Sea (Rare) and The Shape of Water (Uncommon). Measured Breath and Spring
Tide are cut. Provenance note "Kokomi jellyfish build". The C# twin is
`klee-mod/KleeTests/Prototype/KokomiJellyfishBuildTests.cs`. NOTHING
MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import collections

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects, kokomi_plan
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, write)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _attacking(st):
    """Every enemy intends an attack, so the pilot plays a card face-up."""
    for e in st.enemies:
        e.intents = [{"kind": "attack", "amount": 5}]


def _play(st, c):
    st.player.hand.append(c)
    assert not kokomi_plan.plan_aimed_at_pet(st, c)
    combat.play_card(st, c)


# --- the tokens ----------------------------------------------------------------

def test_the_sting_costs_0_and_keeps_its_plan_line():
    row, up = loader.get_card(kokomi_plan.STING_ID), _up(kokomi_plan.STING_ID)
    assert row.cost == 0 and up.cost == 0
    assert row.is_ethereal and row.exhaust
    assert row.effects == [{"op": "damage", "amount": 4, "target": "enemy"}]
    assert row.plan == [{"op": "damage", "amount": 3,
                         "target": "all_enemies"}]
    assert up.effects[0]["amount"] == 6 and up.plan[0]["amount"] == 4


def test_the_ward_costs_0_and_keeps_its_plan_line():
    row, up = loader.get_card(kokomi_plan.WARD_ID), _up(kokomi_plan.WARD_ID)
    assert row.cost == 0 and up.cost == 0
    assert row.is_ethereal and row.exhaust
    assert row.effects == [{"op": "block", "amount": 4}]
    assert row.plan == [{"op": "apply_power", "power": "weak", "amount": 1,
                         "target": "front_enemy"}]
    assert up.effects[0]["amount"] == 6 and up.plan[0]["amount"] == 2


def test_a_0_cost_sting_can_still_be_written_and_carried_out():
    st = kokomi_state(n_enemies=2)
    st.player.energy = 0
    write(st, card(kokomi_plan.STING_ID))
    assert len(st.kk_plan_queue) == 1
    before = [e.hp for e in st.enemies]
    carry_out(st)
    assert [b - e.hp for b, e in zip(before, st.enemies)] == [3, 3]


# --- the generators -------------------------------------------------------------

@pytest.mark.parametrize("cid,base,up", [
    ("proto_kk_jellyfish_drift", 6, 8),
    ("proto_kk_watatsumi_drill", 6, 9),
    # Kokomi round 3 A-list (2026-10-13): 6 [9], Cloak and Dagger's 6.
    ("proto_kk_bubble_ward", 6, 9),
])
def test_the_generators_are_at_the_silents_rates(cid, base, up):
    row = loader.get_card(cid)
    assert row.cost == 1
    assert (row.effects[0]["amount"], _up(cid).effects[0]["amount"]) == (
        base, up)


def test_shoal_call_is_blade_dance_with_plain_stings():
    row = loader.get_card("proto_kk_shoal_call")
    # Common since the Kokomi review (2026-10-13).
    assert row.cost == 1 and row.exhaust and row.rarity == "common"
    assert row.effects == [{"op": "kokomi", "kind": "shoal_call",
                            "amount": 3}]
    assert _up("proto_kk_shoal_call").effects[0]["amount"] == 4
    st = kokomi_state()
    _play(st, card("proto_kk_shoal_call"))
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID] * 3


# --- Endless Shoal --------------------------------------------------------------

def test_endless_shoal_is_an_uncommon_power_at_1_innate_upgraded():
    row, up = (loader.get_card("proto_kk_endless_shoal"),
               _up("proto_kk_endless_shoal"))
    assert (row.type, row.cost, row.rarity) == ("power", 1, "uncommon")
    assert up.cost == 1 and up.innate and not row.innate


def test_endless_shoal_adds_a_sting_per_carry_out():
    st = kokomi_state()
    st.player.powers[kokomi_plan.ENDLESS_SHOAL] = 1
    write(st, card("proto_kk_brine_sting"))
    write(st, card(kokomi_plan.WARD_ID))
    st.player.hand.clear()
    carry_out(st)
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID] * 2


def test_endless_shoal_on_a_doubled_carry_out_gives_two_stings():
    """Nereid's Ascension carries the first Plan of the morning out twice:
    two carry-outs, two Stings."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.ENDLESS_SHOAL] = 1
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    write(st, card("proto_kk_brine_sting"))
    st.player.hand.clear()
    carry_out(st)
    assert st.kk_plans_carried_out_this_combat == 2
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID] * 2


def test_endless_shoal_copies_stack():
    st = kokomi_state()
    st.player.powers[kokomi_plan.ENDLESS_SHOAL] = 2
    write(st, card("proto_kk_brine_sting"))
    st.player.hand.clear()
    carry_out(st)
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID] * 2


# --- what "played" means ----------------------------------------------------------

def test_a_played_sting_counts_and_a_written_one_does_not():
    st = kokomi_state()
    write(st, card(kokomi_plan.STING_ID))
    assert st.kk_stings_played_this_combat == 0
    carry_out(st)                       # a carry-out is not her play either
    assert st.kk_stings_played_this_combat == 0
    _attacking(st)
    _play(st, card(kokomi_plan.STING_ID))
    _play(st, _up(kokomi_plan.STING_ID))
    assert st.kk_stings_played_this_combat == 2
    assert st.kk_stings_played_this_turn == 2
    # Brine Sting is not a Sting.
    _play(st, card("proto_kk_brine_sting"))
    assert st.kk_stings_played_this_combat == 2


def test_a_flipped_sting_carried_out_is_not_played():
    st = kokomi_state()
    write(st, card(kokomi_plan.STING_ID))
    assert kokomi_plan.flip(st, 0)
    carry_out(st)
    assert st.kk_stings_played_this_combat == 0


def test_the_turn_count_rolls_and_the_combat_count_does_not():
    st = kokomi_state()
    _attacking(st)
    _play(st, card(kokomi_plan.STING_ID))
    kokomi_plan.roll_turn(st)
    assert st.kk_stings_played_this_turn == 0
    assert st.kk_stings_played_this_combat == 1
    assert effects._runtime_count(st, "stings_played_this_turn") == 0
    assert effects._runtime_count(st, "stings_played_this_combat") == 1


# --- All Streams Flow to the Sea ------------------------------------------------------

def test_all_streams_is_a_rare_attack_at_1():
    row = loader.get_card("proto_kk_all_streams_flow")
    assert (row.type, row.cost, row.rarity) == ("attack", 1, "rare")
    assert row.effects[0]["amount_formula"] == {
        "base": 4, "per": 2, "count": "stings_played_this_combat"}
    assert _up("proto_kk_all_streams_flow").effects[0]["amount_formula"][
        "base"] == 8


def test_all_streams_counts_every_sting_played_this_combat():
    st = kokomi_state()
    _attacking(st)
    st.enemies[0].hp = st.enemies[0].max_hp = 500
    for _ in range(3):
        _play(st, card(kokomi_plan.STING_ID))
    kokomi_plan.roll_turn(st)           # a new turn: the combat count stays
    _play(st, card(kokomi_plan.STING_ID))
    write_target = card(kokomi_plan.STING_ID)
    st.enemies[0].intents = [{"kind": "block", "amount": 5}]
    write(st, write_target)             # written: not counted
    _attacking(st)
    assert st.kk_stings_played_this_combat == 4
    hp = st.enemies[0].hp
    _play(st, card("proto_kk_all_streams_flow"))
    assert hp - st.enemies[0].hp == 4 + 2 * 4


# --- The Shape of Water ------------------------------------------------------------------
# Kokomi review (2026-10-13), pick (a): a base hit. "Deal 5 [7] Hydro damage,
# plus 5 [7] for each Sting you played this turn." (was 0 + 6 [8] each).

def test_the_shape_of_water_is_an_uncommon_attack_at_1():
    row = loader.get_card("proto_kk_the_shape_of_water")
    assert (row.type, row.cost, row.rarity) == ("attack", 1, "uncommon")
    assert row.effects[0]["amount_formula"] == {
        "base": 5, "per": 5, "count": "stings_played_this_turn"}
    up = _up("proto_kk_the_shape_of_water").effects[0]["amount_formula"]
    assert (up["base"], up["per"]) == (7, 7)


def test_the_shape_of_water_counts_this_turn_only():
    st = kokomi_state()
    _attacking(st)
    st.enemies[0].hp = st.enemies[0].max_hp = 500
    _play(st, card(kokomi_plan.STING_ID))
    kokomi_plan.roll_turn(st)           # last turn's Sting does not count
    _play(st, card(kokomi_plan.STING_ID))
    _play(st, card(kokomi_plan.STING_ID))
    hp = st.enemies[0].hp
    _play(st, card("proto_kk_the_shape_of_water"))
    assert hp - st.enemies[0].hp == 5 + 5 * 2 == 15


def test_the_shape_of_water_with_no_stings_deals_its_base():
    st = kokomi_state()
    _attacking(st)
    st.enemies[0].hp = st.enemies[0].max_hp = 500
    hp = st.enemies[0].hp
    _play(st, card("proto_kk_the_shape_of_water"))
    assert hp - st.enemies[0].hp == 5


@pytest.mark.parametrize("stings, dealt", [(0, 7), (2, 21)])
def test_the_shape_of_water_upgraded(stings, dealt):
    st = kokomi_state()
    _attacking(st)
    st.enemies[0].hp = st.enemies[0].max_hp = 500
    for _ in range(stings):
        _play(st, card(kokomi_plan.STING_ID))
    hp = st.enemies[0].hp
    _play(st, _up("proto_kk_the_shape_of_water"))
    assert hp - st.enemies[0].hp == dealt


# --- the pool ------------------------------------------------------------------------

def test_the_pool_stays_78_at_20_38_20():
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == len(set(ids)) == 78
    rows = {c.id for c in loader.prototype_cards()}
    for gone in ("proto_kk_measured_breath", "proto_kk_spring_tide"):
        assert gone not in ids and gone not in rows
    assert C.KOKOMI_JELLYFISH_IDS == ("proto_kk_all_streams_flow",
                                      "proto_kk_the_shape_of_water")
    assert set(C.KOKOMI_JELLYFISH_IDS) <= set(ids)
    assert "proto_kk_endless_shoal" in ids
    rarity = collections.Counter(loader.get_card(cid).rarity for cid in ids)
    assert rarity == {"common": 20, "uncommon": 38, "rare": 20}
    assert "draw_if_no_plan" not in kokomi_plan.KINDS
