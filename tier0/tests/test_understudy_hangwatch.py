"""EB-1's watchdog, tested without hanging a game.

The failure this defends against takes half an hour to produce by hand, poisons
a save, and writes 2.4 GB to disk on the way. So the judgment has to be right
the first time it fires, unattended, and every OS-touching call in
`understudy/hangwatch.py` is injected so that judgment can be exercised here
instead of live.

NOTHING BELOW IS EVIDENCE ABOUT THE GAME. It is evidence about whether the
watchdog can tell three failures apart: a game that exited, a game that is
alive and silently spinning, and a wire that simply did not answer.
"""

from __future__ import annotations

import pytest

from understudy import hangwatch, soak

from . import test_understudy_soak as ts


def _raises_bridge_error(message):
    def _go():
        raise soak.bridge.BridgeError(message)
    return _go


# The observed EB-1 rate: 2.4 GB in ~30 minutes.
LIVE_FLOOD_BYTES_PER_S = 2_400_000_000 / (30 * 60)


def _probe(start=0, end=0, elapsed=4.0, responding=(True, True, True, True),
           path="godot.log"):
    return hangwatch.Probe(log_path=path, log_bytes_start=start,
                           log_bytes_end=end, elapsed_s=elapsed,
                           responding=tuple(responding))


# ------------------------------------------------------------- the rate ----

def test_the_live_flood_rate_is_comfortably_over_the_bar():
    """The bar is set from one live observation, so the observation is the
    test. 2.4 GB in 30 minutes is ~1.33 MB/s; a threshold it did not clear
    would be a watchdog that watched the wrong thing."""
    assert LIVE_FLOOD_BYTES_PER_S > hangwatch.FLOOD_BYTES_PER_S * 4


def test_an_ordinary_log_trickle_is_not_a_flood():
    p = _probe(start=1_000_000, end=1_012_000, elapsed=4.0)   # 3 KB/s
    assert p.log_bytes_per_s == pytest.approx(3000.0)
    v = hangwatch.classify(p, alive=True, wire_dead=True)
    assert not v.hung
    assert "bridge_unreachable" in v.reason


def test_a_rotated_log_reads_as_no_reading_rather_than_a_negative_rate():
    """The game writes a fresh `godot.log` per launch. A shrinking file is the
    watchdog looking at a different file, not a flood running backwards, and a
    negative rate would silently satisfy `< threshold` forever."""
    assert _probe(start=2_000_000, end=5_000).log_bytes_per_s is None


def test_a_log_nobody_could_read_removes_the_signal_instead_of_faking_a_zero():
    p = hangwatch.Probe(log_path=None, log_bytes_start=None,
                        log_bytes_end=None, elapsed_s=4.0,
                        responding=(None, None))
    assert p.log_bytes_per_s is None
    v = hangwatch.classify(p, alive=True, wire_dead=True)
    assert not v.hung, "an unreadable log must not become a defect"


# ---------------------------------------------------------- the verdict ----

def test_the_live_signature_is_classified_as_a_spin():
    p = _probe(start=0, end=int(LIVE_FLOOD_BYTES_PER_S * 4), elapsed=4.0,
               responding=(False, False, False, False))
    v = hangwatch.classify(p, alive=True, wire_dead=True)
    assert v.hung
    assert len(v.signals) == 2, v.signals
    assert "abandon_run" in v.reason, "the recovery is part of the finding"


def test_a_flood_alone_is_enough_when_the_process_status_is_unknown():
    """A machine that cannot answer `tasklist` still has the loud half of the
    signature, and a watchdog that needed both would be off on that machine."""
    p = _probe(start=0, end=4_000_000, elapsed=4.0,
               responding=(None, None, None, None))
    v = hangwatch.classify(p, alive=True, wire_dead=True)
    assert v.hung and len(v.signals) == 1


def test_not_responding_alone_is_enough_when_the_log_is_unknown():
    p = hangwatch.Probe(log_path=None, elapsed_s=4.0,
                        responding=(False, False, False))
    v = hangwatch.classify(p, alive=True, wire_dead=True)
    assert v.hung and len(v.signals) == 1


def test_one_not_responding_sample_in_a_window_is_a_slow_frame_not_a_hang():
    """This is the false positive that would get the watchdog turned off: a
    long room load also stops pumping messages for a moment. Every sampled
    tick has to agree."""
    p = _probe(responding=(False, True, False, False))
    assert not hangwatch.classify(p, alive=True, wire_dead=True).hung


def test_a_single_sample_is_never_enough_on_its_own():
    p = hangwatch.Probe(log_path=None, elapsed_s=1.0, responding=(False,))
    assert not hangwatch.classify(p, alive=True, wire_dead=True).hung


