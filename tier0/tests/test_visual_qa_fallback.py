"""Gate 3: cross-character fallbacks and skipped copy blocks are a ledger.

build_pck.ps1 PRINTS both facts and gates neither. The comment at
tools/build_pck.ps1:196-201 records what that costs: a `-Exclude` bug dropped
both Furina and Kokomi back onto Klee's art, every gate stayed green, and it
was "caught only because the fallback lines are printed".
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.visual_qa import fallback                        # noqa: E402
from tools.visual_qa.findings import ERROR                  # noqa: E402

FIXTURES = ROOT / "tools" / "visual_qa" / "fixtures"
DIRTY = FIXTURES / "build_dirty.log"
CLEAN = FIXTURES / "build_clean.log"
POLICY = FIXTURES / "fallback_policy.sample.yaml"


def rules(report, severity=None):
    return {
        f.rule for f in report.findings
        if severity is None or f.severity == severity
    }


def test_the_build_lines_are_parsed_exactly_as_build_pck_prints_them():
    fallbacks, skips = fallback.parse_log(
        DIRTY.read_text(encoding="utf-8"))
    assert [(f.into, f.resource, f.source) for f in fallbacks] == [
        ("Furina", "ui/transition_wipe.png", "Klee"),
        ("Furina", "model/combat_model.png", "Klee"),
        ("Kokomi", "ui/select_bg.png", "Klee"),
    ]
    # The end-of-build summary block repeats the skips in a DIFFERENT shape
    # ("  kokomi\\summon (no source at ...)"). Counting those again would
    # double every skip; the parser keys on the "SKIPPED: " line only.
    assert [s.what for s in skips] == ["kokomi/summon", "furina/salon"]


def test_backslash_and_forward_slash_are_one_key():
    """build_pck.ps1 prints Windows separators; policies get written either way."""
    log = (
        "Stamped build id x\n"
        "Furina fallback: ui\\char_icon.png <- Klee\n"
    )
    policy = {"allowed_fallbacks": [
        {"into": "furina", "resource": "ui/char_icon.png",
         "from": "klee", "reason": "same key"}]}
    report = fallback.check(log, policy)
    assert report.errors == [], report.render(verbose=True)


def test_an_undeclared_fallback_is_the_finding():
    report = fallback.run(DIRTY, None, ROOT)
    undeclared = [f for f in report.findings if f.rule == "FB-UNDECLARED"]
    assert len(undeclared) == 3, report.render(verbose=True)
    assert "SK-UNDECLARED" in rules(report, ERROR)


def test_a_matching_policy_clears_the_gate():
    report = fallback.run(DIRTY, POLICY, ROOT)
    assert report.errors == [], report.render(verbose=True)
    assert report.checked["fallbacks"] == 3
    assert report.checked["skips"] == 2


def test_the_allowlist_fails_in_both_directions():
    """A stale exemption is how the NEXT missing asset gets waved through."""
    policy = fallback.load_policy(POLICY)
    policy["allowed_fallbacks"].append(
        {"into": "Kokomi", "resource": "ui/map_marker.png",
         "from": "Klee", "reason": "no longer happens"})
    policy["allowed_skips"].append({"what": "klee/relics", "reason": "gone"})
    report = fallback.check(DIRTY.read_text(encoding="utf-8"), policy)
    assert "FB-STALE" in rules(report, ERROR)
    assert "SK-STALE" in rules(report, ERROR)


def test_a_policy_row_without_a_reason_is_a_warning():
    policy = {"allowed_fallbacks": [
        {"into": "Furina", "resource": "ui/transition_wipe.png", "from": "Klee"}]}
    log = "Stamped build id x\nFurina fallback: ui\\transition_wipe.png <- Klee\n"
    report = fallback.check(log, policy)
    assert "FB-NO-REASON" in rules(report)
    assert report.errors == []


def test_a_log_that_never_reached_the_fallback_blocks_cannot_read_clean():
    """The false clean this gate exists to prevent."""
    report = fallback.check("Importing assets (MegaDot headless)...\n", {})
    assert "FB-NOT-A-BUILD-LOG" in rules(report, ERROR)


def test_a_clean_build_log_has_nothing_to_declare():
    report = fallback.run(CLEAN, POLICY, ROOT)
    # The sample policy declares three fallbacks the clean log does not have,
    # so it must go STALE rather than pass -- both directions, always.
    assert "FB-STALE" in rules(report, ERROR)
    empty = fallback.run(CLEAN, None, ROOT)
    assert empty.errors == [], empty.render(verbose=True)
    assert empty.checked["fallbacks"] == 0
