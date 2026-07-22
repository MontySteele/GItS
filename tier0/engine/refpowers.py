"""The real Ironclad's powers (base-game parity pass).

WHY THIS FILE EXISTS
--------------------
`ref_ironclad` in tier0 is a six-card calibration construct normalised to 3.0
on every axis. Every statline number in the project is measured against it and
nobody has ever checked that it is representative. To check, we score the REAL
87-card Ironclad on the same axes -- which means his 27 in-scope powers have to
exist in tier0.

PARITY, NOT FIDELITY. Klee is scored in a world with no relics, no potions and
no events. Ironclad is scored in that same impoverished world. Nothing here
adds content Klee lacks.

IP: this module is OUR code. The numbers (Amount / SelfDamage / upgrade deltas)
live in game_ref/ironclad.json, which is gitignored. No extracted card number
appears in this file.

WHAT A "HOOK" MEANS HERE
------------------------
StS2's CombatManager runs a fixed player-turn order. tier0 collapses several of
its sites into one. The mapping this module commits to (recon spec §0.1):

    StS2 site                       tier0 call site
    A  BeforeSideTurnStart          refpowers.side_turn_start_early
    B  block clear (ShouldClearBlock)  combat._player_turn, gated on Barricade
    C  energy reset (ModifyMaxEnergy)  combat._player_turn, + Pyre
    D  hand draw (ShouldDraw)          CombatState.draw, gated on NoDraw
    E  AfterPlayerTurnStart          refpowers.player_turn_start_late (part 1)
    F  AfterSideTurnStart            refpowers.player_turn_start_late (part 2)
    G  play phase                    the pilot loop
    I  BeforeSideTurnEndEarly        refpowers.before_side_turn_end_early
    M  AfterSideTurnEnd (player)     refpowers.on_fighter_turn_end
       AfterSideTurnEnd (enemy)      refpowers.after_enemy_side_turn_end

The single most important thing about this file is that E/F are AFTER the draw.
tier0's pre-existing `powers.on_turn_start` runs BEFORE energy and BEFORE the
draw, so anything implemented there is a POST step running at a PRE site. That
is why DemonForm, Plating, CrimsonMantle and Inferno all use the late hook.

FUNNEL GRANULARITY
------------------
The block funnel observes the total amount across one CardPlay, while
`block_gains_this_card` preserves how many BlockGained rows produced it. That
is exact for Unmovable (one multiplier decision for the current CardPlay,
every prior row consuming allowance) and Juggernaut (one trigger per row),
including EvilEye and SecondWind. The exhaust funnel is per-card and exact.

Card-caused self-damage still observes a DELTA across the CardPlay. That is
exact for Rupture's deferral, but a future card with several distinct
self-damage ops would fire Inferno only once. Such a card emits the existing
`refpower_funnel_collapse` event and must not enter the pool unreviewed.

UNIMPLEMENTED (see UNIMPLEMENTED below): Stampede and Hellraiser. Their cards
must be excluded from the pool -- they are NOT approximated.
"""

from __future__ import annotations

from typing import Optional

from tier0 import constants as C
from tier0.engine.state import Card, CombatState, Enemy, Fighter, Player

# ---------------------------------------------------------------------------
# Powers this module refuses to implement, and the cards they gate.
#
# House rule: never approximate a DSL gap silently. A caller that loads one of
# these cards gets a loud event and the loader is expected to drop the card.
# ---------------------------------------------------------------------------
UNIMPLEMENTED: dict[str, str] = {
    "stampede": (
        "StampedePower autoplays N random Attacks from hand at "
        "AfterAutoPostPlayPhaseEntered -- AFTER the pilot loop has exited. "
        "tier0 has no autoplay path, and combat._player_turn's `seen_states` "
        "degeneracy detector only samples between pilot decisions, so a "
        "Stampede + card-generation loop would run below the detector "
        "entirely. Needs auto_play_card() + a detector that extends past the "
        "pilot loop. Card: Stampede."
    ),
    "hellraiser": (
        "HellraiserPower autoplays every drawn card tagged Strike from inside "
        "AfterCardDrawnEarly, which makes CombatState.draw REENTRANT: the "
        "autoplay resolves a card that can draw more cards that autoplay in "
        "turn. tier0's draw() is a tight mutating loop with no depth guard. "
        "Card: Hellraiser."
    ),
}

# Multiplayer-only cards: excluded from the 87-card pool outright (recon BUG 2).
# TankPower is deleted from the work list with its card -- it also applies
# GuardedPower to teammates, of which single-player has none.
MULTIPLAYER_ONLY_CARDS = ("Tank", "DemonicShield")


