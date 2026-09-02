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
from dataclasses import replace
from typing import Optional

from tier0 import constants as C
from tier0 import roster
from tier0.engine.state import Card, sly_riders


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
# W3 (EB-118 Phase 3, R211) -- the Spotlight pricing rider's share.
#
# 0.167 IS THE MEASURED RATE, not a judgement: `spotlight_moved_this_turn`
# reads true on 16.7% of plays in `furina/spotlight_weighted` and on 2.0% of
# plays in the salon and fanfare arms -- an eight-fold plan lock, which is what
# makes the branch a real bar rather than decoration.
#
# WHY THE MEASURED RATE RATHER THAN KLEE'S 0.5 PRECEDENT, and this is the one
# judgement in it: R211 ratified the RIDER but not the SHARE, so the value is
# chosen under R194's direction rule -- every one-directional error in this
# file must make the drafter PASS ON A GOOD CARD, never pay for something it
# cannot see. Both 0.5 (the shape-matching choice: Klee's 0.5 covers exactly
# this class, a branch the player can arrange and the drafter cannot see) and
# 0.167 are defensible; 0.167 is the maximally conservative of the two, and
# anything at or above 1.0 is not defensible at all -- at share 1.0
# `take_it_from_the_top` would price 15.00 base, one of the biggest-priced
# Uncommon Skills on Furina's sheet, on the strength of a branch that fires on
# a sixth of plays in its own arm. [USER] holds the value; this is the second
# of W3's two overridable numbers (the first is STATIC_SPARK_SPEND_COST).
#
# ITS WHOLE REACH IS TWO ROWS, measured card by card rather than inferred:
# `take_it_from_the_top` 5.0000/5.0000 -> 6.6700/7.3400 (the base-to-upgraded
# gap goes from 0.00 to 0.67, which is the entire point of taking the rider),
# and `curtain_cue` 0.0000 -> 0.4000. `directors_cut` does NOT move at any
# share, because both its branches pay in dead dials -- energy and draw.
#
# RECALIBRATION IS OWED AND ITS DIRECTION IS RULED ([USER] 2026-08-25): 0.167
# is the rate a pilot that does not PLAN Spotlight movement produces, which
# makes it a floor on the human rate rather than an estimate of it -- the
# player controls the re-aim, and the card creates a deliberate two-card
# sequence. Recalibrate this share when the pilot learns to plan Spotlight
# movement; until then it stays where the measurement put it.
STATIC_SPOTLIGHT_MOVED_SHARE = 0.167
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
                              # +1 damage per `GARMENT_CHARGE_DIVISOR` Charge
                              # while it holds -- 2 since the v0.3 charge-curve
                              # pass, not the 4 this comment used to say), so
                              # banked points are never dead -- but one
                              # Garment window is all this prices in

# These predicates are readable before a card is played. Mid-resolution
# conditions such as reaction_triggered_by_this and killed_target remain out:
# valuing their best branch unconditionally would recreate the old power bias.
#
# THE UNDER-CREDIT THAT FALLS OUT OF THAT IS ACCEPTED, IN WRITING, HERE
# (EB-118 Phase 2B, the [USER] body ruling of 2026-08-24). A predicate that is
# not in this set does not get a discounted branch -- `effect_power` never
# recurses into it at all, so the branch is credited at ZERO. Big Badda Boom's
# ruled rider ("if it kills, deal 8 to a random other enemy") is therefore
# invisible to the drafter: the card prices at 4.8 base / 8.0 upgraded with the
# rider exactly as it did without it. So does sparkly_explosion's kill branch,
# and showstopper's, and they have priced that way since they shipped -- this
# note names the convention rather than introducing it.
#
# It is accepted on R194's terms and for R194's reason (the Deep Breath modal
# under-credit, [USER] 2026-08-23), and the test that owns the acceptance is
# `tier05/tests/test_ethereal_draft_valuation.py`:
#   * The error is ONE-DIRECTIONAL. Crediting a kill branch would require
#     guessing how often the swing kills, which is a board fact the drafter has
#     no access to; refusing to guess makes the drafter UNDERvalue the card and
#     never overvalue it. The failure it can cause is passing on a good card,
#     not paying for a bad one.
#   * It does NOT move the Ethereal read. The rider is on both faces and prices
#     at zero on both, so the base:upgraded ratio R193's trigger reads is
#     untouched (the trigger note at STATIC_ETHEREAL_SHARE carries this).
#   * REPRICING TRIGGER, inherited not invented: the first time a kill-gated
#     branch has to be told apart from its own base card by a drafted price.
#     Nothing today needs that, because the pilot reads the live predicate at
#     play time (tier0.pilot.policy) and the drafter's blindness costs only an
#     offer ranking.
STATIC_STATE_CONDITIONS = frozenset({
    "has_spark",
    "target_has_nonpyro_aura",
    "target_has_power_vulnerable",
    "card_exhausted_this_turn",
    "hp_lost_this_turn",
    # W3 (EB-118 Phase 3, R211) -- the Spotlight pricing rider. Added WITH the
    # first card whose whole upgrade the offer screen could not otherwise see:
    # `take_it_from_the_top` takes `{conditional_damage: +4}` on a branch gated
    # by this name, and while the name was unpriced the card read 5.0000 on
    # BOTH faces. The ruling took the delta and the rider together, and the
    # rider is what makes the delta visible.
    "spotlight_moved_this_turn",
    # C20 (R189 C2). NOT an extension of what the drafter prices -- a
    # PRESERVATION of it. `elemental_ecstasy`'s Block branch was already
    # priced here under `target_has_nonpyro_aura`; C2 renamed the predicate
    # on that one row, and leaving the new name out would have silently
    # un-priced a branch the offer screen has always seen. No other row
    # prints it, so no other price can move, and no dial value moves either:
    # it takes the same Klee conditional share below.
    "target_has_aura",
})


def _static_condition(name: str) -> bool:
    return (
        name in STATIC_STATE_CONDITIONS
        or name.startswith("target_has_power_")
        or name.startswith("exhaust_pile_at_least_")
    )


def _static_condition_share(name: str) -> float:
    if name in ("has_spark", "target_has_nonpyro_aura", "target_has_aura"):
        return STATIC_KLEE_CONDITIONAL_SHARE
    if name == "spotlight_moved_this_turn":
        return STATIC_SPOTLIGHT_MOVED_SHARE
    return 1.0


def _nested_effects(effect_list: list[dict]):
    """Walk every printed branch and mode for card classification only."""
    for fx in effect_list:
        yield fx
        if fx.get("op") == "conditional":
            yield from _nested_effects(fx.get("then", []))
            yield from _nested_effects(fx.get("else", []))
        elif fx.get("op") == "choose_one":
            # EB-118: every classifier downstream of this walk (_has_tempo,
            # _is_applier, behavioural_archetypes, ...) asks "does this card
            # print X anywhere". A mode the player may always take prints X
            # as much as a branch does.
            for mode in fx.get("modes") or ():
                yield from _nested_effects(mode.get("effects") or [])


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
    whose PROPOSED low-slope Fanfare read on `aria_of_recompense` -- the
    STARTER, one copy in every Furina deck before a single card is offered --
    would have closed this limb at run start, forever, for every deck. That
    body was VETOED at the R130 sitting (2026-08-07) and aria is a pure Encore
    card again, so no basic reads the meter today. The exclusion stays anyway,
    on the argument that outlived the card: this limb exists precisely to ask
    whether the DRAFT assembled a plan that cashes the meter, and a limb a
    free card can satisfy answers nothing -- worse, it would feed
    `_core_progress`'s +3.0 core-advance bonus with a constant, pushing the
    drafter off real payoffs by telling it a third of the plan is free.

    The generation and floor limbs are TOTALS over printed amounts, so a
    basic's contribution to those is a real quantity that scales -- only the
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


# R121 (2026-08-06, [USER] verbatim: "let's shield it"). The reference
# anchor's own cards, by OWNERSHIP -- the loader stamps `character` on every
# draftable row of `ironclad_starter.yaml` / `ironclad_package.yaml`
# (`loader.REF_CARD_SHEETS`), and the anchor arm is authored as
# ("ref_ironclad", "generic") in `tier05/exp_roster_anchors.py`.
ANCHOR_TAG_SHIELD_CHARACTER = "ref_ironclad"


def behavioural_archetypes(card: Card) -> list[str]:
    """A card's tags as BEHAVIOUR is allowed to read them.

    R125 (2026-08-07) widened the R121 shield to all four behavioural tag
    readers. EB-46 measured what the narrow shield left open: the smith
    (`model.rest_action`), the event upgrade (`events.py`) and the plan
    bonuses below still read the anchor's instrumentation tags, worth
    +2.17 pp (z = +6.42) on the shipped row against the reproducible
    untagged baseline of 11.13%. Same scoping rule as `_core_advance_view`
    and the same restores-not-redefines argument for the untouched
    DRAFTER_VERSION: the tags landed with R118, after v14 was stamped, so
    blinding behaviour to them returns the scorer to the world v14
    measured. Instruments -- `core_complete`, the RA-G1/RA-G2 columns --
    still read `card.archetypes` directly, which is the whole point of the
    split: the tags exist FOR the instruments."""
    if card.character == ANCHOR_TAG_SHIELD_CHARACTER and card.archetypes:
        return []
    return card.archetypes


def _core_advance_view(cards: list[Card]) -> list[Card]:
    """`cards` as the +3.0 core-advance bonus alone is allowed to see them.

    R121 SHIELD, and this comment states the constraint because the code
    cannot show it: the 10.2 rider (R118) put `archetypes: [generic]` on the
    reference anchor's package so the core-attainment instrument could read
    the arm at all -- it was structurally 0.00% without them. Those tags then
    also reached this scorer, and the anchor's DRAFTING moved with them
    (roster-anchor v14/v6, n=3000 seed 20260729: win 11.13% -> 7.50%,
    z = -4.84). [USER] ruled SHIELD, not accept.

    The blindness is scoped to THE ANCHOR ARM'S TAGS and nowhere else.
    `core_complete` -- the instrument that sets `RunResult.time_to_online`
    and populates the RA-G1/RA-G2 core-attainment columns -- still reads
    them, as do every other term in `score_offer`, `offer_advances_plan` and
    `plan_live`. Scoping is by owning character rather than by the tag value,
    so a future non-anchor card tagged `generic` is untouched.

    WHY the tags lowered the winrate is not answered here and is not this
    shield's to answer: it is minted as `EB-46` in the engineering backlog.
    """
    if not any(c.character == ANCHOR_TAG_SHIELD_CHARACTER and c.archetypes
               for c in cards):
        return cards                       # the common case: nothing copied
    return [replace(c, archetypes=[])
            if c.character == ANCHOR_TAG_SHIELD_CHARACTER and c.archetypes
            else c
            for c in cards]


