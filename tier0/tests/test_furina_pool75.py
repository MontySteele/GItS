"""FURINA, THE POOL TO 75 in the one-seat sim.

`review/active/furina-pool-growth-2026-10-09.md`, ruled 2026-10-09: sec.3's
guest rule and sec.5's 41 cards, through the sheet's ops
(`tier0/engine/furina_stage.py` on `tier0/engine/furina_tide.py`). One pin
per rule. The C# twins are
`klee-mod/KleeTests/Prototype/FurinaGuestRuleTests.cs`.
"""

from __future__ import annotations

import copy

import pytest

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


# ---- sec.3: the guest rule ---------------------------------------------------

def test_a_guest_star_exhausts_and_has_no_effect_on_summon():
    st = _furina()
    card = _card("proto_fs_guest_star_clorinde")
    hp = st.enemies[0].hp
    _play(st, card)
    assert FS.stage(st.player) == ["clorinde"]
    assert any(c is card for c in st.player.exhaust_pile)
    assert st.enemies[0].hp == hp
    assert st.player.ftd.stage_cards["clorinde"] == [card]


def test_an_evicted_guests_card_returns_to_the_discard_pile():
    st = _furina()
    first = _card("proto_fs_guest_star_wriothesley")
    _play(st, first)
    for cid in ("lynette", "clorinde", "charlotte"):
        _play(st, _card(f"proto_fs_guest_star_{cid}"))
    assert FS.stage(st.player) == ["lynette", "clorinde", "charlotte"]
    assert any(c is first for c in st.player.discard_pile)
    assert not any(c is first for c in st.player.exhaust_pile)
    assert st.player.ftd.ledger["guest_acts"]["wriothesley"] == 0


def test_a_duplicate_moves_its_guest_to_the_newest_seat_with_no_act():
    st = _furina()
    _play(st, _card("proto_fs_guest_star_lynette"))
    _play(st, _card("proto_fs_guest_star_chevreuse"))
    dup = _card("proto_fs_guest_star_lynette+")
    _play(st, dup)
    f = st.player.ftd
    assert FS.stage(st.player) == ["chevreuse", "lynette"]
    assert "lynette" in f.stage_up
    assert len(f.stage_cards["lynette"]) == 2
    assert sum(f.ledger["guest_acts"].values()) == 0


def test_final_bow_acts_twice_then_its_guest_leaves_and_its_card_returns():
    st = _furina()
    clorinde = _card("proto_fs_guest_star_clorinde")
    _play(st, clorinde)
    _play(st, _card("proto_fs_final_bow"))
    f = st.player.ftd
    assert f.ledger["guest_acts"]["clorinde"] == 2
    assert FS.stage(st.player) == []
    assert any(c is clorinde for c in st.player.discard_pile)
    st2 = _furina()
    _play(st2, _card("proto_fs_guest_star_clorinde"))
    _play(st2, _card("proto_fs_final_bow+"))
    assert st2.player.ftd.ledger["guest_acts"]["clorinde"] == 3


def test_the_end_of_turn_acts_oldest_first_then_showstopper_then_the_singer():
    st = _furina()
    f = st.player.ftd
    f.stage = ["wriothesley", "clorinde"]
    st.player.powers[FS.SHOWSTOPPER] = 1
    FS.drain(st, 6)                         # 6 Fanfare, 6 drained
    events = len(st.log)
    T.end_of_turn(st)
    acts = [e["member"] for e in st.log[events:]
            if e.get("event") == "ftd_act"]
    assert acts == ["wriothesley", "clorinde", "wriothesley", "clorinde"]
    assert f.ledger["showstopper_rounds"] == 1
    assert f.fanfare == 6 - 5 + 1           # the Singer's Repay 1 after
    # No guest, no Spend.
    empty = _furina()
    empty.player.powers[FS.SHOWSTOPPER] = 1
    empty.player.ftd.fanfare = 9
    T.end_of_turn(empty)
    assert empty.player.ftd.fanfare == 9


def test_a_line_is_logged_apart_from_an_act():
    st = _furina()
    st.player.ftd.stage = ["wriothesley"]
    FS.drain(st, 3)
    lines = [e for e in st.log if e.get("event") == "ftd_line"]
    assert [e["member"] for e in lines] == ["wriothesley"]
    assert not [e for e in st.log if e.get("event") == "ftd_act"]


