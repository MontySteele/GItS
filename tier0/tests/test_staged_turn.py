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
from pathlib import Path

import pytest

from understudy import qa_packet, staged_turn

REPO = Path(__file__).resolve().parents[2]
TURNS = REPO / "understudy" / "turns"
EXAMPLE = TURNS / "kokomi-first-turn-example.yaml"


# ------------------------------------------------------------- fixtures ----

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
    src = Path(soak.__file__).read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            assert not any(a.name.endswith(("staged_turn", "qa_packet"))
                           for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert not (node.module or "").endswith(("staged_turn",
                                                     "qa_packet"))
            assert not any(a.name in ("staged_turn", "qa_packet")
                           for a in node.names)


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
