"""The bridge's event `body` (2026-10-12).

`BuildEventState` read `body` off the room's canonical event, which never has
a page set, so every event sent `"body": null` and seats never saw an event's
story text. The bridge now reads the page on the player's local copy as plain
text (`vendor/STS2_MCP/gits/GitsEventPage.cs`, `gits/GitsEventBody.cs`, rules
pinned in `klee-mod/KleeTests/GitsEventBodyTests.cs`). These are the
event-shaped states the bridge now sends, read through the seat's page.
"""
from pathlib import Path

import pytest

from understudy import blindplay

REPO = Path(__file__).resolve().parents[2]

STARSNATCH = ("The pond at the foot of the cliff is full of fat, silver fish. "
              "Klee has three bombs left and nobody is watching. She "
              "remembers Jean's face the last time.")


def _event(event_id, name, body, options):
    return {"state_type": "event",
            "run": {"act": 1, "floor": 3, "ascension": 0, "modifiers": []},
            "player": {"character": "Klee", "hp": 70, "max_hp": 70,
                       "gold": 99, "relics": [], "potions": [],
                       "status": []},
            "event": {"event_id": event_id, "event_name": name,
                      "is_ancient": False, "in_dialogue": False,
                      "body": body,
                      "options": [
                          {"index": i, "title": t, "description": d,
                           "is_locked": False, "is_proceed": False,
                           "was_chosen": False, "keywords": []}
                          for i, (t, d) in enumerate(options)]}}


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def test_a_story_events_paragraph_reaches_the_page():
    page = blindplay.observe(_event(
        "KLEEMOD-KLEE_STARSNATCH_CLIFF", "Starsnatch Cliff", STARSNATCH,
        [("Blast the pond!", "Gain 75 Gold. Add Confinement to your deck."),
         ("Just one little bomb.", "Add Fish Blasting to your deck.")]))
    assert STARSNATCH in page


def test_a_base_events_paragraph_reaches_the_page():
    body = ("You come across a golden idol on a pedestal.\n\n"
            "It looks very valuable.")
    page = blindplay.observe(_event(
        "GOLDEN_IDOL", "Golden Idol", body,
        [("Take", "Obtain Golden Idol."), ("Leave", "Nothing happens.")]))
    assert "You come across a golden idol on a pedestal." in page
    assert "It looks very valuable." in page


def test_the_bridge_reads_the_page_for_every_event():
    builder = (REPO / "vendor" / "STS2_MCP"
               / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert 'state["body"] = GitsEventPageBody(eventRoom, eventModel);' in builder
    assert "GitsAbyssPageBody" not in builder