def test_upgraded_guests_raise_their_act_or_line():
    assert T.act_amount("clorinde", True) == 9
    assert T.act_amount("charlotte", True) == 4
    st = _furina()
    _play(st, _card("proto_fs_guest_star_navia+"))
    assert T.navia_discount(st.player.ftd) == 3


# ---- the four new guests ------------------------------------------------------

def test_freminet_blocks_each_drain():
    st = _furina()
    st.player.ftd.stage = ["freminet"]
    FS.drain(st, 4)
    assert st.player.block == 4


def test_navias_first_spend_costs_two_less_and_a_spend_all_keeps_two():
    st = _furina()
    f = st.player.ftd
    f.stage = ["navia"]
    f.fanfare = 6
    assert FS.can_pay(st.player, 8)
    assert FS.spend(st, 6) == 6 and f.fanfare == 2
    assert FS.spend(st, 2) == 2 and f.fanfare == 0
    st2 = _furina()
    st2.player.ftd.stage = ["navia"]
    st2.player.ftd.fanfare = 9
    assert FS.spend_all(st2) == 9
    assert st2.player.ftd.fanfare == 2


def test_neuvillette_adds_to_hydro_and_acts_for_the_hp_drained():
    st = _furina()
    st.player.ftd.stage = ["neuvillette"]
    assert FS.hydro_bonus(st) == 2
    hp = st.enemies[0].hp
    effects.deal_damage_to_enemy(st, st.enemies[0], 5, element="hydro")
    assert hp - st.enemies[0].hp == 7
    FS.drain(st, 4)
    hp = st.enemies[0].hp
    T.act(st, "neuvillette")
    assert hp - st.enemies[0].hp == 4 + 2


def test_escoffier_repays_one_whenever_a_guest_acts():
    st = _furina()
    st.player.ftd.stage = ["charlotte", "escoffier"]
    FS.drain(st, 10)
    T.act_all(st)
    assert st.player.ftd.ledger["lines"]["escoffier"] == 2
    assert st.player.ftd.drained == 10 - 2 - 1 - 1


def test_ensemble_cast_seats_four():
    st = _furina()
    st.player.powers[FS.ENSEMBLE_CAST] = 1
    for who in ("charlotte", "lynette", "clorinde", "sigewinne"):
        FS.guest_star(st, who)
    assert len(FS.stage(st.player)) == 4
    assert FS.guest_star(st, "lyney") == "evict"


# ---- sec.5's new cards --------------------------------------------------------

def test_encore_spends_and_its_oldest_guest_acts():
    st = _furina()
    st.player.ftd.stage = ["wriothesley", "clorinde"]
    st.player.ftd.fanfare = 4
    _play(st, _card("proto_fs_encore"))
    assert st.player.ftd.fanfare == 0
    assert st.player.ftd.ledger["guest_acts"]["wriothesley"] == 1
    assert st.player.ftd.ledger["guest_acts"]["clorinde"] == 0


def test_tutti_and_bring_the_house_down_act_each_guest():
    st = _furina()
    st.player.ftd.stage = ["wriothesley", "clorinde"]
    _play(st, _card("proto_fs_tutti"))
    assert sum(st.player.ftd.ledger["guest_acts"].values()) == 2
    st.player.ftd.fanfare = 10
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_bring_the_house_down"))
    assert sum(st.player.ftd.ledger["guest_acts"].values()) == 4
    assert hp - st.enemies[0].hp >= 10


def test_casting_call_puts_a_guest_star_into_the_hand():
    st = _furina()
    guest = _card("proto_fs_guest_star_lyney")
    st.player.draw_pile = [_card("proto_fs_bubble_aria"), guest]
    _play(st, _card("proto_fs_casting_call"))
    assert any(c is guest for c in st.player.hand)


def test_grand_entrance_repays_on_a_guest_star():
    st = _furina()
    st.player.powers[FS.GRAND_ENTRANCE] = 4
    FS.drain(st, 6)
    _play(st, _card("proto_fs_guest_star_charlotte"))
    assert st.player.ftd.drained == 2


def test_star_turn_costs_one_less_per_six_fanfare():
    st = _furina()
    card = _card("proto_fs_star_turn")
    st.player.ftd.fanfare = 6
    assert combat.card_cost(st, card) == 1
    st.player.ftd.fanfare = 12
    assert combat.card_cost(st, card) == 0


def test_crescendo_and_standing_room_only():
    st = _furina()
    st.player.powers[FS.CRESCENDO] = 1
    st.player.powers[FS.STANDING_ROOM_ONLY] = 1
    st.player.draw_pile = [_card("proto_fs_bubble_aria") for _ in range(3)]
    st.player.ftd.fanfare = 6
    FS.spend(st, 2)
    FS.spend(st, 2)
    assert len(st.player.hand) == 1
    FS.spend_all(st)
    assert st.player.powers.get("strength", 0) == 1


