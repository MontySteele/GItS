"""Seat page 3 (2026-10-05): eight fixes from a live seat round on 0.2.4437
(two Furina lanes, one Ironclad).

1. The enemy briefing prints on the first page of each fight, once per
   fight, whatever an earlier seat or page saw.
2. "Incoming this turn" prints on Furina's stage boards.
3. "Since last page" drops passive powers' noise, and names a Shatter and
   the curtain call's drained HP.
4. A Guest Star card prints its guest's Line and Act under the face.
5. Chevreuse's act logs as damage, not Energy.
6. A debuff telegraph names what the move does.
7. The Drain line says where it comes from.

The owner's terms: page facts, never a computed best play.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from understudy import (blindplay, blindplay_board, blindplay_brief,
                        blindplay_faces,
                        blindplay_moves, blindplay_render, blindplay_shape,
                        qa_packet)

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.setattr(blindplay_faces, "_FIGHT_STORE_DIR",
                        tmp_path)
    monkeypatch.setenv("GITS_LANE", "9")
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


def combat(**battle) -> dict:
    state = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]
    state = copy.deepcopy(state)
    state["battle"].update(battle)
    return state


def body(entity_id: str, name: str, combat_id: int, intents=None,
         hp: int = 40, move_id: str | None = None) -> dict:
    row = {"entity_id": entity_id, "combat_id": combat_id, "name": name,
           "hp": hp, "max_hp": hp, "block": 0, "status": [],
           "intents": intents if intents is not None else [
               {"type": "Attack", "label": "6", "title": "Aggressive",
                "description": "This enemy intends to Attack for 6 "
                               "damage."}]}
    if move_id is not None:
        row["move_id"] = move_id
    return row


def queen(round_: int = 1) -> dict:
    return combat(round=round_, enemies=[
        body("TORCH_HEAD_AMALGAM_0", "Torch Head Amalgam", 1, hp=199),
        body("QUEEN_0", "Queen", 2, hp=400)])


def decimillipede(round_: int = 1) -> dict:
    return combat(round=round_, enemies=[
        body(f"DECIMILLIPEDE_SEGMENT_{part}_0", "Decimillipede", n + 1)
        for n, part in enumerate(("FRONT", "MIDDLE", "BACK"))])


def door(state: dict, tmp_path: Path, capsys, brief: bool = True) -> str:
    """The page as a seat's `observe [--brief]` prints it."""
    raw = tmp_path / "state.json"
    raw.write_text(json.dumps(state), encoding="utf-8")
    args = blindplay.argparse.Namespace(raw_file=str(raw), brief=brief,
                                        define="")
    blindplay.cmd_observe(args)
    return capsys.readouterr().out


HEADING = blindplay_render.BRIEFING_HEADING


# --------------------------------------------- 1. the briefing, per fight --


def test_the_first_brief_page_of_a_fight_briefs_it_once(tmp_path, capsys):
    first = door(queen(), tmp_path, capsys)
    assert HEADING in first
    assert "*Queen* — Puppet Strings" in first
    assert "*Torch Head Amalgam* — Tackle" in first
    again = door(queen(), tmp_path, capsys)
    assert HEADING not in again


def test_a_word_the_lane_saw_does_not_cut_the_briefing(tmp_path, capsys):
    """The live find: the lane's seen-words store held the Queen's briefing
    (its one round-1 page had gone past a seat's own `sed` slice) and every
    later brief page cut it. A new fight briefs regardless."""
    page = blindplay.observe(queen())
    seen = {blindplay_brief.definition_key(*blindplay_brief.definition(ln))
            for ln in page.splitlines() if ln.startswith("*Queen* — ")}
    assert seen
    blindplay_shape.write_words_seen(seen)
    assert "*Queen* — Puppet Strings" in door(queen(), tmp_path, capsys)


def test_the_first_page_of_a_fight_briefs_it_whatever_the_round(
        tmp_path, capsys):
    """A seat whose first page of the fight is round 3 (a handoff, a page
    it never asked for) is still briefed, once."""
    assert "*Queen* —" in door(queen(round_=3), tmp_path, capsys)
    assert HEADING not in door(queen(round_=3), tmp_path, capsys)


