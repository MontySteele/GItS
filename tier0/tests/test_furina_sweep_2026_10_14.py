"""FURINA, THE SWEEP in the one-seat sim.

`review/active/furina-sweep-2026-10-14.md` sec.2 and sec.3: fifteen cut,
fifteen new, the pool still 78 at 23 / 35 / 20. The seven new `furina`
kinds (`furina_stage._generic_kind`), the `furina_upgraded` key, Pneuma and
Ousia (`furina_stage.pneuma_and_ousia`) and Intermission's RetainHandPower
at the flush (`refpowers.retain_at_flush`). The C# twin is
`klee-mod/KleeTests/Prototype/FurinaSweepTests.cs`.
"""

from __future__ import annotations

import copy
from collections import Counter

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS
from tier0.tests.conftest import make_enemy, make_state

CUT = ("soloists_solicitation", "spirited_aria", "standing_ovation_all",
       "hydro_lance", "overdraft", "packed_house", "interval_bell",
       "soothing_waters", "balance_the_books", "salons_encore", "ousia_surge",
       "high_stakes", "pneuma_tides", "the_deluge", "hymn_of_renewal")
NEW = {"rain_of_tears": "common", "rehearsal": "common",
       "silence_in_the_court": "common", "pirouette": "common",
       "spotlight_grab": "common", "costume_fitting": "common",
       "quick_change": "uncommon", "read_the_script": "uncommon",
       "practiced_grace": "uncommon", "mise_en_scene": "uncommon",
       "intermission": "uncommon", "second_act": "uncommon",
       "solo_recital": "uncommon", "pneuma_and_ousia": "rare",
       "stand_in": "rare"}


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(hp=78, enemies=None):
    st = make_state(enemies=enemies or [make_enemy(hp=300)], hp=78)
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


def _filler(n, cid="strike"):
    return [_card(cid) for _ in range(n)]


# ---- the pool -------------------------------------------------------------

def test_the_pool_is_78_at_23_35_20_with_the_fifteen_swapped():
    pool = [loader.get_card(cid) for cid in FS.POOL_IDS]
    assert len(pool) == 78 == len(set(FS.POOL_IDS))
    assert Counter(c.rarity for c in pool) == {
        "common": 23, "uncommon": 35, "rare": 20}
    ids = {c.id for c in loader.prototype_cards()}
    for cut in CUT:
        assert "proto_fs_" + cut not in ids, cut
    for new, rarity in NEW.items():
        assert "proto_fs_" + new in FS.POOL_IDS, new
        assert loader.get_card("proto_fs_" + new).rarity == rarity, new
    assert sum(c.type == "power" for c in pool) == 17


# ---- the plain rows ---------------------------------------------------------

def test_rain_of_tears_blocks_and_puts_hydro_on_every_enemy():
    st = _furina(enemies=[make_enemy(hp=50), make_enemy(hp=50)])
    _play(st, _card("proto_fs_rain_of_tears"))
    assert st.player.block == 5
    assert [e.aura for e in st.enemies] == ["hydro", "hydro"]
    assert _card("proto_fs_rain_of_tears+").effects[0]["amount"] == 8


def test_rehearsal_retains_and_blocks_7_then_10():
    assert _card("proto_fs_rehearsal").retain
    assert _card("proto_fs_rehearsal").effects[0]["amount"] == 7
    assert _card("proto_fs_rehearsal+").effects[0]["amount"] == 10


def test_silence_in_the_court_is_a_this_turn_loss_on_all_and_exhausts():
    card = _card("proto_fs_silence_in_the_court")
    assert card.exhaust and card.rarity == "common"
    fx = card.effects[0]
    assert (fx["op"], fx["amount"], fx["target"], fx["this_turn"]) == (
        "lose_strength", 6, "all_enemies", True)
    assert _card("proto_fs_silence_in_the_court+").effects[0]["amount"] == 8


def test_pirouette_hits_three_times_and_solo_recital_x_times():
    st = _furina()
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_pirouette"))
    assert hp - st.enemies[0].hp == 12
    st = _furina()
    st.player.energy = 3
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_solo_recital"))
    assert hp - st.enemies[0].hp == 21 and st.player.energy == 0


def test_spotlight_grab_puts_a_discarded_card_on_top_of_the_draw_pile():
    st = _furina()
    st.player.discard_pile = [_card("proto_fs_pirouette")]
    st.player.draw_pile = _filler(3)
    _play(st, _card("proto_fs_spotlight_grab"))
    assert st.player.draw_pile[0].id == "proto_fs_pirouette"


def test_practiced_grace_gives_dexterity_2_then_3():
    st = _furina()
    _play(st, _card("proto_fs_practiced_grace"))
    assert st.player.powers.get("dexterity") == 2
    st = _furina()
    _play(st, _card("proto_fs_practiced_grace+"))
    assert st.player.powers.get("dexterity") == 3


# ---- the seven kinds ------------------------------------------------------

