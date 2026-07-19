"""Elemental aura + reaction resolver (spec §4.4). The important one.

Rules:
- One aura per enemy. Same-element hit refreshes duration; different-element
  hit consumes the aura and triggers the reaction table.
- Anemo and Geo never leave auras; they only trigger (design doc §2.1).
- IRON RULE: amplifiers (Vaporize/Melt) multiply ONE hit and consume the
  aura. They must never persist. tests/test_reactions.py asserts this.

resolve_hit() returns the (possibly amplified) damage for this hit and
performs any side effects (splash, powers, freeze, swirl, crystallize).
"""

from __future__ import annotations

from typing import Optional

from tier0 import constants as C
from tier0.engine import powers
from tier0.engine.state import CombatState, Enemy

AURA_ELEMENTS = {"pyro", "hydro", "electro", "cryo"}   # anemo/geo trigger only

_AMPLIFY = {
    frozenset(("pyro", "hydro")): ("vaporize", None),   # mult read at call time
    frozenset(("pyro", "cryo")): ("melt", None),
}


def _amp_mult(name: str) -> float:
    return C.VAPORIZE_MULT if name == "vaporize" else C.MELT_MULT


def apply_aura(state: CombatState, enemy: Enemy, element: str) -> None:
    """Pure application (no damage) — apply_aura op, or post-reaction stick."""
    if element not in AURA_ELEMENTS:
        return
    enemy.aura = element
    enemy.aura_turns_left = C.AURA_DURATION_TURNS
    state.emit("aura_applied", element=element, target=enemy.name)


def tick_auras(state: CombatState) -> None:
    """Called at player turn start; expires stale auras (logged as waste)."""
    for e in state.living_enemies:
        if e.aura:
            e.aura_turns_left -= 1
            if e.aura_turns_left <= 0:
                state.emit("aura_wasted", element=e.aura, target=e.name)
                e.aura = None


def resolve_hit(state: CombatState, enemy: Enemy, element: Optional[str],
                damage: float) -> float:
    """Element-tagged damage hits an enemy. Returns damage for THIS hit."""
    if not element or element == "none":
        return damage

    aura = enemy.aura
    if aura is None:
        apply_aura(state, enemy, element)
        return damage
    if aura == element:
        enemy.aura_turns_left = C.AURA_DURATION_TURNS   # refresh
        return damage

    # Different element on an existing aura: consume + react.
    enemy.aura = None
    enemy.aura_turns_left = 0
    return _react(state, enemy, trigger=element, aura=aura, damage=damage)


def _react(state: CombatState, enemy: Enemy, trigger: str, aura: str,
           damage: float) -> float:
    pair = frozenset((trigger, aura))
    name = None
    out = damage

    if trigger == "anemo":
        name = "swirl"
        for other in state.living_enemies:
            apply_aura(state, other, aura)
    elif trigger == "geo":
        name = "crystallize"
        state.player.block += C.CRYSTALLIZE_BLOCK
    elif pair in _AMPLIFY:
        name = _AMPLIFY[pair][0]
        out = damage * _amp_mult(name)
    elif pair == frozenset(("pyro", "electro")):
        name = "overload"
        for other in state.living_enemies:
            _splash(state, other, C.OVERLOAD_SPLASH)
    elif pair == frozenset(("electro", "cryo")):
        name = "superconduct"
        powers.apply_power(state, enemy, "vulnerable", C.SUPERCONDUCT_VULN)
    elif pair == frozenset(("hydro", "electro")):
        name = "electrocharged"
        powers.apply_power(state, enemy, "dot", C.ELECTROCHARGED_DOT)
    elif pair == frozenset(("hydro", "cryo")):
        name = "frozen"
        if enemy.is_boss and C.FROZEN_BOSS_RESIST:
            pass                                        # consumed, no skip
        else:
            enemy.frozen = True

    if name:
        state.emit("reaction", reaction=name, trigger=trigger, aura=aura,
                   target=enemy.name,
                   amp_delta=(out - damage) if out != damage else 0)
    return out


def _splash(state: CombatState, enemy: Enemy, amount: int) -> None:
    """Reaction splash damage: not element-tagged, ignores block per v1
    simplicity (applied equally to everyone — spec §1 non-goals)."""
    enemy.hp -= amount
    state.emit("damage", target=enemy.name, amount=amount, source="reaction_splash")
