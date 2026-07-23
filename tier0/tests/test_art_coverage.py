"""Card-art coverage gate (tools/art_coverage.py).

Companion module to test_sheet_lints: that one sweeps the sheets for design
defects, this one checks the sheets against what art actually exists on disk.

Deliberately does NOT assert a missing-count. Missing is 101 today and walks
to 0 as the Furina art pass lands; pinning it would make every promoted
portrait a test edit. What IS pinned is the pair of invariants that can
silently rot: stale files must never read as coverage, and a portrait that
already exists must never be re-billed as missing.
"""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]
TOOL = REPO / "tools" / "art_coverage.py"
COMPANION_ART = REPO / "ImageGen" / "images" / "cards" / "companions"


def run_tool(*args):
    return subprocess.run([sys.executable, str(TOOL), *args],
                          capture_output=True, text=True)


def test_no_unrecorded_stale_art():
    """Exit 0 means every file on disk maps to a sheet row or a KNOWN_STALE reason.

    Fires when a portrait is promoted under a card id that no longer exists --
    a renamed card leaves its old png behind, and a coverage report that
    counted it would show the pass finishing while the new id is unpainted.
    """
    res = run_tool()
    assert res.returncode == 0, res.stdout + res.stderr


def test_stale_file_is_not_counted_as_coverage():
    """sec.11: 'Stale files are reported but never counted as coverage.'"""
    res = run_tool()
    assert "xingqiu_raincutter" in res.stdout
    assert "STALE" in res.stdout
    # It sits in the companions dir, but the covered list must not name it.
    covered_lines = [ln for ln in res.stdout.splitlines() if ln.strip().startswith("have:")]
    assert covered_lines, "report printed no covered list"
    assert not any("xingqiu" in ln for ln in covered_lines)


@pytest.mark.skipif(not (COMPANION_ART / "dahlia_sacramental_shower.png").exists(),
                    reason="Tier F art is gitignored; only meaningful on a machine that has fetched it")
def test_existing_portrait_is_not_rebilled_as_missing():
    """Regression for the requirements-doc bill (defect D1 in the tool docstring).

    docs/furina-art-pass-requirements.md sec.1/sec.7 billed
    dahlia_sacramental_shower as missing -- 'this row existed in the plan but
    never reached the final output directory'. It had. Re-fetching it would
    have overwritten an eyes-on-approved 2026-07-21 portrait, and the doc's
    22-missing-companions figure was 21.

    Run this against the doc's bill rather than the tool's and it fails; that
    is the point. The derived number belongs to the tool.

    The invariant is anchored positively -- the existing portrait shows up in
    the COVERED list -- rather than by asserting some sibling is still missing.
    The art pass has since covered every row (favonian_favor included), so a
    "this one is missing" control would rot the moment the pass finished; the
    D1 regression itself does not depend on anything remaining unpainted.
    """
    res = run_tool()
    body = res.stdout
    missing_section = body.split("MISSING (the art bill)")[1].split("STALE")[0]
    assert "dahlia_sacramental_shower" not in missing_section
    covered = "".join(ln for ln in body.splitlines() if ln.strip().startswith("have:"))
    assert "dahlia_sacramental_shower" in covered, "the existing portrait must read as covered"


def test_bill_is_derived_from_canonical_sheets():
    """Every expected id traces to a canonical sheet -- no hardcoded inventory.

    The doc's bill drifted precisely because it was transcribed prose. If this
    tool ever grows its own literal card list it inherits the same failure
    mode, so assert the totals still reconcile against the YAML.
    """
    expected = 0
    for name in ("furina-cards.yaml", "mondstadt-companions.yaml", "fontaine-companions.yaml"):
        rows = yaml.safe_load((REPO / "docs" / name).read_text(encoding="utf-8"))
        expected += sum(1 for r in rows if isinstance(r, dict) and "id" in r)
    tokens = yaml.safe_load(
        (REPO / "tier0" / "content" / "cards" / "tokens.yaml").read_text(encoding="utf-8"))
    expected += sum(1 for r in tokens if isinstance(r, dict) and r.get("rarity") == "token")

    res = run_tool()
    line = [ln for ln in res.stdout.splitlines() if "TOTAL card-sized outputs expected" in ln]
    assert line, res.stdout
    assert int(line[0].rsplit(":", 1)[1]) == expected
