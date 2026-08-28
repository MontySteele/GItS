"""EB-142's targeted-scenario harness, with no game involved.

The half that only a live Windows box with Steam running can check is the half
that matters least here: whether the bridge answers. What CAN be pinned, and
what this file pins, is everything around it -- the file format's refusals, the
resolution of a card name at the moment of the POST, every assertion function,
the guardrail on every log row, and the two structural facts the whole design
rests on: that a scenario is ATTENDED (so `soak.py` cannot reach it) and that
every card a scenario file names actually exists.

A fake wire stands in for `understudy.bridge`. That is not a mock of a thing we
wish were testable -- `Runner` takes the wire as an argument precisely so this
file can exist.
"""

from __future__ import annotations

import json
import io
from pathlib import Path

import pytest
import yaml

from tier0.content import loader
from understudy import bridge, scenario

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"


# ------------------------------------------------------------ fake wire ----

class FakeWire:
    """A bridge that answers from a scripted list of states.

    `states` is consumed one entry per `get_state()`, and the LAST entry
    repeats forever -- so a test writes only the states it cares about and the
    settle reads after the final action do not fall off the end.
    """

    def __init__(self, states, post_answer=None, grant=None, debug=None):
        self.states = list(states)
        self.posts: list[dict] = []
        self.grants: list[dict] = []
        self.debugs: list[dict] = []
        self.post_answer = post_answer or {"status": "ok", "message": "ok"}
        self.grant = grant or {"status": "ok", "message": "queued"}
        self.debug = debug or {"status": "ok", "message": "set", "queued": False}
        self.reads = 0

    def get_state(self):
        self.reads += 1
        if len(self.states) > 1:
            return self.states.pop(0)
        return self.states[0]

    def post(self, **action):
        self.posts.append(action)
        return dict(self.post_answer)

    def give_card(self, card_id, count=1, upgraded=False, pile="deck"):
        self.grants.append({"card_id": card_id, "count": count,
                            "upgraded": upgraded, "pile": pile})
        return dict(self.grant)

    def debug_state(self, op, why, amount=0, who="player", resource="",
                    power=""):
        self.debugs.append({"op": op, "why": why, "amount": amount,
                            "who": who, "resource": resource, "power": power})
        return dict(self.debug)


def combat(hand=(), enemies=(), block=0, hp=70, energy=3, resources=None,
           status=(), state_type="monster", select=None):
    state = {
        "state_type": state_type,
        "battle": {"round": 1, "turn": "player",
                   "enemies": [dict(e) for e in enemies]},
        "player": {"hp": hp, "max_hp": 70, "block": block, "energy": energy,
                   "hand": [dict(c) for c in hand],
                   "status": [dict(s) for s in status],
                   "resources": dict(resources or {})},
    }
    if select is not None:
        state["state_type"] = select[0]
        state[select[0]] = select[1]
    return state


def enemy(eid="JAW_WORM_0", name="Jaw Worm", hp=40, block=0, status=()):
    return {"entity_id": eid, "name": name, "hp": hp, "max_hp": 44,
            "block": block, "status": [dict(s) for s in status]}


def card(name="Kaboom!", cid="KLEEMOD-KABOOM", cost="1", can_play=True,
         reason=None, desc="Deal 7 damage.", upgraded=False):
    return {"id": cid, "name": name, "cost": cost, "can_play": can_play,
            "unplayable_reason": reason, "description": desc,
            "is_upgraded": upgraded, "target_type": "AnyEnemy"}


def run_scenario(steps, states, **wire_kw):
    s = scenario.parse({"name": "t", "character": "KLEEMOD-KLEE",
                        "steps": steps})
    wire = FakeWire(states, **wire_kw)
    buf = io.StringIO()
    r = scenario.Runner(s, "a test", wire=wire, out=buf,
                        sleep=lambda _s: None)
    ok = r.run()
    return ok, r, wire, buf


# --------------------------------------------------------------- format ----

def test_a_step_is_a_single_key_mapping():
    with pytest.raises(scenario.ScenarioError) as e:
        scenario.parse({"name": "t", "character": "c",
                        "steps": [{"play": {"card": "X"}, "end_turn": {}}]})
    assert "single-key" in str(e.value)


