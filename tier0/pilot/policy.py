"""Rule-based greedy pilot (spec §6).

1. If lethal is playable this turn, play toward it.
2. Else if incoming damage >= BLOCK_PANIC_THRESHOLD of remaining HP,
   prioritize block until covered.
3. Else weighted scoring per pilots/*.yaml.

Deliberately dumb; both Klee and reference decks use the same pilot.
"""

from __future__ import annotations

from typing import Optional

from tier0 import constants as C
from tier0.engine import effects, powers, resources
from tier0.engine.combat import card_cost, card_playable
from tier0.engine.state import Card, CombatState


def _places_bombs(card: Card) -> bool:
    return any(fx["op"] == "place_bomb" for fx in card.effects)


def make_pilot(weights: dict):
    def pilot(state: CombatState) -> Optional[Card]:
        playable = [c for c in state.player.hand if card_playable(state, c)]
        if not playable:
            return None

        # State cannot change while this decision is being made, and every
        # valuation below is a pure reader of it -- so damage, block and the
        # incoming-damage estimate are computed ONCE per playable card and
        # reused by the lethal check, the scorer and the regret log. Those
        # three used to recompute the same numbers independently, which made
        # _expected_damage the hottest function in the whole simulator.
        incoming = _incoming_damage(state)
        dmg = [_expected_damage(state, c) for c in playable]
        blk = [_block_value(state, c, incoming) for c in playable]

        lethal = _lethal_card(state, playable, dmg)
        if lethal is not None:
            return lethal

        if (incoming >= C.BLOCK_PANIC_THRESHOLD * max(1, state.player.hp)
                and state.player.block < incoming):
            blockers = [c for c in playable if _raw_block(state, c) > 0]
            if blockers:
                return max(blockers, key=lambda c: _raw_block(state, c))

        scored = [(_score(state, c, weights, dmg[i], blk[i]), -i, c)
                  for i, c in enumerate(playable)]
        best_score, best_neg_i, best = max(scored, key=lambda t: t[:2])
        if best_score <= 0:
            return None
        # Bomb sequencing: attacks resolve BEFORE new placements, so this
        # turn's attacks don't pop bombs placed this turn (forfeiting
        # next-turn detonation + Pounding Surprise sparks).
        if _places_bombs(best):
            attacks = [(s, i, c) for s, i, c in scored
                       if c.type == "attack" and s > 0]
            if attacks:
                _, best_neg_i, best = max(attacks, key=lambda t: t[:2])
        # NOT a rule here: "bank Charge before playing a Charge reader." The
        # v0.4 W1 arm implemented exactly that (same shape as the bomb rule)
        # and MEASURED WORSE -- priest act-1 33% -> 27% over 500 realistic
        # runs, commander flat. Demoting a damage play to a setup play costs
        # tempo in precisely the act-1 fights that kill her, and the bank is
        # deep enough by the time a reader matters. Binding null result;
        # documented in docs/archive/kokomi-v0.4-report.md so it is not retried.
        _log_regret(state, best, -best_neg_i, playable, dmg, blk)
        return best

    return pilot


def _immediate_value(state: CombatState, card: Card) -> float:
    return _expected_damage(state, card) + _block_value(state, card)


def _log_regret(state: CombatState, chosen: Card, chosen_i: int,
                playable: list[Card], dmg: list[float],
                blk: list[float]) -> None:
    """Spec §6 pilot_regret: was a strictly-better single play available?
    'Strictly better' = higher immediate value (damage + effective block)
    at no greater cost. Sanity instrument, not a target — no rng used, so
    determinism is preserved.

    `dmg`/`blk` are the caller's per-playable valuations, positionally
    aligned with `playable` (see pilot()); their sum IS _immediate_value.
    `chosen_i` is passed rather than looked up because Card is a value-
    equality dataclass -- `playable.index` would find the first EQUAL card,
    not this one."""
    chosen_val = dmg[chosen_i] + blk[chosen_i]
    chosen_cost = card_cost(state, chosen)
    for i, other in enumerate(playable):
        if other is chosen:
            continue
        if (card_cost(state, other) <= chosen_cost
                and dmg[i] + blk[i] > chosen_val):
            state.emit("pilot_regret", chosen=chosen.id, better=other.id)
            return


def _est(state: CombatState, val, default: int = 0) -> float:
    """Estimate a possibly-formulaic amount for scoring purposes.

    Every runtime-computed amount string a pool row can carry must either
    be estimated here or fall to `default` -- raw arithmetic on the field
    is how an X-amount card crashed every tier05 run it was drafted into
    (Malaise, first post-pass-6 measurement)."""
    if isinstance(val, (int, float)):
        return val
    if val in ("X", "X_plus_1"):        # X-cards spend all remaining energy
        return state.player.energy + (1 if val == "X_plus_1" else 0)
    if val == "hand_size":              # known exactly at score time
        return len(state.player.hand)
    if val == "discards_this_card":     # both users discard the rest of the
        return max(len(state.player.hand) - 1, 0)   # hand first (CalcGamble,
    return default                                  # Storm of Steel)


