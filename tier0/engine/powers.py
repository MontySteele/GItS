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

# ceremonial_garment (Kokomi kit, kickoff §2.2 Shape B): stacks = turns
# remaining in the state; the same tick-down grammar as the debuffs. No
# other character ever carries it, so the addition is a dead branch there.
DECAYING = ("weak", "vulnerable", "frail",
            "ceremonial_garment")            # tick down at owner's turn end
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
    # Klee survival sprint Window A: the first attack action an enemy makes
    # while Bombed is suppressed at the Weak rate. Combat marks the per-enemy
    # latch after the whole action, so every hit of a multi-hit intent shares
    # the reduction. Real Weak and Bomb suppression use one branch.
    bomb_suppressed = (
        bool(getattr(attacker, "bombs", ()))
        and not getattr(attacker, "bomb_suppression_spent", True)
    )
    if attacker.powers.get("weak", 0) > 0 or bomb_suppressed:
        dmg *= C.WEAK_DEALT_MULT
    return _floor(dmg)


def modify_damage_taken(defender: Fighter, dmg: float,
                        attacker: Fighter | None = None,
                        from_card: bool = False) -> float:
    if defender.powers.get("vulnerable", 0) > 0:
        dmg *= C.VULNERABLE_TAKEN_MULT
    # `attacker` exists for the base-game parity powers that key off the
    # DEALER rather than the target (Cruelty scales the Vulnerable multiplier
    # it deals; Colossus halves what its owner takes from a Vulnerable dealer).
    # It defaults to None so every existing two-argument call still reads the
    # same -- Klee and Furina have no dealer-keyed power.
    # `from_card` is the `cardSource != null` guard several base-game
    # multipliers carry: DoubleDamage doubles a card's Attack and does NOT
    # double a bomb, a poison tick or a summon's pulse.
    from tier0.engine import refpowers          # late import avoids cycle
    return _floor(refpowers.modify_damage_taken(defender, dmg, attacker,
                                                from_card=from_card))


def modify_block_gained(fighter: Fighter, amount: int) -> int:
    """Dexterity (additive), then Frail (-25%, floored).

    The single funnel every card-block site routes through so the debuff
    actually bites -- StS applies Frail to card block via
    AbstractCard.applyPowersToBlock, so passive/power block (Metallicize,
    Crystallize, Solar Isotoma) is deliberately NOT reduced here.

    DEXTERITY LIVES HERE, NOT IN refpowers.gain_block, and the sprint plan
    that said otherwise was wrong on the source. DexterityPower overrides
    `ModifyBlockAdditive` guarded by `props.IsPoweredCardOrMonsterMoveBlock()`
    -- the SAME predicate FrailPower's multiplicative hook uses. tier0 splits
    block along exactly that line already: card block reaches this funnel,
    while refpowers.gain_block carries the Unpowered power-block that Frail
    is (correctly) not allowed to touch. Hanging Dexterity off gain_block
    would have applied it to the block it must NOT scale and missed every
    block it must.

    ORDER IS THE WHOLE INTERACTION: additive before multiplicative, because
    the engine runs ModifyBlockAdditive first -- (base + dex) * 0.75, not
    base * 0.75 + dex. On a 5-block card with 3 Dexterity and Frail that is
    6 versus 6 (they agree), and on 11 block it is 10 versus 11 (they do
    not). Dexterity is AllowNegative, so the sum is floored at 0 before
    Frail rather than letting a negative stack invert the multiplier.
    """
    if amount <= 0:
        return amount
    dex = fighter.powers.get("dexterity", 0)
    if dex:
        amount = max(0, amount + dex)
    # ShadowmeldPower.ModifyBlockMultiplicative -> 2^Amount, and unlike Frail
    # it carries NO IsPoweredCardOrMonsterMoveBlock guard: it doubles every
    # kind of block its owner gains. tier0's two block paths are disjoint
    # (card block reaches here, power block reaches refpowers.gain_block), so
    # the doubling is applied in both and lands exactly once either way.
    meld = fighter.powers.get("shadowmeld", 0)
    if meld:
        amount *= 2 ** meld
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
        # Overkill clamped OUT of the emitted accounting, per the EPOCH 1
        # reactions._splash fix: HP still takes the full hit, but a 5-tick into
        # a 2 HP add is 2 points of damage dealt, not 5. Nothing read dot_tick
        # before this instrument, so `effective` is the only figure the share
        # calculation may use.
        effective = min(hp_loss, max(0, fighter.hp))
        fighter.hp -= hp_loss
        # `to_player` is explicit rather than inferred from `target`: an enemy
        # may legitimately be named "player" in a fixture, and the reaction
        # share-of-damage instrument routes on this flag (electro-charged is
        # the only thing in the sim that puts `dot` on an enemy, so an
        # enemy-side tick is reaction-attributable damage by construction).
        state.emit("dot_tick", amount=dot, effective=effective,
                   target=getattr(fighter, "name", "player"),
                   to_player=fighter is state.player)
        if hp_loss and fighter is state.player:
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
    # Flawless Strategy (Kokomi kickoff §1 law 3 / §2.5): she CANNOT gain
    # Strength — any positive Strength she would gain becomes Charge
    # instead, at this one chokepoint (cards, companions, intents, potions
    # all land here). Negative strength (Mangle-class) is not a gain and
    # still applies; enemies and every other character take the normal
    # path. The conversion is the balance guardrail on an uncapped meter:
    # no Strength-stacking on a Charge finisher, ever.
    if (name == "strength" and stacks > 0 and target is state.player
            and "tamakushi_casket" in state.player.relic_hooks):
        from tier0.engine import resources      # late import (module graph)
        resources.gain_charge(state, stacks, "flawless_strategy")
        state.emit("strength_converted", stacks=stacks)
        return
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
