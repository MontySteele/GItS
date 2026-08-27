"""Tests for the dispatch3 lane A native-animation bake-off.

The bake-off's whole value is that the four approaches are compared on the SAME
rig and the SAME motion suite, and that the numbers in the handoff were
measured rather than asserted. These tests defend exactly that:

  * the shared suite really is shared (every approach consumes every motion);
  * every animation track points at a node that exists, in all four scenes --
    a mistyped node path is silent at import and dead at runtime, which is the
    one defect class this generator could plausibly ship;
  * RESET covers every property any motion drives, because RESET is derived;
  * the fidelity ledger is complete -- expressed + relocated + dropped equals
    the suite, so an approach cannot look cheap by quietly losing tracks;
  * generation is deterministic, which is the precondition for the
    byte-identical-re-export measurement meaning anything;
  * the lane's PowerShell driver follows the repo's native-stderr convention,
    which `tier0/tests/test_repo_python_convention.py` enforces only for the
    four scripts hard-coded in its own list.

Nothing here launches the editor, touches the game, or needs `game_ref/`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.animation_bakeoff import approaches, art, geometry, pck, spec, tscn
from tools.animation_bakeoff.build import write_project

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "tools" / "animation_bakeoff" / "export_bakeoff.ps1"
ROUTER_CS = ROOT / "klee-mod" / "KleeCode" / "Vfx" / "CreatureAnimationRouter.cs"

NODE_RE = re.compile(r'^\[node name="([^"]+)" type="([^"]+)"(?: parent="([^"]+)")?\]')
TRACK_RE = re.compile(r'^tracks/\d+/path = NodePath\("([^"]+)"\)')


def scene_for(key: str) -> str:
    return approaches.build(key, "res://sprig/art").scene_text


def node_paths(scene_text: str) -> set[str]:
    """Every addressable node path in a scene, relative to the scene root."""
    paths: set[str] = set()
    for line in scene_text.splitlines():
        match = NODE_RE.match(line)
        if not match:
            continue
        name, _type, parent = match.groups()
        if parent is None:  # the root
            continue
        paths.add(name if parent == "." else f"{parent}/{name}")
    return paths


def track_targets(scene_text: str) -> list[str]:
    return [TRACK_RE.match(line).group(1) for line in scene_text.splitlines() if TRACK_RE.match(line)]


# --------------------------------------------------------------------------
# the shared suite
# --------------------------------------------------------------------------


def test_the_required_motion_suite_is_present_and_named_as_the_charter_names_it():
    names = [m.name for m in spec.MOTIONS]
    assert names == list(spec.REQUIRED_MOTIONS)


def test_reset_is_derived_from_every_channel_any_motion_touches():
    reset = spec.reset_motion()
    covered = {(t.part, t.channel) for t in reset.tracks}
    used = {(t.part, t.channel) for m in spec.MOTIONS for t in m.tracks}
    assert covered == used
    assert reset.name == "RESET"
    # A derived RESET must be stable, or every regeneration changes the file.
    assert [(t.part, t.channel) for t in spec.reset_motion().tracks] == [
        (t.part, t.channel) for t in reset.tracks
    ]


def test_intent_has_no_routed_game_trigger_today():
    """Documents the gap this lane's charter creates, so it cannot be lost.

    `intent` is required as a MOTION by the charter. The shipped router maps
    seven game triggers onto four states and `intent` is not one of them, so a
    scene that ships this suite would carry a state nothing can reach until
    [USER] rules on how a tell is driven. That is a question, not a defect --
    but a silent one would be a defect.
    """
    assert "intent" in spec.REQUIRED_MOTIONS
    assert "intent" not in spec.ROUTED_STATES


def test_routed_states_still_match_the_shipped_router():
    """`spec.ROUTED_STATES` is a copy of a C# table; copies go stale."""
    if not ROUTER_CS.exists():  # pragma: no cover - present in this repo
        pytest.skip("CreatureAnimationRouter.cs not in this checkout")
    text = ROUTER_CS.read_text(encoding="utf-8")
    block = text[text.index("TriggerToState"):]
    block = block[: block.index("};")]
    mapped = re.findall(r'\]\s*=\s*"([a-z]+)"', block)
    assert set(mapped) == set(spec.ROUTED_STATES), (
        "CreatureAnimationRouter's trigger table moved; update spec.ROUTED_STATES"
    )


