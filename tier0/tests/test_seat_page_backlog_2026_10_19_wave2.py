"""SEAT PAGE BACKLOG, WAVE 2 (2026-10-19): the seat-page lines of
`docs/current/BACKLOG.md` built in one pass. One test group per line.

- Two Decimillipede segments waiting to Reattach no longer print one row
  twice (the page refused the screen).
- The Colorless Potion's Beat Down says when the Discard Pile has no Attacks.
- An enemy that died with no card resolving prints under "Since last page"
  (C# twin in `SeatPageBacklogWave2Tests`).
- A power a card puts on its own player prints on its play line (Wait For
  It...), so the row no longer says nothing landed.
- A hand card's number follows the bridge's per-card handle for the turn.
- An event page showing only "Proceed" is read again until it settles.
- Co-op: a play whose aimed enemy died first says so, and where it went.
- Frozen on an enemy row prints wherever the state carries it.
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from understudy import (blindplay, blindplay_board, blindplay_faces,
                        blindplay_render, blindplay_session, qa_packet)
from understudy.blindplay_read import settle, settle_event
from understudy.blindplay_shape import EVENT_SETTLE_TRIES

from tier0.tests.test_understudy_blindplay import combat_state

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh():
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


def _segment(cid: int, hp: int) -> dict:
    return {"entity_id": f"DECIMILLIPEDE_SEGMENT_{cid}", "combat_id": cid,
            "name": "Decimillipede", "hp": hp, "max_hp": 48, "block": 0,
            "status": [], "intents": [{"type": "Attack", "label": "6",
                                       "title": "Bite"}]}


# ---- two dead segments ------------------------------------------------------

def _two_dead(state: dict) -> dict:
    state["battle"]["enemies"] = [_segment(1, 30)]
    state["battle"]["reviving"] = [
        {"combat_id": 2, "name": "Decimillipede", "max_hp": 48,
         "move_id": "REATTACH_MOVE", "revive_hp": 25},
        {"combat_id": 3, "name": "Decimillipede", "max_hp": 48,
         "move_id": "REATTACH_MOVE", "revive_hp": 25}]
    return state


def test_two_segments_waiting_to_reattach_print_two_rows():
    """Fontaine round, both seats: the page refused its own screen."""
    opening = combat_state()
    opening["battle"]["enemies"] = [_segment(i, 48) for i in (1, 2, 3)]
    blindplay.observe(opening)
    page = blindplay.observe(_two_dead(combat_state()))
    for name in ("Decimillipede (2)", "Decimillipede (3)"):
        assert blindplay_render.REVIVING_NEXT_TURN.format(
            name=name, hp=" with 25 HP") in page


def test_two_dead_segments_on_a_first_look_are_numbered():
    page = blindplay.observe(_two_dead(combat_state()))
    assert page.count("dead, Reattaching") == 2
    assert "**Decimillipede (1)** — dead" in page
    assert "**Decimillipede (2)** — dead" in page


# ---- Beat Down with no Attacks in the discard -------------------------------

def _potion_chooser(discard: list[dict]) -> dict:
    state = combat_state()
    state["state_type"] = "card_select"
    state["card_select"] = {
        "screen_type": "choose", "can_confirm": False, "can_cancel": False,
        "prompt": "Choose a card.",
        "cards": [{"name": "Beat Down", "cost": "1", "type": "Skill",
                   "description": "Play 3 random Attacks from your Discard "
                                  "Pile."},
                  {"name": "Panache", "cost": "0", "type": "Power",
                   "description": "Every time you play 5 cards in a single "
                                  "turn, deal 10 damage to ALL enemies."}]}
    state["player"]["discard_pile"] = discard
    return state


def test_beat_down_says_the_discard_pile_has_no_attacks():
    skills = [{"name": "Defend", "type": "Skill", "cost": "1",
               "description": "Gain 5 Block."}]
    page = blindplay.observe(_potion_chooser(skills))
    note = "    " + blindplay_board.NO_DISCARD_ATTACKS_NOTE
    assert page.count(note) == 1
    beat = page.index("**Beat Down**")
    assert beat < page.index(note) < page.index("**Panache**")
    qa_packet.assert_blind(blindplay_board.NO_DISCARD_ATTACKS_NOTE)


def test_no_note_once_the_discard_pile_holds_an_attack():
    strike = [{"name": "Strike", "type": "Attack", "cost": "1",
               "description": "Deal 6 damage."}]
    page = blindplay.observe(_potion_chooser(strike))
    assert blindplay_board.NO_DISCARD_ATTACKS_NOTE not in page


def test_no_note_off_a_fight():
    state = _potion_chooser([])
    del state["player"]["discard_pile"]
    assert blindplay_board.NO_DISCARD_ATTACKS_NOTE not in blindplay.observe(
        state)


# ---- a death with no card behind it -----------------------------------------

def _between(events: list[dict]) -> dict:
    return {"card_id": "", "card": "", "auto_played": False,
            "carried": False, "overflowed": False, "hits": [],
            "between": True, "events": events}


def test_an_enemy_that_died_outside_a_play_prints_since_last_page():
    state = combat_state()
    state["player"]["resolutions"] = [_between([
        {"kind": "died", "card": "Poison", "target": "Mawler",
         "combat_id": "9", "on_player": False, "seq": 5},
        {"kind": "died", "card": "", "target": "Byrdonis",
         "combat_id": "8", "on_player": False, "seq": 6}])]
    page = blindplay.observe(state)
    assert blindplay_render.EVENT_DIED.format(target="Mawler",
                                              cause="Poison") in page
    assert blindplay_render.EVENT_DIED_NO_CAUSE.format(
        target="Byrdonis") in page
    assert "died" in blindplay_board.PAGE_EVENT_KINDS


# ---- a power the card put on you --------------------------------------------

def _row(card: str, card_type: str, applied: list[dict]) -> dict:
    return {"card_id": "x", "card": card, "auto_played": False,
            "carried": False, "overflowed": False, "card_type": card_type,
            "hits": [], "applied": applied, "events": []}


def test_wait_for_it_prints_the_power_it_put_on_you():
    state = combat_state()
    state["player"]["resolutions"] = [_row("Wait For It...", "Skill", [
        {"target": "Klee", "power": "Wait For It...", "amount": 2,
         "combat_id": "1", "seq": 3, "on_player": True}])]
    page = blindplay.observe(state)
    assert blindplay_render.RESOLUTION_APPLIED.format(
        power="Wait For It...", n=2, target="you") in page
    assert blindplay_render.RESOLUTION_NO_HITS not in page


def test_a_power_card_keeps_its_own_line():
    state = combat_state()
    state["player"]["resolutions"] = [_row("Inflame", "Power", [
        {"target": "Klee", "power": "Inflame", "amount": 2,
         "combat_id": "1", "seq": 3, "on_player": True}])]
    page = blindplay.observe(state)
    assert blindplay_render.RESOLUTION_POWER_PLAYED in page
    assert "on **you**" not in page


# ---- a card's number follows its handle -------------------------------------

def _hand_state(cards: list[tuple[str, int]]) -> dict:
    state = combat_state()
    state["player"]["hand"] = [
        {"name": name, "type": "Skill", "cost": "0", "handle": handle,
         "description": "Deal 3 damage." if name == "Sting" else "Gain 5 "
                                                                 "Block.",
         "index": i, "target_type": "Self", "can_play": True}
        for i, (name, handle) in enumerate(cards)]
    return state


def test_a_copy_keeps_its_number_by_handle_through_a_reorder():
    """Kokomi round 3 lane 5 spent The Shape of Water on a renumbered Sting:
    the in-order alignment re-paired copies whose faces matched."""
    first = _hand_state([("Sting", 11), ("Sting", 12), ("Sting", 13)])
    assert blindplay_faces.hand_labels(first) == [
        "Sting (1)", "Sting (2)", "Sting (3)"]
    # Sting (1) was played; the game put a new card first and the two left
    # in the other order.
    later = _hand_state([("Defend", 20), ("Sting", 13), ("Sting", 12)])
    assert blindplay_faces.hand_labels(later) == [
        "Defend", "Sting (3)", "Sting (2)"]


def test_the_bridge_sends_each_hand_card_its_handle():
    builder = (ROOT / "vendor" / "STS2_MCP"
               / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert "state[GitsCardHandle.Key] = GitsCardHandle.Of(card);" in builder
    handle = (ROOT / "vendor" / "STS2_MCP" / "gits"
              / "GitsCardHandle.cs").read_text(encoding="utf-8")
    assert "ConditionalWeakTable<CardModel" in handle


# ---- an event read mid-change -----------------------------------------------

class _Wire:
    def __init__(self, *states):
        self.states = list(states)
        self.reads = 0

    def get_state(self):
        self.reads += 1
        return self.states.pop(0)


def _event(options: list[dict]) -> dict:
    return {"state_type": "event",
            "event": {"event_name": "The Trial", "is_ancient": False,
                      "in_dialogue": False, "options": options}}


PROCEED = [{"index": 0, "title": "Proceed", "is_proceed": True}]
TRIAL = [{"index": 0, "title": "Accept"}, {"index": 1, "title": "Reject"}]


def test_a_lone_proceed_is_read_again_until_the_room_settles():
    """The Trial's first page printed only "Proceed"."""
    ready = _event(TRIAL)
    wire = _Wire(ready)
    assert settle(_event(PROCEED), wire, delay=0) is ready
    assert wire.reads == 1