def unpowered_damage(state: CombatState, enemy: Enemy, amount: int) -> int:
    """CreatureCmd.Damage(target, Amount, ValueProp.Unpowered).

    Deliberately NOT effects.deal_damage_to_enemy: that is the POWERED attack
    pipeline and applies the dealer's Strength, the target's Vulnerable and the
    reaction amp unconditionally. `IsPoweredAttack()` is false for every power
    in this module that deals damage (Juggernaut, Inferno, FlameBarrier), so
    routing them through it would silently scale them with Strength -- and
    Juggernaut on a DemonForm turn would be badly, invisibly wrong.

    Block still applies (Unpowered is not Unblockable). Bombs do not detonate
    and Shatter does not fire, matching a non-Attack source.
    """
    dmg = int(amount)
    if dmg <= 0:
        return 0
    blocked = min(enemy.block, dmg)
    enemy.block -= blocked
    hp_dmg = dmg - blocked
    was_alive = enemy.alive
    effective = min(hp_dmg, max(0, enemy.hp))     # overkill does not count
    enemy.hp -= hp_dmg
    state.emit("damage", target=enemy.name, amount=effective, blocked=blocked,
               base=amount, source="power")
    if was_alive and not enemy.alive:
        state.kills_this_card += 1
    return hp_dmg


def refuse(state: CombatState, power: str) -> None:
    """Log an UNIMPLEMENTED power loudly. Callers must exclude the card."""
    state.emit("UNIMPLEMENTED", power=power, reason=UNIMPLEMENTED[power])


# ---------------------------------------------------------------------------
# State binding.
#
# A seam, not a design preference: Cruelty and Vicious need the ATTACKER /
# APPLIER identity, and the call that needs it most (effects.deal_damage_to_enemy
# -> powers.modify_damage_taken) lives in effects.py, which this pass may not
# edit. Binding the active CombatState lets those two rules recover the missing
# identity from the one thing that is unambiguous: whose side is acting.
#
# tier0 is single-threaded and one fight runs at a time (combat.run_fight), so
# a module-level binding is safe. It is set with try/finally so a raising fight
# cannot leak a stale state into the next one.
# ---------------------------------------------------------------------------
ACTIVE_STATE: Optional[CombatState] = None


def bind(state: Optional[CombatState]) -> Optional[CombatState]:
    global ACTIVE_STATE
    previous, ACTIVE_STATE = ACTIVE_STATE, state
    return previous


# ---------------------------------------------------------------------------
# Funnel 1 -- block.
# ---------------------------------------------------------------------------

def gain_block(state: CombatState, fighter: Fighter, amount: int,
               card_sourced: bool = False) -> int:
    """The single chokepoint for block gains that powers can see.

    `card_sourced` mirrors StS2's `props.IsCardOrMonsterMove()`: only card
    block is eligible for Unmovable's doubling. Passive block (Plating,
    CrimsonMantle, Rage, FeelNoPain, Metallicize) is Unpowered and is not.
    """
    if amount <= 0:
        return 0
    if card_sourced:
        amount = _apply_unmovable(state, fighter, amount)
    fighter.block += amount
    state.emit("block", amount=amount)
    _after_block_gained(state, fighter, amount)
    return amount


def _apply_unmovable(state: CombatState, fighter: Fighter, amount: int) -> int:
    """UnmovablePower.ModifyBlockMultiplicative -> 2, while the number of
    OTHER card plays that already gained block this turn is below Amount.

    The source counts BlockGainedEntry ROWS, filtered by
    `e.Props.IsCardOrMonsterMove() && e.CardPlay != cardPlay`. The CardPlay
    filter self-excludes every row from the IN-FLIGHT play, so several gains
    inside the CURRENT play share the multiplier decision. A PRIOR play that
    emitted two rows consumes TWO units; block_gains_this_card preserves that
    row count. Stacks raise the per-turn allowance, not the multiplier.
    """
    n = fighter.powers.get("unmovable", 0)
    if not n or fighter is not state.player:
        return amount
    if state.block_gain_card_plays_this_turn >= n:
        return amount
    state.emit("unmovable_doubled", amount=amount)
    return amount * 2


def _after_block_gained(state: CombatState, fighter: Fighter,
                        amount: int) -> None:
    """JuggernautPower.AfterBlockGained(creature == Owner, amount > 0) ->
    damage a RANDOM enemy for Amount, ValueProp.Unpowered.

    Unpowered means IsPoweredAttack() is false, so neither the owner's Strength
    nor the target's Vulnerable applies -- see unpowered_damage. It fires on
    EVERY block gain, including Plating's, Rage's and its own; that is why
    block has to be one chokepoint rather than six patched sites.
    """
    n = fighter.powers.get("juggernaut", 0)
    if not n or fighter is not state.player:
        return
    living = state.living_enemies
    if not living:
        return
    unpowered_damage(state, state.rng.choice(living), n)


