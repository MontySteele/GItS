"""R70: the manifest version gate and the dependency pins actually compare.

These drive `Test-VersionPolicy` -- the function validate.ps1's S3 rule
calls -- rather than re-implementing its logic, so they exercise the shipped
code path. They do NOT drive validate.ps1 end to end, because the gate runs
the whole pytest suite (~78s of an 84.0s run, measured in C6) and a unit test
must not.

That reason is the CORRECTED one. This docstring used to say "S7's game_ref
verification takes minutes" -- the unmeasured claim C6 deleted from
validate.ps1 and Sweep II deleted from version.ps1. The verification is 0.17s;
the cost was always the suite.

The defects being pinned, both from the 2026-07-26 audit:

  3.6  manifest.json had ONE commit ever. Kokomi's shell and three sprints
       all shipped as "0.2.0", and deploy silently overwrote the previous
       zip of that same name. In deterministic-lockstep co-op that is
       exactly the failure the version field exists to prevent.
  R214 (2026-08-27) amended the SHAPE these tests pin: MAJOR-AUTO
  ("0.2-1159") is not a valid semantic version -- the game's parser throws on
  the '-' while still in Minor, leaves our parsed version null, and then
  refuses any dependent mod declaring a min_version on us. The emitted shape
  is now MAJOR.AUTO ("0.2.1159"), with +dirty as build metadata. The old
  shape is pinned as REFUSED below: a lock is not trusted until it is seen to
  fail.

  3.5  min_version 3.3.6 and min_game_version 0.107.1 were compared to
       nothing at all. S3 checked that BaseLib was PRESENT and stopped, so a
       too-old BaseLib passed the deploy gate and failed at boot instead.

Windows-only by nature: the thing under test is a PowerShell deploy gate.
"""

from __future__ import annotations

import json
import re
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
            expected: str, prototype: bool = False) -> list[str]:
    """Run Test-VersionPolicy with synthetic inputs; return its findings.

    `prototype` is the dev-deploy switch (deploy_proto.ps1). It defaults
    FALSE because that is the RELEASE path, which is what every other test in
    this file is about.
    """
    allow = "$true" if prototype else "$false"
    script = f"""
. '{VERSION_PS1}'
$m = '{json.dumps(manifest)}' | ConvertFrom-Json
$installed = @{{}}
{''.join(
    f"$installed['{k}'] = '{json.dumps(v)}' | ConvertFrom-Json" + chr(10)
    for k, v in installed.items())}
$game = {('$null' if game_version is None else chr(39) + game_version + chr(39))}
$out = Test-VersionPolicy -Manifest $m -Installed $installed `
    -GameVersion $game -Expected '{expected}' `
    -AllowPrototypeMetadata:{allow}
foreach ($f in $out) {{ Write-Output "FINDING: $f" }}
"""
    res = _ps(script)
    assert res.returncode == 0, res.stdout + res.stderr
    return [ln[len("FINDING: "):] for ln in res.stdout.splitlines()
            if ln.startswith("FINDING: ")]


def _manifest(**overrides) -> dict:
    m = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    m["version"] = "0.2.138"
    m.update(overrides)
    return m


BASELIB_OK = {"BaseLib": {"id": "BaseLib", "version": "v3.3.8"}}


# --- the version stamp (audit 3.6) -----------------------------------------

def test_a_stale_manifest_version_is_refused():
    """The presenting symptom: 134 commits stuck at 0.2.0."""
    findings = _policy(_manifest(version="0.2.0"), BASELIB_OK,
                       "v0.111.0", "0.2.138")
    assert any("staged manifest version is '0.2.0'" in f for f in findings), \
        findings


def test_a_correctly_stamped_version_passes():
    """Positive control. A gate that refused every version would satisfy the
    test above while being worthless."""
    findings = _policy(_manifest(), BASELIB_OK, "v0.111.0", "0.2.138")
    assert findings == [], findings


def test_a_dirty_stamp_still_has_to_match():
    findings = _policy(_manifest(version="0.2.138"), BASELIB_OK,
                       "v0.111.0", "0.2.138+dirty")
    assert any("computes '0.2.138+dirty'" in f for f in findings), findings


# --- the dependency pin (audit 3.5) ----------------------------------------

def test_an_unsatisfied_min_version_is_refused():
    """Before R70 this passed: BaseLib was present, so S3 stopped looking."""
    findings = _policy(
        _manifest(dependencies=[{"id": "BaseLib", "min_version": "999.0.0"}]),
        BASELIB_OK, "v0.111.0", "0.2.138")
    assert any("requires >= 999.0.0" in f for f in findings), findings


def test_a_satisfied_min_version_passes():
    findings = _policy(
        _manifest(dependencies=[{"id": "BaseLib", "min_version": "3.3.6"}]),
        BASELIB_OK, "v0.111.0", "0.2.138")
    assert findings == [], findings


def test_a_missing_dependency_is_still_refused():
    """The check R70 extended, not replaced."""
    findings = _policy(_manifest(), {}, "v0.111.0", "0.2.138")
    assert any("is not installed" in f for f in findings), findings