def _active_effects(state: CombatState, effect_list: list[dict]):
    """Yield runtime-formula branches the pilot is explicitly able to read.

    Mid-resolution predicates (reaction_triggered_by_this, killed_target)
    deliberately keep their historic top-level-only valuation. Pure current-
    state Klee predicates are safe to read here, as are the pass-5/pass-6
    Ironclad predicates below.
    """
    for fx in effect_list:
        if fx["op"] == "conditional":
            name = fx["if"]
            if name == "has_spark":
                ready = state.player.sparks > 0
            elif name == "target_has_nonpyro_aura":
                target = effects._default_target(state)
                ready = bool(target and target.aura
                             and target.aura != state.player.element)
            elif name.startswith("target_has_power_"):
                target = effects._default_target(state)
                power = name[len("target_has_power_"):]
                ready = bool(target and target.powers.get(power, 0))
            elif name.startswith("exhaust_pile_at_least_"):
                ready = (len(state.player.exhaust_pile)
                         >= int(name.rsplit("_", 1)[1]))
            elif name == "card_exhausted_this_turn":
                ready = state.cards_exhausted_this_turn > 0
            elif name == "hp_lost_this_turn":
                ready = state.hp_lost_this_turn > 0
            elif name.startswith("fanfare_at_least_"):
                # Same clamp the engine's own predicate uses, so the pilot's
                # forecast of which branch fires cannot disagree with the
                # branch that actually fires (Track C.2 negative floor).
                ready = (resources.readable(state.player)
                         >= int(name.rsplit("_", 1)[1]))
            elif name.startswith("encore_at_least_"):
                ready = (state.player.encore
                         >= int(name.rsplit("_", 1)[1]))
            elif name == "reaction_triggered_this_turn":
                # EB-24p: turn-level counter, known exactly at score time
                # (unlike reaction_triggered_by_this, which is mid-resolution
                # and stays excluded). Same read as the engine's predicate.
                ready = state.reactions_this_turn > 0
            else:
                continue
            branch = fx["then"] if ready else fx.get("else", [])
            yield from _active_effects(state, branch)
        else:
            yield fx


def _expected_damage(state: CombatState, card: Card) -> float:
    total = 0.0
    living = state.living_enemies
    # v0.4 W1 (priest-pilot audit): the flat per-attack bonus the engine folds
    # in at resolution — Bennett's next_attack_up, celestial_gift, the Fanfare
    # term, and Kokomi's Ceremonial Garment Charge read. The pilot used to see
    # NONE of it, so it priced every attack at its printed number and played
    # straight through its own buff windows. Same helper the engine calls, so
    # the estimate cannot drift from what resolves; it is a pure read.
    flat = effects.flat_attack_bonus(state, card, card_cost(state, card))
    for fx in _active_effects(state, card.effects):
        if fx["op"] == "damage":
            if fx.get("target") == "self":
                # HP loss is a cost
                total -= fx["amount"] * C.PILOT_SELF_DAMAGE_COST_WEIGHT
                continue
            n_targets = len(living) if fx.get("target") == "all_enemies" else 1
            times = _est(state, fx.get("times", 1), 1)
            times_formula = fx.get("times_formula")
            if isinstance(times_formula, dict):
                times = effects._calc_amount(state, times_formula, card)
            elif times_formula == "2_plus_sparks":
                times = 2 + state.player.sparks
            amount = (effects._calc_amount(state, fx["amount_formula"], card)
                      if "amount_formula" in fx
                      else _est(state, fx.get("amount", 0)))
            per_hit = powers.modify_damage_dealt(state.player,
                                                 amount)
            rider = fx.get("bonus_per_target_power")
            target = effects._default_target(state)
            if rider and target:
                per_hit += (rider["per"]
                            * target.powers.get(rider["power"], 0))
            if "bonus_formula" in fx:       # detonation / fanfare formulas
                try:
                    per_hit += effects._bonus_formula(state,
                                                      fx["bonus_formula"])
                except ValueError:
                    pass
            # Spotlight empowerment is real damage the pilot should see --
            # this is also what makes it PREFER Spotlighted cards.
            per_hit *= effects.spotlight_mult(state, card)
            # After the Spotlight multiply and before the per-hit tally, which
            # is where the engine folds it in (_deal_damage: spotlight scales
            # the PRINTED number, the flat bonus rides on top, per hit).
            per_hit += flat
            # EB-29t: Intangible caps every hit at INTANGIBLE_DAMAGE_CAP
            # (Nemesis alternates it turn-by-turn) -- price the capped
            # number, per target, so an attack dumped into a closed turn
            # scores what it will actually deal.
            hit_targets = (living if fx.get("target") == "all_enemies"
                           else [effects._default_target(state)])
            hit_targets = [t for t in hit_targets if t is not None]
            if hit_targets:
                total += times * sum(
                    min(per_hit, C.INTANGIBLE_DAMAGE_CAP)
                    if t.powers.get("intangible") else per_hit
                    for t in hit_targets)
            else:
                total += per_hit * times * n_targets
        elif fx["op"] == "place_bomb":
            total += fx["bomb_damage"] * _est(state, fx.get("amount", 1), 1)
        elif (fx["op"] == "apply_power"
              and fx.get("power") == "sparks_n_splash"):
            # The Burst payoff: stacks x 4 hits x 5 dmg over coming turns.
            total += (fx["amount"] * C.SPARKS_N_SPLASH_HITS
                      * C.SPARKS_N_SPLASH_HIT_DMG
                      * C.PILOT_FUTURE_DAMAGE_DISCOUNT)
        elif fx["op"] == "summon_kurage":
            # v0.4: the jellyfish's pulses are real damage arriving over the
            # coming turns, same futurity discount as the Burst above. Without
            # this the pilot prices Bake-Kurage at its +1 Charge alone and
            # never fields the summon the whole O4 arm rests on -- the
            # DECISIONS-53 selector lesson, which this pool has already paid
            # for once. The bank read is priced at the CURRENT bank: the
            # pilot cannot see its own future accrual, so this understates a
            # late-fight summon and that is the safe direction to be wrong.
            turns = _est(state, fx.get("amount", C.KURAGE_DURATION),
                         C.KURAGE_DURATION)
            per_pulse = (C.KURAGE_PULSE_BASE
                         + state.player.charge * C.KURAGE_PULSE_PER_CHARGE)
            total += turns * per_pulse * C.PILOT_FUTURE_DAMAGE_DISCOUNT
        elif fx["op"] == "detonate":
            # Early detonation realizes bomb damage now but forfeits the
            # next-turn detonation it would get anyway — value it only
            # when the target would die this turn (review ruling #6).
            for e in living:
                pending = sum(b.damage for b in e.bombs)
                if pending and pending >= e.hp + e.block:
                    total += pending
                if fx.get("target") != "all_enemies":
                    break
    # Shatter (v1.5): an attack hitting the frozen default target adds
    # bonus damage (and thaws it — the tradeoff vs keeping the -50%).
    if (total > 0 and card.type == "attack" and living
            and min(living, key=lambda e: e.hp).frozen):
        total += C.SHATTER_DAMAGE
    return total


