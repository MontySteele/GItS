"""Assigned draft policy + draft_regret (spec §4).

Assigned mode: the run is seeded with a target archetype. Scoring terms:
- archetype fit: enabler value DECAYS as the core completes; payoff value
  is GATED on the core being online (else you draft win-more blanks)
- Fanfare exception: native meter movement + one direct-output spender is
  the core; surplus generation diminishes instead of filling four fake slots
- printed power and conservative mitigation proxies (added at drafter v3;
  v2 counted only direct damage/Block and made Bombs/debuffs invisible.
  The LIVE stamp is DRAFTER_VERSION in tier0/constants.py -- this module
  deliberately does not define one, so do not read a version off this file)
- universal: defense quota (the real-draft principle codified), curve
  awareness, deck-size penalty (steeper for reaction — ruling R2.2)
(The old Burst-priority term left with v1.9: the Burst is kit, never
offered, so a scoring term for it in offers was dead code.)
The adaptive policy (the goodstuff detector) lands in M6; the A/B harness
is structural, so this module keeps policies behind one callable shape:
  policy(rng, deck_cards, offers, archetype) -> Card | None (None = skip)

draft_regret is the pilot-suspect countermeasure one level up, mandated
from day one: sampled decisions are re-scored post-run in the FINAL deck
context; a decision regrets if some other offer then outscores the actual
pick by a full point. Instrument, not a target.
"""

from __future__ import annotations

import random
from typing import Optional

from tier0 import constants as C
from tier0 import roster
from tier0.engine.state import Card


# DRAFTER_VERSION 3: values are expressed in the same rough units as one
# point of printed damage or Block. They are deliberately conservative: the
# assigned drafter only needs to distinguish direct mitigation/power from
# blank cardboard, not solve an engine before choosing a reward. A measured
# sweep rejected flat draw/energy/Spark/Burst proxies: raising them monotonically
# reduced Klee's real-run result, because their value is deck/context dependent.
STATIC_DEBUFF_VALUE = 2.0
STATIC_BOMB_DAMAGE_SHARE = 0.5
STATIC_BOMB_GUARD_VALUE = 1.5
STATIC_KLEE_CONDITIONAL_SHARE = 0.5
STATIC_STRENGTH_VALUE = 2.0        # conservative two future Attack hits (v4)
STATIC_PERSISTENT_PROC_SHARE = 1.0  # one turn of a repeatable Power (v4)
# DRAFTER_VERSION 6: all_enemies damage counts toward the average swarm, not
# a single body. The Furina-0% diagnosis (§10.8.2) caught the v5 scorer
# reading Undercurrent at HALF its table value against the 4-body elite --
# AoE blindness was structural. 2.0 is deliberately conservative (multi-body
# fights average 2-4 bodies; single-target fights make AoE overpriced at
# higher values).
STATIC_AOE_MULT = 2.0
# DRAFTER_VERSION 7 (Kokomi v0.2 sheet pass): her three verbs were
# structurally invisible -- conscript and gain_charge print zero damage or
# Block, and Sly riders live outside card.effects entirely -- the same
# defect class as v6's AoE blindness. Conservative structural proxies:
STATIC_SLY_SHARE = 0.5        # a Sly rider needs a card-effect discard
                              # outlet to fire; half its printed face
STATIC_CONSCRIPT_VALUE = 1.5  # one playable recruit ~ one companion's
                              # conservative static worth per transform
STATIC_FANFARE_FLOOR_VALUE = 0.2  # per printed floor point (v9). A floor is
                              # worth less per point than Charge: Charge is
                              # read by a kit state the player controls,
                              # where a floor only pays through whatever
                              # readers the deck happens to hold. PROPOSED.
STATIC_CHARGE_VALUE = 0.5     # per printed Charge point: the kit Garment
                              # is a universal reader (never-expiring bank,
                              # +1 damage per 4 Charge while it holds), so
                              # banked points are never dead -- but one
                              # Garment window is all this prices in

# These predicates are readable before a card is played. Mid-resolution
# conditions such as reaction_triggered_by_this and killed_target remain out:
# valuing their best branch unconditionally would recreate the old power bias.
STATIC_STATE_CONDITIONS = frozenset({
    "has_spark",
    "target_has_nonpyro_aura",
    "target_has_power_vulnerable",
    "card_exhausted_this_turn",
    "hp_lost_this_turn",
})


def _static_condition(name: str) -> bool:
    return (
        name in STATIC_STATE_CONDITIONS
        or name.startswith("target_has_power_")
        or name.startswith("exhaust_pile_at_least_")
    )


def _static_condition_share(name: str) -> float:
    if name in ("has_spark", "target_has_nonpyro_aura"):
        return STATIC_KLEE_CONDITIONAL_SHARE
    return 1.0


def _nested_effects(effect_list: list[dict]):
    """Walk every printed branch for card classification only."""
    for fx in effect_list:
        yield fx
        if fx.get("op") == "conditional":
            yield from _nested_effects(fx.get("then", []))
            yield from _nested_effects(fx.get("else", []))


def _neutral_amount(fx: dict, default: float = 1.0) -> float:
    amount = fx.get("amount")
    if isinstance(amount, (int, float)):
        return amount
    formula = fx.get("amount_formula")
    if isinstance(formula, dict):
        return formula.get("base", 0) + formula.get("per", default)
    if formula == "per_aura":
        return default
    return default

AMP_PAYOFF_POWERS = C.AMP_PAYOFF_POWERS   # shared with the content loader


def _has_tempo(card: Card) -> bool:
    """Draw / energy anywhere in the printed text -- the velocity class the
    late-run discipline (DRAFTER_VERSION 5) still takes past the lean cap."""
    return any(fx.get("op") in ("draw", "energy")
               for fx in _nested_effects(card.effects))


def _has_block(card: Card) -> bool:
    def contains(effect_list: list[dict]) -> bool:
        for fx in effect_list:
            if fx.get("op") == "block":
                return True
            if (fx.get("op") == "conditional"
                    and _static_condition(fx.get("if", ""))
                    and (contains(fx.get("then", []))
                         or contains(fx.get("else", [])))):
                return True
        return False

    return contains(card.effects)


def _block_density(deck: list[Card]) -> float:
    return sum(1 for c in deck if _has_block(c)) / max(1, len(deck))


def _is_applier(card: Card) -> bool:
    return card.role_c == "applier"


def _is_amp_payoff(card: Card) -> bool:
    # A reaction payoff: rewards existing auras or amps reactions.
    return ("reaction" in card.archetypes and card.role == "payoff")


def _generates_guest_star(card: Card) -> bool:
    return any(fx.get("op") == "generate_guest_star"
               for fx in _nested_effects(card.effects))


def _is_spotlight_access(card: Card) -> bool:
    """A Companion itself or a card that guarantees one in combat."""
    return card.is_companion or _generates_guest_star(card)


def _is_spotlight_machinery(card: Card) -> bool:
    """A real Spotlight engine piece, distinct from finding the cast."""
    return ("spotlight" in card.archetypes
            and card.role in ("enabler", "payoff")
            and not _is_spotlight_access(card))


def _spotlight_payoff_machinery(deck: list[Card]) -> int:
    """Machinery cards whose authored role is PAYOFF.

    DRAFTER_VERSION 15 (R120 / 10.3): one helper, read by both
    `core_complete` and `_core_progress`, so the two limbs cannot drift --
    the same single-definition rule `_generic_core_counts` follows.
    """
    return sum(1 for c in deck
               if _is_spotlight_machinery(c) and c.role == "payoff")


def _fanfare_generation(card: Card) -> float:
    """Printed Fanfare access supplied by one card.

    Furina gains Fanfare when Encore moves in either direction and when she
    loses HP.  This is an intentionally coarse draft-time estimate: it is
    used to distinguish "the deck has a way to move the meter" from "this
    card turns the meter into output", not to predict exact combat totals.
    """
    total = max(0, card.encore_cost)
    for fx in _nested_effects(card.effects):
        if fx.get("op") == "gain_encore":
            total += max(0, _neutral_amount(fx, 0))
        elif fx.get("op") == "damage" and fx.get("target") == "self":
            total += max(0, _neutral_amount(fx, 0))
    return total


def _fanfare_generation_total(deck: list[Card]) -> float:
    return sum(_fanfare_generation(card) for card in deck)


def _fanfare_floor_total(deck: list[Card]) -> float:
    return sum(_grants_fanfare_floor(card) for card in deck)


def _self_damage(card: Card) -> float:
    return sum(
        max(0, _neutral_amount(fx, 0))
        for fx in _nested_effects(card.effects)
        if fx.get("op") == "damage" and fx.get("target") == "self"
    )


def _has_direct_output(card: Card) -> bool:
    """Damage/Block that can cash a resource into immediate survival."""
    return any(
        fx.get("op") == "block"
        or (fx.get("op") == "damage" and fx.get("target") != "self")
        for fx in _nested_effects(card.effects)
    )


def _grants_fanfare_floor(card: Card) -> float:
    """Printed permanent baseline this card builds (DRAFTER_VERSION 9).

    Replaces `_is_fanfare_converter`, which keyed off `fanfare_cost` and died
    with the spend grammar. Floors are what the read-only plan actually
    assembles, and a drafter blind to them would under-draft the identity
    outright -- the measured failure this branch exists to prevent is the
    fanfare plan seeing 6.7 floors/run against salon's ~51.

    THE BY-RARITY POWER TERM IS GONE (Fanfare rework 2026-07-28, Track B).
    It used to add 5 (rares 8) to every Power on the sheet, because the
    engine granted that silently and "a drafter that could only see the
    explicit op would systematically undervalue every Power the archetype
    drafts". The engine no longer grants it, so reading it here would be the
    mirror-image error -- pricing 17 Powers for value they no longer carry.

    What remains is exactly what the card PRINTS, which is now the whole
    truth. `raise_fanfare_cap` is deliberately NOT counted: the cap has not
    been a binding number since F-A5 (read-at-cap under 1% in every arm of
    the pilot-gap battery), so scoring it as baseline would tell the drafter
    a Fanfare Cap card builds a floor it does not build.
    """
    return float(sum(fx.get("amount", 0)
                     for fx in _nested_effects(card.effects)
                     if fx.get("op") == "gain_fanfare_floor"))


