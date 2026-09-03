"""EB-149's blind-QA funnel, with no game involved.

What a live Windows box would add is the one thing that matters least here --
whether the bridge answers. What CAN be pinned, and what this file pins:

  * the turn format's refusals, including the two-halves check that stops the
    falsifier reading a board nobody staged;
  * that the blind packet CANNOT reach a design sheet (an AST walk over
    `qa_packet.py`'s imports) and does not carry design vocabulary when built
    from a wire state that is full of it;
  * every falsifier rule, in both directions -- a complete form survives and
    each refusable form is refused BY NAME;
  * the closeness falsifier on a two-line board, once dominated and once
    close, with the constant that separates them pinned to its derivation;
  * the ledger's down-weighting, which is R213's second guard;
  * and the structural fact that `soak.py` cannot reach any of it.

Mirrors `test_understudy_scenario.py`, whose fake wire and helpers this file
reuses in shape rather than importing -- the two modules assert different
things about the same wire and a shared fixture would couple their failures.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

from understudy import qa_packet
from understudy import scenario as scenario_module
from understudy import staged_turn

REPO = Path(__file__).resolve().parents[2]
TURNS = REPO / "understudy" / "turns"
EXAMPLE = TURNS / "kokomi-first-turn-example.yaml"


# ------------------------------------------------------------- fixtures ----

class FakeWire:
    """A bridge that answers from a scripted list of states, last one
    repeating. `Runner` takes its wire as an argument precisely so this can
    exist -- see `test_understudy_scenario`, which does the same."""

    def __init__(self, states):
        self.states = list(states)
        self.posts: list[dict] = []

    def get_state(self):
        return self.states[0] if len(self.states) == 1 else self.states.pop(0)

    def post(self, **action):
        self.posts.append(action)
        return {"status": "ok", "message": "ok"}


def wire_state():
    """A live-shaped state whose every field is FULL of design vocabulary.

    That is the point: a packet built from this must come out clean, so the
    test proves the allowlist rather than the absence of a leak in a tidy
    fixture.
    """
    return {
        "state_type": "monster",
        "battle": {"round": 2, "turn": "player", "enemies": [
            {"entity_id": "JAW_WORM_0", "name": "Jaw Worm", "hp": 32,
             "max_hp": 44, "block": 0,
             "intents": [{"type": "Attack", "title": "Attack",
                          "label": "11", "description": "Deals 11 damage."}],
             "status": [{"name": "STRENGTH", "amount": 2,
                         "description": "Deals 2 more damage per hit."}]}]},
        "player": {
            "hp": 62, "max_hp": 70, "block": 0, "energy": 3,
            "resources": {"KLEEMOD_CHARGE": 8},
            "status": [{"name": "KLEEMOD_KURAGE_WARD", "title": "Kurage Ward",
                        "amount": 5, "description": "Gain 5 Block per pulse."}],
            "hand": [
                {"id": "KLEEMOD-PEARL_BARRAGE", "name": "Pearl Barrage",
                 "cost": "1", "can_play": True, "is_upgraded": False,
                 "description": "Exhaust 1 card from your hand. Deal 8 damage."},
                {"id": "KLEEMOD-CORAL_GUARD", "name": "Coral Guard",
                 "cost": "1", "can_play": False,
                 "unplayable_reason": "Not enough energy",
                 "is_upgraded": False, "description": "Gain 5 Block."},
            ]},
    }


def form(**overrides):
    base = {
        "turn_id": "t", "packet_sha256": "",
        "grader": {"id": "opus-5", "kind": "llm", "model": "claude-opus-5",
                   "designed_these_cards": False},
        "chosen_line": [{"card": "Pearl Barrage", "target": "Jaw Worm"}],
        "q1_what_did_you_play": "Pearl Barrage into the Jaw Worm.",
        "q2_other_line_considered": "Coral Guard first, then hold the attack.",
        "q3_what_it_gave_up": "The Block, and a card out of hand.",
        "q4_different_intent": "Yes -- a big attack telegraph and I block.",
        "q4_changed": True,
    }
    base.update(overrides)
    return base


def board(hand, energy=1, hp=70, enemy_hp=50, intent=None):
    return staged_turn.Board(
        character="ref_ironclad", pilot="generic", hand=list(hand),
        hp=hp, max_hp=hp, energy=energy,
        enemies=[{"name": "dummy", "hp": enemy_hp, "max_hp": enemy_hp,
                  "intent": intent or {"kind": "attack", "amount": 10}}])


# ---------------------------------------------------------------- parser ---

def test_the_shipped_example_parses():
    turn = staged_turn.load(EXAMPLE)
    assert turn.id == "kokomi-first-turn-example"
    assert len(turn.board.hand) == 5
    assert turn.assumptions


def test_staging_may_not_play_a_card():
    """A staged turn is a BOARD. The line is the grader's answer, and a file
    that played its own turn would be answering its own question."""
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.parse({"id": "t", "character": "c",
                           "staging": [{"play": {"card": "X"}}],
                           "board": {"character": "k", "hand": ["strike"],
                                     "enemies": [{"name": "d", "hp": 1}]}})
    assert "not a staging verb" in str(e.value)


def test_the_id_must_be_a_slug():
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.parse({"id": "EB-149_turn", "character": "c",
                           "staging": [{"set_energy": 3}],
                           "board": {"character": "k", "hand": ["strike"],
                                     "enemies": [{"name": "d", "hp": 1}]}})
    assert "slug" in str(e.value)


def test_an_assumption_that_cites_a_register_id_is_refused_at_parse():
    """Assumptions are folded into the packet's disclosures verbatim, and the
    packet scrub runs at EXPORT -- after the game has booted, embarked and
    boarded. The first slice cited `EB-165` in every file's assumptions,
    `check` passed all eleven, and the first `stage` burned a real launch to
    learn what a parse could have said. So the parse says it."""
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.parse({"id": "t", "character": "c",
                           "staging": [{"give": {"card": "strike"}}],
                           "board": {"character": "k", "hand": ["strike"],
                                     "enemies": [{"name": "d", "hp": 1}]},
                           "assumptions": ["The game deals its own hand on "
                                           "top of this one (EB-165)."]})
    assert "register-id" in str(e.value)
    assert "EB-165" in str(e.value)


def test_the_two_halves_must_describe_the_same_hand():
    """The staged hand and the mirrored hand are one board written twice.
    Left unchecked, `closeness` would read a board nobody staged."""
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.parse({
            "id": "t", "character": "c",
            "staging": [{"give": {"card": "KLEEMOD-STRIKE", "pile": "hand"}}],
            "board": {"character": "k", "hand": ["strike", "defend"],
                      "enemies": [{"name": "d", "hp": 1}]}})
    assert "disagree" in str(e.value)


def test_a_card_dealt_to_another_pile_is_not_part_of_the_hand():
    turn = staged_turn.parse({
        "id": "t", "character": "c",
        "staging": [{"give": {"card": "KLEEMOD-STRIKE", "pile": "hand"}},
                    {"give": {"card": "KLEEMOD-DEFEND", "pile": "draw"}}],
        "board": {"character": "k", "hand": ["strike"],
                  "enemies": [{"name": "d", "hp": 1}]}})
    assert turn.board.hand == ["strike"]


# ------------------------------------------------------------ exact hand ---

def _exact_turn(**over):
    blob = {
        "id": "t", "character": "KLEEMOD-KOKOMI", "exact_hand": True,
        "staging": [{"give": {"card": "KLEEMOD-PEARL_BARRAGE", "pile": "hand"}},
                    {"give": {"card": "KLEEMOD-CORAL_GUARD", "pile": "hand"}}],
        "board": {"character": "kokomi",
                  "hand": ["pearl_barrage", "coral_guard"],
                  "enemies": [{"name": "d", "hp": 10,
                               "intent": {"kind": "attack", "amount": 5}}]},
    }
    blob.update(over)
    return staged_turn.parse(blob)


def test_exact_hand_prepends_the_clear_before_the_first_grant():
    """EB-165. The POSITION is the whole door: after a grant the clear would
    empty the declared hand into the draw pile."""
    steps = _exact_turn().as_scenario().steps
    assert steps[0][0] == "clear_hand"
    assert [v for v, _ in steps].count("clear_hand") == 1
    assert steps[1][0] == "give"


def test_a_turn_without_the_flag_stages_exactly_as_it_did():
    steps = _exact_turn(exact_hand=False).as_scenario().steps
    assert "clear_hand" not in [v for v, _ in steps]


def test_a_turn_may_not_write_clear_hand_itself():
    with pytest.raises(staged_turn.TurnError) as e:
        _exact_turn(staging=[{"clear_hand": None},
                             {"give": {"card": "KLEEMOD-PEARL_BARRAGE",
                                       "pile": "hand"}}],
                    board={"character": "kokomi", "hand": ["pearl_barrage"],
                           "enemies": [{"name": "d", "hp": 10}]})
    assert "exact_hand" in str(e.value)


def test_execute_replays_an_exact_hand_turn_through_the_same_clear():
    """The replay opens with the same clear the stage did. Without it the
    graded line is replayed onto the DEALT hand, which is a different board --
    the guard catches that, and catching it is not replaying the turn."""
    turn = _exact_turn()
    steps = staged_turn.execute_steps(turn, form())
    assert steps[0][0] == "clear_hand"
    assert steps[1][0] == "give"
    plain = staged_turn.execute_steps(_exact_turn(exact_hand=False), form())
    assert "clear_hand" not in [v for v, _ in plain]


def test_the_exact_hand_check_folds_the_three_spellings():
    turn = _exact_turn()
    state = {"player": {"hand": [{"id": "KLEEMOD-PEARL_BARRAGE",
                                 "name": "Pearl Barrage"},
                                {"id": "KLEEMOD-CORAL_GUARD",
                                 "name": "Coral Guard"}]}}
    assert staged_turn.exact_hand_difference(turn, state) == ""


def test_the_exact_hand_check_counts_copies():
    turn = _exact_turn()
    state = {"player": {"hand": [{"id": "KLEEMOD-PEARL_BARRAGE"},
                                 {"id": "KLEEMOD-CORAL_GUARD"},
                                 {"id": "KLEEMOD-CORAL_GUARD"}]}}
    diff = staged_turn.exact_hand_difference(turn, state)
    assert "coral guard" in diff and "did not declare" in diff


def test_an_exact_hand_turn_refuses_to_write_a_packet_of_another_board(
        tmp_path, monkeypatch):
    """The acceptance, as a refusal: a turn that asked for an exact hand and
    got the dealt one writes NO packet, because a blind grader has no way to
    see that the board is not the one the file describes."""
    monkeypatch.setattr(staged_turn, "QA_DIR", tmp_path)
    turn = _exact_turn()
    state = {"state_type": "monster",
             "battle": {"round": 1, "turn": "player", "enemies": []},
             "player": {"hp": 70, "max_hp": 70, "block": 0, "energy": 3,
                        "hand": [{"id": "KLEEMOD-PEARL_BARRAGE",
                                  "name": "Pearl Barrage"},
                                 {"id": "KLEEMOD-CORAL_GUARD",
                                  "name": "Coral Guard"},
                                 {"id": "KLEEMOD-NEREIDS_ASCENSION",
                                  "name": "Nereid's Ascension"}]}}
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.export_packet(turn, state)
    assert "exact_hand" in str(e.value)
    assert not (tmp_path / "t" / "packet.md").exists()


def test_an_exact_hand_turn_writes_the_packet_when_the_hand_matches(
        tmp_path, monkeypatch):
    monkeypatch.setattr(staged_turn, "QA_DIR", tmp_path)
    turn = _exact_turn()
    state = {"state_type": "monster",
             "battle": {"round": 1, "turn": "player", "enemies": []},
             "player": {"hp": 70, "max_hp": 70, "block": 0, "energy": 3,
                        "hand": [{"id": "KLEEMOD-PEARL_BARRAGE",
                                  "name": "Pearl Barrage",
                                  "description": "Deal 5 damage."},
                                 {"id": "KLEEMOD-CORAL_GUARD",
                                  "name": "Coral Guard",
                                  "description": "Gain 5 Block."}]}}
    report = staged_turn.export_packet(turn, state)
    assert report["exact_hand"] is True
    assert report["hand"] == ["Pearl Barrage", "Coral Guard"]
    assert report["cards"] == report["declared_cards"] == 2


# ---------------------------------------------------------------- packet ---

def test_the_packet_builder_cannot_reach_a_sheet():
    """THE NO-LEAK GUARANTEE, STRUCTURALLY. `qa_packet.py` imports nothing
    from `tier0` -- not the sheet loaders, not the engine, not the pilot -- so
    the module that writes the blind packet has no route to a `role:` or an
    `archetypes:` even by accident. The scrub below is the belt to this brace,
    not the other way round."""
    src = Path(qa_packet.__file__).read_text(encoding="utf-8")
    named: list[str] = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            named += [a.name for a in node.names]
        if isinstance(node, ast.ImportFrom):
            named.append(node.module or "")
    assert not [m for m in named if m.split(".")[0] in ("tier0", "tier05")], \
        f"the blind packet builder imports {named}"


def test_the_packet_carries_no_design_vocabulary():
    """Built from a wire state stuffed with ids and mod prefixes, the packet
    comes out with none of them -- and the assertion names each thing that
    must be absent rather than trusting one regex."""
    packet = qa_packet.build(wire_state(), "kokomi-first-turn-example")
    text = qa_packet.dumps(packet) + qa_packet.render(packet)
    for forbidden in ("KLEEMOD", "pearl_barrage", "coral_guard", "role:",
                      "archetypes", "tempo_band", "solve:", "EB-149", "R213",
                      "M14", "JAW_WORM_0"):
        assert forbidden not in text, f"{forbidden!r} leaked into the packet"
    # And the printed truth IS there: a packet that leaks nothing by being
    # empty is not a packet.
    assert "Pearl Barrage" in text and "Jaw Worm" in text
    assert "Charge" in text and "Kurage Ward" in text


def test_a_leak_raises_rather_than_being_written():
    """A card face that carried a sheet field would be a packet the funnel
    must not produce, so the builder raises instead of emitting it."""
    state = wire_state()
    state["player"]["hand"][0]["description"] = "role: payoff. Deal 8 damage."
    with pytest.raises(qa_packet.PacketLeak) as e:
        qa_packet.build(state, "t")
    assert "role" in str(e.value)


def test_the_scrub_reads_values_and_not_keys():
    """`enemies`, `intent` and `hand` are this module's own words. A scrub
    that matched keys would refuse every packet it ever built."""
    assert qa_packet.leaks({"tempo_band": "Deal 8 damage."}) == []
    assert qa_packet.leaks({"safe": "tempo_band"})


def test_the_packet_says_where_each_card_text_came_from():
    packet = qa_packet.build(wire_state(), "t")
    assert all(c["text_source"] == "bridge" for c in packet["board"]["hand"])


def test_a_card_with_no_wire_text_falls_back_and_says_so():
    state = wire_state()
    state["player"]["hand"][0]["description"] = ""
    packet = qa_packet.build(state, "t", repo=REPO)
    card = packet["board"]["hand"][0]
    assert card["text_source"].startswith("generated-cs")
    assert card["text"], "the generated Localization block was not found"


def test_the_guardrail_rides_on_the_packet():
    packet = qa_packet.build(wire_state(), "t")
    assert packet["guardrail"] == qa_packet.PACKET_GUARDRAIL
    assert "fun" in qa_packet.render(packet)


# ------------------------------------------------------------ falsifiers ---

def test_a_complete_form_survives():
    v = staged_turn.grade("t", form(), root=Path("/nonexistent"))
    assert v["verdict"] == "SURVIVES"
    assert v["refused_by"] == []
    assert v["survives_alone"] is True
    assert "not yet falsified" in v["survives_means"]


@pytest.mark.parametrize("answer", ["", "none", "None.", "nothing else",
                                    "no", "N/A"])
def test_a_turn_with_no_second_line_is_refused(answer):
    """R213's readiness test, and the whole reason step two exists."""
    v = staged_turn.grade("t", form(q2_other_line_considered=answer),
                          root=Path("/nonexistent"))
    assert v["verdict"] == "REFUSED"
    assert "no_second_line" in v["refused_by"]
    assert any("no_second_line" in r for r in v["reasons"])


