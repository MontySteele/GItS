"""THE BLIND-PLAY PAGE PRINTS THE STAGE (`EB-735`), AND STOPS PRINTING WHAT
THE STAGE RETIRED (`EB-736`).

The read is `review/active/furina-stage-round-1-2026-09-08.md`, and its section
2 is the whole of both rows:

    "Nothing on the blind-play page names a performer, a seat or a bar. The
    bridge publishes pets and the page draws Kokomi's one; Furina's three have
    no renderer. So in some 550 actions no seat ever knew who was on stage or
    what a bar held. Each learned the roster from one glossary line and
    inferred bars by firing readers and reading the result backwards. Every
    finding below is read through that hole."

    "The second finding rides on the first: the page's combat header still
    prints the shipped Fanfare meter, the shipped Burst meter and `Encore: 0`,
    beside a glossary that calls Fanfare the bar. One word, two resources, the
    shown one dead."

WHAT IS PINNED HERE, and it is the PAGE and never the rule: the three-way
absent/empty/populated contract, the damage order on the first line, the seat
words, the log's five events, and the three meter lines going away with the arm
on and staying with it off. The rules themselves are the C# ledger's
(`klee-mod/KleeTests/Prototype/FurinaStageRoundTwoTests.cs`) and the sim
engine's (`tier0/tests/test_furina_stage.py`).

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import copy

import pytest

from understudy import blindplay, blindplay_board


def _seat(member, name, index, bar, entity_id):
    return {"member": member, "name": name, "seat": index, "fanfare": bar,
            "entity_id": entity_id}


THREE_SEATS = [
    _seat("usher", "Gentilhomme Usher", 0, 5, "7"),
    _seat("chevalmarin", "Surintendante Chevalmarin", 1, 1, "8"),
    _seat("crabaletta", "Mademoiselle Crabaletta", 2, 6, "9"),
]


def _beat(event, member, name, seat=0, bar=0, moved=0, reason=""):
    return {"event": event, "member": member, "name": name, "seat": seat,
            "fanfare": bar, "moved": moved, "reason": reason}


def _state(stage=None, resources=None):
    """A combat screen the page will render, with whatever stage block is
    handed in. Deliberately minimal: what is being asserted is one section, and
    a fixture carrying a hand and a map would put four other sections between
    the assertion and its subject."""
    player = {
        "character": "Furina",
        "hp": 62, "max_hp": 78, "block": 9,
        "energy": 3, "max_energy": 3,
        "gold": 0,
        "hand": [],
        "draw_pile_count": 5, "discard_pile_count": 2, "exhaust_pile_count": 0,
        "draw_pile": [], "discard_pile": [], "exhaust_pile": [],
        "relics": [], "potions": [], "status": [],
        "resources": resources if resources is not None else {
            "KLEEMOD_ENCORE": 0,
            "KLEEMOD_FANFARE": 4,
            "KLEEMOD_FURINA_BURST": 5,
        },
        "pets": [],
    }
    if stage is not None:
        player["furina_stage"] = stage
    return {
        "state_type": "monster",
        "screen": "combat",
        "floor": 3,
        "battle": {"round": 3},
        "player": player,
        "enemies": [{"name": "Nibbit", "hp": 20, "max_hp": 44, "block": 0,
                     "intents": [{"kind": "attack", "amount": 12}],
                     "status": []}],
    }


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def _page(stage=None, resources=None):
    return blindplay.observe(_state(stage, resources))


# ---------------------------------------------------------------------------
# `EB-735`. THE THREE STATES.
# ---------------------------------------------------------------------------

def test_a_build_with_no_stage_prints_no_stage_section():
    """An ABSENT key is "no Stage rule in this build", and the page says
    nothing at all -- the standing rule for every GItS block on this wire."""
    assert "## Your stage" not in _page(None)
    assert blindplay_board.furina_stage({}) is None


def test_a_seat_not_playing_the_arm_prints_no_stage_section():
    """An EMPTY map is "the rule is here and this seat is not playing it". A
    Klee at this table must not be shown an empty stage."""
    assert "## Your stage" not in _page({})


def test_an_empty_stage_prints_the_section_and_says_it_is_empty():
    """A POPULATED map with NO SEATS is the third state and the one an absent
    key cannot carry: rule 8 makes an empty stage the one board on which a
    Spend rider cannot fire at all, so the page states it rather than falling
    silent."""
    page = _page({"live": True, "seats": [], "log": []})
    assert "## Your stage" in page
    assert "The stage is empty" in page
    assert "cannot fire" in page
    assert "lead:" not in page


# ---------------------------------------------------------------------------
# `EB-735`. THE BOARD, IN DAMAGE ORDER.
# ---------------------------------------------------------------------------

def test_the_first_line_is_the_damage_order_and_the_second_is_the_reserve():
    """Brief sec.8's last failure mode, answered: "the strip must show the
    lead's bar beside her Block, in the damage order". Block, then the lead's
    bar, then her HP -- the three numbers one attack meets, in the order it
    meets them (rule 6). The reserve is a SECOND line because nothing reaches
    it, and a reader taking the two as one would read four bars where an attack
    sees two."""
    page = _page({"live": True, "seats": THREE_SEATS, "log": []})
    lines = [ln for ln in page.splitlines() if ln.startswith("- ")]

    assert "- Block 9 · lead: Usher 5 · Furina 62/78" in lines
    assert "- middle: Chevalmarin 1 · back: Crabaletta 6" in lines


def test_three_named_bars_stand_in_seat_order():
    """The row's own acceptance. Round one's seats read the cast as "one
    anonymous pool with three names"; this is the page naming all three, each
    under the seat word its rules are written against."""
    page = _page({"live": True, "seats": THREE_SEATS, "log": []})
    for name in ("Usher", "Chevalmarin", "Crabaletta"):
        assert name in page
    assert page.index("Usher") < page.index("Chevalmarin") < \
        page.index("Crabaletta")


def test_a_lone_performer_is_the_lead_and_never_a_back_performer():
    """Rule 5's second sentence: "with one performer on stage, that is the
    lead". A page that called it a back performer would print the rule's own
    exception as a contradiction -- and a Raise, which lands at the back, would
    read as going somewhere else."""
    page = _page({"live": True, "seats": THREE_SEATS[:1], "log": []})
    assert "lead: Usher 5" in page
    assert "back:" not in page
    assert "middle:" not in page


def test_two_performers_are_lead_and_back_with_no_middle():
    page = _page({"live": True, "seats": THREE_SEATS[:2], "log": []})
    assert "lead: Usher 5" in page
    assert "back: Chevalmarin 1" in page
    assert "middle:" not in page


# ---------------------------------------------------------------------------
# `EB-735`. THE LOG.
# ---------------------------------------------------------------------------

def test_one_line_per_arrival_act_bow_departure_and_rotation():
    """The five moments the row names, each naming its performer."""
    log = [
        _beat("arrive", "chevalmarin", "Surintendante Chevalmarin",
              seat=1, bar=1),
        _beat("act", "usher", "Gentilhomme Usher", seat=0, bar=5, moved=3),
        _beat("leave", "usher", "Gentilhomme Usher", seat=-1, reason="spend"),
        _beat("bow", "usher", "Gentilhomme Usher", seat=-1, moved=4),
        _beat("rotate", "crabaletta", "Mademoiselle Crabaletta", seat=2, bar=6),
    ]
    page = _page({"live": True, "seats": THREE_SEATS, "log": log})

    # The seat word is TODAY'S cast size, floored at the index the beat
    # recorded: Chevalmarin arrived in the back-most empty seat and a third
    # performer has stood behind her since, so the seat she is in now is the
    # middle one and that is the seat the reader is looking at.
    assert "**Chevalmarin** took the middle seat at 1" in page
    assert "**Usher** performed from the lead seat. It moved 3." in page
    assert "**Usher** left the stage: emptied by a Spend, so it takes a Bow." \
        in page
    assert "**Usher** took a [gold]Bow[/gold]. It moved 4." in page
    assert "**Crabaletta** moved from the front seat to the back" in page


def test_a_departure_says_why_because_that_is_rules_seven_and_nine():
    """A bow is earned by Spend and by nothing else, so the reason is not
    decoration: it is the difference between turn one's line B and line C
    (brief sec.7), which round one asked its seats to name."""
    reasons = {
        "hit": "emptied by a hit, so no Bow",
        "spend": "emptied by a Spend, so it takes a Bow",
        "rotated": "rotated off the front to make room, so no Bow",
        "final_bow": "took its Bow and left",
    }
    for reason, sentence in reasons.items():
        page = _page({"live": True, "seats": THREE_SEATS,
                      "log": [_beat("leave", "usher", "Gentilhomme Usher",
                                    seat=-1, reason=reason)]})
        assert f"**Usher** left the stage: {sentence}." in page


def test_a_beat_that_moved_nothing_prints_no_number():
    """Chevalmarin's bow only leaves an aura. A page saying "it moved 0" would
    be answering a question the beat did not raise."""
    page = _page({"live": True, "seats": THREE_SEATS,
                  "log": [_beat("bow", "chevalmarin",
                                "Surintendante Chevalmarin", seat=-1)]})
    assert "**Chevalmarin** took a [gold]Bow[/gold]." in page
    assert "It moved" not in page


def test_the_log_names_the_window_it_covers():
    """The clear is at her turn END, so what a seat opening a turn reads here
    is the sweep it could not watch and the enemy turn that followed. A window
    a reader has to infer is a window a reader gets wrong."""
    page = _page({"live": True, "seats": THREE_SEATS,
                  "log": [_beat("act", "usher", "Gentilhomme Usher", moved=3)]})
    assert "Since you ended your last turn" in page


def test_a_quiet_turn_prints_the_board_and_no_log_heading():
    page = _page({"live": True, "seats": THREE_SEATS, "log": []})
    assert "lead: Usher 5" in page
    assert "Since you ended your last turn" not in page


# ---------------------------------------------------------------------------
# `EB-736`. THE HEADER IS STAGE-ONLY.
# ---------------------------------------------------------------------------

def test_the_three_retired_meters_leave_the_header_with_the_arm_on():
    """Round one's second finding. All three are SHIPPED resources the brief's
    sec.2 retires, and the mod still registers them -- `GitsResources` walks
    BaseLib's registry and knows nothing about who is playing -- so they arrive
    on the wire whatever the arm is."""
    page = _page({"live": True, "seats": THREE_SEATS, "log": []})
    assert "- Encore:" not in page
    assert "- Fanfare:" not in page
    assert "- Furina Burst:" not in page


def test_they_stay_on_a_board_the_arm_is_not_live_on():
    """ASKED OF THE ARM AND NOT OF THE BOARD, `ZERO_METERS`' own question: with
    no Stage block the shipped meters are the truth of that board, and
    `EB-487`'s rule that Encore and Fanfare print their ZERO still holds."""
    page = _page(None)
    assert "- Encore: 0" in page
    assert "- Fanfare: 4" in page
    assert "- Furina Burst: 5" in page


