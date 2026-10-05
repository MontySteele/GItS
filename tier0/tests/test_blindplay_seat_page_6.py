"""Seat page 6 (2026-10-05): the incoming line knows what it leaves out.

Base-game Sonnet seats read "you would be at 0" and lived, or the reverse,
because the line summed the telegraphs against Block and nothing else:

1. Osty takes the unblocked part of an attack up to his HP (`DieForYouPower`).
2. Beating Remnant stops the turn's HP loss at 20.
3. Frost orbs (and Orichalcum, Plating) add Block before the enemies act.
4. Burn, Decay, Disintegration, Constrict hurt at the end of your turn.

Counted where the wire gives the number, said in a few words; named where it
does not. Never a plan.
"""
from __future__ import annotations

from understudy import blindplay, blindplay_render

line = blindplay_render._incoming_line


def _you(hp=60, max_hp=80, block=0, powers=(), relics=(), orbs=None):
    return {"hp": hp, "max_hp": max_hp, "block": block,
            "powers": list(powers), "relics": list(relics), "orbs": orbs}


def _hit(n: int, name="Nibbit") -> list[dict]:
    return [{"name": name, "hp": 20, "intents": [
        {"type": "Attack", "label": str(n), "title": "Butt"}]}]


def _power(name: str, stacks: int) -> dict:
    return {"name": name, "stacks": stacks, "text": ""}


def _card(title: str, text: str) -> dict:
    return {"title": title, "text": text}


BURN = _card("Burn", "Unplayable. At the end of your turn, if this is in "
                     "your Hand, take 2 damage.")
BAD_LUCK = _card("Bad Luck", "Unplayable. At the end of your turn, if this "
                             "is in your Hand, lose 3 HP.")
REMNANT = {"name": "Beating Remnant",
           "text": "You cannot lose more than 20 HP in a single turn."}
ORICHALCUM = {"name": "Orichalcum",
              "text": "If you end your turn without Block, gain 6 Block."}


# ------------------------------------------------------------ plain case --

def test_the_plain_line_is_unchanged():
    assert line(_hit(12), _you(hp=30, block=4), [], []) == (
        "- Incoming this turn: 12 (your Block 4): you would take 8. "
        "You would be at 22/80 HP.")


def test_a_hand_with_nothing_that_hurts_adds_nothing():
    hand = [_card("Strike", "Deal 6 damage.")]
    assert line(_hit(12), _you(block=4), hand, []).endswith(
        "you would take 8. You would be at 52/80 HP.")


# --------------------------------------------------------------- 1. Osty --

OSTY = {"name": "Osty", "hp": 8, "max_hp": 9, "block": 0, "powers": [],
        "absorbs": True}


def test_osty_absorbs_the_unblocked_damage_up_to_his_hp():
    assert line(_hit(15), _you(block=0), [], [OSTY]) == (
        "- Incoming this turn: 15 (your Block 0): you would take 7 "
        "(Osty absorbs up to 8). You would be at 53/80 HP.")


def test_a_downed_osty_absorbs_nothing():
    down = dict(OSTY, hp=0)
    assert line(_hit(15), _you(), [], [down]).endswith(
        "you would take 15. You would be at 45/80 HP.")


def test_osty_is_not_named_when_block_takes_it_all():
    assert "Osty" not in line(_hit(5), _you(block=10), [], [OSTY])


def test_the_page_marks_osty_off_the_wire():
    """End to end: the Necrobinder board's Osty row reaches the line."""
    state = {"state_type": "monster",
             "player": {"character": "Necrobinder", "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": [], "status": [],
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0,
                        "pets": [{"id": "OSTY", "entity_id": "7",
                                  "name": "Osty", "alive": True, "hp": 6,
                                  "max_hp": 9, "block": 0, "status": []}]},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "label": "10",
                               "title": "Bite"}],
                  "status": []}]}}
    page = blindplay.observe(state)
    assert ("- Incoming this turn: 10 (your Block 0): you would take 4 "
            "(Osty absorbs up to 6). You would be at 56/80 HP.") in page


# ---------------------------------------------------- 2. Beating Remnant --

def test_beating_remnant_caps_the_take():
    assert line(_hit(30), _you(relics=[REMNANT]), [], []) == (
        "- Incoming this turn: 30 (your Block 0): you would take 20 "
        "(Beating Remnant caps the turn's HP loss at 20). "
        "You would be at 40/80 HP.")