# ---------------------------------------------------------------------------
# Funnel 2 -- exhaust.
# ---------------------------------------------------------------------------

def exhaust_card(state: CombatState, card: Card,
                 caused_by_ethereal: bool = False) -> None:
    """Move a card to the exhaust pile and fire AfterCardExhausted.

    Mid-card-play (depth > 0) the hook is left to the per-card-play exhaust
    funnel in after_card_played, which sweeps everything the card added to the
    pile. Firing here too would double-pay FeelNoPain and DarkEmbrace for any
    future op that routes through this function instead of appending directly.
    """
    state.player.exhaust_pile.append(card)
    state.emit("exhaust", card=card.id)
    if state.card_play_depth:
        return
    after_card_exhausted(state, card, caused_by_ethereal)


def after_card_exhausted(state: CombatState, card: Card,
                         caused_by_ethereal: bool) -> None:
    """FeelNoPain: AfterCardExhausted -> GainBlock(Amount, Unpowered).

    DarkEmbrace: AfterCardExhausted -> Draw(Amount), EXCEPT exhausts caused by
    ethereal, which are counted and flushed at AfterSideTurnEnd. The source
    comment says outright that the deferral exists so the draw lands AFTER the
    hand flush; drawing immediately would put those cards into a hand that is
    discarded on the very next line.
    """
    p = state.player
    state.cards_exhausted_this_turn += 1
    if card.on_exhaust_energy:
        # DrumOfBattle uses PlayerCmd.GainEnergy, so ExpectAFight's
        # NoEnergyGain hook must deny this payout too. Normal on-play energy
        # is clamped later in after_card_played; Drum fires from this later
        # exhaust sweep and therefore needs the same gate here.
        if state.no_energy_gain_ceiling is not None:
            state.emit("energy_gain_denied", amount=card.on_exhaust_energy)
        else:
            p.energy += card.on_exhaust_energy
            state.emit("energy", amount=card.on_exhaust_energy,
                       source="on_exhaust")
    n = p.powers.get("feel_no_pain", 0)
    if n:
        gain_block(state, p, n)                  # Unpowered: no Unmovable
    n = p.powers.get("dark_embrace", 0)
    if not n:
        return
    if caused_by_ethereal:
        state.dark_embrace_ethereal_count += 1
    else:
        state.draw(n)
        state.emit("extra_draw", amount=n)


def result_pile(state: CombatState, card: Card) -> str:
    """CardModel.GetResultPileTypeForCardPlay(), verbatim shape:

        if (IsDupe || Type == Power)                  -> PileType.None
        if (ExhaustOnNextPlay || Keywords has Exhaust) -> PileType.Exhaust
        else                                           -> PileType.Discard

    Recon BUG 1: tier0 sent Power cards to the EXHAUST pile. With FeelNoPain or
    DarkEmbrace on the field every one of Ironclad's 11 Power cards would have
    falsely paid out block or draw. "none" means removed from combat -- which
    is where a played Power card goes, not the exhaust pile.

    Corruption is folded in here because it is a pile rule
    (ModifyCardPlayResultPileTypeAndPosition -> Exhaust for the owner's Skills),
    not a cost rule.
    """
    if card.type == "power":
        return "none"
    if card.exhaust:
        return "exhaust"
    if card.type == "skill" and state.player.powers.get("corruption", 0):
        return "exhaust"
    return "discard"


# ---------------------------------------------------------------------------
# Funnel 3 -- damage taken by the player.
# ---------------------------------------------------------------------------

def damage_player_unblockable(state: CombatState, amount: int,
                              reason: str) -> None:
    """CreatureCmd.Damage(Unblockable | Unpowered) against the owner.

    Used by CrimsonMantle and Inferno for their SelfDamage vars. Unblockable
    bypasses Block; it also bypasses Encore, following the precedent already
    set by effects._op_damage's self path ("a priced cost stays paid"). Klee
    and Furina never reach this function, so that precedent is not disturbed.
    """
    if amount <= 0:
        return
    p = state.player
    p.hp -= amount
    state.emit("self_damage", amount=amount, reason=reason)
    from tier0.engine import resources
    resources.note_player_hp_loss(state, amount)
    on_damage_received(state, p, unblocked=amount, dealer=None,
                       powered_attack=False)


