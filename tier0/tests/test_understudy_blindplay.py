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

from understudy import blindplay, qa_packet, soak

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
              "adapter", "naming", "staged_turn", "replay"}
    assert not [m for m in named
                if m.split(".")[0] in ("tier0", "tier05")], named
    assert not [m for m in named if m.rsplit(".", 1)[-1] in banned], named


def test_soak_never_imports_blindplay():
    """The other direction, and the same rule `scenario.py` lives under: an
    unattended soak may not reach a tool whose whole job is to hand a screen to
    a third party's model."""
    named = _imported(Path(soak.__file__))
    assert not [m for m in named if "blindplay" in m], named


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
    identity = {**thread.identity(), "build_version": "0.2.1252+proto",
                "build_version_source": "the bridge's health `mod_version`",
                "run_seed": "HUMWKRKNCE",
                "prompt_sha256": summary["prompt_sha256"],
                "actions": summary["actions"],
                "termination": summary["termination"]}
    path = blindplay.seal(summary, identity, log_dir=s.dir,
                          record_root=tmp_path / "committed")
    text = path.read_text(encoding="utf-8")
    assert "0.2.1252+proto" in text and "HUMWKRKNCE" in text
    assert summary["prompt_sha256"] in text
    assert "R217 G" in text and "not approval" in text
    assert "words" in text


def test_the_build_version_is_read_or_left_empty_never_invented():
    class Silent:
        def health(self):
            return {}

    class Broken:
        def health(self):
            raise RuntimeError("no bridge")

    assert blindplay.build_version(blindplay.ScriptedWire([]))[0] == \
        "0.0-scripted"
    assert blindplay.build_version(Silent())[0] == ""
    version, why = blindplay.build_version(Broken())
    assert version == "" and "did not answer" in why
