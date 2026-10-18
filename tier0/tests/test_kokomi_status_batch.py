"""KOKOMI STATUS BATCH (2026-10-01): the sim half.

Paper `review/active/kokomi-status-batch-2026-10-01.md`, ruled: "the 7
removals are good", "Agreed on the Plan text change". Seven cards built here
(Kelp Wall, Tidecleanse, Sea Glass Harvest, Turning Tide, Flotsam Surge,
Abyssal Salvage, and Riptide Ruin, the Rare that replaced the cut Coral
Sanctuary), so the pool is 78 (21 / 37 / 20 since the jellyfish build,
2026-10-12). The C# twin is
`KleeTests/Prototype/KokomiStatusBatchTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).

THE KOKOMI ROUND-1 FIXES (2026-10-12): Kelp Wall counts the hand WHEN THE
PLAN IS WRITTEN (the number its preview shows) and Sea Glass Harvest
transforms the DRAW PILE; both used to read the carry-out hand, which seats
found empty of the statuses they wrote the Plan for.

THE RE-FOUNDING (2026-10-12) cut Turning Tide and Abyssal Salvage and made
Tidecleanse's Exhaust its now-line; their old tests left with them.
"""

from __future__ import annotations

import collections

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan, statuses
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    kokomi_state, overhaul, plan_card)

QUIET = [{"kind": "block", "amount": 5}]
CUT = ("proto_kk_rally", "proto_kk_pearl_diver", "proto_kk_battle_plan",
       "proto_kk_feigned_retreat", "proto_kk_moon_signal",
       "proto_kk_chain_of_command", "proto_kk_all_streams_flow_to_the_sea")


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _quiet_state():
    return kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])


def _filler(n):
    return [plan_card([], cid=f"proto_kk_lib{i}") for i in range(n)]


def _carry_out(st, card):
    """Write `card`'s Plan and carry it out at once."""
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)


# --- the pool -----------------------------------------------------------------

def test_the_batch_cuts_seven_and_its_five_survivors(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 79  # Kokomi v3 (2026-10-18): Unbroken Tide
    rows = {c.id: c for c in loader.prototype_cards()}
    for cid in CUT:
        assert cid not in ids
        assert cid not in rows
    assert "proto_kk_coral_sanctuary" not in rows
    rarity = collections.Counter(_row(cid).rarity for cid in ids)
    # The Kokomi level pass (2026-10-12): Change of Plans C -> U, 20 / 38 / 20.
    assert rarity == {"common": 20, "uncommon": 39, "rare": 20}
    # The re-founding (2026-10-12) cut Turning Tide and Abyssal Salvage.
    for cid in ("proto_kk_turning_tide", "proto_kk_abyssal_salvage"):
        assert cid not in ids
    survivors = ("proto_kk_kelp_wall", "proto_kk_tidecleanse",
                 "proto_kk_sea_glass_harvest", "proto_kk_flotsam_surge",
                 "proto_kk_riptide_ruin")
    shapes = {cid: (_row(cid).type, _row(cid).cost, _row(cid).rarity)
              for cid in survivors}
    assert set(survivors) <= set(ids)
    assert shapes == {
        "proto_kk_kelp_wall": ("skill", 1, "common"),
        "proto_kk_tidecleanse": ("skill", 0, "common"),
        "proto_kk_sea_glass_harvest": ("skill", 1, "uncommon"),
        "proto_kk_flotsam_surge": ("attack", 1, "uncommon"),
        "proto_kk_riptide_ruin": ("attack", 2, "rare"),
    }


# --- Kelp Wall: the count is the hand it was written from ---------------------

def test_kelp_wall_pays_the_flat_block_on_a_clean_hand(overhaul):
    """The Kokomi level pass (2026-10-12): the status count went. The pool
    overhaul (2026-10-13): the Plan is a Counter line -- Hydro damage equal
    to the damage she blocked since she planned it (was a flat 12 [15]
    Block). With nothing blocked, it gives no Block and deals nothing."""
    assert _row("proto_kk_kelp_wall").plan == [
        {"op": "damage_blocked_since", "target": "front_enemy"}]
    st = _quiet_state()
    st.player.hand = _filler(3)
    hp = st.enemies[0].hp
    _carry_out(st, _row("proto_kk_kelp_wall"))
    assert st.player.block == 0
    assert st.enemies[0].hp == hp


def test_kelp_wall_ignores_statuses_in_hand(overhaul):
    st = _quiet_state()
    st.player.hand = [statuses.make_status("dazed"),
                      statuses.make_status("dazed")]
    kokomi_plan.schedule(st, _row("proto_kk_kelp_wall"))
    kokomi_plan.note_enemy_hit(st, st.enemies[0], blocked=9, incoming=12)
    hp = st.enemies[0].hp
    kokomi_plan.resolve_all(st)
    assert st.player.block == 0
    assert hp - st.enemies[0].hp == 9


def test_kelp_wall_upgrades_the_flat_block_only(overhaul):
    """Its upgrade moves the now-line's Block alone (7 -> 9 since the
    numbers pass, kokomi-review-r5-2026-10-14); the Plan line prints no number."""
    up = _up("proto_kk_kelp_wall")
    assert up.effects[0]["amount"] == 9
    assert up.plan == _row("proto_kk_kelp_wall").plan


# --- Tidecleanse -------------------------------------------------------------------

def _play_now(st, card):
    st.player.energy = 3
    st.player.hand.append(card)
    combat.play_card(st, card)


def test_tidecleanse_exhausts_up_to_two(overhaul):
    """The re-founding (2026-10-12): the Exhaust is the now-line, first."""
    st = _quiet_state()
    st.player.hand = [statuses.make_status("dazed"),
                      statuses.make_status("wound"),
                      statuses.make_status("slimed")] + _filler(2)
    card = _row("proto_kk_tidecleanse")
    assert card.plan == []
    _play_now(st, card)
    assert len(kokomi_plan.statuses_in_hand(st)) == 1
    assert sum(c.id.startswith("status_") for c in st.player.exhaust_pile) == 2
    assert len(st.player.hand) == 3


def test_tidecleanse_upgraded_exhausts_three(overhaul):
    st = _quiet_state()
    st.player.hand = [statuses.make_status("dazed") for _ in range(4)]
    _play_now(st, _up("proto_kk_tidecleanse"))
    assert len(st.player.hand) == 1


def test_tidecleanse_now_line_applies_weak(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300)])     # an attack intent
    card = _row("proto_kk_tidecleanse")
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert st.enemies[0].powers.get("weak", 0) == 1
    assert not st.kk_plan_queue


