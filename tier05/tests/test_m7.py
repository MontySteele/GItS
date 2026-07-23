"""M7: rest-site smithing in the run model."""

from tier0.content import loader, upgrades
from tier05 import draft, model


def test_runs_rest_coherently_and_stay_deterministic():
    """DRAFTER_VERSION 5 revision: both template rests directly precede an
    E/B fight, so the pre-fight lookahead heals every bruised (<90%)
    arrival and smithing fires only on near-full ones. The M7 'healthy
    rests smith' contract lives on in test_upgrade_prefers_on_plan_payoffs
    (unit) -- here we assert rests act, smithed ids resolve, and runs
    replay deterministically."""
    rs = model.run_many("klee", "demolition", "demolition",
                        draft.assigned_policy, runs=30, seed=11)
    actions = [t for r in rs for t in r.rests]
    assert actions
    assert [t for t in actions if t[1] == "heal"], \
        "v5 world: bruised pre-E/B rests must heal"
    # Every smithed id (if any run arrived near-full) must resolve.
    for _, _, cid in (t for t in actions if t[1] == "upgrade"):
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


def test_adaptive_runs_are_label_independent_including_rests():
    """Review-workflow regression: M7 smithing consulted the assigned
    label, so adaptive runs (defined to ignore it) diverged by label at
    rest sites. Pilot held fixed so the only remaining label channel --
    the archetype-matched pilot -- cannot mask the rest channel."""
    decks = {}
    for label in ("demolition", "spark", "reaction"):
        rs = model.run_many("klee", label, "generic",
                            draft.adaptive_policy, runs=25, seed=1000)
        decks[label] = [r.deck_ids for r in rs]
    assert decks["demolition"] == decks["spark"] == decks["reaction"]


def test_unappliable_upgrades_never_chosen_at_rest():
    """Derived from the upgrade engine, NOT hard-coded card names. The
    original hard-coded catalytic_conversion as forever-unappliable; R37
    then made that upgrade real and stranded the assertion (caught by the
    first full-suite run -- the cross-tier coupling the full-suite gate
    exists for). Whatever UNAPPLIABLE holds today, a rest must never
    smith it -- and the next disposition ruling can't strand this again."""
    assert upgrades.UNAPPLIABLE, \
        "UNAPPLIABLE is empty -- retire this test with a ruling, not a skip"
    for cid in sorted(upgrades.UNAPPLIABLE):
        # Coherence: unappliable ids must be real sheet entries, or the
        # set is guarding against nothing.
        assert cid in upgrades._upgrade_index(), cid
        deck = loader.starting_deck("klee") + [cid]
        for plan in ("demolition", "spark", "reaction", "generic"):
            action, target = model.rest_action(deck, hp=62, max_hp=62,
                                               archetype=plan)
            assert (action, target) != ("upgrade", cid), plan
