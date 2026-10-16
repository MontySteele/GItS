"""Kokomi's model-scene generator (tools/kokomi_rig), phase A of her model art.

Her frames were first rendered 2026-10-14 (tools/char_render/kokomi_frames.json,
committed); her layer-cut rig and the static merchant sprite no longer ship.
Most of these tests hold the generator against a SYNTHETIC manifest shaped
exactly as tools/char_render/pack.py writes one,
with her clips' real frame times (tools/char_render/kokomi_clips.py), so the
wire step after the render is `python -m tools.kokomi_rig gen` and nothing
more:

  * the generator is deterministic and keeps the router contract;
  * every frame is an AtlasTexture that restores its cell, stepped at the
    rendered times;
  * the water jet's layer draws over the attack from the manifest's frame
    and rests at Hydro;
  * the merchant loops stance B; the shadow sits under both;
  * the shipped scenes are what the generator writes from the real
    manifest, and her attack delay is that manifest's main impact;
  * build_pck copies her frames VRAM-compressed, switches rest and select
    art only when they exist, and writes no static merchant or layer rig.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from tools.kokomi_rig import __main__ as cli
from tools.kokomi_rig import rig

ROOT = Path(__file__).resolve().parents[2]


def _clips():
    spec = importlib.util.spec_from_file_location("kokomi_clips_t", ROOT / "tools" / "char_render" / "kokomi_clips.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


KC = _clips()


def _times(clip: dict) -> list[float]:
    """render.py's frame times for a clip."""
    fps = clip["fps"]
    if clip.get("motion_end"):
        return [round(i / fps, 6) for i in range(int(round(clip["motion_end"] * fps)) + 1)]
    return [round(i / fps, 6) for i in range(int(round(clip["length"] * fps)))]