def test_an_unknown_verb_is_refused_with_the_list():
    """Refused, not skipped. A mistyped step that is silently ignored is a
    scenario that passes without ever running the thing it names."""
    with pytest.raises(scenario.ScenarioError) as e:
        scenario.parse({"name": "t", "character": "c",
                        "steps": [{"playy": {"card": "X"}}]})
    assert "unknown verb" in str(e.value) and "play" in str(e.value)


def test_an_unknown_check_is_refused_with_the_list():
    with pytest.raises(scenario.ScenarioError) as e:
        scenario.parse({"name": "t", "character": "c",
                        "steps": [{"expect": {"enemy_hp": 3}}]})
    assert "unknown check" in str(e.value)


def test_a_scenario_with_no_expect_asserts_nothing_and_is_refused():
    with pytest.raises(scenario.ScenarioError) as e:
        scenario.parse({"name": "t", "character": "c",
                        "steps": [{"end_turn": {}}]})
    assert "asserts nothing" in str(e.value)


def test_a_pile_the_grant_route_does_not_have_is_refused_at_parse_time():
    with pytest.raises(scenario.ScenarioError):
        scenario.parse({"name": "t", "character": "c",
                        "steps": [{"give": {"card": "X", "pile": "exhaust"}},
                                  {"expect": {"player_block": 0}}]})


def test_set_power_needs_both_a_name_and_an_amount():
    for body in ({"amount": 2}, {"name": "SPARK_POWER"}):
        with pytest.raises(scenario.ScenarioError):
            scenario.parse({"name": "t", "character": "c",
                            "steps": [{"set_power": body},
                                      {"expect": {"player_block": 0}}]})


def test_set_power_amount_zero_is_a_removal_and_not_a_missing_field():
    """`amount: 0` is how a file asks for the power to be REMOVED (the bridge
    runs `PowerCmd.Remove` there), so the parser tests for the KEY and never
    for truthiness."""
    s = scenario.parse({"name": "t", "character": "c",
                        "steps": [{"set_power": {"name": "SPARK_POWER",
                                                 "amount": 0}},
                                  {"expect": {"player_block": 0}}]})
    assert s.steps[0][1]["amount"] == 0


def test_the_player_only_board_writes_refuse_a_who():
    """The bridge writes `set_energy` and `set_resource` to the PLAYER's combat
    state and ignores `who`. A file that named an enemy there would read as an
    enemy write and be a player write, so it is refused at parse time rather
    than posted and silently mis-attributed."""
    for verb in scenario.PLAYER_ONLY_SETUP_STEPS:
        body = {"amount": 1, "who": "first"}
        if verb == "set_resource":
            body["name"] = "KLEEMOD_ENCORE"
        with pytest.raises(scenario.ScenarioError) as e:
            scenario.parse({"name": "t", "character": "c",
                            "steps": [{verb: body},
                                      {"expect": {"player_block": 0}}]})
        assert "takes no 'who'" in str(e.value)


def test_the_setup_verbs_and_the_bridge_ops_are_one_list():
    """One door, two spellings, and they have to stay in step: a verb the file
    format accepts that the bridge has no op for is a scenario that parses and
    then fails at the machine, which is the one place nothing here can test."""
    # `give` is the one setup verb with its own endpoint (EB-52); everything
    # else in the list is a debug_state op. Stated as a subtraction rather than
    # a `set_` prefix test since EB-165, whose op moves cards and is named for
    # what it does.
    verbs = set(scenario.SETUP_STEPS) - {"give"}
    assert verbs == set(bridge.DEBUG_OPS)
    assert set(scenario.CREATURE_SETUP_STEPS)         | set(scenario.PLAYER_ONLY_SETUP_STEPS) == verbs
    # Every verb takes an amount except the ones that say they do not.
    assert set(scenario.AMOUNTLESS_SETUP_STEPS) <= verbs


