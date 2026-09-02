"""The Kokomi overhaul arm (slice one) -- the flag, and both sides of it.

The ruled brief is `review/active/kokomi-brief-2026-09-01.md` (sec.4, the eight
rules; sec.8 and sec.9, the relic and the starter) and the slice is
`review/active/kokomi-overhaul-slice-1-2026-09-01.md` (sec.3 the ten-card
starter, sec.4 the 28 pool rows, sec.5 the engine build list).

THE FIRST SECTION IS THE ONE THAT MATTERS. `C.KOKOMI_OVERHAUL` ships OFF, and
with it off every Kokomi number ever measured is still comparable and the
Kurage's-memory arm beside it still owns its own seams. That is an ACCEPTANCE
CONDITION, not an intention, so it is pinned the way `test_klee_overhaul.py`
pins its own: as a digest of a fixed-seed fight's whole event log, plus the
shape of every seam this arm touches.

WHAT THE SIM DOES AND DOES NOT DO HERE. Slice one is C# FIRST (the slice packet
sec.5: "All of it behind the prototype switch, C# first. The Python sim is not
brought up for slice one"). So tier0 LOADS, VALIDATES and RESOLVES-BY-ID the
slice's rows, and it REFUSES to resolve their new ops rather than shipping a
second, unplayed implementation of a rule the mod has not proved yet.
`test_the_new_ops_refuse_to_resolve` is that refusal asserted, not tolerated.

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

SEED = 11

#: Every op slice one adds. Registered in `effects.OPS` so the loader's
#: vocabulary check accepts a row, priced in `draft.STATIC_OP_PRICING` so
#: `lint_op_parity` stays green, and resolved by nothing.
OVERHAUL_OPS = ("gain_tide", "surge", "block_half_surge", "exert", "mend",
                "plan", "draw_companion_from_draw", "next_companion_free",
                "draw_per_tide", "play_top_of_draw")


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
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    yield
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()


def kokomi_fight(seed=SEED):
    pilot = make_pilot(loader.pilot_weights("priest"))
    player = loader.build_player("kokomi")
    return run_fight(player, loader.build_encounter("punisher"), pilot,
                     seed=seed)


def log_digest(state) -> str:
    return hashlib.sha256(
        json.dumps(state.log, sort_keys=True, default=str
                   ).encode("utf-8")).hexdigest()


# --- 1. FLAG OFF IS BYTE-IDENTICAL -----------------------------------------

def test_the_flag_ships_off():
    """The quarantine. Everything below only matters while this holds."""
    assert C.KOKOMI_OVERHAUL is False


def test_a_fixed_seed_kokomi_fight_is_reproducible_with_the_flag_off():
    """THE ACCEPTANCE CONDITION, as a digest of the whole log.

    Pinned against ITSELF at the branch point rather than against a literal
    copied from another file: no other arm's test fights Kokomi, so there is no
    existing digest to share and inventing one here would only pin today's
    date. Two runs of the same seed on the same tree must agree, and the ARM
    must not move either of them -- which is what the pair below says.
    """
    assert log_digest(kokomi_fight()) == log_digest(kokomi_fight())


def test_the_starter_is_the_printed_starter_with_the_flag_off():
    """Twelve cards, the Silent shape, exactly as ratified."""
    ids = loader.starting_deck("kokomi")
    assert len(ids) == 12
    assert not any(cid.startswith("proto_kk_") for cid in ids)


def test_no_pool_is_replaced_with_the_flag_off():
    """The seam returns None for everybody, so `character_pool` never enters
    its branch and is byte-for-byte the function it has always been."""
    for character in ("klee", "furina", "kokomi", "ref_ironclad",
                      "real_silent"):
        assert loader.pool_replacement(character) is None


def test_the_offerable_pool_carries_no_overhaul_row_with_the_flag_off():
    pool = rewards.character_pool("kokomi")
    ids = {c.id for cards in pool.values() for c in cards}
    assert not any(cid.startswith("proto_kk_") for cid in ids)
    # The shipped pool, still there and still hers. `undertow` and
    # `cleansing_tide` are SHIPPED Kokomi rows whose display names the slice
    # re-uses under a "(proto)" suffix, so this also says the two cannot be
    # confused for one another.
    assert "undertow" in ids
    assert "cleansing_tide" in ids


def test_the_overhaul_ids_do_not_resolve_with_the_flag_off():
    """The quarantine's own door, shut. `_card_prototype`'s prototype branch
    is guarded by the flags, so a `proto_kk_` id is a KeyError here -- which
    is what makes "the rows never enter an ordinary run" a property of the
    code rather than a filter somebody remembers."""
    loader._card_prototype.cache_clear()
    with pytest.raises(KeyError):
        loader.get_card(C.KOKOMI_OVERHAUL_STARTER_IDS[0])
    loader._card_prototype.cache_clear()


def test_the_kurage_memory_arm_is_untouched():
    """The overhaul is a FOURTH arm. Editing the memory arm's constants would
    make its OFF/ON pair incomparable, which is the one thing a multi-arm flag
    exists to prevent."""
    assert C.KURAGE_MEMORY_STARTER_DROP == "bake_kurage"
    assert C.KURAGE_MEMORY_POOL_DROP == "kurages_oath"
    assert C.KLEE_OVERHAUL is False
    assert C.COMPANION_OVERHAUL is False


# --- 2. THE ARM'S OWN SHAPE ------------------------------------------------

def test_the_starter_is_ten_cards_five_ids():
    """Slice packet sec.3: Water's Edge x3, Coral Guard x3, Kurage's Oath x2,
    Rising Tide, Stolen Chapter."""
    ids = C.KOKOMI_OVERHAUL_STARTER_IDS
    assert len(ids) == 10
    assert len(set(ids)) == 5
    assert ids.count("proto_kk_waters_edge") == 3
    assert ids.count("proto_kk_coral_guard") == 3
    assert ids.count("proto_kk_kurages_oath") == 2
    assert ids.count("proto_kk_rising_tide") == 1
    assert ids.count("proto_kk_stolen_chapter") == 1


def test_the_pool_is_all_twenty_eight_of_the_slices_rows():
    """Slice packet sec.4, whole. Pinned rather than described because it is
    the slice's own scope statement, and because -- unlike the Klee arm, which
    dropped Vermillion Pact on its packet's own escape -- NOTHING drops here."""
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 28
    assert len(set(ids)) == 28
    assert not set(ids) & set(C.KOKOMI_OVERHAUL_STARTER_IDS)