def _drafted_readers(deck: list[Card]) -> int:
    """Readers the DRAFT put in the deck -- basics excluded.

    The exclusion arrived with the compensation pass (2026-07-28, Track 2.4),
    which put a low-slope Fanfare read on `aria_of_recompense`. That is the
    STARTER: one copy is in every Furina deck before a single card is offered.
    Counted plainly, the reader limb of the fanfare core would be closed at
    run start, forever, for every deck -- and this limb exists precisely to
    ask whether the DRAFT assembled a plan that cashes the meter. A limb that
    is always satisfied answers nothing and, worse, feeds `_core_progress`'s
    +3.0 core-advance bonus with a constant, which would push the drafter off
    real payoffs by telling it a third of the plan is free.

    The generation and floor limbs are TOTALS over printed amounts, so the
    starter's contribution to those is a real quantity that scales -- only the
    reader limb is a COUNT, and only a count can be gamed by a free card.
    """
    return sum(1 for c in deck if c.rarity != "basic" and _reads_fanfare(c))


def _reads_fanfare(card: Card) -> bool:
    """Does the printed output scale with or unlock from held Fanfare?"""
    for fx in _nested_effects(card.effects):
        if str(fx.get("if", "")).startswith("fanfare_"):
            return True
        if str(fx.get("power", "")).startswith("fanfare_"):
            return True
        if "fanfare" in str(fx.get("bonus_formula", "")):
            return True
    return False


def core_complete(deck: list[Card], archetype: str) -> bool:
    """Is the archetype 'online'? (spec §5 as amended by v1.9: reaction
    core := 2 appliers + 1 amp payoff. The Burst left the assembly
    definition when it became kit -- it arrives by charging the meter, not
    by drafting, so requiring it in the DECK measured pool odds, not
    assembly. That 10% 'ever saw the Burst' factor was the binding term in
    reaction's 5.8% achievability. Other archetypes: DRAFT_CORE_SIZE
    on-plan enabler/payoff cards, AT LEAST ONE of which is a payoff --
    DRAFTER_VERSION 14, see the generic limb below.)"""
    if archetype == "reaction":
        appliers = sum(1 for c in deck if _is_applier(c))
        amps = sum(1 for c in deck if _is_amp_payoff(c))
        return appliers >= 2 and amps >= 1
    if archetype == "spotlight":
        # DRAFTER_VERSION 15 (R120 / 10.3, verbatim "Yes"): payoff-presence
        # extends to the spotlight limb -- the v14 note deliberately left
        # this branch alone because enabler-vs-payoff machinery was a
        # definitional question, and [USER] answered it. `limelight` (the
        # only enabler-role machinery card) alone no longer satisfies the
        # machinery limb; the deck must also hold a machinery PAYOFF, the
        # same one-card bar every other limb's payoff half uses.
        access = sum(1 for c in deck if _is_spotlight_access(c))
        machinery = sum(1 for c in deck if _is_spotlight_machinery(c))
        payoffs = _spotlight_payoff_machinery(deck)
        return access >= 2 and machinery >= 1 and payoffs >= 1
    if archetype == "fanfare":
        # Furina's starter already supplies the first half in practice, but
        # keep the definition honest for synthetic/modified decks.
        #
        # THREE limbs since DRAFTER_VERSION 10 (G-E1). Generation and floor
        # are both inputs; without the reader limb this returned True for a
        # deck that moved a meter nothing ever cashed.
        return (
            _fanfare_generation_total(deck) >= FANFARE_GENERATION_COVERAGE
            and _fanfare_floor_total(deck) >= FANFARE_FLOOR_COVERAGE
            and _drafted_readers(deck) >= FANFARE_PAYOFF_COVERAGE
        )
    # DRAFTER_VERSION 14: the generic limb is TWO limbs, for the same reason
    # the fanfare limb became three at v10. Counting enablers and payoffs
    # together answers "did the resource engine assemble", not "did the deck
    # assemble": four on-plan enablers and zero payoffs read ONLINE, which is
    # precisely the failure the fanfare close-out named ("it measures when
    # the RESOURCE assembles, not when the DECK does"). The bar on the payoff
    # limb is ONE, matching every other archetype's low single-card threshold
    # -- `core_complete` asks whether the plan is ONLINE, not whether it is
    # finished. How many payoffs an archetype SHOULD hold is the draft-reach
    # question and does not belong in the instrument.
    on_plan, payoffs = _generic_core_counts(deck, archetype)
    return on_plan >= C.DRAFT_CORE_SIZE and payoffs >= GENERIC_PAYOFF_COVERAGE


def _generic_core_counts(deck: list[Card], archetype: str) -> tuple[int, int]:
    """(on-plan enabler+payoff cards, on-plan payoff cards) for one deck.

    One place, so `core_complete` and `_core_progress` cannot drift apart --
    the v10 fanfare fix had to move both limbs for the same reason.
    """
    on_plan = [c for c in deck
               if archetype in c.archetypes
               and c.role in ("enabler", "payoff")]
    return len(on_plan), sum(1 for c in on_plan if c.role == "payoff")


def _core_progress(deck: list[Card], archetype: str) -> float:
    if archetype == "reaction":
        appliers = min(2, sum(1 for c in deck if _is_applier(c)))
        amps = min(1, sum(1 for c in deck if _is_amp_payoff(c)))
        return (appliers + amps) / 3
    if archetype == "spotlight":
        # DRAFTER_VERSION 15: the payoff limb, weighted equally -- the same
        # shape the v10 fanfare fix and the v14 generic fix used, and the
        # half with teeth: progress feeds score_offer's +3.0 core-advance
        # bonus, so a spotlight deck now reaches for a machinery payoff
        # instead of counting `limelight` as a finished engine.
        access = min(2, sum(1 for c in deck if _is_spotlight_access(c)))
        machinery = min(1, sum(
            1 for c in deck if _is_spotlight_machinery(c)))
        payoff = min(1, _spotlight_payoff_machinery(deck))
        return (access + machinery + payoff) / 4
    if archetype == "fanfare":
        generation = min(
            1.0,
            _fanfare_generation_total(deck) / FANFARE_GENERATION_COVERAGE,
        )
        baseline = min(1.0, _fanfare_floor_total(deck) / FANFARE_FLOOR_COVERAGE)
        # DRAFTER_VERSION 10: the reader limb, weighted equally with the two
        # input limbs. This is the half of the fix with teeth -- progress
        # feeds score_offer's +3.0 core-advance bonus, so a fanfare deck now
        # actually reaches for a payoff instead of only for inputs.
        payoff = min(1.0, _drafted_readers(deck) / FANFARE_PAYOFF_COVERAGE)
        return (generation + baseline + payoff) / 3
    # DRAFTER_VERSION 14: the payoff limb, weighted equally with the
    # assembly limb -- the same shape the v10 fanfare fix used, and the half
    # with teeth. Progress feeds `score_offer`'s +3.0 core-advance bonus, so
    # a generic-limb archetype now reaches for a payoff instead of counting
    # any four on-plan cards as a finished plan.
    on_plan, payoffs = _generic_core_counts(deck, archetype)
    assembly = min(1.0, on_plan / C.DRAFT_CORE_SIZE)
    payoff = min(1.0, payoffs / GENERIC_PAYOFF_COVERAGE)
    return (assembly + payoff) / 2


# Ops whose price is computed by a dedicated branch of `effect_power` above,
# because they need the card, the deck, or the recursion. `_op_price` refuses
# them rather than returning a second, quieter number for the same op.
_PRICED_INLINE = frozenset({
    "damage", "chain_attack", "block", "place_bomb", "apply_power",
    "conditional", "conscript", "gain_charge", "summon_kurage",
    "gain_fanfare_floor", "grow_damage", "repeat_this",
})


def _added_card_value(fx: dict) -> float:
    """One `add_card` / `generate_from_pool` token, signed.

    A `status`-rarity add is a printed COST -- the card puts bloat in your
    own pile -- so it is the same magnitude with the sign flipped. The
    rarity read goes through `loader.peek_card`, guarded: a token id the
    loader cannot resolve prices as a neutral generated card rather than
    taking the drafter down.
    """
    cid = fx.get("card_id") or fx.get("card")
    if cid in (None, "self"):
        # `card: self` clones the playing instance (Anger). That is a copy of
        # something already drafted, not a conjured token.
        return STATIC_CARD_COPY_VALUE if cid == "self" \
            else STATIC_GENERATED_CARD_VALUE
    try:
        from tier0.content import loader
        rarity = loader.peek_card(cid).rarity
    except Exception:
        rarity = ""
    if rarity == "status":
        return -STATIC_STATUS_CARD_COST
    return STATIC_GENERATED_CARD_VALUE


