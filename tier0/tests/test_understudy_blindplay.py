"""EB-167/EB-168: the design-blind any-screen render and its driver.

No game, no codex. What can be pinned without either is everything this row is
actually about: that the module cannot reach a sheet or a policy, that every
screen it knows renders and survives the scrubber, that a screen it does not
know is REFUSED rather than guessed at, that a command resolves by printed name
only, and that the whole session loop runs to a stop on each of its budgets
against a scripted wire and a scripted tester.

FIXTURES: RECORDED WHERE ONE EXISTS, SYNTHETIC WHERE NONE DOES. The combat
screen is a real recorded wire state (`review/qa/kokomi-slice1-r3-t01/
observed.json`, staged live on 2026-08-28 and committed). No other screen kind
has a full committed recording -- the Phase-0 logs store decisions, not states
-- so map, shop, rest, event, the reward screens and the selection overlays are
built here from `vendor/STS2_MCP/docs/raw-simplified.md`'s state table and the
field names `understudy/naming.py` reads off each of them. Those are marked
`synthetic` in `SCREENS` below, and a synthetic fixture proves the RENDERER,
never the wire.
"""

from __future__ import annotations

import ast
import json
import time
from pathlib import Path

import pytest

from understudy import blindplay, embark, qa_packet, soak

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")


# ------------------------------------------------------------- fixtures ----

def combat_state() -> dict:
    """RECORDED. A real staged Kokomi turn as the bridge returned it."""
    blob = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))
    return blob["state"]


def map_state() -> dict:
    """SYNTHETIC. `map.next_options`, named by room type (`naming.py:170`)."""
    return {"state_type": "map",
            "run": {"act": 1, "floor": 3},
            "player": {"hp": 40, "max_hp": 70, "gold": 99},
            "map": {"next_options": [
                {"index": 0, "type": "Monster", "col": 1, "row": 4},
                {"index": 1, "type": "Monster", "col": 2, "row": 4},
                {"index": 2, "type": "rest_site", "col": 3, "row": 4}]}}


def shop_state() -> dict:
    """SYNTHETIC. `items` with `name`/`type`/`price` (`naming.py:202`)."""
    return {"state_type": "shop",
            "player": {"hp": 40, "max_hp": 70, "gold": 120},
            "items": [{"name": "Coral Guard", "type": "card", "price": 75},
                      {"name": "Bottled Tide", "type": "relic", "price": 160,
                       "description": "At the start of each combat, gain 3 "
                                      "Block."}]}


def rest_state() -> dict:
    """SYNTHETIC. `rest_site.options` with `name`/`index`/`is_enabled`."""
    return {"state_type": "rest_site",
            "player": {"hp": 30, "max_hp": 70},
            "rest_site": {"options": [
                {"index": 0, "name": "Rest", "is_enabled": True,
                 "description": "Heal 30% of your maximum health."},
                {"index": 1, "name": "Smith", "is_enabled": True,
                 "description": "Upgrade a card."},
                {"index": 2, "name": "Dig", "is_enabled": False}]}}


def event_state() -> dict:
    """SYNTHETIC. `event.options` carry their own `index` (`naming.py:183`)."""
    return {"state_type": "event",
            "event": {"event_id": "BONFIRE_SPIRITS",
                      "event_name": "Bonfire Spirits",
                      "in_dialogue": False,
                      "body": "The spirits ask for an offering.",
                      "options": [{"index": 0, "title": "Offer a card"},
                                  {"index": 1, "title": "Leave"}]}}


def hazard_event_state() -> dict:
    """SYNTHETIC, and the one screen that must never be played: EB-1."""
    return {"state_type": "event",
            "event": {"event_id": "PUNCH_OFF", "event_name": "Punch Off",
                      "options": [{"index": 0, "title": "Nab it"}]}}


def card_reward_state() -> dict:
    """SYNTHETIC. `card_reward.cards`, printed faces (`naming.py:82`)."""
    return {"state_type": "card_reward",
            "card_reward": {"can_skip": True, "cards": [
                {"name": "Coral Guard", "cost": "1", "type": "Skill",
                 "description": "Gain 5 Block."},
                {"name": "Coral Guard", "cost": "1", "type": "Skill",
                 "is_upgraded": True, "description": "Gain 8 Block."},
                {"name": "Bake-Kurage", "cost": "1", "type": "Skill",
                 "description": "Summon Bake-Kurage for 1 turn."}]}}


def card_select_state() -> dict:
    """SYNTHETIC. The three screens in one name -- the PROMPT is the only
    place the game states which one it is (`policy_v1.py:1066-1070`)."""
    return {"state_type": "card_select",
            "card_select": {"screen_type": "select", "can_confirm": False,
                            "can_cancel": True,
                            "prompt": "Choose a card to Remove.",
                            "cards": [
                                {"name": "Coral Guard", "cost": "1",
                                 "description": "Gain 5 Block."},
                                {"name": "Send the Runner", "cost": "0",
                                 "description": "Draw 1 card."}]}}


def rewards_state() -> dict:
    """SYNTHETIC. `rewards.items` (`naming.py:218`)."""
    return {"state_type": "rewards",
            "rewards": {"items": [{"name": "Gold", "description": "25 gold"},
                                  {"name": "Card"}]}}


def treasure_state() -> dict:
    """SYNTHETIC. `relics` (`naming.py:212`)."""
    return {"state_type": "treasure",
            "relics": [{"name": "Pearl Diver's Charm",
                        "description": "Start each combat with 1 Charge."}]}


def game_over_state() -> dict:
    return {"state_type": "game_over", "run": {"floor": 9},
            "game_over": {"result": "Defeat"}}


def menu_state() -> dict:
    return {"state_type": "menu", "options": [{"name": "embark"}]}


