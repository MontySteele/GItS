"""SEAT PAGE BACKLOG CLEANUP (2026-10-18): the page, bridge and tool lines of
`docs/current/BACKLOG.md` built in one pass. One test group per line.

- Body Slam's "(Deals N damage)" does not fold the enemy's Vulnerable, so the
  fold note names only the mod's faces.
- `ModeLabels` read the card's vars on the upgraded side; the bridge matches a
  mode named without markup.
- A Set off card's own hit on a target its Bombs killed (Kaboom!, Pocket
  Match) is printed on its play line, and so is what the Set off detonated,
  a payload it sent out and where a charge jumped (C# twins in
  `ResolutionLedgerTests`).
- Incoming names an attacker whose Mines go off before its hit.
- The plays of a fight's last turn print on the reward screen.
- Flutter's cut does not reach Bombs, and says so.
- Two folded models that cancel say they cancel (Louse Progenitor).
- Ultimate Strike and Ultimate Defend get a Smith preview.
- An Ancient's lines print (`gits/GitsAncientDialogue.cs`).
- Co-op: a hit on a player is named by character; the partner's own HP cost is
  theirs; the partner's element counts for the reaction glossary; a refused
  `proceed` says it waits on the partner; a downed seat is told it comes back
  at 1 HP.
- A dead Decimillipede segment waiting to Reattach is listed
  (`gits/GitsRevivingEnemies.cs`).
- The enemies act in the order listed.
- A Companion summon's end-of-turn hits print off Kokomi's page.
- Tender's number is the cards played this turn; Spiny Toad's loop is briefed.
- A Sting a carry-out sends to the discard pile sits under that Plan.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest

from understudy import (blindplay, blindplay_board, blindplay_coop,
                        blindplay_enemies, blindplay_faces, blindplay_render,
                        blindplay_session, qa_packet)

from tier0.tests.test_understudy_blindplay import (combat_state, event_state,
                                                   rewards_state)

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh():
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


# ---- Body Slam's fold note --------------------------------------------------

VULN = [{"name": "A", "hp": 10, "powers": [
    {"name": "Vulnerable", "stacks": 2}]}]


def test_a_base_deals_face_is_not_named_as_folding_the_enemys_vulnerable():
    body_slam = {"kind": "Attack", "title": "Body Slam", "mod_card": False,
                 "text": "Deal damage equal to your Block.\n(Deals 9 damage)"}
    assert blindplay_render._enemy_fold_note(VULN, [body_slam]) == [
        "", blindplay_render.ENEMY_FOLD_NOTE]


def test_a_mod_deals_face_still_is():
    riptide = {"kind": "Attack", "title": "Riptide", "mod_card": True,
               "text": "Deal damage equal to your Block.\n(Deals 15 damage)"}
    assert blindplay_render._enemy_fold_note(VULN, [riptide]) == [
        "", blindplay_render.ENEMY_FOLD_NOTE_ONLY.format(cards="**Riptide**")]


def test_the_face_says_whose_card_it_is_off_the_id():
    assert blindplay_faces._card_face(
        {"id": "BODY_SLAM", "name": "Body Slam"})["mod_card"] is False
    assert blindplay_faces._card_face(
        {"id": "KLEEMOD-PROTO_KK_RIPTIDE", "name": "Riptide"})["mod_card"]


# ---- ModeLabels off the vars --------------------------------------------------

GENERATED = ROOT / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"


def test_an_upgraded_modal_lists_its_upgraded_numbers_to_the_bridge():
    src = (GENERATED / "ProtoFsCurtainRise.cs").read_text(encoding="utf-8")
    labels = re.search(r"ModeLabels =>\s*(.*?);", src, re.S).group(1)
    assert '"Deal 10 damage"' in labels and "deal 16 instead" in labels
    # The base side is the sheet's label, byte for byte.
    assert '"Deal 7 damage", "[gold]Drain[/gold] 3: deal 12 instead"' in labels


def test_the_label_keeps_its_wording_and_moves_only_its_numbers():
    from tools import gen_klee_cards as gen
    vars_cs = 'new FoldedDamageVar("PlainDamage", 7m, ValueProp.Move)'
    up = 'DynamicVars["PlainDamage"].UpgradeValueBy(3m);'
    face = "Deal {PlainDamage:diff()} damage"
    assert gen.mode_label_from_face("Deal 7 damage", face, vars_cs, up,
                                    False) == "Deal 7 damage"
    assert gen.mode_label_from_face("Deal 7 damage", face, vars_cs, up,
                                    True) == "Deal 10 damage"
    # A face that does not read as the label keeps the label.
    assert gen.mode_label_from_face("Hit hard", face, vars_cs, up,
                                    True) == "Hit hard"


def test_the_bridge_folds_markup_before_matching_a_mode():
    src = (ROOT / "vendor" / "STS2_MCP" / "gits"
           / "GitsModalTargeting.cs").read_text(encoding="utf-8")
    assert "string want = Fold(wanted);" in src
    assert "public static string Fold(string? text)" in src


# ---- a Set off card's own hit on a dead target ------------------------------

def _row(card: str, **extra) -> dict:
    row = {"card_id": card.lower(), "card": card, "auto_played": False,
           "carried": False, "overflowed": False, "hits": []}
    row.update(extra)
    return row


def _with_rows(*rows: dict, state: dict | None = None) -> dict:
    state = copy.deepcopy(state or combat_state())
    state["player"]["resolutions"] = list(rows)
    return state


def test_kabooms_own_damage_says_its_bombs_killed_the_target_first():
    row = _row("Kaboom!", hits=[{"target": "Corpse Slug", "amount": 0,
                                 "blocked": 0, "combat_id": "1",
                                 "killed": True}],
               events=[{"kind": "no_target", "card": "Kaboom!",
                        "target": "Corpse Slug", "power": "",
                        "combat_id": "1", "seq": 5, "amount": 4}])
    page = blindplay.observe(_with_rows(row))
    assert blindplay_render.RESOLUTION_NO_TARGET.format(
        n=4, target="Corpse Slug") in page
    # Not repeated under "since last page".
    assert page.count("Its own 4 damage") == 1


# ---- the plays of the fight's last turn -------------------------------------

def test_a_fight_ending_play_prints_on_the_reward_screen():
    state = rewards_state()
    state["player"] = {"resolutions": [_row("Rapid Fire", hits=[
        {"target": "Toadpole", "amount": 6, "blocked": 0, "combat_id": "1"},
        {"target": "Toadpole", "amount": 0, "blocked": 0, "combat_id": "1",
         "killed": True}])]}
    page = blindplay.observe(state)
    assert blindplay_render.LAST_PLAYS_HEADING in page
    assert "- **Rapid Fire**" in page
    assert "Toadpole" in page


def test_no_last_plays_when_the_ledger_is_empty_or_absent():
    assert blindplay_board.last_plays(rewards_state()) is None
    state = rewards_state()
    state["player"] = {"resolutions": [
        _row("Strike", carried=True)]}
    assert blindplay_board.last_plays(state) is None


# ---- Flutter and Bombs --------------------------------------------------------

FLUTTER = {"name": "Flutter", "stacks": 3, "kind": "buff",
           "text": "Receives 50% less damage from Attacks."}


def test_flutter_says_it_does_not_cut_bombs_where_bombs_are_in_play():
    c = {"enemies": [{"powers": [{"name": "Bomb", "stacks": 6}]}], "hand": []}
    assert blindplay_render._not_bombs_clause(FLUTTER, c) == \
        blindplay_render.NOT_BOMBS_CLAUSE
    c = {"enemies": [], "hand": [{"text": "Place a Bomb 8."}]}
    assert blindplay_render._not_bombs_clause(FLUTTER, c)
    assert blindplay_render._not_bombs_clause(
        FLUTTER, {"enemies": [], "hand": [{"text": "Deal 6 damage."}]}) == ""
    qa_packet.assert_blind(blindplay_render.NOT_BOMBS_CLAUSE)


# ---- two folded models that cancel ------------------------------------------

def test_strength_and_weak_that_cancel_say_so():
    got = blindplay_render._breakdown_clauses({
        "base": 14, "folded": 14, "repeats": 1, "total": 14,
        "modifiers": ["Strength", "Weak"]})
    assert got == [blindplay_render.INTENT_FOLD_CANCELS.format(
        base=14, folded=14, modifiers="**Strength** and **Weak**")]
    assert "cancel out" in got[0]
    one = blindplay_render._breakdown_clauses({
        "base": 14, "folded": 18, "repeats": 1, "total": 18,
        "modifiers": ["Strength"]})
    assert "cancel" not in one[0]


# ---- Ultimate Strike at the Smith ------------------------------------------

def test_ultimate_strike_and_defend_preview_their_upgrade():
    assert qa_packet.upgrade_preview(
        "ULTIMATE_STRIKE", "Deal 14 damage.", title="Ultimate Strike") == (
        "Deal 20 damage.", "")
    assert qa_packet.upgrade_preview(
        "ULTIMATE_DEFEND", "Gain 11 Block.", title="Ultimate Defend") == (
        "Gain 15 Block.", "")


# ---- an Ancient's lines ---------------------------------------------------

def test_an_ancients_lines_print_under_its_speaker():
    state = event_state()
    state["event"].update({"event_name": "Neow", "in_dialogue": True,
                           "is_ancient": True, "options": [],
                           "dialogue": [
                               {"speaker": "ancient",
                                "text": "Ah, a new\nchallenger."},
                               {"speaker": "you", "text": "Hello."}]})
    page = blindplay.observe(state)
    assert "> **Neow:** Ah, a new challenger." in page
    assert "> **You:** Hello." in page
    assert page.index("Ah, a new") < page.index("still being told")


def test_the_bridge_sends_the_lines_and_the_reader_exists():
    builder = (ROOT / "vendor" / "STS2_MCP"
               / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert "GitsAncientDialogue.Lines(ancientLayout)" in builder
    reader = (ROOT / "vendor" / "STS2_MCP" / "gits"
              / "GitsAncientDialogue.cs").read_text(encoding="utf-8")
    for name in ("_dialogueContainer", "_currentDialogueLine", "_line",
                 "%Text"):
        assert f'"{name}"' in reader


# ---- co-op ----------------------------------------------------------------

KLEE = {"character": "Klee", "is_local": True, "hp": 62, "max_hp": 62,
        "gold": 99, "is_alive": True, "entity_id": "11"}
FURINA = {"character": "Furina", "is_local": False, "hp": 78, "max_hp": 78,
          "gold": 99, "is_alive": True, "entity_id": "12"}


def _coop(state: dict) -> dict:
    s = copy.deepcopy(state)
    s.update({"game_mode": "multiplayer", "net_type": "Host",
              "player_count": 2, "local_player_slot": 0,
              "players": [dict(KLEE, block=0), dict(FURINA, block=0)]})
    return s


def test_a_partners_own_hp_cost_is_theirs_and_named_by_character():
    theirs = _row("Ousia Pledge", is_local=False, hits=[
        {"target": "Test Client 1", "amount": 3, "blocked": 0,
         "combat_id": "12", "on_player": True, "self": True}])
    page = blindplay.observe(_coop(_with_rows(theirs)))
    assert "**Furina** (the other player) -- 3" in page
    assert "their own HP cost" in page
    assert "Test Client 1" not in page
    assert "your own HP cost" not in page


def test_your_own_hit_is_named_by_your_character():
    mine = _row("Drain", hits=[
        {"target": "Test Host", "amount": 2, "blocked": 0,
         "combat_id": "11", "on_player": True, "self": True}])
    page = blindplay.observe(_coop(_with_rows(mine)))
    assert "**Klee** (you) -- 2" in page
    assert "Test Host" not in page


def test_the_partners_element_counts_for_the_glossary():
    rows = blindplay_coop._partner_rows(_coop(combat_state()))
    assert rows[0]["element"] == "Hydro"


def test_a_refused_proceed_in_coop_says_it_waits_on_the_partner():
    refusal = {"status": "error",
               "error": "No proceed button available or enabled"}
    lines = blindplay_session.answer_lines({}, _coop(rewards_state()), refusal)
    assert lines[-1] == blindplay_session.COOP_PROCEED_WAITS
    solo = blindplay_session.answer_lines({}, rewards_state(), refusal)
    assert blindplay_session.COOP_PROCEED_WAITS not in solo


def test_a_downed_seat_is_told_it_comes_back_at_one_hp():
    s = _coop(combat_state())
    s["players"][0]["is_alive"] = False
    info = blindplay_coop.coop_block(s)
    assert "you get back up with 1 HP" in info["waiting"]


# ---- a dead segment coming back -------------------------------------------

def test_a_segment_waiting_to_reattach_is_listed():
    state = combat_state()
    state["battle"]["reviving"] = [
        {"combat_id": 4, "name": "Decimillipede", "max_hp": 48,
         "move_id": "DEAD_MOVE", "revive_hp": 25}]
    page = blindplay.observe(state)
    assert blindplay_render.REVIVING_TWO_TURNS.format(
        name="Decimillipede", hp=" with 25 HP") in page
    assert blindplay_render._reviving_lines([
        {"name": "D", "move_id": "REATTACH_MOVE", "revive_hp": 25}]) == [
        blindplay_render.REVIVING_NEXT_TURN.format(name="D",
                                                   hp=" with 25 HP")]
    for line in (blindplay_render.REVIVING_TWO_TURNS,
                 blindplay_render.REVIVING_NEXT_TURN):
        qa_packet.assert_blind(line.format(name="D", hp=""))


def test_the_bridge_sends_the_dead_enemies_under_their_own_key():
    builder = (ROOT / "vendor" / "STS2_MCP"
               / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert "GitsRevivingEnemies.Build(combatState.Enemies)" in builder


# ---- the order enemies act in -------------------------------------------

def test_two_enemies_say_they_act_in_the_order_listed():
    state = combat_state()
    second = copy.deepcopy(state["battle"]["enemies"][0])
    second.update({"entity_id": "NIBBIT_1", "combat_id": 2})
    state["battle"]["enemies"].append(second)
    assert blindplay_render.ENEMY_ORDER_NOTE in blindplay.observe(state)
    assert blindplay_render.ENEMY_ORDER_NOTE not in blindplay.observe(
        combat_state())


# ---- a summon's hits off Kokomi's page ------------------------------------

def test_ozs_end_of_turn_hit_prints_on_a_klee_page():
    state = combat_state()
    state["player"]["kokomi_plans"] = {"summon_hits": [
        {"card": "Oz, at Your Side", "number": 5,
         "line": "Oz, at Your Side, 5",
         "moved": [{"target": "Nibbit", "combat_id": "1", "amount": 5,
                    "dead": False}]}]}
    assert blindplay_board.kokomi_plans(state["player"]) is None
    page = blindplay.observe(state)
    assert blindplay_render.SUMMON_HITS_HEADING in page
    assert "Oz, at Your Side, 5" in page
    assert "## The Bake-Kurage" not in page


# ---- Tender and Spiny Toad ------------------------------------------------

def test_tenders_number_is_the_cards_played_this_turn():
    power = {"name": "Tender", "stacks": 3, "kind": "debuff",
             "text": "Whenever you play a card, lose 3 Strength and 3 "
                     "Dexterity this turn."}
    assert blindplay_render.TENDER_CLAUSE in blindplay_render._render_power(
        power, "- ")
    bare = {"name": "Tender", "stacks": 3, "kind": "debuff", "text": ""}
    assert blindplay_render.TENDER_CLAUSE in blindplay_render._render_power(
        bare, "- ")
    qa_packet.assert_blind(blindplay_render.TENDER_CLAUSE)


def test_spiny_toads_loop_is_briefed():
    assert "Thorns" in blindplay_enemies.enemy_brief("SPINY_TOAD_0")


# ---- a carry-out's full-hand discard ---------------------------------------

def test_a_sting_the_plan_could_not_hand_you_sits_under_that_plan():
    plans = {"pet": True, "pet_name": "Bake-Kurage", "pet_entity_id": "41",
             "pending": 0, "twice": False, "queue": [],
             "carried_out": [{"card": "Jellyfish Drift", "number": None,
                              "line": "Bake-Kurage: Jellyfish Drift",
                              "discarded": ["Sting", "Sting"]}]}
    state = combat_state()
    state["player"]["kokomi_plans"] = plans
    page = blindplay.observe(state)
    line = "    - " + blindplay_render.EVENT_TO_DISCARD.format(
        n=2, card="Stings")
    assert line in page
    assert page.index("Bake-Kurage: Jellyfish Drift") < page.index(line)


# ---- what a Set off detonated ---------------------------------------------

def test_a_set_off_lists_its_charges_and_says_nothing_jumped():
    row = _row("Sizzle", hits=[
        {"target": "Corpse Slug", "amount": 3, "blocked": 0,
         "combat_id": "1"},
        {"target": "Corpse Slug", "amount": 0, "blocked": 0,
         "combat_id": "1", "killed": True}],
        events=[
            {"kind": "detonated", "card": "Sizzle", "target": "Corpse Slug",
             "power": "Mine 3", "combat_id": "1", "seq": 1, "amount": 3},
            {"kind": "detonated_killed", "card": "Sizzle",
             "target": "Corpse Slug", "power": "Bomb 16", "combat_id": "1",
             "seq": 2, "amount": 2}])
    page = blindplay.observe(_with_rows(row))
    assert ("  Set off on **Corpse Slug**: Mine 3 (3), Bomb 16 (2, killed "
            "it).") in page
    assert blindplay_render.RESOLUTION_NOTHING_JUMPED in page


def test_a_jump_and_a_payload_are_named():
    row = {"detonations": [{"charge": "Bomb 11", "target": "Louse",
                            "amount": 11, "killed": True}],
           "jumps": [{"charge": "Bomb 4", "target": "Slime"}],
           "payloads": [{"charge": "Bomb 11", "placed": "Mine 3",
                         "count": 2}]}
    lines = blindplay_render._detonation_lines(row)
    assert "  Jumped: Bomb 4 to **Slime**." in lines
    assert blindplay_render.RESOLUTION_NOTHING_JUMPED not in lines
    assert ("  Bomb 11's payload put Mine 3 on 2 enemies: the \"Put Mine 3\" "
            "lines above.") in lines
    for line in lines:
        qa_packet.assert_blind(line)


# ---- Mines go off before the hit ------------------------------------------

def test_incoming_names_the_attacker_whose_mines_go_off_first():
    enemies = [{"name": "Nibbit", "hp": 20, "intents": [
        {"type": "Attack", "label": "8", "title": "Butt"}],
        "powers": [{"name": "Mine", "stacks": 3, "text": ""}]}]
    you = {"hp": 60, "max_hp": 80, "block": 0, "powers": [], "relics": [],
           "orbs": None}
    line = blindplay_render._incoming_line(enemies, you)
    assert blindplay_render.INCOMING_MINES_FIRST.format(
        names="**Nibbit**") in line
    enemies[0]["powers"] = []
    assert "Mines on" not in blindplay_render._incoming_line(enemies, you)
