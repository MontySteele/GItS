"""THE POOL-75 ROUND'S RULINGS, BUILT, in the sim (2026-10-09).

`review/records/furina-pool75-round-2026-10-09.md`, "Picks (ruled
2026-10-09)": the Drain line rule (since amended to entry HP minus 1/4 of
Max HP, the same day; Drain past it, the two-part
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

def test_the_arm_runs_the_entry_minus_quarter_max_line():
    st = _furina()
    assert st.player.ftd.line == T.SHIPPED_LINE
    assert (T.LINE_MAX_HP_DIVISOR, T.DRAIN_FLOOR) == (4, 1)
    assert st.player.ftd.entry_max_hp == 78
    assert T.line_hp(st.player) == 59                    # 78 - 19


def test_the_line_is_hp_less_the_drain_buffer_left():
    """The Drain buffer (2026-10-11; it replaced 2026-10-09's entry-HP
    line): 1/4 of her Max HP rounded down, counted in HP drained. The line
    as shown is her HP less the buffer left."""
    assert T.line_hp(_furina(hp=50, max_hp=80).player) == 30   # 20 of room
    assert T.line_hp(_furina(hp=80, max_hp=80).player) == 60
    st = _furina(hp=85, max_hp=85)
    assert st.player.hp - T.line_hp(st.player) == 21           # 21.25 down
    assert T.shipped_buffer(85) == 21
    assert T.shipped_buffer(80, lyney=True) == 30
    assert T.shipped_line(60, 21) == 39
    assert T.shipped_line(10, 20) == 0                         # never below 0
    lyney = _furina(hp=50, max_hp=80)
    lyney.player.ftd.stage = ["lyney"]
    assert T.line_hp(lyney.player) == 20


def test_the_line_snapshots_max_hp_at_combat_start():
    """Max HP is read when the combat opens: a Max HP change mid-fight
    does not move the line."""
    st = _furina(hp=50, max_hp=80)
    st.player.max_hp = 100
    assert T.line_hp(st.player) == 30
    st.player.max_hp = 60
    assert T.line_hp(st.player) == 30


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
    for cid, base, n in (("proto_fs_hydro_lance", 14, 4),
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
    _play(st, _card("proto_fs_hymn_of_many_waters"))        # 6 + (3 - 1)
    assert st.player.block == 8
    st = _furina()
    _play(st, _card("proto_fs_hymn_of_many_waters+"))       # 8 + 4
    assert st.player.block == 12      # the 2026-10-11 trim (was 15)


def test_soothing_waters_keeps_no_leftover_payout():
    """Ruled 2026-10-09: a 0-cost draw-1 card paying out on an empty Repay
    looped forever, so Soothing Waters is "Repay 2. Draw 1 card." [3]."""
    assert "floor" not in _card("proto_fs_soothing_waters").effects[0]
    assert _card("proto_fs_soothing_waters+").effects[0]["amount"] == 3
    st = _furina()
    _play(st, _card("proto_fs_soothing_waters"))
    assert not st.player.powers.get("next_attack_up")
    assert st.player.block == 0


def test_fountain_has_no_floor_and_pneuma_tides_pays_vigor():
    st = _furina()
    effects.resolve_card(st, _card("proto_fs_fountain_of_lucine"))
    assert st.player.block == 8                             # the card's own
    st.player.block = 0
    FS.drain(st, 1)
    T.turn_start(st)
    assert st.player.block == 0                             # no floor (2026-10-13)
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
    assert st.player.block == 3                # Repay 3, nothing drained
    st = _furina()
    st.player.ftd.stage = ["sigewinne"]
    FS.drain(st, 1)
    T.act(st, "sigewinne")
    # Her line's Block of the 1 returned, then the floor's 2 (Repay 3).
    assert st.player.block == 3


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
    # Common again, Spend half (2026-10-11, Furina round 3 record, pick 1).
    assert _card("proto_fs_standing_ovation_all").rarity == "common"
    crab = _card("proto_fs_mademoiselle_crabaletta")
    assert crab.effects[1]["amount"] == 20
    solo = _card("proto_fs_soloists_solicitation")
    assert solo.effects[1]["amount"] == 6
    assert _card("proto_fs_soloists_solicitation+").effects[1]["amount"] == 9
    assert _card("proto_fs_mademoiselle_crabaletta+").effects[1]["amount"] == 26
    gaze = _card("proto_fs_commanding_gaze").effects[0]["modes"][0]
    assert gaze["effects"][0]["amount"] == 2
    assert _card("proto_fs_guest_star_neuvillette").cost == 1


def test_bravuras_upgrade_hits_9_for_every_3_spent():
    # The diversity pass (2026-10-11): "Deal 7 Hydro damage for every 3
    # spent." [9] (was 6 plus 2 a point [10]).
    st = _furina()
    st.player.ftd.fanfare = 5
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_bravura+"))
    assert st.enemies[0].hp == hp - 9


def test_freminets_act_gives_block():
    # The Spend paper (ruled 2026-10-10; 4 [7] since the guest package,
    # 2026-10-13): "Gain 4 Block. Spend a quarter of
    # your Fanfare (rounded down): gain that much more Block." [6]. No hit any
    # more.
    st = _furina()
    st.player.ftd.stage = ["freminet"]
    hp = [e.hp for e in st.enemies]
    T.act(st, "freminet")
    assert st.player.block == 4
    assert [e.hp for e in st.enemies] == hp
    st.player.ftd.stage_up = {"freminet"}
    st.player.block = 0
    T.act(st, "freminet")
    assert st.player.block == 7


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


# ---- the Drain buffer (2026-10-11) ---------------------------------------------

def test_the_users_worked_example_a_hit_never_uses_the_buffer():
    """[USER], 2026-10-11: "There should be a buffer for drain equal to 1/4
    my max HP which should be restore-able, but getting hurt should not
    disqualify it. Say my max HP is 80 and my current HP is 50. Then the
    drain line is 20 below, aka 30. If I take 15 normal damage and Drain 15,
    I expect to be at 20 hp with my Drain line at 15 and be able to Repay to
    35." """
    st = _furina(hp=50, max_hp=80)
    p, f = st.player, st.player.ftd
    assert T.line_hp(p) == 30
    p.hp -= 15                                  # 15 normal damage
    assert T.line_hp(p) == 15                   # the line moves with her HP
    assert T.drain(st, 15)
    assert p.hp == 20
    assert T.line_hp(p) == 15
    assert (f.drained_above, f.drained_past) == (15, 0)
    assert T.repay(st, 15) == 15
    assert p.hp == 35 and f.drained == 0
    assert T.buffer_left(p) == 20               # restore-able


def test_a_drain_past_the_buffer_is_past_the_line():
    st = _furina(hp=50, max_hp=80)              # a buffer of 20
    p, f = st.player, st.player.ftd
    p.hp -= 15
    assert T.drain(st, 25)
    assert p.hp == 10
    assert (f.drained_above, f.drained_past) == (20, 5)
    assert T.line_hp(p) == 10                   # no buffer left
    T.close_ledger(st)
    assert p.hp == 30                           # the 5 past it stay lost
    assert f.ledger["lost_past_line"] == 5


def test_lyney_adds_ten_to_the_buffer():
    st = _furina(hp=50, max_hp=80)
    p, f = st.player, st.player.ftd
    f.stage = ["lyney"]
    assert T.buffer_left(p) == 30 and T.line_hp(p) == 20
    assert T.drain(st, 30)
    assert (f.drained_above, f.drained_past) == (30, 0)
    assert T.guest_drain_room(st, T.LYNEY_ACT_DRAIN) == 0
