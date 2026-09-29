"""Co-op seats: two blind seats, one co-op run, pinned offline.

The live half (the `--fastmp` transport, the lobby, both bridges serving one
run) was proven on lanes 2 and 3 on 2026-09-27 and is recorded in the PR that
built this. What is pinned here is this side of the socket:

  * `embark --coop` launches the host with `--fastmp host_standard`, waits for
    its lobby, launches the client with `--fastmp join`, picks each
    character, sets the ascension on the HOST ONLY, confirms client first,
    waits for both runs, reads the seed off the host's save and writes one
    sidecar per lane plus the co-op sidecar; `--teardown --coop` takes the
    client down first;
  * `bridge` follows the singleplayer route's 409 to the multiplayer route,
    and a singleplayer run is still one request to the singleplayer route;
  * the page's co-op half: the other player, the votes, WAITING, `wait`, the
    ally target, and the run's end;
  * nothing single-player changes.

The fixtures are the wire's own shapes, captured live on 2026-09-27
(`players[]`, `map.votes`, `battle.all_players_ready`) and cut down.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
from pathlib import Path

import pytest

from understudy import (blindplay, blindplay_coop, blindplay_shape, bridge,
                        embark, embark_coop, instances, lanewatch, soak)
from understudy import soak_session
from tier0.tests.test_understudy_blindplay import (combat_state, map_state,
                                                   rewards_state)

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh(monkeypatch):
    blindplay.forget_fight()
    blindplay.forget_run()
    bridge._coop_bases.clear()
    yield
    bridge._coop_bases.clear()
    blindplay.forget_fight()
    blindplay.forget_run()


# ------------------------------------------------------------- fixtures ----

KLEE = {"character": "Klee", "is_local": True, "hp": 62, "max_hp": 62,
        "gold": 99, "is_alive": True}
FURINA = {"character": "Furina", "is_local": False, "hp": 78, "max_hp": 78,
          "gold": 99, "is_alive": True}


def _coop(state: dict, players: list[dict]) -> dict:
    """A singleplayer-shaped state wearing the multiplayer route's keys."""
    s = copy.deepcopy(state)
    s.update({"game_mode": "multiplayer", "net_type": "Host",
              "player_count": len(players), "local_player_slot": 0,
              "players": copy.deepcopy(players)})
    return s


def coop_combat(me_ready=False, partner_ready=False, partner_pets=None,
                me_alive=True, partner_id="7") -> dict:
    me = dict(KLEE, block=0, is_ready_to_end_turn=me_ready,
              is_alive=me_alive)
    them = dict(FURINA, block=6, is_ready_to_end_turn=partner_ready)
    if partner_id is not None:
        them["entity_id"] = partner_id
    if partner_pets is not None:
        them["pets"] = partner_pets
    s = _coop(combat_state(), [me, them])
    s["battle"]["all_players_ready"] = me_ready and partner_ready
    return s


def coop_map(me_voted: bool, partner_voted: bool) -> dict:
    s = _coop(map_state(), [KLEE, FURINA])
    s["map"]["votes"] = [
        {"player": "Klee", "is_local": True, "voted": me_voted,
         "vote_col": 2 if me_voted else None,
         "vote_row": 4 if me_voted else None},
        {"player": "Furina", "is_local": False, "voted": partner_voted,
         "vote_col": 1 if partner_voted else None,
         "vote_row": 4 if partner_voted else None}]
    s["map"]["all_voted"] = me_voted and partner_voted
    return s


STAGE_PETS = [{"id": "GENTILHOMME_USHER", "entity_id": "9",
               "name": "Gentilhomme Usher", "alive": True, "hp": 3,
               "max_hp": 3, "block": 0, "status": [], "stage_member": 0,
               "stage_seat": 0}]


# ------------------------------------------------- single player unchanged --

def test_a_singleplayer_state_has_no_coop_block_and_no_coop_words():
    for state in (combat_state(), map_state(), rewards_state()):
        obs = blindplay.observation(state)
        assert "coop" not in obs
        page = blindplay.render(obs)
        assert "WAITING" not in page and "## The other player" not in page
        assert not any(c.startswith("wait") for c in obs["commands"])


