"""EB-118 with the switch ON: the two evaluators on constructed boards.

THIS IS NOW THE SHIPPED WORLD. Written during the staging window, this file's
`policies_on` fixture was the only place in the suite where the switch was ever
True -- that was the staging contract, and test_eb118_switch_off held the other
half of it. **The Phase-2A flip (`POLICY_VERSION` 8, `PILOT_WEIGHTS_VERSION` 3,
2026-08-24) turned the switch on for good**, so the fixture no longer changes
anything.

It is KEPT rather than deleted, and for a reason that outlives the flip: a test
that asserts a decision should say which world it is asserting in, not inherit
one from a module default that has now moved once. Its sibling file states the
off side the same way. So the pins below -- `test_the_chooser_inverts_the_
placeholder` above all -- read exactly as they did, and now describe what
ships instead of what was staged.

Boards are built to vary ONE thing. Where a term is not what a test is about
it is neutralised on both sides (`bomb_suppression_spent=True` on both enemies,
identical intents), so a pass here is a statement about the term named in the
test and not about the sum.
"""

import pytest

from tier0.engine import effects
from tier0.engine.state import Bomb, Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state

PLACE_5 = {"op": "place_bomb", "amount": 1, "target": "enemy",
           "bomb_damage": 5}


@pytest.fixture
def policies_on(monkeypatch):
    """A no-op since the Phase-2A flip, and deliberately still here: it names
    the world each test asserts in rather than inheriting the default."""
    monkeypatch.setattr(policy, "PILOT_POLICIES_ENABLED", True)


def _enemy(hp, name, spent=True, bombs=()):
    e = make_enemy(hp=hp, name=name)
    e.bomb_suppression_spent = spent
    e.bombs = [Bomb(damage=d, element="pyro", turn_placed=0) for d in bombs]
    return e


def _skill(cid, cost, effs=None, **kw) -> Card:
    return Card(id=cid, name=cid, cost=cost, type="skill",
                effects=effs or [], **kw)


# --- (1) bomb placement ----------------------------------------------------

def test_placement_refuses_the_lethal_waste(policies_on):
    """The lowest-HP aim throws 5 damage at a 3 HP body and loses 2 of it.
    The whole point of the pass: lowest HP is a targeting heuristic, not a
    decision about where the damage lands."""
    low, high = _enemy(3, "low"), _enemy(60, "high")
    state = make_state([low, high])

    assert policy.bomb_placement_target(state, PLACE_5) is high


def test_placement_concentrates_when_the_target_lives_to_detonate(policies_on):
    """A pile detonates as one event; a second bomb on a body that survives to
    receive it is worth more than the same bomb on a clean one. Both enemies
    are past their suppression latch so only the pile differs, and the stacked
    one is the HIGHER-HP body -- so the old aim picks the clean target and the
    test is a statement about concentration rather than about HP order."""
    stacked, clean = _enemy(62, "stacked", bombs=(5,)), _enemy(60, "clean")
    state = make_state([stacked, clean])

    assert effects._pick_targets(state, "enemy") == [clean]
    assert policy.bomb_placement_target(state, PLACE_5) is stacked


def test_concentration_stops_at_the_pile_that_is_already_lethal(policies_on):
    """The same stack, on a body its own pile already kills: every point of
    the new bomb is waste, and the clean target wins by the full 5."""
    dead_already = _enemy(6, "dead_already", bombs=(10,))
    clean = _enemy(60, "clean")
    state = make_state([dead_already, clean])

    assert policy.bomb_placement_target(state, PLACE_5) is clean


def test_placement_reads_the_suppression_latch(policies_on):
    """Arming an enemy that has not spent its latch costs its next attack the
    Weak rate. Equal intents, no piles, and the unspent body is the HIGHER-HP
    one, so the old aim picks the other and the control read is the only thing
    that can be moving this pick."""
    unspent = _enemy(62, "unspent", spent=False)
    spent = _enemy(60, "spent")
    state = make_state([unspent, spent])

    assert effects._pick_targets(state, "enemy") == [spent]
    assert policy.bomb_placement_target(state, PLACE_5) is unspent


def test_a_detonator_in_hand_prices_a_sub_lethal_pop(policies_on):
    """A `detonate` in hand pops the aimed pile THIS turn. Worth adding to
    only when the pop is lethal (the rule `_expected_damage` already applies);
    sub-lethal, the policy places elsewhere -- and without the detonator in
    hand the same board concentrates."""
    stacked, clean = _enemy(60, "stacked", bombs=(4,)), _enemy(61, "clean")
    state = make_state([stacked, clean])
    assert policy.bomb_placement_target(state, PLACE_5) is stacked

    state.player.hand = [_skill("boom", 1, [{"op": "detonate",
                                            "target": "enemy"}])]
    assert policy.bomb_placement_target(state, PLACE_5) is clean


def test_placement_ties_fall_back_to_the_pre_policy_pick(policies_on):
    """Two boards the policy has nothing to say about resolve the way they
    always did: lowest HP, then board order."""
    a, b = _enemy(40, "a"), _enemy(30, "b")
    state = make_state([a, b])

    assert policy.bomb_placement_target(state, PLACE_5) is b