def _estimated_exhausts(state: CombatState, card: Card) -> int:
    """Pre-play estimate for SecondWind's exhausted_this_card multiplier."""
    for fx in card.effects:
        if fx.get("op") != "exhaust_from":
            continue
        pool = [c for c in state.player.hand
                if c is not card and not c.kit_card]
        if fx.get("filter") == "non_attack":
            pool = [c for c in pool if c.type != "attack"]
        elif fx.get("filter") == "status":
            pool = [c for c in pool if c.rarity == "status"]
        return len(pool) if fx.get("amount") == "all" else min(
            len(pool), int(fx.get("amount", 1)))
    return 0


def _raw_block(state: CombatState, card: Card) -> float:
    total = 0.0
    for fx in _active_effects(state, card.effects):
        if fx["op"] != "block":
            continue
        amount = (effects._calc_amount(state, fx["amount_formula"], card)
                  if "amount_formula" in fx else fx["amount"])
        # F-B1: Block carries the same scaling rider damage does, so the
        # pilot has to read it or it prices a Fanfare-scaled blocker at its
        # printed number and blocks with the wrong card. Same helper the
        # engine calls, so the estimate cannot drift from what resolves.
        if "bonus_formula" in fx:
            amount += effects._bonus_formula(state, fx["bonus_formula"])
        times = fx.get("times", 1)
        if times == "exhausted_this_card":
            times = _estimated_exhausts(state, card)
        total += amount * times
    return total


def _block_value(state: CombatState, card: Card,
                 incoming: Optional[float] = None) -> float:
    # Block is worth the damage it actually prevents this turn, not its
    # printed number — otherwise the pilot never blocks chip damage.
    # Healing is the same HP economy, capped by missing HP.
    # `incoming` is the caller's already-computed _incoming_damage, which is
    # the same number for every card in one decision; None recomputes it.
    val = 0.0
    raw = _raw_block(state, card)
    # v0.4: the Kurage's pulse Block arrives at THIS turn's end, i.e. in time
    # for the swing the pilot is currently pricing, so it counts like printed
    # Block. Later pulses are not counted here -- their damage is already
    # valued in _expected_damage and double-counting the defense would make
    # the summon crowd out real blockers on a lethal turn.
    pulse = (C.KURAGE_PULSE_BLOCK
             if any(fx["op"] == "summon_kurage" for fx in card.effects)
             else 0)
    if raw or pulse:
        # Resolved once for BOTH terms: `incoming` is the same number for
        # every card in one decision, which is why the caller hands it down.
        if incoming is None:
            incoming = _incoming_damage(state)
        prevented = max(0.0, incoming - state.player.block)
        val += min(raw, prevented) + min(pulse, prevented)
    heal = sum(fx["amount"] for fx in card.effects if fx["op"] == "heal")
    if heal:
        val += min(heal, state.player.max_hp - state.player.hp)
    return val


def _scaling_value(state: CombatState, card: Card) -> float:
    val = 0.0
    target = effects._default_target(state)
    applied_to_target: dict[str, int] = {}
    for fx in _active_effects(state, card.effects):
        # _est, not the raw field: an X-cost debuff (Malaise: weak X) carries
        # the STRING "X" here, and raw arithmetic on it killed every run the
        # card was drafted into. "-X" falls to _est's default 0 -- a negative
        # enemy amount (strength down) is a benefit this term cannot price,
        # and 0 is the honest refusal (scorer-term question, ask A3/c).
        amount = _est(state, fx.get("amount", 0))
        formula = fx.get("amount_formula")
        if formula and "target_power" in formula:
            power = formula["target_power"]
            amount = ((target.powers.get(power, 0) if target else 0)
                      + applied_to_target.get(power, 0))
        if fx["op"] == "apply_power" and fx.get("target", "self") == "self":
            # Cap per-power contribution: percent-stack powers (Vermillion
            # Pact 25, Durin 30) would otherwise dwarf everything.
            val += (min(amount, C.PILOT_SELF_POWER_STACK_CAP)
                    * C.PILOT_SELF_POWER_VALUE)
        elif fx["op"] == "apply_power":                  # enemy debuff
            val += amount * C.PILOT_ENEMY_DEBUFF_VALUE
            if fx.get("target") == "enemy":
                applied_to_target[fx["power"]] = (
                    applied_to_target.get(fx["power"], 0) + amount)
        elif fx["op"] == "grow_damage":
            # Rampage's increase applies to the circulating card instance;
            # price one future redraw, then let the usual fight-end decay
            # discount late setup.
            val += _est(state, fx["amount"])
    # Setup is worth less as the fight winds down.
    return (val * max(0.0, 1.0 - state.turn / C.PILOT_SETUP_TAPER_TURNS)
            if val else 0.0)


def _card_element(state: CombatState, card: Card) -> Optional[str]:
    if card.element != "none":
        return card.element
    if card.type == "attack" and state.player.cadence == "catalyst":
        return state.player.element
    return None


