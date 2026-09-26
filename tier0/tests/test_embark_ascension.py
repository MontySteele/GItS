"""`embark --ascension N`: the chosen-ascension plumbing, pinned offline.

The endpoint is `vendor/STS2_MCP/gits/GitsAscension.cs`. These tests pin this
side of the socket: the request's shape, the moment it is posted (after the
character pick, before the confirm), the refusal when the lobby or the run
reads back another level, and that an embark without the flag asks for
nothing. Whether the game honours it is a live measurement.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from understudy import bridge, embark, soak
from understudy.soak_shape import Defect


class _StubSession:
    def note_seed_channel(self):
        pass


def _fake(report_for=None):
    from tier0.tests import test_understudy_soak as ts

    fake = ts._FakeBridge()
    calls: list[str] = []

    def set_ascension(n):
        calls.append(f"set_ascension:{n}")
        if report_for is not None:
            return report_for(n)
        return {"status": "ok", "route": "panel", "lobby_ascension": n,
                "max": 10}

    fake.set_ascension = set_ascension
    fake.get_ascension = lambda: {"status": "ok", "lobby_ascension": 5}
    real_post = fake.post
    fake.post = lambda action, **p: (
        calls.append(f"post:{str(p.get('option', action)).lower()}")
        or real_post(action, **p))
    return fake, calls


def _drive(monkeypatch, fake, ascension):
    from tier0.tests import test_understudy_soak as ts

    monkeypatch.setattr(soak, "bridge", fake)
    monkeypatch.setattr(soak, "SETTLE_S", 0)
    d = ts._driver()
    d.session = _StubSession()
    if ascension is not None:
        d.chosen_ascension = ascension
    d._embark(fake.get_state())
    return d


# ----------------------------------------------------------- the wire ------

def test_set_ascension_posts_the_level_to_the_gits_endpoint(monkeypatch):
    seen = {}

    def fake(url, payload=None, timeout=20.0):
        seen["url"], seen["payload"] = url, payload
        return {"status": "ok", "lobby_ascension": 0}

    monkeypatch.setattr(bridge, "_request", fake)
    assert bridge.set_ascension(0)["lobby_ascension"] == 0
    assert seen["url"] == bridge.ASCENSION
    assert seen["payload"] == {"ascension": 0}
    assert json.dumps(seen["payload"]) == '{"ascension": 0}'


def test_get_ascension_is_a_bare_get(monkeypatch):
    seen = {}
    monkeypatch.setattr(bridge, "_request",
                        lambda url, payload=None, timeout=20.0:
                        seen.update(url=url, payload=payload) or {})
    bridge.get_ascension()
    assert seen == {"url": bridge.ASCENSION, "payload": None}


def test_the_endpoint_is_the_forked_bridges():
    assert bridge.ASCENSION.endswith("/api/v1/gits/ascension")


# ------------------------------------------------------- the navigation ----

def test_the_ascension_is_set_after_the_character_and_before_the_confirm(
        monkeypatch):
    """Picking a character resets the level to its saved PreferredAscension
    (`StartRunLobby.SetSingleplayerAscensionAfterCharacterChanged`), and the
    confirm reads the lobby's level: there is one moment that works."""
    fake, calls = _fake()
    _drive(monkeypatch, fake, 0)
    assert "set_ascension:0" in calls
    assert calls.index("post:kleemod-furina") < calls.index("set_ascension:0")
    assert calls.index("set_ascension:0") < calls.index("post:confirm")


def test_without_the_flag_no_ascension_is_asked_for(monkeypatch):
    fake, calls = _fake()
    d = _drive(monkeypatch, fake, None)
    assert d.chosen_ascension is None
    assert not [c for c in calls if c.startswith("set_ascension")]


def test_a_lobby_that_reads_another_level_is_a_defect(monkeypatch):
    fake, calls = _fake(lambda n: {"status": "ok", "route": "panel",
                                   "lobby_ascension": 5})
    with pytest.raises(Defect) as excinfo:
        _drive(monkeypatch, fake, 0)
    assert excinfo.value.kind == "ascension_not_honoured"
    assert "post:confirm" not in calls