def is_on_plan_payoff(card: Card, archetype: str) -> bool:
    """Is this card an on-plan PAYOFF for this archetype? The one predicate.

    `role == "payoff" and archetype in c.archetypes` -- the membership rule
    `review/records/payoff-reach-reregistration.md` §6.4 registers, written
    once and shared, so the sprint's two legs cannot classify the same card
    differently. `_generic_core_counts` below is the DECK side (it counts
    instances in a finished deck); `exp_payoff_reach.static_leg` is the STATIC
    side (it counts ids in a reward pool). §6.5's amended `T3` (`M28`, R196)
    fires on a disagreement between those two readings, so a SECOND
    implementation of this rule is the exact fault `T3` exists to detect --
    which is why the amendment prescribes extracting it rather than
    cross-checking two copies.

    Same idiom, same reason as `_generic_core_counts`' own docstring: one
    place, so the call sites cannot drift apart.
    """
    return card.role == "payoff" and archetype in card.archetypes


def _generic_core_counts(deck: list[Card], archetype: str) -> tuple[int, int]:
    """(on-plan enabler+payoff cards, on-plan payoff cards) for one deck.

    One place, so `core_complete` and `_core_progress` cannot drift apart --
    the v10 fanfare fix had to move both limbs for the same reason. The payoff
    half defers to `is_on_plan_payoff` above, which is the same place the
    static leg reads.
    """
    on_plan = [c for c in deck
               if archetype in c.archetypes
               and c.role in ("enabler", "payoff")]
    return len(on_plan), sum(1 for c in on_plan
                             if is_on_plan_payoff(c, archetype))


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
    "conditional", "choose_one", "conscript", "gain_charge", "summon_kurage",
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


#: The Klee overhaul's eight verbs (slice one, QUARANTINED behind
#: `C.KLEE_OVERHAUL`). Named as a set rather than eight `if op ==` arms because
#: they take ONE pricing decision between them -- see `_op_price`.
KLEE_OVERHAUL_OPS = frozenset((
    "set_off", "plant_bomb", "grow_bombs", "merge_bombs",
    "remove_bomb_for_block", "damage_set_off_total", "double_set_off",
    "draw_per_set_off"))

#: The Kokomi overhaul's verbs (DRAFT 6, QUARANTINED behind
#: `C.KOKOMI_OVERHAUL`). A second set beside the one above rather than a merged
#: one, because the two arms are independent and a merged set would make either
#: one's pricing decision look like the other's when the first of them is
#: eventually taken.
KOKOMI_OVERHAUL_OPS = frozenset((
    "mend", "next_companion_discount", "remove_debuff",
    "carry_out_front_plan", "plan_from_exhaust", "damage_quarter_max_hp",
    "plan_twice", "damage_per_companion_last_turn"))


