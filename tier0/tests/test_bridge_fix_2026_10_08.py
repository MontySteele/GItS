"""The seat harness fixes of 2026-10-08 (bridge review, sections 1a-1e).

Lane state keyed to the lane rather than the checkout (with a migration read
of the old location), the page preferring the build's own Klee numbers, the
seat's baked lane scripts, "the fight is over", atomic state writes, the
action count belonging to the run embarked last, and the brief page's relic
and Spark-price trims.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path, PurePath

import pytest

from understudy import (blindplay, blindplay_brief, blindplay_faces,
                        blindplay_notes, blindplay_record, blindplay_shape,
                        embark)

from tier0.tests.test_understudy_blindplay import combat_state, map_state

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def lanes(monkeypatch):
    """The conftest's per-test lane root, with no flat-folder override and
    lane 3 selected."""
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", None)
    monkeypatch.setenv("GITS_LANE", "3")
    monkeypatch.delenv(blindplay_shape.MAX_ACTIONS_ENV, raising=False)
    return blindplay_shape.lane_state_root()


# ---- 1. per-lane state lives under the lane, not the checkout ------------

def test_the_state_folder_is_the_lanes(lanes):
    assert blindplay_shape.lane_state_dir() == lanes / "lane3" / "blindplay"
    assert blindplay_shape.lane_state_dir("lane1") == \
        lanes / "lane1" / "blindplay"
    blindplay_shape.set_budget(1500)
    assert blindplay_shape.budget_path().parent == lanes / "lane3" / "blindplay"
    assert blindplay_shape.budget_path().is_file()


def test_the_default_root_is_localappdata_gits_lanes(monkeypatch, tmp_path):
    monkeypatch.setattr(blindplay_shape, "_LANE_STATE_ROOT", None)
    monkeypatch.delenv(blindplay_shape.LANE_STATE_ENV, raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert blindplay_shape.lane_state_root() == tmp_path / "gits-lanes"
    monkeypatch.setenv(blindplay_shape.LANE_STATE_ENV, str(tmp_path / "x"))
    assert blindplay_shape.lane_state_root() == tmp_path / "x"


def test_two_checkouts_share_one_lanes_state(lanes, monkeypatch, tmp_path):
    """Suite 5: the act-2 seats ran from a second worktree and lost the cap,
    the words and the count. The checkout is now irrelevant to the lane."""
    monkeypatch.setattr(blindplay_shape, "_LEGACY_STATE_DIR", tmp_path / "a")
    blindplay_shape.set_budget(1500)
    blindplay_shape.count_action()
    blindplay_shape.write_words_seen({"bomb|x"})
    monkeypatch.setattr(blindplay_shape, "_LEGACY_STATE_DIR", tmp_path / "b")
    assert blindplay_shape.budget_spent() == (1, 1500)
    assert blindplay_shape.read_words_seen() == {"bomb|x"}


def test_an_old_location_file_is_read_once_when_the_new_one_is_missing(
        lanes):
    legacy = blindplay_shape._LEGACY_STATE_DIR
    (legacy / "_blindplay-budget-lane3.json").write_text(
        json.dumps({"cap": 1500, "count": 247}), encoding="utf-8")
    (legacy / "_blindplay-words-lane3.json").write_text(
        json.dumps(["tainted|x"]), encoding="utf-8")
    assert blindplay_shape.budget_spent() == (247, 1500)
    assert blindplay_shape.read_words_seen() == {"tainted|x"}
    # The first write lands in the new folder, and it wins from then on.
    assert blindplay_shape.count_action() == 248
    assert blindplay_shape.budget_path().is_file()
    (legacy / "_blindplay-budget-lane3.json").write_text(
        json.dumps({"cap": 9, "count": 9}), encoding="utf-8")
    assert blindplay_shape.budget_spent() == (248, 1500)
    # A forget clears both, so the migration read cannot undo it.
    blindplay_shape.forget_words_seen()
    assert blindplay_shape.read_words_seen() == set()
    assert not (legacy / "_blindplay-words-lane3.json").exists()


def test_the_faces_stores_move_and_migrate(lanes, monkeypatch):
    monkeypatch.setattr(blindplay_faces, "_DECK_STORE_DIR", None)
    monkeypatch.setattr(blindplay_faces, "_FIGHT_STORE_DIR", None)
    assert blindplay_faces._deck_store().parent == \
        lanes / "lane3" / "blindplay"
    assert blindplay_faces._fight_store().parent == \
        lanes / "lane3" / "blindplay"
    # The old store's name read the lane raw; it is still found.
    legacy = blindplay_shape._LEGACY_STATE_DIR
    row = {"cards": [{"name": "Strike"}], "character": "Klee",
           "act": 1, "floor": 3}
    (legacy / "_blindplay-deck-lane3.json").write_text(
        json.dumps(row), encoding="utf-8")
    blindplay_faces._DECK_MEMORY.clear()
    assert blindplay_faces._held_deck()["cards"] == [{"name": "Strike"}]
    blindplay_faces.forget_deck()
    assert not (legacy / "_blindplay-deck-lane3.json").exists()


def test_embark_copies_its_sidecar_to_the_lane(lanes, monkeypatch, tmp_path):
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path / "logs")
    embark._write_sidecar("20261008-010000", {
        "stamp": "20261008-010000", "instance": "lane3",
        "run_seed": "SEEDSEED", "game_dir": str(tmp_path / "game")})
    copy = lanes / "lane3" / "blindplay" / "embark-20261008-010000.json"
    assert copy.is_file()
    assert (tmp_path / "logs" / "embark-20261008-010000.json").is_file()
    assert blindplay_shape.lane_run_seed() == "SEEDSEED"
    assert blindplay_shape.lane_embark_stamp() == "20261008-010000"
    assert blindplay_shape.lane_game_dir() == str(tmp_path / "game")


def test_build_version_finds_the_game_without_local_props(
        lanes, monkeypatch, tmp_path):
    """A second worktree has no `klee-mod/local.props`; the lane's sidecar
    names the install the lane launched."""
    monkeypatch.setattr(blindplay, "LOCAL_PROPS", tmp_path / "absent.props")
    game = tmp_path / "game"
    (game / "mods" / "klee").mkdir(parents=True)
    (game / "mods" / "klee" / "manifest.json").write_text(
        json.dumps({"version": "0.2.4516+next"}), encoding="utf-8-sig")
    assert blindplay_record.build_version()[0] == ""
    blindplay_shape.write_atomic(
        blindplay_shape.lane_state_dir() / "embark-20261008-010000.json",
        json.dumps({"stamp": "20261008-010000", "instance": "lane3",
                    "game_dir": str(game)}))
    assert blindplay_record.build_version()[0] == "0.2.4516+next"


def test_granted_arms_reads_the_lanes_sidecar(lanes):
    blindplay_shape.write_atomic(
        blindplay_shape.lane_state_dir() / "embark-20261008-010000.json",
        json.dumps({"stamp": "20261008-010000", "instance": "lane3",
                    "run_seed": "S1", "arms_granted": [{"card_id": "X"}]}))
    assert blindplay_record.granted_arms("S1")[0] == "X"


# ---- 6. atomic writes ------------------------------------------------------

def test_state_writes_are_atomic(lanes, monkeypatch):
    blindplay_shape.set_budget(10)
    path = blindplay_shape.budget_path()
    held = path.read_text(encoding="utf-8")

    def boom(*_a, **_k):
        raise OSError("killed mid-write")
    monkeypatch.setattr(os, "replace", boom)
    blindplay_shape.count_action()
    # The replace never happened: the old file is whole, no temp is left.
    assert path.read_text(encoding="utf-8") == held
    assert not list(path.parent.glob("*.tmp"))
    monkeypatch.undo()
    blindplay_shape.mark_refusal("board", "play X", "why", lane="3")
    assert blindplay_shape.pending_refusal("board", lane="3")["command"] \
        == "play X"
    assert not list(path.parent.glob("*.tmp"))


# ---- 7. the count belongs to the run embarked last ------------------------

def test_a_count_carried_from_an_earlier_run_restarts(lanes):
    """A control seat saw 20 -> 127: the lane was re-embarked by a door that
    left the previous run's count in the store this seat read."""
    blindplay_shape.set_budget(1500, run="20261008-004653")
    for _ in range(126):
        blindplay_shape.count_action()
    blindplay_shape.write_atomic(
        blindplay_shape.lane_state_dir() / "embark-20261008-004653.json",
        json.dumps({"stamp": "20261008-004653", "instance": "lane3"}))
    assert blindplay_shape.count_action() == 127      # same run: carries on
    blindplay_shape.write_atomic(
        blindplay_shape.lane_state_dir() / "embark-20261008-010000.json",
        json.dumps({"stamp": "20261008-010000", "instance": "lane3"}))
    assert blindplay_shape.count_action() == 1        # a newer embark
    assert blindplay_shape.budget_spent() == (1, 1500)
    assert blindplay_shape.count_action() == 2


