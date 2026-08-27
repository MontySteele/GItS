"""Gate 2 -- resource and animation dependency check for .tscn / .tres.

The failure class this exists for: a scene that references something that is
not there. Today nothing in the repo asks that question of a scene's INSIDES.
`validate.ps1` S6c checks that a C#-referenced `.tscn` path is authored
somewhere and listed in the contract; S12 checks that a C#-referenced pck path
is packed. Neither one opens the scene. So a scene whose sprite points at a
texture nobody exports, or whose AnimationTree travels to a state its
AnimationPlayer does not have, is invisible until the game is running -- and
an AnimationTree travelling to a missing state fails SILENTLY at runtime, so
"until the game is running" can mean "until somebody notices the character
never plays a hurt animation".

Two tiers of check, and the split is what makes this runnable in CI:

  * **Internal** -- everything answerable from the scene text alone. Runs
    everywhere, including on a clean clone with no art and no game.
  * **External** -- ``ext_resource path=`` targets, which can only be resolved
    against a resource universe (the pck contract, or a directory listing).
    When no universe is supplied these are reported as a NOTE saying so,
    never as silence.

Known limits, stated rather than papered over:

  * Animation track NodePaths are resolved against the scene's own node tree
    with the AnimationPlayer's ``root_node`` taken as the scene root when it
    is unset (Godot's default is ``NodePath("..")``, i.e. the player's parent,
    and every player in pck-src is a direct child of the root). A scene that
    parents its player deeper would need the real rule; the gate says so
    instead of guessing.
  * Sub-scene instances (``instance=ExtResource(...)``) are not descended
    into. A track path that crosses into an instanced scene is reported as
    unresolved-but-noted, not as an error.
"""

from __future__ import annotations

import re
from pathlib import Path

from .findings import Report
from .godot_scene import Scene, iter_scene_files, parse

GATE = "scene-deps"

