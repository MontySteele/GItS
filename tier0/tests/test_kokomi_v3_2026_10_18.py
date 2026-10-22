"""KOKOMI V3 (2026-10-18), the sim side.

Card paper `review/active/kokomi-cards-2026-10-18.md` sec.6; [USER]: "Makes
sense! ... let's do both."

  1. Tideturn, Feint and Turning Tide stop counting Plans that are Stings
     or Wards ("..., not Stings or Wards."). Breakwater keeps counting every
     Plan. Shoal of Spears was in this list until 2026-10-20, when it was
     exempted ([USER]: "It's already a Rare.") and counts every Plan again.
  2. Unbroken Tide, Uncommon Skill, 1: "Gain 8 [11] Block. Plan: If you lost
     no HP since you planned this, deal 12 [16] Hydro damage to ALL enemies."

The C# twin is `klee-mod/KleeTests/Prototype/KokomiV3Tests.cs`. NOTHING
MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import collections

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan, resources
from tier0.engine.state import Card
from tier0.tests.test_arm_keyword_tips import proto
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, write)

ATTACK = [{"kind": "attack", "amount": 6}]
STING_TAIL = ", not Stings or Wards."
# Kokomi text audit (2026-10-22, pick 2 (a)): the ruled spelling, its own
# sentence. Turning Tide keeps the short tail: the sentence would take it
# past the 120 ceiling.
DONT_COUNT = ". Stings and Wards don't count."


def _face(cid):
    return {r["id"]: r for r in proto._rows()}[cid]["description"]


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _play(st, c):
    """Play `c` face-up: an enemy intends to attack, so the pilot does not
    write it."""
    for e in st.enemies:
        e.intents = list(ATTACK)
    st.player.hand.append(c)
    assert not kokomi_plan.plan_aimed_at_pet(st, c)
    combat.play_card(st, c)


def _draw_plan(i):
    return Card(id=f"proto_kk_probe{i}", name=f"Probe {i}", cost=0,
                type="skill", effects=[],
                plan=[{"op": "draw", "amount": 1}])


def _plan_jellyfish(st):
    """One Sting and one Ward written on the Bake-Kurage."""
    kokomi_plan.schedule(st, card(kokomi_plan.STING_ID))
    kokomi_plan.schedule(st, card(kokomi_plan.WARD_ID))


# --- 1. the four texts, word for word ----------------------------------------

def test_the_three_faces_say_stings_and_wards_dont_count():
    assert _face("proto_kk_tideturn") == (
        "Deal {CalculationBase:diff()} [gold]Hydro[/gold] damage, plus "
        "{ExtraDamage:diff()} for each [gold]Plan[/gold] waiting" + DONT_COUNT
        + "{InCombat:\n(Deals {CalculatedDamage:diff()} damage)|}")
    assert _face("proto_kk_feint") == (
        "Deal 8 [gold]Hydro[/gold] damage. [gold]Plan[/gold]: Deal 6 "
        "[gold]Hydro[/gold] damage for each [gold]Plan[/gold] carried out "
        "this turn" + DONT_COUNT)
    assert _face("proto_kk_turning_tide_chain") == (
        "Deal 9 [gold]Hydro[/gold] damage. [gold]Plan[/gold]: Deal 5 "
        "[gold]Hydro[/gold] damage to ALL enemies per [gold]Plan[/gold] "
        "carried out this turn" + STING_TAIL)


def test_shoal_of_spears_is_exempt_and_counts_every_plan():
    # 2026-10-20, [USER]: "I'm wondering if we can drop the 'not stings or
    # wards' condition from Shoal of Spears. It's already a Rare."
    assert _face("proto_kk_shoal_of_spears") == (
        "Deal {Damage:diff()} [gold]Hydro[/gold] damage to ALL enemies, plus "
        "once more for each [gold]Plan[/gold] waiting."
        "{InCombat:\n(Deals {TotalDamage:diff()} damage)|}")
    shoal = loader.get_card("proto_kk_shoal_of_spears").effects[0]
    assert shoal["times"] == "plans_held_plus_one"


def test_breakwater_is_unchanged():
    # Battle Formation stopped counting Stings and Wards in the Kokomi finish
    # pass (2026-10-19, `test_kokomi_finish_pass_2026_10_19`).
    assert "Stings" not in _face("proto_kk_breakwater")
    bw = loader.get_card("proto_kk_breakwater").effects[0]
    assert bw["amount_formula"]["count"] == "plans_held"


# --- 1. the counts -------------------------------------------------------------

def test_tideturn_counts_a_real_plan_and_not_a_sting_or_ward():
    st = kokomi_state()
    _plan_jellyfish(st)
    kokomi_plan.schedule(st, _draw_plan(0))
    assert len(st.kk_plan_queue) == 3
    assert kokomi_plan.chain_plans_held(st) == 1
    hp = st.enemies[0].hp
    _play(st, card("proto_kk_tideturn"))
    assert hp - st.enemies[0].hp == 8 + 8 * 1


def test_tideturn_with_only_stings_and_wards_waiting_is_its_floor():
    st = kokomi_state()
    _plan_jellyfish(st)
    hp = st.enemies[0].hp
    _play(st, card("proto_kk_tideturn"))
    assert hp - st.enemies[0].hp == 8


def test_shoal_of_spears_hits_once_more_per_plan_stings_and_wards_too():
    st = kokomi_state(n_enemies=2)
    _plan_jellyfish(st)
    kokomi_plan.schedule(st, _draw_plan(0))
    kokomi_plan.schedule(st, _draw_plan(1))
    before = [e.hp for e in st.enemies]
    _play(st, card("proto_kk_shoal_of_spears"))
    # One hit, plus one for each of the four Plans waiting: the two real
    # Plans, the Sting and the Ward (the 2026-10-20 exemption).
    assert [b - e.hp for b, e in zip(before, st.enemies)] == [35, 35]


def test_feint_counts_itself_and_real_plans_not_stings_or_wards():
    st = kokomi_state()
    kokomi_plan.schedule(st, card(kokomi_plan.STING_ID))
    kokomi_plan.schedule(st, _draw_plan(0))
    kokomi_plan.schedule(st, card(kokomi_plan.WARD_ID))
    write(st, card("proto_kk_feint"))
    st.player.draw_pile = [card("proto_kk_coral_bulwark") for _ in range(4)]
    hp = st.enemies[0].hp
    st.player.energy = 10
    kokomi_plan.resolve_all(st)
    # Four carried out, two of them real (the probe and Feint itself). The
    # Sting's own hit lands on the front enemy too, so read Feint's event.
    assert st.kk_plans_carried_out_this_turn == 4
    assert st.kk_chain_plans_this_turn == 2
    feint = [e for e in st.log if e["event"] == "plan_carried_out"
             and e["card"] == "proto_kk_feint"]
    assert feint
    assert hp - st.enemies[0].hp >= 6 * 2


def test_feint_alone_behind_stings_deals_one_rate():
    st = kokomi_state()
    kokomi_plan.schedule(st, card(kokomi_plan.WARD_ID))
    kokomi_plan.schedule(st, card(kokomi_plan.WARD_ID))
    write(st, card("proto_kk_feint"))
    hp = st.enemies[0].hp
    carry_out(st)
    # Wards deal nothing; Feint counts only itself.
    assert hp - st.enemies[0].hp == 6
    assert st.kk_plans_carried_out_this_turn == 3


def test_turning_tide_skips_a_ward_and_the_turn_roll_clears():
    st = kokomi_state(n_enemies=2)
    kokomi_plan.schedule(st, card(kokomi_plan.WARD_ID))
    kokomi_plan.schedule(st, _draw_plan(0))
    write(st, card("proto_kk_turning_tide_chain"))
    st.player.draw_pile = [card("proto_kk_coral_bulwark")]
    before = [e.hp for e in st.enemies]
    carry_out(st)
    assert [b - e.hp for b, e in zip(before, st.enemies)] == [10, 10]
    kokomi_plan.roll_turn(st)
    assert st.kk_chain_plans_this_turn == 0


def test_battle_formation_no_longer_counts_a_sting_or_ward():
    # The Kokomi finish pass (2026-10-19): "Stings and Wards don't count."
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    _plan_jellyfish(st)
    st.player.energy = 0
    kokomi_plan.resolve_all(st)
    kokomi_plan.battle_formation(st)
    assert st.kk_plans_carried_out_this_turn == 2
    assert st.kk_chain_plans_this_turn == 0
    assert st.player.energy == 0


# --- 2. Unbroken Tide ----------------------------------------------------------

def test_unbroken_tide_row():
    row = loader.get_card("proto_kk_unbroken_tide")
    assert (row.cost, row.type, row.rarity) == (1, "skill", "uncommon")
    assert _face("proto_kk_unbroken_tide") == (
        "Gain 8 [gold]Block[/gold]. [gold]Plan[/gold]: If you lost no HP "
        "since you planned this, deal 12 [gold]Hydro[/gold] damage to ALL "
        "enemies.")
    assert row.effects == [{"op": "block", "amount": 8}]
    assert row.plan == [{"op": "damage_if_no_hp_lost_since", "amount": 12,
                         "target": "all_enemies"}]
    up = _up("proto_kk_unbroken_tide")
    assert up.effects[0]["amount"] == 11
    assert up.plan[0]["amount"] == 16
    op = kokomi_plan.DAMAGE_IF_NO_HP_LOST_SINCE
    assert op in kokomi_plan.PLAN_ONLY_OPS
    assert op in kokomi_plan.PLAN_KINDS
    assert op in kokomi_plan.PLAN_AIMED_OPS


def test_unbroken_tide_fires_when_no_hp_was_lost():
    st = kokomi_state(n_enemies=2)
    write(st, card("proto_kk_unbroken_tide"))
    # A fully blocked hit is no HP lost.
    kokomi_plan.note_enemy_hit(st, st.enemies[0], blocked=6, incoming=6)
    before = [e.hp for e in st.enemies]
    carry_out(st)
    assert [b - e.hp for b, e in zip(before, st.enemies)] == [12, 12]


def test_unbroken_tide_does_not_fire_if_hp_was_lost():
    st = kokomi_state(n_enemies=2)
    write(st, card("proto_kk_unbroken_tide"))
    st.player.hp -= 1
    resources.note_player_hp_loss(st, 1)
    before = [e.hp for e in st.enemies]
    carry_out(st)
    assert [b - e.hp for b, e in zip(before, st.enemies)] == [0, 0]


def test_unbroken_tide_reads_a_real_enemy_attack_through_block():
    st = kokomi_state()
    e = st.enemies[0]
    write(st, card("proto_kk_unbroken_tide"))
    e.intents = [{"kind": "attack", "amount": 7}]
    st.in_player_turn = False
    st.player.block = 5
    combat._enemy_turn(st, e)
    st.in_player_turn = True
    hp = e.hp
    carry_out(st)
    assert hp - e.hp == 0


def test_unbroken_tide_hp_lost_before_it_was_written_does_not_count():
    st = kokomi_state()
    st.player.hp -= 3
    resources.note_player_hp_loss(st, 3)
    write(st, card("proto_kk_unbroken_tide"))
    hp = st.enemies[0].hp
    carry_out(st)
    assert hp - st.enemies[0].hp == 12


# --- the pool -------------------------------------------------------------------

def test_the_pool_is_79_at_20_39_20_with_unbroken_tide_last():
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == len(set(ids)) == 79
    assert ids[-5] == "proto_kk_unbroken_tide"
    rarity = collections.Counter(loader.get_card(cid).rarity for cid in ids)
    assert rarity == {"common": 20, "uncommon": 39, "rare": 20}
