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
from tier0.engine import effects, powers
from tier0.engine.combat import card_cost, card_playable
from tier0.engine.state import Card, CombatState


def _places_bombs(card: Card) -> bool:
    return any(fx["op"] == "place_bomb" for fx in card.effects)


def make_pilot(weights: dict):
    def pilot(state: CombatState) -> Optional[Card]:
        playable = [c for c in state.player.hand if card_playable(state, c)]
        if not playable:
            return None

        lethal = _lethal_card(state, playable)
        if lethal is not None:
            return lethal

        incoming = _incoming_damage(state)
        if (incoming >= C.BLOCK_PANIC_THRESHOLD * max(1, state.player.hp)
                and state.player.block < incoming):
            blockers = [c for c in playable if _raw_block(state, c) > 0]
            if blockers:
                return max(blockers, key=lambda c: _raw_block(state, c))

        scored = [(_score(state, c, weights), -i, c) for i, c in enumerate(playable)]
        best_score, _, best = max(scored, key=lambda t: t[:2])
        if best_score <= 0:
            return None
        # Bomb sequencing: attacks resolve BEFORE new placements, so this
        # turn's attacks don't pop bombs placed this turn (forfeiting
        # next-turn detonation + Pounding Surprise sparks).
        if _places_bombs(best):
            attacks = [(s, i, c) for s, i, c in scored
                       if c.type == "attack" and s > 0]
            if attacks:
                best = max(attacks, key=lambda t: t[:2])[2]
        _log_regret(state, best, playable)
        return best

    return pilot


def _immediate_value(state: CombatState, card: Card) -> float:
    return _expected_damage(state, card) + _block_value(state, card)


def _log_regret(state: CombatState, chosen: Card, playable: list[Card]) -> None:
    """Spec §6 pilot_regret: was a strictly-better single play available?
    'Strictly better' = higher immediate value (damage + effective block)
    at no greater cost. Sanity instrument, not a target — no rng used, so
    determinism is preserved."""
    chosen_val = _immediate_value(state, chosen)
    chosen_cost = card_cost(state, chosen)
    for other in playable:
        if other is chosen:
            continue
        if (card_cost(state, other) <= chosen_cost
                and _immediate_value(state, other) > chosen_val):
            state.emit("pilot_regret", chosen=chosen.id, better=other.id)
            return


def _est(state: CombatState, val, default: int = 0) -> float:
    """Estimate a possibly-formulaic amount for scoring purposes."""
    if isinstance(val, (int, float)):
        return val
    if val in ("X", "X_plus_1"):        # X-cards spend all remaining energy
        return state.player.energy + (1 if val == "X_plus_1" else 0)
    return default


def _active_effects(state: CombatState, effect_list: list[dict]):
    """Yield runtime-formula branches the pilot is explicitly able to read.

    Existing Klee/Furina conditionals deliberately keep their historic
    top-level-only valuation. Their predicates can depend on context created
    during card resolution (reaction_triggered_by_this, killed_target, the
    snapshotted aura), which a pre-play scorer cannot evaluate faithfully.
    The pass-5/pass-6 Ironclad predicates below are pure reads of current
    state.
    """
    for fx in effect_list:
        if fx["op"] == "conditional":
            name = fx["if"]
            if name.startswith("target_has_power_"):
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
            else:
                continue
            branch = fx["then"] if ready else fx.get("else", [])
            yield from _active_effects(state, branch)
        else:
            yield fx


