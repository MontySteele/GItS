"""One turn of the board, off the wire, for the grader and nobody else.

Cut out of `blindplay.py` by `EB-180`. The OBJECTIVE side of a blind
run -- `wire_snapshot` and the meter-ledger rows -- which is a
different channel from the record the tester writes, and never shown
to the tester. Re-exported from `blindplay.py`.
"""
from __future__ import annotations

from typing import Any

from understudy import bridge

from understudy.blindplay_read import (_blob, _enemies, _entity_id, _hand,
                                       _int, _player, _text)


# -------------------------------------------------------- the wire snapshot -

# `EB-216` / `M56` (R224 A). THE OBJECTIVE SIDE OF A BLIND RUN.
#
# Two of the six thresholds a blind run is graded on need a fact the record
# did not carry. `P2` counts a tester's call against THAT TURN'S
# `blocked` / `fires_next` pair; `P6` asks whether an aim call was correct.
# `record.md` holds words -- the tester's own sentences -- and words cannot be
# counted against a board nobody wrote down. The grades already published
# STAND (R101b, R224 A); this is the channel the NEXT run has.
#
# THREE RULES, and each of them is why a field is shaped the way it is.
#
# 1. IT IS MACHINE-WRITTEN FROM THE WIRE, NOT FROM THE TESTER'S PAGE. The page
#    is a scrubbed, printed-faces-only render whose whole purpose is to hide
#    ids; a grader reading it back is reading a rendering of the board and not
#    the board. Every value below is lifted straight off the state the driver
#    already held when it posted, ids and all.
#
# 2. IT IS NEVER SHOWN TO THE TESTER. R101b: the tester's page is the grading
#    surface and this is the erratum reader's. It goes into the session record
#    and the gitignored log; nothing in `observation()` / `render()` consults
#    it, and no snapshot text is ever fed back as feedback.
#
# 3. IT INVENTS NO FIELD. Every key is one the API already serves --
#    `battle.round`, `player.energy`, `player.resources` (BaseLib's registered
#    meters, which is Charge / Encore / Fanfare / Burst), `player.status` (a
#    POWER-shaped meter, which is where Sparks ride), the hand's own `cost`
#    and `spark_price` / `spark_affordable`, `player.kurage_memory` (the queue
#    strip, `gits/GitsKurageMemory.cs`), and the enemies' `intents`. A build
#    without the prototype rule serves no `kurage_memory` and the key is
#    absent here too, which is the same three-state contract the bridge
#    header spells and `kurage_memory()` above honours.
#
# ALL METERS, INCLUDING THE ZEROES, unlike the observed board -- which prints
# only non-zero ones so a tester is not taught about a meter this screen does
# not show. A grader counting "the bank was empty when the call was made"
# needs the zero written down.


def _snapshot_hand(state: dict[str, Any]) -> list[dict[str, Any]]:
    """The hand as the wire has it: id, printed prices, playability."""
    out = []
    for c in _hand(state):
        row = {
            "id": _text(c.get("id")),
            "name": _text(c.get("name")),
            "kind": _text(c.get("type")),
            "energy_cost": _text(c.get("cost")),
            "upgraded": bool(c.get("is_upgraded") or c.get("upgraded")),
            "target_type": _text(c.get("target_type")),
            "can_play": c.get("can_play") is not False,
        }
        # OMITTED WHERE THE WIRE OMITS THEM, which is the bridge's own
        # contract: an absent pair means "this card charges no Sparks", and
        # writing 0 here would make a priced card and a free one look alike
        # to a grader counting affordable sinks.
        if c.get("spark_price") is not None:
            row["spark_price"] = _int(c.get("spark_price"))
            row["spark_affordable"] = bool(c.get("spark_affordable"))
        out.append(row)
    return out


def _snapshot_meters(state: dict[str, Any]) -> dict[str, Any]:
    """Every meter the character has, from the two places the API keeps them.

    `resources` is BaseLib's registered custom-resource registry (Charge,
    Encore, Fanfare, Burst and their riders). `powers` is the creature's own
    power list, which is where the Spark bank lives -- `spark` is a
    `PowerModel`, not a registered resource, and a snapshot that read only one
    of the two would silently lose whichever meter the character in front of
    it actually uses.
    """
    p = _player(state)
    resources = p.get("resources")
    powers = {}
    for row in (p.get("status") or []):
        if isinstance(row, dict) and _text(row.get("id")):
            powers[_text(row.get("id"))] = _int(row.get("amount"))
    return {
        "resources": ({_text(k): _int(v) for k, v in resources.items()}
                      if isinstance(resources, dict) else {}),
        "powers": powers,
    }


