"""Seat page and seat tooling fixes, 2026-10-04 (BACKLOG lines).

Display truth and tooling only: no card number moves. Each test names the
line it closes. Pages are built from the recorded combat state and the map
fixture the blind-play suite already reads.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

import copy
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

from understudy import blindplay, blindplay_shape
from understudy.blindplay_render import _relic_counter

from tier0.tests.test_understudy_blindplay import combat_state, map_state

REPO = Path(__file__).resolve().parents[2]
CODE = REPO / "klee-mod" / "KleeCode"


def _seat():
    spec = importlib.util.spec_from_file_location(
        "seat_tool", REPO / "tools" / "seat.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_seat(*args):
    return subprocess.run(
        [sys.executable, str(REPO / "tools" / "seat.py"), *args],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO),
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})


# ---- 1. The Opus seat's embark carries an explicit cap ----------------------

def test_the_opus_brief_prints_the_embark_with_a_cap_of_120():
    res = _run_seat("--opus-brief", "--lane", "2",
                    "--character", "KLEEMOD-KLEE")
    assert res.returncode == 0, res.stderr
    assert ("-m understudy.embark --character KLEEMOD-KLEE --lane 2 "
            "--max-actions 120") in res.stderr
    # The embark is the coordinator's: stdout is the brief and nothing else.
    assert "understudy.embark" not in res.stdout
    assert res.stdout.startswith("You are the blind seat for")


def test_the_cap_is_a_parameter():
    res = _run_seat("--opus-brief", "--lane", "3", "--max-actions", "1500")
    assert "--lane 3 --max-actions 1500" in res.stderr
    coop = _run_seat("--opus-brief", "--lane", "3", "--coop",
                     "--max-actions", "1500")
    assert "--coop --lanes" in coop.stderr
    assert "--max-actions 1500" in coop.stderr


def test_a_backend_seat_keeps_its_session_cap():
    res = _run_seat("--lane", "1", "--dry-run")
    assert "--max-actions 60" in res.stdout


# ---- 6. Each seat its own notes path ----------------------------------------

def test_the_brief_names_a_per_lane_notes_path_under_scratch(tmp_path):
    seat = _seat()
    plain = seat.brief_text(2, "KLEEMOD-KLEE")
    filled = seat.brief_text(2, "KLEEMOD-KLEE", scratch=str(tmp_path))
    notes = (tmp_path / "seat-lane2" / "notes.md").as_posix()
    head, _, body = filled.partition("\n")
    assert f"`{notes}`" in head
    assert "seat-lane2" not in plain
    # The instrument text is untouched: only the lane line gained the path.
    assert body == plain.partition("\n")[2]


def test_the_coordinator_is_warned_of_an_earlier_seats_notes(tmp_path):
    (tmp_path / "seat-lane2").mkdir()
    (tmp_path / "seat-lane2" / "notes.md").write_text("old", encoding="utf-8")
    res = _run_seat("--opus-brief", "--lane", "2", "--scratch", str(tmp_path))
    assert "already exists" in res.stderr


# ---- 2. The run seed and the ascension --------------------------------------

def _map_here():
    here = json.loads(json.dumps(map_state()))
    here["run"] = {"act": 1, "floor": 3, "ascension": 4}
    return here


def test_the_map_prints_the_ascension_off_the_wire_and_the_seed_off_the_sidecar(
        tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_SIDECAR_DIR", tmp_path)
    monkeypatch.setenv("GITS_LANE", "2")
    (tmp_path / "embark-20261004-100000.json").write_text(json.dumps(
        {"instance": "lane2", "run_seed": "OLDSEED"}), encoding="utf-8")
    (tmp_path / "embark-20261004-110000.json").write_text(json.dumps(
        {"instance": "lane2", "run_seed": "CWL9L0LLL3CH"}), encoding="utf-8")
    (tmp_path / "embark-20261004-120000.json").write_text(json.dumps(
        {"instance": "lane1", "run_seed": "OTHERLANE"}), encoding="utf-8")
    page = blindplay.observe(_map_here())
    assert "Run seed CWL9L0LLL3CH, ascension 4." in page
    assert page.count("Run seed") == 1


def test_no_sidecar_says_the_seed_is_not_known():
    page = blindplay.observe(_map_here())
    assert "Run seed not known to this page, ascension 4." in page


# ---- 3. A relic counter with its threshold ----------------------------------

def test_tuning_fork_prints_of_10():
    fork = {"name": "Tuning Fork", "counter": "7",
            "text": "Every time you play 10 Skills, gain 7 Block."}
    assert _relic_counter(fork) == "7 of 10"
    # The table answers where the sentence does not carry the number.
    assert _relic_counter({**fork, "text": ""}) == "7 of 10"
    # A counter that counts toward nothing is printed as it was.
    assert _relic_counter({"name": "Casket", "counter": "3",
                           "text": "Counts the Plans carried out."}) == "3"

    state = copy.deepcopy(combat_state())
    state["player"]["relics"] = [{"name": "Tuning Fork", "id": "TUNING_FORK",
                                  "counter": 7,
                                  "description": fork["text"]}]
    page = blindplay.observe(state)
    assert "**Tuning Fork** (7 of 10)" in page


# ---- 4. A placed Bomb prints its size ---------------------------------------

def _row(hits=(), applied=()):
    return {"card_id": "x", "card": "Bang Bang!", "auto_played": False,
            "carried": False, "overflowed": False,
            "hits": list(hits), "applied": list(applied)}


def test_the_play_log_prints_the_placed_size():
    state = copy.deepcopy(combat_state())
    enemy = state["battle"]["enemies"][0]["name"]
    state["player"]["resolutions"] = [_row(applied=[
        {"target": enemy, "power": "Bomb", "amount": 11, "combat_id": "1"},
        {"target": enemy, "power": "Mine", "amount": 3, "combat_id": "1"}])]
    page = blindplay.observe(state)
    assert f"Put **Bomb 11** on **{enemy}**." in page
    assert f"Put **Mine 3** on **{enemy}**." in page


def test_the_placement_sizes_its_ledger_entry():
    src = (CODE / "Powers" / "Prototype" / "ProtoBombPower.cs").read_text(
        encoding="utf-8")
    body = src[src.index("public static async Task Place("):
               src.index("public static async Task PlaceOnAll(")]
    assert body.index("ResolutionLedger.MarkApplied()") \
        < body.index("PowerCmd.Apply<ProtoBombPower>") \
        < body.index("ResolutionLedger.SizeAppliedSince(")


# ---- 5. A Thorns hit names its source ---------------------------------------

def _on_you(source=""):
    hit = {"target": "Klee", "amount": 3, "blocked": 0, "combat_id": "0",
           "on_player": True}
    if source:
        hit["source"] = source
    return hit


def test_a_hit_on_you_names_the_thorns_that_dealt_it():
    state = copy.deepcopy(combat_state())
    enemy = state["battle"]["enemies"][0]
    enemy["status"] = [{"id": "THORNS_POWER", "name": "Thorns", "amount": 3,
                        "type": "Buff",
                        "description": "Whenever this is attacked, deal 3 "
                                       "damage back."}]
    state["player"]["resolutions"] = [_row(hits=[_on_you(enemy["name"])])]
    page = blindplay.observe(state)
    assert (f"1. **Klee** (you) -- 3, taken while it resolved, from "
            f"**{enemy['name']}**'s Thorns") in page
    assert "a reaction never hits you" not in page

    # An older mod sends no dealer: the one Thorns holder on the board.
    state["player"]["resolutions"] = [_row(hits=[_on_you()])]
    page = blindplay.observe(state)
    assert f"from **{enemy['name']}**'s Thorns" in page


def test_a_dealer_without_thorns_is_named_plainly():
    state = copy.deepcopy(combat_state())
    state["player"]["resolutions"] = [_row(hits=[_on_you("Spiker")])]
    page = blindplay.observe(state)
    assert "taken while it resolved, from **Spiker**" in page
    assert "Spiker**'s Thorns" not in page


def test_the_ledger_carries_the_dealer():
    src = (CODE / "Powers" / "ResolutionLedger.cs").read_text(encoding="utf-8")
    assert '["source"] = hit.Source' in src
    hook = (CODE / "Diagnostics" / "PlayTelemetry.cs").read_text(
        encoding="utf-8")
    assert "(int)result.BlockedDamage, dealer);" in hook


def test_your_own_hp_cost_is_never_a_thorns_guess():
    """The Furina pool-75 round (2026-10-09): Ousia Pledge's Drain 3, a
    Skill, read "from Toadpole(1)'s Thorns" (Thorns 2). The mod filed no
    dealer, and the page guessed the one Thorns holder. The mod now marks a
    hit with no dealer but you as `self`, and the page says it was your own
    HP cost."""
    state = copy.deepcopy(combat_state())
    enemy = state["battle"]["enemies"][0]
    enemy["status"] = [{"id": "THORNS_POWER", "name": "Thorns", "amount": 2,
                        "type": "Buff",
                        "description": "Whenever this is attacked, deal 2 "
                                       "damage back."}]
    hit = _on_you()
    hit["self"] = True
    state["player"]["resolutions"] = [_row(hits=[hit])]
    page = blindplay.observe(state)
    assert ("1. **Klee** (you) -- 3, taken while it resolved, your own HP "
            "cost") in page
    assert "'s Thorns" not in page

    src = (CODE / "Powers" / "ResolutionLedger.cs").read_text(encoding="utf-8")
    assert '["self"] = hit.Self' in src
    assert "dealer == null || ReferenceEquals(dealer, target)" in src
