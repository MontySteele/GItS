"""FURINA, THE STAGE -- THE GUEST CAST (2026-09-25), the sim engine's pins.

The design is `review/active/furina-guest-batch-2026-09-25.md` (ruled that
evening), with two rulings after it: NO GUEST CAP ([USER]: "why not just let
the Stage be filled with guest stars if the player wants?") and ONE OF EACH
GUEST ("only one Neuvillette allowed - repeats trigger a Bow and then resummon
them, carrying over unused Fanfare"). The C# twin's pins are
`klee-mod/KleeTests/Prototype/FurinaGuestCastTests.cs`, and the SCRIPTED
BOARDS below are shared with it word for word: the mod's forecast is pinned
to the numbers this engine's actual end of turn produces.

WHAT IS PINNED, in the frame's order:

  1. the eight rows, their faces and their numbers;
  2. arrival: an empty seat, a full stage's recast, and a repeat's Bow;
  4. every act pays, an act that cannot pay does nothing, a payment that
     empties a performer ends in its Bow after the act;
  5. the Bow is free;
  6. Wriothesley's reading resets;
  7. the forecast is the actual end of turn, and never touches the state.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import copy
import random

import pytest

from tier0.content import loader
from tier0.engine import combat, effects, furina_stage
from tier0.engine.state import Card, CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _furina(**kw):
    return Player(hp=200, max_hp=200, fanfare_cap=99, character_id="furina",
                  **kw)


def _enemy(hp=500, intents=None, name="paper"):
    return Enemy(hp=hp, max_hp=hp, name=name,
                 intents=intents or [{"kind": "block", "amount": 0}])


def _state(stage=(), enemies=None, seed=0):
    st = CombatState(player=_furina(), enemies=enemies or [_enemy()],
                     rng=random.Random(seed))
    st.turn = 2
    st.player.stage = [list(pair) for pair in stage]
    return st


def _card(effects_, cid="probe"):
    return Card(id=cid, name=cid, cost=1, type="skill", rarity="common",
                effects=effects_)


def _guest(member, amount):
    return _card([{"op": "stage_guest", "member": member, "amount": amount}])


def _guest_front(member, amount):
    """A Guest Star whose card puts the guest in the FRONT seat."""
    return _card([{"op": "stage_guest", "member": member, "amount": amount,
                   "seat": "front"}])


def _rows():
    import yaml
    rows = yaml.safe_load(
        (loader.DOCS_DIR / "prototype-surface.yaml").read_text(
            encoding="utf-8"))
    # The Guest Cast's eight; THE SUPPORTING POOL's two (2026-09-26) are
    # pinned in `test_furina_supporting_pool.py`.
    return {r["id"]: r for r in rows
            if r["id"].startswith("proto_fs_guest_star_")
            and r["id"] not in ("proto_fs_guest_star_lyney",
                                "proto_fs_guest_star_escoffier")}


# ---------------------------------------------------------------------------
# 1. THE EIGHT ROWS.
# ---------------------------------------------------------------------------

#: The build table: (name, rarity, cost, arrives with, upgrade).
TABLE = {
    "neuvillette": ("Neuvillette", "rare", 2, 6, {"cost": -1}),
    "clorinde": ("Clorinde", "rare", 1, 4, {"stage_guest": 2}),
    "navia": ("Navia", "rare", 1, 4, {"stage_guest": 2}),
    "chevreuse": ("Chevreuse", "uncommon", 1, 4, {"stage_guest": 2}),
    "wriothesley": ("Wriothesley", "uncommon", 1, 8, {"stage_guest": 2}),
    "sigewinne": ("Sigewinne", "uncommon", 1, 8, {"stage_guest": 2}),
    "charlotte": ("Charlotte", "uncommon", 1, 4, {"stage_guest": 2}),
    "lynette": ("Lynette", "uncommon", 1, 8, {"stage_guest": 2}),
}


#: The guests whose card puts them in the FRONT seat (the guest seat round,
#: 2026-09-25: "he joins at the back, where hits never reach him, so his act
#: lands nothing").
FRONT = {"wriothesley"}


def test_the_eight_rows_are_the_build_tables():
    rows = _rows()
    assert sorted(rows) == sorted(f"proto_fs_guest_star_{m}" for m in TABLE)
    for member, (name, rarity, cost, n, upgrade) in TABLE.items():
        row = rows[f"proto_fs_guest_star_{member}"]
        assert row["name"] == f"Guest Star: {name}"
        assert (row["rarity"], row["cost"], row["type"]) == (
            rarity, cost, "skill")
        assert row["register"] == "salon"
        # The guest seat round (2026-09-25): Wriothesley joins at the front.
        where = " at the front" if member in FRONT else ""
        assert row["description"] == (
            f"{name} joins the stage{where} with {n} [gold]Fanfare[/gold].")
        effect = {"op": "stage_guest", "member": member, "amount": n}
        if member in FRONT:
            effect["seat"] = "front"
        assert row["effects"] == [effect]
        assert row["upgrade"] == upgrade


def test_the_guests_join_the_arms_pool_in_the_sim():
    named = set(FS.POOL_SUBS.values())
    assert {f"proto_fs_guest_star_{m}" for m in TABLE} <= named
    # THE SUPPORTING POOL (2026-09-26) added Lyney and Escoffier.
    assert set(FS.GUESTS) == set(TABLE) | {"lyney", "escoffier"}


# ---------------------------------------------------------------------------
# 2. ARRIVAL.
# ---------------------------------------------------------------------------

def test_a_guest_takes_the_back_most_empty_seat_holding_its_fanfare(arm):
    st = _state([["usher", 3]])
    effects.resolve_card(st, _guest("clorinde", 4))
    assert st.player.stage == [["usher", 3], ["clorinde", 4]]
    # It does not act on arrival (`EB-738`).
    assert not [e for e in st.log if e["event"] == "stage_act"]


def test_guests_may_fill_all_three_seats(arm):
    """No guest cap (2026-09-25)."""
    st = _state()
    for member, n in (("neuvillette", 6), ("clorinde", 4), ("navia", 4)):
        effects.resolve_card(st, _guest(member, n))
    assert st.player.stage == [["neuvillette", 6], ["clorinde", 4],
                               ["navia", 4]]


def test_a_guest_on_a_full_stage_recasts_the_front(arm):
    """The front Bows (its act) and leaves; the guest arrives at the back
    holding its own N PLUS the front's remaining Fanfare, like any summon
    (2026-09-25: the recast adds, so a guest cast onto a front at 1 does not
    arrive unable to pay)."""
    st = _state([["usher", 5], ["chevalmarin", 2], ["crabaletta", 4]])
    effects.resolve_card(st, _guest("navia", 4))
    assert st.player.block == FS.ACT_USHER_BLOCK          # Usher's Bow
    assert st.player.stage == [["chevalmarin", 2], ["crabaletta", 4],
                               ["navia", 4 + 5]]
    st = _state([["usher", 1], ["chevalmarin", 2], ["crabaletta", 4]])
    effects.resolve_card(st, _guest("neuvillette", 6))
    assert st.player.stage[-1] == ["neuvillette", 6 + 1]


def test_wriothesley_joins_at_the_front_and_takes_the_next_hit(arm):
    """The guest seat round (2026-09-25): played onto a two-performer stage
    he stands in FRONT, the others shift back one, and the next hit is his."""
    st = _state([["usher", 3], ["crabaletta", 4]])
    effects.resolve_card(st, _guest_front("wriothesley", 8))
    assert st.player.stage == [["wriothesley", 8], ["usher", 3],
                               ["crabaletta", 4]]
    hp = st.player.hp
    FS.absorb(st, 5)
    FS.settle_hit(st)
    assert st.player.stage[0] == ["wriothesley", 3]
    assert st.player.stage[1:] == [["usher", 3], ["crabaletta", 4]]
    assert st.player.hp == hp
    # And his act reads what that hit took: twice 5.
    st.enemies = [_enemy(hp=100)]
    FS.perform(st, "wriothesley")
    assert st.enemies[0].hp == 100 - 2 * 5


def test_wriothesley_on_a_full_stage_recasts_the_back(arm):
    """The recast rule, the leaver at the other end: the BACK performer Bows
    and leaves, and he arrives at the front holding 8 plus its Fanfare."""
    st = _state([["usher", 5], ["chevalmarin", 2], ["crabaletta", 4]],
                enemies=[_enemy(hp=100)])
    effects.resolve_card(st, _guest_front("wriothesley", 8))
    assert st.player.stage == [["wriothesley", 8 + 4], ["usher", 5],
                               ["chevalmarin", 2]]
    # Crabaletta's Bow is her act.
    assert st.enemies[0].hp == 100 - FS.ACT_CRABALETTA_DAMAGE
    leave = [e for e in st.log if e["event"] == "stage_leave"]
    assert (leave[-1]["member"], leave[-1]["reason"]) == (
        "crabaletta", "recast")


def test_a_repeat_wriothesley_returns_to_his_own_seat(arm):
    """A second copy is unchanged: he Bows and returns to the seat he had."""
    st = _state([["usher", 3], ["wriothesley", 2]], enemies=[_enemy(hp=100)])
    effects.resolve_card(st, _guest_front("wriothesley", 8))
    assert st.player.stage == [["usher", 3], ["wriothesley", 10]]


def test_the_forecast_puts_the_hit_on_a_front_wriothesley(arm):
    """The forecast reads the stage the card left: past Usher's 3 Block,
    the hit goes to him and none of it to her."""
    st = _state([["usher", 3], ["crabaletta", 4]],
                enemies=[_attack_enemy([9])])
    effects.resolve_card(st, _guest_front("wriothesley", 8))
    forecast = FS.forecast(st)
    assert forecast["after"][0][0] == "wriothesley"
    assert forecast["front_takes"] == 9 - FS.ACT_USHER_BLOCK
    assert forecast["reaches_furina"] == 0


def test_a_second_copy_bows_the_guest_and_returns_it_with_the_fanfare_added(
        arm):
    """One of each guest: its Bow (free), then the same seat, its unused
    Fanfare plus the card's."""
    st = _state([["navia", 5], ["usher", 3]], enemies=[_enemy(hp=100)])
    effects.resolve_card(st, _guest("navia", 4))
    assert st.player.stage == [["navia", 9], ["usher", 3]]
    # Her Bow is her act: Geo damage equal to the Fanfare she held.
    assert st.enemies[0].hp == 100 - 5
    leave = [e for e in st.log if e["event"] == "stage_leave"]
    assert leave[-1]["reason"] == "repeat"


