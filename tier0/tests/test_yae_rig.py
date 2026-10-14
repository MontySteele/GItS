"""Yae Miko's model-scene generator (tools/yae_rig), phase A of her model
art, a temporary model.

Her frames are not rendered yet (2026-10-14: the game was in use, so no
Blender), so tools/char_render/yae_frames.json does not exist and her
placeholder (Klee's still at her path) still ships. These tests hold the
generator against a SYNTHETIC manifest shaped exactly as
tools/char_render/pack.py writes one, with her clips' real frame times
(tools/char_render/yae_clips.py), so the wire step after the render is
`python -m tools.yae_rig gen` and nothing more:

  * the generator is deterministic and keeps the router contract;
  * every frame is an AtlasTexture that restores its cell, stepped at the
    rendered times;
  * the fox spirit's layer draws over the attack from the manifest's frame
    and rests at Electro;
  * the merchant loops stance B; the shadow sits under both;
  * once the real manifest exists, the shipped scenes are what the
    generator writes (until then the CLI says so and the check passes);
  * build_pck copies her frames VRAM-compressed and switches rest and select
    art only when they exist, and Yae.cs loads the scene first.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from tools.yae_rig import __main__ as cli
from tools.yae_rig import rig

ROOT = Path(__file__).resolve().parents[2]


def _clips():
    spec = importlib.util.spec_from_file_location("yae_clips_t", ROOT / "tools" / "char_render" / "yae_clips.py")
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
        rec = _sheet(f"yae_{name}.png", len(times))
        rec.update({"fps": clip["fps"], "length": clip["length"], "loop": clip["loop"],
                    "motion_end": clip.get("motion_end"), "times": times, "ppu": 267.89})
        ev = clip.get("events")
        if ev:
            rec["events"] = ev
            rec["impact_frames"] = [round(t * clip["fps"]) for t in ev["impact"]]
            rec["main_frame"] = round(ev["main"] * clip["fps"])
        sheets[name] = rec
    atk = KC.CLIPS["attack"]
    first = round(atk["trails"][0]["from"] * atk["fps"]) + 1
    fx = _sheet("yae_attack_fx.png", 9, cell=(500, 600), origin=(200, 520))
    fx.update({"first_frame": first, "fps": atk["fps"], "heat": "R=G=B heat"})
    return {"char": "yae", "combat_scale": 0.5, "merchant_scale": 0.85, "texture_import": "vram_compressed",
            "sheets": sheets, "fx": {"attack": fx}, "effects": {},
            "shadow": {"file": "yae_shadow.png", "texture": [256, 64],
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
    # Kokomi's box scaled to her body (x 1.11)
    assert "offset_left = -133.0" in scene_text and "offset_top = -311.0" in scene_text
    assert "position = Vector2(0, -389)" in scene_text


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
            assert f'path="res://yae/model/frames/{p["file"]}"' in scene_text


def test_each_state_steps_its_own_sheet_at_the_rendered_times(scene_text, frames):
    for state, sheet in (("idle", "idle"), ("attack", "attack"), ("hurt", "hurt"), ("death", "death"),
                         ("cast", "cast"), ("power", "cast"), ("idle_low", "idle_low")):
        block = _anim(scene_text, state)
        node = rig.SHEET_NODE[sheet]
        assert f'NodePath("Visuals/Facing/Model/{node}:texture")' in block, state
        assert block.count(f'SubResource("Atlas_{sheet}_') == frames["sheets"][sheet]["count"], state


def test_the_fox_spirit_draws_over_the_attack_from_the_manifests_frame_and_rests_at_electro(scene_text, frames):
    node = scene_text.split('[node name="AttackFx" type="Sprite2D" parent="Visuals/Facing/Model"]', 1)[1]
    node = node.split("\n\n", 1)[0]
    assert "unique_name_in_owner = true" in node and 'metadata/rest_element = "electro"' in node
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
    assert '[node name="YaeMerchant" type="Node2D"]' in text and 'autoplay = "relaxed_loop"' in text
    assert text.count('SubResource("Atlas_merchant_') >= frames["sheets"]["merchant"]["count"]
    for t in (scene_text, text):
        assert 'path="res://yae/model/frames/yae_shadow.png"' in t
        assert '[node name="Shadow" type="Sprite2D"' in t


def test_one_shot_lengths_are_the_clips(frames):
    for name, length in rig.ONE_SHOT_LENGTHS.items():
        sheet = "cast" if name == "power" else name
        assert KC.CLIPS[sheet]["length"] == length, name
    assert set(rig.load_spec()["model"]["sheets"]) == set(rig.SHEET_NODE) == set(KC.CLIPS) - {"merchant"}


def test_the_shipped_scenes_are_the_generators_once_she_is_rendered(capsys):
    if not rig.FRAMES.exists():
        assert cli.main(["gen", "--check"]) == 0
        assert "does not exist yet" in capsys.readouterr().out
        assert cli.main(["gen"]) == 2
        # her placeholder still ships until the render lands: no scene yet
        assert not rig.SCENE.exists() and not rig.MERCHANT_SCENE.exists()
        return
    assert rig.SCENE.read_text(encoding="utf-8") == rig.render_scene()
    assert rig.MERCHANT_SCENE.read_text(encoding="utf-8") == rig.render_merchant_scene()


def test_the_pack_copies_her_frames_compressed_and_switches_rest_and_select_only_when_present():
    ps = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8-sig")
    block = ps.split("$yaeFrames = Join-Path $src 'yae\\model\\frames'", 1)[1].split("\n}\n", 1)[0]
    assert "Write-TextureImport" in block and "Test-Path $yaeFrames" in block
    assert "Test-Path (Join-Path $src 'yae\\model\\yae_rest.png')" in ps
    assert "\"res://yae/model/$yaeRestArt\"" in ps
    assert "Test-Path (Join-Path $src 'yae\\ui\\select_closeup.png')" in ps
    assert "\"res://yae/ui/$yaeSelectArt\"" in ps
    # Klee's placeholders stay the fallback at every path her art does not fill
    assert "Copy-YaeFallback $relative" in ps


def test_yae_loads_her_scene_first_and_keeps_the_still_as_the_fallback():
    cs = (ROOT / "klee-mod" / "KleeCode" / "Yae.cs").read_text(encoding="utf-8")
    body = cs.split("CreateCustomVisuals()", 1)[1]
    assert body.index('KleePck.Path("yae/model/combat.tscn")') < body.index('KleePck.Path("yae/model/combat_model.png")')
