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

CONFIRMED BY DECOMPILE (EB-19/M7, 2026-08-07): CombatManager awaits the
per-player SetupPlayerTurn -- energy reset, hand draw, then E -- before
broadcasting F. This table is the ground truth; the AuraPower.cs comment that
contradicted it lost and was corrected. The resolved order and its citations
are recorded in tier0/tests/test_reaction_phase_parity.py, as
TURN_START_BROADCAST_ORDER.

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
from tier0.engine.state import (SLY_AUTOPLAY_OP, Card, CombatState, Enemy,
                                Fighter, Player, grant_sly_autoplay,
                                remove_instance, sly_autoplays_permanently,
                                sly_granted_this_turn)

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
    dmg = int(_intangible_cap(enemy, int(amount)))    # R128: cap is per hit
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


def unblockable_unpowered_damage(state: CombatState, enemy: Enemy,
                                 amount: int) -> int:
    """CreatureCmd.Damage(target, N, Unblockable | Unpowered).

    Strangle's shape: block does not stop it and no dealer stat scales it.
    Split from unpowered_damage rather than parameterised so the two call
    sites read as the two different ValueProp combinations they are.
    """
    dmg = int(_intangible_cap(enemy, int(amount)))    # R128: unblockable is
    if dmg <= 0:                                      # not uncappable
        return 0
    was_alive = enemy.alive
    effective = min(dmg, max(0, enemy.hp))
    enemy.hp -= dmg
    state.emit("damage", target=enemy.name, amount=effective, blocked=0,
               base=amount, source="power")
    if was_alive and not enemy.alive:
        state.kills_this_card += 1
    return dmg


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
    # Shadowmeld doubles EVERY block its owner gains, card or power (no
    # IsPoweredCardOrMonsterMoveBlock guard on its multiplicative hook). The
    # card-block half of the same rule lives in powers.modify_block_gained;
    # the two funnels are disjoint, so this is applied once per gain.
    meld = fighter.powers.get("shadowmeld", 0)
    if meld:
        amount *= 2 ** meld
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
    # Kokomi (kickoff v1 §2.1/§2.5): the Tamakushi Casket's universal
    # accrual law, at the ONE exhaust funnel — played-exhausts, mid-card
    # exhausts (swept per play), ethereal, the autoplay sweep, and the
    # prevention ward's procs all pass through here, so "whenever one of
    # your cards is Exhausted" is structural, not per-site discipline.
    # Statuses/curses count too (accepted quirk, §2.1). The exhaust event
    # is also her burst-particle economy (KOKOMI_BURST_PER_EXHAUST).
    # Dead branch for every player without the relic hook.
    if "tamakushi_casket" in p.relic_hooks:
        from tier0.engine import resources    # late import (module graph)
        from tier0.engine import relics       # late import (relics -> here)
        # C5: a MUSTERED recruit's rotation is reported separately from every
        # other exhaust. P8 is a claim specifically about conscript income
        # ("mustered-companion exhausts, top-two in commander decks"), and a
        # single "exhaust" bucket cannot answer it -- her whole pool exhausts,
        # so the bucket would be top-one for every plan and confirm nothing.
        # `Card.conscripted` is the stamp the conscript op already sets.
        kind = "exhaust_muster" if getattr(card, "conscripted", False) \
            else "exhaust"
        # Touch of Orobas -> Pearl of Insight (Kokomi's upgraded starter)
        # REPLACES both rates rather than adding to them, so the rates are
        # asked for here instead of granted from the constants directly. The
        # base constants stay the argument, not the answer: a run without the
        # upgrade gets exactly the pre-Orobas numbers back.
        charge, burst = relics.exhaust_accrual(
            p, C.CHARGE_PER_EXHAUST, C.KOKOMI_BURST_PER_EXHAUST)
        resources.gain_charge(state, charge, kind)
        if p.burst_max:
            resources.gain_burst(state, burst, kind)
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
    # damage_per_exhaust (EB-82). Sits at the same funnel as the Casket
    # accrual and for the same reason, but outside its relic gate: the two
    # relics are unrelated and either may be held without the other. Opens
    # on `relic_effects` being empty, so the battery never reaches it. The
    # hook shipped as unused machinery (2026-08-12) and was ARMED by the
    # Grave of the Forgotten conversion (EB-82): `forgotten_soul` is its one
    # carrier, and as an event relic it has exactly one source.
    if p.relic_effects:
        from tier0.engine import relics           # late import (relics -> here)
        relics.on_card_exhausted(state)
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

    DOCUMENTED BEHAVIOUR, RULED 2026-08-06 (R114, FLAG-4 leg (c)).
    A played Power card is removed from combat, so a deck made ENTIRELY of
    Power cards erases itself: the draw pile empties, the discard pile never
    refills it, and the fight runs out its turn limit with an empty hand
    (S13 line `stall_softlock_5`, exploit ledger X14(c) — retired from HEAD;
    `git show pre-simplification-2026-08-06:review/redteam/exploit-ledger.md`).

    That is INTENDED and there is deliberately NO GUARD. Verbatim: "You deck
    out... don't do that." -- the StS precedent, where decking yourself out is
    a thing the player does to themselves and the engine is not obliged to
    prevent it. Recorded here so the next reader of this function files it as
    known rather than as a bug; leg (c) is closed and off the queue.
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
    # Unblockable is not uncappable: IntangiblePower.ModifyHpLostAfterOsty
    # clamps ALL HP loss to 1, poison included -- that clamp is most of what
    # Wraith Form promises, so this path may not skip it.
    amount = int(_intangible_cap(p, amount))
    p.hp -= amount
    state.emit("self_damage", amount=amount, reason=reason)
    from tier0.engine import resources
    resources.note_player_hp_loss(state, amount)
    on_damage_received(state, p, unblocked=amount, dealer=None,
                       powered_attack=False)


