"""FURINA, THE STAGE -- the fixes from the granted-guest seat round
(2026-09-25 night, 0.2.3809+proto), the sim's and the page's pins.

Seat records: lane 1 and lane 2 of the granted-guest round. The mod's pins are
`klee-mod/KleeTests/Prototype/FurinaGuestGrantedFixTests.cs`, whose scripted
boards are the boards below: the forecast there is pinned to what the sim's
ACTUAL end of turn and enemy turn produce here.

  1. A Bow on a killing hit lands before the rest of that hit reaches Furina
     (brief rules 6 and 7): Usher's Bow Block catches the overflow.
  2. The forecast: what the acts deal, the attacks' split hit by hit, one
     Block number.
  3. The seat log: a one-body act prints its hit, an arrival names the seat
     it took, the reaction glossary counts guests.
  4. Text: the Summon tip; the performer rider on Weak, Shrink and Strength.
  5. Lynette's act always lands.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
"""
from __future__ import annotations

import pytest

from tier0.engine import combat, furina_stage
from tier0.tests.test_furina_guest_cast import _enemy, _state

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


# ---------------------------------------------------------------------------
# 1. The Bow lands inside the hit.
# ---------------------------------------------------------------------------

def test_usher_at_3_under_a_single_10_leaves_and_she_takes_4(arm):
    """The packet's own case: Usher at 3, a single 10, Furina at 0 Block. He
    takes 3 and leaves, his Bow's 3 Block takes 3 of the rest, and she takes
    10 - 3 - 3 = 4."""
    st = _state(stage=[["usher", 3]],
                enemies=[_enemy(hp=44,
                                intents=[{"kind": "attack", "amount": 10}])])
    player = st.player
    player.hp = player.max_hp = 78
    combat._enemy_turn(st, st.enemies[0])
    assert player.hp == 78 - 4
    assert player.block == 0
    assert player.stage == []


def test_a_multi_hit_meets_what_the_bow_block_left(arm):
    """Two hits of 5 into Usher 3 and Crabaletta 4, no Block: hit one empties
    Usher and his Bow Block takes the other 2 (1 left); hit two spends that 1
    and empties Crabaletta. Nothing reaches her. The mod's forecast of the
    same board names Usher 3 (leaves), then Crabaletta 4 (leaves)."""
    st = _state(stage=[["usher", 3], ["crabaletta", 4]], enemies=[_enemy(
        hp=44, intents=[{"kind": "attack", "amount": 5, "times": 2}])])
    player = st.player
    player.hp = player.max_hp = 78
    combat._enemy_turn(st, st.enemies[0])
    assert player.hp == 78
    absorbed = [(e["member"], e["amount"], e["fanfare"]) for e in st.log
                if e["event"] == "stage_absorb"]
    assert absorbed == [("usher", 3, 0), ("crabaletta", 4, 0)]


def test_the_sim_forecast_walks_the_hits_performer_by_performer(arm):
    st = _state(stage=[["usher", 3], ["crabaletta", 4]], enemies=[_enemy(
        hp=44, intents=[{"kind": "attack", "amount": 8},
                        ])])
    out = FS.forecast(st)
    # After the acts: Usher's 3 Block. The 8: Block 3, Usher 3 (leaves), and
    # his Bow Block catches the last 2.
    assert out["block_after_acts"] == FS.ACT_USHER_BLOCK
    assert out["takers"] == [["usher", 3, True]]
    assert out["reaches_furina"] == 0


# ---------------------------------------------------------------------------
# 2. What the acts deal: lane 2's Beetle, on the sim's actual end of turn.
# ---------------------------------------------------------------------------

def test_the_beetle_board_the_acts_deal_12(arm):
    """Lane 2, fight 3 turn 2: Crabaletta 1, Crabaletta 5, Chevalmarin 2
    against a 13-HP Shrinker Beetle, which ended the turn on 1. The mod's
    forecast prints 5, 5 and 2 and "In all: 12 to Shrinker Beetle"; the sim's
    actual end of turn takes 12."""
    st = _state(stage=[["crabaletta", 1], ["crabaletta", 5],
                       ["chevalmarin", 2]],
                enemies=[_enemy(hp=13, name="Shrinker Beetle")])
    assert FS.forecast(st)["acts_dealt"] == 12
    FS.end_of_turn_acts(st)
    assert st.enemies[0].hp == 1


# ---------------------------------------------------------------------------
# 5. Lynette's act always lands.
# ---------------------------------------------------------------------------

