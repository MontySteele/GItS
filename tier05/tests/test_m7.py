"""M7: rest-site smithing in the run model."""

from tier0.content import loader, upgrades
from tier05 import draft, model


def test_runs_actually_upgrade_and_stay_deterministic():
    rs = model.run_many("klee", "demolition", "demolition",
                        draft.assigned_policy, runs=30, seed=11)
    upgraded = [r for r in rs
                if any(cid.endswith("+") for cid in r.deck_ids)]
    assert upgraded, "healthy rests must smith on-plan cards"
    smiths = [t for r in rs for t in r.rests if t[1] == "upgrade"]
    assert smiths
    # Every smithed id must resolve through the loader.
    for _, _, cid in smiths:
        loader.get_card(cid + upgrades.SUFFIX)
    again = model.run_many("klee", "demolition", "demolition",
                           draft.assigned_policy, runs=30, seed=11)
    assert [r.deck_ids for r in rs] == [r.deck_ids for r in again]


def test_upgrade_prefers_on_plan_payoffs():
    deck = loader.starting_deck("klee") + ["explosives_workshop", "mine_toss"]
    action, target = model.rest_action(deck, hp=62, max_hp=62,
                                       archetype="demolition")
    assert action == "upgrade"
    assert loader.get_card(target).role == "payoff"      # workshop over toss


def test_upgraded_ids_flow_through_metrics_unchanged():
    """archetype_shares must read mine_toss+ exactly like mine_toss."""
    starter = [loader.get_card(c) for c in loader.starting_deck("klee")]
    plain = starter + [loader.get_card("mine_toss")]
    smithed = starter + [loader.get_card("mine_toss+")]
    assert draft.archetype_shares(plain) == draft.archetype_shares(smithed)


def test_unappliable_upgrades_never_chosen_at_rest():
    deck = loader.starting_deck("klee") + ["catalytic_conversion"]
    # All on-plan reaction candidates for this deck are the unappliable
    # one; the policy must fall through rather than burn a rest on it.
    action, target = model.rest_action(deck, hp=62, max_hp=62,
                                       archetype="reaction")
    assert (action, target) != ("upgrade", "catalytic_conversion")