def test_a_long_answer_opening_with_no_is_still_an_answer():
    """The negative rule is narrow on purpose: reading this as a refusal would
    falsify a turn that passed."""
    v = staged_turn.grade("t", form(q2_other_line_considered=(
        "No line beat it outright, but I weighed Coral Guard first against "
        "leading with the attack for two turns of tempo.")),
        root=Path("/nonexistent"))
    assert v["verdict"] == "SURVIVES"


def test_an_intent_insensitive_turn_is_refused_by_the_boolean():
    v = staged_turn.grade("t", form(q4_changed=False),
                          root=Path("/nonexistent"))
    assert v["refused_by"] == ["intent_insensitive"]


def test_an_intent_insensitive_turn_is_refused_by_the_prose():
    """The boolean is not the authority on its own: a form that ticks yes and
    then writes 'no' has answered no."""
    v = staged_turn.grade("t", form(q4_different_intent="No."),
                          root=Path("/nonexistent"))
    assert "intent_insensitive" in v["refused_by"]


def test_a_designer_may_not_grade_its_own_cards():
    """R213's first guard, declared in the form rather than assumed."""
    v = staged_turn.grade("t", form(grader={"id": "x",
                                            "designed_these_cards": True}),
                          root=Path("/nonexistent"))
    assert "grader_is_designer" in v["refused_by"]


def test_an_empty_line_is_refused():
    v = staged_turn.grade("t", form(chosen_line=[]),
                          root=Path("/nonexistent"))
    assert "empty_line" in v["refused_by"]


def test_a_form_answered_against_another_packet_is_refused(tmp_path):
    d = tmp_path / "t"
    d.mkdir()
    (d / "packet.md").write_text("a board\n", encoding="utf-8")
    v = staged_turn.grade("t", form(packet_sha256="0" * 64), root=tmp_path)
    assert "packet_mismatch" in v["refused_by"]
    ok = staged_turn.grade(
        "t", form(packet_sha256=qa_packet.sha256("a board\n")), root=tmp_path)
    assert ok["verdict"] == "SURVIVES"


def test_a_dominated_turn_is_refused_from_the_closeness_file(tmp_path):
    d = tmp_path / "t"
    d.mkdir()
    (d / "closeness.json").write_text(
        json.dumps({"verdict": "REFUSED", "gap": 0.9}), encoding="utf-8")
    v = staged_turn.grade("t", form(), root=tmp_path)
    assert "line_dominates" in v["refused_by"]


def test_every_refusal_names_a_rule_that_exists():
    v = staged_turn.grade("t", form(chosen_line=[], q4_changed=False,
                                    q2_other_line_considered="none"),
                          root=Path("/nonexistent"))
    assert set(v["refused_by"]) <= set(staged_turn.FALSIFIERS)
    assert len(v["reasons"]) == len(v["refused_by"])


def test_a_verdict_carries_its_quotability_and_its_guardrail():
    v = staged_turn.grade("t", form(), root=Path("/nonexistent"))
    assert "quotable" in v["closeness_quotability"]
    assert v["guardrail"] == qa_packet.PACKET_GUARDRAIL


# ------------------------------------------------------------- closeness ---

def test_a_dominated_pair_is_refused():
    """Two energy, Strike or Bash. Bash is worth more than twice the Strike in
    the pilot's own currency, which is exactly what the constant means."""
    r = staged_turn.closeness(board(["strike", "bash"], energy=2))
    assert r["applicable"] is True
    assert r["verdict"] == "REFUSED"
    assert r["gap"] > staged_turn.DOMINANCE_GAP


def test_a_close_pair_survives():
    r = staged_turn.closeness(board(["strike", "defend"], energy=1))
    assert r["verdict"] == "SURVIVES"
    assert r["gap"] <= staged_turn.DOMINANCE_GAP


def test_closeness_collapses_orderings_onto_sets():
    """The playout is ORDERED, the comparison is over SETS. Without the
    collapse the top two would be two orderings of the same three cards, the
    gap would be near zero, and the falsifier would refuse nothing ever."""
    r = staged_turn.closeness(board(["strike", "defend", "bash"], energy=3))
    # 3 singles + 3 pairs. The triple costs 4 and three energy does not buy
    # it, so it is not a line -- which is the other half of the collapse: an
    # unplayable ordering leaves the enumeration rather than scoring zero.
    assert r["lines_considered"] == 6
    assert all(len(set(line["cards"])) == len(line["cards"])
               for line in r["lines"])


def test_a_card_the_sim_cannot_represent_refuses_the_falsifier():
    """Guessing at a missing card would be scoring a line nobody could play."""
    r = staged_turn.closeness(board(["strike", "not_a_real_card"]))
    assert r["applicable"] is False
    assert r["verdict"] == "NOT READ"
    assert "not_a_real_card" in r["unrepresentable"]


def test_a_one_line_board_is_not_read():
    r = staged_turn.closeness(board(["strike"], energy=1))
    assert r["applicable"] is False
    assert "second line" in r["reason"]


def test_the_enumeration_bound_refuses_rather_than_truncating():
    """A gap that depends on which lines happened to be enumerated first is
    not a reading, so the bound refuses instead of sampling."""
    r = staged_turn.closeness(board(["strike", "defend", "bash"], energy=3),
                              max_lines=2)
    assert r["applicable"] is False
    assert "bound" in r["reason"]


def test_dominance_gap_is_the_pilots_own_doubling():
    """DOMINANCE_GAP is DERIVED (R212), and this is the derivation as an
    assertion: 0.5 is exactly the gap at which the best line is worth twice
    the runner-up. Moving the constant without moving this line is moving a
    number that was not picked."""
    assert staged_turn.DOMINANCE_GAP == 0.5
    best, runner_up = 2.0, 1.0
    assert (best - runner_up) / best == staged_turn.DOMINANCE_GAP


def test_the_closeness_reading_carries_its_licence():
    r = staged_turn.closeness(board(["strike", "defend"], energy=1))
    assert "quotable" in r["quotability"]
    assert "never a claim that a decision is fun" in r["quotability"]
    assert r["guardrail"] == qa_packet.PACKET_GUARDRAIL


