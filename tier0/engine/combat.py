"""Turn loop (spec §3/§4.5). One function: run_fight.

Player turn: bombs detonate -> auras tick -> power hooks -> draw + energy ->
pilot plays until done -> discard hand -> power decay.
Enemy turns: scripted intents, no AI. Asleep enemies take no action but are
still side-turn participants (EB-96: block clear, turn-start and turn-end
hooks all fire); frozen enemies act at -50% damage (Frozen v2, principles
v1.5).
"""

from __future__ import annotations

import random
from typing import Callable

from tier0 import constants as C
from tier0.engine import (effects, furina_reframe, potions, powers,
                          reactions, refpowers, relics, resources)
from tier0.engine.state import (Card, CombatState, Enemy, Player,
                                remove_instance, sync_fanfare_cap_to_max_hp)

# A pilot is a callable: (state) -> Card | None (None = end turn).
Pilot = Callable[[CombatState], Card | None]


def _base_card_id(card_id: str) -> str:
    """`foo+` -> `foo`. The sim's card ids carry the upgrade in the id
    itself (upgrades.SUFFIX); C# carries it as a flag beside a base ModelId.
    Anywhere the two sides must agree on card IDENTITY rather than card
    STATE, the sim has to strip the suffix to see what C# sees."""
    from tier0.content import enchantments, upgrades   # late: avoids a cycle
    card_id, _, _ = enchantments.split(card_id)   # an enchantment is STATE too
    if card_id.endswith(upgrades.SUFFIX):
        return card_id[:-len(upgrades.SUFFIX)]
    return card_id


def spark_threshold(state: CombatState) -> int:
    """RETIRED-UNDER-FLAG (R213 E2, PICK 6). The base rule's bar.

    UNREAD whenever `C.SPARK_ALT_COST_ENABLED` is true: with the flag on
    there is no threshold to be at, nothing is zeroed and nothing is
    consumed, so every caller of this function is guarded by the flag. It
    stays in the file so the OFF arm is still expressible -- that is what a
    two-arm flag is for -- and no new code path calls it.
    """
    # True Spark Knight: free attack at 2 sparks instead of 3.
    return max(1, C.SPARKS_FOR_FREE_ATTACK
               - state.player.powers.get("spark_threshold_down", 0))


def spark_power_price(state: CombatState, card: Card) -> int:
    """The Spark price the STRICT Rare Power contributes to `card`, or 0.

    PICK 5, wording (1), sub-pick (a). "Your Attacks that do not already cost
    [Spark] cost 3 [Spark] instead of their Energy cost." Three clauses, and
    each one is a line here:

      * ATTACKS ONLY -- Skills and Powers keep their Energy cost untouched.
        Energy becomes very nearly pure Skill currency, which is the payoff
        loop the Power is a bet on.
      * "THAT DO NOT ALREADY COST [Spark]" -- sub-pick (a). A card printing
        its own `spend_spark` keeps its printed price; the Power neither
        raises it nor adds to it. (b) would have re-priced Fwoosh! from 1 to
        3, punishing the cards the archetype drafts.
      * X-COST ATTACKS ARE EXEMPT, AND THE PACKET DOES NOT SAY SO. §5 is
        silent on X and this is the reading taken, stated rather than
        buried: an X card's cost IS the energy it spends
        (`card_cost`'s first branch, `state.current_x`), so converting it to
        a flat 3 Sparks would resolve it at X = 0 and deal nothing --
        exactly the reasoning R34 gave for the base rule's own X exemption,
        reached again from the other side. It goes back to [USER] in the
        packet's §10.

    The price is NOT on the card, so `spark_cost` -- which reads printed
    top-level ops and nothing else -- cannot see it and is not asked to. This
    is the second, state-aware half, and `spark_price` below is the sum the
    gate and the payment both consult.
    """
    if not C.SPARK_ALT_COST_ENABLED:
        return 0
    if card.type != "attack" or card.cost == "X":
        return 0
    if not state.player.powers.get("spark_attack_cost", 0):
        return 0
    if spark_cost(card):
        return 0                # already Spark-priced: unaffected, (a)
    return C.SPARK_ATTACK_POWER_PRICE


def spark_price(state: CombatState, card: Card) -> int:
    """What this card charges in Sparks RIGHT NOW: printed plus power.

    One function so the playability gate, the payment and the pilot's hold
    term can never disagree about the number -- the same argument
    `spark_cost` makes for the printed half, one layer up.
    """
    return spark_cost(card) + spark_power_price(state, card)


def grant_charged_kit(state: CombatState) -> None:
    """v1.9: the Burst is kit, not loot. When the meter is full, the kit
    card is granted to hand; casting empties the meter (play_card), so a
    refill re-grants it.

    Two call sites cover every gain: all burst-energy sources (reactions,
    detonation splash, the burst_energy op, skill tags) fire inside the
    player-turn window, either in the turn-start trigger block or during a
    card's resolution -- so checking at turn start and after each play is
    exhaustive without instrumenting the five gain sites individually.

    Respects MAX_HAND_SIZE: a full hand defers the grant to the next check
    rather than dropping it -- the meter stays full, so it cannot be lost.
    """
    p = state.player
    if not p.burst_max or p.burst_energy < p.burst_max:
        return
    for kit in p.kit_cards:
        if any(c.id == kit.id for c in p.hand):
            continue
        if len(p.hand) >= C.MAX_HAND_SIZE:
            return
        p.hand.append(kit)
        state.emit("kit_burst_granted", card=kit.id)


def _revive_player_if_needed(state: CombatState) -> bool:
    """Resolve a held Fairy at combat checkpoints after player HP can move."""
    if state.player.alive or not state.player.potions:
        return False
    return potions.try_fairy_revive(state)


def _settle_phases(state: CombatState) -> None:
    """HP-threshold boss phases (§10.2, RATIFIED 2026-07-23). An enemy at
    hp <= 0 with phases remaining REVIVES into its next phase instead of
    dying: fresh bar, fresh moveset, powers/aura/bombs cleared (a new body).
    Called at every site that can drop enemy HP -- after each card play,
    the bomb-detonation sweep, turn-start potion use, the player-turn-end
    triggers, and each enemy turn (retaliation kills) -- always BEFORE the
    loop re-reads state.over, so a phased boss never ends the fight early.
    Dead branch for every enemy without phases (the whole roster today).

    Known approximation: kill-counting predicates (killed_target et al.)
    observe the hp <= 0 moment before the revive, so a phase-down counts as
    a kill for those card effects. Fatal (Feed) does NOT: counts_for_fatal
    stays False until the last phase is entered."""
    for e in state.enemies:
        while e.phases and e.hp <= 0:
            ph = e.phases.pop(0)
            e.hp = e.max_hp = int(ph["hp"])
            e.intents = ph["intents"]
            e.intent_index = 0
            # A new bar is a new moveset: its ramps start counting HERE, not
            # at combat start. Without this, a phase-2 intent arrives already
            # ramped by however many turns the previous bar took -- Test
            # Subject's Multi-Claw opened at 84 instead of its authored 30.
            e.phase_start_turn = state.turn
            e.intent_uses = {}
            e.block = 0
            # A new bar is a new body -- EXCEPT Strength and Enrage, which
            # the real boss keeps across knockdowns ("only the Adaptable and
            # Painful Stabs powers are cleaned up at the second revive, not
            # Strength", dossier :240). Enrage is fight-long by the same
            # line; per-phase powers arrive from the phase spec below.
            e.powers = {k: v for k, v in e.powers.items()
                        if k in ("strength", "enrage")}
            for pname, amt in (ph.get("powers") or {}).items():
                e.powers[pname] = int(amt)
            # Nemesis opens its phase Intangible: stack 1 at the revive, so
            # the first ACTING turn (after the respawn sleep) is capped --
            # the dossier's turn-1 row. The end-of-turn toggle owns it after.
            if e.powers.get("nemesis", 0):
                e.powers["intangible"] = 1
            e.aura = None
            e.aura_turns_left = 0
            e.bombs = []
            e.frozen = 0
            # Respawn costs the boss its next turn: the real Test Subject
            # spends a full enemy turn reviving and deals nothing on it, once
            # per knockdown (dossiers/enemies/test-subject.md:51-58,129,134).
            # sleep_turns already skips a turn without advancing the intent
            # (_enemy_turn above), which is exactly Respawn's shape.
            e.sleep_turns = 1
            if not e.phases:
                e.counts_for_fatal = True     # the last bar is a real death
            state.emit("phase_change", enemy=e.name, hp=e.hp,
                       remaining=len(e.phases))
    # EB-58: this is the documented "after every site that can drop enemy HP"
    # chokepoint, so it is also where an aura on a body that just died stops
    # counting as uptime. Runs AFTER the revive loop, so a phased knockdown
    # (fresh bar, aura already cleared above) is never reported as a death.
    reactions.close_dead_auras(state)