def on_damage_received(state: CombatState, target: Fighter, unblocked: int,
                       dealer: Optional[Fighter],
                       powered_attack: bool) -> None:
    """AfterDamageReceived, shared by Inferno, Rupture and FlameBarrier.

    The three of them disagree about WHEN they fire, and the disagreement is
    the whole design:

      Inferno   requires CombatState.CurrentSide == Owner.Side. An enemy hit
                landing on you during the ENEMY turn does NOT trigger it. Only
                self-damage and player-turn damage do -- and Inferno's own
                turn-start SelfDamage feeds it, which is the intended engine.
      Rupture   same side check. Without it Rupture stops being a self-damage
                payoff and silently becomes a passive tank power.
      FlameBarrier has NO side check -- it exists to punish the enemy turn --
                and, unlike the other two, NO unblocked>0 requirement either:
                its source ignores the DamageResult entirely (`DamageResult _`)
                and asks only for a `dealer` and a POWERED attack. A fully
                blocked hit still gets burned.
    """
    if target is not state.player:
        return
    p = state.player

    if state.in_player_turn and unblocked > 0:
        n = p.powers.get("inferno", 0)
        if n:
            for enemy in list(state.living_enemies):
                unpowered_damage(state, enemy, n)
        n = p.powers.get("rupture", 0)
        if n:
            # RupturePower defers Strength to AfterCardPlayed when the damage
            # came from a card that is still mid-play, so a multi-hit
            # self-damage attack cannot buff its own remaining hits. tier0's
            # per-card-play funnel gives that deferral for free during a card;
            # outside a card (turn-start SelfDamage) it applies immediately.
            if state.card_play_depth:
                state.rupture_pending += n
            else:
                from tier0.engine import powers as _powers
                _powers.apply_power(state, p, "strength", n, applier=p)

    n = p.powers.get("flame_barrier", 0)
    if (n and powered_attack and isinstance(dealer, Enemy) and dealer.alive):
        unpowered_damage(state, dealer, n)


# ---------------------------------------------------------------------------
# Funnel 4 / 5 -- card plays and power application.
# ---------------------------------------------------------------------------

def free_cost(state: CombatState, card: Card) -> bool:
    """TryModifyEnergyCostInCombatLate -> 0.

    FreeAttack (Unrelenting) zeroes the owner's Attacks; Corruption zeroes the
    owner's Skills. Checked AFTER tier0's native spark discount in
    combat.card_cost, so a spark-freed attack spends the bank -- and, because
    FreeAttackPower.BeforeCardPlayed decrements on every owner Attack play
    without asking whether its own discount mattered, ALSO a FreeAttack stack.
    Pinned by test_free_attack_and_spark_are_both_consumed.
    """
    p = state.player
    if card.type == "attack" and p.powers.get("free_attack", 0):
        return True
    if card.type == "skill" and p.powers.get("corruption", 0):
        return True
    return False


def extra_replays(state: CombatState, card: Card) -> int:
    """OneTwoPunch: ModifyCardPlayCount(card) -> playCount + 1 for Attacks,
    then AfterModifyingCardPlayCount -> Decrement.

    Amount stacks therefore mean "the next Amount Attacks are each played
    TWICE", not "one Attack is played Amount+1 times". The decrement happens
    when the play count is resolved, i.e. once per card, which is why it lives
    here and not in before_card_played (that one fires per play index).
    """
    p = state.player
    if card.type == "attack" and p.powers.get("one_two_punch", 0):
        p.powers["one_two_punch"] -= 1
        state.emit("one_two_punch", card=card.id)
        return 1
    return 0


def before_card_played(state: CombatState, card: Card) -> dict:
    """Hook.BeforeCardPlayed -- fires once per PLAY INDEX, not per card.

    A OneTwoPunch-doubled attack therefore consumes two FreeAttack stacks,
    which is the real behaviour and the reason this is inside the replay loop.

    Returns the snapshot the delta funnels close over.
    """
    p = state.player
    if card.type == "attack" and p.powers.get("free_attack", 0):
        p.powers["free_attack"] -= 1
        state.emit("free_attack_spent", card=card.id)
    if state.no_energy_gain_ceiling is not None:
        # Energy already spent on cost lowers the ceiling; only GAINS are
        # denied (see after_card_played).
        state.no_energy_gain_ceiling = min(state.no_energy_gain_ceiling,
                                           p.energy)
    state.card_play_depth += 1
    return {"hp": p.hp, "block": p.block, "exhaust": len(p.exhaust_pile),
            "energy": p.energy}