def test_the_op_places_through_the_policy_and_reprices_per_bomb(policies_on):
    """End to end, and the multi-bomb case: the second bomb sees the pile the
    first one built, so a two-bomb placement concentrates."""
    low, high = _enemy(3, "low"), _enemy(60, "high")
    state = make_state([low, high])
    effects._op_place_bomb(state, {"op": "place_bomb", "amount": 2,
                                   "target": "enemy", "bomb_damage": 5},
                           _skill("probe", 1))

    assert low.bombs == []
    assert len(high.bombs) == 2


def test_random_placement_is_untouched_by_the_policy(policies_on):
    """`random_enemy` is a variance profile, not a decision. With the switch
    on it still rolls -- this seed lands on the 3 HP body, which is exactly
    the placement the policy refuses when it IS consulted."""
    low, high = _enemy(3, "low"), _enemy(60, "high")
    state = make_state([low, high], seed=1)
    effects._op_place_bomb(state, {"op": "place_bomb", "amount": 1,
                                   "target": "random_enemy",
                                   "bomb_damage": 5}, _skill("probe", 1))

    assert len(low.bombs) == 1
    assert high.bombs == []


# --- (2) exhaust selection -------------------------------------------------

def test_the_chooser_inverts_the_placeholder(policies_on):
    """THE pin. `_worst_card` reads highest-cost non-Attack and so exhausts
    the 2-cost blocker while keeping a 0-cost card that does nothing. The
    chooser weighs what is lost, and loses the dud."""
    dud = _skill("dud", 0)
    payoff = _skill("payoff", 2, [{"op": "block", "amount": 12}])
    state = make_state([make_enemy()])
    pool = [dud, payoff]

    assert effects._worst_card(pool) is payoff          # what it used to pick
    assert policy.exhaust_victim(state, pool) is dud


def test_junk_goes_first_where_the_pool_still_holds_any(policies_on):
    """A Status is negative future value -- it costs a draw every shuffle.
    Reachable only for pools Kokomi's rotation law does not govern; post-C11
    her pool never contains one."""
    junk = Card(id="burn", name="Burn", cost=0, type="status", rarity="status",
                effects=[])
    plain = _skill("plain", 1, [{"op": "block", "amount": 4}])
    state = make_state([make_enemy()])

    assert policy.exhaust_victim(state, [plain, junk]) is junk


def test_cost_efficiency_is_a_discount_not_a_ranking(policies_on):
    """Same card at two costs: the expensive copy returns its value more
    slowly, so it is the one spent. Where cost is the ONLY difference the
    policy agrees with the placeholder -- it is a refinement of that pick,
    not a blind flip of it."""
    cheap = _skill("cheap", 1, [{"op": "damage", "amount": 12}])
    dear = _skill("dear", 3, [{"op": "damage", "amount": 12}])
    state = make_state([make_enemy(hp=200)])

    assert policy.exhaust_victim(state, [cheap, dear]) is dear
    assert effects._worst_card([cheap, dear]) is dear


def test_a_self_exhausting_card_is_cheaper_to_lose(policies_on):
    """It was leaving the deck on its next play anyway: only the one use is
    lost, which is what the discount prices."""
    keeper = _skill("keeper", 1, [{"op": "damage", "amount": 10}])
    burner = _skill("burner", 1, [{"op": "damage", "amount": 10}],
                    exhaust=True)
    state = make_state([make_enemy(hp=200)])

    assert policy.exhaust_victim(state, [keeper, burner]) is burner


def test_the_payout_hook_is_identity_blind_by_default(policies_on):
    """No shipped grammar reads the victim's identity, so the default hook is
    a constant and cannot move the ranking. The interface is the deliverable:
    an identity-sensitive payout arrives as a parameter, and here one flips
    the pick onto the card the blind chooser was keeping."""
    dud = _skill("dud", 0)
    payoff = _skill("payoff", 2, [{"op": "block", "amount": 12}])
    state = make_state([make_enemy()])
    pool = [dud, payoff]

    assert policy.identity_blind_payout(state, None, dud) == 0.0
    assert policy.exhaust_victim(state, pool) is dud
    assert policy.exhaust_victim(
        state, pool, payout=lambda s, c, cand: 50.0 * (cand is payoff)
    ) is payoff


def test_the_op_exhausts_through_the_policy(policies_on):
    """End to end: same board as the inversion, through the engine's own
    chosen branch."""
    dud = _skill("dud", 0)
    payoff = _skill("payoff", 2, [{"op": "block", "amount": 12}])
    state = make_state([make_enemy()])
    state.player.hand = [dud, payoff]
    effects._op_exhaust_from(state, {"op": "exhaust_from", "amount": 1,
                                     "select": "chosen"}, _skill("src", 1))

    assert [c.id for c in state.player.exhaust_pile] == ["dud"]
    assert [c.id for c in state.player.hand] == ["payoff"]


def test_a_random_exhaust_is_not_a_decision(policies_on):
    """The unchosen branch still rolls with the switch on: the policy is
    scoped to a choice the player would actually make."""
    state = make_state([make_enemy()], seed=3)
    state.player.hand = [_skill("a", 0), _skill("b", 3)]
    before = state.rng.getstate()
    effects._op_exhaust_from(state, {"op": "exhaust_from", "amount": 1},
                             _skill("src", 1))

    assert state.rng.getstate() != before