def card_playable(state: CombatState, card: Card) -> bool:
    if card.type == "status":
        return False        # §10.2 injected statuses: unplayable clogs
    # Normality: "you cannot play more than 3 cards this turn", read off
    # whatever cap-bearing card is IN HAND. Gated on a per-combat flag set at
    # fight start so the battery -- where nothing carries a cap -- never even
    # walks the hand; this function is on the pilot's hot path.
    # KNOWN GAP, stated not hidden: the real curse exempts REPLAYS (Echo
    # Form and friends still fire past the cap). Ours has no replay concept
    # at this seam, so a replay-heavy deck is capped slightly harder than the
    # real game caps it -- the harsh direction, unusually, and the reason it
    # is written down.
    if state.hand_play_cap:
        cap = min((c.status_play_cap for c in state.player.hand
                   if c.status_play_cap), default=0)
        if cap and state.cards_played_this_turn >= cap:
            return False
    if card.requires == "burst_energy_full":
        if state.player.burst_energy < state.player.burst_max:
            return False
    elif card.requires == "draw_pile_empty":
        # GrandFinale's `IsPlayable => Draw.GetPile(Owner).Cards.Count == 0`.
        # A real playability GATE, not a cost: the card sits in hand, dead,
        # until the deck runs out. pilot/policy.py already filters on this
        # function, so the pilot inherits the rule without knowing the card.
        if state.player.draw_pile:
            return False
    elif card.requires:
        raise ValueError(f"unknown requires {card.requires!r}")
    if card.encore_cost and state.player.encore < card.encore_cost:
        return False        # "Spend N Encore:" cost line -- a gate, never
                            # an overdraw (that is the spend_encore op)
    # `spark_price`, not `spark_cost`: the printed price PLUS whatever the
    # strict Rare Power contributes (0 with the flag off, so this line is
    # byte-identical there). "Unplayable below 3 Sparks" is this gate.
    price = spark_price(state, card)
    if price and state.player.sparks < price:
        return False        # EB-118 §4.5, the Spark sink's cost line: the
                            # gate one line up, DERIVED from the op instead
                            # of a second sheet field, so the price shown
                            # and the price paid cannot drift apart.
    price = charge_cost(card)
    if price and state.player.charge < price:
        return False        # QUARANTINED (R213 E1), the Charge sink's cost
                            # line -- the Spark gate above, one meter over,
                            # and DERIVED from the op for the same reason.
    # EB-182, per-option playability: a card whose top-level `choose_one`
    # prices EVERY mode above the bank has no line left to offer, so it is
    # unplayable -- the two gates above, one nesting level down.
    # `modal_refusal` is the same predicate with the reason attached.
    if modal_refusal(state, card) is not None:
        return False
    # No Fanfare playability gate: Fanfare is read, never spent (F-A4).
    return card_cost(state, card) <= state.player.energy


def modal_refusal(state: CombatState, card: Card) -> str | None:
    """Why no mode of this card can be paid for, or None (EB-182).

    THE PRINTABLE HALF of the rule in `effects.mode_price`. `card_playable`
    is a bool on the pilot's hot path and cannot carry a reason; every reader
    that shows a refused line to a human or a grader -- a staged-turn packet,
    the falsifier, a replay -- asks here instead, and gets a string naming
    each dead mode's PRICE and the BANK that fell short.

    TOP-LEVEL `choose_one` only, matching `spark_cost` / `charge_cost`: a
    modal nested inside a conditional branch is not a cost line, because the
    branch that would reach it is not settled when the card is offered.
    """
    for fx in card.effects:
        if fx.get("op") != "choose_one":
            continue
        modes = fx.get(effects.MODES_KEY) or []
        if not modes or effects.offered_modes(state, modes):
            continue
        reasons = [effects.mode_refusal(state, mode) for mode in modes]
        return (f"{card.id}: no mode is affordable -- "
                + "; ".join(r for r in reasons if r))
    return None


def spark_cost(card: Card) -> int:
    """What this card's printed text charges in Sparks, 0 for every shipped
    card (EB-118 stages the op; no sheet row uses it).

    TOP-LEVEL ops only. A spend inside a conditional branch is a price the
    player cannot be shown before choosing to play the card, so it is not
    part of the cost line -- effects.spend_sparks refuses it at resolve time
    instead, which is the loud half of the same rule.
    """
    total = 0
    for fx in card.effects:
        if fx.get("op") == "spend_spark":
            total += effects.spend_spark_amount(fx)
    return total


def charge_cost(card: Card) -> int:
    """What this card's printed text charges in Charge, 0 for every shipped
    card. QUARANTINED (R213 E1): `spend_charge` lives on the prototype
    surface alone, and R80 -- Charge is read, never spent -- is what the
    slice reopened rather than what it repealed.

    TOP-LEVEL ops only, `spark_cost`'s rule verbatim. A spend inside a
    `choose_one` mode is not part of THIS cost line: it is the MODE's cost
    line, gated per option by `modal_refusal` since EB-182, and
    `effects._op_spend_charge` still stops the card if one ever resolves
    short -- the loud half of the same rule.
    """
    total = 0
    for fx in card.effects:
        if fx.get("op") == "spend_charge":
            total += effects.spend_charge_amount(fx)
    return total


def card_cost(state: CombatState, card: Card) -> int:
    if card.cost == "X":
        # An X card spends the whole bank and NO cost modifier is consulted --
        # this early return is the game's own shape, not a tier0 shortcut.
        # CardEnergyCost.GetAmountToSpend() opens with
        # `if (CostsX) return Owner.PlayerCombatState?.Energy ?? 0;`, returning
        # before GetWithModifiers; and GetWithModifiers itself opens with
        # `if (CostsX) return num;` BEFORE its
        # `Hook.ModifyEnergyCostInCombat(...)` line. So the ...InCombatLate
        # hook that FreeAttack (Unrelenting) and Corruption implement never
        # runs on an X card, even though each sets modifiedCost = 0
        # unconditionally once reached. Whirlwind is therefore never freed by a
        # FreeAttack stack -- and must not be, since X is the energy actually
        # spent (EnergyCost.CapturedXValue), so a freed Whirlwind would resolve
        # at X = 0 and deal nothing. Same conclusion as the R34 spark exemption
        # below, reached independently. Pinned by
        # test_refpowers.test_free_attack_does_not_zero_an_x_cost_attack.
        return state.player.energy
    cost = card.cost
    # EB-83. An ABSOLUTE combat-scoped set (EnergyCost.SetThisCombat) replaces
    # the printed cost and the RELATIVE deltas below still stack on top -- the
    # game's `_localModifiers` list applies in insertion order and an Absolute
    # entry overwrites the running value at its own position. The one case
    # that differs is a relative modifier added BEFORE the set, which the game
    # would discard and this keeps; nothing in this engine writes both to one
    # instance, and the honest place to record that is here rather than in a
    # second field. None on every shipped card (unused machinery).
    if card.cost_set_this_combat is not None:
        cost = card.cost_set_this_combat
    # PER-INSTANCE cost state, the base game's EnergyCost.AddThisTurn /
    # AddThisCombat / SetToFreeThisTurn. It lives on the CARD OBJECT because
    # that is what the game modifies: two copies of Up My Sleeve in one deck
    # discount themselves separately, and a card that leaves hand and is
    # redrawn keeps its combat-scoped discount. Applied before every other
    # modifier and floored at 0 like they are.
    if card.free_this_turn:
        return 0
    cost = max(0, cost + card.cost_delta_this_turn
               + card.cost_delta_this_combat)
    if card.cost_reduction_per_attack_this_turn:
        cost = max(0, cost - (card.cost_reduction_per_attack_this_turn
                              * state.attacks_played_this_turn))
    if card.cost_reduction_per_skill_this_turn:
        cost = max(0, cost - (card.cost_reduction_per_skill_this_turn
                              * state.skills_played_this_turn))
    if card.is_companion and state.companion_cost_delta_this_turn:
        cost = max(0, cost + state.companion_cost_delta_this_turn)
    # Leading Role (card-level texture, kickoff §3.2): the FIRST
    # Spotlighted card each turn costs less. This is a Furina-card power
    # granting economy, not the Spotlight baseline -- §2.2a governs the
    # multiplier, and the multiplier has no path here.
    p = state.player
    # B2: gated on the PAID counter, so a free Spotlighted play (Ethereal
    # Spotlight's token, chiefly) neither takes the discount nor burns it.
    if (effects.is_spotlighted(state, card)
            and state.spotlighted_paid_cards_this_turn == 0):
        cost = max(0, cost - p.powers.get("spotlight_discount", 0))
    # THE STRICT RARE POWER'S ENERGY HALF (PICK 5): "...instead of their
    # Energy cost". A converted Attack costs 0 Energy; the Sparks are taken in
    # `play_card`. Checked BEFORE the retired zeroing branch below so the two
    # rules can never both fire -- they cannot anyway, the flag makes them
    # mutually exclusive, and the order says so at the site.
    if spark_power_price(state, card):
        return 0
    # RETIRED-UNDER-FLAG: THE ZEROING. "At 3 Sparks, your Attacks cost 0" --
    # the base rule's first half, and the half R213 E2 named as feeding none
    # of D2's six steerable verbs: the bank has one destination and the engine
    # picks it. With `SPARK_ALT_COST_ENABLED` on, an Attack costs what it
    # prints (or what the Power above charges), and a full bank discounts
    # nothing.
    if (not C.SPARK_ALT_COST_ENABLED
            and card.type == "attack"
            and state.player.sparks >= spark_threshold(state)):
        return 0
    # Base-game parity (FreeAttack / Corruption): checked AFTER the spark
    # branch, so a spark-freed attack spends the bank rather than a stack.
    # Precedence pinned by
    # test_refpowers.test_free_attack_and_spark_are_both_consumed.
    if refpowers.free_cost(state, card):
        return 0
    return cost


