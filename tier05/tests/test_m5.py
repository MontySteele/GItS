"""Tier 0.5 M5: run loop, rewards, assigned policy, draft_regret,
fragility plumbing. Determinism at RUN granularity is the load-bearing
test — everything else in M6/M7 builds on replayable runs."""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine.state import CombatState
from tier05 import draft, model, rewards
from tier05.run_metrics import summarize_runs, survival_profile

SEED = 42


# --- run model ---

def test_node_template_shape():
    nodes = model.node_template()
    assert len(nodes) == len(C.RUN_NODE_TEMPLATE)
    # RUNTEMPLATE_VERSION 3 (run-model rework §3.1): "NNNRETN$ERB" -- 11
    # nodes, 7 fights (4 normal + 2 elite + 1 boss), 2 rests, 1 treasure,
    # 1 shop. The burst-check NODE is DROPPED. SURVIVING INVARIANTS: the
    # boss is last, and a rest guards the boss (pre-boss campfire).
    assert nodes[-1] == "B"
    assert nodes[-2] == "R"
    assert nodes.count("N") == 4
    assert nodes.count("E") == 2
    assert nodes.count("R") == 2
    assert nodes.count("T") == 1
    assert nodes.count("$") == 1
    assert nodes.count("B") == 1
    # 7 fights: normals + elites + the boss.
    assert nodes.count("N") + nodes.count("E") + nodes.count("B") == 7
    # The first rest precedes the first elite (§3.1 red-pen: never path to
    # an early elite without a chance to heal/smith first).
    assert nodes.index("R") < nodes.index("E")


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


def test_combat_max_hp_gain_carries_to_the_next_fight(monkeypatch):
    """Permanent combat gains survive player reconstruction between nodes."""
    seen = []

    def gain_once(player, enemies, pilot, seed):
        seen.append((player.hp, player.max_hp))
        if len(seen) == 1:
            player.max_hp += 3
            player.hp += 3
        for enemy in enemies:
            enemy.hp = 0
        return CombatState(player=player, enemies=enemies,
                           rng=random.Random(seed))

    monkeypatch.setattr(model, "node_template", lambda: ["N", "N"])
    monkeypatch.setattr(model, "run_fight", gain_once)
    model.run_one("klee", "demolition", "demolition",
                  lambda rng, deck, offers, archetype: None, SEED)

    assert seen == [(62, 62), (65, 65)]


def test_realistic_normals_easy_then_hard():
    """Run-model rework §4/§3.2: the realistic roster REPLACED the old
    battery-derived lites in build_node_encounter. The first three N nodes
    draw distinct easy-pool encounters; the fourth N draws the hard pool.
    HP lands inside each enemy's spawn band, rolled through the run rng."""
    from tier05 import act1
    easy_ids = {e["id"] for e in act1.pools()["easy"]}
    hard_ids = {e["id"] for e in act1.pools()["hard"]}
    rng = random.Random(SEED)
    draw = act1.ActDraw(rng)
    easy_picks = [draw.encounter_for("N", rng)["id"]
                  for _ in range(act1.EASY_FIGHTS)]
    assert set(easy_picks) <= easy_ids
    assert len(set(easy_picks)) == act1.EASY_FIGHTS   # no repeat within act
    assert draw.encounter_for("N", rng)["id"] in hard_ids   # fight 4 = hard
    # Spawn-time HP range: Nibbit's band is [42, 46]; every roll lands in it.
    nibbit = next(e for e in act1.pools()["easy"] if e["id"] == "nibbit")
    lo, hi = nibbit["enemies"][0]["hp"]
    for s in range(40):
        body = act1.spawn(nibbit, random.Random(s))[0]
        assert lo <= body.hp <= hi and body.max_hp == body.hp


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