# --- the prototype dev route (R213 B) --------------------------------------
#
# A quarantined row is absent from `loader._card_index()` BY CONSTRUCTION, so
# the falsifier reaches one only down a route the turn file DECLARES. These
# four tests are that route in both directions: it opens on the flag, it is
# shut without it, and a shut door says which thing went wrong.

def _proto_id() -> str:
    """One prototype id off the SHIPPED surface, or skip.

    Read from the surface rather than fixtured, because R213 B's deletion
    rule makes the surface empty between slices and a fixture row here would
    be the second permanent pool the ruling forbids, one row deep.
    """
    from tier0.content import loader
    rows = loader.prototype_cards()
    if not rows:
        pytest.skip("the prototype surface is empty (the healthy state)")
    return rows[0].id


def test_a_prototype_id_is_refused_when_the_turn_does_not_declare_one():
    """REFUSED BY NAME, not answered NOT READ. Falling through to
    `unrepresentable` would report "the sim cannot model this card" when what
    actually happened is that the file forgot to say what it was, and two
    very different facts must not share one output."""
    with pytest.raises(staged_turn.TurnError) as exc:
        staged_turn.closeness(board(["strike", _proto_id()]))
    assert _proto_id() in str(exc.value)
    assert "prototype: true" in str(exc.value)


def test_a_declared_prototype_turn_resolves_the_row():
    """The door opens, and the card is the sheet's own row rather than an
    approximation -- so the line the falsifier scores is a line somebody
    could play."""
    r = staged_turn.closeness(board(["strike", _proto_id()], energy=3),
                              prototype=True)
    assert r["source"] == "declared board (prototype route)"
    assert not r.get("unrepresentable")
    assert r["lines_considered"] > 1


def test_the_declared_route_does_not_widen_the_ordinary_one():
    """The flag opens the prototype surface and NOTHING else: a typo is still
    a typo. Without this the fix would trade a refused prototype for an
    unrefusable misspelling."""
    r = staged_turn.closeness(board(["strike", "not_a_real_card"]),
                              prototype=True)
    assert r["verdict"] == "NOT READ"
    assert "not_a_real_card" in r["unrepresentable"]


def test_the_turn_files_prototype_flag_mirrors_the_scenarios():
    """Same spelling, same default, and it reaches `as_scenario` -- one word
    for one idea across the two halves of the harness."""
    import yaml

    example = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    assert staged_turn.parse(example).prototype is False
    turn = staged_turn.parse(dict(example, prototype=True))
    assert turn.prototype is True
    assert turn.as_scenario().prototype is True


def test_check_finds_turns_in_a_slice_subdirectory(tmp_path):
    """A slice is a set of MATCHED PAIRS that only mean anything together, so
    they live in one subdirectory; `check` has to see them there or half the
    parse gate silently stops applying. `fixtures/` stays excluded -- it holds
    grader forms, not turns."""
    (tmp_path / "slice").mkdir()
    (tmp_path / "slice" / "a.yaml").write_text("{}", encoding="utf-8")
    (tmp_path / "fixtures").mkdir()
    (tmp_path / "fixtures" / "form.yaml").write_text("{}", encoding="utf-8")
    found = [p.name for p in staged_turn.all_turns(tmp_path)]
    assert found == ["a.yaml"]


def test_the_example_turn_has_more_than_one_line():
    """The worked example, read by the falsifier it ships with."""
    r = staged_turn.closeness(staged_turn.load(EXAMPLE).board)
    assert r["applicable"] is True
    assert r["lines_considered"] > 1


# ---------------------------------------------------------------- ledger ---

def _verdict_file(root, turn, gid, q2, line=("Pearl Barrage",), q4="Yes."):
    d = root / turn
    d.mkdir(parents=True, exist_ok=True)
    (d / "packet.json").write_text(json.dumps(
        {"board": {"hand": [{"title": "Pearl Barrage"},
                            {"title": "Coral Guard"}]}}), encoding="utf-8")
    (d / f"verdict-{gid}.json").write_text(json.dumps({
        "turn_id": turn, "verdict": "SURVIVES", "refused_by": [],
        "grader": {"id": gid}, "survives_alone": True,
        "chosen_line": [{"card": c} for c in line],
        "answers": {"q1_what_did_you_play": "x",
                    "q2_other_line_considered": q2,
                    "q3_what_it_gave_up": "x",
                    "q4_different_intent": q4}}), encoding="utf-8")


def test_the_ledger_shows_agreement_per_question(tmp_path):
    _verdict_file(tmp_path, "turn-a", "user", "Coral Guard first.")
    _verdict_file(tmp_path, "turn-a", "opus-5", "Coral Guard first.")
    rows = [r.split("\t") for r in
            staged_turn.build_ledger(tmp_path).splitlines()
            if r and not r.startswith("#")]
    header, body = rows[0], rows[1:]
    agent = next(r for r in body if r[header.index("grader")] == "opus-5")
    assert agent[header.index("agree_q2")] == "yes"
    assert agent[header.index("agree_q1")] == "yes"
    # [USER]'s own row is never compared against itself.
    user = next(r for r in body if r[header.index("grader")] == "user")
    assert user[header.index("agree_q2")] == "-"


def test_a_grader_that_keeps_disagreeing_loses_its_solo_survives(tmp_path):
    """R213's second guard, made concrete: three disagreements in the last
    five shared turns and the agent's SURVIVES needs [USER]'s beside it."""
    for i in range(3):
        _verdict_file(tmp_path, f"turn-{i}", "user", "Coral Guard first.")
        _verdict_file(tmp_path, f"turn-{i}", "opus-5", "Pearl Barrage again.")
    (tmp_path / "ledger.tsv").write_text(
        staged_turn.build_ledger(tmp_path), encoding="utf-8")

    down, why = staged_turn.is_down_weighted("opus-5", root=tmp_path)
    assert down and "down-weighted" in why
    v = staged_turn.grade("turn-9", form(), root=tmp_path)
    assert v["verdict"] == "SURVIVES"
    assert v["survives_alone"] is False
    assert "question two" in v["why_not_alone"]


def test_two_disagreements_are_not_enough(tmp_path):
    for i in range(2):
        _verdict_file(tmp_path, f"turn-{i}", "user", "Coral Guard first.")
        _verdict_file(tmp_path, f"turn-{i}", "opus-5", "Pearl Barrage again.")
    (tmp_path / "ledger.tsv").write_text(
        staged_turn.build_ledger(tmp_path), encoding="utf-8")
    assert staged_turn.is_down_weighted("opus-5", root=tmp_path)[0] is False


def test_user_is_never_down_weighted(tmp_path):
    assert staged_turn.is_down_weighted("user", root=tmp_path) == (False, "")


def test_an_uncomparable_answer_is_not_a_disagreement(tmp_path):
    """Neither answer naming a card is an absent comparison, not a
    disagreement -- otherwise prose that happens to avoid card names would
    down-weight a grader that agreed."""
    _verdict_file(tmp_path, "turn-a", "user", "I thought about blocking.")
    _verdict_file(tmp_path, "turn-a", "opus-5", "I thought about blocking.")
    rows = [r.split("\t") for r in
            staged_turn.build_ledger(tmp_path).splitlines()
            if r and not r.startswith("#")]
    agent = next(r for r in rows[1:] if r[1] == "opus-5")
    assert agent[rows[0].index("agree_q2")] == "-"


def test_the_ledger_carries_the_guardrail_and_the_rule(tmp_path):
    _verdict_file(tmp_path, "turn-a", "opus-5", "Coral Guard first.")
    text = staged_turn.build_ledger(tmp_path)
    assert qa_packet.PACKET_GUARDRAIL in text
    assert "down-weighting" in text


# ------------------------------------------------------------ structural ---

def test_the_soak_cannot_reach_a_staged_turn():
    """The soak's claim is that its runs are runs the game generated. A staged
    turn grants five cards and writes a board, so it lives on the attended
    side of the line -- the same pin `test_understudy_scenario` puts on the
    scenario harness."""
    from understudy import soak
    assert not hasattr(soak, "staged_turn")
    assert not hasattr(soak, "qa_packet")
    # The FAMILY `EB-180` split the soak into, not the facade alone.
    from tier0.tests.conftest import seam_files
    for path in seam_files("soak"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                assert not any(a.name.endswith(("staged_turn", "qa_packet"))
                               for a in node.names), path
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").endswith(("staged_turn",
                                                         "qa_packet")), path
                assert not any(a.name in ("staged_turn", "qa_packet")
                               for a in node.names), path


def test_the_form_questions_are_r213s_verbatim():
    """The four questions live in three places -- the ruling, the tool and the
    template -- and the two this repo owns must not drift."""
    text = (REPO / "understudy" / "qa_form.md").read_text(encoding="utf-8")
    for question in staged_turn.QUESTIONS.values():
        assert question in text, f"qa_form.md does not print {question!r}"
    prompt = (REPO / "understudy" / "qa_grader_prompt.md").read_text(
        encoding="utf-8")
    for question in staged_turn.QUESTIONS.values():
        assert question in prompt


def test_the_grader_prompt_forbids_a_quality_verdict():
    prompt = (REPO / "understudy" / "qa_grader_prompt.md").read_text(
        encoding="utf-8")
    assert "not being asked whether this is fun" in prompt
    assert "no tools" in prompt or "no repo access" in prompt


def test_execute_translates_titles_and_never_ids():
    """The agent's line is printed titles; the play steps carry them through
    unchanged and `scenario.find_card` does the translation at the POST."""
    turn = staged_turn.load(EXAMPLE)
    steps = staged_turn.execute_steps(
        turn, form(chosen_line=[{"card": "Bake-Kurage"},
                                {"card": "Pearl Barrage", "target": "Jaw Worm"}]))
    plays = [b for v, b in steps if v == "play"]
    assert [p["card"] for p in plays] == ["Bake-Kurage", "Pearl Barrage"]
    assert plays[1]["target"] == "Jaw Worm"
    assert any(v == "mark" for v, _ in steps), \
        "without a mark the outcome brackets the last play, not the line"


# --------------------------------------------------------------- fixtures --

FIXTURES = REPO / "understudy" / "turns" / "fixtures"


def test_the_shipped_fixture_forms_grade_both_ways():
    """The two directions on the SHIPPED example, through the real files an
    orchestrator would hand the tool -- not a dict built in this module."""
    survives = staged_turn.grade(
        "kokomi-first-turn-example",
        staged_turn.load_form(FIXTURES / "form-complete.json"),
        root=Path("/nonexistent"))
    assert survives["verdict"] == "SURVIVES"
    refused = staged_turn.grade(
        "kokomi-first-turn-example",
        staged_turn.load_form(FIXTURES / "form-no-second-line.json"),
        root=Path("/nonexistent"))
    assert refused["refused_by"] == ["no_second_line"]


def test_the_fixture_forms_answer_the_committed_packet():
    """A form is answered against ONE board. If the example is re-staged the
    packet's hash moves and these two files are answers to a board that no
    longer exists -- which is what `packet_mismatch` refuses at grade time and
    what this pin surfaces at test time instead of six months later."""
    packet = json.loads((REPO / "review" / "qa" / "kokomi-first-turn-example"
                         / "packet.json").read_text(encoding="utf-8"))
    for name in ("form-complete.json", "form-no-second-line.json"):
        form_blob = staged_turn.load_form(FIXTURES / name)
        assert form_blob["packet_sha256"] == packet["packet_sha256"], name


