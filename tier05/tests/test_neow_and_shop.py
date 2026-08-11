"""W2 relic-granting cadence: Neow run-start pick + shop relic stock, and the
load-bearing invariant that the DEFAULT (grant_relics=False, relics=None) run
is byte-for-byte the pre-W2 model.

STYLE (mirrors test_relics_runlayer / test_shop_economy):
  - combat is stubbed to a deterministic WIN so a relic's payout is isolated
    from combat noise; a recorder captures the per-fight entry HP / max HP /
    relic_effects the model built each fight's player with.
  - the granting sites (treasure/elite/boss/astrolabe) all funnel through
    ``relic_pool.roll_relic_reward``; monkeypatching THAT to None silences every
    grant site EXCEPT the shop (which rolls its own shelf via
    ``unowned_common`` + rng.choice), so a single relic can be isolated at a
    single site.
  - the Neow pick is steered by monkeypatching ``neow_offer`` (the pick itself
    is deterministic: highest static valuation, ties by lowest id).

SEED discipline: small fixed seeds, stubbed combat -> modest runtime. The
invariant + anchor tests run REAL combat on a handful of seeds.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import CombatState
from tier0.harness import metrics, runner
from tier0.harness.runner import run_battery
from tier05 import draft, model
from tier05 import maps
from tier05 import relics as relic_pool


@pytest.fixture(autouse=True)
def _single_act(monkeypatch):
    """§10 re-stamp: this suite asserts ACT-1 cadence (7 fights, one shop).
    Pin the registry so acts 2-3 never silently double the counts."""
    monkeypatch.setattr(C, "RUN_ACTS", C.RUN_ACTS[:1])

CHAR = "klee"
ARCH = "demolition"
PILOT = "demolition"
SEED = 7
BASE_HP = loader._character_index()[CHAR]["hp"]      # 62


# --- combat stub: deterministic win + optional per-fight recorder -----------

# §11: these tests are about RELIC/POTION/SHOP hooks firing at particular node
# kinds, not about map generation -- so they pin the legacy v5 spine and index
# into it exactly as they always did. Runs elsewhere walk a generated map.
LEGACY_SPINE = "NNNRETN$ERB"


@pytest.fixture(autouse=True)
def _legacy_spine(monkeypatch):
    monkeypatch.setattr(model, "build_act_map",
                        lambda rng, act: maps.linear(LEGACY_SPINE, act))


def _win_stub(hit=0, records=None):
    """Every fight is an instant win. When `records` is given, snapshot the
    entry HP / max HP / relic_effects the model built the fight's player with --
    how we inspect the context injections without the real engine."""
    def stub(player, enemies, pilot, seed):
        if records is not None:
            records.append({
                "hp": player.hp,
                "max_hp": player.max_hp,
                "relic_effects": [dict(fx) for fx in (player.relic_effects or [])],
            })
        player.hp = max(1, player.hp - hit)
        for e in enemies:
            e.hp = 0
        return CombatState(player=player, enemies=enemies,
                           rng=random.Random(seed))
    return stub


def _skip(rng, deck, offers, archetype):
    return None


def _fight_kinds():
    return [k for k in list(LEGACY_SPINE) if k in ("N", "E", "B")]


def _no_grants(monkeypatch):
    """Silence EVERY relic acquisition except the site under test.

    Both doors, deliberately. `roll_relic_reward` covers treasure / elite /
    boss / astrolabe; `unowned_common` covers the SHOP shelf, which is a
    separate door the older version of this helper left open with a note
    saying so. That note made the isolation a promise the helper did not keep:
    any run whose rng shifted could buy a relic at the shop and smuggle an
    extra hook into a test that asserts on exact hook lists. The §4.7 shop
    channel duly renumbered the run and a shop relic started injecting
    combat_start_energy into every fight of the booming_conch test -- a
    failure that said nothing about booming_conch.
    """
    monkeypatch.setattr(relic_pool, "roll_relic_reward",
                        lambda rng, held, character: None)
    monkeypatch.setattr(relic_pool, "unowned_common",
                        lambda held_ids, character: [])


def _force_neow(monkeypatch, offer):
    """Pin the Neow OFFER (the pick stays real + deterministic)."""
    monkeypatch.setattr(relic_pool, "neow_offer", lambda rng, k=3: list(offer))


# ---------------------------------------------------------------------------
# Neow offer / pick contract.
# ---------------------------------------------------------------------------

def test_neow_offer_three_distinct_from_pool_and_pick_is_deterministic():
    pool = set(relic_pool.neow_pool())
    assert len(pool) >= 3
    for seed in range(80):
        rng = random.Random(seed)
        offer = relic_pool.neow_offer(rng)
        assert len(offer) == 3                       # k=3 boons
        assert len(set(offer)) == 3                  # DISTINCT
        assert set(offer) <= pool                    # all from the Neow pool

        pick = relic_pool.neow_pick(offer, CHAR)
        assert pick in offer                         # one of the offered
        # deterministic: no rng, same offer -> same pick every call
        assert relic_pool.neow_pick(list(offer), CHAR) == pick


def test_neow_pick_takes_highest_valuation_tie_by_id():
    # booming_conch (elite_combat_start, w9) beats golden_pearl (gold, w2).
    assert relic_pool.neow_pick(
        ["golden_pearl", "booming_conch", "fishing_rod"], CHAR) == "booming_conch"
    # tie (both gold_on_pickup, w2) breaks to the lexicographically lower id.
    assert relic_pool.neow_pick(["hand_of_greed", "golden_pearl"], CHAR) == \
        "golden_pearl"
    assert relic_pool.neow_pick([], CHAR) is None


def test_every_pool_hook_is_weighted_or_pending_and_unknown_is_loud():
    """EB-31h: an unpriced hook must never be a silent 0.

    Every hook reachable from a Neow or Ancient boon is either weighted in
    `_NEOW_HOOK_WEIGHT` or explicitly parked in `_NEOW_WEIGHT_PENDING`
    (the EB-31q pricing call); a hook in neither table raises at the pick.
    The pending set must also stay honest both ways: no member that has
    since gained a weight (stale park), no member absent from the pools
    (dead park)."""
    pool_hooks = {fx.get("hook")
                  for pool in (relic_pool.neow_pool(), relic_pool.ancient_pool())
                  for spec in pool.values()
                  for fx in (spec.get("effects") or [])}
    unpriced = {h for h in pool_hooks
                if h not in relic_pool._NEOW_HOOK_WEIGHT
                and h not in relic_pool._NEOW_WEIGHT_PENDING}
    assert not unpriced, (
        f"pool hooks with no weight and no EB-31q pending entry: "
        f"{sorted(unpriced)}")
    stale = relic_pool._NEOW_WEIGHT_PENDING & set(relic_pool._NEOW_HOOK_WEIGHT)
    assert not stale, f"pending hooks that now HAVE weights: {sorted(stale)}"
    dead = relic_pool._NEOW_WEIGHT_PENDING - pool_hooks
    assert not dead, f"pending hooks no pool boon carries: {sorted(dead)}"

    # R126 priced the Orobas four: each variant totals 13, one above the
    # generic ceiling, so the pilot narrowly prefers its own starter's
    # upgrade. Unknown hooks still raise (EB-31h's guard outlives the park).
    assert relic_pool._hook_weight("spotlight_both_modes") == 13
    assert relic_pool._hook_weight("combat_start_spark") == 13
    assert (relic_pool._hook_weight("charge_per_exhaust")
            + relic_pool._hook_weight("burst_per_exhaust")) == 13
    with pytest.raises(KeyError):
        relic_pool._hook_weight("hook_nobody_priced")


# ---------------------------------------------------------------------------
# A grant_relics run APPLIES the Neow relic's effect.
# ---------------------------------------------------------------------------

def test_neow_booming_conch_applies_elite_only_draw_and_energy(monkeypatch):
    # Isolate: no other grants, so relic_effects come ONLY from the Neow
    # booming_conch elite injection. Offer makes booming_conch the pick.
    _no_grants(monkeypatch)
    _force_neow(monkeypatch, ["booming_conch", "golden_pearl", "fishing_rod"])
    records = []
    monkeypatch.setattr(model, "run_fight", _win_stub(0, records))

    res = model.run_one(CHAR, ARCH, PILOT, _skip, SEED, grant_relics=True)
    assert "booming_conch" in res.relics            # the Neow pick was applied

    kinds = _fight_kinds()
    assert len(records) == len(kinds) == 7
    for kind, rec in zip(kinds, records):
        fx = rec["relic_effects"]
        draw = [e for e in fx if e.get("hook") == "combat_start_draw"]
        energy = [e for e in fx if e.get("hook") == "combat_start_energy"]
        if kind == "E":
            assert any(e["amount"] == 2 for e in draw)      # elite: +2 draw
            assert any(e["amount"] == 1 for e in energy)    # elite: +1 energy
        else:
            assert draw == []                               # normals/boss: none
            assert energy == []


def test_neow_maxhp_boon_raises_max_hp_at_run_start(monkeypatch):
    # ossified_relic (+8 max HP) is a pickup boon: max HP is up BEFORE the first
    # fight. Isolate other grants so nothing else moves max HP.
    _no_grants(monkeypatch)
    _force_neow(monkeypatch, ["ossified_relic", "golden_pearl", "hand_of_greed"])
    records = []
    monkeypatch.setattr(model, "run_fight", _win_stub(0, records))

    res = model.run_one(CHAR, ARCH, PILOT, _skip, SEED, grant_relics=True)
    assert "ossified_relic" in res.relics
    # First fight already sees the raised ceiling, and HP rose with it.
    assert records[0]["max_hp"] == BASE_HP + 8
    assert records[0]["hp"] == BASE_HP + 8


# ---------------------------------------------------------------------------
# Shop under grant_relics: stocks + (gold permitting) sells a relic, whose
# effect then applies; never sells an unownable relic.
# ---------------------------------------------------------------------------

def _strawberry_only(held_ids, character):
    """Shop shelf source: strawberry until it is held (honours `exclude`, so
    the shelf never duplicates it)."""
    return [r for r in ["strawberry"] if r not in set(held_ids)]


def test_shop_stocks_and_sells_a_relic_whose_effect_applies(monkeypatch):
    # Guarantee gold (hand_of_greed = +250) and isolate the relic to the SHOP:
    # roll_relic_reward=None kills treasure/elite/boss grants; unowned_common is
    # pinned so the shop shelf is exactly one strawberry (+7 max HP on pickup).
    _no_grants(monkeypatch)
    _force_neow(monkeypatch, ["hand_of_greed"])
    monkeypatch.setattr(relic_pool, "unowned_common", _strawberry_only)
    records = []
    monkeypatch.setattr(model, "run_fight", _win_stub(0, records))

    res = model.run_one(CHAR, ARCH, PILOT, _skip, SEED, grant_relics=True)

    # The shop stocked AND sold the relic ...
    relic_buys = [p for p in res.shop if p.get("buy") == "relic"]
    # "visit" joined every shop record on 2026-08-10 (the P1 attribution
    # repair: the run-level offer and purchase logs had no join key). This run
    # walks into one shop, so the stamp is 0.
    assert relic_buys == [{"buy": "relic", "id": "strawberry",
                           "price": 150, "visit": 0}]
    assert "strawberry" in res.relics               # ... and it is a run relic

    # ... and its +7 max-HP effect APPLIED at the shop: fights before the shop
    # ($ is node index 7) sit at BASE_HP; the two fights after it (E@8, B@10)
    # carry the raised ceiling.
    kinds = _fight_kinds()                           # N N N E N E B
    assert records[4]["max_hp"] == BASE_HP           # node 6 (N), pre-shop
    assert kinds[5] == "E" and records[5]["max_hp"] == BASE_HP + 7   # node 8
    assert kinds[6] == "B" and records[6]["max_hp"] == BASE_HP + 7   # node 10


def test_shop_never_sells_a_relic_the_character_cannot_own(monkeypatch):
    # red_skull is owner-locked to the Ironclads; klee must never be offered or
    # sold it. Proven at the gate the shop uses (unowned_common) AND end-to-end.
    assert "red_skull" not in relic_pool.unowned_common([], CHAR)
    assert "red_skull" in relic_pool.unowned_common([], "ref_ironclad")

    monkeypatch.setattr(model, "run_fight", _win_stub(0))
    for seed in range(12):
        res = model.run_one(CHAR, ARCH, PILOT, _skip, seed, grant_relics=True)
        assert "red_skull" not in res.relics


# ---------------------------------------------------------------------------
# THE KEY INVARIANT: default (grant_relics=False, relics=None) is byte-for-byte
# the pre-W2 model. This is what protects the 372 existing tests.
# ---------------------------------------------------------------------------

def test_default_run_is_byte_for_byte_unchanged_and_grants_nothing():
    # REAL combat: the whole relic path must be dead when unrequested, so a
    # default run reproduces itself decision-for-decision under every framing,
    # and res.relics is empty.
    for seed in (1, 2, 3, 7, 11):
        default = model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed)
        assert default.relics == []                  # nothing granted by default
        variants = [
            model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed,
                          relics=None, grant_relics=False),
            model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed),
        ]
        for other in variants:
            assert other.relics == []
            assert other.deck_ids == default.deck_ids
            assert other.hp_by_node == default.hp_by_node
            assert other.gold == default.gold
            assert other.death_node == default.death_node
            assert other.shop == default.shop
            assert other.rests == default.rests
            assert other.removal_uses == default.removal_uses
            assert [d["picked"] for d in other.decisions] == \
                   [d["picked"] for d in default.decisions]


# ---------------------------------------------------------------------------
# Anchor lock re-run: this file fails loudly if W2 ever perturbed tier0.
# (Mirrors tier0/tests/test_anchor_lock.py::test_ref_ironclad_battery_numbers.)
# ---------------------------------------------------------------------------

def test_anchor_still_exact_after_w2():
    assert runner.BASELINE == ("ref_ironclad", "starter")
    s = metrics.summarize(run_battery("ref_ironclad", "starter", "punisher",
                                      "generic", 200, SEED))
    assert s["winrate"] == pytest.approx(0.525, abs=1e-9)
    assert s["avg_turns"] == pytest.approx(9.585, abs=1e-9)
