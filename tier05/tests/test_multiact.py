"""Multi-act machinery (run-model rework §10, Pass 1, RATIFIED 2026-07-23).

The registry currently defines Act 1 only (acts 2-3 land in Passes 2-3), so
these tests register a SYNTHETIC second act -- Act 1's pool under a 2-easy
spec -- to exercise the act loop, the boundary event (forced-Rare companion
slot, Ancient full heal + relic pick) and the carryover invariants on
machinery the default single-act world does not yet reach."""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import CombatState
from tier05 import acts, draft, model
from tier05 import relics as relic_pool

SEED = 77
CHIP = 4          # flat HP loss per stubbed fight -- every fight is won


def _two_acts(monkeypatch):
    """Register a synthetic 2nd act: Act 1's pool file, StS2's 2-easy rule."""
    monkeypatch.setattr(
        C, "RUN_ACTS",
        (C.RUN_ACTS[0],
         {"id": "act2_test", "pool": "act1_pool.yaml", "easy_fights": 2}))


def _chip_win(player, enemies, pilot, seed):
    player.hp -= CHIP
    for e in enemies:
        e.hp = 0
    return CombatState(player=player, enemies=enemies,
                       rng=random.Random(seed))


def _skip(rng, deck, offers, archetype):
    return None


# --- the act loop + boundary event -----------------------------------------

def test_two_act_run_walks_both_acts_and_heals_at_the_boundary(monkeypatch):
    _two_acts(monkeypatch)
    monkeypatch.setattr(model, "run_fight", _chip_win)
    r = model.run_one("klee", "demolition", "demolition", _skip, SEED,
                      n_acts=2)
    mx = loader._character_index()["klee"]["hp"]

    assert r.won and r.n_acts == 2 and r.acts_completed == 2
    assert len(r.node_kinds) == 2 * len(C.RUN_NODE_TEMPLATE)
    assert len(r.hp_by_node) == len(r.node_kinds)
    # Act-boundary FULL heal (§10.1): the first fight of act 2 starts from
    # max HP, so it ends at exactly mx - CHIP. Without the heal it would
    # carry act 1's accumulated chip (hp_by_node[10] - CHIP, strictly less).
    boss1 = len(C.RUN_NODE_TEMPLATE) - 1
    # DRAFTER_VERSION 5: the pre-boss rest heals (lookahead), capping act-1
    # attrition at the boss's own chip -- but a carried wound would open
    # act 2 at mx - 2*CHIP, so the next line still proves the FULL heal.
    assert r.hp_by_node[boss1] <= mx - CHIP         # act 1 ended wounded
    assert r.hp_by_node[boss1 + 1] == mx - CHIP     # act 2 opened at full
    # Gold carryover: both acts' full income lands in one wallet -- start 99
    # + 2 * (N 10*4 + E 25*2 + B 100 + T 40) with nothing bought (§10.1 boss
    # pays the act-transition 100).
    assert r.gold == C.GOLD_START + 2 * 230


def test_boundary_reward_screen_forces_rare_companion_final_boss_none(
        monkeypatch):
    _two_acts(monkeypatch)
    monkeypatch.setattr(model, "run_fight", _chip_win)
    r = model.run_one("klee", "demolition", "demolition", _skip, SEED,
                      n_acts=2)
    boss1 = len(C.RUN_NODE_TEMPLATE) - 1
    final = 2 * len(C.RUN_NODE_TEMPLATE) - 1
    boundary = [d for d in r.decisions if d["node"] == boss1]
    assert len(boundary) == 1                       # non-final boss: a screen
    comps = [c for c in boundary[0]["offers"] if c.is_companion]
    assert comps                                    # slot present for Klee
    assert all(c.rarity == "rare" and c.star == 5 for c in comps)
    assert all(d["node"] != final for d in r.decisions)   # final boss: none