def test_every_approach_emits_reset_plus_the_whole_suite():
    expected = {"RESET", *spec.REQUIRED_MOTIONS}
    for key in approaches.APPROACH_KEYS:
        text = scene_for(key)
        emitted = set(re.findall(r'^resource_name = "([^"]+)"', text, flags=re.M)) | {"RESET"}
        assert emitted == expected, key
        assert f'states/idle/node = SubResource("Anim_idle")' in text, key


# --------------------------------------------------------------------------
# the scenes
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key", approaches.APPROACH_KEYS)
def test_every_animation_track_points_at_a_node_that_exists(key: str):
    """The defect this generator could actually ship.

    Godot resolves an animation track path lazily; a track aimed at a node
    that is not there imports clean, exports clean, and simply never animates.
    Nothing downstream would notice.
    """
    text = scene_for(key)
    nodes = node_paths(text)
    missing = sorted({t.split(":", 1)[0] for t in track_targets(text)} - nodes)
    assert not missing, f"{key}: tracks aim at absent nodes: {missing}"


@pytest.mark.parametrize("key", approaches.APPROACH_KEYS)
def test_reset_drives_every_property_any_motion_drives(key: str):
    """Otherwise a state exit leaves a limb where the last animation left it."""
    text = scene_for(key)
    blocks = text.split('[sub_resource type="Animation" id="')
    driven: set[str] = set()
    reset: set[str] = set()
    for block in blocks[1:]:
        target = reset if block.startswith("Animation_RESET") else driven
        target.update(track_targets(block))
    assert driven - reset == set(), f"{key}: not reset: {sorted(driven - reset)}"


@pytest.mark.parametrize("key", approaches.APPROACH_KEYS)
def test_the_scene_contract_the_router_looks_up_is_present(key: str):
    """`CreatureAnimationRouter` finds its target by node lookup, not by type."""
    text = scene_for(key)
    for required in (
        '[node name="Visuals" type="Node2D" parent="."]',
        '[node name="AnimationTree" type="AnimationTree" parent="."]',
        '[node name="AnimationPlayer" type="AnimationPlayer" parent="."]',
        '[node name="Bounds" type="Control" parent="."]',
        '[node name="CenterPos" type="Marker2D" parent="."]',
        '[node name="IntentPos" type="Marker2D" parent="."]',
    ):
        assert required in text, f"{key} is missing {required}"
    assert text.count("unique_name_in_owner = true") >= 6, key


@pytest.mark.parametrize("key", approaches.APPROACH_KEYS)
def test_no_scene_carries_a_script(key: str):
    """The pipeline's standing rule: script resources cannot ship in a mod pck.

    `klee-mod/pck-src/README.md:14-18`. The bake-off's probe is a PROJECT
    script, never a scene script, and this asserts the distinction holds.
    """
    assert 'type="Script"' not in scene_for(key)


@pytest.mark.parametrize("key", approaches.APPROACH_KEYS)
def test_every_referenced_texture_is_a_layer_the_art_module_can_produce(key: str):
    result = approaches.build(key, "res://sprig/art")
    for path in result.textures:
        name = Path(path).stem.removeprefix("sprig_")
        assert name in art.ALL_LAYERS, f"{key} references unbuildable layer {name}"


# --------------------------------------------------------------------------
# the fidelity ledger
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key", approaches.APPROACH_KEYS)
def test_the_fidelity_ledger_accounts_for_every_track_in_the_suite(key: str):
    """An approach cannot look cheap by losing tracks without saying so."""
    total = sum(len(m.tracks) for m in spec.MOTIONS)
    fidelity = approaches.build(key, "res://sprig/art").fidelity
    accounted = len(fidelity.expressed) + len(fidelity.relocated) + len(fidelity.dropped)
    assert accounted == total, (
        f"{key}: ledger accounts for {accounted} of {total} suite tracks"
    )


def test_the_layered_approach_is_the_lossless_reference():
    """It is the shape the mod already ships, and it drops nothing.

    If this ever fails, the shared suite has grown a channel that even the
    straightforward rendering cannot express, and the suite is the thing to
    look at -- not the approach.
    """
    fidelity = approaches.build("layered", "res://sprig/art").fidelity
    assert fidelity.dropped == []
    assert fidelity.relocated == []


def test_the_billboard_approach_reports_the_tracks_it_cannot_carry():
    fidelity = approaches.build("particles", "res://sprig/art").fidelity
    assert fidelity.dropped, "a one-node billboard cannot express a per-limb suite"
    reasons = {why for _track, why in fidelity.dropped}
    assert any("no node for this part" in r for r in reasons)


