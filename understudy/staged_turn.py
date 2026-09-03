"""EB-149 (R213 process step 2): the BLIND QA funnel for one staged turn.

    python -m understudy.staged_turn check     understudy/turns/<t>.yaml
    python -m understudy.staged_turn closeness understudy/turns/<t>.yaml
    python -m understudy.staged_turn stage     understudy/turns/<t>.yaml --why "..."
    python -m understudy.staged_turn stage     understudy/turns/<t>.yaml --hold --why "..."
    python -m understudy.staged_turn grade     <turn-id> <form.json>
    python -m understudy.staged_turn execute   <turn-id> <form.json> --why "..."
    python -m understudy.staged_turn execute   <turn-id> <form.json> --why "..." \
        --answer "<prompt>=<printed choice>"
    python -m understudy.staged_turn ledger

WHAT THIS IS, IN ONE PARAGRAPH
------------------------------
R213 accepted a four-step funnel and this file is step two. A STAGED TURN is a
board set up by hand in the real game from a YAML file. A BLIND GRADER -- an
LLM agent with no repo access, or [USER] playing the same board cold -- sees
only the printed truth of that board and answers four questions: what did you
play, what other line did you seriously consider, what did your chosen line
give up, would a different enemy intent have changed it. THE FORM IS A
FALSIFIER AND NOT A SCORE. A turn whose second question has no answer, or whose
fourth is "no", is REFUSED and never reaches [USER]. Nothing in this file rates
a turn, ranks a turn, or says a turn is good; there is no verdict here but
REFUSED and SURVIVES, and SURVIVES means only "not yet falsified".

THE ONE NUMBER, AND THE ONE PLACE IT IS QUOTABLE (R213 F, R215 B)
-----------------------------------------------------------------
`closeness` reads the staged board into a tier0 `CombatState`, enumerates the
plausible lines, scores each with the PILOT'S OWN `_score` surface, and reports
the gap between the best two. It exists to refuse a turn where one line
overwhelmingly dominates. It is not evidence that a decision is fun, it is not
a balance reading, and it may not be compared across turns.

R215 B put the exception in LAW in as many words: no number measured on a
prototype row is quotable, EXCEPT the decision-closeness falsifier, because
the falsifier reads the TURN and not the row. Every verdict this file writes
carries that sentence, so a number lifted out of one arrives with its licence.

WHY THE PACKET IS A SEPARATE MODULE
-----------------------------------
`qa_packet.py` builds the blind packet and imports nothing from `tier0` -- not
the sheet loaders, not the engine, not the pilot. THIS file imports all three,
because the falsifier needs them. Keeping them apart is what makes "the agent
sees no design context" a structural fact rather than a promise: the code that
writes the packet cannot open a sheet, and an AST walk in
`tier0/tests/test_staged_turn.py` says so.

ATTENDED ONLY, LIKE EVERY OTHER STAGED THING
---------------------------------------------
This module grants cards and writes a board, so it sits on `scenario.py`'s side
of the line and `soak.py` does not import it -- pinned structurally, the same
way `test_understudy_scenario` pins the scenario harness's absence. It reaches
a fight through `soak.run_scripted`, the same setup / policy-swap / teardown
dance every attended instrument uses; nothing about the embark is reimplemented
here.

THE FILE FORMAT
---------------
YAML, under `understudy/turns/`. Two halves that describe the same board, and
the parser refuses a file where they disagree:

    id: kokomi-first-turn-example
    character: KLEEMOD-KOKOMI
    exact_hand: true               # EB-165: empty the dealt hand first
    assumptions: ["..."]
    staging:                       # scenario SETUP verbs, run against the game
      - give: {card: KLEEMOD-PEARL_BARRAGE, pile: hand}
      - set_energy: 3
    board:                         # the tier0 mirror, read ONLY by `closeness`
      character: kokomi
      pilot: generic
      hp: 62
      hand: [pearl_barrage, coral_guard]
      enemies:
        - {name: "Jaw Worm", hp: 32, intent: {kind: attack, amount: 11}}

`exact_hand: true` (EB-165) is how a turn asks for the hand it declared and no
other. The game deals its own opening hand on top of the granted one, so
without it a five-card turn stages with ten; with it, `stage` runs the bridge's
`clear_hand` op BEFORE the first grant -- the cards go to the bottom of the
draw pile through the pile move that sits underneath discard and exhaust, so no
trigger fires -- and `export_packet` REFUSES to write a packet whose live hand
is not the declared multiset.

REPLAYING A LINE THROUGH A MODAL PROMPT (EB-170)
------------------------------------------------
A card can stop the turn and ask a question: WHICH card gets Exhausted
(`hand_select`), or WHICH half of a "Choose one" face resolves (`card_select`).
Round 3 of the Kokomi slice met three of those and the replayer walked into the
next play, which reported `no enemy 'Twig Slime (S)'; the fight has []` -- a
true sentence about a card-selection screen and a useless one. So a play's
entry in `chosen_line` may carry two optional keys, both in the grader's own
printed vocabulary:

    {"card": "Tidal Barrage", "target": "Nibbit", "exhaust": "Send the Runner"}
    {"card": "Itto - Oni Rush", "choose": "Deal 14 damage"}

`execute` answers the prompt from them. When a prompt appears and NOBODY said
what to pick, it STOPS with `modal_unanswered`, naming the prompt and listing
what was on the table -- never a heuristic pick, because the first offer, the
biggest number and the cheapest card are all plausible guesses and all three
produce a post-state indistinguishable from a real replay. `--answer
"<prompt>=<printed choice>"` is the OPERATOR's answer for a form written before
these keys existed, read off the grader's own q1 prose; it is logged as
`source: "operator"` on the row and in the record, and it never overrides an
answer the form itself carries.

`staging` may not contain `play`, `end_turn` or `expect`: a staged turn is a
BOARD, and the line is the grader's answer, not the file's. The two halves are
checked against each other by `scenario.card_key`, so a card added to the hand
in one half and forgotten in the other is a parse error and not a falsifier
reading taken on a board nobody staged.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import yaml

from understudy import adapter, bridge, face_defects, qa_packet, scenario

REPO = Path(__file__).resolve().parents[1]

# COMMITTED, unlike `understudy/logs/`. A packet is the artifact the funnel
# exists to produce and a verdict is the record of a refusal; both are prose
# about one hand-set board and neither is a measurement, so they belong in the
# tree where a later reader can find the turn a verdict refused.
QA_DIR = REPO / "review" / "qa"
LEDGER = QA_DIR / "ledger.tsv"


# ---------------------------------------------------------- the seams ----
#
# `EB-180`. This file was 2,900 lines carrying four concerns; they
# now live one to a module and are re-exported here, so every name
# a caller, a test or the CLI reached for on
# `understudy.staged_turn` still resolves off it. Nothing below is
# new: each name is the definition that used to stand in this file.
#
#   staged_turn_shape     the questions, the refusals, the dials
#   staged_turn_model     what a staged turn IS: the board and the turn
#   staged_turn_parse     read a turn file, refuse two halves that disagree
#   staged_turn_stage     set the board in the real game, write the packet
#   staged_turn_grade     the form, and the falsifiers that refuse it
#   staged_turn_closeness the one quotable number, and the walk under it
#   staged_turn_ledger    one row per (turn, grader), and the UNRUN markers
#   staged_turn_execute   replay the grader's own line, prompts included
#
# `QA_DIR` AND `LEDGER` STAY HERE, with the paragraph that explains
# them: `QA_DIR` is what a caller reaches in and swaps, so it has
# one home and the seams read it back off this module at call time
# (`staged_turn_parse._st`).

from understudy.staged_turn_shape import (   # noqa: E402,F401  (re-export)
    DOMINANCE_GAP, FALSIFIERS, is_negative, MAX_LINES, MAX_MODALS_PER_PLAY,
    MODAL_KEY_FOR_SCREEN, MODAL_KEYS, _NEGATIVE_PHRASES, _NEGATIVE_WORDS,
    _norm, QUESTIONS, SLOT_FILE_NAME, TURN_DIR, USER_GRADER, WEIGHT_DISAGREE,
    WEIGHT_WINDOW)
from understudy.staged_turn_model import (   # noqa: E402,F401  (re-export)
    Board, FormError, _ID_RE, StagedTurn, STAGING_VERBS, TurnError)
from understudy.staged_turn_parse import (   # noqa: E402,F401  (re-export)
    all_turns, _check_assumptions_blind, _check_halves_agree, _declared_hp,
    EXPECTS_KEYS, INTENT_KEYS, _intent_words, _live_relics, load, parse,
    _parse_board, _parse_expects, _parse_forecast, _parse_resource_round,
    _parse_slots, turn_dir, wire_assumption_preflight)
from understudy.staged_turn_stage import (   # noqa: E402,F401  (re-export)
    assumption_preflight, assumption_rider_conflicts, declared_hand_keys,
    exact_hand_difference, export_packet, face_defect_preflight,
    PRINTED_RIDERS, _RIDER_CLAIM_RE, stage_board, staged_card_names,
    _staged_tags, _StagingComplete, StagingPolicy)
from understudy.staged_turn_grade import (   # noqa: E402,F401  (re-export)
    apply_falsifiers, forecast_answers, grade, grader_id, load_form)
from understudy.staged_turn_closeness import (   # noqa: E402,F401  (re-export)
    build_combat_state, _closeness, closeness, closeness_observed,
    _enumerate_lines, observed_state, _TooManyLines, WIRE_RESOURCES)
from understudy.staged_turn_ledger import (   # noqa: E402,F401  (re-export)
    build_ledger, _cell, DECIDING_ROLE, grader_role, is_down_weighted,
    LEDGER_COLUMNS, LEDGER_LOCK, ledger_rows, _line_titles, live_enemy_count,
    mark_unreached, mark_unrun, _packet_seed, _packet_titles, q2_agrees,
    _row_instance, unreached_boards, UNREACHED_NOTE, unreached_slots,
    unrun_boards, UNRUN_NOTE, _yn)
from understudy.staged_turn_execute import (   # noqa: E402,F401  (re-export)
    board_differences, execute_steps, ExecuteRunner, _outcome, parse_answers)


# ------------------------------------------------------------------ main ---

def cmd_check(args) -> int:
    paths = [Path(args.file)] if args.file else all_turns()
    if not paths:
        print("no turn files found", file=sys.stderr)
        return 1
    bad = 0
    loaded: list[StagedTurn] = []
    for p in paths:
        try:
            t = load(p)
            face_defect_preflight(t)
            assumption_preflight(t)
            loaded.append(t)
            print(f"OK   {p.name}: id={t.id} {len(t.staging)} staging step(s), "
                  f"{len(t.board.hand)} card(s) in hand, "
                  f"{len(t.board.enemies)} enem(ies), "
                  f"{len(t.assumptions)} assumption(s)"
                  + (", exact_hand" if t.exact_hand else ""))
        except (TurnError, scenario.ScenarioError, yaml.YAMLError) as e:
            bad += 1
            print(f"BAD  {p.name}: {e}", file=sys.stderr)
    # EB-202. A slot's threshold against what its own board set can produce.
    # Checked over whole DIRECTORIES, because a round is a directory: checking
    # one file would compute a ceiling of one and pass everything.
    bad += slot_report(loaded)
    return 1 if bad else 0


def slot_report(turns: Sequence["StagedTurn"]) -> int:
    """Print each counting slot's ceiling. Returns the number unreachable.

    `slot_plan` is imported HERE: it reads the card sheets and this module
    builds the blind packet (see `SLOT_FILE_NAME`).
    """
    from understudy import slot_plan
    try:
        report, refusals = slot_plan.check_round(turns)
    except slot_plan.SlotError as exc:
        print(f"SLOTS BAD  {exc}", file=sys.stderr)
        return 1
    for row in report:
        mark = "OK  " if row["reachable"] else "LOW "
        print(f"SLOT {mark} {row['slot']}: threshold {row['threshold']}, "
              f"ceiling {row['ceiling']} of {row['boards']} board(s)"
              + (f"  [{', '.join(row['qualifying'])}]"
                 if row["qualifying"] else ""))
    for line in refusals:
        print(f"SLOT REFUSED  {line}", file=sys.stderr)
    return len(refusals)


def cmd_closeness(args) -> int:
    turn = load(args.file)
    observed = turn_dir(turn.id) / "observed.json"
    if args.observed and not observed.is_file():
        print(f"no observed board at {observed}; stage the turn first",
              file=sys.stderr)
        return 2
    if args.observed:
        result = closeness_observed(
            json.loads(observed.read_text(encoding="utf-8")),
            pilot=turn.board.pilot, prototype=turn.prototype)
    else:
        result = closeness(turn.board, prototype=turn.prototype)
    d = turn_dir(turn.id)
    d.mkdir(parents=True, exist_ok=True)
    (d / "closeness.json").write_text(
        json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"turn: {turn.id}   pilot: {turn.board.pilot}   "
          f"source: {result['source']}")
    print(f"GUARDRAIL: {qa_packet.PACKET_GUARDRAIL}")
    if not result["applicable"]:
        print(f"NOT READ: {result['reason']}")
        return 0
    print(f"gap {result['gap']:.4f}  (top1 {result['top1']:.3f}, "
          f"top2 {result['top2']:.3f}) over {result['lines_considered']} "
          f"line(s); DOMINANCE_GAP {DOMINANCE_GAP}")
    for line in result["lines"]:
        print(f"  {line['score']:8.3f}  {' + '.join(line['cards'])}")
    print(f"{result['verdict']}: {result['reason']}")
    for note in (result.get("observed_notes") or {}).get(
            "unmapped_resources") or []:
        print(f"  UNMAPPED RESOURCE (read as zero): {note}")
    print(f"closeness: {d / 'closeness.json'}")
    return 0


def cmd_stage(args) -> int:
    if not str(args.why).strip():
        print("stage needs a --why: it grants cards and writes a board",
              file=sys.stderr)
        return 2
    turn = load(args.file)
    # EB-169, and BEFORE the launch: `stage_board` boots the game.
    face_defect_preflight(turn)
    assumption_preflight(turn)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    log = scenario.LOG_DIR / f"staged-{turn.id}-{stamp}.jsonl"
    print(f"turn: {turn.id}  ({turn.character})")
    for a in turn.assumptions:
        print(f"  ASSUMES: {a}")
    print(f"GUARDRAIL: {bridge.GRANT_GUARDRAIL}")
    state, summary = stage_board(turn, args.why, hold=args.hold, out_path=log,
                                 seed=args.seed or None)
    # THE SEED THE GAME ACTUALLY USED, read back off the run rather than taken
    # from the request -- R95's rule, and the whole reason the packet can be
    # replayed at all. `--seed` re-stages a recorded board; with no `--seed`
    # the game rolls and this is where the roll is captured.
    report = export_packet(turn, state, run_seed=summary.get("seed"))
    print(f"\nlog:    {log}")
    print(f"packet: {report['packet_md']}")
    print(f"json:   {report['packet_json']}")
    print(f"sha256: {report['sha256']}")
    print(f"seed:   {report['run_seed']}"
          + ("  (as requested)" if args.seed else "  (game-generated)"))
    print(f"        {report['cards']} card(s) in hand, "
          f"{report['enemies']} enem(ies)")
    if args.hold:
        print("\nHOLDING: the game is still at the staged board.\n"
              "  Play the turn cold, then write your answers into a form "
              "(understudy/qa_form.md is the template) with\n"
              f"  grader.id = {USER_GRADER!r} and packet_sha256 = the hash "
              "above, and grade it with:\n"
              f"    python -m understudy.staged_turn grade {turn.id} "
              f"<your-form.json>")
    return 0


def cmd_grade(args) -> int:
    form = load_form(args.form)
    verdict = grade(args.turn_id, form)
    d = turn_dir(args.turn_id)
    d.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(verdict, indent=1) + "\n"
    name = f"verdict-{grader_id(form)}.json"
    (d / name).write_text(blob, encoding="utf-8")
    # The fixed path too: one turn has one verdict a reader can find without
    # knowing who graded it, and it is the most recent grade. The per-grader
    # copy beside it is what the ledger reads, so a second grader does not
    # erase the first.
    (d / "verdict.json").write_text(blob, encoding="utf-8")
    print(f"{verdict['verdict']}  {args.turn_id}  "
          f"(grader {grader_id(form)})")
    for reason in verdict["reasons"]:
        print(f"  REFUSED BY {reason}")
    # EB-203. The refusal names the play AND prints the hand's aimed cards --
    # half a message ("you played it at nobody") is not actionable by somebody
    # holding the page.
    targets = verdict.get("targets") or {}
    if "target_missing" in (verdict.get("refused_by") or []):
        for hit in targets.get("findings") or []:
            print(f"    play {hit['position']}: {hit['card']} takes a target "
                  f"and carried none")
        takes = targets.get("hand_takes_a_target") or []
        print(f"    cards in this hand that take a target: "
              f"{', '.join(takes) if takes else '(none)'}")
        print(f"    derived from {targets.get('derived_from')}")
    if verdict["verdict"] == "SURVIVES":
        print(f"  {verdict['survives_means']}")
        if not verdict["survives_alone"]:
            print(f"  NOT ALONE: {verdict['why_not_alone']}")
    print(f"verdict: {d / name}")
    return 0


def cmd_execute(args) -> int:
    if not str(args.why).strip():
        print("execute needs a --why: it grants cards and writes a board",
              file=sys.stderr)
        return 2
    from understudy import soak

    form = load_form(args.form)
    answers = parse_answers(getattr(args, "answer", None))
    path = next((p for p in all_turns() if load(p).id == args.turn_id), None)
    if path is None:
        print(f"no turn file with id {args.turn_id!r} under {TURN_DIR}",
              file=sys.stderr)
        return 2
    turn = load(path)
    d = turn_dir(turn.id)
    packet_json = d / "packet.json"
    if not packet_json.is_file():
        print(f"no packet at {packet_json}; stage the turn first",
              file=sys.stderr)
        return 2
    packet = json.loads(packet_json.read_text(encoding="utf-8"))

    # TWO REFUSALS BEFORE THE GAME IS EVEN LAUNCHED, and both are cheaper to
    # take here than to discover at the first play.
    given = str(form.get("packet_sha256") or "")
    if given and given != str(packet.get("packet_sha256") or ""):
        print(f"packet_mismatch: {FALSIFIERS['packet_mismatch']}\n"
              f"  form:   {given}\n"
              f"  packet: {packet.get('packet_sha256')}", file=sys.stderr)
        return 2
    seed = args.seed or packet.get("run_seed") or turn.seed
    if not seed:
        # THE ENCOUNTER IS GENERATED, so a replay with no seed is a replay
        # onto whatever the game felt like making. The first live `execute`
        # of this tool did exactly that and drew a different monster.
        print("no recorded run seed for this packet, so the encounter cannot "
              "be regenerated and a replay would be a replay of nothing. "
              "Re-stage the turn (a `stage` records the seed it ran on), or "
              "pass --seed.", file=sys.stderr)
        return 2

    stamp = time.strftime("%Y%m%d-%H%M%S")
    log = scenario.LOG_DIR / f"executed-{turn.id}-{stamp}.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)

    replay = scenario.Scenario(name=f"{turn.id}/executed",
                               character=turn.character,
                               steps=execute_steps(turn, form),
                               path=turn.path, seed=seed,
                               assumptions=turn.assumptions)
    print(f"turn: {turn.id}   grader: {grader_id(form)}   seed: {seed}")
    for match, choice in answers:
        print(f"  OPERATOR ANSWER: {match!r} -> {choice!r}")
    with log.open("w", encoding="utf-8") as fh:
        runner = ExecuteRunner(replay, args.why, out=fh, packet=packet,
                               answers=answers)
        runner.emit({"step": "execute_begin", "turn": turn.id,
                     "grader": grader_id(form), "seed_requested": seed,
                     "packet_sha256": packet.get("packet_sha256"),
                     "chosen_line": form.get("chosen_line"),
                     # EB-170. ON THE FIRST ROW OF THE LOG, so a reader who
                     # opens the replay learns before anything else that an
                     # answer came from the operator and not from the form.
                     "operator_answers": [{"match": m, "choice": c}
                                          for m, c in answers]})
        policy = scenario.ScenarioPolicy(runner, turns=1)
        summary = soak.run_scripted(policy, stamp, character=turn.character,
                                    max_fights=1, chosen_seed=seed,
                                    do_setup=not args.no_setup)
        # THE BRACKET IS THE WHOLE LINE, not the last play. `Runner.before`
        # is reset by every action step, so reading it here would report the
        # final card's own delta and call it the turn's. The `mark` step
        # emitted the board as it stood when the line began; that row is the
        # left-hand side.
        marks = [r for r in runner.rows if r.get("step") == "mark"]
        outcome = _outcome(marks[-1]["at"] if marks
                           else scenario.digest(runner.before),
                           scenario.digest(runner.state))
        runner.emit({"step": "execute_end", "ok": policy.ok,
                     "seed_used": summary.get("seed"),
                     "outcome": outcome, "run": summary})

    # `"ok" in r` AND NOT `step == "board_check"` ALONE. When the check fails,
    # `Runner.run` emits a SECOND row under the same step name -- its generic
    # `expect_failed` record, which carries no `ok` key -- and taking the last
    # row by step name picked that one and raised a KeyError while reporting
    # the very failure it was reporting. The failure row is still the source of
    # the difference, so it is read for its detail rather than dropped.
    checks = [r for r in runner.rows
              if r.get("step") == "board_check" and "ok" in r]
    failures = [r for r in runner.rows
                if r.get("step") == "board_check" and r.get("expect_failed")]
    if checks:
        board_check = checks[-1]
    elif failures:
        board_check = {"ok": False, "rule": failures[-1]["expect_failed"],
                       "differences": [failures[-1].get("detail", "")]}
    else:
        board_check = {"ok": False,
                       "differences": ["the board check was never reached"]}
    record = {
        "turn_id": turn.id,
        "grader": grader_id(form),
        # WHICH GAME REPLAYED IT. Two lanes replay two boards at once; a
        # record that does not say which process ran cannot be matched to a
        # log, a frame or a crash.
        "instance": bridge.current_label(),
        "packet_sha256": packet.get("packet_sha256"),
        "seed_requested": seed,
        "seed_used": summary.get("seed"),
        "seed_honoured": summary.get("seed") == seed,
        "board_check": board_check,
        "chosen_line": list(form.get("chosen_line") or []),
        "played": [r.get("step") for r in runner.rows
                   if str(r.get("step", "")).startswith("play ")],
        # EB-170. Every prompt the line met, whether it was answered, and by
        # WHOM -- `form` for the grader's own words, `operator` for an answer
        # read off the grader's q1 prose and stated on the command line.
        "modals": list(runner.modals),
        "operator_answers": [{"match": m, "choice": c} for m, c in answers],
        "operator_answers_used": list(runner.answers_used),
        "ok": bool(policy.ok),
        "failures": runner.failures,
        "outcome": outcome,
        "reading": ("diagnostic only, under Guardrail-7: a hand-set board "
                    "played once. A number here is evidence of a DEFECT or "
                    "of nothing at all -- never a comparison, never a "
                    "balance reading, and never a claim about the turn"),
        "guardrail": qa_packet.PACKET_GUARDRAIL,
        "log": str(log),
        "executed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    out_path = d / f"execute-{grader_id(form)}.json"
    out_path.write_text(json.dumps(record, indent=1, default=str) + "\n",
                        encoding="utf-8")
    print(f"log:    {log}")
    print(f"record: {out_path}")
    print(f"seed:   requested {seed}, ran {summary.get('seed')}")
    print("board:  " + ("MATCHES the packet" if board_check["ok"]
                        else "MISMATCH -- refused"))
    for diff in board_check["differences"]:
        print(f"        {diff}")
    for m in runner.modals:
        print(f"modal:  {m['screen']} {m['prompt']!r} -> "
              + (f"{m['choice']!r} ({m['source']})" if m["answered"]
                 else "UNANSWERED"))
    print(json.dumps(outcome, indent=1))
    return 0 if policy.ok else 1


def cmd_packet_section(args) -> int:
    """R221 item (4): the round's results block, written from the records."""
    from understudy import packet_section
    text = packet_section.render(args.slug, heading=args.heading or "")
    # The section quotes packet prose, and a packet is UTF-8. A Windows
    # console defaults to cp1252 and would raise on the first em-dash it was
    # handed, which is a generator that works on one operator's machine.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    sys.stdout.write(text)
    if args.write:
        out = packet_section.append_to(Path(args.write), text)
        print(f"appended to: {out}", file=sys.stderr)
    return 0


