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

def test_the_starter_is_ten_cards_six_ids():
    """Slice packet sec.3, DRAFT 3: Kaboom! x2, Ka-pow! x2, Duck and Cover x3,
    Dig In, Pop!, Jumpy Dumpty.

    The two copy counts are the draft's whole point: draft 2 put *Set off* on
    every starter Attack, so the plain hit and the cash button were one card
    and nothing ever grew. Dig In moved in from the pool, which is why it is
    also absent from `KLEE_OVERHAUL_POOL_IDS` below.
    """
    ids = C.KLEE_OVERHAUL_STARTER_IDS
    assert len(ids) == 10
    assert len(set(ids)) == 6
    assert ids.count("proto_ko_kaboom") == 2
    assert ids.count("proto_ko_kapow") == 2
    assert ids.count("proto_ko_duck_and_cover") == 3
    assert ids.count("proto_ko_dig_in") == 1
    assert ids.count("proto_ko_pop") == 1
    assert ids.count("proto_ko_jumpy_dumpty") == 1


def test_the_pool_is_the_slices_rows_minus_vermillion_pact():
    """Slice packet sec.4, less the one row its sec.5 allows to drop and the
    one draft 3 moved into the starter.

    The count is pinned rather than described because it is the slice's own
    scope statement, and because the ABSENCE is the load-bearing half: an
    unbuilt rule staged as a live card would be a face that lies (D4). See
    `VermillionPactNotBuilt` for the reasoning and `C.KLEE_OVERHAUL_POOL_IDS`
    for the record.

    The last assertion is the one that says Dig In left: the starter and the
    offer pool are disjoint, so a card in both would fail here rather than
    quietly double as a reward.
    """
    ids = C.KLEE_OVERHAUL_POOL_IDS
    assert len(ids) == 26
    assert len(set(ids)) == 26
    assert "proto_ko_vermillion_pact" not in ids
    assert "proto_ko_dig_in" not in ids
    assert not set(ids) & set(C.KLEE_OVERHAUL_STARTER_IDS)


def test_the_numbers_are_the_briefs_placeholders():
    """Slice packet sec.1: no number in it is a claim. These four are the
    rules' own, and they are named so `lint_constant_parity` can compare the
    C# mirrors BY VALUE."""
    assert C.KLEE_OVERHAUL_BOMB_GROWTH == 2
    assert C.KLEE_OVERHAUL_WORKSHOP_GROWTH == 1
    assert C.KLEE_OVERHAUL_ALICE_GROWTH == 4
    assert C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION == 1


# --- 3. THE FLAG ON: the rows are reachable, and only these rows -----------

def test_the_starter_resolves_to_the_slices_ten_cards(overhaul):
    """`starting_deck` is the ONE seam both the tier 0 battery and the tier 0.5
    run read, so this is what she opens with on either path."""
    ids = loader.starting_deck("klee")
    assert ids == list(C.KLEE_OVERHAUL_STARTER_IDS)
    assert all(cid.startswith("proto_ko_") for cid in ids)
    # And each one is a real, loadable, validated card -- not just a string.
    for cid in set(ids):
        card = loader.get_card(cid)
        assert card.character == "klee"
        assert card.id == cid


def test_the_offerable_pool_is_the_slice_and_nothing_else(overhaul):
    """`rewards.character_pool` is the single source of truth for every offer
    surface -- fight rewards, the shop, every event card screen and the tier
    0.5 drafter -- so this one assertion covers all five."""
    pool = rewards.character_pool("klee")
    ids = {c.id for cards in pool.values() for c in cards}
    assert ids == set(C.KLEE_OVERHAUL_POOL_IDS)
    assert not any(cid.startswith("proto_ko_")
                   and cid in C.KLEE_OVERHAUL_STARTER_IDS for cid in ids)


