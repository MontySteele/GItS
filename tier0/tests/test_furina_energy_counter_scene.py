"""EB-40: Furina's energy counter, the half that can be checked without a game.

The acceptance criterion on the backlog row is "all five `GetNode`s resolve",
and resolving is something only a running `NEnergyCounter._Ready` can do. What
IS checkable on a clean checkout is everything that determines the answer:

  * the scene declares the five nodes `_Ready` asks for, spelled exactly, with
    the unique-name marker on the four `%`-prefixed ones;
  * the two stacks carry the five R231 layers in their inferred roles, at the
    out-paths `art_lint.GENERATOR_OWNED` declares -- so a renamed layer breaks
    a test here rather than exporting a textureless orb;
  * Furina points at the scene and keeps the base counter as her fallback,
    while Klee and Kokomi are untouched;
  * the builder actually ships the layer directory.

WHY THE ROOT CARRIES NO SCRIPT. The row quotes the assembly correctly --
`NEnergyCounter.cs:168` hard-casts `Instantiate<NEnergyCounter>`, so the thing
the game gets back must BE an NEnergyCounter -- but a `script` ext_resource is
not how this pack answers that, and could not be: the pck is exported from a
scratch project containing no game code, so the reference would fail MegaDot's
import (and `visual_qa`'s SD-SCRIPT rule fails it here first). BaseLib converts
the registered path instead, logging `Registered scene '...' for auto-conversion
to NEnergyCounter` -- the line s17 read out of a live session for the ironclad
path this scene replaces.

WHAT IS STILL OWED, and cannot be closed from here: the live instantiate. Node
TYPES are an inference (the base scene is inside a PACK_DIR_ENCRYPTED pack and
cannot be read), so if `_Ready` resolves `%EnergyVfxBack` as something narrower
than a `Control` it will throw at the cast, and only a dev build will say so.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.art_lint import GENERATOR_OWNED                  # noqa: E402
from tools.visual_qa import godot_scene                     # noqa: E402

SCENE_PATH = ROOT / "klee-mod" / "pck-src" / "furina" / "ui" / "energy_counter.tscn"
FURINA = (ROOT / "klee-mod" / "KleeCode" / "Furina.cs").read_text(encoding="utf-8")
BUILDER = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")
TELEMETRY = (ROOT / "klee-mod" / "KleeCode" / "Diagnostics"
             / "KleeSceneTelemetry.cs").read_text(encoding="utf-8")

BASE_COUNTER = "res://scenes/combat/energy_counters/ironclad_energy_counter.tscn"

#: `_Ready`'s five, read out of the assembly on 2026-08-13 and quoted on the
#: EB-40 row. The bool is "resolved by unique name" -- i.e. the lookup is
#: `%Name`, which needs `unique_name_in_owner = true` in the scene text.
READY_NODES = (
    ("Label", False),
    ("Layers", True),
    ("RotationLayers", True),
    ("EnergyVfxBack", True),
    ("EnergyVfxFront", True),
)

#: The inferred roles, from tools/gen_energy_orb_layers.py's LAYERS table:
#: which stack each layer lives in, and in what order. %RotationLayers order is
#: load-bearing -- _Process spins child i at delta * num * (i + 1) degrees, so
#: the caustics must precede the ring for the ring to be the faster one.
STACKS = {
    "Layers": ("layer1_backglow", "layer2_body", "layer5_gloss"),
    "RotationLayers": ("layer3_caustics", "layer4_ring"),
}


def scene():
    return godot_scene.parse(SCENE_PATH)


def _nodes_by_path(parsed):
    return {n.path: n for n in parsed.nodes}


def test_the_scene_exists_and_has_a_single_root():
    assert SCENE_PATH.is_file(), f"no energy counter scene at {SCENE_PATH}"
    parsed = scene()
    roots = [n for n in parsed.nodes if n.parent is None]
    assert len(roots) == 1, f"expected one root, got {[n.name for n in roots]}"
    assert roots[0].type == "Control", (
        "the pre-conversion root type is what KleeSceneTelemetry prints and "
        "what BaseLib converts; the HUD tree it joins is Controls "
        "(NCombatUi._Ready iterates GetChildren().OfType<Control>())")


def test_the_root_carries_no_script_resource():
    """The hard cast is satisfied by conversion, not by an ext_resource.

    Asserted rather than assumed, because 'the root must carry that script'
    (the row's words) reads like an instruction to ship one, and shipping one
    would fail the export on a project that has no game code in it.
    """
    parsed = scene()
    assert 'type="Script"' not in SCENE_PATH.read_text(encoding="utf-8")
    for node in parsed.nodes:
        assert "script" not in node.props, f"{node.path} carries a script"


def test_every_node_ready_resolves_is_present_and_spelled_exactly():
    """(b) of the acceptance: the five GetNodes have something to find."""
    by_path = _nodes_by_path(scene())
    for name, unique in READY_NODES:
        assert name in by_path, (
            f"NEnergyCounter._Ready GetNodes '{name}' and the scene has no "
            f"such direct child of the root; it has {sorted(by_path)}")
        node = by_path[name]
        assert node.parent == ".", f"{name} must be a direct child of the root"
        if unique:
            assert node.props.get("unique_name_in_owner") == "true", (
                f"{name} is resolved as %{name} and so needs "
                "unique_name_in_owner = true in the scene text")


def test_the_two_stacks_carry_the_five_layers_in_their_inferred_roles():
    parsed = scene()
    ext = {rid: sec.attrs.get("path", "") for rid, sec in parsed.ext_resources.items()}
    for stack, expected in STACKS.items():
        children = [n for n in parsed.nodes if n.parent == stack]
        got = []
        for child in children:
            ref = re.search(r'ExtResource\("([^"]+)"\)', child.props.get("texture", ""))
            assert ref, f"{child.path} has no texture ExtResource"
            got.append(Path(ext[ref.group(1)]).stem)
        assert tuple(got) == expected, (
            f"%{stack} children are {got}; the roles inferred from the "
            f"NEnergyCounter contract are {list(expected)}")


def test_the_layer_paths_are_the_ones_the_generator_declares():
    """(c): the scene's res:// paths and art_lint's out-paths are one set.

    GENERATOR_OWNED is where R231's five layers are registered so no plan row
    can claim them; if a layer is renamed there and not here, the pack exports
    with a missing texture and the orb goes blank.
    """
    declared = {
        "res://furina/ui/" + key.split("images/furina/ui/", 1)[1]
        for key in GENERATOR_OWNED
        if "images/furina/ui/energy_orb/" in key
    }
    assert len(declared) == 5, f"expected five declared orb layers, got {declared}"

    parsed = scene()
    used = {sec.attrs.get("path") for sec in parsed.ext_resources.values()}
    assert used == declared, (
        f"scene textures {sorted(used)} != declared out-paths {sorted(declared)}")


def test_furina_points_at_the_scene_and_keeps_the_base_counter_as_fallback():
    body = FURINA.split("CustomEnergyCounterPath", 1)[1].split(";", 1)[0]
    assert 'KleePck.Path("furina/ui/energy_counter.tscn")' in body
    assert BASE_COUNTER in body, (
        "a null KleePck.Path with no fallback drops to the id-derived path "
        "that does not exist -- the R9 preload crash")


def test_klee_and_kokomi_still_return_the_base_counter():
    """The change is Furina-only; nobody else's orb moves under them."""
    for name in ("Klee", "Kokomi"):
        source = (ROOT / "klee-mod" / "KleeCode" / f"{name}.cs").read_text(
            encoding="utf-8")
        body = source.split("CustomEnergyCounterPath", 1)[1].split(";", 1)[0]
        assert body.strip().strip("=> \n\"") == BASE_COUNTER, (
            f"{name}'s energy counter moved; EB-40 is Furina's row alone")


def test_the_builder_ships_the_layer_directory():
    """The ui\\ copy loop is non-recursive, so the subdirectory needs its own
    block -- without it the scene exports with five missing textures."""
    assert "furina\\ui\\energy_orb" in BUILDER, (
        "build_pck.ps1 has no copy block for the orb layer directory; the "
        "per-surface Get-ChildItem does not recurse into it")


def test_boot_telemetry_names_the_scene_and_all_five_nodes():
    assert '"furina/ui/energy_counter.tscn"' in TELEMETRY
    for name, _ in READY_NODES:
        assert f'("furina/ui/energy_counter.tscn", "{name}")' in TELEMETRY, (
            f"{name} is not in KleeSceneTelemetry's RequiredNodes; these five "
            "throw rather than no-op, so a miss must be loud at boot")
