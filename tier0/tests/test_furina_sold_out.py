"""FURINA, THE STAGE -- SOLD OUT, THE FOURTH SEAT (the supporting pool,
2026-09-26, family 7 of `review/active/furina-supporting-pool-2026-09-26.md`),
the sim engine's pins.

"Your stage has a fourth seat." Front, two middles, back, for the rest of the
combat; a second copy adds nothing. Every rule that meets a full stage asks
`furina_stage.capacity`, so rule 3's recast, Wriothesley's front-join, the
returns and Full House all meet it at four. The C# twin's pins are
`klee-mod/KleeTests/Prototype/FurinaStageSoldOutTests.cs`.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest
import yaml

from tier0.content import loader
from tier0.engine import effects, furina_stage
from tier0.engine.state import Card, CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _furina(**kw):
    return Player(hp=200, max_hp=200, fanfare_cap=99, character_id="furina",
                  **kw)


def _state(stage=(), sold_out=True, seed=0):
    st = CombatState(player=_furina(),
                     enemies=[Enemy(hp=500, max_hp=500, name="paper",
                                    intents=[{"kind": "block", "amount": 0}])],
                     rng=random.Random(seed))
    st.turn = 2
    st.player.stage = [list(pair) for pair in stage]
    if sold_out:
        st.player.powers[FS.SOLD_OUT] = 1
    return st


def _card(effects_, cid="probe", type_="skill"):
    return Card(id=cid, name=cid, cost=1, type=type_, rarity="common",
                effects=effects_)


def _summon(member):
    return _card([{"op": "stage_summon", "member": member}])


def _row():
    rows = yaml.safe_load((loader.DOCS_DIR / "prototype-surface.yaml")
                          .read_text(encoding="utf-8"))
    return {r["id"]: r for r in rows}


# ---------------------------------------------------------------------------
# The row and the pool.
# ---------------------------------------------------------------------------

def test_the_row_is_the_papers():
    rows = _row()
    row = rows["proto_fs_sold_out"]
    assert (row["name"], row["rarity"], row["type"], row["cost"]) == (
        "Sold Out", "rare", "power", 2)
    assert row["upgrade"] == {"cost": -1}
    assert row["description"] == "Your stage has a fourth seat."
    assert row["effects"] == [{"op": "apply_power", "power": FS.SOLD_OUT,
                               "amount": 1, "target": "self"}]
    # Full House's face says every seat, not all three.
    assert rows["proto_fs_full_house"]["description"] == (
        "If every seat is filled at the end of your turn, your performers "
        "act twice.")


def test_sold_out_replaces_a_dropped_rare_power():
    assert FS.POOL_SUBS["unheard_confession"] == "proto_fs_sold_out"
    shipped = {r["id"]: r for r in yaml.safe_load(
        (loader.DOCS_DIR / "furina-cards.yaml").read_text(encoding="utf-8"))}
    assert (shipped["unheard_confession"]["rarity"],
            shipped["unheard_confession"]["type"]) == ("rare", "power")


# ---------------------------------------------------------------------------
# The capacity.
# ---------------------------------------------------------------------------

def test_capacity_is_three_and_four_under_the_power(arm):
    assert FS.SEATS == 3 and FS.SOLD_OUT_SEATS == 4
    assert FS.capacity(_state(sold_out=False).player) == 3
    assert FS.capacity(_state().player) == 4


def test_a_second_copy_opens_no_fifth_seat(arm):
    st = _state()
    st.player.powers[FS.SOLD_OUT] = 2
    assert FS.capacity(st.player) == 4


def test_capacity_with_the_arm_off_is_three(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", False)
    assert FS.capacity(_state().player) == FS.SEATS


def test_the_card_opens_the_fourth_seat(arm):
    st = _state(sold_out=False)
    effects.resolve_card(st, _card(
        [{"op": "apply_power", "power": FS.SOLD_OUT, "amount": 1,
          "target": "self"}], type_="power"))
    assert FS.capacity(st.player) == 4


# ---------------------------------------------------------------------------
# Rule 3 at four.
# ---------------------------------------------------------------------------

def test_a_fourth_summon_takes_the_fourth_seat(arm):
    st = _state([["usher", 3], ["chevalmarin", 1], ["crabaletta", 1]])
    effects.resolve_card(st, _summon("usher"))
    assert st.player.stage == [["usher", 3], ["chevalmarin", 1],
                               ["crabaletta", 1], ["usher", 1]]
    # No Bow: nobody left.
    assert not [e for e in st.log if e["event"] == "stage_leave"]


def test_a_summon_on_a_full_four_stage_recasts_the_front(arm):
    st = _state([["usher", 6], ["chevalmarin", 2], ["crabaletta", 3],
                 ["usher", 4]])
    effects.resolve_card(st, _summon("crabaletta"))
    # The lead Bows (Usher's act, 3 Block) and leaves; the newcomer takes
    # the fourth seat holding the lead's 6 plus its own 1.
    assert st.player.stage == [["chevalmarin", 2], ["crabaletta", 3],
                               ["usher", 4], ["crabaletta", 7]]
    assert st.player.block == FS.ACT_USHER_BLOCK


def test_without_sold_out_the_third_summon_still_fills_the_stage(arm):
    st = _state([["usher", 6], ["chevalmarin", 2], ["crabaletta", 3]],
                sold_out=False)
    effects.resolve_card(st, _summon("usher"))
    assert st.player.stage == [["chevalmarin", 2], ["crabaletta", 3],
                               ["usher", 7]]


# ---------------------------------------------------------------------------
# Wriothesley's front-join at four.
# ---------------------------------------------------------------------------

def test_wriothesley_joins_a_full_four_stage_and_the_back_leaves(arm):
    st = _state([["usher", 3], ["chevalmarin", 2], ["crabaletta", 2],
                 ["usher", 5]])
    FS.guest_star(st, "wriothesley", 8, front=True)
    # The back Usher Bows (3 Block) and leaves; he arrives at the front with
    # his 8 plus its 5, and the other three shift back one.
    assert st.player.stage == [["wriothesley", 13], ["usher", 3],
                               ["chevalmarin", 2], ["crabaletta", 2]]
    assert st.player.block == FS.ACT_USHER_BLOCK


def test_wriothesley_joins_three_under_sold_out_without_a_recast(arm):
    st = _state([["usher", 3], ["chevalmarin", 2], ["crabaletta", 2]])
    FS.guest_star(st, "wriothesley", 8, front=True)
    assert st.player.stage == [["wriothesley", 8], ["usher", 3],
                               ["chevalmarin", 2], ["crabaletta", 2]]
    assert st.player.block == 0


# ---------------------------------------------------------------------------
# Full House needs every seat.
# ---------------------------------------------------------------------------

def test_full_house_needs_four_under_sold_out(arm):
    three = _state([["usher", 1], ["chevalmarin", 1], ["crabaletta", 1]])
    three.player.powers[FS.FULL_HOUSE] = 1
    FS.end_of_turn_acts(three)
    assert three.player.block == FS.ACT_USHER_BLOCK

    four = _state([["usher", 1], ["chevalmarin", 1], ["crabaletta", 1],
                   ["crabaletta", 1]])
    four.player.powers[FS.FULL_HOUSE] = 1
    FS.end_of_turn_acts(four)
    assert four.player.block == 2 * FS.ACT_USHER_BLOCK


# ---------------------------------------------------------------------------
# The fade reaches both middles.
# ---------------------------------------------------------------------------

def test_both_middles_and_the_back_fade_and_the_front_does_not(arm):
    st = _state([["usher", 9], ["chevalmarin", 9], ["crabaletta", 11],
                 ["usher", 7]])
    FS.fade(st)
    assert [f for _m, f in st.player.stage] == [9, 7, 8, 6]


# ---------------------------------------------------------------------------
# The returns meet a full stage at four.
# ---------------------------------------------------------------------------

def test_a_five_century_return_finds_the_fourth_seat(arm):
    st = _state([["usher", 3], ["chevalmarin", 1], ["crabaletta", 1]])
    st.player.powers[FS.FIVE_CENTURY_ACT] = 1
    FS._after_bow(st, "usher", may_return=True)
    assert st.player.stage[-1] == ["usher", FS.SUMMON_FANFARE]
    assert len(st.player.stage) == 4