def play_card(state: CombatState, card: Card) -> None:
    p = state.player
    cost = card_cost(state, card)
    # R34: X-cost cards are exempt from spark spend. A Spark-freed X card
    # would resolve at X = 0 -- the mechanic cannot coherently apply, and
    # without the exemption an X attack at 0 energy trips this predicate
    # (paid 0, printed != 0) and whiffs the whole spark bank.
    # R39 (user ruling 2026-07-21): effects that READ the spark bank see it
    # as it was when the card was played, before this card's own spend.
    # Gleeful Barrage ("2 + Sparks hits") otherwise fought itself: reaching
    # the threshold that makes it free is exactly what deleted the sparks it
    # counts, so at exactly 3 sparks it went free AND dropped to 2 hits. Only
    # attacks spend, and the two has_spark cards are skills, so this card is
    # the whole blast radius.
    state.sparks_at_play = p.sparks
    # RETIRED-UNDER-FLAG: THE AUTOMATIC CONSUME. "Playing one consumes 3" --
    # the base rule's second half. Under `SPARK_ALT_COST_ENABLED` nothing
    # spends implicitly: every Spark that leaves the bank leaves it because a
    # printed price or the strict Power charged it, both of which are visible
    # before the card is played. R34's X exemption above goes with it (there
    # is no spend to be exempt from); the branch is left inert rather than
    # deleted so the OFF arm still runs the shipped rule byte for byte.
    if (not C.SPARK_ALT_COST_ENABLED
            and card.type == "attack" and cost == 0
            and p.sparks >= spark_threshold(state)
            and card.cost != 0 and card.cost != "X"):
        p.sparks -= spark_threshold(state)
        state.emit("sparks_spent")
    # THE STRICT RARE POWER'S PAYMENT (PICK 5), and it is the only new debit
    # in this function. The printed half of a Spark price is paid by the card's
    # own top-level `spend_spark` op when its effects resolve; the Power's half
    # is not on the card, so it is taken here, at the cost line, beside the
    # energy. `card_playable` has already refused a short bank, so this cannot
    # half-pay -- and `spend_sparks` is all-or-nothing anyway and emits its
    # refusal if it ever does.
    owed = spark_power_price(state, card)
    if owed:
        effects.spend_sparks(state, owed)
    if card.cost == "X":
        state.current_x = cost                # X = energy actually spent
    state.current_card_cost = cost
    p.energy -= cost
    if card.encore_cost:
        # Gated playable -- the "Spend N Encore:" cost line, which is a
        # different sink from the spend_encore OP and is kept apart in the
        # census for that reason (EB-20).
        resources.spend_encore(state, card.encore_cost, "encore_cost",
                               card.id)
    # EB-17: read the draw context BEFORE the instance leaves hand, then
    # release it -- an instance that is no longer in hand has no draw context,
    # and holding the entry past the play is what would let a freed card's
    # address be reused by a later one.
    drawn_turn, first_copy = state.drawn_context(card)
    remove_instance(p.hand, card)
    state.drawn_in_hand.pop(id(card), None)
    state.cards_played_this_turn += 1
    state.emit("play", card=card.id, cost=cost, energy_left=p.energy,
               drawn_turn=drawn_turn, first_copy=first_copy)
    # EB-101 (races-d): Supporting Cast's draw is RECORDED here and RESOLVED
    # below `_finish_play`, which is where the mod resolves it. See the block
    # that sets this, and the one that spends it.
    pending_spotlight_draw = 0
    if effects.is_spotlighted(state, card):
        # Spotlight texture applies in both modes. Only Center Stage creates
        # Fanfare; Guest Cast spends the light on Companion empowerment.
        # Counted BEFORE resolution so the reserve per-turn cap (OFF by
        # default) can compare against this play's own ordinal.
        state.spotlighted_cards_this_turn += 1
        # B2: the discount's own window. PRINTED cost, not the resolved one --
        # a printed-1 card discounted to 0 must still spend the window, or the
        # discount would re-arm behind its own effect and apply every turn.
        # An X-cost card counts as paid (its printed cost is not a number, and
        # X plays are never the free-token case this guard exists for).
        if not isinstance(card.cost, int) or card.cost >= 1:
            state.spotlighted_paid_cards_this_turn += 1
        state.emit("spotlight_card_played", card=card.id)
        # Center Stage's half, asked PER CARD rather than per mode: under
        # Furina's upgraded starter (R2) both halves are live, so "is Center
        # Stage the mode" stops being the same question as "does this card
        # mint Fanfare". Companions are lit under the upgrade and still mint
        # nothing -- the upgrade drops the exclusivity, not the targeting.
        if (effects.center_stage_active(state, card)
                and not furina_reframe.meter_active(p)):
            # RETIRED UNDER `FURINA_REFRAME_METER` (reframe §4.1): a
            # Spotlighted card played mints nothing, because only a member
            # PERFORMING mints. R228's one-mode Spotlight retires Center Stage
            # outright as well, and `center_stage_active` answers False under
            # its own flag -- two flags, two reasons, and either alone is
            # enough to empty this leg.
            resources.gain_fanfare(
                state, C.FANFARE_PER_SPOTLIGHT_CARD, "center_stage")
        # Card-level Spotlight texture (sheet pass 1, ratified design
        # space): Supporting Cast draws on the FIRST Spotlighted card
        # each turn; post-flip Standing Ovation's trickle uses the same
        # first-play window (spotlight_encore_first, pass 3 — the
        # per-play rate was the hot-sustain driver both times it was
        # tried). spotlight_encore (EVERY play) remains engine-supported
        # as the archived pre-flip rate.
        if state.spotlighted_cards_this_turn == 1:
            # EB-101, the RECORD half. The amount is read from the powers
            # dict HERE, on the mod's `BeforeCardPlayed` clock
            # (`SpotlightSystem.NotePlay` stores nothing but PendingDraws),
            # so a card that grants or strips `spotlight_draw` during its own
            # resolution cannot change the size of its own draw. Only the
            # DRAW moves below; the read does not.
            pending_spotlight_draw = p.powers.get("spotlight_draw", 0)
            n = p.powers.get("spotlight_encore_first", 0)
            if n:
                resources.gain_encore(state, n, "spotlight_encore_first",
                                      card.id)
        n = p.powers.get("spotlight_encore", 0)
        if n:
            resources.gain_encore(state, n, "spotlight_encore", card.id)
    if card.requires == "burst_energy_full":
        p.burst_energy = 0                    # playing the Burst empties it
        state.emit("burst_cast", card=card.id)
    if p.burst_max and "skill_tag" in card.tags:
        resources.gain_burst(state, C.BURST_PER_SKILL_TAG, "skill_tag")
    _finish_play(state, card)
    # EB-101 (races-d), the RESOLVE half -- the surviving member of the
    # EB-19/NC-9 broadcast-ordering family, whose siblings closed as
    # races-a/b/c.
    #
    # The mod records this draw in `BeforeCardPlayed` and resolves it in
    # `AfterCardPlayed` (`SpotlightSystem.cs:389-403`), so the triggering
    # card resolves against a hand WITHOUT the drawn cards. tier0 drew them
    # above the card's own resolution, so a Spotlighted card that reads the
    # hand while resolving -- Encore Performance -- selected from a
    # different-sized pool in each engine, and Director's Cut and Curtain
    # Cue flip the same way at MAX_HAND_SIZE.
    #
    # `BeforeCardPlayed` is not async and carries no PlayerChoiceContext, so
    # the mod's half cannot move; the movable leg is this one.
    #
    # NOT A PARITY CRITERION, deliberately: neither engine's draw consumes
    # `Rng.CombatTargets` and the two share no RNG stream, so the guarantee
    # here is structural (a hand size), never a fixed-seed trace match.
    if pending_spotlight_draw:
        state.draw(pending_spotlight_draw)
        state.emit("extra_draw", amount=pending_spotlight_draw)


