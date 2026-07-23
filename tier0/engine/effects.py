"""Atomic effect resolvers — the card DSL.

v1 ops per tier0-simulator-spec.md §4.2, extended per
klee-character-design.md §6 for the real card sheet: detonate, move_bombs,
modify_bombs, burst_energy, swirl, refresh_all_auras, buff_next_attack,
cost_mod, conditional, repeat_this, formula amounts, companion ops.
"""

from __future__ import annotations

from typing import Optional

from tier0 import constants as C
from tier0.engine import powers, reactions, resources
from tier0.engine.state import Bomb, Card, CombatState, Enemy


def _amount(state: CombatState, val) -> int:
    """Resolve a literal or formula amount (X-cost cards)."""
    if isinstance(val, int):
        return val
    if val == "X":
        return state.current_x
    if isinstance(val, str) and val.startswith("X_plus_"):
        return state.current_x + int(val[len("X_plus_"):])
    if val == "exhausted_this_card":
        # Stoke: "exhaust your hand, generate that many cards". The count is
        # captured by the exhaust op as it runs, matching the dll, which
        # reads exhaustCount off the selection list before exhausting.
        return state.exhausted_this_card
    raise ValueError(f"unknown amount formula {val!r}")


def _bonus_formula(state: CombatState, formula: str) -> int:
    """Scaling damage riders. Grammar: 'N_per_detonation_this_combat'
    (The Big One) and 'N_per_M_fanfare' (the Fanfare crescendo — stacks
    grant flat bonuses, kickoff §4 / principles v1.10)."""
    n, _, rest = formula.partition("_per_")
    if not n.isdigit():
        raise ValueError(f"unknown bonus_formula {formula!r}")
    if rest == "detonation_this_combat":
        return int(n) * state.detonations_total
    m, _, what = rest.partition("_")
    if what == "fanfare" and m.isdigit():
        return int(n) * (state.player.fanfare // int(m))
    raise ValueError(f"unknown bonus_formula {formula!r}")


def _runtime_count(state: CombatState, token: str,
                   current_card: Optional[Card] = None) -> int:
    """A live integer the base-game CalculatedX/CalculatedDamage vars read at
    resolution time, not a number the pilot could pre-compute -- which is
    exactly why the real game defers them to play time:

      exhaust_pile   AshenStrike (ExtraDamage x cards in the exhaust pile)
      player_block   BodySlam (ExtraDamage x the owner's CURRENT Block)
      attacks_in_hand ExpectAFight (Energy x Attacks in hand at play time)
      strike_cards   PerfectedStrike (all cards carrying the structurally
                     extracted Strike tag, including the playing card)
      player_damage_events TearAsunder (unblocked player-damage entries this
                     combat, counted per event rather than per HP)
    """
    p = state.player
    if token == "exhaust_pile":
        return len(p.exhaust_pile)
    if token == "player_block":
        return p.block
    if token == "attacks_in_hand":
        return sum(1 for c in p.hand if c.type == "attack")
    if token == "strike_cards":
        piles = (p.draw_pile, p.hand, p.discard_pile, p.exhaust_pile)
        cards = [c for pile in piles for c in pile]
        if (current_card is not None
                and all(c is not current_card for c in cards)):
            cards.append(current_card)  # play_card has removed it from hand
        return sum("strike" in c.tags for c in cards)
    if token == "player_damage_events":
        return state.player_damage_events
    if token == "exhausted_this_card":
        return state.exhausted_this_card
    raise ValueError(f"unknown runtime count {token!r}")


def _calc_amount(state: CombatState, formula: dict,
                 current_card: Optional[Card] = None) -> int:
    """CalculatedDamageVar / CalculatedVar grammar: base + per * count, where
    count is a _runtime_count token. base defaults 0 (BodySlam), per defaults
    1 (ExpectAFight's 1-per-Attack)."""
    return (formula.get("base", 0)
            + formula.get("per", 1)
            * _runtime_count(state, formula["count"], current_card))


def _power_amount_formula(state: CombatState, formula: dict) -> int:
    """apply_power Amount read off a live power stack on the default-aim
    enemy (Dominate's StrengthPerVulnerable, MoltenFist's Vulnerable
    doubling). Evaluated AFTER any preceding op in the same card, so Dominate
    reads the +1 Vulnerable it just applied."""
    if "target_power" in formula:
        tgt = _default_target(state)
        return tgt.powers.get(formula["target_power"], 0) if tgt else 0
    raise ValueError(f"unknown apply_power amount_formula {formula!r}")


def _default_target(state: CombatState) -> Optional[Enemy]:
    """tier0's single-target aim -- the lowest-HP living enemy, the same one
    _pick_targets('enemy') returns and resolve_card snapshots for its aura
    predicate. Dismantle's hit-count predicate and Dominate/MoltenFist's
    power-reading formula both need the enemy the card is about to (or just
    did) hit. CAVEAT, inherent to the model and shared with Bash/Uppercut:
    across ops the aim is RE-picked, so a hit that kills the aimed enemy
    hands the rider to whoever is lowest-HP next, not to a corpse."""
    living = state.living_enemies
    return min(living, key=lambda e: e.hp) if living else None


def _pick_targets(state: CombatState, spec: str) -> list[Enemy]:
    living = state.living_enemies
    if not living:
        return []
    if spec in ("enemy", "lowest_hp_enemy"):        # pilot aims at lowest HP
        # PARITY, not fidelity: the base game rolls a RANDOM enemy for
        # TargetType.AnyEnemy on an autoplay, and the variance profile is
        # the whole identity of Havoc/Cascade. Keeping tier0's lowest-HP aim
        # for free plays would hand those cards a pilot's judgement they do
        # not have. Set only for the duration of a free play.
        if state.force_random_targeting:
            return [state.rng.choice(living)]
        return [min(living, key=lambda e: e.hp)]
    if spec == "all_enemies":
        return list(living)
    if spec in ("random_enemy", "random_enemies"):
        return [state.rng.choice(living)]
    raise ValueError(f"unknown target spec {spec!r}")


def _element_for(state: CombatState, fx: dict, card: Card) -> Optional[str]:
    """Cadence dial (design doc §2.3; Furina kickoff §1).

    catalyst: every attack applies the character's element unless the
    sheet says applies_element: false. Cards with their own element
    (companions) apply that instead.

    skill (Furina, Skill-grade): only Skill/Burst-tagged cards apply the
    CHARACTER's element -- attacks never auto-apply, which is what buys
    the higher base numbers within her low-statline identity. Companion
    cards are exempt from cadence entirely: what a companion applies is
    the sheet's explicit call (application budgets depend on it)."""
    if "applies_element" in fx:
        return card.element if fx["applies_element"] else None
    if (card.type == "attack" and fx["op"] == "damage"
            and state.player.cadence == "catalyst"):
        return card.element if card.element != "none" else state.player.element
    if (state.player.cadence == "skill" and fx["op"] == "damage"
            and not card.is_companion
            and state.player.element != "none"
            and (card.type == "skill" or "burst" in card.tags
                 or "skill_tag" in card.tags)):
        return state.player.element
    return None


# R33 lint-law (DECISIONS 87, the dead-knob exercise counter): a sweep
# that concludes "no effect" must show its swept constant was READ at
# least once per cell. This is the instrument-side tally; experiments
# reset it per cell and assert before publishing a null. E1 (pass 2)
# would have failed this loudly -- that catch is why it exists.
KNOB_READS: dict = {}


def reset_knob_reads() -> None:
    KNOB_READS.clear()


# Diagnostic switch retained for controlled Center/Guest comparisons;
# production never sets it outside experiments and tests.
SPOTLIGHT_FORCE: Optional[str] = None


def is_spotlighted(state: CombatState, card: Card) -> bool:
    """Whether a card receives Spotlight play texture in the active mode."""
    target = state.player.spotlight
    if target == C.SPOTLIGHT_GUEST_CAST:
        return card.is_companion
    return bool(target and card.character == target)


def is_outward_spotlighted(state: CombatState, card: Card) -> bool:
    """Whether Spotlight may change this card's printed numbers."""
    return (is_spotlighted(state, card)
            and state.player.spotlight != state.player.character_id)


def spotlight_mult(state: CombatState, card: Card) -> float:
    """Guest Cast numeric empowerment, including card-mediated bonuses.

    Center Stage always returns 1.0, even if Spotlight bonus powers are
    installed. Guest Cast and the legacy named-partner diagnostic path read
    the outward base plus combat- or turn-scoped bonuses.

    §2.2a extension, ENGINE-ENFORCED: this helper is plumbed into damage,
    Block, and (when the DSL grows one) element-application counts -- and
    nowhere else. Draw, energy, cost, and turn-economy ops have no path
    to it, so 'numbers only' is structure, not per-card discipline."""
    p = state.player
    if not is_outward_spotlighted(state, card):
        return 1.0
    cap = C.SPOTLIGHT_CARDS_PER_TURN_CAP     # schematized, OFF by default
    if cap is not None and state.spotlighted_cards_this_turn > cap:
        return 1.0
    base = C.SPOTLIGHT_BASE_MULT
    KNOB_READS["SPOTLIGHT_BASE_MULT"] = (
        KNOB_READS.get("SPOTLIGHT_BASE_MULT", 0) + 1)
    bonus = (p.powers.get("spotlight_mult_bonus", 0)
             + p.powers.get("spotlight_mult_bonus_turn", 0))
    return base + bonus / 100.0


def _spotlight_scale(state: CombatState, card: Card, amount: int) -> int:
    m = spotlight_mult(state, card)
    return int(amount * m) if m != 1.0 else amount


def deal_damage_to_enemy(state: CombatState, enemy: Enemy, base: float,
                         element: Optional[str] = None,
                         source: str = "card") -> float:
    """Full damage pipeline: strength/weak -> reaction amp -> vulnerable ->
    block -> hp. Returns damage actually dealt to HP (for metrics)."""
    # Solar Isotoma (Crystallize engine): attack hits vs aura'd enemies
    # grant block — checked before the hit can consume the aura.
    if (source == "attack" and enemy.aura
            and state.player.powers.get("solar_isotoma", 0)):
        state.player.block += C.SOLAR_ISOTOMA_BLOCK
    was_frozen = enemy.frozen       # snapshot: a hit can't shatter the
    dmg = powers.modify_damage_dealt(state.player, base)  # freeze it applies
    dmg = reactions.resolve_hit(state, enemy, element, dmg)
    dmg = powers.modify_damage_taken(enemy, dmg)
    # Slow (§10.9 promotion): +N% damage from Attacks per card played this
    # turn. cards_played_this_turn increments at play, BEFORE resolution, so
    # the attacking card counts itself -- the base-game trigger order.
    if enemy.slow and source == "attack":
        dmg *= 1 + enemy.slow * state.cards_played_this_turn / 100.0
    dmg = int(dmg)
    if base > 0 and dmg > base * C.AMP_STACK_LIMIT:
        state.emit("amp_stack_warning", base=base, final=dmg, target=enemy.name)
    blocked = min(enemy.block, dmg)
    enemy.block -= blocked
    hp_dmg = dmg - blocked
    was_alive = enemy.alive
    effective = min(hp_dmg, max(0, enemy.hp))   # overkill doesn't count
    enemy.hp -= hp_dmg
    state.emit("damage", target=enemy.name, amount=effective, blocked=blocked,
               base=base, source=source)
    # Frozen v2 Shatter (v1.5): the first Attack hit on a frozen enemy
    # deals bonus damage and removes Frozen. Direct HP, like splash.
    if was_frozen and enemy.frozen and source == "attack" and enemy.alive:
        enemy.frozen = False
        # shatter_bonus (Freminet, Shattering Pressure): flat rider on the
        # Shatter itself. Burst-direction growth -- every Shatter still
        # ENDS a freeze, so this cannot become control uptime.
        shatter = C.SHATTER_DAMAGE + state.player.powers.get("shatter_bonus", 0)
        sh = min(shatter, max(0, enemy.hp))
        enemy.hp -= shatter
        state.emit("damage", target=enemy.name, amount=sh, blocked=0,
                   base=shatter, source="shatter")
        state.emit("shatter", target=enemy.name)
        hp_dmg += shatter
    if was_alive and not enemy.alive:
        state.kills_this_card += 1
        # The base game's Fatal gate: cardPlay.Target.Powers.All(p =>
        # p.ShouldOwnerDeathTriggerFatal()). Summoned adds are excluded, so
        # Feed cannot farm them for permanent max HP.
        if enemy.counts_for_fatal:
            state.fatal_kills_this_card += 1
    if hp_dmg > 0:
        _detonate_bombs_on_hit(state, enemy, source)
    # Skittish (§10.9 promotion): "The first time it is hit each turn, it
    # gains N Block." AFTER the whole hit resolves (incl. any detonation
    # rider), so the triggering attack is never mitigated by it; the latch
    # resets in combat._player_turn.
    if (enemy.skittish and not enemy.skittish_fired and source == "attack"
            and enemy.alive):
        enemy.skittish_fired = True
        enemy.block += enemy.skittish
        state.emit("skittish_block", target=enemy.name,
                   amount=enemy.skittish)
    return hp_dmg


def _detonate_bombs_on_hit(state: CombatState, enemy: Enemy, source: str) -> None:
    # Bombs detonate early when the enemy is hit by an Attack card (§4.2).
    if source != "attack" or not enemy.bombs or not enemy.alive:
        return
    detonate_bombs(state, enemy)


def detonate_bombs(state: CombatState, enemy: Enemy, bonus: int = 0) -> None:
    bombs, enemy.bombs = enemy.bombs, []
    p = state.player
    for bomb in bombs:
        dmg = bomb.damage + bonus + p.powers.get("bomb_damage_up", 0)
        state.detonations_total += 1
        state.emit("bomb_detonation", target=enemy.name, damage=dmg)
        deal_damage_to_enemy(state, enemy, dmg, element=bomb.element,
                             source="bomb")
        if "spark_on_detonation" in p.relic_hooks:
            gain_sparks(state, 1)
        splash = p.powers.get("detonation_splash", 0)     # Blazing Delight
        if splash and C.DETONATION_SPLASH_PROC_CAP is not None:
            procs = getattr(state, "splash_procs_this_turn", 0)
            if procs >= C.DETONATION_SPLASH_PROC_CAP:
                splash = 0
            else:
                state.splash_procs_this_turn = procs + 1
        if splash:
            for other in state.living_enemies:
                other.hp -= splash
                state.emit("damage", target=other.name, amount=splash,
                           source="detonation_splash")
            if p.burst_max:
                p.burst_energy += C.DETONATION_SPLASH_BURST
        vuln = p.powers.get("detonation_vuln", 0)         # Explosive Frags
        if vuln and enemy.alive:
            powers.apply_power(state, enemy, "vulnerable", vuln)


def gain_sparks(state: CombatState, n: int) -> None:
    state.player.sparks += n
    state.emit("gain_spark", amount=n, total=state.player.sparks)


def _add_token(state: CombatState, card: Card, zone: str) -> None:
    if zone == "hand" and len(state.player.hand) < C.MAX_HAND_SIZE:
        state.player.hand.append(card)
    else:
        state.player.discard_pile.append(card)
    state.emit("add_card", card=card.id, to=zone)


# --- ops ---

def _op_damage(state: CombatState, fx: dict, card: Card) -> None:
    element = _element_for(state, fx, card)
    source = "attack" if card.type == "attack" else "card"

    if fx.get("target") == "self":            # Hot Hands / No Holding Back
        state.player.hp -= fx["amount"]       # HP loss, ignores block AND
        state.emit("self_damage", amount=fx["amount"])   # Encore: a priced
        resources.note_player_hp_loss(state, fx["amount"])  # cost stays paid
        return

    times = fx.get("times", 1)
    if "times_formula" in fx:
        formula = fx["times_formula"]
        if isinstance(formula, dict):
            times = _calc_amount(state, formula, card)
        elif formula != "2_plus_sparks":
            raise ValueError(f"unknown times_formula {fx['times_formula']!r}")
        else:
            # R39: the bank as it was at play time, NOT the post-spend bank --
            # otherwise going free at the threshold is what removes the sparks
            # the card counts.
            times = 2 + state.sparks_at_play  # Gleeful Barrage
    times = _amount(state, times)

    if "amount_formula" in fx:                # AshenStrike, BodySlam
        base = _calc_amount(state, fx["amount_formula"], card)
    else:
        base = _amount(state, fx["amount"])
    if "bonus_formula" in fx:
        base += _bonus_formula(state, fx["bonus_formula"])
    if state.salon_replacements_this_card:
        base *= C.SALON_REPLACE_DAMAGE_MULT
    # Spotlight scales the card's own printed damage -- before external
    # buffs (strength/next_attack_up are not printed numbers) and before
    # per-target riders (v1 boring baseline; riders logged as design room).
    base = _spotlight_scale(state, card, base)
    # Star of the Show: flat rider on Spotlighted cards' damage. Card-level
    # texture (kickoff §3.2 ratified design space), NOT the baseline knob.
    # Pass 2 adds the this-turn variant (stage_lights) on the same pipe.
    if is_outward_spotlighted(state, card):
        base += (state.player.powers.get("spotlight_flat_damage", 0)
                 + state.player.powers.get("spotlight_flat_damage_turn", 0))
    if card.type == "attack":
        base += state.current_attack_bonus
        # card_name_damage_bonus relic rider (dead branch on the battery:
        # relic_effects is empty). Flat, folded in BEFORE strength/vulnerable,
        # matching current_attack_bonus above.
        if state.player.relic_effects:
            from tier0.engine import relics       # late import avoids cycle
            base += relics.card_damage_bonus(state.player, card)
    # tag_damage_<tag> powers (Accuracy-like -> shiv) add per-hit.
    base += sum(state.player.powers.get(f"tag_damage_{t}", 0)
                for t in card.tags)

    for _ in range(times):
        for enemy in _pick_targets(state, fx.get("target", "enemy")):
            hit = base
            if fx.get("bonus_vs_bombed") and enemy.bombs:
                hit += fx["bonus_vs_bombed"]
            if fx.get("bonus_vs_aura") and enemy.aura:
                hit += fx["bonus_vs_aura"]
            # Bully: ExtraDamage x the DEFENDER's own stacks of a named power,
            # evaluated per target -- same shape as the aura/bomb riders above.
            rider = fx.get("bonus_per_target_power")
            if rider:
                hit += rider["per"] * enemy.powers.get(rider["power"], 0)
            deal_damage_to_enemy(state, enemy, hit, element=element,
                                 source=source)


def _op_block(state: CombatState, fx: dict, card: Card) -> None:
    raw = (_calc_amount(state, fx["amount_formula"], card)
           if "amount_formula" in fx else fx["amount"])
    if state.salon_replacements_this_card:
        raw *= C.SALON_REPLACE_DAMAGE_MULT
    times = fx.get("times", 1)
    times = (_runtime_count(state, times, card)
             if isinstance(times, str) else times)
    for _ in range(times):
        amount = _spotlight_scale(state, card, raw)
        # Frail bites each printed card-block gain before the refpower funnel.
        amount = powers.modify_block_gained(state.player, amount)
        state.player.block += amount
        state.block_gains_this_card += 1
        state.emit("block", amount=amount)


def _op_block_next_turn(state: CombatState, fx: dict, card: Card) -> None:
    # Charlotte, Enduring Frosthelm: pre-emptive block that lands at the
    # start of the player's NEXT turn (after the turn-start block reset).
    # Sustain-over-time identity without true healing (R8-shaped).
    # Spotlight scales it at play time (printed Block is printed Block).
    amount = fx["amount"]
    if state.salon_replacements_this_card:
        amount *= C.SALON_REPLACE_DAMAGE_MULT
    powers.apply_power(state, state.player, "block_next_turn",
                       _spotlight_scale(state, card, amount))


def _op_draw(state: CombatState, fx: dict, card: Card) -> None:
    n = fx.get("amount")
    if fx.get("amount_formula") == "per_aura":     # Elemental Ecstasy
        n = sum(1 for e in state.living_enemies if e.aura)
    if state.salon_replacements_this_card:
        n *= C.SALON_REPLACE_NUMERIC_MULT
    state.draw(n)
    state.emit("extra_draw", amount=n)   # A5 velocity accounting


def _op_draw_while(state: CombatState, fx: dict, card: Card) -> None:
    """Pillage: draw one card at a time and KEEP drawing while the card just
    drawn is of `while_type` (Attack) and the hand is not full.

    A fixed CombatState.draw(n) cannot express this -- the exit condition is
    WHAT was drawn -- so this drives the draw one card at a time and inspects
    the card that actually landed in hand (draw() appends, so it is hand[-1]).

    The non-matching card that ends the loop is KEPT: the stop condition is a
    LOOK at the drawn card, not a rejection of it, matching the base game.
    Bounded by the deck -- draw() adds nothing once the hand is full, both
    piles are empty, or NoDraw denies, and a hand that did not grow ends the
    loop. The count guard is a pure backstop against an impossible infinite.
    """
    want = fx.get("while_type", "attack")
    p = state.player
    for _ in range(2 * C.MAX_HAND_SIZE):
        before = len(p.hand)
        state.draw(1)
        if len(p.hand) == before:
            break                          # hand full, deck empty, or denied
        state.emit("extra_draw", amount=1)   # A5 velocity, like _op_draw
        if p.hand[-1].type != want:
            break


def _op_energy(state: CombatState, fx: dict, card: Card) -> None:
    amount = (_calc_amount(state, fx["amount_formula"], card)  # ExpectAFight
              if "amount_formula" in fx else fx["amount"])
    state.player.energy += amount
    state.emit("energy", amount=amount)


def _salon_amount(state: CombatState, base: int) -> int:
    """A Salon member numeric amount (Salon v2): base + the Fanfare Focus
    term (+1 per SALON_FOCUS_PER held, read live) + Grand Salon."""
    p = state.player
    focus = p.fanfare // C.SALON_FOCUS_PER if p.fanfare_cap else 0
    return base + focus + p.powers.get("salon_damage_up", 0)


def _salon_bow(state: CombatState, member: str) -> None:
    """The displaced member's final bow (Salon v2, rework plan §1): its
    UNIQUE payoff. No Encore upkeep, Focus/Grand-Salon scaled numerics,
    feeds the Burst meter like a tick."""
    p = state.player
    spec = C.SALON_MEMBERS[member]["bow"]
    dmg = spec.get("damage", 0)
    if dmg and state.living_enemies:
        enemy = state.rng.choice(state.living_enemies)
        deal_damage_to_enemy(state, enemy, _salon_amount(state, dmg),
                             element="hydro", source="salon_final_bow")
    blk = spec.get("block", 0)
    if blk:
        amt = _salon_amount(state, blk)
        p.block += amt
        state.emit("block", amount=amt)
    if spec.get("aura_all"):
        for enemy in state.living_enemies:
            reactions.resolve_hit(state, enemy, "hydro", 0)
    enc = spec.get("encore", 0)
    if enc:
        resources.gain_encore(state, enc)
    if p.burst_max:
        p.burst_energy += C.SALON_TICK_BURST
    state.emit("salon_final_bow", member=member)


def _deploy_salon_members(state: CombatState, amount: int,
                          member: str = "crabaletta") -> None:
    """Salon v2 deploy (rework plan §1): the typed FIFO queue with Defect
    evoke geometry. Deploying into full slots bows the OLDEST member OUT
    (its unique bow) and the new member takes the vacated slot — the v1
    rule (the excess deploy bowed itself and never entered) is the
    archive. powers['salon_member'] mirrors len(queue) so every count
    read (has_salon_members, the pilot, instruments) is unchanged."""
    p = state.player
    if member not in C.SALON_MEMBERS:
        raise ValueError(f"unknown salon member {member!r}")
    for _ in range(amount):
        if len(p.salon) >= C.SALON_MEMBER_SLOTS:
            state.salon_replacements_this_card += 1
            _salon_bow(state, p.salon.pop(0))
        p.salon.append(member)
        state.emit("salon_deploy", member=member, company=list(p.salon))
    p.powers["salon_member"] = len(p.salon)


def _op_apply_power(state: CombatState, fx: dict, card: Card) -> None:
    cap = fx.get("max_stacks")
    if "amount_formula" in fx:                 # Dominate, MoltenFist
        amount = _power_amount_formula(state, fx["amount_formula"])
    else:
        amount = fx["amount"]
    if (state.salon_replacements_this_card
            and fx["power"] != "salon_member"):
        amount *= C.SALON_REPLACE_NUMERIC_MULT
    # MoltenFist reads the target's current Vulnerable and applies that many
    # MORE -- inert against a target with none, so the guard skips the apply.
    # Dominate needs no guard: it applies 1 first, so its read is always >= 1.
    if fx.get("guard") == "nonzero" and amount <= 0:
        return
    if fx.get("target", "self") == "self":
        if fx["power"] == "salon_member":
            _deploy_salon_members(state, amount,
                                  fx.get("member", "crabaletta"))
            return
        powers.apply_power(state, state.player, fx["power"], amount,
                           max_stacks=cap)
    else:
        for enemy in _pick_targets(state, fx["target"]):
            powers.apply_power(state, enemy, fx["power"], amount,
                               max_stacks=cap)


def _op_apply_aura(state: CombatState, fx: dict, card: Card) -> None:
    times = (C.SALON_REPLACE_NUMERIC_MULT
             if state.salon_replacements_this_card else 1)
    for _ in range(times):
        for enemy in _pick_targets(state, fx.get("target", "enemy")):
            reactions.resolve_hit(state, enemy, fx["element"], 0)


def _op_place_bomb(state: CombatState, fx: dict, card: Card) -> None:
    for _ in range(_amount(state, fx.get("amount", 1))):
        for enemy in _pick_targets(state, fx.get("target", "random_enemy")):
            enemy.bombs.append(Bomb(damage=fx["bomb_damage"],
                                    element=fx.get("element", "pyro"),
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=fx["bomb_damage"])


def _op_detonate(state: CombatState, fx: dict, card: Card) -> None:
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        if enemy.bombs:
            detonate_bombs(state, enemy, bonus=fx.get("bonus", 0))


def _op_move_bombs(state: CombatState, fx: dict, card: Card) -> None:
    # Careful Arrangement: gather all bombs onto one enemy, +bonus each.
    targets = _pick_targets(state, fx.get("target", "enemy"))
    if not targets:
        return
    dest = targets[0]
    moved = []
    for e in state.living_enemies:
        if e is not dest:
            moved.extend(e.bombs)
            e.bombs = []
    for bomb in moved:
        bomb.damage += fx.get("bonus", 0)
        dest.bombs.append(bomb)
    if moved:
        state.emit("bombs_moved", count=len(moved), to=dest.name)


def _op_modify_bombs(state: CombatState, fx: dict, card: Card) -> None:
    scope = fx.get("scope", "all")
    for e in state.living_enemies:
        for bomb in e.bombs:
            if scope == "all" or (scope == "placed_this_turn"
                                  and bomb.turn_placed == state.turn):
                bomb.damage += fx["bonus"]


def _op_burst_energy(state: CombatState, fx: dict, card: Card) -> None:
    if state.player.burst_max:
        state.player.burst_energy += fx["amount"]
        state.emit("burst_energy", amount=fx["amount"],
                   total=state.player.burst_energy)


def _op_swirl(state: CombatState, fx: dict, card: Card) -> None:
    targets = _pick_targets(state, fx.get("target", "enemy"))
    # A human will aim a single-target Swirl at an aura when one exists.
    # Tier 0 otherwise hard-aims every AnyEnemy card at lowest HP, which made
    # Anemo cards blank whenever the aura happened to sit elsewhere.
    if fx.get("target", "enemy") == "enemy" and targets and not targets[0].aura:
        aura_targets = [e for e in state.living_enemies if e.aura]
        if aura_targets:
            targets = [min(aura_targets, key=lambda e: e.hp)]
    for enemy in targets:
        reactions.resolve_hit(state, enemy, "anemo", 0)


def _op_refresh_all_auras(state: CombatState, fx: dict, card: Card) -> None:
    for e in state.living_enemies:
        if e.aura:
            e.aura_turns_left = C.AURA_DURATION_TURNS


def _op_buff_next_attack(state: CombatState, fx: dict, card: Card) -> None:
    powers.apply_power(state, state.player, "next_attack_up", fx["amount"])


def _op_cost_mod(state: CombatState, fx: dict, card: Card) -> None:
    if fx.get("scope") != "companion_cards":
        raise ValueError(f"unknown cost_mod scope {fx.get('scope')!r}")
    state.companion_cost_delta_this_turn += fx["delta"]   # reset at turn start


def _op_gain_spark(state: CombatState, fx: dict, card: Card) -> None:
    gain_sparks(state, fx.get("amount", 1))


def _op_gain_encore(state: CombatState, fx: dict, card: Card) -> None:
    # Her "healing" effects grant Encore (kickoff §4). Unbounded per-combat.
    amount = _amount(state, fx["amount"])
    if state.salon_replacements_this_card:
        amount *= C.SALON_REPLACE_NUMERIC_MULT
    resources.gain_encore(state, amount)


def _op_spend_encore(state: CombatState, fx: dict, card: Card) -> None:
    """The OVERDRAW primitive (kickoff §4, Salon grammar): drains Encore
    first; any shortfall drains TRUE HP -- greed is legal and priced.
    Cards that must not overdraw use the encore_cost field (playability
    gate in combat.card_playable) instead of this op."""
    resources.spend_encore_or_hp(state, _amount(state, fx["amount"]))


def _op_spotlight_designate(state: CombatState, fx: dict, card: Card) -> None:
    """Choose between Center Stage and Guest Cast.

    Center Stage designates Furina: her cards create Fanfare but receive no
    numeric Spotlight bonus. Guest Cast designates the Companion category:
    every Companion card is empowered, but those plays create no Fanfare.
    A ready Companion in hand makes Guest Cast immediately useful; otherwise
    the selector defaults to Center Stage. The diagnostic override retains
    forced self/companion arms for experiments."""
    p = state.player
    companion_in_hand = any(c.is_companion and not c.kit_card for c in p.hand)
    companion_anywhere = any(
        c.is_companion and not c.kit_card
        for c in (p.hand + p.draw_pile + p.discard_pile))
    if SPOTLIGHT_FORCE == "self":
        target = p.character_id or None
    elif SPOTLIGHT_FORCE == "companion":
        target = C.SPOTLIGHT_GUEST_CAST if companion_anywhere else None
    elif companion_in_hand:
        target = C.SPOTLIGHT_GUEST_CAST
    else:
        target = p.character_id or (
            C.SPOTLIGHT_GUEST_CAST if companion_anywhere else None)
    if target is None:
        return                                   # nothing valid to aim at
    if target != p.spotlight:
        p.spotlight = target
        state.spotlight_moved_this_turn = True      # selector-payoff window
        state.spotlight_moves_this_combat += 1
        mode = ("guest_cast" if target == C.SPOTLIGHT_GUEST_CAST
                else "center_stage")
        state.emit("spotlight_designated", character=target, mode=mode)


def _op_raise_fanfare_cap(state: CombatState, fx: dict, card: Card) -> None:
    """Rare uncapper (kickoff §4): raises the Fanfare cap. The nasty setup
    cost is authored on the card (self-damage rider), not here. Inert for
    characters without the resource, like every Fanfare path."""
    p = state.player
    if not p.fanfare_cap:
        return
    p.fanfare_cap += fx["amount"]
    state.emit("fanfare_cap_raised", amount=fx["amount"], cap=p.fanfare_cap)


def _op_generate_guest_star(state: CombatState, fx: dict, card: Card) -> None:
    """Guest Star generation (kickoff §9), four guardrails all structural:
    this-combat-only (tokens live in combat piles; decks rebuild from ids
    per fight), generators Exhaust (sheet field), equal-rarity (the pool
    is filtered to fx['rarity'] == the generator's own printed rarity),
    and the pool is shared companions + the Guest Star set ONLY — playable
    characters' personal cards are structurally absent because they are
    neither companions nor guest_star rows."""
    _generate(state, fx, "guest_star")


def _generation_pool(state: CombatState, fx: dict, which: str) -> list[Card]:
    from tier0.content import loader                # late import avoids cycle
    if which == "guest_star":
        return loader.guest_star_generation_pool(fx["rarity"])
    if which == "character":
        # Stoke: CardFactory.GetForCombat over the character's own unlocked
        # pool, ALL rarities (no equal-rarity clause -- that guardrail is
        # specific to Guest Star generation, not the base game's).
        get_pool = getattr(loader, "character_generation_pool", None)
        if get_pool is None:
            raise NotImplementedError(
                "UNIMPLEMENTED: generate_from_pool(pool: character) needs "
                "loader.character_generation_pool(character_id), which does "
                "not exist yet. Refusing to substitute another pool -- a "
                "silently wrong generation pool is exactly the invisible "
                "bias this project exists to catch. Exclude Stoke until the "
                "loader entry point lands.")
        # CanBeGeneratedInCombat, honored HERE so no pool source can forget
        # it: Feed opts out, and generating it would hand the character a
        # permanent max-HP engine it never drafted.
        pool = [c for c in get_pool(state.player.character_id)
                if c.generatable and not c.kit_card]
        if not pool:
            raise ValueError(
                f"empty generation pool for {state.player.character_id!r}")
        return sorted(pool, key=lambda c: c.id)     # determinism under seed
    raise ValueError(f"unknown generation pool {which!r}")


def _generate(state: CombatState, fx: dict, which: str) -> None:
    import copy as _copy
    from tier0.content import loader, upgrades      # late import avoids cycle
    pool = _generation_pool(state, fx, which)
    amount = fx.get("amount", fx.get("amount_formula", 1))
    for _ in range(_amount(state, amount)):
        pick = _copy.deepcopy(state.rng.choice(pool))
        if fx.get("upgraded") and upgrades.has_upgrade(pick.id):
            # Stoke+ generates upgraded cards. The `+` id convention in
            # loader.get_card carries the upgraded form for free; a card
            # with no expressible upgrade simply arrives unupgraded, which
            # is the same visible-skip policy upgrades.UNAPPLIABLE uses.
            pick = loader.get_card(pick.id + upgrades.SUFFIX)
        if which == "guest_star":
            pick.generated_by_guest_star = True
        if "cost_override" in fx:                   # upgraded form: 0 this turn
            pick.cost = fx["cost_override"]
        _add_token(state, pick, fx.get("to", "hand"))
        if which == "guest_star":
            state.emit("guest_star_generated", card=pick.id)
        else:
            state.emit("card_generated", card=pick.id, pool=which)


def _op_generate_from_pool(state: CombatState, fx: dict, card: Card) -> None:
    """Base-game CardPileCmd.AddGeneratedCardsToCombat (Stoke). The singular
    AddGeneratedCardToCombat (Anger, InfernalBlade) is this same op with a
    fixed id and amount 1 -- use add_card for those. Anger's
    CardCmd.PreviewCardPileAdd is pure UI and is implemented as nothing."""
    _generate(state, fx, fx.get("pool", "character"))


def _op_copy_spotlighted_in_hand(state: CombatState, fx: dict,
                                 card: Card) -> None:
    """Encore Performance (kickoff §9): duplicate a Spotlighted card in
    hand. Dead without a designation and a drafted target — BY DESIGN
    (duplication deepens a committed kit; it must not conjure one)."""
    import copy as _copy
    p = state.player
    if not p.spotlight:
        return
    targets = [c for c in p.hand if is_spotlighted(state, c)
               and not c.kit_card]
    if not targets:
        return
    for _ in range(fx.get("amount", 1)):
        chosen = _copy.deepcopy(state.rng.choice(targets))
        if "cost_override" in fx:
            chosen.cost = fx["cost_override"]
        _add_token(state, chosen, "hand")
        state.emit("encore_performance_copy", card=chosen.id)


def _op_heal(state: CombatState, fx: dict, card: Card) -> None:
    p = state.player
    amount = fx["amount"]
    if state.salon_replacements_this_card:
        amount *= C.SALON_REPLACE_NUMERIC_MULT
    healed = min(amount, p.max_hp - p.hp)
    p.hp += healed
    state.emit("heal", amount=healed)


def _op_add_card(state: CombatState, fx: dict, card: Card) -> None:
    from tier0.content import loader                # late import avoids cycle
    zone = fx.get("zone") or fx.get("to", "discard")
    n = fx.get("amount", 1)
    if fx.get("card") == "self":                    # Anger: clone THIS card
        # CreateClone() of the playing instance -- so Anger+ clones an
        # UPGRADED copy. A fixed card_id add would reload the base id and
        # silently downgrade the clone (the whole point of the mechanic is
        # that the clone inherits this instance's upgrade state).
        import copy as _copy
        for _ in range(n):
            clone = _copy.deepcopy(card)
            if "cost_override" in fx:
                clone.cost = fx["cost_override"]
            _add_token(state, clone, zone)
        return
    if "pool" in fx:                                # Secret Stash
        pool_cards = loader.cards_in_pool(fx["pool"])
        picks = [state.rng.choice(pool_cards) for _ in range(n)]
        ids = [c.id for c in picks]
    else:
        ids = [fx.get("card_id") or fx["card"]] * n
    for cid in ids:
        token = loader.get_card(cid)
        if "cost_override" in fx:
            token.cost = fx["cost_override"]
        _add_token(state, token, zone)


def _op_discard(state: CombatState, fx: dict, card: Card) -> None:
    # Kit cards are exempt: the v1.9 invariant is that the Burst never
    # enters a pile. Without this, a random discard (Bright Idea) moved
    # the granted Burst to discard, it circulated as loot on reshuffle,
    # and grant_charged_kit -- which dedups against HAND only -- appended
    # the same object a second time. Review-workflow catch, repro'd.
    for _ in range(fx.get("amount", 1)):
        pool = [c for c in state.player.hand if not c.kit_card]
        if not pool:
            return
        victim = state.rng.choice(pool)
        state.player.hand.remove(victim)
        state.player.discard_pile.append(victim)
        state.emit("discard", card=victim.id)


def _op_exhaust_from(state: CombatState, fx: dict, card: Card) -> None:
    hand = state.player.hand
    # DEFECT FIX: the status branch used to rebuild the pool from `hand` and
    # so dropped the kit-card exemption two lines above -- a status-filtered
    # exhaust could eat the granted Burst, breaking the v1.9 invariant that
    # the kit never enters a pile. Filter the exempt pool instead.
    pool = [c for c in hand if not c.kit_card]   # same invariant as discard
    if fx.get("filter") == "status":
        pool = [c for c in pool if c.rarity == "status"]
    elif fx.get("filter") == "non_attack":
        pool = [c for c in pool if c.type != "attack"]
    n = fx.get("amount", 1)
    # Stoke exhausts the WHOLE hand and then generates that many cards. The
    # count is fixed BEFORE any exhausting (the dll reads exhaustCount off
    # the selection list up front), which is what len(pool) here gives us.
    n = len(pool) if n == "all" else _amount(state, n)
    # TrueGrit's split: base form exhausts at RANDOM, the upgrade lets the
    # player choose -- exactly the split _op_discard_for_sparks already
    # makes, and it reuses the same _worst_card instrument surface.
    chosen = fx.get("select", "random") == "chosen"
    for _ in range(n):
        if not pool:
            break
        victim = _worst_card(pool) if chosen else state.rng.choice(pool)
        pool = [c for c in pool if c is not victim]
        hand.remove(victim)
        state.player.exhaust_pile.append(victim)
        state.exhausted_this_card += 1
        if chosen:
            state.emit("exhaust", card=victim.id, chosen=True)
        else:
            state.emit("exhaust", card=victim.id)


def _worst_card(cards: list[Card]) -> Card:
    # Shared v1 "lowest-value" pick: highest cost non-attack first (pilot
    # heuristic placeholder; spec allows dumb). INSTRUMENT SURFACE: every
    # chosen-discard measurement rides this choice -- if a window result
    # looks heuristic-shaped, this is the knob to probe.
    return max(cards, key=lambda c: (c.type != "attack",
                                     c.cost if isinstance(c.cost, int) else 99))


def _best_card(cards: list[Card]) -> Card:
    # Mirror of _worst_card for "pick a GOOD card" selections (Headbutt's
    # recall). Prefer an attack, then the most printed power. INSTRUMENT
    # SURFACE: every recall measurement rides this choice.
    return max(cards, key=lambda c: (c.type == "attack", _printed_power(c)))


def _walk_effects(effects: list[dict]):
    """Effect list walk including conditional branches."""
    for fx in effects:
        yield fx
        for branch in ("then", "else"):
            if isinstance(fx.get(branch), list):
                yield from _walk_effects(fx[branch])


def _printed_power(card: Card) -> int:
    """Sum of printed damage and Block on a card — the crude 'how big is
    this card' scalar the choice heuristics rank by. Deliberately reads
    PRINTED numbers only (no strength, no Spotlight, no formulas): the
    pilot is choosing before resolution, and a formula amount is not a
    number it could compare anyway."""
    total = 0
    for fx in _walk_effects(card.effects):
        if fx.get("op") not in ("damage", "block"):
            continue
        amount, times = fx.get("amount"), fx.get("times", 1)
        if isinstance(amount, int) and isinstance(times, int):
            total += amount * times
    return total


def _best_upgrade_target(hand: list[Card], idxs: list[int]) -> int:
    """Armaments' choice: greedy delta — the eligible card that gains the
    most printed damage+block from being upgraded. Ties break to the lowest
    hand index so the pick stays deterministic under a fixed seed.
    INSTRUMENT SURFACE (same convention as _worst_card)."""
    import copy as _copy
    from tier0.content import upgrades              # late import avoids cycle

    def delta(i: int) -> int:
        # Score the same live instance the upgrade will mutate. Reloading the
        # base row erases Rampage growth and temporary generated-card state.
        upped = upgrades.apply_upgrade(_copy.deepcopy(hand[i]))
        return _printed_power(upped) - _printed_power(hand[i])

    return max(idxs, key=lambda i: (delta(i), -i))


def _op_discard_for_sparks(state: CombatState, fx: dict, card: Card) -> None:
    """R36 (Crackle redesign, user-ratified 2026-07-20): FORCED,
    PLAYER-CHOSEN discard; 1 Spark per card ACTUALLY discarded, capped at
    fx["sparks"]. Short hand discards min(amount, hand); an empty hand
    yields no fodder and NO Spark -- the Spark is priced BY the discard
    (an empty-hand free Spark converges on the exact design the ratified
    band rejected, 0.668 vs 0.65). Kit cards are exempt fodder (the v1.9
    invariant, same pool rule as _op_discard)."""
    discarded = 0
    for _ in range(fx.get("amount", 1)):
        pool = [c for c in state.player.hand if not c.kit_card]
        if not pool:
            break
        victim = _worst_card(pool)          # the pilot's chosen discard
        state.player.hand.remove(victim)
        state.player.discard_pile.append(victim)
        state.emit("discard", card=victim.id, chosen=True)
        discarded += 1
    gain = min(fx.get("sparks", discarded), discarded)
    if gain:
        gain_sparks(state, gain)


def _op_scry_discard(state: CombatState, fx: dict, card: Card) -> None:
    # Look at top N, discard the "worst" (shared heuristic above).
    n = fx.get("amount", 1)
    top = state.player.draw_pile[:n]
    if not top:
        return
    worst = _worst_card(top)
    state.player.draw_pile.remove(worst)
    state.player.discard_pile.append(worst)
    state.emit("scry_discard", card=worst.id)


def _op_conditional(state: CombatState, fx: dict, card: Card) -> None:
    branch = fx["then"] if _predicate(state, fx["if"]) else fx.get("else", [])
    _resolve_effects(state, branch, card)


def _predicate(state: CombatState, name: str) -> bool:
    if name == "this_cost_zero":
        return state.current_card_cost == 0
    if name == "has_spark":
        return state.player.sparks > 0
    if name == "target_has_nonpyro_aura":
        # Snapshotted at card start — the card's own first hit may consume
        # the aura via reaction, which is exactly what the bonus rewards.
        return state.target_had_offelement_aura
    if name == "reaction_triggered_by_this":
        return state.reactions_this_card > 0
    if name == "reaction_triggered_this_turn":
        # Chevreuse Vanguard's Valor. RULED: ANY reaction counts, not
        # Overload-only -- must never be a dead draw off-Pyro/Electro.
        return state.reactions_this_turn > 0
    if name == "killed_target":
        return state.kills_this_card > 0
    if name == "killed_target_fatal":
        # Feed. The base game's Fatal gate ignores deaths whose owner says
        # they should not trigger it (summoned adds) -- see
        # Enemy.counts_for_fatal. Distinct from killed_target so Klee's and
        # Furina's existing kill riders keep their exact meaning.
        return state.fatal_kills_this_card > 0
    if name.startswith("target_has_power_"):
        # Dismantle: the hit-count branch reads whether the default-aim enemy
        # carries a named power AT PLAY TIME. The conditional resolves the
        # predicate before any damage op inside its branch, so this is a clean
        # pre-hit read. Parameterised on the power name (target_has_power_
        # vulnerable today) so the next such card needs no new predicate.
        tgt = _default_target(state)
        power = name[len("target_has_power_"):]
        return bool(tgt and tgt.powers.get(power, 0) > 0)
    if name.startswith("exhaust_pile_at_least_"):
        # PactsEnd: the AoE fires only when the exhaust pile already holds at
        # least N cards; otherwise the card resolves as nothing.
        n = int(name.rsplit("_", 1)[1])
        return len(state.player.exhaust_pile) >= n
    if name == "card_exhausted_this_turn":
        return state.cards_exhausted_this_turn > 0
    if name == "hp_lost_this_turn":
        return state.hp_lost_this_turn > 0
    if name == "enemy_intends_attack":
        # Frozen enemies still attack under v1.5 (at -50%), so they count.
        return any(e.current_intent()["kind"] == "attack"
                   and e.sleep_turns == 0
                   for e in state.living_enemies)
    # --- Furina sheet-pass predicates ---
    if name == "has_salon_members":
        return state.player.powers.get("salon_member", 0) > 0
    if name == "spotlight_set":
        return state.player.spotlight is not None
    if name == "spotlight_moved_this_turn":
        return state.spotlight_moved_this_turn
    if name == "spotlight_unmoved_this_combat":
        # Commitment payoff: designated once and never re-aimed. False
        # while nothing is designated (an empty stage is not commitment).
        return (state.player.spotlight is not None
                and state.spotlight_moves_this_combat <= 1)
    if name == "spotlighted_card_played_this_turn":
        return state.spotlighted_cards_this_turn > 0
    if name.startswith("fanfare_at_least_"):
        return state.player.fanfare >= int(name.rsplit("_", 1)[1])
    if name.startswith("encore_at_least_"):
        return state.player.encore >= int(name.rsplit("_", 1)[1])
    raise ValueError(f"unknown predicate {name!r}")


def _op_repeat_this(state: CombatState, fx: dict, card: Card) -> None:
    state.repeat_requested = fx.get("times", 1)     # honored by resolve_card


def _op_grow_damage(state: CombatState, fx: dict, card: Card) -> None:
    """Rampage: permanently raise this card instance's printed damage.

    The card object circulates through the combat piles, so mutating its own
    first damage op preserves growth across redraws; deepcopy-based clones
    inherit the amount they cloned from, matching CardModel clone semantics.
    """
    hit = next((effect for effect in card.effects
                if effect.get("op") == "damage"
                and isinstance(effect.get("amount"), int)), None)
    if hit is None:
        raise ValueError(f"{card.id}: grow_damage has no literal damage op")
    hit["amount"] += fx["amount"]
    state.emit("grow_damage", card=card.id, amount=fx["amount"],
               total=hit["amount"])


def _op_chance_bomb_per_detonation(state: CombatState, fx: dict,
                                   card: Card) -> None:
    # Chained Reactions: per detonation caused by this card so far, a
    # chance to place a fresh bomb on a random enemy.
    n = state.detonations_total - state.detonations_at_card_start
    for _ in range(n):
        if state.rng.random() < fx["chance"] and state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            enemy.bombs.append(Bomb(damage=fx["bomb_damage"],
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=fx["bomb_damage"])


def _op_copy_companion_in_hand(state: CombatState, fx: dict, card: Card) -> None:
    import copy as _copy
    comps = [c for c in state.player.hand if c.is_companion]
    if not comps:
        return
    for _ in range(fx.get("amount", 1)):
        chosen = _copy.deepcopy(state.rng.choice(comps))
        if "cost_override" in fx:            # Borrowed Brilliance upgrade
            chosen.cost = fx["cost_override"]
        _add_token(state, chosen, "hand")


def _op_replay_next_companion(state: CombatState, fx: dict, card: Card) -> None:
    state.replay_next_companion += fx.get("times", 1)   # reset at turn start


def _op_copy_companions_played(state: CombatState, fx: dict, card: Card) -> None:
    from tier0.content import loader
    for cid in dict.fromkeys(state.companions_played):  # unique, in order
        token = loader.get_card(cid)
        if "cost_override" in fx:
            token.cost = fx["cost_override"]
        _add_token(state, token, fx.get("zone", "hand"))


def _op_upgrade_in_hand(state: CombatState, fx: dict, card: Card) -> None:
    """Armaments (base: choose 1; upgraded: every upgradable card in hand).

    Eligibility is upgrades.has_upgrade, which already excludes `+` ids and
    the UNAPPLIABLE set -- so a card whose upgrade the sim cannot express is
    visibly skipped rather than pretend-upgraded.
    """
    import copy as _copy
    from tier0.content import upgrades              # late import avoids cycle
    hand = state.player.hand
    idxs = [i for i, c in enumerate(hand) if upgrades.has_upgrade(c.id)]
    if not idxs:
        return
    if fx.get("scope", "chosen") == "chosen":
        idxs = [_best_upgrade_target(hand, idxs)]
    # Replace BY INDEX. Card is a plain dataclass with eq=True, so
    # list.remove matches by value (combat.play_card already relies on
    # that); a remove/append rebuild would silently reorder the hand and
    # perturb every downstream heuristic that reads hand order.
    for i in idxs:
        # Upgrade the LIVE instance rather than reloading a pristine base row.
        # Rampage's accumulated damage, generated-card cost overrides, and
        # clone state are all combat mutations the real CardModel preserves.
        hand[i] = upgrades.apply_upgrade(_copy.deepcopy(hand[i]))
        state.emit("upgrade_in_hand", card=hand[i].id)


def _op_gain_max_hp(state: CombatState, fx: dict, card: Card) -> None:
    """Feed. CreatureCmd.GainMaxHp raises max HP by `amount` AND heals by
    the same amount -- the heal is part of the command, not a second effect.

    CROSS-TIER FLAG: in the real game this is PERMANENT for the run.
    combat.run_fight is single-combat and never persists hp/max_hp, so
    unless tier05 carries the gain between fights, Feed is systematically
    undervalued and the point of the card vanishes.
    """
    p = state.player
    n = _amount(state, fx["amount"])
    p.max_hp += n
    p.hp += n
    state.emit("gain_max_hp", amount=n)


def _op_recall_to_draw(state: CombatState, fx: dict, card: Card) -> None:
    """Headbutt: put a chosen card from the discard pile on TOP of the draw
    pile. Index 0 IS the top -- state.draw pops index 0 and
    combat.surface_innate prepends. No-op on an empty discard pile."""
    p = state.player
    src = fx.get("from", "discard")
    if src != "discard":
        raise ValueError(f"unknown recall_to_draw source {src!r}")
    pos = fx.get("position", "top")
    if pos != "top":
        raise ValueError(f"unknown recall_to_draw position {pos!r}")
    for _ in range(_amount(state, fx.get("amount", 1))):
        if not p.discard_pile:
            return
        pick = _best_card(p.discard_pile)
        p.discard_pile.remove(pick)
        p.draw_pile.insert(0, pick)
        state.emit("recall_to_draw", card=pick.id)


def _op_transform_in_hand(state: CombatState, fx: dict, card: Card) -> None:
    """PrimalForce: transform every Attack in hand into GiantRock.

    CardCmd.Transform replaces the original AT ITS ORIGINAL PILE INDEX, so
    this replaces in place (same ordering argument as upgrade_in_hand).
    The `+` suffix convention in loader.get_card carries the upgraded
    variant, so the upgrade is a plain `into` string replace.

    The base game also gates on Card.IsTransformable. No tier0 flag exists
    for it: whether any Ironclad Attack is untransformable must be verified
    against the sheet, and adding a flag nothing sets would be an assumption
    wearing the costume of a check. Kit cards ARE excluded -- the v1.9
    invariant is that the Burst never leaves the kit.
    """
    from tier0.content import loader                # late import avoids cycle
    hand = state.player.hand
    filt = fx.get("filter")
    for i, c in enumerate(hand):
        if c.kit_card or (filt and c.type != filt):
            continue
        hand[i] = loader.get_card(fx["into"])
        state.emit("transform", was=c.id, into=hand[i].id)


# Backstop for nested free plays. The seen_states guard in
# combat._player_turn only samples BETWEEN pilot plays, so a Havoc chain
# that flips more Havocs is structurally invisible to it. Belongs in
# tier0/constants.py; it lives here because that file is owned by a
# concurrent edit -- move it when the sheet lands.
MAX_FREE_PLAY_DEPTH = 10


def _free_play(state: CombatState, card: Card,
               force_exhaust: bool = False) -> None:
    """Shared driver for the two base-game free plays: autoplay_from_draw
    (Havoc, Cascade) and the on-exhaust autoplay sweep (HowlFromBeyond).

    The actual play MUST go through combat.resolve_free_play, not
    _resolve_effects: every piece of card-play bookkeeping (pile routing,
    cards_played_this_turn, the `play` event, the per-card context block)
    lives in combat.play_card. Resolving effects directly here would let a
    free play silently clobber the OUTER card's killed_target and
    repeat_this state mid-resolution, and that corruption is invisible in
    results -- which is precisely why this is an engine change and not an op.

    CONTRACT with combat.resolve_free_play(state, card, force_exhaust):
      1. no energy deduction, no spark spend, no encore_cost gate;
      2. save and RESTORE the whole per-card context block resolve_card
         sets (current_card_companion, reactions_this_card,
         kills_this_card, fatal_kills_this_card, exhausted_this_card,
         detonations_at_card_start, repeat_requested,
         target_had_offelement_aura, current_attack_bonus, sparks_at_play,
         current_x, current_card_cost);
      3. current_card_cost = 0 for the free play (this_cost_zero and
         zero_cost_attacks_up both read it), then restore;
      4. route afterwards: force_exhaust -> exhaust; else card.exhaust or
         type == "power" -> exhaust; else discard. The card is NOT in hand,
         so it must not attempt hand.remove;
      5. increment cards_played_this_turn and emit play(cost=0, free=True),
         so MAX_CARDS_PER_TURN can see free plays;
      6. current_x = player.energy when card.cost == "X" (CardCmd.AutoPlay
         sets CapturedXValue from remaining energy).
    """
    from tier0.engine import combat                 # late import avoids cycle
    play = getattr(combat, "resolve_free_play", None)
    if play is None:
        raise NotImplementedError(
            "UNIMPLEMENTED: combat.resolve_free_play(state, card, "
            "force_exhaust) does not exist. Havoc, Cascade and "
            "HowlFromBeyond CANNOT be scored without it and must be "
            "excluded from the sheet. Refusing to approximate a free play "
            "by resolving effects inline: that silently corrupts the outer "
            "card's per-card context. See _free_play's contract docstring.")
    if state.free_play_depth >= MAX_FREE_PLAY_DEPTH:
        state.emit("degeneracy", kind="INFINITE", reason="free_play_depth")
        return
    state.free_play_depth += 1
    prev_random = state.force_random_targeting
    state.force_random_targeting = True
    try:
        play(state, card, force_exhaust=force_exhaust)
    finally:
        state.force_random_targeting = prev_random
        state.free_play_depth -= 1


def _op_autoplay_from_draw(state: CombatState, fx: dict, card: Card) -> None:
    """Havoc (1, forceExhaust) and Cascade (X, no forceExhaust).

    ORDERING, observable and deliberate: the dll selects ALL n cards first
    (moving each to the Play pile inside the selection loop) and only THEN
    plays them in order. Cascade for 3 therefore takes the top 3 up front
    and cannot re-select a card it already queued. ShuffleIfNecessary runs
    before EACH selection, not once.
    """
    p = state.player
    pos = fx.get("position", "top")
    if pos != "top":
        raise ValueError(f"unknown autoplay_from_draw position {pos!r}")
    queued = []
    for _ in range(_amount(state, fx.get("amount", 1))):
        if not p.draw_pile:
            state.shuffle_discard_into_draw()       # ShuffleIfNecessary
        if not p.draw_pile:
            break                                   # deck genuinely empty
        queued.append(p.draw_pile.pop(0))
    for queued_card in queued:
        if state.over:
            break
        _free_play(state, queued_card,
                   force_exhaust=fx.get("force_exhaust", False))


OPS = {
    "damage": _op_damage,
    "block": _op_block,
    "block_next_turn": _op_block_next_turn,
    "draw": _op_draw,
    "draw_while": _op_draw_while,
    "energy": _op_energy,
    "apply_power": _op_apply_power,
    "apply_aura": _op_apply_aura,
    "place_bomb": _op_place_bomb,
    "detonate": _op_detonate,
    "move_bombs": _op_move_bombs,
    "modify_bombs": _op_modify_bombs,
    "burst_energy": _op_burst_energy,
    "swirl": _op_swirl,
    "refresh_all_auras": _op_refresh_all_auras,
    "buff_next_attack": _op_buff_next_attack,
    "cost_mod": _op_cost_mod,
    "gain_spark": _op_gain_spark,
    "gain_encore": _op_gain_encore,
    "spend_encore": _op_spend_encore,
    "spotlight_designate": _op_spotlight_designate,
    "raise_fanfare_cap": _op_raise_fanfare_cap,
    "generate_guest_star": _op_generate_guest_star,
    "copy_spotlighted_in_hand": _op_copy_spotlighted_in_hand,
    "heal": _op_heal,
    "add_card": _op_add_card,
    "discard": _op_discard,
    "discard_for_sparks": _op_discard_for_sparks,
    "exhaust_from": _op_exhaust_from,
    "scry_discard": _op_scry_discard,
    "conditional": _op_conditional,
    "repeat_this": _op_repeat_this,
    "grow_damage": _op_grow_damage,
    "chance_bomb_per_detonation": _op_chance_bomb_per_detonation,
    "copy_companion_in_hand": _op_copy_companion_in_hand,
    "replay_next_companion": _op_replay_next_companion,
    "copy_companions_played_this_combat": _op_copy_companions_played,
    # --- base-game parity ops (the real Ironclad pool) ---
    "upgrade_in_hand": _op_upgrade_in_hand,
    "gain_max_hp": _op_gain_max_hp,
    "recall_to_draw": _op_recall_to_draw,
    "transform_in_hand": _op_transform_in_hand,
    "generate_from_pool": _op_generate_from_pool,
    "autoplay_from_draw": _op_autoplay_from_draw,
}


def _resolve_effects(state: CombatState, effects: list[dict],
                     card: Card) -> None:
    for fx in effects:
        if fx["op"] not in OPS:
            raise ValueError(f"card {card.id!r}: unknown op {fx['op']!r}")
        OPS[fx["op"]](state, fx, card)


def resolve_card(state: CombatState, card: Card) -> None:
    state.current_card_companion = card.is_companion    # control provenance
    state.reactions_this_card = 0
    state.kills_this_card = 0
    state.fatal_kills_this_card = 0
    state.exhausted_this_card = 0
    state.block_gains_this_card = 0
    state.salon_replacements_this_card = 0
    state.detonations_at_card_start = state.detonations_total
    state.repeat_requested = 0
    # Predicate snapshot: does the default target hold an off-element aura?
    living = state.living_enemies
    tgt = min(living, key=lambda e: e.hp) if living else None
    state.target_had_offelement_aura = bool(
        tgt and tgt.aura and tgt.aura != state.player.element)
    # Per-card flat attack bonus (Bennett's next_attack_up consumed here;
    # Nicole's celestial_gift, Bennett-burst attack_up_this_turn, and
    # Spark Knight Style's zero-cost rider all add per attack card).
    bonus = 0
    if card.type == "attack":
        p = state.player
        bonus = (p.powers.pop("next_attack_up", 0)
                 + p.powers.get("celestial_gift", 0)
                 + p.powers.get("attack_up_this_turn", 0))
        if state.current_card_cost == 0:
            bonus += p.powers.get("zero_cost_attacks_up", 0)
        # Rapturous Applause: attacks +N per 10 Fanfare ("stacks grant
        # flat power bonuses", kickoff §4). Reads the pool, spends nothing.
        n = p.powers.get("fanfare_attack_per10", 0)
        if n:
            bonus += n * (p.fanfare // 10)
    state.current_attack_bonus = bonus

    _resolve_effects(state, card.effects, card)
    if state.repeat_requested:                          # Perfect Timing
        times, state.repeat_requested = state.repeat_requested, 0
        for _ in range(times):
            _resolve_effects(
                state,
                [fx for fx in card.effects if fx["op"] != "repeat_this"
                 and not (fx["op"] == "conditional"
                          and any(e.get("op") == "repeat_this"
                                  for e in fx.get("then", [])))],
                card)


# --- player-side power triggers, called from the combat loop ---

def player_turn_start_triggers(state: CombatState) -> None:
    p = state.player
    if "ethereal_spotlight" in p.relic_hooks:           # Furina's relic
        # Selector to hand each turn (kickoff §3.1). Ethereal: unplayed
        # copies vanish at end of turn (combat loop), so the deck never
        # silts up with selectors. Emits its own event, NOT add_card --
        # whether selector cadence counts toward A5 velocity is an open
        # accounting ruling; until ruled it must not inflate the axis.
        from tier0.content import loader                # late import (cycle)
        if (not any(c.id == "ethereal_spotlight" for c in p.hand)
                and len(p.hand) < C.MAX_HAND_SIZE):
            p.hand.append(loader.get_card("ethereal_spotlight"))
            state.emit("selector_granted")
    n = p.powers.pop("block_next_turn", 0)              # Charlotte
    if n:
        p.block += n
        state.emit("block", amount=n)
    salon_tick(state)                                   # Furina (kickoff §5)
    if p.powers.get("celestial_gift", 0):               # Nicole
        p.block += C.CELESTIAL_GIFT_BLOCK
    n = p.powers.get("spark_per_turn", 0)               # Endless Fireworks
    if n:
        gain_sparks(state, n)
    n = p.powers.get("bomb_and_spark_per_turn", 0)      # Playtime Forever
    for _ in range(n):
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            enemy.bombs.append(Bomb(damage=C.PLAYTIME_BOMB_DAMAGE,
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=C.PLAYTIME_BOMB_DAMAGE)
        gain_sparks(state, 1)


def salon_tick(state: CombatState) -> None:
    """Salon v2 (rework plan §1): each active member performs its UNIQUE
    slot passive at the START of the player turn, in queue order
    (Klee-bomb timing, not Oz timing -- the sheet-pass 1 measurement
    decision stands: end-of-turn upkeep drained the buffer BEFORE enemy
    hits and zeroed her elite A4; start-of-turn ticks let absorption take
    first bite and the upkeep eats what survived the night). Upkeep is
    unchanged from v1: each member pays 1 Encore for full numerics; a dry
    member cannot overdraw HP and resolves numerics at three-quarters
    (hydro application on damage ticks still applies either way). Numeric
    amounts carry the Fanfare Focus term + Grand Salon (_salon_amount)."""
    p = state.player
    for member in list(p.salon):
        if not p.alive or not state.living_enemies:
            break
        spec = C.SALON_MEMBERS[member]["tick"]
        paid = p.encore >= C.SALON_TICK_ENCORE_COST
        if paid:
            resources.spend_encore(state, C.SALON_TICK_ENCORE_COST)

        def _num(base: int) -> int:
            amt = _salon_amount(state, base)
            return amt if paid else int(amt * C.SALON_DRY_DAMAGE_MULT)

        dmg = spec.get("damage", 0)
        if dmg:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, _num(dmg), element="hydro",
                                 source="salon")
        blk = spec.get("block", 0)
        if blk:
            amt = _num(blk)
            p.block += amt
            state.emit("block", amount=amt)
        if p.burst_max:
            p.burst_energy += C.SALON_TICK_BURST     # §1 particle economy


def _exhaust_autoplay_sweep(state: CombatState) -> None:
    """HowlFromBeyond: Hook.AfterAutoPostPlayPhaseEntered, which the game's
    CombatManager invokes ONCE per player turn while ending the turn
    (Phase = AutoPostPlay, immediately before BeforeTurnEnd). Howl's
    override fires when the card is sitting in the player's EXHAUST pile
    and auto-plays it for free; it carries no Exhaust keyword, so
    GetResultPileTypeForCardPlay sends it to DISCARD afterwards.

    ONE-SHOT, NOT A LOOP. The flagged cards are snapshotted before any of
    them plays, and each is pulled out of the exhaust pile first -- so a
    card that re-exhausts itself cannot trigger again this sweep. The loop
    reading is the obvious wrong implementation; this must stay pinned by a
    test.

    Only reachable via another card exhausting Howl (Brand, BurningPact,
    TrueGrit+, Stoke, Havoc's forceExhaust). Zero flagged cards is the
    universal case -- Klee and Furina never enter this loop body.
    """
    p = state.player
    flagged = [c for c in p.exhaust_pile if c.on_exhaust_autoplay]
    for c in flagged:
        if state.over or not p.alive:
            return
        p.exhaust_pile.remove(c)
        _free_play(state, c, force_exhaust=False)


def player_turn_end_triggers(state: CombatState) -> None:
    p = state.player
    # Runs FIRST: the game's AutoPostPlay phase lands after the player's
    # plays and before turn end, so the free play resolves ahead of the
    # other end-of-turn triggers and well ahead of the enemy turn.
    _exhaust_autoplay_sweep(state)
    if p.powers.get("sparks_n_splash", 0):              # the Burst
        for _ in range(C.SPARKS_N_SPLASH_HITS):
            if not state.living_enemies:
                break
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.SPARKS_N_SPLASH_HIT_DMG,
                                 element="pyro", source="burst")
        p.powers["sparks_n_splash"] -= 1
    if p.powers.get("oz_summon", 0):                    # Fischl
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.OZ_DMG,
                                 element="electro", source="companion")
        p.powers["oz_summon"] -= 1
    if p.powers.get("witchs_flame", 0):                 # Durin (permanent)
        # Turn Klee's Pyro saturation into a setup window instead of adding
        # still more Pyro. Each consumed aura pays damage + Burst Energy, then
        # leaves the enemy clear for Hydro/Cryo to establish the next reaction.
        damage = p.powers["witchs_flame"]
        for enemy in list(state.living_enemies):
            if enemy.aura != "pyro":
                continue
            enemy.aura = None
            enemy.aura_turns_left = 0
            deal_damage_to_enemy(state, enemy, damage,
                                 element=None, source="companion")
            if p.burst_max:
                p.burst_energy += C.WITCHS_FLAME_BURST
            state.emit("witchs_flame_consumed", target=enemy.name,
                       burst_energy=C.WITCHS_FLAME_BURST)
    if p.powers.get("solar_isotoma", 0):                # Albedo, 3 turns
        p.powers["solar_isotoma"] -= 1
    p.powers.pop("attack_up_this_turn", None)           # Bennett burst