def after_card_played(state: CombatState, card: Card, snap: dict) -> None:
    """Hook.AfterCardPlayed -- also per play index (Rage pays twice on a
    OneTwoPunch-doubled attack; Juggling counts it twice)."""
    p = state.player
    state.card_play_depth -= 1

    # NoEnergyGain (ExpectAFight): ModifyEnergyGain -> 0.
    # NOT a turn-start denial. The turn refill goes through ResetEnergy(), which
    # never calls PlayerCmd.GainEnergy and so never sees this hook -- the power
    # only zeroes EXPLICIT gain effects for the rest of the turn it was applied,
    # i.e. it is an anti-chaining drawback on ExpectAFight itself. Implemented
    # at the turn refill instead, the card would become a hard turn-skipper and
    # its rating would invert. The ceiling is seeded when the power lands (see
    # on_power_applied), so ExpectAFight's OWN gain still resolves.
    if state.no_energy_gain_ceiling is not None:
        if p.energy > state.no_energy_gain_ceiling:
            state.emit("energy_gain_denied",
                       amount=p.energy - state.no_energy_gain_ceiling)
            p.energy = state.no_energy_gain_ceiling
        state.no_energy_gain_ceiling = min(state.no_energy_gain_ceiling,
                                           p.energy)

    # Exhausts the card's own effects caused (effects._op_exhaust_from and
    # friends). Per-card and therefore exact.
    #
    # The sweep has to run BEFORE the block delta below -- the game resolves
    # these exhausts during card resolution, so FeelNoPain's block genuinely
    # precedes the card's own block and reordering would corrupt Unmovable's
    # allowance ordering. But FeelNoPain gains block through `gain_block`,
    # which has ALREADY funnelled it (Unmovable consulted, Juggernaut fired).
    # Leaving it inside `p.block - snap["block"]` would re-process it as card
    # block: UnmovablePower.ModifyBlockMultiplicative returns 1m when
    # `!props.IsCardOrMonsterMove()`, so ValueProp.Unpowered block is never
    # doubled; Juggernaut would pay twice for one BlockGainedEntry; and a
    # pure-exhaust skill would burn an Unmovable allowance the game never
    # counts (its filter is `e.Props.IsCardOrMonsterMove()`). Roll the swept
    # block into the baseline so only the card's OWN block reaches the delta.
    new_exhausts = p.exhaust_pile[snap["exhaust"]:]
    if new_exhausts:
        before = p.block
        for exhausted in new_exhausts:
            after_card_exhausted(state, exhausted, caused_by_ethereal=False)
        snap["block"] += p.block - before

    # Card-sourced block: Unmovable's doubling and Juggernaut's payout.
    delta = p.block - snap["block"]
    if delta > 0:
        doubled = _apply_unmovable(state, p, delta)
        if doubled != delta:
            p.block += doubled - delta
        gains = max(1, state.block_gains_this_card)
        # Unmovable excludes rows from the CURRENT CardPlay and therefore
        # applies one multiplier decision to the aggregate, but later card
        # plays count every row this card emitted. Juggernaut also fires once
        # per row. Tracking the count makes EvilEye and SecondWind exact
        # without changing the block amount pipeline.
        state.block_gain_card_plays_this_turn += gains
        for _ in range(gains):
            _after_block_gained(state, p, doubled)

    # Card-caused self damage -> Inferno / Rupture.
    lost = snap["hp"] - p.hp
    if lost > 0:
        if _counts_multiple_damage_ops(card):
            state.emit("refpower_funnel_collapse", kind="self_damage",
                       card=card.id)
        on_damage_received(state, p, unblocked=lost, dealer=None,
                           powered_attack=False)

    # Rupture's deferred strength, flushed now that the card has finished --
    # this is the point of the deferral.
    if state.rupture_pending:
        n, state.rupture_pending = state.rupture_pending, 0
        from tier0.engine import powers as _powers
        _powers.apply_power(state, p, "strength", n, applier=p)

    if card.type != "attack":
        return

    # RagePower.AfterCardPlayed(owner's Attack) -> GainBlock(Amount, Unpowered).
    n = p.powers.get("rage", 0)
    if n:
        gain_block(state, p, n)

    # JugglingPower.AfterCardPlayed(owner's Attack): count, and on EXACTLY the
    # third attack of the turn add Amount clones of THAT card to hand. The
    # source tests `== 3`, not `% 3 == 0`, so the sixth attack does nothing.
    state.attacks_played_this_turn += 1
    n = p.powers.get("juggling", 0)
    if n and state.attacks_played_this_turn == C.JUGGLING_ATTACK_TRIGGER:
        import copy as _copy
        for _ in range(n):
            # CardPileCmd routes the add through the full-hand check
            # (`isFullHandAdd` -> targetPile = CardPile.Get(PileType.Discard)),
            # so an overflowing clone is REDIRECTED to the discard pile, not
            # destroyed -- it stays in the deck and is drawable next turn.
            # Dropping it would silently cost Ironclad deferred card advantage
            # on exactly the heavy-draw turns Juggling is played for. Same
            # redirect effects._add_token already implements.
            clone = _copy.deepcopy(card)
            if len(p.hand) < C.MAX_HAND_SIZE:
                p.hand.append(clone)
                zone = "hand"
            else:
                p.discard_pile.append(clone)
                zone = "discard"
            state.emit("juggling_clone", card=clone.id, zone=zone)


