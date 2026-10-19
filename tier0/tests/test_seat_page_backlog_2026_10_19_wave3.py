"""BACKLOG WAVE 3 (2026-10-19): the seat-page items found by live checks.
One test group per item.

- Dodoco Tales' opening Sparks name the relic, not "the start of the fight".
- A card the ledger still has open keeps the read waiting, and a row still
  open when the bound runs out says so (a free Bravura listed 1 hit of 4).
- Block a card gives prints on its row (Klee Can Explain!).
- `_SWIRL_WORD` matches the word Swirl (it held backspace characters).
C# twin: `klee-mod/KleeTests/SeatPageBacklogWave3Tests.cs`.
"""
from __future__ import annotations

import copy

import pytest

from understudy import blindplay, blindplay_board, blindplay_render, qa_packet
from understudy import blindplay_read

from tier0.tests.test_understudy_blindplay import combat_state


@pytest.fixture(autouse=True)
def _fresh():
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


# ---- Dodoco Tales ------------------------------------------------------------

DODOCO = {"id": "KLEEMOD-EXPLOSIVE_FRAGS", "name": "Dodoco Tales"}


def _sources(*rows: dict, relics: list[dict] | None = None) -> list[dict]:
    player = {"spark_sources": list(rows)}
    if relics is not None:
        player["relics"] = relics
    return blindplay_board.spark_sources(player) or []


def test_dodoco_tales_names_its_opening_sparks():
    rows = _sources({"source": "relic:explosive_frags/combat_start",
                     "amount": 4}, relics=[DODOCO])
    assert rows == [{"name": "Dodoco Tales", "amount": 4}]


def test_the_slug_is_never_printed_as_a_name():
    """The C# type is ExplosiveFrags; that name is a Rare Power card."""
    rows = _sources({"source": "relic:explosive_frags/combat_start",
                     "amount": 4}, relics=[])
    assert rows == [{"name": "the start of the fight", "amount": 4}]


def test_a_relic_riding_an_explosion_keeps_the_event_word():
    rows = _sources({"source": "relic:explosive_frags/explosion",
                     "amount": 2}, relics=[DODOCO])
    assert rows == [{"name": "an explosion", "amount": 2}]


def test_the_relic_name_reaches_the_page():
    state = copy.deepcopy(combat_state())
    state["character"] = "klee"
    state["player"]["relics"] = [DODOCO]
    state["player"]["spark_sources"] = [
        {"source": "relic:explosive_frags/combat_start", "amount": 4}]
    state["player"].setdefault("resources", {})["KLEEMOD_SPARK"] = 7
    page = blindplay.observe(state)
    assert "+4 Dodoco Tales" in page
    assert "+4 the start of the fight" not in page


# ---- a card still resolving --------------------------------------------------

def _bravura(open_: bool, hits: int) -> dict:
    state = combat_state()
    enemy = state["battle"]["enemies"][0]
    cid = str(enemy["combat_id"])
    state["player"]["resolutions"] = [{
        "card_id": "proto_fs_bravura", "card": "Bravura",
        "auto_played": False, "carried": False, "overflowed": False,
        "card_type": "Attack", "open": open_, "events": [], "applied": [],
        "hits": [{"target": enemy["name"], "amount": 7, "blocked": 0,
                  "combat_id": cid, "seq": i + 1} for i in range(hits)]}]
    return state


class _PollWire:
    def __init__(self, states: list[dict]):
        self.states = list(states)
        self.reads = 0

    def get_state(self) -> dict:
        self.reads += 1
        return self.states.pop(0) if len(self.states) > 1 else self.states[0]


def test_an_open_row_keeps_the_read_waiting(monkeypatch):
    monkeypatch.setattr(blindplay_read.time, "sleep", lambda _s: None)
    first = _bravura(True, 1)
    done = _bravura(False, 3)
    wire = _PollWire([_bravura(True, 1), done, done])
    out = blindplay.settle_board(first, wire, delay=0)
    assert len(out["player"]["resolutions"][0]["hits"]) == 3


def test_a_row_still_open_says_so():
    page = blindplay.observe(_bravura(True, 1))
    assert ("- **Bravura**" + blindplay_render.RESOLUTION_OPEN_CLAUSE) in page
    qa_packet.assert_blind(blindplay_render.RESOLUTION_OPEN_CLAUSE)


def test_a_closed_row_prints_no_clause():
    page = blindplay.observe(_bravura(False, 3))
    assert blindplay_render.RESOLUTION_OPEN_CLAUSE not in page


# ---- Block from a card -------------------------------------------------------

def _explain(block: list[dict]) -> dict:
    state = combat_state()
    state["player"]["resolutions"] = [{
        "card_id": "proto_ko_klee_can_explain", "card": "Klee Can Explain!",
        "auto_played": False, "carried": False, "overflowed": False,
        "card_type": "Skill", "events": [], "applied": [], "hits": [],
        "block": block}]
    return state


def test_klee_can_explain_prints_its_block():
    page = blindplay.observe(_explain([
        {"target": "Klee", "amount": 6, "combat_id": "1", "seq": 2,
         "self": True}]))
    line = blindplay_render.RESOLUTION_BLOCK.format(target="You", n=6)
    assert line in page
    assert blindplay_render.RESOLUTION_NO_HITS not in page
    qa_packet.assert_blind(line)


def test_no_block_still_says_nothing_landed():
    page = blindplay.observe(_explain([]))
    assert blindplay_render.RESOLUTION_NO_HITS in page


# ---- the Swirl word ----------------------------------------------------------

def test_swirl_word_matches_the_word_and_not_swirls():
    word = blindplay_render._SWIRL_WORD
    assert "\b" not in word.pattern
    assert word.search("Deal 4 damage. Swirl.")
    assert not word.search("Whenever a card Swirls, gain 1 Block.")
    assert blindplay_render._holds_a_swirl(
        [{"element": "", "text": "Swirl the target's aura."}])
