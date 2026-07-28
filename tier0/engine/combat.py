"""Turn loop (spec §3/§4.5). One function: run_fight.

Player turn: bombs detonate -> auras tick -> power hooks -> draw + energy ->
pilot plays until done -> discard hand -> power decay.
Enemy turns: scripted intents, no AI. Asleep enemies skip; frozen enemies
act at -50% damage (Frozen v2, principles v1.5).
"""

from __future__ import annotations

import random
from typing import Callable

from tier0 import constants as C
from tier0.engine import (effects, potions, powers, reactions, refpowers,
                          relics, resources)
from tier0.engine.state import (Card, CombatState, Enemy, Player,
                                remove_instance)

# A pilot is a callable: (state) -> Card | None (None = end turn).
Pilot = Callable[[CombatState], Card | None]


def spark_threshold(state: CombatState) -> int:
    # True Spark Knight: free attack at 2 sparks instead of 3.
    return max(1, C.SPARKS_FOR_FREE_ATTACK
               - state.player.powers.get("spark_threshold_down", 0))


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
            e.powers = {}
            e.aura = None
            e.aura_turns_left = 0
            e.bombs = []
            e.frozen = False
            e.sleep_turns = 0
            if not e.phases:
                e.counts_for_fatal = True     # the last bar is a real death
            state.emit("phase_change", enemy=e.name, hp=e.hp,
                       remaining=len(e.phases))


