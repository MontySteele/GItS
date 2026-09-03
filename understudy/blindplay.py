"""EB-167/EB-168: DESIGN-BLIND PLAY of any screen, and the seat that plays it.

`qa_packet.py` renders ONE staged combat turn design-blind. This module is the
same guarantee widened to every screen the wire can return -- map, rewards,
shop, rest, event, the three selection overlays, game over -- plus a command
grammar in player language, plus the smallest driver that lets an independent
model actually play through it.

WHAT IS DIFFERENT FROM `harness state`, AND WHY THIS FILE EXISTS AT ALL
-----------------------------------------------------------------------
`understudy/harness.py` renders a screen with `policy_v0`'s recommendation
printed beside it. That is exactly right for the Phase-0 divergence loop and
exactly wrong here: a tester who is shown what the sim would do is not reading
the board, and R217 E minted this row saying so in as many words. So this
module is built on `qa_packet`'s scrubber and on the title-resolution
convention `staged_turn.execute` and `naming` follow, and NEVER on `harness`.
The AST pin in `tier0/tests/test_understudy_blindplay.py` keeps it that way:
no `harness`, no `policy_v0`, no `policy_v1`, and nothing from `tier0` /
`tier05` -- which also means no `soak`, no `scenario` and no `adapter`, each of
which reaches a sheet loader transitively.

THREE INVARIANTS, ALL TESTED
----------------------------
  * **EVERY OBSERVATION IS SCRUBBED.** `observation()` copies field by field
    from an allowlist, exactly as `qa_packet.build` does, and the finished
    structure AND the rendered Markdown both go through
    `qa_packet.assert_blind`. A leak raises `PacketLeak` and the observation is
    not returned, let alone shown. The one exemption is the wire's own screen
    name (`qa_packet.leaks(..., allow=...)`), passed one token at a time, and
    it exists only so a refusal can say WHICH screen it refused.
  * **AN UNKNOWN SCREEN IS `TOOL-BLOCKED`, NEVER A HEURISTIC.** A `state_type`
    this module does not know, an overlay, a minigame, or a registered hazard
    event renders as `TOOL-BLOCKED: <state_type>` and the driver STOPS. There
    is no "well, press the first button" path anywhere in this file --
    `soak._mechanical_action` has one because a soak's job is to keep moving,
    and a blind tester's job is the opposite.
  * **NOTHING BUT PRINTED FACES CROSSES THE LINE.** No card ids, no entity
    ids, no policy score, no EV, no design tag, no seed, no run comparison.
    Ids exist on this side of the line only long enough to build the POST:
    a title is resolved to a hand INDEX at the moment of posting, one frame
    later than which it would mean a different card (`naming.py:14-17`).

THE COMMAND GRAMMAR IS THE WHOLE INTERFACE
------------------------------------------
    play "<title>" [on "<enemy>"]      end turn        choose "<name>"
    skip            go "<node>"        buy "<item>"    rest
    upgrade ["<title>"]                remove ["<title>"]
    use potion "<title>" [on "<enemy>"]                confirm        proceed

Every name in it is a name the screen printed. The game prints an upgraded
card's own `+`, and the fold keeps it, so `Coral Guard` and `Coral Guard+` are
simply two names. A title matching two cards with DIFFERENT printed faces is
refused as ambiguous rather than guessed at, and BOTH sides are then reachable:
`"<title> (upgraded)"` and `"<title> (not upgraded)"` filter the hits, on
either side of the title, so echoing the screen back verbatim works (EB-173, a
live deadlock: neither copy was playable). A title matching two identical faces takes
the first, because two copies of one card are interchangeable and refusing
there would make a duplicate unplayable. A card the game says cannot be played,
or an item the run cannot afford, is refused WITH THE GAME'S OWN REASON where
the wire gives one.

THE SEAT, AND WHAT IS SEALED (R217 A/C/G)
-----------------------------------------
`session` runs ONE `codex exec` thread per run (`codex exec resume <id>` after
the first turn) so the tester keeps one context across the whole Act, which is
the difference between a run report and eleven disconnected turn reports. The
seat is the same one `seat.py` builds -- same sandbox, same three-source
transcript guard, same identity fill -- and the AUTHOR'S OWN MODEL FAMILY IS
REFUSED as tester: independence is by family, not by fresh context.

Sealed record: `understudy/logs/blindplay/<session>/` (gitignored) holds the
transcript and the model's records verbatim; `review/qa/blindplay/<session>/`
holds the identity block and those same records, committed, under the R217 G
label -- subjective feedback from an independent model playing the real game.
Useful for iteration; not human validation, not balance evidence, not
approval. It never enters an Understudy report, a win-rate table or a
measurement register.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from understudy import authorship, bridge, qa_packet, report, seat

# `klee-mod/local.props` is the machine's one statement of where the game is,
# and this is a DELIBERATE SECOND COPY of the four lines `soak.game_dir()`
# reads it with -- for the same reason `HAZARD_EVENTS` is copied above:
# importing `soak` here would pull `policy_v1` and every tier0 sheet loader
# into the design-blind module. Nothing below reads anything but a version
# string, and a missing file is answered with a reason, never a guess.
LOCAL_PROPS = Path(__file__).resolve().parents[1] / "klee-mod" / "local.props"


# ------------------------------------------------------------ the seams ----
#
# `EB-180`. This file was 4,898 lines carrying four concerns; they
# now live one to a module and are re-exported here, so every name a
# caller, a test or the CLI reached for on `understudy.blindplay`
# still resolves off `understudy.blindplay`. Nothing below is new:
# each name is the definition that used to stand in this file.
#
#   blindplay_shape    paths, screen registers, the two refusals
#   blindplay_read     printed text, folded names, the blobs behind them
#   blindplay_faces    one card, one option, one enemy, as printed
#   blindplay_board    combat, the pet, the meters, the map
#   blindplay_notes    the standing notes, and the arm-keyword glossary
#   blindplay_observe  `observation` -- the no-leak guarantee, once
#   blindplay_render   the observation as the page a tester is handed
#   blindplay_snapshot the wire snapshot, which is the grader's channel
#   blindplay_grammar  one line of player language, resolved
#   blindplay_session  one blind run, one command at a time
#   blindplay_record   the audit, and the two halves `seal` writes
#
# `LOCAL_PROPS` STAYS HERE, with the four lines that explain it: it
# is the path a caller reaches in and swaps, so it has one home and
# `blindplay_record` reads it back off this module at call time.

from understudy.blindplay_shape import (   # noqa: E402,F401  (re-export)
    BlindPlayError, CHARGE_SOURCE_LINE, COMBAT_SCREENS, FIGHT_OVERLAYS,
    HAZARD_EVENT_TITLES, HAZARD_EVENTS, _is_rate_limited,
    AURA_DURATION_TURNS, BOMB_GROWTH, FRAIL_BLOCK_PCT, VULNERABLE_TAKEN_PCT,
    WEAK_DEALT_PCT,
    KURAGE_COST_PER_ENERGY, LOG_ROOT, PLAY_GUARDRAIL, PROMPT_PATH,
    _RATE_LIMIT_MARKERS, RECORD_ROOT, REPO, SeatBudgetExhausted,
    SELECT_SCREENS, SETTLE_DELAY_S, SETTLE_TRIES, UNDRIVEN_SCREENS)
from understudy.blindplay_read import (   # noqa: E402,F401  (re-export)
    _blob, _chest_opening, _combat_torn_down, _despritify, _enemies,
    _entity_id, _fold, _hand, _icon_name, _ICON_SUBJECTS, _int, _label,
    _listing, _number_names, _player, _potions, _relics, _screen, settle,
    _SPRITE_TAG, _text, transient)
from understudy.blindplay_faces import (   # noqa: E402,F401  (re-export)
    _BARE_HOOK, _card_face, _card_title, _dedupe_text, _element,
    _ELEMENT_KEYWORD, EMPTY_SHELF, _enchantment, _enemy_key, _enemy_names,
    _DECK_MEMORY, _FIGHT_MEMORY, forget_deck, forget_fight, forget_shelves,
    _hazard, _hook_note, _intent, _intents, _is_aura, _meter_max,
    _named_option, _number_faces, _OPTION_KIND_KEYS, _OPTION_NAME_KEYS,
    _OPTION_TEXT_KEYS, _powers, relic_faces, remember_deck, remembered_deck,
    _reward_option, _SHELF_MEMORY, _shelf_kind, _shop_fingerprint,
    _shop_items, _shop_options, _SPARK_POWER)
from understudy.blindplay_board import (   # noqa: E402,F401  (re-export)
    ALREADY_UPGRADED, _bundle_cards, _carried_out_row, _combat,
    _event_options, kokomi_plans, kurage_memory, _map_ahead, _map_boss,
    _map_nodes, _map_options, NO_UPGRADE_DEFINED, _omitted_from_upgrade,
    _potion_slots, _preview_cards, _proceed_option, _pulse_phrase,
    _relic_options, _rest_options, _reward_items, _screen_cards,
    _selected_bundle, UNEXPLAINED_OMISSION, upgrade_deck_floor)
from understudy.blindplay_notes import (   # noqa: E402,F401  (re-export)
    _ARM_KEYWORD_RE, ARM_KEYWORDS, AURA_NOTE, _BASE_KEYWORD_RE, BASE_KEYWORDS,
    BOSS_ROOM, _elements_on_screen,
    _every_string, FROZEN_BOSS_CLAUSE, _GAME_KEYWORD_RE, GAME_KEYWORDS,
    HAND_REPEAT_NOTE, keyword_notes, METER_CAPPED_NOTE,
    METER_NOTE, PLAN_HYDRO_NOTE, POWER_NOTE, PREVIEW_LOCKED,
    REACTION_KEYWORDS,
    SELECTION_NOTE, TRANSFORM_NOTE, TRANSFORM_UNREADABLE, _wire_keyword_rows)
from understudy.blindplay_observe import (   # noqa: E402,F401  (re-export)
    observation)
from understudy.blindplay_render import (   # noqa: E402,F401  (re-export)
    _colliding, observe, render, _render_card, _render_intent,
    _render_intents, _render_options, _render_power, sha256, still_in_fight)
from understudy.blindplay_snapshot import (   # noqa: E402,F401  (re-export)
    ledger_rows, _snapshot_hand, _snapshot_meters, SNAPSHOT_VERBS,
    wire_snapshot)
from understudy.blindplay_grammar import (   # noqa: E402,F401  (re-export)
    act, AIMED_TARGETS, _buy, _card_face_key, _choose, Command, _confirm,
    _full_slots, _go, _index_choice, _is_upgraded, _match, _match_bundle,
    _not_in_battle, _numbered_titles, ORDINAL_ADVICE, parse_command,
    _pet_target, _play, _proceed, _QUALIFIER, _QUOTED, _refuse, Resolution,
    _resolve_enemy, _rest_keyword, SELF_TARGETS, _skip, _split_qualifier,
    _STALE_NUMBER, _use_potion, VERBS)
from understudy.blindplay_session import (   # noqa: E402,F401  (re-export)
    AUTHOR_FAMILY, Budget, check_independent, CodexThread, command_schema,
    FIGHT_QUESTIONS, forecast_block, MODEL_FAMILIES, model_family,
    RECORD_DISCLAIMER, record_schema, _result_line, RUN_QUESTIONS,
    ScriptedThread, ScriptedWire, Session, taken_line, Transcript)
from understudy.blindplay_record import (   # noqa: E402,F401  (re-export)
    AUDIT_EXTRA, audit_markdown, build_version, _game_dir, game_version,
    granted_arms, _json_field, leak_audit, meter_plays, notes_markdown,
    read_snapshots, record_markdown, seal, turn_notes)

# -------------------------------------------------------------------- CLI --

def _load_state(args) -> dict[str, Any]:
    """The live state, or a saved one.

    A saved file is either a raw wire state or one of the envelopes this repo
    already writes around one (`review/qa/<turn>/observed.json` keeps it under
    `state`), so the recorded material is usable as a fixture without being
    unwrapped by hand first.

    A LIVE read settles first and a saved one never does (`EB-175`): the
    operator driving `observe` / `act` by hand reads the wire on exactly the
    frames the driver does, and a fixture is a frame somebody chose.
    """
    if not args.raw_file:
        return settle(bridge.get_state())
    blob = json.loads(Path(args.raw_file).read_text(encoding="utf-8"))
    inner = blob.get("state") if isinstance(blob, dict) else None
    if isinstance(inner, dict) and inner.get("state_type"):
        return inner
    return blob


def cmd_observe(args) -> int:
    state = _load_state(args)
    try:
        print(observe(state))
    except qa_packet.PacketLeak as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_act(args) -> int:
    # `EB-370`: `act` reads through `observation()` before it resolves
    # anything (`blindplay_grammar.act`), so a `PacketLeak` on the read path
    # it shares with `observe` used to reach here uncaught -- a seat that
    # typed `act` on a leaking board saw a Python traceback where `observe`
    # on the same board printed a clean one-line refusal. Same catch, same
    # line, same exit code.
    state = _load_state(args)
    try:
        res = act(state, args.command)
    except qa_packet.PacketLeak as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(res, indent=1, default=str))
    if not res["ok"]:
        return 1
    if args.raw_file or args.dry_run:
        return 0
    post = dict(res["post"] or {})
    action = post.pop("action")
    result = bridge.post(action, **post)
    # `EB-341`: the row that was taken, then the game's answer -- the same two
    # lines, in the same order, the session hands its seat.
    for line in (taken_line(res), _result_line(result)):
        if line:
            print(line)
    return 0


def build_thread(log_dir: Path, backend: str, model: str) -> Any:
    """The tester for one run: the Codex seat, or the local backend.

    ONE function so the two cannot drift on the things they share. Both are
    handed the same `log_dir`, both answer `identity()` / `send()` /
    `close()`, and `Session` -- which owns the prompt, the schema, the loop,
    the records and the budgets -- never learns which it got. The CODEX PATH
    IS UNCHANGED and is what an unflagged `session` still runs.

    `local_play` is imported HERE rather than at module scope so this module's
    import list stays what `test_blindplay_cannot_reach_a_sheet_or_a_policy`
    reads it as, and so an operator with no local endpoint configured never
    pays for the import.
    """
    if backend == "local":
        from understudy import local_play
        return local_play.thread(log_dir, model=model)
    # R217 C, asked before a process is started. The LOCAL path asks the same
    # question inside `LocalThread.__init__`, where the served model's own
    # name is finally known.
    resolved = model or seat.DEFAULT_MODEL
    check_independent(resolved)
    return CodexThread(log_dir, model=resolved)


def cmd_session(args) -> int:
    session_id = args.session_id or time.strftime("%Y%m%d-%H%M%S",
                                                  time.gmtime())
    log_dir = LOG_ROOT / session_id
    from understudy import local_play
    try:
        thread = build_thread(log_dir, args.backend, args.model)
    except BlindPlayError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except local_play.LocalPlayError as exc:
        print(f"local backend: {exc}", file=sys.stderr)
        return 2
    version, source = build_version()
    game, game_source = game_version()
    seed = bridge.current_seed() or ""
    budget = Budget(max_actions=args.max_actions,
                    max_wall_s=args.max_wall_s,
                    max_refusals=args.max_refusals,
                    max_stalls=args.max_stalls)
    try:
        session = Session(thread, wire=bridge, session_id=session_id,
                          budget=budget,
                          forecast=list(args.forecast or []))
        # The local backend keeps its per-screen reply row -- the scratchpad
        # it stripped, the token counts, the wall clock -- in the SESSION's
        # transcript rather than a second log, so a reader follows one file.
        # Attached rather than passed, because `Session` builds the transcript
        # and the thread is older than the session it is handed to.
        if hasattr(thread, "transcript"):
            thread.transcript = session.transcript
        summary = session.run()
    finally:
        thread.close()
    arms, arms_source = granted_arms(seed)
    identity = {**thread.identity(), "build_version": version,
                "build_version_source": source,
                "game_version": game, "game_version_source": game_source,
                "run_seed": seed,
                "arms_granted": arms, "arms_granted_source": arms_source,
                "prompt_sha256": summary["prompt_sha256"],
                "actions": summary["actions"],
                "termination": summary["termination"]}
    if summary.get("forecast_questions"):
        identity["forecast_asked"] = len(summary["forecast_questions"])
    path = seal(summary, identity, log_dir=session.dir)
    print(f"transcript: {summary['transcript']}")
    print(f"record:     {path}")
    print(f"actions:    {summary['actions']}   "
          f"stopped: {summary['termination']}")
    return 0


SECTIONS = ("## Turn by turn", "## Leak audit")


def _splice(record: Path, heading: str, block: str) -> None:
    """Replace one appended section of a sealed record, keeping the others.

    The record is the head the seal wrote plus appended sections in `SECTIONS`
    order. Each post-hoc writer replaces its own section and never truncates a
    sibling — the bug this exists to stop is a second writer silently dropping
    the first one's block.
    """
    text = record.read_text(encoding="utf-8")
    blocks: dict[str, str] = {}
    for name in SECTIONS:
        head, sep, tail = text.partition("\n" + name)
        if sep:
            blocks[name] = (sep.lstrip("\n") + tail).rstrip() + "\n"
            text = head
    blocks[heading] = block.rstrip() + "\n"
    # A block may itself have swallowed a later sibling on an older record.
    for name in SECTIONS:
        if name in blocks and name != heading:
            body, sep, _ = blocks[name].partition("\n## ")
            if sep:
                blocks[name] = body.rstrip() + "\n"
    out = text.rstrip()
    for name in SECTIONS:
        if name in blocks:
            out += "\n\n" + blocks[name].rstrip()
    record.write_text(out + "\n", encoding="utf-8")


def cmd_notes(args) -> int:
    """Carry the tester's per-turn sentences into the committed record.

    Separate from `session` for the reason `audit` is: it reads the gitignored
    turn pages of a run that has FINISHED and writes only the committed
    record, so a session sealed before this existed is still completable.
    """
    log_dir = LOG_ROOT / args.session_id
    if not log_dir.is_dir():
        raise BlindPlayError(f"no session log at {log_dir}")
    rows = turn_notes(log_dir)
    record = RECORD_ROOT / args.session_id / "record.md"
    if not record.is_file():
        raise BlindPlayError(f"no sealed record at {record}")
    _splice(record, "## Turn by turn", notes_markdown(rows))
    print(f"record: {record}")
    print(f"turns:  {len(rows)}")
    return 0


def cmd_audit(args) -> int:
    """Read back what the tester was shown, and say so in the record.

    Separate from `session` on purpose: the audit is a claim about a run that
    has FINISHED, and a session that crashed mid-run should still be auditable
    without re-running it. It reads the gitignored turn pages and writes only
    the committed record.
    """
    log_dir = LOG_ROOT / args.session_id
    if not log_dir.is_dir():
        raise BlindPlayError(f"no session log at {log_dir}")
    session = log_dir / "session.json"
    seed = ""
    if session.is_file():
        seed = _text(json.loads(session.read_text(encoding="utf-8"))
                     .get("run_seed"))
    audit = leak_audit(log_dir, seed)

    record = RECORD_ROOT / args.session_id / "record.md"
    if record.is_file():
        _splice(record, "## Leak audit", audit_markdown(audit))
        print(f"record:  {record}")
    print(f"scanned: {audit['observations']} observation(s)")
    print(f"hits:    {audit['total']}")
    for rule, n in sorted(audit["rules"].items()):
        print(f"  {rule}: {n}")
    return 0


def main(argv: list[str] | None = None) -> int:
    # EB-93: this entry point echoes shipped card titles, and two of them carry
    # a music note. A default Windows console is cp1252.
    report.console_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("observe", help="render the current screen, blind")
    o.add_argument("--raw-file", default="",
                   help="a saved wire state instead of the live one")
    o.set_defaults(func=cmd_observe)

    a = sub.add_parser("act", help="resolve one player-language command")
    a.add_argument("command")
    a.add_argument("--raw-file", default="",
                   help="resolve against a saved state and post nothing")
    a.add_argument("--dry-run", action="store_true",
                   help="resolve against the live state and post nothing")
    a.set_defaults(func=cmd_act)

    s = sub.add_parser("session", help="one blind thread plays the run")
    s.add_argument("--backend", choices=("codex", "local"), default="codex",
                   help="who plays. `codex` is the seat and the default and "
                        "is unchanged. `local` plays the same pages through "
                        "the OpenAI-compatible endpoint at "
                        "$GITS_LOCAL_MODEL_URL -- AN OPTION, not a seat: "
                        "the 2026-08-29 ADVANCE covered the staged "
                        "single-turn tester only and whole-run blind play by "
                        "a local model is a pick for [USER]")
    s.add_argument("--model", default="",
                   help=f"the codex model (default {seat.DEFAULT_MODEL}), or "
                        f"with --backend local the served model to ask for "
                        f"(default: whatever /v1/models reports)")
    s.add_argument("--session-id", default="")
    s.add_argument("--max-actions", type=int, default=60)
    s.add_argument("--max-wall-s", type=float, default=3600.0)
    s.add_argument("--max-refusals", type=int, default=3)
    s.add_argument("--max-stalls", type=int, default=6,
                   help="stop after this many identical screens running "
                        "(EB-173: a screen the tester cannot get off)")
    s.add_argument("--forecast", action="append", metavar="QUESTION",
                   help="EB-229: ask this question BEFORE the command on "
                        "every combat turn, and seal the answers with the "
                        "record. Repeatable, in the order the registration "
                        "numbers them. Omit it and the run is asked, sent "
                        "and sealed exactly as it always was.")
    s.set_defaults(func=cmd_session)

    u = sub.add_parser("audit", help="leak-audit a finished session's own "
                                     "observations and append the counts to "
                                     "its committed record")
    u.add_argument("session_id")
    u.set_defaults(func=cmd_audit)

    n = sub.add_parser("notes", help="carry a finished session's per-turn "
                                     "sentences into its committed record")
    n.add_argument("session_id")
    n.set_defaults(func=cmd_notes)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except BlindPlayError as exc:
        print(f"blind play error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