# ---------------------------------------------------------------------------
# 4. EVERY ACT PAYS.
# ---------------------------------------------------------------------------

def test_neuvillette_pays_three_of_his_own_for_eight_hydro_to_all(arm):
    st = _state([["neuvillette", 6]],
                enemies=[_enemy(hp=100), _enemy(hp=100)])
    FS.perform(st, "neuvillette")
    assert st.player.stage == [["neuvillette", 3]]
    assert [e.hp for e in st.enemies] == [92, 92]
    assert all(e.aura == "hydro" for e in st.enemies)
    assert st.stage_ledger["paid_other"] == {"neuvillette": 3}


def test_an_act_that_cannot_pay_does_nothing(arm):
    st = _state([["neuvillette", 2]], enemies=[_enemy(hp=100)])
    FS.perform(st, "neuvillette")
    assert st.player.stage == [["neuvillette", 2]]
    assert st.enemies[0].hp == 100
    assert st.stage_ledger["unpaid"] == {"neuvillette": 1}
    assert [e for e in st.log if e["event"] == "stage_unpaid"]


def test_a_payment_that_empties_the_payer_ends_in_its_free_bow(arm):
    """Pay, then the act, then the Bow: Neuvillette at 3 pays his last 3,
    deals 8, leaves, and his Bow deals 8 more without paying."""
    st = _state([["neuvillette", 3]], enemies=[_enemy(hp=100)])
    FS.perform(st, "neuvillette")
    assert st.player.stage == []
    assert st.enemies[0].hp == 100 - 16
    events = [e["event"] for e in st.log
              if e["event"] in ("stage_pay", "stage_leave", "stage_bow")]
    assert events == ["stage_pay", "stage_leave", "stage_bow"]


