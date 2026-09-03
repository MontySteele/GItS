"""Read a turn file, and refuse one whose two halves disagree.

Cut out of `staged_turn.py` by `EB-180`: `parse`, `load`, the
`expects:` reader and the wire preflight that refuses a board whose
declared facts are not the wire's. Re-exported from `staged_turn.py`,
so `staged_turn.parse(blob, path)` still resolves.
"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from understudy import adapter, qa_packet, scenario

from understudy.staged_turn_model import (Board, _ID_RE, StagedTurn,
                                          STAGING_VERBS, TurnError)
from understudy.staged_turn_shape import SLOT_FILE_NAME, TURN_DIR


def _st():
    """`understudy.staged_turn` itself, imported at CALL time.

    `QA_DIR` is declared on the facade because that is where a caller (and
    the suite) reaches in and swaps it. Binding it here at import would take
    a private copy and the swap would never be seen.
    """
    from understudy import staged_turn
    return staged_turn


def parse(blob: dict[str, Any], path: Path | None = None) -> StagedTurn:
    if not isinstance(blob, dict):
        raise TurnError("a turn file is a mapping at the top level")
    for required in ("id", "character", "staging", "board"):
        if not blob.get(required):
            raise TurnError(f"missing '{required}'")
    turn_id = str(blob["id"])
    if not _ID_RE.match(turn_id):
        # The id names a directory under `review/qa/` and is printed into the
        # blind packet, so it is constrained at both ends: a path-safe slug,
        # and one the packet's own leak scrub will accept.
        raise TurnError(
            f"id {turn_id!r} must be a lowercase hyphenated slug -- it names "
            f"a directory under review/qa/ and is printed in the blind packet")

    raw_steps = blob["staging"]
    if not isinstance(raw_steps, list):
        raise TurnError("'staging' must be a list")
    steps: list[tuple[str, Any]] = []
    for i, entry in enumerate(raw_steps):
        if not isinstance(entry, dict) or len(entry) != 1:
            raise TurnError(
                f"staging step {i}: each step is a single-key mapping; "
                f"got {entry!r}")
        verb, raw = next(iter(entry.items()))
        if verb == "clear_hand":
            # EB-165. The verb is real and the scenario pack may write it; a
            # TURN may not, because here its position is load-bearing and the
            # tool owns it. Declare `exact_hand: true` and it is prepended.
            raise TurnError(
                f"staging step {i}: a turn does not write 'clear_hand' -- its "
                f"POSITION is the whole door, and after a grant it would empty "
                f"the declared hand. Declare `exact_hand: true` at the top "
                f"level and the clear is run before the first grant")
        if verb not in STAGING_VERBS:
            raise TurnError(
                f"staging step {i}: '{verb}' is not a staging verb. A staged "
                f"turn sets a BOARD; the line is the grader's answer, not the "
                f"file's. One of: " + ", ".join(STAGING_VERBS))
        body = scenario._as_body(verb, raw)
        scenario._validate(i, verb, body)
        steps.append((verb, body))

    board = _parse_board(blob["board"])
    turn = StagedTurn(
        id=turn_id, character=str(blob["character"]), staging=steps,
        board=board, path=path, seed=blob.get("seed") or None,
        notes=str(blob.get("notes") or ""),
        assumptions=[str(a) for a in (blob.get("assumptions") or [])],
        prototype=bool(blob.get("prototype", False)),
        exact_hand=bool(blob.get("exact_hand", False)),
        slots=_parse_slots(blob.get("slots")),
        resource_round=_parse_resource_round(blob, path),
        forecast=_parse_forecast(blob.get("forecast")),
        replay_next_turn=bool(blob.get("replay_next_turn", False)),
        expects=_parse_expects(blob.get("expects")))
    _check_halves_agree(turn)
    _check_assumptions_blind(turn)
    return turn


def _parse_slots(raw: Any) -> list[str]:
    """R221 B's `slots:` key: a list of short registered-slot names, or absent.

    Refused rather than coerced. A slot name reaches the ledger, the packet's
    results section and the stopping rule, so a mapping or a bare string here
    would silently become a slot nobody registered.
    """
    if raw in (None, "", []):
        return []
    if not isinstance(raw, list) or not all(
            isinstance(s, str) and s.strip() for s in raw):
        raise TurnError(
            "'slots' is a list of non-empty strings -- the registered "
            "prediction slots this board is evidence about (R221 B). Omit it "
            "and the board carries one slot, its own id")
    return [s.strip() for s in raw]


def _parse_resource_round(blob: dict[str, Any], path: Path | None) -> Any:
    """EB-236's `resource_round:` block, or None. Refuses, never coerces.

    The import is LAZY -- `slot_plan` reads the card sheets, this module
    builds the blind packet, and the two are kept a function call apart on
    purpose (see `SLOT_FILE_NAME` and `slot_report`).
    """
    raw = blob.get("resource_round")
    if raw is None:
        return None
    from understudy import slot_plan
    try:
        return slot_plan.parse_resource_round(raw, where=str(path or blob["id"]))
    except slot_plan.BoardDesignError as exc:
        raise TurnError(str(exc)) from exc


def _parse_forecast(raw: Any) -> list[str]:
    """`forecast:` -- the pre-commit questions, or absent. Refuses, never
    coerces. Blindness is checked with the assumptions, since these are
    printed on the page beside them."""
    if raw in (None, "", []):
        return []
    if not isinstance(raw, list) or not all(
            isinstance(q, str) and q.strip() for q in raw):
        raise TurnError(
            "'forecast' is a list of non-empty question strings, printed at "
            "the top of the blind packet and answered BEFORE the line. Omit "
            "it and the board asks for no forecast")
    return [q.strip() for q in raw]


# ------------- EB-240: the assumptions the wire can be asked about ---------

EXPECTS_KEYS = ("relics", "hp", "intent")

# The two fields an `expects.intent` entry may carry, and the vocabulary is
# `adapter._intent`'s, not the wire's: `kind` is `attack` or the zero-damage
# beat every non-damaging telegraph parses to, `amount` is the number the
# label prints. Written in the board's own existing spelling -- `board:`
# enemies already carry `intent: {kind: attack, amount: 16}` for the shadow
# sim -- so a board declares its telegraph in one vocabulary, not two.
INTENT_KEYS = ("kind", "amount", "times")


def _parse_expects(raw: Any) -> dict[str, Any]:
    """`expects:` -- the structured, checkable half of `assumptions:`, or
    absent. Refuses, never coerces, for the reason every other block here
    does: a declaration that is silently reinterpreted is a declaration that
    can be false without anybody being told.

    Three keys, and all are optional inside it:

      * `relics:` a list of the run's relics by PRINTED NAME, and it means
        EXACTLY that list -- an extra relic on the wire is a mismatch, which
        is precisely the case `KLEESPARK-BT2` printed and nothing caught.
      * `hp:` a mapping of `who` (`player`, or one of `scenario`'s enemy
        symbols) to the HP the board expects to READ. It is for a body no
        `set_hp` step writes; a body one does write is checked automatically
        and does not need declaring.
      * `intent:` a mapping of `who` to the TELEGRAPH the board expects that
        enemy to be showing -- `{kind: attack, amount: 16}`, `kind` required
        and the numbers optional (`EB-244`). It is the leg BT3 needed: the
        encounter is generated from the seed and no staging step writes an
        intent, so a board is free to say what the enemy is about to do and
        be wrong, and both BT3 boards were. Declared and not automatic, for
        the reason relics are: the `board:` mirror's enemy names are the
        SHADOW SIM's symbols ("Act 1 enemy"), not wire symbols, so there is
        no name to resolve a mirror against.
    """
    if raw in (None, "", {}):
        return {}
    if not isinstance(raw, dict) or not raw:
        raise TurnError(
            "'expects' is a mapping of wire facts this board asserts -- "
            "'relics' (a list of printed names, meaning exactly those), "
            "'hp' (who -> the HP the board expects to read) and 'intent' "
            "(who -> the telegraph it expects to be showing). Omit it and "
            "the board asserts nothing a machine can check")
    unknown = sorted(k for k in raw if k not in EXPECTS_KEYS)
    if unknown:
        raise TurnError(
            f"'expects' knows {', '.join(EXPECTS_KEYS)} and nothing else; "
            f"got {', '.join(unknown)}. A key nobody reads is an assumption "
            f"that looks checked and is not")
    out: dict[str, Any] = {}
    if "relics" in raw:
        relics = raw["relics"]
        if not isinstance(relics, list) or not all(
                isinstance(r, str) and r.strip() for r in relics):
            raise TurnError(
                "'expects.relics' is a list of non-empty printed relic names "
                "-- the run's relics, exactly those. An empty list is written "
                "as [] and means the run carries none")
        out["relics"] = [r.strip() for r in relics]
    if "hp" in raw:
        hp = raw["hp"]
        if not isinstance(hp, dict) or not hp or not all(
                isinstance(k, str) and k.strip()
                and isinstance(v, int) and not isinstance(v, bool)
                for k, v in hp.items()):
            raise TurnError(
                "'expects.hp' is a mapping of who -> whole-number HP, e.g. "
                "{player: 42, first: 55}")
        out["hp"] = {str(k).strip(): int(v) for k, v in hp.items()}
    if "intent" in raw:
        intent = raw["intent"]
        if not isinstance(intent, dict) or not intent or not all(
                isinstance(k, str) and k.strip() for k in intent):
            raise TurnError(
                "'expects.intent' is a mapping of who -> the telegraph the "
                "board expects, e.g. {first: {kind: attack, amount: 16}}")
        declared: dict[str, dict[str, Any]] = {}
        for who, spec in intent.items():
            if not isinstance(spec, dict) or not spec.get("kind") \
                    or not isinstance(spec.get("kind"), str) \
                    or not str(spec["kind"]).strip():
                raise TurnError(
                    f"'expects.intent[{who!r}]' needs a 'kind' -- 'attack', "
                    f"or the zero-damage beat every non-damaging telegraph "
                    f"reads as; got {spec!r}")
            unknown = sorted(k for k in spec if k not in INTENT_KEYS)
            if unknown:
                raise TurnError(
                    f"'expects.intent[{who!r}]' knows "
                    f"{', '.join(INTENT_KEYS)} and nothing else; got "
                    f"{', '.join(unknown)}. A field nobody reads is an "
                    f"assumption that looks checked and is not")
            entry: dict[str, Any] = {"kind": str(spec["kind"]).strip()}
            for num in ("amount", "times"):
                if num in spec:
                    if not isinstance(spec[num], int) \
                            or isinstance(spec[num], bool):
                        raise TurnError(
                            f"'expects.intent[{who!r}].{num}' is a whole "
                            f"number; got {spec[num]!r}")
                    entry[num] = int(spec[num])
            declared[str(who).strip()] = entry
        out["intent"] = declared
    return out


def _live_relics(state: dict[str, Any]) -> list[str]:
    """The run's relics off the wire, by printed name. The same field the
    blind page prints (`EB-238`), read here rather than off the page, because
    the page is what a mismatch would already have gone out on."""
    out = []
    for r in (state.get("player") or {}).get("relics") or []:
        if isinstance(r, dict) and str(r.get("name") or "").strip():
            out.append(str(r["name"]).strip())
    return out


def _declared_hp(turn: StagedTurn) -> dict[str, int]:
    """Every HP this board asserts, `who` -> amount: the `set_hp` steps
    (automatic -- the step IS the declaration) with `expects.hp` on top,
    which is how a board says a thing about a body it does not write. The
    LAST `set_hp` for a `who` is the one that stands, because it is the one
    the game ran."""
    out: dict[str, int] = {}
    for verb, body in turn.staging:
        if verb == "set_hp":
            out[str(body.get("who") or "player").strip()] = int(body["amount"])
    out.update(turn.expects.get("hp") or {})
    return out


def _intent_words(spec: dict[str, Any]) -> str:
    """One telegraph in the board's own vocabulary: `attack 16`, `attack 7
    x3`, `block 0`. Only the fields present are spoken, so a declaration by
    kind alone is quoted back as kind alone."""
    out = str(spec.get("kind") or "?")
    if "amount" in spec:
        out += f" {spec['amount']}"
    if spec.get("times", 1) not in (None, 1):
        out += f" x{spec['times']}"
    return out


def wire_assumption_preflight(turn: StagedTurn,
                              state: dict[str, Any]) -> None:
    """`EB-240`. Refuse a staged board whose declared facts are not the wire's.

    WHY THERE IS A CHECK HERE AT ALL. A board's `assumptions:` block is
    printed into the blind packet verbatim and a reader does arithmetic on
    it. `KLEESPARK-BT2` shipped two false ones on all three boards -- one
    relic asserted where the run carried two, and `set_hp: {who: first,
    amount: 55}` against live bodies of 45, 46 and 40 -- and neither was
    catchable, because nothing compared a printed assertion against the
    machine. Both were harmless there and neither is harmless by
    construction: the HP one is what `no lethal line` rests on, and it held
    by 5.

    WHY IT CHECKS THESE TWO AND NOT THE PROSE. `set_hp` is a step the board
    already wrote down, so reading it back costs the file nothing and catches
    a write the game did not take. Relics are the case that needs a
    DECLARATION, because a relic list is a fact about the RUN that no staging
    step sets -- and a board that declares none is not thereby asserting none,
    it is asserting nothing, which is the state every board written before
    this row is in.

    THE THIRD LEG (`EB-244`) is the enemy's TELEGRAPH, and it is the same
    class of falsehood on the one fact the first two could not see. The
    encounter is generated from the seed and no staging step writes an
    intent, so a board can say what the enemy is about to do and be wrong:
    both `KLEESPARK-BT3` boards printed "one enemy telegraphing an attack for
    16" while `t01` drew a Debuff and `t02` an attack for 12. It was causal,
    not cosmetic -- `t01` holds no Attack, so against a Debuff no intent
    could change the line, both deciding forms were refused
    `intent_insensitive`, and `G1`/`G2`/`G4` graded UNREACHED. Declared, like
    relics, because the `board:` mirror names its enemies in the shadow sim's
    vocabulary and those names resolve against no wire.

    RAISED AT STAGE TIME, ON THE LIVE STATE, so the refusal lands before a
    packet is written, before a reader is paid for and before a grade exists
    to be corrupted. Nothing here re-reads or re-grades a published round
    (R101b) -- the boards under `understudy/turns/klee-sparks-bt2r/` and
    earlier are records and are not edited.
    """
    problems: list[str] = []

    want = turn.expects.get("relics")
    if want is not None:
        live = _live_relics(state)
        fold = [r.casefold() for r in live]
        missing = [r for r in want if r.casefold() not in fold]
        extra = [r for r in live
                 if r.casefold() not in [w.casefold() for w in want]]
        if missing or extra:
            problems.append(
                "relics: the board declares "
                + (", ".join(repr(r) for r in want) or "(none)")
                + " and the wire carries "
                + (", ".join(repr(r) for r in live) or "(none)")
                + (f" -- missing {', '.join(repr(r) for r in missing)}"
                   if missing else "")
                + (f" -- unexpected {', '.join(repr(r) for r in extra)}"
                   if extra else ""))

    for who, amount in sorted(_declared_hp(turn).items()):
        blob = scenario._who_blob(state, who)
        if not blob:
            problems.append(
                f"hp: the board declares {who!r} at {amount} and the wire has "
                f"no such creature to read")
            continue
        live_hp = blob.get("hp")
        if live_hp is None or int(live_hp) != int(amount):
            problems.append(
                f"hp: the board declares {who!r} at {amount} and the wire "
                f"reads {live_hp if live_hp is not None else '(no hp field)'}")

    # EB-244: the telegraph. Read through `adapter._intent`, which is the
    # parse the pilot and the falsifier already take -- so a board is checked
    # against the intent the machinery ACTS on, not against a label somebody
    # transcribed. The printed telegraph is carried into the message as well
    # (`qa_packet._intent`), because "block 0" is what a Debuff parses to and
    # is not what the page said.
    for who, want in sorted((turn.expects.get("intent") or {}).items()):
        blob = scenario._who_blob(state, who)
        if not blob:
            problems.append(
                f"intent: the board declares {who!r} showing "
                f"{_intent_words(want)} and the wire has no such creature "
                f"to read")
            continue
        raw = blob.get("intents") or blob.get("intent")
        live = adapter._intent(raw)[0]
        if any(live.get(k) != v for k, v in want.items()):
            printed = qa_packet._intent(raw)
            shown = ", ".join(x for x in (printed["kind"], printed["label"],
                                          printed["text"]) if x)
            problems.append(
                f"intent: the board declares {who!r} showing "
                f"{_intent_words(want)} and the wire telegraphs "
                f"{_intent_words(live)}"
                + (f" -- the page prints {shown!r}" if shown else ""))

    if problems:
        raise TurnError(
            f"{turn.id}: the board's declared assumptions are not the wire's, "
            f"so the packet would print a falsehood a reader does arithmetic "
            f"on (`EB-240`). " + "; ".join(problems))


def _check_assumptions_blind(turn: StagedTurn) -> None:
    """The assumptions are folded into the packet's disclosures VERBATIM, so
    they are scrubbed by the same rules as a card face -- and the scrub runs
    at export, AFTER the game has been booted, embarked and boarded. Refusing
    here, at parse, is what makes `check` the gate it says it is: the first
    slice cited a register id in an assumption, `check` passed all eleven
    files, and the first `stage` burned a real launch to learn what a parse
    could have said.
    """
    bad = qa_packet.leaks(list(turn.assumptions))
    if bad:
        rule, hit, ctx = bad[0]
        raise TurnError(
            f"assumption leaks design vocabulary ({rule}: {hit!r} in "
            f"{ctx[:80]!r}): assumptions are printed in the blind packet, "
            f"so they follow the packet's own scrub -- state the fact, not "
            f"the citation")
    # The forecast questions are printed on the same page and follow the same
    # scrub, for the same reason: a question naming an id would teach a
    # reader the one thing the page exists to withhold.
    bad = qa_packet.leaks(list(turn.forecast))
    if bad:
        rule, hit, ctx = bad[0]
        raise TurnError(
            f"forecast question leaks design vocabulary ({rule}: {hit!r} in "
            f"{ctx[:80]!r}): it is printed at the top of the blind packet -- "
            f"ask it in the vocabulary the page prints")


def _parse_board(raw: Any) -> Board:
    if not isinstance(raw, dict):
        raise TurnError("'board' must be a mapping")
    for required in ("character", "hand", "enemies"):
        if not raw.get(required):
            raise TurnError(f"board: missing '{required}'")
    enemies = []
    for i, e in enumerate(raw["enemies"]):
        if not isinstance(e, dict) or not e.get("name"):
            raise TurnError(f"board enemy {i}: needs a mapping with a 'name'")
        enemies.append(dict(e))
    return Board(
        character=str(raw["character"]),
        hand=[str(c) for c in raw["hand"]],
        enemies=enemies,
        pilot=str(raw.get("pilot") or "generic"),
        hp=int(raw.get("hp", 70)),
        max_hp=int(raw.get("max_hp", raw.get("hp", 70))),
        block=int(raw.get("block", 0)),
        energy=int(raw.get("energy", 3)),
        turn=int(raw.get("turn", 1)),
        resources={str(k): int(v) for k, v in (raw.get("resources") or {}).items()},
    )


def _check_halves_agree(turn: StagedTurn) -> None:
    """The staged hand and the mirrored hand are the same multiset of cards.

    Checked through `scenario.card_key`, which folds the three spellings this
    repo uses. Without this, `closeness` would answer about a board nobody
    staged and the packet would show a board nobody scored -- and the two
    would look like one reading.
    """
    staged = sorted(scenario.card_key(str(b.get("card")))
                    for v, b in turn.staging
                    if v == "give" and str(b.get("pile") or "hand") == "hand"
                    for _ in range(int(b.get("count", 1))))
    mirrored = sorted(scenario.card_key(c) for c in turn.board.hand)
    if staged != mirrored:
        raise TurnError(
            f"the staged hand and board.hand disagree: staged {staged}, "
            f"board {mirrored}. They describe the same board, so a card in "
            f"one and not the other is a falsifier reading taken on a board "
            f"nobody staged")


def load(path: str | Path) -> StagedTurn:
    p = Path(path)
    return parse(yaml.safe_load(p.read_text(encoding="utf-8")), path=p)


def all_turns(directory: Path | None = None) -> list[Path]:
    """Every turn file, RECURSIVELY.

    Recursive because a slice is a set of MATCHED PAIRS that only mean
    anything together, so they live in one subdirectory
    (`understudy/turns/kokomi-slice-1/`) rather than scattered through a flat
    list beside the worked example. `fixtures/` is excluded by name: it holds
    grader FORMS, not turns, and `check` would report every one of them BAD.
    `slots.yaml` is excluded for the same reason: it is EB-202's slot
    registration for the round it sits in, not a board, and `check` reads it
    through `slot_plan` rather than as a turn.
    """
    d = directory or TURN_DIR
    if not d.is_dir():
        return []
    return sorted(path for path in d.rglob("*.yaml")
                  if "fixtures" not in path.relative_to(d).parts
                  and path.name != SLOT_FILE_NAME)


def turn_dir(turn_id: str) -> Path:
    return _st().QA_DIR / turn_id
