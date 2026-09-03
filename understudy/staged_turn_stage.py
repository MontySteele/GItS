"""Boot, embark, reach the first fight, set the board, write the packet.

Cut out of `staged_turn.py` by `EB-180`: `stage_board`, the three
preflights it runs and `export_packet`. Re-exported from
`staged_turn.py`, so `staged_turn.stage_board(turn, why, ...)` still
resolves.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from understudy import face_defects, qa_packet, scenario
from understudy.staged_turn_model import StagedTurn, TurnError
from understudy.staged_turn_parse import turn_dir, wire_assumption_preflight
from understudy.staged_turn_shape import DOMINANCE_GAP, REPO


# --------------------------------------------------------------- staging ---

class _StagingComplete(RuntimeError):
    """The board is set. Raised to stop the driver where the turn begins.

    `RunDriver.run` files any escaping exception as a `harness_exception`
    defect and returns its summary, which is exactly the behaviour wanted
    here: the run STOPS at the staged board instead of handing it to
    `policy_v1`, which would play the turn the grader is supposed to play.
    The summary's outcome is checked for this class's name rather than for
    success, and `cmd_stage` says so in its output.
    """


class StagingPolicy:
    """`policy_v1` everywhere but the first combat screen, where it stops.

    `scenario.ScenarioPolicy` hands combat BACK to `policy_v1` so the fight
    can end. This one must not: the whole point is a board frozen at the
    moment the turn begins, either for a packet export or for a person to sit
    down in front of.
    """

    def __init__(self, runner: scenario.Runner):
        from understudy import policy_v1
        self._policy = policy_v1
        self.POLICY_VERSION = "staged_turn/" + policy_v1.POLICY_VERSION
        self.BLOCK_MATTERS_FRACTION = policy_v1.BLOCK_MATTERS_FRACTION
        self.COMPANION_SHARE_FOR_GUEST_CAST = \
            policy_v1.COMPANION_SHARE_FOR_GUEST_CAST
        self.Memo = policy_v1.Memo
        self.runner = runner
        self.staged_state: dict[str, Any] | None = None
        self.ok: bool | None = None

    def decide(self, state: dict[str, Any], memo: Any,
               commit: str | None = None):
        st = str(state.get("state_type") or "")
        if self.staged_state is None and st in scenario.COMBAT_SCREENS:
            self.ok = self.runner.run()
            self.staged_state = self.runner.state or state
            raise _StagingComplete(
                "the board is staged; the driver stops here so the turn is "
                "not played by a bot")
        return self._policy.decide(state, memo, commit=commit)


def stage_board(turn: StagedTurn, why: str, *, hold: bool,
                out_path: Path, seed: str | None = None
                ) -> tuple[dict[str, Any], dict[str, Any]]:
    """Boot, embark, reach the first fight, set the board. Returns
    `(live wire state, the run summary)`.

    `seed` PINS THE RUN, and the run summary reports back the seed the game
    actually used either way -- `None` is R95's read-back arm (the game rolls,
    we record) and a string is P1.5's chosen arm, which `RunDriver` verifies
    and files as a `seed_not_honoured` defect if the game ignored it. The
    ENCOUNTER IS GENERATED FROM THAT SEED, which is why the recorded value is
    the difference between a packet that can be replayed and one that cannot:
    the first live `execute` of this tool rolled its own seed, drew a Sludge
    Spinner where the packet showed a Shrinker Beetle, and refused at the
    first targeted play.
    """
    from understudy import soak

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        runner = scenario.Runner(turn.as_scenario(), why, out=fh)
        runner.emit({"step": "staged_turn_begin", "turn": turn.id,
                     "character": turn.character, "hold": hold,
                     "file": str(turn.path),
                     "assumptions": turn.assumptions})
        policy = StagingPolicy(runner)
        # `--hold` attaches to a game somebody else launched, and that is not
        # a convenience: `run_scripted`'s `finally` tears the session down,
        # and a teardown that owns the launch KILLS THE GAME -- which is the
        # one thing a hold must not do. With `do_setup=False` the session
        # makes no game-dir changes and owns no process, so the reversibility
        # ledger is empty and the staged board is still on the screen when
        # this returns.
        summary = soak.run_scripted(policy, stamp, character=turn.character,
                                    max_fights=1,
                                    chosen_seed=seed or turn.seed,
                                    do_setup=not hold)
        runner.emit({"step": "staged_turn_end", "staged": policy.staged_state
                     is not None, "steps_ok": policy.ok,
                     "seed_requested": seed or turn.seed,
                     "seed_used": summary.get("seed"), "run": summary})
    if policy.staged_state is None:
        raise TurnError(
            f"no combat screen was ever reached, so nothing was staged "
            f"(run outcome: {summary.get('outcome')} "
            f"{summary.get('detail')})")
    if not policy.ok:
        raise TurnError(
            f"a staging step failed; the board is not the one the file "
            f"describes. See {out_path}")
    # `EB-240`. LAST, ON THE STAGED STATE, AND IT REFUSES THE STAGE. Every
    # step above can report success and still leave a board the file's own
    # printed assertions are false about -- `KLEESPARK-BT2`'s three boards
    # each ran `set_hp: {who: first, amount: 55}` to a clean report and were
    # then read at 45, 46 and 40. The comparison is against the WIRE and not
    # against the packet, because the packet is the document the falsehood
    # would go out on.
    wire_assumption_preflight(turn, policy.staged_state)
    return policy.staged_state, summary


def declared_hand_keys(turn: StagedTurn) -> list[str]:
    """The declared hand as sorted `scenario.card_key`s, one per copy.

    Read off the GIVE steps rather than off `board.hand`, because the give
    steps are what the game was actually told; `_check_halves_agree` has
    already pinned the two equal, so the choice is about which record is the
    instruction and not about which is right.
    """
    return sorted(scenario.card_key(str(b.get("card")))
                  for v, b in turn.staging
                  if v == "give" and str(b.get("pile") or "hand") == "hand"
                  for _ in range(int(b.get("count", 1))))


def staged_card_names(turn: StagedTurn) -> list[str]:
    """Every card the turn names, in both halves: the granted ids and the
    mirrored hand. Both, deliberately -- `_check_halves_agree` has pinned them
    equal for the HAND, but a `give` into `draw` or `discard` is in neither
    hand and can still be drawn into the grader's turn."""
    names = [str(b.get("card")) for v, b in turn.staging
             if v == "give" and b.get("card")]
    return names + list(turn.board.hand)


