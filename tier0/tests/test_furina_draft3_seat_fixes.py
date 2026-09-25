"""Furina, the Stage -- the draft-3 seat round (two Opus seats, 0.2.3778).

This file pins the PAGE halves; the mod halves are
`klee-mod/KleeTests/Prototype/FurinaStageDraft3SeatFixTests.cs`, and the
sim's are in `test_furina_stage.py`.

  1. A hit's Bow is paid right after the hit, on the enemy's turn too ([USER],
     2026-09-25 evening, overruling the wait #676 built), so the hit line
     folds the Bow in and nothing on the page says a Bow is waiting.
  2. A Spend is a line on the stage log.
  3. Chevalmarin's act says what each enemy was dealt and how many it struck
     ("2 damage to each of 4 enemies"), and by how much their HP fell where a
     Block (a Phantasmal Gardener's Skittish) ate some.
  4. "What you played" names the performer a random summon rolled.
  5. "Elemental Reaction" printed on a face is defined even on a screen whose
     cards bear no element (Courtroom Drama on a reward screen).

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

from __future__ import annotations

import pytest

from understudy import blindplay, qa_packet
from understudy.blindplay_board import furina_stage, resolutions
from understudy.blindplay_notes import ARM_KEYWORDS, keyword_notes
from understudy.blindplay_observe import observation
from understudy.blindplay_render import (_render_stage, _render_stage_log,
                                         _resolution_lines)


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def _row(event, member="usher", name="Gentilhomme Usher", **kw):
    """A log row in the mod's own shape (`FurinaStageLedger.Snapshot`)."""
    row = {"event": event, "member": member, "name": name, "seat": 0,
           "fanfare": 0, "moved": 0, "reason": "", "target": "",
           "target_id": "", "each": -1, "hp": -1, "struck": -1}
    row.update(kw)
    return row


def _stage(*log, seats=()):
    return furina_stage({"furina_stage": {
        "live": True, "seats": list(seats), "log": list(log)}})


def _state(log, resolved=None):
    """A Furina combat screen with a stage and this log."""
    player = {
        "character": "Furina", "hp": 60, "max_hp": 78, "block": 0,
        "energy": 3, "max_energy": 3, "gold": 0,
        "hand": [{"id": "x", "name": "Stage Presence",
                  "description": "Gain 5 Block.", "cost": "1",
                  "can_play": True, "target_type": "Self"}],
        "draw_pile_count": 5, "discard_pile_count": 2,
        "exhaust_pile_count": 0, "draw_pile": [], "discard_pile": [],
        "exhaust_pile": [], "relics": [], "potions": [], "status": [],
        "resources": {}, "pets": [],
        "furina_stage": {
            "live": True, "log": log,
            "seats": [{"member": "chevalmarin",
                       "name": "Surintendante Chevalmarin", "seat": 0,
                       "fanfare": 4, "entity_id": "7"}]},
    }
    if resolved is not None:
        player["resolutions"] = resolved
    return {
        "state_type": "monster", "screen": "combat", "floor": 3,
        "battle": {"round": 3}, "player": player,
        "enemies": [{"name": "Seapunk", "hp": 20, "max_hp": 44,
                     "block": 0, "combat_id": "1",
                     "intents": [{"kind": "attack", "amount": 7}],
                     "status": []}],
    }


# ---------------------------------------------------------------------------
# 1. A HIT'S BOW IS PAID RIGHT AFTER THE HIT.
# ---------------------------------------------------------------------------

def test_a_hits_bow_folds_into_the_hit_line():
    stage = _stage(
        _row("hit", fanfare=0, moved=3, target="Seapunk", target_id="1"),
        _row("leave", seat=-1, moved=3, reason="hit"))
    assert _render_stage_log(stage) == [
        "  - **Seapunk** hit **Usher** for 3: 3 → 0, and it leaves the "
        "stage: emptied by a hit, so it takes a Bow."]


def test_nothing_on_the_stage_block_says_a_bow_waits():
    stage = _stage(seats=[{"member": "usher", "name": "Gentilhomme Usher",
                           "seat": 0, "fanfare": 3}])
    assert "owed_bows" not in stage
    lines = _render_stage(stage, {"block": 0, "hp": 50, "max_hp": 78})
    assert not [line for line in lines if "waits" in line]


def test_the_bow_row_is_the_plain_exit():
    # The Guest Cast (2026-09-25): and a guest's Bow does not pay.
    assert ARM_KEYWORDS["Bow"] == (
        "A performer that leaves the stage acts one last time on its way "
        "out, without paying.")


# ---------------------------------------------------------------------------
# 2. THE SPEND LINE.
# ---------------------------------------------------------------------------

def test_a_spend_is_a_line_on_the_stage_log():
    stage = _stage(_row("raise", fanfare=8, moved=5),
                   _row("spend", fanfare=5, moved=3))
    assert _render_stage_log(stage)[-1] == (
        "  - Spent 3 of **Usher**'s Fanfare: 8 → 5.")


