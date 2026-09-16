"""`EB-716`, the relic half: a relic offered as a reward prints what it does.

The potion half shipped first (`EB-661` / `EB-716`, the reward row's kind and
the potion's text) and left this in its own commit message: *"a RELIC reward
carries `description` (the relic's name) and no `relic_description`, so a relic
offer names its kind here and cannot print its rules text. That half is a
bridge field."*

THE BRIDGE FIELD IS HERE. `BuildRewardsState` merges `relic_id`, `relic_name`
and `relic_description` into a relic row, in the same prefixed shape the potion
beside it and `BuildShopState`'s relic shelf already use. `Relic` is null until
the reward is populated (an elite's relic is rolled in `Populate`), so an
absent key is "not rolled yet" and that row is unchanged.

AND THE PAGE READS IT. The relic's text was under the same shadow the potion's
was: `Reward.Description` for a `RelicReward` IS the relic's TITLE, so the
generic `description` reader filled the body with a copy of the heading and
`_dedupe_text` cleared it. The prefixed spelling is the thing's own face and
wins.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import pytest

from understudy import blindplay, blindplay_faces


GOLDEN_PEARL = {
    "index": 0, "type": "relic",
    "description": "Golden Pearl",
    "relic_id": "GOLDEN_PEARL",
    "relic_name": "Golden Pearl",
    "relic_description": "Whenever you enter a Rest Site, gain 25 Gold.",
}
# The row as it arrived before this change, and as it still arrives from a
# reward the game has not populated: a type and a name, and nothing else.
UNPOPULATED = {"index": 1, "type": "relic", "description": "Golden Pearl"}
POTION = {"index": 2, "type": "potion", "potion_name": "Fire Potion",
          "description": "Fire Potion",
          "potion_description": "Deal 20 damage to target enemy."}


def _rewards(items):
    return {"state_type": "rewards",
            "player": {"character": "kokomi", "potions": [],
                       "max_potion_slots": 3},
            "rewards": {"can_proceed": True, "items": list(items)}}


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


# ---------------------------------------------------------------------------
# THE OFFER
# ---------------------------------------------------------------------------

def test_a_relic_reward_prints_its_rules_text():
    page = blindplay.observe(_rewards([GOLDEN_PEARL]))
    assert "**Golden Pearl**" in page
    assert "Whenever you enter a Rest Site, gain 25 Gold." in page


def test_the_relics_name_is_still_printed_once():
    """`Reward.Description` IS the relic's title, so the body would otherwise
    repeat the heading -- which is how this defect looked on the page."""
    page = blindplay.observe(_rewards([GOLDEN_PEARL]))
    assert page.count("Golden Pearl") == 1


def test_a_relic_beside_a_potion_prints_its_own_text():
    """The screen the defect was filed from. The POTION's own text is the
    other half's pin (`test_eb661_eb716_a_reward_names_its_kind.py`, still on
    its branch); what is asserted here is that a two-row screen does not put
    the relic's rules under the wrong name or lose them."""
    page = blindplay.observe(_rewards([GOLDEN_PEARL, POTION]))
    relic, potion = (i for i, line in enumerate(page.splitlines())
                     if "**Golden Pearl**" in line or "**Fire Potion**" in line)
    lines = page.splitlines()
    assert lines[relic + 1].strip() == ("Whenever you enter a Rest Site, gain "
                                        "25 Gold.")
    assert "Whenever you enter a Rest Site" not in lines[potion]


def test_a_reward_whose_relic_is_not_rolled_yet_is_what_it_was():
    """An absent key is a statement, not a hole to fill: the row still names
    the relic and says nothing it was not sent."""
    option = blindplay_faces._dedupe_text(
        blindplay_faces._reward_option(UNPOPULATED))
    assert option["name"] == "Golden Pearl"
    assert option["text"] == ""


def test_the_face_is_read_off_the_prefixed_spelling():
    option = blindplay_faces._dedupe_text(
        blindplay_faces._reward_option(GOLDEN_PEARL))
    assert option["name"] == "Golden Pearl"
    assert option["text"] == "Whenever you enter a Rest Site, gain 25 Gold."
