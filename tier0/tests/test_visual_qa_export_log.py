"""Gate 1: the MegaDot build log is read for errors, in BOTH stages.

The defect this gate exists for is written down at tools/build_pck.ps1:770-781:
the ERROR sweep is applied to the import log only, and the export log is
checked by exit code alone. So the load-bearing assertion here is the one about
an export-stage error being FOUND -- everything else is shape.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.visual_qa import export_log                     # noqa: E402
from tools.visual_qa.findings import ERROR, WARNING        # noqa: E402

FIXTURES = ROOT / "tools" / "visual_qa" / "fixtures"


def rules(report, severity=None):
    return {
        f.rule for f in report.findings
        if severity is None or f.severity == severity
    }


def test_clean_log_passes_and_says_what_it_checked():
    report = export_log.run(FIXTURES / "build_clean.log", ROOT)
    assert report.errors == [], report.render(verbose=True)
    assert not report.failed()
    # The gate must report its own reach: a run that says "0 lines, OK" is
    # telling you it did nothing.
    assert report.checked["log_lines"] > 0
    assert report.checked["godot_errors"] == 0


def test_export_stage_error_is_found_and_attributed():
    """build_pck.ps1 greps only the IMPORT log. This is the half it misses."""
    report = export_log.run(FIXTURES / "build_dirty.log", ROOT)
    export_errors = [
        f for f in report.findings
        if f.severity == ERROR and "[export stage]" in f.detail
    ]
    assert export_errors, report.render(verbose=True)
    assert any("Failed to save pack file" in f.detail for f in export_errors)
    # And the import-stage error is still attributed to the import stage.
    assert any(
        "[import stage]" in f.detail and "Error importing" in f.detail
        for f in report.findings
    )


def test_dependency_failure_without_an_error_prefix_is_caught():
    """Godot writes 'Unrecognized dependency:' with no ERROR: prefix.

    An exit-code check misses it and a grep for 'ERROR' misses it, which is
    the whole reason the soft-failure list exists.
    """
    report = export_log.run(FIXTURES / "build_dirty.log", ROOT)
    assert "XL-DEPENDENCY" in rules(report, ERROR)
    assert any(
        "furina_combat_hat.png" in f.detail
        for f in report.findings if f.rule == "XL-DEPENDENCY"
    )


def test_warnings_are_warnings_not_errors():
    report = export_log.run(FIXTURES / "build_dirty.log", ROOT)
    assert "XL-WARNING" in rules(report, WARNING)
    assert "XL-WARNING" not in rules(report, ERROR)
    # ...and --strict promotes them.
    clean = export_log.scan(
        "Importing assets (MegaDot headless)...\n"
        "WARNING: something cosmetic\n"
        "Exporting pack...\n"
        "Built x (1 bytes; contract roster-pck-v3, 1 resources)\n"
    )
    assert not clean.failed(strict=False)
    assert clean.failed(strict=True)


def test_a_filename_containing_error_is_not_an_error():
    """PowerShell's Select-String 'ERROR' is case-insensitive and unanchored."""
    report = export_log.scan(
        "Importing assets (MegaDot headless)...\n"
        "Import: begin: Importing file: res://klee/ui/error_icon.png\n"
        "Exporting pack...\n"
        "Built x (1 bytes; contract roster-pck-v3, 1 resources)\n"
    )
    assert report.errors == [], report.render(verbose=True)


def test_truncated_log_fails_rather_than_reading_clean():
    """An empty sweep is the failure mode, not a pass (validate.ps1 S8's lesson)."""
    truncated = export_log.scan("Importing assets (MegaDot headless)...\n")
    assert "XL-STAGE-MISSING" in rules(truncated, ERROR)
    assert "XL-INCOMPLETE" in rules(truncated, ERROR)

    empty = export_log.scan("")
    assert "XL-EMPTY" in rules(empty, ERROR)


def test_missing_log_file_is_a_finding_not_a_crash():
    report = export_log.run(ROOT / "no" / "such" / "build.log", ROOT)
    assert "XL-NO-LOG" in rules(report, ERROR)


def test_gate_never_shells_out_to_the_editor():
    """The game is single-install and [USER] is playing on it.

    The module must contain no process launch at all -- this gate reads a
    captured log and nothing else.
    """
    source = (ROOT / "tools" / "visual_qa" / "export_log.py").read_text(
        encoding="utf-8")
    for forbidden in ("subprocess", "os.system", "Popen"):
        assert forbidden not in source, forbidden
