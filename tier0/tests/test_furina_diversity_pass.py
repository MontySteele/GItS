"""FURINA, THE DIVERSITY PASS in the one-seat sim.

`review/ruled/furina-diversity-pass-2026-10-11.md` sec.2 and sec.3, ruled
2026-10-11 (all defaults): Headliner, Leading Lady, Full House and Packed
House in; Bravura at 7 Hydro for every 3 spent; Tutti! and Wriothesley to
Common; Lynette's act; the Final Bow, Casting Call and Ensemble Cast floors;
Gentle Current, Surging Waters, Pay the Tab and Sold Out cut. The C# twin is
`klee-mod/KleeTests/Prototype/FurinaDiversityPassTests.cs`.
"""

from __future__ import annotations

import copy
from collections import Counter

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(hp=78, max_hp=78, enemies=None):
    st = make_state(enemies=enemies or [make_enemy(hp=300)], hp=max_hp)
    st.player.character_id = "furina"
    st.player.hp = hp
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    return st


def _play(st, card):
    st.player.hand.append(card)
    combat.play_card(st, card)


# ---- the pool ---------------------------------------------------------------

def test_the_pool_is_78_at_23_35_20():
    pool = [loader.get_card(cid) for cid in FS.POOL_IDS]
    assert len(pool) == 78 == len(set(FS.POOL_IDS))
    assert Counter(c.rarity for c in pool) == {
        "common": 23, "uncommon": 35, "rare": 20}
    for cut in ("proto_fs_gentle_current", "proto_fs_surging_waters",
                "proto_fs_pay_the_tab", "proto_fs_sold_out"):
        assert cut not in FS.POOL_IDS
    for added in ("proto_fs_headliner", "proto_fs_the_leading_lady",
                  "proto_fs_the_full_house"):
        assert added in FS.POOL_IDS
    assert loader.get_card("proto_fs_tutti").rarity == "common"
    assert loader.get_card("proto_fs_guest_star_wriothesley").rarity == "common"


# ---- style 1 ----------------------------------------------------------------

def test_headliner_is_6_plus_2_a_guest():
    st = _furina()
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_headliner"))
    assert hp - st.enemies[0].hp == 6
    FS.guest_star(st, "charlotte")
    FS.guest_star(st, "sigewinne")
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_headliner+"))
    assert hp - st.enemies[0].hp == 9 + 2 * 2


def test_leading_lady_gives_strength_and_1_a_guest_to_attacks():
    st = _furina()
    _play(st, _card("proto_fs_the_leading_lady"))
    assert st.player.powers.get("strength") == 2
    assert FS.leading_lady_bonus(st) == 0
    FS.guest_star(st, "charlotte")
    FS.guest_star(st, "sigewinne")
    assert FS.leading_lady_bonus(st) == 2
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_headliner"))          # 6 + 2 x 2, +2 Str, +2
    assert hp - st.enemies[0].hp == 6 + 4 + 2 + 2
    st2 = _furina()
    _play(st2, _card("proto_fs_the_leading_lady+"))
    assert st2.player.powers.get("strength") == 3


def test_leading_lady_skips_a_guest_act():
    st = _furina()
    _play(st, _card("proto_fs_the_leading_lady"))
    FS.guest_star(st, "wriothesley")
    st.player.powers.pop("strength", None)
    hp = st.enemies[0].hp
    T.act(st, "wriothesley")
    assert hp - st.enemies[0].hp == T.WRIOTHESLEY_ACT


def test_bravura_hits_7_hydro_for_every_3_spent():
    st = _furina()
    st.player.ftd.fanfare = 10
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_bravura"))
    assert st.player.ftd.fanfare == 0
    assert hp - st.enemies[0].hp == 7 * 3          # 10 // 3 hits
    st = _furina()
    st.player.ftd.fanfare = 2
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_bravura+"))
    assert hp - st.enemies[0].hp == 0              # under 3: no hit
    st = _furina()
    st.player.ftd.fanfare = 6
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_bravura+"))
    assert hp - st.enemies[0].hp == 9 * 2
    row = loader.get_card("proto_fs_bravura")
    assert row.effects[1].get("applies_element") is True


# ---- style 2 ----------------------------------------------------------------

def test_full_house_spends_up_to_4_into_each_damage_act():
    st = _furina()
    _play(st, _card("proto_fs_the_full_house"))
    FS.guest_star(st, "wriothesley")
    FS.guest_star(st, "charlotte")
    st.player.ftd.fanfare = 6
    hp = st.enemies[0].hp
    T.act_all(st)
    # Wriothesley's act takes 4; Charlotte's deals no damage and takes none.
    assert hp - st.enemies[0].hp == T.WRIOTHESLEY_ACT + 4
    assert st.player.ftd.fanfare == 2


def test_full_house_upgraded_is_6_and_takes_what_is_left():
    st = _furina()
    _play(st, _card("proto_fs_the_full_house+"))
    FS.guest_star(st, "clorinde")
    st.player.ftd.fanfare = 3
    hp = st.enemies[0].hp
    T.act(st, "clorinde")
    assert hp - st.enemies[0].hp == T.CLORINDE_ACT + 3
    assert st.player.ftd.fanfare == 0


def test_tutti_draws_1_and_final_bow_draws_1_first():
    st = _furina()
    st.player.draw_pile = [_card("proto_fs_bubble_aria") for _ in range(3)]
    _play(st, _card("proto_fs_tutti"))
    assert len(st.player.hand) == 1
    # The upgrade census (2026-10-23): draws 2, at the same cost (was cost
    # 0, the same draw).
    up = _card("proto_fs_tutti+")
    assert up.cost == 1
    st = _furina()
    st.player.draw_pile = [_card("proto_fs_bubble_aria") for _ in range(3)]
    _play(st, up)
    assert len(st.player.hand) == 2
    st = _furina()
    st.player.draw_pile = [_card("proto_fs_bubble_aria") for _ in range(3)]
    _play(st, _card("proto_fs_final_bow"))         # empty stage: the draw
    assert len(st.player.hand) == 1


def test_lynette_hits_any_enemy_when_none_has_an_aura():
    st = _furina()
    FS.guest_star(st, "lynette")
    hp = st.enemies[0].hp
    T.act(st, "lynette")
    assert hp - st.enemies[0].hp == T.LYNETTE_ACT


def test_casting_call_draws_2_with_no_guest_star_in_the_pile():
    st = _furina()
    st.player.draw_pile = [_card("proto_fs_bubble_aria") for _ in range(3)]
    _play(st, _card("proto_fs_casting_call"))
    assert len(st.player.hand) == 2
    st = _furina()
    guest = _card("proto_fs_guest_star_clorinde")
    st.player.draw_pile = [_card("proto_fs_bubble_aria"), guest]
    _play(st, _card("proto_fs_casting_call"))
    assert [c for c in st.player.hand] == [guest]


def test_ensemble_cast_gives_4_seats_and_summons_a_guest_not_on_stage():
    st = _furina()
    for who in ("charlotte", "clorinde", "lynette"):
        FS.guest_star(st, who)
    _play(st, _card("proto_fs_ensemble_cast"))
    stage = FS.stage(st.player)
    assert len(stage) == 4
    assert stage[:3] == ["charlotte", "clorinde", "lynette"]
    assert stage[3] in FS.GUESTS and stage[3] not in stage[:3]
    assert stage[3] not in st.player.ftd.stage_up