def test_lynettes_act_deals_3_anemo_to_a_body_with_an_aura(arm):
    bare = _enemy(hp=40, name="bare")
    wearing = _enemy(hp=40, name="wearing")
    wearing.aura, wearing.aura_turns_left = "hydro", 2
    st = _state(stage=[["lynette", 8]], enemies=[bare, wearing])
    FS.end_of_turn_acts(st)
    # The aura'd body, every time (the seed does not matter), for 3; and
    # Anemo onto Hydro Swirls it, copying the aura onto ALL enemies.
    assert wearing.hp == 40 - FS.ACT_LYNETTE_DAMAGE
    assert bare.hp == 40
    assert bare.aura == "hydro"


def test_lynettes_act_lands_with_no_aura_anywhere(arm):
    st = _state(stage=[["lynette", 8]], enemies=[_enemy(hp=40)])
    FS.end_of_turn_acts(st)
    assert st.enemies[0].hp == 40 - FS.ACT_LYNETTE_DAMAGE
    assert st.enemies[0].aura is None          # Anemo never sticks


def test_lynettes_number_is_the_mods():
    from tools import lint_constant_parity as parity
    assert FS.ACT_LYNETTE_DAMAGE == 3
    assert parity.MIRRORED["FurinaStageLaw.ActLynetteDamage"] == 3


def test_the_report_credits_each_guests_act_damage(arm):
    from tools import furina_stage_report as report
    st = _state(stage=[["lynette", 8]], enemies=[_enemy(hp=40)])
    FS.end_of_turn_acts(st)
    assert report._guest_act_damage(st)["lynette"] == FS.ACT_LYNETTE_DAMAGE
    assert "guest swirl" in dict(report.ARMS)


# ---------------------------------------------------------------------------
# The page.
# ---------------------------------------------------------------------------

def _row(event, member, name, **kw):
    row = {"event": event, "member": member, "name": name, "seat": 0,
           "fanfare": 0, "moved": 0, "reason": "", "target": "",
           "target_id": "", "each": -1, "hp": -1, "struck": -1, "by": "",
           "by_member": ""}
    row.update(kw)
    return row


def _stage(log=(), forecast=None, seats=(), act_block=None):
    from understudy.blindplay_board import furina_stage as board
    raw = {"live": True, "seats": list(seats), "log": list(log)}
    if forecast is not None:
        raw["forecast"] = forecast
    if act_block is not None:
        raw["act_block"] = act_block
    return board({"furina_stage": raw})


def _forecast(**kw):
    out = {"seats": [{"member": "usher", "name": "Gentilhomme Usher",
                      "now": 1, "after": 0, "leaves": True},
                     {"member": "clorinde", "name": "Clorinde", "now": 4,
                      "after": 4, "leaves": False}],
           "arrivals": [], "block_after_acts": 6, "intent_known": True,
           "front_takes": 3, "reaches_furina": 0, "unknown": False,
           "acts": [], "act_total": -1, "act_total_target": "",
           "takers": []}
    out.update(kw)
    return out


_SEATS = [{"member": "usher", "name": "Gentilhomme Usher", "seat": 0,
           "fanfare": 1},
          {"member": "clorinde", "name": "Clorinde", "seat": 1,
           "fanfare": 4}]


def test_the_header_and_the_attack_line_read_one_block_number():
    """Lane 1, fight 1 turn 2: "after the acts: Block 3" beside "after the
    acts' Block of 6". The header now reads the forecast's Block."""
    from understudy.blindplay_render import _render_stage
    lines = _render_stage(
        _stage(forecast=_forecast(takers=[
            {"member": "clorinde", "name": "Clorinde", "takes": 3,
             "leaves": False}]), seats=_SEATS, act_block=3),
        {"block": 0, "hp": 50, "max_hp": 78})
    head = lines[0]
    assert "after the acts: Block 6" in head
    assert ("- The attacks shown, after the acts' Block of 6: **Clorinde** "
            "takes 3; you take 0.") in lines


def test_the_split_names_each_performer_the_hits_reach():
    from understudy.blindplay_render import _render_stage
    lines = _render_stage(
        _stage(forecast=_forecast(reaches_furina=1, takers=[
            {"member": "usher", "name": "Gentilhomme Usher", "takes": 2,
             "leaves": True},
            {"member": "clorinde", "name": "Clorinde", "takes": 4,
             "leaves": False}]), seats=_SEATS),
        {"block": 0, "hp": 50, "max_hp": 78})
    assert ("- The attacks shown, after the acts' Block of 6: **Usher** "
            "takes 2 and leaves (its Bow lands before the rest of that hit), "
            "then **Clorinde** takes 4; you take 1.") in lines