def _finish_play(state: CombatState, card: Card,
                 force_exhaust: bool = False) -> None:
    """The half of a card play that does not depend on who paid for it.

    CardModel.OnPlayWrapper is entered identically by a manual play and by
    CardCmd.AutoPlay -- only the cost bookkeeping ahead of it differs. This
    is that shared half (the replay loop and its per-play-index hooks, the
    Power floor grant, result-pile routing, and the post-play settlement),
    split out so resolve_free_play cannot drift from play_card. Nothing here
    reads energy or the hand, so both callers are correct by construction.
    """
    p = state.player
    # QUARANTINED (C.KURAGE_MEMORY). HERE, at the shared half of a card play,
    # for the same structural reason the Casket accrual sits at the one
    # exhaust funnel: a manual play and an auto-play both enter through this
    # function and nothing else does, so "when Kokomi plays a card" is one
    # definition rather than per-site discipline. Ahead of the replay loop, so
    # the memory records the CARD PLAY once even when Study Buddy resolves it
    # twice -- a replay is one card being resolved again, not a second play.
    if C.KURAGE_MEMORY:
        effects.note_kurage_play(state, card)
    replays = 1
    if card.is_companion:
        # BFF-dedupe, RULED 2026-08-06: an upgraded companion IS the same
        # pool entry as its base, so `foo` and `foo+` are ONE entry in the
        # Best Friends Forever pool and it replays each companion once.
        #
        # The dedupe lives HERE, at the record site, because that is where
        # C# does it (CompanionPlays.Record keys on `(Owner, Id)`, and an
        # STS2 ModelId is the base card -- upgrade is a flag beside it). The
        # entry kept is the FIRST play's instance id, so the upgrade state a
        # copy carries is the first play's, matching C#'s `card.IsUpgraded`
        # recorded on the first Add. The replay site (effects.
        # _op_copy_companions_played) therefore reads a list that is already
        # unique, in first-play order, and does not dedupe again.
        base_id = _base_card_id(card.id)
        if all(_base_card_id(cid) != base_id
               for cid in state.companions_played):
            state.companions_played.append(card.id)
        state.companion_plays_this_turn += 1
        # Navia, Cannon Fire Support: the pool pays the pool. Fires once per
        # CARD PLAY, here beside companions_played, not once per replay inside
        # the loop below -- Study Buddy's replay is one card being resolved
        # twice, and paying it twice would make the two cards a combo rather
        # than each doing its own job. Sitting before resolve_card also means
        # Navia's own play does not pay itself: the power is not up yet.
        navia = p.powers.get("cannon_fire_support", 0)
        if navia:
            p.block += navia
            state.emit("cannon_fire_support", amount=navia, card=card.id)
        if state.replay_next_companion > 0:   # Study Buddy
            replays += state.replay_next_companion
            state.replay_next_companion = 0
    # Enrage (§10.9 promotion, R128): every Skill played feeds every living
    # enemy carrying the power -- permanent Strength, never telegraphed by an
    # intent (test-subject dossier :227-240). Once per card PLAY, not per
    # replay: a replay is one card being resolved twice.
    if card.type == "skill":
        for e in state.living_enemies:
            n = e.powers.get("enrage", 0)
            if n:
                powers.apply_power(state, e, "strength", n)
                state.emit("enrage_trigger", enemy=e.name, amount=n)
    # OneTwoPunch resolves the play COUNT once, but Before/AfterCardPlayed fire
    # per play index -- so a doubled attack pays Rage twice, counts twice for
    # Juggling, and burns two FreeAttack stacks.
    replays += refpowers.extra_replays(state, card)
    for replay_index in range(replays):
        snap = refpowers.before_card_played(state, card)
        effects.resolve_card(state, card)
        refpowers.after_card_played(state, card, snap)
        if replay_index == 0 and card.is_companion:
            # FURINA REFRAME (§4.3, `F3` (1) / `F4` (1)): a Companion play
            # makes the FRONT Salon member perform, then rotates it to the
            # back. Beside Klee's mint and gated the same way for the same two
            # reasons -- once per PLAY (a replay is one card resolved twice),
            # and after a resolution has run. Inert unless
            # `FURINA_REFRAME_MANUAL` is on, and inert for every other
            # character in every world.
            furina_reframe.companion_play_trigger(state, card)
            # "Little Hexenzirkul" (EB-219): Klee's kit answering a PERSONAL
            # Companion play, which is where LAW:145 puts the grant now that
            # Prune's face may not carry it. INSIDE the loop but gated to the
            # first pass, for two reasons that pull in opposite directions and
            # meet exactly here: the mint has to be ONCE PER PLAY (a replay is
            # one card resolved twice -- the same argument that put Navia's
            # Cannon Fire Support above this loop), and it has to be able to
            # read `reactions_this_card`, which does not exist until a
            # resolution has run. C# does the same at KleeElementalHooks.
            effects.klee_personal_companion_spark(state, card)
    # THE AUTOMATIC POWER FLOOR GRANT USED TO LIVE HERE. Deleted by the
    # Fanfare rework (2026-07-28, Track B, RULED): playing any Power silently
    # raised floor, cap and current by 5 (rares 8), printed on no card and
    # named in no tooltip. A mechanic worth ~4% of her power that the player
    # could not read is a mechanic the player cannot play around.
    #
    # The value moves ONTO THE CARDS as printed keywords -- "Fanfare Cap +X"
    # (raise_fanfare_cap) and "Fanfare +X" (gain_fanfare_floor, rare Powers
    # only). There is deliberately NO card-type branch left in this function:
    # a Power now grants exactly what it prints, the same as every other card
    # type, and that uniformity is the point rather than a side effect.
    if card.kit_card:
        pass                                  # returns to the kit, no pile
    else:
        # CardModel.GetResultPileTypeForCardPlay: a played Power card is
        # REMOVED FROM COMBAT (PileType.None), not exhausted. tier0 used to
        # exhaust it, which would have paid out FeelNoPain and DarkEmbrace on
        # all 11 of Ironclad's Power cards (recon BUG 1).
        dest = "exhaust" if force_exhaust else refpowers.result_pile(state,
                                                                     card)
        if dest == "exhaust":
            refpowers.exhaust_card(state, card)
        elif dest == "discard":
            p.discard_pile.append(card)
    grant_charged_kit(state)
    _settle_phases(state)        # a phased boss dropped to 0 revives BEFORE
    #                              the play loop re-reads state.over
    # Self-damage and Encore overdraw resolve inside a card play rather than
    # the enemy-hit funnel. Give Fairy the same lethal checkpoint, then update
    # HP-threshold relics before the pilot chooses another card.
    _revive_player_if_needed(state)
    if p.relic_effects:
        relics.reevaluate_conditionals(state)


# Every piece of per-card context effects.resolve_card sets. A free play
# resolves an ENTIRE card in the middle of another card's resolution, so each
# of these has to be put back afterwards or the outer card finishes reading
# the inner card's kills, exhausts and repeat request -- a corruption that is
# invisible in results, which is why effects._free_play refuses to resolve
# effects inline and routes here instead. (Its contract docstring names
# fourteen; block_gains_this_card and salon_replacements_this_card are
# resolve_card's too and are saved for the same reason.)
_ABSENT = object()
_FREE_PLAY_CONTEXT = (
    "current_card_companion", "reactions_this_card", "kills_this_card",
    "fatal_kills_this_card", "exhausted_this_card", "block_gains_this_card",
    "salon_replacements_this_card", "detonations_at_card_start",
    "repeat_requested", "target_had_offelement_aura", "target_had_aura",
    "current_attack_bonus",
    "sparks_at_play", "current_x", "current_card_cost",
    # Coverage pass 4's three per-card reads. Same hazard as the rest: a Sly
    # auto-play that discards or gains block in the middle of an outer card
    # would otherwise leave its numbers behind for the outer card to read.
    "block_gained_this_card", "discards_this_card", "last_drawn_type",
    # EB-118's identity context. The saved value is the LIST OBJECT, which is
    # why every writer rebinds instead of clearing in place: a free play that
    # exhausts mid-resolution opens its own list, and the restore below hands
    # the outer card back the one it was reading.
    "exhaust_selection",
    # EB-136 / R210: the play's bound `cardPlay.Target`. A free play is a
    # SECOND `CardPlay` constructed inside the first, with its own target, and
    # `resolve_card`'s `finally` clears the pair on the way out -- so without
    # these two names the outer card would finish its remaining aimed ops
    # unbound, silently reverting to the per-op lowest-HP pick this row exists
    # to kill. Both are saved: `card_aim_bound` carries the distinction between
    # "bound to nothing" and "no play in flight".
    "card_aim", "card_aim_bound")


def resolve_free_play(state: CombatState, card: Card,
                      force_exhaust: bool = False) -> None:
    """CardCmd.AutoPlay -- play `card` with ResourceInfo.EnergySpent = 0.

    Satisfies the contract effects._free_play documents, and is the ONE way
    an effect may play a card: the base game runs an auto-play through the
    same CardModel.OnPlayWrapper as a manual play, so an auto-played card
    fires BeforeCardPlayed/AfterCardPlayed, is recorded by History as a card
    play, and routes to its own result pile.

    NOT ONLY THE COST IS SKIPPED: this enters at _finish_play, below
    play_card's whole head -- so spotlight counting, burst-per-skill-tag
    gain and burst-cast emptying do not run either. Dormant today (no
    roster card auto-plays, and base-game cards have no burst/spotlight),
    but the day a roster card auto-plays a skill_tag card, that card gains
    no burst unless this boundary moves.

    The caller owns the source pile. AutoPlay moves the card into the play
    pile from wherever it is (hand, draw, discard, exhaust), so it must
    already have been removed by the trigger site; there is deliberately no
    hand.remove here.

    Landed 2026-07-27 for ask A4 (CardKeyword.Sly). Before it, this function
    did not exist and _free_play raised UNIMPLEMENTED -- which is why
    Havoc, Cascade and HowlFromBeyond are excluded from the Ironclad sheet.
    They stay excluded: the extractor still cannot read their shapes
    (CardPileCmd.AutoPlayFromDrawPile, a runtime branch, and an out-of-play
    hook), so that anchor is unchanged by this. What DID move is that
    Card.on_exhaust_autoplay and the autoplay_from_draw op are live paths
    now. No committed card sets either, so the roster is unmoved.
    """
    p = state.player
    # Five of these (detonations_at_card_start, repeat_requested,
    # target_had_offelement_aura, target_had_aura, current_attack_bonus)
    # are set by
    # resolve_card rather than declared on CombatState, so before the first
    # card of a fight resolves they do not exist yet -- and the exhaust
    # autoplay sweep fires at TURN END, outside any card. Restoring absence
    # as absence keeps this function from inventing state that the rest of
    # the engine would then read as a resolved card's leftovers.
    saved = [(name, getattr(state, name, _ABSENT))
             for name in _FREE_PLAY_CONTEXT]
    try:
        # The bank as it stands at play time (R39's reading), and cost 0 --
        # EnergySpent is 0 for an auto-play whatever the card's printed
        # cost, so this_cost_zero and zero_cost_attacks_up both see a free
        # card. An X card captures the CURRENT energy without spending it
        # (CapturedXValue = PlayerCombatState.Energy).
        state.sparks_at_play = p.sparks
        state.current_card_cost = 0
        if card.cost == "X":
            state.current_x = p.energy
        state.cards_played_this_turn += 1
        # EB-17, same read as play_card's. An auto-play usually comes from a
        # pile rather than from hand -- the caller has already removed it from
        # wherever it was -- and then reads (-1, False), which is the honest
        # answer: a card the player never held cannot have been played when
        # drawn. A Sly discard IS a hand card, and does carry its context.
        drawn_turn, first_copy = state.drawn_context(card)
        state.drawn_in_hand.pop(id(card), None)
        state.emit("play", card=card.id, cost=0, energy_left=p.energy,
                   free=True, drawn_turn=drawn_turn, first_copy=first_copy)
        _finish_play(state, card, force_exhaust=force_exhaust)
    finally:
        for name, value in saved:
            if value is _ABSENT:
                state.__dict__.pop(name, None)
            else:
                setattr(state, name, value)