def test_wait_is_refused_in_a_singleplayer_run_and_is_not_a_listed_verb():
    res = blindplay.act(combat_state(), "wait")
    assert not res["ok"]
    assert blindplay_coop.NO_PARTNER in res["refusal"]
    assert "wait" not in blindplay.VERBS
    bad = blindplay.act(combat_state(), "dance")
    assert "wait" not in bad["refusal"].split("are:")[-1]


def test_a_singleplayer_state_read_is_one_request_to_the_singleplayer_route(
        monkeypatch):
    calls = []

    def fake(url, payload=None, timeout=20.0):
        calls.append((url, payload))
        return {"state_type": "map"}

    monkeypatch.setattr(bridge, "_request", fake)
    assert bridge.get_state() == {"state_type": "map"}
    bridge.post("choose_map_node", index=1)
    assert calls == [(bridge.SINGLEPLAYER, None),
                     (bridge.SINGLEPLAYER, {"action": "choose_map_node",
                                            "index": 1})]
    assert not bridge.in_coop()


def test_a_session_launch_passes_no_arguments_unless_given(monkeypatch,
                                                          tmp_path):
    seen = []

    class _Proc:
        pid = 4242

        def poll(self):
            return None

    def popen(argv, **kw):
        seen.append(list(argv))
        return _Proc()

    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.setattr(soak_session, "await_dead_gap", lambda: 0.0)
    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    game = tmp_path / "game"
    game.mkdir()
    (game / soak_session.GAME_EXE).write_text("x", encoding="utf-8")
    inst = instances.Instance(game_dir=game, port=15529, appdata=tmp_path,
                              label="lane3")
    plain = soak.Session("s1", instance=inst)
    plain._launch()
    coop = soak.Session("s2", instance=inst,
                        extra_args=embark_coop.client_args(1000))
    coop._launch()
    exe = str(game / soak_session.GAME_EXE)
    assert seen == [[exe], [exe, "--fastmp", "join", "--clientId", "1000"]]
    assert "args" not in plain._launch_entry
    assert coop._launch_entry["args"] == ["--fastmp", "join", "--clientId",
                                          "1000"]


# ----------------------------------------------------------- the routing --

_MP_409 = {"error": "Multiplayer run is active. Use /api/v1/multiplayer "
                    "instead."}
_SP_409 = {"error": "Not in a multiplayer run. Use /api/v1/singleplayer "
                    "instead."}


def test_a_coop_run_is_found_by_the_409_and_remembered(monkeypatch):
    calls = []
    answers = {bridge.SINGLEPLAYER: _MP_409,
               bridge.MULTIPLAYER: {"state_type": "map",
                                    "game_mode": "multiplayer"}}

    def fake(url, payload=None, timeout=20.0):
        calls.append(url)
        return answers[url]

    monkeypatch.setattr(bridge, "_request", fake)
    assert bridge.get_state()["game_mode"] == "multiplayer"
    assert calls == [bridge.SINGLEPLAYER, bridge.MULTIPLAYER]
    assert bridge.in_coop()
    calls.clear()
    bridge.get_state()
    bridge.post("end_turn")
    assert calls == [bridge.MULTIPLAYER, bridge.MULTIPLAYER]


def test_a_refused_post_is_resent_to_the_multiplayer_route(monkeypatch):
    calls = []

    def fake(url, payload=None, timeout=20.0):
        calls.append((url, payload))
        return _MP_409 if url == bridge.SINGLEPLAYER else {
            "status": "ok", "message": "Submitted end turn (waiting for "
                                       "other players)"}

    monkeypatch.setattr(bridge, "_request", fake)
    got = bridge.post("end_turn")
    assert got["status"] == "ok"
    assert calls == [(bridge.SINGLEPLAYER, {"action": "end_turn"}),
                     (bridge.MULTIPLAYER, {"action": "end_turn"})]


def test_the_run_ending_sends_the_lane_back_to_the_singleplayer_route(
        monkeypatch):
    bridge._coop_bases.add(bridge.current_base())
    calls = []

    def fake(url, payload=None, timeout=20.0):
        calls.append(url)
        return _SP_409 if url == bridge.MULTIPLAYER else {
            "state_type": "menu"}

    monkeypatch.setattr(bridge, "_request", fake)
    assert bridge.get_state() == {"state_type": "menu"}
    assert calls == [bridge.MULTIPLAYER, bridge.SINGLEPLAYER]
    assert not bridge.in_coop()


