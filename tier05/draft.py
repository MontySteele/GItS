"""Assigned draft policy + draft_regret (spec §4).

Assigned mode: the run is seeded with a target archetype. Scoring terms:
- archetype fit: enabler value DECAYS as the core completes; payoff value
  is GATED on the core being online (else you draft win-more blanks)
- raw printed power (DRAFTER_VERSION 2, ruling R2.1 — adopted from the
  hybrid experiment after it beat both parents everywhere)
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
from tier0.engine.state import Card

AMP_PAYOFF_POWERS = C.AMP_PAYOFF_POWERS   # shared with the content loader


def _has_block(card: Card) -> bool:
    return any(fx.get("op") == "block" for fx in card.effects)


def _block_density(deck: list[Card]) -> float:
    return sum(1 for c in deck if _has_block(c)) / max(1, len(deck))


def _is_applier(card: Card) -> bool:
    return card.role_c == "applier"


def _is_amp_payoff(card: Card) -> bool:
    # A reaction payoff: rewards existing auras or amps reactions.
    return ("reaction" in card.archetypes and card.role == "payoff")


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
    on_plan = sum(1 for c in deck if archetype in c.archetypes
                  and c.role in ("enabler", "payoff"))
    return on_plan >= C.DRAFT_CORE_SIZE


def _core_progress(deck: list[Card], archetype: str) -> float:
    if archetype == "reaction":
        appliers = min(2, sum(1 for c in deck if _is_applier(c)))
        amps = min(1, sum(1 for c in deck if _is_amp_payoff(c)))
        return (appliers + amps) / 3
    on_plan = sum(1 for c in deck if archetype in c.archetypes
                  and c.role in ("enabler", "payoff"))
    return min(1.0, on_plan / C.DRAFT_CORE_SIZE)


def _static_power(card: Card) -> float:
    """Printed damage+block per energy — a deliberately dumb immediate-
    value proxy for the generic (anchor) archetype, whose cards carry no
    archetype tags. The real power/synergy scorer is M6's adaptive policy."""
    total = 0.0
    for fx in card.effects:
        if fx.get("op") == "damage" and fx.get("target") != "self":
            amt = fx.get("amount", 0)
            if isinstance(amt, int):
                total += amt * (fx.get("times", 1)
                                if isinstance(fx.get("times", 1), int) else 1)
        elif fx.get("op") == "block":
            total += fx.get("amount", 0)
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


def score_offer(card: Card, deck: list[Card], archetype: str) -> float:
    s = 0.0
    progress = _core_progress(deck, archetype)
    online = core_complete(deck, archetype)
    # A card that ADVANCES the core is never a dead pick — without this,
    # reaction deadlocks: its core contains an amp payoff, but payoffs
    # were gated on the core being online (measured: 1% amp assembly).
    if _core_progress(deck + [card], archetype) > progress:
        s += 3.0
    # DRAFTER_VERSION 2 (ruling R2.1): the raw-power term, adopted from
    # the hybrid experiment after it beat both parents in all three
    # archetypes. A plan-committed drafter with zero power awareness is
    # an implausible human, and the acceptance law requires plausible
    # drafts. Share-synergy stays excluded — assigned already prices fit
    # off its target, and stacking share-synergy would double-count it.
    s += min(3.0, _static_power(card) / 3.0)
    if (archetype == "generic" and not card.is_companion
            and card.role in ("enabler", "payoff")):
        # The anchor's roles stand in for engine cards. (Its old private
        # power term dissolved into the universal one above.)
        s += 1.0
    # Same exclusion as adaptive_score: companions get the dedicated block
    # below. Without this the derived reaction tag silently re-tunes assigned
    # mode too, which would move the frozen M5 numbers for a reason that has
    # nothing to do with the drafting question they were measuring.
    if archetype in card.archetypes and not card.is_companion:
        if card.role == "enabler":
            s += 3.0 * max(0.25, 1.0 - progress)     # decays as core fills
        elif card.role == "payoff":
            if archetype == "reaction" and _is_amp_payoff(card):
                s += 4.0 if online else REACTION_AMP_OFFLINE
            else:
                s += 4.0 if online else 1.0          # gated on the core
        else:
            s += 1.5
    elif "generic" in card.archetypes:
        s += 0.8
    if card.is_companion:
        if archetype == "reaction":
            # Companions ARE reaction's enablers (deliberate asymmetry).
            s += (REACTION_APPLIER_WEIGHT * max(0.25, 1.0 - progress)
                  if _is_applier(card) else 1.5)
        else:
            s += 0.5
    if _has_block(card) and _block_density(deck) < C.DRAFT_BLOCK_DENSITY_MIN:
        s += 2.5                                     # defense quota
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
        s -= max(0, len(deck) - REACTION_LEAN_CAP) * REACTION_LEAN_PENALTY
    return s


def assigned_policy(rng: random.Random, deck: list[Card],
                    offers: list[Card], archetype: str) -> Optional[Card]:
    if not offers:
        return None
    scored = sorted(((score_offer(c, deck, archetype), i, c)
                     for i, c in enumerate(offers)), reverse=True)
    best_score, _, best = scored[0]
    if best_score < C.DRAFT_SKIP_THRESHOLD:
        return None                                  # skip is a real pick
    return best


# ---------------------------------------------------------------------------
#  M6: the adaptive policy -- the goodstuff detector
# ---------------------------------------------------------------------------

ARCHETYPES = ("demolition", "spark", "reaction")


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
    tagged = [c for c in deck
              if c.rarity != "basic"
              and (companions or not c.is_companion)
              and any(a in ARCHETYPES for a in c.archetypes)]
    if not tagged:
        return {a: 0.0 for a in ARCHETYPES}
    return {a: sum(1 for c in tagged if a in c.archetypes) / len(tagged)
            for a in ARCHETYPES}


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
    s = min(3.0, _static_power(card) / 3.0)
    shares = archetype_shares(deck)
    # Companions are scored by the dedicated block below, NOT here. They now
    # carry a derived `reaction` tag so that archetype_shares can see them --
    # that was the actual bug -- but the scorers always had bespoke companion
    # handling, so running them through the generic archetype term as well pays
    # reaction's share twice and turns the rich-get-richer loop into a runaway:
    # measured, it drove reaction from 13.2% to 85.5% of decks with both
    # divergence alarms firing. The tag fixes the METRIC; it is not new scoring.
    for a in (card.archetypes if not card.is_companion else ()):
        if a not in ARCHETYPES:
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
        s += 2.0 * shares["reaction"]      # they are reaction's enablers
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
# third arm of anything anymore.
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