def test_the_pool_keeps_the_packets_rarity_split(overhaul):
    """11 Common, 10 Uncommon, 5 Rare -- the packet's sec.4 count with
    Vermillion Pact removed and Dig In moved into the starter (draft 3, which
    is also what made its row `rarity: basic`). Pinned because the rarity
    buckets ARE the offer odds: a row filed in the wrong tier changes how often
    it is seen."""
    pool = rewards.character_pool("klee")
    assert {r: len(cs) for r, cs in sorted(pool.items())} == {
        "common": 11, "uncommon": 10, "rare": 5}


def test_no_other_character_moves_under_the_flag(overhaul):
    """The seam is Klee's alone. A flag that quietly re-pooled Furina would
    make every number measured on her incomparable."""
    for character in ("furina", "kokomi"):
        assert loader.pool_replacement(character) is None
        ids = {c.id for cards in rewards.character_pool(character).values()
               for c in cards}
        assert not any(cid.startswith("proto_ko_") for cid in ids)


# --- 4. THE OPS ARE REGISTERED AND REFUSE TO RUN ---------------------------

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


# --- 5. THE PROTOTYPE-STAGE UPGRADE RULE (EB-283, closing EB-277) ----------
#
# The rule lives in `tier0.content.upgrades` and `tools/gen_prototype_cards.py`
# IMPORTS it, so there is one implementation and no mirror to keep in step.
# That is what these pins are about: the numbers the row states, the clause
# that leaves a row alone, and the fact that the whole thing is still behind
# the flag.

def test_the_prototype_rule_states_the_rows_own_numbers():
    """`EB-283` verbatim: damage +3 (+1 per hit on multi-hit), Block +3,
    Bomb/Mine size +2 (payload Mine +1), grow and power amounts +1, Tide and
    Mend +2. Read off the rows themselves rather than retyped, so a sheet edit
    that moved one of these ops would move the assertion with it."""
    from tier0.content import upgrades

    def delta(card_id):
        card = next(c for c in loader.prototype_cards() if c.id == card_id)
        return upgrades.prototype_default_delta(card.id, card.cost, card.effects)

    assert delta("proto_ko_kaboom") == {"damage": 3}
    assert delta("proto_ko_kapow") == {"damage": 3}          # a set_off's hit
    assert delta("proto_ko_rapid_fire") == {"damage": 1}     # 4 hits: +1 each
    assert delta("proto_ko_duck_and_cover") == {"block": 3}
    assert delta("proto_ko_pop") == {"bomb_size": 2}
    assert delta("proto_ko_jumpy_dumpty") == {"bomb_size": 2, "payload_mine": 1}
    assert delta("proto_ko_chain_fuse") == {"grow": 1}
    assert delta("proto_ko_careful_arrangement") == {"grow": 1}
    assert delta("proto_ko_grounded") == {"power_amount": 1}
    # Kokomi's half of the rule, on DRAFT 6's rows. `tide` left the key list
    # with the verb it read (`gain_tide`), so what is left of her side is the
    # shared Block and Mend clauses -- which is the whole point of a rule
    # written over ops rather than over characters.
    assert delta("proto_kk_coral_bulwark") == {"block": 3}
    assert delta("proto_kk_the_moon_a_ship") == {"mend": 2}


def test_the_cost_clause_is_the_last_resort_and_only_at_two():
    """"A card of cost 2 or more WITH NO NUMBER costs 1 less" -- so the clause
    fires only when nothing else did, and a 0- or 1-cost row with no printed
    number gets no upgrade rather than an invented one. That is why a handful
    of rows are still base-only, and it is a decision rather than a gap."""
    from tier0.content import upgrades

    assert upgrades.prototype_default_delta(
        "proto_kk_the_moon_overlooks_the_waters", 2, [
            {"op": "apply_power", "power": "kk_plans_also_now", "amount": 1,
             "target": "self"}]) == {"cost": -1}
    # The same row at cost 1: nothing to move, and nothing invented.
    assert upgrades.prototype_default_delta(
        "proto_kk_treatise", 1, [
            {"op": "apply_power", "power": "kk_treatise", "amount": 1,
             "target": "self"}]) == {}
    # A row that DID find a number never also gets the discount.
    assert "cost" not in upgrades.prototype_default_delta(
        "proto_kk_the_moon_a_ship", 2, [{"op": "mend", "amount": 10}])


