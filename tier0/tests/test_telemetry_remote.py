"""tools/telemetry_remote.py: the wrangler reply parser, the filters and the summary.

No wrangler and no network: the worker's own tests (telemetry-worker/, vitest)
cover the upload side.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import telemetry_remote as tr  # noqa: E402


def _run(char: str, victory: bool, floor_reached: int, floors: list[dict]) -> dict:
    return {"character": char, "victory": victory, "floor_reached": floor_reached,
            "ascension": 0, "floors": floors}


def _floor(kind: str, offered: list[str], picked: list[str]) -> dict:
    return {"type": kind, "card_choice": {"offered": offered, "picked": picked}}


def test_parse_wrangler_json_skips_the_banner_and_joins_statements():
    stdout = ("some banner line\n"
              + json.dumps([{"results": [{"payload": "1"}], "success": True},
                            {"results": [{"payload": "2"}], "success": True}]))
    assert tr.parse_wrangler_json(stdout) == [{"payload": "1"}, {"payload": "2"}]


def test_build_where_quotes_values():
    assert tr.build_where(None, None, None) == ""
    where = tr.build_where("beta", "CHARACTER.O'BRIEN", 1, now=1000.0 + 86400)
    assert where == (" WHERE variant = 'beta' AND character = 'CHARACTER.O''BRIEN'"
                     " AND received_at >= 1000")


def test_summary_counts_wins_floors_picks_and_passes_without_shops():
    runs = [
        _run("C.A", True, 50, [_floor("monster", ["X", "Y", "Z"], ["X"]),
                               _floor("monster", ["X", "Y", "Z"], []),
                               _floor("shop", ["Y"] * 30, ["Y"])]),
        _run("C.A", False, 10, [_floor("elite", ["X", "Z", "W"], ["Z"])]),
        _run("C.B", False, 20, []),
    ]
    s = tr.summarise(runs, top=2)
    assert list(s) == ["C.A", "C.B"]
    a = s["C.A"]
    assert (a["runs"], a["wins"], a["win_rate"]) == (2, 1, 0.5)
    assert a["floor_median"] == 30
    assert a["card_screens"] == 3 and abs(a["skip_rate"] - 1 / 3) < 1e-9
    assert a["top_picked"][0] == ("X", 1, 3)
    # Y was offered twice off the shop and never taken there; the shop's 30 are ignored.
    assert ("Y", 2, 2) in a["top_passed"]
    assert s["C.B"]["card_screens"] == 0 and s["C.B"]["skip_rate"] == 0.0
    assert "3 runs" in tr.render(s, 3)
