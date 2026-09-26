"""THE WAVE-3 SEAT ROUND'S FIXES (2026-09-26): the sheet, the seat page and
the seat brief.

Records (gitignored): `review/qa/seats-2026-09-26/wave3-*.md`. The mod's pins
are `klee-mod/KleeTests/Prototype/Wave3Fixes20260926Tests.cs`.
"""

from __future__ import annotations

import copy
import os
import subprocess
import sys
from pathlib import Path

import yaml

from understudy import blindplay, qa_packet
from understudy.blindplay_board import furina_stage
from understudy.blindplay_faces import _card_face
from understudy.blindplay_grammar import _play, parse_command
from understudy.blindplay_notes import (ARM_KEYWORDS, CHOOSER_CONFIRM_NOTE,
                                        CHOOSER_MAYBE_CLOSES_NOTE,
                                        CLOSES_NOTE_HEAD, chooser_note,
                                        keyword_notes)
from understudy.blindplay_render import (BOARD_BEHIND_HEADING,
                                         _render_stage_log)

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tier0" / "tests"))

from test_understudy_blindplay import combat_state  # noqa: E402

FIVE_CENTURY = ("Whenever a performer [gold]Bow[/gold]s and leaves, it "
                "returns at the back with 1 [gold]Fanfare[/gold] if a seat is "
                "free.")


# ---- 1. A Five-Century Act's face --------------------------------------------

def test_a_five_century_act_says_it_needs_a_free_seat():
    rows = yaml.safe_load(
        (REPO / "docs" / "prototype-surface.yaml").read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else next(
        v for v in rows.values() if isinstance(v, list))
    row = next(r for r in rows if r.get("id") == "proto_fs_five_century_act")
    assert row["description"] == FIVE_CENTURY
    power = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
             / "FurinaStagePowers.cs").read_text(encoding="utf-8")
    assert '"Whenever a performer [gold]Bow[/gold]s and leaves, it returns "' \
        in power
    brief = (REPO / "review" / "active"
             / "furina-stage-brief-2026-09-08.md").read_text(encoding="utf-8")
    assert ("Whenever a performer Bows and leaves, it returns at the back "
            "with 1 Fanfare if a seat is free.") in brief
    assert "2026-09-26 seat round" in brief


# ---- 2. BaseLib's mod-source tip ---------------------------------------------

WHATMOD = {"name": "WhatMod", "description": "KleeMod"}


def test_the_mod_source_tip_never_reaches_a_face():
    face = _card_face({"name": "Pop!", "description": "Place a Bomb.",
                       "keywords": [WHATMOD,
                                    {"name": "Bomb", "description": "x"}]})
    assert [k["name"] for k in face["keywords"]] == ["Bomb"]


def test_the_orobas_option_prints_no_mod_name():
    from understudy.blindplay_board import _option_faces
    faces = _option_faces({"title": "Touch of Orobas",
                           "relic_name": "Touch of Orobas",
                           "relic_description": "Upgrade your starter relic.",
                           "keywords": [WHATMOD]})
    assert all(f["name"] != "WhatMod" for f in faces)
    assert "KleeMod" not in str(faces)


# ---- 4. Why an act could not pay ---------------------------------------------

def _unpaid(member, name, reason, price):
    return {"event": "unpaid", "member": member, "name": name, "seat": 0,
            "fanfare": 1, "moved": price, "reason": reason, "target": "",
            "target_id": "", "each": -1, "hp": -1, "struck": -1, "by": "",
            "by_member": ""}


def test_an_unpaid_act_says_why():
    stage = furina_stage({"furina_stage": {"live": True, "seats": [], "log": [
        _unpaid("chevreuse", "Chevreuse", "back", 2),
        _unpaid("neuvillette", "Neuvillette", "own", 3),
        _unpaid("clorinde", "Clorinde", "alone", 0),
        _unpaid("chevreuse", "Chevreuse", "", 0)]}})
    assert _render_stage_log(stage) == [
        "  - **Chevreuse** could not pay: the back performer has less than 2 "
        "Fanfare.",
        "  - **Neuvillette** could not pay: he has less than 3 Fanfare.",
        "  - **Clorinde** could not pay: no other performer is on stage to "
        "take Fanfare from.",
        # An older build sends no reason: the line it always printed.
        "  - **Chevreuse** could not pay.",
    ]
    assert qa_packet.leaks(stage) == []


# ---- 5. Upgrade previews -----------------------------------------------------

