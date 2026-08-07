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
from tier0.engine import powers, resources
from tier0.engine.state import CombatState, Enemy

AURA_ELEMENTS = {"pyro", "hydro", "electro", "cryo"}   # anemo/geo trigger only

_AMPLIFY = {
    frozenset(("pyro", "hydro")): ("vaporize", None),   # mult read at call time
    frozenset(("pyro", "cryo")): ("melt", None),
}


def _amp_mult(state: CombatState, name: str) -> float:
    base = C.VAPORIZE_MULT if name == "vaporize" else C.MELT_MULT
    # Vermillion Pact's amp_reaction_up is a PERCENT boost to the base
    # amplifier. +100 doubles Vaporize/Melt's multiplier; the +125 upgraded
    # form puts Melt at 3.9375, just below the 4x provenance detector.
    pct = state.player.powers.get("amp_reaction_up", 0)
    return base * (1 + pct / 100)


def aura_duration(state: CombatState) -> int:
    """Turns a freshly applied or refreshed aura lasts.

    Neuvillette's ancient_sea_authority extends it. Deliberately a function
    rather than a constant read at three call sites: application and refresh
    must never disagree about how long an aura lives, which they would the
    first time someone extended only one of them.
    """
    return C.AURA_DURATION_TURNS + state.player.powers.get(
        "ancient_sea_authority", 0)


def apply_aura(state: CombatState, enemy: Enemy, element: str,
               source: str = "hit") -> None:
    """Pure application (no damage) — apply_aura op, or post-reaction stick.

    `source` is LOG-ONLY (Last Call track H): it names which verb put the aura
    up, so "how often do aura-applying ops fire" can be separated from "how
    often does an element-tagged attack happen to leave one". It changes no
    behaviour and no existing field -- the `aura_applied` event gains a key and
    nothing reads it but `metrics.extract`.
    """
    if element not in AURA_ELEMENTS:
        return
    enemy.aura = element
    enemy.aura_turns_left = aura_duration(state)
    state.emit("aura_applied", element=element, target=enemy.name,
               source=source)


def tick_auras(state: CombatState) -> None:
    """Called at player turn start; expires stale auras (logged as waste)."""
    for e in state.living_enemies:
        if e.aura:
            e.aura_turns_left -= 1
            if e.aura_turns_left <= 0:
                state.emit("aura_wasted", element=e.aura, target=e.name)
                e.aura = None


