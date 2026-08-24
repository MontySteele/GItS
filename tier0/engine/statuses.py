"""Status cards (multi-act §10.2, RATIFIED 2026-07-23): the injection op's
payload. Enemies shuffle these into the player's combat piles via the
`inject` intent (combat._enemy_turn); they are UNPLAYABLE clogs
(combat.card_playable refuses type == "status"), never enter the run deck
(the run layer rebuilds the player from deck_ids each fight), and never
appear in any pool, reward, or the frozen battery.

Semantics per status (real StS2 where codeable; deviations logged §10.9):
  dazed  -- unplayable, ethereal (exhausts from hand at turn end; the
            existing ethereal hand-flush branch handles it for free)
  wound  -- unplayable clog, circulates
  slimed -- unplayable clog, circulates. UNIMPLEMENTED: the real card's
            "1: exhaust" self-removal (§10.9 backlog)
  burn   -- 2 damage at end of player turn while in hand (blockable)
  wither -- 3 damage at end of player turn while in hand (blockable; STS2.
            UNIMPLEMENTED: upgrade-to-6 escalation, §10.9)
  toxic  -- 2 HP loss ON DRAW (§10.3 ratified semantics), circulates
"""

from __future__ import annotations

from tier0.engine.state import Card

_SPECS = {
    "dazed":  {"name": "Dazed", "tags": ["ethereal"]},
    "wound":  {"name": "Wound"},
    "slimed": {"name": "Slimed"},
    "burn":   {"name": "Burn", "eot": 2},
    "wither": {"name": "Wither", "eot": 3},
    "toxic":  {"name": "Toxic", "draw": 2},
}

# The id namespace these cards live in. Named rather than spelled inline
# because a second site now has to RECOGNISE one: a status is in no pool and
# no loader index, so any path holding a card ID rather than a card object
# needs a way to tell "the loader has never heard of this" from "this is a
# clog the engine synthesizes" (EB-123). The two namespaces are disjoint and
# a test pins that they stay so.
STATUS_ID_PREFIX = "status_"


def status_ids() -> tuple[str, ...]:
    return tuple(sorted(_SPECS))


def make_status(status_id: str) -> Card:
    """A FRESH Card instance per call -- injected copies must never share
    identity (pile membership is object-based)."""
    try:
        spec = _SPECS[status_id]
    except KeyError:
        raise ValueError(
            f"unknown status {status_id!r}; known: {sorted(_SPECS)}"
        ) from None
    return Card(
        id=f"{STATUS_ID_PREFIX}{status_id}", name=spec["name"], cost=0,
        type="status", rarity="basic", tags=list(spec.get("tags", [])),
        status_eot_damage=spec.get("eot", 0),
        status_draw_damage=spec.get("draw", 0))


def status_from_card_id(card_id: str) -> Card | None:
    """`make_status` read backwards: a fresh Card for a synthesized status
    ID, or None for anything that is not one.

    None rather than an exception because the caller's question is "is this
    id mine?", and the answer "no" is the common case, not an error.
    """
    if not card_id.startswith(STATUS_ID_PREFIX):
        return None
    status_id = card_id[len(STATUS_ID_PREFIX):]
    if status_id not in _SPECS:
        return None
    return make_status(status_id)