@pytest.mark.parametrize("raw,want", [
    ({"end_turn": None}, {}),
    ({"set_energy": 3}, {"amount": 3}),
    ({"select": ["A", "B"]}, {"cards": ["A", "B"]}),
    ({"read": "after the play"}, {"label": "after the play"}),
])
def test_the_three_shorthands_that_read_better_in_a_file(raw, want):
    s = scenario.parse({"name": "t", "character": "c",
                        "steps": [raw, {"expect": {"player_block": 0}}]})
    assert s.steps[0][1] == want


def test_a_step_body_that_is_not_a_mapping_is_refused_rather_than_guessed():
    with pytest.raises(scenario.ScenarioError):
        scenario.parse({"name": "t", "character": "c",
                        "steps": [{"play": "Kaboom!"}]})


# ------------------------------------------------------------- resolving ---

@pytest.mark.parametrize("a,b", [
    ("KLEEMOD-TAKE_IT_FROM_THE_TOP", "Take It From the Top"),
    ("take_it_from_the_top", "TAKE IT FROM THE TOP"),
    ("KLEEMOD-POP", "Pop!"),
])
def test_the_three_spellings_of_one_card_fold_together(a, b):
    """A scenario author writes the sheet id, the loc key, or the printed
    title, and should not have to know which one this frame is using."""
    assert scenario.card_key(a) == scenario.card_key(b)


def test_two_different_cards_do_not_fold_together():
    assert scenario.card_key("pop") != scenario.card_key("powder_charge")


def test_a_card_is_found_by_id_and_by_title():
    hand = [card(name="Defend", cid="DEFEND_R"),
            card(name="Pop!", cid="KLEEMOD-POP")]
    assert scenario.find_card(hand, "KLEEMOD-POP") == 1
    assert scenario.find_card(hand, "Pop!") == 1
    assert scenario.find_card(hand, "Nothing") is None


def test_the_symbolic_targets_read_the_living_enemies_only():
    st = combat(enemies=[enemy("A_0", hp=0), enemy("B_0", hp=9),
                         enemy("C_0", hp=30)])
    assert scenario.find_enemy(st, "first")["entity_id"] == "B_0"
    assert scenario.find_enemy(st, "lowest_hp")["entity_id"] == "B_0"
    assert scenario.find_enemy(st, "highest_hp")["entity_id"] == "C_0"
    assert scenario.find_enemy(st, "B_0")["entity_id"] == "B_0"


def test_a_symbol_is_pinned_on_the_before_state_and_followed_by_id():
    """`lowest_hp` before a hit and `lowest_hp` after it are two different
    creatures. A check that re-resolved the symbol would silently compare one
    enemy's before to another enemy's after."""
    before = combat(enemies=[enemy("A_0", hp=20), enemy("B_0", hp=30)])
    after = combat(enemies=[enemy("A_0", hp=10), enemy("B_0", hp=30)])
    assert scenario._check_enemy_hp_delta(
        {"who": "lowest_hp", "amount": -10}, before, after) is None


# ---------------------------------------------------------------- checks ---

def test_hp_delta_and_hp_block_delta_disagree_exactly_where_block_stands():
    before = combat(enemies=[enemy(hp=40, block=6)])
    after = combat(enemies=[enemy(hp=39, block=0)])
    assert scenario._check_enemy_hp_delta(
        {"who": "JAW_WORM_0", "amount": -1}, before, after) is None
    assert scenario._check_enemy_hp_block_delta(
        {"who": "JAW_WORM_0", "amount": -7}, before, after) is None


def test_a_wrong_delta_names_both_readings():
    before = combat(enemies=[enemy(hp=40)])
    after = combat(enemies=[enemy(hp=35)])
    why = scenario._check_enemy_hp_delta(
        {"who": "JAW_WORM_0", "amount": -10}, before, after)
    assert "-5" in why and "40" in why and "35" in why


def test_the_splash_check_counts_an_enemy_the_hit_killed():
    """The denominator is the BEFORE state on purpose: a dead enemy is gone
    from `battle.enemies`, and on a splash card that is the interesting one."""
    before = combat(enemies=[enemy("A_0", hp=20), enemy("B_0", hp=5)])
    after = combat(enemies=[enemy("A_0", hp=11)])
    assert scenario._check_each_enemy_hp_block_delta(
        {"amount": -9, "at_least": 2}, before, after) is None


