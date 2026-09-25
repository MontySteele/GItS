"""Furina, the Stage -- the first guest seat round (0.2.3794), the PAGE halves.

Two seats: Opus (lane 2) and Codex (`review/qa/blindplay/20260925-221903`).
The mod halves are `klee-mod/KleeTests/Prototype/FurinaGuestCastTests.cs`
(Wriothesley at the front, the seat key) and `FurinaGuestRoundFixTests.cs`
(the damage previews); the sim's are in `test_furina_guest_cast.py`.

  1. The back performer tip said "Hits reach it last". Rule 6 never runs a
     hit on past the front: "Hits never reach it."
  3. The log said a summoned Usher "stands in the front seat" while the stage
     line showed him at the back -- the page named a beat's seat by NAME, and
     the first Usher stood in front. It names it by the seat's key now.
  4. Words printed and never defined: Elemental Reaction, Swirl, aura, Cryo,
     Companion. Every glossary word attaches wherever it is printed on the
     page, the glossary rows themselves included.
  6. The Wood Carvings event named Toric Toughness and never its cost.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

from __future__ import annotations

import pytest

from understudy import blindplay, qa_packet
from understudy.blindplay_board import furina_stage
from understudy.blindplay_notes import ARM_KEYWORDS, ELEMENT_KEYWORDS
from understudy.blindplay_render import _render_stage_log


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


SALON_SOLITAIRE = {"name": "Salon Solitaire",
                   "description": "Start each combat with Usher in front "
                                  "with 3 [gold]Fanfare[/gold]."}


def _words(page: str) -> dict[str, str]:
    """The page's glossary, name to text."""
    if "## Words on this screen" not in page:
        return {}
    block = page.split("## Words on this screen", 1)[1].split("\n## ", 1)[0]
    out = {}
    for line in block.splitlines():
        if line.startswith("- **"):
            name, _sep, text = line[4:].partition("** — ")
            out[name] = text
    return out


def _reward(*cards: dict, character: str = "Furina") -> str:
    return blindplay.observe({
        "state_type": "card_reward",
        "player": {"character": character, "potions": [],
                   "relics": [SALON_SOLITAIRE] if character == "Furina"
                   else [], "max_potion_slots": 3},
        "card_reward": {"prompt": "Add a card to your deck.",
                        "can_skip": True,
                        "cards": [dict(c, index=i, cost="1",
                                       card_type="Skill")
                                  for i, c in enumerate(cards)]}})


# The live faces, as the wire sends them: the description with its gold
# tags, and each hover tip the card carries as `{name, description}`.
COURTROOM_DRAMA = {
    "id": "KLEEMOD-COURTROOM_DRAMA", "name": "Courtroom Drama",
    "description": "Your first [gold]Elemental Reaction[/gold] each turn "
                   "applies 1 [gold]Vulnerable[/gold] and 1 [gold]Weak[/gold] "
                   "to its target before the hit lands."}
AN_INVITATION = {
    "id": "KLEEMOD-AN_INVITATION", "name": "An Invitation",
    "description": "Add 1 random Common [gold]Companion[/gold] card to your "
                   "hand."}
LYNETTE = {
    "id": "KLEEMOD-PROTO_FS_GUEST_STAR_LYNETTE",
    "name": "Guest Star: Lynette",
    "description": "Lynette joins the stage with 8 [gold]Fanfare[/gold].",
    "keywords": [
        {"name": "Guest Star",
         "description": "A performer who joins the stage, one of each. A "
                        "second copy makes it Bow, then return with the new "
                        "Fanfare added."},
        {"name": "Lynette",
         "description": "End of your turn: [gold]Swirl[/gold] a random "
                        "enemy with an aura."}]}
WRIOTHESLEY = {
    "id": "KLEEMOD-PROTO_FS_GUEST_STAR_WRIOTHESLEY",
    "name": "Guest Star: Wriothesley",
    "description": "Wriothesley joins the stage at the front with 8 "
                   "[gold]Fanfare[/gold].",
    "keywords": [
        {"name": "Guest Star",
         "description": "A performer who joins the stage, one of each."},
        {"name": "Wriothesley",
         "description": "End of your turn: deal [gold]Cryo[/gold] damage to "
                        "a random enemy equal to twice the Fanfare he lost "
                        "to hits since his last act."}]}


