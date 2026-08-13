"""The vendored bridge has not drifted off its pin (tools/lint_vendor_pin.py).

Dual-wiring, per house style: the lint is invoked directly in CI, from
`deploy_bridge.ps1` before it builds, and from here so the suite carries it
too. The Understudy sprint opened `vendor/` with no precedent, and a snapshot
nobody checks is a snapshot that silently becomes "some version of STS2MCP".
"""

import subprocess
import sys
from pathlib import Path

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]
LINT = REPO / "tools" / "lint_vendor_pin.py"


def _run(*args):
    return subprocess.run([sys.executable, str(LINT), *args],
                          capture_output=True, text=True)


def test_vendored_source_matches_its_recorded_pin():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_the_lint_states_its_scope_not_just_a_verdict():
    """A bare CLEAN from a hash check invites the reading it cannot support:
    that the pin is the RIGHT commit. It is not that; it is only that the tree
    still is what we wrote down. Say which."""
    res = _run()
    assert "scope (what this lint has NO opinion about)" in res.stdout, res.stdout


def test_the_bridge_is_actually_vendored_and_pinned():
    """The gate above passes vacuously on a repo with no vendor/ -- which is
    the correct behaviour for the lint and the wrong assertion for this sprint.
    Understudy's whole first work item is that this component exists."""
    prov = REPO / "vendor" / "STS2_MCP" / "PROVENANCE.md"
    assert prov.exists(), "the ratified vendored bridge is missing"
    text = prov.read_text(encoding="utf-8")
    # P0 stop-and-surface item 2: the release binary is the one way to get the
    # version-pin failure the brief worried about, and it is easy to do by
    # accident. The pin is load-bearing, so it is asserted, not described.
    assert "pin: 55e0648" in text
    assert "license: MIT" in text
    assert (REPO / "vendor" / "STS2_MCP" / "LICENSE").exists()


def test_our_additions_live_apart_from_upstreams_source():
    """gits/ is ours; everything else is theirs. If that boundary blurs, the
    manifest stops meaning anything and the refresh procedure stops working."""
    manifest = (REPO / "vendor" / "STS2_MCP" / "UPSTREAM_MANIFEST.tsv").read_text(
        encoding="utf-8")
    assert "\tgits/" not in manifest, "our own files must not be listed as upstream's"
    modified = [ln.split("\t")[2] for ln in manifest.splitlines()
                if "\tgits-modified\t" in ln]
    # Today: THREE files, recorded in PROVENANCE.md. This is not a cap -- it
    # is a tripwire, so growth is a thing someone decided to do.
    #
    # It has grown TWICE, deliberately, and these are those decisions written
    # down:
    #
    # P1.5 (2026-08-05, R104) added `state["resources"] = ...` to
    # BuildPlayerState, because a resources map attached out-of-band by a
    # Harmony patch would not be ATOMIC with the state read it belongs to, and
    # a meter read a frame after the hand it describes is a different
    # measurement. Everything else P1.5 added lives in gits/.
    #
    # EB-92 (2026-08-13) added two guards to McpMod.Wiki.cs's result
    # formatter. It is an edit rather than a gits/ addition because there is
    # nothing to route: the failure is INSIDE upstream's formatting of one
    # candidate, where a throwing custom model took the whole search down with
    # a 500. A patch would have to re-implement the method to wrap it. The
    # guards are upstreamable as they stand -- any mod's custom model can do
    # this to upstream's wiki -- so this row is expected to shrink again if
    # the fix ever goes home.
    assert modified == ["McpMod.cs", "McpMod.StateBuilder.cs",
                        "McpMod.Wiki.cs"], (
        f"upstream files we have edited changed: {modified}. Update PROVENANCE.md's "
        f"'What we changed' table and this assertion together, deliberately.")
