"""The lane B seam: five fields, one adapter function, one fixture.

Lane B (`EB-148`) owns the art/provenance ledger and is being built at the same
time in its own worktree. Lane C therefore knows a ledger row ONLY through
`tools/visual_qa/ledger_adapter.py`, and this file pins what "aligning at
merge" means: change `ALIASES` (and, if the field set really grew, the
dataclass), change nothing else.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.visual_qa import contract, fallback, ledger_adapter   # noqa: E402
from tools.visual_qa.findings import ERROR                       # noqa: E402

FIXTURES = ROOT / "tools" / "visual_qa" / "fixtures"
LEDGER = FIXTURES / "ledger_rows.sample.json"
SAMPLE_CONTRACT = FIXTURES / "sample.contract.txt"


def rules(report, severity=None):
    return {
        f.rule for f in report.findings
        if severity is None or f.severity == severity
    }


def test_the_seam_is_exactly_five_fields():
    """If this list grows, lane B and lane C have to talk. That is the point."""
    fields = set(ledger_adapter.LedgerRow.__dataclass_fields__)
    assert fields == {
        "asset_id", "packed_path", "fallback_from", "rights_tier", "review_state"
    }
    assert set(ledger_adapter.ALIASES) == fields


def test_alternate_column_spellings_are_bridged_not_guessed():
    rows = ledger_adapter.load_rows(LEDGER)
    by_id = {row.asset_id: row for row in rows}
    # written as `packed`, with a res:// prefix, and read as packed_path
    assert by_id["furina_char_icon"].packed_path == "furina/ui/char_icon.png"
    assert by_id["furina_char_icon"].rights_tier == "private"
    # a row with no packed column at all keeps None; nothing is invented
    assert by_id["kokomi_pearl_relic"].packed_path is None


def test_windows_separators_and_the_res_prefix_are_normalised():
    row = ledger_adapter.row_from_mapping(
        {"id": "x", "packed": r"res://furina\ui\char_icon.png"})
    assert row.packed_path == "furina/ui/char_icon.png"


def test_a_ledger_row_pointing_at_an_unpacked_resource_is_a_finding():
    packed = contract.parse(
        SAMPLE_CONTRACT.read_text(encoding="utf-8")).resource_set
    rows = ledger_adapter.load_rows(LEDGER)
    report = ledger_adapter.check_against_contract(rows, packed, "fixture")
    # the fixture ledger is deliberately clean except for the row with no
    # packed path, which is a WARNING (unknown), never an error
    assert report.errors == [], report.render(verbose=True)
    assert report.checked["rows_without_packed_path"] == 1

    report = ledger_adapter.check_against_contract(
        rows, packed - {"shared/gauge.tscn"}, "fixture")
    assert "LG-EXPECTED-MISSING" in rules(report, ERROR)


def test_an_empty_ledger_export_fails_rather_than_passing():
    report = ledger_adapter.check_against_contract([], set(), "fixture")
    assert "LG-EMPTY" in rules(report, ERROR)


def test_a_fallback_the_ledger_does_not_record_is_a_finding():
    """The half a policy file cannot answer: does the bookkeeping KNOW?"""
    rows = ledger_adapter.load_rows(LEDGER)
    observed, _ = fallback.parse_log(
        (FIXTURES / "build_dirty.log").read_text(encoding="utf-8"))

    report = ledger_adapter.check_fallbacks(rows, observed, "fixture")
    found = rules(report, ERROR)
    # transition_wipe IS recorded (fallback_from: Klee) -> no finding for it;
    # combat_model.png has no ledger row at all;
    # kokomi/ui/select_bg.png has no ledger row at all.
    assert "LG-FALLBACK-UNKNOWN" in found
    assert not any(
        "transition_wipe" in f.detail for f in report.findings)

    wipe_only = [row for row in rows if row.asset_id == "furina_transition_wipe"]
    mismatched = [
        ledger_adapter.LedgerRow(
            asset_id=row.asset_id, packed_path=row.packed_path,
            fallback_from="Kokomi")
        for row in wipe_only
    ]
    report = ledger_adapter.check_fallbacks(
        mismatched, [o for o in observed if "transition" in o.resource], "fixture")
    assert "LG-FALLBACK-MISMATCH" in rules(report, ERROR)


def test_lane_c_does_not_import_lane_b_code():
    """Concurrent lanes: the seam is a fixture and an adapter, not an import."""
    package = ROOT / "tools" / "visual_qa"
    for path in sorted(package.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for forbidden in ("art_ledger", "provenance_ledger", "lint_art_ledger"):
            assert forbidden not in text, f"{path}: {forbidden}"
