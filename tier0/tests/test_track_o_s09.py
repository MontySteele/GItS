"""Track O / slice 9 — pins around the soak driver's `unexpected_start_state`.

WHAT IS PINNED HERE AND WHY ONLY THIS MUCH. The red-team pass that produced
this file found several places where a soak whose runs died at the start line
still reports numbers as though they had run (the fixtures under
`review/redteam/fixtures/track_o/s09-*` reproduce them, and
`docs`/the slice report name them). Those are wrong numbers, not settled
behaviour, so nothing below asserts them: a test that pinned them would make
the defect load-bearing.

What IS pinned is the behaviour the source states unambiguously about itself:

  * `understudy/soak.py:1103-1108` — a run that opens on a non-menu screen is a
    STOP-AND-SURFACE, filed under the kind `unexpected_start_state`;
  * `understudy/soak.py:1596-1603` — that kind is HARNESS-side, i.e. the
    instrument failing rather than the build;
  * `understudy/soak.py:1567-1579` — a DEFECT run is not trusted to leave a
    clean state, so the session is restarted before the next run;
  * `understudy/soak.py:457-461` — the record schema is a shared surface, so
    the defect record's key set is a contract other readers rely on.

These pass today. They exist so that a fix to the reporting side cannot quietly
take the stop-and-surface itself away.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from understudy import soak

FIXTURES = (Path(__file__).resolve().parents[2]
            / "review" / "redteam" / "fixtures" / "track_o")
PARKED = FIXTURES / "s09-b3-parked-state.json"


class _FakeSession:
    """Only the surface `RunDriver` touches on the failure path."""
    exit_code = None

    def alive(self) -> bool:
        return True

    def died(self, grace: float = 0.0) -> bool:
        return False


class _FakeBridge:
    BridgeError = Exception

    def __init__(self, state: dict) -> None:
        self.state = state

    def get_state(self) -> dict:
        return dict(self.state)

    def post(self, **kw):                       # pragma: no cover - guard
        raise AssertionError("no action may be posted from a parked screen")

    def current_seed(self):                     # pragma: no cover - guard
        raise AssertionError("the run must not reach the seed read-back")


@pytest.fixture()
def parked_run(tmp_path, monkeypatch):
    """Drive a real `RunDriver` whose first state read is the parked screen."""
    state = json.loads(PARKED.read_text(encoding="utf-8"))
    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "bridge", _FakeBridge(state))
    driver = soak.RunDriver(_FakeSession(), 2, "20260805-130311",
                            "KLEEMOD-FURINA", commit=None,
                            chosen_seed="TRACKB3B", max_fights=4)
    summary = driver.run()
    return driver, summary


def test_parked_screen_is_a_stop_and_surface(parked_run):
    """A non-menu screen at run start ends the run; it is never driven from."""
    driver, summary = parked_run
    assert summary["outcome"] == "defect"
    assert summary["actions"] == 0
    assert summary["fights"] == 0
    assert [d["kind"] for d in driver.defects] == ["unexpected_start_state"]
    assert "found 'rewards'" in driver.defects[0]["detail"]


def test_unexpected_start_state_is_harness_side():
    """soak.py:1596-1603 states the classification; readers branch on it."""
    assert "unexpected_start_state" in soak._HARNESS_SIDE


def test_defect_record_keeps_its_declared_key_set(parked_run):
    """The record schema is a shared surface (soak.py:457-461)."""
    driver, _ = parked_run
    rec = driver.defects[0]
    for key in ("record", "kind", "detail", "seed", "run", "act", "floor",
                "state_type", "actions_taken", "proc_exit_code",
                "state_dump", "recent"):
        assert key in rec, key
    assert rec["record"] == "defect"


def test_the_defect_run_is_written_to_its_own_log(parked_run, tmp_path):
    """Every run leaves a log even when it never embarked -- the run_begin /
    defect / run_end triple is what `understudy/report.py` reads."""
    driver, _ = parked_run
    lines = [json.loads(x) for x
             in driver.log.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert [r["record"] for r in lines] == ["run_begin", "defect", "run_end"]


def test_a_defect_run_forces_a_session_restart(tmp_path, monkeypatch):
    """soak.py:1567-1579: a defect run is not trusted to leave a clean state.

    Driven through the real `soak()` loop with a scripted session and driver,
    so the restart GATE is the thing under test rather than a paraphrase of it.
    """
    events: list[str] = []

    class _Ledger:
        entries: list = []

        def table(self) -> str:
            return "(none)"

    class _Session:
        ledger = _Ledger()

        def __init__(self, stamp, do_setup=True, intent=None):
            pass

        def setup(self):
            pass

        def restart(self):
            events.append("restart")

        def teardown(self):
            pass

        def alive(self):
            return True

    class _Driver:
        character_actual = None          # EB-117: read back, never requested

        def __init__(self, session, run_index, stamp, character, commit=None,
                     chosen_seed=None, max_fights=None, hazard_guard=True):
            self.run_index = run_index
            self.chosen_seed = chosen_seed
            self.defects = ([{"kind": "unexpected_start_state"}]
                            if run_index == 1 else [])

        def run(self):
            defective = self.run_index == 1
            return {"record": "run_end",
                    "outcome": "defect" if defective else "died",
                    "detail": "", "seed": None if defective else self.chosen_seed,
                    "run": self.run_index, "actions": 0 if defective else 200,
                    "wall_s": 0.3, "fights": 0 if defective else 3,
                    "final_act": None if defective else 1,
                    "final_floor": None if defective else 6,
                    "defects": len(self.defects), "forced_defaults": 0,
                    "log": "x"}

    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "Session", _Session)
    monkeypatch.setattr(soak, "RunDriver", _Driver)
    monkeypatch.setattr(soak.deckwatch, "reset", lambda: None)

    result = soak.soak(runs=2, character="KLEEMOD-FURINA", do_setup=True,
                       seeds=["S1", "S2"], max_fights=None)
    assert events == ["restart"], "a defect run must be followed by a restart"
    assert result["stopped_on"] is None
    assert len(result["runs"]) == 2