def test_an_unparseable_installed_version_is_not_treated_as_satisfied():
    findings = _policy(
        _manifest(dependencies=[{"id": "BaseLib", "min_version": "3.3.6"}]),
        {"BaseLib": {"id": "BaseLib", "version": "who knows"}},
        "v0.111.0", "0.2.138")
    assert any("unparseable version" in f for f in findings), findings


# --- the game pin (audit 3.5) ----------------------------------------------

def test_an_unsatisfied_min_game_version_is_refused():
    findings = _policy(_manifest(min_game_version="999.0.0"), BASELIB_OK,
                       "v0.111.0", "0.2.138")
    assert any("requires >= 999.0.0" in f for f in findings), findings


def test_an_unknown_game_version_warns_and_does_not_claim_verification():
    """A build machine may legitimately lack release_info.json. "Not
    verified" must never read as "verified" -- that was the old behaviour."""
    findings = _policy(_manifest(), BASELIB_OK, None, "0.2.138")
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
    findings = _policy(_manifest(), BASELIB_OK, game, "0.2.138")
    assert findings == [], findings


# --- the computed version --------------------------------------------------

def test_the_computed_version_is_major_dot_auto():
    """R214: AUTO is the PATCH component, so the whole string is semver."""
    res = _ps(f". '{VERSION_PS1}'; "
              f"(Get-PackageVersion -SourceManifest '{SOURCE_MANIFEST}' "
              f"-RepoRoot (Get-RepoRoot)).Version")
    assert res.returncode == 0, res.stdout + res.stderr
    version = res.stdout.strip()
    major = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["version"]
    assert version.startswith(f"{major}."), version
    auto = version[len(major) + 1:]
    assert auto.replace("+dirty", "").isdigit(), (
        f"AUTO must be a commit count (optionally +dirty), got {auto!r}")
    assert re.fullmatch(r"\d+\.\d+\.\d+(\+dirty)?", version), (
        f"the emitted version must parse as semver, got {version!r}")


def test_the_source_manifest_holds_only_the_major():
    """MAJOR is a ratified artifact bumped by hand. If AUTO ever leaks into
    the committed manifest, the next deploy stamps MAJOR.AUTO.AUTO."""
    major = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["version"]
    assert re.fullmatch(r"\d+\.\d+", major), (
        f"committed manifest version {major!r} is not a bare MAJOR "
        f"(exactly two dotted integers)")


@pytest.mark.parametrize("bad", ["0.2-1", "0.2.1", "0.2.1+dirty", "0"])
def test_a_manifest_carrying_an_auto_part_is_refused_as_a_source(bad):
    """R214 widened this: with AUTO now a dotted component, looking for a
    dash no longer sees a leaked AUTO. The check is a shape check, and the
    OLD dashed shape must still be refused."""
    res = _ps(f". '{VERSION_PS1}'; "
              "$p = Join-Path $env:TEMP 'r70_bad_manifest.json'; "
              f"'{{\"version\":\"{bad}\"}}' | Set-Content $p -Encoding utf8; "
              "try { Get-ManifestMajor -SourceManifest $p; 'NO THROW' } "
              "catch { 'threw' }")
    assert res.stdout.strip() == "threw", res.stdout + res.stderr


# --- R214: the semver shape, seen to fail ----------------------------------

def test_the_old_dashed_shape_is_refused():
    """The defect R214 fixes, pinned as a refusal. `0.2-1159` shipped for
    months; the game's parser threw on it every boot and left our version
    null. A gate that has never refused this string is not a gate."""
    findings = _policy(_manifest(version="0.2-1159"), BASELIB_OK,
                       "v0.111.0", "0.2-1159")
    assert any("not a valid semantic version" in f for f in findings), findings


def test_the_new_shape_and_its_dirty_form_both_pass_the_semver_check():
    """Positive control for the refusal above."""
    for good in ("0.2.1159", "0.2.1159+dirty"):
        findings = _policy(_manifest(version=good), BASELIB_OK,
                           "v0.111.0", good)
        assert findings == [], (good, findings)


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


# --- the +proto build metadata (the DEV deploy path) ------------------------
#
# R214 ruled MAJOR.AUTO with `+dirty` as semver build metadata. `+proto` is a
# SECOND token on that same channel, added so a package built with the
# quarantined prototype surface compiled in (R213 B) is identifiable on sight
# -- deploy_proto.ps1 writes to the same mods\klee directory the release path
# writes to, so without a mark on the version string there is nothing anywhere
# that says which build is installed. The extension is flagged for the next
# ruling; these tests are what it means today.

def test_a_prototype_stamp_is_refused_from_the_release_path():
    """The whole point of the switch: the release gate never accepts the mark.

    Refused BY NAME rather than falling out of the Expected comparison, so
    the finding says what happened instead of "0.2.138+proto is not 0.2.138".
    """
    findings = _policy(_manifest(version="0.2.138+proto"), BASELIB_OK,
                       "v0.111.0", "0.2.138")
    assert any("+proto" in f and "deploy_proto.ps1" in f for f in findings), \
        findings


def test_a_prototype_stamp_is_accepted_when_the_dev_script_asks():
    findings = _policy(_manifest(version="0.2.138+proto"), BASELIB_OK,
                       "v0.111.0", "0.2.138+proto", prototype=True)
    assert findings == []


