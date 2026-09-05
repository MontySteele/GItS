"""Rule-based greedy pilot (spec §6).

1. If lethal is playable this turn, play toward it.
2. Else if incoming damage >= BLOCK_PANIC_THRESHOLD of remaining HP,
   prioritize block until covered.
3. Else weighted scoring per pilots/*.yaml.

Deliberately dumb; both Klee and reference decks use the same pilot.
"""

from __future__ import annotations

import contextlib
from typing import Optional

from tier0 import constants as C
from tier0.engine import effects, klee_overhaul, powers, resources
from tier0.engine.combat import (card_cost, card_playable, spark_cost,
                                 spark_price, spark_threshold)
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


# ---------------------------------------------------------------------------
#  EB-144: the pilot's conditional literacy, DECLARED rather than implied.
#
#  `_active_effects`'s chain used to end in a bare `else: continue`, which
#  yields NEITHER branch -- so a predicate the pilot had never been taught
#  made it price the whole conditional at zero, silently, with no test that
#  could notice. The `C19` audit found TEN sheet rows in that hole, not the
#  two the standing read names: `hold_the_line` + `warmup_act`
#  (enemy_intends_attack), `take_it_from_the_top` + `curtain_cue` +
#  `directors_cut` (spotlight_moved_this_turn), `many_waters_melody` +
#  `waters_embrace` + `tempo_change` (has_salon_members), `read_the_current`
#  (charge_at_least_10) and `tail_of_flame` (this_cost_zero). Seven of the
#  ten predate `W3` by months.
#
#  The two collections below are that hole made visible. Every predicate any
#  sheet PRINTS must appear in exactly one of them, and
#  `test_eb144_predicate_literacy.py` fails the build otherwise -- a lint, not
#  a comment, because the failure mode is silence. WHICH sheets are loadable
#  depends on the checkout: the roster always, the `real_*` reference pools
#  only where `game_ref/` is present, so the reference half of that lint is
#  discharged by the S7 gate in `klee-mod/build/validate.ps1` and skipped
#  everywhere else.
#
#  SCORABLE: evaluated live at score time, so the correct branch is scored.
#  BLIND:    MID-RESOLUTION by nature -- the fact the branch reads does not
#            exist until the card is already resolving, so there is no honest
#            score-time answer and the historic top-level-only valuation is
#            kept deliberately. Being listed here is the claim that this was
#            decided, not forgotten.
# ---------------------------------------------------------------------------

# Names the pilot delegates VERBATIM to `effects._predicate`: pure reads of
# current state, with no snapshot field and no telemetry side effect, so one
# rule asked from both sides beats a second copy (the Track C.2 lesson that
# the fanfare clamp below records the other half of).
_ENGINE_LIVE_PREDICATES = frozenset({
    "enemy_intends_attack",
    "has_salon_members",
    "spotlight_moved_this_turn",
})
_ENGINE_LIVE_PREFIXES = ("charge_at_least_",)

SCORABLE_PREDICATES = frozenset({
    "has_spark",
    "target_has_nonpyro_aura",
    # R189 C2's any-aura sibling, read live below on the same pattern as the
    # off-element one -- so `elemental_ecstasy`'s Block keeps being scored at
    # score time instead of dropping into EB-144's silent-zero hole the
    # moment its predicate was renamed.
    "target_has_aura",
    "card_exhausted_this_turn",
    "hp_lost_this_turn",
    "reaction_triggered_this_turn",
    "this_cost_zero",
}) | _ENGINE_LIVE_PREDICATES
SCORABLE_PREDICATE_PREFIXES = (
    "target_has_power_",
    "exhaust_pile_at_least_",
    "fanfare_at_least_",
    "encore_at_least_",
) + _ENGINE_LIVE_PREFIXES

BLIND_PREDICATES = frozenset({
    # Both read a fact produced BY this card's own earlier ops, mid-
    # resolution. Nothing at score time can answer them without simulating
    # the card, which the pilot deliberately does not do.
    "reaction_triggered_by_this",
    "killed_target",
    # The three below are printed ONLY by the `real_ironclad` / `real_silent`
    # reference pools, which live in the gitignored `game_ref/` and so are
    # invisible to a fresh clone and to CI. They were untriaged until the S7
    # deploy gate -- the one place the suite runs WITH `game_ref/` present --
    # went red on them.
    #
    # `killed_target_fatal` (ic_feed, si_the_hunt) and `drew_skill_this_card`
    # (si_escape_plan) are `killed_target`'s own class: a fact produced by
    # this card's earlier ops, mid-resolution, unanswerable at score time
    # without simulating the card.
    "killed_target_fatal",
    "drew_skill_this_card",
    # `self_has_power_tracking` (si_tracking) is NOT that class -- it is a
    # pure read of a power the player already holds, and
    # `effects._predicate` would answer it live and correctly. It is declared
    # blind anyway, and deliberately: these two collections are read by the
    # lint and by nothing else (`_active_effects`'s if-chain names its
    # predicates itself), so a name landing here moves no measured number,
    # while making it SCORABLE would change how the `real_silent` anchor
    # scores its hand and so force a `P` stamp bump -- and a standing
    # re-baseline is being taken at `P11` right now. The live read is a
    # candidate for a future `P` window; it is not a defect, so it is not
    # backlog.
    "self_has_power_tracking",
})
BLIND_PREDICATE_PREFIXES: tuple[str, ...] = ()


def predicate_is_scorable(name: str) -> bool:
    """Would `_active_effects` evaluate `name` and score the right branch?"""
    return (name in SCORABLE_PREDICATES
            or name.startswith(SCORABLE_PREDICATE_PREFIXES))


def predicate_is_declared_blind(name: str) -> bool:
    return (name in BLIND_PREDICATES
            or (bool(BLIND_PREDICATE_PREFIXES)
                and name.startswith(BLIND_PREDICATE_PREFIXES)))


def _plan_discounted(fx: dict) -> dict:
    """One planned clause, at `C.PLAN_DELAY_DISCOUNT` of its printed face.

    EB-311. THE DISCOUNT IS APPLIED TO THE AMOUNT rather than to each scoring
    term, and the reason is arithmetic rather than taste: every term downstream
    of `_active_effects` that prices one of these clauses is LINEAR in
    `amount` (`_expected_damage` multiplies it by hits, `_raw_block` by times,
    `_scaling_value` by the debuff dial, `_tempo_value` reads it straight), so
    scaling the amount once here is the same number as scaling five terms and
    it cannot fall out of step with a sixth added later.

    A COPY, NEVER THE CARD'S OWN DICT. `card.plan` is the sheet's list, shared
    by every instance of the row and read again by
    `kokomi_plan._resolve_clause` when the Plan is actually carried out;
    scaling it in place would make the forecast rewrite the card it forecast.

    A clause with no numeric `amount` -- the Max-HP fraction, the exhaust
    replay -- passes through untouched. Neither is priced by any term today;
    the discount declines to invent a price for them on the way past.

    `times` IS NOT DISCOUNTED (`EB-492`). It is a COUNT OF HITS and not a
    magnitude: Pincer's planned line is three hits of a discounted 3, which is
    what every term downstream already reads (`_expected_damage` multiplies
    `amount` by `times`), and scaling both would take the delay twice.

    THE DURATION CARVE-OUT IS GONE with the clause that needed it: `plan_twice`
    was the one planned amount that meant TURNS, and Nereid's Ascension is a
    Power now, so every remaining numeric `amount` in a `plan:` list is a
    magnitude.
    """
    amount = fx.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        return fx
    return {**fx, "amount": amount * C.PLAN_DELAY_DISCOUNT}