def _player_turn(state: CombatState, pilot: Pilot) -> None:
    p = state.player
    state.turn += 1
    # INSTRUMENT ONLY, log-side, no game state read or written (the `round_hp`
    # precedent below). The turn-OPENING sample for the per-turn record in
    # metrics.turn_trajectory: HP before anything this turn touches it, and the
    # block that SURVIVED the enemy -- taken here, above the block clear at the
    # `should_clear_block` line, because that leftover is a different quantity
    # from the block the player ENDS the turn holding (`turn_close` below), and
    # the two wear the same word in every report that conflates them.
    state.emit("turn_open", hp=max(0, state.player.hp), block=state.player.block)
    state.cards_played_this_turn = 0
    for e in state.enemies:
        e.skittish_fired = False     # Skittish latch is per-turn (§10.9)
    state.in_player_turn = True              # StS2 CombatState.CurrentSide
    refpowers.reset_turn_counters(state)
    # Fanfare decay, HERE at the true top of the turn -- before the block
    # clear, the draw, Salon upkeep and every other turn-start generator.
    # Order is a design choice, not an accident: decay eats what was CARRIED
    # OVER, and then this turn's activity builds on the remainder. Applying
    # it after turn-start generation would tax income instead of inventory.
    resources.decay_fanfare(state)
    # StS2 site A (BeforeSideTurnStart) -- BEFORE the block clear and BEFORE
    # the draw. Aggression pulls Attacks out of the discard pile here; running
    # it after the draw would over-fill the hand versus the real game.
    refpowers.side_turn_start_early(state)
    if refpowers.should_clear_block(p):      # Barricade suppresses the clear
        p.block = 0

    state.companion_plays_this_turn = 0          # Blocking Notes' slope
    # NEITHER `replay_next_companion` NOR `companion_cost_delta_this_turn` is
    # cleared here any more: both expire at the END of the turn that wrote
    # them (see `in_player_turn = False` below). X11 first, ratified by R110;
    # X1's accumulator joined it under FLAG-1 (R114) -- "Limit the cost
    # discount to the current turn? Yes." One boundary idiom, used twice.
    state.splash_procs_this_turn = 0             # detonation_splash cap
    state.reactions_this_turn = 0                # Chevreuse predicate window
    state.spotlighted_cards_this_turn = 0        # Ovation / reserve cap
    state.spotlighted_paid_cards_this_turn = 0   # B2: Leading Role's window
    state.spotlight_moved_this_turn = False      # selector-payoff window
    state.prevention_used_this_turn = False      # Kokomi ward latch (§2.4)
    state.encore_spend_draws_this_turn = 0       # Gallery Stirs latch (R85)
    state.cards_created_this_turn = 0            # engine_closure window
    state.charge_reads_this_turn = {}            # EB-78 (2) instrument
    # QUARANTINED (C.KURAGE_MEMORY): the two per-TURN halves of the memory
    # rule. The pulse key is cleared here so a turn where she plays nothing
    # pulses nothing (§2's "a price on a wasted turn"), and the fire latch is
    # cleared here so the one-card-per-turn cap is a turn boundary and not a
    # bank size. `kurage_queue` and `kurage_last_attack_target` are per-FIGHT
    # and deliberately survive this line.
    state.kurage_last_card_type = ""
    state.kurage_fired_this_turn = False

    for enemy in list(state.living_enemies):     # bombs from last turn go off
        if enemy.bombs:
            effects.detonate_bombs(state, enemy)
    _settle_phases(state)
    reactions.tick_auras(state)
    powers.on_turn_start(state, p)
    _settle_phases(state)        # aura ticks / DoT can drop a phased boss;
    #                              without a settle before the over-check, a
    #                              queued bar reads as a WIN
    _revive_player_if_needed(state)             # player DoT can be lethal
    if not p.alive or state.over:
        return
    effects.player_turn_start_triggers(state)
    _settle_phases(state)        # Salon upkeep damages enemies inside the
    #                              triggers -- same hole as above (EB-29a:
    #                              66% of Furina/test_subject wins were
    #                              counterfeit before this settle)
    _revive_player_if_needed(state)             # Salon upkeep can overdraw HP
    if not p.alive or state.over:
        return

    p.energy = refpowers.energy_for_turn(state)      # site C, + Pyre
    # site D, with Hook.ModifyHandDraw folded in (ToolsOfTheTrade and
    # DrawCardsNextTurn). Relic-driven opening-hand bonuses are a different
    # hook and stay where they are.
    refpowers.before_hand_draw(state)                # Hook.BeforeHandDraw
    state.draw(C.CARDS_DRAWN_PER_TURN + refpowers.hand_draw_bonus(p),
               from_hand_draw=True)
    # StS2 sites E/F (AfterPlayerTurnStart, AfterSideTurnStart) -- AFTER the
    # draw. tier0's powers.on_turn_start above is a PRE site; anything that
    # reads the hand or must land post-draw belongs here instead.
    refpowers.player_turn_start_late(state)
    _revive_player_if_needed(state)             # Inferno / Mantle self-damage
    if not p.alive or state.over:
        return
    grant_charged_kit(state)                 # turn-start gains + full-hand defer

    # Combat-side relics (dead branch on the battery). combat_start_* fires
    # once, HERE on turn 1 -- AFTER the block clear / energy reset / draw above,
    # so combat-start block survives the clear and the turn-1-only energy/draw
    # riders stack on the turn's own refill and draw. Per-turn hooks
    # (every_n_turns_*, conditional_power re-eval) run every turn.
    if p.relic_effects:
        if state.turn == 1:
            relics.apply_combat_start(state)
        relics.on_player_turn_start(state, state.turn)

    # Combat-side potions (dead branch on the battery: potions empty). Bounded
    # greedy use-policy at turn start, AFTER the draw/energy/relic setup so a
    # defensive block or an offensive strength lands on this turn's real state.
    if p.potions:
        potions.try_use_potions(state)
        _settle_phases(state)    # an offensive potion can drop a phased boss
        if p.relic_effects:
            # Blood Potion can cross Red Skull's HP threshold after its normal
            # turn-start evaluation and before the first card is chosen.
            relics.reevaluate_conditionals(state)

    # Pass 4 Q1a: Fanfare trajectory snapshot, taken HERE -- after turn-start
    # triggers, Salon upkeep, energy and draw, before the first card -- because
    # that is the state the pilot actually decides in, and the state that
    # determines whether this turn's generation overflows. Report-only (R14).
    if p.fanfare_cap:
        state.emit("fanfare_turn", total=p.fanfare, cap=p.fanfare_cap,
                   floor=p.fanfare_floor,
                   at_cap=p.fanfare >= p.fanfare_cap,
                   at_floor=p.fanfare <= p.fanfare_floor)

    # QUARANTINED (C.KURAGE_MEMORY): PICK B1, the turn-START fire. HERE --
    # after the block clear, the turn-start triggers, the energy refill, the
    # draw and the relic/potion pass, and immediately BEFORE the first card is
    # chosen -- because that is the whole argument for B1: the free card must
    # land in the state the player is planning in, not be tacked onto a turn
    # already spent. It is also the point the Fanfare snapshot above calls
    # "the state the pilot actually decides in", so the two agree.
    if C.KURAGE_MEMORY and C.KURAGE_FIRE_TIMING == "turn_start":
        effects.kurage_fire(state)
        _settle_phases(state)    # a replayed attack can drop a phased boss,
        #                          the same hole the settles above close
        _revive_player_if_needed(state)
        if not p.alive or state.over:
            return

    seen_states: set[tuple] = set()
    while not state.over:
        if state.cards_played_this_turn >= C.MAX_CARDS_PER_TURN:
            state.emit("degeneracy", kind="INFINITE", reason="card_cap")
            break
        snapshot = (tuple(sorted(c.id for c in p.hand)), len(p.draw_pile),
                    len(p.discard_pile), p.energy)
        if snapshot in seen_states:
            state.emit("degeneracy", kind="INFINITE", reason="state_repeat")
            break
        card = pilot(state)
        if card is None:
            break
        seen_states.add(snapshot)
        play_card(state, card)

    # Kokomi §7 engine_closure detector (report-only, R14: diagnostics,
    # never acceptance targets): a turn that CREATED at least as many cards
    # as it consumed while playing several cards is a candidate
    # positive-sum engine cycle. v0 heuristic on purpose — full
    # energy/draw-closure accounting is a later instrument; this flags
    # candidates for eyes-on. Dead branch until a creation op runs.
    if (state.cards_created_this_turn > 0
            and state.cards_created_this_turn
            >= max(1, state.cards_exhausted_this_turn)):
        state.emit("engine_closure",
                   created=state.cards_created_this_turn,
                   consumed=state.cards_exhausted_this_turn,
                   plays=state.cards_played_this_turn)

    # StS2 site I (BeforeSideTurnEndEarly). PlatingPower's own source comment:
    # "We do this in early so that it triggers before end-of-turn damage
    # effects" -- which is precisely what player_turn_end_triggers holds.
    refpowers.before_side_turn_end_early(state)
    effects.player_turn_end_triggers(state)      # Oz, Sparks 'n' Splash, ...
    _settle_phases(state)        # turn-end burst (Sparks 'n' Splash) can
    #                              drop a phased boss
    # Injected Burn/Wither (§10.2): end-of-turn damage while in hand,
    # BLOCKABLE (the real cards' shape) -- fires before the hand flush
    # discards them. Dead branch unless an enemy injected this combat.
    eot_statuses = [c for c in p.hand if c.status_eot_damage]
    for c in eot_statuses:
        dmg = c.status_eot_damage
        blocked = min(p.block, dmg)
        p.block -= blocked
        p.hp -= dmg - blocked
        resources.note_player_hp_loss(state, dmg - blocked)
        state.emit("status_eot_damage", card=c.id, amount=dmg - blocked,
                   blocked=blocked)
    _revive_player_if_needed(state)
    grant_charged_kit(state)     # Salon-tick particles can fill the meter
                                 # at turn end; the Burst's Retain keeps it
    # Burst cards have Retain (principles v1.4): they stay in hand.
    # Ethereal cards (the Spotlight selector) vanish to exhaust instead of
    # discarding -- an unplayed selector must never circulate as loot.
    # `Card.is_ethereal`, not the raw tag: EB-118 added the printed base-card
    # field beside it and all three seams below must read the same door.
    retained = [c for c in p.hand if "burst" in c.tags or c.retain]
    # WellLaidPlans (BeforeFlushLate): single-turn Retain on up to N cards
    # that were about to be flushed. Computed against what WOULD flush, so it
    # can never "retain" a card that was staying anyway.
    would_flush = [c for c in p.hand
                   if "burst" not in c.tags and not c.retain
                   and not c.is_ethereal]
    retained += refpowers.retain_at_flush(state, would_flush)
    ethereal = [c for c in p.hand
                if c.is_ethereal
                and "burst" not in c.tags and not c.retain]
    # Membership must be by IDENTITY: Card is a dataclass, so two copies of
    # the same card compare EQUAL, and a value check here would drop the
    # unretained twin from every pile -- a silent deck-shrink.
    retained_ids = {id(c) for c in retained}
    # EB-17, dead-in-hand half one: everything the flush takes away. Both
    # destinations count -- a card discarded unplayed and an unplayed Ethereal
    # burned to exhaust are the same finding ("it was in hand and it did
    # nothing"), and a RETAINED card is deliberately not here, because it is
    # still in play next turn and is only dead once it finally leaves unplayed
    # or the combat ends on it. Computed against `p.hand` before the rebind
    # below, which is the last moment the flushed cards are enumerable.
    flushed = [c for c in p.hand if id(c) not in retained_ids]
    p.discard_pile.extend(c for c in p.hand
                          if "burst" not in c.tags and not c.retain
                          and not c.is_ethereal
                          and id(c) not in retained_ids)
    p.hand = retained
    for c in flushed:
        turn_drawn, _ = state.drawn_context(c)
        if turn_drawn >= 0:      # DRAWN instances only -- see the emit note
            state.emit("dead_in_hand", card=c.id, drawn_turn=turn_drawn,
                       reason="flush")
    # Rebuild the draw-context map to exactly the hand that survives. This is
    # the sweep that keeps it from accumulating entries for cards an effects.py
    # path pulled out of hand (a discard op, an exhaust op) without passing
    # either of the two release sites combat.py owns.
    state.drawn_in_hand = {id(c): state.drawn_in_hand[id(c)]
                           for c in p.hand if id(c) in state.drawn_in_hand}
    for c in ethereal:
        # DarkEmbrace counts ethereal exhausts instead of drawing on them; the
        # deferred draw is flushed in powers.on_turn_end below, i.e. AFTER this
        # hand flush -- which is the stated reason the source defers it.
        refpowers.exhaust_card(state, c, caused_by_ethereal=True)
    state.in_player_turn = False
    # SAME TURN ONLY (sitting 2026-08-06, family X11). Study Buddy / Duet write
    # one shared `replay_next_companion` counter; an unspent grant now dies with
    # the turn that made it instead of surviving the enemy side and being
    # cleared at the next player turn's open. WRITE-SIDE scoping, chosen for
    # parity: the C# twin is a PowerStackType.Counter whose stacks carry no
    # per-stack metadata, so neither engine can stamp a grant with its turn and
    # filter at spend time -- but both can bound the counter's LIFETIME at the
    # writing turn's end, and ReplayNextCompanionPower.AfterSideTurnEnd already
    # does exactly this. One mechanism, one boundary, both parity twins covered.
    state.replay_next_companion = 0
    # FLAG-1 (R114, Errata Batch 2 item 7): the SAME boundary, for the OTHER
    # mechanism. `companion_cost_delta_this_turn` is additive and uncapped,
    # and its discount used to be cleared at the next player turn's OPEN --
    # so a stack written on turn N was still standing through the enemy side
    # and into turn N+1's opening. It now dies with the turn that wrote it.
    #
    # DISTINCT FROM FLAG-2(ii)'s `cost_override`, and they may not be
    # conflated: two mechanisms, two fixes, one shared boundary idiom.
    #
    # WHAT THIS DOES NOT CLOSE, stated because the fix invites the mistake:
    # the WITHIN-turn free-companion loop survives BY DESIGN. A same-turn
    # bound does not touch a mechanism that accumulates and spends inside one
    # turn -- the same shape X11's errata hit, and the same shape the X1 pin
    # still reports. That loop is governed by the X2 rarity law (R109).
    state.companion_cost_delta_this_turn = 0
    # INSTRUMENT ONLY (pair of `turn_open`): the block standing when the player
    # hands the turn over, which is the quantity a demand curve is read against.
    # A turn that ended by killing the last enemy or by the player dying never
    # reaches here, and metrics records -1 there rather than inventing a zero.
    state.emit("turn_close", block=p.block)
    # INSTRUMENT ONLY (EB-78 (2), the reads-per-turn distribution R188 ruled
    # a watch trigger would need). One sample per completed player turn, taken
    # HERE because the Kurage pulse fires inside player_turn_end_triggers
    # above -- sampling any earlier would systematically drop the one reader
    # that is once-per-turn by construction. Emitted even at zero, because a
    # distribution that silently omits its zeros is not a distribution.
    #
    # WHAT THIS SAMPLE CANNOT SEE, declared rather than discovered at grading
    # time: it shares `turn_close`'s own blind spot -- a turn that ended by
    # killing the last enemy or by the player dying never reaches this line,
    # so the final turn of most fights contributes no sample. That truncation
    # is toward the BUSY end (a killing turn is rarely a quiet one), and any
    # reading of this event states it.
    state.emit("charge_reads_turn",
               total=sum(state.charge_reads_this_turn.values()),
               by_source=dict(state.charge_reads_this_turn))
    powers.on_turn_end(state, p)
    _revive_player_if_needed(state)


