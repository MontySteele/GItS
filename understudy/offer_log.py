"""The card offers a seat saw, and what it took (project review 2026-10-08,
pick 10, Varka).

A round has to tell "the payoff was offered and passed" from "the payoff was
never offered". The mod's telemetry cannot: `PlayTelemetry` logs plays, and
`SelectionTelemetry` records only in-fight choosers, only against an open
fight record, and nothing on a skip (its own declared limits). Card rewards,
shops and event choosers all happen outside a fight. The bridge sees every one
of them, because the seat's `blindplay act` reads the screen and posts the
answer in one process. So this log is written there: after a command on an
offer screen has been POSTED, one row goes to
`understudy/logs/offers/card-offers-lane<N>.jsonl` (gitignored).

WHAT IS LOGGED (one row per accepted command on an offer screen):

  * `card_reward` -- the cards on the screen; `choose` is `taken`, `skip`
    and `sacrifice` are `skipped`. The room the reward came from (`monster`,
    `elite`, `boss`, ...) is the map node the lane last walked into, which
    this module remembers on each `go`.
  * `shop` (and the `?` room's fake merchant) -- the card shelves with prices,
    on every command sent in the shop; a `buy` of a card is `bought`, any
    other command is `seen`. The reader folds one shop visit into one offer.
  * `choose` / `simple_select` -- an out-of-fight card chooser (an event's or
    an Ancient's "choose a card"). A `simple_select` grid whose cards are all
    already in the deck is a deck operation, not an offer, and is not logged;
    the deck screens (`select`, `upgrade`, `transform`, `enchant`) never are.
  * `bundle` -- a bundle chooser: every card in every bundle, each with its
    bundle number; `choose` takes the whole bundle.
  * `card_reward_unopened` -- `proceed` from a reward screen that still held a
    card reward. The cards were never on the wire, so the row has none; the
    reader drops it when the same floor also has a `card_reward` row (opened,
    skipped, then left).

NEVER BREAKS A COMMAND. `record` swallows everything: an instrument that can
fail an act is not an instrument.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

from understudy.blindplay_board import _bundle_cards, _map_nodes
from understudy.blindplay_faces import _shop_items
from understudy.blindplay_read import _blob, _int, _listing, _screen, _text
from understudy.blindplay_shape import (
    lane_embark_stamp, lane_run_seed, lane_state_dir, lane_tag,
    read_state_json, write_atomic)

SCHEMA = 1
OFFER_LOG_ENV = "GITS_OFFER_LOG_DIR"
DEFAULT_DIR = Path(__file__).resolve().parent / "logs" / "offers"

#: The `card_select` screen types that offer cards from OUTSIDE the deck.
CHOOSER_TYPES = frozenset({"choose", "simple_select"})

_TAKE_VERBS = frozenset({"choose"})
_SKIP_VERBS = frozenset({"skip", "sacrifice"})


def log_dir() -> Path:
    env = os.environ.get(OFFER_LOG_ENV, "").strip()
    return Path(env) if env else DEFAULT_DIR


def log_path(lane: object = None) -> Path:
    return log_dir() / f"card-offers-lane{lane_tag(lane)}.jsonl"


def _room_path(lane: object = None) -> Path:
    return lane_state_dir(lane) / f"_offer-room-lane{lane_tag(lane)}.json"


# ----------------------------------------------------------------- cards --

def card_row(entry: dict[str, Any], *, prefix: str = "") -> dict[str, Any]:
    """One offered card: id, name (without `+`), upgraded, rarity."""
    name = _text(entry.get(f"{prefix}name"))
    upgraded = entry.get("is_upgraded")
    if not isinstance(upgraded, bool):
        upgraded = name.endswith("+")
    row: dict[str, Any] = {"id": _text(entry.get(f"{prefix}id")),
                           "name": name.rstrip("+").strip(),
                           "upgraded": bool(upgraded or name.endswith("+"))}
    rarity = _text(entry.get(f"{prefix}rarity"))
    if rarity:
        row["rarity"] = rarity.lower()
    return row


def _cards(entries: list[Any]) -> list[dict[str, Any]]:
    return [card_row(e) for e in entries
            if isinstance(e, dict) and _text(e.get("name"))]


def _deck_names(state: dict[str, Any]) -> list[str]:
    deck = _blob(state, "player").get("master_deck")
    return [_text(c.get("name")) for c in deck or []
            if isinstance(c, dict)] if isinstance(deck, list) else []


def _all_in_deck(cards: list[dict[str, Any]], deck: list[str]) -> bool:
    """True when every card is a copy already in the deck (a multiset)."""
    if not deck:
        return False
    left = list(deck)
    for c in cards:
        shown = c["name"] + ("+" if c["upgraded"] else "")
        hit = shown if shown in left else (c["name"] if c["name"] in left
                                           else None)
        if hit is None:
            return False
        left.remove(hit)
    return True


# ---------------------------------------------------------------- screens --

def _offer(state: dict[str, Any], res: dict[str, Any]
           ) -> tuple[str, list[dict[str, Any]], str, list[dict[str, Any]]]:
    """`(screen, offered, outcome, taken)`; `screen == ""` when the command
    was not an answer to a card offer."""
    st = _screen(state)
    verb = _text(res.get("verb"))
    post = res.get("post") or {}
    if st == "card_reward":
        offered = _cards(_listing(state, "card_reward.cards", "cards"))
        if verb in _TAKE_VERBS:
            idx = post.get("card_index")
            taken = [offered[idx]] if isinstance(idx, int) \
                and 0 <= idx < len(offered) else []
            return st, offered, "taken", taken
        if verb in _SKIP_VERBS:
            return st, offered, "skipped", []
        return "", [], "", []
    if st in ("shop", "fake_merchant"):
        offered = []
        for item in _shop_items(state):
            if _text(item.get("category")).lower() != "card" \
                    or not _text(item.get("card_name")):
                continue
            row = card_row(item, prefix="card_")
            row["price"] = item.get("price")
            row["stocked"] = item.get("is_stocked") is not False
            offered.append(row)
        if not offered:
            return "", [], "", []
        printed = res.get("printed") or {}
        if verb == "buy" and _text(printed.get("kind")).lower() \
                .startswith("card"):
            name = _text(printed.get("item")).rstrip("+").strip()
            taken = [c for c in offered if c["name"] == name][:1]
            return "shop", offered, "bought", taken
        return "shop", offered, "seen", []
    if st == "card_select" and not state.get("battle"):
        blob = _blob(state, "card_select")
        kind = _text(blob.get("screen_type"))
        if kind not in CHOOSER_TYPES:
            return "", [], "", []
        offered = _cards(_listing(state, "card_select.cards"))
        if not offered or (kind == "simple_select"
                           and _all_in_deck(offered, _deck_names(state))):
            return "", [], "", []
        if verb in _TAKE_VERBS:
            idx = post.get("index", post.get("card_index"))
            taken = [offered[idx]] if isinstance(idx, int) \
                and 0 <= idx < len(offered) else []
            return kind, offered, "taken", taken
        if verb in _SKIP_VERBS:
            return kind, offered, "skipped", []
        return "", [], "", []
    if st == "bundle_select":
        bundles = _listing(state, "bundle_select.bundles",
                           "bundle_select.cards", "bundles")
        offered = []
        for i, b in enumerate(bundles):
            for c in _cards(_bundle_cards(b)):
                c["bundle"] = i
                offered.append(c)
        if not offered:
            return "", [], "", []
        if verb in _TAKE_VERBS:
            idx = post.get("index")
            return ("bundle", offered, "taken",
                    [c for c in offered if c["bundle"] == idx])
        if verb in _SKIP_VERBS:
            return "bundle", offered, "skipped", []
        return "", [], "", []
    if st == "rewards" and verb == "proceed":
        left = [r for r in _listing(state, "rewards.items", "items")
                if isinstance(r, dict) and _text(r.get("type")) == "card"
                and not _text(r.get("card_name"))]
        if left:
            return "card_reward_unopened", [], "unopened", []
    return "", [], "", []


def remember_room(state: dict[str, Any], res: dict[str, Any],
                  lane: object = None) -> None:
    """On a `go`, keep the room type walked into, for the reward after it."""
    if _text(res.get("verb")) != "go":
        return
    idx = (res.get("post") or {}).get("index")
    nodes = _map_nodes(state)
    if not isinstance(idx, int) or not 0 <= idx < len(nodes):
        return
    node = nodes[idx] if isinstance(nodes[idx], dict) else {}
    room = _text(node.get("type")).lower()
    run = _blob(state, "run")
    write_atomic(_room_path(lane), json.dumps(
        {"room": room, "act": _int(run.get("act")),
         "from_floor": _int(run.get("floor"))}))


def _room(lane: object = None) -> str:
    held = read_state_json(_room_path(lane))
    return _text(held.get("room")) if isinstance(held, dict) else ""


def offer_row(state: dict[str, Any], res: dict[str, Any], command: str = "",
              lane: object = None, now: dt.datetime | None = None
              ) -> dict[str, Any] | None:
    """The row this accepted command writes, or None. Pure but for the lane's
    embark sidecar and room mark, which it reads."""
    screen, offered, outcome, taken = _offer(state, res)
    if not screen:
        return None
    run = _blob(state, "run")
    row: dict[str, Any] = {
        "schema": SCHEMA,
        "ts": (now or dt.datetime.now()).isoformat(timespec="seconds"),
        "lane": f"lane{lane_tag(lane)}",
        "embark": lane_embark_stamp(lane),
        "seed": lane_run_seed(lane),
        "character": _text(_blob(state, "player").get("character")),
        "act": _int(run.get("act")),
        "floor": _int(run.get("floor")),
        "ascension": _int(run.get("ascension")),
        "screen": screen,
        "offered": offered,
        "outcome": outcome,
        "taken": taken,
        "command": command,
    }
    if screen in ("card_reward", "card_reward_unopened"):
        row["room"] = _room(lane)
    return row


def record(state: dict[str, Any], res: dict[str, Any], command: str = "",
           lane: object = None) -> dict[str, Any] | None:
    """Append the row for one POSTED command, if it answered a card offer.
    Never raises."""
    try:
        remember_room(state, res, lane)
        row = offer_row(state, res, command, lane)
        if row is None:
            return None
        path = log_path(lane)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row
    except Exception:                                        # noqa: BLE001
        return None