# --------------------------------------------------------------------------
# skeleton math
# --------------------------------------------------------------------------


def test_bone_globals_land_on_the_parts_they_drive():
    """The cutout rig is only equivalent to the layered rig if this holds."""
    for part in spec.PARTS:
        bx, by = geometry.bone_global(part.bone)
        ox, oy = geometry.sprite_offset(part)
        assert (bx + ox, by + oy) == part.rest


def test_every_bone_path_is_rooted_at_the_skeleton_root():
    for bone in spec.BONES:
        assert geometry.bone_path(bone.name).split("/")[0] == "Root"


def test_the_mesh_scene_uses_the_bone_spelling_this_engine_accepts():
    """The one silent defect this lane actually hit, kept as a regression.

    On MegaDot 4.5.1 `Polygon2D` exposes a single internal `bones` property; a
    `bones/0/path` line -- the older spelling, and the one an out-of-date
    reference will hand you -- is DISCARDED BY THE SCENE PARSER WITH NO ERROR.
    Import exits 0, export exits 0, the scene loads and instantiates, and
    `get_bone_count()` is 0, so nothing deforms. Measured against the editor
    (`Polygon2D.get_property_list()` and a `PackedScene.pack` round-trip), then
    fixed; without this test the fix silently rots the next time the emitter is
    touched.
    """
    text = scene_for("mesh")
    assert "bones/0/path" not in text
    assert "bones/0/weights" not in text
    assert re.search(r'^bones = \["Root/Hip", PackedFloat32Array\(', text, flags=re.M)
    # Every skinned polygon names bones that exist in the emitted skeleton.
    bone_nodes = {p.rsplit("/", 1)[-1] for p in node_paths(text) if "/Skeleton/" in p}
    for row in re.findall(r'^bones = \[(.+)\]$', text, flags=re.M):
        for path in re.findall(r'"([^"]+)"', row):
            assert path.split("/")[-1] in bone_nodes, path


def test_torso_weights_sum_to_one_at_every_vertex():
    """A skinned vertex whose weights do not sum to 1 collapses toward origin."""
    torso = spec.PART_BY_NAME["torso"]
    polygon = geometry.polygon_for(torso)
    rows = geometry.weights_for(torso, polygon)
    assert len(rows) == 3
    for i in range(len(polygon)):
        total = sum(weights[i] for _bone, weights in rows)
        assert total == pytest.approx(1.0, abs=1e-3)


@pytest.mark.parametrize("part", spec.PARTS, ids=lambda p: p.name)
def test_polygon_and_uv_arrays_have_equal_length(part):
    polygon = geometry.polygon_for(part)
    assert len(geometry.uv_for(part, polygon)) == len(polygon)
    for _bone, weights in geometry.weights_for(part, polygon):
        assert len(weights) == len(polygon)


# --------------------------------------------------------------------------
# determinism
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key", approaches.APPROACH_KEYS)
def test_scene_generation_is_byte_identical_across_runs(key: str):
    assert scene_for(key).encode("utf-8") == scene_for(key).encode("utf-8")


def test_two_generated_projects_are_byte_identical(tmp_path: Path):
    """The precondition for the byte-identical-re-export measurement.

    If the generator itself drifted between runs, a differing pack hash would
    tell us nothing about the editor.
    """
    a = tmp_path / "a"
    b = tmp_path / "b"
    write_project(a, "layered")
    write_project(b, "layered")
    files_a = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
    files_b = sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
    assert files_a == files_b
    for rel in files_a:
        assert (a / rel).read_bytes() == (b / rel).read_bytes(), rel


def test_generated_art_is_drawn_only_from_primitives():
    """No fetched, game, or licensed pixels can reach the bake-off."""
    assert {p.shape for p in spec.PARTS} <= {"ellipse", "capsule", "roundrect", "diamond"}
    source = (ROOT / "tools" / "animation_bakeoff" / "art.py").read_text(encoding="utf-8")
    assert "Image.open" not in source
    assert "http" not in source


# --------------------------------------------------------------------------
# the pack reader
# --------------------------------------------------------------------------


def _fake_pack(entries: list[tuple[str, int]]) -> bytes:
    import struct

    directory = struct.pack("<I", len(entries))
    for path, size in entries:
        raw = path.encode("utf-8")
        directory += struct.pack("<I", len(raw)) + raw
        directory += struct.pack("<QQ", 0, size) + b"\0" * 16 + struct.pack("<I", 0)
    header = bytearray(b"GDPC" + struct.pack("<IIIII", 3, 4, 5, 1, 2))
    header += struct.pack("<Q", 112)
    header += struct.pack("<Q", 112)  # directory offset
    header += b"\0" * (112 - len(header))
    return bytes(header) + directory


