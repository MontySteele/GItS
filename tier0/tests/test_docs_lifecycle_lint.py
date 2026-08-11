"""The docs-lifecycle lint runs green AND can see each defect class.

Same pinning pattern as test_r_numbers_lint.py: a lint that scans zero
files or matches nothing is also "no findings", so each defect class is
reproduced in a tmp tree and asserted visible. The lint is the enforcement
half of R178 (exit is part of close) — metadata is checked, not prose, so
an active packet mentioning HISTORICAL evidence is not a finding.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_docs_lifecycle.py"

META = "<!--\nlifecycle: active\nowner: M14\nexit_when: graded\n-->\n"


def _module():
    spec = importlib.util.spec_from_file_location("lint_docs_lifecycle", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tree(tmp_path, packet=META + "body\n"):
    (tmp_path / "docs" / "current").mkdir(parents=True)
    (tmp_path / "review" / "active").mkdir(parents=True)
    (tmp_path / "docs" / "current" / "QUEUE.md").write_text(
        "| ID | Decision needed | Status | Provenance |\n"
        "|---|---|---|---|\n"
        "| `M14` | countersign | OPEN | R149 |\n", encoding="utf-8")
    (tmp_path / "docs" / "current" / "BACKLOG.md").write_text(
        "| ID | Item | Provenance |\n|---|---|---|\n", encoding="utf-8")
    (tmp_path / "review" / "active" / "packet.md").write_text(
        packet, encoding="utf-8")
    return tmp_path


def test_the_real_tree_is_clean():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # A scan of zero pages would also be "no findings" -- assert it saw the
    # governing surface and the packets.
    mod = _module()
    rels = [p.relative_to(mod.REPO).as_posix() for p in mod.pages()]
    assert "docs/current/QUEUE.md" in rels
    assert any(r.startswith("review/active/") for r in rels)
    assert (mod.REPO / mod.ACTIVE_DIR).is_dir()


def test_a_conforming_tmp_tree_is_clean(tmp_path):
    mod = _module()
    assert mod.findings(_tree(tmp_path)) == []


def test_a_packet_without_the_block_is_a_finding(tmp_path):
    mod = _module()
    bad = mod.findings(_tree(tmp_path, packet="# just prose\n"))
    assert len(bad) == 1 and "lifecycle" in bad[0], bad


def test_an_orphaned_packet_is_a_finding(tmp_path):
    """The R178 defect: the owning row closed but the packet stayed."""
    root = _tree(tmp_path)
    (root / "docs" / "current" / "QUEUE.md").write_text(
        "| ID | Decision needed | Status | Provenance |\n"
        "|---|---|---|---|\n", encoding="utf-8")
    mod = _module()
    bad = mod.findings(root)
    assert len(bad) == 1 and "M14" in bad[0] and "exits" in bad[0], bad


def test_a_non_active_lifecycle_is_a_finding(tmp_path):
    root = _tree(tmp_path, packet=META.replace("active", "historical")
                 + "body\n")
    mod = _module()
    bad = mod.findings(root)
    assert len(bad) == 1 and "historical" in bad[0], bad


def test_a_dead_current_path_is_a_finding(tmp_path):
    root = _tree(tmp_path)
    (root / "docs" / "current" / "STATE.md").write_text(
        "see docs/current/GONE.md for detail\n", encoding="utf-8")
    mod = _module()
    bad = mod.findings(root)
    assert len(bad) == 1 and "GONE.md" in bad[0], bad


def test_git_show_syntax_is_exempt(tmp_path):
    """Retrieve-by-commit is the declared citation form for exited paths."""
    root = _tree(tmp_path)
    (root / "docs" / "current" / "STATE.md").write_text(
        "see `git show abc123:review/active/gone.md` §3\n", encoding="utf-8")
    mod = _module()
    assert mod.findings(root) == []


def test_historical_mention_in_prose_is_not_a_finding(tmp_path):
    """Metadata is linted, not vocabulary (the GPT-audit refinement)."""
    root = _tree(tmp_path, packet=META
                 + "This packet cites HISTORICAL evidence, GRADED runs and a "
                   "REFERENCE record.\n")
    mod = _module()
    assert mod.findings(root) == []
