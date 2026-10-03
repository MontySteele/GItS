"""KOKOMI STATUS BATCH (2026-10-01): the sim half.

Paper `review/active/kokomi-status-batch-2026-10-01.md`, ruled: "the 7
removals are good", "Agreed on the Plan text change". Seven cards built here
(Kelp Wall, Tidecleanse, Sea Glass Harvest, Turning Tide, Flotsam Surge,
Abyssal Salvage, and Riptide Ruin, the Rare that replaced the cut Coral
Sanctuary), so the pool is 78 (21 / 36 / 21). The C# twin is
`KleeTests/Prototype/KokomiStatusBatchTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).

The load-bearing reading: a Plan resolves after the next turn's draw (brief
sec.2 rule 2), so "in your hand" on a Plan is the hand just drawn.
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
    """Write `card`'s Plan and carry it out against the hand as it stands."""
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)


# --- the pool -----------------------------------------------------------------

def test_the_batch_cuts_seven_and_adds_seven(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 78
    assert ids[-7:] == C.KOKOMI_STATUS_BATCH_IDS
    rows = {c.id: c for c in loader.prototype_cards()}
    for cid in CUT:
        assert cid not in ids
        assert cid not in rows
    assert "proto_kk_coral_sanctuary" not in rows
    rarity = collections.Counter(_row(cid).rarity for cid in ids)
    assert rarity == {"common": 21, "uncommon": 36, "rare": 21}
    shapes = {cid: (_row(cid).type, _row(cid).cost, _row(cid).rarity)
              for cid in C.KOKOMI_STATUS_BATCH_IDS}
    assert shapes == {
        "proto_kk_kelp_wall": ("skill", 1, "common"),
        "proto_kk_tidecleanse": ("skill", 0, "common"),
        "proto_kk_sea_glass_harvest": ("skill", 1, "uncommon"),
        "proto_kk_turning_tide": ("skill", 0, "uncommon"),
        "proto_kk_flotsam_surge": ("attack", 1, "uncommon"),
        "proto_kk_abyssal_salvage": ("power", 1, "uncommon"),
        "proto_kk_riptide_ruin": ("attack", 2, "rare"),
    }


# --- the next hand: a Plan reads the hand drawn before it ----------------------

def test_a_plan_reads_the_hand_drawn_that_morning(overhaul):
    """Kelp Wall written today; tomorrow's draw brings two Dazed; the Plan,
    carried out after the draw, counts them. The real turn loop drives it."""
    st = _quiet_state()
    kokomi_plan.schedule(st, _row("proto_kk_kelp_wall"))
    st.player.hand = []
    st.player.draw_pile = ([statuses.make_status("dazed"),
                            statuses.make_status("dazed")] + _filler(8))
    combat._player_turn(st, lambda s: None)
    kelp = [e for e in st.log if e["event"] == "plan_kelp_wall"]
    assert kelp and kelp[0]["statuses"] == 2
    assert st.player.block == 7 + 3 * 2


def test_kelp_wall_pays_the_flat_block_on_a_clean_hand(overhaul):
    st = _quiet_state()
    st.player.hand = _filler(3)
    _carry_out(st, _row("proto_kk_kelp_wall"))
    assert st.player.block == 7


def test_kelp_wall_upgrades_the_flat_block_only(overhaul):
    st = _quiet_state()
    st.player.hand = [statuses.make_status("wound")]
    _carry_out(st, _up("proto_kk_kelp_wall"))
    assert st.player.block == 10 + 3


# --- Tidecleanse -------------------------------------------------------------------

def test_tidecleanse_exhausts_up_to_two(overhaul):
    st = _quiet_state()
    st.player.hand = [statuses.make_status("dazed"),
                      statuses.make_status("wound"),
                      statuses.make_status("slimed")] + _filler(2)
    _carry_out(st, _row("proto_kk_tidecleanse"))
    assert len(kokomi_plan.statuses_in_hand(st)) == 1
    assert len(st.player.exhaust_pile) == 2
    assert len(st.player.hand) == 3


def test_tidecleanse_upgraded_exhausts_three(overhaul):
    st = _quiet_state()
    st.player.hand = [statuses.make_status("dazed") for _ in range(4)]
    _carry_out(st, _up("proto_kk_tidecleanse"))
    assert len(st.player.hand) == 1


def test_tidecleanse_now_line_applies_weak(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300)])     # an attack intent
    card = _row("proto_kk_tidecleanse")
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert st.enemies[0].powers.get("weak", 0) == 1
    assert not st.kk_plan_queue


# --- Sea Glass Harvest ---------------------------------------------------------------

def test_sea_glass_harvest_transforms_statuses_and_curses(overhaul):
    st = _quiet_state()
    curse = plan_card([], cid="proto_kk_curse_probe")
    curse.type, curse.rarity = "curse", "curse"
    keep = _filler(1)[0]
    st.player.hand = [statuses.make_status("dazed"), keep, curse]
    _carry_out(st, _row("proto_kk_sea_glass_harvest"))
    ids = [c.id for c in st.player.hand]
    assert ids == [kokomi_plan.SEA_GLASS, keep.id, kokomi_plan.SEA_GLASS]
    glass = st.player.hand[0]
    assert glass.cost == 0 and glass.exhaust
    assert glass.effects == [{"op": "energy", "amount": 1}]