def test_clorinde_taxes_each_other_performer_and_a_taxed_out_one_bows(arm):
    st = _state([["clorinde", 4], ["usher", 1], ["crabaletta", 3]],
                enemies=[_enemy(hp=100)])
    FS.perform(st, "clorinde")
    # Usher paid his last 1, left, and Bowed for 3 Block after her hit.
    assert st.player.stage == [["clorinde", 4], ["crabaletta", 2]]
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert st.enemies[0].hp == 100 - FS.ACT_CLORINDE_DAMAGE
    assert st.enemies[0].aura == "electro"
    assert st.stage_ledger["paid_other"] == {"clorinde": 2}


def test_clorinde_alone_cannot_pay(arm):
    st = _state([["clorinde", 4]], enemies=[_enemy(hp=100)])
    FS.perform(st, "clorinde")
    assert st.enemies[0].hp == 100
    assert st.stage_ledger["unpaid"] == {"clorinde": 1}


def test_chevreuse_spends_two_from_the_back_for_energy_next_turn(arm):
    st = _state([["chevreuse", 4], ["usher", 5]])
    FS.perform(st, "chevreuse")
    assert st.player.stage == [["chevreuse", 4], ["usher", 3]]
    assert st.player.stage_energy_next == FS.ACT_CHEVREUSE_ENERGY
    energy = st.player.energy
    FS.turn_start_powers(st)
    assert st.player.energy == energy + FS.ACT_CHEVREUSE_ENERGY
    assert st.player.stage_energy_next == 0


