"""EB-771's act door, on the harness side, with no game involved.

The C# half (`vendor/STS2_MCP/gits/GitsSkipAct.cs` and the op in
`gits/GitsDebugState.cs`) is checked by the compiler and by
`klee-mod/KleeTests/GitsSkipActTests.cs`, which compiles the decision file
itself. What can be pinned here is the harness's side of the same discipline:
the fields the op sends, the refusals it makes before a live game is involved,
the sentence it rides under, and the driver's wait -- including the place the
wait GIVES UP, because a driver that quietly called the op twice would move the
run two acts and nobody would see which one it meant to look at.
"""

from __future__ import annotations

import pytest

from understudy import bridge, scenario, skip_act


class _Recorder:
    def __init__(self, answer=None):
        self.calls = []
        self.answer = answer or {
            "status": "ok", "message": "skipped",
            "guardrail": "DEV ROUTE. ...", "op": "skip_act",
            "who": "MONDSTADT", "before": 0, "after": 1, "queued": True,
            "why": "EB-771 proof", "act": "MONDSTADT", "next_act": "NATLAN",
            "act_index": 0, "next_act_index": 1,
            "acts": ["MONDSTADT", "NATLAN", "FONTAINE"]}

    def __call__(self, url, payload=None, timeout=20.0):
        self.calls.append((url, payload))
        return dict(self.answer)


# ------------------------------------------------------------- the wire ----

def test_the_skip_goes_to_the_debug_state_route_with_every_field(monkeypatch):
    """One route, one op list. It is not a route of its own because it is
    disqualifying in exactly the way the board writes are, and a second route
    would be a second guardrail a reader learns to skip."""
    rec = _Recorder()
    monkeypatch.setattr(bridge, "_request", rec)
    bridge.skip_act("EB-771 act-2 dressing proof")
    url, payload = rec.calls[0]
    assert url == bridge.DEBUG_STATE
    assert payload == {"op": "skip_act", "amount": 0, "who": "player",
                       "resource": "", "power": "", "card": "", "event": "",
                       "why": "EB-771 act-2 dressing proof"}


def test_the_op_is_on_the_bridges_list_and_the_list_is_the_gate(monkeypatch):
    """`debug_state` refuses an op it does not know before any round trip, and
    the new op has to be on that list or the client refuses its own call."""
    assert "skip_act" in bridge.DEBUG_OPS
    monkeypatch.setattr(bridge, "_request", _Recorder())
    with pytest.raises(ValueError):
        bridge.debug_state("skip_the_act", "why")


def test_a_blank_why_is_refused_client_side(monkeypatch):
    """The reason is refused here rather than at the endpoint, because the
    answer is knowable here and a round trip to learn it only happens when a
    live game is up. Same rule `give_card` follows."""
    monkeypatch.setattr(bridge, "_request", _Recorder())
    with pytest.raises(ValueError):
        bridge.skip_act("   ")


def test_it_is_not_a_scenario_verb_and_says_why(monkeypatch):
    """A scenario grades one fight. A step that threw the run into the next
    act would leave every step after it addressing a combat that is gone -- and
    the runner wakes on a combat screen, so it could never stand on the map the
    op acts from anyway."""
    assert "skip_act" in scenario.NON_SCENARIO_OPS
    assert "skip_act" not in scenario.STEP_VERBS


# ------------------------------------------------------- the act number ----

@pytest.mark.parametrize("state,want", [
    ({"run": {"act": 2}}, 2),
    ({"act": 3}, 3),
    ({"run": {}}, None),
    ({}, None),
    ({"run": {"act": None}}, None),
    ({"run": {"act": "two"}}, None),
])
def test_the_act_number_is_read_from_the_run_block_or_nothing(state, want):
    """`McpMod.StateBuilder` writes `run.act = CurrentActIndex + 1` on every
    screen. It is the one act fact always on the wire -- the act ID is not --
    so the arrival check is made on the number, and a shape the wire does not
    have answers None rather than guessing."""
    assert skip_act.act_number(state) == want


# ---------------------------------------------------------- the driver -----

def _states(*acts):
    """A get_state sequence reporting these act numbers in order, repeating the
    last one forever."""
    seq = list(acts)

    def _get():
        value = seq.pop(0) if len(seq) > 1 else seq[0]
        return {"state_type": "map", "run": {"act": value}}
    return _get