def test_an_error_body_with_other_keys_is_not_a_redirect(monkeypatch):
    body = {"error": "Use /api/v1/multiplayer", "stack_trace": "x"}
    monkeypatch.setattr(bridge, "_request",
                        lambda url, payload=None, timeout=20.0: body)
    assert bridge.get_state() is body
    assert not bridge.in_coop()


def test_the_game_over_overlay_is_renamed_to_the_singleplayer_shape():
    state = {"state_type": "overlay", "game_mode": "multiplayer",
             "overlay": {"screen_type": "NGameOverScreen", "message": "x"},
             "run": {"floor": 7},
             "players": [dict(KLEE, hp=0, is_alive=False),
                         dict(FURINA, hp=0, is_alive=False)]}
    got = bridge.coop_state(state)
    assert got["state_type"] == "game_over"
    assert "overlay" not in got
    assert got["game_over"]["result"] == "defeat"
    alive = copy.deepcopy(state)
    alive["players"][1]["is_alive"] = True
    assert "result" not in bridge.coop_state(alive)["game_over"]
    other = {"state_type": "overlay", "overlay": {"screen_type": "NFoo"}}
    assert bridge.coop_state(other) is other


def test_the_run_ending_prints_clearly_and_ends_the_session(tmp_path):
    over = bridge.coop_state(
        {"state_type": "overlay", "game_mode": "multiplayer",
         "overlay": {"screen_type": "NGameOverScreen"}, "run": {"floor": 7},
         "players": [dict(KLEE, hp=0, is_alive=False),
                     dict(FURINA, hp=0, is_alive=False)]})
    page = blindplay.observe(over)
    assert page.startswith("TOOL-BLOCKED: game_over")
    assert "The run ended on floor 7. You LOST the run." in page
    assert "## The other player" in page and "down (0 HP)" in page
    thread = blindplay.ScriptedThread([])
    s = blindplay.Session(thread, wire=blindplay.ScriptedWire([over]),
                          session_id="t", log_root=tmp_path)
    assert s.run()["termination"] == "run_over"


# ------------------------------------------------------------- the page ----

def test_the_other_player_is_printed_with_their_turn_and_their_stage():
    page = blindplay.observe(coop_combat(partner_ready=True,
                                         partner_pets=STAGE_PETS))
    block = page.split("## The other player", 1)[1]
    assert "- **Furina**: HP 78/78, Block 6, has ended their turn" in block
    assert "  - Gentilhomme Usher (front): Fanfare 3" in block
    assert "WAITING" not in page


def test_after_end_turn_the_page_says_it_is_waiting_and_offers_wait():
    state = coop_combat(me_ready=True)
    obs = blindplay.observation(state)
    assert obs["coop"]["waiting"].startswith("You have ended your turn. "
                                             "Furina is still playing")
    assert obs["commands"][0] == blindplay_coop.WAIT_COMMAND
    assert not any(c.startswith(("play", "end turn"))
                   for c in obs["commands"])
    page = blindplay.render(obs)
    assert page.startswith("**WAITING.** You have ended your turn.")
    assert "still playing their turn" in page
    for command in ('play "Coral Guard"', "end turn"):
        res = blindplay.act(state, command)
        assert not res["ok"] and "Say `wait`" in res["refusal"]


def test_a_seat_that_is_down_waits_for_the_other():
    obs = blindplay.observation(coop_combat(me_alive=False))
    assert obs["coop"]["waiting"].startswith("You are down.")
    assert obs["commands"][0] == blindplay_coop.WAIT_COMMAND