def _op_price(fx: dict, *, prints_damage: Optional[bool] = None) -> float:
    """The DRAFTER_VERSION 13 static price of one effect dict.

    Every rationale is one line in STATIC_OP_PRICING, and
    `tools/lint_op_parity.py` asserts this function and that table between
    them cover the engine's whole OPS registry. All values PROPOSED.

    `prints_damage` is the ONE piece of card context this function takes, and
    exactly one branch (`spend_spark`, EB-233) reads it: whether the card the
    effect belongs to prints an Attack body anywhere. It is keyword-only and
    defaults to None -- "the caller did not say" -- which every branch treats
    as the conservative reading, so a card-less call is unchanged.
    """
    op = fx.get("op")
    if op in _PRICED_INLINE:
        return 0.0
    aoe = (STATIC_AOE_MULT if fx.get("target") == "all_enemies" else 1.0)

    # -- damage- and Block-shaped -----------------------------------------
    if op == "block_next_turn":
        return _neutral_amount(fx, 0) * STATIC_DELAYED_BLOCK_SHARE
    if op == "block_at_turn_start":
        # EB-83, the duration-scoped twin: the same delayed-Block discount,
        # once per turn it is printed to pay. `turns` is a literal positive int
        # by construction (`effects.block_at_turn_start_turns`, enforced at
        # load), so this multiply cannot meet a formula. NO CARD ON ANY SHEET
        # PRINTS THIS OP, so the branch is unreachable and `D` does not move --
        # it exists because `tools/lint_op_parity.py` requires a pricing
        # decision at the moment the author still knows the answer, which is
        # the whole discipline. PROPOSED, like every value in this table.
        return (_neutral_amount(fx, 0) * STATIC_DELAYED_BLOCK_SHARE
                * fx.get("turns", 1))
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
    # -- Kokomi's bank, cost side (R213 E1, QUARANTINED) -------------------
    if op == "spend_charge":
        # `spend_encore`'s shape and `spend_encore`'s reason, one meter over:
        # the GAIN dial with the sign flipped, no new constant. Deliberately
        # NOT `spend_spark`'s shape -- that op earned its own dial (R211)
        # from three converging derivations off measured Spark waste and a
        # measured threshold, and there is no equivalent measurement of what
        # a Charge is worth AT THE MOMENT IT IS SPENT because until this
        # slice no card could spend one.
        #
        # NO DRAFTER_VERSION BUMP, and that is a claim about output rather
        # than an exemption: `spend_charge` lives on the quarantined
        # prototype surface alone, which no pool, digest or drafter can see,
        # so every drafted number in the world is byte-identical with and
        # without this branch. If a spender is ever re-authored onto a real
        # sheet, THAT is the change that moves the drafter and archives the
        # numbers -- see the slice-2 packet.
        return -_neutral_amount(fx, 0) * STATIC_CHARGE_VALUE
    if op == "play_front_memory":
        # ZERO, and a DELIBERATE zero (the Kurage's memory v3, QUARANTINED
        # behind C.KURAGE_MEMORY). The op plays a card the memory already
        # holds, so its whole value is the value of THAT card -- which the
        # drafter priced when it priced the card, and would double-count if
        # it priced it again here. There is also nothing to price against: no
        # sheet row prints this op, no pool or digest can see it, and with the
        # flag off it cannot even fire. `spend_charge`'s argument for not
        # bumping DRAFTER_VERSION applies unchanged: every drafted number in
        # the world is byte-identical with and without this branch. If an
        # acceleration keyword is ever authored onto a real sheet, THAT is the
        # change that moves the drafter and archives the old world.
        return 0.0
    if op == "raise_fanfare_cap":
        return _neutral_amount(fx, 0) * STATIC_FANFARE_CAP_VALUE
    if op == "crash_fanfare":
        return -_neutral_amount(fx, 0) * STATIC_CRASH_FANFARE_VALUE
    if op == "salon_bow":
        return _neutral_amount(fx) * STATIC_SALON_BOW_VALUE
    if op == "salon_perform":
        return _neutral_amount(fx) * STATIC_SALON_PERFORM_VALUE
    if op == "salon_rotate":
        return STATIC_SALON_ROTATE_VALUE
    if op == "spotlight_designate":
        return STATIC_SPOTLIGHT_DESIGNATE_VALUE

    # -- the Klee overhaul, slice one (QUARANTINED, C.KLEE_OVERHAUL) --------
    if op in KLEE_OVERHAUL_OPS:
        # ZERO, and a DELIBERATE zero. The arm is C# FIRST (the slice packet
        # sec.5) -- tier0 registers these eight verbs and REFUSES to resolve
        # them, so there is no sim behaviour for a price to approximate and a
        # guessed number would be a claim about a rule this engine has never
        # run. No `docs/*-cards.yaml` row prints any of them, no pool, digest
        # or stamp can see one, and with `C.KLEE_OVERHAUL` off the rows are
        # unreachable by draft at all -- so every drafted number in the world
        # is byte-identical with and without this branch, and DRAFTER_VERSION
        # does not move. When the slice survives the Prototype gate and the
        # sim arm is built, THAT is the change that prices these and archives
        # the old world.
        return 0.0

    # -- the Kokomi overhaul, slice one (QUARANTINED, C.KOKOMI_OVERHAUL) ----
    if op in KOKOMI_OVERHAUL_OPS:
        # ZERO, and a DELIBERATE zero, on exactly the argument the branch above
        # makes: the arm is C# FIRST (its slice packet sec.5), tier0 registers
        # these ten verbs and REFUSES to resolve them, so there is no sim
        # behaviour for a price to approximate and a guessed number would be a
        # claim about a rule this engine has never run. No `docs/*-cards.yaml`
        # row prints any of them, no pool, digest or stamp can see one, and
        # with `C.KOKOMI_OVERHAUL` off the rows are unreachable by draft at
        # all -- so every drafted number in the world is byte-identical with
        # and without this branch, and DRAFTER_VERSION does not move.
        #
        # `mend` IS IN THAT SET AND IS NOW ALSO REACHABLE FROM THE OTHER ARM
        # (a rewritten Inazuma Universal prints it, and `effects._op_mend`
        # resolves it behind `C.COMPANION_OVERHAUL`), so the "tier0 refuses to
        # resolve it" half of the argument stopped covering it on 2026-09-02.
        # The ZERO stands on the OTHER half, which is the one that decides:
        # only a `proto_` row prints the keyword, no offerable pool the drafter
        # reads can hold one with the flag off, and healing has no priced
        # channel in this table at all -- `heal` itself is `_PRICED_INLINE`.
        # Pricing a bounded heal is acceptance work, and it moves `D` then.
        return 0.0

    # -- the Inazuma companion overhaul (QUARANTINED, C.COMPANION_OVERHAUL) -
    if op == "block_half_damage":
        # ZERO, and a DELIBERATE zero, for a reason NEITHER branch above
        # gives: this op RESOLVES in tier0 -- Gorou's Inuzaka All-Round Defense
        # is played by both engines -- and it really does grant Block. What
        # cannot be priced is the AMOUNT, because it is not on the card: it is
        # half of what the card's own damage line actually landed, which
        # depends on Strength, Weak, an amplifier and the target's Block at
        # resolution time. The three honest options were a guess, the printed
        # damage halved (a guess wearing an argument), and zero; zero is the
        # one that makes no claim. The row is a `proto_` row and no offerable
        # pool holds one with the flag off, so every drafted number in the
        # world is unchanged and DRAFTER_VERSION does not move.
        return 0.0

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
        return fx.get("sparks", 0) * spark_gain_value()     # chosen fodder
    if op == "exhaust_from":
        per = (STATIC_STATUS_EXHAUST_VALUE
               if fx.get("filter") == "status" else STATIC_EXHAUST_VALUE)
        n = fx.get("amount", 1)
        return (1.0 if n == "all" else _neutral_amount(fx)) * per
    if op == "scry_discard":
        return STATIC_SCRY_VALUE
    if op == "recall_to_draw":
        # Source-agnostic on purpose (EB-118); the argument is at the
        # constant, and `fx["from"]` is deliberately not read here.
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
        # `spark_gain_value()`, not the constant: PICK 7 gives the
        # alternative-cost arm its own derived dial and leaves this one at
        # 0.0 for the shipped world. See SPARK_ALT_VALUE.
        return _neutral_amount(fx) * spark_gain_value()
    if op == "spend_spark":
        # A PRINTED COST, PRICED AS ONE -- spend_encore's shape and
        # spend_encore's reason, and since W3 (R211) it has its OWN dial
        # rather than the gain side's with the sign flipped.
        #
        # THE OWED BUMP IS DISCHARGED HERE. This branch used to carry a
        # licence saying DRAFTER_VERSION was not moved because no sheet row
        # printed the op, and naming what would end that: "the first sink
        # card that prints it". `powder_charge` is that row (W3-Klee,
        # R211), so the bump landed with it, unconditionally.
        #
        # THE ASYMMETRY IS DELIBERATE AND IS THE WHOLE DESIGN POSITION: the
        # SPEND side has a real price and the GAIN side (STATIC_SPARK_VALUE)
        # stays at 0.0. R211 kept it there, which is why NO existing row
        # re-prices at this bump -- the archive scope is the three new sink
        # rows and nothing else. See STATIC_SPARK_SPEND_COST for the
        # derivation and for what waking the gain side would reach.
        # `spark_spend_cost()` for the reason on the gain branch above.
        #
        # EB-233: the rate is card-shaped under the flag. `prints_damage` is
        # the caller's read of whether THIS card prints an Attack body; None
        # means the caller could not say, and that keeps the dearer rate.
        return -_neutral_amount(fx) * spark_spend_cost(
            prints_damage=prints_damage)
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
    # EB-233. Read ONCE per card, off the same `all_effects` walk, and handed
    # down to `_op_price` so the `spend_spark` branch can charge a sink at the
    # rate its own body is denominated in. Whole-card context by construction:
    # a nested `damage` still makes the card an Attack body for this purpose.
    has_attack_body = any(fx.get("op") in STATIC_ATTACK_BODY_OPS
                          for fx in all_effects)

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
            elif fx.get("op") == "choose_one":
                # EB-118 sec.5.4. One shipped card carries a `choose_one`:
                # `deep_breath`, the Phase-2C prototype (R192 picked the card,
                # R194 ruled the pair, R205 re-bodied mode 2).
                #
                # THE UNDER-CREDIT IS ACCEPTED, IN WRITING, AT THIS ROW
                # (R194, [USER] 2026-08-23). Deep Breath's mode 1 is the body
                # the card already shipped -- `energy 1` + `gain_encore 2` --
                # and its mode 2 is `spend_encore 3` + `draw 3`. Both `draw`
                # and `energy` are static ZERO here (STATIC_DRAW_VALUE /
                # STATIC_ENERGY_VALUE, the v3 flat-proxy sweep), so mode 2
                # prices at MINUS its own spend and `MAX(modes)` returns mode
                # 1 by construction. Two consequences, both intended:
                #
                #   * The conversion moves NO drafter number. Deep Breath is
                #     priced to the digit as it was before it became modal,
                #     because the mode that wins the max IS the old body.
                #     THE R205 RE-BODY DOES NOT MOVE IT EITHER, and that was
                #     measured rather than assumed: mode 2 goes -0.6000 ->
                #     -0.9000 and the max still returns mode 1's 0.6000, on
                #     both faces. A sheet edit that deepens the LOSING mode is
                #     invisible to a MAX -- which is the same accepted
                #     under-credit read from the other side.
                #   * The card's flexibility -- the whole reason it was
                #     converted -- goes UN-CREDITED. That is a bounded,
                #     one-directional error: the drafter undervalues the
                #     card, never over-values it, and the failure it can
                #     cause is passing on a good card rather than paying for
                #     a bad one.
                #
                # The arbitration leg is therefore NOT exercised by the
                # shipped sheet at all, which is why R194 also owed a
                # SYNTHETIC pin: two nonzero-priced fixture modes, in both
                # orders, in `tier0/tests/test_eb118_modal.py`. Without it the
                # max would first be exercised by a Phase-3 card carrying
                # real stakes.
                #
                # Repricing trigger: the first modal mode whose winning body
                # is priced by a dial that is NOT zero. When `draw` stops
                # being a static zero, this row is re-read against Deep
                # Breath rather than inherited.
                #
                # AGGREGATE = MAX of the modes' generic prices. A conditional
                # blends its branches by a reachability SHARE because the
                # board decides which one fires and the drafter cannot see
                # the board. A modal has no such uncertainty: the PLAYER
                # decides, at play time, with the board in front of them, and
                # every mode is always available. So a share blend would be
                # modelling a coin flip that does not exist.
                #
                # Max is also the conservative choice among the defensible
                # ones. A modal card is worth AT LEAST its best mode -- it
                # dominates a card printing that mode alone -- so max is a
                # lower bound, and the surplus it declines to credit is the
                # optionality itself (the right to decide late), which is
                # real but is exactly what the pilot's mode chooser has to
                # measure before it can be priced. Under-crediting until then
                # keeps the drafter from paying for a mode-valuation whose
                # own weights are still hand-picked
                # (`policy.MODE_OVERDRAW_HP_VALUE`, unswept).
                mode_powers = [effect_power(mode.get("effects") or [])
                               for mode in fx.get("modes") or ()]
                total += max(mode_powers, default=0.0)
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
                  and fx.get("target", "self") == "self"
                  and fx.get("power") == "salon_member"):
                # EB-28 / v18: the salon DEPLOY. `apply_power` is priced
                # inline and no inline branch named this power, so a printed
                # company priced at 0.0 and the members were invisible to
                # every plan but salon -- where the archetype term, not this
                # function, was paying for them.
                #
                # MUST SIT ABOVE the generic self-power branch below: Endless
                # Waltz is `type: power`, so that branch would otherwise
                # swallow the whole card at STATIC_POWER_ENGINE_VALUE (0.0)
                # and the deploy would stay invisible on the one row where
                # the drafter most needs to see it.
                #
                # MEMBER-AGNOSTIC by construction. The printed `member:` key
                # names a type (or `random`), and the three types are worth
                # different amounts, but which one is worth MORE depends on
                # what is already on stage -- occupancy an offer screen
                # cannot read. One flat dial, one number, at the floor of the
                # band; the derivation is at the constant.
                total += _neutral_amount(fx) * STATIC_SALON_MEMBER_VALUE
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
                total += _op_price(fx, prints_damage=has_attack_body)
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
    # EB-118, the same placement one line down and the opposite sign: a
    # keyword that decides whether the printed effects resolve at all scales
    # the whole card. Reads `is_ethereal`, so both spellings price the same.
    #
    # THE NO-BUMP LICENCE IS SPENT (EB-118 Phase 2B). The note this replaces
    # said the PROPOSED DRAFTER_VERSION bump was not taken because the term
    # was provably inert -- no committed sheet row printed `ethereal:`, and
    # the only cards the tag spelling reached were Statuses, Curses and the
    # Spotlight token, whose rarities sit outside RARITY_ODDS. It named the
    # row that would end that: "Phase 2's big_badda_boom". That row is now in
    # docs/klee-cards.yaml. A Common Klee attack is offerable by every reward,
    # shop and Neow channel, so this multiplier now moves a drafted price and
    # the bump was OWED, not proposed.
    # IT IS TAKEN: `DRAFTER_VERSION` 15 -> 16 at the Phase-2 integration
    # window, 2026-08-24, with the re-baseline in the same window
    # (`review/records/sitting-reads-2026-08-24-c13-d16.md`). The integer was
    # written at integration and not before, which is what packet §3 asks for;
    # the price it moved is `big_badda_boom` 8.0000 -> 4.8000, and the R193
    # read of that number is at the constant above.
    if card.is_ethereal:
        total *= STATIC_ETHEREAL_SHARE
    # `if card.sly` first: this is the draft hot path and the overwhelming
    # majority of cards have an empty list, so the comprehension inside
    # `sly_riders` should not allocate for them.
    riders = sly_riders(card) if card.sly else []
    if riders:
        # v7: a Sly rider is the same printed grammar at half face -- it
        # fires only when a card effect discards this from hand, and the
        # drafter cannot see outlet density at offer time.
        #
        # EB-71 (R174): `sly_riders` drops the base-game `sly_autoplay`
        # marker, which the unification moved onto this same field. The
        # marker is worth EXACTLY ZERO here, which is the price the keyword
        # already carried (it lived on a boolean this function never read) --
        # the unification is stamp-free and may not move a drafted number.
        # Pricing the base-game Sly rider is a real question and a separate,
        # [USER]-owned one: a change to the priced-op set is a
        # DRAFTER_VERSION bump.
        total += effect_power(riders) * STATIC_SLY_SHARE
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
# Values are the round-2 sweep winner (docs/archive/silent-pilot-review-2026-07-27.md
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
# 1000 paired-seed runs -- docs/archive/silent-pilot-review-2026-07-27.md s6):
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
STATIC_SALON_MEMBER_VALUE = 1.5    # per member DEPLOYED by a printed
                                   # `apply_power power: salon_member`
                                   # (EB-28, DRAFTER_VERSION 18). Until this
                                   # dial existed a deploy priced at exactly
                                   # ZERO: `apply_power` is priced inline and
                                   # no inline branch named the power, so
                                   # CROSS-PLAN -- a Furina drafting anything
                                   # but salon -- the whole company was
                                   # invisible. The archetype term paid for
                                   # these rows inside the salon plan and
                                   # nothing paid for them outside it.
                                   #
                                   # DERIVED, NOT PICKED. Three routes; the
                                   # band is 1.5 to 4.0 and this is its
                                   # CONSERVATIVE end, which for a VALUE
                                   # (unlike D17's cost) is the BOTTOM.
                                   #   (1) PERFORM PARITY, the in-family
                                   #   floor. `salon_perform` prices exactly
                                   #   one member tick, on demand, at 1.5. A
                                   #   deploy delivers AT LEAST that -- the
                                   #   member ticks at the start of the next
                                   #   player turn. -> 1.5.
                                   #   (2) TICK PLUS EVENTUAL BOW, the
                                   #   in-family full-member read. The
                                   #   perform dial's own note calls a tick
                                   #   "the smaller half of a member", and
                                   #   FIFO displacement at
                                   #   SALON_MEMBER_SLOTS = 3 means a member
                                   #   that stands long enough is bowed out
                                   #   at STATIC_SALON_BOW_VALUE. 1.5 + 2.0
                                   #   -> 3.5.
                                   #   (3) KURAGE PARITY, the cross-family
                                   #   ceiling. The repo's other persistent
                                   #   per-turn engine credits ONE pulse at
                                   #   FACE value -- (KURAGE_PULSE_BASE +
                                   #   KURAGE_PULSE_BLOCK) *
                                   #   STATIC_PERSISTENT_PROC_SHARE = 4.0. A
                                   #   salon tick's face, averaged over the
                                   #   three types a deploy can land
                                   #   (crabaletta 6 damage, usher 3 Block,
                                   #   chevalmarin 2 damage + one hydro aura
                                   #   at STATIC_AURA_VALUE), is 4.33, less
                                   #   the tick's 1-Encore upkeep at
                                   #   STATIC_ENCORE_VALUE -> 4.03.
                                   # (2) and (3) converge on 3.5-4.0 from
                                   # opposite directions and (1) is the hard
                                   # floor. THE FLOOR IS TAKEN, and the gap
                                   # is named rather than hidden: everything
                                   # above one tick -- the repeat ticks, the
                                   # eventual bow, the Fanfare Focus scaling
                                   # -- is stage occupancy and combat length,
                                   # which is exactly what an offer screen
                                   # cannot see. That is
                                   # STATIC_SALON_ROTATE_VALUE's own argument
                                   # applied to a value it CAN at least
                                   # bound. The residual error under-credits
                                   # the member and never over-credits it, so
                                   # the failure it can cause is passing on a
                                   # good card rather than paying for a bad
                                   # one (R194's direction rule).
                                   #
                                   # NOT CAPPED AT SALON_MEMBER_SLOTS. A
                                   # fourth deploy bows the oldest member out
                                   # rather than fizzling, so it still pays;
                                   # capping would mean reading stage
                                   # occupancy, which is the thing this
                                   # family of dials refuses to do.
                                   #
                                   # [USER]-OVERRIDABLE, and this is the one
                                   # constant to move: 3.5 (route 2) is the
                                   # defensible larger number in the same
                                   # method, and the argument for it is that
                                   # a member is strictly better than one
                                   # on-demand perform. Moving it re-prices
                                   # the NINE rows archived at D18 and
                                   # nothing else.
