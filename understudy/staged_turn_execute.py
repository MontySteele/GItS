"""Replay the grader's own line on the real board, prompts included.

Cut out of `staged_turn.py` by `EB-180`: `execute_steps`, the answer
parser, the board diff and `ExecuteRunner` -- `scenario.Runner` with
one extra verb. Re-exported from `staged_turn.py`, so
`staged_turn.ExecuteRunner(...)` still resolves.
"""
from __future__ import annotations

from typing import Any

from understudy import adapter, qa_packet, scenario
from understudy.staged_turn_model import FormError, StagedTurn
from understudy.staged_turn_shape import (FALSIFIERS, MAX_MODALS_PER_PLAY,
                                          MODAL_KEY_FOR_SCREEN, MODAL_KEYS)


# --------------------------------------------------------------- execute ---

def execute_steps(turn: StagedTurn, form: dict[str, Any]
                  ) -> list[tuple[str, Any]]:
    """The staging steps, a mark, then the grader's line as `play` steps.

    THE TRANSLATION FROM TITLE TO ID HAPPENS HERE AND NOWHERE THE GRADER CAN
    SEE. `scenario.find_card` matches a printed title against the hand the
    wire just returned and hands the POST a card INDEX -- so the agent's
    answer stays a list of faces and the bridge still gets the identity it
    needs. Same for a target: `find_enemy` takes the enemy's display name.
    """
    # THE SAME OPENING `stage` USES, and for the same reason: a turn that asked
    # for an exact hand and is replayed without the clear is replayed onto the
    # dealt hand, which is a different board. The guard below would catch it --
    # and did, the first time this ran on an exact-hand turn -- but catching it
    # is not the same as replaying the turn.
    steps = ([("clear_hand", {})] if turn.exact_hand else []) + list(turn.staging)
    # BEFORE THE MARK AND BEFORE EVERY PLAY. A line replayed onto a board the
    # packet never showed is not a replay of anything.
    steps.append(("board_check", {}))
    steps.append(("mark", {}))
    for play in form.get("chosen_line") or []:
        body: dict[str, Any] = {"card": str(play["card"])}
        if play.get("target"):
            body["target"] = str(play["target"])
        # EB-184: THE MODE TRAVELS WITH THE PLAY, not only with the screen that
        # follows it. The form's `choose` is answered a step later, on the
        # choose-a-card screen -- but the bridge has to decide whether the play
        # needs aiming BEFORE that screen exists, because the game aims a card
        # before its mode is chosen. Told the mode here, it asks the mode; told
        # nothing, it asks the card TYPE and refuses a targetless Block half of
        # an Attack-typed modal, which is exactly how slice 1 round 4 `t02`
        # ended UNTESTED. The value is the same string the `answer_modal` step
        # below carries, off the same form key: one reading, two readers.
        if play.get("choose"):
            body["mode"] = str(play["choose"])
        steps.append(("play", body))
        # EB-170. ONE AFTER EVERY PLAY, unconditionally, and not only after
        # the plays whose form entry carries a key. A modal is a property of
        # the card and the board, not of what the grader remembered to write
        # down: the step is a no-op when no screen is up, and the whole point
        # of the row is that a prompt nobody declared is REPORTED rather than
        # walked into by the next play. Round 3 walked into three of them and
        # read `no enemy 'Twig Slime (S)'; the fight has []` -- a true
        # sentence about a card-selection screen, and a useless one.
        answers = {k: str(play[k]) for k in MODAL_KEYS
                   if play.get(k) is not None}
        steps.append(("answer_modal", {"card": str(play["card"]), **answers}))
    steps.append(("read", {"label": "after the graded line"}))
    if turn.replay_next_turn:
        # `EB-236` item (e). END THE TURN AND READ AGAIN. A price whose refund
        # arrives at the START of the next turn -- Bombs sitting on a body
        # until the turn-start sweep pops them and `Pounding Surprise` pays
        # one Spark each -- cannot be read on a board that stops when the
        # line does. The enemy takes its telegraphed turn in between, which
        # is why this is opt-in and why the board that asks for it declares
        # the incoming damage in its own assumptions.
        steps.append(("end_turn", {}))
        steps.append(("read", {"label": "the start of the next turn"}))
    return steps


def parse_answers(raw: list[str] | None) -> list[tuple[str, str]]:
    """`--answer "<prompt>=<printed choice>"`, as ordered (match, choice).

    THE OPERATOR'S ANSWER, AND IT IS LABELLED AS ONE. It exists for exactly
    one situation: a form written BEFORE the `exhaust` / `choose` keys existed,
    whose q1 prose names the choice unambiguously, being replayed so the record
    stops saying "untested". The operator reads the prose, states the answer on
    the command line, and every row it fills is logged with
    `source: "operator"` and the prose it came from is the reader's to check.
    It is never a default, never a heuristic, and it never overrides the form:
    a form that says `exhaust` is the grader's own answer and wins.

    The left-hand side matches the live PROMPT TEXT (case-insensitive
    substring) or the screen's own wire name, because a screen can arrive with
    no prompt at all and an operator still has to be able to name it.
    """
    out: list[tuple[str, str]] = []
    for entry in raw or []:
        if "=" not in str(entry):
            raise FormError(
                f"--answer takes '<prompt>=<printed choice>'; got {entry!r}. "
                f"The left side matches the prompt the game shows (or the "
                f"screen name, hand_select / card_select) and the right side "
                f"is the PRINTED text of the choice")
        match, choice = str(entry).split("=", 1)
        if not match.strip() or not choice.strip():
            raise FormError(f"--answer {entry!r}: both halves are required")
        out.append((match.strip(), choice.strip()))
    return out