def test_costume_fitting_upgrades_one_card_and_all_upgraded():
    st = _furina()
    st.player.hand = [_card("proto_fs_pirouette"), _card("proto_fs_rehearsal")]
    _play(st, _card("proto_fs_costume_fitting"))
    assert st.player.block == 5
    assert sum(c.id.endswith("+") for c in st.player.hand) == 1
    st = _furina()
    st.player.hand = [_card("proto_fs_pirouette"), _card("proto_fs_rehearsal")]
    _play(st, _card("proto_fs_costume_fitting+"))
    assert all(c.id.endswith("+") for c in st.player.hand)


def test_quick_change_discards_the_hand_and_draws_that_many_plus_1_upgraded():
    st = _furina()
    st.player.hand = _filler(3, "defend")
    st.player.draw_pile = _filler(6)
    _play(st, _card("proto_fs_quick_change"))
    assert [c.id for c in st.player.hand] == ["strike"] * 3
    assert sum(c.id == "defend" for c in st.player.discard_pile) == 3
    st = _furina()
    st.player.hand = _filler(3, "defend")
    st.player.draw_pile = _filler(6)
    _play(st, _card("proto_fs_quick_change+"))
    assert len(st.player.hand) == 4


def test_read_the_script_takes_one_of_four_and_discards_three():
    st = _furina()
    st.player.draw_pile = _filler(3, "defend") + [_card("proto_fs_pirouette")] \
        + _filler(2)
    _play(st, _card("proto_fs_read_the_script"))
    assert [c.id for c in st.player.hand] == ["proto_fs_pirouette"]
    assert len(st.player.draw_pile) == 2
    assert sum(c.id == "defend" for c in st.player.discard_pile) == 3
    assert _card("proto_fs_read_the_script+").cost == 0


def test_mise_en_scene_frees_the_costliest_card_and_draws_1():
    st = _furina()
    big = _card("proto_fs_intermission")
    st.player.hand = [_card("proto_fs_pirouette"), big]
    st.player.draw_pile = _filler(2)
    _play(st, _card("proto_fs_mise_en_scene"))
    assert big.free_this_turn
    assert len(st.player.hand) == 3


def test_intermission_retains_the_hand_once():
    st = _furina()
    st.player.hand = _filler(2, "defend")
    _play(st, _card("proto_fs_intermission"))
    assert st.player.block == 11
    from tier0.engine import refpowers
    kept = refpowers.retain_at_flush(st, _filler(3))
    assert len(kept) == 3                         # this turn's flush keeps all
    assert refpowers.retain_at_flush(st, _filler(3)) == []   # then it is spent


def test_second_act_returns_a_discarded_card_and_exhausts():
    st = _furina()
    st.player.discard_pile = [_card("proto_fs_pirouette")]
    card = _card("proto_fs_second_act")
    assert card.exhaust
    _play(st, card)
    assert st.player.block == 4
    assert [c.id for c in st.player.hand] == ["proto_fs_pirouette"]


def test_stand_in_copies_a_card_and_the_copy_exhausts():
    st = _furina()
    st.player.hand = [_card("proto_fs_pirouette")]
    _play(st, _card("proto_fs_stand_in"))
    assert [c.id for c in st.player.hand] == ["proto_fs_pirouette"] * 2
    assert [c.exhaust for c in st.player.hand] == [False, True]
    assert _card("proto_fs_stand_in+").cost == 0


def test_the_kinds_work_for_anyone():
    st = make_state(enemies=[make_enemy(hp=50)])
    st.in_player_turn = True
    st.player.energy = 9
    st.player.discard_pile = [_card("strike")]
    _play(st, _card("proto_fs_second_act"))
    assert [c.id for c in st.player.hand] == ["strike"]


# ---- Pneuma and Ousia ------------------------------------------------------

def test_pneuma_and_ousia_blocks_on_attacks_and_hits_on_skills():
    st = _furina()
    _play(st, _card("proto_fs_pneuma_and_ousia"))
    assert st.player.powers[FS.PNEUMA_AND_OUSIA] == 2
    block = st.player.block
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_pirouette"))
    assert st.player.block == block + 2
    assert hp - st.enemies[0].hp == 12               # no hit on an Attack
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_rehearsal"))
    assert hp - st.enemies[0].hp == 2
    st = _furina()
    _play(st, _card("proto_fs_pneuma_and_ousia+"))
    assert st.player.powers[FS.PNEUMA_AND_OUSIA] == 3


def test_stand_in_never_copies_a_stand_in():
    """Design call (2026-10-14): two Stand-In+ copied each other forever at
    0 Energy; with Pneuma and Ousia that is unlimited damage."""
    st = _furina()
    st.player.hand = [_card("proto_fs_stand_in+")]
    _play(st, _card("proto_fs_stand_in+"))
    assert [c.id for c in st.player.hand] == ["proto_fs_stand_in+"]