def poison_tick(state: CombatState, fighter: Fighter) -> None:
    """PoisonPower.AfterSideTurnStart, verified against the decompiled power.

    The behaviour, from the source rather than from memory or the wiki:

      * `CreatureCmd.Damage(Owner, Amount, Unblockable | Unpowered)` -- the
        amount is the CURRENT stack, it bypasses Block entirely, and it is
        Unpowered, so neither the poisoner's Strength nor the victim's
        Vulnerable scales it.
      * then `PowerCmd.Decrement(this)` -- ONE stack, and ONLY `if
        (base.Owner.IsAlive)`. A poison that kills does not decrement, which
        matters for nothing today and is free to keep exact.
      * `TriggerCount = Math.Min(Amount, 1 + sum of opponents' Accelerant)`.
        Accelerant is not implemented (its card stays excluded), so the loop
        runs exactly once while Amount >= 1. The min() is transcribed anyway,
        because the day Accelerant lands this function must already be the
        thing it modifies, not a thing that has to be rediscovered.
      * StackType.Counter -- applications add, and `apply_power` already
        does that.

    WHY THIS IS NOT `dot`. tier0's generic `dot` (reactions.py,
    Electro-Charged) ticks in `powers.on_turn_start`, which is StS2 site A:
    BEFORE the energy reset and BEFORE the draw. Real poison fires at site F,
    AFTER the draw. Retiming `dot` to match would have moved a mechanic Klee
    and Kokomi are already balanced around -- their numbers are load-bearing
    and the poison parity work has no claim on them. So the two coexist:
    same shape, different clocks, and neither pretends to be the other.
    """
    amount = fighter.powers.get("poison", 0)
    if amount <= 0:
        return
    # "sum of the OPPONENTS' Accelerant" -- the poisoner's stat, not the
    # victim's. For a poisoned enemy that is the player; for a poisoned
    # player it is every living enemy. Implemented 2026-07-27; this function
    # was already written around it, which is why landing the power changed
    # one line and no logic.
    if fighter is state.player:
        accelerant = sum(e.powers.get("accelerant", 0)
                         for e in state.living_enemies)
    else:
        accelerant = state.player.powers.get("accelerant", 0)
    for _ in range(min(amount, 1 + accelerant)):
        amount = fighter.powers.get("poison", 0)
        if amount <= 0:
            return
        if fighter is state.player:
            # Unblockable, and the self-damage path already bypasses Encore
            # ("a priced cost stays paid"); poison is not a priced cost, but
            # Encore is Furina's and no Furina card applies poison, so the
            # branch is unreachable rather than decided here.
            damage_player_unblockable(state, amount, reason="poison")
        else:
            # NOT `unpowered_damage`: that one lets Block absorb ("Unpowered
            # is not Unblockable") and poison is BOTH. `kills_this_card` is
            # deliberately not touched either -- it feeds the `killed_target`
            # predicate, and a turn-start tick has no card that killed
            # anything. It is reset at every card resolution, so incrementing
            # it here would be harmless today and wrong the moment that
            # ordering changes.
            dealt = int(_intangible_cap(fighter, amount))
            effective = min(dealt, max(0, fighter.hp))
            fighter.hp -= dealt
            state.emit("damage", target=fighter.name, amount=effective,
                       blocked=0, base=amount, source="poison")
        state.emit("poison_tick", amount=amount,
                   target=getattr(fighter, "name", "player"))
        if fighter.alive:                # PowerCmd.Decrement, alive-gated
            fighter.powers["poison"] = fighter.powers.get("poison", 0) - 1