def test_the_map_vote_prints_both_choices_and_waits_after_yours():
    obs = blindplay.observation(coop_map(me_voted=True, partner_voted=False))
    assert obs["coop"]["votes"] == ["You: Monster (path 2)",
                                    "Furina: not chosen yet"]
    assert "the party moves when both of you have chosen" \
        in obs["coop"]["waiting"]
    assert obs["commands"][0] == blindplay_coop.WAIT_COMMAND
    assert 'go "<node>"' in obs["commands"]
    page = blindplay.render(obs)
    assert "Choices so far:\n- You: Monster (path 2)\n- Furina: not chosen " \
           "yet" in page
    theirs = blindplay.observation(coop_map(me_voted=False,
                                            partner_voted=True))
    assert theirs["coop"]["votes"][1] == "Furina: Monster (path 1)"
    assert theirs["coop"]["waiting"] == ""


def test_a_shared_event_and_a_chest_report_their_votes():
    event = _coop({"state_type": "event",
                   "event": {"event_name": "A Fork", "is_shared": True,
                             "options": [{"index": 0, "title": "Left"},
                                         {"index": 1, "title": "Right"}],
                             "votes": [{"player": "Klee", "is_local": True,
                                        "voted": True, "vote_option": 1},
                                       {"player": "Furina",
                                        "is_local": False, "voted": False,
                                        "vote_option": None}],
                             "all_voted": False}}, [KLEE, FURINA])
    lines, mine, everyone = blindplay_coop.votes(event)
    assert lines == ["You: Right", "Furina: not chosen yet"]
    assert mine and not everyone
    chest = _coop({"state_type": "treasure",
                   "treasure": {"relics": [{"index": 0, "name": "Anchor"}],
                                "bids": [{"player": "Furina",
                                          "is_local": False, "voted": True,
                                          "vote_relic_index": 0}],
                                "all_bid": False}}, [KLEE, FURINA])
    assert blindplay_coop.votes(chest)[0] == ["Furina: Anchor"]


# -------------------------------------------------------- the ally target --

def _with_ally_card(state: dict) -> dict:
    state["player"]["hand"][3]["target_type"] = "AnyAlly"      # Coral Guard
    return state


def test_a_card_for_another_player_is_offered_and_aimed_at_them():
    state = _with_ally_card(coop_combat())
    obs = blindplay.observation(state)
    assert ('play "<card title>" on "Furina"   (a card that targets '
            'another player)') in obs["commands"]
    for command in ('play "Coral Guard" on "Furina"', 'play "Coral Guard"'):
        res = blindplay.act(state, command)
        assert res["ok"], res
        assert res["post"] == {"action": "play_card", "card_index": 3,
                               "target": "7"}
        assert res["printed"]["target"] == "Furina"


def test_an_ally_card_refuses_a_name_that_is_not_a_player():
    res = blindplay.act(_with_ally_card(coop_combat()),
                        'play "Coral Guard" on "Nibbit"')
    assert not res["ok"]
    assert "no other player here is called 'Nibbit'" in res["refusal"]
    assert "Furina" in res["refusal"]


def test_an_ally_card_on_a_bridge_without_the_handle_says_so():
    res = blindplay.act(_with_ally_card(coop_combat(partner_id=None)),
                        'play "Coral Guard"')
    assert not res["ok"]
    assert "did not say where Furina stands" in res["refusal"]


# ------------------------------------------------------------------ wait ----

def test_wait_parses_bounded():
    assert blindplay_coop.parse_wait("wait") == blindplay_coop.WAIT_DEFAULT_S
    assert blindplay_coop.parse_wait("wait 30s") == 30
    assert blindplay_coop.parse_wait("Wait 9999") == blindplay_coop.WAIT_MAX_S
    assert blindplay_coop.parse_wait("waiting") == -1
    res = blindplay.act(coop_combat(me_ready=True), "wait 20")
    assert res["ok"] and res["verb"] == "wait" and res["post"] is None
    assert res["printed"] == {"seconds": 20}


class _Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


class _Frames:
    def __init__(self, frames):
        self.frames = list(frames)

    def get_state(self):
        return self.frames.pop(0) if len(self.frames) > 1 else self.frames[0]


def test_wait_returns_when_the_other_player_acts():
    before = coop_combat(me_ready=True)
    same = copy.deepcopy(before)
    after = copy.deepcopy(before)
    after["battle"]["enemies"][0]["hp"] -= 6           # the partner's hit
    clock = _Clock()
    got, waited, moved = blindplay_coop.wait_for_partner(
        _Frames([same, same, after]), before, 60, clock=clock,
        sleep=clock.sleep)
    assert moved and got is after and waited == 3
    assert "the game moved" in blindplay_coop.wait_line(waited, moved, got)


