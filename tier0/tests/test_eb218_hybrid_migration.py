"""EB-218 -- the three hybrid spenders go SPARK-ONLY under the flag.

R224 (2026-08-30) took sec.14.3 option (5) of
`review/active/klee-sparks-2026-08-29.md` and ruled its branch: `powder_charge`,
`hold_the_line` and `smoke_and_sparks` -- the three shipped Klee spenders whose
payoff is not a plain Attack, all three HYBRIDS at 1 Energy AND `spend_spark 2`
-- migrate to 0 Energy with the price paid WHOLLY in Sparks. It is a
**dev-only substitution**, not a shipped-pool edit: the same seam the eight
prototype rows already use (`loader._pool_substitutions`' Klee half, under
`C.SPARK_ALT_COST_ENABLED`, off `C.SPARK_ALT_POOL_SUBS`), and with the flag OFF
the pool is byte-identical to shipped.

NOTHING IS REPRICED, and that is asserted here rather than described: each
migrated row carries its shipped Spark number (2) and its shipped body, and the
only delta between twin and shipped row is the Energy.

The flag-off half is pinned as a DIGEST of the whole offerable pool -- every
rarity, every id, name, cost, type and effect list -- taken on this branch's
parent (`ae9dcde`) before a byte of the migration existed. A prose claim that
"the pool did not move" is worth nothing; this is worth exactly as much as the
pool is deterministic, which it is.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
"""

import hashlib
import json

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine.combat import card_playable, spark_cost
from tier0.tests.conftest import make_state
from tier05 import rewards

# {shipped id: migrated prototype id}, the R224 half of the substitution map.
MIGRATED = {
    "powder_charge": "proto_powder_charge_spark",
    "hold_the_line": "proto_hold_the_line_spark",
    "smoke_and_sparks": "proto_smoke_and_sparks_spark",
}

# The digest of the flag-off Klee pool, MEASURED on ae9dcde (this branch's
# parent) before the migration was written. See the module docstring.
SHIPPED_POOL_DIGEST = (
    "59df435117c2a53712159cd59817ecd0f11623b6e2c5a09eb9cc18642ac7a3a2")


def _clear():
    """Every memo a flag flip invalidates. `character_pool` is `lru_cache`d
    and reads the substitution map, so a test that flips without clearing it
    reads the other arm."""
    loader._card_prototype.cache_clear()
    loader._substituted_card_index.cache_clear()
    rewards.character_pool.cache_clear()


@pytest.fixture
def alt_cost(monkeypatch):
    _clear()
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", True)
    yield
    _clear()


def pool_view(character="klee"):
    """The offerable pool as plain data -- what an offer screen can show."""
    pool = rewards.character_pool(character)
    return {rarity: [{"id": c.id, "name": c.name, "cost": c.cost,
                      "type": c.type, "effects": c.effects}
                     for c in cards]
            for rarity, cards in pool.items()}


def pool_digest(character="klee") -> str:
    return hashlib.sha256(
        json.dumps(pool_view(character), sort_keys=True, default=str
                   ).encode("utf-8")).hexdigest()


def proto(card_id):
    return next(c for c in loader.prototype_cards() if c.id == card_id)


# --- 1. FLAG OFF IS BYTE-IDENTICAL -----------------------------------------

def test_the_flag_ships_off():
    assert C.SPARK_ALT_COST_ENABLED is False


def test_the_shipped_pool_is_unmoved_with_the_flag_off():
    """THE ACCEPTANCE CONDITION, as a digest of the whole pool rather than a
    claim about it. A shipped-pool edit would move this; a dev-only
    substitution behind a flag cannot."""
    _clear()
    assert pool_digest() == SHIPPED_POOL_DIGEST


def test_the_three_hybrids_are_still_hybrids_with_the_flag_off():
    """The shipped faces, unmoved: 1 Energy AND a top-level Spend 2."""
    _clear()
    for shipped in MIGRATED:
        card = loader.get_card(shipped)
        assert card.cost == 1
        assert spark_cost(card) == 2


def test_no_migrated_row_is_reachable_with_the_flag_off():
    _clear()
    ids = {c["id"] for cards in pool_view().values() for c in cards}
    for shipped, migrated in MIGRATED.items():
        assert shipped in ids
        assert migrated not in ids


def test_the_pool_diff_between_the_two_flag_states_is_exactly_the_swap(
        monkeypatch):
    """The diff itself, both directions, as ONE test -- because the claim
    ("flag off byte-identical, flag on exactly these swaps") is a
    COMPARISON and reads wrong as two separate assertions."""
    _clear()
    off = {c["id"] for cards in pool_view().values() for c in cards}
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", True)
    _clear()
    on = {c["id"] for cards in pool_view().values() for c in cards}
    _clear()

    assert off - on == set(C.SPARK_ALT_POOL_SUBS)
    assert on - off == set(C.SPARK_ALT_POOL_SUBS.values())
    for shipped, migrated in MIGRATED.items():
        assert shipped in off - on
        assert migrated in on - off


# --- 2. FLAG ON: 0 ENERGY, THE PRINTED SPARK PRICE -------------------------

@pytest.mark.parametrize("shipped,migrated", sorted(MIGRATED.items()))
def test_the_migrated_row_is_zero_energy_at_the_shipped_spark_price(
        alt_cost, shipped, migrated):
    old = loader.get_card(shipped)
    new = proto(migrated)

    assert old.cost == 1 and new.cost == 0        # the whole delta
    assert spark_cost(new) == spark_cost(old) == 2  # and NOT a reprice
    assert new.type == old.type
    assert new.rarity == old.rarity               # the offer odds do not move


@pytest.mark.parametrize("shipped,migrated", sorted(MIGRATED.items()))
def test_the_body_did_not_move(alt_cost, shipped, migrated):
    """A migration that also changed a body would confound sec.14.4's
    question. Everything after the price is the shipped row's, verbatim."""
    assert proto(migrated).effects == loader.get_card(shipped).effects


@pytest.mark.parametrize("shipped,migrated", sorted(MIGRATED.items()))
def test_the_bank_alone_reaches_it_and_pays_exactly_the_price(
        alt_cost, shipped, migrated):
    """The point of the migration: energy-gating is what stopped a hybrid
    from ever competing with the bank, so a null read on one would have
    measured the gate rather than the sink."""
    card = proto(migrated)
    state = make_state()
    state.player.energy = 0                       # NO energy at all

    state.player.sparks = 1
    assert not card_playable(state, card)         # the gate, one short

    state.player.sparks = 2
    assert card_playable(state, card)             # ... on the bank alone
    state.player.hand.append(card)
    combat.play_card(state, card)
    assert state.player.sparks == 0               # paid, exactly
    assert state.player.energy == 0               # and nothing else charged


def test_the_shipped_hybrid_is_gone_from_the_pool_under_the_flag(alt_cost):
    ids = {c["id"] for cards in pool_view().values() for c in cards}
    for shipped, migrated in MIGRATED.items():
        assert shipped not in ids, "a migrated row must not also be offered"
        assert migrated in ids


def test_the_migrated_rows_are_the_only_non_attack_sinks_on_the_arm(alt_cost):
    """The reason option (5) is prior to re-authoring: after the migration
    the priced-sink economy already HAS non-damage destinations, which is
    what candidates 3, 5, 6 and 7 were proposed to create."""
    non_attack = {cid for cid in C.SPARK_ALT_POOL_SUBS.values()
                  if proto(cid).type != "attack" and spark_cost(proto(cid))}
    assert non_attack == set(MIGRATED.values())