def _op_price(fx: dict) -> float:
    """The DRAFTER_VERSION 13 static price of one effect dict.

    Every rationale is one line in STATIC_OP_PRICING, and
    `tools/lint_op_parity.py` asserts this function and that table between
    them cover the engine's whole OPS registry. All values PROPOSED.
    """
    op = fx.get("op")
    if op in _PRICED_INLINE:
        return 0.0
    aoe = (STATIC_AOE_MULT if fx.get("target") == "all_enemies" else 1.0)

    # -- damage- and Block-shaped -----------------------------------------
    if op == "block_next_turn":
        return _neutral_amount(fx, 0) * STATIC_DELAYED_BLOCK_SHARE
    if op == "buff_next_attack":
        return _neutral_amount(fx, 0) * STATIC_NEXT_ATTACK_SHARE
    if op == "detonate":
        return (STATIC_DETONATE_VALUE + fx.get("bonus", 0)) * aoe
    if op == "move_bombs":
        return (STATIC_BOMB_MOVE_VALUE
                + fx.get("bonus", 0) * STATIC_BOMB_DAMAGE_SHARE)
    if op == "modify_bombs":
        return fx.get("bonus", 0) * STATIC_BOMB_DAMAGE_SHARE   # one bomb
    if op == "chance_bomb_per_detonation":
        return (fx.get("chance", 0) * fx.get("bomb_damage", 0)
                * STATIC_BOMB_DAMAGE_SHARE)                    # one det.
    if op == "strip_block":
        return STATIC_STRIP_BLOCK_VALUE

    # -- reaction machinery ------------------------------------------------
    if op == "apply_aura":
        return STATIC_AURA_VALUE * aoe
    if op == "swirl":
        return STATIC_SWIRL_VALUE * aoe
    if op == "refresh_all_auras":
        return STATIC_AURA_REFRESH_VALUE

    # -- Furina's meter ----------------------------------------------------
    if op == "gain_encore":
        return _neutral_amount(fx, 0) * STATIC_ENCORE_VALUE
    if op == "spend_encore":
        return -_neutral_amount(fx, 0) * STATIC_ENCORE_VALUE
    if op == "raise_fanfare_cap":
        return _neutral_amount(fx, 0) * STATIC_FANFARE_CAP_VALUE
    if op == "crash_fanfare":
        return -_neutral_amount(fx, 0) * STATIC_CRASH_FANFARE_VALUE
    if op == "salon_bow":
        return _neutral_amount(fx) * STATIC_SALON_BOW_VALUE
    if op == "spotlight_designate":
        return STATIC_SPOTLIGHT_DESIGNATE_VALUE

    # -- cards from nowhere ------------------------------------------------
    if op in ("generate_guest_star", "generate_from_pool"):
        return _neutral_amount(fx) * STATIC_GENERATED_CARD_VALUE
    if op == "add_card":
        zone = fx.get("zone") or fx.get("to", "discard")
        share = 1.0 if zone == "hand" else STATIC_OFFPILE_CARD_SHARE
        return _neutral_amount(fx) * _added_card_value(fx) * share
    if op in ("copy_companion_in_hand", "copy_spotlighted_in_hand"):
        per = STATIC_CARD_COPY_VALUE + (
            STATIC_FREE_COPY_BONUS if fx.get("cost_override") == 0 else 0.0)
        return _neutral_amount(fx) * per
    if op == "copy_companions_played_this_combat":
        # Unbounded at runtime; ONE unique companion is the same neutral
        # single-unit estimate the damage formulas use for a live count.
        return STATIC_CARD_COPY_VALUE + (
            STATIC_FREE_COPY_BONUS if fx.get("cost_override") == 0 else 0.0)
    if op == "replay_next_companion":
        return fx.get("times", 1) * STATIC_CARD_COPY_VALUE
    if op == "autoplay_from_exhaust":
        return STATIC_AUTOPLAY_VALUE                      # one neutral card
    if op == "autoplay_from_draw":
        return _neutral_amount(fx) * STATIC_AUTOPLAY_VALUE
    if op == "extra_card_screen":
        return _neutral_amount(fx) * STATIC_EXTRA_SCREEN_VALUE

    # -- deck manipulation --------------------------------------------------
    if op == "discard":
        if fx.get("select", "random") == "chosen":
            return 0.0
        return -_neutral_amount(fx) * STATIC_RANDOM_DISCARD_COST
    if op == "discard_for_sparks":
        return fx.get("sparks", 0) * STATIC_SPARK_VALUE    # chosen fodder
    if op == "exhaust_from":
        per = (STATIC_STATUS_EXHAUST_VALUE
               if fx.get("filter") == "status" else STATIC_EXHAUST_VALUE)
        n = fx.get("amount", 1)
        return (1.0 if n == "all" else _neutral_amount(fx)) * per
    if op == "scry_discard":
        return STATIC_SCRY_VALUE
    if op == "recall_to_draw":
        return _neutral_amount(fx) * STATIC_RECALL_VALUE
    if op == "upgrade_in_hand":
        return STATIC_UPGRADE_VALUE                        # one neutral card
    if op == "grant_sly_this_turn":
        return STATIC_GRANT_SLY_VALUE
    if op == "remember_card":
        return STATIC_REMEMBER_CARD_VALUE
    if op == "transform_in_hand":
        return STATIC_TRANSFORM_VALUE

    # -- HP economy ---------------------------------------------------------
    if op == "heal":
        return _neutral_amount(fx, 0) * STATIC_HEAL_SHARE
    if op == "gain_max_hp":
        return _neutral_amount(fx, 0) * STATIC_MAX_HP_VALUE

    # -- the measured dead dials (v3 sweep; see the v13 header) -------------
    if op in ("draw", "draw_to_hand_size"):
        return _neutral_amount(fx) * STATIC_DRAW_VALUE
    if op == "draw_while":
        return 2 * STATIC_DRAW_VALUE       # the match plus its stopper
    if op == "energy":
        return _neutral_amount(fx, 0) * STATIC_ENERGY_VALUE
    if op == "cost_mod":
        return abs(fx.get("delta", 1)) * STATIC_ENERGY_VALUE
    if op == "gain_spark":
        return _neutral_amount(fx) * STATIC_SPARK_VALUE
    if op == "burst_energy":
        return _neutral_amount(fx, 0) * STATIC_BURST_VALUE

    # Unreachable while lint_op_parity is green; loud rather than silent if
    # it ever is not, because a silent 0.0 here is the exact defect this
    # whole version bump exists to end.
    raise KeyError(f"no DRAFTER v13 static price for op {op!r}")


def _static_power(card: Card, deck: Optional[list[Card]] = None) -> float:
    """Conservative printed power per energy for reward decisions.

    Damage and Block remain face value. Enemy debuffs and Bombs receive small,
    explicit proxies so the generic anchor no longer treats direct mitigation
    and delayed damage as zero. Draw/energy/resource engines remain with the
    archetype scorer and M6 adaptive policy: a flat proxy sweep made both
    reference characters draft worse decks.
    """
    all_effects = list(_nested_effects(card.effects))
    has_enemy_weak = any(
        fx.get("op") == "apply_power"
        and fx.get("power") == "weak"
        and fx.get("target") != "self"
        for fx in all_effects
    )
    has_bomb = any(fx.get("op") == "place_bomb" for fx in all_effects)

    def effect_power(effect_list: list[dict]) -> float:
        total = 0.0
        for fx in effect_list:
            if fx.get("op") == "conditional":
                name = fx.get("if", "")
                if _static_condition(name):
                    # Drafting has no combat state. Klee's Spark/aura branches
                    # receive a neutral availability discount; predicates
                    # backed by a deck/pile condition retain the established
                    # reachable-branch convention. Actual play always reads
                    # the live predicate in tier0.pilot.policy.
                    then_power = effect_power(fx.get("then", []))
                    else_power = effect_power(fx.get("else", []))
                    share = _static_condition_share(name)
                    total += (else_power
                              + share * (then_power - else_power))
            elif (fx.get("op") in ("damage", "chain_attack")
                  and fx.get("target") != "self"):
                amt = fx.get("amount", 0)
                formula = fx.get("amount_formula")
                if isinstance(formula, dict):
                    count = 1
                    if formula.get("count") == "strike_cards" and deck is not None:
                        count = (sum("strike" in c.tags for c in deck)
                                 + int("strike" in card.tags))
                    # Otherwise one unit of the live count is a conservative
                    # neutral offer-state estimate (pile, current Block, ...).
                    amt = (formula.get("base", 0)
                           + formula.get("per", 1) * count)
                rider = fx.get("bonus_per_target_power")
                if isinstance(rider, dict):
                    amt += rider.get("per", 0)  # one matching stack
                if isinstance(amt, (int, float)):
                    times = (fx.get("times", 1)
                             if isinstance(fx.get("times", 1), int) else 1)
                    times_formula = fx.get("times_formula")
                    if isinstance(times_formula, dict):
                        times = (times_formula.get("base", 0)
                                 + times_formula.get("per", 1))
                    # v13: chain_attack is a damage line whose volley
                    # repeats once per body it kills, so it is priced HERE
                    # rather than as its own verb -- a chain that kills
                    # nothing is exactly this damage line.
                    if fx.get("op") == "chain_attack":
                        amt *= STATIC_CHAIN_ATTACK_MULT
                    if fx.get("target") == "all_enemies":
                        total += amt * times * STATIC_AOE_MULT      # v6
                    else:
                        total += amt * times
            elif fx.get("op") == "block":
                times = 2 if fx.get("times") == "exhausted_this_card" else 1
                total += fx.get("amount", 0) * times
            elif fx.get("op") == "place_bomb":
                total += (fx.get("bomb_damage", 0)
                          * _neutral_amount(fx)
                          * STATIC_BOMB_DAMAGE_SHARE)
            elif (fx.get("op") == "apply_power"
                  and fx.get("target", "self") == "self"
                  and fx.get("power") == "strength"):
                total += _neutral_amount(fx) * STATIC_STRENGTH_VALUE
            elif (fx.get("op") == "apply_power"
                  and fx.get("target", "self") == "self"
                  and fx.get("power") == "dexterity"):
                # v12: the mirror of the Strength line. temp_dexterity is
                # a different power string and deliberately falls through.
                total += _neutral_amount(fx) * STATIC_DEXTERITY_VALUE
            elif (fx.get("op") == "apply_power"
                  and fx.get("target", "self") == "self"
                  and fx.get("power") == "witchs_flame"):
                # Durin is reliable on Klee's catalyst cadence, but offer
                # scoring credits only one end-turn aura rather than pricing
                # an entire permanent engine up front.
                total += _neutral_amount(fx) * STATIC_PERSISTENT_PROC_SHARE
            elif (fx.get("op") == "apply_power"
                  and fx.get("target") != "self"
                  and fx.get("power") in ("weak", "vulnerable")):
                total += _neutral_amount(fx) * STATIC_DEBUFF_VALUE
            elif (fx.get("op") == "apply_power"
                  and fx.get("target", "self") == "self"
                  and card.type == "power"):
                # v12: a persistent engine the proxies above cannot name.
                # One flat conservative credit per printed self-power --
                # the drafter cannot see an engine's payout curve at offer
                # time, same reasoning as the Durin/Kurage single-pulse
                # convention.
                total += STATIC_POWER_ENGINE_VALUE
            elif fx.get("op") == "conscript":                       # v7
                total += _neutral_amount(fx) * STATIC_CONSCRIPT_VALUE
            elif fx.get("op") == "gain_charge":                     # v7
                total += _neutral_amount(fx) * STATIC_CHARGE_VALUE
            elif fx.get("op") == "summon_kurage":                   # v8
                # A persistent summon, priced like Durin: credit ONE pulse,
                # not the whole duration. The bank read is invisible at
                # offer time (the drafter cannot know her Charge curve), so
                # only the flat pulse + its Block are counted -- deliberately
                # conservative, same reasoning as the Durin line above.
                total += (C.KURAGE_PULSE_BASE + C.KURAGE_PULSE_BLOCK
                          ) * STATIC_PERSISTENT_PROC_SHARE
            elif fx.get("op") == "gain_fanfare_floor":                # v9
                # A permanent baseline, priced like Strength: it is not
                # output now, it is output on every later read. Conservative
                # on purpose -- the drafter cannot see how many readers the
                # deck will end up holding, and over-pricing a floor would
                # bend every Furina plan toward the same few cards.
                total += _neutral_amount(fx) * STATIC_FANFARE_FLOOR_VALUE
            elif fx.get("op") == "grow_damage":
                total += fx.get("amount", 0) * 0.5  # one discounted redraw
            else:
                # DRAFTER_VERSION 13: everything else in the registry. One
                # branch per op, in the order STATIC_OP_PRICING documents
                # them; the lint above guarantees no op reaches this `else`
                # without an entry, and _op_price returns 0.0 only for the
                # ops whose entry says ZERO.
                total += _op_price(fx)
        return total

    total = effect_power(card.effects)
    # v13: `repeat_this` re-resolves the card's OWN effects, so it is a
    # MULTIPLIER on what the rest of the card printed rather than a term
    # beside it -- which is why it is applied here and not in `effect_power`,
    # where the branch would only ever see its own siblings. At half share:
    # every printed use of the op sits behind a condition.
    repeats = sum(fx.get("times", 1) for fx in all_effects
                  if fx.get("op") == "repeat_this")
    if repeats:
        total *= 1.0 + repeats * STATIC_REPEAT_SHARE
    if card.sly:
        # v7: a Sly rider is the same printed grammar at half face -- it
        # fires only when a card effect discards this from hand, and the
        # drafter cannot see outlet density at offer time.
        total += effect_power(card.sly) * STATIC_SLY_SHARE
    # An armed Bomb suppresses one enemy attack action. Do not also price that
    # protection when the same card applies Weak: the two reductions share one
    # branch at runtime and never multiply.
    if has_bomb and not has_enemy_weak:
        total += STATIC_BOMB_GUARD_VALUE
    cost = card.cost if isinstance(card.cost, int) else 2
    return total / max(1, cost)