def _counts_multiple_damage_ops(card: Card) -> bool:
    return sum(1 for fx in card.effects
               if fx.get("op") == "damage" and fx.get("target") == "self") > 1


def on_power_applied(state: CombatState, target: Fighter, name: str,
                     stacks: int, applier: Optional[Fighter]) -> None:
    """Hook.AfterPowerAmountChanged, called from powers.apply_power.

    APPLIER INFERENCE. `applier` is genuinely unknown at effects._op_apply_power
    (that file is owned by another agent this pass). It is recovered from the
    acting side, which is unambiguous in tier0: powers are applied by cards
    during the player turn and by intents during the enemy turn. Enemy intents
    pass their applier explicitly from combat._enemy_turn, so the inference
    only ever fires on the player-turn path.
    """
    if applier is None and state.in_player_turn:
        applier = state.player

    # TemporaryStrengthPower: apply +-Amount Strength NOW and revert the same
    # magnitude at the owner's turn end. SetupStrike is IsPositive=true on
    # self; Mangle overrides IsPositive=false on an enemy. Deliberately NOT a
    # decaying stack -- the magnitude must be restored, not decremented by 1.
    if name == "temp_strength" and stacks:
        target.powers["strength"] = target.powers.get("strength", 0) + stacks
    elif name == "temp_strength_down" and stacks:
        target.powers["strength"] = target.powers.get("strength", 0) - stacks

    # InfernoPower / CrimsonMantlePower.IncrementSelfDamage(). Both cards'
    # OnPlay is `PowerCmd.Apply<XPower>(Amount)?.IncrementSelfDamage()`, so the
    # SelfDamage DynamicVar (base 0) is bumped by ONE PER PLAY -- never by the
    # 6/8 PowerVar amount. Without this the counter stays 0 forever: the
    # turn-start self-hit is skipped by the `amount <= 0` guard, Inferno's
    # retaliation engine never starts, and CrimsonMantle reads as pure block
    # with no drawback. Half the power would be dead code in every real run.
    elif name in ("inferno", "crimson_mantle") and stacks > 0:
        key = f"{name}_self_damage"
        target.powers[key] = target.powers.get(key, 0) + 1

    # NoEnergyGain seeds its ceiling at the moment it lands, so the energy
    # ExpectAFight itself grants is kept and everything after it is denied.
    #
    # Seeded ONLY on the first application. PowerStackType.Single means a
    # re-Apply is a no-op and the live power's ModifyEnergyGain still returns
    # 0, so a second ExpectAFight gains nothing. Reseeding unconditionally
    # would launder that gain: tier0 resolves the card's `energy` op before its
    # `apply_power` op, so the banked energy would become the new ceiling and
    # after_card_played would find nothing to clamp.
    elif name == "no_energy_gain" and stacks:
        if state.no_energy_gain_ceiling is None:
            state.no_energy_gain_ceiling = state.player.energy

    # ViciousPower.AfterPowerAmountChanged(power is Vulnerable, amount > 0,
    # applier == Owner) -> Draw(Amount). Fires ONCE PER CREATURE the Vulnerable
    # lands on, so a multi-target Vulnerable card draws Amount x targets.
    if (name == "vulnerable" and stacks > 0
            and applier is state.player
            and state.player.powers.get("vicious", 0)):
        n = state.player.powers["vicious"]
        state.draw(n)
        state.emit("extra_draw", amount=n)


# ---------------------------------------------------------------------------
# Damage modifiers (called from powers.modify_damage_taken).
# ---------------------------------------------------------------------------