#: The four creature states CreatureAnimationRouter travels to, plus the RESET
#: pose Godot writes. Source: klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs
#: TriggerToState -- idle / attack / hurt / death. Passed in explicitly by the
#: caller; this constant is the documented default for combat scenes, never
#: applied to every scene (a gauge has no "hurt").
CREATURE_STATES = ("idle", "attack", "hurt", "death")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def check_scene(
    scene: Scene,
    report: Report,
    where: str,
    universe: set[str] | None = None,
    require_states: tuple[str, ...] = (),
) -> None:
    """Every rule for one scene. Appends to `report`."""
    ext_ids = set(scene.ext_resources)
    sub_ids = set(scene.sub_resources)
    used_ext: set[str] = set()
    used_sub: set[str] = set()
    for section in scene.sections:
        if section.kind in ("ext_resource", "sub_resource"):
            # A sub_resource may reference another; its own declaration line
            # does not count as a use of itself.
            pass
        e, s = section.ref_ids()
        used_ext |= e
        used_sub |= s
    # A sub_resource referencing itself would be a cycle; not a shape this
    # repo writes, so it is not modelled.

    for ref in sorted(used_ext - ext_ids):
        report.error(
            "SD-EXTRES-UNDECLARED", where,
            f'ExtResource("{ref}") is used but no [ext_resource] declares that id.',
        )
    for ref in sorted(used_sub - sub_ids):
        report.error(
            "SD-SUBRES-UNDECLARED", where,
            f'SubResource("{ref}") is used but no [sub_resource] declares that id.',
        )
    for ref in sorted(ext_ids - used_ext):
        section = scene.ext_resources[ref]
        report.warning(
            "SD-EXTRES-UNUSED", f"{where}:{section.line}",
            f'ext_resource id="{ref}" ({section.attrs.get("path", "?")}) is '
            "declared and never referenced; it still ships in the pack.",
        )
    for ref in sorted(sub_ids - used_sub):
        section = scene.sub_resources[ref]
        # An AnimationLibrary is reached through the player's `libraries`
        # dictionary, which IS a reference, so this only fires on genuinely
        # orphaned sub-resources.
        report.warning(
            "SD-SUBRES-UNUSED", f"{where}:{section.line}",
            f'sub_resource id="{ref}" (type '
            f'{section.attrs.get("type", "?")}) is declared and never referenced.',
        )

    declared = scene.declared_load_steps
    if declared is not None and declared != scene.expected_load_steps:
        report.warning(
            "SD-LOADSTEPS", where,
            f"load_steps={declared} but the file declares "
            f"{len(scene.ext_resources)} ext + {len(scene.sub_resources)} sub "
            f"(= {scene.expected_load_steps}). Godot uses this for load "
            "progress only, so it is cosmetic -- but it means the file was "
            "hand-edited after the editor last wrote it.",
        )

    # --- external paths ---------------------------------------------------
    for res_id, section in sorted(scene.ext_resources.items()):
        path = section.attrs.get("path", "")
        if section.attrs.get("type") == "Script":
            report.error(
                "SD-SCRIPT", f"{where}:{section.line}",
                "scene declares an ext_resource type=\"Script\". Script "
                "resources cannot ship in a mod pck (klee-mod/pck-src/README.md); "
                "behaviour attaches from C#.",
            )
        if not path:
            report.error(
                "SD-EXTRES-NOPATH", f"{where}:{section.line}",
                f'ext_resource id="{res_id}" has no path attribute.',
            )
            continue
        if not path.startswith("res://"):
            report.error(
                "SD-EXTPATH-SCHEME", f"{where}:{section.line}",
                f"ext_resource path {path!r} is not a res:// path; a pck "
                "resource has no other addressable form at runtime.",
            )
            continue
        relative = path[len("res://"):]
        if universe is None:
            continue
        if relative not in universe:
            report.error(
                "SD-EXTPATH-MISSING", f"{where}:{section.line}",
                f"references res://{relative}, which is not in the supplied "
                "resource universe (contract / directory). The scene will "
                "load with a null texture.",
            )

    # --- animation --------------------------------------------------------
    names = scene.animation_names()
    libraries = scene.animation_libraries()
    for lib_id, entries in sorted(libraries.items()):
        for anim_name, anim_sub in sorted(entries.items()):
            if anim_sub not in scene.sub_resources:
                report.error(
                    "SD-ANIMLIB-MISSING", where,
                    f'AnimationLibrary "{lib_id}" maps animation '
                    f'"{anim_name}" to SubResource("{anim_sub}"), which is '
                    "not declared.",
                )

    for player in scene.animation_players():
        raw = player.props.get("libraries", "")
        for sub_ref in re.findall(r'SubResource\("([^"]+)"\)', raw):
            if sub_ref not in libraries:
                report.error(
                    "SD-PLAYER-LIBRARY", f"{where}:{player.line}",
                    f"AnimationPlayer {player.path} loads library "
                    f'SubResource("{sub_ref}"), which is not an '
                    "AnimationLibrary in this scene.",
                )

    for sub_id, anim_name in sorted(scene.animation_node_animations().items()):
        if anim_name not in names:
            report.error(
                "SD-ANIM-MISSING", where,
                f'AnimationNodeAnimation "{sub_id}" plays animation '
                f'"{anim_name}", which no AnimationLibrary in this scene '
                f"declares (has: {sorted(names) or 'none'}). The tree travels "
                "to it and nothing happens -- silently.",
            )

    for sm_id, (states, transitions) in sorted(scene.state_machines().items()):
        known = states | {"Start", "End"}
        for src, dst in transitions:
            for endpoint in (src, dst):
                if endpoint not in known:
                    report.error(
                        "SD-TRANSITION-STATE", where,
                        f'state machine "{sm_id}" has a transition touching '
                        f'"{endpoint}", which is not one of its states '
                        f"({sorted(states)}).",
                    )
        for required in require_states:
            if required not in states:
                report.error(
                    "SD-REQUIRED-STATE", where,
                    f'state machine "{sm_id}" has no "{required}" state. '
                    "CreatureAnimationRouter travels to it on a game trigger; "
                    "a missing state is a no-op the game never reports.",
                )

    for tree in scene.animation_trees():
        raw = tree.props.get("anim_player", "")
        match = re.search(r'NodePath\("([^"]*)"\)', raw)
        if not match:
            report.error(
                "SD-ANIMTREE-PLAYER", f"{where}:{tree.line}",
                f"AnimationTree {tree.path} declares no anim_player NodePath.",
            )
            continue
        target = _resolve_nodepath(scene, tree, match.group(1))
        if target is None:
            report.error(
                "SD-ANIMTREE-PLAYER", f"{where}:{tree.line}",
                f"AnimationTree {tree.path} points anim_player at "
                f'"{match.group(1)}", which resolves to no node in this scene.',
            )
        elif target.type != "AnimationPlayer":
            report.error(
                "SD-ANIMTREE-PLAYER", f"{where}:{tree.line}",
                f"AnimationTree {tree.path} points anim_player at "
                f"{target.path}, which is a {target.type}, not an "
                "AnimationPlayer.",
            )

    # --- animation track targets -----------------------------------------
    node_paths = scene.node_paths()
    unique = scene.unique_names()
    instanced = {node.path for node in scene.nodes if node.is_instance}
    for anim_sub, raw, node_part in scene.animation_track_paths():
        if node_part in ("", "."):
            continue
        if node_part.startswith("%"):
            if node_part[1:].split("/")[0] not in unique:
                report.error(
                    "SD-TRACK-NODE", where,
                    f'animation "{anim_sub}" has a track on {raw!r}; no node '
                    "in this scene carries that unique name.",
                )
            continue
        if node_part in node_paths:
            continue
        if any(node_part.startswith(p + "/") for p in instanced):
            report.note(
                "SD-TRACK-INSTANCED", where,
                f'animation "{anim_sub}" targets {raw!r} inside an instanced '
                "sub-scene; not descended into.",
            )
            continue
        report.error(
            "SD-TRACK-NODE", where,
            f'animation "{anim_sub}" has a track on {raw!r}; the scene has no '
            f"node at {node_part!r}. The track is dead weight and whatever it "
            "was written to move never moves.",
        )