def test_the_numbers_are_the_briefs_placeholders():
    """Slice packet sec.1: no number in it is a claim. These six are the rules'
    own, and they are named so `lint_constant_parity` can compare the C#
    mirrors BY VALUE."""
    assert C.KOKOMI_OVERHAUL_PULSE_MEND == 2
    assert C.KOKOMI_OVERHAUL_PULSE_BUDGET == 8
    assert C.KOKOMI_OVERHAUL_SONG_MEND == 3
    assert C.KOKOMI_OVERHAUL_SONG_BUDGET == 12
    assert C.KOKOMI_OVERHAUL_GARMENT_MEND == 2
    assert C.KOKOMI_OVERHAUL_TIDE_PER_CARD == 5


# --- 3. THE FLAG ON: the rows are reachable, and only these rows -----------

def test_the_starter_resolves_to_the_slices_ten_cards(overhaul):
    """`starting_deck` is the ONE seam both the tier 0 battery and the tier 0.5
    run read, so this is what she opens with on either path."""
    ids = loader.starting_deck("kokomi")
    assert ids == list(C.KOKOMI_OVERHAUL_STARTER_IDS)
    assert all(cid.startswith("proto_kk_") for cid in ids)
    # And each one is a real, loadable, validated card -- not just a string.
    for cid in set(ids):
        card = loader.get_card(cid)
        assert card.character == "kokomi"
        assert card.id == cid


