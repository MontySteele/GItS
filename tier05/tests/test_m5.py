"""Tier 0.5 M5: run loop, rewards, assigned policy, draft_regret,
fragility plumbing. Determinism at RUN granularity is the load-bearing
test — everything else in M6/M7 builds on replayable runs."""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier05 import draft, model, rewards
from tier05.run_metrics import summarize_runs

SEED = 42


# --- run model ---

def test_node_template_shape():
    nodes = model.node_template()
    assert len(nodes) == len(C.RUN_NODE_TEMPLATE)
    assert nodes[C.BURST_CHECK_NODE] == "BC"
    assert nodes[-1] == "B"
    assert nodes.count("E") == 2 and nodes.count("R") == 2


def test_run_determinism():
    a = model.run_one("klee", "demolition", "demolition",
                      draft.assigned_policy, SEED)
    b = model.run_one("klee", "demolition", "demolition",
                      draft.assigned_policy, SEED)
    assert a.deck_ids == b.deck_ids
    assert a.hp_by_node == b.hp_by_node
    assert a.death_node == b.death_node
    assert [d["picked"] for d in a.decisions] == \
           [d["picked"] for d in b.decisions]


def test_death_logs_node_index_and_hp_persists():
    results = model.run_many("klee", "demolition", "demolition",
                             draft.assigned_policy, 30, SEED)
    assert any(r.death_node is not None for r in results)
    for r in results:
        if r.death_node is not None:
            assert r.hp_by_node[-1] == 0
            assert len(r.hp_by_node) == r.death_node + 1
        assert len(r.fight_stats) >= 1          # instrumentation attached


def test_lite_encounters_are_derived_not_tuned():
    rng = random.Random(SEED)
    seen = {}
    for _ in range(50):
        for e in model.build_node_encounter("N", rng):
            seen[e.name] = e
    lite = seen["punisher_lite"]
    full = loader._encounter_index()["punisher"]["enemies"][0]
    assert lite.hp == round(full["hp"] * C.PUNISHER_LITE_SCALE)
    assert lite.intents[0]["amount"] == round(
        full["intents"][0]["amount"] * C.PUNISHER_LITE_SCALE)
    assert seen["grinder_lite"].hp == C.ATTRITION_LITE_HP
    assert seen["swarmling"].hp == 14           # frozen battery, untouched


def test_rest_policy_heals_when_hurt_else_upgrades_then_removes():
    deck = loader.starting_deck("klee")
    action, _ = model.rest_action(deck, hp=20, max_hp=62)
    assert action == "heal"                     # hurt always heals first
    # M7: healthy rests smith an on-plan card before thinning.
    action, target = model.rest_action(deck, hp=60, max_hp=62,
                                       archetype="demolition")
    assert action == "upgrade"
    assert "demolition" in loader.get_card(target).archetypes
    # With every on-plan card already upgraded, the old removal preference
    # returns: basic attacks first.
    upgraded = [cid + "+" if upgrades.has_upgrade(cid) else cid
                for cid in deck]
    action, removed = model.rest_action(upgraded, hp=60, max_hp=62,
                                        archetype="demolition")
    assert action == "remove"
    assert loader.get_card(removed).rarity == "basic"
    assert not any(fx.get("op") == "block"
                   for fx in loader.get_card(removed).effects)


# --- rewards ---

def test_reward_rarity_odds_and_slot():
    rng = random.Random(SEED)
    counts = {"common": 0, "uncommon": 0, "rare": 0}
    for _ in range(1500):
        offers = rewards.roll_rewards(rng, "klee")
        assert len(offers) == C.REWARD_CARD_OFFERS + 1   # + companion slot
        comp = offers[-1]
        assert comp.is_companion
        if comp.rarity == "rare":
            assert comp.star == 5       # 5-stars at rare odds ONLY
        else:
            assert comp.star == 4
        for c in offers[:-1]:
            assert not c.is_companion   # card offers never companions
            counts[c.rarity] += 1
    total = sum(counts.values())
    assert counts["common"] / total == pytest.approx(0.60, abs=0.04)
    assert counts["rare"] / total == pytest.approx(0.05, abs=0.02)


def test_ref_pool_is_own_kit_no_companions():
    rng = random.Random(SEED)
    package = set(loader.character_packages("ref_ironclad")
                  ["archetype_package"])
    for _ in range(200):
        offers = rewards.roll_rewards(rng, "ref_ironclad")
        assert len(offers) == C.REWARD_CARD_OFFERS    # no companion slot
        assert all(c.id in package for c in offers)


# --- assigned draft policy ---

def _cards(*ids):
    return [loader.get_card(i) for i in ids]


