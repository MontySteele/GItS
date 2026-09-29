"""A lane holds one game: an embark beside a game an earlier embark left up is
refused, naming the stamp to tear down (Varka seat, lane 1, 2026-09-29).

The live failure: embark `145523` was never reverted, its game sat on
`game_over` holding lane 1's port, and the next embark launched a second game
that could not bind it -- the boot watch read the old game's `game_over`
until it gave up. Nothing here launches a game.
"""

from __future__ import annotations

import json

import pytest

from understudy import embark, soak


def _embark_on_disk(tmp_path, stamp, lane, state="APPLIED", pid=27116,
                    hold=False):
    ledger = tmp_path / f"rev-{stamp}.json"
    ledger.write_text(json.dumps([
        {"n": 1, "change": "Launched `SlayTheSpire2.exe` directly",
         "state": state, "pid": pid},
    ]), encoding="utf-8")
    (tmp_path / f"embark-{stamp}.json").write_text(json.dumps({
        "stamp": stamp, "ledger": str(ledger), "instance": lane,
        "hold": hold}), encoding="utf-8")


def _alive(*pids):
    return lambda pid: "SlayTheSpire2.exe" if pid in pids else None


def test_a_live_untorn_launch_on_the_lane_is_found(tmp_path, monkeypatch):
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "pid_image", _alive(27116))
    _embark_on_disk(tmp_path, "20260929-145523", "lane1")
    assert embark.live_launch_on_lane("lane1") == ("20260929-145523", 27116)
    # Another lane's game is not this lane's business.
    assert embark.live_launch_on_lane("lane2") is None


def test_a_reverted_or_dead_launch_is_not_counted(tmp_path, monkeypatch):
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "pid_image", _alive(27116))
    _embark_on_disk(tmp_path, "20260929-145523", "lane1", state="REVERTED")
    _embark_on_disk(tmp_path, "20260929-150609", "lane1", pid=43264)
    assert embark.live_launch_on_lane("lane1") is None


def test_an_unreadable_probe_does_not_block(tmp_path, monkeypatch):
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "pid_image", lambda pid: "<pid probe failed>")
    _embark_on_disk(tmp_path, "20260929-145523", "lane1")
    assert embark.live_launch_on_lane("lane1") is None


def test_the_embark_refuses_and_names_the_stamp(tmp_path, monkeypatch):
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "pid_image", _alive(27116))
    _embark_on_disk(tmp_path, "20260929-145523", "lane1")
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.embark("varka", lane=1)
    msg = str(excinfo.value)
    assert "--teardown --lane 1 --stamp 20260929-145523" in msg
    assert "27116" in msg
    # Refused before anything is written: no new sidecar.
    assert len(list(tmp_path.glob("embark-*.json"))) == 1
