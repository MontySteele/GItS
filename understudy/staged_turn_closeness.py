"""The one quotable number: the gap between the best two lines.

Cut out of `staged_turn.py` by `EB-180`: the staged board as a tier0
`CombatState`, the bounded walk over the lines it can play, and the
R213 F falsifier over the two best. Re-exported from
`staged_turn.py`, so `staged_turn.closeness(board)` still resolves.

R215 B put the exception in LAW in as many words: no number measured
on a prototype row is quotable, EXCEPT this falsifier, because it
reads the TURN and not the row.
"""
from __future__ import annotations

import copy
from typing import Any

from understudy import adapter, qa_packet

from understudy.staged_turn_model import Board, TurnError
from understudy.staged_turn_shape import DOMINANCE_GAP, FALSIFIERS, MAX_LINES


# ------------------------------------------------------------- closeness ---

def build_combat_state(board: Board, *, prototype: bool = False):
    """The staged board as a tier0 `CombatState`.

    Returns `(state, unrepresentable)`. `unrepresentable` is the list of hand
    cards the sim has no row for; the caller REFUSES the falsifier for that
    turn rather than guessing, because a line scored with a card missing from
    it is a line nobody could play.

    `prototype` is the turn's own DEV-ROUTE DECLARATION (R213 B). Prototype
    ids are absent from `loader._card_index()` BY CONSTRUCTION -- that
    absence is the quarantine, and it is structural rather than a filter --
    so with the flag set they are resolved through the surface's own reader,
    `loader.prototype_cards()`, and only then. The flag is required rather
    than inferred from the prefix: an explicit declaration is what makes a
    prototype turn distinguishable from a turn that has a typo in it, and
    "the id started with proto_" is not a decision anybody made.
    """
    import random

    from tier0.content import loader
    from tier0.engine.state import CombatState, Enemy, Player

    proto_index: dict[str, Any] = {}
    if prototype:
        proto_index = {c.id: c for c in loader.prototype_cards()}
    else:
        # Refused BY NAME, and loudly. Without the flag a `proto_` id would
        # fall through to `unrepresentable` and the falsifier would answer
        # NOT READ -- a verdict that reads as "the sim cannot model this
        # card" when what actually happened is that the file forgot to say
        # what it was. Two very different facts must not share one output.
        stray = [n for n in board.hand
                 if str(n).startswith(loader.PROTOTYPE_ID_PREFIX)]
        if stray:
            raise TurnError(
                f"board.hand names prototype row(s) {stray} but the turn does "
                f"not declare `prototype: true`. A quarantined row is outside "
                f"the sim's card index on purpose (R213 B); the falsifier "
                f"reaches it only down the declared dev route.")

    hand = []
    unrepresentable: list[str] = []
    for name in board.hand:
        card = proto_index.get(name)
        if card is not None:
            # A COPY, because `peek_card` hands back the shared prototype and
            # every caller here is expected not to mutate it -- but
            # `prototype_cards()` builds fresh objects per call, so two hand
            # slots naming one row would otherwise be the SAME object and a
            # line that played one would consume the other.
            hand.append(copy.deepcopy(card))
            continue
        try:
            hand.append(loader.peek_card(name))
        except (KeyError, ValueError):
            unrepresentable.append(name)
    if unrepresentable:
        return None, unrepresentable

    player = Player(hp=board.hp, max_hp=board.max_hp, block=board.block,
                    energy=board.energy, hand=hand,
                    character_id=board.character)
    for key, amount in board.resources.items():
        if not hasattr(player, key):
            raise TurnError(
                f"board.resources names {key!r}, which is not a field on the "
                f"sim's Player -- a resource the sim cannot hold is a board "
                f"the falsifier cannot read")
        setattr(player, key, int(amount))

    enemies = []
    for e in board.enemies:
        intent = dict(e.get("intent") or {"kind": "block", "amount": 0})
        hp = int(e.get("hp", 1))
        enemies.append(Enemy(hp=hp, max_hp=int(e.get("max_hp", hp)),
                             block=int(e.get("block", 0)),
                             name=str(e["name"]), intents=[intent],
                             aura=e.get("aura")))
    state = CombatState(player=player, enemies=enemies,
                        # Never consumed: every scoring path below is pure,
                        # and a line that drew from the stream would make the
                        # gap depend on enumeration order.
                        rng=random.Random(0), turn=board.turn)
    return state, []


class _TooManyLines(RuntimeError):
    """The bounded walk hit its ceiling. Refuses; never truncates."""


