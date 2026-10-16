"""The event heading reads the local player's copy (co-op story rooms, 2026-10-16).

THE FIND. In a co-op seat run the Varka player's story pages carried the right
options under the heading "A Quiet Landing", the placeholder's. A co-op story
room is one canonical `StoryCoopRoomEvent`; each player's mutable copy routes
to that player's event (`klee-mod/KleeCode/Story/StoryEvents.cs`), but the
canonical copy is never routed, so its Title is the placeholder's.
`BuildEventState` read `event_name` off `eventRoom.CanonicalEvent`.

THE GAME WAS RIGHT. `EventRoom.EnterInternal` hands
`EventSynchronizer.GetLocalEvent()` to `NEventRoom.Create`, and
`NEventRoom.SetupLayout` calls `SetTitle(_event.Title)` on that copy. Only
the bridge read the canonical one.

WHAT IS PINNED HERE. A SOURCE assertion (the bridge has no C# test harness):
`event_name` reads the local copy through the `GitsLocalEvent.OrNothing`
guard, falling back to the canonical event.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a bridge.
"""
from __future__ import annotations

from pathlib import Path

STATE_BUILDER = (Path(__file__).resolve().parents[2]
                 / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs")


def _body(text: str, signature: str) -> str:
    start = text.index(signature)
    end = text.index("\n    private static ", start + len(signature))
    return text[start:end]


def test_event_name_reads_the_local_copy_with_canonical_fallback():
    body = _body(STATE_BUILDER.read_text(encoding="utf-8"),
                 "object?> BuildEventState(EventRoom eventRoom")
    local = ("GitsLocalEvent.OrNothing(() => eventRoom.LocalMutableEvent)"
             " ?? eventModel;")
    assert local in body
    assert 'state["event_name"] = SafeGetText(() => titleModel.Title);' in body
    assert 'state["event_name"] = SafeGetText(() => eventModel.Title);' not in body