def _active_effects(state: CombatState, effect_list: list[dict],
                    card: Optional[Card] = None):
    """Yield runtime-formula branches the pilot is explicitly able to read.

    Mid-resolution predicates (reaction_triggered_by_this, killed_target)
    deliberately keep their historic top-level-only valuation. Pure current-
    state Klee predicates are safe to read here, as are the pass-5/pass-6
    Ironclad predicates below.

    `card` is the HOST card whose body this is, when there is one. Exactly one
    predicate needs it (`this_cost_zero`, which is a question about the card
    being scored and not about the state), and a mode body probed without a
    host still scores -- it just cannot answer that one.

    THE PLAN SWAP (QUARANTINED, C.KOKOMI_OVERHAUL) IS THE FIRST THING THIS
    FUNCTION DOES, and it is here rather than at the fifteen call sites for the
    reason the `choose_one` branch below is here: this is the ONE place the
    pilot turns a printed face into "what will actually happen", so it is the
    one place the other half of a Plan card's face can be substituted without
    every valuation term having to learn the rule.

    IT ASKS THE ENGINE, the Track C.2 lesson: `kokomi_plan.plan_aimed_at_pet`
    is the same pure function `effects._resolve_card_bound` calls a moment
    later to decide which half to RUN, so the pilot's read and the play cannot
    disagree. A card headed for the jellyfish does none of its now-line, so
    scoring the now-line would price a play that is not going to happen -- and
    four rows (Ambush, War Council, Chain of Command, Battle Plan) print an
    EMPTY body, so without the swap they would score zero and never be played.

    THE TURN OF DELAY IS NOW MODELLED (`EB-311`), and this paragraph used to
    say the opposite: a planned clause was valued at FACE, as though it landed
    now, and the note called discounting it a `POLICY_VERSION` question. It is
    discounted here by `C.PLAN_DELAY_DISCOUNT` -- the SAME constant
    `tier05.draft._static_power` prices a `plan:` list with, so the pilot that
    ranks a hand and the drafter that ranks an offer screen have one opinion
    about what a Plan is worth between them instead of two opposite ones (the
    drafter's was ZERO).

    NO `POLICY_VERSION` BUMP, and that is a claim about OUTPUT rather than an
    exemption. The swap this rides is gated on `plan_aimed_at_pet`, which is
    False without `C.KOKOMI_OVERHAUL` AND without Kokomi in the seat, and only
    a `proto_` row carries a `plan:` list at all -- so every pilot decision in
    the published world is byte-identical with and without this discount, which
    `tier05/tests/test_eb311_plan_pricing.py` pins rather than asserts. When
    the arm leaves quarantine, THAT is the change that moves `P`.
    """
    planned = False
    if (card is not None and card.plan and effect_list is card.effects
            and effects.kokomi_plan.plan_aimed_at_pet(state, card)):
        effect_list = card.plan
        planned = True
    for fx in effect_list:
        if fx["op"] == "conditional":
            name = fx["if"]
            if name == "has_spark":
                ready = state.player.sparks > 0
            elif name == "target_has_nonpyro_aura":
                target = effects._default_target(state)
                ready = bool(target and target.aura
                             and target.aura != state.player.element)
            elif name == "target_has_aura":
                # The forecast of the engine's card-start snapshot: at score
                # time no aim is bound yet, so the default aim is the honest
                # answer -- exactly what the off-element branch above does.
                target = effects._default_target(state)
                ready = bool(target and target.aura)
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
            elif name == "this_cost_zero":
                # EB-144. The ENGINE reads `state.current_card_cost`, which at
                # score time still holds the LAST resolved card's cost -- so
                # delegating would be worse than not reading it at all. The
                # pilot reads `card_cost(state, card)`, which is literally the
                # number `combat.play_card` is about to assign to that field
                # one line before this branch resolves. No host card (a mode
                # body probed on a neutral frame) means no answer, and the
                # historic zero-valuation stands for that case only.
                if card is None:
                    continue
                ready = card_cost(state, card) == 0
            elif (name in _ENGINE_LIVE_PREDICATES
                  or name.startswith(_ENGINE_LIVE_PREFIXES)):
                # EB-144. Pure current-state reads with no snapshot field and
                # no telemetry side effect, so the pilot ASKS THE ENGINE
                # rather than keeping a second copy of the rule -- the same
                # round trip `choose_one` below makes, and the half of the
                # Track C.2 lesson the fanfare clamp above cannot take (that
                # one goes through `resources.readable` precisely BECAUSE the
                # engine's predicate files a census row on the way past).
                ready = effects._predicate(state, name)
            else:
                continue
            branch = fx["then"] if ready else fx.get("else", [])
            yield from _active_effects(state, branch, card)
        elif fx["op"] == "choose_one":
            # EB-118: the pilot forecasts the mode it will actually take by
            # asking the ENGINE's chooser rather than keeping a second copy
            # of the rule -- the Track C.2 lesson the fanfare clamp above
            # records. With the switch off that chooser is the staged fixed
            # index; with it on it is `choose_mode` below, and the round trip
            # (pilot -> engine seam -> pilot) is deliberate: one rule, asked
            # the same way from both sides. `None` for the card is why
            # `_mode_probe` scores a mode body on a neutral frame -- there is
            # no host card to offer here, and a score that needed one would
            # make this forecast disagree with the play it forecasts.
            modes = fx[effects.MODES_KEY]
            index = effects._chosen_mode(state, modes, None)
            yield from _active_effects(state, modes[index]["effects"], card)
        else:
            yield _plan_discounted(fx) if planned else fx


def _salon_verb_yield(state: CombatState, card: Card
                      ) -> tuple[float, float, float]:
    """EB-144: what this card's SALON VERBS pay right now, as
    `(damage, block, encore_spent)`.

    `salon_rotate` and `salon_perform` shipped in Phase 2 and stayed unprinted
    until `change_the_bill` (`C19`), so the pilot had never been taught either
    and the card scored as its Block 3 and nothing else. Neither verb gets a
    number of its own here; both are valued by DOING WHAT THE RESOLVER DOES
    and pricing the result through the terms that already price damage, Block
    and Encore. Change `SALON_MEMBERS` and this moves with it.

      * `salon_perform` runs `salon_member_act` on the LEFTMOST member, `N`
        times, and that function's whole payout is one `salon_tick_amount`
        per tick -- so this asks that same function (`note=False`: a forecast
        must not file a `fanfare_read` census row, which is the only reason
        the kwarg exists). Damage members pay damage, the Usher pays Block,
        and the Encore upkeep is charged per tick that can afford it, exactly
        as `salon_member_act` charges it, with the dry three-quarters falling
        out of `salon_tick_amount` for the ticks that cannot.
      * `salon_rotate` is worth ZERO ON ITS OWN and that is not a placeholder
        -- it is the drafter's ratified reading (`STATIC_SALON_ROTATE_VALUE`,
        EB-118 §5.5): rotating delivers nothing, its whole value is WHICH
        member the next consumer finds. What it does get here is the thing
        the drafter cannot see, because the drafter has no stage: inside one
        card body the rotate moves the queue BEFORE a later `salon_perform`
        reads it, so `offset` picks the member that will actually perform.
        `change_the_bill` prints exactly that pair, and with a Crabaletta in
        front of an Usher the two orderings score differently -- correctly.

    Conservative by construction, disclosed rather than papered over: the
    Chevalmarin tick's hydro application and the `SALON_TICK_BURST` particle
    are NOT priced (no term here owns either), a stage this card would DEPLOY
    into is not counted (the queue is read as it stands at score time), and a
    perform that would kill the last enemy mid-loop still counts its later
    ticks. Every one of those understates the verb.
    """
    p = state.player
    # `salon_member_act`'s own refusal, and `_op_salon_perform`'s whiff: an
    # empty stage, a dead player, or nothing left to act against pays nothing
    # and the resolver says so out loud with `salon_perform_whiffed`.
    if not p.salon or not p.alive or not state.living_enemies:
        return (0.0, 0.0, 0.0)
    offset = 0
    dmg = blk = spent = 0.0
    encore = p.encore
    for fx in _active_effects(state, card.effects, card):
        op = fx["op"]
        if op == "salon_rotate":
            offset += _est(state, fx.get("amount", 1), 1)
        elif op == "salon_perform":
            member = p.salon[offset % len(p.salon)]
            spec = C.SALON_MEMBERS[member]["tick"]
            for _ in range(int(_est(state, fx.get("amount", 1), 1))):
                paid = encore >= C.SALON_TICK_ENCORE_COST
                amt = effects.salon_tick_amount(state, member, paid,
                                                note=False)
                if spec.get("damage", 0):
                    # Same pipeline head the pilot's card damage uses, and
                    # the same one `deal_damage_to_enemy` opens with.
                    dmg += powers.modify_damage_dealt(p, amt)
                if spec.get("block", 0):
                    blk += amt
                if paid:
                    encore -= C.SALON_TICK_ENCORE_COST
                    spent += C.SALON_TICK_ENCORE_COST
    return (dmg, blk, spent)


