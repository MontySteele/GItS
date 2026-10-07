"""THE KLEE FINAL PASS (2026-10-02): the sim half.

Paper `review/active/klee-final-pass-2026-10-02.md`, "Ruled": HP 70;
Kitchen Alchemy unchanged; Cover Your Ears! in (Uncommon Skill, 0 Energy and
2 Sparks, Exhaust: "ALL enemies lose 6 [8] Strength this turn."); Blast
Shield to Common; Where Did I Put It? cut. The C# twin is
`KleeTests/Prototype/KleeFinalPassTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).
"""

from __future__ import annotations

import collections

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, powers
from tier0.tests.conftest import make_enemy
from tier0.tests.test_klee_r276_expansion import (  # noqa: F401
    klee_state, load, overhaul, play)

CYE = "proto_ko_cover_your_ears"


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _loss(card):
    return next(fx for fx in card.effects if fx.get("op") == "lose_strength")


def test_klee_starts_on_seventy():
    assert loader._character_index()["klee"]["hp"] == 70


def test_the_pool_stays_seventy_eight_at_24_33_21(overhaul):
    ids = C.KLEE_OVERHAUL_POOL_IDS
    assert len(ids) == 78
    assert CYE in ids
    assert "proto_ko_where_did_i_put_it" not in ids
    assert "proto_ko_where_did_i_put_it" not in {
        c.id for c in loader.prototype_cards()}
    rarity = collections.Counter(load(cid).rarity for cid in ids)
    assert rarity == {"common": 25, "uncommon": 32, "rare": 21}
    assert load("proto_ko_blast_shield").rarity == "common"


def test_cover_your_ears_shape_and_numbers(overhaul):
    card = load(CYE)
    assert (card.type, card.cost, card.rarity) == ("skill", 0, "uncommon")
    assert card.exhaust
    assert combat.spark_cost(card) == 2
    assert _loss(card)["amount"] == 6 and _loss(card)["this_turn"] is True
    assert _loss(_up(CYE))["amount"] == 8
    assert combat.spark_cost(_up(CYE)) == 2


def test_cover_your_ears_needs_two_sparks(overhaul):
    st = klee_state([make_enemy(hp=200)])
    st.player.sparks = 1
    assert not combat.card_playable(st, load(CYE))
    st.player.sparks = 2
    assert combat.card_playable(st, load(CYE))


def test_cover_your_ears_takes_six_from_all_for_the_enemy_turn_only(overhaul):
    """Piercing Wail's shape: the Strength is gone now and comes back at the
    end of each enemy's own turn (`temp_strength_down`)."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    b.powers["strength"] = 3
    st = klee_state([a, b])
    st.player.sparks = 2
    play(st, load(CYE))
    assert st.player.sparks == 0
    assert (a.powers.get("strength"), b.powers.get("strength")) == (-6, -3)
    st.in_player_turn = False
    powers.on_turn_end(st, a)
    powers.on_turn_end(st, b)
    assert (a.powers.get("strength"), b.powers.get("strength")) == (0, 3)
    assert "temp_strength_down" not in a.powers


def test_cover_your_ears_upgraded_takes_eight(overhaul):
    a = make_enemy(hp=200, name="a")
    st = klee_state([a])
    st.player.sparks = 2
    play(st, _up(CYE))
    assert a.powers.get("strength") == -8


def test_kitchen_alchemy_is_unchanged(overhaul):
    """Ruled: "Kitchen Alchemy stays as it is." Permanent, 1 plus 1 per
    status, upgrade Retain."""
    loss = _loss(load("proto_ko_kitchen_alchemy"))
    assert (loss["amount"], loss["per_status"]) == (1, 1)
    assert "this_turn" not in loss