# ---------------------------------------------------------------------------
# 3. CHEVALMARIN'S ACT.
# ---------------------------------------------------------------------------

def _cheval(**kw):
    return _row("act", member="chevalmarin",
                name="Surintendante Chevalmarin", **kw)


def test_chevalmarin_says_what_each_enemy_was_dealt():
    stage = _stage(_cheval(moved=8, each=2, struck=4))
    assert _render_stage_log(stage) == [
        "  - **Chevalmarin** acted: 2 damage to each of 4 enemies."]


def test_where_a_block_ate_some_the_line_says_what_their_hp_lost():
    """The lane-2 elite: four Phantasmal Gardeners, one of whose 2 its
    Skittish Block ate. The act was right; the page now says so."""
    stage = _stage(_cheval(moved=6, each=2, struck=4))
    assert _render_stage_log(stage) == [
        "  - **Chevalmarin** acted: 2 damage to each of 4 enemies (their HP "
        "fell by 6 in all)."]


def test_one_enemy_and_an_uneven_sweep_read_plainly():
    assert _render_stage_log(_stage(_cheval(moved=2, each=2, struck=1))) == [
        "  - **Chevalmarin** acted: 2 damage to its one enemy."]
    assert _render_stage_log(_stage(_cheval(moved=5, struck=2))) == [
        "  - **Chevalmarin** acted: 5 in total across 2 enemies."]


def test_an_older_build_without_the_count_reads_as_before():
    assert _render_stage_log(_stage(_cheval(moved=6))) == [
        "  - **Chevalmarin** acted: 6 in total, split across the enemies."]


# ---------------------------------------------------------------------------
# 4. A RANDOM SUMMON NAMES WHO IT ROLLED.
# ---------------------------------------------------------------------------

def _resolved(card, summoned):
    return {"card_id": "x", "card": card, "auto_played": False,
            "carried": False, "overflowed": False, "hits": [],
            "summoned": summoned}


def test_what_you_played_names_the_summoned_performer():
    rows = resolutions({"resolutions": [
        _resolved("Take the Stage",
                  [{"member": "crabaletta",
                    "name": "Mademoiselle Crabaletta"}]),
        _resolved("Double Casting",
                  [{"member": "usher", "name": "Gentilhomme Usher"},
                   {"member": "chevalmarin",
                    "name": "Surintendante Chevalmarin"}])]})
    assert rows[0]["summoned"] == ["Crabaletta"]
    lines = _resolution_lines(rows, stage=True)
    assert lines[:2] == ["- **Take the Stage**",
                         "  It summoned **Crabaletta**."]
    assert "  It summoned **Usher** and **Chevalmarin**." in lines


# ---------------------------------------------------------------------------
# 5. THE WHOLE PAGE, AND THE PACKET STAYS BLIND.
# ---------------------------------------------------------------------------

def test_the_new_beats_cross_the_packet_and_print():
    state = _state(
        [_row("spend", fanfare=5, moved=3),
         _row("hit", fanfare=0, moved=3, target="Seapunk", target_id="1"),
         _row("leave", seat=-1, moved=3, reason="hit"),
         _cheval(moved=6, each=2, struck=4)],
        resolved=[_resolved("Understudy",
                            [{"member": "crabaletta",
                              "name": "Mademoiselle Crabaletta"}])])
    assert qa_packet.leaks(observation(state)) == []
    page = blindplay.observe(state)
    assert qa_packet.leaks(page) == []
    assert "Spent 3 of **Usher**'s Fanfare: 8 → 5." in page
    assert "emptied by a hit, so it takes a Bow." in page
    assert "waits for your turn" not in page
    assert "2 damage to each of 4 enemies (their HP fell by 6 in all)" in page
    assert "It summoned **Crabaletta**." in page


# ---------------------------------------------------------------------------
# 6. "ELEMENTAL REACTION" IS DEFINED WHERE A FACE PRINTS IT.
# ---------------------------------------------------------------------------

def test_the_umbrella_word_is_defined_on_a_screen_with_no_element():
    obs = {"state_type": "card_reward", "player": {"character": "Furina"},
           "card_reward": {"cards": [{
               "name": "Courtroom Drama",
               "description": "Your first Elemental Reaction each turn "
                              "applies 1 Vulnerable and 1 Weak to its target "
                              "before the hit lands."}]}}
    rows = {row["name"]: row["text"] for row in keyword_notes(obs)}
    assert rows["Elemental Reaction"] == (
        "A hit of a different element than the aura an enemy is already "
        "wearing.")


def test_a_screen_that_never_prints_it_raises_no_umbrella():
    obs = {"state_type": "card_reward", "player": {"character": "Furina"},
           "card_reward": {"cards": [{"name": "Stage Presence",
                                      "description": "Gain 5 Block."}]}}
    assert "Elemental Reaction" not in {
        row["name"] for row in keyword_notes(obs)}