def _reaction_value(state: CombatState, card: Card) -> float:
    """Expected reaction opportunities from this play.

    This remains a deliberately compact strategic score (the concrete damage,
    block, and debuffs still live in their own terms), but it must model the
    card's REAL targeting. The old any-enemy check credited a single-target
    card with a reaction when the aura sat on a different enemy, and capped an
    all-enemy trigger at the same value as one reaction. Both distort the
    dedicated pilot more than a coarse constant does.
    """
    living = state.living_enemies
    if not living:
        return 0.0

    card_elem = _card_element(state, card)
    capable = False
    best_expected_triggers = 0.0

    for fx in card.effects:
        op = fx["op"]
        if op == "swirl":
            elem = "anemo"
        elif op == "apply_aura":
            # Apply-only skills carry their element on the effect. Relying on
            # card.element made a neutral utility wrapper seed-aware but blind
            # to the reaction it would actually trigger.
            elem = fx.get("element") or card_elem
        elif (op == "damage" and card_elem is not None
              and fx.get("applies_element", card.type == "attack")):
            elem = card_elem
        else:
            continue

        if not elem or elem == "none":
            continue
        capable = True
        reactable = [e for e in living if e.aura and e.aura != elem]
        target = fx.get("target", "enemy")

        if target == "enemy":
            # Single-target Swirl is deliberately aura-aware in the engine:
            # it models the player's target choice rather than blindly using
            # tier0's generic lowest-HP aim.
            aimed = (min(reactable, key=lambda e: e.hp)
                     if op == "swirl" and reactable
                     else effects._default_target(state))
            expected = float(bool(aimed and aimed in reactable))
        elif target == "all_enemies":
            expected = float(len(reactable))
        else:  # random_enemy / random_enemies
            hits = max(1.0, _est(state, fx.get("times", 1), 1))
            # Expected distinct aura-bearing targets hit at least once in N
            # independent random hits. A target can react only on its first
            # hit because that consumes its aura.
            expected = len(reactable) * (1.0 - (1.0 - 1.0 / len(living)) ** hits)

        # Multiple elemental effects on one card usually revisit the same
        # targets after their aura was consumed. Taking the strongest effect
        # avoids double-credit without mutating a preview copy of combat.
        best_expected_triggers = max(best_expected_triggers, expected)

    if not capable:
        return 0.0
    # Preserve the calibrated strategic scale: seeding=2, one trigger=6.
    # AoE and random cards now scale by their expected reaction count.
    return (C.PILOT_REACTION_TRIGGER_VALUE * best_expected_triggers
            if best_expected_triggers else C.PILOT_REACTION_SEED_VALUE)


def _tempo_value(state: CombatState, card: Card) -> float:
    val = 0.0
    for fx in _active_effects(state, card.effects):
        if fx["op"] in ("draw", "energy"):
            formula = fx.get("amount_formula")
            if isinstance(formula, dict):
                val += effects._calc_amount(state, formula, card)
            elif formula == "per_aura":
                # DRAFTER_VERSION 4: live aura count instead of the flat
                # default -- moves elemental_ecstasy's committed scoring.
                val += sum(1 for enemy in state.living_enemies if enemy.aura)
            else:
                val += _est(state, fx.get("amount", 1), 1)
        elif fx["op"] == "draw_while":
            # One matching card plus the non-matching stopper in a mixed deck.
            val += C.PILOT_DRAW_WHILE_VALUE
        elif fx["op"] == "gain_spark":
            val += fx.get("amount", 1) * C.PILOT_SPARK_VALUE
        elif fx["op"] == "burst_energy":
            val += fx["amount"] / C.PILOT_BURST_DIVISOR
        elif fx["op"] in ("copy_companion_in_hand", "replay_next_companion"):
            # POLICY 7 (EB-17p §13.8). Both ops turn a companion you already
            # hold into a second use of it, and both are DEAD with no companion
            # in hand: the engine's `_op_copy_companion_in_hand` returns early
            # on an empty `comps`, and a replay grant expires with the turn
            # that wrote it. Gated on the SAME predicate the engine selects
            # with -- `Card.is_companion`, no kit filter -- so the pilot and
            # the engine cannot disagree about what counts. `amount` is the
            # copy op's key, `times` the replay op's.
            if any(c.is_companion for c in state.player.hand):
                val += (PILOT_COMPANION_COPY_VALUE
                        * fx.get("amount", fx.get("times", 1)))
    return val


def _sustain_value(state: CombatState, card: Card) -> float:
    """Encore is deferred HP economy (absorbs after Block). Worth most of
    its face -- it keeps until used, unlike Block -- but discounted for
    not stopping THIS turn's hits when drawn late."""
    encore = sum(fx.get("amount", 0) for fx in card.effects
                 if fx["op"] == "gain_encore"
                 and isinstance(fx.get("amount"), int))
    return encore * C.PILOT_ENCORE_VALUE