def enemy_side_turn_start(state: CombatState, enemy: Enemy) -> None:
    """StS2 site F for the ENEMY side (AfterSideTurnStart).

    The player's site F is `player_turn_start_late`, which is separated from
    site A by the energy reset and the hand draw. An enemy does neither, so
    for enemies the two sites are adjacent -- but they are still two sites,
    and poison must land on the later one for the same reason it does for
    the player: `dot` owns the early one and is not being retimed.
    """
    poison_tick(state, enemy)


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

    # ThornsPower has the same shape as FlameBarrier and a different lifetime:
    # BeforeDamageReceived, no side check, no `unblocked > 0` requirement (it
    # never looks at the DamageResult), and it does NOT expire at the enemy
    # turn end. A fully blocked hit is still thorned.
    #
    # tier0 fires it AFTER the hit rather than before. The damage numbers are
    # identical either way -- the incoming amount is already computed -- and
    # the only observable difference is the order in which Thorns and
    # FlameBarrier reach an enemy they both finish off. Recorded, not hidden.
    n = p.powers.get("thorns", 0)
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
    # FreeSkillPower (Pounce) is Corruption on a counter: the owner's next
    # Amount Skills cost 0. It decrements in before_card_played, per play
    # index, exactly like FreeAttack.
    if card.type == "skill" and p.powers.get("free_skill", 0):
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
    # BurstPower is the same shape for SKILLS, and decrements at the same
    # site (AfterModifyingCardPlayCount). Stacks are "the next N Skills are
    # each played twice", not "one Skill N+1 times".
    if card.type == "skill" and p.powers.get("burst", 0):
        p.powers["burst"] -= 1
        state.emit("burst_replay", card=card.id)
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
    # FreeSkillPower decrements per owner Skill played from hand/play,
    # whether or not its discount actually mattered -- the same
    # "decrement on the play, not on the saving" rule FreeAttack has.
    if card.type == "skill" and p.powers.get("free_skill", 0):
        p.powers["free_skill"] -= 1
        state.emit("free_skill_spent", card=card.id)
    state.card_play_depth += 1
    # Afterimage / SerpentForm / Strangle all keep a
    # Dictionary<CardModel,int> filled at BeforeCardPlayed and drained at
    # AfterCardPlayed. The indirection is not decoration: it is what stops a
    # card that GRANTS one of these powers from paying itself on the very
    # play that granted it. Snapshotting the amounts here reproduces that.
    return {"hp": p.hp, "block": p.block, "exhaust": len(p.exhaust_pile),
            "energy": p.energy,
            "afterimage": p.powers.get("afterimage", 0),
            "serpent_form": p.powers.get("serpent_form", 0),
            "strangle": [(e, e.powers.get("strangle", 0))
                         for e in state.living_enemies
                         if e.powers.get("strangle", 0)]}


