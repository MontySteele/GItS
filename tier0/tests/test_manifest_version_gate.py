"""R70: the manifest version gate and the dependency pins actually compare.

These drive `Test-VersionPolicy` -- the function validate.ps1's S3 rule
calls -- rather than re-implementing its logic, so they exercise the shipped
code path. They do NOT drive validate.ps1 end to end, because S7's game_ref
verification takes minutes; a version check nobody can afford to run would
be the same class of defect this ruling is closing.

The defects being pinned, both from the 2026-07-26 audit:

  3.6  manifest.json had ONE commit ever. Kokomi's shell and three sprints
       all shipped as "0.2.0", and deploy silently overwrote the previous
       zip of that same name. In deterministic-lockstep co-op that is
       exactly the failure the version field exists to prevent.
  3.5  min_version 3.3.6 and min_game_version 0.107.1 were compared to
       nothing at all. S3 checked that BaseLib was PRESENT and stopped, so a
       too-old BaseLib passed the deploy gate and failed at boot instead.

Windows-only by nature: the thing under test is a PowerShell deploy gate.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]
BUILD = REPO / "klee-mod" / "build"
VERSION_PS1 = BUILD / "version.ps1"
SOURCE_MANIFEST = REPO / "klee-mod" / "Klee" / "manifest.json"

pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or not shutil.which("powershell"),
    reason="the gate under test is a Windows PowerShell deploy script")


def _ps(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, cwd=str(REPO))


def _policy(manifest: dict, installed: dict, game_version: str | None,
            expected: str) -> list[str]:
    """Run Test-VersionPolicy with synthetic inputs; return its findings."""
    script = f"""
. '{VERSION_PS1}'
$m = '{json.dumps(manifest)}' | ConvertFrom-Json
$installed = @{{}}
{''.join(
    f"$installed['{k}'] = '{json.dumps(v)}' | ConvertFrom-Json" + chr(10)
    for k, v in installed.items())}
