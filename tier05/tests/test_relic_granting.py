"""W2 relic-GRANTING cadence: the sites where a ``grant_relics=True`` run
accrues relics through the StS Act-1 loop -- the Neow run-start pick, the
treasure (T) lump, elite (E) / boss (B) wins, and shop stock. The run-layer
application (pickup effects, HeldRelics bookkeeping) is proven in
test_relics_runlayer; THIS module pins the CADENCE: which node kinds grant and
which do not, that a grant is never a duplicate, that owner-locked relics only
reach their owner, and that an exhausted pool degrades to "grant nothing"
instead of crashing.

Isolation trick: to prove a SINGLE node kind grants, we monkeypatch
``model.node_template`` to a one-node run and diff its ``res.relics`` against
the Neow-only baseline (an empty template). The Neow pick is computed before
the node loop from the same run rng, so it is byte-identical across templates
and the delta is exactly the node under test. Combat is stubbed to a
deterministic win (the ``_win`` trick from the shop/runlayer suites) so a
grant that rides on a WON fight actually fires and the run reaches every site.
"""

import random

import pytest

from tier0 import constants as C
from tier0.engine.state import CombatState
from tier05 import draft, model
from tier05 import relics as relic_pool


@pytest.fixture(autouse=True)
def _single_act(monkeypatch):
    """§10 re-stamp: this suite asserts ACT-1 granting cadence (one Neow,
    one treasure, 2 elites + 1 boss). Pin the registry so acts 2-3 never
    silently double the grants under test."""
    monkeypatch.setattr(C, "RUN_ACTS", C.RUN_ACTS[:1])

CHAR, ARCH, PILOT = "klee", "demolition", "demolition"
# ref_ironclad is the committed reference character (real_ironclad is a
# gitignored local artifact); red_skull is owner-locked to both ironclads.
IC_CHAR, IC_ARCH, IC_PILOT = "ref_ironclad", "ironclad", "ironclad"
SEED = 7


# --- combat stub: every fight is an instant win, player untouched -----------

def _win_stub(player, enemies, pilot, seed):
    for e in enemies:
        e.hp = 0
    return CombatState(player=player, enemies=enemies,
                       rng=random.Random(seed))


def _skip(rng, deck, offers, archetype):
    return None


def _neow_pick(seed, character):
    """Reproduce run_one's Neow pick: the offer is the FIRST draw off
    random.Random(seed) (the banner uses a separate stream), so this replays
    it exactly."""
    rng = random.Random(seed)
    return relic_pool.neow_pick(relic_pool.neow_offer(rng), character)


def _run(monkeypatch, template, seed=SEED, character=CHAR, arch=ARCH,
         pilot=PILOT):
    """A grant_relics run over a custom node template, combat stubbed to win."""
    monkeypatch.setattr(model, "run_fight", _win_stub)
    monkeypatch.setattr(model, "node_template", lambda: list(template))
    return model.run_one(character, arch, pilot, _skip, seed,
                         grant_relics=True)


# --- a grant run ends holding >=1 relic, and the Neow relic is present -------

def test_grant_run_holds_relic_including_the_neow_pick(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub)
    res = model.run_one(CHAR, ARCH, PILOT, _skip, SEED, grant_relics=True)
    assert res.relics                                   # holds >= 1 relic
    pick = _neow_pick(SEED, CHAR)
    assert pick is not None
    assert pick in res.relics                           # the Neow relic is held
    # The won run reached the treasure/elite/boss/shop sites too, so it holds
    # more than just the Neow relic.
    assert res.won
    assert len(res.relics) > 1


def test_grant_relics_false_grants_nothing():
    # The negative control: without grant_relics the cadence is dead even under
    # a completing run -- res.relics stays empty (W1 world intact).
    res = model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, SEED)
    assert res.relics == []


# --- the treasure (T) node grants one relic beyond the Neow baseline --------

def test_treasure_node_grants_a_relic(monkeypatch):
    baseline = _run(monkeypatch, "").relics               # Neow only
    across_t = _run(monkeypatch, "T").relics              # Neow + T grant
    assert set(baseline) <= set(across_t)
    assert len(across_t) == len(baseline) + 1             # held count rose by 1
    granted = [r for r in across_t if r not in baseline]
    assert granted[0] in relic_pool.common_pool()         # from the Common pool


# --- an elite win and a boss win each grant; a normal win does NOT ----------

def test_elite_and_boss_grant_but_normal_does_not(monkeypatch):
    baseline = _run(monkeypatch, "").relics
    normal = _run(monkeypatch, "N").relics
    elite = _run(monkeypatch, "E").relics
    boss = _run(monkeypatch, "B").relics

    assert normal == baseline                             # N win grants nothing
    assert len(elite) == len(baseline) + 1                # E win grants 1
    assert len(boss) == len(baseline) + 1                 # B win grants 1
    for got in (elite, boss):
        assert set(baseline) <= set(got)
        assert [r for r in got if r not in baseline][0] in relic_pool.common_pool()


# --- no relic id is ever granted twice in a run -----------------------------

def test_no_duplicate_relic_ever_granted(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub)     # reach every site
    for seed in range(40):
        res = model.run_one(CHAR, ARCH, PILOT, _skip, seed, grant_relics=True)
        assert len(res.relics) == len(set(res.relics))     # dup-free


# --- owner gating: klee never holds red_skull; an ironclad can --------------

def test_owner_gating_pool_eligibility():
    # The gate at ROLL time: red_skull is offered to an ironclad but never to
    # klee, so klee can never be granted it in the first place.
    assert "red_skull" not in relic_pool.unowned_common([], "klee")
    assert "red_skull" in relic_pool.unowned_common([], "ref_ironclad")


def test_klee_never_granted_red_skull(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub)
    for seed in range(40):
        res = model.run_one(CHAR, ARCH, PILOT, _skip, seed, grant_relics=True)
        assert "red_skull" not in res.relics


def test_ironclad_can_be_granted_red_skull(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub)
    holders = [seed for seed in range(40)
               if "red_skull" in model.run_one(
                   IC_CHAR, IC_ARCH, IC_PILOT, _skip, seed,
                   grant_relics=True).relics]
    assert holders                                         # at least one run held it


# --- exhausted pool: grant nothing rather than crash, still dup-free --------

def test_exhausted_common_pool_grants_nothing_not_crash(monkeypatch):
    # Shrink the Common pool to two ids: the ~6 grant sites in a full run far
    # outnumber it, so most sites find the pool exhausted. roll_relic_reward
    # must return None there (never crash, never re-grant a held id).
    full = relic_pool.common_pool()
    tiny = {k: full[k] for k in ("anchor", "vajra")}
    monkeypatch.setattr(relic_pool, "common_pool", lambda: tiny)
    monkeypatch.setattr(model, "run_fight", _win_stub)
    for seed in range(12):
        res = model.run_one(CHAR, ARCH, PILOT, _skip, seed,
                            grant_relics=True)          # no exception
        assert len(res.relics) == len(set(res.relics))  # no duplicate granted
        commons = [r for r in res.relics if r in tiny]
        assert len(commons) <= len(tiny)                # capped by the pool


# --- determinism: same seed + grant_relics -> identical res.relics ----------

def test_determinism_same_seed_identical_relics():
    for seed in (1, 2, 3, 7, 11):
        a = model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed,
                          grant_relics=True)
        b = model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed,
                          grant_relics=True)
        assert a.relics == b.relics
