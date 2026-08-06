"""The frozen R/D namespace lint runs green AND can see each defect class.

Successor to test_ledger_numbers_lint.py (retired with the ledgers,
2026-08-06). The namespace moved from DECISIONS volumes to git history at
tag pre-simplification-2026-08-06; the lint now guards docs/current/ against
citing unissued R-numbers and against re-declaring frozen ones. Both
directions are pinned here so the check cannot rot into a no-op.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_r_numbers.py"


def _module():
    spec = importlib.util.spec_from_file_location("lint_r_numbers", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_real_tree_is_one_clean_namespace():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # A scan of zero pages would also be "no findings" -- assert it saw the
    # governing surface.
    mod = _module()
    rels = [p.relative_to(mod.REPO).as_posix() for p in mod.pages()]
    assert "docs/current/LAW.md" in rels
    assert "docs/current/QUEUE.md" in rels


def test_a_citation_above_the_ceiling_is_a_finding(tmp_path):
    """The new-regime defect: a ruling number appears in prose that was never
    issued -- a typo, or a ruling that landed without its ceiling bump."""
    (tmp_path / "docs" / "current").mkdir(parents=True)
    (tmp_path / "docs" / "current" / "QUEUE.md").write_text(
        "Discharged by R999, allegedly.\n", encoding="utf-8")
    mod = _module()
    mod.REPO = tmp_path
    bad = mod.findings()
    assert len(bad) == 1 and "R999" in bad[0], bad


def test_a_frozen_number_re_declared_is_a_finding(tmp_path):
    """The old lint's defect class, translated: `## R7` heading a page in
    docs/current forks a number whose meaning is frozen at the tag."""
    (tmp_path / "docs" / "current").mkdir(parents=True)
    (tmp_path / "docs" / "current" / "LAW.md").write_text(
        "## R7 -- reborn\nbody\n", encoding="utf-8")
    mod = _module()
    mod.REPO = tmp_path
    bad = mod.findings()
    assert len(bad) == 1 and "R7" in bad[0] and "frozen" in bad[0], bad


def test_a_duplicate_new_declaration_is_a_finding(tmp_path):
    """Two pages both heading the same post-ceiling number is the
    cross-volume duplicate of the old regime, one directory over."""
    (tmp_path / "docs" / "current").mkdir(parents=True)
    (tmp_path / "docs" / "current" / "a.md").write_text(
        "## R122 -- here\n", encoding="utf-8")
    (tmp_path / "docs" / "current" / "b.md").write_text(
        "## R122 -- also here\n", encoding="utf-8")
    mod = _module()
    mod.REPO = tmp_path
    bad = [b for b in mod.findings() if "declared 2 times" in b]
    assert len(bad) == 1 and "R122" in bad[0], bad