def test_wait_gives_the_page_back_at_its_bound():
    before = coop_combat(me_ready=True)
    clock = _Clock()
    got, waited, moved = blindplay_coop.wait_for_partner(
        _Frames([copy.deepcopy(before)]), before, 5, clock=clock,
        sleep=clock.sleep)
    assert not moved and waited == 5
    assert "Furina has not acted yet" in blindplay_coop.wait_line(
        waited, moved, got)


def test_a_session_waits_without_spending_an_action_or_a_stall(tmp_path):
    """Three waits on a page that does not move: no action is charged and
    the stall stop (two identical pages here) never fires, because a WAITING
    page is the other seat's turn and not a screen this seat is stuck on."""
    waiting = coop_combat(me_ready=True)
    thread = blindplay.ScriptedThread(
        [{"command": "wait 1", "thinking": "their turn"}] * 3
        + [{"command": "dance", "thinking": "stop"}] * 3)
    s = blindplay.Session(thread, wire=blindplay.ScriptedWire([waiting]),
                          session_id="t", log_root=tmp_path,
                          budget=blindplay.Budget(max_stalls=2),
                          settle_delay_s=0.0)
    s.wait_poll_s = 0.05
    summary = s.run()
    assert summary["actions"] == 0
    assert summary["termination"] == "refusal_limit"
    rows = [json.loads(line) for line in (tmp_path / "t" / "transcript.jsonl")
            .read_text(encoding="utf-8").splitlines()]
    assert [r["moved"] for r in rows if r["kind"] == "wait"] == [False] * 3
    assert not any(r["kind"] == "stall" for r in rows)
    assert "Furina has not acted yet" in thread.sent[1]


def test_the_session_seed_of_a_coop_run_comes_off_the_lane_sidecar(
        monkeypatch):
    monkeypatch.setattr(bridge, "get_state", lambda: coop_combat())
    monkeypatch.setattr(bridge, "current_seed",
                        lambda: pytest.fail("the compendium is not asked"))
    monkeypatch.setattr(lanewatch, "sidecar_row",
                        lambda lane=None: {"run_seed": "P8SFJZPHDXGL"})
    assert blindplay._session_seed() == "P8SFJZPHDXGL"
    monkeypatch.setattr(bridge, "get_state", lambda: combat_state())
    monkeypatch.setattr(bridge, "current_seed", lambda: "SPSEED")
    assert blindplay._session_seed() == "SPSEED"


# ------------------------------------------------------------ the embark ---

class _Ledger:
    def __init__(self, path):
        self.path = path


class _Session:
    made: list = []

    def __init__(self, stamp, instance, args, install_bridge, world):
        self.stamp, self.instance, self.args = stamp, instance, args
        self.install_bridge = install_bridge
        self.world = world
        self.ledger = _Ledger(Path(f"reversibility-{stamp}.json"))
        self.seed_noted = False
        _Session.made.append(self)

    def setup(self):
        self.world.events.append(f"setup:{self.instance.label}")
        self.world.up.add(self.instance.label)

    def note_seed_channel(self):
        self.seed_noted = True