def test_the_driver_waits_for_the_act_number_the_report_predicted(monkeypatch):
    """The endpoint answers `queued: true` -- the fade, the asset preload and
    the map generation run over the frames after it -- so the confirmation is a
    READ, and it is a read of the act and not of the screen type: the run was
    on a map before the call and is on a map after it."""
    monkeypatch.setattr(bridge, "_request", _Recorder())
    monkeypatch.setattr(bridge, "get_state", _states(1, 1, 1, 2))
    monkeypatch.setattr(skip_act.time, "sleep", lambda _s: None)
    state = skip_act.skip_to_next_act("EB-771 proof", log=lambda _m: None)
    assert skip_act.act_number(state) == 2


def test_a_transition_that_never_lands_is_an_error_and_not_a_shrug(monkeypatch):
    """Naming the stall matters more here than anywhere else on this route: a
    caller that read a silent success would call the op again, and a second
    skip moves the run two acts past the dressing it meant to look at."""
    monkeypatch.setattr(bridge, "_request", _Recorder())
    monkeypatch.setattr(bridge, "get_state", _states(1))
    monkeypatch.setattr(skip_act.time, "sleep", lambda _s: None)
    with pytest.raises(skip_act.SkipActError) as exc:
        skip_act.skip_to_next_act("EB-771 proof", max_polls=3,
                                  log=lambda _m: None)
    assert "two acts" in str(exc.value)


def test_a_refused_skip_stops_the_driver_with_the_endpoints_words(monkeypatch):
    """The four refusals that matter are made by the endpoint against the live
    run (a combat up, a stacked sub-room, the victory room, the last act). The
    driver's job is to carry the sentence out, not to re-derive it."""
    monkeypatch.setattr(bridge, "_request", _Recorder(
        {"status": "error",
         "message": "This run is already in its last act, and skip_act adds "
                    "no act-4 path."}))
    monkeypatch.setattr(bridge, "get_state",
                        lambda: {"state_type": "map", "run": {"act": 3}})
    with pytest.raises(skip_act.SkipActError) as exc:
        skip_act.skip_to_next_act("EB-771 proof", log=lambda _m: None)
    assert "act-4" in str(exc.value)


def test_it_refuses_a_menu_before_it_writes_anything(monkeypatch):
    """This driver embarks nothing. On a menu there is no run to act on, and
    saying so is cheaper than a round trip that says it less clearly."""
    rec = _Recorder()
    monkeypatch.setattr(bridge, "_request", rec)
    monkeypatch.setattr(bridge, "get_state", lambda: {"state_type": "menu"})
    with pytest.raises(skip_act.SkipActError):
        skip_act.skip_to_next_act("EB-771 proof", log=lambda _m: None)
    assert rec.calls == []


# ------------------------------------------------------------- the CLI -----

def test_the_cli_refuses_a_missing_why(monkeypatch):
    with pytest.raises(SystemExit):
        skip_act.main([])


def test_list_reads_the_act_list_and_writes_nothing(monkeypatch, capsys):
    """The dry-run half, and the reason it exists: which face this seed rolled
    for act 2 -- Natlan or Inazuma -- is decided at embark, so a caller can
    read it BEFORE deciding whether this is the run worth skipping in."""
    rec = _Recorder({"status": "ok", "acts": ["MONDSTADT", "INAZUMA",
                                              "SUMERU"],
                     "act_index": 0, "act": "MONDSTADT",
                     "next_act": "INAZUMA"})
    monkeypatch.setattr(bridge, "_request", rec)
    assert skip_act.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "INAZUMA" in out and "<-- here" in out
    # A GET and nothing else: no payload means no write.
    assert all(payload is None for _url, payload in rec.calls)


def test_list_says_so_when_no_run_is_up(monkeypatch, capsys):
    monkeypatch.setattr(bridge, "_request",
                        _Recorder({"status": "ok", "acts": [],
                                   "act_index": -1, "act": "",
                                   "next_act": ""}))
    assert skip_act.main(["--list"]) == 0
    assert "no run is up" in capsys.readouterr().out


# -------------------------------------------------------- the guardrail ----

def test_the_module_says_what_a_run_that_used_it_is_not():
    """Every door on this route carries the sentence, and this one carries a
    HARDER version of it: `force_next_event` consumes no rng and says so, while
    the floors this op skips are floors whose rolls never happen."""
    doc = skip_act.__doc__ or ""
    assert "ATTENDED ONLY" in doc
    assert "NOT COMPARABLE" in (bridge.skip_act.__doc__ or "")
    assert "no act-4 path" in doc.lower() or "act-4 path" in doc