def test_tidecleanse_draws_per_status_in_the_kind_not_a_row_op(overhaul):
    """[USER]'s run (2026-10-11): "Tidecleanse as a cycling card at Common is
    too good" -- the card pass's "Draw 1 card." comes off. Kokomi review r9
    (2026-10-15, item 1) gives it back as "Draw 1 card for each" Status
    exhausted, inside the `exhaust_statuses` kind, so the rows are the same."""
    assert _row("proto_kk_tidecleanse").effects == [
        {"op": "kokomi", "kind": "exhaust_statuses", "amount": 2},
        {"op": "apply_power", "power": "weak", "amount": 1,
         "target": "enemy"}]


# --- Sea Glass Harvest ---------------------------------------------------------------

def test_sea_glass_harvest_transforms_the_hand_and_draw_piles_statuses(
        overhaul):
    """Kokomi round-1 fixes (2026-10-12): the DRAW PILE, in place; and the
    HAND too since the round-5 review (2026-10-14, A8), so a Status drawn
    that morning becomes Sea Glass the same turn."""
    st = _quiet_state()
    curse = plan_card([], cid="proto_kk_curse_probe")
    curse.type, curse.rarity = "curse", "curse"
    keep = _filler(1)[0]
    held = statuses.make_status("wound")
    st.player.hand = [held]
    st.player.draw_pile = [statuses.make_status("dazed"), keep, curse]
    _carry_out(st, _row("proto_kk_sea_glass_harvest"))
    ids = [c.id for c in st.player.draw_pile]
    assert ids == [kokomi_plan.SEA_GLASS, keep.id, kokomi_plan.SEA_GLASS]
    assert [c.id for c in st.player.hand] == [kokomi_plan.SEA_GLASS]
    assert held not in st.player.hand
    glass = st.player.draw_pile[0]
    assert glass.cost == 0 and glass.exhaust
    assert glass.effects == [{"op": "energy", "amount": 1}]


def test_sea_glass_harvest_upgraded_makes_sea_glass_plus(overhaul):
    up = _up("proto_kk_sea_glass_harvest")
    assert up.plan == [{"op": "transform_statuses_you_have",
                        "upgraded": True}]
    st = _quiet_state()
    st.player.draw_pile = [statuses.make_status("wound")]
    _carry_out(st, up)
    assert st.player.draw_pile[0].effects == [{"op": "energy", "amount": 2}]


# --- Flotsam Surge ------------------------------------------------------------------------

def test_flotsam_surge_hits_all_and_discards_two_dazed(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=100), make_enemy(hp=100)])
    st.player.draw_pile = _filler(4)
    card = _row("proto_kk_flotsam_surge")
    st.player.energy = 3
    st.player.hand.append(card)
    combat.play_card(st, card)
    # The Kokomi level pass (2026-10-12): 10 [13] (was 13 [17]).
    assert all(e.hp == 100 - 10 for e in st.enemies)
    dazed = [c for c in st.player.discard_pile if c.id == "status_dazed"]
    assert len(dazed) == 2
    assert _up("proto_kk_flotsam_surge").effects[0]["amount"] == 13


# --- Riptide Ruin ------------------------------------------------------------------------

def test_riptide_ruin_hits_all_twice_and_adds_no_dazed(overhaul):
    """The Rare in Coral Sanctuary's place (ruled 2026-10-01). Since the card
    text pass and the Kokomi level pass (2026-10-12): "Deal 11 [14] Hydro
    damage to ALL enemies twice." The Dazed went."""
    st = kokomi_state(enemies=[make_enemy(hp=100), make_enemy(hp=100)])
    st.player.draw_pile = _filler(4)
    card = _row("proto_kk_riptide_ruin")
    assert (card.type, card.cost, card.rarity) == ("attack", 2, "rare")
    st.player.energy = 3
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert all(e.hp == 100 - 11 * 2 for e in st.enemies)
    dazed = [c for c in st.player.discard_pile if c.id == "status_dazed"]
    assert dazed == []
    up = _up("proto_kk_riptide_ruin").effects[0]
    assert (up["amount"], up["times"]) == (14, 2)


# --- the shape check -------------------------------------------------------------------------

@pytest.mark.parametrize("op", ["block_per_status_in_hand",
                                "transform_statuses_you_have"])
def test_the_two_surviving_clauses_are_plan_only(op):
    assert op in kokomi_plan.PLAN_KINDS
    assert op in kokomi_plan.PLAN_ONLY_OPS
