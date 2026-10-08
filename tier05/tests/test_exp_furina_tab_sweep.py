"""The Salon's Tab sweep (`tier05.exp_furina_tab_sweep`) reads the runs it
claims to: its `always` cell is the unpatched run, and its `never` cell
declines every Drain mode it is offered."""

from __future__ import annotations

import pytest

from tier0.engine import furina_stage as FS
from tier05 import draft, model
from tier05 import exp_furina_tab_sweep as S

SEED, RUNS = 11, 2


@pytest.fixture
def restore(monkeypatch):
    # The sweep patches these in its worker; serial here, so put them back.
    monkeypatch.setattr(model, "run_fight", model.run_fight)
    monkeypatch.setattr(FS, "FURINA_TIDE_DECIDER", FS.FURINA_TIDE_DECIDER)
    monkeypatch.setattr(model._RunCtx, "_sweep_fights", [], raising=False)


def test_always_cell_is_the_unpatched_run(restore):
    plain = [model.run_one("furina", "salon", "salon",
                           draft.POLICIES["adaptive"], SEED + i,
                           grant_relics=True, grant_potions=True)
             for i in range(RUNS)]
    swept = S.run_cell("furina", "adaptive", "hunter", "always", RUNS, SEED,
                       jobs=1)
    assert [r["won"] for r in swept] == [r.won for r in plain]
    assert [r["acts_completed"] for r in swept] == [
        r.acts_completed for r in plain]
    assert [len(r["fights"]) for r in swept] == [
        len(r.fight_stats) for r in plain]
    row = S.summarize(swept)
    assert row["k3"]["taken_of_legal"] == 1.0


def test_never_cell_declines_every_drain_mode(restore):
    swept = S.run_cell("furina", "adaptive", "hunter", "never", RUNS, SEED,
                       jobs=1)
    fights = [f for r in swept for f in r["fights"]]
    assert sum(f["drain_offers"] for f in fights) > 0
    assert sum(f["drain_taken"] for f in fights) == 0
