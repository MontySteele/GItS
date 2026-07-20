"""Assigned draft policy + draft_regret (spec §4).

Assigned mode: the run is seeded with a target archetype. Scoring terms:
- archetype fit: enabler value DECAYS as the core completes; payoff value
  is GATED on the core being online (else you draft win-more blanks)
- universal: defense quota (the real-draft principle codified), curve
  awareness, deck-size penalty, Burst priority for reaction
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
    """Is the archetype 'online'? (spec §5: reaction core := 2 appliers +
    1 amp payoff + Burst; other archetypes: DRAFT_CORE_SIZE on-plan
    enabler/payoff cards.)"""
    if archetype == "reaction":
        appliers = sum(1 for c in deck if _is_applier(c))
        amps = sum(1 for c in deck if _is_amp_payoff(c))
        burst = any("burst" in c.tags for c in deck)
        return appliers >= 2 and amps >= 1 and burst
    on_plan = sum(1 for c in deck if archetype in c.archetypes
                  and c.role in ("enabler", "payoff"))
    return on_plan >= C.DRAFT_CORE_SIZE


def _core_progress(deck: list[Card], archetype: str) -> float:
    if archetype == "reaction":
        appliers = min(2, sum(1 for c in deck if _is_applier(c)))
        amps = min(1, sum(1 for c in deck if _is_amp_payoff(c)))
        burst = 1 if any("burst" in c.tags for c in deck) else 0
        return (appliers + amps + burst) / 4
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


def score_offer(card: Card, deck: list[Card], archetype: str) -> float:
    s = 0.0
    progress = _core_progress(deck, archetype)
    online = core_complete(deck, archetype)
    # A card that ADVANCES the core is never a dead pick — without this,
    # reaction deadlocks: its core contains an amp payoff, but payoffs
    # were gated on the core being online (measured: 1% amp assembly).
    if _core_progress(deck + [card], archetype) > progress:
        s += 3.0
    if archetype == "generic" and not card.is_companion:
        # The anchor drafts on raw power; roles stand in for engine cards.
        s += min(2.5, _static_power(card) / 3.0)
        if card.role in ("enabler", "payoff"):
            s += 1.0
    # Same exclusion as adaptive_score: companions get the dedicated block
    # below. Without this the derived reaction tag silently re-tunes assigned
    # mode too, which would move the frozen M5 numbers for a reason that has
    # nothing to do with the drafting question they were measuring.
    if archetype in card.archetypes and not card.is_companion:
        if card.role == "enabler":
            s += 3.0 * max(0.25, 1.0 - progress)     # decays as core fills
        elif card.role == "payoff":
            s += 4.0 if online else 1.0              # gated on the core
        else:
            s += 1.5
    elif "generic" in card.archetypes:
        s += 0.8
    if card.is_companion:
        if archetype == "reaction":
            # Companions ARE reaction's enablers (deliberate asymmetry).
            s += 3.5 * max(0.25, 1.0 - progress) if _is_applier(card) else 1.5
        else:
            s += 0.5
    if archetype == "reaction" and "burst" in card.tags:
        s += 3.0                                     # Burst priority
    if _has_block(card) and _block_density(deck) < C.DRAFT_BLOCK_DENSITY_MIN:
        s += 2.5                                     # defense quota
    cost = card.cost if isinstance(card.cost, int) else 2
    avg_cost = (sum(c.cost for c in deck if isinstance(c.cost, int))
                / max(1, sum(1 for c in deck if isinstance(c.cost, int))))
    if cost >= 2 and avg_cost > 1.3:
        s -= 1.0                                     # curve awareness
    s -= max(0, len(deck) - C.DRAFT_DECK_SOFT_CAP) * 0.4   # deck bloat
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
    if "burst" in card.tags:
        s += 1.0 + 2.5 * shares["reaction"]
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

    Only reaction behaved differently (14/214), because appliers and Burst move
    its core without carrying an archetype tag -- which is why reaction was the
    one archetype whose relevance moved with the policy.

    The measured effect of tightening this is small and downward: it removes
    offers that were already complete-core no-ops. Relevance was NOT rescued by
    the stricter reading, so the 60-70% claim fails under both.
    """
    progress = _core_progress(deck, archetype)
    return any(_core_progress(deck + [c], archetype) > progress for c in offers)


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
