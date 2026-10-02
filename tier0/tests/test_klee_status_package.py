"""THE KLEE STATUS PACKAGE (2026-10-01): the sim half.

Paper `review/active/klee-status-package-2026-10-01.md`, ruled: "1) I think
a) is fine - we can keep tho the game's conventions 2) and 3) agreed on your
defaults". Eight pool cards in, eight out, and Albedo's Klee stand-in swapped
for Dust of Purification. The C# twin is
`KleeTests/Prototype/KleeStatusPackageTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).

"Status" is a card of Status TYPE or Status RARITY, so Confiscated (a 1-cost
Skill at Status rarity) counts; curses do not.
"""

from __future__ import annotations

import collections

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, companion_standins, klee_overhaul, statuses
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy
from tier0.tests.test_klee_r276_expansion import (  # noqa: F401
    filler, klee_state, load, overhaul, play, sizes)

CUT = ("proto_ko_pocket_fireworks", "proto_ko_rapid_fire",
       "proto_ko_flame_dance", "proto_ko_dodoco_cover",
       "proto_ko_careful_now", "proto_ko_split_charge", "proto_ko_fish_fry",
       "proto_ko_friendship_bracelet")
ALBEDO = "proto_mc_albedo_dust_of_purification"


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _confiscated():
    return loader.get_card(klee_overhaul.CONFISCATED_ID)


def _first(card, op):
    return next(fx for fx in card.effects if fx.get("op") == op)


# --- the pool -----------------------------------------------------------------

def test_the_package_cuts_eight_and_adds_eight(overhaul):
    ids = C.KLEE_OVERHAUL_POOL_IDS
    assert len(ids) == 78
    assert ids[-8:] == C.KLEE_STATUS_PACKAGE_IDS
    rows = {c.id for c in loader.prototype_cards()}
    for cid in CUT:
        assert cid not in ids
        assert cid not in rows
    rarity = collections.Counter(load(cid).rarity for cid in ids)
    assert rarity == {"common": 24, "uncommon": 33, "rare": 21}
    shapes = {cid: (load(cid).type, load(cid).cost, load(cid).rarity)
              for cid in C.KLEE_STATUS_PACKAGE_IDS}
    assert shapes == {
        "proto_ko_forbidden_fun": ("attack", 0, "common"),
        "proto_ko_it_wasnt_me": ("skill", 0, "common"),
        "proto_ko_lisas_treats": ("skill", 0, "uncommon"),
        "proto_ko_red_knight": ("attack", 2, "rare"),
        "proto_ko_finders_keepers": ("power", 1, "uncommon"),
        "proto_ko_klee_can_explain": ("skill", 1, "uncommon"),
        "proto_ko_damage_report": ("power", 1, "rare"),
        "proto_ko_solitary_confinement": ("power", 1, "rare"),
    }


def test_the_papers_numbers_and_upgrades(overhaul):
    assert _first(load("proto_ko_forbidden_fun"), "damage")["amount"] == 10
    assert _first(_up("proto_ko_forbidden_fun"), "damage")["amount"] == 14
    assert _first(load("proto_ko_it_wasnt_me"), "block")["amount"] == 6
    assert _first(_up("proto_ko_it_wasnt_me"), "block")["amount"] == 9
    assert _first(load("proto_ko_lisas_treats"), "energy")["amount"] == 2
    assert _first(_up("proto_ko_lisas_treats"), "energy")["amount"] == 3
    assert _first(load("proto_ko_red_knight"), "damage")["amount"] == 22
    assert _first(_up("proto_ko_red_knight"), "damage")["amount"] == 28
    assert _first(load("proto_ko_finders_keepers"), "apply_power")["amount"] == 5
    assert _first(_up("proto_ko_finders_keepers"), "apply_power")["amount"] == 7
    assert _first(load("proto_ko_klee_can_explain"), "block")["amount"] == 6
    assert _first(_up("proto_ko_klee_can_explain"), "block")["amount"] == 8
    assert _first(load("proto_ko_damage_report"), "apply_power")["amount"] == 5
    assert _first(_up("proto_ko_damage_report"), "apply_power")["amount"] == 7
    assert not load("proto_ko_solitary_confinement").innate
    assert _up("proto_ko_solitary_confinement").innate
    grow = "exhaust_statuses_grow_largest"
    assert _first(load(ALBEDO), grow)["amount"] == 6
    assert _first(_up(ALBEDO), grow)["amount"] == 8


