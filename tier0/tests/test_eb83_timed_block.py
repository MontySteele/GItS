"""EB-83 -- `block_at_turn_start`, the duration-scoped repeating Block power,
built as UNUSED MACHINERY.

The row's one live blocker was an engine op: Toric Toughness's replacement
(designed-not-shipped as *Chinowa Ward*) prints "gain X Block at the start of
your next 2 turns", and tier0 had no way to say it. `block_next_turn` is a
one-shot bank popped whole at the next turn start, and `powers` is a
`name -> int` map, so a power carrying *(amount, turns remaining)* had nowhere
to put its second number.

It is built FIRST AND ALONE, on the EB-82 admission rule: an engine surface is
never invented inline inside a conversion. The two replacement cards and the
Wood Carvings conversion are [USER]-gated (the RT window, and the S4-G11
name eye-read), so this lands with NO CARRIER at all.

The first tests below pin that carrier-lessness -- which is the stamp-free
claim, and therefore the claim that no measured number moved. The rest drive
the op by hand, which is the only way the machinery runs at all today.
"""

from pathlib import Path

import pytest

from tier0.content import enchantments, loader
from tier0.engine import combat, effects, powers
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import draft
from tools import card_connectivity_report as ccr
from tools import effect_walk

OP = effects.BLOCK_AT_TURN_START

REPO = Path(effects.__file__).resolve().parents[2]