def _expected_damage(state: CombatState, card: Card) -> float:
    total = _salon_verb_yield(state, card)[0]
    living = state.living_enemies
    # EB-145: built ONLY when a printed formula asks for it, so a card that
    # reads no selection allocates nothing and scores through the identical
    # arithmetic it scored through before (`_formula_amount`'s first branch).
    selection: dict = {}
    # v0.4 W1 (priest-pilot audit): the flat per-attack bonus the engine folds
    # in at resolution — Bennett's next_attack_up, celestial_gift, the Fanfare
    # term, and Kokomi's Ceremonial Garment Charge read. The pilot used to see
    # NONE of it, so it priced every attack at its printed number and played
    # straight through its own buff windows. Same helper the engine calls, so
    # the estimate cannot drift from what resolves; it is a pure read.
    #
    # `valuation=True` (EB-253): the Fanfare term inside that helper files a
    # `fanfare_read`, and scoring a hand is not playing it. Same declaration
    # the `bonus_formula` call below already carries for EB-242's instrument.
    flat = effects.flat_attack_bonus(state, card, card_cost(state, card),
                                     valuation=True)
    for fx in _active_effects(state, card.effects, card):
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
            amount = (_formula_amount(state, fx, card, selection)
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
                    # valuation=True (EB-242): an estimate, not a play, so it
                    # ticks no reads-per-turn instrument.
                    per_hit += effects._bonus_formula(
                        state, fx["bonus_formula"], valuation=True)
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
        # --- THE KLEE OVERHAUL'S FOUR DAMAGE VERBS (QUARANTINED,
        # C.KLEE_OVERHAUL). REACHABLE ONLY ON THE ARM BY CONSTRUCTION: no
        # shipped row prints one of these ops, and `loader._card_prototype`
        # refuses a `proto_ko_` id with the flag off, so every shipped arm's
        # score is byte-identical and `POLICY_VERSION` covers the same
        # decisions it covered before.
        #
        # WHY THEY ARE HERE AT ALL. Without them the pilot priced Ka-pow! and
        # Jumpy Dumpty at ZERO and played neither: a first read of the arm
        # reported 27 plays, all of them Strike and Defend, and 18 dead in
        # hand. That is an instrument artifact, not a design finding, and it
        # would have been quoted as one.
        #
        # WHAT THEY DELIBERATELY UNDERSTATE, stated rather than left to be
        # discovered -- the `summon_kurage` arm's own posture, and the safe
        # direction: GROWTH (a Bomb left to cook is worth more than its size
        # today), the SPARK an explosion mints, Jumpy Dumpty's Mine PAYLOAD,
        # the Mine's defensive half, and every reaction. The pilot has no
        # cook-or-cash policy; it reads the board's numbers and nothing else.
        elif fx["op"] == "set_off":
            # THE PILE IS THE CARD'S REAL DAMAGE, and it is a plain board read
            # rather than a forecast -- exactly the number the mod's badge
            # shows on the enemy. The card's own printed hit rides on top,
            # through the same `per_hit` arithmetic a `damage` row takes.
            printed = int(fx.get("damage", 0) or 0)
            times = _est(state, fx.get("times", 1), 1)
            hit_targets = (living if fx.get("target") == "all_enemies"
                           else [effects._default_target(state)])
            hit_targets = [t for t in hit_targets if t is not None]
            for enemy in hit_targets:
                total += klee_overhaul.total_size(enemy)
            if printed:
                per_hit = powers.modify_damage_dealt(
                    state.player, printed) + flat
                total += per_hit * times * max(1, len(hit_targets))
        elif fx["op"] == "plant_bomb":
            # `place_bomb`'s line one op over, at its own face value: the size
            # planted, per body it lands on. Undiscounted for the same reason
            # the shipped line is -- a Bomb that is never cashed is a play the
            # pilot got wrong, not a number this function should hedge.
            n = len(living) if fx.get("target") == "all_enemies" else 1
            total += int(fx.get("size", 0)) * n
        elif fx["op"] in ("grow_bombs", "merge_bombs"):
            # Growth is damage the pile will deal when it is finally cashed,
            # and it is worth nothing at all on a board with no pile -- which
            # is the same sentence `EB-261` gates Quick Fuse's playability on.
            amount = int(fx.get("amount", fx.get("growth", 0)) or 0)
            if any(klee_overhaul.holds_charge(e) for e in living):
                total += amount
        elif fx["op"] == "damage_set_off_total":
            # Big Badda Boom's second clause hits again for what the Bombs
            # dealt, so the pile counts TWICE on that row -- once for the Set
            # off above it and once here.
            enemy = effects._default_target(state)
            if enemy is not None:
                total += klee_overhaul.total_size(enemy)
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
            if C.KURAGE_MEMORY:
                # QUARANTINED. Under the memory rule neither term below
                # exists: the summon is persistent (no duration to multiply)
                # and the pulse carries no Charge multiplier. The pilot is
                # priced at ONE flat pulse and no more, which UNDERSTATES a
                # persistent jellyfish badly -- and that is the declared, safe
                # direction to be wrong, the same stance the shipped comment
                # above takes about a late-fight summon.
                #
                # WHAT THE PILOT DOES NOT SEE, stated rather than left to be
                # discovered: it does not value the QUEUE at all. It does not
                # know that playing a Companion banks a free replay, does not
                # know a fire is one turn away, and does not steer play order.
                # A flagged sim arm therefore exercises the RULE end to end
                # and NOT the decision the rule exists for -- which is exactly
                # why the proposal's §6 routes acceptance through whole-fight
                # BLIND PLAY and forbids quoting any number off this arm.
                total += C.KURAGE_PULSE_BASE * C.PILOT_FUTURE_DAMAGE_DISCOUNT
            else:
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
    # EB-144: the Usher's tick prints Block, so a `salon_perform` that lands
    # on her is Block this turn and belongs in the same number the panic-block
    # rule and _block_value read.
    total = _salon_verb_yield(state, card)[1]
    selection: dict = {}      # EB-145, see _expected_damage
    for fx in _active_effects(state, card.effects, card):
        if fx["op"] != "block":
            continue
        amount = (_formula_amount(state, fx, card, selection)
                  if "amount_formula" in fx else fx["amount"])
        # F-B1: Block carries the same scaling rider damage does, so the
        # pilot has to read it or it prices a Fanfare-scaled blocker at its
        # printed number and blocks with the wrong card. Same helper the
        # engine calls, so the estimate cannot drift from what resolves.
        if "bonus_formula" in fx:
            # valuation=True (EB-242): the same helper the engine calls, so
            # the estimate cannot drift -- and the same reason it must not
            # tally, because pricing a blocker is not blocking with it.
            amount += effects._bonus_formula(state, fx["bonus_formula"],
                                             valuation=True)
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
    for fx in _active_effects(state, card.effects, card):
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

        # `front_enemy` (QUARANTINED, C.KOKOMI_OVERHAUL) is a SINGLE-target
        # spelling and rides this branch rather than falling through to the
        # random one, which would price one planned Hydro hit as a spread. The
        # aim it estimates against is this engine's default (lowest HP) and not
        # literally the leftmost, which is the same approximation every other
        # single-target estimate here makes.
        if target in ("enemy", "front_enemy"):
            # Single-target Swirl is deliberately aura-aware, and since
            # EB-139 / R211 (`C20`) it is aura-aware AT THE BIND
            # (`effects.bind_card_aim`) rather than inside `_op_swirl`: a card
            # carrying an aimed Swirl binds its WHOLE play to the lowest-HP
            # aura-bearer. This line is unchanged and needed no weight, because
            # it already computed that creature -- `reactable` is the living
            # bodies holding an off-anemo aura, and no aura is ever ANEMO
            # (`reactions.AURA_ELEMENTS` is pyro/hydro/electro/cryo; anemo and
            # geo are trigger-only), so it is the same set the engine now binds
            # from. The estimate and the resolution moved TOWARD each other.
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
    for fx in _active_effects(state, card.effects, card):
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
    not stopping THIS turn's hits when drawn late.

    EB-144: a `salon_perform` BUYS its tick with the same currency, one point
    of upkeep per tick that can pay, so the bill is charged here at the price
    a point is credited at two lines up. Symmetric by construction rather
    than picked -- an on-demand tick that costs a point of Encore must not be
    free to a scorer that pays a point of Encore 0.8.
    """
    encore = sum(fx.get("amount", 0) for fx in card.effects
                 if fx["op"] == "gain_encore"
                 and isinstance(fx.get("amount"), int))
    encore -= _salon_verb_yield(state, card)[2]
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
    for fx in _active_effects(state, card.effects, card):
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

# --- EB-118 pilot policies. LIVE since the EB-118 Phase-2A flip (2026-08-24).
# Two decisions the engine used to make with a placeholder heuristic live here,
# behind ONE switch -- which now DEFAULTS ON.
#
# WHY A SWITCH, AND WHAT IT GUARDS NOW: both policies change what the pilot
# DECIDES, so every Klee and Kokomi tier-0.5 number re-baselined at the flip.
# The switch did NOT become decoration when it was thrown -- the pre-policy
# code is still live behind it (`effects._op_place_bomb` concentration form
# falls back to `_pick_targets`' lowest-HP aim, `effects._op_exhaust_from`
# chosen form to `_worst_card`'s highest-cost non-Attack), and that fallback is
# the only way the pre-flip world can still be run: it is what the W4 sweep's
# byte-identity arm forces off (`tier05/pilot_weight_sweep.sandbox`,
# `force=False`) to prove that a weight reaches the engine ONLY through this
# gate. Pin: `tier0/tests/test_eb118_switch_off.py`, which flipped from "the
# shipped default is off" to "the legacy path is preserved and reachable".
#
# THE FLIP WAS ONE EDIT AND THREE INTEGERS, and no fourth: `POLICY_VERSION`
# 7 -> 8 (tier05/draft.py), `C.PILOT_WEIGHTS_VERSION` 2 -> 3, and this switch.
# 2C's `MODE_CHOOSER_ENABLED` is a DIFFERENT switch with its own activation
# window (R191) and is not touched by this one.
#
# The constants below are filed here rather than in constants.py for the reason
# at the head of the STOKE_* block -- constants.py is the surface the C# parity
# gate compares by value and the mod ships no bot -- and they JOIN the set
# C.PILOT_WEIGHTS_VERSION labels. That stamp moved with the switch, in the same
# landing edit: while the switch was off no weight below was ever read, so the
# labeled set was arithmetically unchanged and the stamp could not move first.
#
# HAND-PICKED, AND STILL HAND-PICKED AFTER THE SWEEP. The values below were
# chosen by hand and never swept when they were written; W4
# (`tier05/pilot_weight_sweep.py`) RAN inside this same activation window and
# returned the null it predicted in advance -- 78 weight points classified,
# every one INSEPARABLE, no DOMINATING point, so the adoption rule decided
# without a judgement call and NOTHING WAS ADOPTED. `EXHAUST_JUNK_BONUS` was
# refused by the R67 dead-knob gate (post-C11 Kokomi's rotation law drops junk
# before the chooser ever sees it) and is left alone rather than fed a read,
# per R33. Any later change to one of these is still its own
# `C.PILOT_WEIGHTS_VERSION` bump with the sweep row cited -- and most of that
# grid's outcomes are [USER]'s call, not the integration's (that module's
# TASTE / TUNING LINE).
PILOT_POLICIES_ENABLED = True

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

# Mode valuation (EB-118 2C, R191/R194/R205). Which body a `choose_one`
# resolves. LIVE since the EB-118 Phase-2C flip (2026-08-24) -- the SECOND and
# LAST of Phase 2's two activation windows.
# ADDITIVE to the block above and to nothing else: no weight that existed
# before this edit changes, which is what lets the 2A weight sweep and this
# slice sit in the same file without one renumbering the other.
#
# ITS OWN SWITCH, not `PILOT_POLICIES_ENABLED`. R191 ruled that the mode
# chooser takes its OWN activation window, and the 2A pair flipped first in the
# ruled sequence -- so a shared flag would have activated this policy inside
# 2A's window and left 2C with no flip of its own to attribute anything to. Two
# flags, two windows, two POLICY_VERSION bumps; the sibling ruling that 2B and
# 2C may not share a D window is the same argument about the same pair of
# slices.
#
# THE SWITCH DID NOT BECOME DECORATION WHEN IT WAS THROWN, exactly as the 2A
# pair's did not: off, `effects._chosen_mode` returns the fixed index the seam
# was staged with, and that path is still live behind the flag and still
# pinned (`test_eb118_switch_off`). It is the only way the pre-flip world can
# be run.
#
# THE FLIP WAS ONE EDIT AND THREE INTEGERS: `POLICY_VERSION` 8 -> 9
# (tier05/draft.py), `C.PILOT_WEIGHTS_VERSION` 3 -> 4, and this switch. A
# FOURTH integer moves in the SAME landing on its OWN ground and is not part of
# the flip -- `C.CONSTANTS_VERSION` 13 -> 14, for the mode-2 re-body, which is
# a material card-sheet edit under R179/M15 and would have owed a bump with the
# chooser still off.
#
# BOTH WEIGHTS ARE HAND-PICKED AND UNSWEPT, AND STILL ARE. The W4 sweep pattern
# was available in this window and was NOT run over these two: the pair the
# chooser reads was re-bodied instead (R205), on the finding that no setting of
# these weights could rescue it -- mode 1 carries no state-dependent term, so
# the dominance was structural, and both weights are SHARED policy whose
# bending reprices every Encore generator in the pool. Any later change to one
# of them is still its own `C.PILOT_WEIGHTS_VERSION` bump.
MODE_CHOOSER_ENABLED = True
MODE_OVERDRAW_HP_VALUE = 1.0   # per point of TRUE HP a `spend_encore` shortfall
                               # drains. The chooser's scale is already "points
                               # of damage": _block_value prices Block by the
                               # damage it prevents and heal by the HP it
                               # restores, both at 1. A point of HP paid and a
                               # point of damage taken are the same point, so
                               # this weight is 1.0 for the same reason
                               # BOMB_SUPPRESSION_VALUE is
MODE_TIE_EPSILON = 1e-9        # the band inside which two modes are a TIE.
                               # Float noise must not decide a mode, because the
                               # tie-break is the rule that keeps replays stable
                               # and reproduces the pre-flip placeholder

# EB-29t (POLICY 6): the promoted Test Subject reads (R128). The Strength an
# Enrage trigger grants is PERMANENT, but the greedy pilot prices it over a
# deliberately short horizon of future attack turns -- understating a
# long-fight cost is the safe direction to be wrong (the Kurage-bank
# precedent above). Not character machinery: Enrage and Intangible are
# board-state facts every pilot should read, like Frozen/Shatter.
ENRAGE_TAX_TURNS = 2.0      # future attack turns a +Strength grant is priced
                            # over, discounted by PILOT_FUTURE_DAMAGE_DISCOUNT


# ---------------------------------------------------------------------------
#  EB-143 (P11): the Spark HOLD-versus-SPEND term
# ---------------------------------------------------------------------------
#
# `spend_spark` appeared NOWHERE in this package until this window. The bank
# was a one-way meter to the pilot -- `_tempo_value` paid
# `C.PILOT_SPARK_VALUE` per Spark GAINED and nothing charged for a Spark
# SPENT -- so the three `C19` sinks (`powder_charge`, `hold_the_line`,
# `smoke_and_sparks`) bought their payoff for free at score time and the
# standing read had to publish their contribution as a FLOOR
# (`review/records/sitting-reads-2026-08-25-c19-d17-p10.md`).
#
# THE LEDGER WAS THE DEFECT, not the eagerness. A gain worth +0.7 and a spend
# worth 0.0 is an arbitrage the scorer could see: `sparkly_treasure` (gain 1,
# cost 0) followed by any sink scored strictly positive with the board
# unchanged. So the spend is charged, and it is charged in the same currency
# the gain is paid in.
#
# WHAT THE TERM IS: the value of the Sparks a play would CONSUME, if they were
# BANKED instead. Three legs, and the largest wins -- the bank has ONE best
# use, so they are alternatives and not an addition:
#
#   1. THE STOCK FLOOR, `spent * C.PILOT_SPARK_VALUE`. The gain dial, mirrored.
#      Its own comment reads "sparks -> free attacks", which is exactly what
#      the bank is: at `C.SPARKS_FOR_FREE_ATTACK` = 3 a Spark is a third of a
#      free Attack, and 3 x 0.7 = 2.1 is what the pilot already says that
#      Attack is worth. Nothing new is asserted by charging it on the way out.
#   2. THE THRESHOLD LEG. A spend that carries the bank from at-or-above
#      `combat.spark_threshold` to below it forfeits a free Attack OUTRIGHT
#      rather than a linear share of one, and only while an Attack that would
#      have used it is in hand. Priced at `threshold * C.PILOT_SPARK_VALUE`,
#      i.e. at the same dial -- the convexity the floor cannot express.
#   3. THE READER LEG, and this is the one that makes the term a DECISION
#      rather than a tax: the largest amount by which the drop reduces what
#      some OTHER card in hand is worth, measured by re-reading that card at
#      the two bank levels with the pilot's own valuations. It is DERIVED and
#      names no card and no predicate -- `gleeful_barrage`'s `2_plus_sparks`
#      hits and the `has_spark` riders (`eager_to_help`, `patched_dress`) are
#      found because the scorer already reads them, so a Spark reader added to
#      any sheet tomorrow is priced here on the day it ships.
#
# HAND ONLY, DELIBERATELY. A reader still in the draw pile is not counted:
# reading the pile would give the pilot information the player does not have
# at decision time, and the residual error UNDER-values banking, which spends
# more readily -- the direction closer to the pre-`P11` behaviour and the safe
# one under R194's direction rule.
#
# PLACEHOLDER -- sheet-pass sweep, [USER] pick: LEG 1's existence, not its
# value. Charging the stock floor says a Spark is worth something even with no
# reader in hand and the threshold untouched; charging 0.0 there would say the
# bank is worth only what is currently readable off it. The floor is taken
# because of the arbitrage above and because it is the conservative direction
# (it UNDER-values the sink, per R194), but "does a Spark have hold value
# outside a reachable payoff" is a design question and this is one defensible
# answer, not the ruled one. Legs 2 and 3 stand on their own either way.
#
# NOT AN ARCHETYPE WEIGHT, and that is also a choice: a Spark is a Spark, the
# free-Attack threshold is `combat`'s and not any pilot's, and the three sinks
# are drafted by `demolition` and `generic` decks as well as `spark` ones. The
# term is therefore pilot-independent and no row of
# `tier0/content/pilots/archetypes.yaml` moves -- which is also what keeps the
# archive scope to the three cards that print the op.
#
# STAMPING OWED AT INTEGRATION: this weight ENTERS the set
# `C.PILOT_WEIGHTS_VERSION` labels (the EB-5 rule), and it lands inside the ONE
# `P11` window with `EB-144` and `EB-129` (R207) -- where `POLICY_VERSION`
# 10 -> 11 and `PILOT_WEIGHTS_VERSION` 5 -> 6 move together and this name joins
# the pinned set in `tier0/tests/test_pin_tier0_pilot.py`. Neither integer is
# moved here: a window with three items in it gets one bump, not three.
SPARK_HOLD_VALUE_WEIGHT = 1.0   # the scale is DAMAGE POINTS, the same scale
                                # `EXHAUST_FORMULA_PAYOUT_WEIGHT` and
                                # `MODE_OVERDRAW_HP_VALUE` already use. At 1.0
                                # a point of banked-Spark value and a point of
                                # payoff trade one for one, which is the only
                                # setting at which the subtraction in `_score`
                                # means anything. At 0.0 the term vanishes and
                                # the pilot is byte-identical to `P10` -- the
                                # degenerate case, pinned as a test rather
                                # than argued. THE ONE PLACE TO OVERRIDE IT.


def _spark_bank_probe(state: CombatState, card: Card, bank: int) -> float:
    """What `card` is worth to the pilot with the Spark bank at `bank`.

    A pure read taken at a counterfactual bank: the field is set, the pilot's
    own valuations are asked, and the field is restored unconditionally. The
    three terms are the ones that can read the bank at all -- damage
    (`2_plus_sparks` hit counts, `has_spark` branches), block (`has_spark`
    riders) and tempo (`has_spark` draws) -- and every one of them is a pure
    function of state, so a card that reads no Spark returns the SAME float at
    both banks and contributes exactly 0.0 to the leg. No epsilon, no
    tolerance: identical arithmetic on identical inputs.
    """
    p = state.player
    saved = p.sparks
    p.sparks = bank
    try:
        return (_expected_damage(state, card)
                + _block_value(state, card)
                + _tempo_value(state, card))
    finally:
        p.sparks = saved


def _spark_reader_loss(state: CombatState, card: Card,
                       before: int, after: int) -> float:
    """Leg 3: the biggest single payoff in hand the drop would shrink."""
    worst = 0.0
    for other in state.player.hand:
        if other is card:
            continue        # this card's own payoff is scored on its own terms
        loss = (_spark_bank_probe(state, other, before)
                - _spark_bank_probe(state, other, after))
        if loss > worst:
            worst = loss
    return worst


def _spark_unit_value(state: CombatState, card: Card) -> float:
    """LEG 1 UNDER `C.SPARK_ALT_COST_ENABLED`: what one banked Spark is worth.

    THE OLD LEG 1 IS RETIRED WITH THE RULE IT QUOTED. Its own comment said a
    Spark is "a third of a free Attack" at `SPARKS_FOR_FREE_ATTACK` = 3, which
    is a sentence about a rule that does not run under this flag. Nothing
    zeroes and nothing consumes, so a Spark's whole worth is what it BUYS.

    THE REPLACEMENT, and it is deliberately the floor rather than the best
    case: A SHARE OF THE CHEAPEST AFFORDABLE SINK IN HAND. Walk the hand for
    cards whose Spark price the bank can already meet, take the CHEAPEST such
    price (ties broken by the larger payoff), and price one Spark at that
    card's payoff divided by its price. With no affordable sink in hand a
    Spark is worth EXACTLY ZERO, which is the honest reading of the new
    economy and the sentence the packet's sec.6.3 puts at the centre of it:
    "retire the threshold and holding has no payoff at all -- a Spark is worth
    exactly what you buy with it."

    WHY CHEAPEST AND NOT BEST-RATE. The cheapest affordable sink is the use
    the bank is guaranteed to be able to make; the best rate may need Sparks
    the bank does not hold. Under-valuing spends more readily, which is the
    same safe direction R194 picks everywhere else in this file, and it is the
    direction that cannot invent a hold the player has no way to cash.

    HAND ONLY, inherited unchanged from leg 3: a sink in the draw pile is
    information the player does not have at decision time.

    The card being scored is excluded -- its own payoff is scored on its own
    terms, which is leg 3's rule and the same reason.

    WHAT THE PILOT STILL CANNOT SEE, stated rather than discovered later.
    Every one of these makes it spend more readily than a player would, which
    is the one-way direction, but they are real blind spots and the smoke's
    "idle bank" number is measured against them:
      (1) SINKS IN THE DRAW PILE. Hand-only is inherited and deliberate, so a
          bank held for the Firework Finale two cards down reads as a bank
          held for nothing.
      (2) SPARKS ALREADY IN FLIGHT. Bombs on the board will pay the relic on
          detonation; the pilot prices the bank it HAS, never the bank it is
          about to have, so it cannot plan a two-turn purchase.
      (3) THE FLOOR OF ITS OWN POWER -- REPAIRED, and this note is kept
          because it says what the repair had to be. Under the strict Rare
          Power, spending to 2 Sparks makes EVERY unpriced Attack in hand
          unplayable, and leg 3 could not catch it: `_spark_bank_probe` asks
          what a card is WORTH at a bank, not whether it is PLAYABLE at one,
          and an Attack's expected damage is the same float either way. That
          is now LEG 4, `_spark_playability_loss`, which walks the hand for
          cards affordable BEFORE this spend and not after and charges the
          largest of their payoffs. It is gated on this same flag and moves no
          flag-off number, so it is not a `POLICY_VERSION` event.
      (4) MULTI-TURN VALUE. One Spark banked across two turns and one Spark
          spent now score identically; nothing in the term is a discount rate.
    """
    payoff_per_spark = 0.0
    best_price: int | None = None
    for other in state.player.hand:
        if other is card:
            continue
        price = spark_price(state, other)
        if not price or price > state.player.sparks:
            continue
        payoff = _spark_bank_probe(state, other, state.player.sparks) / price
        if best_price is None or price < best_price:
            best_price, payoff_per_spark = price, payoff
        elif price == best_price and payoff > payoff_per_spark:
            payoff_per_spark = payoff
    return max(0.0, payoff_per_spark)


def _spark_free_attack_loss(state: CombatState,
                            before: int, after: int) -> float:
    """Leg 2: a free Attack forfeited outright by crossing the threshold.

    RETIRED-UNDER-FLAG. There is no threshold under
    `C.SPARK_ALT_COST_ENABLED`, so there is no bar to cross and no free Attack
    to forfeit; the leg returns 0.0 and the whole term collapses to legs 1
    and 3, which is the collapse the packet's sec.6.3 predicted.
    """
    if C.SPARK_ALT_COST_ENABLED:
        return 0.0
    threshold = spark_threshold(state)
    if before < threshold or after >= threshold:
        return 0.0          # nothing to forfeit, or the bar still cleared
    if not any(c.type == "attack" and c.cost != 0 and c.cost != "X"
               for c in state.player.hand):
        return 0.0          # `combat.play_card` only spends the bank for an
                            # Attack with a printed cost; nothing here to cash
    return threshold * C.PILOT_SPARK_VALUE


def _spark_playability_loss(state: CombatState, card: Card,
                            before: int, after: int) -> float:
    """LEG 4, and it exists ONLY under `C.SPARK_ALT_COST_ENABLED` (R220 pick
    6(d), the first half: make the pilot able to PLAY a priced economy).

    THE HOLE IT FILLS, named verbatim by `_spark_unit_value`'s blind spot (3)
    and by the `KLEESPARK-R1` packet sec.11.5: `_spark_bank_probe` asks what a
    card is WORTH at a bank, never whether it is PLAYABLE at one, and an
    Attack's expected damage is the same float at bank 0 and bank 9. So leg 3
    -- which is a difference of two probes -- returns EXACTLY 0.0 for the one
    consequence a human prices first: paying for the small sink now means the
    big sink in the same hand cannot be played at all this turn.

    THE TERM. Walk the rest of the hand for cards that carry a Spark price the
    bank can meet at `before` and cannot meet at `after`. Each one is a card
    that was playable and is not; the loss is its WHOLE payoff at the bank it
    would have been played at, not a difference. The LARGEST such payoff is
    taken, matching legs 1-3's "the biggest single thing forfeited" shape --
    the pilot gets one more turn, so it could only have cashed one of them.

    WHY THE WHOLE PAYOFF AND NOT A DISCOUNTED ONE. A card locked out this turn
    is not destroyed; it is deferred, and the deferral is usually one turn.
    Charging the whole payoff therefore OVER-values holding, which is the
    opposite of R194's usual direction -- and it is deliberate here, because
    the standing error runs the other way (the packet measures the ON arm
    spending a higher share of its income than the OFF arm) and because the
    losing side of the trade is the visible one: the pilot that cannot see
    this spends 1 Spark on a 5-damage Attack and forfeits a 20-damage
    finisher. The term still cannot invent a hold: with no OTHER priced card
    in hand it is exactly 0.0, and it is capped by that card's own payoff, so
    a bank held for nothing is still worth nothing.

    HAND ONLY, and the scored card excluded -- legs 1 and 3's rules, for the
    same two reasons (draw-pile knowledge the player does not have; a card's
    own payoff is scored on its own terms).
    """
    if not C.SPARK_ALT_COST_ENABLED:
        return 0.0
    if not C.SPARK_ALT_COST_ENABLED:
        return 0.0
    return max(0.0, (_spark_best_alternative(state, card, before)
                     - _spark_best_alternative(state, card, after)))


def _spark_best_alternative(state: CombatState, card: Card,
                            bank: int) -> float:
    """The best OTHER thing in hand this bank can buy right now, or 0.0.

    ONE card, not a basket. The pilot plays one card per decision and the
    Sparks it does not spend stay in the bank, so the alternative to this
    play is the single best affordable sink in the same hand -- never a sum,
    and never a per-Spark rate multiplied back up by a price the hand has no
    second sink to absorb. That multiplication is what leg 1 does, and it is
    why leg 1 is CAPPED by this function under the flag: with one 3-priced
    sink in hand, `3 x (its payoff / 3)` and `its payoff` agree, but with a
    1-priced sink setting the rate, `3 x rate` claims three copies of a card
    the hand holds once.

    Payoff is read at `bank`, the counterfactual the caller is asking about,
    through the same `_spark_bank_probe` legs 1 and 3 use.
    """
    best = 0.0
    for other in state.player.hand:
        if other is card:
            continue
        price = spark_price(state, other)
        if not price or price > bank:
            continue
        payoff = _spark_bank_probe(state, other, bank)
        if payoff > best:
            best = payoff
    return best


def _spark_hold_cost(state: CombatState, card: Card) -> float:
    """What the Sparks this play consumes are worth BANKED. See the block
    comment above for the three legs and why the largest wins.

    The price is `combat.spark_price` -- the engine's own cost line, asked the
    same way from both sides, so the pilot can never charge itself for a
    quantity the playability gate would not have demanded. That gate has
    already run (`pilot()` filters on `card_playable`), so the bank covers the
    price and the drop is the whole price.

    `spark_price` rather than `spark_cost`, so that under the strict Rare
    Power the pilot is charged for the three Sparks the Power takes off an
    Attack that prints no price. With the flag off the two functions return
    the same number for every card, so this line is byte-identical there.
    """
    price = spark_price(state, card)
    if not price:
        return 0.0
    before = state.player.sparks
    after = max(0, before - price)
    # LEG 1. Under the flag the stock floor is not a fixed dial any more --
    # see `_spark_unit_value` for why, and for what it costs in blindness.
    stock = ((before - after) * _spark_unit_value(state, card)
             if C.SPARK_ALT_COST_ENABLED
             else (before - after) * C.PILOT_SPARK_VALUE)
    if C.SPARK_ALT_COST_ENABLED:
        # THE CAP (R220 pick 6(d)). Leg 1 is a per-Spark RATE multiplied by
        # the whole price, and the hand may hold nothing to spend the rest
        # on: a 1-priced sink setting the rate makes a 3-Spark play look
        # like three of it. Bounded by the single best thing the bank could
        # otherwise buy, the term stops charging for purchases the hand
        # cannot make -- which is what made the pilot score its whole hand
        # negative and pass the turn holding a bank it had no bigger use
        # for. Flag-gated; the else-branch above is untouched.
        stock = min(stock, _spark_best_alternative(state, card, before))
    return max(stock,
               _spark_free_attack_loss(state, before, after),
               _spark_reader_loss(state, card, before, after),
               # LEG 4, flag-gated and 0.0 with the flag off: the sink in hand
               # this spend makes UNPLAYABLE. See `_spark_playability_loss`.
               _spark_playability_loss(state, card, before, after))


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
    for fx in _active_effects(state, card.effects, card):
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
    # EB-143: the Spark ledger's other half. Subtracted here rather than folded
    # into `_tempo_value` beside the GAIN, on purpose: `_tempo_value` is also
    # read by `exhaust_future_value` and `mode_score` at weight 1, and a sink's
    # price is a fact about PLAYING it, not about keeping it or about which
    # body a mode resolves. Gated on the printed price, which is 0 for every
    # card in the repo but three -- so nothing else pays for the lookup and
    # nothing else moves.
    #
    # THE FLAG'S HALF (R220 pick 6(d), the playability repair). With
    # `C.SPARK_ALT_COST_ENABLED` on a price can also come from the strict Rare
    # Power, which is NOT printed on the card -- so gating the lookup on
    # `spark_cost` alone let a converted Attack drain three Sparks and be
    # charged nothing for them, which is exactly the blind spot (3)
    # `_spark_unit_value` names. The disjunct is DEAD with the flag off
    # (`spark_power_price` returns 0 there, so `spark_price == spark_cost` for
    # every card in the repo), which is what keeps every shipped number
    # byte-identical and `POLICY_VERSION` still.
    if spark_cost(card) or (C.SPARK_ALT_COST_ENABLED
                            and spark_price(state, card)):
        total -= SPARK_HOLD_VALUE_WEIGHT * _spark_hold_cost(state, card)
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
    """The pre-W3 payout hook, kept as the named zero.

    It is what the chooser did before a shipped card read the victim's
    identity: Stoke and True Grit+ pay the same for any card, so the honest
    answer was a constant, and a constant cannot change the ranking. W3
    (EB-118 Phase 3, R211) made `formula_aware_payout` the default because
    `pearl_barrage` and `the_tide_remembers` now print a payout slope over the
    selection. This function is still the exact behaviour of that default for
    every card that prints no such slope, and it is what the callers that pass
    `payout=` explicitly can still ask for by name."""
    return 0.0


# W3 (EB-118 Phase 3, R211). The scale is DAMAGE POINTS -- the same scale
# BOMB_LANDED_DAMAGE_VALUE and MODE_OVERDRAW_HP_VALUE already use, and the same
# scale `exhaust_future_value` is denominated in (_block_value prices Block by
# the damage it prevents). At 1.0 a point of payout and a point of forgone
# future value trade one for one, which is the only setting that makes the
# subtraction in `exhaust_victim` mean anything.
#
# THE RARE-ROTATION TRADE IS THE COST AND IT WAS RULED, NOT DISCOVERED:
# measured on `kokomi/priest_weighted`, at `the_tide_remembers`'s own plays the
# formula-aware chooser takes a Rare on 21.7% of selections against the blind
# chooser's 13.1%, buying about +1.21 damage per play. Lowering the weight
# softens the hazard without removing it (0.5 -> 19.0% Rares, +0.92 damage;
# 0.34 -> 17.4%, +0.72), which says the hazard is inherent in paying by cost
# rather than sitting in this constant. R211 ACCEPTS IT AND PAIRS IT WITH
# RETRIEVAL -- `shell_of_sanctuary`'s W3 body ("Salvage the Line") loans a
# rotated Rare back out of the Exhaust pile. Any later change to this value is
# its own `C.PILOT_WEIGHTS_VERSION` bump.
EXHAUST_FORMULA_PAYOUT_WEIGHT = 1.0


def _printed_effects(effect_list: list[dict]):
    """Every printed effect, branches and modal bodies included.

    Deliberately NOT `_active_effects`: that one asks which branch will fire
    right now, and this one asks what the card PRINTS. A payout the player may
    reach at all is a payout this hook must be able to read, and the ranking it
    feeds is a comparison between candidates for the same card -- so a branch
    the board happens not to satisfy scales every candidate identically and
    cannot mis-rank them.
    """
    for fx in effect_list:
        yield fx
        if fx.get("op") == "conditional":
            yield from _printed_effects(fx.get("then") or [])
            yield from _printed_effects(fx.get("else") or [])
        elif fx.get("op") == "choose_one":
            for mode in fx.get("modes") or ():
                yield from _printed_effects(mode.get("effects") or [])


def _selection_payout_terms(card: Optional[Card]):
    """Every printed damage effect on `card` whose formula reads a selection.

    Yields `(count_key, per, is_wide)` for each one.
    """
    if card is None:
        return
    for fx in _printed_effects(card.effects):
        if fx.get("op") != "damage":
            continue
        formula = fx.get("amount_formula")
        if not isinstance(formula, dict):
            continue
        count = formula.get("count", "")
        if not isinstance(count, str):
            continue
        if not count.startswith(effects.EXHAUST_SELECTION_PREFIX):
            continue
        yield (count[len(effects.EXHAUST_SELECTION_PREFIX):],
               formula.get("per", 1),
               fx.get("target") == "all_enemies")


def formula_aware_payout(state: CombatState, card: Optional[Card],
                         candidate: Card) -> float:
    """What the EXHAUSTING card pays, in damage points, for taking THIS victim.

    DERIVED FROM WHAT THE CARD PRINTS -- never a preference for expensive
    cards. It walks the exhausting card's printed effects for damage whose
    formula reads an exhaust-selection count, and returns the MARGINAL
    contribution this candidate would make to that count:

        count == exhaust_selection_cost      -> per * candidate.cost
        count == exhaust_selection_attacks   -> per * (type == "attack")
        count == exhaust_selection_skills    -> per * (type == "skill")
        count == exhaust_selection_powers    -> per * (type == "power")
        count == exhaust_selection_companions-> per * is_companion
        count == exhaust_selection_personal  -> per * (not is_companion)
        count == exhaust_selection_upgraded  -> per * is_upgraded
        count == exhaust_selection_size      -> per * 1   (CONSTANT: every
                                                candidate contributes exactly
                                                one, so it cannot rank)

    R211: IF THE DAMAGE EFFECT CARRYING THE FORMULA TARGETS `all_enemies`, THE
    PAYOUT IS MULTIPLIED BY `len(state.living_enemies)`. A wide card really
    does buy `per` points on every body, and a hook that ignored that would
    under-read its own printed text on exactly the boards the card is for.
    Measured on the two ratified carriers, which is why the clause is not a
    general re-weighting but the difference between them: `pearl_barrage` aims
    (`per: 3`, multiplier 1) and `the_tide_remembers` is wide (`per: 2`,
    multiplier = living enemies). On a one-enemy board -- 62% of the wide
    card's plays -- the clause buys +0.34 damage per play; on a five-body board
    the effective slope is 10 and it buys +5.41.

    A CARD PRINTING NO SUCH FORMULA RETURNS 0.0, so this default degenerates
    EXACTLY to `identity_blind_payout` and every other card keeps its pick.
    That is not an argument, it is a regression test (test_eb118_policies).
    """
    terms = list(_selection_payout_terms(card))
    if not terms:
        return 0.0
    # ONE definition of what a victim contributes, shared with the engine: the
    # marginal is this candidate's own row in `exhaust_selection_counts`, which
    # is the same function the runtime count, the predicates and the emitted
    # C#-parity row all read. A formula can therefore never be paid for a
    # quantity the engine would count differently -- including the X-cost rule
    # (a non-int cost contributes nothing rather than being coerced).
    marginals = effects.exhaust_selection_counts(
        [effects.exhaust_descriptor(candidate)])
    total = 0.0
    for count_key, per, is_wide in terms:
        marginal = marginals.get(count_key)
        if not marginal:
            # Either a count with no marginal rule, or one this candidate does
            # not move. `size` is the interesting case and it is deliberately
            # NOT special-cased away: every candidate contributes exactly 1, so
            # the term is a constant across the pool and cannot rank -- which
            # is the honest answer, and it still adds the constant so a caller
            # comparing absolute payouts sees the card's real slope.
            continue
        bodies = len(state.living_enemies) if is_wide else 1
        total += per * marginal * bodies
    return total * EXHAUST_FORMULA_PAYOUT_WEIGHT


def exhaust_future_value(state: CombatState, card: Card) -> float:
    """What keeping this card is worth, per energy.

    The four terms enter at weight 1 apiece: the chooser runs at RESOLUTION
    time, where the pilot's archetype weight set is not reachable (the weights
    are closed over by `make_pilot`), so it cannot ask which pilot is flying.
    Under-weighting a character term is the safe direction -- it makes the
    chooser conservative about exhausting machinery, not eager.

    EB-145 SUSPENDS ITS OWN FORECAST HERE, and that keeps this function's
    arithmetic BYTE-IDENTICAL to `P10`'s. A candidate that itself prints a
    selection-reading payout (`pearl_barrage`, `the_tide_remembers`) is valued
    at its BASE, not at the payout it would reach if it were played later off
    a pool that does not exist yet. Two reasons, and the second is the ground:
    a candidate's own payout is conditional on a future play, which is exactly
    the speculation this function's docstring already refuses; and pricing it
    here would move the CHOOSER, which `P10` ratified and this window is not
    reopening. It also terminates the recursion -- the forecast asks the
    chooser, the chooser asks this, and one of the two has to stop.
    """
    with _forecast_suspended():
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
    what losing it costs, so on a card that prints no payout slope the pick is
    the least valuable card -- NOT the most expensive one, which is what the
    placeholder read and is the inversion `test_eb118_policies` pins.

    W3 (R211): the default is `formula_aware_payout`, which returns 0.0 for
    every card that prints no selection formula and is therefore byte-identical
    to the old `identity_blind_payout` default on every such card. What it adds
    is that `pearl_barrage` and `the_tide_remembers` now pull the pick toward
    the victim their OWN printed slope pays most for.
    """
    payout = payout or formula_aware_payout
    best = None
    best_key = None
    for i, cand in enumerate(pool):
        key = (payout(state, card, cand) - exhaust_future_value(state, cand),
               _legacy_worst_key(cand), -i)
        if best_key is None or key > best_key:
            best, best_key = cand, key
    return best