def test_sigewinne_gives_behind_her_or_wraps_to_the_front(arm):
    mid = _state([["usher", 2], ["sigewinne", 8], ["navia", 1]])
    FS.perform(mid, "sigewinne")
    assert mid.player.stage == [["usher", 2], ["sigewinne", 5], ["navia", 4]]
    back = _state([["usher", 2], ["sigewinne", 8]])
    FS.perform(back, "sigewinne")
    assert back.player.stage == [["usher", 5], ["sigewinne", 5]]
    alone = _state([["sigewinne", 8]])
    FS.perform(alone, "sigewinne")
    assert alone.player.stage == [["sigewinne", 8]]


def test_sigewinne_gives_what_she_has_and_her_bow_gives_the_whole_gift(arm):
    st = _state([["usher", 2], ["sigewinne", 2]])
    FS.perform(st, "sigewinne")
    # 2 given (all she had), she leaves, and her free Bow gives 3 more.
    assert st.player.stage == [["usher", 2 + 2 + 3]]


def test_charlotte_gives_each_other_performer_one(arm):
    st = _state([["usher", 2], ["charlotte", 4], ["navia", 1]])
    FS.perform(st, "charlotte")
    assert st.player.stage == [["usher", 3], ["charlotte", 4], ["navia", 2]]


def test_lynette_swirls_an_enemy_with_an_aura_and_nothing_without_one(arm):
    st = _state([["lynette", 8]], enemies=[_enemy(hp=100), _enemy(hp=100)])
    FS.perform(st, "lynette")
    assert [e.aura for e in st.enemies] == [None, None]
    st.enemies[0].aura = "pyro"
    FS.perform(st, "lynette")
    # Swirl: the aura is consumed and copied onto ALL enemies.
    assert st.enemies[1].aura == "pyro"


def test_full_house_makes_each_act_pay_again(arm):
    """Rule 4: a repeated act pays each time. Neuvillette at 6 under Full
    House pays twice, empties, and Bows once."""
    st = _state([["neuvillette", 6], ["usher", 3], ["crabaletta", 4]],
                enemies=[_enemy(hp=200)])
    st.player.powers[FS.FULL_HOUSE] = 1
    FS.end_of_turn_acts(st)
    assert [m for m, _f in st.player.stage] == ["usher", "crabaletta"]
    bows = [e["member"] for e in st.log if e["event"] == "stage_bow"]
    assert bows == ["neuvillette"]


def test_bis_makes_a_guest_pay_twice_and_stops_when_it_leaves(arm):
    """2026-09-26 balance review, Bis! acts twice: a guest's act pays each
    time; a guest that paid its last Fanfare on the first act has left, so
    the second act does not happen and the performer behind does not take
    it."""
    rich = _state([["neuvillette", 6], ["usher", 3]],
                  enemies=[_enemy(hp=100)])
    FS.perform_lead(rich, 2)
    assert rich.stage_ledger["paid_other"] == {"neuvillette": 6}
    assert rich.enemies[0].hp == 100 - 3 * 8           # two acts and a Bow
    assert [m for m, _f in rich.player.stage] == ["usher"]
    poor = _state([["neuvillette", 3], ["usher", 3]],
                  enemies=[_enemy(hp=100)])
    FS.perform_lead(poor, 2)
    assert poor.enemies[0].hp == 100 - 2 * 8           # one act and a Bow
    assert poor.player.block == 0                      # Usher never acted
    assert [m for m, _f in poor.player.stage] == ["usher"]


# ---------------------------------------------------------------------------
# 5-6. THE FREE BOW, AND WRIOTHESLEY'S READING.
# ---------------------------------------------------------------------------