def after_card_played(state: CombatState, card: Card, snap: dict) -> None:
    """Hook.AfterCardPlayed -- also per play index (Rage pays twice on a
    OneTwoPunch-doubled attack; Juggling counts it twice)."""
    p = state.player
    state.card_play_depth -= 1

    # CardPlaysFinished, tallied per tag. Counted here rather than at play
    # time because the base game's readers ask what has FINISHED this turn:
    # the card doing the asking must not count itself.
    for tag in card.tags:
        state.tag_plays_this_turn[tag] = state.tag_plays_this_turn.get(tag, 0) + 1
    # The same tally by TYPE. Pinpoint discounts itself by one per Skill
    # played this turn, and counts them here for the same reason: it is
    # CardPlaysFinished the card reads, so the Skill doing the asking is not
    # in the count until it is done.
    if card.type == "skill":
        state.skills_played_this_turn += 1

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

    # --- the Silent's per-card-play powers, all reading the BeforeCardPlayed
    # snapshot rather than the live stack (see before_card_played).
    n = snap.get("afterimage", 0)
    if n:
        gain_block(state, p, n)                  # Unpowered: no Unmovable
    n = snap.get("serpent_form", 0)
    if n:
        living = state.living_enemies
        if living:
            unpowered_damage(state, state.rng.choice(living), n)
    for enemy, amount in snap.get("strangle", ()):
        if enemy.alive:
            unblockable_unpowered_damage(state, enemy, amount)

    # MasterPlannerPower.AfterCardPlayed(owner's Skill) -> ApplyKeyword(Sly).
    # It marks THE CARD OBJECT, so the skill keeps Sly for the rest of the
    # fight and auto-plays every later time an effect discards it. Single
    # stack type: the power is a switch, not a counter.
    #
    # EB-71 (R174): the mark speaks the unified grammar -- an `sly_autoplay`
    # rider with NO `until`, which is what "for the rest of the fight" means
    # once the turn sweep below drops only the turn-scoped ones. A card
    # already PERMANENTLY auto-playing is left alone and emits nothing,
    # exactly as the boolean did -- and a Skill carrying only Hand Trick's
    # one-turn grant is still upgraded to permanent here, as it was.
    if card.type == "skill" and p.powers.get("master_planner", 0):
        if not sly_autoplays_permanently(card):
            grant_sly_autoplay(card)
            state.emit("master_planner", card=card.id)

    # EVERYTHING BELOW IS ATTACK-ONLY (Rage, Juggling). The Silent's four
    # per-play powers are above this line because they fire on every card
    # type -- Afterimage on a Skill is most of what the card is for.
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
    # Quick Change (Curtain Call B, R85): the FIRST Attack each turn draws.
    # Same first-play-window grammar as spotlight_draw; counted per play
    # index like Juggling below, so a Study-Buddy-doubled attack is two
    # plays and only the first of the turn pays.
    n = p.powers.get("first_attack_draw", 0)
    if n and state.attacks_played_this_turn == 1:
        state.draw(n)
        state.emit("extra_draw", amount=n)
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


# ---------------------------------------------------------------------------
# The SILENT's powers (second base-game parity pass, 2026-07-27).
#
# Same contract as everything above: read off the decompiled PowerModel, never
# from memory, and a power that tier0 cannot host stays off the dial with its
# card excluded. Nothing here is Silent-SPECIFIC machinery -- they are ordinary
# parity powers that happen to be hers, and every one is a dead branch for the
# roster because no committed card applies them.
#
# TWO OF HER POWERS ARE CO-OP ONLY and are recorded in MULTIPLAYER_ONLY_POWERS
# rather than implemented, because in a single-player fight they can never
# fire at all: implementing them would produce a card that reads as a buff and
# measurably does nothing.
# ---------------------------------------------------------------------------
MULTIPLAYER_ONLY_POWERS: dict[str, str] = {
    "sneaky": (
        "it pays out only when an ALLY plays an Attack, and single-player "
        "has no allies (SneakyPower.AfterCardPlayed requires the card's "
        "owner to be someone other than the power's owner; enemies play no "
        "cards at all). Card: Sneaky."
    ),
    "flanking": (
        "it multiplies damage only from a dealer OTHER than the applier, "
        "and in single-player the applier is the only dealer "
        "(FlankingPower.ModifyDamageMultiplicative returns 1 when dealer == "
        "Applier). Card: Flanking."
    ),
}


def hand_draw_bonus(player: Player) -> int:
    """Hook.ModifyHandDraw, the turn-start hand-size modifiers.

    ToolsOfTheTrade adds Amount unconditionally (and then makes you discard
    Amount at site E -- the card is a filter, not card advantage).
    DrawCardsNextTurn adds Amount only when `AmountOnTurnStart != 0`; since it
    is applied during the play phase, which is AFTER this draw, the guard is
    satisfied for free by tier0's turn order and the power is removed at
    site F below.
    """
    return (player.powers.get("tools_of_the_trade", 0)
            + player.powers.get("draw_cards_next_turn", 0))


def before_hand_draw(state: CombatState) -> None:
    """Hook.BeforeHandDraw -- runs before the turn-start hand draw, so the
    cards it makes are in hand BEFORE the draw counts against the hand cap.

    InfiniteBladesPower creates Amount of the owner's token here. The token's
    id is not in this file: it arrives as a `payload` on the row that applied
    the power (see effects._op_apply_power), because a base-game card id is
    decompiled game data and this module is committed.
    """
    p = state.player
    from tier0.content import loader                # late import avoids cycle
    from tier0.engine.effects import _add_token

    n = p.powers.get("infinite_blades", 0)
    if n:
        token = p.power_payloads.get("infinite_blades")
        if not token:
            state.emit("UNIMPLEMENTED", power="infinite_blades",
                       reason="no payload: the row that applied it named "
                              "no card")
        else:
            for _ in range(n):
                _add_token(state, loader.get_card(token), "hand")

    # NightmarePower, the same hook: Amount COPIES of the card chosen when it
    # was played, then PowerCmd.Remove(this) -- one payout, not a standing
    # buff. The stacks are the copy count, and the power removes itself
    # whether or not the copies fit in hand.
    n = p.powers.get("nightmare", 0)
    if n:
        remembered = p.power_payloads.pop("nightmare", None)
        p.powers.pop("nightmare", None)
        if not remembered:
            state.emit("UNIMPLEMENTED", power="nightmare",
                       reason="no remembered card: nothing was in hand to "
                              "choose when it resolved")
        else:
            for _ in range(n):
                _add_token(state, loader.get_card(remembered), "hand")


