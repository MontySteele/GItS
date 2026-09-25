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

#: Every op the arm has: slice one's eight, plus R244's `hexerei_mark_hand`,
#: R252's `block_largest_bomb` and the round-11 pool pass's
#: `grow_largest_bomb`. Registered in `effects.OPS` so the loader's
#: vocabulary check accepts a row, priced in `draft.STATIC_OP_PRICING` so
#: `lint_op_parity` stays green, and resolved only with the flag on and Klee in
#: the seat.
OVERHAUL_OPS = ("set_off", "plant_bomb", "grow_bombs", "merge_bombs",
                "remove_bomb_for_block", "block_largest_bomb",
                "grow_largest_bomb", "damage_set_off_total",
                "multiply_set_off", "draw_per_set_off", "companion_mark_hand",
                "mine_bombs")


@pytest.fixture
def overhaul(monkeypatch):
    """The flag ON, with every id-resolving cache cleared on both sides.

    `_card_prototype` is memoized and its answer for a `proto_` id DEPENDS on
    the flag, so a test that flips the flag without clearing it would read a
    KeyError cached from an earlier test. `rewards.character_pool` is memoized
    too and its answer moves with the same flag. Cleared going in and out.

    THE TWO UPGRADE INDICES JOINED THEM (2026-09-05). They are memoized on the
    same flag -- a prototype row is upgradable only with the arm on -- and a
    test that resolved a `proto_` card here left a populated index behind for
    `test_no_prototype_row_is_upgradable_with_the_flags_off` and
    `test_the_overhaul_ids_do_not_resolve_with_the_flag_off` to read on the
    same xdist worker, which is exactly the intermittent pair those two turned
    into. Three tests below already cleared them by hand in a `finally`; doing
    it here is that discipline moved to the one door every arm test passes
    through, and their own clears are left where they are because a test that
    does not take this fixture still needs them.

    AND THE FOURTH WAS THE SECOND LEAKER (`EB-569`, reopened 2026-09-06).
    Naming caches by hand is how one gets missed, and the one that was missed
    is `loader._substituted_card_index`: it is built from `_starter_ids` and
    `_pool_substitutions`, both of which READ THE FLAGS, so warming it once
    under this fixture leaves `proto_ko_jumpy_dumpty` and `proto_ko_kapow` in
    it for the rest of the worker's life -- after which
    `get_card("proto_ko_kapow")` no longer raises and `has_upgrade` says yes,
    which is exactly the pair above failing about one run in three. The list
    is now `loader.reset_arm_caches()`, stated once beside the flags it
    depends on; `rewards.character_pool` stays here because tier0 may not
    import tier05.
    """
    def _clear():
        loader.reset_arm_caches()
        rewards.character_pool.cache_clear()

    _clear()
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    yield
    _clear()


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
    code rather than a filter somebody remembers.

    NAMED, not read off `KLEE_OVERHAUL_STARTER_IDS[0]`, since draft 4 (R242):
    that slot is now the BASE GAME's `strike`, which resolves on every tree by
    design and would have turned this test green for the wrong reason."""
    # `EB-569`: the whole flag-dependent family, not `_card_prototype` alone.
    # `_substituted_card_index` warmed under the arm is what made this pass
    # alone and fail about one run in three under `-n auto`.
    loader.reset_arm_caches()
    with pytest.raises(KeyError):
        loader.get_card("proto_ko_kapow")
    loader.reset_arm_caches()


def test_the_sparks_arms_rule_stands_and_its_content_is_gone():
    """`EB-750`. The overhaul was a THIRD arm and the Sparks arm's RULE is
    still untouched -- editing that would make its published OFF/ON pair
    incomparable, which is the one thing a two-arm flag exists to prevent.

    What DID go is the arm's CONTENT, and R270 is why: it ruled Spark a
    currency under this arm, which superseded all eleven priced rows, so the
    rows, both substitution maps and the derived `KLEE_SPARK_ALT_ROWS` left
    HEAD together (commit 036c12d150d6dbd58f0776a0d07e3c028a321a61). The two
    names below are asserted ABSENT rather than deleted from the test, so a
    re-introduction has to argue with a lock."""
    assert C.SPARK_ALT_COST_ENABLED is False
    assert not hasattr(C, "SPARK_ALT_STARTER_SUBS")
    assert not hasattr(C, "SPARK_ALT_POOL_SUBS")
    assert not hasattr(C, "KLEE_SPARK_ALT_ROWS")
    assert C.KURAGE_MEMORY is False or C.KURAGE_MEMORY is True   # still there


# --- 2. THE ARM'S OWN SHAPE ------------------------------------------------

def test_the_starter_is_the_canonical_ten():
    """Slice packet sec.3, DRAFT 4 (ruled R242 pick 3): Strike x4, Defend x4,
    Jumpy Dumpty, Ka-pow!.

    [USER]: "the starting deck already does too much; base characters open with
    four Strikes, four Defends and two good cards of their own, and Klee had
    three, two and five." The shape IS the ruling, so the four-and-four is
    pinned by count, and so is the fact that exactly two of the ten are hers.

    `strike` and `defend` are the BASE GAME's ids, not `proto_` rows -- tier0
    has carried them at the base stat line since `ironclad_starter.yaml` -- so
    a regression that re-minted renamed twins fails here."""
    ids = C.KLEE_OVERHAUL_STARTER_IDS
    assert len(ids) == 10
    assert ids.count("strike") == 4
    assert ids.count("defend") == 4
    assert ids.count("proto_ko_jumpy_dumpty") == 1
    assert ids.count("proto_ko_kapow") == 1
    assert len([i for i in ids if i.startswith("proto_")]) == 2
    # Draft 3's six ids: two deleted outright, two back in the offer pool.
    for gone in ("proto_ko_kaboom", "proto_ko_duck_and_cover"):
        assert gone not in {c.id for c in loader.prototype_cards()}
    assert "proto_ko_pop" in C.KLEE_OVERHAUL_POOL_IDS
    assert "proto_ko_dig_in" in C.KLEE_OVERHAUL_POOL_IDS


def test_the_pool_is_the_slices_rows_and_the_passes_that_followed():
    """Slice packet sec.4, plus the passes that followed it, less the one row
    draft 3 moved into the starter.

    The count is pinned rather than described because each packet's count is
    its own scope statement, and because an ABSENCE is load-bearing wherever a
    row was drafted and withdrawn: a withdrawn row staged as a live card would
    be a face nobody ruled. `C.KLEE_OVERHAUL_POOL_IDS` is the record.

    The last assertion is the disjointness one: the starter and the offer pool
    share no row, so a card in both would fail here rather than quietly double
    as a reward.

    TWENTY-EIGHT AT DRAFT 4 (R242). Dig In and Pop! are back, because the
    canonical starter has no room for either.

    THIRTY-ONE SINCE R244, and the three that arrived are a SECOND slice
    rather than a redraft of this one: `review/ruled/
    klee-hexerei-readers-2026-09-02.md` adds Klee's three Hexerei readers.
    They are pinned by name for the same reason the absence above is -- the
    ruled packet's scope statement is "three, no more", and a fourth arriving
    without a ruling is what this count catches.

    THIRTY-THREE SINCE R252, a THIRD slice on the same terms: the defence shelf
    (`review/ruled/klee-overhaul-round-9-2026-09-04.md`, pick 1 taken at its
    default). The pick drafted four and the R253 charter audit withdrew two of
    them (Fire Safety and Safety Lesson), so TWO arrived; the packet's own
    scope statement is what the names below hold -- each keyed to the Bomb
    state, and neither a plain Block, which is why `proto_ko_dig_in` beside
    them is still the arm's only unconditional Block and is still a Spark sink.

    THIRTY-FOUR SINCE THE ROUND-10 POOL PASS (2026-09-04), and the one that
    arrived is `proto_ko_countdown`: the arm's only detonator priced in ENERGY
    that asks nothing else of the board. Three round-10 seats held Spark-priced
    detonators at 0 Spark with a fat Bomb on the enemy and no energy-priced
    detonator drawn; Ka-pow! is the starter's, one card in ten. The Spark sink
    drafted beside it (Explosive Spark) was WITHDRAWN on the card audit's C3
    clause and is on no surface, so its absence is pinned here for the reason
    Fire Safety's is.

    THIRTY-FIVE SINCE THE ROUND-11 POOL PASS (2026-09-04), and the one that
    arrived is `proto_ko_stoke_the_fuse`: the Spark SINK, written a second
    time and answering the C3 clause that withdrew the first. Explosive
    Spark's value followed the banked Sparks; this row's follows the Bomb
    decision -- the bank buys growth on a charge the player chose to keep
    cooking, and buys nothing at all with no Bomb on the board.

    FORTY-FIVE SINCE THE POOL PASS (2026-09-05, `EB-491`), and the TEN that
    arrived are the readings of rounds 13 to 16 made into cards: three for
    Cook, three for Spray, three for React and one bridge. `proto_ko_vermillion_pact`
    IS AMONG THEM, and its arrival is the one thing this test used to pin the
    other way round -- slice one's sec.5 allowed the row to drop because it
    touches shared reaction code, and this pass built it. The absence pinned in
    its place is the shape it did NOT take: no row here re-prices Sparks 'n'
    Splash, Countdown or Catalytic Converter, which the packet's sec.1 leaves
    as built.

    FIFTY-ONE SINCE POOL PASS TWO (2026-09-08, `EB-732`), and the SIX that
    arrived are three pairs: the defence shelf's two (Blast Shield, Return to
    Sender), the sinks' two beside Stoke the Fuse (Bottomless Bag, Once More!)
    and the engines' two, both paying Energy (Sparkling Burst, Blazing
    Delight). Named below for the reason every block above names its own: the
    pass's scope statement is "six", and a seventh arriving without a ruling is
    what this count catches.

    FORTY-NINE SINCE R271 STAGE ONE (`EB-749`, 2026-09-14), and the fall of two
    is a CONSOLIDATION rather than a pass: the ruled packet's sec.4 CUT
    `proto_ko_fwoosh` (Pocket Match is the same card at 5 with Retain) and
    `proto_ko_fireworks_show` (merged into Tinder Toss, which now prints "Set
    off ALL enemies. Deal 3 damage to ALL enemies." at 1 Spark), and REDESIGNED
    `proto_ko_powder_charge` into `proto_ko_booby_trap` -- the same 0-Energy,
    1-Spark placer bought from the bank, now the pool's only single-target
    Mine. Three names go and one arrives. The two cut ids are pinned ABSENT
    below for the reason Fire Safety's absence is: a cut row staged as a live
    card would be a face nobody ruled.

    FORTY-EIGHT SINCE R276 (2026-09-23, pick 1): five of R271's shelf CUT
    (Long Fuse, Explosives Workshop, Sugar Rush, Kindling, Catalytic
    Converter) and four ARRIVED (Hair Trigger, Explosive Frags, Where Did I
    Put It?, Big Bounce). Both halves pinned, for the cut rows' reason above.
    """
    ids = C.KLEE_OVERHAUL_POOL_IDS
    assert len(ids) == 78
    assert len(set(ids)) == 78
    assert {"proto_ko_dig_in", "proto_ko_pop"} <= set(ids)
    assert not set(ids) & set(C.KLEE_OVERHAUL_STARTER_IDS)
    # R244's three, and only three: `Hex and Wick` is the packet's sec.3
    # fourth, left out at pick 1's default until the round-8 read asks for a
    # cheaper fuse.
    assert {"proto_ko_coven_errand", "proto_ko_witches_circle",
            "proto_ko_alices_introduction_magic"} <= set(ids)
    assert "proto_ko_hex_and_wick" not in ids
    # R252's two, and only two: the R253 charter audit withdrew the other two
    # and they are on no surface, so their absence is pinned beside the
    # presence for the reason `proto_ko_hex_and_wick`'s is.
    assert {"proto_ko_dodoco_cover", "proto_ko_careful_now"} <= set(ids)
    assert "proto_ko_fire_safety" not in ids
    assert "proto_ko_safety_lesson" not in ids
    # The round-10 pool pass's one, and only one: the Spark sink written with
    # it was withdrawn on the audit's C3 clause and is on no surface.
    assert "proto_ko_countdown" in ids
    assert "proto_ko_explosive_spark" not in ids
    # The round-11 pool pass's one: the Spark SINK, written a second time and
    # this time keyed to the Bomb rather than to the bank -- the C3 clause
    # that withdrew Explosive Spark is what the row above it is answering.
    assert "proto_ko_stoke_the_fuse" in ids
    # THE POOL PASS's ten (`EB-491`), by name, for the reason every block above
    # names its own: the packet's scope statement is "ten", and an eleventh
    # arriving without one is what this catches.
    assert {"proto_ko_all_of_my_treasures",
            "proto_ko_fish_blasting", "proto_ko_pocket_match",
            "proto_ko_bombs_away", "proto_ko_flash_point",
            "proto_ko_vermillion_pact", "proto_ko_split_charge"} <= set(ids)
    # R271 STAGE ONE's two cuts and its one redesign (`EB-749`), pinned both
    # ways: the cut ids are on no surface, and Booby Trap stands in Powder
    # Charge's slot.
    assert "proto_ko_fwoosh" not in ids
    assert "proto_ko_fireworks_show" not in ids
    assert "proto_ko_powder_charge" not in ids
    assert "proto_ko_booby_trap" in ids
    # POOL PASS TWO's six (`EB-732`), by name and for the same reason.
    assert {"proto_ko_blast_shield", "proto_ko_return_to_sender",
            "proto_ko_bottomless_bag", "proto_ko_once_more",
            "proto_ko_sparkling_burst",
            "proto_ko_blazing_delight"} <= set(ids)
    # R276's five cuts and four arrivals.
    for cut in ("proto_ko_long_fuse", "proto_ko_explosives_workshop",
                "proto_ko_sugar_rush", "proto_ko_kindling",
                "proto_ko_catalytic_converter"):
        assert cut not in ids, cut
    assert {"proto_ko_hair_trigger", "proto_ko_explosive_frags",
            "proto_ko_where_did_i_put_it",
            "proto_ko_big_bounce"} <= set(ids)
    # THE POOL EXPANSION's thirty (R276), by name and for the same reason,
    # in their own block at the end of the tuple.
    assert list(ids[-30:]) == [
        "proto_ko_hiding_spot", "proto_ko_playdate",
        "proto_ko_jumpy_dumpty_mk_iii", "proto_ko_spinning_sparkler",
        "proto_ko_mine_all_mine", "proto_ko_team_effort",
        "proto_ko_fish_fry", "proto_ko_one_more_charge",
        "proto_ko_sit_tight", "proto_ko_treasure_map",
        "proto_ko_tag_along", "proto_ko_come_back_and_play",
        "proto_ko_boom_badge", "proto_ko_wait_for_it",
        "proto_ko_duck_and_run", "proto_ko_party_poppers",
        "proto_ko_look_out", "proto_ko_patience_klee",
        "proto_ko_friendship_bracelet", "proto_ko_secret_base",
        "proto_ko_half_a_mountain", "proto_ko_favonius_escort",
        "proto_ko_adventure_club", "proto_ko_windblume_fireworks",
        "proto_ko_fireworks_finale", "proto_ko_dodoco",
        "proto_ko_aftershock", "proto_ko_spark_knight",
        "proto_ko_alices_detonator", "proto_ko_second_surprise"]


def test_the_numbers_are_the_briefs_placeholders():
    """Slice packet sec.1: no number in it is a claim. These four are the
    rules' own, and they are named so `lint_constant_parity` can compare the
    C# mirrors BY VALUE."""
    # FOUR: the round-5 packet raised it from 3 to 5 and [USER] read 5 back
    # down on the same day ("growth 5 is likely too much").
    assert C.KLEE_OVERHAUL_BOMB_GROWTH == 4
    assert C.KLEE_OVERHAUL_WORKSHOP_GROWTH == 1
    # A MULTIPLIER since the 2026-09-02 balance pass: Alice's Recipe doubles
    # the turn's growth ("your Bombs grow twice each turn") instead of
    # replacing the base 3 with a 4 a second Explosives Workshop beat.
    assert C.KLEE_OVERHAUL_ALICE_MULTIPLIER == 2
    assert C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION == 1
    # FIVE since R242 pick 1: rule 4's opening bank. [USER]: "Regent starts
    # with 3 stars ... so 1 is a reasonable compromise."
    assert C.KLEE_OVERHAUL_OPENING_SPARK == 1


# --- 3. THE FLAG ON: the rows are reachable, and only these rows -----------

def test_the_starter_resolves_to_the_slices_ten_cards(overhaul):
    """`starting_deck` is the ONE seam both the tier 0 battery and the tier 0.5
    run read, so this is what she opens with on either path."""
    ids = loader.starting_deck("klee")
    assert ids == list(C.KLEE_OVERHAUL_STARTER_IDS)
    # And each one is a real, loadable, validated card -- not just a string.
    for cid in set(ids):
        card = loader.get_card(cid)
        assert card.id == cid
        if cid.startswith("proto_ko_"):
            assert card.character == "klee"

    # THE BASE BASICS, at the base stat line and the base upgrade (R242). They
    # are not hers and carry no `character:`, which is the point: the ruling
    # says "Strike and Defend are the base game's cards", so a twin re-minted
    # on her sheet would fail the identity below as well as the numbers.
    strike, defend = loader.get_card("strike"), loader.get_card("defend")
    assert (strike.cost, strike.type, strike.rarity) == (1, "attack", "basic")
    assert strike.effects == [{"op": "damage", "amount": 6, "target": "enemy"}]
    assert (defend.cost, defend.type, defend.rarity) == (1, "skill", "basic")
    assert defend.effects == [{"op": "block", "amount": 5}]
    assert loader.get_card("strike+").effects[0]["amount"] == 9
    assert loader.get_card("defend+").effects[0]["amount"] == 8


def test_a_base_strike_in_her_hand_applies_nothing(overhaul):
    """[USER], 2026-09-02: "I think we actually SHOULD remove the elemental
    application from the basic Strikes for all characters. Those cards are
    supposed to be bad!" R242 put the base game's Strike in her starter and
    `EB-307` read that as "her Strikes must keep applying Pyro"; this is the
    ruled reading of the same swap, and LAW's cadence line now carries it.

    RULE 5 IS STILL ABOUT THE CHARACTER: her OWN Attacks apply with nothing
    printed, which is what the second half of this pin holds. The C# twin is
    `CatalystCadence.IsBaseGameBasic`."""
    from tier0.tests.conftest import make_state
    from tier0.engine import effects as fx_mod

    state = make_state()
    state.player = loader.build_player("klee")
    assert (state.player.cadence, state.player.element) == ("catalyst", "pyro")
    strike = loader.get_card("strike")
    assert strike.element == "none"
    assert fx_mod._element_for(state, strike.effects[0], strike) is None
    # A DEFEND applied nothing before the ruling either: the cadence is about
    # Attacks, and this is the second reason it does not.
    defend = loader.get_card("defend")
    assert fx_mod._element_for(state, defend.effects[0], defend) is None

    # AND HER OWN ATTACK IS UNMOVED, which is the whole point of the exemption
    # being about the base game's card rather than about her cadence.
    bait = next(c for c in loader.prototype_cards()
                if c.id == "proto_ko_fish_flavored_bait")
    assert bait.element == "none"
    assert fx_mod._element_for(state, bait.effects[0], bait) == "pyro"


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
    """16 Common, 12 Uncommon, 6 Rare -- the slice packet's sec.4 count with
    Vermillion Pact removed and, since DRAFT 4 (R242), Pop! and Dig In back as
    Commons, plus ONE OF EACH from R244's Hexerei readers and ONE OF EACH from
    what is left of R252's defence shelf (it drafted two Commons and two
    Uncommons; the charter audit withdrew Fire Safety, a Common, and Safety
    Lesson, an Uncommon). Pinned because the rarity buckets ARE the offer odds:
    a row filed in the wrong tier changes how often it is seen, both returning
    rows had to stop being `rarity: basic` to be offerable at all, and the R244
    packet files its three one per tier on purpose (a Common that reads the
    turn, an Uncommon Power that is dead alone, a Rare enabler). The
    round-10 pool pass adds ONE Common (`proto_ko_countdown`): a detonator a
    seat has to be OFFERED often is a Common or it is not the answer to the
    finding it was written for. The round-11 pool pass adds ONE Uncommon
    (`proto_ko_stoke_the_fuse`) and NOT a Common, for the other half of the
    same argument: a sink that pays only into a Bomb already cooking is a card
    a deck is built around rather than one every hand needs to be holding.

    THE POOL PASS (`EB-491`) adds FIVE Commons, THREE Uncommons and TWO Rares,
    which is where 21 / 16 / 8 comes from. The Rare count is the number the
    packet's sec.2 states outright ("Rares 8, the brief's count"), and it is
    pinned here rather than described because the brief's Rare budget is a
    scope statement: a ninth Rare arriving without a ruling is what this
    catches.

    POOL PASS TWO (`EB-732`) adds ONE Common (Bottomless Bag), FOUR Uncommons
    (Blast Shield, Return to Sender, Once More!, Sparkling Burst) and ONE Rare
    (Blazing Delight), which is where 22 / 20 / 9 comes from. THE RARE IS A
    NINTH, one past the brief's sec.2 budget of eight, and it is recorded here
    rather than absorbed: the count above says in as many words that a ninth
    Rare arriving without a ruling is what this test catches, so the pass is
    the ruling and the number moves with it.

    R271 STAGE ONE (`EB-749`) takes it to 22 / 18 / 9. It cuts ONE Common
    (Fwoosh!) and TWO Uncommons (Fireworks Show, Powder Charge) and adds ONE
    Common (Booby Trap, Powder Charge's shape at Common because the ruled row
    says Common Skill). The Common count is therefore unmoved and the Uncommon
    count falls by two, which is what a consolidation looks like in this
    table.

    R276 takes it to 22 / 18 / 8. It cuts TWO Commons (Long Fuse, Kindling),
    TWO Uncommons (Explosives Workshop, Catalytic Converter) and ONE Rare
    (Sugar Rush), and adds TWO Commons (Hair Trigger, Where Did I Put It?) and
    TWO Uncommons (Explosive Frags, Big Bounce) -- so the Rare count is back
    at the brief's eight.

    THE POOL EXPANSION (R276) adds TWO Commons, EIGHTEEN Uncommons and TEN
    Rares toward the 78-card pool R276 ruled, which is where 24 / 36 / 18
    comes from. R276 is the ruling the Rare count moves with."""
    pool = rewards.character_pool("klee")
    assert {r: len(cs) for r, cs in sorted(pool.items())} == {
        "common": 24, "uncommon": 36, "rare": 18}


def test_no_other_character_moves_under_the_flag(overhaul):
    """The seam is Klee's alone. A flag that quietly re-pooled Furina would
    make every number measured on her incomparable."""
    for character in ("furina", "kokomi"):
        assert loader.pool_replacement(character) is None
        ids = {c.id for cards in rewards.character_pool(character).values()
               for c in cards}
        assert not any(cid.startswith("proto_ko_") for cid in ids)


# --- 4. THE OPS ARE REGISTERED AND REFUSE OFF THE ARM ----------------------

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


def test_the_new_ops_refuse_to_resolve_off_the_arm():
    """THE QUARANTINE, AT THE RESOLVER. `EB-312` built the twin
    (`tier0/engine/klee_overhaul.py`), so these eight resolve now -- but only
    with the flag ON and Klee in the seat, which is the mod's
    `KleeOverhaul.Enabled` plus the `IKleeCharacter` test every seam carries
    beside it. Off the arm they still raise, because a silently no-op resolver
    is the worst possible stand-in: a prototype that reports numbers for rules
    it never ran.

    BOTH CLAUSES OF THE GATE are asserted, a default seat and a KLEE seat with
    the flag still off, so neither can be dropped without this failing. The ON
    side lives in `tier0/tests/test_klee_overhaul_rules.py`."""
    from tier0.tests.conftest import make_state
    from tier0.engine.state import Card

    for op in OVERHAUL_OPS:
        for character in (None, "klee"):
            state = make_state()
            if character:
                state.player.character_id = character
            card = Card(id="probe", name="probe", cost=1, type="attack",
                        effects=[{"op": op}])
            with pytest.raises(NotImplementedError) as excinfo:
                effects.OPS[op](state, {"op": op}, card)
            assert "KLEE_OVERHAUL" in str(excinfo.value)


def test_the_two_predicates_refuse_off_the_arm():
    """Rule 7's two per-turn reads, on the same gate the ops take. Neither is a
    synonym for `reaction_triggered_this_turn`, so answering False off the arm
    would report a game this engine never played."""
    from tier0.tests.conftest import make_state

    for name in ("bomb_went_off_this_turn", "bomb_reacted_this_turn"):
        assert name in effects.PREDICATE_NAMES
        with pytest.raises(NotImplementedError):
            effects._predicate(make_state(), name)


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

    assert delta("proto_ko_kapow") == {"damage": 3}          # a set_off's hit
    assert delta("proto_ko_rapid_fire") == {"damage": 1}     # 4 hits: +1 each
    assert delta("proto_ko_run_away") == {"block": 3}
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
    # R276 pick 1 gave The Moon a Block now-line, so no row's face-up half is
    # a bare Mend any more; the Mend clause of the rule is asked of the op.
    assert upgrades.prototype_default_delta(
        "proto_kk_the_moon_a_ship", 2, [{"op": "mend", "amount": 3}]) == {
            "mend": 2}


def test_the_cost_clause_is_the_last_resort_and_only_at_two():
    """"A card of cost 2 or more WITH NO NUMBER costs 1 less" -- so the clause
    fires only when nothing else did.

    AMENDED 2026-09-02 by [USER]'s own play ("'Change of Plans' has no
    upgrade?", "Neither does Rally"). The clause is no longer the last one:
    below it sit two more, so a 0- or 1-cost row printing no number loses
    Exhaust if it has it and otherwise draws one more. What is unchanged is
    this clause's own shape -- it still fires only on a numberless row, and
    still only at cost 2 or more."""
    from tier0.content import upgrades

    assert upgrades.prototype_default_delta(
        "proto_kk_nereids_ascension", 2, [
            {"op": "apply_power", "power": "kk_nereids_ascension",
             "amount": 1, "target": "self"}]) == {"cost": -1}
    # The same row at cost 1: no discount -- it falls to the added draw.
    assert upgrades.prototype_default_delta(
        "proto_kk_treatise", 1, [
            {"op": "apply_power", "power": "kk_treatise", "amount": 1,
             "target": "self"}]) == {"add": {"op": "draw", "amount": 1}}
    # A row that DID find a number never also gets the discount.
    assert "cost" not in upgrades.prototype_default_delta(
        "proto_kk_the_moon_a_ship", 2, [{"op": "mend", "amount": 10}])


def test_the_two_last_clauses_are_exhaust_then_a_draw():
    """`EB-283`'s two APPLIED DEFAULTS, from [USER] playing the arm. Before
    them a 0- or 1-cost row printing no number got nothing at all, which is an
    upgrade slot that is a blank rather than a choice.

    Both named rows are [USER]'s own examples, pinned by id. `proto_kk_vanguard`
    left this pair under `R250` pick 1 (round-4d sec.6): it gained a now-line
    with its own printed number, so the RAW default (this probe's whole
    subject, and it deliberately reads `effects:` alone -- no `plan:` -- the
    same as the day this test was written) now reads `power_amount` off that
    line; the row itself keeps "remove exhaust" off the table by declaring its
    own `upgrade:` (`test_prototype_surface.py` pins that). Moon's Reflection
    -- `exhaust: true`, no printed number on either line -- is the same shape
    Vanguard used to be.
    """
    from tier0.content import upgrades

    def delta(card_id):
        card = next(c for c in loader.prototype_cards() if c.id == card_id)
        return upgrades.prototype_default_delta(
            card.id, card.cost, card.effects, bool(card.exhaust))

    # Change of Plans keeps its text and loses Exhaust.
    assert delta("proto_kk_change_of_plans") == {"remove": "exhaust"}
    assert delta("proto_kk_moons_reflection") == {"remove": "exhaust"}

    # Rally is the counted-power half: `weak` at 1 IS a printed number, so it
    # never reaches the two clauses at all -- Rally+ applies 2 Weak.
    assert delta("proto_kk_rally") == {"power_amount": 1}
    assert delta("proto_kk_exposed_flank") == {"power_amount": 1}

    # And a row with a now-line, no Exhaust and no number draws one more.
    assert upgrades.prototype_default_delta(
        "proto_ko_x", 1, [{"op": "apply_power", "power": "ko_alices_recipe",
                           "amount": 1, "target": "self"}]) == {
        "add": {"op": "draw", "amount": 1}}

    # TWO SILENCES, and both are the codegen refusing rather than the rule
    # declining. A row that already draws would collide on the one `Cards`
    # var; a PLAN-ONLY row has no effects walk to hang the added draw on, and
    # a now-line draw would contradict the "Play on the Bake-Kurage." its
    # target type earns it. `proto_kk_ambush` left this second example under
    # `R250` pick 1, the same as Vanguard above -- a real Plan-only shape,
    # not a real row, since round-4d left only Nereid's Ascension (cost 2,
    # which reaches the cost clause first) with an empty now-line.
    assert delta("proto_kk_stolen_chapter") == {}
    assert upgrades.prototype_default_delta("proto_kk_x", 1, []) == {}


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
    counted = [{"op": "apply_power", "power": "weak", "amount": 1,
                "target": "enemy"}]
    # A FLAG finds no power number and falls through to the added-draw clause
    # below the cost one; the key that matters here is that it is not
    # `power_amount`.
    assert "power_amount" not in upgrades.prototype_default_delta(
        "proto_ko_x", 1, flag)
    assert upgrades.prototype_default_delta("proto_ko_x", 1, printed) == {
        "power_amount": 1}
    # AMENDED 2026-09-02: a COUNTED power prints its amount even at 1
    # (`upgrades.COUNTED_POWERS`), which is the half `> 1` alone got wrong --
    # Rally's "Apply 1 Weak" is a number and Alice's Recipe's 1 is a switch.
    assert upgrades.prototype_default_delta("proto_ko_x", 1, counted) == {
        "power_amount": 1}
    assert "weak" in upgrades.COUNTED_POWERS
    assert "ko_alices_recipe" not in upgrades.COUNTED_POWERS


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
        # ROUND 5 PICK 1, taken at its default ([USER] 2026-09-02: "I'm fine
        # with the default on Ka-Pow!"): Retain moved onto the BASE card, so
        # holding a Bomb no longer means discarding the only detonator. The
        # row's `upgrade:` block went with it, which hands the upgrade back to
        # the Prototype default rule -- a set_off's hit, +3.
        assert base.retain is True and upgraded.retain is True
        assert base.effects[0]["damage"] == 4
        assert upgraded.effects[0]["damage"] == 7
        # Jumpy Dumpty's authored block beats the default the same way: the
        # default is +2/+1, the ruling is Bomb 11 and Mine 4.
        jd = loader.get_card("proto_ko_jumpy_dumpty+")
        assert jd.effects[0]["size"] == 11
        assert jd.effects[0]["payload_mine_all"] == 4
        # The Spark price is never what the campfire moved.
        dig = loader.get_card("proto_ko_dig_in+")
        assert [f for f in dig.effects if f["op"] == "spend_spark"] == [
            {"op": "spend_spark", "amount": 1}]
        assert [f["amount"] for f in dig.effects if f["op"] == "block"] == [11]
    finally:
        upgrades._prototype_upgrade_index.cache_clear()
        upgrades._upgrade_index.cache_clear()


# --- `EB-557` (R261): THE PLACER IS INNATE AND THE DETONATOR IS NOT ---------

def test_the_arms_placer_is_innate_and_its_detonator_is_not(overhaul):
    """R261, the row itself.

    [USER] took none of the round-17 options as written -- Pop! in the starter
    was declined and a relic-planted Bomb was passed over -- and narrowed
    Innate on both basics to ONE: "Jumpy Dumpty gains Innate; Ka-pow! does
    not." So turn one always holds the placer, the detonator still has to be
    drawn, and the other draws still have to carry the Block.

    THE FIELD AND NOT THE UPGRADE. `innate:` is on the row, so both faces
    carry it: an upgrade is a different card and a player who smiths the
    placer must not lose the opening it was ruled for.
    """
    assert loader.get_card("proto_ko_jumpy_dumpty").innate is True
    assert loader.get_card("proto_ko_jumpy_dumpty+").innate is True
    assert loader.get_card("proto_ko_kapow").innate is False
    assert loader.get_card("proto_ko_kapow+").innate is False


def test_every_opening_hand_under_the_arm_holds_the_placer(overhaul):
    """The acceptance condition, driven on the real combat opening.

    `combat._player_turn`'s first turn shuffles the built deck and calls
    `surface_innate`, so the question "does the opening hand hold it" is
    decided by the draw pile's top after that call -- which is what this walks,
    over enough shuffles that a lucky seed cannot pass it.

    KA-POW! IS DRAWN NORMALLY, and that is the half the ruling is about: it is
    NOT asserted absent, because a normal draw finds it sometimes. What is
    asserted is that it is never surfaced -- the placer is alone on top.
    """
    import random

    from tier0.engine.combat import surface_innate

    for seed in range(25):
        player = loader.build_player("klee")
        random.Random(seed).shuffle(player.draw_pile)
        surface_innate(player.draw_pile)
        assert player.draw_pile[0].id == "proto_ko_jumpy_dumpty", seed
        # Five cards is the opening hand, and the placer is in it every time.
        assert "proto_ko_jumpy_dumpty" in [c.id for c in player.draw_pile[:5]]
        surfaced = [c.id for c in player.draw_pile if c.innate]
        assert surfaced == ["proto_ko_jumpy_dumpty"], seed


def test_the_shipped_klee_opening_is_untouched_by_the_row():
    """Flag off, nothing changes: the printed starter carries no Innate at all,
    so `surface_innate` reorders nothing and the shipped opening hand is the
    shuffle's. The arm's row is unreachable here by construction -- it lives
    only on the prototype surface -- which is why this is a statement about the
    SHIPPED deck rather than about a flag branch."""
    import random

    from tier0.engine.combat import surface_innate

    player = loader.build_player("klee")
    before = [c.id for c in player.draw_pile]
    random.Random(3).shuffle(player.draw_pile)
    shuffled = [c.id for c in player.draw_pile]
    surface_innate(player.draw_pile)
    assert [c.id for c in player.draw_pile] == shuffled
    assert sorted(before) == sorted(shuffled)
    assert not any(c.innate for c in player.draw_pile)


# --- 2026-09-23: NO COMPANION PLAY PAYS KLEE'S SPARK UNDER THE ARM ---------

def test_no_companion_play_pays_klees_spark_under_the_arm(overhaul):
    """R276 pick 2 had made any Companion card pay Klee the Spark under the
    arm; [USER] turned it off on 2026-09-23: "It sounds like we've massively
    increased the Spark generation and it's worth decreasing now to go back to
    the old levels and then see if play is Spark-constrained."

    The four cases R276 pinned as paying -- a Universal, a family stand-in, a
    coven Personal and a card outside the old family -- now pay nothing.
    """
    from tier0.engine.combat import play_card
    from tier0.tests.conftest import make_state

    for cid in ("proto_mc_razor_claw_and_thunder",      # a Universal
                "proto_mc_fischl_sinful_hex",           # a family stand-in
                "proto_mc_noelle_i_got_your_back",      # a coven Personal
                "proto_mi_gorou_war_banner"):           # outside the old family
        card = loader.get_card(cid)
        assert card.is_companion, cid
        state = make_state()
        state.player.character_id = "klee"
        state.player.hand = [card]
        play_card(state, card)
        assert state.player.sparks == 0, cid
        assert not any(e["event"] == "klee_companion_spark"
                       for e in state.log), cid


def test_alices_marked_cards_pay_no_spark_under_the_arm(overhaul):
    """`EB-663`'s pin, re-read on 2026-09-23. The marked cards still count as
    Companion cards (the readers' question), but no play of one pays a
    Spark, and neither does the spell itself."""
    from tier0.engine import companion_hexerei
    from tier0.engine.combat import play_card
    from tier0.tests.conftest import make_state

    alices = loader.get_card("proto_ko_alices_introduction_magic")
    marked = [loader.get_card("proto_ko_careful_now") for _ in range(3)]
    assert not alices.is_companion
    assert not any(card.is_companion for card in marked)

    state = make_state()
    state.player.character_id = "klee"
    state.player.hand = [alices, *marked]
    play_card(state, alices)
    assert state.player.sparks == 0
    # The window is over the INSTANCES that were in hand (R244).
    assert len(state.ko_companion_marked) == 3

    for card in marked:
        assert companion_hexerei.counts_as_companion(state, card)
        play_card(state, card)
        assert state.player.sparks == 0


def test_the_companion_gate_still_stands_off_the_arm():
    """R213 B rather than taste: OFF the arm the rule stays the Companion +
    Personal-pool test `EB-219` moved into the kit at parity. Written against
    the effect directly, because a prototype row is not loadable with the flag
    down -- which is the quarantine doing its job."""
    from tier0.engine import effects
    from tier0.engine.state import Card
    from tier0.tests.conftest import make_state

    assert not C.KLEE_OVERHAUL
    state = make_state()
    state.player.character_id = "klee"
    # A Universal Companion pays nothing off the arm (and nothing under it
    # since 2026-09-23).
    universal = Card(id="x_universal", name="Universal", cost=1,
                     type="skill", tags=["companion"])
    effects.klee_companion_spark(state, universal)
    assert state.player.sparks == 0
    # And the shipped rule's own row still pays, untouched.
    personal = Card(id="x_personal", name="Personal", cost=1, type="skill",
                    tags=["companion"], personal_pool="klee")
    effects.klee_companion_spark(state, personal)
    assert state.player.sparks == C.KLEE_COMPANION_SPARK_BASE


def test_only_klee_is_paid_by_her_own_kit(overhaul):
    """`EB-434`, written out at last: the grant names the character.

    The old gate asked the CARD's pool against its owner and named nobody, so
    Kokomi playing her own Personal banked a Spark she has no surface to read.
    Sparks are Klee's resource; nobody else is paid.
    """
    from tier0.engine.combat import play_card
    from tier0.tests.conftest import make_state

    razor = loader.get_card("proto_mc_razor_claw_and_thunder")
    state = make_state()
    state.player.character_id = "kokomi"
    state.player.hand = [razor]
    play_card(state, razor)
    assert state.player.sparks == 0


def test_no_face_prints_the_retired_hexerei_mark():
    """R276 pick 2 retired the Hexerei mark: no prototype row carries the
    `hexerei:` key, no face prints the word, and the codegen no longer has a
    family tag to add. `_family_tags` is gone rather than switched off."""
    import yaml

    from tools import gen_klee_cards as gen

    rows = yaml.safe_load(
        (gen.REPO / "docs" / "prototype-surface.yaml").read_text(
            encoding="utf-8"))
    assert not [r["id"] for r in rows if "hexerei" in r]
    assert not [r["id"] for r in rows
                if "Hexerei" in str(r.get("description", ""))]
    assert not hasattr(gen, "_family_tags")
    assert "Hexerei" not in {k.word for k in gen.ARM_KEYWORDS}


# ---------------------------------------------------------------------------
# 8. POOL PASS TWO (`EB-732`) -- one case per row, both new ops and both new
#    powers. C# twin: `klee-mod/KleeTests/Prototype/KleeOverhaulPoolPassTwoTests.cs`,
#    case for case.
# ---------------------------------------------------------------------------

def _pass_two_state(enemies=None, hp=62):
    """A Klee seat with the arm live, `test_klee_overhaul_rules.klee_state`'s
    shape: `klee_overhaul.live` reads the flag AND the character, so both
    halves have to be true before anything in the arm runs."""
    from tier0.tests.conftest import make_enemy, make_state

    st = make_state(enemies=enemies or [make_enemy(hp=200)], hp=hp)
    st.player.character_id = "klee"
    st.player.element = "pyro"
    st.player.cadence = "catalyst"
    st.in_player_turn = True
    st.player.energy = 3
    return st


def test_blast_shield_comes_back_to_hand_and_can_be_played_again(overhaul):
    """ROW 1. "Gain 6 Block. Return this card to your hand."

    THE ROUTING IS THE RULE. The card is in no pile while it resolves, so the
    `return_to_hand` op raises a per-play flag and `_finish_play` reads it at
    the one line that decides where a played card lands -- the same layer the
    mod answers at, with `GetResultLocationForCardPlay` returning
    `PileType.Hand`. So the assertion is about the PILES and not about a log.

    AND IT REALLY IS PLAYABLE AGAIN, for another Spark (1 since the Klee
    balance review, pick 4a, 2026-09-25): a second play is a second Block and
    a second price, which is the whole card.
    """
    from tier0.engine.combat import play_card

    state = _pass_two_state()
    card = loader.get_card("proto_ko_blast_shield")
    state.player.sparks = 5
    state.player.hand = [card]

    play_card(state, card)
    assert state.player.block == 6
    assert state.player.sparks == 4
    assert card in state.player.hand, "the card came back"
    assert card not in state.player.discard_pile

    play_card(state, card)
    assert state.player.block == 12, "played twice, paid twice"
    assert state.player.sparks == 3
    assert card in state.player.hand

    # AND THE UPGRADE MOVES THE BLOCK AND NOTHING ELSE.
    up = loader.get_card("proto_ko_blast_shield+")
    state2 = _pass_two_state()
    state2.player.sparks = 2
    state2.player.hand = [up]
    play_card(state2, up)
    assert state2.player.block == 8
    assert up in state2.player.hand


def test_return_to_sender_plants_what_the_block_absorbed_and_only_now(overhaul):
    """ROW 2. "Gain 8 Block. This turn, damage this Block absorbs is placed on
    the attacker as a Bomb."

    THE CHARGE IS THE ABSORBED AMOUNT, CAPPED AT THE ALLOWANCE (`EB-749`,
    R271 sec.5.2): both hits below are inside an 8-mark, so what each plants is
    what it absorbed. The cap itself is
    `test_eb749_return_to_sender_is_capped_at_one_allowance_a_turn`. It rides
    the ONE site that can say "this Block absorbed damage"
    (`companion_overhaul_block_absorbed`, called from `_enemy_turn` right after
    Block is spent) and is FIRST in it.

    "THIS TURN" IS THE MARK'S OWN LIFETIME and needs no timer: Block is cleared
    at the start of Klee's next turn and `turn_start_late` deletes a mark with
    nothing behind it. C# twin: `BlockMark.Absorb` / `ClearIfSpent`.
    """
    from tier0.engine import klee_overhaul
    from tier0.engine.combat import play_card

    state = _pass_two_state()
    enemy = state.enemies[0]
    card = loader.get_card("proto_ko_return_to_sender")
    state.player.sparks = 2
    state.player.hand = [card]
    play_card(state, card)

    assert state.player.block == 8
    assert state.player.powers[klee_overhaul.RETURN_TO_SENDER] == 8

    # ONE ABSORPTION of 5: a Bomb 5 on the attacker, and the mark is down to 3.
    effects.companion_overhaul_block_absorbed(state, enemy, 5, 8)
    assert [c.size for c in enemy.ko_charges] == [5]
    assert state.player.powers[klee_overhaul.RETURN_TO_SENDER] == 3

    # A SECOND ABSORPTION fires again while the mark stands -- "whenever" --
    # and the mark is gone after it.
    effects.companion_overhaul_block_absorbed(state, enemy, 3, 3)
    assert [c.size for c in enemy.ko_charges] == [5, 3]
    assert klee_overhaul.RETURN_TO_SENDER not in state.player.powers

    # A MARK WITH NO BLOCK BEHIND IT IS GONE AT TURN START, which is the whole
    # of "this turn".
    state2 = _pass_two_state()
    state2.player.sparks = 2
    card2 = loader.get_card("proto_ko_return_to_sender")
    state2.player.hand = [card2]
    play_card(state2, card2)
    state2.player.block = 0                      # the turn tick
    klee_overhaul.roll_to(state2, 2)
    klee_overhaul.turn_start_late(state2)
    assert klee_overhaul.RETURN_TO_SENDER not in state2.player.powers
    effects.companion_overhaul_block_absorbed(state2, state2.enemies[0], 4, 4)
    assert state2.enemies[0].ko_charges == [], "expired: nothing is planted"

    # AND THE UPGRADE MOVES BOTH NUMBERS TOGETHER, so the Block and the mark
    # cannot drift.
    state3 = _pass_two_state()
    up = loader.get_card("proto_ko_return_to_sender+")
    state3.player.sparks = 2
    state3.player.hand = [up]
    play_card(state3, up)
    assert state3.player.block == 11
    assert state3.player.powers[klee_overhaul.RETURN_TO_SENDER] == 11


def test_eb749_return_to_sender_is_capped_at_one_allowance_a_turn(overhaul):
    """R271 sec.5.2 (`EB-749`). The conversion is CAPPED at the Block the card
    granted, as ONE allowance spent across every hit of the turn -- never an
    independent cap per hit.

    TWO HITS THAT TOGETHER EXCEED IT is the case the ruling is about: 6 and 6
    against an 8-mark plant 6 and then 2, and not 6 and 6. One huge hit is the
    same rule from the other side: an 8-mark eating a 20 plants 8 and is spent,
    where the row planted a 20 before this.
    """
    from tier0.engine import klee_overhaul
    from tier0.engine.combat import play_card

    state = _pass_two_state()
    enemy = state.enemies[0]
    card = loader.get_card("proto_ko_return_to_sender")
    state.player.sparks = 2
    state.player.hand = [card]
    play_card(state, card)
    state.player.block = 20                  # a wall the mark is only part of
    assert state.player.powers[klee_overhaul.RETURN_TO_SENDER] == 8

    effects.companion_overhaul_block_absorbed(state, enemy, 6, 20)
    effects.companion_overhaul_block_absorbed(state, enemy, 6, 14)

    assert [c.size for c in enemy.ko_charges] == [6, 2]
    assert sum(c.size for c in enemy.ko_charges) == 8, "one allowance, not two"
    assert klee_overhaul.RETURN_TO_SENDER not in state.player.powers

    # ONE HIT PAST THE ALLOWANCE, the same rule read the other way.
    state2 = _pass_two_state()
    other = state2.enemies[0]
    card2 = loader.get_card("proto_ko_return_to_sender")
    state2.player.sparks = 2
    state2.player.hand = [card2]
    play_card(state2, card2)
    state2.player.block = 20

    effects.companion_overhaul_block_absorbed(state2, other, 20, 20)

    assert [c.size for c in other.ko_charges] == [8]
    assert klee_overhaul.RETURN_TO_SENDER not in state2.player.powers


def test_bottomless_bag_draws_two_and_three_upgraded(overhaul):
    """ROW 3. "Draw 2 cards." The arm's Spark sink that buys CARDS, and the
    upgrade takes Countdown's own `draw` key so both rows move one number."""
    from tier0.engine.combat import play_card
    from tier0.engine.state import Card

    def fodder(n):
        return [Card(id=f"strike{i}", name="Strike", cost=1, type="attack",
                     effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
                for i in range(n)]

    state = _pass_two_state()
    card = loader.get_card("proto_ko_bottomless_bag")
    # 2026-09-25 afternoon seats: the price is 1 Spark (it was 2).
    state.player.sparks = 1
    state.player.draw_pile = fodder(5)
    state.player.hand = [card]
    play_card(state, card)
    assert len(state.player.hand) == 2
    assert state.player.sparks == 0

    state2 = _pass_two_state()
    up = loader.get_card("proto_ko_bottomless_bag+")
    state2.player.sparks = 1
    state2.player.draw_pile = fodder(5)
    state2.player.hand = [up]
    play_card(state2, up)
    assert len(state2.player.hand) == 3


def test_once_more_takes_the_last_set_off_card_out_of_the_discard(overhaul):
    """ROW 4. "Return the last Set off card you played this combat to your
    hand."

    THE NOTE IS TAKEN AT THE OP SITE, so a Set off played into an empty board
    still counts -- which is what "the last Set off card you PLAYED" says. By
    INSTANCE, so two copies of one detonator are two cards.

    NOTHING HAPPENS AND THE SPARKS ARE STILL SPENT when the card is not in the
    discard pile: the price is a cost line and a cost line is paid before the
    body runs. That is the same bargain every Spark-priced row makes.
    """
    from tier0.engine import klee_overhaul
    from tier0.engine.combat import play_card

    state = _pass_two_state()
    enemy = state.enemies[0]
    klee_overhaul.place(state, enemy, 4)

    detonator = loader.get_card("proto_ko_countdown")
    state.player.sparks = 6
    state.player.hand = [detonator]
    play_card(state, detonator)
    assert detonator in state.player.discard_pile
    assert state.ko_last_set_off_card is detonator

    once = loader.get_card("proto_ko_once_more")
    state.player.hand.append(once)
    play_card(state, once)

    assert detonator in state.player.hand
    assert detonator not in state.player.discard_pile
    assert state.player.sparks == 4, "2 Sparks paid (balance review 4a)"

    # PLAYED AGAIN WITH NOTHING IN THE DISCARD: the detonator is in HAND now,
    # so the row moves nothing and the Sparks are still gone.
    once2 = loader.get_card("proto_ko_once_more")
    state.player.hand.append(once2)
    play_card(state, once2)
    assert detonator in state.player.hand
    assert state.player.sparks == 2

    # AND NONE PLAYED AT ALL is the same silence, on a fresh combat.
    fresh = _pass_two_state()
    fresh.player.sparks = 2
    solo = loader.get_card("proto_ko_once_more")
    fresh.player.hand = [solo]
    play_card(fresh, solo)
    assert fresh.player.hand == []
    assert fresh.ko_last_set_off_card is None
    assert fresh.player.sparks == 0


def test_sparkling_burst_pays_one_energy_or_two_by_the_predicate(overhaul):
    """ROW 5. "Gain 1 Energy. If a Bomb went off this turn, gain 1 more."

    RUN AWAY!'s PREDICATE EXACTLY (`bomb_went_off_this_turn`), so the two rows
    read one counter and cannot disagree about what a turn's explosion is.
    """
    from tier0.engine import klee_overhaul
    from tier0.engine.combat import play_card

    state = _pass_two_state()
    card = loader.get_card("proto_ko_sparkling_burst")
    state.player.sparks = 3
    state.player.energy = 0
    state.player.hand = [card]
    play_card(state, card)
    assert state.player.energy == 1, "nothing went off: the flat line only"
    assert card in state.player.discard_pile, "not Exhaust"

    state2 = _pass_two_state()
    enemy = state2.enemies[0]
    klee_overhaul.place(state2, enemy, 4)
    klee_overhaul.set_off(state2, enemy)
    card2 = loader.get_card("proto_ko_sparkling_burst")
    state2.player.sparks = 3
    state2.player.energy = 0
    state2.player.hand = [card2]
    play_card(state2, card2)
    assert state2.player.energy == 2

    # THE UPGRADE MOVES THE SPARK PRICE and nothing on the face.
    # (2 Sparks, 1 upgraded, since the Klee balance review, pick 4a.)
    state3 = _pass_two_state()
    up = loader.get_card("proto_ko_sparkling_burst+")
    state3.player.sparks = 1
    state3.player.energy = 0
    state3.player.hand = [up]
    play_card(state3, up)
    assert state3.player.energy == 1
    assert state3.player.sparks == 0


def test_blazing_delight_pays_energy_and_a_card_at_turn_start(overhaul):
    """ROW 6. "At the start of your turn, gain 1 Energy and draw 1 card."

    THE SITE IS `turn_start_late`, Grounded's, and that is the rule: the energy
    reset and the turn's opening draw have already happened there, so the
    Energy survives and the card is drawn on top of the opening hand.

    STACKS ADD, both halves off one number: two copies pay 2 and 2.
    """
    from tier0.engine import klee_overhaul
    from tier0.engine.combat import play_card
    from tier0.engine.state import Card

    def fodder(n):
        return [Card(id=f"strike{i}", name="Strike", cost=1, type="attack",
                     effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
                for i in range(n)]

    state = _pass_two_state()
    card = loader.get_card("proto_ko_blazing_delight")
    state.player.sparks = 5
    state.player.draw_pile = fodder(6)
    state.player.hand = [card]
    play_card(state, card)
    assert state.player.powers[klee_overhaul.BLAZING_DELIGHT] == 1

    state.player.energy = 3
    klee_overhaul.roll_to(state, 2)
    klee_overhaul.turn_start_late(state)
    assert state.player.energy == 4
    assert len(state.player.hand) == 1

    # A SECOND COPY PAYS TWICE, on one number read twice.
    state.player.powers[klee_overhaul.BLAZING_DELIGHT] = 2
    state.player.energy = 3
    state.player.hand = []
    klee_overhaul.roll_to(state, 3)
    klee_overhaul.turn_start_late(state)
    assert state.player.energy == 5
    assert len(state.player.hand) == 2

    # THE UPGRADE CUTS THE SPARK PRICE, Once More!'s and Sparkling Burst's
    # rail: the `+` card is the SAME body for 2 Sparks and the same 2 Energy
    # (3 and 2 since the Klee balance review, pick 4a, 2026-09-25).
    # Authored on the row rather than left to the Prototype rule, which would
    # have fallen through to its cost clause and sold a 1-energy Rare instead
    # (`amount: 1` on a Power reads as "this row prints no power number").
    up = loader.get_card("proto_ko_blazing_delight+")
    assert up.cost == 2
    assert [fx for fx in up.effects
            if fx["op"] == "spend_spark"][0]["amount"] == 2
    state4 = _pass_two_state()
    state4.player.sparks = 2
    state4.player.draw_pile = fodder(3)
    state4.player.hand = [up]
    play_card(state4, up)
    assert state4.player.sparks == 0
    assert state4.player.powers[klee_overhaul.BLAZING_DELIGHT] == 1

    # AND A SEAT WITHOUT THE POWER PAYS NOTHING.
    bare = _pass_two_state()
    bare.player.energy = 3
    bare.player.draw_pile = fodder(3)
    klee_overhaul.roll_to(bare, 2)
    klee_overhaul.turn_start_late(bare)
    assert bare.player.energy == 3
    assert bare.player.hand == []
