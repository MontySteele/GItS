"""Varka's generated model scenes (tools/varka_rig), phase B of his model art.

klee-mod/pck-src/varka/model/combat.tscn and merchant_character.tscn are
GENERATED from tools/varka_rig/varka.yaml and the committed manifest
tools/char_render/varka_frames.json. [USER], 2026-10-13: "Ok, the Varka one
looks good! I think doing more requires I see it in-game; let's ship it! (a)"

These tests hold what needs neither the art nor the engine:

  * the shipped scenes are what the generator writes, byte-identically;
  * the manifest reading: every frame an AtlasTexture whose margin restores
    the clip's cell, on the page the manifest names;
  * the router contract plus `ascension`, and the trigger that reaches it;
  * the element layer: drawn over the attack and the ascension from the
    frames the manifest names, coloured by one shader whose colours are the
    mod's element table;
  * the ground burst: two copies from the ascension's impact frame, one at
    the blade's point and one mirrored for the target;
  * the pack: VRAM-compressed imports, the rest/select switches, and one
    producer for every out-path.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.klee_rig import verify
from tools.varka_rig import rig

ROOT = Path(__file__).resolve().parents[2]
CS = ROOT / "klee-mod" / "KleeCode"


@pytest.fixture(scope="module")
def scene_text() -> str:
    return rig.SCENE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def frames() -> dict:
    return rig.load_frames()


def _keys(text: str, anim: str, path: str) -> tuple[list[float], list[str]]:
    """(times, values) of one track of one animation."""
    block = text.split(f'[sub_resource type="Animation" id="Animation_{anim}"]', 1)[1].split("\n[", 1)[0]
    m = re.search(r'tracks/(\d+)/path = NodePath\("' + re.escape(path) + r'"\)', block)
    assert m, f"{anim}: no track {path}"
    i = m.group(1)
    keys = block.split(f"tracks/{i}/keys = {{", 1)[1].split("\n}", 1)[0]
    times = [float(x) for x in re.search(r'"times": PackedFloat32Array\(([^)]*)\)', keys).group(1).split(", ")]
    values = re.search(r'"values": \[(.*)\]', keys).group(1)
    return times, re.findall(r'SubResource\("[^"]+"\)|Color\([^)]*\)', values)


def test_the_generator_is_deterministic_and_matches_both_shipped_scenes(scene_text):
    assert rig.render_scene() == rig.render_scene() == scene_text, \
        "combat.tscn is stale: run `python -m tools.varka_rig gen`"
    assert rig.render_merchant_scene() == rig.MERCHANT_SCENE.read_text(encoding="utf-8")


def test_the_router_contract_and_the_ascension_state(scene_text):
    nodes = verify.parse_nodes(scene_text)
    for p in verify.CONTRACT_NODES:
        assert p in nodes, p
    anims = verify.track_paths(scene_text)
    assert set(anims) == {"RESET", *rig.ANIMATION_ORDER}
    for name, length in rig.ONE_SHOT_LENGTHS.items():
        assert f'resource_name = "{name}"\nlength = {rig.fnum(length)}\n' in scene_text
    assert rig.STATE_MACHINE in scene_text
    for name, paths in anims.items():
        for p in paths:
            assert p.split(":")[0] in nodes, f"{name}: track to a missing node {p}"
    # the old layer-cut rig is gone
    assert "Visuals/Facing/Rig" not in nodes and "res://varka/model/layers/" not in scene_text
    # the scene opts in to the base game's random idle speed, as Klee's does
    assert "metadata/idle_desync = true" in scene_text


def test_every_frame_is_an_atlas_texture_that_restores_its_cell(scene_text, frames):
    spec = rig.load_spec()
    clips = rig.clips_of(spec, frames)
    for key, clip in clips.items():
        cw, ch = clip.rec["cell"]
        for fr, atlas in zip(clip.rec["frames"], clip.atlases):
            x, y, w, h = fr["rect"]
            mx, my, mw, mh = atlas.margin
            assert (w + mw, h + mh) == (cw, ch) and (mx, my) == tuple(fr["offset"]), key
            page = clip.rec["pages"][fr["page"]]
            assert x + w <= page["size"][0] and y + h <= page["size"][1], key
            block = (f'[sub_resource type="AtlasTexture" id="{atlas.id}"]\n'
                     f'atlas = ExtResource("{atlas.page_id}")\n'
                     f'region = Rect2({x}, {y}, {w}, {h})\n'
                     f'margin = Rect2({mx}, {my}, {mw}, {mh})\n')
            assert block in scene_text, atlas.id
        for ext_id, file in clip.pages:
            assert f'path="res://varka/model/frames/{file}" id="{ext_id}"' in scene_text
    # the sprite's offset puts the cell's feet anchor on the node origin
    nodes = verify.parse_nodes(scene_text)
    for name in spec["model"]["sheets"]:
        ox, oy = frames["sheets"][name]["origin"]
        assert nodes[f"Visuals/Facing/Model/{rig.SHEET_NODE[name]}"].props["offset"] == rig.vec2((-ox, -oy))


def test_each_state_steps_its_own_sheet_at_the_rendered_times(scene_text, frames):
    spec = rig.load_spec()
    for state in rig.ANIMATION_ORDER:
        sheet = spec["animations"][state]["sheet"]
        times, values = _keys(scene_text, state, f"Visuals/Facing/Model/{rig.SHEET_NODE[sheet]}:texture")
        assert times == pytest.approx(frames["sheets"][sheet]["times"], abs=1e-4)
        assert values == [f'SubResource("Atlas_{sheet}_{i}")' for i in range(len(times))]


def test_the_ascension_is_triggered_by_four_winds_ascension_and_absorbs_its_lunge():
    router = (CS / "Vfx" / "CreatureAnimationRouter.cs").read_text(encoding="utf-8")
    assert '["Ascension"] = new[] { "ascension", "attack" },' in router
    assert "currentState is SetOffState or JumpyState or AscensionState" in router
    motion = (CS / "Vfx" / "CardPlayMotion.cs").read_text(encoding="utf-8")
    assert "=> card is ProtoVkFourWindsAscension;" in motion
    assert "IsAscensionPlay(card) ? AscensionTrigger" in motion
    # only that card: the visual paper names no other move for the clip
    paper = (ROOT / "review" / "active" / "varka-visual-paper-2026-10-13.md").read_text(encoding="utf-8")
    assert "Northwind" not in paper


def test_the_element_layer_draws_over_the_attack_and_the_ascension_from_the_manifests_frame(scene_text, frames):
    for clip, node in rig.FX_NODE.items():
        fx = frames["fx"][clip]
        path = f"Visuals/Facing/Model/{node}"
        times, values = _keys(scene_text, clip, f"{path}:texture")
        first = fx["first_frame"]
        assert times == pytest.approx(frames["sheets"][clip]["times"][first:first + fx["count"]], abs=1e-4)
        assert len(values) == fx["count"]
        show_t, show_v = _keys(scene_text, clip, f"{path}:self_modulate")
        assert show_t[1] == pytest.approx(times[0]) and show_v[1] == "Color(1, 1, 1, 1)"
        assert show_v[0] == show_v[2] == "Color(1, 1, 1, 0)"
        # hidden in every other state
        for state in rig.ANIMATION_ORDER:
            if rig.load_spec()["animations"][state]["sheet"] != clip:
                assert _keys(scene_text, state, f"{path}:self_modulate")[1] == ["Color(1, 1, 1, 0)"], state


def test_the_ground_burst_plays_twice_from_the_impact_frame_at_the_blade_and_mirrored_for_the_target(
        scene_text, frames):
    use = frames["effects"]["ground_burst"]["uses"][0]
    assert use["clip"] == "ascension" and use["both_positions"] and use["mirror"]
    t0 = frames["sheets"]["ascension"]["times"][use["start_frame"]]
    assert use["start_frame"] == frames["sheets"]["ascension"]["main_frame"]
    sc = frames["combat_scale"]
    nodes = verify.parse_nodes(scene_text)
    blade = nodes["Visuals/Facing/GroundBurst"].props
    target = nodes["Visuals/Facing/TargetBurst"].props
    tip = next(p for p in use["places"] if p["at"] == "blade_tip")
    assert blade["position"] == rig.vec2((tip["offset_px"][0] * sc, tip["offset_px"][1] * sc))
    assert blade["scale"] == rig.vec2((sc, sc))
    assert target["scale"] == rig.vec2((-sc, sc))            # mirrored about the ground point
    assert blade["metadata/place"] == '"blade_tip"' and target["metadata/place"] == '"target"'
    for props in (blade, target):
        assert props["unique_name_in_owner"] == "true"
        ox, oy = frames["effects"]["ground_burst"]["origin"]
        assert props["offset"] == rig.vec2((-ox, -oy))
    count = frames["effects"]["ground_burst"]["count"]
    for node in ("GroundBurst", "TargetBurst"):
        times, values = _keys(scene_text, "ascension", f"Visuals/Facing/{node}:texture")
        assert times[0] == pytest.approx(t0) and len(times) == count
        assert values == [f'SubResource("Atlas_burst_{i}")' for i in range(count)]
        assert times[-1] < rig.ONE_SHOT_LENGTHS["ascension"]
        assert _keys(scene_text, "attack", f"Visuals/Facing/{node}:self_modulate")[1] == ["Color(1, 1, 1, 0)"]


def test_one_material_tints_every_layer_with_the_mods_element_colours(scene_text):
    fx_py = (ROOT / "tools" / "char_render" / "fx.py").read_text(encoding="utf-8")
    fx_elements = dict(re.findall(r'"(\w+)": "(#[0-9a-f]{6})"', fx_py.split("ELEMENTS = {", 1)[1].split("}", 1)[0]))
    assert rig.ELEMENT_HEX == fx_elements
    reaction = (CS / "Vfx" / "ReactionFx.cs").read_text(encoding="utf-8")
    table = reaction.split("ElementFlashHex(Element element)", 1)[1].split("};", 1)[0]
    cs = {name.lower(): hexc for name, hexc in re.findall(r'Element\.(\w+) => "(#[0-9a-f]{6})"', table)}
    cs["anemo"] = re.search(r'_ => "(#[0-9a-f]{6})"', table).group(1)
    for name, hexc in rig.ELEMENT_HEX.items():
        assert cs[name] == hexc, name
    # the shader is the review sheets' tint (fx.tint): mix to white over heat 0.72..1
    assert "smoothstep(0.72, 1.0, heat.r)" in rig.SHADER_CODE and "(heat - 0.72) / 0.28" in fx_py
    assert scene_text.count(f'material = SubResource("{rig.MATERIAL_ID}")') == 4
    assert "resource_local_to_scene = true" in scene_text
    assert f"shader_parameter/element = {rig.color(rig.hex_color(rig.ANEMO_HEX))}" in scene_text
    trail = (CS / "Vfx" / "ElementTrail.cs").read_text(encoding="utf-8")
    assert f'ElementParam = "{rig.ELEMENT_PARAM}"' in trail
    for node in (*rig.FX_NODE.values(), *rig.BURST_NODE.values()):
        assert f'= "{node}";' in trail, node


def test_the_merchant_loops_stance_b_on_its_own_atlas(frames):
    text = rig.MERCHANT_SCENE.read_text(encoding="utf-8")
    rec = frames["sheets"]["merchant"]
    assert 'autoplay = "relaxed_loop"' in text
    assert text.count('[sub_resource type="AtlasTexture"') == rec["count"]
    assert f"scale = {rig.vec2((frames['merchant_scale'], frames['merchant_scale']))}" in text
    assert 'path="res://varka/model/frames/varka_merchant.png"' in text


def test_the_pack_imports_his_sheets_vram_compressed_and_switches_rest_and_select(frames):
    assert frames["texture_import"] == "vram_compressed"
    ps = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")
    assert "compress/mode=2" in ps.split("function Write-TextureImport", 1)[1].split('"@)', 1)[0]
    block = ps.split("$varkaFrames = Join-Path $src 'varka\\model\\frames'", 1)[1].split("\n}\n", 1)[0]
    assert "Write-TextureImport" in block
    assert "'varka_rest.png'" in ps and "res://varka/model/$varkaRestArt" in ps
    assert "'select_closeup.png'" in ps and "res://varka/ui/$varkaSelectArt" in ps
    # his old rig's layers no longer ship, and the merchant scene is the generated one
    assert "varka\\model\\layers" not in ps
    assert "'varka\\model\\merchant_character.tscn'" not in ps


def test_every_out_path_of_his_model_art_has_one_producer(scene_text, frames):
    from tools import art_lint
    owned = art_lint.GENERATOR_OWNED
    files = set(re.findall(r'path="res://varka/model/frames/([^"]+)"', scene_text))
    files |= set(re.findall(r'path="res://varka/model/frames/([^"]+)"',
                            rig.MERCHANT_SCENE.read_text(encoding="utf-8")))
    for f in sorted(files):
        assert owned[f"ImageGen/images/varka/model/frames/{f}"] == "char_render/pack.py", f
    for out in ("model/varka_rest.png", "ui/select_closeup.png", "ui/select_portrait.png",
                "ui/select_portrait_locked.png"):
        assert owned[f"ImageGen/images/varka/{out}"] == "char_render/pack.py", out
    stills = (ROOT / "tools" / "gen_varka_stills.py").read_text(encoding="utf-8")
    assert '"select_portrait.png"' not in stills and '"select_portrait_locked.png"' not in stills
