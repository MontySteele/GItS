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


def test_strict_promotes_warnings():
    """The live scenes carry cosmetic load_steps warnings and no errors."""
    assert run("scene-deps").returncode == 0
    assert run("--strict", "scene-deps").returncode == 1


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
