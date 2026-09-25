"""Every Stage log beat the mod can send crosses the blind packet, and an
`act` always ends on a line of words.

1. THE LEAK (2026-09-25, Codex seat `20260925-193725`). The seat stopped with
   `observation_leak`: "internal-snake-case-id: 'hit_furina' in 'hit_furina'".
   The observation IS the packet -- `blindplay_observe.observation` hands the
   whole structure to `qa_packet.assert_blind`, which walks every string value
   -- and `blindplay_board.furina_stage` copied each log row's wire `event`
   into it verbatim. Every beat before 2026-09-25 was one plain word; the
   Furina hit beat (`FurinaStageLedger.HitFurinaEvent`) was the first with an
   underscore. The board now carries the observation's own word
   (`stage_event`), so the installed build is fixed with no C# change.

   The event list is READ OFF THE C# SOURCE, not typed here, so a beat added
   to the ledger later is checked the day it lands.

2. THE BARE `}` (2026-09-25, Opus seat, lane 2). `act 'play "Stage Presence
   (1)"'` printed a `}` and nothing else. `cmd_act` prints the resolution as
   JSON first, and a refusal and a failed POST both stopped on its closing
   brace. Each now closes on a sentence.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from unittest import mock

import pytest

from understudy import blindplay, blindplay_shape, bridge, qa_packet
from understudy.blindplay_board import furina_stage, stage_event
from understudy.blindplay_observe import observation

REPO = Path(__file__).resolve().parents[2]
PROTO = REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"

#: Every beat named on 2026-09-25. The source scan below must find at least
#: these, so a regex that silently stops matching fails here rather than
#: passing on an empty list.
KNOWN = {"arrive", "act", "bow", "leave", "rotate", "raise", "regain", "hit",
         "hit_furina", "fade"}

_EVENT_SOURCES = (
    re.compile(r'const string \w*Event\s*=\s*"([a-z_]+)"'),
    re.compile(r'new StageBeat\(\s*"([a-z_]+)"'),
    re.compile(r'string what\s*=\s*"([a-z_]+)"'),
    re.compile(r'\b(?:Act|RaiseLead|NoteRaise)\([^;]*?"([a-z_]+)"\)'),
)


def ledger_events() -> set[str]:
    found: set[str] = set()
    for name in ("FurinaStageLedger.cs", "FurinaStage.cs"):
        text = (PROTO / name).read_text(encoding="utf-8")
        for pattern in _EVENT_SOURCES:
            found.update(pattern.findall(text))
    return found


def _state(log):
    """A Furina combat screen with a populated stage and this log."""
    seats = [
        {"member": "usher", "name": "Gentilhomme Usher", "seat": 0,
         "fanfare": 5, "entity_id": "7"},
        {"member": "crabaletta", "name": "Mademoiselle Crabaletta", "seat": 1,
         "fanfare": 2, "entity_id": "9"},
    ]
    return {
        "state_type": "monster", "screen": "combat", "floor": 3,
        "battle": {"round": 3},
        "player": {
            "character": "Furina", "hp": 60, "max_hp": 78, "block": 0,
            "energy": 3, "max_energy": 3, "gold": 0,
            "hand": [{"id": "x", "name": "Stage Presence",
                      "description": "Gain 5 Block.", "cost": "1",
                      "can_play": True, "target_type": "Self"}],
            "draw_pile_count": 5, "discard_pile_count": 2,
            "exhaust_pile_count": 0, "draw_pile": [], "discard_pile": [],
            "exhaust_pile": [], "relics": [], "potions": [], "status": [],
            "resources": {}, "pets": [],
            "furina_stage": {"live": True, "seats": seats, "log": log},
        },
        "enemies": [{"name": "Twig Slime (M)", "hp": 20, "max_hp": 28,
                     "block": 0, "combat_id": "1",
                     "intents": [{"kind": "attack", "amount": 7}],
                     "status": []}],
    }


def _row(event, **kw):
    """A log row in the mod's own shape (`FurinaStageLedger.Snapshot`)."""
    furina = event == "hit_furina"
    row = {"event": event,
           "member": "furina" if furina else "usher",
           "name": "Furina" if furina else "Gentilhomme Usher",
           "seat": -1 if furina else 0, "fanfare": 3, "moved": 2,
           "reason": "spend" if event == "leave" else "",
           "target": "Twig Slime (M)", "target_id": "1", "each": -1,
           "hp": 60 if furina else -1}
    row.update(kw)
    return row


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