# DRAFTER_VERSION 2 reaction weights (ruling R2.2) — swept at 1000
# runs/cell (M8 report). The sweep's verdict: the twice-convicted
# reaction scorer was guilty of exactly one thing, power blindness —
# the R2.1 power term alone took assigned-reaction 10.7% -> 34.4%,
# past adaptive. Raising applier (4.5) or offline-amp (2.5) valuations
# measured WORSE (33.4%); only the lean-deck line helped (+1.9), which
# is §3's density finding expressed as scorer behavior. Module-level so
# sweeps can vary them without editing the scorer.
REACTION_APPLIER_WEIGHT = 3.5     # sweep: 4.5 hurts
REACTION_AMP_OFFLINE = 1.0        # sweep: 2.5 hurts
REACTION_LEAN_CAP = 13            # reaction's own bloat line (§3: lean decks)
REACTION_LEAN_PENALTY = 0.4       # winner at x0.4; x0.8 overshoots (16.6 cards)

# DRAFTER_VERSION 5 late-run discipline (red-pen 2026-07-23, the
# Ironclad-0.6% diagnosis §10.8.1). The 99%-pick-rate degeneracy: the
# soft-cap penalty was tuned in a 10-screen world where 22 cards was
# unreachable, so 30 screens produced 28-35-card decks. The human act-2
# rule ("stop taking cards; fish for powers and velocity") expressed as a
# hard gate: past LEAN_CAP only Powers / tempo (draw-energy) / Block make
# the cut, past LEAN_BLOCK_CAP Powers and tempo only. Measured as the
# lean15 arm: deck 28.9 -> ~17, act-2-boss deaths 32% -> ~20%.
# Applied to assigned_policy ONLY -- the measured arm; adaptive keeps its
# emergent-shape scoring unchanged until separately measured.
DRAFT_LEAN_CAP = 15
DRAFT_LEAN_BLOCK_CAP = 20
# DRAFTER_VERSION 6: the strong-pick escape hatch the measured arm's
# docstring promised but its code never implemented (§10.8.1 lever-world
# flag: the v5 gate filtered real_ironclad's rare attack payoffs and his
# win fell 5.4->3.0). Past the lean cap, a RARE whose score clears this
# bar is always eligible.
DRAFT_LEAN_RARE_BAR = 4.0

# DRAFTER_VERSION 11 -- the R83 discrimination pass (Silent pilot review
# s1a, 2026-07-27). The corrected evidence: drafting is strongly net-
# positive on the generic anchors (skip-all control 7.9% vs assigned 23.3%
# act-1 clear), but the scorer cannot tell the strong commons from the weak
# ones (leg_sweep +31.8 lift vs anticipate -16.9 under the same policy).
# Two levers, BOTH SCOPED TO archetype == "generic" so only the two anchor
# characters move -- every house plan drafts under its own archetype and
# keeps its measured numbers:
#   GENERIC_SKIP_THRESHOLD    the anchors' own skip bar. The global 0.5 was
#                             tuned for plan-committed house drafting, where
#                             an off-plan screen is worth little; the
#                             anchors' +1.0 role / +0.8 pool freebies mean
#                             0.5 skips nothing at all.
#   GENERIC_REDUNDANCY_PENALTY  per functional twin ALREADY DRAFTED: an
#                             offer whose top-level op signature equals a
#                             non-basic deck card's is "the thing you
#                             already have, plus some Block" (the same
#                             phenomenon the distinctness gate's neardup
#                             measures on pools, showing up as draft
#                             behavior). Basics are excluded from the twin
#                             count on purpose: five starter Defends must
#                             not veto the first real block card (Deflect
#                             carries +25.3 lift), and the rest policy is
#                             already removing basics.
# Values are the round-2 sweep winner (docs/silent-pilot-review-2026-07-27.md
# s5): at 1000 paired-seed runs the winner reads real_silent 28.8% act-1
# clear (baseline 23.3%) and real_ironclad 33.3% (baseline 26.9%), with the
# take-when-offered tails finally aligned to the measured lifts (anticipate
# 30.6% -> 5.7% taken, deflect 25.6% -> 46.2%). RATIFIED [USER] 2026-07-27
# (R84); the same ruling ordered the 3-act roster re-measured before any
# anchor reading is quoted again.
GENERIC_SKIP_THRESHOLD = 1.5
# Swept 0.0/0.5/1.0 twice: never helped (its op-signature twin test punishes
# the measured-GOOD plain block cards hardest). Kept at 0 as a documented
# dead dial rather than deleted, so the next pass starts from the
# measurement instead of re-proposing it.
GENERIC_REDUNDANCY_PENALTY = 0.0
# The lever with teeth, added when the first two measured WEAK (the round-1
# skip-3.5 winner cut deflect's take-rate 25.6%->13.8% while anticipate
# held -- a bare bar cuts backwards, because the plan bonuses are what
# misprice the offer). Scales the role-label plan bonuses on generic
# anchors only; 1.0 is the pre-pass behavior, 0.0 measured slightly worse
# than keeping a quarter-weight prior (27.9%/32.2% vs 28.8%/33.3%).
# KNOWN RESIDUAL, on the record: _static_power cannot see self-powers, so
# with the labels quieted Footwork's take rate fell 70% -> 21% against a
# +23.6 measured lift. A power-aware static term is the named next lever,
# not smuggled into this one.
GENERIC_PLAN_BONUS_MULT = 0.25

# DRAFTER_VERSION 12 -- the power-aware static term (R84, the Footwork
# residual paid). Two structural proxies were built and swept (16-cell
# grid, 300 runs/cell, seed 11, bare 1-act, serial; winners confirmed at
# 1000 paired-seed runs -- docs/silent-pilot-review-2026-07-27.md s6):
#   STATIC_DEXTERITY_VALUE   permanent self Dexterity, the exact mirror of
#                            STATIC_STRENGTH_VALUE: two future Block gains.
#                            DELIBERATELY excludes `temp_dexterity` -- a
#                            one-turn grant is not future scaling, and the
#                            card that prints it (Anticipate) carries a
#                            -16.9 measured lift the v11 pass just taught
#                            the scorer to decline. Measured: helps
#                            monotonically (Footwork taken 21% -> 74% at
#                            2.0, against its +23.6 lift); 2.0/3.0/4.0 are
#                            indistinguishable at n=1000, so the value
#                            keeps the Strength mirror rather than chasing
#                            a noise peak. real_silent 28.8% -> 29.1%.
#   STATIC_POWER_ENGINE_VALUE  flat credit per otherwise-unpriced self-power
#                            printed by a POWER-type card (Afterimage,
#                            Noxious Fumes, Demon Form...). FLAT, not
#                            amount-scaled: printed amounts are
#                            heterogeneous across engines (Cruelty 25,
#                            Outbreak 11, Afterimage 1) and say nothing
#                            comparable about value. Skills' self-powers
#                            stay unpriced -- they are one-turn riders
#                            (Blur, Rage, Flame Barrier) and most print
#                            Block or damage beside them anyway.
#                            MEASURED A DEAD DIAL, kept at 0.0: it hurt at
#                            every swept value on every dex level (28.0%
#                            -> 25.7% by 2.25) -- a flat credit cannot
#                            tell Noxious Fumes (+29.7 lift) from the junk
#                            engines it drags in at the same price. A
#                            discriminating engine term needs per-power
#                            evidence, not a constant; that is a future
#                            pass, and it starts from this measurement.
STATIC_DEXTERITY_VALUE = 2.0
STATIC_POWER_ENGINE_VALUE = 0.0

