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
        id=f"status_{status_id}", name=spec["name"], cost=0, type="status",
        rarity="basic", tags=list(spec.get("tags", [])),
        status_eot_damage=spec.get("eot", 0),
        status_draw_damage=spec.get("draw", 0))