def _expected_damage(state: CombatState, card: Card) -> float:
    total = 0.0
    living = state.living_enemies
    for fx in _active_effects(state, card.effects):
        if fx["op"] == "damage":
            if fx.get("target") == "self":
                total -= fx["amount"] * 0.5          # HP loss is a cost
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
            total += per_hit * times * n_targets
        elif fx["op"] == "place_bomb":
            total += fx["bomb_damage"] * _est(state, fx.get("amount", 1), 1)
        elif (fx["op"] == "apply_power"
              and fx.get("power") == "sparks_n_splash"):
            # The Burst payoff: stacks x 4 hits x 5 dmg over coming turns.
            total += (fx["amount"] * C.SPARKS_N_SPLASH_HITS
                      * C.SPARKS_N_SPLASH_HIT_DMG * 0.8)
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
        times = fx.get("times", 1)
        if times == "exhausted_this_card":
            times = _estimated_exhausts(state, card)
        total += amount * times
    return total


def _block_value(state: CombatState, card: Card) -> float:
    # Block is worth the damage it actually prevents this turn, not its
    # printed number — otherwise the pilot never blocks chip damage.
    # Healing is the same HP economy, capped by missing HP.
    val = 0.0
    raw = _raw_block(state, card)
    if raw:
        prevented = max(0.0, _incoming_damage(state) - state.player.block)
        val += min(raw, prevented)
    heal = sum(fx["amount"] for fx in card.effects if fx["op"] == "heal")
    if heal:
        val += min(heal, state.player.max_hp - state.player.hp)
    return val


def _scaling_value(state: CombatState, card: Card) -> float:
    val = 0.0
    target = effects._default_target(state)
    applied_to_target: dict[str, int] = {}
    for fx in _active_effects(state, card.effects):
        amount = fx.get("amount", 0)
        formula = fx.get("amount_formula")
        if formula and "target_power" in formula:
            power = formula["target_power"]
            amount = ((target.powers.get(power, 0) if target else 0)
                      + applied_to_target.get(power, 0))
        if fx["op"] == "apply_power" and fx.get("target", "self") == "self":
            # Cap per-power contribution: percent-stack powers (Vermillion
            # Pact 25, Durin 30) would otherwise dwarf everything.
            val += min(amount, 6) * 3
        elif fx["op"] == "apply_power":                  # enemy debuff
            val += amount * 2
            if fx.get("target") == "enemy":
                applied_to_target[fx["power"]] = (
                    applied_to_target.get(fx["power"], 0) + amount)
        elif fx["op"] == "grow_damage":
            # Rampage's increase applies to the circulating card instance;
            # price one future redraw, then let the usual fight-end decay
            # discount late setup.
            val += fx["amount"]
    # Setup is worth less as the fight winds down.
    return val * max(0.0, 1.0 - state.turn / 12.0) if val else 0.0


def _card_element(state: CombatState, card: Card) -> Optional[str]:
    if card.element != "none":
        return card.element
    if card.type == "attack" and state.player.cadence == "catalyst":
        return state.player.element
    return None


def _reaction_value(state: CombatState, card: Card) -> float:
    # Only ops that actually carry an element count — a hydro-flavored
    # heal (Barbara's Melody) applies nothing and must score 0 here.
    elem = _card_element(state, card)
    swirls = any(fx["op"] == "swirl" for fx in card.effects)
    applies = swirls or any(
        fx["op"] == "apply_aura"
        or (fx["op"] == "damage" and elem is not None
            and fx.get("applies_element", card.type == "attack"))
        for fx in card.effects)
    if not applies:
        return 0.0
    # Triggering beats seeding: any living enemy holding a reactable aura.
    for e in state.living_enemies:
        if e.aura and (swirls or (elem and e.aura != elem)):
            return 6.0
    return 2.0


def _tempo_value(state: CombatState, card: Card) -> float:
    val = 0.0
    for fx in _active_effects(state, card.effects):
        if fx["op"] in ("draw", "energy"):
            formula = fx.get("amount_formula")
            if isinstance(formula, dict):
                val += effects._calc_amount(state, formula, card)
            elif formula == "per_aura":
                val += sum(1 for enemy in state.living_enemies if enemy.aura)
            else:
                val += fx.get("amount", 1)
        elif fx["op"] == "draw_while":
            # One matching card plus the non-matching stopper in a mixed deck.
            val += 2.0
        elif fx["op"] == "gain_spark":
            val += fx.get("amount", 1) * 0.7    # sparks -> free attacks
        elif fx["op"] == "burst_energy":
            val += fx["amount"] / 10
    return val