def after_card_drawn(state: CombatState, card: Card,
                     from_hand_draw: bool) -> None:
    """Hook.AfterCardDrawn -- per CARD, not per draw effect.

    CorrosiveWave poisons every enemy on ANY draw (it is removed at the
    owner's turn end, so it is a one-turn burst). Speedster hits every enemy
    on any draw that is NOT the turn-start hand draw and only during its
    owner's turn -- the two conditions are what stop it paying out on the
    opening hand and on enemy-turn draws.
    """
    p = state.player
    n = p.powers.get("corrosive_wave", 0)
    if n:
        from tier0.engine import powers as _powers
        for enemy in list(state.living_enemies):
            _powers.apply_power(state, enemy, "poison", n, applier=p)
    n = p.powers.get("speedster", 0)
    if n and not from_hand_draw and state.in_player_turn:
        for enemy in list(state.living_enemies):
            unpowered_damage(state, enemy, n)
    randomise_cost_on_draw(state, card)


def randomise_cost_on_draw(state: CombatState, card: Card) -> None:
    """The per-INSTANCE on-draw hook (EB-83; the base game's Slither).

    Slither is `AfterCardDrawn` on the ENCHANTMENT, gated on the drawn card
    being its own and on that card having landed in hand, and it writes
    `EnergyCost.SetThisCombat(Rng.CombatEnergyCosts.NextInt(4))`. tier0 has
    no per-card callback registry and is not growing one, so the rider is a
    field on the instance and this is the site that reads it -- the same
    shape `status_draw_damage` already takes at the neighbouring line.

    UNUSED MACHINERY as landed: `on_draw_randomise_cost` is None on every
    card any sheet can produce, so no roll is taken and no randomness is
    consumed. `tier0.content.enchantments.CATALOG` deliberately still does
    NOT hold `slither` -- the event that would grant it (Wood Carvings) is
    blocked on a [USER] call about two base-game colorless cards (QUEUE
    `M23`), and an enchantment nobody grants is a name with no caller.

    The hand check is the game's and it is load-bearing: a draw that
    overflows `MAX_HAND_SIZE` never reaches here, but a card the caller
    routes elsewhere would, and re-rolling a cost for a card that is not in
    hand is not what the enchantment says.
    """
    n = card.on_draw_randomise_cost
    if not n or n <= 0:
        return
    # IDENTITY, not equality. `Card` is a plain dataclass, so `in` would
    # compare field by field and two copies of the same card in the deck are
    # equal -- the drawn instance would be indistinguishable from its twin
    # sitting in hand. This machinery is per-INSTANCE by construction (the
    # cost it writes is instance state), and the neighbouring identity checks
    # in combat.py take the same care.
    if not any(c is card for c in state.player.hand):
        return
    card.cost_set_this_combat = state.rng.randrange(n)
    state.emit("cost_randomised", card=card.id,
               amount=card.cost_set_this_combat)