def test_a_power_amount_of_one_is_read_as_no_number():
    """The `> 1` test, which is the rule's one judgement call and is made in
    one place. A power's `amount` is a printed number on some rows (Grounded's
    6 Block) and a bare ON FLAG on others (Alice's Recipe, Sparks 'n' Splash,
    The Art of War), and nothing on the row tells them apart -- so a 1 is read
    as "prints no power number" and a Balance-stage `upgrade:` block is what
    gives such a card a real one."""
    from tier0.content import upgrades

    flag = [{"op": "apply_power", "power": "ko_alices_recipe", "amount": 1,
             "target": "self"}]
    printed = [{"op": "apply_power", "power": "ko_grounded", "amount": 6,
                "target": "self"}]
    assert upgrades.prototype_default_delta("proto_ko_x", 1, flag) == {}
    assert upgrades.prototype_default_delta("proto_ko_x", 1, printed) == {
        "power_amount": 1}


def test_the_rule_reaches_only_the_four_overhaul_prefixes():
    """The staged Sparks rows and the two Kokomi probes are not overhaul rows
    and are not the rule's to price: they were staged base-only on purpose and
    stay that way."""
    from tier0.content import upgrades

    hit = [{"op": "damage", "amount": 6, "target": "enemy"}]
    assert upgrades.prototype_default_delta("proto_spark_strike", 1, hit) == {}
    assert upgrades.prototype_default_delta("kaboom", 1, hit) == {}
    for prefix in upgrades.PROTOTYPE_DEFAULT_PREFIXES:
        assert upgrades.prototype_default_delta(prefix + "x", 1, hit) == {
            "damage": 3}


def test_no_prototype_row_is_upgradable_with_the_flags_off():
    """The quarantine, unmoved. `_prototype_deltas` registers a row only if a
    live flag already resolves its id, so on a shipped tree the index is
    byte-identical to what it was before this rule existed."""
    from tier0.content import upgrades

    upgrades._prototype_upgrade_index.cache_clear()
    upgrades._upgrade_index.cache_clear()
    try:
        assert not upgrades.has_upgrade("proto_ko_kapow")
        assert not upgrades.has_upgrade("proto_kk_treatise")
    finally:
        upgrades._prototype_upgrade_index.cache_clear()
        upgrades._upgrade_index.cache_clear()


def test_under_the_flag_a_prototype_row_smiths_into_a_different_card(overhaul):
    """`EB-277`'s close in the sim: the upgraded card is NOT the base card.
    Through the real applier, so this is the rest-smith's own result."""
    from tier0.content import upgrades

    upgrades._prototype_upgrade_index.cache_clear()
    upgrades._upgrade_index.cache_clear()
    try:
        assert upgrades.has_upgrade("proto_ko_kapow")
        upgraded = loader.get_card("proto_ko_kapow+")
        base = loader.get_card("proto_ko_kapow")
        assert upgraded.effects != base.effects
        assert upgraded.effects[0]["damage"] == 10      # 7 + 3
        assert base.effects[0]["damage"] == 7
        # The Spark price is never what the campfire moved.
        dig = loader.get_card("proto_ko_dig_in+")
        assert [f for f in dig.effects if f["op"] == "spend_spark"] == [
            {"op": "spend_spark", "amount": 1}]
        assert [f["amount"] for f in dig.effects if f["op"] == "block"] == [11]
    finally:
        upgrades._prototype_upgrade_index.cache_clear()
        upgrades._upgrade_index.cache_clear()
