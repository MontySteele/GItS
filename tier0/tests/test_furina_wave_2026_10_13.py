"""THE FURINA WAVE (2026-10-13): the record's "To change now" list.

`review/records/furina-wave-2026-10-13.md`, items 1-7. Text, previews and the
harness only; no card number, cost or rule moves:

1. One Drain number on the seat page (the buffer left, and that it returns
   after combat); no "Drain line N HP". A no-choice Drain stopped at the line
   says so in the stage log.
2. Rising Applause's rider opens with "Whenever you lose HP, gain that much
   Fanfare."
3. Crashing Waves' face says what its "Spend up to 16" buys now.
4. Final Bow's rider: its acts happen one after another.
5. The boss Frozen preview is titled Vulnerable.
6. Buffer (a base power) prints in the player's powers on a Furina page.
7. `proceed` is held once past a chest's relic and a card offer.

The C# twin is `klee-mod/KleeTests/Prototype/FurinaWaveTests.cs`.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import pytest

from understudy import (blindplay, blindplay_board, blindplay_render,
                        blindplay_shape, lanewatch)

from tier0.tests.test_arm_keyword_tips import PROTOTYPE_DIR, TIPS_CS, gen, proto
from tier0.tests.test_understudy_blindplay import combat_state

REPO = Path(__file__).resolve().parents[2]
POWERS = REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
KLEEMOD_CS = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"
KEYWORD_JSON = (REPO / "klee-mod" / "pck-src" / "klee" / "localization"
                / "eng" / "card_keywords.json")


def _rows() -> dict[str, dict]:
    return {r["id"]: r for r in proto._rows()}


def _wire(**extra) -> dict:
    raw = {"live": True, "fanfare": 4, "drained": 6, "drain_line": 61,
           "drain_line_why": "your HP minus your Drain buffer: 1/4 of your "
                             "Max HP, less what you have drained",
           "entry_hp": 78, "entry_max_hp": 78, "drain_buffer": 19,
           "drain_buffer_left": 13, "seats": [], "log": []}
    raw.update(extra)
    return raw


def _stage_lines(raw: dict) -> list[str]:
    stage = blindplay_board.furina_stage({"furina_stage": raw})
    assert stage is not None
    return blindplay_render._render_stage(
        stage, {"block": 0, "hp": 74, "max_hp": 78})


# ---- 1. one Drain number ------------------------------------------------------

def test_the_page_prints_one_drain_number_and_no_line():
    lines = _stage_lines(_wire())
    drain = [ln for ln in lines if "Drain" in ln]
    assert drain == ["- Drain buffer: 13 HP left. Drain inside it returns "
                     "after combat; past it (past your line), only Repay "
                     "returns."]
    page = "\n".join(lines)
    assert "Drain line" not in page and "61" not in page
    assert "of 19" not in page


def test_every_buffer_sentence_carries_one_number():
    for raw in (_wire(), _wire(drain_line=0), _wire(past_returns=True),
                _wire(drained=25, drained_past=6, drain_buffer_left=0)):
        line = next(ln for ln in _stage_lines(raw)
                    if ln.startswith("- Drain buffer"))
        assert "Drain line" not in line
        # The buffer left, and (only past it) the HP lost past it.
        numbers = [w for w in line.replace(".", " ").split() if w.isdigit()]
        assert len(numbers) <= 2, line


def _stopped(**row) -> dict:
    beat = {"event": "stopped", "member": "lyney", "name": "Lyney",
            "seat": -1, "seat_key": -1, "fanfare": 4, "moved": 2,
            "reason": "buffer", "source": ""}
    beat.update(row)
    return beat


def test_a_guests_drain_stopped_at_the_line_is_printed():
    stage = blindplay_board.furina_stage(
        {"furina_stage": _wire(log=[_stopped()])})
    assert stage["log"][0]["event"] == "stopped"
    assert blindplay_render._render_stage_log(stage) == [
        "  - **Lyney**'s Drain was stopped: your Drain buffer is used up."]


def test_reginas_stop_names_the_power_and_the_hp_reason_reads():
    stage = blindplay_board.furina_stage({"furina_stage": _wire(log=[
        _stopped(member="", name="", source="Regina of All Waters"),
        _stopped(reason="hp")])})
    assert blindplay_render._render_stage_log(stage) == [
        "  - **Regina of All Waters**' Drain was stopped: your Drain buffer "
        "is used up.",
        "  - **Lyney**'s Drain was stopped: it would take you to 0 HP."]


def test_the_mod_notes_the_stop_for_lyney_and_regina():
    director = (POWERS / "FurinaStageDirector.cs").read_text(encoding="utf-8")
    ledger = (POWERS / "FurinaStageLedger.cs").read_text(encoding="utf-8")
    assert 'public const string StoppedEvent = "stopped";' in ledger
    assert "NoChoiceDrain(FurinaStageLaw.LyneyActDrain" in director
    assert "NoChoiceDrain(FurinaStageLaw.ReginaDrain" in director
    # No guest Drain reads the room by hand any more.
    assert "GuestDrainRoom(FurinaStageLaw." not in director


def test_the_counter_and_the_face_print_no_line_number():
    counter = (REPO / "klee-mod" / "KleeCode" / "Vfx" / "Prototype"
               / "DrainedCounter.cs").read_text(encoding="utf-8")
    # The localization census (2026-10-23, step 2): keyed rows.
    assert '"Drain buffer: [blue]{Buffer}[/blue] HP left.' in counter
    assert '"Drain line [blue]' not in counter
    face = (POWERS / "FurinaStageBowPreview.cs").read_text(encoding="utf-8")
    # Her HP legibility pass (2026-10-19): the all-past tag.
    assert '"\\n(Past your line: lost unless you Repay)");' in face
    assert "Drain line of {line}" not in face


# ---- 2. Rising Applause teaches Fanfare -----------------------------------------

def test_rising_applause_says_lost_hp_becomes_fanfare():
    # The tip's keyed row (the localization census, 2026-10-23).
    tips = TIPS_CS.with_name("PlayerTips.cs").read_text(encoding="utf-8")
    assert ('"Whenever you lose HP, gain that much [gold]Fanfare[/gold]. Its "'
            in tips)
    src = (PROTOTYPE_DIR / "ProtoFsStandingOvation.cs").read_text(
        encoding="utf-8")
    assert "ArmKeywordTips.ForBankDamage(" in src
    # Rendered with its markup folded, it fits the tip ceiling.
    body = ("Whenever you lose HP, gain that much Fanfare. Its damage is the "
            "Fanfare you hold: play it when the bank is worth it.")
    assert len(body) <= 135


# ---- 3. Crashing Waves' preview ---------------------------------------------------

def test_crashing_waves_previews_what_its_spend_buys():
    src = (PROTOTYPE_DIR / "ProtoFsCrashingWaves.cs").read_text(
        encoding="utf-8")
    assert "{InCombat:{StageSpendHits}|}" in src
    assert ('description.Add("StageSpendHits", '
            "FurinaStageFacePreview.SpendUpToHits(this, 16));") in src
    face = (POWERS / "FurinaStageBowPreview.cs").read_text(encoding="utf-8")
    assert ': no extra hit)"' in face
    for rid, row in _rows().items():
        assert (gen.stage_spend_hits_call(row) is not None) == (
            rid == "proto_fs_crashing_waves"), rid


# ---- 4. Final Bow -------------------------------------------------------------------

def test_final_bow_says_its_acts_are_in_turn():
    src = (PROTOTYPE_DIR / "ProtoFsFinalBow.cs").read_text(encoding="utf-8")
    assert "ArmKeywordTips.ForFinalBowInTurn(" in src
    assert ('"Its acts happen one after another, not all at once."'
            in TIPS_CS.read_text(encoding="utf-8"))
    assert "ArmKeywordTips.FinalBowInTurnKey + \".title\"" in (
        KLEEMOD_CS.read_text(encoding="utf-8"))
    for rid, row in _rows().items():
        assert gen.final_bow_acts_in_turn(row) == (
            rid == "proto_fs_final_bow"), rid


# ---- 5. the boss preview says Vulnerable ----------------------------------------------

def test_the_boss_frozen_preview_is_titled_vulnerable():
    mod = KLEEMOD_CS.read_text(encoding="utf-8")
    assert ('["KLEEMOD-FROZEN_BOSS_PREVIEW.title"] = '
            '"Reaction preview: Vulnerable (Boss)"') in mod
    loc = json.loads(KEYWORD_JSON.read_text(encoding="utf-8"))
    assert loc["KLEEMOD-FROZEN_BOSS_PREVIEW.title"] == (
        "Reaction preview: Vulnerable (Boss)")
    assert "Vulnerable" in loc["KLEEMOD-FROZEN_BOSS_PREVIEW.description"]


# ---- 6. Buffer on a Furina page -------------------------------------------------------

BUFFER = {"id": "BUFFER_POWER", "name": "Buffer", "amount": 1, "type": "Buff",
          "stack": "Counter",
          "description": "Prevent the next time you would lose HP.",
          "keywords": []}


def test_buffer_prints_in_the_players_powers_on_a_furina_page():
    blindplay.forget_fight()
    blindplay.forget_run()
    state = combat_state()
    player = state["player"]
    player["status"] = list(player.get("status") or []) + [copy.deepcopy(BUFFER)]
    player["furina_stage"] = _wire()
    page = blindplay.observe(state)
    assert ("- Buffer 1 (buff) — Prevent the next time you would lose HP."
            in page.splitlines())
    blindplay.forget_fight()
    blindplay.forget_run()


# ---- 7. the proceed hold ----------------------------------------------------------------

@pytest.fixture
def lane(tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.delenv(blindplay.LANE_ENV, raising=False)
    monkeypatch.delenv(blindplay.MAX_ACTIONS_ENV, raising=False)
    monkeypatch.setattr(lanewatch, "guard", lambda *a, **k: "")
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


class _Wire:
    def __init__(self, state):
        self.state = state
        self.posts: list = []

    def get_state(self):
        return json.loads(json.dumps(self.state))

    def health(self):
        return {"status": "ok"}

    def post(self, action, **kw):
        self.posts.append((action, kw))
        return {"status": "ok", "message": f"Doing {action}"}


def _live(monkeypatch, state) -> _Wire:
    wire = _Wire(state)
    monkeypatch.setattr(blindplay, "bridge", wire)
    monkeypatch.setattr(blindplay, "_load_state", lambda _a: wire.get_state())
    return wire


def _act(command: str) -> int:
    return blindplay.cmd_act(argparse.Namespace(
        raw_file="", command=command, dry_run=False, brief=True))


def _chest(*relics) -> dict:
    return {"state_type": "treasure", "run": {"act": 2, "floor": 26},
            "player": {"character": "Furina", "hp": 60, "max_hp": 88,
                       "gold": 100, "potions": [], "relics": []},
            "treasure": {"relics": list(relics), "can_proceed": True}}


SHIELD = {"index": 0, "id": "PARRYING_SHIELD", "name": "Parrying Shield",
          "description": "Whenever you play an Attack, gain 1 Block.",
          "rarity": "Uncommon", "keywords": []}


def test_proceed_past_a_chests_relic_is_held_once(lane, monkeypatch, capsys):
    wire = _live(monkeypatch, _chest(SHIELD))
    assert _act("proceed") == 1
    out = capsys.readouterr().out
    assert "this chest still holds Parrying Shield" in out
    assert "Say `proceed` again" in out
    assert wire.posts == []
    # The second `proceed` is the deliberate skip.
    assert _act("proceed") == 0
    assert [a for a, _ in wire.posts] == ["proceed"]


def test_an_emptied_chest_is_not_held(lane, monkeypatch):
    wire = _live(monkeypatch, _chest())
    assert _act("proceed") == 0
    assert [a for a, _ in wire.posts] == ["proceed"]


def test_the_seat_brief_names_the_new_holds():
    brief = (REPO / "docs" / "current" / "operations" / "seat-brief.md"
             ).read_text(encoding="utf-8")
    assert "a relic or a card offer still on" in brief
    assert "a relic still in an open chest" in brief
