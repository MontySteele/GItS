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
# Defence in the status pile (2026-10-01, the paper's sec.5): three more out.
DEFENCE_CUT = ("proto_ko_fish_flavored_bait", "proto_ko_big_bounce",
               "proto_ko_spinning_sparkler")
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
    assert ids[-11:] == C.KLEE_STATUS_PACKAGE_IDS
    rows = {c.id for c in loader.prototype_cards()}
    for cid in CUT + DEFENCE_CUT:
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
        "proto_ko_up_in_smoke": ("skill", 1, "common"),
        "proto_ko_behind_jeans_desk": ("skill", 1, "uncommon"),
        "proto_ko_kitchen_alchemy": ("skill", 1, "uncommon"),
    }
    assert load("proto_ko_kitchen_alchemy").exhaust


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


# --- defence in the status pile (2026-10-01, the paper's sec.5) ----------------
#
# [USER]: "Ok Klee - I'd say we go for option 1 and add the defensive utility
# into her status pile, which gives some incentive for players to engage with
# it. We can give a mix of weak, high-block cards (already present) and
# perhaps an alchemy-flavored Strength reduction?"

def test_the_defence_rows_numbers_and_upgrades(overhaul):
    smoke = _first(load("proto_ko_up_in_smoke"), "apply_power")
    assert (smoke["power"], smoke["amount"], smoke["target"]) == (
        "weak", 2, "all_enemies")
    assert _first(_up("proto_ko_up_in_smoke"), "apply_power")["amount"] == 3
    assert _first(load("proto_ko_behind_jeans_desk"), "block")["amount"] == 14
    assert _first(_up("proto_ko_behind_jeans_desk"), "block")["amount"] == 18
    loss = _first(load("proto_ko_kitchen_alchemy"), "lose_strength")
    assert (loss["amount"], loss["target"], loss["per_status"]) == (
        1, "all_enemies", 1)
    up = _first(_up("proto_ko_kitchen_alchemy"), "lose_strength")
    assert (up["amount"], up["per_status"]) == (2, 1)


def test_up_in_smoke_weakens_every_enemy_and_shuffles_a_dazed(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a, b])
    st.player.draw_pile = filler(3)
    play(st, load("proto_ko_up_in_smoke"))
    assert (a.powers.get("weak"), b.powers.get("weak")) == (2, 2)
    made = [c for c in st.player.draw_pile if klee_overhaul.is_status(c)]
    assert [c.type for c in made] == ["status"]
    assert not any(klee_overhaul.is_confiscated(c) for c in made)

    a2, b2 = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a2, b2])
    play(st, _up("proto_ko_up_in_smoke"))
    assert (a2.powers.get("weak"), b2.powers.get("weak")) == (3, 3)


def test_behind_jeans_desk_blocks_and_adds_a_confiscated(overhaul):
    enemy = make_enemy(hp=200)
    st = klee_state([enemy])
    st.player.draw_pile = filler(3)
    play(st, load("proto_ko_behind_jeans_desk"))
    assert st.player.block == 14
    made = [c for c in st.player.draw_pile if klee_overhaul.is_status(c)]
    assert len(made) == 1 and klee_overhaul.is_confiscated(made[0])

    st = klee_state([make_enemy(hp=200)])
    play(st, _up("proto_ko_behind_jeans_desk"))
    assert st.player.block == 18


# Kitchen Alchemy, reworked 2026-10-02 after the forced-deck seat (0 plays in
# 7 hands: a status is rarely in hand): "ALL enemies lose 1 [2] Strength.
# Exhaust every status in your hand; they lose 1 more for each."

def test_kitchen_alchemy_plays_with_no_status_and_every_enemy_loses_one(
        overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    b.powers["strength"] = 3
    st = klee_state([a, b])
    st.player.hand = [load("proto_ko_chain_fuse")]
    card = load("proto_ko_kitchen_alchemy")
    assert combat.card_playable(st, card)
    play(st, card)
    assert [c.id for c in st.player.hand] == ["proto_ko_chain_fuse"]
    # Permanent: negative Strength on the body, not a this-turn loss.
    assert (a.powers.get("strength"), b.powers.get("strength")) == (-1, 2)


def test_kitchen_alchemy_exhausts_every_status_and_each_adds_one(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a, b])
    dazed, conf = statuses.make_status("dazed"), _confiscated()
    st.player.hand = [dazed, load("proto_ko_chain_fuse"), conf]
    play(st, load("proto_ko_kitchen_alchemy"))
    assert [c.id for c in st.player.hand] == ["proto_ko_chain_fuse"]
    assert dazed in st.player.exhaust_pile and conf in st.player.exhaust_pile
    # 1 + 1 per status, applied once as one total.
    assert (a.powers.get("strength"), b.powers.get("strength")) == (-3, -3)


def test_kitchen_alchemy_upgraded_base_is_two(overhaul):
    c = make_enemy(hp=200, name="c")
    st = klee_state([c])
    st.player.hand = []
    play(st, _up("proto_ko_kitchen_alchemy"))
    assert c.powers.get("strength") == -2

    d = make_enemy(hp=200, name="d")
    st = klee_state([d])
    st.player.hand = [statuses.make_status("dazed")]
    play(st, _up("proto_ko_kitchen_alchemy"))
    assert d.powers.get("strength") == -3        # the per-status 1 holds


def test_kitchen_alchemy_leaves_a_curse_in_hand(overhaul):
    enemy = make_enemy(hp=200)
    st = klee_state([enemy])
    curse = Card(id="regret", name="Regret", cost=-1, type="curse",
                 rarity="curse", effects=[])
    dazed = statuses.make_status("dazed")
    st.player.hand = [curse, dazed]
    play(st, load("proto_ko_kitchen_alchemy"))
    assert st.player.hand == [curse]
    assert curse not in st.player.exhaust_pile
    assert enemy.powers.get("strength") == -2
