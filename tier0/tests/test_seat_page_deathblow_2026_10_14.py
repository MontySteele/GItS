"""Seat page, 2026-10-14: Waterfall Giant's Death Blow, and a leaked verb.

Two seats (Yae, Klee) killed the act-1 boss and then died to its Steam
Eruption ("When killed, deals N damage at the end of your next turn") while
the Incoming line counted nothing. And a refused `choose` at Neow told a seat
to use "[an internal id]" -- the bridge's own action name, redacted.
"""
from __future__ import annotations

import copy

from understudy import blindplay, blindplay_render, blindplay_session, qa_packet

from tier0.tests.test_understudy_blindplay import combat_state

line = blindplay_render._incoming_line

STEAM = {"name": "Steam Eruption", "stacks": 39, "kind": "Buff",
         "text": "When killed, deals 39 damage at the end of your next turn."}


def _you():
    return {"hp": 30, "max_hp": 80, "block": 0, "powers": [], "relics": [],
            "orbs": None}


def _giant(intents, hp=120, powers=(STEAM,)):
    flip = hp >= 100_000_000
    return {"name": "Waterfall Giant", "hp": hp, "max_hp": hp,
            "phase_flip": flip, "intents": intents, "powers": list(powers)}


def test_before_the_kill_the_line_says_what_killing_it_costs():
    got = line([_giant([{"type": "Attack", "label": "10"}])], _you())
    assert "you would take 10" in got
    assert ("Killing Waterfall Giant now: 39 damage at the end of your next "
            "turn (Steam Eruption).") in got


def test_after_the_kill_the_stun_turn_names_the_blow_coming():
    got = line([_giant([{"type": "Stun", "label": ""}], hp=999_999_999)],
               _you())
    assert ("Not this turn: Waterfall Giant deals 39 damage at the end of "
            "your next turn (Steam Eruption).") in got
    assert "Killing" not in got


def test_the_explode_turn_counts_the_death_blow():
    got = line([_giant([{"type": "DeathBlow", "label": "39"}],
                       hp=999_999_999, powers=())], _you())
    assert "Incoming this turn: 39" in got
    assert "you would take 39" in got
    assert "You would be at 0/80 HP." in got


def test_a_death_blow_with_its_breakdown_counts_the_game_number():
    intent = {"type": "DeathBlow", "label": "8", "breakdown": {
        "base": 8, "folded": 8, "repeats": 1, "total": 8, "modifiers": []}}
    got = line([{"name": "Gas Bomb", "hp": 7, "intents": [intent],
                 "powers": []}], _you())
    assert "you would take 8" in got


def test_a_power_with_no_number_in_its_text_uses_its_stacks():
    power = dict(STEAM, text="When killed, deals damage equal to this at "
                             "the end of your next turn.")
    got = line([_giant([{"type": "Buff", "label": ""}], powers=(power,))],
               _you())
    assert "Killing Waterfall Giant now: 39 damage" in got


def test_an_ordinary_phase_flip_attack_is_still_skipped():
    got = line([_giant([{"type": "Attack", "label": "12"}], hp=999_999_999,
                       powers=())], _you())
    assert got == blindplay_render.INCOMING_NONE


def test_the_new_lines_are_blind():
    for template in (blindplay_render.DEATH_BLOW_IF_KILLED,
                     blindplay_render.DEATH_BLOW_PENDING):
        qa_packet.assert_blind(template.format(
            name="Waterfall Giant", n=39, power="Steam Eruption"))


def test_the_combat_page_carries_it_off_the_wire():
    state = copy.deepcopy(combat_state())
    enemy = state["battle"]["enemies"][0]
    enemy.setdefault("status", []).append({
        "id": "STEAM_ERUPTION_POWER", "name": "Steam Eruption", "amount": 21,
        "type": "Buff",
        "description": "When killed, deals 21 damage at the end of your "
                       "next turn."})
    page = blindplay.observe(state)
    assert "now: 21 damage at the end of your next turn (Steam Eruption)." \
        in page


# ---- the refused choose at Neow ------------------------------------------

def test_the_dialogue_refusal_names_the_page_verb():
    got = blindplay_session._result_line({
        "status": "error",
        "error": "Ancient dialogue in progress - use advance_dialogue until "
                 "it ends, then choose"})
    assert "[an internal id]" not in got
    assert "type `proceed` until it ends, then choose" in got
    qa_packet.assert_blind(got)