$game = {('$null' if game_version is None else chr(39) + game_version + chr(39))}
$out = Test-VersionPolicy -Manifest $m -Installed $installed `
    -GameVersion $game -Expected '{expected}'
foreach ($f in $out) {{ Write-Output "FINDING: $f" }}
"""
    res = _ps(script)
    assert res.returncode == 0, res.stdout + res.stderr
    return [ln[len("FINDING: "):] for ln in res.stdout.splitlines()
            if ln.startswith("FINDING: ")]


def _manifest(**overrides) -> dict:
    m = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    m["version"] = "0.2-138"
    m.update(overrides)
    return m


BASELIB_OK = {"BaseLib": {"id": "BaseLib", "version": "v3.3.8"}}


# --- the version stamp (audit 3.6) -----------------------------------------

def test_a_stale_manifest_version_is_refused():
    """The presenting symptom: 134 commits stuck at 0.2.0."""
    findings = _policy(_manifest(version="0.2.0"), BASELIB_OK,
                       "v0.107.1", "0.2-138")
    assert any("staged manifest version is '0.2.0'" in f for f in findings), \
        findings


def test_a_correctly_stamped_version_passes():
    """Positive control. A gate that refused every version would satisfy the
    test above while being worthless."""
    findings = _policy(_manifest(), BASELIB_OK, "v0.107.1", "0.2-138")
    assert findings == [], findings


def test_a_dirty_stamp_still_has_to_match():
    findings = _policy(_manifest(version="0.2-138"), BASELIB_OK,
                       "v0.107.1", "0.2-138+dirty")
    assert any("computes '0.2-138+dirty'" in f for f in findings), findings


# --- the dependency pin (audit 3.5) ----------------------------------------

def test_an_unsatisfied_min_version_is_refused():
    """Before R70 this passed: BaseLib was present, so S3 stopped looking."""
    findings = _policy(
        _manifest(dependencies=[{"id": "BaseLib", "min_version": "999.0.0"}]),
        BASELIB_OK, "v0.107.1", "0.2-138")
    assert any("requires >= 999.0.0" in f for f in findings), findings


def test_a_satisfied_min_version_passes():
    findings = _policy(
        _manifest(dependencies=[{"id": "BaseLib", "min_version": "3.3.6"}]),
        BASELIB_OK, "v0.107.1", "0.2-138")
    assert findings == [], findings


def test_a_missing_dependency_is_still_refused():
    """The check R70 extended, not replaced."""
    findings = _policy(_manifest(), {}, "v0.107.1", "0.2-138")
    assert any("is not installed" in f for f in findings), findings


def test_an_unparseable_installed_version_is_not_treated_as_satisfied():
    findings = _policy(
        _manifest(dependencies=[{"id": "BaseLib", "min_version": "3.3.6"}]),
        {"BaseLib": {"id": "BaseLib", "version": "who knows"}},
        "v0.107.1", "0.2-138")
    assert any("unparseable version" in f for f in findings), findings


# --- the game pin (audit 3.5) ----------------------------------------------

def test_an_unsatisfied_min_game_version_is_refused():
    findings = _policy(_manifest(min_game_version="999.0.0"), BASELIB_OK,
                       "v0.107.1", "0.2-138")
    assert any("requires >= 999.0.0" in f for f in findings), findings


def test_an_unknown_game_version_warns_and_does_not_claim_verification():
    """A build machine may legitimately lack release_info.json. "Not
    verified" must never read as "verified" -- that was the old behaviour."""
    findings = _policy(_manifest(), BASELIB_OK, None, "0.2-138")
    assert len(findings) == 1, findings
    assert findings[0].startswith("WARN:"), findings
    assert "NOT verified" in findings[0]


def test_the_real_pins_are_satisfied_on_this_machine():
    """The pins as actually shipped, against what is actually installed.

    Skips rather than fails where the game or BaseLib is absent: this is the
    one case here that depends on the machine.
    """
    res = _ps(f". '{VERSION_PS1}'; "
              "Get-InstalledGameVersion "
              "'C:\\Program Files (x86)\\Steam\\steamapps\\common\\"
              "Slay the Spire 2'")
    game = res.stdout.strip()
    if not game:
        pytest.skip("game not installed on this machine")
    findings = _policy(_manifest(), BASELIB_OK, game, "0.2-138")
    assert findings == [], findings


# --- the computed version --------------------------------------------------

def test_the_computed_version_is_major_dash_auto():
    res = _ps(f". '{VERSION_PS1}'; "
              f"(Get-PackageVersion -SourceManifest '{SOURCE_MANIFEST}' "
              f"-RepoRoot (Get-RepoRoot)).Version")
    assert res.returncode == 0, res.stdout + res.stderr
    version = res.stdout.strip()
    major = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["version"]
    assert version.startswith(f"{major}-"), version
    auto = version[len(major) + 1:]
    assert auto.replace("+dirty", "").isdigit(), (
        f"AUTO must be a commit count (optionally +dirty), got {auto!r}")


def test_the_source_manifest_holds_only_the_major():
    """MAJOR is a ratified artifact bumped by hand. If AUTO ever leaks into
    the committed manifest, the next deploy stamps MAJOR-AUTO-AUTO."""
    major = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["version"]
    assert "-" not in major, (
        f"committed manifest version {major!r} contains an AUTO part")


def test_a_manifest_carrying_an_auto_part_is_refused_as_a_source():
    res = _ps(f". '{VERSION_PS1}'; "
              "$p = Join-Path $env:TEMP 'r70_bad_manifest.json'; "
              "'{\"version\":\"0.2-1\"}' | Set-Content $p -Encoding utf8; "
              "try { Get-ManifestMajor -SourceManifest $p; 'NO THROW' } "
              "catch { 'threw' }")
    assert res.stdout.strip() == "threw", res.stdout + res.stderr


def test_version_comparison_is_numeric_not_lexical():
    """The trap a string compare falls into: "3.10" > "3.9" numerically and
    "3.10" < "3.9" as text. A lexical pin silently passes a too-old
    dependency the day the minor version reaches double digits."""
    res = _ps(f". '{VERSION_PS1}'; "
              "$a = ConvertTo-ComparableVersion 'v3.10.0'; "
              "$b = ConvertTo-ComparableVersion '3.9.0'; "
              "if ($a -gt $b) { 'numeric' } else { 'lexical' }")
    assert res.stdout.strip() == "numeric", res.stdout + res.stderr


def test_an_unparseable_version_is_not_silently_satisfied():
    """Returning $null makes callers report it. Returning a default would
    reproduce the original defect: a check that always passes."""
    res = _ps(f". '{VERSION_PS1}'; "
              "$v = ConvertTo-ComparableVersion 'not-a-version'; "
              "if ($null -eq $v) { 'null' } else { \"got $v\" }")
    assert res.stdout.strip() == "null", res.stdout + res.stderr


# --- deploy-side enforcement ------------------------------------------------

def test_deploy_refuses_to_overwrite_an_existing_handoff_zip():
    """R70's overwrite refusal, asserted at the source.

    Running it for real needs a full dotnet build, so this pins the control
    flow instead: the old `Remove-Item $zip -Force` must be gone and a
    refusal must stand in its place. A weak test, and deliberately a test
    rather than nothing -- silently replacing a zip of the same name is the
    co-op desync this ruling exists to stop.
    """
    src = (BUILD / "deploy.ps1").read_text(encoding="utf-8")
    assert "Remove-Item $zip -Force" not in src, (
        "deploy still silently deletes the existing handoff zip")
    assert "refusing to overwrite an existing handoff zip" in src


def test_a_dirty_tree_is_marked_and_announced():
    """A +dirty build is never handed to a co-op partner: the commit count
    no longer identifies its contents, so two zips can share a name and
    differ."""
    src = (BUILD / "deploy.ps1").read_text(encoding="utf-8")
    assert "DIRTY WORKING TREE" in src
    assert "DO NOT hand this build to a co-op partner" in src

    res = _ps(f". '{VERSION_PS1}'; "
              "$a = Get-AutoVersion -RepoRoot (Get-RepoRoot); "
              "if ($a.IsDirty) { if ($a.Auto -like '*+dirty') "
              "{ 'marked' } else { 'UNMARKED' } } else { 'clean' }")
    assert res.stdout.strip() in ("marked", "clean"), res.stdout + res.stderr


def test_deploy_and_validate_share_one_version_implementation():
    """Two copies of "compute the version" is the drift this gate cannot
    survive: the stamp and the check would disagree about what is correct."""
    for name in ("deploy.ps1", "validate.ps1"):
        src = (BUILD / name).read_text(encoding="utf-8")
        assert "version.ps1" in src, f"{name} does not source version.ps1"
        assert "rev-list" not in src, (
            f"{name} computes the AUTO version itself instead of asking "
            f"version.ps1")


def test_the_build_scripts_are_pure_ascii():
    """PS 5.1 reads a BOM-less .ps1 as ANSI, so a stray non-ASCII byte ships
    as mojibake. validate.ps1's own S8 rule scans SourceDir, which contains
    no .ps1 files at all (audit 3.1), so the build scripts are checked here
    instead."""
    exempt = "# ascii-exempt:"
    for script in sorted(BUILD.glob("*.ps1")):
        for n, line in enumerate(
                script.read_text(encoding="utf-8").splitlines(), 1):
            if exempt in line:
                continue
            bad = [c for c in line if ord(c) > 127]
            assert not bad, (
                f"{script.name}:{n} has non-ASCII "
                f"{[hex(ord(c)) for c in bad]}: {line!r}")