def test_the_splash_check_refuses_a_fight_that_is_too_small_to_answer():
    before = combat(enemies=[enemy("A_0", hp=20)])
    why = scenario._check_each_enemy_hp_block_delta(
        {"amount": -9, "at_least": 2}, before, before)
    assert "at least 2" in why


def test_a_survivor_that_took_the_wrong_amount_is_named():
    before = combat(enemies=[enemy("A_0", hp=20), enemy("B_0", hp=20)])
    after = combat(enemies=[enemy("A_0", hp=11), enemy("B_0", hp=20)])
    why = scenario._check_each_enemy_hp_block_delta(
        {"amount": -9, "at_least": 2}, before, after)
    assert "B_0" in why


def test_power_stacks_and_absence():
    after = combat(enemies=[enemy(status=[{"name": "Bomb", "amount": 1}])],
                   status=[{"name": "Spark", "amount": 2}])
    assert scenario._check_power(
        {"who": "player", "name": "Spark", "stacks": 2}, after, after) is None
    assert scenario._check_power(
        {"who": "JAW_WORM_0", "name": "Bomb", "stacks": 1}, after, after) is None
    assert scenario._check_no_power(
        {"who": "player", "name": "Bomb"}, after, after) is None
    assert "still present" in scenario._check_no_power(
        {"who": "player", "name": "Spark"}, after, after)


def test_a_missing_resources_key_is_reported_as_a_missing_instrument():
    """The ABSENCE of `player.resources` means the bridge predates P1.5; an
    EMPTY map means nothing is registered. gits/GitsResources.cs draws that
    distinction deliberately and a check that blurred it would report a missing
    instrument as a wrong number."""
    st = combat()
    st["player"].pop("resources")
    why = scenario._check_resource({"name": "KLEEMOD_ENCORE", "amount": 1},
                                   st, st)
    assert "predates P1.5" in why


def test_a_resource_that_is_not_registered_lists_the_ones_that_are():
    st = combat(resources={"KLEEMOD_ENCORE": 3})
    why = scenario._check_resource({"name": "KLEEMOD_FANFARE", "amount": 1},
                                   st, st)
    assert "KLEEMOD_ENCORE" in why


def test_can_play_failure_carries_the_reason_the_game_gave():
    st = combat(hand=[card(name="Hold the Line", cid="KLEEMOD-HOLD_THE_LINE",
                           can_play=False, reason="BlockedByCardLogic")])
    why = scenario._check_can_play(
        {"card": "Hold the Line", "value": True}, st, st)
    assert "BlockedByCardLogic" in why
    assert scenario._check_unplayable_reason(
        {"card": "Hold the Line", "value": "BlockedByCardLogic"},
        st, st) is None
    assert scenario._check_unplayable_reason(
        {"card": "Hold the Line", "value": None}, st, st) is not None


def test_prompt_equality_and_containment_read_the_active_screen():
    st = combat(select=("hand_select",
                        {"prompt": "Select a card to Exhaust.", "cards": []}))
    assert scenario._check_prompt("Select a card to Exhaust.", st, st) is None
    assert scenario._check_prompt_contains("exhaust", st, st) is None
    assert "does not contain" in scenario._check_prompt_contains("Upgrade", st, st)


def test_description_contains_reads_the_wire_text_not_a_sheet():
    st = combat(hand=[card(name="Hold the Line", desc="Spend 2 Sparks. Gain 5 Block.")])
    assert scenario._check_description_contains(
        {"card": "Hold the Line", "text": "Spend 2"}, st, st) is None


# ---------------------------------------------------------------- runner ---

def test_a_scenario_without_a_why_is_refused_before_anything_is_posted():
    s = scenario.parse({"name": "t", "character": "c",
                        "steps": [{"expect": {"player_block": 0}}]})
    with pytest.raises(scenario.ScenarioError) as e:
        scenario.Runner(s, "   ", wire=FakeWire([combat()]))
    assert "--why" in str(e.value)


