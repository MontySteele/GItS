"""EB-761's event door, on the harness side, with no game involved.

The C# half (`vendor/STS2_MCP/gits/GitsForceEvent.cs` and the op in
`gits/GitsDebugState.cs`) is checked by the compiler and by
`klee-mod/KleeTests/GitsForceEventTests.cs`, which compiles the arithmetic file
itself. What can be pinned here is the harness's side of the same discipline:
the field the op sends, the refusals it makes before a live game is involved,
the sentence it rides under, and the driver's walk -- including every place the
walk STOPS, because a driver that quietly fights its way to a `?` room would be
`soak.py` with a destination.
"""

from __future__ import annotations

import pytest

from understudy import bridge, force_event, scenario


class _Recorder:
    def __init__(self, answer=None):
        self.calls = []
        self.answer = answer or {"status": "ok", "message": "forced",
                                 "guardrail": "DEV ROUTE. ...",
                                 "op": "force_next_event",
                                 "event": "ROOM_FULL_OF_CHEESE",
                                 "act": "MONDSTADT", "before": 7, "after": 2,
                                 "moved": True, "queued": False}

    def __call__(self, url, payload=None, timeout=20.0):
        self.calls.append((url, payload))
        return dict(self.answer)


# ------------------------------------------------------------- the wire ----

def test_the_force_goes_to_the_debug_state_route_with_every_field(monkeypatch):
    """One route, one op list. It is not a route of its own because it is
    disqualifying in exactly the way the board writes are, and a second route
    would be a second guardrail a reader learns to skip."""
    rec = _Recorder()
    monkeypatch.setattr(bridge, "_request", rec)
    bridge.force_next_event("ROOM_FULL_OF_CHEESE", "EB-761 re-proof")
    url, payload = rec.calls[0]
    assert url == bridge.DEBUG_STATE
    assert payload == {"op": "force_next_event", "amount": 0, "who": "player",
                       "resource": "", "power": "", "card": "",
                       "event": "ROOM_FULL_OF_CHEESE",
                       "why": "EB-761 re-proof"}


def test_the_op_is_on_the_bridges_list_and_the_list_is_the_gate(monkeypatch):
    """`debug_state` refuses an op it does not know before any round trip, and
    the new op has to be on that list or the client refuses its own call."""
    assert "force_next_event" in bridge.DEBUG_OPS
    monkeypatch.setattr(bridge, "_request", _Recorder())
    with pytest.raises(ValueError):
        bridge.debug_state("force_next_room", "why", event="X")


def test_a_force_with_no_reason_is_refused_here(monkeypatch):
    """The endpoint refuses a write with no `why` (HTTP 400). Refused
    client-side for the reason every other op's is: a round trip to learn the
    reason field was empty is a round trip that only happens with a live game
    up."""
    monkeypatch.setattr(bridge, "_request", _Recorder())
    with pytest.raises(ValueError):
        bridge.force_next_event("ROOM_FULL_OF_CHEESE", "   ")


def test_an_error_answer_comes_back_as_a_dict_not_an_exception(monkeypatch):
    """This module's standing convention for the bridge's two error shapes,
    and the four live refusals (no run, unknown id, already visited, not
    allowed) all arrive in this shape."""
    monkeypatch.setattr(bridge, "_request",
                        _Recorder({"status": "error",
                                   "message": "No event 'X' pending"}))
    assert bridge.force_next_event("X", "why")["status"] == "error"


def test_the_docstring_says_nothing_after_it_is_comparable():
    """The claim is load-bearing and lives where a caller reads it. A door
    whose disqualification is only in a record nobody opened is a door that
    produces numbers somebody quotes."""
    doc = (bridge.force_next_event.__doc__ or "").lower()
    assert "not comparable" in doc
    assert "never for a number" in doc


def test_the_op_is_deliberately_not_a_scenario_verb():
    """The scenario runner wakes on a COMBAT screen and this op acts on a map,
    so a verb for it could never fire. Recorded as data on both sides so the
    absence reads as a decision rather than an omission."""
    assert "force_next_event" in scenario.NON_SCENARIO_OPS
    assert "force_next_event" not in scenario.STEP_VERBS


# ---------------------------------------------------------- the driver -----

def _wire(monkeypatch, states, *, force=None, post=None):
    """Point `force_event`'s bridge calls at a scripted list of states.

    THE FIRST ENTRY IS CONSUMED BY THE RUN CHECK, before the force is posted
    -- the driver reads the screen once to refuse a menu. The last entry
    repeats forever, so a test writes only the states it cares about.
    """
    seen = {"forced": [], "posts": []}
    pending = list(states)

    def get_state():
        return pending.pop(0) if len(pending) > 1 else pending[0]

    def force_next_event(event_id, why):
        seen["forced"].append((event_id, why))
        return dict(force or {"status": "ok", "message": "forced",
                              "event": event_id, "act": "MONDSTADT",
                              "before": 7, "after": 2, "moved": True})

    def do_post(action, **params):
        seen["posts"].append((action, params))
        return dict(post or {"status": "ok"})

    monkeypatch.setattr(bridge, "get_state", get_state)
    monkeypatch.setattr(bridge, "force_next_event", force_next_event)
    monkeypatch.setattr(bridge, "post", do_post)
    monkeypatch.setattr(bridge, "settle", lambda *a, **k: {})
    return seen