def wire_snapshot(state: dict[str, Any], *, index: int, verb: str,
                  command: str = "") -> dict[str, Any]:
    """One turn of the board, off the wire, for the grader and nobody else.

    Taken from the state the seat ACTED ON -- pre-post, the board the decision
    was made against -- because every threshold this exists for asks whether a
    call matched the board the caller could see.
    """
    p = _player(state)
    battle = _blob(state, "battle")
    enemies = _enemies(state)
    snap: dict[str, Any] = {
        "index": index,
        "verb": verb,
        "command": command,
        "state_type": _text(state.get("state_type")),
        "turn": _int(battle.get("round")),
        "battle_turn": _int(battle.get("turn")),
        "energy": _int(p.get("energy")),
        "max_energy": _int(p.get("max_energy")),
        "hp": _int(p.get("hp")),
        "max_hp": _int(p.get("max_hp")),
        "block": _int(p.get("block")),
        "meters": _snapshot_meters(state),
        "hand": _snapshot_hand(state),
        "piles": {"draw": _int(p.get("draw_pile_count")),
                  "discard": _int(p.get("discard_pile_count")),
                  "exhaust": _int(p.get("exhaust_pile_count"))},
        "enemy_count": len(enemies),
        "enemies": [{
            "entity_id": _entity_id(e),
            "name": _text(e.get("name")),
            "hp": _int(e.get("hp")),
            "max_hp": _int(e.get("max_hp", e.get("hp"))),
            "block": _int(e.get("block")),
            "intents": [{"type": _text(i.get("type")),
                         "label": _text(i.get("label")),
                         "title": _text(i.get("title"))}
                        for i in (e.get("intents") or [])
                        if isinstance(i, dict)],
        } for e in enemies],
    }
    # THE QUEUE STRIP, VERBATIM AND UNSCRUBBED. `kurage_memory()` above is the
    # PAGE's reading and deliberately drops the per-row `state` id; a grader is
    # entitled to the developer's vocabulary the page must not print, so the
    # raw map goes here. An absent key stays absent: no memory rule in this
    # build (`PROTOTYPE_CARDS` undefined) is a different fact from an empty
    # memory, and both differ from a populated one.
    memory = p.get("kurage_memory")
    if isinstance(memory, dict):
        snap["kurage_memory"] = memory
    # `EB-273`. THE KOKOMI ARM'S OWN METER, on the same terms as the strip
    # above and for the same reason. The wire has carried `player.kokomi_plans`
    # since the Plan build (`vendor/STS2_MCP/gits/GitsKokomiPlan.cs`) and
    # `kokomi_plans()` puts it on the tester's PAGE -- but the snapshot the
    # GRADER reads carried none of it, so "the queue was empty when the call
    # was made" was not a fact a seat run could be asked. The map goes in raw
    # and unscrubbed (the page's reading drops the pet's entity id; a grader is
    # entitled to the id a play aimed at), and an absent key stays absent: no
    # Plan rule in this build is a different fact from an empty queue.
    plans = p.get("kokomi_plans")
    if isinstance(plans, dict):
        snap["kokomi_plans"] = plans
    return snap


# The two verbs a snapshot is taken on: every play, and every end of turn.
SNAPSHOT_VERBS = ("play", "end turn")


def ledger_rows(wire: Any, after_index: int = 0) -> tuple[list[dict[str, Any]],
                                                          str]:
    """The meter-ledger rows minted since `after_index`, and a note.

    `EB-216` / R225's clause. The mod keeps one ledger of every meter mutation
    routed through its own gain/spend chokepoints, each named by the ENGINE
    EVENT that made it. This is the read; `understudy.bridge.meter_ledger` is
    the route.

    THE NOTE IS RETURNED RATHER THAN RAISED, and the distinction it carries is
    the one the bridge is careful about: `unavailable` means this build has no
    klee mod to ask, and is a different fact from a ledger that exists and is
    empty. A wire that cannot answer at all is `error: ...` -- a snapshot with
    no ledger is still a snapshot, and a run must never die because an
    instrument did.
    """
    read = getattr(wire, "meter_ledger", None)
    if read is None:
        return [], "no ledger route on this wire"
    try:
        blob = read()
    except bridge.BridgeError as exc:
        return [], f"error: {exc}"
    if not isinstance(blob, dict):
        return [], "error: the ledger route did not answer with an object"
    if not blob.get("available"):
        return [], "unavailable: this build has no meter ledger"
    all_rows = [r for r in (blob.get("rows") or []) if isinstance(r, dict)]
    # THE LEDGER RESTARTS ITS NUMBERING AT EVERY COMBAT, because a row carried
    # between fights would let a grader attribute a spend to the wrong one. A
    # watermark the ledger has fallen behind therefore means "new fight", not
    # "nothing new" -- filtering on it blindly would drop a whole fight.
    highest = max((_int(r.get("index")) for r in all_rows), default=0)
    if highest < after_index:
        return all_rows, ""
    return [r for r in all_rows if _int(r.get("index")) > after_index], ""

