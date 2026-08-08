"""P1.5 -- the three new wire surfaces, pinned.

Understudy P1.5 (R104) added one endpoint, one state key and one fight-record
field. Each is a contract somebody else now codes against, so each is pinned
here rather than left to be rediscovered:

    item 1  CHOSEN SEEDS       `bridge.set_seed` / `clear_seed`, and the
                               read-back check that makes a chosen seed a
                               VERIFIED seed rather than a requested one
    item 2  RESOURCE VISIBILITY `player.resources` -> the encore column, which
                               read UNSEEN (-1) on every bot fight before this
    item 3  SELECTOR RECORDING `fight.selectors`, and the offered list that
                               makes a recorded answer reconstructible

`understudy/trace_replay.py` is imported as `replay` throughout this file for
brevity. It is NOT `understudy/replay.py`, which is S7's sim-fidelity replay
and a different instrument that happened to land on main under the name P1.5's
spec had asked for; the module docstring records the collision.

WHAT THIS FILE CANNOT TEST, STATED SO NOBODY READS MORE INTO A GREEN BAR
Whether the GAME honours a chosen seed. That is a live-game measurement, it
was made, and it is written up in the sprint log with its seed and its
read-back. These tests pin the plumbing on this side of the socket: the shape
of the request, the reading of the reply, and the refusal to continue when the
reply disagrees with the request.
"""

from __future__ import annotations

import json

import pytest

from understudy import bridge, soak
from understudy import trace_replay as replay


# ------------------------------------------------------- item 2: meters ----

def _state(resources=None, status=None):
    player = {"hp": 40, "max_hp": 60, "status": status or []}
    if resources is not None:
        player["resources"] = resources
    return {"state_type": "monster", "player": player,
            "battle": {"round": 1}}


def test_encore_is_unseen_without_a_resources_key():
    """A pre-P1.5 bridge carries no `resources`, and its logs must keep saying
    UNSEEN. Reading 0 there would claim the meter was empty in fights where it
    demonstrably was not -- the exact error the -1 convention exists to
    prevent."""
    assert soak._meters(_state())[3] == soak.METER_UNSEEN == -1


def test_encore_is_read_from_the_resource_map():
    meters = soak._meters(_state(resources={"KLEEMOD_ENCORE": 7}))
    assert meters[3] == 7


def test_a_resource_map_without_encore_reads_zero_not_unseen():
    """`resources` present and Encore absent is a player who has no Encore --
    a fact, not a blind spot. Only the ABSENCE of the map is unseen."""
    assert soak._meters(_state(resources={"SOMEONE_ELSES": 3}))[3] == 0


def test_fanfare_prefers_the_resource_over_the_badge():
    """The badge is SYNCED from the resource at known hook sites, so between
    two sync moments the badge is the stale one. The canonical value wins."""
    state = _state(resources={"KLEEMOD_FANFARE": 12},
                   status=[{"id": "FANFARE_METER_POWER", "amount": 9}])
    assert soak._meters(state)[0] == 12


def test_fanfare_still_falls_back_to_the_badge():
    state = _state(status=[{"id": "FANFARE_METER_POWER", "amount": 9}])
    assert soak._meters(state)[0] == 9


def test_the_salon_cap_follows_casting_call():
    """`SalonCapUpPower` is an ordinary PowerModel and has been in the status
    strip all along; the cap column used to record the printed base and ignore
    it. Printed 3 + a raise of 2 is a live cap of 5."""
    state = _state(status=[{"id": "SALON_CAP_UP_POWER", "amount": 2}])
    assert soak._meters(state)[2] == soak.SALON_PRINTED_CAP + 2


def test_the_salon_cap_is_the_printed_base_without_a_raise():
    assert soak._meters(_state())[2] == soak.SALON_PRINTED_CAP == 3


# ---------------------------------------------------- item 3: selectors ----

class _StubSession:
    def note_seed_channel(self):
        pass


def _driver():
    d = object.__new__(soak.RunDriver)
    d.fight = soak.FightTelemetry(act=1, floor=3, kind="monster")
    d.fight.turns = 4
    return d


