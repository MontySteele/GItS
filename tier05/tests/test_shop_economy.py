"""Shop node ($) + gold economy (run-model rework §5, Economy phase).

The load-bearing proof the task asks for: GOLD FLOWS -- it rises on a won
fight (and treasure) and falls on a shop buy. Plus the ownership guard (shop
stock is the character's own, companion-free pool) and the removal policy
(fires only on a known-dead card; rising price).

SEEN-TO-FAIL (hard rule 7): each lock fails against the pre-Economy stub.
  - `test_run_gold_rises_on_wins_and_falls_on_buy`: the stub left gold
    untouched at the shop, so the buy run would equal the skip run (269) and
    the `== skip - spent` identity (89) would fail.
  - `test_removal_removes_a_known_dead_card`: the stub bought nothing, so the
    dead card would still be in the deck and `removal_uses` would stay 0.
  - `test_no_removal_on_clean_deck` is the negative control: with the REAL
    dead-card detector and Klee's all-upgradable basics, nothing is removed --
    proving the removal is gated on deadness, not just on having gold.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card, CombatState
from tier05 import draft, model, rewards, shop


@pytest.fixture(autouse=True)
def _single_act(monkeypatch):
    """§10 re-stamp: this suite asserts ACT-1 cadence totals (7 fights, one
    shop/treasure, income 329). Pin the registry to act 1 so registering
    acts 2-3 never silently doubles the counts under test."""
    monkeypatch.setattr(C, "RUN_ACTS", C.RUN_ACTS[:1])

HIT = 8


def _win_fights(player, enemies, pilot, seed):
    """Win every fight taking a fixed hit -- isolates economy flow from
    combat noise, same trick as the Burning Blood run-layer test."""
    player.hp = max(1, player.hp - HIT)
    for e in enemies:
        e.hp = 0
    return CombatState(player=player, enemies=enemies,
                       rng=random.Random(seed))


def _skip(rng, deck, offers, archetype):
    return None


# --- ownership guard: own pool, never a companion or another character ---

def test_shop_offers_only_owned_noncompanion_cards():
    owned = {c.id for cs in rewards.character_pool("klee").values()
             for c in cs}
    for s in range(200):
        for c in shop.shop_offer(random.Random(s), "klee"):
            assert c.id in owned              # from klee's own draft pool
            assert not c.is_companion         # never a companion
            assert c.character == "klee"      # never another character's card


# --- gold flow: rises on a win/treasure, falls on a buy ---

def test_run_gold_rises_on_wins_and_falls_on_buy(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_fights)
    # Skip policy: wins all 7 fights + treasure, buys nothing -> pure income.
    # 99 start + N 10*4 + E 25*2 + B 100 + treasure 40 = 329 (boss pays the
    # §10.1 act-transition 100 as of RUNTEMPLATE v4; was 40 / total 269).
    r_skip = model.run_one("klee", "demolition", "demolition", _skip, 1)
    assert r_skip.won
    assert r_skip.gold > C.GOLD_START         # gold ROSE on wins + treasure
    assert r_skip.gold == 329
    assert r_skip.shop == []                   # nothing bought

    # Same wins, but the assigned policy spends at the shop. rng consumption
    # is identical (policies draw no rng), so income is identical; the only
    # delta is the spend -- gold FELL by exactly the purchase total.
    r_buy = model.run_one("klee", "demolition", "demolition",
                          draft.assigned_policy, 1)
    assert r_buy.won
    card_buys = [p for p in r_buy.shop if p["buy"] == "card"]
    assert card_buys                           # the policy bought >=1 card
    spent = sum(p["price"] for p in r_buy.shop)
    assert spent > 0
    assert r_buy.gold == r_skip.gold - spent   # gold fell exactly by spend
    # every bought card actually entered the deck
    for p in card_buys:
        assert p["id"] in r_buy.deck_ids


# --- buy policy reuses the draft valuation, gated by gold ---

def test_buys_a_card_the_policy_would_draft(monkeypatch):
    monkeypatch.setattr(shop, "shop_offer",
                        lambda rng, ch, n=C.SHOP_CARD_OFFERS:
                        [loader.get_card("mine_toss")])
    deck = loader.starting_deck("klee")
    out = shop.visit_shop(random.Random(0), "klee", deck, 300,
                          "demolition", draft.assigned_policy)
    assert out.purchases == [{"buy": "card", "id": "mine_toss",
                              "price": C.SHOP_CARD_PRICE}]
    assert out.gold == 300 - C.SHOP_CARD_PRICE
    assert out.deck_ids.count("mine_toss") == deck.count("mine_toss") + 1


def test_no_buy_when_gold_short(monkeypatch):
    monkeypatch.setattr(shop, "shop_offer",
                        lambda rng, ch, n=C.SHOP_CARD_OFFERS:
                        [loader.get_card("mine_toss")])
    deck = loader.starting_deck("klee")
    out = shop.visit_shop(random.Random(0), "klee", deck,
                          C.SHOP_CARD_PRICE - 1, "demolition",
                          draft.assigned_policy)
    assert out.purchases == []                 # can't afford it
    assert out.gold == C.SHOP_CARD_PRICE - 1
    assert out.deck_ids == deck


def test_skip_policy_buys_nothing(monkeypatch):
    monkeypatch.setattr(shop, "shop_offer",
                        lambda rng, ch, n=C.SHOP_CARD_OFFERS:
                        [loader.get_card("mine_toss")])
    out = shop.visit_shop(random.Random(0), "klee",
                          loader.starting_deck("klee"), 300, "demolition",
                          _skip)
    assert out.purchases == []                 # policy skips -> no buy


# --- removal: only a known-dead card, rising price ---

def _fab(**kw):
    kw.setdefault("name", "x")
    kw.setdefault("cost", 1)
    kw.setdefault("type", "skill")
    return Card(**kw)


def test_is_known_dead_classifier():
    # Curse tag -> dead.
    assert shop.is_known_dead(_fab(id="c", tags=["curse"]))
    # Real Klee basics are upgradable -> NOT dead (clean deck stays clean).
    assert not shop.is_known_dead(loader.get_card("kaboom"))
    # An already-upgraded basic is spent, not filler -> NOT dead.
    assert not shop.is_known_dead(loader.get_card("kaboom+"))


def test_removal_removes_a_known_dead_card(monkeypatch):
    monkeypatch.setattr(shop, "shop_offer",
                        lambda *a, **k: [])          # isolate removal
    # Treat a real deck id as dead so a REAL card leaves the deck end-to-end.
    monkeypatch.setattr(shop, "is_known_dead", lambda c: c.id == "kaboom")
    deck = loader.starting_deck("klee")              # 4x kaboom
    out = shop.visit_shop(random.Random(0), "klee", deck, 300,
                          "demolition", _skip, removal_uses=0)
    assert out.purchases == [{"buy": "removal", "id": "kaboom",
                              "price": C.SHOP_REMOVAL_PRICE}]
    assert out.deck_ids.count("kaboom") == deck.count("kaboom") - 1
    assert out.removal_uses == 1
    # Rising price: the Nth removal costs base + N*step.
    out2 = shop.visit_shop(random.Random(0), "klee", deck, 300,
                           "demolition", _skip, removal_uses=2)
    assert out2.purchases[0]["price"] == (C.SHOP_REMOVAL_PRICE
                                          + 2 * C.SHOP_REMOVAL_PRICE_STEP)


def test_no_removal_on_clean_deck(monkeypatch):
    # Negative control with the REAL detector: Klee's basics are all
    # upgradable, so nothing is dead and no removal is bought even flush.
    monkeypatch.setattr(shop, "shop_offer", lambda *a, **k: [])
    deck = loader.starting_deck("klee")
    out = shop.visit_shop(random.Random(0), "klee", deck, 300,
                          "demolition", _skip)
    assert out.purchases == []
    assert out.deck_ids == deck


def test_no_removal_when_dead_card_unaffordable(monkeypatch):
    monkeypatch.setattr(shop, "shop_offer", lambda *a, **k: [])
    monkeypatch.setattr(shop, "is_known_dead", lambda c: c.id == "kaboom")
    deck = loader.starting_deck("klee")
    out = shop.visit_shop(random.Random(0), "klee", deck,
                          C.SHOP_REMOVAL_PRICE - 1, "demolition", _skip)
    assert out.purchases == []                 # dead card present but broke
    assert out.deck_ids == deck


# --- treasure relic slot is a no-op stub (§1) ---

def test_treasure_relic_slot_is_a_noop_stub():
    deck = loader.starting_deck("klee")
    before = list(deck)
    assert shop.grant_treasure_relic("klee", deck) is None
    assert deck == before                      # the stub grants nothing