def test_the_guardrail_rides_on_every_row_not_once_at_the_top():
    """GitsGiveCard's own reasoning applied to this log: a caveat outside the
    record is a caveat lost the moment two records are concatenated."""
    ok, r, _, buf = run_scenario(
        [{"give": {"card": "KLEEMOD-POP", "pile": "hand"}},
         {"expect": {"player_block": 0}}],
        [combat()])
    assert ok
    rows = [json.loads(x) for x in buf.getvalue().splitlines()]
    assert rows, "the runner wrote nothing"
    assert all(row["guardrail"] == bridge.GRANT_GUARDRAIL for row in rows)
    assert all(row["why"] == "a test" for row in rows)


def test_the_stated_reason_travels_onto_every_board_write():
    _, _, wire, _ = run_scenario(
        [{"set_energy": 3}, {"expect": {"player_block": 0}}], [combat()])
    assert wire.debugs == [{"op": "set_energy", "why": "a test", "amount": 3,
                            "who": "player", "resource": "", "power": ""}]


def test_a_play_resolves_the_card_at_the_state_it_is_about_to_post_into():
    """R93 revision #7's rule, and the place it is easiest to get wrong: a
    scenario is written in card NAMES, and index 2 is a different card one
    frame later."""
    first = combat(hand=[card(name="Defend"), card(name="Pop!")],
                   enemies=[enemy()])
    moved = combat(hand=[card(name="Pop!"), card(name="Defend")],
                   enemies=[enemy()])
    ok, _, wire, _ = run_scenario(
        [{"play": {"card": "Pop!", "target": "first"}},
         {"expect": {"player_block": 0}}],
        [first, moved, moved])
    # The read the runner makes INSIDE `_do_play` is the one that counts, and
    # it is the second state -- where Pop! sits at index 0, not index 1.
    assert wire.posts[0] == {"action": "play_card", "card_index": 0,
                             "target": "JAW_WORM_0"}


def test_a_card_that_is_not_in_hand_fails_with_the_hand_printed():
    ok, r, _, _ = run_scenario(
        [{"play": {"card": "Pop!"}}, {"expect": {"player_block": 0}}],
        [combat(hand=[card(name="Defend")])])
    assert not ok
    assert "Defend" in r.failures[0]["detail"]


def test_an_enemy_the_fight_does_not_have_fails_with_the_ids_printed():
    ok, r, _, _ = run_scenario(
        [{"play": {"card": "Pop!", "target": "SLIME_9"}},
         {"expect": {"player_block": 0}}],
        [combat(hand=[card(name="Pop!")], enemies=[enemy("JAW_WORM_0")])])
    assert not ok
    assert "JAW_WORM_0" in r.failures[0]["detail"]


def test_the_two_selection_screens_get_their_two_different_verbs():
    hs = combat(select=("hand_select",
                        {"prompt": "p", "cards": [card(name="Tide of Names")]}))
    cs = combat(select=("card_select",
                        {"prompt": "p", "cards": [card(name="Center Stage")]}))
    _, _, w1, _ = run_scenario([{"select": ["Tide of Names"]},
                                {"expect": {"player_block": 0}}], [hs])
    _, _, w2, _ = run_scenario([{"select": ["Center Stage"]},
                                {"expect": {"player_block": 0}}], [cs])
    assert w1.posts[0] == {"action": "combat_select_card", "card_index": 0}
    assert w2.posts[0] == {"action": "select_card", "index": 0}


def test_a_confirm_on_a_screen_that_already_closed_is_recorded_not_failed():
    """A `card_select` of the "choose" type takes the pick immediately
    (raw-full.md:728). A scenario that wrote `confirm` after one would
    otherwise fail on a screen that did exactly what it was asked."""
    ok, _, wire, buf = run_scenario(
        [{"confirm": {}}, {"expect": {"player_block": 0}}], [combat()])
    assert ok
    assert wire.posts == []
    rows = [json.loads(x) for x in buf.getvalue().splitlines()]
    assert any("skipped" in row for row in rows)


