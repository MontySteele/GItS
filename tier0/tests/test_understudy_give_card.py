"""EB-52's dev card-grant door, on the harness side, with no game involved.

The C# half (`vendor/STS2_MCP/gits/GitsGiveCard.cs`) is checked by the compiler
and owes a live smoke. What CAN be pinned here is the discipline around it: the
route the client speaks to, the refusal of a pile the endpoint does not have,
and -- the part that actually matters six months from now -- that a grant is
written to the run log WITH the sentence saying the run it happened in is no
longer a run the generators produced.

A log that recorded the effect of a grant without recording the grant is a log
that shows a card appearing in a deck from nowhere.
"""

from __future__ import annotations

import json

import pytest

from understudy import bridge, harness


class _Recorder:
    def __init__(self, answer=None):
        self.calls = []
        self.answer = answer or {"status": "ok", "message": "queued",
                                 "guardrail": "DEV ROUTE. ...",
                                 "card_id": "UNHEARD_CONFESSION",
                                 "card_name": "Unheard Confession",
                                 "count": 1, "pile": "deck"}

    def __call__(self, url, payload=None, timeout=20.0):
        self.calls.append((url, payload))
        return self.answer


# ------------------------------------------------------------- the wire ----

def test_the_grant_goes_to_the_gits_route_and_not_the_action_endpoint(
        monkeypatch):
    """It is a fork route, like speed and seed. Posting it as an `action` on
    `/api/v1/singleplayer` would put it through upstream's dispatcher, which
    does not know it and would answer `Unknown action`."""
    rec = _Recorder()
    monkeypatch.setattr(bridge, "_request", rec)
    bridge.give_card("UNHEARD_CONFESSION")
    url, payload = rec.calls[0]
    assert url == bridge.GIVE_CARD
    assert url.endswith("/api/v1/gits/give_card")
    assert payload == {"card_id": "UNHEARD_CONFESSION", "count": 1,
                       "upgraded": False, "pile": "deck"}


def test_every_field_the_endpoint_reads_is_always_sent(monkeypatch):
    """Defaults are sent explicitly rather than omitted. An omitted field is a
    field whose default lives on the far side of a version boundary, and the
    far side here is a vendored snapshot that gets refreshed."""
    rec = _Recorder()
    monkeypatch.setattr(bridge, "_request", rec)
    bridge.give_card("X", count=3, upgraded=True, pile="hand")
    assert rec.calls[0][1] == {"card_id": "X", "count": 3,
                              "upgraded": True, "pile": "hand"}


@pytest.mark.parametrize("pile", ["deck", "hand", "draw", "discard"])
def test_the_four_piles_the_endpoint_has_are_accepted(monkeypatch, pile):
    monkeypatch.setattr(bridge, "_request", _Recorder())
    bridge.give_card("X", pile=pile)


def test_a_pile_the_endpoint_does_not_have_is_refused_here(monkeypatch):
    """Refused client-side because the answer is knowable client-side. A
    round-trip to learn a typo is a round-trip that only happens when a live
    game is up, which is the one moment nobody wants to spend on a typo."""
    monkeypatch.setattr(bridge, "_request", _Recorder())
    with pytest.raises(ValueError):
        bridge.give_card("X", pile="exhaust")


def test_an_error_answer_comes_back_as_a_dict_not_an_exception(monkeypatch):
    """This module's standing convention for the bridge's two error shapes
    (`understudy/bridge.py` parses HTTP error bodies as JSON and returns
    them), and the grant route does not get to be the exception."""
    monkeypatch.setattr(bridge, "_request",
                        _Recorder({"status": "error",
                                   "message": "No run in progress"}))
    assert bridge.give_card("X")["status"] == "error"


# ------------------------------------------------------- the log record ----

def _args(**over):
    ns = type("A", (), {})()
    ns.card_id = "UNHEARD_CONFESSION"
    ns.count = 1
    ns.upgraded = False
    ns.pile = "deck"
    ns.why = "EB-52(a): the fourth Fanfare evidence shape"
    for k, v in over.items():
        setattr(ns, k, v)
    return ns


def _run_verb(monkeypatch, tmp_path, answer=None, **over):
    written: list = []
    monkeypatch.setattr(harness, "_session", lambda: {"seed": "SEEDTEST01"})
    monkeypatch.setattr(harness, "append",
                        lambda seed, rec: written.append((seed, rec)))
    monkeypatch.setattr(
        harness.bridge, "give_card",
        lambda card_id, count, upgraded, pile: (
            answer or {"status": "ok", "message": "queued",
                       "card_id": card_id, "count": count, "pile": pile}))
    code = harness.cmd_give_card(_args(**over))
    return code, written


def test_the_grant_is_logged_against_the_run_with_its_guardrail(
        monkeypatch, tmp_path):
    code, written = _run_verb(monkeypatch, tmp_path)
    assert code == 0
    assert len(written) == 1
    seed, rec = written[0]
    assert seed == "SEEDTEST01", "the grant belongs to the run it changed"
    assert rec["event"] == "dev_card_grant"
    assert rec["guardrail"] == bridge.GRANT_GUARDRAIL
    assert "not one the generators produced" in rec["guardrail"]


def test_the_logged_request_is_what_was_asked_for_not_what_came_back(
        monkeypatch, tmp_path):
    """The request and the report are separate keys. A row that recorded only
    the answer could not tell a grant that was clamped or redirected from one
    that landed as asked."""
    _, written = _run_verb(monkeypatch, tmp_path, count=4, pile="hand",
                           upgraded=True)
    rec = written[0][1]
    assert rec["request"] == {"card_id": "UNHEARD_CONFESSION", "count": 4,
                              "upgraded": True, "pile": "hand"}
    assert "result" in rec


def test_the_stated_reason_travels_onto_the_row(monkeypatch, tmp_path):
    _, written = _run_verb(monkeypatch, tmp_path, why="checking the floor")
    assert written[0][1]["why"] == "checking the floor"


def test_a_refused_grant_is_still_logged_and_exits_nonzero(
        monkeypatch, tmp_path):
    """A refusal is a fact about the run too -- and an unlogged failed attempt
    is how a reader concludes nobody tried."""
    code, written = _run_verb(
        monkeypatch, tmp_path,
        answer={"status": "error", "message": "No run in progress"})
    assert code == 1
    assert written[0][1]["result"]["status"] == "error"


def test_the_row_is_json_serialisable_like_every_other_row(monkeypatch,
                                                           tmp_path):
    _, written = _run_verb(monkeypatch, tmp_path)
    json.dumps(written[0][1])


# ------------------------------------------------------- where it lives ----

def test_the_soak_has_no_grant_verb():
    """The soak's whole claim is that its runs are runs the game generated. A
    grant reachable from an unattended overnight loop is a way for that claim
    to become false while nobody is watching, so the door is on the ATTENDED
    harness only. If this ever fails, the claim in `soak.py`'s header needs
    rewriting before the feature ships."""
    from understudy import soak
    assert not hasattr(soak, "give_card")
    assert "give_card" not in soak.main.__doc__ if soak.main.__doc__ else True
    src = (soak.Path(soak.__file__)).read_text(encoding="utf-8")
    assert "give_card" not in src