def test_embark_zeroes_the_count_for_its_own_stamp(lanes):
    blindplay_shape.set_budget(1500, "3", run="20261008-010000")
    blob = json.loads(blindplay_shape.budget_path().read_text(encoding="utf-8"))
    assert blob == {"cap": 1500, "count": 0, "run": "20261008-010000"}


# ---- 2. the build's own numbers first --------------------------------------

def _klee_board(growth=2, opening=3):
    state = json.loads(json.dumps(combat_state()))
    state["player"]["character"] = "Klee"
    state["player"]["resources"]["KLEEMOD_SPARK"] = 0
    state["run"] = {"act": 1, "floor": 2, "ascension": 0,
                    "klee_law": {"bomb_growth": growth,
                                 "opening_spark": opening}}
    return state


def test_the_page_quotes_the_builds_opening_spark():
    page = blindplay.observe(_klee_board(opening=3))
    assert "you start each combat with 3," in page
    state = _klee_board()
    del state["run"]["klee_law"]
    assert (f"you start each combat with {blindplay_shape.OPENING_SPARK},"
            in blindplay.observe(state))


def test_the_live_law_reads_and_falls_back():
    obs = blindplay.observation(_klee_board(growth=2, opening=3))
    assert obs["klee_law"] == {"bomb_growth": 2, "opening_spark": 3}
    assert blindplay_shape.bomb_growth(obs) == 2
    assert blindplay_shape.opening_spark(obs) == 3
    assert blindplay_shape.bomb_growth({}) == blindplay_shape.BOMB_GROWTH
    assert blindplay_shape.live_klee_law({"run": {"klee_law": "x"}}) == {}
    assert "Grows 2 at the start" in \
        blindplay_notes.glossary_definition("Bomb", 2)[1]


