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
absent/empty/populated contract, her one Fanfare number and its flow, the
seats front to back, the log's beats in plain words, and the three meter lines
going away with the arm on and staying with it off. The re-founding
(2026-10-04, review/active/furina-refounding-2026-10-03.md) retired the bars,
the damage order and the back performer; the rules are the C# ledger's
(`klee-mod/KleeTests/Prototype/`) and the sim engine's
(`tier0/tests/test_furina_stage_v2.py`).

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import copy

import pytest

from understudy import blindplay, blindplay_board


def _seat(member, name, index, entity_id, guest=False, price=0, key=None):
    return {"member": member, "name": name, "seat": index,
            "seat_key": index + 1 if key is None else key, "guest": guest,
            "price": price, "entity_id": entity_id}


THREE_SEATS = [
    _seat("usher", "Gentilhomme Usher", 0, "7"),
    _seat("chevalmarin", "Surintendante Chevalmarin", 1, "8"),
    _seat("crabaletta", "Mademoiselle Crabaletta", 2, "9"),
]


def _stage(seats=None, log=None, fanfare=5, **kw):
    """The wire's `furina_stage` map (`FurinaStageLedger.Snapshot`)."""
    out = {"live": True, "fanfare": fanfare, "gained_this_turn": 0,
           "spent_this_turn": 0, "paid_this_turn": 0, "rehearsal": 0,
           "capacity": 3, "seats": THREE_SEATS if seats is None else seats,
           "log": log or []}
    out.update(kw)
    return out


def _beat(event, member, name, seat=0, fanfare=0, moved=0, reason="",
          target="", combat_id="", source=""):
    return {"event": event, "member": member, "name": name, "seat": seat,
            "fanfare": fanfare, "moved": moved, "reason": reason,
            "target": target, "target_id": combat_id, "source": source}


def _state(stage=None, resources=None, hand=None,
           enemy="Nibbit"):
    """A combat screen the page will render, with whatever stage block is
    handed in. Deliberately minimal: what is being asserted is one section, and
    a fixture carrying a hand and a map would put four other sections between
    the assertion and its subject."""
    player = {
        "character": "Furina",
        "hp": 62, "max_hp": 78, "block": 9,
        "energy": 3, "max_energy": 3,
        "gold": 0,
        "hand": list(hand or []),
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
        "enemies": [{"name": enemy, "hp": 20, "max_hp": 44, "block": 0,
                     "intents": [{"kind": "attack", "amount": 12}],
                     "status": []}],
    }


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def _page(stage=None, resources=None, hand=None, enemy="Nibbit"):
    return blindplay.observe(_state(stage, resources, hand, enemy))


def _card(text, name="Some Card"):
    """One hand entry, enough for the glossary to read its body off."""
    return {"id": "x", "name": name, "description": text, "cost": "1",
            "can_play": True, "target_type": "Self"}


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
    key cannot carry, so the page states it rather than falling silent."""
    page = _page(_stage(seats=[]))
    assert "## Your stage" in page
    assert "- The stage is empty." in page
    assert "Seats, front to back" not in page


# ---------------------------------------------------------------------------
# THE RE-FOUNDING (2026-10-04): HER FANFARE, AND THE SEATS FRONT TO BACK.
# ---------------------------------------------------------------------------

def test_the_first_line_is_her_fanfare_and_this_turns_flow():
    """Fanfare is ONE number on Furina; the page prints it with what this
    turn gained, what Spends took and what the stars paid, and Rehearsal
    where she has any."""
    page = _page(_stage(fanfare=6, gained_this_turn=4, spent_this_turn=3,
                        paid_this_turn=2, rehearsal=1))
    assert ("- Fanfare 6 (this turn: 4 gained, 3 spent on Spend, 2 paid by "
            "stars) · Rehearsal 1") in page
    assert "· Rehearsal" not in _page(_stage())


def test_the_seats_print_front_to_back_with_guests_and_their_price():
    seats = [_seat("usher", "Gentilhomme Usher", 0, "7"),
             _seat("neuvillette", "Neuvillette", 1, "8", guest=True, price=2),
             _seat("charlotte", "Charlotte", 2, "9", guest=True)]
    page = _page(_stage(seats=seats))
    assert ("- Seats, front to back (3 of 3): **Usher**, **Neuvillette** "
            "(Guest Star, pays 2 per act), **Charlotte** (Guest Star).") in page


def test_the_block_line_says_what_the_acts_will_add():
    """`EB-743`, second half: the Block on the strip while she decides is the
    Block BEFORE the acts. The mod's forecast says what they add."""
    forecast = {"fanfare_after": 5, "block": 4, "acts": [
        {"member": "usher", "name": "Gentilhomme Usher", "seat_key": 1,
         "kind": "block", "amount": 4, "element": "", "target": "",
         "times": 1, "price": 0, "skips": False}]}
    page = _page(_stage(seats=THREE_SEATS[:1], forecast=forecast,
                        act_block=4))
    assert "- Block 9 · after the acts: Block 13 · Furina 62/78" in page