def test_a_selector_row_carries_the_offers_it_was_chosen_from():
    """The denominator rule. "Center Stage" means one thing against
    [Center Stage, Guest Cast] and nothing at all against a list that did not
    contain Guest Cast -- so the offers travel with the answer, exactly as
    `hand` travels with a card play."""
    d = _driver()
    before = {"state_type": "card_select",
              "card_select": {"screen_type": "choose",
                              "cards": [{"name": "Center Stage"},
                                        {"name": "Guest Cast"}]}}
    row = d._selector_row(before, {"action": "select_card", "index": 1},
                          {"card_name": "Guest Cast", "screen_type": "choose"})
    assert row == [4, "choose", 1, "Guest Cast",
                   ["Center Stage", "Guest Cast"]]


def test_the_screen_type_is_one_spelling_per_screen():
    """Measured live: the same screen reached by two verbs wrote
    `NCombatPileCardSelectScreen` on one row and the lowercased form on the
    next, because `naming.describe` lowercases and the blob fallback did not.
    Two spellings of one screen, in the channel whose whole job is to be
    compared."""
    d = _driver()
    blob = {"screen_type": "NCombatPileCardSelectScreen", "cards": []}
    named = d._selector_row({"state_type": "card_select", "card_select": blob},
                            {"action": "select_card", "index": 0},
                            {"screen_type": "ncombatpilecardselectscreen"})
    bare = d._selector_row({"state_type": "card_select", "card_select": blob},
                           {"action": "select_card"}, {})
    assert named[1] == bare[1] == "ncombatpilecardselectscreen"


def test_a_selector_row_survives_a_screen_with_no_index():
    """A confirm or a skip resolves a selector without naming an option. It is
    still a selector answer and it is still recorded; -1 says which kind."""
    d = _driver()
    row = d._selector_row({"state_type": "hand_select", "hand_select": {}},
                          {"action": "combat_select_card"}, {})
    assert row[2] == -1 and row[3] == "" and row[4] == []


def test_selectors_are_in_the_fight_record():
    f = soak.FightTelemetry(act=1, floor=1, kind="monster")
    f.selectors.append([1, "choose", 0, "Center Stage",
                        ["Center Stage", "Guest Cast"]])
    rec = f.as_record()
    assert rec["selectors"] == [[1, "choose", 0, "Center Stage",
                                 ["Center Stage", "Guest Cast"]]]


def test_the_selector_screen_set_excludes_overlay():
    """`overlay` is the shape a soft-lock takes. A screen nobody can answer
    has no choice to record, and recording one would put a phantom answer in
    a trace that a replay would then have to explain."""
    assert "overlay" in soak.MID_FIGHT
    assert "overlay" not in soak.SELECTOR_SCREENS
    assert set(soak.SELECTOR_SCREENS) < set(soak.MID_FIGHT)


# --------------------------------------------------------- item 1: seeds ----

def test_set_seed_posts_the_seed_to_the_gits_endpoint(monkeypatch):
    seen = {}

    def fake(url, payload=None, timeout=20.0):
        seen["url"], seen["payload"] = url, payload
        return {"status": "ok", "route": "lobby"}

    monkeypatch.setattr(bridge, "_request", fake)
    assert bridge.set_seed("ssrweglnrg")["route"] == "lobby"
    assert seen["url"] == bridge.SEED
    assert seen["payload"] == {"seed": "ssrweglnrg"}


def test_clear_seed_sends_an_explicit_null(monkeypatch):
    """Not an empty string and not an omission: the endpoint distinguishes
    "clear it" from "you forgot the field", and a teardown that sent the
    second would leave a global, sticky override behind."""
    seen = {}
    monkeypatch.setattr(bridge, "_request",
                        lambda url, payload=None, timeout=20.0:
                        seen.update(payload=payload) or {"status": "ok"})
    bridge.clear_seed()
    assert seen["payload"] == {"seed": None}
    assert json.dumps(seen["payload"]) == '{"seed": null}'


def test_seed_not_honoured_is_a_harness_side_defect():
    """The game rolling its own seed is the game behaving normally. What
    failed is this harness's claim to have chosen one -- so two of them halt
    the soak rather than filling a night with runs that are not the runs they
    say they are."""
    assert "seed_not_honoured" in soak._HARNESS_SIDE