def test_an_older_build_keeps_the_one_number_split():
    from understudy.blindplay_render import _render_stage
    forecast = _forecast()
    del forecast["takers"]
    lines = _render_stage(_stage(forecast=forecast, seats=_SEATS),
                          {"block": 0, "hp": 50, "max_hp": 78})
    assert ("- The attacks shown, after the acts' Block of 6: your front "
            "performer takes 3, you take 0.") in lines


def test_the_page_prints_what_the_acts_deal_and_their_total():
    from understudy.blindplay_render import _render_stage
    acts = [{"member": "crabaletta", "name": "Mademoiselle Crabaletta",
             "amount": 5, "element": "", "target": "random", "bow": False},
            {"member": "navia", "name": "Navia", "amount": 10,
             "element": "Geo", "target": "random", "bow": False},
            {"member": "chevalmarin", "name": "Surintendante Chevalmarin",
             "amount": 2, "element": "", "target": "all", "bow": False},
            {"member": "neuvillette", "name": "Neuvillette", "amount": 8,
             "element": "Hydro", "target": "all", "bow": True}]
    lines = _render_stage(
        _stage(forecast=_forecast(acts=acts, act_total=25,
                                  act_total_target="Shrinker Beetle"),
               seats=_SEATS),
        {"block": 0, "hp": 50, "max_hp": 78})
    at = lines.index("- What the acts will deal at the end of your turn:")
    assert lines[at + 1:at + 6] == [
        "  - **Crabaletta**: 5 to a random enemy",
        "  - **Navia**: 10 Geo to a random enemy",
        "  - **Chevalmarin**: 2 to ALL",
        "  - **Neuvillette's Bow**: 8 Hydro to ALL",
        "  - In all: 25 to Shrinker Beetle",
    ]


def test_an_act_prints_its_hit_and_the_hp_the_body_had():
    """Lane 2: "Wriothesley acted: 1 Cryo to Wriggler" was his 14 into a body
    with 1 HP left."""
    from understudy.blindplay_render import _render_stage_log
    stage = _stage([
        _row("act", "wriothesley", "Wriothesley", moved=1, target="Wriggler",
             dealt=14, target_hp=1, blocked=0),
        _row("bow", "crabaletta", "Mademoiselle Crabaletta", moved=2,
             target="Inklet", dealt=5, target_hp=9, blocked=3),
    ])
    assert _render_stage_log(stage) == [
        "  - **Wriothesley** acted: 14 Cryo to Wriggler, which had 1 HP "
        "left.",
        "  - **Crabaletta** took a Bow: 5 to Inklet (3 of it onto Block).",
    ]


def test_a_bow_says_what_its_block_caught_of_the_hit():
    from understudy.blindplay_render import _render_stage_log
    stage = _stage([_row("bow", "usher", "Gentilhomme Usher", moved=3,
                         caught=3)])
    assert _render_stage_log(stage) == [
        "  - **Usher** took a Bow: Furina gains 3 Block, 3 of it spent on "
        "the rest of the hit that emptied it."]


def test_an_arrival_names_the_seat_it_took_not_the_one_it_was_pushed_to():
    """Lane 2: "Navia joined the stage ... and stands in the middle seat"
    when she joined at the back. The mod files the count standing then."""
    from understudy.blindplay_render import _render_stage_log
    seats = [{"member": "wriothesley", "name": "Wriothesley", "seat": 0,
              "fanfare": 8, "seat_key": 3},
             {"member": "usher", "name": "Gentilhomme Usher", "seat": 1,
              "fanfare": 3, "seat_key": 1},
             {"member": "navia", "name": "Navia", "seat": 2, "fanfare": 4,
              "seat_key": 2}]
    stage = _stage([
        _row("arrive", "usher", "Gentilhomme Usher", seat=0, fanfare=3,
             seat_key=1, standing=1),
        _row("arrive", "navia", "Navia", seat=1, fanfare=4, seat_key=2,
             standing=2),
        _row("arrive", "wriothesley", "Wriothesley", seat=0, fanfare=8,
             seat_key=3, standing=3),
    ], seats=seats)
    assert _render_stage_log(stage) == [
        "  - **Usher** joined the stage at 3 Fanfare, in the front seat.",
        "  - **Navia** joined the stage at 4 Fanfare, in the back seat.",
        "  - **Wriothesley** joined the stage at 8 Fanfare, in the front "
        "seat.",
    ]