# =========================================================================
# DRAFTER_VERSION 13 -- the op repricing (sim-hygiene sprint, 2026-07-29,
# [USER]-accepted as the sprint's headline). ALL VALUES BELOW ARE PROPOSED.
#
# THE DEFECT. `_static_power` hand-enumerated 10 of the engine's 56
# registered ops. The other 46 were priced at EXACTLY ZERO at offer time --
# not "approximately zero", not "conservatively low", but invisible -- so a
# card whose whole printed text is `detonate`, `salon_bow`, `add_card`,
# `apply_aura`, `block_next_turn` or `copy_companion_in_hand` read to every
# drafting arm as blank cardboard. This is the SAME defect class the repo
# has now found four times (v6 AoE blindness, v7 Kokomi's three verbs, v8
# summon_kurage, v9 floor grants): each time it was found by noticing one
# character drafting badly, and each time the fix was scoped to that
# character's verbs. This pass stops finding it one op at a time. Task 2 of
# the same sprint adds `tools/lint_op_parity.py`, which fails the build when
# a newly registered op has no entry in STATIC_OP_PRICING below -- so the
# NEXT op cannot arrive unpriced and silent.
#
# MAGNITUDES follow the file's established idiom: one unit is one point of
# printed damage or Block; nothing is priced at the value it would have in a
# solved deck, only at what an offer screen can defend without combat state.
#
# THE DELIBERATE ZEROS ARE NOT OVERSIGHTS. Four groups of ops are priced at
# zero ON THE RECORD, each with a measurement or a stated reason behind it,
# and each as a NAMED constant so the next pass starts from a dial instead
# of from a rediscovery:
#   * draw / energy / spark / burst (and cost_mod, which is energy in
#     another costume). The v3 header records the sweep: "a measured sweep
#     rejected flat draw/energy/Spark/Burst proxies: raising them
#     monotonically reduced Klee's real-run result." Honouring a measurement
#     beats honouring a symmetry.
#   * raise_fanfare_cap. The op's own docstring carries the measurement:
#     read-at-cap under 1% under every pilot, so headroom is worth ~nothing
#     at current constants. It becomes live the moment floors stack.
#   * crash_fanfare. See its constant below -- pricing a cost whose paired
#     benefit is still invisible would be a bookkeeping asymmetry, not a
#     valuation.
#   * strip_block / transform_in_hand / remember_card, each for a reason
#     stated at its constant.
#
# WHAT THIS BUMP DOES NOT DO, named so the next reader does not assume it
# did: `bonus_formula` (20 printed uses -- `1_per_4_fanfare`,
# `2_per_salon_member`, `1_per_2_charge` ...) and self `apply_power` for
# non-engine powers (`salon_member`, 15 uses) are STILL priced at zero.
# They are the same defect in a different grammar, they are not ops, and
# folding them in here would have made the D12->D13 delta unattributable to
# the change the user accepted. They are this sprint's named still-owed.
# =========================================================================
# -- damage- and Block-shaped, near face value ----------------------------
STATIC_DELAYED_BLOCK_SHARE = 0.8   # block_next_turn: real printed Block one
                                   # turn late. It cannot answer the attack
                                   # in front of you, which is the discount.
STATIC_NEXT_ATTACK_SHARE = 0.8     # buff_next_attack: flat damage on the
                                   # next Attack; nearly always spent, small
                                   # discount for needing an Attack to spend
                                   # it on.
STATIC_CHAIN_ATTACK_MULT = 1.25    # chain_attack: the volley repeats once
                                   # per body it KILLS. Priced as its own
                                   # damage line plus a quarter -- a chain
                                   # that never kills is exactly the base
                                   # volley, and the drafter cannot see the
                                   # enemy HP that decides the rest.
STATIC_DETONATE_VALUE = 3.0        # detonate: the payoff that makes
                                   # STATIC_BOMB_DAMAGE_SHARE's half-price
                                   # placement real. Roughly one armed bomb
                                   # cashed early; `bonus` adds on top, and
                                   # an all_enemies detonation takes the
                                   # same STATIC_AOE_MULT the damage line
                                   # takes.
STATIC_BOMB_MOVE_VALUE = 1.0       # move_bombs: consolidation onto one
                                   # body, worth about a point before its
                                   # printed `bonus`.
# -- reaction machinery (Klee/Furina/Kokomi's shared elemental layer) ------
STATIC_AURA_VALUE = 2.0            # apply_aura: the reaction plan's entry
                                   # token, priced at the Weak/Vulnerable
                                   # magnitude. An aura is not damage; it is
                                   # what every amp payoff in three kits
                                   # reads.
STATIC_SWIRL_VALUE = 1.5           # swirl: spreads/consumes an aura someone
                                   # else applied, so it is worth less than
                                   # applying one and worth nothing alone.
STATIC_AURA_REFRESH_VALUE = 1.0    # refresh_all_auras: extends what is
                                   # already on the board; strictly weaker
                                   # than applying, and dead on a clean one.
# -- Furina's meter -------------------------------------------------------
STATIC_ENCORE_VALUE = 0.3          # per printed Encore point, either sign.
                                   # Between the Fanfare floor (0.2, pays
                                   # only through drafted readers) and
                                   # Charge (0.5, read by a kit state):
                                   # Encore is a real buffer the player
                                   # holds, but its converters are drafted.
                                   # spend_encore pays the SAME rate with
                                   # the sign flipped -- an overdraw is a
                                   # printed cost and must read as one.
STATIC_FANFARE_CAP_VALUE = 0.0     # raise_fanfare_cap. MEASURED INERT, not
                                   # unpriced: the op's docstring records
                                   # read-at-cap under 1% under every pilot.
STATIC_CRASH_FANFARE_VALUE = 0.0   # crash_fanfare. The Final Verdict's
                                   # crash is the PRICE of a damage line the
                                   # static scorer still cannot see
                                   # (`bonus_formula: 1_per_1_fanfare`).
                                   # Pricing the cost while the benefit
                                   # reads zero would make the sheet's only
                                   # Hyperbeam undraftable on a bookkeeping
                                   # asymmetry rather than on a valuation.
                                   # Held at 0.0 until the formula reader
                                   # lands, and this line is the reason it
                                   # must land before this dial moves.
STATIC_SALON_BOW_VALUE = 2.0       # salon_bow: one member's bow, on demand.
                                   # Priced at one conservative bow rather
                                   # than at the stage it implies -- the
                                   # drafter cannot see stage occupancy, and
                                   # the plan bonus already pays for the
                                   # Salon shape.
STATIC_SPOTLIGHT_DESIGNATE_VALUE = 1.5  # spotlight_designate: prints
                                   # nothing and is what the whole
                                   # Spotlight kit reads. Deliberately
                                   # modest: `_is_spotlight_access` already
                                   # pays it once through the archetype
                                   # term, and this is the universal half.
# -- cards from nowhere ---------------------------------------------------
STATIC_GENERATED_CARD_VALUE = 2.0  # per token generated into hand
                                   # (generate_guest_star, generate_from_
                                   # pool, add_card). A conjured card still
                                   # costs energy to play, so it is worth
                                   # well under a drafted one; rarity is NOT
                                   # differentiated, which is conservative
                                   # for the uncommon generators.
STATIC_OFFPILE_CARD_SHARE = 0.5    # the same token added to draw/discard
                                   # instead of hand: same card, later, and
                                   # maybe not this fight.
STATIC_STATUS_CARD_COST = 2.0      # a card added to your OWN piles whose
                                   # rarity is `status`: the same magnitude
                                   # with the sign flipped. Self-inflicted
                                   # bloat is a printed cost.
STATIC_CARD_COPY_VALUE = 3.0       # copy/replay of a card ALREADY in the
                                   # deck (copy_companion_in_hand,
                                   # copy_spotlighted_in_hand,
                                   # copy_companions_played_this_combat,
                                   # replay_next_companion). Worth more than
                                   # a conjured token because it duplicates
                                   # something the player chose.
STATIC_FREE_COPY_BONUS = 1.0       # `cost_override: 0` on such a copy.
STATIC_AUTOPLAY_VALUE = 2.0        # autoplay_from_exhaust /
                                   # autoplay_from_draw: a card played for
                                   # free, but not one the player picked.
                                   # One neutral card, the same
                                   # one-unit-of-a-live-count convention the
                                   # damage formulas use.
STATIC_EXTRA_SCREEN_VALUE = 2.0    # extra_card_screen: an extra reward
                                   # screen after a WON fight. Real
                                   # run-layer value, discounted for firing
                                   # only on a win.
# -- deck manipulation ----------------------------------------------------
STATIC_RANDOM_DISCARD_COST = 0.5   # per card discarded AT RANDOM. A
                                   # `select: chosen` discard is priced at
                                   # zero instead: the pilot discards
                                   # `_worst_card`, which makes it card
                                   # SELECTION, not card loss.
STATIC_EXHAUST_VALUE = 0.5         # exhaust_from, unfiltered: thinning.
STATIC_STATUS_EXHAUST_VALUE = 1.5  # exhaust_from `filter: status`: removing
                                   # a Status/Curse is the real version of
                                   # the same verb.
STATIC_SCRY_VALUE = 0.5            # scry_discard: exactly one worst card
                                   # leaves the top of the pile, whatever
                                   # the printed look-at count.
STATIC_RECALL_VALUE = 1.0          # recall_to_draw: a CHOSEN card from the
                                   # discard onto the top of the draw pile.
STATIC_UPGRADE_VALUE = 1.5         # upgrade_in_hand, per card upgraded --
                                   # combat-scoped here, which is why it is
                                   # under a full card's worth.
STATIC_GRANT_SLY_VALUE = 0.5       # grant_sly_this_turn: one turn of the
                                   # rider STATIC_SLY_SHARE already
                                   # half-prices when printed.
STATIC_STRIP_BLOCK_VALUE = 0.0     # strip_block. The op's docstring says it
                                   # plainly: enemies rarely carry Block in
                                   # tier0, and whether they should is a
                                   # question about the ENCOUNTER set. A
                                   # nonzero price here would answer it by
                                   # fiat.
STATIC_TRANSFORM_VALUE = 0.0       # transform_in_hand. Its value is
                                   # ENTIRELY the destination card, which
                                   # the static scorer would have to load
                                   # and re-price; no committed card prints
                                   # the op today, so the honest entry is a
                                   # zero with this sentence next to it.
STATIC_REMEMBER_CARD_VALUE = 0.0   # remember_card writes a payload that a
                                   # POWER later reads. The value is on the
                                   # power, where the self-power branch
                                   # already prices it; paying here too
                                   # would be double-counting.
# -- HP economy -----------------------------------------------------------
STATIC_HEAL_SHARE = 0.5            # heal, per point. Under the R52 healing
                                   # law healing converts to Block, and
                                   # out-of-combat HP is the run resource
                                   # the drafter cannot see the level of.
STATIC_MAX_HP_VALUE = 1.0          # gain_max_hp, per point: permanent HP
                                   # AND an immediate heal of the same size,
                                   # priced at one point of Block each.
# -- structural -----------------------------------------------------------
STATIC_REPEAT_SHARE = 0.5          # repeat_this multiplies the card's OWN
                                   # printed effects. Applied at half,
                                   # because every printed use of the op
                                   # sits behind a condition.
# -- the measured dead dials (see the header above) ------------------------
STATIC_DRAW_VALUE = 0.0            # draw, draw_while, draw_to_hand_size
STATIC_ENERGY_VALUE = 0.0          # energy, and cost_mod through it
STATIC_SPARK_VALUE = 0.0           # gain_spark, discard_for_sparks
STATIC_BURST_VALUE = 0.0           # burst_energy