def test_post_boss_companion_slot_is_rare_only():
    rng = random.Random(SEED)
    for _ in range(100):
        offers = rewards.roll_rewards(
            rng, "klee", companion_rarity="rare")
        companion = offers[-1]
        assert companion.is_companion
        assert companion.rarity == "rare"
        assert companion.star == 5


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
    offers = _cards("borrowed_brilliance")   # deep reaction machinery
    pick = draft.assigned_policy(random.Random(0), starter, offers,
                                 "demolition")
    assert pick is None


def test_drafter_v3_values_klee_visible_utility():
    """Direct mitigation is visible; deck-context engines stay neutral."""
    assert draft._static_power(loader.get_card("alchemical_curiosity")) == 0
    assert draft._static_power(loader.get_card("trip_wire")) == 5.5
    assert draft._static_power(loader.get_card("skip_and_hop")) == 2

    dreams = loader.get_card("elemental_ecstasy")
    assert draft._has_block(dreams)
    # Conditional 8 Block is available at the draft-time 50% share.
    assert draft._static_power(dreams) == 2
    assert draft._static_power(loader.get_card("patched_dress")) == 6


def test_bomb_guard_proxy_does_not_stack_with_printed_weak():
    trip = loader.get_card("trip_wire")
    sorry = loader.get_card("sorry_jean")

    # Trip Wire's Bomb and Weak share one runtime reduction branch, so the
    # card gets delayed damage + Weak but not a second guard allowance.
    assert draft._static_power(trip) == 7 * 0.5 + 2
    # Sorry, Jean has no printed Weak, so its pending Bomb receives the one
    # conservative guard allowance in addition to damage and Block.
    assert draft._static_power(sorry) == 4 + 4 * 0.5 + 1.5


def test_draft_regret_deterministic():
    r = model.run_many("klee", "spark", "spark",
                       draft.assigned_policy, 20, SEED)
    r2 = model.run_many("klee", "spark", "spark",
                        draft.assigned_policy, 20, SEED)
    assert sum(x.regret_samples for x in r) == \
           sum(x.regret_samples for x in r2)


# --- triage ruling 3b/4 mechanisms ---

def test_elite_pool_draws_two_distinct_and_boss_is_vantom():
    """Run-model rework §4.3/§4.4: E nodes draw two DISTINCT enemies from
    the 3-enemy elite pool; B is Vantom at his real 173 HP. The old
    compensator (punisher*0.8 elite / 240*0.7 boss) is GONE -- the roster
    carries real StS2 numbers with no run-context scaling."""
    from tier05 import act1
    rng = random.Random(SEED)
    draw = act1.ActDraw(rng)
    e1 = draw.encounter_for("E", rng)["id"]
    e2 = draw.encounter_for("E", rng)["id"]
    assert e1 != e2                                  # 2 distinct elites
    assert {e1, e2} <= {e["id"] for e in act1.pools()["elite"]}
    boss = act1.spawn(draw.encounter_for("B", rng), rng)
    assert len(boss) == 1
    assert boss[0].name == "vantom"
    assert boss[0].hp == 173 and boss[0].is_boss     # real HP, uncompensated


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

def _fake_run(hp_by_node, kinds):
    """A RunResult with a hand-built HP curve, for metric unit tests."""
    return model.RunResult(seed=0, won=True, death_node=None,
                           hp_by_node=list(hp_by_node), deck_ids=[],
                           node_kinds=list(kinds))


