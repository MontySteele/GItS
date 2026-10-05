"""Seat page 7 (2026-10-05): the incoming line counts Dusk Plan Block.

A Kokomi seat read the incoming line overstating the damage in two fights:
the Bake-Kurage carries a waiting Dusk Plan out at the END of this turn,
before the enemies act, and the line left its Block out.

Seat page 6's rule: counted where the wire gives the number (the entry's
own Plan text, `plan_line`, numbers filled), named where it does not.
`KokomiPlan.QueueRow` sends a Dusk entry's Plan line off the card's rendered
face (`DuskPlanText`); an older bridge sends none, and the entry is named.
"""
from __future__ import annotations

from understudy import blindplay_render

line = blindplay_render._incoming_line


def _you(hp=60, max_hp=80, block=0, relics=()):
    return {"hp": hp, "max_hp": max_hp, "block": block, "powers": [],
            "relics": list(relics), "orbs": None}


def _hit(n: int, name="Nibbit") -> dict:
    return {"name": name, "hp": 20, "intents": [
        {"type": "Attack", "label": str(n), "title": "Butt"}]}


def _plans(*queue: dict, twice=False) -> dict:
    return {"pet": True, "pet_name": "Bake-Kurage", "pending": len(queue),
            "twice": twice, "queue": list(queue)}


def _entry(name: str, plan_line: str = "") -> dict:
    return {"name": name, "clauses": 1, "plan_line": plan_line}


MORNING = _entry("Slack Water")


def test_a_plain_dusk_block_is_counted():
    plans = _plans(_entry("Dusk: Shell of Sanctuary", "Gain 9 Block."))
    assert line([_hit(12)], _you(block=0), [], [], plans) == (
        "- Incoming this turn: 12 (your Block 0): you would take 3 "
        "(Shell of Sanctuary (Dusk Plan) adds 9 Block first). "
        "You would be at 57/80 HP.")


def test_nereids_ascension_counts_the_first_dusk_entry_twice():
    plans = _plans(_entry("Dusk: Shell of Sanctuary", "Gain 9 Block."),
                   twice=True)
    assert "Shell of Sanctuary (Dusk Plan) x2 add 18 Block first" in line(
        [_hit(20)], _you(), [], [], plans)


def test_a_per_plan_dusk_block_counts_the_plans_left_waiting():
    """Breakwater counts the queue once the Dusk entries are out of it."""
    plans = _plans(_entry("Dusk: Breakwater",
                          "Gain 5 Block, and 3 more for each Plan waiting."),
                   MORNING, MORNING)
    assert "Breakwater (Dusk Plan) adds 11 Block first" in line(
        [_hit(20)], _you(), [], [], plans)


def test_a_per_attacker_dusk_block_counts_the_attacks_shown():
    plans = _plans(_entry("Dusk: Evening Watch",
                          "Gain 5 Block for each enemy intending to attack."))
    buff = {"name": "Cultist", "hp": 30, "intents": [{"type": "Buff"}]}
    assert "Evening Watch (Dusk Plan) adds 10 Block first" in line(
        [_hit(6), _hit(6, "Louse"), buff], _you(), [], [], plans)


def test_double_your_block_is_named_not_counted():
    plans = _plans(_entry("Dusk: Brace for the Tide", "Double your Block."))
    got = line([_hit(12)], _you(block=4), [], [], plans)
    assert got.startswith("- Incoming this turn: 12 (your Block 4): "
                          "you would take 8.")
    assert got.endswith(" Not counted: Brace for the Tide (Dusk Plan).")


def test_a_dusk_entry_with_no_plan_text_on_the_wire_is_named():
    """An older bridge: the Dusk row carries its name and no Plan text."""
    plans = _plans({"name": "Dusk: Breakwater", "clauses": 2}, MORNING)
    got = line([_hit(12)], _you(), [], [], plans)
    assert "you would take 12." in got
    assert got.endswith(" Not counted: Breakwater (Dusk Plan).")