def board_differences(packet: dict[str, Any],
                      state: dict[str, Any]) -> list[str]:
    """How the LIVE board differs from the one the packet showed.

    Compared in the grader's own vocabulary and in no other: the enemies'
    PRINTED names and the hand's PRINTED titles as a MULTISET. Not ids, not
    HP, not intents. The question this answers is "is this the same turn the
    form was answered about", and the two things that make it a different turn
    are a different encounter and a different hand -- both of which the first
    live `execute` produced at once, because it rolled its own seed.

    A multiset and not a set: three Coral Guards and one Coral Guard are
    different hands, and a set comparison would call them equal.
    """
    from understudy import adapter

    want_enemies = sorted(qa_packet._text(e.get("name"))
                          for e in (packet.get("board") or {}).get("enemies") or [])
    got_enemies = sorted(qa_packet._text(e.get("name"))
                         for e in adapter.enemy_blobs(state))
    want_hand = sorted(qa_packet._text(c.get("title"))
                       for c in (packet.get("board") or {}).get("hand") or [])
    got_hand = sorted(qa_packet._text(c.get("name"))
                      for c in scenario._hand(state))
    out: list[str] = []
    if want_enemies != got_enemies:
        out.append(f"enemies: packet showed {want_enemies}, the fight has "
                   f"{got_enemies}")
    if want_hand != got_hand:
        out.append(f"hand: packet showed {want_hand}, the board has "
                   f"{got_hand}")
    return out