def retain_at_flush(state: CombatState, flushing: list[Card]) -> list[Card]:
    """WellLaidPlansPower.BeforeFlushLate: keep up to Amount cards that would
    otherwise be discarded, giving each single-turn Retain.

    The base game asks the PLAYER which ones. tier0 asks the same pilot
    surface `_best_card` already answers with, so this is not a second
    heuristic to keep honest -- and, like every pilot placeholder, it is the
    knob to probe if a Well Laid Plans measurement looks heuristic-shaped.
    Returns the subset to keep in hand; the caller flushes the rest.
    """
    keep: list[Card] = []
    if not flushing:
        return keep

    # PhantomBladesPower gives Retain to every tagged card it owns
    # (AfterApplied over AllCards, then AfterCardEnteredCombat for each new
    # one). tier0 has no per-instance keyword grant, but Retain IS "survives
    # the flush", so granting it here is the same observable rule applied at
    # the only site that reads it. NOT capped by a count: unlike Well Laid
    # Plans below, this power keeps ALL of them.
    tag = state.player.power_payloads.get("phantom_blades")
    if state.player.powers.get("phantom_blades", 0) and tag:
        keep = [c for c in flushing if tag in c.tags]
        if keep:
            state.emit("phantom_blades_retain", kept=[c.id for c in keep])

    # Well Laid Plans keeps up to Amount MORE. Its allowance is its own: the
    # cards Phantom Blades already retained were never candidates for it,
    # and counting them would silently shrink a power nobody changed.
    n = state.player.powers.get("well_laid_plans", 0)
    if not n:
        return keep
    from tier0.engine.effects import _best_card
    # Identity, not equality: equal twins are distinct instances, and a
    # value-based filter/remove here would either shrink the candidate pool
    # by every copy of a kept card or hand the same instance out twice.
    keep_ids = {id(c) for c in keep}
    pool = [c for c in flushing if id(c) not in keep_ids]
    wlp: list[Card] = []
    while pool and len(wlp) < n:
        pick = _best_card(pool)
        pool = [c for c in pool if c is not pick]
        wlp.append(pick)
    state.emit("well_laid_plans", kept=[c.id for c in wlp])
    return keep + wlp


def envenom_on_hit(state: CombatState, enemy: Enemy, unblocked: float,
                   source: str) -> None:
    """EnvenomPower.AfterDamageGiven(dealer == Owner, IsPoweredAttack,
    UnblockedDamage > 0) -> apply Amount Poison to the target.

    All three conditions matter and each removes a different free lunch: an
    Unpowered power tick does not envenom, a fully blocked hit does not, and
    a non-attack does not.
    """
    n = state.player.powers.get("envenom", 0)
    if not n or source != "attack" or unblocked <= 0 or not enemy.alive:
        return
    from tier0.engine import powers as _powers
    _powers.apply_power(state, enemy, "poison", n, applier=state.player)


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

    # TemporaryDexterityPower (Anticipate) applies real Dexterity now and
    # unapplies the same magnitude at the owner's turn end -- its
    # InternallyAppliedPower IS DexterityPower.
    elif name == "temp_dexterity" and stacks:
        target.powers["dexterity"] = target.powers.get("dexterity", 0) + stacks

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
    # OutbreakPower.AfterPowerAmountChanged(power is Poison, amount > 0,
    # applier == Owner): count, and on every THIRD application damage every
    # enemy for Amount (Unpowered), then `timesPoisoned %= 3`. The counter is
    # per APPLICATION, not per stack -- poisoning three enemies with one card
    # fires it once, and a single 9-stack Deadly Poison does not fire it at
    # all. The threshold is the power's own const.
    if (name == "poison" and stacks > 0 and applier is state.player
            and state.player.powers.get("outbreak", 0)):
        state.outbreak_poisonings += 1
        if state.outbreak_poisonings >= C.OUTBREAK_POISON_THRESHOLD:
            state.outbreak_poisonings %= C.OUTBREAK_POISON_THRESHOLD
            n = state.player.powers["outbreak"]
            for enemy in list(state.living_enemies):
                unpowered_damage(state, enemy, n)

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
                        attacker: Optional[Fighter],
                        from_card: bool = False) -> float:
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
        return _intangible_cap(defender, dmg)

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

    # TrackingPower.ModifyDamageMultiplicative returns base.Amount -- the
    # stacks ARE the multiplier, not a percentage: 2 stacks is double damage
    # against a Weak target, and a second application makes it 3. It is
    # keyed off the DEALER holding the power and the TARGET holding Weak, so
    # it belongs on this two-sided hook rather than in modify_damage_dealt,
    # which only ever sees the attacker.
    tracking = attacker.powers.get("tracking", 0)
    if tracking and defender.powers.get("weak", 0) > 0:
        dmg *= tracking

    # DoubleDamagePower returns a FLAT 2, never base.Amount -- the stacks are
    # a turn counter (one is decremented at each of the owner's turn ends),
    # not a multiplier. Two stacks is two turns of doubling, not quadruple
    # damage, and reading it the other way would be a large silent buff.
    # Requires a card source: a bomb or a poison tick is not doubled.
    if from_card and attacker.powers.get("double_damage", 0):
        dmg *= C.DOUBLE_DAMAGE_MULT

    return _intangible_cap(defender, dmg)


