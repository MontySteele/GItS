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
from tools.visual_qa import contract, godot_scene            # noqa: E402

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
    # Every scene draws its body's own art, whatever the scene is called: the
    # whole plate for a shared-set row, that plate's own cut layers for a
    # bespoke one -- and never another body's.
    for name, row in gen.scenes(ROWS).items():
        text = gen.scene_source(row)
        if row.bespoke:
            for layer in gen.manifests()[row.body]:
                assert f'path="{gen.layer_res(row.body, layer)}"' in text, name
        else:
            assert f'path="{gen.RES_ROOT}/{row.body}.png"' in text, name


def test_the_contract_fixture_names_the_same_bodies():
    """A row nothing produces, or a scene the pack would not carry.

    Both directions, because comparing a set against itself answers neither.
    """
    parsed = contract.parse(FIXTURE.read_text(encoding="utf-8"))
    prefix = "teyvat/creature_visuals/"
    rows = {r for r in parsed.resource_set if r.startswith(prefix)}
    expected = {f"{prefix}{body}.png" for body in gen.bodies(ROWS)}
    expected |= {f"{prefix}{name}.tscn" for name in gen.scenes(ROWS)}
    # Pass two: a bespoke body's CUT LAYERS are packed beside its plate, under
    # a directory of the plate's own name. Which layers exist is a third
    # question from "which plates" and "which scenes", and the cut manifest is
    # what answers it.
    expected |= set(gen.layer_resources(ROWS))
    assert rows == expected

    # And the motion libraries, which are a second producer under a second
    # prefix -- `build_pck.ps1` overlays `pck-src` verbatim, so a `.tres` packs
    # exactly as a `.tscn` does and the contract derives it the same way.
    motion = {r for r in parsed.resource_set if r.startswith("teyvat/motion/")}
    assert motion == (
        {f"teyvat/motion/{name}.tres" for name in gen.MOTIONS}
        | {f"teyvat/motion/{gen.BESPOKE}/{body}.tres"
           for body in gen.BESPOKE_CLIPS})


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
        if row.bespoke:
            continue
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
        row = next(r for r in ROWS
                   if relative.endswith(f"/{r.scene_id}.tscn"))
        if not row.bespoke:
            assert ('[node name="Body" type="Sprite2D" parent="Visuals/Rig"]'
                    in text), relative
        assert ('[node name="AnimationPlayer" type="AnimationPlayer" parent="."]'
                in text), relative
        assert ('[node name="AnimationTree" type="AnimationTree" parent="."]'
                in text), relative
        assert 'anim_player = NodePath("../AnimationPlayer")' in text, relative


MOTION_DIR = ROOT / "klee-mod" / "pck-src" / "teyvat" / "motion"


def test_every_scene_names_a_motion_library_that_exists():
    for name, row in gen.scenes(ROWS).items():
        assert row.motion in gen.LEGAL_MOTIONS, name
        text = gen.scene_source(row)
        assert (f'[ext_resource type="AnimationLibrary" '
                f'path="{row.motion_library}"') in text, name
        committed = MOTION_DIR / row.motion_library.split("teyvat/motion/")[1]
        assert committed.is_file(), name


def test_every_row_names_a_legal_motion_and_load_refuses_anything_else():
    assert {r.motion for r in ROWS} <= set(gen.LEGAL_MOTIONS)
    assert gen.MOTION_SETS == ("stand", "bounce", "hover", "loom", "mech")
    assert gen.LEGAL_MOTIONS == gen.MOTION_SETS + ("bespoke",)


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
    for name in gen.MOTIONS:
        text = gen.motion_source(name)
        paths = set(re.findall(r'path = NodePath\("([^"]+)"\)', text))
        assert paths <= allowed, (name, sorted(paths - allowed))
        assert paths, name


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


