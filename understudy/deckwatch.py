"""What the deck currently is, reconstructed from combat.

The bridge does not expose `player.deck` outside combat. At a card reward --
the one screen where the draft policy most needs the deck -- the wire carries
the three offers and nothing else. Scoring `score_offer` against an empty deck
would silently disable core progress, block density, the curve penalty and the
bloat penalty, which is most of what the draft policy IS.

Inside combat the deck is fully visible: hand + draw + discard + exhaust is
exactly the deck. So the watcher snapshots that union every time it sees a
combat state, and the draft counterfactual reads the most recent snapshot.

The known staleness, stated rather than papered over: a snapshot is as old as
the last fight. A card added at the reward screen immediately after that fight
is not in it, and neither is a shop purchase or an event gift, until the next
combat re-observes the deck. In practice that is one card of drift at the
moment of a draft decision -- the deck the policy scores against is the deck
that FOUGHT, which is arguably the right denominator anyway.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STORE = Path(__file__).resolve().parent / "logs" / "_deck.json"

PILES = ("hand", "draw_pile", "discard_pile", "exhaust_pile")


def record(state: dict[str, Any]) -> list[str] | None:
    """Snapshot the deck if this state is a combat state. Returns it, or None."""
    p = state.get("player") or {}
    if not any(isinstance(p.get(k), list) for k in PILES):
        return None
    ids: list[str] = []
    for pile in PILES:
        for e in p.get(pile) or []:
            if isinstance(e, dict) and e.get("id"):
                ids.append(str(e["id"]))
    if not ids:
        return None

    # WHEN to trust a snapshot. At round 1 every card is in hand or draw, so
    # the union is exactly the deck -- that is the authoritative reading, and
    # it is the only one that can observe a REMOVAL. Later rounds can lose
    # cards to exhaust-and-clear or to a post-fight state where the piles have
    # already been torn down, so a mid-fight union is only accepted when it is
    # bigger than what we already hold. Without this the snapshot taken at the
    # victory screen (3 cards) replaced the real deck (13).
    rnd = (state.get("battle") or {}).get("round")
    if rnd != 1 and len(ids) <= len(current()):
        return None

    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps({
        "ids": ids,
        "act": (state.get("run") or {}).get("act"),
        "floor": (state.get("run") or {}).get("floor"),
        "round": (state.get("battle") or {}).get("round"),
    }, indent=1), encoding="utf-8")
    return ids


def current() -> list[str]:
    if not STORE.exists():
        return []
    try:
        return list(json.loads(STORE.read_text(encoding="utf-8")).get("ids") or [])
    except (json.JSONDecodeError, OSError):
        return []


def provenance() -> dict[str, Any]:
    if not STORE.exists():
        return {}
    try:
        d = json.loads(STORE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {k: d.get(k) for k in ("act", "floor", "round")}


def reset() -> None:
    if STORE.exists():
        STORE.unlink()