_MAP = {"state_type": "map",
        "map": {"next_options": [{"kind": "monster"}, {"kind": "event"}]}}
_EVENT = {"state_type": "event", "event": {"title": "..."}}


def test_the_walk_forces_then_takes_the_question_room(monkeypatch):
    seen = _wire(monkeypatch, [_MAP, _MAP, _EVENT])
    state = force_event.walk_to_event("ROOM_FULL_OF_CHEESE", "why",
                                      log=lambda _: None)
    assert state["state_type"] == "event"
    assert seen["forced"] == [("ROOM_FULL_OF_CHEESE", "why")]
    assert seen["posts"] == [("choose_map_node", {"index": 1})]


def test_the_force_happens_before_the_walk_not_after(monkeypatch):
    """Order is the whole mechanism: `PullNextEvent` reads the list when the
    room is ENTERED, so a force after the step is a force into the next `?`
    room and not this one."""
    seen = _wire(monkeypatch, [_MAP, _MAP, _EVENT])
    force_event.walk_to_event("X", "why", log=lambda _: None)
    assert seen["forced"] and seen["posts"]


def test_a_refused_force_stops_before_a_single_node_is_taken(monkeypatch):
    """Walking anyway would spend a `?` room on whatever the list already had
    -- and the room cannot be un-entered."""
    seen = _wire(monkeypatch, [_MAP, _MAP, _EVENT],
                 force={"status": "error", "message": "No event 'X' pending"})
    with pytest.raises(force_event.ForceEventError) as e:
        force_event.walk_to_event("X", "why", log=lambda _: None)
    assert "No event 'X' pending" in str(e.value)
    assert seen["posts"] == []


def test_a_menu_screen_is_refused_before_the_force(monkeypatch):
    seen = _wire(monkeypatch, [{"state_type": "menu"}])
    with pytest.raises(force_event.ForceEventError) as e:
        force_event.walk_to_event("X", "why", log=lambda _: None)
    assert "No run is open" in str(e.value)
    assert seen["forced"] == []


def test_a_floor_with_no_question_room_stops_and_says_what_was_offered(
        monkeypatch):
    """It does NOT walk on through a fight to find one. That would make this
    a run driver, and a run driver whose runs are not the game's own is the
    one thing `soak.py`'s claim cannot survive."""
    only_fights = {"state_type": "map",
                   "map": {"next_options": [{"kind": "monster"},
                                            {"kind": "elite"}]}}
    seen = _wire(monkeypatch, [only_fights])
    with pytest.raises(force_event.ForceEventError) as e:
        force_event.walk_to_event("X", "why", log=lambda _: None)
    assert "no `?` room" in str(e.value)
    assert seen["posts"] == []


def test_a_screen_that_is_neither_map_nor_event_stops_and_names_itself(
        monkeypatch):
    _wire(monkeypatch, [_MAP, {"state_type": "monster"}])
    with pytest.raises(force_event.ForceEventError) as e:
        force_event.walk_to_event("X", "why", log=lambda _: None)
    assert "'monster'" in str(e.value)


def test_a_refused_map_node_is_an_error_and_not_a_silent_retry(monkeypatch):
    _wire(monkeypatch, [_MAP, _MAP],
          post={"status": "error", "message": "node not reachable"})
    with pytest.raises(force_event.ForceEventError) as e:
        force_event.walk_to_event("X", "why", log=lambda _: None)
    assert "node not reachable" in str(e.value)


def test_a_map_that_never_becomes_an_event_gives_up_rather_than_spinning(
        monkeypatch):
    _wire(monkeypatch, [_MAP])
    with pytest.raises(force_event.ForceEventError) as e:
        force_event.walk_to_event("X", "why", max_screens=3,
                                  log=lambda _: None)
    assert "gave up" in str(e.value)


def test_the_options_are_read_from_either_place_the_wire_puts_them(
        monkeypatch):
    """`next_options` has lived at the top level and under `map`; a driver
    that knew only one would answer 'nothing to walk to' against the other."""
    flat = {"state_type": "map", "next_options": [{"kind": "event"}]}
    seen = _wire(monkeypatch, [flat, flat, _EVENT])
    force_event.walk_to_event("X", "why", log=lambda _: None)
    assert seen["posts"] == [("choose_map_node", {"index": 0})]


def test_the_guardrail_sentence_is_printed_with_the_force(monkeypatch):
    """`bridge.GRANT_GUARDRAIL` rides on the operator's screen, because this
    driver's output is read by a person and not filed as a row."""
    _wire(monkeypatch, [_MAP, _MAP, _EVENT])
    lines: list[str] = []
    force_event.walk_to_event("X", "why", log=lines.append)
    assert any(bridge.GRANT_GUARDRAIL in line for line in lines)


# ------------------------------------------------------- the module line ---

def test_the_soak_cannot_reach_this_module():
    """The same structural pin `test_understudy_scenario` puts on the scenario
    runner: an unattended soak whose runs are the game's own must not be able
    to import a door that makes them not."""
    import understudy.soak as soak
    text = (soak.__file__ and open(soak.__file__, encoding="utf-8").read()) or ""
    assert "force_event" not in text