# The op-parity table (Task 2 of the same sprint). EVERY key of
# tier0.engine.effects.OPS must appear here exactly once, with the one-line
# rationale for the price it receives in `_static_power.effect_power`.
# `tools/lint_op_parity.py` fails the build otherwise -- an op registered
# with no entry here is a FINDING, not a skip, in the same discipline
# `tools/lint_constant_parity.py` applies to the C# mirrors. Adding an op
# therefore forces a pricing decision at the moment the author still knows
# the answer, which is the whole point.
STATIC_OP_PRICING: dict[str, str] = {
    # --- priced before v13 -----------------------------------------------
    "damage": "face value; all_enemies takes STATIC_AOE_MULT bodies (v6)",
    "block": "face value; doubled on the exhausted_this_card times form",
    "apply_power": "self Strength/Dexterity/witchs_flame, enemy Weak/Vuln, "
                   "and a flat engine credit on POWER-type cards (v4/v12)",
    "place_bomb": "bomb damage at STATIC_BOMB_DAMAGE_SHARE + a guard credit",
    "conditional": "reachable-branch share; Klee's live predicates at half",
    "conscript": "STATIC_CONSCRIPT_VALUE per recruit (v7)",
    "gain_charge": "STATIC_CHARGE_VALUE per printed point (v7)",
    "summon_kurage": "ONE pulse, not the duration (v8)",
    "gain_fanfare_floor": "STATIC_FANFARE_FLOOR_VALUE per point (v9)",
    "grow_damage": "one discounted future redraw",
    # --- damage/Block-shaped, new in v13 ---------------------------------
    "block_next_turn": "printed Block at STATIC_DELAYED_BLOCK_SHARE",
    "buff_next_attack": "flat damage at STATIC_NEXT_ATTACK_SHARE",
    "chain_attack": "its own damage line x STATIC_CHAIN_ATTACK_MULT",
    "detonate": "STATIC_DETONATE_VALUE + printed bonus, AoE-scaled",
    "move_bombs": "STATIC_BOMB_MOVE_VALUE + bonus at bomb-damage share",
    "modify_bombs": "bonus at STATIC_BOMB_DAMAGE_SHARE, one neutral bomb",
    "chance_bomb_per_detonation": "chance x bomb damage x bomb-damage share",
    "strip_block": "ZERO: STATIC_STRIP_BLOCK_VALUE, an encounter-set question",
    # --- reaction machinery ----------------------------------------------
    "apply_aura": "STATIC_AURA_VALUE per applied aura, AoE-scaled",
    "swirl": "STATIC_SWIRL_VALUE; needs an aura it did not apply",
    "refresh_all_auras": "STATIC_AURA_REFRESH_VALUE, dead on a clean board",
    # --- Furina's meter ---------------------------------------------------
    "gain_encore": "STATIC_ENCORE_VALUE per printed point",
    "spend_encore": "the same rate, NEGATIVE: an overdraw is a printed cost",
    "raise_fanfare_cap": "ZERO: STATIC_FANFARE_CAP_VALUE, measured inert",
    "crash_fanfare": "ZERO: STATIC_CRASH_FANFARE_VALUE until the meter-read "
                     "formula is priced; see the constant",
    "salon_bow": "STATIC_SALON_BOW_VALUE per bow taken",
    "spotlight_designate": "STATIC_SPOTLIGHT_DESIGNATE_VALUE, the universal "
                           "half of what the archetype term already pays",
    "generate_guest_star": "STATIC_GENERATED_CARD_VALUE per token",
    "copy_spotlighted_in_hand": "STATIC_CARD_COPY_VALUE per copy",
    # --- cards from nowhere ----------------------------------------------
    "add_card": "STATIC_GENERATED_CARD_VALUE per token, off-pile share "
                "applied, NEGATIVE for a `status`-rarity add",
    "generate_from_pool": "STATIC_GENERATED_CARD_VALUE per token",
    "copy_companion_in_hand": "STATIC_CARD_COPY_VALUE (+ free-cost bonus)",
    "copy_companions_played_this_combat": "one neutral unique companion",
    "replay_next_companion": "STATIC_CARD_COPY_VALUE per replay",
    "autoplay_from_exhaust": "STATIC_AUTOPLAY_VALUE, one neutral card",
    "autoplay_from_draw": "STATIC_AUTOPLAY_VALUE per card taken",
    "extra_card_screen": "STATIC_EXTRA_SCREEN_VALUE per screen earned",
    # --- deck manipulation ------------------------------------------------
    "discard": "NEGATIVE at STATIC_RANDOM_DISCARD_COST when random; a "
               "`chosen` discard is selection, not loss, and prices at zero",
    "discard_for_sparks": "chosen discard (no cost) + Sparks at the dead dial",
    "exhaust_from": "STATIC_STATUS_EXHAUST_VALUE filtered, else "
                    "STATIC_EXHAUST_VALUE",
    "scry_discard": "STATIC_SCRY_VALUE; one card leaves however many are seen",
    "recall_to_draw": "STATIC_RECALL_VALUE per chosen card recalled",
    "upgrade_in_hand": "STATIC_UPGRADE_VALUE per card upgraded",
    "grant_sly_this_turn": "STATIC_GRANT_SLY_VALUE, one turn of the rider",
    "remember_card": "ZERO: STATIC_REMEMBER_CARD_VALUE, paid on the power",
    "transform_in_hand": "ZERO: STATIC_TRANSFORM_VALUE, value is the "
                         "destination card",
    # --- HP economy --------------------------------------------------------
    "heal": "STATIC_HEAL_SHARE per point",
    "gain_max_hp": "STATIC_MAX_HP_VALUE per point (permanent HP + a heal)",
    # --- structural --------------------------------------------------------
    "repeat_this": "multiplies the card's own effects at STATIC_REPEAT_SHARE",
    # --- the measured dead dials -------------------------------------------
    "draw": "ZERO: STATIC_DRAW_VALUE, the v3 flat-proxy sweep",
    "draw_while": "ZERO: STATIC_DRAW_VALUE on two neutral cards",
    "draw_to_hand_size": "ZERO: STATIC_DRAW_VALUE on the refill",
    "energy": "ZERO: STATIC_ENERGY_VALUE, the v3 flat-proxy sweep",
    "cost_mod": "ZERO: energy in another costume, priced through "
                "STATIC_ENERGY_VALUE",
    "gain_spark": "ZERO: STATIC_SPARK_VALUE, the v3 flat-proxy sweep",
    "burst_energy": "ZERO: STATIC_BURST_VALUE, the v3 flat-proxy sweep",
}


def _op_signature(card: Card) -> frozenset:
    return frozenset(fx.get("op") for fx in card.effects)


# Fanfare is a native-resource plan, not a four-card assembly puzzle.  One
# Aria of Recompense supplies five printed points of meter movement before the
# first reward screen.  Once that coverage exists, more generation is useful
# support but has sharply diminishing draft value; the priority is securing a
# card that converts held Fanfare into immediate output.
FANFARE_GENERATION_COVERAGE = 5
# DRAFTER_VERSION 9: the plan's second half is no longer "own a converter"
# (that grammar is retired) but "own a baseline the meter rests on". The bar
# is deliberately a low single-card threshold -- core_complete asks whether
# the plan is ONLINE, not whether it is finished.
#
# The UNIT used to be "one uncommon Power's automatic grant", which was 5
# because the engine handed 5 to every Power played. Track B (2026-07-28)
# deleted that automatic, so the number no longer derives from anything: it
# is now simply the smallest PRINTED "Fanfare +X" the sheet carries. Held at
# 5 deliberately rather than retuned, so this instrument does not move
# underneath the sprint that is measuring against it -- but it is a bar with
# no derivation behind it any more, and re-deriving it belongs to whichever
# pass next rules the keyword's numbers.
FANFARE_FLOOR_COVERAGE = 5.0
# DRAFTER_VERSION 10 (G-E1): the third limb, and the one whose ABSENCE was the
# instrument bug. Generation and floor are both INPUTS -- they move the meter
# and they raise its baseline -- and a plan built entirely of inputs reads a
# stat nothing cashes. Without this limb `core_complete("fanfare")` reported
# 85.7-86.0% online while the average deck held 1.87 readers in 20 cards, and
# the fanfare sprint's close-out banned measuring anything against it until it
# was fixed.
#
# ONE, not more. `core_complete` asks whether the plan is ONLINE, not whether
# it is finished -- the same low single-card bar the other two limbs use. The
# question of how many readers a fanfare deck SHOULD hold is exactly the
# draft-reach question, and it belongs to the pool-sweep pass with this
# instrument in hand, not to the instrument itself.
FANFARE_PAYOFF_COVERAGE = 1
# DRAFTER_VERSION 14: the generic limb's sibling of the constant above, and
# it is deliberately the SAME number. `core_complete` asks whether the plan
# is online; one printed payoff is the smallest deck that can cash whatever
# the enablers assemble. It lives here rather than in tier0/constants.py
# beside DRAFT_CORE_SIZE because it is a drafter-instrument bar with no C#
# counterpart -- the constant-parity lint compares tier0 against the mod.
GENERIC_PAYOFF_COVERAGE = 1
FANFARE_FIRST_FLOOR = 2.0     # was FANFARE_FIRST_CONVERTER
FANFARE_LATER_FLOOR = 1.5     # was FANFARE_LATER_CONVERTER
FANFARE_READER_VALUE = 1.0
FANFARE_SURPLUS_GENERATION_CAP = 1.0
FANFARE_SELF_DAMAGE_COST = 0.5
FANFARE_SKIP_THRESHOLD = 1.5


def _fanfare_plan_score(card: Card, deck: list[Card],
                        online: bool) -> float:
    """Contextual plan value after universal printed power is counted."""
    if _grants_fanfare_floor(card):
        return FANFARE_LATER_FLOOR if online else FANFARE_FIRST_FLOOR

    score = FANFARE_READER_VALUE if _reads_fanfare(card) else 0.0
    generation = _fanfare_generation(card)
    if generation:
        covered = _fanfare_generation_total(deck)
        if covered < FANFARE_GENERATION_COVERAGE:
            missing = FANFARE_GENERATION_COVERAGE - covered
            score += min(3.0, generation, missing) * 0.6
        else:
            score += min(FANFARE_SURPLUS_GENERATION_CAP,
                         generation / FANFARE_GENERATION_COVERAGE)
    # HP loss does move the meter, but it is not free generation in a run
    # where deaths persist.  The ordinary static-power proxy cannot express
    # printed downsides, so price that risk here rather than teaching the
    # Fanfare drafter to prefer the six-damage uncapping setup card.
    return score - _self_damage(card) * FANFARE_SELF_DAMAGE_COST