def test_a_fixture_form_names_only_printed_titles():
    """The grader never sees an id, so a form cannot contain one."""
    packet = json.loads((REPO / "review" / "qa" / "kokomi-first-turn-example"
                         / "packet.json").read_text(encoding="utf-8"))
    titles = {c["title"] for c in packet["board"]["hand"]}
    for name in ("form-complete.json", "form-no-second-line.json"):
        blob = staged_turn.load_form(FIXTURES / name)
        for play in blob["chosen_line"]:
            assert play["card"] in titles, f"{name}: {play['card']!r}"


# ------------------------------------------------- the seed and the board --

def test_stage_records_the_seed_the_game_actually_used(tmp_path, monkeypatch):
    """The encounter is generated from the run seed, so a packet without one
    cannot be replayed -- which is what the first live `execute` proved by
    rolling its own and drawing a different monster."""
    turn = staged_turn.load(EXAMPLE)
    monkeypatch.setattr(staged_turn, "QA_DIR", tmp_path)
    report = staged_turn.export_packet(turn, wire_state(), run_seed="HKB8EJD5G4")
    blob = json.loads((tmp_path / turn.id / "packet.json").read_text(
        encoding="utf-8"))
    observed = json.loads((tmp_path / turn.id / "observed.json").read_text(
        encoding="utf-8"))
    assert report["run_seed"] == "HKB8EJD5G4"
    assert blob["run_seed"] == "HKB8EJD5G4"
    assert observed["run_seed"] == "HKB8EJD5G4"


def test_the_seed_is_not_on_the_page_the_grader_reads(tmp_path, monkeypatch):
    """`packet_sha256` and `run_seed` are envelope keys on the JSON, added
    after the scrub. Neither is rendered into `packet.md`, which is the page a
    grader is handed -- and which is what the hash is taken over, so recording
    a seed cannot move it."""
    turn = staged_turn.load(EXAMPLE)
    monkeypatch.setattr(staged_turn, "QA_DIR", tmp_path)
    with_seed = staged_turn.export_packet(turn, wire_state(),
                                          run_seed="HKB8EJD5G4")
    md = (tmp_path / turn.id / "packet.md").read_text(encoding="utf-8")
    assert "HKB8EJD5G4" not in md
    without = staged_turn.export_packet(turn, wire_state(), run_seed=None)
    assert with_seed["sha256"] == without["sha256"]


def test_the_board_matches_the_packet_it_came_from():
    packet = qa_packet.build(wire_state(), "t")
    assert staged_turn.board_differences(packet, wire_state()) == []


def test_a_different_encounter_is_a_board_mismatch():
    """The failure the first live `execute` hit, as an assertion: the fresh
    game generated a Sludge Spinner where the packet showed a Jaw Worm."""
    packet = qa_packet.build(wire_state(), "t")
    live = wire_state()
    live["battle"]["enemies"][0]["name"] = "Sludge Spinner"
    live["battle"]["enemies"][0]["entity_id"] = "SLUDGE_SPINNER_0"
    diffs = staged_turn.board_differences(packet, live)
    assert len(diffs) == 1
    assert "enemies" in diffs[0] and "Sludge Spinner" in diffs[0]


def test_a_different_hand_is_a_board_mismatch_and_counts_copies():
    """A multiset, not a set: three Coral Guards and one Coral Guard are
    different hands, and a set comparison would call them equal."""
    packet = qa_packet.build(wire_state(), "t")
    live = wire_state()
    live["player"]["hand"].append(dict(live["player"]["hand"][1]))
    diffs = staged_turn.board_differences(packet, live)
    assert len(diffs) == 1 and diffs[0].startswith("hand:")


def test_execute_checks_the_board_before_the_first_play():
    """Ordering is the guard. A check that ran after the first play would fire
    only once the wrong board had already been played onto."""
    turn = staged_turn.load(EXAMPLE)
    steps = staged_turn.execute_steps(
        turn, form(chosen_line=[{"card": "Bake-Kurage"}]))
    verbs = [v for v, _ in steps]
    assert "board_check" in verbs
    assert verbs.index("board_check") < verbs.index("mark") < verbs.index("play")


def test_the_board_check_refuses_by_name_and_lists_the_differences():
    """Through the real runner, on a fake wire: the step raises, the row names
    `board_mismatch`, and the failure carries both sides."""
    import io

    packet = qa_packet.build(wire_state(), "t")
    live = wire_state()
    live["battle"]["enemies"][0]["name"] = "Sludge Spinner"
    replay = scenario_module.Scenario(
        name="t", character="KLEEMOD-KOKOMI",
        steps=[("board_check", {}), ("mark", {})])
    runner = staged_turn.ExecuteRunner(replay, "a test", wire=FakeWire([live]),
                                       out=io.StringIO(),
                                       sleep=lambda _s: None, packet=packet)
    assert runner.run() is False
    assert runner.failures[0]["check"] == "board_mismatch"
    assert "Sludge Spinner" in runner.failures[0]["detail"]
    row = next(r for r in runner.rows if r.get("step") == "board_check")
    assert row["ok"] is False and row["rule"] == "board_mismatch"


def test_the_board_check_passes_and_the_run_continues():
    import io

    packet = qa_packet.build(wire_state(), "t")
    replay = scenario_module.Scenario(
        name="t", character="KLEEMOD-KOKOMI",
        steps=[("board_check", {}), ("mark", {})])
    runner = staged_turn.ExecuteRunner(replay, "a test",
                                       wire=FakeWire([wire_state()]),
                                       out=io.StringIO(),
                                       sleep=lambda _s: None, packet=packet)
    assert runner.run() is True
    row = next(r for r in runner.rows if r.get("step") == "board_check")
    assert row["ok"] is True and row["differences"] == []


def test_board_mismatch_is_a_named_falsifier():
    assert "board_mismatch" in staged_turn.FALSIFIERS
    assert "different turn" in staged_turn.FALSIFIERS["board_mismatch"]


# ------------------------------------------- EB-169: the funnel preflight ---
#
# The register ships EMPTY, so every test that needs a bite passes its own
# one-entry FIXTURE register. That is not a weaker test than a live entry --
# it is the only honest one: an entry in the shipped register would be a claim
# that a card is currently misprinted, and none is.

RED_FIXTURE = TURNS / "fixtures" / "open-face-defect.yaml"

# What round 2 of the Kokomi slice was actually in, reconstructed: EB-164 open
# against the one face staged on all eleven boards.
FIXTURE_REGISTER = {
    "all_streams_flow": {
        "eb": "EB-164",
        "titles": ("All Streams Flow to the Sea",),
        "defect": "the printed damage already folds Charge in and a second "
                  "sentence claims the fold again, so a reader adds it twice",
    },
}


def test_the_shipped_register_is_empty_and_the_file_says_so():
    """EB-164 is closed, so there is nothing to refuse. An empty register is
    the correct state and the module states it in as many words -- a reader
    who finds `{}` should not have to guess whether it was ever filled."""
    from understudy import face_defects

    assert face_defects.OPEN_FACE_DEFECTS == {}
    doc = face_defects.__doc__ or ""
    assert "EMPTY" in doc and "EB-164" in doc


def test_a_staged_board_holding_a_registered_card_is_refused_by_name():
    """The red fixture. The refusal names the CARD and the EB id, because
    "this packet is unsafe" sends a reader to grep and "All Streams Flow to
    the Sea -- EB-164" sends them to the row."""
    turn = staged_turn.load(RED_FIXTURE)
    with pytest.raises(staged_turn.TurnError) as exc:
        staged_turn.face_defect_preflight(turn, FIXTURE_REGISTER)
    text = str(exc.value)
    assert "open_face_defect" in text
    assert "EB-164" in text
    assert "All Streams Flow to the Sea" in text


def test_the_preflight_passes_a_board_with_no_registered_card():
    """The other direction, so the refusal is not "everything is refused".
    The worked example holds no registered card under this register."""
    register = {"pearl_barrage": dict(FIXTURE_REGISTER["all_streams_flow"],
                                      titles=("Pearl Barrage",),
                                      eb="EB-999")}
    turn = staged_turn.load(RED_FIXTURE)
    staged_turn.face_defect_preflight(turn, register)


def test_the_preflight_matches_ids_titles_and_the_mod_spelling():
    """`card_key` folds the three spellings, and it must, because the two
    halves of a turn file and the packet each use a different one: the staging
    grants `KLEEMOD-ALL_STREAMS_FLOW`, the mirror says `all_streams_flow`, and
    a packet prints `All Streams Flow to the Sea`."""
    from understudy import face_defects

    for spelling in ("KLEEMOD-ALL_STREAMS_FLOW", "all_streams_flow",
                     "All Streams Flow to the Sea"):
        hits = face_defects.hits([spelling], FIXTURE_REGISTER)
        assert len(hits) == 1, spelling
        assert hits[0]["eb"] == "EB-164"
    assert face_defects.hits(["Coral Guard"], FIXTURE_REGISTER) == []


def test_check_refuses_the_red_fixture_at_the_command(monkeypatch, capsys):
    """Through the CLI, because that is where it has to bite: `check` is the
    gate that runs with no game, and a refusal that only exists as a function
    is one a sitting can walk past."""
    from understudy import face_defects

    monkeypatch.setattr(face_defects, "OPEN_FACE_DEFECTS", FIXTURE_REGISTER)
    rc = staged_turn.main(["check", str(RED_FIXTURE)])
    assert rc == 1
    assert "open_face_defect" in capsys.readouterr().err


def test_check_passes_the_red_fixture_under_the_shipped_register():
    """The same file, the same command, the empty register: OK. Proof the red
    is the REGISTER's doing and not a malformed turn file."""
    assert staged_turn.main(["check", str(RED_FIXTURE)]) == 0


def test_the_preflight_reads_the_staging_half_as_well_as_the_mirror():
    """A `give` into the draw pile is in no hand and can still be drawn into
    the grader's turn, so both halves are swept."""
    turn = staged_turn.load(RED_FIXTURE)
    names = staged_turn.staged_card_names(turn)
    assert "KLEEMOD-ALL_STREAMS_FLOW" in names   # the staging half
    assert "all_streams_flow" in names           # the mirror


def test_open_face_defect_is_a_named_falsifier():
    from understudy import face_defects

    assert face_defects.RULE in staged_turn.FALSIFIERS
    assert "OPEN defect" in staged_turn.FALSIFIERS[face_defects.RULE]


def test_execute_is_deliberately_not_preflighted():
    """A replay is how a misread already in the record gets settled against
    the board. Refusing it would take away the one tool that answers the
    question the register exists to raise, so `cmd_execute` does not call the
    preflight -- pinned, so the omission reads as a decision."""
    import inspect

    src = inspect.getsource(staged_turn.cmd_execute)
    assert "face_defect_preflight" not in src
    for name in ("cmd_check", "cmd_stage"):
        assert "face_defect_preflight" in inspect.getsource(
            getattr(staged_turn, name)), name


def test_every_register_entry_cites_an_open_backlog_row():
    """The closing discipline, as a test as well as a lint: an entry whose row
    has left HEAD is stale, and stale means over-refusing in silence."""
    import sys

    sys.path.insert(0, str(REPO / "tools"))
    import lint_face_defects

    assert lint_face_defects.findings() == []
    # And the lint bites: a fixture register citing a row that is not open.
    rows = lint_face_defects.open_rows()
    assert "EB-164" not in rows, "EB-164 is closed; its row must have left HEAD"
    bad = lint_face_defects.findings(FIXTURE_REGISTER, rows)
    assert bad and "EB-164" in bad[0]