def card(cid="c", type="skill", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


def play(state, fx, **kw):
    c = card("driver", fx=fx, **kw)
    state.player.hand.append(c)
    combat.play_card(state, c)
    return c


# --- what reaches the op: nothing -----------------------------------------

def test_no_loaded_card_prints_the_op_anywhere_in_its_tree():
    """The stamp-free claim, at the loader. Walked as a TREE, not a flat list:
    a `conditional`'s `then:` and a `choose_one`'s mode body are as printed as
    anything at the top level, and a flat read is exactly how an op hides."""
    for cid, c in loader._card_index().items():
        for field in (c.effects, c.sly, c.enchant_effects,
                      c.enchant_first_play_effects):
            assert all(fx.get("op") != OP
                       for fx in effect_walk.iter_effects(field)), cid


def test_no_committed_sheet_mentions_the_op_at_all():
    """The same claim one level below the loader, as raw text, so it also
    covers the sheets the card index does not build: every `*-upgrades.yaml`
    delta key, the tier 0.5 relic / potion / event content, and any sheet a
    fresh clone loads that this process happened not to.

    Text rather than structure ON PURPOSE. The question is not "does a card
    resolve this op" -- it is "did any number that a measured world is made of
    move", and for that the honest test is that the string does not occur.
    """
    roots = [REPO / "docs", REPO / "tier05" / "content", REPO / "tier0" /
             "content"]
    scanned = 0
    for root in roots:
        for path in sorted(root.rglob("*.yaml")):
            scanned += 1
            assert OP not in path.read_text(encoding="utf-8"), path
    assert scanned > 10, "the sheet sweep found almost nothing; it has rotted"


def test_the_carrier_is_empty_on_a_freshly_built_player():
    """`survives nothing across combats` is a claim about a LIFETIME, and the
    lifetime is `powers`': both maps default empty on a fresh Player, and tier
    0.5 builds one per fight. Neither is swept in `run_fight`, and this pins
    that they agree rather than that either one is swept."""
    p = make_state().player
    assert p.timed_power_amounts == {}
    assert p.powers == {}


# --- the op, driven by hand -----------------------------------------------

def test_it_pays_at_the_start_of_exactly_the_printed_number_of_turns():
    st = make_state(enemies=[make_enemy(hp=400)])
    play(st, [{"op": OP, "amount": 5, "turns": 2}])
    # Nothing on the turn it was played -- the payout seam is turn START, and
    # this turn's has already gone by.
    assert st.player.block == 0
    assert st.player.powers[OP] == 2
    assert st.player.timed_power_amounts[OP] == 5

    combat._player_turn(st, lambda s: None)      # resets block, then triggers
    assert st.player.block == 5
    assert st.player.powers[OP] == 1

    combat._player_turn(st, lambda s: None)
    assert st.player.block == 5
    # Expired: BOTH entries leave together, so nothing is left for a later
    # application to add itself onto.
    assert OP not in st.player.powers
    assert OP not in st.player.timed_power_amounts

    combat._player_turn(st, lambda s: None)
    assert st.player.block == 0                  # a third turn pays nothing


def test_turns_one_is_the_block_next_turn_shape_and_agrees_with_it():
    """The degenerate duration must not be a different mechanic. Both ops on
    the same board, same amount: identical Block, one turn later, and both
    gone afterwards."""
    a = make_state(enemies=[make_enemy(hp=400)])
    play(a, [{"op": OP, "amount": 6, "turns": 1}])
    b = make_state(enemies=[make_enemy(hp=400)])
    play(b, [{"op": "block_next_turn", "amount": 6}])
    combat._player_turn(a, lambda s: None)
    combat._player_turn(b, lambda s: None)
    assert a.player.block == b.player.block == 6
    assert OP not in a.player.powers
    assert "block_next_turn" not in b.player.powers


def test_the_amount_is_snapshotted_at_play_time_and_never_re_read():
    """"Gain THAT MUCH Block" is settled when the card resolves, which is why
    the amount lives in the carrier instead of being re-derived at each payout.

    Driven with a RUNTIME COUNT, because that is the only amount whose re-read
    would give a different answer: `block_gained_this_card` is 7 while the card
    resolves and 0 by the time either payout fires. Both turns pay 7.
    """
    st = make_state(enemies=[make_enemy(hp=400)])
    powers.apply_power(st, st.player, "dexterity", 3)
    play(st, [{"op": "block", "amount": 4},
              {"op": OP, "amount": "block_gained_this_card", "turns": 2}])
    assert st.player.timed_power_amounts[OP] == 7
    play(st, [])                                 # any next card clears it
    assert st.block_gained_this_card == 0        # the source is already gone

    combat._player_turn(st, lambda s: None)
    assert st.player.block == 7
    assert st.player.timed_power_amounts[OP] == 7    # the carrier is unmoved
    combat._player_turn(st, lambda s: None)
    assert st.player.block == 7


def test_the_payout_is_raw_like_its_one_shot_sibling():
    """`block_next_turn`'s payout is deliberately outside both block funnels:
    the power that banked it has expired, and Dexterity must not scale power
    block. The duration-scoped twin shares that behaviour rather than
    acquiring its own -- two delayed-Block ops with different funnels is the
    drift this pins against.

    Both directions, because the funnel is additive at one end and
    multiplicative at the other: Dexterity does not inflate the payout, and a
    Frail landed after the play does not shrink a half already banked.
    """
    st = make_state(enemies=[make_enemy(hp=400)])
    powers.apply_power(st, st.player, "dexterity", 3)
    play(st, [{"op": OP, "amount": 4, "turns": 1}])
    combat._player_turn(st, lambda s: None)
    assert st.player.block == 4                  # not 7

    other = make_state(enemies=[make_enemy(hp=400)])
    play(other, [{"op": OP, "amount": 10, "turns": 1}])
    powers.apply_power(other, other.player, "frail", 5)
    combat._player_turn(other, lambda s: None)
    assert other.player.block == 10              # not 7


# --- stacking (PLACEHOLDER: additive amount, max turns) --------------------

def test_stacking_is_additive_on_amount_and_max_on_turns():
    """PLACEHOLDER -- sheet-pass sweep, user pick. No ratified rule for
    same-name *(amount, turns)* effects exists to inherit: the engine's
    ratified duration rules are all single-field refreshes and settle only the
    turns half. This pins the placeholder so a change to it is a deliberate
    edit rather than a quiet one."""
    st = make_state(enemies=[make_enemy(hp=400)])
    play(st, [{"op": OP, "amount": 5, "turns": 3}])
    play(st, [{"op": OP, "amount": 2, "turns": 1}])
    assert st.player.timed_power_amounts[OP] == 7     # additive
    assert st.player.powers[OP] == 3                  # max, never shortened
    combat._player_turn(st, lambda s: None)
    assert st.player.block == 7


def test_a_second_casting_never_shortens_a_standing_one():
    st = make_state(enemies=[make_enemy(hp=400)])
    play(st, [{"op": OP, "amount": 4, "turns": 4}])
    play(st, [{"op": OP, "amount": 4, "turns": 2}])
    assert st.player.powers[OP] == 4


# --- the duration is printed text, and it is checked at LOAD --------------

@pytest.mark.parametrize("turns", [0, -1, None, "X", 2.0, True])
def test_a_duration_that_is_not_a_positive_literal_int_is_refused(turns):
    with pytest.raises(ValueError, match="positive literal int"):
        effects.block_at_turn_start_turns({"op": OP, "amount": 5,
                                           "turns": turns})


def test_the_loader_refuses_it_at_load_not_at_resolve():
    """EB-135's discipline: a printed-text error is reported when the sheet is
    read, not the first time a card already in front of a player resolves."""
    row = {"id": "fabricated_ward", "name": "Fabricated", "cost": 1,
           "type": "skill", "rarity": "common",
           "effects": [{"op": OP, "amount": 5, "turns": "X"}]}
    with pytest.raises(ValueError, match="fabricated_ward"):
        loader._validate_effect_vocabulary(row["id"], row["effects"])


def test_a_nested_branch_is_reached_by_the_load_check_too():
    row_effects = [{"op": "conditional", "if": "killed_target",
                    "then": [{"op": OP, "amount": 5, "turns": 0}]}]
    with pytest.raises(ValueError, match="positive literal int"):
        loader._validate_effect_vocabulary("fabricated_branch", row_effects)


def test_a_well_formed_row_loads_clean():
    row_effects = [{"op": OP, "amount": 5, "turns": 2}]
    loader._validate_effect_vocabulary("fabricated_ok", row_effects)


# --- registration: the op is KNOWN everywhere an op has to be known -------

def test_the_op_is_registered_in_the_engine():
    assert OP in effects.OPS


def test_the_connectivity_classifier_knows_the_token():
    """`test_eb118_connectivity` pins OP_HOOKS against OPS both ways; this
    says WHICH state the new op was classified as moving, so a later edit that
    keeps the totality but changes the answer is visible here."""
    assert ccr.OP_HOOKS[OP] == ccr.OP_HOOKS["block_next_turn"]


def test_the_drafter_prices_it_and_says_why():
    """`tools/lint_op_parity.py` requires the entry; this requires the entry
    to be the price the rationale claims -- the delayed-Block share, once per
    printed turn."""
    assert OP in draft.STATIC_OP_PRICING
    fx = {"op": OP, "amount": 5, "turns": 2}
    assert draft._op_price(fx) == pytest.approx(
        5 * draft.STATIC_DELAYED_BLOCK_SHARE * 2)
    one = {"op": OP, "amount": 5, "turns": 1}
    assert draft._op_price(one) == pytest.approx(
        draft._op_price({"op": "block_next_turn", "amount": 5}))


def test_nimble_does_not_ride_the_delayed_block():
    """EB-85 divergence 4, inherited by construction: `_BLOCK_OPS` is an
    ALLOWLIST, so the delayed-Block ops are excluded without anybody having to
    remember them. Pinned because "absent" and "forgotten" look alike."""
    assert OP not in enchantments._BLOCK_OPS
    assert not enchantments._grants_block([{"op": OP, "amount": 5,
                                            "turns": 2}])


# --- nothing here consumes randomness -------------------------------------

def test_the_op_advances_no_rng_stream():
    """A fight is a seed. An op that drew a number would renumber every roll
    after it, which is how "unused machinery" stops being free."""
    st = make_state(enemies=[make_enemy(hp=400)], seed=7)
    before = st.rng.getstate()
    play(st, [{"op": OP, "amount": 5, "turns": 3}])
    for _ in range(3):
        combat._player_turn(st, lambda s: None)
    assert st.rng.getstate() == before
