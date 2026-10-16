"""The Kokomi round 7 display fixes (2026-10-14), from that day's blind seats.

1. The Energy line named Prismatic Gem (whose Energy is already in "N a
   turn") and called the Tea Set's 2 "from this turn's plays" on turn 1.
2. A Plan's hit meets the Vulnerable an earlier Plan applies in the same
   morning; the Plan strip now says so.
3. Ringing counts a Plan that plays a card (a Companion), as it counts any
   card the game plays for you; the strip warns, and the turn says it.

The C# twin is `klee-mod/KleeTests/Prototype/KokomiRound7DisplayTests.cs`.
"""
from __future__ import annotations

from tier0.tests.test_understudy_blindplay import _past_lethal_state
from understudy import blindplay, blindplay_render

GEM = {"name": "Prismatic Gem",
       "text": "Gain 1 Energy at the start of each turn. Card rewards now "
               "contain cards from other colors."}
LANTERN = {"name": "Lantern",
           "text": "At the start of each combat, gain 1 Energy."}
TEA_SET = {"name": "Venerable Tea Set",
           "text": "Whenever you enter a Rest Site, start the next combat "
                   "with 2 Energy."}


# ---- 1: the Energy line ----------------------------------------------------

def test_the_seats_turn_one_names_lantern_and_the_tea_set_not_the_gem():
    you = {"energy": 7, "max_energy": 4, "relics": [GEM, LANTERN, TEA_SET]}
    assert blindplay_render._energy_line(you) == (
        "Energy 7 (4 a turn, +1 Lantern, +2 Venerable Tea Set)")


def test_an_every_turn_relic_is_never_a_bonus_on_top():
    you = {"energy": 6, "max_energy": 4, "relics": [GEM]}
    assert blindplay_render._energy_line(you) == (
        "Energy 6 (4 a turn, +2 from other effects)")


def test_a_used_up_relic_is_not_named():
    you = {"energy": 4, "max_energy": 3,
           "relics": [dict(TEA_SET, used_up=True)]}
    assert blindplay_render._energy_line(you) == (
        "Energy 4 (3 a turn, +1 from other effects)")


def test_the_line_under_the_turns_energy_is_unchanged():
    assert blindplay_render._energy_line(
        {"energy": 2, "max_energy": 4, "relics": [GEM]}) == (
        "Energy 2 left of 4")


# ---- 2: Vulnerable from an earlier Plan ---------------------------------------

def _body(name, cid):
    return {"entity_id": f"{name.upper()}_0", "combat_id": cid, "name": name,
            "hp": 40, "max_hp": 40, "block": 0, "status": [],
            "intents": [{"type": "Attack", "label": "7",
                         "title": "Aggressive",
                         "description": "This enemy intends to Attack for 7."}]}


def _page(queue, enemies=None):
    state = _past_lethal_state(queue=queue, hp=40, enemies=enemies)
    return blindplay.render(blindplay.observation(state)).splitlines()


def test_an_all_hit_behind_spearhead_counts_its_vulnerable():
    lines = _page([{"name": "Spearhead", "clauses": 1,
                    "vulnerable_aim": "all"},
                   {"name": "Sting", "clauses": 1, "aim": "all",
                    "written": 3}],
                  enemies=[_body("Beetle", 1), _body("Wurm", 2)])
    assert ("     - Lands 3 to ALL next turn (4 on Beetle, 4 on Wurm, after "
            "Vulnerable from Spearhead).") in lines


def test_a_front_hit_behind_a_front_vulnerable_counts_it():
    lines = _page([{"name": "Exposed Flank", "clauses": 1,
                    "vulnerable_aim": "front"},
                   {"name": "Kurage's Oath", "clauses": 1, "aim": "front",
                    "damage": 9, "written": 9}],
                  enemies=[_body("Beetle", 1)])
    assert ("     - Lands 9 at the front enemy next turn (13 after "
            "Vulnerable from Exposed Flank).") in lines


def test_a_hit_ahead_of_the_vulnerable_plan_is_not_raised():
    lines = _page([{"name": "Sting", "clauses": 1, "aim": "all",
                    "written": 3},
                   {"name": "Spearhead", "clauses": 1,
                    "vulnerable_aim": "all"}],
                  enemies=[_body("Beetle", 1)])
    assert "     - Lands 3 to ALL next turn." in lines


# ---- 3: Ringing -----------------------------------------------------------------

def test_a_card_playing_plan_warns_under_ringing():
    state = _past_lethal_state(
        queue=[{"name": "Jean — Gale Blade", "clauses": 1,
                "plays_card": True},
               {"name": "Kurage's Oath", "clauses": 1}], hp=40)
    state["player"] = dict(state["player"], status=[
        {"id": "RINGING_POWER", "name": "Ringing", "amount": 1,
         "type": "Debuff", "description": "You can only play 1 card."}])
    lines = blindplay.render(blindplay.observation(state)).splitlines()
    assert lines.count(
        "     - Ringing: a carried-out Plan uses your one card.") == 1
    at = lines.index("     - Ringing: a carried-out Plan uses your one card.")
    assert "Jean" in "".join(lines[at - 3:at])


def test_no_ringing_warning_without_ringing():
    lines = _page([{"name": "Jean — Gale Blade", "clauses": 1,
                    "plays_card": True}])
    assert not any("Ringing:" in line for line in lines)


def test_an_intended_ringing_counts():
    enemies = [{"intents": [{"type": "Debuff",
                             "effect": "applies Ringing 1"}]}]
    assert blindplay_render._ringing_on_or_coming({}, enemies)
    assert not blindplay_render._ringing_on_or_coming({}, [{"intents": []}])


def test_the_ringing_turn_names_the_card_played_for_you():
    you = {"powers": [{"name": "Ringing", "stacks": 1}]}
    rows = [{"card": "Jean — Gale Blade", "auto_played": True},
            {"card": "Strike", "auto_played": False}]
    assert blindplay_render._ringing_used_lines(you, rows) == [
        "", "- Ringing: **Jean — Gale Blade** was played for you, which "
            "used your one card this turn."]
    assert blindplay_render._ringing_used_lines({"powers": []}, rows) == []