# ------------------------------- EB-170: replaying through a modal prompt ---
#
# Round 3 met three of these and the replayer walked into the next play,
# reporting `no enemy 'Twig Slime (S)'; the fight has []` -- a true sentence
# about a card-selection screen and a useless one. These pin the three
# outcomes: answered from the form, answered by the operator, and stopped by
# name.

def select_state(screen, prompt, offered, **over):
    """A live-shaped state sitting on a selection screen. The wire's own
    shape: `state_type` names the screen and the screen's blob is a sibling
    key, which is why `_select_blob` reads the type rather than guessing."""
    st = wire_state()
    st["state_type"] = screen
    st[screen] = {"prompt": prompt,
                  "cards": [{"id": "KLEEMOD-" + t.upper().replace(" ", "_"),
                             "name": t} for t in offered]}
    st.update(over)
    return st


def modal_runner(states, form_body, answers=None):
    import io

    replay = scenario_module.Scenario(
        name="t", character="KLEEMOD-KOKOMI",
        steps=[("answer_modal", form_body)])
    return staged_turn.ExecuteRunner(
        replay, "a test", wire=FakeWire(states), out=io.StringIO(),
        sleep=lambda _s: None, packet=qa_packet.build(wire_state(), "t"),
        answers=answers or [])


def test_execute_steps_puts_a_modal_answer_after_every_play():
    """Unconditionally, and not only after the plays whose form entry carries
    a key: a modal is a property of the card and the board, not of what the
    grader remembered to write down."""
    steps = staged_turn.execute_steps(
        staged_turn.load(EXAMPLE),
        form(chosen_line=[{"card": "Bake-Kurage"},
                          {"card": "Pearl Barrage", "target": "Jaw Worm",
                           "exhaust": "Coral Guard"}]))
    verbs = [v for v, _ in steps]
    assert verbs.count("play") == 2 and verbs.count("answer_modal") == 2
    for i, v in enumerate(verbs):
        if v == "play":
            assert verbs[i + 1] == "answer_modal"
    bodies = [b for v, b in steps if v == "answer_modal"]
    assert bodies[0] == {"card": "Bake-Kurage"}
    assert bodies[1] == {"card": "Pearl Barrage", "exhaust": "Coral Guard"}


def test_a_hand_selection_is_answered_from_the_forms_exhaust_key():
    """Kokomi's "which card gets Exhausted", which is a `hand_select` -- the
    hand enters select mode and no screen is built, so the confirm is
    `combat_confirm_selection` and not `confirm_selection`."""
    up = select_state("hand_select", "Choose a card to Exhaust.",
                      ["Coral Guard", "Send the Runner"])
    runner = modal_runner([up] * 5 + [wire_state(), wire_state()],
                          {"card": "Tidal Barrage",
                           "exhaust": "Send the Runner"})
    assert runner.run() is True
    assert [p["action"] for p in runner.wire.posts] == [
        "combat_select_card", "combat_confirm_selection"]
    assert runner.wire.posts[0]["card_index"] == 1
    row = next(r for r in runner.rows if r.get("step") == "answer_modal")
    assert row["answered"] is True and row["source"] == "form"
    assert row["choice"] == "Send the Runner"


def test_a_mode_choice_is_answered_from_the_forms_choose_key():
    """The either-faces: a `card_select` whose offers are the card's own modes,
    printed as whole sentences. Its verbs are the other pair."""
    up = select_state("card_select", "Choose a card.",
                      ["Deal 14 damage", "Gain 6 Block"])
    runner = modal_runner([up] * 5 + [wire_state(), wire_state()],
                          {"card": "Itto - Oni Rush",
                           "choose": "Gain 6 Block"})
    assert runner.run() is True
    assert [p["action"] for p in runner.wire.posts] == [
        "select_card", "confirm_selection"]
    assert runner.wire.posts[0]["index"] == 1


def test_a_prompt_nobody_answered_stops_by_name_and_quotes_it():
    """`modal_unanswered`, naming the prompt and listing the offers. NEVER a
    heuristic pick: the first offer, the biggest number and the cheapest card
    are all plausible guesses, and all three produce a post-state
    indistinguishable from a real replay."""
    up = select_state("card_select", "Choose a card.",
                      ["Deal 14 damage", "Gain 6 Block"])
    runner = modal_runner([up, up], {"card": "Itto - Oni Rush"})
    assert runner.run() is False
    fail = runner.failures[0]
    assert fail["check"] == "modal_unanswered"
    assert "Choose a card." in fail["detail"]
    assert "Deal 14 damage" in fail["detail"]
    assert runner.wire.posts == [], "it must not post a guess"
    assert runner.modals[0]["answered"] is False


def test_an_answer_that_is_not_on_the_screen_is_refused():
    """A choice the screen does not offer is not an answer, and posting a
    near-miss index would be the guess this rule exists to forbid."""
    up = select_state("card_select", "Choose a card.",
                      ["Deal 14 damage", "Gain 6 Block"])
    runner = modal_runner([up, up], {"card": "Itto - Oni Rush",
                                     "choose": "Gain 4 Block"})
    assert runner.run() is False
    assert runner.failures[0]["check"] == "modal_unanswered"
    assert "not on the screen" in runner.failures[0]["detail"]
    assert runner.wire.posts == []


def test_no_screen_up_is_a_no_op_row_and_not_a_failure():
    """The common case: most plays raise nothing, and the step costs one GET."""
    runner = modal_runner([wire_state()], {"card": "Coral Guard"})
    assert runner.run() is True
    row = next(r for r in runner.rows if r.get("step") == "answer_modal")
    assert row["answered"] is False and row["screen"] == ""
    assert "rule" not in row and runner.wire.posts == []


def test_the_operator_answer_fills_a_form_that_predates_the_keys():
    """The three round-3 replays are forms written before `exhaust` and
    `choose` existed. The operator reads the grader's own q1 prose, states the
    answer, and the row says `operator` -- never `form`."""
    up = select_state("card_select", "Choose a card.",
                      ["Deal 14 damage", "Gain 6 Block"])
    runner = modal_runner([up] * 5 + [wire_state(), wire_state()],
                          {"card": "Itto - Oni Rush"},
                          answers=[("Choose a card.", "Deal 14 damage")])
    assert runner.run() is True
    row = next(r for r in runner.rows if r.get("step") == "answer_modal")
    assert row["source"] == "operator" and row["choice"] == "Deal 14 damage"
    assert runner.answers_used == [
        {"index": 0, "prompt": "Choose a card.", "screen": "card_select",
         "choice": "Deal 14 damage"}]


def test_the_operator_answer_never_overrides_the_forms_own():
    """The form is the grader's answer and the operator's is a stand-in for a
    missing one. If both are present the grader wins, and the row says so."""
    up = select_state("card_select", "Choose a card.",
                      ["Deal 14 damage", "Gain 6 Block"])
    runner = modal_runner([up] * 5 + [wire_state(), wire_state()],
                          {"card": "Itto - Oni Rush",
                           "choose": "Gain 6 Block"},
                          answers=[("Choose a card.", "Deal 14 damage")])
    assert runner.run() is True
    row = next(r for r in runner.rows if r.get("step") == "answer_modal")
    assert row["source"] == "form" and row["choice"] == "Gain 6 Block"
    assert runner.answers_used == []


def test_the_operator_answer_may_name_the_screen_when_there_is_no_prompt():
    """A screen can arrive with no prompt text at all, and an operator still
    has to be able to name it."""
    up = select_state("hand_select", "", ["Coral Guard", "Send the Runner"])
    runner = modal_runner([up] * 5 + [wire_state(), wire_state()],
                          {"card": "Tidal Barrage"},
                          answers=[("hand_select", "Coral Guard")])
    assert runner.run() is True
    assert runner.modals[0]["source"] == "operator"


def test_parse_answers_refuses_a_malformed_override():
    assert staged_turn.parse_answers(["Choose a card.=Deal 14 damage"]) == [
        ("Choose a card.", "Deal 14 damage")]
    assert staged_turn.parse_answers(None) == []
    for bad in ("no equals sign", "=Deal 14 damage", "Choose a card.="):
        with pytest.raises(staged_turn.FormError):
            staged_turn.parse_answers([bad])


def test_the_form_keys_are_optional_and_nullable(tmp_path):
    """Every form written before EB-170 still loads, and a null reads as
    "this play raised no such prompt"."""
    path = tmp_path / "f.json"
    for line in ([{"card": "Pearl Barrage"}],
                 [{"card": "Pearl Barrage", "exhaust": None, "choose": None}],
                 [{"card": "Pearl Barrage", "exhaust": "Coral Guard"}]):
        path.write_text(json.dumps(form(chosen_line=line)), encoding="utf-8")
        assert staged_turn.load_form(path)["chosen_line"] == line
    path.write_text(json.dumps(form(chosen_line=[{"card": "X", "exhaust": 7}])),
                    encoding="utf-8")
    with pytest.raises(staged_turn.FormError):
        staged_turn.load_form(path)


def test_modal_unanswered_is_a_named_falsifier():
    assert "modal_unanswered" in staged_turn.FALSIFIERS
    assert "guessed" in staged_turn.FALSIFIERS["modal_unanswered"]


# ------------------------------------------------------- EB-186, the page ---

def banked_state(bank: int = 3):
    """A Klee board at a Spark bank, drawn the way the LIVE game draws it.

    Two Attacks whose faces print 1 and 2 are both rendered at 0 and both
    `can_play: true`, because the Spark hook the game consults for display is
    the same hook it consults for payment. This is not a hypothetical: it is
    `review/qa/klee-slice1-t01/observed.json`, which is the board twelve blind
    readers were handed in round 1 of the Klee slice.
    """
    return {
        "state_type": "monster",
        "battle": {"round": 1, "enemies": [
            {"name": "Seapunk", "hp": 45, "max_hp": 45, "block": 0,
             "intents": [{"type": "Attack", "label": "11",
                          "description": "Attack for 11 damage."}]}]},
        "player": {
            "hp": 42, "max_hp": 62, "block": 0, "energy": 2,
            "resources": {},
            "status": ([{"id": "SPARK_POWER", "name": "Spark", "amount": bank,
                         "type": "Buff",
                         "description": "At 3 Sparks, your Attacks cost 0. "
                                        "Playing one consumes 3 Sparks."}]
                       if bank else []),
            "hand": [
                {"id": "KLEEMOD-KABOOM", "name": "Kaboom!", "type": "Attack",
                 "cost": "0" if bank >= 3 else "1", "can_play": True,
                 "is_upgraded": False,
                 "description": "Deal 7 damage. Applies Pyro."},
                {"id": "KLEEMOD-RAPID_FIRE", "name": "Rapid Fire",
                 "type": "Attack", "cost": "0" if bank >= 3 else "2",
                 "can_play": True, "is_upgraded": False,
                 "description": "Deal 4 damage to random enemies four times."},
                {"id": "KLEEMOD-DUCK_AND_COVER", "name": "Duck and Cover",
                 "type": "Skill", "cost": "1", "can_play": True,
                 "is_upgraded": False, "description": "Gain 5 Block."},
            ]},
    }