# `(name, builder, provenance, drivable)`. `provenance` is the honest label the
# module docstring promises: `recorded` means a real wire state is committed in
# this repo, `synthetic` means the fixture was written from the wire doc.
SCREENS = [
    ("combat", combat_state, "recorded", True),
    ("map", map_state, "synthetic", True),
    ("shop", shop_state, "synthetic", True),
    ("rest_site", rest_state, "synthetic", True),
    ("event", event_state, "synthetic", True),
    ("card_reward", card_reward_state, "synthetic", True),
    ("card_select", card_select_state, "synthetic", True),
    ("rewards", rewards_state, "synthetic", True),
    ("treasure", treasure_state, "synthetic", True),
    ("game_over", game_over_state, "synthetic", False),
    ("menu", menu_state, "synthetic", False),
    ("hazard", hazard_event_state, "synthetic", False),
]


# ------------------------------------------------------- structural pins ---

def _imported(path: Path) -> list[str]:
    names: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        if isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    return names


def test_blindplay_cannot_reach_a_sheet_or_a_policy():
    """THE NO-LEAK GUARANTEE, STRUCTURALLY -- the same pin `qa_packet` carries,
    widened by the two modules R217 E named. `harness` prints policy_v0's
    recommendation beside the screen, which is precisely the leak this row
    forbids; `soak`, `scenario`, `adapter` and `naming` each reach a tier0
    sheet loader transitively, so they are refused by the same walk."""
    named = _imported(Path(blindplay.__file__))
    banned = {"harness", "policy_v0", "policy_v1", "soak", "scenario",
              "adapter", "naming", "staged_turn", "replay", "embark"}
    assert not [m for m in named
                if m.split(".")[0] in ("tier0", "tier05")], named
    assert not [m for m in named if m.rsplit(".", 1)[-1] in banned], named


def test_soak_never_imports_blindplay():
    """The other direction, and the same rule `scenario.py` lives under: an
    unattended soak may not reach a tool whose whole job is to hand a screen to
    a third party's model."""
    named = _imported(Path(soak.__file__))
    assert not [m for m in named if "blindplay" in m], named


def test_a_base_game_sprite_tag_renders_instead_of_refusing():
    """FOUND LIVE, on the first screen of the first acceptance run. Neow's boon
    list prints Booming Conch as "...and gain [silent_energy_icon.png]" -- the
    base game's own inline sprite tag, which the blunt snake_case rule reads as
    an internal id. It refused the screen and no run could start. The tag names
    an ICON THE PLAYER IS LOOKING AT, so it is rendered, not exempted: showing
    a tester a filename is not showing them the screen."""
    state = {"state_type": "event",
             "event": {"event_id": "NEOW", "event_name": "Neow",
                       "options": [
                           {"index": 0, "title": "Booming Conch",
                            "description": "At the start of Elite combats, "
                                           "draw 2 additional cards and gain "
                                           "[silent_energy_icon.png]."}]}}
    page = blindplay.observe(state)                  # would raise PacketLeak
    assert "[silent energy icon]" in page
    assert ".png" not in page

    # And the narrowness is the point: a bracketed token WITHOUT an image
    # extension is still an id, and still refuses.
    state["event"]["options"][0]["description"] = "gain [pearl_barrage]"
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observe(state)


def test_blindplay_never_imports_the_operator_side_embark():
    """`embark.py` exists BECAUSE `blindplay` may not launch a game: it imports
    `soak`, and through it `policy_v1` and every tier0 sheet loader. An import
    of it from the blind module would carry the whole banned tree in behind one
    innocuous name, so it is pinned in both directions -- named in `banned`
    above, and checked here from the other end."""
    assert embark.soak is soak, "embark is the side that owns the launch"
    assert not [m for m in _imported(Path(blindplay.__file__))
                if "embark" in m], "blindplay reached the operator side"


def test_embark_expands_a_roster_id_to_a_select_screen_option():
    """EB-117's cheap half: `--character kokomi` must not reach `soak._embark`,
    which compares against the screen's own option strings and would embark on
    whatever was highlighted."""
    assert embark.option_id("kokomi") == "KLEEMOD-KOKOMI"
    assert embark.option_id("KLEEMOD-KOKOMI") == "KLEEMOD-KOKOMI"
    with pytest.raises(embark.EmbarkError):
        embark.option_id("")


def test_a_hold_embark_has_nothing_to_tear_down(tmp_path, monkeypatch):
    """FOUND LIVE. A `--hold` attaches to a game somebody else launched and
    records no ledger rows -- so it must not be picked as "the latest embark"
    by a teardown, or the launch that DOES need reverting hides behind it and
    the mod stays in the game directory."""
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    (tmp_path / "embark-20260101-000000.json").write_text(json.dumps(
        {"stamp": "20260101-000000", "hold": False,
         "ledger": str(tmp_path / "led.json")}), encoding="utf-8")
    (tmp_path / "embark-20260202-000000.json").write_text(json.dumps(
        {"stamp": "20260202-000000", "hold": True, "ledger": "gone"}),
        encoding="utf-8")
    assert embark.latest_stamp() == "20260101-000000"
    assert "nothing to revert" in embark.teardown("20260202-000000")


def test_every_soak_ledger_row_has_an_embark_teardown_slot():
    """`--teardown` runs in a DIFFERENT PROCESS from the embark, so it rebinds
    `Session`'s undo entries by the ledger text on disk. A row soak learns to
    write that this map does not know would be left APPLIED forever, which is a
    teardown that silently keeps a mod in somebody's game directory."""
    slots = [attr for attr, _ in embark._LEDGER_SLOTS]
    for attr in ("_seed_entry", "_speed_entry", "_launch_entry",
                 "_bridge_entry", "_appid_entry"):
        assert attr in slots, attr
    assert len(slots) == len(set(slots))


