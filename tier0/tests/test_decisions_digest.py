"""The generated current-law digest is current, complete, and honest.

Track R-D (Clear the Stage, 2026-08-06). Three facts pinned:

1. `--check` is green — the block in `tier0/DECISIONS.md` matches a fresh
   render (this is also a CI step; here it runs with the rest of the suite).
2. The sidecar covers exactly R39–R120, one row each — the volumization's
   stated range, no invented pre-R39 entries, no gaps.
3. EVERY row renders as the status the sidecar gives it, and the header
   counts the categories rather than hiding them. This started life as an
   UNREVIEWED-only honesty clause -- the digest must not pretend a pass
   happened that had not. The 2026-08-06 Class-P status pass ran and left
   zero UNREVIEWED rows, so the clause is GENERALIZED rather than deleted:
   the same contract now binds every status value, and the UNREVIEWED half
   still binds the moment a new ruling lands unread. A test that only
   watched one value would have gone quiet at exactly the point the file
   started making claims.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "gen_decisions_digest.py"


def _module():
    spec = importlib.util.spec_from_file_location("gen_decisions_digest", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_check_mode_is_green():
    res = subprocess.run([sys.executable, str(TOOL), "--check"],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_sidecar_covers_exactly_the_volumized_range():
    mod = _module()
    rows = mod._sidecar()
    assert sorted(rows) == list(range(39, 121)), (
        "sidecar must hold exactly R39-R120: the volumized range plus the "
        "live file's rulings, nothing invented below R39")


def test_every_row_renders_as_the_status_the_sidecar_gives_it():
    mod = _module()
    block = mod.render()
    rows = mod._sidecar()
    seen = set(rows.values())
    assert seen, "a sidecar with no statuses renders nothing to check"
    for status in seen:
        assert block.count(f"`{status}`") == sum(1 for s in rows.values()
                                                 if s == status), (
            f"digest lines carrying `{status}` must equal the sidecar's rows "
            "with that status -- the digest renders, it never re-judges")


def test_the_header_counts_the_categories_rather_than_hiding_them():
    mod = _module()
    block = mod.render()
    rows = mod._sidecar()
    header = block.split("\n\n")[1]
    operative = sum(1 for s in rows.values() if s == "OPERATIVE")
    doubt = sum(1 for s in rows.values() if s == "DOUBT")
    unreviewed = sum(1 for s in rows.values() if s == "UNREVIEWED")
    moved = len(rows) - operative - doubt - unreviewed
    assert f"{len(rows)} rulings" in header
    assert f"{operative} OPERATIVE" in header
    assert f"{moved} moved" in header
    assert f"{doubt} DOUBT" in header
    # The original honesty clause, still binding: an unread row must be
    # visible in the headline the moment one exists.
    assert (f"{unreviewed} UNREVIEWED" in header) == bool(unreviewed)


def test_a_missing_marker_pair_is_loud_not_silent():
    mod = _module()
    with pytest.raises(SystemExit):
        mod._splice("a ledger with no digest markers", "block")
