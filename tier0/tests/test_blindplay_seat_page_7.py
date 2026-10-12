"""Seat page 7 (2026-10-05), rewritten by the Kokomi re-founding (2026-10-12).

The page first counted a waiting Dusk Plan's Block into the incoming line: a
Kokomi seat read that line overstating the damage, because the Bake-Kurage
carried a Dusk Plan out at the END of the turn, before the enemies act. Dusk
left with the re-founding, and what lands at that moment for her now is the
Tamakushi Casket: "At the end of your turn, if a Plan is waiting, gain 3
Block." (its Watatsumi upgrade the same at 5).

Seat page 6's rule: counted where the wire gives the number (the relic's own
text, and the queue the page prints), named where it does not.
"""
from __future__ import annotations

from understudy import blindplay_render

line = blindplay_render._incoming_line

CASKET = {"name": "Tamakushi Casket",
          "text": "At the end of your turn, if a Plan is waiting, gain 3 "
                  "Block."}
WATATSUMI = {"name": "Watatsumi Casket",
             "text": "At the end of your turn, if a Plan is waiting, gain 5 "
                     "Block."}


def _you(hp=60, max_hp=80, block=0, relics=()):
    return {"hp": hp, "max_hp": max_hp, "block": block, "powers": [],
            "relics": list(relics), "orbs": None}


def _hit(n: int, name="Nibbit") -> dict:
    return {"name": name, "hp": 20, "intents": [
        {"type": "Attack", "label": str(n), "title": "Butt"}]}


def _plans(*queue: dict, twice=False) -> dict:
    return {"pet": True, "pet_name": "Bake-Kurage", "pending": len(queue),
            "twice": twice, "queue": list(queue)}


MORNING = {"name": "Slack Water", "clauses": 1, "plan_line": ""}


def test_the_casket_block_is_counted_while_a_plan_waits():
    plans = _plans(MORNING)
    assert line([_hit(12)], _you(relics=[CASKET]), [], [], plans) == (
        "- Incoming this turn: 12 (your Block 0): you would take 9 "
        "(Tamakushi Casket adds 3 Block first). "
        "You would be at 51/80 HP.")


def test_the_upgrade_is_counted_at_its_own_number():
    plans = _plans(MORNING)
    assert "Watatsumi Casket adds 5 Block first" in line(
        [_hit(12)], _you(relics=[WATATSUMI]), [], [], plans)


def test_no_plan_waiting_no_casket_block():
    """The condition is the queue: empty or absent, nothing is folded and the
    relic is not named either -- the page knows it gives nothing."""
    plain = line([_hit(12)], _you(hp=30, block=4), [], [])
    assert plain == ("- Incoming this turn: 12 (your Block 4): you would "
                     "take 8. You would be at 22/80 HP.")
    for plans in (None, _plans()):
        assert line([_hit(12)], _you(hp=30, block=4, relics=[CASKET]), [],
                    [], plans) == plain


def test_orichalcum_is_named_beside_a_counted_casket():
    """The two share one end-of-turn moment; which lands first is not on the
    page."""
    orichalcum = {"name": "Orichalcum",
                  "text": "If you end your turn without Block, gain 6 Block."}
    got = line([_hit(12)], _you(relics=[CASKET, orichalcum]), [], [],
               _plans(MORNING))
    assert "you would take 9" in got
    assert got.endswith(" Not counted: Orichalcum.")


def test_the_page_passes_the_plan_queue_to_the_line():
    """End to end: a queue on the wire and the relic on the belt reach the
    incoming line."""
    from understudy import blindplay
    state = {"state_type": "monster",
             "player": {"character": "Kokomi", "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [],
                        "relics": [{"id": "KLEEMOD-TAMAKUSHI_CASKET",
                                    "name": "Tamakushi Casket",
                                    "description": CASKET["text"]}],
                        "status": [],
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0,
                        "kokomi_plans": {
                            "pet": True, "pet_name": "Bake-Kurage",
                            "pet_entity_id": "KURAGE", "pending": 1,
                            "twice": False, "carried_out": [],
                            "queue": [{"name": "Breakwater",
                                       "clauses": 1}]}},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "label": "10",
                               "title": "Bite"}],
                  "status": []}]}}
    page = blindplay.observe(state)
    assert "(Tamakushi Casket adds 3 Block first)" in page
