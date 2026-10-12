"""Enchant preview confirm (2026-10-12): Gnarled Hammer's screen never closed.

THE FIND. A seat bought Gnarled Hammer (enchant 3 cards, minimum 0, not
cancelable). After the third pick the game opens the multi-card preview
(`NDeckEnchantSelectScreen.OnCardClicked` -> `PreviewSelection`). `confirm`
looked for the preview under the upgrade and removal spellings only, missed
`%EnchantMultiPreviewContainer`, and pressed the grid's main `Confirm`, which
on this screen is wired to `PreviewSelection` again. Each press appended
three more preview cards (the page's "What you have picked" grew 3, 6, 12)
and the screen stayed open. `skip` missed the preview's `Cancel` the same way.

WHAT IS PINNED HERE. A SOURCE assertion (the bridge has no C# test harness):
every preview container the state read knows is one confirm and cancel also
look in, and confirm never presses the main button while a preview is open.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a bridge.
"""
from __future__ import annotations

import re
from pathlib import Path

BRIDGE = Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
ACTIONS = BRIDGE / "McpMod.Actions.cs"
STATE_BUILDER = BRIDGE / "McpMod.StateBuilder.cs"


def _body(text: str, signature: str) -> str:
    start = text.index(signature)
    end = text.index("\n    private static ", start + len(signature))
    return text[start:end]


def _action_containers() -> set[str]:
    text = ACTIONS.read_text(encoding="utf-8")
    block = text[text.index("GitsSelectPreviewContainers ="):]
    block = block[:block.index("};")]
    return set(re.findall(r'"(%\w*PreviewContainer)"', block))


def test_actions_know_every_preview_the_state_read_knows():
    state = STATE_BUILDER.read_text(encoding="utf-8")
    body = _body(state, "BuildCardSelectState(NCardGridSelectionScreen")
    read = set(re.findall(r'GetNodeOrNull<Godot\.Control>\("(%\w*PreviewContainer)"\)',
                          body))
    assert {"%EnchantSinglePreviewContainer",
            "%EnchantMultiPreviewContainer"} <= read
    assert read <= _action_containers()


def test_confirm_and_cancel_use_the_shared_list():
    text = ACTIONS.read_text(encoding="utf-8")
    for sig in ("object?> ExecuteConfirmSelection()", "object?> ExecuteCancelSelection()"):
        body = _body(text, sig)
        assert "foreach (var containerName in GitsSelectPreviewContainers)" \
            in body, sig
        assert '"%UpgradeSinglePreviewContainer"' not in body, sig


def test_confirm_never_presses_main_under_an_open_preview():
    body = _body(ACTIONS.read_text(encoding="utf-8"),
                 "object?> ExecuteConfirmSelection()")
    guard = body.index("if (previewOpen)")
    assert body.index("previewOpen = true;") < guard
    assert guard < body.index("var mainConfirm")
    assert guard < body.index("FindAll<NConfirmButton>(screen)")
