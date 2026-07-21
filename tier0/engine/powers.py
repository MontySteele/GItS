"""Counter-based powers with four hooks (spec §4.3).

Implemented: strength, weak, vulnerable, frail (block-gain reduction), dot
(generic poison-like), metallicize, plus elemental auras which live on Enemy
directly (reactions.py). Nothing else until a card needs it.

Powers are plain stack counts in Fighter.powers; this module holds the
rules for how stacks modify damage and what ticks at turn boundaries.
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.engine.state import CombatState, Fighter

DECAYING = ("weak", "vulnerable", "frail")   # tick down at owner's turn end
# This-turn windows: cleared entirely at their owner's turn end (R16
# card-mediated Spotlight boosts; a _turn power is a window, not a stack).
EXPIRING = ("spotlight_mult_bonus_turn", "spotlight_flat_damage_turn")


def _floor(dmg: float) -> float:
    """Hooks.Hook.ModifyDamage's last statement is `return Math.Max(0m, num)`:
    the whole additive+multiplicative chain is clamped at zero BEFORE the
    number ever reaches Creature.DamageBlockInternal.

    tier0 splits that chain across modify_damage_dealt / modify_damage_taken,
    so both ends clamp. Without it a big negative Strength (Mangle's
    StrengthLoss is far larger than a typical tier0 intent) reaches
    combat._enemy_turn's `blocked = min(block, dmg); block -= blocked`, where a
    dmg of -4 makes the player GAIN 4 block from being attacked -- an
    invisible gift to the block and survival axes. No multiplier in the chain
    is negative, so clamping at both ends is identical to clamping once.
    """
    return dmg if dmg > 0 else 0.0


def modify_damage_dealt(attacker: Fighter, base: float) -> float:
    dmg = base + attacker.powers.get("strength", 0)
    if attacker.powers.get("weak", 0) > 0:
        dmg *= C.WEAK_DEALT_MULT
    return _floor(dmg)


def modify_damage_taken(defender: Fighter, dmg: float,
                        attacker: Fighter | None = None) -> float:
    if defender.powers.get("vulnerable", 0) > 0:
        dmg *= C.VULNERABLE_TAKEN_MULT
    # `attacker` exists for the base-game parity powers that key off the
    # DEALER rather than the target (Cruelty scales the Vulnerable multiplier
    # it deals; Colossus halves what its owner takes from a Vulnerable dealer).
    # It defaults to None so every existing two-argument call still reads the
    # same -- Klee and Furina have no dealer-keyed power.
    from tier0.engine import refpowers          # late import avoids cycle
    return _floor(refpowers.modify_damage_taken(defender, dmg, attacker))


def modify_block_gained(fighter: Fighter, amount: int) -> int:
    """Frail: the affected creature gains -25% block (StS Frail, floored).

    The single funnel every card-block site routes through so the debuff
    actually bites -- StS applies Frail to card block via
    AbstractCard.applyPowersToBlock, so passive/power block (Metallicize,
    Crystallize, Solar Isotoma) is deliberately NOT reduced here.
    """
    if amount <= 0:
        return amount
    if fighter.powers.get("frail", 0) > 0:
        return int(amount * C.FRAIL_BLOCK_MULT)   # StS floors block*0.75
    return amount


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
    for name in EXPIRING:
        fighter.powers.pop(name, None)
    # StS2 site M (AfterSideTurnEnd) for the base-game parity powers. This is
    # the correct site for BOTH sides: the player reaches it after the hand
    # flush, each enemy after its intent -- which is exactly where Mangle's
    # temporary Strength has to unwind (one enemy action, no more).
    from tier0.engine import refpowers          # late import avoids cycle
    refpowers.on_fighter_turn_end(state, fighter)


def apply_power(state: CombatState, target: Fighter, name: str, stacks: int,
                max_stacks: int | None = None,
                applier: Fighter | None = None) -> None:
    new = target.powers.get(name, 0) + stacks
    if max_stacks is not None:              # sheet v0.2 stack caps
        new = min(new, max_stacks)
    target.powers[name] = new
    state.emit("apply_power", power=name, stacks=stacks,
               target=getattr(target, "name", "player"))
    # `applier` is StS2's AfterPowerAmountChanged argument. Vicious is the only
    # power that needs it; callers that do not know it (effects._op_apply_power)
    # leave it None and refpowers recovers it from the acting side.
    from tier0.engine import refpowers          # late import avoids cycle
    refpowers.on_power_applied(state, target, name, stacks, applier)
