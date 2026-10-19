"""The true-HP-loss hook.

Deliberately low in the import graph (state + constants only) so effects.py,
powers.py and the rest can call it without a cycle.

The shipped kit's Encore buffer, Charge (Kokomi) and Burst meters left the sim
on 2026-10-08 with the rest of the shipped-kit machinery, and the shipped
Fanfare meter followed on 2026-10-19: the Stage had retired it for the only
character that carried it. Furina's Fanfare is the Stage's, in `furina_tide`
and `furina_stage`.
"""

from __future__ import annotations

from tier0.engine.state import CombatState


def note_player_hp_loss(state: CombatState, n: int) -> None:
    """The hook for TRUE HP loss (enemy hits reaching HP, DoT, self-damage).
    Callers deduct HP themselves; this only records the flux."""
    if n <= 0:
        return
    state.hp_lost_this_turn += n
    state.hp_lost_since_last_turn += n
    state.hp_lost_this_combat += n           # Facade (the Furina sweep)
    state.player_damage_events += 1
    # THE FURINA RESEARCH SLICE (`furina_tide`, sim only): HP lost prints
    # Fanfare 1:1 on that arm. A no-op for anyone else.
    from tier0.engine import furina_tide           # late: avoids the cycle
    furina_tide.on_hp_loss(state, n)
    # THE FONTAINE POOL REWORK (2026-10-19): Wriothesley's Chilling Penalty,
    # a Cryo hit on any HP lost, at this one funnel (`ChillingPenaltyPower`).
    from tier0.engine import effects               # late: avoids the cycle
    effects.chilling_penalty(state)
