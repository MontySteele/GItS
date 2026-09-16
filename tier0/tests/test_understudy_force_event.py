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
                           "relic": "", "potion": "", "slot": -1,
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


# ---------------------------------------- EB-767: dressed ids translate ----

def test_a_dressed_id_is_translated_to_the_base_the_pending_list_holds():
    """A dressing does not replace an event in the act's pool -- the pool is
    shuffled once at run start and a pool one element different moves every
    later roll on that stream -- so the substitution happens downstream, in the
    `PullNextEvent` postfix. The pending list therefore holds the BASE id, and
    six proof ids typed as their dressed names all failed against a run that
    was holding exactly the events they dress (proofs-3)."""
    target, dressing = force_event.resolve_event_id(
        "GUILD_DESKS_RETURNED_COPY")
    assert target == "SELF_HELP_BOOK"
    assert dressing == "Mondstadt"


def test_a_base_id_is_left_exactly_alone():
    assert force_event.resolve_event_id("SELF_HELP_BOOK") == (
        "SELF_HELP_BOOK", None)


def test_an_unknown_id_is_a_passthrough_and_not_a_guess():
    """A translation, never a validation. The endpoint's own refusal prints
    the act's pending list back, which is a better answer for an unknown id
    than anything this file could invent without a run up."""
    assert force_event.resolve_event_id("NO_SUCH_EVENT") == (
        "NO_SUCH_EVENT", None)


def test_the_table_is_the_generated_file_and_covers_every_dressed_event():
    """One substitution table in the repo. `TeyvatEventsGenerated.cs` is
    written by `tools/gen_teyvat_events.py` from the curated faces and drift-
    checked by that generator's `--check`; a second table maintained by hand
    here would be a second thing to forget when a face lands."""
    table = force_event.dressed_to_base()
    source = force_event._SUBSTITUTIONS_SOURCE.read_text(encoding="utf-8")
    rows = source.partition("Substitutions =")[2].count("[(TeyvatFrame.")
    assert rows > 0
    assert len(table) == rows
    # Every value is a base id and a dressing name, and no dressed id is also
    # a base id -- if one were, a translation would be ambiguous.
    bases = {base for base, _ in table.values()}
    assert not (bases & set(table))


def test_the_wire_id_rule_is_the_generators_own():
    """Pinned against `tools/gen_teyvat_events.py`'s `slugify` over every class
    name in the table rather than against a handful of examples: the two
    functions produce `Id.Entry` for the same names, and a drift between them
    would send the op at an id the game never answers to. `ToABetterYou` is
    `TO_A_BETTER_YOU`, which is the case that already cost a proof round."""
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location(
        "_gen_teyvat_events",
        force_event.REPO / "tools" / "gen_teyvat_events.py")
    gen = importlib.util.module_from_spec(spec)
    # REGISTERED BEFORE IT IS EXECUTED: the generator declares dataclasses, and
    # `dataclasses` resolves a string annotation through `sys.modules[cls.
    # __module__]`, which is None for a module that was never registered.
    sys.modules[spec.name] = gen
    try:
        spec.loader.exec_module(gen)
    finally:
        sys.modules.pop(spec.name, None)

    source = force_event._SUBSTITUTIONS_SOURCE.read_text(encoding="utf-8")
    block = source.partition("Substitutions =")[2]
    names = set()
    for _dressing, base_cls, dressed_cls in (
            force_event._SUBSTITUTION_ROW.findall(block)):
        names.add(base_cls)
        names.add(dressed_cls)
    assert names
    for name in sorted(names):
        assert force_event.wire_id(name) == gen.slugify(name), name
    assert force_event.wire_id("ToABetterYou") == "TO_A_BETTER_YOU"


def test_the_walk_forces_the_translated_id_and_says_it_did(monkeypatch):
    """Said out loud on every translation. A driver that silently retargeted
    an id would make the next failure unreadable."""
    seen = _wire(monkeypatch, [_MAP, _MAP, _EVENT])
    lines: list[str] = []
    force_event.walk_to_event("GUILD_DESKS_RETURNED_COPY", "why",
                              log=lines.append)
    assert seen["forced"] == [("SELF_HELP_BOOK", "why")]
    assert any("DRESSED" in line and "SELF_HELP_BOOK" in line
               for line in lines)


def test_list_annotates_each_base_id_with_the_faces_that_dress_it(
        monkeypatch, capsys):
    """Without this the list is a wall of names that match nothing on any page
    a reader has seen."""
    monkeypatch.setattr(
        force_event, "pending_events",
        lambda: {"events": ["SELF_HELP_BOOK", "A_NIGHT_AT_THE_INN"],
                 "events_visited": 0, "next_event": "SELF_HELP_BOOK"})
    assert force_event.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "GUILD_DESKS_RETURNED_COPY" in out
    assert "dressed as" in out
    assert "EB-767" in out