def test_the_printed_cost_index_reads_the_shipped_face():
    """The face in `klee-mod` is where the number comes from, and it agrees
    with the sheet the generator emitted it from -- EVERY id, not a sample.
    `qa_packet` may not import a sheet loader; this test may, which is
    exactly why the cross-check lives here."""
    from tier0.content import loader
    index = qa_packet.printed_cost_index(REPO)
    assert index["KABOOM"] == 1 and index["RAPID_FIRE"] == 2
    assert index["FLAME_ON_THE_WICK"] == 0
    disagree = [(c.id, index[c.id.upper()], c.cost)
                for c in loader._card_index().values()
                if c.id.upper() in index and isinstance(c.cost, int)
                and index[c.id.upper()] != c.cost]
    assert not disagree, f"the face and the sheet disagree: {disagree}"
    assert len(index) > 200, f"only {len(index)} faces carried a cost"


def test_the_printed_cost_index_is_keyed_by_id_not_by_title():
    """`EB-267`. The prototype surface ships a re-priced twin of a shipped
    card under the SAME printed name, so a title-keyed map had one row where
    the game has two faces: *Flame Dance* is cost 2 shipped and cost 1 on the
    proto row, and the page told a blind reader the proto card's own printed
    cost was wrong. Both rows are here, under the ids the wire sends."""
    index = qa_packet.printed_cost_index(REPO)
    assert index["FLAME_DANCE"] == 2
    assert index["PROTO_KO_FLAME_DANCE"] == 1
    # The key is the wire's `Id.Entry` with the mod prefix off, which is what
    # every hand entry carries.
    assert qa_packet.card_key("KLEEMOD-PROTO_KO_FLAME_DANCE") \
        == "PROTO_KO_FLAME_DANCE"
    assert qa_packet.card_key("KLEEMOD-KABOOM") == "KABOOM"
    assert qa_packet.card_key(None) == ""


def test_the_class_name_key_agrees_with_every_generated_sheet_id():
    """The key is derived from the C# CLASS NAME because that is what BaseLib
    derives `ModelId.Entry` from (`KleeMod.cs:81`). The generated header also
    prints the sheet id it came from, so the two can be checked against each
    other on every generated face -- which is the pin that keeps the
    derivation honest rather than a guess this file made once."""
    ids = re.compile(r"Sheet entry:\s*id=([a-z0-9_]+)")
    checked = 0
    for path in sorted((REPO / "klee-mod").glob("KleeCode/Cards/**/*.cs")):
        src = path.read_text(encoding="utf-8")
        m = ids.search(src)
        if m is None:
            continue
        checked += 1
        assert qa_packet._class_key(src) == m.group(1).upper(), path.name
    assert checked > 300, f"only {checked} generated faces carried an id"


# ------------------------ EB-282, the Spark price in the cost slot ---

def test_the_printed_spark_index_reads_the_shipped_face():
    """`EB-282`. The row's own body no longer says "Spend 1 Spark." -- the
    price is on the badge in game, and on THIS page it has to come from
    somewhere or the seats are reading a card whose cost they cannot see.

    It comes off the same faces `printed_cost_index` reads, out of the one
    place the generator writes the number: `ISparkPricedCard.PrintedSparkPrice`,
    which the card's own playability gate reads back through
    `SparkCost.PriceOf`. Cross-checked against the surface here, in a test that
    MAY import a loader, for the reason the energy twin above gives.
    """
    from tier0.content import loader
    index = qa_packet.printed_spark_index(REPO)
    assert index["PROTO_KO_FWOOSH"] == 1
    assert index["PROTO_KO_BANG_BANG"] == 2
    # A card with no Spark price has NO row -- silence, never a zero.
    assert "KABOOM" not in index
    assert "PROTO_KO_KAPOW" not in index, (
        "draft 3 made Ka-pow! pay energy; a stale Spark price would print a "
        "cost the card does not charge")

    disagree = []
    for card in loader.prototype_cards():
        priced = [f for f in card.effects if f.get("op") == "spend_spark"]
        want = int(priced[0]["amount"]) if priced else None
        got = index.get(card.id.upper())
        if want != got:
            disagree.append((card.id, got, want))
    assert not disagree, f"the face and the surface disagree: {disagree}"


def test_the_cost_slot_prints_the_spark_price():
    """The page says the price in the same slot the game paints the badge in,
    and in the keyword's own words. Singular and plural are the card's, not a
    grammar rule this page invented for it."""
    assert qa_packet.cost_label({"cost": "0", "printed_spark": 1}) == "1 Spark"
    assert qa_packet.cost_label({"cost": "0", "printed_spark": 2}) == "2 Sparks"
    # No Spark price: exactly what the slot always said.
    assert qa_packet.cost_label({"cost": "1"}) == "1"
    assert qa_packet.cost_label({"cost": "", "printed_spark": None}) == "-"
    # Priced in both -- no row is today, and a page that dropped half a price
    # is the defect this function exists to repair.
    assert qa_packet.cost_label({"cost": "2", "printed_spark": 1})         == "2 and 1 Spark"


def test_eb339_a_spark_priced_face_says_what_a_discount_does_not_cover():
    """`EB-339`. A cost-to-zero effect covers Energy, and the face says so.

    THE SEAT'S OWN CARD. `Vexing Puzzlebox` prints "It's free to play this
    turn"; the card it handed over arrived as `Powder Charge -- cost 1 Spark`
    with no note at all, and the seat had to derive "free apparently means free
    of ENERGY" from a card that silently did not work
    (`klee round 7b, opus-act2.md`, section (c)).

    AND `_discounted` WAS RIGHT TO SAY NO. A Spark price is an `op:
    spend_spark`, not a cost, so `printed_cost` is 0 on every Spark row and a
    cost-to-zero effect moves 0 to 0. So the sentence is tied to the ENERGY
    SLOT reading zero -- which is exactly when something can claim the card is
    free -- rather than to a discount the wire never mentions.
    """
    note = qa_packet.cost_note(
        {"cost": "0", "printed_cost": 0, "printed_spark": 1})
    assert "Its 1 Spark is a price, not an Energy cost" in note
    assert "covers Energy only" in note
    assert "still spent" in note
    # Plural is the card's, exactly as the cost slot's own is.
    assert "Its 2 Sparks is a price" in qa_packet.cost_note(
        {"cost": "0", "printed_cost": 0, "printed_spark": 2})
    # A card with no Spark price gains not one word, in either direction.
    assert qa_packet.cost_note({"cost": "0", "printed_cost": 0}) == ""
    assert "Spark" not in qa_packet.cost_note(
        {"cost": "0", "printed_cost": 1})
    # Both halves on one line where both apply, the Energy slot first.
    both = qa_packet.cost_note(
        {"cost": "0", "printed_cost": 1, "printed_spark": 1})
    assert both.startswith("The cost printed on this card is 1")
    assert "Its 1 Spark is a price" in both


def test_eb339_the_rendered_page_carries_the_spark_discount_sentence():
    """End to end on the page an agent is handed, which is where the seat read
    the card and found nothing."""
    state = banked_state(0)
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_KO_POWDER_CHARGE", "name": "Powder Charge",
         "type": "Skill", "cost": "0", "can_play": True, "is_upgraded": False,
         "description": "Place a Bomb 6."},
    ]
    page = qa_packet.render(qa_packet.build(state, "t", repo=REPO))
    assert "- Cost: 1 Spark" in page
    assert "covers Energy only" in page


def test_the_rendered_page_shows_a_spark_priced_card_at_its_price():
    """End to end on the page an agent is handed: a Spark row is drawn at 0
    energy, and before this it read as free."""
    state = banked_state(0)
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_KO_FWOOSH", "name": "Fwoosh!", "type": "Attack",
         "cost": "0", "can_play": True, "is_upgraded": False,
         "description": "Set off and deal 5 damage to a random enemy."},
    ]
    page = qa_packet.render(qa_packet.build(state, "t", repo=REPO))
    assert "- Cost: 1 Spark" in page


def test_a_same_named_proto_row_prints_no_discrepancy():
    """`EB-267`'s acceptance, both directions. The proto *Flame Dance* is
    drawn at the cost its own row prints, so the page says nothing about it; a
    card the board really is discounting still says so on its own line."""
    state = banked_state(0)
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_KO_FLAME_DANCE", "name": "Flame Dance",
         "type": "Attack", "cost": "1", "can_play": True, "is_upgraded": False,
         "description": "Deal 9 damage to ALL enemies."},
        {"id": "KLEEMOD-KABOOM", "name": "Kaboom!", "type": "Attack",
         "cost": "0", "can_play": True, "is_upgraded": False,
         "description": "Deal 7 damage. Applies Pyro."},
    ]
    page = qa_packet.render(qa_packet.build(state, "t", repo=REPO))
    assert "The cost printed on this card is 2" not in page
    assert "The cost printed on this card is 1; it is showing 0 here." in page
    assert page.count("The cost printed on this card") == 1


def test_the_unplayable_enum_reaches_the_page_as_plain_words():
    """`EB-264`. The wire's reason is `UnplayableReason.ToString()`, and a
    blind tester reported `CANNOT BE PLAYED: BlockedByCardLogic` as the least
    readable thing on the screen. Neither enum name reaches a page; a reason
    the wire spells as a SENTENCE is kept in the game's own words, which is
    the door the mod's own Spark refusal comes through."""
    state = banked_state(0)
    for card in state["player"]["hand"]:
        card["can_play"] = False
    state["player"]["hand"][0]["unplayable_reason"] = "BlockedByCardLogic"
    state["player"]["hand"][1]["unplayable_reason"] = "EnergyCostTooHigh"
    state["player"]["hand"][2]["unplayable_reason"] = "you have no Spark"
    page = qa_packet.render(qa_packet.build(state, "t", repo=REPO))
    assert "BlockedByCardLogic" not in page
    assert "EnergyCostTooHigh" not in page
    assert "this card's own rule is stopping you right now" in page
    assert "you do not have enough energy" in page
    assert "you have no Spark" in page


def test_an_unmapped_enum_is_spelled_out_rather_than_dropped():
    """A reason this map has never seen is still legible AND still reported:
    silence would hide the next enum exactly the way this row's three were
    hidden. A `[Flags]` combination prints as `A, B` and each part is read."""
    assert qa_packet.unplayable_reason("BlockedByHook") \
        == "something else on the board is stopping you right now"
    assert qa_packet.unplayable_reason("SomeNewReason") == "some new reason"
    assert qa_packet.unplayable_reason("EnergyCostTooHigh, StarCostTooHigh") \
        == "you do not have enough energy; you do not have enough Stars"
    assert qa_packet.unplayable_reason("None") == ""
    assert qa_packet.unplayable_reason(None) == ""


def test_a_banked_board_prints_the_rule_and_names_every_discount():
    """EB-186's acceptance. At a bank of three the page states Spark's OWN
    words once, and beside each Attack shown below its printed cost says what
    that card prints. Round 1's readers had neither."""
    page = qa_packet.render(
        qa_packet.build(banked_state(3), "t", repo=REPO))
    assert "At 3 Sparks, your Attacks cost 0. Playing one consumes 3 " \
           "Sparks." in page
    assert "covers 1 of the 2" in page
    assert "The cost printed on this card is 1; it is showing 0 here." in page
    assert "The cost printed on this card is 2; it is showing 0 here." in page
    # And the card that is NOT discounted carries no note.
    assert page.count("The cost printed on this card") == 2