def test_the_block_line_reads_the_mods_forecast_when_the_wire_sends_one():
    """R276 batch two: the mod's own `act_block`, never a flat sum."""
    assert "after the acts: Block 27" in _page(_stage(act_block=18))
    assert "after the acts" not in _page(_stage(act_block=0))


def test_three_named_performers_stand_in_seat_order():
    page = _page(_stage())
    for name in ("Usher", "Chevalmarin", "Crabaletta"):
        assert name in page
    assert page.index("**Usher**") < page.index("**Chevalmarin**") < \
        page.index("**Crabaletta**")


def test_no_bar_and_no_back_performer_is_printed():
    """The re-founding retired the bars and the back performer."""
    page = _page(_stage())
    assert "back:" not in page and "middle:" not in page
    assert "back performer" not in page


# ---------------------------------------------------------------------------
# `EB-735`. THE LOG, IN PLAIN WORDS.
# ---------------------------------------------------------------------------

def test_one_line_per_beat():
    """Every beat the re-founded ledger files, each naming its performer."""
    log = [
        _beat("arrive", "chevalmarin", "Surintendante Chevalmarin", seat=1),
        _beat("act", "usher", "Gentilhomme Usher", seat=0, moved=4),
        _beat("pay", "neuvillette", "Neuvillette", seat=1, fanfare=3,
              moved=2),
        _beat("act", "neuvillette", "Neuvillette", seat=1, moved=9),
        _beat("skip", "clorinde", "Clorinde", seat=2, fanfare=0,
              reason="short"),
        _beat("leave", "usher", "Gentilhomme Usher", seat=-1,
              reason="evicted"),
        _beat("bow", "usher", "Gentilhomme Usher", seat=-1, reason="leaves"),
        _beat("act", "usher", "Gentilhomme Usher", seat=-1, moved=4),
        _beat("gain", "usher", "Gentilhomme Usher", seat=-1, fanfare=4,
              moved=1, source="Bow"),
        _beat("cue", "crabaletta", "Mademoiselle Crabaletta", seat=2),
        _beat("move", "crabaletta", "Mademoiselle Crabaletta", seat=0),
        _beat("spend", "usher", "Gentilhomme Usher", seat=-1, fanfare=1,
              moved=3),
        _beat("walk_on", "chevalmarin", "Surintendante Chevalmarin",
              seat=-1),
    ]
    page = _page(_stage(log=log))
    for line in (
            "**Chevalmarin** joined the stage.",
            "**Usher** acted: Furina gains 4 Block.",
            "**Neuvillette** paid 2 Fanfare: 5 → 3.",
            "**Neuvillette** acted: 9 Hydro damage to ALL enemies.",
            "**Clorinde** skipped its act: not enough Fanfare to pay.",
            ("**Usher** left the stage: a fourth summon took its seat; its "
             "card went to your discard pile."),
            "**Usher** took a Bow.",
            "**Usher** acted for free: Furina gains 4 Block.",
            "You gained 1 Fanfare from Bow: 3 → 4.",
            "You Cued **Crabaletta**.",
            "**Crabaletta** moved to the front.",
            "You spent 3 Fanfare: 4 → 1.",
            "**Chevalmarin** walked on"):
        assert line in page, line