# ---------------------------------------------------------------------------
#  EB-145 (P11): payout-aware SCORING of a chosen exhaust
# ---------------------------------------------------------------------------
#
# `P10` made the PICK formula-aware and left the SCORE at the base. Those are
# two seams and the standing read says so: `Tide of Names` deals
# `5 + 2 per exhaust_selection_cost` to ALL enemies, the selection has not
# happened at score time, and `effects._calc_amount` reads
# `state.exhaust_selection` -- which is EMPTY (or, worse, still holds the
# PREVIOUS card's victims) while the pilot is deciding. So the pilot priced a
# 2-cost wide attack at 5 per body no matter what it was about to eat.
#
# THE REPAIR IS TO ASK, NOT TO ESTIMATE. The scorer runs the same chooser the
# engine will run, over the same pool `effects.exhaust_pool` will build, and
# reads the resulting descriptors through the engine's OWN `_calc_amount`.
# Nothing here re-implements the formula grammar, the count vocabulary or the
# selection rules; the forecast is a temporary `state.exhaust_selection` and
# the arithmetic on top of it is the engine's.
#
# NO NEW WEIGHT IS INTRODUCED AND NONE IS OWED. The payout is the card's own
# printed `base`/`per`, the victim is the chooser's, and R211's multiplicity
# clause is already in `_expected_damage`: an `all_enemies` damage effect is
# summed over `state.living_enemies`, so a wide selection payout is multiplied
# by the living bodies without a second multiply here. (`EB-129`'s ruling has
# the same shape for the same reason -- the quantity was already denominated.)
#
# BOTH SHIPPED CARRIERS WERE BLIND AND BOTH ARE FIXED BY THIS ONE SEAM.
# `the_tide_remembers` (per 2, `all_enemies`) and `pearl_barrage` (per 3,
# aimed) print the only two selection formulas on any sheet; the fix is in
# `_formula_amount`, which every printed `amount_formula` already flows
# through, so neither card is named anywhere in the code.