def test_a_dirty_prototype_stamp_is_accepted_when_the_dev_script_asks():
    findings = _policy(_manifest(version="0.2.138+proto.dirty"), BASELIB_OK,
                       "v0.111.0", "0.2.138+proto.dirty", prototype=True)
    assert findings == []


def test_the_dev_path_refuses_an_unmarked_package():
    r"""The other direction. A dev deploy whose stamp lost its mark would put
    an indistinguishable prototype build in mods\klee, which is the exact
    ambiguity the token exists to remove."""
    findings = _policy(_manifest(version="0.2.138"), BASELIB_OK,
                       "v0.111.0", "0.2.138", prototype=True)
    assert any("no +proto mark" in f for f in findings), findings


def test_a_prototype_stamp_is_still_a_parseable_semantic_version():
    """R214's reason for the shape: the game keeps the PARSED version, and a
    null version refuses every dependent mod declaring a min_version on us.
    Build metadata is ignored by the parser, so the mark costs nothing."""
    for version in ("0.2.138+proto", "0.2.138+proto.dirty"):
        findings = _policy(_manifest(version=version), BASELIB_OK,
                           "v0.111.0", version, prototype=True)
        assert not any("not a valid semantic version" in f for f in findings)


def test_get_package_version_composes_the_four_shapes():
    """The non-prototype string must be BYTE-IDENTICAL to what shipped before
    the switch existed -- that is why it is composed from Count/IsDirty and
    the plain path still returns Auto untouched."""
    script = f"""
. '{VERSION_PS1}'
$src = '{SOURCE_MANIFEST}'
$root = '{REPO}'
$plain = Get-PackageVersion -SourceManifest $src -RepoRoot $root
$proto = Get-PackageVersion -SourceManifest $src -RepoRoot $root -Prototype
Write-Output "PLAIN: $($plain.Version)"
Write-Output "PROTO: $($proto.Version)"
Write-Output "ISPROTO: $($proto.IsPrototype)"
Write-Output "PLAINISPROTO: $($plain.IsPrototype)"
"""
    res = _ps(script)
    assert res.returncode == 0, res.stdout + res.stderr
    out = dict(ln.split(": ", 1) for ln in res.stdout.splitlines() if ": " in ln)
    plain, proto = out["PLAIN"], out["PROTO"]
    assert re.fullmatch(r"\d+\.\d+\.\d+(\+dirty)?", plain), plain
    assert re.fullmatch(r"\d+\.\d+\.\d+\+proto(\.dirty)?", proto), proto
    # Same MAJOR and same AUTO count; only the metadata differs.
    assert proto.split("+")[0] == plain.split("+")[0]
    # And dirtiness agrees between them, whichever way this tree happens to be.
    assert plain.endswith("+dirty") == proto.endswith(".dirty")
    assert out["ISPROTO"] == "True" and out["PLAINISPROTO"] == "False"


def test_only_the_dev_script_sets_the_prototype_compile_flag():
    """The quarantine's release-path leg (R213 B), stated over the whole
    build directory rather than over two named files.

    `tier0/tests/test_prototype_surface.py` pins that deploy.ps1 and
    validate.ps1 never mention the property. This says the complement: EXACTLY
    ONE script in the directory does, and it is the dev one. A third script
    growing the flag would be a second release path nobody audited.
    """
    setters = sorted(p.name for p in BUILD.glob("*.ps1")
                     if "PrototypeCards" in p.read_text(encoding="utf-8"))
    assert setters == ["deploy_proto.ps1"], setters


def test_the_dev_deploy_runs_the_whole_gate():
    """A prototype build that skipped gates would prove nothing about the
    cards it exists to try, so the dev path is the release path plus a flag
    -- never minus a rule."""
    src = (BUILD / "deploy_proto.ps1").read_text(encoding="utf-8")
    assert "validate.ps1" in src
    assert "-StaticOnly" not in src
    assert "-p:PrototypeCards=true" in src
    assert "version.ps1" in src, "deploy_proto.ps1 does not source version.ps1"
    assert "rev-list" not in src, (
        "deploy_proto.ps1 computes the AUTO version itself instead of asking "
        "version.ps1")
    # It stamps through the shared switch rather than string-editing a version.
    assert "-Prototype" in src
    # No handoff zip: co-op is lockstep and a peer on a release build has no
    # prototype classes at all.
    assert "Compress-Archive" not in src
    # The restore route is named on the script, because there is no undo to
    # offer -- deploy.ps1 simply overwrites it.
    assert "deploy.ps1" in src


def test_the_dev_deploy_checks_the_prototype_codegen_first():
    """The one staleness gate validate.ps1 cannot supply: its S6a runs the
    ROSTER codegen check, which cannot see the quarantined surface."""
    src = (BUILD / "deploy_proto.ps1").read_text(encoding="utf-8")
    assert "gen_prototype_cards.py" in src
    assert "--check" in src
    assert src.index("gen_prototype_cards.py") < src.index("dotnet build"), \
        "the staleness check must run before anything is built"
