"""Each kit's card trail, the parts checkable without a game.

[USER], 2026-10-23: "Card trail - can we make our own trails?" Every kit flies
its cards on its own recoloured copy of the base trail scene
(`tools/gen_card_trails.py`, colours from `CardFrameColors.cs`). Pinned here:
the committed scenes are the generator's, each one is the base shape with the
base game's scripts and textures referenced by path (never copied), the
scene-deps gate lets exactly those base paths through, and every character
points at its own scene with the base trail as the fallback.

Still owed, and only the game can say: that the instance casts to
`NCardTrailVfx` from our pack and draws.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import gen_card_trails as gen                                  # noqa: E402
from tools.visual_qa import godot_scene, scene_deps           # noqa: E402
from tools.visual_qa.findings import Report                   # noqa: E402

CHARACTERS = {"klee": "Klee", "furina": "Furina", "kokomi": "Kokomi",
              "varka": "Varka", "yae": "Yae"}


def test_every_committed_trail_matches_the_generator():
    assert gen.check() == []


def test_the_generator_reads_every_kit_colour_from_the_table():
    colours = gen.kit_colours()
    assert set(colours) == set(CHARACTERS)
    assert colours["yae"] == "D63CC8"
    assert colours["kokomi"] == "E89A86"


def test_each_trail_keeps_the_base_shape_and_references_only_base_paths():
    for kit in CHARACTERS:
        text = gen.out_path(kit).read_text(encoding="utf-8")
        # No scene uid of its own: the base scene's would collide.
        assert text.startswith("[gd_scene load_steps=15 format=3]\n"), kit
        paths = re.findall(r'\[ext_resource [^\]]*path="res://([^"]+)"', text)
        assert set(paths) == set(scene_deps.BASE_GAME_RESOURCES), kit
        for node in ("Trails/OuterTrail", "Trails/InnerTrail", "Sprites/BigSparks",
                     "Sprites/LittleSparks", "Sprites/Sprite2D2", "Sprites/Sprite2D3"):
            parent, name = node.split("/")
            assert f'[node name="{name}"' in text and f'parent="{parent}"' in text, (kit, node)


def test_the_trails_are_clean_under_scene_deps_even_against_a_universe():
    for kit in CHARACTERS:
        path = gen.out_path(kit)
        report = Report(scene_deps.GATE)
        scene_deps.check_scene(godot_scene.parse(path), report, kit, universe=set())
        assert report.errors == [], [f.detail for f in report.errors]


def test_any_other_script_is_still_sd_script():
    text = gen.out_path("yae").read_text(encoding="utf-8").replace(
        "res://src/Core/Nodes/Vfx/NCardTrail.cs", "res://yae/vfx/our_trail.cs")
    report = Report(scene_deps.GATE)
    scene_deps.check_scene(godot_scene.parse(gen.out_path("yae"), text), report, "yae")
    assert "SD-SCRIPT" in {f.rule for f in report.errors}


def test_every_character_points_at_its_own_trail():
    for kit, name in CHARACTERS.items():
        src = (ROOT / "klee-mod" / "KleeCode" / f"{name}.cs").read_text(encoding="utf-8")
        assert f'KleePck.Path("{kit}/vfx/card_trail.tscn")' in src, name


def test_the_boot_log_names_every_trail():
    telemetry = (ROOT / "klee-mod" / "KleeCode" / "Diagnostics"
                 / "KleeSceneTelemetry.cs").read_text(encoding="utf-8")
    for kit in CHARACTERS:
        assert f'"{kit}/vfx/card_trail.tscn"' in telemetry, kit
