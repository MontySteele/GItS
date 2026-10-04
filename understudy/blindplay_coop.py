"""Co-op: the other player, the votes, and waiting for them.

A blind seat in a co-op run shares the run with another seat it cannot talk to.
Everything here is the page's half of that, read off the multiplayer state the
bridge serves once a co-op run is in progress (`bridge.get_state` routes there
on the singleplayer route's 409): `players[]` for every player's HP, Block,
end-turn readiness and pets, and the vote blocks on the map, a shared event and
a chest.

NOTHING HERE FIRES OUTSIDE A CO-OP RUN. Every reader starts from `is_coop`,
which asks the wire's own `game_mode`, so a singleplayer state -- every state
this page was built for before co-op -- gets `None` back and the page is
exactly what it was.

WAITING IS A SCREEN STATE, NOT A STALL. After `end turn` the fight does not
move until the other player ends theirs too, and after a map vote the party
does not move until both have voted. Without a word for that, the next
`observe` reads the same board and a seat takes it for a dead command. So the
page says what it is waiting on, and `wait` blocks (bounded) until something
the other player did shows on the wire.

Design-blind like every `blindplay_*` seam: it imports the page's own readers
and nothing from `soak`, `embark` or a sheet.
"""
from __future__ import annotations

import json
import re
import time
from typing import Any, Callable

from understudy.blindplay_board import _map_nodes, _map_options
from understudy.blindplay_faces import _named_option
from understudy.blindplay_read import (_blob, _fold, _hand, _int, _listing,
                                       _player, _text)
from understudy.blindplay_shape import COMBAT_SCREENS

#: `wait` with no number waits this long, and no `wait` waits longer than the
#: ceiling: a seat whose partner has gone quiet gets the page back rather than
#: a command that never returns.
WAIT_DEFAULT_S = 60
WAIT_MAX_S = 300
WAIT_POLL_S = 1.0

#: The line `wait` is offered under on a waiting page.
WAIT_COMMAND = ("wait   (holds until the other player does something, "
                f"up to {WAIT_DEFAULT_S} seconds; wait 120 holds longer, at "
                f"most {WAIT_MAX_S})")

#: What `wait` answers where there is nobody to wait for.
NO_PARTNER = ("there is no other player in this run, so there is nothing to "
              "wait for")

#: The base game's ally target: "any player excluding itself". Singleplayer
#: never offers one (the card is unplayable with no living ally).
ALLY_TARGETS = frozenset({"anyally"})


def is_coop(state: dict[str, Any]) -> bool:
    """Is this a co-op run's state? The wire's own `game_mode` decides."""
    return _text(state.get("game_mode")).lower() == "multiplayer"


def _rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in (state.get("players") or []) if isinstance(p, dict)]


def _me(state: dict[str, Any]) -> dict[str, Any]:
    return next((p for p in _rows(state) if p.get("is_local") is True), {})


def partners(state: dict[str, Any]) -> list[dict[str, Any]]:
    """The other players' rows, in the wire's order."""
    return [p for p in _rows(state) if p.get("is_local") is not True]


def partner_name(state: dict[str, Any]) -> str:
    """How the page names the other player: their character's printed name.

    Two seats on one character are both called by it, so the page says
    "the other player" there rather than a name that is also yours.
    """
    others = partners(state)
    if len(others) != 1:
        return "the other players"
    name = _text(others[0].get("character"))
    mine = _text(_me(state).get("character"))
    if not name or _fold(name) == _fold(mine):
        return "the other player"
    return name


# ----------------------------------------------------------- the partner --

def _pet_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    """A partner's pets, the stage's performers named by their seat."""
    pets = [p for p in (row.get("pets") or []) if isinstance(p, dict)
            and p.get("alive") is not False and _text(p.get("name"))]
    on_stage = [p for p in pets if p.get("stage_member") is not None]
    out = []
    for pet in pets:
        entry = {"name": _text(pet.get("name")), "hp": _int(pet.get("hp")),
                 "max_hp": _int(pet.get("max_hp")),
                 "block": _int(pet.get("block")), "seat": "",
                 "stage": pet.get("stage_member") is not None}
        if pet.get("stage_member") is not None:
            # The re-founding (2026-10-04): seats front to back, no bars.
            seat = _int(pet.get("stage_seat"))
            entry["seat"] = ("front" if seat <= 0 or len(on_stage) <= 1
                             else f"seat {seat + 1}")
        out.append(entry)
    return out


