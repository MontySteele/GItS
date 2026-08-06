"""The P-ledger lint runs green, AND both red directions are still visible to it.

Same graduation idiom as test_r_citation_lint.py: a lint asserted only in the
green direction can rot into a no-op, so both charter-mandated failure modes
(`docs/class-p-charter-2026-08-06.md` §3, R119) are pinned here against
fabricated inputs -- a row missing an attestation line, and a handle commit
that touches a file owned by a [USER]-gated register.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_p_ledger.py"


def _module():
    spec = importlib.util.spec_from_file_location("lint_p_ledger", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_FIVE = """\
**Attestation:**
1. Zero design authority -- fabricated.
2. Truth-restoring -- fabricated.
3. Reversible in one commit -- fabricated.
4. Predictability -- fabricated.
5. No gate collision -- fabricated.
"""


def test_ledger_lint_runs_green_and_saw_work():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # The dead-gate class: zero rows would mean the parser stopped matching
    # the ledger's real format. The tool itself fails on zero rows; assert the
    # green line still reports a count all the same.
    assert "0 row(s)" not in res.stdout


def test_a_row_without_five_attestation_lines_is_a_finding():
    mod = _module()
    body = "**Handle:** `0123abc`\n" + _FIVE.replace(
        "5. No gate collision -- fabricated.\n", "")
    items = mod.parse_items("## fabricated row\n" + body)
    assert len(items) == 1
    assert mod.attestation_problem(items[0][1]) is not None
    # And the complete block passes, so the check discriminates.
    ok = mod.parse_items("## fabricated row\n**Handle:** `0123abc`\n" + _FIVE)
    assert mod.attestation_problem(ok[0][1]) is None


def test_a_missing_attestation_block_is_a_finding():
    mod = _module()
    items = mod.parse_items("## fabricated row\n**Handle:** `0123abc`\n")
    assert mod.attestation_problem(items[0][1]) is not None


def test_a_commit_touching_a_gated_register_is_visible():
    """Rule 2's matcher, fed the exact surfaces the charter names."""
    mod = _module()
    hit = mod.owned_paths([
        "tier0/DECISIONS.md",
        "klee-mod/DECISIONS.md",
        "docs/probe-e-corpse-detonation-registration-draft.md",
        "docs/payoff-reach-reregistration-draft-2026-08-06.md",
        "docs/roster-anchor-v14-v6-2026-08-06.md",
        "docs/kokomi-playtest-protocol.md",
    ])
    assert len(hit) == 6, hit
    # And the surfaces Class-P legitimately edits stay unowned -- the charter
    # directs the swarm to strike queue rows, so flagging them would make
    # every legitimate landing a finding.
    clear = mod.owned_paths([
        "docs/registry/user-queue.md",
        "docs/dockets/engineering-backlog.md",
        "docs/registry/p-ledger.md",
        "docs/atlas/vendor-sts2-mcp.md",
        "tools/lint_p_ledger.py",
    ])
    assert clear == [], clear


def test_a_sha_only_row_body_parses_as_a_row():
    """A row is DEFINED by its handle; prose sections must not parse as rows."""
    mod = _module()
    text = ("## header prose\nno handle here\n"
            "## real row\n**Handle:** `deadbeef`\n" + _FIVE)
    items = mod.parse_items(text)
    assert [h for h, _ in items] == ["real row"]
    assert mod.handles(items[0][1]) == ["deadbeef"]