def test_the_bridge_reads_constants_the_mod_declares():
    cs = (REPO / "vendor" / "STS2_MCP" / "gits" / "GitsKleeLaw.cs"
          ).read_text(encoding="utf-8")
    law = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "KleeOverhaul.cs").read_text(encoding="utf-8")
    assert '"KleeMod.Powers.KleeOverhaulLaw"' in cs
    assert "namespace KleeMod.Powers;" in law
    for field, key in (("BombGrowth", "bomb_growth"),
                       ("OpeningSpark", "opening_spark")):
        assert f'"{field}"' in cs and f'["{key}"]' in cs
        assert f"public const int {field} =" in law
    builder = (REPO / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs"
               ).read_text(encoding="utf-8")
    assert 'runInfo["klee_law"] = kleeLaw;' in builder


def test_the_skew_warning():
    assert blindplay_record.build_skew("0.2.4516+next", "main")
    assert blindplay_record.build_skew("0.2.4516", "klee-next")
    assert not blindplay_record.build_skew("0.2.4516+next", "klee-next")
    assert not blindplay_record.build_skew("0.2.4516+proto", "main")
    assert not blindplay_record.build_skew("", "main")


# ---- 5. the fight is over --------------------------------------------------

def _live_args(command):
    return argparse.Namespace(raw_file="", dry_run=False, brief=True,
                              command=command)