def test_a_hit_emptying_a_guest_bows_it_right_away_and_free(arm):
    """The Bow comes right after the hit, on the enemy's turn ([USER],
    2026-09-25), and a guest's Bow pays nothing: Neuvillette at 2 is hit
    empty and his Bow still deals 8 to ALL."""
    player = _furina()
    player.stage = [["neuvillette", 2], ["usher", 3]]
    st = CombatState(player=player, enemies=[
        _enemy(hp=100, intents=[{"kind": "attack", "amount": 2}])],
        rng=random.Random(0))
    st.turn = 2
    combat._enemy_turn(st, st.enemies[0])
    assert player.stage == [["usher", 3]]
    assert st.enemies[0].hp == 100 - FS.ACT_NEUVILLETTE_DAMAGE


def test_wriothesley_reads_what_he_lost_and_a_repeat_reads_zero(arm):
    st = _state([["wriothesley", 8], ["usher", 3]], enemies=[_enemy(hp=100)])
    FS.absorb(st, 3)                               # he loses 3 to a hit
    FS.perform(st, "wriothesley")
    assert st.enemies[0].hp == 100 - 2 * 3
    FS.perform(st, "wriothesley")                  # a repeat reads 0
    assert st.enemies[0].hp == 100 - 2 * 3


def test_wriothesley_counts_hits_only(arm):
    """2026-09-25: he is the tank, not a Spend engine. A Spend off his bar
    and the fade take Fanfare and do not count; a hit does."""
    st = _state([["usher", 3], ["wriothesley", 10]],
                enemies=[_enemy(hp=100)])
    FS.spend(st, 2)                                # he is the back: 10 -> 8
    FS.fade(st)                                    # 8 -> 7
    FS.perform(st, "wriothesley")
    assert st.enemies[0].hp == 100
    st.player.stage.reverse()                      # he steps to the front
    FS.absorb(st, 2)
    FS.perform(st, "wriothesley")
    assert st.enemies[0].hp == 100 - 2 * 2


def test_wriothesleys_bow_on_a_hit_reads_the_hit_that_took_him_down(arm):
    st = _state([["wriothesley", 4], ["usher", 3]], enemies=[_enemy(hp=100)])
    FS.absorb(st, 9)
    FS.settle_hit(st)
    assert st.enemies[0].hp == 100 - 2 * 4


# ---------------------------------------------------------------------------
# 7. THE FORECAST -- SHARED SCRIPTED BOARDS.
#
# Each board: the stage, Full House copies, the posted hits (per hit), and
# the expected end of turn: each seat's bar after (None where it leaves), the
# Block after the acts, what the front performers take and what reaches
# Furina. `FurinaGuestCastTests.cs` carries the same table for the mod's
# forecast, so the two engines are pinned to one set of numbers.
# ---------------------------------------------------------------------------

BOARDS = [
    ("neuvillette pays", [["neuvillette", 6], ["usher", 3]], 0, [],
     [3, 3], 3, 0, 0),
    ("tax and gift", [["usher", 3], ["clorinde", 4], ["charlotte", 4]], 0,
     [], [3, 5, 3], 3, 0, 0),
    ("the last payment bows",
     [["neuvillette", 3], ["sigewinne", 8]], 0, [], [None, 8], 0, 0, 0),
    ("a gift wraps to the front", [["usher", 2], ["sigewinne", 8]], 0, [],
     [5, 5], 3, 0, 0),
    ("chevreuse spends herself", [["usher", 3], ["chevreuse", 4]], 0, [],
     [3, 2], 3, 0, 0),
    ("chevreuse cannot pay", [["chevreuse", 4], ["usher", 1]], 0, [],
     [4, 1], 3, 0, 0),
    ("full house pays twice",
     [["neuvillette", 6], ["usher", 3], ["crabaletta", 4]], 1, [],
     [None, 3, 4], 6, 0, 0),
    ("the fade is not a hit", [["usher", 3], ["wriothesley", 10]], 0, [],
     [3, 8], 3, 0, 0),
    ("two hits through the front",
     [["usher", 3], ["crabaletta", 4]], 0, [7, 7], [3, 4], 3, 7, 1),
]


def _attack_enemy(hits):
    if not hits:
        return _enemy(hp=500)
    assert len(set(hits)) == 1
    return _enemy(hp=500, intents=[{"kind": "attack", "amount": hits[0],
                                    "times": len(hits)}])