def test_the_loaders_pay_the_tier_the_paper_names(overhaul):
    """Light tax: one Dazed. Heavy tax: two Confiscated."""
    for cid, token, n in (("proto_ko_forbidden_fun", "status_dazed", 1),
                          ("proto_ko_it_wasnt_me", "status_dazed", 1),
                          ("proto_ko_lisas_treats", "confiscated", 2),
                          ("proto_ko_red_knight", "confiscated", 2)):
        fx = _first(load(cid), "add_card")
        assert (fx["card"], fx["zone"], fx["amount"]) == (token, "draw", n)
        enemy = make_enemy(hp=400)
        st = klee_state([enemy])
        st.player.draw_pile = filler(3)
        play(st, load(cid), aim=enemy)
        made = [c for c in st.player.draw_pile if klee_overhaul.is_status(c)]
        assert len(made) == n


# --- what counts as a status ---------------------------------------------------

def test_status_is_status_type_or_status_rarity():
    assert klee_overhaul.is_status(statuses.make_status("dazed"))
    assert klee_overhaul.is_status(_confiscated())
    assert klee_overhaul.is_confiscated(_confiscated())
    curse = Card(id="regret", name="Regret", cost=-1, type="curse",
                 rarity="curse", effects=[])
    assert not klee_overhaul.is_status(curse)
    assert not klee_overhaul.is_status(load("proto_ko_pop"))


# --- the payoffs ---------------------------------------------------------------

def test_finders_keepers_places_a_bomb_per_confiscated_played(overhaul):
    enemy = make_enemy(hp=200)
    st = klee_state([enemy])
    st.player.powers[klee_overhaul.FINDERS_KEEPERS] = 5
    klee_overhaul.note_card_played(st, _confiscated())
    klee_overhaul.note_card_played(st, load("proto_ko_pop"))
    assert sizes(enemy) == [5]


def test_solitary_confinement_frees_confiscated_only(overhaul):
    st = klee_state()
    assert combat.card_cost(st, _confiscated()) == 1
    st.player.powers[klee_overhaul.SOLITARY_CONFINEMENT] = 1
    assert combat.card_cost(st, _confiscated()) == 0
    assert combat.card_cost(st, load("proto_ko_chain_fuse")) == 1


def test_damage_report_hits_all_per_status_drawn(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a, b])
    st.player.powers[klee_overhaul.DAMAGE_REPORT] = 5
    st.player.hand = []
    st.player.draw_pile = [statuses.make_status("dazed"), _confiscated(),
                           load("proto_ko_pop")]
    st.draw(3)
    assert (200 - a.hp, 200 - b.hp) == (10, 10)


def test_klee_can_explain_turns_every_status_into_pop(overhaul):
    enemy = make_enemy(hp=200)
    st = klee_state([enemy])
    st.player.hand = [statuses.make_status("dazed"), _confiscated(),
                      load("proto_ko_chain_fuse")]
    play(st, load("proto_ko_klee_can_explain"), aim=enemy)
    assert [c.id for c in st.player.hand] == [
        "proto_ko_pop", "proto_ko_pop", "proto_ko_chain_fuse"]
    assert st.player.block == 6


def test_dust_of_purification_exhausts_statuses_into_the_largest_bomb(
        overhaul):
    enemy = make_enemy(hp=200)
    st = klee_state([enemy])
    klee_overhaul.place(st, enemy, 5)
    st.player.hand = [statuses.make_status("dazed"), _confiscated(),
                      load("proto_ko_chain_fuse")]
    play(st, load(ALBEDO))
    assert [c.id for c in st.player.hand] == ["proto_ko_chain_fuse"]
    assert len(st.player.exhaust_pile) == 2
    assert sizes(enemy) == [17]


def test_dust_of_purification_is_albedos_klee_stand_in(overhaul):
    assert ALBEDO in C.COMPANION_STANDIN_IDS
    assert "proto_mc_albedo_tectonic_tide" not in C.COMPANION_STANDIN_IDS
    row = load(ALBEDO)
    assert (row.type, row.cost, row.rarity) == ("skill", 1, "rare")
    assert ALBEDO in companion_standins.standin_ids()
