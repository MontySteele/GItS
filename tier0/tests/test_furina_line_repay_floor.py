"""THE POOL-75 ROUND'S RULINGS, BUILT, in the sim (2026-10-09).

`review/records/furina-pool75-round-2026-10-09.md`, "Picks (ruled
2026-10-09)": the Drain line rule (3/4 line, Drain past it, the two-part
ledger, the curtain call, Repay's order, A Five-Century Act's new text,
Lyney), the Repay floor card by card, and the ruled card numbers. The line,
the split, the Repay order and the curtain call are also pinned rule by rule
in `test_furina_tide_arm.py`. The C# twin is
`klee-mod/KleeTests/Prototype/FurinaLineRepayFloorTests.cs`.
"""

from __future__ import annotations

import copy

from tier0.content import loader
from tier0.engine import combat, effects, furina_stage as FS, furina_tide as T
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


# ---- the Drain line rule -------------------------------------------------------

def test_the_arm_runs_the_three_quarter_line():
    st = _furina()
    assert st.player.ftd.line == T.LINE_SHARE == 0.75
    assert (T.LINE_NUMERATOR, T.LINE_DENOMINATOR, T.DRAIN_FLOOR) == (3, 4, 1)
    assert T.line_hp(st.player) == 59


def test_a_drain_records_its_split_on_the_ledger_and_the_past_part_is_lost():
    st = _furina()
    _play(st, _card("proto_fs_mademoiselle_crabaletta"))   # Drain 5: 73
    for _ in range(3):
        _play(st, _card("proto_fs_mademoiselle_crabaletta"))
    f = st.player.ftd
    assert st.player.hp == 58                               # 20 drained
    assert (f.drained_above, f.drained_past) == (19, 1)
    FS.close_combat(st)
    assert st.player.hp == 77


def test_near_the_line_counts_any_hp_at_or_below_it():
    st = _furina()                                          # line 59
    st.player.hp = 64
    assert FS.near_line(st.player)                          # 5 over it
    st.player.hp = 65
    assert not FS.near_line(st.player)
    st.player.hp = 40
    assert FS.near_line(st.player)                          # below it
    st.player.hp = 59
    assert FS.near_line(st.player)


def test_a_five_century_act_reads_its_new_text():
    row = _card("proto_fs_a_five_century_act")
    assert (row.cost, row.rarity) == (2, "rare")
    st = _furina()
    effects.resolve_card(st, row)
    FS.drain(st, 30)
    FS.close_combat(st)
    assert st.player.hp == 78


# ---- the Repay floor ------------------------------------------------------------

def test_the_damage_cards_repay_first_then_add_the_leftover():
    for cid, base, n in (("proto_fs_surging_waters", 6, 3),
                         ("proto_fs_hydro_lance", 14, 4),
                         ("proto_fs_cleansing_torrent", 10, 4)):
        row = _card(cid)
        assert [fx["op"] for fx in row.effects] == ["stage_repay", "damage"]
        # Nothing drained: the whole N is added.
        st = _furina()
        hp = st.enemies[0].hp
        _play(st, _card(cid))
        assert st.enemies[0].hp == hp - (base + n), cid
        # One drained: N - 1 is added.
        st = _furina()
        FS.drain(st, 1)
        hp = st.enemies[0].hp
        _play(st, _card(cid))
        assert st.player.hp == 78
        assert st.enemies[0].hp == hp - (base + n - 1), cid
        # Everything returned: the printed damage.
        st = _furina()
        FS.drain(st, 10)
        hp = st.enemies[0].hp
        _play(st, _card(cid))
        assert st.enemies[0].hp == hp - base, cid


def test_hymn_pays_block_for_what_it_could_not_repay():
    st = _furina()
    FS.drain(st, 1)
    _play(st, _card("proto_fs_hymn_of_many_waters"))        # 8 + (3 - 1)
    assert st.player.block == 10
    st = _furina()
    _play(st, _card("proto_fs_hymn_of_many_waters+"))       # 11 + 4
    assert st.player.block == 15


def test_soothing_waters_pays_vigor():
    st = _furina()
    _play(st, _card("proto_fs_soothing_waters"))
    assert st.player.powers.get("next_attack_up") == 2
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_soloists_solicitation"))      # 6 + 2 Vigor
    assert st.enemies[0].hp == hp - 8
    assert not st.player.powers.get("next_attack_up")