def test_the_idle_tempo_is_the_one_the_user_look_asked_for():
    """`EB-816`, [USER] on `0.2.3656` (2026-09-17): a pack of slimes "all
    bobbing at the exact same time at high speed".

    HIGH SPEED was `bounce`'s idle, a whole squash-and-stretch cycle in one
    second. It is two seconds now, with a rest at the bottom of the squash;
    `hover` went 2.4 -> 3.0 beside it. The other three sets were not the
    complaint and did not move, and pinning THEM is the point of this test as
    much as pinning the two: a tempo pass that quietly retuned `stand` would
    have changed 72 rows nobody looked at.

    Seen to FAIL: bounce was 1.0 and hover 2.4.
    """
    idles = {name: next(c for c in clips if c.name == "idle").length
             for name, clips in gen.MOTIONS.items()}

    assert idles["bounce"] == 2.0
    assert idles["hover"] == 3.0
    assert idles["stand"] == 2.6
    assert idles["loom"] == 3.5
    assert idles["mech"] == 1.0

    # THE REST AT THE BOTTOM is the shape, not just the length: the squash
    # value is held across two adjacent keys, which is what reads as weight.
    bounce = next(c for c in gen.MOTIONS["bounce"] if c.name == "idle")
    track = next(t for t in bounce.tracks if t.path == gen.RIG_SCALE)
    assert track.times == (0, 0.5, 0.7, 1.2, 2.0)
    assert track.values[1] == track.values[2]
    assert 0.15 <= track.times[2] - track.times[1] <= 0.25

    # And the amplitude eased down rather than up -- a slower body moving as
    # far as it did would read as a pulse. 0.8x of what it was.
    assert track.values[1] == (1.032, 0.976)
    assert track.values[3] == (0.976, 1.032)

    # Nothing but the two idles moved: attack, hurt and death are untouched
    # across every set, so R213's freeze on what an enemy DOES is not even
    # adjacent to this.
    assert [c.length for c in gen.MOTIONS["bounce"] if c.name != "idle"] \
        == [0.001, 0.5, 0.4, 1.2]
    assert [c.length for c in gen.MOTIONS["hover"] if c.name != "idle"] \
        == [0.001, 0.5, 0.4, 1.2]


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
    assert {p.name for p in MOTION_DIR.glob("*")} == (
        {f"{name}.tres" for name in gen.MOTIONS} | {gen.BESPOKE})


# ---------------------------------------------------------------------------
# MOTION (pass two): bespoke layered rigs for six bosses
# ---------------------------------------------------------------------------
#
# Everything pass one could get wrong silently, pass two can get wrong twice
# over, because a bespoke body has more parts to disagree about:
#
#   * a clip can key `Visuals/Rig/<layer>` for a layer the cut never produced,
#     and a track on a node that is not there never moves and never says so;
#   * a scene can grow or shrink the box it occupies, which moves the HP bar
#     and the intent marker off the body;
#   * one plate with two size classes (the Golden Wolflord) shares ONE library,
#     so a layer whose rest pose depended on the class would be right in one
#     scene and wrong in the other;
#   * a fence, a manifest or a library can go missing and leave a boss standing
#     perfectly still in pass one's clothes.

BESPOKE_ROWS = [r for r in ROWS if r.bespoke]


def test_the_six_bespoke_bodies_are_the_six_the_table_names():
    assert {r.body for r in BESPOKE_ROWS} == set(gen.BESPOKE_CLIPS)
    assert set(gen.BESPOKE_CLIPS) == {
        "azhdaha", "all_devouring_narwhal", "rhodeia_of_loch",
        "emperor_of_fire_and_iron", "golden_wolflord",
        "everlasting_lord_of_arcane_wisdom"}
    # Every row of a bespoke body is bespoke -- a plate that looms on one face
    # and rigs on another would split into two scenes for a reason nobody
    # decided.
    for row in ROWS:
        if row.body in gen.BESPOKE_CLIPS:
            assert row.bespoke, row


def test_a_bespoke_row_has_a_fence_a_manifest_and_a_library():
    """`check` refuses each of the three by name; this says so out loud."""
    assert gen.bespoke_gaps(ROOT, ROWS) == []
    for body in gen.BESPOKE_CLIPS:
        assert (ROOT / gen.fence_relative(body)).is_file(), body
        assert (ROOT / gen.manifest_relative(body)).is_file(), body
        assert (MOTION_DIR / gen.BESPOKE / f"{body}.tres").is_file(), body


def test_every_bespoke_layer_node_is_a_layer_of_that_bodys_cut():
    """The scene's node names ARE the manifest's keys, in its order.

    Not "a subset": the scene draws every layer the cut produced, or a piece
    of the boss is simply missing from the arena, and it draws them in the
    manifest's back-to-front order, which is the only thing that decides what
    overlaps what.
    """
    for name, row in gen.scenes(ROWS).items():
        if not row.bespoke:
            continue
        text = gen.scene_source(row)
        drawn = re.findall(
            r'\[node name="([^"]+)" type="Sprite2D" parent="Visuals/Rig"\]', text)
        assert drawn == list(gen.manifests()[row.body]), name