def test_orichalcum_is_named_when_a_dusk_block_is_counted():
    """Which of the two lands first is not on the page."""
    orichalcum = {"name": "Orichalcum",
                  "text": "If you end your turn without Block, gain 6 Block."}
    plans = _plans(_entry("Dusk: Shell of Sanctuary", "Gain 9 Block."))
    got = line([_hit(12)], _you(relics=[orichalcum]), [], [], plans)
    assert "you would take 3" in got
    assert got.endswith(" Not counted: Orichalcum.")


def test_no_dusk_entries_leave_the_line_unchanged():
    plain = line([_hit(12)], _you(hp=30, block=4), [], [])
    assert plain == ("- Incoming this turn: 12 (your Block 4): you would "
                     "take 8. You would be at 22/80 HP.")
    for plans in (None, _plans(), _plans(MORNING)):
        assert line([_hit(12)], _you(hp=30, block=4), [], [], plans) == plain


def test_the_page_passes_the_plan_queue_to_the_line():
    """End to end: a Dusk row on the wire reaches the incoming line."""
    from understudy import blindplay
    state = {"state_type": "monster",
             "player": {"character": "Kokomi", "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": [], "status": [],
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0,
                        "kokomi_plans": {
                            "pet": True, "pet_name": "Bake-Kurage",
                            "pet_entity_id": "KURAGE", "pending": 1,
                            "twice": False, "carried_out": [],
                            "queue": [{"name": "Dusk: Breakwater",
                                       "clauses": 2}]}},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "label": "10",
                               "title": "Bite"}],
                  "status": []}]}}
    page = blindplay.observe(state)
    assert "Not counted: Breakwater (Dusk Plan)." in page


def _wire_row(name: str, plan_line: str, clauses: int = 1) -> dict:
    """One queue row exactly as `KokomiPlan.QueueRow` sends a Dusk entry."""
    return {"name": name, "two_line": False, "now_line": "",
            "plan_line": plan_line, "line": "plan", "clauses": clauses,
            "damage": 0, "aim": ""}


def _kokomi_state(*queue: dict) -> dict:
    return {"state_type": "monster",
            "player": {"character": "Kokomi", "hp": 60, "max_hp": 80,
                       "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                       "potions": [], "relics": [], "status": [],
                       "draw_pile_count": 5, "discard_pile_count": 0,
                       "exhaust_pile_count": 0,
                       "kokomi_plans": {
                           "pet": True, "pet_name": "Bake-Kurage",
                           "pet_entity_id": "KURAGE",
                           "pending": len(queue), "twice": False,
                           "carried_out": [], "queue": list(queue)}},
            "battle": {"round": 2, "enemies": [
                {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                 "hp": 30, "max_hp": 44, "block": 0,
                 "intents": [{"type": "Attack", "label": "20",
                              "title": "Bite"}],
                 "status": []}]}}


def test_a_wire_breakwater_and_shell_of_sanctuary_are_counted():
    """End to end off realistic wire rows: Breakwater+ (7, and 3 for the one
    morning Plan left waiting) and Shell of Sanctuary (9)."""
    from understudy import blindplay
    morning = {"name": "Slack Water", "two_line": False, "now_line": "",
               "plan_line": "", "line": "plan", "clauses": 1,
               "damage": 6, "aim": "front"}
    page = blindplay.observe(_kokomi_state(
        _wire_row("Dusk: Breakwater+",
                  "Gain 7 Block, and 3 more for each Plan waiting.", 2),
        _wire_row("Dusk: Shell of Sanctuary", "Gain 9 Block."),
        morning))
    assert ("- Incoming this turn: 20 (your Block 0): you would take 1 "
            "(Breakwater+ (Dusk Plan) and Shell of Sanctuary (Dusk Plan) "
            "add 19 Block first). You would be at 59/80 HP.") in page
    assert "Not counted" not in page