def test_the_arm_hides_only_the_three_and_not_every_meter():
    """A neighbouring meter is not collateral: what is retired is three named
    resources, not the header."""
    page = _page({"live": True, "seats": THREE_SEATS, "log": []},
                 resources={"KLEEMOD_ENCORE": 3, "KLEEMOD_FANFARE": 4,
                            "KLEEMOD_FURINA_BURST": 5, "KLEEMOD_CHARGE": 2})
    assert "- Charge: 2" in page
    assert "- Encore:" not in page


# ---------------------------------------------------------------------------
# THE READER'S OWN CONTRACT.
# ---------------------------------------------------------------------------

def test_the_reader_keeps_the_seat_index_the_wire_sent():
    """The list IS in seat order, and the index is emitted anyway: a reader
    reconstructing the seat from an array position has to be told somewhere
    that the array is ordered, and the data is that somewhere."""
    read = blindplay_board.furina_stage(
        {"furina_stage": {"live": True, "seats": copy.deepcopy(THREE_SEATS),
                          "log": []}})
    assert [row["seat"] for row in read["seats"]] == [0, 1, 2]
    assert [row["name"] for row in read["seats"]] == [
        "Usher", "Chevalmarin", "Crabaletta"]
    assert [row["long_name"] for row in read["seats"]] == [
        "Gentilhomme Usher", "Surintendante Chevalmarin",
        "Mademoiselle Crabaletta"]
    assert [row["entity_id"] for row in read["seats"]] == ["7", "8", "9"]