def test_a_real_lone_proceed_settles_after_two_agreeing_reads():
    again = _event(PROCEED)
    wire = _Wire(again)
    assert settle_event(_event(PROCEED), wire, delay=0) is again
    assert wire.reads == 1


def test_the_wait_is_bounded():
    two = [{"index": 0, "title": "Proceed"}, {"index": 1, "title": "Leave"}]
    # The room flips between the lone Proceed and another list every read.
    wire = _Wire(*[_event(two if i % 2 == 0 else PROCEED)
                   for i in range(EVENT_SETTLE_TRIES * 2)])
    settle_event(_event(PROCEED), wire, delay=0)
    assert wire.reads <= EVENT_SETTLE_TRIES


def test_an_event_with_real_options_is_not_read_again():
    wire = _Wire()
    ready = _event(TRIAL)
    assert settle_event(ready, wire, delay=0) is ready
    assert wire.reads == 0


# ---- co-op: the aimed enemy died first --------------------------------------

def _two_nibbits() -> dict:
    state = combat_state()
    second = copy.deepcopy(state["battle"]["enemies"][0])
    second.update({"entity_id": "NIBBIT_1", "combat_id": 2})
    state["battle"]["enemies"].append(second)
    state["player"]["resolutions"] = []
    return state


def _strike_row(target: str, cid: str) -> dict:
    return {"card_id": "STRIKE", "card": "Pearl Barrage",
            "auto_played": False, "carried": False, "overflowed": False,
            "card_type": "Attack", "is_local": True,
            "hits": [{"target": target, "amount": 9, "blocked": 0,
                      "combat_id": cid, "killed": False, "seq": 4}],
            "applied": [], "events": []}


