"""real_silent: the second real base-game pool wired in as a reference.

EVERY test here is module-skipped when game_ref/ is absent, for the same
reason test_real_ironclad.py's are: game_ref/ is gitignored decompiled
material (.gitignore:28), so on a fresh clone the character genuinely does
not exist and there is nothing to assert. The fresh-clone half of the
contract is pinned unguarded in test_anchor_lock.py.

WHAT THIS ANCHOR IS, stated once so no number read off it is over-claimed:
the assembled pool is 56 of the character's 88 cards (22 -> 27 -> 46 -> 56
over 2026-07-27: the Sly keyword, then nineteen of her powers, then a
hand-translated layer of foreach/conditional/formula cards). The 32 excluded
are still not a random sample -- they are systematically the SHIV cards (the
token is not implemented), plus the cards that need a playability gate, a
card-selection prompt, or an enchantment.
This is a FLOOR on the Silent, not a portrait of her, and the coverage
fraction travels with every statline she produces.
"""

import random

import pytest
import yaml

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft, rewards

pytestmark = pytest.mark.skipif(
    not (loader.GAME_REF_DIR / "silent_pool.yaml").exists(),
    reason="game_ref/ is a local artifact; regenerate with "
           "tools/extract_base_game_pool.py + tools/build_official_sheet.py")


@pytest.fixture(scope="module")
def ref_cards():
    return [c for c in loader._card_index().values()
            if c.character == "real_silent"]


def test_every_reference_card_is_tagged(ref_cards):
    # rewards.character_pool filters on `character` (rewards.py:48). An
    # untagged row would be offered to EVERY character.
    assert ref_cards
    assert all(c.id.startswith("si_") for c in ref_cards)


def test_the_two_anchors_do_not_collide_with_each_other(ref_cards):
    """THE reason the id prefix had to stop being a module constant. Both
    pools contain a Strike and a Defend; under a shared prefix the second
    extraction would not have collided loudly, it would have overwritten the
    first in the card index."""
    ironclad = {c.id for c in loader._card_index().values()
                if c.character == "real_ironclad"}
    silent = {c.id for c in ref_cards}
    assert silent and not (silent & ironclad)
    assert all(cid.startswith("ic_") for cid in ironclad)


def test_reference_ids_do_not_collide_with_the_committed_pool(ref_cards):
    committed = {"strike", "defend", "shiv", "blade_dance_like"}
    assert not {c.id for c in ref_cards} & committed


def test_klee_is_never_offered_a_reference_card():
    pool = rewards.character_pool("klee")
    assert not [c for cs in pool.values() for c in cs
                if c.character == "real_silent"]


def test_reference_pool_is_the_real_pool_not_the_shiv_package():
    """The point of the exercise: real_silent must NOT fall into the
    ref_silent special case, whose "pool" is the six-card shiv_package."""
    pool = rewards.character_pool("real_silent")
    assert sum(len(cs) for cs in pool.values()) > 6
    assert any(c.character == "real_silent"
               for cs in pool.values() for c in cs)


def test_reference_pool_excludes_basic_and_ancient():
    pool = rewards.character_pool("real_silent")
    assert set(pool) <= {"common", "uncommon", "rare"}


def test_no_companions_for_the_reference():
    # PARITY: companions are Klee/Furina content and would inject elements
    # and reactions into a run that must be scored in the element-less world.
    rng = random.Random(1)
    for _ in range(20):
        assert not any(c.is_companion
                       for c in rewards.roll_rewards(rng, "real_silent"))


def test_build_player_matches_the_decompiled_character():
    # ...Models.Characters.Silent: StartingHp 70 and a TWELVE-card deck
    # (5 Strike / 5 Defend / Neutralize / Survivor) -- two more than the
    # Ironclad's ten, which is a real difference between the anchors and not
    # a transcription slip.
    player = loader.build_player("real_silent")
    assert player.max_hp == 70
    assert len(player.draw_pile) == 12
    # Ring of the Snake, wired 2026-07-27 (ask A1 ruled: implement). It acts
    # INSIDE combat -- +2 cards on turn one only -- unlike Burning Blood's
    # battery-inert post-fight heal, so it rides relic_effects (which carries
    # the amount) and not relic_hooks (which cannot). The battery gets it too:
    # scoring her without the relic she starts every fight holding understates
    # exactly the resource her discard plan spends.
    assert player.relic_hooks == []
    assert player.relic_effects == [{"hook": "combat_start_draw", "amount": 2}]