def test_a_bridge_refusal_stops_the_scenario_rather_than_rolling_on():
    ok, r, _, _ = run_scenario(
        [{"end_turn": {}}, {"expect": {"player_block": 99}}],
        [combat()], post_answer={"status": "error", "message": "not your turn"})
    assert not ok
    assert "not your turn" in r.failures[0]["detail"]


def test_a_failed_grant_is_a_failure_and_the_later_expects_do_not_run():
    """Fail-fast, and not for tidiness: an expect that fails after a failed
    grant is not a second finding, it is the same one wearing a new number."""
    ok, r, _, _ = run_scenario(
        [{"give": {"card": "KLEEMOD-NOPE", "pile": "hand"}},
         {"expect": {"player_block": 0}}],
        [combat()], grant={"status": "error", "message": "No card with id"})
    assert not ok
    assert len(r.failures) == 1 and r.failures[0]["step"] == "give"


def test_a_failed_expect_records_both_readings_for_the_printed_diff():
    ok, r, _, _ = run_scenario(
        [{"end_turn": {}}, {"expect": {"player_block": {"amount": 12}}}],
        [combat(block=0)])
    assert not ok
    f = r.failures[0]
    assert f["check"] == "player_block"
    assert "before" in f and "after" in f
    assert f["after"]["player"]["block"] == 0


def test_a_board_write_resolves_its_creature_selector_before_posting():
    """DEFECT A, from the first live run (EB-146). `set_block: {who: first}`
    posted the literal string `first` and the bridge answered *No living
    creature named 'first'. Use "player", or one of the entity ids the last GET
    reported: ...*. `play` had resolved its target through `find_enemy` since
    day one; the board writes handed the raw string over. The living-only
    filter is pinned here too -- the dead slime is not `first`."""
    st = combat(enemies=[enemy("TWIG_SLIME_S_0", hp=0),
                         enemy("TWIG_SLIME_M_0", hp=12),
                         enemy("LEAF_SLIME_S_0", hp=9)])
    ok, _, wire, _ = run_scenario(
        [{"set_block": {"who": "first", "amount": 0}},
         {"expect": {"player_block": 0}}], [st])
    assert ok
    assert wire.debugs[0]["who"] == "TWIG_SLIME_M_0"


def test_a_board_write_logs_both_the_selector_and_the_id_it_resolved_to():
    """A log read back later has to say WHICH creature moved without
    re-deriving a symbol against a board it no longer has."""
    st = combat(enemies=[enemy("JAW_WORM_0", hp=40)])
    _, _, _, buf = run_scenario(
        [{"set_hp": {"who": "lowest_hp", "amount": 5}},
         {"expect": {"player_block": 0}}], [st])
    rows = [json.loads(x) for x in buf.getvalue().splitlines()]
    row = next(r for r in rows if r.get("step") == "set_hp")
    assert row["selector"] == "lowest_hp"
    assert row["resolved_who"] == "JAW_WORM_0"


def test_a_board_write_selector_that_names_nothing_fails_before_it_posts():
    ok, r, wire, _ = run_scenario(
        [{"set_block": {"who": "SLIME_9", "amount": 0}},
         {"expect": {"player_block": 0}}],
        [combat(enemies=[enemy("JAW_WORM_0")])])
    assert not ok
    assert wire.debugs == []
    assert "JAW_WORM_0" in r.failures[0]["detail"]


def test_the_player_selector_is_passed_through_as_itself():
    _, _, wire, _ = run_scenario(
        [{"set_block": {"who": "player", "amount": 0}},
         {"expect": {"player_block": 0}}], [combat()])
    assert wire.debugs[0]["who"] == "player"


def test_clear_hand_posts_the_op_with_no_who_and_no_amount():
    """EB-165. The op empties the LOCAL PLAYER's hand and there is no partial
    form, so the POST carries neither a creature nor a count."""
    _, _, wire, _ = run_scenario(
        [{"clear_hand": None}, {"expect": {"player_block": 0}}],
        [combat(hand=[card()]), combat()])
    assert wire.debugs == [{"op": "clear_hand", "why": "a test", "amount": 0,
                            "who": "player", "resource": "", "power": ""}]


