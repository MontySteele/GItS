"""A finished Crystal Sphere under the open map reads as the map in co-op.

2026-10-06 co-op seat round (Klee host lane 2, Varka client lane 3, act 2
floor 28): both players chose Uncover Future, spent their divinations, took
the gold and pressed proceed. The game opened the map (both bridges answered
`choose_map_node` with "2 options available"), but `/api/v1/multiplayer`
kept printing `crystal_sphere` with `can_proceed: false`, "0 Divinations
remain" and every unrevealed cell as clickable, and the page offered `reveal`
on cells the game ignores.

Why, from the decompiled game:
- `RunManager.ProceedFromTerminalRewardsScreen` only opens the map; the
  sphere overlay stays on `NOverlayStack` until `ClearScreens` on the next
  room.
- `NOverlayStack` connects `NMapScreen.Opened` to `HideOverlays`, which calls
  `Peek()?.AfterOverlayHidden()`, and `NCrystalSphereScreen.AfterOverlayHidden`
  is `_proceedButton.Disable()`.
- `NCrystalSphereScreen.OnCellClicked` does nothing once `DivinationCount` is
  0, and `OnMinigameFinished` hides the tool buttons but not the cells.

The singleplayer builder already guarded the sphere branch with `!mapIsOpen`
(upstream issue #73); the multiplayer builder did not.
"""
from __future__ import annotations

import re
from pathlib import Path

from understudy import blindplay
from understudy.blindplay_shape import sphere_owes

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "vendor" / "STS2_MCP"


def _code(src: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in src.splitlines())


def _mp_builder() -> str:
    return _code((BRIDGE / "McpMod.MultiplayerState.cs").read_text(
        encoding="utf-8"))


def test_multiplayer_sphere_branch_yields_to_the_open_map():
    src = _mp_builder()
    branch = re.search(r"else if \(([^)]*)topOverlay is NCrystalSphereScreen "
                       r"crystalSphereScreen\)", src)
    assert branch, "multiplayer builder lost its crystal_sphere branch"
    assert "!mapIsOpen" in branch.group(1), (
        "the co-op sphere branch must not fire while the map is open: the "
        "map disables the sphere's proceed button and leaves it on the stack")


def test_multiplayer_overlay_catch_all_excludes_the_sphere():
    src = _mp_builder()
    start = src.index("topOverlay is IOverlayScreen")
    head = src[start:src.index("{", start)]
    assert "topOverlay is not NCrystalSphereScreen" in head, (
        "a sphere under the open map must fall through to the room's map "
        "branch, not the generic overlay catch-all")


def _finished_sphere(can_proceed: bool) -> dict:
    """The live wire on lanes 2 and 3 before the fix: buttons hidden, cells
    still listed, proceed disabled by the map."""
    return {"state_type": "crystal_sphere",
            "crystal_sphere": {
                "grid_width": 2, "grid_height": 1,
                "cells": [{"x": 0, "y": 0, "is_hidden": True,
                           "is_clickable": True}],
                "clickable_cells": [{"x": 0, "y": 0}],
                "revealed_items": [],
                "tool": "big", "can_use_big_tool": False,
                "can_use_small_tool": False,
                "divinations_left_text": "0 Divinations remain",
                "can_proceed": can_proceed}}


def test_a_finished_sphere_owes_nothing_and_offers_no_reveal():
    state = _finished_sphere(can_proceed=False)
    assert not sphere_owes(state["crystal_sphere"])
    obs = blindplay.observation(state)
    assert "reveal" not in obs["commands"]
    assert blindplay.act(state, "reveal")["refusal"]


def test_a_finished_sphere_that_can_proceed_offers_leave():
    state = _finished_sphere(can_proceed=True)
    obs = blindplay.observation(state)
    assert obs["commands"] == ["leave"]
    assert blindplay.act(state, "leave")["post"] == {
        "action": "crystal_sphere_proceed"}


def test_an_older_feed_without_tool_keys_reads_as_before():
    blob = _finished_sphere(can_proceed=False)["crystal_sphere"]
    del blob["can_use_big_tool"], blob["can_use_small_tool"]
    assert sphere_owes(blob)