def test_the_starting_deck_needs_the_chosen_discard(ref_cards):
    """Survivor is a STARTER, and its second half is a chosen discard. If
    that op ever regresses, the failure should name the starting deck rather
    than surfacing as a strange win-rate."""
    survivor = next(c for c in ref_cards if c.id == "si_survivor")
    discards = [fx for fx in survivor.effects if fx["op"] == "discard"]
    assert discards and discards[0]["select"] == "chosen"
    assert "si_survivor" in [c.id for c in loader.build_player(
        "real_silent").draw_pile]


def test_reference_cards_carry_no_teyvat_machinery(ref_cards):
    # Same contract as the Ironclad anchor: `generic` IS required (draft.py
    # pays it +0.8, and withholding it would handicap the character under
    # test for a reason unrelated to her pool), while `generic` is not an
    # ARCHETYPE, so the tag cannot fake commitment.
    for c in ref_cards:
        assert c.archetypes == ["generic"]
        assert not any(a in draft.ARCHETYPES for a in c.archetypes)
        assert c.role_c is None and not c.guest_star and not c.kit_card
        assert c.element == "none"


def test_the_silent_pilot_has_every_mandatory_weight():
    # policy._score indexes these six with [] -- a missing key is a KeyError
    # mid-battery, not a bad score.
    w = loader.pilot_weights("silent")
    assert set(w) >= {"damage", "block", "scaling", "reaction", "tempo", "cost"}
    assert w["block"] == 1.2          # DECISIONS.md #9: frozen everywhere


def test_every_reference_card_has_an_applicable_upgrade(ref_cards):
    # Atomic external-artifact contract: partial coverage would bias smithing
    # and shop removal toward whichever cards happened to receive a `+` form.
    from tier0.content import upgrades
    # 22 -> 27 -> 46 across 2026-07-27: ask A4 (CardKeyword.Sly) freed the
    # five Sly cards, and the coverage pass that followed put nineteen more
    # of her powers on the dial. The count is pinned rather than derived
    # because a pool that quietly loads SMALLER is the failure this anchor
    # cannot detect any other way.
    assert len(ref_cards) == 56
    pool_ids = {card.id for card in ref_cards}
    for layer_name in loader.EXTERNAL_CARD_LAYERS["silent_pool.yaml"]:
        layer = yaml.safe_load((loader.GAME_REF_DIR / layer_name).read_text())
        assert {row["id"] for row in layer} <= pool_ids
    assert all(upgrades.has_upgrade(c.id) for c in ref_cards)
    for card in ref_cards:
        upgraded = loader.get_card(card.id + upgrades.SUFFIX)
        assert upgraded.id == card.id + upgrades.SUFFIX
        assert upgraded.name == card.name + upgrades.SUFFIX


def test_the_required_layer_lists_agree_between_loader_and_builder():
    """A reviewed layer listed in one place and not the other is a pool that
    loads at the wrong size -- silently, because both sides fail closed only
    against their OWN list."""
    from tools import build_official_sheet as build
    for name, spec in build.CHARACTERS.items():
        sheet = f"{name}_pool.yaml"
        if sheet not in loader.EXTERNAL_CARD_SHEETS:
            continue
        assert tuple(p.name for p in spec.supplements) == \
            loader.EXTERNAL_CARD_LAYERS.get(sheet, ())


def test_no_silent_card_silently_dropped_a_printed_keyword(ref_cards):
    """The defect this anchor's first extraction found: five Sly cards and
    two Innate cards were emitted as vanilla rows. Every printed keyword must
    now arrive on a FIELD rather than merely having survived the trip.

    The Sly five are in the pool as of ask A4 (ruled 2026-07-27: implement
    the base-game keyword), and they must carry `sly_keyword` -- the
    base-game auto-play -- and never Kokomi's `sly` effect list, which would
    read as a printed rule that does nothing."""
    assert sum(c.sly_keyword for c in ref_cards) == 7
    assert not any(c.sly for c in ref_cards)
    assert any(c.innate for c in ref_cards)


def test_ring_of_the_snake_fires_on_turn_one_and_only_turn_one(ref_cards):
    """Ask A1, ruled 2026-07-27. The relic is a first-turn hand-size bonus
    (ModifyHandDraw returns count + 2, then bails out for TurnNumber > 1),
    so it must show up as two extra cards in the OPENING hand and nothing
    afterwards. Driven through a real fight rather than asserted on the yaml
    -- the point of the ruling is that she plays with the relic, and the
    battery path is the one that had none."""
    from tier0.engine import combat
    from tier0.tests.conftest import make_enemy

    hands = []

    def pilot(state):
        hands.append(len(state.player.hand))

    player = loader.build_player("real_silent")
    combat.run_fight(player, [make_enemy(hp=200)], pilot, seed=11)
    assert hands[0] == C.CARDS_DRAWN_PER_TURN + 2
    assert hands[1] == C.CARDS_DRAWN_PER_TURN