def test_beating_remnant_says_nothing_under_its_cap():
    assert "Remnant" not in line(_hit(12), _you(relics=[REMNANT]), [], [])


def test_beating_remnant_is_named_where_the_take_is_unknown():
    weak = [{"name": "Rocket", "hp": 20, "powers": [_power("Weak", 1)],
             "intents": [{"type": "Attack", "label": "9", "title": "Beam"}]}]
    out = line(weak, _you(relics=[REMNANT]), [], [])
    assert "plus an unknown amount from Rocket" in out
    assert "Beating Remnant caps the turn's HP loss at 20" in out


# ------------------------------------------------- 3. end-of-turn Block --

FROST = {"name": "Frost", "passive": 3, "evoke": 5, "text": ""}


def test_frost_orbs_add_their_block_first():
    orbs = {"slots": 3, "list": [FROST, FROST]}
    assert line(_hit(10), _you(orbs=orbs), [], []) == (
        "- Incoming this turn: 10 (your Block 0): you would take 4 "
        "(Frost x2 add 6 Block first). You would be at 56/80 HP.")


def test_lightning_adds_no_block():
    orbs = {"slots": 3, "list": [{"name": "Lightning", "passive": 3,
                                  "evoke": 8, "text": ""}]}
    assert line(_hit(10), _you(orbs=orbs), [], []).endswith(
        "you would take 10. You would be at 50/80 HP.")


def test_orichalcum_counts_only_with_no_block_up():
    assert "(Orichalcum adds 6 Block first)" in line(
        _hit(10), _you(relics=[ORICHALCUM]), [], [])
    assert "Orichalcum" not in line(
        _hit(10), _you(block=2, relics=[ORICHALCUM]), [], [])


def test_plating_adds_its_stacks():
    out = line(_hit(10), _you(powers=[_power("Plating", 4)]), [], [])
    assert "you would take 6 (Plating adds 4 Block first)" in out


def test_the_page_folds_the_wires_frost_orb():
    """End to end: the Defect board's orb rows reach the line."""
    state = {"state_type": "monster",
             "player": {"character": "Defect", "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": [], "status": [],
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0, "orb_slots": 3,
                        "orbs": [{"id": "FROST_ORB", "name": "Frost",
                                  "passive_val": 2, "evoke_val": 5,
                                  "description": "Passive: At the end of "
                                  "turn, gain 2 Block."}]},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "label": "10",
                               "title": "Bite"}],
                  "status": []}]}}
    page = blindplay.observe(state)
    assert ("- Incoming this turn: 10 (your Block 0): you would take 8 "
            "(Frost adds 2 Block first). You would be at 52/80 HP.") in page


# ------------------------------------------------ 4. end-of-turn damage --

def test_burns_in_hand_and_disintegration_eat_block_then_hp():
    hand = [BURN, dict(BURN, title="Burn (2)")]
    you = _you(block=5, powers=[_power("Disintegration", 3)])
    assert line(_hit(6), you, hand, []) == (
        "- Incoming this turn: 6 (your Block 5): you would take 8 "
        "(Disintegration and Burn x2 hit you for 7 first). "
        "You would be at 52/80 HP.")


def test_hp_loss_cards_skip_block():
    assert "you would take 3 (Bad Luck costs 3 HP)" in line(
        _hit(6), _you(block=10), [BAD_LUCK], [])


def test_burn_with_no_attack_still_prints_the_take():
    assert line([], _you(), [BURN], []) == (
        "- Incoming this turn: no attack is shown (your Block 0): you would "
        "take 2 (Burn hits you for 2 first). You would be at 58/80 HP.")


def test_regret_and_intangible_are_named_not_counted():
    out = line(_hit(6), _you(powers=[_power("Intangible", 1)]),
               [_card("Regret", "Unplayable. At the end of your turn, lose "
                                "1 HP for each card in your Hand.")], [])
    assert out.endswith("you would take 6. You would be at 54/80 HP. "
                        "Not counted: Intangible and Regret.")


def test_no_attack_and_nothing_that_hurts_is_unchanged():
    assert line([], _you(), [], []) == blindplay_render.INCOMING_NONE