def test_a_play_after_the_fight_ended_prints_the_next_page(
        lanes, monkeypatch, capsys):
    blindplay.forget_run()
    blindplay.screen_page(combat_state())        # the lane's last page
    monkeypatch.setattr(blindplay, "_lane_guard", lambda args: "")
    monkeypatch.setattr(blindplay, "_live_load",
                        lambda args, **kw: map_state())
    assert blindplay.cmd_act(_live_args('play "Strike"')) == 1
    out = capsys.readouterr().out
    assert out.startswith("The fight is over: nothing was sent.")
    assert "REFUSED" not in out
    assert "## What you can say" in out
    # On a screen that was not a fight, the refusal stays a refusal.
    blindplay.forget_run()
    blindplay.screen_page(map_state())
    assert blindplay.cmd_act(_live_args('play "Strike"')) == 1
    assert capsys.readouterr().out.startswith("REFUSED: you are not in a")
    blindplay.forget_run()


def test_room_closed_names_the_shop_too():
    assert blindplay.room_closed("you are not in a shop", "shop") \
        .startswith("The shop is closed")
    assert blindplay.room_closed("you are not in a battle", "map") == ""
    assert blindplay.room_closed("you are not in a battle. Say: x", "elite") \
        .startswith("The fight is over")


# ---- 8. the brief page's relic and price trims -----------------------------

PAGE = "\n".join([
    "# Battle — round 2", "", "- HP 40/68", "- Block 0", "- Energy 3/3", "",
    "## Your relics", "",
    "- **Pendulum** (1 of 3) — Every 3 turns, draw 1 card.",
    "- **Akabeko** — At the start of each combat, gain 8 Vigor.", "",
    "## Your hand", "",
    "- **Blast Shield** — cost 1 Spark, skill",
    "    Gain 4 Block. Return this card to your hand.",
    "    Its 1 Spark is a price, not an Energy cost: an effect that makes a "
    "card free to play, or cuts its cost to 0, covers Energy only, and the 1 "
    "Spark is still spent.",
    "- **Sparkling Burst** — cost 2 Sparks, skill",
    "    Its 2 Sparks is a price, not an Energy cost: an effect that makes a "
    "card free to play, or cuts its cost to 0, covers Energy only, and the 2 "
    "Sparks is still spent.", "",
    "## What you can say", "", "- `end turn`", ""])


def test_relics_print_whole_on_a_fights_first_page_then_name_and_counter():
    seen: set[str] = set()
    first = blindplay_brief.brief(PAGE, seen, relics_full=True)
    assert "Every 3 turns, draw 1 card." in first
    later = blindplay_brief.brief(PAGE, seen, relics_full=False)
    assert "- **Pendulum** (1 of 3)\n" in later
    assert "- **Akabeko**\n" in later
    assert "Vigor" not in later
    # A relic new to the lane prints whole even off the fight's first page.
    fresh = PAGE.replace("Akabeko", "Anchor")
    assert "Anchor** — At the start" in blindplay_brief.brief(
        fresh, seen, relics_full=False)


def test_the_spark_price_sentence_prints_once_per_lane():
    seen: set[str] = set()
    first = blindplay_brief.brief(PAGE, seen)
    assert first.count("is a price, not an Energy cost") == 1
    assert "is a price" not in blindplay_brief.brief(PAGE, seen)
    # Without a lane memory nothing is remembered, so it stays.
    assert blindplay_brief.brief(PAGE, None).count("is a price") == 2