STATIC_SALON_BOW_VALUE = 2.0       # salon_bow: one member's bow, on demand.
                                   # Priced at one conservative bow rather
                                   # than at the stage it implies -- the
                                   # drafter cannot see stage occupancy, and
                                   # the plan bonus already pays for the
                                   # Salon shape.
# EB-118 §5.5 (staged 2026-08-23). BOTH VALUES BELOW ARE PROPOSED, and
# neither moves a number today: no sheet row prints either op, so every
# drafting arm scores exactly as it did before. DRAFTER_VERSION therefore
# does NOT move -- an unused op cannot change an offer screen, and the pin at
# 14 (R121's payoff-reach registration) is untouched. The first card that
# prints one of these verbs is what makes these dials load-bearing, and the
# bump belongs to that window, not this one.
STATIC_SALON_PERFORM_VALUE = 1.5   # salon_perform: one extra member tick, on
                                   # demand. Priced BELOW salon_bow because
                                   # a tick is the smaller half of a member
                                   # (Crabaletta 6 against 14) and because
                                   # the tick pays its Encore upkeep, which
                                   # the bow does not -- the drafter cannot
                                   # see whether the meter can afford it, so
                                   # the conservative read is the priced one.
STATIC_SALON_ROTATE_VALUE = 0.0    # salon_rotate: ZERO, and structurally so
                                   # rather than pending a number. Rotating
                                   # delivers nothing by itself; its whole
                                   # value is which member the NEXT bow,
                                   # perform or displacement finds, and stage
                                   # occupancy is exactly what an offer
                                   # screen cannot see (the salon_bow note
                                   # above says the same thing about a value
                                   # it could at least bound). Priced at zero
                                   # deliberately, not by omission -- the
                                   # STATIC_STRIP_BLOCK_VALUE precedent.
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
                                   # PROPOSED (EB-118, staged): the exhaust
                                   # SOURCE prices at this same rate and gets
                                   # no hook of its own. The offer-time
                                   # question is unchanged -- one chosen card
                                   # lands on top of the draw pile -- and the
                                   # two ways the sources differ point in
                                   # opposite directions: the exhaust pile is
                                   # a strictly smaller (often empty)
                                   # reservoir, and what it returns is on
                                   # LOAN, gaining Exhaust and leaving again
                                   # after one use. A split rate would be a
                                   # number nothing has measured, and
                                   # DRAFTER_VERSION does not move for a
                                   # staged capability no shipped card uses.
                                   # test_eb118_recall_exhaust pins that the
                                   # generic price applies to both sources.
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
STATIC_ETHEREAL_SHARE = 0.6        # EB-118. Ethereal is a DOWNSIDE and the
                                   # drafter must price it, or a card whose
                                   # whole design is "strong, but it dies in
                                   # your hand" scores as if the second half
                                   # were not printed. A card-level LIFECYCLE
                                   # discount, not an op price: the keyword
                                   # touches no effect, it decides whether the
                                   # effects ever resolve at all -- so it
                                   # scales what the card printed rather than
                                   # sitting as a term beside it, the same
                                   # placement STATIC_REPEAT_SHARE takes
                                   # below and for the mirror-image reason.
                                   # 0.6 is a JUDGEMENT, not a sweep: an
                                   # Ethereal card is lost outright on the
                                   # draws where its cost cannot be paid the
                                   # turn it arrives, and at the drafter's
                                   # ~3-energy turn that is a large minority
                                   # of them. It is deliberately not harsher:
                                   # the keyword costs nothing on the draws
                                   # where the card IS played, which is the
                                   # majority, and the sheet buys the whole
                                   # downside off at the campfire.
                                   #
                                   # ===== RATIFIED (R205, 2026-08-24) =====
                                   # 0.6 IS A SETTLED NUMBER. It did not become
                                   # one by default: R193 armed a trigger with
                                   # the constant, the trigger fired, the read
                                   # was taken, and the ruling was made on the
                                   # read. The arithmetic is recorded here
                                   # rather than in a report nobody reaching
                                   # this constant would open.
                                   # THE READ, taken 2026-08-24 at the `D16`
                                   # integration bump: `big_badda_boom` is the
                                   # pool's FIRST DRAFTABLE CARRIER of the
                                   # keyword and prices its whole upgrade on
                                   # this share, so a read of that card is a
                                   # read of this number and of nothing else.
                                   # `draft._static_power`, both faces of
                                   # `big_badda_boom` as they ship on `main`:
                                   #
                                   #   base face      4.8000
                                   #   upgraded face  8.0000
                                   #   base with the keyword cleared  8.0000
                                   #   ratio base:upgraded  0.600000
                                   #
                                   # so the share's whole contribution is
                                   # -3.2000 on the base face and exactly zero
                                   # on the upgraded one (the upgrade removes
                                   # the keyword), and the ratio the trigger
                                   # reads IS this constant to six places --
                                   # 4.8 and 8.0 are the two figures R193
                                   # predicted, unchanged by R201's Option A
                                   # body (its rider rides BOTH faces, so the
                                   # base-to-upgraded delta is still exactly
                                   # the keyword and the read stays
                                   # one-variable).
                                   # THE ONE-VARIABLE CLAIM CHECKED RATHER
                                   # THAN ASSUMED: the Option A rider prices at
                                   # 4.8000 -> 4.8000 base and 8.0000 ->
                                   # 8.0000 upgraded against the same rows with
                                   # the `conditional` stripped, so it
                                   # contributes zero to both sides and moves
                                   # neither end of the ratio.
                                   # WHAT THE READ SAYS ABOUT THE NUMBER, as
                                   # far as arithmetic can say anything: the
                                   # base face ranks 17th of the 29 Klee
                                   # draftable Commons at 0.6, and that rank is
                                   # a PLATEAU rather than a knife edge --
                                   # rank 17 holds for every share in
                                   # [0.5625, 0.6250] (below 0.5625 the price
                                   # drops under `bomb_voyage`'s 4.5; above
                                   # 0.6250 it clears the four-way tie at 5.0
                                   # and the card jumps to 13th). 0.6 sits
                                   # near the middle of that plateau, so the
                                   # shipped value is not load-bearing to the
                                   # third digit and a small move would change
                                   # no offer ranking at all.
                                   # WHAT IT DOES NOT SAY, and this is the
                                   # limit of the mechanical half: the note's
                                   # own rationale for 0.6 is a claim about
                                   # the FREQUENCY of a lost draw ("lost
                                   # outright on the draws where its cost
                                   # cannot be paid the turn it arrives"), and
                                   # nothing in either engine counts that
                                   # today -- no per-card Ethereal-loss
                                   # telemetry exists, so the frequency cannot
                                   # be read off a run. Building it is a
                                   # build, not a read.
                                   # THE RULE THE RATIFICATION ADOPTS: no
                                   # decision unless a RE-DERIVATION DISAGREES
                                   # with 0.6. None is derivable today -- the
                                   # frequency is uninstrumented, per the
                                   # paragraph above -- and the plateau says
                                   # the third digit is not load-bearing, so
                                   # there is nothing for a decision to be
                                   # about. R193's obligation is discharged in
                                   # both halves, READ and RULING, and QUEUE
                                   # `M41` is closed.
                                   # WHAT WOULD REOPEN IT: a re-derivation that
                                   # DISAGREES -- which means building the
                                   # per-card Ethereal-loss telemetry first,
                                   # deliberately, not as a side effect of some
                                   # other instrument. A move is still its own
                                   # `DRAFTER_VERSION` bump with its own
                                   # re-baseline, and every drafted number in
                                   # the tree archives with it.
                                   # ===========================================
STATIC_REPEAT_SHARE = 0.5          # repeat_this multiplies the card's OWN
                                   # printed effects. Applied at half,
                                   # because every printed use of the op
                                   # sits behind a condition.
# -- the measured dead dials (see the header above) ------------------------
STATIC_DRAW_VALUE = 0.0            # draw, draw_while, draw_to_hand_size
STATIC_ENERGY_VALUE = 0.0          # energy, and cost_mod through it
STATIC_SPARK_VALUE = 0.0           # gain_spark, discard_for_sparks. STAYS
                                   # DEAD, and that is a design position
                                   # rather than an oversight: R211 kept the
                                   # GAIN side at zero while giving the SPEND
                                   # side a real price (STATIC_SPARK_SPEND_COST
                                   # below). An undocumented asymmetry reads as
                                   # a bug to the next person, so: waking this
                                   # dial would re-price TWELVE shipped rows --
                                   # all_my_treasures, cant_catch_me, crackle,
                                   # da_da_da, hot_hands, skip_and_hop, snap,
                                   # spark_collection, sparkly_treasure,
                                   # sugar_rush, warm_glow, and prune_witch_hunt
                                   # in docs/mondstadt-companions.yaml -- and for
                                   # four of those (sparkly_treasure,
                                   # spark_collection, hot_hands, sugar_rush,
                                   # all at 0.0000 today) it would be a
                                   # VISIBILITY FLIP rather than a re-price.
                                   # None of that happens while this is 0.0.
