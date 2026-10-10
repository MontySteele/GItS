"""Fresh hand previews (2026-10-10): the page printed a stale number.

THE FIND. Under Frail, Hold the Stage printed 18 Block on the seat page and
gained 13. The bridge reads a hand card's text through
`CardModel.GetDescriptionForPile(PileType.Hand)`, which (0.111.0 decompile)
formats the dynamic vars' current `PreviewValue` and never computes one; only
`UpdateDynamicVarPreview` does, and the game calls it when the card node
redraws.

WHAT IS PINNED HERE. A SOURCE assertion, because the C# is not reachable from
pytest (the bridge has no C# test harness): every hand-card description the
state builder emits is preceded by `GitsRefreshHandPreview(card)`, and that
helper refreshes with hooks on (Hand pile, live combat), no target, inside a
try/catch.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a bridge.
"""
from __future__ import annotations

import re
from pathlib import Path

BRIDGE = Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
STATE_BUILDER = BRIDGE / "McpMod.StateBuilder.cs"
HELPER = BRIDGE / "gits" / "GitsFreshPreview.cs"

_HAND_DESC = 'SafeGetCardDescription(card); // hand cards use default pile'


def test_every_hand_description_is_read_after_a_refresh():
    lines = STATE_BUILDER.read_text(encoding="utf-8").splitlines()
    sites = [i for i, line in enumerate(lines) if _HAND_DESC in line]
    assert len(sites) == 2, "BuildCardState and the hand-select loop"
    for i in sites:
        window = "\n".join(lines[max(0, i - 8):i])
        assert "GitsRefreshHandPreview(card);" in window, lines[i]
        # Before BuildCardInfo, so nothing reads the card's vars stale.
        assert window.index("GitsRefreshHandPreview(card);") < \
            window.index("BuildCardInfo(card)")


def test_the_refresh_is_the_games_own_and_is_guarded():
    text = HELPER.read_text(encoding="utf-8")
    body = text[text.index("static void GitsRefreshHandPreview"):]
    assert re.search(r"\btry\b", body) and re.search(r"\bcatch\b", body)
    assert "IsInProgress: true" in body
    assert "card.Pile?.Type != PileType.Hand" in body
    assert "card.DynamicVars.ClearPreview();" in body
    assert ("card.UpdateDynamicVarPreview(CardPreviewMode.Normal, null, "
            "card.DynamicVars);") in body
    assert "card.Enchantment.DynamicVars.ClearPreview();" in body
    # A real hand card is never put into the one-way preview state.
    assert "UpgradePreviewType" not in body
