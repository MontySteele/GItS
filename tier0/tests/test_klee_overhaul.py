"""The Klee overhaul arm (slice one) -- the flag, and both sides of it.

The ruled brief is `review/active/klee-brief-2026-09-01.md` (sec.3, the seven
rules; sec.8, the starter and the relic) and the slice is
`review/active/klee-overhaul-slice-1-2026-09-01.md` (sec.3 the ten-card
starter, sec.4 the 28 pool rows, sec.5 the engine build list).

THE FIRST SECTION IS THE ONE THAT MATTERS. `C.KLEE_OVERHAUL` ships OFF, and
with it off every Klee number ever measured is still comparable and the Sparks
arm beside it still owns its own seams. That is an ACCEPTANCE CONDITION, not an
intention, so it is pinned the way `test_spark_alt_cost.py` pins its own: as a
digest of a fixed-seed fight's whole event log, plus the shape of every seam
this arm touches.

WHAT THE SIM DOES AND DOES NOT DO HERE. Slice one is C# FIRST (the slice packet
sec.5: "All of it goes behind the prototype switch, C# first, per the ruled
process... The Python sim is not brought up for slice one"). So tier0 LOADS,
VALIDATES and RESOLVES-BY-ID the slice's rows, and it REFUSES to resolve their
new ops rather than shipping a second, unplayed implementation of a rule the
mod has not proved yet. `test_the_new_ops_refuse_to_resolve` is that refusal
asserted, not tolerated.

NOTHING MEASURED ON ANY PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import hashlib
import json

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.engine.combat import run_fight
from tier0.pilot.policy import make_pilot
from tier05 import draft, rewards

SEED = 7

#: Every op slice one adds. Registered in `effects.OPS` so the loader's
#: vocabulary check accepts a row, priced in `draft.STATIC_OP_PRICING` so
#: `lint_op_parity` stays green, and resolved by nothing.
OVERHAUL_OPS = ("set_off", "plant_bomb", "grow_bombs", "merge_bombs",
                "remove_bomb_for_block", "damage_set_off_total",
                "double_set_off", "draw_per_set_off")


@pytest.fixture
def overhaul(monkeypatch):
    """The flag ON, with every id-resolving cache cleared on both sides.

    `_card_prototype` is memoized and its answer for a `proto_` id DEPENDS on
    the flag, so a test that flips the flag without clearing it would read a
    KeyError cached from an earlier test. `rewards.character_pool` is memoized
    too and its answer moves with the same flag. Cleared going in and out.
    """
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    yield
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()


def klee_fight(seed=SEED):
    pilot = make_pilot(loader.pilot_weights("demolition"))
    player = loader.build_player("klee")
    return run_fight(player, loader.build_encounter("punisher"), pilot,
                     seed=seed)


def log_digest(state) -> str:
    return hashlib.sha256(
        json.dumps(state.log, sort_keys=True, default=str
                   ).encode("utf-8")).hexdigest()


# --- 1. FLAG OFF IS BYTE-IDENTICAL -----------------------------------------

def test_the_flag_ships_off():
    """The quarantine. Everything below only matters while this holds."""
    assert C.KLEE_OVERHAUL is False


def test_a_fixed_seed_klee_fight_is_unchanged_with_the_flag_off():
    """THE ACCEPTANCE CONDITION, as a digest of the whole log.

    The same fight and the same digest `test_spark_alt_cost.py` pins, and
    deliberately the same literal: the two arms make the same promise about
    the same fight, and two different numbers for it would mean one of them
    had quietly moved the tree the other measured on.
    """
    assert log_digest(klee_fight()) == (
        "20b877d3411ccdc5306f6b8c0664c8d0f0dd7f9b30421d73af411aa8c3dbe9fa")


def test_the_starter_is_the_printed_starter_with_the_flag_off():
    assert loader.starting_deck("klee") == [
        "kaboom", "kaboom", "kaboom", "kaboom",
        "duck_and_cover", "duck_and_cover", "duck_and_cover", "duck_and_cover",
        "jumpy_dumpty", "pop"]


def test_no_pool_is_replaced_with_the_flag_off():
    """The new seam returns None for everybody, so `character_pool` never
    enters its branch and is byte-for-byte the function it has always been."""
    for character in ("klee", "furina", "kokomi", "ref_ironclad",
                      "real_silent"):
        assert loader.pool_replacement(character) is None


def test_the_offerable_pool_carries_no_overhaul_row_with_the_flag_off():
    pool = rewards.character_pool("klee")
    ids = {c.id for cards in pool.values() for c in cards}
    assert not any(cid.startswith("proto_ko_") for cid in ids)
    # The shipped pool, still there and still hers: `big_badda_boom` is a
    # SHIPPED Klee row whose name the slice re-uses, so this also says the two
    # cannot be confused for one another.
    assert "big_badda_boom" in ids


def test_the_overhaul_ids_do_not_resolve_with_the_flag_off():
    """The quarantine's own door, shut. `_card_prototype`'s prototype branch
    is guarded by the flags, so a `proto_ko_` id is a KeyError here -- which
    is what makes "the rows never enter an ordinary run" a property of the
    code rather than a filter somebody remembers."""
    loader._card_prototype.cache_clear()
    with pytest.raises(KeyError):
        loader.get_card(C.KLEE_OVERHAUL_STARTER_IDS[0])
    loader._card_prototype.cache_clear()


def test_the_sparks_arm_is_untouched():
    """The overhaul is a THIRD arm. Editing the Sparks arm's constants would
    make its OFF/ON pair incomparable, which is the one thing a two-arm flag
    exists to prevent."""
    assert C.SPARK_ALT_COST_ENABLED is False
    assert dict(C.SPARK_ALT_STARTER_SUBS) == {
        "pop": "proto_pop_spark", "kaboom": "proto_kaboom_sink"}
    assert len(C.SPARK_ALT_POOL_SUBS) == 9
    assert C.KURAGE_MEMORY is False or C.KURAGE_MEMORY is True   # still there


# --- 2. THE ARM'S OWN SHAPE ------------------------------------------------

def test_the_starter_is_ten_cards_five_ids():
    """Slice packet sec.3: Kaboom! x3, Ka-pow! x1, Duck and Cover x4, Pop!,
    Jumpy Dumpty."""
    ids = C.KLEE_OVERHAUL_STARTER_IDS
    assert len(ids) == 10
    assert len(set(ids)) == 5
    assert ids.count("proto_ko_kaboom") == 3
    assert ids.count("proto_ko_kapow") == 1
    assert ids.count("proto_ko_duck_and_cover") == 4
    assert ids.count("proto_ko_pop") == 1
    assert ids.count("proto_ko_jumpy_dumpty") == 1


def test_the_pool_is_twenty_eight_distinct_rows():
    """Slice packet sec.4. The count is the slice's own scope statement --
    'the ten-card starter plus 28 pool cards' -- so it is pinned, not
    described."""
    ids = C.KLEE_OVERHAUL_POOL_IDS
    assert len(ids) == 28
    assert len(set(ids)) == 28
    assert not set(ids) & set(C.KLEE_OVERHAUL_STARTER_IDS)


def test_the_numbers_are_the_briefs_placeholders():
    """Slice packet sec.1: no number in it is a claim. These four are the
    rules' own, and they are named so `lint_constant_parity` can compare the
    C# mirrors BY VALUE."""
    assert C.KLEE_OVERHAUL_BOMB_GROWTH == 2
    assert C.KLEE_OVERHAUL_WORKSHOP_GROWTH == 1
    assert C.KLEE_OVERHAUL_ALICE_GROWTH == 4
    assert C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION == 1


