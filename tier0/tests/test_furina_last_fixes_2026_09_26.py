"""Furina, the Stage: the last fixes from the 2026-09-26 wave-3 seat round
(lane 3, seat b). The C# twin is
`klee-mod/KleeTests/Prototype/FurinaLastFixes20260926Tests.cs`.

(Its first fix, Navia's Bow reading the bar she had, left with the bars:
the re-founded Stage, review/active/furina-refounding-2026-10-03.md, gives
performers no bars, and her act reads the Fanfare spent this turn --
`tier0/tests/test_furina_stage.py`.)

2. AN ANSWERED CHOOSER IS A TRANSITION, NOT A SCREEN. The seat: "Arkhe
   Alignment's chooser opened twice in a row" with one copy in play. The
   lane's own game log has exactly one `chose cards [...ARKHE_OUSIA_OPTION]`
   per turn, so the game asked once; the page drew the answered chooser a
   second time, in the frame before the game took it off the overlay stack.
"""

from __future__ import annotations

from understudy import blindplay_read


# ---- 2. An answered chooser ---------------------------------------------------

def _chooser(answered):
    blob = {"screen_type": "choose", "prompt": "Choose a card.",
            "cards": [{"index": 0, "name": "Ousia"},
                      {"index": 1, "name": "Pneuma"}]}
    if answered is not None:
        blob["answered"] = answered
    return {"state_type": "card_select", "card_select": blob}


def test_an_answered_chooser_is_ridden_out_and_an_open_one_is_a_screen():
    assert blindplay_read.transient(_chooser(True))
    assert not blindplay_read.transient(_chooser(False))
    # An older bridge that does not say is a screen, as before.
    assert not blindplay_read.transient(_chooser(None))


def test_settle_waits_for_the_game_to_take_an_answered_chooser_down():
    class Wire:
        def __init__(self):
            self.reads = 0

        def get_state(self):
            self.reads += 1
            return {"state_type": "monster", "battle": {"is_play_phase": True}}

    wire = Wire()
    state = blindplay_read.settle(_chooser(True), wire, tries=3, delay=0)
    assert state["state_type"] == "monster"
    assert wire.reads == 1


def test_the_bridge_says_whether_the_chooser_took_its_pick():
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    bridge = repo / "vendor" / "STS2_MCP"
    helper = (bridge / "gits" / "GitsChooserAnswered.cs").read_text(
        encoding="utf-8")
    assert '"_screenComplete"' in helper
    state = (bridge / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert 'state["answered"] = answered' in state
    actions = (bridge / "McpMod.Actions.cs").read_text(encoding="utf-8")
    # A press on an answered chooser is refused, and a press the screen
    # ignored (it drops picks in its first 350 ms) says nothing was chosen.
    assert "GitsChooserAnswered(chooseScreen) == true" in actions
    assert "GitsChooserAnswered(chooseScreen) == false" in actions
