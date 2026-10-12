"""No event option mid-exchange (2026-10-12): Klee's Ancient greeting.

THE FIND. On a Spiral Abyss run Klee's two-line Neow greeting was on line 0
when `choose` ForceClicked an Abyss option. The option changed the Ancient's
page, `NEventRoom.RefreshEventState` cleared the dialogue unread, and the
layout's hitbox stayed up over no lines, so the next `advance_dialogue` threw
in `NAncientEventLayout.SetDialogueLineAndAnimate` (lane 1, 0.2.5077). A
player cannot click an option there: the buttons sit below the dialogue,
unfocusable, until the last line.

WHAT IS PINNED HERE. A SOURCE assertion (the bridge has no C# test harness):
`choose_event_option` refuses while the dialogue hitbox is visible and
enabled -- the same test the state read uses for `in_dialogue` -- before it
touches a button.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a bridge.
"""
from __future__ import annotations

from pathlib import Path

BRIDGE = Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
ACTIONS = BRIDGE / "McpMod.Actions.cs"
STATE_BUILDER = BRIDGE / "McpMod.StateBuilder.cs"

HITBOX = 'GetNodeOrNull<NClickableControl>("%DialogueHitbox")'


def _body(text: str, signature: str) -> str:
    start = text.index(signature)
    end = text.index("\n    private static ", start + len(signature))
    return text[start:end]


def test_choose_refuses_while_the_dialogue_hitbox_is_up():
    body = _body(ACTIONS.read_text(encoding="utf-8"),
                 "object?> ExecuteChooseEventOption(")
    guard = body.index(".Visible && gitsDialogueHitbox.IsEnabled)")
    assert HITBOX in body
    assert "GItS LOCAL EDIT" in body
    assert guard < body.index("return Error(\"Ancient dialogue in progress")
    assert guard < body.index("FindAll<NEventOptionButton>(uiRoom)")
    assert guard < body.index("button.ForceClick()")


def test_the_refusal_is_the_state_reads_in_dialogue_test():
    state = STATE_BUILDER.read_text(encoding="utf-8")
    assert HITBOX in state
    assert "hitbox != null && hitbox.Visible && hitbox.IsEnabled" in state