def test_the_hazard_register_covers_soak_s():
    """`blindplay.HAZARD_EVENTS` is a deliberate second copy (importing soak
    would drag policy_v1 in). This is the test that keeps the copy honest: the
    day soak registers a hazard this file does not, it goes red."""
    assert set(soak.HAZARD_EVENTS) <= set(blindplay.HAZARD_EVENTS)


# ------------------------------------------------------------- rendering ---

@pytest.mark.parametrize("name,build,provenance,drivable", SCREENS,
                         ids=[s[0] for s in SCREENS])
def test_every_screen_renders_and_is_blind(name, build, provenance, drivable):
    state = build()
    obs = blindplay.observation(state)
    page = blindplay.render(obs)
    assert page.strip()
    assert bool(obs["blocked"]) is not drivable
    # The scrubber has already run inside `observation` and `render`; this is
    # the same claim spelled out in the vocabulary a reader checks by eye.
    for forbidden in ("KLEEMOD", "pearl_barrage", "role:", "archetypes",
                      "tempo_band", "policy", "score", "EV "):
        assert forbidden not in page, f"{forbidden!r} leaked into {name}"
    assert provenance in ("recorded", "synthetic")


def test_the_recorded_combat_screen_prints_the_faces_and_no_ids():
    """A render that leaks nothing by being empty is not a render."""
    page = blindplay.observe(combat_state())
    assert "Pearl Barrage" in page and "Nibbit" in page
    assert "Intent: Aggressive, 12" in page
    assert "Charge: 8" in page                    # a meter that holds something
    assert "Burst" not in page                    # ...and one that does not
    assert "11 in the draw pile" in page          # pile COUNTS, not contents
    assert "Bake-Kurage" not in page              # ...which is in the draw pile
    assert "KLEEMOD" not in page and "_" not in page.replace("state_type", "")


def test_a_card_face_carrying_an_internal_id_is_refused():
    """The belt to the allowlist's brace, exactly as in `qa_packet`: a wire
    that started printing ids would be refused rather than rendered."""
    state = combat_state()
    state["player"]["hand"][0]["description"] = "Play pearl_barrage. Deal 5."
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observation(state)


def test_a_design_tag_on_a_face_is_refused():
    state = combat_state()
    state["player"]["hand"][0]["description"] = "role: payoff. Deal 5 damage."
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observation(state)


def test_a_policy_hint_and_the_run_seed_never_reach_the_page():
    """STRUCTURAL, not scrubbed, and the distinction is worth stating. A
    policy recommendation and the run seed are refused by the ALLOWLIST -- no
    line of this module copies either -- which is the stronger of the two
    guards, because nothing has to recognise them. The scrubber only ever sees
    what the allowlist already let through."""
    state = combat_state()
    state["policy_v0"] = {"action": "play_card", "label": "Pearl Barrage",
                          "score": 12.5}
    state["recommendation"] = "play Pearl Barrage on Nibbit"
    state["run_seed"] = "HUMWKRKNCE"
    page = blindplay.observe(state)
    assert "12.5" not in page and "recommend" not in page.lower()
    assert "HUMWKRKNCE" not in page


def test_an_unknown_state_type_is_tool_blocked_and_never_guessed():
    obs = blindplay.observation({"state_type": "seance_minigame"})
    assert obs["blocked"]
    assert "TOOL-BLOCKED: seance_minigame" in blindplay.render(obs)
    # ...and nothing can be done on it, however reasonable the command reads.
    assert blindplay.act({"state_type": "seance_minigame"}, "proceed")[
        "refusal"]


def test_the_undriven_screens_are_named_rather_than_lumped_in():
    for st in ("crystal_sphere", "overlay", "unknown"):
        obs = blindplay.observation({"state_type": st})
        assert obs["blocked"] and obs["screen"] == "undriven"


def test_a_hazard_event_is_tool_blocked():
    """EB-1. The register, not a heuristic: the screen renders as refused and
    the driver stops, because there is no safe option to pick."""
    obs = blindplay.observation(hazard_event_state())
    assert obs["screen"] == "hazard" and obs["blocked"]
    assert "TOOL-BLOCKED: event" in blindplay.render(obs)
    assert blindplay.act(hazard_event_state(), 'choose "Nab it"')["refusal"]
    # A NON-hazard event on the same screen type is driven normally.
    assert not blindplay.observation(event_state())["blocked"]


# -------------------------------------------------------------- grammar ----

def test_the_grammar_refuses_what_it_does_not_know():
    with pytest.raises(blindplay.BlindPlayError):
        blindplay.parse_command("attack the big one")
    with pytest.raises(blindplay.BlindPlayError):
        blindplay.parse_command("play Pearl Barrage")     # no quotes
    assert blindplay.parse_command('play "A" on "B"').names == ["A", "B"]
    assert blindplay.parse_command("end turn").verb == "end turn"
    assert blindplay.parse_command('use potion "Fire"').verb == "use potion"


def test_a_play_resolves_by_printed_title_at_the_moment_of_posting():
    state = combat_state()
    res = blindplay.act(state, 'play "All Streams Flow to the Sea" on "Nibbit"')
    assert res["ok"]
    assert res["post"]["action"] == "play_card"
    assert res["post"]["card_index"] == 4           # list position, not `index`
    assert res["post"]["target"] == "NIBBIT_0"      # the id lives HERE only
    assert res["printed"] == {"card": "All Streams Flow to the Sea",
                              "target": "Nibbit"}


def test_a_single_enemy_needs_no_naming_but_a_wrong_name_refuses():
    state = combat_state()
    assert blindplay.act(state, 'play "Pearl Barrage"')["ok"]
    res = blindplay.act(state, 'play "Pearl Barrage" on "Jaw Worm"')
    assert not res["ok"] and "Jaw Worm" in res["refusal"]