def test_each_performers_act_says_what_it_did():
    """`EB-743`: each act names its own effect, with the beat's figure."""
    def line(member, name, moved):
        return _page(_stage(log=[_beat("act", member, name, moved=moved)]))

    assert "acted: Furina gains 4 Block." in line(
        "usher", "Gentilhomme Usher", 4)
    assert "acted: 2 damage to ALL enemies." in line(
        "chevalmarin", "Surintendante Chevalmarin", 2)
    assert "acted: 5 damage to a random enemy." in line(
        "crabaletta", "Mademoiselle Crabaletta", 5)
    # Seat page 3 (2026-10-05): the Salon's Tab guests' acts, as the mod's
    # `FurinaStage.CueOf` has them (the v2 kinds logged Chevreuse as Energy).
    assert "acted: 8 Pyro damage to ALL enemies." in line("lyney", "Lyney", 8)
    assert "acted: 4 damage to a random enemy." in line(
        "chevreuse", "Chevreuse", 4)
    assert "acted: you Repay 2." in line("sigewinne", "Sigewinne", 2)


def test_an_act_that_dealt_nothing_prints_no_zero():
    page = _page(_stage(log=[_beat("act", "navia", "Navia", moved=0)]))
    assert "**Navia** acted: no damage." in page
    assert "acted: 0" not in page


def test_a_departure_says_why():
    reasons = {
        # The pool to 75 (2026-10-09, sec.3): a leaving guest does not
        # act, and its card goes back to the discard pile.
        "evicted": ("a fourth summon took its seat; its card went to your "
                    "discard pile"),
        "final_bow": ("it took its Final Bow; its card went to your discard "
                      "pile"),
    }
    for reason, sentence in reasons.items():
        page = _page(_stage(log=[_beat("leave", "usher", "Gentilhomme Usher",
                                       seat=-1, reason=reason)]))
        assert f"**Usher** left the stage: {sentence}." in page


def test_a_guest_bow_that_stays_says_so():
    page = _page(_stage(log=[_beat("bow", "neuvillette", "Neuvillette",
                                   seat=1, reason="stays")]))
    assert "**Neuvillette** took a Bow and stays on stage." in page


def test_the_log_names_the_window_it_covers():
    """The clear is at her turn END, so what a seat opening a turn reads here
    is the sweep it could not watch and the enemy turn that followed. A window
    a reader has to infer is a window a reader gets wrong."""
    page = _page(_stage(log=[_beat("act", "usher", "Gentilhomme Usher",
                                   moved=4)]))
    assert "Since you ended your last turn" in page


def test_a_quiet_turn_prints_the_board_and_no_log_heading():
    page = _page(_stage())
    assert "Seats, front to back" in page
    assert "Since you ended your last turn" not in page


# ---------------------------------------------------------------------------
# `EB-736`. THE HEADER IS STAGE-ONLY.
# ---------------------------------------------------------------------------

def test_the_three_retired_meters_leave_the_header_with_the_arm_on():
    """Round one's second finding. All three are SHIPPED resources the brief's
    sec.2 retires, and the mod still registers them -- `GitsResources` walks
    BaseLib's registry and knows nothing about who is playing -- so they arrive
    on the wire whatever the arm is."""
    page = _page(_stage())
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
    page = _page(_stage(),
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
        {"furina_stage": _stage(seats=copy.deepcopy(THREE_SEATS))})
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
        _page(_stage(log=[_beat("act", "usher", "Gentilhomme Usher",
                                moved=4)])))


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

    after = _state(_stage(log=[_beat("bow", "usher", "Gentilhomme Usher",
                                     seat=-1)]))
    contains = scenario.CHECKS["page_contains"]
    lacks = scenario.CHECKS["page_lacks"]

    assert contains({"text": "Seats, front to back"}, {}, after) is None
    assert contains({"text": "**Crabaletta**"}, {}, after) is None
    assert contains({"text": "took a Bow"}, {}, after) is None
    assert contains({"text": "no such line"}, {}, after) is not None
    assert lacks({"text": "- Encore:"}, {}, after) is None
    assert lacks({"text": "## Your stage"}, {}, after) is not None


def test_the_stage_scenario_asserts_the_block_and_parses():
    """The row's acceptance, on the file that carries it: her Fanfare, the
    seats front to back and the Spend line, asserted rather than eyeballed."""
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
    assert "Seats, front to back" in body
    assert "You spent 3 Fanfare" in body
    assert "back performer" in body          # asserted ABSENT (page_lacks)


