"""Embark prints each mod patch class the lane's log says did not arm.

The 2026-10-23 element-token patch (LocManager.SmartFormat) never armed; the
log said so at boot and nothing read it, so every token face printed raw.
"""
from understudy.embark import unarmed_patches


def test_reads_failed_patch_lines(tmp_path):
    log = tmp_path / "godot.log"
    log.write_text(
        "[INFO] [klee] harmony: 164 patch class(es) armed.\n"
        "[ERROR] [klee] HARMONY BOOTSTRAP: 1 PATCH CLASS(ES) DID NOT ARM\n"
        "[ERROR] [klee]   FAILED  OverriddenElementFace_Format_Patch "
        "(target: LocManager.SmartFormat): HarmonyException\n",
        encoding="utf-8")
    found = unarmed_patches(log)
    assert len(found) == 1
    assert found[0].startswith("OverriddenElementFace_Format_Patch")


def test_clean_or_missing_log_reports_nothing(tmp_path):
    log = tmp_path / "godot.log"
    log.write_text("[INFO] [klee] harmony: 165 patch class(es) armed.\n",
                   encoding="utf-8")
    assert unarmed_patches(log) == []
    assert unarmed_patches(tmp_path / "absent.log") == []