@pytest.mark.parametrize("board", BOARDS, ids=[b[0] for b in BOARDS])
def test_the_forecast_is_the_actual_end_of_turn(arm, board):
    _name, stage, full_house, hits, after, block, front, you = board
    st = _state(stage, enemies=[_attack_enemy(hits)])
    st.player.powers[FS.FULL_HOUSE] = full_house
    before = copy.deepcopy(st.player.stage)
    forecast = FS.forecast(st)
    # PURE: the real state has not moved.
    assert st.player.stage == before and st.player.block == 0
    # The actual end of turn, on the real state.
    seats = list(st.player.stage)
    FS.end_of_turn_acts(st)
    actual = [pair[1] if any(p is pair for p in st.player.stage) else None
              for pair in seats]
    assert actual == after
    assert st.player.block == block
    assert forecast["block_after_acts"] == block
    assert forecast["front_takes"] == front
    assert forecast["reaches_furina"] == you
    # And the forecast's bars are the actual bars, seat for seat.
    assert [f for _m, f in forecast["after"]] == [
        f for _m, f in st.player.stage]
    # The hits, actually dealt.
    hp = st.player.hp
    absorbed_before = sum(e.get("amount", 0) for e in st.log
                          if e["event"] == "stage_absorb")
    combat._enemy_turn(st, st.enemies[0])
    absorbed = sum(e.get("amount", 0) for e in st.log
                   if e["event"] == "stage_absorb") - absorbed_before
    assert absorbed == front
    assert hp - st.player.hp == you


def test_the_ledger_balances_with_guests(arm):
    """start + gained - spent - paid_other - left - faded - hit == end, with
    arrivals, a repeat, taxes, gifts and a free Bow in the fight."""
    st = _state([["usher", 3]], enemies=[_enemy(hp=500)])
    FS.ledger(st)
    for card in (_guest("clorinde", 4), _guest("charlotte", 4),
                 _guest("clorinde", 6)):
        effects.resolve_card(st, card)
    FS.end_of_turn_acts(st)
    FS.absorb(st, 2)
    FS.settle_hit(st)
    led = st.stage_ledger
    assert FS.ledger_expected_end(led) == FS.total_fanfare(st.player)
    assert led["gained"]["guest"] == 4 + 4 + 6
    assert led["paid_other"].get("clorinde", 0) > 0


# ---------------------------------------------------------------------------
# THE SEAT PAGE: payments, a failed payment, the forecast, and the glossary.
# ---------------------------------------------------------------------------

def _row(event, member, name, **kw):
    row = {"event": event, "member": member, "name": name, "seat": 0,
           "fanfare": 0, "moved": 0, "reason": "", "target": "",
           "target_id": "", "each": -1, "hp": -1, "struck": -1, "by": "",
           "by_member": ""}
    row.update(kw)
    return row


def _stage(log=(), forecast=None, seats=()):
    from understudy.blindplay_board import furina_stage
    raw = {"live": True, "seats": list(seats), "log": list(log)}
    if forecast is not None:
        raw["forecast"] = forecast
    return furina_stage({"furina_stage": raw})


def test_the_log_prints_each_payment_and_a_failed_one():
    from understudy.blindplay_render import _render_stage_log
    stage = _stage([
        _row("pay", "neuvillette", "Neuvillette", fanfare=3, moved=3,
             by="Neuvillette", by_member="neuvillette"),
        _row("pay", "usher", "Gentilhomme Usher", fanfare=2, moved=1,
             by="Clorinde", by_member="clorinde"),
        _row("unpaid", "chevreuse", "Chevreuse", fanfare=4),
    ])
    assert _render_stage_log(stage) == [
        "  - **Neuvillette** paid 3 of his Fanfare: 6 → 3.",
        "  - **Clorinde** took 1 of **Usher**'s Fanfare: 3 → 2.",
        "  - **Chevreuse** could not pay.",
    ]


