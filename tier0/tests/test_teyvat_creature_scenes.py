"""The dressed enemy bodies: one table, one producer, one shape (`EB-811`).

Four things can drift apart here and every one of them is silent in the game
rather than loud:

  * a committed `.tscn` under `klee-mod/pck-src/teyvat/creature_visuals` can be
    hand-edited away from what `tools/gen_teyvat_creature_scenes.py` would
    write, so the next run of the generator quietly reverts someone's fix;
  * `TeyvatCreaturesGenerated.cs` can fall behind the table, so a body has a
    scene the C# never names;
  * the pck contract can claim a row nothing produces, or miss one that is
    committed;
  * a body can get its picture without its NAME, or the reverse -- which on
    the screen is a Genshin body announcing itself as a Nibbit.

The failure mode for the first three is the pink fallback creature
(`MonsterModel.CreateVisuals`'s catch), which "works" and looks like a bug;
the failure mode for the fourth is a dressing that reads as a defect. All four
are deploy questions, and the point of this file is that they are asked
headlessly instead.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import gen_teyvat_creature_scenes as gen        # noqa: E402
from tools.visual_qa import contract                        # noqa: E402

FIXTURE = ROOT / "tools" / "visual_qa" / "fixtures" / "sample.contract.txt"
GENERATED_CS = ROOT / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatCreaturesGenerated.cs"
ROWS = gen.load()


def test_the_committed_scenes_and_the_c_sharp_table_are_not_stale():
    """The staleness gate, on `gen_act_placeholders.py`'s precedent."""
    problems = gen.check(ROOT, ROWS)
    assert problems == [], "\n".join(problems)


def test_every_scene_is_the_tables_and_the_directory_holds_no_other():
    committed = {
        p.name for p in
        (ROOT / "klee-mod" / "pck-src" / "teyvat" / "creature_visuals").glob("*.tscn")
    }
    assert committed == {f"{name}.tscn" for name in gen.scenes(ROWS)}


def test_a_scene_per_size_class_and_no_more():
    """One scene per body, EXCEPT where the table gives a plate two classes.

    A scene fixes one sprite scale, so a plate that dresses a boss on one face
    and a regular on another cannot share one `.tscn` -- and a plate that does
    not must not be split, or the directory doubles for nothing. Motion splits
    a body the same way and is checked in the same breath: a scene names ONE
    library, so two rows wanting two motions are two scenes.
    """
    variants = {}
    for row in ROWS:
        variants.setdefault(row.body, set()).add((row.size_class, row.motion))
    for body, seen in variants.items():
        ids = {r.scene_id for r in ROWS if r.body == body}
        if len(seen) == 1:
            assert ids == {body}, body
            continue
        # The suffix names only the axis that varies, so a body that differs in
        # class alone still reads `<body>_<class>` and a rename never happens
        # for a reason nobody can see in the table.
        classes = {c for c, _ in seen}
        motions = {m for _, m in seen}
        expected = set()
        for klass, motion in seen:
            parts = [body]
            if len(classes) > 1:
                parts.append(klass)
            if len(motions) > 1:
                parts.append(motion)
            expected.add("_".join(parts))
        assert ids == expected, body
    # Every scene draws its body's own plate, whatever the scene is called.
    for name, row in gen.scenes(ROWS).items():
        assert f'path="{gen.RES_ROOT}/{row.body}.png"' in gen.scene_source(row), name


def test_the_contract_fixture_names_the_same_bodies():
    """A row nothing produces, or a scene the pack would not carry.

    Both directions, because comparing a set against itself answers neither.
    """
    parsed = contract.parse(FIXTURE.read_text(encoding="utf-8"))
    prefix = "teyvat/creature_visuals/"
    rows = {r for r in parsed.resource_set if r.startswith(prefix)}
    expected = {f"{prefix}{body}.png" for body in gen.bodies(ROWS)}
    expected |= {f"{prefix}{name}.tscn" for name in gen.scenes(ROWS)}
    assert rows == expected

    # And the motion libraries, which are a second producer under a second
    # prefix -- `build_pck.ps1` overlays `pck-src` verbatim, so a `.tres` packs
    # exactly as a `.tscn` does and the contract derives it the same way.
    motion = {r for r in parsed.resource_set if r.startswith("teyvat/motion/")}
    assert motion == {f"teyvat/motion/{name}.tres" for name in gen.MOTIONS}