def card_playable(state: CombatState, card: Card) -> bool:
    if card.type == "status":
        return False        # §10.2 injected statuses: unplayable clogs
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
    # No Fanfare playability gate: Fanfare is read, never spent (F-A4).
    return card_cost(state, card) <= state.player.energy


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
    if (card.type == "attack"
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
    if (card.type == "attack" and cost == 0
            and p.sparks >= spark_threshold(state)
            and card.cost != 0 and card.cost != "X"):
        p.sparks -= spark_threshold(state)
        state.emit("sparks_spent")
    if card.cost == "X":
        state.current_x = cost                # X = energy actually spent
    state.current_card_cost = cost
    p.energy -= cost
    if card.encore_cost:
        resources.spend_encore(state, card.encore_cost)   # gated playable
    remove_instance(p.hand, card)
    state.cards_played_this_turn += 1
    state.emit("play", card=card.id, cost=cost, energy_left=p.energy)
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
        if p.spotlight == p.character_id:
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
            n = p.powers.get("spotlight_draw", 0)
            if n:
                state.draw(n)
                state.emit("extra_draw", amount=n)
            n = p.powers.get("spotlight_encore_first", 0)
            if n:
                resources.gain_encore(state, n)
        n = p.powers.get("spotlight_encore", 0)
        if n:
            resources.gain_encore(state, n)
    if card.requires == "burst_energy_full":
        p.burst_energy = 0                    # playing the Burst empties it
        state.emit("burst_cast", card=card.id)
    if p.burst_max and "skill_tag" in card.tags:
        resources.gain_burst(state, C.BURST_PER_SKILL_TAG, "skill_tag")
    _finish_play(state, card)


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
    replays = 1
    if card.is_companion:
        state.companions_played.append(card.id)
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
    # OneTwoPunch resolves the play COUNT once, but Before/AfterCardPlayed fire
    # per play index -- so a doubled attack pays Rage twice, counts twice for
    # Juggling, and burns two FreeAttack stacks.
    replays += refpowers.extra_replays(state, card)
    for _ in range(replays):
        snap = refpowers.before_card_played(state, card)
        effects.resolve_card(state, card)
        refpowers.after_card_played(state, card, snap)
    # Constellation grant (F-A3): playing a POWER permanently raises the
    # Fanfare floor by rarity. Fires AFTER resolution so a power that also
    # grants a floor outright does not double-count against its own read,
    # and once per card rather than once per replay -- a doubled Power is
    # still one performance the audience remembers.
    if card.type == "power":
        resources.gain_fanfare_floor(
            state,
            C.FANFARE_FLOOR_PER_POWER_RARE if card.rarity == "rare"
            else C.FANFARE_FLOOR_PER_POWER,
            f"power:{card.id}")
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
# twelve; block_gains_this_card and salon_replacements_this_card are
# resolve_card's too and are saved for the same reason.)
_ABSENT = object()
_FREE_PLAY_CONTEXT = (
    "current_card_companion", "reactions_this_card", "kills_this_card",
    "fatal_kills_this_card", "exhausted_this_card", "block_gains_this_card",
    "salon_replacements_this_card", "detonations_at_card_start",
    "repeat_requested", "target_had_offelement_aura", "current_attack_bonus",
    "sparks_at_play", "current_x", "current_card_cost",
    # Coverage pass 4's three per-card reads. Same hazard as the rest: a Sly
    # auto-play that discards or gains block in the middle of an outer card
    # would otherwise leave its numbers behind for the outer card to read.
    "block_gained_this_card", "discards_this_card", "last_drawn_type")


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
    # Four of these (detonations_at_card_start, repeat_requested,
    # target_had_offelement_aura, current_attack_bonus) are set by
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
        state.emit("play", card=card.id, cost=0, energy_left=p.energy,
                   free=True)
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

    state.companion_cost_delta_this_turn = 0     # Friendly Visit expires
    state.replay_next_companion = 0              # Study Buddy expires
    state.splash_procs_this_turn = 0             # detonation_splash cap
    state.reactions_this_turn = 0                # Chevreuse predicate window
    state.spotlighted_cards_this_turn = 0        # Ovation / reserve cap
    state.spotlighted_paid_cards_this_turn = 0   # B2: Leading Role's window
    state.spotlight_moved_this_turn = False      # selector-payoff window
    state.prevention_used_this_turn = False      # Kokomi ward latch (§2.4)
    state.encore_spend_draws_this_turn = 0       # Gallery Stirs latch (R85)
    state.cards_created_this_turn = 0            # engine_closure window

    for enemy in list(state.living_enemies):     # bombs from last turn go off
        if enemy.bombs:
            effects.detonate_bombs(state, enemy)
    _settle_phases(state)
    reactions.tick_auras(state)
    powers.on_turn_start(state, p)
    _revive_player_if_needed(state)             # player DoT can be lethal
    if not p.alive or state.over:
        return
    effects.player_turn_start_triggers(state)
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
    retained = [c for c in p.hand if "burst" in c.tags or c.retain]
    # WellLaidPlans (BeforeFlushLate): single-turn Retain on up to N cards
    # that were about to be flushed. Computed against what WOULD flush, so it
    # can never "retain" a card that was staying anyway.
    would_flush = [c for c in p.hand
                   if "burst" not in c.tags and not c.retain
                   and "ethereal" not in c.tags]
    retained += refpowers.retain_at_flush(state, would_flush)
    ethereal = [c for c in p.hand
                if "ethereal" in c.tags
                and "burst" not in c.tags and not c.retain]
    # Membership must be by IDENTITY: Card is a dataclass, so two copies of
    # the same card compare EQUAL, and a value check here would drop the
    # unretained twin from every pile -- a silent deck-shrink.
    retained_ids = {id(c) for c in retained}
    p.discard_pile.extend(c for c in p.hand
                          if "burst" not in c.tags and not c.retain
                          and "ethereal" not in c.tags
                          and id(c) not in retained_ids)
    p.hand = retained
    for c in ethereal:
        # DarkEmbrace counts ethereal exhausts instead of drawing on them; the
        # deferred draw is flushed in powers.on_turn_end below, i.e. AFTER this
        # hand flush -- which is the stated reason the source defers it.
        refpowers.exhaust_card(state, c, caused_by_ethereal=True)
    state.in_player_turn = False
    powers.on_turn_end(state, p)
    _revive_player_if_needed(state)


def _enemy_turn(state: CombatState, enemy: Enemy) -> None:
    if not enemy.alive:
        return
    if enemy.sleep_turns > 0:
        enemy.sleep_turns -= 1
        state.emit("enemy_sleep", enemy=enemy.name)
        return
    enemy.block = 0
    powers.on_turn_start(state, enemy)          # site A: metallicize, dot
    refpowers.enemy_side_turn_start(state, enemy)    # site F: poison
    if not enemy.alive:
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
    # damage. Consumed by acting (or by Shatter before this turn).
    frozen = enemy.frozen
    if frozen:
        enemy.frozen = False
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
        for _ in range(intent.get("times", 1)):
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
                state, dmg - blocked - prevented)
            state.player.hp -= hp_loss
            resources.note_player_hp_loss(state, hp_loss)
            # Combat-side relic on_first_hp_loss_draw (dead branch on the
            # battery). Fires at most once per combat, on real HP loss.
            if hp_loss > 0 and state.player.relic_effects:
                relics.note_hp_loss(state)
            state.emit("player_hit", amount=hp_loss, blocked=blocked,
                       block_before=block_before)
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
            state.enemies.append(Enemy(hp=spawn["hp"], max_hp=spawn["hp"],
                                       name=spawn.get("name", "add"),
                                       intents=spawn["intents"],
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


def surface_innate(draw_pile: list) -> None:
    """Innate (R37): innate cards surface to the TOP of the shuffled draw
    pile, so the first hand contains them (base-game semantics; hand-size
    overflow degrades to "drawn first", which is also base-game). Order
    among innate cards stays shuffle-relative -- no hidden second sort."""
    innate = [c for c in draw_pile if c.innate]
    if innate:
        draw_pile[:] = innate + [c for c in draw_pile if not c.innate]


def _run_rounds(state: CombatState, pilot: Pilot) -> None:
    while not state.over and state.turn < C.MAX_TURNS:
        _player_turn(state, pilot)
        if state.over:
            break
        for enemy in list(state.enemies):
            _enemy_turn(state, enemy)
            _settle_phases(state)    # FlameBarrier retaliation can drop a
            #                          phased boss mid-enemy-round
            if state.over:
                break
        # AfterSideTurnEnd(side == Enemy): the once-per-round enemy tick. This
        # is where FlameBarrier is removed and Colossus decrements -- doing
        # either at the PLAYER's turn end instead makes Flame Barrier do
        # literally nothing.
        refpowers.after_enemy_side_turn_end(state)


def run_fight(player: Player, enemies: list[Enemy], pilot: Pilot,
              seed: int) -> CombatState:
    state = CombatState(player=player, enemies=enemies,
                        rng=random.Random(seed))
    # Per-combat resources (v1.6: the reset IS the safety on unbounded
    # Encore). Spotlight designation likewise re-aims fresh each combat.
    player.encore = 0
    player.fanfare = 0
    # Constellation floors are per-COMBAT, like every other Furina resource:
    # a Power is replayed each fight and re-earns its grant. The cap must be
    # rewound with them or it ratchets upward all run -- `player` is one
    # object reused across every fight, so a leak here would silently inflate
    # the ceiling fight after fight. Subtracting the accumulated floor is
    # exact rather than approximate: gain_fanfare_floor raises cap and floor
    # by the SAME n every time, and it is the only writer of either.
    player.fanfare_cap -= player.fanfare_floor
    player.fanfare_floor = 0
    player.charge = 0            # Kokomi: the meter is per-combat (§2.1)
    player.spotlight = None
    state.rng.shuffle(player.draw_pile)
    surface_innate(player.draw_pile)
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
    if won and "heal_after_won_fight" in state.player.relic_hooks:
        # Burning Blood (ruling 1): post-fight, can't affect combat —
        # counts toward the A4 healing metric, not hp_left.
        state.emit("heal", amount=C.BURNING_BLOOD_HEAL, post_fight=True)
    state.emit("fight_end", won=won, turns=state.turn,
               hp_left=max(0, state.player.hp))
    return state