def test_an_unbanked_board_prints_nothing_extra():
    """The other direction, and it is the one that keeps the note honest: with
    no bank nothing is discounted, so the page gains not one word."""
    page = qa_packet.render(
        qa_packet.build(banked_state(0), "t", repo=REPO))
    assert "The cost printed on this card" not in page
    assert "Spark, and the costs below" not in page


def test_the_spark_note_quotes_and_never_invents():
    """The rule sentence is the power's own hover text and the arithmetic is
    division on two numbers the page already shows. A power whose text says
    nothing about consuming loses the count and keeps the quote."""
    powers = [{"name": "Spark", "stacks": 6,
               "text": "At 3 Sparks, your Attacks cost 0. Playing one "
                       "consumes 3 Sparks."}]
    hand = [{"cost": "0", "printed_cost": 1}, {"cost": "0", "printed_cost": 2},
            {"cost": "1", "printed_cost": 1}]
    note = qa_packet.spark_note(powers, hand)
    assert "covers 2 of the 2" in note and "Your bank is 6." in note
    silent = qa_packet.spark_note(
        [{"name": "Spark", "stacks": 6, "text": "Sparks do something."}], hand)
    assert "covers" not in silent and "Sparks do something." in silent
    assert qa_packet.spark_note([], hand) == ""


# --------------------------------------- EB-185, the Spark bank observed ---

def test_the_observed_board_carries_the_spark_bank():
    """EB-185's acceptance. Sparks ride the wire as a POWER and the sim keeps
    them on `Player.sparks`; before the crossing existed, every observed
    reading of a Klee board scored a bank of zero and reported `spark` as an
    unmapped status."""
    state, unrep, notes = staged_turn.observed_state(
        {"state": banked_state(3)})
    assert state.player.sparks == 3
    assert "spark" not in notes["unmapped_statuses"]
    assert notes["player_fields"] == {"sparks": 3}
    empty, _, notes0 = staged_turn.observed_state({"state": banked_state(0)})
    assert empty.player.sparks == 0 and notes0["player_fields"] == {}


def test_a_status_the_sim_has_no_field_for_is_refused_not_guessed():
    """The refusal half: a mapping onto a field the Player does not carry
    would write the bank where nothing reads it and report success."""
    from understudy import adapter
    state = banked_state(3)
    state["player"]["status"][0]["name"] = "Spark"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(adapter, "STATUS_FIELDS", {"spark": "no_such_field"})
        with pytest.raises(AttributeError):
            adapter.build_combat_state(state)


# ---------------------- EB-187, an assumption the face already contradicts ---

RIDER_FIXTURE = TURNS / "fixtures" / "double-counted-rider.yaml"


def test_an_assumption_claiming_a_printed_rider_is_refused():
    """EB-187's red fixture, carrying the sentence that corrupted a grade. The
    refusal names the claim, the card and the tag, because "this board is
    unsafe" sends a reader to grep and the sentence sends them to the line."""
    turn = staged_turn.load(RIDER_FIXTURE)
    found = staged_turn.assumption_rider_conflicts(turn)
    assert len(found) == 1, found
    assert "clockwork_toy" in found[0] and "skill_tag" in found[0]
    assert "Burst +5" in found[0]
    with pytest.raises(staged_turn.TurnError) as exc:
        staged_turn.assumption_preflight(turn)
    assert "already prints" in str(exc.value)


def test_the_reworded_assumption_passes_on_the_same_board():
    """The other direction, and it is the whole point of the rule's shape: a
    line saying the printed rider IS the tag is exactly what the check wants.
    Anything else would be a check that refuses every board mentioning Burst."""
    turn = staged_turn.load(RIDER_FIXTURE)
    turn.assumptions[0] = (
        "The Burst meter is written to 20 of 40 through the registered "
        "resource. Where a card's face prints a Burst rider, that printed "
        "rider IS the whole of what playing the card adds to the meter on "
        "top of the card's own text -- nothing further is added behind it.")
    assert staged_turn.assumption_rider_conflicts(turn) == []
    staged_turn.assumption_preflight(turn)


def test_the_rider_check_needs_the_tag_on_the_board():
    """An untagged hand cannot double-count a rider nothing prints, so the same
    sentence passes there -- the check reads the staged rows, not the prose."""
    turn = staged_turn.load(RIDER_FIXTURE)
    turn.staging[:] = [s for s in turn.staging
                       if "CLOCKWORK_TOY" not in str(s)]
    turn.board.hand[:] = ["kaboom"]
    assert staged_turn.assumption_rider_conflicts(turn) == []


def test_every_shipped_turn_passes_the_rider_check():
    """The sweep, which is what `check` runs. Klee slice 1's pair 3 was the
    only board carrying the claim and both halves are reworded."""
    bad = {p.name: staged_turn.assumption_rider_conflicts(staged_turn.load(p))
           for p in staged_turn.all_turns()}
    assert not {k: v for k, v in bad.items() if v}


# ============================================================== EB-238 =====

def test_the_staged_packet_prints_the_runs_relics():
    """THE LOCK, on the surface `KLEESPARK-BT1`'s readers actually read.

    The staged packet is `packet.md`, not the blind-play page, and it printed
    no relic either -- which is how a round measuring a 3-Spark price ran
    four boards in front of a starter relic that hands the price back one
    Spark per detonated Bomb (§22.4).
    """
    state = {
        "state_type": "battle",
        "player": {
            "hp": 42, "max_hp": 62, "block": 0, "energy": 3,
            "hand": [], "status": [],
            "relics": [{"id": "KLEEMOD-POUNDING_SURPRISE",
                        "name": "Pounding Surprise",
                        "description": "Whenever a Bomb detonates, gain 1 "
                                       "Spark.",
                        "counter": None}],
        },
        "battle": {"round": 4, "enemies": []},
    }
    packet = qa_packet.build(state, "eb238-relic-line")
    assert packet["board"]["you"]["relics"] == [
        {"name": "Pounding Surprise",
         "text": "Whenever a Bomb detonates, gain 1 Spark."}]
    page = qa_packet.render(packet)
    assert ("- Relic — Pounding Surprise: Whenever a Bomb detonates, gain 1 "
            "Spark." in page)
    assert "KLEEMOD" not in page


# ------- EB-240: the assumptions a machine can check, checked at stage -----
#
# `KLEESPARK-BT2` printed two false assumptions on all three boards -- "the
# run carries Klee's starting relic and no other" against a wire carrying
# TWO, and `set_hp: {who: first, amount: 55}` against live bodies of 45, 46
# and 40 -- and nothing could see either, because the block a reader does
# arithmetic on is English prose. The English is not parsed here and never
# will be; a board declares the fact it wants checked in a shape with one
# meaning, and the stage refuses on a mismatch.
#
# The wire is MOCKED: these are the two states the preflight is about, the
# one BT2 staged and the one it thought it had.


def _bt2_wire(*, relics=("Pounding Surprise", "Fishing Rod"), enemy_hp=45,
              player_hp=42, intents=None):
    """The board `KLEESPARK-BT2` ACTUALLY staged, field for field: two relics
    where every board asserted one, and a body at 45 where every board wrote
    55. Both are recorded at klee-sparks §24.9 and neither moved a grade.

    `intents` is the wire's telegraph list in the shape the bridge sends it
    (EB-244) -- the same field `adapter._intent` and the blind page both read.
    Absent by default, which is the state every case written before that row
    was checked against."""
    enemy = {"id": "e1", "name": "Act 1 enemy", "hp": enemy_hp,
             "max_hp": enemy_hp, "block": 0, "status": []}
    if intents is not None:
        enemy["intents"] = list(intents)
    return {
        "state_type": "battle",
        "player": {"hp": player_hp, "max_hp": 62, "block": 0, "energy": 3,
                   "hand": [], "status": [],
                   "relics": [{"id": f"KLEEMOD-{n.upper().replace(' ', '_')}",
                               "name": n, "description": "", "counter": None}
                              for n in relics]},
        "battle": {"round": 4, "turn": 4, "enemies": [enemy]},
    }


# The two telegraphs `KLEESPARK-BT3` actually drew, against the one both its
# boards declared. `t01` drew the Debuff and `t02` the attack for 12.
BT3_DEBUFF = [{"type": "DebuffStrong", "title": "Strategic",
               "label": "", "description": "Applies a debuff."}]
BT3_ATTACK_12 = [{"type": "Attack", "title": "Attack",
                  "label": "12", "description": "Deals 12 damage."}]
BT3_ATTACK_16 = [{"type": "Attack", "title": "Attack",
                  "label": "16", "description": "Deals 16 damage."}]


def _bt2_board(**over):
    """`klee-sparks-bt2r/t01.yaml`'s shape, cut to what the preflight reads.
    The published file itself is a RECORD and is not edited (R101b); this is
    a copy of its declarations, which is what the row asked be seen to
    fail."""
    blob = {
        "id": "eb240-board", "character": "KLEEMOD-KLEE",
        "staging": [
            {"give": {"card": "KLEEMOD-KABOOM", "pile": "hand"}},
            {"set_hp": {"who": "player", "amount": 42}},
            {"set_hp": {"who": "first", "amount": 55}},
            {"read": "the staged board"}],
        "board": {"character": "klee", "hp": 42, "max_hp": 62, "energy": 3,
                  "hand": ["kaboom"],
                  "enemies": [{"name": "Act 1 enemy", "hp": 55,
                               "intent": {"kind": "attack", "amount": 16}}]},
    }
    blob.update(over)
    return staged_turn.parse(blob)


def test_a_board_that_declares_nothing_is_checked_on_what_it_already_wrote():
    """Absent `expects:` is not a failure: it is every board written before
    this key existed, and it still gets the automatic read-back, because a
    `set_hp` step IS a declaration and reading it back costs the file
    nothing."""
    turn = _bt2_board()
    assert turn.expects == {}
    staged_turn.wire_assumption_preflight(turn, _bt2_wire(enemy_hp=55))


def test_the_hp_a_board_wrote_and_the_game_did_not_take_refuses_the_stage():
    """SEEN TO FAIL ON BT2's OWN DECLARATIONS. All three boards ran
    `set_hp: {who: first, amount: 55}` to a clean staging report and were
    then read at 45, 46 and 40. It moved no grade there -- the largest line
    was 40, so *no lethal line* held by 5 -- and it is what that clause
    rested on."""
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(_bt2_board(), _bt2_wire())
    assert "'first' at 55" in str(e.value) and "reads 45" in str(e.value)
    assert "EB-240" in str(e.value)


def test_the_relic_a_board_declares_is_compared_against_the_wires_list():
    """THE OTHER HALF, SEEN TO FAIL ON BT2's OWN WORDS. Every board asserted
    Klee's starting relic *and no other*; the page printed two. Declared as
    one relic, the extra is named and the stage is refused."""
    turn = _bt2_board(expects={"relics": ["Pounding Surprise"]})
    assert turn.expects["relics"] == ["Pounding Surprise"]
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(turn, _bt2_wire(enemy_hp=55))
    assert "unexpected 'Fishing Rod'" in str(e.value)
    # A relic the board declares and the wire does NOT carry is the same
    # kind of falsehood and is refused the same way.
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(
            _bt2_board(expects={"relics": ["Pounding Surprise"]}),
            _bt2_wire(relics=(), enemy_hp=55))
    assert "missing 'Pounding Surprise'" in str(e.value)


