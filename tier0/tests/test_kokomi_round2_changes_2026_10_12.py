"""Kokomi round-2 changes (2026-10-12), the sim side.

From the Fable round-1 review and the round record
`review/records/kokomi-round-1-2026-10-12.md`; provenance note "Kokomi
round-2 changes, 2026-10-12". The C# twins are
`klee-mod/KleeTests/Prototype/KokomiRound2ChangesTests.cs`. NOTHING MEASURED
HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import pytest

from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, write)
from tier0.tests.test_arm_keyword_tips import (  # noqa: E402
    PROTOTYPE_DIR, TIPS_CS, gen, proto)


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _amount(c):
    return c.effects[0]["amount"]


# The three jellyfish generators moved again in the jellyfish build
# (2026-10-12): `test_kokomi_jellyfish_build_2026_10_12`.
@pytest.mark.parametrize("cid,base,up", [
    ("proto_kk_coordinated_tide", 6, 9),
    ("proto_kk_kurage_canopy", 3, 4),
    ("proto_kk_grand_strategist", 7, 10),
    ("proto_kk_shoal_of_spears", 5, 6),
])
def test_the_retuned_numbers(cid, base, up):
    assert (_amount(_row(cid)), _amount(_up(cid))) == (base, up)


def test_tideturn_is_8_per_plan_waiting_and_10_upgraded():
    assert _row("proto_kk_tideturn").effects[0]["amount_formula"]["per"] == 8
    assert _up("proto_kk_tideturn").effects[0]["amount_formula"]["per"] == 10


# Shoal Call is Blade Dance since the jellyfish build (2026-10-12): cost 1.
@pytest.mark.parametrize("cid", ["proto_kk_watatsumi_muster"])
def test_the_generators_cost_0_exhaust_and_cannot_be_written(cid):
    row = _row(cid)
    assert row.cost == 0 and row.exhaust
    assert _up(cid).cost == 0
    assert not kokomi_plan.can_be_written(row)


def test_call_the_generals_hands_a_card_that_costs_0_this_turn():
    st = kokomi_state()
    assert kokomi_plan.call_the_generals(st) == 1
    (got,) = st.player.hand
    assert got.free_this_turn and got.is_ethereal and got.cost >= 2
    rows = {r["id"]: r for r in proto._rows()}
    assert rows["proto_kk_call_the_generals"]["description"].endswith(
        "It costs 0 this turn.")


def _draws(st):
    return [e for e in st.log if e["event"] == "plan_treatise"]


def test_treatise_draws_for_a_companion_played_without_writing_it():
    st = kokomi_state()
    st.player.powers[kokomi_plan.TREATISE] = 1
    st.player.draw_pile = [card("proto_kk_evening_watch") for _ in range(3)]
    companion = card("proto_mi_shinobu_thundergrust")
    st.enemies[0].intents = [{"kind": "attack", "amount": 5}]
    st.player.hand.append(companion)
    assert not kokomi_plan.plan_aimed_at_pet(st, companion)
    combat.play_card(st, companion)
    assert len(_draws(st)) == 1


def test_treatise_draws_nothing_for_a_plain_card():
    st = kokomi_state()
    st.player.powers[kokomi_plan.TREATISE] = 1
    st.player.draw_pile = [card("proto_kk_evening_watch") for _ in range(3)]
    plain = card("proto_kk_evening_watch")
    assert not kokomi_plan.can_be_written(plain)
    st.player.hand.append(plain)
    combat.play_card(st, plain)
    assert _draws(st) == []


def test_treatise_draws_nothing_for_a_written_companions_carry_out():
    st = kokomi_state()
    write(st, card("proto_mi_shinobu_thundergrust"))
    st.player.powers[kokomi_plan.TREATISE] = 1
    st.player.draw_pile = [card("proto_kk_evening_watch") for _ in range(3)]
    carry_out(st)
    assert _draws(st) == []


def test_nereids_ascension_carries_the_twice_tip():
    rows = {r["id"]: r for r in gen._load_prototype_rows()} \
        if hasattr(gen, "_load_prototype_rows") else None
    src = (PROTOTYPE_DIR / "ProtoKkNereidsAscension.cs").read_text(
        encoding="utf-8")
    assert "ArmKeywordTips.ForNereidsTwice(" in src
    tips = TIPS_CS.read_text(encoding="utf-8")
    assert ("\"Twice means twice: the [gold]Plan[/gold]'s debuffs, and any \""
            in tips)
    assert "\"Tainted it causes, double too. A [gold]Plan[/gold] carried out \"" in tips
    for rid, row in {r["id"]: r for r in proto._rows()}.items():
        assert gen.doubles_the_first_plan(row) == (
            rid == "proto_kk_nereids_ascension"), rid