def _enemy_turn(state: CombatState, enemy: Enemy) -> None:
    if not enemy.alive:
        return
    # EB-96: a SLEEPING creature is still a side-turn participant. The
    # authority builds `creaturesStartingTurn` with no Asleep filter
    # (CombatManager.cs:443-448); sleep suppresses `TakeTurn` and nothing else
    # (Creature.cs:711-717); AsleepPower itself hangs off
    # `AfterSideTurnEnd(participants.Contains(Owner))`. So the block clear,
    # site A, site F and the turn-end tick all fire on a sleep turn -- an
    # early return above them stalled the sleeper's dot, froze its duration
    # debuffs and left its temporary Strength never reverting. NC-7/R116
    # hoisted Frozen's tick out of this function for exactly this reason; the
    # same shape applies here, one clock at a time.
    #
    # The early return WAS load-bearing for two things, and both are kept
    # below: a sleep turn advances no intent, and it toggles no Nemesis
    # Intangible (the phase respawn opens the stack, and the respawn sleep
    # turn must not immediately close it).
    asleep = enemy.sleep_turns > 0
    if asleep:
        enemy.sleep_turns -= 1
        state.emit("enemy_sleep", enemy=enemy.name)
    enemy.block = 0
    powers.on_turn_start(state, enemy)          # site A: metallicize, dot
    refpowers.enemy_side_turn_start(state, enemy)    # site F: poison
    if not enemy.alive:
        return
    if asleep:
        # Site M for a participant that never took its turn. Mirrors the
        # acting path's `if not enemy.alive: return` above -- a sleeper that
        # died to its own dot reaches neither.
        powers.on_turn_end(state, enemy)
        return
    # Crab Rage (§10.2, gated on the spec field -- inert everywhere else):
    # once, at this enemy's first turn start after any ally has died, apply
    # the buff. Polled here rather than at the death site so one choke point
    # covers every way an ally can die; the at-most-one-turn lag is accepted
    # (§10.3). Applied AFTER the block reset so the block survives into the
    # player's next turn, which is the real power's shape.
    if (enemy.ally_death_buff is not None and not enemy.ally_death_fired
            and any(not e.alive for e in state.enemies if e is not enemy)):
        enemy.ally_death_fired = True
        for pname, amt in (enemy.ally_death_buff.get("powers") or {}).items():
            powers.apply_power(state, enemy, pname, int(amt))
        blk = int(enemy.ally_death_buff.get("block", 0))
        if blk:
            enemy.block += blk
        state.emit("ally_death_trigger", enemy=enemy.name)
    intent = enemy.current_intent()
    kind = intent["kind"]
    # Frozen v2 (v1.5): the enemy still acts, but its action deals -50%
    # damage. NC-7 (R116): acting no longer CONSUMES the freeze -- the timer
    # is spent by the clock at the end of the enemy side, not by the action,
    # so a two-stack freeze halves two actions. Shatter still clears it.
    frozen = enemy.frozen > 0
    if frozen:
        state.emit("frozen_action", enemy=enemy.name, kind=kind,
                   by_companion=enemy.frozen_by_companion)
    state.emit("intent", enemy=enemy.name, kind=kind,
               debuffed=bool(enemy.powers.get("weak", 0)
                             or enemy.powers.get("vulnerable", 0)),
               # A6 v2 (R18): application uptime = intents taken while
               # carrying an elemental aura. ref_ironclad applies
               # nothing, so the baseline's uptime is 0 by construction.
               aura=enemy.aura is not None)

    if kind == "attack":
        # Snapshot before resolving the action. The latch is spent only after
        # the hit loop so a multi-hit intent receives one coherent modifier.
        bomb_suppressed = (
            bool(enemy.bombs) and not enemy.bomb_suppression_spent
        )
        amount = enemy.ramped_amount(intent, state.turn)
        for _ in range(enemy.ramped_times(intent)):
            dmg = powers.modify_damage_dealt(enemy, amount)
            if frozen:
                dmg *= C.FROZEN_DAMAGE_MULT
            # `enemy` is passed as the dealer so Colossus can read ITS
            # Vulnerable (ColossusPower halves only what a Vulnerable attacker
            # lands on its owner).
            dmg = powers.modify_damage_taken(state.player, dmg, enemy)
            dmg = int(dmg)
            block_before = state.player.block
            blocked = min(state.player.block, dmg)
            state.player.block -= blocked
            # Kokomi's prevention ward (kickoff §2.4): after Block, before
            # anything reaches HP — the first unblocked hit each round is
            # prevented up to the ward's stacks, priced as one random
            # draw-pile card through the exhaust funnel (which is itself a
            # Charge event). Dead branch for every player without the
            # power. Its event stream is REPORTED SEPARATELY, not folded
            # into `blocked` and not credited to any axis yet — A4 credit
            # is a metric ruling ask (Encore precedent), not a default.
            prevented = effects.prevent_damage_exhaust(state, dmg - blocked)
            # Encore absorbs after Block, before HP (kickoff §4). Its own
            # event stream credits A4 sustain -- NEVER folded into
            # `blocked` (§2 harness note, Tier 0 binding).
            hp_loss = resources.absorb_into_encore(
                state, dmg - blocked - prevented, "enemy_hit")
            state.player.hp -= hp_loss
            resources.note_player_hp_loss(state, hp_loss)
            # Combat-side relic on_first_hp_loss_draw (dead branch on the
            # battery). Fires at most once per combat, on real HP loss.
            if hp_loss > 0 and state.player.relic_effects:
                relics.note_hp_loss(state)
            # `incoming` is the hit as it ARRIVES -- after the dealer's own
            # Strength/Weak/Frozen and after the player's Vulnerable, before
            # block, before the Kokomi ward and before Encore. It is the
            # numerator of the incoming-attacks-per-turn instrument; `amount`
            # (HP actually lost) is what SURVIVED three mitigation layers and
            # cannot answer "how hard did this turn hit".
            state.emit("player_hit", amount=hp_loss, blocked=blocked,
                       block_before=block_before, incoming=dmg)
            # Painful Stabs (§10.9 promotion, R128): every UNBLOCKED hit adds
            # a Wound to the discard, per hit of a multi-hit intent. Block is
            # the gate -- the ward and Encore absorb after it and do not
            # prevent the Wound (dossier :191-200: "every unblocked hit").
            stabs = enemy.powers.get("painful_stabs", 0)
            if stabs and dmg - blocked > 0:
                from tier0.engine import statuses    # late import, as inject
                for _s in range(stabs):
                    state.player.discard_pile.append(
                        statuses.make_status("wound"))
                state.emit("painful_stabs", enemy=enemy.name, count=stabs)
            # AfterDamageReceived fires per HIT, not per intent -- FlameBarrier
            # retaliates against every hit of a multi-hit attack. Inferno and
            # Rupture are silent here: both require CurrentSide == Owner.Side,
            # and state.in_player_turn is False.
            refpowers.on_damage_received(state, state.player,
                                         unblocked=dmg - blocked, dealer=enemy,
                                         powered_attack=True)
            if not state.player.alive:
                # Fairy in a Bottle (dead branch on the battery: potions
                # empty). Passive revive at the lethal hit; if it saves the
                # player the turn continues and a later hit of a multi-hit
                # intent can still kill (the fairy is spent).
                if not _revive_player_if_needed(state):
                    return
            if not enemy.alive:
                break               # FlameBarrier can kill the dealer
        if bomb_suppressed:
            enemy.bomb_suppression_spent = True
            state.emit("bomb_suppression_spent", enemy=enemy.name)
    elif kind == "block":
        enemy.block += intent["amount"]
    elif kind == "buff":
        powers.apply_power(state, enemy, intent.get("power", "strength"),
                           intent["amount"])
    elif kind == "debuff":
        # applier=enemy: Vicious must NOT draw off an enemy-applied Vulnerable.
        powers.apply_power(state, state.player, intent["power"],
                           intent["amount"], applier=enemy)
    elif kind == "summon":
        for spawn in intent["wave"]:
            # is_minion=True: the game applies MinionPower to summoned adds
            # (gas-bomb/guardbot/parafright/tough-egg dossiers), and NC-7
            # alpha (Q13 / R117) keys Frozen's boss-room substitution on
            # exactly that fact. Set beside counts_for_fatal=False, which
            # already mirrors the same secondary-enemy concept's death rule.
            state.enemies.append(Enemy(hp=spawn["hp"], max_hp=spawn["hp"],
                                       name=spawn.get("name", "add"),
                                       intents=spawn["intents"],
                                       is_minion=True,
                                       counts_for_fatal=False))
    elif kind == "inject":
        # §10.2 (RATIFIED 2026-07-23): shuffle status cards into a player
        # pile. Default pile is the discard (the common StS shape); "draw"
        # inserts at a random depth via the combat rng; "hand" respects
        # MAX_HAND_SIZE with overflow to discard (base-game overflow rule).
        from tier0.engine import statuses     # late import, engine-internal
        pile = intent.get("pile", "discard")
        p = state.player
        for _ in range(intent.get("count", 1)):
            card = statuses.make_status(intent["status"])
            if pile == "draw":
                p.draw_pile.insert(
                    state.rng.randrange(len(p.draw_pile) + 1), card)
            elif pile == "hand":
                if len(p.hand) < C.MAX_HAND_SIZE:
                    p.hand.append(card)
                else:
                    p.discard_pile.append(card)
            elif pile == "discard":
                p.discard_pile.append(card)
            else:
                raise ValueError(f"unknown inject pile {pile!r}")
        state.emit("status_injected", enemy=enemy.name,
                   status=intent["status"], count=intent.get("count", 1),
                   pile=pile)
    elif kind == "heal":
        # §10.2: enemy self-heal (Knowledge Demon's Ponder), capped at max.
        amt = min(int(intent["amount"]), enemy.max_hp - enemy.hp)
        if amt > 0:
            enemy.hp += amt
        state.emit("enemy_heal", enemy=enemy.name, amount=max(0, amt))
    else:
        raise ValueError(f"unknown intent kind {kind!r}")

    enemy.advance_intent()
    powers.on_turn_end(state, enemy)
    # Nemesis (§10.9 promotion, R128): at the end of every ACTING enemy turn
    # the power toggles Intangible 1 on its owner -- applied on odd toggles,
    # removed on even (dossier :205-218). The phase opens Intangible
    # (_settle_phases applies stack 1 at the revive, and the respawn sleep
    # turn returns above before reaching this), so the first acting turn is
    # capped, the second is open, alternating -- the dossier's turn table.
    # Enemy-side Intangible never auto-decays (the after_enemy_side_turn_end
    # decrement is player-only), so this toggle is the stack's one owner.
    if enemy.alive and enemy.powers.get("nemesis", 0):
        if enemy.powers.get("intangible", 0):
            del enemy.powers["intangible"]
        else:
            enemy.powers["intangible"] = 1
        state.emit("nemesis_toggle", enemy=enemy.name,
                   intangible=bool(enemy.powers.get("intangible", 0)))