STATIC_BURST_VALUE = 0.0           # burst_energy
# -- Klee's Spark price (W3, EB-118 Phase 3, R211) --------------------------
# THE COST-SIDE DIAL, on STATIC_CRASH_FANFARE_VALUE's idiom: the sign lives in
# `_op_price`'s branch, the magnitude lives here, and the reason lives beside
# the magnitude.
#
# THE UNIT IS THE FILE'S OWN: "values are expressed in the same rough units as
# one point of printed damage or Block" (the v3 header). So the question this
# number answers is not "what is a Spark worth" in the abstract -- it is how
# many points of printed damage-or-Block one Spark is worth AT THE MOMENT IT IS
# SPENT. A printed `spend_spark: 2` therefore costs a card 5.00.
#
# DERIVED, NOT PICKED -- three routes, two of which converge from opposite
# directions on the same number (the derivation and its full sensitivity table
# publish in the W3 packet; the load-bearing lines are these):
#   (1) USE-VALUE. Sparks buy free Attacks. The value of a free Attack is the
#       ENERGY it refunds, not the Attack's printed power -- you would have
#       played that card anyway. Klee's pool's MEDIAN price-per-energy is 5.00
#       (median 5.00 whether or not the ten zero-priced Powers are in the
#       sample, which is what makes it the number to use), and 2 Sparks is one
#       free Attack under True Spark Knight (`combat.spark_threshold` drops
#       SPARKS_FOR_FREE_ATTACK to 2). 5.00 / 2 -> 2.50.
#   (2) ACQUISITION, AT THE MATCHED QUANTITY. `spark_collection` gives up its
#       whole slot to buy exactly TWO Sparks, at Common cost 1 Skill, whose
#       non-Spark slot median is 5.00. 5.00 / 2 -> 2.50. The sheet's own price
#       for a purchase of two, applied to a spend of two, needs no bridging
#       assumption at all. (The whole purchase ladder is a coherent bulk
#       discount -- sparkly_treasure 4.00, spark_collection 2.50, hot_hands
#       1.67 -- and its median is also 2.50.)
#   (3) THE SINKS' OWN PRINTED EXCHANGE RATES pull DOWN, to 1.0-1.7, and
#       powder_charge is written as if a Spark were worth less than nothing.
#       That is not a defect in the derivation: a sink is SUPPOSED to be a
#       slightly bad deal in raw output, because what it really buys is a USE
#       for a bank that would otherwise sit there -- which the drafter cannot
#       see, and which is exactly why the residual error must under-value.
#
# R194's DIRECTION RULE PICKS THE TOP OF THE CONVERGENT RANGE. Every
# one-directional error already in this file makes the drafter PASS ON A GOOD
# CARD, never PAY FOR A COST IT CANNOT SEE. This is the drafter's first cost
# term of that kind, so 2.5 deliberately OVER-charges the sink by up to ~30%:
# two discounts that would lower it are declined on direction grounds -- the
# waste discount (12-30% of Sparks gained are never converted, giving 2.19 or
# 1.75) and the measured-threshold discount (both weighted arms actually run at
# threshold 3, giving 1.67).
#
# WHAT IT DOES, and it is disclosed rather than buried: every sink loses
# 2 x dial on both faces. powder_charge 7.00/10.00 -> 2.00/5.00,
# hold_the_line 5.00/8.00 -> 0.00/3.00, smoke_and_sparks 6.00/8.00 ->
# 1.00/3.00. In a `spark` draft all three stay above DRAFT_SKIP_THRESHOLD; in a
# `demolition` draft hold_the_line scores 0.00, BELOW it, because it is tagged
# [spark] only and was already weak there. [USER] holds the value: 1.5 is the
# defensible smaller number in the same method (between the threshold-3 read
# and the sinks' own rates) if that offer-screen effect is not wanted.
STATIC_SPARK_SPEND_COST = 2.5      # spend_spark, per Spark. NOT the gain
                                   # dial's mirror -- see above.

# =============================================================================
# PICK 7, ANSWERED THE WAY THE SEAT RULED IT: "3, derive it from the new sink
# prices once sec.4's numbers are ruled". They are now set, so it is derived.
#
# DERIVED, NOT PICKED (R212's ladder: one-way error direction, archive scope
# bounded by the flag, ONE constant). NEITHER SHIPPED DIAL MOVES BY ONE BYTE.
# `STATIC_SPARK_VALUE` (0.0) and `STATIC_SPARK_SPEND_COST` (2.5) are both
# [USER]-held, and both were derived against a rule that does not run under
# `C.SPARK_ALT_COST_ENABLED` -- 2.5's own route (1) reads "2 Sparks is one
# free Attack under True Spark Knight", a sentence with no referent once the
# threshold is retired. So the flag gets ONE number of its own and the
# shipped world keeps both of its own.
#
# WHY ONE NUMBER FOR BOTH SIDES. R211 gave the gain side 0.0 and the spend
# side 2.5 because a Spark only fed a discount: the gain was invisible value,
# the spend a real price. Under an alternative-cost economy a Spark is worth
# exactly what it buys and it is bought for exactly what it is worth, so gain
# and spend are the SAME number in the same unit, and printing two would be
# asserting an asymmetry the new rule does not have.
#
# THE ARITHMETIC, in the file's own unit ("the same rough units as one point
# of printed damage or Block", the v3 header). For each of the five sinks
# PICK 3/4 sets: what does the Spark price buy OVER a 0-energy neighbour of
# the same rarity? Every one of these five is 0 energy, so the energy line
# cancels out and the whole delta is the Sparks.
#
#   The 0-energy baselines, off the shipped sheet and not invented here:
#     Common 0E Attack   -- `crackle` 3 damage, `study_of_explosions` 4
#                           damage: baseline 3.5.
#     Uncommon 0E Attack -- `flame_on_the_wick` 6 damage: baseline 6.0.
#   AoE bodies count `STATIC_AOE_MULT` = 2.0 enemies, which is this file's
#   own convention (`_static_power`, v6) and not a new assumption.
#
#     Fwoosh!          8            - 3.5 = 4.5 over 1 Spark  -> 4.50
#     Tinder Toss      4 x 2.0 = 8  - 3.5 = 4.5 over 1 Spark  -> 4.50
#     Bang Bang!       5 x 2  = 10  - 3.5 = 6.5 over 2 Sparks -> 3.25
#     Dodoco Blast     7 x 2.0 = 14 - 6.0 = 8.0 over 2 Sparks -> 4.00
#     Firework Finale  18          - 6.0 = 12.0 over 3 Sparks -> 4.00
#
#   MEDIAN of {4.50, 4.50, 3.25, 4.00, 4.00} = 4.00.
#
# THE MEDIAN, NOT THE MEAN, for the reason the 2.5 derivation gave: a median
# is what makes an outlier row (Bang Bang!'s deliberately poor rate, which is
# what the sheet charges for a two-Spark purchase) fail to move the dial.
# Firework Finale's Exhaust is NOT discounted here -- discounting it would
# lower the number, and a LOWER number is the unsafe direction on the spend
# side. Left undiscounted and named.
#
# THE ERROR DIRECTION, and it is one-way on both sides at 4.00 because the
# two sides want opposite things and the median sits between them: on the
# GAIN side 4.00 is the first non-zero price a `gain_spark` has ever had, so
# the drafter can finally see a generator at all (0.0 made twelve shipped
# rows invisible); on the SPEND side 4.00 is 1.6x the shipped 2.5, so a sink
# is charged MORE, never less, which is the direction that cannot make the
# drafter pay for a cost it cannot see.
#
# WHAT IT DOES: under the flag every `gain_spark` row gains
# `amount x 4.00` and every `spend_spark` row loses `amount x 4.00`. Flag
# off, nothing reads this and both shipped dials stand.
SPARK_ALT_VALUE = 4.0              # derived above. ONE dial, both sides.

# =============================================================================
# EB-233. THE SPEND SIDE IS TWO RATES, NOT ONE, AND NO NEW NUMBER IS MINTED.
#
# THE DEFECT, in the derivation printed immediately above rather than in a
# measurement. Every one of the five rows whose median is `SPARK_ALT_VALUE`
# -- Fwoosh!, Tinder Toss, Bang Bang!, Dodoco Blast, Firework Finale -- prints
# `damage`, and every baseline it is netted against ("Common 0E Attack ...
# 3.5", "Uncommon 0E Attack ... 6.0") is an Attack. 4.00 is therefore the
# price of a Spark SPENT ON DAMAGE, stated in the one unit the file prices at
# face value. It has NO REFERENT on a sink that prints no Attack body: such a
# card's whole worth is carried by ops the file prices at a SHARE or a proxy
# (Block, `detonate` at STATIC_DETONATE_VALUE, a debuff at
# STATIC_DEBUFF_VALUE), which the 4.00 median never saw. Charged 4.00 anyway,
# every non-damage sink under the flag scores NEGATIVE before the offer screen
# is reached -- Set It Off -1.00, Powder Smoke -2.00, Dig In -3.00 -- so the
# drafter cannot take one at any bank, from any deck, on any seed. That is a
# SCORER fact, and it is what makes a share of drafted decks holding one an
# OFFER number rather than a bank number.
#
# THE FIX IS THE FILE'S OTHER ALREADY-DERIVED PER-SPARK PRICE, USED WHOLE.
# `STATIC_SPARK_SPEND_COST` = 2.50 is the only per-Spark spend price this
# repository has derived WITHOUT a damage row anywhere in it: its route (1) is
# the ENERGY a free Attack refunds (Klee's pool's median price-per-energy
# 5.00, over the 2 Sparks that buy one) and its route (2) is
# `spark_collection`'s slot price for a purchase of exactly two (5.00 over 2).
# Both are slot-and-energy arithmetic, which is precisely the unit a sink that
# prints no damage trades in. So: a sink that prints an Attack body pays the
# damage-derived rate; a sink that prints none pays the slot-derived rate.
# NOTHING IS PICKED HERE -- both numbers were derived before this row existed,
# and this dial only routes between them.
#
# ERROR DIRECTION, ONE-WAY (R194, and R212's ladder clause). 2.50 < 4.00, so
# this can only ever charge a non-damage sink LESS. It cannot charge one less
# than the SHIPPED world already does, because 2.50 *is* the shipped charge:
# `STATIC_SPARK_SPEND_COST`'s own disclosure publishes these three rows at it
# -- powder_charge 2.00, hold_the_line 0.00, smoke_and_sparks 1.00 -- and
# those are the numbers this branch reproduces under the flag. R194's rule is
# that the drafter must pass on a good card rather than pay for a cost it
# cannot see; today it pays 4.00 a Spark for a purchase it can see NO value in
# at all, which is the failure the rule exists to forbid.
#
# ARCHIVE SCOPE, bounded twice. `C.SPARK_ALT_COST_ENABLED` ships FALSE, so no
# shipped drafted number moves by one byte and DRAFTER_VERSION is NOT bumped
# -- the same licence, on the same flag, that `SPARK_ALT_VALUE` landed under.
# Under the flag the scope is sink rows printing no Attack body: the three
# `EB-218` twins and Rummage. The six damage sinks are untouched.
#
# WHAT "PRINTS DAMAGE" MEANS, named so it cannot drift: a `damage` or
# `chain_attack` op anywhere in the card's printed branches and modes. Those
# are the only two ops STATIC_OP_PRICING prices at FACE VALUE damage, so they
# are exactly the rows the 4.00 median is denominated in. `place_bomb` and
# `detonate` are deliberately NOT counted -- both are priced at a share, not
# at face value, which is the whole distinction this dial turns on.
SPARK_ALT_NONDAMAGE_SPEND_COST = STATIC_SPARK_SPEND_COST   # 2.50, see above.