def test_an_in_combat_clause_does_not_hide_the_upgrade():
    """Bravura printed "not shown -- the face on this screen is not the
    sentence this card was written with": its template ends in an
    `{InCombat:...|}` arm with a hole of its own."""
    face = ("Spend all of your back performer's Fanfare. Deal 3 damage per "
            "point.")
    assert qa_packet.upgrade_preview("KLEEMOD-PROTO_FS_BRAVURA", face) == (
        "Spend all of your back performer's Fanfare. Deal 4 damage per "
        "point.", "")
    # Printed in combat, the in-combat line is struck, not copied through.
    assert qa_packet.upgrade_preview(
        "KLEEMOD-PROTO_FS_BRAVURA", face + "\n(Deals 9 damage)")[0] == (
        "Spend all of your back performer's Fanfare. Deal 4 damage per "
        "point.")
    assert qa_packet.upgrade_preview(
        "KLEEMOD-PROTO_FS_DA_CAPO",
        "Deal 6 damage, plus 2 for each Bow this combat.") == (
        "Deal 9 damage, plus 3 for each Bow this combat.", "")


def test_a_numbered_defend_still_previews():
    """Two Defends on a Smith print as `Defend (1)` and `Defend (2)`, and the
    base-game table is keyed on the name."""
    assert qa_packet.upgrade_preview("DEFEND_IRONCLAD", "Gain 5 Block.",
                                     title="Defend (2)") == ("Gain 8 Block.",
                                                             "")


def test_the_smith_passes_the_games_own_title():
    card = {"id": "DEFEND_IRONCLAD", "name": "Defend",
            "description": "Gain 5 Block.", "type": "Skill", "cost": "1"}
    state = {"state_type": "card_select",
             "player": {"character": "klee", "potions": [], "relics": [],
                        "max_potion_slots": 3},
             "card_select": {"screen_type": "upgrade", "prompt": "Upgrade",
                             "can_confirm": False, "preview_showing": False,
                             "selection_known": True,
                             "cards": [dict(card, index=0),
                                       dict(card, index=1)]}}
    page = blindplay.observe(state)
    assert page.count("Upgraded: Gain 8 Block.") == 2
    assert "no written face" not in page


# ---- 6. Pickers that close on their last pick --------------------------------

