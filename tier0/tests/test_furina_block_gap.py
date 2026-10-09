"""FURINA, THE BLOCK GAP in the one-seat sim (ruled 2026-10-09).

`review/records/furina-drain-line-round-2026-10-09.md`, pick 2. [USER]: "Yeah,
agreed - let's plug the block gap now." Four cards, through the sheet's ops
(`tier0/engine/furina_stage.py` on `tier0/engine/furina_tide.py`) and the
research slice's own rows (`furina_tide.CARDS`, which the pilot drafts):

- Velvet Curtain (1, Common): Gain 7 Block. Gain 2 Fanfare. [10, 3]
- Private Box (1, Uncommon): Gain 5 Block, plus 3 for each guest on stage.
  [7, plus 4]
- The Masquerade (1, Uncommon, Power): Whenever you Drain, gain that much
  Block. [cost 0]
- The Show Must Go On (2, Rare): Gain Block equal to your Fanfare. [cost 1]

The C# twins are `klee-mod/KleeTests/Prototype/FurinaBlockGapTests.cs`.
"""

from __future__ import annotations

import copy
import random

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS, furina_tide as T
from tier0.engine.state import CombatState, Enemy
from tier0.tests.conftest import make_enemy, make_state


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(hp=78, max_hp=78):
    st = make_state(enemies=[make_enemy(hp=300)], hp=max_hp)
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


# ---- the sheet and the pool -------------------------------------------------

def test_the_four_rows_are_as_ruled():
    rows = {c.id: c for c in loader.prototype_cards()}
    want = {
        "proto_fs_velvet_curtain": (1, "skill", "common"),
        "proto_fs_private_box": (1, "skill", "uncommon"),
        "proto_fs_the_masquerade": (1, "power", "uncommon"),
        "proto_fs_the_show_must_go_on": (2, "skill", "rare"),
    }
    for cid, (cost, kind, rarity) in want.items():
        row = rows[cid]
        assert (row.cost, row.type, row.rarity) == (cost, kind, rarity), cid
        assert cid in FS.POOL_IDS, cid
    assert loader.get_card("proto_fs_the_masquerade+").cost == 0
    assert loader.get_card("proto_fs_the_show_must_go_on+").cost == 1


# ---- Velvet Curtain -----------------------------------------------------------

def test_velvet_curtain_gains_7_block_and_2_fanfare_as_gained_fanfare():
    st = _furina()
    f = st.player.ftd
    _play(st, _card("proto_fs_velvet_curtain"))
    assert st.player.block == 7
    assert f.fanfare == 2
    # A gain on the ledger, the path Universal Revelry's gain takes.
    assert f.gained_this_turn == 2
    assert f.ledger["gained"] == 2


def test_velvet_curtain_upgraded_gains_10_and_3():
    st = _furina()
    _play(st, _card("proto_fs_velvet_curtain+"))
    assert st.player.block == 10
    assert st.player.ftd.fanfare == 3


# ---- Private Box --------------------------------------------------------------

def test_private_box_with_no_guest_gains_5():
    st = _furina()
    _play(st, _card("proto_fs_private_box"))
    assert st.player.block == 5


def test_private_box_with_three_guests_gains_14():
    st = _furina()
    st.player.ftd.stage = ["charlotte", "lynette", "clorinde"]
    _play(st, _card("proto_fs_private_box"))
    assert st.player.block == 5 + 3 * 3


def test_private_box_upgraded_with_three_guests_gains_19():
    st = _furina()
    st.player.ftd.stage = ["charlotte", "lynette", "clorinde"]
    _play(st, _card("proto_fs_private_box+"))
    assert st.player.block == 7 + 4 * 3


def test_private_box_is_card_block_so_dexterity_applies():
    st = _furina()
    st.player.powers["dexterity"] = 2
    st.player.ftd.stage = ["charlotte"]
    _play(st, _card("proto_fs_private_box"))
    assert st.player.block == 5 + 3 + 2


# ---- The Masquerade -----------------------------------------------------------