def test_every_bespoke_clip_keys_only_that_bodys_own_layers():
    """A track on a node the scene does not have never moves and never says so."""
    for body in gen.BESPOKE_CLIPS:
        layers = tuple(gen.manifests()[body])
        for clip in gen.bespoke_clips(ROOT, body):
            for track in clip.tracks:
                assert gen.legal_track(track.path, layers), (body, clip.name,
                                                             track.path)
        # And the same read off the committed TEXT, not off the data.
        text = gen.bespoke_source(ROOT, body)
        for path in re.findall(r'path = NodePath\("([^"]+)"\)', text):
            assert gen.legal_track(path, layers), (body, path)


def test_every_bespoke_set_carries_the_five_clips_and_resets_what_it_touches():
    for body in gen.BESPOKE_CLIPS:
        clips = gen.bespoke_clips(ROOT, body)
        assert {c.name for c in clips} == set(gen.CLIP_NAMES), body
        assert {c.name for c in clips if c.loop} == {"idle"}, body
        reset = next(c for c in clips if c.name == "RESET")
        touched = {t.path for c in clips for t in c.tracks}
        assert touched <= {t.path for t in reset.tracks}, body
        death = next(c for c in clips if c.name == "death")
        assert 0.5 <= death.length <= 30.0, (body, death.length)


def test_the_layers_occupy_exactly_the_box_the_single_body_did():
    """The three markers are the whole reason this has to hold.

    `%Bounds`, `%IntentPos` and `%CenterPos` are derived from the plate and the
    size class and nothing else, so a bespoke scene that drew its layers at a
    different scale would put the health bar somewhere the boss is not. The
    check is that the three lines are byte-identical to the ones the SAME row
    would have carried under a shared set, and that every layer sprite takes
    the size class exactly as `Body` does.
    """
    for name, row in gen.scenes(ROWS).items():
        if not row.bespoke:
            continue
        _, scale = BODY_TRANSFORM[row.size_class]
        text = gen.scene_source(row)
        shared = gen.scene_source(gen.replace(row, motion="loom"))
        for marker in ('[node name="Bounds"', '[node name="IntentPos"',
                       '[node name="CenterPos"'):
            assert (text.split(marker)[1].split("[node")[0]
                    == shared.split(marker)[1].split("[node")[0]), (name, marker)
        for layer in gen.manifests()[row.body]:
            block = text.split(f'[node name="{layer}"')[1].split("[node")[0]
            assert f"scale = {scale}" in block, (name, layer)
            # `position` is never written: it stays at the origin so a clip's
            # keys are pure deltas, and the placement rides `offset`, which
            # Godot applies inside the node transform.
            assert "position =" not in block, (name, layer)
            assert "offset = Vector2(" in block, (name, layer)


def test_one_plate_with_two_classes_shares_one_library_and_one_offset_table():
    """The Golden Wolflord, which is why `offset` carries the placement.

    Its two scenes differ in the sprite SCALE and in the three markers, and in
    nothing else -- same layer textures, same offsets, same library. A
    `position`-based placement would have had to differ, and one library
    cannot hold two rest poses.
    """
    boss = gen.scene_source(gen.scenes(ROWS)["golden_wolflord_boss"])
    regular = gen.scene_source(gen.scenes(ROWS)["golden_wolflord_regular"])
    for layer, entry in gen.manifests()["golden_wolflord"].items():
        line = (f"offset = Vector2({gen._n(entry['offset_x'])}, "
                f"{gen._n(entry['offset_y'] - gen.PLATE_H / 2)})")
        assert line in boss, layer
        assert line in regular, layer
    library = 'path="res://teyvat/motion/bespoke/golden_wolflord.tres"'
    assert library in boss and library in regular


def test_every_committed_bespoke_library_parses_as_a_godot_resource():
    """The pass-one parser, pointed at the new folder.

    A `.tres` that does not parse is the quietest failure in this mechanism:
    `AnimationPlayer.libraries` loads nothing, the tree's `Travel` becomes a
    no-op, and the boss stands still looking exactly like pass one's stills.
    """
    directory = MOTION_DIR / gen.BESPOKE
    files = godot_scene.iter_scene_files(directory)
    assert {p.name for p in files} == {
        f"{body}.tres" for body in gen.BESPOKE_CLIPS}
    for path in files:
        parsed = godot_scene.parse(path)
        assert parsed.kind == "gd_resource", path
        animations = {
            section.attrs.get("id") for section in parsed.sub_resources.values()}
        assert animations == {f"Animation_{c}" for c in gen.CLIP_NAMES}, path
        # `load_steps` is what Godot writes and what a stale hand-edit gets
        # wrong: five sub-resources plus the resource itself.
        assert parsed.header_attrs["load_steps"] == "6", path