def test_a_play_whose_target_died_first_says_where_it_went():
    sent = _two_nibbits()
    blindplay.observe(sent)
    blindplay_session.card_played(
        sent, "play_card", {"action": "play_card", "card_index": 0,
                            "target": "NIBBIT_0"}, {"status": "ok"})
    after = _two_nibbits()
    after["battle"]["enemies"] = after["battle"]["enemies"][1:]
    # The partner's play killed Nibbit (1) first; then this one resolved.
    partner = {"card_id": "STRIKE", "card": "Strike", "auto_played": False,
               "carried": False, "overflowed": False, "card_type": "Attack",
               "is_local": False,
               "hits": [{"target": "Nibbit", "amount": 0, "blocked": 0,
                         "combat_id": "1", "killed": True, "seq": 3}],
               "applied": [], "events": []}
    after["player"]["resolutions"] = [partner, _strike_row("Nibbit", "2")]
    page = blindplay.observe(after)
    assert blindplay_render.RESOLUTION_RETARGETED.format(
        aimed="Nibbit (1)", went="**Nibbit (2)**") in page


def test_a_play_that_hit_its_aim_says_nothing_more():
    sent = _two_nibbits()
    blindplay.observe(sent)
    blindplay_session.card_played(
        sent, "play_card", {"action": "play_card", "card_index": 0,
                            "target": "NIBBIT_0"}, {"status": "ok"})
    after = _two_nibbits()
    after["player"]["resolutions"] = [_strike_row("Nibbit", "1")]
    page = blindplay.observe(after)
    assert "which died before it landed" not in page


def test_a_refused_play_at_a_dead_enemy_says_nothing_was_played():
    lines = blindplay_session.answer_lines(
        {"verb": "play", "printed": {}}, _two_nibbits(),
        {"status": "error",
         "error": "Target 'NIBBIT_0' not found among alive enemies"})
    assert blindplay_session.TARGET_DIED_FIRST in lines
    qa_packet.assert_blind(blindplay_session.TARGET_DIED_FIRST)
    for line in (blindplay_render.RESOLUTION_RETARGETED,
                 blindplay_render.RESOLUTION_RETARGET_NOTHING):
        qa_packet.assert_blind(line.format(aimed="Nibbit", went="Nibbit"))


# ---- Frozen on an enemy row -------------------------------------------------

def test_frozen_prints_on_a_boss_room_enemy_row():
    """Furina round 2026-10-12, lane 2. The row prints what the state
    carries; whether a guest's act ends a freeze needs the game."""
    state = combat_state()
    state["state_type"] = "boss"
    state["battle"]["enemies"][0]["status"] = [
        {"id": "KLEEMOD-FROZEN_POWER", "name": "Frozen", "amount": 1,
         "type": "Debuff", "description": "Takes less damage."}]
    page = blindplay.observe(state)
    other = page[page.index("## The other side"):]
    assert "Frozen 1 (debuff)" in other.split("\n\n")[1]
