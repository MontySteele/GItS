"""real_ironclad: the real base-game pool wired in as a second reference.

EVERY test here is module-skipped when game_ref/ is absent. That is not
timidity about a flaky fixture -- game_ref/ is gitignored decompiled
material (.gitignore:28), so on a fresh clone the character genuinely does
not exist and there is nothing to assert. The fresh-clone half of the
contract is pinned unguarded in test_anchor_lock.py.
"""

import random

import pytest

from tier0.content import loader
from tier05 import draft, rewards

pytestmark = pytest.mark.skipif(
    not (loader.GAME_REF_DIR / "ironclad_pool.yaml").exists(),
    reason="game_ref/ is a local artifact; regenerate with "
           "tools/extract_base_game_pool.py + tools/build_ironclad_sheet.py")


@pytest.fixture(scope="module")
def ref_cards():
    return [c for c in loader._card_index().values()
            if c.character == "real_ironclad"]


def test_every_reference_card_is_tagged(ref_cards):
    # rewards.character_pool filters on `character` (rewards.py:48). An
    # untagged row would be offered to EVERY character -- Klee drafting a
    # Bash is the failure this tag prevents.
    assert ref_cards
    assert all(c.id.startswith("ic_") for c in ref_cards)


def test_reference_ids_do_not_collide_with_the_committed_pool(ref_cards):
    # A raw `Bash` -> `bash` would hit the duplicate-id raise in
    # _card_index() and red the suite for everyone holding game_ref/.
    # _card_index() building at all is most of the proof; this names it.
    committed = {"strike", "defend", "bash"}
    assert not {c.id for c in ref_cards} & committed


def test_klee_is_never_offered_a_reference_card():
    pool = rewards.character_pool("klee")
    assert not [c for cs in pool.values() for c in cs
                if c.character == "real_ironclad"]


def test_reference_pool_is_the_real_pool_not_a_package():
    # The point of the whole exercise: he must NOT fall into the
    # ref_ironclad special case, whose "pool" is 5 distinct cards.
    pool = rewards.character_pool("real_ironclad")
    assert sum(len(cs) for cs in pool.values()) > 5
    assert any(c.character == "real_ironclad"
               for cs in pool.values() for c in cs)


def test_reference_pool_leaks_exactly_the_untagged_construct_cards():
    """PRE-EXISTING, and pinned here rather than fixed.

    The untagged `*_like` cards in tier0/content/cards/ carry no
    `character`, so rewards.py:48 cannot exclude them from ANY pool --
    Klee's reward screens have always offered Cleave-like. real_ironclad
    inherits the same leak, which means the two characters are drafting
    under identical contamination. That is parity, so it is the correct
    state for this comparison; tagging them would move Klee's pool and
    invalidate her archived pass numbers. Anyone reading an Ironclad
    scorecard needs this on the record.
    """
    leaked = {c.id for cs in rewards.character_pool("real_ironclad").values()
              for c in cs if c.character is None}
    assert leaked == {c.id for cs in rewards.character_pool("klee").values()
                      for c in cs if c.character is None}


def test_reference_pool_excludes_basic_and_ancient():
    # Basic (the starters) and Ancient are not draftable rarities. They are
    # dropped by the rarity filter, NOT remapped to `rare` -- a remap would
    # quietly inject Break/Corruption into reward screens.
    pool = rewards.character_pool("real_ironclad")
    assert set(pool) <= {"common", "uncommon", "rare"}


def test_no_companions_for_the_reference():
    # PARITY: companions are Klee/Furina content and would inject elements
    # and reactions into a run that must be scored in the same
    # element-less world Klee was.
    rng = random.Random(1)
    for _ in range(20):
        assert not any(c.is_companion
                       for c in rewards.roll_rewards(rng, "real_ironclad"))


def test_build_player_matches_the_decompiled_character():
    # ilspycmd -t ...Models.Characters.Ironclad: StartingHp 80, a 10-card
    # deck of 5 Strike / 4 Defend / 1 Bash, and Burning Blood.
    player = loader.build_player("real_ironclad")
    assert player.max_hp == 80
    assert len(player.draw_pile) == 10
    assert player.relic_hooks == ["heal_after_won_fight"]


def test_reference_cards_carry_no_teyvat_machinery(ref_cards):
    # No role_c and no guest_star keeps them out of the companion and
    # guest-star pools; element "none" keeps them out of the reaction system.
    #
    # `generic` IS required, and an earlier revision of this test asserting
    # `archetypes == []` was wrong in a way that would have biased the
    # measurement it exists to support. Two reasons, both mechanical:
    #   - draft.py:143 pays `generic` +0.8 in the reward scorer. Untagged
    #     Ironclad cards would score 0.8 below every untagged Klee glue card,
    #     handicapping the character under test in the tier05 comparison for
    #     a reason that has nothing to do with his pool. PARITY means he
    #     carries the same tag our own untagged glue carries (83 cards do).
    #   - archetype_shares (draft.py:241) counts only ARCHETYPES, and
    #     `generic` is deliberately not one -- so the tag cannot fake
    #     commitment. That was the property `[]` was reaching for, and it
    #     already holds without paying the drafting penalty.
    # The leak `[]` was actually guarding -- cards_in_pool() not filtering on
    # `character` -- is real but unreachable: `demolition_commons` is the only
    # pool any card names, and no `generic_*` pool exists. Logged, not fixed
    # here; fixing it belongs with cards_in_pool, not with this sheet.
    for c in ref_cards:
        assert c.archetypes == ["generic"]
        assert not any(a in draft.ARCHETYPES for a in c.archetypes)
        assert c.role_c is None and not c.guest_star and not c.kit_card
        assert c.element == "none"


def test_the_ironclad_pilot_has_every_mandatory_weight():
    # policy._score indexes these six with [] -- a missing key is a
    # KeyError mid-battery, not a bad score.
    w = loader.pilot_weights("ironclad")
    assert set(w) >= {"damage", "block", "scaling", "reaction", "tempo", "cost"}
    assert w["block"] == 1.2          # DECISIONS.md #9: frozen everywhere


def test_reference_cards_are_unupgraded_and_say_so(ref_cards):
    # LOGGED, not fixed: upgrades.UPGRADE_SHEETS is a fixed docs/ tuple, so
    # no `<id>+` form exists for the reference pool and he is scored
    # entirely unupgraded. If someone wires external upgrades in, this test
    # fails and the report's caveat has to be revisited with it.
    from tier0.content import upgrades
    assert not any(upgrades.has_upgrade(c.id) for c in ref_cards)
