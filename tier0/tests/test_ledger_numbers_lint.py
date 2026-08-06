"""The cross-volume duplicate-number lint runs green AND can see a duplicate.

The CI `ledger` job's check was an inline per-file script until the R-D ledger
split (2026-08-06) added the failure mode it could not see: one number headed
in two volumes. The graduated tool treats `tier0/DECISIONS*.md` +
`klee-mod/DECISIONS*.md` as ONE namespace. Both directions are pinned here so
the check cannot rot into a no-op (same discipline as test_r_citation_lint).
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_ledger_numbers.py"


def _module():
    spec = importlib.util.spec_from_file_location("lint_ledger_numbers", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_real_volumes_are_one_clean_namespace():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # A scan of zero volumes would also be "no duplicates" -- assert it saw
    # at least the live tier0 and klee-mod ledgers.
    mod = _module()
    rels = [v.relative_to(mod.REPO).as_posix() for v in mod.volumes()]
    assert "tier0/DECISIONS.md" in rels
    assert "klee-mod/DECISIONS.md" in rels


def test_a_cross_volume_duplicate_is_a_finding(tmp_path):
    """The exact defect the widening exists for: `## R7` headed in a tier0
    volume AND in klee-mod is one number declared twice across the namespace."""
    (tmp_path / "tier0").mkdir()
    (tmp_path / "klee-mod").mkdir()
    (tmp_path / "tier0" / "DECISIONS.md").write_text(
        "## R7 -- live\nbody\n", encoding="utf-8")
    (tmp_path / "tier0" / "DECISIONS-archive-R1-R6.md").write_text(
        "## R5 -- archived\nbody\n", encoding="utf-8")
    (tmp_path / "klee-mod" / "DECISIONS.md").write_text(
        "## R7 -- also here\n## D2 -- fine\n", encoding="utf-8")
    mod = _module()
    mod.REPO = tmp_path
    bad = mod.findings()
    assert len(bad) == 1, bad
    assert bad[0].startswith("R7 declared 2 times"), bad[0]


def test_a_within_volume_duplicate_is_still_a_finding(tmp_path):
    """The original per-file guarantee survives the widening."""
    (tmp_path / "tier0").mkdir()
    (tmp_path / "tier0" / "DECISIONS.md").write_text(
        "## R3 -- once\n## R3 -- twice\n", encoding="utf-8")
    mod = _module()
    mod.REPO = tmp_path
    bad = mod.findings()
    assert len(bad) == 1 and "R3" in bad[0], bad