def test_sea_glass_harvest_upgraded_makes_sea_glass_plus(overhaul):
    up = _up("proto_kk_sea_glass_harvest")
    assert up.plan == [{"op": "transform_statuses_in_hand",
                        "upgraded": True}]
    st = _quiet_state()
    st.player.hand = [statuses.make_status("wound")]
    _carry_out(st, up)
    assert st.player.hand[0].effects == [{"op": "energy", "amount": 2}]


# --- Turning Tide -----------------------------------------------------------------------

def test_turning_tide_discards_the_clogs_and_draws_that_many(overhaul):
    st = _quiet_state()
    st.player.hand = [statuses.make_status("wound"),
                      statuses.make_status("wound")] + _filler(1)
    st.player.draw_pile = _filler(5)
    _carry_out(st, _row("proto_kk_turning_tide"))
    assert not kokomi_plan.statuses_in_hand(st)
    assert len(st.player.hand) == 3
    assert len(st.player.discard_pile) == 2


# --- Flotsam Surge ------------------------------------------------------------------------

def test_flotsam_surge_hits_all_and_discards_two_dazed(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=100), make_enemy(hp=100)])
    st.player.draw_pile = _filler(4)
    card = _row("proto_kk_flotsam_surge")
    st.player.energy = 3
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert all(e.hp == 100 - 13 for e in st.enemies)
    dazed = [c for c in st.player.discard_pile if c.id == "status_dazed"]
    assert len(dazed) == 2
    assert _up("proto_kk_flotsam_surge").effects[0]["amount"] == 17


# --- Riptide Ruin ------------------------------------------------------------------------

def test_riptide_ruin_hits_all_twice_and_discards_three_dazed(overhaul):
    """The Rare in Coral Sanctuary's place (ruled 2026-10-01): "Deal 9 [12]
    damage to ALL enemies twice. Add 3 Dazed into your Discard Pile." """
    st = kokomi_state(enemies=[make_enemy(hp=100), make_enemy(hp=100)])
    st.player.draw_pile = _filler(4)
    card = _row("proto_kk_riptide_ruin")
    assert (card.type, card.cost, card.rarity) == ("attack", 2, "rare")
    st.player.energy = 3
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert all(e.hp == 100 - 9 * 2 for e in st.enemies)
    dazed = [c for c in st.player.discard_pile if c.id == "status_dazed"]
    assert len(dazed) == 3
    up = _up("proto_kk_riptide_ruin").effects[0]
    assert (up["amount"], up["times"]) == (12, 2)


# --- Abyssal Salvage -----------------------------------------------------------------------

def test_abyssal_salvage_feeds_the_casket_per_status_exhausted(overhaul):
    st = _quiet_state()
    st.player.powers[kokomi_plan.ABYSSAL_SALVAGE] = 1
    st.player.hand = [statuses.make_status("dazed"),
                      statuses.make_status("wound")]
    _carry_out(st, _row("proto_kk_tidecleanse"))
    # Two exhausted, plus the Plan's own carry-out (no Casket relic here,
    # so the relic's count does not move; the Power's does).
    assert st.kk_casket == 2
    assert st.player.block == 0


def test_abyssal_salvage_ignores_her_own_cards(overhaul):
    from tier0.engine import refpowers
    st = _quiet_state()
    st.player.powers[kokomi_plan.ABYSSAL_SALVAGE] = 1
    refpowers.exhaust_card(st, _filler(1)[0])
    assert st.kk_casket == 0


def test_abyssal_salvage_upgraded_also_blocks(overhaul):
    up = _up("proto_kk_abyssal_salvage")
    assert up.effects[0]["power"] == kokomi_plan.ABYSSAL_SALVAGE_PLUS
    st = _quiet_state()
    st.player.energy = 3
    st.player.hand.append(up)
    combat.play_card(st, up)
    assert st.player.powers[kokomi_plan.ABYSSAL_SALVAGE_PLUS] == 1
    from tier0.engine import refpowers
    refpowers.exhaust_card(st, statuses.make_status("dazed"),
                           caused_by_ethereal=True)
    assert st.kk_casket == 1
    assert st.player.block == 2


def test_an_ethereal_dazed_at_turn_end_counts(overhaul):
    """Flotsam's Dazed exhausts itself from hand at turn end: that pays."""
    st = _quiet_state()
    st.player.powers[kokomi_plan.ABYSSAL_SALVAGE] = 1
    st.player.hand = []
    st.player.draw_pile = [statuses.make_status("dazed")] + _filler(8)
    combat._player_turn(st, lambda s: None)
    assert st.kk_casket >= 1


# --- the shape check -------------------------------------------------------------------------

@pytest.mark.parametrize("op", ["block_per_status_in_hand",
                                "exhaust_statuses_in_hand",
                                "transform_statuses_in_hand",
                                "discard_and_draw"])
def test_the_four_clauses_are_plan_only(op):
    assert op in kokomi_plan.PLAN_KINDS
    assert op in kokomi_plan.PLAN_ONLY_OPS
