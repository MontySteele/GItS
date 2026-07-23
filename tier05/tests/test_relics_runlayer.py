"""Run-layer relic proofs (relic-content pass).

These seed a run via ``model.run_one(..., relics=[...])`` and assert the
RUN-SCOPED half of each relic actually fires in the run loop -- the half that
lives in tier05/relics.py + tier05/model.py, NOT the combat engine. The
combat-side seam is exercised by capturing the ``relic_effects`` that
``build_player_from_ids`` is handed per fight (the context injections the
run layer computes for combat.py).

Combat is stubbed to a deterministic WIN (the ``_win`` trick from
test_shop_economy) so a relic's run-layer payout is isolated from combat
noise: every relic run is compared against a byte-identical no-relic run under
the same seed, and the ONLY delta is the relic. The last test is the load-
bearing "nothing moved" lock: ``relics=None`` / ``[]`` reproduce the pre-relic
run decision-for-decision under REAL combat.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import CombatState
from tier05 import draft, model


@pytest.fixture(autouse=True)
def _single_act(monkeypatch):
    """§10 re-stamp: this suite asserts ACT-1 per-node cadence (7 fights,
    node_template() indices). Pin the registry so acts 2-3 never silently
    change the counts under test."""
    monkeypatch.setattr(C, "RUN_ACTS", C.RUN_ACTS[:1])

CHAR = "klee"
ARCH = "demolition"
PILOT = "demolition"
SEED = 7
BASE_HP = loader._character_index()[CHAR]["hp"]     # 62


# --- combat stub: deterministic win, optional fixed HP hit + fx recorder ----

def _win_stub(hit=0, records=None):
    """Every fight is an instant win: kill all enemies, dock a fixed `hit` of
    player HP (0 = untouched). When `records` is given, snapshot the entry HP /
    max HP / relic_effects the model built the fight's player with -- that is
    how we inspect the context-dependent combat injections (elite / post-rest)
    without running the real engine."""
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


def _pick_first(rng, deck, offers, archetype):
    return offers[0]                # always a card offer (companion is last)


def _fight_kinds():
    return [k for k in model.node_template() if k in ("N", "E", "B")]


def _n_upgraded(deck_ids):
    return sum(1 for cid in deck_ids if cid.endswith("+"))


# --- strawberry: +7 max HP, and current HP rises with it (pickup) -----------

def test_strawberry_raises_max_hp_and_current_hp(monkeypatch):
    rec_relic, rec_base = [], []
    monkeypatch.setattr(model, "run_fight", _win_stub(0, rec_relic))
    model.run_one(CHAR, ARCH, PILOT, _skip, SEED, relics=["strawberry"])
    monkeypatch.setattr(model, "run_fight", _win_stub(0, rec_base))
    model.run_one(CHAR, ARCH, PILOT, _skip, SEED)

    assert rec_base[0]["max_hp"] == BASE_HP
    assert rec_relic[0]["max_hp"] == BASE_HP + 7          # +7 max HP
    assert rec_relic[0]["hp"] == BASE_HP + 7              # current HP rose too
    assert rec_relic[0]["hp"] > rec_base[0]["hp"]


# --- golden_pearl: +150 gold at run start (pickup) --------------------------

def test_golden_pearl_grants_150_gold_at_start(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub(0))
    base = model.run_one(CHAR, ARCH, PILOT, _skip, SEED)
    relic = model.run_one(CHAR, ARCH, PILOT, _skip, SEED, relics=["golden_pearl"])
    assert relic.gold - base.gold == 150


# --- amethyst_aubergine: +15 gold per WON fight -----------------------------

def test_amethyst_aubergine_adds_gold_per_won_fight(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub(0))
    base = model.run_one(CHAR, ARCH, PILOT, _skip, SEED)
    relic = model.run_one(CHAR, ARCH, PILOT, _skip, SEED,
                          relics=["amethyst_aubergine"])
    won = len(_fight_kinds())                       # 4 N + 2 E + 1 B = 7 wins
    assert won == 7
    assert relic.gold - base.gold == 15 * won


# --- regal_pillow: extra heal at a rest node --------------------------------

def test_regal_pillow_extra_heal_at_rest(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub(8))   # arrive hurt
    base = model.run_one(CHAR, ARCH, PILOT, _skip, SEED)
    relic = model.run_one(CHAR, ARCH, PILOT, _skip, SEED, relics=["regal_pillow"])
    ri = model.node_template().index("R")                   # first rest = 3
    assert base.hp_by_node[ri] < BASE_HP                    # room to heal into
    assert relic.hp_by_node[ri] == min(BASE_HP, base.hp_by_node[ri] + 15)
    assert relic.hp_by_node[ri] > base.hp_by_node[ri]


# --- meal_ticket: heal at the shop node -------------------------------------

def test_meal_ticket_heals_at_shop(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub(8))
    base = model.run_one(CHAR, ARCH, PILOT, _skip, SEED)
    relic = model.run_one(CHAR, ARCH, PILOT, _skip, SEED, relics=["meal_ticket"])
    si = model.node_template().index("$")                   # shop node = 7
    assert base.hp_by_node[si] < BASE_HP
    assert relic.hp_by_node[si] == min(BASE_HP, base.hp_by_node[si] + 15)
    assert relic.hp_by_node[si] > base.hp_by_node[si]


# --- book_of_five_rings: heal after 5 cards added (drive adds through a run) -

def test_book_of_five_rings_heals_after_five_cards(monkeypatch):
    # Neutralise the shop so the ONLY card adds are the reward-screen picks
    # (a card each): 5 reward screens land by the shop node, tripping exactly
    # one 20-HP heal. The pick-first policy adds a card at every screen.
    from tier05 import shop

    def _noop_shop(rng, character, deck_ids, gold, archetype, policy,
                   removal_uses=0, n_offers=None):
        return shop.ShopOutcome(deck_ids=list(deck_ids), gold=gold,
                                removal_uses=removal_uses, purchases=[])
    monkeypatch.setattr(shop, "visit_shop", _noop_shop)
    monkeypatch.setattr(model, "run_fight", _win_stub(8))

    base = model.run_one(CHAR, ARCH, PILOT, _pick_first, SEED)
    relic = model.run_one(CHAR, ARCH, PILOT, _pick_first, SEED,
                          relics=["book_of_five_rings"])
    # The 5th card is added at the reward screen after the node-6 fight; the
    # +20 heal shows going into the shop node (index 7).
    si = model.node_template().index("$")
    assert base.hp_by_node[si] < BASE_HP
    assert relic.hp_by_node[si] == min(BASE_HP, base.hp_by_node[si] + 20)
    assert relic.hp_by_node[si] > base.hp_by_node[si]


# --- fishing_rod: a deck card gets upgraded after 3 normal wins -------------

def test_fishing_rod_upgrades_after_three_normal_wins(monkeypatch):
    # Skip drafting so the deck only moves via rest-smithing + the fishing
    # upgrade; both runs rest-smith identically (same HP curve under the fixed
    # hit), so the sole delta is fishing_rod's every-3rd-N-win upgrade.
    # Hit 0 (was 8): the v5 pre-E/B lookahead heals any bruised rest arrival,
    # so rests only smith when the run arrives near-full.
    monkeypatch.setattr(model, "run_fight", _win_stub(0))
    base = model.run_one(CHAR, ARCH, PILOT, _skip, SEED)
    relic = model.run_one(CHAR, ARCH, PILOT, _skip, SEED, relics=["fishing_rod"])
    assert _n_upgraded(base.deck_ids) >= 1                  # rests smith too
    assert _n_upgraded(relic.deck_ids) == _n_upgraded(base.deck_ids) + 1


# --- booming_conch: elite fights get extra draw/energy, normals do NOT ------

def test_booming_conch_elite_only_draw_and_energy(monkeypatch):
    records = []
    monkeypatch.setattr(model, "run_fight", _win_stub(0, records))
    model.run_one(CHAR, ARCH, PILOT, _skip, SEED, relics=["booming_conch"])

    kinds = _fight_kinds()
    assert len(records) == len(kinds) == 7
    for kind, rec in zip(kinds, records):
        fx = rec["relic_effects"]
        draw = [e for e in fx if e.get("hook") == "combat_start_draw"]
        energy = [e for e in fx if e.get("hook") == "combat_start_energy"]
        if kind == "E":
            assert any(e["amount"] == 2 for e in draw)     # elite: +2 draw
            assert any(e["amount"] == 1 for e in energy)   # elite: +1 energy
        else:
            assert draw == []                              # normals/boss: none
            assert energy == []


# --- venerable_tea_set / post_rest_energy: +2 energy first combat after rest -

def test_venerable_tea_set_energy_first_combat_after_rest(monkeypatch):
    records = []
    monkeypatch.setattr(model, "run_fight", _win_stub(0, records))
    model.run_one(CHAR, ARCH, PILOT, _skip, SEED, relics=["venerable_tea_set"])

    nodes = model.node_template()
    fight_pos = [i for i, k in enumerate(nodes) if k in ("N", "E", "B")]
    after_rest = {i for i in fight_pos if i > 0 and nodes[i - 1] == "R"}
    assert after_rest == {4, 10}          # fight right after each rest (E, B)

    for pos, rec in zip(fight_pos, records):
        energy = [e for e in rec["relic_effects"]
                  if e.get("hook") == "combat_start_energy"]
        if pos in after_rest:
            assert any(e["amount"] == 2 for e in energy)   # +2 energy post-rest
        else:
            assert energy == []                            # incl. every normal


# --- the lock: relics=None / [] is byte-for-byte the pre-relic run ----------

def test_relics_none_is_byte_for_byte_unchanged():
    # REAL combat (no stub): the None/empty relic path must be dead, so a
    # relic-less run reproduces the pre-relic run decision-for-decision.
    for seed in (1, 2, 3, 7, 11):
        default = model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed)
        variants = [
            model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed,
                          relics=None),
            model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed,
                          relics=[]),
        ]
        for other in variants:
            assert other.deck_ids == default.deck_ids
            assert other.hp_by_node == default.hp_by_node
            assert other.gold == default.gold
            assert other.death_node == default.death_node
            assert other.shop == default.shop
            assert other.rests == default.rests
            assert other.removal_uses == default.removal_uses
            assert [d["picked"] for d in other.decisions] == \
                   [d["picked"] for d in default.decisions]