def _intangible_cap(defender: Fighter, dmg: float) -> float:
    """IntangiblePower is a CAP, not a multiplier, so it is the last word:
    ModifyDamageCap returns 1 for the owner and ModifyHpLostAfterOsty clamps
    HP loss to 1 on top of that. Damage BELOW 1 is left alone (`if (amount <
    1m) return amount`) -- Intangible does not round a 0 up.

    Its own function because it must apply on BOTH exits of
    modify_damage_taken. The dealer-keyed powers above bail out when the
    attacker is unknown; a damage cap has nothing to do with who is dealing.
    """
    if defender.powers.get("intangible", 0) and dmg > C.INTANGIBLE_DAMAGE_CAP:
        return C.INTANGIBLE_DAMAGE_CAP
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
        remove_instance(p.discard_pile, card)
        p.hand.append(_upgraded(state, card))
        state.emit("aggression_recall", card=card.id)


def _upgraded(state: CombatState, card: Card) -> Card:
    """`loader.get_card(id + upgrades.SUFFIX)`, the repo's one upgrade path.

    A card with no `+` entry is NOT quietly handed over un-upgraded: the move
    half is implemented, the upgrade half is logged loudly so the sheet gap is
    visible in the event stream rather than biasing Aggression's rating down.

    ONLY A SHEET GAP IS LOGGED. `except Exception` used to cover this call and
    report every failure as "no upgrade entry", which is a claim about the
    SHEET made without knowing what threw. The three things this path can
    raise are not one fact:

      - `KeyError` -- the base id is not in the card index at all (a synthetic
        id, or an already-upgraded card whose `++` has no base);
      - `ValueError("no applicable upgrade ...")` -- the id is real and the
        sheet has no expressible `+` delta for it;
      - any other `ValueError` -- `apply_upgrade` rejecting a MALFORMED delta
        (`innate delta must be true`, a bad field, a duplicate upgrade id).

    The first two are the gap this event exists to record, and they are
    recorded apart because they want different fixes. The third is a defect in
    the upgrade sheet; filing it as "this card has no upgrade" would hide a
    broken row behind an ordinary-looking absence, so it propagates.
    """
    from tier0.content import loader, upgrades
    try:
        return loader.get_card(card.id + upgrades.SUFFIX)
    except KeyError:
        reason = "no card-sheet entry for this id; moved unupgraded"
    except ValueError as exc:
        if "no applicable upgrade" not in str(exc):
            raise
        reason = "no upgrade entry for this card id; moved unupgraded"
    state.emit("UNIMPLEMENTED", power="aggression", card=card.id,
               reason=reason)
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

    # ToolsOfTheTrade, also site E (AfterPlayerTurnStart): it raised the hand
    # draw by Amount in hand_draw_bonus and now takes Amount BACK as a chosen
    # discard. The card is a filter, not card advantage, and splitting it
    # across the two sites is what makes that true rather than asserted.
    n = p.powers.get("tools_of_the_trade", 0)
    if n:
        from tier0.engine import effects as _effects
        _effects.OPS["discard"](state, {"op": "discard", "amount": n,
                                        "select": "chosen"}, None)

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

    # Blur decrements at the owner's side turn start -- AFTER the block clear
    # it just suppressed (site B ran before this), so a single stack carries
    # block across exactly one boundary.
    if p.powers.get("blur", 0):
        p.powers["blur"] -= 1

    # DrawCardsNextTurn is REMOVED (not decremented) at the turn start whose
    # draw it just paid for. hand_draw_bonus added it a few lines of engine
    # ago at site D; this is the other half of that one-shot.
    p.powers.pop("draw_cards_next_turn", None)

    # NoxiousFumes: poison every enemy at site F, every turn, forever.
    n = p.powers.get("noxious_fumes", 0)
    if n:
        from tier0.engine import powers as _powers
        for enemy in list(state.living_enemies):
            _powers.apply_power(state, enemy, "poison", n, applier=p)

    # WraithForm's downside, site F: the owner LOSES Amount Dexterity every
    # turn, forever. It is a Debuff on its own owner and never expires, which
    # is the whole cost of the card -- Intangible 2 up front, paid for by an
    # accelerating Dexterity hole. Applied through the normal power path so
    # the loss stacks and reaches the block funnel like any other Dexterity.
    n = p.powers.get("wraith_form", 0)
    if n:
        from tier0.engine import powers as _powers
        _powers.apply_power(state, p, "dexterity", -n, applier=p)

    # ShadowStepPower, site F (AfterSideTurnStart): it converts itself into
    # DoubleDamage and is REMOVED -- a one-turn delayed payload, not a
    # standing buff. Order matters: this runs at the start of the turn the
    # doubling applies to, so the card played last turn pays out this turn.
    n = p.powers.pop("shadow_step", 0)
    if n:
        from tier0.engine import powers as _powers
        _powers.apply_power(state, p, "double_damage", n, applier=p)

    # Poison, also site F. It can kill; the caller re-checks p.alive.
    poison_tick(state, p)


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
    # TemporaryDexterityPower (Anticipate) reverts the same way: remove the
    # marker and unapply the magnitude, never decrement by one.
    n = fighter.powers.pop("temp_dexterity", 0)
    if n:
        fighter.powers["dexterity"] = fighter.powers.get("dexterity", 0) - n

    if fighter is not state.player:
        # StranglePower sits on an ENEMY and is removed at the ENEMY side's
        # turn end (`participants.Contains(Owner)`), so the debuff covers the
        # player turn it was applied on plus nothing else.
        fighter.powers.pop("strangle", None)
        return

    # Removed WHOLE at the owner's turn end (PowerCmd.Remove, not Decrement).
    # burst / corrosive_wave / shadowmeld are the Silent's three one-turn
    # powers and share the site exactly.
    for name in ("rage", "no_draw", "no_energy_gain", "one_two_punch",
                 "burst", "corrosive_wave", "shadowmeld"):
        fighter.powers.pop(name, None)
    state.no_energy_gain_ceiling = None

    # DoubleDamage DECREMENTS here (PowerCmd.Decrement, not Remove), which is
    # why its stacks read as turns of doubling remaining -- the multiplier
    # itself is a flat 2 no matter how many are left.
    if fighter.powers.get("double_damage", 0) > 0:
        fighter.powers["double_damage"] -= 1

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
    # IntangiblePower decrements on `side == CombatSide.Enemy`, so its stacks
    # read as "enemy turns survived at 1 damage".
    if p.powers.get("intangible", 0) > 0:
        p.powers["intangible"] -= 1