def spark_gain_value() -> float:
    """The per-Spark GAIN dial in force. `SPARK_ALT_VALUE` under the flag."""
    return SPARK_ALT_VALUE if C.SPARK_ALT_COST_ENABLED else STATIC_SPARK_VALUE


def spark_spend_cost(*, prints_damage: Optional[bool] = None) -> float:
    """The per-Spark SPEND dial in force, for a card of this shape.

    Flag off: `STATIC_SPARK_SPEND_COST`, whatever the card prints -- the
    shipped world has one rate and EB-233 does not give it a second.

    Flag on: `SPARK_ALT_VALUE` for a card that prints an Attack body, and
    `SPARK_ALT_NONDAMAGE_SPEND_COST` for one that does not. `prints_damage`
    is None when the caller has no card in hand; that keeps the dearer rate,
    so an un-informed call can never under-charge a sink.
    """
    if not C.SPARK_ALT_COST_ENABLED:
        return STATIC_SPARK_SPEND_COST
    return (SPARK_ALT_NONDAMAGE_SPEND_COST if prints_damage is False
            else SPARK_ALT_VALUE)


#: The ops STATIC_OP_PRICING prices at FACE VALUE printed damage, and so the
#: ops `SPARK_ALT_VALUE`'s median is denominated in. See EB-233 above.
STATIC_ATTACK_BODY_OPS = frozenset({"damage", "chain_attack"})


