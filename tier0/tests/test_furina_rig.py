"""Furina's generated model scenes (tools/furina_rig), phase B of her model art.

klee-mod/pck-src/furina/model/combat.tscn, merchant_character.tscn and the
eleven guest_<name>.tscn are GENERATED from tools/furina_rig/furina.yaml and
the committed manifest tools/char_render/furina_frames.json. [USER],
2026-10-13: "Furina looks good!"

These tests hold what needs neither the art nor the engine:

  * the shipped scenes are what the generator writes, byte-identically;
  * the manifest reading: every frame an AtlasTexture whose margin restores
    the clip's cell, on the page the manifest names;
  * the router contract plus `rejoice`, and the trigger that reaches it;
  * the rapier's element layer: drawn over the attack from the frame the
    manifest names, resting at Hydro;
  * the stage effects: Spend, Drain and Repay, each a sprite at her chest on
    its own tint and its own AnimationPlayer, hooked to the director's
    Spend, Drain and Repay beats;
  * the guests: each still at its manifest height, feet on the ground line,
    its Bounds its own width, and Freminet in a scene of his own;
  * the pack: VRAM-compressed imports, the rest/select switches, the old rig
    and cutouts out, and one producer for every out-path.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.furina_rig import guests, rig
from tools.klee_rig import verify

ROOT = Path(__file__).resolve().parents[2]
CS = ROOT / "klee-mod" / "KleeCode"
PROTO = CS / "Powers" / "Prototype"


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
    return times, re.findall(r'SubResource\("[^"]+"\)|Color\([^)]*\)|Vector2\([^)]*\)', values)


# ---------------------------------------------------------------------------
# the combat scene
# ---------------------------------------------------------------------------


def test_the_generator_is_deterministic_and_matches_every_shipped_scene(scene_text):
    assert rig.render_scene() == rig.render_scene() == scene_text, \
        "combat.tscn is stale: run `python -m tools.furina_rig gen`"
    assert rig.render_merchant_scene() == rig.MERCHANT_SCENE.read_text(encoding="utf-8")
    for name, text in guests.render_guests().items():
        assert text == guests.scene_path(name).read_text(encoding="utf-8"), \
            f"guest_{name}.tscn is stale: run `python -m tools.furina_rig gen`"


def test_the_router_contract_and_the_rejoice_state(scene_text):
    nodes = verify.parse_nodes(scene_text)
    for p in verify.CONTRACT_NODES:
        assert p in nodes, p
    anims = verify.track_paths(scene_text)
    assert {"RESET", *rig.ANIMATION_ORDER} <= set(anims)
    for name, length in rig.ONE_SHOT_LENGTHS.items():
        assert f'resource_name = "{name}"\nlength = {rig.fnum(length)}\n' in scene_text
    assert rig.STATE_MACHINE in scene_text
    assert "states/rejoice/node = SubResource(" in scene_text
    for name, paths in anims.items():
        for p in paths:
            assert p.split(":")[0] in nodes, f"{name}: track to a missing node {p}"
    # the old layer-cut rig is gone
    assert "Visuals/Facing/Rig" not in nodes and "res://furina/model/layers/" not in scene_text
    assert "metadata/idle_desync = true" in scene_text
    # her box is the old rig's, which the guest line was laid out against
    assert "offset_left = -120.0\noffset_top = -280.0\noffset_right = 120.0" in scene_text


def test_every_frame_is_an_atlas_texture_that_restores_its_cell(scene_text, frames):
    spec = rig.load_spec()
    clips = rig.clips_of(spec, frames)
    assert {f"stage_{n}" for n in rig.STAGE_EFFECTS} <= set(clips)
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
            assert f'path="res://furina/model/frames/{file}" id="{ext_id}"' in scene_text
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


def test_rejoice_is_triggered_by_let_the_people_rejoice_and_absorbs_its_lunge():
    router = (CS / "Vfx" / "CreatureAnimationRouter.cs").read_text(encoding="utf-8")
    assert '["Rejoice"] = new[] { "rejoice", "attack" },' in router
    assert "currentState is SetOffState or JumpyState or AscensionState or RejoiceState" in router
    motion = (CS / "Vfx" / "CardPlayMotion.cs").read_text(encoding="utf-8")
    assert "=> card is ProtoFsLetThePeopleRejoice;" in motion
    assert "IsRejoicePlay(card) ? RejoiceTrigger" in motion
    assert "trigger == RejoiceTrigger ? RejoiceDelay" in motion


def test_her_hits_land_on_the_clips_main_frames(frames):
    furina = (CS / "Furina.cs").read_text(encoding="utf-8")
    delay = float(re.search(r"AttackAnimDelay => ([0-9.]+)f;", furina).group(1))
    assert delay == pytest.approx(frames["sheets"]["attack"]["events"]["main"])
    motion = (CS / "Vfx" / "CardPlayMotion.cs").read_text(encoding="utf-8")
    rejoice = float(re.search(r"RejoiceDelay = ([0-9.]+)f;", motion).group(1))
    assert rejoice + delay == pytest.approx(frames["sheets"]["rejoice"]["events"]["main"])


def test_the_rapier_layer_draws_over_the_attack_from_the_manifests_frame_and_rests_at_hydro(scene_text, frames):
    fx = frames["fx"]["attack"]
    path = "Visuals/Facing/Model/AttackFx"
    times, values = _keys(scene_text, "attack", f"{path}:texture")
    first = fx["first_frame"]
    assert times == pytest.approx(frames["sheets"]["attack"]["times"][first:first + fx["count"]], abs=1e-4)
    assert len(values) == fx["count"]
    show_t, show_v = _keys(scene_text, "attack", f"{path}:self_modulate")
    assert show_t[1] == pytest.approx(times[0]) and show_v[1] == "Color(1, 1, 1, 1)"
    for state in rig.ANIMATION_ORDER:
        if state != "attack":
            assert _keys(scene_text, state, f"{path}:self_modulate")[1] == ["Color(1, 1, 1, 0)"], state
    body = verify.parse_nodes(scene_text)[path].props
    assert body["unique_name_in_owner"] == "true"
    assert body["material"] == f'SubResource("{rig.MATERIAL_ID}")'
    assert body["metadata/rest_element"] == '"hydro"'
    assert rig.HYDRO_HEX == frames["effects"]["drain"]["tint"]   # the same Hydro as her effects
    assert f"shader_parameter/element = {rig.color(rig.hex_color(rig.HYDRO_HEX))}" in scene_text
    trail = (CS / "Vfx" / "ElementTrail.cs").read_text(encoding="utf-8")
    assert 'RestElementMeta = "rest_element"' in trail and 'AttackFxNode = "AttackFx"' in trail
    reaction = (CS / "Vfx" / "ReactionFx.cs").read_text(encoding="utf-8")
    assert f'Element.Hydro => "{rig.HYDRO_HEX}"' in reaction


# ---------------------------------------------------------------------------
# the stage effects
# ---------------------------------------------------------------------------


def test_each_stage_effect_is_a_sprite_at_her_chest_on_its_own_tint_and_player(scene_text, frames):
    nodes = verify.parse_nodes(scene_text)
    group = f"{rig.FACING}/{rig.STAGE_GROUP}"
    assert nodes[group].props["position"] == rig.vec2(frames["stance_a"]["chest_px"])
    sc = frames["combat_scale"]
    for name in rig.STAGE_EFFECTS:
        eff = frames["effects"][name]
        sprite = nodes[f"{group}/{rig.STAGE_NODE[name]}"].props
        assert sprite["unique_name_in_owner"] == "true"
        assert sprite["self_modulate"] == "Color(1, 1, 1, 0)", f"{name} shows at rest"
        assert sprite["offset"] == rig.vec2((-eff["origin"][0], -eff["origin"][1]))
        assert sprite["scale"] == rig.vec2((sc, sc))
        assert sprite["material"] == f'SubResource("{rig.stage_material_id(name)}")'
        block = scene_text.split(f'[sub_resource type="ShaderMaterial" id="{rig.stage_material_id(name)}"]', 1)[1]
        assert block.split("\n\n", 1)[0].endswith(
            f"shader_parameter/element = {rig.color(rig.hex_color(eff['tint']))}")
        player = nodes[rig.STAGE_PLAYER[name]]
        assert player.type == "AnimationPlayer" and player.props["unique_name_in_owner"] == "true"
        assert f'&"": SubResource("AnimationLibrary_stage_{name}")' in scene_text
        # its one clip, named for it, at the manifest's length and fps, shown
        # from 0 and gone at its end
        assert f'resource_name = "{name}"\nlength = {rig.fnum(eff["length"])}\n' in scene_text
        times, values = _keys(scene_text, f"stage_{name}", f"{rig.stage_path(name)}:texture")
        assert times == pytest.approx([i / eff["fps"] for i in range(eff["count"])], abs=1e-4)
        assert values == [f'SubResource("Atlas_stage_{name}_{i}")' for i in range(eff["count"])]
        show_t, show_v = _keys(scene_text, f"stage_{name}", f"{rig.stage_path(name)}:self_modulate")
        assert show_t == pytest.approx([0.0, eff["length"]]) and show_v == ["Color(1, 1, 1, 1)", "Color(1, 1, 1, 0)"]
        # no state of hers touches it: it plays over whatever she is doing
        state_paths = verify.track_paths(scene_text)
        for state in ("RESET", *rig.ANIMATION_ORDER):
            assert not any(rig.STAGE_NODE[name] in p for p in state_paths[state]), (name, state)
        if name in rig.REACHING:
            reach = (eff["to"][0] - eff["origin"][0]) * sc
            assert float(sprite["metadata/reach"]) == pytest.approx(reach)
        else:
            assert "metadata/reach" not in sprite


def test_the_stage_effects_are_hooked_to_spend_drain_and_repay():
    director = (PROTO / "FurinaStageDirector.cs").read_text(encoding="utf-8")
    assert "void Effect(StageEffect effect);" in director

    def body(sig: str) -> str:
        start = director.index(sig)
        return director[start:director.index("\n    }\n", start)]

    for sig in ("public async Task<int> Spend(int price)", "public async Task<int> SpendAll()",
                "public async Task<int> SpendUpTo("):
        assert "_board.Effect(StageEffect.Spend);" in body(sig), sig
    assert "_board.Effect(StageEffect.Drain);" in body("public async Task<bool> Drain(int amount)")
    assert "_board.Effect(StageEffect.Repay);" in body("public async Task<int> Repay(int amount)")
    # the curtain call returns HP but is not a Repay: no droplets
    assert "_board.Effect" not in body("public async Task<CurtainCallParts> CurtainCallParts()")
    board = (PROTO / "FurinaStage.cs").read_text(encoding="utf-8")
    assert "public void Effect(StageEffect effect) =>\n        Vfx.FurinaStageFx.Play(_owner, effect);" in board
    fx = (CS / "Vfx" / "Prototype" / "FurinaStageFx.cs").read_text(encoding="utf-8")
    for name in rig.STAGE_EFFECTS:
        assert f'=> "{name}",' in fx or f'_ => "{name}",' in fx, name
        assert f'"{rig.STAGE_NODE[name]}"' in fx, name
        assert rig.STAGE_PLAYER[name] == rig.STAGE_NODE[name] + "Player"
    assert 'PlayerFor(StageEffect effect) => SpriteFor(effect) + "Player";' in fx
    assert 'ReachMeta = "reach";' in fx


# ---------------------------------------------------------------------------
# the merchant
# ---------------------------------------------------------------------------


def test_the_merchant_loops_stance_b_on_its_own_atlas(frames):
    text = rig.MERCHANT_SCENE.read_text(encoding="utf-8")
    rec = frames["sheets"]["merchant"]
    assert 'autoplay = "relaxed_loop"' in text
    assert text.count('[sub_resource type="AtlasTexture"') == rec["count"]
    assert f"scale = {rig.vec2((frames['merchant_scale'], frames['merchant_scale']))}" in text
    assert 'path="res://furina/model/frames/furina_merchant.png"' in text


# ---------------------------------------------------------------------------
# the guests
# ---------------------------------------------------------------------------


def _performers() -> list[str]:
    stage = (PROTO / "FurinaStage.cs").read_text(encoding="utf-8")
    body = stage[stage.index("public enum StagePerformer"):]
    body = re.sub(r"//[^\n]*", "", body[body.index("{") + 1:body.index("}")])
    return re.findall(r"\b([A-Z][A-Za-z]+)\b", body)


def test_every_performer_stands_as_their_rendered_still_freminet_included(frames):
    pets = (PROTO / "FurinaStagePets.cs").read_text(encoding="utf-8")
    fn = pets[pets.index("ModVisualsPathFor(StagePerformer who)"):]
    literals = dict(re.findall(r'StagePerformer\.(\w+)\s*=>\s*KleePck\.Path\("([^"]+)"\)', fn[:fn.index("};")]))
    assert set(literals) == set(_performers()) == {n.capitalize() for n in frames["guests"]}
    assert literals["Freminet"] == "furina/model/guest_freminet.tscn"
    for who, path in literals.items():
        assert path == f"furina/model/guest_{who.lower()}.tscn"
        text = (ROOT / "klee-mod" / "pck-src" / path).read_text(encoding="utf-8")
        assert f'path="res://furina/model/guests/guest_{who.lower()}.png"' in text


@pytest.mark.parametrize("name", ["charlotte", "chevreuse", "clorinde", "escoffier", "freminet", "lynette",
                                  "lyney", "navia", "neuvillette", "sigewinne", "wriothesley"])
def test_each_guest_stands_at_its_manifest_height_with_its_feet_on_the_ground(name, frames):
    rec = frames["guests"][name]
    sc = frames["combat_scale"]
    text = guests.scene_path(name).read_text(encoding="utf-8")
    nodes = verify.parse_nodes(text)
    w, h = rec["size"]
    fx, fy = rec["feet"]
    body = nodes["Visuals/Rig/Body"].props
    # the still at the combat scale, centred across its box, feet on y = 0
    assert body["centered"] == "false"
    assert body["scale"] == rig.vec2((sc, sc))
    assert body["offset"] == rig.vec2((-w / 2, -fy))
    assert nodes["Visuals/Rig"].props["position"] == "Vector2(0, 0)"
    # its height on screen is the renderer's measure (head to foot, hats
    # included, within a texel and the sole slack)
    assert abs(fy * sc - rec["full_px"]) <= 3.0
    bounds = {k[len("offset_"):]: float(v) for k, v in nodes["Bounds"].props.items() if k.startswith("offset_")}
    assert bounds["top"] == pytest.approx(-fy * sc, abs=0.05)
    assert bounds["bottom"] == 0.0
    assert bounds["right"] - bounds["left"] == pytest.approx(rec["width_px"], abs=0.11)
    assert bounds["left"] == -bounds["right"]


def test_guests_are_drawn_at_furinas_scale_by_their_canon_heights(frames):
    """A guest's head bone stands at (height over 63 in) times hers (the
    paper's scale rule), so the line reads true beside her."""
    furina_head = frames["measure"]["neck_px"]
    for name, rec in frames["guests"].items():
        want = rec["height_in"] / 63.0 * furina_head
        assert abs(rec["head_px"] - want) / want <= 0.04, name


