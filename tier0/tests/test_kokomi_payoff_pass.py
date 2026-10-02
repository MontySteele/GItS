"""KOKOMI PAYOFF PASS (2026-10-01): Second Thoughts cut, two Uncommons added.

The main session recommended cutting Second Thoughts ("an undo button, and an
undo is a dead draw") alongside a Plan-volume payoff that is not damage, and
[USER] ruled: "Sounds good! Please proceed!" The sim half; the C# twin is
`KleeTests/Prototype/KokomiPayoffPassTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).

  * Kurage Canopy: "Whenever the Bake-Kurage carries out a Plan, gain 2
    Block." Per carry-out, so a Plan carried out twice pays twice.
  * Coral Tithe: "Empty the Casket. Gain 1 Energy and draw 1 card for every 3
    in it." Rounds down; only while she holds a Casket.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    kokomi_state, overhaul, plan_card)

QUIET = [{"kind": "block", "amount": 5}]


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _write(st, card, energy=10):
    card = _row(card) if isinstance(card, str) else card
    st.player.energy = energy
    st.player.hand.append(card)
    combat.play_card(st, card)
    return card


def _library(st, n=10):
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_lib{i}")
                           for i in range(n)]


# --- the pool -----------------------------------------------------------------

def test_the_pass_cuts_second_thoughts_and_adds_two_uncommons(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    # Pool completion (2026-10-01) appended eight after the two, and the
    # status batch (2026-10-01) seven more.
    assert len(ids) == 78
    assert ids[-17:-15] == C.KOKOMI_PAYOFF_PASS_IDS == (
        "proto_kk_kurage_canopy", "proto_kk_coral_tithe")
    assert "proto_kk_second_thoughts" not in ids
    assert "proto_kk_second_thoughts" not in {
        c.id for c in loader.prototype_cards()}
    assert not hasattr(kokomi_plan, "cancel_last_plan")
    for cid in C.KOKOMI_PAYOFF_PASS_IDS:
        assert _row(cid).rarity == "uncommon"
    assert _row("proto_kk_kurage_canopy").cost == 1
    assert _row("proto_kk_kurage_canopy").type == "power"
    assert _row("proto_kk_coral_tithe").cost == 0
    assert _row("proto_kk_coral_tithe").type == "skill"


# --- Kurage Canopy --------------------------------------------------------------

def test_kurage_canopy_blocks_per_carry_out(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    _write(st, "proto_kk_kurage_canopy")
    assert st.player.powers[kokomi_plan.KURAGE_CANOPY] == 2
    st.player.block = 0
    for i in range(2):
        kokomi_plan.schedule(st, plan_card(
            [{"op": "energy", "amount": 1}], cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_all(st)
    assert st.player.block == 2 * 2


def test_kurage_canopy_pays_a_doubled_carry_out_twice(overhaul):
    """Second Wave's rider: the Plan after it is carried out twice, so three
    carry-outs in all (the rider's own entry, then the next one twice)."""
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 2
    st.player.block = 0
    kokomi_plan.schedule(st, plan_card(
        [{"op": "next_plan_extra_carry_out"}], cid="proto_kk_rider"))
    kokomi_plan.schedule(st, plan_card(
        [{"op": "energy", "amount": 1}], cid="proto_kk_next"))
    kokomi_plan.resolve_all(st)
    assert st.kk_plans_carried_out_this_turn == 3
    assert st.player.block == 3 * 2


def test_kurage_canopy_upgrades_to_three(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    _write(st, _up("proto_kk_kurage_canopy"))
    assert st.player.powers[kokomi_plan.KURAGE_CANOPY] == 3
    assert _up("proto_kk_kurage_canopy").cost == 1


# --- Coral Tithe ----------------------------------------------------------------

@pytest.mark.parametrize("casket,paid", [(0, 0), (3, 1), (7, 2)])
def test_coral_tithe_pays_one_per_three(overhaul, casket, paid):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    _library(st)
    st.kk_casket = casket
    _write(st, "proto_kk_coral_tithe", energy=0)
    assert st.kk_casket == 0
    assert st.player.energy == paid
    assert len(st.player.hand) == paid


@pytest.mark.parametrize("casket,paid", [(0, 0), (3, 1), (7, 3)])
def test_coral_tithe_upgraded_pays_one_per_two(overhaul, casket, paid):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    _library(st)
    st.kk_casket = casket
    _write(st, _up("proto_kk_coral_tithe"), energy=0)
    assert st.kk_casket == 0
    assert st.player.energy == paid
    assert len(st.player.hand) == paid


def test_coral_tithe_does_nothing_without_a_casket(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    _library(st)
    st.kk_casket = 7
    _write(st, "proto_kk_coral_tithe", energy=0)
    assert st.kk_casket == 7
    assert st.player.energy == 0
    assert st.player.hand == []
