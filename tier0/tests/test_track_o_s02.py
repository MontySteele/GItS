"""Track O, slice 2 -- pins under the SELECTOR RECORDING channel.

These are the three properties of `fight.selectors` that the red-team pass
found load-bearing AND unambiguous from the instruments' own documentation.
The pass's actual findings (screen-coverage gaps, the round that opens behind
an overlay, short-row tolerance) are NOT pinned here: pinning current
behaviour there would ratify a defect. They are written up as prose.

Nothing in this file modifies an instrument; it drives `understudy/soak.py`'s
recorder and `understudy/replay.py`'s reader on synthetic dicts.
"""

from __future__ import annotations

from understudy import replay, soak


def _driver():
    d = soak.RunDriver.__new__(soak.RunDriver)
    d.fight = None
    d.fights = []
    d.commit = ""
    d.emit = lambda rec: None
    return d


def _combat(hp=50, round_=1):
    return {
        "state_type": "monster", "run": {"act": 1, "floor": 3},
        "battle": {"round": round_, "enemies": [
            {"entity_id": "JAW_0", "name": "Jaxfruit", "hp": 30, "max_hp": 40,
             "block": 0, "intents": [{"type": "Attack", "label": "7"}],
             "status": []}]},
        "player": {"hp": hp, "max_hp": 71, "block": 0, "energy": 3,
                   "hand": [], "draw_pile": [], "discard_pile": [],
                   "exhaust_pile": []},
    }


def _screen(kind, cards):
    """A selector overlay. It carries NO `battle` block -- which is the whole
    reason `_selector_row` reads the round off the fight's own counter."""
    return {"state_type": kind, "run": {"act": 1, "floor": 3},
            "player": {"hp": 50, "max_hp": 71},
            kind: {"screen_type": kind,
                   "cards": [{"name": c} for c in cards]}}


PAIR = ["Center Stage", "Guest Cast"]


def test_every_screen_that_records_a_selector_also_survives_the_fight():
    """A screen the recorder answers INSIDE a fight must not also be a screen
    that ends the fight. `SELECTOR_SCREENS` is written as a subset of
    `MID_FIGHT` (`soak.py`'s own comment: "screens that interrupt a fight
    WITHOUT ending it"); the day one leaves that set, its answers land on a
    fight record that `_close_fight` has already sealed and shipped."""
    assert set(soak.SELECTOR_SCREENS) <= set(soak.MID_FIGHT)


def test_a_selector_row_carries_the_round_the_overlay_stands_on():
    """The overlay state has no `battle` block at all, so the round comes from
    the fight's own turn counter -- documented in `_selector_row`'s docstring.
    A row stamped `None` would match no reader's round and read as "this turn
    had no selector"."""
    d = _driver()
    fight = _combat(round_=2)
    d._observe(_combat(round_=1), _combat(round_=1), {}, {"action": "noop"})
    d._observe(_combat(round_=1), fight, {}, {"action": "end_turn"})
    d._observe(_screen("card_select", PAIR), fight,
               {"card_name": "Guest Cast", "screen_type": "card_select"},
               {"action": "choose", "index": 1})
    assert d.fight.turns == 2
    assert d.fight.selectors == [[2, "card_select", 1, "Guest Cast", PAIR]]


def test_the_screen_type_is_lowercased_however_the_screen_was_reached():
    """The P1.5 live run's one found defect: `naming.describe` lowercases and
    the blob fallback did not, so one screen wrote two spellings into the
    channel whose entire job is to be compared."""
    d = _driver()
    fight = _combat()
    d._observe(fight, fight, {}, {"action": "noop"})
    d._observe({"state_type": "card_select", "run": {"act": 1, "floor": 3},
                "player": {"hp": 50, "max_hp": 71},
                "card_select": {"screen_type": "NCombatPileCardSelectScreen",
                                "cards": [{"name": c} for c in PAIR]}},
               fight, {"card_name": "Center Stage"},
               {"action": "choose", "index": 0})
    assert d.fight.selectors[0][1] == "ncombatpilecardselectscreen"


def test_the_reader_needs_the_offer_list_to_have_held_both_answers():
    """Restated on the FIXTURE side of the wire: a row whose offer list is
    missing entirely is not read as an answer. This is the reader's stated
    rule (`replay.SPOTLIGHT_OFFERS`), and it is what makes a short row silent
    rather than loud -- see the slice-02 write-up."""
    assert replay._selector_choice(
        {"selectors": [[1, "card_select", 1, "Guest Cast", PAIR]]}, 1) == "companion"
    assert replay._selector_choice(
        {"selectors": [[1, "card_select", 1, "Guest Cast", []]]}, 1) is None