def test_a_picture_and_a_name_are_the_same_row():
    """The whole reason one table feeds both C# dictionaries."""
    text = GENERATED_CS.read_text(encoding="utf-8")
    for row in ROWS:
        if not row.live:
            continue
        face = f"TeyvatFrame.{row.face.capitalize()}"
        assert f'[({face}, "{row.base_entry}")] =' in text, row
        assert f'[({face}, "{row.base_entry}.name")] =' in text, row


def test_every_scene_carries_the_four_nodes_ncreaturevisuals_demands():
    """`_Ready` fetches these with `GetNode`, not `GetNodeOrNull`.

    A scene missing any one of them throws before the picture is ever drawn,
    and the throw is swallowed into the fallback body.
    """
    for relative, text in gen.scene_sources(ROWS).items():
        for node in ('name="Visuals"', 'name="Bounds"',
                     'name="IntentPos"', 'name="CenterPos"'):
            assert node in text, (relative, node)
        # `unique_name_in_owner` is what makes the `%` lookups resolve; the
        # four the engine fetches, plus `%AnimationPlayer` and `%AnimationTree`
        # which `Vfx/CreatureAnimationRouter` and `Vfx/ModdedPlayerDeathSeam`
        # look up by exactly that name.
        assert text.count("unique_name_in_owner = true") == 6, relative
        # No script, per `pck-src/README.md` -- and load-bearing here, because
        # a scripted root is the wrong type for the cast in `CreateVisuals`.
        assert 'type="Script"' not in text, relative
        # `Visuals.Scale` is `NCreature`'s (memory:
        # sts2-creature-visual-invariants item 2), so the scale rides the
        # `Sprite2D` we own underneath it.
        visuals = text.split('[node name="Visuals"')[1].split("[node")[0]
        assert "scale" not in visuals, relative


def test_the_bounds_the_intent_and_the_centre_all_move_with_the_scale():
    """A grown plate whose bounds did not grow puts the HP bar on its waist."""
    for body, row in gen.bodies(ROWS).items():
        text = gen.scene_source(row)
        height = gen.PLATE_H * row.scale
        assert f"offset_top = {gen._f(-height)}" in text, body
        assert f"offset_left = {gen._f(-gen.PLATE_W / 2 * row.scale)}" in text, body
        assert f"offset_right = {gen._f(gen.PLATE_W / 2 * row.scale)}" in text, body
        assert f"Vector2(0, {gen._f(-height - gen.INTENT_CLEARANCE)})" in text, body
        assert f"Vector2(0, {gen._f(-height / 2)})" in text, body


def test_the_three_size_classes_are_the_three_numbers_the_docstring_derives():
    """Pinned so a re-scale is a decision, not a diff nobody reads."""
    assert gen.SCALES == {"regular": 1.0, "elite": 1.3, "boss": 1.6}
    assert (gen.PLATE_W, gen.PLATE_H) == (240, 280)


def test_the_spikes_one_row_survives_the_generalisation():
    """Nibbit is still the Wooden Shield Hilichurl Guard, in Mondstadt only.

    ONLY Mondstadt, and that is the re-keying: `NIBBIT` is an Overgrowth entry
    and the Liyue face stands on the Underdocks, so a Liyue row keyed on it
    could never fire.
    """
    nibbit = [r for r in ROWS if r.base_entry == "NIBBIT"]
    assert {r.face for r in nibbit} == {"MONDSTADT"}
    assert nibbit[0].body == "wooden_shield_hilichurl_guard"
    assert nibbit[0].display_name == "Wooden Shield Hilichurl Guard"


