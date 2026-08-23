"""Kokomi's ROTATION LAW ([USER] ruling, 2026-08-23).

"Whenever one of YOUR cards is Exhausted" reads literally: a Status or a
Curse is never one of her cards. Three seams carry the law and this file
pins all three, plus the two things that must NOT move:

  1. Muster (`conscript`) never transforms a Status or a Curse.
  2. Her chosen Exhaust never offers a Status or a Curse (the unfiltered
     pool under her relic hook drops them); an explicit `filter:` opts a
     card back in, which is Dodge Roll's shape and the design space for a
     dedicated Uncommon/Rare.
  3. The Charge funnel pays nothing for a Status/Curse exhaust by ANY route
     (Ethereal, a played Dazed, the ward's random draw-pile pick).

Unchanged: Klee's Dodge Roll (`filter: status`) still eats a Status, and a
player WITHOUT the relic hook (real_ironclad True Grit+) keeps the any-card
pool -- the law is hers, not the engine's.

The retired behaviour was kickoff v1 §2.1's "statuses/curses count too
(accepted quirk)", which made her uniquely status-resistant for free.
"""
import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, refpowers
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy


def kokomi_state(seed=0):
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


def kokomi_card(**kw):
    d = dict(id="kokomi_test", name="t", cost=0, type="skill",
             character="kokomi")
    d.update(kw)
    return Card(**d)


def a_curse():
    return loader.get_card("curse_guilty")      # rarity curse, unplayable


def a_status():
    return loader.get_card("confiscated")       # rarity status


# --- 0. the predicate itself ---

def test_is_junk_is_status_or_curse_only():
    assert a_curse().is_junk and a_status().is_junk
    assert not kokomi_card().is_junk
    assert not loader.get_card("gorou_war_banner").is_junk


# --- 1. Muster ---

def test_muster_never_transforms_a_status_or_curse():
    st = kokomi_state()
    curse, status = a_curse(), a_status()
    st.player.hand = [curse, status]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "conscript", "amount": 1}]))
    assert any(ev["event"] == "conscript_whiffed" for ev in st.log)
    assert st.player.hand == [curse, status]


def test_muster_still_takes_her_own_card_beside_junk():
    st = kokomi_state()
    chaff = kokomi_card(id="chaff", effects=[{"op": "block", "amount": 1}])
    st.player.hand = [a_curse(), chaff, a_status()]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "conscript", "amount": 1}]))
    assert sum(1 for c in st.player.hand if c.is_companion) == 1
    assert sum(1 for c in st.player.hand if c.is_junk) == 2


# --- 2. chosen Exhaust ---

def test_chosen_exhaust_never_offers_junk_under_her_law():
    st = kokomi_state()
    curse, status = a_curse(), a_status()
    st.player.hand = [curse, status]
    burner = kokomi_card(
        id="burner",
        effects=[{"op": "exhaust_from", "amount": 1, "select": "chosen"}])
    st.player.hand.append(burner)
    st.player.energy = 3
    combat.play_card(st, burner)
    # Nothing was eligible: both junk cards are still in hand, none in the
    # exhaust pile beyond the (non-Exhaust) burner's own result pile.
    assert curse in st.player.hand and status in st.player.hand
    assert not any(c.is_junk for c in st.player.exhaust_pile)
    assert st.player.charge == 0


def test_chosen_exhaust_picks_her_card_over_junk():
    st = kokomi_state()
    fodder = kokomi_card(id="fodder", cost=2,
                         effects=[{"op": "block", "amount": 1}])
    st.player.hand = [a_curse(), fodder, a_status()]
    burner = kokomi_card(
        id="burner",
        effects=[{"op": "exhaust_from", "amount": 1, "select": "chosen"}])
    st.player.hand.append(burner)
    st.player.energy = 3
    combat.play_card(st, burner)
    assert fodder in st.player.exhaust_pile
    assert st.player.charge == C.CHARGE_PER_EXHAUST


def test_explicit_status_filter_still_eats_a_status():
    """Dodge Roll's shape: `filter: status` is the opt-in and is untouched
    by the law -- it is exactly how a dedicated junk-eater is written."""
    st = kokomi_state()
    status = a_status()
    st.player.hand = [status, kokomi_card(id="keep")]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "exhaust_from", "amount": 1, "filter": "status"}]))
    assert status in st.player.exhaust_pile


def test_law_is_hers_not_the_engines():
    """A player without the relic hook keeps the any-card pool: real
    Ironclad's True Grit+ may still exhaust a Curse."""
    p = loader.build_player("ref_ironclad")
    st = CombatState(player=p, enemies=[make_enemy(hp=50)],
                     rng=random.Random(0))
    curse = a_curse()
    st.player.hand = [curse]
    effects.resolve_card(st, Card(
        id="true_grit_plus", name="t", cost=0, type="skill",
        effects=[{"op": "exhaust_from", "amount": 1, "select": "chosen"}]))
    assert curse in st.player.exhaust_pile


# --- 3. the Charge funnel ---

def test_funnel_pays_nothing_for_a_curse_by_any_route():
    st = kokomi_state()
    p = st.player
    refpowers.exhaust_card(st, a_curse())
    refpowers.exhaust_card(st, a_status())
    assert p.charge == 0
    assert p.burst_energy == 0
    assert not any(ev["event"] == "gain_charge" for ev in st.log)
    # ...and her own card still pays, so the funnel itself is alive.
    refpowers.exhaust_card(st, kokomi_card())
    assert p.charge == C.CHARGE_PER_EXHAUST
    assert p.burst_energy == C.KOKOMI_BURST_PER_EXHAUST


def test_ethereal_curse_pays_nothing():
    """Clumsy exhausts itself at end of turn (Ethereal); that route is the
    one the kickoff's 'accepted quirk' line was about. Driven through the
    real turn loop so the ethereal sweep, not a direct funnel call, is what
    is under test."""
    p = loader.build_player("kokomi")
    p.draw_pile = []
    p.hand = [loader.get_card("curse_clumsy")]
    state = combat.run_fight(
        p, [make_enemy(hp=1, intents=[{"kind": "block", "amount": 0}])],
        lambda s: None, seed=0)
    assert any(c.id == "curse_clumsy" for c in state.player.exhaust_pile)
    assert not any(ev["event"] == "gain_charge" for ev in state.log)
