"""EB-183 -- the per-companion half of R216 D, asked at the FUNNEL.

QUARANTINED (R213 E1, prototype surface only). R216 D deferred Muster's Charge
subsidy into E1 rather than settling it, in these words: *a Mustered Companion
costs 1 less, Exhausts, and pays 1 Charge, so blocking with one also advances
Kokomi's finisher*. That sentence has TWO readings and slice 2 could only ask
one of them.

  SLICE 2's reading -- put the subsidy's SIGN on a card. The order SPENDS
  Charge instead of paying it (`proto_charge_muster_price`). That lives in an
  effect list, and it retired with the rest of slice 2 under R227 / M67 (1).

  THIS reading -- the recruits of a PAID order pay no Charge when they
  Exhaust. That is not an effect list at all: it is a property of the exhaust
  FUNNEL, and it wants a flag on the recruit plus a check where the wage is
  paid. Nothing in slice 2 could express it, which is why EB-183 was minted
  instead of being smuggled into a card row.

THE THREE THINGS THESE TESTS PIN:

  1. A flagged recruit exhausts FREE -- no Charge, and the Burst particle is
     untouched, because R216 D's sentence is about Charge and an arm that
     moved two meters would be unattributable.
  2. An UNFLAGGED recruit pays the shipped wage, on the same board, from the
     same pool, through the same funnel. That is the pair's control.
  3. THE FLAG NEVER ESCAPES THE GATE. No shipped card carries the op key, the
     stamp is refused where the order did not actually pay the cost down, and
     a shipped conscript play is byte-identical with the branch in place.
"""

import copy
import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, refpowers
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy


def kokomi_state(seed=0):
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


def order(**kw):
    """A Muster order, as a bare card carrying one conscript op."""
    fx = dict(op="conscript", amount=1)
    fx.update(kw)
    return Card(id="test_order", name="order", cost=1, type="skill",
                character="kokomi", effects=[fx])


def _fodder(n):
    """Cards a transform-mode Muster is allowed to take."""
    return [Card(id=f"fodder_{i}", name="f", cost=1, type="skill",
                 character="kokomi") for i in range(n)]


# --- 1. the flagged recruit exhausts free -----------------------------------

def test_waived_recruit_pays_no_charge_on_exhaust():
    st = kokomi_state()
    st.player.hand = _fodder(1)
    effects.resolve_card(st, order(subsidy="waived"))
    (recruit,) = [c for c in st.player.hand if c.conscripted]
    assert recruit.muster_subsidised is True

    refpowers.exhaust_card(st, recruit)
    assert st.player.charge == 0


def test_waived_recruit_still_pays_the_burst_particle():
    """CHARGE ONLY. R216 D's sentence is about the finisher meter; the Burst
    economy is a second question and this arm does not ask it."""
    st = kokomi_state()
    st.player.hand = _fodder(1)
    effects.resolve_card(st, order(subsidy="waived"))
    (recruit,) = [c for c in st.player.hand if c.conscripted]

    refpowers.exhaust_card(st, recruit)
    assert st.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST


def test_waived_recruit_still_counts_as_a_muster_rotation():
    """C5's separate conscript-income bucket is a count of ROTATIONS, and the
    recruit did rotate. What the arm moves is the AMOUNT, not the kind."""
    st = kokomi_state()
    st.player.hand = _fodder(1)
    effects.resolve_card(st, order(subsidy="waived"))
    (recruit,) = [c for c in st.player.hand if c.conscripted]

    refpowers.exhaust_card(st, recruit)
    assert any(ev["event"] == "burst_income"
               and ev["source"] == "exhaust_muster" for ev in st.log)


# --- 2. the control: an unflagged recruit pays -------------------------------

def test_unwaived_recruit_pays_the_shipped_wage():
    st = kokomi_state()
    st.player.hand = _fodder(1)
    effects.resolve_card(st, order())
    (recruit,) = [c for c in st.player.hand if c.conscripted]
    assert recruit.muster_subsidised is False

    refpowers.exhaust_card(st, recruit)
    assert st.player.charge == C.CHARGE_PER_EXHAUST