def _partner_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for row in partners(state):
        out.append({
            "name": _text(row.get("character")) or "the other player",
            "hp": _int(row.get("hp")), "max_hp": _int(row.get("max_hp")),
            "block": (_int(row.get("block"))
                      if row.get("block") is not None else None),
            "alive": row.get("is_alive") is not False,
            "ready": (row.get("is_ready_to_end_turn")
                      if isinstance(row.get("is_ready_to_end_turn"), bool)
                      else None),
            "pets": _pet_rows(row),
        })
    return out


# ------------------------------------------------------------- the votes --

def _vote_rows(blob: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return [v for v in (blob.get(key) or []) if isinstance(v, dict)]


def _map_vote_name(state: dict[str, Any], vote: dict[str, Any]) -> str:
    """The printed name of the node a map vote went to, as `go` names it."""
    col, row = vote.get("vote_col"), vote.get("vote_row")
    for raw, option in zip(_map_nodes(state), _map_options(state)):
        if isinstance(raw, dict) and raw.get("col") == col \
                and raw.get("row") == row:
            return option["name"]
    return "a room this page is not offering you"


def _indexed_name(options: list[Any], index: Any) -> str:
    """The printed name of the option whose wire `index` is `index`."""
    for pos, raw in enumerate(options):
        wire = raw.get("index") if isinstance(raw, dict) else None
        if (wire if wire is not None else pos) == index:
            return _named_option(raw)["name"] or f"option {pos + 1}"
    return "an option this page is not showing"


def votes(state: dict[str, Any]) -> tuple[list[str], bool, bool]:
    """`(lines, you have voted, everyone has voted)` for this screen's vote.

    Empty lines where the screen has no vote (and `True, True`, so nothing
    waits on it): the map, a SHARED event and a chest's relic bid are the
    three the wire reports.
    """
    st = _text(state.get("state_type"))
    if st == "map":
        blob, key, done = _blob(state, "map"), "votes", "all_voted"
        name = lambda v: _map_vote_name(state, v)              # noqa: E731
    elif st == "event" and _blob(state, "event").get("is_shared") is True:
        blob, key, done = _blob(state, "event"), "votes", "all_voted"
        opts = _listing(state, "event.options", "options")
        name = lambda v: _indexed_name(opts, v.get("vote_option"))  # noqa
    elif st == "treasure" and _blob(state, "treasure").get("bids"):
        blob, key, done = _blob(state, "treasure"), "bids", "all_bid"
        relics = _listing(state, "treasure.relics", "relics")
        name = lambda v: _indexed_name(relics,                  # noqa: E731
                                       v.get("vote_relic_index"))
    else:
        return [], True, True
    rows = _vote_rows(blob, key)
    if not rows:
        return [], True, True
    lines, mine = [], False
    for v in rows:
        who = ("You" if v.get("is_local") is True
               else _text(v.get("player")) or "The other player")
        if v.get("voted") is True:
            lines.append(f"{who}: {name(v)}")
            mine = mine or v.get("is_local") is True
        else:
            lines.append(f"{who}: not chosen yet")
    everyone = (blob.get(done) is True
                or all(v.get("voted") is True for v in rows))
    return lines, mine, everyone


# ------------------------------------------------------------ the block --

def coop_block(state: dict[str, Any]) -> dict[str, Any] | None:
    """The co-op part of one observation, or `None` outside a co-op run.

    `waiting` is the one sentence that says what the run is waiting on, and
    is empty whenever this seat has something of its own to do.
    """
    if not is_coop(state):
        return None
    st = _text(state.get("state_type"))
    who = partner_name(state)
    me = _me(state)
    lines, voted, everyone = votes(state)
    waiting = ""
    if st in COMBAT_SCREENS and isinstance(state.get("battle"), dict):
        if me.get("is_alive") is False:
            waiting = (f"You are down. {who} fights on; the fight ends "
                       f"when they win it or fall too. Say `wait`.")
        elif (me.get("is_ready_to_end_turn") is True
              and _blob(state, "battle").get("all_players_ready") is not True):
            waiting = (f"You have ended your turn. {who} is still playing "
                       f"theirs; the enemies act once both of you have "
                       f"ended. Say `wait`.")
    elif lines and voted and not everyone:
        what = {"map": "the party moves when both of you have chosen",
                "event": "the event goes on when both of you have chosen",
                "treasure": "the chest is shared out when both of you have "
                            "chosen"}.get(st, "")
        waiting = (f"You have chosen; {who} has not yet"
                   + (f", and {what}" if what else "") + ". Say `wait`, or "
                   "choose again to change yours.")
    return {"partner": who, "partners": _partner_rows(state),
            "votes": lines, "waiting": waiting}


def ally_forms(state: dict[str, Any]) -> list[str]:
    """The `play ... on "<player>"` form, where a card in hand aims at one."""
    if not is_coop(state) or not any(
            _fold(c.get("target_type")) in ALLY_TARGETS for c in _hand(state)):
        return []
    names = [p["name"] for p in _partner_rows(state) if p["alive"]]
    return [f'play "<card title>" on "{n}"   (a card that targets another '
            f"player)" for n in names]


def ally_target(state: dict[str, Any], entry: dict[str, Any],
                named: str) -> tuple[str, str, str] | None:
    """`(entity id, printed name, refusal)` for a card aimed at a player.

    `None` where the card does not aim at another player, or the run is not
    co-op -- the caller's ordinary path then runs untouched. With one living
    teammate an unnamed target means them, as the game's own drag would have
    to; a name picks among them by the character name the page prints.
    """
    if not is_coop(state) or _fold(entry.get("target_type")) not in ALLY_TARGETS:
        return None
    alive = [p for p in partners(state) if p.get("is_alive") is not False]
    if named:
        hits = [p for p in alive if _fold(p.get("character")) == _fold(named)]
    else:
        hits = alive if len(alive) == 1 else []
    printed = [_text(p.get("character")) for p in alive]
    if not hits:
        why = (f"no other player here is called {named!r}" if named
               else "this card goes to another player; say which")
        return "", "", (f"{why}. The players it can go to: "
                        + (", ".join(printed) or "none left standing"))
    row = hits[0]
    name = _text(row.get("character"))
    handle = _text(row.get("entity_id"))
    if not handle:
        return "", name, (f"the game did not say where {name} stands, so a "
                          f"card aimed at them cannot be sent from here (this "
                          f"build of the bridge does not carry it)")
    return handle, name, ""


def waiting_refusal(state: dict[str, Any], verb: str) -> str:
    """A refusal for a fight command typed while this seat's turn is ended."""
    info = coop_block(state)
    if not info or not info["waiting"] or verb not in ("play", "end turn"):
        return ""
    return info["waiting"]


# -------------------------------------------------------------- waiting --

_WAIT = re.compile(r"wait(?:\s+(?:for\s+)?(\d+)\s*(?:s|secs?|seconds?)?)?")


def parse_wait(head: str) -> int:
    """`wait` / `wait 30` / `wait 30s` -> seconds, bounded. Else -1."""
    m = _WAIT.fullmatch(" ".join(str(head or "").casefold().split()))
    if m is None:
        return -1
    if m.group(1) is None:
        return WAIT_DEFAULT_S
    return max(1, min(WAIT_MAX_S, int(m.group(1))))


def signature(state: dict[str, Any]) -> str:
    """What the other player's actions can move, as one comparable string.

    The screen and the run's place, the fight's round and phase, every
    enemy's HP, Block and powers (a teammate's attack lands there), every
    player's HP, Block, readiness and pets, the three vote blocks, and this
    seat's own hand size. Nothing is read for meaning; `wait` only asks
    whether it moved.
    """
    battle = _blob(state, "battle")
    enemies = [(_text(e.get("name")), e.get("hp"), e.get("block"),
                [(_text(s.get("name")), s.get("amount"))
                 for s in (e.get("status") or []) if isinstance(s, dict)])
               for e in (battle.get("enemies") or []) if isinstance(e, dict)]
    players = [(_text(p.get("character")), p.get("hp"), p.get("block"),
                p.get("is_ready_to_end_turn"), p.get("is_alive"),
                [(q.get("hp"), q.get("block"), q.get("alive"))
                 for q in (p.get("pets") or []) if isinstance(q, dict)])
               for p in _rows(state)]
    voting = {k: (_blob(state, k).get("votes") or _blob(state, k).get("bids"))
              for k in ("map", "event", "treasure")}
    return json.dumps({
        "screen": state.get("state_type"), "run": state.get("run"),
        "battle": {k: battle.get(k) for k in ("round", "turn",
                                              "is_play_phase",
                                              "all_players_ready")},
        "enemies": enemies, "players": players, "votes": voting,
        "hand": len(_hand(state)),
        "options": len(_listing(state, "event.options")),
    }, sort_keys=True, default=str)


def wait_for_partner(wire: Any, state: dict[str, Any], seconds: int, *,
                     poll: float = WAIT_POLL_S,
                     clock: Callable[[], float] = time.monotonic,
                     sleep: Callable[[float], None] = time.sleep
                     ) -> tuple[dict[str, Any], float, bool]:
    """Block until the wire moves, or `seconds` pass. Never raises on time.

    Returns `(the last state read, seconds waited, whether it moved)`. The
    caller settles and renders it; this only watches.
    """
    before = signature(state)
    start = clock()
    latest = state
    while clock() - start < seconds:
        sleep(poll)
        latest = wire.get_state()
        if signature(latest) != before:
            return latest, clock() - start, True
    return latest, clock() - start, False


def wait_line(waited: float, moved: bool, state: dict[str, Any]) -> str:
    """The one sentence `wait` answers with, ahead of the new page."""
    who = partner_name(state) if is_coop(state) else "the other player"
    if moved:
        return f"Waited {waited:.0f}s; the game moved. The page now:"
    return (f"Waited {waited:.0f}s and nothing moved; {who} has not acted "
            f"yet. The page is unchanged.")


# ------------------------------------------------------------ rendering --

def render_lines(info: dict[str, Any]) -> list[str]:
    """`## The other player` -- their board, and any vote -- for the page."""
    out = ["", "## The other player", ""]
    for p in info["partners"]:
        bits = [f"HP {p['hp']}/{p['max_hp']}"]
        if p["block"]:
            bits.append(f"Block {p['block']}")
        if not p["alive"]:
            bits = ["down (0 HP)"]
        if p["ready"] is True:
            bits.append("has ended their turn")
        elif p["ready"] is False and p["alive"]:
            bits.append("still playing their turn")
        out.append(f"- **{p['name']}**: " + ", ".join(bits))
        for pet in p["pets"]:
            where = f" ({pet['seat']})" if pet["seat"] else ""
            # A stage performer has no HP or bar to print (the re-founding,
            # 2026-10-04): its name and seat only. Any other pet is HP.
            if pet["stage"]:
                out.append(f"  - {pet['name']}{where}")
                continue
            out.append(f"  - {pet['name']}{where}: HP {pet['hp']}/"
                       f"{pet['max_hp']}"
                       + (f", Block {pet['block']}" if pet["block"] else ""))
    if info["votes"]:
        out += ["", "Choices so far:"]
        out += [f"- {line}" for line in info["votes"]]
    return out


def banner(info: dict[str, Any] | None) -> list[str]:
    """The waiting sentence, at the top of the page, or nothing."""
    if not info or not info.get("waiting"):
        return []
    return [f"**WAITING.** {info['waiting']}", ""]