def _sheet(file: str, n: int, cell=(300, 460), origin=(150, 440), per_page=40) -> dict:
    """A pack.py sheet record: n frames, shelf-packed 10 to a row, paged."""
    pages, frames = [], []
    for i in range(n):
        pg, j = divmod(i, per_page)
        frames.append({"page": pg, "rect": [(j % 10) * 120, (j // 10) * 200, 110, 190],
                       "offset": [10 + i % 3, 20 + i % 5]})
    for pg in range((n + per_page - 1) // per_page):
        name = file if pg == 0 else file.replace(".png", f"_p{pg + 1}.png")
        pages.append({"file": name, "count": sum(1 for f in frames if f["page"] == pg), "size": [1200, 800]})
    return {"cell": list(cell), "count": n, "pages": pages, "frames": frames, "origin": list(origin)}


def synthetic_frames() -> dict:
    sheets = {}
    for name, clip in KC.CLIPS.items():
        times = _times(clip)
        rec = _sheet(f"kokomi_{name}.png", len(times))
        rec.update({"fps": clip["fps"], "length": clip["length"], "loop": clip["loop"],
                    "motion_end": clip.get("motion_end"), "times": times, "ppu": 267.65})
        ev = clip.get("events")
        if ev:
            rec["events"] = ev
            rec["impact_frames"] = [round(t * clip["fps"]) for t in ev["impact"]]
            rec["main_frame"] = round(ev["main"] * clip["fps"])
        sheets[name] = rec
    atk = KC.CLIPS["attack"]
    first = round(atk["trails"][0]["from"] * atk["fps"]) + 1
    fx = _sheet("kokomi_attack_fx.png", 9, cell=(500, 600), origin=(200, 520))
    fx.update({"first_frame": first, "fps": atk["fps"], "heat": "R=G=B heat"})
    return {"char": "kokomi", "combat_scale": 0.5, "merchant_scale": 0.85, "texture_import": "vram_compressed",
            "sheets": sheets, "fx": {"attack": fx}, "effects": {},
            "shadow": {"file": "kokomi_shadow.png", "texture": [256, 64],
                       "combat": {"center": [0.0, -1.0], "size": [120.0, 22.0]},
                       "merchant": {"center": [0.0, -2.0], "size": [200.0, 36.0]}}}


@pytest.fixture(scope="module")
def frames() -> dict:
    return synthetic_frames()


@pytest.fixture(scope="module")
def scene_text(frames) -> str:
    return rig.render_scene(frames=frames)


def _anim(text: str, name: str) -> str:
    return text.split(f'[sub_resource type="Animation" id="Animation_{name}"]', 1)[1].split("\n[", 1)[0]


def test_the_generator_is_deterministic(frames, scene_text):
    assert rig.render_scene(frames=frames) == scene_text
    assert rig.render_merchant_scene(frames) == rig.render_merchant_scene(frames)


def test_the_router_contract(scene_text):
    for node in ("Visuals", "Facing", "Bounds", "CenterPos", "IntentPos", "AnimationPlayer", "AnimationTree"):
        assert re.search(rf'\[node name="{node}" [^\]]*\]\nunique_name_in_owner = true', scene_text), node
    for st in ("idle", "attack", "hurt", "death", "cast", "power", "idle_low"):
        assert f'animation = &"{st}"' in scene_text, st
    assert 'advance_condition = &"low_hp"' in scene_text and 'advance_condition = &"healthy"' in scene_text
    assert "metadata/idle_desync = true" in scene_text
    # phase A: no signature clip yet
    assert "rejoice" not in scene_text and "ascension" not in scene_text
    # the old rig's box, kept
    assert "offset_left = -120.0" in scene_text and "position = Vector2(0, -350)" in scene_text


def test_every_frame_is_an_atlas_texture_that_restores_its_cell(scene_text, frames):
    for name in rig.SHEET_NODE:
        rec = frames["sheets"][name]
        for i, fr in enumerate(rec["frames"]):
            block = scene_text.split(f'id="Atlas_{name}_{i}"]', 1)[1].split("\n\n", 1)[0]
            x, y, w, h = fr["rect"]
            assert f"region = Rect2({x}, {y}, {w}, {h})" in block, (name, i)
            ox, oy = fr["offset"]
            cw, ch = rec["cell"]
            assert f"margin = Rect2({ox}, {oy}, {cw - w}, {ch - h})" in block, (name, i)
        for p in rec["pages"]:
            assert f'path="res://kokomi/model/frames/{p["file"]}"' in scene_text


def test_each_state_steps_its_own_sheet_at_the_rendered_times(scene_text, frames):
    for state, sheet in (("idle", "idle"), ("attack", "attack"), ("hurt", "hurt"), ("death", "death"),
                         ("cast", "cast"), ("power", "cast"), ("idle_low", "idle_low")):
        block = _anim(scene_text, state)
        node = rig.SHEET_NODE[sheet]
        assert f'NodePath("Visuals/Facing/Model/{node}:texture")' in block, state
        assert block.count(f'SubResource("Atlas_{sheet}_') == frames["sheets"][sheet]["count"], state


def test_the_water_jet_draws_over_the_attack_from_the_manifests_frame_and_rests_at_hydro(scene_text, frames):
    node = scene_text.split('[node name="AttackFx" type="Sprite2D" parent="Visuals/Facing/Model"]', 1)[1]
    node = node.split("\n\n", 1)[0]
    assert "unique_name_in_owner = true" in node and 'metadata/rest_element = "hydro"' in node
    assert 'material = SubResource("ShaderMaterial_element")' in node
    assert "resource_local_to_scene = true" in scene_text
    block = _anim(scene_text, "attack")
    first = frames["fx"]["attack"]["first_frame"]
    t0 = frames["sheets"]["attack"]["times"][first]
    assert re.search(r'"times": PackedFloat32Array\(0, ' + re.escape(f"{t0:g}"), block), "shown from its first frame"
    for st in ("idle", "hurt", "cast"):
        assert 'NodePath("Visuals/Facing/Model/AttackFx:self_modulate")' in _anim(scene_text, st)


def test_the_merchant_loops_stance_b_and_both_scenes_carry_the_shadow(scene_text, frames):
    text = rig.render_merchant_scene(frames)
    assert '[node name="KokomiMerchant" type="Node2D"]' in text and 'autoplay = "relaxed_loop"' in text
    assert text.count('SubResource("Atlas_merchant_') >= frames["sheets"]["merchant"]["count"]
    for t in (scene_text, text):
        assert 'path="res://kokomi/model/frames/kokomi_shadow.png"' in t
        assert '[node name="Shadow" type="Sprite2D"' in t


def test_one_shot_lengths_are_the_clips(frames):
    for name, length in rig.ONE_SHOT_LENGTHS.items():
        sheet = "cast" if name == "power" else name
        assert KC.CLIPS[sheet]["length"] == length, name
    assert set(rig.load_spec()["model"]["sheets"]) == set(rig.SHEET_NODE) == set(KC.CLIPS) - {"merchant"}


def test_the_shipped_scenes_are_the_generators_now_she_is_rendered():
    assert rig.FRAMES.exists()
    assert cli.main(["gen", "--check"]) == 0
    assert rig.SCENE.read_text(encoding="utf-8") == rig.render_scene()
    assert rig.MERCHANT_SCENE.read_text(encoding="utf-8") == rig.render_merchant_scene()
    # her layer-cut rig no longer ships
    assert "kokomi_combat_body.png" not in rig.SCENE.read_text(encoding="utf-8")


def test_her_attack_hit_lands_on_the_clips_main_impact():
    real = json.loads(rig.FRAMES.read_text(encoding="utf-8"))
    cs = (ROOT / "klee-mod" / "KleeCode" / "Kokomi.cs").read_text(encoding="utf-8")
    delay = float(re.search(r"AttackAnimDelay => ([0-9.]+)f;", cs).group(1))
    assert delay == pytest.approx(real["sheets"]["attack"]["events"]["main"])


def test_the_pack_copies_her_frames_compressed_and_switches_rest_and_select_only_when_present():
    ps = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8-sig")
    block = ps.split("$kokomiFrames = Join-Path $src 'kokomi\\model\\frames'", 1)[1].split("\n}\n", 1)[0]
    assert "Write-TextureImport" in block and "Test-Path $kokomiFrames" in block
    assert "Test-Path (Join-Path $src 'kokomi\\model\\kokomi_rest.png')" in ps
    assert "\"res://kokomi/model/$kokomiRestArt\"" in ps
    assert "Test-Path (Join-Path $src 'kokomi\\ui\\select_closeup.png')" in ps
    assert "\"res://kokomi/ui/$kokomiSelectArt\"" in ps
    # the generated merchant scene replaced the static sprite; the old rig's layers no longer ship
    assert "'kokomi\\model\\merchant_character.tscn'" not in ps
    assert "$rigChar" not in ps and "kokomi\\model\\layers" not in ps