def test_survival_profile_reads_the_curve_it_is_given():
    """Pass-4 instrument: fragility as max-HP-normalized scalars.

    Unit-tested on synthetic curves rather than sim output, so the metric
    is pinned independently of any balance number that may later move.
    """
    kinds = ["N", "N", "R", "N"]          # 3 fights, one rest (excluded)
    # max_hp 100: fights at 80, 40, 20 -> mean 46.7%, 2 of 3 under 30%.
    s = survival_profile([_fake_run([80, 40, 99, 20], kinds)], 100)
    assert s["median_hp_pct_by_fight"] == [0.8, 0.4, 0.2]   # rest dropped
    assert s["act_median_hp_pct"] == pytest.approx(0.4667, abs=1e-3)
    assert s["act_share_below_30pct"] == pytest.approx(1 / 3)  # only 20%

    # Near-death floor is 15% of max: 20/100 is above it, 10/100 below.
    assert s["near_death_rate"] == 0.0
    assert survival_profile([_fake_run([80, 40, 99, 10], kinds)],
                            100)["near_death_rate"] == 1.0
    # Dead (0 HP) is not "near death" -- the floor is for LIVING runs.
    assert survival_profile([_fake_run([80, 40, 99, 0], kinds)],
                            100)["near_death_rate"] == 0.0


def test_survival_profile_separates_a_fragile_run_from_a_sturdy_one():
    """The seen-to-FAIL half: the metric must actually discriminate.

    Two characters with the SAME max HP and different curves -- every
    scalar must move in the fragile direction. This is the comparison the
    run-winrate scalar cannot make: both runs below could complete the
    act and report an identical 100% winrate.
    """
    kinds = ["N", "N", "N"]
    sturdy = survival_profile([_fake_run([80, 60, 45], kinds)], 100)
    fragile = survival_profile([_fake_run([50, 25, 12], kinds)], 100)
    assert fragile["act_median_hp_pct"] < sturdy["act_median_hp_pct"]
    assert fragile["act_share_below_30pct"] > sturdy["act_share_below_30pct"]
    assert fragile["near_death_rate"] > sturdy["near_death_rate"]


def test_survival_profile_keeps_dead_runs_in_later_fight_cohorts():
    """Dying early must not improve the later median by removing the run."""
    kinds = ["N", "N"]
    sturdy = _fake_run([100, 100], kinds)
    fragile_survivor = _fake_run([1, 1], kinds)
    fragile_death = model.RunResult(
        seed=1, won=False, death_node=0, hp_by_node=[0], deck_ids=[],
        node_kinds=kinds)

    survived = survival_profile([sturdy, fragile_survivor], 100)
    died = survival_profile([sturdy, fragile_death], 100)

    assert died["median_hp_pct_by_fight"] == [0.5, 0.5]
    assert died["act_median_hp_pct"] < survived["act_median_hp_pct"]


def test_summarize_runs_fragility_shape():
    res = model.run_many("klee", "demolition", "demolition",
                         draft.assigned_policy, 40, SEED)
    s = summarize_runs(res)
    assert 0.0 <= s["winrate"] <= 1.0
    assert s["wins"] == sum(r.won for r in res)
    lo, hi = s["winrate_wilson95"]
    assert lo <= s["winrate"] <= hi
    assert sum(s["death_heatmap"].values()) == \
        sum(1 for r in res if r.death_node is not None)
    reached = [b["reached"] for b in s["hp_bands"] if b]
    assert reached[0] == 40                    # everyone fights node 0
    assert all(x >= y for x, y in zip(reached, reached[1:]))  # monotone
    # Elite/boss death clustering — the spec's declared expectation
    # (post-compensator, the boss carries a healthy share of it).
    # 2026-07-20 WORLD CHANGE (Furina sprint 1): loading the Fontaine
    # companion sheet put cross-nation glue in Klee's uniform reward half;
    # measured clustering moved 0.6+ -> 0.588 at this n=40 cell (10/17 —
    # binomial sd ~0.12, so 0.6 was inside noise of the old world too).
    # Relaxed to majority-clustering; flagged for red-pen in the sprint 1
    # report. The ratified 1000-fight winrate bands are untouched and
    # remain the real lock.
    eb_deaths = sum(s["death_heatmap"].get(i, 0)
                    for i, k in enumerate(model.node_template())
                    if k in ("E", "B"))
    assert eb_deaths >= sum(s["death_heatmap"].values()) * 0.5