def test_the_pack_reader_reads_a_directory(tmp_path: Path):
    path = tmp_path / "x.pck"
    path.write_bytes(_fake_pack([("a/b.ctex", 10), ("c.tscn.remap", 20)]))
    pack = pck.read(path)
    assert pack.engine_version == (4, 5, 1)
    assert pack.resource_paths == ("a/b.ctex", "c.tscn.remap")
    assert pack.payload_bytes == 30


def test_the_pack_reader_refuses_a_non_pack(tmp_path: Path):
    """An empty resource list is exactly the reading that hides a bad export."""
    path = tmp_path / "x.pck"
    path.write_bytes(b"NOPE" + b"\0" * 200)
    with pytest.raises(ValueError):
        pck.read(path)


def test_the_pack_reader_refuses_an_unknown_format(tmp_path: Path):
    import struct

    path = tmp_path / "x.pck"
    path.write_bytes(b"GDPC" + struct.pack("<IIIII", 99, 4, 5, 1, 0) + b"\0" * 200)
    with pytest.raises(ValueError):
        pck.read(path)


# --------------------------------------------------------------------------
# the lane's PowerShell driver
# --------------------------------------------------------------------------


def test_the_driver_is_pure_ascii():
    """PS 5.1 reads a BOM-less .ps1 as ANSI; validate.ps1 S8 scans every one."""
    raw = DRIVER.read_bytes()
    bad = [(i, b) for i, b in enumerate(raw) if b > 0x7F]
    assert not bad, f"non-ASCII byte(s) at {bad[:5]}"


def test_the_driver_routes_every_native_call_through_the_eap_helper():
    """Same convention `test_repo_python_convention.py` pins for the four
    scripts hard-coded in its own list; this file is not in that list, so the
    convention is asserted here instead of assumed."""
    lines = DRIVER.read_text(encoding="utf-8").splitlines()
    helper = [i for i, line in enumerate(lines, 1) if line.startswith("function Invoke-NativeCaptured")]
    assert helper, "the driver shells out and must define the EAP-lowering helper"
    start = helper[0]
    depth = 0
    started = False
    inside = set()
    for i in range(start, len(lines) + 1):
        depth += lines[i - 1].count("{") - lines[i - 1].count("}")
        started = started or "{" in lines[i - 1]
        inside.add(i)
        if started and depth <= 0:
            break
    offenders = [
        (i, line.strip())
        for i, line in enumerate(lines, 1)
        if i not in inside and not line.lstrip().startswith("#")
        and (re.search(r"&\s*\$\w+", line) or "2>&1" in line)
    ]
    assert not offenders, offenders
    body = "\n".join(lines[start - 1 : max(inside)])
    assert "$ErrorActionPreference = 'Continue'" in body
    assert "finally" in body and "$ErrorActionPreference = $prev" in body


def _driver_code_lines() -> list[str]:
    """The driver with its block comment and `#` lines removed.

    Prose is exempt for the same reason it is in
    `test_repo_python_convention.py`: the header legitimately NAMES the paths
    this script must never write to, and forbidding the words in a comment
    would forbid saying so.
    """
    lines = DRIVER.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    in_block = False
    for line in lines:
        if line.strip().startswith("<#"):
            in_block = True
        if in_block:
            if "#>" in line:
                in_block = False
            continue
        if line.lstrip().startswith("#"):
            continue
        out.append(line)
    return out


def test_the_driver_never_writes_into_the_game_or_the_mod_assets():
    """Lane A must not deploy, and must not race the shared pck producer."""
    code = "\n".join(_driver_code_lines())
    for forbidden in ("steamapps", "mods\\klee", "klee-mod\\assets", "build_pck.ps1"):
        assert forbidden not in code, forbidden


def test_tscn_number_formatting_is_stable():
    assert tscn.num(3.0) == "3"
    assert tscn.fnum(3.0) == "3.0"
    assert tscn.vec2((0.0, -140.0)) == "Vector2(0, -140)"
    assert tscn.color((1.0, 0.45, 0.4, 1.0)) == "Color(1, 0.45, 0.4, 1)"
    assert tscn.literal("flag", True) == "true"
    assert tscn.literal("flag", False) == "false"