def test_a_title_matching_two_different_faces_is_refused_as_ambiguous():
    """Two Coral Guards, one upgraded, are two different cards. A driver that
    picked one would be answering a question the tester did not ask."""
    res = blindplay.act(card_reward_state(), 'choose "Coral Guard"')
    assert not res["ok"] and "more than one" in res["refusal"]
    ok = blindplay.act(card_reward_state(), 'choose "Bake-Kurage"')
    assert ok["ok"] and ok["post"]["card_index"] == 2


def test_two_identical_copies_are_interchangeable():
    """...and the same rule the other way: refusing here would make a second
    copy of a card unplayable, which is not an ambiguity a player has."""
    state = combat_state()
    hand = state["player"]["hand"]
    hand.append(json.loads(json.dumps(hand[3])))     # a second Coral Guard
    res = blindplay.act(state, 'play "Coral Guard"')
    assert res["ok"] and res["post"]["card_index"] == 3


def test_an_unplayable_card_is_refused_with_the_game_s_own_reason():
    state = combat_state()
    state["player"]["hand"][0]["can_play"] = False
    state["player"]["hand"][0]["unplayable_reason"] = "Not enough energy"
    res = blindplay.act(state, 'play "Pearl Barrage"')
    assert not res["ok"] and "Not enough energy" in res["refusal"]


def test_a_shop_refuses_what_the_run_cannot_afford():
    res = blindplay.act(shop_state(), 'buy "Bottled Tide"')
    assert not res["ok"] and "160" in res["refusal"] and "120" in res["refusal"]
    ok = blindplay.act(shop_state(), 'buy "Coral Guard"')
    assert ok["ok"] and ok["post"] == {"action": "shop_purchase", "index": 0}


def test_the_map_numbers_its_paths_so_a_fork_is_nameable():
    page = blindplay.observe(map_state())
    assert "Monster (path 1)" in page and "Rest Site (path 3)" in page
    ambiguous = blindplay.act(map_state(), 'go "Monster"')
    assert not ambiguous["ok"]
    res = blindplay.act(map_state(), 'go "Monster (path 2)"')
    assert res["ok"] and res["post"] == {"action": "choose_map_node",
                                         "index": 1}


def test_the_screen_decides_the_verb_not_the_command():
    """One `choose`, six wire actions. Each is the verb that screen advertises
    in `vendor/STS2_MCP/docs/raw-simplified.md`."""
    cases = [
        (event_state(), 'choose "Leave"',
         {"action": "choose_event_option", "index": 1}),
        (rest_state(), "rest", {"action": "choose_rest_option", "index": 0}),
        (rest_state(), "upgrade", {"action": "choose_rest_option", "index": 1}),
        (rewards_state(), 'choose "Gold"',
         {"action": "claim_reward", "index": 0}),
        (treasure_state(), 'choose "Pearl Diver\'s Charm"',
         {"action": "claim_treasure_relic", "index": 0}),
        (card_select_state(), 'choose "Send the Runner"',
         {"action": "select_card", "index": 1}),
        (card_reward_state(), "skip", {"action": "skip_card_reward"}),
        (combat_state(), "end turn", {"action": "end_turn"}),
        (shop_state(), "proceed", {"action": "proceed"}),
    ]
    for state, command, want in cases:
        res = blindplay.act(state, command)
        assert res["ok"], f"{command}: {res['refusal']}"
        assert res["post"] == want, command


def test_a_disabled_option_is_refused():
    res = blindplay.act(rest_state(), 'choose "Dig"')
    assert not res["ok"] and "not available" in res["refusal"]


def test_a_command_on_the_wrong_screen_is_refused():
    assert not blindplay.act(map_state(), "end turn")["ok"]
    assert not blindplay.act(combat_state(), 'go "Monster (path 1)"')["ok"]
    assert not blindplay.act(shop_state(), 'play "Coral Guard"')["ok"]


# -------------------------------------------------------------- session ----

def fight_states() -> list[dict]:
    """A scripted fight: two combat frames, a reward screen, then game over."""
    a = combat_state()
    b = json.loads(json.dumps(a))
    b["battle"]["enemies"][0]["hp"] = 20
    return [a, b, rewards_state(), game_over_state()]


def _session(tmp_path, replies, states=None, **budget):
    thread = blindplay.ScriptedThread(replies)
    wire = blindplay.ScriptedWire(states if states is not None
                                  else fight_states())
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(**budget),
                          log_root=tmp_path)
    return s, s.run(), wire, thread


def test_a_scripted_fight_runs_end_to_end(tmp_path):
    """The whole loop, without the game and without codex: observation ->
    command -> POST -> the next screen, then the fight record at the end of the
    fight and the run record at the end of the run, both kept verbatim."""
    replies = [
        {"command": 'play "Pearl Barrage" on "Nibbit"', "thinking": "chip"},
        {"command": "end turn", "thinking": "nothing left"},
        {"record": "I opened with the exhaust attack."},
        {"command": 'choose "Gold"', "thinking": "take it"},
        {"record": "Kokomi seems to want a full rotation."},
    ]
    s, summary, wire, thread = _session(tmp_path, replies)
    assert summary["termination"] == "run_over"
    assert summary["actions"] == 3
    assert [p["action"] for p in wire.posts] == ["play_card", "end_turn",
                                                 "claim_reward"]
    assert wire.posts[0]["target"] == "NIBBIT_0"
    assert summary["fight_records"] == ["I opened with the exhaust attack."]
    assert summary["run_record"].startswith("Kokomi seems")
    # The first prompt carries the blind brief; later ones are just screens.
    assert "Everything you know is on the page" in thread.sent[0]
    assert "Everything you know is on the page" not in thread.sent[1]
    rows = [json.loads(l) for l in
            (tmp_path / "t" / "transcript.jsonl").read_text(
                encoding="utf-8").splitlines()]
    assert {r["kind"] for r in rows} >= {"observation", "command", "result",
                                         "record"}
    assert all(len(r["observation_sha256"]) == 64
               for r in rows if r["kind"] == "observation")