def face_defect_preflight(turn: StagedTurn,
                          register: dict[str, Any] | None = None) -> None:
    """EB-169. Refuse a turn that stages a card with an OPEN face defect.

    RAISES BEFORE THE GAME IS LAUNCHED, which is the whole point. Round 2 of
    the Kokomi slice staged `all_streams_flow` on eleven boards while `EB-164`
    sat open against that face, graded them, replayed them and pair-read them,
    and only then learned that the arithmetic every refusal rested on was the
    repo's own defect. The cost of learning it late is eleven launches and
    seven manufactured refusals; the cost of learning it here is a parse.

    Called by `check` and by `stage`, and NOT by `execute`: a replay is how a
    misread already in the record gets settled against the board, so refusing
    it would take away the one tool that answers the question. `grade` has its
    own copy of this check on the packet's printed hand (see `seat.py`), which
    is the belt to this one's braces.
    """
    found = face_defects.hits(staged_card_names(turn), register)
    if found:
        raise TurnError(face_defects.refusal(found))


# EB-187. AN ASSUMPTION MAY NOT CLAIM A GAIN THE FACE ALREADY PRINTS.
#
# Klee slice 1 `t06` is the case that filed it. The board's assumptions told
# the grader that "a Skill-tagged card adds 5 to [the Burst meter] on play,
# over and above anything the card's own text grants" -- while the face the
# grader was reading printed `Gain 10 Burst Energy. Burst +5`, where the
# `Burst +5` IS that tag, written onto the face by the description builder for
# every row carrying it (`tools/lint_burst_legibility.py` is the join that
# keeps the two in step). A grader who believes both counts the tag twice, and
# one did: it predicted 20 -> 40 where the board produced 20 -> 35, and the
# pair read named the arithmetic in RETURNing the arm.
#
# THE CHECK IS STRUCTURAL RATHER THAN TEXTUAL, because the face text is not
# available with no game running. The tag is: a staged row either carries
# `skill_tag` or it does not, and the lint above pins that a row carrying it
# prints the rider. So a claim of the shape "adds <N> ... over and above the
# card's own text" is refused when a staged card carries a tag whose rider is
# printed and worth exactly <N>.
#
# NARROW ON PURPOSE. It refuses a sentence that says the gain is ADDITIONAL to
# what the face says; a sentence that says the rider IS what the face prints,
# which is what those two files now say, is exactly what it wants and passes.
PRINTED_RIDERS: dict[str, tuple[str, str]] = {
    # tag -> (the tier0 constant that sizes it, what the face prints)
    "skill_tag": ("BURST_PER_SKILL_TAG", "Burst +{n}"),
}

