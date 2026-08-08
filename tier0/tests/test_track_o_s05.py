"""Track O, slice 5 -- pins on the two replayers' reading of malformed logs.

The slice attacked `understudy/replay.py` and `understudy/trace_replay.py` with
truncated, duplicated, reordered and corrupted soak logs. Most of what it found
is UNPINNED on purpose: a silent misattribution is a defect, and writing a test
that asserts the defect would ratify it.

What IS pinned here is the small set of readings whose correct answer the
instruments' own prose already states, and which a future reader-rewrite could
break without any suite noticing:

    1. WHITESPACE IS INERT. Blank lines and a missing final newline are
       formatting, not data. `report.read_run_log` and `replay.read_jsonl`
       both strip and skip, and every downstream number must be unchanged.
    2. THE SCHEMA IS ADDITIVE. `soak.py`'s fight record carries "Keys only
       ADDED -- nothing renamed, which is what the shared-schema rule in
       understudy/README.md costs and permits". An unknown record type and an
       unknown field on a known record must therefore both read as inert.
    3. A DUPLICATED SELECTOR ROUND IS LAST-WINS. `replay._selector_choice`
       states it: "The LAST matching row for the round wins: a turn that
       re-designates has the later answer standing".
    4. A MISSING TRACE KEY DOES NOT RAISE -- and, since `EB-59`, does not
       read as EMPTY either. A pre-P1.5 record carries no `selectors`, so
       `trace_replay.trace` returns `NOT_RECORDED` for it: no crash, and no
       false agreement with a run that was offered none.

Fixtures: `review/redteam/fixtures/track_o/s05-*` (built by `s05_build.py`).
"""

from __future__ import annotations

import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from understudy import replay, report, trace_replay

FIX = (Path(__file__).resolve().parents[2]
       / "review" / "redteam" / "fixtures" / "track_o")
BASE = FIX / "s05-baseline-run001.jsonl"
BASE_INDEX = FIX / "s05-baseline-index.json"


def _summary(path: Path) -> dict:
    """`replay.main` over one log, as its own printed JSON summary."""
    out = Path(tempfile.mkdtemp()) / "d.tsv"
    buf = io.StringIO()
    with redirect_stdout(buf):
        replay.main(["--logs", str(path), "--out", str(out),
                     "--character", "furina"])
    rows = out.read_text(encoding="utf-8").splitlines()[1:]
    shutil.rmtree(out.parent, ignore_errors=True)
    summary = json.loads(buf.getvalue())
    summary["_rows"] = rows
    return summary


def _report(path: Path, monkeypatch) -> str:
    tmp = Path(tempfile.mkdtemp())
    idx = json.loads(BASE_INDEX.read_text(encoding="utf-8"))
    idx["stamp"] = "S05PIN"
    (tmp / "soak-S05PIN-index.json").write_text(json.dumps(idx),
                                                encoding="utf-8")
    shutil.copyfile(path, tmp / "soak-S05PIN-run001.jsonl")
    monkeypatch.setattr(report, "LOG_DIR", tmp)
    try:
        return report.render("S05PIN")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="module")
def baseline():
    return _summary(BASE)


# --------------------------------------------------------------------------
# 1 + 2. whitespace is inert; the schema is additive
# --------------------------------------------------------------------------

INERT = [
    "s05-m10-blanklines-no-trailing-nl-run001.jsonl",
    "s05-m11-unknown-rows-run001.jsonl",
]


@pytest.mark.parametrize("name", INERT)
def test_replay_reading_is_unmoved_by_whitespace_and_unknown_keys(
        name, baseline):
    got = _summary(FIX / name)
    for key in ("fights_found", "fights_replayed", "rows",
                "rows_flagged_reading", "comparisons", "by_field"):
        assert got[key] == baseline[key], key
    # Not just the counts: the divergence rows themselves, byte for byte
    # except the fight_id stem, which carries the file name.
    def strip(rows):
        return [r.split("\t", 1)[1] for r in rows]
    assert strip(got["_rows"]) == strip(baseline["_rows"])


@pytest.mark.parametrize("name", INERT)
def test_report_is_unmoved_by_whitespace_and_unknown_keys(name, monkeypatch):
    base = _report(BASE, monkeypatch)
    got = _report(FIX / name, monkeypatch)
    assert got == base


@pytest.mark.parametrize("name", INERT)
def test_trace_compare_is_unmoved_by_whitespace_and_unknown_keys(
        name, monkeypatch):
    tmp = Path(tempfile.mkdtemp())
    for stamp, src in (("S05A", BASE), ("S05B", FIX / name)):
        idx = json.loads(BASE_INDEX.read_text(encoding="utf-8"))
        idx["stamp"] = stamp
        (tmp / f"soak-{stamp}-index.json").write_text(json.dumps(idx),
                                                      encoding="utf-8")
        shutil.copyfile(src, tmp / f"soak-{stamp}-run001.jsonl")
    monkeypatch.setattr(report, "LOG_DIR", tmp)
    try:
        assert trace_replay.compare_runs(("S05A", 1), ("S05B", 1)) == []
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# 3. a duplicated selector round is LAST-wins, as `_selector_choice` says
# --------------------------------------------------------------------------

def test_duplicated_selector_round_takes_the_later_answer():
    offers = ["Center Stage", "Guest Cast"]
    fight = {"selectors": [
        [1, "card_select", 0, "Center Stage", offers],
        [1, "card_select", 1, "Guest Cast", offers],
    ]}
    assert replay._selector_choice(fight, 1) == "companion"
    fight["selectors"].reverse()
    assert replay._selector_choice(fight, 1) == "self"


def test_a_selector_row_without_both_offers_is_declined():
    """"Center Stage" against a list that never offered Guest Cast is a
    different screen wearing a familiar word."""
    fight = {"selectors": [[1, "card_select", 0, "Center Stage",
                            ["Center Stage", "Encore"]]]}
    assert replay._selector_choice(fight, 1) is None


# --------------------------------------------------------------------------
# 4. a missing trace key reads as NOT RECORDED, never as a raise and never
#    as empty (amended by `EB-59`)
# --------------------------------------------------------------------------

def test_trace_reads_a_missing_key_as_not_recorded():
    assert trace_replay.trace({}) == {k: trace_replay.NOT_RECORDED
                                      for k in trace_replay.TRACE_KEYS}
    # An explicit null is the same fact as an absent key: no column here.
    assert (trace_replay.trace({"selectors": None})["selectors"]
            is trace_replay.NOT_RECORDED)
    # And it is still not a raise, which is the half of the rule that stands.
    assert set(trace_replay.trace({})) == set(trace_replay.TRACE_KEYS)
