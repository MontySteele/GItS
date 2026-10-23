"""Yae review r6, items 1 to 7 (review/active/yae-review-r6-2026-10-15.md).
Sim and page half; the C# half is
`klee-mod/KleeTests/Prototype/YaeReviewR6Tests.cs`.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy
from understudy import (blindplay, blindplay_notes, blindplay_render,
                        blindplay_shape)

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


def _ym(name):
    return loader.get_card("proto_ym_" + name)


def _row(card_id):
    import yaml
    rows = yaml.safe_load((REPO / "docs" / "prototype-surface.yaml")
                          .read_text(encoding="utf-8"))
    rows = rows["cards"] if isinstance(rows, dict) else rows
    return next(r for r in rows if r["id"] == card_id)


# 1. Serialization: whenever you Edit a card, gain 3 [4] Block ---------------

def test_serialization_row_is_per_edit():
    row = _row("proto_ym_serialization")
    assert row["description"] == (
        "Whenever you [gold]Edit[/gold] a card, gain 3 [gold]Block[/gold].")
    assert row["upgrade"] == {"power_amount": 1}


def test_serialization_pays_per_card_edited():
    st = _state()
    _play(st, _ym("serialization"))
    st.player.hand += [loader.get_card("strike"), loader.get_card("defend")]
    st.player.block = 0
    _play(st, _ym("footnote"))                   # Edits 2 cards
    assert st.player.block == 2 * 3


def test_upgraded_serialization_pays_four():
    st = _state()
    _play(st, _ym("serialization+"))
    st.player.hand.append(loader.get_card("strike"))
    st.player.block = 0
    _play(st, _ym("margin_note"))                # Edits 1 card
    assert st.player.block == 4


def test_each_sakura_an_edit_annotates_pays():
    st = _state()
    _play(st, _ym("serialization"))
    for _ in range(3):
        Y.plant(st, 1)
    st.player.block = 0
    _play(st, _ym("inked_branches"))             # every Sakura
    assert Y.ledger(st.player).edits == 3
    assert st.player.block == 3 * 3


def test_a_publish_and_an_annotated_play_pay_nothing():
    st = _state()
    _play(st, _ym("serialization"))
    c = loader.get_card("strike")
    st.player.hand.append(c)
    Y.annotate(st, c, Y.FOOTNOTE)
    st.player.block = 0
    Y.publish_card(st, c)
    assert st.player.block == 0
    _play(st, c)
    assert st.player.block == 0


# 2. Manuscript Pile: draw 2 [3], then Edit a card in your hand: Red Ink -----

def test_manuscript_pile_row():
    row = _row("proto_ym_manuscript_pile")
    assert row["description"] == (
        "Draw {Cards:diff()} cards. [gold]Edit[/gold] a card in your [gold]Hand[/gold]: "
        "[gold]Red Ink[/gold].")
    assert row["effects"] == [
        {"op": "draw", "amount": 2},
        {"op": "yae", "kind": "edit", "annotation": "red_ink", "amount": 1}]
    assert row["upgrade"] == {"draw": 1}


def test_manuscript_pile_draws_first_then_edits_a_drawn_card():
    st = _state()
    st.player.hand = []
    st.player.draw_pile = [loader.get_card("strike"),
                           loader.get_card("defend")]
    _play(st, _ym("manuscript_pile"))
    assert len(st.player.hand) == 2              # the pile itself has left
    assert [Y.temp(c) for c in st.player.hand].count(Y.RED_INK) == 1
    assert Y.ledger(st.player).edits == 1


# 3. Meditations of a Yako with nothing to Publish -------------------------

def _rewards(flag):
    state = {"state_type": "rewards",
             "rewards": {"can_proceed": True, "items": [
                 {"index": 0, "type": "gold", "description": "30 Gold",
                  "gold_amount": 30}]},
             "player": {"character": "Yae Miko", "relics": [],
                        "potions": []}}
    if flag is not None:
        state["player"]["yae_shrine"] = flag
    return state


def test_the_reward_screen_says_why_no_publish_came():
    page = blindplay_render.observe(_rewards({"nothing_to_publish": True}))
    assert blindplay_notes.NOTHING_TO_PUBLISH_NOTE in page
    assert blindplay_notes.NOTHING_TO_PUBLISH_NOTE == (
        "*No Publish was offered: you made no Annotation that fight.*")
    for flag in (None, {}, {"nothing_to_publish": False}):
        assert "No Publish was offered" not in blindplay_render.observe(
            _rewards(flag))


def test_the_relic_flashes_and_says_nothing_to_publish():
    src = (REPO / "klee-mod" / "KleeCode" / "Relics"
           / "MeditationsOfAYako.cs").read_text(encoding="utf-8")
    assert "NothingToPublish = true;" in src
    assert "YaeEditing.NothingToPublishKey" in src
    ann = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "YaeAnnotations.cs").read_text(encoding="utf-8")
    assert 'NothingToPublishText = "Nothing to Publish."' in ann


# 4. Reprint stacks --------------------------------------------------------

REPRINT = ("The first time this card is played each combat, play it once "
           "more for each Reprint.")


def test_the_reprint_row_says_each_reprint_adds_a_play():
    assert blindplay_notes.ARM_KEYWORDS["Reprint"] == REPRINT
    ann = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "YaeAnnotations.cs").read_text(encoding="utf-8")
    assert ('"The first time this card is played each combat, play it once "\n'
            '          + "more for each Reprint."') in ann


# 5. Which enemy a Sakura strikes ------------------------------------------

TARGET = ("A Sakura strikes Kitsune Pounce's target when Pounce makes it "
          "strike, else the enemy Foxfire Lure marked this turn, else "
          "(with Hunting Gaze) the last enemy your Attacks hit, else a "
          "random enemy.")


def test_the_target_rule_is_one_sentence_on_the_page_and_the_hover():
    assert blindplay_notes.SAKURA_TARGET_RULE == TARGET
    assert blindplay_notes.ARM_KEYWORDS["Sakura"].endswith(" " + TARGET)
    assert blindplay_render.SHRINE_TARGET_LINE == "- " + TARGET
    tips = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
            / "ArmKeywordTips.cs").read_text(encoding="utf-8")
    assert ('"A Sakura strikes Kitsune Pounce\'s target when Pounce makes it '
            'strike, "\n      + "else the enemy Foxfire Lure marked this '
            'turn, else (with Hunting Gaze) "\n      + "the last enemy your '
            'Attacks hit, else a random enemy."') in tips


def _shrine(*rows):
    return {"sakura": [dict({"slot": i + 1, "level": 1, "planted": 1,
                             "turns": 3, "annotation": None}, **r)
                       for i, r in enumerate(rows)],
            "cap": 3, "lure": None, "annotated": 0, "edits": None}


def test_the_block_prints_the_rule_where_a_striking_sakura_stands():
    lines = blindplay_render._render_shrine(
        _shrine({"kind": "thunder", "strike": 3}))
    assert "- " + TARGET in lines
    lines = blindplay_render._render_shrine(
        _shrine({"kind": "kitsune", "strike": 3}))
    assert "- " + TARGET not in lines


# 6. The Incoming line counts the Kitsune Sakura's Block -------------------

def _you(block=0):
    return {"block": block, "hp": 40, "max_hp": 70, "powers": [],
            "relics": []}


def _attacker(n):
    return [{"name": "Hilichurl", "hp": 20, "max_hp": 20, "powers": [],
             "intents": [{"type": "Attack", "label": str(n),
                          "damage": n, "hits": 1}]}]


def test_kitsune_block_parts_read_the_rows():
    shrine = _shrine({"kind": "kitsune", "strike": 5, "turns": 2},
                     {"kind": "kitsune", "strike": 4, "turns": 1},
                     {"kind": "kitsune", "strike": 6, "turns": 1,
                      "annotation": "Deadline Extension"},
                     {"kind": "thunder", "strike": 9})
    # The 1-turn one acts, then acts once more as it withers.
    assert blindplay_render._kitsune_block_parts(shrine) == [
        ("Kitsune Sakura", 5), ("Kitsune Sakura", 8), ("Kitsune Sakura", 6)]
    assert blindplay_render._kitsune_block_parts(None) == []


def test_kitsune_block_parts_on_its_last_turn_is_its_act_and_its_bloom():
    # Yae round 8, lane 2: "adds 6 Block first" with one 3-Block Kitsune
    # standing is its end-of-turn act and its Last Bloom (1 turn left), not a
    # double count; Sacred Shade is not in it.
    shrine = _shrine({"kind": "kitsune", "strike": 3, "turns": 1})
    assert blindplay_render._kitsune_block_parts(shrine) == [
        ("Kitsune Sakura", 6)]
    # Yae draft pass, 2026-10-17: Eternity stops the timers, so no bloom.
    assert blindplay_render._kitsune_block_parts(shrine, eternal=True) == [
        ("Kitsune Sakura", 3)]


def test_the_incoming_line_reads_eternity_off_your_powers():
    shrine = _shrine({"kind": "kitsune", "strike": 3, "turns": 1})
    you = _you(2)
    plain = blindplay_render._incoming_line(_attacker(12), you, shrine=shrine)
    assert "adds 6 Block first" in plain
    you = dict(you, powers=[{"name": "Eternity", "stacks": 1}])
    held = blindplay_render._incoming_line(_attacker(12), you, shrine=shrine)
    assert "adds 3 Block first" in held


def test_kitsune_block_parts_see_deadline_extension_among_several():
    # The pool to 78, pick 2 (a): Deadline Extension need not be the first.
    shrine = _shrine({"kind": "kitsune", "strike": 6, "turns": 1,
                      "annotation": "Red Ink",
                      "annotations": ["Red Ink", "Deadline Extension"]})
    assert blindplay_render._kitsune_block_parts(shrine) == [
        ("Kitsune Sakura", 6)]


def test_the_incoming_line_folds_the_kitsune_block_in():
    shrine = _shrine({"kind": "kitsune", "strike": 5, "turns": 3})
    plain = blindplay_render._incoming_line(_attacker(12), _you(2))
    line = blindplay_render._incoming_line(_attacker(12), _you(2),
                                           shrine=shrine)
    assert "you would take 10" in plain, plain
    assert "you would take 5" in line, line
    assert "Kitsune Sakura adds 5 Block first" in line, line


# 7. A chooser's look keeps the fight it sits in ---------------------------

from tier0.tests.test_understudy_blindplay import (  # noqa: E402
    card_select_state, combat_state, rewards_state)


@pytest.fixture
def lane(monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", None)
    monkeypatch.setenv("GITS_LANE", "2")
    monkeypatch.delenv(blindplay_shape.MAX_ACTIONS_ENV, raising=False)
    monkeypatch.setattr(blindplay_shape, "lane_embark_stamp",
                        lambda lane=None: "")
    monkeypatch.setattr(blindplay, "_lane_guard", lambda args: "")
    monkeypatch.setattr(blindplay, "_warn_build_skew", lambda state: None)
    screen = {"now": combat_state()}
    monkeypatch.setattr(blindplay, "_live_load",
                        lambda args, **kw: screen["now"])
    posted: list = []
    monkeypatch.setattr(blindplay, "post_when_the_room_is_open",
                        lambda *a, **kw: posted.append(a) or {})
    blindplay.forget_run()
    yield screen, posted
    blindplay.forget_run()


def _act(command):
    return argparse.Namespace(raw_file="", dry_run=False, brief=True,
                              command=command)


def _observe():
    return argparse.Namespace(raw_file="", brief=True, define="")


def test_an_overlay_look_keeps_the_last_looks_room(lane):
    blindplay_shape.remember_look("fight", ["nibbit"])
    blindplay_shape.remember_look("", [], screen="hand_select")
    look = blindplay_shape.read_look()
    assert look["room"] == "fight" and look["screen"] == "hand_select"


def test_a_pick_that_ended_the_fight_skips_the_chained_play(lane, capsys):
    screen, posted = lane
    assert blindplay.cmd_observe(_observe()) == 0
    # A turn-start chooser (Stratagem), looked at with the boss alive.
    chooser = card_select_state()
    chooser["card_select"]["prompt"] = "Choose a card to add into your Hand."
    screen["now"] = chooser
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    # The pick let the turn start finish and the fight ended.
    screen["now"] = rewards_state()
    assert blindplay.cmd_act(_act('play "Pearl Barrage"')) == 1
    out = capsys.readouterr().out
    assert out.startswith("Skipped: the fight ended since your last look"), out
    assert "REFUSED" not in out
    assert blindplay_shape.refusal_streak() == 0
    assert posted == []
