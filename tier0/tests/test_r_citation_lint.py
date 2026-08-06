"""The attribution lint runs green, AND it can still see the bug it was built for.

A lint asserted only in the green direction is a lint that can rot into a
no-op -- change one regex and it passes everything forever, silently. So the
F14 defect itself is pinned here as a FACT about the tier0 DECISIONS volumes: clause
`1c` belongs to R90 and not to R91. If a future ruling ever moves it, this test
goes red and whoever moved it is told that the citations downstream need
re-reading -- which is the whole point of the graduation.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_r_citations.py"


def _module():
    spec = importlib.util.spec_from_file_location("lint_r_citations", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_canon_role_tempo_citations_resolve():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # A gate that checked zero citations would print the same clean line as one
    # that checked them all -- the dead-gate class. Assert it saw work.
    assert "OK: 0 clause-bearing" not in res.stdout


def test_the_f14_defect_is_still_visible_to_the_checker():
    """R90 owns clause 1c; R91 owns 2a-2d. This is the misattribution's fact."""
    mod = _module()
    # Since the R-D ledger split, R90/R91 live in the archive volume; read the
    # entries the same way the lint does -- across every tier0 volume.
    entries: dict[str, str] = {}
    for volume in mod._decision_volumes():
        for number, body in mod._entries(
                volume.read_text(encoding="utf-8")).items():
            entries[number] = entries.get(number, "") + body
    assert mod._declares(entries["90"], "1c")
    assert not mod._declares(entries["91"], "1c"), (
        "R91 now declares a clause 1c -- the F14 repair's premise moved; "
        "re-read every R90/1c citation before touching this test")
    assert mod._declares(entries["91"], "2b")