def test_the_seed_is_set_after_the_character_and_before_the_confirm(monkeypatch):
    """THE MOMENT IS THE WHOLE TRICK, and it is the game's constraint, not a
    style choice. `NCharacterSelectScreen.AfterInitialized()` sets
    `NGame.DebugSeedOverride = null` as the screen opens, so a seed set before
    character select is wiped by the screen it was chosen for; and the run is
    generated inside the confirm, so there is no "after"."""
    from tier0.tests import test_understudy_soak as ts

    fake = ts._FakeBridge()
    calls: list[str] = []
    fake.set_seed = lambda seed: (calls.append(f"set_seed:{seed}")
                                  or {"status": "ok", "route": "lobby",
                                      "chosen": seed})
    real_post = fake.post
    fake.post = lambda action, **p: (
        calls.append(f"post:{str(p.get('option', action)).lower()}")
        or real_post(action, **p))

    monkeypatch.setattr(soak, "bridge", fake)
    monkeypatch.setattr(soak, "SETTLE_S", 0)
    d = ts._driver()
    d.chosen_seed = "SSRWEGLNRG"
    d.session = _StubSession()
    d._embark(fake.get_state())

    assert "set_seed:SSRWEGLNRG" in calls
    assert calls.index("set_seed:SSRWEGLNRG") < calls.index("post:confirm")
    assert calls.index("post:kleemod-furina") < calls.index("set_seed:SSRWEGLNRG")


def test_the_canonical_seed_is_taken_from_the_game_not_recomputed(monkeypatch):
    """`SeedHelper.CanonicalizeSeed` upper-cases and maps 'O'->'0', 'I'->'1'.
    The run reads back the CANONICAL string, so a harness comparing against
    what a person typed would file `seed_not_honoured` against a seed the game
    honoured exactly. The mapping is asked for, never retyped."""
    from tier0.tests import test_understudy_soak as ts

    fake = ts._FakeBridge()
    fake.set_seed = lambda seed: {"status": "ok", "route": "lobby",
                                  "chosen": "P15BR1DGE1"}
    monkeypatch.setattr(soak, "bridge", fake)
    monkeypatch.setattr(soak, "SETTLE_S", 0)
    d = ts._driver()
    d.chosen_seed = "p15bridge1"
    d.session = _StubSession()
    d._embark(fake.get_state())
    assert d.chosen_seed == "P15BR1DGE1"


def test_the_read_back_arm_sets_no_seed_at_all(monkeypatch):
    """The default is unchanged and stays unchanged: R95's arm asks the
    endpoint for nothing."""
    from tier0.tests import test_understudy_soak as ts

    fake = ts._FakeBridge()
    called = []
    fake.set_seed = lambda seed: called.append(seed)
    monkeypatch.setattr(soak, "bridge", fake)
    monkeypatch.setattr(soak, "SETTLE_S", 0)
    d = ts._driver()
    d._embark(fake.get_state())
    assert called == []


def test_the_endpoint_is_the_forked_bridges_and_not_upstreams(tmp_path):
    """Upstream's own `menu_select(seed=...)` refuses singleplayer on a
    `charSelect.Lobby == null` guard that the decompile contradicts. P1.5 does
    not fight that arm; it adds its own route. If this ever points back at
    /api/v1/singleplayer, the refusal is back."""
    assert bridge.SEED.endswith("/api/v1/gits/seed")


# ------------------------------------------------------------- replay ------

def _fight_record(**over):
    f = soak.FightTelemetry(act=1, floor=2, kind="monster")
    f.cards_played = [[1, "Stage Presence"]]
    f.selectors = [[1, "choose", 0, "Center Stage",
                    ["Center Stage", "Guest Cast"]]]
    f.meters_by_turn = [[1, 4, 1, 3, 6]]
    rec = f.as_record()
    rec.update(over)
    return rec


def test_replay_reads_the_new_fields_into_a_trace():
    t = replay.trace(_fight_record())
    assert t["selectors"][0][3] == "Center Stage"
    assert t["meters_by_turn"][0][4] == 6
    assert set(t) == set(replay.TRACE_KEYS)