def _enumerate_lines(state, weights, max_lines: int
                     ) -> tuple[dict[frozenset[int], float], int, int]:
    """Every line the board can actually play, scored in the pilot's currency.

    A DEPTH-FIRST WALK THAT PLAYS AS IT GOES, rather than an enumeration of
    subsets filtered afterwards, and the difference is what makes this usable
    on a live board. The game deals its own opening hand, so a staged hand is
    ten cards, not five -- and ten cards is 9.8 million orderings if you
    enumerate first and check playability second. Walking prunes at the first
    card the energy cannot buy, which takes the same board to a few hundred
    playouts.

    Each card is scored by `pilot.policy._score` against the state AS IT IS
    WHEN THAT CARD IS PLAYED, and then actually resolved through
    `combat.play_card`, so an ordering that sets something up before spending
    it scores differently from the reverse. That is why the playout is real
    rather than a sum of static reads.

    Returns `(best score per SET of cards, playouts walked, plays refused)`.
    The collapse onto sets is the other half: "what other line did you
    seriously consider" is a question about WHICH CARDS, and a top-two made of
    two orderings of the same three cards would report a gap of nearly zero
    and refuse nothing, ever.
    """
    from tier0.engine import combat
    from tier0.pilot import policy

    n = len(state.player.hand)
    best: dict[frozenset[int], float] = {}
    walked = 0
    refused = 0

    def walk(s, slots, chosen: frozenset[int], total: float) -> None:
        nonlocal walked, refused
        for i in range(n):
            if i in chosen:
                continue
            card = slots[i]
            # `Card` is a value-equality dataclass and `play_card` removes the
            # instance from hand, so the SLOT LIST -- taken before the first
            # play and copied alongside the state -- is what keeps index `i`
            # meaning the same card for the whole line. A lookup by id or by
            # equality would find the first EQUAL card instead.
            if card not in s.player.hand or not combat.card_playable(s, card):
                continue
            if walked >= max_lines:
                raise _TooManyLines(walked)
            s2, slots2 = copy.deepcopy((s, slots))
            try:
                score = total + policy._score(s2, slots2[i], weights)
                combat.play_card(s2, slots2[i])
            except Exception:                                # noqa: BLE001
                # A line the sim cannot resolve is not a line the grader could
                # have chosen, so it leaves the walk rather than scoring zero.
                refused += 1
                continue
            walked += 1
            key = chosen | {i}
            if score > best.get(key, float("-inf")):
                best[key] = score
            walk(s2, slots2, key, score)

    walk(state, list(state.player.hand), frozenset(), 0.0)
    return best, walked, refused


# The registered resources the sim holds as named Player fields. `adapter`
# does not map them (nothing in the bot loop reads them off the wire), and a
# Charge reader scored against a bank of zero is a card scored as a different
# card -- which on this repo's one shipped meter reader is the whole
# difference between a live choice and a small attack. Explicit table rather
# than a `setattr(k.lower())` guess: an unmapped resource is REPORTED, so a
# meter the falsifier silently could not see never passes for one it read.
#
# THE THREE BURST METERS ALL LAND ON ONE FIELD, and by `max` rather than by
# assignment: the wire registers `KLEEMOD_BURST`, `KLEEMOD_FURINA_BURST` and
# `KLEEMOD_KOKOMI_BURST` separately while the sim holds one
# `Player.burst_energy`, and on any real board exactly one of them is
# non-zero. `max` makes the order the dict is walked in irrelevant, which
# assignment would not.
#
# KNOWN GAP, stated rather than hidden: `burst_max` is NOT on the wire, so a
# card gated on `requires: burst_energy_full` reads as playable on an observed
# board whatever the meter holds. Nothing in this funnel's way uses that gate
# today; the day one does, this is where it breaks.
WIRE_RESOURCES = {"KLEEMOD_CHARGE": "charge", "KLEEMOD_ENCORE": "encore",
                  "KLEEMOD_FANFARE": "fanfare",
                  "KLEEMOD_BURST": "burst_energy",
                  "KLEEMOD_FURINA_BURST": "burst_energy",
                  "KLEEMOD_KOKOMI_BURST": "burst_energy"}


