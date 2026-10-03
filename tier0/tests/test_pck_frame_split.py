"""The release pck carries no Teyvat-frame resource (2026-10-02).

The Teyvat run frame is off in a release build: `TeyvatFrame.DefaultEnabled`
is `#if TEYVAT_FRAME`, only `deploy_proto.ps1 -TeyvatFrame` passes it, and
every Teyvat patch, registration and music seam returns on
`!TeyvatFrame.Enabled`. Yet the release `klee.pck` shipped the whole frame --
359 MB of file data, 316 MB of it 27 music tracks that never play.

The split: `tools/build_pck.ps1` prunes the frame-only trees unless
`-TeyvatFrame`, which builds `klee-teyvat.pck` instead; `deploy_proto.ps1
-TeyvatFrame` stages that variant as `klee.pck`; `tools/deploy_round.py --arms
teyvat` passes the switch to both; validate.ps1 S2b refuses a release package
that carries a frame row. This file pins the four lists to one another and
pins the code side: a C# file outside the frame that names a frame path would
be reading a resource the release pck no longer has.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import deploy_round                              # noqa: E402
from tools import gen_act_placeholders as gen              # noqa: E402
from tools.visual_qa import contract                        # noqa: E402
from tools.visual_qa.findings import Report                 # noqa: E402

BUILD_PCK = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")
VALIDATE = (ROOT / "klee-mod" / "build" / "validate.ps1").read_text(
    encoding="utf-8")
DEPLOY_PROTO = (ROOT / "klee-mod" / "build" / "deploy_proto.ps1").read_text(
    encoding="utf-8")
KLEECODE = ROOT / "klee-mod" / "KleeCode"
PCK_SRC = ROOT / "klee-mod" / "pck-src"
RELEASE_CONTRACT = ROOT / "klee-mod" / "assets" / "klee.pck.contract.txt"

#: C# outside KleeCode/Teyvat/ that may NAME a frame path, each because it
#: gates every use on `TeyvatFrame.Enabled` (read the cited line).
GATED_FRAME_READERS = {
    # CoversDressedBody(TeyvatFrame.Enabled, ...) -- ModdedPlayerDeathSeam.cs
    "Vfx/ModdedPlayerDeathSeam.cs",
    # Covers(TeyvatFrame.Enabled, DressedVisualsScene(entity)) -- IdleDesync.cs
    "Vfx/IdleDesync.cs",
}


def _ps_list(text: str, anchor: str) -> list[str]:
    start = text.index(anchor)
    line = text[start:text.index("\n", start)]
    return re.findall(r"'([a-z]+)'", line)


def test_the_four_dressing_lists_agree():
    build = _ps_list(BUILD_PCK, "$teyvatDressings = @(")
    validate = _ps_list(VALIDATE, "$frameOnlyRes = @(")
    assert tuple(build) == contract.TEYVAT_DRESSINGS
    assert tuple(validate) == contract.TEYVAT_DRESSINGS
    assert {n.id for n in gen.NATIONS} == set(contract.TEYVAT_DRESSINGS)


def test_build_pck_prunes_the_frame_after_the_overlay_and_before_import():
    overlay = BUILD_PCK.index('Write-Host "Overlaid pck-src scene sources."')
    prune = BUILD_PCK.index("$frameOnly = @('teyvat') + @($teyvatDressings")
    guard = BUILD_PCK.index("if (-not $TeyvatFrame) {", prune)
    removal = BUILD_PCK.index("Remove-Item $p -Recurse -Force", guard)
    importing = BUILD_PCK.index("--headless --path $work --import")
    assert overlay < prune < guard < removal < importing
    assert '"scenes\\backgrounds\\$_"' in BUILD_PCK
    # And the build refuses its own output if a frame row survived.
    assert "frame-only resource(s)" in BUILD_PCK


def test_build_pck_writes_the_two_variants_to_two_paths():
    assert "[switch]$TeyvatFrame" in BUILD_PCK
    assert "'klee-mod\\assets\\klee-teyvat.pck'" in BUILD_PCK
    assert "'klee-mod\\assets\\klee.pck'" in BUILD_PCK
    # Separate work dirs, so the variants never share an import cache.
    assert "'klee-mod\\dist\\pck-work-teyvat'" in BUILD_PCK


def test_validate_s2b_refuses_frame_rows_in_a_release_package():
    block = VALIDATE[VALIDATE.index("# S2b"):]
    block = block[:block.index("# S3.")]
    assert "if (-not $PrototypeBuild)" in block
    assert "'res://teyvat/'" in block
    assert '"res://scenes/backgrounds/$_/"' in block
    assert "Fail 'S2b'" in block


def test_the_frame_arm_stages_the_frame_variant_as_klee_pck():
    assert "'assets\\klee-teyvat.pck'" in DEPLOY_PROTO
    assert "(Join-Path $stage 'klee.pck')" in DEPLOY_PROTO
    assert "(Join-Path $stage 'klee.pck.contract.txt')" in DEPLOY_PROTO


def test_deploy_round_builds_and_checks_the_variant_its_arms_need():
    assert deploy_round.pck_for([]) == deploy_round.PCK
    assert deploy_round.pck_for(["teyvat"]) == deploy_round.FRAME_PCK

    class Args:
        pck = True
        arms: list = []

    build = [c for c in deploy_round.plan(Args()) if "tools\\build_pck.ps1" in c]
    assert build and "-TeyvatFrame" not in build[0]
    Args.arms = ["teyvat"]
    build = [c for c in deploy_round.plan(Args()) if "tools\\build_pck.ps1" in c]
    assert build and build[0][-1] == "-TeyvatFrame"


def test_no_release_code_names_a_frame_resource():
    """A frame path named outside the frame would load nothing in release."""
    pattern = re.compile(
        r'"(?:res://)?(?:teyvat/|scenes/backgrounds/(?:'
        + "|".join(contract.TEYVAT_DRESSINGS) + r")/)")
    offenders = []
    for path in KLEECODE.rglob("*.cs"):
        rel = path.relative_to(KLEECODE).as_posix()
        if rel.startswith("Teyvat/") or rel in GATED_FRAME_READERS:
            continue
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(rel)
    assert offenders == [], offenders
    for rel in GATED_FRAME_READERS:
        assert "TeyvatFrame.Enabled" in (KLEECODE / rel).read_text(
            encoding="utf-8"), rel


def test_no_release_scene_source_references_a_frame_resource():
    """A release scene drawing a pruned texture would fail the export."""
    for path in PCK_SRC.rglob("*"):
        if not path.is_file() or path.suffix not in (".tscn", ".tres"):
            continue
        rel = path.relative_to(PCK_SRC).as_posix()
        if contract.is_frame_only(rel):
            continue
        text = path.read_text(encoding="utf-8")
        assert not any(f"res://{p}" in text
                       for p in contract.FRAME_ONLY_PREFIXES), rel


def test_a_release_contract_does_not_owe_the_frame_sources(tmp_path):
    sample = (ROOT / "tools" / "visual_qa" / "fixtures" /
              "sample.contract.txt").read_text(encoding="utf-8")
    release = "\n".join(
        line for line in sample.splitlines()
        if not contract.is_frame_only(line.removeprefix("resource=res://"))
    ) + "\n"
    report = Report(contract.GATE)
    contract.check_sources(PCK_SRC, contract.parse(release), report, ROOT)
    assert report.errors == [], report.render(verbose=True)


@pytest.mark.skipif(not RELEASE_CONTRACT.exists(),
                    reason="no locally built release pck (gitignored)")
def test_the_built_release_pck_has_no_frame_rows():
    rows = [line.removeprefix("resource=res://")
            for line in RELEASE_CONTRACT.read_text(encoding="utf-8").splitlines()
            if line.startswith("resource=res://")]
    leaked = [r for r in rows if contract.is_frame_only(r)]
    assert leaked == [], (f"{len(leaked)} frame rows in the release pck, e.g. "
                          f"{leaked[:3]}; rebuild with tools/build_pck.ps1")