def test_the_session_stops_on_the_action_budget(tmp_path):
    replies = [{"command": "end turn", "thinking": "x"} for _ in range(5)]
    replies.append({"record": "short run"})
    s, summary, wire, _ = _session(tmp_path, replies,
                                   states=[combat_state()], max_actions=2)
    assert summary["termination"] == "max_actions"
    assert summary["actions"] == 2 and len(wire.posts) == 2


def test_the_session_stops_on_consecutive_refusals(tmp_path):
    """A tester that keeps naming a card that is not there is stopped, not
    looped: nothing is posted and the refusal count is the budget."""
    replies = [{"command": 'play "Fireball"', "thinking": "?"}
               for _ in range(5)]
    s, summary, wire, _ = _session(tmp_path, replies, states=[combat_state()],
                                   max_refusals=2)
    assert summary["termination"] == "refusal_limit"
    assert wire.posts == [] and summary["actions"] == 0
    assert summary["run_record"] == ""      # nothing was played, nothing asked


def test_the_session_stops_on_the_wall_clock(tmp_path):
    thread = blindplay.ScriptedThread(
        [{"command": "end turn", "thinking": "x"} for _ in range(3)])
    wire = blindplay.ScriptedWire([combat_state()])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(max_wall_s=-1.0),
                          log_root=tmp_path)
    assert s.run()["termination"] == "max_wall"


class _LimitedThread(blindplay.ScriptedThread):
    """A seat whose account quota runs out after `after` replies."""

    def __init__(self, replies, after: int):
        super().__init__(replies)
        self.after = after

    def send(self, prompt, schema):
        if self.calls >= self.after:
            raise blindplay.SeatBudgetExhausted("codex exited 1 on a usage "
                                                "limit: 429 rate limit")
        return super().send(prompt, schema)


def test_a_usage_limit_stops_the_session_under_its_own_name(tmp_path):
    """SOMEBODY ELSE'S QUOTA IS NOT A FINDING ABOUT THIS GAME. A seat that runs
    out of account budget mid-run is `budget:rate_limit`, not `seat_refused` --
    the two read as opposite things in a sealed record, one a fact about the
    tester's plan and the other a fact about the tool. The partial records
    survive it either way."""
    thread = _LimitedThread([{"command": "end turn", "thinking": "x"}], after=1)
    wire = blindplay.ScriptedWire([combat_state()])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(), log_root=tmp_path)
    summary = s.run()
    assert summary["termination"] == "budget:rate_limit"
    assert summary["actions"] == 1 and len(wire.posts) == 1
    rows = [json.loads(l) for l in
            (tmp_path / "t" / "transcript.jsonl").read_text(
                encoding="utf-8").splitlines()]
    assert any(r["kind"] == "seat_budget" for r in rows)


@pytest.mark.parametrize("text,limited", [
    ("stream error: 429 Too Many Requests", True),
    ("You've hit your usage limit. Try again later.", True),
    ("error: unexpected argument '-C' found", False),
    ("", False),
])
def test_the_rate_limit_markers_read_a_third_party_s_wording(text, limited):
    assert blindplay._is_rate_limited(text) is limited


def test_resume_drops_the_flags_resume_does_not_take(tmp_path):
    """FOUND LIVE, on the SECOND action of the first acceptance run. `codex
    exec resume` accepts neither `-C` nor `--sandbox` nor `--color`, so a
    session that pastes the first turn's argv after `resume` dies every time
    one action in -- no fight, no record. The sandbox is not given up, it moves
    to the config key the flag sets."""
    t = blindplay.CodexThread.__new__(blindplay.CodexThread)
    t.codex, t.model, t.scratch = "codex", "gpt-test", tmp_path
    t.thread_id = ""
    first = t._argv(tmp_path)
    assert first[:2] == ["codex", "exec"] and "-C" in first
    assert "--sandbox" in first

    t.thread_id = "abc-123"
    resumed = t._argv(tmp_path)
    assert resumed[:4] == ["codex", "exec", "resume", "abc-123"]
    for flag in ("-C", "--sandbox", "--color"):
        assert flag not in resumed, flag
    assert 'sandbox_mode="read-only"' in resumed
    # Both arms still end on the stdin prompt and still name the model.
    for argv in (first, resumed):
        assert argv[-1] == "-" and "-m" in argv
        assert "--ignore-user-config" in argv and "--json" in argv


class _TransientWire(blindplay.ScriptedWire):
    """A wire that answers with the transition before it answers with the room.

    Two reads of `unknown` -- one of them with no `state_type` key at all --
    and then the screen. Nothing is posted in between, which is exactly the
    live shape: walking onto a map node changes the room before the bridge can
    name it.
    """

    def __init__(self, states):
        super().__init__(states)
        self.transients = [{"state_type": "unknown"}, {}]

    def get_state(self):
        if self.transients:
            return self.transients.pop(0)
        return super().get_state()


def test_a_transition_is_ridden_out_and_never_reported_as_a_screen(tmp_path):
    """The first live acceptance run stopped TOOL-BLOCKED against the moment
    between two rooms. A bounded settle rides it out; only a wire that STAYS
    unnamed is blocked."""
    thread = blindplay.ScriptedThread([{"command": "end turn",
                                        "thinking": "."},
                                       {"record": "r"}, {"record": "r"}])
    wire = _TransientWire([combat_state(), game_over_state()])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(max_actions=1),
                          log_root=tmp_path, settle_delay_s=0.0)
    summary = s.run()
    assert wire.posts and wire.posts[0]["action"] == "end_turn"
    assert summary["termination"] != "tool_blocked"


