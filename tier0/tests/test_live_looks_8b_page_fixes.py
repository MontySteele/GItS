"""The live look of 2026-09-16, the four repairs that live on the PAGE side.

The record is not on main; it is on PR #570's branch, retrieved as
`git show 02039d2b:review/records/live-looks-8b-2026-09-16.md` (CLAUDE.md,
"History retrieval"). Each test below names the row or the defect number it
closes and quotes the screen the look read.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): these are shape assertions about a
renderer, taken on hand-built wire.
"""

import copy

from understudy import blindplay, targeting

from tier0.tests.test_understudy_blindplay import combat_state


# ----------------------------------------------- EB-610, the other shape ---

def _spark_power_state() -> dict:
    """A Klee combat whose wire carries Spark POWER-shaped.

    This is the shape `0.2.3480+proto` sent and the reason the row failed: a
    `Spark 3 (buff)` status row with no `KLEEMOD_SPARK` resource behind it, so
    the page's meters loop -- where `EB-610`'s clause was emitted -- never ran
    for Spark at all.
    """
    state = copy.deepcopy(combat_state())
    state["character"] = "klee"
    state["player"]["resources"] = {}
    state["player"]["spark_sources"] = [
        {"source": "relic:pounding_surprise/explosion", "amount": 1,
         "card": "Pocket Match"},
        {"source": "companion:personal/play", "amount": 2,
         "card": "Barbara — Front Row Seat"}]
    state["player"]["status"] = list(state["player"]["status"]) + [
        {"id": "SPARK_POWER", "name": "Spark", "amount": 3,
         "is_debuff": False,
         "description": "Cards cost Sparks instead of Energy."}]
    return state


def _spark_meter_state() -> dict:
    """The same turn, METER-shaped: the build `EB-610` was written against."""
    state = copy.deepcopy(combat_state())
    state["character"] = "klee"
    state["player"]["resources"] = {"KLEEMOD_SPARK": 3}
    state["player"]["spark_sources"] = [
        {"source": "relic:pounding_surprise/explosion", "amount": 1,
         "card": "Pocket Match"},
        {"source": "companion:personal/play", "amount": 2,
         "card": "Barbara — Front Row Seat"}]
    return state


def _source_lines(page: str) -> list[str]:
    return [line for line in page.splitlines()
            if line.strip().startswith("- This turn:")]


def test_eb610_the_sources_print_beside_a_power_shaped_spark_row():
    """THE FIND. "The wire carries it ... and the page never prints it."

    Seen to FAIL before this change: the wire carried both sources,
    `blindplay.observation()` folded them to `an explosion` and
    `Barbara — Front Row Seat`, and no line of the page said so.
    """
    page = blindplay.observe(_spark_power_state())
    lines = _source_lines(page)
    assert lines, "the Spark power row printed no source line"
    assert "+1 an explosion" in lines[0]
    assert "+2 Barbara — Front Row Seat" in lines[0]


def test_eb610_the_sources_still_print_beside_a_meter_shaped_spark_row():
    """The shape the clause was written for is untouched."""
    lines = _source_lines(blindplay.observe(_spark_meter_state()))
    assert lines and "+1 an explosion" in lines[0]


def test_eb610_a_build_that_sends_both_shapes_prints_one_copy():
    """A fact printed twice on one screen is `EB-407`'s defect, and this is
    the one build that could produce it."""
    state = _spark_meter_state()
    state["player"]["status"] = list(state["player"]["status"]) + [
        {"id": "SPARK_POWER", "name": "Spark", "amount": 3,
         "is_debuff": False,
         "description": "Cards cost Sparks instead of Energy."}]
    assert len(_source_lines(blindplay.observe(state))) == 1


def test_eb610_the_power_row_prints_the_sources_under_itself():
    page = blindplay.observe(_spark_power_state())
    lines = page.splitlines()
    idx = next(i for i, line in enumerate(lines)
               if line.strip().startswith("- This turn:"))
    assert "Spark 3" in lines[idx - 1], (
        "the source line belongs to the row whose number it explains")
    assert lines[idx].startswith("    - "), "and hangs under it, indented"


# --------------------------------------- defect 1, the renderer's markup ---

def _stage_state() -> dict:
    """A Furina combat with a stage on it and a log of arrivals, acts and
    bows -- the section the look read the raw tags off."""
    state = copy.deepcopy(combat_state())
    state["character"] = "furina"
    state["player"]["furina_stage"] = {
        "seats": [{"member": "usher", "name": "Usher", "fanfare": 3},
                  {"member": "crabaletta", "name": "Crabaletta",
                   "fanfare": 1}],
        "log": [
            {"event": "arrive", "member": "usher", "name": "Usher",
             "fanfare": 3, "moved": 0, "target": "", "why": ""},
            {"event": "act", "member": "usher", "name": "Usher",
             "fanfare": 3, "moved": 3, "target": "", "why": ""},
            {"event": "bow", "member": "crabaletta", "name": "Crabaletta",
             "fanfare": 0, "moved": 8, "target": "Corpse Slug (1)",
             "why": ""}]}
    return state


