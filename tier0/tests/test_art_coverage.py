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


# 1x1 transparent PNG. Content is irrelevant everywhere below -- coverage keys
# on the FILENAME, never on pixels (that is art_lint's job, not this tool's).
PROBE_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae"
    "426082")


def first_companion_id():
    """A real expected id from a canonical companion sheet, read not hardcoded.

    Used to seed a COVERED probe. Which row it is does not matter; that it
    comes from the sheet rather than a literal does -- a literal here would be
    the `test_bill_is_derived_from_canonical_sheets` failure mode one level up.
    """
    sys.path.insert(0, str(REPO / "tools"))
    import art_coverage

    for path, outdir, _label in art_coverage.SHEETS:
        if outdir != COMPANION_ART:
            continue
        rows = yaml.safe_load(path.read_text(encoding="utf-8"))
        for r in rows:
            if isinstance(r, dict) and "id" in r:
                return r["id"]
    raise AssertionError("no companion sheet row found to seed a covered probe")


def test_no_unrecorded_stale_art():
    """Exit 0 means every file on disk maps to a sheet row or a KNOWN_STALE reason.

    Fires when a portrait is promoted under a card id that no longer exists --
    a renamed card leaves its old png behind, and a coverage report that
    counted it would show the pass finishing while the new id is unpainted.
    """
    res = run_tool()
    assert res.returncode == 0, res.stdout + res.stderr


def test_stale_file_is_not_counted_as_coverage():
    """sec.11: 'Stale files are reported but never counted as coverage.'

    Creates its OWN stale probe instead of asserting on `xingqiu_raincutter`.
    That file is real legacy art, but it is gitignored Tier F, so the test only
    ever passed on a machine that happened to still have it -- a fresh clone
    has no ImageGen/images at all and failed here. (It was destroyed on
    2026-07-25 by a `git worktree remove` that followed a junction into the
    real directory, which is how the fragility was found; the KNOWN_STALE entry
    for it stays, because the reason it records is still true.)

    A test that depends on an artifact nothing can regenerate is a test that
    reports the machine, not the code.

    It seeds BOTH probes. The stale one is the subject; the covered one exists
    so the `have:` list is non-empty *by construction* rather than because the
    machine happens to hold art. Asserting "the covered list is non-empty and
    does not name the stale probe" against a list that is empty on a bare clone
    is a vacuous assertion wearing a real one's clothes -- which is exactly how
    this test failed on a fresh clone before (audit sec.A1). The covered probe
    is written only if that path is currently unoccupied, and removed only if
    this test wrote it: on a machine that HAS the real portrait we must not
    overwrite an eyes-on-approved file, and we do not need to.
    """
    stale = COMPANION_ART / "zz_stale_probe_not_a_card.png"
    covered = COMPANION_ART / f"{first_companion_id()}.png"
    COMPANION_ART.mkdir(parents=True, exist_ok=True)
    stale.write_bytes(PROBE_PNG)
    seeded_covered = not covered.exists()
    if seeded_covered:
        covered.write_bytes(PROBE_PNG)
    try:
        res = run_tool()
        assert stale.stem in res.stdout, res.stdout
        assert "STALE" in res.stdout
        covered_lines = [ln for ln in res.stdout.splitlines()
                         if ln.strip().startswith("have:")]
        # The positive control: coverage is being reported at all, so the
        # negative assertions below have something to be negative about.
        assert covered_lines, "report printed no covered list"
        assert any(covered.stem in ln for ln in covered_lines), \
            f"seeded {covered.stem} did not read as coverage:\n{res.stdout}"
        # Both probes sit in the same directory. Only one of them is coverage.
        assert all(stale.stem not in ln for ln in covered_lines)
        # The KNOWN_STALE legacy file, where a machine still has it, is a NOTE
        # and must not be counted either. Vacuous on a clone that lacks it --
        # deliberately so: it is a guard on the KNOWN_STALE path, not evidence.
        assert not any("xingqiu" in ln for ln in covered_lines)
    finally:
        stale.unlink(missing_ok=True)
        if seeded_covered:
            covered.unlink(missing_ok=True)


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

    The SHEET LIST comes from the tool, not from a literal here. It used to be
    hardcoded -- which was this very failure mode one level up: adding Klee,
    Kokomi and the Inazuma companions to the tool (2026-07-25) turned a green
    test red without a single number being wrong. A test that has to be edited
    whenever the thing it checks grows is a test that will eventually be
    edited without being read.
    """
    sys.path.insert(0, str(REPO / "tools"))
    import art_coverage

    expected = 0
    for path, _outdir, _label in art_coverage.SHEETS:
        rows = yaml.safe_load(path.read_text(encoding="utf-8"))
        expected += sum(1 for r in rows if isinstance(r, dict) and "id" in r)
    tokens = yaml.safe_load(
        (REPO / "tier0" / "content" / "cards" / "tokens.yaml").read_text(encoding="utf-8"))
    expected += sum(1 for r in tokens if isinstance(r, dict) and r.get("rarity") == "token")

    res = run_tool()
    line = [ln for ln in res.stdout.splitlines() if "TOTAL card-sized outputs expected" in ln]
    assert line, res.stdout
    assert int(line[0].rsplit(":", 1)[1]) == expected