def test_boundary_card_offers_are_forced_rare(monkeypatch):
    """§10.1's boss drop is a choice-of-3 RARE CARDS (RUNTEMPLATE_VERSION 5).
    v4 forced only the companion slot -- a no-companion character got plain
    commons at the act transition (the Ironclad-0.6% diagnosis)."""
    _two_acts(monkeypatch)
    monkeypatch.setattr(model, "run_fight", _chip_win)
    r = model.run_one("klee", "demolition", "demolition", _skip, SEED,
                      n_acts=2)
    boss1 = len(C.RUN_NODE_TEMPLATE) - 1
    screen = next(d for d in r.decisions if d["node"] == boss1)
    cards = [c for c in screen["offers"] if not c.is_companion]
    assert len(cards) == C.REWARD_CARD_OFFERS
    assert all(c.rarity == "rare" for c in cards)
    # Ordinary (non-boundary) screens keep the native rarity roll: over the
    # rest of the run SOMETHING non-rare is offered.
    ordinary = [c for d in r.decisions if d["node"] != boss1
                for c in d["offers"] if not c.is_companion]
    assert any(c.rarity != "rare" for c in ordinary)


def test_boundary_grants_exactly_one_ancient_on_realistic_runs(monkeypatch):
    _two_acts(monkeypatch)
    monkeypatch.setattr(model, "run_fight", _chip_win)
    r = model.run_one("klee", "demolition", "demolition", _skip, SEED,
                      grant_relics=True, n_acts=2)
    ancients = [rid for rid in r.relics if rid in relic_pool.ancient_pool()]
    assert len(ancients) == 1          # one boundary -> one Ancient boon
    # Ordinary grant sites (Neow/treasure/elite/boss/shop) stay Common-pool:
    # nothing else in the haul comes from the ancient pool.
    assert all(rid in relic_pool.ancient_pool()
               or rid in relic_pool.common_pool()
               or rid in relic_pool.neow_pool() for rid in r.relics)


# --- per-act draw rules -----------------------------------------------------

def test_second_act_uses_its_own_easy_fights_rule(monkeypatch):
    _two_acts(monkeypatch)
    rng = random.Random(SEED)
    draw = acts.ActDraw(rng, 1)
    easy_ids = {e["id"] for e in acts.pools(1)["easy"]}
    hard_ids = {e["id"] for e in acts.pools(1)["hard"]}
    picks = [draw.encounter_for("N", rng)["id"] for _ in range(2)]
    assert set(picks) <= easy_ids and len(set(picks)) == 2
    assert draw.encounter_for("N", rng)["id"] in hard_ids   # 3rd N is HARD


# --- ancient pool machinery -------------------------------------------------

def test_ancient_offer_and_pick():
    pool_ids = sorted(relic_pool.ancient_pool())
    assert len(pool_ids) >= 6          # the ratified representative sample
    offer = relic_pool.ancient_offer(random.Random(3), [], "klee")
    assert len(offer) == 3 == len(set(offer))
    assert set(offer) <= set(pool_ids)
    # Static valuation: combat-start energy (10) > max-HP (5) > gold (2).
    pick = relic_pool.ancient_pick(
        ["signet_ring", "very_hot_cocoa", "looming_fruit"], "klee")
    assert pick == "very_hot_cocoa"
    # A held boon is never re-offered (one-time pickups).
    assert "very_hot_cocoa" not in relic_pool.unowned_ancient(
        ["very_hot_cocoa"], "klee")


# --- the real Hive registry (Pass 2) ----------------------------------------