_RIDER_CLAIM_RE = re.compile(
    r"\b(?:adds?|grants?|gives?)\s+(\d+)\b[^.]*?"
    r"\b(?:over and above|on top of|in addition to|as well as|besides)\b",
    re.I | re.S)


def _staged_tags(turn: StagedTurn) -> dict[str, list[str]]:
    """`{tag: [card ids carrying it]}` over everything the turn stages."""
    from tier0.content import loader

    index: dict[str, list[str]] = {}
    proto = ({c.id: c for c in loader.prototype_cards()}
             if turn.prototype else {})
    for raw in staged_card_names(turn):
        # `card_key` folds the three spellings onto a SPACED key, which is
        # what the face-defect register is written in; a sheet id is the same
        # key with underscores, so the fold is reused and re-spelled rather
        # than re-implemented.
        key = scenario.card_key(str(raw)).replace(" ", "_")
        card = proto.get(key)
        if card is None:
            try:
                card = loader.peek_card(key)
            except (KeyError, ValueError):
                continue
        for tag in card.tags or ():
            index.setdefault(str(tag), []).append(key)
    return index


def assumption_rider_conflicts(turn: StagedTurn) -> list[str]:
    """Every assumptions line claiming a gain the staged faces already print."""
    from tier0 import constants as C

    tags = _staged_tags(turn)
    found: list[str] = []
    for line in turn.assumptions:
        for m in _RIDER_CLAIM_RE.finditer(" ".join(str(line).split())):
            claimed = int(m.group(1))
            for tag, (const_name, printed) in PRINTED_RIDERS.items():
                amount = int(getattr(C, const_name))
                if claimed != amount or tag not in tags:
                    continue
                found.append(
                    f"an assumption says {m.group(0)!r}, but "
                    f"{', '.join(sorted(set(tags[tag])))} carr"
                    f"{'y' if len(set(tags[tag])) > 1 else 'ies'} `{tag}` and "
                    f"the face already prints "
                    f"'{printed.format(n=amount)}' -- a grader who believes "
                    f"both counts it twice")
    return found


def assumption_preflight(turn: StagedTurn) -> None:
    """EB-187. Refuse a turn whose assumptions double-count a printed rider."""
    found = assumption_rider_conflicts(turn)
    if found:
        raise TurnError(
            "the assumptions block claims a gain the card's own face already "
            "prints; say the printed rider IS the tag, or drop the sentence: "
            + "; ".join(found))


def exact_hand_difference(turn: StagedTurn, state: dict[str, Any]) -> str:
    """`""` when the live hand IS the declared hand, else what differs.

    EB-165's acceptance, checked at the one place it can be checked: after the
    clear and after the grants, against the board the packet is about to be
    written from. A multiset, in `card_key`'s folded vocabulary, so the wire's
    `KLEEMOD-CORAL_GUARD` and the file's `coral_guard` compare equal and two
    Coral Guards do not compare equal to one.
    """
    want = declared_hand_keys(turn)
    got = sorted(scenario.card_key(str(c.get("id") or c.get("name") or ""))
                 for c in scenario._hand(state))
    if want == got:
        return ""
    from collections import Counter
    extra = sorted((Counter(got) - Counter(want)).elements())
    missing = sorted((Counter(want) - Counter(got)).elements())
    parts = []
    if extra:
        parts.append(f"the board holds {extra} that the file did not declare")
    if missing:
        parts.append(f"the file declared {missing} that the board does not "
                     f"hold")
    return "; ".join(parts)


