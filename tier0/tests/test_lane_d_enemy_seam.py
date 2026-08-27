"""Lane D's neutral enemy presentation seam, pinned as source text.

WHY SOURCE TEXT. The spike is a Harmony/BaseLib mod assembly: it only executes
inside Godot, there is no C# test project, and the Python suite cannot import a
Godot assembly (`docs/current/atlas/klee-mod-runtime.md` sec.2). The BEHAVIOUR
gate is the offline harness at `klee-mod/spikes/lane-d-enemy-seam/bitecheck/`,
which needs the Steam install and so cannot run in CI -- the same split
`test_harmony_bootstrap_contract.py` uses for the mod's own bootstrap. This
file is the half that runs everywhere.

WHAT IT IS DEFENDING. Three properties, each of which fails silently:

1. **No global overwrite.** Godot's `ProjectSettings.LoadResourcePack` replaces
   colliding `res://` paths. A pack that carried
   `res://scenes/creature_visuals/<id>.tscn` would replace the base scene for
   every player, not just for this mod -- and it would look identical in game
   to doing it correctly. The check is that the replacement string never points
   into the base namespace.
2. **Exactly one subject.** A prefix that forgets its id guard re-skins the
   entire bestiary and still boots.
3. **No mechanics.** The seam must not be able to reach HP, moves, intents or
   damage. Presentation-only is the whole permission it has.

The proof scene is checked too, because its failure mode is a hard throw:
`NCreatureVisuals._Ready()` calls `GetNode<T>` -- not `GetNodeOrNull` -- for
four named children, and a scene missing one of them takes down combat setup.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPIKE = ROOT / "klee-mod" / "spikes" / "lane-d-enemy-seam"
SEAM_PATH = SPIKE / "EnemySeamSpike" / "NeutralEnemySeam.cs"
BOOTSTRAP_PATH = SPIKE / "EnemySeamSpike" / "SeamBootstrap.cs"
SCENE_PATH = SPIKE / "pck-src" / "laned" / "creature_visuals" / "proof_prism.tscn"

SEAM = SEAM_PATH.read_text(encoding="utf-8")
BOOTSTRAP = BOOTSTRAP_PATH.read_text(encoding="utf-8")
SCENE = SCENE_PATH.read_text(encoding="utf-8")


def _code_only(source: str) -> str:
    """Strip comments so prose about a trap never satisfies a check for it.

    This file's subject argues at length in `///` blocks and names, in that
    prose, every single thing it must not do -- `res://scenes/`,
    `GenerateMoveStateMachine`, `PatchAll`. A bare substring test would pass on
    the strength of the warning against the thing.
    """
    return "\n".join(
        line for line in source.splitlines()
        if not line.lstrip().startswith(("///", "//")))


CODE = _code_only(SEAM)
BOOT_CODE = _code_only(BOOTSTRAP)


# --- property 1: no global overwrite -------------------------------------

def test_the_replacement_path_is_namespaced_and_not_a_base_scene():
    match = re.search(r'ProofScenePath\s*=\s*"([^"]+)"', CODE)
    assert match, "ProofScenePath must be a single string constant"
    path = match.group(1)

    assert path.startswith("res://"), path
    assert not path.startswith("res://scenes/"), (
        f"{path} is inside the BASE game's scene namespace. Shipping that path "
        "inside a mod pck overwrites the base resource for every creature of "
        "that id, globally -- Godot's pack loader replaces colliding paths. "
        "The replacement must be a DIFFERENT string in the mod's own tree.")


def test_the_packed_proof_scene_lives_where_the_constant_points():
    """The constant and the file on disk have to agree, or nothing loads.

    Spelled as a derivation rather than as two literals: a rename that moves
    the scene and forgets the constant (or the reverse) is precisely the defect
    a second literal would hide.
    """
    match = re.search(r'ProofScenePath\s*=\s*"res://([^"]+)"', CODE)
    assert match
    relative = match.group(1)
    assert (SPIKE / "pck-src" / Path(relative)).is_file(), (
        f"ProofScenePath points at res://{relative}, but no such file exists "
        f"under {SPIKE / 'pck-src'}")


def test_the_base_namespace_guard_is_a_function_not_a_comment():
    """The rule is executable, so the harness can assert it at runtime too."""
    assert "RejectsBaseNamespace" in CODE
    assert 'StartsWith("res://scenes/"' in CODE.replace(" ", "") or \
           'StartsWith("res://scenes/"' in CODE, CODE


def test_the_spike_ships_no_base_game_path_anywhere_in_its_pack_source():
    """Every file the pack would carry must sit under the mod's own prefix.

    A single stray file at a base path is enough to make the pack a global
    overwrite, and the mistake is invisible until someone else's game changes.
    """
    pck_src = SPIKE / "pck-src"
    tops = {p.name for p in pck_src.iterdir() if p.is_dir()}
    assert tops == {"laned"}, (
        f"pck-src top level is {sorted(tops)}; anything other than the mod's "
        "own namespace collides with base res:// paths when the pack merges")


# --- property 2: exactly one subject, and it falls through otherwise ------

def test_the_subject_is_one_named_entry_in_one_place():
    entries = re.findall(r'TargetEntry\s*=\s*"([^"]+)"', CODE)
    assert entries == ["NIBBIT"], entries
    # The literal must not be repeated: a second copy is how a guard and a
    # lookup drift apart.
    assert CODE.count('"NIBBIT"') == 1, (
        "the subject id appears more than once; every other site must read "
        "TargetEntry so that changing the subject is a one-line edit")


def test_the_claim_check_is_an_exact_entry_match_and_excludes_mod_monsters():
    claims = re.search(r"public static bool Claims\(MonsterModel\?? model\)\s*=>(.*?);",
                       CODE, re.S)
    assert claims, "Claims must exist as a single expression-bodied predicate"
    body = claims.group(1)

    assert "model.Id.Entry" in body and "TargetEntry" in body, body
    assert "StringComparison.Ordinal" in body, (
        "an entry match must be ordinal; a culture-sensitive compare on an id "
        "is a defect waiting for a Turkish locale")
    assert "is not CustomMonsterModel" in body, (
        "a BaseLib CustomMonsterModel belongs to whichever mod declared it and "
        "has its own supported override; this seam must never claim one")


def test_every_prefix_falls_through_when_it_does_not_claim():
    """`return true` is the difference between a spike and a bestiary reskin.

    Both prefixes must open with the same shape: not claimed -> run the
    original. Checked per-prefix rather than by counting `return true`, because
    the fallthrough that matters is the FIRST statement.
    """
    prefixes = re.findall(
        r"private static bool Prefix\([^)]*\)\s*\{(.*?)\n        \}", CODE, re.S)
    assert len(prefixes) == 2, f"expected two prefixes, found {len(prefixes)}"
    for body in prefixes:
        assert re.match(r"\s*if \(!Claims\(__instance\)\)\s*\{\s*return true;",
                        body), body


def test_a_missing_pack_leaves_the_enemy_alone():
    """No pack must mean base art, never a dead path handed to the engine.

    Same contract as `KleePck.Path` (returns null on a miss so callers degrade
    to base behaviour). The failure this forbids -- returning the path
    unconditionally -- produces the engine's red error scene on every fight
    with that enemy, on any build where the pack is stale.
    """
    assert re.search(r"if \(path == null\)\s*\{\s*return true;", CODE), CODE
    assert CODE.count("ResolveProofScene()") >= 2, (
        "both prefixes must ask whether the scene resolves; a prefix that "
        "skips the probe is the one that ships the dead path")


# --- property 3: presentation only ---------------------------------------

MECHANICS_TOKENS = (
    "GenerateMoveStateMachine",
    "MinInitialHp",
    "MaxInitialHp",
    "DamageCmd",
    "CreatureCmd",
    "AbstractIntent",
    "MonsterMoveStateMachine",
    "CombatState",
    "ToMutable",
    "SpawnPet",
)


def test_the_seam_cannot_reach_mechanics():
    hits = [t for t in MECHANICS_TOKENS if t in CODE + BOOT_CODE]
    assert hits == [], (
        f"the spike references {hits}. Presentation is the entire permission "
        "this lane has; mechanics, mappings and pools are [USER]'s")


def test_the_only_patched_members_are_the_two_presentation_sockets():
    targets = re.findall(r"\[HarmonyPatch\(typeof\((\w+)\), \"(\w+)\"", CODE)
    assert sorted(targets) == [
        ("MonsterModel", "CreateVisuals"),
        ("MonsterModel", "VisualsPath"),
    ], targets


def test_both_prefixes_yield_to_baselib_by_priority():
    """Composition, not luck.

    BaseLib patches the same two members at default priority and returns true
    for anything that is not a CustomMonsterModel. Harmony skips the remaining
    prefixes once one returns false, so running LAST is what guarantees a mod's
    own monster is resolved by its owner and never by this spike.
    """
    assert CODE.count("[HarmonyPriority(Priority.Low)]") == 2, CODE


# --- the bootstrap --------------------------------------------------------

def test_the_bootstrap_patches_per_type_and_never_calls_patchall():
    assert "CreateClassProcessor" in BOOT_CODE
    assert "PatchAll" not in BOOT_CODE, (
        "PatchAll walks the assembly inside one try/catch: the first class "
        "that throws aborts the walk and every class after it is silently "
        "never applied")


def test_a_class_that_armed_nothing_is_reported_as_a_failure():
    """Harmony returns an empty list, not an exception, for a dead lookup.

    For a presentation seam that is the worst outcome available: the game looks
    entirely normal and the spike is simply absent.
    """
    assert re.search(r"patched == null \|\| patched\.Count == 0", BOOT_CODE)
    assert "armed NO methods" in BOOT_CODE


def test_scene_registration_is_separate_from_arming_patches():
    """The harness must be able to arm patches without touching Godot.

    `NodeFactory.RegisterSceneType` reaches native Godot string helpers, so it
    cannot run in a bare .NET process. Keeping `Install()` out of `ApplyAll()`
    is what lets the offline bite-check exist at all.
    """
    apply_all = re.search(r"public static int ApplyAll\(.*?\n    \}", BOOT_CODE, re.S)
    assert apply_all, BOOT_CODE
    assert "Install()" not in apply_all.group(0), (
        "ApplyAll must not call Install(); the offline harness arms patches "
        "in a process with no Godot runtime")


# --- the proof art --------------------------------------------------------

HARD_REQUIRED_NODES = ("Visuals", "Bounds", "IntentPos", "CenterPos")


def test_the_proof_scene_declares_every_node_ncreaturevisuals_throws_without():
    """`_Ready` uses GetNode<T>, not GetNodeOrNull, for these four.

    A scene missing one does not degrade -- it throws while the creature node
    is being built, which surfaces as a combat that never starts.
    """
    for name in HARD_REQUIRED_NODES:
        block = re.search(
            rf'\[node name="{name}" type="(\w+)" parent="[^"]*"\]\n((?:.+\n)*?)\n',
            SCENE)
        assert block, f"the proof scene has no {name} node"
        assert "unique_name_in_owner = true" in block.group(2), (
            f"{name} must be addressable as %{name}; NCreatureVisuals looks it "
            "up by unique name")

    types = dict(re.findall(r'\[node name="(\w+)" type="(\w+)"', SCENE))
    assert types["Visuals"] == "Node2D"
    assert types["Bounds"] == "Control"
    assert types["IntentPos"] == "Marker2D"
    assert types["CenterPos"] == "Marker2D"


def test_the_proof_scene_carries_no_script():
    """pck-src standing rule: behaviour attaches from C#, never from a scene.

    Our assembly builds with plain Microsoft.NET.Sdk and has no ScriptPath
    mapping, so an `ext_resource type="Script"` cannot resolve at all -- it is
    a load failure, not a degraded scene.
    """
    assert 'type="Script"' not in SCENE


def test_the_proof_art_is_drawn_here_and_imports_nothing():
    """Original geometry, checkable.

    Every visible shape is a Polygon2D with its vertices in the file. No
    texture, no import, nothing derived from the base game or from any other
    work -- which is what keeps a rendering proof from carrying a rights
    question into the morning.
    """
    assert "ext_resource" not in SCENE, (
        "the proof scene pulls in an external resource; it must be "
        "self-contained original geometry")
    polygons = re.findall(r"polygon = PackedVector2Array\(([^)]+)\)", SCENE)
    assert len(polygons) >= 5, f"only {len(polygons)} drawn shapes"
    for verts in polygons:
        coords = [c for c in verts.split(",") if c.strip()]
        assert len(coords) >= 6 and len(coords) % 2 == 0, verts


def test_the_scene_root_carries_no_transform():
    """BaseLib's factory frees the root and keeps only its children.

    `TransferAndCreateNodes` moves the source root's CHILDREN onto a freshly
    constructed NCreatureVisuals and calls QueueFree on the root, so anything
    positioned on the root is silently lost. Same shape as the shipped
    klee/model/combat.tscn.
    """
    root = re.search(r'\[node name="\w+" type="Node2D"\]\n(.*?)\n\[', SCENE, re.S)
    assert root, SCENE
    assert root.group(1).strip() == "", (
        f"the scene root declares {root.group(1)!r}; the factory discards the "
        "root, so position it on the children instead")


# --- containment ----------------------------------------------------------

def test_the_spike_is_not_wired_into_any_build_or_deploy_path():
    """A spike that ships by accident is the failure mode of a spike.

    Nothing about this may reach a deployed build until [USER] rules on the
    subject enemy, so no shared build script may name it.
    """
    watched = [
        ROOT / "klee-mod" / "KleeCode" / "KleeCode.csproj",
        ROOT / "klee-mod" / "build" / "deploy.ps1",
        ROOT / "klee-mod" / "build" / "validate.ps1",
        ROOT / "tools" / "build_pck.ps1",
    ]
    for path in watched:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in ("lane-d-enemy-seam", "EnemySeamSpike", "laned-enemy-seam"):
            assert token not in text, f"{path.name} references {token}"


def test_the_spike_does_not_live_inside_the_shipped_assembly_tree():
    """`klee-mod/KleeCode` is scanned by four gates that would now see it.

    lint_constant_parity, lint_pool_membership, test_roster_runtime_contracts
    and the codegen manifests all walk that tree. Keeping the spike beside it
    rather than inside it is why none of them changed.
    """
    assert not (ROOT / "klee-mod" / "KleeCode" / "spikes").exists()
    assert SEAM_PATH.is_relative_to(ROOT / "klee-mod" / "spikes")
