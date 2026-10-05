"""Seat page 4 (2026-10-05): the HP an incoming hit leaves, and the rest
site's healing room. From the Sonnet effort test
(review/records/sonnet-effort-test-2026-10-05.md)."""
from __future__ import annotations

from understudy import blindplay_render


def _rest_obs(hp: int, max_hp: int) -> dict:
    return {"state_type": "rest_site", "screen": "rest_site", "blocked": None,
            "hp": hp, "max_hp": max_hp, "gold": 99, "commands": [], "guardrail": "",
            "options": [{"name": "Rest", "description": "Heal 24 HP.",
                         "enabled": True}]}


def test_rest_site_prints_the_healing_room():
    page = blindplay_render.render(_rest_obs(62, 80))
    assert "HP 62/80 (healing stops at max HP: at most 18 more)" in page


def test_rest_site_at_full_hp_prints_no_room():
    page = blindplay_render.render(_rest_obs(80, 80))
    assert "healing stops" not in page


def test_incoming_line_says_the_hp_it_leaves():
    you = {"hp": 30, "max_hp": 80, "block": 4, "status": []}
    enemies = [{"name": "Nibbit", "hp": 20, "intents": [
        {"type": "Attack", "label": "12", "title": "Butt"}]}]
    assert blindplay_render._incoming_line(enemies, you) == (
        "- Incoming this turn: 12 (your Block 4): you would take 8. "
        "You would be at 22/80 HP.")


def test_incoming_line_fully_blocked_adds_nothing():
    you = {"hp": 30, "max_hp": 80, "block": 20, "status": []}
    enemies = [{"name": "Nibbit", "hp": 20, "intents": [
        {"type": "Attack", "label": "12", "title": "Butt"}]}]
    assert blindplay_render._incoming_line(enemies, you).endswith(
        "you would take 0.")