def test_the_decimillipede_is_briefed(tmp_path, capsys):
    page = door(decimillipede(), tmp_path, capsys)
    assert page.count("Reattach: a segment at 0 HP") == 1


def test_the_next_fight_is_briefed_again(tmp_path, capsys):
    door(queen(), tmp_path, capsys)
    assert "*Decimillipede* —" in door(decimillipede(), tmp_path, capsys)


def test_a_new_seat_is_briefed_mid_fight(tmp_path, capsys):
    door(queen(round_=2), tmp_path, capsys)
    blindplay.cmd_new_seat(None)
    capsys.readouterr()
    assert "*Queen* —" in door(queen(round_=2), tmp_path, capsys)


def test_plain_observe_still_prints_it_every_round_one_page(tmp_path,
                                                            capsys):
    door(queen(), tmp_path, capsys)
    assert "*Queen* —" in door(queen(), tmp_path, capsys, brief=False)
    assert HEADING not in door(queen(round_=2), tmp_path, capsys,
                               brief=False)


# ------------------------------------------------ 2. incoming on a stage --


def stage_combat(seats=("chevreuse",), log=()) -> dict:
    state = combat(round=2, enemies=[body("NIBBIT_0", "Nibbit", 1)])
    state["player"]["character"] = "Furina"
    state["player"]["furina_stage"] = {
        "live": True, "fanfare": 4, "drained": 3, "drain_line": 39,
        "entry_hp": 78,
        "seats": [{"member": m, "name": m.capitalize(), "seat": n,
                   "entity_id": str(20 + n), "seat_key": n + 1,
                   "guest": True}
                  for n, m in enumerate(seats)],
        "log": list(log)}
    return state


def incoming(page: str) -> str:
    return next(ln for ln in page.splitlines()
                if ln.startswith("- Incoming this turn"))


def test_a_stage_board_prints_the_incoming_line():
    line = incoming(blindplay.observe(stage_combat()))
    assert line.startswith("- Incoming this turn: 6 (your Block")
    assert "guests" not in line


def test_sigewinne_on_stage_says_the_acts_may_add_block():
    line = incoming(blindplay.observe(stage_combat(("sigewinne",))))
    assert line.endswith(blindplay_render.INCOMING_STAGE_BLOCK)


def test_co_op_still_prints_no_incoming_line():
    """A co-op telegraph carries no target: either player may take it."""
    src = Path(blindplay_render.__file__).read_text(encoding="utf-8")
    guard = src.split('_incoming_line(c["enemies"], you,', 1)[0]
    assert guard.split("\n")[-2].strip() == (
        'if c["enemies"] and not obs.get("coop"):')


# --------------------------------------------------- 3. since last page --


def ev(kind, seq, card="", target="", power="", on_player=False,
       amount=0) -> dict:
    return {"kind": kind, "card": card, "target": target, "power": power,
            "combat_id": "", "on_player": on_player, "seq": seq,
            "amount": amount}


def row(card: str, events) -> dict:
    return {"card_id": card.upper(), "card": card, "auto_played": False,
            "carried": False, "overflowed": False, "hits": [], "applied": [],
            "summoned": [], "oath": [], "between": not card,
            "events": list(events)}


def since(state: dict) -> list[str]:
    return [ln for ln in blindplay.observe(state).splitlines()
            if ln.startswith(blindplay_render.EVENTS_HEAD)]


def test_passive_powers_are_not_news():
    state = queen(round_=2)
    state["player"]["resolutions"] = [
        row("Strike", [ev("triggered", 1, target="Vantom", power="Slippery"),
                       ev("triggered", 2, target="Vantom", power="Slippery"),
                       ev("triggered", 3, target="Spiny Toad",
                          power="Thorns"),
                       ev("triggered", 4, target="Bygone Effigy",
                          power="Slow")]),
        row("", [ev("triggered", 5, target="Frog Knight", power="Plating")])]
    assert since(state) == []


