"""Klee's bone-and-mesh combat rig (tools/klee_rig).

klee-mod/pck-src/klee/model/combat.tscn is GENERATED from tools/klee_rig/
klee.yaml and the committed occupancy grid klee_cells.json. These tests hold
the parts that need neither the art nor the engine:

  * the shipped scene is exactly what the generator writes, and two runs are
    byte-identical (no set/dict ordering leaks into the text);
  * every Polygon2D is skinned through the FLAT `bones` array -- the
    `bones/0/path` spelling is dropped by MegaDot's parser without an error
    (bake-off, commit 09864c273) -- with one weight per vertex per bone;
  * the rest pose is exact by construction: polygon == uv + the old sprite's
    top-left, weights sum to 1 with at most four bones, Bone2D pose == rest;
  * the router contract: the scene nodes, the seven states plus RESET, the
    one-shot lengths and the state machine block are the old scene's.

Engine-side checks (get_bone_count() per polygon, the rendered rest pose
against the layered composite, facing parity) are `python -m tools.klee_rig
verify --godot`, which needs MegaDot and the art; the coverage test below
runs only where ImageGen/ exists.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.klee_rig import rig, verify

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def scene_text() -> str:
    return rig.SCENE.read_text(encoding="utf-8")


def test_generator_is_deterministic_and_matches_the_shipped_scene(scene_text):
    first = rig.render_scene()
    second = rig.render_scene()
    assert first == second
    assert first == scene_text, "combat.tscn is stale: run `python -m tools.klee_rig gen`"


def test_static_rest_contract_and_skin(scene_text):
    assert verify.static_problems(scene_text) == []


def test_every_polygon_uses_the_flat_bones_array(scene_text):
    nodes = verify.parse_nodes(scene_text)
    polys = [n for n in nodes.values() if n.type == "Polygon2D"]
    assert [p.name for p in polys] == ["Smoke", "Floaters", "Dumpty", "Body", "Dodoco"]
    for p in polys:
        assert "bones/0/path" not in scene_text
        bones = verify.parse_bones(p.props["bones"])
        assert bones, p.name
        n = len(verify.parse_vec_array(p.props["polygon"]))
        assert all(len(ws) == n for _b, ws in bones), p.name


def test_rest_pose_uv_equals_polygon_minus_topleft(scene_text):
    nodes = verify.parse_nodes(scene_text)
    for name, rec in rig.load_cells()["layers"].items():
        node = nodes[f"Visuals/Facing/Rig/{name}"]
        poly = verify.parse_vec_array(node.props["polygon"])
        uv = verify.parse_vec_array(node.props["uv"])
        tx, ty = rec["topleft"]
        assert poly == [(u + tx, v + ty) for u, v in uv], name


def test_all_seven_animations_and_reset(scene_text):
    anims = verify.track_paths(scene_text)
    assert set(anims) == {"RESET", *verify.STATES}
    for name in verify.STATES:
        assert anims[name], name
    # RESET is derived: it covers every property any state drives.
    driven = {p for name in verify.STATES for p in anims[name]}
    assert driven <= set(anims["RESET"])


def test_one_shot_lengths_are_the_base_clock(scene_text):
    # The base skeletons' one-shots (klee-visual-paper-2026-10-12): attack
    # 0.93-1.5 s, cast 0.97-1.8, hurt 0.73-1.0, die 1.87-4.17.
    for name, length in {"attack": 1.0, "hurt": 0.8, "death": 2.0, "cast": 1.0, "power": 1.0,
                         "setoff": 1.2}.items():
        assert f'resource_name = "{name}"\nlength = {rig.fnum(length)}\n' in scene_text


def test_the_splash_rig_rests_invisible_and_only_setoff_shows_it(scene_text):
    nodes = verify.parse_nodes(scene_text)
    assert nodes["Visuals/Facing/Rig"].props["modulate"] == "Color(1, 1, 1, 0)"
    anims = verify.track_paths(scene_text)
    showing = [a for a, paths in anims.items() if "Visuals/Facing/Rig:modulate" in paths and a != "RESET"]
    assert showing == ["setoff"]


def test_every_state_draws_one_sheet_from_the_manifest(scene_text):
    frames = rig.load_frames()
    spec = rig.load_spec()
    for state, anim in spec["animations"].items():
        assert anim["sheet"] in frames["sheets"], state
    nodes = verify.parse_nodes(scene_text)
    for name in spec["model"]["sheets"]:
        n = nodes[f"Visuals/Facing/Model/{rig.SHEET_NODE[name]}"]
        ox, oy = frames["sheets"][name]["origin"]
        assert n.props["offset"] == rig.vec2((-ox, -oy)), name
        assert n.props["texture"] == f'ExtResource("{rig.SHEET_IDS[name]}")', name


def test_travel_transitions_are_enabled_so_they_cross_fade():
    # advance_mode 0 (disabled) made every Travel teleport: no cross-fade.
    sm = rig.state_machine()
    assert 'id="Transition_idle_attack"]\nxfade_time = 0.1\nadvance_mode = 1' in sm
    assert 'id="Transition_attack_idle"]\nxfade_time = 0.05\nswitch_mode = 2\nadvance_mode = 2' in sm


def test_cells_grid_is_rectangular():
    for name, rec in rig.load_cells()["layers"].items():
        widths = {len(r) for r in rec["rows"]}
        assert len(widths) == 1, name
        w, h = rec["texture"]
        assert widths == {-(-w // rec["cell"])} and len(rec["rows"]) == -(-h // rec["cell"]), name


@pytest.mark.skipif(not (ROOT / "ImageGen" / "images" / "model" / "layers" / "combat").is_dir(),
                    reason="needs the combat layer art (gitignored ImageGen/)")
def test_mesh_covers_every_drawn_texel():
    assert verify.coverage_problems(ROOT) == []
