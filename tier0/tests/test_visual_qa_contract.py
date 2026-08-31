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
    # energy_orb layers it references. Asserted as a number rather than
    # derived, so a scene that gains a texture nobody added to the fixture
    # universe fails HERE, beside the file, and not only in the scene-deps
    # gate downstream that resolves against it.
    assert len(parsed.resources) == 28


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
    assert report.checked["contract_resources"] == 28   # +6 at EB-40
    assert report.checked["package_files"] == 3
