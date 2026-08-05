"""Track O slice 10 — pins for the S13 replay harness (review/redteam/harness.py).

These pin only behaviour that is unambiguously correct TODAY and that a future
edit to the harness could silently regress: the harness must fail LOUDLY
(``ok: False``) on an input it cannot honour, must refuse a line whose script
could not be followed, and must be deterministic for a fixed seed.

Deliberately NOT pinned: that a claim satisfied by the null case still returns
``verified: True`` (Track O finding O10-1). Pinning that would ratify the
defect. See docs/instrument-redteam-2026-08-05.md.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import warnings

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HARNESS_PY = ROOT / "review" / "redteam" / "harness.py"
LINES_JSON = ROOT / "review" / "redteam" / "exploit-lines.json"


@pytest.fixture(scope="module")
def harness():
    spec = importlib.util.spec_from_file_location("s13_harness", HARNESS_PY)
    mod = importlib.util.module_from_spec(spec)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def a_real_line():
    lines = json.loads(LINES_JSON.read_text())
    by_id = {line["line_id"]: line for line in lines}
    return by_id["klee_spark_1_bright_idea_refund_infinite"]


def _line(base, **kw):
    out = dict(base)
    out.update(kw)
    return out


def _run(harness, line):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return harness.run_line(line)


# --------------------------------------------------------------------------
# The harness fails loudly on inputs it cannot honour.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("mutation", [
    pytest.param({"deck": ["no_such_card_track_o"] * 10}, id="unknown_card"),
    pytest.param({"relics": ["no_such_relic_track_o"]}, id="unknown_relic"),
    pytest.param({"encounter_id": "no_such_encounter_track_o"},
                 id="unknown_encounter"),
    pytest.param({"claim": {"kind": "metric", "metric": "no_such_metric",
                            "op": ">=", "value": 0}}, id="unknown_metric"),
    pytest.param({"claim": {"kind": "metric", "metric": "hp_left",
                            "op": "!=", "value": 0}}, id="unsupported_op"),
    pytest.param({"claim": {"kind": "no_such_kind"}}, id="unknown_claim_kind"),
])
def test_unhonourable_input_is_never_silently_verified(
        harness, a_real_line, mutation):
    """An input the harness cannot honour must surface, not verify.

    Every one of these is a way a red-team line could reference something that
    does not exist. If any of them ever returns ``verified: True`` -- or even
    ``ok: True`` -- a line could pass by naming nothing at all.
    """
    base = _line(a_real_line, line_id="track_o_s10",
                 claim={"kind": "metric", "metric": "hp_left",
                        "op": ">=", "value": 0})
    result = _run(harness, _line(base, **mutation))

    assert result["ok"] is False, (
        f"harness accepted an unhonourable line: {mutation!r}")
    assert result["verified"] is False
    assert "error" in result and result["error"].strip()


def test_scripted_card_absent_from_hand_is_a_miss_and_blocks_verification(
        harness, a_real_line):
    """A script the pilot could not follow must not verify, however easy the claim.

    ``executed`` is the harness's only guard that the line's *script* -- not
    merely its claim -- described what happened. A card named in the script and
    never present must land in ``misses`` and must veto the verdict.
    """
    line = _line(a_real_line, line_id="track_o_s10_miss",
                 script=[["no_such_card_track_o"]],
                 script_default="pass",
                 claim={"kind": "metric", "metric": "hp_left",
                        "op": ">=", "value": 0})
    result = _run(harness, line)

    assert result["ok"] is True, "a bad card id in the SCRIPT is not a crash"
    assert result["claim_holds"] is True, "the claim itself is trivially true"
    assert result["executed"] is False
    assert result["verified"] is False, (
        "a line whose script could not be followed must not verify even when "
        "its claim holds")
    assert [m["card"] for m in result["misses"]] == ["no_such_card_track_o"]
    assert result["misses"][0]["reason"] == "not_in_hand"


def test_run_line_is_deterministic_for_a_fixed_seed(harness, a_real_line):
    """The ledger's re-executability claim rests on this.

    `review/redteam/exploit-ledger.md` states every line "is re-executable ...
    reproduces replay-results.json deterministically per seed". If two runs of
    one line disagree, no verdict in that ledger means anything.
    """
    line = _line(a_real_line, line_id="track_o_s10_determinism")

    first = _run(harness, line)
    second = _run(harness, line)

    assert first["ok"] is True
    for key in ("verified", "claim_holds", "executed", "plays_made", "fight"):
        assert first[key] == second[key], f"{key} is not reproducible"


def test_metric_claim_reads_the_metric_it_names(harness, a_real_line):
    """`observed` must be keyed on the claim's own metric name.

    The ledger quotes `observed` as the evidence for every metric finding; a
    verdict reported under the wrong key would be unreadable.
    """
    line = _line(a_real_line, line_id="track_o_s10_observed",
                 claim={"kind": "metric", "metric": "damage_dealt_total",
                        "op": ">=", "value": 0})
    result = _run(harness, line)

    assert result["ok"] is True
    assert list(result["observed"]) == ["damage_dealt_total"]
    assert result["observed"]["damage_dealt_total"] == \
        result["fight"]["damage_dealt_total"]
