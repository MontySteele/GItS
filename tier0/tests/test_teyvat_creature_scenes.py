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


def test_every_body_has_exactly_one_scene_and_the_directory_holds_no_other():
    committed = {
        p.name for p in
        (ROOT / "klee-mod" / "pck-src" / "teyvat" / "creature_visuals").glob("*.tscn")
    }
    assert committed == {f"{body}.tscn" for body in gen.bodies(ROWS)}


def test_the_contract_fixture_names_the_same_bodies():
    """A row nothing produces, or a scene the pack would not carry.

    Both directions, because comparing a set against itself answers neither.
    """
    parsed = contract.parse(FIXTURE.read_text(encoding="utf-8"))
    prefix = "teyvat/creature_visuals/"
    rows = {r for r in parsed.resource_set if r.startswith(prefix)}
    expected = set()
    for body in gen.bodies(ROWS):
        expected.add(f"{prefix}{body}.tscn")
        expected.add(f"{prefix}{body}.png")
    assert rows == expected


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
        # `unique_name_in_owner` is what makes the `%` lookups resolve; four
        # nodes, four declarations.
        assert text.count("unique_name_in_owner = true") == 4, relative
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
    """Nibbit is still the Wooden Shield Hilichurl Guard, in Mondstadt only."""
    nibbit = [r for r in ROWS if r.base_entry == "NIBBIT"]
    assert {r.face for r in nibbit} == {"MONDSTADT", "LIYUE"}
    mondstadt = next(r for r in nibbit if r.face == "MONDSTADT")
    assert mondstadt.body == "wooden_shield_hilichurl_guard"
    assert mondstadt.display_name == "Wooden Shield Hilichurl Guard"


def test_one_id_entry_draws_one_body():
    """`gen.load` refuses a double claim; this says so out loud."""
    keys = [(r.face, r.base_entry) for r in ROWS if r.live]
    assert len(keys) == len(set(keys))


def test_every_face_in_the_table_is_a_face_teyvatframe_holds():
    assert {r.face for r in ROWS} <= set(gen.FACES)