def test_explicit_paid_is_the_shipped_wage():
    """`subsidy: paid` is the default spelled out, not a third behaviour."""
    st = kokomi_state()
    st.player.hand = _fodder(1)
    effects.resolve_card(st, order(subsidy="paid"))
    (recruit,) = [c for c in st.player.hand if c.conscripted]

    refpowers.exhaust_card(st, recruit)
    assert st.player.charge == C.CHARGE_PER_EXHAUST


def test_a_pair_of_orders_differs_only_in_the_wage():
    """The matched pair, in one assertion: the SAME seed, the same pool, the
    same recruit, and the only thing that moves is the Charge."""
    banks = {}
    for waived in (False, True):
        st = kokomi_state(seed=13)
        st.player.hand = _fodder(1)
        fx = {"subsidy": "waived"} if waived else {}
        effects.resolve_card(st, order(**fx))
        (recruit,) = [c for c in st.player.hand if c.conscripted]
        recruit_id = recruit.id
        refpowers.exhaust_card(st, recruit)
        banks[waived] = (recruit_id, st.player.charge,
                         st.player.burst_energy)
    assert banks[False][0] == banks[True][0]          # same recruit
    assert banks[False][2] == banks[True][2]          # same Burst
    assert banks[False][1] == C.CHARGE_PER_EXHAUST
    assert banks[True][1] == 0


# --- 3. the flag never escapes the gate -------------------------------------

def test_no_shipped_card_carries_the_subsidy_key():
    """THE QUARANTINE, read off the sheets rather than asserted. The op key is
    the only door to the stamp, so a shipped row carrying it would be the arm
    shipping by accident."""
    offenders = []
    for card in loader._card_index().values():
        for fx in (card.effects or []):
            if fx.get("op") == "conscript" and "subsidy" in fx:
                offenders.append(card.id)
    assert offenders == []


def test_unknown_subsidy_value_raises():
    """A typo must not read as the control. `subsidy: waved` is a stop, not a
    silent 'paid' -- an arm that quietly becomes its own control grades as a
    null result and nothing in the record would say why."""
    with pytest.raises(ValueError):
        effects._conscript_subsidy_waived({"op": "conscript",
                                           "subsidy": "waved"})


def test_waiver_is_refused_when_the_order_paid_nothing():
    """DERIVED, not picked (R212): 'a PAID order' means the order actually put
    the recruit below its printed cost. A `cost_override` landing ON the
    printed number moved no energy, so it bought no waiver, and the doubt
    always resolves toward the SHIPPED wage."""
    st = kokomi_state()
    st.player.hand = _fodder(1)
    pool = loader.companion_pool("inazuma")
    printed = {c.id: c.cost for c in pool}

    effects.resolve_card(st, order(subsidy="waived", cost_override=99))
    (recruit,) = [c for c in st.player.hand if c.conscripted]
    assert recruit.cost > printed[recruit.id]
    assert recruit.muster_subsidised is False

    refpowers.exhaust_card(st, recruit)
    assert st.player.charge == C.CHARGE_PER_EXHAUST


def test_shipped_muster_play_is_unchanged_by_the_branch():
    """FLAG-OFF BYTE IDENTITY, on the shipped order that R216 D was written
    about. `mass_mobilization` conscripts 2 and gains 1 Charge; with the
    branch in place and no op key on it, the bank after two rotations is
    exactly the shipped number."""
    st = kokomi_state(seed=3)
    st.player.hand = _fodder(3)
    st.player.energy = 3
    card = copy.deepcopy(loader.get_card("mass_mobilization"))
    effects.resolve_card(st, card)
    recruits = [c for c in st.player.hand if c.conscripted]
    assert len(recruits) == 2
    for recruit in recruits:
        assert recruit.muster_subsidised is False
        refpowers.exhaust_card(st, recruit)
    assert st.player.charge == 1 + 2 * C.CHARGE_PER_EXHAUST