def reset_turn_counters(state: CombatState) -> None:
    """Per-player-turn windows owned by this module."""
    state.attacks_played_this_turn = 0            # Juggling
    state.skills_played_this_turn = 0             # Pinpoint
    state.block_gain_card_plays_this_turn = 0     # Unmovable's allowance
    state.cards_exhausted_this_turn = 0           # EvilEye / ForgottenRitual
    state.hp_lost_this_turn = 0                   # Spite
    state.discards_this_turn = 0                  # MementoMori
    state.tag_plays_this_turn = {}                # PhantomBlades
    # Per-instance TURN-scoped card state expires here (BulletTime's free
    # cost, Pinpoint's discount, HandTrick's granted Sly). Swept across every
    # pile because a freed card that was discarded and redrawn must not come
    # back still free; the combat-scoped delta is deliberately untouched.
    #
    # EB-71 (R174): the granted Sly is a rider in the unified `sly` list, so
    # the sweep drops riders marked `until: turn_end` and leaves everything
    # else -- the printed keyword, Master Planner's permanent mark, and
    # Kokomi's authored Assist effects all survive the boundary, exactly as
    # they did when the grant was its own boolean. The list is rebound only
    # when something is actually dropped, so the common path allocates
    # nothing (this loop runs over every pile every turn).
    p = state.player
    for pile in (p.hand, p.draw_pile, p.discard_pile, p.exhaust_pile):
        for held in pile:
            held.free_this_turn = False
            held.cost_delta_this_turn = 0
            # The guard asks the helper rather than re-writing its predicate:
            # what expires at the turn boundary is DEFINED in one place
            # (state.sly_granted_this_turn), and a second copy here could drift
            # from it silently.
            if sly_granted_this_turn(held):
                held.sly = [fx for fx in held.sly
                            if not (fx.get("op") == SLY_AUTOPLAY_OP
                                    and fx.get("until") == "turn_end")]
    state.rupture_pending = 0


def energy_for_turn(state: CombatState) -> int:
    """PyrePower.ModifyMaxEnergy(player, amount) => amount + Amount.

    This is a reset to MAX, not an accumulating gain -- it does not compound
    across turns, and it is deliberately NOT the same site as NoEnergyGain.
    """
    return C.BASE_ENERGY_PER_TURN + state.player.powers.get("pyre", 0)


def should_clear_block(player: Player) -> bool:
    """ShouldClearBlock => Owner != creature, for BOTH powers that override it.

    Barricade is permanent; Blur is the same suppression on a counter that
    ticks down at the owner's turn START (site F, after this runs), so N
    stacks carry block through N turn boundaries.
    """
    if player.powers.get("barricade", 0):
        return False
    return not player.powers.get("blur", 0)


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