def test_gentle_current_pays_block_when_its_repay_lands_next_turn():
    st = _furina()
    _play(st, _card("proto_fs_gentle_current"))
    assert st.player.block == 5
    st.player.block = 0
    T.turn_start(st)
    assert st.player.block == 4


def test_fountain_pays_block_each_turn_and_pneuma_tides_vigor():
    st = _furina()
    effects.resolve_card(st, _card("proto_fs_fountain_of_lucine"))
    FS.drain(st, 1)
    T.turn_start(st)
    assert st.player.block == 2                             # 3 - 1
    st.player.block = 0
    T.turn_start(st)
    assert st.player.block == 3
    st = _furina()
    effects.resolve_card(st, _card("proto_fs_pneuma_tides"))
    T.turn_start(st)
    assert st.player.powers.get("next_attack_up") == 2


def test_grand_entrance_charlotte_and_sigewinne_pay_block():
    st = _furina()
    effects.resolve_card(st, _card("proto_fs_grand_entrance"))
    _play(st, _card("proto_fs_guest_star_charlotte"))
    assert st.player.block == 4
    st.player.block = 0
    T.act(st, "charlotte")
    assert st.player.block == 2
    st = _furina()
    st.player.ftd.stage = ["sigewinne"]
    FS.drain(st, 1)
    T.act(st, "sigewinne")
    # Her line's Block of the 1 returned, then the floor's 1.
    assert st.player.block == 2


def test_the_unchanged_repays_pay_no_floor():
    for cid in ("proto_fs_pneuma_refrain", "proto_fs_clean_slate",
                "proto_fs_balance_the_books", "proto_fs_rising_tide",
                "proto_fs_riptide_lunge", "proto_fs_ebb_and_flow",
                "proto_fs_singer_of_many_waters",
                "proto_fs_grand_absolution"):
        row = _card(cid)
        for fx in row.effects:
            assert "floor" not in fx, cid


def test_endless_waltz_is_cut():
    assert "proto_fs_endless_waltz" not in FS.POOL_IDS
    assert all(c.id != "proto_fs_endless_waltz"
               for c in loader.prototype_cards())
    assert "endless_waltz" not in FS.ARM_POWER_IDS


# ---- the ruled card numbers ----------------------------------------------------------

def test_the_ruled_card_numbers():
    assert _card("proto_fs_standing_ovation_all").rarity == "uncommon"
    crab = _card("proto_fs_mademoiselle_crabaletta")
    assert crab.effects[1]["amount"] == 20
    solo = _card("proto_fs_soloists_solicitation")
    assert solo.effects[1]["amount"] == 6
    assert _card("proto_fs_soloists_solicitation+").effects[1]["amount"] == 9
    assert _card("proto_fs_mademoiselle_crabaletta+").effects[1]["amount"] == 26
    gaze = _card("proto_fs_commanding_gaze").effects[0]["modes"][0]
    assert gaze["effects"][0]["amount"] == 2
    assert _card("proto_fs_guest_star_neuvillette").cost == 1


def test_bravuras_upgrade_raises_the_base_to_ten():
    st = _furina()
    st.player.ftd.fanfare = 5
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_bravura+"))
    assert st.enemies[0].hp == hp - (10 + 2 * 5)


def test_freminets_act_also_gives_block():
    st = _furina()
    st.player.ftd.stage = ["freminet"]
    T.act(st, "freminet")
    assert st.player.block == 6
    st.player.ftd.stage_up = {"freminet"}
    st.player.block = 0
    T.act(st, "freminet")
    assert st.player.block == 9


def test_neuvillette_acts_for_all_hp_lost_since_her_last_turn():
    st = _furina(enemies=[make_enemy(hp=300), make_enemy(hp=300)])
    st.player.ftd.stage = ["neuvillette"]
    T.on_hp_loss(st, 7)                         # the enemies' turn
    FS.drain(st, 3)
    FS.drain(st, 2)
    hp = [e.hp for e in st.enemies]
    T.end_of_turn(st)                           # he acts; the window resets
    # 12, plus his own line's Hydro bonus of 2.
    assert [e.hp for e in st.enemies] == [h - 14 for h in hp]
    assert st.player.ftd.hp_lost_window == 0