def resolve_hit(state: CombatState, enemy: Enemy, element: Optional[str],
                damage: float, source: str = "hit") -> float:
    """Element-tagged damage hits an enemy. Returns damage for THIS hit.

    `source` is log-only provenance (track H); see `apply_aura`.
    """
    if not element or element == "none":
        return damage

    aura = enemy.aura
    if aura is None:
        apply_aura(state, enemy, element, source)
        return damage
    if aura == element:
        enemy.aura_turns_left = aura_duration(state)    # refresh
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
            apply_aura(state, other, aura, "swirl_spread")
    elif trigger == "geo":
        name = "crystallize"
        state.player.block += C.CRYSTALLIZE_BLOCK
    elif pair in _AMPLIFY:
        name = _AMPLIFY[pair][0]
        out = damage * _amp_mult(state, name)
    elif pair == frozenset(("pyro", "electro")):
        name = "overload"
        for other in state.living_enemies:
            _splash(state, other, C.OVERLOAD_SPLASH)
        # The explosion staggers the reacted target. This is ordinary Weak,
        # so it uses the shared debuff rules and never multiplies with Klee's
        # armed-Bomb suppression.
        if C.OVERLOAD_WEAK:
            powers.apply_power(state, enemy, "weak", C.OVERLOAD_WEAK)
    elif pair == frozenset(("electro", "cryo")):
        name = "superconduct"
        powers.apply_power(state, enemy, "vulnerable", C.SUPERCONDUCT_VULN)
    elif pair == frozenset(("hydro", "electro")):
        name = "electrocharged"
        powers.apply_power(state, enemy, "dot", C.ELECTROCHARGED_DOT)
    elif pair == frozenset(("hydro", "cryo")):
        name = "frozen"
        # NC-7 alpha (Q13 / R117, verbatim "I'd say A"): the Vulnerable
        # substitution is keyed on BOSS ROOM x NON-MINION -- the sim's
        # mirror of the mod's `RoomType == Boss && no MinionPower`
        # predicate (ReactionEffects.cs). Under alpha the freezable set in
        # a boss room is minion-flagged creatures ONLY, so a boss-room
        # helper (kaiser_rocket, a slotted monster, not a minion) now
        # takes Vulnerable where the pre-alpha per-creature `is_boss` read
        # froze it. That is R116's stated second-claw consequence,
        # DELIBERATELY overridden by [USER]'s alpha selection -- a chosen
        # reading, not a missed example. Room membership reads
        # state.enemies (not living_enemies), like the mod's RoomType,
        # which does not change when the boss dies first.
        boss_room = any(e.is_boss for e in state.enemies)
        if boss_room and not enemy.is_minion:
            # Substitution (round 3; stands post-errata, alpha-scoped).
            powers.apply_power(state, enemy, "vulnerable", C.FROZEN_BOSS_VULN)
        else:
            # v1.5: soft control — actions at -50%, shatterable. No skip.
            # NC-7 (R116): STACKING EXTENDS. One more turn on the timer per
            # application, which is what the mod's Counter power already did.
            enemy.frozen += 1
            enemy.frozen_by_companion = state.current_card_companion

    if name:
        state.reactions_this_card += 1
        state.reactions_this_turn += 1
        p = state.player
        # Courtroom Drama (Curtain Call B, R85): the FIRST reaction each
        # turn puts its target on the stand -- Vulnerable + Weak per stack.
        # Gated on the existing reactions_this_turn counter (== 1 is the
        # first), so a silent turn pays nothing and a reaction storm pays
        # once: activity-triggered, never per-turn, per the sheet header.
        n = p.powers.get("cross_examination", 0)
        if n and state.reactions_this_turn == 1:
            powers.apply_power(state, enemy, "vulnerable", n)
            powers.apply_power(state, enemy, "weak", n)
        if p.burst_max:
            resources.gain_burst(state, C.BURST_PER_REACTION, "reaction")
        # Catalytic Converter (R120 rename; id catalytic_conversion unchanged):
        # reactions grant bonus sparks + burst energy.
        bonus = p.powers.get("reaction_bonus_spark_energy", 0)
        if bonus:
            p.sparks += bonus
            resources.gain_burst(
                state, C.CATALYTIC_BURST_PER_REACTION * bonus, "catalytic")
        state.emit("reaction", reaction=name, trigger=trigger, aura=aura,
                   target=enemy.name,
                   amp_delta=(out - damage) if out != damage else 0)
    return out


def _splash(state: CombatState, enemy: Enemy, amount: int) -> None:
    """Reaction splash damage: not element-tagged, ignores block per v1
    simplicity (applied equally to everyone — spec §1 non-goals).

    OVERKILL IS CLAMPED OUT OF THE EMITTED AMOUNT (audit 2026-07-26 §1.7,
    fixed in EPOCH 1). The canonical path in effects.deal_damage_to_enemy
    has always clamped -- `effective = min(hp_dmg, max(0, enemy.hp))` -- and
    this path did not, so 8 splash into a 3 HP swarm add credited 8 to
    `total_damage_dealt` instead of 3.

    That is not a rounding issue: A6 is a ratified elite axis, it is summed
    from these emitted amounts, and the over-read scaled with the number of
    small adds a hit could spill over. So it over-read hardest for exactly
    the reaction archetypes A6 exists to grade, and the same events feed
    `reaction_damage_share`.

    HP still takes the full unclamped hit; only the accounting is clamped.
    """
    from tier0.engine import refpowers              # late import (cycle)
    amount = int(refpowers._intangible_cap(enemy, amount))    # R128: per hit
    effective = min(amount, max(0, enemy.hp))
    enemy.hp -= amount
    state.emit("damage", target=enemy.name, amount=effective,
               source="reaction_splash")