def test_a_wire_that_answered_is_not_a_hang_however_loud_the_log_is():
    p = _probe(start=0, end=100_000_000, elapsed=4.0,
               responding=(False, False, False))
    v = hangwatch.classify(p, alive=True, wire_dead=False)
    assert not v.hung and "answered" in v.reason


def test_an_exited_process_is_left_to_process_died():
    """Two kinds competing for one failure is how a defect table stops being
    readable. `Session.died` already owns the grace period that makes this
    question answerable."""
    p = _probe(start=0, end=100_000_000, elapsed=4.0,
               responding=(False, False, False))
    v = hangwatch.classify(p, alive=False, wire_dead=True)
    assert not v.hung and "process_died" in v.reason


def test_the_evidence_carries_the_two_byte_counts_that_produced_the_rate():
    """A defect record whose rate cannot be re-derived is a number nobody can
    check, which is the one thing this house does not ship."""
    ev = _probe(start=10, end=4_000_010, elapsed=4.0).as_evidence()
    assert ev["log_bytes_start"] == 10 and ev["log_bytes_end"] == 4_000_010
    assert ev["elapsed_s"] == 4.0
    assert ev["log_bytes_per_s"] == pytest.approx(1_000_000.0)
    assert ev["flood_threshold_bytes_per_s"] == hangwatch.FLOOD_BYTES_PER_S


# ---------------------------------------------------------- the sampler ----

def test_the_sampler_takes_the_sizes_around_the_whole_window():
    sizes = iter([1_000, 9_000_000])
    ticks = iter([100.0, 104.0])
    p = hangwatch.sample(
        hangwatch.Path("x.log"), "GAME.exe", samples=5, interval=1.0,
        sizer=lambda _p: next(sizes), responder=lambda _n: False,
        sleep=lambda _s: None, clock=lambda: next(ticks))
    assert p.log_bytes_start == 1_000 and p.log_bytes_end == 9_000_000
    assert p.elapsed_s == 4.0
    assert len(p.responding) == 5


def test_the_sampler_never_takes_fewer_than_two_status_reads():
    """One read cannot distinguish a hang from a frame, and `classify` refuses
    a lone sample -- so a caller asking for one must not be able to produce a
    window that silently cannot fire."""
    p = hangwatch.sample(None, "GAME.exe", samples=1, interval=0,
                         sizer=lambda _p: None, responder=lambda _n: False,
                         sleep=lambda _s: None, clock=lambda: 0.0)
    assert len(p.responding) >= 2


# -------------------------------------------------- the tasklist reading ----

@pytest.mark.parametrize("out, expected", [
    ("", True),
    ("INFO: No tasks are running which match the specified criteria.", True),
    ("SlayTheSpire2.exe   12345 Console   1   1,234,567 K", False),
    ("some future format nobody here has seen", None),
])
def test_the_status_query_is_read_conservatively(out, expected):
    assert hangwatch.windows_responding(
        "SlayTheSpire2.exe", query=lambda _n: out) is expected


def test_a_status_query_that_raises_is_unknown_and_not_a_hang():
    def boom(_name):
        raise OSError("tasklist is not on this machine")
    assert hangwatch.windows_responding("X.exe", query=boom) is None


def test_the_log_path_is_overridable_and_never_guessed():
    assert hangwatch.default_log_path({"GITS_GODOT_LOG": "D:/elsewhere.log"}) \
        == hangwatch.Path("D:/elsewhere.log")
    assert hangwatch.default_log_path({}) is None


# ------------------------------------------------- wired into the driver ----

def test_a_spin_is_filed_under_its_own_kind_and_not_the_harness_side_one(
        monkeypatch):
    """The whole point of the leg. Before it, a spinning game was filed as
    `bridge_unreachable` -- a HARNESS-side kind -- so the instrument blamed its
    own wire for a build defect it had just caught, and two of them halted the
    soak on the wrong diagnosis."""
    d = ts._driver()
    filed = {}
    d.file_defect = lambda kind, detail, state, extra=None: filed.update(
        kind=kind, detail=detail, extra=extra or {})
    d.session.died = lambda: False
    d.session.halt_spin = lambda why: {"killed": True, "why": why}
    monkeypatch.setattr(
        soak.hangwatch, "diagnose",
        lambda *a, **k: hangwatch.classify(
            _probe(start=0, end=8_000_000, elapsed=4.0,
                   responding=(False, False, False)),
            alive=True, wire_dead=True))
    monkeypatch.setattr(d, "_to_main_menu",
                        _raises_bridge_error("bridge unreachable"))

    summary = d.run()

    assert filed["kind"] == hangwatch.DEFECT_KIND == "unresponsive_spin"
    assert filed["extra"]["teardown"] == {"killed": True,
                                          "why": "unresponsive_spin at run 1"}
    assert filed["extra"]["hangwatch"]["log_bytes_end"] == 8_000_000
    assert summary["outcome"] == "defect"


