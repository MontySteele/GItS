"""Seat page 7 (2026-10-05), rewritten by the Kokomi re-founding and again by
the Casket's move to the start of the turn (both 2026-10-12).

The page first counted a waiting Dusk Plan's Block into the incoming line: a
Kokomi seat read that line overstating the damage, because the Bake-Kurage
carried a Dusk Plan out at the END of the turn, before the enemies act. Dusk
left with the re-founding, and the Tamakushi Casket's end-of-turn Block took
its place in the line. Then [USER] ruled: "For Kokomi - let's have her starter
relic apply block at the beginning of the turn rather than the end." The
Casket now reads "At the start of your turn, if a Plan is waiting, gain 3
Block." (its Watatsumi upgrade the same at 5): its Block lands after the hits
the incoming line is about, so the line neither counts it nor names it.
"""
from __future__ import annotations

from understudy import blindplay_render

line = blindplay_render._incoming_line

CASKET = {"name": "Tamakushi Casket",
          "text": "At the start of your turn, if a Plan is waiting, gain 3 "
                  "Block."}
WATATSUMI = {"name": "Watatsumi Casket",
             "text": "At the start of your turn, if a Plan is waiting, gain 5 "
                     "Block."}


def _you(hp=60, max_hp=80, block=0, relics=()):
    return {"hp": hp, "max_hp": max_hp, "block": block, "powers": [],
            "relics": list(relics), "orbs": None}


def _hit(n: int, name="Nibbit") -> dict:
    return {"name": name, "hp": 20, "intents": [
        {"type": "Attack", "label": str(n), "title": "Butt"}]}


PLAIN = ("- Incoming this turn: 12 (your Block 0): you would take 12. "
         "You would be at 48/80 HP.")


def test_neither_casket_is_counted_before_the_hits():
    for relic in (CASKET, WATATSUMI):
        assert line([_hit(12)], _you(relics=[relic]), [], []) == PLAIN


def test_orichalcum_beside_the_casket_is_counted_as_usual():
    """The two no longer share the end-of-turn moment, so Orichalcum is
    folded in on its own number."""
    orichalcum = {"name": "Orichalcum",
                  "text": "If you end your turn without Block, gain 6 Block."}
    got = line([_hit(12)], _you(relics=[CASKET, orichalcum]), [], [])
    assert "you would take 6" in got
    assert "Not counted" not in got


def test_the_page_does_not_fold_the_casket_with_a_plan_waiting():
    """End to end: a queue on the wire and the relic on the belt leave the
    incoming line at the telegraph."""
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
    assert "Tamakushi Casket adds" not in page
    assert "you would take 10" in page