def _sustain_value(state: CombatState, card: Card) -> float:
    """Encore is deferred HP economy (absorbs after Block). Worth most of
    its face -- it keeps until used, unlike Block -- but discounted for
    not stopping THIS turn's hits when drawn late."""
    encore = sum(fx.get("amount", 0) for fx in card.effects
                 if fx["op"] == "gain_encore"
                 and isinstance(fx.get("amount"), int))
    return encore * 0.8


def _spotlight_value(state: CombatState, card: Card) -> float:
    """Selector + Spotlight-machinery value (sheet pass 1). Without this
    her pilots score the selector 0 and never designate -- the exact
    anchor-drafted-nothing failure M5 logged (DECISIONS 53)."""
    p = state.player
    val = 0.0
    for fx in card.effects:
        if fx["op"] == "spotlight_designate":
            # Aiming an empty stage is the whole archetype; re-aiming is
            # nearly free but rarely urgent.
            val += 4.0 if p.spotlight is None else 0.3
        elif (fx["op"] == "apply_power"
              and fx.get("power") in ("spotlight_mult_bonus",
                                      "spotlight_mult_bonus_turn",
                                      "spotlight_flat_damage_turn",
                                      "ovation_spend_boost")):
            # R16 card-mediated boosts: worth playing when a stage exists
            # (combat-scoped stacks compound; turn windows want same-turn
            # Spotlighted plays). ovation_spend_boost (R32.1 flip) is a
            # combat-scoped engine like top_billing's mult.
            if p.spotlight is not None:
                val += (3.0 if fx["power"] in ("spotlight_mult_bonus",
                                               "ovation_spend_boost")
                        else 1.5)
            else:
                val += 0.3                       # not dead, just early
        elif fx["op"] == "generate_guest_star":
            val += 2.5 * fx.get("amount", 1)     # a card in hand, roughly
        elif fx["op"] == "copy_spotlighted_in_hand":
            has_target = p.spotlight and any(
                c.character == p.spotlight and not c.kit_card
                for c in p.hand)
            val += 3.5 if has_target else 0.0    # dead without a target,
    return val                                   # and the pilot knows it


def _score(state: CombatState, card: Card, w: dict) -> float:
    cost = card_cost(state, card)
    return (w["damage"] * _expected_damage(state, card)
            + w["block"] * _block_value(state, card)
            + w["scaling"] * _scaling_value(state, card)
            + w["reaction"] * _reaction_value(state, card)
            + w["tempo"] * _tempo_value(state, card)
            + w.get("sustain", 1.0) * _sustain_value(state, card)
            + w.get("spotlight", 0.0) * _spotlight_value(state, card)
            - w["cost"] * cost)


def _incoming_damage(state: CombatState) -> float:
    total = 0.0
    for e in state.living_enemies:
        if e.sleep_turns > 0:
            continue
        intent = e.current_intent()
        if intent["kind"] == "attack":
            amount = intent["amount"] + intent.get("ramp", 0) * max(
                0, state.turn - intent.get("ramp_after", 0))
            per_hit = powers.modify_damage_dealt(e, amount)
            if e.frozen:                # v1.5: halved, not skipped — and an
                per_hit *= C.FROZEN_DAMAGE_MULT   # attack this turn thaws it
            per_hit = powers.modify_damage_taken(state.player, per_hit)
            total += int(per_hit) * intent.get("times", 1)
    return total


def _lethal_card(state: CombatState, playable: list[Card]) -> Optional[Card]:
    """Single-card lethal check only — cheap and good enough (spec: dumb ok)."""
    remaining = sum(e.hp + e.block for e in state.living_enemies)
    for card in playable:
        if _expected_damage(state, card) >= remaining:
            return card
    return None