def test_a_one_off_trigger_still_prints():
    state = queen(round_=2)
    state["player"]["resolutions"] = [
        row("Bash", [ev("triggered", 1, target="Rocket", power="Crab Rage")])]
    assert since(state) == ["- Since last page: Rocket's Crab Rage fired."]


def test_a_shatter_names_the_card_and_the_frozen_it_took():
    state = queen(round_=2)
    state["player"]["resolutions"] = [
        row("Strike", [ev("shattered", 1, card="Strike", target="Queen",
                          power="Frozen")])]
    assert since(state) == [
        "- Since last page: Strike Shattered Queen: Frozen removed."]


def reward_state(rows) -> dict:
    return {"state_type": "card_reward",
            "player": {"character": "Furina", "potions": [], "relics": [],
                       "max_potion_slots": 3, "resolutions": rows},
            "card_reward": {"prompt": "Add a card to your deck.",
                            "can_skip": True,
                            "cards": [{"index": 0, "name": "Strike",
                                       "description": "Deal 6 damage.",
                                       "cost": "1", "card_type": "Attack"}]}}


def test_the_curtain_call_is_said_once_on_the_next_screen(tmp_path, capsys):
    rows = [row("", [ev("curtain", 9001, amount=12)])]
    first = door(reward_state(rows), tmp_path, capsys)
    assert ("- Since last page: Drained 12 HP returned (the fight ended)."
            in first)
    assert "Drained 12 HP returned" not in door(reward_state(rows), tmp_path,
                                                capsys)
    # No printing door, no line (the session's pages are not lane pages).
    assert "Drained" not in blindplay.observe(reward_state(rows))


# ------------------------------------------------- 4. a guest, readable --


CHEVREUSE = {
    "id": "KLEEMOD-PROTO_FS_GUEST_STAR_CHEVREUSE",
    "name": "Guest Star: Chevreuse", "description": "Summon Chevreuse.",
    "cost": "1", "card_type": "Skill",
    "keywords": [
        {"name": "Summon", "description": "A guest joins at the back."},
        {"name": "Guest Star", "description": "Acts at the end of your "
                                              "turn."},
        {"name": "Chevreuse",
         "description": "Whenever you Spend, apply 1 Vulnerable to a random "
                        "enemy. Act: deal 4 damage to a random enemy."}]}


def test_a_guest_star_prints_its_line_and_act_under_the_face():
    page = blindplay.observe(reward_state([]) | {
        "card_reward": {"prompt": "Add a card to your deck.",
                        "can_skip": True,
                        "cards": [dict(CHEVREUSE, index=0)]}})
    lines = page.splitlines()
    at = lines.index("    Summon Chevreuse.")
    assert lines[at + 1] == ("    Line: Whenever you Spend, apply 1 "
                             "Vulnerable to a random enemy.")
    assert lines[at + 2] == "    Act: deal 4 damage to a random enemy."
    assert "*Chevreuse* —" not in page
    # The brief page keeps them: they are not glosses.
    brief = blindplay_brief.brief(page, set())
    assert "    Act: deal 4 damage to a random enemy." in brief


# ------------------------------------------------ 5. Chevreuse's act log --


def test_chevreuse_acts_for_damage_not_energy():
    stage = blindplay_board.furina_stage({"furina_stage": {
        "live": True, "seats": [],
        "log": [{"event": "act", "member": "chevreuse",
                 "name": "Chevreuse", "seat": 0, "seat_key": 1,
                 "fanfare": 0, "moved": 4, "target": "", "target_id": ""}]}})
    (line,) = blindplay_render._render_stage_log(stage)
    assert "4 damage to a random enemy" in line
    assert "Energy" not in line