def test_defect_one_no_raw_markup_reaches_the_stage_section():
    """THE FIND. The page printed `joined the stage at 3 [gold]Fanfare[/gold]`,
    `Furina gains 3 [gold]Block[/gold]` and `took a [gold]Bow[/gold]`.

    `EB-246`'s fold runs over what arrives on the WIRE, so a tag typed into a
    renderer LITERAL never meets it.
    """
    page = blindplay.observe(_stage_state())
    assert "[gold]" not in page and "[/gold]" not in page


def test_defect_one_the_words_themselves_survive_the_fold():
    """Folding a tag out is not deleting the word inside it."""
    page = blindplay.observe(_stage_state())
    assert "Fanfare" in page
    assert "Bow" in page


# ------------------------------------------ defect 2, the bridge's modes ---

SPEND_AS_THE_PAGE_PRINTS_IT = "Spend 3: deal 13 instead"
SPEND_AS_THE_BRIDGE_HOLDS_IT = "[gold]Spend[/gold] 3: deal 13 instead"


def test_defect_two_a_mode_named_off_the_page_posts_the_bridge_s_spelling():
    """THE FIND, with the exact strings. Playing `Curtain Rise` with
    `mode: "Spend 3: deal 13 instead"` -- the text the page prints -- was
    refused: *"has no mode matching ... Modes: 'Deal 7 damage' |
    '[gold]Spend[/gold] 3: deal 13 instead'"*.

    Neither of `GitsModalTargeting.Match`'s two rules can land it: the folded
    want is not the raw label, and neither contains the other, because the
    markup sits in the MIDDLE of the phrase.
    """
    assert (targeting.posted_mode("Curtain Rise", SPEND_AS_THE_PAGE_PRINTS_IT)
            == SPEND_AS_THE_BRIDGE_HOLDS_IT)


def test_defect_two_the_plain_mode_of_the_same_card_is_unchanged():
    """A label with no markup in it posts exactly as it was typed."""
    assert (targeting.posted_mode("Curtain Rise", "Deal 7 damage")
            == "Deal 7 damage")


def test_defect_two_the_raw_spelling_still_resolves_to_itself():
    """A caller who already had the bridge's spelling keeps it."""
    assert (targeting.posted_mode("Curtain Rise", SPEND_AS_THE_BRIDGE_HOLDS_IT)
            == SPEND_AS_THE_BRIDGE_HOLDS_IT)


def test_defect_two_an_unresolvable_mode_goes_over_unchanged():
    """No such card, no `choose_one`, no matching label: the bridge's own
    refusal -- which lists the labels it DOES have -- is a better answer than
    a guess."""
    assert targeting.posted_mode("Strike", "Spend 3: deal 13 instead") == (
        "Spend 3: deal 13 instead")
    assert targeting.posted_mode("Curtain Rise", "no such mode") == (
        "no such mode")
    assert targeting.posted_mode("Curtain Rise", "") == ""


# ---------------------------------- defect 5, two elements on one face ---

def _overridden_face_state() -> dict:
    """Ka-pow! in hand under Lightning Fang: the override row the mod grows,
    beside the printed `Applies Pyro` the override has not removed."""
    state = copy.deepcopy(combat_state())
    state["character"] = "klee"
    state["player"]["hand"] = [{
        "index": 0,
        "id": "KLEEMOD-PROTO_KO_KAPOW",
        "name": "Ka-pow!",
        "description": "Set off every Bomb.",
        "cost": "0",
        "can_play": True,
        "target_type": "AnyEnemy",
        "keywords": [
            {"name": "Applies Pyro",
             "description": "Leaves a Pyro aura on the enemy."},
            {"name": "Element overridden",
             "description": "This card applies Electro instead of the "
                            "element it prints."}]}]
    return state


def test_defect_five_the_applies_row_follows_the_override():
    """THE FIND. The title read `[Electro]`, an `*Element overridden*` clause
    explained it, and then an `*Applies Pyro*` keyword row still followed --
    three rows of one face, two agreeing and the third contradicting both.
    """
    page = blindplay.observe(_overridden_face_state())
    assert "Applies Electro" in page
    assert "Applies Pyro" not in page


def test_defect_five_the_row_keeps_its_body():
    """The row is renamed and not dropped: it carries the only sentence on the
    page saying what an element DOES."""
    page = blindplay.observe(_overridden_face_state())
    assert "Leaves a Pyro aura on the enemy." in page


def test_defect_five_a_face_with_no_override_is_untouched():
    """Every board with no Lightning Fang on it reads exactly as before."""
    state = _overridden_face_state()
    state["player"]["hand"][0]["keywords"] = [
        {"name": "Applies Pyro",
         "description": "Leaves a Pyro aura on the enemy."}]
    page = blindplay.observe(state)
    assert "Applies Pyro" in page
    assert "Applies Electro" not in page