def modify_damage_taken(defender: Fighter, dmg: float,
                        attacker: Optional[Fighter]) -> float:
    """Colossus and Cruelty. Both key off the DEALER, which is why
    powers.modify_damage_taken grew an `attacker` argument.

    When `attacker` is None the dealer is recovered from ACTIVE_STATE: the only
    unattributed call site is effects.deal_damage_to_enemy, where the dealer is
    always the player (enemies deal damage through combat._enemy_turn, which
    passes itself). Recovering it is what makes Cruelty reachable at all.
    """
    state = ACTIVE_STATE
    if attacker is None and state is not None and defender is not state.player:
        attacker = state.player
    if attacker is None:
        return dmg

    # CrueltyPower is read BY VulnerablePower.ModifyDamageMultiplicative, which
    # returns `amount + Amount/100` -- i.e. Cruelty adds PERCENTAGE POINTS to
    # the Vulnerable multiplier the owner's attacks see. It does nothing
    # against a non-Vulnerable target, and nothing on unpowered damage.
    cruelty = attacker.powers.get("cruelty", 0)
    if cruelty and defender.powers.get("vulnerable", 0) > 0:
        # powers.modify_damage_taken has already applied the base multiplier;
        # fold in only the delta so the two do not multiply twice.
        dmg *= (C.VULNERABLE_TAKEN_MULT + cruelty / 100.0) \
            / C.VULNERABLE_TAKEN_MULT

    # ColossusPower.ModifyDamageMultiplicative -> 0.5 when the target is the
    # owner, the hit is a powered attack, AND THE DEALER HAS VULNERABLE. The
    # Colossus card does NOT apply Vulnerable -- its decompiled OnPlay only
    # gains Block and applies the power; VulnerablePower appears solely as a
    # hover tip. So the halving fires only against a dealer that got Vulnerable
    # from ELSEWHERE (Bash, Cruelty targets, etc.), never self-enabling.
    if (defender.powers.get("colossus", 0)
            and attacker.powers.get("vulnerable", 0) > 0):
        dmg *= C.COLOSSUS_TAKEN_MULT

    return dmg


# ---------------------------------------------------------------------------
# Turn hooks.
# ---------------------------------------------------------------------------

def side_turn_start_early(state: CombatState) -> None:
    """StS2 site A -- Hook.BeforeSideTurnStart. BEFORE the block clear and
    BEFORE the turn-start draw.

    AggressionPower: take Amount random Attacks from the DISCARD pile, move
    them to hand, and upgrade each. Running this after the draw instead would
    over-fill the hand relative to the real game and change MAX_HAND_SIZE
    pressure, which is why it needs its own site rather than sharing the
    existing on_turn_start.
    """
    p = state.player
    n = p.powers.get("aggression", 0)
    if not n:
        return
    pool = [c for c in p.discard_pile if c.type == "attack" and not c.kit_card]
    if not pool:
        return
    state.rng.shuffle(pool)
    for card in pool[:n]:
        if len(p.hand) >= C.MAX_HAND_SIZE:
            break
        p.discard_pile.remove(card)
        p.hand.append(_upgraded(state, card))
        state.emit("aggression_recall", card=card.id)


def _upgraded(state: CombatState, card: Card) -> Card:
    """`loader.get_card(id + upgrades.SUFFIX)`, the repo's one upgrade path.

    A card with no `+` entry is NOT quietly handed over un-upgraded: the move
    half is implemented, the upgrade half is logged loudly so the sheet gap is
    visible in the event stream rather than biasing Aggression's rating down.
    """
    from tier0.content import loader, upgrades
    try:
        return loader.get_card(card.id + upgrades.SUFFIX)
    except Exception:
        state.emit("UNIMPLEMENTED", power="aggression", card=card.id,
                   reason="no upgrade entry for this card id; moved unupgraded")
        return card


def player_turn_start_late(state: CombatState) -> None:
    """StS2 sites E then F -- AfterPlayerTurnStart, then AfterSideTurnStart.

    Both are AFTER the hand draw. tier0's pre-existing powers.on_turn_start is
    before energy and before the draw, so none of these may live there.
    """
    p = state.player

    # --- site E: AfterPlayerTurnStart ---

    # CrimsonMantle: take SelfDamage (Unblockable|Unpowered) and THEN gain
    # Amount block. SelfDamage starts at 0 and the card calls
    # IncrementSelfDamage() on each play, so it equals the number of copies
    # played -- tracked as its own counter alongside the stack.
    n = p.powers.get("crimson_mantle", 0)
    if n:
        damage_player_unblockable(
            state, p.powers.get("crimson_mantle_self_damage", 0),
            reason="crimson_mantle")
        if p.alive:
            gain_block(state, p, n)

    # Inferno (a): the same IncrementSelfDamage counter. This is what feeds
    # Inferno (b) in on_damage_received -- (a) and (b) are one engine.
    if p.powers.get("inferno", 0):
        damage_player_unblockable(
            state, p.powers.get("inferno_self_damage", 0), reason="inferno")

    if not p.alive or state.over:
        return

    # --- site F: AfterSideTurnStart ---

    # DemonForm: Apply<StrengthPower>(Owner, Amount) every turn, permanently.
    n = p.powers.get("demon_form", 0)
    if n:
        from tier0.engine import powers as _powers
        _powers.apply_power(state, p, "strength", n, applier=p)

    # Plating: Decrement -- but SKIPPED on the player's first turn
    # (`PlayerCombatState.TurnNumber != 1`). Missing that exemption is an
    # off-by-one on every stack for the rest of the fight.
    if p.powers.get("plating", 0) and state.turn != 1:
        p.powers["plating"] -= 1


