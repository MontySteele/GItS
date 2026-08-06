"""The generated current-law digest is current, complete, and honest.

Track R-D (Clear the Stage, 2026-08-06). Three facts pinned:

1. `--check` is green — the block in `tier0/DECISIONS.md` matches a fresh
   render (this is also a CI step; here it runs with the rest of the suite).
2. The sidecar covers exactly R39–R120, one row each — the volumization's
   stated range, no invented pre-R39 entries, no gaps.
3. UNREVIEWED rows render AS unreviewed: the digest must not pretend the
   [USER] red-pen pass happened (it has not; queue s.4 row).
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


def test_unreviewed_rows_say_so_in_the_rendered_block():
    mod = _module()
    block = mod.render()
    rows = mod._sidecar()
    unreviewed = sum(1 for s in rows.values() if s == "UNREVIEWED")
    # The honesty contract: every UNREVIEWED sidecar row is an UNREVIEWED
    # digest line, and the header states the count rather than hiding it.
    assert block.count("`UNREVIEWED`") == unreviewed
    assert f"{unreviewed} UNREVIEWED" in block


def test_a_missing_marker_pair_is_loud_not_silent():
    mod = _module()
    with pytest.raises(SystemExit):
        mod._splice("a ledger with no digest markers", "block")