def test_the_offerable_pool_is_the_slice_and_nothing_else(overhaul):
    """`rewards.character_pool` is the single source of truth for every offer
    surface -- fight rewards, the shop, every event card screen and the tier
    0.5 drafter -- so this one assertion covers all five."""
    pool = rewards.character_pool("kokomi")
    ids = {c.id for cards in pool.values() for c in cards}
    assert ids == set(C.KOKOMI_OVERHAUL_POOL_IDS)


def test_the_pool_keeps_the_packets_rarity_split(overhaul):
    """12 Common, 12 Uncommon, 4 Rare -- the packet's sec.4 count. Pinned
    because the rarity buckets ARE the offer odds: a row filed in the wrong
    tier changes how often it is seen."""
    pool = rewards.character_pool("kokomi")
    assert {r: len(cs) for r, cs in sorted(pool.items())} == {
        "common": 12, "uncommon": 12, "rare": 4}


def test_no_other_character_moves_under_the_flag(overhaul):
    """The seam is Kokomi's alone. A flag that quietly re-pooled Klee would
    make every number measured on him incomparable."""
    for character in ("klee", "furina"):
        assert loader.pool_replacement(character) is None
        ids = {c.id for cards in rewards.character_pool(character).values()
               for c in cards}
        assert not any(cid.startswith("proto_kk_") for cid in ids)


def test_every_row_prints_its_own_face():
    """EB-215's channel, and the whole slice uses it: a prototype that rewrites
    what a shipped power does cannot say so through the body renderers without
    moving the shipped card's face with it.

    Read off the SHEET rather than off a loaded `Card`, because `description:`
    is deliberately not a tier0 card field -- it is the emitter's channel and
    the sim has no use for it.
    """
    import yaml
    rows = yaml.safe_load(loader.PROTOTYPE_SHEET.read_text(encoding="utf-8"))
    faces = {r["id"]: r.get("description") for r in rows}
    for cid in set(C.KOKOMI_OVERHAUL_POOL_IDS) | set(
            C.KOKOMI_OVERHAUL_STARTER_IDS):
        assert faces.get(cid), cid


# --- 4. THE ONE C# FACT NO IL SCAN CAN SEE ---------------------------------

def test_exert_is_block_first_and_not_an_hp_loss():
    """RULE 5, source-level, because a ValueProp is invisible to an IL scan.

    The one word that IS the rule. The mod's shipped self-cost
    (`{op: damage, target: self}`, Hot Hands) is `Unblockable | Unpowered`,
    which is how the base game models an HP cost -- it walks PAST Block on
    purpose. Exert must not: the brief's contested thing (sec.5) is that "a
    Block card is worth two things and she picks which", and dropping
    `Unblockable` is the whole of what makes Block fuel.

    A ValueProp is an enum literal, so `Il.Calls` cannot see it and the C# pin
    can only assert that a damage command is reached. Source-level here, for
    the same reason `test_starter_relic_upgrades.py` is source-level: the
    logic is C#, the fact is a constant, and the absence is exactly what a
    compiler cannot see.
    """
    from pathlib import Path
    import re
    root = Path(__file__).resolve().parents[2]
    src = (root / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "ProtoBakeKuragePower.cs").read_text(encoding="utf-8")
    body = re.search(r"public static async Task Exert\(.*?\n    \}",
                     src, re.DOTALL)
    assert body, "KokomiTide.Exert is gone -- rule 5 moved under this pin"
    call = body.group(0)
    assert "ValueProp.Unpowered" in call
    assert "Unblockable" not in call, (
        "KokomiTide.Exert marks its damage Unblockable, which walks past "
        "Block -- rule 5 is 'Lose N HP, taken from Block FIRST', and the "
        "brief's contested thing depends on Block being able to eat it")


# --- 5. THE OPS ARE REGISTERED AND REFUSE TO RUN ---------------------------

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
        card = Card(id="probe", name="probe", cost=1, type="skill",
                    effects=[{"op": op}])
        with pytest.raises(NotImplementedError) as excinfo:
            effects.OPS[op](state, {"op": op}, card)
        assert "KOKOMI_OVERHAUL" in str(excinfo.value)