def test_hive_pool_loads_and_boss_ops_are_wired():
    assert acts.n_acts() >= 2 and acts.easy_fights(1) == 2
    p = acts.pools(1)
    assert {e["id"] for e in p["easy"]} == \
        {"bowlbug_pod", "exoskeleton_trio", "tunneler"}
    assert len(p["elite"]) == 3
    assert {b["id"] for b in acts.boss_pool(1)} == \
        {"knowledge_demon", "kaiser_crab"}
    # Kaiser Crab: two claws, both carrying the Crab Rage §10.2 op.
    kaiser = next(b for b in acts.boss_pool(1) if b["id"] == "kaiser_crab")
    claws = acts.spawn(kaiser, random.Random(0))
    assert len(claws) == 2
    assert all(c.ally_death_buff == {"powers": {"strength": 6}, "block": 99}
               for c in claws)
    # Knowledge Demon: real HP, the heal op in his cycle, the dot Curse.
    kd = acts.spawn(next(b for b in acts.boss_pool(1)
                         if b["id"] == "knowledge_demon"), random.Random(0))[0]
    assert kd.hp == 379 and kd.is_boss
    kinds = [i["kind"] for i in kd.intents]
    assert "heal" in kinds
    assert any(i["kind"] == "debuff" and i["power"] == "dot"
               for i in kd.intents)
    # The signature Act-2 pressure exists: at least one injector per pool.
    hard_kinds = [i["kind"] for e in p["hard"]
                  for spec in e["enemies"] for i in spec["intents"]]
    assert "inject" in hard_kinds


def test_glory_pool_loads_with_phase_boss():
    assert acts.n_acts() == 3 and acts.easy_fights(2) == 2
    p = acts.pools(2)
    assert len(p["elite"]) == 3
    assert {b["id"] for b in acts.boss_pool(2)} == \
        {"test_subject", "aeonglass"}
    # Test Subject: the §10.2 phase op -- 100 -> 200 -> 300, fatal-exempt
    # until the last bar so Feed can never farm a phase-down.
    ts = acts.spawn(next(b for b in acts.boss_pool(2)
                         if b["id"] == "test_subject"), random.Random(0))[0]
    assert ts.hp == 100 and len(ts.phases) == 2
    assert not ts.counts_for_fatal
    assert ts.phases[-1]["hp"] == 300
    ag = acts.spawn(next(b for b in acts.boss_pool(2)
                         if b["id"] == "aeonglass"), random.Random(0))[0]
    assert ag.hp == 512 and not ag.phases and ag.counts_for_fatal
    assert any(i["kind"] == "inject" and i["status"] == "wither"
               for i in ag.intents)


def test_default_run_spans_all_registered_acts():
    r = model.run_one("klee", "demolition", "demolition",
                      draft.assigned_policy, 5)
    assert r.n_acts == acts.n_acts() == 3
    assert len(r.node_kinds) == 3 * len(C.RUN_NODE_TEMPLATE)


# --- n_acts contract --------------------------------------------------------

def test_n_acts_defaults_to_registry_and_is_bounds_checked(monkeypatch):
    _two_acts(monkeypatch)
    monkeypatch.setattr(model, "run_fight", _chip_win)
    r = model.run_one("klee", "demolition", "demolition", _skip, SEED)
    assert r.n_acts == 2               # default spans every registered act
    with pytest.raises(ValueError):
        model.run_one("klee", "demolition", "demolition", _skip, SEED,
                      n_acts=3)
    r1 = model.run_one("klee", "demolition", "demolition", _skip, SEED,
                       n_acts=1)       # the single-act instrument survives
    assert r1.n_acts == 1 and r1.won and r1.acts_completed == 1
    assert len(r1.node_kinds) == len(C.RUN_NODE_TEMPLATE)


def test_multiact_run_determinism(monkeypatch):
    _two_acts(monkeypatch)
    a = model.run_one("klee", "demolition", "demolition",
                      draft.assigned_policy, SEED, n_acts=2)
    b = model.run_one("klee", "demolition", "demolition",
                      draft.assigned_policy, SEED, n_acts=2)
    assert a.hp_by_node == b.hp_by_node
    assert a.deck_ids == b.deck_ids
    assert a.death_node == b.death_node
    assert a.acts_completed == b.acts_completed
    if a.death_node is not None:       # a real 2-act death logs globally
        assert a.hp_by_node[-1] == 0
        assert len(a.hp_by_node) == a.death_node + 1