def surface_innate(draw_pile: list) -> None:
    """Innate (R37): innate cards surface to the TOP of the shuffled draw
    pile, so the first hand contains them (base-game semantics; hand-size
    overflow degrades to "drawn first", which is also base-game). Order
    among innate cards stays shuffle-relative -- no hidden second sort.

    PERFECT FIT DOES NOT RIDE THIS SITE (EB-85 divergence 5). Its text --
    "whenever this would be shuffled into your Draw Pile, place it on the top
    instead" -- reads like it covers both shuffles, but the implementation
    refuses the opening one outright:

        public override void ModifyShuffleOrder(Player player,
                                                List<CardModel> cards,
                                                bool isInitialShuffle)
        {
            if (!isInitialShuffle && cards.Contains(base.Card)) { ... }
        }

    tier0 hoisted it here as well, which handed the enchantment a free Innate
    -- a strictly stronger card than the game's. The mid-combat reshuffle is
    the only place it applies (state.shuffle_discard_into_draw).
    """
    innate = [c for c in draw_pile if c.innate]
    if innate:
        draw_pile[:] = innate + [c for c in draw_pile if not c.innate]


def _run_rounds(state: CombatState, pilot: Pilot) -> None:
    while not state.over and state.turn < C.MAX_TURNS:
        _player_turn(state, pilot)
        if not state.over:
            for enemy in list(state.enemies):
                _enemy_turn(state, enemy)
                _settle_phases(state)    # FlameBarrier retaliation can drop a
                #                          phased boss mid-enemy-round
                if state.over:
                    break
            # AfterSideTurnEnd(side == Enemy): the once-per-round enemy tick.
            # This is where FlameBarrier is removed and Colossus decrements --
            # doing either at the PLAYER's turn end instead makes Flame Barrier
            # do literally nothing.
            refpowers.after_enemy_side_turn_end(state)
            # NC-7 (R116, Errata Batch 2 item 5): Frozen's clock. The mod's
            # FrozenPower ticks in `AfterSideTurnEnd(side == Enemy)`, and
            # R116 ruled that timer canonical, so this is the sim's mirror of
            # the same hook -- one decrement per enemy side, for every enemy
            # that carries the status.
            #
            # UNCONDITIONAL, deliberately, because the mod's is: it does not
            # ask whether the enemy acted. A sleeping enemy loses its freeze,
            # and a freeze applied after an enemy has already acted is spent
            # by this same side-end. Making it conditional would be a second
            # ruling, not an implementation detail of this one.
            for enemy in state.enemies:
                if enemy.frozen > 0:
                    enemy.frozen -= 1
        # INSTRUMENT ONLY, log-side, no game state read or written: the
        # authoritative end-of-round player HP, for the HP-trajectory half of
        # Kokomi's stability instrument (R51 / D5). It is sampled HERE rather
        # than derived in metrics.py from `player_hit` + `heal`, because HP also
        # moves through paths that emit neither -- effects.py's block-ignoring
        # self-damage, the Encore shortfall in resources.py, and the Fairy
        # revive -- so a derived trajectory would be quietly wrong on exactly
        # the cards a stability reading is about. `state.player.hp` is the only
        # thing that cannot disagree with itself.
        #
        # The `if not state.over` restructure above is control-flow-identical to
        # the `break` it replaced (the loop condition re-tests `state.over`);
        # it exists so the final, possibly lethal, round is sampled too.
        state.emit("round_hp", hp=max(0, state.player.hp))