# ---------------------------------------------------------------------------
# 1. THE BACK PERFORMER TIP.
# ---------------------------------------------------------------------------

def test_the_back_performer_row_says_hits_never_reach_it():
    assert ARM_KEYWORDS["back performer"].startswith(
        "Gains and Spends Fanfare. Hits never reach it. At the end of your "
        "turn, it loses half its Fanfare above 5.")
    for row in ARM_KEYWORDS.values():
        assert "reach it last" not in row


# ---------------------------------------------------------------------------
# 3. THE ARRIVAL LINE NAMES THE SEAT THE PERFORMER STANDS IN.
# ---------------------------------------------------------------------------

def _usher(seat, fanfare, key):
    return {"member": "usher", "name": "Gentilhomme Usher", "seat": seat,
            "fanfare": fanfare, "entity_id": str(10 + key), "seat_key": key}


def _arrive(seat, fanfare, key):
    return {"event": "arrive", "member": "usher",
            "name": "Gentilhomme Usher", "seat": seat, "fanfare": fanfare,
            "moved": 0, "reason": "", "target": "", "target_id": "",
            "each": -1, "hp": -1, "struck": -1, "seat_key": key}


def test_a_second_ushers_arrival_names_the_back_seat():
    """The Opus seat, fight 4 turn 4: a second Usher joined at the back and
    the log said he "stands in the front seat", where the FIRST Usher
    stood."""
    stage = furina_stage({"furina_stage": {
        "live": True, "seats": [_usher(0, 3, 1), _usher(1, 1, 2)],
        "log": [_arrive(1, 1, 2)]}})
    assert _render_stage_log(stage) == [
        "  - **Usher** joined the stage at 1 Fanfare, and stands in the "
        "back seat."]


def test_an_arrival_that_has_since_left_names_no_seat():
    stage = furina_stage({"furina_stage": {
        "live": True, "seats": [_usher(0, 3, 1)],
        "log": [_arrive(1, 1, 2)]}})
    assert _render_stage_log(stage) == [
        "  - **Usher** joined the stage at 1 Fanfare."]


def test_an_older_build_with_no_key_keeps_the_name_lookup():
    seats = [_usher(0, 3, 1)]
    del seats[0]["seat_key"]
    row = _arrive(0, 3, 1)
    del row["seat_key"]
    stage = furina_stage({"furina_stage": {
        "live": True, "seats": seats, "log": [row]}})
    assert _render_stage_log(stage) == [
        "  - **Usher** joined the stage at 3 Fanfare, and stands in the "
        "front seat."]


# ---------------------------------------------------------------------------
# 4. EVERY WORD ATTACHES WHERE IT IS PRINTED. One test per word.
# ---------------------------------------------------------------------------

def test_elemental_reaction_is_defined_on_courtroom_dramas_reward():
    words = _words(_reward(COURTROOM_DRAMA))
    assert words["Elemental Reaction"].startswith(
        "A hit of a different element than the aura an enemy is already "
        "wearing.")


def test_companion_is_defined_on_an_invitations_reward():
    words = _words(_reward(AN_INVITATION))
    assert words["Companion"].startswith(
        "A card titled with a character's name, a dash, then its own.")


def test_swirl_is_defined_on_lynettes_reward():
    words = _words(_reward(LYNETTE))
    assert words["Swirl"] == ARM_KEYWORDS["Swirl"]
    assert "Lynette" in words


def test_aura_is_defined_where_lynettes_tip_prints_it():
    words = _words(_reward(LYNETTE))
    assert words["aura"] == ELEMENT_KEYWORDS["aura"]


def test_cryo_is_defined_where_wriothesleys_tip_prints_it():
    words = _words(_reward(WRIOTHESLEY))
    assert words["Cryo"] == ELEMENT_KEYWORDS["Cryo"]
    assert words["Cryo"].startswith("An element. A Cryo hit on an enemy")
    # And his face's new words still raise the Guest Star row.
    assert "Guest Star" in words