def _simple(closes, picks=1):
    blob = {"screen_type": "simple_select", "prompt": "Choose a card.",
            "can_skip": False, "can_cancel": False, "preview_showing": False,
            "can_confirm": False, "selection_known": True,
            "cards": [{"index": 0, "name": "Strike", "id": "STRIKE_IRONCLAD",
                       "description": "Deal 6 damage.", "type": "Attack",
                       "cost": "1"},
                      {"index": 1, "name": "Bash", "id": "BASH",
                       "description": "Deal 8 damage.", "type": "Attack",
                       "cost": "2"}]}
    if closes is not None:
        blob["closes_on_last_pick"] = closes
        blob["picks_needed"] = picks
    return {"state_type": "card_select",
            "player": {"character": "klee", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "card_select": blob}


def test_a_picker_that_closes_on_its_last_pick_never_says_confirm():
    page = blindplay.observe(_simple(True, 2))
    assert CLOSES_NOTE_HEAD in page
    assert "once you have picked 2 cards" in page
    assert CHOOSER_CONFIRM_NOTE not in page
    assert "Confirm is not available" not in page


def test_the_note_is_chosen_by_what_the_bridge_says():
    assert chooser_note("simple_select", False) == CHOOSER_CONFIRM_NOTE
    assert chooser_note("simple_select", None) == CHOOSER_MAYBE_CLOSES_NOTE
    assert chooser_note("simple_select", True, 1).startswith(CLOSES_NOTE_HEAD)
    assert "picked 1 card:" in chooser_note("simple_select", True, 1)
    # The grids that open a preview keep the two-command sentence.
    assert chooser_note("upgrade") == CHOOSER_CONFIRM_NOTE
    assert CHOOSER_MAYBE_CLOSES_NOTE in blindplay.observe(_simple(None))


def test_the_bridge_reads_the_screens_own_prefs():
    src = (REPO / "vendor" / "STS2_MCP" / "gits"
           / "GitsSelectPrefs.cs").read_text(encoding="utf-8")
    assert "RequireManualConfirmation" in src and "MaxSelect" in src
    assert '"NSimpleCardSelectScreen"' in src


# ---- 7. A reaction names the body by the page's own name ---------------------

def test_a_reaction_row_uses_the_enemy_lists_name():
    state = copy.deepcopy(combat_state())
    enemies = state["battle"]["enemies"]
    twin = copy.deepcopy(enemies[0])
    twin["combat_id"] = 2
    twin["entity_id"] = "nibbit_1"
    enemies.append(twin)
    state["player"]["reactions"] = [
        {"reaction": "Melt", "source": "Kaeya", "target": "Nibbit",
         "combat_id": "2"}]
    obs = blindplay.observation(state)
    names = [e["name"] for e in obs["combat"]["enemies"]]
    assert len(set(names)) == 2
    assert obs["combat"]["reactions"][0]["target"] == names[1]


# ---- 8. A word inside an item's name is not the keyword ----------------------

def _shop(name, text):
    return {"state_type": "shop",
            "player": {"character": "klee", "gold": 200, "potions": [],
                       "relics": [], "max_potion_slots": 3},
            "shop": {"items": [{"index": 0, "category": "relic",
                                "price": 150, "is_stocked": True,
                                "can_afford": True, "relic_name": name,
                                "relic_description": text}]}}


def test_a_relic_named_ringing_does_not_define_ringing():
    obs = blindplay.observation(_shop("Ringing Triangle",
                                      "At the start of each combat, gain 1 "
                                      "Energy."))
    assert "Ringing" not in [r["name"] for r in keyword_notes(obs)]


def test_a_rule_that_prints_ringing_still_defines_it():
    obs = blindplay.observation(_shop("Odd Bell",
                                      "Your first card each turn gives "
                                      "Ringing."))
    assert "Ringing" in [r["name"] for r in keyword_notes(obs)]


# ---- 9. A pick that went to the discard pile ---------------------------------

def test_a_card_a_full_hand_sent_to_the_discard_pile_is_found():
    state = copy.deepcopy(combat_state())
    hand = state["player"]["hand"]
    while len(hand) < 10:
        extra = copy.deepcopy(hand[0])
        extra["index"] = len(hand)
        hand.append(extra)
    state["player"]["discard_pile"] = [
        {"name": "Fish Fry", "id": "FISH_FRY", "description": "x"}]
    res = _play(state, parse_command('play "Fish Fry"'))
    assert not res.ok
    assert "Fish Fry is in your discard pile" in res.refusal
    assert "hand of 10 cards" in res.refusal


# ---- 10. The seat brief ------------------------------------------------------

def test_the_brief_tells_seats_to_keep_to_their_lane():
    out = subprocess.run(
        [sys.executable, str(REPO / "tools" / "seat.py"), "--opus-brief",
         "--lane", "3", "--character", "KLEEMOD-FURINA"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO),
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert out.returncode == 0
    assert "share one scratchpad" in out.stdout
    assert "a folder named for your lane" in out.stdout
    assert "`GITS_LANE=3` on every" in out.stdout
    # After the Bash-scratch paragraph, inside "What blindness means here".
    text = out.stdout
    assert (text.index("What blindness means here")
            < text.index("You may use the Bash tool for your own scratch")
            < text.index("share one scratchpad")
            < text.index("If you hit a screen the tool refuses"))


# ---- 11. The fight behind a mid-fight chooser --------------------------------

def test_a_chooser_over_a_fight_prints_the_fight():
    state = copy.deepcopy(combat_state())
    state["state_type"] = "card_select"
    state["card_select"] = {
        "screen_type": "choose", "prompt": "Choose a card.",
        "can_skip": False, "can_cancel": False, "preview_showing": False,
        "can_confirm": False,
        "cards": [{"index": 0, "name": "Ousia", "id": "X_OUSIA",
                   "description": "Acts deal double damage.",
                   "type": "Skill", "cost": "0"},
                  {"index": 1, "name": "Pneuma", "id": "X_PNEUMA",
                   "description": "Acts give double Block.",
                   "type": "Skill", "cost": "0"}]}
    page = blindplay.observe(state)
    assert BOARD_BEHIND_HEADING in page
    behind = page.split(BOARD_BEHIND_HEADING)[1]
    assert "Nibbit" in behind and "Intent:" in behind
    assert "- Your hand: " in behind
    # And a chooser with no fight under it prints none.
    del state["battle"]
    assert BOARD_BEHIND_HEADING not in blindplay.observe(state)


# ---- 12 and 13. Pneuma, and three log labels ---------------------------------

def test_pneuma_says_it_summons_nobody():
    assert ARM_KEYWORDS["Pneuma"].endswith("It summons nobody.")


def _row(event, member, name, bar, moved, **kw):
    row = {"event": event, "member": member, "name": name, "seat": 0,
           "fanfare": bar, "moved": moved, "reason": "", "target": "",
           "target_id": "", "each": -1, "hp": -1, "struck": -1, "by": "",
           "by_member": "", "source": ""}
    row.update(kw)
    return row


def test_the_log_names_pneuma_a_card_in_hand_and_rejoice():
    stage = furina_stage({"furina_stage": {"live": True, "seats": [], "log": [
        _row("regain", "usher", "Gentilhomme Usher", 5, 2, source="Pneuma"),
        _row("regain", "usher", "Gentilhomme Usher", 6, 1),
        _row("hit", "usher", "Gentilhomme Usher", 3, 2, source="Burn"),
        _row("leave", "usher", "Gentilhomme Usher", 0, 3,
             reason="rejoice")]}})
    lines = _render_stage_log(stage)
    assert lines[0] == "  - **Usher** gains 2 Fanfare from Pneuma: 3 → 5."
    assert lines[1] == ("  - **Usher** regained 1 Fanfare as the front "
                        "performer: 5 → 6.")
    assert lines[2].startswith("  - **Usher** took 2 damage from Burn: 5 → 3")
    assert "emptied by Let the People Rejoice, so it takes a Bow" in lines[3]
    assert "Spend" not in lines[3]
