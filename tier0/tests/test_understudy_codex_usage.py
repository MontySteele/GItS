"""EB-227: the Codex seat reads its own meter, and stops at the stop line.

Fixture rollout lines, not a live `$CODEX_HOME`: the point of the guard is
that it behaves the same at 02:00 on a machine nobody is watching, and a
test that depended on what the real seat happened to have spent would be a
test that says something different every day.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from understudy import codex_usage, seat


def _line(primary_pct, secondary_pct, *, primary_resets, secondary_resets,
          stamp="2026-08-30T04:45:37.586Z", nested=False):
    limits = {
        "limit_id": "codex",
        "primary": {"used_percent": primary_pct, "window_minutes": 300,
                    "resets_at": primary_resets},
        "secondary": {"used_percent": secondary_pct,
                      "window_minutes": 10080,
                      "resets_at": secondary_resets},
        "plan_type": "plus",
    }
    payload = {"type": "token_count", "info": {"total_tokens": 27508}}
    if nested:
        payload["info"]["rate_limits"] = limits
    else:
        payload["rate_limits"] = limits
    return json.dumps({"timestamp": stamp, "ordinal": 218,
                       "type": "event_msg", "payload": payload})


NOW = datetime(2026, 8, 30, 5, 0, 0, tzinfo=timezone.utc)
SOON = int((NOW + timedelta(hours=2)).timestamp())
NEXT_WEEK = int((NOW + timedelta(days=6)).timestamp())
GONE = int((NOW - timedelta(hours=3)).timestamp())


def _usage(text_lines, **kw):
    from pathlib import Path
    return codex_usage.usage_from_lines(text_lines,
                                        rollout=Path("rollout.jsonl"),
                                        now=NOW, **kw)


# ------------------------------------------------------------- the read ----

def test_a_fresh_rollout_reads_both_windows():
    u = _usage([_line(3.0, 11.0, primary_resets=SOON,
                      secondary_resets=NEXT_WEEK)])
    assert u is not None
    assert (u.primary.used_percent, u.primary.window_minutes) == (3.0, 300)
    assert (u.secondary.used_percent, u.secondary.window_minutes) == (11.0,
                                                                     10080)
    assert u.primary.label == "5h" and u.secondary.label == "week"
    assert u.primary.resets_at.tzinfo is not None
    assert u.secondary.resets_at.tzinfo is not None
    assert u.observed_at == datetime(2026, 8, 30, 4, 45, 37, 586000,
                                     tzinfo=timezone.utc)
    assert u.plan == "plus"
    assert u.over() is None


def test_rate_limits_is_read_from_either_home_on_the_payload():
    """codex 0.56 hangs it off `payload`; older writeups nested it in `info`."""
    flat = _usage([_line(4.0, 5.0, primary_resets=SOON,
                         secondary_resets=NEXT_WEEK)])
    nested = _usage([_line(4.0, 5.0, primary_resets=SOON,
                           secondary_resets=NEXT_WEEK, nested=True)])
    assert flat.primary.used_percent == nested.primary.used_percent == 4.0


def test_the_last_block_wins_and_null_and_junk_lines_are_skipped():
    lines = [
        _line(1.0, 2.0, primary_resets=SOON, secondary_resets=NEXT_WEEK),
        '{"type":"event_msg","payload":{"type":"token_count",'
        '"rate_limits":null}}',
        "not json at all, but it has rate_limits in it",
        "",
        _line(42.0, 9.0, primary_resets=SOON, secondary_resets=NEXT_WEEK,
              stamp="2026-08-30T04:55:00.000Z"),
    ]
    u = _usage(lines)
    assert u.primary.used_percent == 42.0
    assert u.observed_at.minute == 55


def test_a_rolled_over_window_reads_as_zero_and_the_summary_says_so():
    """Stale data from a window that no longer exists is not a bill."""
    u = _usage([_line(93.0, 11.0, primary_resets=GONE,
                      secondary_resets=NEXT_WEEK)])
    assert u.primary.stale is True
    assert u.primary.used_percent == 0.0
    assert u.primary.reported_percent == 93.0     # what the file said
    assert u.secondary.stale is False
    assert "rolled over" in u.summary()
    # And so it does NOT refuse -- which is the whole point of the rule.
    assert u.over() is None


def test_no_rate_limit_line_anywhere_is_none_not_an_exception():
    assert _usage(["", '{"type":"event_msg","payload":{}}']) is None


def test_a_missing_codex_home_probes_to_none(tmp_path):
    assert codex_usage.probe(home=tmp_path / "nothing-here") is None


def test_probe_reads_the_newest_rollout_by_mtime(tmp_path):
    import os
    sessions = tmp_path / "sessions" / "2026" / "08" / "30"
    sessions.mkdir(parents=True)
    old = sessions / "rollout-2026-08-30T09-00-00-aaa.jsonl"
    new = sessions / "rollout-2026-08-30T01-00-00-bbb.jsonl"
    old.write_text(_line(1.0, 1.0, primary_resets=SOON,
                         secondary_resets=NEXT_WEEK) + "\n", encoding="utf-8")
    new.write_text(_line(7.0, 8.0, primary_resets=SOON,
                         secondary_resets=NEXT_WEEK) + "\n", encoding="utf-8")
    # `new` began EARLIER by name and was written LATER; mtime is the truth.
    os.utime(old, (1_700_000_000, 1_700_000_000))
    u = codex_usage.probe(home=tmp_path, now=NOW)
    assert u is not None and u.primary.used_percent == 7.0


def test_the_one_line_summary_has_the_shape_the_operator_reads():
    u = _usage([_line(3.0, 11.0, primary_resets=SOON,
                      secondary_resets=NEXT_WEEK)])
    line = u.summary()
    assert line.startswith("codex: 5h 3% (resets ")
    assert " · week 11% (resets " in line
    assert " · from rollout rollout.jsonl @ 2026-08-30T04:45:37Z" in line


# ---------------------------------------------------------- the stop line --

def test_the_defaults_are_eighty_five_and_fifty(monkeypatch):
    monkeypatch.delenv(codex_usage.PRIMARY_STOP_ENV, raising=False)
    monkeypatch.delenv(codex_usage.WEEKLY_STOP_ENV, raising=False)
    assert codex_usage.primary_stop() == 85.0
    assert codex_usage.weekly_stop() == 50.0


def test_env_vars_override_and_a_typo_falls_back(monkeypatch):
    monkeypatch.setenv(codex_usage.PRIMARY_STOP_ENV, "20")
    monkeypatch.setenv(codex_usage.WEEKLY_STOP_ENV, "not a number")
    assert codex_usage.primary_stop() == 20.0
    assert codex_usage.weekly_stop() == 50.0     # a typo never disarms it


@pytest.mark.parametrize("primary,secondary,reason", [
    (85.0, 1.0, "codex_budget_primary"),        # AT the line, not past it
    (99.0, 1.0, "codex_budget_primary"),
    (1.0, 50.0, "codex_budget_weekly"),
    (1.0, 88.0, "codex_budget_weekly"),
])
def test_over_names_the_window_that_stopped_the_call(primary, secondary,
                                                     reason, monkeypatch):
    monkeypatch.delenv(codex_usage.PRIMARY_STOP_ENV, raising=False)
    monkeypatch.delenv(codex_usage.WEEKLY_STOP_ENV, raising=False)
    u = _usage([_line(primary, secondary, primary_resets=SOON,
                      secondary_resets=NEXT_WEEK)])
    over = u.over()
    assert over is not None and over[0] == reason


def test_just_under_both_lines_spends_the_call(monkeypatch):
    monkeypatch.delenv(codex_usage.PRIMARY_STOP_ENV, raising=False)
    monkeypatch.delenv(codex_usage.WEEKLY_STOP_ENV, raising=False)
    u = _usage([_line(84.9, 49.9, primary_resets=SOON,
                      secondary_resets=NEXT_WEEK)])
    assert u.over() is None


def test_the_record_carries_both_windows_and_the_lines_it_was_judged_against():
    u = _usage([_line(3.0, 11.0, primary_resets=SOON,
                      secondary_resets=NEXT_WEEK)])
    rec = u.record()
    assert rec["primary_used_percent"] == 3.0
    assert rec["secondary_used_percent"] == 11.0
    assert rec["primary_window_minutes"] == 300
    assert rec["secondary_stale"] is False
    assert rec["primary_stop_percent"] == codex_usage.primary_stop()
    assert rec["weekly_stop_percent"] == codex_usage.weekly_stop()
    assert rec["observed_at"] == "2026-08-30T04:45:37Z"
    json.dumps(rec)          # it has to survive the ledger it lands in


# ------------------------------------------------------------- the seat ----

def _fixture_home(tmp_path, primary, secondary):
    sessions = tmp_path / "sessions" / "2026" / "08" / "30"
    sessions.mkdir(parents=True)
    (sessions / "rollout-2026-08-30T00-42-50-fixture.jsonl").write_text(
        _line(primary, secondary, primary_resets=int(
            (datetime.now(timezone.utc) + timedelta(hours=2)).timestamp()),
            secondary_resets=int(
            (datetime.now(timezone.utc) + timedelta(days=6)).timestamp()))
        + "\n", encoding="utf-8")
    return tmp_path


def test_budget_check_returns_the_record_and_the_refusal(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", str(_fixture_home(tmp_path, 90.0, 1.0)))
    record, over = seat.budget_check(quiet=True)
    assert record["available"] is True
    assert record["primary_used_percent"] == 90.0
    assert over is not None and over[0] == "codex_budget_primary"


def test_budget_check_proceeds_when_there_is_no_rollout(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "empty"))
    record, over = seat.budget_check(quiet=True)
    assert record["available"] is False
    assert over is None            # a missing file NEVER blocks a round


def test_grade_refuses_before_it_spends_the_call(tmp_path, monkeypatch):
    """The seat's own refusal shape, and `codex exec` is never reached."""
    monkeypatch.setenv("CODEX_HOME", str(_fixture_home(tmp_path, 1.0, 77.0)))

    ran: list[list[str]] = []

    def _never(argv, **kw):
        ran.append(argv)
        raise AssertionError("a refused seat must not run codex")

    monkeypatch.setattr(seat, "_run", _never)
    monkeypatch.setattr(seat, "codex_path", lambda: "codex")
    monkeypatch.setattr(seat, "_codex_version", lambda _c: "0.0-test")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(seat, "scratch_root", lambda: scratch)

    turn = "EB227-BUDGET-T01"
    d = seat.REPO / "review" / "qa" / turn
    d.mkdir(parents=True, exist_ok=True)
    try:
        (d / "packet.md").write_text("# packet\n", encoding="utf-8")
        logs = tmp_path / "logs"
        code = seat.main(["grade", turn, "--log-root", str(logs)])
        assert code == 1
        assert ran == []
        blob = json.loads(next(logs.rglob("seat.json")).read_text(encoding="utf-8"))
        assert blob["refused"] == "codex_budget_weekly"
        assert blob["codex_usage"]["secondary_used_percent"] == 77.0
        assert "week" in blob["refused_detail"][0]
    finally:
        for p in sorted(d.rglob("*"), reverse=True):
            p.unlink()
        d.rmdir()


