"""Counter-based powers with four hooks (spec §4.3).

Implemented: strength, weak, vulnerable, dot (generic poison-like),
metallicize, plus elemental auras which live on Enemy directly (reactions.py).
Nothing else until a card needs it.

Powers are plain stack counts in Fighter.powers; this module holds the
rules for how stacks modify damage and what ticks at turn boundaries.
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.engine.state import CombatState, Fighter

DECAYING = ("weak", "vulnerable")   # tick down at their owner's turn end


def modify_damage_dealt(attacker: Fighter, base: float) -> float:
    dmg = base + attacker.powers.get("strength", 0)
    if attacker.powers.get("weak", 0) > 0:
        dmg *= C.WEAK_DEALT_MULT
    return dmg


def modify_damage_taken(defender: Fighter, dmg: float) -> float:
    if defender.powers.get("vulnerable", 0) > 0:
        dmg *= C.VULNERABLE_TAKEN_MULT
    return dmg


def on_turn_start(state: CombatState, fighter: Fighter) -> None:
    if fighter.powers.get("metallicize", 0):
        fighter.block += fighter.powers["metallicize"]
    dot = fighter.powers.get("dot", 0)
    if dot > 0:
        # DoT ignores block, StS-poison-like -- but the player's Encore
        # buffer absorbs it first (kickoff §4: chip-reduction, credited
        # A4). Enemies have no encore; the import is late to keep powers
        # below resources in the module graph.
        hp_loss = dot
        if getattr(fighter, "encore", 0) > 0:
            from tier0.engine import resources
            hp_loss = resources.absorb_into_encore(state, dot)
        fighter.hp -= hp_loss
        state.emit("dot_tick", amount=dot, target=getattr(fighter, "name", "player"))
        if hp_loss and getattr(fighter, "fanfare_cap", 0):
            from tier0.engine import resources
            resources.note_player_hp_loss(state, hp_loss)
        fighter.powers["dot"] = dot - 1         # decays by 1 per tick


def on_turn_end(state: CombatState, fighter: Fighter) -> None:
    for name in DECAYING:
        if fighter.powers.get(name, 0) > 0:
            fighter.powers[name] -= 1


def apply_power(state: CombatState, target: Fighter, name: str, stacks: int,
                max_stacks: int | None = None) -> None:
    new = target.powers.get(name, 0) + stacks
    if max_stacks is not None:              # sheet v0.2 stack caps
        new = min(new, max_stacks)
    target.powers[name] = new
    state.emit("apply_power", power=name, stacks=stacks,
               target=getattr(target, "name", "player"))