def observed_state(blob: dict[str, Any], *, prototype: bool = False):
    """The LIVE board from an `observed.json`, as a tier0 `CombatState`.

    Reuses `understudy.adapter.build_combat_state`, which is the repo's
    existing wire-to-sim constructor and already carries the two decisions
    that matter here: a hand card resolves to its SHEET row where the wire id
    names one (and is flagged approximate where it does not), and enemy powers
    are dropped because the intent label the wire prints has already folded
    them in.

    Returns `(state, unrepresentable, notes)`.
    """
    from understudy import adapter

    raw = blob.get("state") or {}
    if not raw:
        raise TurnError(
            "observed.json holds no raw state -- it was written by a build of "
            "this tool that only kept the digest. Re-stage the turn")
    cs, notes = adapter.build_combat_state(raw, prototype=prototype)
    wire = (raw.get("player") or {}).get("resources") or {}
    unmapped = []
    for key, amount in wire.items():
        field_name = WIRE_RESOURCES.get(str(key))
        if field_name is None:
            unmapped.append(str(key))
            continue
        setattr(cs.player, field_name,
                max(int(amount or 0), int(getattr(cs.player, field_name, 0))))
    notes = dict(notes, unmapped_resources=sorted(unmapped))
    return cs, list(notes.get("approximate_cards") or []), notes


def closeness(board: Board, *, max_lines: int = MAX_LINES,
              prototype: bool = False) -> dict[str, Any]:
    """The R213 F falsifier on the DECLARED board. Refuses; never rates."""
    state, unrepresentable = build_combat_state(board, prototype=prototype)
    return _closeness(state, board.pilot, unrepresentable,
                      max_lines=max_lines,
                      source=("declared board (prototype route)" if prototype
                              else "declared board"))


def closeness_observed(blob: dict[str, Any], *, pilot: str = "",
                       max_lines: int = MAX_LINES,
                       prototype: bool = False) -> dict[str, Any]:
    """The same falsifier on the board the grader actually saw.

    `prototype` reaches the wire resolver for the same reason it reaches the
    declared one: without it a live prototype card degrades to the adapter's
    text approximation and the reading is refused as approximate, which is
    the wrong answer to give about a card the sim has an exact row for.
    """
    state, unrepresentable, notes = observed_state(blob, prototype=prototype)
    result = _closeness(state, pilot or str(blob.get("pilot") or "generic"),
                        unrepresentable, max_lines=max_lines,
                        source="observed board (live wire state)")
    return dict(result, observed_notes=notes)


def _closeness(state, pilot: str, unrepresentable: list[str], *,
               max_lines: int, source: str) -> dict[str, Any]:
    from tier0.content import loader

    base = {
        "source": source,
        "falsifier": "decision-closeness (R213 F)",
        "dominance_gap": DOMINANCE_GAP,
        "quotability": (
            "a falsifier reading of the TURN, quotable under R215 B's "
            "exception to the prototype clause; never a claim that a "
            "decision is fun and never comparable across turns"),
        "guardrail": qa_packet.PACKET_GUARDRAIL,
    }
    if unrepresentable:
        return dict(base, applicable=False, verdict="NOT READ",
                    reason=f"not representable in the sim: "
                           f"{', '.join(unrepresentable)}",
                    unrepresentable=unrepresentable)

    weights = loader.pilot_weights(pilot)
    try:
        best_by_set, walked, unplayable = _enumerate_lines(state, weights,
                                                           max_lines)
    except _TooManyLines:
        return dict(base, applicable=False, verdict="NOT READ",
                    reason=f"the board's line space passed the {max_lines} "
                           f"playout bound; the falsifier refuses rather "
                           f"than truncating, because a gap that depends on "
                           f"which lines were walked first is not a reading")

    ranked = sorted(((score, sorted(key)) for key, score in best_by_set.items()),
                    key=lambda t: (-t[0], t[1]))
    named = [{"cards": [state.player.hand[i].name for i in cards],
              "score": round(score, 4)} for score, cards in ranked[:5]]
    if len(ranked) < 2:
        return dict(base, applicable=False, verdict="NOT READ",
                    reason=f"only {len(ranked)} playable line(s) on this "
                           f"board; there is no second line to be close to",
                    lines=named)
    top1, top2 = ranked[0][0], ranked[1][0]
    if top1 <= 0:
        return dict(base, applicable=False, verdict="NOT READ",
                    reason="the pilot's surface values no line above zero "
                           "here, so a ratio against it says nothing",
                    lines=named)
    gap = (top1 - top2) / top1
    dominated = gap > DOMINANCE_GAP
    return dict(base, applicable=True,
                verdict="REFUSED" if dominated else "SURVIVES",
                gap=round(gap, 4), top1=round(top1, 4), top2=round(top2, 4),
                lines_considered=len(best_by_set),
                playouts=walked, plays_refused=unplayable,
                pilot=pilot, lines=named,
                reason=(FALSIFIERS["line_dominates"] if dominated else
                        "no line dominates by more than the derived gap"))
