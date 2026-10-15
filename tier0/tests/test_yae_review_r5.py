"""Yae review r5, items 1 to 7 (review/active/yae-review-r5-2026-10-15.md).
Sim and page half; the C# half is
`klee-mod/KleeTests/Prototype/YaeReviewR5Tests.cs`. Item 1's page test is
`test_yae_seat_page.test_a_multi_card_edit_is_one_chooser_of_up_to_n`."""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy
from understudy import blindplay_faces, blindplay_notes, blindplay_render

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _state():
    enemies = [Enemy(hp=100, max_hp=100, name="e0",
                     intents=[{"kind": "block", "amount": 0}])]
    p = Y.build_player()
    p.draw_pile = []
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _play(st, card):
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _nothing(st):
    return [e for e in st.log if e.get("event") == "yae_edit_nothing"]


# 1. The "up to N" Edit chooser ----------------------------------------------

def test_the_up_to_chooser_marks_what_an_edit_replaces():
    faces = [{"enchantment": {"name": "Annotated",
                              "text": "This combat: Footnote."}}]
    blindplay_faces.mark_edit_replaces(
        "Choose up to 2 cards to Edit: Red Ink (x).", faces)
    assert faces[0]["replaces"] == "Footnote"


def test_the_glossary_edit_row_says_one_chooser():
    row = blindplay_notes.ARM_KEYWORDS["Edit"]
    assert "one chooser" in row and "twice" not in row
    assert blindplay_notes.ARM_KEYWORDS["Full shrine"] == (
        FULL_SHRINE[0].upper() + FULL_SHRINE[1:])


# 2. Inked Branches+ with nothing to Edit says so once ------------------------

def test_inked_branches_plus_with_nothing_says_nothing_to_edit_once():
    st = _state()
    st.player.hand[:] = []
    _play(st, loader.get_card("proto_ym_inked_branches+"))
    assert [e.get("what") for e in _nothing(st)] == ["hand"]


def test_inked_branches_plus_that_edited_a_sakura_is_quiet_about_the_hand():
    st = _state()
    Y.plant(st, 1)
    st.player.hand[:] = []
    _play(st, loader.get_card("proto_ym_inked_branches+"))
    assert _nothing(st) == []
    assert Y.ledger(st.player).sakura[0].annotation == Y.RED_INK


def test_plain_inked_branches_with_no_sakura_still_says_so():
    st = _state()
    _play(st, loader.get_card("proto_ym_inked_branches"))
    assert [e.get("what") for e in _nothing(st)] == ["sakura"]


# 3. A replay whose target died hits nothing ---------------------------------

def test_a_replayed_card_that_killed_says_a_dead_target_is_not_hit_again():
    rows = [{"card": "Thunderbolt Tithe", "play_count": 2,
             "killed": ["Nibbit"],
             "hits": [{"target": "Nibbit", "amount": 14, "blocked": 0,
                      "killed": True}]}]
    line = blindplay_render._resolution_lines(rows)[0]
    assert "played two times" in line
    assert "does not pick a new target" in line
    plain = [{"card": "Strike", "play_count": 2, "hits": [
        {"target": "Nibbit", "amount": 6, "blocked": 0},
        {"target": "Nibbit", "amount": 6, "blocked": 0}]}]
    assert "new target" not in blindplay_render._resolution_lines(plain)[0]


# 5. Full shrine ---------------------------------------------------------------

FULL_SHRINE = ("planting makes your oldest Sakura act. If the new Sakura is "
               "the same kind, the oldest stays and gains a Level. If not, the "
               "oldest withers and the new one takes its place.")


def test_full_shrine_text_on_the_page_and_the_hover():
    assert blindplay_render.SHRINE_FULL_LINE == "- Shrine full: " + FULL_SHRINE
    tips = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
            / "ArmKeywordTips.cs").read_text(encoding="utf-8")
    assert '"Planting makes your oldest Sakura act. If the new Sakura is the same "' in tips


# 6. Meditations of a Yako -----------------------------------------------------

def test_meditations_says_the_annotation_was_made_that_fight():
    src = (REPO / "klee-mod" / "KleeCode" / "Relics"
           / "MeditationsOfAYako.cs").read_text(encoding="utf-8")
    assert '"Annotation you made that fight."' in src
    assert '"2 Annotations you made that fight."' in src


# 7. Sakura Seal and Footnote say what their Annotation does -----------------

def _row(card_id):
    import yaml
    rows = yaml.safe_load((REPO / "docs" / "prototype-surface.yaml")
                          .read_text(encoding="utf-8"))
    rows = rows["cards"] if isinstance(rows, dict) else rows
    return next(r for r in rows if r["id"] == card_id)


def test_sakura_seal_and_footnote_name_what_their_annotation_does():
    assert _row("proto_ym_sakura_seal")["description"] == (
        "[gold]Edit[/gold] up to 2 cards in your hand: [gold]Sakura Seal[/gold]"
        " (when played, plant a [gold]Sakura[/gold]).")
    assert _row("proto_ym_footnote")["description"] == (
        "[gold]Edit[/gold] up to 2 cards in your hand: [gold]Footnote[/gold]"
        " (when played, draw 1 card).")
