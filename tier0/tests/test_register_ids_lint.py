"""EB-127: the row-id uniqueness lint runs green AND can see the collision.

The sibling of `test_r_numbers_lint.py`, for the sibling namespace. The
R/D-series had a gate; the `M`-series in QUEUE and the `EB`-series in BACKLOG
had none, and two collisions reached review inside two weeks
(`EB-119`/`EB-120`, and `M38` minted twice off one base) — both caught by a
human, neither by the suite.

The lint carries its own `--self-test` (a uniqueness check that has never seen
a duplicate is indistinguishable from one that cannot see duplicates), and
this file both RUNS that self-test and asserts the real tree is clean with a
non-vacuous denominator. The two are not redundant: the self-test proves the
rules bite, this proves the tool is wired to the actual registers.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_register_ids.py"


def _module():
    spec = importlib.util.spec_from_file_location("lint_register_ids", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_committed_registers_are_clean():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_the_sweep_is_not_vacuous():
    """A scan of zero rows is also 'no findings'. Assert it saw both
    registers and a real number of rows in each."""
    mod = _module()
    _, where = mod.findings()
    per = {rel: 0 for rel in mod.REGISTERS}
    for sites in where.values():
        for rel, _line in sites:
            per[rel] += 1
    for rel, count in per.items():
        assert count >= 5, f"{rel} contributed only {count} row id(s): {per}"
    # The two series the row was filed about are both present.
    assert any(cid.startswith("EB-") for cid in where), sorted(where)[:5]
    assert any(cid.startswith("M") and cid[1:].isdigit() for cid in where), \
        sorted(where)


def test_the_lints_own_self_test_passes():
    res = subprocess.run([sys.executable, str(TOOL), "--self-test"],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "0 failure(s)" in res.stdout, res.stdout


def test_the_self_test_case_count_is_honest():
    """The printed denominator is a hand-kept number; a self-test that says
    eleven cases and runs three is the vacuum this file exists to prevent."""
    mod = _module()
    assert mod.SELF_TEST_CASES == 11
    assert mod.self_test() == []


def test_it_is_registered_in_the_ci_lane():
    """`run_lints.registry_gaps()` would fail the whole run on an unregistered
    lint; this asserts the lane it landed in, which that check cannot."""
    from tools import run_lints
    assert run_lints.registry_gaps() == []
    row = next(l for l in run_lints.REGISTRY if l.name == "register-ids")
    assert row.lane == "ci"
    assert row.script == "tools/lint_register_ids.py"


# --- the three rules, asserted here as well as in the tool -----------------

def test_a_duplicate_in_one_register_is_a_finding():
    mod = _module()
    q, b = mod.REGISTERS
    bad, _ = mod.findings({q: "| `M38` | one |\n| `M38` | two |", b: ""})
    assert any(f.startswith("DUPLICATE:") for f in bad), bad


def test_the_same_id_in_both_registers_is_a_finding():
    mod = _module()
    q, b = mod.REGISTERS
    bad, _ = mod.findings({q: "| `EB-9` | queue |", b: "| `EB-9` | backlog |"})
    assert any(f.startswith("CROSS-REGISTER:") for f in bad), bad


def test_a_citation_is_not_a_definition():
    """The scope line: citations elsewhere are fine and out of scope. A row
    whose PROSE names another row's id must not read as a second definition
    of it — that shape is on nearly every row in BACKLOG."""
    mod = _module()
    q, b = mod.REGISTERS
    bad, where = mod.findings({
        q: "| `M14` | blocked on `EB-74`, see `EB-74` |",
        b: "| `EB-74` | staged; QUEUE `M14` owns the pull |"})
    assert bad == [], bad
    assert sorted(where) == ["EB-74", "M14"], sorted(where)