def _resolve_nodepath(scene: Scene, origin, raw: str):
    """Resolve a NodePath written on `origin` against the scene's node tree."""
    if raw.startswith("%"):
        name = raw[1:]
        for node in scene.nodes:
            if node.name == name:
                return node
        return None
    parts = [p for p in raw.split("/") if p != ""]
    current = origin.parent if origin.parent is not None else "."
    for part in parts:
        if part == "..":
            if current in (".", None):
                current = "."
            elif "/" in current:
                current = current.rsplit("/", 1)[0]
            else:
                current = "."
            continue
        current = part if current == "." else f"{current}/{part}"
    return scene.find_node(current)


# ---------------------------------------------------------------------------
# C# side: animation names the mod asks for by name
# ---------------------------------------------------------------------------

#: `anim.Play("flash")`, `anim.Queue($"slot{i + 1}_pop")`. The interpolated
#: form is turned into a pattern rather than skipped -- a rename that misses
#: one of the five slot animations is exactly the defect this catches.
_PLAY_CALL = re.compile(r'\.(?:Play|Queue|PlayBackwards)\(\s*\$?"([^"]*)"')
_SCENE_CONST = re.compile(r'"([A-Za-z0-9_]+(?:/[A-Za-z0-9_./]+)*\.tscn)"')
_INTERP = re.compile(r"\{[^}]*\}")


def _pattern_for(name: str) -> re.Pattern[str]:
    parts = [re.escape(p) for p in _INTERP.split(name)]
    return re.compile("^" + ".+".join(parts) + "$")