def export_packet(turn: StagedTurn, state: dict[str, Any], *,
                  run_seed: str | None = None) -> dict[str, Any]:
    """Write `packet.md`, `packet.json` and `observed.json`. Returns a report.

    THREE FILES, AND THE THIRD IS NOT PART OF THE PACKET. `packet.md` and
    `packet.json` are what a grader is handed and they are scrubbed;
    `observed.json` is the tool's own record of the live board -- the RAW wire
    state, entity ids and wire card ids included -- and it is never given to a
    grader.

    THE RAW STATE IS KEPT BECAUSE THE LIVE BOARD IS NOT THE DECLARED ONE, and
    the first live run of this tool is what proved it: the game deals its own
    opening hand, so a turn that grants five cards is staged with TEN in hand,
    and the encounter is generated, so the enemy and its telegraph are
    whatever rolled. `closeness --observed` reads this file and scores the
    board the grader actually saw. The declared `board:` half stays useful --
    it is the reading available with no game -- but where the two disagree the
    observed one is the turn.
    """
    if turn.exact_hand:
        # EB-165'S ACCEPTANCE, AND IT REFUSES RATHER THAN WARNS. A turn that
        # asked for an exact hand and got something else is a turn whose blind
        # packet would show a board the file did not describe -- the exact
        # failure the door exists to end -- and writing it anyway would put
        # that board in front of a grader who has no way to know.
        diff = exact_hand_difference(turn, state)
        if diff:
            raise TurnError(
                f"exact_hand: the live hand is not the declared hand -- "
                f"{diff}. The clear or a grant did not land; the packet is "
                f"NOT written")
    d = turn_dir(turn.id)
    d.mkdir(parents=True, exist_ok=True)
    # THE DISCLOSURES ARE SCRUBBED LIKE EVERYTHING ELSE, which is why none of
    # them names a ruling: the packet's own leak rules refuse an `R213` as
    # readily in a disclosure as in a card face, and they are right to -- a
    # grader who can see a ruling number can look up what the ruling wanted.
    # The constant is disclosed because a falsifier the grader cannot see the
    # threshold of is a filter, not a disclosure; the citation for it lives in
    # the verdict and in this module's docstring, where no grader reads.
    disclosures = [
        f"A decision-closeness falsifier reads this turn with a dominance "
        f"threshold of {DOMINANCE_GAP}.",
        "You are not being asked whether this turn is fun.",
    ] + list(turn.assumptions)
    packet = qa_packet.build(state, turn.id, repo=REPO,
                             disclosures=disclosures,
                             forecast=list(turn.forecast))
    md = qa_packet.render(packet)
    digest = qa_packet.sha256(md)
    # THE ENVELOPE, ADDED AFTER THE SCRUB AND NEVER RENDERED INTO packet.md.
    # `packet.md` is the page a grader reads and these two keys are not on
    # it: the hash is what a form is answered AGAINST, and the seed is what
    # `execute` embarks with so the encounter regenerates identically. Both
    # are facts about the RUN rather than about the board, so a grader that
    # was handed the json instead of the page learns nothing about the game
    # from either -- but neither belongs on the page.
    packet["packet_sha256"] = digest
    packet["run_seed"] = run_seed
    (d / "packet.md").write_text(md, encoding="utf-8")
    (d / "packet.json").write_text(qa_packet.dumps(packet), encoding="utf-8")
    (d / "observed.json").write_text(
        json.dumps({"turn_id": turn.id,
                    "guardrail": qa_packet.PACKET_GUARDRAIL,
                    "pilot": turn.board.pilot,
                    "run_seed": run_seed,
                    "not_a_packet": ("the RAW wire state, ids included. Tool "
                                     "side only -- never hand this to a "
                                     "grader"),
                    "digest": scenario.digest(state),
                    "state": state}, indent=1, default=str) + "\n",
        encoding="utf-8")
    live = [c["title"] for c in packet["board"]["hand"]]
    return {"dir": d, "packet_md": d / "packet.md",
            "packet_json": d / "packet.json",
            "observed_json": d / "observed.json", "sha256": digest,
            "run_seed": run_seed, "exact_hand": turn.exact_hand,
            "cards": len(live), "hand": live,
            "declared_cards": len(turn.board.hand),
            "enemies": len(packet["board"]["enemies"])}
