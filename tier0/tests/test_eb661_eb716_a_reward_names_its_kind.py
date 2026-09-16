"""`EB-661` and `EB-716`: a combat reward row says WHAT it is and what it does.

`EB-661` (round 25 lane 1, item 5). The reward screen printed a potion as a
bare name beside the relics, with no type and no rules text, and the seat took
`Mazaleth's Gift` believing it was a relic. The chest screen one room over
prints a relic's text; this one printed nothing.

`EB-716` (r32 lane 1). `Blessing of the Forge` was offered as a bare name with
no kind and no rules text, "and the seat then looked for it among relics; it is
a potion."

BOTH FIELDS WERE ON THE WIRE AND NEITHER WAS READ. `BuildRewardsState`
(`McpMod.StateBuilder.cs:2069`) sends `type` on every row and, for a potion,
`potion_name` and `potion_description` beside it. Nothing read `type` -- the
shop's category reader looks at `category` and `card_type`, which a reward
carries neither of -- and the potion's own text was shadowed by the generic
`description` reader, because `Reward.Description` for a potion IS the potion's
title, so the body line repeated the heading and `_dedupe_text` cleared it.

WHAT IS STILL OWED TO THE BRIDGE. A RELIC reward carries `description` (the
relic's NAME) and nothing else -- no `relic_description` -- so a relic offer
names its kind here and still cannot print its rules text. That half needs a
bridge field and is not in this change.
"""

from __future__ import annotations

from understudy import blindplay


def _rewards(items: list[dict]) -> dict:
    """A rewards screen in `BuildRewardsState`'s own shape."""
    return {"state_type": "rewards",
            "player": {"character": "kokomi", "potions": [],
                       "max_potion_slots": 3},
            "rewards": {"can_proceed": True, "items": items}}


POTION = {"index": 0, "type": "potion", "potion_id": "BLESSING_OF_THE_FORGE",
          "potion_name": "Blessing of the Forge",
          "description": "Blessing of the Forge",
          "potion_description": "Upgrade a card in your hand for the rest of "
                                "combat."}
RELIC = {"index": 1, "type": "relic", "description": "Mazaleth's Gift"}
CARD = {"index": 2, "type": "card", "description": "Strike"}
GOLD = {"index": 3, "type": "gold", "description": "12 Gold",
        "gold_amount": 12}


# ---------------------------------------------------------------------------
# `EB-661`. EVERY OFFER NAMES ITS KIND
# ---------------------------------------------------------------------------

def test_every_reward_row_names_what_kind_of_thing_it_is():
    page = blindplay.observe(_rewards([POTION, RELIC, CARD, GOLD]))
    assert "**Blessing of the Forge** — potion" in page
    assert "**Mazaleth's Gift** — relic" in page
    assert "**Strike** — card" in page
    assert "**12 Gold** — gold" in page


def test_the_relic_the_seat_mistook_a_potion_for_is_marked_relic():
    """The whole find: two rows, one relic and one potion, told apart."""
    page = blindplay.observe(_rewards([RELIC, POTION]))
    relic = next(l for l in page.splitlines() if "Mazaleth" in l)
    potion = next(l for l in page.splitlines() if "Blessing" in l)
    assert relic.endswith("— relic")
    assert potion.endswith("— potion")


def test_a_kind_that_is_the_whole_name_is_not_printed_twice():
    """`_shelf_kind`'s rule: a row the wire could name no better than `Card`
    reads `**Card**`, not `**Card** — card`."""
    page = blindplay.observe(_rewards([{"index": 0, "type": "card",
                                        "description": "Card"}]))
    assert "- **Card**\n" in page
    assert "— card" not in page


# ---------------------------------------------------------------------------
# `EB-716`. AND A POTION CARRIES ITS TEXT
# ---------------------------------------------------------------------------

def test_a_potion_reward_prints_its_rules_text():
    page = blindplay.observe(_rewards([POTION]))
    assert "Upgrade a card in your hand for the rest of combat." in page


def test_the_potions_text_is_not_a_second_copy_of_its_title():
    """`_dedupe_text`'s job is untouched: the body repeats no heading."""
    page = blindplay.observe(_rewards([POTION]))
    assert page.count("Blessing of the Forge") == 1


def test_a_potion_whose_feed_carries_no_text_still_names_its_kind():
    """Absent is not zero: an older feed prints the kind and no body line."""
    page = blindplay.observe(_rewards([
        {"index": 0, "type": "potion", "potion_name": "Fire Potion",
         "description": "Fire Potion"}]))
    assert "**Fire Potion** — potion" in page
