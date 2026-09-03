"""The form, and the falsifiers that refuse it. No score, no verdict.

Cut out of `staged_turn.py` by `EB-180`: `load_form`,
`apply_falsifiers` and `grade`. Re-exported from `staged_turn.py`, so
`staged_turn.grade(turn_id, form)` still resolves.

THE FORM IS A FALSIFIER AND NOT A SCORE. Nothing here rates a turn or
ranks one; the only verdicts are REFUSED and SURVIVES, and SURVIVES
means `not yet falsified`.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from understudy import qa_packet

from understudy.staged_turn_closeness import closeness
from understudy.staged_turn_ledger import is_down_weighted
from understudy.staged_turn_model import FormError
from understudy.staged_turn_shape import (FALSIFIERS, is_negative, MODAL_KEYS,
                                          _norm, QUESTIONS)


def _st():
    """`understudy.staged_turn` itself, imported at CALL time.

    `QA_DIR` is declared on the facade because that is where a caller (and
    the suite) reaches in and swaps it. Binding it here at import would take
    a private copy and the swap would never be seen.
    """
    from understudy import staged_turn
    return staged_turn


def load_form(path: str | Path) -> dict[str, Any]:
    blob = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(blob, dict):
        raise FormError("a form is a JSON object")
    for key in ("grader", "chosen_line", *QUESTIONS):
        if key not in blob:
            raise FormError(f"the form has no {key!r}")
    grader = blob["grader"]
    if not isinstance(grader, dict) or not grader.get("id"):
        raise FormError("'grader' needs at least an 'id' -- the packet has to "
                        "record who answered it and on what")
    line = blob["chosen_line"]
    if not isinstance(line, list):
        raise FormError("'chosen_line' is an ordered list of plays")
    for i, play in enumerate(line):
        if not isinstance(play, dict) or not play.get("card"):
            raise FormError(f"chosen_line[{i}] needs a 'card' -- the PRINTED "
                            f"title, which is the only spelling the grader was "
                            f"shown")
        # EB-170. OPTIONAL and NULLABLE, so every form written before these
        # keys existed still loads unchanged. Both are stated in the PRINTED
        # vocabulary the grader was shown -- a card's title for the Exhaust
        # choice, an option's own text for a mode choice -- because that is
        # the only spelling a blind grader has.
        for key in MODAL_KEYS:
            if play.get(key) is not None and not isinstance(play[key], str):
                raise FormError(
                    f"chosen_line[{i}].{key} is the PRINTED text of the "
                    f"choice, as a string (or absent). Got "
                    f"{type(play[key]).__name__}")
    return blob


def grader_id(form: dict[str, Any]) -> str:
    return str((form.get("grader") or {}).get("id") or "unknown")


# ------------------------------------------------------------- the grade ---

def forecast_answers(form: dict[str, Any]) -> list[str]:
    """The form's `forecast` list as strings. `EB-236` item (d).

    A LIST AND NOT A MAPPING: the questions are printed and numbered on the
    page, so the answers are positional and a grader never has to spell a
    key. Numbers are accepted and stringified -- most of these ask for one.
    """
    raw = form.get("forecast")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise FormError("'forecast' is a LIST of answers, one per question "
                        "the page numbered, in that order")
    return [str(a).strip() for a in raw]


def apply_falsifiers(turn_id: str, form: dict[str, Any], *,
                     packet_sha: str | None,
                     closeness: dict[str, Any] | None,
                     targets: dict[str, Any] | None = None,
                     forecast_asks: int = 0) -> list[str]:
    """Every rule that refuses this form, in the order they are checked.

    `targets` is EB-203's reading, computed by `grade` off the card sheet and
    the packet's hand. It defaults to `None` -- absent, not clean -- so a
    caller with no board (the ledger rebuilders, the tests that hand a bare
    form) grades exactly as it did before this rule existed.
    """
    refused: list[str] = []
    if targets and targets.get("refused"):
        refused.append("target_missing")
    given = str(form.get("packet_sha256") or "")
    if packet_sha and given and given != packet_sha:
        refused.append("packet_mismatch")
    if bool((form.get("grader") or {}).get("designed_these_cards")):
        refused.append("grader_is_designer")
    if any(not _norm(form.get(q)) for q in QUESTIONS):
        refused.append("incomplete_form")
    if not form.get("chosen_line"):
        refused.append("empty_line")
    if is_negative(form.get("q2_other_line_considered")):
        refused.append("no_second_line")
    # BOTH HALVES, and the boolean is not the authority on its own: a form
    # that ticks `q4_changed: true` and then writes "no" has answered no.
    if (form.get("q4_changed") is False
            or is_negative(form.get("q4_different_intent"))):
        refused.append("intent_insensitive")
    if closeness and closeness.get("verdict") == "REFUSED":
        refused.append("line_dominates")
    # DEFAULTS TO ZERO -- absent, not clean -- so every caller with no packet
    # (the ledger rebuilders, the tests that hand a bare form) grades exactly
    # as it did before this rule existed.
    if forecast_asks:
        answers = [a for a in forecast_answers(form) if a]
        if len(answers) < forecast_asks:
            refused.append("forecast_missing")
    return refused


def grade(turn_id: str, form: dict[str, Any], *,
          root: Path | None = None) -> dict[str, Any]:
    d = (root or _st().QA_DIR) / turn_id
    packet_md = d / "packet.md"
    packet_sha = (qa_packet.sha256(packet_md.read_text(encoding="utf-8"))
                  if packet_md.is_file() else None)
    closeness_path = d / "closeness.json"
    closeness = (json.loads(closeness_path.read_text(encoding="utf-8"))
                 if closeness_path.is_file() else None)

    # EB-203, and it reads a SHEET, so it is imported here rather than at
    # module scope -- the same rule `local_tester._post_read` keeps and for
    # the same reason: nothing that builds a blind packet may be one refactor
    # away from a design sheet.
    from understudy import targeting
    targets = targeting.summary(form.get("chosen_line") or [],
                                hand=targeting.packet_titles(d))

    # `EB-236` item (d). HOW MANY QUESTIONS THE BOARD ASKED IS READ OFF THE
    # PACKET, not off the turn file: the packet is what the grader was
    # handed, and a turn file edited after a packet was written would be
    # grading a form against questions nobody was shown.
    packet_json = d / "packet.json"
    asks = 0
    if packet_json.is_file():
        blob = json.loads(packet_json.read_text(encoding="utf-8"))
        asks = len(blob.get("forecast") or [])

    refused = apply_falsifiers(turn_id, form, packet_sha=packet_sha,
                               closeness=closeness, targets=targets,
                               forecast_asks=asks)
    gid = grader_id(form)
    down, why_down = is_down_weighted(gid, root=root)
    verdict = {
        "turn_id": turn_id,
        "verdict": "REFUSED" if refused else "SURVIVES",
        "refused_by": refused,
        "reasons": [f"{rule}: {FALSIFIERS[rule]}" for rule in refused],
        "grader": dict(form.get("grader") or {}),
        "packet_sha256": packet_sha,
        "chosen_line": list(form.get("chosen_line") or []),
        "answers": {q: str(form.get(q) or "") for q in QUESTIONS},
        # `EB-236` item (d): A FIELD TO COUNT. `EB-229`'s finding was that a
        # forecast slot had nothing to grade because nothing recorded one;
        # this is the record, positional against the questions the packet
        # printed, and it is carried on every verdict including a refused
        # one.
        "forecast_asked": asks,
        "forecast": forecast_answers(form),
        # SURVIVES means NOT YET FALSIFIED and nothing else. It is written out
        # in the record because a one-word verdict read six months later is
        # exactly the kind of thing that gets promoted into "the tool liked
        # it".
        "survives_means": ("not yet falsified -- this funnel refuses turns "
                           "and never rates them"),
        "survives_alone": not refused and not down,
        "why_not_alone": why_down if (down and not refused) else "",
        "closeness": closeness,
        # EB-203. Carried on every verdict, refused or not: the list of the
        # hand's aimed cards is what makes the refusal actionable, and on a
        # clean form it is the record that the check ran.
        "targets": targets,
        "closeness_quotability": (
            "the decision-closeness gap is a falsifier reading of the TURN "
            "and is quotable under R215 B's exception; it is never evidence "
            "that a decision is fun"),
        "guardrail": qa_packet.PACKET_GUARDRAIL,
        "graded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    return verdict
