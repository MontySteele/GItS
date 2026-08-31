"""EB-154: a dropped dependency fails the build.

The row's acceptance, driven against FIXTURE logs -- the sweep is exercised,
never a real `build_pck.ps1` run, which needs MegaDot, the Tier F art tree and
several minutes. The fixtures below are the shapes Godot actually emits; two
of them are the exact lines the old `Select-String 'ERROR'` could not see.

The second half of the file pins the CALL SITE, because a correct sweep that
one of the two logs never reaches is the defect this row is about.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools import godot_log_sweep as sweep   # noqa: E402

BUILD_PCK = (REPO / "tools" / "build_pck.ps1").read_text(encoding="utf-8")

CLEAN = """Godot Engine v4.5.1.stable.mono - https://godotengine.org
Importing file: res://klee/powers/spark.png
Editor folder: C:/Users/x/pck-work/.godot
WARNING: Property 'error_reporting' is deprecated.
 at: _get_property (scene/main/node.cpp:1234)
Saving file: res://klee/error_icons/warning.png
0 errors, 0 warnings
"""


# --------------------------------------------------- the under-match half --

@pytest.mark.parametrize("line,rule", [
    ("Unrecognized dependency: res://klee/powers/aura_pyro.png",
     "dropped-dependency"),
    ("Failed loading resource: res://furina/salon/member_usher.png.",
     "load-failure"),
    ("Cannot open file 'res://kokomi/powers/bake_kurage.png'.",
     "open-failure"),
    ("No loader found for resource: res://klee/build_id.tres",
     "no-loader"),
    ("Error importing 'res://klee/powers/bomb.png'.", "import-failure"),
])
def test_the_failures_with_no_ERROR_prefix_are_caught(line, rule):
    """The whole row. Godot reports a dropped dependency with none of these
    lines carrying `ERROR:`, so the old sweep matched not one of them."""
    out = sweep.findings(CLEAN + line + "\n")

    assert len(out) == 1, out
    assert rule in out[0]
    assert line in out[0]


def test_a_dropped_dependency_fails_the_sweep_end_to_end(tmp_path):
    """The acceptance clause, through the CLI the build script calls."""
    log = tmp_path / "megadot-export.log"
    log.write_text(
        CLEAN + "Unrecognized dependency: res://furina/powers/fanfare.png\n",
        encoding="utf-8")

    assert sweep.main([str(log), "--stage", "export"]) == 1


def test_a_clean_log_passes(tmp_path):
    """The control arm: a sweep that always fired would pass every test
    above and mean nothing."""
    log = tmp_path / "megadot-import.log"
    log.write_text(CLEAN, encoding="utf-8")

    assert sweep.findings(CLEAN) == []
    assert sweep.main([str(log), "--stage", "import"]) == 0


def test_a_missing_log_is_a_failure_not_a_pass(tmp_path):
    assert sweep.main([str(tmp_path / "nope.log"), "--stage", "import"]) == 1


# ---------------------------------------------------- the over-match half --

def test_the_word_error_inside_a_line_is_not_a_finding():
    """`Select-String 'ERROR'` is unanchored AND case-insensitive: a path
    holding the word, a deprecation warning quoting it, and the summary line
    "0 errors, 0 warnings" all matched. Each of those is in CLEAN."""
    assert sweep.findings(CLEAN) == []


@pytest.mark.parametrize("line", [
    "ERROR: Condition \"!f.is_valid()\" is true.",
    "  ERROR: Cannot create file.",
    "SCRIPT ERROR: Invalid call.",
    "USER ERROR: something the tool asserted",
    "FATAL: Method/function failed.",
])
def test_an_anchored_error_prefix_still_bites(line):
    """Anchoring is not a loosening: a real Godot error at the head of a line
    is exactly what the old sweep was trying to catch."""
    assert len(sweep.findings(line)) == 1


def test_one_line_reports_once():
    """A line matching two patterns is one finding, so a count is a count of
    LINES and a reader can compare two builds' numbers."""
    assert len(sweep.findings(
        "ERROR: Failed loading resource: res://x.png")) == 1


# ------------------------------------------------------------- call site ---

def test_build_pck_sweeps_BOTH_logs():
    """The export half had no sweep at all -- exit code only."""
    assert "Assert-GodotLogClean -Log $importLog -Stage 'import'" in BUILD_PCK
    assert "Assert-GodotLogClean -Log $exportLog -Stage 'export'" in BUILD_PCK


def test_the_old_unanchored_sweep_is_gone():
    """Deleted rather than kept beside the new one: two sweeps for one
    question is one too many, and the loose one is the one that rots."""
    code = "\n".join(line for line in BUILD_PCK.splitlines()
                     if not line.lstrip().startswith("#"))
    assert "Select-String 'ERROR'" not in code


def test_the_helper_goes_through_the_repo_python_convention():
    """PS 5.1 raises NativeCommandError on native stderr even at exit 0; the
    EAP helper is the repo's answer and `test_repo_python_convention` polices
    it. Asserted here too because this call site is new."""
    helper = BUILD_PCK[BUILD_PCK.index("function Assert-GodotLogClean"):]
    helper = helper[:helper.index("\nif (-not (Test-Path $MegaDot)")]
    assert "Invoke-RepoPython" in helper
    assert "throw" in helper