# --- 3. THE OPS ARE REGISTERED AND REFUSE TO RUN ---------------------------

def test_every_new_op_is_registered():
    """The loader validates `op:` NAMES at load (`_validate_effect_vocabulary`),
    so a row carrying an unregistered op cannot be staged at all."""
    for op in OVERHAUL_OPS:
        assert op in effects.OPS, op


def test_every_new_op_is_priced_for_the_drafter():
    """`lint_op_parity`'s discipline, asserted here too: registering an op
    forces a pricing decision at the moment the author knows the answer."""
    for op in OVERHAUL_OPS:
        assert op in draft.STATIC_OP_PRICING, op


def test_the_new_ops_refuse_to_resolve():
    """C# FIRST, said out loud. The slice packet does not bring the sim up,
    and a silently no-op resolver would be the worst possible stand-in: a
    prototype that reports numbers for rules it never ran."""
    from tier0.tests.conftest import make_state
    from tier0.engine.state import Card

    for op in OVERHAUL_OPS:
        state = make_state()
        card = Card(id="probe", name="probe", cost=1, type="attack",
                    effects=[{"op": op}])
        with pytest.raises(NotImplementedError) as excinfo:
            effects.OPS[op](state, {"op": op}, card)
        assert "KLEE_OVERHAUL" in str(excinfo.value)