#: The two act-1 zones, as `Acts/Overgrowth.cs` and `Acts/Underdocks.cs`
#: roll them in v0.111.0. A face dresses the zone it REPLACES
#: (`Patches/ModelDbActsPatch.Swaps`), so a row keyed outside its own zone can
#: never fire -- which is exactly what the first pass shipped and the running
#: game caught.
#:
#: All 29 Overgrowth entries, not the 22 the first pass had names for: the
#: 2026-09-17 census re-read `Acts/Overgrowth.cs`'s encounters through
#: `AllPossibleMonsters` and every `ModelDb.Monster<>` reference, and found the
#: five Ruby Raiders, the Wriggler and the Eye with Teeth, which the act-1
#: mapping packet's Table A never scored.
OVERGROWTH = {
    "ASSASSIN_RUBY_RAIDER", "AXE_RUBY_RAIDER", "BRUTE_RUBY_RAIDER",
    "BYGONE_EFFIGY", "BYRDONIS", "CEREMONIAL_BEAST", "CROSSBOW_RUBY_RAIDER",
    "CUBEX_CONSTRUCT", "EYE_WITH_TEETH",
    "FLYCONID", "FOGMOG", "FUZZY_WURM_CRAWLER", "INKLET", "KIN_FOLLOWER",
    "KIN_PRIEST", "LEAF_SLIME_M", "LEAF_SLIME_S", "MAWLER", "NIBBIT",
    "PHROG_PARASITE", "SHRINKER_BEETLE", "SLITHERING_STRANGLER",
    "SNAPPING_JAXFRUIT", "TRACKER_RUBY_RAIDER", "TWIG_SLIME_M",
    "TWIG_SLIME_S", "VANTOM", "VINE_SHAMBLER", "WRIGGLER",
}
UNDERDOCKS = {
    "CALCIFIED_CULTIST", "CORPSE_SLUG", "DAMP_CULTIST", "FAT_GREMLIN",
    "FOSSIL_STALKER", "GAS_BOMB", "GREMLIN_MERC", "HAUNTED_SHIP",
    "LAGAVULIN_MATRIARCH", "LIVING_FOG", "PHANTASMAL_GARDENER",
    "PUNCH_CONSTRUCT", "SEAPUNK", "SEWER_CLAM", "SKULKING_COLONY",
    "SLUDGE_SPINNER", "SNEAKY_GREMLIN", "SOUL_FYSH", "TERROR_EEL", "TOADPOLE",
    "TWO_TAILED_RAT", "WATERFALL_GIANT",
}


def test_each_act_one_face_keys_only_the_zone_it_stands_on():
    """The defect this file was extended for.

    Mondstadt replaces Overgrowth and Liyue replaces the Underdocks. The first
    pass keyed every Liyue row on an Overgrowth entry, so a Liyue run drew
    undressed fights and nothing failed anywhere -- a lookup that never fires
    looks exactly like a lookup that is not needed.
    """
    for face, zone in (("MONDSTADT", OVERGROWTH), ("LIYUE", UNDERDOCKS)):
        keyed = {r.base_entry for r in ROWS if r.face == face and r.live}
        assert keyed <= zone, (face, sorted(keyed - zone))


def test_no_surviving_row_calls_itself_inert():
    """The re-keying's own acceptance: every live row can actually fire."""
    for row in ROWS:
        assert "inert" not in row.notes, row


def test_one_id_entry_draws_one_body():
    """`gen.load` refuses a double claim; this says so out loud."""
    keys = [(r.face, r.base_entry) for r in ROWS if r.live]
    assert len(keys) == len(set(keys))


def test_every_face_in_the_table_is_a_face_teyvatframe_holds():
    assert {r.face for r in ROWS} <= set(gen.FACES)


# ---------------------------------------------------------------------------
# MOTION (pass one): five shared sets on a Rig node
# ---------------------------------------------------------------------------
#
# The failure modes here are all silent in the running game, which is why they
# are asked headlessly:
#
#   * a clip keying `Body` would flatten every elite and boss to regular size
#     the first time it played, because `Body`'s scale IS the size class;
#   * a clip keying `%Visuals` would fight `NCreature.ScaleTo` for a property
#     the engine owns;
#   * a track on a node the scene does not have never moves and never says so;
#   * a scene whose `.tres` is not in the pack loads with an empty library and
#     the tree's `Travel` becomes a no-op.

#: The Body transform per size class, pinned as LITERALS rather than derived.
#: The motion pass moved `Body` one level down the tree (under `Rig`) and had
#: to leave these numbers untouched -- a plate that changed size while nobody
#: was looking is exactly the drift a derived check would agree with.
BODY_TRANSFORM = {
    "regular": ("Vector2(0, -140.0)", "Vector2(1.0, 1.0)"),
    "elite": ("Vector2(0, -182.0)", "Vector2(1.3, 1.3)"),
    "boss": ("Vector2(0, -224.0)", "Vector2(1.6, 1.6)"),
}


def test_the_body_transform_did_not_move_when_the_rig_went_in():
    for name, row in gen.scenes(ROWS).items():
        position, scale = BODY_TRANSFORM[row.size_class]
        body = gen.scene_source(row).split('[node name="Body"')[1].split("[node")[0]
        assert f"position = {position}" in body, name
        assert f"scale = {scale}" in body, name