#: Re-entrancy latch. TRUE while a forecast (or a chooser valuation) is in
#: flight, and it is the whole termination argument: the forecast asks
#: `exhaust_victim`, which asks `exhaust_future_value`, which scores a
#: candidate -- and a candidate that prints its own selection payout would
#: forecast again. Module-level rather than on the state because it is a
#: property of the CALL STACK, not of the combat; it is only ever written
#: through `_forecast_suspended`, which restores the previous value, so no
#: exception can leave it armed and determinism is untouched (no rng, no
#: ordering dependence, single-threaded by `jobs=1`).
_FORECASTING = False


@contextlib.contextmanager
def _forecast_suspended():
    global _FORECASTING
    was = _FORECASTING
    _FORECASTING = True
    try:
        yield
    finally:
        _FORECASTING = was


def _reads_a_selection(fx: dict) -> bool:
    """Does this effect's printed formula count an exhaust selection?

    Read off the SAME prefix the engine registers the family under
    (`effects.EXHAUST_SELECTION_PREFIX`), never a list of token names, so a
    ninth derived count added to `exhaust_selection_counts` is visible here on
    the day it is added.
    """
    formula = fx.get("amount_formula")
    return (isinstance(formula, dict)
            and isinstance(formula.get("count"), str)
            and formula["count"].startswith(effects.EXHAUST_SELECTION_PREFIX))


