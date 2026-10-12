"""`understudy.embark --abyss` (2026-10-12): a seat lane starts a Spiral
Abyss run.

The flag sets `GITS_ABYSS=1` on the launched game; the mod
(`klee-mod/KleeCode/Abyss/AbyssLane.cs`, pinned in
`klee-mod/KleeTests/AbyssLaneTests.cs`) puts the Spiral Abyss modifier on the
run the ordinary character select starts, and the embark reads the run's
modifiers back off the bridge's `run.modifiers`. Co-op is pinned in
`test_coop_seats.py`. The last block checks the blind page prints what an
Abyss run puts in front of a seat: the choice page, the Blessing and Shadow
relics, the enemy badges and the Abyss Mage Shield, by name and text.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from understudy import blindplay, bridge, embark, soak

REPO = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------- the flag --

def test_the_variable_is_the_one_the_mod_reads():
    lane = (REPO / "klee-mod" / "KleeCode" / "Abyss"
            / "AbyssLane.cs").read_text(encoding="utf-8")
    assert f'"{embark.ABYSS_ENV}"' in lane
    assert embark.abyss_env(True) == {"GITS_ABYSS": "1"}
    # Cleared, not left out, so a stray export cannot reach the game.
    assert embark.abyss_env(False) == {"GITS_ABYSS": ""}


def test_the_read_back():
    assert embark.abyss_read_back(["KLEEMOD-SPIRAL_ABYSS"]) is True
    assert embark.abyss_read_back(["spiral_abyss"]) is True
    assert embark.abyss_read_back([]) is False
    assert embark.abyss_read_back(["DRAFT"]) is False
    assert embark.abyss_read_back(None) is None
    assert embark.abyss_word(True) == "abyss"
    assert embark.abyss_word(None) == "abyss (unread)"
    assert embark.abyss_word(False) == ""


def test_every_parallel_lane_gets_the_flag():
    labels = ["lane1", "lane2"]
    cmds = embark.lane_commands(labels, characters=["klee", "varka"],
                                seeds=[None, None], ascension=None,
                                max_actions=0, arms=[], abyss=True)
    assert all(c[-1] == "--abyss" for c in cmds)
    plain = embark.lane_commands(labels, characters=["klee", "varka"],
                                 seeds=[None, None], ascension=None,
                                 max_actions=0, arms=[])
    assert all("--abyss" not in c for c in plain)


def test_the_parallel_cli_passes_it(monkeypatch):
    seen = {}

    def fake(labels, commands, **kw):
        seen["commands"] = commands
        return []

    monkeypatch.setattr(embark, "embark_lanes", fake)
    embark.main(["--lanes", "1,2", "--character", "klee", "--abyss"])
    assert all("--abyss" in c for c in seen["commands"])


def test_a_hold_embark_refuses_it(capsys):
    assert embark.main(["--hold", "--abyss"]) == 2
    assert "--abyss" in capsys.readouterr().err


def test_the_status_row_says_abyss():
    row = {"lane": "lane1", "port": 15527, "exit": 0, "character": "Klee",
           "run_seed": "SEED", "ascension": 0, "stamp": "S", "log": "L",
           "abyss": True}
    assert "UP  Klee  abyss  seed SEED" in embark.render_lane_rows([row])
    plain = dict(row, abyss=False)
    assert "UP  Klee  seed SEED" in embark.render_lane_rows([plain])
    unread = dict(row, abyss=None)
    assert "Klee  abyss (unread)  seed" in embark.render_lane_rows([unread])


# ------------------------------------------------------------ the embark --

class _Session:
    made: list["_Session"] = []

    def __init__(self, stamp, do_setup=True, intent=None, instance=None,
                 install_bridge=True, extra_env=None):
        self.instance = instance
        self.extra_env = extra_env
        self.ledger = soak.Reversibility(Path("rev.json"))
        type(self).made.append(self)

    def setup(self):
        pass


def _driver(modifiers):
    class _Driver:
        character_actual = "Klee"
        log = Path("run.jsonl")

        def __init__(self, *a, **kw):
            pass

        def _to_main_menu(self):
            return {"state_type": "menu"}

        def _embark(self, state):
            return state

        def _verify_character(self, state):
            run = {"floor": 1, "ascension": 0}
            if modifiers is not None:
                run["modifiers"] = list(modifiers)
            return {"state_type": "event", "run": run}

    return _Driver


def _stubs(tmp_path, monkeypatch, modifiers=("KLEEMOD-SPIRAL_ABYSS",)):
    _Session.made = []
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "Session", _Session)
    monkeypatch.setattr(soak, "RunDriver", _driver(modifiers))
    monkeypatch.setattr(bridge, "seed_read_back", lambda: "SEEDSEED")


def test_the_embark_hands_the_game_the_variable_and_records_the_run(
        tmp_path, monkeypatch):
    _stubs(tmp_path, monkeypatch)
    blob = embark.embark("KLEE", abyss=True)
    assert _Session.made[-1].extra_env["GITS_ABYSS"] == "1"
    assert blob["abyss_requested"] is True and blob["abyss"] is True
    on_disk = json.loads((tmp_path / f"embark-{blob['stamp']}.json")
                         .read_text(encoding="utf-8"))
    assert on_disk["run_modifiers"] == ["KLEEMOD-SPIRAL_ABYSS"]
    assert on_disk["abyss"] is True


def test_a_plain_embark_clears_the_variable(tmp_path, monkeypatch):
    _stubs(tmp_path, monkeypatch, modifiers=())
    blob = embark.embark("KLEE")
    assert _Session.made[-1].extra_env["GITS_ABYSS"] == ""
    assert blob["abyss_requested"] is False and blob["abyss"] is False


def test_a_run_that_lacks_the_abyss_is_refused(tmp_path, monkeypatch):
    _stubs(tmp_path, monkeypatch, modifiers=())
    with pytest.raises(embark.EmbarkError, match="abyss_not_honoured"):
        embark.embark("KLEE", abyss=True)


def test_an_older_bridge_leaves_it_unread(tmp_path, monkeypatch):
    _stubs(tmp_path, monkeypatch, modifiers=None)
    blob = embark.embark("KLEE", abyss=True)
    assert blob["abyss"] is None


def test_the_solo_cli_prints_the_mode(tmp_path, monkeypatch, capsys):
    _stubs(tmp_path, monkeypatch)
    monkeypatch.setattr(soak, "lane_setup", lambda lane: (None, True))
    assert embark.main(["--character", "klee", "--abyss"]) == 0
    assert "mode:      abyss" in capsys.readouterr().out


# ---------------------------------------------------- the page a seat reads --

PAGE_BODY = ("The Spiral Abyss stirs before the Ancient. Take one Blessing. "
             "The enemies take one of the two Shadows you pass, at random.")


def _option(index, title, text):
    return {"index": index, "title": title, "description": text,
            "is_locked": False, "is_proceed": False, "was_chosen": False,
            "keywords": []}


def _choice_page():
    return {"state_type": "event",
            "run": {"act": 1, "floor": 1, "ascension": 0,
                    "modifiers": ["KLEEMOD-SPIRAL_ABYSS"]},
            "player": {"character": "Klee", "hp": 70, "max_hp": 70,
                       "gold": 99, "relics": [], "potions": [],
                       "status": []},
            "event": {"event_id": "NEOW", "event_name": "Neow",
                      "is_ancient": True, "in_dialogue": False,
                      "body": PAGE_BODY,
                      "options": [
                          _option(0, "The Ley Line",
                                  "Enemies' auras fade.\nIf passed: Abyss "
                                  "Herald. Enemies have 15% more HP."),
                          _option(1, "Resonance",
                                  "Turn 1: draw 1 and gain 1 Energy.\nIf "
                                  "passed: Sheer Cold. End your turn with no "
                                  "Block: lose 3 HP."),
                          _option(2, "Fateful Fortune",
                                  "Gain 12 Max HP.\nIf passed: Rally. When an "
                                  "enemy dies, the others gain 1 Strength.")]}}


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def test_the_choice_page_prints_as_an_ordinary_event():
    page = blindplay.observe(_choice_page())
    assert PAGE_BODY in page
    for title in ("The Ley Line", "Resonance", "Fateful Fortune"):
        assert f"**{title}**" in page
    assert "Gain 12 Max HP." in page
    assert "If passed: Sheer Cold." in page
    assert 'choose "<option>"' in page


def _combat():
    return {"state_type": "elite",
            "run": {"act": 1, "floor": 6, "ascension": 0,
                    "modifiers": ["KLEEMOD-SPIRAL_ABYSS"]},
            "player": {"character": "Klee", "hp": 60, "max_hp": 82,
                       "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                       "potions": [], "status": [],
                       "draw_pile_count": 5, "discard_pile_count": 0,
                       "exhaust_pile_count": 0,
                       "relics": [
                           {"id": "KLEEMOD-ABYSS_FATEFUL_FORTUNE_RELIC",
                            "name": "Fateful Fortune",
                            "description": "Gain 12 Max HP."},
                           {"id": "KLEEMOD-ABYSS_SHADOWS_RELIC",
                            "name": "Abyss Shadows",
                            "description": "The enemies carry these Shadows:"
                                           "\nAbyss Mage Shield: Elites enter "
                                           "combat with a shield."}]},
            "battle": {"round": 1, "enemies": [
                {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                 "hp": 44, "max_hp": 44, "block": 0,
                 "intents": [{"type": "Attack", "damage": 5}],
                 "status": [
                     {"id": "KLEEMOD-ABYSS_MAGE_SHIELD_SHADOW_POWER",
                      "name": "Abyss Mage Shield", "amount": 1,
                      "stack": "Single", "type": "Buff",
                      "description": "Elites enter combat with a shield of "
                                     "this act's element.",
                      "keywords": []},
                     {"id": "KLEEMOD-PYRO_ABYSS_SHIELD_POWER",
                      "name": "Pyro Abyss Shield", "amount": 8,
                      "stack": "Counter", "type": "Buff",
                      "description": "Stops all damage. Each hit removes 1 "
                                     "and a reaction removes 3. A Hydro hit "
                                     "breaks it.",
                      "keywords": []}]}]}}


def test_the_badges_and_the_shield_print_by_name_and_text():
    page = blindplay.observe(_combat())
    assert "Abyss Mage Shield" in page
    assert "Pyro Abyss Shield" in page
    assert "Stops all damage." in page
    assert "A Hydro hit breaks it." in page


def test_the_abyss_relics_print_by_name_and_text():
    page = blindplay.observe(_combat())
    assert "Fateful Fortune" in page
    assert "Abyss Shadows" in page