def test_clear_hand_refuses_an_amount():
    with pytest.raises(scenario.ScenarioError) as e:
        scenario.parse({"name": "t", "character": "c",
                        "steps": [{"clear_hand": {"amount": 3}},
                                  {"expect": {"player_block": 0}}]})
    assert "takes no 'amount'" in str(e.value)


def test_clear_hand_fails_the_step_when_the_hand_does_not_empty():
    """The bound is a REFUSAL and not a timeout that shrugs: a hand still
    holding cards after the clear is a board the next grant lands on top of,
    and a wrong board in a design-blind packet is invisible to the grader."""
    ok, r, _, _ = run_scenario(
        [{"clear_hand": None}, {"expect": {"player_block": 0}}],
        [combat(hand=[card()])])
    assert not ok
    assert r.failures[0]["check"] == "clear_hand"
    assert "did not empty" in r.failures[0]["detail"]


def test_a_set_power_step_posts_the_power_id_beside_the_resolved_creature():
    st = combat(enemies=[enemy("JAW_WORM_0")])
    _, _, wire, _ = run_scenario(
        [{"set_power": {"who": "first", "name": "VULNERABLE_POWER",
                        "amount": 2}},
         {"expect": {"player_block": 0}}], [st])
    assert wire.debugs[0] == {"op": "set_power", "why": "a test", "amount": 2,
                              "who": "JAW_WORM_0", "resource": "",
                              "power": "VULNERABLE_POWER"}


def test_a_queued_write_is_settled_before_the_next_assertion_reads_it():
    """`set_hp` and `set_energy` answer `queued: true` -- they go through async
    commands that run visuals. Trusting the answer instead of settling is how
    the next assertion races the write."""
    _, _, wire, _ = run_scenario(
        [{"set_hp": {"who": "player", "amount": 30}},
         {"expect": {"player_block": 0}}],
        [combat()], debug={"status": "ok", "queued": True})
    assert wire.reads >= 2


# --------------------------------------------------------- where it lives --

