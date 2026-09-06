"""THE FURINA REFRAME'S POOL SEAM (QUARANTINED, `furina_reframe.FURINA_REFRAME`).

Round 2 pick 1, taken at its default 2026-09-04. Four shipped rows gate on a
Fanfare bar the arm's performance-only meter does not reach -- 12, 12, 15 and
20, against a meter that ranged 0 to 15 across three rounds -- so under the arm
the shipped id leaves the offer surface and an arm-only copy at 6, 6, 8 and 10
takes its slot at the SAME rarity. Nothing on the shipped sheet moves.

The seam is `furina_reframe.POOL_SUBS`, read by
`loader._pool_substitutions` at the one door `tier05.rewards.character_pool`
already reads (fight rewards, the shop, every event card screen and the tier
0.5 drafter). Its C# twin is `FurinaReframeRoster.SwapOfferedRiders`, wired
into `FurinaCardPool.FilterThroughEpochs` beside Kokomi's Oath swap.

THE SAME SEAM NOW CARRIES `EB-507` (2026-09-06). The arm mints Fanfare by
PERFORMING, and `gain_fanfare_floor` mints it for being played -- a second
source the reframe neither has nor priced, printed by three shipped Rares. Two
of them are swapped for the same body without the rider; the third is nothing
BUT the rider, so its Rare slot goes to the arm's own Rare drain. The same
change re-prices two arm `+` cards (Florid Cadenza's copy moves its bar rather
than deleting its gate; Shared Billing's buys a card rather than going free).

NOTHING MEASURED HERE IS QUOTABLE (R215 B): these are shape assertions about an
offer surface, not numbers about a game.
"""

import pytest

from tier0.content import loader, upgrades
from tier0.engine import furina_reframe as fr
from tier05 import rewards


@pytest.fixture
def reframe(monkeypatch):
    """The master flag on, with both id-resolving caches cleared on the way in
    and out -- `test_kokomi_overhaul.overhaul`'s fixture, for its reasons."""
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(fr, "FURINA_REFRAME", True)
    yield
    loader.reset_caches()
    rewards.character_pool.cache_clear()


def pool_ids(character="furina"):
    return {c.id for cards in rewards.character_pool(character).values()
            for c in cards}


def by_rarity(character="furina"):
    return {r: len(cs)
            for r, cs in rewards.character_pool(character).items()}


def test_the_map_is_the_sheets_own_replaces_key():
    """DERIVED IN NEITHER DIRECTION, COMPARED IN BOTH. The maps are literals in
    `furina_reframe` (the flag lives there rather than in `constants.py`, for
    the reason that module's header gives) and the rows carry `replaces:`; a
    copy on the surface that nobody named in either would otherwise be a row
    that is never offered AND never dealt, which is exactly the defect
    `lint_arm_pool_parity` was written for one arm over.

    BOTH SEAMS AT ONCE, because the sheet key does not say which door a row
    goes through: `replaces:` means only "this arm swaps me in", and R254's
    starter reader is the first row that swaps in at the printed starter
    rather than at the offer. The two maps are asserted DISJOINT, so the union
    cannot quietly cover a shipped id claimed by both."""
    on_sheet = {c.replaces: c.id for c in loader.prototype_cards()
                if c.replaces is not None and not c.personal_pool
                and c.character == "furina"}
    assert not set(fr.POOL_SUBS) & set(fr.STARTER_SUBS)
    assert on_sheet == {**fr.POOL_SUBS, **fr.STARTER_SUBS}


def test_the_arm_off_offers_the_shipped_rows_and_no_prototype():
    """The acceptance condition on the flag, pinned rather than intended."""
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    assert loader.pool_substitutions("furina") == {}
    ids = pool_ids()
    for shipped, proto in fr.POOL_SUBS.items():
        assert shipped in ids
        assert proto not in ids


def test_the_arm_on_offers_the_copy_and_not_the_shipped_row(reframe):
    assert loader.pool_substitutions("furina") == dict(fr.POOL_SUBS)
    ids = pool_ids()
    for shipped, proto in fr.POOL_SUBS.items():
        assert shipped not in ids
        assert proto in ids


