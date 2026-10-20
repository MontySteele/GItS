"""The newcomer seat (2026-10-19): a page that shows only what a human sees.

[USER]: "see if the seats can actually independently figure out how to pilot
the characters". `GITS_NEWCOMER=1` (`tools/seat.py --opus-brief --newcomer`)
turns the seat page into the player's: the player's hover tips (the bridge's
`?audience=player`), no ledger, no forecasts, no glossary, and `--define`
answering with the game's own tip only. Off, every page is the page it was.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path

import pytest

from understudy import blindplay, blindplay_newcomer, bridge

from tier0.tests.test_understudy_blindplay import (card_reward_state,
                                                   combat_state, event_state,
                                                   game_over_state, rest_state,
                                                   rewards_state)

REPO = Path(__file__).resolve().parents[2]


def _seat():
    spec = importlib.util.spec_from_file_location(
        "seat_tool_newcomer", REPO / "tools" / "seat.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def lane(monkeypatch):
    monkeypatch.setenv("GITS_LANE", "3")
    monkeypatch.delenv(bridge.NEWCOMER_ENV, raising=False)


@pytest.fixture
def newcomer(lane, monkeypatch):
    monkeypatch.setenv(bridge.NEWCOMER_ENV, "1")


def _fight() -> dict:
    """The recorded Kokomi turn, with a power on each side and a resolved
    card on the ledger, so every seat-only section has something to say."""
    state = copy.deepcopy(combat_state())
    state["tip_audience"] = "player"
    state["battle"]["round"] = 2
    state["player"]["status"] = [{
        "id": "STRENGTH", "name": "Strength", "amount": 2, "type": "Buff",
        "description": "Increases attack damage by 2."}]
    state["battle"]["enemies"][0]["status"] = [{
        "id": "HYDRO_AURA", "name": "Hydro Aura", "amount": 2,
        "type": "Debuff", "description": "Wears Hydro for 2 turns."}]
    state["player"]["resolutions"] = [{
        "card_id": "water_s_edge", "card": "Water's Edge",
        "auto_played": False, "carried": False, "overflowed": False,
        "hits": [{"target": "Nibbit", "amount": 6, "blocked": 0,
                  "combat_id": "", "label": ""}]}]
    return state


# ---- off: unchanged ----------------------------------------------------------

def test_off_the_seat_page_keeps_its_seat_only_sections(lane):
    page = blindplay.screen_page(_fight())
    assert "## Words on this screen" in page
    assert "Incoming this turn" in page
    assert "## What you played this turn" in page
    assert "[Hydro]" in page


def test_off_the_bridge_asks_for_no_audience(lane, monkeypatch):
    urls = []
    monkeypatch.setattr(bridge, "_request",
                        lambda url, *a, **k: urls.append(url) or {})
    bridge.get_state()
    assert urls and all("audience" not in u for u in urls)


def test_off_the_brief_is_the_brief_and_names_no_newcomer():
    seat = _seat()
    text = seat.brief_text(2, "KLEEMOD-KLEE")
    assert "NEWCOMER" not in text and "GITS_NEWCOMER" not in text
    assert "Exit form" not in text
    coop = seat.brief_text(2, "KLEEMOD-KLEE", coop=True)
    assert "NEWCOMER" not in coop and "Exit form" not in coop
    assert "You share this run with another seat" in coop
    assert "GITS_NEWCOMER" not in seat.lane_scripts(2)["o"]


# ---- on: the fight ----------------------------------------------------------

def test_the_newcomer_fight_keeps_what_a_player_sees(newcomer):
    page = blindplay.screen_page(_fight())
    for line in ("- HP 24/70", "- Block 0", "- Energy 2/3",
                 "- Strength 2 — Increases attack damage by 2.",
                 "Hydro Aura 2 — Wears Hydro for 2 turns.",
                 "- **Pearl of Wisdom** — Whenever a card is Exhausted",
                 "- **Coral Guard** — cost 1, skill",
                 "    Gain 5 Block.",
                 "    *Exhaust* — Removed until the end of combat.",
                 "Intent: Aggressive (12) — This enemy intends to Attack "
                 "for 12 damage.",
                 "## What you can say",
                 "- `end turn`"):
        assert line in page, line


def test_the_newcomer_fight_drops_what_only_a_seat_is_shown(newcomer):
    page = blindplay.screen_page(_fight())
    for cut in ("## Words on this screen",      # the glossary
                "Incoming this turn",           # a forecast
                "You would be at",              # a forecast
                "Since last page",              # the ledger
                "What you played",              # the ledger
                "Elemental Reaction",           # reaction explanation
                "Each enemy keeps its letter",  # a page note
                "[Hydro]",                      # the page's element tag
                "the game's data feed"):        # a meter explanation
        assert cut not in page, cut


def test_a_newcomer_reads_the_page_whole_under_brief(newcomer, capsys,
                                                     tmp_path):
    raw = tmp_path / "state.json"
    raw.write_text(json.dumps(_fight()), encoding="utf-8")
    args = argparse.Namespace(raw_file=str(raw), dry_run=False, brief=True,
                              define="")
    assert blindplay.cmd_observe(args) == 0
    out = capsys.readouterr().out
    assert "## Your hand" in out and "## Words on this screen" not in out


# ---- on: every other screen --------------------------------------------------

def test_the_newcomer_rest_site_drops_the_arithmetic_and_the_ledger(newcomer):
    page = blindplay.screen_page(rest_state())
    assert "HP 30/70" in page and "- **Rest**" in page
    assert "healing stops at max HP" not in page
    assert "## Since the screen before this one" not in page
    assert "This page reads one HP figure" not in page


def test_the_newcomer_card_reward_drops_the_glossary(newcomer):
    page = blindplay.screen_page(card_reward_state())
    assert "- **Bake-Kurage** — cost 1, skill" in page
    assert "## Words on this screen" not in page
    assert "oldest guest" not in page


def test_a_note_that_names_a_command_is_kept(newcomer):
    page = blindplay.screen_page(rewards_state())
    assert "`choose` it to open the card screen" in page


# ---- on: --define ------------------------------------------------------------

def test_define_answers_with_the_games_own_tip(newcomer):
    assert blindplay_newcomer.define(_fight(), "exhaust") == (
        "**Exhaust** — Removed until the end of combat.\n")
    assert "Increases attack damage" in blindplay_newcomer.define(
        _fight(), "Strength")


def test_define_has_no_tip_for_a_seat_glossary_word(newcomer):
    assert blindplay_newcomer.define(_fight(), "Elemental Reaction") == (
        blindplay_newcomer.NO_TIP.format(word="Elemental Reaction") + "\n")


def test_observe_define_goes_through_the_newcomer(newcomer, capsys, tmp_path):
    raw = tmp_path / "state.json"
    raw.write_text(json.dumps(_fight()), encoding="utf-8")
    args = argparse.Namespace(raw_file=str(raw), dry_run=False, brief=True,
                              define="aura")
    assert blindplay.cmd_observe(args) == 0
    assert capsys.readouterr().out.startswith('No tip for "aura"')


# ---- on: the bridge -----------------------------------------------------------

def test_the_newcomer_asks_the_bridge_for_the_players_tips(newcomer,
                                                           monkeypatch):
    urls = []
    monkeypatch.setattr(bridge, "_request",
                        lambda url, *a, **k: urls.append(url) or {})
    bridge.get_state()
    assert urls and all(u.endswith("?audience=player") for u in urls)


def test_an_older_bridge_is_told_apart():
    assert blindplay_newcomer.bridge_ignored_audience({"state_type": "map"})
    assert not blindplay_newcomer.bridge_ignored_audience(
        {"state_type": "map", "tip_audience": "player"})


def test_the_bridge_builds_a_newcomers_state_outside_the_seat_scope():
    mod = (REPO / "vendor" / "STS2_MCP" / "McpMod.cs").read_text(
        encoding="utf-8")
    assert mod.count("GitsAudienceIsPlayer(request)") == 2
    assert "GitsAsPlayer(BuildGameState)" in mod
    assert "GitsAsPlayer(BuildMultiplayerGameState)" in mod
    tips = (REPO / "vendor" / "STS2_MCP" / "gits" / "GitsSeatTips.cs"
            ).read_text(encoding="utf-8")
    assert 'state["tip_audience"] = "player"' in tips


# ---- on: the brief ----------------------------------------------------------

EXIT_FORM = (
    "In one or two sentences, what is this character's central choice?",
    "What confused you, and when (floor/fight) did you figure it out,",
    "What did you misread, and what did it cost?",
    "Would you play another run with this character? Why?",
)


def test_the_newcomer_brief_keeps_the_grammar_and_adds_the_exit_form():
    text = _seat().brief_text(4, "KLEEMOD-YAE", newcomer=True)
    assert text.startswith("You are the blind seat for **KLEEMOD-YAE**")
    assert "blind NEWCOMER seat" in text
    commands = [line for line in text.splitlines()
                if "-m understudy.blindplay" in line]
    assert len(commands) == 2
    assert all("GITS_LANE=4 GITS_NEWCOMER=1 " in line for line in commands)
    assert 'play "<title>" [on "<enemy>"]' in text
    assert "Never call bare `python` or `python3`" in text
    for question in EXIT_FORM:
        assert question in text, question
    assert "<LANE>" not in text


def test_the_newcomer_brief_explains_no_rule():
    text = _seat().brief_text(4, "KLEEMOD-KOKOMI", newcomer=True)
    assert "A Plan nobody flips" not in text
    assert "defines each word the first time" not in text
    assert "## THE BRIEF" not in text and "## CO-OP" not in text
    # The coordinator's paragraph above the rule stays off the seat's page.
    assert "replaces THE BRIEF above" not in text


def test_the_newcomer_coop_brief_adds_the_coop_section():
    text = _seat().brief_text(2, "KLEEMOD-KLEE", coop=True, newcomer=True)
    assert "blind NEWCOMER seat" in text
    assert "You share this run with another seat" in text


def test_the_newcomer_lane_scripts_set_the_flag(tmp_path):
    seat = _seat()
    scripts = seat.lane_scripts(2, newcomer=True)
    for body in scripts.values():
        assert "export GITS_LANE=2 GITS_NEWCOMER=1 " in body
    head = seat.brief_text(2, "X", scratch=str(tmp_path), newcomer=True)
    assert "the newcomer setting" in head.splitlines()[0]


def test_a_power_s_energy_icon_reads_as_energy(newcomer):
    """Newcomer round lane 1 (2026-10-19): Blazing Delight's power text kept
    its `[ironclad_energy_icon.png]` tag, the leak guard refused every page
    and the run stalled mid-fight. Power text goes through `_text`."""
    state = _fight()
    state["player"]["status"].append({
        "id": "BLAZING_DELIGHT", "name": "Blazing Delight", "amount": 1,
        "type": "Buff", "description": "At the start of your turn, gain "
        "[ironclad_energy_icon.png] and draw that many cards."})
    page = blindplay.screen_page(state)
    assert "energy_icon" not in page
    assert "Blazing Delight 1 — At the start of your turn, gain" in page


# ---- Swirl legibility (2026-10-19): the aim preview --------------------------

_SWIRL_TIP = {"name": "Reaction preview: Swirl",
              "description": "Removes the Hydro aura and deals 2 damage to "
                             "ALL enemies."}


def _aimed_fight() -> dict:
    """`_fight()` with the bridge's aim preview on the first card: what a
    drag onto the Nibbit (combat id 1) would show."""
    state = _fight()
    state["player"]["hand"][0]["aim_previews"] = [
        {"combat_id": 1, "tips": [_SWIRL_TIP]},
        # An enemy that is not on this board prints nothing.
        {"combat_id": 99, "tips": [_SWIRL_TIP]}]
    return state


def test_the_newcomer_page_prints_the_aim_preview_under_its_card(newcomer):
    page = blindplay.screen_page(_aimed_fight())
    line = ("    On Nibbit: *Reaction preview: Swirl* — Removes the Hydro "
            "aura and deals 2 damage to ALL enemies.")
    assert page.count(line) == 1
    lines = page.splitlines()
    card = next(i for i, ln in enumerate(lines)
                if ln.startswith("- **Pearl Barrage**"))
    nxt = next(i for i, ln in enumerate(lines)
               if i > card and ln.startswith("- **"))
    assert card < lines.index(line) < nxt
    assert page.count("    On ") == 1


def test_a_card_with_no_aim_preview_prints_no_on_line(newcomer):
    assert "    On " not in blindplay.screen_page(_fight())


def test_off_the_seat_page_is_unmoved_by_the_aim_preview(lane):
    assert (blindplay.screen_page(_aimed_fight())
            == blindplay.screen_page(_fight()))


def test_the_bridge_reads_the_games_own_aim_preview():
    root = REPO / "vendor" / "STS2_MCP"
    aim = (root / "gits" / "GitsAimPreview.cs").read_text(encoding="utf-8")
    assert '"KleeMod.Cards.ReactionAim"' in aim
    assert '"PreviewsFor"' in aim
    assert "if (!_gitsPlayerAudience) return;" in aim
    tips = (root / "gits" / "GitsSeatTips.cs").read_text(encoding="utf-8")
    assert "GitsSetPlayerAudience(true);" in tips
    assert "GitsSetPlayerAudience(false);" in tips
    builder = (root / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert "GitsAddAimPreviews(card, cardRow);" in builder


# ---- newcomer round 1 page fixes (2026-10-19) ---------------------------------

def _reviving_fight() -> dict:
    """Test Subject between forms: every body at 0, no intents, and the
    wire's `battle.reviving` row for the one coming back."""
    state = _fight()
    for e in state["battle"]["enemies"]:
        e["hp"] = 0
        e["intents"] = []
        e.pop("intent", None)
    state["battle"]["reviving"] = [{"combat_id": "", "name": "Test Subject",
                                    "max_hp": 100, "move_id": "RESPAWN"}]
    return state


