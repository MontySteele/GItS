"""Pin tests for the tier 0.5 draft scorer and policy.

Three behaviours that the rest of the suite exercises only indirectly: the
AoE premium in `_static_power`, the deck size at which the late-run lean
gate engages in `assigned_policy`, and the margin `draft_regret` requires
before it calls a decision regretted. Each test pins the constant's effect
at its boundary, not merely its direction.
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft


def _cards(*ids):
    return [loader.get_card(i) for i in ids]


class _AlwaysSample:
    """An rng stand-in whose `random()` always clears the regret sample gate."""

    def random(self) -> float:
        return 0.0


# --- HIGH-20: the AoE premium ---

def test_all_enemies_damage_is_priced_at_the_aoe_multiple_of_its_face():
    """A damage line targeting all_enemies is worth STATIC_AOE_MULT times
    what the same printed damage would be worth against a single body, so an
    AoE card can outprice a single-target card that prints more damage at the
    same cost."""
    # Undercurrent prints 2 damage x3 at all_enemies, cost 2.
    undercurrent = loader.get_card("undercurrent")
    single_target_reading = 2 * 3 / 2
    assert draft._static_power(undercurrent) == \
        single_target_reading * draft.STATIC_AOE_MULT
    assert draft._static_power(undercurrent) == 6.0

    # The premium is large enough to reorder cards: 8 damage to all enemies
    # at cost 1 prices above 10 damage to one enemy at cost 1.
    cleave = loader.get_card("cleave_like")          # 8 all_enemies, cost 1
    waterspout = loader.get_card("waterspout")       # 10 enemy, cost 1
    assert draft._static_power(cleave) == 16.0
    assert draft._static_power(waterspout) == 10.0
    assert draft._static_power(cleave) > draft._static_power(waterspout)


# --- HIGH-21: the late-run lean gate boundary ---

def test_lean_gate_engages_at_exactly_draft_lean_cap_cards():
    """The late-run discipline starts filtering offers once the deck HOLDS
    DRAFT_LEAN_CAP cards: at one card below the cap the highest-scoring offer
    is taken as-is, at the cap itself only Powers / tempo / Block / bar-
    clearing rares remain eligible even when a plain attack scores higher."""
    assert draft.DRAFT_LEAN_CAP == 15
    deck_below = _cards(*loader.starting_deck("klee")) + \
        _cards("strike", "strike", "strike", "shiv")
    deck_at_cap = deck_below + _cards("shiv")
    assert len(deck_below) == draft.DRAFT_LEAN_CAP - 1
    assert len(deck_at_cap) == draft.DRAFT_LEAN_CAP

    # blast_radius is the higher-scoring offer but is a plain common attack:
    # no Power, no tempo, no Block, not a rare. durin_witchs_flame scores
    # lower and survives the gate purely by being a Power.
    blast = loader.get_card("blast_radius")
    durin = loader.get_card("durin_witchs_flame")
    assert draft.score_offer(blast, deck_at_cap, "demolition") > \
        draft.score_offer(durin, deck_at_cap, "demolition")
    assert durin.type == "power"
    assert blast.type != "power"
    assert not draft._has_tempo(blast) and not draft._has_block(blast)

    offers = [blast, durin]
    assert draft.assigned_policy(
        random.Random(0), deck_below, offers, "demolition") is blast
    assert draft.assigned_policy(
        random.Random(0), deck_at_cap, offers, "demolition") is durin


# --- MEDIUM-11: the regret margin ---

def test_draft_regret_needs_a_full_point_of_hindsight_advantage():
    """A sampled decision counts as regretted only when some other offer
    re-scores MORE THAN a full point above the card actually picked: a
    rival that merely outscores the pick by a fraction is not a regret."""
    assert C.DRAFT_REGRET_SAMPLE == 0.10
    final_deck = _cards(*loader.starting_deck("klee"))
    # FIXTURE SWAP 2026-08-06 (R118 10.2 rider): the near-miss rival used to
    # be `cleave_like`, but the ref_ironclad package cards gained
    # `archetypes: [generic]` for the anchor instrumentation, and the
    # drafter's off-plan generic term (+0.8) moved cleave_like's score to an
    # exact tie with blast_radius -- no longer "beaten by a fraction".
    # `sizzle` carries the same 0-< delta <-1 shape (0.8) with no tag in
    # play. The pin's invariant (a regret needs MORE THAN a full point of
    # hindsight advantage) is untouched.
    score = {cid: draft.score_offer(loader.get_card(cid), final_deck,
                                    "demolition")
             for cid in ("blast_radius", "sizzle", "rapid_fire")}

    # Rival beats the pick, but by less than a point -- not a regret.
    assert 0 < score["blast_radius"] - score["sizzle"] < 1.0
    near_miss = {"offers": _cards("sizzle", "blast_radius"),
                 "picked": "sizzle"}
    assert draft.draft_regret(_AlwaysSample(), [near_miss], final_deck,
                              "demolition") == 0

    # Rival beats the pick by more than a point -- a regret.
    assert score["blast_radius"] - score["rapid_fire"] > 1.0
    real_regret = {"offers": _cards("rapid_fire", "blast_radius"),
                   "picked": "rapid_fire"}
    assert draft.draft_regret(_AlwaysSample(), [real_regret], final_deck,
                              "demolition") == 1

    # Both decisions in one sample: only the second is counted.
    assert draft.draft_regret(_AlwaysSample(), [near_miss, real_regret],
                              final_deck, "demolition") == 1