def test_review_refuses_before_it_spends_the_call(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", str(_fixture_home(tmp_path, 96.0, 1.0)))

    def _never(argv, **kw):
        raise AssertionError("a refused seat must not run codex")

    monkeypatch.setattr(seat, "_run", _never)
    monkeypatch.setattr(seat, "codex_path", lambda: "codex")
    brief = tmp_path / "brief.md"
    brief.write_text("Read the charter and answer FOLLOWS or not.\n",
                     encoding="utf-8")
    out = tmp_path / "review.md"
    assert seat.main(["review", str(brief), "--out", str(out)]) == 1
    rec = json.loads(out.with_suffix(".usage.json").read_text(encoding="utf-8"))
    assert rec["primary_used_percent"] == 96.0


def test_a_seat_under_the_line_still_reaches_codex(tmp_path, monkeypatch):
    """The guard has to let the normal case through, or it is just an off switch."""
    monkeypatch.setenv("CODEX_HOME", str(_fixture_home(tmp_path, 3.0, 11.0)))

    reached: list[str] = []

    def _stop(argv, **kw):
        reached.append("codex")
        raise SystemExit(0)

    monkeypatch.setattr(seat, "_run", _stop)
    monkeypatch.setattr(seat, "codex_path", lambda: "codex")
    brief = tmp_path / "brief.md"
    brief.write_text("Read the charter and answer FOLLOWS or not.\n",
                     encoding="utf-8")
    with pytest.raises(SystemExit):
        seat.main(["review", str(brief), "--out", str(tmp_path / "r.md")])
    assert reached == ["codex"]


def test_both_budget_reasons_have_prose_in_the_refusal_table():
    for reason in ("codex_budget_primary", "codex_budget_weekly"):
        assert reason in seat.REFUSAL_REASONS
        assert len(seat.REFUSAL_REASONS[reason]) > 20