def test_payoff_gated_beyond_core():
    # Post-triage shape: a payoff that ADVANCES the core is a fine early
    # pick (the deadlock fix); the gate bites on payoffs BEYOND the core.
    starter = _cards(*loader.starting_deck("klee"))
    amp = next(c for c in loader._card_index().values()
               if "reaction" in c.archetypes and c.role == "payoff")
    offline = starter + [amp, loader.get_card("dahlia_sacramental_shower")]
    assert not draft.core_complete(offline, "reaction")
    cold = draft.score_offer(amp, offline, "reaction")   # 2nd amp, offline
    online = starter + [amp] + _cards("dahlia_sacramental_shower",
                                      "kaeya_frostgnaw")
    assert draft.core_complete(online, "reaction")
    hot = draft.score_offer(amp, online, "reaction")
    assert hot > cold


def test_enabler_value_decays():
    enabler = loader.get_card("mine_toss")
    starter = _cards(*loader.starting_deck("klee"))
    early = draft.score_offer(enabler, starter, "demolition")
    late = draft.score_offer(
        enabler, starter + _cards("mine_toss", "double_pop", "bomb_voyage",
                                  "quick_fuse"), "demolition")
    assert early > late


def test_reaction_core_rule():
    # v1.9: the Burst left the core definition -- it arrives by charging
    # the meter, not by drafting, so assembly is 2 appliers + 1 amp payoff.
    starter = _cards(*loader.starting_deck("klee"))
    assert not draft.core_complete(starter, "reaction")
    core = starter + _cards("dahlia_sacramental_shower", "kaeya_frostgnaw",
                            "sizzle")
    assert draft.core_complete(core, "reaction")


def test_skip_is_a_real_pick():
    # A hand of off-plan cards below threshold gets skipped.
    starter = _cards(*loader.starting_deck("klee"))
    offers = _cards("combustion_study")      # reaction card, demolition run
    pick = draft.assigned_policy(random.Random(0), starter, offers,
                                 "demolition")
    assert pick is None


def test_draft_regret_deterministic():
    r = model.run_many("klee", "spark", "spark",
                       draft.assigned_policy, 20, SEED)
    r2 = model.run_many("klee", "spark", "spark",
                        draft.assigned_policy, 20, SEED)
    assert sum(x.regret_samples for x in r) == \
           sum(x.regret_samples for x in r2)


# --- triage ruling 3b/4 mechanisms ---

def test_progression_compensator_scales_elite_and_boss_only():
    rng = random.Random(SEED)
    full = loader._encounter_index()["punisher"]["enemies"][0]
    elite = model.build_node_encounter("E", rng)[0]
    assert elite.hp == round(full["hp"]
                             * C.PROGRESSION_GAP_COMPENSATOR["elite"])
    boss = model.build_node_encounter("B", rng)[0]
    assert boss.hp == round(240 * C.PROGRESSION_GAP_COMPENSATOR["boss"])
    assert C.PROGRESSION_GAP_COMPENSATOR["normal"] == 1.0   # untouched


def test_pity_slot_fires_after_k_companionless_screens():
    # pity(k) mechanism (pulled forward from M7 by triage ruling 4):
    # k screens without taking a companion -> next slot offers 3.
    def no_companions(rng, deck, offers, archetype):
        picks = [c for c in offers if not c.is_companion]
        return picks[0] if picks else None
    r = model.run_one("klee", "demolition", "demolition", no_companions,
                      SEED, slot_mode="pity(2)")
    comp_counts = [sum(1 for c in d["offers"] if c.is_companion)
                   for d in r.decisions]
    assert comp_counts[:2] == [1, 1]        # standard until pity builds
    assert 3 in comp_counts                 # then the choose-3 fires


def test_core_advance_never_dead_pick():
    # Regression for the reaction deadlock: an amp payoff must outscore
    # nothing-burger offers even before the core is online.
    starter = _cards(*loader.starting_deck("klee"))
    deck = starter + _cards("dahlia_sacramental_shower", "kaeya_frostgnaw")
    amp = next(c for c in loader._card_index().values()
               if "reaction" in c.archetypes and c.role == "payoff")
    assert draft.score_offer(amp, deck, "reaction") \
        >= C.DRAFT_SKIP_THRESHOLD


# --- fragility metrics ---

def test_summarize_runs_fragility_shape():
    res = model.run_many("klee", "demolition", "demolition",
                         draft.assigned_policy, 40, SEED)
    s = summarize_runs(res)
    assert 0.0 <= s["winrate"] <= 1.0
    assert sum(s["death_heatmap"].values()) == \
        sum(1 for r in res if r.death_node is not None)
    reached = [b["reached"] for b in s["hp_bands"] if b]
    assert reached[0] == 40                    # everyone fights node 0
    assert all(x >= y for x, y in zip(reached, reached[1:]))  # monotone
    # Elite/boss death clustering — the spec's declared expectation
    # (post-compensator, the boss carries a healthy share of it).
    eb_deaths = sum(s["death_heatmap"].get(i, 0)
                    for i, k in enumerate(model.node_template())
                    if k in ("E", "B"))
    assert eb_deaths >= sum(s["death_heatmap"].values()) * 0.6
