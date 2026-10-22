"""KOKOMI PAYOFF PASS (2026-10-01): Second Thoughts cut, two Uncommons added.

The main session recommended cutting Second Thoughts ("an undo button, and an
undo is a dead draw") alongside a Plan-volume payoff that is not damage, and
[USER] ruled: "Sounds good! Please proceed!" The sim half; the C# twin is
`KleeTests/Prototype/KokomiPayoffPassTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).

  * Kurage Canopy: "At the start of your turn, if 2 or more of your Plans
    were carried out, add a Ward to your Hand. Stings and Wards don't count."
    (Kokomi defence pass, 2026-10-22; was a Ward per carry-out since the
    round 3 A-list, 2026-10-13.) Upgraded, Ward+.
  * Coral Tithe: cut with the Casket count (the re-founding, 2026-10-12);
    its tests left with it.
"""

from __future__ import annotations

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


# --- the pool -----------------------------------------------------------------

def test_the_pass_cuts_second_thoughts_and_canopy_stays(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 79  # Kokomi v3 (2026-10-18): Unbroken Tide
    # The re-founding (2026-10-12) cut Coral Tithe; Kurage Canopy stays.
    assert "proto_kk_kurage_canopy" in ids
    assert "proto_kk_coral_tithe" not in ids
    assert "proto_kk_second_thoughts" not in ids
    assert "proto_kk_second_thoughts" not in {
        c.id for c in loader.prototype_cards()}
    assert not hasattr(kokomi_plan, "cancel_last_plan")
    assert _row("proto_kk_kurage_canopy").rarity == "uncommon"
    assert _row("proto_kk_kurage_canopy").cost == 1
    assert _row("proto_kk_kurage_canopy").type == "power"


# --- Kurage Canopy --------------------------------------------------------------

def _wards(st, upgraded=False):
    want = kokomi_plan.WARD_ID + (upgrades.SUFFIX if upgraded else "")
    return sum(1 for c in st.player.hand if c.id == want)


def _morning(st):
    """The turn start's Kokomi steps, in `combat._player_turn`'s order."""
    kokomi_plan.resolve_all(st)
    kokomi_plan.battle_formation(st)
    kokomi_plan.kurage_canopy(st)


def test_kurage_canopy_adds_one_ward_after_two_plans(overhaul):
    """Kokomi defence pass (2026-10-22): "At the start of your turn, if 2 or
    more of your Plans were carried out, add a Ward to your Hand. Stings and
    Wards don't count." Once a morning, not per carry-out."""
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    _write(st, "proto_kk_kurage_canopy")
    assert st.player.powers[kokomi_plan.KURAGE_CANOPY] == 1
    st.player.hand.clear()
    st.player.block = 0
    for i in range(3):
        kokomi_plan.schedule(st, plan_card(
            [{"op": "energy", "amount": 1}], cid=f"proto_kk_p{i}"))
    _morning(st)
    assert _wards(st) == 1
    assert st.player.block == 0


def test_kurage_canopy_one_plan_pays_nothing(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 1
    st.player.hand.clear()
    kokomi_plan.schedule(st, plan_card(
        [{"op": "energy", "amount": 1}], cid="proto_kk_p"))
    _morning(st)
    assert _wards(st) == 0


def test_kurage_canopy_upgraded_adds_an_upgraded_ward(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    _write(st, _up("proto_kk_kurage_canopy"))
    assert st.player.powers[kokomi_plan.KURAGE_CANOPY_PLUS] == 1
    assert kokomi_plan.KURAGE_CANOPY not in st.player.powers
    assert _up("proto_kk_kurage_canopy").cost == 1
    st.player.hand.clear()
    for i in range(2):
        kokomi_plan.schedule(st, plan_card(
            [{"op": "energy", "amount": 1}], cid=f"proto_kk_p{i}"))
    _morning(st)
    assert _wards(st, upgraded=True) == 1
    assert _wards(st) == 0