def score_offer(card: Card, deck: list[Card], archetype: str) -> float:
    s = 0.0
    progress = _core_progress(deck, archetype)
    online = core_complete(deck, archetype)
    # A card that ADVANCES the core is never a dead pick — without this,
    # reaction deadlocks: its core contains an amp payoff, but payoffs
    # were gated on the core being online (measured: 1% amp assembly).
    # DRAFTER_VERSION 11 (R83): on the GENERIC anchors every plan-shaped
    # bonus below is scaled by one swept multiplier. The anchor sheets'
    # role labels "stand in for engine cards", but the measured lifts say
    # the labels do not track generic value (anticipate, role enabler,
    # scored 6.25 with 0.00 static power and carries a -16.9 lift; deflect,
    # role glue, scored 2.83 and carries +25.3) -- so how much plan value
    # a label is worth on an anchor is a measured dial, not an assumption.
    plan_mult = GENERIC_PLAN_BONUS_MULT if archetype == "generic" else 1.0
    if _core_progress(deck + [card], archetype) > progress:
        s += 3.0 * plan_mult
    # DRAFTER_VERSION 3: v2's raw-power term now includes conservative
    # Bomb/debuff/conditional-Block proxies. A plan-committed drafter that
    # reads those direct effects as literal zero is no more plausible than one
    # with no power awareness. Flat draw/resource proxies were measured and
    # rejected; those effects need deck context rather than a face-value bump.
    # Share-synergy stays excluded -- assigned already prices fit off its
    # target, and stacking share-synergy would double-count it.
    s += min(3.0, _static_power(card, deck) / 3.0)
    if (archetype == "generic" and not card.is_companion
            and card.role in ("enabler", "payoff")):
        # The anchor's roles stand in for engine cards. (Its old private
        # power term dissolved into the universal one above.)
        s += 1.0 * plan_mult
    # Same exclusion as adaptive_score: companions get the dedicated block
    # below. Without this the derived reaction tag silently re-tunes assigned
    # mode too, which would move the frozen M5 numbers for a reason that has
    # nothing to do with the drafting question they were measuring.
    if (archetype == "fanfare"
            and "fanfare" in card.archetypes
            and not card.is_companion):
        s += _fanfare_plan_score(card, deck, online)
    elif archetype in card.archetypes and not card.is_companion:
        if card.role == "enabler":
            s += 3.0 * max(0.25, 1.0 - progress) * plan_mult
        elif card.role == "payoff":
            if archetype == "reaction" and _is_amp_payoff(card):
                s += 4.0 if online else REACTION_AMP_OFFLINE
            else:
                s += (4.0 if online else 1.0) * plan_mult
        else:
            s += 1.5 * plan_mult
    elif "generic" in card.archetypes:
        s += 0.8
    if card.is_companion:
        if archetype == "reaction":
            # Companions ARE reaction's enablers (deliberate asymmetry).
            s += (REACTION_APPLIER_WEIGHT * max(0.25, 1.0 - progress)
                  if _is_applier(card) else 1.5)
        elif archetype == "spotlight":
            # Guest Cast buffs every Companion, so a mixed cast is coherent:
            # no same-character depth requirement and no selector-v3 trap.
            s += 3.0 * max(0.25, 1.0 - progress)
        else:
            s += 0.5
    if _has_block(card) and _block_density(deck) < C.DRAFT_BLOCK_DENSITY_MIN:
        s += 2.5                                     # defense quota
    if archetype == "generic":
        # DRAFTER_VERSION 11 (R83): the redundancy discount, anchors only.
        s -= GENERIC_REDUNDANCY_PENALTY * sum(
            1 for c in deck if c.rarity in C.RARITY_ODDS
            and _op_signature(c) == _op_signature(card))
    cost = card.cost if isinstance(card.cost, int) else 2
    avg_cost = (sum(c.cost for c in deck if isinstance(c.cost, int))
                / max(1, sum(1 for c in deck if isinstance(c.cost, int))))
    if cost >= 2 and avg_cost > 1.3:
        s -= 1.0                                     # curve awareness
    s -= max(0, len(deck) - C.DRAFT_DECK_SOFT_CAP) * 0.4   # deck bloat
    if archetype == "reaction":
        # Ruling R2.2 folds in the §3 finding: reaction uniquely prefers
        # lean decks (20.2% at 13.4 cards under threshold 2.0). Expressed
        # as scorer behavior — a steeper bloat line for reaction — so the
        # skip threshold stays one global constant instead of forking.
        # LATENT (review pass): past DRAFT_DECK_SOFT_CAP this line STACKS
        # with the global penalty (combined 0.8/card — the slope the R2.2
        # sweep rejected from cap 13). Unreachable today: 10 reward
        # screens cap decks at 20, so the global line has never fired in
        # tier05. The sweep measured the stacked form as-is; if a future
        # template exceeds ~12 screens, re-sweep before trusting either
        # coefficient past 22.
        s -= max(0, len(deck) - REACTION_LEAN_CAP) * REACTION_LEAN_PENALTY
    return s


def assigned_policy(rng: random.Random, deck: list[Card],
                    offers: list[Card], archetype: str) -> Optional[Card]:
    if not offers:
        return None
    scored = sorted(((score_offer(c, deck, archetype), i, c)
                     for i, c in enumerate(offers)), reverse=True)
    best_score, _, best = scored[0]
    threshold = (FANFARE_SKIP_THRESHOLD if archetype == "fanfare"
                 else GENERIC_SKIP_THRESHOLD if archetype == "generic"
                 else C.DRAFT_SKIP_THRESHOLD)
    if best_score < threshold:
        return None                                  # skip is a real pick
    n = len(deck)
    if n >= DRAFT_LEAN_CAP:
        # v5 late-run discipline + the v6 rare strong-pick hatch (see the
        # constants blocks above).
        score = {i: s for s, i, c in scored}
        ok = [c for i, c in enumerate(offers)
              if c.type == "power" or _has_tempo(c)
              or (n < DRAFT_LEAN_BLOCK_CAP and _has_block(c))
              or (c.rarity == "rare" and score[i] >= DRAFT_LEAN_RARE_BAR)]
        if not ok:
            return None
        return max(ok, key=lambda c: score_offer(c, deck, archetype))
    return best


# ---------------------------------------------------------------------------
#  M6: the adaptive policy -- the goodstuff detector
# ---------------------------------------------------------------------------

ARCHETYPES = ("demolition", "spark", "reaction")

# POLICY_VERSION 2 (G-E3, "Ship What We Know", 2026-07-25). The free-drafting
# instrument.
#
# v1 -- the implicit pre-stamp generation -- is every policy number taken
# before this date: `assigned_policy` (plan-committed) and `adaptive_policy`
# (emergent) as they stood, with ARCHETYPES above hardcoded to KLEE's three.
#
# That hardcoding is the finding. `adaptive_score` is already exactly what
# G-E3 describes -- standalone power plus synergy weighted by what the deck
# has accumulated, with no assigned label anywhere in it -- but its archetype
# term begins `if a not in ARCHETYPES: continue`, and none of Furina's plans
# are in ARCHETYPES. So running "free draft" on Furina today would not have
# measured free drafting. It would have measured a scorer that cannot see
# salon, spotlight or fanfare AT ALL, and reported the result as evidence
# about drafting behaviour. Every Furina card would have scored as pure
# printed power plus the universal block quota.
#
# So the archetype set becomes character-aware. KLEE'S NUMBERS DO NOT MOVE --
# her tuple is unchanged and every other character had no synergy term to lose
# -- which is why this is a policy bump rather than a drafter bump.
#
# POLICY_VERSION 3 (R66, 2026-07-26). v2 made the registry character-aware,
# and Kokomi's entry in it named three tags that existed on ZERO cards -- so
# she kept the exact defect v2 was written to remove: a scorer structurally
# blind to her archetypes, reporting its output as evidence about drafting.
#
# EVERY adaptive/free-draft Kokomi number ever taken was measured through the
# broken registry and is ARCHIVED as of this ruling. Klee's and Furina's
# tuples are untouched and their numbers do not move. Assigned-plan Kokomi
# numbers (the R56 battery) STAND: they route through runner.py's plan
# registry, which was always correct.
POLICY_VERSION = 3

# F1 (Serenitea Sweep): DERIVED from tier0/roster.py, which is now the one
# place a character's archetype vocabulary is declared -- and where it is
# cross-checked against the tags her cards actually carry. R66 happened because
# two registries in one repo disagreed and nothing compared them; the registry
# is now compared, so neither direction of that can recur:
#
#   * a registry naming a tag that exists on zero cards FAILS
#     (this is R66 exactly: ("garment", "ward", "conscript") matched nothing,
#     dominant_archetype() returned "goodstuff" for every Kokomi deck, and
#     every adaptive number ever taken for her was measured through it);
#   * a card tag no registry knows about FAILS too, which is the direction a
#     derived-from-cards version would have silently absorbed.
#
# What did NOT change: Klee's and Furina's tuples, and the values here. The
# per-character history moved into the registry rows beside the values it
# explains.
ROSTER_ARCHETYPES: dict[str, tuple[str, ...]] = {
    c.id: c.archetypes for c in roster.ROSTER
}


def archetypes_for(deck: list[Card]) -> tuple[str, ...]:
    """Which archetype family this deck's character plays in.

    Read from the cards rather than passed in, because the whole point of a
    free-drafting policy is that it never receives a plan label -- and a
    character label smuggled down the same channel would be the first step
    back toward one. The character is a property of the deck that exists
    whether or not anyone has a plan.

    Falls back to Klee's set for decks with no character (synthetic test
    decks, the reference characters' generic anchor), which is what every
    caller got before this existed.
    """
    for card in deck:
        family = ROSTER_ARCHETYPES.get(getattr(card, "character", None) or "")
        if family:
            return family
    return ARCHETYPES


