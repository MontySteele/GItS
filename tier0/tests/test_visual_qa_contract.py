"""Gate 4: the pck contract and the staged package are checked against each other.

The live contract is gitignored (`*.pck.contract.txt`), so the fixtures here
are the portable half -- exactly the split tier0/tests/test_pck_reference_gate.py
already draws for validate.ps1's S12.

The rule with real teeth is PK-SRC-UNPACKED: `klee-mod/pck-src` is committed,
its layout IS the pack layout (tools/build_pck.ps1:733-737), so "a scene source
exists in the repo and has no contract row" is answerable on any machine.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.visual_qa import contract                        # noqa: E402
from tools.visual_qa.findings import ERROR, Report          # noqa: E402

FIXTURES = ROOT / "tools" / "visual_qa" / "fixtures"
SAMPLE = FIXTURES / "sample.contract.txt"
PCK_SRC = ROOT / "klee-mod" / "pck-src"


def rules(report, severity=None):
    return {
        f.rule for f in report.findings
        if severity is None or f.severity == severity
    }


def stage(tmp_path: Path, contract_text: str, pck_bytes: bytes = b"PCK-BODY"):
    """A minimal well-formed staged package."""
    package = tmp_path / "stage"
    package.mkdir(parents=True)
    (package / "manifest.json").write_text(
        '{"id": "klee", "has_dll": false, "has_pck": true}', encoding="utf-8")
    (package / "klee.pck").write_bytes(pck_bytes)
    (package / "klee.pck.contract.txt").write_text(contract_text, encoding="utf-8")
    return package


def with_hash(text: str, payload: bytes) -> str:
    digest = hashlib.sha256(payload).hexdigest().upper()
    return "\n".join(
        f"sha256={digest}" if line.startswith("sha256=") else line
        for line in text.splitlines()
    ) + "\n"


# ---------------------------------------------------------------------------
# the contract file itself
# ---------------------------------------------------------------------------

def test_the_sample_contract_is_well_formed():
    parsed = contract.parse(SAMPLE.read_text(encoding="utf-8"))
    report = Report(contract.GATE)
    contract.check_contract(parsed, report, "sample.contract.txt")
    assert report.errors == [], report.render(verbose=True)
    assert parsed.version == "roster-pck-v3"
    # 22 until EB-40, then +6: furina/ui/energy_counter.tscn and the five
    # energy_orb layers it references. Then +2 for the Bake-Kurage pet's
    # creature scene and the summon sprite it draws. Then +6 for the Furina
    # stage's three performers (`EB-725`): a creature scene each, and the three
    # SALON member sprites they draw -- which the pack already carried (the
    # salon copy block) but the fixture did not, because until these scenes
    # nothing referenced them from a scene and the universe is what
    # `scene-deps` resolves an ext_resource against. Then +155 for the Teyvat
    # run frame's dressed bodies (`res://teyvat/creature_visuals/...`, behind
    # `-p:TeyvatFrame=true`) -- 77 kept plates and the 78 scenes that draw them
    # (the Golden Wolflord dresses a boss on one face and a regular on another,
    # and a scene fixes one scale, so that plate has two),
    # where the spike shipped one, generated from a single table by
    # `tools/gen_teyvat_creature_scenes.py` (`EB-811`) and pinned against that
    # generator in tier0/tests/test_teyvat_creature_scenes.py: the scenes are
    # committed under `pck-src/teyvat/`, so PK-SRC-UNPACKED wants their rows,
    # and their textures are Tier F -- gitignored, produced into
    # `ImageGen/images/teyvat/creature_visuals/` and copied in by the pck
    # build's Teyvat block. THERE IS NO SEPARATE TIER F SPELLING and a texture
    # row is one either way: a contract row asserts what reaches the PACK, not
    # what is committed, which is why `kokomi/summon/bake_kurage.png` and every
    # `*/model/layers/*.png` row above are already exactly this shape.
    # Asserted as a number rather than derived, so a scene that gains a texture
    # nobody added to the fixture universe fails HERE, beside the file, and not
    # only in the scene-deps gate downstream that resolves against it.
    #
    # Then +84 for the SIX dressings' complete act asset sets, FOURTEEN rows
    # each (`tools/gen_act_placeholders.py`;
    # `docs/current/operations/act-assets.md` is the shape in one table): seven
    # committed scene sources -- five `_bg_NN_a` layers, one `_fg_a` and the
    # background root -- and seven Tier F textures, six layer plates and one
    # rest-site plate. Plus +12 for the map OVERLAY, a wordmark and a vignette
    # a face, which are NOT in the generator's plan (they are optional by
    # construction -- the overlay stands down when they are absent) and are
    # pinned in tier0/tests/test_map_overlay_plan.py instead.
    #
    # FOURTEEN AND NOT EIGHTEEN, and 2026-09-17 took the four off in two
    # unrelated fixes:
    #
    #   * the three MAP plates went (-18 rows) when the map ground became the
    #     base zone's again (`Patches/ActMapBgPathPatch.cs`), [USER] having
    #     read ours as harder to follow than the base game's map; the overlay
    #     above (+12) is what dresses it now;
    #   * the rest-site SCENE went (-6 rows). We shipped one per face until a
    #     base character (the Silent) hard-crashed the game at a dressed
    #     campfire -- our `%RestSiteLighting` was an empty `Control` and the
    #     base campfire figure's Spine rig reaches into it. A face now wears
    #     the base zone's whole rest scene and only the PLATE row above is
    #     ours, swapped into that scene's `RestSiteBG` by a postfix on
    #     `ActModel.CreateRestSiteBackground`.
    #
    # The scenes that remain sit
    # under `pck-src/scenes/...` rather than a `teyvat/` namespace because
    # `ActModel`'s five asset-path properties are NON-VIRTUAL and derive
    # `res://scenes/backgrounds/<id>/...` from
    # the act id; satisfying them with our own files is what retires the
    # `get_FilePathIdentifier` alias patch. SIX faces and not two, because R273
    # dresses all three acts: act 1 as Mondstadt or Liyue, act 2 as Natlan or
    # Inazuma, act 3 as Fontaine or Sumeru -- and a face costs the same
    # fourteen files whether its base zone has a sibling or not. The
    # eighty-four rows are pinned against the generator's own plan in
    # tier0/tests/test_act_placeholder_plan.py, so neither side can move alone.
    # The last five are the motion pass's shared AnimationLibraries
    # (`teyvat/motion/<set>.tres`): 123 creature scenes load their clips from
    # five files rather than inlining the same keyframes 25 times over, and
    # `build_pck.ps1` overlays `pck-src` verbatim so a `.tres` packs and
    # contracts exactly as a `.tscn` does. The last twenty-four are motion
    # pass TWO: eighteen cut layers over six bespoke boss bodies (two or three
    # each) and the six per-body libraries that move them
    # (`teyvat/motion/bespoke/<body>.tres`). The last sixteen are the Furina
    # stage's eight GUEST bodies (tools/cut_guest_bodies.py): a committed
    # scene each and the Tier F sprite it draws, the same shape as the trio's
    # six above. The last four are the supporting pool's two guests, Lyney and
    # Escoffier, in the same shape.
    assert len(parsed.resources) == 426


def test_a_v2_contract_is_stale_by_definition():
    """A v2 contract is a hand-written assertion, not a measurement (C4)."""
    parsed = contract.parse("contract=roster-pck-v2\nsha256=" + "a" * 64 +
                            "\nresource=res://klee/ui/char_icon.png\n")
    report = Report(contract.GATE)
    contract.check_contract(parsed, report, "x")
    assert "CT-VERSION" in rules(report, ERROR)


def test_scaffolding_duplicates_and_root_files_are_rejected():
    parsed = contract.parse(
        "contract=roster-pck-v3\nsha256=" + "b" * 64 + "\n"
        "resource=res://project.godot\n"
        "resource=res://klee/ui/char_icon.png\n"
        "resource=res://klee/ui/char_icon.png\n"
        "resource=res://klee/ui/char_icon.png.import\n"
        "resource=res://klee.pck\n"
    )
    report = Report(contract.GATE)
    contract.check_contract(parsed, report, "x")
    found = rules(report, ERROR)
    assert {"CT-SCAFFOLDING", "CT-DUPLICATE", "CT-NO-NAMESPACE", "CT-SELF"} <= found
    assert "CT-UNSORTED" in rules(report)


def test_sha256_is_compared_against_the_pack_beside_it(tmp_path):
    payload = b"a real pack would be larger"
    good = stage(tmp_path / "good", with_hash(SAMPLE.read_text(encoding="utf-8"),
                                              payload), payload)
    report = contract.run(None, ROOT, package_dir=good, pck_src=PCK_SRC)
    assert "CT-SHA-MISMATCH" not in rules(report)

    bad = stage(tmp_path / "bad", SAMPLE.read_text(encoding="utf-8"), payload)
    report = contract.run(None, ROOT, package_dir=bad, pck_src=PCK_SRC)
    assert "CT-SHA-MISMATCH" in rules(report, ERROR)


# ---------------------------------------------------------------------------
# the staged package shape
# ---------------------------------------------------------------------------

def test_stray_json_in_the_package_is_a_finding(tmp_path):
    """ModManager parses EVERY *.json under mods/ as a manifest (S1's lesson)."""
    package = stage(tmp_path, SAMPLE.read_text(encoding="utf-8"))
    (package / "deps.json").write_text("{}", encoding="utf-8")
    report = Report(contract.GATE)
    contract.check_package(package, report, tmp_path)
    assert "PK-STRAY-JSON" in rules(report, ERROR)


def test_a_pck_without_its_contract_is_a_finding(tmp_path):
    package = stage(tmp_path, SAMPLE.read_text(encoding="utf-8"))
    (package / "klee.pck.contract.txt").unlink()
    report = Report(contract.GATE)
    assert contract.check_package(package, report, tmp_path) is None
    assert "PK-NO-CONTRACT" in rules(report, ERROR)


def test_an_empty_package_fails_rather_than_passing(tmp_path):
    empty = tmp_path / "stage"
    empty.mkdir()
    report = Report(contract.GATE)
    contract.check_package(empty, report, tmp_path)
    assert "PK-EMPTY" in rules(report, ERROR)


# ---------------------------------------------------------------------------
# committed scene sources vs the contract
# ---------------------------------------------------------------------------

def test_every_committed_scene_source_has_a_contract_row():
    parsed = contract.parse(SAMPLE.read_text(encoding="utf-8"))
    report = Report(contract.GATE)
    contract.check_sources(PCK_SRC, parsed, report, ROOT)
    assert report.errors == [], report.render(verbose=True)
    assert report.checked["scene_sources"] >= 8


def test_a_scene_that_did_not_reach_the_pack_is_named():
    parsed = contract.parse(
        "\n".join(
            line for line in SAMPLE.read_text(encoding="utf-8").splitlines()
            if "shared/gauge.tscn" not in line
        ) + "\n"
    )
    report = Report(contract.GATE)
    contract.check_sources(PCK_SRC, parsed, report, ROOT)
    assert "PK-SRC-UNPACKED" in rules(report, ERROR)
    assert any("shared/gauge.tscn" in f.detail for f in report.findings)


def test_end_to_end_on_a_staged_package(tmp_path):
    payload = b"pack"
    package = stage(tmp_path, with_hash(SAMPLE.read_text(encoding="utf-8"),
                                        payload), payload)
    report = contract.run(None, ROOT, package_dir=package, pck_src=PCK_SRC)
    assert report.errors == [], report.render(verbose=True)
    # +6 at EB-40, +2 for the pet, +6 for the stage, +245 for the Teyvat
    # frame's 122 dressed bodies (122 Tier F plates and the 123 scenes that
    # draw them -- 2026-09-17 closed the last 52 act-1..3 face-slots), +108 for
    # the six act dressings' placeholder asset sets, -18 for the map plates
    # they stopped overriding the ground with, +12 for the overlay that
    # replaced them and -6 for the rest-site scenes they stopped shipping (see
    # the count's reason above the first assertion), +5 for
    # the motion pass's shared AnimationLibraries, +24 for pass two (eighteen
    # cut layers over six bespoke boss bodies, and their six per-body
    # libraries), +16 for the stage's eight guest bodies (a scene and a
    # sprite each), +4 for the supporting pool's two guests.
    assert report.checked["contract_resources"] == 426
    assert report.checked["package_files"] == 3