def cmd_ledger(args) -> int:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    text = build_ledger()
    with LEDGER_LOCK:
        LEDGER.write_text(text, encoding="utf-8")
    print(text, end="")
    print(f"\nledger: {LEDGER}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="parse only; no game involved")
    c.add_argument("file", nargs="?", default="")
    c.set_defaults(func=cmd_check)

    cl = sub.add_parser("closeness", help="the R213 F falsifier; no game")
    cl.add_argument("file")
    cl.add_argument("--observed", action="store_true",
                    help="read the board the grader actually saw, from the "
                         "observed.json a previous `stage` wrote, instead of "
                         "the file's declared mirror. The live board is the "
                         "one with the game's own opening hand in it")
    cl.set_defaults(func=cmd_closeness)

    s = sub.add_parser("stage", help="set the board and export a blind packet")
    s.add_argument("file")
    s.add_argument("--why", default="",
                   help="one line, logged on every row. REQUIRED")
    s.add_argument("--seed", default="",
                   help="re-stage a RECORDED board. The encounter is "
                        "generated from the run seed, so this is what makes "
                        "a packet reproducible; with no --seed the game rolls "
                        "and the roll is recorded into packet.json")
    s.add_argument("--hold", action="store_true",
                   help="leave the game at the staged board for a human to "
                        "play cold. Attaches to a game that is already up, "
                        "because a session that owns the launch kills it at "
                        "teardown")
    s.set_defaults(func=cmd_stage)

    g = sub.add_parser("grade", help="apply the falsifier rules to one form")
    g.add_argument("turn_id")
    g.add_argument("form")
    g.set_defaults(func=cmd_grade)

    e = sub.add_parser("execute", help="replay a graded line live")
    e.add_argument("turn_id")
    e.add_argument("form")
    e.add_argument("--why", default="")
    e.add_argument("--seed", default="",
                   help="override the seed recorded in packet.json. Normally "
                        "unnecessary and normally wrong")
    e.add_argument("--answer", action="append", default=[],
                   metavar="PROMPT=CHOICE",
                   help="EB-170. THE OPERATOR'S OWN ANSWER to a modal prompt "
                        "the form did not carry, for replaying a form written "
                        "before the `exhaust` / `choose` keys existed. The "
                        "left side matches the prompt text (or the screen "
                        "name); the right side is the PRINTED choice. Logged "
                        "as `source: operator` on the row and in the record, "
                        "never silently, and never over a form's own answer. "
                        "Repeatable; each is consumed at most once")
    e.add_argument("--no-setup", action="store_true")
    e.set_defaults(func=cmd_execute)

    ps = sub.add_parser("packet-section",
                        help="write a round's results block FROM the records")
    ps.add_argument("slug", help="the round's slug -- the records are "
                                 "review/qa/<slug>-t*/")
    ps.add_argument("--write", default="",
                    help="also APPEND the section to this packet file")
    ps.add_argument("--heading", default="",
                    help="override the section heading")
    ps.set_defaults(func=cmd_packet_section)

    ld = sub.add_parser("ledger", help="rebuild review/qa/ledger.tsv")
    ld.set_defaults(func=cmd_ledger)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except (TurnError, FormError, scenario.ScenarioError,
            qa_packet.PacketLeak, yaml.YAMLError) as exc:
        print(f"staged turn error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