def test_the_masquerade_pays_the_hp_drained_past_the_line_too():
    st = _furina()                          # line 78 - 78 // 4 = 59
    f = st.player.ftd
    _play(st, _card("proto_fs_the_masquerade"))
    assert st.player.powers[FS.THE_MASQUERADE] == 1
    assert st.player.block == 0
    st.player.hp = T.line_hp(st.player) + 1     # 1 HP of room above the line
    _play(st, _card("proto_fs_overdraft"))      # Drain 4: 3 of it past the line
    assert f.drained_past == 3
    assert st.player.block == 4


def test_the_masquerade_pays_a_guest_acts_drain_stopped_at_the_line():
    st = _furina()
    f = st.player.ftd
    st.player.powers[FS.THE_MASQUERADE] = 1
    f.stage = ["lyney"]
    st.player.hp = T.line_hp(st.player) + 1     # Lyney's Drain 2 has room 1
    assert T.guest_drain_room(st, T.LYNEY_ACT_DRAIN) == 1
    T.act(st, "lyney")
    assert f.drained == 1
    assert st.player.block == 1
    # At the line, no Drain and no Block.
    T.act(st, "lyney")
    assert st.player.block == 1


def test_the_masquerade_is_a_powers_block_so_dexterity_does_not_apply():
    st = _furina()
    st.player.powers[FS.THE_MASQUERADE] = 1
    st.player.powers["dexterity"] = 3
    FS.drain(st, 3)
    assert st.player.block == 3


def test_two_masquerades_pay_twice():
    st = _furina()
    st.player.powers[FS.THE_MASQUERADE] = 2
    FS.drain(st, 3)
    assert st.player.block == 6


# ---- The Show Must Go On ------------------------------------------------------

def test_the_show_must_go_on_gains_block_equal_to_fanfare_and_spends_none():
    st = _furina()
    f = st.player.ftd
    f.fanfare = 12
    _play(st, _card("proto_fs_the_show_must_go_on"))
    assert st.player.block == 12
    assert f.fanfare == 12
    assert f.ledger["spends"] == 0


def test_the_show_must_go_on_with_no_fanfare_gains_nothing():
    st = _furina()
    _play(st, _card("proto_fs_the_show_must_go_on"))
    assert st.player.block == 0


# ---- the research slice's rows (the pilot drafts these) -----------------------

def _slice(hp=78):
    p = T.build_player([])
    p.hp = hp
    st = CombatState(player=p,
                     enemies=[Enemy(hp=200, max_hp=200, name="paper",
                                    intents=[{"kind": "block", "amount": 0}])],
                     rng=random.Random(0))
    st.turn = 1
    st.current_attack_bonus = 0
    T.turn_open(st)
    p.energy = 9
    return st


def _slice_play(st, cid):
    card = T.make_card(cid)
    st.player.hand.append(card)
    combat.play_card(st, card)


def test_the_slice_mirrors_the_four():
    st = _slice()
    f = st.player.ftd
    _slice_play(st, "ftd_velvet_curtain")
    assert st.player.block == 7 and f.fanfare == 2
    st.player.block = 0
    f.stage = ["charlotte", "lynette", "clorinde"]
    _slice_play(st, "ftd_private_box")
    assert st.player.block == 14
    st.player.block = 0
    f.fanfare = 9
    _slice_play(st, "ftd_show_must_go_on")
    assert st.player.block == 9 and f.fanfare == 9
    st.player.block = 0
    _slice_play(st, "ftd_masquerade")
    assert f.powers["masquerade"] == 1
    T.drain(st, 4)
    assert st.player.block == 4


def test_the_pilot_values_each_of_the_four():
    from tier0.pilot import furina_tide_pilot as P
    st = _slice()
    st.player.ftd.fanfare = 8
    st.player.ftd.stage = ["charlotte"]
    for cid in ("ftd_velvet_curtain", "ftd_private_box",
                "ftd_show_must_go_on", "ftd_masquerade"):
        card = T.make_card(cid)
        assert P.value(st, card, [card], P.DEFAULT_DECIDER) > 0, cid