def test_the_page_never_prints_a_section_twice():
    """`assert_one_page`'s rule, which the stage section is now one more
    tenant of."""
    blindplay.assert_one_page(
        _page({"live": True, "seats": THREE_SEATS,
               "log": [_beat("act", "usher", "Gentilhomme Usher", moved=3)]}))


# ---------------------------------------------------------------------------
# THE SCENARIO CHECKS (`EB-735` acceptance, `EB-736`'s half).
# ---------------------------------------------------------------------------

def test_a_scenario_can_assert_the_stage_block_and_the_missing_meters():
    """`understudy/scenario` reads the WIRE and nothing else -- which is right
    for a rule and useless for a row whose whole defect was that a true board
    reached the page and the page printed nothing about it. So the two checks
    added here read the RENDERER, through the same module the seat runs."""
    from understudy import scenario

    assert "page_contains" in scenario.CHECKS
    assert "page_lacks" in scenario.CHECKS

    after = _state({"live": True, "seats": THREE_SEATS,
                    "log": [_beat("bow", "usher", "Gentilhomme Usher",
                                  seat=-1, moved=4)]})
    contains = scenario.CHECKS["page_contains"]
    lacks = scenario.CHECKS["page_lacks"]

    assert contains({"text": "lead: Usher 5"}, {}, after) is None
    assert contains({"text": "back: Crabaletta 6"}, {}, after) is None
    assert contains({"text": "took a [gold]Bow[/gold]"}, {}, after) is None
    assert contains({"text": "no such line"}, {}, after) is not None
    assert lacks({"text": "- Encore:"}, {}, after) is None
    assert lacks({"text": "## Your stage"}, {}, after) is not None


def test_the_stage_scenario_asserts_the_block_and_parses():
    """The row's acceptance, on the file that carries it: three named bars in
    seat order and a bow line, asserted rather than eyeballed."""
    import pathlib

    from understudy import scenario

    path = (pathlib.Path(__file__).resolve().parents[2] / "understudy"
            / "scenarios" / "furina-stage-damage-order.yaml")
    parsed = scenario.load(path)
    named = {key
             for verb, spec in parsed.steps if verb == "expect"
             for key in spec}

    assert "page_contains" in named
    assert "page_lacks" in named
    body = path.read_text(encoding="utf-8")
    assert "lead: Chevalmarin" in body
    assert "back: Crabaletta" in body
    assert "took a [gold]Bow[/gold]" in body
