"""Gate 2: scenes are checked for broken resource and animation references.

Two halves, both asserted:

  * the fixture scenes carry one defect per rule and every rule must FIRE;
  * the repo's real scenes under klee-mod/pck-src must be CLEAN of every
    error-severity rule -- which is what makes this a gate rather than a
    report. It is allowed to carry warnings (two scenes have a cosmetic
    load_steps drift today); it is not allowed to carry errors.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.visual_qa import contract, godot_scene, scene_deps   # noqa: E402
from tools.visual_qa.findings import ERROR, Report              # noqa: E402

FIXTURES = ROOT / "tools" / "visual_qa" / "fixtures"
PCK_SRC = ROOT / "klee-mod" / "pck-src"
CSHARP = ROOT / "klee-mod" / "KleeCode"


def check_one(name: str, **kwargs) -> Report:
    path = FIXTURES / "scenes" / name
    report = Report(scene_deps.GATE)
    scene_deps.check_scene(godot_scene.parse(path), report, name, **kwargs)
    return report


def rules(report, severity=None):
    return {
        f.rule for f in report.findings
        if severity is None or f.severity == severity
    }


# ---------------------------------------------------------------------------
# the fixtures: every rule fires on a scene built to break it
# ---------------------------------------------------------------------------

def test_undeclared_and_misdeclared_resources():
    report = check_one("bad_refs.tscn")
    found = rules(report)
    assert "SD-EXTRES-UNDECLARED" in found       # ExtResource("9_missing")
    assert "SD-SCRIPT" in found                  # scripts cannot ship in a pck
    assert "SD-EXTPATH-SCHEME" in found          # user:// is not addressable
    assert "SD-EXTRES-UNUSED" in found
    assert "SD-SUBRES-UNUSED" in found
    assert "SD-LOADSTEPS" in found


def test_missing_texture_is_found_only_against_a_resource_universe():
    """No universe -> the gate says so; a universe -> it names the miss."""
    blind = check_one("bad_refs.tscn")
    assert "SD-EXTPATH-MISSING" not in rules(blind)

    seeing = check_one("bad_refs.tscn", universe={"klee/ui/other.png"})
    assert "SD-EXTPATH-MISSING" in rules(seeing, ERROR)
    assert any(
        "klee/ui/char_icon.png" in f.detail
        for f in seeing.findings if f.rule == "SD-EXTPATH-MISSING"
    )


def test_animation_tree_travelling_to_a_missing_state_is_an_error():
    """The silent one: Travel() to an absent animation does nothing, quietly."""
    report = check_one("bad_anim.tscn")
    found = rules(report, ERROR)
    assert "SD-ANIM-MISSING" in found            # plays "hurt", library has idle
    assert "SD-TRANSITION-STATE" in found        # transition to "ghost"
    assert "SD-TRACK-NODE" in found              # track on Missing/Node
    assert "SD-ANIMTREE-PLAYER" in found         # anim_player points at a Sprite2D
    assert any(
        "not an AnimationPlayer" in f.detail
        for f in report.findings if f.rule == "SD-ANIMTREE-PLAYER"
    )


def test_required_creature_states_are_opt_in_and_bite_when_asked():
    off = check_one("bad_anim.tscn")
    assert "SD-REQUIRED-STATE" not in rules(off)

    on = check_one("bad_anim.tscn", require_states=scene_deps.CREATURE_STATES)
    missing = {
        f.detail.split('"')[3]
        for f in on.findings if f.rule == "SD-REQUIRED-STATE"
    }
    assert missing == {"attack", "death"}


def test_router_contract_is_read_from_the_csharp_source_not_invented():
    """CREATURE_STATES must stay equal to CreatureAnimationRouter's map."""
    text = (CSHARP / "Vfx" / "CreatureAnimationRouter.cs").read_text(
        encoding="utf-8")
    body = text[text.index("TriggerToState = new()"):]
    body = body[: body.index("};")]
    states = {
        line.split('"')[3] for line in body.splitlines() if '] = "' in line
    }
    assert set(scene_deps.CREATURE_STATES) == states


# ---------------------------------------------------------------------------
# the live tree: the gate is green on what ships
# ---------------------------------------------------------------------------

def test_live_scenes_carry_no_errors():
    report = scene_deps.run(PCK_SRC, ROOT, csharp_source=CSHARP)
    assert report.errors == [], report.render(verbose=True)
    assert report.checked["scenes"] >= 8
    assert report.checked["animations"] > 0
    assert report.checked["csharp_play_calls"] > 0


def test_live_scenes_resolve_against_the_fixture_contract_universe():
    """Every ext_resource in pck-src is a path the contract fixture knows.

    The fixture contract is a hand-kept list of the eleven textures the
    committed scenes reference; if a scene gains a twelfth and nobody updates
    the fixture, this fails -- which is the point. The live contract is
    gitignored (*.pck.contract.txt), so this is the portable half.
    """
    parsed = contract.parse(
        (FIXTURES / "sample.contract.txt").read_text(encoding="utf-8"))
    report = scene_deps.run(PCK_SRC, ROOT, universe=parsed.resource_set)
    misses = [f for f in report.findings if f.rule == "SD-EXTPATH-MISSING"]
    assert misses == [], "\n".join(str(f) for f in misses)


def test_combat_scenes_carry_the_four_router_states():
    report = scene_deps.run(PCK_SRC, ROOT)
    assert "SD-REQUIRED-STATE" not in rules(report)
    trees = 0
    for path in godot_scene.iter_scene_files(PCK_SRC):
        scene = godot_scene.parse(path)
        for states, _ in scene.state_machines().values():
            trees += 1
            assert set(scene_deps.CREATURE_STATES) <= states, path
    assert trees == 2, "klee and furina combat scenes both drive a state machine"


def test_empty_tree_fails_rather_than_passing(tmp_path):
    report = scene_deps.run(tmp_path, ROOT)
    assert "SD-EMPTY-SWEEP" in rules(report, ERROR)


def test_csharp_interpolated_animation_names_are_matched_as_patterns(tmp_path):
    """`anim.Play($"slot{i + 1}_pop")` is checked, not skipped."""
    source = tmp_path / "src"
    source.mkdir()
    (source / "Bridge.cs").write_text(
        'const string Scene = "furina/ui/salon_stage.tscn";\n'
        'void Go() { anim.Play($"slot{i + 1}_pop"); }\n'
        'void Bad() { anim.Play($"tier{i}_wobble"); }\n',
        encoding="utf-8",
    )
    scenes = {
        path.relative_to(PCK_SRC).as_posix(): godot_scene.parse(path)
        for path in godot_scene.iter_scene_files(PCK_SRC)
    }
    report = Report(scene_deps.GATE)
    scene_deps.check_csharp_animation_names(source, scenes, report, tmp_path)
    details = [f.detail for f in report.findings if f.rule == "SD-CS-ANIM-MISSING"]
    assert len(details) == 1, report.render(verbose=True)
    assert "tier{i}_wobble" in details[0]
