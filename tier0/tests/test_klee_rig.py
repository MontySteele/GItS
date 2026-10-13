"""Klee's generated combat scene (tools/klee_rig).

klee-mod/pck-src/klee/model/combat.tscn is GENERATED from tools/klee_rig/
klee.yaml and the committed frame manifest klee_frames.json. These tests hold
the parts that need neither the art nor the engine:

  * the shipped scene is exactly what the generator writes, and two runs are
    byte-identical (no set/dict ordering leaks into the text);
  * the router contract: the scene nodes, the seven states plus `setoff` and
    RESET, the one-shot lengths and the state machine block;
  * every state, `setoff` included, draws a sheet of the official model, and
    the old floating-splash rig is gone (owner, 2026-10-13: "I regret keeping
    that around").

Engine-side checks (the AnimationTree driven through its states, the merchant
loop) are `python -m tools.klee_rig verify --godot`, which needs MegaDot and
the art.
"""
from __future__ import annotations

import pytest

from tools.klee_rig import rig, verify


@pytest.fixture(scope="module")
def scene_text() -> str:
    return rig.SCENE.read_text(encoding="utf-8")


def test_generator_is_deterministic_and_matches_the_shipped_scene(scene_text):
    first = rig.render_scene()
    second = rig.render_scene()
    assert first == second
    assert first == scene_text, "combat.tscn is stale: run `python -m tools.klee_rig gen`"


def test_static_contract(scene_text):
    assert verify.static_problems(scene_text) == []


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
    # 0.93-1.5 s, cast 0.97-1.8, hurt 0.73-1.0, die 1.87-4.17. Set Off is a
    # quick cheer, 0.85 s; Jumpy Dumpty's two-handed heave is heavier, 1.2 s.
    for name, length in {"attack": 1.0, "hurt": 0.8, "death": 2.0, "cast": 1.0, "power": 1.0,
                         "setoff": 0.85, "jumpy": 1.2}.items():
        assert f'resource_name = "{name}"\nlength = {rig.fnum(length)}\n' in scene_text


def test_the_old_splash_rig_is_gone(scene_text):
    nodes = verify.parse_nodes(scene_text)
    assert "Visuals/Facing/Rig" not in nodes
    assert not any(n.type in ("Skeleton2D", "Bone2D", "Polygon2D") for n in nodes.values())
    assert "res://klee/model/layers/" not in scene_text


def test_set_off_plays_its_own_model_sheet(scene_text):
    spec = rig.load_spec()
    assert spec["animations"]["setoff"]["sheet"] == "setoff"
    assert "hold_frame" not in spec["animations"]["setoff"]
    anims = verify.track_paths(scene_text)
    assert "Visuals/Facing/Model/SetOff:frame" in anims["setoff"]


def test_jumpy_dumpty_plays_its_own_sheet_and_throws_the_big_bomb(scene_text):
    spec = rig.load_spec()
    assert spec["animations"]["jumpy"]["sheet"] == "jumpy"
    anims = verify.track_paths(scene_text)
    assert "Visuals/Facing/Model/Jumpy:frame" in anims["jumpy"]
    nodes = verify.parse_nodes(scene_text)
    big = nodes["Visuals/Facing/JumpyProjectile"]
    assert big.type == "Sprite2D" and big.props["visible"] == "false"
    assert 'path="res://klee/model/frames/klee_bomb_big.png" id="10_bomb_big"' in scene_text
    # the attack still throws its own, smaller bomb
    assert nodes["Visuals/Facing/ThrownProjectile"].props["texture"] == 'ExtResource("8_bomb")'
    # every live state can cut to it, and it fades back to idle like a cast
    sm = rig.state_machine()
    assert 'id="Transition_idle_jumpy"]\nxfade_time = 0.1\nadvance_mode = 1' in sm
    assert 'id="Transition_jumpy_idle"]\nxfade_time = 0.05\nswitch_mode = 2\nadvance_mode = 2' in sm


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
    # Set Off starts and ends in stance A: it fades like a cast, both ways.
    assert 'id="Transition_idle_setoff"]\nxfade_time = 0.05\nadvance_mode = 1' in sm
    assert 'id="Transition_setoff_idle"]\nxfade_time = 0.05\nswitch_mode = 2\nadvance_mode = 2' in sm
