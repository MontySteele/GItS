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

AMP_PAYOFF_POWERS = {"amp_reaction_up", "witchs_flame"}


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
    if archetype in card.archetypes:
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