def before_side_turn_end_early(state: CombatState) -> None:
    """StS2 site I -- Hook.BeforeSideTurnEndEarly. The source comment on
    PlatingPower says outright: "We do this in early so that it triggers
    before end-of-turn damage effects."

    Plating gains Amount block HERE, at the player's turn END. tier0 clears
    player block at the start of the NEXT player turn, so the block correctly
    protects only the intervening enemy turn.

    Sequence this pins: played turn 3 with N stacks -> end of turn 3 gain N ->
    start of turn 4 decrement to N-1 -> end of turn 4 gain N-1.
    """
    p = state.player
    n = p.powers.get("plating", 0)
    if n:
        gain_block(state, p, n)                  # Unpowered: no Unmovable


def on_fighter_turn_end(state: CombatState, fighter: Fighter) -> None:
    """StS2 site M -- AfterSideTurnEnd, for whichever side just ended.

    Called from powers.on_turn_end, which runs for the player after the hand
    flush and for each enemy after its intent.
    """
    # TemporaryStrengthPower reverts at its OWNER's side turn end. Mangle sits
    # on an ENEMY and is applied during the player's turn, so it debuffs
    # exactly one enemy action; SetupStrike sits on the player and reverts at
    # the player's own turn end.
    n = fighter.powers.pop("temp_strength", 0)
    if n:
        fighter.powers["strength"] = fighter.powers.get("strength", 0) - n
    n = fighter.powers.pop("temp_strength_down", 0)
    if n:
        fighter.powers["strength"] = fighter.powers.get("strength", 0) + n

    if fighter is not state.player:
        return

    # Removed WHOLE at the owner's turn end (PowerCmd.Remove, not Decrement).
    for name in ("rage", "no_draw", "no_energy_gain", "one_two_punch"):
        fighter.powers.pop(name, None)
    state.no_energy_gain_ceiling = None

    # DarkEmbrace's deferred ethereal draws. This site is already AFTER the
    # hand flush in combat._player_turn, which is precisely why the source
    # defers them here instead of drawing at exhaust time.
    if state.dark_embrace_ethereal_count:
        count = state.dark_embrace_ethereal_count
        state.dark_embrace_ethereal_count = 0
        n = fighter.powers.get("dark_embrace", 0)
        if n:
            state.draw(n * count)
            state.emit("extra_draw", amount=n * count)


def after_enemy_side_turn_end(state: CombatState) -> None:
    """AfterSideTurnEnd(side == Enemy), the once-per-round enemy-side tick.

    FlameBarrier is removed HERE (`Owner.Side != side`): play it on your turn,
    it covers the following enemy turn, then it vanishes. Removing it at the
    PLAYER's turn end instead makes the card do nothing at all.

    Colossus decrements here too (`if (side == CombatSide.Enemy)`), so its
    stacks read as "turns of protection remaining".
    """
    p = state.player
    p.powers.pop("flame_barrier", None)
    if p.powers.get("colossus", 0) > 0:
        p.powers["colossus"] -= 1


def reset_turn_counters(state: CombatState) -> None:
    """Per-player-turn windows owned by this module."""
    state.attacks_played_this_turn = 0            # Juggling
    state.block_gain_card_plays_this_turn = 0     # Unmovable's allowance
    state.cards_exhausted_this_turn = 0           # EvilEye / ForgottenRitual
    state.hp_lost_this_turn = 0                   # Spite
    state.rupture_pending = 0


def energy_for_turn(state: CombatState) -> int:
    """PyrePower.ModifyMaxEnergy(player, amount) => amount + Amount.

    This is a reset to MAX, not an accumulating gain -- it does not compound
    across turns, and it is deliberately NOT the same site as NoEnergyGain.
    """
    return C.BASE_ENERGY_PER_TURN + state.player.powers.get("pyre", 0)


def should_clear_block(player: Player) -> bool:
    """BarricadePower.ShouldClearBlock(creature) => Owner != creature."""
    return not player.powers.get("barricade", 0)


def should_draw(player: Player, from_hand_draw: bool) -> bool:
    """NoDrawPower.ShouldDraw(player, fromHandDraw) => fromHandDraw.

    The turn-start hand draw is `fromHandDraw: true` and therefore still
    happens; every other draw is denied. In practice the power is removed at
    the owner's turn end so the turn-start case never arises, but this is the
    actual rule and it is cheap to state correctly.
    """
    if from_hand_draw:
        return True
    return not player.powers.get("no_draw", 0)
