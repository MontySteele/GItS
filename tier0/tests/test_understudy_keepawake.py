"""EB-226: the power request is taken, given back, and never left dangling.

The subject is a `ctypes` call into `kernel32`, so what is actually asserted
everywhere below is THE FLAG SEQUENCE a fake setter recorded. That is the
whole observable behaviour: `ES_CONTINUOUS | ES_SYSTEM_REQUIRED` on the way
in, a bare `ES_CONTINUOUS` on the way out, on one thread, exactly once each
however many holders there were.
"""

from __future__ import annotations

import threading

import pytest

from understudy import keepawake


class _Recorder:
    """A stand-in for `SetThreadExecutionState` that remembers everything."""

    def __init__(self, raises: BaseException | None = None):
        self.flags: list[int] = []
        self.threads: list[int] = []
        self.raises = raises

    def __call__(self, flags: int) -> int:
        self.flags.append(flags)
        self.threads.append(threading.get_ident())
        if self.raises is not None:
            raise self.raises
        return 1


def _request(rec, log=None):
    return keepawake.PowerRequest(set_state=rec, log=log or (lambda _m: None))


def test_acquire_then_release_is_hold_then_free():
    rec = _Recorder()
    req = _request(rec)
    assert req.acquire("a run") is True
    assert rec.flags == [keepawake.ES_HOLD]
    assert req.held is True
    assert req.release() is True
    assert rec.flags == [keepawake.ES_HOLD, keepawake.ES_FREE]
    assert req.held is False


def test_the_hold_and_the_release_run_on_one_thread_and_not_the_caller():
    """The flags are per-THREAD, so both calls must land on the same one.

    And it must not be the caller's: `Session.setup` and `Session.teardown`
    reach this from different lane workers, and a request set on a worker
    that later exits is released by the OS behind the harness's back.
    """
    rec = _Recorder()
    req = _request(rec)
    req.acquire()
    req.release()
    assert len(set(rec.threads)) == 1
    assert rec.threads[0] != threading.get_ident()


def test_the_context_manager_releases_when_the_body_raises():
    rec = _Recorder()
    req = _request(rec)
    with pytest.raises(ValueError):
        with req.holding("a run that dies"):
            assert rec.flags == [keepawake.ES_HOLD]
            raise ValueError("the run blew up mid-fight")
    assert rec.flags == [keepawake.ES_HOLD, keepawake.ES_FREE]
    assert req.held is False


def test_two_holders_take_one_request_and_the_first_release_keeps_it():
    """A two-lane round is two sessions and ONE machine."""
    rec = _Recorder()
    req = _request(rec)
    assert req.acquire("lane0") is True
    assert req.acquire("lane1") is False       # already held
    assert rec.flags == [keepawake.ES_HOLD]
    assert req.holders == 2
    assert req.release() is False              # lane 0 went home first
    assert rec.flags == [keepawake.ES_HOLD]    # lane 1 is still playing
    assert req.release() is True
    assert rec.flags == [keepawake.ES_HOLD, keepawake.ES_FREE]


def test_an_unmatched_release_is_a_no_op_and_never_underflows():
    rec = _Recorder()
    req = _request(rec)
    assert req.release() is False
    assert req.holders == 0
    assert rec.flags == []


def test_no_kernel32_is_one_logged_line_and_a_no_op():
    lines: list[str] = []
    req = keepawake.PowerRequest(probe=lambda: None, log=lines.append)
    assert req.acquire("a run") is False
    assert req.held is False
    assert len(lines) == 1 and "not available" in lines[0]
    # The second acquire says nothing new -- a soak that opens forty sessions
    # would otherwise print forty identical lines.
    assert req.acquire("another") is False
    assert len(lines) == 1
    assert req.release() is False


def test_a_setter_that_raises_is_logged_and_does_not_hang_the_acquire():
    rec = _Recorder(raises=OSError("kernel32 said no"))
    lines: list[str] = []
    req = _request(rec, log=lines.append)
    req.acquire("a run")                        # must return, not block
    req.release()
    assert rec.flags == [keepawake.ES_HOLD]     # it never got to the release
    assert any("refused by the OS" in ln for ln in lines)


def test_the_flag_constants_are_the_windows_values():
    assert keepawake.ES_CONTINUOUS == 0x80000000
    assert keepawake.ES_SYSTEM_REQUIRED == 0x00000001
    assert keepawake.ES_HOLD == 0x80000001
    assert keepawake.ES_FREE == 0x80000000
    # NOT display-required: the run needs the CPU, not the monitor.
    assert keepawake.ES_HOLD & 0x00000002 == 0


def test_a_non_windows_process_never_touches_ctypes(monkeypatch):
    monkeypatch.setattr(keepawake.sys, "platform", "linux")
    assert keepawake.kernel32_setter() is None


# ------------------------------------------------------- the wiring --------

def test_a_soak_session_holds_the_request_from_setup_to_teardown(monkeypatch):
    """The claim EB-226 actually makes: the hold spans the game, not a call."""
    from understudy import soak

    events: list[str] = []
    monkeypatch.setattr(keepawake, "acquire",
                        lambda reason="": events.append(f"acquire {reason}"))
    monkeypatch.setattr(keepawake, "release",
                        lambda: events.append("release"))

    s = soak.Session.__new__(soak.Session)
    s.stamp = "20260830-000000"
    s.do_setup = False
    s.instance = None
    s.wire = lambda: None
    s._require_bridge = lambda: None
    s.setup()
    assert events == ["acquire session 20260830-000000"]

    s.ledger = None
    for attr in ("_seed_entry", "_speed_entry", "_launch_entry",
                 "_bridge_entry", "_appid_entry"):
        setattr(s, attr, None)
    s.teardown()
    assert events == ["acquire session 20260830-000000", "release"]


def test_a_session_that_never_set_up_releases_nothing(monkeypatch):
    from understudy import soak

    events: list[str] = []
    monkeypatch.setattr(keepawake, "release",
                        lambda: events.append("release"))
    s = soak.Session.__new__(soak.Session)
    s.wire = lambda: None
    for attr in ("_seed_entry", "_speed_entry", "_launch_entry",
                 "_bridge_entry", "_appid_entry"):
        setattr(s, attr, None)
    s.teardown()
    assert events == []
