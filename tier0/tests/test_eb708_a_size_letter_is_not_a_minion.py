"""`EB-708`: the enemy legend says `(S)`/`(M)`/`(L)` are sizes, and that Minion
is a printed status.

THE FIND (Kokomi r31 lane 2, (c)). `Twig Slime (M)` and `Leaf Slime (S)` read
as MINION MARKERS against a Plan rule written in terms of Minion, and the seat
guessed whether a single-target Plan could hit them. The letters are part of
the name the GAME prints; the page had a legend for the `[A]` handle beside
them and none for these, so a screen carrying two bracketed conventions
explained one.

THE NOTE IS NOT A CLAIM ABOUT ANY BODY. It says what the brackets are and
where the Minion answer actually lives -- on the body's own status line, which
is the same row `mark_front` reads to decide the FRONT. So the two assertions
below are one fact checked from both ends: the note prints, and the screen it
prints on does carry the `Minion` line it sends the reader to.
"""

from __future__ import annotations

from understudy import blindplay

MINION_STATUS = {"name": "Minion", "amount": 1, "type": "Buff",
                 "description": "This creature is a Minion."}


def _body(entity: str, cid: int, name: str, hp: int, status=()) -> dict:
    return {"entity_id": entity, "combat_id": cid, "name": name, "hp": hp,
            "max_hp": hp, "block": 0,
            "intents": [{"type": "Attack", "damage": 5}],
            "status": list(status)}


def _combat(enemies: list[dict]) -> dict:
    return {"state_type": "monster",
            "player": {"character": "kokomi", "hp": 60, "max_hp": 80,
                       "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                       "potions": [], "relics": [], "status": [],
                       "draw_pile_count": 5, "discard_pile_count": 0,
                       "exhaust_pile_count": 0},
            "battle": {"round": 2, "enemies": enemies}}


SLIMES = [_body("SLIME_M", 1, "Twig Slime (M)", 12),
          _body("SLIME_S", 2, "Leaf Slime (S)", 6, [MINION_STATUS]),
          _body("PRIEST", 3, "Priest", 30)]


def test_a_board_with_a_size_letter_prints_the_legend_for_it():
    page = blindplay.observe(_combat(SLIMES))
    assert "is its SIZE" in page
    assert "`(S)` small, `(M)` medium, `(L)` large" in page


def test_the_legend_says_minion_is_a_printed_status():
    page = blindplay.observe(_combat(SLIMES))
    assert "Minion is a printed status" in page
    # and the line it sends the reader to is on this very screen
    assert "Minion 1" in page


def test_the_body_wearing_no_minion_line_is_the_one_an_aim_lands_on():
    """The seat's actual question, answered by the rows rather than the note:
    the sized body with no Minion status is the FRONT."""
    page = blindplay.observe(_combat(SLIMES))
    front = next(l for l in page.splitlines() if "FRONT" in l and "**" in l)
    assert "Twig Slime (M)" in front


def test_a_board_with_no_size_letter_does_not_carry_the_legend():
    """Once per screen and only where a size letter does -- the rule every
    other note in the enemy block is under."""
    page = blindplay.observe(_combat([
        _body("PRIEST", 1, "Priest", 30),
        _body("FOLLOWER", 2, "Follower", 10, [MINION_STATUS])]))
    assert "is its SIZE" not in page


def test_the_legend_prints_once_however_many_sized_bodies_there_are():
    page = blindplay.observe(_combat(SLIMES))
    assert page.count("is its SIZE") == 1
