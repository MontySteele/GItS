"""EB-233: a non-damage SPEND gets a value the drafter can see.

`SPARK_ALT_VALUE` = 4.00 is a median over five rows that ALL print `damage`,
netted against 0-energy ATTACK baselines. Charged to a sink that prints no
Attack body, it drove every such row NEGATIVE under the flag, so the drafter
could not take one at any bank, on any seed. The fix routes those rows to
`STATIC_SPARK_SPEND_COST` -- the repository's other, already-derived,
damage-free per-Spark price -- and mints no number.

WHAT THIS FILE PINS:

  * the non-damage sink's price MOVES, and lands exactly on the figures
    `STATIC_SPARK_SPEND_COST`'s own disclosure already publishes for the three
    shipped twins (2.00 / 0.00 / 1.00);
  * the DAMAGE sink's price does NOT move -- byte-identical under the flag,
    before and after, which is the intended relationship;
  * the SHIPPED world (flag off) has ONE rate still, for both shapes;
  * an un-informed `spark_spend_cost()` call keeps the DEARER rate, so the
    one-way error direction cannot be lost by a caller that forgets to say;
  * `prints_attack_body` and `_static_power`'s inlined copy of the same test
    agree on every card on the Klee sheet.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card
from tier05 import draft


@pytest.fixture
def alt_cost(monkeypatch):
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", True)
    loader._card_prototype.cache_clear()
    loader._substituted_card_index.cache_clear()
    yield
    loader._card_prototype.cache_clear()
    loader._substituted_card_index.cache_clear()


def _sink(body, ctype="skill", price=2):
    return Card(id="t", name="t", cost=0, type=ctype,
                effects=[{"op": "spend_spark", "amount": price}] + body)


DAMAGE_BODY = [{"op": "damage", "amount": 10, "target": "enemy"}]
BLOCK_BODY = [{"op": "block", "amount": 10}]


# --- the dial itself --------------------------------------------------------

def test_no_new_number_is_minted():
    """The non-damage rate IS `STATIC_SPARK_SPEND_COST`, not a copy of it."""
    assert (draft.SPARK_ALT_NONDAMAGE_SPEND_COST
            == draft.STATIC_SPARK_SPEND_COST == 2.5)
    assert draft.SPARK_ALT_NONDAMAGE_SPEND_COST < draft.SPARK_ALT_VALUE


def test_the_shipped_world_still_has_exactly_one_rate():
    assert not C.SPARK_ALT_COST_ENABLED
    for shape in (True, False, None):
        assert (draft.spark_spend_cost(prints_damage=shape)
                == draft.STATIC_SPARK_SPEND_COST)


def test_an_uninformed_call_keeps_the_dearer_rate(alt_cost):
    """`None` means "the caller did not say" and must never under-charge."""
    assert draft.spark_spend_cost() == draft.SPARK_ALT_VALUE
    assert draft.spark_spend_cost(prints_damage=None) == draft.SPARK_ALT_VALUE
    assert draft.spark_spend_cost(prints_damage=True) == draft.SPARK_ALT_VALUE
    assert (draft.spark_spend_cost(prints_damage=False)
            == draft.SPARK_ALT_NONDAMAGE_SPEND_COST)


# --- the scorer -------------------------------------------------------------

def test_a_non_damage_sinks_score_moves(alt_cost):
    """Block 10 for 2 Sparks: -8 + 10 = 2.00 before, 10 - 5 = 5.00 after."""
    assert draft._static_power(_sink(BLOCK_BODY)) == 5.0


def test_a_damage_sinks_score_does_not_move(alt_cost):
    """10 damage for 2 Sparks stays at 10 - 2 x SPARK_ALT_VALUE."""
    assert draft._static_power(_sink(DAMAGE_BODY, ctype="attack")) == 2.0


def test_a_nested_attack_body_still_counts_as_damage(alt_cost):
    """The read is whole-card: a `damage` behind a branch is an Attack body."""
    nested = _sink([{"op": "conditional", "if": "enemy_intends_attack",
                     "then": DAMAGE_BODY}], ctype="attack")
    assert draft.prints_attack_body(nested)
    assert draft._static_power(nested) < 0.0   # charged the DAMAGE rate


def test_a_bomb_or_detonate_body_is_not_an_attack_body(alt_cost):
    """Both are priced at a SHARE, which is the distinction the dial turns on."""
    for body in ([{"op": "place_bomb", "amount": 6, "target": "enemy"}],
                 [{"op": "detonate", "target": "enemy", "bonus": 4}]):
        assert not draft.prints_attack_body(_sink(body))


# --- the three EB-218 twins, against the already-published figures ----------

#: `STATIC_SPARK_SPEND_COST`'s own disclosure prints these for the SHIPPED
#: twins at 2.5. Under the flag the prototype twins are the same bodies with
#: the Energy deleted, so the alternative-cost arm must reproduce them.
TWIN_SCORES = {"proto_powder_charge_spark": 2.0,     # powder_charge 2.00
               "proto_hold_the_line_spark": 0.0,     # hold_the_line 0.00
               "proto_smoke_and_sparks_spark": 1.0}  # smoke_and_sparks 1.00


@pytest.mark.parametrize("cid,expected", sorted(TWIN_SCORES.items()))
def test_the_twins_land_on_the_published_figures(alt_cost, cid, expected):
    card = loader.peek_card(cid)
    assert not draft.prints_attack_body(card)
    assert draft._static_power(card) == expected


def test_the_twins_were_negative_before_this_row(alt_cost, monkeypatch):
    """The defect, pinned: at ONE rate every twin is unpickable."""
    monkeypatch.setattr(draft, "SPARK_ALT_NONDAMAGE_SPEND_COST",
                        draft.SPARK_ALT_VALUE)
    assert all(draft._static_power(loader.peek_card(c)) < 0.0
               for c in TWIN_SCORES)


@pytest.mark.parametrize("cid", ("proto_kaboom_sink", "proto_spark_strike",
                                 "proto_spark_sweep",
                                 "proto_spark_double_tap",
                                 "proto_spark_blast",
                                 "proto_spark_finisher"))
def test_the_six_damage_sinks_are_unmoved(alt_cost, monkeypatch, cid):
    after = draft._static_power(loader.peek_card(cid))
    monkeypatch.setattr(draft, "SPARK_ALT_NONDAMAGE_SPEND_COST",
                        draft.SPARK_ALT_VALUE)          # the pre-EB-233 world
    assert draft._static_power(loader.peek_card(cid)) == after
    assert draft.prints_attack_body(loader.peek_card(cid))


# --- the two copies of the predicate agree ----------------------------------

def test_the_helper_and_the_inlined_read_agree_on_the_whole_sheet(alt_cost):
    from tier05 import rewards
    rewards.character_pool.cache_clear()
    pool = rewards.character_pool("klee")
    cards = [c for tier in pool.values() for c in tier]
    assert cards
    for card in cards:
        inlined = any(fx.get("op") in draft.STATIC_ATTACK_BODY_OPS
                      for fx in draft._nested_effects(card.effects))
        assert draft.prints_attack_body(card) is inlined
    rewards.character_pool.cache_clear()