def _mid_turn_frame(state: dict) -> dict:
    """The frame `EB-175` was diagnosed on, copied field for field.

    Recorded live on 2026-08-29, 55 ms after `end_turn` answered
    `ok Ending turn`: still `state_type: monster`, still `turn: player`, the
    ROUND UNCHANGED, the hand already discarded to zero, energy still full,
    and `is_play_phase` FALSE. Two of these arrive before the real next round.
    """
    frame = json.loads(json.dumps(state))
    frame["battle"]["is_play_phase"] = False
    frame["player"]["hand"] = []
    frame["player"]["discard_pile_count"] = \
        int(frame["player"].get("discard_pile_count", 0) or 0) + 5
    return frame


class _EndTurnWire:
    """A wire whose `end_turn` is ASYNCHRONOUS, as the bridge's really is.

    `ExecuteEndTurn` calls `PlayerCmd.EndTurn` and answers at once; the next
    two reads are the turn still being handed over. Every POST records the
    round of the frame the TESTER WAS LOOKING AT, which is the whole
    assertion: one `end turn` from the tester must spend exactly one round.

    A turn ends only when it is ended from a play-phase frame -- ending from
    the hand-over frame is what the game itself refuses ("Not in play phase")
    and what the seat spent its real turns on.
    """

    def __init__(self, rounds: list[dict], tail: dict):
        self.rounds, self.tail = list(rounds), tail
        self.i = 0
        self.pending: list[dict] = []
        self.posts: list[dict] = []
        self.posted_rounds: list[int | None] = []
        self.handed: dict = {}

    def _current(self) -> dict:
        return (self.rounds[self.i] if self.i < len(self.rounds)
                else self.tail)

    def get_state(self) -> dict:
        self.handed = self.pending.pop(0) if self.pending else self._current()
        return self.handed

    def post(self, action: str, **params) -> dict:
        seen = self.handed or self._current()
        battle = seen.get("battle") or {}
        self.posts.append({"action": action, **params})
        self.posted_rounds.append(battle.get("round"))
        if action == "end_turn" and battle.get("is_play_phase"):
            self.pending = [_mid_turn_frame(seen), _mid_turn_frame(seen)]
            self.i += 1
        return {"status": "ok", "message": "Ending turn"}

    def health(self) -> dict:
        return {"mod_version": "0.0-scripted"}


def test_the_frame_between_two_turns_is_named_a_transition():
    """`EB-175`, the predicate. A combat screen with `is_play_phase` false is
    a moment, not a screen; a build that does not carry the key at all is not
    read as one."""
    live = combat_state()
    assert blindplay.transient(live) == ""
    assert blindplay.transient(_mid_turn_frame(live))
    no_key = json.loads(json.dumps(live))
    no_key["battle"].pop("is_play_phase")
    assert blindplay.transient(no_key) == ""


def test_one_end_turn_from_the_tester_spends_exactly_one_round(tmp_path):
    """`EB-175`. Four times in one blind session the seat said `end turn`, was
    answered `ok Ending turn`, and was then shown a combat screen with an
    empty hand and full energy -- the frame above -- so it said `end turn`
    again and spent a REAL turn on it. The rounds it recorded went 1 -> 3 -> 5.

    Three `end turn`s, three rounds, and no round entered twice."""
    rounds = []
    for n, hp in ((1, 57), (2, 40), (3, 20)):
        frame = json.loads(json.dumps(combat_state()))
        frame["battle"]["round"] = n
        frame["battle"]["enemies"][0]["hp"] = hp
        rounds.append(frame)
    wire = _EndTurnWire(rounds, game_over_state())
    thread = blindplay.ScriptedThread(
        [{"command": "end turn", "thinking": "."} for _ in range(3)]
        + [{"record": "fight"}, {"record": "run"}])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(max_actions=3),
                          log_root=tmp_path, settle_delay_s=0.0)
    s.run()
    assert [p["action"] for p in wire.posts] == ["end_turn"] * 3
    assert wire.posted_rounds == [1, 2, 3]


def test_a_wire_that_stays_unnamed_is_still_tool_blocked(tmp_path):
    wire = blindplay.ScriptedWire([{"state_type": "unknown"}])
    s = blindplay.Session(blindplay.ScriptedThread([]), wire=wire,
                          session_id="t", log_root=tmp_path,
                          settle_tries=3, settle_delay_s=0.0)
    assert s.run()["termination"] == "tool_blocked" and wire.posts == []


def test_the_session_stops_on_a_screen_it_will_not_drive(tmp_path):
    s, summary, wire, _ = _session(tmp_path, [], states=[hazard_event_state()])
    assert summary["termination"] == "tool_blocked" and wire.posts == []


def test_a_refusal_is_told_back_to_the_tester_in_its_own_words(tmp_path):
    replies = [{"command": 'play "Fireball"', "thinking": "?"},
               {"command": "end turn", "thinking": "fine"},
               {"record": "r"}, {"record": "r"}]
    s, summary, wire, thread = _session(tmp_path, replies,
                                        states=[combat_state()],
                                        max_actions=1)
    assert "That did not work" in thread.sent[1]
    assert "nothing here is called" in thread.sent[1]


# ------------------------------------------------- the seat and the seal ---

def test_the_author_s_own_model_family_is_refused_as_tester():
    """R217 C: independence is by model FAMILY, not by fresh context."""
    for model in ("claude-opus-5", "claude-sonnet-4.5", "anthropic/fable"):
        with pytest.raises(blindplay.BlindPlayError) as e:
            blindplay.check_independent(model)
        assert "family" in str(e.value)
    blindplay.check_independent("gpt-5.6-sol")          # the Codex seat passes
    with pytest.raises(blindplay.BlindPlayError):
        blindplay.check_independent("some-unheard-of-model")


def test_the_prompt_is_readable_and_stamped():
    body = blindplay.seat.template_body(
        blindplay.PROMPT_PATH.read_text(encoding="utf-8"))
    assert "one command" in body
    assert "judgement of whether the game is fun" in body.lower()
    assert len(blindplay.sha256(body)) == 64