def test_every_guest_act_kind_matches_the_mod():
    """The page's table against `FurinaStage.CueOf`: a Repay guest logs a
    Repay, every other guest logs damage."""
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "FurinaStage.cs").read_text(encoding="utf-8")
    body = src.split("private static StageForecastCue CueOf", 1)[1]
    body = body.split("};", 1)[0]
    repay = set(re.findall(r"StagePerformer\.(\w+) => new\(seat\.Who, "
                           r"seat\.Key,\s*StageCueKind\.Repay", body))
    guests = re.search(r"Guests =\s*\{([^}]*)\}", src).group(1)
    current = re.findall(r'"(\w+)"', guests)
    assert len(current) == 11          # the pool to 75's four join
    kinds = {m: blindplay_render.STAGE_MEMBER_KINDS.get(m, "damage")
             for m in current}
    assert {m.capitalize() for m, k in kinds.items() if k == "repay"} \
        == repay
    assert set(kinds.values()) == {"repay", "damage"}


# --------------------------------------------- 6. what a debuff move does --


def test_a_debuff_telegraph_names_what_the_move_does():
    state = combat(round=2, enemies=[
        body("FLYCONID_0", "Flyconid", 1, move_id="FRAIL_SPORES_MOVE",
             intents=[{"type": "Attack", "label": "8", "title": "Aggressive",
                       "description": "This enemy intends to Attack for 8 "
                                      "damage."},
                      {"type": "Debuff", "title": "Strategic",
                       "description": "This enemy intends to apply a "
                                      "Debuff."}]),
        body("THIEVING_HOPPER_0", "Thieving Hopper", 2,
             move_id="THIEVERY_MOVE",
             intents=[{"type": "CardDebuff", "title": "Malicious",
                       "description": "This enemy intends to do something "
                                      "to your cards."}])])
    page = blindplay.observe(state)
    # Seat page 5: the game's generic hover sentence is not printed.
    assert "Strategic (Debuff) — the move: applies Frail 2" in page
    assert "the move: steals a card from your draw or discard pile" in page
    assert page.count("the move:") == 2


def test_an_unknown_move_prints_nothing_extra():
    state = combat(round=2, enemies=[
        body("NIBBIT_0", "Nibbit", 1, move_id="SOME_MOVE",
             intents=[{"type": "Debuff", "title": "Strategic"}])])
    assert "the move:" not in blindplay.observe(state)


@pytest.mark.parametrize("key", sorted(blindplay_moves.MOVE_EFFECTS))
def test_every_move_effect_is_blind_and_short(key):
    text = blindplay_moves.MOVE_EFFECTS[key]
    qa_packet.assert_blind(blindplay_render.INTENT_EFFECT_CLAUSE.format(
        effect=text))
    assert len(text) <= 120, key
    for word in ("should", "best", "you want"):
        assert word not in text


def test_the_bridge_sends_the_move_id():
    src = (REPO / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs"
           ).read_text(encoding="utf-8")
    assert 'state["move_id"] = moveState.Id;' in src


# ----------------------------------------------------- 7. the Drain line --


def test_the_drain_line_says_where_it_comes_from():
    state = stage_combat()
    state["player"]["furina_stage"]["drain_line_why"] = (
        "the HP you started this fight with, minus 1/4 of your Max HP")
    page = blindplay.observe(state)
    # The Drain line rule (2026-10-09): a Drain may go past the line, and
    # the line is entry HP minus 1/4 of Max HP.
    assert ("Drain line 39 HP (the HP you started this fight with, minus "
            "1/4 of your Max HP): HP you Drain past it is lost unless you "
            "Repay it.") in page
    # The glossary's Drain row says the rule plainly.
    assert ("Your line is the HP you started this fight with, minus 1/4 of "
            "your Max HP.") in blindplay.ARM_KEYWORDS["Drain"]


def test_an_older_build_derives_the_half_line():
    page = blindplay.observe(stage_combat())
    assert "Drain line 39 HP (half the HP you started this fight with)" \
        in page


# --------------------------------------------------- 8. the seat brief --


def test_the_seat_brief_says_never_call_bare_python():
    text = (REPO / "docs" / "current" / "operations" / "seat-brief.md"
            ).read_text(encoding="utf-8")
    assert "Never call bare `python` or `python3`" in text