def prints_attack_body(card: Card) -> bool:
    """EB-233: does this card print an Attack body anywhere?

    Reads every printed branch and mode (`_nested_effects`), on the same
    "does this card print X anywhere" rule every other classifier in this
    file uses. `_static_power` inlines the identical test over the walk it
    already holds; a test pins the two to agree.
    """
    return any(fx.get("op") in STATIC_ATTACK_BODY_OPS
               for fx in _nested_effects(card.effects))


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
    "choose_one": "MAX of the modes -- the player picks, so no share blend; "
                  "deep_breath's mode-2 under-credit ACCEPTED at the row "
                  "(R194) and its price is unmoved by the conversion",
    "conscript": "STATIC_CONSCRIPT_VALUE per recruit (v7)",
    "gain_charge": "STATIC_CHARGE_VALUE per printed point (v7)",
    "spend_charge": "the same rate, NEGATIVE: a printed cost (R213 E1, "
                    "prototype surface only -- no shipped row prints it and "
                    "no drafted number moves)",
    "summon_kurage": "ONE pulse, not the duration (v8)",
    "play_front_memory": "ZERO: the memory's own card carries the value and "
                         "was priced once already (Kurage memory v3, "
                         "prototype surface only -- no shipped row prints it "
                         "and no drafted number moves)",
    "gain_fanfare_floor": "STATIC_FANFARE_FLOOR_VALUE per point (v9)",
    "grow_damage": "one discounted future redraw",
    # --- the Klee overhaul, slice one (QUARANTINED, C.KLEE_OVERHAUL) ------
    # One rationale, eight ops, because it is ONE decision: the arm is C#
    # first, tier0 refuses to resolve any of them, and a price is an estimate
    # of behaviour that does not exist here yet. See `_op_price`.
    **{op: "ZERO: the KLEE_OVERHAUL arm is C# FIRST and tier0 refuses to "
            "resolve it, so there is no sim behaviour to price (slice packet "
            "sec.5; prototype surface only -- no shipped row prints it and no "
            "drafted number moves)"
       for op in ("set_off", "plant_bomb", "grow_bombs", "merge_bombs",
                  "remove_bomb_for_block", "damage_set_off_total",
                  "double_set_off", "draw_per_set_off")},
    # --- the Kokomi overhaul, slice one (QUARANTINED, C.KOKOMI_OVERHAUL) --
    # One rationale, ten ops, and the same one decision for the same reason.
    **{op: "ZERO: the KOKOMI_OVERHAUL arm is C# FIRST and tier0 refuses to "
            "resolve it, so there is no sim behaviour to price (slice packet "
            "sec.5; prototype surface only -- no shipped row prints it and no "
            "drafted number moves)"
       for op in ("next_companion_discount", "remove_debuff",
                  "carry_out_front_plan", "plan_from_exhaust",
                  "damage_quarter_max_hp", "plan_twice",
                  "damage_per_companion_last_turn")},
    # `mend` OUT OF THAT BULK, because half of its rationale stopped being
    # true: it is the one Kokomi verb a rewritten Inazuma UNIVERSAL prints, so
    # tier0 does resolve it behind `C.COMPANION_OVERHAUL`.
    "mend": "ZERO: healing has no priced channel in this table at all "
            "(`heal` is _PRICED_INLINE), and only a `proto_` row prints the "
            "keyword -- no offerable pool holds one with the flag off, so no "
            "drafted number moves",
    # --- the Inazuma companion overhaul (QUARANTINED, C.COMPANION_OVERHAUL) -
    "block_half_damage": "ZERO: the amount is half of what the card's own "
                         "damage line LANDED, which no static pricer can see "
                         "(prototype surface only -- no shipped row prints it "
                         "and no drafted number moves)",
    # --- damage/Block-shaped, new in v13 ---------------------------------
    "block_next_turn": "printed Block at STATIC_DELAYED_BLOCK_SHARE",
    "block_at_turn_start": "printed Block at STATIC_DELAYED_BLOCK_SHARE, once "
                           "per printed turn (EB-83; no sheet prints it)",
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
    "salon_perform": "STATIC_SALON_PERFORM_VALUE per act performed "
                     "(PROPOSED; no sheet row prints it, so no number moves)",
    "salon_rotate": "ZERO: STATIC_SALON_ROTATE_VALUE, a stage-occupancy "
                    "question an offer screen cannot see",
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
    "recall_to_draw": "STATIC_RECALL_VALUE per chosen card recalled, "
                      "source-agnostic (EB-118: `from: exhaust` prices the "
                      "same, PROPOSED at the constant)",
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
    "spend_spark": "NEGATIVE STATIC_SPARK_SPEND_COST, its own live dial: a "
                   "Spark price is a printed cost (W3/R211; the gain side "
                   "stays dead on purpose). Under SPARK_ALT_COST_ENABLED the "
                   "rate is card-shaped (EB-233): SPARK_ALT_VALUE for a sink "
                   "printing an Attack body, SPARK_ALT_NONDAMAGE_SPEND_COST "
                   "for one that does not, because the 4.00 median is "
                   "denominated in damage rows only",
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
    # R121 SHIELD: this bonus, and ONLY this bonus, reads the deck through
    # `_core_advance_view` -- the anchor arm's instrumentation tags are
    # invisible here. `progress` above is the unshielded number and stays
    # that way: every other term below (the enabler decay, the payoff gate,
    # the skip threshold) is outside the ruling's scope.
    blind = _core_advance_view(deck)
    blind_progress = progress if blind is deck else _core_progress(blind,
                                                                   archetype)
    if _core_progress(_core_advance_view(deck + [card]),
                      archetype) > blind_progress:
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
            and "fanfare" in behavioural_archetypes(card)
            and not card.is_companion):
        s += _fanfare_plan_score(card, deck, online)
    elif (archetype in behavioural_archetypes(card)
          and not card.is_companion):
        if card.role == "enabler":
            s += 3.0 * max(0.25, 1.0 - progress) * plan_mult
        elif card.role == "payoff":
            if archetype == "reaction" and _is_amp_payoff(card):
                s += 4.0 if online else REACTION_AMP_OFFLINE
            else:
                s += (4.0 if online else 1.0) * plan_mult
        else:
            s += 1.5 * plan_mult
    elif "generic" in behavioural_archetypes(card):
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
#
# POLICY_VERSION 4 (R124, 2026-08-07). EB-31p: the pilot's Spotlight
# valuation (`tier0/pilot/policy.py _spotlight_value`) now reads the
# both-modes flag the four engine readers use -- under The Curtain Never
# Falls, designates score dead, Guest Cast reads live, and
# copy_spotlighted_in_hand sees its targets. Latent at the bump: the relic
# only arrives through the Ancient pick, whose Orobas weights land in the
# same window (R125, EB-31q) -- Furina cells move when that does. No other
# character reads any of the three branches.
#
# POLICY_VERSION 5 (EB-24p, 2026-08-07). `policy._active_effects` reads
# `reaction_triggered_this_turn` (the Chevreuse window) -- an unlisted
# predicate skips the WHOLE conditional, both branches, so
# `audience_participation`'s unconditional else-glue scored ~0 and the card
# measured drawn 974 / played 0. Turn-level counter, known exactly at score
# time; `reaction_triggered_by_this` stays excluded (mid-resolution).
#
# POLICY_VERSION 6 (EB-29t, 2026-08-07). The promoted Test Subject reads
# (R128): Skills are taxed by living enemies' Enrage (each play grants
# permanent Strength; priced over ENRAGE_TAX_TURNS future attack turns),
# and per-hit damage into an Intangible target prices the
# INTANGIBLE_DAMAGE_CAP it will actually deal. Both are universal
# board-state reads, live for every pilot; only cells whose encounters
# carry those powers move (act-3 test_subject).
#
# POLICY_VERSION 7 (R176, 2026-08-11). The pilot values
# `copy_companion_in_hand` (EB-17p §13.8 resolution): 40,396 draws / 0 plays
# was pilot SCORING by construction, not an unsatisfiable condition -- the op
# was worth nothing in `_tempo_value`, so base borrowed_brilliance always
# scored -0.1 (= -cost_weight x 1) and the hard `best_score <= 0` rule never
# let it be played, while the drafter kept taking it at 4.0. New
# `PILOT_COMPANION_COPY_VALUE` = 1.5 in `_tempo_value`, gated on the ENGINE's
# own companion predicate (`Card.is_companion`, the `comps` selection in
# `_op_copy_companion_in_hand`) so the two cannot disagree; `study_buddy`'s
# `replay_next_companion` reads through the same branch. Universal, but only
# Klee and Furina print either op, so only their cells move -- every Klee
# tier0.5 number does. C.PILOT_WEIGHTS_VERSION 1 -> 2 in the same edit. The
# payoff-reach registration's DRAFTER_VERSION = 14 pin is UNTOUCHED: the
# drafter is not taught anything here, only the pilot.
# POLICY_VERSION 8 (EB-118 Phase 2A, 2026-08-24). THE SWITCH IS THROWN, and
# this is the integer the PROPOSED block reserved when the pair landed inert on
# 2026-08-23: the bump executes when the switch is thrown, not when the code
# lands.
#
# Two decisions the engine had been making with a placeholder moved into
# `tier0/pilot/policy.py`, both behind `policy.PILOT_POLICIES_ENABLED`, which
# shipped FALSE and now ships TRUE. While it was off, both call sites ran their
# pre-EB-118 code and every number on the staging branch -- the frozen
# calibration battery included -- was byte-identical, which is why the stamp
# could not move first. That pre-policy code is still LIVE BEHIND the switch:
# it is the comparator the W4 sweep's byte-identity arm forces off
# (`tier05/pilot_weight_sweep.sandbox`, `force=False`), not dead code.
#
# (a) KLEE, bomb placement. `place_bomb` in its concentration form
# (`target: enemy`) resolved through `_pick_targets`, i.e. lowest HP: a
# targeting heuristic standing in for a decision. `bomb_placement_target`
# enumerates the legal enemies and prices what a bomb is actually worth on
# each -- what the target can still absorb before the pile is past lethal
# (bombs beyond lethal are simply not dealt), the pile it joins and lives to
# detonate with, the Weak-rate attack that arming an unsuppressed enemy costs
# it, and the pile readers in hand (`detonate` aimed here pays only when the
# pop is lethal, which is the rule the damage estimator already applies).
# Random-target placements and free plays' forced random targeting are
# untouched: those are variance profiles and parity law, not decisions.
#
# (b) KOKOMI, exhaust selection. A chosen `exhaust_from` spent
# `_worst_card` -- highest-cost non-Attack -- which looks expert exactly when
# the expensive card happens to be the dead one and is otherwise backwards: it
# throws away the payoff and keeps the dud. `exhaust_victim` scores each
# candidate as the exhausting card's payout for that victim minus the victim's
# own future value (its pilot valuation in the current state, per energy, with
# junk negative and a self-exhausting card discounted). The payout is a HOOK
# defaulting to identity-blind, because no shipped grammar reads the victim's
# identity; when one is written its payout arrives as a parameter rather than
# as a second heuristic. The pool is the engine's -- post-C11 Kokomi's rotation
# law has already dropped junk from it -- and the chooser never widens it.
#
# ONE BUMP, not two: both are the same class of change (the pilot's judgement,
# not the engine's rules), they land behind one switch, and neither is
# quotable alone -- the switch cannot be thrown for one policy and not the
# other, so no cell exists in which only one is live. Same argument v11 and
# v12 made on the RUNTEMPLATE side.
#
# WHAT RE-BASELINED AT THE BUMP: every Klee tier-0.5 number (four printed rows
# place in the concentration form) and every Kokomi number that touches a chosen
# exhaust, which under the casket is her whole Charge engine. Moving in the
# SAME landing edit and nothing else: `C.PILOT_WEIGHTS_VERSION` 2 -> 3, because
# the EB-118 weights ENTER the set it labels the moment they are first read --
# the R176 reading of that rule. `RUNTEMPLATE_VERSION` (12), `DRAFTER_VERSION`
# (16) and `CONSTANTS_VERSION` (13) are all UNTOUCHED: the drafter learns
# nothing here, only the pilot, and no run-layer content and no balance
# constant moved. THE LIVE CELL AT THIS LANDING IS `RT12/D16/P8/C13` -- D16 and
# C13 are Phase 2's CONTENT windows, closed earlier the same day as R202's step
# (iii) required and NOT anything this edit moved; the block above was written
# against the pre-close `D15`/`C12` world and is corrected here rather than
# left to rot.
#
# THE GATE THAT HELD THIS FLIP WAS RETIRED, NOT SATISFIED. It was staged rather
# than landed against ONE red test -- `test_pass3.py::test_per_deck_a2_bands`,
# `klee/reaction_weighted` `A2_scaling` 3.4898 -> 3.5290 against a ratified
# band of 3.5 -- and R204 (2026-08-24) retired the live per-axis deck-band
# system as acceptance law roster-wide, deleting that test with the system it
# read and closing `QUEUE` `M40` with NO replacement number. What the ruling
# acted on is the probe: the band did not hold pre-flip either (3.5810 at
# seed 7, 3.7735 at n=1000/seed 42), so the gate was passing on one lucky cell
# by 0.0102, and the flip's own contribution is a consistent +0.035 against a
# 0.21 seed spread. Seven-axis values are reportable diagnostics from here and
# gate nothing. UN-GATED IS NOT UN-SEQUENCED: this landing keeps its place in
# R191's window order, which is exactly why the 2C block below is still
# PROPOSED and `MODE_CHOOSER_ENABLED` is still False.
#
# WHAT THE SWITCH DID TO THE SIM, recorded here so no later reader mistakes it
# for the Phase-2 result: at the shipped weights NO cell separates at either
# read -- `klee/demolition` 7.05% -> 6.70%, `klee/spark` 4.35% -> 3.75%,
# `kokomi/priest` 1.35% -> 1.30%, `kokomi/assist` 0.40% -> 0.35% (n=2000, seed
# 12, every interval overlapping), with `furina/salon` byte-identical across
# the switch. A better decision rule bought no measurable winrate on these
# cells; the citable Phase-2 read is the post-read owed AFTER 2C's window
# closes, not these four numbers.
#
# POLICY_VERSION 9 -- the EB-118 PHASE-2C MODE-CHOOSER FLIP (2026-08-24), the
# SECOND and LAST of Phase 2's two activation windows, and with it Phase 2 is
# complete. Deliberately not folded into the one above: R191 ruled that the
# mode-valuation chooser takes its OWN activation window, so it rides its own
# flag (`policy.MODE_CHOOSER_ENABLED`, now True) rather than the 2A pair's.
# Two flags, two flips, two integers -- and the flip is what executes either,
# not the code landing.
#
# WHAT MOVES: `effects._chosen_mode`, the seam a `choose_one` resolves
# through, stops returning a fixed index and asks `policy.choose_mode` --
# argmax of the pilot's EXISTING per-op play valuations (damage, block,
# scaling, tempo, sustain, each at weight 1, for `exhaust_future_value`'s
# reason) over the live board, minus the TRUE HP an overdrawing
# `spend_encore` would cost at `policy.MODE_OVERDRAW_HP_VALUE`. Ties break to
# the LOWEST mode index, which is what makes the staged fixed index the
# degenerate case of the new rule instead of a branch beside it.
#
# WHAT RE-BASELINES AT THE BUMP: every tier-0.5 number taken with a modal card
# in the pool. Today that is `deep_breath` and nothing else -- the prototype
# discipline is one card until the pilot and the price can distinguish the
# modes -- and see the acceptance note at the `choose_one` price row for why
# the drafter's number does not move with it.
#
# THE PAIR THE CHOOSER READS WAS RE-BODIED FIRST, IN THE SAME LANDING (R205,
# [USER] 2026-08-24), and the reason is the measurement this block used to
# predict. As staged, under R194's ratified 2/2 pair, the chooser took mode 1
# on EVERY board: mode 1 scores `energy 1` + `gain_encore 2` = 1.0 + 1.6 = 2.6
# with NO state-dependent term in it, and 2/2 topped out at `draw 2` = 2.0 on a
# bank that covered the spend, so the gap was at least 0.6 whatever the board
# looked like. That was a real reading of the pilot's currency and not a broken
# chooser -- and it meant the flip would have moved NO Furina number, which is
# a null nobody could read as "modal cards are neutral".
# The exit taken is the RE-BODY, not a weight sweep: mode 2 is `Spend 3 Encore:
# draw 3` and mode 1 is unchanged. The dominance was STRUCTURAL (mode 1 has no
# state-dependent term to lose on, so no setting of the two weights makes mode
# 2 win a board), and `MODE_OVERDRAW_HP_VALUE` and `MODE_TIE_EPSILON` are
# SHARED policy whose bending reprices every Encore generator in the pool.
# MEASURED AT THIS LANDING AGAINST `policy.mode_score` ITSELF, not against the
# arithmetic above, and IDENTICAL ON BOTH FACES (the score reads the mode BODY
# on a neutral frame, so the `{cost: -1}` upgrade cannot move it):
#   bank    0     1     2     3+
#   mode 1  2.6   2.6   2.6   2.6
#   mode 2  0.0   1.0   2.0   3.0
#   pick    1     1     1     2
# So the chooser now takes mode 2 at a bank of 3 or more and mode 1 below it,
# which is the property the ruled pair lacked. The drafter's number is
# unmoved by the re-body as well as by the conversion -- mode 2 prices at
# -0.6000 -> -0.9000 and `MAX(modes)` returns mode 1's 0.6000 either way, on
# both faces -- so no `DRAFTER_VERSION` move is owed here.
#
# BOTH PHASE-2 FLIPS ARE NOW TAKEN AND PHASE 2 IS COMPLETE. `POLICY_VERSION` 8
# was the 2A pair's flip and nothing else; 9 is this one and nothing else,
# exactly as R191 separated them. What is owed next is R202 step (iii)'s tail:
# the Phase-2 post-read, taken ONCE over both activation windows rather than
# once per switch.
#
# POLICY_VERSION 10 -- the EB-118 PHASE-3 WINDOW 3 EXHAUST-CHOOSER REPAIR
# (R211, [USER] 2026-08-25), landed 2026-08-25. NOT A FLIP: there is no switch
# here and none was staged. `policy.exhaust_victim`'s DEFAULT payout hook
# changes from `identity_blind_payout` to `formula_aware_payout`, and
# `C.PILOT_WEIGHTS_VERSION` 4 -> 5 labels the weight that arrives with it
# (`EXHAUST_FORMULA_PAYOUT_WEIGHT = 1.0`).
#
# WHY A BODY ALONE DOES NOT WORK, which is the whole reason R208 deferred
# `pearl_barrage` into this window as ONE design unit: the old default was
# "lose the least", a constant that cannot see a printed payout slope, so a
# card whose damage scales with the COST of what you exhausted exerted no pull
# at all on which card the pilot picked. Measured, the shipped chooser already
# ties the pool's dearest cost on ~79% of selections and realises ~82% of the
# available cost -- so the defect is REAL, MODEST and FORMULA-BLIND, not
# cheapest-seeking, and the repair is correspondingly small.
#
# WHAT THE HOOK READS IS WHAT THE CARD PRINTS, never a preference for
# expensive cards: the marginal contribution the candidate would make to the
# exhausting card's own printed `exhaust_selection_*` count, times that card's
# own printed `per`, times the board its own printed `target` names. R211's
# multiplicity clause is that last factor -- an `all_enemies` formula
# multiplies by `len(state.living_enemies)`, because a wide card really does
# buy `per` points on every body. Change the slope and the chooser changes
# with it; delete the card and the chooser is identity-blind again.
#
# WHAT RE-BASELINES AT THIS BUMP IS NARROWER THAN THE STAMP SUGGESTS, and it
# is asserted rather than argued. The hook returns 0.0 for any card printing
# no selection formula, exactly TWO rows on any sheet print one, and the
# chooser is deterministic given the pool -- so every OTHER chosen-Exhaust
# carrier's pick is unchanged, over all twelve of them, Sly riders included.
# `test_eb118_policies.test_no_existing_carriers_pick_moved` sweeps that in
# milliseconds, and it exists BECAUSE it replaces a fourth scratch run that
# would have been provably bit-identical to baseline.
#
# ONE WINDOW, and each field moves on its own ground: `C` 18 -> 19 (the eight
# sheet rows), `D` 16 -> 17 (the spend dial and the Spotlight rider), `RT`
# untouched. R191's one-variable-per-window order is kept by what is NOT here:
# the pilot's Encore opportunity-cost repair is a second pilot-version change
# with its own re-baseline and is deferred out of this window by ruling.
#
# POLICY_VERSION 11 -- THE SCORER-LITERACY WINDOW (2026-08-26). ONE window
# under R207's shared-window clause, carrying FOUR items, because nothing
# turns on attributing a movement to one of them: all four are repairs to
# what the pilot can SEE, none of them changes a printed number, a label, an
# upgrade delta or a drafter dial, and the decision that follows the window
# (the Phase-4 milestone read) needs the whole set landed rather than any one
# of them isolated.
#
#   * EB-143 -- the Spark HOLD-versus-SPEND term, and the ONE new weight in
#     the window: `policy.SPARK_HOLD_VALUE_WEIGHT = 1.0`, which takes
#     `C.PILOT_WEIGHTS_VERSION` 5 -> 6. `spend_spark` appeared nowhere in
#     `tier0/pilot/` before this, so the bank was a one-way meter -- a Spark
#     GAINED paid `C.PILOT_SPARK_VALUE` and a Spark SPENT cost nothing, an
#     arbitrage the scorer could see. Three legs, largest wins: the stock
#     floor, the free-Attack threshold, and the biggest payoff in hand the
#     drop would shrink. At 0.0 the term vanishes and the pilot is
#     byte-identical to `P10`, which is pinned as a test.
#   * EB-144 -- predicate and Salon-verb literacy, NO new weight.
#     `_active_effects` ended in a bare `else: continue` that yielded NEITHER
#     branch, so an untaught predicate priced a whole conditional at zero in
#     silence. FIVE predicates over TEN sheet rows, seven of them predating
#     `W3`. `reaction_triggered_by_this` and `killed_target` stay BLIND on
#     purpose -- they are mid-resolution and have no honest score-time answer
#     -- and `policy.BLIND_PREDICATES` is that decision made visible. Both
#     Salon verbs are valued by asking the resolver's own
#     `salon_tick_amount`, so no dial is minted for them.
#   * EB-145 -- payout-aware SCORING of a chosen exhaust, NO new weight.
#     `P10` made the PICK formula-aware and left the SCORE at the base; the
#     scorer now runs the same chooser over `effects.exhaust_pool` and reads
#     the result through the engine's own `_calc_amount`. Tide of Names and
#     Pearl Barrage are the only two rows that print a selection formula, and
#     neither is named in the code. `exhaust_future_value` SUSPENDS the
#     forecast, which both terminates the recursion and keeps `P10`'s ratified
#     chooser arithmetic byte-identical.
#   * EB-129 -- Book of Five Rings chunk credit at event valuation, no new
#     weight. R205 filed it for its own window; [USER] set that gate aside
#     2026-08-26 on the strength of a null commit-hash scratch, applying
#     R207's shared-window clause.
#
# ARCHIVE SCOPE: roster combat and tier-0.5 numbers only. Both anchors are
# provably unmoved -- `ref_ironclad` and `ref_silent` print none of the five
# predicates, neither Salon verb, no `spend_spark` and no selection formula
# (asserted directly in `test_eb144_predicate_literacy`), and EB-129's bare
# arms take no events by construction.
#
# WHAT IS OWED NEXT: ONE re-baseline at this cell, and it has NOT been taken
# here. The standing read's three diagnostic caveats
# (`review/records/sitting-reads-2026-08-25-c19-d17-p10.md`) clear AT THAT
# RE-BASELINE, not at this bump -- landing the repair is not reading it. The
# Phase-4 milestone read follows the re-baseline (R207, R211 item 7).
POLICY_VERSION = 11

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