def archetype_shares(deck: list[Card], *, companions: bool = True) -> dict[str, float]:
    """What fraction of the deck's *drafted, committed* cards belong to each
    archetype.

    Committed means carrying a real archetype tag: generic glue is excluded,
    because counting it would dilute every share toward zero and flatten
    exactly the signal this is here to detect.

    BASICS ARE EXCLUDED, and that exclusion is load-bearing rather than
    tidiness. Klee's starting deck contains Jumpy Dumpty and Pop, both tagged
    `demolition`, so including basics puts every run at demolition share 1.0
    before a single reward screen is shown. Measured with basics in, adaptive
    drafting "converged" on demolition in 100% of runs -- which was the
    starting deck being read back, not a pool finding. Spec §4 asks for
    commitment emerging from *what has been drafted*, and the starter was not
    drafted. Rarity separates the two exactly: every starter card is basic and
    basic never appears in the draftable pool.

    Klee's starter does give demolition a real head start in play, and that is
    deliberate design. It is a fact about her kit, not evidence about whether
    the pool's archetypes pull -- so it belongs in the report, not in this
    number.

    COMPANIONS ARE EXCLUDED WHEN MEASURING COMMITMENT (`companions=False`), for
    the same reason basics are: commitment means choosing something scarce, and
    companions are not scarce. The reward screen carries a GUARANTEED companion
    slot, so every deck is offered one every screen and drafting them signals
    nothing about a plan.

    Counting them measured that directly. With companions in, 65.6% of decks
    classified as reaction and the dominance alarm fired -- but only 3.5% of
    those decks had an online reaction core, and 60.7% of their tagged cards
    were companions. The classifier had stopped reporting "what plan did this
    deck commit to" and started reporting "how many companions did it draft",
    which is nearly constant across runs.

    Scoring still counts them (`companions=True`, the default): a deck holding
    six appliers really should value Burst and an amp payoff more highly. That
    is a claim about what the deck can DO. Classification is a claim about what
    the drafter CHOSE. Those are different questions and they get different
    card sets -- deliberately, and documented, rather than the accidental
    disagreement that existed when companions carried no tag at all.
    """
    # POLICY_VERSION 2: the key set follows the deck's character. Klee's is
    # unchanged, so her shares -- and every number derived from them -- are
    # identical to v1.
    family = archetypes_for(deck)
    tagged = [c for c in deck
              if c.rarity != "basic"
              and (companions or not c.is_companion)
              and any(a in family for a in c.archetypes)]
    if not tagged:
        return {a: 0.0 for a in family}
    return {a: sum(1 for c in tagged if a in c.archetypes) / len(tagged)
            for a in family}


def dominant_archetype(deck: list[Card],
                       threshold: float = C.ADAPTIVE_COMMIT_THRESHOLD) -> str:
    """The deck's emergent shape, or 'goodstuff' if it never committed.

    'goodstuff' is not a failure of the classifier -- it is the finding the
    divergence metric exists to surface. A pool where adaptive drafting never
    commits is a pool whose archetypes are not pulling.
    """
    shares = archetype_shares(deck, companions=False)   # commitment == scarce
    top = max(shares, key=lambda a: shares[a])
    return top if shares[top] >= threshold else "goodstuff"


def adaptive_score(card: Card, deck: list[Card]) -> float:
    """Pure power + synergy. NO assigned archetype anywhere in here.

    Commitment is emergent: synergy is weighted by the share each archetype
    already holds in the deck, so early picks are near-pure power and later
    picks are pulled toward whatever happened to accumulate. That rich-get-
    richer term is the whole experiment -- if the pool still converges on one
    shape across many seeds, the convergence is the pool's, not the policy's.
    """
    s = min(3.0, _static_power(card, deck) / 3.0)
    shares = archetype_shares(deck)
    # Companions are scored by the dedicated block below, NOT here. They now
    # carry a derived `reaction` tag so that archetype_shares can see them --
    # that was the actual bug -- but the scorers always had bespoke companion
    # handling, so running them through the generic archetype term as well pays
    # reaction's share twice and turns the rich-get-richer loop into a runaway:
    # measured, it drove reaction from 13.2% to 85.5% of decks with both
    # divergence alarms firing. The tag fixes the METRIC; it is not new scoring.
    family = archetypes_for(deck)
    for a in (card.archetypes if not card.is_companion else ()):
        if a not in family:
            continue
        share = shares[a]
        if card.role == "payoff":
            # Payoffs are worth what their enablers make them worth. Unlike
            # assigned mode this is a smooth ramp rather than a core gate:
            # adaptive has no core to be online, so a hard gate would make
            # payoffs permanently unpickable and no shape could ever finish.
            s += 5.0 * share
        elif card.role == "enabler":
            s += 1.2 + 2.0 * share
        else:
            s += 0.8 + 1.0 * share
    if card.is_companion:
        # Companions are off-plan power: always playable, never scaling.
        s += 1.5 if _is_applier(card) else 1.0
        # .get, because POLICY_VERSION 2 made the share keys character-aware
        # and "reaction" is Klee's plan. On a roster that has no reaction
        # archetype this term is correctly zero rather than a KeyError -- the
        # claim it encodes ("companions are reaction's enablers") is a claim
        # about Klee's pool, not a universal one.
        s += 2.0 * shares.get("reaction", 0.0)
    if _has_block(card) and _block_density(deck) < C.DRAFT_BLOCK_DENSITY_MIN:
        s += 2.5                            # defense quota is universal
    cost = card.cost if isinstance(card.cost, int) else 2
    avg_cost = (sum(c.cost for c in deck if isinstance(c.cost, int))
                / max(1, sum(1 for c in deck if isinstance(c.cost, int))))
    if cost >= 2 and avg_cost > 1.3:
        s -= 1.0
    s -= max(0, len(deck) - C.DRAFT_DECK_SOFT_CAP) * 0.4
    return s


def adaptive_policy(rng: random.Random, deck: list[Card],
                    offers: list[Card], archetype: str) -> Optional[Card]:
    """Same callable shape as assigned_policy; `archetype` is ignored by
    construction -- that is the point, and the A/B harness depends on the two
    policies being swappable."""
    if not offers:
        return None
    scored = sorted(((adaptive_score(c, deck), i, c)
                     for i, c in enumerate(offers)), reverse=True)
    best_score, _, best = scored[0]
    if best_score < C.DRAFT_SKIP_THRESHOLD:
        return None
    return best


# Adaptive's plan is EMERGENT, and that must hold at rest sites too, not
# just reward screens. M7 smithing picks an on-plan card, and passing the
# assigned label into that choice made adaptive runs vary with a label the
# policy is defined not to see -- measured: 5/40 seeds diverged, 2/40 win
# flips (review-workflow catch). run_one reads this flag and derives the
# rest plan from dominant_archetype(deck) instead.
adaptive_policy.emergent_plan = True


# DRAFTER_VERSION 2: the hybrid IS the assigned drafter now — ruling
# R2.1 adopted its power term into score_offer, so the diagnostic that
# beat both parents (M7 §4) graduated to the standard model. The alias
# stays so experiment scripts and grid tables keep running; it is not a
# third arm of anything anymore. CAVEAT (review pass): the alias
# reproduces the archived hybrid only for the three measured archetypes.
# In GENERIC-anchor mode the old hybrid double-counted power (private
# anchor term + hybrid term); v2 removed the double-count, so a generic
# hybrid re-run will not match any pre-v2 generic number (none were
# published — M7's hybrid tables cover the three archetypes only).
hybrid_policy = assigned_policy


# The A/B pair. hybrid_policy is a diagnostic run on demand (see its
# docstring), not a third arm of the standing A/B.
POLICIES = {"assigned": assigned_policy, "adaptive": adaptive_policy}


def offer_advances_plan(offers: list[Card], deck: list[Card],
                        archetype: str) -> bool:
    """Reward relevance (spec §5): did this screen offer anything that moves
    the run's plan forward?

    Deliberately NOT 'did the policy take something' -- a screen can be worth
    taking from without advancing the plan (defense quota, raw power), and
    conflating the two would measure the policy instead of the pool.

    STRICT: an offer advances the plan iff it strictly increases core progress.

    The old second clause -- "or is an on-plan enabler/payoff" -- was removed
    because it was not a widening, it was the whole test. For demolition and
    spark, `_core_progress` rises exactly when a card is an on-plan
    enabler/payoff, so clause 2 subsumed clause 1 and the function never read
    the deck at all: predicting from the offers alone was correct in 214/214
    cases for both archetypes. That made the docstring's "the deck can still
    use" untrue, and it counted a 7th demolition enabler handed to an
    already-online deck as advancing a plan that was already finished.

    Only reaction behaved differently (14/214), because appliers move its core
    without carrying an archetype tag -- which is why reaction was the one
    archetype whose relevance moved with the policy.

    The measured effect of tightening this is small and downward: it removes
    offers that were already complete-core no-ops. Relevance was NOT rescued by
    the stricter reading, so the 60-70% claim fails under both.
    """
    progress = _core_progress(deck, archetype)
    return any(_core_progress(deck + [c], archetype) > progress for c in offers)


def offer_worth_engaging(offers: list[Card], deck: list[Card],
                         archetype: str) -> bool:
    """The LOOSE read, reported as a secondary and never enforced.

    This is the two-clause definition that was removed from
    offer_advances_plan for subsuming the strict one -- reintroduced here
    deliberately, under the name that says what it measures. The morning
    triage ruling revised the 60-70% claim rather than failing it: the
    faith-era number conflated "advances the plan" (strict, now the
    enforced >=35% floor) with "worth engaging with" (this: an on-plan
    card is on offer, even if the plan no longer needs it). Expected
    60-75%, unenforced."""
    if offer_advances_plan(offers, deck, archetype):
        return True
    return any(archetype in c.archetypes and c.role in ("enabler", "payoff")
               for c in offers)


def draft_regret(rng: random.Random, decisions: list[dict],
                 final_deck: list[Card], archetype: str) -> int:
    """Post-run re-scoring of sampled decisions in the final-deck context.
    Returns the number of regretted decisions among the sample."""
    regrets = 0
    for d in decisions:
        if rng.random() >= C.DRAFT_REGRET_SAMPLE:
            continue
        rescored = {c.id: score_offer(c, final_deck, archetype)
                    for c in d["offers"]}
        picked = d["picked"]
        picked_score = rescored.get(picked, 0.0)     # skip scores 0
        if any(v > picked_score + 1.0 for v in rescored.values()):
            regrets += 1
    return regrets