def test_the_reply_schemas_constrain_shape_and_never_content():
    for schema in (blindplay.command_schema(), blindplay.record_schema()):
        assert schema["additionalProperties"] is False
        blob = json.dumps(schema)
        assert "enum" not in blob and "minLength" not in blob


def test_the_sealed_record_carries_the_identity_and_the_words_verbatim(tmp_path):
    replies = [{"command": "end turn", "thinking": "x"}, {"record": "words"}]
    s, summary, _wire, thread = _session(tmp_path, replies,
                                         states=[combat_state()],
                                         max_actions=1)
    identity = {**thread.identity(), "build_version": "0.2.1269",
                "build_version_source":
                    "the deployed `mods\\klee\\manifest.json` `version`",
                "game_version": "v0.111.0",
                "game_version_source":
                    "the game's own `release_info.json` `version`",
                "run_seed": "HUMWKRKNCE",
                "prompt_sha256": summary["prompt_sha256"],
                "actions": summary["actions"],
                "termination": summary["termination"]}
    path = blindplay.seal(summary, identity, log_dir=s.dir,
                          record_root=tmp_path / "committed")
    text = path.read_text(encoding="utf-8")
    assert "0.2.1269" in text and "v0.111.0" in text and "HUMWKRKNCE" in text
    assert summary["prompt_sha256"] in text
    assert "R217 G" in text and "not approval" in text
    assert "words" in text


def test_both_versions_are_read_off_disk_or_left_empty_never_invented(
        tmp_path, monkeypatch):
    """`EB-174`. A sealed record has to name the MOD build and the GAME build,
    each labelled with where it was read -- and name neither rather than
    invent one. The bridge's health payload is not consulted at all: it
    carries the VENDORED bridge's own version and never ours, which is how
    every record's identity block came to read `(not read)`."""
    game = tmp_path / "Slay the Spire 2"
    (game / "mods" / "klee").mkdir(parents=True)
    props = tmp_path / "local.props"
    props.write_text(f"<Project><PropertyGroup><GameDir>{game}</GameDir>"
                     f"</PropertyGroup></Project>", encoding="utf-8")
    monkeypatch.setattr(blindplay, "LOCAL_PROPS", props)

    # Nothing deployed and no release file: two empties, two reasons.
    assert blindplay.build_version()[0] == ""
    assert "no deployed package" in blindplay.build_version()[1]
    assert blindplay.game_version()[0] == ""
    assert "release_info.json" in blindplay.game_version()[1]

    # `deploy.ps1` writes the manifest with a BOM; both reads survive one.
    (game / "mods" / "klee" / "manifest.json").write_text(
        '﻿{"id": "klee", "version": "0.2.1269"}', encoding="utf-8")
    (game / "release_info.json").write_text(
        '{"version": "v0.111.0", "commit": "41cef1ea"}', encoding="utf-8")
    assert blindplay.build_version() == (
        "0.2.1269", "the deployed `mods\\klee\\manifest.json` `version`")
    assert blindplay.game_version() == (
        "v0.111.0", "the game's own `release_info.json` `version`")

    # No local.props at all is a reason, not a traceback and not a guess.
    monkeypatch.setattr(blindplay, "LOCAL_PROPS", tmp_path / "absent.props")
    assert blindplay.build_version()[0] == ""
    assert blindplay.game_version()[0] == ""


# --- EB-173: the deadlock a live session died on --------------------------

def test_the_games_own_plus_is_not_folded_away():
    """FOUND LIVE, 2026-08-29, run B of the EB-167 acceptance. `_fold` stripped
    punctuation, and the `+` the GAME appends to an upgraded title is not
    punctuation -- it is the only thing distinguishing the two cards. Folded
    away, `Coral Guard` and `Coral Guard+` shared one key, so with both in hand
    EVERY naming of EITHER was refused as ambiguous and neither could be
    played. The session burned its refusal budget on round 5 and stopped."""
    state = combat_state()
    hand = state["player"]["hand"]
    base = json.loads(json.dumps(hand[3]))
    assert base["name"] == "Coral Guard"
    up = json.loads(json.dumps(base))
    up["name"] = "Coral Guard+"
    up["is_upgraded"] = True
    up["description"] = "Gain 8 Block."
    hand.append(up)

    plain = blindplay.act(state, 'play "Coral Guard"')
    assert plain["ok"] and plain["post"]["card_index"] == 3
    plus = blindplay.act(state, 'play "Coral Guard+"')
    assert plus["ok"] and plus["post"]["card_index"] == len(hand) - 1


def test_echoing_the_screen_back_verbatim_resolves():
    """The render prints `**Coral Guard+** (upgraded)`, and a tester who types
    that back must be understood. Before the fix it answered `nothing here is
    called 'Coral Guard+ (upgraded)'` -- the escape hatch the refusal itself
    advertised was documented in the grammar and implemented nowhere."""
    state = combat_state()
    hand = state["player"]["hand"]
    up = json.loads(json.dumps(hand[3]))
    up["name"] = "Coral Guard+"
    up["is_upgraded"] = True
    hand.append(up)
    res = blindplay.act(state, 'play "Coral Guard+ (upgraded)"')
    assert res["ok"] and res["post"]["card_index"] == len(hand) - 1


def test_the_qualifier_reaches_both_sides_of_an_ambiguous_pair():
    """The card-reward screen prints NO `+` -- two rows both read `Coral
    Guard`, one upgraded -- so the ambiguity refusal is still right there. What
    changed is that it is now escapable in BOTH directions: a disambiguator
    that could only ever name one of the two would leave the other
    unselectable, which is the same defect wearing a different hat."""
    amb = blindplay.act(card_reward_state(), 'choose "Coral Guard"')
    assert not amb["ok"] and "more than one" in amb["refusal"]

    up = blindplay.act(card_reward_state(), 'choose "Coral Guard (upgraded)"')
    assert up["ok"] and up["post"]["card_index"] == 1
    base = blindplay.act(card_reward_state(),
                         'choose "Coral Guard (not upgraded)"')
    assert base["ok"] and base["post"]["card_index"] == 0