def check_csharp_animation_names(
    source_dir: Path, scenes: dict[str, Scene], report: Report, root: Path
) -> None:
    """Every `Play("x")` in C# must name an animation some scene declares.

    Association is per FILE: a `.cs` file that names one or more `.tscn`
    paths is checked against those scenes; a file that names none is checked
    against the union of every scene. That is a heuristic and it is written
    down as one -- it is strictly better than the alternative (no check at
    all) and it cannot produce a false ERROR unless the animation name exists
    in NO scene at all, which is the defect.
    """
    if not source_dir.is_dir():
        report.note("SD-CS-NOSOURCE", _rel(source_dir, root),
                    "C# source directory absent; animation-name cross-check "
                    "did not run.")
        return
    all_names = {n for scene in scenes.values() for n in scene.animation_names()}
    files = sorted(source_dir.rglob("*.cs"), key=lambda p: p.as_posix())
    calls = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        scene_paths = sorted(set(_SCENE_CONST.findall(text)))
        pool = {
            name
            for key, scene in scenes.items()
            if not scene_paths or key in scene_paths
            for name in scene.animation_names()
        } or all_names
        for number, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for match in _PLAY_CALL.finditer(line):
                name = match.group(1)
                calls += 1
                if "{" in name:
                    pattern = _pattern_for(name)
                    if not any(pattern.match(candidate) for candidate in pool):
                        report.error(
                            "SD-CS-ANIM-MISSING", f"{_rel(path, root)}:{number}",
                            f'plays interpolated animation "{name}" and no '
                            f"animation in {scene_paths or 'any scene'} matches "
                            "that shape.",
                        )
                elif name not in pool:
                    report.error(
                        "SD-CS-ANIM-MISSING", f"{_rel(path, root)}:{number}",
                        f'plays animation "{name}", which is declared by no '
                        f"scene in {scene_paths or 'the whole pck-src tree'}.",
                    )
    report.checked["csharp_play_calls"] = calls
    if files and calls == 0:
        report.warning(
            "SD-CS-EMPTY-SWEEP", _rel(source_dir, root),
            f"scanned {len(files)} C# file(s) and found no Play/Queue "
            "animation call. The mod makes several; an empty sweep is the "
            "failure mode, not a pass.",
        )


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def run(
    pck_src: Path,
    root: Path,
    universe: set[str] | None = None,
    csharp_source: Path | None = None,
    require_states_in: tuple[str, ...] = ("model/combat.tscn",),
    required_states: tuple[str, ...] = CREATURE_STATES,
) -> Report:
    """Check every scene under `pck_src`.

    `require_states_in` is a tuple of path SUFFIXES: any scene whose pck-
    relative path ends with one of them must carry the creature state set.
    Passing an empty tuple turns that rule off.
    """
    report = Report(GATE)
    if not pck_src.is_dir():
        report.error("SD-NO-SOURCE", _rel(pck_src, root),
                     "scene source directory does not exist.")
        return report

    files = iter_scene_files(pck_src)
    if not files:
        report.error(
            "SD-EMPTY-SWEEP", _rel(pck_src, root),
            "found no .tscn/.tres files to check. An empty sweep is the "
            "failure mode, not a pass.",
        )
        return report

    scenes: dict[str, Scene] = {}
    for path in files:
        key = path.relative_to(pck_src).as_posix()
        where = _rel(path, root)
        try:
            scene = parse(path)
        except (OSError, UnicodeDecodeError) as exc:
            report.error("SD-UNREADABLE", where, f"{type(exc).__name__}: {exc}")
            continue
        scenes[key] = scene
        wanted = (
            required_states
            if any(key.endswith(suffix) for suffix in require_states_in)
            else ()
        )
        check_scene(scene, report, where, universe=universe, require_states=wanted)
        for section in scene.unknown:
            report.note(
                "SD-UNKNOWN-SECTION", f"{where}:{section.line}",
                f"section [{section.kind}] is not modelled by this reader; "
                "its contents were not checked.",
            )

    report.checked["scenes"] = len(scenes)
    report.checked["ext_resources"] = sum(
        len(s.ext_resources) for s in scenes.values()
    )
    report.checked["animations"] = sum(
        len(s.animation_names()) for s in scenes.values()
    )
    if universe is None:
        report.note(
            "SD-NO-UNIVERSE", _rel(pck_src, root),
            "no resource universe supplied (--contract / --resource-dir), so "
            "ext_resource paths were checked for SHAPE only, never for "
            "existence.",
        )
    if csharp_source is not None:
        check_csharp_animation_names(csharp_source, scenes, report, root)
    return report