def _spotlight_value(state: CombatState, card: Card) -> float:
    """Selector + two-mode Spotlight machinery value. Without this
    her pilots score the selector 0 and never designate -- the exact
    anchor-drafted-nothing failure M5 logged (DECISIONS 53)."""
    p = state.player
    val = 0.0
    # EB-31p (R124): the pilot reads the same both-modes flag the four
    # engine readers do. Under The Curtain Never Falls a designate is
    # functionally dead (both halves live regardless of p.spotlight, and
    # the moved-this-turn window is always-on -- effects.py:1773), Guest
    # Cast's half is permanently live, and is_spotlighted has targets with
    # p.spotlight still None.
    both_modes = effects.both_spotlight_modes(state)
    companion_waiting = any(c.is_companion and not c.kit_card for c in p.hand)
    generator_waiting = any(
        any(fx.get("op") == "generate_guest_star" for fx in c.effects)
        for c in p.hand)
    for fx in card.effects:
        if fx["op"] == "spotlight_designate":
            if both_modes:
                pass                    # dead op: nothing left to choose
            # When a generator is waiting, invite first so this same selector
            # can put the resulting Companion into Guest Cast.
            elif companion_waiting:
                # sequencing priority: light, then play
                val += C.PILOT_SPOTLIGHT_DESIGNATE_SEQUENCING
            elif generator_waiting:
                val += C.PILOT_SPOTLIGHT_DESIGNATE_GENERATOR
            else:
                val += (C.PILOT_SPOTLIGHT_DESIGNATE_OPENING
                        if p.spotlight is None
                        else C.PILOT_SPOTLIGHT_DESIGNATE_REDESIGNATE)
        elif (fx["op"] == "apply_power"
              and fx.get("power") in ("spotlight_mult_bonus",
                                      "spotlight_mult_bonus_turn",
                                      "spotlight_flat_damage_turn",
                                      "ovation_spend_boost")):
            # R16 card-mediated boosts: worth playing when a stage exists
            # (combat-scoped stacks compound; turn windows want same-turn
            # Spotlighted plays). ovation_spend_boost (R32.1 flip) is a
            # combat-scoped engine like top_billing's mult.
            guest_mode_live = (both_modes
                               or p.spotlight == C.SPOTLIGHT_GUEST_CAST)
            if guest_mode_live or companion_waiting:
                val += (C.PILOT_SPOTLIGHT_BOOST_COMBAT
                        if fx["power"] in ("spotlight_mult_bonus",
                                           "ovation_spend_boost")
                        else C.PILOT_SPOTLIGHT_BOOST_TURN)
            else:
                # not dead, just early
                val += C.PILOT_SPOTLIGHT_BOOST_EARLY
        elif fx["op"] == "generate_guest_star":
            # a card in hand, roughly
            val += C.PILOT_GUEST_STAR_VALUE * fx.get("amount", 1)
        elif fx["op"] == "copy_spotlighted_in_hand":
            has_target = (p.spotlight or both_modes) and any(
                effects.is_spotlighted(state, c) and not c.kit_card
                for c in p.hand)
            # dead without a target, and the pilot knows it
            val += C.PILOT_SPOTLIGHT_COPY_VALUE if has_target else 0.0
    return val


