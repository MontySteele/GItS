"""The bridge drops a potion through the game's synced action.

2026-10-06 co-op seat round (Klee host, Varka client, seed 30KMHAVG9SMQ): the
client's belt was full, it dropped a potion to take a Tiny Mailbox reward, and
`ExecuteDiscardPotion` emptied the slot with `PotionCmd.Discard` on the client
only. The host saw a full belt, granted nothing, and the run was abandoned on
a checksum divergence. The multiplayer switch routes `discard_potion` to the
same method, so the method itself must enqueue `DiscardPotionGameAction`, as
the belt's own Discard button does (`NPotionPopup.OnDiscardButtonPressed`).
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "vendor" / "STS2_MCP"


def _method(src: str, name: str) -> str:
    start = src.index(f"Dictionary<string, object?> {name}(")
    nxt = src.find("private static ", start + 1)
    return src[start:nxt if nxt > 0 else len(src)]


def _code(body: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in body.splitlines())


def test_multiplayer_discard_routes_to_execute_discard_potion():
    mp = (BRIDGE / "McpMod.MultiplayerActions.cs").read_text(encoding="utf-8")
    route = re.search(r'"discard_potion"\s*=>\s*(\w+)\(', mp)
    assert route, "multiplayer switch lost its discard_potion arm"
    assert route.group(1) == "ExecuteDiscardPotion", route.group(1)


def test_discard_enqueues_the_synced_action_not_a_local_command():
    src = (BRIDGE / "McpMod.Actions.cs").read_text(encoding="utf-8")
    body = _code(_method(src, "ExecuteDiscardPotion"))
    assert "PotionCmd.Discard" not in body, (
        "ExecuteDiscardPotion calls PotionCmd.Discard directly: in co-op that "
        "discards on this machine only and the run desyncs")
    assert "ActionQueueSynchronizer.RequestEnqueue" in body
    assert "new DiscardPotionGameAction(" in body