class ExecuteRunner(scenario.Runner):
    """`scenario.Runner` with one extra verb: `board_check`.

    THE GUARD RUNS BEFORE THE FIRST PLAY AND REFUSES BY NAME. `_do_play`'s own
    "no enemy 'Shrinker Beetle'" is a fine second line of defence and it is
    kept, but it fires per play and reads as one bad target rather than as the
    whole board being somebody else's -- which is what it actually was the
    first time this ran live. A guard that names `board_mismatch` and lists
    both differences is a failure a person can act on.

    A subclass rather than a verb added to `scenario.py`: `Runner._step`
    dispatches on `_do_<verb>`, so the verb exists exactly where its meaning
    does, and the scenario pack's parser still refuses it as unknown.
    """

    def __init__(self, *args: Any, packet: dict[str, Any] | None = None,
                 answers: list[tuple[str, str]] | None = None,
                 **kw: Any):
        super().__init__(*args, **kw)
        self.packet = packet or {}
        # EB-170. The operator's answers, in order, each consumed at most once
        # so a single `--answer` cannot silently drive two different prompts.
        self.answers = list(answers or [])
        self.answers_used: list[dict[str, Any]] = []
        self.modals: list[dict[str, Any]] = []

    def _do_board_check(self, body: dict[str, Any]) -> None:
        self.read()
        diffs = board_differences(self.packet, self.state)
        self.emit({"step": "board_check", "rule": "board_mismatch",
                   "ok": not diffs, "differences": diffs,
                   "packet_sha256": self.packet.get("packet_sha256"),
                   "run_seed": self.packet.get("run_seed")})
        if diffs:
            raise scenario.ExpectFailed(
                "board_mismatch", FALSIFIERS["board_mismatch"] + " -- "
                + "; ".join(diffs), self.state, self.state)

    # ---------------------------------------------------- EB-170: modals ---

    def _operator_answer(self, screen: str, prompt: str
                         ) -> tuple[str, int] | None:
        """The first UNUSED `--answer` whose left side matches this prompt.

        Matched against the prompt text first and the screen's wire name
        second, so `--answer "Choose a card.=Deal 14 damage"` and
        `--answer "card_select=Deal 14 damage"` both work and an operator
        facing a screen that arrives with no prompt still has a handle.
        """
        used = {u["index"] for u in self.answers_used}
        want = (prompt or "").casefold()
        for i, (match, choice) in enumerate(self.answers):
            if i in used:
                continue
            m = match.casefold()
            if (want and m in want) or m == screen.casefold():
                return choice, i
        return None

    def _do_answer_modal(self, body: dict[str, Any]) -> None:
        """Close whatever prompt the play just raised, from the form's own
        words -- or STOP, naming the prompt.

        THE THREE OUTCOMES, and each is a row:
          * no screen is up -- `answered: false`, and the step is a no-op. This
            is the common case and it costs one GET.
          * a screen is up and somebody said what to pick -- the pick is posted
            through `scenario`'s own `select` / `confirm`, so the two screens'
            two different verb pairs are resolved in exactly one place.
          * a screen is up and nobody said -- `modal_unanswered`, naming the
            PROMPT and listing the offered text. Never a heuristic pick: the
            first offer, the biggest number and the cheapest card are all
            plausible guesses and all three would produce a post-state
            indistinguishable from a real replay.
        """
        # EACH KEY ANSWERS AT MOST ONE PROMPT PER PLAY. Without this, a screen
        # that failed to close would be answered with the same word forever --
        # the replayer would look like it was working while playing the same
        # pick over and over.
        used_keys: set[str] = set()
        for _ in range(MAX_MODALS_PER_PLAY):
            self.read()
            screen, blob = scenario._select_blob(self.state)
            if not screen:
                self.emit({"step": "answer_modal", "card": body.get("card"),
                           "answered": False, "screen": "",
                           "why": "no selection screen is up"})
                return
            prompt = str(blob.get("prompt") or "")
            offered = [c for c in (blob.get("cards") or [])
                       if isinstance(c, dict)] or scenario._hand(self.state)
            titles = [str(c.get("name") or c.get("id") or "") for c in offered]
            key = MODAL_KEY_FOR_SCREEN.get(screen, "")
            choice = (str(body.get(key) or "")
                      if key and key not in used_keys else "")
            source = "form"
            operator = None
            if not choice:
                operator = self._operator_answer(screen, prompt)
                if operator is not None:
                    choice, source = operator[0], "operator"
            if not choice:
                detail = (f"{FALSIFIERS['modal_unanswered']} -- screen "
                          f"{screen!r}, prompt {prompt!r}, offering {titles}. "
                          f"State it on the play as "
                          f"{key or 'exhaust/choose'!r}, in the printed "
                          f"vocabulary, or pass "
                          f"--answer \"{prompt or screen}=<printed choice>\"")
                self.emit({"step": "answer_modal", "card": body.get("card"),
                           "answered": False, "screen": screen,
                           "prompt": prompt, "offered": titles,
                           "rule": "modal_unanswered"})
                self.modals.append({"card": body.get("card"), "screen": screen,
                                    "prompt": prompt, "offered": titles,
                                    "answered": False, "source": "",
                                    "choice": ""})
                raise scenario.ExpectFailed("modal_unanswered", detail,
                                            self.state, self.state)
            if scenario.find_card(offered, choice) is None:
                raise scenario.ExpectFailed(
                    "modal_unanswered",
                    f"{choice!r} is not on the screen. Prompt {prompt!r} "
                    f"offers {titles}; an answer that is not on the table is "
                    f"not an answer", self.state, self.state)
            self.emit({"step": "answer_modal", "card": body.get("card"),
                       "answered": True, "screen": screen, "prompt": prompt,
                       "offered": titles, "choice": choice, "source": source})
            self.modals.append({"card": body.get("card"), "screen": screen,
                                "prompt": prompt, "offered": titles,
                                "answered": True, "source": source,
                                "choice": choice})
            if operator is not None:
                self.answers_used.append(
                    {"index": operator[1], "prompt": prompt,
                     "screen": screen, "choice": choice})
            used_keys.add(key)
            self._do_select({"cards": [choice]})
            self._do_confirm({})
        raise scenario.ExpectFailed(
            "modal_unanswered",
            f"one play raised more than {MAX_MODALS_PER_PLAY} prompts; the "
            f"replayer is not closing them and stops rather than spinning",
            self.state, self.state)


def _outcome(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """HP/Block/resource deltas across the graded line. DIAGNOSTIC ONLY."""
    def creature(d, key):
        return {"hp": (d.get(key) or {}).get("hp"),
                "block": (d.get(key) or {}).get("block")}

    enemies_before = {e["id"]: e for e in before.get("enemies") or []}
    enemies_after = {e["id"]: e for e in after.get("enemies") or []}
    return {
        "player": {"before": creature(before, "player"),
                   "after": creature(after, "player"),
                   "resources_before": (before.get("player") or {}).get("resources"),
                   "resources_after": (after.get("player") or {}).get("resources")},
        "enemies": [{"id": eid,
                     "name": enemies_before[eid].get("name"),
                     "hp_before": enemies_before[eid].get("hp"),
                     "hp_after": (enemies_after.get(eid) or {}).get("hp"),
                     "block_before": enemies_before[eid].get("block"),
                     "block_after": (enemies_after.get(eid) or {}).get("block")}
                    for eid in enemies_before],
        # GUARDRAIL-7, on the row and not in a header. These numbers exist to
        # catch a DEFECT -- a card that did not do what its face says when a
        # person's line played it. They are not a comparison, not a balance
        # reading, and not evidence about the turn.
        "reading": ("diagnostic only: a hand-set board, played once. A number "
                    "here is evidence of a DEFECT or of nothing at all"),
        "guardrail": qa_packet.PACKET_GUARDRAIL,
    }

