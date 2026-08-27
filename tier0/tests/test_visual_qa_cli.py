"""The CLI contract: exit 1 on an error, exit 0 otherwise, same as every lint.

That contract is what lets these gates be wired into tools/run_lints.py and
klee-mod/build/validate.ps1 later without either file learning anything new.
Neither wiring is done on this branch -- both files are shared and
single-owner, and the proposed rows live in the lane handoff.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tools" / "visual_qa" / "fixtures"

# Spelled out so the probe scene below reads as lines rather than
# as one escape-laden literal.
NL = chr(10)


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "tools.visual_qa", *args],
        cwd=ROOT, capture_output=True, text=True,
        # stdin pinned to DEVNULL: these gates never read stdin, and an
        # inherited handle is not always valid under a CI or agent shell
        # (WinError 6 on Windows when the parent has no console stdin).
        stdin=subprocess.DEVNULL,
        encoding="utf-8", errors="backslashreplace",
    )


def test_scene_deps_over_the_live_tree_exits_zero():
    proc = run("scene-deps")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "scene-deps:" in proc.stdout
    assert proc.stdout.rstrip().endswith("OK")


def test_a_dirty_log_exits_one_and_names_the_gate():
    proc = run("export-log", str(FIXTURES / "build_dirty.log"))
    assert proc.returncode == 1, proc.stdout
    assert "XL-ERROR" in proc.stdout
    assert proc.stdout.rstrip().endswith("FAIL")


def test_a_clean_log_exits_zero():
    proc = run("export-log", str(FIXTURES / "build_clean.log"))
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_the_live_scenes_are_clean_even_under_strict():
    """Until 2026-08-27 two Furina scenes carried cosmetic SD-LOADSTEPS
    warnings, and this test pinned `--strict` on their presence -- so fixing
    the headers turned a green suite red. The live tree is now warning-free
    on this gate, and `--strict`'s own behaviour is pinned on a fixture
    below instead of on whatever debt the tree happens to hold."""
    clean = run("scene-deps")
    strict = run("--strict", "scene-deps")
    assert clean.returncode == 0, clean.stdout + clean.stderr
    assert strict.returncode == 0, strict.stdout + strict.stderr
    assert "SD-LOADSTEPS" not in strict.stdout


def test_strict_promotes_warnings(tmp_path):
    """A warning is exit 0 normally and exit 1 under `--strict`. The probe is
    a scene with one sub-resource and a deliberately wrong load_steps -- the
    cheapest SD-LOADSTEPS there is, and no error alongside it."""
    src = tmp_path / "pck-src" / "probe"
    src.mkdir(parents=True)
    (src / "probe.tscn").write_text(
        "[gd_scene load_steps=9 format=3]" + NL
        + NL
        + '[sub_resource type="Gradient" id="Gradient_probe"]' + NL
        + "offsets = PackedFloat32Array(0, 1)" + NL
        + NL
        + '[node name="Probe" type="Node2D"]' + NL,
        encoding="utf-8")

    args = ("scene-deps", "--pck-src", str(src.parent), "--no-csharp")
    lax = run(*args)
    strict = run("--strict", *args)
    assert lax.returncode == 0, lax.stdout + lax.stderr
    assert strict.returncode == 1, strict.stdout + strict.stderr
    assert "SD-LOADSTEPS" in strict.stdout


def test_verbose_shows_what_the_gate_did_not_check():
    quiet = run("scene-deps")
    loud = run("--verbose", "scene-deps")
    assert "SD-NO-UNIVERSE" not in quiet.stdout
    assert "SD-NO-UNIVERSE" in loud.stdout


def test_contact_sheet_subcommand_writes_a_sheet(tmp_path):
    sys.path.insert(0, str(ROOT))
    from tools.visual_qa.fixtures.make_capture_fixtures import write_fixtures

    captures = tmp_path / "captures"
    write_fixtures(captures)
    out = tmp_path / "sheet.png"
    proc = run("--verbose", "contact-sheet", str(captures), "--out", str(out))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert out.is_file()
    assert "png_sha256=" in proc.stdout