def test_hymn_of_renewal_counts_hp_actually_repaid():
    st = _furina()
    st.player.powers[FS.HYMN_OF_RENEWAL] = 1
    FS.drain(st, 3)
    FS.repay(st, 6)                          # returns 3
    assert st.player.powers.get("strength", 0) == 0
    FS.drain(st, 5)
    FS.repay(st, 4)
    assert st.player.powers.get("strength", 0) == 1


def test_turn_start_regina_gentle_current_pneuma_tides_and_prima_donna():
    st = _furina()
    p = st.player
    p.powers[FS.REGINA_OF_ALL_WATERS] = 1
    p.powers[FS.PNEUMA_TIDES] = 2
    p.powers[FS.PRIMA_DONNA] = 1
    p.ftd.repay_next = 4
    p.ftd.fanfare = 10
    p.energy = 3
    FS.drain(st, 6)
    T.turn_start(st)
    assert p.powers.get("strength", 0) == 1          # Regina drained 3
    assert p.ftd.drained == 6 + 3 - 4 - 2
    assert p.energy == 4


def test_the_drain_cards_and_their_counts():
    st = _furina()
    _play(st, _card("proto_fs_overdraft"))
    # The loop ruling (2026-10-09): its Energy comes next turn.
    assert st.player.hp == 74 and st.player.energy == 9
    assert st.player.ftd.energy_next == 1
    _play(st, _card("proto_fs_overdraft+"))
    assert st.player.hp == 71
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_undercurrent"))
    assert hp - st.enemies[0].hp == 5 + 3      # three Drains this combat
    _play(st, _card("proto_fs_all_in"))
    assert st.player.hp == 61


def test_against_the_tide_and_high_stakes_read_the_line():
    st = _furina()                             # entered at 78: line 39
    st.player.hp = 43                          # within 5 of it
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_against_the_tide"))
    assert hp - st.enemies[0].hp == 14
    st.player.powers[FS.HIGH_STAKES] = 4
    assert FS.high_stakes_bonus(st) == 4
    far = _furina()
    far.player.powers[FS.HIGH_STAKES] = 4
    assert FS.high_stakes_bonus(far) == 0


def test_riptide_lunge_repays_on_a_kill():
    st = _furina(enemies=[make_enemy(hp=10)])
    _play(st, _card("proto_fs_riptide_lunge"))
    assert st.player.ftd.drained == 3 - 3      # drained 3, repaid on kill


def test_the_repay_cards_and_their_counts():
    st = _furina()
    FS.drain(st, 20)
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_balance_the_books"))
    assert hp - st.enemies[0].hp >= 10         # half of 20
    _play(st, _card("proto_fs_soothing_waters"))
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_rising_tide"))
    assert hp - st.enemies[0].hp == 6 + 3 * 2
    _play(st, _card("proto_fs_gentle_current"))
    assert st.player.ftd.repay_next == 4
    left = st.player.ftd.drained
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_grand_absolution"))
    assert st.player.ftd.drained == 0
    assert hp - st.enemies[0].hp == left


def test_sold_out_draws_now_and_gives_its_energy_next_turn():
    st = _furina()
    st.player.ftd.fanfare = 6
    st.player.draw_pile = [_card("proto_fs_bubble_aria") for _ in range(2)]
    _play(st, _card("proto_fs_sold_out"))
    assert st.player.energy == 8                 # paid 1, gained nothing now
    assert st.player.ftd.energy_next == 1
    assert len(st.player.hand) == 2
    assert T.energy_kept(st) == 1


def test_ebb_and_flow_nets_minus_two():
    st = _furina()
    _play(st, _card("proto_fs_ebb_and_flow"))
    assert st.player.hp == 76 and st.player.ftd.fanfare == 6


@pytest.mark.parametrize("cid", [c for c in FS.POOL_IDS[FS.POOL_IDS.index("proto_fs_casting_call"):]])
def test_every_new_row_loads_upgrades_and_never_throws_off_character(cid):
    assert loader.get_card(cid + "+") is not None
    st = make_state(enemies=[make_enemy(hp=300)])
    st.player.character_id = "klee"
    st.in_player_turn = True
    effects.resolve_card(st, loader.get_card(cid))
    assert st.player.hp == 80