def test_a_board_whose_declarations_are_the_wires_stages():
    """The green case, and it is the board BT2 believed it had: the relic
    list declared truthfully, and the body at the number the file wrote."""
    turn = _bt2_board(
        expects={"relics": ["Pounding Surprise", "Fishing Rod"]})
    staged_turn.wire_assumption_preflight(turn, _bt2_wire(enemy_hp=55))
    # Case and order are the run's business, not the board's.
    turn = _bt2_board(expects={"relics": ["fishing rod", "POUNDING SURPRISE"]})
    staged_turn.wire_assumption_preflight(turn, _bt2_wire(enemy_hp=55))


def test_a_board_may_declare_hp_for_a_body_no_step_writes():
    """`expects.hp` is for the body a `set_hp` does not set -- the automatic
    half cannot see a fact the file never wrote down."""
    turn = _bt2_board(expects={"hp": {"player": 40}})
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(turn, _bt2_wire(enemy_hp=55))
    assert "'player' at 40" in str(e.value) and "reads 42" in str(e.value)


def test_a_declared_creature_the_wire_does_not_have_is_refused_not_skipped():
    """An enemy symbol that resolves to nobody is a board about a fight that
    is not on the screen, which is the loudest possible mismatch and must
    not read as *nothing to check*."""
    wire = _bt2_wire(enemy_hp=55)
    wire["battle"]["enemies"] = []
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(_bt2_board(), wire)
    assert "no such creature" in str(e.value)


def test_the_expects_block_refuses_a_shape_it_cannot_mean_one_thing_by():
    """Refused, never coerced -- the rule every other block in this file
    follows. A key nobody reads is an assumption that looks checked."""
    for bad in ({"relics": "Pounding Surprise"},
                {"relics": [""]},
                {"hp": {"first": "55"}},
                {"hp": {}},
                {"relics": ["x"], "starting_deck": ["y"]},
                "the usual"):
        with pytest.raises(staged_turn.TurnError):
            _bt2_board(expects=bad)
    # An empty list is a real declaration: this run carries NO relics.
    turn = _bt2_board(expects={"relics": []})
    assert turn.expects == {"relics": []}
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(turn, _bt2_wire(enemy_hp=55))
    assert "declares (none)" in str(e.value)


def test_the_stage_is_what_refuses_and_it_refuses_before_the_packet():
    """Position matters as much as the check: `stage_board` calls the
    preflight after the last staging step and before it hands the state
    back, so nothing downstream -- packet, reader, grade -- exists yet."""
    # `EB-180` moved `stage_board` into `staged_turn_stage.py`; the read is
    # of the whole seam family, so the claim follows the function.
    from tier0.tests.conftest import seam_source
    src = seam_source("staged_turn")
    body = src.split("def stage_board(")[1].split("\ndef ")[0]
    assert "wire_assumption_preflight(turn, policy.staged_state)" in body
    assert body.index("if not policy.ok") < body.index(
        "wire_assumption_preflight(turn, policy.staged_state)")


def test_bt2s_own_published_boards_are_what_this_check_was_seen_to_fail_on():
    """THE ROW'S ACCEPTANCE, ON THE FILES THEMSELVES. `KLEESPARK-BT2`'s three
    boards are READ here and never edited -- they are a published record and
    stand as published (R101b). Every one of them declares
    `set_hp: {who: first, amount: 55}`, and the live bodies were 45, 46 and
    40; parsed as they are committed and put in front of the wire that round
    actually had, all three are refused."""
    import yaml
    boards = sorted((TURNS / "klee-sparks-bt2r").glob("t0*.yaml"))
    assert len(boards) == 3
    for path, live in zip(boards, (45, 46, 40)):
        turn = staged_turn.parse(
            yaml.safe_load(path.read_text(encoding="utf-8")), path)
        assert turn.expects == {}, "the published files are not edited"
        mine = staged_turn._declared_hp(turn)["player"]
        with pytest.raises(staged_turn.TurnError) as e:
            staged_turn.wire_assumption_preflight(
                turn, _bt2_wire(enemy_hp=live, player_hp=mine))
        assert f"declares 'first' at 55" in str(e.value)
        assert f"reads {live}" in str(e.value)
        # And the same board against the body it declared stages clean.
        staged_turn.wire_assumption_preflight(
            turn, _bt2_wire(enemy_hp=55, player_hp=mine))


# --- EB-244: the third leg, the enemy's INTENT ------------------------------
#
# EB-240 gave `expects:` a relics leg and an hp leg and nothing that could see
# a TELEGRAPH. The encounter is generated from the seed and no staging step
# writes an intent, so a board is free to say what the enemy is about to do
# and be wrong. `KLEESPARK-BT3` was: both boards' notes and their `board:`
# mirror printed "one enemy telegraphing an attack for 16" while `t01` drew a
# Debuff and `t02` an attack for 12. It was causal, not cosmetic -- `t01`
# holds no Attack, so against a Debuff no intent could change the line, both
# deciding forms were refused `intent_insensitive`, and `G1`/`G2`/`G4` all
# graded UNREACHED.


def test_a_board_declaring_an_intent_the_wire_lacks_is_refused():
    """SEEN TO FAIL ON BT3's OWN DECLARATION. The board says attack 16, the
    wire telegraphs a Debuff, and the refusal names both."""
    turn = _bt2_board(
        expects={"intent": {"first": {"kind": "attack", "amount": 16}}})
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(
            turn, _bt2_wire(enemy_hp=55, intents=BT3_DEBUFF))
    msg = str(e.value)
    assert "intent:" in msg and "'first'" in msg
    assert "attack 16" in msg
    assert "Strategic" in msg          # what the page actually printed
    assert "EB-240" in msg             # the same refusal, one more leg


def test_the_same_declaration_against_the_other_boards_wire():
    """`t02`'s half: the right KIND and the wrong NUMBER, which is the
    quieter of the two and the one a reader would do arithmetic on."""
    turn = _bt2_board(
        expects={"intent": {"first": {"kind": "attack", "amount": 16}}})
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(
            turn, _bt2_wire(enemy_hp=55, intents=BT3_ATTACK_12))
    assert "attack 16" in str(e.value) and "attack 12" in str(e.value)


def test_a_board_whose_intent_is_the_wires_stages():
    """The green case: the board BT3 believed it had."""
    turn = _bt2_board(
        expects={"intent": {"first": {"kind": "attack", "amount": 16}}})
    staged_turn.wire_assumption_preflight(
        turn, _bt2_wire(enemy_hp=55, intents=BT3_ATTACK_16))


def test_an_intent_may_be_declared_by_kind_alone():
    """`amount` is optional, because a board that only needs *it attacks*
    should not have to assert a number it does not depend on -- and a board
    that declares the number gets the number checked."""
    turn = _bt2_board(expects={"intent": {"first": {"kind": "attack"}}})
    staged_turn.wire_assumption_preflight(
        turn, _bt2_wire(enemy_hp=55, intents=BT3_ATTACK_12))
    with pytest.raises(staged_turn.TurnError):
        staged_turn.wire_assumption_preflight(
            turn, _bt2_wire(enemy_hp=55, intents=BT3_DEBUFF))


def test_a_non_damaging_telegraph_is_declarable_too():
    """The Debuff has a name in this vocabulary -- `adapter._intent` reads
    every non-damaging telegraph as a zero-damage beat, and a board that
    means *it does not attack me this turn* must be able to say so."""
    turn = _bt2_board(
        expects={"intent": {"first": {"kind": "block", "amount": 0}}})
    staged_turn.wire_assumption_preflight(
        turn, _bt2_wire(enemy_hp=55, intents=BT3_DEBUFF))
    with pytest.raises(staged_turn.TurnError):
        staged_turn.wire_assumption_preflight(
            turn, _bt2_wire(enemy_hp=55, intents=BT3_ATTACK_12))


def test_an_intent_declared_for_a_creature_the_wire_lacks_is_refused():
    """Same rule the hp leg follows: a symbol that resolves to nobody is a
    board about a fight that is not on the screen, not *nothing to check*."""
    wire = _bt2_wire(enemy_hp=55)
    wire["battle"]["enemies"] = []
    turn = _bt2_board(
        staging=[{"give": {"card": "KLEEMOD-KABOOM", "pile": "hand"}},
                 {"set_hp": {"who": "player", "amount": 42}},
                 {"read": "the staged board"}],
        expects={"intent": {"first": {"kind": "attack", "amount": 16}}})
    with pytest.raises(staged_turn.TurnError) as e:
        staged_turn.wire_assumption_preflight(turn, wire)
    assert "no such creature" in str(e.value)


def test_a_board_that_declares_no_intent_is_asked_nothing_about_one():
    """The leg is OPTIONAL, exactly like relics: a board that declares no
    intent is not thereby asserting the wire has none, it is asserting
    nothing -- which is the state every board written before this row is in,
    and the state the published BT2 boards must keep."""
    turn = _bt2_board()
    assert "intent" not in turn.expects
    staged_turn.wire_assumption_preflight(
        turn, _bt2_wire(enemy_hp=55, intents=BT3_DEBUFF))


def test_the_intent_leg_refuses_a_shape_it_cannot_mean_one_thing_by():
    """Refused, never coerced -- the rule the rest of `expects:` follows."""
    for bad in ({"intent": {"first": "attack 16"}},
                {"intent": {"first": {}}},
                {"intent": {"first": {"amount": 16}}},
                {"intent": {"first": {"kind": ""}}},
                {"intent": {"first": {"kind": "attack", "amount": "16"}}},
                {"intent": {"first": {"kind": "attack", "damage": 16}}},
                {"intent": {"": {"kind": "attack"}}},
                {"intent": {}},
                {"intent": []}):
        with pytest.raises(staged_turn.TurnError):
            _bt2_board(expects=bad)


def test_bt3s_own_published_boards_declare_the_intent_they_drew():
    """THE ROW'S ACCEPTANCE ON THE FILES THEMSELVES. Both `KLEESPARK-BT3`
    boards mirror `intent: {kind: attack, amount: 16}` on their `board:`
    half. Parsed as committed and put in front of the wire that round
    actually had, the declaration each one would make is refused."""
    import yaml
    boards = sorted((TURNS / "klee-sparks-bt3").glob("t0*.yaml"))
    assert len(boards) == 2
    for path, live in zip(boards, (BT3_DEBUFF, BT3_ATTACK_12)):
        blob = yaml.safe_load(path.read_text(encoding="utf-8"))
        mirrored = blob["board"]["enemies"][0]["intent"]
        assert mirrored == {"kind": "attack", "amount": 16}
        turn = staged_turn.parse(blob, path)
        probe = staged_turn._parse_expects({"intent": {"first": mirrored}})
        wire = _bt2_wire(enemy_hp=int(blob["board"]["enemies"][0]["hp"]),
                         player_hp=int(blob["board"]["hp"]), intents=live)
        turn.expects.update(probe)
        with pytest.raises(staged_turn.TurnError) as e:
            staged_turn.wire_assumption_preflight(turn, wire)
        assert "intent:" in str(e.value)