def test_a_second_page_of_a_fight_is_brief_on_relics(lanes, capsys):
    blindplay.forget_fight()
    blindplay.screen_page(combat_state())
    assert blindplay._FIGHT_OPENING[0] is True
    blindplay.screen_page(combat_state())
    assert blindplay._FIGHT_OPENING[0] is False
    blindplay.forget_fight()


# ---- 3. the seat's lane scripts and its UTF-8 brief ------------------------

def _seat():
    spec = importlib.util.spec_from_file_location(
        "seat_tool_1008", REPO / "tools" / "seat.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_lane_scripts_carry_lane_interpreter_brief_and_root():
    scripts = _seat().lane_scripts(4)
    py = '"' + PurePath(sys.executable).as_posix() + '"'
    for name, verb in (("o", "observe"), ("a", "act")):
        text = scripts[name]
        assert f'cd "{PurePath(REPO).as_posix()}"' in text
        assert "GITS_LANE=4" in text
        assert f"{py} -m understudy.blindplay {verb} --brief" in text
        assert "\r" not in text and "\\" not in text


def test_opus_brief_with_scratch_writes_scripts_and_a_utf8_lf_brief(
        tmp_path):
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "seat.py"), "--opus-brief",
         "--lane", "2", "--character", "KLEEMOD-KLEE", "--scratch",
         str(tmp_path)], capture_output=True, cwd=str(REPO),
        env={k: v for k, v in os.environ.items()
             if k != "PYTHONIOENCODING"})
    assert res.returncode == 0, res.stderr
    assert b"\r\n" not in res.stdout
    text = res.stdout.decode("utf-8")
    folder = (tmp_path / "seat-lane2").as_posix()
    assert f"`bash {folder}/o`" in text
    assert f'`bash {folder}/a "<command>"`' in text
    assert "—" in text                       # an em dash, as UTF-8
    for name in ("o", "a"):
        assert (tmp_path / "seat-lane2" / name).is_file()
    brief = (tmp_path / "brief-lane2.md").read_bytes()
    assert b"\r\n" not in brief
    assert brief.decode("utf-8").startswith("You are the blind seat")


# ---- 4. the brief's text ----------------------------------------------------

def test_the_seat_brief_says_the_lanes_cap_and_asks_for_notes():
    text = (REPO / "docs" / "current" / "operations" / "seat-brief.md"
            ).read_text(encoding="utf-8")
    assert "the lane's cap, printed on every page" in text
    assert "120 accepted" not in text
    assert "Opus tester" not in text and "blind seat" in text.splitlines()[0]
    assert "After each fight, append one line to your notes file" in text


def test_observe_prints_the_lanes_cap(lanes, capsys):
    blindplay_shape.set_budget(1500)
    blindplay_shape.count_action()
    args = argparse.Namespace(
        raw_file=str(REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                     / "observed.json"), dry_run=False, brief=True,
        define="")
    assert blindplay.cmd_observe(args) == 0
    assert "actions: 1 of 1500 on this lane" in capsys.readouterr().out


def test_build_version_falls_back_to_the_machines_local_props(
        lanes, monkeypatch, tmp_path):
    """Every worktree's MSBuild reads `%LOCALAPPDATA%/gits/local.props`;
    the record reads it too where the checkout has none of its own."""
    absent = tmp_path / "checkout" / "local.props"
    monkeypatch.setattr(blindplay, "LOCAL_PROPS", absent)
    monkeypatch.setattr(blindplay_record, "_DEFAULT_PROPS", absent)
    game = tmp_path / "game"
    (game / "mods" / "klee").mkdir(parents=True)
    (game / "mods" / "klee" / "manifest.json").write_text(
        json.dumps({"version": "0.2.9+next"}), encoding="utf-8")
    (tmp_path / "gits").mkdir()
    (tmp_path / "gits" / "local.props").write_text(
        f"<Project><PropertyGroup><GameDir>{game}</GameDir>"
        f"</PropertyGroup></Project>", encoding="utf-8")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert blindplay_record.build_version()[0] == "0.2.9+next"