def test_a_word_inside_a_glossary_row_is_defined_too():
    """A performer tip reached through the STAGE LINE, not a card: Lynette on
    stage prints her name, her row prints Swirl and aura, and both are
    defined off the row itself."""
    page = _combat_with_guest("lynette", "Lynette")
    words = _words(page)
    assert "Lynette" in words
    assert "Swirl" in words and "aura" in words


def test_cryo_is_defined_off_wriothesleys_row_on_the_stage():
    words = _words(_combat_with_guest("wriothesley", "Wriothesley"))
    assert "Wriothesley" in words and "Cryo" in words


def test_an_element_a_card_defines_itself_is_not_defined_twice():
    card = {"id": "KLEEMOD-X", "name": "Frost Card",
            "description": "Deal 4 Cryo damage.",
            "keywords": [{"name": "Applies Cryo",
                          "description": "No aura: applies Cryo for 2 "
                                         "turns."}]}
    assert "Cryo" not in _words(_reward(card))


def test_the_trio_rows_are_not_raised_off_the_seat_rows_acts_sentence():
    """`STAGE_ACTS` defines the trio's acts itself, so a named summon's
    reward still prints its own performer's row and no other."""
    card = {"id": "KLEEMOD-X", "name": "Crab Call",
            "description": "Summon Crabaletta."}
    words = _words(_reward(card))
    assert "Mademoiselle Crabaletta" in words
    assert "Surintendante Chevalmarin" not in words


def _combat_with_guest(member: str, name: str) -> str:
    player = {
        "character": "Furina", "hp": 60, "max_hp": 78, "block": 0,
        "energy": 3, "max_energy": 3, "gold": 0,
        "hand": [{"id": "x", "name": "Stage Presence",
                  "description": "Gain 5 Block.", "cost": "1",
                  "can_play": True, "target_type": "Self"}],
        "draw_pile_count": 5, "discard_pile_count": 2,
        "exhaust_pile_count": 0, "draw_pile": [], "discard_pile": [],
        "exhaust_pile": [], "relics": [], "potions": [], "status": [],
        "resources": {}, "pets": [],
        "furina_stage": {
            "live": True, "log": [],
            "seats": [{"member": member, "name": name, "seat": 0,
                       "fanfare": 8, "entity_id": "7", "seat_key": 1}]},
    }
    return blindplay.observe({
        "state_type": "monster", "screen": "combat", "floor": 3,
        "battle": {"round": 3}, "player": player,
        "enemies": [{"name": "Seapunk", "hp": 20, "max_hp": 44,
                     "block": 0, "combat_id": "1",
                     "intents": [{"kind": "attack", "amount": 7}],
                     "status": []}]})


# ---------------------------------------------------------------------------
# 6. AN EVENT'S NAMED CARD PRINTS ITS COST.
# ---------------------------------------------------------------------------

def _wood_carvings(cost: str | None) -> str:
    tip = {"name": "Toric Toughness",
           "description": "Gain 5 Block. Gain 5 Block at the start of your "
                          "next 2 turns."}
    if cost is not None:
        tip["cost"] = cost
    return blindplay.observe({
        "state_type": "event",
        "event": {"event_id": "WOOD_CARVINGS", "event_name": "Wood Carvings",
                  "in_dialogue": False, "body": "Three carvings.",
                  "options": [{"index": 0, "title": "Torus",
                               "description": "Transform a card into Toric "
                                              "Toughness.",
                               "keywords": [tip]},
                              {"index": 1, "title": "Leave"}]}})


def test_an_event_option_prints_the_cost_of_the_card_it_names():
    page = _wood_carvings("2")
    assert ("    · **Toric Toughness** — cost 2 — Gain 5 Block. Gain 5 "
            "Block at the start of your next 2 turns.") in page
    assert qa_packet.leaks(page) == []


def test_a_feed_with_no_cost_prints_the_card_as_before():
    page = _wood_carvings(None)
    assert "    · **Toric Toughness** — Gain 5 Block." in page
    assert "cost" not in page.split("Toric Toughness**", 1)[1].split("\n")[0]
