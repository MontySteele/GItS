"""`EB-748`: the refusal on the blind page names what refused.

THE FIND (Furina, the Stage, round two, sec.4). A card refused under Smoggy
arrived on the wire as the bare enum `BlockedByHook`, which
`understudy/qa_packet.UNPLAYABLE_REASONS` renders as *"something else on the
board is stopping you right now"*. Two seats flagged it and the second one
GUESSED -- correctly, off `Smoggy 1` in the status list, which is luck and not
a reading. Every other refusal on that page names its cause.

THE BRIDGE HALF is `vendor/STS2_MCP/gits/GitsRefusalSource.cs` and is pinned
in `klee-mod/KleeTests/GitsRefusalSourceTests.cs`: `CardModel.CanPlay`'s second
out parameter is the preventer, the bridge was discarding it, and it now sends
the sentence as `unplayable_reason_text`.

THIS FILE IS THE PAGE HALF, and it is the whole of what a seat sees:

  * a refusal that arrives WITH the sentence prints the sentence, and the
    vague line is gone;
  * a refusal that arrives WITHOUT it -- an older bridge, or a preventer with
    no readable name -- prints exactly what it printed before, because
    `_hook_note` must keep covering that build;
  * the mod's own sentence still wins over the game's class name, which is the
    order `BuildCardState` writes and the reason a Spark shortfall still reads
    as a price and a bank rather than as a power's name.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import pytest

from understudy import blindplay


SMOGGY = "Smoggy is stopping you right now"
VAGUE = "something else on the board is stopping you"


def _card(name="Tidal Flourish", reason=None, text=None):
    """One hand entry the game has refused (or not)."""
    entry = {"id": "x", "name": name, "description": "Deal 8 damage.",
             "cost": "1", "type": "attack", "target_type": "Enemy",
             "can_play": reason is None}
    if reason is not None:
        entry["unplayable_reason"] = reason
    if text is not None:
        entry["unplayable_reason_text"] = text
    return entry


def _state(hand, status=None):
    return {
        "state_type": "monster",
        "screen": "combat",
        "floor": 3,
        "battle": {"round": 2},
        "player": {"character": "Furina", "hp": 62, "max_hp": 78, "block": 0,
                   "energy": 3, "max_energy": 3, "gold": 0,
                   "hand": list(hand),
                   "draw_pile_count": 5, "discard_pile_count": 2,
                   "exhaust_pile_count": 0,
                   "draw_pile": [], "discard_pile": [], "exhaust_pile": [],
                   "relics": [], "potions": [],
                   "status": list(status or [])},
        "enemies": [{"name": "Nibbit", "hp": 20, "max_hp": 44, "block": 0,
                     "intents": [{"kind": "attack", "amount": 12}],
                     "status": []}],
    }


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def _page(hand, status=None):
    return blindplay.observe(_state(hand, status))


# ---------------------------------------------------------------------------
# THE FIND ITSELF
# ---------------------------------------------------------------------------

def test_a_hook_refusal_names_the_power_that_refused_it():
    page = _page([_card(reason="BlockedByHook", text=SMOGGY)],
                 status=[{"name": "Smoggy", "stacks": 1}])
    assert f"CANNOT BE PLAYED: {SMOGGY}" in page
    assert VAGUE not in page


def test_the_named_refusal_does_not_also_print_the_where_to_look_note():
    """`_hook_note`'s clause is what the page said INSTEAD of a name. A
    refusal that names its power has no use for it."""
    page = _page([_card(reason="BlockedByHook", text=SMOGGY)],
                 status=[{"name": "Smoggy", "stacks": 1}])
    assert "the feed does not name" not in page


# ---------------------------------------------------------------------------
# AND THE BUILD THAT CANNOT SAY IT
# ---------------------------------------------------------------------------

def test_a_bare_hook_still_prints_what_it_printed_before():
    """An older bridge, or a preventer with no readable name: the wire sends
    the enum alone and the page must still be the page it was."""
    page = _page([_card(reason="BlockedByHook")],
                 status=[{"name": "Smoggy", "stacks": 1}])
    assert VAGUE in page
    assert "Smoggy is stopping you" not in page


def test_the_mods_own_sentence_still_wins():
    """`BuildCardState` writes the mod's answer first and the game's class
    name under it, because the mod knows the price and the bank and a class
    name cannot. The page prints whatever arrived, unrewritten."""
    priced = "you have no Spark, and this costs 1"
    page = _page([_card(reason="BlockedByCardLogic", text=priced)])
    assert f"CANNOT BE PLAYED: {priced}" in page


def test_a_playable_card_says_nothing_at_all():
    page = _page([_card()])
    assert "CANNOT BE PLAYED" not in page