def _forecast_exhaust_selection(state: CombatState,
                                card: Card) -> Optional[list[dict]]:
    """The descriptors this card's own chosen `exhaust_from` WOULD produce.

    `None` means "no forecast is available" -- the card prints no chosen
    exhaust, or a forecast is already in flight -- and every caller falls back
    to the live `state.exhaust_selection`, which is the pre-`P11` reading.

    THE FIRST chosen `exhaust_from` in resolution order is the one forecast,
    because that is the selection a formula placed after it reads. A card
    printing two of them rebinds the context on the second (the engine's ruled
    behaviour: two rotations on one card are two questions, not one pile) and
    is not a shape any sheet prints; if one ever does, the payout it reads is
    the SECOND selection and this returns the first, which under-reads rather
    than over-reads.

    IT RESPECTS THE `EB-118` SWITCH, and that is not decoration. With
    `PILOT_POLICIES_ENABLED` off the engine takes `effects._worst_card`'s pick,
    so a forecast that asked `exhaust_victim` anyway would price a victim the
    engine is not going to take -- and the W4 harness's whole gate claim ("a
    weight reaches the engine ONLY through the gate") would become false at the
    scorer. Same gate, same call shape, same fallback as
    `effects._op_exhaust_from`.
    """
    if _FORECASTING:
        return None
    # EB-144 landed in the same window: the host card is passed so the walk
    # that finds the `exhaust_from` reads the same branches the scoring walks
    # read -- a chosen exhaust behind a conditional the pilot can now evaluate
    # must be forecast on the branch that will actually resolve.
    for fx in _active_effects(state, card.effects, card):
        if fx.get("op") != "exhaust_from" or fx.get("select") != "chosen":
            continue
        pol = effects._pilot_policies()
        pool = effects.exhaust_pool(state, fx, exclude=card)
        n = fx.get("amount", 1)
        n = len(pool) if n == "all" else int(_est(state, n, 1))
        picked: list[dict] = []
        with _forecast_suspended():
            for _ in range(max(0, n)):
                if not pool:
                    break
                victim = (exhaust_victim(state, pool, card) if pol is not None
                          else effects._worst_card(pool))
                pool = [c for c in pool if c is not victim]
                picked.append(effects.exhaust_descriptor(victim))
        return picked
    return None