class _World:
    """Two lanes' bridges, scripted: a lobby, then a co-op run."""

    BridgeError = bridge.BridgeError

    def __init__(self, host="lane2", client="lane3", lobby_ascension=5):
        self.host, self.client = host, client
        self.lane = None
        self.up: set[str] = set()
        self.events: list[str] = []
        self.picked: dict[str, str] = {}
        self.ready: set[str] = set()
        self.ascension = lobby_ascension

    def use(self, inst):
        self.lane = inst.label

    def health(self):
        if self.lane not in self.up:
            raise bridge.BridgeError("unreachable")
        return {"status": "ok"}

    def _lobby(self):
        players = [{"is_local": lane == self.lane,
                    "character_id": self.picked.get(lane, "")}
                   for lane in (self.host, self.client) if lane in self.up]
        return {"type": "host" if self.lane == self.host else "client",
                "player_count": len(players), "players": players,
                "ascension": self.ascension}

    def get_state(self):
        if self.lane not in self.up:
            raise bridge.BridgeError("unreachable")
        if self.ready >= {self.host, self.client}:
            who = {"KLEEMOD-KLEE": "Klee", "KLEEMOD-FURINA": "Furina"}
            return {"state_type": "map", "game_mode": "multiplayer",
                    "run": {"floor": 1, "ascension": self.ascension},
                    "player": {"character": who[self.picked[self.lane]]}}
        opts = [{"name": "KLEEMOD-KLEE"}, {"name": "KLEEMOD-FURINA"}]
        if self.lane in self.picked:
            opts.append({"name": "confirm"})
        return {"state_type": "menu", "menu_screen": "character_select",
                "options": opts, "lobby": self._lobby()}

    def post(self, action, **params):
        opt = params.get("option")
        self.events.append(f"post:{self.lane}:{opt}")
        if opt == "confirm":
            self.ready.add(self.lane)
        else:
            self.picked[self.lane] = opt
        return {"status": "ok"}

    def set_ascension(self, n):
        self.events.append(f"ascension:{self.lane}:{n}")
        self.ascension = n
        return {"status": "ok", "lobby_ascension": n}

    def set_seed(self, seed):
        self.events.append(f"seed:{self.lane}:{seed}")
        return {"status": "ok", "chosen": seed}