# ---------------------------------------------------------------------------
# 1. EVERY BEAT CROSSES THE PACKET.
# ---------------------------------------------------------------------------

def test_the_source_scan_finds_every_named_beat():
    assert KNOWN <= ledger_events()


@pytest.mark.parametrize("event", sorted(ledger_events() | KNOWN))
def test_every_ledger_beat_passes_the_leak_scan_on_the_seat_path(event):
    """The path a seat's packet takes: the wire state through
    `observation()` (which raises `PacketLeak` itself) and then the page."""
    state = _state([_row(event)])
    obs = observation(state)
    assert qa_packet.leaks(obs) == []
    assert qa_packet.leaks(blindplay.observe(state)) == []


def test_the_furina_hit_beat_still_prints_its_line():
    stage = furina_stage(_state([_row("hit_furina")])["player"])
    assert stage["log"][0]["event"] == "hurt"
    page = blindplay.observe(_state([_row("hit_furina")]))
    assert ("**Twig Slime (M)** hit **Furina** for 2 past your Block and "
            "front performer: 62 → 60 HP.") in page


def test_an_unknown_snake_case_beat_is_dropped_not_leaked():
    """A newer build's beat this page has never seen prints nothing, which is
    the render's answer to any beat it does not know -- and never stops the
    seat."""
    assert stage_event("curtain_call") == ""
    assert stage_event("Hit") == ""
    assert stage_event("arrive") == "arrive"
    state = _state([_row("curtain_call")])
    assert qa_packet.leaks(observation(state)) == []


# ---------------------------------------------------------------------------
# 2. AN ACT NEVER ENDS ON `}`.
# ---------------------------------------------------------------------------

@pytest.fixture
def no_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.delenv(blindplay.LANE_ENV, raising=False)
    monkeypatch.delenv(blindplay.MAX_ACTIONS_ENV, raising=False)
    blindplay.set_budget(0)
    return tmp_path


def _last_line(out: str) -> str:
    return out.rstrip().splitlines()[-1]


def _act(command, raw_file="", dry_run=False):
    return blindplay.cmd_act(argparse.Namespace(
        raw_file=raw_file, command=command, dry_run=dry_run))


def test_a_refusal_ends_on_its_sentence(tmp_path, capsys):
    raw = tmp_path / "fight.json"
    raw.write_text(json.dumps(_state([])), encoding="utf-8")
    assert _act('play "Nothing Like It"', raw_file=str(raw)) == 1
    last = _last_line(capsys.readouterr().out)
    assert last.startswith("REFUSED: ")
    assert last != "}"


def test_the_numbered_form_of_a_lone_card_resolves(tmp_path, capsys):
    raw = tmp_path / "fight.json"
    raw.write_text(json.dumps(_state([])), encoding="utf-8")
    assert _act('play "Stage Presence (1)"', raw_file=str(raw)) == 0
    assert json.loads(capsys.readouterr().out)["printed"] == {
        "card": "Stage Presence"}


class _Wire:
    def __init__(self, state, answer=None, fail=None):
        self.state, self.answer, self.fail = state, answer, fail
        self.posts = 0

    def get_state(self):
        return json.loads(json.dumps(self.state))

    def post(self, action, **kw):
        self.posts += 1
        if self.fail:
            raise self.fail
        return self.answer


def test_a_post_the_game_does_not_answer_ends_on_words(no_budget, capsys,
                                                       monkeypatch):
    monkeypatch.setattr(blindplay.lanewatch, "guard", lambda *a, **k: "")
    wire = _Wire(_state([]), fail=bridge.BridgeError(
        "bridge connection failed: TimeoutError: timed out"))
    with mock.patch.object(blindplay, "bridge", wire), \
            mock.patch.object(blindplay, "settle_board", lambda s: s), \
            mock.patch.object(blindplay, "settle", lambda s: s):
        assert _act('play "Stage Presence (1)"') == 1
    last = _last_line(capsys.readouterr().out)
    assert last.startswith("NO ANSWER: ")
    assert wire.posts == 1


def test_a_wordless_answer_still_ends_on_words(no_budget, capsys):
    """`end turn` has no taken line; an answer with no status, message or
    error used to leave the JSON's brace as the last thing printed."""
    wire = _Wire(_state([]), answer={})
    with mock.patch.object(blindplay, "bridge", wire), \
            mock.patch.object(blindplay, "settle_board", lambda s: s), \
            mock.patch.object(blindplay, "settle", lambda s: s):
        assert _act("end turn") == 0
    assert _last_line(capsys.readouterr().out) == blindplay.ACT_SENT_SILENT