def _formula_amount(state: CombatState, fx: dict, card: Card,
                    cache: dict) -> int:
    """`effects._calc_amount` for one printed formula, read against the
    selection this card's own chosen exhaust WOULD make.

    EVERY CARD PRINTING NO SELECTION FORMULA TAKES THE FIRST BRANCH and is
    therefore byte-identical to the pre-`P11` call it replaces -- that is not
    an argument, it is `test_eb145_payout_aware_scoring`'s regression sweep.

    `cache` is the caller's per-card dict: one card can print several formulas
    over one selection (none does today) and the chooser must be run once, not
    once per effect.
    """
    formula = fx["amount_formula"]
    if not _reads_a_selection(fx):
        return effects._calc_amount(state, formula, card)
    if "forecast" not in cache:
        cache["forecast"] = _forecast_exhaust_selection(state, card)
    forecast = cache["forecast"]
    if forecast is None:
        return effects._calc_amount(state, formula, card)
    # The forecast is INSTALLED rather than interpreted: `_calc_amount` ->
    # `_runtime_count` -> `exhaust_selection_counts` is the one definition the
    # runtime count, the predicates and the C#-parity row all read, so a score
    # taken this way cannot pay for a quantity the engine would count
    # differently. Restored unconditionally -- the pilot is a PURE READER of
    # combat state and a scorer that left a forecast behind would hand the
    # next card a selection that never happened.
    saved = state.exhaust_selection
    state.exhaust_selection = forecast
    try:
        return effects._calc_amount(state, formula, card)
    finally:
        state.exhaust_selection = saved