# ---------------------------------------------------------------------------
# `EB-744`. UNDER THE ARM THE GLOSSARY IS THE STAGE'S.
# ---------------------------------------------------------------------------

def test_the_encore_row_is_gone_from_an_arm_page():
    """Round two, sec.4: "the glossary still carries the old words: an Encore
    row". Encore has no job under the Stage (brief sec.2, R269) and since
    `EB-745` nothing grants it, so a rule for a meter that cannot move is noise
    -- even where a shipped row the arm did not swap still prints the word."""
    face = [_card("Spend 2 [gold]Encore[/gold]: draw 2 cards.")]
    arm = _page(_stage(), hand=face)
    assert "**Encore**" not in arm
    # And with no stage block the page is the shipped Furina's, untouched.
    assert "**Encore**" in _page(None, hand=face)


def test_the_companion_row_says_what_a_companion_does_under_the_arm():
    """The round-two Preserve seat played Companion cards for a run believing
    they rotate the stage, which is the SHIPPED Salon's rule. The Stage retires
    that outright; its Hydro comes from her cards."""
    face = [_card("Deal 4 damage for each Companion you played last turn.")]
    arm = _page(_stage(), hand=face)
    assert "It does nothing to your stage" in arm
    assert "performs the front member" not in arm
    shipped = _page(None, hand=face)
    assert "performs the front member" in shipped


def test_a_monster_called_a_bomb_does_not_raise_the_bomb_row():
    """Round two, sec.4: "a Bomb row beside a Gas Bomb". A creature's name is
    in the glossary's haystack on purpose -- a power's badge is a printed rule
    -- but a monster called one is not a charge on the board, and a Furina seat
    with no Bomb in the game read Klee's whole charge rule on every screen it
    stood on."""
    page = _page(_stage(),
                 enemy="Gas Bomb")
    assert "**Bomb**" not in page
    # `EB-753` CLOSED THE SECOND HALF FROM THE OTHER SIDE. This row used to add
    # that a card PLACING one still raises the word on a Furina board, "keyed
    # off the board and the faces". It is not raised there any more, and must
    # not be: `Bomb` is Klee's, the glossary is scoped to the arm the run's
    # character owns, and a Furina seat has no route to a charge whatever a
    # face on the screen says. The word keeps its definition on Klee's own run,
    # which `test_a_kit_word_is_defined_on_the_run_that_owns_it` pins.
    assert "**Bomb**" not in _page(
        {"live": True, "seats": THREE_SEATS, "log": []}, enemy="Gas Bomb",
        hand=[_card("Place 1 [gold]Bomb[/gold] dealing 5.")])


def test_the_performer_picker_says_what_it_asks_and_prints_no_cost():
    """The re-founding (2026-10-04): "Cue a performer" opens a small panel,
    one face per seat front to back (`StageSeatOption`). It is the card just
    played asking WHICH performer, so the heading says so, and a face is
    never played, so it prints no cost and no type."""
    from understudy.blindplay_notes import STAGE_SEAT_CHOOSER_PROMPT

    def face(index, key, title, text):
        return {"index": index, "id": f"KLEEMOD-{key}_SEAT_OPTION",
                "name": title, "description": text, "cost": "0",
                "type": "Skill", "card_type": "Skill"}
    page = blindplay.observe({
        "state_type": "card_select",
        "player": {"character": "Furina", "potions": [], "relics": [],
                   "max_potion_slots": 3},
        "card_select": {"screen_type": "choose", "prompt": "Choose a card.",
                        "can_skip": False, "can_cancel": False,
                        "preview_showing": False, "can_confirm": False,
                        "selection_known": True,
                        "cards": [face(0, "USHER", "Gentilhomme Usher",
                                       "Act: gain 4 Block."),
                                  face(1, "CRABALETTA",
                                       "Mademoiselle Crabaletta",
                                       "Act: deal 5 damage to a random "
                                       "enemy.")]}})
    assert f"# {STAGE_SEAT_CHOOSER_PROMPT}" in page
    assert "- **Gentilhomme Usher**\n" in page
    assert "cost 0" not in page