def test_a_quiet_dead_wire_is_still_bridge_unreachable(monkeypatch):
    """The fallback is the old behaviour, unchanged. A watchdog that renamed
    every unreachable bridge would be worse than none."""
    d = ts._driver()
    filed = {}
    d.file_defect = lambda kind, detail, state, extra=None: filed.update(
        kind=kind)
    d.session.died = lambda: False
    monkeypatch.setattr(
        soak.hangwatch, "diagnose",
        lambda *a, **k: hangwatch.classify(_probe(), alive=True,
                                           wire_dead=True))
    monkeypatch.setattr(d, "_to_main_menu",
                        _raises_bridge_error("timed out"))

    d.run()
    assert filed["kind"] == "bridge_unreachable"


def test_a_probe_that_raises_falls_back_rather_than_becoming_an_exception(
        monkeypatch):
    d = ts._driver()

    def boom(*_a, **_k):
        raise RuntimeError("the probe itself broke")

    monkeypatch.setattr(soak.hangwatch, "diagnose", boom)
    v = d._diagnose_spin()
    assert not v.hung and "falling back" in v.reason


def test_the_two_new_kinds_are_not_on_the_harness_side_of_the_line():
    """Both are the soak CATCHING EB-1, which is the soak working. Putting
    either in `_HARNESS_SIDE` would halt a night on the second observation of
    a live-play hazard."""
    assert hangwatch.DEFECT_KIND not in soak._HARNESS_SIDE
    assert "hazard_event" not in soak._HARNESS_SIDE


# ------------------------------------------------- the hazard register ----

def _event(event_id="SOMETHING_HARMLESS", name="Something Harmless"):
    return {"state_type": "event", "run": {"act": 1, "floor": 7},
            "player": {"hp": 50, "max_hp": 71},
            "event": {"event_id": event_id, "event_name": name,
                      "in_dialogue": False,
                      "options": [{"index": 0, "is_locked": False}]}}


def test_the_punch_off_room_is_refused_rather_than_answered():
    """EB-1. `PunchOff` fires `PunchEachOther()` from `AfterEventStarted()`, so
    the hazard is entry and no option avoids it -- and the frozen frame carried
    no options to pick from anyway. Stopping the run is the whole defence: the
    save is poisoned, and the restart path's `abandon_run` is the recorded
    recovery."""
    d = ts._driver()
    with pytest.raises(soak.Defect) as exc:
        d._check(_event("PUNCH_OFF", "Punch Off"))
    assert exc.value.kind == "hazard_event"
    assert "EB-1" in exc.value.detail


def test_the_wire_id_is_matched_case_and_whitespace_insensitively():
    d = ts._driver()
    with pytest.raises(soak.Defect):
        d._check(_event(" punch_off ", "whatever"))


def test_the_display_title_is_the_second_reading():
    """An id is the thing itself and a title is loc data, so the id is matched
    first -- but a screen this harness must not drive is worth catching twice,
    and a bridge that ever reported the title in the id slot should still
    stop."""
    d = ts._driver()
    with pytest.raises(soak.Defect) as exc:
        d._check(_event(event_id="", name="Punch  Off"))
    assert exc.value.kind == "hazard_event"


def test_an_ordinary_event_is_driven_exactly_as_before():
    d = ts._driver()
    d._check(_event())                       # no raise
    assert soak._mechanical_action(_event()) == {
        "action": "choose_event_option", "index": 0}


def test_a_non_event_screen_named_like_one_is_not_a_hazard():
    """The register is keyed on the EVENT screen. A map node, a reward, a card
    whose title collides -- none of those is the room."""
    state = dict(_event("PUNCH_OFF", "Punch Off"))
    state["state_type"] = "map"
    assert soak._hazard_event(state) is None


def test_the_guard_can_be_turned_off_for_a_deliberate_reproduction():
    """`--allow-hazard-events`. A defence that cannot be lifted is a defence
    that makes the hazard unreproducible, and EB-1 stays open precisely because
    it is a live-play hazard somebody may need to look at again."""
    d = ts._driver()
    d.hazard_guard = False
    d._check(_event("PUNCH_OFF", "Punch Off"))      # no raise