def test_the_refusal_advertises_only_what_is_implemented():
    """The whole shape of EB-173: advice a tester cannot act on is worse than
    no advice, because it costs a turn of the refusal budget to discover."""
    amb = blindplay.act(card_reward_state(), 'choose "Coral Guard"')
    assert "(upgraded)" in amb["refusal"] and "(not upgraded)" in amb["refusal"]
    for phrase in ("Coral Guard (upgraded)", "Coral Guard (not upgraded)"):
        assert blindplay.act(card_reward_state(), f'choose "{phrase}"')["ok"]


def test_a_qualifier_that_matches_nothing_says_so_rather_than_guessing():
    state = combat_state()
    res = blindplay.act(state, 'play "Coral Guard (upgraded)"')
    assert not res["ok"] and "is upgraded" in res["refusal"]


def bundle_select_state() -> dict:
    """SYNTHETIC, and shaped on the LIVE wire read 2026-08-29: a bundle has an
    `index` and a list of `cards`, and NO name of its own."""
    return {"state_type": "bundle_select",
            "bundle_select": {"screen_type": "bundle",
                              "prompt": "Choose a bundle.",
                              "bundles": [
                {"index": 0, "card_count": 2, "cards": [
                    {"name": "Call to Arms", "cost": "1", "type": "Skill",
                     "description": "Muster 1. Draw 1 card."},
                    {"name": "Massed Volley", "cost": "1", "type": "Attack",
                     "description": "Deal 5 damage to ALL enemies."}]},
                {"index": 1, "card_count": 2, "cards": [
                    {"name": "Crane Wing", "cost": "1", "type": "Skill",
                     "description": "Gain 4 Block."},
                    {"name": "Massed Volley", "cost": "1", "type": "Attack",
                     "description": "Deal 5 damage to ALL enemies."}]}]}}


def test_a_bundle_is_named_by_what_is_in_it():
    """EB-173, second half. A bundle has no name, and asking the wire for one
    rendered `- **(unnamed)**` twice on a screen whose only verb was
    `choose "<bundle>"`. Nothing on it could be named; a live session sat there
    answering `confirm` until its action budget ran out. The cards inside DO
    have printed titles, so the bundle is named by its contents -- which is
    also how a player at the screen would say it out loud."""
    page = blindplay.render(blindplay.observation(bundle_select_state()))
    assert "(unnamed)" not in page
    assert "A bundle of: Call to Arms, Massed Volley" in page
    assert "Gain 4 Block." in page          # the faces, not just the titles
    assert "any card title in the bundle you want" in page


def test_choosing_a_bundle_by_a_card_only_it_holds():
    res = blindplay.act(bundle_select_state(), 'choose "Call to Arms"')
    assert res["ok"] and res["post"] == {"action": "select_bundle", "index": 0}
    res = blindplay.act(bundle_select_state(), 'choose "Crane Wing"')
    assert res["ok"] and res["post"] == {"action": "select_bundle", "index": 1}


def test_a_card_in_both_bundles_is_refused_rather_than_guessed():
    """Which bundle was meant is exactly the question being asked."""
    res = blindplay.act(bundle_select_state(), 'choose "Massed Volley"')
    assert not res["ok"] and "more than one bundle" in res["refusal"]


def test_a_card_in_no_bundle_is_told_what_is_on_the_screen():
    res = blindplay.act(bundle_select_state(), 'choose "Pearl Barrage"')
    assert not res["ok"]
    assert "Call to Arms" in res["refusal"] and "Crane Wing" in res["refusal"]


def test_the_session_stops_on_a_screen_it_cannot_get_off(tmp_path):
    """EB-173, third half, and the reason the other two cost a whole run. The
    action, wall and refusal budgets all stop a session that is going WRONG.
    None of them sees a session going NOWHERE: a command the resolver ACCEPTS
    and the wire answers with an error resets the refusal counter and spends an
    action, so the loop can sit on one screen until the action budget is gone.
    Live, that was 150+ identical `confirm`s at one bundle screen."""
    replies = [{"command": "confirm", "thinking": ""} for _ in range(40)]
    replies.append({"record": "nothing happened"})
    s, summary, wire, _ = _session(
        tmp_path, replies, states=[bundle_select_state()],
        max_actions=200, max_stalls=4)
    assert summary["termination"] == "stalled"
    assert summary["actions"] < 10


def test_a_hand_select_screen_does_not_kill_the_session():
    """EB-176, found live: a `hand_select` state renders as `card_select`, and
    only the WIRE's name was exempt from the snake_case rule -- so the tool's
    own name for the screen, written into the tool's own observation, tripped
    the blindness assertion and stopped a session on a screen that had leaked
    nothing. Both names are screen vocabulary; neither names a card, a role or
    a ruling."""
    state = {"state_type": "hand_select",
             "hand_select": {"prompt": "Choose a card to discard.",
                             "cards": [{"name": "Coral Guard", "cost": "1",
                                        "type": "Skill",
                                        "description": "Gain 5 Block."}]}}
    obs = blindplay.observation(state)          # must not raise
    assert obs["state_type"] == "hand_select" and obs["screen"] == "card_select"
    assert "Coral Guard" in blindplay.render(obs)


def test_the_exemption_is_still_only_the_screen_names():
    """The other half: widening the allowance must not have widened it to
    anything a card, a sheet or a ruling could put on the page."""
    state = {"state_type": "hand_select",
             "hand_select": {"prompt": "Choose a card to discard.",
                             "cards": [{"name": "Coral Guard", "cost": "1",
                                        "type": "Skill",
                                        "description": "role: bridge"}]}}
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observation(state)
