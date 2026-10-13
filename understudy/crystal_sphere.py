"""The Crystal Sphere's divinations, read off the wire (2026-09-26).

Shared by the seat page's `reveal` (`blindplay_shape`) and the soak's forced
move (`soak_screens`): the game refuses `crystal_sphere_proceed` while
divinations are owed, so both spend them first. A neutral module because the
soak may not import any blindplay file
(`test_soak_never_imports_blindplay`).
"""

from __future__ import annotations

from typing import Any


def sphere_owes(blob: dict[str, Any]) -> bool:
    """Does the Crystal Sphere still refuse to let the run go on, with a
    hidden cell left to spend a divination on? False on a feed that sends
    no `can_proceed` (an older bridge), which keeps `leave` as it was."""
    if not isinstance(blob, dict) or "can_proceed" not in blob:
        return False
    # 2026-10-06 (co-op, Klee + Varka, lanes 2 and 3): a FINISHED sphere owes
    # nothing. The game hides both divination buttons when the minigame ends
    # (`NCrystalSphereScreen.OnMinigameFinished`) but leaves the unrevealed
    # cells visible, so the feed still lists them as clickable -- and a click
    # there is a no-op (`OnCellClicked` returns while `DivinationCount` is 0).
    # With the sphere stranded under the open map (`can_proceed` false) the
    # page offered `reveal` on those cells forever. No tool offered means
    # nothing left to spend; a feed without the tool keys reads as before.
    if ("can_use_big_tool" in blob or "can_use_small_tool" in blob) and not (
            blob.get("can_use_big_tool") or blob.get("can_use_small_tool")):
        return False
    return (blob.get("can_proceed") is not True
            and bool(blob.get("clickable_cells")))


def sphere_reveal_action(blob: dict[str, Any]) -> dict[str, Any] | None:
    """The one post `reveal` makes, or None where there is nothing to reveal:
    select a tool where none is selected (the big one where the game offers
    it), else click the first hidden cell with the tool selected."""
    if not sphere_owes(blob):
        return None
    tool = str(blob.get("tool") or "none")
    if tool not in ("big", "small"):
        pick = ("big" if blob.get("can_use_big_tool")
                else "small" if blob.get("can_use_small_tool") else "")
        if pick:
            return {"action": "crystal_sphere_set_tool", "tool": pick}
    cell = next((c for c in blob.get("clickable_cells") or []
                 if isinstance(c, dict)
                 and c.get("x") is not None and c.get("y") is not None),
                None)
    if cell is None:
        return None
    return {"action": "crystal_sphere_click_cell",
            "x": int(cell["x"]), "y": int(cell["y"])}