def test_the_guest_motion_is_the_trios_scaled_to_each_guest(frames):
    """usher.tscn's keys, re-based on the feet and scaled by the guest's own
    height over the trio's 144 px."""
    usher = (ROOT / "klee-mod" / "pck-src" / "furina" / "model" / "usher.tscn").read_text(encoding="utf-8")
    rest = -guests.TRIO_H / 2

    def vecs(text: str, anim: str) -> list[tuple[float, float]]:
        _t, v = _keys(text, anim, "Visuals/Rig:position")
        return [tuple(float(c) for c in s[8:-1].split(", ")) for s in v]

    sc = frames["combat_scale"]
    for name, rec in frames["guests"].items():
        k = round(rec["feet"][1] * sc, 1) / guests.TRIO_H
        text = guests.scene_path(name).read_text(encoding="utf-8")
        for anim in ("idle", "attack", "hurt", "death"):
            want = [c for x, y in vecs(usher, anim) for c in (x * k, (y - rest) * k)]
            got = [c for v in vecs(text, anim) for c in v]
            assert got == pytest.approx(want, abs=0.06), (name, anim)


# ---------------------------------------------------------------------------
# the pack
# ---------------------------------------------------------------------------


def test_the_pack_imports_her_sheets_and_guests_vram_compressed_and_switches_rest_and_select(frames):
    assert frames["texture_import"] == "vram_compressed"
    ps = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")
    for anchor in ("$furinaFrames = Join-Path $src 'furina\\model\\frames'",
                   "$furinaGuests = Join-Path $src 'furina\\model\\guests'"):
        block = ps.split(anchor, 1)[1].split("\n}\n", 1)[0]
        assert "Write-TextureImport" in block, anchor
    assert "'furina_rest.png'" in ps and "res://furina/model/$furinaRestArt" in ps
    # the select scene is her rig's (tier0/tests/test_select_bg.py), not the pack's
    assert "furina\\ui\\char_select_bg_furina.tscn" not in ps
    # her old rig's layers and the flat guest cutouts no longer ship, and the
    # merchant scene is the generated one
    assert "furina\\model\\layers\\combat" not in ps
    assert "Where-Object { $_.Name -notlike 'guest_*.png' }" in ps
    assert "'furina\\model\\merchant_character.tscn'" not in ps


def test_every_out_path_of_her_model_art_has_one_producer(scene_text, frames):
    from tools import art_lint
    owned = art_lint.GENERATOR_OWNED
    files = set(re.findall(r'path="res://furina/model/frames/([^"]+)"', scene_text))
    files |= set(re.findall(r'path="res://furina/model/frames/([^"]+)"',
                            rig.MERCHANT_SCENE.read_text(encoding="utf-8")))
    assert len(files) == 13
    for f in sorted(files):
        assert owned[f"ImageGen/images/furina/model/frames/{f}"] == "char_render/pack.py", f
    for rec in frames["guests"].values():
        assert owned[f"ImageGen/images/furina/model/guests/{rec['file']}"] == "char_render/pack.py"
    for out in ("model/furina_rest.png", "ui/select_closeup.png", "ui/select_portrait.png",
                "ui/select_portrait_locked.png"):
        assert owned[f"ImageGen/images/furina/{out}"] == "char_render/pack.py", out
    stills = (ROOT / "tools" / "gen_furina_stills.py").read_text(encoding="utf-8")
    assert '"select_portrait.png"' not in stills and '"select_portrait_locked.png"' not in stills
    assert art_lint.generator_owned([]) == []