# ---------------------------------------------------------------------------
#  The blind-pick CONTROL (payoff-reach registration §6.5, control C2)
# ---------------------------------------------------------------------------

def blind_policy(rng: random.Random, deck: list[Card],
                 offers: list[Card], archetype: str) -> Optional[Card]:
    """Take uniformly at random from the screen. The offer floor, empirically.

    NOT A PILOT AND NOT AN ARM OF THE STANDING A/B. This is the negative
    control the payoff-reach registration authorises as its `C2` (the same
    shape R181 authorised for `M13`'s `C2`): the census computes a blind-draft
    offer floor ARITHMETICALLY -- `offer x cards drafted` -- and Q-A's
    prediction is stated against that floor. Comparing a sim number against an
    arithmetic one is the weakness the control removes: this policy draws the
    floor from the same run machinery the arms use, so the comparison is
    like-for-like.

    Uniform over the WHOLE screen and it never skips. That is the definition
    the floor needs: the census's `offer_reach` is "the chance that ONE offered
    card is a payoff", scaled by cards drafted, which presumes one card taken
    per screen with no selection at all. A skip rule, a defense quota, or any
    scoring here would make this a bad drafter rather than no drafter.

    `POLICY_VERSION` is UNTOUCHED by this addition and that is not an
    oversight. The stamp's `P` names the shipped pilot/drafting behaviour that
    every quoted tier-0.5 number was measured through; `assigned` and
    `adaptive` are byte-identical before and after this edit, so no archived
    number moves and there is nothing for a bump to archive. A control that
    only ever runs in its own declared arm adds a row to POLICIES; it does not
    change what P7 means.

    RNG: the run's MAIN stream is not used. `own_rng` below makes `model` hand
    this policy a dedicated stream (`seed + 6e9`, the next free offset in
    understudy/rng.py's registry) for the standing reason every dedicated
    stream in this repo exists -- drawing picks off the main stream would
    advance it and renumber every encounter, reward roll and shop after each
    screen, so the control would not be measuring the same runs the arms
    measure. Seed-determined either way, so the control replays.
    """
    if not offers:
        return None
    return rng.choice(offers)


# Read by `model._RunCtx`: this policy is handed the dedicated policy stream
# instead of the run's main rng. Same seam shape as `emergent_plan` above --
# the model reads a flag the policy declares, rather than knowing its name.
blind_policy.own_rng = True


# The A/B pair, plus the registered control. hybrid_policy is a diagnostic run
# on demand (see its docstring), not a third arm of the standing A/B; `blind`
# is a negative control and is never a comparator for a shipped number.
POLICIES = {"assigned": assigned_policy, "adaptive": adaptive_policy,
            "blind": blind_policy}

# The STANDING A/B, named separately from the registry above so that adding a
# control to POLICIES cannot silently enlarge it. `ab.run_ab` used to iterate
# POLICIES itself, which made "every callable a run may fly" and "the two arms
# the A/B compares" the same list -- a control landing in a shipped comparison
# report is precisely the interference a control must not cause.
AB_POLICIES = ("assigned", "adaptive")


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


# The hindsight advantage a re-scored rival must clear before the decision it
# beat is called a regret. UNCALIBRATED and NOT RATIFIED (R164, 2026-08-10:
# "pre-register the measurement; do NOT ratify +1.0"). It was a bare literal
# inside the loop below until EB-72 gave it a name; naming it derives nothing
# and blesses nothing -- it exists so `draft_regret_gaps` can be the
# margin-free half and this can be the one place the threshold is spelled.
# Its route twin is `run_metrics.ROUTE_REGRET_MARGIN`, which carries the longer
# note on why neither number has a provenance. Pinned at its boundary by
# test_pin_tier05_draft.py (MEDIUM-11).
DRAFT_REGRET_MARGIN = 1.0


def draft_regret_gaps(rng: random.Random, decisions: list[dict],
                      final_deck: list[Card], archetype: str,
                      sample: float = C.DRAFT_REGRET_SAMPLE) -> list[float]:
    """The RAW hindsight gaps behind `draft_regret` (EB-72).

    One entry per SAMPLED screen, in screen order: the best re-score on that
    screen minus the re-score of the card actually picked, both in the final
    deck's context. Zeros stay in the sample -- a screen the drafter got right
    is a 0.0, not an absence from it -- because a percentile taken over only
    the decisions that already cleared the margin would be a percentile of the
    threshold as much as of the drafter.

    NOT CLAMPED AT ZERO, and this is the one place a gap can go negative: a
    SKIPPED screen scores the pick at 0.0 by convention (`draft_regret`'s
    "skip scores 0"), so a screen where every offer re-scored negative gives a
    negative gap. Clamping would be tidier and would report a skip as a
    decision with nothing to regret. A screen with no offers contributes no
    entry.

    `draft_regret` is the count of these above `DRAFT_REGRET_MARGIN`. Same rng,
    same draws, same order -- but NOT bit-identical to the pre-split loop. That
    loop asked `any(v > picked + 1.0)`; this one asks `(max - picked) > 1.0`,
    and in floating point those differ at the exact-1.0 boundary. The
    re-associated form is the faithful reading of MEDIUM-11's invariant ("MORE
    THAN a full point"), so a gap of exactly 1.0 is NOT a regret; the old form
    counted some of them, because `picked + 1.0` can round below the rival's
    score. It is reachable on real data and it moves the count: measured over
    120 runs at census sample rate, 197 -> 196. Nothing gates on the count, so
    this is a reporting difference, not a behaviour change. The boundary itself
    is pinned by `test_regret_distribution.py`.

    `sample` is overridable for the same reason the route twin's is (see
    `C.ROUTE_REGRET_SAMPLE`'s comment): the 0.10 default exists to keep the
    IN-RUN re-scoring cheap, and a post-hoc reader that wants the whole census
    of screens should not have to edit a constant to get it. Overriding it
    changes which screens are re-scored and therefore breaks the equality with
    the run's own `regret_samples` -- callers that rely on that equality must
    leave it alone.
    """
    gaps: list[float] = []
    for d in decisions:
        if rng.random() >= sample:
            continue
        rescored = {c.id: score_offer(c, final_deck, archetype)
                    for c in d["offers"]}
        if not rescored:
            continue
        picked_score = rescored.get(d["picked"], 0.0)   # skip scores 0
        gaps.append(max(rescored.values()) - picked_score)
    return gaps


def draft_regret(rng: random.Random, decisions: list[dict],
                 final_deck: list[Card], archetype: str) -> int:
    """Post-run re-scoring of sampled decisions in the final-deck context.
    Returns the number of regretted decisions among the sample."""
    return sum(1 for gap in draft_regret_gaps(rng, decisions, final_deck,
                                              archetype)
               if gap > DRAFT_REGRET_MARGIN)
