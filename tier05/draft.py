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

    Powers grant by rarity without printing an op, so they count here too:
    the grant is a rule of the engine, not a line on the card, and a drafter
    that could only see the explicit op would systematically undervalue every
    Power the archetype drafts.
    """
    total = float(sum(fx.get("amount", 0)
                      for fx in _nested_effects(card.effects)
                      if fx.get("op") == "gain_fanfare_floor"))
    if card.type == "power":
        total += (C.FANFARE_FLOOR_PER_POWER_RARE if card.rarity == "rare"
                  else C.FANFARE_FLOOR_PER_POWER)
    return total


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
    on-plan enabler/payoff cards.)"""
    if archetype == "reaction":
        appliers = sum(1 for c in deck if _is_applier(c))
        amps = sum(1 for c in deck if _is_amp_payoff(c))
        return appliers >= 2 and amps >= 1
    if archetype == "spotlight":
        access = sum(1 for c in deck if _is_spotlight_access(c))
        machinery = sum(1 for c in deck if _is_spotlight_machinery(c))
        return access >= 2 and machinery >= 1
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
            and sum(1 for c in deck if _reads_fanfare(c))
            >= FANFARE_PAYOFF_COVERAGE
        )
    on_plan = sum(1 for c in deck if archetype in c.archetypes
                  and c.role in ("enabler", "payoff"))
    return on_plan >= C.DRAFT_CORE_SIZE


def _core_progress(deck: list[Card], archetype: str) -> float:
    if archetype == "reaction":
        appliers = min(2, sum(1 for c in deck if _is_applier(c)))
        amps = min(1, sum(1 for c in deck if _is_amp_payoff(c)))
        return (appliers + amps) / 3
    if archetype == "spotlight":
        access = min(2, sum(1 for c in deck if _is_spotlight_access(c)))
        machinery = min(1, sum(
            1 for c in deck if _is_spotlight_machinery(c)))
        return (access + machinery) / 3
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
        payoff = min(
            1.0,
            sum(1 for c in deck if _reads_fanfare(c)) / FANFARE_PAYOFF_COVERAGE,
        )
        return (generation + baseline + payoff) / 3
    on_plan = sum(1 for c in deck if archetype in c.archetypes
                  and c.role in ("enabler", "payoff"))
    return min(1.0, on_plan / C.DRAFT_CORE_SIZE)


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
            elif fx.get("op") == "damage" and fx.get("target") != "self":
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
        return total

    total = effect_power(card.effects)
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


def _op_signature(card: Card) -> frozenset:
    return frozenset(fx.get("op") for fx in card.effects)


# Fanfare is a native-resource plan, not a four-card assembly puzzle.  One
# Aria of Recompense supplies five printed points of meter movement before the
# first reward screen.  Once that coverage exists, more generation is useful
# support but has sharply diminishing draft value; the priority is securing a
# card that converts held Fanfare into immediate output.
FANFARE_GENERATION_COVERAGE = 5
# DRAFTER_VERSION 9: the plan's second half is no longer "own a converter"
# (that grammar is retired) but "own a baseline the meter rests on". One
# uncommon Power's grant is the unit; the bar is deliberately a low
# single-card threshold, matching the converter predicate it replaces --
# core_complete asks whether the plan is ONLINE, not whether it is finished.
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