def test_the_page_prints_the_mods_forecast():
    from understudy.blindplay_render import _render_stage
    forecast = {
        "seats": [{"member": "neuvillette", "name": "Neuvillette", "now": 6,
                   "after": 3, "leaves": False},
                  {"member": "usher", "name": "Gentilhomme Usher", "now": 3,
                   "after": 0, "leaves": True}],
        "arrivals": [], "block_after_acts": 3, "intent_known": True,
        "front_takes": 4, "reaches_furina": 2, "unknown": False}
    lines = _render_stage(
        _stage(forecast=forecast,
               seats=[{"member": "neuvillette", "name": "Neuvillette",
                       "seat": 0, "fanfare": 6},
                      {"member": "usher", "name": "Gentilhomme Usher",
                       "seat": 1, "fanfare": 3}]),
        {"block": 0, "hp": 50, "max_hp": 78})
    assert ("- At the end of your turn: **Neuvillette** 6 → 3 · **Usher** "
            "3 → 0 (leaves).") in lines
    assert ("- The attacks shown, after the acts' Block of 3: your front "
            "performer takes 4, you take 2.") in lines


def test_the_new_beats_cross_the_blind_packet():
    """#674's leak test: every event word is one plain word, and the pay
    beat's actor is a name, never an id."""
    from understudy import qa_packet
    from understudy.blindplay_board import stage_event
    for word in ("pay", "unpaid"):
        assert stage_event(word) == word
    stage = _stage([_row("pay", "usher", "Gentilhomme Usher", fanfare=2,
                         moved=1, by="Clorinde", by_member="clorinde")])
    assert stage["log"][0]["by"] == "Clorinde"
    assert qa_packet.leaks(stage) == []


def test_the_glossary_has_the_guest_star_and_every_guest_word_for_word():
    from understudy.blindplay_notes import ARM_KEYWORDS
    assert ARM_KEYWORDS["Guest Star"] == (
        "A performer who joins the stage, one of each. A second copy makes "
        "it Bow, then return with the new Fanfare added.")
    assert ARM_KEYWORDS["Bow"] == (
        "A performer that leaves the stage acts one last time on its way "
        "out, without paying. A performer emptied by a hit Bows before the "
        "rest of that hit reaches you.")
    assert ARM_KEYWORDS["Neuvillette"] == (
        "End of your turn: pay 3 of his Fanfare to deal 8 Hydro damage to "
        "ALL enemies.")
    assert ARM_KEYWORDS["Sigewinne"] == (
        "End of your turn: give 3 of her Fanfare to the performer behind "
        "her, or to your front performer if she is at the back.")
    for guest in ("Clorinde", "Navia", "Chevreuse", "Wriothesley",
                  "Charlotte", "Lynette"):
        assert ARM_KEYWORDS[guest].startswith("End of your turn: ")


def test_a_guest_star_face_raises_its_rows_and_a_companion_title_does_not():
    from understudy.blindplay_notes import keyword_notes
    obs = {"state_type": "card_reward", "character": "Furina",
           "stage_arm": True,
           "player": {"character": "Furina",
                      "relics": [{"name": "Salon Solitaire"}]},
           "card_reward": {"cards": [{
               "name": "Guest Star: Neuvillette",
               "description": "Neuvillette joins the stage with 6 Fanfare."}]}}
    names = {row["name"] for row in keyword_notes(obs)}
    assert {"Guest Star", "Neuvillette"} <= names
    obs["card_reward"]["cards"] = [{
        "name": "Neuvillette — O Tears, I Shall Repay",
        "description": "Deal 7 damage. Neuvillette — the name, dashed."}]
    assert "Neuvillette" not in {row["name"] for row in keyword_notes(obs)}


def test_the_report_prints_the_guest_casts_measures(arm):
    """`tools/furina_stage_report.py` report 7: per guest, acts that could
    not pay, turns on stage and Fanfare paid; per fight, the damage that
    reached Furina."""
    import io
    from tier0.pilot.policy import make_pilot
    from tools import furina_stage_report as report
    pilot = make_pilot(loader.pilot_weights("salon"))
    states = [combat.run_fight(
        loader.build_player_from_ids("furina", report.BASICS + report.STAR),
        loader.build_encounter("attrition"), pilot, seed=seed)
        for seed in range(4)]
    out = io.StringIO()
    row = report.guest_cast(states, out=out)
    text = out.getvalue()
    assert "7. The Guest Cast:" in text
    assert "damage reaching Furina" in text
    assert "neuvillette" in text and "acts unpaid" in text
    assert "Fanfare paid" in text
    assert set(row) >= {"to_her", "dealt", "turns", "fh_fired"}
    labels = dict(report.ARMS)
    for deck in ("guest star", "guest tank", "3 crabalettas",
                 "3 crabalettas + full house", "3 ushers"):
        assert deck in labels