def run_fight(player: Player, enemies: list[Enemy], pilot: Pilot,
              seed: int) -> CombatState:
    state = CombatState(player=player, enemies=enemies,
                        rng=random.Random(seed),
                        # Dedicated stream, offset 4e9 (see CombatState and
                        # understudy/rng.py's offset registry): the X14(b)
                        # hand-full selector fallback must not advance the
                        # main combat stream and renumber existing seeds.
                        selector_rng=random.Random(seed + 4 * 10 ** 9))
    # Per-combat resources (v1.6: the reset IS the safety on unbounded
    # Encore). Spotlight designation likewise re-aims fresh each combat.
    player.encore = 0
    player.fanfare = 0
    # Fanfare floors and cap grants are per-COMBAT, like every other Furina
    # resource: a card is replayed each fight and re-earns what it prints.
    #
    # RESTORE FROM A SNAPSHOT, not by subtracting the floor. The old rewind
    # (`fanfare_cap -= fanfare_floor`) was exact only while gain_fanfare_floor
    # was the sole writer of both fields and always moved them together. The
    # Fanfare rework broke that on both sides: raise_fanfare_cap moves the cap
    # alone, and the Hyperbeam's floor drop moves the floor alone and
    # DOWNWARD -- which under the old line would have ADDED ceiling on the way
    # out of every fight it was played in. See Player.fanfare_cap_base.
    #
    # EB-97: re-derive the base term from LIVE max HP first. tier05 rebuilds
    # the Player from the sheet and only THEN assigns the run's real max HP
    # (`tier05/model.py`), so without this the whole run would fight on the
    # printed-HP ceiling -- the deviation from LAW.md:189 the mod never had.
    sync_fanfare_cap_to_max_hp(player)
    player.fanfare_cap = player.fanfare_cap_base
    player.fanfare_floor = 0
    player.charge = 0            # Kokomi: the meter is per-combat (§2.1)
    # QUARANTINED (C.KURAGE_MEMORY + C.KURAGE_ALWAYS_ON): THE BASE KIT.
    # [USER], 2026-08-29 -- "make Bake-Kurage part of the base kit (always on)
    # rather than a separate card". The jellyfish is installed HERE, at true
    # fight start, beside the other per-combat resources, and it never
    # expires: `kurage_summon` stops being a countdown, or even a summon, and
    # becomes a fact about Kokomi. It sits on the same line as the meter it
    # spends because the two now have the same lifetime -- one fight.
    #
    # The pulse gate in `player_turn_end_triggers` reads this power, so
    # installing it here is also what makes the pulse fire at EVERY turn end
    # from turn 1, with no card played and nothing summoned.
    #
    # Its OWN event, not `summon_kurage`: nothing summoned it, and a reader
    # counting summons must not see one that no card paid for.
    if C.KURAGE_MEMORY and C.KURAGE_ALWAYS_ON \
            and player.character_id == "kokomi":
        player.powers["kurage_summon"] = 1
        state.emit("kurage_base_kit", persistent=True)
    player.spotlight = None
    state.rng.shuffle(player.draw_pile)
    surface_innate(player.draw_pile)
    # Per-combat gates that are pure functions of the built deck. Both are
    # False/off for every character and every battery deck, so both are dead
    # branches everywhere except a run that met the event that grants them.
    state.hand_play_cap = any(c.status_play_cap for c in player.draw_pile)
    for c in player.draw_pile:
        c.enchant_played_this_combat = False
        # EB-83: `SetThisCombat` expires at end of combat, so the absolute
        # cost a randomiser wrote last fight must not survive into this one.
        # Cleared on the same walk rather than a second pass, for the same
        # reason the two placements share `surface_innate`.
        c.cost_set_this_combat = None
    # Combat-side relics: clear per-combat counters at true fight start. Dead
    # branch on the battery (relic_effects empty); the combat_start_* effects
    # themselves fire on the first player turn (see _player_turn).
    if player.relic_effects:
        relics.reset_combat(state)
    # Bound so refpowers can recover the dealer/applier identity that
    # effects.py cannot pass; try/finally so a raising fight never leaks a
    # stale state into the next one.
    outer = refpowers.bind(state)
    try:
        _run_rounds(state, pilot)
    finally:
        refpowers.bind(outer)
    won = bool(state.player.alive) and not state.living_enemies
    # EB-17, dead-in-hand half two: the cards the combat ENDED on. A fight that
    # ends inside a player turn never reaches the hand flush, and a Retained
    # card can sit in hand for the whole fight and never meet one either, so
    # without this half the instrument would silently under-count exactly the
    # cards it exists to find. EMIT-ONLY and after `won` is decided, so nothing
    # here can move the result.
    for c in state.player.hand:
        turn_drawn, _ = state.drawn_context(c)
        if turn_drawn >= 0:
            state.emit("dead_in_hand", card=c.id, drawn_turn=turn_drawn,
                       reason="fight_end")
    if won and "heal_after_won_fight" in state.player.relic_hooks:
        # Burning Blood (ruling 1): post-fight, can't affect combat —
        # counts toward the A4 healing metric, not hp_left.
        state.emit("heal", amount=C.BURNING_BLOOD_HEAL, post_fight=True)
    # D8 telemetry (salon UI sprint, 2026-07-28). EMIT-ONLY. Guarded on
    # fanfare_cap, the same Furina marker the fanfare_turn snapshot uses --
    # encore is hers alone in content, and a zero-valued row in every Klee log
    # would be noise pretending to be data. Separate from fight_end rather
    # than a key on it: fight_end is every character's event, and a
    # character-specific field on a shared row is how a metric ends up being
    # read for a character that never had it.
    if state.player.fanfare_cap:
        state.emit("encore_end", encore=state.player.encore,
                   members=len(state.player.salon), won=won)
    state.emit("fight_end", won=won, turns=state.turn,
               hp_left=max(0, state.player.hp))
    return state