def test_the_new_fields_cross_the_blind_packet():
    """#674's leak test: the new beat and forecast fields are numbers and
    names, never ids."""
    from understudy import qa_packet
    stage = _stage(
        [_row("act", "wriothesley", "Wriothesley", moved=1,
              target="Wriggler", dealt=14, target_hp=1, blocked=0,
              caught=0, standing=2)],
        forecast=_forecast(acts=[{"member": "crabaletta",
                                  "name": "Mademoiselle Crabaletta",
                                  "amount": 5, "element": "",
                                  "target": "random", "bow": False}],
                           act_total=5, act_total_target="Wriggler",
                           takers=[{"member": "usher",
                                    "name": "Gentilhomme Usher", "takes": 1,
                                    "leaves": True}]),
        seats=_SEATS)
    assert qa_packet.leaks(stage) == []


def test_the_reaction_census_counts_a_guest_star_card_and_a_guest_on_stage():
    """Lane 1, fight 1 turn 3: "NO REACTION IS REACHABLE HERE: Electro is the
    only element this screen can supply" with Guest Star: Neuvillette (8
    Hydro to ALL enemies) in hand against an Electro aura."""
    from understudy.blindplay_faces import deck_elements
    from understudy.blindplay_notes import guest_elements
    card = {"id": "KLEEMOD-PROTO_FS_GUEST_STAR_NEUVILLETTE",
            "name": "Guest Star: Neuvillette", "type": "Skill", "cost": "2",
            "keywords": [],
            "description": "Neuvillette joins the stage with 6 Fanfare."}
    assert guest_elements({"player": {"hand": [card]}}) == {"Hydro"}
    assert deck_elements({"player": {"draw_pile": [card]}}) == ["Hydro"]
    on_stage = {"combat": {"stage": {"seats": [
        {"name": "Lynette", "member": "lynette"}]}}}
    assert guest_elements(on_stage) == {"Anemo"}
    # A guest whose act applies no element supplies none.
    chevreuse = dict(card, name="Guest Star: Chevreuse")
    assert guest_elements({"player": {"hand": [chevreuse]}}) == set()


def test_a_guest_star_in_hand_makes_the_reaction_reachable():
    from understudy import blindplay
    from tier0.tests.test_understudy_blindplay import elemental_hand_state
    state = elemental_hand_state(elements=("Electro",))
    state["player"]["hand"].append(
        {"id": "KLEEMOD-PROTO_FS_GUEST_STAR_NEUVILLETTE",
         "name": "Guest Star: Neuvillette", "type": "Skill", "cost": "2",
         "can_play": True, "index": 1, "target_type": "Self",
         "is_upgraded": False, "keywords": [],
         "description": "Neuvillette joins the stage with 6 Fanfare."})
    page = blindplay.observe(state)
    assert "NO REACTION IS REACHABLE" not in page
    assert "- **Electro-Charged** — " in page


# ---------------------------------------------------------------------------
# 4. Text.
# ---------------------------------------------------------------------------

def test_the_summon_tip_is_the_ruled_sentence():
    from understudy.blindplay_notes import ARM_KEYWORDS
    assert ARM_KEYWORDS["Summon"] == (
        "A performer joins at the back with 1 Fanfare. On a full stage, the "
        "front one Bows and leaves its Fanfare to the newcomer.")


def test_lynettes_row_is_the_ruled_sentence():
    from understudy.blindplay_notes import ARM_KEYWORDS
    assert ARM_KEYWORDS["Lynette"] == (
        "End of your turn: deal 3 Anemo damage to a random enemy, one with "
        "an aura if any.")


def test_weak_shrink_and_strength_say_the_performers_acts_are_not_changed():
    from understudy.blindplay_notes import (STAGE_PERFORMER_RIDER,
                                            keyword_notes)
    rows_with = keyword_notes({
        "character": "Furina", "stage_arm": True,
        "combat": {"stage": {"seats": [{"name": "Usher",
                                        "member": "usher"}],
                             "log": []}},
        "player": {"status": [{"name": "Shrink", "amount": -1},
                              {"name": "Weak", "amount": 1},
                              {"name": "Strength", "amount": 2}]}})
    texts = {row["name"]: row["text"] for row in rows_with}
    assert STAGE_PERFORMER_RIDER == " Your performers' acts are not changed."
    for word in ("Weak", "Shrink", "Strength"):
        assert texts[word].endswith(STAGE_PERFORMER_RIDER), word
    # No one on stage: the rows are the base game's words alone.
    rows_without = keyword_notes({
        "character": "Furina", "stage_arm": True,
        "combat": {"stage": {"seats": [], "log": []}},
        "player": {"status": [{"name": "Weak", "amount": 1}]}})
    weak = {row["name"]: row["text"] for row in rows_without}["Weak"]
    assert not weak.endswith(STAGE_PERFORMER_RIDER)