@pytest.fixture
def coop_dirs(monkeypatch, tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    monkeypatch.setattr(embark, "LOG_DIR", logs)
    monkeypatch.setattr(embark_coop, "LOG_DIR", logs)
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", logs)
    monkeypatch.setattr(lanewatch, "_STORE_DIR", logs)
    _Session.made = []
    return tmp_path


def _lane(tmp_path):
    def make(label):
        appdata = tmp_path / label
        return instances.Instance(game_dir=tmp_path, port=15526
                                  + int(label[4:]), appdata=appdata,
                                  label=label)
    return make


def _save(tmp_path, label, seed):
    saves = (tmp_path / label / "SlayTheSpire2" / "steam" / "123"
             / "modded" / "profile1" / "saves")
    saves.mkdir(parents=True, exist_ok=True)
    (saves / embark_coop.MP_SAVE).write_text(
        json.dumps({"rng": {"seed": seed}}), encoding="utf-8")


def _embark(world, tmp_path, **kw):
    clock = _Clock()
    _save(tmp_path, "lane2", "P8SFJZPHDXGL")
    return embark_coop.embark(
        ["lane2", "lane3"], ["KLEEMOD-KLEE", "KLEEMOD-FURINA"], wire=world,
        session_factory=lambda stamp, inst, args, ib: _Session(
            stamp, inst, args, ib, world),
        lane_factory=_lane(tmp_path), port_free=lambda: True,
        clock=clock, sleep=clock.sleep, **kw)


def test_a_coop_embark_runs_host_then_client_and_writes_both_sidecars(
        coop_dirs):
    world = _World()
    blob = _embark(world, coop_dirs, ascension=0, max_actions=90)
    host, client = _Session.made
    assert host.args == embark_coop.HOST_ARGS
    assert client.args == ("--fastmp", "join", "--clientId", "1000")
    ev = world.events
    assert ev.index("setup:lane2") < ev.index("setup:lane3")
    # The ascension goes on the host alone, after both picks, before either
    # confirm; the client confirms first.
    assert [e for e in ev if e.startswith("ascension")] == [
        "ascension:lane2:0"]
    assert ev.index("post:lane3:KLEEMOD-FURINA") \
        < ev.index("ascension:lane2:0") < ev.index("post:lane3:confirm") \
        < ev.index("post:lane2:confirm")
    assert not any(e.startswith("seed") for e in ev)
    assert blob["run_seed"] == "P8SFJZPHDXGL"
    assert blob["ascension"] == {"lane2": 0, "lane3": 0}
    assert blob["character_actual"] == {"lane2": "Klee", "lane3": "Furina"}
    on_disk = json.loads(embark_coop.coop_path(blob["stamp"])
                         .read_text(encoding="utf-8"))
    assert on_disk["state"] == "open" and on_disk["host"] == "lane2"
    for label, role in (("lane2", "host"), ("lane3", "client")):
        side = json.loads(Path(on_disk["lane_sidecars"][label])
                          .read_text(encoding="utf-8"))
        assert side["instance"] == label
        assert side["coop"]["role"] == role
        assert side["run_seed"] == "P8SFJZPHDXGL"
        assert side["max_actions"] == 90
        # What the lane readers already read, unchanged.
        assert lanewatch.sidecar_row(label, log_dir=embark.LOG_DIR) == side


def test_a_chosen_seed_goes_on_the_host_only(coop_dirs):
    world = _World()
    blob = _embark(world, coop_dirs, seed="CHOSEN")
    assert [e for e in world.events if e.startswith("seed")] == [
        "seed:lane2:CHOSEN"]
    assert _Session.made[0].seed_noted and not _Session.made[1].seed_noted
    assert blob["run_seed"] == "CHOSEN"


def test_a_host_that_never_reaches_its_lobby_is_refused_by_name(coop_dirs):
    world = _World()
    world.get_state = lambda: {"state_type": "menu", "menu_screen": "main",
                               "options": [{"name": "settings"}]}
    with pytest.raises(embark_coop.EmbarkError) as exc:
        _embark(world, coop_dirs)
    assert "never reached a host lobby" in str(exc.value)
    assert "menu_screen=main" in str(exc.value)
    assert len(_Session.made) == 1                 # the client never launched


def test_the_embark_refuses_before_launching_anything(coop_dirs):
    with pytest.raises(embark_coop.EmbarkError, match="33771"):
        embark_coop.embark(["lane2", "lane3"], ["KLEEMOD-KLEE"] * 2,
                           wire=_World(), port_free=lambda: False,
                           lane_factory=_lane(coop_dirs))
    for bad in ("2", "2,2", "0,3", "2,9"):
        with pytest.raises(embark_coop.EmbarkError):
            embark_coop.parse_lanes(bad)
    assert embark_coop.parse_lanes("2,3") == ["lane2", "lane3"]
    assert embark_coop.parse_characters("klee") == ["KLEEMOD-KLEE"] * 2
    assert _Session.made == []


def test_the_seed_is_read_only_from_a_save_written_after_the_launch(tmp_path):
    _save(tmp_path, "lane2", "OLD")
    saves = next((tmp_path / "lane2").rglob(embark_coop.MP_SAVE))
    os.utime(saves, (1000, 1000))
    assert embark_coop.mp_save_seed(tmp_path / "lane2", since=5000) == ""
    assert embark_coop.mp_save_seed(tmp_path / "lane2", since=500) == "OLD"


def test_the_teardown_takes_the_client_down_first(coop_dirs):
    world = _World()
    _embark(world, coop_dirs)
    order = []

    def down(stamp, lane=None):
        order.append((lane, stamp))
        return "| ledger |"

    text = embark_coop.teardown(["lane3", "lane2"], lane_teardown=down)
    assert [lane for lane, _ in order] == ["lane3", "lane2"]
    assert all(stamp.endswith(lane) for lane, stamp in order)
    assert "lane3:" in text and "lane2:" in text
    blob = json.loads(embark_coop.latest(["lane2", "lane3"])
                      .read_text(encoding="utf-8"))
    assert blob["state"] == "torn_down"


def test_the_embark_cli_routes_coop_and_refuses_an_arm():
    assert embark.main(["--coop", "--lanes", "2,3", "--characters", "klee",
                        "--arm", "x"]) == 2


# -------------------------------------------------------------- the brief --

def test_the_coop_paragraph_is_printed_only_with_coop():
    from tier0.tests.test_agent_rituals import _module
    seat = _module("seat")
    plain = seat.brief_text(2, "KLEEMOD-KLEE")
    coop = seat.brief_text(2, "KLEEMOD-KLEE", coop=True)
    assert "co-op" not in plain.lower() and "wait" not in plain.lower()
    assert coop.startswith(plain.rstrip())
    assert 'act "wait"' in coop and "## CO-OP" not in coop
