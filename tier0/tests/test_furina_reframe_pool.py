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
than deleting its gate; Shared Billing's stops going free).

AND A SECOND-WAVE READ OF THE SAME DAY (2026-09-06, a D default) found three of
those rows still mis-priced: the Cadenza copy Exhausts, because a 0-cost draw
whose gate depletes nothing is the same hold-the-deck loop at bar 3 as at 6;
Shared Billing's `+` buys 3 Block rather than a card, which was the loop piece
wearing a second hat; and the Rare drain pays 2 per Fanfare drained, with
Unheard Confession's per-change payout at 2. Those pins sit together at the
bottom of this file, each beside the loop or the dead slot it answers.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): these are shape assertions about an
offer surface, not numbers about a game.
"""

import random

import pytest

from tier0.content import loader, upgrades
from tier0.engine import combat, effects, furina_reframe as fr, resources
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy
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


def _state(enemies=None, seed=0):
    """A Furina fight, the shape `test_furina_reframe_slice2.furina_state`
    makes: the rows below are PLAYED rather than read, because Exhaust is a
    property of a card leaving the hand and nothing shorter can see it."""
    return CombatState(player=loader.build_player("furina"),
                       enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def test_the_cadenza_copy_exhausts_and_the_shipped_row_does_not(reframe):
    """THE HALF THE MOVED BAR DID NOT REACH (2026-09-06, a D default).

    A 0-cost draw whose gate DEPLETES nothing is a hold-the-rest-of-the-deck
    loop -- three copies, a hand cap of 10, the overflow to discard -- and it
    is that loop at bar 3 exactly as much as at bar 6, so re-pricing the smith
    could not close it. Exhaust makes each copy a one-shot instead.

    Read on the row AND in play: the flag is what the codegen emits the keyword
    from, and the pile is what the flag has to mean."""
    proto_id = fr.POOL_SUBS["florid_cadenza"]
    assert loader.peek_card(proto_id).exhaust is True
    assert not loader.peek_card("florid_cadenza").exhaust
    # The `+` card too -- the delta moves the bar and nothing else, so a copy
    # that stopped Exhausting at the smith would put the loop back. `get_card`
    # and not `peek_card`: `apply_upgrade` rewrites the card it is handed, and
    # peek's is the shared prototype every later read in this test sees.
    assert upgrades.apply_upgrade(loader.get_card(proto_id)).exhaust is True

    st = _state()
    card = loader.get_card(proto_id)
    st.player.energy = 5
    st.player.hand.append(card)
    combat.play_card(st, card)

    assert [c.id for c in st.player.exhaust_pile] == [proto_id]
    assert not [c for c in st.player.discard_pile if c.id == proto_id]


def test_the_drain_pays_five_plus_two_per_fanfare_drained(reframe):
    """THE ARM'S RARE DRAIN, at its second-wave slope (2026-09-06, a D
    default). At `per: 1` it never out-damaged Universal Revelry's arm copy
    anywhere in the meter's measured 0-to-15 range while ALSO emptying the
    meter, so it paid twice and bought nothing.

    Read off the ROW rather than off a literal formula, which is what makes
    this a pin on the card and not on the rail (the rail's own arithmetic is
    `test_furina_reframe_slice2`). 6 held is 5 + 12; an empty meter is the
    printed 5, because the row is small at 0 and never dead."""
    for held, expect in ((6, 17), (0, 5)):
        enemy = make_enemy(hp=300)
        st = _state(enemies=[enemy])
        resources.gain_fanfare(st, held, "fixture")

        effects.resolve_card(
            st, loader.get_card("proto_fr_let_the_people_rejoice"))

        assert st.player.fanfare == 0, held
        assert 300 - enemy.hp == expect, held


def test_the_shared_billing_copy_buys_block_at_the_smith(reframe):
    """The `+` card that used to buy a CARD (2026-09-06, a D default). A Common
    that already refunds its own Energy and then replaces itself is the loop
    piece the shipped `{cost: -1}` was taken off for; Block is neither energy
    nor draw, so the upgrade buys survival and the loop stays shut.

    The base row is unchanged, which is the other half of the claim: the Block
    arrives at the smith and nowhere else."""
    proto_id = fr.POOL_SUBS["shared_billing"]
    assert not [fx for fx in loader.peek_card(proto_id).effects
                if fx["op"] == "block"]

    # `get_card`, for the reason in the Cadenza pin above.
    upgraded = upgrades.apply_upgrade(loader.get_card(proto_id))
    assert upgraded.effects[-1] == {"op": "block", "amount": 3}
    assert not [fx for fx in upgraded.effects if fx["op"] == "draw"]
    # ... and the shipped row keeps its own `{cost: -1}` (R213 B).
    assert (upgrades.apply_upgrade(loader.get_card("shared_billing")).cost
            == loader.peek_card("shared_billing").cost - 1)


def test_the_confession_copy_pays_two_block_per_change(reframe):
    """The arm copy's power amount (2026-09-06, a D default). `EB-507` took the
    `gain_fanfare_floor` rider off this Rare and left the payout at the shipped
    1 -- but the power pays per change EVENT and not per point moved, and a
    2-cost Rare paying 1 Block per tick is a dead card. 2 is the floor that
    makes the slot worth a Rare; the shipped row stands at its own 1."""
    proto = loader.peek_card(fr.POOL_SUBS["unheard_confession"])
    power = next(fx for fx in proto.effects
                 if fx.get("power") == "fanfare_delta_block")
    assert power["amount"] == 2

    shipped = next(fx for fx in loader.peek_card("unheard_confession").effects
                   if fx.get("power") == "fanfare_delta_block")
    assert shipped["amount"] == 1


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
