"""Furina sweep round (2026-10-14) text and display fixes.

1. Playing Ousia logged "Playing 'Pneuma'": the bridge read the card's title
   after the play was queued, and a two-faced card has turned over by then.
   The title is read before the play.
2. Neuvillette's act counts HP lost to her own Drains
   (`FurinaStageLedger.NoteDrain` adds to `HpLostSinceLastTurn`); his text
   says "lost or Drained".
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_the_bridge_names_the_face_played_not_the_face_after():
    src = (ROOT / "vendor/STS2_MCP/McpMod.Actions.cs").read_text(
        encoding="utf-8")
    title_at = src.index("string playedTitle = card.Title;")
    play_at = src.index("RequestEnqueue(new PlayCardAction(card, target))")
    assert title_at < play_at
    assert "$\"Playing '{playedTitle}'\"" in src
    assert "$\"Playing '{card.Title}'\"" not in src


def test_neuvilletes_act_text_says_drains_count():
    # The badge's keyed act row since the localization census (2026-10-23).
    from tools import lint_text_conventions as ltc
    assert ltc._guest_halves()["Neuvillette"][1].endswith(
        "equal to HP lost or [gold]Drained[/gold] since your last turn.")