def test_a_refused_level_is_a_defect(monkeypatch):
    fake, calls = _fake(lambda n: {"status": "error",
                                   "error": "Ascension 20 is above this "
                                            "character's maximum of 5"})
    with pytest.raises(Defect) as excinfo:
        _drive(monkeypatch, fake, 20)
    assert excinfo.value.kind == "ascension_not_honoured"
    assert "maximum of 5" in excinfo.value.detail
    assert "post:confirm" not in calls


def test_ascension_not_honoured_is_a_harness_side_defect():
    assert "ascension_not_honoured" in soak._HARNESS_SIDE


# ------------------------------------------------------------ the embark ---

class _Session:
    def __init__(self, stamp, do_setup=True, intent=None, instance=None,
                 install_bridge=True):
        self.instance = instance
        self.ledger = soak.Reversibility(Path("rev.json"))

    def setup(self):
        pass


def _spy_driver(read_back):
    class _Driver:
        character_actual = "The Silent"
        log = Path("run.jsonl")
        kwargs: dict = {}

        def __init__(self, *a, **kw):
            type(self).kwargs = kw

        def _to_main_menu(self):
            return {"state_type": "menu"}

        def _embark(self, state):
            return state

        def _verify_character(self, state):
            return {"state_type": "map",
                    "run": {"floor": 1, "ascension": read_back}}

    return _Driver


def _stubs(tmp_path, monkeypatch, read_back):
    driver = _spy_driver(read_back)
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "Session", _Session)
    monkeypatch.setattr(soak, "RunDriver", driver)
    monkeypatch.setattr(bridge, "seed_read_back", lambda: "SEEDSEED")
    return driver


def test_the_embark_threads_the_level_and_records_the_request(tmp_path,
                                                              monkeypatch):
    driver = _stubs(tmp_path, monkeypatch, 0)
    blob = embark.embark("SILENT", chosen_ascension=0)
    assert driver.kwargs["chosen_ascension"] == 0
    assert blob["ascension_requested"] == 0
    assert blob["ascension"] == 0
    on_disk = json.loads(
        (tmp_path / f"embark-{blob['stamp']}.json").read_text(encoding="utf-8"))
    assert on_disk["ascension_requested"] == 0


def test_an_embark_without_the_flag_records_no_request(tmp_path, monkeypatch):
    driver = _stubs(tmp_path, monkeypatch, 5)
    blob = embark.embark("SILENT")
    assert driver.kwargs["chosen_ascension"] is None
    assert "ascension_requested" not in blob
    assert blob["ascension"] == 5


def test_a_run_that_reads_back_another_level_fails_the_embark(tmp_path,
                                                             monkeypatch):
    _stubs(tmp_path, monkeypatch, 5)
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.embark("SILENT", chosen_ascension=0)
    assert str(excinfo.value).startswith("ascension_not_honoured")
    # The mismatch is on the record before the refusal.
    (sidecar,) = tmp_path.glob("embark-*.json")
    blob = json.loads(sidecar.read_text(encoding="utf-8"))
    assert (blob["ascension_requested"], blob["ascension"]) == (0, 5)


def test_the_cli_flag_reaches_the_embark(monkeypatch, capsys):
    seen = {}
    monkeypatch.setattr(soak, "lane_setup", lambda v: (None, True))
    monkeypatch.setattr(embark, "embark", lambda *a, **k: seen.update(k) or {
        "stamp": "S", "instance": "lane0", "character_actual": "The Silent",
        "run_seed": "ABC", "screen": "map", "floor": 1, "ascension": 0})
    assert embark.main(["--character", "SILENT", "--ascension", "0"]) == 0
    assert seen["chosen_ascension"] == 0


def test_the_cli_default_asks_for_no_level(monkeypatch, capsys):
    seen = {}
    monkeypatch.setattr(soak, "lane_setup", lambda v: (None, True))
    monkeypatch.setattr(embark, "embark", lambda *a, **k: seen.update(k) or {
        "stamp": "S", "instance": "lane0", "character_actual": "The Silent",
        "run_seed": "ABC", "screen": "map", "floor": 1})
    assert embark.main(["--character", "SILENT"]) == 0
    assert seen["chosen_ascension"] is None