def test_the_swap_moves_no_card_between_rarity_tiers(reframe):
    """A substitution is a face swap. Moving a card between tiers would move
    the odds it is offered at, which is a balance change smuggled in as a
    quarantine -- `rewards.character_pool` raises on one, and this is the read
    from the other side: the buckets are the same size with the arm on."""
    off = by_rarity()
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    with_arm = by_rarity()
    assert off == with_arm
    for shipped, proto in fr.POOL_SUBS.items():
        assert (loader.peek_card(shipped).rarity
                == loader.peek_card(proto).rarity)


def test_the_copies_carry_the_arms_thresholds_and_the_shipped_rows_do_not(
        reframe):
    """The whole reason the swap exists. The shipped bars are 12, 12, 15 and
    20; the copies read 6, 6, 8 and 10, and the shipped rows are untouched.

    THE THIRD COLUMN IS THE `+` CARD (2026-09-06). Only Florid Cadenza's copy
    moves its bar at the smith -- its upgrade used to DELETE the gate, which
    made a 0-cost draw-3 that asks nothing -- and the other three ask the same
    question upgraded as they do printed. Written as one column rather than a
    second test so that "which copies move a bar, and to where" is one table
    to read, and a copy that starts moving one cannot do it unnoticed."""
    bars = {"florid_cadenza": ("fanfare_at_least_12", "fanfare_at_least_6",
                               "fanfare_at_least_3"),
            "dramatic_entrance": ("fanfare_at_least_12", "fanfare_at_least_6",
                                  "fanfare_at_least_6"),
            "universal_revelry": ("fanfare_at_least_15", "fanfare_at_least_8",
                                  "fanfare_at_least_8"),
            "flood_of_emotion": ("fanfare_at_least_20", "fanfare_at_least_10",
                                 "fanfare_at_least_10")}
    for shipped, (shipped_bar, proto_bar, upgraded_bar) in bars.items():
        proto = loader.peek_card(fr.POOL_SUBS[shipped])
        assert _bar(loader.get_card(shipped)) == shipped_bar
        assert _bar(proto) == proto_bar
        assert _bar(upgrades.apply_upgrade(proto)) == upgraded_bar


def test_the_cadenza_copy_upgrades_by_moving_its_bar_not_by_dropping_it(
        reframe):
    """`{condition: fanfare_at_least_3}`, the grammar's second spelling.

    The delta this row used to carry was `{condition: unconditional}`, which
    hoists the branch out and leaves a 0-cost "draw 3" with no question on it.
    The upgraded card still draws 1 and still asks; it asks for less. Pinned as
    the SHAPE of the upgraded body -- one conditional, still there, with a
    lower bar -- because the failure it guards against is the branch being
    hoisted again and the test passing on the numbers alone."""
    proto = loader.peek_card(fr.POOL_SUBS["florid_cadenza"])
    upgraded = upgrades.apply_upgrade(proto)

    assert [fx["op"] for fx in upgraded.effects] == ["draw", "conditional"]
    assert upgraded.effects[0]["amount"] == 1
    assert upgraded.effects[1]["if"] == "fanfare_at_least_3"
    assert upgraded.effects[1]["then"] == [{"op": "draw", "amount": 2}]


def test_no_offered_card_promises_fanfare_for_being_played(reframe):
    """`EB-507`'s acceptance condition, and the arm's one sentence about its
    meter: Fanfare is minted by PERFORMING. `gain_fanfare_floor` mints it for
    being played, which is a second source the reframe neither has nor priced,
    and three shipped Rares print one. With the arm on, no card any offer
    surface can roll carries the op."""
    for card in _offerable():
        assert not any(fx.get("op") == "gain_fanfare_floor"
                       for fx in card.effects), card.id


def test_the_arm_off_still_offers_all_three_floor_rows():
    """The other half of the same claim, and the acceptance condition on the
    flag: the three shipped floor Rares are Balance-stage content and do not
    move for a prototype arm (R213 B)."""
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    floors = {card.id for card in _offerable()
              if any(fx.get("op") == "gain_fanfare_floor"
                     for fx in card.effects)}
    assert floors == {"rapturous_applause", "unheard_confession",
                      "the_sea_is_my_stage"}


def _offerable(character="furina"):
    return [c for cards in rewards.character_pool(character).values()
            for c in cards]


def _bar(card):
    return next(fx["if"] for fx in card.effects
                if fx.get("op") == "conditional")


def test_no_other_character_moves(reframe):
    """Every leg of this arm is character-scoped (`is_furina`), and the pool
    seam is no exception: in co-op the other seat may be Klee."""
    for other in ("klee", "kokomi"):
        assert loader.pool_substitutions(other) == {}