# ---------------------------------------------------------------------------
#  EB-118 2C: mode valuation -- which body a `choose_one` resolves
# ---------------------------------------------------------------------------
#
# The chooser contract, ratified with the Deep Breath modes (R194, [USER]
# 2026-08-23), in the order it was written:
#
#   1. score each mode body with the pilot's EXISTING per-op play valuations
#      over current state, minus an overdraw penalty priced at the pilot's HP
#      value when `spend_encore` would shortfall;
#   2. argmax, with a deterministic tie-break to the LOWEST mode index;
#   3. weights in this file, beside the other policy weights, hand-picked;
#   4. behind the default-off switch until 2C's own POLICY_VERSION bump;
#   5. Exhaust, cost, and every card-level field are MODE-INDEPENDENT -- the
#      choice selects a body, never a frame.
#
# Point 2 is what retires `effects._chosen_mode`'s fixed index without leaving
# a second code path behind it: a board on which every mode scores the same is
# a TIE, the tie-break takes the lowest index, and the lowest index is 0 --
# which is exactly what the placeholder returned. The pre-flip behaviour is
# therefore the DEGENERATE CASE of the new rule rather than a branch that
# survives inside it.

def _mode_probe(mode: dict) -> Card:
    """The mode body as a scoreable card, on a NEUTRAL frame.

    Deliberately not a copy of the host card. Two reasons, and the second is
    load-bearing:

    * Contract point 5. The frame -- cost, type, Exhaust, tags -- belongs to
      the CARD and is identical whichever mode is taken, so a frame-sensitive
      score would be pricing something the choice does not select.
    * `policy._active_effects` forecasts the mode the pilot will take and has
      no host card to offer (it walks an effect list, not a play), while
      `effects._op_choose_one` resolves with the real one. Scoring the body
      ALONE makes those two calls the same arithmetic by construction, which
      is the agreement `test_eb118_modal` pins -- rather than a property that
      happens to hold until a mode body reads a card field.

    The cost term is left out of the score entirely for the same reason: it is
    the card's, it is shared by every mode, and a constant cannot change an
    argmax.
    """
    return Card(id="_mode", name="_mode", cost=0, type="skill",
                effects=list(mode.get("effects", [])))


def _mode_overdraw_hp(state: CombatState, mode: dict) -> float:
    """TRUE HP this mode body's spends would drain, given the bank NOW.

    `resources.spend_encore_or_hp` drains Encore first and charges any
    shortfall to HP, so the penalty is the shortfall and not the spend: paying
    out of a full bank costs the buffer, which `_sustain_value` already prices
    on the other side of the ledger, while paying out of an empty one costs
    life the pilot cannot get back.

    The bank is walked in body ORDER and a gain inside the same body refills
    it, because that is what the engine does when the two ops sit in one mode.
    """
    bank = float(state.player.encore)
    short = 0.0
    for fx in _active_effects(state, mode.get("effects", [])):
        if fx["op"] == "gain_encore":
            bank += _est(state, fx.get("amount", 0))
        elif fx["op"] == "spend_encore":
            n = _est(state, fx.get("amount", 0))
            paid = min(bank, n)
            bank -= paid
            short += n - paid
    return short


def mode_score(state: CombatState, mode: dict) -> float:
    """What taking this mode is worth on the board as it stands.

    The five terms enter at weight 1 apiece, for `exhaust_future_value`'s
    reason and with its docstring's caveat: the chooser runs at RESOLUTION
    time, where the pilot's archetype weight set is closed over by
    `make_pilot` and cannot be asked which pilot is flying. The character
    machinery terms (`_spotlight_value`, `_charge_value`, `_stoke_value`,
    `_reaction_value`) are left out for the same reason `_score` gates them
    behind a per-archetype weight -- unweighted, they would let one
    character's machinery outvote another's on a card neither is flying.
    """
    probe = _mode_probe(mode)
    return (_expected_damage(state, probe)
            + _block_value(state, probe)
            + _scaling_value(state, probe)
            + _tempo_value(state, probe)
            + _sustain_value(state, probe)
            - _mode_overdraw_hp(state, mode) * MODE_OVERDRAW_HP_VALUE)


def choose_mode(state: CombatState, modes: list[dict],
                card: Optional[Card] = None) -> int:
    """Which mode index the pilot takes. Argmax, ties to the lowest index.

    `card` is accepted and unused -- see `_mode_probe`. It stays in the
    signature because the engine's seam passes it and a later
    identity-sensitive modal grammar would arrive through it as a parameter,
    the way `identity_blind_payout` does for exhaust selection.

    Strictly-greater-by-MODE_TIE_EPSILON is the whole tie rule: a later mode
    has to BEAT the incumbent, so an exact tie, a float-noise tie, and an
    empty read all resolve to the earliest mode -- index 0 in the degenerate
    case, which is the index the placeholder returned.
    """
    best_index = 0
    best = None
    for i, mode in enumerate(modes):
        score = mode_score(state, mode)
        if best is None or score > best + MODE_TIE_EPSILON:
            best_index, best = i, score
    return best_index