def test_the_soak_cannot_reach_a_scenario():
    """The soak's whole claim is that its runs are runs the game generated.
    Every scenario grants a card and writes a board, so a scenario reachable
    from an unattended overnight loop is a way for that claim to become false
    while nobody is watching. Same pin, same reason, as
    `test_understudy_give_card.test_the_soak_has_no_grant_verb`."""
    import ast

    from understudy import soak
    assert not hasattr(soak, "scenario")

    src = Path(soak.__file__).read_text(encoding="utf-8")
    # The IMPORT is the claim, checked structurally rather than by substring:
    # `soak.py` names `scenario.py` in the comment that explains why
    # `run_scripted` was factored out, and a bare grep would read that
    # explanation as the violation it is explaining.
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            assert all("scenario" not in a.name for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert "scenario" not in (node.module or "")
            assert all(a.name != "scenario" for a in node.names)
    # And the two doors themselves are unreachable from here, by the same
    # substring rule `test_understudy_give_card` applies to the grant verb.
    assert "debug_state" not in src
    assert "give_card" not in src


def test_the_scenario_runner_is_on_the_harness_side_of_the_line():
    """It reuses `soak.run_scripted` to REACH a fight -- that direction is
    fine and is the point of the factoring. The direction that must never
    exist is the other one."""
    src = (Path(scenario.__file__)).read_text(encoding="utf-8")
    assert "soak.run_scripted" in src


# -------------------------------------------------------------- the pack ---

def _sheet_names() -> set[str]:
    names: set[str] = set()
    for sheet in sorted(DOCS.glob("*-cards.yaml")) + \
            sorted(DOCS.glob("*-companions.yaml")):
        rows = yaml.safe_load(sheet.read_text(encoding="utf-8")) or []
        for row in rows:
            if not isinstance(row, dict):
                continue
            for key in ("id", "name"):
                if row.get(key):
                    names.add(scenario.card_key(str(row[key])))
    return names


def test_every_scenario_in_the_pack_parses():
    files = scenario.all_scenarios()
    assert files, "the pack is empty"
    for p in files:
        scenario.load(p)          # raises on anything malformed


def test_the_pack_exercises_the_set_power_door():
    """EB-146's acceptance shape: the op does not ship without a file that
    runs it, for the reason `test_every_scenario_in_the_pack_parses` exists --
    an instrument nothing points at is not an instrument."""
    verbs = {v for p in scenario.all_scenarios()
             for v, _ in scenario.load(p).steps}
    assert "set_power" in verbs


def test_every_card_a_scenario_names_exists_on_a_sheet_or_is_a_declared_token():
    """The lint that makes a typo in a card name a red test rather than a live
    session's wasted hour. Tokens are not on any sheet by construction, so they
    are declared in `scenario.TOKEN_CARDS` with the reason each is reachable --
    a list, not a switched-off check."""
    sheet = _sheet_names()
    tokens = {scenario.card_key(k) for k in scenario.TOKEN_CARDS}
    # EB-147: prototype rows are resolvable while a slice is STAGED and absent
    # the rest of the time, which is the quarantine working rather than a gap.
    # A `prototype: true` file is checked against the surface as it stands.
    proto: set[str] = set()
    for card in loader.prototype_cards():
        proto.add(scenario.card_key(card.id))
        if card.name:
            proto.add(scenario.card_key(card.name))
    unknown: list[str] = []
    for p in scenario.all_scenarios():
        s = scenario.load(p)
        if s.prototype:
            continue           # covered by the prototype lint below instead
        for name in s.cards_named():
            if scenario.card_key(name) not in sheet | tokens | proto:
                unknown.append(f"{p.name}: {name}")
    assert not unknown, "cards named by a scenario that exist nowhere: " + \
        ", ".join(unknown)


def test_a_prototype_scenario_grants_only_prototype_ids():
    """EB-147 (R213 B): the half of the name lint that survives an empty surface.

    A `prototype: true` file names cards that exist only while their slice is
    staged, so "does this name resolve" is unanswerable in the committed tree.
    What IS answerable, and what actually protects the deferred live run, is
    that every id it GRANTS carries the prototype prefix: a typo that reached
    for a shipped card would be granting a real card under a prototype's name,
    which is the one confusion this whole surface exists to prevent.
    """
    prefix = loader.PROTOTYPE_ID_PREFIX.upper()
    checked = 0
    for p in scenario.all_scenarios():
        s = scenario.load(p)
        if not s.prototype:
            continue
        grants = [str(body["card"]) for verb, body in s.steps
                  if verb == "give" and body.get("card")]
        assert grants, f"{p.name}: a prototype scenario that grants nothing"
        for card in grants:
            assert card.upper().startswith(f"KLEEMOD-{prefix}"), \
                f"{p.name}: {card} is not a prototype id"
        checked += 1
    assert checked, "no prototype scenario in the pack"


def test_the_pack_covers_all_three_of_the_roster_and_states_its_assumptions():
    """Every file carries `assumptions`, and the reason is in scenario.py's
    docstring: an exact expected number usually depends on something the
    scenario did not set, and a file that states nothing is a file whose
    failure means "something, somewhere"."""
    chars = set()
    for p in scenario.all_scenarios():
        s = scenario.load(p)
        chars.add(s.character)
        assert s.assumptions, f"{p.name} states no assumptions"
    assert {"KLEEMOD-KLEE", "KLEEMOD-FURINA", "KLEEMOD-KOKOMI"} <= chars


def test_every_scenario_names_a_character_the_roster_knows():
    from understudy import soak
    from tier0 import roster
    known = {c.id for c in roster.ROSTER}
    for p in scenario.all_scenarios():
        s = scenario.load(p)
        assert soak.canonical_character(s.character) in known, \
            f"{p.name}: {s.character} is not a roster member"


def test_the_declared_tokens_are_real_classes_in_the_mod():
    """A token row is a claim that the card exists in the mod and is reachable
    without a draft. The sheet lint cannot check it, so this does."""
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina"
           / "SpotlightCards.cs").read_text(encoding="utf-8")
    for cls in ("EtherealSpotlight", "CenterStageOption", "GuestCastOption"):
        assert f"class {cls}" in src