def _charge_value(state: CombatState, card: Card) -> float:
    """Kokomi's Charge-engine machinery (kickoff §2). Without this her
    pilots would score conscription and deliberate exhausts near zero and
    never run the engine — the DECISIONS-53 selector lesson again. Values
    only the MACHINERY; the payoff damage (charge bonus_formula, garment
    state) already flows through _expected_damage and _scaling_value.
    Default weight 0.0: every non-Kokomi pilot is unchanged."""
    p = state.player
    engine_live = "tamakushi_casket" in p.relic_hooks
    val = 0.0
    for fx in _active_effects(state, card.effects):
        op = fx["op"]
        if op == "gain_charge":
            val += (_est(state, fx.get("amount", 1), 1)
                    * C.PILOT_CHARGE_GAIN_VALUE)
        elif op == "conscript":
            # A recruit in hand at a discount, plus its Exhaust feeds the
            # meter later. Create mode nets a card; transform pays one.
            n = _est(state, fx.get("amount", 1), 1)
            val += n * (C.PILOT_CONSCRIPT_CREATE_VALUE
                        if fx.get("mode") == "create"
                        else C.PILOT_CONSCRIPT_TRANSFORM_VALUE)
        elif op == "exhaust_from" and engine_live:
            # Deliberate exhausts are Charge + deck-thinning when the
            # casket is on. amount can be "all" (Stoke grammar).
            n = fx.get("amount", 1)
            n = (C.PILOT_EXHAUST_ALL_ESTIMATE if n == "all"
                 else _est(state, n, 1))
            val += n * C.PILOT_DELIBERATE_EXHAUST_VALUE
    if engine_live and card.exhaust and not card.kit_card:
        # self-mill is fuel, not just loss
        val += C.PILOT_SELF_MILL_VALUE
    # The garment state: worth its remaining-turn Charge read. Scored here
    # (not _scaling_value) because its value RISES with banked Charge.
    for fx in card.effects:
        if (fx["op"] == "apply_power"
                and fx.get("power") == "ceremonial_garment"):
            turns = fx.get("amount", C.CEREMONIAL_GARMENT_TURNS)
            val += (turns * (p.charge // C.GARMENT_CHARGE_DIVISOR)
                    * C.PILOT_GARMENT_CHARGE_VALUE
                    + C.PILOT_GARMENT_BASE_VALUE)
    return val


# --- Stoker tuning (pilot-gap sprint, 2026-07-28). Module-level, NOT in
# tier0/constants.py: constants.py is the surface the C# parity gate compares
# by value, and a pilot heuristic has no C# counterpart to compare against --
# the mod ships no bot. These are PILOT JUDGMENT, not balance, and the sprint
# log records that they were picked by hand and never swept.
# Stamped by C.PILOT_WEIGHTS_VERSION all the same (EB-5): the stamp labels the
# pilot's whole scoring weight set, and where a weight is FILED is not what
# decides which readings are comparable.
STOKE_DEPLOY_OPEN = 6.0     # a member entering an EMPTY slot: pure addition
STOKE_DEPLOY_FULL = 1.5     # a member entering a FULL stage: a bow trigger,
                            # which is a different decision (§Track 1.1)
STOKE_RUNWAY_TURNS = 2.0    # "fuel it while the runway is under ~2 turns"
STOKE_FUEL_HUNGRY = 1.2     # per point that CLOSES the runway gap
STOKE_FUEL_SATED = 0.15     # per point beyond it -- not zero: surplus still
                            # absorbs, which is the whole D8 argument

# POLICY 7 (EB-17p §13.8, R176). A free copy of a companion ALREADY IN HAND is
# a card you chose to draft, not the blind top of your deck: it is worth more
# than the flat Draw 1 the tempo term prices at C.PILOT_SPARK_VALUE-scale 0.7.
# Filed here, not in constants.py, for the C#-parity reason at the head of this
# block -- and stamped by C.PILOT_WEIGHTS_VERSION all the same, which is why
# that stamp moves to 2 in the same edit: a weight ENTERING the labeled set
# changes the set, and two pilot readings across it are not one measurement.
PILOT_COMPANION_COPY_VALUE = 1.5

# --- EB-118 pilot policies (STAGED). Two decisions the engine has been making
# with a placeholder heuristic move here, behind ONE switch that DEFAULTS OFF.
#
# WHY A SWITCH: both policies change what the pilot DECIDES, so every Klee and
# Kokomi tier-0.5 number re-baselines the moment they are live. Off, the two
# call sites (`effects._op_place_bomb` concentration form,
# `effects._op_exhaust_from` chosen form) run the identical code they ran
# before this file was touched -- which is what keeps the frozen calibration
# battery and every regression pin byte-identical on this branch. Turning it on
# is the POLICY_VERSION event, written PROPOSED in tier05/draft.py and executed
# at landing, not here.
#
# The constants below are filed here rather than in constants.py for the reason
# at the head of the STOKE_* block -- constants.py is the surface the C# parity
# gate compares by value and the mod ships no bot -- and they JOIN the set
# C.PILOT_WEIGHTS_VERSION labels. That stamp moves with the switch, in the same
# landing edit: while the switch is off no weight below is ever read, so the
# labeled set is arithmetically unchanged and the stamp must NOT move yet.
PILOT_POLICIES_ENABLED = False

# Bomb placement (concentration form: `place_bomb` with `target: enemy`). The
# scale is DAMAGE POINTS: a point of bomb damage that will actually land is
# worth 1, so every other term below is priced against a point of damage and
# the weights can be read as "how many points of damage is this worth".
BOMB_LANDED_DAMAGE_VALUE = 1.0    # per point the target can still absorb
BOMB_LETHAL_WASTE_WEIGHT = 1.0    # per point past what it has left: bombs
                                  # beyond lethal are simply not dealt, and
                                  # the pile is spent on a corpse either way
BOMB_CONCENTRATION_VALUE = 2.0    # per bomb ALREADY on a target that lives to
                                  # detonation -- one pile detonates as one
                                  # event, which is what the pile readers and
                                  # Pounding Surprise's per-detonation riders
                                  # are priced on
BOMB_CONCENTRATION_STACK_CAP = 3  # counted stacks, at most: past three the
                                  # marginal pile-reader gain is noise next to
                                  # the lethal-waste risk it carries
BOMB_SUPPRESSION_VALUE = 1.0      # per point of the enemy's next attack that
                                  # arming an UNSUPPRESSED target costs it
                                  # (powers.modify_damage_dealt applies the
                                  # Weak rate). A point prevented and a point
                                  # dealt are the same point, hence 1.0
BOMB_READER_LETHAL_POP_VALUE = 4.0   # a detonator in hand, aimed here, and the
                                     # pile pops LETHAL: the one case the
                                     # damage estimator already credits early
                                     # detonation for
BOMB_EARLY_POP_PENALTY = 3.0      # same detonator, SUB-lethal pop: the bomb is
                                  # cashed this turn instead of detonating on
                                  # its own next turn, forfeiting nothing but
                                  # buying a smaller event
BOMB_MOVE_READER_AIM_VALUE = 1.0  # `move_bombs` gathers onto the aimed enemy,
                                  # so a pile already there is one it does not
                                  # have to move

# Exhaust selection (chosen `exhaust_from`). Candidate score is
#   payout(this card, candidate) - future_value(candidate)
# and the DEFAULT payout hook is identity-blind (0.0 for every candidate), so
# the default ranking is purely "lose the least". A grammar that pays per
# victim identity passes its own hook; the interface exists so that arrives as
# a parameter and not as a second heuristic.
EXHAUST_COST_EFFICIENCY_WEIGHT = 0.5   # future value is per-energy: a card's
                                       # worth divided by 1 + w x cost, so an
                                       # expensive payoff is discounted for the
                                       # turn it costs to deploy, not for being
                                       # big. This is the term the placeholder
                                       # had BACKWARDS -- it exhausted the
                                       # expensive card first, by cost alone
EXHAUST_JUNK_BONUS = 6.0          # a Status or Curse is negative future value:
                                  # it costs a draw every shuffle. Reachable
                                  # only for pools Kokomi's rotation law does
                                  # not govern (post-C11 her pool has no junk
                                  # in it), e.g. a real_ironclad True Grit+
EXHAUST_SELF_EXHAUST_DISCOUNT = 0.5   # a card that Exhausts itself on play was
                                      # leaving the deck anyway; only the one
                                      # use is lost

# EB-29t (POLICY 6): the promoted Test Subject reads (R128). The Strength an
# Enrage trigger grants is PERMANENT, but the greedy pilot prices it over a
# deliberately short horizon of future attack turns -- understating a
# long-fight cost is the safe direction to be wrong (the Kurage-bank
# precedent above). Not character machinery: Enrage and Intangible are
# board-state facts every pilot should read, like Frozen/Shatter.
ENRAGE_TAX_TURNS = 2.0      # future attack turns a +Strength grant is priced
                            # over, discounted by PILOT_FUTURE_DAMAGE_DISCOUNT


def _stoke_value(state: CombatState, card: Card) -> float:
    """Furina's SALON machinery: deploy the stage, then keep it fuelled.

    The sprint hypothesis (docs/archive/sprint-pilot-gap-2026-07-28.md) is that the
    sim/table divergence is a PILOT gap, not an arithmetic one: a stage that
    is dry half the time is a stage nobody is stoking. Two things the greedy
    pilot cannot see:

    1. A deploy is an `apply_power` on self, so its ONLY valuation is
       `_scaling_value`'s `min(amount, 6) * 3` -- decayed by
       `max(0, 1 - turn/12)`. That decay is right for a one-shot buff and
       WRONG for a member: a member fielded on turn 10 ticks every remaining
       turn of the fight, and by turn 12 the greedy pilot prices it at
       exactly zero. This term does not decay.
    2. Encore is valued by `_sustain_value` at a flat 0.8/point, which is a
       statement about Encore as a damage buffer and says nothing about the
       upkeep bill. A point of Encore that keeps a three-member stage ticking
       is worth more than the fourth point on an idle one -- that is the
       runway the D7 ribbon draws, and it is the quantity this term reads.

    Deliberately NOT lookahead and NOT a general improvement (Track 1.4): no
    damage or block is revalued here, so a stoker that comes back WORSE than
    greedy is a real reading of the loop and not a broken pilot.

    Default weight 0.0, the `charge`/`spotlight` precedent: every other pilot
    is arithmetically unchanged.
    """
    p = state.player
    live = len(p.salon)
    room = max(0, effects.salon_slots(p) - live)
    # The bill the CURRENT stage presents each upkeep. Zero with no members,
    # which makes every Encore gain score at the sated rate -- correct: with
    # no stage there is nothing to starve, and _sustain_value already prices
    # the buffer. It also means the stoker deploys BEFORE it fuels, which is
    # the ordering the brief asks for and falls out rather than being coded.
    bill = live * C.SALON_TICK_ENCORE_COST
    shortfall = max(0.0, STOKE_RUNWAY_TURNS * bill - p.encore)
    val = 0.0
    for fx in _active_effects(state, card.effects):
        op = fx["op"]
        if (op == "apply_power" and fx.get("power") == "salon_member"
                and fx.get("target", "self") == "self"):
            n = _est(state, fx.get("amount", 1), 1)
            opened = min(n, room)
            val += opened * STOKE_DEPLOY_OPEN
            val += (n - opened) * STOKE_DEPLOY_FULL
        elif op == "gain_encore":
            n = _est(state, fx.get("amount", 0))
            closes = min(n, shortfall)
            val += closes * STOKE_FUEL_HUNGRY
            val += (n - closes) * STOKE_FUEL_SATED
    return val


def _score(state: CombatState, card: Card, w: dict,
           dmg: Optional[float] = None, blk: Optional[float] = None) -> float:
    # `dmg`/`blk` are this card's already-computed _expected_damage and
    # _block_value (pilot() shares them with the lethal check and the regret
    # log); None computes them here.
    cost = card_cost(state, card)
    if dmg is None:
        dmg = _expected_damage(state, card)
    if blk is None:
        blk = _block_value(state, card)
    total = (w["damage"] * dmg
             + w["block"] * blk
             + w["scaling"] * _scaling_value(state, card)
             + w["reaction"] * _reaction_value(state, card)
             + w["tempo"] * _tempo_value(state, card)
             + w.get("sustain", 1.0) * _sustain_value(state, card)
             - w["cost"] * cost)
    # Character-machinery terms, skipped when their weight is zero. All three
    # are pure readers of state, so a zeroed weight makes the whole term
    # arithmetically dead -- and every pilot but Furina's zeroes spotlight,
    # every pilot but Kokomi's zeroes charge, and every pilot but the stoker
    # zeroes stoke. Scanning the hand for Companions and Guest-Star
    # generators on each of those was the single most-called thing in a
    # non-Furina fight.
    sw = w.get("spotlight", 0.0)
    if sw:
        total += sw * _spotlight_value(state, card)
    cw = w.get("charge", 0.0)
    if cw:
        total += cw * _charge_value(state, card)
    kw = w.get("stoke", 0.0)
    if kw:
        total += kw * _stoke_value(state, card)
    # EB-29t: every Skill played feeds each Enraged enemy its enrage stacks
    # in PERMANENT Strength (R128 _finish_play). Priced as +n damage on each
    # of the enemy's hits over ENRAGE_TAX_TURNS future attack turns; hits
    # read from the current intent (its ramp included), 1 when it is not
    # attacking -- the greedy read, understating a long fight on purpose.
    if card.type == "skill":
        tax = 0.0
        for e in state.living_enemies:
            n = e.powers.get("enrage", 0)
            if not n:
                continue
            intent = e.current_intent()
            hits = (e.ramped_times(intent)
                    if intent.get("kind") == "attack" else 1)
            tax += n * hits
        if tax:
            total -= tax * ENRAGE_TAX_TURNS * C.PILOT_FUTURE_DAMAGE_DISCOUNT
    return total


def _incoming_damage(state: CombatState) -> float:
    total = 0.0
    for e in state.living_enemies:
        if e.sleep_turns > 0:
            continue
        intent = e.current_intent()
        if intent["kind"] == "attack":
            # Same helper the enemy turn uses -- these two ramp readings were
            # duplicated formulas, and a pilot that mispredicts incoming
            # damage blocks against the wrong number.
            amount = e.ramped_amount(intent, state.turn)
            per_hit = powers.modify_damage_dealt(e, amount)
            if e.frozen:                # v1.5: halved, not skipped — and an
                per_hit *= C.FROZEN_DAMAGE_MULT   # attack this turn thaws it
            per_hit = powers.modify_damage_taken(state.player, per_hit)
            total += int(per_hit) * intent.get("times", 1)
    return total


def _lethal_card(state: CombatState, playable: list[Card],
                 dmg: Optional[list[float]] = None) -> Optional[Card]:
    """Single-card lethal check only — cheap and good enough (spec: dumb ok).

    `dmg` is the caller's per-playable _expected_damage, positionally aligned
    with `playable`; None recomputes it."""
    remaining = sum(e.hp + e.block for e in state.living_enemies)
    if dmg is None:
        dmg = [_expected_damage(state, c) for c in playable]
    for card, d in zip(playable, dmg):
        if d >= remaining:
            return card
    return None


# ---------------------------------------------------------------------------
#  EB-118 (1): bomb placement
# ---------------------------------------------------------------------------

def _hand_has_op(state: CombatState, op: str) -> bool:
    return any(fx.get("op") == op
               for c in state.player.hand for fx in c.effects)


def _pile_damage(state: CombatState, enemy) -> float:
    """What this enemy's EXISTING pile detonates for, `bomb_damage_up`
    included -- the same sum `effects.detonate_bombs` pays out, per bomb."""
    up = state.player.powers.get("bomb_damage_up", 0)
    return sum(b.damage + up for b in enemy.bombs)


def bomb_placement_score(state: CombatState, fx: dict, enemy) -> float:
    """Value of putting ONE bomb from `fx` on `enemy`.

    Lowest HP alone is not this decision: a bomb is damage that arrives at the
    START of the next player turn (combat._player_turn detonates last turn's
    piles), so what it is worth depends on whether the target is still alive
    to receive it, on the pile it joins, and on the attack it suppresses on the
    way. Pure reader of state, no rng -- determinism is preserved.
    """
    p = state.player
    per_bomb = fx["bomb_damage"] + p.powers.get("bomb_damage_up", 0)
    pending = _pile_damage(state, enemy)
    # Block is counted as effective HP: an enemy blocking on its own turn is
    # still holding that Block when the pile goes off at the player turn
    # start. Wrong only in the conservative direction (it understates waste).
    headroom = max(0.0, enemy.hp + enemy.block - pending)
    landed = min(per_bomb, headroom)
    score = (landed * BOMB_LANDED_DAMAGE_VALUE
             - (per_bomb - landed) * BOMB_LETHAL_WASTE_WEIGHT)

    survives = headroom > 0
    if survives and enemy.bombs:
        score += (min(len(enemy.bombs), BOMB_CONCENTRATION_STACK_CAP)
                  * BOMB_CONCENTRATION_VALUE)
    if not enemy.bombs and not enemy.bomb_suppression_spent:
        # The suppression latch arms on the FIRST bomb (powers reads
        # `bool(bombs) and not spent`), so this is marginal only for an empty
        # target -- which is precisely the term that argues against blind
        # concentration. Priced at the Weak rate the latch actually applies.
        intent = enemy.current_intent()
        if intent.get("kind") == "attack":
            swing = (enemy.ramped_amount(intent, state.turn)
                     * enemy.ramped_times(intent))
            score += (swing * (1.0 - C.WEAK_DEALT_MULT)
                      * BOMB_SUPPRESSION_VALUE)

    aim = effects._default_target(state)
    if enemy.bombs and enemy is aim:
        if _hand_has_op(state, "detonate"):
            score += (BOMB_READER_LETHAL_POP_VALUE
                      if pending + per_bomb >= enemy.hp + enemy.block
                      else -BOMB_EARLY_POP_PENALTY)
        if _hand_has_op(state, "move_bombs"):
            score += BOMB_MOVE_READER_AIM_VALUE
    return score


def bomb_placement_target(state: CombatState, fx: dict,
                          card: Optional[Card] = None):
    """The enemy this bomb goes on, or None on an empty board.

    Ties fall back to the pre-policy pick (lowest HP, then board order) so a
    board the policy has nothing to say about resolves exactly as it did.
    """
    living = state.living_enemies
    if not living:
        return None
    best = None
    best_key = None
    for i, enemy in enumerate(living):
        key = (bomb_placement_score(state, fx, enemy), -enemy.hp, -i)
        if best_key is None or key > best_key:
            best, best_key = enemy, key
    return best


# ---------------------------------------------------------------------------
#  EB-118 (2): exhaust selection
# ---------------------------------------------------------------------------

def identity_blind_payout(state: CombatState, card: Optional[Card],
                          candidate: Card) -> float:
    """Default payout hook: what the EXHAUSTING card pays for this particular
    victim. Today no shipped grammar reads the victim's identity -- Stoke and
    True Grit+ pay the same for any card -- so the honest default is a
    constant, and a constant cannot change the ranking. The hook exists so
    that when an identity-sensitive card is written its payout arrives as a
    parameter instead of as a second heuristic inside this chooser."""
    return 0.0


def exhaust_future_value(state: CombatState, card: Card) -> float:
    """What keeping this card is worth, per energy.

    The four terms enter at weight 1 apiece: the chooser runs at RESOLUTION
    time, where the pilot's archetype weight set is not reachable (the weights
    are closed over by `make_pilot`), so it cannot ask which pilot is flying.
    Under-weighting a character term is the safe direction -- it makes the
    chooser conservative about exhausting machinery, not eager.
    """
    val = (_expected_damage(state, card)
           + _block_value(state, card)
           + _scaling_value(state, card)
           + _tempo_value(state, card)
           + _sustain_value(state, card))
    if card.is_junk:
        val -= EXHAUST_JUNK_BONUS
    cost = card_cost(state, card)
    val /= 1.0 + EXHAUST_COST_EFFICIENCY_WEIGHT * max(0, cost)
    if card.exhaust:
        val *= EXHAUST_SELF_EXHAUST_DISCOUNT
    return val


def _legacy_worst_key(card: Card) -> tuple:
    """`effects._worst_card`'s key, mirrored so ties resolve to the pick this
    policy replaces. Kept in sync by test_eb118_switch_off."""
    return (card.type != "attack",
            card.cost if isinstance(card.cost, int) else 99)


def exhaust_victim(state: CombatState, pool: list[Card],
                   card: Optional[Card] = None, payout=None) -> Card:
    """Which card a CHOSEN exhaust spends, out of the already-legal `pool`.

    `pool` arrives filtered by the engine (kit exemption, an explicit
    `filter:`, and Kokomi's rotation law, which already drops junk for her);
    this chooser never widens it. Score is the payout for this victim minus
    what losing it costs, so with the identity-blind default the pick is the
    least valuable card -- NOT the most expensive one, which is what the
    placeholder read and is the inversion `test_eb118_policies` pins.
    """
    payout = payout or identity_blind_payout
    best = None
    best_key = None
    for i, cand in enumerate(pool):
        key = (payout(state, card, cand) - exhaust_future_value(state, cand),
               _legacy_worst_key(cand), -i)
        if best_key is None or key > best_key:
            best, best_key = cand, key
    return best