def test_every_scene_carries_the_rig_the_player_and_the_tree():
    """The three nodes the motion pass added, and where each of them sits.

    `Rig` is between `%Visuals` and `Body` and is the ONLY node a clip moves:
    `%Visuals` is the engine's and `Body` carries the size class. The player
    and the tree are root-level siblings, which is what makes
    `anim_player = NodePath("../AnimationPlayer")` resolve after BaseLib's
    factory reparents our children onto a fresh `NCreatureVisuals`.
    """
    for relative, text in gen.scene_sources(ROWS).items():
        assert '[node name="Rig" type="Node2D" parent="Visuals"]' in text, relative
        assert '[node name="Body" type="Sprite2D" parent="Visuals/Rig"]' in text, relative
        assert ('[node name="AnimationPlayer" type="AnimationPlayer" parent="."]'
                in text), relative
        assert ('[node name="AnimationTree" type="AnimationTree" parent="."]'
                in text), relative
        assert 'anim_player = NodePath("../AnimationPlayer")' in text, relative


def test_every_scene_names_a_motion_library_that_exists():
    for name, row in gen.scenes(ROWS).items():
        assert row.motion in gen.MOTIONS, name
        text = gen.scene_source(row)
        assert (f'[ext_resource type="AnimationLibrary" '
                f'path="{row.motion_library}"') in text, name
        committed = (ROOT / "klee-mod" / "pck-src" / "teyvat" / "motion"
                     / f"{row.motion}.tres")
        assert committed.is_file(), name


def test_every_row_names_a_legal_motion_and_load_refuses_anything_else():
    assert {r.motion for r in ROWS} <= set(gen.MOTIONS)
    assert gen.MOTION_SETS == ("stand", "bounce", "hover", "loom", "mech")


def test_the_assignment_rule_still_answers_for_every_body():
    """`default_motion` is the rule that FILLED the column, not a gate on it.

    It must keep answering -- a body added tomorrow is given a motion by it --
    and its answer must be legal. It is deliberately NOT compared against the
    committed column: a veto on one row is a one-cell edit and nothing here
    argues back.
    """
    for row in ROWS:
        assert gen.default_motion(row.body, row.size_class) in gen.MOTIONS, row


def test_every_clip_keys_only_the_four_paths_a_creature_scene_carries():
    """The one that would be invisible: a track on `Body` or on `%Visuals`."""
    allowed = set(gen.ALLOWED_TRACKS)
    for name, clips in gen.MOTIONS.items():
        for clip in clips:
            for track in clip.tracks:
                assert track.path in allowed, (name, clip.name, track.path)
    # And the same read off the committed TEXT, not off the data that wrote it.
    for relative, text in gen.motion_sources().items():
        paths = set(re.findall(r'path = NodePath\("([^"]+)"\)', text))
        assert paths <= allowed, (relative, sorted(paths - allowed))
        assert paths, relative


def test_every_set_carries_the_five_clips_the_router_needs():
    for name, clips in gen.MOTIONS.items():
        assert {c.name for c in clips} == set(gen.CLIP_NAMES), name
        # Only `idle` loops: attack, hurt and death each return to idle at the
        # end of the clip (or, for death, do not return at all), and a looping
        # one would never reach that end.
        assert {c.name for c in clips if c.loop} == {"idle"}, name
        # RESET keys every property any clip in the set touches, or a death
        # fade leaves the next body half-transparent.
        reset = next(c for c in clips if c.name == "RESET")
        touched = {t.path for c in clips for t in c.tracks}
        assert touched <= {t.path for t in reset.tracks}, name


def test_the_death_clip_is_the_length_the_seam_will_report():
    """`ModdedPlayerDeathSeam` reads this number off the clip at runtime.

    Pinned so a set whose death clip grew past the base's 30 s ceiling, or
    shrank to nothing, is a decision rather than a diff nobody reads.
    """
    for name, clips in gen.MOTIONS.items():
        death = next(c for c in clips if c.name == "death")
        assert 0.5 <= death.length <= 30.0, (name, death.length)


def test_no_generated_file_carries_a_comment_line():
    """A `.tscn`/`.tres` that fails to parse falls back SILENTLY.

    `MonsterModel.CreateVisuals` swaps in the pink error body, which "works"
    and looks like a bug -- so the provenance lives in the README and in
    `--check`, neither of which has to survive a parser.
    """
    files = {**gen.scene_sources(ROWS), **gen.motion_sources()}
    for relative, text in files.items():
        for number, line in enumerate(text.splitlines(), start=1):
            assert not line.lstrip().startswith((";", "#")), (relative, number)


def test_the_committed_motion_directory_is_exactly_the_five_sets():
    directory = ROOT / "klee-mod" / "pck-src" / "teyvat" / "motion"
    assert {p.name for p in directory.glob("*")} == {
        f"{name}.tres" for name in gen.MOTIONS}