# ------------------------------- EB-770: what the predicate wants ----------
#
# The proofs-7 record (PR #556) spent four launches on four
# events that each answered only "IsAllowed is false". The gate itself cannot
# be read at runtime -- it is a compiled method -- so it is lifted off the
# decompile into `tools/data/sts2_base_events.json` and printed from here.


def test_every_base_event_a_face_dresses_carries_a_gate_note():
    """The pin that keeps the table honest as faces land. A dressing whose
    base event has no note would put the next round back where proofs-7 was:
    a refusal with nothing in it but the word false."""
    notes = force_event.allowed_notes()
    assert notes, "the index carries no is_allowed notes at all"
    missing = sorted({base for base, _ in force_event.dressed_to_base().values()
                      if base not in notes})
    assert missing == [], f"no IsAllowed note for: {missing}"


def test_the_four_events_proofs_seven_could_not_force_now_say_what_they_want():
    """The round's own list, by name. Each one is the base event's own
    `IsAllowed`, folded to one expression; the numbers beside it on a refusal
    are the bridge's `run_facts`."""
    assert force_event.allowed_note("SLIPPERY_BRIDGE") == (
        "TotalFloor > 6 && Players.All(Deck.Cards.Any(IsRemovable))")
    assert force_event.allowed_note("RELIC_TRADER") == (
        "CurrentActIndex != 0 && "
        "Players.All(Relics.Where(IsTradable).Count() >= 5)")
    assert force_event.allowed_note("RANWID_THE_ELDER") == (
        "CurrentActIndex != 0 && Players.All(Relics.Where(IsTradable).Any()) "
        "&& Players.All(Gold >= 100) && Players.All(Potions.Any())")
    assert force_event.allowed_note("WELCOME_TO_WONGOS") == (
        "CurrentActIndex == 1 && Players.All(Gold >= 100)")


def test_an_event_with_no_gate_says_so_rather_than_saying_nothing():
    """`EventModel.IsAllowed` returns true. An empty note would read as a
    missing row; this one reads as an event that is always allowed."""
    assert "no gate" in (force_event.allowed_note("SELF_HELP_BOOK") or "")


def test_an_id_the_index_does_not_carry_is_none_and_not_a_guess():
    assert force_event.allowed_note("NO_SUCH_EVENT") is None


def test_a_refusal_prints_the_gate_and_what_the_run_holds(monkeypatch):
    """The two halves together. Neither is useful alone: the gate without the
    run does not say which clause failed, and the run without the gate is a
    row of numbers."""
    seen = _wire(monkeypatch, [_MAP], force={
        "status": "error",
        "error": "'SLIPPERY_BRIDGE' is not allowed in this run right now",
        "run_facts": {"TotalFloor": 3, "RemovableCards": 12}})
    with pytest.raises(force_event.ForceEventError) as exc:
        force_event.walk_to_event("SLIPPERY_BRIDGE", "why", log=lambda _: None)
    message = str(exc.value)
    assert "TotalFloor > 6" in message
    assert "TotalFloor=3" in message
    assert "RemovableCards=12" in message
    assert seen["posts"] == []


def test_a_refusal_from_an_older_bridge_still_prints_the_gate(monkeypatch):
    """`run_facts` is new. A bridge that does not send it must not cost the
    caller the half that lives in this tree."""
    _wire(monkeypatch, [_MAP], force={"status": "error",
                                      "error": "not allowed"})
    with pytest.raises(force_event.ForceEventError) as exc:
        force_event.walk_to_event("WELCOME_TO_WONGOS", "why",
                                  log=lambda _: None)
    assert "CurrentActIndex == 1" in str(exc.value)
    assert "HOLDS:" not in str(exc.value)


def test_the_act_index_legend_rides_with_every_note():
    """`CurrentActIndex == 1` is act TWO. A reader who takes it for act one
    spends the launch the note was written to save."""
    detail = force_event.refusal_detail({}, "WELCOME_TO_WONGOS")
    assert "ZERO-BASED" in detail


def test_list_prints_the_gate_beside_each_pending_id(monkeypatch, capsys):
    monkeypatch.setattr(
        force_event, "pending_events",
        lambda: {"events": ["SLIPPERY_BRIDGE"], "events_visited": 0,
                 "next_event": "SLIPPERY_BRIDGE"})
    assert force_event.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "allowed when: TotalFloor > 6" in out