def test_replay_tolerates_a_pre_p15_record():
    """A record written before P1.5 has no `selectors`. The honest reading is
    "this run recorded no selector answers", not a crash -- and, since
    `EB-59`, not `[]` either: `[]` is what a recorder that HAD the column and
    saw nothing in it writes, and the two must not compare equal."""
    rec = _fight_record()
    del rec["selectors"]
    assert replay.trace(rec)["selectors"] is replay.NOT_RECORDED


def test_replay_reconstructs_the_offer_list_not_just_the_answer():
    lines = replay.selector_lines(_fight_record())
    assert len(lines) == 1
    assert "*Center Stage*" in lines[0] and "Guest Cast" in lines[0]


def test_replay_compares_traces_and_not_outcomes(monkeypatch):
    """`hp_trajectory` and the damage totals are the OUTPUT a comparison
    measures. Folding them into the trace identity would make every
    interesting result an inequality of the thing being compared with
    itself."""
    a = _fight_record(hp_trajectory=[[1, 40, 0]], damage_taken=3)
    b = _fight_record(hp_trajectory=[[1, 31, 0]], damage_taken=12)
    assert replay.trace(a) == replay.trace(b)


def test_replay_calls_two_identical_recordings_identical(monkeypatch):
    log = [{"record": "seed_read_back", "seed": "ABC", "chosen": "ABC",
            "honoured": True}, _fight_record()]
    monkeypatch.setattr(replay, "read_run_log", lambda stamp, i: log)
    assert replay.compare_runs(("a", 1), ("b", 1)) == []


def test_replay_reports_a_selector_divergence(monkeypatch):
    seed = {"record": "seed_read_back", "seed": "ABC", "chosen": "ABC",
            "honoured": True}
    other = _fight_record()
    other["selectors"] = [[1, "choose", 1, "Guest Cast",
                           ["Center Stage", "Guest Cast"]]]
    logs = {"a": [seed, _fight_record()], "b": [seed, other]}
    monkeypatch.setattr(replay, "read_run_log", lambda stamp, i: logs[stamp])
    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert len(findings) == 1 and "selectors diverges" in findings[0]


def test_replay_refuses_to_compare_two_different_seeds(monkeypatch):
    """Two runs on different seeds are two different runs. Reporting a
    per-field diff between them would dress an incomparable pair as a
    measurement."""
    logs = {"a": [{"record": "seed_read_back", "seed": "ABC"},
                  _fight_record()],
            "b": [{"record": "seed_read_back", "seed": "XYZ"},
                  _fight_record()]}
    monkeypatch.setattr(replay, "read_run_log", lambda stamp, i: logs[stamp])
    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert len(findings) == 1 and findings[0].startswith("SEED:")


# ------------------------------------------------- the fork, on disk -------

REPO_VENDOR = None


def test_the_fork_is_recorded_as_a_fork_not_smuggled():
    """`tools/lint_vendor_pin.py` enforces the marker/manifest discipline; this
    asserts the P1.5 files exist and carry their side of it, so a future
    session that deletes the marker fails here as well as there."""
    from pathlib import Path
    vendor = Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
    for name in ("gits/GitsSeed.cs", "gits/GitsResources.cs"):
        text = (vendor / name).read_text(encoding="utf-8")
        assert "GItS LOCAL ADDITION" in text, name
    state_builder = (vendor / "McpMod.StateBuilder.cs").read_text(
        encoding="utf-8")
    assert "GItS LOCAL EDIT" in state_builder
    assert 'state["resources"] = GitsResourceSnapshot(combatState);' in \
        state_builder
    assert '"/api/v1/gits/seed"' in \
        (vendor / "McpMod.cs").read_text(encoding="utf-8")


@pytest.mark.parametrize("key", ["selectors"])
def test_the_new_fight_key_is_an_addition_and_not_a_rename(key):
    """Adding a key to the shared schema is free; renaming one is a
    cross-session change. This asserts P1.5 did the free thing -- every P1 key
    is still there."""
    rec = soak.FightTelemetry(act=1, floor=1, kind="monster").as_record()
    assert key in rec
    for old in ("cards_played", "meters_by_turn", "hp_trajectory",
                "enemy_pool_by_turn", "intent", "feed", "source", "schema"):
        assert old in rec
    assert rec["schema"] == "1"      # ADDITIONS do not bump the schema