def test_a_reviving_enemy_is_on_the_newcomer_board(newcomer):
    page = blindplay.screen_page(_reviving_fight())
    enemies = page.split("## Enemies", 1)[1]
    assert ("- **Test Subject** — HP 0/100, down but still on the board"
            in enemies)


def test_a_board_with_no_living_enemy_still_names_who_was_there(newcomer):
    state = _reviving_fight()
    state["battle"]["reviving"] = []
    enemies = blindplay.screen_page(state).split("## Enemies", 1)[1]
    assert "down but still on the board" in enemies


def test_an_event_page_prints_the_top_bar(newcomer):
    state = copy.deepcopy(event_state())
    state["player"] = {"hp": 72, "max_hp": 72, "gold": 171}
    page = blindplay.screen_page(state)
    assert "- HP 72/72, 171 gold" in page


def test_a_page_that_prints_hp_gets_no_second_bar(newcomer):
    state = copy.deepcopy(rest_state())
    state["player"] = {**(state.get("player") or {}), "hp": 30,
                       "max_hp": 70, "gold": 5}
    page = blindplay.screen_page(state)
    assert "gold" not in page.split("HP 30/70", 1)[0]
    assert "- HP 30/70, 5 gold" not in page


def test_the_reward_screen_drops_the_last_fights_plays(newcomer):
    text = ("# What the fight left behind\n\n- **Card**\n\n"
            "## Your plays on the fight's last turn\n\n- **Strike**\n\n"
            "## What you can say\n\n- `proceed`\n")
    page = blindplay_newcomer.trim_page(text)
    assert "# Rewards" in page and "left behind" not in page
    assert "last turn" not in page and "Strike" not in page
    assert "- `proceed`" in page


def test_the_run_over_page_prints_the_deck():
    state = copy.deepcopy(game_over_state())
    state["player"] = {"hp": 0, "max_hp": 72, "gold": 9, "master_deck": [
        {"name": "Strike"}, {"name": "Strike"}, {"name": "Twin Sakura+"}]}
    page = blindplay.screen_page(state)
    assert "- Deck (3 cards): Strike x2, Twin Sakura+" in page
